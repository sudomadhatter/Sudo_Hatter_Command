---
description: Review + gate TASK work — re-derives the blast radius against current main (Step 0.7, because sibling lanes land while you build), then a clean-room adversarial review of the diff, an acceptance audit against the task's checkable list, the command-centre gate (enforcement suite + assertion evidence + link/anchor + SOP currency + door parity) and /smh-clean-code-audit, producing a PASS/CONCERNS/FAIL/WAIVED verdict in the task walkthrough. The smh- counterpart of /cicd-code-review, for work with no story, no board and no epic branch. Use when the user says "review this task" / "smh code review".
platforms: [opencode, antigravity, claude, codex]
---

# /smh-code-review — Review + Gate for Task Work

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push
>   `main`, never force-push
> - `.agents/rules/worktree-per-story.md` §"cwd is not intent" — the diff and the artifacts are pinned
>   from command output; with sibling `chore/*` lanes live, a lookalike file in the shared checkout is
>   another lane's, not evidence
> - `.agents/rules/artifacts-always-first.md` §6 — the verdict is a **section appended to the task
>   walkthrough**, never a standalone review file
> - `.agents/rules/tests-must-gate-for-real.md` — an empty diff, a missing tool and a piped exit code
>   are the three ways this gate goes vacuously green

Thin orchestrator. Runs the adversarial review, the acceptance audit, the command-centre gate and the
clean-code gate, then appends ONE `## Code Review (<date>)` section to the task's `walkthrough.md` —
the section `/smh-close-task-merge-tree` reads before it will merge anything.

> Flow position: `/smh-quick-dev` → **`/smh-code-review`** → **[STOP]** → `/smh-close-task-merge-tree`.

**Why this is not `/cicd-code-review`.** That command binds `smh-target-resolution.md` (*"exactly ONE
project, never the lobby"*), reads `_bmad-output/sudo-tests.yaml` for its opt-in, inherits a
`certification-<story>.json` from ② Step 4.5, runs `bmad-testarch-trace`/`nfr`/`test-review` against a
coverage floor, and writes into `_artifacts/epic_<E>/<story>/`. **None of that exists for a Task**, and
its evidence tool `gate_receipt.py` resolves a BMAD project and **exits with an error in the command
centre** — there is no board file for it to find. This is the same review discipline rebuilt on the
evidence a Task actually has. Both commands exist on purpose; the prefix carries the permission.

---

## Step 0 — Resolve the repo and the lane (FIRST) — from command output, never from belief

The subject is **where you are standing**. If `$ARGUMENTS` names a folder under `Projects/` or a path,
use that; otherwise the current repo. Do **not** read `.agents/active-project.txt`.

```bash
git worktree list                                     # find THIS task's tree
REPO=$(cd "<the tree you resolved>" && git rev-parse --show-toplevel)
BRANCH=$(git -C "$REPO" rev-parse --abbrev-ref HEAD)
HEAD_SHA=$(git -C "$REPO" rev-parse HEAD)
echo "Reviewing: $(basename "$REPO") | $BRANCH @ ${HEAD_SHA:0:8}"
```

⛔ **Echo that from the commands.** A self-reported echo can only confirm a wrong belief, and with
sibling lanes live the shared checkout is the wrong tree more often than not.

The task's `implementation_plan.md`, `walkthrough.md` and `task.yaml` live in **this tree**, under
`_artifacts/_main/<YYYY-MM-DD>_<slug>/`. **Absent here means that step never ran** — a lookalike folder
in the shared checkout belongs to another lane and is not evidence.

## Step 0.5 — Resolve the diff

```bash
env -u GITHUB_TOKEN git -C "$REPO" fetch origin main  # a bare `main` is this checkout's LAST PULL
git -C "$REPO" diff --name-only origin/main...HEAD    # the task's committed work
git -C "$REPO" status --short                         # anything uncommitted (report it; it is not reviewed)
```

Echo the file count. **An empty set is a STOP, not a pass.**

Dirty files under `_artifacts/_memory/` are **named separately and left alone** — another session's
memory is never swept, deleted, or committed under this task.

## Step 0.7 — ⭐ Re-derive the blast radius against **current** `main` (MANDATORY)

**The pre-work audit expires.** `/smh-self-audit` traced this work's blast radius against the `main`
that existed when the plan was written. On a Task lane, sibling `chore/*` branches land while you
build, so by the time you get here that trace can describe a repo that no longer exists. **Every gate
in Step 3 can be green while a landed lane has moved a file this work depends on** — a green suite
proves your code runs, not that your references still resolve.

That is not hypothetical: on SCC-78 a sibling lane relocated the SOP PRD mid-task, and two commands in
the diff still named its old path as the standard they load. The full floor was green before and after.
Only this re-derivation caught it, which is why it is a step and not advice.

```bash
env -u GITHUB_TOKEN git -C "$REPO" fetch origin main
BASE=$(git -C "$REPO" merge-base HEAD origin/main)
git -C "$REPO" diff --name-only "$BASE"..origin/main | sort > /tmp/theirs.txt  # what landed while you built
git -C "$REPO" diff --name-only origin/main...HEAD   | sort > /tmp/mine.txt    # what you changed
grep -Fxf /tmp/mine.txt /tmp/theirs.txt                                        # the TRUE overlap
git -C "$REPO" merge-tree --write-tree --messages HEAD origin/main | head -40  # conflicts, before they are real
git -C "$REPO" worktree list                                                   # sibling lanes still live
```

⚠ **`zsh` does not word-split an unquoted variable** the way `bash` does. Build file lists into a file
and expand with `$(cat …)`, or the whole list arrives as one argument and your sweep silently checks
nothing — a vacuous green in the tool you brought to prevent vacuous greens.

Then answer these three, in writing:

1. **Did anything this diff REFERENCES move, get renamed, or get deleted on `main`?** Re-resolve every
   repo path and `#L` anchor the diff names — especially the ones a command or rule loads as its
   *standard*, its *rule pointer*, or its *script*. A reference that a landed lane moved out from
   under you is a **FAIL**, not a nit: the command still reads correctly and instructs the agent to
   open a file that is not there.
2. **What is the true overlap, and does the merge conflict?** Report the intersection and the
   `merge-tree` result. A conflict in a **generated** file (a sync manifest, a mirror, an INDEX the
   tooling writes) is resolved by **regenerating it**, never by hand-merging.
3. **Which sibling lanes are still live, and does one of them need to land first?** Name the
   landing-order dependency and what happens to this work if the order is reversed.

**Absorb `main` now, before the verdict** — conflicts belong on this branch, never on `main`
(`git-policy`). Re-run Step 3's floor **after** absorbing; a verdict measured on a pre-merge sha is a
verdict about code that will never exist.

> This step is the post-dev half of `/smh-self-audit`, deliberately placed **here** rather than offered
> as a second invocation of that command. An opt-in re-audit is one nobody runs — the memory audit sat
> unused inside `/smh-update-maps-indexes` for exactly that reason. See that command's
> **§ Running it after the work is built** for which phases go stale and which do not.

## Step 0.9 — ⭐ Probe the review runtime and RECORD it (before the engine, SCC-177)

**Can this session fan out to subagents?** Answer it from this runtime, not from what usually
happens: a headless pipeline or a platform without a subagent tool makes the answer `inline`, and
both are invisible until a lens fails to launch.

⛔ **The question is a **capability**, never a **policy** — and conflating the two silently gutted a
review on SCC-197 (SCC-203).** *Does a subagent tool exist in this runtime?* is the whole question.
*Am I permitted to use it right now?* is a different one, and answering it here is how a session
directive — *"do not spawn subagents unless the user asks"* — got read as *"this runtime is
inline"*. The entire review then ran in the builder's own context and the flow recorded it as a
legitimate outcome. The operator caught it by reading the chat; nothing in the system would have.

⭐ **Subagents are the DEFAULT, and invoking this command **IS** that request.** A review needs
clean-context lenses to be worth running, so the ask is built into the workflow rather than left to
the operator to remember. Where a directive gates subagent use on being asked, this step is the
asking — you do not stop and put the question to the operator, and you never quietly downgrade to
`inline` to avoid it. **Only a runtime with no subagent tool at all is `inline`.**

And if you are `inline` while holding this lane's plan and walkthrough, the engine **drops** the
Blind Hunter rather than faking it — see step-01 § *When the order CANNOT protect it*. A roster is
not allowed to claim a review was more independent than it was.

Write the answer into the walkthrough header, **above `## Code Review`**, exactly like this:

```
review-runtime: fan-out
```

⛔ **`inline` is a different review, not a slower one — which is why it is declared before the hunt
rather than discovered during it.** Under `inline` the engine runs the ladder ONCE, blind lens first
on the diff alone, and every lens comes back `recovered-inline`; a roster reporting `ok` under an
`inline` header is a contradiction that `walkthrough_roster.py` blocks on. Declaring it afterwards,
from the roster you already have, makes the check circular and buys nothing.

---

## Step 1 — Clean-room adversarial review  *(the blind hunt — ORDERING IS DELIBERATE)*

Invoke the **`code-review-engine`** skill on the diff — the same house engine `/cicd-code-review`
runs (SCC-116), so Task work is reviewed to the story lane's standard: a parallel lens fan-out, an
evidence-verification pass over what they find, then triage. The lenses each run in their own clean
context, which is what zeroes out the builder's bias — an agent reviewing its own reasoning anchors
on it.

**Resolve every input first — the engine resolves nothing itself, and a missing required input is a
stop, not a guess:**

| Input | What you pass |
|---|---|
| `REPO` | the repo Step 0 resolved |
| `WORKTREE` | this task's tree (Step 0 pinned it from `git worktree list`) |
| `DIFF` | the `origin/main...HEAD` diff, **re-taken after Step 0.7 absorbed `origin/main`** — committed work only |
| `HEAD_SHA` | `git rev-parse HEAD` **re-read here, after that absorb** — never Step 0's value |
| `review_mode` | `full` when the task's `implementation_plan.md` exists; `no-spec` when it does not |
| `STORY_FILE` | that `implementation_plan.md` — on this lane the plan's acceptance list **is** the spec |
| `ARTIFACT_DIR` | `_artifacts/_main/<YYYY-MM-DD>_<slug>/` inside this tree |
| `lens_budget` | `standard` — the interactive budget; this lane is typed by hand. **This command does not define what the caps are; step-01 of the engine does, once** — a cap each caller repeats is a cap that drifts. Naming nothing is not neutral: it silently selects the autopilot's budget, which is why this row is explicit (SCC-147) |
| `review_runtime` | `fan-out` or `inline` — **what you PROBED at Step 0.9, never what you expect.** Pass it down and write the same value into the walkthrough header, so the roster the engine returns can be checked against the runtime that produced it |

⚠ **Step 0 read `HEAD_SHA` before Step 0.7 absorbed `main`.** Re-read both it and the diff here, or
the engine reviews a tree that no longer exists and your verdict cites a commit that is no longer the
tip — the exact invariant Step 0.7 opens by stating.

**Hunt the DIFF first. Open the plan and the walkthrough only AFTER the engine's summary comes
back** — for claimed evidence, plan-vs-built deviations, and the `## Your Actions` rows. Reading the
builder's account before the hunt imports exactly the bias this step exists to remove, which is why
the Blind Hunter is starved of context on purpose.

The lenses hunt for: logic flaws · AI drift · over-engineering · bloat · unnecessary abstraction · a
check that cannot fail · a claim in the walkthrough the diff does not support · missing test tiers ·
acceptance items the diff does not deliver.

**Then fix in thread — before Step 2, before any gate.** Every `patch` the engine hands back is
applied by you, in this lane, now; every `decision_needed` is walked with the operator now, in this
thread, and becomes a patch or a dismiss on their word — one they do not decide now stays an open
DECISION row in `## Your Actions` (Step 5; a decision is theirs and may hold the ticket, it is not a
ticket) with its `defer` bullet pointing at that row. Re-run the scoped check for what you touched
(the ONE full gate lands in Step 3, after your last change). **Nothing that survived the relevance
gate leaves this lane as future work** — not a residue ticket, not a "proposed" or "decided" ticket,
not a ticket-ruling row (operator ruling 2026-08-15, second: "we need the fixes made in thread not a
ticket made every story"). The only exception is a `defer` naming one structural blocker (another
live lane owns the file · another repo · an open decision), written to `_artifacts/_main/deferred-work.md`.

**The engine returns a `severity_floor`, and it BINDS Step 4.** `none` < `CONCERNS` < `FAIL`: this
command's verdict may be the floor or anything more severe — Step 3's gates add their own reasons —
never anything less.

**Degradation is reported, never silent.** The engine owns the per-lens failure contract (retry once,
re-run inline, and only a lens still dead after both raises the floor) and hands back each lens as
`ok | recovered-inline | dead`, plus any lens that was `n/a` for the mode. **Copy that line into the
verdict as it came back:** "4 lenses ran" and "3 ran plus 1 rerun inline" are different evidence. A
lens skipped by mode is not a degradation; a lens that never ran is an unexamined surface, and an
unknown is not a pass.

⛔ **Copy means COPY — the `lenses_run:` block goes into Step 4 verbatim, rows and all.** It is the
only evidence that survives this chat, and `walkthrough_roster.py` reads it at close-out. Summarising
it back to a sentence ("all lenses clean") deletes the evidence and leaves the `Verdict:` line
asserting its own result, which is the defect SCC-173 exists to close.

## Step 2 — Acceptance audit  *(against the checkable list, not against the code)*

Recover the task's acceptance list — `/smh-quick-dev` Step 1 echoed it, the plan carries it, and the
ticket's own `ACCEPTANCE` block is the authority behind both (`acli jira workitem view <KEY>`).

**No double audit.** In `full` mode the engine's Acceptance Auditor lens already walked the diff
against that plan — **import its findings** into the matrix below (source `review`) rather than
re-deriving them. What stays yours is the matrix itself: every item paired with the assertion that
proves it, which is a claim about evidence a lens cannot make for you.

For **each item**: name where the diff satisfies it, and **the assertion that proves it**. Then the
other direction — **anything in the diff beyond the list is drift**: cut it, or name why it stays.

- An item with **no evidence** is not satisfied, however obviously true it looks. **CONCERNS floor.**
- An item whose evidence is *"I read it and it looks right"* is not evidence. Run something.
- No acceptance list recoverable anywhere → say so and cap the verdict at **CONCERNS**; a review with
  no contract to review against is an opinion.

## Step 3 — The command-centre gate

**Paste actual output for every row. Run gates bare** — piping to `tail`/`head` returns the *pipe's*
exit code, which is how a red gate reads as green.

| Gate | Command | When |
|---|---|---|
| **Enforcement suite** | `python3 .agents/scripts/tests/run_all.py` | **always** — N/N files, exit 0 |
| **Toolkit lint** | `python3 .agents/scripts/workflow_lint.py --toolkit-only` | **always** — errors FAIL, warnings are CONCERNS |
| **Assertion evidence** | re-run the task's own Step 2 RED assertions — `--case "<label>"` where the suite declares blocks, so this row cites the NAMED cases rather than a whole file | **always** — they must be GREEN now |
| **SOP currency** | `python3 .agents/scripts/sop_currency.py --paths <changed> --message "<subject>"` | a usage surface is in the diff |
| **Link + anchor** | resolve every path and `#L` anchor the diff touched | any `.md` in the diff |
| **Door parity** | every added/renamed command has exactly the doors its `platforms:` claims | a command was added, renamed or deleted |

**Receipts ride this lane too (SCC-146).** `/smh-quick-dev` Step 3 stamps the suite run at
`_artifacts/_main/<date>_<slug>/gates/` via `gate_receipt.py run --task <KEY> --gate suite --root
<task-artifacts> --cwd <worktree>`. Inherit it the way `/cicd-code-review` inherits a certification:
**receipt result `pass` or `warn` (advisory findings — read them before adopting; the preflight
accepts both, SCC-154) + stamped on a clean tree + no non-artifact file changed between its sha and
HEAD → adopt it, cite the receipt, do not re-run the suite.** Anything else — no receipt, a `fail`
or `DIRTY` stamp, code, test or doc changes since — **run it yourself and re-stamp** with the same
command. Port the rule verbatim: **fail toward running, never toward trusting.**

⛔ **An absorb does NOT automatically invalidate the receipt — freshness is a TREE comparison, not a
sha comparison.** Step 0.7 moves HEAD, and it is tempting to conclude the inherited receipt died with
it; it did not. `gate_receipt.check_receipt` asks `wf.same_tree(repo, sha, target)` — literally
`git diff --quiet <sha> <HEAD>` — so a merge commit whose tree is identical to the stamped one
(a no-op absorb, or one that only moved `_artifacts/`) leaves the receipt **valid**, and re-running
the suite there buys a second copy of an answer you already have. What invalidates it is a
**content** change outside `_artifacts/`, whoever authored it.

**Run the suite ONCE, on the code that will actually land — ONE re-stamp, after the LAST
code-touching change.** While fixing, run scoped — the tests for what you touched, and where the
suite file declares blocks, `--case "<label>"` runs just those (exit 3 = the label matched nothing,
which is a mistyped command, not a result). **After your LAST change**, run `run_all.py` in full
**through the receipt writer** and paste it, with the sha. Artifact-only commits after that run do
**not** invalidate it, and neither does a no-op or artifacts-only absorb (same tree ⇒ same
receipt); code,
test **or doc** changes do — only `_artifacts/` is exempt, and a `docs/` commit invalidates
(SCC-154; the old "doc-only" wording overstated the exemption and was disproven live when a docs
commit staled a receipt mid-review). The receipt's freshness check reads exactly that rule,
mechanically (`task_preflight.py` § code-fresh). The evidence contract is unchanged: **pasted real output, plus
`git rev-parse HEAD` recorded beside it**, in the walkthrough's `## Evidence` — the receipt is how
the close-out *verifies* the claim, never a substitute for the pasted run.

**Guards, per `tests-must-gate-for-real`:**
- **A missing tool is a finding, not a skip.** `run_all.py` failing to start means the floor is
  unrunnable — report it and name the fix.
- **A check that cannot fail is a finding.** If the diff adds a gate, prove it **rejects** the case it
  must reject *and* **allows** the case it must allow. One half is not a gate.
- **A red that asserts strings or paths absent from real source is fiction**, not legacy debt. Do not
  grandfather it — FAIL and fix or delete it.

## Step 3.5 — Gate: clean code (ALWAYS runs)

**Invoke `/smh-clean-code-audit`**, bound to the same worktree Step 0 resolved. Its standards are
`docs/_scc_sops_prds/workflows_testing_SOP.md` (the command centre's own) and
`.agents/rules/code-standards.md` (for real code).

- **No double drift-hunt.** Step 1 already walked these hunks — run the machine floor and the comment
  contract (§2A) plus the convention table (§2C), and **import Step 1's drift/bloat findings** into the
  table (source `review`) instead of re-running the §2B ban-hunt. The full two-half pass is for
  standalone runs.
- **No double machine floor either (SCC-146).** Nested here, the audit **imports Step 3's receipts
  and pasted runs** for `run_all`, `workflow_lint`, `sop_currency` and the link+anchor sweep instead
  of re-running them, and runs only what Step 3 did not: `py_compile`, the comment contract (§2A),
  the convention table (§2C). A missing or invalid receipt means Step 3 owes a run — send it back,
  don't paper over it here. Standalone `/smh-clean-code-audit` is unchanged.
- **Diff-scoped.** Legacy debt in untouched files is noted, never gated on.
- **An empty diff is a STOP, not a pass.**

Fold its findings table into the verdict section **verbatim**, with the actual output pasted. Apply the
fixes you can make safely, then re-run the affected check and paste the new output.

---

## Step 4 — Verdict (append to the walkthrough — NO separate file)

Append a `## Code Review (<date>)` section to `_artifacts/_main/<YYYY-MM-DD>_<slug>/walkthrough.md`
**inside the worktree Step 0 resolved** — it rides the branch through the merge. Never mint a
standalone review file (`artifacts-always-first` §6).

The section carries:

- **FIRST line, canonical** — this is what `/smh-close-task-merge-tree` reads:

  ```
  Verdict: PASS|CONCERNS|FAIL|WAIVED @ <HEAD-sha>
  ```

  plus one line naming the sha the suite evidence was measured on.
- ⛔ **the engine's `lenses_run:` block, pasted VERBATIM** — the header line, then one
  `- <lens> · ok | recovered-inline | dead` row per lens, a `—` note on every row that is not `ok`:

  ```
  lenses_run:
  - blind-hunter · ok
  - edge-case-hunter · recovered-inline — fan-out returned nothing, rerun inline
  ```

  **A `Verdict:` is the review's conclusion; this block is what shows the review happened.** Without
  it the verdict is the only record of itself, and a walkthrough with zero lenses run merges clean —
  the defect SCC-173 was raised on. `walkthrough_roster.py` reads it here and
  `/smh-close-task-merge-tree` blocks a lane that does not carry it. Do not summarise it, do not
  re-order the rows into prose, and never write a state a lens did not report.
- scope + method, one line each;
- **ONE findings table** — `file:line` · severity · failure scenario · disposition
  (`applied @ <sha>` / `deferred — blocked by <other live lane | other repo | open decision>` /
  `dismissed` — a relevance kill carries its one-line reason; pure noise is count-only). **The
  authoritative copy**; the plan links here, never restates.
  (In `full` mode the engine may also leave `[ ] [Review]…` action items in the file you passed as
  `STORY_FILE` — a worklist carrying no dispositions, never a second record. This table wins.)
- each gate's result in one line with its **actual** output;
- the acceptance matrix from Step 2 — every item → its proving assertion;
- a `### Clean-Code Gate` subsection carrying Step 3.5's table and pasted output;
- **Step 0.7's re-derivation**, in three lines — what `main` moved under this diff, the true overlap +
  `merge-tree` result, and any **sibling-lane landing-order dependency**. "Nothing moved" is a
  reportable result; silence is not.

**Verdict rules:**

- **FAIL** — the enforcement suite is red · a `workflow_lint --toolkit-only` **error** · an acceptance
  item the diff does not deliver · a dead link the diff introduced · **a reference this diff depends on
  that a landed lane moved, renamed or deleted (Step 0.7)** · a door-parity break · a committed
  secret · a banned pattern shipped · a gate that cannot fail · a deployable path in the diff (which is
  also an immediate handoff to `/cicd-push-e2e`).
- **CONCERNS** — soft issues only: `workflow_lint` warnings · comment-contract gaps · bloat,
  duplication, an unowned TODO · a review layer that never ran · an acceptance item with no evidence ·
  no acceptance list recoverable.
- **PASS** — every gate green on the changed set, every acceptance item evidenced, nothing above noise.
- **WAIVED** — the repo has **no enforcement suite at all** (`run_all.py` absent). Rare, and it does
  not waive Step 3.5: report the clean-code result inside the waiver.

> The split is deliberate: objective things block, taste does not. Taste gets recorded, argued, and
> fixed on its merits — never used to stall work on a reviewer's preference.

## Step 5 — Refresh the walkthrough body + clear `## Your Actions` (REQUIRED)

The walkthrough is the living source of truth, and the body around your section must not go stale:

- **If you changed anything:** refresh what your fixes staled — the `## Evidence` matrix, the pasted
  totals (**REPLACE** them with your final run + sha), and tick the `## Task Checklist` rows your fixes
  completed, with an indented finding bullet under the task it belongs to.
- **If you changed nothing:** say so in the Step 4 section — *"Changes applied: none — implementation
  correct as-is."*
- **`## Your Actions` triage:** attempt every agent-solvable row yourself — a deferred check, a missing
  artifact link, a doc fix — and tick it with a one-line note. Leave ONLY genuine operator calls (a
  product decision, or a ticket transition they have reserved).
  ⛔ **And NEVER the ceremony's own steps** (SCC-193). "Click Merge on the PR", "then re-invoke
  `/smh-close-task-merge-tree --after-merge <KEY>`", "run the preflight" — the operator's
  **decision to proceed** is the sign-off (the word `approved`, or invoking one of the two doors),
  and from that word on every step is the ceremony's and the agent runs it. `jira_feed.py`
  **refuses** a close-out on such a row, at `check-actions` and again at `finish`. The one
  merge-shaped row that belongs is the door's ledger line, `- [x] The merge itself — lands via
  this branch's PR`, which SCC-175 checks against ancestry rather than against its tick.
  ⛔ A row assigning the operator ANY ticket born from review findings — a residue ticket ("One
  follow-on ticket for the N deferred items"), a "proposed" ticket, a "decided" ticket to rule on —
  is the retired defect (operator rulings 2026-08-15, both), never a valid action row: the
  survivors were fixed in Step 1, a `defer` names its structural blocker in the ledger, and a
  review never produces a ticket. An open box here born from a finding HOLDS the ticket on the
  review ladder forever (`jira_feed finish`) — that is the loop, not a feature.
- **Hard rule: never finish this command with the walkthrough body left stale after applying fixes.**

## Stay in lane

Commit review fixes inside the task worktree, explicit paths only, every subject leading with the
ticket key. **Never merge to `main`, never transition the ticket, never prune the branch** — that is
`/smh-close-task-merge-tree`, and invoking **it** is the operator's per-merge sign-off. One invocation
authorises exactly one merge and never carries forward. Updating the walkthrough (Steps 4–5) is IN
lane: that is documenting the review, not closing it out.

Optional additional input (a repo, a branch, or a base ref): $ARGUMENTS
