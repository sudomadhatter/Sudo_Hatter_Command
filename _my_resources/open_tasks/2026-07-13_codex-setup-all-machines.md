# Codex Setup — Every Machine (rules · skills · `/` commands · BMAD)

**Date:** 2026-07-13 · **Author:** Claude (Fable 5), from the command center
**Goal:** get OpenAI **Codex** wired into the single-source `.agents/` toolkit on every machine — same rules,
skills, `/` commands, and full BMAD that Claude / opencode / Antigravity already have.

> **Status: setup-now, log-in-later.** You have NOT linked Codex to your account yet — that's fine. Everything
> below just *writes files to disk* (`~/.codex/prompts` + `~/.codex/skills`); no login or `codex` binary is
> needed to lay the toolkit down. Sign in whenever you're ready and it's all already there. The one-time
> **verify** steps (§4) need the login, so do those after you connect the account.

---

## 0. Why Codex needs so little

Codex is the **lightest** of the four surfaces because it natively speaks two of our three layers — verified
against OpenAI's docs (2026-07-13):

| Layer | How Codex gets it | Work on our side |
|---|---|---|
| **Rules / front door** | Codex reads **`AGENTS.md`** natively (repo root + nested + `~/.codex/AGENTS.md`). Our lobby and every project already speak AGENTS.md. | **None.** No `CODEX.md` adapter exists or is needed. |
| **Our skills** (sudo-*, gitnexus, workspace-structure…) | Codex implements the **open Agent Skills standard** — discovers `$REPO_ROOT/.agents/skills` + `~/.codex/skills`. Our skills live in `.agents/skills`. | **None.** Seen from the repo automatically. |
| **BMAD skills** (the 56 `bmad-*`) | Same standard — BUT BMAD installs these to **`.claude/skills`** (its manifest targets `ides: [claude-code, antigravity]`), which Codex does **not** read. | **Mirror** `.claude/skills/bmad-*` → `~/.codex/skills` (done by `/sync-agents`). |
| **`/` commands** (`/sudo-*`, `/1_*`, etc.) | Codex's `/commands` equivalent is **custom prompts** in `~/.codex/prompts`, invoked **`/prompts:<name>`**. | **Sync** the command set → `~/.codex/prompts` (done by `/sync-agents`). |

So the whole integration is: **run `/sync-agents` once per machine** to fill the two Codex caches. That's it.

> ⚠️ **Deprecation note (not blocking):** OpenAI marks *custom prompts* as deprecated in favor of *skills*.
> They still work fully today. If they're ever removed, the migration is to regenerate the `/prompts` set as
> skill wrappers — a future toolkit change, transparent to you. Your BMAD + our own skills already ride the
> non-deprecated skills path.

---

## 1. Install Codex (per machine)

1. **CLI** (optional but recommended — enables `/sync-agents` verification and headless use):
   ```powershell
   npm install -g @openai/codex
   codex --version   # confirm it's on PATH
   ```
2. **IDE extension** — install the OpenAI Codex extension in the IDE (VS Code / Antigravity). This is what you
   already did on this machine.
3. **Sign in — whenever you're ready.** Link Codex to your account via the extension or `codex` login. *Setup
   below does not require this;* only the §4 verification does.

---

## 2. Get the repo + lay down the toolkit

On each machine, from the **command-center lobby root** (`Sudo_Hatter_Command/`):

```powershell
# 1. Make sure the repo is present and current (Codex reads AGENTS.md + .agents/skills straight from it)
git pull                      # or clone it if this is a fresh machine

# 2. Fill the two Codex caches (prompts + bmad-* skills mirror) — plus refresh the other globals
& ".agents/scripts/sync-agents.ps1"
#    ^ no -Target = lobby sync = refreshes ALL machine-global caches (opencode, Antigravity, Codex)

# (or, to touch ONLY the global caches and skip local tool dirs:)
& ".agents/scripts/sync-agents.ps1" -GlobalsOnly
```

You can run `/sync-agents` from inside the IDE instead of the raw script — same thing.

**What it writes for Codex** (on a lobby sync):
- `~/.codex/prompts/*.md` — the codex-eligible `/` commands (invoked `/prompts:<name>`).
- `~/.codex/skills/bmad-*/` — all 56 BMAD skills mirrored from `.claude/skills` (invoked via `/skills`).

Expected tail of the run:
```
sync-agents: codex global -> <N> cmds  (C:\Users\<you>\.codex\prompts)
sync-agents: codex skills -> 56 bmad-* mirrored  (C:\Users\<you>\.codex\skills)
```

> **First-machine gotcha:** if you `-WhatIf` (dry-run) on a brand-new machine, the codex **prompts** cache
> shows as **SKIPPED** ("path not writable") — that's just because the `~/.codex/prompts` dir doesn't exist
> yet and dry-run won't create it to test. A **real** run creates it first, then copies. (Same is true for the
> opencode/Antigravity caches on a fresh box.) The **skills** mirror previews fine under `-WhatIf`.

---

## 3. What lands where (mental model)

```
.agents/  (master, single source — edit here, never the copies)
   ├── commands/   ──/sync-agents──►  ~/.codex/prompts/     (Codex /prompts:<name>)
   ├── skills/     ──read in place──►  Codex reads $REPO_ROOT/.agents/skills natively
   └── rules/, AGENTS.md ──read in place──►  Codex reads AGENTS.md natively
.claude/skills/bmad-*  ──/sync-agents mirror──►  ~/.codex/skills/bmad-*   (Codex /skills)
```

- **Both Codex caches are machine-local** (exactly like the opencode + Antigravity global caches). They do NOT
  travel through git — that's why every machine runs its own `/sync-agents`.
- **Re-run `/sync-agents` after:** editing any command in `.agents/commands/`, or after a **BMAD update**
  (which refreshes `.claude/skills/bmad-*` — the sync then re-mirrors them to Codex).
- `.claude/` is **git-tracked**, so a fresh clone already carries the 56 `bmad-*` skills → the mirror has
  something to copy even before you install/refresh BMAD locally.

---

## 4. Verify (after you sign in)

In a Codex session opened at the lobby (or any project):

1. **Rules** — start a fresh chat and ask *"what's the routing law here?"* → Codex should quote `AGENTS.md`
   (START HERE / router). Proves native AGENTS.md pickup.
2. **`/` commands** — type `/prompts:` and confirm the sudo/1_ commands appear; e.g. `/prompts:sudo-quick-dev`.
3. **Our skills** — `/skills` should list the `sudo-*`, `gitnexus-*`, `workspace-structure` skills (from the
   repo `.agents/skills`).
4. **BMAD** — `/skills` should also list the `bmad-*` set (from `~/.codex/skills`). Try invoking
   `bmad-help` or a persona (`bmad-agent-dev`) — because BMAD's `_bmad/` module lives in the repo, the skill
   resolves its config the same way it does under Claude.

If a `bmad-*` skill is missing from `/skills`: re-run `/sync-agents` (the mirror only runs on a **lobby** sync,
not a project sync), and confirm `.claude/skills/bmad-*` exists on that machine.

---

## 5. Reach map — what Codex does and doesn't get (by design)

| Command group | On Codex? | Why |
|---|---|---|
| Universal `/` commands (no `platforms:` key) — `sync-agents`, `1_*`, `new-project`, `merge_main_debug`, `webm-alpha-video`, `slash_command_updating` | ✅ prompts | default = everywhere |
| `sudo-quick-dev`, `sudo-bdd-tests`, `sudo-incident-response` | ✅ prompts | interactive sudo commands with **no** skill twin |
| `sudo-boot/write/dev/self-audit/code-review/update/create-*` (7) | ✅ **as skills**, not prompts | Codex discovers the `sudo-*` **skills** natively from `.agents/skills`; a prompt too would double the menu |
| All `bmad-*` (personas, testarch, workflows) | ✅ **as skills** (via `~/.codex/skills` mirror) | "we use bmad in everything" — mirrored, not stubbed |
| `*_AP` (autopilot headless: self-audit / code-review / dev-story) | ❌ | pinned `[claude, opencode]` — only the claude/opencode autopilot engines invoke them |
| `autopilot_claude` / `autopilot_opencode` / `autopilot_mobile` | ❌ | engine-specific (need the claude or opencode CLI) |
| BMAD **opencode bridge stubs** (`analyst`, `dev`, `tea`, `testarch-*`, …) | ❌ | opencode-only bridges; Codex gets the real skills directly, so the stub would be a duplicate |

---

## 6. Per-machine checklist (copy this)

- [ ] `npm install -g @openai/codex` (+ IDE extension installed)
- [ ] repo cloned/pulled at the lobby root, current with `main`
- [ ] ran `& ".agents/scripts/sync-agents.ps1"` from the lobby → saw the two `codex` report lines
- [ ] `~/.codex/prompts` populated · `~/.codex/skills/bmad-*` = 56 dirs
- [ ] (after sign-in) `/prompts:`, `/skills`, AGENTS.md pickup all verified
- [ ] re-run `/sync-agents` whenever commands change or BMAD updates

---

*Toolkit is single-source: always edit `.agents/` at the lobby, never the machine caches, then re-sync.
Engine + full policy: [sync-agents.ps1](../../.agents/scripts/sync-agents.ps1) ·
[/sync-agents doc](../../.agents/commands/sync-agents.md) ·
[workspace-standard.md](../../docs/workspace-standard.md) “one master, four platforms”.*
