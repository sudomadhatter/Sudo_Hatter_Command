---
IsArtifact: true
ArtifactMetadata:
  title: Update maps and indexes after artifact year/month reorganization
  type: implementation_plan
  date: 2026-08-09
---

# Implementation Plan — Update Maps and Indexes

## Goal

Reconcile the lobby and maintained project navigation artifacts against disk after the June and July
home-base sessions moved under year/month folders. Preserve unrelated parallel work and leave every
deterministic or substantive exception explicit.

## Approved scope

1. Reconcile the home-base artifact ledgers:
   - update 56 moved paths in `_artifacts/_main/INDEX.md`;
   - add missing recent session rows;
   - create `2026/06/INDEX.md` and `2026/07/INDEX.md`;
   - backfill uncovered root-ledger sessions, restore newest-first order, and archive overflow to keep
     the live ledger at roughly 50 rows.
2. Repair navigation references affected by the move in the root ledger, active context, archive, and
   `_artifacts` README structure descriptions.
3. Refresh only the `## Open Work` manifest in the home-base `todo_list.md`, preserving Daniel's prose.
4. Reconcile AviationChat's new Epic 19 session and NEXgen's ledger ordering in their owning repos.
5. Delete the approved duplicate `2026/06/proposal_graphrag_executiblity.md`; its canonical content
   already lives in `2026-08-07_command-center-workflow-memory/implementation_plan.md`.
6. Re-run the fan-out linter. Keep the generated Playwright-output false positive and the obsolete
   AviationChat board-hook instructions visible as deferred defects rather than disguising them.
7. Refresh GitNexus for the lobby and AviationChat during this pass, then rerun after commit if the
   commit-based freshness stamp changes.

## Boundaries

- Do not edit or stage unrelated SCC-56 or operator prose changes.
- Do not create an INDEX inside generated `frontend/test-results` output.
- Do not rewrite the obsolete AviationChat hook behavior during this navigation-only pass.
- Do not commit or push; `/update-maps-indexes` lands by hand per repository.

## Verification

- Run `python3 .agents/scripts/check_maps.py --all` and classify every remaining failure.
- Verify every June/July session folder has a matching monthly and `_main` row.
- Verify the live root ledger has 50 newest rows and every archived row remains present.
- Verify open-work manifests match disk and Daniel's prose diff is preserved.
- Verify only approved files changed in each repository.
