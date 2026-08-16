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

## What shipped (R4) — a deletion, not an addition

The operator set three constraints after R3 was built and audited: **not per machine** · **no
changing the rules for the agent** · **must work for all four platforms**. R3's Part C-2 (allow-list
lines in `.claude/settings.local.json`) failed all three, and the agent-self-merge split existed
only because of it. So R4 removed everything that failed a constraint and kept the road that had
already worked, with the rules exactly as they are — the one that landed PR #5, #6 and #8.

| | |
|---|---|
| **The road** | close-out Steps 0–2.5 unchanged → `gh pr create --base main --head <branch> --fill` → **print the URL, STOP** → *the operator clicks Merge* → `--after-merge <KEY>` verifies with plain git, then Dev Record, ticket, prune |
| **The gate** | `main-write-gate` on the PR — GitHub refuses the merge button until it is green, for every PR, from every machine, opened by any agent |
| **The sign-off** | the click. Not a token, not "invoking the command", not an inferred approval |

**Deleted:** `land_pr.py` (470 lines) · `test_land_pr.py` (69 cases) · the mutation sweep table and
result · the `scripts/INDEX.md` row · `## Break-glass` from both doors (~60 lines each) · the
self-merge split and its `merge_eligible` / `is_prose` predicate · "three roads" from `git-policy.md`
· the break-glass blocks in the SOP and `jira_manual.md`.

**Kept:** the two door bodies' PR-default shape and `--after-merge`, both server-side settings, and
the law/SOP updates — rewritten for one road.

### Why deleting was right, check by check

Every refusal `land_pr.py` performed was already held somewhere that works everywhere:

| It checked | Already held by |
|---|---|
| not a git repo | close-out Step 0 (`rev-parse --show-toplevel`) |
| branch shape · wrong Jira key | the `commit-msg` hook, and `main-write-gate` on the PR — **server-side** |
| dirty tree | `task_preflight.py` Step 1: clean **and** pushed |
| nothing to land | `gh pr create` refuses; the compare page says "nothing to compare" |
| diverged branch | `git push` refuses a non-fast-forward; force is banned |
| `gh` missing | the compare URL is printed instead — so **`gh` is now optional**, which it was not before |
| an existing PR | `gh pr create` prints the existing URL |
| stale base | `strict_required_status_checks_policy` — server-side, every path, every machine |
| merge shape | squash/rebase disabled — a repo setting |
| eligibility, polling, pre-merge ancestry | **nothing — the agent never merges** |

### And the break-glass road could never have done its job

I kept it "for when GitHub is down". Measured against its own contents: it pushes to
`gate/main-<sha>` (**needs github.com**), waits on `main-write-gate` via `gh api` (**needs Actions
and `gh`**), then mints a token and pushes. That is a strict **superset** of the PR door's
dependencies — there is no outage in which break-glass works and the PR door does not. It was
error handling for a state that cannot occur: the same tripwire this lane cut twice elsewhere,
shipped in the same lane.

### One more thing the constraints fixed

R3 relied on the agent merging prose lanes, which needed the allow-list, which is **gitignored**
(`.gitignore:56`). Measured while checking: the tracked `.claude/settings.json` has **no `allow`
list at all** — so no permission grant on this machine has ever travelled to the other one. That is
a pre-existing property of the system, surfaced by asking the cross-machine question, and it is why
"the fix needs an allow-list entry" can never be the right shape here.

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

**And the R4 answer is better than a fifth attempt: the question is gone.** No agent merges, so
nothing has to decide which files are safe to land unread. Four cuts, two CRITICALs and a mutation
table went into getting a predicate right that R4 deletes entirely. ⭐ **The lesson worth keeping is
the technique, not the predicate**: the fourth appearance was found by *running the rule over
`git ls-files`* instead of reading it, after two careful audits had read it and passed it. Any future
rule about which files are safe to treat differently should be enumerated against the repo on day one.

## Evidence

| Gate | Result |
|---|---|
| `run_all.py` | **32/32 files**, exit 0, run **bare** (33 before — `test_land_pr.py` was deleted with the script it tested) |
| `test_door_preflight_order.py` | **15/15** — the lobby door is now checked by **absence** (no mint, no `git push origin main`, no `gate/**` ref) plus the presence of `gh pr create` |
| `workflow_lint.py --toolkit-only` | 0 errors, 0 warnings |
| `check_maps.py --depth3-only --strict` | clean |
| AC-3 — no permission surface touched | `git diff origin/main -- .claude/settings*.json .claude/hooks` = **0 lines** |
| AC-3b — `.claude/` changes | exactly the two generated `skills/*/SKILL.md` launchers |
| AC-4 — deletions complete | `git grep -c 'land_pr\|merge_eligible\|is_prose' -- .agents docs` = **0** |

⛔ **Two ACs I wrote were sloppy and were corrected rather than fudged into a pass.** AC-3 originally
said *"zero files under `.claude/` in the diff"* — impossible, because the two door launchers under
`.claude/skills/` are **generated from the command's frontmatter** and must move with it. What I
actually meant, and what is now asserted, is that no **permission** surface is touched. AC-3c
originally grepped for the string `allow-list` and expected zero; the one hit is the paragraph in
`git-policy.md` **recording that such an edit was refused**, which is the opposite of requiring one.
A grep counts mentions, not requirements.

### Ten door surfaces, kept in agreement

Two commands × five surfaces each — `.agents/commands` (the brain), `.opencode/commands` (a
byte-identical mirror), `.agents/workflows` (Antigravity), and `.claude/skills` + `.agents/skills`
(generated launchers). The launchers copy the brain's `description:` **verbatim** and
`is_launcher_for()` compares exactly that, so a frontmatter edit and its regeneration are **one
commit** or all doors flip to `badlauncher`. `test_command_surfaces.py` is what caught the fifth
surface existing at all.

⛔ **AC-14b is the check that structural agreement cannot make.** All ten surfaces are generated from
one source, so **ten consistent copies of a false sentence agree perfectly.** They all said
*"merges to `main` with `--no-ff` … invoking it IS the merge sign-off"*, which R4 makes false twice
over. A named-string assertion catches that; a consistency check never can.

### What the ORDER check could not have caught, kept as a control

`test_door_preflight_order.py` pins the token ceremony's order — and that ordering still binds
`/cicd-push-e2e`, which ships project epics and still merges locally. But relocating a ceremony
leaves every needle present and in order, so the order check **stays green while certifying a road
the door no longer takes**. `MUTANT_CEREMONY_IS_STILL_DEFAULT` pins exactly that: it passes the
order check and is caught only by checking the section. All three original negative controls, the
`--delete` assertion and the `PROJECT_DOOR` guard survive unchanged.

### Bugs found by running rather than reading (R3, kept as record)

The R3 build is deleted, but three of its findings are about this repo, not about that script:

1. **`norm()` written as `lstrip("./")`** — it takes a character *set*, so it ate the leading dot off
   every `.agents/` and `.claude/` path, and `lane_qualify` stopped seeing them as toolkit paths.
   This repo has now shipped that exact bug **three times**; `lane_qualify.norm`'s docstring exists
   because of the second one.
2. **A fence-blind section reader** — `# ── Pre-flight …` inside a ```bash block is a shell comment,
   but as markdown it is an `<h1>`. Same family as `comment-literals-invert-source-grep-tests`.
3. **An unreachable guard** — proved dead because a mutation of it killed nothing.

## The operator's acts — two, both server-side

1. `gh repo edit --enable-squash-merge=false --enable-rebase-merge=false` — **both are ON**
   (measured). Either rewrites the commit, which would also break `--after-merge`'s
   `merge-base --is-ancestor` verification.
2. `strict_required_status_checks_policy: true` on ruleset `20756052` — closes the stale-PR window
   on the click path. **A yes/no that needs the operator's own words**, because it can block a
   shipping path.

Both apply to both machines and all four platforms at once, and neither touches any agent's
permissions. **Nothing else is owed, on any machine.**

## Close-out checklist

- [x] The merge itself — lands via this branch's PR

## Limits

- **Not yet exercised end to end.** The road is `gh pr create` → click → `--after-merge`, and this
  lane's own landing is its first real run. That is deliberate: the door is tested by using it.
- **`--after-merge` reads the PR number off `origin/main`'s merge subject** (`Merge pull request #N
  from …`). That is GitHub's format for a merge-commit merge; it is exactly why squash and rebase
  must be off, and act #1 is what makes it true.
- **The local token gate still exists** (`.githooks/pre-push`, the minter, `MAIN-PUSH-ENFORCE`) and
  no `smh-` door uses it any more. In this repo the server ruleset already refuses an unchecked push
  to `main`, so it is a second refusal on the same act — redundant, not harmful. Retiring it is a
  **follow-on**, with a real blast radius: `hooks_armed.py`, `task_preflight.py`, four test files,
  and `/cicd-push-e2e`, which still needs it for project repos.
- **Project repos are unchanged** and still ship through `/cicd-push-e2e` with the token. Porting
  the PR door to them is each project's own ticket (AVCH-63).

---

**Verdict: PASS @ 3150732d** — builder's self-review. R4 is a deletion whose safety argument
is a table of what already holds each removed check, and the suite, lint and maps are green after
it. ⛔ Not an independent review: `/smh-code-review` is available and is the thing that has
historically caught what a builder's own pass did not — twice on this lane.
