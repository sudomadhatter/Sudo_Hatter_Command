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
- [x] **Step 4** — `/smh-code-review` — **5/5 lenses, PASS @ `30f93aa` after fixes**
  - ⛔ It found a **critical** defect the builder did not: the backstop refused every legitimate
        `claude/*` story-lane push once a sibling had landed on the shared epic — `/cicd-park`'s
        exact sequence, on a push `git-policy.md` marks FREE. Three lenses, two reproductions.
  - ⚠ Four more real defects: octopus merges judged on the first parent only, `--squash` invisible
        to both halves, `pre-push` failing **open** and skipping the token gate, and a Windows path
        corruption in a worktree.
  - ⚠ Seven of eight refusal cells were undefended, and the guard had never been run in a worktree.
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

90 cases. **The ALLOW half outnumbers the REFUSE half on purpose** — A, C, D, D2, H, I, I2, M, N,
N2, O are negative controls. The expensive failure here is the false red: a gate that blocks a
correct merge gets routed around, and this repo has shipped four of those.

### A7 · the three folds

`Step 3` scratch-file dump · `4b` the `[sop-ok]` sentence (with the answer the open question needed)
· `4b` the worked re-measurement stamp · plus one line at `4d`. Doors regenerated with
`/smh-sync-agents`; only the opencode mirror is a full copy, the other three read the body live.

### A8 · the gate, bare, at `30f93aa`

⚠ **REPLACED after the review.** The pre-review stamp read `1754 @ 89aa410`; the fixes added 38
cases and moved the sha, so that pair is void by this repo's own (totals, SHA) contract.

```
python3 .agents/scripts/tests/run_all.py                     -> 22/22 files, 1794/1794 cases, exit 0
python3 .agents/scripts/workflow_lint.py --toolkit-only      -> 0 errors, 0 warnings, 8 info, exit 0
python3 .agents/scripts/check_maps.py --depth3-only --strict -> exit 0
```

**Case total exactly additive: 1702 (main) + 92 (this lane) = 1794.** One new file, no displaced
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

## Code Review (2026-08-13)

```
Verdict: PASS @ 30f93aa
```

Gate evidence measured at **`30f93aa`** — the landing sha, after every fix below.

- **Scope:** 19 files, `main...HEAD`, committed work only. `main` had not moved since the lane was
  cut (`BASE == main == 5dadcd6`), so no reference this diff depends on was relocated under it.
- **Method:** `code-review-engine`, `review_mode: full`. **5/5 lenses ran** (Blind Hunter,
  Literal-Correctness, Edge Case, Acceptance Auditor, Test-Adequacy Auditor), each in its own clean
  context, `lenses_na: none`, no degradation. Two lenses reproduced their headline finding
  end-to-end against a real bare remote rather than reasoning about it.

**The review changed the outcome of this lane.** It found a critical defect the builder did not,
plus four more real ones. Everything below is `applied`.

| file:line | sev | failure scenario | disposition |
|---|---|---|---|
| `pre-push-merge-backstop.sh` (landed-check) | **critical** | A `claude/*` story lane that absorbed its epic after a sibling landed on that epic was **REFUSED at push**. "Already landed" was measured against `origin/main` only, and an epic does not reach `main` until `/cicd-push-e2e` ships it. `/cicd-park` performs that exact sequence and `git-policy.md` marks the push **FREE**. Found by 3 lenses, reproduced by 2. | **applied** — reference set is per-class (`origin/main`, plus every `origin/epic/*` for a story lane); controls `PARK` and `G2` |
| `pre-push-merge-backstop.sh` `refuse()` | important | The remedy named `origin/<lane>`, which does not exist on a first push, and said "land it on main first" — the one thing the guard **refuses** for a story lane | **applied** — `integration_of()`, per-class remedy |
| `merge-target-guard.sh` (source resolution) | important | **Octopus merge:** both `rev-parse MERGE_HEAD` forms return only the *first* parent, exiting 0 rather than failing. `git merge main <sibling>` was judged on `main`, allowed, and sealed an illegal later parent — position-dependently | **applied** — reads the MERGE_HEAD *file* via `--git-path`; case `OCT` |
| `merge-target-guard.sh` (source resolution) | important | **`git merge --squash`** writes no `MERGE_HEAD` and rewrites history, so the source is not an ancestor either — invisible to **both** halves, while the backstop's header claimed exactly one blind spot | **applied** — recovered from `SQUASH_MSG`; case `SQ` |
| `.githooks/pre-push:47` | important | `cat > "$REFS" \|\| exit 0` **failed open**, skipping both gates including the SCC-77 token gate, printing nothing | **applied** — fails closed, names the remedy and the override |
| `.githooks/pre-push` (path normalisation) | important | `--git-path` is absolute in a worktree; the hand-rolled `case "$REFS" in /*)` is correct on POSIX and wrong on git-for-windows, where `C:/…` fails that test and the repo root was prepended to an absolute path — **in a worktree, on the PC** | **applied** — `cd "$ROOT"`, git's answer used as given |
| `test_git_hooks.py` (arm flag) | suggestion | `the arm flag is tracked` asserted `Path.is_file()` — existence, not the index. The untracked state it names is the one this lane was actually in | **applied** — `git ls-files --error-unmatch` |
| `merge-target-guard.sh` `judge()` | important | **Seven of eight refusal cells were undefended** — a sweep flipped them to `allow` with the suite green; only `chore:chore` had a case | **applied** — every refusing cell + three shipping-path ALLOW cells, each asserting *classified, not declined* |
| `merge-target-guard.sh` | important | The guard was **never run inside a worktree** — where every lane lives. Mutants reverting it to the literal `.git/` probes survived | **applied** — case `WT` |
| `test_hooks_armed.py` `seed()`, case R | important | The `ARM_FLAGS` row existed while the five vacuous-ARMED shapes never exercised it (A5's promised assertion) | **applied** |
| `pre-push-merge-backstop.sh` | important | `DISABLE`, the disarmed path, and the whole `claude/*` half it names in its own pattern had no case | **applied** — `G3`, `G4`, `G5` |
| `.githooks/commit-msg:29` | nitpick | The missing-guard warning claimed "merge allowed" on **every ordinary commit** | **applied** |
| `.agents/scripts/INDEX.md:52` | nitpick | Said 21 files / 1091 cases while this diff makes it 22 — and the diff already edits that file | **applied** — 22 / 1794 |
| folds oversized vs "ONE LINE" | suggestion | +45 lines against a 3-line spec | **dismissed with reason** — the extra length in fold 1 *is* the answer to the open question the ticket ordered determined; fold 3's template is the "worked example" asked for |
| SOP §10 mermaid node | suggestion | The plan listed it; not added | **deferred** — `pre-push-main-approval.sh` is absent from that diagram too, so adding one gate alone would misrepresent the set. Its own ticket |

**Two fixture bugs and one self-inflicted regression, all caught by cases going red, all recorded**
rather than quietly fixed: a `before` sha captured while HEAD was still on the source branch; an
absorb fixture whose epic never moved, so the merge was *Already up to date* and proved nothing; and
the renamed-refspec fix skipped by **sha**, which silently deleted the primary fast-forward case,
because a contaminated lane sits at exactly the foreign lane's tip. Case `G` caught that one.

⛔ **Mutation residue was found on a live gate before it could be committed.** A `timeout`-killed
sweep left `commit-msg-jira.sh` reverted to the worktree-blind `.git/MERGE_HEAD` probe — this
lane's own bug, sitting on disk, uncommitted. Restored, re-gated, and it is the reason the harness
needs restore-on-interrupt. **See `Your Actions`.**

### Gates

| Gate | Result |
|---|---|
| Enforcement suite | `run_all.py` → **22/22 files, 1794/1794 cases, exit 0** |
| Toolkit lint | `workflow_lint.py --toolkit-only` → **0 errors, 0 warnings, 8 info, exit 0** |
| Map/INDEX | `check_maps.py --depth3-only --strict` → **exit 0** |
| Assertion evidence | every Step 2 RED is GREEN; RED artifacts committed beside this file |
| SOP currency | the three usage-surface commits each staged the SOP doc; the doc-only commits carry `[sop-ok]` |
| Link + anchor | `test_sops_prds_folder.py` T9 — went **red on this lane's own prose** and was fixed |
| Door parity | `test_command_surfaces.py` green after `/smh-sync-agents` |

**Case total additive:** 1702 (main) + 92 (this lane) = **1794**.

### Step 0.7 — re-derivation against current `main`

1. **Nothing moved.** `main` is still `5dadcd6`; `BASE == main`, so no reference this diff names was
   relocated, renamed or deleted while it was built.
2. **True overlap with `main`: none.** `merge-tree` produced a clean tree, no conflict messages.
3. **Sibling lane `chore/SCC-129-gate-the-gate` is live and now has commits.** Overlap is exactly
   the three shared files every lane touches — `.agents/scripts/INDEX.md`, `_artifacts/_main/INDEX.md`,
   `docs/_scc_sops_prds/workflows_testing_SOP.md`. All append-shaped. **Landing order: either.**
   Whoever lands second absorbs `main` and re-gates; the `check_maps` missing-row gate catches a
   dropped ledger row, as it did on 2026-08-13.

### Clean-Code Gate

The command-centre machine floor is the three gates above, and all three are green at `30f93aa`.
Judgment pass: the two new scripts follow the house shape exactly (POSIX `sh`, dumb dispatcher,
`*-ENFORCE` flag, `DISABLE` kill switch, `hooks_armed` row, `--no-verify` documented in-file). No
`|| true`, no report-only step, no unowned TODO. Comment density is high and deliberately so —
every non-obvious decision carries the measurement or the incident behind it, which is this repo's
own convention.

## Your Actions

- **Review and close out** — `/smh-close-task-merge-tree`. Invoking it is the merge sign-off.
- **⛔ File the mutation-harness ticket (operator has one open).** Two separate failures in this lane
  came from the same absence: **there is no mutation procedure anywhere in the command surface.**
  `grep -rn "mutant\|mutation" .agents/commands/` returns **one** hit, and it is Lynn Margulis in the
  adviser board. The entire doctrine is a single sentence buried as the fifth sub-bullet of Rule 4 in
  `tests-must-gate-for-real.md` (a rule headlined about certification SHAs), it never names the
  practice, and the one technique it gives — *relocate, never delete* — is shape-specific to a
  structural-guard-plus-behavioural-test pair and does not transfer to a gate, where the useful
  mutant **inverts a decision**. Worse, `/smh-quick-dev` and `/smh-self-audit` — the commands that
  *write* the assertions — do not load that rule at all; only `/smh-code-review`, which runs after
  the mutants are already designed. Three concrete fixes, cheapest first:
  1. Add `tests-must-gate-for-real.md` to `/smh-quick-dev`'s and `/smh-self-audit`'s rules-in-force.
  2. A Step 3 bullet: *declare the mutant table before mutating — each mutant, the file, and the
     named case it must kill. Run them in one sweep. A **surviving** mutant is a finding; a mutant
     that kills **nothing** is a **defective mutant** and must be re-aimed before it is believed.*
     That check is what hand-running structurally cannot do, and it is what cost this lane two
     re-runs.
  3. **Restore-on-interrupt.** A `timeout`-killed sweep left a mutated gate on disk in this very
     lane. The harness must restore in a `finally`/signal handler, and a sweep should refuse to
     start against a dirty tree.
  4. The review's own finding on top: *the mutant set was drawn from the cases rather than from the
     code* — 24 of 25 code-derived mutants survived the 14 that were case-derived. That is
     `prose-pinning-guards-are-vacuous` recurring one level up, inside the mutation pass.
- **⚠ Arm the gate on the PC.** `core.hooksPath` is per-machine and git never carries it.
- **⚠ Arm the gate on the other machine.** `core.hooksPath` is per-machine and git never carries it.
  This lane adds a gate to a hook that is already armed here, so nothing new is owed on this box —
  but on the PC, `git config core.hooksPath .githooks` is still what makes any of it run.
- **Not done, deliberately:** propagating these hooks to `Projects/*`. The branch model is shared;
  the enforcement is repo-local by law, and each repo needs its own ticket key.
