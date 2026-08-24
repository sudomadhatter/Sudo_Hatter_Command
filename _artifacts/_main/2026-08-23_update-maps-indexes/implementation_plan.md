---
IsArtifact: true
ArtifactMetadata:
  title: Map and INDEX reconciliation — lobby
  type: implementation_plan
  date: 2026-08-23
---

# Map and INDEX reconciliation — lobby

## Goal

Reconcile the home-base navigation layer against disk after the 2026-08-09 through 2026-08-23 command-centre work. Keep generated maps mode-preserving, restore the root artifact ledger to its newest-50 contract, and repair only current navigation prose. Historical session descriptions remain historical.

This is one half of the operator-confirmed two-repo scope: the Command Center plus AviationChat. NEXgen VR is explicitly excluded.

## Acceptance criteria

1. The lobby repo-map and doc graph remain byte-current in `mode=content`.
2. The root artifact ledger shows the newest 50 sessions, with older rows moved verbatim to the archive; the `_main` bucket remains one-row-per-session.
3. Current navigation text names `/smh-update-maps-indexes`, not the retired `/update-maps-indexes` door.
4. The skills family map states the measured inventory (73 master skill directories: 50 hand-authored + 23 generated launchers; Claude exposes 74 non-BMAD + 56 BMAD skills), and removes the retired `adk-prompting` example.
5. The commands INDEX no longer claims Claude receives `.claude/commands/`; the workflows INDEX describes the current eleven-check map linter.
6. Lobby-only map lint and generated-doc verification pass. The focused Command Center + AviationChat verification is clean; NEXgen VR remains untouched.

## Execution order

1. Rebuild `_artifacts/INDEX.md` from the already-current `_artifacts/_main/INDEX.md`: add the 108 unindexed sessions, retain the newest 50 in the live ledger, and move the displaced rows verbatim into `INDEX-archive.md`.
2. Add this reconciliation session to the root and `_main` ledgers.
3. Repair the three current artifact-navigation references.
4. Correct the three master `.agents/*/INDEX.md` inventory/structure claims.
5. Re-run the lobby linter and generated-doc verification; inspect the diff for historical-text preservation.
6. Update the lobby continuity brief and write one walkthrough with evidence; after the operator's later shipping instruction, land through the ticketed SCC-308 and AVCH-87 lanes.

## Declared Change Set

- NEW `_artifacts/_main/2026-08-23_update-maps-indexes/implementation_plan.md` → records the approved lobby plan
- NEW `_artifacts/_main/2026-08-23_update-maps-indexes/walkthrough.md` → records final evidence and handoff
- EDIT `_artifacts/INDEX.md` → restores newest-50 root session coverage and current command naming
- EDIT `_artifacts/INDEX-archive.md` → preserves displaced ledger rows verbatim
- EDIT `_artifacts/_main/INDEX.md` → indexes this reconciliation session
- EDIT `_artifacts/AGENTS.md` → repairs the current map-maintenance command pointer
- EDIT `_artifacts/README.md` → repairs the current map-maintenance command pointer
- EDIT `.agents/skills/INDEX.md` → reconciles measured skill counts and removes a retired example
- EDIT `.agents/commands/INDEX.md` → removes the retired Claude command-door claim
- EDIT `.agents/workflows/INDEX.md` → reconciles the map linter's eleven checks and seven fatal checks
- EDIT `.claude/skills/INDEX.md` → keeps the generated Claude cache index byte-identical to its master
- EDIT `.agents/scripts/check_links.py` → treats the rolled archive as the same historical ledger class as the live ledger
- EDIT `.agents/scripts/tests/test_check_links.py` → proves archive claims are skipped while equivalent current claims still fail
- EDIT `_artifacts/_main/active-context.md` → records the two-repo reconciliation handoff

## Open questions

None. AviationChat's conformance repair is explicit in its own plan and must run before its map edits.

## Verification

```bash
python3 .agents/scripts/check_maps.py
python3 .agents/scripts/refresh_maps.py --verify
python3 .agents/scripts/check_maps.py --root Projects/AGY_AVIATIONCHAT
git diff --check
git diff -- _artifacts/INDEX.md _artifacts/INDEX-archive.md _artifacts/_main/INDEX.md _artifacts/AGENTS.md _artifacts/README.md .agents/skills/INDEX.md .agents/commands/INDEX.md .agents/workflows/INDEX.md
```

Both targeted lint runs must be clean. NEXgen VR is outside this run and is not modified.
