#!/usr/bin/env python3
"""One permission source, three rendered fences (SCC-378).

The terminal-approval policy for this shop is ONE policy - "allows are broad, denies are the
fence" - written until now in three grammars in three files that nothing reconciled:

    .vscode/settings.json            zoo-code.allowedCommands / deniedCommands   (Zoo Code)
    .claude/settings.json            permissions.allow                          (Claude Code)
    .agents/permissions/antigravity.json  userSettings.globalPermissionGrants  (Antigravity)

This script renders all three from ``.agents/permissions/families.json``. A row in the source is
a FAMILY - an intent, with ``id``, ``cmd``, ``why`` - and each platform's exact rule text either
comes from an explicit ``render: {zoo: [...], claude: [...], antigravity: [...]}`` (the rows
seeded from the pre-SCC-378 lists carry their historical spellings this way) or is DERIVED from
``cmd`` by the platform's grammar. ``only: [..]`` / ``not: [..]`` scope a row to platforms when
a row is genuinely one-platform (Zoo's longest-prefix re-allows, Antigravity's target-scoped
denies). An honest source over a clean one that drifts in the renderers.

Identical DECISIONS, never identical bytes - the matchers differ (guide s3, s6, s3A), so the
renderers encode each platform's quirks and ``tests/test_permission_parity.py`` proves the three
rendered lists agree on one battery of commands.

    python3 .agents/scripts/permission_render.py            # render all three (a sync step)
    python3 .agents/scripts/permission_render.py --check    # exit 0 in sync, 1 on drift (read-only)

``/smh-sync-agents`` runs the render on a sync and ``--check`` on ``-Status``. Pushing a rendered
list into a LIVE machine store stays a separate, explicit apply (``zoo_permissions_apply.py``,
``antigravity_permissions_apply.py``) - those need the editor closed or write outside git.

Stdlib only; runs on the Mac and inside Ubuntu on the PC under ``python3``.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLATFORMS = ("zoo", "claude", "antigravity")
SOURCE_REL = Path(".agents") / "permissions" / "families.json"
AG_REL = Path(".agents") / "permissions" / "antigravity.json"
VSCODE_REL = Path(".vscode") / "settings.json"
CLAUDE_REL = Path(".claude") / "settings.json"
ZOO_ALLOW_KEY = "zoo-code.allowedCommands"
ZOO_DENY_KEY = "zoo-code.deniedCommands"


# ---------------------------------------------------------------- source


def load_source(root: Path = REPO_ROOT) -> dict:
    return json.loads((root / SOURCE_REL).read_text(encoding="utf-8"))


def _applies(row: dict, platform: str) -> bool:
    if "only" in row and platform not in row["only"]:
        return False
    if "not" in row and platform in row["not"]:
        return False
    return True


def _dedupe(items: list[str]) -> list[str]:
    seen, out = set(), []
    for it in items:
        if it not in seen:
            seen.add(it); out.append(it)
    return out


def _validate_source(src: dict) -> None:
    """Refuse a malformed row by NAME before anything is rendered (SCC-378 code review, 2026-09-03).

    `/smh-llm-approvals` and hand edits write this file. An empty `cmd` reached `cmd[-1]` as a bare
    IndexError naming no row; a `render` value written as a string instead of a list was spread
    character by character, so `"zoo": "git status "` rendered seven one-letter Zoo allow prefixes
    (`g`, `i`, `t`, ...) and `gcc` auto-approved. Duplicate ids make a family unaddressable."""
    seen: set[str] = set()
    for kind in ("allow", "deny"):
        for row in src.get(kind, []):
            rid = row.get("id", "?")
            if rid in seen:
                raise ValueError(f"families.json: duplicate id {rid!r}")
            seen.add(rid)
            if not isinstance(row.get("cmd"), str) or not row["cmd"].strip():
                raise ValueError(f"families.json: row {rid!r} has an empty cmd")
            for platform, rules in (row.get("render") or {}).items():
                if isinstance(rules, str) or not all(isinstance(r, str) for r in rules):
                    raise ValueError(f"families.json: row {rid!r} render.{platform} must be a list of strings")


# ---------------------------------------------------------------- derivation per grammar
# Only reached for a row WITHOUT an explicit render for that platform.

def _derive_zoo(row: dict, kind: str, env_twin: str) -> list[str]:
    cmd = row["cmd"].rstrip()
    if kind == "allow":
        # a prefix ending in a path/assignment separator takes NO trailing space (`backend/.venv/bin/`,
        # `REPO=`) - the real command has none there; every other prefix ends in one so `tr` != `trap`
        return [cmd if row.get("bare") or cmd[-1] in "/=-:" else cmd + " "]
    out = [cmd]
    if cmd.startswith(("git ", "gh ")) and env_twin:
        out.append(env_twin + cmd)
    return out


def _derive_claude(row: dict, kind: str) -> list[str]:
    if kind == "deny":
        return []                                  # Claude carries no deny list (guide s3)
    cmd = row["cmd"].rstrip()
    if row.get("bare"):
        return [f"Bash({cmd})"]
    # `X:*` is dead after a path separator - the space before * would never match (SCC-375 A2b)
    return [f"Bash({cmd}*)" if cmd[-1] in "/=-:" else f"Bash({cmd}:*)"]


def _ag_token(tok: str, kind: str, last: bool) -> str:
    """One derived Antigravity token, escaped, in the shape the anchored matcher needs.

    A source `cmd` is a PREFIX (Zoo's grammar); this platform fullmatches each token, so the last
    token of a prefix ending in `/ = - :` takes a `.*` tail (`backend/\\.venv/bin/.*`, or nothing
    ever matches), and a single-letter flag on a deny becomes its cluster class (`-f` ->
    `-[a-zA-Z]*f[a-zA-Z]*`, or `-fd` slips past). SCC-378 code review, 2026-09-03."""
    if kind == "deny" and re.fullmatch(r"-[a-zA-Z]", tok):
        return f"-[a-zA-Z]*{tok[1]}[a-zA-Z]*"
    esc = re.escape(tok)
    return esc + ".*" if last and tok[-1] in "/=-:" else esc


def _derive_antigravity(row: dict, kind: str, env_twin: str) -> list[str]:
    # each token is an anchored REGEX on this platform, so a derived row escapes per token
    # (`backend/.venv/bin/` -> `backend/\.venv/bin/.*`); explicit renders are written already-escaped
    toks = row["cmd"].split()
    cmd = " ".join(_ag_token(t, kind, i == len(toks) - 1) for i, t in enumerate(toks))
    bodies = [cmd]
    if kind == "deny" and row["cmd"].startswith(("git ", "gh ")) and env_twin:
        bodies.append(env_twin + cmd)
    out = []
    for b in bodies:
        out += [f"command({b})", f"unsandboxed({b})"]
    return out


_AG_BODY = re.compile(r"^(command|unsandboxed)\((.*)\)$", re.S)


def _house_twins(rules: list[str], prefix: str) -> list[str]:
    """Every Antigravity deny, also behind the house command shape `cd <abs> && ...`.

    The vendor documents per-token matching on a command's leading tokens and nothing about chains
    (antigravity.google/docs/permissions, read 2026-09-03). If the whole line is matched, the
    `cd <abs> && git <verb>` shape command-shape.md mandates begins with the allowed token `cd`, and
    no deny row can see past it. The twin fences that shape either way; if the vendor splits chains
    it is a dead row, never a wrong one. SCC-378 code review, 2026-09-03."""
    out = []
    for r in rules:
        m = _AG_BODY.match(r)
        if m:
            out.append(f"{m.group(1)}({prefix}{m.group(2)})")
    return out


def _rows(src: dict, kind: str, platform: str) -> list[str]:
    _validate_source(src)
    env_twin = src.get("env_twin_prefix", "")
    out: list[str] = []
    for row in src.get(kind, []):
        if not _applies(row, platform):
            continue
        explicit = (row.get("render") or {}).get(platform)
        if explicit is not None:
            out += list(explicit)
            continue
        if platform == "zoo":
            out += _derive_zoo(row, kind, env_twin)
        elif platform == "claude":
            out += _derive_claude(row, kind)
        else:
            out += _derive_antigravity(row, kind, env_twin)
    if platform == "antigravity" and kind == "deny" and src.get("house_twin_prefix"):
        out += _house_twins(out, src["house_twin_prefix"])
    return _dedupe(out)


def render_zoo(src: dict) -> tuple[list[str], list[str]]:
    return _rows(src, "allow", "zoo"), _rows(src, "deny", "zoo")


def render_claude(src: dict) -> list[str]:
    return _rows(src, "allow", "claude")


def render_antigravity(src: dict) -> dict:
    return {"allow": _rows(src, "allow", "antigravity"), "deny": _rows(src, "deny", "antigravity")}


# ---------------------------------------------------------------- the three files


def _comment_end(text: str, i: int) -> int:
    """Index just past the JSONC comment starting at `i` (`//` to end of line, `/* */` to its close),
    or -1 when no comment starts there. Both shapes are legal in .vscode/settings.json."""
    if text.startswith("//", i):
        j = text.find("\n", i)
        return len(text) if j < 0 else j
    if text.startswith("/*", i):
        j = text.find("*/", i + 2)
        return len(text) if j < 0 else j + 2
    return -1


def _jsonc_load(text: str) -> dict:
    """json.loads for the JSONC VS Code writes: comments anywhere outside a string (a whole line,
    or trailing a value, or `/* */`) and a trailing comma before `]` / `}`. Until the code review of
    2026-09-03 only whole-line `//` was stripped, so an inline note crashed `--check` and the parity
    test file while `write()` accepted the same text."""
    out, i, in_str, esc = [], 0, False, False
    while i < len(text):
        ch = text[i]
        if in_str:
            out.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            i += 1
            continue
        j = _comment_end(text, i)
        if j >= 0:
            i = j
            continue
        if ch == '"':
            in_str = True
        elif ch == "," and re.match(r",\s*[\]}]", text[i:]):
            i += 1                                   # a trailing comma VS Code tolerates; json.loads does not
            continue
        out.append(ch)
        i += 1
    return json.loads("".join(out))


def _find_array_span(text: str, key: str) -> tuple[int, int, str]:
    """(start, end, indent) of the `[...]` value of `"key":` - end is the index AFTER `]`.
    Bracket-matched, quote-aware, comment-aware, so a `]` inside a string or a comment cannot end
    the scan."""
    m = re.search(r'^([ \t]*)"' + re.escape(key) + r'"\s*:\s*\[', text, re.M)
    if not m:
        raise KeyError(key)
    i, depth, in_str, esc = m.end(), 1, False, False
    while i < len(text):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == "/" and _comment_end(text, i) >= 0:
            # a JSONC comment: skip it whole, or a quote or `]` inside it desyncs the scan
            i = _comment_end(text, i)
            continue
        elif ch == '"':
            in_str = True
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return m.end() - 1, i + 1, m.group(1)
        i += 1
    raise ValueError(f"unterminated array for {key}")


def _replace_jsonc_array(text: str, key: str, values: list[str]) -> str:
    start, end, indent = _find_array_span(text, key)
    inner = indent + "  "
    body = ",\n".join(inner + json.dumps(v, ensure_ascii=False) for v in values)
    return text[:start] + "[\n" + body + "\n" + indent + "]" + text[end:]


def current_lists(root: Path) -> dict:
    """What the three files say NOW (sets are compared; order is the renderer's).
    A file that will not parse raises ValueError naming it - `check()` reports that as drift."""
    out: dict = {}
    vs = root / VSCODE_REL
    if vs.exists():
        try:
            d = _jsonc_load(vs.read_text(encoding="utf-8"))
        except ValueError as e:
            raise ValueError(f"{VSCODE_REL}: unreadable ({e})") from e
        out["zoo"] = (list(d.get(ZOO_ALLOW_KEY, [])), list(d.get(ZOO_DENY_KEY, [])))
    cl = root / CLAUDE_REL
    if cl.exists():
        try:
            d = json.loads(cl.read_text(encoding="utf-8"))
        except ValueError as e:
            raise ValueError(f"{CLAUDE_REL}: unreadable ({e})") from e
        out["claude"] = list(d.get("permissions", {}).get("allow", []))
    ag = root / AG_REL
    if ag.exists():
        try:
            g = json.loads(ag.read_text(encoding="utf-8"))["userSettings"]["globalPermissionGrants"]
        except (ValueError, KeyError, TypeError) as e:
            raise ValueError(f"{AG_REL}: unreadable ({e!r})") from e
        out["antigravity"] = (list(g.get("allow", [])), list(g.get("deny", [])))
    return out


def _diff_msg(label: str, want: list[str], have: list[str]) -> str | None:
    w, h = set(want), set(have)
    if w == h:
        return None
    extra = sorted(h - w)[:3]
    missing = sorted(w - h)[:3]
    return (f"{label}: file has {len(h - w)} row(s) the source does not render {extra}, "
            f"source renders {len(w - h)} row(s) the file lacks {missing}")


def check(root: Path = REPO_ROOT) -> list[str]:
    """Drift messages, empty when every rendered file equals its render (as sets)."""
    src_path = root / SOURCE_REL
    if not src_path.exists():
        return [f"{SOURCE_REL}: missing"]
    src = load_source(root)
    try:
        have = current_lists(root)
        za, zd = render_zoo(src)
    except ValueError as e:                  # an unreadable file or a malformed source row IS drift
        return [str(e)]
    msgs: list[str] = []
    if "zoo" not in have:
        msgs.append(f"{VSCODE_REL}: missing")
    else:
        for lbl, w, h in ((f"{VSCODE_REL} {ZOO_ALLOW_KEY}", za, have["zoo"][0]),
                          (f"{VSCODE_REL} {ZOO_DENY_KEY}", zd, have["zoo"][1])):
            m = _diff_msg(lbl, w, h)
            if m:
                msgs.append(m)
    if "claude" not in have:
        msgs.append(f"{CLAUDE_REL}: missing")
    else:
        m = _diff_msg(f"{CLAUDE_REL} permissions.allow", render_claude(src), have["claude"])
        if m:
            msgs.append(m)
    ag = render_antigravity(src)
    if "antigravity" not in have:
        msgs.append(f"{AG_REL}: missing")
    else:
        for lbl, w, h in ((f"{AG_REL} allow", ag["allow"], have["antigravity"][0]),
                          (f"{AG_REL} deny", ag["deny"], have["antigravity"][1])):
            m = _diff_msg(lbl, w, h)
            if m:
                msgs.append(m)
    return msgs


def write(root: Path = REPO_ROOT) -> list[str]:
    """Render all three targets in place, touching only the keys each platform owns.

    Every target is rendered to text BEFORE the first write, and the Claude file goes first: run from
    Claude Code its sandbox refuses that path, and a write order of Zoo -> Claude -> Antigravity left
    the Zoo list ahead of the other two - the exact three-lists-disagree state this renderer exists
    to remove (SCC-378 code review, 2026-09-03)."""
    src = load_source(root)
    za, zd = render_zoo(src)
    vs = root / VSCODE_REL
    text = vs.read_text(encoding="utf-8")
    new = _replace_jsonc_array(_replace_jsonc_array(text, ZOO_ALLOW_KEY, za), ZOO_DENY_KEY, zd)
    cl = root / CLAUDE_REL
    data = json.loads(cl.read_text(encoding="utf-8"))
    ca = render_claude(src)
    cl_changed = data.get("permissions", {}).get("allow") != ca
    if cl_changed:
        data.setdefault("permissions", {})["allow"] = ca
    cl_text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    ag_path = root / AG_REL
    ag_doc = {"userSettings": {"globalPermissionGrants": render_antigravity(src)}}
    ag_text = json.dumps(ag_doc, indent=2, ensure_ascii=False) + "\n"
    ag_changed = not ag_path.exists() or ag_path.read_text(encoding="utf-8") != ag_text

    written: list[str] = []
    if cl_changed:
        cl.write_text(cl_text, encoding="utf-8"); written.append(str(CLAUDE_REL))
    if new != text:
        vs.write_text(new, encoding="utf-8"); written.append(str(VSCODE_REL))
    if ag_changed:
        ag_path.parent.mkdir(parents=True, exist_ok=True)
        ag_path.write_text(ag_text, encoding="utf-8"); written.append(str(AG_REL))
    return written


# ---------------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--check", action="store_true", help="read-only: exit 0 in sync, 1 on drift")
    p.add_argument("--root", type=Path, default=REPO_ROOT)
    a = p.parse_args(argv)
    if a.check:
        msgs = check(a.root)
        if msgs:
            print("permission_render: DRIFT")
            for m in msgs:
                print("  " + m)
            return 1
        print("permission_render: in sync (zoo, claude, antigravity)")
        return 0
    written = write(a.root)
    print("permission_render: wrote " + (", ".join(written) if written else "nothing (already in sync)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
