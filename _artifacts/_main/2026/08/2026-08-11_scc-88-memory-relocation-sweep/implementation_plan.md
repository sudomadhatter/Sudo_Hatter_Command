# SCC-88 — the first relocation sweep (lobby half)

**Plan gate:** `/smh-memory-audit` Step 4. The proposal below was presented and approved per item
on 2026-08-11 before anything outside `_artifacts/` was touched, which is this command's plan gate
(`.agents/rules/artifacts-always-first.md`).

**Paired with AVCH-53** — the AGY half, which is the *destination* and therefore lands first.

## Why now

The index is 21,296 / 25,600 B (83.2%) and is loaded whole into every session, on every platform,
on both machines, before any work happens. SCC-69 ground-truthed all 145 memories and freed
**633 bytes**, so compaction is measured spent. Relocation is the remaining lever and it
summarizes nothing away.

## What was ground-truthed (Step 3)

| Claim checked | Result |
|---|---|
| Is AGY content genuinely single-project? NEXgen shares the architecture | NEXgen is a **scaffold**: 9 backend `.py`, no frontend source, 0 BMAD stories, a 471 B `firestore.rules`. The "two projects depend on it" test does not bite today. |
| Are the memories under `## AGY *` headings actually AGY? | **No.** `## AGY infra & ops` is mostly the git branch model, the ⛔ backticks hazard, the one-merge rule, worktrees, and all four per-machine memories. `## AGY sprint & stories` is entirely cross-project workflow law. |
| Four that *look* AGY | `firestore-rules-tests-need-java` (NEXgen ships rules), `git-merge-wedges-next-dev-tailwind` (toolchain), `vitest-full-suite-contends-across-lanes` (per-STACK), `check-maps-all-false-stale-agy` (the defect is in the **lobby's** fan-out). All stay. |
| The 9 `CLOSED/RETIRED/FIXED` rows the gate surfaced | 7 are live lessons that merely *mention* something retired. 2 are genuinely closed (`tea-retrofit-active-initiative` verified closed 2026-07-03, commits landed in `dea87746`; `governance-gate-scans-venv` closed 2026-08-03) and both still carry live lessons. **No retirements.** |
| AGY's back-pointer | Verified **absent** — 0 occurrences of the lobby store path in its index. |
| AGY's branch | On `epic/AVCH-18-adk-2x-runtime`, **3 ahead / 8 behind main**, carrying a written "don't merge to main early". Wrong destination; AVCH-53 branches off AGY's main. |

## Approved dispositions

**📦 Relocate — 33 files** to `Projects/AGY_AVIATIONCHAT/_artifacts/_memory/`: auth/entitlement/
product internals (10), sprint & board state (5), infra & ops (7), test-harness instances (10),
one code hazard. 13 index rows deleted outright, 5 grouped rows rewritten.

**✅ Kept despite the signal — operator rulings, 2026-08-11:**
- The three ⛔ data-safety rows (`agy-has-real-nda-users`, `agy-archive-never-delete-ruling`,
  `agy-corpus-is-the-asset`). AGY-scoped by subject, but they guard real production data and the
  trade is asymmetric: ~500 B of index against the corpus. A comment in the index records the
  ruling so a later sweep does not "finish" the job.
- `tea-retrofit-active-initiative` — CLOSED and AGY-scoped, but the most-linked memory in either
  store (13 inbound) with 10 referrers staying in the lobby. Reach beats tidiness.

**🗑️/🔀/🗜️ — none.** Compaction is spent; that is the finding, not an omission.

**🚩 Not mine to touch:** `_my_resources/migrations/` → `docs/migrations/` appeared in the main
checkout at 11:58:47, mid-session, from another live session. Excluded entirely; this lane is a
worktree partly so that work cannot be swept in.

## Acceptance

- A1 index falls materially below the 90% trigger without the cap moving — **25 KB / 90% unchanged**
- A2 every relocated file exists in AGY's store and is indexed there before the lobby deletes it
- A3 AGY's back-pointer present, so the outbound cross-store links are followable (AVCH-53)
- A4 `check_store()` clean on both stores; every markdown link in both indexes resolves
- A5 no doc outside the store carries a broken markdown link to a relocated file
- A6 the gate does not report relocated targets as danglers to "fix at the source"
- A7 `run_all` 12/12, `workflow_lint --toolkit-only` 0/0, `sop_currency` exit 0
