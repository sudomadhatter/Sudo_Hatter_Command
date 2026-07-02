## Todo list
<!-- Daniel's personal task notes for AGY_AVIATIONCHAT. READ-ONLY for agents.
    - Always cross-check against the live project files before trusting anything here. -->

1. **On the laptop, GitNexus needs its own local index — it never syncs via git (2026-07-02 session):**
   - `.gitnexus/` (the actual index, ~165MB KuzuDB store) is gitignored on purpose, and `~/.gitnexus/registry.json` (which repos are known) lives under the Windows user profile — both are per-machine. Pulling the latest commits does NOT bring the index with it.
   - Steps on the laptop, per repo you want indexed (at least `Sudo_Hatter_Command` root and `Projects/AGY_AVIATIONCHAT`): `cd` into it and run `node .gitnexus/run.cjs analyze`. First run there will be a full index, not incremental — give it a few minutes for AGY_AVIATIONCHAT (~1800 files).
   - No `.gitnexus/run.cjs` yet on the laptop (fresh clone)? Run `npx gitnexus analyze` instead. If npx crashes on npm 11 (`node.target is null`), `npm i -g gitnexus` once, then `gitnexus analyze`.
   - If `analyze` fails with `IO exception: Cannot open file ... lbug.shadow` (the exact bug fixed today on the desktop): check for leaked `gitnexus mcp` node processes — PowerShell `Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -like '*gitnexus*mcp*' }`, kill any orphans (`Stop-Process -Id <pid> -Force`), then retry. Full writeup is in `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` → Troubleshooting (pulled from `origin/main_debug` once you're on the laptop).
   - Verify it worked: `list_repos` (MCP) or `node .gitnexus/run.cjs status` should show the repo registered at your current commit, no staleness warning.
2. **On the DESKTOP (when home): re-scope + rebuild the GitNexus indexes (2026-07-02 laptop session):**
   - The laptop indexes were mapping noise — lobby was 78% `_artifacts`/`_my_resources`/`_bmad` and missed `.agents/` entirely; AGY_AVIATIONCHAT (1786 files) was 66% artifacts/personal docs with no `.gitnexusignore` at all. Fixed on the laptop by writing scoped `.gitnexusignore` files (lobby: excludes `_artifacts`, `_my_resources`, `_bmad*`, `_routing-canary`, re-includes `!/.agents/`; AGY: excludes `_artifacts`, `_my_resources`, `_bmad*`, `*.out`, `*.bak`) and re-running analyze.
   - The `.gitnexusignore` files travel via git (committed to `main_debug` in the lobby repo and the AGY repo) — but the INDEX does not (per item 1). So on the desktop: pull both repos, then `node .gitnexus/run.cjs analyze` in the lobby root AND in `Projects/AGY_AVIATIONCHAT`. The stale desktop indexes still contain all the noise until re-run.
   - If analyze fails with the `lbug.shadow` IO error, it's the leaked `gitnexus mcp` orphan again — kill per item 1's troubleshooting, retry.
3. Invoke bmad-testarch-atdd for stories that are already written to get the tests, then run the sudo-dev-story-tests.
3. Finish the back log on TEA Stories, use C:\Sudo_Hatter_Command\_my_resources\open_tasks\tea_testing_guide.md as reference to get up to speed quickly.
4. Add a Tag like to the vidoes for instagram..."So you want to be a (pilot_rating)

## Open Work
<!-- These are my research on topics we are working on, diagrams and notes for context, cross check these to the sprint status, use these as reference to get up to speed quickly: -->
    - tea_testing_guide.md