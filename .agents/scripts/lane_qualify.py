"""lane_qualify.py — which lane is this work in? (SCC-162, 2026-08-15)

The lightweight lane exists because of an operator ruling: *"not everything is a full quick
dev. sometimes I just want an agent to do something specific… this does not touch anything
that can break. so we don't need to over engineer it."* And a second one, which is the scope:
*"this is only for the smh / commands, we need this for the command center not normal cicd
work… things that do not affect our development system."*

That second sentence is the whole test, and this script is it. It is a script rather than a
paragraph in a rule for one reason: **the previous version of this rule was prose, and an
agent talked itself past it.** A qualification an agent evaluates by judgement is a
qualification it can want its way through; a path list it must run is a fact.

    lane_qualify.py [--repo PATH] [--paths P ...] [--no-file-changes]

    LIGHT               the lightweight lane - do it, push it, hand back        (exit 0)
    LIGHT-VCS           a DECLARED git-hygiene action that changes no files      (exit 0)
    TASK                the full /smh-quick-dev lane: plan, audit, RED, review   (exit 1)
    HANDOFF             a deployable path - /cicd-push-e2e's road, never a Task  (exit 2)
    NOT-COMMAND-CENTRE  a project repo - use the cicd-* lanes                    (exit 3)

  ── READ THE WORD, NOT THE EXIT CODE ───────────────────────────────────────────────────────
The verdict is printed as a bare word on the first line because a piped gate reports the
PIPE's status, not the script's (`piping-a-gate-hides-its-exit-code`). The exit code is there
for scripts; the word is there for the agent, and they always agree.

  ── WHY EACH REFUSAL EXISTS, IN THE ORDER IT IS CHECKED ─────────────────────────────────────
1. NOT THE COMMAND CENTRE. Checked FIRST, before paths are read at all, because the failure
   this prevents is an agent standing in a project with a small doc change reasoning its way
   into a lane that was never meant to reach product work. Derived, never asserted by name:
   the centre owns workflow law and projects are thin, so `.agents/commands/` masters exist in
   exactly one repo. A hard-coded folder name would be wrong the first time it is cloned.
2. A CONTRADICTED DECLARATION. `--no-file-changes` is a statement; naming paths alongside it
   is a statement that contradicts itself, and the safe reading of a self-contradiction is
   never the permissive one.
3. SILENCE. No paths at all is UNKNOWN scope, not empty scope, and unknown resolves to TASK.
   "A check whose empty input reads as a pass" is a named tripwire in the house audit, and
   this is the one input an agent controls completely.
4. DEPLOYABLE. Imported from `task_preflight`, never re-typed, so the close-out gate and this
   one can never disagree about what "deployable" means.
5. THE TOOLKIT. Anything under `.agents/`, `.githooks/`, `_bmad*` or the root `AGENTS.md`.

  ⛔ Rule 5 is deliberately BLUNTER than `sop_currency.classify()`, and the difference is the
  point. That function exempts `.agents/scripts/tests/` - correctly, for ITS question, since
  editing a test changes nothing the operator types. Reusing it here would have rated an edit
  to the ENFORCEMENT SUITE as safe. "Does this need a SOP update?" and "can this break
  something?" are different questions; `test_lane_qualify.py` pins the divergence and
  cross-checks that this script is never the more permissive of the two.

It reads and prints. It never edits, never branches, never merges, and it is never the
authority for a merge - that stays `task_preflight.py`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
# ONE definition of "deployable" in this repo, not two. `task_preflight` already owns it and
# already carries the SCC-118 reasoning about why `.github/` differs in kind from the product
# dirs. Import-safe: its work is guarded by `if __name__ == "__main__"`.
from task_preflight import DEPLOY_DIRS

# The toolkit itself. Prefix match, plus one exact filename.
TOOLKIT_PREFIXES = (".agents/", ".githooks/", "_bmad/", "_bmad-output/")
TOOLKIT_FILES = frozenset({"AGENTS.md"})

VERDICTS = {"LIGHT": 0, "LIGHT-VCS": 0, "TASK": 1, "HANDOFF": 2, "NOT-COMMAND-CENTRE": 3}


def norm(path: str) -> str:
    """Normalize a path for prefix comparison.

    NOT `lstrip("./")` — lstrip takes a character SET, so it eats the leading dot off every
    `.agents/...` path and every toolkit rule silently stops matching. `sop_currency._norm`
    shipped that bug for exactly one test run; this is the same fix, written the same way, on
    purpose — two normalizers that disagree are how the drift case starts failing.
    """
    p = path.replace("\\", "/").strip()
    while p.startswith("./"):
        p = p[2:]
    return p


def is_command_centre(repo: Path) -> bool:
    """Does this repo hold the command masters? That is what makes it the centre."""
    d = repo / ".agents" / "commands"
    return d.is_dir() and any(d.glob("*.md"))


def classify(repo: Path, paths: list[str], no_file_changes: bool) -> tuple[str, str]:
    """Return (verdict, one-line reason). Order matters — see the module docstring."""
    if not is_command_centre(repo):
        return ("NOT-COMMAND-CENTRE",
                f"no .agents/commands/ masters under {repo} - this is a project repo, not the "
                f"command centre. Product work uses the cicd-* lanes, however small it looks")

    clean = [norm(p) for p in paths if norm(p)]

    if no_file_changes:
        if clean:
            return ("TASK",
                    f"--no-file-changes was declared but {len(clean)} path(s) were named "
                    f"({clean[0]}...) - a self-contradicting declaration is never read the "
                    f"permissive way")
        return ("LIGHT-VCS",
                "a declared git-hygiene action with no file diff - still names only what the "
                "operator named, and every git call carries -C")

    if not clean:
        return ("TASK",
                "no paths given - that is UNKNOWN scope, not empty scope. Silence is never a "
                "pass; declare --no-file-changes if this genuinely edits nothing")

    hits = [p for p in clean if p.startswith(DEPLOY_DIRS)]
    if hits:
        return ("HANDOFF",
                f"deployable path(s): {', '.join(hits[:3])} - the product has one road to "
                f"main and it is /cicd-push-e2e. There is no override, deliberately")

    tool = [p for p in clean
            if p.startswith(TOOLKIT_PREFIXES) or p in TOOLKIT_FILES]
    if tool:
        return ("TASK",
                f"toolkit path(s): {', '.join(tool[:3])} - this changes the development "
                f"system, so it takes the full lane (plan, audit, RED, review)")

    return ("LIGHT",
            f"{len(clean)} path(s), none deployable and none in the toolkit - do it, push it, "
            f"hand back")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Which lane is this work in? (SCC-162)")
    ap.add_argument("--repo", default=".", help="repo root to judge (default: cwd)")
    ap.add_argument("--paths", nargs="*", default=[],
                    help="the paths the work will change; omitting this is UNKNOWN, not empty")
    ap.add_argument("--no-file-changes", action="store_true",
                    help="declare a git-hygiene action that edits no files")
    args = ap.parse_args(argv)

    verdict, why = classify(Path(args.repo).resolve(), args.paths, args.no_file_changes)
    print(verdict)
    print(why)
    return VERDICTS[verdict]


if __name__ == "__main__":
    raise SystemExit(main())
