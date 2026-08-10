---
description: Review + gate TASK work — clean-room adversarial review of the diff, an acceptance audit against the task's checkable list, the command-centre gate (enforcement suite + assertion evidence + link/anchor + SOP currency + door parity) and /smh-clean-code-audit, producing a PASS/CONCERNS/FAIL/WAIVED verdict in the task walkthrough. The smh- counterpart of /cicd-code-review, for work with no story, no board and no epic branch. Use when the user says "review this task" / "smh code review".
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
git -C "$REPO" diff --name-only main...HEAD           # the task's committed work
git -C "$REPO" status --short                         # anything uncommitted (report it; it is not reviewed)
```

Echo the file count. **An empty set is a STOP, not a pass.**

Dirty files under `_artifacts/_memory/` are **named separately and left alone** — another session's
memory is never swept, deleted, or committed under this task.

---

## Step 1 — Clean-room adversarial review  *(the blind hunt — ORDERING IS DELIBERATE)*

Invoke **`bmad-review-adversarial-general`** in a subagent with **NO conversation context**, at the
same model capability, on the diff. Zero out any builder's bias: an agent reviewing its own reasoning
anchors on it.

**Hunt the DIFF first. Open the plan and the walkthrough only AFTER** — for claimed evidence,
plan-vs-built deviations, and the `## Your Actions` rows. Reading the builder's account before hunting
imports exactly the bias this step exists to remove.

Hunt for: logic flaws · AI drift · over-engineering · bloat · unnecessary abstraction · a check that
cannot fail · a claim in the walkthrough that the diff does not support.

**Subagent-failure contract — a dead layer is a FINDING, never a silent skip:**
1. **Retry it once.** Transient tool failures are the common case.
2. **Still failing → re-run that lens INLINE yourself**, in this context. A lens is a prompt, not a
   privileged tool; losing the parallelism costs time, not coverage.
3. **Record the degradation in the verdict** — name the layer, the failure, and the recovery. "ran" and
   "died, re-run inline" are different evidence and must read differently.
4. **A layer that never ran at all caps the verdict at `CONCERNS`.** An unexamined surface is an
   unknown, and an unknown is not a pass.

## Step 2 — Acceptance audit  *(against the checkable list, not against the code)*

Recover the task's acceptance list — `/smh-quick-dev` Step 1 echoed it, the plan carries it, and the
ticket's own `ACCEPTANCE` block is the authority behind both (`acli jira workitem view <KEY>`).

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
| **Assertion evidence** | re-run the task's own Step 2 RED assertions | **always** — they must be GREEN now |
| **SOP currency** | `python3 .agents/scripts/sop_currency.py --paths <changed> --message "<subject>"` | a usage surface is in the diff |
| **Link + anchor** | resolve every path and `#L` anchor the diff touched | any `.md` in the diff |
| **Door parity** | every added/renamed command has exactly the doors its `platforms:` claims | a command was added, renamed or deleted |

**No receipts on this lane, and that is a stated limit, not an oversight.** `gate_receipt.py` writes to
`_bmad-output/gates/<story>/` and resolves a BMAD project; it cannot run here. So the evidence contract
is: **pasted real output, plus `git rev-parse HEAD` recorded beside it**, in the walkthrough's
`## Evidence`. Any code or script change between that sha and HEAD invalidates the verdict — which is
the same invariant the receipt enforces mechanically elsewhere, held by hand here.

**Run the suite ONCE, on the code that will actually land.** While fixing, run scoped — the tests for
what you touched. **After your LAST change**, run `run_all.py` in full and paste it, with the sha.
Artifact- and doc-only commits after that run do **not** invalidate it; code or test changes do.

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
- scope + method, one line each;
- **ONE findings table** — `file:line` · severity · failure scenario · disposition
  (`applied`/`deferred`/`dismissed`). The only copy anywhere; the plan links here, never restates;
- each gate's result in one line with its **actual** output;
- the acceptance matrix from Step 2 — every item → its proving assertion;
- a `### Clean-Code Gate` subsection carrying Step 3.5's table and pasted output;
- any **sibling-lane landing-order dependency** the review found.

**Verdict rules:**

- **FAIL** — the enforcement suite is red · a `workflow_lint --toolkit-only` **error** · an acceptance
  item the diff does not deliver · a dead link the diff introduced · a door-parity break · a committed
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
  product decision, a `main` merge, a ticket transition).
- **Hard rule: never finish this command with the walkthrough body left stale after applying fixes.**

## Stay in lane

Commit review fixes inside the task worktree, explicit paths only, every subject leading with the
ticket key. **Never merge to `main`, never transition the ticket, never prune the branch** — that is
`/smh-close-task-merge-tree`, and invoking **it** is the operator's per-merge sign-off. One invocation
authorises exactly one merge and never carries forward. Updating the walkthrough (Steps 4–5) is IN
lane: that is documenting the review, not closing it out.

Optional additional input (a repo, a branch, or a base ref): $ARGUMENTS
