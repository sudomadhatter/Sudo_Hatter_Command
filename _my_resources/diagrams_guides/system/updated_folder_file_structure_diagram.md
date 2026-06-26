# Updated Folder / File Structure — System Quick Reference

> **What this is.** A one-look reference to the home-base system and the file-change strategy executed on
> 2026-06-24 (the `workspace-standard-and-repo-map` session). Green = NEW this session, Yellow = CHANGED this
> session, Red = BLOCKED / not done. Full detail lives in
> `_artifacts/_main/2026-06-24_workspace-standard-and-repo-map/` and `_docs/workspace-standard.md`.

---

## 1. The home base at a glance (what lives where)

```mermaid
flowchart TD
    subgraph LOBBY ["Sudo_Hatter_Command — LOBBY (own git repo)"]
        ADP["CLAUDE.md / GEMINI.md\n(one-line adapters to AGENTS.md)"]
        BRAIN["AGENTS.md — the brain\nroot law, Map/Mission/Support, gates\nCHANGED: mandatory artifacts gate + always-load"]
        ROUTER["router.md\nmaster map: categories to projects"]
        ADP --> BRAIN
        BRAIN --> ROUTER
    end

    subgraph TOOLKIT [".agents/ — MASTER TOOLKIT (single source of authorship)"]
        RULES["rules/\nconstitution, karpathy, artifacts-always-first\nCHANGED: git-policy (was git-closeout-commits)"]
        SCRIPTS["scripts/\nNEW: generate_repo_map.py"]
        OTHER["commands/, skills/, workflows/, templates/, bmad/"]
    end

    subgraph MEM ["_artifacts/ — SHARED MEMORY (you own it)"]
        INDEX["INDEX.md (session ledger)"]
        STORE["_main/ and (project)/ and opencode/\nactive-context.md + session folders"]
    end

    DOCS["_docs/\nmaster-implementation-plan.md\nNEW: workspace-standard.md"]
    CANARY["_routing-canary/\nRENAMED from _experiment/\nrouting regression check"]
    SYS["_system/\nbuilder: /new-project, /sync-agents"]
    SETTINGS[".claude/settings.json\nNEW: SessionStart hook"]
    PROJ["Projects/(name)/  — 7 repos, gitignored\neach: adapters + AGENTS.md + vendored .agents/"]

    BRAIN --> TOOLKIT
    BRAIN --> MEM
    BRAIN --> DOCS
    BRAIN --> CANARY
    BRAIN --> SYS
    BRAIN --> SETTINGS
    ROUTER --> PROJ
    TOOLKIT --> PROJ

    classDef new fill:#d4f7d4,stroke:#2e7d32,color:#000
    classDef chg fill:#fff3d6,stroke:#b8860b,color:#000
    class SCRIPTS,DOCS,SETTINGS,CANARY new
    class BRAIN,RULES chg
```

---

## 2. The file-change strategy we just ran (the 6 parts)

```mermaid
flowchart TD
    PLAN["Approved plan:\nworkspace-standard-and-repo-map"]
    PLAN --> F["Part F: RENAME\n_experiment to _routing-canary\n+ fix all references"]
    PLAN --> E["Part E: RECONCILE rules\none git policy, purge _claude_artifacts\nfrom the rule set"]
    PLAN --> A["Part A: STANDARD\nwrite _docs/workspace-standard.md"]
    PLAN --> D["Part D: ORG SCHEME\nbucket rule + random vs epic/story folders"]
    PLAN --> C["Part C: LOBBY PARITY\nAGENTS.md gate + new settings.json hook"]
    PLAN --> B["Part B: GENERATOR\nauthor generate_repo_map.py"]
    B --> PROVE["Proven read-only on ingestion\n514 to 192 lines"]
    B --> BLOCK["NEXT: lab-prove in clean-bmad\n(Daniel's clean-shell template) + propagate"]

    classDef done fill:#d4f7d4,stroke:#2e7d32,color:#000
    classDef blocked fill:#ffd6d6,stroke:#c62828,color:#000
    class F,E,A,D,C,B,PROVE done
    class BLOCK blocked
```

---

## 3. One rule set, one source (the anti-drift model)

The whole reason for the cleanup: rules had forked across copies over months. Now there is one source.

```mermaid
flowchart LR
    EDIT["Edit rules HERE only"] --> SRC[".agents/ (master = single source)"]
    SRC -->|"/sync-agents vendors copies"| LOBBY[".claude/ and .opencode/ (lobby)"]
    SRC -->|"/sync-agents vendors copies"| PROJ["Projects/(name)/.agents/\n+ docs/workspace-standard.md"]
    NEVER["NEVER hand-edit a vendored copy\nproject-specific rules go in constitution.project.md"] --> PROJ

    classDef warn fill:#fff3d6,stroke:#b8860b,color:#000
    class NEVER warn
```

---

## 4. The plan-first + git lifecycle (how every task runs)

```mermaid
flowchart TD
    REQ["Task arrives"] --> RES["1. Research (read-only)"]
    RES --> PW["2. Write implementation_plan.md\npick bucket by where you work FROM: _main OR the project"]
    PW --> GATE{"3. STOP — did Daniel say 'approved'?"}
    GATE -- "No" --> WAIT["wait / revise (no file edits)"]
    GATE -- "Yes" --> EX["4. Execute with live TodoWrite"]
    EX --> CL["5. Close: walkthrough.md + task-list.md\n+ INDEX row + active-context hand-off"]
    CL --> GIT["GIT: hand Daniel the exact command\nnever commit/push yourself unless delegated"]

    classDef gate fill:#fff3d6,stroke:#b8860b,color:#000
    class GATE,GIT gate
```

**Artifact folder naming (the org scheme):**
- Random task: `_artifacts/(workspace)/(YYYY-MM-DD)_(slug)/`
- Story: `_artifacts/(workspace)/(epic)/(story)/`  — epic folder houses all its stories
- Bucket = decided by **where you work FROM** (your cwd): the project's bucket for project work, `_main` for
  home-base/cross-project work. Create the bucket/epic folder if missing. opencode mirrors this under `opencode/`.

---

## 5. The repo-map hybrid (how the navigation index stays honest)

```mermaid
flowchart TD
    GEN["scripts/generate_repo_map.py"]
    subgraph MAP ["docs/repo-map.md"]
        CUR["CURATED header (hand-written)\nto-find-X table + knowledge map\nNEVER overwritten"]
        AUTO["AUTO body (between sentinels)"]
    end
    GEN -->|"rewrites ONLY the auto block"| AUTO
    GEN --> SIG["code dirs: function/class signatures"]
    GEN --> COL["any dir over 8 files: collapse to 1 summary line\n(also makes content workspaces folder-level)"]

    HOOK["SessionStart hook (.claude/settings.json)"]
    HOOK -->|"injects at session start"| MAP
    HOOK --> DRIFT["DRIFT flag if a folder is missing from the map\n(detect-only; human supplies the purpose at end-of-task)"]

    classDef new fill:#d4f7d4,stroke:#2e7d32,color:#000
    class GEN,HOOK new
```

---

## 6. Quick-reference tables

**Key files touched / created this session**

| Path | What it is | Status |
|---|---|---|
| `_docs/workspace-standard.md` | Canonical "how to format + upkeep a workspace" doctrine | NEW |
| `.agents/scripts/generate_repo_map.py` | Hybrid repo-map generator (signatures + collapse + sentinels) | NEW |
| `.claude/settings.json` | Lobby SessionStart hook (injects active-context + gate) | NEW |
| `.agents/rules/git-policy.md` | The one git rule (renamed from `git-closeout-commits.md`) | CHANGED |
| `.agents/rules/constitution.md` + `artifacts-always-first.md` | Reconciled to the git policy + org scheme | CHANGED |
| `AGENTS.md` | Mandatory artifacts gate + always-load + standard reference | CHANGED |
| `_routing-canary/` | Routing regression check (renamed from `_experiment/`) | RENAMED |

**Git policy (locked):** never run `git commit`/`push` yourself — hand Daniel the exact command. The only
exception: Daniel explicitly delegates that specific commit/push in the moment.

**When to run `_routing-canary/`:** after changing routing structure (`AGENTS.md` / `router.md` / the
adapter-skill pattern), or when qualifying a new LLM/CLI. A green run proves the mechanism, not that your real
routing is correct (use the cold-route test for that).

**Done vs Blocked**

| Done (home base) | Blocked / next |
|---|---|
| Rename, rule reconciliation, standard doc, org scheme, lobby gate + hook, generator (proven 514 to 192) | Lab-prove the repo-map in `clean-bmad-workspace` (Daniel's clean-shell template) + propagate to projects |
|  | Retire-list follow-up: autopilot workflow + `1_*` commands still reference `_claude_artifacts/` (engine-coupled) |
|  | Home-base changes are UNCOMMITTED — git command is in the session `walkthrough.md` |
```
