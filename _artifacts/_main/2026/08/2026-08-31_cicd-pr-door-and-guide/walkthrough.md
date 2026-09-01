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
| `test_door_preflight_order.py` | 53/53 at the build sha → **57/57** after the review's coverage rows |
| `test_closeout_preflight.py` | 58/58 at the build sha → **69/69** after them |
| `test_command_surfaces.py` | 238/238 at the build sha → **246/246** after them |
| `test_check_links.py` | 50/50 — three rows added with the convention-6b carve-out |
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

- [x] The merge itself — lands via this branch's PR

Nothing else is owed before this can land. For context on what happens next:

- The PR for this lane is the ordinary Task road — `/smh-close-task-merge-tree --expect-key SCC-347`
  opens it and stops; riders SCC-356 and SCC-357 flip first, the parent SCC-347 closes last.
- **AVCH-111** and **AVCH-112** are minted and queued under AVCH-43. AVCH-111 ports the server-side
  `main-write-gate` + ruleset into AviationChat, which is what puts a required check on the PRs this
  lane's door now opens there; AVCH-112 writes AGY's first overview guide, after which its
  `overview` check stops warning and starts checking. Both run after this lands, in that order.
- Until AVCH-111 lands, an AGY epic PR is guarded by the local gate `/cicd-push-e2e` runs plus your
  reading of it — strictly more than the merge had before, when the GitHub-side road had nothing.

## Code Review (2026-08-31)

**Scope:** the full lane diff `origin/main...HEAD` — two commands rewritten (`cicd-push-e2e`,
`cicd-update-sprint-memory`), one rule (`git-policy`), two gate scripts (`closeout_preflight`,
`check_links`), five test files, a new template, the SOP family, and the generated mirrors.
**Method:** five adversarial lenses fanned out over the diff in isolated worktrees, then
verification, then triage. Every survivor was fixed **in this lane, RED first**, and each fix's
mutant re-run to prove the new assertion bites.

review-runtime:  fan-out
lens_isolation:  worktree
lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none
dispositions:    per-lens (acted-on/dismissed/relevance-killed): blind-hunter=5/0/0 · edge-case-hunter=9/0/0 · literal-correctness-hunter=10/0/0 · acceptance-auditor=7/0/0 · test-adequacy-auditor=8/0/0
drift:           none — Step 0.7 re-derived the blast radius against `origin/main` at `8a1b3cbf`; no sibling lane had landed since the plan was written, so the declared change set still described the live tree.

### Step 0.7 — re-derivation

1. `git fetch origin && git log --oneline origin/main -1` → `8a1b3cbf`, the same commit the plan
   was audited at. No lane landed underneath this one.
2. The declared change set was re-walked file by file against the tree; every path still existed
   at the path the plan named, and two files were added to it consequentially and disclosed below.
3. `check_maps --depth3-only --strict` exit 0 and `run_all.py` 66/66 at the review sha, so the
   diff the lenses read is the diff that lands.

### Findings — every one fixed in-lane, RED first

Two were structural and both were mine, in the same new function, and neither was reachable by my
own tests because my fixtures posed a world the doors forbid.

| # | Lens | Severity | Finding | Fix |
| --- | --- | --- | --- | --- |
| EC1 · LC1 | edge-case · literal | critical | `check_overview` diffed the guide against the **shared checkout's `HEAD`**, but `--project` IS the shared checkout and the lane lives in a separate worktree — `/cicd-prune-worktree` passes `--branch` and no worktree at all. Reproduced both directions: a lane that edited the guide is refused for not editing it, and another epic's edit left on the checkout satisfies this one | takes `args.branch`; OV10 poses the parked-checkout topology |
| EC2 · AA1 | edge-case · acceptance | critical | the cutoff read the **epic folder's** date. Measured on AviationChat: **0 of 70** story lanes carry a dated folder and 21 carry no dated review header — so the exemption fired for almost nothing and undatable lanes hit a hard error whose only remedy is re-running a save on finished work, the exact outcome the cutoff exists to prevent | prefer the walkthrough's `## Code Review (<date>)` header, fall back to the folder, **undatable → exempt**; OV9, OV11 |
| F2 | blind | important | the lane diff collapses to empty **once the branch lands**, and `/cicd-prune-worktree` re-runs this preflight after the landing | the accounting line accepts an `edited` state; OV7, OV8 |
| F1 · EC4 · LC3 | blind · edge-case · literal | important | the door's `BEHIND` currency guard was computed **before the only fetch**, so it was inert by construction — unfetched, `HEAD..origin/main` is empty for exactly the epic that just changed the file | fetch first, then measure |
| LC2 | literal | important | that same guard measured the **project** repo, and a thin project has no `.agents/commands/`, so its own printed remedy fails there with *path does not exist* | scoped to the LOBBY |
| EC3 · LC6 | edge-case · literal | important | **fenced-example bypass** (the SCC-154 class): the accounting line was read from raw text, so pasting Step 3.5's own fenced example satisfied the gate | `wf.strip_fenced`; OV12 |
| EC7 · LC5 · TA2 | edge-case · literal · test-adequacy | important | `absent` was **credited on a project that HAS a guide** — a lane saved before the first guide landed could ship afterwards without ever opening it | warns instead of crediting; OV13 |
| LC4 | literal | important | the cutoff read `hits[0]`, which is **glob order** — a two-folder story had its exemption decided nondeterministically | `max()` over dated hits |
| EC5 | edge-case | important | `--after-merge <KEY>` carries no slug, so a guessed branch name makes a real landing read as *NOT merged yet* | branch resolved from the bare key |
| EC8 | edge-case | important | the `--is-ancestor` proof **depends on squash and rebase being disabled**, and that was unverified on a repo measured as having no protection at all | `gh api` check at Step 4 + the SOP line |
| F3 | blind | suggestion | Step 5.5 recorded *"shipped as specified"* when the guide was merely **absent** — certifying a comparison that structurally could not happen | third outcome: `PRD: not reconciled` |
| F4 · LC11 | blind · literal | suggestion | Step 6's third git line was left unpinned while its two siblings got the `cd <abs> && git` pin | pinned; `test_stale_base_refs` key + control fixture updated |
| F6 | blind | suggestion | `git-policy.md`'s PR row dropped `--fill`, and a bare `gh pr create` cannot run headless | restored |
| EC6 | edge-case | suggestion | Step 1's chore-lane prose still named *"Step 4's merge message and mint `--branch`"* after the mint was deleted | rewritten |
| LC8 · EC9 · AA4 | literal · edge-case · acceptance | suggestion | the template said §5's row is written at `--after-merge`; Step 3.5 actually writes it, and a row first appearing at ship time was reconstructed from memory | attribution corrected; `Shipped` is the only column filled at `--after-merge` |
| AA9 | acceptance | suggestion | the template header's *"neither is an ERROR that blocks the close-out"* reads **inverted** — neither present IS the error | rewritten, and it now teaches all three states |
| AA2 | acceptance | suggestion | **five** SOP-family passages still drew the retired local-merge road; two were stale since SCC-183, before this lane existed | all five corrected |
| AA3 · AA5 · AA6 | acceptance | suggestion | acceptance row 6 forbade `[sop-ok]` absolutely (the lane used it twice, correctly, on artifacts-only and test-only commits the rule itself excludes); the amendment ledger claimed *"4 fences"* written from the plan's own prose rather than from the file (`grep -c` returns `1`); row 3 pinned an em dash the command does not emit | all three corrected in the plan, as corrections, not quietly met |

**The coverage half — four mutants that SURVIVED, each now dead.** The refusal halves were pinned
and the allow halves were not, so the guards certified an absence set while the thing the absences
exist to forbid could walk through the middle of it.

| # | Lens | Mutant that survived | Now |
| --- | --- | --- | --- |
| TA3 | test-adequacy | **N9** — a door that does `git checkout main && git merge --no-ff epic/…` before the tip push *and opens the PR anyway* tripped none of the four absence checks: it mints nothing, never writes `git push origin main`, publishes no gate ref. Survived at 53/53 | pinned on the merge SOURCE (`git merge epic/`), because Step 2's `git merge origin/main` absorb is required. **Dies** |
| TA10 | test-adequacy | **N10** — replacing `git push origin --delete epic/` with an echo. The resume half was asserted only by its ancestor check, so a door that proves the merge and then abandons the branch stayed green | prune presence pinned. **Dies** |
| TA4 · TA7 · TA9 | test-adequacy | **N1** (the silent no-walkthrough branch becomes an error), **N3** (the accounting line's decoration class leaves the regex), **N5** (the diff-failure warn goes silent) | OV15, OV14, OV16. All three **die** |
| LC10 | literal | P2's new tail (push the tip → open the PR) had no reordered fixture; it was carried by the head's control, which fires elsewhere in the sequence | `PR_FIRST` mutant + its presence control |
| TA1 · TA11 | test-adequacy | nothing proved Step 3.5 **exists**, nor that the story door stages the file Step 3.5 edits — delete Step 3.5 outright and every OV case stays green, because each poses its own walkthrough by hand | new block **CS-20**, allow-half, with both controls |
| TA5 · LC9 | test-adequacy · literal | CS-19 A and D read the **whole door**, so a door that only *mentions* the reconcile — in an aside, or a note explaining its removal — stayed green | scoped to the Step 5.5 section, with the `ELSEWHERE` control |

**One real red the new cases found, and it is why they were worth writing.** `check_overview`
WARNed on a failed diff and then **fell through to the ERROR anyway** — whose single named remedy
(*"write the accounting line, Step 3.5 never ran"*) is a guess when the comparison never ran at
all, and the lane may well have edited the guide. The warn is now terminal. Found by OV16, which
existed only because TA9 said the branch was unpinned.

**And its counterpart in the instructions.** Accepting an `edited` state was half the post-landing
fix; *instructing* it was the other half, and it was missing. Without it the story that did the
most work — the one that actually moved the guide — is the one the prune door refuses. Step 3.5
now teaches all three states and says why the `edited` line looks redundant and is not.

### Deviations from the approved plan, disclosed

- **`check_links.py` + `test_check_links.py` edited — not in the declared set.** The guide is a
  page a *project* copies; the lobby will never hold it, so every command, rule and standard that
  governs it produced a permanently-unresolvable claim — 12 of them, correct by construction. That
  is the thirty-false-hits failure (SCC-285) reintroduced on purpose. `check_links` already had a
  home for this (convention 6, *"a child-project path is not this repo's to resolve"*), but no
  prefix reaches a project page under a directory the **lobby also owns**. Added `PROJECT_FILES`,
  exact filenames only, with two controls pinning that it never becomes a prefix and never
  exempts a real lobby page. 21 unresolved → 6.
- **Four more SOP-family docs edited** beyond the two AA2 named — `jira_manual.md` (a table row and
  a flowchart), `jira_integration_guide.md` (two flowcharts). Same defect class, one line each,
  fixed in-lane rather than listed.

### Clean-Code Gate

`/smh-clean-code-audit` floor, run at this sha: `run_all.py` **66/66 files**, `workflow_lint
--toolkit-only` **0 errors / 0 warnings**, `check_maps --depth3-only --strict` **exit 0**,
`check_links --base origin/main` **6 unresolved** (5 pre-existing in `.agents/INDEX.md` and
`docs/workspace-standard.md`; 1 is this plan deliberately quoting a wrong path as an audit
finding), `sop_currency` green on every usage-surface commit. Judgment pass over the toolkit
conventions: mermaid `flowchart TD` only and no `sequenceDiagram` in any fence; every path handed
over is a clickable Markdown link; no `git add -A`; no secret, no invented citation.

**Gates at this sha:** suite 66/66 (receipt [gates/suite.json](gates/suite.json)) ·
`test_door_preflight_order` 57/57 · `test_closeout_preflight` 69/69 · `test_command_surfaces`
246/246 · `test_check_links` 50/50 · `test_stale_base_refs` 28/28 · three mutation sweeps 7/7,
5/5, 1/1 killed by declared case, plus six mutants re-run by hand in this review, all killed.

Verdict: PASS @ 9d23c6a5
