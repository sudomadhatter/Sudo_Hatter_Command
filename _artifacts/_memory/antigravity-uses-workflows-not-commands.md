---
name: antigravity-uses-workflows-not-commands
description: Antigravity (Gemini) surfaces / via WORKFLOWS (.agents/workflows/) + SKILLS (.agents/skills/), never "commands" (a Claude-only concept). Daniel runs the Antigravity IDE, whose paths differ from the CLI and the old install.
metadata:
  type: reference
  originSessionId: 315ab028-3603-4a16-812f-e70b12b06a2f
  modified: 2026-08-13T01:31:04.590Z
---

**Antigravity has no "commands."** Its `/` menu = **workflows** (markdown in `.agents/workflows/`, plural is current default; `.agent/workflows/` singular is legacy/back-compat — verify per version) invoked as `/name`, plus **skills** (`.agents/skills/`, auto-activated, NOT `/`-invoked — the BMAD personas like `bmad-agent-dev` are skills). `commands/` (`.claude/commands/`, `.opencode/commands/`) is a **Claude/opencode-only** concept Daniel got when he added Claude Code. So a capability authored ONLY in `.agents/commands/` is invisible in Gemini — which is exactly why the `sudo-*` flow didn't show in Antigravity (it was never in `.agents/workflows/`).

**Daniel runs the Antigravity *IDE*, not the CLI** — and the installs use different on-disk stores: `~/.gemini/antigravity/` (older, `.pb` conversations), `~/.gemini/antigravity-ide/` (his ACTIVE IDE, sqlite `.db` conversations), and shared `~/.gemini/`. `sync-agents.ps1` writes the global cache to the OLD `~/.gemini/antigravity/global_workflows/` — likely the wrong folder for the IDE, the leading suspect for "global workflows don't work." Confirm the IDE's real global path via the in-app "…" → Workflows → **+ Global** button, then see which file lands on disk.

**Gotchas:** workflow files have a **12,000-char limit**; Antigravity **v1.20.5** has a bug where `/` doesn't trigger workflows (only the "…" dropdown shows them) — fixed in 1.19.6, so check version before concluding a setup is broken.

⛔ **Over-cap TRUNCATES, it does not drop — corrected 2026-08-12 by measurement (SCC-135).** This memory and `sync-agents.ps1` both said "silently dropped" and that wrong word is what kept a live break invisible for weeks: a dropped workflow fails obviously, a **truncated** one runs and looks fine. `/smh-update-maps-indexes` shipped a 39,594-char body; the agent got the header, the target list, Step 0 and half of Step 0.5 (cut mid-sentence), lost 70% of the steps **including the Step 4 approval gate**, then improvised a partial reconcile and edited files with no findings report. **The tell:** a command that starts correctly, does the first mechanical thing right, then goes vague, skips its stop-and-ask, and produces a thinner result than it should. It was the only command whose body lived in `workflows/` while `commands/` held a wrapper — that inversion put it on the sync's `$excluded` list and exempted it from the launcher rule. Now un-inverted; `$excluded` is down to `smh-adviser-board.md` + `INDEX.md`. See [[one-door-per-platform-per-command]].

**12k cap SOLVED structurally (2026-07-25):** `Sync-AntigravityWorkflowMirror` now emits a **GENERATED THIN
LAUNCHER** (≈1.4 KB stub: "read `.agents/commands/<name>.md` and follow it END TO END") for any command over
**11,500 bytes**, instead of a verbatim copy that AG would silently drop. Never byte-golf a near-cap workflow
again — grow the command freely; the mirror handles it. First launcher conversions: `sudo-update-sprint-memory`
(command 13.7k), `sudo-dev-story-tests`, `sudo-code-review` (both were at 11.9k, byte-identical to their
commands — verified before the swap, zero content lost). The hand-authored `sudo-adviser-board` launcher stays
in `$excluded` as before.

**Fix shipped 2026-06-28:** `sync-agents.ps1` now has `Sync-AntigravityWorkflowMirror` — it copies the 6 antigravity-eligible `sudo-*` commands from `.agents/commands/` → `.agents/workflows/` VERBATIM (frontmatter stays line 1, no injected header) so Antigravity sees the dev flow as `/` workflows. ONE source (`commands/`), generated mirrors (regenerated each sync — edit the command, never the workflow copy). Mirrors ONLY `sudo-*` (not BMAD personas = skills, not `1_*` = real workflows) to avoid duplicate `/` entries. Surface chosen: **per-project `.agents/workflows/`** (clone-safe); the old global cache `~/.gemini/antigravity/global_workflows/` is left as harmless legacy (the IDE wasn't reading it). Self-audit was unified: full content now lives in `commands/sudo-self-audit.md` (no proxy), `1_self-audit-stress-test.md` deleted + ghosts purged, dependents (opus-auditor, sudo-self-audit_AP, INDEX) repointed. **PENDING:** Daniel reloads the Antigravity IDE to confirm `/sudo-*` appears (if a `/` entry shows twice, stop the sync writing the global cache). Plan: `_artifacts/_main/2026/06/2026-06-28_antigravity-command-surface-fix/implementation_plan.md`. See [[sudo-commands-have-ap-twins-that-drift]], [[toolkit-sync-covers-agents-not-docs]], [[close-out-command-is-daniels-signoff]].
