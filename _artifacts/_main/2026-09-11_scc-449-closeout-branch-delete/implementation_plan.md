# SCC-449 — the close-out leaves merged branches behind, and the door licensed it

**Ticket:** SCC-449 (Task) · **Branch:** `chore/SCC-449-closeout-branch-delete` · **Lane:** solo, one part
**Approved:** 2026-09-11, operator — *"Approved fix it"*

## The problem, measured

At the close of SCC-447 the door's own Step 5 ran `git branch -d` and git refused: *"the branch is not
fully merged."* The branch **was** fully merged — `git rev-list --count origin/main..<branch>` returned
**0**. The refusal was git answering a different question than the one that matters.

**Why it refused.** `git branch -d` checks *merged-into-upstream* when an upstream is configured and
*merged-into-HEAD* when one is not. This lane's branch had **no upstream**, because the sandbox cannot
write the lobby's `.git/config` (`.git/config.lock` is a char device — `approval-cost-is-a-threat`'s
measured environment), so every lane here pushes without `-u`. With no upstream, `-d` fell back to
HEAD — the shared lobby standing on `main`, which was **20 commits stale**. It compared a merged
branch against a `main` that predated the merge and answered honestly about the wrong reference.

**Why it kept happening — three compounding causes, and this is the part that matters.**

1. **The door states a FALSE diagnosis.** Step 5 says: *"A refusal here after a successful Step 3 means
   the merge did not land — go look, do not force."* That is wrong. After a successful Step 3 the merge
   **has** landed; a refusal means the check is pointed at a stale reference. An agent following the
   door goes looking for a failed merge, finds a landed one, has no instruction for that state, and
   retains the branch.
2. **Step 6's verification carries a blanket escape.** Its report template reads
   `Pruned: … local + remote` ***(or why it was retained)***. A verify step that accepts its own
   failure as a valid outcome can never fail. Every occurrence was reported as compliant.
3. **The correct knowledge exists in the SIBLING door and was never ported.** `/cicd-prune-worktree`
   Step 5 documents the upstream-vs-HEAD mechanism in full, measured 2026-08-01 ("all three
   set-close-out `-d`s failed remote-last, all three succeeded remote-first"), deletes the **remote
   first** on purpose to force the real ancestry question, and spells out the refusal ladder. The Task
   door has none of it and uses the opposite order. A half-port — the failure class SCC-447 exists to
   catch, in the door that closes SCC-447's own lane.

**The measured recurrence, taken 2026-09-11 before any cleanup:** 7 local and 10 remote lane branches
left behind; **5 of the 7 local branches had no upstream at all**, which is the root cause visible in
the data. 14 of them were fully merged and safe to remove; 2 held genuine unmerged work. The
enforcement suite was 90/90 green throughout — nothing in the repo could see any of it.

⛔ **And the workaround was stored where no gate can reach it.** An agent-memory note recorded the
refusal as expected and prescribed *"RETAIN the branch and say why — never `-D`"*. That note is the
license: it converted a defect into policy, outside the repo, where no test, lint or suite run can
contradict it. Rules, commands, hooks and scripts are checkable; a note is not. (The general form of
this is **SCC-448**, parked; this lane fixes only the close-out instance and moves its knowledge into
the door.)

## Acceptance — checkable

| Row | Statement | Proved by |
|---|---|---|
| **A** | `smh-close-task-merge-tree.md` Step 5 deletes the **remote first**, then the local branch — the order `/cicd-prune-worktree` measured — and says why the order is load-bearing | `test_closeout_branch_delete.py` block A, with a counter-example the check must reject |
| **B** | Step 5 no longer claims a refusal means the merge did not land. It names the real cause (no upstream → `-d` falls back to HEAD → a stale shared `main`) and gives the ladder: prove with `merge-base --is-ancestor <branch> origin/main`, then pin the check at the landing ref with `--set-upstream-to=origin/main` and re-run `-d`. `-D` stays banned | block B |
| **C** | Step 6's retention escape is gone. A branch proven merged and still present is a **failed** close-out, not a reportable outcome; retention stays legal only for a branch that genuinely did not land, which is a different and provable claim | block C |
| **D** | Both doors agree on the mechanism — the sentence that `-d` checks upstream-when-set and HEAD-when-not appears in the Task door and in `/cicd-prune-worktree`, so the next half-port fails | block D (a cross-door check, the SCC-447 twin-law shape) |
| **E** | The agent-memory note that licensed retention is deleted, and its real content now lives in the door | block E: the note's path is absent; the door carries the mechanism |

## Design

**D1 — the order is the fix, not a preference.** Deleting the remote first removes the upstream in
every case, which forces `-d` onto merged-into-HEAD: a real ancestry question. The Task door's current
order asks the upstream question first, which on a `-u`-less push is no question at all.

**D2 — the HEAD fallback still lies when the lobby is stale, so the door owes a ladder.** Unlike the
story lane (where `main` legitimately lacks the story until its epic lands), a Task lane's merge **is**
on `main` the moment the PR merges. So a refusal here has exactly one honest cause — the shared
checkout has not caught up — and exactly one correct remedy, which keeps the safety check intact
rather than bypassing it: point the check at the landing ref.

```bash
git rev-list --count origin/main..chore/<KEY>-<slug>          # 0 = every commit landed; anything else, STOP
git branch --set-upstream-to=origin/main chore/<KEY>-<slug>   # aim the check at the ref that HAS the merge
git branch -d chore/<KEY>-<slug>                              # now -d asks the right question, unbypassed
```

⛔ `-D` remains banned. The point is not to force past the check; it is to stop asking it the wrong
question. Never pull the shared lobby to fix this — it carries other sessions' uncommitted work.

**D3 — a verify step may not accept its own failure.** Step 6 asserts the branch list is empty. If it
is not, the close-out is incomplete and says so. The only legal retention is a branch that did not
land, and that is provable with the same `rev-list` count.

## Declared Change Set

- EDIT `.agents/commands/smh-close-task-merge-tree.md` — Step 5: remote-first order, the ladder, the corrected diagnosis; Step 6: the escape removed → A, B, C, D
- EDIT `.opencode/commands/smh-close-task-merge-tree.md` — byte mirror → A, B, C, D
- NEW `.agents/scripts/tests/test_closeout_branch_delete.py` — blocks A–E, every content check with a counter-example applied in memory → A, B, C, D, E
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — the close-out's branch-delete row says the mechanism and the ladder → A, B
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one row → A, B, C
- DELETE `~/.claude/projects/-home-dlohn-Sudo-Hatter-Command/memory/closeout-prune-blocked-by-a-stale-lobby.md` + its `MEMORY.md` pointer — the license; its content moves into the door → E

## Risks, named

- **The door is the file that closes this very lane.** The lane lands through the door it is editing, so
  the fixed text is read from `origin/main` at `--after-merge`, exactly as SCC-193 requires. That is
  why the lane's own close-out is the first real exercise of the fix.
- **`--set-upstream-to` writes `.git/config`, which the sandbox refuses.** It needs one sandbox-off
  call. The door says so rather than leaving the next agent to rediscover it.
