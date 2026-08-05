---
name: shared-registration-file-entangles-stories
description: "In AGY's one-working-tree multi-story flow, shared files like registry.py carry hunks from sibling in-flight stories; a blanket git add can commit a router registration without its untracked module and crash a clean-checkout boot."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6de074f5-9dd8-494a-b4f4-248b2a922496
---

AGY develops several stories concurrently in ONE uncommitted working tree, so a shared
registration file (`backend/routers/registry.py`) accumulates hunks from MULTIPLE sibling
stories at once. Each hunk does `from backend.routers import <mod>` at **startup**
(`register_all_routers`, called by `main.py`). If story A's close-out `git add`s the whole
`registry.py`, it stages story B's `include_router` line too — but B's module is still
untracked → a clean checkout (CI/CD, Cloud Run) crashes on `ModuleNotFoundError` at boot.
Local runs mask it because the untracked file is physically present.

Seen 2026-07-02: story 8.19.6 (`sudoadmin`) and 8.20.2 (`admin_cost`) both landed adjacent
hunks in `registry.py`; 8.19.6's walkthrough `git add registry.py` would have shipped the
`admin_cost` register without `admin_cost.py`.

**Why:** the tests pass green (module present locally), so this slips past the suite gate —
it only bites on a fresh clone. It's a commit-hygiene / release defect, not a test failure.

**How to apply:** during `/sudo-code-review` (and close-out), don't trust the walkthrough's
`git add` list — `git diff --cached` (or per-hunk `git add -p`) any SHARED file (registry,
barrel/index, DI wiring) and confirm every staged `import X` has its module `X` staged too.
Guard line: `git diff --cached backend/routers/registry.py | grep -q admin_cost && echo STOP`.
Relates to [[story-status-flip-contract]] (both are close-out correctness gates the human owns).
