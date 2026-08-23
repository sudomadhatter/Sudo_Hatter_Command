# Repo Map — Sudo_Hatter_Command

<!-- REPO-MAP:CURATED-START -->
> **Navigation index for the home base (the LOBBY).** Hand-edit this block — the script only rewrites the
> AUTO body below. The folder *is* the app; this map says where to go. Least-context loading is the whole
> game: read `router.md` to route; to work inside a project read THAT project's `Projects/<name>/docs/repo-map.md`.

## To find X -> look here
| Need | Folder / file |
|---|---|
| Route / "what should I work on" / ownership | `router.md` (lobby map) |
| Home-base law + gates + persistence | `AGENTS.md` (`CLAUDE.md` / `GEMINI.md` are thin adapters) |
| The actual projects (each its own git repo + own repo-map) | `Projects/<name>/` → read that project's `docs/repo-map.md` |
| Master toolkit (single source of authorship) | `.agents/` — rules · commands · skills · workflows · bmad · scripts · templates |
| Synced engine mirrors (so `/commands` + skills resolve here) | `.claude/`, `.opencode/` |
| Shared memory (plans · walkthroughs · handoffs · ledger) | `_artifacts/` (`_main/` = home-base work; `<project>/` = per-project; `opencode/` = opencode's mirror) |
| Home-base docs (this map · workspace standard) | `docs/` |
| **Every SOP + PRD** — what the operator does and types | **`docs/_scc_sops_prds/`** — start at its `INDEX.md`; `workflows_testing_SOP.md` is THE quick reference |
| How to add / maintain workspaces (`/smh-new-project`, `/smh-sync-agents`) | `docs/system-builder.md` |
| Model-agnostic proof the routing works | `_routing-canary/` |
| BMAD-generated output (planning/implementation/test artifacts from running BMAD workflows at the home base) | `_bmad-output/` |
| Daniel's thinking space — **⛔ IGNORE unless he links a document** (ruling 2026-08-10) | `_my_resources/` — not authoritative, deliberately un-scanned, staleness fine by design. Exception: `open_tasks/todo_list.md` (the `migrations/` exception retired under SCC-89 — that kit now lives in `docs/migrations/`) |
| Secrets / env files — ALL gitignored, so never in the AUTO tree below | lobby `.env` (root) + per-project files; master bundle master.env under the migrations `auth_keys/` tree (hand-carried, NEVER committed; the whole `auth_keys/` tree is gitignored, so it is invisible to git and to this lint); export/restore: `docs/migrations/scripts/Export-EnvMaster.ps1` / `scripts/Restore-EnvMaster.ps1` — both now default to the operator's real bundle location (`docs/migrations/auth_keys/_secrets/master.env`) and resolve the lobby root three levels up, fixed under SCC-89; `-MasterPath` still overrides for a USB copy |
| **"What do we do next" / open tasks / Daniel's plans & PRPs** — READ-ONLY, never edit | `_my_resources/open_tasks/` (start at `todo_list.md`; cross-check vs live project files) |
| Scratch scripts and temp files | `scratch/` |

## Knowledge map (which doc to read when)
| Doc | Read it when |
|---|---|
| `router.md` | Routing / ownership / "where does this go" |
| `AGENTS.md` | The home-base operating contract (gates, artifacts, persistence) |
| `docs/workspace-standard.md` | How a workspace is shaped + kept healthy (repo-map, artifacts, naming) |
| `_artifacts/INDEX.md` | The session ledger — "pick up" scans it, "hand off" appends to it |
| a project's `Projects/<name>/AGENTS.md` | When you go work inside that project (not this file) |
| `_my_resources/open_tasks/` | Daniel asks "what do we do next / what's left" — read his todo + saved plans/PRPs (read-only) |
| `docs/system-builder.md` | Growing/maintaining the home base itself — `/new-project`, `/sync-agents`, workspace-conversion rules |
| `docs/migrations/INDEX.md` | New-machine setup / repopulating any `.env` or `auth_keys/` file (→ `new_machine-migration-guide.md`; the manifest inside the hand-carried master.env lists every secret file + its exact path). Standing reference kit. Moved out of `_my_resources/` (excluded from regen) into `docs/` under SCC-89, so it now DOES appear in the AUTO tree below — its `auth_keys/` subtree does not, being ignored by name |

**code-review-graph (the code graph) — ⛔ THE CENTRE CARRIES NONE, BY DESIGN (SCC-289).** A code graph
parses code; this repo is markdown, so an index here described almost nothing. There is no MCP server for
it on any of the four platforms, no ignore file, and no index — `check_maps.py` check 9 says *"no index →
skip"* and that is the permanent answer here, not a machine that has not built one yet.

The graph is **project-level tooling** and the centre keeps only the project-facing half of it: the
`code-review-graph` skill, `risk_seam.py`, and `docs/code-review-graph.md`. Inside a project under
`Projects/`, that project is its own repo with its own index, and a review run *from here* must say which
one — `risk_seam.py classify --repo <the project worktree> …`. Without `--repo` the seam resolves the repo
from CWD, which during a project review is this repo, and the answer is always `unclassified`.

What maps the centre instead is the **doc graph** (`docs/doc-graph.md`) — markdown link structure over
`.agents/` and `docs/` — plus the AUTO tree below.

```bash
code-review-graph build      # full rebuild, ~4s here
code-review-graph update     # incremental, only changed files
code-review-graph status     # nodes, edges, built_at_commit vs current_sha
```

The graph records the commit it was built at, so `check_maps.py` check 9 can compare it with `HEAD` and
hint when it is stale. Tier-2/disposable — the maps above stay canonical. Full guidance:
`docs/code-review-graph.md`.

> Note: the markdown rule/workflow files yield few cross-file edges (the parser extracts code structure,
> not doc references) — the graph is strong for the `.py`/`.ps1` scripts and thin for the prose; trust the
> files and the doc-graph for "what references what."
>
> **Doc wiring (the prose layer the code graph does not model):** `docs/doc-graph.md` (+ `doc-graph.json`)
> is the owned, deterministic, no-LLM map of which `.md` references which across `.agents/` — hubs, plus a
> broken-path / ambiguous-ref report. Rebuild after editing rules/workflows:
> `python3 .agents/scripts/generate_doc_graph.py` (PC: `python`). Source:
> `.agents/scripts/generate_doc_graph.py`.

**Drift:** checked at SessionStart by `.agents/scripts/check-repo-map-drift.ps1 -MapPath docs/repo-map.md` — it
nags if a new top-level folder isn't named here. Rebuild the AUTO body:
`python3 .agents/scripts/generate_repo_map.py --root . --mode content --ignore Projects,_my_resources` (`--root .` is required here — the master generator lives at `.agents/scripts/`, so its default root would otherwise resolve to `.agents/`; the default output is `docs/repo-map.md`).
<!-- REPO-MAP:CURATED-END -->

<!-- REPO-MAP:AUTO-START -->
<!-- generated by scripts/generate_repo_map.py — do NOT hand-edit this block;
     mode=content, collapse-threshold=8 files. Edit the CURATED block above. -->

```text
Sudo_Hatter_Command/
  _bmad/
    _config/
        [4 files: .csvx3, .yamlx1 | e.g. bmad-help.csv]
    bmm/
        [2 files: .yamlx1, .csvx1 | e.g. config.yaml]
    core/
        [2 files: .yamlx1, .csvx1 | e.g. config.yaml]
    custom/
        [5 files: .tomlx5 | e.g. bmad-dev-story.toml]
    scripts/
        [3 files: .pyx3 | e.g. memlog.py]
    tea/
      workflows/
        testarch/
            [1 files: .mdx1 | e.g. README.md]
        [2 files: .yamlx1, .csvx1 | e.g. config.yaml]
      [2 files: .tomlx2 | e.g. config.toml]
  _bmad-output/
    brainstorming/
      brainstorm-tdad-integration-2026-07-07/
        [1 files: .mdx1 | e.g. INDEX.md]
    forge/
      aviationchat-prd/
  _routing-canary/
    control/
        [2 files: .mdx2 | e.g. INDEX.md]
    skills/
        [2 files: .mdx2 | e.g. INDEX.md]
      [6 files: .mdx6 | e.g. AGENTS.md]
  docs/
    _scc_sops_prds/
        [15 files: .mdx15 | e.g. INDEX.md]
    migrations/
      antigravity_extensions/
          [1 files: .txtx1 | e.g. antigravity-extension-ids.txt]
      gemini_extensions/
          [2 files: .mdx1, .shx1 | e.g. gemini-extensions-sync-guide.md]
      install_guides/
          [7 files: .mdx7 | e.g. antigravity-ide-extension-migration.md]
      scripts/
          [9 files: .ps1x4, .pyx2, .shx2, .patchx1 | e.g. Export-EnvMaster.ps1]
        [1 files: .mdx1 | e.g. INDEX.md]
      [10 files: .mdx9, .jsonx1 | e.g. AGENTS.md]
  scratch/
      [1 files: .pyx1 | e.g. find_brainstorm.py]
    [9 files: .mdx5, .txtx3, .jsonx1 | e.g. AGENTS.md]
```
<!-- REPO-MAP:AUTO-END -->
