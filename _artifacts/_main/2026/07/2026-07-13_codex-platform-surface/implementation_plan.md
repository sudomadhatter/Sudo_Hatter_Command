---
IsArtifact: true
ArtifactMetadata:
  title: Add Codex (OpenAI) as the 4th command surface
  type: implementation_plan
  date: 2026-07-13
---

# Implementation Plan — Codex as a 4th platform (rules + skills + / commands)

**Goal:** Daniel added the OpenAI Codex extension/CLI to the IDE. Wire Codex into the single-source
`.agents/` toolkit so it gets (a) the rules/front-door, (b) the skills, and (c) the `/` command set —
same one-brain model as Claude / opencode / Antigravity. Plus a per-machine setup guide in
`_my_resources/open_tasks/`.

## What the docs say Codex reads natively (verified 2026-07-13, developers.openai.com)

| Surface | Codex mechanism | Work needed |
|---|---|---|
| Rules / front door | Codex reads **`AGENTS.md`** natively (repo root + nested + `~/.codex/AGENTS.md` global) | **NONE** — the lobby and every project already speak AGENTS.md. No `CODEX.md` adapter exists or is needed. |
| Our skills | Codex implements the **open Agent Skills standard**: discovers `$REPO_ROOT/.agents/skills/`, `$CWD/.agents/skills/`, `$HOME/.agents/skills/` (+ its own `~/.codex/skills/`) | **NONE** — the master toolkit IS `.agents/skills/`. Our own skills (7 `sudo-*` dev-flow + gitnexus + workspace-structure …) are already visible in the lobby and vendored into projects. |
| **BMAD skills** | Same standard — BUT the 56 `bmad-*` skills live in **`.claude/skills`** (BMAD installs there; manifest `ides: [claude-code, antigravity]` only) and are **excluded from `.agents/skills`**. Codex reads `.agents/skills` + `~/.codex/skills`, **not** `.claude/skills`. | **NEW mirror** — Daniel: "we use bmad in everything." Sync mirrors `.claude/skills/bmad-*` → **`~/.codex/skills/`** (a machine-global cache, parallel to the prompts cache). Codex then invokes BMAD natively via `/skills` — same model as Claude, no duplicate `/prompts:` stubs. `.claude/` is git-**tracked**, so a fresh clone already carries the 56 skills → mirror works right after clone+sync (BMAD updates refresh `.claude/skills`, next sync re-mirrors). |
| / commands | **Custom prompts**: `~/.codex/prompts/*.md`, invoked `/prompts:<name>`. Global-only (no repo-level dir). Frontmatter `description:` + `argument-hint:`; supports `$ARGUMENTS`/`$1..$9` — same file format our commands already use. ⚠️ OpenAI marks custom prompts **deprecated in favor of skills** (still fully functional; migration noted below). | **This is the sync work** — a 4th machine-global cache, exactly parallel to the opencode + Antigravity caches. |

Local recon: `~/.codex/` exists on this machine (extension state + `skills/.system`), but `codex` is
not on PATH in PowerShell — the CLI install goes into the setup guide.

## Changes (execution order)

1. **[sync-agents.ps1](.agents/scripts/sync-agents.ps1)** — three edits:
   - `$AllPlatforms = @('claude','opencode','antigravity','codex')` — commands with **no**
     `platforms:` key stay "universal" and now include codex.
   - Add a codex entry to the machine-global `$caches` array:
     `@{ Name='codex'; Platform='codex'; Path=(Join-Path $env:USERPROFILE ".codex\prompts") }` —
     mirror-exact like the other two (the `bmad-*` preserve guard is harmless there).
   - **NEW `Sync-CodexSkills` block** (lobby sync only): mirror each `.claude/skills/bmad-*` dir into
     `~/.codex/skills/<name>` (per-dir robocopy `/MIR`; purge codex-side `bmad-*` dirs whose source is
     gone; **preserve `.system` and any foreign dirs**). Guarded like the caches (broken/missing path →
     warn+skip, never crash). Our own skills need no mirror — Codex reads them from repo `.agents/skills`.
   - Update header comments ("ALL three" → "ALL four") + final report lines.
   - No local-tool-dir work: codex has no repo-level prompts dir; its repo-level surface is
     `.agents/skills/` + `AGENTS.md`, both already vendored into projects by the existing sync.

2. **Frontmatter reach decisions** (edit `.agents/commands/` masters only):
   - **No change** to the 7 sudo commands that have skill twins (`sudo-boot-sprint-memory`,
     `sudo-write-story-tests`, `sudo-dev-story-tests`, `sudo-self-audit`, `sudo-code-review`,
     `sudo-update-sprint-memory`, `sudo-create-epics-stories-sprint`) — Codex discovers the skills
     natively; adding the prompt too would create duplicate `/` entries (same reason `claude` isn't
     in their lists).
   - **Add `codex`** to the 3 interactive sudo commands with **no** skill twin:
     [sudo-quick-dev.md](.agents/commands/sudo-quick-dev.md),
     [sudo-bdd-tests.md](.agents/commands/sudo-bdd-tests.md),
     [sudo-incident-response.md](.agents/commands/sudo-incident-response.md).
   - **Pin the 3 `_AP` headless commands** (`sudo-self-audit_AP`, `sudo-code-review_AP`,
     `sudo-dev-story-tests_AP`) to `platforms: [claude, opencode]` — today they carry no key
     (= universal), which would leak orchestrator-only commands into the codex (and Antigravity
     global) menus. The two autopilot engines that invoke them run on claude + opencode only.
   - **No codex** on the BMAD persona/testarch opencode bridges — Codex gets BMAD via the native
     `~/.codex/skills` mirror (change #1), so a `/prompts:` stub would double the menu entry (same
     reason claude isn't on them). Also **no codex** on `autopilot_*` (claude/opencode engines only).
   - Net codex prompt set: **14 universal + 3 sudo additions = 17** prompts in `~/.codex/prompts`,
     PLUS the **56 `bmad-*` skills** in `~/.codex/skills` and our repo `.agents/skills` set.

3. **Docs** — [sync-agents.md](.agents/commands/sync-agents.md) (three→four platforms, codex cache,
   report line), [AGENTS.md](AGENTS.md) §4 "Lobby tool dirs" row + §8 Portability (add codex; note it
   needs no adapter file), [.agents/AGENTS.md](.agents/AGENTS.md) platform mentions,
   [docs/workspace-standard.md](docs/workspace-standard.md) portability section — and hand-propagate
   the workspace-standard edit to `Projects/Fresh_Workspace_BMAD/docs/workspace-standard.md` (the
   living-template hash drift check compares them).

4. **Setup guide** → new file `_my_resources/open_tasks/2026-07-13_codex-setup-all-machines.md`
   (`todo_list.md` stays untouched — read-only carve-out). Framed **setup-now / log-in-later**
   (Daniel hasn't linked his account yet — populating the two caches is just writing files, no login
   or `codex` binary needed). Contents: install CLI (`npm i -g @openai/codex`) + IDE extension, pull
   this repo, run `/sync-agents` (or `sync-agents.ps1 -GlobalsOnly`) to fill `~/.codex/prompts` +
   `~/.codex/skills`; **later** sign in and verify (`/prompts:`, `/skills`, AGENTS.md pickup);
   per-machine notes (both caches are machine-local like the opencode/AG caches — re-run sync after
   editing commands or after a BMAD update; `.claude/` is tracked so a clone already has bmad-* to
   mirror), and the custom-prompts deprecation caveat.

5. **Run + verify** — `sync-agents.ps1 -WhatIf` first (preview the codex copy set), then the real
   lobby sync; list `~/.codex/prompts` and check count = 17 and no `_AP`/persona ghosts; existing
   surfaces unchanged (`.claude/commands`, `.opencode/commands`, 2 old global caches). Close with
   `walkthrough.md` (+ Task Checklist + Your Actions incl. the git commit command).

## Open questions
1. **Codex CLI on this machine** — not on PATH; is it only inside the IDE extension? The guide
   assumes the npm CLI per machine; in-IDE verification of `/prompts:` is a Daniel step.
2. **Phase 2?** Bridge BMAD (testarch/personas) to Codex, and/or migrate the codex surface from
   deprecated custom prompts to generated skill wrappers. Not in this task unless you say so.

## Verification plan
- `-WhatIf` preview shows exactly the 17 expected copies to `~/.codex/prompts` and no purges on other surfaces beyond current behavior.
- Post-sync: file count + spot-check `sudo-quick-dev.md` present, `sudo-code-review.md` absent (skill covers it), `sudo-code-review_AP.md` absent.
- Antigravity global cache no longer carries the 3 `_AP` files (intentional cleanup — called out in walkthrough).
- Daniel (in IDE): `/prompts:sudo-quick-dev` resolves; `/skills` lists the sudo-* skills; Codex quotes AGENTS.md routing on a fresh chat.

<!-- CHECKPOINT id="ckpt_mrjkdc70_fg2gr9" time="2026-07-13T18:36:45.180Z" note="auto" fixes=0 questions=0 highlights=0 sections="" -->

<!-- CHECKPOINT id="ckpt_mrjzyyuh_y26fox" time="2026-07-14T01:53:28.553Z" note="auto" fixes=0 questions=0 highlights=0 sections="" -->
