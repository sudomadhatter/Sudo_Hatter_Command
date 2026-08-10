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
| Home-base docs (this map · workspace standard · master plan) | `docs/` |
| How to add / maintain workspaces (`/new-project`, `/sync-agents`) | `docs/system-builder.md` |
| Model-agnostic proof the routing works | `_routing-canary/` |
| BMAD-generated output (planning/implementation/test artifacts from running BMAD workflows at the home base) | `_bmad-output/` |
| Daniel's personal area — **PROTECTED** (don't edit/reference unless he says/links) | `_my_resources/` — **EXCEPT** `open_tasks/` (read-only carve-out below) |
| Secrets / env files — ALL gitignored, so never in the AUTO tree below | lobby `.env` (root) + per-project files; master bundle master.env under the migrations `auth_keys/` tree (hand-carried, NEVER committed; the whole `auth_keys/` tree is gitignored, so it is invisible to git and to this lint); export/restore: `_my_resources/migrations/scripts/Export-EnvMaster.ps1` / `scripts/Restore-EnvMaster.ps1` — ⚠ both still default to the pre-move location (a `_secrets` folder directly under `migrations/`); pass `-MasterPath` or update them |
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
| `_my_resources/migrations/INDEX.md` | New-machine setup / repopulating any `.env` or `auth_keys/` file (→ `new_machine-migration-guide.md`; the manifest inside the hand-carried master.env lists every secret file + its exact path). Disposable kit — `_my_resources/` is excluded from repo-map regen, so it never appears in the AUTO tree below |

> **⚠ There are actually TWO indexes here, and the lint checks the one you don't query** (found
> 2026-08-08). `check_maps.py`'s freshness hint reads the **root** `.gitnexus/meta.json` — a small
> whole-repo index (86 nodes; the lobby is nearly all markdown) whose only job is to carry a
> `lastCommit` stamp. The index you actually query is `SUDO_COMMAND` under `.agents/`, and because its
> documented build uses `--skip-git` it writes **no** commit stamp at all — so it can never satisfy that
> check, and the root one nagged permanently while pinned to `main_debug`, a branch retired 2026-08-07.
> **Re-index both**: `gitnexus analyze . --index-only -f` clears the lint; the `.agents/` command below
> refreshes what queries use. Node counts after centralization: root 86 · SUDO_COMMAND **2,664**.

**GitNexus (Tier-2 graph — on-demand, disposable).** ONE index you query: **`SUDO_COMMAND`** = the command
center itself — all of `.agents/` (rules · workflows · commands · skills · scripts). Rooted directly at
`.agents/` (with `--skip-git`) to bypass GitNexus's dot-folder skip. This is "the one everything points to,"
not the pointer/adapter copies (`.claude/`/`.opencode/` mirrors are excluded). Re-index after editing any
rule/workflow (no commit-tracking, so do it manually):
`$env:GITNEXUS_NO_GITIGNORE="1"; gitnexus analyze .agents --skip-git --index-only --name SUDO_COMMAND -f`.
Tier-2/disposable — the maps above stay canonical (see `_my_resources/.../gitnexus-usage-guide.md`).
> Note: the markdown rule/workflow files yield few cross-file edges (GitNexus extracts headings, not
> doc references) — the graph is strong for the `.py`/`.ps1` scripts, thin for the prose; trust the files for
> "what references what." No project source is indexed here (projects are cherry-picked as their own repos).
>
> **Doc wiring (the prose layer GitNexus misses):** `docs/doc-graph.md` (+ `doc-graph.json`) is the owned,
> deterministic, no-LLM map of which `.md` references which across `.agents/` — hubs, plus a broken-path /
> ambiguous-ref report. Rebuild after editing rules/workflows:
> `python .agents/scripts/generate_doc_graph.py`. Source: `.agents/scripts/generate_doc_graph.py`.

**Drift:** checked at SessionStart by `.agents/scripts/check-repo-map-drift.ps1 -MapPath docs/repo-map.md` — it
nags if a new top-level folder isn't named here. Rebuild the AUTO body:
`python3 .agents/scripts/generate_repo_map.py --root . --mode content --ignore Projects,_my_resources` (`--root .` is required here — the master generator lives at `.agents/scripts/`, so its default root would otherwise resolve to `.agents/`; the default output is `docs/repo-map.md`).
<!-- REPO-MAP:CURATED-END -->

<!-- REPO-MAP:AUTO-START -->
<!-- generated by scripts/generate_repo_map.py — do NOT hand-edit this block;
     mode=auto, collapse-threshold=8 files. Edit the CURATED block above. -->

```text
Sudo_Hatter_Command/
  _bmad/
    _config/
        bmad-help.csv
        files-manifest.csv
        manifest.yaml
        skill-manifest.csv
    bmm/
        config.yaml
        module-help.csv
    core/
        config.yaml
        module-help.csv
    custom/
        bmad-dev-story.toml
        bmad-quick-dev.toml
        bmad-testarch-atdd.toml
        bmad-testarch-automate.toml
        config.toml
    scripts/
        memlog.py
            def now()
            def resolve(args)
            def split(text)
            def render(meta, body)
            def touch(meta)
            def write_atomic(path, text)
            def entry_count(body)
            def ack(path, body)
            def cmd_init(args)
            def cmd_append(args)
            def cmd_set(args)
            def add_target(sp)
            def main(argv)
        resolve_config.py
            def load_toml(file_path, required)
            def _detect_keyed_merge_field(items)
            def _merge_by_key(base, override, key_name)
            def _merge_arrays(base, override)
            def deep_merge(base, override)
            def extract_key(data, dotted_key)
            def main()
        resolve_customization.py
            def find_project_root(start)
            def load_toml(file_path, required)
            def _detect_keyed_merge_field(items)
            def _merge_by_key(base, override, key_name)
            def _merge_arrays(base, override)
            def deep_merge(base, override)
            def extract_key(data, dotted_key)
            def write_json_stdout(output)
            def main()
    tea/
      workflows/
        testarch/
            README.md
        config.yaml
        module-help.csv
      config.toml
      config.user.toml
  _bmad-output/
    brainstorming/
      brainstorm-tdad-integration-2026-07-07/
        INDEX.md
    forge/
      aviationchat-prd/
  _routing-canary/
    control/
        INDEX.md
        agent.md
    skills/
        INDEX.md
        skill.md
      AGENTS.md
      CLAUDE.md
      GEMINI.md
      Power.md
      README.md
      agent.md
  docs/
      [9 files: .mdx8, .jsonx1 | e.g. AGENTS.md]
  scratch/
      find_brainstorm.py
    AGENTS.md
    CLAUDE.md
    GEMINI.md
    check_maps_output.txt
    opencode.json
    requirements-tdad.txt
    requirements.txt
    router.md
```
<!-- REPO-MAP:AUTO-END -->
