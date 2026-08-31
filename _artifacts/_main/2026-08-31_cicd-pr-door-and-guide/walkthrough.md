# Walkthrough — SCC-347 · the cicd flow gets a PR door and projects get an overview guide

review-runtime: fan-out

**Lane:** `chore/SCC-347-cicd-pr-door-and-guide` (CONSOLIDATED; riders SCC-356 Part A, SCC-357 Part B)
**Plan:** [implementation_plan.md](implementation_plan.md) · `Audit verdict: GO` · batch approval recorded at `acb02585`
**Tip gate:** `suite PASS exit=0 108.7s @ f5b3af72` — [gates/suite.json](gates/suite.json)

## What this changes, in one read

Two things the operator found on the smh (command-centre) side that the cicd (project) side lacked.

**The projects' `main` was the least guarded branch in the system, and nobody could see it.** The
lobby stopped merging locally back in SCC-183: its door opens a pull request, the operator clicks
*Merge pull request*, and a required `main-write-gate` check stands between the two. `/cicd-push-e2e`
— the command that ships **production** — still merged `--no-ff` on the machine, minted a single-use
token and pushed `main`. The reasoning that left it there was that a project publishes no check to
wait for, which is true and answers a different question. The token guards a push **from a machine
here**; it is structurally absent from a merge made on GitHub's servers, which is the road a web or
mobile session takes. Measured this session: `Projects/AGY_AVIATIONCHAT` `main` returned **404
*Branch not protected*** — no protection, no ruleset, nothing. The GitHub-side road into a live
product was guarded by *nothing at all*, while the local hook diligently guarded a push the operator
had stopped making. Part A gives that door the PR shape: gate locally, push the gated tip, open the
PR with the e2e numbers in the body, **stop**; `--after-merge <KEY>` proves the merge with
`git merge-base --is-ancestor`, watches the deploy, verifies live, prunes and moves the ticket.

**And projects had no page that says what was built.** AviationChat carries a repo map, a 19 KB
project-context, a 110 KB PRD and seven architecture files — zero diagrams, and none of them written
for a human trying to understand how a request flows. Part B adds `project_overview_guide.md` to
each project's `docs/` (skeleton at [`.agents/templates/project_overview_guide.md`](../../../.agents/templates/project_overview_guide.md),
flowcharts only), keeps it current **one story at a time** at `/cicd-update-sprint-memory` Step 3.5,
and then uses its per-epic delta as the **index into the PRD** at the ship. The PRD is
**reconciled, never rewritten** — it says what was *wanted*, the guide says what was *built*, and
regenerating one from the other would turn a requirements document into a second, more expensive
copy of the guide.

## Task Checklist

- [x] **A1** `cicd-push-e2e.md` Steps 4–6.5 rewritten to the PR road; Step 4.5 `--after-merge` added
- [x] **A2** `ship_preflight.py` docstring follows the road it describes
- [x] **A3** `test_door_preflight_order.py` standing guard flipped + docstring rationale rewritten
- [x] **A4** `git-policy.md` — the `main` row, the epic's one road, the write-gate scope
- [x] **A5** SOP §7 + landing table + hold paragraph + three atlas diagrams + `commands/INDEX.md` 56/58 + changelog
  - the two **smh** atlas diagrams were already stale (they drew *mint the token · push main* two weeks after SCC-183); fixed in the same pass, in lane
- [x] **A6** launchers regenerated (5 mirror surfaces, not 3); suite green
- [x] **B1** `.agents/templates/project_overview_guide.md` + `.agents/INDEX.md` `templates/` row (audit F2)
- [x] **B2** `workspace-standard.md` — supporting-files bullet, conversion-checklist row, comparison row
- [x] **B3** `cicd-update-sprint-memory.md` Step 3.5
- [x] **B4** `cicd-close-story-merge-tree.md` Step 2 explicit-path list
- [x] **B5** `closeout_preflight.py` `check_overview` + `story_walkthroughs` + block OV
- [x] **B6** `cicd-push-e2e.md` Step 5.5 (PRD reconcile) + block CS-19
- [x] **B7** SOP "three altitudes" subsection + changelog row

## Evidence

**HEAD at the gate: `f5b3af72`.** Every RED below was run before the edit it names.

### A — the door opens a PR (SCC-356)

RED, against the un-reshaped door:

```
-- 48/53 passed --
FAILED: /cicd-push-e2e · the road IS gh pr create, /cicd-push-e2e does NOT mint a token,
        /cicd-push-e2e does NOT push main directly,
        /cicd-push-e2e verifies the landed merge with plain git (--after-merge),
        P2 ORDER preflight -> absorb main -> push the epic tip -> open the PR
```

The `gate/**` row passed from the start — that door was never on the pre-flight-ref road — and the
CONTROL fixture passed throughout, which is what says the new P2 comparison bites on a correct door
rather than being broken.

GREEN, after the rewrite: `-- 53/53 passed --`.

⭐ **The run also exposed something the audit had only caught as a comment.** `P2 ORDER` is a *live*
ordering check on this door, not just the `REQUIRED_ORDER` fixture constant — so the audit's F6
("the comment at line 233 is stale") was understating it. The tail of that ordering claim was
repointed from `mint -> push main` to `push the epic tip -> open the PR`, and its reference fixture
with it. The head — preflight **before** the first write, the SCC-211 defect — is untouched.

### B — the guide, and the reconcile (SCC-357)

RED, block OV, before `check_overview` existed:

```
-- 19/25 passed --
FAILED: OV1 no guide in the project -> WARN, never an error, OV2 guide edited on the lane -> INFO,
        OV3 guide unchanged + the walkthrough says why -> INFO,
        OV4 guide unchanged and unaccounted for -> ERROR,
        OV5 a lane dated before the cutoff is EXEMPT, not blocked,
        OV6 CONTROL a line that claims neither `unchanged` nor `absent` does NOT satisfy
```

GREEN: `-- 6/6 passed --`, whole file `-- 58/58 passed --`.

RED, block CS-19, before Step 5.5 existed: `-- 3/7 passed --` (the four claims red, all three
ordering controls green). GREEN after: `-- 7/7 passed --`, whole file `-- 238/238 passed --`.

⛔ **The dated `OVERVIEW_CUTOFF` is the part that makes this safe to ship as an ERROR at all.**
`closeout_preflight.py` is also run by `/cicd-prune-worktree` and `/cicd-merge-epic-workingtrees`.
Without the cutoff, the day AviationChat gains a guide, every story saved before this law starts
failing here — and those stories are `Done`, their worktrees are exactly what the operator is trying
to prune, and the only remedy the error could name is re-running a save on closed work. A refusal
with no reachable fix is a gate that gets disarmed. It reuses `walkthrough_roster.lane_date` rather
than parsing a date twice.

### Suite Ledger

| Gate | Result |
| --- | --- |
| `run_all.py` through the receipt writer | **PASS** exit 0, 108.7s @ `f5b3af72`, 66/66 files |
| `test_door_preflight_order.py` | 53/53 |
| `test_closeout_preflight.py` | 58/58 |
| `test_command_surfaces.py` | 238/238 |
| `test_sops_prds_folder.py` | 61/61 |
| `test_stale_base_refs.py` | 28/28 — the `0 0` exemption still rules a live line |
| Mutation sweep [`sweep.json`](sweep.json) (Part A, door) | **7/7 killed** by declared case |
| Mutation sweep [`sweep-b.json`](sweep-b.json) (Part B, `check_overview`) | **5/5 killed** by declared case |
| Mutation sweep [`sweep-c.json`](sweep-c.json) (Part B, door order) | **1/1 killed** by declared case |

**Two reds the gates found that reading would not have:**

1. `check_maps` **F2** refused the first receipt run — the lane's own `_artifacts/_main/INDEX.md`
   row was missing. A real red, fixed, not waved through.
2. ⭐ **The mutation sweep's mandatory full unfiltered run caught a `NameError` I had shipped.**
   Factoring the walkthrough finder out of `check_artifacts` left its no-walkthrough error message
   referencing a `slug` that had moved. Every OV case supplies a walkthrough, so the scoped
   `--case` subset could never reach that line — this is precisely the `8681d83` class the full-run
   rule exists for, hit on its first use here.

**Three doc-gate refusals, each fixed rather than opted out of.** The commit-msg maps gate rejected
a new unresolvable reference twice (`_bmad-output/planning-artifacts/epics.md`, then the same path
under `PROJECT_ROOT/`), and `test_sops_prds_folder` T9 rejected `docs/project_overview_guide.md` in
the SOP — all three are **project** paths being resolved against the **lobby**, and no project has
an overview guide yet. Each was re-worded to name the location in prose and keep only paths that
exist in this repo. `[maps-ok]` was available and not used: the gate's own message says it is for a
scope change, not for waving a real broken link through.

## Your Actions

Nothing is owed before this can land. For context on what happens next:

- The PR for this lane is the ordinary Task road — `/smh-close-task-merge-tree --expect-key SCC-347`
  opens it and stops; riders SCC-356 and SCC-357 flip first, the parent SCC-347 closes last.
- **AVCH-111** and **AVCH-112** are minted and queued under AVCH-43. AVCH-111 ports the server-side
  `main-write-gate` + ruleset into AviationChat, which is what puts a required check on the PRs this
  lane's door now opens there; AVCH-112 writes AGY's first overview guide, after which its
  `overview` check stops warning and starts checking. Both run after this lands, in that order.
- Until AVCH-111 lands, an AGY epic PR is guarded by the local gate `/cicd-push-e2e` runs plus your
  reading of it — strictly more than the merge had before, when the GitHub-side road had nothing.
