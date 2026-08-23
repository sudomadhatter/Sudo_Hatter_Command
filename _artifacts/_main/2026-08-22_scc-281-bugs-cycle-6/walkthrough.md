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

⛔ **And the review found the hole in the fix itself — four lenses, independently, three by execution.** The fourth bucket as built compared the working copy to `<sibling>:<path>`. But a sibling lane's committed **tree** carries `main`'s bytes for every file it never touched, so that equality is also true of a hand-revert to main — the moment **one unrelated sibling worktree is live**, which on this machine means always (six were live during the review). The self-audit's "`main` is never a sibling" guard excluded main *by name* and was dead code on every real run; B4 passed only because its fixture had no sibling worktree. The predicate is now **"the lane CHANGED it"**: a sibling owns a path only when its blob differs from the base's blob for that path, so a revert-to-base can never match anyone (B7, M12). Four more rulings rode in with it: the lane's **own** branch is a legitimate owner — the lane that dirtied the shared checkout must be able to close itself, and the first cut wedged exactly that (B8, M17); a **prunable** worktree is not a live lane (B12, M13); a **staged** sibling copy is never owned and errors with the `git restore --staged` remedy instead of "commit it" (B13, M16); and the compare is by **blob id through git's clean filter**, because the PC runs `core.autocrlf=true` (`.gitattributes` says so) and a raw-byte compare made the whole bucket dead on one of the two machines (B15, M14). The `"mutated": null` regression in C (a crash where a refusal used to be) and the `ls-files` quotepath gap were fixed in the same pass (K6g, M15; B11).

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
- [x] Suite receipt on the committed tip @ `72b3df2` (52/52 files) — and re-stamped after the review fixes, below
- [x] `/smh-code-review` — five clean-context lenses, 36 findings, 12 patches applied in thread, re-swept and re-stamped — below
  - finding (four lenses, three reproductions): a sibling's committed TREE holds main's bytes for untouched files → a revert-to-main was owned the moment any sibling was live; B4 had no sibling. Predicate is now "the lane CHANGED it" (blob ≠ base blob), B7 pins it
  - finding: the OWNING lane wedged itself at its own close-out (own branch excluded) → B8
  - finding (reproduced ×3): `"mutated": null` crashed the sweep with a TypeError → refused, K6g
  - finding (reproduced ×2, `.gitattributes` confirms the PC's `autocrlf=true`): raw-byte compare was dead on CRLF → blob ids through the clean filter, B15
  - findings: `ls-files` without `quotepath` (B11) · prunable worktree counted live (B12) · staged sibling copy got the wrong remedy (B13) · all-must-match had no case and `all→any` survived (B10, M11)

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

### B/C — review round (`--case "SCC-283"` · `--case "K6"`)

**RED** @ `b3c46b1` (B7–B15 and K6g written from the lens findings; B9/B10 were already correct and are now pinned):
```
[PASS] B4 fixture: the reverted bytes equal main's committed copy
[FAIL] B7 a revert-to-main still errors when an UNRELATED sibling lane is live (its tree holds main's bytes for that path): exit 1
[FAIL] B8 the OWNING lane's committed bytes, dirty in the shared checkout, do not wedge its own close-out: exit 2
[PASS] B9 a single untracked file under a tracked dir is owned when the sibling committed it: exit 1
[PASS] B10 a collapsed untracked dir with ONE stray file is still dirt (all-must-match, never any): exit 2
[FAIL] B11 a non-ASCII filename under a collapsed untracked dir is still owned: exit 2
[FAIL] B12 a PRUNABLE sibling worktree is not a live lane - its leftover copy is dirt: exit 1
[FAIL] B13 a STAGED sibling copy still errors, with the UNSTAGE remedy named: exit 2
[FAIL] B15 under core.autocrlf=true a CRLF working copy of the sibling's LF blob is still owned: exit 2
-- 14/20 passed --
[FAIL] K6g a NON-STRING `mutated` (null) refuses at the loader, exit 2, no traceback: exit=1 … Traceback
-- 6/7 passed --
```
B7's `exit 1` IS the hole: the revert was reported as `chore/SCC-12-other`'s working copy and the verdict cleared.

**GREEN** @ the review-fix commit (helper rewritten: base-blob predicate · own-lane owner · prunable skip · `STAGED` remedy · `hash-object --path` blob ids · `quotepath` on `ls-files`; loader refuses non-string `mutated`):
```
-- 20/20 passed --        (SCC-283 block)
-- 7/7 passed --          (K6 block)
-- 100/100 passed --      (test_task_preflight_contract.py, full)
-- 109/109 passed --      (test_task_preflight.py, full)
-- 34/34 passed --        (test_mutation_sweep.py, full)
```

### Mutation sweep — this lane ([sweep.json](sweep.json), 16 mutants drawn from the code, one a real deletion; M7 retired as EQUIVALENT under the base-blob predicate and replaced by M17)

Round 3, after the review-round fixes (16 mutants; M7 retired as equivalent, M11–M17 added):
```
-- sweep: 16 mutant(s) over 2 file(s) @ 02dc7b80 --
-- sweep clean: 16/16 killed by their declared case --
exit=0
```
| # | Mutant (from the code) | Killed by |
|---|---|---|
| M11 | `all(found)` → `any(found)` on a collapsed untracked dir | B10 |
| M12 | the base-blob predicate removed — a sibling "owns" every file it never touched | B7 |
| M13 | a `prunable` worktree counts as a live lane again | B12 |
| M14 | `hash-object --no-filters` — raw bytes again, dead on CRLF | B15 |
| M15 | the non-string `mutated` refusal disabled | K6g |
| M16 | staged sibling copies lose their remedy | B13 |
| M17 | the lane's own branch excluded from the owners again | B8 |

Round 2's table (M1–M10) stands, with M6 and M9 re-aimed at the rewritten lines and **M7 retired**: under the base-blob predicate `main`'s blob *is* the base blob, so making `main` a "sibling" can own nothing — the mutant became equivalent, which is the predicate doing the allowlist's job; the allowlist stays as a second belt and its own mutant is no longer informative.



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

**Re-stamped after the review-round fixes** (the last code-touching commit is `02dc7b80`; the receipt below is the one that governs):
```
[PASS] suite exit=0 83.1s @ d00e9d12
        receipt: gates/suite.json
…
52/52 files passed
```
Receipt: [gates/suite.json](gates/suite.json) — `result: pass`, `sha: d00e9d127418e0f4f72568897ebcbfc949f91be8`, `dirty_tree: false`. `d00e9d1` is the commit carrying this Code Review section; the tree outside `_artifacts/` is identical to `02dc7b80`, the verdict sha (`git diff --quiet 02dc7b80 d00e9d1 -- . ':(exclude)_artifacts/**'` → clean), so the receipt governs the code the verdict names.

---

## Code Review (2026-08-22)

Verdict: PASS @ 02dc7b804dd2b3a54afc1f7ed60a7d6613df7fa4
Suite evidence measured on the same sha — `gates/suite.json` re-stamped after the last code-touching change (see the receipt block below).

review-runtime: fan-out
lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none
findings:        0 decision · 12 patch · 0 defer   (8 noise-dismissed · 4 relevance kills)
dispositions:    per-lens: blind=4/2/1 · edge=6/0/0 · literal=6/1/0 · acceptance=6/4/1 · test-adequacy=2/5/2
severity_floor:  none (one `critical` and six `important` came back; every one that passed REAL · BEHAVIOUR · THIS DIFF was patched in this lane before this verdict — the floor is computed over what survives)
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — `declared_change_set.py diff` against the real diff at `72b3df2`; the `task_preflight.py` bullet was amended to name the parse fix and the review-round changes it now carries
notes:           lenses ran against the frozen diff at `72b3df2` (10 source/test/doc files; `_artifacts/`, `.opencode/` mirrors and `.sync-manifest.json` withheld as planning/generated surfaces). Verify wave: the three headline findings were REPRODUCED by the lenses themselves by execution (Literal R1/R2/R5; Edge S1/S1b/S3/S4/P1/probe_sweep) and then again by the assessor as RED tests (B7, B8, B11, B12, B13, B15, K6g) — execution is the verification record here; no separate verifier role was launched, recorded as `evidence-verifier · recovered-inline (cold — replaced by RED reproductions)`. Compound: the one interaction (allowing the lane's OWN branch as an owner while adding the base-blob predicate) is pinned jointly by B7 + B8 both green on the same code — `compound-synthesis · recovered-inline (cold)`. Disposition tail in ONE line: 36 findings came back; 24 assessed real (12 distinct patches, several found by 2–4 lenses on one anchor); 12 dismissed under the 2026-08-17 ruling (8 cosmetic/noise, 4 relevance kills). Calibration: the Blind Hunter's one `critical` (BH1) was correctly graded and was the most important finding of the lane; the `important` it put on "any mention counts" (BH3) contradicts acceptance A1 and was killed.

**Scope:** `origin/main@a634c35...HEAD`, 10 source/test/doc files + artifacts + 2 regenerated mirrors. **Method:** five parallel clean-context lenses → assessor disposition (REAL · BEHAVIOUR · THIS DIFF) → RED pins → fixes → full files → re-sweep → re-stamp.

### Findings (the authoritative table)

| # | file:line (at `72b3df2`) | severity | failure scenario | src | disposition |
|---|---|---|---|---|---|
| 1 | `task_preflight.py` `lane_of` (byte match vs `<lane>:<rel>`) | critical | a sibling's tree holds main's bytes for untouched paths → a hand-revert-to-main is owned and the close-out clears; dead `main`-by-name guard | blind+edge+literal (+acceptance on B4's pin) | applied — base-blob predicate; B7 + M12 |
| 2 | `task_preflight.py` `name == branch` exclusion | important | the lane that legitimately dirtied the shared checkout cannot close itself | blind (+test-adequacy: no RED test) | applied — own branch is an owner, own-lane wording; B8 + M17 |
| 3 | `task_preflight.py` `show.stdout == blob` | important | CRLF working copy never equals the LF blob on the PC → bucket dead there | blind+acceptance+edge+literal | applied — `hash-object --path` vs `rev-parse`; B15 + M14 |
| 4 | `mutation_sweep.py` loader | suggestion→important (reproduced) | `"mutated": null` crashes the sweep, exit 1 = "a mutant survived" | blind+edge+literal | applied — non-string refusal; K6g + M15 |
| 5 | `task_preflight.py` `ls-files` expansion | suggestion | non-ASCII name under a collapsed dir octal-quoted → never owned | literal+edge | applied — `-c core.quotepath=false`; B11 |
| 6 | `task_preflight.py` lanes loop | suggestion | a `prunable` worktree counts as live → stale copy "leave it alone" forever | edge | applied — prunable skip; B12 + M13 |
| 7 | `task_preflight.py` status-code tuple | suggestion | `MM`/`A ` staged content: index holds a third version / wrong remedy | acceptance+literal+edge | applied — ownable = ` M`/`??`; staged copies error with `git restore --staged`; B13 + M16 |
| 8 | `test_task_preflight_contract.py` B1 shape | important (coverage) | all-must-match untested; `all→any` survived (executed) | test-adequacy | applied — B10 + M11 |
| 9 | `test_task_preflight_contract.py` B4 | important (pin quality) | no precondition that the bytes equal `main:` | acceptance | applied — fixture assertion |
| 10 | single untracked FILE shape (ticket's `?? .claude/hooks/…`) | suggestion | no green case | acceptance | applied — B9 |
| 11 | plan Declared Change Set / Step 4 numbering | suggestion | parse fix undeclared inside a declared bullet; plan's mutant numbering stale vs `sweep.json` | acceptance | applied — plan bullets amended |
| 12 | `subprocess.run` without timeout | nitpick | wedged git hangs per path × lane | literal | applied — compare goes through `wf.git` (timeout 60) |
| — | "any mention counts" (`subject_keys`) | important (lens) | a trim commit naming left-behind keys evidences them | blind | dismissed — relevance leg 3: acceptance A1 says *anywhere*, verbatim |
| — | `LANE_BRANCH_RE` allowlist vs base denylist | suggestion | other prefixes non-sibling (fail-closed) | acceptance | dismissed — documented design choice (SOP names the three prefixes); now a second belt behind the base-blob predicate |
| — | `claude/`/`epic/` regex alternatives unexercised · `and not owned` info-line text · over-matching SCC-282 mutant | suggestion | symmetry coverage / text only / fixture-equivalent | test-adequacy | dismissed — relevance leg 1 (no realistic path to a wrong outcome) |
| — | joined-owner grammar · short sha wording · `KEY_RE` matches `UTF-8` · line-vs-anchor wording · plan/diff signature drift · `here` equivalent mutant · `code != 2` leniency | nitpick | cosmetic / no wrong outcome | blind+acceptance+literal+test-adequacy | dismissed — noise (counted) |

### Gates (Step 3 — run bare, pasted)

| Gate | Result |
|---|---|
| Enforcement suite | `52/52 files passed`, exit 0 — receipt `gates/suite.json` (re-stamped on the final sha; block below) |
| Toolkit lint | `-- 0 error(s), 0 warning(s), 8 info --` |
| Assertion evidence | `--case "K6"` 7/7 · `--case "SCC-170 partial"` 17/17 · `--case "SCC-283"` 20/20 — all GREEN now, each was RED first (pasted above) |
| SOP currency | `sop_currency.py --paths <the 16 changed> --message "SCC-283 …"` → exit 0; CONTROL without the SOP doc → `Commit rejected.` |
| Link + anchor | 0 new links / `#L` anchors in the added markdown; named paths are fixture paths in test comments |
| Door parity | n/a — no command added, renamed or deleted; mirrors regenerated by `sync-agents.ps1` |
| py_compile | OK on all five changed `.py` files |

### Acceptance matrix (Step 2 — imported from the Acceptance Auditor, `source: review`, plus the assessor's evidence)

| Item | Proof |
|---|---|
| C1 | K6a/K6b/K6c green; loader `k not in m` vs `not m.get(k)` split |
| C2 | K6d/K6e — message says ABSENT and EMPTY |
| C3 | K6f — the LOADER's `EMPTY original` message, never the anchor-count fallback (M5) |
| C4 | SCC-244 sweep `27/27` with M16/M23/M26 as `""` deletions |
| C5 / A4 / B5 | suite receipt pass, 52/52 |
| A1 | `SCC-282 …` cases 17/17; `subject_keys` on the verbatim `d9d9a9d` subject → `{SCC-244, SCC-253}`; live read matched |
| A2 | M1/M2 killed |
| A3 | `smh-close-task-merge-tree.md` partial step 1 + `work-consolidation.md` rule 2 row + `jira.md:356` + `smh-plan-task.md:164` + SOP — all read "named in" |
| B1 | B1 (untracked dir) · B5 (tracked-modified first line) · B9 (untracked file) · B15 (CRLF) |
| B2 | B2 control · B10 mixed dir · B12 prunable |
| B3 | B3 · M6 |
| B4 | B4 with the bytes-equal-main precondition · **B7 with a live sibling** · M12 |
| (review) | B8 owning lane · B13 staged remedy · K6g non-string |

Beyond the list: nothing — the parse fix and the review-round changes are named in the plan bullet and in this walkthrough.

### Clean-Code Gate — PASS

**Machine floor**
- run_all.py       : PASS — 52/52 files, exit 0 (receipt)
- workflow_lint    : PASS — 0 errors, 0 warnings
- sop_currency     : PASS — SOP staged with every usage-surface commit; control refuses
- py_compile       : PASS — task_preflight.py, mutation_sweep.py, three test files
- link + anchor    : PASS — 0 new links; 0 dead
- door parity      : n/a — no command added/renamed
- lint / types     : not applicable to this repo (no venv, no ruff, no tsc)

**Judgment pass (§2A comment contract · §2C conventions):** every new block carries `SCC-28x` provenance and the reason (7 keyed comment blocks); no stale `AIDEV-NOTE` touched; no unowned TODO; no personal name in `.agents/` bodies; docs spell `python3` with the PC rule stated once in the SOP; no generated file hand-edited (mirrors via the sync); no new gate, so nothing ships warn-only. §2B imported from the findings table above.

| # | file:line | Severity | Category | Finding | Disposition |
|---|---|---|---|---|---|
| 1 | `.agents/scripts/task_preflight.py` (status-code comment) | CONCERNS | comment-contract | the comment named rename/deletion/conflict while the tuple also excluded staged codes | applied — `OWNABLE`/`STAGED` named constants, comment says what each excludes |

### Step 0.7 — re-derivation (against `origin/main` fetched at review time)

1. **Moved under this diff:** nothing — `origin/main` is still `a634c35`, the lane's base; `theirs` = 0 files, so no path, rule pointer or script this diff references changed on `main`.
2. **True overlap + merge-tree:** overlap ∅ (16 mine ∩ 0 theirs); `git merge-tree --write-tree HEAD origin/main` → clean tree, no conflict messages.
3. **Live sibling lanes and landing order:** `scc-285` (touches `.sync-manifest.json` + `smh-quick-dev.md`/`smh-code-review.md` — none in this set beyond the manifest, which whichever lane lands second regenerates), `SCC-280` (dirty `jira.md` at lines 17–27; mine is line 356 — trivial absorb either way), `SCC-287`, `SCC-288`, `SCC-294` (docs only, disjoint). No lane must land first; no absorb was needed.

**Changes applied:** the 12 patches above, all in this lane, red-first, before this verdict; the walkthrough body, evidence and checklist refreshed to the final state.

## Your Actions

What landed is above. Nothing here is owed to you but the close-out decision; every board write (three riders to `Done`, then SCC-281) is the ceremony's and runs inside `/smh-close-task-merge-tree`.

- SCC-293 (cycle 7) is open and empty, holding `running-bug-list` — the next home for discovered work.
- `jira.md:356` changed one clause; SCC-280's tree has an uncommitted `jira.md` in another section. Whichever lands second absorbs a trivial merge.
