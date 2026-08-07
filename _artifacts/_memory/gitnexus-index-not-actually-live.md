---
name: gitnexus-index-not-actually-live
description: "GitNexus's index is a MACHINE-LOCAL artifact (~/.gitnexus/ + a gitignored project .gitnexus/ runner) that does NOT travel via git — built per-machine. LIVE on this laptop as of 2026-07-02 (lobby + AGY, PDG layer, pinned via committed .gitnexusrc). Plain `analyze` STRIPS the PDG layer unless .gitnexusrc pins pdg:true. Re-verify freshness on any fresh machine/checkout before trusting impact()."
metadata: 
  node_type: memory
  type: project
  originSessionId: 73ca08eb-87a8-432b-af19-3522ff5d8898
---

In AGY_AVIATIONCHAT the project `CLAUDE.md` instructs agents to run `impact()`/`context()` and references `.gitnexus/run.cjs`. **Status RESOLVED 2026-06-29: the index is now LIVE** — Daniel rebuilt it ("all set up"); the PreToolUse hook surfaces related symbols, `CLAUDE.md` claims 48,020 symbols / 104,734 rels / 300 flows, and `impact()`/`context()`/`detect_changes()` are usable again. (Earlier this session it was NOT live on this machine — `.gitnexus/` missing, `~/.gitnexus/` empty, MCP `list_repos` → `total: 0`, `impact` erroring "No indexed repositories" — the failure this memory originally captured.)

**Root cause (Daniel, 2026-06-29):** a GitNexus index is a **machine-local artifact** — the symbol DB lives in `~/.gitnexus/` on whichever machine ran `gitnexus analyze`, plus a gitignored project `.gitnexus/` runner. **It does NOT travel through git.** What's committed is only the *claim* in `CLAUDE.md` (the "18,051 symbols" line), not the index itself. Daniel indexed on his OTHER machine, so it works there but not here. Restarting the IDE does not help — this machine never ran `analyze`.

**ACCESS — `repo` param is now MANDATORY (2026-07-02):** two repos are indexed (`Sudo_Hatter_Command` lobby + `AGY_AVIATIONCHAT`), so EVERY GitNexus MCP call must pass `repo:"<name>"` — a bare call HARD-ERRORS: `"Multiple repositories indexed. Specify which one with the \"repo\" parameter. Available: Sudo_Hatter_Command, AGY_AVIATIONCHAT"`. The MCP server does NOT auto-resolve by CWD/active-project. When working in AviationChat pass `repo:"AGY_AVIATIONCHAT"`; from the lobby pass `repo:"Sudo_Hatter_Command"`. AGY's `CLAUDE.md`/`AGENTS.md` example snippets show BARE calls (no repo) and are gitnexus-auto-generated (`<!-- gitnexus:start -->` block, overwritten each analyze) so they can't be durably patched — remember to inject `repo` yourself. Verified working project-level against AGY 2026-07-02: `query`, `context`, `impact` (callgraph → `calculate_cognitive_zone` HIGH risk, 7 upstream into event_stream/specialist_chat/quiz_tutor/socratic_chat), `impact mode:"pdg"` (statement-precise interproc), `pdg_query controls` (1,055 CDG edges w/ guard flags), `explain` (taint layer live, 0 findings), `detect_changes`. CLI access from lobby without cd: `node Projects/AGY_AVIATIONCHAT/.gitnexus/run.cjs <cmd>`.

**Lobby scope trap — submodules get swallowed (2026-07-02):** `Projects/*` are git **submodules** (mode 160000 gitlinks; `.gitmodules` present) — each an independent repo with its OWN GitNexus map. The lobby (`Sudo_Hatter_Command`) is meant to index ONLY its own home-base infra. BUT GitNexus enumerates by **filesystem walk, not `git ls-files`**, so it does NOT respect submodule boundaries — a plain `analyze` at the lobby descends into every submodule working tree and balloons the map to ~105k nodes / 5910 files. `Projects/` is intentionally NOT gitignored (so VS Code auto-discovers the nested repos), so `.gitignore` won't stop it. Fix = a committed **`.gitnexusignore`** at the lobby root containing `/Projects/` (GitNexus reads `.gitnexusignore` with `.gitignore` semantics via `config/ignore-service.js`; there is NO `--ignore` CLI flag). This file is committable → propagates to the desktop.

**Noise scoping (2026-07-02 pm, Daniel-directed):** the first-pass indexes were mostly NOISE — lobby 1,535 "symbols" were 78% `_artifacts` walkthroughs + `_my_resources` personal docs + `_bmad` vendor (and MISSED `.agents/` entirely); AGY (1,786 files) was 66% the same noise with no `.gitnexusignore` at all. Both repos now carry committed scoped `.gitnexusignore` files (exclude `_artifacts/`, `_my_resources/`, `_bmad/`, `_bmad-output/`; lobby also `_routing-canary/`; AGY also `*.out`, `*.bak`). Post-scope truth: **lobby = 67 symbols** (routing/docs surface only — that small number is CORRECT, don't "fix" it), **AGY = ~37.7k symbols / 300 flows, 100% product code** (backend/frontend/scripts/load/docs). HARD LIMIT: **`.agents/` (the master toolkit) cannot be indexed on gitnexus 1.6.8** — `dist/core/ingestion/filesystem-walker.js` hardcodes glob `dot:false`, so dot-dirs are skipped BEFORE ignore rules; `!pattern` negation (#771) only rescues `DEFAULT_IGNORE_LIST` names (`vendor`, `__tests__`, …), never dotted paths. The `!/.agents/` line in the lobby ignore file is inert future-proofing. GitNexus is therefore blind to toolkit scripts — grep/read those directly. Desktop is still on the noisy indexes until it pulls + re-runs `analyze` in both repos (todo item exists).

**Laptop rebuild (2026-07-02):** both repos re-indexed on this machine (lobby `Sudo_Hatter_Command` @ its current commit + `Projects/AGY_AVIATIONCHAT`), `list_repos` shows both registered. Gotcha discovered: the indexes were originally built with `--pdg`, and running plain `analyze` (what the todo/CLAUDE.md say) forces a full rebuild WITHOUT the PDG layer — killing `pdg_query`/`explain` taint/`impact mode:"pdg"`. Fix: a committed `.gitnexusrc` (`{"pdg": true}`) now sits at both repo roots pinning the mode, so plain `analyze` keeps PDG and stays incremental. The lbug.shadow orphan-process bug from the desktop never triggered here (leaked `gitnexus mcp` node processes existed but analyze succeeded — only kill them if analyze actually fails with the IO exception).

**Mac setup — TWO things are per-machine, not one (2026-08-06):** the index is the well-known half; the
**MCP registration is the half that bites silently.** The tracked lobby `.mcp.json` launches the server
as `cmd /c gitnexus mcp` — `cmd` does not exist on macOS, so the server never starts and the agent has
**zero gitnexus tools even with a perfectly fresh index**. Do NOT "fix" the tracked file: native Windows
genuinely needs the `cmd /c` wrapper, so a bare command breaks the other machines. Add a **local-scope**
override instead (precedence: local > project > user) in `~/.claude.json` under
`projects["<repo path>"].mcpServers` — set for the lobby and AGY here. **Use absolute paths, not the
`gitnexus` shim**: `{"command": "/opt/homebrew/bin/node", "args":
["/opt/homebrew/lib/node_modules/gitnexus/dist/cli/index.js", "mcp"]}`. `launchctl getenv PATH` is
unset on macOS, so a GUI-launched editor spawns children with only `/usr/bin:/bin` — bare `gitnexus`
never resolves, and absolute `/opt/homebrew/bin/gitnexus` ALSO dies because its `#!/usr/bin/env node`
shebang re-looks-up node on that stripped PATH. Both failure modes are silent. The CLI is also not installed by anything else: `npm i -g gitnexus`. Indexed on
this Mac 2026-08-06 (gitnexus **1.6.9**): lobby 86 symbols / 18 files, AGY 50,234 symbols / 119,663
edges / 546 clusters / 300 flows, both PDG-pinned via the committed `.gitnexusrc`. Smoke-test the server
without a session by piping `initialize` + `tools/list` into `gitnexus mcp` (expect **17** tools) — but
macOS has **no `timeout`** binary, so a test using it exits 127 and prints nothing, which looks exactly
like a dead server; use `perl -e 'alarm(40); exec "gitnexus","mcp"'`. Also: **`analyze` rewrites tracked
skill docs** (`.claude/skills/gitnexus/*/SKILL.md`) to match the installed version — upstream to the
`.agents/` master before committing or `/sync-agents` reverts them, and keep every machine on the same
version or three files flip-flop forever. (The 1.6.8 `.agents/`-unindexable limit above is untested on
1.6.9 — the lobby index still excludes it.)

**How to apply:** Now that it's live, USE `impact()`/`context()`/`detect_changes()` per AGY's `CLAUDE.md` — run `impact` before editing a symbol, `detect_changes` before committing. On ANY fresh machine/checkout the index will be absent again (machine-local) → verify first (`list_repos`, or the `gitnexus://repo/AGY_AVIATIONCHAT/context` resource); if absent, `npx gitnexus analyze` rebuilds it (Daniel handles the re-index; may need `npm i -g gitnexus` per the npm-11 note). When genuinely unavailable, substitute a manual blast-radius check + full regression and note `impact unavailable` in the gate verdict. Related: [[command-center-sudo-skills]], [[tea-retrofit-active-initiative]].
