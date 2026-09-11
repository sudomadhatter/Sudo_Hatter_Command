"""epic_mode.py — the epic's mode as ONE query, printed first, read by every door (SCC-446).

An agent must know which epic it is on from command output, never from belief, and the mode is
chosen once by the operator at kickoff and carried in the branch NAME (git-policy § The epic's
mode): `epic/<KEY>-epic-<N>-<slug>` is FULL, `epic/<KEY>-light-epic-<N>-<slug>` is LIGHT, no
`origin/epic/*` at all is TRUNK. Before this script every branch-touching door carried its own
`for-each-ref` query and read a `-quickdev` suffix nothing ever cut; now the twelve doors call
this and echo its two lines.

  ── WHY THESE CASES ────────────────────────────────────────────────────────────────────────
Line 1 is the WORD (a piped gate reports the pipe's status, not the script's), line 2 is the
landing cost the operator reads. ORIGIN decides: a local-only epic head is a cache, not a mode —
a stale local branch must not turn a trunk project back into an epic project. Two live epics is
AMBIGUOUS, exit 2: the doors already stop on more than one epic and this script must not pick.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir, run_script
import _pf_fixtures as pf

ROOT = SCRIPTS.parents[1]
SCRIPT = SCRIPTS / "epic_mode.py"


def run(repo: Path) -> tuple[int, list[str]]:
    rc, out = run_script("epic_mode.py", "--repo", str(repo))
    return rc, [ln for ln in out.splitlines() if ln.strip()]


def first(lines: list[str]) -> str:
    return lines[0].strip() if lines else ""


def second(lines: list[str]) -> str:
    return lines[1].strip() if len(lines) > 1 else ""


def main() -> int:
    c = Cases("epic_mode.py — the epic's mode as one query (SCC-446)")

    if c.block("A · TRUNK: no origin/epic/* at all"):
        with TempDir() as t:
            repo = pf.make_repo(t)
            rc, lines = run(repo)
            c.check("line 1 is the bare word TRUNK, exit 0",
                    first(lines) == "TRUNK" and rc == 0, f"rc={rc} {lines}")
            c.check("line 2 names the landing cost: main by a PR the operator merges",
                    "main" in second(lines) and re.search(r"PR|pull request", second(lines)) is not None,
                    second(lines))
            # ORIGIN decides. A local-only epic head is a cache, never a mode.
            pf.git(repo, "branch", "epic/SCC-1-epic-9-local-only")
            rc, lines = run(repo)
            c.check("⛔ a LOCAL-only epic head is NOT a mode: still TRUNK (origin decides)",
                    first(lines) == "TRUNK" and rc == 0, f"rc={rc} {lines}")

    if c.block("B · FULL: epic/<KEY>-epic-<N>-<slug> on origin"):
        with TempDir() as t:
            repo = pf.make_repo(t)
            pf.branch(repo, "epic/SCC-1-epic-2-x", {"docs/a.md": "a\n"}, push=True)
            rc, lines = run(repo)
            c.check("line 1 is `FULL epic/SCC-1-epic-2-x`, exit 0",
                    first(lines) == "FULL epic/SCC-1-epic-2-x" and rc == 0, f"rc={rc} {lines}")
            c.check("line 2: lands by PR into the epic, four checks, E2E on every landing",
                    "epic/SCC-1-epic-2-x" in second(lines) and "four checks" in second(lines)
                    and "every landing" in second(lines), second(lines))

    if c.block("C · LIGHT: the -light-epic- token, exactly what the ruleset and CI read"):
        with TempDir() as t:
            repo = pf.make_repo(t)
            pf.branch(repo, "epic/SCC-1-light-epic-2-x", {"docs/a.md": "a\n"}, push=True)
            rc, lines = run(repo)
            c.check("line 1 is `LIGHT epic/SCC-1-light-epic-2-x`, exit 0",
                    first(lines) == "LIGHT epic/SCC-1-light-epic-2-x" and rc == 0, f"rc={rc} {lines}")
            c.check("line 2: lands by PR into the epic, two checks, E2E once at /cicd-push-e2e",
                    "two checks" in second(lines) and "/cicd-push-e2e" in second(lines)
                    and "/cicd-e2e" in second(lines), second(lines))
            # ⛔ The token is `-light-epic-`, NOT the word `light` anywhere in the slug.
            pf.git(repo, "checkout", "-q", "main")
            pf.git(repo, "push", "-q", "origin", "--delete", "epic/SCC-1-light-epic-2-x")
            pf.branch(repo, "epic/SCC-1-epic-3-light-theme", {"docs/b.md": "b\n"}, push=True)
            rc, lines = run(repo)
            c.check("⛔ `light` in the SLUG is not the token: `epic/SCC-1-epic-3-light-theme` is FULL",
                    first(lines) == "FULL epic/SCC-1-epic-3-light-theme", f"rc={rc} {lines}")

    if c.block("D · AMBIGUOUS: two live epics is exit 2, never a pick"):
        with TempDir() as t:
            repo = pf.make_repo(t)
            pf.branch(repo, "epic/SCC-1-epic-2-x", {"docs/a.md": "a\n"}, push=True)
            pf.git(repo, "checkout", "-q", "main")
            pf.branch(repo, "epic/SCC-2-light-epic-3-y", {"docs/b.md": "b\n"}, push=True)
            rc, lines = run(repo)
            c.check("line 1 is AMBIGUOUS and the exit is 2",
                    first(lines) == "AMBIGUOUS" and rc == 2, f"rc={rc} {lines}")
            c.check("...and both refs are printed so the operator can see what to prune",
                    any("epic/SCC-1-epic-2-x" in ln for ln in lines[1:])
                    and any("epic/SCC-2-light-epic-3-y" in ln for ln in lines[1:]), str(lines))

    if c.block("E · breakage is ERROR, never a mode"):
        with TempDir() as t:
            notrepo = t / "plain"
            notrepo.mkdir()
            rc, lines = run(notrepo)
            c.check("a path that is not a git repo exits 2 with ERROR on line 1",
                    rc == 2 and first(lines) == "ERROR", f"rc={rc} {lines}")
        rc, out = run_script("epic_mode.py")
        c.check("--repo is required (no cwd default: cwd is not intent)", rc == 2, f"rc={rc}")
        src = SCRIPT.read_text(encoding="utf-8") if SCRIPT.exists() else ""
        # The one git call is `for-each-ref`; a `git(["fetch", …])` would be a network call the
        # door already made. Read as a code literal, not as a word in the docstring.
        c.check("the script makes no network call of its own (no fetch; the door fetched first)",
                bool(src) and '"fetch"' not in src and "'fetch'" not in src
                and 'git(["for-each-ref"' in src,
                "the door's Step 0 fetches with --prune, the script only reads the refs")

    if c.block("F · registered and called where the house looks"):
        idx = (ROOT / ".agents" / "scripts" / "INDEX.md").read_text(encoding="utf-8")
        c.check(".agents/scripts/INDEX.md carries a row for epic_mode.py", "`epic_mode.py`" in idx,
                "test_shape_scan.py precedent")
        cmds = ROOT / ".agents" / "commands"
        callers = sorted(p.name for p in cmds.glob("cicd-*.md")
                         if "epic_mode.py --repo" in p.read_text(encoding="utf-8"))
        c.check("twelve branch-touching cicd doors call it (the mode line at the top of Step 0)",
                len(callers) == 12, f"{len(callers)}: {callers}")
        own_query = sorted(p.name for p in cmds.glob("cicd-*.md")
                           if re.search(r"for-each-ref[^\n]*epic", p.read_text(encoding="utf-8")))
        c.check("⛔ no cicd door carries its own for-each-ref epic query any more",
                not own_query, str(own_query))

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
