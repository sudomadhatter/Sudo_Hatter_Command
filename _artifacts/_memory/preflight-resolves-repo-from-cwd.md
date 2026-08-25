---
name: preflight-resolves-repo-from-cwd
description: "task_preflight/closeout_preflight resolve the repo by walking up from cwd and default --branch to that HEAD, so a close-out can print a fully honest \"clear to merge\" verdict about SOMEONE ELSE'S branch."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f3e01c24-9b74-4562-ba18-4cc66697fffd
  modified: 2026-08-24T19:03:53.248Z
---

`task_preflight.py` resolves the repo by walking up from **cwd** looking for `.git`
(`git_root()`, ~line 56-68) and defaults `--branch` to that repo's current HEAD (~line 300).
`closeout_preflight.py` has the same shape. **cwd resets to the main checkout at slash-command
boundaries**, so a close-out invoked from a worktree lane can silently resolve the lobby instead.

2026-08-09, SCC-60: Step 1 printed `== task preflight - chore/SCC-59-update-maps-indexes ==` …
`VERDICT: clear to close out and merge`. Every check was honest — about the wrong branch.
Proceeding would have merged another lane's in-flight work to `main` under my ticket's close-out.

**Why:** the script cannot know which ticket you *meant* to close, so there is no mismatch it
could detect. And `close-task-merge-tree`'s Step 0 asks you to echo `Repo: <name> | Branch:
<branch>` — which I did, **from belief rather than command output**, so the one guard that exists
could not catch the one thing it is for. Same defect class as reading a sandboxed `acli` failure
as board state ([[jira-integration-live]]).

**How to apply:** pass `--repo <path>` **and** `--branch <name>` explicitly whenever a worktree is
in play — that is exactly when cwd and intent diverge. Derive the Step 0 echo from an actual
`git -C <path> rev-parse --abbrev-ref HEAD`, never from memory, and confirm the resolved Jira key
is the ticket you are closing before reading the verdict at all.

The doc fix (Step 0 derives from output + names the expected key; Step 1 asserts key match and
STOPs on mismatch) was scoped 2026-08-09 and **deferred** — so this memory is the only place it
lives. It now belongs in `.agents/skills/close-task-merge-tree/SKILL.md`, not the command file:
SCC-59 is converting that command to a skill. See `.agents/rules/worktree-per-story.md` (it forbids chore worktrees).

## ⛔ Passing both flags is NOT enough — `--repo` must be the WORKTREE (2026-08-15, AVCH-59)

I passed `--repo` and `--branch` and `--expect-key`, all correct, and still got a **false
`VERDICT: BLOCKED`** at close-out. `--repo` named the repo's **main checkout**; the lane lives in a
worktree. The preflight then split its answers across two trees:

- **ref-based checks read the BRANCH and were right** — `base` (9 ahead, origin/main absorbed),
  `scope`, `landing`, `intent`, `branch`.
- **file-based checks read the WORKING TREE and were wrong** — `manifest` warned "no task.yaml
  declares AVCH-59" (it is in the worktree), `artifacts` listed two *other* lanes' walkthroughs,
  `gate` concluded "foreign evidence never gates this lane", and `sync` raised an ERROR for an
  unrelated uncommitted file that belonged to a different piece of work entirely.

Nothing in the output says which tree it read, so the report looks internally consistent and the
error looks like the lane's. **Point `--repo` at the tree where the branch is checked out** — the
worktree path is a legitimate `--show-toplevel` — and re-read: the same call went to
`0 error(s)`, `clear to close out and merge`.

**And the dirt was not mine.** The main checkout carried an uncommitted `README.md`; it belonged to
another lane. A wrong `--repo` makes another session's dirty tree look like your blocker — and the
temptation is to "clean it up". Don't: park or leave it, exactly as the memory-store rule says
([[commit-and-push-are-one-action]] is about YOUR work, not someone else's).

**Also: cwd persists across Bash calls.** A `cd` I ran to inspect the submodule made the very next
`python3 .agents/scripts/…` resolve against AGY and die on a missing file. Use absolute script
paths and `git -C` on every call — [[nothing-guards-the-merge-target]] is the same failure class
with a worse ending.

## ⛔ `gate_receipt.py` inverts the rule — in a worktree, OMIT `--project` (2026-08-24, AVCH-45)

The same family, opposite advice, so it cannot be guessed from the entries above. `gate_receipt.py`
has **no `--repo`**: `--project <NAME>` resolves the receipts root through the board and always lands
on the **shared checkout**, and `--cwd` does *not* redirect it — `--cwd` only says where the gate
command executes. So in a story worktree:

- `run --story 19-5 --gate suite --project AGY_AVIATIONCHAT --cwd <worktree>` measured the worktree
  correctly (right SHA, right cwd recorded in the receipt) but **wrote the receipt into
  `Projects/AGY_AVIATIONCHAT/_bmad-output/gates/`**, leaving the shared checkout dirty and the lane
  with a stale receipt. Story 19.5's ② hit this too and its walkthrough records it — **twice
  observed, still unfixed.**
- `check … --project <NAME>` reads the wrong tree the same way and reports **`NO RECEIPT — the gate
  has no evidence it ran`** (exit 2) for a receipt that exists and is valid.

**How to apply:** inside a worktree, `cd` there and run `gate_receipt.py` with **no `--project`** —
resolution falls back to cwd and both `run` and `check` hit the lane (verified: same `check` went
exit 2 → exit 0). `--root` is *not* the fix: it is the Task lane's bypass and writes the flat
`<root>/gates/<gate>.json`, not the story lane's `_bmad-output/gates/<story>/<gate>.json`. If a
receipt did land in the shared checkout, copy it byte-identically into the lane, `cmp` to prove it,
delete it from the shared checkout, and leave that tree clean.

**Run the receipt only against a CLEAN tree** — it stamps `dirty_tree: true` with the paths, which is
honest but makes the receipt weak evidence. Commit the docs first, then take the receipt, then commit
the receipt alone.

## ⛔ `closeout_preflight.py` reads the BOARD from the shared checkout too (2026-08-24, AVCH-45)

Same root, third script — and here it makes the close-out door unusable on the **normal** case.
`--project <NAME>` resolves to the project's MAIN checkout, and `--worktree` is only a *sync-check
input*: it does not move where the board is read from. So on a story whose `sprint-status.yaml` row
lives on an **unmerged epic branch** — which is every in-flight story — the preflight answers:

```
[ERR] no board key matches '19-5-adk-agent-evaluation-stage-2'
```

…because `main` has no epic-19 block at all. **Fix: `cd` into the worktree and OMIT `--project`.**
Then it reads the lane and every check answers about the right tree.

**Three of its rows are still wrong from inside the worktree, and all three read as blockers:**

1. **`landed:` compares against `main`, not the epic branch** — so a healthy story lane reports
   *"N commit(s) NOT on main"* plus a "changed on BOTH sides" file list, both measured against a base
   this lane never lands on. `/cicd-close-story-merge-tree` Step 0.6 documents this row as asking
   about the **epic** branch; it does not. Expected noise on the story lane; read it, don't obey it.
2. **`artifacts: no walkthrough.md found`** is a **SLUG MISMATCH**, not a missing file. It searches
   the folder named after the BOARD key (`19-5-adk-agent-evaluation-stage-2`) while artifacts live
   under the lane slug (`story-19-5-adk-eval-stage-2`). The walkthrough was 35 KB with a
   `**Verdict:**` line. Third slug in play: `gate_receipt.py` keys receipts on `19-5`. **One story,
   three identifiers** — same family as [[devrecord-story-slug-forks-the-record]].
3. **`gates: … STALE`** fires on ANY file drift since the receipt, including the receipt's own
   commit. `tests-must-gate-for-real` Rule 4 exempts artifact/doc-only changes; this check does not
   implement the exemption. Verify with `git diff --name-only <receipt-sha> HEAD -- backend/ frontend/`
   before believing it — empty means the certification still stands.

**How to apply:** run it from inside the worktree without `--project`, then **assess the rows, never
the exit code**. Filed with the `gate_receipt.py` half as SCC-317 on rolling ticket SCC-305.
⭐ **Re-measured 2026-08-24 (AVCH-35): passing the WORKTREE PATH as `--project` works too, and is the
better habit** — `cd`-ing in and omitting the flag relies on cwd, which resets at slash-command
boundaries (the very defect at the top of this file). With the path, all three rows above still
misfire exactly as described, but every *other* row reads the lane: board `review` (not main's stale
`deferred`), the walkthrough's `Verdict:`, the file-list, and the gate receipt. Path-as-`--project`
therefore unifies the cure with `story_status.py` — two of the three scripts take it, so **try the
path first and fall back to cwd** rather than memorising a per-script table.
⛔ And the ticket lookup that rule prescribes is itself stale — the rolling ticket's live label is
**`running-bug-list`**, not the `bugs-and-updates` in `.agents/rules/jira.md`; every ticket carrying
the old label is `Done`, so the documented pre-mint search returns zero rows forever.

## ⛔ `story_status.py set` joins the family — and its cure is the THIRD variant (2026-08-24, AVCH-33)

`story_status.py set 19.1 done --project AGY_AVIATIONCHAT` resolved the SHARED checkout and flipped
the MAIN copy of `sprint-status.yaml` + the story file (`board deferred -> done` — main's stale
state was the tell: the worktree read `review`). The flip is supposed to ride the story branch;
written to main's working tree it publishes nothing and dirties a checkout another lane will read.
Recovery: `git -C <main> checkout -- <both files>`, re-run with **`--project <WORKTREE PATH>`** —
it accepts a path, and then writes the lane ([SET] review -> done [AGREE]).

So the family now has three different cures, one per script — **pass the worktree PATH as
`--project`** (story_status), **omit `--project` from inside the tree** (gate_receipt,
closeout_preflight), **pass `--repo <worktree>`** (task_preflight). Same root: name-based
resolution lands on the shared checkout. Check which flag the script takes BEFORE flipping
anything; the tell is always a state transition naming the WRONG current status.