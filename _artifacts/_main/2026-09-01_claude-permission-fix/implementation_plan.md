# Implementation Plan — Claude terminal permission fix (`.claude/settings.json`)

**Ticket:** SCC-366 (minted under grouping epic SCC-33 — CI/CD For Sudo Dev System)
**Lane:** command-centre Task; branch `chore/SCC-364-claude-permission-fix` off `main`
**Approval:** Mr. Hatter's directive of 2026-09-01 — the operator supplied the full fix spec
(FIX 1–4, the never-add list, and the verify protocol) verbatim in the tasking message. That
directive IS the approved plan; this file records it for the artifact protocol.

## Problem

~60 terminal commands across the last 20 Claude sessions plus the SCC-360 close-out lane stopped
and waited for operator approval. Evidence:
`/private/tmp/claude-501/.../scratchpad/approve-these.txt` (Groups A + B).

Root causes, verified against https://code.claude.com/docs/en/permissions:
1. `additionalDirectories` absent from all three settings files → every `> /tmp/…` redirect and
   every `cd` into a `/private/tmp` scratchpad prompts regardless of Bash rules.
2. Leading variable assignments (`REPO=…; cd "$REPO"`) are their own subcommands and block
   prefix matching.
3. Genuinely missing prefixes: the whole `gh` family, several `git` forms, `sleep`, `test`,
   env-prefixed twins.

## Changes (all in `.claude/settings.json`, `permissions` block only)

- **FIX 1** — add `"additionalDirectories": ["/tmp", "/private/tmp"]`.
  Consequence (stated for the record): this makes /tmp readable and writable without a prompt.
  That is the trade for the scratchpad workflow; nothing outside /tmp is affected.
- **FIX 2** — variable-assignment rules SCOPED TO THE VALUE, never bare:
  `REPO=/*`, `W=/*`, `L=/*`, `P=/*`, `S=/*`, `WORKTREE=/*`, `PROJECT_ROOT=/*`,
  `D=_artifacts/*`, `EPIC=epic/*`, `B=https://github.com/*`,
  `BRANCH=$(git rev-parse *)`, `HEAD_SHA=$(git rev-parse *)`, `BEHIND=$(git rev-list *)`.
  ⛔ No `Bash(D=*)` / `Bash(REPO=*)` — a bare assignment rule admits `D=$(arbitrary code)`.
- **FIX 3** — missing prefixes (deduped against the 80 existing rules):
  - `gh` per-subcommand only: `pr create|view|checks|list`, `run view|list` — plus the
    `env -u GITHUB_TOKEN` twin of each. ⛔ Never `Bash(gh *)`, never `gh pr merge`.
  - `git`: `rev-list`, `stash push`, `stash pop` (never drop/clear), `pull --ff-only` bare form
    (+ env twin), `branch -a`, `branch --show-current`, `config --get` (read form only),
    `env -u GITHUB_TOKEN git push origin chore/:*`, `env -u GITHUB_TOKEN git push -u origin chore/:*`.
  - other: `env -u GITHUB_TOKEN python3 .agents/scripts/:*`, `sleep:*`, `test:*`.
  - NOT added (harness already handles): time, xargs, pwd, find, wc, which, diff, stat, du, ls,
    cat, echo, head, tail, grep, cd.
- **FIX 4 (decision, reported either way)** — `Bash(acli jira workitem edit:*)` is a live board
  write with no confirmation step. Add ONLY if the operator left the line in; otherwise report
  its exclusion.

## Exclusions (deliberate, per git-policy / constitution)

`git reset`, `git clean`, `git push --force/-f/--force-with-lease/--mirror/--all`, `git branch -D`,
`git rebase`, `git filter-branch`, `git update-ref`, `git stash drop/clear`, `git add -A/./-u`,
`git checkout .`, `git restore .`, bare `git config`, bare `gh`, `gh pr merge`, `sudo`, `rm`,
`rm -rf`, `rm -r`. Group B's `rm` of two `_artifacts/_memory` files is NOT allowed (constitution
§Ask First). Group A's `git reset --hard origin/main` line is excluded; the rest of its chain is
covered by other rules.

## Known-unfixable classes (reported, not chased)

Shell loops (`for`/`until`), heredocs, commands >10,000 chars, `find -exec/-delete`, unquoted
globs on write-capable commands. Remedy lives in the commands, not the settings.

## Verification

Re-run representative commands from approve-these.txt in a scratch session; confirm no prompt.
Report rows added, exclusions, and which remaining prompts fall into which unfixable class.

## Out of scope

No commit, no push, no PR — the operator reviews the diff in the working tree.
