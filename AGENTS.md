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
7. **Entering any folder: if it carries an `AGENTS.md`, read that FIRST** (the local law — how to act
   there); read its `INDEX.md`/`README.md` only when you need the inventory. Tier model (which folders
   get one) → `docs/workspace-standard.md` Part 1.

## 2. MAP / MISSION / SUPPORT  (answer these for every task — then you're never lost)
- **MAP** — where am I, where can I go?   → `router.md` (lobby) → a workspace `AGENTS.md` (floor)
- **MISSION** — what is the work here?     → the target workspace's `AGENTS.md` routing table
- **SUPPORT** — what tools/skills/context? → `.agents/skills/`, `.agents/commands/`, pulled per the table

## 3. ALWAYS-LOAD  (small by design)
Load now: `.agents/rules/constitution.md` (hard stops + gates), `.agents/rules/karpathy-guidelines.md`
(how to work), and `.agents/rules/artifacts-always-first.md` (the plan-first gate — see below). Everything
else in `.agents/rules/` loads **on demand** when a task calls for it — do not preload the rest. The full
rule set is the shared toolkit, not a startup payload. How a workspace is shaped + kept healthy →
`docs/workspace-standard.md`.

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
| Docs | `docs/` | home-base documentation (master implementation plan, workspace standard) |
| Navigation index | `docs/repo-map.md` | the lobby's repo-map (curated header + auto body); drift-checked at SessionStart |
| Routing canary | `_routing-canary/` | model-agnostic proof the routing works (Claude/opencode/Antigravity) |
| System builder | `_system/` | how to add/maintain workspaces (`/new-project`, `/sync-agents`) |
| Lobby tool dirs | `.claude/`, `.opencode/` | synced copies of the master so `/commands` + skills resolve here. `/sync-agents` mirrors `.agents/commands/` to all three platforms (incl. the opencode + Antigravity machine-global caches); `platforms:` frontmatter limits a command's reach |
| Projects | `Projects/<name>/` | the actual projects, each its own git repo |

> **⚠️ SEARCHING THE TREE — GREP IS BLIND TO `Projects/` ONLY FROM THE LOBBY ROOT (lobby-only gotcha).**
> `Projects/` is **gitignored** here (each project is its own git repo nested under the lobby). The **Grep
> tool runs ripgrep, which honors `.gitignore`** — so a Grep whose `path` is the lobby root (or unset)
> **silently skips everything under `Projects/`** and returns zero hits from the project repos. A grep that
> finds a master file in `.agents/` is **not** proof it's the only copy: that same file is **vendored** into
> each `Projects/<name>/.agents/`, and a root-level Grep can't see those.
> **The fix is to go one level down.** Point the Grep tool's `path` *directly at a project repo*
> (`Projects/<name>/` or deeper) and it works fine — that directory is its **own git repo root**, so
> ripgrep starts a fresh ignore context there and never applies the lobby's parent `.gitignore`. So:
> **single project → use the Grep tool with `path: Projects/<name>`** (fast, indexed). **One sweep across
> ALL projects at once → use the Bash tool** (`find Projects -name '<file>'`, then `grep`/`diff` each hit;
> confirm with `git check-ignore <path>`), since a single root-level Grep is blind and you'd otherwise have
> to loop Grep per project. Canonical fix path is unchanged: edit the master `.agents/`, then
> `/sync-agents <project>` to re-vendor.
> *(This caveat is lobby-specific — inside a project you're past the ignore boundary, so don't carry it
> into a project's `AGENTS.md`.)*

## 5. NAMING & ARTIFACT PLACEMENT  (this replaces a database)
Artifacts go **where you work FROM**. The full bucket rules (per-project `_artifacts/<project>/` · home-base
`_artifacts/_main/` · the `opencode/` namespace · story `<epic>/<story>/` · from-home-base-vs-inside-project),
the file-naming patterns (`YYYY-MM-DD_<slug>.md`, `_draft`/`_v2`/`_final`), and numbered memory sections all
live in the always-loaded **`.agents/rules/artifacts-always-first.md`** (§2) · full model →
`docs/workspace-standard.md`. Append every home-base session to `_artifacts/INDEX.md`.

## 6. GATES  (consult before acting)
- **ROUTING GATE**: confirm the target workspace via `router.md` before touching files in it.
- **SEARCH GATE** — a root-level Grep is blind to `Projects/` (ripgrep honors the lobby `.gitignore`) and
  reads as a false "clean"; point Grep at `Projects/<name>` or use Bash. **Full mechanics → §4.**
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
  - Approve a merge into `main_debug` by invoking `/merge_main_debug` — invoking it IS the per-action
    approval. *Hook + settings enforcement mechanics → `.agents/rules/git-policy.md`.*
- Full hard stops + "ask first" list → `.agents/rules/constitution.md`.

## 7. PERSISTENCE  (you own this — not a vendor)
- **Location follows where you work FROM** — home-base `_artifacts/<project|_main>/active-context.md` + the
  `_artifacts/INDEX.md` ledger; the `opencode/` namespace when you're opencode; a project's own `_artifacts/`
  from inside it. Full model → `.agents/rules/artifacts-always-first.md` · `docs/workspace-standard.md`.
- **"pick up"** → read-only continuity brief from the right `active-context.md`, then surface open tasks from
  this workspace's `_my_resources/open_tasks/todo_list.md` (**READ-ONLY** — never edit; cross-check vs live
  files; trigger also → `router.md`). **"hand off"** → write state back, append the matching `INDEX.md` row,
  read it back to verify.

## 8. PORTABILITY
`AGENTS.md` is the universal contract; `CLAUDE.md` / `GEMINI.md` are one-line adapters pointing here (nothing
model-specific in shared files). One command set (`.agents/commands/`) mirrors to all three via `/sync-agents`
(`platforms:` frontmatter opts a command out; default = everywhere). Full model → `docs/workspace-standard.md`.

> **GitNexus** — code-intelligence (impact · detect_changes · query · context) for this repo →
> `docs/gitnexus.md`. (Lobby index is routing-surface only; product work uses `repo: "AGY_AVIATIONCHAT"`.)
