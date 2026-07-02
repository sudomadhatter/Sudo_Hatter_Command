---
name: gitnexus-cli
description: "Use when the user needs to run GitNexus CLI commands like analyze/index a repo, check status, clean the index, generate a wiki, or list indexed repos. Examples: \"Index this repo\", \"Reanalyze the codebase\", \"Generate a wiki\""
---

# GitNexus CLI Commands

Commands below use `node .gitnexus/run.cjs <command>` — the project-local runner `gitnexus analyze` drops next to the index. It auto-selects an available runner at call time (global `gitnexus`, else `pnpm dlx`, else `npx`), so no package-manager assumption and no global install is required.

> **Not analyzed yet, or `node .gitnexus/run.cjs` reports `Cannot find module`** (the gitignored runner is absent — e.g. a fresh clone or `git clean`)? (Re)generate it with `npx gitnexus analyze` from the project root. On **npm 11.x**, if `npx` crashes during install (`node.target is null`), install once with `npm i -g gitnexus` (then `gitnexus analyze`) or use `pnpm --allow-build=@ladybugdb/core --allow-build=gitnexus --allow-build=tree-sitter dlx gitnexus@latest analyze`. See [#1939](https://github.com/abhigyanpatwari/GitNexus/issues/1939).

## Commands

### analyze — Build or refresh the index

```bash
node .gitnexus/run.cjs analyze
```

Run from the project root. This parses all source files, builds the knowledge graph, writes it to `.gitnexus/`, and generates CLAUDE.md / AGENTS.md context files.

| Flag           | Effect                                                           |
| -------------- | ---------------------------------------------------------------- |
| `--force`      | Force full re-index even if up to date                           |
| `--embeddings` | Enable embedding generation for semantic search (off by default) |
| `--drop-embeddings` | Drop existing embeddings on rebuild. By default, an `analyze` without `--embeddings` preserves them. |

**When to run:** First time in a project, after major code changes, or when `gitnexus://repo/{name}/context` reports the index is stale. In Claude Code, a PostToolUse hook detects staleness after `git commit` and `git merge` and notifies the agent to run `analyze` — the hook does not run analyze itself, to avoid blocking the agent for up to 120s and risking KuzuDB corruption on timeout.

### status — Check index freshness

```bash
node .gitnexus/run.cjs status
```

Shows whether the current repo has a GitNexus index, when it was last updated, and symbol/relationship counts. Use this to check if re-indexing is needed.

### clean — Delete the index

```bash
node .gitnexus/run.cjs clean
```

Deletes the `.gitnexus/` directory and unregisters the repo from the global registry. Use before re-indexing if the index is corrupt or after removing GitNexus from a project.

| Flag      | Effect                                            |
| --------- | ------------------------------------------------- |
| `--force` | Skip confirmation prompt                          |
| `--all`   | Clean all indexed repos, not just the current one |

### wiki — Generate documentation from the graph

```bash
node .gitnexus/run.cjs wiki
```

Generates repository documentation from the knowledge graph using an LLM. Requires an API key (saved to `~/.gitnexus/config.json` on first use).

| Flag                | Effect                                    |
| ------------------- | ----------------------------------------- |
| `--force`           | Force full regeneration                   |
| `--model <model>`   | LLM model (default: minimax/minimax-m2.5) |
| `--base-url <url>`  | LLM API base URL                          |
| `--api-key <key>`   | LLM API key                               |
| `--concurrency <n>` | Parallel LLM calls (default: 3)           |
| `--gist`            | Publish wiki as a public GitHub Gist      |

### list — Show all indexed repos

```bash
node .gitnexus/run.cjs list
```

Lists all repositories registered in `~/.gitnexus/registry.json`. The MCP `list_repos` tool provides the same information.

## After Indexing

1. **Read `gitnexus://repo/{name}/context`** to verify the index loaded
2. Use the other GitNexus skills (`exploring`, `debugging`, `impact-analysis`, `refactoring`) for your task

## Troubleshooting

- **"Not inside a git repository"**: Run from a directory inside a git repo
- **Index is stale after re-analyzing**: Restart Claude Code to reload the MCP server
- **Embeddings slow**: Omit `--embeddings` (it's off by default) or set `OPENAI_API_KEY` for faster API-based embedding
- **`analyze` fails with `IO exception: Cannot open file ... lbug.shadow` (or similar "cannot open/find file" on `.gitnexus/lbug*`)**: A leaked `gitnexus mcp` server process (from a Claude Code window that was closed without cleanly exiting) is still holding the KuzuDB file open, blocking the CLI from writing to it. This accumulates over sessions — check for it before assuming index corruption:
  1. List candidates: PowerShell `Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -like '*gitnexus*mcp*' } | Select ProcessId, CommandLine` (bash equivalent: `ps` won't show command lines reliably on Windows — use the PowerShell form).
  2. If there are more `gitnexus mcp` processes than open Claude Code windows, the extras are orphans. Kill them: `Stop-Process -Id <pid> -Force`. Killing one also kills that window's own GitNexus MCP connection — warn the user first if other windows might be active, since it's not obvious from the process list alone which PID belongs to which window.
  3. Re-run `node .gitnexus/run.cjs analyze --force` after clearing the locks.
  4. This repo's own GitNexus tools go dead once its own `gitnexus mcp` process is killed — reconnect by restarting Claude Code / reloading MCP servers.
- **A repo vanished from `list_repos` / `~/.gitnexus/registry.json` even though `.gitnexus/` still has data on disk**: The registry entry can get dropped independently of the on-disk index (e.g. after a project folder rename, or a registry write racing a leaked MCP process — see above). `node .gitnexus/run.cjs status` (run from inside the project) still works off the local `.gitnexus/meta.json` and will show the true last-indexed commit even when `list_repos` doesn't know about the repo. Fix: clear any file locks per above, then `analyze --force` from the project root to rebuild and re-register it.
- **The index does NOT sync across machines**: `.gitnexus/` is gitignored by design (it's a large binary KuzuDB store) and `~/.gitnexus/registry.json` is per-machine, per-user. Every computer you use needs its own `node .gitnexus/run.cjs analyze` after cloning — a story marked "unblocked by GitNexus" on one machine can still show as GitNexus-blocked on another until that machine indexes too. If a story's blocker doc says a GitNexus block was "resolved" on some date, treat that as machine-scoped, not global — re-check `gitnexus://repo/{name}/context` staleness (or run `status`) on whichever machine you're actually working from before trusting it.
