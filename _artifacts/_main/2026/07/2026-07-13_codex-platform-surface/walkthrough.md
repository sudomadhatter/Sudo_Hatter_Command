---
IsArtifact: true
ArtifactMetadata:
  title: Add Codex (OpenAI) as the 4th command surface — walkthrough
  type: walkthrough
  date: 2026-07-13
---

# Walkthrough — Codex as the 4th platform

**Outcome:** Codex now has the full toolkit — rules, skills, `/` commands, and all 56 BMAD skills — on this
machine, and `/sync-agents` lays it down on any machine in one command. A per-machine
[setup guide](../../../_my_resources/open_tasks/2026-07-13_codex-setup-all-machines.md) is in `open_tasks/`.

## What changed & why

The core insight from the doc recon: **Codex is the lightest surface to add.** It reads `AGENTS.md` natively
AND discovers Agent Skills from `.agents/skills/` (the open standard) — so **rules and our own skills needed
zero work**. Only two things had to be pushed to it, both machine-global caches parallel to the existing
opencode/Antigravity ones:

1. **`/` commands → `~/.codex/prompts`** (Codex's `/commands` equivalent, invoked `/prompts:<name>`).
2. **BMAD skills → `~/.codex/skills`** — because BMAD installs its 56 `bmad-*` skills to `.claude/skills`
   (manifest `ides: [claude-code, antigravity]`), which Codex does **not** read. You said "we use bmad in
   everything," so I mirror them into a dir Codex *does* read. Codex then invokes BMAD via `/skills` — same
   model as Claude, no duplicate `/prompts:` stub.

### File-by-file

**Engine — [.agents/scripts/sync-agents.ps1](../../../../../.agents/scripts/sync-agents.ps1)**
- `$AllPlatforms` gained `'codex'` → commands with no `platforms:` key stay universal and now reach Codex.
- Added a `codex` entry to the machine-global `$caches` array → `~/.codex/prompts` (mirror-exact, `bmad-*`
  preserved — harmless there).
- **New `Sync-CodexSkills` function** + call: per-dir robocopy `/MIR` of each `.claude/skills/bmad-*` into
  `~/.codex/skills/<name>`; purges codex-side `bmad-*` dirs whose source is gone; **preserves `.system` and any
  foreign (non-bmad) dirs**. Guarded like the caches — a broken/missing path warns and skips, never crashes.
- Header/`.PARAMETER`/report-line comments updated three→four platforms.

**Frontmatter (masters in `.agents/commands/`)**
- `+codex` on the 3 interactive sudo commands with **no** skill twin: `sudo-quick-dev`, `sudo-bdd-tests`,
  `sudo-incident-response`.
- The 7 sudo commands that HAVE skill twins were left off codex on purpose — Codex discovers those `sudo-*`
  **skills** natively, so a prompt too would double the menu (same reason `claude` isn't on them).
- **Pinned the 3 `_AP` headless commands** (`sudo-code-review_AP`, `sudo-self-audit_AP`,
  `sudo-dev-story-tests_AP`) to `platforms: [claude, opencode]`. They had **no** key before (= universal),
  which leaked orchestrator-only commands into the Codex *and* Antigravity menus. Bonus: this cleaned 3 stale
  `_AP` ghosts out of the Antigravity global cache (verified below).

**Docs** — [AGENTS.md](../../../../../AGENTS.md) §4 + §8 (four platforms; Codex needs no adapter file),
[sync-agents.md](../../../../../.agents/commands/sync-agents.md) (surfaces, reach, first-machine `-WhatIf` note),
[docs/workspace-standard.md](../../../../../docs/workspace-standard.md) "one master, four platforms" — and the same
edit hand-propagated to **Fresh** (`Projects/Fresh_Workspace_BMAD/docs/workspace-standard.md`) so the
living-template drift check stays green (it did — "Fresh living-template check OK").

**Setup guide** — new
[`_my_resources/open_tasks/2026-07-13_codex-setup-all-machines.md`](../../../_my_resources/open_tasks/2026-07-13_codex-setup-all-machines.md).
Framed setup-now / log-in-later (you haven't linked the account yet — filling the caches is just writing files,
no login needed). `todo_list.md` untouched (read-only carve-out).

## What fought back

Nothing broke, but two things needed care:
- **The `-WhatIf` dry-run reported the codex prompts cache as SKIPPED.** Diagnosed, not a bug: dry-run doesn't
  create `~/.codex/prompts`, so the writability `Test-Path` fails and it skips — same as opencode/Antigravity
  would on a fresh machine. The real run creates the dir first, then copies (proven below). I gave the
  **skills** mirror a `-and -not $WhatIf` guard so it previews correctly regardless, and documented the prompts
  quirk in both the command doc and the setup guide rather than refactor the shared copy path in a sync tool.
- **BMAD location.** Ground-truthed on disk that `bmad-*` skills live in `.claude/skills` (56 of them), are
  excluded from `.agents/skills` by design, and that `.claude/` is git-**tracked** — so a fresh clone already
  carries them and the mirror has a source immediately after clone.

## Test output (pasted)

Real lobby sync (`& ".agents\scripts\sync-agents.ps1"`):
```
sync-agents: antigravity workflow mirror -> 21 sudo-* in .agents/workflows/
sync-agents: .claude\commands   -> 20 cmds
sync-agents: .opencode\commands -> 47 cmds
sync-agents: opencode global -> 47 cmds  (C:\Users\dlohn\.config\opencode\commands)
sync-agents: antigravity global -> 24 cmds  (C:\Users\dlohn\.gemini\antigravity\global_workflows)
sync-agents: codex global -> 17 cmds  (C:\Users\dlohn\.codex\prompts)
sync-agents: codex skills -> 56 bmad-* mirrored  (C:\Users\dlohn\.codex\skills)
sync-agents: Fresh living-template check OK (front-door pattern current).
sync-agents: done.
```

Cache verification:
```
~/.codex/prompts        = 17 files (14 universal + sudo-quick-dev + sudo-bdd-tests + sudo-incident-response)
  3 sudo additions       PRESENT ✓
  skill-twin sudo / _AP / personas (analyst,dev,tea)  ABSENT ✓
~/.codex/skills         = 56 bmad-* dirs, .system PRESERVED ✓
antigravity global      = no _AP files (stale ghosts purged by the [claude,opencode] pin) ✓
```

## Task Checklist
- [x] Doc-verify Codex surfaces (AGENTS.md native, Agent Skills native, custom-prompts `/prompts:`, deprecation)
- [x] `implementation_plan.md` written + approved; revised for the BMAD-mirror + setup-only scope after your answers
- [x] `sync-agents.ps1` — `$AllPlatforms`, codex prompts cache, `Sync-CodexSkills` mirror, comments
- [x] Frontmatter — `+codex` on the 3 skill-less sudo commands; `_AP` trio pinned `[claude, opencode]`
- [x] Docs — AGENTS.md §4/§8, sync-agents.md, workspace-standard.md (lobby + Fresh)
- [x] Setup guide → `_my_resources/open_tasks/2026-07-13_codex-setup-all-machines.md`
- [x] Real lobby sync run; caches verified (17 prompts / 56 skills / _AP purge / Fresh check OK)
- [x] `walkthrough.md` + INDEX row
- [ ] **Deferred (phase 2, your call):** migrate the codex `/prompts` set to skill wrappers before OpenAI
      removes custom prompts; bridge BMAD **opencode-stub** personas if you ever want them as `/prompts` too
      (not needed — the skills mirror already delivers BMAD).

## Your Actions

**1. Verify in Codex once you sign in** (the only step needing the account): open a Codex session at the lobby →
`/prompts:` lists the sudo/1_ commands · `/skills` lists both `sudo-*` and `bmad-*` · a fresh chat quotes
`AGENTS.md` routing. Full checklist in the setup guide §4.

**2. Commit — two repos** (lobby + Fresh are separate git repos; explicit paths per git-policy, no `git add -A`):

Lobby (`main_debug`):
```bash
git add .agents/scripts/sync-agents.ps1 \
  .agents/commands/sudo-quick-dev.md .agents/commands/sudo-bdd-tests.md .agents/commands/sudo-incident-response.md \
  .agents/commands/sudo-code-review_AP.md .agents/commands/sudo-self-audit_AP.md .agents/commands/sudo-dev-story-tests_AP.md \
  .agents/commands/sync-agents.md \
  .agents/workflows/sudo-quick-dev.md .agents/workflows/sudo-bdd-tests.md .agents/workflows/sudo-incident-response.md \
  .claude/commands/sudo-quick-dev.md .claude/commands/sudo-code-review_AP.md .claude/commands/sudo-self-audit_AP.md .claude/commands/sudo-dev-story-tests_AP.md .claude/commands/sync-agents.md \
  .opencode/commands/sudo-quick-dev.md .opencode/commands/sudo-bdd-tests.md .opencode/commands/sudo-incident-response.md \
  .opencode/commands/sudo-code-review_AP.md .opencode/commands/sudo-self-audit_AP.md .opencode/commands/sudo-dev-story-tests_AP.md .opencode/commands/sync-agents.md \
  AGENTS.md docs/workspace-standard.md \
  _my_resources/open_tasks/2026-07-13_codex-setup-all-machines.md \
  _artifacts/INDEX.md _artifacts/_main/2026-07-13_codex-platform-surface/
git commit -m "feat(toolkit): add Codex as the 4th command surface (prompts + BMAD skills mirror)"
```

Fresh (its own repo — `main_debug`):
```bash
cd Projects/Fresh_Workspace_BMAD
git add docs/workspace-standard.md
git commit -m "docs: sync workspace-standard to 'one master, four platforms' (Codex)"
```

**3. On every OTHER machine:** `git pull` at the lobby, then `& ".agents/scripts/sync-agents.ps1"` — it fills
that machine's `~/.codex/prompts` + `~/.codex/skills` (both caches are machine-local, like the opencode/AG
ones). Restart opencode there too, per the usual globals note.
