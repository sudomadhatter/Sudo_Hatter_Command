"""TRUNK MODE — the third epic mode, and the guard it must NOT weaken (SCC-423).

AviationChat moved to trunk-based development on the operator's direction of 2026-09-06: Epic 24
phase 1 ships to `main`, and everything after it is built **from `main`** — story lanes cut from
`origin/main`, landing on `main` through a pull request the operator merges. No epic branch.

SCC-416 gave this system TWO epic modes and made the switch mechanical; SCC-441 named them FULL
and LIGHT, read from the third token of the branch name (`-epic-` or `-light-epic-`, right after
the key) by every door, impossible to drift from what the server enforces. This is the third, and
its switch is the same shape read one level up: **there is no `origin/epic/<KEY>-*` at all.** An
agent never chooses the mode and never infers it from prose.

  ── WHY A THIRD MODE AND NOT A REWRITE ─────────────────────────────────────────────────────
The two existing modes are still correct and still in use by every other project here. A rewrite
of the branch model to "stories land on main" would have silently re-pointed AviationChat's
siblings, and the epic-mode doctrine is load-bearing for them. So `trunk` is ADDITIVE: the doors
grow a third arm and the law grows a third bullet. (SCC-441 later folded the two epic arms into
ONE - FULL and LIGHT both land by a PR into the epic, and the direct-push arm is retired - so
the close-out door has two arms today, not three; block B pins that shape.) The control for the
guard claim is D1 below.

  ── ⛔ THE CONTROL THAT MATTERS MOST IS D1, AND IT ASSERTS ABSENCE OF CHANGE ────────────────
`merge-target-guard.sh` is an ARMED `commit-msg` hook that refuses known-bad merge topologies,
and one of them is `main:story` — a `claude/*` story lane merged LOCALLY onto `main`. The lazy
reading of trunk mode is "stories land on main now, so un-refuse that pair." **That would be
wrong, and it would delete the SCC-97 wrong-target protection on the one branch that is live
production.** A trunk landing is a PULL REQUEST, performed on GitHub's servers, where no local
hook runs at all — the guard is not in its way and never sees it. The pair it refuses is a
merge someone typed on this machine by accident, which is exactly as illegal as it was before.

The same reasoning keeps `story:main` on `allow`: absorbing `origin/main` into your own lane is
the everyday trunk-mode move, and it was already legal.

  ── WHY THE DOOR CHECKS READ ONLY FENCED CODE ──────────────────────────────────────────────
These door files are mostly prose and they DISCUSS `gh pr create` and `main` at length. A
document-wide substring search matches a sentence ABOUT a step and reports the step present when
it is not — the inversion `test_door_preflight_order.py` records. Only lines inside ``` fences
count as a step. `PROSE_ONLY` in block E is the control proving that distinction bites.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases

ROOT = SCRIPTS.parents[1]
RULES = ROOT / ".agents" / "rules"
COMMANDS = ROOT / ".agents" / "commands"

GIT_POLICY = RULES / "git-policy.md"
WORKTREE = RULES / "worktree-per-story.md"
CONSTITUTION = RULES / "constitution.md"
AGENTS = ROOT / "AGENTS.md"
GUARD = SCRIPTS / "git-hooks" / "merge-target-guard.sh"

CLOSE_STORY = COMMANDS / "cicd-close-story-merge-tree.md"
CREATE_EPIC = COMMANDS / "cicd-create-epic-sprint.md"
DEV_STORY = COMMANDS / "cicd-dev-story-tests.md"
PUSH_E2E = COMMANDS / "cicd-push-e2e.md"

# The word itself, as a MODE — not the English noun. `trunk` alone would match "trunk-based" in a
# stray sentence and, worse, would pass on a file that merely mentions it in a link.
TRUNK = re.compile(r"\btrunk\b", re.I)
# The switch, stated mechanically: the ABSENCE of an epic ref is what selects the mode. A door
# that says "if this is a trunk project" is prose an agent has to interpret; this is a git query.
SWITCH = re.compile(r"origin/epic/", re.I)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def fenced(text: str) -> str:
    """Only the lines inside ``` fences — a step is a command, never a sentence about one."""
    out, inside = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            inside = not inside
            continue
        if inside:
            out.append(line)
    return "\n".join(out)


def fences(text: str) -> list[str]:
    """Each ``` fence as its own block, so a check can ask for two things in the SAME fence."""
    out, cur, inside = [], [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            if inside:
                out.append("\n".join(cur))
                cur = []
            inside = not inside
            continue
        if inside:
            cur.append(line)
    return out


def names_trunk_mode(text: str) -> bool:
    """The mode is NAMED and its switch is MECHANICAL — both, or it is not a mode."""
    return bool(TRUNK.search(text)) and bool(SWITCH.search(text))


def main() -> int:
    c = Cases("trunk mode — the third epic mode (SCC-423)")

    policy = read(GIT_POLICY)
    guard = read(GUARD)

    if c.block("A · the LAW names three modes and the switch is mechanical"):
        c.check("git-policy.md exists and was read (an empty file is a FAIL, not a pass)",
                len(policy) > 2000, f"{len(policy)} bytes")
        # SCC-441: the modes are FULL / LIGHT / TRUNK — the words themselves, in capitals, the way
        # the kickoff names them. "full gate" inside a sentence is not the mode.
        for mode in ("FULL", "LIGHT", "TRUNK"):
            c.check(f"git-policy.md names the mode: {mode}",
                    re.search(rf"\b{mode}\b", policy) is not None,
                    "the three modes are the whole switch")
        for shape in ("epic/<KEY>-epic-<N>-<slug>", "epic/<KEY>-light-epic-<N>-<slug>"):
            c.check(f"git-policy.md names the branch shape: {shape}",
                    shape in policy, "the mode is the third token, right after the key")
        policy_fenced = fenced(policy)
        c.check("the mode token `-light-epic-` sits INSIDE the switch fence, beside `origin/epic/`",
                any(SWITCH.search(f) and "-light-epic-" in f for f in fences(policy)),
                "the switch is a git query plus the token it reads, never prose to interpret")
        c.check("the trunk switch is stated as a git ref query, not as prose to interpret",
                names_trunk_mode(policy), "expected `origin/epic/` near the trunk bullet")
        # SCC-441 retired the `-quickdev` direct-push mode: it was never cut, nothing read its
        # suffix, and the epic ruleset would refuse the push it described.
        for label, path in (("git-policy.md", GIT_POLICY), ("worktree-per-story.md", WORKTREE),
                            ("constitution.md", CONSTITUTION), ("AGENTS.md", AGENTS)):
            c.check(f"⛔ `quickdev` appears nowhere in {label} (the direct-push mode is retired)",
                    re.search(r"quickdev", read(path), re.I) is None,
                    "a retired mode named in the law is a mode an agent will try to select")
        c.check("⛔ no fence in git-policy.md pushes `HEAD:epic/` — the landing is a pull request",
                "HEAD:epic/" not in policy_fenced,
                "FULL and LIGHT alike land by PR into the epic; the direct push is gone")
        # ⭐ The freeze is SCC-416's whole point and trunk mode must not read as deleting it.
        c.check("⭐ the live-epic freeze on `main` SURVIVES the third mode",
                "freeze" in policy.lower() or "frozen" in policy.lower(),
                "a trunk project has no live epic; the freeze still governs every project that does")

    if c.block("B · every door grows a THIRD arm (fenced code only)"):
        close_fenced = fenced(read(CLOSE_STORY))
        c.check("close-out door: a fenced `gh pr create --base main` — the trunk landing",
                re.search(r"gh pr create[^\n]*--base main", close_fenced) is not None,
                "the trunk arm lands on main by PR, like the epic arm lands on the epic")
        # SCC-441/SCC-446: the epic arm is ONE arm for FULL and LIGHT alike - a PR into the epic
        # whose ruleset decides which checks run - and the direct-push arm (`-quickdev`) is gone.
        # No fence in the door may push `HEAD:epic/` any more: the epic ruleset refuses it.
        c.check("close-out door: the epic arm is a fenced `gh pr create --base epic/` and NO "
                "fence pushes `HEAD:epic/` (the direct-push arm is retired)",
                re.search(r"gh pr create[^\n]*--base epic/", close_fenced) is not None
                and "HEAD:epic/" not in close_fenced,
                "FULL and LIGHT land by PR into the epic; a HEAD:epic/ push is refused server-side")
        c.check("close-out door: names the trunk mode in prose so the arm can be SELECTED",
                names_trunk_mode(read(CLOSE_STORY)), "the arm is keyed on the mode")

        c.check("kickoff door: offers trunk as a third answer",
                names_trunk_mode(read(CREATE_EPIC)), "the mode is decided once, at kickoff")
        c.check("dev-story door: Step 0.6's epic-behind-main stop knows the trunk case",
                names_trunk_mode(read(DEV_STORY)),
                "there is no epic to be behind; the lane absorbs origin/main instead")
        c.check("ship door: says trunk mode has no epic to ship",
                names_trunk_mode(read(PUSH_E2E)),
                "/cicd-push-e2e must not be left looking like the trunk road")

    if c.block("C · the FLOOR anchors carry it (the anchor invariant)"):
        # A protocol rule is conditional; its LAW is not. Every gate git-policy carries is also
        # stated inline in AGENTS.md and constitution.md, so the stop binds in a session that
        # never opens the rule. A third mode that lives only in the protocol tier is a defect.
        c.check("AGENTS.md names the trunk landing",
                TRUNK.search(read(AGENTS)) is not None,
                "the floor must not describe a branch model the doors no longer follow")
        c.check("constitution.md names the trunk landing",
                TRUNK.search(read(CONSTITUTION)) is not None,
                "same invariant, second anchor")

    if c.block("D · ⛔ CONTROL — the armed guard was NOT weakened"):
        c.check("merge-target-guard.sh was read (an empty read would pass every check below)",
                len(guard) > 2000, f"{len(guard)} bytes")
        c.check("⛔ `main:story` is STILL refused — a LOCAL story-into-main merge stays illegal",
                re.search(r"main:story\)\s*echo refuse", guard) is not None,
                "a trunk landing is a PR on GitHub's servers; no local hook is in its way")
        c.check("`story:main` stays ALLOWED — absorbing main is the everyday trunk move",
                re.search(r"story:main\|story:epic\)\s*echo allow", guard) is not None,
                "already legal before this ticket; asserted so a later edit cannot drop it")
        wt = read(WORKTREE)
        c.check("worktree rule STILL carries the never-branch-a-story-from-main hard stop",
                re.search(r"NEVER branch a story worktree from `main`", wt) is not None,
                "the trunk exception qualifies this rule; it must not delete it")
        c.check("...and that hard stop now names the trunk exception in the same breath",
                names_trunk_mode(wt),
                "an unqualified hard stop and a third mode cannot both be followed")

    if c.block("E · the checks BITE (mutant controls)"):
        stripped = "\n".join(l for l in policy.splitlines() if not TRUNK.search(l))
        c.check("a policy with every trunk line removed FAILS the mode check",
                not names_trunk_mode(stripped),
                "proves block A is reading the text, not the filename")
        PROSE_ONLY = ("Some prose that merely discusses `gh pr create --base main` "
                      "without ever running it.\n")
        c.check("prose naming the landing OUTSIDE a fence is not a step",
                re.search(r"gh pr create[^\n]*--base main", fenced(PROSE_ONLY)) is None,
                "block B's fenced() is what makes its assertions mean anything")
        c.check("a guard with the refusal deleted FAILS the control",
                re.search(r"main:story\)\s*echo refuse",
                          guard.replace("main:story)                   echo refuse", "")) is None,
                "proves D is a real control and not a tautology")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
