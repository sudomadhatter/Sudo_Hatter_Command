---
name: sandbox-denies-writes-under-dot-claude-hooks-skills
description: The OS sandbox refuses every write under .claude/hooks/ and .claude/skills/ at any depth, so git merge and /smh-sync-agents fail in-session.
metadata:
  type: project
---

⛔ **The OS sandbox denies EVERY write under a `.claude/hooks/` or `.claude/skills/` directory,
at any depth, regardless of `sandbox.filesystem.allowWrite`.** This is Claude Code protecting its
own hooks and skills from the agent. It is not a settings mistake and it cannot be configured away.

Measured 2026-08-23 in the lobby (`touch` probe, sandbox on):

```
DENY   <repo>/.claude/hooks/          DENY   <repo>/.claude/skills/
DENY   <worktree>/.claude/skills/     ALLOW  <repo>/.claude/worktrees/
ALLOW  <worktree>/.claude/rules/      ALLOW  <repo>/.agents/hooks/
```

**Why: it breaks git, not just file edits.** Any `git merge`, `checkout`, `pull` or `worktree add`
that must write those paths dies with `Operation not permitted`. Hit live: `git merge origin/main`
into a lane failed on `unable to unlink old '.claude/hooks/guard-cwd-escape.py'` after SCC-299 moved
that file on `main`. Every lane routes through those commands, so this fires whenever `main` moves a
hook or a skill. It is also why `/smh-sync-agents` cannot write launcher skills from inside a
session — the command is fine (`-WhatIf` exits 0, the 59 opencode mirrors are byte-identical); the
write is what is blocked. See [[toolkit-sync-covers-agents-not-docs]] and [[one-door-per-platform-per-command]].

**How to apply:** run only the specific git command with the sandbox disabled, never the whole flow,
and say in the report that you did. ⛔ **Disabling the sandbox also moves `TMPDIR`** from
`/tmp/claude-<uid>` to `/var/folders/…`, so a test re-run that way is measuring different conditions —
a green there can be vacuous ([[red-test-can-die-before-its-assertion]]). Tracked as SCC-300.
