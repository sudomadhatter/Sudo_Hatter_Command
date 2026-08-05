---
name: parallel-lanes-fix-the-same-finding
description: "Two lanes running on one triage doc can ship the SAME fix; re-diff main_debug before close-out, the Part 1/Part 3 split does not partition files. With 3+ lanes open the operator's rule is RECONCILE THE SET — no lane lands alone"
metadata: 
  node_type: memory
  type: project
  originSessionId: 53787862-b9c8-4d97-bbe2-1b6379c921c0
  modified: 2026-08-01T03:23:44.951Z
---

AGY runs a quick-dev lane and a full ①②③ lane in parallel off one triage doc. On 2026-07-25 both
lanes fixed the same two findings: story debug-2.3 (full lane) landed the identical
`toast.error("SIGN IN FAILED", …)` and reset-toast on `main_debug` while story debug-3.1 (quick-dev)
was building them on a worktree branch. `main_debug` moved 4 commits under the open branch.

**Why:** the triage doc's Part 1 / Part 2 / Part 3 split partitions *findings*, not *files* or
*lanes*. Nothing stops the other team's story from touching the same handler, and neither team sees
the other's branch. A quick-dev batch is exactly the window where this bites — it runs long enough
for the full lane to land, and its whole premise is small fixes on shared surfaces.

**How to apply:**
- Before close-out, re-diff `main_debug` against the branch base. `git rev-list --left-right --count`
  then `git merge-tree --write-tree --name-only` gives a non-destructive conflict list.
- **Merge BEFORE you build, not just before you close out** (added 2026-07-26, story 21.3). A branch that
  sat while the other lane landed is missing that lane's **tests**, not only its code — and a test you
  cannot see cannot fail. 21.3 planned an 8th roster column; the merge brought
  `student-roster-email-first.red.test.tsx`, which asserts `cells[cells.length - 1]` carries the pinned
  sticky classes. Building first would have looked **green locally** and broken on landing, with the cause
  a merge away from the symptom. Treat "merge `main_debug`" as a blocking precondition of the first edit
  whenever the branch is older than the trunk.
- **Catch the collision at ①, and serialize on the shared EDIT SITE — not on the missing symbol**
  (added 2026-07-31, story 21.11). 21.11's ① found it needed `demo_master.is_master_demo_uid`, a
  predicate story 21.8 owns and had not built. The tempting read is "21.11 is blocked on a missing
  module" — wrong, and it under-states the problem. Reading 21.8's `implementation_plan.md` showed
  it also modifies `check_cost_cap` ("consult the predicate at the top … return allowed for the
  master") plus `usage_guard.py` — byte-for-byte the edit 21.11's own task list described. The two
  lanes would have conflicted **inside that one function whether or not the module existed**, and
  could have shipped two divergent fail-closed predicates. Two consequences: (a) when ① discovers a
  sibling story owns a symbol, read that story's plan/tasks for the *files and functions* it
  touches, not just the symbol it exports; (b) an **add/add conflict on a brand-new file has no
  merge base**, so a reviewer must hand-pick between two whole implementations — much worse than a
  normal 3-way. Record the gate in the story frontmatter (`blocked_by:`) AND the board row, with an
  explicit machine-checkable start condition (`git ls-tree main_debug -- <path>` returns the file,
  then merge). Also state how many reds are actually gated: 21.11's were 6 of 25, so the story was
  never "blocked" as a whole — only its ② start was. **Structural fix landed same day:**
  `/update-personal-sprint-map` Step 2.5 now derives every parallel claim as a verdict (touch-set
  intersection from branch diffs + implementation-plan "Modify" lines + story surfaces, plus
  contract edges) — ✅ needs evidence, no-story-file = ⚠️ scheduled as serialized, and quick-dev is
  P2/P3-only. If a board asserts "parallel" without a verdict table, it predates that fix.
- **At 3+ open lanes the unit of landing is the SET, not the story** (operator ruling 2026-07-31,
  Epic 21). Four worktrees ran at once — 21.8, 21.9, 21.10, 21.11 — all against the same demo tenant.
  Daniel's rule: **no lane lands on `main_debug` on its own.** Merge `main_debug` into each branch,
  re-diff the lanes against *each other* (not just against trunk), resolve overlaps, then land. The
  pairwise habit above does not scale: it catches lane-vs-trunk drift but is blind to lane-vs-lane
  overlap, which is where 21.8 ∩ 21.11 (`check_cost_cap`) and 21.8 ∩ 21.10 (the demo account's
  session lifecycle — one resets it, the other dirties it via the real checkride consequence) both
  live. **Branch bases diverge fast:** on 07-31 `main_debug` moved twice inside one ① session, and a
  lane branched before `f3dcdf9d` would have re-introduced the committed active-context merge
  conflict that had just been fixed. Also expect *every* lane to touch `active-context.md` and the
  sprint map — those two files collide by construction, so treat them as always-conflicting and
  resolve them last, in one pass, rather than per-lane.
- **The set-rule binds on PRODUCTION-FILE OVERLAP, not on lane count** (operator amendment 2026-07-31,
  story 21.8 close-out: *"just for this story we will reconcile the other ones to this one"*). With the
  same four lanes open, 21.8 landed **solo** — and it was provably safe, not merely permitted. The test
  is cheap and should be run before invoking the set flow, because it can dissolve it:

  ```bash
  for b in <lanes>; do git diff --name-only $(git merge-base claude/$b origin/main_debug)..claude/$b; done
  ```

  Here 21.9/21.10/21.11 were **①-only** — each touched just its own story file and its own new red file —
  so the sole intersection with 21.8 was `sprint-status.yaml`, where every lane owns a distinct line. The
  lane-vs-lane overlaps the ruling was written to catch (21.8 ∩ 21.11 on `check_cost_cap`) are **planned**
  overlaps that had not been written yet; a set-landing would have bundled three lanes with no code in
  them. **Read the rule's purpose, not its trigger:** it exists to stop two lanes editing one function, so
  when the diff proves disjoint production files, land and let the rest reconcile *to* the landed trunk.
  Corollary that argues FOR landing early: those three lanes' board rows still read `backlog` on the trunk
  while their worktrees had ① done — holding a finished lane back does not keep the board honest, it just
  extends the [[landing-is-not-closeout]] window for everyone.
- **Do not trust the other lane's close-out commit message about the board.** debug-2.3's commit said
  "close out — status done, board + learnings" and its `sprint-status.yaml` hunk added only story 11.19's
  line; debug-2.3 itself was never written to the board. Grep the board for the other story's id (BOTH
  dot and dash forms) rather than assuming its close-out ran clean — see
  [[sprint-dependency-map-recommends-stale-work]].
- When both sides fixed it, keep the *residue*: the cleanups the other lane skipped (dead state left
  standing, a banned `any` in their catch). Take their render/UI wholesale.
- The resolution may be **forced** rather than chosen — here the merge auto-applied our deletion of a
  state declaration while leaving their orphaned write inside the conflict region, so their side
  would not compile. Check for that before agonising over the choice.
- Debt one lane logged for the operator may already be **closed** by the other. Mark it closed, not
  deferred, or it resurfaces as a phantom follow-up — see [[settled-decisions-are-not-gaps]].
- The seam between two independently-correct fixes is where the untested case hides. Here: one story
  pinned success→card, the other failure→toast, neither pinned failure→NO-card.

Related: [[landing-is-not-closeout]], [[git-branch-model-standard]],
[[shared-registration-file-entangles-stories]], [[red-file-hosts-expansion-tests]].
