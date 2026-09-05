---
name: antigravity-uses-workflows-not-commands
description: Antigravity (Gemini) surfaces / via SKILLS (.agents/skills/) - the same launcher skill Claude and Codex read. Workflows are deprecated and retire 2026-11-01; .agents/workflows/ and the global_workflows machine cache are gone. ONE PC with two sides: Ubuntu-in-WSL runs the Antigravity CLI, the Windows side runs the IDE; before the 2026-11-01 retirement each side had its own workflow cache, and both are now purged.
metadata:
  probe: 'test -z "$(ls -A ~/.gemini/antigravity/global_workflows 2>/dev/null)"'
  type: reference
  originSessionId: 315ab028-3603-4a16-812f-e70b12b06a2f
  modified: 2026-09-04T00:00:00.000Z
---

⭐ **THE ONE RULE: Antigravity's `/` menu is `.agents/skills/`.** Any `.agents/skills/<name>/SKILL.md`
is invoked as `/<name>`, and that is the SAME generated launcher Claude and Codex read — one file, three
platforms. A launcher is a few hundred bytes: "read `.agents/commands/<name>.md` and follow it END TO END".
Commands grow to any size and their door never changes shape. Skills are an **unrestricted bundle** in the
vendor's own words, so **there is no size rule anywhere** — do not re-derive one, do not measure a command
against a cap, do not byte-golf anything.

⛔ **The consequence to know before editing `platforms:`.** `.agents/skills/` is Codex's native surface AND
Antigravity's, so `platforms:` cannot give a command to one without the other. That split was already
fiction: every command declaring `[opencode, antigravity]` carries a hand-authored skill Codex had been
reading all along. Google documents `~/.gemini/config/skills/` as a separate GLOBAL path; nothing of ours
writes it today. See [[one-door-per-platform-per-command]].

⚠️ **The one behaviour cost, accepted.** A launcher only resolves where `.agents/commands/` exists — the
lobby. Under the thin model a project carries no tier-1 copy, so a command invoked inside a project STOPS
and says so rather than running.

⭐ **ONE PC, two sides, and Antigravity runs DIFFERENTLY on each** (measured 2026-09-04; this paragraph
previously said *"Daniel runs the Antigravity IDE, not the CLI"*, which was written for a machine model
that no longer exists and produced four wrong statements to the operator in one afternoon).

| | Ubuntu, inside WSL — **where the work happens** | Windows side |
|---|---|---|
| what runs | the **CLI**, `~/.gemini/bin/agy` | the **IDE** (a Windows app) |
| store | `~/.gemini/antigravity/` | `C:\Users\dlohn\.gemini\antigravity-ide\` (sqlite `.db`) |
| logs | `~/.gemini/antigravity/log/cli-*.log` | — |
| `antigravity-ide/` present? | **no** | yes |
| workflow cache | 40 files, 0 `bmad-*` | 42 files, 2 `bmad-*` |
| the repo it opens | `/home/dlohn/Sudo_Hatter_Command` | `C:\Sudo_Hatter_Command` — a SEPARATE clone |

⛔ **Which cache a sync purges is decided by `$UserHome` in `sync-agents.ps1` — `USERPROFILE` else `HOME`.**
Under WSL `pwsh`, `USERPROFILE` is **empty**, so a sync run from Ubuntu cleans the **Ubuntu** cache and
never touches the Windows one. They are two caches on one machine, not one cache on two machines; each
side needs its own run. Verify, never assume:
`pwsh -NoProfile -Command 'if ($env:USERPROFILE) { $env:USERPROFILE } else { $env:HOME }'`.

⭐ **Runtime proof that the skill door works, from the product rather than a doc:** the CLI's own log
names our launchers by full path — `/home/dlohn/Sudo_Hatter_Command/.agents/skills/smh-close-task-merge-tree/SKILL.md`
and `.../cicd-prune-context/SKILL.md`. That is Antigravity resolving `.agents/skills/<name>/SKILL.md` at
run time, which is stronger evidence than any menu screenshot.

**Gotcha:** v1.20.5 has a bug where `/` doesn't trigger a menu entry (only the "…" dropdown shows them) —
fixed in 1.19.6, so check version before concluding a setup is broken. The **CLI has no skills listing**:
`agy` exposes agent/mcp/models/plugin subcommands and nothing that enumerates skills, so any "count the
Skills panel" instruction is IDE-only and cannot be followed on the Ubuntu side.

⛔ **Never run the vendor's shipped `/migrate-workflows` skill.** It scans `~/.gemini/config/` and
`<workspace>/.agents/workflows/` and renames what it finds to `.md.bak`. Every target `SKILL.md` already
exists here, so it would change nothing except littering. The sync engine IS the migration.

**Superseded history, in three lines so nobody re-derives it.** 2026-06-28 introduced a workflow mirror;
2026-07-25 made it a launcher *only for big commands*, which left the cap a live rule (14 of 40 doors still
shipped verbatim three months later — **a rule you still have to measure against is not a rule you have
removed**); SCC-370 deleted the condition; SCC-394 (2026-09-04) retired the whole surface when the vendor
deprecated workflows for **2026-11-01**, and purged the old `~/.gemini/antigravity/global_workflows/` cache
once per machine. The hazard that drove all of it: Antigravity **truncated** an over-long workflow instead
of rejecting it (SCC-135) — a dropped file fails obviously, a truncated one runs and looks fine.
**The tell, if a door is ever wrong again:** a command that starts correctly, does the first mechanical
thing right, then goes vague, skips its stop-and-ask, and produces a thinner result than it should.
See [[sudo-commands-have-ap-twins-that-drift]], [[toolkit-sync-covers-agents-not-docs]],
[[close-out-command-is-daniels-signoff]].
