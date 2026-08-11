---
name: check-maps-stale-is-false-in-worktrees
description: "check_maps.py always reports AUTO block STALE inside a git worktree, and its printed regenerate command writes the worktree's directory name into the committed repo-map."
metadata:
  node_type: memory
  type: reference
---

`generate_repo_map.py` labels the tree with **`Path(root).name`** — the basename of wherever you run
it. Inside `.claude/worktrees/<lane>/` that is the *lane* name, so regenerating there writes e.g.
`scc-80-followon/` as the repo root into a file destined for `main`. It shipped that way once
(SCC-74, fixed at `05938cf`).

`check_maps.py` then compares the map's label to the CWD basename and reports the **correct** map as
stale, with a remedy that would introduce the very defect it looks like it is reporting:

```
[x] AUTO block is STALE - regenerate: ... --root .../scc-80-followon
[x]   on disk but not in map: scc-80-followon/      <- the worktree's own name
[x]   in map but not on disk: Sudo_Hatter_Command/  <- the CORRECT label it wants removed
```

**So the warning fires on every lane, every time, and means only "you are in a worktree."** That is
never drift. Judge the other check_maps sections (`repo-map paths`, `folder coverage`, `INDEX.md
paths`, `level-2 INDEX presence`) on their own — they are accurate inside a worktree.

**How to apply:** never regenerate the repo-map from a worktree on the strength of that warning. If a
real content change forces a regen there (adding/removing a file under `docs/` does), regenerate,
correct the single root-label line, then **prove** it: `rsync -a --exclude=.git ./ <scratch>/Sudo_Hatter_Command/`,
run the generator with `--root <scratch>/Sudo_Hatter_Command`, and diff. Byte-identical means the
committed AUTO body is genuine generator output, so no hand-edit exemption is being claimed.
Otherwise regenerate from the main checkout after the merge.

Real tool fix (unticketed): derive the label from git's **common dir** (the main worktree) rather
than the CWD basename.

Sibling false-positive with a different cause: [[check-maps-all-false-stale-agy]] (the `--all`
fan-out applies one default ignore set). Both say the same thing — **an AUTO-STALE report is a
hypothesis, not a verdict**; diff the generator output before spending a regen+commit on it.
Related: [[worktrees-do-not-inherit-gitignored-assets]], [[preflight-resolves-repo-from-cwd]] (same
root cause class: a lobby tool reading CWD as identity).
