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
- [ ] **Part F · SCC-441** — the closing docs (`tea_testing_guide.md` § 6.0, SOP § 6, one line in `smh-new-project.md`) — a closure lane after AVCH-152, per the plan; not this landing

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

**Gates at the shipping tip** (`85454a49`, after the review fixes): `workflow_lint.py
--toolkit-only` 0 errors, 0 warnings, 8 info · `check_maps.py --depth3-only --strict` clean ·
`check_links.py --base origin/main` **clean, 111 markdown files, 1108 path claims** (run
sandbox-off) · `run_all.py` **86/86 files** (84 → 86 across the lane: `test_scope_check.py`,
`test_epic_mode.py`).

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

- [ ] On the other machine, after pulling: run `/smh-sync-agents` once — its global caches still hold the old `smh-quick-dev` body and the retired `smh-quick-fix` door until then (Part D's audit, pre-mortem).
- AVCH-152 is next in the order (its plan carries its own `approved` stop and three ask-first stops on CI, rulesets and the skeleton); Part F's closure lane follows it.

## Code Review (2026-09-10)

Verdict: PASS @ 46bc4267ffda04ffce24933dab0ed77fa5154c27
Suite evidence measured on 46bc4267ffda04ffce24933dab0ed77fa5154c27 — run_all.py 86/86 files, workflow_lint --toolkit-only 0 errors 0 warnings, check_maps --depth3-only --strict clean, check_links --base origin/main clean, py_compile green on all 28 changed .py files, 19/19 mutants killed across four declared tables.

review-runtime: fan-out

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- acceptance-auditor · ok
- literal-correctness-hunter · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none

dispositions:    per-lens: blind-hunter=7/0/0 · edge-case-hunter=7/0/0 · acceptance-auditor=8/0/0 · literal-correctness-hunter=2/0/0 · test-adequacy-auditor=9/0/0 · clean-code-audit=8/0/0 · applied-claim-verification=3/0/0
drift:           undeclared=7 · unimplemented=2 · incomplete=0 — the 7 are dispositioned above, the 2 are Part F's closure lane after AVCH-152

### Step 0.7 — re-derivation

- Nothing moved under this lane: `origin/main` is `cf1544f9`, the merge-base is the same commit, and 0 commits landed on the trunk while the lane was built.
- It changes nothing here, because true overlap with the trunk is EMPTY — no path this lane touches was touched on `origin/main` since the fork.
- Re-measured at the shipping tip `46bc4267` after BOTH fix batches: `run_all.py` 86/86 files, `check_links --base origin/main` clean (111 files, 1108 claims), `check_maps --depth3-only --strict` clean, `workflow_lint --toolkit-only` 0 errors 0 warnings, and two mutant tables 10/10 killed with the restore verified.

**Why PASS.** Under §7 the three triggers are properties of the shipped diff, and all three are
clear: no machine check errors on changed lines (the floor here is `run_all.py`, `workflow_lint`,
`check_maps` and `check_links`, plus `py_compile` on all 28 changed scripts — there is no
`backend/`, no `frontend/` and no repo venv, so ruff, pyrefly and tsc do not apply), no §2 banned
pattern, no secret, and zero unresolved §1 comment-contract gaps or §2 judgment calls. All 44 raw
findings are applied. Nineteen mutants across four declared tables are killed, restores verified.

**This verdict first read CONCERNS, and that was wrong.** Recorded here because the correction is
the more useful fact. The first stamp reasoned that "a review which had to correct this much of
its own subject does not read PASS" — a judgement about the lane's *process*, borrowed from the
SCC-412 precedent, which §7 does not authorise. §7's CONCERNS row lists unresolved comment-contract
gaps and unresolved judgment calls; nothing was unresolved. The operator refused the verdict on the
standing ruling that CONCERNS does not ship, and the refusal was correct on the law.

**What it was NOT corrected by is a re-label.** Re-stamping on that argument alone would have been
the same failure wearing the other sign. Instead every row in the table below marked `applied` was
re-verified against the shipped tree rather than trusted, and a clean-code audit ran the §1/§2/§3
pass the first stamp had skipped. Together they found **eight more real defects**, rows 25–32, and
three of them are the same shape as the finding the review called critical:

- The two gates that guard the Step 0 mode line did not guard the half that broke. Worse, one of
  them **prints its requirement text to the author on a miss**, and that text asked for the
  unpinned form by name — so the gate would have instructed the defect back in.
- The law described the mode switch as "the third token of the branch name". The code, like the
  server's own `contains()`, tests for a substring. The positional rule is false even of its own
  canonical example, and nothing pinned the wording.
- The headline fix of Part E's review — the derived pathspec — had no failing case. Reverting it
  left the file 106/106 green, because every fixture builds `backend/` and the fallback arm is the
  one the lobby itself takes.

One of the audit's own proposed fixes was **rejected on the merits**: excluding `*.md` from the
staleness check would have blinded it to the lobby's entire product, since the lobby carries none
of the five product directories and its doors and rules are markdown. The wording was fixed
instead, and a mutant now pins that the exclusion stays out.

**Calibration.** 44 findings, 44 applied, none dismissed — and that is the number worth arguing
with, so: each one was re-tested against §6.5's three questions, and what carried them was that the
subject is law text and small scripts, where "is it REAL?" is answerable by running the line. None
was fixed because it was cheap. The two that came closest to taste — a duplicated five-line
normaliser and an unreachable default argument — are named §2 bans, not preferences, and both were
introduced by this lane.

### Findings

**33 raw findings, 24 rows.** The gap is cross-lens duplication, deduped here and counted whole in
`dispositions:` above: the lobby map's under-coverage came from the blind hunter and the edge-case
hunter independently, the empty-`--repo` defect from the edge-case hunter against both scripts, the
all-empty-map fallback from the blind hunter and the edge-case hunter, and the vacuous
`--repo is required` row from the blind hunter and the test-adequacy auditor. Two lenses finding
the same defect from opposite ends is the signal the fan-out exists for, so it is recorded, not
collapsed into one lens's credit.

| # | file:line | severity | failure scenario | disposition |
|---|---|---|---|---|
| 1 | twelve `cicd-*` doors, Step 0 | critical | The mode line runs `python3 .agents/scripts/epic_mode.py` on the line after `cd "$PROJECT_ROOT"`. No project ships that script, so the first step of every branch-touching door dies `No such file or directory`. | **applied @ 85454a49** — `L=$(pwd)` pins the lobby before the fetch's `cd`, and the call is `cd "$L" && python3 …` in all twelve |
| 2 | `test_closeout_preflight.py` | critical | The VERDICT arm of the new shared staleness helper had no failing case: deleting `elif changed:`'s body outright left the file 89/89 green. Only the quick-lane arm was pinned. | **applied @ 85454a49** — QL11–QL14; mutant M1 (delete the branch) now KILLED by QL8, M2 (collapse the two remedies) by QL14 |
| 3 | `scope_check.py`, `epic_mode.py` | important | An unbound `$PROJECT_ROOT` reaches the script as `""`; `cd ""` exits 0 without moving and `Path("").resolve()` is the cwd, so both answer confidently about the **lobby**. From the lobby the answer is `TRUNK`, which routes a story on a live FULL epic to the close-out's trunk arm — a PR into `main`. | **applied @ 85454a49** — both refuse an empty `--repo` before resolving; mutants E2 and S1 killed |
| 4 | `epic_mode.py:39-44` | important | LIGHT's cost line promises "two checks, E2E once". No repo's CI reads `-light-epic-` yet, so every landing still pays four checks — and the close-out tells the agent a skipped E2E "is the design, not a red", so a genuinely red E2E reads as the expected skip. | **applied @ 85454a49** — `light_armed()` probes the repo's own workflows and appends `⛔ NOT ARMED HERE` until one reads the token; derived, so the caveat clears itself. Mutants E3/E4 killed |
| 5 | `.agents/critical-surfaces.json` | important | The lobby's `ci` surface listed four preflights. The roster gate, the receipt writers, the SOP gate, the shared `git()` helper every gate imports, the gate tests and the permission fences were all CLEAR — a quick lane could rewrite what "green" means and the line that is supposed to stop it. | **applied @ 85454a49** — the surface now carries the whole gate family plus `.agents/scripts/tests/`; the map, the script and the rule already protected themselves |
| 6 | `scope_check.py` | important | A map that parses with zero patterns matched nothing **and** suppressed the loud generic fallback, so it was strictly weaker than having no file — and the skeleton ships exactly that placeholder. A new project's first lane read a bare `CLEAR` with no `MAP:` line. | **applied @ 85454a49** — `elif not rows:` falls back to the generic set and prints which of the two happened; mutant S2 killed |
| 7 | `scope_check.py` `load_map` | important | A non-string entry became `str(None)` — the literal pattern `"None"`, which matches no path and reads to a maintainer as a protected surface. | **applied @ 85454a49** — a non-string or blank entry is an ERROR naming the map; mutant S3 killed |
| 8 | `closeout_preflight.py` | important | The staleness check diffed `backend/ frontend/` only, so a post-approval commit to `firebase/`, `functions/` or a root `Dockerfile` moved nothing it could see — and in a repo with **neither** directory git exits 0 on a pathspec matching nothing, which reads exactly like "no code moved". | **applied @ 85454a49** — the pathspec is derived from `PRODUCT_DIRS` with a whole-tree-minus-planning fallback |
| 9 | `closeout_preflight.py` | important | The quick lane's record line captured its sha, printed eight characters and dropped it, so a walkthrough approved at one tree read clean after later commits — the exact question the sha was made required to answer. | **applied @ 0363764b** — one helper, two callers; QL7–QL9 |
| 10 | `closeout_preflight.py` | important | An approval sha resolving to nothing was a non-blocking WARN, and the quick lane has no roster behind it — that line is the entire evidence of approval. | **applied @ 85454a49** — ERROR on the approval arm, WARN kept on the verdict arm where `roster.judge` corroborates; mutant M3 killed |
| 11 | `cicd-quick-dev.md:336` | important | Step 4 called `## Your Actions` "errands only, never a decision" — the exact inverse of its twin and of `jira_feed.py check-actions`, which hard-refuses an errand row. A door following its own text produces a walkthrough the close-out refuses. | **applied @ 85454a49** — the twin's wording, plus the naming of the refusal |
| 12 | `cicd-close-story-merge-tree.md:356` | important | The landing record demanded the epic sha in a walkthrough that must be committed **before** the PR opens, and its remedy ("push the story branch again") cannot reach a merged PR — it moves a dead head, re-runs checks on a branch Step 5 is about to delete, and leaves the tree dirty for the prune. | **applied @ 85454a49** — the merge sha goes to Step 4's Dev Record, filed after the landing on purpose; the walkthrough's landing line carries only what is knowable pre-PR |
| 13 | `cicd-prune-worktree.md:345,380` | important | Both passages taught the retired `HEAD:epic/` landing and cited the rewritten `git-policy` as authority. The second told the agent an absent remote branch is the normal case, which the PR landing **inverted** — the landing PR's head puts the branch on origin. | **applied @ 85454a49** — and the remote-first reason rewritten: under the PR landing the merged-into-upstream check passes vacuously on a parked branch, so deleting the remote first is what forces the real ancestry question |
| 14 | `cicd-merge-epic-workingtrees.md:279` | important | The batch door still landed every lane by direct `HEAD:epic/` push. This record had deferred it as out of scope; the auditor rebutted that on the merits. | **applied @ 85454a49** — each lane lands by its own PR into the epic, one at a time |
| 15 | `critical-surfaces.md:104-106`, `rules/INDEX.md:56`, the SOP | important | The rule pointed the eject tripwire at two **close-out** doors that never call the script, so a reader looking for it at the door found nothing. It was built at Step 5 of the two quick lanes. | **applied @ 85454a49** — all three pointers re-aimed at Step 5 |
| 16 | `check_links.py` at `4d7b3a2e` | important | 15 unresolved path claims while this record called the gate clean. The claim came from a `--paths` run over the then-dirty files, not the lane diff. | **applied @ 85454a49** — all 15 fixed; the record corrects itself above rather than restating |
| 17 | `test_scope_check.py`, `test_epic_mode.py` | important | No pin that either quick-lane door actually calls `scope_check.py`; `epic_mode.py` had no fixture for a **linked worktree**, which is where all twelve callers run and where `.git` is a FILE; a well-formed-JSON map with the wrong shape had no case at all. | **applied @ 85454a49** — block G pins both doors' `--paths`/`--diff`/`--repo`; E2 runs a real linked worktree (mutant E1, `.exists()`→`.is_dir()`, killed); six wrong-shape cases added |
| 18 | `test_epic_mode.py:109` | suggestion | `--repo is required` asserted only `rc == 2` — a MISSING script also exits 2. The same vacuity its sibling file documents and guards against. | **applied @ 85454a49** — the refusal text is pinned |
| 19 | `test_scope_check.py` | suggestion | "A repo map WINS over the generic rule" asserted CLEAR and nothing else, so a script that always printed CLEAR passed it. The `what` label, `--diff`'s blindness to uncommitted work, and `_QUICK_LANE_RE`'s tolerances were all unexercised. | **applied @ 85454a49** — the map-WINS case is now a pair (same path OVERLAPs unmapped); QL13/QL14 pin each remedy wording; QL15 pins the contract with the dirty-tree gate; QL16 runs 7 tolerated spellings and 4 controls |
| 20 | `epic_mode.py` docstring | nitpick | It described a positional "third token" test the code does not perform — the code searches the whole name, which is what CI's `contains()` does. | **applied @ 85454a49** — "the name CONTAINS" |
| 21 | `test_boot_epic_branch_read.py` | suggestion | The ref-discovery regex accepted an unquoted `--repo $PROJECT_ROOT` while the requirement beside it pinned the quoted form. | **applied @ 4d7b3a2e** — regex requires a quote, with a quotes-only mutant |
| 22 | five part plans | suggestion | Five per-part `walkthrough.md` paths were declared NEW and never built — the per-part folders were retired when the five lanes became one. | **applied @ 85454a49** — re-pointed at this consolidated record |
| 23 | six plan files | nitpick | The two `docs/doc-graph.*` bullets carried no `→ row`, so the parser counted them as neither declared nor incomplete and the drift check listed nine undeclared paths. | **applied @ 85454a49** — both carry the row their SOP bullet carries; 0 incomplete in all six |
| 24 | this record | nitpick | Three counts and one gate result were wrong. | **applied @ 85454a49** — corrected in place, with the original claim shown |

### Findings 25–32 — the second pass, after the CONCERNS verdict was refused

Rows 1–24 came from the five lenses. These came from verifying those rows' `applied` claims
against the shipped tree, and from the clean-code audit that should have preceded any verdict.

| # | file:line | severity | failure scenario | disposition |
|---|---|---|---|---|
| 25 | `test_boot_epic_branch_read.py:53` | important | The `ref-discovery` gate accepted the bare `python3 .agents/scripts/epic_mode.py` — the exact shape finding 1 proved cannot run — and its requirement text, which the gate PRINTS to an author on a miss, asked for that shape by name. The gate would have reinstated the defect it exists to catch. | **applied @ 46bc4267** — the regex requires `cd "$L" &&` on the call line, the requirement text says why, the GOOD fixture carries the pinned form; mutants G1 (unpinned) and G2 (pinned at the project) killed |
| 26 | `test_epic_mode.py` block F | important | It counted twelve callers of `epic_mode.py` and never asked whether any could execute. It reported twelve happy callers throughout the entire period when all twelve were broken. | **applied @ 46bc4267** — every call line must carry the lobby pin, and `L=$(pwd)` must appear BEFORE it, since a pin bound after a `cd` points wherever the shell was left; mutant G3 killed |
| 27 | `git-policy.md:78`, `worktree-per-story.md:267`, the SOP's LIGHT section, `test_trunk_mode.py:8,124` | important | The law said the mode is "the third token of the branch name". `classify()` and CI's `contains()` both test for a substring. The positional rule is false even of its own canonical example — split `SCC-441-light-epic-2-x` on `-` and the third token is `light` — and on `epic/SCC-9-epic-2-light-epic-migration` a reader answers FULL while every door answers LIGHT. | **applied @ 479ae450** — all four sites state containment, and `test_trunk_mode.py` now requires the law to say so and refuses the phrase `third token`, because every other assertion in that block is a substring search the wrong description satisfied equally well |
| 28 | `closeout_preflight.py:315` | important | In a repo with none of the five product directories — **the lobby is one** — the fallback counts every tracked file, so a `docs/` typo after an approval reported as `1 code file(s) changed … STALE, re-gate`. The identical commit in a repo with `backend/` reported nothing. | **applied @ 46bc4267** — the block stays (this arm genuinely cannot tell code from prose, and re-gating is the cheaper error) but the message says what was measured; mutants A5/A6 pin both halves of the derivation |
| 29 | `test_closeout_preflight.py` | important | The headline SCC-446 fix had no failing case. Reverting the derived pathspec to the pre-fix `["backend/", "frontend/"]` left the file **106/106 green**, because every fixture builds `backend/` and the fallback arm was never executed. A gate never seen red is a description of intent (`tests-must-gate-for-real` §5). | **applied @ 46bc4267** — `lane_repo(product_dirs=False)` plus QL17–QL20c; the audit's surviving mutant A1 is now KILLED, and A2/A3 pin the fallback's width and its two exclusions |
| 30 | `scope_check.py:77` | suggestion | A third byte-identical copy of `lane_qualify.norm` (§2, re-implementing what exists). | **applied @ 46bc4267** — hoisted to `wf_common.norm_path`. Importing the sibling, as the audit suggested, would couple the RISK checker to the SIZE checker, which the rule says answer different questions; the two pre-existing copies are out of this diff and left alone |
| 31 | `epic_mode.py:85,94` | suggestion | `classify(names, repo=None)` forced a `repo is not None` guard that can never be False: `main()` is the only caller and always passes one (§2, dead branches; flexibility nobody asked for). | **applied @ 46bc4267** — `repo` is required, the guard is gone |
| 32 | `closeout_preflight.py:296,332`, `scope_check.py:96,106`, `test_scope_check.py:106,193` | nitpick | §3 contract gaps in new code: two unhinted parameters on a new signature, a 142-char line over the 120 limit, two public undocumented functions where `pattern_hit` is where the match semantics live, two `f`-strings with no placeholders. | **applied @ 46bc4267** |

**Mutation tables — 19 mutants, 19 killed, every restore verified byte-identical.**

| Table | Mutants | Killed | What it certifies |
|---|---|---|---|
| `sweep_review` | 3 | 3/3 | the staleness gate's verdict arm, its two distinct remedies, its asymmetric warn/err |
| `sweep_scripts` | 7 | 7/7 | the linked-worktree `.git` file, both empty-`--repo` refusals, the `light_armed` probe in both directions, the empty-map fallback, the dead-pattern guard |
| `sweep_gate` | 3 | 3/3 | the lobby pin on a door's mode line, the project-pinned spelling, `L` bound after a `cd` |
| `sweep_audit` | 6 | 6/6 | the audit's own survivor, the fallback's width, its two exclusions, **the `*.md` exclusion staying out**, and both arms of the derived wording |
