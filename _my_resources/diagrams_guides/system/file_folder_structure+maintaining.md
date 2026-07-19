# The Home-Base System — Guide & Overview

> **What this is.** The one-stop guide to what we built in `Sudo_Hatter_Command` and how it works: a
> **folder-as-workspace routing system** where the folder is the app, markdown is the program, and the
> model *becomes* the agent each workspace describes. This is the living overview; the deeper docs it
> sits on top of:
>
> | Doc | Role |
> |---|---|
> | `_my_resources/youtube_transcripts/implementation-plan_folder-as-workspace-routing-system.md` | the **theory** (mentor transcript, distilled) |
> | `_my_resources/docs/master-implementation-plan.md` | the **rollout record** (how it got built) + evolution log (§8) |
> | `docs/workspace-standard.md` | the **standing spec** (PATH CONTRACT, tier model, upkeep rules) |
> | `.agents/workflows/update-maps-indexes.md` | the **maintenance workflow** (how it stays honest) |
> | *this file* | the **guide & overview** (read this first) |

---

## 1. The idea in one paragraph

Never load what the task doesn't need — that's the whole game. Instead of one mega-prompt or N
hard-coded agents, the system is a tree of folders where every workspace answers three questions the
moment an agent enters: **MAP** (where am I, where can I go), **MISSION** (what is the work here), and
**SUPPORT** (what tools/rules/skills to pull). Entry files auto-load, a router dispatches, routing
tables say *read this / skip that / use skill Z*, and everything persists to files **we** own — not a
vendor's memory. It works identically in Claude Code, opencode, and Antigravity/Gemini because the
brain is always `AGENTS.md` and each LLM's front door is a one-line adapter.

## 2. The home base at a glance

```mermaid
flowchart TD
    subgraph LOBBY ["Sudo_Hatter_Command — LOBBY (own git repo)"]
        ADP["CLAUDE.md / GEMINI.md\n(one-line adapters to AGENTS.md)"]
        BRAIN["AGENTS.md — the brain\nroot law, Map/Mission/Support, gates"]
        ROUTER["router.md\nmaster map: categories to projects"]
        ADP --> BRAIN
        BRAIN --> ROUTER
    end

    subgraph TOOLKIT [".agents/ — MASTER TOOLKIT (single source of authorship)"]
        RULES["rules/\nconstitution, karpathy, artifacts-always-first,\ngit-policy, lobby-search, mobile-mode"]
        SCRIPTS["scripts/\ncheck_maps.py (linter)\nsync-agents.ps1 · record_map_changes.py"]
        CMDS["commands/ + workflows/\nINDEX.md (command registry)\nupdate-maps-indexes.md (the workflow)"]
        OTHER["skills/, templates/, bmad/"]
    end

    subgraph MEM ["_artifacts/ — SHARED MEMORY (you own it)"]
        LAW["AGENTS.md (local law) + adapters\n(auto-attached at point of contact)"]
        INDEX["INDEX.md (session ledger, depth-2)\n+ INDEX-archive.md (pruned history)"]
        DEPTH3["_main/INDEX.md, (project)/INDEX.md,\n(epic)/INDEX.md, tea/INDEX.md\n(depth-3, per-bucket session indexes)"]
        STORE["active-context.md + session folders"]
    end

    DOCS["docs/\nAGENTS.md (local law) + adapters\nworkspace-standard.md (the WHAT)\nrepo-map.md (hybrid nav index)"]
    MYRES["_my_resources/\nDaniel's personal area (Tier-2 law)\nopen_tasks/ read-only carve-out"]
    BMADL["_bmad/ + _bmad-output/\nBMAD module + state (lobby)"]
    CANARY["_routing-canary/\nrouting regression check"]
    SYS["_system/\nbuilder: /new-project, /sync-agents"]
    SETTINGS[".claude/settings.json + .mcp.json\nhooks + MCP servers (gitnexus, md-feedback)"]
    PROJ["Projects/(name)/ — nested git repos, gitignored\neach: adapters + AGENTS.md + vendored .agents/"]

    BRAIN --> TOOLKIT
    BRAIN --> MEM
    BRAIN --> DOCS
    BRAIN --> MYRES
    BRAIN --> BMADL
    BRAIN --> CANARY
    BRAIN --> SYS
    BRAIN --> SETTINGS
    ROUTER --> PROJ
    TOOLKIT --> PROJ
```

## 3. How an agent finds its way (the routing walk)

1. **Auto-load.** The harness injects the front door: `CLAUDE.md` (Claude) or `GEMINI.md` (Gemini) —
   one line: *read `AGENTS.md`*. Codex/opencode read `AGENTS.md` natively. One brain, many doors.
2. **Root law.** `AGENTS.md` is numbered for skip-to-N: `1 START HERE` · `2 MAP/MISSION/SUPPORT` ·
   `3 ALWAYS-LOAD` (only `constitution.md` + `karpathy-guidelines.md` + `artifacts-always-first.md`) ·
   `4 WHAT LIVES WHERE` · `5 NAMING & ARTIFACT PLACEMENT` · `6 GATES` · `7 PERSISTENCE` · `8 PORTABILITY`.
3. **Route.** A "what should I work on / whose is this" question → `router.md` — the lobby directory,
   **categories only** (detail lives on each floor). Every floor routes back up: *if it's not here, go
   back to the root router* — an agent can never dead-end.
4. **Become the agent.** The target workspace's `AGENTS.md` (Layer 2) carries its own
   Map/Mission/Support and the **routing table** — the single most important thing in the system:
   *task → read these / skip these / skills*. Rules and skills (Layer 3) load only when a table row
   calls them.

**The reading-order rule (root law §1.7):** entering any folder — if it carries an `AGENTS.md`, read
that FIRST (the local law: how to *act* here); read `INDEX.md`/`README.md` only when you need the
*inventory*. They are complements: `AGENTS.md` = behavior, `INDEX.md` = contents.

### The folder-file tier model (which folders get an `AGENTS.md`)

| Tier | What | Folders | Carries |
|---|---|---|---|
| **1 — Floors** | work happens here | lobby root, each `Projects/(name)/`, `_system/`, `_routing-canary/`, `.agents/` | full `AGENTS.md` (brain) + 1-line adapters |
| **2 — Guarded infrastructure** | rules apply here, work doesn't | `_artifacts/`, `_my_resources/`, `docs/` | ~15-line **local-law `AGENTS.md`** + 1-line adapters |
| **3 — Leaf content** | storage | epic buckets, session folders, `diagrams_guides/`, transcripts | `INDEX.md`/`README.md` only — **no** `AGENTS.md` |

**Why the adapters give this teeth** (auto-attach — no reliance on the model choosing to read):

```mermaid
flowchart LR
    TOUCH["agent touches ANY file\nunder a Tier-2 folder"] --> AUTO["harness auto-attaches the nested adapter\n(Claude Code: CLAUDE.md - Gemini: GEMINI.md\nCodex: nested AGENTS.md natively)"]
    AUTO --> LAW["adapter points at the folder's\nAGENTS.md = the LOCAL LAW"]
    LAW --> ACT["agent acts by the local law\n(e.g. _my_resources = READ-ONLY,\n_artifacts = bucket + epic-nesting rules)"]

    classDef law fill:#d4f7d4,stroke:#2e7d32,color:#000
    class LAW,ACT law
```

A Tier-2 `AGENTS.md` is a *digest that points at canon* — never a second canonical copy. Not every
folder gets one: boilerplate in every hop burns tokens, drifts, and kills the beacon.

## 4. Where work lands (artifacts + persistence)

**The plan-first lifecycle every task runs:**

```mermaid
flowchart TD
    REQ["Task arrives"] --> RES["1. Research (read-only)"]
    RES --> PW["2. Write implementation_plan.md\npick bucket by where you work FROM"]
    PW --> GATE{"3. STOP — did Daniel say 'approved'?"}
    GATE -- "No" --> WAIT["wait / revise (no file edits)"]
    GATE -- "Yes" --> EX["4. Execute with live TodoWrite"]
    EX --> CL["5. Close: ONE walkthrough.md\n(ends: Task Checklist + Your Actions)\n+ INDEX row + active-context hand-off"]
    CL --> MAPS["6. Run /update-maps-indexes if structure changed\n(depth-3 INDEX, repo-map, linter)"]
    CL --> GIT["GIT: hand Daniel the exact command\nnever commit/push yourself unless delegated"]

    classDef gate fill:#fff3d6,stroke:#b8860b,color:#000
    class GATE,GIT,MAPS gate
```

**Bucket rule — artifacts go where you work FROM (your cwd):**
- Project work from the lobby → `_artifacts/(project-folder-name)/` (e.g. `_artifacts/AGY_AVIATIONCHAT/`)
- Main / home-base / cross-project → `_artifacts/_main/`
- Stories → nest under the parent epic: `(epic)/(story)/` — the epic folder houses its stories
- Inside a project → that project's own `_artifacts/` (its rules, not the lobby ledger)
- opencode → the same rules inside its `_artifacts/opencode/` namespace

**Persistence (pick up / hand off):** *"pick up"* reads a read-only continuity brief from the right
`active-context.md` (+ surfaces `_my_resources/open_tasks/todo_list.md`, READ-ONLY); *"hand off"*
prepends one dated block to the brief, appends one `INDEX.md` row, and reads it back to verify. Memory
lives in **our files**, not the vendor's — survive any context reset, switch LLMs freely.

**Pruning is a MOVE, never a delete** (verified 2026-07-09 end-to-end): old brief blocks →
`active-context-archive.md`; old ledger rows → `INDEX-archive.md`; consumed maps-journal lines →
`.maps-journal-archive.jsonl` (the script appends to the archive *before* rewriting the live file).
History stays readable — just out of the hot path.

## 5. The two-layer INDEX contract (depth-2 + depth-3)

```mermaid
flowchart LR
    subgraph D2 ["DEPTH-2 (every workspace)"]
        WS_INDEX["workspace-root/INDEX.md\ncommand + artifact ledgers"]
        REPO_MAP["docs/repo-map.md\nhybrid: curated header + AUTO body"]
    end

    subgraph D3 ["DEPTH-3 (_artifacts/ only)"]
        BUCKET["_artifacts/(bucket)/INDEX.md\nper-bucket session index"]
        EPIC["_artifacts/(epic)/INDEX.md\nper-epic story index"]
        MAIN["_artifacts/_main/INDEX.md\nhome-base session index"]
    end

    D2 -->|"check_maps.py checks both"| D3
    D3 -->|"triggered when a bucket has\n>= 2 session subfolders"| BUCKET

    classDef depth3 fill:#d4f7d4,stroke:#2e7d32,color:#000
    class BUCKET,EPIC,MAIN depth3
```

**Why depth-3 only for `_artifacts/`:** session folders are content-rich (bug-tracking history, story
context). Code dirs use GitNexus + the repo-map AUTO block instead — a depth-3 INDEX there would just
duplicate what the graph already indexes.

## 6. How it stays honest (the maintaining system)

Four pieces: the **linter** (detect), the **recorder** (pre-scope), the **workflow** (reconcile), and
the **hooks** (nag).

```mermaid
flowchart TD
    subgraph LINTER ["check_maps.py — 9 checks (+ 2.5 level-2 INDEX)"]
        C1["1. AUTO-block freshness\n(mode-preserving regen + diff)"]
        C2["2. path existence\n(map/INDEX table-row paths resolve)"]
        C3["3. top-level folder coverage"]
        C4["4. git baseline\n(renames since last anchor)"]
        C5["5. context hygiene\n(prune nag — HINT only)"]
        C6["6. structure conformance\n(PATH CONTRACT gate)"]
        C7["7. depth-3 _artifacts INDEX\n(missing/stale per-bucket)"]
        C8["8. tier-2 local law\n(AGENTS.md + redirecting adapters — HINT only)"]
        C9["9. gitnexus index freshness\n(meta.json lastCommit == HEAD — HINT only)"]
    end

    REC[".githooks/post-commit\nrecord_map_changes.py\nclassifies each commit into a journal"]
    REC -->|"docs/.maps-journal.jsonl\n(cache, never the truth)"| WORKFLOW

    HOOK["SessionStart hooks\n(.claude/settings.json)\nClaude Code only"]
    HOOK -->|"depth-3 nag + journal nag\n(non-fatal)"| C7

    WORKFLOW["/update-maps-indexes command\nthe reconciliation workflow"]
    WORKFLOW -->|"Step 3: audit all checks"| LINTER
    WORKFLOW -->|"Step 5: fix drift\nregen AUTO (mode-preserving)\nadd missing depth-3 INDEXes\nprune (MOVE to archives)"| LINTER
    WORKFLOW -->|"Step 6: commit per repo\n+ --set-anchor (consumes journal)"| ANCHOR["docs/.maps-state.json\nbaseline for next drift check"]

    classDef hook fill:#fff3d6,stroke:#b8860b,color:#000
    classDef depth3 fill:#d4f7d4,stroke:#2e7d32,color:#000
    class HOOK,REC hook
    class C7,C8,C9 depth3
```

### check_maps.py flags

| Flag | What it does |
|---|---|
| `--all` | Run all 9 checks (+ the unnumbered level-2 INDEX presence check, "2.5") across all conformant workspaces |
| `--depth3-only` | Run ONLY check 7 (depth-3 INDEX); exits 0 always — for the SessionStart nag |
| `--set-anchor` | Write current state to `docs/.maps-state.json` + consume the maps-journal (run AFTER committing) |
| `--ignore <dirs>` | Skip dirs (lobby: `Projects,_my_resources`; projects: `_my_resources,_bmad`) |

**Fan-out:** run from the home base, `/update-maps-indexes` reconciles the lobby **and every conformant
project** in one pass (each repo commits + re-anchors separately). Run inside a project, it does just
that workspace.

### The four SessionStart hooks (Claude Code only) + one PreToolUse guard

| # | Hook | What it does |
|---|---|---|
| 1 | continuity + gate + repo-map | Injects `_artifacts/_main/active-context.md`, the artifacts/git gate text, AND the full `docs/repo-map.md` |
| 2 | repo-map drift check | `check-repo-map-drift.ps1` — nags on top-level folders on disk but missing from the map |
| 3 | depth-3 nag | Runs `check_maps.py --depth3-only` — surfaces drift without blocking |
| 4 | maps-journal nag | Runs `record_map_changes.py --nag` — pre-scoped drift worklist since the last anchor |
| PT | git push approval | PreToolUse on Bash: `.claude/hooks/require-push-approval.py` guards agent `git commit`/`push` |

> **Platform note:** hooks fire only on Claude Code. opencode and Antigravity/Gemini get the full
> linter when `/update-maps-indexes` runs.

### The routing canary (`_routing-canary/`)

The smallest thing that proves the routing mechanism works in any tool: paste ONE entry-file path into
a fresh agent with no other text → it hops adapter → `agent.md` → `control/` → fetches words from a
skill file → writes `Power.md` == `control your agent` → replies "done boss". **Re-run it whenever
routing structure changes** (root `AGENTS.md`, `router.md`, the adapter pattern) or when qualifying a
new LLM/CLI; reset `Power.md` to its placeholder after. (Last green: 2026-07-09, post root-law slim.)

## 7. One rule set, one source (the anti-drift model)

```mermaid
flowchart LR
    EDIT["Edit rules HERE only"] --> SRC[".agents/ (master = single source)"]
    SRC -->|"/sync-agents vendors copies"| LOBBY[".claude/ and .opencode/ (lobby)\n+ opencode global cache\n+ Antigravity global cache"]
    SRC -->|"/sync-agents vendors copies"| PROJ["Projects/(name)/.agents/\n+ .claude/ + .opencode/"]
    NEVER["NEVER hand-edit a vendored copy\nproject-specific rules go in constitution.project.md"] --> PROJ

    classDef warn fill:#fff3d6,stroke:#b8860b,color:#000
    class NEVER warn
```

- **The loop:** edit master `.agents/` → `/sync-agents` (or `/sync-agents <project>`) → byte-identical
  copies land on all three platforms + the projects.
- **Fresh_Workspace_BMAD is the living template** — every new project clones it (`<PROJECT_NAME>`
  placeholders, one find-replace). Any structural change at the home base must land in Fresh
  (`living-template-sync` rule; `/sync-agents` auto-flags Fresh drift). `/new-project` scaffolds and
  registers a new workspace in `router.md`.
- **Lobby-only search gotcha:** from the lobby root, Grep/Glob are **blind to `Projects/`** (ripgrep
  honors the lobby `.gitignore`). Point Grep at `Projects/<name>` or sweep with Bash `find`. Full
  mechanics → `.agents/rules/lobby-search.md`.

## 8. The git model (locked)

- **Desktop default:** agents never run `git commit`/`push` — the walkthrough's "Your Actions" hands
  Daniel the exact command (explicit paths, never `git add -A`). Exception: an explicitly delegated,
  per-action commit. Enforced by the PreToolUse hook.
- **Branch model:** all dev on `main_debug`; `main` is protected — promoting `main_debug` → `main` is
  Daniel's deliberate manual act. `/merge_main_debug` IS the per-action merge approval.
- **Web/mobile** (`CLAUDE_CODE_REMOTE=true`): the agent owns git delivery instead → `mobile-mode.md`.
- Each project is its **own repo** — one commit per touched repo, never cross-commit.

## 9. The MD Feedback review loop

Daniel annotates any `.md` (plan, walkthrough, draft) in VS Code — highlight / fix / question — and
says **"review"**. The agent then: returns to that document, reads the annotations (via the
`md-feedback` MCP server or the `<!-- USER_MEMO -->` blocks), addresses fixes and answers questions,
and resolves memos **only through the MCP tools** (`apply_memo`, `batch_apply`) — never by hand-editing
the HTML blocks (that corrupts tracking hashes).

**Where the server is wired (2026-07-09):** every workspace (lobby, AGY_AVIATIONCHAT,
Fresh_Workspace_BMAD) carries it in all four config surfaces — root **`.mcp.json`** (what Claude Code
actually reads), plus `.claude/mcp.json`, `.opencode/mcp.json`, `.antigravity/mcp.json`. Requires
Node 18+ (`npx -y md-feedback`). New/changed servers appear after a session restart + approval.

## 10. Workspace status (which repos are conformant)

| Workspace | Conformant? | repo-map mode | Notes |
|---|---|---|---|
| Lobby (home base) | ✅ Yes | `content` | ignore `Projects,_my_resources`; `_bmad/custom/` guard + dialect tomls (2026-07-09 — guards direct lobby-rooted BMAD runs) |
| AGY_AVIATIONCHAT | ✅ Yes | `content` | ignore `_my_resources,_bmad`; project rules in `constitution.project.md`; `_bmad/custom/` guard + TDAD dialect tomls (2026-07-09) |
| Fresh_Workspace_BMAD | ✅ Yes | `auto` | ignore `_my_resources,_bmad`; **the living template — born enforcing since 2026-07-09**: armed TEA gate (`_bmad-output/sudo-tests.yaml`), CI gating `main`+`main_debug` (`pr-check.yml`), BDD layer (`backend/tests/features/` + self-binding `tests/bdd/steps_*.py`), `_bmad/custom/` guard + dialect tomls + resolver scripts |
| BRKN_Tattoos | ⏳ active | — | active in `router.md`; conformance not yet audited |
| RAG_Pipeline_AC (AviationChat ingestion) | ❌ No | — | needs `/new-project` or manual standardization |
| B-L-WorldWide · NEXGen-Films · OpenChat-Openrouter | ❌ pending | — | registered in `router.md`, not yet converted |

## 11. Quick-reference: key files

| Path | What it is |
|---|---|
| `AGENTS.md` (root) | The brain — root law §1–§8, always loaded |
| `router.md` | The master map — categories → workspaces, routes up & down |
| `docs/workspace-standard.md` | The WHAT — structure contract (PATH CONTRACT, tier model, depth-3 rule, end-of-task checklist) |
| `_artifacts/AGENTS.md` · `_my_resources/AGENTS.md` · `docs/AGENTS.md` | Tier-2 local law (+ adapters) — auto-attached at point of contact |
| `.agents/workflows/update-maps-indexes.md` | The HOW — reconciliation workflow (audit → fix → commit → anchor) |
| `.agents/scripts/check_maps.py` | The linter — 9 checks + unnumbered 2.5 + `--depth3-only` + `--set-anchor` |
| `.agents/scripts/sync-agents.ps1` | The propagator — mirrors master `.agents/` to all platforms + projects (**excludes `_bmad/`** — see next row) |
| `_bmad/custom/*.toml` + `_bmad/scripts/resolve_*.py` (projects only) | The BMAD guard layer — plan-first + artifact-insurance overrides (`bmad-dev-story`/`quick-dev`), TDAD dialect pins (`bmad-testarch-atdd`/`automate`, pytest-bdd + automate-evidence `on_complete`). Lives in ALL THREE repos (lobby included — direct BMAD skill runs from the lobby seat bind `{project-root}` to the lobby, Daniel's management lane; the sudo story flow binds to the child project). Propagates ONLY by cloning Fresh or 3-way hand-copy — never `/sync-agents` |
| `.agents/rules/lobby-search.md` | The lobby search gotcha (Grep/Glob blind to `Projects/`) — mechanics |
| `docs/repo-map.md` | Hybrid nav index (curated header + AUTO body) — per workspace |
| `_artifacts/INDEX.md` | Depth-2 session ledger — per workspace |
| `_artifacts/(bucket)/INDEX.md` | Depth-3 per-bucket session index — created at ≥ 2 session subfolders |
| `.claude/settings.json` · `.mcp.json` | 4 SessionStart hooks + PreToolUse git guard · MCP servers (gitnexus, md-feedback) |
| `docs/.maps-state.json` · `docs/.maps-journal.jsonl` | Drift anchor · commit-time drift journal (cache, never truth) |
| `_routing-canary/` | The routing regression check (README has run + reset instructions) |

## 12. Playbook — when to run what

| Moment | Do |
|---|---|
| Session start (from the lobby) | say **"pick up"** / run `/sudo-boot-sprint-memory` for sprint work — brief + open tasks surface |
| Starting any file-touching task | plan-first: `implementation_plan.md` in the right bucket → STOP for "approved" |
| Closing a task | ONE `walkthrough.md` (Task Checklist + Your Actions) + INDEX row + **"hand off"** |
| After any structural change (folders moved/added, sessions created) | `/update-maps-indexes` — then commit, then `--set-anchor` |
| After editing master `.agents/` | `/sync-agents` (lobby) or `/sync-agents <project>` |
| After changing routing structure (`AGENTS.md`, `router.md`, adapters) | re-run `_routing-canary/` + reset `Power.md` |
| After committing (if check 9 hinted) | `node .gitnexus/run.cjs analyze` in the stale repo |
| Reviewing a doc Daniel annotated | say **"review"** → md-feedback loop (§9) |
| Adding a new project | `/new-project <name>` — scaffold from Fresh, register in `router.md` |
