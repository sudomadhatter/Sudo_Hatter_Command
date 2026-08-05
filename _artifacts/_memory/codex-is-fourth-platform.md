---
name: codex-is-fourth-platform
description: "Codex (OpenAI) is the 4th LLM command surface; how it's wired into the .agents toolkit and the two machine-global caches it needs."
metadata: 
  node_type: memory
  type: project
  originSessionId: b854c6e3-95bb-4b46-b6b0-725c961a456a
---

Codex (OpenAI) was added as the **4th command surface** alongside Claude / opencode / Antigravity (2026-07-13).
It is the **lightest** surface because it reads two layers natively:
- **`AGENTS.md`** — native (repo root + nested + `~/.codex/AGENTS.md`). No `CODEX.md` adapter exists or is needed.
- **Agent Skills** — native, open standard: discovers `$REPO_ROOT/.agents/skills` + `~/.codex/skills`. So our
  own skills (sudo-*, gitnexus…) are seen straight from the repo — zero sync work.

Only **two machine-global caches** are pushed by `/sync-agents` (lobby sync only; both are machine-local like
the opencode/AG caches → re-run per machine):
1. **`~/.codex/prompts`** — Codex's `/commands` equivalent, invoked **`/prompts:<name>`**. Custom-prompts file
   format == ours (`description:`, `$ARGUMENTS`). ⚠️ OpenAI marks custom prompts **deprecated → skills** (works
   today; phase-2 migration = regenerate as skill wrappers).
2. **`~/.codex/skills`** — the **BMAD mirror**. The 56 `bmad-*` skills install to `.claude/skills` (BMAD
   manifest `ides:[claude-code,antigravity]`), which Codex does NOT read, so `Sync-CodexSkills` mirrors them
   there (per-dir robocopy /MIR; purges stale bmad-*; **preserves `.system` + foreign dirs**). `.claude/` is
   git-tracked so a clone already has the source. Extends [[bmad-wrappers-are-opencode-only-bridges]] — Codex
   gets BMAD as real skills (no `/prompts` stub, which would double the menu), same model as Claude.

Frontmatter reach (`platforms:` in `.agents/commands/`): absent = all four. `+codex` only on the 3 skill-less
sudo commands (quick-dev, bdd-tests, incident-response); the 7 with skill twins stay off (native discovery).
The `_AP` autopilot trio is pinned `[claude, opencode]` (was keyless=universal → leaked into codex+AG menus).
Full wiring: `docs/workspace-standard.md` "one master, four platforms"; setup guide at
`_my_resources/open_tasks/2026-07-13_codex-setup-all-machines.md`. Note: this makes
[[autopilot-has-three-drifting-engines]] a **four**-platform world for the sync surface (autopilot engines are
still claude/opencode/mobile only).
