"""The Zoo Code matcher mirror — ONE copy, imported by everything that needs a verdict.

Extracted from `.agents/scripts/tests/test_zoo_permissions.py` (SCC-354). It mirrors Zoo
v3.80.1's own extracted parser as documented in `docs/migrations/zoo-code-permissions-guide.md`
section 4: lowercase starts-with per piece, longest prefix wins allow-vs-deny, tie goes to deny.

It lived inside the test file because the battery was its only consumer. `/smh-llm-approvals`
is the second: it replays approval-blocked commands through this exact function to work out
which allow row would have let each one through. A copy would be a second matcher, and the
first verdict to drift between the two is one the battery cannot see.

ROOT is re-derived here at `parents[2]` rather than moved: this module sits directly under
`.agents/scripts/`, one level shallower than the test file it came from, and the test still
needs its own `parents[3]` for the guide, the apply script and the door scan.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SETTINGS = ROOT / ".vscode" / "settings.json"


def load_lists() -> tuple[list[str], list[str]]:
    plain = re.sub(r"^\s*//.*$", "", SETTINGS.read_text(encoding="utf-8"), flags=re.M)
    data = json.loads(plain)
    return data["zoo-code.allowedCommands"], data["zoo-code.deniedCommands"]


ALLOW, DENY = load_lists()

# --- mirror of the documented matcher (guide §4) -------------------------------------------


def _mask_quotes(text: str) -> str:
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == "\\":
            out.append(text[i:i + 2]); i += 2; continue
        if c in "'\"":
            q, j = c, i + 1
            while j < n and text[j] != q:
                j += 2 if (q == '"' and text[j] == "\\") else 1
            out.append("\x00" * (min(j + 1, n) - i)); i = min(j + 1, n); continue
        out.append(c); i += 1
    return "".join(out)


def pieces(cmd: str) -> list[str]:
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
            lo, hi = 0, len(part)
            # recover the original text for this span via offsets in the masked line
            idx = masked.find(part) if part else -1
            token = part.strip()
            if not token:
                continue
            m = re.fullmatch(r"\x01(\d+)", token)
            if m:
                out.append(subsh[int(m.group(1))]); continue
            # restore quoted spans: map masked span back onto cmd by position search
            out.append(token)
    # positions of masked pieces need original text; rebuild by re-splitting the raw cmd the
    # same way when no quotes were masked (fixtures with quotes are heredoc/one-piece or the
    # quote content carries no operators, so masked text == raw text for split purposes)
    rebuilt: list[str] = []
    cursor = 0
    for p in out:
        clean = p.replace("\x00", "")
        if "\x00" in p:
            # find the original substring of equal length at the same relative position
            pos = masked.find(p, cursor)
            rebuilt.append(cmd[pos:pos + len(p)].strip() if pos >= 0 else clean)
            cursor = pos + len(p) if pos >= 0 else cursor
        else:
            rebuilt.append(clean)
    return rebuilt


def _longest(piece: str, entries: list[str]) -> str | None:
    p = piece.strip().lower()
    best = None
    for e in entries:
        s = e.lower()
        if (s == "*" or p.startswith(s)) and (best is None or len(s) > len(best)):
            best = s
    return best


def decide(cmd: str, allow: list[str] = ALLOW, deny: list[str] = DENY) -> str:
    # Redirections are masked BEFORE the piece split, like the real matcher (guide §4)
    # — splitting first cut `2>&1` into `2>` + `1` and turned an allowed capture
    # (`> log 2>&1`, the shape command-shape.md itself recommends) into an ask
    # (SCC-351 review, blind lens).
    cmd = re.sub(r"\d*>&\d*", " ", cmd)
    verdicts = []
    for raw in pieces(cmd):
        p = re.sub(r"\d*>&\d*", "", raw, count=1).strip()
        if not p:
            verdicts.append("auto_approve"); continue
        a, d = _longest(p, allow), _longest(p, deny)
        if a and not d:
            verdicts.append("auto_approve")
        elif d and not a:
            verdicts.append("auto_deny")
        elif a and d:
            verdicts.append("auto_approve" if len(a) > len(d) else "auto_deny")
        else:
            verdicts.append("ask_user")
    if "auto_deny" in verdicts:
        return "auto_deny"
    if verdicts and all(v == "auto_approve" for v in verdicts):
        return "auto_approve"
    return "ask_user"
