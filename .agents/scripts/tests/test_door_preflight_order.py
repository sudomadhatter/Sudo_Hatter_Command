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

  ── SCC-347: NEITHER DOOR TAKES IT NOW ─────────────────────────────────────────────────────
`/cicd-push-e2e` took that road until SCC-347 — it shipped PROJECT epics by merging locally,
minting the token and pushing. It now opens a PR and stops, exactly as this door does, so the
ordering contract below governs only the mutant FIXTURES. It is kept, not deleted, for two
reasons: the fixtures are the controls that prove `order_ok` bites, and the sequence records why
the wait had to precede the mint — the approval token has a 30-minute TTL
(`pre-push-main-approval.sh`, `TTL_SECONDS=1800`), so a slow CI run inserted between mint and
push silently ate the token's life and the push died on "stale token" after all the work was
done. Anyone re-introducing a local-merge road needs that, and it is cheaper to keep than to
rediscover. The historical order:

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

  ── BOTH DOORS TAKE THE PR ROAD; WHAT DIFFERS IS THE WAIT (SCC-118, then SCC-347) ──────────
The SCC-118 plan said "both doors" and building it showed that was wrong THEN, for one reason
that is still true and one that no longer is.

Still true: `/cicd-push-e2e` is a `cicd-*` command, so it binds exactly ONE PROJECT and never the
lobby (AGENTS.md § command naming law). A project publishes `main-write-gate` only once it files
its own ticket in its own tracker ([[cross-repo-work-needs-a-ticket-per-repo]]) — AVCH-111 for
AGY. A pre-flight WAIT there would poll forever for a check that may never appear: every ship, a
hang. So the wait, the `gate/**` ref and the token stay out of that door, and the standing guard
below is what keeps a later well-meaning edit from copying them in.

No longer true: that this justified leaving the LOCAL MERGE in place there. It did not. The token
guards a push from a machine here; it is structurally absent from a merge made on GitHub's
servers, which is the road a web or mobile session takes. Measured 2026-08-31, AGY `main` carried
no protection and no ruleset at all, so that road into a production repo was guarded by nothing
while the token guarded a push nobody was making. SCC-347 gave `/cicd-push-e2e` the same PR shape
this door has: gate locally, push the gated tip, `gh pr create`, STOP, and `--after-merge` to
finish. The guard on it is therefore now the SAME absence assertions as the DOORS loop, MINUS the
check-wait rows.

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
    # SCC-393. This door lands a permission harvest under the exemption in
    # artifacts-always-first.md, so it reaches `main` on its own road and the absence
    # assertions below are the ONLY thing standing between that road and a self-merge.
    # It was written once WITH the token road (checkout main -> merge --no-ff -> mint ->
    # push origin main) and the suite stayed green purely because this dict did not name
    # it - the invariant in this file's docstring said "no live door takes that road" and
    # was false while it said so. Naming it here is what makes the sentence true.
    "/smh-llm-approvals": REPO / ".agents/commands/smh-llm-approvals.md",
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


def fold_continuations(lines: list[str]) -> list[str]:
    """Fenced lines joined across trailing `\\` — one shell command, one string.

    ⛔ WRITTEN BECAUSE THE FIRST CUT OF THE SCC-211 CHECK WAS BRITTLE (caught by its own red).
    "the door invokes X with flag F" was asserted as *one line containing both*, and a legal
    continuation — the way every multi-flag call in these doors is actually formatted — put
    the command and the flag on different lines. The predicate failed a door that was
    correct.

    That is worse than a gap: a guard a legitimate formatting choice breaks is a guard the
    next author reformats around, and this file already carries two lessons of the same
    family (a comment matching first, a `contains` that cannot see order). The question the
    check MEANS to ask is about the logical command, so the reader is made to see logical
    commands. `NO_FLAG` below is the control proving it did not become "the flag appears
    somewhere".
    """
    out: list[str] = []
    pending = ""
    for line in lines:
        stripped = line.rstrip()
        if stripped.endswith("\\"):
            pending += stripped[:-1].rstrip() + " "
            continue
        out.append((pending + stripped.strip()) if pending else line)
        pending = ""
    if pending:
        out.append(pending.strip())
    return out


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
# kept ONLY for the fixtures below — since SCC-347 NO live door takes that road. The
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

    # ⛔ EVERY `c.check` HERE SITS UNDER A `c.block` GUARD (test_suite_runner's ORPHAN
    # rule): an unguarded check runs under EVERY `--case` filter and counts toward every
    # filtered tally, so a mutant it kills is attributed to whichever case was named. The
    # guards arrived when SCC-193 wired the first block into this file. Fixtures the blocks
    # share stay at module level, where a filtered run can still see them.
    if c.block("LIVE · the live doors take the road the model says"):
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

        # ── the OTHER door takes the same road, since SCC-347 ──────────────────────────────────
        # `/cicd-push-e2e` ships PROJECT epics, and until SCC-347 it reached `main` the way this
        # file's ordering contract describes: merge locally, mint the single-use token, push. That
        # was the shape SCC-183 deleted on the lobby door, kept here on the reasoning that a
        # project publishes no check to wait for — true, and it answered the wrong question. The
        # token guards a push FROM A MACHINE HERE; it is structurally absent from a merge performed
        # on GitHub's servers, which is the road a web or mobile session takes.
        #
        # Measured 2026-08-31, before the reshape: AGY `main` carried no ruleset and no protection
        # (`gh api repos/{owner}/{repo}/branches/main/protection` -> 404 "Branch not protected"),
        # so the web-merge road into a PRODUCTION repo was guarded by nothing at all, while the
        # local token diligently guarded a push the operator had stopped making. Same hole as PR #2
        # (SCC-118), one repo over.
        #
        # ⭐ WHAT STAYS TRUE IS THE WAIT, AND ONLY THE WAIT. A `cicd-*` command binds a PROJECT,
        # and a project publishes `main-write-gate` only once it files its own ticket in its own
        # tracker (AVCH-111 for AGY). A wait here still polls forever for a check that may never
        # appear — so this door opens the PR and STOPS, and whatever ruleset the target repo has
        # is what gates the click. That asymmetry is the reason this guard is not simply the
        # DOORS-loop assertions applied to a second path.
        if PROJECT_DOOR.is_file():
            proj = code_lines(PROJECT_DOOR.read_text(encoding="utf-8"))
            c.check("/cicd-push-e2e does NOT wait on a check its target repo cannot publish",
                    idx(proj, CHECK_NAME) < 0,
                    "cicd-* binds a PROJECT, never the lobby; a wait there polls forever")
            c.check(f"/cicd-push-e2e · the road IS {DEFAULT_LANDER}",
                    idx(proj, DEFAULT_LANDER) >= 0,
                    "the door hands back a link and stops; the click is how the sign-off reaches "
                    "GitHub")
            c.check("/cicd-push-e2e does NOT mint a token",
                    idx(proj, "mint-push-token.sh") < 0,
                    "a merge on GitHub never touches this machine, so there is no push to gate")
            c.check("/cicd-push-e2e does NOT push main directly",
                    idx(proj, "git push origin main") < 0,
                    "production `main` advances by the operator's click, not by this command")
            c.check("/cicd-push-e2e does NOT push a gate/** ref",
                    idx(proj, GATE_REF) < 0,
                    "a pre-flight ref exists to carry a green onto a LOCAL merge commit; there "
                    "is no local merge commit on this road")
            # ⛔ THE PAIR IS THE POINT. Absence alone is satisfiable by a door that does nothing
            # after the PR — which would leave the epic ticket open, the branch unpruned and the
            # deploy unwatched, and every absence check above would still be green.
            c.check("/cicd-push-e2e verifies the landed merge with plain git (--after-merge)",
                    idx(proj, "merge-base --is-ancestor") >= 0,
                    "the resume half must PROVE the merge landed before it moves the ticket; "
                    "`gh` is not required for that half, so it works on any machine")

            # ⛔ THE ABSENCES ABOVE REMOVE THE CEREMONY'S ACCESSORIES, NOT ITS ROAD. A door that
            # does `git checkout main && git merge --no-ff epic/<KEY>-<slug>` right before the tip
            # push, and opens the PR anyway, trips NOT ONE of them: it mints nothing (the token is
            # what a `main` PUSH wants, and this variant lets the PR carry the merge), it never
            # writes `git push origin main`, and it publishes no gate ref. That mutant SURVIVED
            # this file at 53/53 until this row — the guard certified an absence set while the
            # thing the absences exist to forbid walked through the middle of it.
            #
            # The needle is the merge SOURCE, and it has to be: `git merge origin/main` at Step 2
            # is the ABSORB, it is required, and a blanket "no `git merge`" would refuse the
            # correct door. `git checkout main` is required too — the resume half stands on `main`
            # after the click. So what is forbidden is naming the epic as a merge source.
            c.check("/cicd-push-e2e does NOT merge the epic LOCALLY",
                    idx(proj, "git merge epic/") < 0 and idx(proj, "git merge --no-ff") < 0,
                    "the absorb (`git merge origin/main`) is the only merge on this road; an "
                    "`epic/ -> main` merge here is the retired ceremony wearing the PR's clothes")
            # ⛔ AND THE PAIR AGAIN, one level down. `--after-merge` is asserted above only by its
            # ancestor check — a resume half that proves the merge and then stops leaves a shipped
            # epic's branch on `origin` forever, and every check in this guard stays green.
            c.check("/cicd-push-e2e PRUNES the epic branch after the merge lands",
                    idx(proj, "git push origin --delete epic/") >= 0,
                    "the resume half owns the cleanup; the door that opened the branch is the "
                    "one that closes it")

    if c.block("CONTROLS · the fence/comment readers and the ordering mutants"):
        # ⛔ COMPUTED HERE, NOT IN THE BLOCK ABOVE. `prose`/`ok` used to be assigned at the tail
        # of the LIVE block and read here, which is fine unfiltered and an UnboundLocalError
        # under `--case CONTROLS` - a sibling block simply does not run. That crash reads as a
        # non-zero exit, which a mutation sweep scores as KILLED: a false kill for every mutant
        # aimed at this block, i.e. the guards here would have looked pinned while proving
        # nothing. (SCC-156 paid for that lesson with five files; the LIVE block's own comment
        # states the rule this violated.)
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

    if c.block("AC-14b · no door calls the LOCAL --no-ff merge the sign-off"):
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
                    # ⛔ AND THE NESTED STEP FILES. `*/SKILL.md` misses
                    # `code-review-engine/steps/*.md`, which this very lane edited - the
                    # engine's step bodies are read by an agent about to act, so a retired
                    # sentence there is exactly as live as one in a command (blind lens, F8).
                    + sorted(REPO.glob(".agents/skills/*/steps/*.md"))
                    + sorted(REPO.glob(".claude/skills/*/steps/*.md"))
                    + sorted(REPO.glob(".agents/workflows/*.md"))
                    + sorted(REPO.glob(".opencode/commands/*.md"))
                    + sorted(REPO.glob(".claude/skills/smh-*/SKILL.md"))
                    + sorted(REPO.glob(".agents/scripts/*.py"))
                    # ⛔ tests/ TOO. The first cut globbed `scripts/*.py` only, and a retired
                    # phrase sat in a test comment under `.agents/` for the whole lane - a
                    # scope hole is indistinguishable from a clean sweep (acceptance audit,
                    # gap 2).
                    + sorted(REPO.glob(".agents/scripts/tests/*.py"))
                    + sorted(REPO.glob("docs/_scc_sops_prds/*.md"))
                    + [REPO / "AGENTS.md"])

        # Each phrase makes the merge the operator's WORK. The ruling replaces every one.
        FORBIDDEN = (
            "the merge is the operator's",
            "the merge is yours",
            "the merge is mine",
            # ⛔ NOT the literal "click is the sign-off": the SOP's own table row read "That
            # click is YOUR sign-off" and slipped through the whole lane on one interposed
            # word (acceptance audit, gap 1). The phrase is the CLAIM, not a fixed string.
            "click is the sign-off",
            "click is your sign-off",
            "that click is the",
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
        ALLOW_FILES = {
            # this file: it must quote the retired phrases in order to forbid them
            ".agents/scripts/tests/test_door_preflight_order.py",
        }
        # ⛔ PAIRS, NOT FILES. A whole-file exemption stops covering the thing the pin was
        # written for; a (file, phrase) pair with a reason stays auditable. These are FIXTURE
        # DATA - SCC-164's actual rows, quoted verbatim so `ceremony_rows` can be proved to
        # REFUSE them. A test that cannot quote the defect cannot test the defect.
        ALLOW_PAIRS = {
            (".agents/scripts/tests/test_jira_feed.py", "that click is the"),
            (".agents/scripts/tests/test_jira_feed.py", "click is the sign-off"),
        }
        hits = []
        for path in SURFACES:
            rel = str(path.relative_to(REPO)).replace("\\", "/")
            if rel in ALLOW_FILES:
                continue
            for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace")
                                     .splitlines(), 1):
                low = line.lower()
                for bad in FORBIDDEN:
                    if bad in low and (rel, bad) not in ALLOW_PAIRS:
                        hits.append(f"{rel}:{n}: {bad!r} in {line.strip()[:70]}")
        c.check("S5 no surface still says the merge is the operator's to perform",
                not hits, f"{len(hits)} hit(s): " + " | ".join(hits[:6]))

        # ⛔ THE NEGATIVE CONTROL A LIVE SWEEP CANNOT DO WITHOUT. `hits` is built by scanning
        # the real tree, so a PASS is by definition a run that found nothing - and a broken
        # predicate, an empty SURFACES list or a typo'd phrase reads exactly the same as a
        # clean tree. The sibling block written in this same lane already carries this control
        # (`U6d`); the blind lens found this one without it. Fabricate an offender and require
        # the same predicate to fire on it.
        FAKE = ("Step 9: the operator performs the merge, so click **Merge** on the PR "
                "and that click is the sign-off.\n")
        fired = [bad for bad in FORBIDDEN if bad in FAKE.lower()]
        c.check("S5 CONTROL: the same predicate FIRES on a fabricated offending line",
                bool(fired) and bool(FORBIDDEN) and bool(SURFACES),
                f"FORBIDDEN={len(FORBIDDEN)} SURFACES={len(SURFACES)} fired={fired}")

        # The positive half: the replacement sentence must actually BE somewhere, in the two
        # places an agent reads before it acts. Deleting the wrong sentence is not the fix.
        # ⛔ AND THE HAND-AUTHORED SKILL. `.claude/skills/smh-close-task-merge-tree/SKILL.md`
        # is exempt from door parity because the sync never rewrites it - which is exactly why
        # it is the surface most likely to keep a retired sentence, and it did (this lane's own
        # finding #3). Exempt from parity is not exempt from being current.
        # ⛔ AND THE PRODUCTION DOOR (SCC-211). The ruling names three forms and TWO OF THEM
        # ARE INVOCATIONS, one of which is `/cicd-push-e2e` - so the one command the ruling
        # names by name was the one surface that never carried it, and contradicted it
        # instead: its Step 4 mint comment demanded the operator's verbatim this-turn merge
        # words and said "No such words this turn -> STOP and ask". An operator who typed
        # only `/cicd-push-e2e` had given the sign-off in one of its three legal forms and
        # was asked for it again - or the agent invented a quote for `--operator-approval`,
        # since `mint-push-token.sh` REFUSES non-interactively without one.
        RULING = "decision to proceed is the sign-off"
        for rel in (".claude/skills/smh-close-task-merge-tree/SKILL.md",
                    ".agents/rules/git-policy.md",
                    ".agents/commands/smh-close-task-merge-tree.md",
                    ".agents/commands/cicd-push-e2e.md"):
            body = (REPO / rel).read_text(encoding="utf-8", errors="replace").lower()
            c.check(f"S5 ...and {rel} states the ruling positively",
                    RULING in body, f"missing: {RULING!r}")

        # And the three FORMS it takes, named where each door's Rule 1 is. BOTH doors: a
        # ruling stated in one door and contradicted in the other is not stated.
        for rel in (".agents/commands/smh-close-task-merge-tree.md",
                    ".agents/commands/cicd-push-e2e.md"):
            door = (REPO / rel).read_text(encoding="utf-8", errors="replace")
            for form in ("`approved`", "/smh-close-task-merge-tree", "/cicd-push-e2e"):
                c.check(f"S5 ...and {rel} names the form: {form}", form in door)

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

    # ══ SCC-211 · THE PRODUCTION DOOR PRE-FLIGHTS BEFORE IT WRITES OR GATES ═══════════════
    #
    # `/cicd-push-e2e` is the only command that writes production `main`, and it was the only
    # door that ran NO mechanical precheck: both siblings call one first
    # (`cicd-close-story-merge-tree.md` Step 0.6, `smh-close-task-merge-tree.md` Step 1),
    # while this one resolved a branch from `git branch -a`, asked the operator to "confirm
    # it by name", and started merging.
    #
    # THE DEFECT, STATED AS A SEQUENCE: uncommitted changes sit in the epic checkout; Step 3
    # gates that dirty tree GREEN; Step 4 merges the BRANCH, which does not contain them.
    # What shipped to production was never gated, and the door could not say so.
    #
    # ⛔ WHY ORDER, NOT PRESENCE. A precheck placed after `git merge origin/main` is not a
    # precheck - the first write has already happened, on the tree the gate is about to
    # measure. Presence-only would be GREEN on exactly the arrangement that fails, which is
    # this file's founding lesson ([[source-grep-guards-cannot-see-order]]); the CONTROLS
    # below are the mutants that prove the comparison bites.
    if c.block("SCC-211 · /cicd-push-e2e pre-flights BEFORE it writes or gates"):
        text = PROJECT_DOOR.read_text(encoding="utf-8", errors="replace")
        lines = code_lines(text)
        logical = fold_continuations(lines)

        # P1 · the precheck is a COMMAND the door runs, not a paragraph about prechecks.
        c.check("P1 the door RUNS ship_preflight.py (fenced, not prose)",
                idx(lines, "ship_preflight.py") >= 0,
                "prose describing a check is not a check: " + " | ".join(lines[:4]))
        # ⛔ ALL THREE OPERANDS, not just the pinned key. The script REQUIRES `--repo`,
        # `--branch` and `--expect-key`, so a door that drops one has written a fenced command
        # that dies on argparse the first time anyone runs it — and the order checks below
        # would stay green, because the needle they look for is the script name. Two mutants
        # survived this block before these rows existed: one deleting `--branch "$BRANCH" \`,
        # one swapping `--repo "$PROJECT_ROOT"` for `--repo .` (which re-opens "cwd is not
        # intent" in the one command that writes production).
        for flag, why in (("--expect-key", "without the pinned key the script can only ever "
                                           "return an honest verdict about the WRONG branch"),
                          ("--branch", "the script requires it; a door missing it has written "
                                       "a command that cannot run"),
                          ("--repo", "`--repo .` is cwd, and cwd is not intent - the door "
                                     "runs from the lobby and must name PROJECT_ROOT")):
            c.check(f"P1 ...and passes {flag}",
                    any("ship_preflight.py" in ln and flag in ln for ln in logical), why)
        c.check("P1 ...and it is PROJECT_ROOT that is passed, never a bare cwd",
                any("ship_preflight.py" in ln and "PROJECT_ROOT" in ln for ln in logical),
                "a preflight aimed at the wrong repo returns an honest verdict about it")

        # P7 · the STOP is the gate's teeth, and it was unpinned: replacing
        # `Exit 2 → STOP.` with "It is informational." left this whole block green, which
        # would ship a door that RUNS the precheck and then ignores it — the SCC-211 defect
        # wearing the fix's clothes.
        step15 = section(text, "Step 1.5")
        c.check("P7 Step 1.5 says a refusal STOPS the command",
                "exit 2" in step15.lower() and "STOP" in step15,
                "a precheck whose refusal is advisory is not a precheck: "
                + step15.strip()[:160])

        # P2 · the ordering claim, the whole reason this is a preflight. ⭐ SCC-347 REPOINTED
        # ITS TAIL, NOT ITS HEAD. The head — preflight BEFORE the first write — is the SCC-211
        # defect and is untouched. The tail was `mint -> push main`; on the PR road the last two
        # steps are pushing the gated epic TIP and opening the PR against it, and their order
        # matters for the same reason the old pair's did: `gh pr create --head <branch>` on an
        # unpushed branch is an error, so a door that opens the PR first has written a ceremony
        # that cannot run.
        ok, detail = order_ok(lines, "ship_preflight.py", "git merge origin/main",
                              "git push origin epic/", DEFAULT_LANDER)
        c.check("P2 ORDER preflight -> absorb main -> push the epic tip -> open the PR", ok, detail)

        # P6 · the key is PINNED before any tool has answered anything. A key read off the
        # branch the door just resolved cannot disagree with it - the check would compare a
        # value with itself, which is the circularity this whole file exists to refuse.
        ok, detail = order_ok(lines, "EXPECTED_KEY=", "ship_preflight.py")
        c.check("P6 ORDER EXPECTED_KEY pinned -> then the preflight reads it", ok, detail)

        # P3/P4 · the chore branch: admitted at Step 1 and then named nowhere after it.
        step1 = section(text, "Step 1 ")
        c.check("P3 Step 1 conditions the chore admission on the DIFF",
                "deployable" in step1.lower(),
                "git-policy.md routes only the deployable-touching chore diff here")
        c.check("P3 ...and hands the rest to the Task door",
                "/smh-close-task-merge-tree" in step1,
                "a docs-only chore lane landing here skips the whole Task ceremony - "
                "manifest, `## Your Actions`, Dev Record, ticket move, prune")
        c.check("P4 ...and a chore lane that legitimately stays has a written procedure",
                "substitutes" in step1 and "chore/<JIRA-KEY>-<slug>" in step1,
                "every operative line after the admission names only epic/*, including the "
                "mint's --branch - which is what the token records as WHAT is being landed")

        # P5 · the sign-off contradiction, both directions.
        step4 = section(text, "Step 4")
        c.check("P5 Step 4 treats THIS TURN's invocation as the approval evidence",
                "invocation this turn" in step4.lower(), step4.strip()[:200])
        c.check("P5 ...and the door no longer demands words the ruling says were given",
                "No such words this turn" not in text,
                "the operator typed one of the ruling's three forms; asking again is the "
                "contradiction, and inventing a quote for --operator-approval is worse")

        # ── CONTROLS · each predicate above, fired at a door built to fail it ──────────────
        # A live sweep can only prove the tree is currently clean. These are the mutants.
        GOOD = ("# /d\n\n```bash\nEXPECTED_KEY=SCC-00\n"
                "python3 .agents/scripts/ship_preflight.py --expect-key \"$EXPECTED_KEY\"\n"
                "git merge origin/main\ngit push origin epic/KEY-slug\n"
                "gh pr create --base main\n```\n")
        good = code_lines(GOOD)
        c.check("CONTROL: the reference door passes P2 and P6",
                order_ok(good, "ship_preflight.py", "git merge origin/main",
                         "git push origin epic/", DEFAULT_LANDER)[0]
                and order_ok(good, "EXPECTED_KEY=", "ship_preflight.py")[0])

        RELOCATED = ("# /d\n\n```bash\nEXPECTED_KEY=SCC-00\ngit merge origin/main\n"
                     "python3 .agents/scripts/ship_preflight.py --expect-key \"$EXPECTED_KEY\"\n"
                     "mint-push-token.sh\ngit push origin main\n```\n")
        c.check("CONTROL: a preflight RELOCATED below the first write is caught",
                not order_ok(code_lines(RELOCATED), "ship_preflight.py",
                             "git merge origin/main")[0],
                "presence is unchanged and every needle is still there - only ORDER moved, "
                "which is exactly the mutation a `contains` check cannot see")

        # ⛔ P2's TAIL NEEDS ITS OWN MUTANT. `RELOCATED` above fires at the HEAD of the sequence
        # (the SCC-211 defect) and would still pass if the new tail were unordered — so until
        # this fixture the two steps SCC-347 added to P2 were carried by the head's control.
        # The failure it isolates is real and immediate: `gh pr create --head <branch>` against a
        # branch that was never pushed is an error, so a door in this order has written a ceremony
        # that cannot run on the first try.
        PR_FIRST = ("# /d\n\n```bash\nEXPECTED_KEY=SCC-00\n"
                    "python3 .agents/scripts/ship_preflight.py --expect-key \"$EXPECTED_KEY\"\n"
                    "git merge origin/main\ngh pr create --base main\n"
                    "git push origin epic/KEY-slug\n```\n")
        pr_first = code_lines(PR_FIRST)
        c.check("CONTROL: every P2 step is PRESENT in the tail mutant (so only order is isolated)",
                all(idx(pr_first, n) >= 0 for n in ("ship_preflight.py", "git merge origin/main",
                                                    "git push origin epic/", DEFAULT_LANDER)))
        c.check("CONTROL: a door that opens the PR BEFORE pushing the tip is caught",
                not order_ok(pr_first, "ship_preflight.py", "git merge origin/main",
                             "git push origin epic/", DEFAULT_LANDER)[0],
                "the head is in perfect order here - only the two steps SCC-347 added moved, "
                "which is the half `RELOCATED` cannot see")

        PROSE = ("# /d\n\nRun `ship_preflight.py` first, then absorb main.\n\n"
                 "```bash\ngit merge origin/main\nmint-push-token.sh\n"
                 "git push origin main\n```\n")
        c.check("CONTROL: a door that only TALKS about the preflight is caught",
                idx(code_lines(PROSE), "ship_preflight.py") < 0,
                "the sentence is true and the door still never runs it")

        PINNED_LATE = ("# /d\n\n```bash\n"
                       "python3 .agents/scripts/ship_preflight.py --expect-key \"$EXPECTED_KEY\"\n"
                       "EXPECTED_KEY=SCC-00\n```\n")
        c.check("CONTROL: a key pinned AFTER the preflight reads it is caught",
                not order_ok(code_lines(PINNED_LATE), "EXPECTED_KEY=",
                             "ship_preflight.py")[0],
                "an unset variable is an empty --expect-key, and an empty operand is never "
                "a pass")

        # ── CONTROLS for `fold_continuations` · both directions ────────────────────────────
        # It exists so a legal `\` continuation does not fail a correct door. The risk in
        # that fix is the opposite error: folding everything into one blob until "the flag
        # appears somewhere in the fence" reads as "the command was passed the flag".
        SPLIT = ("# /d\n\n```bash\npython3 .agents/scripts/ship_preflight.py --repo \"$R\" \\\n"
                 "        --expect-key \"$EXPECTED_KEY\"\n```\n")
        c.check("CONTROL: a call split across a `\\` continuation still reads as ONE command",
                any("ship_preflight.py" in ln and "--expect-key" in ln
                    for ln in fold_continuations(code_lines(SPLIT))))
        NO_FLAG = ("# /d\n\n```bash\npython3 .agents/scripts/ship_preflight.py --repo \"$R\"\n"
                   "echo --expect-key is documented below\n```\n")
        c.check("CONTROL: the flag on a SEPARATE command is NOT credited to the preflight",
                not any("ship_preflight.py" in ln and "--expect-key" in ln
                        for ln in fold_continuations(code_lines(NO_FLAG))),
                "no trailing backslash, so these are two commands and must stay two")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
