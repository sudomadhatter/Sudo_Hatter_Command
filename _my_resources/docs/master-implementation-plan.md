---
title: Sudo_Hatter_Command Home Base — Master Implementation Plan
subtitle: Folder-as-Workspace Routing System
type: reference-doc
date: 2026-06-24
status: built-live — historical rollout record + evolution log (§8)
owner: Daniel
sources:
  - youtube_transcripts/main_script_for_structure.md            # Jake Van Cleef — the spec
  - youtube_transcripts/script_for_structure.md                 # reaction — operating mechanics
  - youtube_transcripts/implementation-plan_folder-as-workspace-routing-system.md  # theory: Strategy + PRP + Plan
  - ~/.claude/plans/swift-herding-pillow.md                     # approved applied plan
---

# Sudo_Hatter_Command Home Base — Master Implementation Plan

> **What this is.** The theory doc (`youtube_transcripts/implementation-plan_folder-as-workspace-routing-system.md`)
> is the *generic spec*. This master plan is that spec **realized in Daniel's real environment**: multiple
> existing projects, multiple tools (Claude Code / opencode / Antigravity-Gemini), BMAD, a `Projects/`
> container, one git repo per project, and a shared `_artifacts/` memory. Where the theory says
> "workspace-a / router.md / _memory," this says "Projects/clean-bmad-workspace / router.md / _artifacts."

> **How to read this doc (added 2026-07-09).** §0–§7 are the **historical rollout record** — kept for
> lineage (only the worst-drifted lines corrected in place). The **standing spec** for how workspaces are
> shaped and maintained is `docs/workspace-standard.md`; refinements since the rollout land in §8 (the
> evolution log); §9 is current strategy. Old→new names: see the §8 preamble.

---

## 0. Locked decisions

| Decision | Choice |
|---|---|
| Home base | `C:\Sudo_Hatter_Command\` is the lobby + its own git repo |
| Master toolkit | `C:\Sudo_Hatter_Command\.agents\` = single source of authorship (rules, commands, skills, workflows, bmad, scripts, templates) |
| Sharing mechanism | **Routing/pointer files** (transcript-faithful) for the semantic layer; **`/sync-agents` vendors copies** into each tool dir / repo so clones are self-contained. opencode also points natively via `opencode.json`. **No junctions.** |
| Shared memory | One master `C:\Sudo_Hatter_Command\_artifacts\` — every agent (any tool, any project) reads/writes here. Absorbs the theory's `_memory/`. |
| Project container | Projects move to `C:\Sudo_Hatter_Command\Projects\<name>\` (per-project move during conversion, with path-fix + `.venv` recreate). |
| Reference donor | `aviationChat-AGY` (most up-to-date) — we **copy** its rules/commands/skills into the master; convert it **last**. |
| First conversion | `clean-bmad-workspace` (safe baseline) — proves the recipe. |
| IDE reality | Antigravity is the IDE → markdown-routing only; nothing depends on a Claude-only feature. |
| Rollout | Top first, then `clean-bmad-workspace`, then the rest, aviationChat last. |

---

## 1. Theory → applied mapping

| Theory concept (generic) | Realized here (applied) |
|---|---|
| `workspace-root/` | `C:\Sudo_Hatter_Command\` (the lobby) |
| `CLAUDE.md` = one-line adapter | Same. Plus `GEMINI.md` adapter for Antigravity/Gemini. Both say "read `AGENTS.md`." |
| `AGENTS.md` = lobby (root law, start-here, Map/Mission/Support, naming, gates) | Same — the universal entry; references shared rules in `.agents/rules/` by path. |
| `router.md` = master map, categories→workspaces, routes up & down | **New root file.** Categories → `Projects/<name>`; each workspace routes back up to it. |
| Layer-3 `skills/` referenced only where needed | `.agents/skills/` (BMAD + dev skills), pulled per workspace routing table. |
| `_memory/` (active-context + handoffs, numbered) | **Folded into `_artifacts/`**: `_artifacts/<ws>/active-context.md` + session folders + global `INDEX.md` ledger. |
| `_routing-canary/` routing smoke test | `C:\Sudo_Hatter_Command\_routing-canary\` — permanent model-agnostic CI (Claude + opencode + Antigravity). |
| `_system/` builder agent | The home base itself: `.agents/commands/{new-project,sync-agents}` + `.agents/scripts/` + `.agents/templates/project-template/` (+ a `_system/AGENTS.md` builder note). |
| Workspace `AGENTS.md` + routing table | Each `Projects/<name>/AGENTS.md`: Map/Mission/Support + task→read/skip/skills table + "go up to `../../router.md`." |
| Naming-conventions-as-database | Documented in root `AGENTS.md`; `_artifacts/INDEX.md` is the scannable ledger. |
| Pickup / Handoff codewords | Implemented against `_artifacts/` (read-only brief / write+verify). |
| Gates (routing + risk) | Surfaced in root `AGENTS.md`, backed by `.agents/rules/constitution.md`. |
| Start small (2 workspaces before scaling) | Prove on `_routing-canary` + `clean-bmad-workspace` before the rest. |

**Net new vs the earlier applied plan:** add `router.md` (split from AGENTS.md), the Map/Mission/Support
framing, the `_routing-canary/` CI, numbered skip-to-N memory sections, and an explicit `_system/` builder note.

---

## 2. Target structure (applied)

```
C:\Sudo_Hatter_Command\                         ← HOME BASE (lobby) · own git repo
├─ CLAUDE.md        → "read AGENTS.md"            ┐ Layer 1 — entry adapters
├─ GEMINI.md        → "read AGENTS.md"            │
├─ AGENTS.md        = root law · START HERE · Map/Mission/Support · naming · GATES · persistence
├─ router.md        = MASTER MAP: categories → Projects/<name> (routes up & down)
├─ opencode.json    → instructions + skills.paths → .agents/
├─ .gitignore       → ignores Projects/, node_modules, .venv, caches
│
├─ .agents\                  ← MASTER toolkit (single source of authorship)
│   ├─ rules\  commands\  skills\  workflows\  bmad\  scripts\  templates\project-template\
│
├─ docs\                     ← HOME-BASE DOCUMENTATION (workspace-standard.md · repo-map.md; this plan now lives in _my_resources\docs\)
│
├─ _artifacts\               ← SHARED MEMORY (all agents read/write; theory's _memory absorbed)
│   ├─ INDEX.md              ledger: date · workspace · slug · summary · status  (skip-to scan)
│   ├─ _main\                root-level / cross-project session work (formerly _home)
│   └─ <project>\
│       ├─ active-context.md  numbered sections (1 PRIME · 5 PICK UP · 6 HAND OFF)
│       └─ <YYYY-MM-DD>_<slug>\  implementation_plan · walkthrough (ends: Task Checklist + Your Actions) · code-review …
│
├─ _routing-canary\              ← routing CI: CLAUDE→agent→control→skill→Power.md=="control your agent"
├─ _system\                  ← builder note (how to add/maintain workspaces) → AGENTS.md
├─ .claude\  .opencode\      ← LOBBY tool dirs (synced copies of master)
├─ _my_resources\            ← Daniel's personal area (docs\ · youtube_transcripts\ · open_tasks\) — protected, Tier-2 law
│
└─ Projects\                 ← all projects (git-ignored by home base; each its own repo)
    ├─ AGY_AVIATIONCHAT\      pointer CLAUDE/GEMINI → AGENTS.md (workspace) · vendored .agents
    ├─ Fresh_Workspace_BMAD\  (the living template — the first conversion, since renamed)
    ├─ BRKN_Tattoos\  AGY_JETCHAT\  B-L-WorldWide\  NEXGen-Films\  RAG_Pipeline_AC\  OpenChat-Openrouter\
```

---

## 3. Phased rollout

| Phase | Theory phase | Goal | Done when |
|---|---|---|---|
| **A — Spine** | 0 | Root adapters + `AGENTS.md` + `router.md`; `.agents` master (rules/commands/skills/bmad harvested from aviationChat, genericized); `_artifacts/` memory + `INDEX.md`; `opencode.json`; lobby `.claude`/`.opencode` synced; `.gitignore` + `git init`. | Cold session at root reads the entry map and states the structure back; `/sync-agents` + a BMAD command resolve. |
| **A2 — Prove routing** | 1 | Build `_routing-canary/`; run the word test. | `Power.md == "control your agent"` in **Claude, opencode, and Antigravity** with no instruction beyond the entry file. |
| **B — First workspace** | 2–4 | Convert `clean-bmad-workspace`: move into `Projects/` (+path-fix +`.venv` recreate), pointer/`AGENTS.md` with routing table, consume master, register in `router.md`; pickup/handoff via `_artifacts/`. | "work on clean-bmad-workspace" cold-routes from root and inside; out-of-domain routes back up; handoff→pickup round-trips. |
| **B2 — Second workspace** | 2 | Stand up one more workspace (a lightweight 2nd, or `jetChat-AGY`) so routing is proven on **two**. | Two workspaces route cleanly; the negative test routes up, not hallucinate. |
| **C — Scale** | 6 | Roll remaining projects one at a time; **convert aviationChat last**; verify on a 2nd/3rd LLM. | Real work runs here; agent/tool swap loses nothing. |
| **D — Builder** | 5 | `/new-project` + `/sync-agents` + `_system/` note + gates finalized. | Adding a project is a one-command conversation; gates enforced. |

> Phases **A** and **A2** are the "top first" milestone to verify before touching any project.

---

## 4. Key file specs (applied templates)

**`CLAUDE.md` / `GEMINI.md` (every level)** — one line: "Read `AGENTS.md` in this folder and follow it.
Single source of truth." Identical everywhere → one front door per LLM.

**Root `AGENTS.md`** — numbered for skip-to-N:
- `ROOT LAW` (header) — prime mission of the home base.
- `1 START HERE` — you're in the lobby; don't read the tree; routing question → `router.md`; risky action → GATES.
- `2 MAP / MISSION / SUPPORT` — the three answers every task needs.
- `3 ALWAYS-LOAD` — small set only (`constitution.md` + `karpathy-guidelines.md` + `artifacts-always-first.md`); everything else routed on demand (least-context loading).
- `4 WHAT LIVES WHERE` — the home-base infrastructure table.
- `5 NAMING & ARTIFACT PLACEMENT` — dates/versions/slugs; replaces a database (details → `artifacts-always-first.md` §2).
- `6 GATES` — routing + search + risk/git gates → `.agents/rules/constitution.md`.
- `7 PERSISTENCE` — pickup/handoff → `_artifacts/`.
- `8 PORTABILITY` — `AGENTS.md` universal; `CLAUDE.md`/`GEMINI.md` one-line adapters.

**Root `router.md`** — lobby = categories only:

```
| If the work is about… | Go to | Read first |
|---|---|---|
| aviation ground-school app  | Projects/aviationChat-AGY/      | its AGENTS.md |
| clean baseline / sandbox    | Projects/clean-bmad-workspace/ | its AGENTS.md |
| maintaining THIS system     | _system/                       | _system/AGENTS.md |
```
Rule line: "If not listed, ask — don't guess. Any workspace may send you BACK here."

**Workspace `Projects/<name>/AGENTS.md`** — Map/Mission/Support + the routing table (task → read these /
skip these / skills) + "if not here, GO BACK to `../../router.md`." Project-specific rules stay local;
shared rules referenced from the vendored `.agents/rules/`.

**`_routing-canary/`** — `CLAUDE.md`→`agent.md`→`control/agent.md` (write 3 words to `../Power.md`, fetch each
from `../skills/skill.md`: 1=control 2=your 3=agent)→ reply "done boss". Permanent CI; re-runnable any time.

**`_artifacts/` persistence** — `active-context.md` per workspace, numbered: `1 PRIME STATE`, `5 PICK UP`
(5.1 doing / 5.2 changed / 5.3 open / 5.4 blocked / 5.5 next), `6 HAND OFF` (6.1 completed / 6.2 in-progress
/ 6.3 open trade-offs / 6.4 links). `INDEX.md` appends one line per session. **pickup** = read-only brief
from these; **handoff** = write + read-back-verify.

**`/sync-agents` (`.agents/scripts/sync-agents.ps1` + command doc)** — copies `.agents/{commands,skills}`
into a target's `.claude/commands`, `.claude/skills`, `.opencode/command|agent` (markdown only, never
`node_modules`); reports a diff. Run for the lobby and per project. Authorship stays single-source: always
edit `.agents/`, never the copies.

**`/new-project <name>`** — scaffold `Projects/<name>` from `templates/project-template/` (pointer
CLAUDE/GEMINI + `AGENTS.md` skeleton w/ starter routing table + `_artifacts/<name>/`), run
`/sync-agents`, append to `router.md`, add to `.gitignore`, `git init` the new repo.

---

## 5. Validation loop (the "done enough to live in" test)

1. **Routing experiment** passes in **Claude + opencode + Antigravity** (`Power.md == "control your agent"`).
2. **Cold route** from root: "work on clean-bmad-workspace" → light lookup lands in the folder; never "I don't know."
3. **Re-route** mid-session ("never mind, work on <other>") → clean switch, prior state preserved on disk.
4. **Persistence**: handoff → new session → pickup reproduces state from `_artifacts/`.
5. **Token-frugality**: a cold route reads entry map + one router hop + one workspace context — not the tree.
6. **Negative test**: ask a workspace something out of scope → it routes **up** via `router.md`, not hallucinate.
7. **Git isolation**: root `git status` shows only home-base files (no `Projects/`, no `node_modules`); each sub-repo unaffected.

---

## 6. Anti-patterns (actively avoid)

- One mega `AGENTS.md` preloading every workspace/skill (token burn).
- Building a framework/DB — naming conventions + routing + `_artifacts/` ARE the database and app.
- Pre-building N hard-coded agents — the model becomes the workspace's agent.
- All detail in the lobby router — lobby = categories; detail on the floor.
- Model-specific content in shared files — `CLAUDE.md`/`GEMINI.md` stay one-line adapters.
- Skipping pickup/handoff — that re-rents vendor memory.
- Scaling to many folders before routing works on two.

---

## 7. Progress + immediate next steps  (historical — Phase A snapshot, superseded; see §8)

**Done so far (Phase A, partial):** `.agents/{rules,commands,skills,workflows,bmad,scripts,templates}`
created; `_artifacts/_home` created; 12 shared rules harvested into `.agents/rules/`; this master plan
written to `_docs/`.

**Next (on go-ahead) — finish Phase A + A2:**
1. Finish harvest (skills, commands, BMAD core) + genericize `constitution.md` / `git-closeout-commits.md` + repoint `artifacts-always-first` to `_artifacts/`.
2. Write the root spine: `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`, `router.md`, `opencode.json`.
3. Build `_routing-canary/` and run the model-agnostic word test (Claude, opencode, Antigravity).
4. Build `/sync-agents` (+ `/new-project`), wire the lobby `.claude`/`.opencode`.
5. `.gitignore` + `git init` (no commit until Daniel approves).
6. Report for the "top first" verification checkpoint before converting `clean-bmad-workspace`.

---

## 8. Evolution log (refinements since the original build)

> The Phase A–D system above is **built and live** — the frontmatter status line is historical. This log
> records significant refinements made *after* the original rollout, newest first. Current names: the home
> base is the lobby repo; projects are `Projects/AGY_AVIATIONCHAT/` + `Projects/Fresh_Workspace_BMAD/`; the
> home-base cross-project bucket is `_artifacts/_main/` (the old `_home`). Each entry links its full
> walkthrough.

### 2026-07-09 — Docs truth-sync + lobby-search mechanics extracted (lobby)
Audit vs the source transcript passed (R1–R8 met or exceeded); every fix was documentation drift, not
structure: this doc's status line / §2 tree / §4 spec corrected in place (+ this "how to read" banner),
`router.md`'s transcript path fixed, the file/folder guide's hook + workspace tables synced to disk, and
the lobby grep-gotcha **mechanics** moved to `.agents/rules/lobby-search.md` — the §6 SEARCH GATE trigger
stays inline (refines 2026-07-06's "stays inline": trigger-inline, mechanics-routed). `/1_update-maps`
prune verified **move-never-delete** end to end (workflow prose + Step-4 gate +
`record_map_changes.consume()` archives before rewriting). Full detail →
[`_artifacts/_main/2026-07-09_system-docs-truth-sync/walkthrough.md`](../../_artifacts/_main/2026-07-09_system-docs-truth-sync/walkthrough.md).

### 2026-07-06 — Front door leaned + GitNexus block single-sourced (lobby + AGY + Fresh)
Operationalized two of §6's anti-patterns ("no mega `AGENTS.md`", "`CLAUDE.md`/`GEMINI.md` stay one-line
adapters") by **removing duplicated content from the always-loaded front door** — a dedupe, not an extraction
of live rules. Safety invariant held throughout: only trim content whose destination is *already*
always-loaded (`artifacts-always-first.md` is in the §4 load manifest) or is a before-trigger foot-gun that
**stays inline** (the lobby grep-gotcha, the git write gate).

- **Lobby `AGENTS.md`** (16,034 → 13,595 B): §5 naming / §6 git-enforcement / §7 persistence / §8 portability
  trimmed to pointers; the twice-written "Grep is blind to `Projects/`" gotcha deduped to one copy (§4); the
  hand-authored GitNexus scope note relocated *above* the generated block (portable to all three platforms).
- **GitNexus block single-sourced:** kept in `AGENTS.md` (all three platforms read it — opencode + Antigravity
  never read `CLAUDE.md`), **stripped from `CLAUDE.md`**. The block is auto-generated by the `gitnexus`
  CLI, which hardcodes injecting into both files with no per-file toggle → set `.gitnexusrc`
  `"analyze": {"skipAgentsMd": true}` to stop re-injection (freezes the block's cosmetic symbol-count, which
  nothing consumes — real staleness is tracked by `.gitnexus/meta.json` + `check_maps` check-9).
- **`CLAUDE.md` → true bare adapter** (matching `GEMINI.md`): lobby 4,327 → 257 B; AGY 3,643 → 132 B. Because
  `CLAUDE.md` is auto-loaded into the Claude Code system prompt *every session*, this is a recurring per-session
  token win (~7.5 KB across the two repos).
- **AGY_AVIATIONCHAT:** its `AGENTS.md` was already lean (Layer-2 map, pointer-based) → **only** the CLAUDE.md
  block-strip + `skipAgentsMd`. **Fresh_Workspace_BMAD:** already in the target state (no GitNexus block,
  bare `CLAUDE.md`) → no front-door change.
- **Shared rule:** the file-naming micro-conventions (`YYYY-MM-DD_<slug>.md`, `_draft`/`_v2`/`_final`, numbered
  memory sections) relocated into `.agents/rules/artifacts-always-first.md` §2 so the lobby §5 trim lost
  nothing; propagated to both projects' vendored copies → md5-identical ×3.
- Full detail → [`_artifacts/_main/2026-07-06_agents-md-dedupe-triage/walkthrough.md`](../../_artifacts/_main/2026-07-06_agents-md-dedupe-triage/walkthrough.md).

### 2026-07-06 — Commit-time map-drift recorder (lobby + AGY + Fresh)
A recorder that keeps the repo-map / `INDEX` upkeep loop pre-scoped, so the SessionStart nag and
`/1_update-maps` read a ready-made worklist instead of re-deriving "what changed."

- **Pieces (per repo):** `.githooks/post-commit` (non-blocking hook, fires after every commit) →
  `.agents/scripts/record_map_changes.py` (classifier: `--commit HEAD` / `--nag` / `--consume <sha>`) →
  `docs/.maps-journal.jsonl` (the journal — **gitignored / machine-local**, like `.gitnexus/`). SessionStart
  runs `record_map_changes.py --nag`; `check_maps.py --set-anchor` now also **consumes** the journal (archives
  reconciled lines — a move, not a delete).
- **The rule that matters:** the journal is a **cache, never the truth.** Every reader runs a freshness guard
  (journal's last sha == HEAD?); a bypass (another machine, `--no-verify`, rebase) prints "behind HEAD" and
  falls back to `check_maps.py`'s `git diff <anchor>..HEAD` (ground truth).
- **Enable (one-time per repo):** `git config core.hooksPath .githooks`. Already set for the lobby,
  AGY_AVIATIONCHAT, Fresh_Workspace_BMAD. Other `Projects/<name>` need the same 4 steps (vendor the script,
  add the hook, gitignore the journal, add the SessionStart nag). Byproduct: fixed a pre-existing Windows
  cp1252 crash in `check_maps.py`'s depth-3 nag.
- Full detail → [`_artifacts/_main/2026-07-06_maps-recorder/walkthrough.md`](../../_artifacts/_main/2026-07-06_maps-recorder/walkthrough.md).

---

## 9. Files & folders organization strategy

> The canonical, complete spec is `docs/workspace-standard.md`; the auto-surfacing decision layer is the
> **`workspace-structure` skill** (it triggers on any create/move/reorganize/scaffold task). This section is the
> at-a-glance summary — the "guide to files & folder organization strategy."

### Tier model — which folders get a control file
| Tier | What | Gets |
|---|---|---|
| **1 — Floor** (work happens here) | workspace roots: the lobby, each `Projects/<name>/`, `_system/`, `_routing-canary/`, `.agents/` | a full **`AGENTS.md`** (Map/Mission/Support + routing table) + 1-line `CLAUDE.md`/`GEMINI.md` adapters |
| **2 — Guarded infrastructure** | `_artifacts/`, `_my_resources/`, `docs/` | a short local-law **`AGENTS.md`** (~15 lines) + adapters, so the folder's special rules self-enforce |
| **3 — Leaf content** | everything else | **`INDEX.md`** only (inventory), or nothing |

### Reading-order rule
Entering any folder: **if it carries an `AGENTS.md`, read that FIRST** (the local law); read its
`INDEX.md`/`README.md` only when you need the inventory. Only "special instruction" folders carry an
`AGENTS.md` — most don't, and for those `INDEX.md` is the map.

### Adapters + GitNexus stay out of the front door
`CLAUDE.md` / `GEMINI.md` are **always bare one-line adapters** → "read `AGENTS.md`." Nothing model-specific or
heavy in them. GitNexus code-intelligence, where a repo has it, lives in its **own `docs/gitnexus.md`** with a
one-line pointer from `AGENTS.md` — never inline (keeps the always-read front door lean; set `.gitnexusrc`
`skipAgentsMd` so the generator can't re-inject the block).

### Fresh_Workspace_BMAD is the living template
It's the skeleton every new project is cloned + renamed from (`<PROJECT_NAME>` placeholders → one find-replace
on clone). **Any structural change at the home base must land in Fresh** so new projects start current. Rules +
toolkit propagate automatically via `/sync-agents`; front-door + `docs/` + folder-layout changes are
per-workspace and **hand-mirrored** — and `/sync-agents` (lobby) now **auto-flags** when Fresh has drifted.
Codified as the `living-template-sync` rule.
