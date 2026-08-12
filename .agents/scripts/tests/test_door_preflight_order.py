"""test_door_preflight_order — the lobby's door to `main` must pre-flight, in the right ORDER.

Once a required status check guards `main`, a merge commit made on a machine cannot be pushed:
it has never been to GitHub, so it carries no check, and the ruleset refuses it. The door
therefore pushes that exact commit to a throwaway `gate/**` ref first, waits for the check, and
only then pushes `main` — checks attach to a COMMIT, so the green travels with it.

  ── THE ORDERING IS THE WHOLE TEST, AND IT IS NOT COSMETIC ─────────────────────────────────
The approval token has a 30-minute TTL (`pre-push-main-approval.sh`, `TTL_SECONDS=1800`). The
doors have always minted it immediately before the push, which was correct when nothing sat in
between. Insert a CI wait between mint and push and a slow run silently eats the token's life:
everything else passes, then the push dies on "stale token — it has been discarded", and the
operator is left re-running a close-out that already did all its work.

So the required order is:

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

REQUIRED_ORDER = (GATE_REF, CHECK_NAME, "mint-push-token.sh", "git push origin main")


def main() -> int:
    c = Cases("door pre-flight + ordering (SCC-118)")

    for label, path in DOORS.items():
        if not path.is_file():
            c.check(f"{label} · the door exists", False, str(path))
            continue
        lines = code_lines(path.read_text(encoding="utf-8"))

        c.check(f"{label} · pre-flights the merge to a gate/** ref",
                idx(lines, GATE_REF) >= 0,
                "a locally-made merge commit carries no check and the ruleset refuses it")
        c.check(f"{label} · waits on the check by name",
                idx(lines, CHECK_NAME) >= 0)
        c.check(f"{label} · still mints the token (local half unchanged)",
                idx(lines, "mint-push-token.sh") >= 0)
        c.check(f"{label} · still pushes main directly (local hook still fires)",
                idx(lines, "git push origin main") >= 0)

        ok, detail = order_ok(lines, *REQUIRED_ORDER)
        c.check(f"{label} · ORDER pre-flight → wait → mint → push", ok, detail)

        c.check(f"{label} · deletes the gate ref afterwards",
                idx(lines, "--delete gate/main-") >= 0,
                "an abandoned pre-flight ref per ship, otherwise")

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

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
