---
name: interactive-startup-files-are-invisible-to-automation
description: "An env var set in an INTERACTIVE-only startup file (`~/.bashrc` here, `~/.zshrc` on zsh) works when the operator tests by hand and is GONE in every automated path on the same box — agents, git hooks, npm scripts, `bash -c`. Put anything a script needs in `~/.profile` and invoke through a LOGIN shell (`bash -lc`). Re-measured on this PC 2026-09-04."
metadata:
  node_type: memory
  type: project
  probe: "grep -q '.profile' docs/migrations/install_guides/jira-api-token-setup.md"
  modified: 2026-09-04
---

The install guide that encodes this is `docs/migrations/install_guides/jira-api-token-setup.md`
— it is what the probe on this file watches, so the memory reds if that advice is ever removed.

**The trap, in one line:** the variable is present when Mr. Hatter tests by hand and absent in every
automated path **on the same box**, so a suite passes interactively and fails under automation with
no environmental difference anyone can see.

> ⛔ Renamed from `zshrc-is-invisible-to-automation` on 2026-09-04 (SCC-401). The old name pinned
> the lesson to zsh on a Mac that does not exist ([[one-pc-windows-and-wsl]]), so an agent on this
> box read it as "not my shell" and walked into the identical bash version. The trap is about
> **interactive-only startup files**, not about zsh.

## Live here, measured 2026-09-04

`~/.bashrc` opens with the stock Debian guard — *"If not running interactively, don't do anything"*
— and `return`s at line 8. So:

```bash
bash -c  'echo ${JIRA_API_TOKEN:+SET}'    # -> empty   (non-interactive: .bashrc returned early)
bash -lc 'echo ${JIRA_API_TOKEN:+SET}'    # -> SET     (login shell: .profile is read)
```

`JIRA_API_TOKEN` lives in **`~/.profile`**, which is why `jira_ticket.py attach` must be invoked
through `bash -lc`. That is not a quirk of that script — it is this rule.

⛔ **Never echo the value to check it.** Use `${VAR:+SET}`; a bare `echo $VAR` puts the secret in
a transcript, a scrollback and a log, and it cannot be taken back out.

## The same shape on other shells

- **zsh:** `~/.zshrc` is interactive-only, `~/.zprofile` is login-only, and only **`~/.zshenv`** is
  read by *every* zsh including `zsh -c`. Bitten twice on the retired Mac (2026-08-06): Node 22's
  PATH ([[node-26-breaks-vitest-jsdom-storage]]) and `JAVA_HOME` for the Firestore rules suite
  ([[firestore-rules-tests-need-java]]).
- **PowerShell (the Windows side):** profile scripts are skipped entirely under `-NoProfile`, which
  is how every gate here invokes it — same class, different spelling.

## How to apply

1. Put anything a script, agent or hook needs in **`~/.profile`** (bash) / `~/.zshenv` (zsh) —
   never the interactive file.
2. Invoke through a **login** shell (`bash -lc`) when the value must be present.
3. Verify more than one mode; checking one proves nothing:
   ```bash
   for m in -c -lc -ic; do bash $m 'echo ${VAR:+SET}'; done   # ALL must agree
   ```
4. **Diagnosis corollary:** when something passes by hand and fails under automation, suspect
   shell startup-file scope BEFORE suspecting the code.

Related: [[git-hooks-live-in-githooks-not-git-hooks]] — the other "it looks armed and is not".
