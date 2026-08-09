---
name: echo-truncates-at-backslash-c
description: "`echo \"$out\"` silently TRUNCATES at a `\\c` sequence — and `.claude\\commands` contains one. Gate greps over captured output then read a cut-off stream and under-report. Use printf '%s\\n'."
metadata:
  type: feedback
---

`echo "$out"` stops dead at a `\c` escape. Any captured output mentioning a Windows-style path
like `.claude\commands` carries one, so **everything after that line vanishes** — no error, no
truncation marker.

Hit on 2026-08-09 (SCC-66): greps over a captured `sync-agents.ps1` run reported **0** Codex-prompt
purges while the purge was working perfectly — the report line sat after `.claude\commands` in the
stream. Nearly recorded a working feature as broken.

**Why:** this is the same shape as [[piping-a-gate-hides-its-exit-code]] — the reading mechanism
corrupts the evidence, so a healthy thing reads as failed (or a failed thing as healthy), and the
output *looks* complete either way.

**How to apply:** print captured output with `printf '%s\n' "$out"`, never `echo "$out"`. Suspect
this first whenever a grep over captured output returns 0 for something you can see happening.
Also watch bare `=====` separators in zsh: a leading `=word` triggers `=cmd` expansion and kills
the rest of a compound command.
