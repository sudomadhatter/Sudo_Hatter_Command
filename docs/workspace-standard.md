---
title: Workspace Standard — How to Format and Upkeep a Workspace
type: reference-doc
date: 2026-06-24
owner: Daniel
status: canonical
canonical_location: _docs/workspace-standard.md (home base) — vendored copy in each Projects/<name>/docs/
sources:
  - _my_resources/youtube_transcripts/implementation-plan_folder-as-workspace-routing-system.md  # theory
  - _docs/master-implementation-plan.md                                                          # the rollout
---

# Workspace Standard

> **What this is.** The single, evergreen standard for how every workspace in `Sudo_Hatter_Command` is
> *shaped* and *kept healthy*. The transcript is the theory; the master-implementation-plan is the one-time
> rollout; **this** is the standing spec an agent consults whenever it creates, converts, or maintains a
> workspace. It is model-agnostic — it serves Claude, opencode, and Antigravity/Gemini equally.
>
> **Where it lives.** Canonically at `_docs/workspace-standard.md`. A **vendored copy** travels in each
> `Projects/<name>/docs/` (same model as `.agents/rules/*`), so every repo is self-contained. Edit the
> canonical copy; re-distribute with `/sync-agents`. Never hand-edit a vendored copy.

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

---

## Part 1 — How to FORMAT a workspace

A compliant workspace has these, and nothing it doesn't need.

### Layer 1 — entry + map
- **`CLAUDE.md`** and **`GEMINI.md`** — one-line adapters, identical everywhere: *"Read `AGENTS.md` in this
  same folder and follow it. That is the single source of truth."* Nothing model-specific beyond the name.
- **`AGENTS.md`** — the brain. Numbered sections so agents skip-to-N:
  1. **ROOT LAW / prime mission** — one line: what this workspace exists to do.
  2. **START HERE** — you're in this workspace; don't read the tree; routing question → the routing table /
     `../../router.md`; risky action → GATES.
  3. **MAP / MISSION / SUPPORT** — the three answers every task needs (where am I + where can I go / what is the
     work / what tools+context).
  4. **ALWAYS-LOAD** — the *small* set only: `.agents/rules/constitution.md`, `karpathy-guidelines.md`, and
     `artifacts-always-first.md`. Everything else loads on demand.
  5. **ARTIFACTS PROTOCOL — MANDATORY FIRST ACTION** — the plan-first gate, stated up front (see Part 2).
  6. **ROUTING TABLE** — the heart (Layer 2, below).
  7. **NAMING CONVENTIONS** — dates/versions/slugs; replaces a database.
  8. **GATES** — routing gate + risk gate → `.agents/rules/constitution.md`.
  9. **PERSISTENCE** — pickup/handoff → the right `_artifacts/` for where you work from (Part 2). **"pick up"
     also surfaces `_my_resources/open_tasks/todo_list.md`** (READ-ONLY) — the same notes the routing-table
     "what's next / open tasks" row serves, so both triggers land on one source.

### Layer 2 — the routing table (the single most important thing)
A plain-English table in `AGENTS.md`: **task → read these / skip these / skills**. It is what makes
least-context loading real. Always include the up-route: *"if what you need isn't here, GO BACK to
`../../router.md`."* Routers route up as well as down — an agent can never dead-end.

### Layer 3 — skills (referenced, never preloaded)
Skills live in the vendored `.agents/skills/<name>/SKILL.md` and are pulled **only** by the workspace rows
that call them. Never load skills globally.

### Supporting files every workspace carries
- **`docs/repo-map.md`** — the navigation index (Part 3).
- **`active-context.md`** (home-base bucket or project-local, per Part 2) — continuity (numbered: `1 PRIME`, `5 PICK UP`, `6 HAND OFF`).
- **`_my_resources/open_tasks/todo_list.md`** — Daniel's "what's next" queue (+ any plan/PRP `.md` notes alongside). Surfaced by BOTH the routing-table "what's next" row AND on "pick up." **READ-ONLY for agents — with one exception:** `/1_update-maps` refreshes the **`## Open Work` file-list** to mirror the task files beside it (Daniel's `## Todo list` prose and the task files stay his). Cross-check vs live files.
- **`.agents/`** — the vendored master toolkit (rules, commands, skills, workflows, scripts, templates).
- **`opencode.json`** — `instructions` = the slim least-context set (`AGENTS.md` + the always-load rules);
  `skills.paths` = `[".agents/skills"]`.
- **A vendored copy of this standard** at `docs/workspace-standard.md`.

### Format checklist (stamp a workspace)
| ✓ | Item |
|---|---|
| ☐ | `CLAUDE.md` + `GEMINI.md` are one-line adapters (no `{{PLACEHOLDER}}`, no dead commands) |
| ☐ | `AGENTS.md` numbered, with Map/Mission/Support + a real routing table + up-route |
| ☐ | `.agents/` vendored; `opencode.json` points at `.agents/` paths |
| ☐ | `docs/repo-map.md` present and current (Part 3) |
| ☐ | the workspace's `active-context.md` exists (home-base bucket or project-local) |
| ☐ | `_my_resources/open_tasks/todo_list.md` present (READ-ONLY); wired into BOTH the "what's next" routing row AND "pick up" |
| ☐ | registered as a row in the root `router.md` |
| ☐ | vendored `docs/workspace-standard.md` present |

### The PATH CONTRACT (exact files & where they live — what the tooling verifies)
This is the machine-checkable heart of the standard: the **exact path** of every standard element, in the two
**modes** a workspace can run in. `check_maps.py` reads this contract to (a) confirm a workspace is conformant
and (b) know what to reconcile/prune — which is what lets **one generic `/1_update-maps` serve every workspace**
instead of a per-repo fork. Keep workspaces matching this table and the generic tool just works.

| Element | Home base (LOBBY) mode | Project (`Projects/<name>/`) mode | Notes |
|---|---|---|---|
| Entry adapters | `CLAUDE.md` · `GEMINI.md` (1-line) | same | identical everywhere |
| Brain | `AGENTS.md` | `AGENTS.md` | numbered §1–§9 |
| Toolkit | `.agents/` (**MASTER** here) | `.agents/` (**vendored**, synced) | one source of authorship |
| Navigation index | `_docs/repo-map.md` | `docs/repo-map.md` | **`_docs/` (lobby) vs `docs/` (project)** — the tool auto-detects both |
| Structure standard | `_docs/workspace-standard.md` | `docs/workspace-standard.md` | this file; vendored copy per project |
| Maintenance scripts | `.agents/scripts/{check_maps,generate_repo_map}.py` | same (synced copies) | run central with `--root <path>`; synced copy is for standalone use |
| Drift baseline | `_docs/.maps-state.json` | `docs/.maps-state.json` | sits beside the repo-map |
| Continuity store | `_artifacts/` (buckets: `_main/`, `<project>/`) | `_artifacts/` (project-local) | **"artifacts go where you work FROM"** |
| Pickup/handoff brief (**prune target**) | `_artifacts/<bucket>/active-context.md` | **BMAD project:** `_bmad-output/active-context/active-context.md` (the live brief; `_artifacts/` holds *session history* only) | the file the **prune** trims |
| Context archive (prune overflow) | `_artifacts/<bucket>/active-context-archive.md` | `_bmad-output/active-context/_archive/` | created on first prune |
| Session ledger | `_artifacts/INDEX.md` | `_artifacts/INDEX.md` | one row per session; archive overflow → `INDEX-archive.md` |
| Retired artifacts | `_artifacts/_archived/` | `_artifacts/_archived/` | — |
| Open tasks ("what's next") | `_my_resources/open_tasks/todo_list.md` (+ plan/PRP notes) | same | **READ-ONLY for context**, but `/1_update-maps` refreshes its `## Open Work` file-list; surfaced on pickup + "what's next" |
| Personal area (protected) | `_my_resources/` | `_my_resources/` | off-limits **except** the `## Open Work` manifest in `open_tasks/todo_list.md` (maintained by `/1_update-maps`) |
| BMAD (if present) | — | `_bmad/` (owned, regenerated) · `_bmad-output/` (state) | `_bmad-output/active-context/active-context.md` **IS** the continuity brief above; `_bmad/` itself is never hand-edited |

**Two modes, one rule.** The only legitimate home-base↔project differences are: (1) the docs folder is `_docs/`
at the lobby, `docs/` in a project; (2) the lobby's `_artifacts/` is split into **buckets** (`_main/`,
`<project>/`) because work from the lobby is filed by *which workspace it changes*, whereas a project's
`_artifacts/` is flat history; (3) the **continuity brief** that pickup reads and the prune trims lives at
`_artifacts/<bucket>/active-context.md` at the lobby but at **`_bmad-output/active-context/active-context.md`**
in a BMAD project (a project's `_artifacts/` holds *session history* — folders + `INDEX.md` — not the brief).
Everything else is identical. `check_maps.py` detects the mode by the presence of a `Projects/` directory (and
a `_bmad-output/` directory) and applies the right column.

---

## Part 2 — How to UPKEEP a workspace

Formatting is one-time; upkeep is forever. Who does what, and when.

### Rules: one source, no forks
- **Authored ONLY in `.agents/`.** Copies in `.claude/`, `.opencode/`, and per-project tool dirs are
  **vendored** by `/sync-agents` — never hand-edit a copy; edit the master and re-sync.
- **Project-specific hard-stops** live in that project's local `constitution.project.md` — never by editing a
  vendored generic rule. This is the anti-fork rule that prevents the drift this whole standard exists to fix.

### Command sync & platform reach — one master, three platforms
The **single canonical invocable set is `.agents/commands/`**. It mirrors to every platform via one command,
`/sync-agents` (engine: `.agents/scripts/sync-agents.ps1`) — there is no second sync tool to drift against.

- **Surfaces it feeds.** Local tool dirs `.claude/{commands,skills}` + `.opencode/{commands,agent}`; and, on a
  **lobby** sync, the two **machine-global** caches `~/.config/opencode/commands` and
  `~/.gemini/antigravity/global_workflows`. (A project sync vendors `.agents/` and refreshes that project's
  local dirs; it does **not** touch the globals — globals reflect the lobby's canonical set.)
- **`commands/` vs `workflows/`.** `.agents/commands/` are the invocable `/slash` units that mirror out.
  `.agents/workflows/` are **in-repo reference process-docs** read via routing tables — they are NOT pushed to
  any command cache. *(Antigravity confusingly calls its invocable units "workflows," but our source is always
  `commands/` — name-matching that to `.agents/workflows/` is the exact bug this rule prevents.)*
- **Platform reach.** A command declares scope with frontmatter `platforms: [claude, opencode, antigravity]`.
  **Absent = universal** (all three). The sync copies a command only to the platforms it lists, so a tool that
  can't run it (e.g. `/autopilot_claude` needs the `claude` CLI) never appears in the wrong surface.
- **Purge policy.** Local tool dirs purge only master-managed-but-now-ineligible commands (a project's own
  commands are left alone). Global caches are **mirror-exact** — stale ghosts purged — **except `bmad-*`**,
  which BMAD installs globally and is never ours to delete.
- **Gemini is global-only.** Antigravity has no project-local command dir; it reads from the global cache. That
  asymmetry is a platform constraint, not a defect — the same canonical set still reaches it.

### Git — one policy
Never run `git commit`/`git push` yourself; the `walkthrough.md` "Your Actions" hands Daniel the exact command.
The only exception is when Daniel explicitly delegates a specific commit/push in the moment. Full rule →
`.agents/rules/git-policy.md`.

### Artifacts — the plan-first discipline
Every non-trivial, file-touching task: research read-only → write `implementation_plan.md` and **STOP for
"approved"** → execute with a live TodoWrite list → close with `walkthrough.md` (+ "Your Actions") and a
`task-list.md` snapshot → append one row to `_artifacts/INDEX.md` → update `active-context.md` (the hand-off).
Full rule → `.agents/rules/artifacts-always-first.md`.

**Artifact organization — artifacts go WHERE YOU WORK FROM (Daniel, 2026-06-25):**
The deciding factor is the workspace you have open (your cwd), not only what the work is about.
- **Working from the home base** (`Sudo_Hatter_Command/` is your cwd) → home-base `_artifacts/`:
  - **project work** → a per-project bucket `_artifacts/<project-folder-name>/<YYYY-MM-DD>_<slug>/`
    (e.g. `_artifacts/aviationChat-AGY/`, `_artifacts/clean-bmad-workspace/`; the bucket name = the
    `Projects/<name>/` folder name).
  - **main / home-base / cross-project work** (routing, the `.agents/` toolkit, multi-project) →
    `_artifacts/_main/<YYYY-MM-DD>_<slug>/` (formerly `_home`).
  - For project work, **create the per-project bucket if it isn't there yet; otherwise reuse it.**
  - Either way, log a row in the home-base `_artifacts/INDEX.md`.
- **Working from inside a project** (`Projects/<name>/` is your cwd) → **follow THAT project's rules**:
  project-local `Projects/<name>/_artifacts/`, with the project's own `_artifacts/active-context.md`
  (+ `_artifacts/INDEX.md`). The project owns this history so it travels with the repo. (There is no `_main`
  inside a project — every task there is that project's work.)
- **opencode** writes under its own `_artifacts/opencode/` namespace and applies the **same rules inside it**:
  `opencode/<project>/`, `opencode/_main/`, `opencode/<project>/<epic>/<story>/`.
- Within either location: **random task** → `<YYYY-MM-DD>_<slug>/`; **story** → `<epic>/<story>/` (epic folder
  houses its stories — create the epic folder if missing); retired history → `_archived/`.
- **Finding a project's history:** look in BOTH the home-base bucket `_artifacts/<project>/` (sessions run
  from the home base) AND the project-local `Projects/<name>/_artifacts/` (sessions run inside the project).

### Routing canary — the regression cadence
`_routing-canary/` is a permanent check, not a one-time demo. **Re-run it when** you change routing structure
(`AGENTS.md`/`router.md`/the adapter-skill pattern) or qualify a new LLM/CLI. A green run proves the
*mechanism* works in that tool; it does NOT prove your real routing is correct — for that, run the cold-route
test ("work on X" from a fresh session lands in the right workspace). Full how/when → `_routing-canary/README.md`.

### Router + repo-map drift
- Add/remove/convert a workspace → update its row in the root `router.md` (lobby = categories only).
- Repo-map: the SessionStart hook *detects* drift and nags; the human/agent *supplies the purpose line* at
  end-of-task — and only when a top-level folder or an agent was added/removed (Part 3).

### Context hygiene — prune the continuity brief (don't let it grow forever)
A **session** = one pick-up→hand-off; each hand-off prepends one dated block (`**YYYY-MM-DD: …**`) to the
continuity `active-context.md` and one row to `INDEX.md`. Left alone these grow without bound and bloat every
pickup. `/1_update-maps` carries a **prune** step: keep the **newest ~10 session blocks** in the brief, archive
older ones to the context archive (`active-context-archive.md` at the lobby; `_bmad-output/active-context/_archive/`
in a BMAD project); keep the newest **~25** `INDEX.md` rows, archive older to `INDEX-archive.md`. `check_maps.py`
only *nags* past ~12 blocks (hysteresis — not every session), and the prune is approval-gated like every other
edit. Session **folders** under `_artifacts/` are disk-only (never auto-loaded into context) → archive them on
epic close, not on a schedule.

The same command also **refreshes the open-tasks list**: it rewrites the `## Open Work` file-list in
`_my_resources/open_tasks/todo_list.md` to mirror the plan/PRP `.md` files actually sitting in `open_tasks/`
(Daniel drops them in; moves them out when he picks one up). It touches only that manifest — his `## Todo list`
prose and the task files stay his — and it's approval-gated like the prune.

**Run scope — fan-out.** `/1_update-maps` is **mode-driven**: from the **home base** (a `Projects/` dir exists)
it fans out — `check_maps.py --all` reconciles the lobby **and every conformant project** (one with an
`AGENTS.md`) in one run, so a single command from the top cleans + prunes + refreshes the open-tasks list
everywhere. From **inside a project** it reconciles just that workspace. Each repo commits and re-anchors
(`--set-anchor`) separately.

### End-of-Task checklist (before saying "done" on anything that produced changes)
- ☐ `walkthrough.md` (what changed + real pasted test output + "Your Actions" with the exact git command)
- ☐ `task-list.md` snapshot of the final TodoWrite list
- ☐ `active-context.md` updated (the hand-off)
- ☐ `INDEX.md` row appended
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
  **later superseded 2026-06-25 by the work-from-cwd model** — see Part 2).
- `prose-formatting.md` repointed off the dead `_claude_artifacts/` store.
- `_experiment/` → `_routing-canary/`.

**Resolved 2026-06-27 — `_claude_artifacts/` fully retired:**
- The `1_*` commands (`1_run-all-tests-back_front`, `1_make-workflow-from-chat`, `1_check-for-tech-stack-updates`)
  and the `autopilot-dev-story.ps1` engine were repointed off `_claude_artifacts/` → `_artifacts/` at the master
  `.agents/` source and across every synced copy. Fresh-workspace (clean-bmad-workspace) was converted to the
  project-local `_artifacts/` model (matching aviationChat) and its dead `_claude_artifacts/` store was deleted.
  Ignore-lists keep the name defensively; historical mentions (a skill's origin-session paths) are left as
  accurate history.

**Retire-list (follow-up reconcile pass — NOT yet done; some are engine-coupled):**
- Cleanup unrelated to the artifact store: `(some) @.agent/` singular paths + `your-action-required.md` in the
  autopilot docs; per-project copies carrying the opposite git policy, `mandatory-session-artifacts.md`, or dead
  gate files — retired/re-vendored during each project's conversion (separate propagation plan).
- Anti-fork rule (Part 2) is the standing guard so this can't re-accumulate.
