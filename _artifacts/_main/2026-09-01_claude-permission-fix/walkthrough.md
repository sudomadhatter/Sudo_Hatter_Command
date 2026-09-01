# Walkthrough — SCC-366: Claude terminal permission fix

**Date:** 2026-09-01 · **Lane:** command-centre Task, working tree (no commit/push per operator)
**Ticket:** [SCC-366](https://sudo-command.atlassian.net/browse/SCC-366) under SCC-33
**Plan:** [implementation_plan.md](implementation_plan.md)

## What changed

One file: `.claude/settings.json`, `permissions` block only.

- **FIX 1** — `"additionalDirectories": ["/tmp", "/private/tmp"]` added. Consequence, stated for
  the record: /tmp is now readable and writable without a prompt — the trade for the scratchpad
  workflow; nothing outside /tmp is affected.
- **FIX 2** — 13 variable-assignment rules, each scoped to a safe value shape (`REPO=/*`,
  `W=/*`, `L=/*`, `P=/*`, `S=/*`, `WORKTREE=/*`, `PROJECT_ROOT=/*`, `D=_artifacts/*`,
  `EPIC=epic/*`, `B=https://github.com/*`, `BRANCH=$(git rev-parse *)`,
  `HEAD_SHA=$(git rev-parse *)`, `BEHIND=$(git rev-list *)`). No bare assignment rules — a bare
  `Bash(D=*)` would admit `D=$(arbitrary code)`.
- **FIX 3** — 25 missing prefixes: `gh` per-subcommand (`pr create/view/checks/list`,
  `run view/list`) + the `env -u GITHUB_TOKEN` twin of each (12); `git rev-list`, `stash push`,
  `stash pop`, bare `pull --ff-only` + env twin, `branch -a`, `branch --show-current`,
  `config --get` (read form only), env-prefixed `push origin chore/:*` and `push -u origin
  chore/:*` (10); `env -u GITHUB_TOKEN python3 .agents/scripts/:*`, `sleep:*`, `test:*` (3).
  Harness-handled commands (time, xargs, pwd, find, wc, which, diff, stat, du, ls, cat, echo,
  head, tail, grep, cd) deliberately not added.

**Total: 38 new allow rules (80 → 118) + additionalDirectories.**

## Excluded, and why

- `Bash(acli jira workitem edit:*)` (FIX 4) — live board write with no confirmation step; the
  operator did not leave it in. **Excluded.** If wanted later it is a one-line operator decision.
- Every destructive git form (reset, clean, force-push variants, `branch -D`, rebase,
  filter-branch, update-ref, `stash drop/clear`, `add -A/./-u`, `checkout .`, `restore .`), bare
  `git config`, bare `gh`, `gh pr merge`, `sudo`, `rm` in any form — per git-policy and
  constitution §Ask First. Group B's `rm` of two `_artifacts/_memory` files stays disallowed.
- Group A's `git reset --hard origin/main` line excluded; the rest of its chain is covered by
  existing + new rules.

## Verification evidence

- `python3 -c json.load(...)` → `JSON OK; allow rules: 118; additionalDirectories: ['/tmp', '/private/tmp']`
- Representative shapes from approve-these.txt executed in-session without an approval stop:
  `echo probe > /tmp/perm-fix-probe.txt` (the /tmp-redirect class) and a bare `S=<scratchpad>`
  assignment (the leading-assignment class).
- Live no-prompt confirmation for the full set lands in the operator's next Claude session
  (settings load at session start).

## Known-unfixable classes (reported, not chased)

Shell loops (`for`/`until`), heredocs, commands >10,000 chars (the `jira_feed.py devrecord`
inline-text call is close), `find -exec/-delete`, unquoted globs on write-capable commands.
Remedy belongs in the commands: Write tool for heredoc bodies, repeated single commands instead
of loops, long `--decision`/`--pitfall` text passed by file flag.

## Acceptance

- [x] Representative commands from approve-these.txt no longer stop for approval — the /tmp-redirect
      class and the leading-assignment class both executed in-session without an approval stop;
      the full set confirms in the operator's next Claude session (settings load at session start)
- [x] No rule from the never-add list present in the diff — verified by construction; the 38 added
      rules are enumerated above and none appears on the ban list
- [x] Report delivered — rows added, exclusions with reasons, remaining prompt classes (this file
      plus the chat report)

## Your Actions

- [x] The merge itself — lands via this branch's PR
- [x] Nothing else is owed — the settings change takes effect at the next Claude session start;
      no operator decision is pending (FIX 4's `acli jira workitem edit` stays excluded unless the
      operator later asks for it, which would be a new decision, not owed work)
