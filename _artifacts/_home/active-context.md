# ACTIVE CONTEXT — _home  (you own this, not a vendor)

## 1. PRIME STATE
Current workspace: `_home` (lobby at `C:\Sudo_Hatter_Command`)   |   Last session: 2026-06-24
Restructure DONE: projects relocated under `Projects\`; all paths fixed to `Sudo_Hatter_Command`.

## 5. PICK UP  (read-only brief)
- 5.1 Doing: Standing up the home base (folder-as-workspace routing system). **Phase A COMPLETE. Rename-day restructure COMPLETE.**
- 5.2 Changed recently: ran `_system\rename-fix.ps1 -Apply` — (1) moved all 7 projects into `Projects\` (aviationChat-AGY, clean-bmad-workspace, jetChat-AGY, B&L WorldWide, NEXGen Films, ingestion-Pipeline-AC, openCode); (2) rewrote old root name → `Sudo_Hatter_Command` (project refs → `…\Projects\<name>`) across **262 text files**: home-base spine + every project's own files + user-global `~\.claude\settings.json`. Verified: **zero stale `AGY-Projects` refs remain** in the tree. First had to make the script run on Windows PowerShell 5.1 (it was authored for pwsh 7): `(try{}catch{})` expression → `$(try{}catch{})` on lines 85/116, and ASCII-normalized 4 smart chars (em-dash/ellipsis). No move/replace logic changed. NOTE: the script rewrote its own `$OldName` default → it is now a spent/no-op tool.
- 5.3 Open decisions: RESOLVED (rename + bulk-move done in a single pass).
- 5.4 Blocked / needs approval: (a) `git commit` still NOT approved (only `git init` done) — home-base repo + each project repo now carry path-only diffs. (b) **5 venvs kept, NOT removed** (Daniel chose "Apply, keep venvs") — they still hardcode the old path and must be recreated per-project when next used: `Projects\NEXGen Films\.venv`, `Projects\jetChat-AGY\backend\venv`, `Projects\clean-bmad-workspace\.venv`, `Projects\B&L WorldWide\.venv`, `Projects\aviationChat-AGY\backend\.venv`. (c) IDE reload recommended (settings paths changed).
- 5.5 Best next move (THE immediate step): (1) Reload the IDE window so it picks up new `Projects\` paths + rewritten settings. (2) Recreate each project's venv as you enter it (`uv sync` or `python -m venv .venv`). (3) Begin **Phase B**: convert `Projects\clean-bmad-workspace` first.

## 6. HAND OFF  (verified state at this checkpoint)
- 6.1 Completed: Phase A home-base spine + master toolkit + `_experiment/` + engines + lobby sync + `git init`. **Rename-day restructure applied & verified** (move + 262-file path-fix; 0 stale refs). `rename-fix.ps1` made 5.1-safe.
- 6.2 In progress: nothing executing. Awaiting Daniel's IDE reload + per-project venv recreation, then Phase B.
- 6.3 Open tasks / trade-offs: Phase B (convert clean-bmad-workspace), Phase C (remaining projects, aviationChat last), Phase D (gates + scaffolder finalize). Cross-LLM cold test of `_experiment/` in opencode + Antigravity still to run. Decide whether/when to `git commit` the restructure (per-project repos affected).
- 6.4 Related links: `_docs/master-implementation-plan.md`.
