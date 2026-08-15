# Walkthrough — SCC-155 — plan-the-whole-Task + labelling surface v2 + user-tasks close-out

**Lane:** `chore/SCC-155-label-tasks` in `.claude/worktrees/label-tasks`
**Plan:** [implementation_plan.md](implementation_plan.md) · **Manifest:** [task.yaml](task.yaml)
**Operator rulings this lane:** retire `/cicd-parallel-check` (reuse the logic, delete the
command, only *after* the replacements are complete) · add a whole-Task planner · **"no sub task
we need to one shot this"** — SCC-155 itself gets no Subtasks, all three clusters land here.

---

## Task Checklist

- [x] **A1 — one labelling engine, two commands.** `parallel_check.py` → `label_tasks.py` by
      `git mv` (history preserved). Story mode serves `/cicd-label-tasks`; **task mode** serves
      `/smh-label-tasks` with its own grounding ladder (branch-diff → sibling `task.yaml`'s plan →
      the ticket's own description; ambiguity counts as an EDIT). Both stamp `parallel-ok` **and**
      `quick-dev`, and both post a verdict comment on the parent.
- [x] **A2 — `/smh-plan-task` plans the whole Task in one shot.** Propose-and-STOP → mint the
      Subtasks → per subtask: cut the worktree, write the plan into that lane, self-audit, commit
      and **push**, update the ticket → finish by invoking `/smh-label-tasks` and printing the
      parallel table.
- [x] **A3 — batch approval is recorded evidence, never self-written.** One STOP presents every
      plan, its audit verdict and the parallel table; the operator's **verbatim** words are
      recorded into each plan (the SCC-37 quote pattern). `000-PLAN-FIRST-GATE.md` gains a narrow
      clause with four mandatory conditions; any edit to a plan re-arms the gate.
- [x] **A4 — open operator actions hold the ticket out of `Done`.** `jira_feed.py finish` reads
      the walkthrough's `## Your Actions

- [x] **Install a review column on the SCC board.** Done — you created it and named it
      **`Review Required`**. It now leads `finish`'s ladder, which turns the no-column
      fall-through from the live path into the corner case it was always meant to be.
      `--review-status` overrides the whole ladder, so if the board ever renames that column
      it is a flag on one invocation, not an edit and a release.
- [x] **Run the memory audit.** Done. The rows were **doubly** stale: they named
      `/sudo-parallel-check`, a name SCC-63's naming law retired *before* this lane renamed it
      again. The lesson still bites, so it was a mechanical repair, not a retirement — the
      rename history is recorded, both current commands are named, and the store now says
      `quick-dev` has a second writer. Floor 46/46; index 18,485 / 25,600 bytes.
- [x] **The ten deferred findings.** Rolled into this ticket on your ruling — no follow-on.
      All applied test-first; see the findings table above, every row `applied`.

Nothing is owed. This section is deliberately left with its boxes ticked rather than deleted:
`jira_feed.py finish` reads it, and an absent section is a refusal, not a pass.

### Still worth your eye at close-out — not blockers, not owed work

- **Landing order against `chore/SCC-156-lane-speed`.** It is live and overlaps this lane on 10
  files. `merge-tree` predicts two conflicts, both in generated/index files
  (`.agents/.sync-manifest.json`, `_artifacts/_main/INDEX.md`) — resolved by **regenerating**,
  never by hand-merging. Whichever lands second absorbs `main` and re-runs `sync-agents`.
- **`Review Required` is asserted, not observed.** The board has no ticket in that column yet, so
  the exact status string is pinned by test and by your word, not by a live transition. The first
  real held close-out proves it; if the string is off, `--review-status` fixes it without a code
  change and the `user-tasks` label carries the signal meanwhile.
