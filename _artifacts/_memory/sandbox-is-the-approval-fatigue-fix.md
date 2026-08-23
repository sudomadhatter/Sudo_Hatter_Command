---
name: sandbox-is-the-approval-fatigue-fix
description: The OS sandbox — not a hook — is what stops approval prompts; Mac only, and four things break under it.
metadata:
  type: reference
---

⭐ **`sandbox.enabled` + `autoAllowBashIfSandboxed` (defaults true) is the ONLY general fix for
approval fatigue.** Measured on 2026-08-22 over one 929-call session: `Bash(...)` allow rules got
16% auto-approved; the best hook anyone can write took it to 36% and left **588 prompts**. The
sandbox takes all of them, because the CAGE becomes the boundary instead of the string.

**Why no hook can do it:** `Bash(...)` rules match by **PREFIX over the WHOLE command string**, so
**no rule can ever match a string containing a pipe** — 81 rules in `settings.local.json` never get
a chance. A `PreToolUse` hook is the entire remaining permission surface. It is the ceiling, not a
step toward one.

⛔ **There is NO native Windows implementation — WSL2 only.** On the PC ([[two-machines-mac-and-pc]])
the sandbox does not exist, which is the sole reason `allow-readonly-chain.py` (SCC-287) shipped.

**Live config is `.claude/settings.local.json` — gitignored, per-machine, nothing in the repo
records it.** `network.allowedDomains` is a guest list enforced by a local filtering proxy that
403s anything unlisted. `filesystem.denyRead` is a DENY-list, so reads are open by default.

**Four things break under it, all hit live:**

| Symptom | Cause | Fix |
|---|---|---|
| `gh` → `x509: OSStatus -26276` | Go CLIs fail TLS under Seatbelt (documented) | `excludedCommands` |
| `python3 jira_feed.py` → acli silently no-ops | a sandboxed parent CAGES its children | exclude the parent script too |
| `git worktree remove` / `push -u` → `Operation not permitted` | Bash writes into `.claude/` and `.git/` are refused; **`filesystem.allowWrite` did NOT take effect** (may need a session restart — unverified) | `dangerouslyDisableSandbox`, only after proving the sha is an ancestor of `origin/main` |
| a green gate reports a failing exit code | a `> /tmp/…` REDIRECT is refused and the shell reports the redirect's failure as the command's | run gates BARE — see [[piping-a-gate-hides-its-exit-code]] |

⛔ **`excludedCommands` matches the COMMAND STRING as a glob** — the docs' own example is `docker *`,
not `docker`. `env -u GITHUB_TOKEN gh …` does **not** match `gh *`; drop the prefix.

Docs: https://code.claude.com/docs/en/sandboxing
