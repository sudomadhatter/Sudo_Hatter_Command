"""test_door_preflight_order — the lobby's door to `main` must pre-flight, in the right ORDER.

Once a required status check guards `main`, a merge commit made on a machine cannot be pushed:
it has never been to GitHub, so it carries no check, and the ruleset refuses it. The door
therefore pushes that exact commit to a throwaway `gate/**` ref first, waits for the check, and
only then pushes `main` — checks attach to a COMMIT, so the green travels with it.

  ── SCC-183: THE LOBBY DOOR NO LONGER TAKES THIS ROAD ──────────────────────────────────────
`/smh-close-task-merge-tree` now opens a pull request and stops; the operator's click on
*Merge pull request* is the sign-off, and GitHub enforces `main-write-gate` before allowing it.
So for that door this file asserts **absence**: no token mint, no `git push origin main`, no
`gate/**` ref on its road — plus that the road it DOES take is `gh pr create`.

The ordering contract below still binds `/cicd-push-e2e`, which ships PROJECT epics and still
merges locally, and it still governs the mutant fixtures. Keeping it live matters: the reason
the wait must precede the mint is that the approval token has a 30-minute TTL
(`pre-push-main-approval.sh`, `TTL_SECONDS=1800`), so a slow CI run inserted between mint and
push silently eats the token's life and the push dies on "stale token" after all the work is
done. Required order, where it still applies:

    merge locally
    push HEAD to gate/main-<sha>          pre-flight
    wait for main-write-gate to go green   ← the wait lives HERE, before the clock starts
    mint the token                         ← still immediately before the push
    push main                              the local hook spends the token, unchanged
    delete the gate ref                    cleanup

  ── WHY THIS READS ONLY FENCED CODE ────────────────────────────────────────────────────────
These door files are mostly prose, and the prose discusses `git push origin main` and the token
at length. A document-wide substring search matches a sentence ABOUT the step and reports the
step present when it is not — the same inversion `[[comment-literals-invert-source-grep-tests]]`
records. Only lines inside ``` fences count, and `PROSE_ONLY` below is the control proving it.

And a "contains" search cannot see order at all, so every ordering claim here is an index
comparison with a reordered mutant to prove the comparison bites
(`[[source-grep-guards-cannot-see-order]]`).

  ── ONE DOOR, NOT TWO — AND THE SECOND ONE MUST STAY OUT ───────────────────────────────────
The SCC-118 plan said "both doors". Building it showed that is wrong, and the wrong version
would have been worse than doing nothing.

`/cicd-push-e2e` is a `cicd-*` command, so it binds exactly ONE PROJECT and never the lobby
(AGENTS.md § command naming law): it ships `epic/*` branches in project repos. Those repos do
not publish `main-write-gate`, and giving them the server-side half is a separate ticket in each
of their own trackers ([[cross-repo-work-needs-a-ticket-per-repo]]). A pre-flight wait there
would poll forever for a check that never appears — every AGY ship, a hang.

So: the ordering contract below covers `/smh-close-task-merge-tree`, the lobby's own door, and
there is a standing guard that the pattern has NOT been copied into `/cicd-push-e2e` by a later
well-meaning edit.

Stdlib only, no pytest.
"""
from __future__ import annotations

import sys
from pathlib import Path

from _harness import Cases

REPO = Path(__file__).resolve().parents[3]

# The lobby's door to `main`. This is the only door whose target repo publishes the check.
DOORS = {
    "/smh-close-task-merge-tree": REPO / ".agents/commands/smh-close-task-merge-tree.md",
}

# Ships PROJECT epics, never the lobby. Must NOT wait on a check its target does not publish.
PROJECT_DOOR = REPO / ".agents/commands/cicd-push-e2e.md"

# The check the ruleset requires — the doors must wait on this exact name, and
# test_main_write_gate_ci.py pins the same string against the workflow's job name.
CHECK_NAME = "main-write-gate"
GATE_REF = "gate/main-"


def code_lines(text: str) -> list[str]:
    """Executable lines inside ``` fences, in document order.

    Two things are discarded, both for the same reason — they TALK ABOUT the step instead of
    BEING it, and a substring search cannot tell the difference:

      * prose outside the fences (the door explains the token at length), and
      * `#` comments inside them. This one is not hypothetical: the door's pre-flight block
        opens with a comment naming `main-write-gate`, several lines ABOVE the command that
        pushes the gate ref. Counting it would make the order check read wait-before-push and
        fail a correct door — the same inversion as
        [[comment-literals-invert-source-grep-tests]], just pointing the other way.

    `COMMENT_ONLY_FENCE` and `PROSE_ONLY` are the controls that keep both halves honest.
    """
    out, inside = [], False
    for raw in text.splitlines():
        if raw.lstrip().startswith("```"):
            inside = not inside
            continue
        if not inside or raw.lstrip().startswith("#"):
            continue
        line = raw.split(" #", 1)[0].rstrip()
        if line.strip():
            out.append(line)
    return out


def idx(lines: list[str], needle: str) -> int:
    for i, line in enumerate(lines):
        if needle in line:
            return i
    return -1


def order_ok(lines: list[str], *needles: str) -> tuple[bool, str]:
    """Every needle present, and appearing in the given order."""
    seen = [(n, idx(lines, n)) for n in needles]
    missing = [n for n, i in seen if i < 0]
    if missing:
        return False, "missing: " + ", ".join(missing)
    positions = [i for _, i in seen]
    if positions != sorted(positions):
        return False, "wrong order: " + ", ".join(f"{n}@{i}" for n, i in seen)
    return True, ", ".join(f"{n}@{i}" for n, i in seen)


# A door whose ONLY mentions of the steps are in prose. Every check must report it BROKEN —
# if this ever passes, fence extraction has regressed and the live checks are matching sentences.
PROSE_ONLY = """\
# /some-door

First you push HEAD to gate/main-<sha> and wait for main-write-gate to go green.
Then run mint-push-token.sh and finally `git push origin main`, then
`git push origin --delete gate/main-<sha>` to clean up.
"""

# The live shape, but with the wait moved after the mint — the TTL hazard, and the mutation a
# plain "contains" check cannot distinguish from correct.
MUTANT_WAIT_AFTER_MINT = """\
```bash
git merge chore/SCC-1-x --no-ff -m "merge"
git push origin HEAD:refs/heads/gate/main-$SHA
sh .agents/scripts/git-hooks/mint-push-token.sh --command /x --branch chore/SCC-1-x --key SCC-1
gh api repos/o/r/commits/$SHA/check-runs --jq '.check_runs[]|select(.name=="main-write-gate")'
env -u GITHUB_TOKEN git push origin main
git push origin --delete gate/main-$SHA
```
"""

# A fence whose only mentions of the steps are shell comments. Must satisfy nothing.
COMMENT_ONLY_FENCE = """\
```bash
# push HEAD to gate/main-$SHA, wait for main-write-gate, then mint-push-token.sh
# and finally git push origin main, then git push origin --delete gate/main-$SHA
git status
```
"""

# ⛔ The mutant the ORDER check cannot see: the ceremony is untouched and perfectly ordered,
# it is simply still the DEFAULT road rather than break-glass. `order_ok` returns True on this.
MUTANT_CEREMONY_IS_STILL_DEFAULT = """\
# /some-door

## Step 3 — Merge to `main`

```bash
git merge chore/SCC-1-x --no-ff -m "merge"
git push origin HEAD:refs/heads/gate/main-$SHA
until gh api ... --jq '... main-write-gate ... .status' | grep -qx completed; do sleep 10; done
sh .agents/scripts/git-hooks/mint-push-token.sh --command /some-door
git push origin main
git push origin --delete gate/main-$SHA
```
"""

# The correctly-split shape, as a positive control for the same mechanism.
SPLIT_REFERENCE = """\
# /some-door

## Step 3 — Land it

```bash
gh pr create --base main --head "$BRANCH" --fill
```

## Break-glass — the local token push

```bash
git merge chore/SCC-1-x --no-ff -m "merge"
git push origin HEAD:refs/heads/gate/main-$SHA
until gh api ... --jq '... main-write-gate ... .status' | grep -qx completed; do sleep 10; done
sh .agents/scripts/git-hooks/mint-push-token.sh --command /some-door
git push origin main
git push origin --delete gate/main-$SHA
```

## Step 4 — after
"""

REQUIRED_ORDER = (GATE_REF, CHECK_NAME, "mint-push-token.sh", "git push origin main")

# ── SCC-183: the lobby door has ONE road, and the ceremony is GONE ─────────────────────────
# ⛔ THE ORDER CHECK ALONE CANNOT SEE A RELOCATION: move the whole ceremony under any
# heading and every needle is still present and still in order, so `REQUIRED_ORDER` stays
# GREEN while certifying a road the door no longer takes. `REQUIRED_ORDER` is therefore
# kept ONLY for the fixtures below and for `/cicd-push-e2e`, which still takes it. The
# live lobby door is checked by ABSENCE instead (source-grep guards cannot see ORDER's
# sibling: they cannot see SECTION).
BREAK_GLASS = "Break-glass"
DEFAULT_LANDER = "gh pr create"


def section(text: str, title: str) -> str:
    """The body under the first heading containing `title`, up to the next same-or-higher one.

    ⛔ FENCE-AWARE, and that is not defensive coding — it is the bug this had on the first run.
    A `#` at the start of a line inside a ```bash fence is a SHELL COMMENT, and the door's
    break-glass block opens with `# ── Pre-flight the SERVER-SIDE gate …`. Read as markdown that
    is an `<h1>`, i.e. a heading of *higher* level than `## Break-glass`, so extraction stopped
    two lines in and every break-glass assertion reported the ceremony MISSING — a door that had
    just been written correctly. Same family as [[comment-literals-invert-source-grep-tests]]:
    the literal a guard keys on appears in a comment first.
    """
    out: list[str] = []
    depth = None
    fenced = False
    for raw in text.splitlines():
        s = raw.lstrip()
        if s.startswith("```"):
            fenced = not fenced
            if depth is not None:
                out.append(raw)
            continue
        if s.startswith("#") and not fenced:
            level = len(s) - len(s.lstrip("#"))
            if depth is None:
                if title.lower() in s.lower():
                    depth = level
                continue
            if level <= depth:
                break
        if depth is not None:
            out.append(raw)
    return "\n".join(out)


def without(text: str, title: str) -> str:
    """The document with that section removed — i.e. the DEFAULT road."""
    body = section(text, title)
    return text.replace(body, "") if body else text


def main() -> int:
    c = Cases("door landing road (SCC-118 ordering; ONE road since SCC-183)")

    for label, path in DOORS.items():
        if not path.is_file():
            c.check(f"{label} · the door exists", False, str(path))
            continue
        text = path.read_text(encoding="utf-8")
        lines = code_lines(text)

        # ── the DEFAULT road is the PR door ────────────────────────────────────────────────
        default = code_lines(without(text, BREAK_GLASS))
        c.check(f"{label} · the DEFAULT road invokes {DEFAULT_LANDER}",
                idx(default, DEFAULT_LANDER) >= 0,
                "one command that prints a link — the ceremony this replaced could not run "
                "under the agent's permission layer at all (SCC-184)")
        c.check(f"{label} · the DEFAULT road does NOT mint a token",
                idx(default, "mint-push-token.sh") < 0,
                "a GitHub merge never touches this machine, so there is no push to gate")
        c.check(f"{label} · the DEFAULT road does NOT push main directly",
                idx(default, "git push origin main") < 0)
        c.check(f"{label} · the DEFAULT road does NOT push a gate/** ref",
                idx(default, GATE_REF) < 0,
                "the PR carries its own check run on GitHub; nothing is pre-flighted from here")

        # SCC-133: the flight event is recorded BEFORE the merge — after the merge the only tree
        # holding it is main's, and a write there is a main write outside the token. Still true
        # on the PR road: record it before anything lands.
        ok, detail = order_ok(lines, "flight_recorder.py", DEFAULT_LANDER)
        c.check(f"{label} · ORDER flight_recorder.py record → {DEFAULT_LANDER} (record is pre-merge)",
                ok, detail)

    # ── the standing guard on the OTHER door ───────────────────────────────────────────────
    # Not an oversight that this one has no pre-flight — a requirement. See the docstring.
    if PROJECT_DOOR.is_file():
        proj = code_lines(PROJECT_DOOR.read_text(encoding="utf-8"))
        c.check("/cicd-push-e2e does NOT wait on a check its target repo cannot publish",
                idx(proj, CHECK_NAME) < 0,
                "cicd-* binds a PROJECT, never the lobby; a wait there polls forever")
        c.check("/cicd-push-e2e still mints + pushes main unchanged",
                idx(proj, "mint-push-token.sh") >= 0 and idx(proj, "git push origin main") >= 0)

    # ── the controls ───────────────────────────────────────────────────────────────────────
    prose = code_lines(PROSE_ONLY)
    ok, _ = order_ok(prose, *REQUIRED_ORDER)
    c.check("control · prose describing the steps does NOT satisfy the check", not ok,
            "fence extraction regressed — these checks would match sentences, not commands")

    commented = code_lines(COMMENT_ONLY_FENCE)
    ok, _ = order_ok(commented, *REQUIRED_ORDER)
    c.check("control · shell comments naming the steps do NOT satisfy the check", not ok,
            "comment stripping regressed — a commented-out door would read as implemented")

    mutant = code_lines(MUTANT_WAIT_AFTER_MINT)
    present = all(idx(mutant, n) >= 0 for n in REQUIRED_ORDER)
    ok, detail = order_ok(mutant, *REQUIRED_ORDER)
    c.check("control · every step PRESENT in the mutant (so only order is isolated)", present)
    c.check("mutant caught · the wait moved after the mint (the TTL hazard)", not ok, detail)

    # ── SCC-183: controls for the SECTION mechanism ────────────────────────────────────────
    # ⛔ The mutant that matters here is the one `REQUIRED_ORDER` cannot see. In it the whole
    # ceremony is exactly as it always was — every needle present, perfect order — it is simply
    # NOT under a break-glass heading, i.e. it is still the default road. The order check calls
    # that green. Only the section split calls it what it is.
    mut = code_lines(MUTANT_CEREMONY_IS_STILL_DEFAULT)
    ok, _ = order_ok(mut, *REQUIRED_ORDER)
    c.check("control · the un-split mutant PASSES the old order check "
            "(so the new checks are the only thing catching it)", ok)
    mut_default = code_lines(without(MUTANT_CEREMONY_IS_STILL_DEFAULT, BREAK_GLASS))
    c.check("mutant caught · ceremony left on the DEFAULT road",
            idx(mut_default, "mint-push-token.sh") >= 0
            and idx(mut_default, DEFAULT_LANDER) < 0,
            "the section split is what sees this; the order check never can")

    # And the reverse control: a correctly-split door must not trip it.
    good_default = code_lines(without(SPLIT_REFERENCE, BREAK_GLASS))
    c.check("control · a correct door passes: lander present, ceremony absent",
            idx(good_default, DEFAULT_LANDER) >= 0
            and idx(good_default, "mint-push-token.sh") < 0)

    # ── AC-14b: the SEMANTIC check AC-14 structurally cannot make ──────────────────────────
    # All four doors + both SKILL.md launchers agree by construction — they are generated from
    # one source — so four consistent copies of a FALSE sentence agree perfectly. Part B makes
    # "invoking this is the operator's per-merge sign-off" false: the sign-off is now the click.
    stale = []
    for p in sorted(REPO.glob(".claude/skills/smh-*/SKILL.md")) \
            + sorted(REPO.glob(".agents/skills/smh-*/SKILL.md")) \
            + [REPO / ".agents/commands/smh-close-task-merge-tree.md",
               REPO / ".opencode/commands/smh-close-task-merge-tree.md",
               REPO / ".agents/commands/smh-merge-multiple-workingtrees.md",
               REPO / ".opencode/commands/smh-merge-multiple-workingtrees.md"]:
        if not p.is_file():
            continue
        body = p.read_text(encoding="utf-8").lower()
        if "merge-tree" not in p.name and "workingtrees" not in p.name and "smh-" not in str(p):
            continue
        # The false pairing: calling the LOCAL --no-ff merge the sign-off.
        if "--no-ff" in body and "sign-off" in body:
            for line in body.splitlines():
                if "sign-off" in line and "--no-ff" in line:
                    stale.append(f"{p.relative_to(REPO)}: {line.strip()[:80]}")
    c.check("AC-14b · no door still calls the LOCAL --no-ff merge the operator's sign-off",
            not stale, "; ".join(stale[:3]))


    # ══ SCC-193 · THE SIGN-OFF IS A DECISION, NOT A MERGE THE OPERATOR OWES ════════════════
    #
    # OPERATOR RULING, 2026-08-17, VERBATIM: "we also need to change the wording for closing
    # things out. right now it says the merge is mine. that is not correct, its my decisiton to
    # move forward with the push, is the wording that will stop causing confusion. lets fix that
    # too. the way I approve you to push or close is by saying approved or one of the 2 /
    # commands."
    #
    # And the mechanism DOES NOT CHANGE - operator, same day, asked which of two readings:
    # "i wording only". The click on *Merge pull request* stays a physical operator act; it is
    # HOW the decision reaches GitHub, not a task owed. SCC-183's "one click, one merge, held by
    # something that cannot be talked out of it" is untouched.
    #
    # ⛔ WHY THIS IS A GREP PIN AND NOT A NOTE. Slip #4 of six on SCC-164's landing was the
    # agent writing "Click Merge" and "re-invoke the door" into `## Your Actions` as OPERATOR
    # TASKS - and it wrote them because every surface it had read said the merge was the
    # operator's. The wording produced the defect; a wording fix nothing pins rots back.
    #
    # BOTH DIRECTIONS, because a one-way pin is satisfied by deleting the sentence entirely.
    if c.block("SCC-193 · the sign-off wording, pinned both directions"):
        SURFACES = (sorted(REPO.glob(".agents/rules/*.md"))
                    + sorted(REPO.glob(".agents/commands/*.md"))
                    + sorted(REPO.glob(".agents/skills/*/SKILL.md"))
                    + sorted(REPO.glob(".agents/workflows/*.md"))
                    + sorted(REPO.glob(".opencode/commands/*.md"))
                    + sorted(REPO.glob(".claude/skills/smh-*/SKILL.md"))
                    + sorted(REPO.glob(".agents/scripts/*.py"))
                    + sorted(REPO.glob("docs/_scc_sops_prds/*.md"))
                    + [REPO / "AGENTS.md"])

        # Each phrase makes the merge the operator's WORK. The ruling replaces every one.
        FORBIDDEN = (
            "the merge is the operator's",
            "the merge is yours",
            "the merge is mine",
            "click is the sign-off",
            "a product decision, a main merge",
            "things that only you can do",
            "you merge it",
        )
        # ⛔ NOT FORBIDDEN, AND THE REASON IS THE RULING ITSELF: "invoking it is the operator's
        # PER-MERGE SIGN-OFF" stays true. The operator's decision is given in exactly three
        # ways, and TWO OF THEM ARE INVOCATIONS - `/smh-close-task-merge-tree` and
        # `/cicd-push-e2e`. Banning that phrase would delete a true sentence from five surfaces
        # and leave the false ones standing. What the ruling retires is the merge described as
        # the operator's WORK, not the invocation described as their decision.
        # ⛔ THE ALLOW-LIST IS PAIRS, NAMED, WITH A REASON - never a whole file. A file-level
        # exemption is how a pin quietly stops covering the thing it was written for.
        ALLOW = {
            # this file: it must quote the retired phrases in order to forbid them
            ".agents/scripts/tests/test_door_preflight_order.py",
        }
        hits = []
        for path in SURFACES:
            rel = str(path.relative_to(REPO)).replace("\\", "/")
            if rel in ALLOW:
                continue
            for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace")
                                     .splitlines(), 1):
                low = line.lower()
                for bad in FORBIDDEN:
                    if bad in low:
                        hits.append(f"{rel}:{n}: {bad!r} in {line.strip()[:70]}")
        c.check("S5 no surface still says the merge is the operator's to perform",
                not hits, f"{len(hits)} hit(s): " + " | ".join(hits[:6]))

        # The positive half: the replacement sentence must actually BE somewhere, in the two
        # places an agent reads before it acts. Deleting the wrong sentence is not the fix.
        RULING = "decision to proceed is the sign-off"
        for rel in (".agents/rules/git-policy.md",
                    ".agents/commands/smh-close-task-merge-tree.md"):
            body = (REPO / rel).read_text(encoding="utf-8", errors="replace").lower()
            c.check(f"S5 ...and {rel} states the ruling positively",
                    RULING in body, f"missing: {RULING!r}")

        # And the three FORMS it takes, named where the door's Rule 1 is.
        door = (REPO / ".agents/commands/smh-close-task-merge-tree.md").read_text(
            encoding="utf-8", errors="replace")
        for form in ("`approved`", "/smh-close-task-merge-tree", "/cicd-push-e2e"):
            c.check(f"S5 ...and the door names the form: {form}", form in door)

    # ══ SCC-193 C · the door reads ITSELF from origin/main on --after-merge ════════════════
    #
    # SLIP #5 OF SIX. The agent followed an instruction its own lane had DELETED: it read the
    # door from a checkout that was behind `origin/main`, and the lane that had just merged had
    # rewritten that very file. `git fetch` had been run; the working tree was never pulled.
    # Nothing checks that the door text you are following is current - in the one command most
    # likely to be reading a file its own lane just changed.
    if c.block("SCC-193 C · --after-merge warns when the door text itself is stale"):
        door = (REPO / ".agents/commands/smh-close-task-merge-tree.md").read_text(
            encoding="utf-8", errors="replace")
        after = section(door, "Resuming after the operator")
        c.check("C1 the --after-merge road exists to check",
                bool(after.strip()), "section 'Resuming after the operator' not found")
        code = code_lines(after)
        c.check("C2 it measures the checkout against origin/main",
                any("rev-list" in ln and "HEAD..origin/main" in ln for ln in code),
                "the count must be MEASURED, not asserted: " + " | ".join(code[:6]))
        c.check("C3 ...and says the door text may be the PRE-merge copy",
                "behind origin/main" in after and "git show origin/main:" in after,
                "the remedy must name how to read the current door")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
