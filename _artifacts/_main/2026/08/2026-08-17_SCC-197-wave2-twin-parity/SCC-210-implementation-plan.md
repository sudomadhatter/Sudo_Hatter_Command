# SCC-210 — rebalance the cicd close-out

Standalone Task. No lane cut yet; nothing edited.
Repo: this one (the command centre). Suggested lane: `chore/SCC-210-close-out-rebalance`.

⛔ Re-grep every line number below before acting on it. All were measured at `origin/main` @
`fd22097`. Numbers drift, and a prior ticket was discarded because its prescription rested on
numbers nobody re-measured.

⚠️ This plan has not been self-audited. Run the task-lane self-audit on it before the plan-first
gate. Treat the acceptance list as a draft to pressure-test, not as settled law.

---

## 1. Context — what is wrong and why it matters

Responsibilities drifted into the wrong commands.

`/cicd-update-sprint-memory` is named for updating sprint memory. It grew into the entire story
close-out: it lands the story on the epic branch, moves the Jira ticket, files the Dev Record, then
calls the prune. `/cicd-close-workingtree` was left holding only disk cleanup.

The SOP records the consequence directly: you almost never type `/cicd-close-workingtree`, because
both story close-outs call it as their own last step.

So the command you type to close out a story is named after a side effect rather than its job. That
is what makes the close-out family hard to remember.

The equivalent task-lane command in the other family does all of this in one place, in the correct
order. The goal here is not novelty; it is making the two families the same shape.

## 2. Target state

| Command | Was | Job |
|---|---|---|
| `/cicd-close-story-merge-tree` | `cicd-update-sprint-memory` | The door. Gate, invoke sprint-memory, land on the epic branch, file the Dev Record, move the ticket, prune. |
| `/cicd-update-sprint-memory` | keeps its name, slimmed | Route learnings to their homes, update board / story / active-context, hold the context budget. Standalone-invocable. |
| `/cicd-prune-worktree` | `cicd-close-workingtree` | The disk utility. Called by the door and by the multi-lane landing command. |

The unit here is a **story**, not a task — hence `close-story-merge-tree`. The other family's unit is
a task. Each door names its own subject; the shape stays identical across families.

## 3. The step-level split

| Step in `cicd-update-sprint-memory` today | Goes to |
|---|---|
| 1 · read current state and artifacts | stays |
| 2 · verify claimed work exists on disk | stays |
| 3 · route each learning to its home | stays — this is what sprint memory means |
| 4 · apply updates to specs / rules / active-context | stays |
| 5 · prune and budget context | stays |
| 6 · artifacts, summary, manual catch | stays |
| 4.5a · Jira transition | **the door**, and after the landing |
| 4.5b · Dev Record | **the door** |
| 7 · land the story on the epic branch | **the door** |
| 8 · prune worktree and branches | **the door**, delegating to the utility |

## 4. The defect this kills

In `cicd-update-sprint-memory.md`: the Jira transition to Done is at `:161`; the landing push is at
`:258`. Three STOPs sit between them — a merge conflict at `:246`, a red gate at `:254`, a rejected
push at `:269`.

A Jira transition is a remote write and rides no branch. A stopped landing therefore leaves the code
on one disk under a ticket that reads Done. The file's own defence — that board edits ride the branch
— does not reach `:161`, because that write is not a file edit.

Moving the ticket write into the door, after the push returns 0, matches the other family exactly.

⛔ Do not patch this separately. The restructure makes it impossible; a separate patch would be dead
code.

## 5. DO

1. Rename `cicd-close-workingtree` → `cicd-prune-worktree` first. Smallest blast radius, and the
   door's new body can then reference the final name.
2. Rename `cicd-update-sprint-memory` → `cicd-close-story-merge-tree`, keeping its Steps 4.5a, 4.5b,
   7 and 8 — it already holds the landing and ticket logic, so renaming preserves it.
3. Relocate the Done transition to after the landing push returns 0.
4. Carve Steps 1–6 back out into a slimmed `cicd-update-sprint-memory`, standalone-invocable. The
   door invokes it as a step.
5. Give the utility a prune-only entry point for the multi-lane landing command.
6. Apply the nine findings in § 9 as part of the rewrite, not as a second pass.
7. Re-point every caller. Grep, then hand-check each hit to confirm it should change.
8. Rewrite the SOP section that describes the close-out altitudes, including both diagrams.
9. Extend the existing retired-doors test so the old names cannot return.
10. Run the agent sync once at the end, then verify all four platform doors resolve for all three names.

## 6. DO NOT

- **Do not use `jira_feed.py finish` in the story door.** Its merge check hardcodes `origin/main`:
  it fetches `origin main` and asks whether the tip is an ancestor of it. A story lane lands on
  `epic/<KEY>-<slug>`, so the tip is not an ancestor until the epic ships — the call would return
  "held" forever while the story status file already reads done. That is a two-surface divergence.
  The door keeps its existing transition call. Teaching that script a landing-target argument is a
  separate follow-on that would let both families share one close-out engine.
- **Do not break the multi-lane landing command.** It calls the utility once per lane for pruning
  only. Without a prune-only path it will either double-land or fail.
- **Do not rewrite anything under `_artifacts/`.** Those are session records; rewriting them
  falsifies history. References to the old names inside them stay.
- **Do not hand-edit generated surfaces** — the platform command mirrors, workflow copies, generated
  skills, the sync manifest, or the doc graph. One sync run regenerates all of them.
- **Do not let either story close-out touch `main`.** They land on the epic branch and stop.
  Production remains a separate, explicitly gated act.
- **Do not absorb the production-door findings.** Four findings about that command were mis-routed
  here and moved to their own ticket. Leave them there.

## 7. Cost — measured

|  | total files | `_artifacts/` history | generated | real hand-edits |
|---|---|---|---|---|
| `cicd-update-sprint-memory` | 102 | 22 | 34 | **46** |
| `cicd-close-workingtree` | 32 | 8 | 10 | **14** |

Roughly 60 real edits, and 47 of them are in the single SOP file that has to be rewritten anyway,
because the altitude table it contains is the design that changes. The remainder is about a dozen
files at three to seven one-line references each, plus four script and test touches.

Renaming is mechanical: grep, then confirm each hit by hand. It is not the risk in this ticket.

## 8. Success and failure

**Success looks like**

- Three commands under their new names; no file outside `_artifacts/` references a retired name.
- The Done transition happens only after the landing push returns 0.
- The slimmed sprint-memory command performs no landing, no ticket write, and no prune.
- The multi-lane landing command still prunes per lane.
- All four platform doors resolve for all three names after one sync.
- The SOP describes the new altitudes and no longer claims the utility is rarely typed by hand.

**Failure looks like**

- A landing fails, and the board still reads Done — the exact defect this ticket exists to remove,
  reintroduced because the transition was left ahead of the push.
- The story door adopts the task-lane close-out machinery, and every story close-out is held forever
  because the merge check is looking at the wrong branch.
- The multi-lane command silently stops pruning, and worktrees accumulate until a later lane fails
  to create one.
- A retired name survives in a rule or command, and an agent invokes a door that no longer exists.

## 9. The nine findings to apply during the rewrite

All nine were re-measured against the tree and then passed a disposition test — is the failure real,
does fixing it change behaviour, is it in scope. This group had no rejections.

### CO-01 — HIGH

The cicd story close-out writes `Done` with a hand-written `acli jira workitem transition` (cicd-update-sprint-memory.md:160-161) - the exact fallback smh:591-592 bans - instead of `jira_feed.py finish`, so an open `- [ ]` row under `## Your Actions` cannot hold the ticket.

**Failure:** A story walkthrough carries an open `- [ ]` ('operator must rotate the key'). :161 writes `Done` unconditionally; `jira_feed.py finish` would have exited 3, posted the open items as a 'User tasks' comment and added the `user-tasks` label. The owed item dies with the lane while the board reads Done.

**Edit:** cicd-update-sprint-memory.md:160-161 - the `done -> Done` half becomes `python3 .agents/scripts/jira_feed.py finish --key <KEY> --walkthrough <the walkthrough> --apply`; port smh:577-582's four-row exit table (0 closed / 3 HELD 'landed and awaiting you' / 2 fix the artifact / 4 transport, retry) and smh:591-592's ban on the hand-written fallback. The `review -> In Review` half stays as acli.

### CO-02 — MEDIUM

cicd-code-review.md:366-372 tells the story agent that `jira_feed.py` refuses a close-out on a banned or ceremony action row 'at check-actions and again at finish', but neither cicd-update-sprint-memory.md nor cicd-close-workingtree.md ever calls either subcommand - the cicd family claims a refusal that no step on its close-out path performs.

**Failure:** A story walkthrough's `## Your Actions` carries 'click Merge on the PR' or a row assigning the operator ticket work; the close-out runs end to end and lands, and the refusal the review step promised never fires - the fix is now a post-landing commit instead of a free pre-landing edit.

**Edit:** cicd-update-sprint-memory.md, head of Step 7 before :244's commit: `python3 .agents/scripts/jira_feed.py check-actions --walkthrough <the walkthrough> || { echo 'fix `## Your Actions` BEFORE the landing'; exit 1; }`, citing SCC-163/SCC-193 as smh:358-365 does. Run it once over the project's existing story walkthroughs and record the hit count in the ticket before arming the STOP - the zero-false-positive corpus (jira_feed.py:2786-2796) was 145 TRACKED lobby walkthroughs and Projects/ is gitignored.

### CO-03 — HIGH

cicd-update-sprint-memory writes the ticket to `Done` at :161, ~100 lines and three STOPs before the landing push at :258, inverting smh:454-458's rule that the ticket moves AFTER the code lands.

**Failure:** The merge gate at :252-254 goes red -> 'STOP: no push, nothing lands'. The ticket already reads Done. The file's own defence at :254 ('the board/status flips from Steps 1-6 ride this branch, so a stopped landing publishes nothing') does not reach :161: an acli transition is a remote write that rides nothing - and since :260-264 forbids pushing the `claude/*` branch, the code is left on one disk under a Done ticket.

**Edit:** move only the `--status "Done"` transition out of Step 4.5a (:160-161) to immediately after :258's landing push returns 0, before Step 8's prune, carrying smh:456's one-line rationale. Leave 4.5b (Dev Record) and 4.5c (check) where they are - :191-192 feeds 4.5c's output into the Step 6 summary. The `review -> In Review` half of :160 stays put; it certifies no landing.

### CO-04 — HIGH

cicd-update-sprint-memory.md:46-47 brackets `[--branch <name>]` as optional and Step 0.6 (:40-58) never reads the target the preflight echoed - breaching worktree-per-story.md:165-175, the one rule this file declares in force at :9, while its cicd sibling cicd-close-workingtree.md:27,30-35 complies.

**Failure:** A sibling lane moved the shared checkout. closeout_preflight.py resolves the repo by walking up from cwd (:364) and guesses branches from ids and worktrees (:43-67), so it reports landed/sync/worktrees honestly about the WRONG lane and prints 'clear to close out' - the 2026-08-09 shape, with nothing in Step 0.6 to catch it.

**Edit:** cicd-update-sprint-memory.md:47 - unbracket `--branch <name>` (and `--worktree <path>`); add cicd-close-workingtree.md:30-35's sentence to Step 0.6: check the target the script echoes BEFORE reading its verdict, resolved story/branch != the one Step 0 echoed -> STOP.

### CO-05 — MEDIUM

closeout_preflight.py has no intent argument at all: given an explicit `--branch` it returns `[explicit]` (:43-51) and checks it without ever comparing it to the lane the caller named - the check task_preflight.py:1452 made mechanical (`--expect-key`, required=True) after the 2026-08-09 failure.

**Failure:** `closeout_preflight.py --story 4.2 --project AGY --fetch --branch claude/AVCH-91-sibling` reports landed/sync/worktrees for the sibling's branch and prints `VERDICT: clear to close out`, exit 0. worktree-per-story.md:155-160 states why prose cannot catch this ('it runs every check honestly and reports a clean result about the wrong branch'), and prose is exactly what failed on 2026-08-09.

**Edit:** .agents/scripts/closeout_preflight.py:354-361 - add `--expect-key`; in check_landed compare the key segment of each resolved branch (`^[a-z]+/([A-Z][A-Z0-9]*-\d+)-`) against it, mismatch -> `rep.err` (exit 2), no key segment at all (pre-Jira branch) -> `rep.warn`. Pass it from cicd-close-workingtree.md:27 and cicd-update-sprint-memory.md:46. Make it `required=True` only in the same commit that updates both callers.

### CO-08 — MEDIUM

cicd-update-sprint-memory.md:191 runs `jira_feed.py check --key <KEY> --story <id>`, and the scoped branch (jira_feed.py:2584-2607) returns before the duplicate and FORK arms (:2617-2669) ever run - so the SCC-174 fork is structurally invisible to the cicd close-out, and `--story` is the very flag whose slug forks the record.

**Failure:** A story ticket carries ONE lane's Dev Record filed under two slugs. The cicd close-out's scoped check finds the record matching this lane's id, prints 'one Dev Record', exits 0, and the fork ships - while smh:531's unscoped run would have reported 'FORKED Dev Record' with the remedy.

**Edit:** cicd-update-sprint-memory.md:191 - keep the scoped run and add an unscoped second one, `python3 .agents/scripts/jira_feed.py check --key <KEY> --project <PROJECT>`, plus one line carrying smh:546-552's remedy (delete the record filed under the slug that is not a lane, re-post with the manifest's/branch's slug) and the ban: never `--append-new` past it.

### CO-09 — MEDIUM

cicd-update-sprint-memory.md:229 states the sign-off with no spend clause anywhere in the file, so the invocation sits in the agent's context and still reads as valid on a second story's landing later in the same session - SCC-71 exactly, with git-policy.md:72-73's 'per-action and never carries forward' never restated in the command body.

**Failure:** Story A's close-out is invoked and lands. Later in the same session story B reaches its landing; the agent reads :229 as standing authority, pushes to the epic branch, and no line in the file refuses it - the guard at :232-235 only fires when sibling worktrees are ALREADY live and routes to /cicd-merge-epic-workingtrees.

**Edit:** append one sentence to cicd-update-sprint-memory.md:229: this sign-off covers THIS story's landing and is spent by it - a second story needs its own invocation, and a landing offered on the strength of an earlier one is refused (git-policy.md:72-73, SCC-71).

### CO-06 — MEDIUM

closeout_preflight.py's `--fetch` is opt-in with no `--no-fetch`, and the unfetched path emits an INFO that leaves the exit code clean and the verdict line carrying no freshness state at all - task_preflight.py defaults it on and puts STALE in the verdict itself.

**Failure:** `closeout_preflight.py --story <id> --project <p>` with the flag omitted prints `sync: no --fetch, ahead/behind is vs the LAST fetch` as an INFO (:110-111), rep.exit_code() stays 0, and :396-398 prints `clear to close out` - a pass computed against yesterday's remote, in the only line an agent acts on.

**Edit:** closeout_preflight.py:360 -> `action=argparse.BooleanOptionalAction, default=True`; return a `fresh` flag out of check_sync (:101-111), warn rather than info on the no-fetch path; give the verdict at :396-398 a third state - errors -> BLOCKED, not fresh -> 'clear - but vs the LAST fetch (STALE); re-run without --no-fetch' with a non-zero exit. task_preflight.py:1463-1465 and :1519-1534 are the shape to copy.

### CO-07 — MEDIUM

closeout_preflight.py:124-127 folds every dirty path into one undifferentiated 'N uncommitted change(s) - commit before closing out', where task_preflight.py:926,955-961 splits `_artifacts/_memory/` out as its own class with the ruling attached (park or leave another session's memory - never sweep, delete, or commit it under this lane).

**Failure:** Another session leaves `_artifacts/_memory/x.md` dirty. The preflight blocks at exit 2 saying 'commit before closing out'; cicd-update-sprint-memory.md:244-245 lists `artifacts` among the paths to commit, and `_artifacts/_memory/` is under it - so the agent clears the block by committing another session's memory under this story's key, the exact act task_preflight names and forbids.

**Edit:** closeout_preflight.py:124-127 - filter `_artifacts/_memory/` lines out of the generic count and give them their own `rep.err` carrying task_preflight.py:955-961's ruling text. Both classes stay `rep.err`, so no exit code moves; only the reporting splits.

## 10. Acceptance → the assertion that proves it

| # | Acceptance | Assertion (must fail first) |
|---|---|---|
| 1 | The three commands exist under their new names | no file outside `_artifacts/` references a retired name |
| 2 | Retired names cannot return | a test fails if either old name reappears as a door, proven by mutation |
| 3 | The board cannot lie | the Done transition's line number is greater than the landing push's — fails against today's ordering |
| 4 | Multi-lane still prunes | the prune-only path is exercised |
| 5 | sprint-memory is genuinely slimmed | it performs no landing, no ticket write, no prune |
| 6 | Every door resolves | all four platform surfaces present for all three names after one sync |
| 7 | The SOP tells the truth | the altitude section matches the new design |

## 11. RED first

Nothing is edited until something fails. Start with acceptance #3 — assert the Done write comes after
the landing push, and watch it fail against today's file. Then #1, #5 and #7 as greps returning the
wrong count now.

Paste the actual failing output and read which line raised it. A check that dies in setup looks
identical to one that fails its assertion, and only one of those is a real failure.

Assertions must run on both machines: one has no bare `python`, the other has no `python3`. Write
them interpreter-neutral or provide both forms.

## 12. Relationship to the other live tickets

- The twin-parity guard ticket builds a check whose pair list names command files. Landing this
  ticket first means that list is written against final names once. If this lands after, updating the
  pair list belongs to this ticket's diff — a grep and replace, not rework.
- The `_AP` ticket should land first regardless: its gate fires the moment any cicd command is
  committed without its abandoned twin.
- The production-door ticket and the 84 content ports are separate. Do not absorb either.
