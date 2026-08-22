---
name: zshrc-is-invisible-to-automation
description: "~/.zshrc is interactive-only — agents, hooks, npm scripts and `zsh -c` never source it, so an env var set there works by hand and is GONE in automation on the same machine. Put shared env in ~/.zshenv and verify all three shell modes."
metadata:
  node_type: memory
  type: project
---

`~/.zshrc` is sourced by **interactive** shells only. `~/.zprofile` is **login** shells only.
Only **`~/.zshenv`** is read by *every* zsh — including `zsh -c`, which is what agent tool calls,
git hooks, npm scripts and CI-shaped invocations actually use.

The failure this produces is uniquely nasty: the variable is present when the operator tests by
hand and absent in every automated path **on the same machine**, so the suite passes interactively
and fails under automation with no environmental difference anyone can see.

**This has now bitten twice on the Mac (2026-08-06), both times costing a debugging cycle:**
- Node 22's PATH in `.zshrc` → `zsh -c` still ran Node 26 → vitest died on jsdom storage
  ([[node-26-breaks-vitest-jsdom-storage]]). Real fix was at the brew link, not the export.
- `JAVA_HOME` in `.zshrc` → firebase emulators + the Firestore rules suite failed only in
  automation.

**How to apply:** put anything a script/agent/hook needs in `~/.zshenv`, never `~/.zshrc`. Then
verify all three modes — checking one proves nothing:
```bash
for m in -c -lc -ic; do zsh $m 'echo $VAR'; done   # ALL THREE must agree
```
Corollary for diagnosis: when something passes by hand and fails under automation, suspect shell
startup-file scope BEFORE suspecting the code. Related: [[git-hooks-live-in-githooks-not-git-hooks]].
