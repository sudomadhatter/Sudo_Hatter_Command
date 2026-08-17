---
name: antigravity-scm-repo-list-collapses
description: Antigravity IDE Source Control — repos stack (fixed by git.path shim) and the multi-repo view collapses to one on a click; restore with cmd+alt+r.
metadata:
  type: reference
---

Antigravity IDE 1.107 (VS Code 1.107 base), Mac only — two separate Source Control defects, two separate fixes:

1. **Stacking.** `Projects/*` are submodules of the lobby, so the view nests them under it.
   Fixed by `~/.local/bin/git-flat-scm` (strips `--show-superproject-working-tree`), wired via
   `"git.path"` in the IDE user `settings.json`. This one is stable; it has not regressed.
2. **Collapse to one repo.** `onTreeSelectionChange` sets `visibleRepositories = selected repo
   nodes` on any real click, and `onWillSaveState` persists it to `scm:view:visibleRepositories`
   in `workspaceStorage/<hash>/state.vscdb` — so a stray click on a repo row survives restarts and
   reads as "the fix got reverted". It did not; only the selection did.

**How to apply:** don't re-debug the shim when only one repo's changes show — check
`sqlite3 state.vscdb "select value from ItemTable where key='scm:view:visibleRepositories'"`.
`visible:[0]` = collapsed selection. Restore by flipping
`scm.repositories.selectionMode` single -> multiple (the "multiple" branch re-selects every repo);
`cmd+alt+r` in `keybindings.json` runs both flips. No supported setting pins "always show all".

Related: [[two-machines-mac-and-pc]] — this is Mac-side only; per-machine, never travels.
