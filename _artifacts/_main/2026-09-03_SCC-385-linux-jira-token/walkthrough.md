# Walkthrough — SCC-385: the Jira API token on Linux / WSL (2026-09-03)

**Ticket:** SCC-385 · **Branch:** `chore/SCC-385-linux-token` · **Date:** 2026-09-03

## Task Checklist

- [x] Token created by the operator (guide §2) and stored: `~/.config/sudo-jira/token` (600), exported from `~/.profile`
- [x] Verified from a fresh login shell: `bash -lc` → 192 chars; `/rest/api/3/myself` → `OK: Sudo Hatter …`
- [x] `jira_ticket.py attach` landed the SCC-384 walkthrough on its ticket (it had exited 5 at the close-out)
- [x] Guide §3 gains a `Linux / WSL2 (Ubuntu)` block and a Linux row in "What has actually been run"
- [x] INDEX row 6b's Linux cell names the env-var route
- [x] The merge itself — lands via this branch's PR

## Evidence

```
$ bash -lc 'echo ${#JIRA_API_TOKEN}'                    → 192
$ … | curl -s -K - … /rest/api/3/myself | python3 …     → OK: Sudo Hatter sudomadhatter@gmail.com
$ bash -lc 'python3 .agents/scripts/jira_ticket.py attach --key SCC-384 --file …/walkthrough.md'
jira-ticket: attached walkthrough.md to SCC-384
```

## Decisions

- **`~/.profile`, not `~/.bashrc`.** Ubuntu's `.bashrc` returns on its first lines for non-interactive
  shells; a variable exported there exists in the terminal you typed it in and nowhere an agent or hook
  runs. `.profile` is read by every login shell — WSL terminals, the VS Code WSL server, `bash -lc`.
- **A 600-mode file, not the token inline in `.profile`.** Same secret, but the profile stays free of
  it and the file can be rotated without editing shell startup.
- **No `secret-tool`.** libsecret needs a Secret Service daemon; WSL has no dependable one.

## Pitfalls

- An agent's shell is a snapshot from session start: it will not see a new variable until a new session
  or `bash -lc`. Testing in the shell you typed the export into proves nothing.

## Your Actions

Nothing is owed. The token is stored and verified; the expiry date goes on SCC-385 as a comment when the
operator reads it off the Atlassian token page.
