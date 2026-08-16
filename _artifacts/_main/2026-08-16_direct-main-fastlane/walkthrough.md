# Walkthrough — SCC-183 · The PR door

**What changed, in one line:** landing a lane on `main` is now one command that prints a link and
one click, instead of ~15 hand-typed strings that the agent's permission layer could not run.

---

## The problem, restated from measurement

SCC-184 was docs-only — 226 lines added, 0 deleted, suite 32/32 — and it did **not** reach `main`
in a full session. Every gate passed. What failed was `/smh-close-task-merge-tree` **Step 3**.

| Measured | Result |
|---|---|
| Controlled pair, same op, same target | `git merge X --no-ff` **allowed** · `git -C <path> merge X --no-ff` **DENIED** |
| Who mandates `-C` | `.agents/rules/nothing-guards-the-merge-target.md` — on **every** git call |
| How the allow-list is written | bare `Bash(git merge *)`, no `-C` form |
| The shared checkout at that moment | held dirty by another session; the stash was denied too |
| The documented workaround (landing worktree at `origin/main`) | refused by our own minter: `HEAD is 'HEAD', not 'main'` |
| `gh pr merge` | denied by the **risk classifier**, not the allow-list — so adding allow-list patterns never converges |
| PR #5, #6, #8 | all **merged**, `main-write-gate` green in ~45 s, **zero** denials |

**Obeying the safety law guaranteed the permission miss.** No gate could fix that, because no gate
was the problem — the *shape* was: many strings, shared tree. The road that already worked was a
pull request.

## What was built

| Part | What | State |
|---|---|---|
| **A** | `.agents/scripts/land_pr.py` + `test_land_pr.py` (69 cases) | ✅ `05161be` |
| **B** | both close-out doors split into PR-default + `## Break-glass`; five surfaces each | ✅ `f0c9e48` |
| **C** | the operator's one-time acts | ⏸ **owed — see below** |
| **D** | `git-policy.md`, the SOP, `jira_manual.md`, the ticket description | ✅ `05161be` / `f0c9e48` + Jira |
| **E** | retire R1's `--direct` token push | ✅ `7858710` / `a280117` |

### The check order, and why it is that order

`R1` repo → `R2` branch shape → `R3` jira key → `R4` dirty tree → **`R7` gh** → **`P` PR state** →
`R5` nothing-to-land → `R6` diverged → **freshness** → push/create → `R8` eligibility.

⛔ **`R7` moved ahead of `P` during the build.** The plan had `P` earlier, but `P` is the first check
that calls `gh` — so a missing `gh` would have produced a raw subprocess error instead of the
install/login hint `R7` exists to give. Found by running it, not by reading it.

### `merge_eligible` — two predicates, either alone sufficient to refuse

```
lane_qualify says LIGHT   AND   every changed path is prose
```

Measured, and the whole reason the second predicate exists: `lane_qualify` rates
`.claude/hooks/require-push-approval.py` — the agent's own permission hook — **`LIGHT`**.

`is_prose` evaluates **refusals first**, and precedence is load-bearing (a path like
`docs/CLAUDE.md` matches both an allow arm and a refusal).

## ⛔ The defect this lane kept re-learning — four appearances

Every cut shipped a rule about *which files are safe to land unread*, and every one was wrong the
same way: **written from what the author had in mind rather than from what `git ls-files` returns.**

| # | Where | What it would have auto-landed | Caught by |
|---|---|---|---|
| 1 | R1 | `docs/**` declared "a prose tree" | code review → **FAIL** |
| 2 | R3 cut 1 | `lane_qualify` alone ⇒ the agent's own permission hook | self-audit **F1 (CRITICAL)** |
| 3 | R3 cut 2 | the **nine** per-folder `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` front doors | re-audit **N1 (CRITICAL)** |
| 4 | R3 cut 3 | root **`router.md`** — the MASTER ROUTER | **running the predicate over the repo** |

The fourth survived the audit that killed the third, because that audit was hunting the prefix arm
and `router.md` was an exact-path arm. It was found by a twenty-line probe that ran the predicate
against all 3,235 tracked files and asked what came back.

**So the fix is not another rule.** `AC-4` is now a property test over the real repo — no root file,
no front door, no non-`.md`, nothing outside the three roots — and every refusal must kill a mutant.

## Evidence

| Gate | Result |
|---|---|
| `test_land_pr.py` | **69/69**, RED first (import error before the module existed) |
| `test_door_preflight_order.py` | **22/22**, RED first (13 failures against the un-edited door) |
| `run_all.py` | **33/33 files**, exit 0, run **bare** — a piped gate reports `tail`'s exit code |
| `mutation_sweep.py` (15 declared mutants) | **15/15 KILLED**, restore verified byte-identical |
| `workflow_lint.py --toolkit-only` | 0 errors, 0 warnings |
| `check_maps.py --depth3-only --strict` | clean |

Sweep table and result: [`mutation-sweep.json`](mutation-sweep.json) ·
[`mutation-sweep-result.txt`](mutation-sweep-result.txt).

### Three bugs the build found that reading had not

1. **`norm()` written as `lstrip("./")`.** It takes a character *set*, so it ate the leading dot off
   every `.agents/` and `.claude/` path — `lane_qualify` then stopped classifying them as toolkit,
   rated them `LIGHT`, and **half of `merge_eligible` was silently switched off while the suite
   stayed green.** This repo has now shipped that exact bug three times; `lane_qualify.norm`'s
   docstring exists because of the second. Fixed by importing it rather than writing a fourth.
2. **`section()` read shell comments as markdown headings.** The break-glass block opens with
   `# ── Pre-flight the SERVER-SIDE gate …`, which as markdown is an `<h1>` — so extraction stopped
   two lines in and every break-glass assertion reported the ceremony *missing* on a door that had
   just been written correctly. Same family as `comment-literals-invert-source-grep-tests`.
3. **An unreachable guard, proved dead by the sweep.** `if "/" not in p` killed no mutant: no root
   path can start with `docs/`, so the allow arm already refused `router.md`. The real fix was
   deleting `router.md`'s allow arm. Cut, with the property test kept.

### What the ORDER check could not have caught

Relocating the whole token ceremony under `## Break-glass` leaves every needle present and in
order, so `REQUIRED_ORDER` **stays green while certifying a road the door no longer takes**. A
control pins exactly that: `MUTANT_CEREMONY_IS_STILL_DEFAULT` passes the old check and is caught
only by the section split. All three original negative controls, the `--delete` assertion, the
flight-recorder ordering and the `PROJECT_DOOR` case survive unchanged (AC-10 / N15).

`AC-14b` is the sibling of the same idea: the five door surfaces are generated from one source, so
**four consistent copies of a false sentence agree perfectly.** AC-14 structurally cannot catch it;
a named-string check can.

## ⏸ Part C — owed by the operator, and the lane is honest about it

1. `gh repo edit --enable-squash-merge=false --enable-rebase-merge=false` — both are **ON** today
   (measured). Either would put a single-parent commit on `main`.
2. Allow-list lines in `.claude/settings.local.json`:
   `Bash(python3 .agents/scripts/land_pr.py *)`, `Bash(gh pr create *)`, `Bash(gh pr view *)`,
   `Bash(gh pr list *)`. ⛔ **Not** a bare `Bash(gh pr *)` — that is a superset of
   `gh pr merge --merge` and would hand every future session an unconditional merge that bypasses
   `merge_eligible` entirely.
3. **Decide `strict_required_status_checks_policy`** (currently `false`). Setting it `true` closes
   the stale-PR window on the **click** path, which `land_pr.py` cannot reach. Recommended, and it
   needs the operator's own words because it can block a shipping path.

## ⚠ Declared narrowing — a proposal, not the ruling

The ruling was *"doc / index / memory / maps lanes → the agent merges."* This door is **narrower**:
`.agents/` rules and toolkit `INDEX.md` files still need a click. Measured against real lanes —
PR #5 (maps) ✅ allowed, PR #8 (memory) ✅ allowed, **PR #6 (SCC-184) ⛔ refused**, because it
touched `.agents/rules/git-policy.md`. Narrower is the safe direction, but presenting it *as* the
ruling would not be: a derived corollary is a proposal, never law.

## What is NOT in this lane

- The port to project repos (**AVCH-63**) — its own repo, its own ticket, after this lands.
- Deleting the local token door — kept as break-glass.
- Widening the prose set — the operator's call.

## Limits

- **`land_pr.py` has never run against real GitHub.** Every test uses an injected `gh` recorder and
  scratch repos; the one live assertion (`AC-12`, merge-method) is `@live`-guarded and skips
  offline. The first real invocation is this lane's own landing, which is the correct first test.
- **⚠ UNVERIFIED — whether subprocess `gh`/`git` calls are visible to the permission layer.** Never
  measured, and the design deliberately does not depend on it: routing around the operator's own
  control of the agent is not something this lane will do.
- The `--after-merge` resume path is written into both doors but has not been exercised end to end;
  it will be, by this lane.

---

**Verdict: PASS @ 1149640c** — builder's self-review. The measured evidence behind it is the
suite (33/33), the RED-first sequence on both test files, and the 15/15 mutation sweep with restore
verified; the three defects listed above were found by *running* rather than reading, and are fixed
with tests that kill their mutants. ⛔ It is **not** an independent review: an independent pass
(`/smh-code-review`) is available and is the one thing that has historically caught what a builder's
own pass did not — twice on this very lane.
