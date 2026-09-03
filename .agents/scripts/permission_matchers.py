#!/usr/bin/env python3
"""The three terminal-approval matchers, one signature (SCC-378).

Each function answers ``"allow" | "deny" | "ask"`` for ONE command string against a platform's
own list grammar. They exist so one battery can ask every platform the same question and demand
the same answer (``tests/test_permission_parity.py``). Nothing here decides anything at run time
- the real matchers live inside Zoo Code, Claude Code and the Antigravity extension; these are
mirrors, each verified against its vendor's documented or extracted semantics.

  zoo_verdict         Zoo Code v3.80.x: split into PIECES (newline, &&, ||, ;, |, & outside
                      quotes; heredocs whole; $() bodies one unsplit piece), each piece matched
                      LOWERCASE by plain starts-with against both lists, LONGEST prefix wins
                      allow-vs-deny, tie -> deny. Any denied piece -> deny; all allowed -> allow;
                      else ask. Mirror carried from tests/test_zoo_permissions.py, where it was
                      executed against the real extracted parser on 2026-08-30 (guide s6).
  claude_verdict      Claude Code: rules are ``Bash(prefix:*)`` == ``Bash(prefix *)`` (the space
                      before a trailing * is part of the rule - SCC-375 A2b), a bare
                      ``Bash(exact)`` matches the exact command, and a compound is judged per
                      segment. The tracked file has NO deny list (the fence is hooks + the OS
                      sandbox, guide s3), so this never returns "deny": unmatched -> "ask".
  antigravity_verdict Antigravity extension: each whitespace token of a rule is an ANCHORED regex
                      (^(?:tok)$) matched against the command's leading tokens; a rule with more
                      tokens than the command cannot match; strict Deny > Ask > Allow. Rules are
                      wrapped ``command(...)`` / ``unsandboxed(...)`` - the wrapper is stripped,
                      both kinds count for execution. Regex is case-sensitive (unlike Zoo).
"""
from __future__ import annotations

import re

VERDICTS = ("allow", "deny", "ask")

# ---------------------------------------------------------------- Zoo (mirror, guide s6)


def _mask_quotes(text: str) -> str:
    out, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "\\":
            out.append(text[i:i + 2]); i += 2; continue
        if ch in "'\"":
            q, j = ch, i + 1
            while j < n and text[j] != q:
                j += 2 if (q == '"' and text[j] == "\\") else 1
            out.append("\x00" * (min(j + 1, n) - i)); i = min(j + 1, n); continue
        out.append(ch); i += 1
    return "".join(out)


def zoo_pieces(cmd: str) -> list[str]:
    """Split like Zoo does: heredocs stay whole; $() bodies become their own unsplit piece;
    otherwise split on newlines and && || ; | & outside quotes."""
    if re.search(r"<<-?\s*['\"]?\w", cmd):
        return [cmd]
    masked = _mask_quotes(cmd)
    masked = re.sub(r"\$\{[^}]+\}", lambda m: "\x00" * len(m.group(0)), masked)
    subsh: list[str] = []

    def grab(m: re.Match) -> str:
        subsh.append(cmd[m.start(1):m.end(1)].strip())
        return " \x01%d " % (len(subsh) - 1)

    masked = re.sub(r"\S*?\$\(([^()]*)\)", grab, masked)
    out: list[str] = []
    for line in masked.split("\n"):
        for part in re.split(r"&&|\|\||;|\||&", line):
            token = part.strip()
            if not token:
                continue
            m = re.fullmatch(r"\x01(\d+)", token)
            if m:
                out.append(subsh[int(m.group(1))]); continue
            out.append(token)
    rebuilt: list[str] = []
    cursor = 0
    for p in out:
        clean = p.replace("\x00", "")
        if "\x00" in p:
            pos = masked.find(p, cursor)
            rebuilt.append(cmd[pos:pos + len(p)].strip() if pos >= 0 else clean)
            cursor = pos + len(p) if pos >= 0 else cursor
        else:
            rebuilt.append(clean)
    return rebuilt


def _zoo_longest(piece: str, entries: list[str]) -> str | None:
    p = piece.strip().lower()
    best = None
    for e in entries:
        s = e.lower()
        if (s == "*" or p.startswith(s)) and (best is None or len(s) > len(best)):
            best = s
    return best


def zoo_verdict(cmd: str, allow: list[str], deny: list[str]) -> str:
    cmd = re.sub(r"\d*>&\d*", " ", cmd)          # redirections masked BEFORE the split
    verdicts = []
    for raw in zoo_pieces(cmd):
        p = re.sub(r"\d*>&\d*", "", raw, count=1).strip()
        if not p:
            verdicts.append("allow"); continue
        a, d = _zoo_longest(p, allow), _zoo_longest(p, deny)
        if a and not d:
            verdicts.append("allow")
        elif d and not a:
            verdicts.append("deny")
        elif a and d:
            verdicts.append("allow" if len(a) > len(d) else "deny")
        else:
            verdicts.append("ask")
    if "deny" in verdicts:
        return "deny"
    if verdicts and all(v == "allow" for v in verdicts):
        return "allow"
    return "ask"


# ---------------------------------------------------------------- Claude Code


_CLAUDE_RULE = re.compile(r"^Bash\((.*)\)$", re.S)


def _claude_rule_matches(rule: str, segment: str) -> bool:
    m = _CLAUDE_RULE.match(rule.strip())
    if not m:
        return False
    spec = m.group(1)
    seg = segment.strip()
    if spec.endswith(":*"):                       # Bash(prefix:*) == Bash(prefix *)
        prefix = spec[:-2]
        return seg == prefix or seg.startswith(prefix + " ") or (
            prefix and prefix[-1] in "/=-:" and seg.startswith(prefix))
    if spec.endswith("*"):                        # Bash(prefix*) - glob tail, no boundary
        return seg.startswith(spec[:-1])
    return seg == spec                            # Bash(exact)


def claude_segments(cmd: str) -> list[str]:
    """Claude judges a compound per segment; quotes are respected the same way Zoo's are."""
    masked = _mask_quotes(cmd)
    segs, start = [], 0
    for m in re.finditer(r"&&|\|\||;|\|", masked):
        segs.append(cmd[start:m.start()]); start = m.end()
    segs.append(cmd[start:])
    return [s.strip() for s in segs if s.strip()]


def claude_verdict(cmd: str, allow: list[str]) -> str:
    """No deny list in the tracked file: every segment allowed -> allow, else ask."""
    segs = claude_segments(cmd)
    if not segs:
        return "ask"
    for seg in segs:
        if not any(_claude_rule_matches(r, seg) for r in allow):
            return "ask"
    return "allow"


# ---------------------------------------------------------------- Antigravity


_AG_RULE = re.compile(r"^(\w+)\((.*)\)$", re.S)
_AG_EXEC_KINDS = ("command", "unsandboxed")


def ag_rule_body(rule: str) -> str | None:
    """The rule text inside command(...)/unsandboxed(...); None for other rule kinds."""
    m = _AG_RULE.match(rule.strip())
    if not m or m.group(1) not in _AG_EXEC_KINDS:
        return None
    return m.group(2)


def _ag_hit(body: str, cmd: str) -> bool:
    rt, ct = body.split(), cmd.split()
    if not rt or len(rt) > len(ct):
        return False
    for r, c in zip(rt, ct):
        try:
            if not re.fullmatch(r, c):
                return False
        except re.error:
            return False
    return True


def antigravity_verdict(cmd: str, allow: list[str], deny: list[str]) -> str:
    """Deny > Ask > Allow, per-token anchored regex, leading-token prefix."""
    for r in deny:
        b = ag_rule_body(r)
        if b is not None and _ag_hit(b, cmd):
            return "deny"
    for r in allow:
        b = ag_rule_body(r)
        if b is not None and _ag_hit(b, cmd):
            return "allow"
    return "ask"
