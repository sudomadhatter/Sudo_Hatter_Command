# File & Folder Structure + Maintaining — System Quick Reference

> **What this is.** A one-look reference to the home-base system: what lives where, and how it stays
> honest. This is the living current-state doc (not a session changelog). Full detail lives in
> `docs/workspace-standard.md` (the WHAT) and `.agents/workflows/1_update-maps.md` (the HOW).

---

## 1. The home base at a glance (what lives where)

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
        RULES["rules/\nconstitution, karpathy, artifacts-always-first,\ngit-policy, mobile-mode"]
        SCRIPTS["scripts/\ncheck_maps.py (7-check linter)\nsync-agents.ps1"]
        CMDS["commands/ + workflows/\nINDEX.md (command registry)\n1_update-maps.md (the workflow)"]
        OTHER["skills/, templates/, bmad/"]
    end

    subgraph MEM ["_artifacts/ — SHARED MEMORY (you own it)"]
        INDEX["INDEX.md (session ledger, depth-2)\n+ INDEX-archive.md (pruned history)"]
        DEPTH3["_main/INDEX.md, (project)/INDEX.md,\n(epic)/INDEX.md, tea/INDEX.md\n(depth-3, per-bucket session indexes)"]
        STORE["active-context.md + session folders"]
    end

    DOCS["docs/\nmaster-implementation-plan.md\nworkspace-standard.md (the WHAT)\nrepo-map.md (hybrid nav index)"]
    CANARY["_routing-canary/\nrouting regression check"]
    SYS["_system/\nbuilder: /new-project, /sync-agents"]
    SETTINGS[".claude/settings.json\n3 SessionStart hooks:\nactive-context + gate + depth-3 nag"]
    PROJ["Projects/(name)/ — nested git repos, gitignored\neach: adapters + AGENTS.md + vendored .agents/"]

    BRAIN --> TOOLKIT
    BRAIN --> MEM
    BRAIN --> DOCS
    BRAIN --> CANARY
    BRAIN --> SYS
    BRAIN --> SETTINGS
    ROUTER --> PROJ
    TOOLKIT --> PROJ
```

---

## 2. The two-layer structure contract (depth-2 + depth-3)

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

**Bucket rule (decided by where you work FROM):**
- Project work → `_artifacts/(project-folder-name)/` (e.g. `_artifacts/AGY_AVIATIONCHAT/`)
- Main / home-base / cross-project → `_artifacts/_main/`
- Stories → nest under the parent epic folder: `(epic)/(story)/`
- opencode → mirror under `opencode/` (e.g. `_artifacts/opencode/_main/`)

---

## 3. The maintaining system (how it stays honest)

Three pieces work together: the **linter** (detect), the **workflow** (reconcile), and the
**SessionStart hook** (nag).

```mermaid
flowchart TD
    subgraph LINTER ["check_maps.py — 7 checks"]
        C1["1. repo-map exists"]
        C2["2. repo-map AUTO in sync"]
        C3["3. INDEX.md exists (depth-2)"]
        C4["4. INDEX rows match folders"]
        C5["5. repo-map drift (new dirs)"]
        C6["6. settings.json hooks present"]
        C7["7. depth-3 _artifacts INDEX\n(missing/stale per-bucket)"]
    end

    HOOK["SessionStart hook #3\n(.claude/settings.json)\nruns --depth3-only\nClaude Code only"]
    HOOK -->|"~50ms, exits 0 (non-fatal nag)"| C7

    WORKFLOW["/1_update-maps command\nthe reconciliation workflow"]
    WORKFLOW -->|"Step 3: audit all 7 checks"| LINTER
    WORKFLOW -->|"Step 5: fix drift\nregen AUTO (mode-preserving)\nadd missing depth-3 INDEXes"| LINTER
    WORKFLOW -->|"Step 6: commit per repo\n+ --set-anchor"| ANCHOR["docs/.maps-state.json\nbaseline for next drift check"]

    classDef hook fill:#fff3d6,stroke:#b8860b,color:#000
    classDef depth3 fill:#d4f7d4,stroke:#2e7d32,color:#000
    class HOOK hook
    class C7 depth3
```

### check_maps.py flags

| Flag | What it does |
|---|---|
| `--all` | Run all 7 checks across all conformant workspaces |
| `--depth3-only` | Run ONLY check 7 (depth-3 INDEX); exits 0 always — for SessionStart nag |
| `--set-anchor` | Write current state to `docs/.maps-state.json` (run AFTER committing) |
| `--ignore <dirs>` | Skip dirs (lobby: `Projects,_my_resources`; projects: `_my_resources,_bmad`) |

### The three SessionStart hooks (Claude Code only)

| # | Hook | What it does |
|---|---|---|
| 1 | active-context injection | Reads the workspace's `active-context.md` into session context |
| 2 | plan-first gate | Enforces the artifacts-always-first gate |
| 3 | depth-3 nag | Runs `check_maps.py --depth3-only` — surfaces drift without blocking |

> **Platform note:** hooks fire only on Claude Code (desktop + web/mobile). opencode and Antigravity/Gemini
> don't have a SessionStart hook system — they get the full linter when you run `/1_update-maps` manually.

---

## 4. One rule set, one source (the anti-drift model)

```mermaid
flowchart LR
    EDIT["Edit rules HERE only"] --> SRC[".agents/ (master = single source)"]
    SRC -->|"/sync-agents vendors copies"| LOBBY[".claude/ and .opencode/ (lobby)\n+ opencode global cache\n+ Antigravity global cache"]
    SRC -->|"/sync-agents vendors copies"| PROJ["Projects/(name)/.agents/\n+ .claude/ + .opencode/"]
    NEVER["NEVER hand-edit a vendored copy\nproject-specific rules go in constitution.project.md"] --> PROJ

    classDef warn fill:#fff3d6,stroke:#b8860b,color:#000
    class NEVER warn
```

**The propagation loop:** edit master `.agents/` → run `/sync-agents` (or `/sync-agents <project>`)
→ byte-identical copies land in all three platforms + both projects. `check_maps.py` is synced the
same way.

---

## 5. The plan-first + git lifecycle (how every task runs)

```mermaid
flowchart TD
    REQ["Task arrives"] --> RES["1. Research (read-only)"]
    RES --> PW["2. Write implementation_plan.md\npick bucket by where you work FROM"]
    PW --> GATE{"3. STOP — did Daniel say 'approved'?"}
    GATE -- "No" --> WAIT["wait / revise (no file edits)"]
    GATE -- "Yes" --> EX["4. Execute with live TodoWrite"]
    EX --> CL["5. Close: walkthrough.md + task-list.md\n+ INDEX row + active-context hand-off"]
    CL --> MAPS["6. Run /1_update-maps if structure changed\n(depth-3 INDEX, repo-map, linter)"]
    CL --> GIT["GIT: hand Daniel the exact command\nnever commit/push yourself unless delegated"]

    classDef gate fill:#fff3d6,stroke:#b8860b,color:#000
    class GATE,GIT,MAPS gate
```

---

## 6. The repo-map hybrid (how the navigation index stays honest)

```mermaid
flowchart TD
    GEN["check_maps.py --regen\n(or generate_repo_map.py)"]
    subgraph MAP ["docs/repo-map.md"]
        CUR["CURATED header (hand-written)\nto-find-X table + knowledge map\nNEVER overwritten"]
        AUTO["AUTO body (between sentinels)\nfolder tree + signatures"]
    end
    GEN -->|"rewrites ONLY the auto block"| AUTO
    GEN --> COL["any dir over 8 files: collapse to 1 summary line"]

    classDef auto fill:#d4f7d4,stroke:#2e7d32,color:#000
    class AUTO auto
```

**Modes (mode-preserving regen):**
- `content` — curated header + AUTO body (lobby, AGY)
- `auto` — fully generated (Fresh_Workspace_BMAD)

---

## 7. Workspace status (which repos are conformant)

| Workspace | Conformant? | repo-map mode | Notes |
|---|---|---|---|
| Lobby (home base) | ✅ Yes | `content` | ignore `Projects,_my_resources` |
| AGY_AVIATIONCHAT | ✅ Yes | `content` | ignore `_my_resources,_bmad`; has project-specific rules in `constitution.project.md` |
| Fresh_Workspace_BMAD | ✅ Yes | `auto` | ignore `_my_resources,_bmad` |
| Ingestion_pipeline_AvCh | ❌ No | — | needs `/new-project` or manual standardization |

---

## 8. Quick-reference: key files

| Path | What it is |
|---|---|
| `docs/workspace-standard.md` | The WHAT — structure contract (PATH CONTRACT table, depth-3 rule, end-of-task checklist) |
| `.agents/workflows/1_update-maps.md` | The HOW — 7-step reconciliation workflow (audit → fix → commit → anchor) |
| `.agents/scripts/check_maps.py` | The linter — 7 checks + `--depth3-only` + `--set-anchor` |
| `.agents/scripts/sync-agents.ps1` | The propagator — mirrors master `.agents/` to all platforms + projects |
| `docs/repo-map.md` | Hybrid nav index (curated header + AUTO body) — per workspace |
| `_artifacts/INDEX.md` | Depth-2 session ledger — per workspace |
| `_artifacts/(bucket)/INDEX.md` | Depth-3 per-bucket session index — created when bucket has >= 2 session subfolders |
| `.claude/settings.json` | 3 SessionStart hooks (active-context + gate + depth-3 nag) — Claude Code only |
| `docs/.maps-state.json` | Drift baseline anchor — set via `--set-anchor` after committing |

**Git policy (locked):** never run `git commit`/`push` yourself — hand Daniel the exact command. The only
exception: Daniel explicitly delegates that specific commit/push in the moment. (Web/mobile sessions:
agent owns git delivery → `mobile-mode.md`.)

**When to run `/1_update-maps`:** after any structural change — new folders, new sessions, moved files,
INDEX drift, repo-map staleness. The linter catches it; the workflow reconciles it.
