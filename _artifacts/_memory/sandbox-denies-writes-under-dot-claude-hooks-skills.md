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

**How to apply (Resolved in SCC-300):**
1. **Hooks Single-Sourced**: `.claude/hooks/` is completely retired and untracked. `.claude/settings.json` executes hooks directly from `.agents/hooks/` via `run-hook.sh`. Because `.agents/hooks/` is explicitly writable in the sandbox, `git merge` on `main` hook updates never encounters sandbox denials.
2. **Plumbing & Sync**: `sync-agents.ps1` no longer attempts to sync `.claude/hooks/` and catches `.claude/skills/` sandbox write blocks gracefully in-session, reporting an informative warning while maintaining all other surfaces (.agents/skills, .opencode/commands, .roo/commands, and machine caches).
3. If `.claude/skills/` updates must be written to disk, run `/smh-sync-agents` outside the Claude Code OS sandbox (e.g. from terminal, Antigravity, or Opencode). ⛔ **Disabling the sandbox in Claude Code also moves `TMPDIR`** from `/tmp/claude-<uid>` to `/var/folders/…`, so test executions should remain sandboxed to avoid vacuous test results ([[red-test-can-die-before-its-assertion]]). Resolved under SCC-300.
