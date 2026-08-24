---
IsArtifact: true
ArtifactMetadata:
  title: Walkthrough — Command Center and AviationChat map reconciliation
  type: walkthrough
  date: 2026-08-23
---

# Walkthrough — Command Center and AviationChat map reconciliation

**Ticket:** SCC-308 · **Branch:** `chore/SCC-308-update-maps-indexes`

## Outcome

The approved two-repo scope is reconciled. The Command Center and AviationChat map gates pass; NEXgen VR
was removed from the run and is clean. No commit or push was made.

## Command Center

- Rebuilt the root artifact ledger from `_artifacts/_main/INDEX.md` plus the existing live/archive rows.
- Added 110 previously unrepresented `_main` sessions (including this session), retained exactly the newest
  50 rows live, and moved 110 overflow rows verbatim into the archive. Archive total: 168 rows.
- Repaired the current `/smh-update-maps-indexes` pointers in the artifact law and README.
- Reconciled the skill inventory to 73 local directories (34 hand-authored + 39 generated launchers) plus
  56 BMAD skills, removed the retired `adk-prompting` example, corrected Claude's launcher-skill surface,
  and updated the workflow inventory to the ten-check linter.

## AviationChat

See the project-local walkthrough at
`Projects/AGY_AVIATIONCHAT/_artifacts/_main/2026-08-23_update-maps-indexes/walkthrough.md`.

## Verification

```text
$ python3 .agents/scripts/check_maps.py
All maps & INDEXes agree with disk. [ok]

$ python3 .agents/scripts/check_maps.py --root Projects/AGY_AVIATIONCHAT
All maps & INDEXes agree with disk. [ok]
```

The AviationChat gate also reports `[ok] graph matches HEAD`; the lobby correctly reports that it carries
no code graph. `check_links.py` was clean for the edited lobby navigation files.

## Task Checklist

- [x] Confirm scope as Command Center + AviationChat only.
- [x] Restore AviationChat thin-project conformance before map reconciliation.
- [x] Reconcile AviationChat repo-map, depth-3 ledgers, and current navigation.
- [x] Restore the Command Center newest-50 live ledger and verbatim archive.
- [x] Correct current Command Center inventory and command-surface claims.
- [x] Verify both targeted map gates and preserve NEXgen untouched.
- [x] Update both continuity briefs and write one walkthrough per owning repo.
- [x] SCC-308 and AVCH-87 minted and moved to In Progress.
- [x] The merge itself — lands via this branch's PR

## Your Actions

Nothing is owed after the gated PR merge; the close-out ceremony owns Jira finalization and pruning.
