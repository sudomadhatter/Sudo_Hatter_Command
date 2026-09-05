---
name: jira-attachments-need-the-rest-token
description: "acli cannot attach files (list/delete only) — uploading to a ticket is REST + the API token in keychain item `sudo-jira`; storing that token has two silent-corruption traps"
metadata:
  type: reference
---

**Attaching a file to a Jira ticket does NOT go through `acli`.** `acli jira workitem attachment`
has `list` and `delete` and no `add` (measured on 1.3.22-stable, 2026-08-22). The upload is
`POST /rest/api/3/issue/<KEY>/attachments` with header `X-Atlassian-Token: no-check`, multipart
field `file`, basic auth `<atlassian-email>:<api-token>`. Everything else — minting, editing,
transitioning, JQL — is `acli` and needs nothing extra.

**The token lives in OS credential store item `sudo-jira`**, account = the Atlassian account email
(`acli jira auth status` prints it; it is NOT the git email). Read it at the moment of use, pass it
via `curl -K -` on stdin so it never enters `argv`, `unset` after. ⛔ `acli`'s OWN stored credential
is a wrapped copy and 401s against `/rest/api/3/myself` — it is not reusable.

⛔ **Storing that token corrupts silently two ways, and every failure looks like a wrong token
(401), so the hunt goes to the email and the site first.** Measured, both of them, 2026-08-22:
interactive `security add-generic-password -w` with no value truncates at **exactly 128 chars**
(fixed prompt buffer); `-w "$(pbpaste)"` stores **the command text**, because running a command
means copying it, which replaces the token on the clipboard. Use the shell's own `read -rs` (no
length limit) and print `${#T}` — a complete token is ~190 chars.

Full procedure, both machines: `docs/migrations/install_guides/jira-api-token-setup.md` (SCC-294).
The token page's `Last accessed` column is the diagnostic — `Never Accessed` proves a token has
never reached Jira, and it identifies WHICH token a machine uses when several exist.
Related: [[jira-integration-live]] · [[one-pc-windows-and-wsl]] · [[env-migration-kit]]
