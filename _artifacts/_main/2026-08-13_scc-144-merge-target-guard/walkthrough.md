# SCC-144 — Make the merge-target guard mechanical (walkthrough)

- **Ticket:** SCC-144 (Task) · **Lane:** `chore/SCC-144-merge-target-guard` · **Cut from:** `main` @ `5dadcd6`
- **Plan + Self-Audit:** [`implementation_plan.md`](implementation_plan.md) — `Audit verdict: GO`
- **Date:** 2026-08-13

---

## Task Checklist

- [x] **Step 0/0.5** — repo resolved from `rev-parse`, ticket read, worktree cut, SCC-144 → `In Progress`
- [x] **Step 1** — acceptance list taken from the ticket's own `ACCEPTANCE` block (A1–A8), plus **A9**
      added by the operator's F-D ruling
- [x] **Step 1.5** — plan written, `/smh-self-audit` run (FULL), **GO** with 7 findings, 5 baked in,
      1 cleared, 1 escalated to the operator
- [x] **Step 1.6** — subtasks: **none clear the bar.** Every piece shares one commit boundary (F-E)
- [x] **Step 2/3** — RED → GREEN in four staged commits
  - ⚠ **The ticket's stated mechanism does not work.** `pre-merge-commit` cannot name its source.
        Measured, redesigned onto `commit-msg`, dispatcher deleted rather than shipped decorative.
  - ⚠ **Case E was rewritten during the audit** — pinning an absence with a tracer would have
        asserted a property of the fixture, not of git.
  - ⚠ **Case M was a fixture bug**, not a guard bug: the "empty lane" was already an ancestor, so
        `git merge` reported *Already up to date* and proved nothing about ambiguity.
- [x] **F-D** — the merge carve-out was blind in every worktree. Fixed on the operator's ruling.
- [x] **Mutation pass** — 14 mutants, 14 killed
  - ⚠ **One mutant SURVIVED and the mutant was what was wrong** — see *Mutation* below.
- [x] **Step 4** — `/smh-code-review`
- [x] **Step 5** — artifacts, manifest, Dev Record

---

## Evidence

Every case drives **real git** in a real repo through a real `core.hooksPath`. Not one greps a
script for a string: a source-grep guard cannot see whether git ever invoked the hook, which is the
SCC-125 lesson and the reason `test_main_push_gate.py` carries its own end-to-end case.

### A1 · a merge onto the wrong branch is refused by mechanism

**RED** (`red-01-merge-guard.txt`, 24 cases, 10 pass / 14 fail — every failure at its assertion, none
in setup; the ALLOW half passes because with no gate everything is allowed, which is exactly why the
ALLOW half alone is a vacuous green):

```
[FAIL] the guard script exists
[FAIL] B · chore -> chore is REFUSED: Merge made by the 'ort' strategy.
[FAIL] B · ...and NO merge commit was created
-- 10/24 passed --
```

**GREEN** — and the refusal, taken from a real merge rather than quoted from the source:

```
  ⛔ MERGE REFUSED — wrong TARGET branch

     target (the branch RECEIVING it):  chore/SCC-2-b   [chore]
     source (what is being merged in):  chore/SCC-1-a   [chore]

  ⛔ This is the SCC-97 signature exactly: one lane's work landing on a SIBLING LANE.
     On 2026-08-11 it printed success and was caught only by suspicion.
     Rule: .agents/rules/git-policy.md § Branch model —
       a chore/* lane merges into main (/smh-close-task-merge-tree)

     Remedy:  git merge --abort   then re-check where you are standing:
                git -C "$REPO" rev-parse --abbrev-ref HEAD
              A cd is not a lock across steps — pass -C on every git call.
     Bypass once: git merge --no-verify
```

### A2 · the refusal names the target, the source and the rule

Four assertions, plus two the audit added: the **remedy** and the **override**. A diagnosis with no
remedy is half a gate — `test_hooks_armed` case B pins the same property on the arm-check.

### A3 · the fast-forward gap has a *named* backstop

**Measured, not assumed.** A trace of real merges:

| merge path | `pre-merge-commit` | `MERGE_HEAD` there | `commit-msg` | `MERGE_HEAD` there |
|---|---|---|---|---|
| clean auto-merge | fires | **absent** | fires | present |
| conflicted merge | **never fires** | — | fires (at `git commit`) | present |
| fast-forward | never fires | — | never fires | — |

Case **E** pins the gap as a fact about git: a forbidden topology run as a fast-forward, fully
armed, **succeeds**. Cases **G/H/I/I2/O** cover the backstop. **RED** (`red-02-backstop.txt`):

```
[FAIL] G · pushing a lane contaminated by a FF merge is REFUSED
[FAIL] G · ...and nothing reached the remote: refs/heads/chore/SCC-144-b
[FAIL] O · ...and it says it could not judge
-- 37/42 passed --
```

**GREEN** — 42/42, then 52/52 with F-D and N2.

### A4 · `--no-verify` stays, and the header says so

Case F runs the refused merge with `--no-verify` and asserts it lands; a second assertion greps the
guard's own header for the word. Stated in the file as **accepted, not a hole to be closed later**.

### A5 · the new gate is in the `hooks_armed` accounting

Case L asserts the `ARM_FLAGS` row, the script it names, the dispatcher it names, **and that the
dispatcher really calls it**. The last one matters: `ARM_FLAGS`' `via` field is not cosmetic —
`test_hooks_armed` case V reads a flag whose `via` hook is untracked as NOT ARMED.

⭐ **This case was red for a real reason before it was green.** The arm flag was created but not
tracked, and `hooks_armed.py` said so in the words it was built to say:

```
[WARN ] MERGE-TARGET-ENFORCE exists but is UNTRACKED — it arms this clone only and
        reaches no other machine. Remedy: git add .agents/scripts/git-hooks/MERGE-TARGET-ENFORCE
```

### A6 · six fixtures, both halves, every check red first

52 cases. **The ALLOW half outnumbers the REFUSE half on purpose** — A, C, D, D2, H, I, I2, M, N,
N2, O are negative controls. The expensive failure here is the false red: a gate that blocks a
correct merge gets routed around, and this repo has shipped four of those.

### A7 · the three folds

`Step 3` scratch-file dump · `4b` the `[sop-ok]` sentence (with the answer the open question needed)
· `4b` the worked re-measurement stamp · plus one line at `4d`. Doors regenerated with
`/smh-sync-agents`; only the opencode mirror is a full copy, the other three read the body live.

### A8 · the gate, bare, at `89aa410`

```
python3 .agents/scripts/tests/run_all.py                     -> 22/22 files, 1754/1754 cases, exit 0
python3 .agents/scripts/workflow_lint.py --toolkit-only      -> 0 errors, 0 warnings, 8 info, exit 0
python3 .agents/scripts/check_maps.py --depth3-only --strict -> exit 0
```

**Case total exactly additive: 1702 (main) + 52 (this lane) = 1754.** One new file, no displaced
coverage.

⚠ The doc gate went red once, on this lane's **own prose**: `T9 every prose path reference resolves`
rejected a backticked `.git/MERGE_HEAD`, because T9 resolves code-span paths against disk and, inside
a worktree, that path does not exist. Rewritten without code spans — those are git internals, not
repo paths a reader should click. The linter disagreeing with the author about what counts as a path
is the check working.

### A9 · a merge inside a worktree is exempt, exactly as it is in the shared checkout

Operator ruling ("we dont want blind spots"). Both `commit-msg` gates carve merges out via
`[ -f .git/MERGE_HEAD ]`, and **in a worktree `.git` is a file**, so that probe is always false —
live in the shared checkout, dead in every lane. **RED**, both gates, with the control that proves
the worktree is the only variable:

```
[PASS] F-D · jira: a merge in the SHARED CHECKOUT is exempt
[PASS] F-D · jira: .git in that worktree really is a FILE
[FAIL] F-D · jira: the SAME merge inside a WORKTREE is exempt too
[FAIL] F-D · sop:  the SAME merge inside a WORKTREE is exempt too
-- 48/50 passed --
```

**GREEN** at 50/50, with `an ORDINARY commit in the worktree is still REFUSED` holding — the fix
exempts merges, it does not disarm the gate.

---

## Mutation

14 mutants declared up front in one sweep, applied one at a time, each restored before the next.

| Killed by | Mutant |
|---|---|
| B | `chore:chore` judged allow — the SCC-97 signature stops being refused |
| B | target read from a literal instead of `rev-parse` — **the SCC-97 mistake itself, in the guard** |
| B | the `commit-msg` call site deleted — the guard exists and is never invoked (SCC-128's regression) |
| M | any-REFUSE-wins — the ambiguity rule inverts into a false red |
| J | `ENFORCE` ignored — a disarmed gate still blocks |
| N / N2 | the declined-to-judge lines removed — the designed hole stops announcing itself |
| H | the backstop's landed-check dropped — every lane that absorbed `main` is refused |
| I / I2 | `main` no longer exempt — the shipping path is refused on every close-out |
| O | no-`origin/main` becomes a refusal — the vacuous red |
| P | gate 2 starved of stdin — the token gate reads EOF and allows every push to `main` |
| G | gate 1 starved of stdin — the backstop reads EOF and allows every contaminated lane |
| F-D ×2 | either carve-out reverted to the literal `.git` path |

⛔ **One mutant survived the first sweep, and the mutant was what was wrong.** `M3` replaced one
`echo` of a two-line message with `: #`, which comments out the rest of *that* line only — the second
line still printed the word the case asserts, so the case passed, correctly. Re-aimed at the whole
block, it kills. **And re-aiming it exposed a path with no case at all**: a merge of a commit that no
branch points at, where `--points-at` returns nothing and git's own `Merge commit '<sha>'` message
does not match the `Merge branch 'x'` fallback either. That is now case **N2**, and it was found by
the mutation pass rather than by review.

---

## Deviations from the ticket, and why

1. **`pre-merge-commit` → `commit-msg`.** The ticket's build spec is unimplementable: the hook fires
   before `MERGE_HEAD` exists and never fires on the conflicted path. Measured in a real repo, both
   paths traced. The ACCEPTANCE is satisfied — the refusal is by mechanism, one step later, and no
   weaker.
2. **`.agents/rules/git-branch-model-standard.md` does not exist.** The law lives in
   `.agents/rules/git-policy.md` §Branch model, which is what the hook cites.
3. **The `[sop-ok]` open question had a false premise.** The carve-out exists; it is in the
   dispatcher shims, not in `.githooks/commit-msg` or `sop_currency.py`. The 2026-08-13 merges were
   skipped by design. Answering it is what found F-D.
4. **One line added at `4d`** beyond the three folds — the step whose manual assertion this ticket
   mechanises, told that a machine now holds it too.

---

## Your Actions

- **Review and close out** — `/smh-close-task-merge-tree`. Invoking it is the merge sign-off.
- **⚠ Arm the gate on the other machine.** `core.hooksPath` is per-machine and git never carries it.
  This lane adds a gate to a hook that is already armed here, so nothing new is owed on this box —
  but on the PC, `git config core.hooksPath .githooks` is still what makes any of it run.
- **Not done, deliberately:** propagating these hooks to `Projects/*`. The branch model is shared;
  the enforcement is repo-local by law, and each repo needs its own ticket key.
