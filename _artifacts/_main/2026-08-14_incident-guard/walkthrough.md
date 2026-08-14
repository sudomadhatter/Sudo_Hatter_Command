---
type: walkthrough
story: SCC-148
---

# SCC-148 — task_preflight misroutes a live incident branch (the incident/ guard is dead code)

## Task Checklist

- [x] Plan written, self-audited (GO), operator-reviewed (3 plan defects found and folded in), `approved`
  - Review F1: the stale `incident/SCC-11-thing` test tuple would have gone RED after the fix, unpredicted
  - Review F2: the planned key-set pin was order-blind — a check that could not fail for this ticket's own bug class; shadowing assertion added
  - Review F3: the armed SOP-currency gate was unaddressed; `[sop-ok]` pre-declared with verification
- [x] RED first: 2 of 4 new cases failing, each for the right reason (misroute reproduced verbatim; key-set pin caught the dead entry)
- [x] GREEN: `WRONG_LANE` reordered (`claude/incident-` before `claude/`), dead `incident/` entry removed — 105/105
- [x] Prose synced same commit: `git-policy.md:210` + `scripts/INDEX.md` task_preflight row
- [x] Mutation sweep — 5 declared, **M4 SURVIVED the first pass** (nothing pinned the anchored
  scan); finding fixed with a case seen red under the mutant, re-sweep 5/5 killed
  - The first sweep run was timeout-killed mid-mutant and **left a mutant on disk** — caught by
    `git status` + restore, exactly the RESTORE hazard the doctrine names (SCC-144 had the same)
- [x] Full suite bare: run_all 23/23 files, 1878/1878 cases, exit 0 (1875 + 3, exactly additive);
  workflow_lint --toolkit-only 0/0 exit 0; check_maps --depth3-only --strict exit 0
- [ ] `/smh-code-review` verdict

## Evidence

### Acceptance 1 — RED test first, failing for the right reason

The real shape `/cicd-mobile-error-team` creates (`claude/incident-<short-id-lower>`), fed to
today's preflight — the misroute reproduced verbatim before any fix:

```
[ERROR] branch: claude/incident-abc123 is not a task branch - a story branch lands on its
        EPIC branch at close-out, never on main. Use /cicd-update-sprint-memory.
```

RED run (`python3 .agents/scripts/tests/test_task_preflight.py`, pre-fix):

```
[PASS] SCC-148 claude/incident-* (the real shape) is refused: exit 2
[FAIL] SCC-148 ...naming /cicd-mobile-error-team, never the story close-out
[FAIL] SCC-148 WRONG_LANE holds exactly the prefixes real commands create: got ['claude/', 'epic/', 'incident/']
[PASS] SCC-148 no WRONG_LANE entry is shadowed by an earlier prefix (first-match scan)
-- 103/105 passed --
```

Which line raised, and why it is the RIGHT red: the misroute check failed on the routing
assertion (the output named `/cicd-update-sprint-memory`), not in setup; the key-set pin failed
naming the actual stale keys. The shadow check **passes pre-fix by design** — today's table has
no shadowing (its bug is a dead-by-nonexistence entry plus the misroute); the shadow assertion
exists for the *future* re-sort that would re-kill the fix under a green set pin (plan review F2).
The stale tuple `("incident/SCC-11-thing", "/cicd-mobile-error-team")` was rewritten in the same
edit — post-fix it would have gone red for a predicted, uninteresting reason (falls through to the
shape regex).

### Acceptance 2 — post-fix routing, both halves

GREEN run (post-fix):

```
[PASS] SCC-148 claude/incident-* (the real shape) is refused: exit 2
[PASS] SCC-148 ...naming /cicd-mobile-error-team, never the story close-out
[PASS] SCC-148 WRONG_LANE holds exactly the prefixes real commands create: got ['claude/', 'claude/incident-', 'epic/']
[PASS] SCC-148 no WRONG_LANE entry is shadowed by an earlier prefix (first-match scan)
-- 105/105 passed --
```

The pre-existing `claude/SCC-11-thing` (ordinary story branch) control still refuses naming
`/cicd-update-sprint-memory` — the reorder did not break the case the table already got right.

### Acceptance 3 — no dead entry, guarded both ways an entry dies

Two module-level assertions on the imported `WRONG_LANE` (not grepped prose):
- **Key-set pin** — exactly `{"epic/", "claude/incident-", "claude/"}` — kills
  dead-by-nonexistence. Seen red pre-fix (above).
- **Shadowing assertion** — no earlier entry is a prefix of a later one, modeled on the scan's
  first-match `startswith` semantics — kills dead-by-shadowing, which a set pin is structurally
  blind to. Proven able to fail by mutation M1 below.

### Acceptance 4 — one prefix, system-wide, same commit

`git-policy.md:210-212` now reads `claude/incident-*` (and notes the branches match the
`claude/*` glob, so a resume reading that listing must skip the `incident-` infix);
`scripts/INDEX.md`'s task_preflight row names the corrected scan order and why it is
load-bearing. Sweep for any surviving bare prefix in the three touched files:

```
$ grep -rn "incident" <touched files> | grep -v "claude/incident" | <noise filter>
(only this walkthrough's own prose matches)
```

### Acceptance 5 — the SOP gate, cleared as a decision

`[sop-ok]` carried on the fix commit: verified before commit that the SOP's `task_preflight.py`
row (workflows_testing_SOP.md:1307) does not enumerate the `WRONG_LANE` prefixes, so nothing in
the SOP becomes false; the change corrects a refusal message's routing, no operator-typed surface.

### Full suite at the code sha (2727ec1), every command bare

```
$ python3 .agents/scripts/tests/run_all.py
== task_preflight ==
-- 106/106 passed --
23/23 files passed
[exited with code 0]        # 1878/1878 cases total

$ python3 .agents/scripts/workflow_lint.py --toolkit-only
-- 0 error(s), 0 warning(s), 8 info --   # exit 0

$ python3 .agents/scripts/check_maps.py --depth3-only --strict
# exit 0  (after adding this session's ledger row — test_check_maps F2 caught the
# missing row mid-lane and blocked, exactly as SCC-138 built it to)
```

**Additivity, closed exactly:** main's baseline 1875 (recorded at SCC-145's landing, zero
SIGNAL) + 3 net cases here (−2 rewritten stale tuple, +4 SCC-148 guards, +1 anchored-scan
survivor case) = **1878**. Suite ran bare in the background and its exit code read directly —
the first in-lane run was piped through `tail` and printed the pipe's exit, not the suite's,
which is the `piping-a-gate-hides-its-exit-code` trap; re-run bare before anything was believed.

### Mutation sweep — table DECLARED BEFORE MUTATING (tests-must-gate-for-real § Mutation Testing)

All mutants drawn from `task_preflight.py`'s code (the dict + its scan), not from the cases.
One sweep, restore in a trap, `git status` checked clean after.

| # | Mutant (edit to task_preflight.py) | Technique | Named case that must kill it |
|---|---|---|---|
| M1 | Swap the two `claude/*` entries back (generic before specific) | INVERT (the original bug, reintroduced) | `SCC-148 no WRONG_LANE entry is shadowed by an earlier prefix` — and this is the mutation that proves the shadow check CAN fail |
| M2 | Delete the `claude/incident-` entry entirely | delete-the-guard | `SCC-148 ...naming /cicd-mobile-error-team, never the story close-out` (misroutes again) + the key-set pin |
| M3 | Reintroduce the dead `incident/` entry (append) | reintroduce-drift | `SCC-148 WRONG_LANE holds exactly the prefixes real commands create` |
| M4 | `branch.startswith(prefix)` → `prefix in branch` in the scan loop | operator swap | `chore/` shape cases — a chore branch whose slug contains a lane word must not be refused; verified against the suite's chore-branch controls |
| M5 | `branch.startswith(prefix)` → `branch == prefix` | operator swap | every wrong-lane case (`epic/`, `claude/`, `claude/incident-` all pass through to the shape error, dropping their named commands) |

Results — one sweep, restore in a trap, `git status` verified after:

```
== M1: exit=1 failing_cases=2
    [FAIL] SCC-148 ...naming /cicd-mobile-error-team, never the story close-out
    [FAIL] SCC-148 no WRONG_LANE entry is shadowed by an earlier prefix (first-match scan):
           unreachable: [('claude/', 'claude/incident-')]
== M2: exit=1 failing_cases=2
    [FAIL] SCC-148 ...naming /cicd-mobile-error-team, never the story close-out
    [FAIL] SCC-148 WRONG_LANE holds exactly the prefixes real commands create: got ['claude/', 'epic/']
== M3: exit=1 failing_cases=1
    [FAIL] SCC-148 WRONG_LANE holds exactly the prefixes real commands create:
           got ['claude/', 'claude/incident-', 'epic/', 'incident/']
== M4: exit=0 failing_cases=0
    M4 SURVIVED
== M5: exit=1 failing_cases=3
    [FAIL] epic/ refusal names /cicd-push-e2e
    [FAIL] claude/ refusal names /cicd-update-sprint-memory
    [FAIL] SCC-148 ...naming /cicd-mobile-error-team, never the story close-out
```

**M4 survived — a finding, per the doctrine.** The declared kill ("the suite's chore-branch
controls") was wrong: no fixture branch embeds a lane word, so nothing pinned that the scan is
*anchored* — `prefix in branch` is true for every wrong-lane branch (prefix at position 0) and
false for every existing chore fixture. `BRANCH_RE`'s slug group is `.+`, which matches slashes,
so `chore/SCC-11-docs-for-epic/pages` is git-legal and shape-legal — and the substring scan
wrong-lanes it to `/cicd-push-e2e`. Fixed with a new case, proven both ways:

```
(M4 re-applied)  == M4 re-sweep: exit=1 failing=1
    [FAIL] SCC-148 a chore slug embedding a lane word is not wrong-laned (anchored scan)
(restored)       -- 106/106 passed --
```

**Final: 5/5 killed.** Commit `2727ec1` carries the survivor fix.

**Process note, recorded because it is this lane's own subject:** the first sweep invocation was
timeout-killed between mutants and **left a mutant on disk** — caught by the restore trap +
`git status` re-check, which is exactly why RESTORE-on-interrupt is a named technique
(SCC-144's timeout-killed sweep left `commit-msg-jira.sh` mutated the same way). The remaining
mutants were re-run with an adequate timeout; every result above is from a verified-clean start.

## Code Review (<date>)

(appended by /smh-code-review)

## Your Actions

- The branch is local-only until review; close-out is yours via `/smh-close-task-merge-tree`
  (typing it is the merge sign-off).
- Proposed NEW ticket (operator's call, not minted): `merge-target-guard.sh` carries SCC-148's
  twin — its `incident-*` carve-out comment (line 51) is dead: no case arm exists, and the real
  `claude/incident-*` matches the `claude/*)` arm (line 151), so an emergency LOCAL merge of an
  incident hotfix to `main` would be refused as "a claude/* story lane merges into ITS epic/*
  branch". Low reach (incident merges land via GitHub PR, which never runs local hooks) but the
  same confidently-wrong-under-pressure shape. The SOP's §gate-table row (line 1304) repeats the
  bare `incident-*` pattern and would ride the same fix.
- Assessed, from your ticket note: "preflight runs twice" does not hold against current source —
  `task_preflight.py` is invoked exactly once in the flow (`/smh-close-task-merge-tree` Step 1);
  `/smh-code-review` never calls it. The close-out's Step 4 child re-check is a documented
  second *layer* (board-reachability), not a second run. No change made.
