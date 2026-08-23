---
IsArtifact: true
ArtifactMetadata:
  title: SCC-281 — the rolling bug list run as one consolidated lane (cycle 6)
  type: walkthrough
  date: 2026-08-22
---

review-runtime: fan-out

# SCC-281 — Three carried-forward defects, one lane, and the bug the lane found in its own fix

**Lane:** `chore/SCC-281-bugs-cycle-6` · **Ticket:** SCC-281 (Task, rolling "Bugs and Updates", cycle 6)
**Riders:** SCC-282 Part A · SCC-283 Part B · SCC-284 Part C — all three carried forward from SCC-262 (SCC-264/265/266), found at SCC-244's close-out
**Plan:** [implementation_plan.md](implementation_plan.md) (with its Self-Audit, `Audit verdict: GO`)
**Base:** `origin/main@a634c35`, unmoved for the whole lane — no absorb was needed.
**Successor:** SCC-293 (cycle 7) — cloned by `jira_feed.py start` the minute this ticket went `In Progress`, retitled, INDEX emptied, PREDECESSOR names this lane. Baton read back: SCC-293 `running-bug-list`, SCC-281 `bugs-and-updates`, one each.

---

## What this changed, and the one thing the build found that the ticket did not

Three riders, each a real defect re-verified on `a634c35` before a line was written, each fixed red-first in one worktree on the operator's word (*"one shot the ticket on one working tree"*). Build order C → A → B. Every commit names its subtask key.

- **C — `mutation_sweep.py` (SCC-284).** The loader tested its five required fields with a FALSY check, so a deletion mutant — `"mutated": ""`, *remove this line and see if anything notices* — was refused as *"missing mutated"*. It now distinguishes **absent** (refused, and says so) from **empty** (legal for `mutated` only). SCC-244's three inert-substitute mutants (M16/M23/M26) became real deletions and that sweep still came back **27/27** — the record is now right about what was proven.
- **A — `task_preflight.py` rider evidence (SCC-282).** `lane_commit_keys()` read only the *leading* key of a commit subject, while the house convention leads with the *lane* key — so on a consolidated lane no rider could ever earn `landing_mode: partial`. New `subject_keys()` reads every key in a subject; `d9d9a9d`'s verbatim subject is a regression fixture and the test also reads the live commit when reachable. Five prose sites that taught *"leads no commit"* now say *"is named in no commit subject"*, and the close-out's partial-landing step says how a rider earns its evidence **before** the commits are immutable.
- **B — `task_preflight.py` dirt classifier (SCC-283).** A fourth bucket: a dirty path whose **bytes** equal a live sibling lane's **committed** copy is *that lane's working copy* — named with its branch as a warning, never errored, never swept. Different bytes still error; a path no lane has still errors. ⭐ **The self-audit caught a hole in the plan's own design** — `trees_to_measure` would have made the `main` checkout a "sibling", waving an uncommitted revert-to-main through (permissive in the SCC-180 direction) — so siblings are `chore/` · `claude/` · `epic/` worktrees only, and case B4 pins it.

⛔ **The bug the build found in its own fix (B).** The first GREEN still failed B1 with exit 2. Reproduced by hand: `git status --porcelain` **collapses an untracked new directory to one line** — `.claude/x.json` arrived as `?? .claude/`, and the helper tried to read a directory. The fix expands an untracked-directory entry and owns it only when **every** file under it is some live lane's committed copy; one unowned file and the whole entry stays dirt. Recorded because the real-world case (`?? .claude/hooks/allow-scratchpad.py` in the ticket) would have been the file-level line only because `.claude/hooks/` already existed — a fresh directory would have silently kept erroring.

⭐ **And the sweep found the bug the tests could not (B, second round).** The first 9-mutant sweep came back **7/9**: M5 and M7 survived. M5 was a weak assertion — `original: ""` was refused *downstream* by the unique-anchor check, so K6f never pinned the loader's own guard; tightened to demand the loader's *EMPTY* message. **M7 was the real one.** Making `main` a "sibling" should have turned B4 red and did not — because B4 was passing for the wrong reason: `_check_tree_dirt` ran `.strip()` over the **whole** porcelain output before splitting, which eats the leading space of the **first line only**. ` M path` arrived as `M path`, `ln[3:]` read a path with its first character missing, and every path-reading rule in that function — the memory ruling (SCC-64), the own-receipt exclusion, and the new sibling match — silently missed the first dirty file whenever it was a tracked modification. That is **exactly** the ticket's shape: `M .claude/settings.json`. Every B1–B3 fixture had used an untracked file (`??`, no leading space), so the tests were green over a fix that would not have fired in production. Two new cases (B5: tracked-modified sibling copy on the first line; B6: tracked-modified memory file on the first line) went red, the split-then-filter fix turned them green, and mutant M10 pins it.

**Consolidation decision** (work-consolidation.md rule 2, said out loud): one lane, because the three parts share a repo and a lane class, no part needed to run beside another, and the operator asked for it. No `landing_mode:` line — this landing closes SCC-281.

---

## Task Checklist

- [x] Board: SCC-281 → `In Progress`; SCC-293 cloned as cycle 7, retitled, INDEX emptied, PREDECESSOR updated; baton verified on both labels
- [x] Worktree `scc-281-bugs-cycle-6` off `origin/main@a634c35`, upstream unset, assets linked; sibling lanes read (overlap: `.sync-manifest.json`, one `jira.md` line vs SCC-280)
- [x] Plan + `task.yaml` (`riders: [SCC-282, SCC-283, SCC-284]`), Declared Change Set parses, self-audit GO with two findings baked in
- [x] Part C RED (3/6 in K6, *"is missing mutated"*) → GREEN (6/6; full file 33/33) → SCC-244 re-sweep 27/27 with three real deletions
- [x] Part A RED (15/17, exit 2 + `found []`) → GREEN (17/17; full file 109/109) → five prose sites + close-out step + SOP → mirrors re-synced
- [x] Part B RED (3/5, exit 2) → GREEN (5/5; full file 85/85)
  - finding: `?? .claude/` directory collapse — expanded and owned-only-if-all-match
- [x] Sweep round 1: 7/9 — M5 (weak K6f assertion) and M7 (the first-line `.strip()` parse bug) survived
  - finding: ` M path` on the first porcelain line lost its leading space → wrong path → sibling match and memory ruling both blind to the ticket's own shape; B5/B6 RED → parse fix GREEN (8/8; full file 88/88); K6f tightened (6/6)
  - finding: the B5 fixture was wrong twice (unpushed `main`; lane merged into `main`) — rebuilt
- [x] Mutant table: 10 mutants drawn from the code, anchors verified unique, one of them a real deletion (M8), M10 pins the parse fix — result below
- [ ] Suite receipt on the committed tip — below
- [ ] `/smh-code-review` — below

## Evidence

### C — SCC-284 (`tests/test_mutation_sweep.py --case "K6"`)

**RED** @ `2e83ddc`:
```
[SWEEP ERROR] .../sweep.json: mutant #1 is missing mutated
-- 3/6 passed --
FAILED: K6a `"mutated": ""` LOADS - the table is not refused as missing a field, K6b ...and it APPLIES as a deletion and is scored like any other (KILLED, exit 0), K6e ...and the message says ABSENT, so the reader does not hunt for a typo in a field that is there
```
**GREEN** @ `0080adb`:
```
[PASS] K6a `"mutated": ""` LOADS - the table is not refused as missing a field: exit=0   M1 delete the guard line
[PASS] K6b ...and it APPLIES as a deletion and is scored like any other (KILLED, exit 0)
[PASS] K6c ...and the deleted line is back afterwards (restore proven)
[PASS] K6d a mutant whose `mutated` key is genuinely ABSENT still refuses, exit 2
[SWEEP ERROR] ...: mutant #1 is missing mutated - the key is ABSENT (an EMPTY `"mutated": ""` is legal and declares a deletion)
[PASS] K6e ...and the message says ABSENT, so the reader does not hunt for a typo in a field that is there
[SWEEP ERROR] ...: mutant #1 has an EMPTY original - only `mutated` may be empty (a deletion); `original` must be a unique anchor
[PASS] K6f `"original": ""` still refuses - a mutant that inserts from nowhere has no unique anchor: exit=2
-- 6/6 passed --
```
Full file: `-- 33/33 passed --`.

**C4 — SCC-244's sweep, M16/M23/M26 rewritten to `"mutated": ""`** (M23's `if pending_label:` block sits inside `if m:` with `current = [...]` after it, so the deletion leaves valid Python — checked before declaring):
```
-- sweep: 27 mutant(s) over 10 file(s) @ 2e83ddc5 --
-- sweep clean: 27/27 killed by their declared case --
exit=0
```

### A — SCC-282 (`tests/test_task_preflight.py --case "SCC-170 partial"`)

**RED** @ `10b8b36`:
```
[FAIL] SCC-282 a rider NAMED in a subject the lane key leads earns its evidence (the house convention is not a declaration error): exit 2
[FAIL] SCC-282 subject_keys() finds EVERY key in d9d9a9d's verbatim subject, not just the leading one: found []
[PASS] SCC-282 ...and the fixture IS the live subject of d9d9a9d: SCC-244 rider SCC-253: scripts/INDEX.md names a lever that is worth two seconds [sop-ok]
-- 15/17 passed --
```
**GREEN** @ `53451fc`:
```
[PASS] SCC-282 a rider NAMED in a subject the lane key leads earns its evidence (the house convention is not a declaration error): exit 1
[PASS] SCC-282 subject_keys() finds EVERY key in d9d9a9d's verbatim subject, not just the leading one: found ['SCC-244', 'SCC-253']
[PASS] SCC-282 ...and the fixture IS the live subject of d9d9a9d
-- 17/17 passed --
```
Full file: `-- 109/109 passed --`. Mirrors: `sync-agents.ps1` from the worktree — `.opencode/commands/` ×2 and `.sync-manifest.json` changed; `.agents/workflows/` launchers carry no body and did not.

### B — SCC-283 (`tests/test_task_preflight_contract.py --case "SCC-283"`)

**RED** @ `de89d38`:
```
[FAIL] SCC-283 a dirty path byte-identical to a live sibling lane's committed copy does NOT error: exit 2
[FAIL] SCC-283 ...and it is reported as THAT lane's working copy, naming the branch
[PASS] SCC-283 CONTROL a dirty path matching NO live lane still errors: exit 2
[PASS] SCC-283 a sibling's path whose CONTENT differs from its committed copy still errors: exit 2
[PASS] SCC-283 a revert-to-main in the working copy still errors - `main` is never a sibling lane: exit 2
-- 3/5 passed --
```
**First GREEN attempt — still 3/5.** Hand reproduction:
```
STATUS: '?? .claude/\n'
[ERROR] sync: the checkout: 1 uncommitted change(s) - commit (explicit paths) and push before merging
```
**GREEN** @ `f6b9e10` (after the untracked-directory expansion):
```
[PASS] SCC-283 a dirty path byte-identical to a live sibling lane's committed copy does NOT error: exit 1
[PASS] SCC-283 ...and it is reported as THAT lane's working copy, naming the branch
[PASS] SCC-283 CONTROL a dirty path matching NO live lane still errors: exit 2
[PASS] SCC-283 a sibling's path whose CONTENT differs from its committed copy still errors: exit 2
[PASS] SCC-283 a revert-to-main in the working copy still errors - `main` is never a sibling lane: exit 2
-- 5/5 passed --
```
Full file: `-- 85/85 passed --`.

**Second round — the first sweep's survivors (7/9 @ `f6b9e10`):**
```
⛔ NOT KILLED M5 (C) `original` drops out of the non-empty check - SURVIVED
⛔ NOT KILLED M7 (B) every worktree is a sibling, `main` included - SURVIVED
-- SWEEP FAILED --
```
M7 applied by hand, B4 still exit 2 — instrumented: `rest=['M .agents/scripts/tests/run_all.py'] owned={}` — the leading space of the first porcelain line was gone.

**RED** @ `78ab229` (B5 tracked-modified sibling copy on line 1; B6 tracked-modified memory file on line 1; K6f tightened):
```
[PASS] B5 fixture: the sibling's file is a TRACKED-MODIFIED first line (` M`): ' M .claude/x.json\n'
[FAIL] SCC-283 a TRACKED-MODIFIED sibling copy on the FIRST status line is owned (the ticket's `M .claude/settings.json` shape): exit 2
[FAIL] SCC-283 a TRACKED-MODIFIED memory file on the FIRST status line still gets the memory ruling, not the generic count: exit 2
-- 6/8 passed --
```
**GREEN** — parse fix @ `913e102` (B6 green; B5 still red — the FIXTURE was wrong twice: an unpushed `main` tripped the stalled-landing check, then merging the lane into `main` left it nothing to merge), fixture rebuilt @ the commit after it:
```
-- 8/8 passed --
```
Full file: `-- 88/88 passed --`. K6 after tightening: `-- 6/6 passed --`.

### Mutation sweep — this lane ([sweep.json](sweep.json), 10 mutants drawn from the code, one a real deletion)

Round 2, after the M5/M7 fixes and M10 added (`mutation_sweep.py --table …/sweep.json`):
```
-- sweep: 10 mutant(s) over 2 file(s) @ 4cef34d2 --
-- sweep clean: 10/10 killed by their declared case --
exit=0
```
| # | Mutant (from the code) | File | Killed by |
|---|---|---|---|
| M1 | `lane_commit_keys` reads only the LEADING key again | task_preflight.py | SCC-282 a rider NAMED in a subject the lane key leads earns its evidence |
| M2 | `subject_keys` returns only the first key | task_preflight.py | SCC-282 subject_keys() finds EVERY key in d9d9a9d's verbatim subject |
| M3 | loader back to a FALSY presence test | mutation_sweep.py | K6a |
| M4 | refusal stops saying ABSENT | mutation_sweep.py | K6e |
| M5 | `original` drops out of the non-empty check | mutation_sweep.py | K6f (after tightening — survived round 1) |
| M6 | sibling match by PATH only | task_preflight.py | SCC-283 … CONTENT differs … still errors |
| M7 | every worktree is a sibling, `main` included | task_preflight.py | SCC-283 a revert-to-main … still errors (after the parse fix — survived round 1) |
| M8 | **DELETION** — owned paths never removed from `rest` | task_preflight.py | SCC-283 … does NOT error |
| M9 | the warning stops saying whose WORKING COPY | task_preflight.py | SCC-283 … reported as THAT lane's working copy |
| M10 | porcelain output stripped whole again | task_preflight.py | SCC-283 a TRACKED-MODIFIED sibling copy on the FIRST status line is owned |

### Enforcement suite — receipt

Stamped once, on the committed tip, through the receipt writer (`gate_receipt.py run --task SCC-281 --gate suite --root … --cwd <worktree> -- python3 .agents/scripts/tests/run_all.py`):
```
[PASS] suite exit=0 75.1s @ 72b3df2e
        receipt: gates/suite.json
…
-- 59/59 passed --
============================================================
52/52 files passed
```
Receipt: [gates/suite.json](gates/suite.json) — `result: pass`, `sha: 72b3df2e5fa9a7778d6ed72705a4ab835d36adac`, `dirty_tree: false`. `git rev-parse HEAD` at the run: `72b3df2e5fa9a7778d6ed72705a4ab835d36adac`.
Toolkit lint (bare): `-- 0 error(s), 0 warning(s), 8 info --`. `py_compile` on the five changed `.py` files: OK.

---

## Your Actions

What landed is above. Nothing here is owed to you but the close-out decision; every board write (three riders to `Done`, then SCC-281) is the ceremony's and runs inside `/smh-close-task-merge-tree`.

- SCC-293 (cycle 7) is open and empty, holding `running-bug-list` — the next home for discovered work.
- `jira.md:356` changed one clause; SCC-280's tree has an uncommitted `jira.md` in another section. Whichever lands second absorbs a trivial merge.
