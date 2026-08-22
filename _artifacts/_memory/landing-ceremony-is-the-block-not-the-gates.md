---
name: landing-ceremony-is-the-block-not-the-gates
description: "SCC-184 (docs-only, all gates green) could not reach main in a full session — the block was the hand-typed Step 3 landing in the shared checkout vs the agent's permission layer, never a gate; the PR door already works and is the fix (SCC-183 R3)"
metadata: 
  node_type: memory
  type: project
  originSessionId: b0d18846-6aa5-48aa-bf0a-033d6aaad1e9
  modified: 2026-08-16T15:48:36.082Z
---

**2026-08-16.** SCC-184 — 226 lines of docs, 0 deletions, suite 32/32 — did NOT land after a full
session. Every gate passed. What failed was `/smh-close-task-merge-tree` **Step 3**: ~15 hand-typed
git/gh incantations run in the SHARED main checkout, each string judged separately by the agent's
permission layer (allow-list + auto-mode risk classifier; a hook `ask` = DENY there).

Measured, controlled pair — same op, same target: `git merge X --no-ff` ALLOWED ·
`git -C <path> merge X --no-ff` DENIED. The allow-list is written bare; [[nothing-guards-the-merge-target]]
mandates `-C`. **Obeying the safety law guarantees the permission miss.** Also: the shared checkout
held another session's uncommitted files (stash denied); a landing worktree at `origin/main` dodges
that and the minter refuses it (`HEAD is 'HEAD', not 'main'`); the gate-ref push and the settings
edit were denied by the risk-judging layer, so adding allow-list patterns never converges; a denial
mid-ceremony strands state (local merge made, token TTL running).

**Why:** the ceremony was sized for deployable code and it is the *shape* — many strings, shared
tree — that fails, not any one gate. Adding gates cannot fix it; SCC-183 R1/R2 were the fix and were
themselves reviewed FAIL/parked because their landing needed the broken step.

**How to apply:** the road that works is a **pull request** — PR #5 (SCC-153) landed 2026-08-14 with
`main-write-gate` SUCCESS as a merge commit; the ruleset requires that check on `pull_request`;
`main_write_gate.py --mode pr` passed both live lanes. Push the chore branch (free), `gh pr create`,
the operator merges (their click IS the sign-off; no token because a GitHub merge never touches a
machine — SCC-118's own words). ⛔ **RULED, not pending — SCC-183 shipped R4, a DELETION** (2026-08-16).
The old open question — operator clicks vs agent merges on the words — is closed in favour of **(b1) the operator clicks**, and R3's
machinery went with it: `land_pr.py` (470 lines), `test_land_pr.py`, and the self-merge split with
its `merge_eligible` / `is_prose` predicate are all deleted. There is no eligibility test and no
"small enough" class — `git-policy.md:125` carries the law. The sign-off is the click: *"not a
token, not 'invoking the command', not an inferred approval."* Order ran SCC-184 → SCC-183 →
SCC-164 second half (re-derived; Part G closed by design). Related:
[[main-merge-needs-operator-verbatim-approval]], [[hook-ask-becomes-autodeny-in-auto-mode]],
[[lightweight-lane-for-specific-no-break-work]].
