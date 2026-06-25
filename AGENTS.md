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

> **Web/mobile session?** If you're running in a remote container (Claude Code on the web or phone),
> also load `.agents/rules/mobile-mode.md` — it adapts git, the approval gate, and verification for a
> device with no terminal.

> **⛔ ARTIFACTS — MANDATORY FIRST ACTION.** Before modifying ANY file outside `_artifacts/`, write an
> `implementation_plan.md` into `_artifacts/<workspace>/…` and **STOP until Daniel says "approved."** Track
> work with a live TodoWrite list; close with `walkthrough.md` + `task-list.md`. **This applies at the lobby
> too — not only inside projects.** Full protocol → `.agents/rules/artifacts-always-first.md`. (Skip only for
> read-only/investigatory asks and trivial one-liners.)

## 4. WHAT LIVES WHERE  (home-base infrastructure)
| Area | Path | Purpose |
|---|---|---|
| Master toolkit | `.agents/` | rules · commands · skills · workflows · bmad · scripts · templates (single source of authorship) |
| Shared memory | `_artifacts/` | every agent's plans/walkthroughs/handoffs; `INDEX.md` ledger; per-workspace `active-context.md` |
| Docs | `_docs/` | home-base documentation (the master implementation plan, etc.) |
| Routing canary | `_routing-canary/` | model-agnostic proof the routing works (Claude/opencode/Antigravity) |
| System builder | `_system/` | how to add/maintain workspaces (`/new-project`, `/sync-agents`) |
| Lobby tool dirs | `.claude/`, `.opencode/` | synced copies of the master so `/commands` + skills resolve here |
| Projects | `Projects/<name>/` | the actual projects, each its own git repo |

## 5. NAMING CONVENTIONS  (this replaces a database)
- Dated output: `YYYY-MM-DD_<slug>.md`
- Versioned drafts: `<slug>_draft.md`, `<slug>_v2.md`, `<slug>_final.md`
- Artifacts: `_artifacts/<workspace>/<YYYY-MM-DD>_<slug>/…`  (`<workspace>` = project name, or `_home`)
- Memory / active-context sections are NUMBERED (e.g. 5.2) so agents **skip-to-N** instead of reading all.

## 6. GATES  (consult before acting)
- **ROUTING GATE**: confirm the target workspace via `router.md` before touching files in it.
- **RISK GATE**: never delete / overwrite / publish without explicit go-ahead. Never run `git commit`/`push`
  yourself — hand Daniel the command unless he delegates it in the moment (→ `.agents/rules/git-policy.md`).
- Full hard stops + "ask first" list → `.agents/rules/constitution.md`.

## 7. PERSISTENCE  (you own this — not a vendor)
- **"pick up"** → read-only continuity brief from `_artifacts/<workspace>/active-context.md` (+ recent `INDEX.md` rows). Don't change anything; don't explain the obvious.
- **"hand off"** → write current state to `_artifacts/<workspace>/active-context.md`, append a row to `_artifacts/INDEX.md`, then read it back and verify without relying on chat memory.
- Full protocol → `.agents/rules/artifacts-always-first.md`.

## 8. PORTABILITY
`AGENTS.md` is the universal contract; `CLAUDE.md` and `GEMINI.md` are one-line adapters that point
here. Nothing model-specific lives in shared files — so Claude, opencode, and Antigravity all drive
the same system, and your work is saved to **your** files, not a vendor's memory.
