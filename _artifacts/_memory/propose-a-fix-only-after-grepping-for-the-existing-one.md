---
name: propose-a-fix-only-after-grepping-for-the-existing-one
description: "Before proposing ANY new mechanism, grep for the one the repo already has — and bring a plan with solutions, not a stream of concerns"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 75c473ee-850f-49df-8333-fbd4cd0cab4a
  modified: 2026-08-21T02:35:58.838Z
---

When a defect surfaces mid-lane, do NOT propose or build a fix until you have grepped the repo
for an existing mechanism that owns it. On SCC-240 (2026-08-20) a wrong-tree test run surfaced;
I proposed and started building a tree label in `_harness.py` — and the SCC-190 guard already
existed in `run_all.py`, pinned by `TREE` cases in `test_suite_runner.py`. The right move was to
EXTEND it (one body, `wf_common.tree_guard`), which is what shipped.

Second half, operator's words: *"why do you just keep adding problems with no solution? I want a
plan to fix things not new concerns every reply."* When reporting a defect, every concern arrives
WITH its solution inside the same plan — a wrinkle you name without resolving is a stop you forced
on the operator.

**Why:** the operator is blocked on a growing queue of toolkit tickets before real project work;
every invented mechanism and every unresolved "one wrinkle" is a stop that costs a session. See
[[settled-decisions-are-not-gaps]] (same failure, one level up) and
[[bash-cwd-resets-to-main-checkout]] (the hazard that triggered it).

**How to apply:** (1) `grep -rn <the symptom's keyword>` across `.agents/scripts/` and its tests
BEFORE writing a line; if a mechanism exists, extend it in its own vocabulary. (2) In the plan,
each risk row carries its fix in the same row. (3) Since SCC-240, single-file test runs from the
main checkout REFUSE while a lane worktree exists — `--on-main` on the file or `WF_ON_MAIN=1`
allows it; run tests by ABSOLUTE path into the worktree.
