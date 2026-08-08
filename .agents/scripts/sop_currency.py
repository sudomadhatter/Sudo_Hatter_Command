"""sop_currency.py — keep the SOP quick-reference from going stale (SCC-31, 2026-08-08).

`_my_resources/_quick_reference/sudo_workflows_testing.md` is the PRD for how this system is
USED: the command menu, the two rules above every command, the safety net, the shipping road.
It is the one document an operator reads start-to-finish, and the only one that answers "what
do I type." A stale line there is worse than a missing one — it is an instruction that fails
in the operator's hands, months after the change that broke it.

That already happened, twice over, on a single line: the doc said `python .agents/scripts/
tests/run_all.py — 94 checks` when the Mac has no bare `python` (only `python3`) and the count
was 98. Both halves wrong, and nothing anywhere could have noticed. The first fix then swung the
other way and declared `python3` universal — equally wrong, because this system is driven from a
Windows PC too, where a python.org install has only `python`. Docs get read on BOTH machines.

  ── WHAT THIS CHECKS ───────────────────────────────────────────────────────────────────────
Given a set of changed paths, it answers ONE question: did a **usage surface** change without
the SOP doc changing in the same commit? A usage surface is anything that alters what the
operator types, what a command does, or what a gate refuses:

    .agents/commands/*.md        the `/` menu itself — add/delete/rename is ALWAYS a usage change
    .agents/rules/*.md           the law those commands cite
    .agents/scripts/*.py         the safety net (§5 of the doc names these one by one)
    .agents/scripts/git-hooks/   the gates that refuse a commit
    .githooks/                   their installed shims
    AGENTS.md (root)             the front door

Deliberately NOT surfaces: `INDEX.md` inventory churn (mechanical, re-generated), `reference/`,
`templates/`, `skills/`, `workflows/` (mirrors of commands), `_artifacts/` (history), and this
script's own tests. Widening this list is how a useful gate becomes a disabled one.

  ── SCOPE IS DELIBERATELY DUMB ─────────────────────────────────────────────────────────────
It checks CO-OCCURRENCE, not content. It cannot know whether the doc edit was the *right* edit
— no check can. What it can do is guarantee the author looked. That is the whole design: the
gate converts "I'll update the doc later" into a decision made now, in the one moment the
author still holds the context.

  ── MODES ──────────────────────────────────────────────────────────────────────────────────
    SOP-ENFORCE present   BLOCK — reject the commit  (default; ships armed)
    marker deleted        WARN  — print and pass
A warn-only hook is invisible under VS Code, which renders hook output nowhere the operator
looks: it reads as a clean success. Shipping this warn-only would have been shipping nothing.

  ── THE ESCAPE HATCH ───────────────────────────────────────────────────────────────────────
`[sop-ok]` anywhere in the commit message means "this genuinely does not change how the system
is used" — a typo fix, a comment, an internal refactor. One token, and it lands in the git log
where it is auditable forever. Same shape as the encoding gate's `wf-lint: allow-encoding-
literals` stand-down, and for the same reason: a gate with no legitimate exit gets `--no-verify`d
into oblivion, and then nothing is checked at all.

Stdlib only, plain ASCII output — same constraints as its siblings (Windows consoles are cp1252).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# The document this whole file exists to protect.
SOP_DOC = "_my_resources/_quick_reference/sudo_workflows_testing.md"

# Opt-out token. Matched case-insensitively so [SOP-OK] works at 2am.
SKIP_TOKEN = "[sop-ok]"

# Arming marker, resolved relative to the repo root.
ENFORCE_MARKER = ".agents/scripts/git-hooks/SOP-ENFORCE"

# ── Surfaces ──────────────────────────────────────────────────────────────────
# (prefix, suffix or None) — a path is a surface when it starts with the prefix and,
# if a suffix is given, ends with it. Ordered most-specific first for the reason text.
_SURFACES: list[tuple[str, tuple[str, ...] | None, str]] = [
    (".agents/commands/", (".md",), "the / command menu"),
    (".agents/rules/", (".md",), "the rules commands cite"),
    (".agents/scripts/git-hooks/", None, "a commit gate"),
    (".githooks/", None, "an installed hook shim"),
    # .ps1 belongs here as much as .py: sync-agents.ps1 IS the propagation engine.
    (".agents/scripts/", (".py", ".ps1"), "the safety-net scripts"),
]

# Checked before _SURFACES; an exact match here is never a surface.
_EXEMPT_NAMES = {"INDEX.md"}
_EXEMPT_PREFIXES = (".agents/scripts/tests/",)


def _norm(path: str) -> str:
    """Normalize a git path to compare against the surface prefixes.

    NOT `lstrip("./")` — lstrip takes a character SET, so it eats the leading dot off
    every `.agents/...` path and the whole gate silently matches nothing. It shipped that
    way for exactly one test run; cases A-D and X are the regression.
    """
    p = path.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def classify(path: str) -> str | None:
    """Return why `path` is a usage surface, or None if it is not one."""
    p = _norm(path)
    if p == SOP_DOC:
        return None
    if p == "AGENTS.md":
        return "the front door"
    if Path(p).name in _EXEMPT_NAMES:
        return None
    if any(p.startswith(x) for x in _EXEMPT_PREFIXES):
        return None
    for prefix, suffixes, why in _SURFACES:
        if p.startswith(prefix) and (suffixes is None or p.endswith(suffixes)):
            return why
    return None


def staged_paths(repo: Path) -> list[str]:
    """Paths staged for commit. A failure here yields [] — never a false block."""
    try:
        r = subprocess.run(["git", "diff", "--cached", "--name-only"],
                           cwd=repo, capture_output=True, text=True, errors="replace")
    except OSError:
        return []
    if r.returncode != 0:
        return []
    return [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]


def evaluate(paths: list[str], message: str) -> tuple[bool, list[tuple[str, str]], str]:
    """(ok, offending [(path, why)], reason). Pure — no I/O, so the tests can drive it."""
    if any(t in message.lower() for t in (SKIP_TOKEN,)):
        return True, [], "opted out with " + SKIP_TOKEN
    normalized = [_norm(p) for p in paths]
    if SOP_DOC in normalized:
        return True, [], "SOP doc updated in the same commit"
    offending = [(p, why) for p in normalized if (why := classify(p))]
    if not offending:
        return True, [], "no usage surface touched"
    return False, offending, "usage surface changed, SOP doc did not"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Require an SOP-doc update alongside usage changes.")
    ap.add_argument("--repo", default=".", help="repo root (default: cwd)")
    ap.add_argument("--message", default="", help="commit message text")
    ap.add_argument("--message-file", help="file holding the commit message")
    ap.add_argument("--paths", nargs="*", help="changed paths (default: the staged set)")
    a = ap.parse_args(argv)

    repo = Path(a.repo).resolve()
    message = a.message
    if a.message_file:
        try:
            # Strip git's comment block: it lists the staged files, and that listing
            # contains the SOP doc's own path whenever it is staged. An unstripped read
            # would let the file list satisfy a token match and silently disarm the gate.
            raw = Path(a.message_file).read_text(encoding="utf-8", errors="replace")
            message = "\n".join(ln for ln in raw.splitlines() if not ln.startswith("#"))
        except OSError:
            message = ""

    paths = a.paths if a.paths is not None else staged_paths(repo)
    ok, offending, reason = evaluate(paths, message)
    if ok:
        return 0

    armed = (repo / ENFORCE_MARKER).exists()
    print("")
    print("  x The SOP quick-reference was not updated with this change.")
    print("")
    print("    You changed how the command center is USED:")
    for p, why in offending[:8]:
        print(f"      - {p}   ({why})")
    if len(offending) > 8:
        print(f"      ... and {len(offending) - 8} more")
    print("")
    print(f"    Update  {SOP_DOC}")
    print("    so the page still matches the system it describes, and stage it with this commit.")
    print("")
    print(f"    If this genuinely does not change how anything is used, put {SKIP_TOKEN}")
    print("    in the commit message. It stays in the log as the record of that call.")
    print("")
    if armed:
        print("    Commit rejected.")
        print("")
        return 1
    print(f"    (warn-only - commit allowed. Arm it with: touch {ENFORCE_MARKER})")
    print("")
    return 0


if __name__ == "__main__":
    sys.exit(main())
