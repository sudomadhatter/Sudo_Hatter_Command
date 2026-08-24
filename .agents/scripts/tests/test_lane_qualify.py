"""Which lane does this work belong in? (SCC-162)

`lane_qualify.py` answers one question mechanically, so an agent cannot answer it by
judgement: **is this the lightweight lane?** The operator's ruling that created the lane
(2026-08-15) is also its test — *"things that do not affect our development system"* — and
the whole point of putting it in a script is that the previous version of this rule lived in
prose and an agent talked itself past it.

  -- WHY EVERY CASE BELOW IS A REGRESSION, NOT A HAPPY PATH ---------------------------------
Four of these pin a specific way the check was found wrong before it shipped, in the plan's
own self-audit. They are the reason the file exists; deleting one re-opens a live hole.

  F9  a project repo must NEVER reach this lane, whatever its paths look like. The plan had
      command-centre-only as an IMPLICATION (Task-shaped, no deployable path) rather than a
      rule, so an agent standing in a project with a small doc change could reason its way
      in. Checked FIRST, before paths are even read.
  F3  `.agents/scripts/tests/` is EXEMPT in `sop_currency.classify()` - correctly, for its
      own question, because editing a test does not change what the operator types. Reusing
      that function as the safety test would therefore rate an edit to the ENFORCEMENT SUITE
      as safe. "Does this need a SOP update?" and "can this break something?" are different
      questions and this is where they diverge.
  F2  an empty path set must never read as LIGHT. "A check whose empty input reads as a
      pass" is a named tripwire in `/smh-self-audit` Phase 2, and here it is the whole
      ballgame: silence is the one input an agent controls completely.
  VCS the operator's own first example - "cleaning up a messy source control" - changes ZERO
      files, so F2's fix would have refused it. The split is UNKNOWN vs DECLARED: no --paths
      is unknown and stays TASK; an explicit --no-file-changes is a stated git-hygiene
      action and is checkable against `git diff` afterwards.

The drift case is the last one and it is the load-bearing one for the long run: this script
must never be MORE PERMISSIVE than the armed commit gate. It does not import that gate's
exemption list (see F3) - it cross-checks against it, so a future widening there cannot
silently widen the lane here.
"""
from __future__ import annotations

import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir, run_script

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sop_currency


def centre(root: Path) -> Path:
    """A repo SHAPED like the command centre: it holds `.agents/commands/` masters.

    Derived, never asserted by name. The centre owns workflow law and projects are thin
    (`thin-projects-center-owns-workflow-law`), so the command masters exist in exactly one
    repo - which makes their presence the honest test for "am I standing in the centre?"
    A hard-coded folder name would be wrong the first time the repo is cloned elsewhere.
    """
    (root / ".agents" / "commands").mkdir(parents=True, exist_ok=True)
    (root / ".agents" / "commands" / "smh-quick-fix.md").write_text("---\n---\n", encoding="utf-8")
    return root


def verdict(out: str) -> str:
    """The first bare token of output. The verdict is a WORD, not an exit code, because a
    piped gate reports the pipe's status and an agent reading only `$?` would misread it."""
    return (out.strip().splitlines() or [""])[0].strip()


c = Cases("lane_qualify - which lane is this work in?")

with TempDir() as tmp:
    if c.block("F9 - a project repo never reaches this lane"):
        proj = tmp / "project"
        (proj / "docs").mkdir(parents=True)
        # No .agents/commands/ - this is a thin project, not the centre.
        rc, out = run_script("lane_qualify.py", "--repo", str(proj), "--paths", "docs/guide.md")
        c.check("F9 a repo with no command masters refuses",
                verdict(out) == "NOT-COMMAND-CENTRE", out.strip()[:200])
        c.check("F9 the refusal names the cicd lanes as the answer",
                "cicd" in out.lower(), out.strip()[:200])

with TempDir() as tmp:
    root = centre(tmp / "centre")
    if c.block("HANDOFF - a deployable path is never a Task"):
        rc, out = run_script("lane_qualify.py", "--repo", str(root),
                             "--paths", "backend/api/routes.py")
        c.check("backend/ is HANDOFF", verdict(out) == "HANDOFF", out.strip()[:200])

    if c.block("SCC-118 - .github/ in the command centre is TASK, never HANDOFF"):
        # ⛔ THE REGRESSION THIS BLOCK EXISTS FOR, and it shipped for one review cycle.
        # `task_preflight.DEPLOY_DIRS` = PRODUCT_DIRS + (".github/",), and importing the
        # COMBINED list here recreated SCC-118 precisely: the command centre HAS a .github/
        # (the server-side half of the main write gate), it ships nothing, and a HANDOFF
        # verdict sends a toolkit change to /cicd-push-e2e - a cicd-* command barred from the
        # lobby by smh-target-resolution, running an E2E suite this repo does not have and
        # never will. "A verdict nobody could comply with", in task_preflight's own words.
        #
        # This lane is command-centre-ONLY by condition 0, and the centre ships nothing, so
        # PRODUCT_DIRS is the whole deployable question here. `.github/` is the development
        # system - CI and the gates - which is exactly what TASK means.
        rc, out = run_script("lane_qualify.py", "--repo", str(root),
                             "--paths", ".github/workflows/main-write-gate.yml")
        c.check("SCC-118 .github/ is TASK in the command centre",
                verdict(out) == "TASK", out.strip()[:200])
        # The control, so the narrowing above can never be mistaken for switching HANDOFF off.
        rc, out = run_script("lane_qualify.py", "--repo", str(root), "--paths", "frontend/app.tsx")
        c.check("SCC-118 control: a real product dir still HANDOFFs",
                verdict(out) == "HANDOFF", out.strip()[:200])

    if c.block("TASK - the toolkit is never LIGHT"):
        for p in (".agents/scripts/task_preflight.py", ".agents/rules/git-policy.md",
                  ".agents/commands/smh-quick-dev.md", ".githooks/pre-push", "AGENTS.md"):
            rc, out = run_script("lane_qualify.py", "--repo", str(root), "--paths", p)
            c.check(f"{p} is TASK", verdict(out) == "TASK", out.strip()[:160])

    if c.block("F3 - the enforcement suite is TASK, though sop_currency exempts it"):
        target = ".agents/scripts/tests/test_task_preflight.py"
        c.check("F3 precondition: sop_currency really does exempt it",
                sop_currency.classify(target) is None,
                "if this fails the finding changed shape - re-read it before editing below")
        rc, out = run_script("lane_qualify.py", "--repo", str(root), "--paths", target)
        c.check("F3 a test file is still TASK here", verdict(out) == "TASK", out.strip()[:200])

    if c.block("F2 - silence is never a pass"):
        rc, out = run_script("lane_qualify.py", "--repo", str(root))
        c.check("F2 no --paths is TASK, not LIGHT", verdict(out) == "TASK", out.strip()[:200])
        rc, out = run_script("lane_qualify.py", "--repo", str(root), "--paths")
        c.check("F2 an EMPTY --paths list is TASK too", verdict(out) == "TASK", out.strip()[:200])

    if c.block("LIGHT - the work the lane exists for"):
        for p in ("docs/guides/how-to-fly.md", "_my_resources/notes.md", "README.md"):
            rc, out = run_script("lane_qualify.py", "--repo", str(root), "--paths", p)
            c.check(f"{p} is LIGHT", verdict(out) == "LIGHT", out.strip()[:160])

    if c.block("VCS - a declared git-hygiene action changes zero files"):
        rc, out = run_script("lane_qualify.py", "--repo", str(root), "--no-file-changes")
        c.check("--no-file-changes is LIGHT-VCS", verdict(out) == "LIGHT-VCS", out.strip()[:200])
        # DECLARED, not inferred: the flag is a statement the agent makes and the close-out
        # can falsify against the real diff. Without it, the same empty input stays TASK.
        rc, out = run_script("lane_qualify.py", "--repo", str(root),
                             "--no-file-changes", "--paths", "docs/x.md")
        c.check("--no-file-changes CONTRADICTED by paths is refused",
                verdict(out) == "TASK", out.strip()[:200])

    if c.block("SCC-302 · size draws the lane - a one-liner and a rewrite are different work"):
        # ⛔ THE SCAR: classify() decided by PATH PREFIX alone, so a one-character fix and a
        # forty-file rewrite were indistinguishable - SCC-295 was one line in one function,
        # the operator asked for /smh-quick-fix, and the qualifier ejected it into a lane
        # that consumed a whole session. There was also nowhere to eject TO: the verdict set
        # had nothing between LIGHT and TASK.
        rc, out = run_script("lane_qualify.py", "--repo", str(root),
                             "--paths", ".agents/scripts/lane_qualify.py", "--lines", "1")
        c.check("C2 a ONE-LINE toolkit edit is TASK-LIGHT, not the full fan-out",
                verdict(out) == "TASK-LIGHT", out.strip()[:200])
        c.check("C2 ...and its exit stays in the TASK family (nonzero - never the light lane)",
                rc == 1, f"rc={rc}")
        rc, out = run_script("lane_qualify.py", "--repo", str(root),
                             "--paths", ".agents/scripts/a.py", ".agents/scripts/b.py",
                             ".agents/rules/c.md", "--lines", "400")
        c.check("C2 a multi-file toolkit rewrite stays TASK - different verdicts, same prefix",
                verdict(out) == "TASK", out.strip()[:200])
        # No --lines -> no size evidence -> the conservative verdict, exactly as before this
        # ticket. Silence about size is not smallness (the F2 principle, applied to the
        # second input an agent controls completely).
        rc, out = run_script("lane_qualify.py", "--repo", str(root),
                             "--paths", ".agents/scripts/lane_qualify.py")
        c.check("C2d WITHOUT --lines a toolkit path is still TASK - size silence is not small",
                verdict(out) == "TASK", out.strip()[:200])
        # A small edit to MANY files is not small work - the file count caps it too.
        rc, out = run_script("lane_qualify.py", "--repo", str(root),
                             "--paths", ".agents/scripts/a.py", ".agents/scripts/b.py",
                             ".agents/rules/c.md", "--lines", "3")
        c.check("C2e three files at one line each is TASK - the blast is the file count",
                verdict(out) == "TASK", out.strip()[:200])
        rc, out = run_script("lane_qualify.py", "--repo", str(root),
                             "--paths", "frontend/app.tsx", "--lines", "1")
        c.check("C3 a one-line change under PRODUCT_DIRS is still HANDOFF - size never buys "
                "an exception", verdict(out) == "HANDOFF", out.strip()[:200])
        proj2 = tmp / "sized-project"
        (proj2 / "docs").mkdir(parents=True, exist_ok=True)
        rc, out = run_script("lane_qualify.py", "--repo", str(proj2),
                             "--paths", "docs/x.md", "--lines", "1")
        c.check("C4 NOT-COMMAND-CENTRE keeps winning regardless of size",
                verdict(out) == "NOT-COMMAND-CENTRE", out.strip()[:200])
        rc, out = run_script("lane_qualify.py", "--repo", str(root),
                             "--paths", "docs/guide.md", "--lines", "1")
        c.check("C2f CONTROL: --lines does not disturb a LIGHT verdict",
                verdict(out) == "LIGHT", out.strip()[:200])

    if c.block("drift - never more permissive than the armed commit gate"):
        # Every path sop_currency calls a usage surface must come back non-LIGHT here.
        # Not an import of its list (F3): a cross-check, so widening THERE cannot quietly
        # widen the lane HERE - it fails this case instead.
        surfaces = [".agents/commands/x.md", ".agents/rules/x.md", ".agents/scripts/x.py",
                    ".agents/scripts/x.ps1", ".agents/scripts/git-hooks/commit-msg",
                    ".githooks/commit-msg", "AGENTS.md"]
        flagged = [p for p in surfaces if sop_currency.classify(p) is not None]
        c.check("drift precondition: the gate still flags these", len(flagged) == len(surfaces),
                f"gate flags {len(flagged)}/{len(surfaces)}: missing "
                f"{[p for p in surfaces if p not in flagged]}")
        # ⛔ `!= "LIGHT"` IS A VACUOUS GREEN AND THIS CASE SHIPPED THAT WAY FOR ONE RUN.
        # Before `lane_qualify.py` existed, every invocation printed a Python "can't open
        # file" error - which is not the string "LIGHT", so the case PASSED while the thing
        # under test did not exist. That is precisely the F2 hazard one level up, inside the
        # check written to guard against it. Membership in the KNOWN verdict set is what
        # makes a missing or broken script fail here instead of scoring.
        KNOWN_SAFE = {"TASK", "HANDOFF", "NOT-COMMAND-CENTRE"}
        leaked, unreadable = [], []
        for p in flagged:
            rc, out = run_script("lane_qualify.py", "--repo", str(root), "--paths", p)
            v = verdict(out)
            if v == "LIGHT":
                leaked.append(p)
            elif v not in KNOWN_SAFE:
                unreadable.append((p, v[:60]))
        c.check("no usage surface classifies as LIGHT", not leaked, f"leaked: {leaked}")
        c.check("every usage surface returns a KNOWN verdict (not an error)",
                not unreadable, f"unreadable: {unreadable}")

# ══ SCC-243 · a table can never fall behind the script again ═══════════════════════════
# ⭐ THIS IS THE ROW THAT STOPS RECURRENCE, and every other row on this ticket is a repair.
# `lane_qualify.py` grew `LIGHT-VCS` and `NOT-COMMAND-CENTRE` after its callers' tables were
# written, and nothing in the tree noticed: the script returns a verdict the command that ran
# it has no instruction for, so the agent improvises - which is exactly what putting the
# question in a script was meant to prevent.
#
# ⛔ THE CALLER LIST IS DISCOVERED, NEVER HARDCODED. A hardcoded list is the same defect one
# level up: the fourth command to call this script would be invisible to the guard written to
# protect it. Discovery is by INVOCATION (`lane_qualify.py --repo`), not by mention -
# `commands/INDEX.md` describes the verdicts in prose and calls nothing, and indicting a
# router for not carrying a table would teach the next person to delete the check.
if c.block("SCC-243 · every caller's verdict table lists every verdict the script can return"):
    import re as _re
    import lane_qualify  # noqa: E402

    # SCRIPTS is `.agents/scripts`; the commands live beside it.
    CMDS = SCRIPTS.parent / "commands"
    INVOKES = "lane_qualify.py " + "--repo"
    ROW = _re.compile(r"^\|\s*`([A-Z][A-Z0-9-]*)`\s*\|")

    def table_verdicts(text: str) -> set:
        """Every verdict this command's body documents an answer for."""
        return {m.group(1) for m in (ROW.match(ln) for ln in text.splitlines()) if m}

    callers = sorted(f for f in CMDS.glob("*.md")
                     if INVOKES in f.read_text(encoding="utf-8"))
    known = set(lane_qualify.VERDICTS)

    # P0 · ANTI-VACUITY, both ends. An empty caller list makes P1 pass by having nothing to
    # check, and an empty verdict set makes every table "complete". Neither is evidence.
    c.check("P0 the sweep found real callers, by invocation",
            len(callers) >= 3, f"found {len(callers)}: {[f.name for f in callers]}")
    c.check("P0 ...and the script really exposes a verdict set to compare against",
            len(known) >= 3, f"VERDICTS={known}")

    missing = {}
    for f in callers:
        gap = known - table_verdicts(f.read_text(encoding="utf-8"))
        if gap:
            missing[f.name] = sorted(gap)
    c.check("P1 no caller's table is missing a verdict the script can return",
            not missing,
            f"a command that runs this script and cannot read its answer: {missing}. "
            f"The script returns {sorted(known)}")

    # P2 · the parser itself, over synthetic bodies - because "no gaps found" is also what a
    # parser that reads nothing reports. Same function the live check runs.
    FULL = "\n".join(f"| `{v}` | do the thing |" for v in sorted(known))
    c.check("P2 CONTROL: a table listing all five reads complete",
            not (known - table_verdicts(FULL)), str(table_verdicts(FULL)))
    THIN = "\n".join(f"| `{v}` | do the thing |" for v in sorted(known)[:-1])
    c.check("P2 CONTROL: ...and dropping one row is CAUGHT",
            known - table_verdicts(THIN) == {sorted(known)[-1]},
            f"the parser must see the gap: {known - table_verdicts(THIN)}")
    c.check("P2 CONTROL: prose naming a verdict is not a table row",
            not table_verdicts("The script may answer `LIGHT-VCS` for git hygiene.\n"),
            "only a leading table cell counts, or documentation of the check satisfies it")


# ══ SCC-243 · the cicd- lane names what it refuses, from the AUTHORITY ═════════════════
# ⛔ THE VERDICT TABLE ABOVE CANNOT DO THIS JOB IN A CHILD PROJECT, and that is why this
# block exists. `NOT-COMMAND-CENTRE` is returned BEFORE any path is read (lane_qualify.py
# :107-112), so in the repo `/cicd-non-crit-pr-push` actually runs in, `TASK` and `HANDOFF`
# are unreachable - measured 2026-08-20: `--paths backend/api.py` and `--paths docs/notes.md`
# return the identical answer against the same project. The command therefore carries its own
# deployable-path check, and this is the row that keeps that check's list honest.
#
# ⭐ IMPORTED, NEVER RE-TYPED. A prose copy of a constant is a copy that goes stale in
# silence: add `worker/` to PRODUCT_DIRS and the command keeps refusing four of five.
if c.block("SCC-243 · the cicd- lane names every deployable prefix it will refuse"):
    import task_preflight  # noqa: E402

    body = (SCRIPTS.parent / "commands" / "cicd-non-crit-pr-push.md").read_text(
        encoding="utf-8")
    expected = tuple(task_preflight.PRODUCT_DIRS) + (task_preflight.CI_DIR,)

    # N0 · ANTI-VACUITY. An empty constant makes N1 pass by asking nothing.
    c.check("N0 the authority really exposes prefixes to name",
            len(expected) >= 5, f"{expected}")
    unnamed = [d for d in expected if d not in body]
    c.check("N1 every member of PRODUCT_DIRS (+ CI_DIR) is named in the command body",
            not unnamed,
            f"the lane refuses these and never says so: {unnamed}. Name them, or the "
            f"agent reads the check's output without knowing what it covers")

    # N2 · the body must cite the CONSTANT, not just happen to contain the strings - so the
    # next reader knows where the list came from and does not maintain a second copy.
    c.check("N2 ...and it says WHERE the list comes from",
            "PRODUCT_DIRS" in body and "task_preflight" in body,
            "a list with no cited authority is a list someone will edit in place")

    # N3 · the check the command tells you to run must actually be runnable from here.
    # ⛔ Without this the body could name a script that does not exist and N1/N2 stay green.
    c.check("N3 the constants the body cites are importable by the command's own snippet",
            hasattr(task_preflight, "PRODUCT_DIRS") and hasattr(task_preflight, "CI_DIR"),
            "the snippet imports both names; if either moves, the command breaks silently")


raise SystemExit(c.finish())
