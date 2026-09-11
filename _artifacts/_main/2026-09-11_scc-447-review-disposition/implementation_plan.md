---
IsArtifact: true
ArtifactMetadata:
  title: SCC-447 — Review disposition doctrine: one review per lane, reproduce or drop, three lenses, no cap
  type: implementation_plan
  date: 2026-09-11
---

# SCC-447 — implementation plan

**Ticket:** [SCC-447](https://sudo-command.atlassian.net/browse/SCC-447) · **Decisions of record:** ticket comment 10508 (2026-09-11), which governs over the description where they differ
**Lane:** `chore/SCC-447-review-disposition` · worktree `.claude/worktrees/scc-447-review-disposition` · cut from `origin/main` @ `03778605`
**Door:** `/smh-dev-task-tests` (the full lane — the work touches gate scripts and the tests directory, which the quick lane may not)
**Sibling lanes:** none live. `.claude/worktrees/SCC-439-retire-bmad-token-gate` is a dead stub (its `.git/worktrees` entry is gone) and `.claude/worktrees/scc-386-memory-long-term-only` is an empty stub on `main`. Neither carries a diff; no landing-order dependency. Both need a sandbox-off prune — out of scope, one line here so it is on the record.

## The problem, in one paragraph

The review engine has no stop condition an agent can reach on its own. Its lenses are told to be exhaustive and are measured by what they return, the assessor was told to fix everything that survived, the verdict floor was computed before the fixes and never moved with them, and the preflight's remedy for FAIL said "re-run the review". Measured over every review on disk (138 with a verdict, 88 with per-lens ledgers): FAIL on the first stamp 3 of 138, 17.9 fixes per review, 52% of those fixes on findings that can never block, re-review converting a non-PASS to PASS 1 time in 7, the verifier wave refuting 2 findings in 18 reviews. SCC-441 ran that machine three times over a 155-file, 1.46 MB diff (48 files were byte-copy mirrors, 26 the lane's own records) and consumed a week of credit without closing.

## Acceptance — checkable, in the ticket's revised order

| Row | Statement | Proved by |
|---|---|---|
| **A** | `code-standards.md` §6.5 and §7 (and the byte twin `.claude/rules/code-standards.md`) carry reproduce-or-drop, the action policy by severity, "CONCERNS ships on the operator's word", "one review per lane", and "the floor is computed on what is still OPEN at the stamp" | `test_review_disposition.py` block A: relationship regexes with in-memory counter-examples; twin byte-equality |
| **B** | Engine: step-01's lens table has exactly three rows (Edge Case, Acceptance, Test-Adequacy) and no levels; the hunter contract and the auditor rubric require a runnable reproduction command on every critical/important; step-02 is a pass-through; step-03 §4/§5 carry the action policy with the floor on open rows; step-04's record vocabulary matches; the `.claude/skills/code-review-engine/` cache is byte-identical | `test_review_disposition.py` block B; `test_review_engine.py` and `test_lens_roster_contract.py` updated and green |
| **C** | Both review doors and their `.opencode/` byte mirrors: Step 1 runs `review_scope.py` and passes its output as `DIFF`; the fix paragraph is the action policy; Step 3.5 nested runs the machine floor only; Step 4 carries the re-stamp block and the revised verdict rules; NO door instructs a full re-review on a fix batch; no level derivation, no `lens_budget` row | `test_review_disposition.py` block C; `test_command_surfaces.py` 343/343; `test_twin_parity.py` green |
| **D** | Scripts, each seen red first: `review_scope.py` strips mirrors/records/generated launchers, groups commits by key, refuses a range spanning two keys; `repro_receipt.py` records command, exit and output per finding id; `walkthrough_roster.py` refuses a second full roster without the operator's line, a fixed suggestion/nitpick, a fixed row without a pin, a fixed/escalated critical/important without a receipt on disk, and a PASS/CONCERNS with an open critical; `task_preflight.py`'s FAIL message says "re-run the pins and the suite, re-stamp" | `test_review_scope.py`, `test_repro_receipt.py`, `test_walkthrough_roster_dispositions.py`, `test_task_preflight.py` (one new case) — all with a mutation sweep |
| **E** | `cicd-autopilot-claude.md` (+ mirror), `autopilot_SOP.md`, and the SOP §15 table row: a non-PASS verdict escalates; no fix child, no fresh reviewer; "never ships by itself" gone | `test_review_disposition.py` block E |
| **F** | `work-consolidation.md` Rule 2 and `smh-plan-task.md` (+ mirror): parts are built AND reviewed in sequence, each review on its own commits; the enforcement suite is the integration check; a plan-time size warning when a part's declared set exceeds 40 files | `test_review_disposition.py` block F |
| **G** | `workflows_testing_SOP.md` and its changelog updated in the same commits as the surfaces they describe; `workflow_lint.py --toolkit-only` 0 errors; `run_all.py` N/N through the receipt writer on a clean tree | pasted output + `gates/suite.json` |

## Design — the mechanisms, stated once

### D1. The action policy (code-standards §6.5 + §7, engine step-03)

| A lens reports | The assessor does | Disposition written |
|---|---|---|
| `critical` or `important` **with** a reproduction command | runs it through `repro_receipt.py`; the receipt is the evidence | see the next two rows |
| reproduced `critical` | fixes it, in this lane, with a pin, through `reproduce-before-you-fix` G1–G5 | `fixed @<sha> · pin <test>[:<case>] · repro <id>` |
| reproduced `important` | does **not** fix it; it goes to the operator in the end-of-review message with the receipt and a one-line recommendation | `escalated · repro <id> · default: ships as recorded` |
| `critical`/`important` that does not reproduce, or arrives with no command | dropped, counted, never written up individually | `dropped — no reproduction` (one count line) |
| `suggestion` / `nitpick` | nothing; a count | `recorded` (one count line) |
| a reproduced row this lane structurally cannot hold (other live lane · other repo · open decision) | the existing `defer` with its ONE named blocker | `deferred — <blocker>` |

The verdict floor is computed at the stamp on what is **open**: an open reproduced `critical` → FAIL; an open reproduced `important` (escalated, or deferred) → CONCERNS; everything else → none. A row closed by a fix and a green pin no longer counts. CONCERNS is a shippable verdict; the go/no-go is the operator's word.

### D2. One review per lane, and the re-stamp

The engine runs once. After the agent's fix batch (reproduced criticals only) the retest is: the pins named in the `fixed` rows, plus the enforcement suite once through the receipt writer. Then a new section:

```
## Code Review (<date>, re-stamp after fixes)

Verdict: PASS|CONCERNS @ <sha>
retest: scoped — pins: <test:case>, … · suite: run_all N/N @ <sha> (gates/suite.json)
review: carried from the one review @ <sha1> — no lens re-run
```

No second `lenses_run:` roster. `walkthrough_roster.py` counts roster headers in the stripped text; a second one refuses the close-out unless a line `re-review: approved by the operator — "<his words>"` is present. The last `Verdict:` still governs (unchanged reader).

### D3. The end-of-review message (the review never pauses)

The review runs lenses → reproduce → fix reproduced criticals → gates → stamp → **ends the turn** with one screen: the verdict and sha; the fixed rows (id, pin); the escalated rows (id, one-line evidence from the receipt, recommendation); the counts of dropped and recorded; the default ("ships as recorded"); and the two words that move it: `approved` (the operator runs the close-out door) or `fix <ids>` (the agent fixes those with pins, runs the scoped retest, re-stamps, in one turn). Nothing is written under `## Your Actions` for a finding — an open action row holds the ticket forever at `finish`, which is the loop.

### D4. `review_scope.py` — what a lens reads, with no cap

```
python3 .agents/scripts/review_scope.py --repo <worktree> --base origin/main \
        [--key <PART-KEY> | --range <sha>..<sha>] --out <artifacts>/review/diff.patch
```

Reads `base..HEAD` commits, extracts every `[A-Z]+-\d+` in each subject, and groups commits by part key (a key other than the lane key in the subject is the part; otherwise the lane key). With more than one part in the range and no `--key`/`--range`: **exit 2, naming the keys**. Writes the diff restricted to the selected commits' files, minus the withheld classes: mirrors (`.opencode/`, `.roo/`, `.claude/`, `.agent/`), generated launchers (any file whose text carries `GENERATED by sync-agents`), and records (`_artifacts/`, `_bmad-output/`, `docs/_scc_sops_prds/`). Prints every withheld path with its class, the kept count and bytes. No byte cap exists; the size of a review is the size of a part. Measured on the SCC-441 diff: 155 files / 1.46 MB in, 81 files / 658 KB out.

### D5. `repro_receipt.py` — a reproduction is a receipt, not a paste

```
python3 .agents/scripts/repro_receipt.py run --root <artifacts> --id <finding-id> --cwd <worktree> -- <command…>
```

Writes `<root>/gates/repro/<id>.json`: `{id, command, cwd, exit_code, output_tail, sha, dirty_tree, recorded_at}`. There is no `--result` flag; a receipt implies execution. An existing id refuses (exit 2) unless `--replace`. The findings row cites `repro <id>`; `walkthrough_roster.py` resolves the file beside the walkthrough and refuses when it is absent. Same shape as `gate_receipt.py`, kept separate because a gate receipt is one per gate name and a reproduction is one per finding.

### D6. The roster (engine step-01)

| Lens | Gets | Tree | Runs | Reproduction field |
|---|---|---|---|---|
| Edge Case Hunter | `DIFF` + `REPO` | own worktree copy | always | required on every critical/important: `reproduce: <command>` + `expected_wrong_output: <text>` |
| Acceptance Auditor | `DIFF` + `STORY_FILE` + context docs | own worktree copy | `review_mode: full` | required (a command or a grep that shows the missing behaviour) |
| Test-Adequacy Auditor | `DIFF` + `REPO` | own worktree copy | always | required (the mutant or the input under which the test still passes) |

Blind Hunter, Literal-Correctness, the two levels, `lens_budget` (it governed only the Literal lens), the verify wave and the compound role are retired. `lenses_counted: 3/3`. The `dispositions:` line keeps its shape with three lenses.

### D7. Parts in sequence (work-consolidation Rule 2, completed)

Rule 2 already sequences the BUILD by the overlap map. The added sentence: **each part is reviewed on its own commits before the next part starts**, the scope script selects the part by key, and the enforcement suite at each part's close and at the tip is the integration check across parts — no lens is. `/smh-plan-task` and `/smh-dev-task-tests` Step 1.5 warn when `declared_change_set.py parse` counts more than 40 paths for one part: split it at plan time, when splitting is free.

## Step 1.6 — subtasks

None proposed. Every piece below is the same lane class in the same repo and shares files (the SOP, the engine, the doors); by Rule 2 they are parts of one lane, not lanes. The parts below are the build-and-review order per D7.

## Parts, in order — each: RED first, then the edit, then GREEN, then one commit

### Part 1 — the doctrine (rows A, B) — `SCC-447 doctrine: …`

**RED:** `test_review_disposition.py` blocks A and B, every check with a counter-example the harness applies in memory and must reject (SCC-122 shape); run `--case A` and `--case B`, paste the red. `test_review_engine.py` step-02 checks and `test_lens_roster_contract.py` SCC-232/SCC-147/SCC-203 checks are updated **in the same commit** to pin the new text (their old pins go red on the edit, which is the proof they were live).

**Edits:**
- `.agents/rules/code-standards.md` §6.5: the three questions gain the gate above them — *"Is it REPRODUCED? A critical or important with no receipt does not exist."* — and "Fix what passes all three" becomes the D1 table: the agent fixes only a reproduced critical; a reproduced important is escalated with its receipt; suggestions and nitpicks are a count. §7: the FAIL row requires a reproduction receipt; a new paragraph states that CONCERNS ships on the operator's word, that the floor is computed on open rows at the stamp, and that a lane gets one review with pins-plus-suite as the retest. Twin: byte copy to `.claude/rules/`.
- `.agents/skills/code-review-engine/steps/step-01-review.md`: the assessor section keeps its ruling and adds the reproduction gate; the lens table becomes D6; the hunter contract and the auditor rubric gain the required `reproduce:` / `expected_wrong_output:` fields (a finding without them is dropped unread); `## The two levels`, `### lens_budget`, the Literal-Correctness section, the Blind Hunter drop rule (SCC-203) and the evidence-pack section are retired with a one-paragraph retirement note naming SCC-447 and the measurement; the lens-roster contract keeps its invariant, the dead-lens ladder, `review_runtime`, and skipped-by-mode (Acceptance under `no-spec`).
- `steps/step-02-verify.md`: becomes a pass-through — one paragraph: the wave is retired (SCC-447: 2 refutations in 18 reviews; reproduction in step 3 is the verification), findings travel to step 3 with `verification: none`, and the `notes` line records `verify wave: retired (SCC-447)`.
- `steps/step-03-triage.md`: §1 gains `reproduce` and `expected_wrong_output` fields; §4's `patch` bucket becomes `fix` (reproduced critical) and a new `escalate` bucket (reproduced important); the relevance gate is replaced by the reproduction gate for critical/important and the "count only" rule for suggestion/nitpick; §5's table reads OPEN rows at the stamp; the "fixed in this lane… full stop" sentence becomes "fixed or escalated in this thread, never a ticket" (the 2026-08-15 rulings against residue tickets stand unchanged).
- `steps/step-04-record.md`: the record boxes become `[Review][Fix]`, `[Review][Escalate]`, `[Review][Defer]`; `src=` keeps its three short names; the summary line becomes `findings: <f> fix · <e> escalate · <w> defer (<d> dropped — no reproduction · <r> recorded)`; `dispositions:` unchanged in shape.
- `SKILL.md`: the return block matches step-04; the description drops "verifies findings".
- `.claude/skills/code-review-engine/` — byte copy of the five files.
- `.agents/skills/INDEX.md` engine row: description updated.
- SOP: §③, §`/smh-code-review`, §11 and the engine paragraphs restated in present tense; one changelog row.

**Decision at approval (Ask First — a deletion):** `evidence_extract.py` and `test_evidence_extract.py` serve only the retired wave. Recommendation: delete both in this part (the change makes them dead; `karpathy-guidelines` §3). Keeping them means a script nothing calls. Your word decides.

### Part 2 — the scope script (row D) — `SCC-447 scope: …`

**RED:** `test_review_scope.py` against a temp git repo built in the test: (1) mirrors, generated launchers and records withheld, masters kept, bytes reported; (2) commits grouped by key, rider key wins over lane key; (3) a two-key range with no selector exits 2 naming both keys; (4) `--key` selects one part's files only; (5) `--range` selects explicit commits; (6) `--out` writes the patch and prints kept/withheld counts; (7) an empty selection exits 2, never a clean patch. Paste the red.

**Edits:** `.agents/scripts/review_scope.py` (new, stdlib, docstring carries the SCC-441 measurement); `.agents/scripts/INDEX.md` row; SOP §11 paragraph + changelog row.

### Part 3 — receipts and the roster gate (row D) — `SCC-447 gates: …`

**RED:** `test_repro_receipt.py`: writes the json with the true exit code and output tail; an existing id refuses without `--replace`; a dirty tree is recorded; no `--result` flag exists (argparse rejects it). `test_walkthrough_roster_dispositions.py` on synthetic walkthroughs dated after the new cutoff (`DISPOSITION_CUTOFF = 2026-09-12`): a fixed `nitpick` row refuses; a `fixed` row without `pin` refuses; a `fixed`/`escalated` critical/important whose `repro <id>` file is absent refuses and names the path; present → passes; PASS with an open critical refuses; PASS with an escalated important refuses (must be CONCERNS); two roster headers without the operator line refuse; with the line, pass; a re-stamp section with no roster reads the earlier roster and passes; a pre-cutoff walkthrough (SCC-441's own) is untouched. `test_task_preflight.py` gains one case: the FAIL refusal names "pins and the suite" and never "re-run the review".

**Edits:** `.agents/scripts/repro_receipt.py` (new); `.agents/scripts/walkthrough_roster.py` — a findings-table parser (header row must carry a `sev`/`severity` and a `disposition` column; other columns free) and the refusals above inside `judge()`, the second-roster count in `parse()`, gated by a **literal** `DISPOSITION_CUTOFF = "2026-09-12"` (E4c: a computed cutoff exempts its own lane); `.agents/scripts/task_preflight.py:1618` one string; `.agents/scripts/workflow_lint.py:114-119` — ⚠️ AUDIT FINDING 2: the `("code-standards", "producing findings", …)` trigger regex keys on `applied / deferred / dismissed`; add the new vocabulary as a third alternation so a door written only in the new words still owes the §6.5 pointer (one case in the lint's test); `.agents/scripts/INDEX.md` row; SOP §10/§11 paragraphs + changelog row.

**Mutation sweep** (Step 3) over `review_scope.py`, `repro_receipt.py`, `walkthrough_roster.py`: table declared in `sweep.json` before mutating, mutants drawn from the code (drop a withheld prefix; invert the two-key refusal; write the receipt before running the command; drop the `pin` requirement; drop the open-critical floor; count rosters from the raw text instead of the stripped text), each naming the case that must kill it; run through `mutation_sweep.py`.

### Part 4 — the doors (row C) — `SCC-447 doors: …`

**RED:** `test_review_disposition.py` block C: both doors carry the D2 re-stamp block, the D3 message contract, the scope-script call in Step 1, "machine floor only" in the nested Step 3.5, the D1 policy in the fix paragraph; no `lens_budget` row; no `twin-law: review-level` fence; no sentence matching `re-run the review|fresh review|fresh lens|invalidates the verdict`; the `.opencode/` copies byte-equal. `test_review_engine.py`'s "exactly ONE lens_budget row" checks are retired in the same commit.

**Edits:** `.agents/commands/smh-code-review.md` and `cicd-code-review.md`: Step 0.7 loses the level-derivation fence; Step 1's input table drops `lens_budget`, `DIFF` becomes the `review_scope.py` output (with the command shown), a `## Reproduce` sub-step follows the engine's return (run every critical/important's command through `repro_receipt.py`; drop the rest), the "Then fix in thread" paragraph becomes D1; Step 3.5 nested: "run the machine floor (Step 1 of the audit door) only — the judgment pass is not run inside a review"; Step 4: the findings table header is fixed to `| # | file:line | sev | lens | failure scenario | disposition |`, the disposition vocabulary from D1, the re-stamp block D2, the end-of-review message D3, the verdict rules (FAIL = an open reproduced critical or a red machine floor; CONCERNS = an open reproduced important or a dead lens; PASS = nothing open), and "any code/test diff between that sha and HEAD invalidates the **suite evidence** — re-run the pins and the suite and re-stamp; never the lenses". `smh-clean-code-audit.md` and `cicd-clean-code-audit.md`: one line under Step 2 — "nested inside a review, this pass does not run (SCC-447)". `smh-close-task-merge-tree.md` §2 tail: the severity-triage sentence narrowed to the D1 policy. All five `.opencode/` mirrors byte-copied. SOP §③ and §`/smh-code-review` rewritten in present tense; changelog row.

### Part 5 — consolidation, planner, autopilot (rows E, F) — `SCC-447 lanes: …`

**RED:** `test_review_disposition.py` blocks E and F: the autopilot's step-3 row for CONCERNS/FAIL contains `escalate` and neither `fix child` nor `fresh`; `never ships by itself` absent from the door, `autopilot_SOP.md` and the SOP §15 row; Rule 2 carries "reviewed on its own commits" and "the enforcement suite is the integration check"; `smh-plan-task.md` and `smh-dev-task-tests.md` Step 1.5 carry the 40-path warning.

**Edits:** `.agents/commands/cicd-autopilot-claude.md:122` row → "**escalate** — post the D3 message on the ticket via `needs_human`; no fix child, no second reviewer; the operator's word moves it" (⚠️ AUDIT FINDING 1: `platforms: [claude]` — no `.opencode/` mirror exists for this door, so none is touched); `docs/_scc_sops_prds/autopilot_SOP.md:192` and the SOP §15 table row to match; `.agents/rules/work-consolidation.md` Rule 2 (D7 sentences); `.agents/commands/smh-plan-task.md` Step 2.5 and `smh-dev-task-tests.md` Step 1.5 (the size warning); the `.opencode/` mirrors of those two; changelog row.

### Part 6 — the gate at the tip (row G) — `SCC-447 records: …`

`workflow_lint.py --toolkit-only` (0 errors); `check_links.py --base origin/main`; `check_maps.py --depth3-only --strict`; `sop_currency.py` on the changed set; then **one** full `run_all.py` through `gate_receipt.py run --task SCC-447 --gate suite`, on a clean tree; the walkthrough with RED→GREEN evidence per row, the sweep record, `## Your Actions`; the Dev Record via `jira_feed.py devrecord`. Then STOP: `/smh-code-review` runs when you ask, under the doors this lane just changed.

## Declared Change Set

- NEW `.agents/scripts/review_scope.py` — the diff a lens reads: one part, masters only, no cap → D
- NEW `.agents/scripts/repro_receipt.py` — a reproduction is a receipt → D
- NEW `.agents/scripts/tests/test_review_disposition.py` — the prose pins with counter-examples → A
- NEW `.agents/scripts/tests/test_review_scope.py` — the scope script seen red → D
- NEW `.agents/scripts/tests/test_repro_receipt.py` — the receipt writer seen red → D
- NEW `.agents/scripts/tests/test_walkthrough_roster_dispositions.py` — the new refusals seen red → D
- EDIT `.agents/rules/code-standards.md` — §6.5 reproduce-or-drop + the action policy; §7 CONCERNS ships, floor on open rows, one review → A
- EDIT `.claude/rules/code-standards.md` — byte twin → A
- EDIT `.agents/skills/code-review-engine/SKILL.md` — return block and description → B
- EDIT `.agents/skills/code-review-engine/steps/step-01-review.md` — three lenses, reproduction fields, retirements → B
- EDIT `.agents/skills/code-review-engine/steps/step-02-verify.md` — pass-through → B
- EDIT `.agents/skills/code-review-engine/steps/step-03-triage.md` — action policy, floor on open rows → B
- EDIT `.agents/skills/code-review-engine/steps/step-04-record.md` — record vocabulary → B
- EDIT `.claude/skills/code-review-engine/SKILL.md` — cache copy → B
- EDIT `.claude/skills/code-review-engine/steps/step-01-review.md` — cache copy → B
- EDIT `.claude/skills/code-review-engine/steps/step-02-verify.md` — cache copy → B
- EDIT `.claude/skills/code-review-engine/steps/step-03-triage.md` — cache copy → B
- EDIT `.claude/skills/code-review-engine/steps/step-04-record.md` — cache copy → B
- EDIT `.agents/skills/INDEX.md` — engine row description → B
- EDIT `.agents/scripts/tests/test_review_engine.py` — step-02 and lens_budget pins retired, new pins → B
- EDIT `.agents/scripts/tests/test_lens_roster_contract.py` — SCC-232/147/203 pins retired, roster pins → B
- DELETE `.agents/scripts/evidence_extract.py` — served only the retired wave (your word at approval) → B
- DELETE `.agents/scripts/tests/test_evidence_extract.py` — its test (your word at approval) → B
- EDIT `.agents/commands/smh-code-review.md` — scope, reproduce, policy, re-stamp, message, verdict rules → C
- EDIT `.opencode/commands/smh-code-review.md` — byte mirror → C
- EDIT `.agents/commands/cicd-code-review.md` — the same, story-lane twin → C
- EDIT `.opencode/commands/cicd-code-review.md` — byte mirror → C
- EDIT `.agents/commands/smh-clean-code-audit.md` — nested: machine floor only → C
- EDIT `.opencode/commands/smh-clean-code-audit.md` — byte mirror → C
- EDIT `.agents/commands/cicd-clean-code-audit.md` — nested: machine floor only → C
- EDIT `.opencode/commands/cicd-clean-code-audit.md` — byte mirror → C
- EDIT `.agents/commands/smh-close-task-merge-tree.md` — §2 tail narrowed to the policy → C
- EDIT `.opencode/commands/smh-close-task-merge-tree.md` — byte mirror → C
- EDIT `.agents/scripts/walkthrough_roster.py` — findings-table parser and the five refusals → D
- EDIT `.agents/scripts/task_preflight.py` — the FAIL message string → D
- EDIT `.agents/scripts/tests/test_task_preflight.py` — one case for the message → D
- EDIT `.agents/scripts/INDEX.md` — two script rows → D
- EDIT `.agents/commands/cicd-autopilot-claude.md` — step-3 row: escalate (⚠️ AUDIT FINDING 1: `platforms: [claude]`, so it has NO `.opencode/` mirror — none declared) → E
- EDIT `docs/_scc_sops_prds/autopilot_SOP.md` — the matching row → E
- EDIT `.agents/scripts/workflow_lint.py` — ⚠️ AUDIT FINDING 2: the `code-standards` finding-producer trigger learns the new disposition vocabulary (`fixed` / `escalated` / `dropped` / `recorded`) beside the old, with one lint case → C
- EDIT `.agents/rules/work-consolidation.md` — Rule 2: review per part, suite is the integration check → F
- EDIT `.agents/commands/smh-plan-task.md` — plan-time size warning → F
- EDIT `.opencode/commands/smh-plan-task.md` — byte mirror → F
- EDIT `.agents/commands/smh-dev-task-tests.md` — Step 1.5 size warning → F
- EDIT `.opencode/commands/smh-dev-task-tests.md` — byte mirror → F
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — §③, §`/smh-code-review`, §10, §11, §15 in present tense → G
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one row per part → G
- EDIT `docs/_scc_sops_prds/operator_workflows_quickref.md` — the extractor mention, if the deletion is approved → G

Launcher skills (`.agents/skills/<cmd>/SKILL.md`, `.roo/commands/`) carry only each command's description, which this lane does not change, so they are not regenerated. `sync-agents.ps1` is available (`pwsh` is installed) if a description does move.

## Risks, named

- **A new gate refuses once before it settles.** Every roster-parser tier in this house produced one false refusal on its first lane (SCC-210: two round trips). The disposition vocabulary is five words, pinned by tests, and every refusal names the row and the fix. Expect one bump on the first review under it.
- **Reproduction moves work into the assessor.** Each critical/important costs one command through the receipt writer. On a three-lens review of a part-sized diff that is a handful; it replaces a whole verifier wave. On a bad diff it is the slowest step, and it is the step that should be.
- **Coverage lost, stated:** one of seven historical criticals was Blind-only, one Literal-only; the fence checker SCC-441 added covers the Literal class. Findings that are true but cannot be shown as wrong output are dropped by design.
- **Per-part review has a seam.** Part N's review does not see part N-1's files. The suite at each part's close and at the tip is the integration check; D7 says so in the rule so nobody adds a lens for it.
- **The prose pins are one test file.** `test_review_disposition.py` guards the doctrine; the roster parser guards the behaviour. Both, deliberately.

## Not in this lane

The phase-2 fork (lenses forked from a review parent that loaded only the diff — measured 92% saving in the SCC-430 spike; own ticket, measured first on the SCC-124 fixture). The three SCC-441 findings escalated in that lane's pass-3 note (own ticket). The labeller's SOP shared-ground rule (untouched). The two stale worktree stubs (a sandbox-off prune, one line).

## Self-Audit (2026-09-11)

**Level:** LEDGER+BLAST — the declared set touches rules, gate scripts, doors on every platform, the tests directory, and carries two `DELETE` rows. **Mode:** PRE-WORK. **Runtime:** the three lenses were run inline by the assessor with real commands (outputs quoted below); they were not fanned out.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  declared block parses · every declared path exists in the state its op requires · every section/line anchor the plan names exists · commands run on both sides · lane fit (no deployable path) · Scope Ledger (NEW × acceptance row)
read:        declared_change_set.py parse → entries=48 incomplete=[] ops={NEW:6, EDIT:40, DELETE:2}
             audit_paths.py → mismatches: [('EDIT but missing', '.opencode/commands/cicd-autopilot-claude.md')]
             .agents/commands/cicd-autopilot-claude.md:3 → `platforms: [claude]`; ls .opencode/commands | grep -c autopilot → 0
             workflows_testing_SOP.md → `## 10. The safety net` :2391 · `## 11. Is this review still valid?` :2608 · `## 15. The autopilot lane` :2924
             smh-plan-task.md → `## Step 2.5 — ⭐ Pick the MODE` :117 · task_preflight.py:1618 → `"the review verdict is FAIL - fix on the branch and re-run the "` · cicd-autopilot-claude.md:122 · autopilot_SOP.md:192
             twin-law fences: smh-code-review.md:120 `review-level` · cicd-code-review.md:181 `review-level`
             Scope Ledger — NEW × row: review_scope.py→D · repro_receipt.py→D · test_review_disposition.py→A(+B,C,E,F) · test_review_scope.py→D · test_repro_receipt.py→D · test_walkthrough_roster_dispositions.py→D — no empty cell. Caller count: review_scope.py 0 existing callers, 2 planned (both doors); repro_receipt.py 0 existing, 2 doors + walkthrough_roster reads its files.
verdict:     findings below (1)
```

```
lens:        2 Parity + Blast
checks_run:  command files → platform doors · rule → citing commands + workflow_lint _RULE_POINTERS · scripts → callers in hooks + tests + INDEX · gate/hook arming · DELETE → every reference repo-wide · SOP same commit · twins · file in >1 repo (port rule) · sibling worktrees · risk seam
read:        workflow_lint.py:114-119 → `("code-standards", "producing findings", re.compile(r"`?applied`?\s*/\s*`?deferred`?\s*/\s*`?dismissed`?" | r"^\s*-\s*\*\*FAIL\*\*\s*[-—–=:]" …))`
             roster.judge( callers → closeout_preflight.py:413, task_preflight.py:1579 (signature unchanged; new refusals behind a literal cutoff)
             hooks naming changed scripts → git-hooks/merge-target-guard.sh:163 (a comment only)
             evidence_extract references → step-02 (rewritten) · scripts/INDEX.md (row) · operator_workflows_quickref.md · changelog (history, kept) · test_review_engine.py:605-608 (check retired with step-02) · test_command_surfaces.py:3932 (comment)
             test_twin_parity.py:189 → FENCED_TODAY comment names `review-level` (a comment; the check compares law maps, so removing the fence from BOTH doors keeps parity)
             test_lens_roster_contract.py:142 → QUICK_TOKEN = "≤3 source files"; SOP:660-662 restates it (retired together, Part 1 + Part 6)
             Projects/*/ → only `Projects/sudo-command-center/` carries the rule, the engine and the door; .gitmodules → a submodule of `sudomadhatter/sudo-command-center.git`, `ignore = all`; docs/workspace-standard.md:260 → "the published teaching edition of this lobby — a sanitized export, never edited in place" (export-teaching-edition.ps1); its copies already differ from the lobby's. NOT in SCOPE → the port rule does not fire.
             git worktree list → SCC-439 stub (not a git repository), scc-386 stub on main, no diff → no landing-order dependency
             risk_seam.py classify → {"status": "unclassified"} (markdown repo, SCC-289 — correct)
             workflow_lint.py --toolkit-only on the untouched tree → 0 error(s), 0 warning(s), 8 info
verdict:     findings below (1)
```

```
lens:        3 Pre-Mortem (attached to anchored findings only)
checks_run:  the silent one · the fresh-clone one · the sibling-lands-first one · the own-lane-exempt one
read:        F1 shipped as declared → /smh-code-review Step 2's declared-set drift reports `unimplemented=1` on every review of this lane for a file that cannot exist, capping at CONCERNS forever.
             F2 shipped without → the next lane that rewrites a clean-code door in the new vocabulary loses the §6.5 pointer requirement silently — a check that cannot fail (tests-must-gate-for-real §5). The review doors still fire through the `- **FAIL**` arm.
             cutoff (design, not a finding) → a computed "today" cutoff would exempt this lane's own walkthrough (E4c scar); the plan pins the literal `2026-09-12` and the test asserts the literal.
             fresh clone → the two new scripts are stdlib; the new refusals ride a script the close-out already runs, so nothing needs arming.
verdict:     clean — nothing to originate; two narratives attached above
```

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/commands/cicd-autopilot-claude.md:3` | `platforms: [claude]` | the declared `.opencode/commands/cicd-autopilot-claude.md` cannot exist; every review of this lane reports one unimplemented declared path | medium — **baked in: entry removed** |
| `.agents/scripts/workflow_lint.py:114-119` | `("code-standards", "producing findings", re.compile(r"`?applied`?\s*/\s*`?deferred`?\s*/\s*`?dismissed`?" …` | the finding-producer trigger keys on the vocabulary this plan replaces; a door carrying only the new words would lose the §6.5 pointer requirement silently | medium — **baked in: Part 3 adds the alternation + one case** |

### Observations (uncounted)

- `test_twin_parity.py:189`'s FENCED_TODAY comment names `review-level`; update the comment when the fence goes (cosmetic, a comment is not law).
- The `lenses_na` machinery in `walkthrough_roster.py` stays: the Acceptance Auditor is still `n/a` under `review_mode: no-spec`, and `test_walkthrough_roster.py`'s NA fixtures use `blind-hunter` as a lens name, which the parser never validates — they keep passing.
- `Projects/sudo-command-center/` will pick these files up on its next export, not by port.

**Sibling landing-order dependency:** none.

Audit verdict: GO
