# SCC-423 — trunk mode: a third epic mode, where stories land on `main` — walkthrough

**Ticket:** SCC-423 · **Lane:** `chore/SCC-423-trunk-mode` off `origin/main` · **Date:** 2026-09-06
**Plan:** [implementation_plan.md](implementation_plan.md) — approved by the operator this session.

## Why

Operator direction, 2026-09-06: ship Epic 24 phase 1 to `main` and *"develop the rest of this with
cicd from main, no more branch."* AviationChat is dropping its integration branch. The command
centre's law and doors described exactly two ways an epic can run, so without this lane every door
would keep sending AviationChat's stories to a branch that no longer exists.

## What trunk mode is, in one paragraph

`main` stays live production and the only long-lived branch — none of that moves. What changes is
that a story lane is cut from **`origin/main`** instead of an epic branch, and lands on **`main`**
through a **pull request the operator merges**, so **every merge is a deploy**. The ①②③ story
ceremony is untouched; only the base and the destination differ.

⭐ **The switch is a git query, never prose.** `git for-each-ref 'refs/remotes/origin/epic/*'`
returning nothing for a project IS trunk mode. That is deliberately the same shape as SCC-416's
`-quickdev` suffix — a fact about refs that no door can misread and no agent can talk itself past —
read one level up.

## Additive, never a rewrite

The two existing modes are still correct and still in use by every other project here. Rewriting the
branch model to "stories land on main" would have silently re-pointed AviationChat's siblings. So
`trunk` is a **third arm**: the doors grow one, the law grows one bullet, and the two older arms are
byte-untouched. Block D of the new test is the control that proves it.

## ⛔ The two things that deliberately did NOT change

Both were the tempting, wrong reading of "stories land on main now":

1. **`merge-target-guard.sh` still refuses `main:story`** — a `claude/*` lane merged onto `main`
   **locally**. Un-refusing it would delete the SCC-97 wrong-target protection on the one branch that
   is production. A trunk landing is a pull request, performed on GitHub's servers, where **no local
   hook runs at all** — the guard was never in its way. The pair it refuses is still an accident
   someone typed on this machine. `story:main` (absorbing `origin/main` into your lane) was already
   `allow` and is the everyday trunk move.
2. **The never-branch-a-story-worktree-from-`main` hard stop still binds** in every project that has
   a live epic. Trunk qualifies it in the same breath rather than deleting it.

## Assert-first — the check was RED before a single doc was touched

`.agents/scripts/tests/test_trunk_mode.py`, 22 cases in five blocks, discovered automatically by
`run_all.py` (so CI runs it on every PR into `main`).

| Run | Result |
|---|---|
| Before any doc edit | **12/22** — the ten doctrine gaps RED, all four controls already green |
| After the edits | **22/22** |

The controls being green *first* is the point: blocks D and E assert **absence of change** (the guard
still refuses, the hard stop still exists) plus three mutants proving the assertions bite — a policy
with every trunk line stripped fails the mode check, prose naming the landing outside a ``` fence is
not a step, and a guard with the refusal deleted fails the control.

Door checks read **only fenced code**, because these files discuss `gh pr create` and `main` in prose
at length and a document-wide substring search reports a step present when only a sentence about it
is. That is the inversion `test_door_preflight_order.py` records.

## What changed

| File | Change |
|---|---|
| `.agents/rules/git-policy.md` | § The epic's mode → three modes; the switch as a `for-each-ref` query; the trunk landing block under § The landing; the `main` row of the write-gate table; the two "did not change" notes above |
| `.agents/rules/worktree-per-story.md` | lane-table base column; the hard stop now names the trunk exception and how to resolve it mechanically |
| `.agents/rules/constitution.md` | floor anchor — the trunk base and landing |
| `AGENTS.md` | floor anchor ×2 — the worktree base, and `main`'s doors |
| `.agents/commands/cicd-close-story-merge-tree.md` | Step 3 → **three** arms, with the mode resolved by `for-each-ref` before an arm is picked; the trunk arm opens the PR into `main` and **STOPS** (never `gh pr merge`), and Step 4 waits for `--after-merge` |
| `.agents/commands/cicd-create-epic-sprint.md` | the kickoff question gains a third answer, which **cuts nothing** |
| `.agents/commands/cicd-dev-story-tests.md` | Step 0.6's epic-behind-main stop short-circuits in trunk; the lane absorbs `origin/main` |
| `.agents/commands/cicd-push-e2e.md` | Step 1's "None" branch says a trunk project has no epic to ship — the design, not a gap |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` + its changelog | §5 lane table, the kickoff paragraph, one changelog row |
| `.agents/scripts/tests/test_trunk_mode.py` | **new** — the 22 assertions above |
| `.opencode/`, `.roo/`, `.agents/.sync-manifest.json` | regenerated by `/smh-sync-agents` — masters changed, mirrors follow |

## Gates

| Gate | Result |
|---|---|
| `.agents/scripts/tests/run_all.py` | **81/81 files passed** |
| `test_trunk_mode.py` alone | 22/22 |
| `check_maps.py` | clean on the shared checkout; see the note below |

### Three suite failures on the first run, all mine, all fixed

`78/81` on the first pass. Two were mirror staleness — editing masters under `.agents/` leaves
`.opencode/` and `.roo/` behind — closed by `/smh-sync-agents`. ⓘ The sync also warns it could not
write `~/.codex/` (read-only under the sandbox); those are machine-local caches outside the repo and
no gate reads them.

**The third was a genuine doctrinal error the gate caught, and it is worth recording.** I had written
that *"the operator's click is the sign-off"*. House law is the opposite and for a reason: the
**decision** to proceed is the sign-off, and the click is only how that decision reaches GitHub —
never an errand handed back to him. `test_door_preflight_order.py` case S5 exists to catch exactly
that phrasing, and it did.

### The map lint, and why its two hits are not drift

`check_maps.py` in this worktree reports a dead path, `docs/migrations/auth_keys/_secrets/master.env`,
twice. **It is a worktree artifact, not drift**: that tree is gitignored and hand-carried, so it
exists in the main checkout and cannot exist in a fresh worktree. Verified by running the same lint on
the main checkout, where it does not appear. Nothing to fix.

That control run surfaced one real thing, and it was mine: this session's plan folder had been written
into the **shared checkout**, so the lobby ledger was missing its row and the tree was dirty on `main`.
Both are corrected here — the folder and the `active-context.md` hand-off now ride this lane, and the
shared checkout was restored with `git checkout origin/main -- …` (the safe form: a ref, never a sha).

## Your Actions

- [x] The merge itself — landed via this branch's PR (#186, `41fb27a1`).

ⓘ **The first version of this section asked the operator to "merge this lane's pull request", and
`jira_feed.py finish` refused the close-out over it (exit 2) — correctly.** The merge is the
ceremony's own step, not work owed to him: his **decision** to proceed is the sign-off, and the click
is only how that decision reaches GitHub. This section holds what only he *decides*. Recorded here
because the same lane wrote the doctrine into `git-policy` and then broke it in its own record two
files later, which is precisely the drift the gate exists to catch.
