---
IsArtifact: true
ArtifactMetadata:
  title: SCC-441 - two development toggles, built as one lane (Parts A-E)
  type: walkthrough
  date: 2026-09-10
---

review-runtime: fan-out

# SCC-441 — the quick lane and the epic mode, one lane, five parts

**Ticket:** SCC-441 (parent) with riders SCC-442, SCC-443, SCC-444, SCC-445, SCC-446 ·
**Branch:** `chore/SCC-441-dev-styles-quick-lane-light-epic` · **Plan:** [implementation_plan.md](implementation_plan.md) ·
**Parts:** [A](parts/SCC-442.md) · [B](parts/SCC-443.md) · [C](parts/SCC-444.md) · [D](parts/SCC-445.md) · [E](parts/SCC-446.md) ·
**Batch approval:** "Approved. Let’s start on the first task" — recorded at `9bb61f00`, stamped `e36ea365`, Step 1.5 check `APPROVAL-INTACT`.

**Bottom line.** All five parts are built, each RED then GREEN, each committed under its own key, all
pushed. The law names FULL / LIGHT / TRUNK and defines the quick lane once; the scope check exists as
a rule, a map and a script; `/cicd-quick-dev` and `/smh-quick-dev` are the same five-step quick lane
at both levels; the full Task lane is `/smh-dev-task-tests`; every branch-touching `cicd-*` door
prints the epic mode first and the close-out lands by pull request in every mode. Part F (the three
closing docs) waits for AVCH-152 in a closure lane, as the plan says.

## Task Checklist

- [x] **Part A · SCC-442** — the law: FULL / LIGHT / TRUNK, the quick lane defined once, the rails — `17546e8c`
- [x] **Part B · SCC-443** — `critical-surfaces.md`, the lobby's map, `scope_check.py`, `test_scope_check.py` — `2d57ba27`
- [x] **Part C · SCC-444** — `/cicd-quick-dev` rebuilt as the quick lane; the close-out preflight reads the quick-lane record line — `5aa18f0c`, `9fdfee3f`
- [x] **Part D · SCC-445** — `/smh-quick-dev` is the quick lane, `/smh-dev-task-tests` is the full lane, `/smh-quick-fix` retired, 74 references re-pointed by meaning — `49dc82ed`
- [x] **Part E · SCC-446** — `epic_mode.py`, the kickoff asks FULL/LIGHT/TRUNK, twelve doors print the mode, the close-out has two arms — `4d7b3a2e`
- [x] **Part F · SCC-441** — the closing docs (`tea_testing_guide.md` § 6.0, SOP § 6, one line in `smh-new-project.md`) — the closure lane after AVCH-152, as the plan said; see § Part F below

## Evidence

Every part was seen red before it was made green. The totals below are pasted from the runs; the
sha is the commit the run described.

| Part | RED (before) | GREEN (after) | Full suite at the part's tip |
|---|---|---|---|
| A | `test_trunk_mode.py` 24/30 — the six new block-A checks red against the old policy text | 30/30 | 84/84 files @ `17546e8c` |
| B | `test_scope_check.py` 5/54 with the script absent (the three `ERROR` rows were tightened to require the word on line 1 after they passed vacuously on a missing script) | 54/54 | 85/85 files @ `2d57ba27` |
| C | `test_closeout_preflight.py` 84/86 — QL1 and QL5 red before `_QUICK_LANE_RE` | 86/86 | 85/85 files @ `9fdfee3f` (the first full run caught the missing `--no-track`, fixed in the second commit) |
| D | the rename itself: the pinned tests would red on a missing `smh-quick-dev.md` body; **not run before the sweep** — the re-pointing was applied in the same pass, so Part D has no separate RED transcript | `test_command_surfaces` 343/343, `test_twin_parity` 68/68, `test_review_engine` 867/867, `test_lane_qualify` 46/46, `test_sops_prds_folder` 61/61 | 85/85 files @ `49dc82ed` |
| E | `test_epic_mode.py` 1/16 with the script absent; `test_trunk_mode.py` block B 29/30; `test_boot_epic_branch_read.py` 26/27 | 16/16 · 30/30 · 27/27 | see the receipt below (`gates/suite.json`) |

**Gates at the second-pass fix tip** (`14b59913`, 2026-09-11, after the re-review's thirty rows were applied — § Code
Review (2026-09-11, second pass) → Changes applied; the first pass's fix tip was `fb2639ac`): `run_all.py` **87/87 files**, exit 0, clean tree, receipt
`gates/suite.json` @ `14b59913` (84 → 87 across the lane: `test_scope_check.py`, `test_epic_mode.py`,
`test_approved_word_is_the_operators.py`) · `workflow_lint.py --toolkit-only` 0 errors, 0 warnings, 8
info · `check_maps.py --depth3-only --strict` clean · `check_links.py --base origin/main` clean ·
`test_command_surfaces.py` 343/343. The per-file closing runs: `test_scope_check` 141/141 ·
`test_epic_mode` 38/38 · `test_task_preflight` 139/139 · `test_closeout_preflight` 135/135 ·
`test_boot_epic_branch_read` 51/51 · `test_trunk_mode` 37/37 · `test_approved_word_is_the_operators`
130/130. (The earlier gate line at `85454a49` — 86/86, lint 0/0/8, maps and links clean — is
superseded by this one.)

⚠️ **Correcting this record — three claims above were written before they were true.** They are
left visible rather than quietly restated, because the review found them and that is what a record
is for.

| The claim as first written | What was actually true | Now |
|---|---|---|
| `check_links.py` … clean, at `4d7b3a2e` | **RED — 15 unresolved path claims.** The run behind the claim used `--paths` over the then-dirty files, not the lane diff, so it never looked at most of what the lane wrote. | all 15 fixed (five `../implementation_plan.md` relative links, five per-part walkthrough bullets re-pointed at this consolidated record, three illustrative tokens in the Part B plan, two forward-looking AviationChat paths); clean at `85454a49` against `origin/main` |
| 144 paths in the real diff | 145 | 145 at the shipping tip |
| 138 declared entries | 140 declared, and **two bullets the parser could not read at all** — the `docs/doc-graph.*` pair carried no `→ row`, so they counted as neither declared nor incomplete | 142 declared, 0 incomplete, in all six plan files |

**Acceptance, by the plan's rows.**

| Row | Statement | Evidence |
|---|---|---|
| A | Part A's six rows green | `test_trunk_mode.py` 30/30; `grep -rn quickdev .agents/rules AGENTS.md` empty; `.roo/rules/constitution.md` regenerated by the same transform `sync-agents.ps1` uses, verified byte-identical against its own previous output |
| B | Part B's six rows green | `test_scope_check.py` 54/54; `scope_check.py --repo <lobby> --paths .agents/hooks/shape-guard.py docs/x.md` → `OVERLAP` with the `ci` line, exit 3; `run_all` 84 → 85 |
| C | Part C's eight rows green | `grep -c code-review-engine cicd-quick-dev.md` = 0; `scope_check.py` called at Step 1 and Step 5; `light-epic` only in the Step 0 mode fence; `test_declared_change_set.py` S7 flipped (the door is an emitter); the Step 0.7 fence byte-identical to the twin (`test_twin_parity` 68/68); `first-pass gate` gone from the autopilot door; the guard toml's clause (a) retired |
| D | Part D's six rows green | the rename delta is 5 changed lines (`git diff HEAD:…/smh-quick-dev.md …/smh-dev-task-tests.md`); `smh-quick-fix.md` and its three launchers deleted; `smh-quick-fix` survives only in history rows and the three sentences that say it was retired (`DISCUSSED_AS_RETIRED` entry); doors regenerated on every platform, the manifest updated |
| E | Part E's seven rows green | `test_epic_mode.py` 16/16; `grep -rc quickdev .agents/commands` = 0; twelve doors call `epic_mode.py --repo`, none carries `for-each-ref … epic`; `test_trunk_mode.py` block B green with no `HEAD:epic/` fence in the close-out door; `LIGHT` named in `cicd-push-e2e.md` (4) and `cicd-e2e.md` (5); both hand-authored launchers current in both copies (`diff` empty); live: `epic_mode.py --repo Projects/AGY_AVIATIONCHAT` → `TRUNK` + the cost line |
| G | every commit leads with the key of the part it builds | `git log --format=%s origin/main..HEAD`: SCC-441 ×5 (plan + approval), SCC-442, SCC-443, SCC-444 ×2, SCC-445, SCC-446 |
| H | one gate at the tip, one review, the riders flip and the parent stays open | the receipt below; `task.yaml` carries `riders: [SCC-442..446]` and `landing_mode: partial`; the review section follows |
| F | the closure lane after AVCH-152 | not this landing (open box above) |

**Declared change set vs the real diff** at `85454a49` (`declared_change_set.py parse` → **142
entries, 0 incomplete**; `git diff --name-only --no-renames origin/main...HEAD` → **145 paths**;
reconciled → **undeclared 7 · unimplemented 2**). Undeclared, each with its disposition:

- `.agents/rules/reproduce-before-you-fix.md` — one phrase (`Step 3's review gate` → `Step 3's RED phase`) so the rule's pointer at the rebuilt door stays true; stays.
- `.agents/scripts/tests/test_sops_prds_folder.py` — `smh-quick-fix` added to `DISCUSSED_AS_RETIRED` with its reason, the shape that test asks for when a door is retired and the SOP names it once to say what replaced it; stays.
- `.agents/skills/cicd-e2e/SKILL.md`, `.claude/skills/cicd-e2e/SKILL.md`, `.agents/skills/smh-self-audit/SKILL.md`, `.claude/skills/smh-self-audit/SKILL.md` — GENERATED launchers whose `description:` moved with the command (sync regenerates them); stays.
- `.claude/rules/living-template-sync.md` — the path-scoped mirror of the edited master (`test_rule_frontmatter.py` requires the mirror); stays.
- `.agents/commands/smh-merge-multiple-workingtrees.md` line 255 (declared for the lane-name re-point) also had its SCC-127 artifact pointer fixed (`2026/08/` move) because `check_links.py` flagged it on the touched file; stays.

Declared and not touched — the two Part F bullets (`smh-new-project.md`, `tea_testing_guide.md`): the
plan lands them in the closure lane after AVCH-152; expected at this landing.

**One thing the lane found and did not widen into** (one line, with the remedy):

- The kickoff door pushes its own artifacts onto the epic branch it just cut (`cicd-create-epic-sprint.md` lines 189, 224, 258, `HEAD:epic/`). That is the epic's CREATION, not a story landing, so the PR arm does not apply — the remedy is for AVCH-152's ruleset to allow the epic's creator to push until the first story PR, or for the kickoff to open its own PR. Raised for AVCH-152's plan, which owns the ruleset.

> **The batch door's direct push is no longer on this list — it was FIXED, at review.** This record
> first deferred it as "not in SCC-446's scope"; the acceptance auditor rebutted that on the merits,
> and it was right: the lane retired the direct `HEAD:epic/` landing in the law and in the solo door,
> so leaving one door still teaching it is not deferral, it is a contradiction the lane created.
> `/cicd-merge-epic-workingtrees` Step 4 now lands each lane by its own PR into the epic.

**Three acceptance rows' literal checks diverge from what was built, and the spec is left as
approved.** The substance each row asserts is delivered; the literal count or letter written into
the approved plan is not what the finished door reports. Retro-fitting the spec to match the build
would destroy the only record of the gap, so the divergence is recorded here instead.

| Row | The plan's literal check | What it actually reports | Why |
|---|---|---|---|
| Part C, row C | `grep -c "scope_check.py" cicd-quick-dev.md` = 2 | **4** | the row was written for two call sites; the built door has one prose reference in its Step 0 rules block and **three** call lines — `--paths` at Step 1, and two `--diff` spellings at Step 5 (one for a story lane on a FULL or LIGHT epic, one for a chore lane or a TRUNK story lane). The two-arm tripwire did not exist when the row was drafted. |
| Part D, row B | `grep -c "scope_check.py" smh-quick-dev.md` = 2 | **3** | same shape, one arm fewer than Part C: the lobby has no epic ref to branch on, so one prose reference plus two calls. |
| Part D, row A | `git diff -M --stat …smh-dev-task-tests.md` shows **a rename** | git reports **`A`** (add) | git cannot pair them: the old `smh-quick-dev.md` content moved to the new name **while a different file took the old name**. With the source path still present there is no rename to detect, only an add plus an in-place rewrite. The row's intent — that the new file is the old body with only description, title and flow line changed — holds and was verified directly: `git diff HEAD:…/smh-quick-dev.md …/smh-dev-task-tests.md` is 5 changed lines. |

**Also written this lane:** the operator's verbatim batch approval into the plan and all five parts
(`9bb61f00`, stamped `e36ea365`); `_artifacts/_main/INDEX.md` row for the lane folder; the SOP
changelog rows SCC-442 → SCC-446 in the same commits as their parts; the sync manifest updated by hand
to what a sync run writes (`smh-quick-fix` out, `smh-dev-task-tests` in).

**Not run:** `pwsh .agents/scripts/sync-agents.ps1` — the generated doors were regenerated by a script
mirroring its three templates (skill launcher, zoo launcher, opencode mirror) and its floor-copy
transform, each verified byte-identical against the file the ps1 itself had written at `HEAD` before
regenerating; hand-authored skills were detected by the missing `GENERATED` marker and left alone.
The next `/smh-sync-agents` run on either machine should print nothing to change for these files.

## Your Actions

- [x] DECISION — lift the 2026-09-10 freeze on rules, gates and tests for this lane's fix batch (the 30 rows of § Code Review (2026-09-11)). Given 2026-09-11: *"approved to fix this"*, with the autopilot's lobby route explicitly deferred to another time. Applied at `fe5d7845` → `fb2639ac`; see § Changes applied.
- [ ] On the other machine, after pulling: run `/smh-sync-agents` once — its global caches still hold the old `smh-quick-dev` body and the retired `smh-quick-fix` door until then (Part D's audit, pre-mortem).
- AVCH-152 is next in the order (its plan carries its own `approved` stop and three ask-first stops on CI, rulesets and the skeleton); Part F's closure lane follows it.

## Code Review (2026-09-11)

Verdict: FAIL @ dd5a5c425ed521335588573dda98341b4f0af8c2
Suite evidence measured on dd5a5c425ed521335588573dda98341b4f0af8c2 — run_all.py 86/86 files (exit 0, clean tree, receipt `gates/suite.json`), workflow_lint --toolkit-only 0 errors 0 warnings 8 info, check_links --base origin/main clean, check_maps --depth3-only --strict clean, sop_currency clean, test_command_surfaces 343/343, py_compile green on all 3 changed .py files.

review-runtime: fan-out

lens_isolation:  worktree — every repo-reading lens got its own worktree copy of the repo under review, each verified from inside its own tree (`git rev-parse --show-toplevel` naming the lens copy, HEAD `dd5a5c42`). The Blind Hunter got no tree; its starvation is prompt-enforced, not sandbox-enforced, and that is stated rather than recorded as isolation.

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none

dispositions:    per-lens: blind-hunter=6/0/0 · edge-case-hunter=6/0/0 · literal-correctness-hunter=7/0/0 · acceptance-auditor=6/2/0 · test-adequacy-auditor=7/3/0 · clean-code-audit=3/0/0
drift:           undeclared=8 · unimplemented=2 · incomplete=0 — both sets are dispositioned under § Acceptance matrix, Declared-set reconciliation: the 8 stay with the reason named, the 2 are Part F's closure lane after AVCH-152, deferred and recorded

40 raw findings from five lenses plus the clean-code gate. 35 assessed real under `code-standards` §6.5, 5 dismissed. **At the time of this review none were fixed:** the fix batch was held at the operator's standing freeze on rules, gates and tests (2026-09-10: *"Do not touch the rules"*), which he had lifted for exactly two pinning tests and no further, so every real row was recorded `deferred — blocked by open decision` with the decision as a `## Your Actions` row. **He lifted the freeze for this lane on 2026-09-11** (*"approved to fix this"*), and the table below now carries where each row was applied — see § Changes applied for the batch and the evidence.

**Calibration — the one place the assessment disagreed with a lens's own label:** the clean-code gate proposed CONCERNS on the grounds that its two important findings are comment-contract violations, which §7 caps there. That is correct about its own half and does not bind the verdict: Step 1 and Step 3 supply two independent FAIL triggers this gate never looked at.

### Why FAIL, and not CONCERNS

Two of Step 4's FAIL triggers fired, both proved by execution rather than argued.

**A gate that cannot fail.** The quick lane's scope check is the whole substance of toggle 1, and in six of its invocations the variable holding the lobby path is never bound. A ```bash block is its own shell, `cd ""` exits 0 without moving, and the lobby-only script then resolves against a project that does not carry it. Three hunters found it independently and two reproduced the death. Separately, the test asserting that check has no bypass greps its own source for the word `override`, so a real `--force` flag added to the script leaves the suite 86/86 green.

**An acceptance item the diff does not deliver.** Part E row B is *"asks FULL / LIGHT / TRUNK, cuts the right name"*. The door cuts `epic/<KEY>-light-epic-<N>-<slug>` and then, eighteen lines later, tells the agent the echoed branch must read `epic/<KEY>-epic-<N>-<slug>` or STOP. Every LIGHT kickoff halts itself.

### Step 0.7 — re-derivation

- Nothing this diff references moved: `origin/main` is `cf1544f9`, the merge-base is the same commit, and 0 commits landed on the trunk while the lane was built. There was nothing to absorb and no absorb was faked.
- The true overlap is EMPTY — 0 of 148 files. `git merge-tree --write-tree --messages HEAD origin/main` wrote tree `301400f6` with no conflict messages.
- No sibling lanes are live: `git worktree list` shows only the shared checkout on `main` and this lane, so there is no landing-order dependency. `risk_seam.py classify` returns `unclassified` with the lane's own root echoed — the permanent, correct answer for a markdown repo with no code graph (SCC-289), so every judgement below comes from reading the diff.

`review_level: standard`, derived from that radius and not chosen: the radius holds gate scripts, rules and hooks, and the re-taken diff is 148 files, so two of the three `quick` conditions fail.

### Scope and method

**Scope:** `origin/main...HEAD`, 148 committed files, 13,998 diff lines. The six `?? .claude/*` rows are sandbox bind mounts, not files, and were not reviewed.

**Method:** `/smh-code-review` Steps 0 through 3.5, invoking the `code-review-engine` skill at Step 1 as a five-lens fan-out. Four repo-reading lenses each ran in their own isolated worktree copy; the Blind Hunter ran on the diff text alone with no repo. `lens_budget: standard`; the literal-correctness lens received the mandated 20-file cap in diff order with all 128 withheld paths named to it, took no top-up, and declared the truncation as its first line. Six findings were proved by mutations that survived the suite, every mutant restored and verified byte-identical.

### Findings

| # | file:line | Sev | Lens | Failure scenario | Disposition |
|---|---|---|---|---|---|
| 1 | `cicd-quick-dev.md:237,401,402` · `smh-quick-dev.md:117,158,315` (+6 mirrors) | critical | blind · edge · literal | `$L` used in six blocks that never bind it. The block is its own shell, `cd ""` exits 0 without moving, and the lobby-only `scope_check.py` resolves against the project: `No such file or directory`, exit 2. The quick lane's only line over auth, billing and CI never runs, at Step 1 or at the Step 5 tripwire. `smh-quick-dev.md:117` is worse — `link-worktree-assets.py` DOES exist in a lobby worktree, so it runs from the wrong cwd with a path resolving nowhere and the lane's assets are silently never linked. Reproduced; the lane's own `unbound_L()` finds all 12 rows. | applied @ 2cee8c5f |
| 2 | `test_boot_epic_branch_read.py:A6` | important | blind · edge | The fence-scoped checker added at `dd5a5c42` says in its own comment "every fence, not just Step 2b's" and is wired to one file. That is why row 1 shipped green. | applied @ fe5d7845 |
| 3 | `scope_check.py:188` | important | edge | An absolute path defeats a mapped repo's check. `--paths .agents/scripts/main_write_gate.py` → `OVERLAP` exit 3; the same file as an absolute path → `CLEAR` exit 0. `--repo` is documented as absolute, so one command line silently requires the others to be relative. Fails open only where a map exists, i.e. where the map is the authority. Reproduced. | applied @ fb2639ac |
| 4 | `test_scope_check.py` ("no override flag") | important | test-adequacy | The no-bypass assertion is a source grep for `override`. Mutants adding `--force` and an `SCOPE_CHECK_SKIP` env check both printed `CLEAR` and both SURVIVED, 80/80 and 86/86. A gate that cannot fail, guarding the critical-surfaces line. | applied @ 5f574b25 |
| 5 | `scope_check.py:180` (`diff_paths`) | important | test-adequacy | Mutating the merge-base to a two-dot diff SURVIVED 80/80 and 86/86 — the one thing the docstring says must never happen. Reproduced behaviour difference: with `main` advanced after the fork, HEAD says `CLEAR`, the mutant ejects on a `.github/` file the lane never touched. Block E never moves `main`, so the two spellings are identical there. | applied @ 5f574b25 |
| 6 | `scope_check.py:102` (`load_map`) | important | test-adequacy | A bare-word path in a repo's own map is a silently dead pattern: with `fragments=False` it falls to `path == pattern`, so `"paths": ["auth"]` answers `CLEAR` for `backend/auth/token.py`. This is the likeliest authoring mistake, because the rule publishes `auth`/`session`/`billing` as the generic fragment list one page above the map format — and it is the exact failure the `null`-entry guard was added to prevent. Reproduced. | applied @ fb2639ac |
| 7 | `.agents/critical-surfaces.json` | important | edge | The `ci` surface omits `workflow_lint.py`, `check_links.py`, `check_maps.py`, `mutation_sweep.py` and `epic_mode.py`. All five answer `CLEAR`. The changelog claims the surface "grew from four gate scripts to the whole gate family plus its tests, so the quick lane cannot quietly rewrite what green means" — it did not, and a quick lane can edit the linter and then report its green. Reproduced. | applied @ fb2639ac |
| 8 | `cicd-autopilot-claude.md:168` | important | literal | An added line grants the lead both quick-lane `approved` stops. The lane then writes `Review: none - quick lane; walkthrough approved by the operator @ <sha>`, which `closeout_preflight._QUICK_LANE_RE` reads as evidence. An agent can supply the operator's approval and file a record naming him. `constitution` §Hard Stops and `000-PLAN-FIRST-GATE` both reserve that word to Mr. Hatter. | applied @ 2cee8c5f |
| 9 | `cicd-create-epic-sprint.md:146` | important | acceptance | The post-cut assertion admits only `epic/<KEY>-epic-<N>-<slug>`; the LIGHT fence 18 lines above cuts `epic/<KEY>-light-epic-<N>-<slug>`. Every LIGHT kickoff STOPs on the branch it was just told to cut. The line predates the lane and was correct until LIGHT existed, so this lane broke it. | applied @ 2cee8c5f |
| 10 | `cicd-quick-dev.md:330` | important | literal | Names `story_status.py` inside a `§BIND`-scoped project command. The script exists only in the lobby (`find Projects -name story_status.py` → nothing). The same file three sections earlier forbids exactly this: *"naming it here would cite a file that is not on the target (SCC-285)"*. | applied @ 2cee8c5f |
| 11 | `cicd-close-story-merge-tree.md:408-411` | important | literal | The merge sha is read with `git rev-parse origin/epic/<KEY>-<slug>`, unconditionally. TRUNK is defined as no `origin/epic/*` at all, and Arm B reaches Step 4 via `--after-merge`, so the read is `fatal: ambiguous argument`, exit 128. AviationChat runs TRUNK today. | applied @ 2cee8c5f |
| 12 | `cicd-close-story-merge-tree.md:278-287` | important | blind | Step 3 requires the walkthrough to carry the PR URL AND to be committed before the PR opens. The URL first exists at `gh pr create`, strictly after the required commit, so the instruction is unsatisfiable. Both ways out are bad: omit the URL from the record close-out reads, or commit after creation and re-trigger the epic's checks mid-`--watch`. | applied @ 2cee8c5f |
| 13 | `closeout_preflight.py` ↔ `task_preflight.py` | important | edge · acceptance | The project quick lane's approval sha is dereferenced (`_stale_against_sha(..., "approved")`); the lobby's is not. `task_preflight.check_gate` reads only `VERDICT_RE`, finds no `Verdict:`, and returns benign. So the operator approves the lobby walkthrough at sha X, the agent commits three more files, the full gate runs green and he merges work he never saw. The `@ <sha>` on `smh-quick-dev.md:282` is decorative. | applied @ fb2639ac |
| 14 | quick-lane record line: 10 writer files ↔ `closeout_preflight.py:289` | important | test-adequacy | Writer and reader are never checked against each other. Changing the verb in all ten writers left the suite 86/86. The consequence is proved by the reader's own QL16 control: a lane that did exactly what the door said gets "the review step has not run", and the agent's natural repair is a `Verdict:` stamp for lenses that never launched — the SCC-173 trap. | applied @ 5f574b25 |
| 15 | `epic_mode.py:65-68` (`uncommented`) | important | edge · clean-code | The docstring I added at `dd5a5c42` claims an escaped quote "can only make the scan strip MORE… fails toward the loud answer". False, by two different inputs. An unmatched apostrophe (`echo it's fine   # … -light-epic-`) leaves the comment unstripped; so does `echo "a \" b" # -light-epic-`, where the early close lets the next quote swallow the `#`. Both over-report ARMED, the direction the same file calls "hides a live E2E". | applied @ fb2639ac |
| 16 | `epic_mode.py:24-25` | important | clean-code | The module docstring says `pr-check.yml` "reads with `contains()`" in the present tense; `light_armed` 60 lines below says no repo does. History shows why: `4d7b3a2e` wrote the docstring with no probe, `85454a49` added the probe and left the paragraph. A reader starts at line 1 and forms the exact belief the probe exists to break. | applied @ fb2639ac |
| 17 | `epic_mode.py:76` (`uncommented`) | suggestion | test-adequacy | Deleting the quote tracking entirely SURVIVED 30/30 and 86/86 — block E3's comment case has the `#` after the token, so a naive first-`#` cut still passes. Reproduced: `run: echo "build #4 targets -light-epic-"` flips a genuinely armed repo to NOT ARMED under the mutant. | applied @ 5f574b25 |
| 18 | `scope_check.py:130` (`pattern_hit`) | suggestion | test-adequacy | Dropping the `fragments and` guard SURVIVED 80/80. The "a declared path is never widened into a substring search" contract has no case, because block B's map paths all contain `/` or `.` and never reach the branch. Pairs with row 6. | applied @ 5f574b25 |
| 19 | `closeout_preflight.py:300-335` | suggestion | test-adequacy | Two load-bearing decisions unexecuted: the warn/err asymmetry the comment calls "the whole point" (mutating `say` to always `err` SURVIVED 115/115), and the `":(exclude)_bmad-output/"` half of the fallback pathspec (removing it SURVIVED). | applied @ 5f574b25 |
| 20 | `scope_check.py:180-186` | suggestion | blind · edge | `--diff` with zero changed files prints `CLEAR`, exit 0 — the `--paths` arm's empty guard sits inside the `else:` branch and is skipped. The same script makes empty `--paths` a hard ERROR on the reasoning "silence is UNKNOWN scope, never clear", and both doors quote *"an empty diff is a STOP, not a pass"* two steps earlier. Reachable with uncommitted-only work, or `--repo` pointed at a checkout on `main`. | applied @ fb2639ac |
| 21 | `scope_check.py` `GENERIC` | suggestion | blind | The fallback set does not protect `.agents/critical-surfaces.json`, `scope_check.py` or the rule itself, so in an unmapped repo — which today is every project — a quick lane can write the line's own map without ever tripping the line. The rule states the invariant ("a line that can widen itself is not a line") and enforces it with a map row, which by definition cannot exist where there is no map. | applied @ fb2639ac |
| 22 | `cicd-push-e2e.md:59` vs `:74` | suggestion | blind · literal | Both lines are added by this lane and they give different answers for `AMBIGUOUS`: Step 0 says STOP "before anything else runs", Step 1 says show each and decide together. Taken literally Step 1's arm is unreachable. | applied @ 2cee8c5f |
| 23 | `cicd-prune-worktree.md:346` | suggestion | literal | The Step 5 case analysis rests on "Only `/cicd-park` sets an upstream (`push -u`)". Line 226 of the same file runs `git push -u origin claude/<KEY>-<slug>` on the preserve-uncommitted-work path, and the close-out door names that behaviour explicitly. The conclusion still holds; the reasoning a reader is meant to follow does not. | applied @ 2cee8c5f |
| 24 | `cicd-close-story-merge-tree.md:308-311` | suggestion | acceptance | *"on LIGHT the two E2E checks show as skipped — that is the design, not a red"*, stated unconditionally at the landing moment. In an unarmed repo — today, all of them — that is false, and `light_armed`'s NOT-ARMED caveat is 250 lines away at Step 0 with no pointer forward. | applied @ 2cee8c5f |
| 25 | `cicd-create-epic-sprint.md:135` | suggestion | literal | Asserts the mode token "sits between the key and the sprint number". `classify()` is an unanchored substring test, so `epic/SCC-441-epic-24-light-epic-rollout` reads LIGHT. Reproduced. Same class as the "third token" claim already corrected in four sites; this site was missed. | applied @ 2cee8c5f |
| 26 | `cicd-create-epic-sprint.md:114` | suggestion | acceptance | The banner instruction lives only inside the TRUNK bullet; its aside "the FULL and LIGHT answers record theirs the same way" points at an instruction with no FULL/LIGHT home, and Step 3's board write never mentions the mode word. | applied @ 2cee8c5f |
| 27 | `smh-quick-dev.md:2449-2450` (Step 1 prose) | suggestion | blind | The lobby surface list reads ".github/, the hooks, the preflights, the permission fence" and omits `.agents/scripts/tests/`, which the map declares. Step 3 then mandates a test in that directory for any script work, so every script-shaped quick lane OVERLAPs at Step 1 or ejects at Step 5 after the work is done. The map is intentional; the door does not warn. | applied @ 2cee8c5f |
| 28 | `_artifacts/_main/INDEX.md:7` | nitpick | acceptance | Says "144 files"; the diff at HEAD is 148 paths. | applied — the records commit after fb2639ac (the INDEX row now carries the real count) |
| 29 | `scope_check.py:188` | nitpick | clean-code | `(args.paths or [])` is a dead branch — the mutually-exclusive group plus `nargs="*"` guarantees a list, never `None`. Reads as though `--paths` can be absent, a state the parser refuses. | applied @ fb2639ac |
| 30 | `preflight-receipt.json` | important | acceptance | Carries `verdict_sha: 46bc4267`, pointing at the `Verdict: PASS` stamp retracted by `fcaccebf`. The record now references a verdict that no longer exists. Re-running `task_preflight.py` at the shipping tip clears it. | deferred — in this lane: the receipt is rewritten by task_preflight at the shipping tip, after the re-review stamps its verdict |

**Dismissed under `code-standards` §6.5 (5 findings), one line as the rule requires:** the unpinned `break` in `overlaps` and the `PRODUCT_DIRS`-widening mutant guard behaviour that is already correct and whose failure changes output shape, not a verdict; the `.yaml` extension and whitespace-`--repo` micro-branches both fail toward the loud answer; 11 doors naming `AMBIGUOUS` but not `ERROR` as a stop is a loud failure carrying its own reason line; the missing `bmad-quick-dev` door-scan guards a premise verified true today that nothing in this diff threatens; and the walkthrough's 7-vs-8 undeclared count was resolved by the retraction at `fcaccebf` before triage. The absence of judge-style behavioural tests anywhere in this repo was raised once by the test-adequacy lens as house architecture and is out of this lane's scope under question 3.

### Gates

| Gate | Result |
|---|---|
| Enforcement suite | `run_all.py` **86/86 files passed**, exit 0, 30.5s, clean tree — receipt `gates/suite.json` stamped @ `dd5a5c42` by `gate_receipt.py`, which executes the gate and has no `--result` flag |
| Toolkit lint | `workflow_lint.py --toolkit-only` — **0 errors, 0 warnings, 8 info** (UTF-8 BOM notices on vendor `testarch-*` files) |
| Assertion evidence | the lane's own RED assertions, re-run green: `test_boot_epic_branch_read.py` **37/37** (35/37 before the fix), `test_epic_mode.py` **30/30** (28/30 before) |
| SOP currency | `sop_currency.py --paths <148 changed> --message "<subject>"` — clean, no output |
| Link + anchor | `check_links.py --base origin/main` — **clean** |
| Door parity | `test_command_surfaces.py` — **343/343 passed** |

⛔ **Every gate above is green, and the verdict is still FAIL.** That is the point of rows 1, 4, 5 and 14: a green suite proves the code runs, never that the checks would have caught it breaking. Four of this lane's own new gates were mutated and survived.

### Acceptance matrix

The Acceptance Auditor walked all 37 rows of the plan and its five parts against the diff in an isolated tree, running rather than reading wherever a check was runnable, and its per-row evidence is imported here rather than re-derived (Step 2, no double audit). **31 rows satisfied with a named proving assertion.** The exceptions:

| Row | State | Proving assertion |
|---|---|---|
| **E·B** "cuts the right name" | **NOT satisfied** | the cut fence and the post-cut assertion disagree — finding 9 |
| B·D "run_all 85/85" | satisfied, count moved | 86/86 at HEAD; 85 was Part B's own tip, Part E added `test_epic_mode.py` |
| C·C "Step 1 + Step 5 call scope_check" | satisfied, literal count diverges | 4 hits not 2 (prose plus 3 calls); the divergence is recorded |
| D·A "≤6 changed lines" | satisfied, git reports `A` | git cannot pair the rename; body verified as the full lane |
| P·H "one gate at the tip green" | **satisfied only as of this review** | evidence was 4 commits stale at `46bc4267`; re-stamped at `dd5a5c42` above — finding 30 |
| P·F the closure lane | **deferred and recorded** | `declared_change_set.py diff` returns exactly the two Part F bullets as `unimplemented`; `tickets/AVCH-152.md` carries the plan |

The LIGHT toggle's server side is deferred and properly recorded, not missing: it is Part E's "Not in this lane", it is AVCH-152's plan rows 1-2, and `light_armed()` prints a loud NOT-ARMED caveat derived from the repo so the gap cannot go quiet. Findings 15, 16 and 17 are about that caveat's correctness, not its absence.

**Declared-set reconciliation.** Block present, 0 rejected bullets, 8 undeclared, 2 unimplemented. The 8 stay, and the reason is named: each is a consequence of declared work rather than scope creep — a rule sentence naming quick-dev's retired review gate, the `norm_path` hoist into `wf_common`, the template-sync rule's new pull-request-gate row, and four generated launcher descriptions following their commands' frontmatter. The 2 are plan overreach, not dropped scope: both files were grepped for every name this lane renamed or retired and for its other surfaces, and neither mentions any of them.

### Clean-Code Gate

Run nested per Step 3.5, importing Step 3's receipts and pasted runs rather than re-running them, and importing Step 1's drift findings rather than re-sweeping §2B. Its findings are rows 15, 16 and 29 above.

⛔ **The four machine-floor commands of `code-standards` §6 — `ruff check`, `pyrefly check`, `npm run lint`, `npx tsc --noEmit` — do not exist in this repo.** There is no venv, no `backend/`, no `frontend/`, no `package.json` and no linter or type checker installed. This is not a skipped check: the enforcement suite plus `workflow_lint --toolkit-only` and `py_compile` ARE the objective floor here, and they are green.

Zero findings, stated rather than padded: no AIDEV anchor was added, removed or invalidated across all 148 files; no commented-out code; no unowned TODO (the only ones are fixture data and prose about a TODO); no comment merely restating its code. The §2C convention table came back entirely clean on added lines — no line over 120 chars, full annotations on every added `def`, no placeholder-less f-string, `Path(__file__).resolve().parent` throughout, no bare `python`, no `C:/` path, no `;` separator, no leftover debug print, no bare `except`. Both new scripts refuse unknown input loudly rather than passing quietly.

The gate also verified several of the lane's strong factual claims as TRUE, which is the §2A check cutting the other way: "twelve doors now call this" is exactly 12 and is itself pinned by a test; the `lane_qualify.py:24-27` citation lands on the block it names; `task_preflight.py` is import-safe by AST; `DEPLOY_DIRS = PRODUCT_DIRS + (CI_DIR,)` as its comment claims.

### Changes applied

**All 29 rows with a code or text remedy, on 2026-09-11, after the operator lifted the freeze for this lane; row 30 is done at the tip.** Four commits, in the reproduce-before-you-fix shape — the pins committed RED first, the fixes second, each fix proved by putting the old text back (pin red) and restoring it byte-identical (pin green):

| Commit | What | Seen red on its tree |
|---|---|---|
| `fe5d7845` | the door pins: `unbound_L()` reads every door; `test_trunk_mode` block B asks the kickoff door for both branch shapes, containment wording and the banner mode word, and the close-out door for a TRUNK merge-sha read and the NOT-ARMED caveat; new `test_approved_word_is_the_operators.py` | test_boot 49/51 · test_trunk_mode 32/37 · test_approved 120/122 |
| `2cee8c5f` | rows 1, 8, 9, 10, 11, 12, 22, 23, 24, 25, 26, 27 — six fences bind `$L`, the LIGHT shape passes the kickoff's post-cut STOP, Step 3 records the mode word, the close-out reads the merge sha off `origin/main` on TRUNK and keeps the PR URL out of the walkthrough, the skipped-E2E sentence carries the NOT-ARMED caveat, the AMBIGUOUS arms agree, both upstream setters are named, the lobby surface list names the tests dir, and neither the autopilot door nor its SOP hands `approved` to the lead. Mirrors byte-copied. | green: 51/51 · 37/37 · 122/122; revert proofs 50/51, 34/37, 35/37, 121/122 (×2), each restored byte-identical |
| `5f574b25` | the script pins: 35 checks across `test_scope_check`, `test_epic_mode`, `test_task_preflight`, `test_closeout_preflight` (rows 3, 4, 5, 6, 7, 13, 14, 15, 17, 18, 19, 20, 21 and the two §5 nitpicks) | each block red by behaviour before its fix; the six surviving mutants of the review (rows 4, 5, 14, 17, 18, 19) re-applied by hand and now KILLED |
| `fb2639ac` | rows 3, 6, 7, 13, 15, 16, 20, 21, 29 — absolute paths rebased (outside the repo is ERROR), a bare-word map entry must name a root file, the lobby `ci` surface gains the five Step 3 floor scripts, `task_preflight.check_gate` dereferences the quick lane's approval sha with the one helper (moved from `closeout_preflight`, which imports it back), `uncommented()` handles the escape and the apostrophe and its docstring claims only what is pinned, a zero-file `--diff` is ERROR, GENERIC protects the line itself, the dead branch is gone | test_scope_check 106/106 · test_epic_mode 34/34 · test_task_preflight 124/124 · test_closeout_preflight 126/126; every fix hunk reverted by hand → red → restored byte-identical |

Prose-only rows that can carry no test, said as the rule asks: 10, 12, 16, 22, 23, 27. Row 28 is corrected in the records commit that carries this section. Row 30 waits for the re-review's stamp: `task_preflight.py` rewrites the receipt at the tip.

**The pattern under the thirty, in one line each, for the next lane:** a `$L` pinned once at Step 0 and used in a later fence (the mechanism behind row 1, reachable in any door that binds a variable in one fence and reads it in another); a test that greps its own source for a word instead of running the behaviour (rows 4, 14); a fixture that never exercises the branch the code was written for (rows 5, 17, 18, 19); and prose written beside a fix that no test held (rows 15, 16, 25).

Whole suite at the fix tip: `run_all.py` **87/87 files** @ `fb2639ac`, clean tree, receipt `gates/suite.json` — 87 because `test_approved_word_is_the_operators.py` joined. `workflow_lint.py --toolkit-only` 0 errors 0 warnings 8 info · `check_maps.py --depth3-only --strict` clean · `check_links.py --base origin/main` clean (three fixture paths in `review-lenses.md` marked `<fixture>/`) · `test_command_surfaces.py` 343/343.

## Code Review (2026-09-11, second pass — after the thirty-row fix batch)

Verdict: CONCERNS @ 14b59913
Suite evidence measured on 14b59913 — run_all.py 87/87 files (exit 0, clean tree, receipt `gates/suite.json`), workflow_lint --toolkit-only 0 errors 0 warnings 8 info, check_links --base origin/main clean, check_maps --depth3-only --strict clean, sop_currency clean, test_command_surfaces 343/343, py_compile green on every changed .py file.

review-runtime: fan-out

lens_isolation:  worktree — every repo-reading lens ran in its own worktree copy of this repo, each verified from inside its copy (`git rev-parse --show-toplevel` naming the copy, HEAD `ffca21c7`): edge-case-hunter `agent-aff4d76ed7e987b69`, literal-correctness-hunter `agent-a62ee26c2c510809b`, acceptance-auditor `agent-a266bab402b1eb5e7`, test-adequacy-auditor `agent-a070c52f4e3277d56`. The Blind Hunter got no tree: prompt-enforced starvation, stated rather than recorded as isolation.

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none

findings:        0 decision · 30 patch · 0 defer   (0 noise-dismissed · 8 relevance kills)
dispositions:    per-lens: blind-hunter=8/0/1 · edge-case-hunter=9/0/0 · literal-correctness-hunter=1/0/1 · acceptance-auditor=6/0/1 · test-adequacy-auditor=6/0/4 · compound=5/0/1
drift:           undeclared=12 · unimplemented=2 · incomplete=0 — the 12 are consequences of declared work (the review-1 pins and fixes, the norm_path hoist, four generated launchers, the path-scoped rule mirror, the retirement entry, and `cicd-label-tasks.md` with its mirror from this pass's row 24), each named under § Acceptance matrix; the 2 are Part F's closure lane after AVCH-152, deferred by design

37 raw findings from five lenses, verified one by one (Evidence Verifier: all 37 `verified: true`, severities re-graded from evidence), plus 6 compound findings (Compound Synthesis, each with named parents). Same-claim groups {1, 6, 19} · {7, 15} · {5, 21} · {13, 29} were verified once and expanded, so the unique claims are 32 + 6 compound. **30 assessed real and fixed in this lane; 8 dismissed at the relevance gate, one line each below.** Nothing was deferred.

**Calibration — where the assessment disagreed with a lens's label:** the unset-upstream fatal (three lenses, self-rated important / suggestion / nitpick) is a suggestion on its own and important in company — the Compound role showed it trains a reader to ignore the one `fatal` that matters, a failed fetch before the mode query — so both were fixed together. The staleness check's blindness to `.github/` in a repo with product dirs (blind, important) is real and dismissed: the Step 5 tripwire overlaps `.github/` first, and the residual needs a commit after the tripwire the door forbids.

### Why CONCERNS, and not PASS

The engine's floor binds the verdict and it is CONCERNS: seven findings graded **important** by the Verifier survived triage into the patch bucket — every one applied and pinned in this lane before this stamp, none open. No FAIL trigger fired: no acceptance item undelivered (33 of 37 rows satisfied by a named assertion, 6 divergences recorded below, 2 deferred by design), every gate green at the tip, no gate left that cannot fail. A fresh review at the fixed tip is what turns this record into a PASS; the fixes are unreviewed edits until then, which is the reason the floor does not move with them.

### Step 0.7 — re-derivation

- Nothing this diff references moved: `origin/main` is `cf1544f9`, the merge-base is the same commit, 0 commits landed on the trunk while the lane was built; nothing to absorb and no absorb was faked.
- The true overlap is EMPTY — 0 of 152 files; `git merge-tree --write-tree --messages HEAD origin/main` wrote tree `952acb16` with no conflict messages.
- No sibling lanes are live: `git worktree list` shows the shared checkout on `main` and this lane only, so there is no landing-order dependency. `risk_seam.py classify --repo <this tree>` returns `unclassified` with this tree's root echoed — the permanent answer for a markdown repo with no code graph (SCC-289).

`review_level: standard`, derived: the radius holds gate scripts, rules and hooks, and the re-taken diff is 152 files.

### Scope and method

**Scope:** `origin/main...HEAD` at `ffca21c7`, 152 committed files, 15,576 diff lines, frozen to a patch file the lenses read. **Method:** `/smh-code-review` Steps 0 through 3.5, invoking the `code-review-engine` skill at Step 1 as a five-lens fan-out (`lens_budget: standard`; the literal-correctness lens received the 20-file cap in diff order with all 132 withheld paths named to it, took its one top-up on `closeout_preflight.py` and declared the truncation as its first line), then the engine's Step 2 verification wave — an Evidence Verifier over all 37 findings and a Compound Synthesis role, both on a dossier built by `evidence_extract.py` (37 packages) — then Step 3 triage by the assessor under `code-standards` §6.5 and the relevance gate. The raw lens reports, the verifier's table and the compound findings are in [review-lenses.md](review-lenses.md) § Second pass.

### Findings

| # | file:line | Sev | Lens | Failure scenario | Disposition |
|---|---|---|---|---|---|
| 1 | `cicd-quick-dev.md:103` · `smh-quick-dev.md:117` | suggestion | literal · blind · edge | `git worktree add --no-track` then `git branch --unset-upstream`: rc 128 `fatal: no upstream information` on every quick-lane open, reproduced by three lenses. In company with row 18 it is the line that teaches a reader to ignore a `fatal`. | applied @ c75d713a — both lines deleted |
| 2 | `smh-dev-task-tests.md:514` | nitpick | literal | "the task.yaml you wrote in Step 0" — Step 5 writes it. Inherited from the renamed file. | dismissed — relevance: no path fires, the agent finds the manifest eleven lines up |
| 3 | `git-policy.md:190` | suggestion | blind | Row 5 of § Two toggles says the close-out door re-runs the scope check; `critical-surfaces.md` and the code say only the quick-dev doors' Step 5 does. A reader of the hub rule treats Step 5 as courtesy. | applied @ c75d713a — row 5 rewritten: the tripwire is the door's Step 5, the close-out runs none |
| 4 | `smh-quick-dev.md:259-264` · `cicd-quick-dev.md` Step 3 | important | blind | The floor fence is four bare script lines with no tree pin; cwd persists between calls, so a floor run from the shared checkout measures `main` and prints a green the walkthrough pastes. | applied @ c75d713a — every floor line pinned `cd "<the tree>" &&`; the project door says so in prose |
| 5 | `handoff.md` | important | blind · acceptance | The hand-off says the freeze is not lifted, rows 1/8/9 are open and the receipt is @ dd5a5c42 — four commits stale; a next agent re-does or refuses done work. | applied @ c75d713a — SUPERSEDED banner at the top pointing at the walkthrough's last section |
| 7 | `scope_check.py` `load_map` | suggestion | blind · edge | A directory row without its trailing `/`, a leading-`/` row, or an exact-file row naming nothing is a dead row that reads as protected (`backend/auth` → CLEAR for `backend/auth/token.py`). | applied @ c75d713a — one rule for every non-prefix row: leading `/` is ERROR, an existing directory is ERROR (needs `/`), a row naming no file and not gitignored is ERROR; `.claude/settings.local.json` stays legal through the gitignore arm |
| 8 | `cicd-quick-dev.md` Step 4 · `smh-quick-dev.md` Step 4 | suggestion | blind | The record line `walkthrough approved by the operator @ <sha>` is written before the stop that obtains the word, and neither door says which sha. | applied @ c75d713a — written after the word, as a plain line naming the code tip he saw; a `STALE` means the word again, never a sha bumped by hand (compound 4) |
| 9 | `smh-non-crit-pr-push.md:34` · `lane_qualify.py:20,92` | suggestion | blind | `TASK-LIGHT` routes a small toolkit edit to the full lane citing a right-sizing licence this diff deleted; the quick lane built for that case is not offered. | applied @ c75d713a — the row and both docstrings name the quick lane |
| 10 | `task_preflight.py:1424` | suggestion | blind | In a repo with product dirs the staleness pathspec omits `.github/` and `firebase.json`. | dismissed — relevance: the Step 5 tripwire overlaps `.github/` (verified in the same fixture); the residual needs a commit after the tripwire, which the door forbids |
| 11 | `cicd-prune-worktree.md:363` | nitpick | blind | Fence comment still says "i.e. it was PARKED" under prose this lane rewrote. | applied @ c75d713a |
| 12 | `task_preflight.py` `_stale_against_sha` | important | edge | Absorbing `origin/main` after the approval — the preflight's own remedy — flips the approval STALE, because `<sha>..HEAD` is a two-endpoint tree diff. Reproduced. | applied @ c75d713a — the lane's own post-approval changes are listed with `git log --cc --name-only <sha>..HEAD ^<base>` (measured: names a conflict resolution, ignores a clean absorb); fallback to the tree diff, said aloud, when the base ref is unavailable |
| 13 | `task_preflight.py:1507` · `closeout_preflight.py:348` | important | edge · test-adequacy | A fenced record line or a literal `<sha>` reads in the lobby as "no review Verdict line — the full gate runs" (exit 0, no dereference); the project reader scans raw text, so the two disagree. Reproduced. | applied @ c75d713a — both readers scan stripped text and both refuse an unreadable record line (fenced or placeholder) as an ERROR; the cicd door names the reader the ad-hoc lane meets (compound 2) |
| 14 | `scope_check.py:172` | important | edge | The Step 5 tripwire reads the map from the lane's own tree; a lane that prunes the self rows (or writes a repo's first one-row map) reads CLEAR. Reproduced. | applied @ c75d713a — on `--diff` the map at the merge-base is unioned with HEAD's (generic set when the base has none); the `MAP:` line names what was used |
| 16 | `scope_check.py:230` | important | edge | A lobby-relative planned path (`<fixture>/Projects/X/backend/auth.py`, as typed from the lobby) or a `..` path compares as a string and answers CLEAR in a mapped repo. Reproduced. | applied @ c75d713a — a path that exists under the cwd is rebased onto the repo; outside is ERROR; `..` is ERROR; a planned new repo-relative file stays legal |
| 17 | `scope_check.py:98` | suggestion | edge | A planned set at directory granularity (`backend/`, `.`) is CLEAR over a critical child; the eject fires after the build. Reproduced. | applied @ c75d713a — a planned directory is judged as a prefix |
| 18 | twelve `cicd-*` Step 0 fences | suggestion | edge | The fetch and the mode query are independent lines; a failed fetch leaves cached refs and `epic_mode.py` prints `FULL <dead epic>` exit 0. Reproduced. | applied @ c75d713a — chained with `&&` in all twelve doors and their mirrors; a named STOP paragraph follows each fence (compound 6) |
| 20 | `smh-quick-dev.md:159` | nitpick | edge | The pin comment claims the fence is self-contained while the same line reads `$REPO` from Step 0. | applied @ c75d713a — the comment separates the PIN (bound here) from the FILLS (carried) in all five fences |
| 22 | `preflight-receipt.json` | suggestion | acceptance | Names the retracted `46bc4267` stamp. | applied at close-out — `task_preflight.py` rewrites it at the tip once this stamp exists (review-1 row 30) |
| 23 | `smh-quick-dev.md` Step 0.5 | suggestion | acceptance | The "reusing a tree `/smh-plan-task` cut? absorb `main` FIRST" block was dropped while `/smh-plan-task` routes its ⚡ lanes here; the first absorb then lands after the approval (row 12). | applied @ c75d713a — the block restored, with the reason (compound 3) |
| 24 | `cicd-label-tasks.md:44` · `smh-label-tasks.md:226` · `smh-close-task-merge-tree.md:331` | nitpick | acceptance | Three "light lane" survivors of Part D's re-point sweep, ambiguous now that LIGHT names an epic mode. | applied @ c75d713a — the three bodies say "quick lane"; `smh-label-tasks.md`'s frontmatter phrase stays (changing a description regenerates four launchers for one word — dismissed half) |
| 25 | `parts/SCC-446.md` row C | nitpick | acceptance | The literal `grep -l epic_mode.py` now lists 13 (the row-25 prose mention), not 12. | applied — recorded under § Acceptance matrix; the 12 call lines are pinned |
| 26 | `smh-dev-task-tests.md:27-28` | nitpick | acceptance | The rename carries a fourth edit (the intro paragraph) the plan did not enumerate. | applied — recorded under § Acceptance matrix |
| 27 | `parts/SCC-446.md` §3 | nitpick | acceptance | The stated reason for leaving `cicd-park.md` untouched overstates; park's epic push is a no-op under the PR landing. | dismissed — relevance: a plan aside, no failure follows |
| 28 | `task_preflight.py:1545` | important | test-adequacy | `if foreign_stamped: … elif quick:` — a stamped sibling walkthrough that merely mentions the key silences the lane's own approval-sha dereference. Reproduced. | applied @ c75d713a — the dereference runs whenever the lane's record line exists |
| 30 | `epic_mode.py:59` | suggestion | test-adequacy | The "git failed" branch had no case; with it removed a broken linked worktree prints TRUNK. | applied @ 6fc36dfa — pinned (`.git` file naming a missing gitdir → ERROR exit 2) |
| 31 | `scope_check.py` `--paths ""` | suggestion | test-adequacy | The empty-string guard had no case; the mutant prints CLEAR on a quoted unset variable. | applied @ 6fc36dfa — pinned |
| 32 | `wf_common.norm_path` | suggestion | test-adequacy | The backslash normalisation had no case; the mutant prints CLEAR on the PC spelling. | applied @ 6fc36dfa — pinned through scope_check |
| 33 | `test_approved_word_is_the_operators.py` | suggestion | test-adequacy | The grant scan matched five possessives; the same grant re-worded (a seat name, a verb form) passed. | applied @ 6fc36dfa — the seat roster and verb forms fire, the negation control stays quiet |
| 34 | `epic_mode.py:106` | nitpick | test-adequacy | Whitespace-before-`#` rule dead to the suite. | dismissed — relevance: fails toward the loud side; coverage for symmetry |
| 35 | `epic_mode.py:76` | nitpick | test-adequacy | The escape-only-in-double-quotes distinction is dead to the suite. | dismissed — relevance: contrived input |
| 36 | `scope_check.py` `overlaps` | nitpick | test-adequacy | "One line per path" unpinned. | dismissed — relevance: output shape, the word and exit unchanged (ruled the same in review 1) |
| 37 | `scope_check.py` `load_map` | nitpick | test-adequacy | The `why` default unpinned. | dismissed — relevance: cosmetic |
| C1 | lobby close-out | important | compound | The critical-surfaces line has no enforcement point outside the agent's hands and the hub rule claimed one. Parents: 3, 14, 16, 17. | dismissed — relevance: the line is a soft stop run by the agent by the operator's design (`critical-surfaces.md`); the text contradiction is fixed (3) and the base-map union (14) makes Step 5 honest |
| C2 | `cicd-quick-dev.md:355` | important | compound | The door promised a refusal (`closeout_preflight`) the ad-hoc lane never meets (it closes through `task_preflight`). Parents: 13, 29, 8. | applied @ c75d713a + c75d713a — the reader named per lane; the near-miss guard in both readers |
| C3 | `smh-quick-dev.md` Step 0.5 | important | compound | The dropped absorb-first block makes row 12's false STALE certain for every `/smh-plan-task` lane. Parents: 23, 12. | applied — under 23 and 12 |
| C4 | both Step 4s | important | compound | The STALE remedy is agent self-service: nothing distinguishes a re-approval from a sha bumped by hand. Parents: 8, 12, 33. | applied — under 8: the line is written on the word, a `STALE` means the word again; the runtime cannot tell, the door now says so |
| C5 | `scope_check.py` · `task_preflight.py` | important | compound | Both gate scripts resolved unrecognised input to the permissive word, patched one shape at a time. Parents: 7, 15, 16, 17, 13, 28. | applied — one rule per script under 7, 16, 17 and 13, 28 |
| C6 | `cicd-quick-dev.md:103` · twelve Step 0 fences | important | compound | The unconditional `fatal` masks the one `fatal` that matters, a failed fetch. Parents: 1, 18. | applied — under 1 and 18 |

Rows 6, 15, 19, 21 and 29 are the expanded members of the four same-claim groups and carry their group's disposition.

### Gates

| Gate | Result |
|---|---|
| Enforcement suite | `run_all.py` **87/87 files passed**, exit 0, clean tree — receipt `gates/suite.json` stamped @ `14b59913` by `gate_receipt.py` |
| Toolkit lint | `workflow_lint.py --toolkit-only` — **0 errors, 0 warnings, 8 info** |
| Assertion evidence | the lane's RED assertions and both fix batches' pins, re-run green: `test_scope_check` 141/141 · `test_epic_mode` 38/38 · `test_task_preflight` 139/139 · `test_closeout_preflight` 135/135 · `test_approved_word_is_the_operators` 130/130 · `test_boot_epic_branch_read` 51/51 · `test_trunk_mode` 37/37 |
| SOP currency | `sop_currency.py --paths <changed> --message "<subject>"` — clean, no output |
| Link + anchor | `check_links.py --base origin/main` — **clean** |
| Door parity | `test_command_surfaces.py` — **343/343 passed**; every edited door byte-copied to its `.opencode/` twin |

### Acceptance matrix

Imported from the Acceptance Auditor (Step 2, no double audit): all 37 rows of the plan and its five parts walked in an isolated copy, running wherever a row was runnable — **33 satisfied with a named proving assertion, 0 not satisfied, 6 diverging literally, 2 deferred by design.** The divergences, each with the truth beside the literal:

| Row | The plan's literal | What HEAD reports | Why |
|---|---|---|---|
| B·D | `run_all.py` 85/85 | 87/87 | `test_epic_mode.py` and `test_approved_word_is_the_operators.py` joined |
| C·C | `grep -c scope_check.py cicd-quick-dev.md` = 2 | 4 | one prose reference plus three call lines (recorded in review 1) |
| D·A | a rename with ≤ 6 changed lines | git reports `A`; 5 changed lines | git cannot pair the rename; the fourth changed line pair is the intro paragraph at 27-28, which the plan did not enumerate (finding 26) |
| D·B | `grep -c scope_check.py smh-quick-dev.md` = 2 | 3 | one prose reference plus two call lines (recorded in review 1) |
| D·C | no live `smh-quick-fix` reference outside history | 7 retirement notices remain | each says the door is retired; none invokes it |
| E·C | twelve doors call `epic_mode.py` | `grep -l` lists 13 | the thirteenth is the row-25 prose mention in the kickoff door; the 12 call lines are pinned by `test_epic_mode.py` F (finding 25) |

Plan row H (one gate at the tip, one review, the riders flip and the parent stays open) is satisfied by this section and the receipt; Plan row F is Part F's closure lane after AVCH-152.

**Declared-set reconciliation** (`declared_change_set.py diff` at `14b59913`, 154 paths). Block present, 0 rejected bullets, 12 undeclared, 2 unimplemented. The 12 stay, each a consequence of declared work: `reproduce-before-you-fix.md` (one phrase re-pointing at the rebuilt door), `test_sops_prds_folder.py` (the retirement entry), `wf_common.py` (the `norm_path` hoist), four generated launchers whose descriptions followed their commands, `.claude/rules/living-template-sync.md` (the path-scoped mirror), the two review-1 additions `test_approved_word_is_the_operators.py` and `test_task_preflight.py`, and `cicd-label-tasks.md` with its `.opencode/` mirror (this pass's row 24, one phrase). The 2 are Part F, deferred by design.

### Clean-Code Gate

Run nested per Step 3.5, importing Step 3's receipts and runs. `py_compile` on every changed `.py`: green. §2A comment contract on the added hunks: every non-obvious block carries its `SCC-441` provenance; no `AIDEV-*` note exists in the touched scripts to invalidate; no unowned TODO (the one `TODO` string is a test fixture); no comment restating code. §2C convention table on added lines: no Python line over 120 chars (the two long added lines are JSON prose strings), full annotations on every added `def`, no bare `python`, no `C:/` path, no `;` separator, no leftover debug print (the `print("ERROR")` lines are the script's verdict word), no bare `except`. ⛔ The four machine-floor commands of `code-standards` §6 do not exist in this repo (no venv, no `backend/`, no `frontend/`); the enforcement suite plus `workflow_lint --toolkit-only` and `py_compile` are the objective floor here, and they are green. Findings folded from Step 1: rows 11 and 20 (stale and self-contradicting comments), both applied.

### Changes applied

**All 30 patches, on 2026-09-11, in three commits in the reproduce-before-you-fix shape:**

| Commit | What | Seen red on its tree |
|---|---|---|
| `6fc36dfa` | the pins: `test_task_preflight.py` (absorb-then-not-stale, lane-commit-stale, hand-resolved-conflict-stale, the helper's three base arms, fenced/placeholder line refused, foreign stamp does not shield), `test_closeout_preflight.py` (the project caller's absorb and own-commit arms, both shapes refused, reader agreement on a fenced line), `test_scope_check.py` (fork-map union and unmapped-base variant, dead rows ×3 + gitignored arm + symlink, lobby-relative and `..` paths, planned directories, `--paths ""`, backslash and `./` spellings), `test_epic_mode.py` (a `.git` file naming a missing gitdir → ERROR; the fetch chained on every caller's call line), `test_approved_word_is_the_operators.py` (seat names, verb forms, the passive; three negation controls) | each block red by behaviour before its fix; the two that bind to names the fix commit introduces red by import as well |
| `c75d713a` | rows 1, 3, 4, 5, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 20, 23, 24 and compound 2–6: `task_preflight._stale_against_sha` takes the base ref and lists the lane's own post-approval changes with `git log --cc --name-only <sha>..HEAD ^<base>` (falls back to the tree diff, said aloud); both close-outs scan stripped text and refuse an unreadable record line; the lane's dereference runs beside a foreign stamp; `scope_check.py` unions the fork's map on `--diff`, resolves planned paths (cwd rebase, `..` ERROR, planned directory as prefix) and refuses a row that can never match (gitignore-aware); `lane_qualify.py` names the quick lane; the twelve Step 0 fences chained with a named STOP; the two dead `--unset-upstream` lines gone; the lobby floor pinned to the tree; the absorb-first block restored; the record line written after the word in both doors; git-policy row 5; the TASK-LIGHT row; three "light lane" phrases; the prune fence comment; five pin comments; every edited door byte-copied to `.opencode/`; SOP tables and rows, one changelog row, the map-row rule and the fork-map union in `critical-surfaces.md` | each fix hunk reverted by hand → its pin red → restored byte-identical → green (the agent's per-row proofs are quoted in review-lenses.md § Second pass); closing runs: `test_scope_check` 141/141 · `test_epic_mode` 38/38 · `test_task_preflight` 139/139 · `test_closeout_preflight` 135/135 · `test_approved_word_is_the_operators` 130/130 · `test_boot_epic_branch_read` 51/51 · `test_trunk_mode` 37/37 · `test_command_surfaces` 343/343 |
| `14b59913` | rows 5/21 (the hand-off's SUPERSEDED banner) and the second pass's raw reports appended to review-lenses.md | records; no pin owed |

Rows 25 and 26 are applied in this section's acceptance matrix; row 22 is applied at close-out, after this stamp, by `task_preflight.py` rewriting the receipt. The eight relevance kills (2, 10, 27, 34, 35, 36, 37, compound 1) carry their one-line reason in the table. One deliberate deviation from a lens's remedy, said aloud: a planned path that exists under the cwd but resolves OUTSIDE the repo is kept as a planned repo-relative file rather than refused — the doors run from the lobby, which holds a `README.md` and a `critical-surfaces.json` a project lane may legitimately be planning; only a `..` spelling, which can never be repo-relative, is refused (`scope_check.py` main, the comment says why).

**The pattern under the thirty, for the next lane:** a gate that compares strings it was handed instead of resolving them against the tree it judges (rows 7, 14, 16, 17), two readers of one record line fed different text (13), a precedence that let foreign evidence shield the lane's own (28), and a measure that compared trees where it meant to measure a lane (12). Each is now one rule in one place, pinned on both sides.

Whole suite at the fix tip: `run_all.py` **87/87 files** @ `14b59913`, clean tree, receipt `gates/suite.json`. `workflow_lint.py --toolkit-only` 0 errors 0 warnings 8 info · `check_maps.py --depth3-only --strict` clean · `check_links.py --base origin/main` clean · `sop_currency.py` over the 154 changed paths clean · `test_command_surfaces.py` 343/343 · `py_compile` on all nine changed Python files green.

## Pass 3 (2026-09-11) — dispositioned under the operator's new rule, no fourth review

The verdict of record for this lane stays the pass-2 **CONCERNS** section above. A third review pass
was run and it surfaced regressions from the pass-2 fixes; midway through it the operator ruled that
the fix -> full-re-review loop had wasted the day's credit and must never run again. The new rule
(memory `concerns-does-not-ship-fix-the-macro-in-lane`, 2026-09-11): the agent auto-fixes only
REPRODUCED FAILs; CONCERNS and sub-medium findings go to the operator, his call; the retest runs only
the pins that caught the fixed issues, never a fresh lens fan-out.

**Fixed here (`0a8faf85`), the one reproduced regression I introduced in pass 2 plus stale wording:**
`closeout_preflight.integration_branch` now reads the epic off `origin/epic/*` as well as local heads,
so a `--no-track` story lane no longer falls back to `origin/main` and reads a clean epic absorb as
STALE (pinned, `test_closeout_preflight.py` review-3, 136/136); the SOP index row and the quickref
FAST-eject arrow name the current mechanism instead of the retired quick-fix lane and router.

**Escalated to the operator, not fixed (his call):**
- The **project** quick lane serving a STORY lane cannot close: `/cicd-close-story-merge-tree` demands a
  `suite` receipt the quick lane never stamps (BLOCKED) and `finish` needs a tip it never writes (HELD).
  This is a design question — is the quick lane meant for story lanes, or only ad-hoc task lanes? It does
  not affect this lobby lane, whose `task_preflight` reports clear.
- The approval-staleness net in a repo **with** product dirs (`backend/`, `frontend/`, …) is blind to a
  post-approval commit to a root deployable (`Dockerfile`, `firebase.json`). Widening the net is a
  tradeoff (it re-gates on docs typos), so it is the operator's call, not a silent patch.
- The project quick lane's later fences bind `$L=$(pwd)`, which captures the project tree by Step 5, so
  the lobby-only tripwire is looked for in a thin project. Inferred, non-blocking; the fix is to carry the
  Step-0 lobby absolute as a literal rather than re-run `pwd`. Left for the operator's go.

This lane (`chore/SCC-441-...`) closes through `/smh-close-task-merge-tree` -> `task_preflight`, which
reports `clear to close out and merge` at this tip. None of the three escalated items touches it.

---

## Part F — the closure lane (2026-09-12)

**What was waiting.** Parts A–E shipped the toggles; Part F is the three lobby documents that
describe the finished state, and the plan deliberately held them until AVCH-152 landed, because
AVCH-152 is what decides whether the light epic's discount is real. AVCH-152 is Done, and both of
its rulesets are armed on GitHub, so the docs can now describe a system instead of an intention.

**What was measured before a word was written.** Both epic rulesets were read live off the API
rather than off AVCH-152's plan, because a plan says what someone meant to arm:

| Ruleset | Includes | Excludes | Required contexts |
|---|---|---|---|
| `epic write gate (AVCH-119)` · `22247932` | `refs/heads/epic/**` | `refs/heads/epic/*-light-epic-*` | Backend (Python) · Frontend (Node.js) · Backend E2E (Firestore emulator) · Frontend E2E (Playwright) |
| `epic write gate — light (AVCH-152)` · `23051729` | `refs/heads/epic/*-light-epic-*` | — | Backend (Python) · Frontend (Node.js) |

Both `active`, both strict, both carrying a `pull_request` rule, neither with a bypass actor. The
partition is exact: every `epic/**` ref is claimed by one of the two and no ref by both. That is the
property worth checking rather than assuming, because the two ways it can break are not symmetric —
an overlap is dishonest and harmless, a gap is an epic branch with no required checks and no
required pull request at all.

**The four edits.**

| File | What it now says |
|---|---|
| [`workflows_testing_SOP.md`](../../../docs/_scc_sops_prds/workflows_testing_SOP.md) § 6 | Two paragraphs after the `⛔ NOT ARMED HERE` caveat: the server half of the LIGHT toggle is two rulesets, not one; a ruleset demanding an E2E check the workflow skips blocks nothing (a skipped job reports **Success** and satisfies the requirement) but advertises a gate that never ran; and the arming order is fixed **light before full** because `full` first writes the light-epic exclude while the light ruleset is still absent |
| [`tea_testing_guide.md`](../../../docs/_scc_sops_prds/tea_testing_guide.md) § 6.0 | The routing half nobody had written down — the changed paths pick the stacks, the PR's **base branch** picks the E2E tiers — as its own table beside the path table; then the two epic rulesets with their ids, patterns and contexts, appended to *What blocks a merge*; and the three-gates table's ruleset row widened from `main` alone to all three branch rulesets |
| [`smh-new-project.md`](../../../.agents/commands/smh-new-project.md) | A step 5: a skeleton clone ships all three ruleset recipes and arms **none** of them, so the server requires nothing until somebody runs `arm_rulesets.py` — dry run, then one `--apply` at a time, light before full. The recipes were already in the skeleton; the instruction to run them was in nobody's file |
| [`workflows_testing_SOP_changelog.md`](../../../docs/_scc_sops_prds/workflows_testing_SOP_changelog.md) | One row, per `sop-currency`, in the same commit |

`.opencode/commands/smh-new-project.md` is a byte-identical mirror and was re-mirrored; `.roo/` and
the Claude skill are generated thin launchers that carry no body, so they need nothing.

**Evidence at this lane's tip.**

| Gate | Result |
|---|---|
| `python3 .agents/scripts/tests/run_all.py` | **92/92 files passed** |
| `python3 .agents/scripts/workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, 8 info |
| `python3 .agents/scripts/check_maps.py --depth3-only --strict` | clean, exit 0 |
| `python3 .agents/scripts/check_links.py --base origin/main` | clean |
| `python3 .agents/scripts/task_preflight.py` | clear to close out and merge |

**No `Verdict:` line is added by this lane, deliberately.** § Code Review (2026-09-11)'s
`CONCERNS @ 14b59913` still governs and still describes the code it was stamped on; Part F moves no
code, and `task_preflight` reads the four documents that moved as exactly what they are — the full
gate runs rather than a skip being granted. Adding a second stamp for a docs edit would pull in the
roster gate for a review that never ran.

**Declared-set reconciliation.** The two bullets `declared_change_set.py diff` has returned as
`unimplemented` since 2026-09-10 — `tea_testing_guide.md` and `smh-new-project.md` — are implemented
here, which is what closes the parent. The SOP and its changelog were already in the declared set as
Part F rows.
