# SCC-113 — gate honesty (follow-on lane 3)

**Branch:** `chore/SCC-113-gate-honesty` · **HEAD:** `a82c09a` · **Base:** `main @ 2e8aa46`
**Commits:** `ddfd583` (revert) · `a82c09a` (fix-forward)

One sentence: **every check in this lane asserted something the system had never promised**, and
two of them blocked correct work while claiming to protect it.

---

## Task Checklist

- [x] Reopen SCC-113 `Done → In Progress` (a follow-on rides the ticket it came from)
  - `jira_feed.py start` refuses a `Done` key **by design** (ACCEPTANCE 3), so the reopen is an
    explicit `acli transition --yes`; `start` then confirmed it as an idempotent no-op, exit 0.
- [x] **2.4a — diagnose the blocker before fixing it**
  - ⚠️ The diagnosis falsified the audit's own stated cause. See Correction 1 below.
- [x] Part 1 — revert `fe46b4a`
- [x] 2.1 — opencode ghost sweep honours the engine's keep-list
  - ⚠️ Deliberately **not** applied to the workflows sweep; that path is unreachable. See below.
- [x] 2.2 — the placement exemption must be *spoken*, not earned by silence
- [x] 2.3 — correct three false statements I shipped
  - ⚠️ A fourth surface (a code comment) carried the same claim and was corrected too.
- [x] 2.4b — `--story` wired rather than deleted from three surfaces
- [x] Mutation battery — 5 attacks, baseline 42/42
  - The review ran 10 more; two found assertions that did not exist. See `## Code Review`.
- [x] Gates run **bare**
- [x] **Code review — `CONCERNS @ 6cd01c7`.** Three HIGHs; two were defects in code this lane
      wrote and are fixed, one is the revert blocking this lane's own close-out.
  - ⛔ **H-1 is unresolved and is an operator decision.** See `## Your Actions`.

---

## Evidence

Every row carries the command that proves it. Gates were run bare — a piped gate returns the
pipe's exit code, which is how a green can lie.

### AC1 — `fe46b4a` reverted across all three files

```
$ git revert --no-commit fe46b4a
REVERT_EXIT=0
 .agents/scripts/task_preflight.py            | 45 +++-------------------------
 .agents/scripts/tests/test_task_preflight.py | 39 ------------------------
 docs/_scc_sops_prds/workflows_testing_SOP.md |  2 +-
```

**GREEN:** `python3 .agents/scripts/tests/test_task_preflight.py` → `79/79`, `REAL_EXIT=0`
(was 81/81 — `fe46b4a` had added exactly the two assertions this removes).

> A trial revert from the audit session was still staged when this lane resumed. It was preserved
> to scratch, reset, and re-generated from `git revert`; the two patches `diff`ed **IDENTICAL**.
> Recorded because I had reported that tree clean and it was not.

### AC2 / AC2b — the keep-list exemption, opencode only

**RED** (`test_command_surfaces.py:488`):

```
NameError: name 'ghost_doors' is not defined
```

⚠️ Named honestly: that is a *rule-does-not-exist* red, not an assertion red. The assertion-level
reds are attacks 3 and 5 in the battery below, which fail on their assertions with the rule present.

**GREEN:** `42/42`, `REAL_EXIT=0` (was 33/33 — five new controls).

The rule is a **pure function** on purpose. `.agents/project-own.txt` does not exist anywhere in
this repo, so an exemption wired only to disk would have been a permanent green that never once
ran the exempting path — the vacuous shape A-3 was raised about. Battery attack 4 runs the disk
path for real.

**AC2b** — `parse_own_list("*\n")` yields the literal filename `*`, which matches nothing:

```
[PASS] own-list: `*` is a literal name, never a wildcard
[PASS] own-list: a claim is an EXACT name, never a prefix
[PASS] own-list: an UNCLAIMED door is still a ghost   <- negative control
```

**Scope cut, with evidence.** The plan originally said "both ghost sweeps." `Get-SurfaceState`
maps `.agents\workflows` to the **master's own** workflows (`sync-agents.ps1:319`), so in the
lobby that surface is compared against itself and can never produce an orphan; `-Reconcile`
therefore cannot stage a lobby workflow into the keep-list, and this test is lobby-only
(`ROOT = parents[3]`). Wiring it there would be unreachable code dressed as symmetry.

### AC3 / AC3b — the exemption must be spoken

**RED** — a real assertion failure, naming the door that had been exempt by silence:

```
[FAIL] every hand-owned workflow EXPLICITLY declares the surface it sits on:
       ['smh-update-maps-indexes.md']
-- 41/42 passed --   REAL_EXIT=1
```

**GREEN** after adding `platforms: [antigravity]` to that workflow → `42/42`, `REAL_EXIT=0`.

`platforms_declared()` separates two readings of silence that had been collapsed into one:
commands keep the engine's rule (absent = universal), while the hand-owned exemption now requires
an explicit claim. `platforms: []` remains a real claim of *nowhere* and correctly fails.

**AC3b:** `workflow_lint.py --toolkit-only` → `0 error(s), 0 warning(s)`, `LINT_EXIT=0`.

### AC4 — the false statements

See **Corrections** below. Four surfaces, not three.

### AC5 — the blocker, proved live on the real board

```
$ python3 .agents/scripts/jira_feed.py check --key SCC-113
[INFO ] devrecord: SCC-113: 2 Dev Records, one per lane
        (scc-113-door-content-parity, scc-113-jira-in-progress-seam)
        - a follow-on lane rides the ticket it came from, so this is the designed state
-- 0 error(s), 0 warning(s), 2 info --
REAL_EXIT=0
```

Before this lane: `REAL_EXIT=1`, against `smh-close-task-merge-tree.md:245`'s `# must exit 0`.

### AC5b — `--story` wired, both directions, live

```
$ ... check --key SCC-113 --story scc-113-door-content-parity   -> REAL_EXIT=0  (one Dev Record)
$ ... check --key SCC-113 --story scc-113-gate-honesty          -> REAL_EXIT=2  (never filed one)
```

The error arm is the load-bearing half, and its control asserts the **message**, not just the
code — an unknown flag also exits 2, which is exactly how this would have passed for the wrong
reason while `--story` stayed unwired.

### AC6 / AC7 — nothing else moved

⚠️ **Final run, at the landing sha `6cd01c7`** — these replace the dev-time totals. The per-step
`42/42` and `137/137` figures above are accurate *as of the step that records them*, before the
code review added three more assertions; they are left standing as the RED→GREEN trail.

| Gate | Result |
|---|---|
| `tests/run_all.py` | **16/16 files**, `RUN_ALL_EXIT=0` |
| `test_command_surfaces.py` | **43/43** (33/33 pre-lane) |
| `test_jira_feed.py` | **141/141** (134/134 pre-lane) |
| `test_task_preflight.py` | 79/79 |
| `workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, exit 0 |
| `sop_currency` | exit 0 on the real staged set; `SOP_DOC` staged in all three usage-surface commits |
| `py_compile` | exit 0 |
| live `jira_feed check --key SCC-113` | exit 0 (was 1) |

---

## Mutation battery — 5 attacks, throwaway copy, baseline 42/42

| # | Attack | Result |
|---|---|---|
| 1 | hand-owned door drops `platforms:` entirely (exempt by silence — the pre-lane state) | **1 FAIL** |
| 2 | hand-owned door DENIES the surface it sits on (`platforms: [claude]`) | **1 FAIL** |
| 3 | an opencode door with no command source, unclaimed | **1 FAIL** |
| 4 | the same ghost, **CLAIMED** in `project-own.txt` | **0 FAIL** — exemption holds |
| 5 | the keep-list claims `*` instead | **1 FAIL** — cannot widen |

**Attack 4 is the one that matters.** It proves the keep-list path is *reachable* rather than
dead code — which is precisely what the self-audit flagged it as a risk of being. The pure
controls cover the parse; only this ran the disk path.

---

## Corrections — things I had asserted that were not true

### Correction 1 — the audit's own diagnosis (A-1) was wrong

A-1 stated *"the Task close-out does not pass `--story`."* **It does** —
`smh-close-task-merge-tree.md:236` and `smh-quick-dev.md:246`, both keyed off `<branch-slug>`.

A-1's *conclusion* held: do not ship a fix for an undiagnosed defect. Diagnosing first is what
caught that its stated reason was itself wrong. The real cause:

| # | Record on SCC-113 | Merge |
|---|---|---|
| 1 | `Dev Record - scc-113-jira-in-progress-seam (close-out, 2026-08-11)` | `302bd37` |
| 2 | `Dev Record - scc-113-door-content-parity (close-out, 2026-08-12)` | `2e8aa46` |

Two lanes → two branch slugs → two story ids. `find_devrecord` filters by id **deliberately**
(*"so a ticket that legitimately carries records for two ids does not have one overwrite the
other"*). Nothing posted around the update path and **there was no data to repair.** The check
counted without reading ids, so it could not tell *one lane posting twice* (a real defect) from
*two lanes each posting once* (the design). It now groups; the pre-existing same-id test stays
green as the negative control.

### Correction 2 — "kept FOREVER" was false, on four surfaces

I wrote that opencode's sync keeps a deleted command's door forever. It does not:
`Invoke-ManifestPurge` runs on the very next line after the sweep (`sync-agents.ps1:822`) and
retires it. **I read `Sync-CommandDir` in isolation and stopped one line short of its caller** —
then repeated the claim into a code comment, the SOP row, and the previous lane's walkthrough.

The true gap is narrower and still worth a check: the manifest can only retire *a name a previous
run recorded writing* (`sync-agents.ps1:380`). A door predating the manifest, hand-dropped, or
genuinely this repo's own is unreachable by it — which is exactly what `project-own.txt`
adjudicates. Corrected in all four places, with the original text left standing in the prior
walkthrough per `story-artifacts-two-doc-close`.

### Correction 3 — "true of the skill doors only"

True for **placement**. For **ghosts** it was true of no surface: `.agents/skills` and
`.claude/skills` are unswept to this day. Queued, not silently fixed.

---

## Decisions made while building

**`project-own.txt` was NOT created, and that was the point.** `T9 every prose path reference
resolves` correctly failed my SOP edit for naming a path that resolves nowhere. Creating an empty
file would have satisfied the lint and **armed an unreviewed purge**: `Get-OwnAllowList` returns
`$null` for an absent list (which *blocks* purging) and `@()` for an authored empty one (which
authorises purging every unclaimed orphan on the next `-Reconcile`). The fix was the truth — the
SOP now says the file is staged on demand and does not exist until then.

That is the lane's own thesis applied to the lane: satisfying a green by changing the world
instead of the claim is how this ticket got here.

---

## Your Actions

### ⛔ BLOCKER — this lane cannot mechanically close, and the revert is why

`task_preflight.py`, run bare against this repo after the revert:

```
[ERROR] manifest: _artifacts/_main/2026-08-11_scc-113-jira-in-progress-seam/task.yaml declares
        branch `chore/SCC-113-jira-in-progress-seam` but this preflight resolved
        `chore/SCC-113-gate-honesty` - one of them is wrong
[ERROR] manifest: _artifacts/_main/2026-08-12_scc-113-door-content-parity/task.yaml ... (same)
VERDICT: BLOCKED - resolve the errors above
PREFLIGHT_EXIT=2
```

Both of those branches are merged and pruned (`git branch -a --list '*113*'` → only this lane).
`smh-close-task-merge-tree.md:126` runs this preflight and stops on a blocking verdict, **so
`/smh-close-task-merge-tree` will not land this branch as it stands.**

**This is the cost I named in `ddfd583` arriving immediately, and my own pre-mortem predicted
it** (*"no auditable escape hatch on the restored preflight; the operator is the first to hit the
restored ERROR"*). What I got wrong is that the plan said *"SCC-113 itself is already closed, so
nothing in flight is affected"* — SCC-113 is `In Progress` and this is its **third** lane. AC1's
evidence was `test_task_preflight.py 79/79`, which is fixtures; **the preflight was never run
against the repo it has to close.** A fixture-green gate on a repo it blocks is this lane's own
subject, one layer up.

**This is an operator decision, and the flow says stop.** `/smh-quick-dev` Step 3.5 ejects when a
review finding is bigger than a trivial patch. Options, with my recommendation first:

| # | Option | Cost |
|---|---|---|
| **A (recommended)** | Build the positive-ancestry rule now: ask *"is this manifest's artifact folder already on `origin/main`?"* — positive evidence from the merge graph, which is the sound question `ddfd583` said the revert was making room for | Scope expansion beyond the approved plan; needs its own RED. It is the item already queued below |
| B | Delete or relocate the two closed lanes' `task.yaml` files | Fast, but it satisfies a gate by changing the world instead of the claim — the exact antipattern this walkthrough calls out under *Decisions* |
| C | Re-land `fe46b4a` and queue the redesign | Restores the convenience and re-lands the two HIGHs that justified the revert |
| D | Land by operator judgment with the block acknowledged | The preflight has no override flag, deliberately; there is no sanctioned mechanism for this |

⚠️ I have **not** picked one. Nothing is merged and nothing is transitioned.

### State

- Branch `chore/SCC-113-gate-honesty` pushed. **The tree is not clean** — see the correction
  below; a stale "tree clean" claim stood here and is the second time this lane made it.
- SCC-113 is **In Progress**; this lane has filed **no** Dev Record — proved, not assumed:
  `check --story scc-113-gate-honesty` → exit 2.

**Queued, not done here:**

| Item | Why it is not in this lane |
|---|---|
| **The positive-ancestry preflight rule** (option A above) | The revert removed the wrong answer. The right one needs its own red and its own lane — and it is now this lane's blocker. |
| Ghost sweeps for `.agents/skills` and `.claude/skills` | Correction 3 found them unswept. Widening scope mid-lane is the drift Phase 2 exists to stop. |
| `find_devrecord`'s id match is plain containment | Pre-existing on the **write** path, where over-matching is conservative. The **read** gate no longer depends on it (see H-3). |
| Wire `--story "$BRANCH_SLUG"` into `smh-close-task-merge-tree.md:245` | M-4: no Task surface passes `--story` to `check`, so the close-out cannot yet verify its *own* lane filed a record. A command-body change is a usage surface with door regeneration — not a review fix. |

## Code Review (2026-08-12)

```
Verdict: CONCERNS @ 6cd01c7
```

Suite evidence measured at **`6cd01c7`** — the sha that will land. `run_all.py` re-run in full
after the last code change.

⚠️ **`CONCERNS` is not "proceed".** Every gate is green and every acceptance item is delivered;
the verdict is held down by **H-1**, which is not a code defect but a design consequence that
**mechanically blocks this branch's own close-out**. See `## Your Actions`. The preflight will
refuse regardless of this line.

**Scope:** 11 files, `main @ 2e8aa46` → `chore/SCC-113-gate-honesty @ 6cd01c7`, resolved from
`rev-parse`, not from belief.
**Method:** clean-room adversarial subagent on the diff **before** it was allowed to read the
plan or walkthrough · acceptance audit against the plan's table · command-centre gate, all bare ·
`/smh-clean-code-audit` · my own 5-attack mutation battery, plus 10 more the reviewer ran.

### Step 0.7 — re-derivation against current `main`

1. **Nothing this diff references moved.** `origin/main` = local `main` = `merge-base` =
   `2e8aa46`; **0 files** landed since this lane branched.
2. **True overlap: empty.** `merge-tree --write-tree` returned a clean tree, no conflict messages.
3. **No sibling lane.** `git worktree list` → `main` and this lane only. No landing-order
   dependency.

### Findings

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| H-1 | `.agents/scripts/task_preflight.py` (the revert) | **HIGH** | Preflight run bare on this repo → `VERDICT: BLOCKED`, exit 2, on two merged-and-pruned lanes' manifests. `/smh-close-task-merge-tree` will not land this branch. Plan claimed "nothing in flight is affected"; SCC-113 is `In Progress` with three lanes. AC1's evidence was fixtures only. | **deferred — operator decision.** Ejected per Step 3.5; artifacts corrected to state the impact |
| H-2 | `jira_feed.py` `cmd_check` | **HIGH** | An unparseable header returns `""`, which sat beside a real id and satisfied the "two lanes" arm → INFO exit 0 where the old check warned. Any comment containing "Dev Record" triggers it. Reproduced. | **applied** — `""` is unidentifiable, never a lane; warns |
| H-3 | `jira_feed.py:1236` → `find_devrecord:545` | **HIGH** | `--story` delegated to bare containment over the whole 400-char head. A record whose **body** names a sibling lane certified that lane as having filed one. Reproduced, plus `9.1` adopting `9.10`. | **applied** — matched on the header, exactly |
| M-1 | `test_command_surfaces.py` `parse_own_list` | MED | Cited `:309` (the `Test-Path` guard) instead of `:310`; claimed "mirrored exactly" while PowerShell's `-contains` is case-insensitive — engine keeps `Smh-Review.md`, sweep called it a ghost | **applied** — both sides fold, with a control; citation fixed |
| M-1b | — | — | Reviewer's BOM hazard | **dismissed** — every caller reads via `read()`, which is `utf-8-sig`. Verified, not assumed |
| M-2 | `test_command_surfaces.py` + SOP row 1196 | MED | *"only a NAME a previous run recorded writing"* is `Invoke-ManifestPurgeDir`'s docstring (`:379`), the skills-**directory** variant — the opencode sweep calls `Invoke-ManifestPurge` (`:365`). Substance true of both; citation named the wrong function, in the surfaces rewritten to fix mis-citation | **applied** |
| M-3 | `test_command_surfaces.py` | MED | `Get-SurfaceState` maps `.agents\workflows` at `:325`; `:319` is `$mCmd` — the wrong half of the function the scope-cut argument is drawn from | **applied** |
| M-4 | `smh-close-task-merge-tree.md:245` | MED | No Task surface passes `--story` to `check`, so close-out cannot verify its own lane filed a record | **deferred** — command-body change = usage surface + door regeneration. Queued |
| L-1 | `walkthrough.md` | LOW | *"tree clean"* while a file was uncommitted — a verbatim repeat of this lane's own confession | **applied** — committed; claim rewritten |
| L-2 | `platforms_declared` docstring | LOW | Said *"that is the engine's rule"* while the plan queues two known divergences (60-line cap, case) | **applied** — both named in the docstring |
| L-3 | `record_story_id` | LOW | Id stops at first `(`; parenthesised ids would collapse into a false duplicate | **applied** — constraint stated; fails loud, not silent |
| L-4 | `test_command_surfaces.py` | LOW | Plan required the comment state the `$null` vs `@()` distinction; only the SOP did | **applied** |
| L-5 | SOP row 1196 | LOW | `-Reconcile` stages the keep-list only on a run that **finds orphans** | **applied** |

### Gates — all run bare, at `6cd01c7`

| Gate | Output |
|---|---|
| `run_all.py` | `16/16 files passed` · `RUN_ALL_EXIT=0` |
| `workflow_lint --toolkit-only` | `0 error(s), 0 warning(s), 8 info` · `LINT_EXIT=0` |
| `test_command_surfaces.py` | `43/43` (33/33 pre-lane) |
| `test_jira_feed.py` | `141/141` (134/134 pre-lane) |
| `test_task_preflight.py` | `79/79` |
| `sop_currency` | `exit 0` on the real staged set; SOP staged in all three usage-surface commits |
| `py_compile` | `exit 0` |
| link + anchor | 18 tokens resolved; 1 defect found and fixed |
| door parity | n/a — no command added, renamed, or deleted |
| lint / types | not applicable to this repo (no venv, no ruff, no tsc) |
| **live board** | `jira_feed check --key SCC-113` → `exit 0` (was 1) |

### Assertion evidence — which checks I made FIRE

Baseline 43/43 · 141/141 · 16/16, all exit 0 bare. Mutations reverted, tree re-verified green.

| Mutation | Result |
|---|---|
| strip `platforms:` from the hand-owned workflow | FAIL — 42/43 |
| `claims_explicitly` reverts to universal-on-silence | FAIL |
| `parse_own_list` stops stripping `#` | FAIL |
| `ghost_doors` → prefix match | FAIL |
| `ghost_doors` → `return []` | **3 FAILs** |
| real ghost on disk, unclaimed | FAIL |
| same ghost **claimed** in `project-own.txt` | **PASS** — the disk path is reachable, not dead code |
| same ghost claimed in the **wrong case** | FAIL before the M-1 fix, PASS after |
| `record_story_id` always returns `""` | FAIL |
| `--story` accepted and ignored (pre-lane) | 2 FAILs |
| `--story` miss demoted `err`→`info` | FAIL |
| duplicate warn demoted `warn`→`info` | FAIL |

**Could not be made to fire, before the fixes:** the `""` bucket (H-2) and `--story` substring
collision (H-3) had **no assertion at all**. Both now do, and both were seen red first.

**Regression check on the refactor:** the reviewer differential-fuzzed old vs new `platforms_of`
across 168 inputs — 21 hand-built edge cases plus every real file in `.agents/commands`,
`.agents/workflows`, `.opencode/commands` — **0 divergences**, both migrated call sites confirmed,
none missed.

### Clean-Code Gate — CONCERNS

**Machine floor** — `run_all` PASS (16/16, exit 0) · `workflow_lint` PASS (0/0) · `sop_currency`
PASS (exit 0) · `py_compile` PASS · link+anchor PASS after 1 fix · door parity n-a ·
lint/types **not applicable to this repo**.

Banned-pattern scan over 251 added `.py` lines: no secrets, no `print(`, no bare `except`, no
commented-out code, no absolute paths, no bare `python`. No `AIDEV-` anchor invalidated (none
present). No personal name in any `.agents/` body.

| # | file:line | Sev | Category | Finding | Disposition |
|---|---|---|---|---|---|
| 1 | `test_command_surfaces.py` `parse_own_list`, `ghost_doors` | CONCERNS | comment-contract | no `SCC-113:` provenance on two new helpers, one encoding a cross-language rule | applied, then **reverted outside this flow** — left as the operator found it |
| 2 | `.agents/workflows/smh-update-maps-indexes.md` | — | generated-files | Looks like a banned hand-edit to a generated surface | **dismissed with evidence** — in `$excluded` at `sync-agents.ps1:517`, *"never written by this mirror, never pruned by it"*. Read from source |

**No over-engineering or AI-drift findings**, independently confirmed by the clean-room pass: the
`platforms_declared` split is load-bearing, the pure-function controls are the right answer to an
unexercisable disk path, and the workflows-sweep scope cut was re-derived independently.

### Changes applied during review

H-2, H-3, M-1, M-2, M-3, L-1..L-5 fixed and committed as `6cd01c7`, each with an assertion seen
red first. H-1 and M-4 deferred with reasons above. Evidence totals and the `## Your Actions`
section above were rewritten to match this run — no pre-review numbers left standing.
