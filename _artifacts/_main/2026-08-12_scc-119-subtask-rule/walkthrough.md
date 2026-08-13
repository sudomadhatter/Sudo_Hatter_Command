---
type: walkthrough
task: SCC-119
branch: chore/SCC-119-subtask-rule
---

# SCC-119 — Subtasks: the ticket you were handed is the top-level one

**What changed, in one line:** work an agent breaks out of a ticket now goes **underneath it as
`Subtask`s** instead of beside it as more `Task`s — and the five places in the toolkit that actively
refused subtasks were fixed, including one that was corrupting the board on every commit.

## Task Checklist

- [x] **The rule** — `.agents/rules/jira.md` §Subtasks: hierarchy (three levels, no nesting), the
      parent's-type discriminator, the one test, the branch+worktree threshold, the mint seam, the
      lifecycle. Plus the `Subtask` row in the five-types table and the close-out routing table.
- [x] **`jira_feed.py start`** — the `Subtask` refusal **deleted**. This was the live defect.
  - ⚠️ It also made `have` unused; removed rather than left dangling. `start` now gates on **status
    alone**, which is correct: every type a keyed branch can carry is startable.
- [x] **`jira_feed.py flag`** — `Epic` and `Subtask` refusals **split**. A subtask still refuses, but
      the reason is now true and the refusal **names the parent to flag instead**.
  - ⚠️ The old message argued against itself: it called a subtask "a container" (it is a leaf) and
    then said *"flag the child ticket whose work broke"* — which is the ticket it had just refused.
- [x] **`jira_feed.py audit`** — subtasks are no longer skipped as "containers". `check_subtask()`
      checks **placement**: no parent · parented to an `Epic` · nested under another subtask · a
      parent lagging its children. **None auto-fixed** — re-parenting is a board move.
  - ⚠️ `print_human` was **hoisted out of the branches**: the `--apply` path never printed the
    report, so placement findings would have been invisible on exactly the run an operator makes
    when they intend to fix the board.
- [x] **`task_preflight.py check_children()`** — a parent cannot close while a child is open.
      `Deferred` is the escape hatch. First network call this script has ever made.
- [x] **Command bodies** — `/smh-quick-dev` Step 1.6 (propose-then-stop) and the deleted exit-2 row;
      `/smh-close-task-merge-tree` re-checks children with the board in hand before writing `Done`.
- [x] **`scripts/INDEX.md`** — three sentences this change made false, corrected.
- [x] **SOP** + **8 platform doors** regenerated via `sync-agents`.
- [x] **Review fix (R1)** — `test_hooks_armed.py` was quietly querying the **live Jira board**.
  - ⚠️ `task_preflight.py` gained its **first ever network call** in this ticket, and that test runs
    the preflight to check something unrelated (the arm-state seam). It set no `ACLI_BIN`, so acli
    resolved off PATH and hit production: **1.90s per run**, credential-dependent, and up to a **20s
    block** on a dead uplink. The assertions never touched the board, which is precisely why the
    suite stayed green and nothing caught it. Adding a network call to a shared script reaches
    further than the diff that adds it.

### Cut during the build — both are the audit's own tripwires firing on my plan

| Planned | Cut because | Instead |
|---|---|---|
| `devrecord --closing` subtask guard | The restore branch is `if have == "Bug":`, and a subtask never carries `Bug` under the ruling — **the guard defended an unreachable state** (*"error handling for states that cannot occur"*) | **No code.** A characterization test pins that a subtask through `--closing` is not re-typed |
| `mint --parent-key` | `mint` renders a description **from a story file**; a subtask has none. And Tasks are already minted with raw `acli`, never through `mint` — *a flag no acceptance item requires* | The exact `acli` form documented in `jira.md` §Subtasks |

### Deviation from the plan — stated, not slipped in

**Plan §4a.3 said an unreachable board must flip the VERDICT to `NOT CLEAR`. It does not.** It warns.
Sandboxed agent shells cannot reach the OS credential store at all (`jira.md` §top), so blocking there
would have made `NOT CLEAR` the *normal* output of a preflight that has always worked offline — and a
verdict that fires constantly stops being read. The second layer is `/smh-close-task-merge-tree`, which
re-asserts the check immediately before it transitions the ticket, where the board is provably
reachable. Neither layer is load-bearing alone — the same shape as the two `start` seams (SCC-113).

## Evidence

| AC | Proved by | Result |
|---|---|---|
| AC1 rule written | `jira.md` §Subtasks + type/close-out tables | inspection |
| AC2 story lane never | rule text; AVCH still holds **0** subtasks | board-verified |
| AC3 branch+worktree threshold | rule text + `/smh-quick-dev` Step 1.6 | inspection |
| AC4 propose then stop | Step 1.6; no board write in any code path | inspection |
| AC5 subtask lane no longer breaks the board | `test_jira_feed.py` — **L905 inverted**, was `code == 2`, now `code == 0` | 152/152 |
| AC6 parent closes last | `test_task_preflight.py` — open blocks, `Deferred` does not, failed query never reads clean | 100/100 |
| AC7 subtask never `Bug` | `flag` refuses + names the parent; `devrecord` characterization | 152/152 |
| AC8 nothing says stop-on-Subtask | exit-2 row deleted from `smh-quick-dev.md` | inspection |

**Gate, all bare, at the working tree:**

```
run_all.py            21/21 files · 1110/1110 cases   exit 0   (baseline 1091 → +19 new)
workflow_lint.py --toolkit-only   0 errors, 0 warnings, 8 info   exit 0
sop_currency.py       exit 0 WITH the SOP doc · exit 1 WITHOUT (positive control, "Commit rejected")
py_compile            4 changed .py files clean
link + anchor         24 links across 8 changed docs, 0 problems
hooks_armed.py        ARMED — core.hooksPath=.githooks
```

**Mutation evidence — 3/3 killed on the one gate that could have shipped vacuous:**

| Mutant | Killed by |
|---|---|
| unreadable board reads as "no children" | 3 cases |
| `Deferred` no longer counts as closed | 1 case |
| row count instead of exit code | 3 cases |

⚠️ **A false green I caught in my own gate run.** The first two `sop_currency` runs both exited 0 —
including the positive control that was supposed to FAIL. Cause: **zsh does not word-split unquoted
parameter expansions**, so `--paths $POS` passed one newline-containing string that matched no
surface prefix. The gate was fine; my invocation was vacuous. Re-run through `xargs`, it behaves
correctly in both directions. Worth recording because the failure mode is invisible: a gate handed
garbage input reports clean, exactly like a gate handed good input.

## Suite Ledger

| Suite | Before | After |
|---|---|---|
| `test_jira_feed.py` | 141/141 | **152/152** |
| `test_task_preflight.py` | 92/92 | **100/100** |
| `test_hooks_armed.py` | 31/31 | **31/31** (unchanged count — made hermetic, R1) |
| `run_all.py` (all files) | 1091/1091 | **1110/1110** @ `cc553bc` |

## Code Review (2026-08-12)

```
Verdict: CONCERNS @ cc553bc
```

**Suite evidence measured on:** `cc553bc` — the run below post-dates the last code/test change.
Only doc commits follow it.

**Scope:** 16 files, `chore/SCC-119-subtask-rule` (15 from the build + `test_hooks_armed.py` from
this review), after absorbing `origin/main`.
**Method:** ⚠️ **DEGRADED — Step 1's clean-room subagent did not run.** The operator declined the
subagent invocation, so the adversarial hunt was re-run **inline, by the builder**, per the
subagent-failure contract (retry → inline → *record the degradation*). **That is the entire reason
this is CONCERNS and not PASS:** every gate is green and every acceptance item is evidenced, but a
diff hunted by its own author has lost the one property Step 1 exists to provide. The hunt was not
vacuous — it found and fixed a real defect (R1) — but self-review is weaker evidence and must read
as weaker. **Clearing it is one clean-room run away, or the operator's explicit accept.**

### Findings

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| **R1** | `.agents/scripts/tests/test_hooks_armed.py:264` | **CONCERNS** | That test runs `task_preflight.py`, which this ticket gave its **first ever network call** (`check_children`, resolving `acli` off PATH). The test set no `ACLI_BIN`, so **every suite run queried the live Jira board.** Proven: the preflight printed `SCC-119: no subtasks` in **1.90s** — obtainable only from the real board. Cost: a round-trip per run, credential-dependent, divergent on a machine with no acli or a sandboxed shell, and up to a **20s block** on a dead uplink. The assertions never depended on the board, which is exactly why the suite stayed green and nothing caught it. | **applied** @ `cc553bc` — `ACLI_BIN` pinned to a childless stub around that call. Proven hermetic: **31/31 with PATH stripped of acli entirely.** |

**Refuted during the hunt — recorded so they are not re-litigated:**

| Suspicion | Why it is not a finding |
|---|---|
| `os.environ["ACLI_BIN"]` in `test_task_preflight.py` leaks into sibling test files | `run_all.py:26` spawns each file as a **subprocess** (`subprocess.run([sys.executable, …])`). Env cannot cross. |
| `import jira_feed` in `task_preflight.py` is unsafe / cyclic | Import measured at **0.019s**, no module-level side effects, and `jira_feed` imports neither `task_preflight` nor `hooks_armed` — no cycle. |
| `check_children` can pass without checking | Every path traced: acli absent → warn; non-zero exit → `acli_json` returns `None` → warn; malformed JSON → `None` → warn; timeout → `ACLI_UNREACHABLE` → warn. **No path reaches "no open children" without a successful read.** Mutation-proven, 3/3 killed. |
| A doc still claims `start` refuses a Subtask | Swept all four changed docs — every "refuses" hit is `flag` (correct) or the parent gate (correct); `jira.md:431` states ACCEPTED explicitly. |
| Status matching is case- or None-fragile | Verified: `Done/done/DEFERRED` → closed; `Blocking`, `In Review`, `''` → **open (blocks)**. Unknown status fails **safe**. |
| `cmd_audit`'s restructure broke an exit-code contract | Traced every return. `0` clean · `1` dry-run mistypes **or** subtask placement problems · `2` a conversion that failed. Pre-existing cases keep their codes; `print_human` hoisting only **adds** output on the `--apply` path, where findings were previously invisible. |

### Gates

| Gate | Result |
|---|---|
| Enforcement suite | `21/21 files · 1110/1110 cases` **exit 0** (bare) |
| Toolkit lint | `0 error(s), 0 warning(s), 8 info` **exit 0** (bare) — the 8 are pre-existing UTF-8 BOMs on `testarch-*` |
| Assertion evidence | every Step-2 RED assertion re-run and **GREEN** — `start` accepts a Subtask · `flag` redirects naming `TEST-4` · parentless refuses cleanly · all four `audit` placement cases · open-blocks / `Deferred`-does-not / failed-query-never-clean |
| SOP currency | **exit 0** with the doc · **exit 1** without it (positive control — the gate is alive and ARMED) |
| Link + anchor | `24 links / 9 changed docs, 0 problems` |
| Door parity | both commands **modified, none added/renamed/deleted**; all 4 doors present for each (`claude · agents · opencode · workflow`) |
| py_compile | clean on all 5 changed `.py` |

### Acceptance matrix

| AC | Proving assertion | Result |
|---|---|---|
| AC1 rule written | `jira.md` §Subtasks + the 5-type and close-out tables | ✅ inspection |
| AC2 story lane NEVER | rule text; AVCH re-queried — still **0** subtasks | ✅ board-verified |
| AC3 branch+worktree threshold | rule text + `/smh-quick-dev` Step 1.6 | ✅ inspection |
| AC4 propose then stop | Step 1.6; **no board write exists in any code path** in this diff | ✅ verified by absence |
| AC5 subtask lane no longer breaks the board | `test_jira_feed.py` L905 **inverted** (`code == 2` → `code == 0`) | ✅ 152/152 |
| AC6 parent closes last | `test_task_preflight.py` — open blocks, `Deferred` does not, failed query never reads clean | ✅ 100/100, 3/3 mutants |
| AC7 subtask never `Bug` | `flag` refuses + names parent; `devrecord` characterization | ✅ 152/152 |
| AC8 nothing says stop-on-Subtask | exit-2 row deleted; doc sweep clean | ✅ inspection |

**Drift check (the other direction):** nothing in the diff is outside the list. Two planned items
were **cut** during the build (`devrecord` guard, `mint --parent-key`) — both recorded in the plan
with reasons; cuts narrow scope and are not drift.

### Clean-Code Gate

Machine floor — all bare, all above: `run_all` · `workflow_lint` · `sop_currency` (+ control) ·
`py_compile` · link+anchor. **No FAIL-tier finding.**

| Check | Result |
|---|---|
| Comment contract | ✅ Every non-obvious block carries its ticket and the *why*. Density matches the surrounding file, which is deliberately heavy-comment. |
| AI-drift bans | ✅ None found — no placeholder, no dead branch, no invented API. |
| Over-engineering | ✅ Two abstractions **removed** mid-build by the audit's own tripwires. `check_subtask` is the only new function and each of its four checks maps to a named board failure. |
| Convention fit | ✅ Law in `jira.md`, obligation restated as command **steps**, doors regenerated not hand-edited, table-parse asserts over bare greps. |
| Diff-scoped | ✅ Legacy debt in untouched files noted, not gated on (the 8 BOM infos). |

**Changes applied by this review:** one — R1.

### Step 0.7 — re-derivation against current `main`

1. **Did anything this diff references move?** **No.** `main` advanced `af821b0 → 2151568` (SCC-117's
   artifacts, 2 files). All 13 repo paths this diff introduces were re-resolved; 10 exist, and the 3
   that do not are **prose or fixtures**, verified line by line — the dead SOP path appears *only* in
   text stating it does not exist, `docs/x.md` is a temp-repo fixture, and the worktree path names a
   real dir in the main checkout. Every load-bearing reference re-checked against `origin/main`
   itself, including `SOP_DOC`, which a sibling had **not** changed.
2. **True overlap + merge:** **zero overlap**; `merge-tree` **clean** (exit 0). `origin/main`
   absorbed at `a2b102a`, before this verdict.
3. **Sibling lanes:** `chore/SCC-135-update-maps-launcher` (the shared checkout moved onto it
   mid-build, at `main`, no commits yet) and `chore/SCC-124-baseline-trial` @ `bd097ee`, which holds
   **only `_artifacts/`**. **No landing-order dependency in either direction** — this lane may land
   first or last without consequence.

## Rolled in at the operator's direction (2026-08-12) — a parallel team's audit

A second team audited `main` @ `b1ac733` and handed over a findings list. **Every claim below was
re-verified in source before acting** — they were all accurate. Four rolled in; the rest are tickets,
because they belong to other subsystems and folding them here would be exactly the drift this
ticket's own review gate would FAIL on.

| Rolled in | Was | Now |
|---|---|---|
| **`_artifacts/_main/INDEX.md` row** ⛔ **blocking** | SCC-119 had **no INDEX row of its own** — it was silently riding a row a truncated Antigravity run left behind, which SCC-135 then removed. `check_maps` would have gone **RED the moment this landed**. | Row added. `check_maps`'s missing-row drift is **gone**. |
| **`task_preflight.py` printed a false statement** | *"this repo has no deployable surface (no … `.github`)"* — while `.github/workflows/main-write-gate.yml` sits right there. The **verdict** was right (a CI dir cannot deploy a repo that ships nothing); the **sentence** was untrue. | Renders `PRODUCT_DIRS` (the list actually consulted) and says `.github/` exists but ships nothing here. |
| **Dead link, target never existed** | `active-context.md` linked `docs/gitnexus-sync.md` through `file:///c:/Users/dlohn/.gemini/antigravity/scratch/…`. **0 commits in git history, absent from disk.** Not a mis-pathed link — the guide was authored in an Antigravity scratch dir on the PC and never landed. | De-linked, with the loss recorded in place. **Repair was never an option: there is nothing to point at.** |
| **Mojibake** | `lobbyâ€"it` — a cp1252 round-trip of an em-dash. | Repaired to `lobby—it`. |
| **INDEX date ordering** | `2026-08-10_scc-77` sat between two `2026-08-11` rows. | Moved; the column is now **strictly descending**, verified programmatically. |

**Filed instead of folded — `SCC-137` (Bug) + two subtasks, the rule's first real use:**

The other team found that the close-out gate reported GREEN while `check_maps` was RED. **They named
the symptom; the root cause is worse and I verified it in source:** `task_preflight.gate_plan()`
builds the lane's gate from exactly two entries — `run_all.py` and `workflow_lint.py`. **`check_maps`
is not in it.** The gate cannot fail on a linter it never runs.

- **SCC-137** `Bug` — close-out reports GREEN while `check_maps` is RED (under epic SCC-33).
- **SCC-138** `Subtask` — wire `check_maps` into `gate_plan`, handling the worktree false-positives.
- **SCC-139** `Subtask` — `test_check_maps` live-tree **MISSING-row** coverage (case F asserts *stale*
  only — verified) + `SCAN_IGNORES`, which has **zero** coverage. Both mutation-proven.

Each subtask earns its own branch and worktree — different files, independently shippable, its own
gate run. **That is the threshold applied honestly, not mechanically.** `jira_feed.py audit` was then
run against the **live board** and reads both children as well-formed under a `Bug` parent:
`0 error(s), 0 warning(s), 110 info`.

**Deliberately NOT rolled in:** the stale maps anchor (must be set from the shared checkout on `main`
— from a worktree the remedy ships the **lane name**), the GitNexus re-index and the PC cache sync
(machine-local, not commits), and the Antigravity runtime re-verification (needs an IDE reload).

## Your Actions

**Landed on the branch, not on `main`.** `chore/SCC-119-subtask-rule`, reviewed at `cc553bc`, with
`origin/main` absorbed. Worktree: `.claude/worktrees/SCC-119-subtask-rule`.

- [x] **`/smh-code-review` run** — verdict `CONCERNS @ cc553bc`, one finding, applied.
- [x] **`main` absorbed** (`a2b102a`) so conflicts cannot reach `main`.
- [x] **SCC-119 itself gets no subtasks, and that is the rule working.** Doc and enforcement must
      land together or one is a lie, and one gate covers both.

**Genuine operator calls, all that remain:**

1. **The `CONCERNS` is one thing only: the clean-room review did not run.** You declined the Step 1
   subagent, so the adversarial hunt was re-run inline **by the author of the diff**. Every gate is
   green and every acceptance item is evidenced — the cap is purely the lost independence. Clear it
   by running the clean-room pass, or by accepting it explicitly.
2. **The merge** — `/smh-close-task-merge-tree`. Not done here by design.
3. **`jira_feed.py start`'s refusal was broken shipped work from SCC-113.** Per your ruling it is
   recorded in this Dev Record rather than flagged `Bug`. Say the word to flag it instead.
4. **Your memory index carries a dead SOP path**
   (`_my_resources/_quick_reference/sudo_workflows_testing.md`); the live one is
   `docs/_scc_sops_prds/workflows_testing_SOP.md`. It misled this plan once already, and it will
   mislead the next session the same way. Worth a `/memory-audit`.

**Landed alongside, in a different repo — reported here so it is not lost:** two GitNexus-pass
updates in `Projects/AGY_AVIATIONCHAT` (`docs/.maps-state.json` reconcile stamp,
`scripts/git-hooks/INDEX.md` wording) were committed as **`AVCH-18` @ `428a19d9`** and pushed to
`epic/AVCH-18-adk-2x-runtime`. **They could not ride this ticket** — a separate git repo whose
`.agents/jira.conf` declares `AVCH`, so its files cannot enter this branch and its armed commit-msg
gate rejects an `SCC` key. No deployable path touched, so no E2E was owed.
