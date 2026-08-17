# SCC-197 — rolling ticket, cycle 2 (one lane, two parts)

**Lane** `chore/SCC-197-rolling-cycle2` · worktree `.claude/worktrees/SCC-197-rolling-cycle2` ·
base `origin/main` @ `5123e81` · riders **SCC-198 (Part A)** · **SCC-200 (Part B)**

Consolidated per the operator, 2026-08-17: *"we need to run do this whole ticket with
/smh-quick-dev in one working tree again"* — the SCC-190 shape, riders in `task.yaml`, one ceremony.

> **The cycle already fired.** SCC-197 moved to In Progress at lane start and its own first line
> was honoured on the spot: **SCC-201** was cloned as cycle 3, summary bumped, INDEX emptied,
> PREDECESSOR updated, read back through the rule's jql. That is the first live exercise of the
> mechanism Part A is about to put in code.

---

# Part A — SCC-198 · `cmd_start` clones the next rolling ticket and hands the baton on

## The problem, measured

SCC-190's cycle instruction lived only in its own description (`BEFORE CLOSING THIS OUT CLONE A NEW
ONE WITH NO SUB TASKS`, first line, capitals). It did not fire — the operator had to say it out
loud. Their words: *"its writen in the ticket I just dont know if you will read it."*

Both halves ship, by operator decision: the **prompt** (already live at the top of SCC-197) and the
**tag** (this part). The prompt fires because at *start* the agent must read that description — the
INDEX of subtasks to run is in it. The tag fires whether or not anyone reads anything.

## ⭐ The label is a BATON, not a property (operator ruling, 2026-08-17 — supersedes the two-tag design)

The first cut of this part put **two** labels on the rolling ticket at once: `bugs-and-updates` as
identity and `running-bug-list` as trigger, both permanent. The operator rejected it:

> *"I dont like the two tags — once you move it to In Progress we switch the tag. this avoids issues
> with the tag linked to the script cloning again too. this way it can only [clone] one. it now
> clones, it moves the original, and switches the tag to the bugs-and-updates."*

**One marker at a time, and it moves.** At any moment exactly **one** ticket on the board carries
`running-bug-list`: the next cycle's ticket, un-started. Starting it hands the baton to its own
successor and stamps the original with `bugs-and-updates`.

| Label | Meaning | How many tickets carry it |
|---|---|---|
| `running-bug-list` | *this is the next cycle, not yet started* — **the trigger** | exactly one, always |
| `bugs-and-updates` | *this is a rolling ticket that has started* — **the identity** | every cycle ever run |

**Why this is better than what I built, and it is not a matter of taste.** A permanent trigger can
fire twice, so every guard against a second clone has to *ask the board* — a jql search, a network
call, a thing that can be wrong or slow. A baton is **consumed by use**: after the swap the original
does not carry the trigger, so re-running `start` on it cannot clone, with no query and nothing to
get wrong. The guard stops being a check and becomes the shape of the data. The board search stays
in as a backstop for one specific failure (below), not as the primary defence.

⛔ **Ordering is load-bearing, and it is the operator's: clone → transition → swap.**

1. **Clone first.** `acli clone` carries labels (measured), so the successor inherits
   `running-bug-list` — that *is* the handoff. Swap first and the baton is `bugs-and-updates` by the
   time the clone copies it, and the cycle ends silently and forever.
2. **Swap only if the clone succeeded.** Same failure, other direction: stamping the original before
   a successor exists leaves **nobody** holding the baton. On a clone failure the original keeps
   `running-bug-list` — the trigger survives, the next `start` retries, and the cycle self-heals.
3. ⛔ **`--labels` REPLACES the whole set** on the real acli (already pinned by an existing case at
   `test_jira_feed.py:1591`). The swap must resend every *other* label the ticket carried, or it
   silently strips them. The labels are already in memory from the pre-transition read.

## What the two labels mean for *filing discovered work* (`work-consolidation.md` rung 3)

Rung 3 currently says: find the open rolling ticket by label `bugs-and-updates`. That still holds,
and now needs one qualifier — **`bugs-and-updates` and not Done**. The `running-bug-list` ticket is
*next month's placeholder*, not a filing target; you do not put today's discovered work in it. If no
`bugs-and-updates` ticket is open, starting the `running-bug-list` one produces one. The rule text
gets that qualifier; the lookup does not otherwise change.

## Why the START seam and not close-out

Running this ticket is exactly the window in which the system has **no open home** for discovered
work — the only open rolling ticket is the one being run. Cloning at start means cycle N+1 exists
from the lane's first minute. Cloning at close-out leaves that whole window uncovered.

## It costs nothing on the normal path, and that is measured

`view_fields()` already requests `labels` on its whitelist (`jira_feed.py:518`), and `cmd_start`
already calls it once to read the status before transitioning. **The labels are already in memory
at the moment of the transition.** The trigger is one list-membership test:

```python
if TRIGGER_LABEL in (fields.get("labels") or []):
```

- ordinary ticket → one `in` on data already fetched. No extra board call, no I/O.
- the rolling ticket, once per cycle → the three clone calls.

⛔ **`acli jira workitem view` does NOT print labels in its human table**, but `--json` returns them
(measured on SCC-197: `"labels": ["bugs-and-updates"]`). A check written against the table output
would read empty and silently never fire.

## What changes

**`.agents/scripts/jira_feed.py` — `cmd_start()` only.** After the transition to In Progress
succeeds, and only then:

1. `running-bug-list` present in the labels **already in memory**? No → return, unchanged behaviour.
   This is the whole cost on the normal path.
2. Does another open ticket already carry `running-bug-list`? Yes → **skip the clone, but still do
   the swap** (step 4). Under the baton this happens when the operator's prompt already cloned by
   hand; the successor exists, so this ticket's baton is spent either way.
3. Otherwise clone, and **rewrite nothing**. Summary and description are copied verbatim, and both
   should be: the description carries the operator's own cycle prompt, which the successor must
   inherit word for word, and a rolling ticket's summary is the same by design. An earlier draft
   said "bump the summary, rewrite the description from a file" — dropped, because it invents a
   cycle-numbering scheme nobody asked for and builds a `--description` string for no reason
   (backticks inside one execute). Not rewriting is both simpler and more correct.
4. **Swap iff a successor exists** — found at step 2 or created at step 3. One `edit --labels` call
   carrying every other label the ticket held, minus `running-bug-list`, plus `bugs-and-updates`.
5. ⛔ **Neither a clone failure nor a swap failure fails the start.** Work is never blocked because
   the successor could not be minted. Both report loudly and the lane proceeds — and a clone failure
   leaves the trigger in place so the next `start` retries.

> **The invariant, stated once, because every branch above is a consequence of it:**
> ***a rolling ticket holds `running-bug-list` until its successor exists, and not one moment
> longer.*** That is why the swap is owed even when this run did not do the cloning, and why it is
> withheld when the clone failed.

**`.agents/rules/work-consolidation.md`** — rung 3 gains the `and not Done` qualifier and one line
saying `running-bug-list` marks next cycle's placeholder, not a filing target. The label semantics
change here, so the rule that names the label changes with it or it is stale law.

## The assertions, written FIRST

`.agents/scripts/tests/test_jira_feed.py`, against the existing acli stub (which already models both
measured behaviours: `clone` carries labels, `edit --labels` replaces the set):

- fires on the tagged ticket; **does not** fire on an ordinary one (both directions).
- **the handoff itself** — the successor ends up holding `running-bug-list`, the original ends up
  holding `bugs-and-updates` and **not** the trigger.
- **the baton is spent**: a ticket carrying only `bugs-and-updates` clones nothing. This is what
  makes a second clone structurally impossible, so it is the case that matters most.
- **no extra board call** for an unlabelled ticket — counted, not asserted by eye.
- a clone failure leaves `start`'s own exit code intact **and leaves the trigger on the original**,
  so the cycle self-heals rather than ending silently.
- the original's other labels survive the swap.

---

# Part C — SCC-202 · `--labels` ADDS, and the `user-tasks` strip has never worked

**Not planned. Found by building Part A, and forced by it** — this is the honest kind of discovered
work: fixing the test stub to match reality turns an existing case red, so it cannot be deferred.

## The measurement

The stub modelled `acli jira workitem edit --labels` as **replacing** the whole label set. Measured
against the live board (SCC-197: probe label added, read back, removed, read back at every step):

| Sent | Before | After |
|---|---|---|
| `--labels zzz-probe` | `[bugs-and-updates, running-bug-list]` | `[bugs-and-updates, running-bug-list, zzz-probe]` |
| `--remove-labels zzz-probe` | `[…, zzz-probe]` | `[bugs-and-updates, running-bug-list]` |
| `--labels X --remove-labels Y` | `[bugs-and-updates, running-bug-list]` | `[bugs-and-updates]` |

**`--labels` ADDS. `--remove-labels` is a separate flag. acli honours both in one call.**

## The defect that hid behind it

`cmd_finish`'s `user-tasks` strip built the reduced set (`labels - {user-tasks}`) and sent it via
`--labels`. Against an adding API that **re-adds every label already present and removes nothing** —
exit 0, label still there. **The strip has never worked on the board.** By its own code comment, a
Done ticket still carrying `user-tasks` *"poisons the filter it exists to feed"*, and that strip was
itself an SCC-155 review finding.

⭐ **Why no test caught it:** the case asserting the strip ran against the stub that modelled a
replace. This is the rule already written in that same test file's view-whitelist comment, violated
in the other direction — *a stub more generous than the tool it stands in for cannot fail on the bug
it exists to catch.* The stub was not more generous here; it was differently wrong, which is worse,
because it made a broken writer look correct.

**It also means Part A shipped wrong for an hour.** The hand-off was written as a read-modify-write
and all 18 of its cases passed — against the lying stub. Fixing the stub reddened three of them.

## What changes

1. **`test_jira_feed.py`** — the stub models add/remove as measured, with the measurement in the
   comment. This is the change that turns the strip case red.
2. **`jira_feed.py` `cmd_finish`** — strip via `--remove-labels`.
3. **`jira_feed.py` `cmd_finish`** — the sibling ADD site sends the one label, not the union. It was
   correct only by accident, on the same false belief; leaving it makes the two halves look like
   they share a mechanism they do not.
4. **`roll_the_cycle`** — one call, `--labels <identity> --remove-labels <trigger>`.

**The red was observed, not assumed:** 331/335 with the truthful stub and the old writers — the
strip case plus three baton cases — then 335/335 with the writers fixed.

---

# Part B — SCC-200 · every artifact is handed back as a clickable link

> ⭐ **Carried over verbatim from SCC-196, plan and audit both, with the operator's `approved`
> already given on 2026-08-17.** SCC-196 was minted as a standalone Task while SCC-190 was
> mid-close and SCC-197 did not yet exist, so rung 3 had no open rolling ticket to point at; `acli`
> cannot re-parent a subtask (SCC-105), so the ticket moved and the work did not. Nothing below
> changed after approval — only its home.

## The problem, measured

The agent writes `implementation_plan.md` and `walkthrough.md` into `_artifacts/`, then refers to
them **in prose, by path**. The operator cannot open a path. On SCC-190 the whole lane ran — plan,
five review lenses, close-out, PR — and the operator still had to ask *"I can't see the artifacts
unless you give me the hyperlink in the chat."*

Two things make this worse than a formatting slip:

1. **The artifacts are the deliverable of the approval gate.** §3 of the rule says *STOP and wait
   for `approved`* — the operator is being asked to approve a document they were never handed.
2. **A worktree path is not guessable.** The file lives under
   `.claude/worktrees/<slug>/_artifacts/_main/<date>_<slug>/`, which is not where the operator is
   standing and not a path anyone types from memory.

## Why `artifacts-always-first.md` and nothing else

It is the single source of truth for **both** documents (its own `description:` says so), and every
command that writes one already binds it in its "Rules in force" block — `/smh-quick-dev`,
`/smh-quick-fix`, `/smh-plan-task`, `/smh-code-review`, `/smh-close-task-merge-tree` and the
`cicd-*` twins. Writing the obligation once there reaches all of them. Putting it in a command
instead would mean N copies that drift (`sudo-commands-have-ap-twins-that-drift`).

⛔ **Not a new rule file.** `rule-org-single-source-audit` — rules are read in place, and a second
file about artifacts is a second place to look.

## What changes

**One file: `.agents/rules/artifacts-always-first.md`.**

1. **A new `## Hand It Back` section** (after `The Lean Artifact Set`) stating the obligation: every
   artifact the agent creates or updates is reported in chat as a **markdown link relative to the
   workspace root**, at the moment it is written — never as a bare path, never only at the end.
   It names the worktree case explicitly, because that is the path the operator cannot construct.
2. **Three insertion points in `## The Sequence`**, so the obligation sits where the act happens
   rather than only in a section someone may not reach:
   - §2 (create the plan) — the link goes back with the plan.
   - §3 (STOP for `approved`) — ⛔ the approval request **carries the link**. Asking for sign-off on
     an unreadable document is the defect.
   - §5 (write `walkthrough.md`) — same, and again at close-out hand-back.

## The assertion, written FIRST

`.agents/scripts/tests/test_rules_content.py` (or the existing rules test, if one owns this file —
resolved at implementation, not assumed here) gains a block that fails when the obligation is
absent:

- **RED first**: the check fails against `origin/main`'s copy of the rule.
- It pins the **wiring, not the prose** (`prose-pinning-guards-are-vacuous`): the assertion is that
  the rule states a markdown-link obligation **and** that it appears in the approval-gate section —
  because a rule that only says it in a footer is the defect restated.
- **A negative control**: the same predicate must FIRE on a fabricated copy with the obligation
  stripped, so a broken check cannot read as a clean tree (`S5`/`U6d` class, SCC-190).

## Scope — what this does NOT do

- **No command file is edited.** They bind the rule already; editing them is the N-copies drift.
- **No change to what artifacts are written, or where.** Only how they are reported.
- **No mechanical link-checker.** Verifying a posted chat link is not something this repo can see;
  the check is that the rule *states the obligation*, which is what makes agents do it.

## Risk

Low, and bounded to one rules file plus one test block. The failure mode if I get it wrong is a
red assertion, not a broken gate. `lane_qualify` rates it `TASK` — correctly, since `.agents/rules/`
is the development system — which is why this is `/smh-quick-dev` and not the lightweight lane the
operator first suggested.

## Gates

`run_all.py` · `workflow_lint.py --toolkit-only` · `check_maps.py --depth3-only --strict` ·
SOP currency (a usage-surface change stages `docs/_scc_sops_prds/workflows_testing_SOP.md`, or
`[sop-ok]` with the reason).

---


---

## Self-Audit (2026-08-17) — the consolidated lane

**Mode:** PRE-WORK. **Right-size:** **Full** — Part A touches a script other scripts import and a
gate-adjacent seam; Part B touches a `.agents/rules/` file. Both are named in Phase 0.2.
`Repo: SCC-197-rolling-cycle2 | Branch: chore/SCC-197-rolling-cycle2` (echoed from `rev-parse`).

### Part B — the audit is CARRIED, not re-run

Its plan is byte-identical to the one audited under SCC-196 and approved by the operator on
2026-08-17. Re-auditing unchanged text would be ceremony, not a gate. Its two findings were already
folded in and both still hold on this lane:

- the assertion's home is `test_door_preflight_order.py` (no rules-content test exists;
  `test_main_ruleset_armed.py` is about GitHub's server-side ruleset), and
- `origin/main` had to be absorbed first — **now moot**: this lane was cut from `5123e81`, which
  already contains SCC-190, so the S5 block is present here from the start. *(Verified: the
  `S5 CONTROL` case is in the tree at line 468.)*

### Part A — audited here for the first time

**Phase 0 · traceability.** All seven of SCC-198's acceptance items trace to a plan step, and no
plan step traces to nothing. **Lane check:** `.agents/scripts/` + its test — no deployable path, so
`LOCAL`, closing through `/smh-close-task-merge-tree`.

**Phase 1 · blast radius.** `cmd_start` is called by `/smh-quick-fix`, `/smh-quick-dev`,
`/smh-plan-task` and **the post-commit recorder**, which is the one that matters: it fires on every
commit, so any new failure path there reaches every commit in the repo. That is why acceptance 6
(*a clone failure never fails the start*) is load-bearing rather than polite — and why the change
sits strictly **after** the transition, so nothing on the existing path can be perturbed.
`view_fields`'s whitelist is untouched; `labels` was already on it.

⛔ **FINDING 1 — the race is now CONFINED, not eliminated, and the difference is worth naming.**
Re-audited against the baton design. The common re-fire — the post-commit recorder running `start`
again on a ticket that already started — is now structurally safe: the trigger is gone, so there is
nothing to check and nothing to get wrong. What survives is genuine concurrency: two agents starting
the *same un-started* ticket in the same instant both read the trigger before either swaps, and both
clone. Accepted, not solved — the blast radius is one spare ticket versus a lock this system has no
way to hold. Recorded in the code comment so the next reader does not mistake it for an oversight.
**This is strictly better than the two-tag design it replaces**, where every re-fire, not just the
simultaneous ones, depended on the board answering correctly.

⛔ **FINDING 2 — the prompt and the tag both fire, and the fix is the invariant, not a return.**
The first draft had the tag see an open successor and *return*. That is wrong under the baton: the
prompt's manual clone inherits `running-bug-list`, so returning early leaves **two** tickets holding
a trigger that is supposed to be unique — the exact ambiguity the operator's design removes. Hence
step 2 skips only the clone and still performs the swap. The invariant is the specification; each
branch is derived from it rather than patched onto it. Pinned by its own case.

**Phase 2 · over-engineering.** No new command, no new rule file, no new mode. Part A adds one
conditional and one helper to an existing function; Part B adds a section to an existing rule. The
`TRIGGER_LABEL` is a module constant, not a flag — nothing is configurable that has one caller.
**No tripwire fires.**

**One honest limit, restated because it applies to both parts:** neither the prompt nor the tag
**detects** its own failure, and no check in this repo can see whether a link was posted in chat.
What is checkable is that the code fires and that the rule states the obligation. Recorded on
SCC-198 as the still-unbuilt board assertion; deliberately out of scope here.

### Verdict — **GO**

Part B carries its approval unchanged. Part A's two findings are both *stated constraints* rather
than plan changes: the race is accepted with its blast radius named, and the double-clone is
already prevented by the step the plan specifies.
