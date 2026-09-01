---
IsArtifact: true
ArtifactMetadata:
  title: "Implementation Plan — Story-Artifact Token Optimization (two-doc close)"
  type: implementation_plan
  date: 2026-08-02
---

# Implementation Plan — Story-Artifact Token Optimization

> Goal: a story ends with exactly TWO living documents — `implementation_plan.md` (plan + self-audit)
> and `walkthrough.md` (task outline + evidence + code review + your-actions) — with hard size budgets,
> machine-readable verdict lines, and every downstream reader re-pointed. Exemplar audited:
> story 8.23.2 (AGY).

## Audit — what one story writes today (8.23.2, bytes on disk)

| Artifact | Size | Written by |
|---|---|---|
| `implementation_plan.md` | 8.5 KB | ② Step 1 |
| `self-audit-stress-test.md` | 5.9 KB | ② Step 2 (mandated standalone by `artifacts-always-first` §7) |
| `walkthrough.md` | 13.2 KB | ② Step 5, re-edited by ③ Step 5 |
| `sudo-code-review-<story>.md` | 12.4 KB | ③ Step 4 (verdict file) |
| `automation-summary-<story>.md` | 2.3 KB | ② Step 4 |
| `atdd-checklist-<story>.md` | 6.4 KB | ① (TEA) |
| Story file (Dev Agent Record / File List / Review Findings) | 8.2 KB | BMAD-owned |
| **Total** | **~57 KB ≈ 14k tokens written** | + each doc re-read by ② audit, ③, and close-out |

**Duplication map (the actual waste — same fact written N times):**

1. **Review findings ×3** — verdict file (full table) + walkthrough (condensed copy of the same table) + story-file Review Findings.
2. **Test-output pastes ×6** — walkthrough carries 4 historical pastes (red, first green, expansion, post-review); verdict pastes again; automation-summary pastes again.
3. **AC traceability ×4** — plan task→AC map, audit AC↔plan trace, walkthrough AC→evidence matrix, verdict traceability section.
4. **File-by-file change list ×4** — plan, walkthrough table, verdict scope section, story File List.
5. **Self-audit findings ×2** — standalone file AND folded into the plan (the fold already happens; the standalone file is a near-pure duplicate).
6. **"What this delivers" prose ×3** — plan intro, walkthrough intro, story description.

## Target design

### Doc 1 — `implementation_plan.md` (pre-dev thinking, unchanged in role)
Keeps its current job: the reasoning artifact `/sudo-self-audit` attacks. Changes:
- `/sudo-self-audit` **appends `## Self-Audit (<date>)` INTO the plan** instead of writing
  `self-audit-stress-test.md`: right-size level, one line per phase cleared, findings table with
  dispositions, **`Audit verdict: GO|NO-GO`** canonical line. Inline `⚠️ AUDIT FINDING` flags in
  affected sections stay (the dev reads them in context).
- Blind-handoff lane: a pasted external audit is appended into this section (source noted), not copied
  as a standalone file. Skip lane: one line `Audit: skipped by human decision (<date>)`.
- **`self-audit-stress-test.md` is retired** for new stories.

### Doc 2 — `walkthrough.md` (the living build record — outline, not narrative)
Restructured around the TodoWrite task list, replacing narrative + separate checklist (they duplicated
each other):
1. **Header** — story link, status, branch + commit range.
2. **`## Task Outline`** — each executed task as a checklist line; under a task, ONLY indented bullets
   for pitfalls / findings / deviations met doing it ("went clean" tasks get no sub-bullets). This
   MERGES the old narrative + `## Task Checklist` into one section.
3. **`## Evidence`** — ONE AC→evidence matrix (the only copy anywhere) + ONE test block: the LATEST
   full-suite totals + `git rev-parse HEAD` (totals lines only, never reporter dumps). Re-runs
   **replace** the block — git keeps history. Static checks: one line.
4. **`## Code Review (<date>)`** — appended by ③, replacing the verdict file: canonical line
   **`Verdict: PASS|CONCERNS|FAIL|WAIVED @ <sha>`** (+ suite-evidence SHA), findings table
   (file:line · sev · finding · disposition), gate results one line each, clean-code findings folded in.
5. **`## Your Actions`** (LAST) — required-human items, also posted in chat. ③ attempts any
   agent-solvable item here and ticks it; only genuine human calls (product decisions, live checks,
   `main` promotion) survive.
6. Autopilot's `## Close-Out Handoff` block — unchanged (close-out Step 3 lifts it).

### TEA outputs — KEPT, out of scope (operator ruling 2026-08-02)
`automation-summary-<story>.md` and `atdd-checklist-<story>.md` stay standalone under
`_bmad-output/test-artifacts/`, unchanged. ② Step 4 and ③'s automate-evidence check are untouched;
the walkthrough links them in one line (as today). This keeps the TEA lane's evidence contract stable
and removes two behavior changes from the rollout — safer upgrade, ~2.3 KB/story cost accepted.

### Machine-read contracts (what downstream greps instead of re-reading)
- Close-out done-flip gate: grep walkthrough for `Verdict:` — FAIL blocks, all else flips (unchanged
  semantics, new location). Legacy fallback: if no `## Code Review` section, read
  `_bmad-output/implementation-artifacts/sudo-code-review-<story>.md` (epics ≤ now keep it).
- ③ baseline inheritance: the Evidence block's totals + SHA (unchanged semantics, one location now).
- Staleness: verdict line carries the reviewed SHA; any code diff SHA..HEAD invalidates (unchanged).

### Budgets (hard, like active-context's)
- `implementation_plan.md` ≤ **8 KB** including the audit section.
- `walkthrough.md` ≤ **10 KB** including the review section.
- Over budget → compress in place (pointers to git/story file), never split into a new file.

### Clean-room caveat (deliberate ordering)
③ still runs its Blind Hunter pass **diff-first, before opening the walkthrough**, then reads the
walkthrough for claimed evidence, deviations, and `## Your Actions` items it can clear. Reading the
dev's story before hunting would import the builder's bias the clean-room step exists to zero out.

## Files to change (17 references found; masters only — workflows regenerate)

| # | File | Change |
|---|---|---|
| 1 | `.agents/rules/artifacts-always-first.md` | Lean set → 2 living docs; rewrite §5 (walkthrough shape), §6 (review appends to walkthrough; legacy note), §7 (audit appends to plan); Hard Stops; add budgets |
| 2 | `.agents/commands/sudo-self-audit.md` (+`_AP` twin) | Persist target = plan's `## Self-Audit` section |
| 3 | `.agents/commands/sudo-dev-story-tests.md` (+`_AP`) | Step 2 persist wording; Step 5 checklist = 2 docs + sections-present check (Step 4 / automate evidence untouched) |
| 4 | `.agents/commands/sudo-code-review.md` (+`_AP`) | Step 4 verdict → walkthrough `## Code Review` (canonical line); Step 5 merges into it; diff-first ordering; Your-Actions clearing; legacy fallback note |
| 5 | `.agents/commands/sudo-update-sprint-memory.md` | Step 1.5 (one doc), Step 4 verdict read → walkthrough line, legacy file fallback |
| 6 | `.agents/commands/sudo-merge-epic-workingtrees.md` | Same verdict re-point per lane |
| 7 | `.agents/commands/sudo-prune-context.md` | Pointer-map references |
| 8 | `.agents/rules/constitution.md` | Artifact-set reference |
| 9 | `.agents/reference/autopilot_bmad_dev_loop.md` + `autopilot_claude.md` / `autopilot_opencode.md` / `autopilot_mobile.md` | Stage 2 writes audit into plan; Stage 4 writes review into walkthrough; mobile INLINES stage content — edit its inlined copy too (all three engines or none) |
| 10 | `.agents/workflows/*` (antigravity) | Never hand-edit — regenerate via `/sync-agents` |
| 11 | `Fresh_Workspace_BMAD` template | Propagate per `living-template-sync` |
| 12 | AGY `_artifacts/AGENTS.md` (+ other maintained projects') | Local-law copy of the two-doc close |

Out of scope: ALL TEA test-artifacts (kept by ruling, see Target design) and slimming the BMAD
story-file Dev Agent Record to pointers (phase 2 if ever — touches BMAD internals; house rule: fix
the rule, not BMAD internals).

## Execution order
1. Rule first (#1), then commands (#2–7), diffing each `_AP` twin.
2. Constitution + autopilot reference + 3 engines (#8–9).
3. `/sync-agents` to regenerate workflows + push to all four platforms (#10).
4. Templates + project AGENTS.md (#11–12).
5. Memory: update `sudo-commands-have-ap-twins-that-drift`-adjacent notes; new memory for the two-doc
   close + legacy fallback.

## Back-compat
- Old stories keep their standalone files — valid history; all readers get "section first, legacy file
  second" fallbacks (same pattern §6 already uses for epics 11–12).
- `story-artifacts-live-in-the-tree` still holds: the check becomes "section present in the doc", and
  an absent section = that step never ran — same action, run the command.

## Verification
- Dry-run one story close on AGY (next story in lane) end-to-end: ② produces 2 docs, ③ appends, close-out
  flips from the walkthrough verdict line, board rebuild unchanged.
- Grep the toolkit for the retired filenames afterward — zero live references outside legacy-fallback
  clauses and history.

## Expected savings
- Writes: ~57 KB → ~27 KB per story (**~50–55% output-token cut**), from killing the verdict file
  (12.4 KB), the standalone audit (5.9 KB), duplicate findings/AC tables, and 3 of 4 historical test
  pastes. TEA files kept by ruling (~8.7 KB/story, accepted).
- Reads: ③ and close-out re-read 2 docs (+ a one-line TEA link) instead of 4–5; budgets cap the
  re-read ceiling permanently.

## Open questions
None blocking.
