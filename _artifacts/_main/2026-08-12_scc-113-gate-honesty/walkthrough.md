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
- [x] Gates run **bare**

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

| Gate | Result |
|---|---|
| `tests/run_all.py` | **16/16 files**, `RUN_ALL_EXIT=0` |
| `test_command_surfaces.py` | 42/42 (from 33/33) |
| `test_jira_feed.py` | 137/137 (from 134/134) |
| `test_task_preflight.py` | 79/79 |
| `workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, exit 0 |
| `sop_currency` | satisfied in-commit (`SOP_DOC` staged with the script change) |
| `py_compile` | exit 0 |

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

- **Nothing is merged.** Branch `chore/SCC-113-gate-honesty` is pushed, `0 0`, tree clean.
- SCC-113 is **In Progress**; this lane has **not** filed a Dev Record yet (proved above, exit 2).
- Landing needs a fresh `/smh-close-task-merge-tree` — one invocation, one merge.

**Queued, not done here:**

| Item | Why it is not in this lane |
|---|---|
| A gate answering *"did this branch land?"* from the merge graph | The revert removed the wrong answer. The right one needs its own red and its own lane. |
| Ghost sweeps for `.agents/skills` and `.claude/skills` | Correction 3 found them unswept. Widening scope mid-lane is the drift Phase 2 exists to stop. |
| `find_devrecord`'s id match is plain containment, not `slug_matches` | Pre-existing; `SCC-11` would match `SCC-110`. Untouched deliberately. |

## Code Review (2026-08-12)

_appended by `/smh-code-review`_
