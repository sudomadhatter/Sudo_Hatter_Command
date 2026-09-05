---
name: vscode-hides-git-hook-output
description: "VS Code's Source Control panel swallows git-hook output — it goes to View > Output > Git. A warn-only hook fires, complains, and looks like a clean success. This is how a wrong-key commit reached AviationChat's main on 2026-08-07."
metadata: 
  probe: "test -e .agents/jira.conf"
  node_type: memory
  type: feedback
  originSessionId: 8bc78088-0a6e-4b75-b4eb-edc817c5fe79
  modified: 2026-08-07T22:10:02.358Z
---

Daniel commits from the **VS Code Source Control panel**, not a terminal. The panel shells out to git,
so hooks run identically — but it **does not surface what a hook prints**. Output lands in
`View → Output → Git`, a dropdown nobody has open.

Consequence: **a hook that only warns is invisible.** The commit succeeds, the panel goes quiet, and
the warning is never read. In ENFORCE mode a *rejection* does raise a notification with a *Show Command
Output* button, so blocks are visible — but anything short of a block is not.

**Why:** on 2026-08-07 a commit carrying `SCC-10` landed on AviationChat's `main`, where
`.agents/jira.conf` binds the repo to `AVCH`. The commit-msg hook fired and complained exactly as
designed. Nobody saw it. The standard "roll out a hook in WARN for a few days first" advice silently
assumes a terminal — it is wrong for this operator, and following it cost a wrong-key commit on
production's branch within hours of shipping the hook. See [[jira-integration-live]].

**How to apply:**
- **Ship new hooks ARMED, not warning**, in this system. A warning nobody reads is not a gate.
- When telling Daniel to watch a hook do something, either tell him to use the terminal for that one
  command or point him at `View → Output → Git` explicitly — never assume he'll see stdout.
- When a hook "didn't fire," check the Git output channel before concluding it's broken. Also check
  `core.hooksPath` ([[git-hooks-live-in-githooks-not-git-hooks]]).
- Blanket staging is the panel's other trap: *Stage All Changes* is one click and sweeps parallel work
  into the commit. It did, on the same evening — 15 files instead of 6. Stage file by file.
