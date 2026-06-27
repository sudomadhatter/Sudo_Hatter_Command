# ROOT LAW — Sudo_Hatter_Command Operating System

Prime mission: Sudo_Hatter_Command is Daniel's **home base**. From here, an agent (Claude, opencode, or
Antigravity/Gemini) routes into the right workspace, loads **only what the task needs**, does the
work, and persists everything to the shared `_artifacts/` memory. The folder is the app; markdown is
the program; you **become** the agent the workspace describes.

## 1. START HERE  (read this — not the whole tree)
1. You are in the LOBBY. Do NOT read the whole tree; that burns tokens. Least-context loading is the whole game.
2. A routing / "what should I work on" / ownership question → read `router.md`.
3. Working inside a project → read THAT project's `AGENTS.md` (its workspace map), not this file.
4. Before any risky/irreversible action → see §6 GATES.
5. Continuity ("pick up" / "hand off") → see §7 PERSISTENCE.
6. Before editing any file outside `_artifacts/` → an approved `implementation_plan.md` is required (see §3 gate).

## 2. MAP / MISSION / SUPPORT  (answer these for every task — then you're never lost)
- **MAP** — where am I, where can I go?   → `router.md` (lobby) → a workspace `AGENTS.md` (floor)
- **MISSION** — what is the work here?     → the target workspace's `AGENTS.md` routing table
- **SUPPORT** — what tools/skills/context? → `.agents/skills/`, `.agents/commands/`, pulled per the table

## 3. ALWAYS-LOAD  (small by design)
Load now: `.agents/rules/constitution.md` (hard stops + gates), `.agents/rules/karpathy-guidelines.md`
(how to work), and `.agents/rules/artifacts-always-first.md` (the plan-first gate — see below). Everything
else in `.agents/rules/` loads **on demand** when a task calls for it — do not preload the rest. The full
rule set is the shared toolkit, not a startup payload. How a workspace is shaped + kept healthy →
`_docs/workspace-standard.md`.

> **Web/mobile session?** When env **`CLAUDE_CODE_REMOTE=true`** (Claude Code on the web or phone), also
> load `.agents/rules/mobile-mode.md` — the web/mobile lane: it adapts git, the approval gate, artifacts,
> and verification for a device with no terminal. On a desktop IDE session the var is unset → ignore it and
> use the desktop defaults. `mobile-mode.md` owns the trigger (single source for the lane boundary).

> **⛔ ARTIFACTS — MANDATORY FIRST ACTION.** Before modifying ANY file outside `_artifacts/`, write an
> `implementation_plan.md` into the right `_artifacts/` for where you work from (§5) and **STOP until Daniel says "approved."** Track
> work with a live TodoWrite list; close with `walkthrough.md` + `task-list.md`. **This applies at the lobby
> too — not only inside projects.** Full protocol → `.agents/rules/artifacts-always-first.md`. (Skip only for
> read-only/investigatory asks and trivial one-liners.)

## 4. WHAT LIVES WHERE  (home-base infrastructure)
| Area | Path | Purpose |
|---|---|---|
| Master toolkit | `.agents/` | rules · commands · skills · workflows · bmad · scripts · templates (single source of authorship) |
| Shared memory | `_artifacts/` | every agent's plans/walkthroughs/handoffs; `INDEX.md` ledger; per-workspace `active-context.md` |
| Docs | `_docs/` | home-base documentation (master implementation plan, workspace standard) |
| Navigation index | `_docs/repo-map.md` | the lobby's repo-map (curated header + auto body); drift-checked at SessionStart |
| Routing canary | `_routing-canary/` | model-agnostic proof the routing works (Claude/opencode/Antigravity) |
| System builder | `_system/` | how to add/maintain workspaces (`/new-project`, `/sync-agents`) |
| Lobby tool dirs | `.claude/`, `.opencode/` | synced copies of the master so `/commands` + skills resolve here. `/sync-agents` mirrors `.agents/commands/` to all three platforms (incl. the opencode + Antigravity machine-global caches); `platforms:` frontmatter limits a command's reach |
| Projects | `Projects/<name>/` | the actual projects, each its own git repo |

## 5. NAMING CONVENTIONS  (this replaces a database)
- Dated output: `YYYY-MM-DD_<slug>.md`
- Versioned drafts: `<slug>_draft.md`, `<slug>_v2.md`, `<slug>_final.md`
- Artifacts go **where you work FROM** (not just what the work is about). Three rules decide the bucket:
  1. **Project work** → a per-project bucket `_artifacts/<project-folder-name>/` (e.g. `_artifacts/aviationChat-AGY/`,
     `_artifacts/clean-bmad-workspace/`; the bucket = the `Projects/<name>/` folder name). **Create it if it
     isn't there yet; otherwise reuse it.**
  2. **Main / home-base / cross-project work** (routing, the `.agents/` toolkit, the standard, multi-project) →
     the home-base bucket `_artifacts/_main/` (formerly `_home`).
  3. **Stories** → nest under the parent **epic folder**: `<epic>/<story>/` (create the epic folder if missing).
     Random/system tasks → `<YYYY-MM-DD>_<slug>/`; retired → `_archived/`.
  - **From the home base** (this folder is your cwd) → home-base `_artifacts/` per rules 1–3; append a row to
    `_artifacts/INDEX.md`. **From inside a project** (`Projects/<name>/` is your cwd) → **follow THAT project's
    rules**: project-local `Projects/<name>/_artifacts/…` + its own `active-context.md`/`INDEX.md` (there is no
    `_main` inside a project — every task there is that project's work).
  - **opencode** writes under its own `_artifacts/opencode/` namespace and applies the **same three rules inside
    it**: `opencode/<project>/`, `opencode/_main/`, `opencode/<project>/<epic>/<story>/`.
  - Full model → `_docs/workspace-standard.md`.
- Memory / active-context sections are NUMBERED (e.g. 5.2) so agents **skip-to-N** instead of reading all.

## 6. GATES  (consult before acting)
- **ROUTING GATE**: confirm the target workspace via `router.md` before touching files in it.
- **RISK GATE**: never delete / overwrite / publish without explicit go-ahead. **GIT — desktop default:**
  never run `git commit`/`push` yourself — hand Daniel the command unless he delegates it in the moment
  (→ `.agents/rules/git-policy.md`). On **web/mobile** (`CLAUDE_CODE_REMOTE=true`) the agent owns git
  delivery instead (commits/pushes its own files, asks before the PR) → `.agents/rules/mobile-mode.md`; on
  desktop the var is unset → ignore that file.
- **GIT WRITE APPROVAL — free on your OWN branch; the button on the owner's.** (Canonical source of the
  branch model → `.agents/rules/git-policy.md` § "Branch model — `main_debug` → `main`".) The gate keys on
  WHERE a write lands, not the act of pushing.
  - **FREE**: push freely to your own `claude/*` session branch; open/update PRs. (Loops/retries are fine.)
  - **APPROVAL** (per-action, never carries forward): any write to the owner's branches — a direct
    `git push` to `main_debug`/`main`, or merging a PR into them.
  - `main` is extra-protected: never push/PR/merge to it; promoting `main_debug` → `main` is the owner's
    deliberate manual decision. (Web/mobile clone/fork specifics → `.agents/rules/mobile-mode.md`.)
  - *Enforcement note:* a PreToolUse hook (canonical `.agents/hooks/require-push-approval.py`, deployed to
    every `.claude/hooks/` by `/sync-agents`) forces the prompt on
    any `git push` targeting `main`/`main_debug` however wrapped; `merge_pull_request` is gated in
    `.claude/settings.json`. Pushes to `claude/*` and PR create/update are NOT gated. Approve a merge into
    `main_debug` by invoking `/merge_main_debug` — invoking it IS the per-action approval.
- Full hard stops + "ask first" list → `.agents/rules/constitution.md`.

## 7. PERSISTENCE  (you own this — not a vendor)
- **Where it lives — decided by where you work FROM.** Working **from the home base** → home-base `_artifacts/`
  (`_artifacts/<project>/active-context.md` for a project worked on from here; `_artifacts/_main/active-context.md`
  for home-base work) + the home-base `_artifacts/INDEX.md` ledger. Working **from inside a project**
  (`Projects/<name>/` open) → that project's own `_artifacts/active-context.md` + `INDEX.md` (follow its rules).
- **"pick up"** → read-only continuity brief from the right `active-context.md` for where you're working from.
  Don't change anything; don't explain the obvious. **Also surface open tasks:** after the `active-context.md`
  brief, read this workspace's `_my_resources/open_tasks/todo_list.md` (+ any plan/PRP `.md` notes alongside it)
  and add a one-line "what's queued." **READ-ONLY** — Daniel's notes; never edit; cross-check vs live files.
  (Same source the "what's next / open tasks / what's left" routing trigger uses → `router.md`.)
- **"hand off"** → write current state to that `active-context.md`, append a row to the matching `INDEX.md`,
  then read it back and verify without relying on chat memory.
- Full protocol → `.agents/rules/artifacts-always-first.md`. Full model → `_docs/workspace-standard.md`.

## 8. PORTABILITY
`AGENTS.md` is the universal contract; `CLAUDE.md` and `GEMINI.md` are one-line adapters that point
here. Nothing model-specific lives in shared files — so Claude, opencode, and Antigravity all drive
the same system, and your work is saved to **your** files, not a vendor's memory. One canonical command
set (`.agents/commands/`) mirrors to all three via `/sync-agents`; a command opts out of a platform with
`platforms:` frontmatter (default = everywhere). Full model → `_docs/workspace-standard.md`.
