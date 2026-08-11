---
IsArtifact: true
ArtifactMetadata:
  title: SCC-96 — check_maps false-STALEs a ledger row that cites a memory
  type: walkthrough
  date: 2026-08-11
---

# Walkthrough — SCC-96

**Branch:** `chore/SCC-96-checkmaps-false-stale` · **Lane:** LOCAL

## How it was found — the combined gate earning its place

Five lanes landed on `main` tonight. Each was green alone, and each was green again after absorbing
its predecessors. **The combined run on `main` was the first thing to see all five together**, and it
reported:

```
_artifacts/_main/INDEX.md: stale row `tea-retrofit-active-initiative/` (folder not on disk)
```

There is no such folder and none is owed. SCC-88's ledger row names the **memory**
`tea-retrofit-active-initiative` in prose, explaining which memory its ruling rests on.

## The bug

`_check_depth3_tree()` pulled every backticked token out of every table row, **`rstrip("/")`-ed the
trailing slash off**, and then asked `SESSION_FOLDER_RE` whether each token was a session folder.

The slash was the signal. A row *declares* its session folder in column one, written `` `2026-08-11_slug/` ``;
everything else in the row is prose. Stripping it left the regex — `^(story-|\d{4}-|tea-|wave-|close-out-|epic-|autopilot-)`,
written to classify **directory names** — deciding the question about arbitrary English.

**Not a one-off.** Nine memories in the lobby store carry a matching prefix:

```
autopilot-engine-is-project-local · autopilot-glm-hybrid-lane · autopilot-has-three-drifting-engines
autopilot-manual-takeover-check-liveness · close-out-command-is-daniels-signoff
story-artifacts-live-in-the-tree · story-artifacts-two-doc-close · story-status-flip-contract
tea-retrofit-active-initiative
```

Any ledger row citing one of them reds the gate. ⭐ **The SOP already stated the correct principle** —
*"a row describing work that deleted something has to be able to name it"* — the code simply did not
honour it for this check. And the cost is the one SCC-82 is the written record of: a gate whose clean
state is non-zero teaches people to read past it.

## The fix

Two sets instead of one, each matched to what its check actually wants:

- **`mentioned`** — any backticked token in the row. Permissive *on purpose*: it only ever
  **suppresses** a "missing row" complaint, so generosity here cannot invent a problem.
- **`declared`** — the row's **first cell**, written with a trailing `/`. Strict *on purpose*: it is
  the only thing allowed to raise "stale row".

## Test-first, and the mirror case is the point

`test_check_maps.py` is new (auto-discovered, so the floor went 12 → 13 files with no wiring).

**RED before the fix: 4/9 passed.** Cases A×4 and F failed with the exact live message.

Cases **D** and **E** passed *before and after* — deliberately. Without them the "fix" could have
been *stop reporting stale rows at all*, and case A would have gone green on a gate that had simply
gone blind. D asserts a genuinely deleted session folder is **still** reported; E asserts a session
folder with no row is **still** reported. One half is not a gate.

Case **F** runs against the live `_artifacts/` tree, so this specific regression cannot come back
silently.

```
BEFORE:  -- 4/9 passed --   (A×4, F red)
AFTER:   -- 9/9 passed --
```

## Evidence

```
python3 .agents/scripts/tests/test_check_maps.py       -> exit 0   9/9 passed   (bare)
python3 .agents/scripts/tests/run_all.py               -> exit 0   13/13 files passed (bare)
python3 .agents/scripts/workflow_lint.py --toolkit-only-> exit 0   (bare)
```

Every gate run **bare** — piping to `tail` returns the *pipe's* exit code, which is how a red gate
reads as green.

`check_maps.py` itself is verified on `main` after the merge, not in this worktree: its AUTO-block
check labels the tree by the **CWD basename**, so it reports a false stale inside any worktree, and
the repo-map's curated block names a **gitignored** secrets path that does not travel to worktrees.
Both are known traps, and both are why this one is measured where it counts.

**Follow-on noted, not fixed here:** `docs/repo-map.md`'s curated block names
`docs/migrations/auth_keys/_secrets/master.env`, which is gitignored. It resolves on the operator's
machine and reads as a **dead path in any worktree and on any fresh clone**. Pre-existing class
(the old `_my_resources/` path had the same property), carried forward by SCC-89's repoint rather
than introduced by it.

Verdict: PASS @ (this commit)
