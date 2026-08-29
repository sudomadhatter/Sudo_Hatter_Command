# Walkthrough — SCC-346 approval fix + Roo→Zoo / Antigravity→VS Code transition

review-runtime: fan-out
lens_isolation: worktree

- **Lane:** `chore/SCC-346-approval-fix-zoo` (consolidated; rider SCC-349)
- **Plan:** [implementation_plan.md](implementation_plan.md) — batch approval recorded at `ba1cc13`
  (operator, verbatim: "then lets keep pushing and finish this whole ticket")
- **Ticket:** SCC-346 (Bug-typed Task) · rider SCC-349 (Part E)

## What shipped, part by part

- **Part D** (operator-directed, first): the extension migration guide serves VS Code —
  [vscode-ide-extension-migration.md](../../../docs/migrations/install_guides/vscode-ide-extension-migration.md)
  (renamed from `antigravity-ide-extension-migration.md`; `code --install-extension` flow, Roo→Zoo
  Part 0, per-machine checklist + user-settings port table). Inbound links repointed.
- **Part C**: [command-shape.md](../../../.agents/rules/command-shape.md) — run gates BARE (no
  cd-chains, no `; echo "EXIT=$?"` tails, no piped gates); AGENTS.md §6 gate bullet; SOP + changelog
  in the same commit (`3c9e1da`).
- **Part A**: the 77 stable allow rules promoted into tracked
  [.claude/settings.json](../../../.claude/settings.json) with 3 `python` PC twins (80 total); no
  machine-absolute paths (`36f38f8`).
- **Part B**: `zoo-code.allowedCommands` / `deniedCommands` + `zoo-code.useAgentRules` in tracked
  [.vscode/settings.json](../../../.vscode/settings.json); Zoo Code + google-antigravity added to
  [.vscode/extensions.json](../../../.vscode/extensions.json) (`b7b6e36`).
- **Part E** (SCC-349): `zoo` is sync-agents platform 5 —
  [sync-agents.ps1](../../../.agents/scripts/sync-agents.ps1) gained `Sync-ZooSurfaces` generating
  33 [.roo/commands/](../../../.roo/commands/) launchers, [.roomodes](../../../.roomodes) (six BMAD
  personas), per-persona `.roo/rules-<slug>/`, and floor-rule copies in
  [.roo/rules/](../../../.roo/rules/); `zoo` added to the 19 opencode-only masters
  (cicd-autopilot-opencode deliberately kept opencode-only); SOP + changelog same commit (`45e5db8`).
- **Part F**: the three FLOOR rules delivered mechanically on all five platforms —
  [CLAUDE.md](../../../CLAUDE.md) + [GEMINI.md](../../../GEMINI.md) `@` imports,
  [opencode.json](../../../opencode.json) instructions, Zoo via `.roo/rules/` (Part E), Codex via a
  marker-guarded floor block the sync writes into `~/.codex/AGENTS.md` (`9c5eff0`). Verified live:
  this session's own harness injected the three rules from the CLAUDE.md imports.

## Recorded decisions

- The 11 commands declaring `platforms: [opencode, antigravity, claude, codex]` (the main
  smh-/cicd- task-lane doors) were **left untouched** — the approved Declared Change Set names only
  the 20-file `[opencode]` set. Universal commands (no `platforms:` key) reach Zoo automatically
  (33 launchers). Extending the all-four doors to Zoo is a one-line-per-file follow-on if wanted.
- `.roo/` + `.roomodes` are generated-but-TRACKED (they must travel to the PC via git), pruned via
  the GENERATED marker — same contract as the Antigravity workflow mirror; no manifest key needed.
- The machine-global caches on this Mac (opencode, antigravity, codex floor block, codex skills)
  were refreshed from this lane during verification; a post-merge `/smh-sync-agents` from `main`
  re-stamps them from the landed tree.
- AGY repo halves (its allowlist promotion + zoo-code keys) and the `sudo-project-skeleton`
  front-door mirror are DEFERRED — separate repos, ticket per repo; proposed at close-out.

## Evidence

| Claim | Proof |
|---|---|
| Tracked Claude allowlist travels, both spellings, no machine paths | `test_settings_allowlist.py` A1–A4 PASS (count=80, twins=3, bad=[]) |
| Zoo allow/deny lists + extension recommendations travel | B1–B4 PASS |
| Zoo platform 5 wired + surfaces generated | E1–E7 PASS (33 launchers, 6 modes, floor copies present) |
| Floor rules always-on on five platforms | F1–F4 PASS + live confirmation (imports injected into this session) |
| Command-shape rule surfaced | `command-shape.md` exists; AGENTS.md §6 references it; `test_rule_frontmatter.py` 10/10 |
| Guide serves VS Code | guide greps: `code --install-extension` present, no live `agy-ide` step; link gate green |
| Full floor | `run_all.py` 63/63 files @ `9c5eff0` (receipt below) |

## Task Checklist

- [x] 1 Tracked Claude allowlist (A) — test A1–A4
- [x] 2 Zoo allowlist travels via git (B) — test B1–B4
- [x] 3 Command-shape rule exists and is surfaced (C) — rule + AGENTS.md + SOP row
- [x] 4 Migration guide serves VS Code (D) — landed `987f42c`/earlier, link gate green
- [x] 5 Zoo is sync-agents platform 5 (E) — test E1–E7, sync run output pasted in plan lane
- [x] 6 Floor rules always-on everywhere (F) — test F1–F4

## Your Actions

- [ ] **Roo → Zoo import, per machine:** in Antigravity, Roo settings panel → Export; in VS Code,
  Zoo settings panel → Import; then DELETE the export file (it carries API keys — never commit it).
- [ ] **Zoo auto-approve, per machine:** enable the master toggle + tiles once (the allowlists
  themselves arrived via git in `.vscode/settings.json`).
- [ ] **PC pickup:** pull `main` after the merge, run the guide's Part 3–6 (extensions, user
  settings port, `git config --global core.hooksPath .githooks`, `python` spelling check).
- [ ] **DECISION — AVCH ticket for the AGY halves** (promote its 49 local allow rules into tracked
  settings; add its `zoo-code.*` keys) and the skeleton front-door mirror (`@` imports +
  `.roo`/`.roomodes` shape): one ticket per repo, minting is your placement call.
