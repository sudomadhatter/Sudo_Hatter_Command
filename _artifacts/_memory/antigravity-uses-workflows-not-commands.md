---
name: antigravity-uses-workflows-not-commands
description: Antigravity (Gemini) surfaces / via WORKFLOWS (.agents/workflows/) + SKILLS (.agents/skills/), never "commands" (a Claude-only concept). EVERY workflow door is a thin launcher - there is no size rule to reason about. The operator runs the Antigravity IDE, whose paths differ from the CLI and the old install.
metadata:
  type: reference
  originSessionId: 315ab028-3603-4a16-812f-e70b12b06a2f
  modified: 2026-08-13T01:31:04.590Z
---

**Antigravity has no "commands."** Its `/` menu = **workflows** (markdown in `.agents/workflows/`, plural is current default; `.agent/workflows/` singular is legacy/back-compat — verify per version) invoked as `/name`, plus **skills** (`.agents/skills/`, auto-activated, NOT `/`-invoked — the BMAD personas like `bmad-agent-dev` are skills). `commands/` (`.claude/commands/`, `.opencode/commands/`) is a **Claude/opencode-only** concept Daniel got when he added Claude Code. So a capability authored ONLY in `.agents/commands/` is invisible in Gemini — which is exactly why the `sudo-*` flow didn't show in Antigravity (it was never in `.agents/workflows/`).

**Daniel runs the Antigravity *IDE*, not the CLI** — and the installs use different on-disk stores: `~/.gemini/antigravity/` (older, `.pb` conversations), `~/.gemini/antigravity-ide/` (his ACTIVE IDE, sqlite `.db` conversations), and shared `~/.gemini/`. `sync-agents.ps1` writes the global cache to the OLD `~/.gemini/antigravity/global_workflows/` — likely the wrong folder for the IDE, the leading suspect for "global workflows don't work." Confirm the IDE's real global path via the in-app "…" → Workflows → **+ Global** button, then see which file lands on disk.

**Gotcha:** Antigravity **v1.20.5** has a bug where `/` doesn't trigger workflows (only the "…" dropdown shows them) — fixed in 1.19.6, so check version before concluding a setup is broken.

⭐ **THE ONE RULE, and it has no number in it (SCC-370, 2026-09-01): EVERY Antigravity door is a thin
launcher.** `Sync-AntigravityWorkflowMirror` emits a few-hundred-byte stub — "read `.agents/commands/<name>.md`
and follow it END TO END" — for every eligible command, unconditionally. Commands grow to any size; their doors
never change shape. **Do not re-derive a size rule, do not measure a command against a cap, do not byte-golf
anything.** The one place the old number is still written down is `/smh-sync-agents`'s `-GlobalsOnly` section,
where it explains WHY the launcher surface exists; `test_command_surfaces.py` CS-18 N/O/P keep it that way.

⛔ **Why the surface exists — as history, not as a rule.** Antigravity **truncates** an over-long workflow
instead of rejecting it (measured, SCC-135). That distinction is the whole hazard: a dropped workflow fails
obviously, a truncated one runs and looks fine. `/smh-update-maps-indexes` shipped a 39,594-char body; the
agent got the header, the target list, Step 0 and half of Step 0.5 (cut mid-sentence), lost 70% of the steps
**including the Step 4 approval gate**, then improvised a partial reconcile and edited files with no findings
report. **The tell, if a truncation ever happens again:** a command that starts correctly, does the first
mechanical thing right, then goes vague, skips its stop-and-ask, and produces a thinner result than it should.

⛔ **The trap this cost two tickets to close: a CONDITIONAL fix leaves the rule alive.** The 2026-07-25 pass
made the launcher conditional on size, and three months later 14 of 40 doors still shipped as full bodies —
`/smh-sync-agents`'s own door sat 1,648 chars under the cap, fine that day and truncated the week its command
grew. Every session still had to hold the number. Deleting the condition is what retired it. **A rule you
still have to measure against is not a rule you have removed.** See [[one-door-per-platform-per-command]].

⚠️ **The one behaviour cost, accepted.** A launcher only resolves where `.agents/commands/` exists — the
lobby. Under the thin model a project carries no tier-1 copy, so **any** command invoked from Antigravity's
*global* menu inside a project now STOPS and says so. `sentry-security-team-avch` is the only genuinely
project-scoped door; run it from the lobby. `$excluded` (never generated, never pruned) is
`smh-adviser-board.md` + `INDEX.md` — the board because its door carries Antigravity-only INLINE-mode
instructions the generator cannot produce, NOT because of its size.

**Superseded history, kept in one line so nobody re-derives it:** 2026-06-28 introduced the mirror,
2026-07-25 made it a launcher *only for big commands*, SCC-370 (2026-09-01) deleted that condition and
made every door a launcher. Below is the
2026-06-28 shape, when command names were still `sudo-*`; read it as archaeology, not as instructions.

**Fix shipped 2026-06-28:** `sync-agents.ps1` now has `Sync-AntigravityWorkflowMirror` — it copies the 6 antigravity-eligible `sudo-*` commands from `.agents/commands/` → `.agents/workflows/` VERBATIM (frontmatter stays line 1, no injected header) so Antigravity sees the dev flow as `/` workflows. ONE source (`commands/`), generated mirrors (regenerated each sync — edit the command, never the workflow copy). Mirrors ONLY `sudo-*` (not BMAD personas = skills, not `1_*` = real workflows) to avoid duplicate `/` entries. Surface chosen: **per-project `.agents/workflows/`** (clone-safe); the old global cache `~/.gemini/antigravity/global_workflows/` is left as harmless legacy (the IDE wasn't reading it). Self-audit was unified: full content now lives in `commands/sudo-self-audit.md` (no proxy), `1_self-audit-stress-test.md` deleted + ghosts purged, dependents (opus-auditor, sudo-self-audit_AP, INDEX) repointed. **PENDING:** Daniel reloads the Antigravity IDE to confirm `/sudo-*` appears (if a `/` entry shows twice, stop the sync writing the global cache). Plan: `_artifacts/_main/2026/06/2026-06-28_antigravity-command-surface-fix/implementation_plan.md`. See [[sudo-commands-have-ap-twins-that-drift]], [[toolkit-sync-covers-agents-not-docs]], [[close-out-command-is-daniels-signoff]].
