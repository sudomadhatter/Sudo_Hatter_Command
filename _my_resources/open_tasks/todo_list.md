## Todo list
<!-- Daniel's personal task notes for AGY_AVIATIONCHAT. READ-ONLY for agents.
    - Always cross-check against the live project files before trusting anything here. -->

1. **On the DESKTOP (when home): re-scope + rebuild the GitNexus indexes (2026-07-02 laptop session):**
   - The laptop indexes were mapping noise — lobby was 78% `_artifacts`/`_my_resources`/`_bmad` and missed `.agents/` entirely; AGY_AVIATIONCHAT (1786 files) was 66% artifacts/personal docs with no `.gitnexusignore` at all. Fixed on the laptop by writing scoped `.gitnexusignore` files (lobby: excludes `_artifacts`, `_my_resources`, `_bmad*`, `_routing-canary`; AGY: excludes `_artifacts`, `_my_resources`, `_bmad*`, `*.out`, `*.bak`) and re-running analyze. Result: lobby 67 symbols (routing/docs surface only), AGY 37.7k symbols (100% product code, was 66% noise). NOTE: `.agents/` can NOT be indexed on gitnexus 1.6.8 — the walker hardcodes `dot:false` so dot-dirs are skipped before ignore rules; the `!/.agents/` line in the lobby file is inert future-proofing, don't expect toolkit symbols in the map.
   - The `.gitnexusignore` files travel via git (committed to `main_debug` in the lobby repo and the AGY repo) — but the INDEX does not (per item 1). So on the desktop: pull both repos, then `node .gitnexus/run.cjs analyze` in the lobby root AND in `Projects/AGY_AVIATIONCHAT`. The stale desktop indexes still contain all the noise until re-run.
   - If analyze fails with the `lbug.shadow` IO error, it's the leaked `gitnexus mcp` orphan again — kill per item 1's troubleshooting, retry.
3. Invoke bmad-testarch-atdd for stories that are already written to get the tests, then run the sudo-dev-story-tests.
4. Finish the back log on TEA Stories, use C:\Sudo_Hatter_Command\_my_resources\open_tasks\tea_testing_guide.md as reference to get up to speed quickly.
5. Add a Tag like to the vidoes for instagram..."So you want to be a (pilot_rating)
3. **Security hardinging**
   - Error reporting we have something already in place just verify how this works and how the agents can get access to it
   - CLI and MCP access to crashes 
   - Review the _artifacts to see how we built the crashed feature. 

## Open Work
<!-- open_tasks files — auto-listed by /1_update-maps -->