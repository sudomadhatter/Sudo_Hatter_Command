---
IsArtifact: true
ArtifactMetadata:
  title: SCC-122 engine scaffold - .agents/skills/code-review-engine
  type: implementation_plan
  date: 2026-08-12
---

# SCC-122 — Engine scaffold: `.agents/skills/code-review-engine/`

Lane: `chore/SCC-122-engine-scaffold` · parent SCC-116 · epic spec:
`_artifacts/_main/2026-08-12_scc-116-house-review-engine/implementation_plan.md` (§SCC-122).
This plan is lane-scoped; the epic plan is the architecture authority and is NOT restated here.

## Goal

The house review engine EXISTS and is runnable: a hand-authored skill with 4 step files that
carries the vendor's proven mechanics (fan-out shape, 4-bucket triage) and the two new rulings
(severity→verdict mapping, NA-vs-died), and carries NONE of the vendor's three law conflicts.
Nothing is rewired — `cicd-code-review`/`smh-code-review` still invoke the vendor skill until
SCC-128. This subtask only has to make SCC-124's head-to-head trial possible.

## Acceptance (each checkable by a command; the RED test asserts all of them)

1. **Structure exists:** `.agents/skills/code-review-engine/SKILL.md` +
   `steps/step-01-review.md`, `steps/step-02-verify.md`, `steps/step-03-triage.md`,
   `steps/step-04-record.md`.
2. **Caller contract stated in SKILL.md:** `REPO` · `WORKTREE` · `DIFF` · `STORY_FILE` (optional)
   · `HEAD_SHA` · `review_mode` (`full` | `no-spec`) — and the sentence that the engine never
   resolves these itself.
3. **step-01 = the ported fan-out:** all four current lenses (Blind Hunter diff-only · Edge Case
   Hunter · Acceptance Auditor, full-mode only · Test-Adequacy Auditor), the callers'
   subagent-failure contract verbatim (retry once → rerun inline → record the degradation →
   a lens that never ran caps at CONCERNS), and the NA-vs-died rule: Acceptance lens skipped under
   `no-spec` records `n/a (mode)` and does NOT cap the verdict.
4. **step-03 = triage + severity machinery:** the 4 buckets verbatim
   (`decision_needed`/`patch`/`defer`/`dismiss`, incl. the no-spec reclassification rule), the
   severity alias normalization map (critical←high,blocker · important←medium,major ·
   suggestion←minor,low + unrecognized-fallback · nitpick←info,trivia,trivial), and the
   severity→verdict table defined ONCE: confirmed critical→FAIL · important→CONCERNS floor ·
   suggestion/nitpick never gate · verifier-revised severity wins over hunter-asserted.
5. **step-04 records and nothing else:** findings→walkthrough/story block + deferred-work routing
   (the ~20 portable lines of vendor step-04 §2), and ZERO matches for any of: story status flip,
   `sprint-status.yaml` sync, `HALT`, `resolve_customization.py`, `{communication_language}`.
   (These negative controls are the whole reason SCC-116 exists — they go in the test.)
6. **Registered + cache parity:** `.agents/skills/INDEX.md` routes to the engine (Code quality
   gates family); `.claude/skills/code-review-engine/` exists and is byte-identical to master
   (`diff -r` clean). Gates: `run_all.py` all files exit 0 (new `test_review_engine.py` red-first
   then green) · `workflow_lint.py --toolkit-only` exit 0.

## Design decisions (settled here so the audit can attack them)

- **step-02-verify at scaffold time = honest pass-through.** The self-gating contract is real
  (0 findings → no wave; <2 → no compound) but until SCC-127 lands the roles, findings pass
  through UNVERIFIED and the step says so in its output contract. A runnable engine now beats a
  fictional verifier; SCC-124's trial needs to run this file as it will actually behave.
- **Lens invocation stays as today:** Blind Hunter via `bmad-review-adversarial-general`, Edge
  Case Hunter via `bmad-review-edge-case-hunter` — these are persona skills without law
  conflicts, and `smh-code-review` already calls the first directly. SCC-125 decides whether the
  pr-af prompt transplant inlines them. The resurrection lint (SCC-128) bans `bmad-code-review`
  only.
- **Evidence pack is an OPTIONAL step-01 input** (absent → lenses run as today). The extractor
  arrives at SCC-123; the scaffold must not depend on a script that does not exist.
- **Sync in a worktree:** author the master, then `pwsh .agents/scripts/sync-agents.ps1
  -NoGlobals` so the repo-local `.claude/skills/` tree-copy updates WITHOUT touching
  machine-global caches (`~/.codex` etc.) from an unlanded lane. Cache copy is committed (it is
  git-tracked — 1086 files under `.claude/skills/` today). If `-NoGlobals` misbehaves inside a
  worktree, fall back to a hand tree-copy and record it in the walkthrough.
- **The epic plan file rides THIS lane.** It sits uncommitted on main's working tree; this lane
  commits it at its canonical path as the spec evidence. After the lane commit, the untracked
  copy on main's tree is removed (byte-identity verified first) so the eventual merge never hits
  the untracked-file collision. The SCC-38 plan folder + `proposal_graphrag_executiblity.md`
  stay on main's tree untouched — they belong to future lanes.
- **SOP gate:** whole diff is exempt by design (`.agents/skills/` not a surface;
  `.agents/scripts/tests/` + `INDEX.md` explicitly exempt in `sop_currency.py`). No SOP edit, no
  `[sop-ok]` — nothing an operator types changes until SCC-128.

## Steps

| # | Step | Proves acceptance |
|---|---|---|
| 1 | RED: write `.agents/scripts/tests/test_review_engine.py` asserting items 1–6 (incl. the five negative controls as `assertNotIn`-style checks); run it, paste the failure, confirm it fails in the ASSERTION not in setup | the assertions exist and can fail |
| 2 | Author `SKILL.md` + 4 step files in the worktree master | 1, 2, 3, 4, 5 |
| 3 | Add the INDEX family-row entry; run sync `-NoGlobals`; `diff -r` master vs cache | 6 |
| 4 | GREEN: re-run the test, then full `run_all.py` + `workflow_lint.py --toolkit-only` | 6 |
| 5 | Commit (explicit paths: skill dir, cache dir, test, INDEX rows, epic plan file, lane artifacts); remove main's now-committed untracked epic-plan copy | landing hygiene |
| 6 | `/smh-code-review` → walkthrough + `task.yaml` + Dev Record | the lane's own gate |

⚠️ **AUDIT FINDINGS baked into the test design (2026-08-12 self-audit):**
- **Existence before negatives.** Every negative control (no `HALT`, no `sprint-status.yaml`, …)
  asserts the target file EXISTS and is non-empty FIRST — a grep-zero on a missing file is a
  vacuous green, the exact failure `e2e-gate-fiction` already taught us.
- **Source-greps count prose.** The authored step files must not MENTION the banned tokens in
  comments or narration (a comment saying "unlike the vendor's HALT" trips the control — correct
  behavior, so write around it). Test vocabulary is pinned to this plan's §Acceptance wording.
- **INDEX cache parity too.** Acceptance 6's parity check covers BOTH the engine dir AND
  `skills/INDEX.md` master↔cache — workflow_lint has ZERO skill checks (verified), so this test
  is the only mechanical guard on the whole surface.

## Boundaries

- No rewiring of any caller; no retirement of the fix rule (SCC-128). No evidence extractor
  (SCC-123). No pr-af prompt text beyond the severity/alias/mapping tables (SCC-125). No 5th
  lens (SCC-126). No verifier/compound prompts (SCC-127).
- Vendor skill files are never touched — `.claude/skills/bmad-code-review/` stays as the
  regenerator left it.
- Surgical diff: skill dir + cache dir + one test file + one INDEX row (both trees) +
  `.agents/.sync-manifest.json` (written by the sync the INDEX row requires; hand-editing it is
  banned) + the two artifact folders. Anything else is drift.

## Self-Audit (2026-08-12)

Mode: PRE-WORK · Right-size: **Full** (new multi-platform surface: skills master + committed
Claude cache; test-suite addition; naming-law territory). Repo pinned from command output:
`scc-122-engine-scaffold | chore/SCC-122-engine-scaffold`.

- **Phase 0** — change set named (5 adds + 1 INDEX row edit + lane artifacts); checkable list =
  the 6 §Acceptance items (authority: ticket description + epic plan §SCC-122); traceability
  clean both directions (step 5 is landing mechanics, not scope); lane check: no deployable
  paths — smh lane correct.
- **Phase 1** — blast radius walked with greps: `code-review-engine` name is virgin (only the
  research doc + these plans reference it); no dir collision in either skills tree; no test-name
  collision; `workflow_lint.py` has NO skill checks (so the new test is the only mechanical
  guard — noted inline); run_all auto-discovers `test_*.py` (no registration file to entangle);
  vendor skill + fix rule untouched until SCC-128; siblings: NONE live (worktree list = main +
  this lane). Landing-order note: the epic plan file is untracked on main's working tree — this
  lane commits it, then removes main's copy (byte-verified) so the merge cannot hit the
  untracked-file collision.
- **Phase 2** — over-engineering gate: new skill = the ticket itself; new test file follows the
  script→test convention and becomes the red-file future subtasks EXTEND (never fork);
  step-02 pass-through is the minimal honest runnable version (SCC-124 needs to trial the real
  behavior); porting vendor steps is deliberate documented duplication across ownership
  boundaries. No tripwire fires.
- **Phase 3** — pre-mortem: both machines (test is stdlib+pathlib; `python3`/`python` noted;
  pwsh exists both sides); no new gate/hook (fresh-clone + escape-hatch rows N/A); empty-input
  row FIRED → existence-before-negatives baked into the test design (finding F1); platform
  reach: skills self-route (Claude reads committed `.claude/skills/`, Codex reads
  `.agents/skills/` natively; no doors — not a command); rollback = revert the lane merge,
  nothing irreversible (jira start already idempotent; devrecord updates in place).

| Finding | Severity | Failure scenario | Disposition |
|---|---|---|---|
| F1 negative controls vacuous if target file missing | MEDIUM | step-04 never created → all five negative greps pass green | baked in: existence+non-empty asserted before any negative |
| F2 source-greps count comments | LOW | a step file narrating "the vendor's HALT" trips the control | baked in: authored files avoid banned tokens in prose; vocabulary pinned |
| F3 `sync -NoGlobals` unverified inside a worktree | LOW | cache copy lands wrong or half | fallback in plan: hand tree-copy + record in walkthrough |
| F4 INDEX cache drift invisible to the engine-dir diff | LOW | master INDEX row lands, cache INDEX stale | baked in: parity check covers `skills/INDEX.md` both trees |

Four quick gates: verification strategy present (every item → a named command in the test /
run_all / diff -r) · nothing irreversible · no step vague enough to guess (step-02 content
decision settled in §Design decisions) · convention fit anchored (naming law §SCC-63 no-prefix,
INDEX family map, artifacts-always-first).

Audit verdict: GO
