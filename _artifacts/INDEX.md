# _artifacts INDEX — shared memory ledger

One row per session, newest at top. **"pick up"** scans this; **"hand off"** appends to it.
This is the scannable "database" — naming conventions + this ledger replace a query layer.

| Date | Workspace | Slug | Summary | Status |
|---|---|---|---|---|
| 2026-06-24 | _home | push-all-project-repos | Committed + pushed path-fixes to all 7 project repos. 5 clean FF (aviationChat, clean-bmad, B&L, jetChat, NEXGen — jetChat/NEXGen bundled pre-existing WIP per Daniel). ingestion+openCode were stale/behind → reset --hard origin/main to take newer remote work; ingestion still had old paths so re-applied path-fix (39 files)+pushed, openCode remote already clean (FF only). All 7 now clean/in-sync. Home base local (active-context+INDEX) committed too | handoff |
| 2026-06-24 | _home | github-setup-and-repo-verify | Home base committed (036ae32, 2223 files, main) + pushed to origin github.com/sudomadhatter/Sudo_Hatter_Command (private). Verified all 7 Projects/ keep their OWN repos+remotes (outer repo ignores /Projects/, no gitlinks); fixed B&L origin (was Fresh_Workspace_BMAD → B-L-WorldWide); jetChat/others confirmed correct. Path-fixes left uncommitted per Daniel | handoff |
| 2026-06-24 | _home | rename-day-restructure | Applied rename-fix.ps1: moved 7 projects→Projects/, path-fixed 262 files →Sudo_Hatter_Command (0 stale refs); fixed script for PS5.1; venvs kept (recreate per-project). Next: IDE reload → Phase B (clean-bmad) | handoff |
| 2026-06-24 | _home | home-base-routing-system | Phase A complete (spine · master · experiment · engines · lobby · git init); rename→Sudo_Hatter_Command + bulk-move to Projects/ pending | handoff |
