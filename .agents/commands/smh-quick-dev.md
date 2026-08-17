---
description: The TASK lane's dev cycle — assert-first development for command-centre work that has no story, no sprint board and no epic branch. Write the check that fails FIRST (a test for a script, a machine-verifiable assertion for a doc or a structure), then make it pass, then the review gate. Acts on the repo you are standing in. Hands off to /smh-close-task-merge-tree. Use when the user says "dev this task" / "smh quick dev".
platforms: [opencode, antigravity, claude, codex]
---

# /smh-quick-dev — The Task Lane's Dev Cycle (assert-first)

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push
>   `main`, never force-push; every branch and every commit carries the repo's Jira key
> - `.agents/rules/worktree-per-story.md` — every commit-producing lane opens a worktree, Task lanes
>   included (SCC-62); §"cwd is not intent" is why the branch below is pinned from command output
> - `.agents/rules/000-PLAN-FIRST-GATE.md` — the literal word `approved`, and the four things that
>   are explicitly **not** it
> - `.agents/rules/artifacts-always-first.md` — a Task's artifacts live in
>   `_artifacts/_main/<YYYY-MM-DD>_<slug>/`; the closing `walkthrough.md` is never skipped
> - `.agents/rules/reproduce-before-you-fix.md` — **when the task is a BUG fix**: reproduce → minimize
>   → pin a test seen red → falsify one hypothesis at a time → minimal fix → prove by reverting
> - `.agents/rules/tests-must-gate-for-real.md` — Step 2's red must fail for the RIGHT reason, and
>   Step 3's mutants follow its **§ Mutation Testing**. Loaded HERE, at the command that *writes* the
>   assertions — it used to arrive only at review, one step after the mutants were designed (SCC-145)

**The dev cycle BMAD has no answer for.** `/cicd-dev-story-tests` carries the test-first discipline but
needs a story file, a sprint board, an epic branch and a status flip. `/cicd-quick-dev` is the fast lane
and is still story-shaped. A Task — move thirteen docs and rewrite thirty-two references; extend a
commit gate; add a command to four platform menus — has **real testable behavior** (the gate must still
reject, the links must still resolve, the menus must still agree with disk) and **no ceremony to hang it
on.** This is that cycle.

> **What "quick" means here, and what it does not.** What this lane drops is the BMAD *ceremony* — no
> story file, no `sprint-status.yaml` row, no epic branch, no `review`→`done` flip. What it keeps is
> everything that makes work correct: a worktree, a right-sized plan, an adversarial pre-work audit,
> the literal `approved`, an assertion written **before** the edit, and a mandatory review gate.
> **Accuracy over speed.**

> Flow position: `/smh-quick-dev` → `/smh-code-review` → **[STOP]** → `/smh-close-task-merge-tree`
> (the operator's, and typing it IS the merge sign-off).

---

## Step 0 — Resolve the repo (FIRST) — from command output, never from belief

The subject is **where you are standing**, not a pointer. If `$ARGUMENTS` names a folder under
`Projects/` or a path, use that; otherwise the current repo. Do **not** read
`.agents/active-project.txt` — this lane's whole point is that the command centre is a legitimate
subject, and that pointer names a child.

```bash
REPO=$(cd "<the path you resolved>" && git rev-parse --show-toplevel)
echo "Repo: $(basename "$REPO")"
```

**Pin the ticket key you are working, before any tool has answered anything.** Task work is filed
under a grouping epic and every branch and commit must carry the key, or the armed `commit-msg` hook
refuses the commit:

```bash
EXPECTED_KEY="SCC-00"     # the ticket you MEAN
acli jira workitem view "$EXPECTED_KEY"      # read its ACCEPTANCE block — Step 1 needs it
```

No ticket at all → **STOP and ask.** Never invent a key; a keyless Task cannot be committed, closed,
or found again.

**⭐ Probe the review runtime here, at Step 0, and record it (SCC-177).** Ask this runtime whether it
can fan out to subagents — do not answer from what usually happens, because a headless pipeline or
a platform with no subagent tool makes the answer `inline`, and both are invisible until a lens
fails to launch three steps later. The answer goes into the
walkthrough header Step 5 writes, on its own line, above everything else:

⛔ **The probe is a **capability**, never a **policy** (SCC-203).** *Does a subagent tool exist in
this runtime?* is the whole question; *am I permitted to use it?* is a different one, and answering
it here is how a session directive — *"do not spawn subagents unless the user asks"* — got read as
*"this runtime is inline"*, ran an entire review inside the builder's own context, and had the flow
record it as legitimate. ⭐ **Subagents are the DEFAULT, and invoking a review IS that request** —
you never stop to ask for them, and never quietly downgrade to `inline` to avoid asking. Only a
runtime with no subagent tool at all is `inline`.

```
review-runtime: fan-out
```

⛔ **Step 0, not Step 4 — the probe must precede the review it describes.** Recorded afterwards it is
read off the roster that already exists, which makes the check circular: the header can only ever
agree with the states it was derived from. Recorded here it is an independent claim, and
`walkthrough_roster.py` blocks the close-out when the roster disagrees with it (`inline` + a lens
reporting `ok` is the contradiction it catches).

## Step 0.5 — Worktree and branch (before the first edit)

Per `worktree-per-story` + SCC-62, every commit-producing lane isolates — Task lanes included. The old
ban on `chore/*` worktrees existed only because nothing cleaned them up; `/smh-close-task-merge-tree`
Step 5 does now.

```bash
git -C "$REPO" worktree list                                   # reuse this task's tree if it exists
git -C "$REPO" fetch origin                                    # ⛔ the base is origin/main, never a bare `main`
git -C "$REPO" worktree add .claude/worktrees/<slug> -b chore/<KEY>-<slug> origin/main
git -C "<the new tree>" branch --unset-upstream                # a start-point of origin/main sets upstream to MAIN
python3 .agents/scripts/link-worktree-assets.py .claude/worktrees/<slug>   # PC: `python`
BRANCH=$(git -C "<the new tree>" rev-parse --abbrev-ref HEAD)
echo "Lane: $BRANCH"
```

**⭐ Reusing a tree `/smh-plan-task` cut? Absorb `main` FIRST (SCC-155).** That command cuts every
lane's worktree at planning time, so a 🔒 lane picked up days later is branched from a `main` its
siblings have since moved. Absorb before the first edit, never at the merge:

```bash
git -C "<tree>" fetch origin && git -C "<tree>" merge --no-edit origin/main
```

Conflicts here are cheap and yours; the same conflicts at close-out are on `main`'s doorstep.

Echo the branch **from `rev-parse`, never from memory.** Every path and command from here binds to that
tree.

**Move the ticket to `In Progress` — now, at the tree, not at the merge (SCC-113):**

```bash
python3 .agents/scripts/jira_feed.py start --key <KEY> --apply    # PC: `python`
```

Idempotent, so a re-run or a resumed lane is a no-op. **Read its exit code — three outcomes:**

| Exit | Means | What you do |
|---|---|---|
| `0` | moved, or already `In Progress` | carry on |
| `3` | **left alone** — the ticket is `Blocking` / `In Review` / `Deferred` | **stop and ask.** You are opening a lane on a ticket that is waiting on something; say which and confirm that is intended |
| `2` | **the board refused it** — a `Done` key (so the key is wrong), or a move that did not land | **stop.** Never work a closed ticket's key; mint one at the `jira.md` §Who-mints-tickets seam |
| `4` | **the board was unreachable** — transport, not a verdict | **carry on and retry later.** ⛔ Do *not* mint a ticket: nothing here says your key is wrong. Sandboxed shells cannot reach the credential store (`jira.md` top), and the operator commits from planes |

> **The `post-commit` hook does this too, and that is deliberate, not redundant.** The hook fires on
> the first commit of any `chore/ · claude/ · epic/` branch, so work started without this command
> still shows on the board. This call moves it *earlier* — at the tree, before the first commit —
> and visibly. Neither layer is load-bearing alone: `core.hooksPath` is per-machine, so on a fresh
> clone the hook is silently OFF until it is set, and this line is what still works.

**⭐ Read the sibling lanes now, not at merge time.** Several `chore/*` lanes run at once and their
uncommitted work is invisible to `grep`:

```bash
git worktree list
git -C <each-other-tree> diff --name-only origin/main...HEAD
git -C <each-other-tree> status --short
```

Any file in both their set and your intended set is a **landing-order dependency**. Say which lane
should land first and what happens to your work if it does not. Carry it into the plan.

---

## Step 1 — Fix the checkable list (before any plan, and before any code)

There is no story file, so there are no story ACs. **The acceptance list comes from, in this authority
order:** the ticket's own `ACCEPTANCE` block → the operator's stated intent in this session → you write
2–6 statements and echo them for confirmation.

**Every item must be checkable by a command or an inspection.** This is the whole accuracy baseline of
the lane: Step 2 turns each one into an assertion that FAILS first, so an item that cannot be checked
cannot be built here.

| Not checkable | Checkable |
|---|---|
| "the docs are consolidated" | `docs/_scc_sops_prds/` holds all N files and no other copy remains on disk |
| "the gate is folder-aware" | `sop_currency.py --paths docs/_scc_sops_prds/x.md` exits non-zero without the doc staged |
| "the new command works" | `workflow_lint.py --toolkit-only` exits 0 and all four platform doors exist |

Echo the list. If the intent will not reduce to checkable statements, that is not work for this lane —
say so and stop.

## Step 1.5 — Plan, audit it, then STOP for `approved`

⛔ **Read the batch box below BEFORE item 1.** It is placed after the list for readability, but an
agent following the numbered steps literally would rewrite and re-audit the very plan the operator
already approved — and by clause 3 of `000-PLAN-FIRST-GATE`, editing the plan **re-arms the gate**,
destroying the approval the box exists to honour. Fail-safe, but it makes the feature unreachable
by literal reading, which in this house is the same as not shipping it (SCC-155 review #11).
**If this lane arrived from `/smh-plan-task` with a plan already on it, items 1 and 2 are already
done — verify the box's four conditions and go straight to Step 2.**

1. **Write `implementation_plan.md`** *(skip if this lane arrived with an approved plan — see the box)* into `_artifacts/_main/<YYYY-MM-DD>_<slug>/`, right-sized to the
   work. Each acceptance item maps to a step, and each step names **the assertion that will prove it**.
2. **Invoke `/smh-self-audit`** on that plan. It appends its `## Self-Audit (<date>)` section and a
   canonical `Audit verdict: GO | NO-GO`. A **NO-GO stops the lane** — fix the plan and re-audit; do not
   proceed on a NO-GO and do not re-run it hoping for a different answer.
3. **STOP and wait for the literal word `approved`.**

> **⭐ Already approved as part of a batch? (SCC-155)** If this lane came from `/smh-plan-task`,
> its plan already carries a `**Batch approval (<date>):** "<the operator's words>"` line naming
> this subtask's key. That IS the approval for this plan — go straight to Step 2.
>
> **All FOUR of the rule's conditions, restated here because this is where they are acted on** —
> the box used to claim "two conditions" and check two of them, and an agent follows the literal
> step list (SCC-155 review #13/#17):
>
> 1. the line carries the operator's **verbatim words**, and they name **this** subtask key;
> 2. that lane's plan recorded `Audit verdict: GO` at the stop;
> 3. the plan is **unchanged since the approval was recorded** — and the approval line now ends
>    `— recorded at <sha>`, so this is a real comparison:
>    `git log -1 --format=%h -- <the plan>` **must equal that sha**. No sha on the line means the
>    planner predates this contract: **the gate re-arms, you stop.** A missing operand is never a
>    pass;
> 4. the work is still the planning-only scope the batch covered.
>
> Any one of them missing? You stop here like any other lane. See `000-PLAN-FIRST-GATE.md`
> § "One approval MAY cover several plans".

⛔ Per `000-PLAN-FIRST-GATE`, these are **not** approval and never have been: "ok" · "looks good" ·
"continue" · clicking an option you wrote (that answers *which*, never *whether*) · being told to do
the work ("go build it" is the *reason* for a plan, not permission to skip one) · answering your
clarifying question · the operator **correcting** the plan — a correction narrows the plan and you stop
and wait **again**. You are forbidden from putting the word "approved" in a button label; writing the
word yourself and reading it back is how this gate actually gets bypassed.

**The one exemption**, and it is narrow: the self-audit's Phase 0 returned **Skip** — a typo, a comment,
a one-line doc tweak. Say which, then proceed. Anything above that gets the gate.

---

## Step 1.6 — Subtasks: PROPOSE the breakdown, then stop (SCC-119)

> ⭐ **Look for a home BEFORE you mint (`work-consolidation.md` rule 1, SCC-170).** Work discovered
> mid-lane — a review finding, a bug met while building, a defect a test exposes — is **not**
> automatically a new Task. In order: does this lane's own ticket cover it (a checklist line)? is
> there an **open parent** whose surface this belongs to (then it is the next lettered
> **Subtask** under it, with an index row added via `jira_feed.py index-row`, which reads the
> parent's description back and refuses if a line went missing)? no thematic parent — then it is a
> subtask on the **OPEN ROLLING TICKET** (`Bugs and Updates - <YYYY-MM>`, label `bugs-and-updates`; `SCC-190` today), which is rung 3 and the normal answer for a
> finding a landing exposes; only then mint, for work that is a lane in its own right — and say in
> ONE line what you looked at. Judgment, not a gate; the unstated choice is the thing that is banned.
> *"we are not developing 3 task for every 1 we try to fix"* (operator, 2026-08-15).

**Runs only after `approved`, and only on a `Task`** — never on a BMAD Story, whose story file already
holds its breakdown (`jira.md` §Subtasks: the story lane's answer is **NEVER**).

Read the approved plan and ask **one** question of each piece of work in it:

> **Does this piece earn its own `chore/<KEY>-<slug>` branch in its own worktree?**

- **No** → it stays a checklist line in the plan or in the ticket's `ACCEPTANCE` block. Three edits in
  one commit are not three subtasks, and a ticket with no branch is a row nothing will ever write to.
- **Yes** → it is a `Subtask` under **the ticket you were handed**, which is the top-level one.

**If nothing clears the bar, say so and move on — that is the normal answer for most tasks.**

⛔ **PROPOSE, then STOP. You write nothing to the board until the operator says go.** Print one line
per proposed subtask, each naming the branch it would get. Placement is the operator's (guardrail 2)
and minting off your own reading is speculative work (guardrail 3).

On the operator's go, mint each one with raw `acli` — parented to this ticket, bare, no `--assignee`:

```bash
acli jira workitem create --project <PROJ> --type Subtask --parent <THIS-TICKET-KEY> \
  --summary "…" --description "…"
```

Then work each subtask as its own lane: its own worktree, its own branch, its own run of this command,
its own `/smh-close-task-merge-tree`. **The parent closes LAST**, when every child is `Done` or
`Deferred` — `task_preflight.py` refuses it otherwise.

⚠️ A `Subtask` cannot have children (`hierarchyLevel: -1` is the floor). If a piece needs its own
breakdown, either keep that as a checklist inside it or promote it to a `Task` — do not try to nest.

---

## Step 2 — ⭐ RED — write the assertion that fails, FIRST

**Nothing is edited until something is failing.** A check that never failed proves nothing, and on this
lane it is the only proof there is. Pick the tier the work actually has — the discipline is identical,
only the instrument changes:

| The work is… | The RED is… | Where it lives |
|---|---|---|
| a **script** (`.agents/scripts/*.py`) | a real test asserting the new behavior | `.agents/scripts/tests/test_<name>.py`, run via `run_all.py` |
| a **gate or hook** | a test that the gate **refuses** the case it must refuse — and **passes** the case it must allow. Both halves, always: a gate that rejects everything is as broken as one that rejects nothing | `.agents/scripts/tests/test_<gate>.py` |
| a **command or a rule** | `workflow_lint.py --toolkit-only` reporting the specific error, or the specific missing door, before you fix it | the linter's own output |
| a **move / rename / delete** | the link + anchor sweep listing the references that will break, captured **before** the move | pasted into the walkthrough |
| a **doc or structure** | a machine-verifiable assertion: this path exists, this INDEX row matches disk, this link resolves, this grep returns zero | a test file if it will recur, the pasted command if it will not |

**Run it and paste the actual RED output.** Then read *which line raised* — a check that dies in setup
looks identical to one that fails its assertion, and only one of those is a real red.

> **Run the new cases, not the whole file.** Where a suite file declares blocks (`if c.block("…"):`),
> `python3 <suite> --case "<label>"` runs just yours — seconds instead of the file's full wall, which
> on the big suites is 58 s (`test_task_preflight.py`), 51 s (`test_git_hooks.py`) and 42 s
> (`test_task_preflight_receipts.py`). ⛔ **Exit 3 means the filter selected NOTHING to run** (typo'd
> label, a file with no blocks, a block with no cases, or a label that went missing — a bare
> `--case`/`--case=`/empty value, which is what an unset shell variable becomes) — it is not a red and not a green, it is a mis-typed
> command. The full file still runs before you commit; the filter is for the loop, not the proof.

⛔ **A red that asserts strings, paths or preconditions that do not exist in real source is fiction, not
a red.** Delete it and write one against what is actually there.

⛔ **Never write the assertion after the edit and call it test-first.** If the work is already done when
you arrive, say so plainly in the walkthrough — a characterization check written green is honest; a
green check presented as a red is not.

## Step 3 — GREEN — implement, minimally

Make the failing check pass and **nothing more.** The plan is the scope; anything beyond it is drift —
cut it or name why it stays.

- **Surgical changes.** Do not reformat, re-order or "tidy" adjacent lines your change did not break.
- **Commit inside the worktree, explicit paths only** (`git add -A`/`.`/`-u` are banned), every subject
  leading with the ticket key.
- ⛔ **Backticks in `-m "…"` EXECUTE.** A message quoting a shell command runs it. Use `git commit -F
  <file>` whenever the message contains a backtick.
- **A usage-surface change must stage the SOP doc in the SAME commit** — `.agents/commands/`,
  `.agents/rules/`, `.agents/scripts/*.py|.ps1`, git hooks, root `AGENTS.md`. The armed gate refuses
  otherwise. `[sop-ok]` is the auditable exit when the change genuinely alters nothing an operator
  types; it stays in the log as the record of that call.
- **Generated surfaces are never hand-edited.** `.agents/workflows/`, `.opencode/commands/`, and
  `GENERATED by sync-agents` skills come from the command file. Edit the command, then run
  `/smh-sync-agents`.
- **Re-run the RED check and paste it GREEN.** While fixing, keep it case-scoped (`--case`); run the
  whole file once after the LAST fix.
- **⭐ STAMP-FIRST — the receipt run IS the suite run, not a second opinion.** Do **not** run
  `run_all.py` bare "to check" and then run it again through the receipt writer: that is one
  70-second suite paid for twice, for nothing (3.4 minutes if you reach for `--serial`). The first full run of the landing code goes through
  the writer. **A red receipt is the mechanism working** — it records what the suite actually said,
  you fix, you re-stamp. Run the full enforcement suite once, on the code that will actually land —
  **through the receipt writer (SCC-146)**, so the run leaves evidence the review and the close-out
  can inherit instead of re-running it:

  ```bash
  python3 .agents/scripts/gate_receipt.py run --task <KEY> --gate suite \
      --root _artifacts/_main/<YYYY-MM-DD>_<slug> --cwd <worktree> \
      -- python3 .agents/scripts/tests/run_all.py
  ```

  Paste the real output exactly as before — the receipt is *additional* evidence, never a
  replacement for reading the run. It lands at `<task-artifacts>/gates/suite.json` and rides the
  chore branch through the merge. Stamp it on a **clean tree** (commit first, then run): a
  receipt over uncommitted **code** edits records `DIRTY` and inherits as invalid — correctly.
  The receipt is not its own dirt: since **SCC-178** the writer excludes the `<root>/gates/`
  directory it is writing into from the measurement, so a second gate in the same lane no
  longer reads DIRTY off the first one's receipt, and no lane pays a second full suite run to
  clear a smudge the writer made itself. Everything else still counts — a sibling file under
  `<root>/`, another lane's artifacts, any code path.
- **⭐ Declare the mutant table BEFORE you mutate, and draw every mutant *from the code*.** One row per
  mutant: the mutant, the file, and **the NAMED case it must kill.** Run them as **one sweep**, never
  one at a time — a sweep improvised one mutant at a time cannot check itself.

  **Since SCC-179 the sweep is a SCRIPT, and running it by hand is the defect.** Write the table as
  JSON and hand it to `mutation_sweep.py`; it refuses to start if a table file is already dirty,
  restores in a `finally` and on SIGTERM, proves the restore against the pinned pre-sweep sha AND the
  pre-sweep bytes, and runs the **full** test file unfiltered at the end — the run that would have
  caught `8681d83`, where every scoped `--case` was green and a live mutant rode into the gate.

  ```bash
  python3 .agents/scripts/mutation_sweep.py --table _artifacts/_main/<folder>/sweep.json
  ```

  ```json
  {"test": ["python3", ".agents/scripts/tests/test_thing.py"],
   "mutants": [{"id": "M1 what it does", "file": ".agents/scripts/thing.py",
                "original": "<exact text, EXACTLY once in the file>",
                "mutated": "<the mutation>",
                "case":  "<the case that must appear on the FAILED: line>",
                "block": "<the c.block() label --case selects; omit if it equals `case`>"}]}
  ```

  ⛔ **`case` and `block` are different namespaces, and conflating them is a sweep that cannot
  run.** The harness filters by **block** label; attribution reads the **case** name off the
  `FAILED:` line. Declaring a case name as the filter matches no block, the harness exits 3, and
  the sweep refuses to call that a kill — which is the correct answer and a wasted sweep. This
  script's own first run got it wrong on all eight mutants.

  Paste its output into the walkthrough as the sweep record. Then:
  - A **surviving** mutant is a finding.
  - A mutant whose edit does not appear in the original text is **DEFECTIVE** — a SKIP that **counts
    as a survivor** — and it must be re-aimed before it is believed.
  - Mutants drawn from your own **cases** rather than **from the code** are circular; they prove only
    that the suite agrees with itself (SCC-144: its 14 case-derived mutants were all killed, while a
    later set drawn from the code left **24 of 25 surviving**).
  - **Restore in a `finally`/trap and re-check `git status` when the sweep ends.** A killed sweep
    leaves the mutant on disk, and a mutated gate is committable.

  Record the table in the walkthrough. Full doctrine, including which technique fits which shape:
  `.agents/rules/tests-must-gate-for-real.md` **§ Mutation Testing**.

## Step 3.5 — ⛔ EJECT TRIPWIRE (check here, and again as you go)

**STOP and hand the work over if any of these is true:**

- **A deployable path is in the diff** — `backend/`, `frontend/`, `firebase/`, `functions/`, `mobile/`,
  `.github/`. That is a product change whatever the ticket says, and the product has one road to
  `main`: `/cicd-push-e2e`. There is no override, deliberately.
- **The work turns out to be BMAD story work** — it has a story id, it belongs on a sprint board, it
  needs an epic branch. Hand it to `/cicd-write-story-tests` ①.
- **The acceptance list will not reduce to checkable statements** (Step 1), or a review finding in
  Step 4 is bigger than a trivial patch.
- **The self-audit returned NO-GO** and the plan cannot be fixed without re-scoping.

Report the one-line reason; keep the worktree and everything written. Discard nothing.

---

## Step 4 — Review gate (mandatory — never skipped, never "assumed clean")

**Invoke `/smh-code-review`.** It runs the independent adversarial review, the acceptance audit against
your Step 1 list, `/smh-clean-code-audit` (the machine floor), and issues the canonical
`Verdict: PASS|CONCERNS|FAIL|WAIVED @ <sha>` line into the walkthrough.

A **FAIL** is not a finding to note and move past — fix it and re-run the gate. Anything bigger than a
trivial patch fires Step 3.5.

## Step 5 — Artifacts, the manifest, and the Dev Record

**The walkthrough** — `_artifacts/_main/<YYYY-MM-DD>_<slug>/walkthrough.md`, carrying, in order:
`review-runtime:` (the header from Step 0, one line) → `## Task Checklist` (the todo list's end
state, findings indented under the task that fought back) →
`## Evidence` (each acceptance item → the assertion that proves it, **RED output then GREEN output**,
plus the HEAD sha) → `## Code Review (<date>)` (appended by Step 4, with the `Verdict:` line and the
`lenses_run:` roster) → `## Your Actions` (what landed, and what is still the operator's). It is never
skipped — the close-out preflight blocks without it.

> **⭐ `## Your Actions` is a MACHINE CONTRACT now, not prose (SCC-155).** The close-out reads it
> through `jira_feed.py finish`, and it decides whether the ticket may go `Done`:
>
> - **An unchecked `- [ ]` line under that heading is something only the operator can do.** It
>   holds the ticket out of `Done`, posts itself to the board as a "User tasks" comment, and adds
>   the `user-tasks` label. Continuation lines indented under it ride along.
> - **`- [x]` is settled**, and prose is context. Neither holds anything.
> - **Write the section even when nothing is owed** — an empty `## Your Actions` closes cleanly,
>   but a *missing* one is a hard refusal. An absent section is not evidence that nothing is owed,
>   and `finish` will not guess.
>
> **⛔ And the CEREMONY's steps are not entries (SCC-193).** A row telling the operator to click
> Merge, to re-invoke the close-out, or to run `--after-merge` is **refused** by `jira_feed.py`
> (`check-actions`, and again at `finish`). Their **decision to proceed** is the sign-off — the word
> `approved`, or invoking `/smh-close-task-merge-tree` or `/cicd-push-e2e` — and from that word on
> every step is the ceremony's and you run it. What belongs here is what only they can DECIDE.
>
> So: everything genuinely owed to the operator goes in as a checkbox. Everything else — what
> landed, what you decided — stays prose above them.

**The manifest** — `task.yaml` beside it, so intent lives somewhere no cwd drift can reach:

```yaml
task_key: SCC-00
primary_repo: <repo folder name>
branch: chore/SCC-00-<slug>
close_command: smh-close-task-merge-tree
secondary_repos: []
```

**The Dev Record** — file it now, because this lane may end here:

```bash
python3 .agents/scripts/jira_feed.py devrecord --key <KEY> \
       --stage quick-dev --walkthrough <the walkthrough> \
       --outcome "<what shipped, one line>" --verdict "<the Step 4 verdict>" \
       --decision "<a ruling made while building>" --pitfall "<what nearly bit>" \
       --followon "<only what Step 4 deferred against a NAMED blocker - never a pile>" --apply
```

**Exactly one Dev Record per ticket** — the script finds an existing record and UPDATES it, so a later
`/smh-close-task-merge-tree` ends with one current record instead of two partial ones. ⛔ **It finds it
by the SLUG, not by `--key`, so do not pass `--story` (SCC-174).** The slug is read from the
`task.yaml` you wrote in Step 0 — the same source the close-out uses, which is the whole point: this
step filing AVCH-59 under `main-write-gate` while the close-out passed `avch-59-main-write-gate` gave
the ticket two records and `check` called it "the designed state". **Never pass
`--append-new`.** It reads the ticket back and exits 2 if the comment is not there; a non-zero exit
means the record did **not** land — report that, not success.

## Done — stop here

Do **NOT** merge to `main`, do **NOT** transition the ticket, do **NOT** prune the branch. That is
`/smh-close-task-merge-tree`, and **invoking it is the operator's per-merge sign-off** — one invocation
authorises exactly one merge, and it never carries forward to the next task.

Print: the plan link · the walkthrough link · the RED→GREEN evidence · the Step 4 verdict · the branch
and its push state · anything still owed. Then invite the operator to review and close it out.

Optional additional input (a repo, a ticket key, or the intent): $ARGUMENTS
