---
name: lane-collision-is-gates-not-files
description: Two lanes with ZERO file overlap can still break each other, because a new gate in one judges the other's artifacts; check gates across the boundary, not just the diff.
metadata:
  type: project
---

"Zero code overlap" does NOT mean two lanes are safe to land in either order. A gate is
code that reads *other lanes'* files, so a lane that ships a gate reaches sideways into
every lane in flight — and a lane that ships an artifact gets judged by gates that did not
exist when it was written.

Measured 2026-08-16, SCC-187 vs SCC-164. File overlap was exactly two append-style ledgers,
zero code overlap. Both real collisions were invisible to that check:

- **Forward** — SCC-187's new `NESTED` walker in `test_suite_runner.py` derives its subject
  set dynamically (`test_*.py` containing `c.block(`), so it judged SCC-164's four wired
  test files the moment they merged.
- **Backward** — SCC-164's `walkthrough_roster.py` BLOCKS any lane dated ≥ its `CUTOFF`
  (`2026-08-15`) whose verdict carries no per-lens roster. SCC-187 was dated 08-16 and its
  review had already run, so a gate written later would have refused it at close-out.

**Why:** a merge-conflict check answers "do these edits touch the same bytes". Gates are
about *behaviour over a set*, and the set is usually a glob or a date, not a file list.

**How to apply:** before landing two live lanes, in addition to `git merge-tree`:
1. List each lane's NEW or CHANGED gate scripts and date cutoffs.
2. Run each lane's gates against the OTHER lane's actual blobs (`git show <branch>:<path>`
   into a scratch dir) — do not reason about it, run it.
3. A date-scoped gate (`CUTOFF`) is the sharpest one: check whether the other lane's
   artifacts fall on the wrong side of it.

Related: [[parallel-lanes-fix-the-same-finding]] · [[multi-lane-closeout-board-merge-shape]] ·
[[landing-is-not-closeout]] · [[test-certification-at-shipping-sha]]
