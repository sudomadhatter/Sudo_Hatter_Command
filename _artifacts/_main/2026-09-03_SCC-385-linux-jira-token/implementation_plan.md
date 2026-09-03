# Implementation Plan — SCC-385: the Jira API token on Linux / WSL

**Date:** 2026-09-03 · **Workspace:** `_main` · **Status:** approved (operator: "walk me through this I will do that now so we have it all correct")

## What was wrong

`jira-api-token-setup.md` §3 stores the token in the macOS keychain or Windows SecretManagement and has
no Linux section. `jira_ticket.py`'s `resolve_token()` on Linux reads `$JIRA_API_TOKEN` and nothing
else, so on the WSL box `attach` exited 5 at the SCC-384 close-out and the walkthrough never reached the
ticket. The INDEX's new Linux column marked row 6b ✅ on the strength of `acli` being authenticated —
half the step.

## Steps

1. Operator creates the token (guide §2) and stores it: `~/.config/sudo-jira/token`, mode 600, exported
   from `~/.profile` (not `~/.bashrc`, which returns early for non-interactive shells).
2. Verify from a fresh login shell (`bash -lc`), then §5's `/rest/api/3/myself`, then run the `attach`
   that had failed.
3. Write the route into the guide as a `### Linux / WSL2 (Ubuntu)` block in §3, add the Linux row to
   "What has actually been run", and correct the INDEX 6b Linux cell.

## Not doing

- No keyring integration in `jira_ticket.py` (libsecret needs a running Secret Service, which WSL has
  no reliable copy of); the env-var route is the one the script already supports on every OS.
