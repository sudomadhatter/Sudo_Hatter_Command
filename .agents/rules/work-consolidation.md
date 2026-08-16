---
name: work-consolidation
description: "Fires the moment work is DISCOVERED mid-lane, and again when a Task's subtasks are planned. Six rules, each with the command that answers it: (1) look for a home before you mint — discovered work becomes a lettered part under an open parent, and minting is legal only after you say what you looked at; (2) when able, ONE worktree and ONE branch carries a whole Task including its subtasks, declared as `riders:` in task.yaml, keyed per-commit by the subtask and closed once under the parent; (3) verify the batch in one block, not one command per part; (4) artifact-first — a constraint or a skipped step goes into the walkthrough the moment it is known; (5) two stops per lane (plan approval, merge sign-off) and nothing else; (6) verify the OUTCOME of a board write, never the exit code. Judgment, not a gate: the agent decides and says why. Operator ruling, 2026-08-15. Pairs with worktree-per-story.md and jira.md."
---

# Work Consolidation — one home, one lane, one close

> **Why this exists, in the operator's words (2026-08-15).**
> *"every task we develop seems to find new bugs to fix, this as of now leads to 2 or 3 new task
> tickets for every one found. … Rules: 1. look for a ticket to add one issue fixes too 2. when able
> use one workingtree/branch to develope the whole ticket including subtasks. close it all out with
> one SCC or AVCH tag for git. then manually just move the subtasks to done."*
> … *"we are not developing 3 task for every 1 we try to fix."*
> … *"I just said I want to do as much as i can in one run on one workingtree/branch. i know its not
> the best coding practice but as slow as this is going I have no choice"*

The system was correct and unusably slow. Every lane found real defects, every defect became a Task,
every Task became a worktree, a plan, an audit, a review, a close-out — and the queue grew faster than
it drained. This rule is the compaction: **the same rigor, spent once per batch instead of once per
finding.**

⛔ **This is judgment, not a gate.** No check enforces rules 1–6; a command may WARN, never block. The
operator ruled it directly: *"the goal is the agent looks first and tries … this is not black and
white."* What is mandatory is **saying what you decided and why** — in the walkthrough, in the plan, or
in the ticket. An unstated choice is the thing this rule bans, not a particular choice.

---

## Rule 1 — Look for a home BEFORE you mint

Work discovered mid-lane (a review finding, a bug met while building, a defect a test exposes) is
**not** automatically a new ticket. In authority order:

1. **Does this lane's own ticket cover it?** Then it is a checklist line in the plan or the ticket's
   `ACCEPTANCE` block. Three edits in one commit are not three tickets.
2. **Is there an OPEN parent whose surface this belongs to?** Then it becomes the next **lettered
   part** — a `Subtask` under that parent, with a row in the parent's index description. This is the
   normal answer.
3. **Nothing fits?** Mint — and say in ONE line what you looked at. That sentence is the whole
   enforcement mechanism.

```bash
# The look, before the mint. Both, and read them:
acli jira workitem search --jql "project = SCC AND statusCategory != Done AND type = Task ORDER BY key DESC" \
     --fields key,summary --limit 50
acli jira workitem view <the-parent-you-suspect>      # does its surface really cover this?
```

⛔ **The parent's description is an INDEX, and `acli edit --description` REPLACES the field.** Append a
row by reading the description, adding the row, writing it back, and **reading it back again** to
confirm every prior line survived. SCC-164 lost its Part E row exactly this way. Use:

```bash
python3 .agents/scripts/jira_feed.py index-row --key <PARENT> --line "  Part M  SCC-000  one line" --apply
```

It refuses (exit 2) if the read-back is missing any line it did not add. This is a **data-loss guard**,
not a policy gate — the one place in this rule where a mechanism earns its keep.

## Rule 2 — When able, ONE worktree and ONE branch for the whole Task

**"When able" means: same repo, same lane class, and no genuine need for parallelism.** A consolidated
lane is the default answer for a Task whose subtasks share a surface; the per-subtask-worktree mode
stays for work that really does run side by side (`/smh-label-tasks` computes that set).

| | Consolidated lane | Per-subtask lanes |
|---|---|---|
| Worktree / branch | ONE, keyed by the **parent** — `chore/<PARENT-KEY>-<slug>` | one per subtask |
| Plan | one `implementation_plan.md`, N part sections | one per lane |
| Manifest | `riders: [<every subtask key>]` in `task.yaml`, written at cut time | no riders |
| Commits | **the SUBTASK's key per commit** — each child's Jira dev panel shows its own commits, and a part can be reverted as a unit | the lane's own key |
| The merge | ONE `--no-ff` merge under the **parent's** key | one per lane |
| Close-out | ONE ceremony: riders flip to Done first, parent last | one per lane |
| Gate | ONCE, at the tip, through the receipt writer | once per lane |

**The order the parts are built in is the overlap map, not a preference.** Run `/smh-label-tasks
<PARENT>` and use its output as BUILD ORDER: parts that share a file are sequenced, and the part that
makes the *rest of this lane* cheaper goes first.

**Partial landing is legal and declared, never improvised.** If the lane must ship before every part
is built, write `landing_mode: partial` in `task.yaml` and **trim `riders:` to the subset that actually
landed**. Then the declared riders flip, the **parent stays open**, and the remainder becomes the next
`chore/<PARENT-KEY>-<slug2>` lane with its own manifest. `task_preflight.py` checks the trim against
the lane's commits and refuses a rider that leads no commit — *never declare a ticket whose work is
not real.*

## Rule 3 — Verify the batch in ONE block

A consolidated lane's verification is **one block of independent commands**, run together, read
together. Per part: that part's own test file and its RED→GREEN capture. For the lane: the full
enforcement suite **once**, at the tip, through `gate_receipt.py` (the receipt run IS the suite run —
never a bare "let me check" run followed by the real one).

## Rule 4 — Artifact-first

A constraint discovered, a conflict met, a lens that died, a step deliberately skipped: it goes into
the walkthrough **the moment it is known**, not at the end. Chat is not a record — a session ends and
takes every unwritten decision with it.

## Rule 5 — Two stops, and no others

A lane stops **twice**: at plan approval (`000-PLAN-FIRST-GATE`, the literal word `approved`) and at
the merge sign-off (the operator invoking the close-out command). Everything between them is the
agent's: act on the obvious answer, write the choice into the walkthrough, keep going. Do **not** ask
"post now or later", "keep it narrow or widen it", "should this be its own ticket" — decide, record,
move.

## Rule 6 — Verify the OUTCOME of a board write, never the exit code

`acli` exits 0 on writes that recorded nothing. Every board write is followed by a read-back that
proves the thing is there — `jira_feed.py` does this internally and exits non-zero when the read-back
is empty. A non-zero exit means the write did **not** land: report that, never success.

---

## Where this rule is cited

`/smh-plan-task` (consolidated mode at cut time) · `/smh-close-task-merge-tree` (riders + partial
landing) · `/smh-quick-dev` (discovery → a lettered part) · `/smh-quick-fix` (same) ·
`code-review-engine` triage (a finding looks for a home before it becomes a ticket).

Pairs with `worktree-per-story.md` (a consolidated lane is still ONE worktree, opened before the first
edit) and `jira.md` (§Subtasks: a Story's answer is still NEVER — this rule is the Task lane's).
