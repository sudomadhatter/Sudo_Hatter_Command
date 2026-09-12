---
description: Review + gate TASK work — re-derives the blast radius against current main (Step 0.7, because sibling lanes land while you build), then a clean-room adversarial review of the diff, an acceptance audit against the task's checkable list, the command-centre gate (enforcement suite + assertion evidence + link/anchor + SOP currency + door parity) and /smh-clean-code-audit, producing a PASS/CONCERNS/FAIL/WAIVED verdict in the task walkthrough. The smh- counterpart of /cicd-code-review, for work with no story, no board and no epic branch. Use when the user says "review this task" / "smh code review".
platforms: [opencode, antigravity, claude, codex, zoo]
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

> Flow position: `/smh-dev-task-tests` → **`/smh-code-review`** → **[STOP]** → `/smh-close-task-merge-tree`.

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
BRANCH=$(cd "$REPO" && git rev-parse --abbrev-ref HEAD)
HEAD_SHA=$(cd "$REPO" && git rev-parse HEAD)
echo "Reviewing: $(basename "$REPO") | $BRANCH @ ${HEAD_SHA:0:8}"
```

⛔ **Echo that from the commands.** A self-reported echo can only confirm a wrong belief, and with
sibling lanes live the shared checkout is the wrong tree more often than not.

The task's `implementation_plan.md`, `walkthrough.md` and `task.yaml` live in **this tree**, under
`_artifacts/_main/<YYYY-MM-DD>_<slug>/`. **Absent here means that step never ran** — a lookalike folder
in the shared checkout belongs to another lane and is not evidence.

## Step 0.5 — Resolve the diff

```bash
cd "$REPO" && env -u GITHUB_TOKEN git fetch origin main  # a bare `main` is this checkout's LAST PULL
cd "$REPO" && git diff --name-only origin/main...HEAD    # the task's committed work
cd "$REPO" && git status --short                         # anything uncommitted (report it; it is not reviewed)
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
cd "$REPO" && env -u GITHUB_TOKEN git fetch origin main
BASE=$(cd "$REPO" && git merge-base HEAD origin/main)
cd "$REPO" && git diff --name-only "$BASE"..origin/main | sort > /tmp/theirs.txt  # what landed while you built
cd "$REPO" && git diff --name-only origin/main...HEAD   | sort > /tmp/mine.txt    # what you changed
grep -Fxf /tmp/mine.txt /tmp/theirs.txt                                        # the TRUE overlap
cd "$REPO" && git merge-tree --write-tree --messages HEAD origin/main | head -40  # conflicts, before they are real
cd "$REPO" && git worktree list                                                   # sibling lanes still live
python3 .agents/scripts/risk_seam.py classify --repo "$REPO" $(cat /tmp/mine.txt)  # risk tiers (see below)
```

**Read the tier map beside the overlap list — and know what it can say HERE.** ⛔ **The command
centre carries no code graph at all (SCC-289): `unclassified` is the permanent, correct answer for
this repo, not a machine that has not built an index yet.** A code graph parses code; this repo is
markdown. So on a `smh-` lane this line is a one-second no-op you run for the shape, and every
judgement in this review comes from reading the diff.

`--repo "$REPO"` is still mandatory and not decoration: the flag is what makes the JSON echo
`"root"`, so the output states which tree it answered about. The same script, invoked from here with
a project worktree in `--repo`, DOES read that project's graph — which is the whole reason the flag
exists (`docs/code-review-graph.md`).

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
> **§ After the work is built** for which lenses go stale and which do not.

## Step 0.9 — ⭐ Probe the review runtime and RECORD it (before the engine, SCC-177)

**Can this session fan out to subagents?** Answer it from this runtime, not from what usually
happens: a headless pipeline or a platform without a subagent tool makes the answer `inline`, and
both are invisible until a lens fails to launch.

<!-- twin-law: subagent-probe -->
⛔ **The question is a **capability**, never a **policy** — and conflating the two silently gutted a
review on SCC-197 (SCC-203).** *Does a subagent tool exist in this runtime?* is the whole question.
*Am I permitted to use it right now?* is a different one, and answering it here is how a session
directive — *"Do not call the AgentTool unless the user requested it"* — got read as *"this
runtime is inline"*. The entire review then ran in the builder's own context and the flow recorded it as a
legitimate outcome. The operator caught it by reading the chat; nothing in the system would have.

⭐ **Answer ONE question: does a subagent tool exist in this runtime?**

- **Yes → `review-runtime: fan-out`.** Launch them. Stop reading this box.
- **No → `review-runtime: inline (no subagent tool)`.**

⛔ **Do not ask a second question.** *"Am I allowed to?"* is already answered: **the operator
invoked this command, and a `/` command IS a user request.** The standing directive *"Do not call
the AgentTool unless the user requested it"* is **satisfied here** — typing the command is the
operator asking, and this step is where that ask lands. Do not stop and put it to them again.

⛔ **If you still believe you cannot launch one, you may not record a bare `inline`.** Write the
reason on the header line: `review-runtime: inline (blocked: <quote what blocked you>)`. A bare
`inline` from a runtime that HAS the tool is a false record, and at close-out it is
indistinguishable from a runtime that never had one — which IS the SCC-203 defect. This third door
exists so an agent that believes it is forbidden has somewhere to put that belief where a reader
can see it, instead of laundering it into a clean-looking `inline`. **`walkthrough_roster.py`
READS that reason (SCC-285):** a bare `inline`, or one resting on permission rather than on
capability, is refused at close-out — this rule stopped being prose.
<!-- /twin-law -->

And if you are `inline`, every lens comes back `recovered-inline` and the roster says so — a roster
is not allowed to claim a review was more independent than it was. There is no blind lens left to
contaminate: SCC-447 closed the roster at three, so the only `n/a` it can carry is the Acceptance
Auditor's `skipped-by-mode (no-spec)`.

Write the answer into the walkthrough header, **above `## Code Review`**, exactly like this:

```
review-runtime: fan-out
```

⛔ **`inline` is a different review, not a slower one — which is why it is declared before the hunt
rather than discovered during it.** Under `inline` the engine runs the ladder ONCE — every lens
executes inline and sequentially in this context — and every lens comes back `recovered-inline`; a roster reporting `ok` under an
`inline` header is a contradiction that `walkthrough_roster.py` blocks on. Declaring it afterwards,
from the roster you already have, makes the check circular and buys nothing.

---

## Step 1 — Clean-room adversarial review  *(hunt cold — ORDERING IS DELIBERATE)*

Invoke the **`code-review-engine`** skill on the diff — the same house engine `/cicd-code-review`
runs (SCC-116), so Task work is reviewed to the story lane's standard: a parallel fan-out of three
lenses over the scoped diff, then triage. Each lens runs in its own clean context, which is what
zeroes out the builder's bias — an agent reviewing its own reasoning anchors on it — and each one
**reproduces what it reports** (SCC-447 retired the separate verify wave; the proof is now the
finder's job, and Step 1.4 re-runs it here).

**First, cut the review's scope — the lane is not the review:**

```bash
cd "$REPO" && python3 .agents/scripts/review_scope.py --repo "$REPO" --base origin/main --key <PART-KEY> --out <task-artifacts>/review/diff.patch   # PC: `python`
```

<!-- twin-law: review-scope -->
⛔ **A review reads ONE PART, and the masters only (SCC-447).** Handing the engine the whole
`base..HEAD` diff makes a lens read a byte-copy MIRROR of a file already in the same diff — it finds
the defect twice and reports it twice — and makes it read the lane's own RECORDS, which is reviewing
the description of the code instead of the code. Measured on SCC-441: 155 files and 1.46 MB became
82 files and 618 KB. `review_scope.py` groups the commits by their rider key (`work-consolidation`
Rule 2) and PRINTS every path it withheld beside the class that withheld it — a filter nobody can
see is a filter nobody can correct. More than one part in range with no selector is **exit 2 naming
the keys**, never a guess: a review of the wrong thing looks exactly like a review of the right one.
A lane whose parts carry no rider keys selects with `--range <the commit before the part>..<its last
commit>` — git's `A..B` excludes A, so the left bound is the commit BEFORE the part, never its first.

⛔ **There is NO byte cap, and that is a refusal rather than an omission.** A cap truncates at an
arbitrary line and the lens never learns what it did not see — the one kind of gap a review cannot
catch from inside itself. The size of a review is the size of a part; a part too big to review is a
part that should have been two.
<!-- /twin-law -->

**Then resolve every input — the engine resolves nothing itself, and a missing required input is a
stop, not a guess:**

| Input | What you pass |
|---|---|
| `REPO` | the repo Step 0 resolved |
| `WORKTREE` | this task's tree (Step 0 pinned it from `git worktree list`) |
| `DIFF` | the patch `review_scope.py` wrote — **one PART, masters only** (the command is above; re-taken after Step 0.7 absorbed `origin/main`) |
| `HEAD_SHA` | `git rev-parse HEAD` **re-read here, after that absorb** — never Step 0's value |
| `review_mode` | `full` when the task's `implementation_plan.md` exists; `no-spec` when it does not |
| `STORY_FILE` | that `implementation_plan.md` — on this lane the plan's acceptance list **is** the spec |
| `ARTIFACT_DIR` | `_artifacts/_main/<YYYY-MM-DD>_<slug>/` inside this tree — optional to the engine, which writes no receipts, and the root you pass the receipt writer at Step 1.4 |
| `review_runtime` | `fan-out` or `inline` — **what you PROBED at Step 0.9, never what you expect.** Pass it down and write the same value into the walkthrough header, so the roster the engine returns can be checked against the runtime that produced it |

⚠ **Step 0 read `HEAD_SHA` before Step 0.7 absorbed `main`.** Re-read both it and the diff here, or
the engine reviews a tree that no longer exists and your verdict cites a commit that is no longer the
tip — the exact invariant Step 0.7 opens by stating.

**Hunt the DIFF first. Open the plan and the walkthrough only AFTER the engine's summary comes
back** — for claimed evidence, plan-vs-built deviations, and the `## Your Actions` rows. Reading the
builder's account before the hunt imports exactly the bias this step exists to remove. **The ORDER
is the protection now** — SCC-447 retired the blind lens whose starvation used to carry it, so
nothing but this instruction stands between you and the builder's framing.

The lenses hunt for: logic flaws · AI drift · over-engineering · bloat · unnecessary abstraction · a
check that cannot fail · a claim in the walkthrough the diff does not support · missing test tiers ·
acceptance items the diff does not deliver.

⛔ **What comes back is a CLAIM, and you fix nothing yet.** Every `critical` and `important` arrives
with the command the lens says proves it; Step 1.4 runs that command HERE, on the tree that ships,
and the receipt it writes is what decides whether the finding exists at all. Fixing straight from
the engine's summary is fixing a lens's belief about a tree it may itself have edited (SCC-295).

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

## Step 1.4 — Reproduce on the real tree (the door's own run — SCC-447)

<!-- twin-law: reproduce-gate -->
⛔ **A `critical` or `important` with no receipt on disk does not exist.** The engine holds no Bash
and never runs a command, by design — what it returns is the lens's CLAIM plus the `reproduce:`
command the lens says proves it. A lens proves a defect in its OWN worktree copy, which it may have
edited: SCC-295 measured three of five lenses writing to the builder's tree, and one reporting a RED
that no version of the real code could produce. So the door runs every surviving `critical` and
`important` again, here, on the tree that ships — and the receipt is what proves the run happened.

Three results, and the exit code says which, so you can branch on it:

| Receipt | What it means | What you do |
|---|---|---|
| `reproduced` (exit 0) | the command FAILED on the real tree — the finding is there | the action policy below |
| `not-reproduced` (exit 1) | the command exited 0 — the finding is not there | `dropped — no reproduction`, counted |
| `unrunnable` (exit 2) | a missing tool, an import error — the command never RAN | neither: repair the command |

A command that exits 0 did not reproduce: the row is `dropped — no reproduction`, counted in one
line under the findings table and never written up individually.

⛔ **`unrunnable` is not a result** — nobody has learned anything from it, so repair the command and
run it again; never fix or drop the finding on it. A finding whose reproduction never ran is an
unexamined claim, and an unknown is not a pass.
<!-- /twin-law -->

```bash
cd "$REPO" && python3 .agents/scripts/repro_receipt.py run --root <task-artifacts> --id <finding-id> --cwd "$REPO" -- <the lens's reproduce command>   # PC: `python`
```

⛔ **Every flag goes BEFORE `--`; everything after it is the command verbatim** — and a `reproduce:`
line that carries a shell operator (`|`, `&&`, `||`, `;`, a redirect) is passed as ONE argument and
run through a shell: `-- bash -c '<the lens command>'`, or the caller's shell splits it before the
writer ever starts and the receipt attests to a command the lens never wrote. There is no
`--result` flag — you cannot hand the writer a verdict, only a command to run. `--cwd` is required:
without it the command runs wherever the shell happened to be standing and records a result about
nothing (SCC-154). Receipts land at `<root>/gates/repro/<id>.json`, one per finding id, and an
existing id refuses without `--replace` — two receipts for one finding is two stories.

<!-- twin-law: disposition-policy -->
⭐ **THEN FIX WHAT REPRODUCED — here, in this lane, in this turn (`code-standards` §6.5).** A
reproduced finding is fixed. There is no third bucket: nothing is escalated, nothing is deferred,
and no finding becomes a ticket (operator ruling 2026-09-11 — both retired buckets put a reproduced
defect in front of him to read, which is the review the lenses were made to reproduce so that
nobody has to).

| The receipt says | You do | Disposition written |
|---|---|---|
| reproduced `critical` or `important` | fix it here, now, with a pin seen RED then GREEN (`reproduce-before-you-fix` G1–G5) | `fixed @<sha> · pin <test>[:<case>] · repro <id>` |
| reproduced, and the fix needs the operator's permission — the constitution's **Ask First** list, or it contradicts the spec | write the fix and its pin as a patch beside the receipt, prove it with `git apply --check` on the lane tip, do **not** apply it | `held — ask-first: <row> \| spec-conflict · repro <id> · patch <path>` |
| reproduced, in a file this lane did not touch | not this lane's work (another repo · a file another LIVE lane owns): the `work-consolidation` ladder, receipt attached | `out-of-lane — <where it went>` |
| `critical` / `important` that did not reproduce, or arrived without its three fields | dropped, counted, never written up individually | `dropped — no reproduction` (one count line) |
| `suggestion` / `nitpick` | nothing at all; a count | `recorded` (one count line) |

**`held` is never a question and never carries a recommendation to weigh.** The fix is already
written; the only thing missing is permission the constitution says you may not grant yourself. Two
operator words move it — `apply <id>` (you apply the patch, run its pin red then green and re-stamp)
and `approved` (the lane ships without it and the row closes as `ruled — <his word>`).

⛔ **Nothing a finding produced is written under `## Your Actions`** — an open box there holds the
ticket forever at `jira_feed.py finish` (`:1774`, `:2452`), which is the loop, not a feature. The
survivors were fixed here, a `held` row carries its patch, and a review never produces a ticket
(operator rulings 2026-08-15, both).
<!-- /twin-law -->

<!-- twin-law: floor-at-the-stamp -->
**The engine's `severity_floor` is PROVISIONAL.** Step 4 resolves it at the stamp, on the rows still
**open** — never at triage, from whatever the lenses first returned. A row closed by a fix and a
green pin does not appear there at all. There are exactly **two** ways a row comes down, and both are
evidence on disk, never judgment: a receipt showing the command does not fail, or a fix with a test
seen red and then green. Any other downgrade is you overruling the review, which you may not do;
more severe needs no permission, because your own gates add their own reasons.
<!-- /twin-law -->

## Step 2 — Acceptance audit  *(against the checkable list, not against the code)*

Recover the task's acceptance list — `/smh-dev-task-tests` Step 1 echoed it, the plan carries it, and the
ticket's own `ACCEPTANCE` block is the authority behind both (`acli jira workitem view <KEY>`).

**No double audit.** In `full` mode the engine's Acceptance Auditor lens already walked the diff
against that plan — **import its findings** into the matrix below (source `review`) rather than
re-deriving them. What stays yours is the matrix itself: every item paired with the assertion that
proves it, which is a claim about evidence a lens cannot make for you.

For **each item**: name where the diff satisfies it, and **the assertion that proves it**. Then the
other direction — **anything in the diff beyond the list is drift**: cut it, or name why it stays.

**Then the SECOND left-hand side (SCC-231) — the declared set.** The acceptance list says what
must be TRUE; the plan's `## Declared Change Set` block says which files were meant to MOVE — a
file edited that satisfies an acceptance row but was never declared is invisible to the
reconciliation above. Diff the block against the real diff:

```bash
python3 .agents/scripts/declared_change_set.py diff <the plan> \
        --changed $(cd "$REPO" && git diff --name-only --no-renames <the same base this review resolved>)   # PC: `python`
```

(`--no-renames` matters: with rename detection on, a renamed file surfaces only under its NEW
path, so the declared `DELETE` of its old path reads as a false `unimplemented` row — and the
answer would depend on the machine's git config.)

<!-- twin-law: declared-drift -->
- **`undeclared`** = files(diff) − files(declared): a file the plan never named was edited.
  One finding per file, severity **important**.
- **`unimplemented`** = files(declared) − files(diff): declared and untouched — plan
  overreach, or dropped scope. One finding per file, severity **suggestion**.
- **`incomplete`** = declaration attempts the grammar rejected (a star bullet, a glob path, a
  missing row mapping) — the diff verb carries them through. One finding per bullet, severity
  **important**: a rejected declaration means the block cannot be trusted as the declared set,
  and its paths will read as `undeclared` noise until the bullets are repaired.
- An absent BLOCK returns `present: false` — that is itself ONE finding at **important**:
  "no declared set to reconcile against". Never a silent skip; the vacuous green is the exact case
  this side exists to catch. (An absent plan FILE is a loud exit-2 error — a broken invocation,
  never a state to reconcile.)
- Paths under `_artifacts/`, `_bmad/`, `_bmad-output/`, `_my_resources/` are carved out on BOTH
  sides — planning surfaces never count as drift (Step 1's raw diff still shows them).
- **Declared checks reconcile like declared files.** The plan's promised assertions and recorded
  evidence are part of the declared set: a promised check that shipped weaker — a presence pin
  where a mutation was promised, a recorded number that never landed — is drift — cut it, or
  name why it stays.
- **No drift row auto-fails the verdict.** Every drift row takes the same contract as the first
  side: cut it, or name why it stays.
<!-- /twin-law -->

- An item with **no evidence** is not satisfied, however obviously true it looks — run the assertion,
  or the item is one the diff does not deliver, which is this lane's own **FAIL** reason. It is not a
  soft note: §7 has two CONCERNS grounds and "nobody checked" is not one of them.
- An item whose evidence is *"I read it and it looks right"* is not evidence. Run something.
- No acceptance list recoverable anywhere → say so in the record: that is `no-spec` mode, declared up
  front rather than discovered here — the Acceptance Auditor is skipped by mode, the matrix is empty,
  and neither is a verdict ground (§7 has exactly two, and a mode-skip is not a dead lens). A review
  with no contract is reviewed on what it can prove: the hunt, the tests, the gates.

## Step 3 — The command-centre gate

**Paste actual output for every row. Run gates bare** — piping to `tail`/`head` returns the *pipe's*
exit code, which is how a red gate reads as green.

| Gate | Command | When |
|---|---|---|
| **Enforcement suite** | `python3 .agents/scripts/tests/run_all.py` | **always** — N/N files, exit 0 |
| **Toolkit lint** | `python3 .agents/scripts/workflow_lint.py --toolkit-only` | **always** — errors FAIL; a warning is recorded, never a verdict (§7) |
| **Assertion evidence** | re-run the task's own Step 2 RED assertions — `--case "<label>"` where the suite declares blocks, so this row cites the NAMED cases rather than a whole file | **always** — they must be GREEN now |
| **SOP currency** | `python3 .agents/scripts/sop_currency.py --paths <changed> --message "<subject>"` | a usage surface is in the diff |
| **Link + anchor** | `python3 .agents/scripts/check_links.py --base origin/main` | any `.md` in the diff |
| **Door parity** | every added/renamed command has exactly the doors its `platforms:` claims | a command was added, renamed or deleted |

**Receipts ride this lane too (SCC-146).** `/smh-dev-task-tests` Step 3 stamps the suite run at
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

<!-- twin-law: nested-machine-floor -->
⛔ **Run the machine floor only** (the audit door's Step 1). Nested inside a review the
judgment pass does **not** run: §1 comment-contract gaps and §2 judgment calls are counts in the
record, never a verdict (§7 as ruled 2026-09-11 — CONCERNS has exactly two grounds, and taste is
not one of them). A judgment pass nested inside a review can only manufacture a third ground. The
full two-half pass is for a STANDALONE audit.
<!-- /twin-law -->

- **No double drift-hunt.** Step 1 already walked these hunks — **import its drift/bloat findings**
  into the table (source `review`) instead of re-running the §2B ban-hunt.
- **No double machine floor either (SCC-146).** Nested here, the audit **imports Step 3's receipts
  and pasted runs** for `run_all`, `workflow_lint`, `sop_currency` and the link+anchor sweep instead
  of re-running them, and runs only what Step 3 did not: `py_compile`. A missing or invalid receipt
  means Step 3 owes a run — send it back, don't paper over it here. Standalone
  `/smh-clean-code-audit` is unchanged.
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

  ⛔ **Shown UNFENCED because that is how it must land (SCC-240).** `walkthrough_roster.py`
  strips code fences before it reads anything (SCC-154 — a canonical verdict pasted as evidence
  inside a fence once became the governing verdict), so a roster inside a code fence is a roster
  the gate cannot see. Copy these as PLAIN LINES.

  lenses_run:
  - edge-case-hunter · ok
  - test-adequacy-auditor · recovered-inline — fan-out returned nothing, rerun inline
  lenses_counted:  2/2
  lenses_na:
  - acceptance-auditor · n/a — skipped-by-mode (no-spec)

  ⭐ **Check the paste HERE, not at close-out** — `python3 .agents/scripts/walkthrough_roster.py
  <the walkthrough>` *(PC: `python`)*. It prints the rows it actually read and answers **one**
  question: can this roster be READ? Exit 0 yes; exit 1 names which of three things went wrong —
  a fenced roster, a header whose rows are not contiguous with it, or no roster at all; exit 2
  is a bad path, never a verdict about content.
  ⛔ **Bare, it is deliberately NOT the whole close-out gate**, and that is what makes it usable
  here: at this moment `dispositions:`, `drift:`, Step 0.7 and the `Verdict:` line are still
  unwritten, so a full-gate run would refuse on a missing `dispositions:` line and send you to
  hunt a fence that is not there. Once the section is complete, `--gate` asks the fuller
  question — and before the stamp exists it needs `--verdict PASS|CONCERNS|FAIL|WAIVED`.

<!-- twin-law: roster -->
  ⛔ **`lenses_na` and `lenses_counted` are part of the block, not optional trimmings (SCC-203).**
  The engine returns four roster fields and this step used to demand one. With the roster closed at
  three lenses (SCC-447), `lenses_na` carries exactly one legal row — the Acceptance Auditor's
  `acceptance-auditor · n/a — skipped-by-mode (no-spec)` — and `lenses_counted` is what keeps that
  skip out of the total, so a spec-less review reports `2/2` and a full one `3/3`. Omitting them is
  how a lens that did not run becomes invisible, which is the exact failure these two fields exist
  to prevent.
<!-- /twin-law -->

<!-- twin-law: record-lines -->
- ⛔ **two more machine-read lines, in the same section (SCC-231/233, law since 2026-08-20):**

  ```
  dispositions:    per-lens: <lens>=<reproduced>/<dropped>/<recorded> · …
  drift:           undeclared=<n> · unimplemented=<n> · incomplete=<n> — <dispositions live in the findings table, or name why there was no block to reconcile>
  ```

  `dispositions:` is pasted from the engine summary VERBATIM — the per-lens counts are the SCC-233
  record, and which lens's findings survived the reproduction gate is computable only if they land
  here.
  `drift:` is the declared-set reconciliation result from this command's own step, in one line.
  `walkthrough_roster.py` reads both and the close-out preflights BLOCK a lane missing either —
  the measured base rate for prose-only record obligations is 12 of 142, so neither line is left
  to memory.
<!-- /twin-law -->

  **A `Verdict:` is the review's conclusion; this block is what shows the review happened.** Without
  it the verdict is the only record of itself, and a walkthrough with zero lenses run merges clean —
  the defect SCC-173 was raised on. `walkthrough_roster.py` reads it here and
  `/smh-close-task-merge-tree` blocks a lane that does not carry it. Do not summarise it, do not
  re-order the rows into prose, and never write a state a lens did not report.
- scope + method, one line each;
<!-- twin-law: findings-table -->
- **ONE findings table, and it is the authoritative copy.** The header is fixed, because
  `walkthrough_roster.py` reads these rows at close-out and refuses a stamp they do not support:

  | # | file:line | sev | lens | failure scenario | repro | disposition |
  |---|---|---|---|---|---|---|
  | 1 | .agents/scripts/x.py:44 | critical | logic | an empty `--paths` list makes the sweep vacuous | f1 | fixed @a1b2c3d · pin test_x.py:S2 · repro f1 |
  | 2 | .agents/scripts/y.py:88 | important | drift | writes outside the lane's declared set | f2 | held — ask-first: CI config · repro f2 · patch gates/repro/f2.patch |

  Every `fixed` row names its pin; every `fixed` or `held` row names the `repro <id>` whose receipt
  is on disk and says `reproduced`; every `held` row names a patch that is on disk. Each of those is
  refused by row, naming what would satisfy it. `dropped` and `recorded` are COUNT lines under the
  table — one line each, never rows — because a finding that does not exist is not worth a row and
  taste is not worth a reader.
<!-- /twin-law -->
  (In `full` mode the engine may also leave `[ ] [Review]…` action items in the file you passed as
  `STORY_FILE` — a worklist carrying no dispositions, never a second record. This table wins.)
- each gate's result in one line with its **actual** output;
- the acceptance matrix from Step 2 — every item → its proving assertion;
- a `### Clean-Code Gate` subsection carrying Step 3.5's table and pasted output;
<!-- twin-law: rederive-record -->
- **Step 0.7's re-derivation**, under its own `### Step 0.7 — re-derivation` sub-heading as three
  numbered lines — what the landing ref moved under this diff, the true overlap + `merge-tree` result,
  and any sibling-lane landing-order dependency. "Nothing moved" is a reportable result; silence is
  not — `walkthrough_roster.py --gate` counts list rows under a heading matching `0.7`/`re-deriv`
  (E7) and refuses fewer than three.
<!-- /twin-law -->

<!-- twin-law: verdict-rules -->
**Verdict rules — resolved HERE, at the stamp, on the rows still OPEN (`code-standards` §7):**

- **FAIL** — an **open reproduced `critical`** at this stamp, held or not, with its receipt on disk.
  Or a machine reason of your own: the enforcement floor red on changed lines, a §2 banned pattern
  shipped, a committed secret, a gate that cannot fail.
- **CONCERNS** — exactly two grounds and nothing else: **authority**, an open reproduced `important`
  `held` because its fix needs the operator's word, with the patch written beside its receipt; and
  **coverage**, a lens still `dead` after its retry and its inline rerun — the review did not look
  everywhere. Taste is a count in the record, never a verdict.
- **PASS** — nothing open: every reproduced row closed by a fix with a green pin, every applicable
  lens ran, and the machine floor green on the changed set.

⛔ A reproduced `important` that is neither `fixed` nor `held` is **no verdict at all** —
`walkthrough_roster.py` refuses the stamp, naming the row, and you go finish the fix. It is not a
softer verdict; there is no verdict to write yet.

**CONCERNS is shippable, and the go/no-go is the operator's word.** It says the review found one of
exactly two things it cannot settle itself — a surface it could not examine, or a written fix it is
not allowed to apply — and he decides with the receipt and the patch in front of him, never with a
file to read. FAIL is the blocker; no command, door or agent may treat CONCERNS as one on its own
authority.
<!-- /twin-law -->

**This lane's own gates add their own FAIL reasons**, and they are machine reasons, never taste: an
acceptance item the diff does not deliver · a dead link or anchor the diff introduced · **a reference
this diff depends on that a landed lane moved, renamed or deleted (Step 0.7)** · a door-parity break ·
a `workflow_lint --toolkit-only` **error** · a deployable path in the diff (which is also an immediate
handoff to `/cicd-push-e2e`).

- **WAIVED** — the repo has **no enforcement suite at all** (`run_all.py` absent). Rare, and it does
  not waive Step 3.5: report the clean-code result inside the waiver.

> The split is deliberate: objective things block, taste does not. Taste gets recorded and fixed on
> its merits — never used to stall work on a reviewer's preference, and never used to make a verdict.

<!-- twin-law: one-review-per-lane -->
⛔ **One review per PART — the lenses run ONCE over each part.** A lane of one part is one review; a
consolidated lane (`work-consolidation` Rule 2) carries one roster per part, each under a
`## Code Review` heading that names its part (`part <KEY>`, or its `<sha>..<sha>` range). When
your fixes land, the retest is the pins named
in the `fixed` rows plus the enforcement suite once through the receipt writer. Never a second
fan-out over the same diff: measured over 138 reviews on disk, a re-review converted a non-PASS to
PASS one time in seven and cost a full roster every time. Append a NEW section rather than editing
the first — the last `Verdict:` governs:

```
## Code Review (<date>, re-stamp after fixes)

Verdict: PASS|CONCERNS @ <sha>
retest: scoped — pins: <test:case>, … · suite: run_all N/N @ <sha> (gates/suite.json)
review: carried from the one review @ <sha1> — no lens re-run
```

No second `lenses_run:` roster over the same part. `walkthrough_roster.py` counts roster headers PER
PART in the stripped text and refuses a walkthrough carrying two over one part without the operator's
written word on the section, his words quoted: `re-review: approved by the operator — "<his words>"`.

⛔ **The stamp's sha is the sha the SUITE evidence was measured on.** Any code or test diff between
that sha and HEAD invalidates the **suite evidence**, never the review: re-run the pins and the suite and
re-stamp — never the lenses. Artifact-only commits invalidate nothing.
<!-- /twin-law -->

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
  is the retired defect (operator rulings 2026-08-15, both), never a valid action row: what
  reproduced was fixed at Step 1.4, what could not be applied is a `held` patch on disk, and a
  review never produces a ticket. An open box here born from a finding HOLDS the ticket on the
  review ladder forever (`jira_feed finish`) — that is the loop, not a feature.
- **Hard rule: never finish this command with the walkthrough body left stale after applying fixes.**

## Step 6 — End the turn

<!-- twin-law: end-of-review -->
⭐ **End the turn with one screen, and end it — the review never pauses to ask.** You ran the lenses,
reproduced what they found on the real tree, fixed what reproduced, ran the gates and stamped. What
the operator gets is one screen: the verdict and its sha; the `fixed` rows (id, pin); the `held` rows
(id, reason, one line of evidence from the receipt, a link to the patch); the `out-of-lane` rows (id,
where they went); the counts of `dropped` and `recorded`; and the two words that move it — `approved`
(he runs the close-out door, and every `held` row closes as `ruled — <his word>`) or `apply <ids>`
(you apply those patches, run their pins red then green and re-stamp, in one turn).

**Nothing is a question and nothing is a recommendation to weigh.** A finding he has to read is a
bill, not a contribution (`operator-profile` obligation 9): by the time this screen exists, every
finding has been fixed, written as a patch, sent down the consolidation ladder, or counted.
<!-- /twin-law -->

## Stay in lane

Commit review fixes inside the task worktree, explicit paths only, every subject leading with the
ticket key. **Never merge to `main`, never transition the ticket, never prune the branch** — that is
`/smh-close-task-merge-tree`, and invoking **it** is the operator's per-merge sign-off. One invocation
authorises exactly one merge and never carries forward. Updating the walkthrough (Steps 4–5) is IN
lane: that is documenting the review, not closing it out.

Optional additional input (a repo, a branch, or a base ref): $ARGUMENTS
