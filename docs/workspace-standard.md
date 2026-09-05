---
title: Workspace Standard — How to Format and Upkeep a Workspace
type: reference-doc
date: 2026-06-24
owner: Daniel
status: canonical
canonical_location: docs/workspace-standard.md (home base; thin projects carry no copy — legacy vendored copies retire at conversion)
sources:
  - _my_resources/research_docs/implementation-plan_folder-as-workspace-routing-system.md  # the theory (design-time input; lives in the thinking space, read only when linked)
  # the one-time rollout doc (_my_resources/docs/master-implementation-plan.md) was RETIRED — deleted in f43c7bf; the rollout is done and this standard is what remains of it
---

# Workspace Standard

> **What this is.** The single, evergreen standard for how every workspace in `Sudo_Hatter_Command` is
> *shaped* and *kept healthy*. The folder-as-workspace routing plan is the theory (§0.5 maps its
> requirements to what is live); the one-time rollout is finished and its plan retired; **this** is the
> standing spec an agent consults whenever it creates, converts, or maintains a workspace. It is
> model-agnostic — it serves Claude, opencode, Antigravity/Gemini, and Codex equally.
>
> **Where it lives.** Canonically at `docs/workspace-standard.md` — the ONE live copy (thin model,
> 2026-08-07: sessions run from the center, so projects no longer carry one). Legacy vendored copies still
> sitting in unconverted `Projects/<name>/docs/` retire at conversion; never hand-edit one.

---

## 0. Principles (the why, in one screen)

1. **Least-context loading.** Never load what the task doesn't need. This is the whole game.
2. **The map is the single source of truth** — one navigable description of structure, auto-loaded, kept current.
3. **Natural-language function routing** — "for this task, read X, skip Y, use skill Z," in English not code.
4. **Composition + transparency** — small plain-markdown files; no hidden state, no DB, no framework.
5. **Persistence by convention** — naming + pickup/handoff files = durable memory *you* own, not a vendor's.
6. **Portability over lock-in** — `AGENTS.md` is the universal contract; `CLAUDE.md`/`GEMINI.md` are one-line adapters.
7. **The folder is the app; the model becomes the agent** — describe the workspace, don't hard-code N agents.
8. **Start small** — prove routing on a little before scaling to a lot (that's what `_routing-canary/` is for).

### 0.5 Lineage — the plan this implements, and where each piece lives now

The design input was the **folder-as-workspace routing plan**
(`_my_resources/research_docs/implementation-plan_folder-as-workspace-routing-system.md`: three layers —
map → workspace context → skills — plus routing up and down, naming-as-database, pickup/handoff, and
`AGENTS.md` as the universal contract). Its requirements are **all live**; the plan's names changed
where the system grew past them. Audited 2026-08-22 (SCC-269). Use this table to answer "is the idea
actually implemented?" without re-deriving it.

| Plan requirement | Live in this repo | Stated in |
|---|---|---|
| **R1** auto-loaded entry map: `CLAUDE.md` → `AGENTS.md` (root law · start-here · naming · gates) | root `CLAUDE.md` + `GEMINI.md` (adapters) → `AGENTS.md` §1 START HERE … §8 PORTABILITY | Part 1 Layer 1 |
| **R2** master router: categories only, routes **up** as well as down, ask-don't-guess | `router.md` — "Lobby = categories only … ASK — don't guess … Any workspace may send you BACK here" | Part 1 Layer 2 (up-route) · Part 2 Router drift |
| **R3** workspace context: Map / Mission / Support + a **routing table** | root `AGENTS.md` §2 (lobby; `router.md` is its table) · each floor's `AGENTS.md` §3 + §6 (e.g. `Projects/AGY_AVIATIONCHAT/`, `Projects/RAG_Pipeline_AC/`) | Part 1 Layer 1 + Layer 2 |
| **R4** skills referenced only where needed, never preloaded | `.agents/skills/<name>/SKILL.md`, pulled by routing-table rows; `opencode.json` `skills.paths` | Part 1 Layer 3 |
| **R5** naming conventions replace a database | root `AGENTS.md` §5 NAMING & ARTIFACT PLACEMENT; floors §7 | Part 1 Layer 1 item 7 |
| **R6** persistence: "pick up" (read-only brief) / "hand off" (write, read back, verify), numbered `_memory/` | root `AGENTS.md` §7; `_artifacts/_main/active-context.md` (`1 PRIME` · `5 PICK UP` · `6 HAND OFF`); project briefs per the PATH CONTRACT. The plan's `_memory/` became **two stores**: the continuity brief (`active-context.md`) and the portable auto-memory (`_artifacts/_memory/`) | Part 1 item 9 · PATH CONTRACT · Part 2 Auto-memory |
| **R7** gates before routing and before risky action | root `AGENTS.md` §6 GATES (routing · project-law · search · risk · worktree · git-write) → `.agents/rules/constitution.md` | Part 1 item 8 |
| **R8** portability: `CLAUDE.md` a pure redirect, nothing model-specific in shared files, ≥2 agents verified | root `AGENTS.md` §8; one command set reaches four platforms via `/smh-sync-agents`; canary runs per tool. ✅ **Exception CLOSED 2026-08-22 (SCC-279)** — root `GEMINI.md` had grown three "GEMINI SPECIFIC HARD RULES"; operator ruling was **FOLD**, and the file is now the house adapter. Nothing was lost: all three were already law every platform loads — explicit staging is `git-policy.md`, worktree-before-edit is `worktree-per-story.md`, and sync scope is `project-law.md` (“`/smh-sync-agents` targets the command center and the machine-global caches only”), which `sync-agents.ps1` enforces by exiting 1 on the retired `-Maintained` flag that rule actually told Gemini to run. Now **checked, not asserted**: `.agents/scripts/tests/test_entry_adapters.py` | Part 1 Layer 1 · Part 2 Command sync |
| `_experiment/` — the routing smoke test | `_routing-canary/` (renamed: permanent regression check, not a demo) | Part 2 Routing canary |
| the deleted _system/AGENTS.md — the system-builder agent | `docs/system-builder.md` (`_system/` dissolved 2026-07-25; `router.md` row "Maintaining THIS home-base system") · `/smh-new-project` adds a workspace by cloning the skeleton | Part 2 Router drift |
| Validation loop (canary · cold-route · persistence · token-frugality · negative/route-up) | all five named in Part 2 "Routing canary — the regression cadence" | Part 2 |
| Anti-patterns (mega `AGENTS.md`; framework/DB; agent-per-task; detail in the lobby; model-specific shared files; skipping pickup/handoff; scaling before routing works) | guarded by: ALWAYS-LOAD tiers (§Layer 1 item 4) · the folder-file tier model · "lobby = categories only" in `router.md` · the canary triggers · the anti-fork rule (Part 2 Rules) | throughout |

**Lobby vs floor numbering.** The §1–§9 shape in Layer 1 below is the **floor** (project) brain. The
**lobby** brain (`AGENTS.md` at the root) runs §1–§8 with a different middle: it carries no routing
table (`router.md` *is* the lobby's table), §4 is WHAT LIVES WHERE (home-base infrastructure), and §8
is PORTABILITY. Both shapes satisfy the same plan requirements; the difference is that the lobby
routes *to* floors and a floor routes *within* itself.

---

## Part 1 — How to FORMAT a workspace

A compliant workspace has these, and nothing it doesn't need.

### Layer 1 — entry + map
- **`CLAUDE.md`** and **`GEMINI.md`** — one-line adapters, identical everywhere: *"Read `AGENTS.md` in this
  same folder and follow it. That is the single source of truth."* Nothing model-specific beyond the name.
  ⛔ **This is a gate, not a convention (SCC-279).** `.agents/scripts/tests/test_entry_adapters.py`
  reads every TRACKED adapter and fails `run_all` on any line that is not the title, the redirect, or
  the house footnote. It exists because root `GEMINI.md` carried three model-specific hard rules and
  `check_maps`' check 8 passed it — that check asks whether the redirect is PRESENT, and it was.
  *Contains the redirect* and *is the redirect* are different claims; only the second is the promise
  above. `_routing-canary/`'s adapters are exempt BY NAME (they point at `agent.md` by design).
- **`AGENTS.md`** — the brain. Numbered sections so agents skip-to-N:
  1. **ROOT LAW / prime mission** — one line: what this workspace exists to do.
  2. **START HERE** — you're in this workspace; don't read the tree; routing question → the routing table /
     the home base's `router.md` (two levels up from inside a project); risky action → GATES.
  3. **MAP / MISSION / SUPPORT** — the three answers every task needs (where am I + where can I go / what is the
     work / what tools+context).
  4. **ALWAYS-LOAD** — three tiers, only the first always-on. **Floor:** `.agents/rules/operator-profile.md`,
     `constitution.md`, `karpathy-guidelines.md`. **Protocol** (the moment a session may touch files, not
     before): `artifacts-always-first.md`, `000-PLAN-FIRST-GATE.md`, `git-policy.md`, `worktree-per-story.md`.
     **On-demand:** everything else, per its trigger. This classification is stated in exactly two live
     places — this section's counterpart in the workspace's `AGENTS.md`, and the `Load` column of
     `.agents/rules/INDEX.md`. They must agree; a rule's frontmatter does **not** declare its own load class.
  5. **ARTIFACTS PROTOCOL — MANDATORY FIRST ACTION** — the plan-first gate, stated up front (see Part 2).
  6. **ROUTING TABLE** — the heart (Layer 2, below).
  7. **NAMING CONVENTIONS** — dates/versions/slugs; replaces a database.
  8. **GATES** — routing gate + risk gate → `.agents/rules/constitution.md`.
  9. **PERSISTENCE** — pickup/handoff → the `_artifacts/` owned by the target workspace (Part 2). **"pick up"
     also surfaces open work from the live Jira board** — `In Progress` → `To Do Next` → `To Do`, first
     non-empty rank wins (root `AGENTS.md` §7 · `.agents/rules/jira.md` §The queue). ⛔ **Never from
     `_my_resources/open_tasks/todo_list.md`** — retired as an agent source (ruling 2026-08-09): it is the
     operator's personal notes, stale by design, and duplicates tickets that already exist.

### Layer 2 — the routing table (the single most important thing)
A plain-English table in `AGENTS.md`: **task → read these / skip these / skills**. It is what makes
least-context loading real. Always include the up-route: *"if what you need isn't here, GO BACK to
the home base's `router.md`"* — **written in the project's own file as the relative path, which from
a project root is two levels up.** Routers route up as well as down — an agent can never dead-end.
(The relative form is described rather than written out because this page lives in the home base, not
in a project: spelled literally it is a path that does not resolve from here, and both `check_links`
and the doc-graph gate correctly read it as broken. Layer 1 above uses the same wording for the same
reason.)

### Layer 3 — skills (referenced, never preloaded)
Skills live in the vendored `.agents/skills/<name>/SKILL.md` and are pulled **only** by the workspace rows
that call them. Never load skills globally.

### The folder-file tier model (which folders get an `AGENTS.md`)
Not every folder gets one — boilerplate in every hop burns tokens and drifts, and if every folder has
one the beacon dies. Three tiers, one reading-order rule:

| Tier | What it is | Carries |
|---|---|---|
| **1 — Floors** (work happens here) | workspace roots: the lobby, each `Projects/<name>/`, `_routing-canary/`, `.agents/` | full `AGENTS.md` (Map/Mission/Support + routing table) + 1-line adapters |
| **2 — Guarded infrastructure** (rules apply here, work doesn't) | `_artifacts/`, `_my_resources/`, `docs/` | a short **local-law `AGENTS.md`** (~15 lines: what this place is, the law, where the detail lives) + 1-line `CLAUDE.md`/`GEMINI.md` adapters |
| **3 — Leaf content** (storage) | epic buckets, session folders, diagrams, transcripts | `INDEX.md` (and/or `README.md`) only — **no** `AGENTS.md` |

**The reading-order rule (codified in every brain's START HERE):** entering any folder — if it carries
an `AGENTS.md`, read that FIRST (how to *act* here); read `INDEX.md`/`README.md` only when you need the
*inventory*. They are complements, not substitutes: `AGENTS.md` = behavior, `INDEX.md` = contents.

**`.agents/` is a Tier-1 floor, and it is linted like one.** It carries the same brain + inventory +
adapters any workspace root does, and each of its subfolders carries an `INDEX.md`. Dot-dirs are
otherwise treated as tool cache and skipped wholesale, so `.agents/` is named in `DOT_CONTENT_DIRS`
(PATH CONTRACT below) to opt it back into the scan. It does **not** index deeper than level 2 — six of
its ten subfolders are flat, `skills/` is self-describing via `SKILL.md` frontmatter, and `bmad/` is
BMAD-owned and regenerated. (`templates/project-template/` was retired 2026-08-07,
SCC-31 — `/smh-new-project` clones the skeleton repo instead.) Depth is not the need there; enforcement is.

**Why the adapters matter at Tier 2:** harnesses auto-attach their nested memory file at the point of
contact — Claude Code injects a subfolder's `CLAUDE.md` the moment it touches any file under it (Codex:
nested `AGENTS.md`; Gemini: hierarchical context files). So the local law self-enforces when an agent
wanders in, with zero reliance on it choosing to read anything. A Tier-2 `AGENTS.md` is a **digest that
points at canon** (the synced rule / the README / the INDEX header) — never a second canonical copy.
Coverage is linted by `check_maps.py` check 8 (non-fatal hint until every workspace carries the files).

### Supporting files every workspace carries
- **`docs/repo-map.md`** — the navigation index (Part 3).
- **`docs/project_overview_guide.md`** (dev workspaces) — **what was BUILT and how a request flows
  through it, for a human.** Distinct from the PRD, which says what was WANTED and is never
  rewritten from this page. Skeleton: [`.agents/templates/project_overview_guide.md`](../.agents/templates/project_overview_guide.md);
  `flowchart` diagrams only. Kept current story-by-story by `/cicd-update-sprint-memory` Step 3.5
  (edit it, or the walkthrough says why not — `closeout_preflight.py`'s `overview` check reads one
  or the other), and it is the index the epic-level PRD reconcile opens at
  `/cicd-push-e2e --after-merge`. A project that has none yet is warned, never blocked.
- **`active-context.md`** (home-base/exception bucket or project-local, per Part 2) — continuity (numbered: `1 PRIME`, `5 PICK UP`, `6 HAND OFF`).
- **`_my_resources/open_tasks/todo_list.md`** — Daniel's personal notes (+ any plan/PRP `.md` notes alongside). ⛔ **Not an agent source for "what's next" or "pick up"** (retired 2026-08-09 — the queue is the live Jira board, root `AGENTS.md` §7). Agents never edit it, **with one mechanical exception:** `/smh-update-maps-indexes` refreshes the **`## Open Work` file-list** to mirror the task files beside it (Daniel's `## Todo list` prose and the task files stay his).
- **`.agents/`** — at the home base: the MASTER toolkit (rules, commands, skills, scripts,
  templates). In a project (thin model, 2026-08-07): **tier-2 law only** — the project's own `rules/` +
  `skills/` + `INDEX.md`; the center carries all workflow law → `.agents/rules/project-law.md`.
- **`opencode.json`** — home base only (thin projects carry none; sessions run from the center):
  `instructions` = the slim least-context set; `skills.paths` = `[".agents/skills"]`.

### The enforcement layer a dev workspace carries (standard since 2026-07-09)
Anywhere stories/code get built — the projects, AND the lobby (Daniel also manages from there; direct
BMAD skill runs bind `{project-root}` to wherever you sit) — carries four enforcement pieces on top of
the toolkit:

- **`_bmad/custom/` guard + dialect tomls** (+ `_bmad/scripts/resolve_customization.py` /
  `resolve_config.py`): `bmad-dev-story.toml` + `bmad-quick-dev.toml` enforce the plan-first gate +
  artifact protocol *inside* BMAD skill runs (persistent facts + un-skippable `on_complete`);
  `bmad-testarch-atdd.toml` + `bmad-testarch-automate.toml` pin test scaffolding to **pytest +
  pytest-bdd** and persist `automation-summary-<story>.md` — the evidence `/cicd-code-review`'s gate
  check 5 looks for. The tomls load `.agents/rules/000-PLAN-FIRST-GATE.md` (master-owned; projects
  inherit it via `/smh-sync-agents`). **`_bmad/` itself is NEVER synced** — toml parity across lobby + AGY +
  Fresh is a 3-way hand-copy; new projects inherit by cloning Fresh.
- **`_bmad-output/sudo-tests.yaml`** — present = the `/cicd-code-review` TEA gate is **ARMED**
  (absent = auto-WAIVED, and a workspace that starts WAIVED tends to stay WAIVED). Ships armed in the
  template with ratchet-from-zero floors; `l1_coverage_min` and CI's `--cov-fail-under` only ever go UP.
- **A project's `pr-check.yml` workflow** — CI gates PRs to **`main` AND `epic/**`** (the 2026-07 audit's
  P0-1 lesson: an ungated integration branch is where regressions hide — under the epic-branch model
  that means story landings get CI too, not just the epic's merge to `main`).
- **BDD layer (TDAD Layer 1)** — Gherkin contracts at `backend/tests/features/<domain>/*.feature`,
  **self-binding** steps at `backend/tests/bdd/steps_<domain>.py` (each calls `pytest_bdd.scenarios()`;
  pyproject `python_files` includes `steps_*.py`) — dropping a feature+steps pair into the tree is all it
  takes for the suite and CI to execute it.

### Format checklist (stamp a workspace)
| ✓ | Item |
|---|---|
| ☐ | `CLAUDE.md` + `GEMINI.md` are one-line adapters (no `{{PLACEHOLDER}}`, no dead commands) — asserted by `tests/test_entry_adapters.py`, which is where a “just this one extra rule” gets caught |
| ☐ | `AGENTS.md` numbered, with Map/Mission/Support + a real routing table + up-route |
| ☐ | `.agents/`: master at the lobby · **tier-2 law only** in a thin project (`rules/` + `skills/` + `INDEX.md`; no vendor, no `opencode.json`) — `project-law.md` |
| ☐ | `docs/repo-map.md` present and current (Part 3) |
| ☐ | dev workspace: `docs/project_overview_guide.md` present (from the centre template) — until it exists the close-out preflight WARNs and the save records it `absent` |
| ☐ | the workspace's `active-context.md` exists in its owning home-base, exception, or project-local store |
| ☐ | "what's next" and "pick up" both read the **live Jira board** (`In Progress` → `To Do Next` → `To Do`); nothing routes to `todo_list.md` |
| ☐ | registered as a row in the root `router.md` |
| ☐ | **no** vendored `docs/workspace-standard.md` in a thin project (the one live copy is the center's; a leftover copy is a conversion defect) |
| ☐ | Tier-2 local law: `_artifacts/`, `_my_resources/`, `docs/` each carry `AGENTS.md` + 1-line adapters |
| ☐ | dev workspace: `_bmad/custom/` guard layer present (4 tomls + resolver scripts — hand-copy parity, never synced) |
| ☐ | dev workspace: `_bmad-output/sudo-tests.yaml` ARMED · `pr-check.yml` gates `main` + `epic/**` |
| ☐ | dev workspace: BDD layer wired (`backend/tests/features/` + self-binding `tests/bdd/steps_*.py` + `python_files`) |

### The PATH CONTRACT (exact files & where they live — what the tooling verifies)
This is the machine-checkable heart of the standard: the **exact path** of every standard element, in the two
**modes** a workspace can run in. `check_maps.py` reads this contract to (a) confirm a workspace is conformant
and (b) know what to reconcile/prune — which is what lets **one generic `/smh-update-maps-indexes` serve every workspace**
instead of a per-repo fork. Keep workspaces matching this table and the generic tool just works.

| Element | Home base (LOBBY) mode | Project (`Projects/<name>/`) mode | Notes |
|---|---|---|---|
| Entry adapters | `CLAUDE.md` · `GEMINI.md` (1-line) | same | identical everywhere |
| Brain | `AGENTS.md` | `AGENTS.md` | numbered §1–§9 |
| Toolkit | `.agents/` (**MASTER** here) | `.agents/` = **tier-2 law only**: `rules/` + `skills/` + `INDEX.md` (thin model 2026-08-07; legacy full-vendor pending conversion) | one source of authorship; two-tier contract → `project-law.md` |
| Navigation index | `docs/repo-map.md` | `docs/repo-map.md` | plain `docs/` everywhere — one form, no underscore |
| System overview | — (the lobby's equivalent is the operator SOP) | `docs/project_overview_guide.md` | what was BUILT, for a human; template at the centre, currency enforced at the story close-out |
| Structure standard | `docs/workspace-standard.md` | — (thin: read the canonical copy at the center) | canonical at the home base; per-project vendored copies retire at conversion |
| Maintenance scripts | `.agents/scripts/{check_maps,generate_repo_map}.py` | — (thin: center-run with `--root Projects/<name>`) | legacy full-vendor projects still hold synced copies until converted |
| Drift baseline | `docs/.maps-state.json` | `docs/.maps-state.json` | sits beside the repo-map |
| Continuity store | `_artifacts/_main/` plus explicitly registered Sudo-managed exception buckets | `_artifacts/` (project-local) | ownership decides; cwd/tool never does |
| Pickup/handoff brief (**prune target**) | `_artifacts/_main/active-context.md` or a registered exception's `active-context.md` | **BMAD project:** `_bmad-output/active-context/active-context.md` (the live brief; `_artifacts/` holds *session history* only) | the file the **prune** trims |
| Context archive (prune overflow) | owning bucket's `active-context-archive.md` | `_bmad-output/active-context/_archive/` | created on first prune |
| Session ledger | `_artifacts/INDEX.md` | `_artifacts/INDEX.md` | one row per session; archive overflow → `INDEX-archive.md` |
| INDEX depth | **level 2** everywhere, except the two named lists below | same | the house rule: every level-2 folder carries an `INDEX.md`. Exceptions are **named sets in `check_maps.py`**, never hardcoded at the call site — opting a folder in is a one-line edit. |
| ↳ `DEPTH3_DIRS` (deeper) | `_artifacts/<bucket>/INDEX.md` (bucket = `_main` or a registered exception) | `_artifacts/<epic_or_bucket>/INDEX.md` (e.g. `epic_8/`, `epic_11/`, `_main/`, `tea/`) | folders that index one level **deeper**: skipped by check 2.5, walked by check 7 instead. One row per session folder, listing the story/what + artifact files present; scan-to-find for bug-tracking. Not for code dirs. Created when a bucket has ≥2 session folders; `/smh-update-maps-indexes` reconciles. |
| ↳ `DOT_CONTENT_DIRS` (scanned) | `.agents/` | `.agents/` | dot-dirs that are real **content**, not tool cache, so they are scanned like any normal folder. Everything else starting with `.` stays skipped (`.ruff_cache/0.15.21/` would otherwise be permanent FATAL drift). Applies at **level 1 only** — the level-2 dot-skip stays blanket, keeping `.agents/.claude` and the tool caches exempt. |
| Portable auto-memory | `_artifacts/_memory/` | `_artifacts/_memory/` | the **canonical** home of Claude Code's auto-memory. The harness writes to `~/.claude/projects/<slug>/memory/`, which is not a repo and never leaves the machine; a **junction (Windows) / symlink (macOS)** points it here so memory travels in git. Linked by `.agents/scripts/link-memory.ps1` · `link-memory.sh` (twins; dry-run by default). `README.md`/`.gitkeep` are scaffolding, not memories. **Two-tier since SCC-73:** this store is the **inbox** — every platform writes here, always, because Claude's harness bakes an absolute per-workspace path into its own instruction and no repo law can redirect it. Facts that settle into project-only truth are **relocated** to the project's store below, by `/smh-memory-audit`, per item, on the operator's word. A `## Project stores` section in the index signposts every one of them. |
| ↳ per-project memory | *(home base only)* | `Projects/<name>/_artifacts/_memory/` | the same store shape, **inside the project's own repo** — so a project's memories version with the code they describe and arrive with a clone. Read by any lane launched inside that project (which never loads the lobby index), and by `/cicd-boot-sprint-memory` Step 1.5 after it binds a target. ⛔ **A separate repo, therefore a separate ticket key** — AGY answers to `AVCH` only, and an `SCC`-keyed commit there is rejected by its armed hook. The lobby gate reports project-store defects as `[SIGNAL]`, never as a blocking failure, because the lobby is not allowed to fix them. |
| Retired artifacts | `_artifacts/_archived/` | `_artifacts/_archived/` | — |
| Testing & Debugging | `_artifacts/debugging/` | `_artifacts/debugging/` | standardized folder for isolated testing, bug repros, and debug scripts |
| Tier-2 local law | `_artifacts/AGENTS.md` · `_my_resources/AGENTS.md` · `docs/AGENTS.md` (+ 1-line `CLAUDE.md`/`GEMINI.md` adapters beside each) | same | tier model above; PRESENCE linted as a **non-fatal hint** (`check_maps` check 8), adapter BODY asserted fatally by `tests/test_entry_adapters.py` |
| Open tasks ("what's next") | the **live Jira board** (`SCC`) — `In Progress` → `To Do Next` → `To Do` | the project's own board (e.g. `AVCH`) | root `AGENTS.md` §7 · `.agents/rules/jira.md`. ⛔ `_my_resources/open_tasks/todo_list.md` is **not** a source (retired 2026-08-09); `/smh-update-maps-indexes` only refreshes its `## Open Work` file-list |
| Personal area (protected) | `_my_resources/` | `_my_resources/` | off-limits **except** the `## Open Work` manifest in `open_tasks/todo_list.md` (maintained by `/smh-update-maps-indexes`) |
| BMAD (if present) | — | `_bmad/` (owned, regenerated) · `_bmad-output/` (state) | `_bmad-output/active-context/active-context.md` **IS** the continuity brief above; `_bmad/` itself is never hand-edited |

**Two modes, one ownership rule.** Every workspace uses a plain `docs/` folder. A non-exempt project owns
its session history in its own `_artifacts/` regardless of where a chat starts. The lobby store contains
only `_main/` plus the named Sudo-managed exceptions in `router.md`. In a BMAD project, the continuity brief
that pickup reads and pruning trims lives at `_bmad-output/active-context/active-context.md`; project-local
`_artifacts/` holds session history. `check_maps.py` detects lobby/project mode and applies the right column.

---

## Part 2 — How to UPKEEP a workspace

Formatting is one-time; upkeep is forever. Who does what, and when.

### The nine projects — what each one IS

Nine git submodules sit under `Projects/`, and until 2026-09-04 nothing said what they were. That gap
had a cost: `test_rule_frontmatter.py` audited `sudo-command-center` — the **published teaching
edition** — as if it were a thin project, failed three assertions on a shipped product, and held the
suite floor red at 72/73 for every lane (SCC-399). A list with no stated model is a list anyone can
misread.

| Submodule | What it is | Kept current by | Audited by the lobby's suite? |
|---|---|---|---|
| `sudo-command-center` | the **published teaching edition** of this lobby — a sanitized export, never edited in place | `export-teaching-edition.ps1`, from the `claude/teaching-edition` branch | **no** — it is a mirror; its 28 rule files ship on purpose |
| `sudo-project-skeleton` | the **new-project template** — what `/smh-new-project` seeds from | seeded from AviationChat's stack **by hand, never a blind copy** — AviationChat-specific rules must not propagate into a fresh project (Mr. Hatter's ruling, 2026-09-04). Settings and fence shape are propagated into it **deliberately, per ticket** — SCC-379 did the SCC-376 fence — so a new project is not born stale | **not by the suite** — it carries no `.agents/` the lobby audits; a ticket keeps it current |
| `AGY_AVIATIONCHAT` | a maintained thin project (board `AVCH`) | its own story lanes | **yes** — listed in `.agents/maintained-projects.txt` |
| `NEXgen-VR-Director` | a maintained thin project | its own story lanes | **yes** — listed in `.agents/maintained-projects.txt` |
| `B-L-WorldWide` · `BRKN_Tattoos` · `NEXGen-Films` · `OpenChat-Openrouter` · `RAG_Pipeline_AC` | separate projects on their own schedules | themselves | **no** |

**The rule this table states:** the lobby lints exactly the names in
`.agents/maintained-projects.txt` and nothing else. A name is absent because the lobby does not
drive that repo — **never** because nobody got to it. Never hand-loop over `Projects/*`; that reaches
repos we deliberately do not keep current, and it is the exact bug SCC-399 fixed.

`Fresh_Workspace_BMAD` was a tenth entry: the living template until 2026-08-07 (SCC-25), removed from
git 2026-09-04 (SCC-403). `sudo-project-skeleton` holds that role now.

### Rules: one source, no forks
- **Authored ONLY in `.agents/`.** Copies in `.claude/`, `.opencode/`, and per-project tool dirs are
  **vendored** by `/smh-sync-agents` — never hand-edit a copy; edit the master and re-sync.
- **Project-specific hard-stops** live in that project's local `constitution.project.md` — never by editing a
  vendored generic rule. This is the anti-fork rule that prevents the drift this whole standard exists to fix.
  Which tier ANY rule or skill belongs to — and the bind-time obligation to read a project's
  `.agents/INDEX.md` — is the two-tier contract in `.agents/rules/project-law.md`.
- **BMAD skill overrides are the sanctioned per-repo exception:** `_bmad/custom/*.toml` customize installed
  BMAD skills per repo and survive skill updates — `/smh-sync-agents` never touches `_bmad/`. Keep the three
  repos' sets identical by hand-copy (new projects inherit from `sudo-project-skeleton`); personal tweaks go in
  `*.user.toml` (gitignored), team law in the committed `*.toml`.

### Command sync & platform reach — one master, four platforms
The **single canonical invocable set is `.agents/commands/`**. It mirrors to every platform via one command,
`/smh-sync-agents` (engine: `.agents/scripts/sync-agents.ps1`) — there is no second sync tool to drift against.

- **Surfaces it feeds.** Local tool dirs `.claude/{commands,skills}` + `.opencode/{commands,agent}` +
  `.roo/commands/`; the master launcher skills in `.agents/skills/` (read natively by Codex **and**
  Antigravity); and, on a **lobby** sync, the **machine-global** cache `~/.config/opencode/commands`
  (sourced from `commands/`). (A project sync vendors `.agents/` and refreshes that project's local dirs;
  it does **not** touch the globals — globals reflect the lobby's canonical set.)
- **Codex is the lightest surface.** It reads `AGENTS.md` **and** the Agent Skills in `.agents/skills/`
  natively (open Agent Skills standard: `$REPO_ROOT/.agents/skills` + `~/.codex/skills`), so rules and our own
  skills need zero sync work — only the custom-prompts cache above. The one gap: BMAD installs its skills to
  `.claude/skills` (manifest `ides: [claude-code, antigravity]`), which Codex doesn't read — so a lobby sync
  **mirrors the `bmad-*` skills into `~/.codex/skills`**, making BMAD reachable there via `/skills`. Both Codex
  caches are machine-local (like the opencode/AG caches), so re-run the sync per machine.
- **`commands/` vs `skills/`.** `.agents/commands/` is where a command is **authored** — full body, any
  length. `.agents/skills/` carries the **generated launcher** for each eligible command: a few hundred bytes
  that point the agent back at `.agents/commands/<name>.md`. **Codex and Antigravity both read that
  directory natively**, invoking any `SKILL.md` in it as `/<name>`, and Claude reaches the same file through
  the `.claude/skills/` tree copy — so one launcher is the door for three platforms. There is no size rule
  anywhere: skills are an unrestricted bundle.
  *(ⓘ Why launchers exist at all: Antigravity — and only Antigravity — **truncated** an over-long workflow
  rather than rejecting it, so a raw 30 KB body ran on partial steps and looked fine. See SCC-135. That
  surface is retired, and the vendor retires workflows outright on 2026-11-01.)*
- **Platform reach.** A command declares scope with frontmatter `platforms: [claude, opencode, antigravity,
  codex]`. **Absent = universal** (all four). The sync copies a command only to the platforms it lists, so a
  tool that can't run it (e.g. `/cicd-autopilot-claude` needs the `claude` CLI) never appears in the wrong surface.
- **Purge policy.** Local tool dirs purge only master-managed-but-now-ineligible commands (a project's own
  commands are left alone). Global caches are **mirror-exact** — stale ghosts purged — **except `bmad-*`**,
  which BMAD installs globally and is never ours to delete. The Codex skills mirror likewise purges stale
  `bmad-*` dirs but preserves `.system` and any foreign (non-bmad) skill dirs.
- **Antigravity reads the skill surface.** It invokes any `.agents/skills/<name>/SKILL.md` as `/<name>`,
  straight out of the workspace, and it keeps no global cache of ours.
  ⚠ **A launcher only resolves where `.agents/commands/` exists — the lobby.** Under the thin model a
  project carries no tier-1 copy, so a command invoked inside a project STOPS and says so, rather than
  running. That is a deliberate trade and the right direction: before SCC-332 a global menu entry
  delivered a truncated prefix of the body and the agent improvised the rest.
  A command that fails visibly beats one that runs on 27% of its steps. Full bodies reach every other
  platform directly from `commands/`.
  *(SCC-370 widened this from "a big command" to "any command": 14 doors used to ship verbatim and so
  ran from a project's global menu. **Thirteen of the fourteen** are lobby commands by design — 7 `cicd-*`
  command-center→project doors, and 6 `smh-*` that act on the centre itself. **Two** members are worth
  naming rather than one. `sentry-security-team-avch` is genuinely project-scoped. And `smh-review` is
  the one whose loss is a real trade rather than a formality: its old door was 326 bytes that invoked
  the `md-feedback` MCP server and named no repo file at all, so it ran anywhere and could never have
  been truncated — the justification above does not cover it. Both now stop in a thin project and say
  so; run either from the lobby.)*

### Git — one policy
**Agents commit and push their own work** — explicit paths (never `git add -A`), the repo's Jira key leading
every branch and subject, in the lane's own worktree, and **commit + push are one action** (unpushed is
stranded). `main` is the only long-lived branch and is reached only through a door
(`/cicd-push-e2e` · `/smh-close-task-merge-tree`) whose invocation is the operator's sign-off. The old
default — "never run git yourself; hand Daniel the command" — is **gone** (it produced commits carrying four
unrelated sessions). Full rule → `.agents/rules/git-policy.md`.

### Artifacts — the plan-first discipline
Every non-trivial, file-touching task: research read-only → write `implementation_plan.md` and **STOP for
"approved"** → execute with a live TodoWrite list → close with a single `walkthrough.md` (narrative + a
`## Task Checklist` snapshot + a `## Your Actions` section — no separate `task-list.md`) → append one row
to `_artifacts/INDEX.md` → update `active-context.md` (the hand-off).
Full rule → `.agents/rules/artifacts-always-first.md`.

**Artifact organization — ownership first (Daniel, 2026-07-30):**
- **Default:** every current or future directory under `Projects/` owns its session history in
  `Projects/<name>/_artifacts/`, regardless of cwd or tool.
- **Exceptions:** the home `router.md` contains the complete Sudo-managed exception registry. Only those
  named workspaces use home-base `_artifacts/<name>/` buckets. An exception never transfers to a clone.
- **Home-base/cross-project work:** routing, master `.agents/`, and multi-project governance use
  `_artifacts/_main/<YYYY-MM-DD>_<slug>/`.
- **No fallback:** if a non-exempt project's local store is missing, create the standard project-local
  skeleton; never create a home-base project bucket.
- Within the owning store: **random task** → `_main/<YYYY-MM-DD>_<slug>/` for project-owned stores;
  **story** → `<epic>/<story>/`; retired history → `_archived/`; **testing/debugging** →
  `debugging/<YYYY-MM-DD>_<slug>/`.
- **One authoritative history:** do not split a non-exempt project's history by launch directory or agent.

### Auto-memory — junctioned into the repo, because the harness store is path-derived
Claude Code keeps auto-memory at `~/.claude/projects/<slug>/memory/`, where `<slug>` is **derived from the
workspace's absolute path** (`:` `\` `/` `_` → `-`). Left alone that store fails three ways: it never leaves
the machine (`~/.claude` is not a repo, not a link, not cloud-synced), a **rename silently orphans it**
(the slug changes), and two casings of a path can collide on a case-insensitive volume.

So the canonical store is `_artifacts/_memory/` **in the repo**, and the harness path is a junction/symlink
pointing at it — set up per machine with `.agents/scripts/link-memory.ps1` (Windows) or `link-memory.sh`
(macOS). They are **twins by contract**: change one, change both.

Two operational rules, both learned the expensive way:
- **The first machine to link SEEDS the shared store**; later machines find it populated and move their own
  local memory *aside to a backup* rather than merging. **Link the machine with the newest memories first.**
  The scripts never delete or merge — but a stale machine seeding first propagates stale memory to all.
- **Re-run the linker on rename day.** `rename-fix.ps1` repairs `.claude/settings.json` but not the memory
  slug. That gap stranded **15 memory files** across two dead slugs before this was set up. Once junctioned,
  a rename costs nothing but re-pointing the link — the data was never in the slug directory.

Full contract → `_artifacts/_memory/README.md`; setup steps → `docs/migrations/INDEX.md` §1 step 8
(new machine) and §3 (rename day).

### Routing canary — the regression cadence
`_routing-canary/` is a permanent check, not a one-time demo. **Re-run it when** you change routing structure
(`AGENTS.md`/`router.md`/the adapter-skill pattern) or qualify a new LLM/CLI. A green run proves the
*mechanism* works in that tool; it does NOT prove your real routing is correct — for that, run the cold-route
test ("work on X" from a fresh session lands in the right workspace). Full how/when → `_routing-canary/README.md`.

The plan's full **validation loop** is five checks; the canary is only the first. Run the rest when the
change warrants it:

| Check | How | Pass |
|---|---|---|
| **Canary** (mechanism) | paste `_routing-canary/<adapter>` into a fresh agent, nothing else | `Power.md` == `control your agent`, reply `done boss` |
| **Cold route** (real routing) | fresh session at the root: "work on X"; then "never mind, Y" | lands in the right workspace via a light lookup; re-routes cleanly |
| **Persistence** | trivial edit → "hand off" → new session → "pick up" | the brief matches the hand-off, and nothing was mutated by the pick-up |
| **Negative / route-up** | ask a workspace something outside its domain | it routes **back up** via `router.md` — no hallucinated answer, no tree wander |
| **Token frugality** | watch the agent's "reading …" trace on a cold route | entry map + one router hop + one workspace context; not the tree |

### Router + repo-map drift
- Add/remove/convert a workspace → update its row in the root `router.md` (lobby = categories only).
- Repo-map: the SessionStart hook *detects* drift and nags; the human/agent *supplies the purpose line* at
  end-of-task — and only when a top-level folder or an agent was added/removed (Part 3).

### Context hygiene — prune the continuity brief (don't let it grow forever)
A **session** = one pick-up→hand-off; each hand-off prepends one dated block (`**YYYY-MM-DD: …**`) to the
continuity `active-context.md` and one row to `INDEX.md`. Left alone these grow without bound and bloat every
pickup. `/smh-update-maps-indexes` carries a **prune** step: keep the **newest ~10 session blocks** in the brief, archive
older ones to the context archive (`active-context-archive.md` at the lobby; `_bmad-output/active-context/_archive/`
in a BMAD project); keep the newest **~50** `INDEX.md` rows, archive older to `INDEX-archive.md`. `check_maps.py`
only *nags* past ~12 blocks (hysteresis — not every session), and the prune is approval-gated like every other
edit. Session **folders** under `_artifacts/` are disk-only (never auto-loaded into context) → archive them on
epic close, not on a schedule.

The same command also **refreshes the open-tasks list**: it rewrites the `## Open Work` file-list in
`_my_resources/open_tasks/todo_list.md` to mirror the plan/PRP `.md` files actually sitting in `open_tasks/`
(Daniel drops them in; moves them out when he picks one up). It touches only that manifest — his `## Todo list`
prose and the task files stay his — and it's approval-gated like the prune.

**Run scope — fan-out.** `/smh-update-maps-indexes` is **mode-driven**: from the **home base** (a `Projects/` dir exists)
it fans out — `check_maps.py --all` reconciles the lobby **and every conformant project** (one with an
`AGENTS.md`) in one run, so a single command from the top cleans + prunes + refreshes the open-tasks list
everywhere. From **inside a project** it reconciles just that workspace. Each repo commits and re-anchors
(`--set-anchor`) separately.

### End-of-Task checklist (before saying "done" on anything that produced changes)
- ☐ `walkthrough.md` — the single closing doc: what changed + real pasted test output + a `## Task Checklist`
  (final TodoWrite snapshot) + a `## Your Actions` section with the exact git command
- ☐ `active-context.md` updated (the hand-off)
- ☐ `INDEX.md` row appended
- ☐ **depth-3 `INDEX.md`** updated (if the session landed inside an `_artifacts/` epic/bucket folder that already has one — or created if the folder now has ≥2 sessions)
- ☐ `docs/repo-map.md` updated **only if** a top-level folder/agent was added/removed
- ☐ ran `_routing-canary/` if routing structure changed
- ☐ story `.md` status + `sprint-status.yaml` synced (story work only)

---

## Part 3 — The repo-map standard (two modes)

`docs/repo-map.md` is the **folder-level navigation index** every harness reads first instead of grepping the
tree blind. It has two zones, separated by sentinels:

- **Curated header** (`<!-- REPO-MAP:CURATED-START -->` … `END`) — hand-written, the part a script can't
  produce: the "to find X → look here" routing table and the "which doc to read when" knowledge map. **Never
  clobbered** by regeneration.
- **Auto body** (`<!-- REPO-MAP:AUTO-START -->` … `END`) — generated by `scripts/generate_repo_map.py`
  (vendored from master `.agents/scripts/`). Only this zone is rewritten on regen.

**Two modes, so the standard fits every project (code and non-code):**
- **Code workspace** (has `backend/`/`src/` with real code): the auto body emits **function/class signatures**
  for code dirs, and **collapses** any data/asset dir over the threshold (**default 8 files**) into ONE
  summarized line (e.g. *"`rkp_manifests/` — 47 per-lesson JSON, named `PPL_PA_<area>_<task>_<n>_rkp.json`"*)
  instead of enumerating every file.
- **Content workspace** (assets/media, e.g. a films project): the auto body is **folder-level only** — every
  dir summarized, no signature extraction. The collapse rule makes this the natural degenerate case.

**Maintenance loop:** the `.claude/settings.json` SessionStart hook (a) injects `docs/repo-map.md` into context
and (b) runs a **detect-only** drift check — lists real subdirs, skips an ignore list (`__pycache__`, `.venv`,
`.pytest_cache`, `node_modules`, `.adk`, `_test_scripts`, `_debug_audio`, `__tests__`), flags any folder on
disk but missing from the map. Detection nags; it does **not** self-heal — a script can't write the one-line
*purpose*, so the human/agent supplies it at end-of-task. Regenerate the auto body by running the generator;
hand-edit only the curated header.

---

## Appendix — Reconciliation status (the "starting fresh" cleanup)

This standard replaces months of contradictory, duplicated rules. State as of 2026-06-24:

**Resolved (at the master `.agents/` source):**
- One git policy (`git-policy.md`, formerly the contradictory `git-closeout-commits.md`).
- `constitution.md` + `artifacts-always-first.md` reconciled to it (both wrote to `_artifacts/<workspace>/`;
  **later superseded 2026-06-25 by a cwd-based model, then superseded again 2026-07-30 by the
  ownership-first model** — see Part 2).
- `prose-formatting.md` repointed off the dead `_claude_artifacts/` store.
- `_experiment/` → `_routing-canary/`.

**Resolved 2026-06-27 — `_claude_artifacts/` fully retired:**
- The `1_*` commands (`1_run-all-tests-back_front`, `1_make-workflow-from-chat`, `1_check-for-tech-stack-updates`)
  and the `autopilot-dev-story.ps1` engine were repointed off `_claude_artifacts/` → `_artifacts/` at the master
  `.agents/` source and across every synced copy. Fresh-workspace (Fresh_Workspace_BMAD) was converted to the
  project-local `_artifacts/` model (matching AGY_AVIATIONCHAT) and its dead `_claude_artifacts/` store was deleted.
  Ignore-lists keep the name defensively; historical mentions (a skill's origin-session paths) are left as
  accurate history.

**Retire-list (follow-up reconcile pass — NOT yet done; some are engine-coupled):**
- Cleanup unrelated to the artifact store: `(some) @.agent/` singular paths + `your-action-required.md` in the
  autopilot docs; per-project copies carrying the opposite git policy, `mandatory-session-artifacts.md`, or dead
  gate files — retired/re-vendored during each project's conversion (separate propagation plan).
- Anti-fork rule (Part 2) is the standing guard so this can't re-accumulate.
