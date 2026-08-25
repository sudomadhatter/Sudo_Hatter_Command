---
name: epic-branch-carries-both-numbers
description: "Epic branches are `epic/<JIRA-KEY>-epic-<N>-<slug>` — BOTH the ticket key and the sprint number; the `epic/` prefix stays in FRONT because every resolution globs `epic/*` and the armed merge-target guard matches `epic/*)`."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 35fe3c99-d04d-404c-a60d-0dcb1e4a24d7
  modified: 2026-08-24T18:27:01.067Z
---

**An epic has TWO numbers that do not track each other**, and the branch name must carry both:

```
epic/AVCH-18-epic-19-adk-2x-runtime
     └ ticket   └ sprint   └ slug
```

`<JIRA-KEY>` (`AVCH-18`) is the epic's **Jira ticket**. `epic-<N>` (`epic-19`) is its **sprint /
BMAD epic number** — the one the board key, `sprint-status.yaml`, `epics.md` and
`_artifacts/epic_<N>/` are all filed under.

**Why:** operator ruling 2026-08-24 (SCC-316). A branch naming only the ticket made every reader
hold the mapping, and the two are close enough to look like a typo of each other —
`epic/AVCH-18-…` sitting beside artifacts at `epic_19/` reads as drift on every glance.

⛔ **The `epic/` prefix stays in FRONT. The sprint number goes in the SLUG, never ahead of the
prefix.** `epic-19/AVCH-18-…` was the operator's first spelling and was rejected on **measured**
cost, not taste:

- every `$EPIC` resolution globs `epic/*` (`git branch --list 'epic/*'`,
  `for-each-ref 'refs/remotes/origin/epic/*'`) → all of them fall back to `origin/main`, which is
  the stale-ref defect SCC-165 swept out of this family
- `merge-target-guard.sh:159` — an **armed** hook — classifies with a `case` arm spelled literally
  `epic/*)`, so the branch becomes `unknown`
- **147 references across 38 files**, incl. three git hooks, `main_write_gate.py`,
  `closeout_preflight.py`, `ship_preflight.py` and six test files

**How to apply:** cut every new epic branch as `epic/<JIRA-KEY>-epic-<N>-<slug>`. When renaming a
live one: push the new ref from the **same sha**, verify both refs report that sha, delete the old
ref, then `git branch -m` locally. Never rename while a story lane is mid-landing against the old
name. AviationChat's Epic 19 was renamed this way; `epic/AVCH-23-thin-toolkit` was deliberately left
alone and takes the new shape when next cut.

Related: [[git-branch-model-standard]] · [[nothing-guards-the-merge-target]] ·
[[sudo-commands-have-ap-twins-that-drift]]
