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
  9. **PERSISTENCE** — pickup/handoff → `_artifacts/<workspace>/`.

### Layer 2 — the routing table (the single most important thing)
A plain-English table in `AGENTS.md`: **task → read these / skip these / skills**. It is what makes
least-context loading real. Always include the up-route: *"if what you need isn't here, GO BACK to
`../../router.md`."* Routers route up as well as down — an agent can never dead-end.

### Layer 3 — skills (referenced, never preloaded)
Skills live in the vendored `.agents/skills/<name>/SKILL.md` and are pulled **only** by the workspace rows
that call them. Never load skills globally.

### Supporting files every workspace carries
- **`docs/repo-map.md`** — the navigation index (Part 3).
- **`_artifacts/<workspace>/active-context.md`** — continuity (numbered: `1 PRIME`, `5 PICK UP`, `6 HAND OFF`).
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
| ☐ | `_artifacts/<workspace>/active-context.md` exists |
| ☐ | registered as a row in the root `router.md` |
| ☐ | vendored `docs/workspace-standard.md` present |

---

## Part 2 — How to UPKEEP a workspace

Formatting is one-time; upkeep is forever. Who does what, and when.

### Rules: one source, no forks
- **Authored ONLY in `.agents/`.** Copies in `.claude/`, `.opencode/`, and per-project tool dirs are
  **vendored** by `/sync-agents` — never hand-edit a copy; edit the master and re-sync.
- **Project-specific hard-stops** live in that project's local `constitution.project.md` — never by editing a
  vendored generic rule. This is the anti-fork rule that prevents the drift this whole standard exists to fix.

### Git — one policy
Never run `git commit`/`git push` yourself; the `walkthrough.md` "Your Actions" hands Daniel the exact command.
The only exception is when Daniel explicitly delegates a specific commit/push in the moment. Full rule →
`.agents/rules/git-policy.md`.

### Artifacts — the plan-first discipline
Every non-trivial, file-touching task: research read-only → write `implementation_plan.md` and **STOP for
"approved"** → execute with a live TodoWrite list → close with `walkthrough.md` (+ "Your Actions") and a
`task-list.md` snapshot → append one row to `_artifacts/INDEX.md` → update `active-context.md` (the hand-off).
Full rule → `.agents/rules/artifacts-always-first.md`.

**Artifact organization — artifacts live WITH the work they're about (Daniel, 2026-06-25):**
- **Project work** (the work is about a `Projects/<name>/` repo — even if launched from the home base) →
  **PROJECT-LOCAL** `Projects/<name>/_artifacts/`. The project owns its history so it travels with the repo;
  Daniel works inside each project directly. Each project keeps its own `_artifacts/active-context.md`
  (+ optional `_artifacts/INDEX.md`).
- **Home-base / cross-project work** (the work is about the home base itself — routing, the toolkit, multi-project)
  → home base `_artifacts/_home/<YYYY-MM-DD>_<slug>/`, logged in the home-base `_artifacts/INDEX.md`.
- **The test is what the work is ABOUT, not where you launched it.** The lab where you *test* is not the bucket.
- Within either location: **random task** → `<YYYY-MM-DD>_<slug>/`; **story** → `<epic>/<story>/` (epic folder
  houses its stories); retired history → `_archived/`.
- **The home base finds a project's history** at `Projects/<name>/_artifacts/` (+ that project's
  `active-context.md`). The home-base `_artifacts/` holds only `_home/` — not per-project buckets.

### Routing canary — the regression cadence
`_routing-canary/` is a permanent check, not a one-time demo. **Re-run it when** you change routing structure
(`AGENTS.md`/`router.md`/the adapter-skill pattern) or qualify a new LLM/CLI. A green run proves the
*mechanism* works in that tool; it does NOT prove your real routing is correct — for that, run the cold-route
test ("work on X" from a fresh session lands in the right workspace). Full how/when → `_routing-canary/README.md`.

### Router + repo-map drift
- Add/remove/convert a workspace → update its row in the root `router.md` (lobby = categories only).
- Repo-map: the SessionStart hook *detects* drift and nags; the human/agent *supplies the purpose line* at
  end-of-task — and only when a top-level folder or an agent was added/removed (Part 3).

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
- `constitution.md` + `artifacts-always-first.md` reconciled to it; both write to `_artifacts/<workspace>/`.
- `prose-formatting.md` repointed off the dead `_claude_artifacts/` store.
- `_experiment/` → `_routing-canary/`.

**Retire-list (follow-up reconcile pass — NOT yet done; some are engine-coupled):**
- `.agents/workflows/autopilot_bmad_dev_loop.md` + `.agents/commands/{autopilot, 1_ccps_update-active-context,
  1_check-for-tech-stack-updates, 1_run-all-tests-back_front, 1_make-workflow-from-chat}` still reference
  `_claude_artifacts/` and (some) `@.agent/` singular paths + `your-action-required.md`. **The autopilot engine
  (`autopilot-dev-story.ps1`) must be checked before moving its artifact paths** — docs and engine must move
  together or a new contradiction is created.
- Per-project copies still carrying `_claude_artifacts/`, the opposite git policy, `mandatory-session-artifacts.md`,
  or dead gate files — retired/re-vendored during each project's conversion (separate propagation plan).
- Anti-fork rule (Part 2) is the standing guard so this can't re-accumulate.
