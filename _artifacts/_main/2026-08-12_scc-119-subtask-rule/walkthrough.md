---
type: walkthrough
task: SCC-119
branch: chore/SCC-119-subtask-rule
---

# SCC-119 — Subtasks: the ticket you were handed is the top-level one

**What changed, in one line:** work an agent breaks out of a ticket now goes **underneath it as
`Subtask`s** instead of beside it as more `Task`s — and the five places in the toolkit that actively
refused subtasks were fixed, including one that was corrupting the board on every commit.

## Task Checklist

- [x] **The rule** — `.agents/rules/jira.md` §Subtasks: hierarchy (three levels, no nesting), the
      parent's-type discriminator, the one test, the branch+worktree threshold, the mint seam, the
      lifecycle. Plus the `Subtask` row in the five-types table and the close-out routing table.
- [x] **`jira_feed.py start`** — the `Subtask` refusal **deleted**. This was the live defect.
  - ⚠️ It also made `have` unused; removed rather than left dangling. `start` now gates on **status
    alone**, which is correct: every type a keyed branch can carry is startable.
- [x] **`jira_feed.py flag`** — `Epic` and `Subtask` refusals **split**. A subtask still refuses, but
      the reason is now true and the refusal **names the parent to flag instead**.
  - ⚠️ The old message argued against itself: it called a subtask "a container" (it is a leaf) and
    then said *"flag the child ticket whose work broke"* — which is the ticket it had just refused.
- [x] **`jira_feed.py audit`** — subtasks are no longer skipped as "containers". `check_subtask()`
      checks **placement**: no parent · parented to an `Epic` · nested under another subtask · a
      parent lagging its children. **None auto-fixed** — re-parenting is a board move.
  - ⚠️ `print_human` was **hoisted out of the branches**: the `--apply` path never printed the
    report, so placement findings would have been invisible on exactly the run an operator makes
    when they intend to fix the board.
- [x] **`task_preflight.py check_children()`** — a parent cannot close while a child is open.
      `Deferred` is the escape hatch. First network call this script has ever made.
- [x] **Command bodies** — `/smh-quick-dev` Step 1.6 (propose-then-stop) and the deleted exit-2 row;
      `/smh-close-task-merge-tree` re-checks children with the board in hand before writing `Done`.
- [x] **`scripts/INDEX.md`** — three sentences this change made false, corrected.
- [x] **SOP** + **8 platform doors** regenerated via `sync-agents`.

### Cut during the build — both are the audit's own tripwires firing on my plan

| Planned | Cut because | Instead |
|---|---|---|
| `devrecord --closing` subtask guard | The restore branch is `if have == "Bug":`, and a subtask never carries `Bug` under the ruling — **the guard defended an unreachable state** (*"error handling for states that cannot occur"*) | **No code.** A characterization test pins that a subtask through `--closing` is not re-typed |
| `mint --parent-key` | `mint` renders a description **from a story file**; a subtask has none. And Tasks are already minted with raw `acli`, never through `mint` — *a flag no acceptance item requires* | The exact `acli` form documented in `jira.md` §Subtasks |

### Deviation from the plan — stated, not slipped in

**Plan §4a.3 said an unreachable board must flip the VERDICT to `NOT CLEAR`. It does not.** It warns.
Sandboxed agent shells cannot reach the OS credential store at all (`jira.md` §top), so blocking there
would have made `NOT CLEAR` the *normal* output of a preflight that has always worked offline — and a
verdict that fires constantly stops being read. The second layer is `/smh-close-task-merge-tree`, which
re-asserts the check immediately before it transitions the ticket, where the board is provably
reachable. Neither layer is load-bearing alone — the same shape as the two `start` seams (SCC-113).

## Evidence

| AC | Proved by | Result |
|---|---|---|
| AC1 rule written | `jira.md` §Subtasks + type/close-out tables | inspection |
| AC2 story lane never | rule text; AVCH still holds **0** subtasks | board-verified |
| AC3 branch+worktree threshold | rule text + `/smh-quick-dev` Step 1.6 | inspection |
| AC4 propose then stop | Step 1.6; no board write in any code path | inspection |
| AC5 subtask lane no longer breaks the board | `test_jira_feed.py` — **L905 inverted**, was `code == 2`, now `code == 0` | 152/152 |
| AC6 parent closes last | `test_task_preflight.py` — open blocks, `Deferred` does not, failed query never reads clean | 100/100 |
| AC7 subtask never `Bug` | `flag` refuses + names the parent; `devrecord` characterization | 152/152 |
| AC8 nothing says stop-on-Subtask | exit-2 row deleted from `smh-quick-dev.md` | inspection |

**Gate, all bare, at the working tree:**

```
run_all.py            21/21 files · 1110/1110 cases   exit 0   (baseline 1091 → +19 new)
workflow_lint.py --toolkit-only   0 errors, 0 warnings, 8 info   exit 0
sop_currency.py       exit 0 WITH the SOP doc · exit 1 WITHOUT (positive control, "Commit rejected")
py_compile            4 changed .py files clean
link + anchor         24 links across 8 changed docs, 0 problems
hooks_armed.py        ARMED — core.hooksPath=.githooks
```

**Mutation evidence — 3/3 killed on the one gate that could have shipped vacuous:**

| Mutant | Killed by |
|---|---|
| unreadable board reads as "no children" | 3 cases |
| `Deferred` no longer counts as closed | 1 case |
| row count instead of exit code | 3 cases |

⚠️ **A false green I caught in my own gate run.** The first two `sop_currency` runs both exited 0 —
including the positive control that was supposed to FAIL. Cause: **zsh does not word-split unquoted
parameter expansions**, so `--paths $POS` passed one newline-containing string that matched no
surface prefix. The gate was fine; my invocation was vacuous. Re-run through `xargs`, it behaves
correctly in both directions. Worth recording because the failure mode is invisible: a gate handed
garbage input reports clean, exactly like a gate handed good input.

## Suite Ledger

| Suite | Before | After |
|---|---|---|
| `test_jira_feed.py` | 141/141 | **152/152** |
| `test_task_preflight.py` | 92/92 | **100/100** |
| `run_all.py` (all files) | 1091/1091 | **1110/1110** |

## Your Actions

**Landed on the branch, not on `main`.** `chore/SCC-119-subtask-rule` is committed and pushed; the
worktree is at `.claude/worktrees/SCC-119-subtask-rule`.

1. **Review, then `/smh-code-review`** — this lane stops here by design. I have not merged,
   transitioned SCC-119, or pruned anything.
2. **SCC-119 itself gets no subtasks, and that is the rule working.** The doc and the machinery that
   enforces it must land together or one of them is a lie, and one gate covers both.
3. **Two things outside this ticket's scope, for your call:**
   - `jira_feed.py start`'s refusal was broken shipped work from SCC-113. Per your ruling it is
     recorded here rather than flagged `Bug` — say the word if you want it flagged instead.
   - Your **memory index carries a dead SOP path** (`_my_resources/_quick_reference/sudo_workflows_testing.md`);
     the real one is `docs/_scc_sops_prds/workflows_testing_SOP.md`. It misled this plan once already.
     Worth a `/memory-audit`.
