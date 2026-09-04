---
name: codex-is-fourth-platform
description: "Codex (OpenAI) is the 4th LLM command surface; how it's wired into the .agents toolkit and the two machine-global caches it needs."
metadata: 
  node_type: memory
  type: project
  originSessionId: b854c6e3-95bb-4b46-b6b0-725c961a456a
---

Codex (OpenAI) was added as the **4th command surface** alongside Claude / opencode / Antigravity (2026-07-13); Zoo Code became the 5th (SCC-349), and Antigravity remains live as the VS Code extension after its desktop IDE was retired (SCC-378, 2026-09-03).
It is the **lightest** surface because it reads two layers natively:
- **`AGENTS.md`** — native (repo root + nested + `~/.codex/AGENTS.md`). No `CODEX.md` adapter exists or is needed.
- **Agent Skills** — native, open standard: discovers `$REPO_ROOT/.agents/skills` + `~/.codex/skills`. So our
  own skills (sudo-*, gitnexus…) are seen straight from the repo — zero sync work. ⭐ **Antigravity reads
  that same directory** (SCC-394), so one launcher is the door for Claude, Codex and Antigravity — and
  `platforms:` can no longer give a command to Codex without also giving it to Antigravity.

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
Full wiring: `docs/workspace-standard.md` "one master, four platforms" (the per-machine setup
guide it used to cite is gone; the sync itself is the install). Note: this makes
[[autopilot-engine-is-project-local]] a **four**-platform world for the sync surface (autopilot engines are
still claude/opencode/mobile only).

**Mac 2026-08-07 — the caches lie about whether Codex is usable.** `~/.codex/prompts` (18) and
`~/.codex/skills` (56) are written by `/sync-agents -GlobalsOnly`, which does NOT need the Codex CLI
to exist. So a machine can show both caches fully populated while `codex` is not installed at all —
it reads as "Codex is set up" when nothing can invoke it. Check the BINARY, not the caches:
`command -v codex`.

Install on macOS: `brew install --cask codex` — a plain **binary** cask (links `/opt/homebrew/bin/codex`),
so unlike the Temurin `.pkg` cask it needs no interactive sudo and an agent can run it. Verified
0.147.0, resolves in all three zsh modes.

⛔ **Auth is operator-only.** There is **no OpenAI key in `master.env`** (Anthropic + Gemini + Z.ai
only), so the API-key route does not exist here — `codex login` (ChatGPT account, browser OAuth) is
the only path, it needs a real terminal, and backgrounding it wedges exactly like `gh auth login`.
Until it is done `codex login status` says `Not logged in` and `codex doctor` fails only the auth
check. A `⚠ websocket` warning from `doctor` is normal on a healthy fresh install — not a blocker.
Related: [[zshrc-is-invisible-to-automation]].
