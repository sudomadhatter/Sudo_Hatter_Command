---
IsArtifact: true
ArtifactMetadata:
  title: SCC-128 rewire callers + retire the bmad-code-review surface
  type: implementation_plan
  date: 2026-08-13
---

# SCC-128 — Rewire callers + retire the `bmad-code-review` surface

**Lane:** `chore/SCC-128-rewire-callers` in `.claude/worktrees/scc-128-rewire-callers`, off `main` @ `36e1ffe`.
**Parent spec:** `_artifacts/_main/2026-08-12_scc-116-house-review-engine/implementation_plan.md` (SCC-128 section).
The engine (`.agents/skills/code-review-engine/`) is already on `main`; this lane points the callers at it and
retires the vendor surface behind an armed lint.

**Scope transfer honored:** `.agents/commands/cicd-code-review-AP.md` is **not touched** — its rewire moved
to SCC-126 (operator-approved, in the ticket). Consequence handled in §Landing order.

## Acceptance list (each item = a checkable assertion)

| # | Item | Proving assertion |
|---|---|---|
| A1 | `cicd-code-review.md` Step 1 invokes `code-review-engine` with the full caller contract | inspection of Step 1 supplies `REPO·WORKTREE·DIFF·HEAD_SHA·review_mode·STORY_FILE`; `grep bmad-code-review` on the file = 0 hits |
| A2 | `smh-code-review.md` Step 1 invokes the engine (task lane gains the lenses) | same greps on that file; contract supplies the task plan as acceptance source |
| A3 | `.agents/rules/bmad_code_review_sudo_fix.md` deleted; its `rules/INDEX.md` row gone | file absent on disk; `grep bmad_code_review .agents/rules/INDEX.md` = 0 |
| A4 | `.agents/opencode-agents/opus-reviewer.md` rewritten — doctrine sourced from the engine, no reference to the retired rule or vendor skill | `grep -E "bmad[-_]code[-_]review"` on the file = 0; output contract to the autopilot (story-file sections) unchanged |
| A5 | INDEX + SOP current in the SAME commit as the usage change (no `[sop-ok]`) | `sop_currency.py` passes with the SOP staged; `skills/INDEX.md`, `workflows/INDEX.md`, `rules/INDEX.md` rows updated; SOP ③ diagram names the engine |
| A6 | **Resurrection lint armed**: no command/rule may reference `bmad-code-review`/`bmad_code_review` | `workflow_lint.py --toolkit-only` ERRORs on a seeded fixture (RED proven first) and stays quiet on a clean one; live tree scan wired into the lobby check path |
| A7 | AP file untouched | `git diff --name-only main...HEAD` does not list `cicd-code-review-AP.md` |
| A8 | Floor green | `run_all.py` all files pass; `workflow_lint --toolkit-only` — zero errors **except** the ticketed AP hit while SCC-126 is unlanded (§Landing order) |

## Steps (each maps to an acceptance item)

1. **RED first (A6):** extend `.agents/scripts/tests/test_workflow_lint.py` with resurrection-lint cases —
   seeded `commands/bad.md` + `rules/bad.md` fixtures must produce `ERROR`, a clean file none. Run → fails
   (the check doesn't exist yet). Then add `check_retired_surfaces()` to `workflow_lint.py` scanning
   `.agents/commands/*.md` + `.agents/rules/*.md` for `bmad[-_]code[-_]review` → ERROR, wired into the lobby
   block of `main()` (runs under `--toolkit-only`). Test goes GREEN; live scan now reds on every stale
   reference — the rest of the lane turns those off one by one, AP excepted.
2. **Rewire `cicd-code-review.md` Step 1 (A1):** replace the vendor-skill invocation with the engine —
   caller resolves `REPO` (=`PROJECT_ROOT`), `WORKTREE` (Step 0.5's tree), `DIFF` (story diff), `HEAD_SHA`,
   `review_mode` (`full` when a story file exists, else `no-spec`), `STORY_FILE`, `ARTIFACT_DIR`,
   `DEFERRED_WORK`; `EVIDENCE_PACK` stays absent (normal today per the engine contract). The engine's
   returned `severity_floor` binds Step 4 (may report more severe, never less). The inline subagent-failure
   contract compresses to a pointer — the engine owns per-lens retry/inline/dead semantics now; the caller
   keeps applying fixes + scoped re-runs. Clean-room ordering note stays (it is the caller's framing).
3. **Rewire `smh-code-review.md` Step 1 (A2):** replace `bmad-review-adversarial-general` with the engine —
   `review_mode: full` with the task's `implementation_plan.md` acceptance list as `STORY_FILE` when present,
   else `no-spec`; task lane thereby gains Edge-Case + Test-Adequacy (+ Acceptance) lenses. Step 2's
   acceptance matrix stays the command's own.
4. **Retire the adapter rule (A3):** delete `bmad_code_review_sudo_fix.md`; drop its `rules/INDEX.md` row.
5. **Sweep the remaining in-scope references (A6 turns green):**
   `cicd-self-audit.md` ("shipped code → …" now points at the review commands / engine) ·
   `artifacts-always-first.md` §6 enumeration ·
   `skills/INDEX.md` BMAD-lifecycle row (drop the entry; the engine is already in the Code-quality row) ·
   `workflows/INDEX.md` cicd-self-audit row (hand-owned file).
6. **Rewrite `opus-reviewer.md` (A4):** doctrine source becomes the engine (`SKILL.md` + `steps/step-01`) run
   solo-sequential — the three FP gates, severity rubric, and pass order come from the engine's lens specs;
   its autopilot interface (story-file sections, artifact mirror, no status flip) is unchanged.
7. **SOP + regenerate (A5):** update `workflows_testing_SOP.md` ③ diagram; run `sync-agents.ps1`
   (`-WhatIf` first, then real) so the generated mirrors/launchers follow the edited commands; commit
   explicit paths only. Rebuild the doc graph (the deleted rule stales `docs/doc-graph.json`) and verify
   `check_maps.py --depth3-only --strict`.
8. **Gate:** `run_all.py` + `workflow_lint --toolkit-only` + re-run of the Step-2 RED cases GREEN →
   `/smh-code-review`.

## Landing order (the one open dependency — ticketed, operator's call at close-out)

The armed lint scans ALL commands, and `cicd-code-review-AP.md` still references `bmad-code-review` — a file
this lane may not edit. Until SCC-126 lands its AP rewire on `main`, this lane's `workflow_lint` shows
errors **on that file only**. The lint's red-capability is proven independently by the seeded-fixture
test (A6), so the check is real either way.

**⚠️ AUDIT FINDING (upgrades this from cosmetic to behavioral):** `cicd-code-review-AP.md:21,36` references
the retired rule **by path** (`.agents/rules/bmad_code_review_sudo_fix.md`). If this lane merges before
SCC-126, the AP autopilot QA lane instructs its agent to read a **deleted file** — a live behavioral break,
the exact "reference a landed lane moved" FAIL class from `/smh-code-review` Step 0.7. Therefore the
preferred order is firm: **SCC-126 lands first**, this lane absorbs `main` (review Step 0.7), lint goes
fully green, then merge. Merging this lane first is the operator's explicit call to make at close-out, with
that break named. No other file overlap with SCC-126/127 exists (their trees touch `test_review_engine.py` +
engine step files + the AP command; this lane touches none of those).

## Boundaries

- `cicd-code-review-AP.md`, `test_review_engine.py`, `.agents/skills/code-review-engine/steps/*` — sibling
  lanes' surfaces, untouched here.
- `_bmad/`-installed + `.agents/bmad/` vendor files untouched; the vendor skill's `.claude/skills/` copy is
  left for the regenerator (lint scope is commands + rules only, deliberately).
- `docs/` guides outside the SOP: `tea_deep_reference.md`'s ③ lines are updated (they document this exact
  command's chain and would become factually wrong); `tea_testing_guide.md` + `tdad_stack_install_guide.md`
  are left as-is (closed-initiative/history, out of lint scope) — called out so the choice is visible.
- No engine behavior changes; no noise filter added anywhere (SCC-116 boundary).
- `_artifacts/_memory/story-status-flip-contract.md` names the retired rule as "the sanctioned override" —
  the store is READ-ONLY outside its flows, so this lane does not touch it; flagged as a follow-on for the
  sanctioned memory flow (the fact goes stale the moment this lands).

## Self-Audit (2026-08-13)

**Right-size: Full** — deletes a rule, arms a lint, edits four platform-surfaced commands and a hand-owned
INDEX; multiple platform caches move.

**Phase 0 — traceability:** every acceptance item A1–A8 maps to a numbered step and back; no unowned step.
Lane check clear — no deployable path in the change set (toolkit + docs only).

**Phase 1 — blast radius (traced against the live tree, sibling worktrees read):**
- Full-tree sweep of `bmad[-_]code[-_]review`: in-scope hits enumerated in steps 2–6; remaining hits are
  vendor manifests (`.agents/bmad/**` — never hand-edited), historical `_artifacts/**` (out of lint scope,
  left as history), generated mirrors (`.opencode/**`, `.agents/workflows/**` — regenerated by sync, step 7),
  `docs/doc-graph.json` (cache — rebuilt, step 7), and the AP command (SCC-126's, see §Landing order).
- Retired-rule pointer sweep: `opus-reviewer.md` (master + synced copy), `rules/INDEX.md`, and
  **`cicd-code-review-AP.md:21,36` — the AUDIT FINDING above**; `workflow_lint.py::_RULE_POINTERS` does not
  name the rule (clear).
- Doors: all four doors exist for `cicd-code-review`, `smh-code-review`, `cicd-self-audit`; body edits reach
  them via the sync run in step 7, which also refreshes `.opencode/agent/opus-reviewer.md`.
- Sibling lanes: SCC-126 holds uncommitted `test_review_engine.py` + its artifacts; SCC-127 clean. Zero file
  overlap with this lane's change set. Possible trivial adjacent-line merge on SOP/INDEX files if siblings
  also update them — absorbed at review Step 0.7, named here so it reads as expected.

**Phase 2 — over-engineering:** no new command, rule, script, or flag; lint is one function + test cases in
existing files; callers shrink (inline failure-contract prose compresses to the engine pointer). No tripwire
fires.

**Phase 3 — pre-mortem:** both-machines ✅ (Python changes run under `run_all.py`, already cross-machine);
fresh clone ✅ (lint lives in `workflow_lint --toolkit-only`, not in a hook — armed wherever the gate runs);
fires-on-someone-else ✅ (error text names the remedy: point at `code-review-engine`, cite SCC-128);
escape hatch — deliberately none inside commands/rules (that is the resurrection guard's job; docs, commit
messages and history stay free; the auditable exit is editing the lint under its own ticket); empty-input ✅
(seeded fixture proves the check fires; a check that cannot fail would fail A6's RED half); four caches ✅
(step 7 sync); sibling-lands-first ✅ (either order merges cleanly; behavioral order named); rollback ✅
(pure git revert — the deleted rule is one `git checkout` away; the only Jira transition already happened at
Step 0.5). **Surviving failure mode, named:** this lane landing before SCC-126 breaks the AP QA lane's rule
pointer — carried as the explicit landing-order ruling, not silently.

| Finding | Severity | Failure scenario | Disposition |
|---|---|---|---|
| `cicd-code-review-AP.md:21,36` points at the rule this lane deletes | important | lane merges before SCC-126 → AP autopilot reads a deleted rule | landing order pinned: SCC-126 first; operator rules otherwise at close-out |
| `_artifacts/_memory/story-status-flip-contract.md` will go stale | suggestion | future reader told the retired rule is the sanctioned override | follow-on for the sanctioned memory flow; store untouched here |

**Four gates:** verification strategy present per item (A-table) ✅ · irreversible: the rule delete is
git-recoverable; no history rewrite, no ticket transition beyond the Step 0.5 start ✅ · vague steps: none —
each names its file and its assertion ✅ · convention fit: naming law untouched, door model via sync,
artifacts in `_artifacts/_main/`, extend-don't-fork for tests ✅.

Audit verdict: GO
