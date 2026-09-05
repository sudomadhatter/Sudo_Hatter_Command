---
name: gitnexus-index-not-actually-live
description: "⛔ RETIRED 2026-08 (SCC-272..288). GitNexus is GONE — replaced by code-review-graph, which is PROJECTS-ONLY (SCC-288): AGY_AVIATIONCHAT has it, the command centre deliberately does not. Do not call impact()/context()/detect_changes() via gitnexus; there is no server and no index. The ~1.1 GB of leftover .gitnexus/ caches was deleted 2026-08-25. Transferable lesson kept: a code index AND its MCP registration are BOTH per-machine, and the registration is the half that fails silently."
metadata:
  type: project
---

**⛔ GitNexus is retired. This file used to be its operating manual; that content was deleted because
it instructed agents to call tools that no longer exist.**

**What replaced it:** `code-review-graph`, via SCC-272 (bake-off) → SCC-273 (MCP registration, ignore
files, index scope) → SCC-274 ("all twelve gitnexus skill docs removed, ONE house skill") → SCC-275
(`check_maps` check 9 reads the graph DB via stdlib `sqlite3`) → SCC-288. All Done.

**⭐ It is PROJECTS-ONLY, and that is a ruling, not an omission (SCC-288: "Code graph to projects
only").** `Projects/AGY_AVIATIONCHAT` carries `.code-review-graph/`, `.code-review-graphignore`,
`docs/code-review-graph.md`, and `code-review-graph` in its `.mcp.json`. The command centre carries
none of it and must not be "fixed" — the lobby's map layer is `check_maps` + the doc-graph, refreshed
by hook. A lobby with no code graph is the correct state.

**Cleanup done 2026-08-25:** seven orphaned `.gitnexus/` caches totalling ~1.1 GB were deleted — one
per project plus two at the lobby (`.gitnexus/` and `.agents/.gitnexus/`). All were untracked and
gitignored, none had been re-indexed since 2026-06/07, and nothing referenced them. The `.agents/`
ones had `repoPath` pointing at the toolkit subfolder, so they only ever indexed `.agents/`. If any
reappear, they are stale by definition — delete them.

**⭐ The one lesson that transfers to any index tool, and the reason it is kept:** the index and its
**MCP registration are two separate per-machine problems**, and the registration is the half that
fails in silence. A tracked `.mcp.json` launching a server as `cmd /c <tool>` works on Windows and
does nothing on macOS — `cmd` does not exist there, so the agent has **zero tools even with a
perfectly fresh index**, with no error. Do not "fix" the tracked file (native Windows needs the
wrapper); add a local-scope override in `~/.claude.json` under `projects["<repo path>"].mcpServers`
with **absolute paths**. On macOS `launchctl getenv PATH` is unset, so a GUI-launched editor spawns
children with only `/usr/bin:/bin`: a bare command never resolves, and even an absolute Homebrew
shim dies because its `#!/usr/bin/env node` shebang re-looks-up node on that stripped PATH.

**How to apply:** never invoke gitnexus. In a project, use `code-review-graph`; from the lobby, use
`check_maps` and the doc-graph. Verify a graph tool is actually reachable before trusting an answer
from it — an absent MCP server and a tool that found nothing look identical. Related:
[[base-is-not-a-gitnexus-replacement]] (why the swap happened and why `base` was rejected),
[[one-pc-windows-and-wsl]], [[check-maps-all-false-stale-agy]], [[map-drift-recorder]].
