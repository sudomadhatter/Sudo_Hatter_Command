---
description: Sync the master .agents toolkit into a target's tool dirs (lobby or a project).
---

# /sync-agents

Push the master `.agents/` toolkit (commands, skills, opencode-agents) into a target's `.claude/`
and `.opencode/` dirs. For a project target it also vendors the whole `.agents/` so the repo is
clone-safe. **Authorship stays single-source — always edit `.agents/`, never the copies.**

Argument (`$ARGUMENTS`): optional target path. No argument = sync the home-base lobby (root).

Run (PowerShell):

```
& ".agents/scripts/sync-agents.ps1" -Target "$ARGUMENTS"
```

(If `$ARGUMENTS` is empty, run `& ".agents/scripts/sync-agents.ps1"` with no `-Target`.)

After it runs, report which dirs were updated (`.claude/commands`, `.claude/skills`,
`.opencode/commands`, `.opencode/agent`, and — for a project — the vendored `.agents/`).
