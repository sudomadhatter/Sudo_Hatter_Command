---
IsArtifact: true
ArtifactMetadata:
  title: SCC-201 cycle 3 — mutation sweep
  type: evidence
  date: 2026-08-20
---

# Row Q — every new case declared against a mutant it alone kills

Nine mutants, run one at a time against a restored tree. A case that kills nothing is a case
that proves nothing, and a mutant killed by five cases tells you only that the suite is noisy.

| # | Mutant | Killed by | Rider |
|---|---|---|---|
| M1 | `moves_ticket` drops the closer needle (`TRANS` only) | CS-13 C2, C6, C7-positive | SCC-242 F |
| M2 | the story door's `finish` loses `--apply` | CS-13 **C2b only** | SCC-242 F |
| M3 | `moves_ticket` drops the `--key` requirement | CS-13 **C7 only** (+ C3 on the live door) | SCC-242 F |
| M4 | drop `mobile/` from the cicd- body's refusal list | **N1 only** | SCC-243 N |
| M5 | drop the `LIGHT-VCS` row from the smh- table | **P1 only** | SCC-243 O/P |
| M6 | a ticked item no longer closes the window | I, K2 | SCC-206 I |
| M7 | HTML comments no longer skipped | J, J2 | SCC-206 J |
| M8 | delete the continuation fold (the lazy fix) | **K, K2** | SCC-206 K |
| M9 | `index_append` reverts to append-at-end | G1 ×2, G3 | SCC-242 G |
| M10 | the clone stops naming the INDEX | **A1f only** | SCC-242 H |

⭐ **M8 is the one that matters most.** Deleting the fold makes I, J and J2 green in a single
edit — the cheapest possible "fix" — and truncates every genuine multi-line instruction to its
first line. K is the control that refuses it.

⛔ **M3 is the one that nearly shipped.** The first cut of the CS-13 needle matched a bare
mention, so the story door's own prose explaining that Step 4b runs the closer read as a
transition — and that sentence sits in Step 2, ahead of the landing push. The guard accused the
door of writing `Done` before it landed. C7 is the control that pins it.

## The vacuous green caught before it shipped

The first `STORY_ROW` fixture read `**The merge itself** — lands on the epic via
`/cicd-close-story-merge-tree``. Case A2 PASSED immediately, because `is_merge_row` is
*door-name **OR** canonical-phrase* — it matched on the phrase and never touched `MERGE_DOORS`
at all. Rewritten to name only the door, it went red, and A1/A3/A5 became genuinely dependent
on it.

Then all five were red, so nothing proved the fixture sound rather than broken. **A6** was added
— the unchanged Task path through the same helpers, green before and after. Red above plus green
there is what makes the defect real rather than assumed.
