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
- [x] Full suite bare at the dev sha: run_all 23/23 files, 1878/1878 cases, exit 0 (1875 + 3,
  exactly additive); workflow_lint --toolkit-only 0/0 exit 0; check_maps --depth3-only --strict exit 0
- [x] `/smh-code-review` — 5/5 lenses + verify wave + compound pass; 2 importants found and fixed
  in-lane (the close-out command's stale refusal row; the resume universal claim made newly false);
  a third same-class instance caught by the review-corrected repo-wide sweep (close-workingtree);
  suite re-run at the review-fix sha — Verdict: PASS @ b50da78 (section below)
  - The review changed the diff: 8 files → 13 (three command bodies + mirrors + manifest)

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
The stale tuple `("incident/SCC-11-thing", "/cicd-mobile-error-team")` was removed from the loop
and replaced by the standalone real-shape block (the loop's `split('/')[0]` labeling would have
collided) — post-fix the old tuple would have gone red for a predicted, uninteresting reason
(falls through to the shape regex). The review later added a dedicated bare-`incident/`
fall-through case, so that path is pinned again rather than merely absent.

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
load-bearing.

**The evidence here was rewritten by the review (compound finding 1):** the original sweep
covered only the three touched files — structurally incapable of finding a stale reference in
a file this lane forgot, and exactly such a file existed (`smh-close-task-merge-tree.md:147`,
found by the Literal lens, fixed in the review commit). The honest sweep is repo-wide over the
surfaces that can carry a branch prefix, run post-fix, pasted verbatim:

```
$ grep -rnE '`incident[-/]' .agents/commands/ .agents/rules/ .agents/scripts/*.py \
    --include="*.md" --include="*.py" | grep -v "claude/incident"
.agents/commands/cicd-mobile-error-team.md:17:  (`incident:<short-id>`)          # a GitHub label, not a branch
.agents/commands/cicd-mobile-error-team.md:234: (`incident-response.yml` ...)    # a workflow filename
.agents/rules/git-policy.md:212:  must skip the `incident-` infix ...            # this lane's own carve-out prose
.agents/rules/mobile-mode.md:48:  (`incident-response.yml` checks ...)           # a workflow filename
```

Zero bare branch-prefix survivors. Known and deferred with the follow-on ticket (outside this
sweep's command/rule scope, disclosed): `merge-target-guard.sh:51`'s comment and the SOP's
gate-table row 1304, both `.sh`/`docs/` surfaces carrying the old `incident-*` wording.

### Acceptance 5 — the SOP gate, cleared as a decision

`[sop-ok]` carried on the fix commit: verified before commit that the SOP's `task_preflight.py`
row (workflows_testing_SOP.md:1307) does not enumerate the `WRONG_LANE` prefixes, so nothing in
the SOP becomes false; the change corrects a refusal message's routing, no operator-typed surface.

Evidence (added by the review — the claim was true but unpasted):

```
$ git log d408ce6 -1 --format=%B | head -1
SCC-148 fix(preflight): route real incident branches to their lane; kill the dead incident/ entry [sop-ok]
# ...body carries the full [sop-ok] justification paragraph; the armed commit-msg gate accepted it.
$ python3 .agents/scripts/sop_currency.py --paths .agents/scripts/task_preflight.py \
    .agents/rules/git-policy.md .agents/scripts/INDEX.md \
    .agents/scripts/tests/test_task_preflight.py --message "<the subject above>"
# exit 0
```

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

## Code Review (2026-08-14)

Verdict: PASS @ b50da78
Suite evidence measured at b50da78 (the review-fix commit; the only later commit is this
artifacts-only walkthrough/plan commit, which per the gate's own rule does not invalidate it).

**Scope:** the SCC-148 diff, `main...HEAD` (8 files at review start, 13 after review fixes).
**Method:** house `code-review-engine` — 5 parallel clean-room lenses (`lens_budget: standard`),
then the verify wave (Evidence Verifier + Compound Synthesis, both dossier-backed via
`evidence_extract.py`), then triage; Step 0.7 re-derivation; command-centre gate; clean-code gate.

**Engine summary, as returned:**

```
lenses_run:      5/5   (blind ok · edge ok · literal ok · acceptance ok · test-adequacy ok)
lenses_na:       none
findings:        0 decision · 6 patch · 2 defer   (3 dismissed; 16 raw → 11 after dedupe, +5 compound)
severity_floor:  none   (both importants patched in-lane at b50da78; nothing surviving gates)
notes:           verify wave ran (16 raw findings; all 16 verified true, severities revised);
                 compound pass emitted 5; literal lens received 4/8 files (the 4 artifact docs
                 withheld as prose records — stated by the lens as its first line)
```

**Findings table (authoritative; verifier-revised severities):**

| # | file:line | sev | failure scenario | disposition |
|---|---|---|---|---|
| 1 | .agents/commands/smh-close-task-merge-tree.md:147 | important | the check table of the exact command this script backs promised the deleted bare `incident/` refusal "by name" and omitted `claude/incident-` — an operator at close-out reads a false claim (Literal lens, conf 0.9) | **applied** @ b50da78: row corrected; + bare-`incident/` fall-through case added so the row's claim has a machine behind it (compound 4) |
| 2 | .agents/rules/git-policy.md:210 ↔ .agents/commands/cicd-resume.md:56 | important | this lane's corrected rule line is the first written admission incident branches match the `claude/*` glob, making resume's universal "every claude/* listed is in-flight story work" newly false in writing; an agent resuming on a cold machine classifies an incident branch as parked story work (Literal, conf 0.85; 4 lenses converged) | **applied** @ b50da78 in the direction compound 3 constrained (implement in the consumer, never delete the rule sentence): the carve-out now lives in resume's own step list |
| 3 | .agents/commands/cicd-close-workingtree.md:326 | important-class (found post-triage by the corrected sweep) | the branch-DELETING command carried the same bare `incident-*` pattern (compound 2 named it a consumer whose failure escalates from misreport to prune) | **applied** @ b50da78: `claude/incident-*` + explicit never-sweep-a-listing line |
| 4 | .agents/scripts/tests/test_task_preflight.py:329 | suggestion | the anchored-scan case (sole M4 kill) asserted only string-absence — a crash's traceback contains neither pinned string, so the case would score green over a dead run (4 lenses independently; verifier conf 0.95) | **applied** @ b50da78: pins the positive post-scan marker `-> SCC-11` + `code in (0,1)` |
| 5 | .agents/scripts/task_preflight.py:66 | nitpick (verifier downgraded from suggestion) | the comment over-claimed the key-set pin verifies creator linkage; it verifies the exact set, forcing a conscious edit — the verifier ruled a derivation test would be the prose-pinning anti-pattern the repo just retired | **applied** @ b50da78: comment precision fix, mechanism unchanged |
| 6 | walkthrough Acceptance 4/5 | suggestion | Acceptance-4's sweep was scoped to touched files — structurally incapable of catching finding 1 (compound 1); Acceptance-5's claim was true but unpasted (verifier settled it with `git log` itself) | **applied**: repo-wide sweep run post-fix and pasted verbatim; commit-message + sop_currency evidence pasted |
| 7 | resume-claim consumer surfaces (cicd-boot-sprint-memory.md:100 · cicd-merge-epic-workingtrees Step 1 · cicd-update-sprint-memory.md:237) | suggestion | compound 2: the same universal claim has more consumers; merge-epic's inventory → land → prune path escalates a misclassified incident branch from misreport to swept-and-pruned | **deferred** → follow-on ticket (below), enlarged to the full consumer set; the two worst arms (resume, close-workingtree) are fixed in-lane |
| 8 | .agents/scripts/git-hooks/merge-target-guard.sh:51 + SOP:1304 | suggestion | the twin defect: dead `incident-*` carve-out comment, no case arm, real prefix matches `claude/*)` → STORY (pre-existing, not this diff's) | **deferred** → the same follow-on ticket (proposed at plan time) |
| 9 | wrong-lane reason-text pinning · tuple-wording nitpick · plan-ambiguity note | nitpick | reason strings are explanatory prose, the command token is the load-bearing half (verifier); tuple wording corrected in walkthrough; ambiguity already resolved in the doc | **dismissed** (3), each with the verifier's reasoning recorded here |

**Acceptance matrix (Step 2 — engine's Acceptance Auditor imported, source `review`):** all five
items delivered, each with its proving assertion in `## Evidence` above; items 4 and 5's evidence
strengthened by this review (repo-wide sweep; pasted commit message). Reverse direction: every
diff element traces to an acceptance item or a disposition in this table — nothing unjustified.

**Command-centre gate (each run bare, actual output in `## Evidence` and here):**
- Enforcement suite @ b50da78: `run_all.py` — 23/23 files, 1879/1879 cases, exit 0 (1875 main + 3 dev + 1 review case, exactly additive)
- `workflow_lint.py --toolkit-only`: 0 errors, 0 warnings, exit 0 (re-run after the command edits + sync)
- RED assertions re-run GREEN: test_task_preflight 107/107
- `sop_currency.py`: exit 0; both command-touching commits carry `[sop-ok]` with written justification
- Link + anchor: no new md links introduced; `check_maps.py --depth3-only --strict` exit 0
- Door parity: no command added/renamed/deleted; the 3 edited commands' mirrors regenerated via `sync-agents.ps1 -NoGlobals` (manifest committed)

### Clean-Code Gate (/smh-clean-code-audit, diff-scoped)
Machine floor: `workflow_lint --toolkit-only` 0/0 exit 0 · `py_compile` both changed `.py` exit 0 ·
`check_maps --depth3-only --strict` exit 0 · `sop_currency` exit 0 — all pasted above.
§2A comment contract: changed hunks carry why-comments matched to surrounding density (the ORDER
comment cites its incident and its guards; the test comments name which property each pins). §2C
conventions: house voice, no hand-edited generated surfaces (sync ran), explicit-path commits,
key-led subjects. §2B drift imported from Step 1: the lenses raised no over-engineering or bloat
findings; every addition traces to an acceptance item or a review disposition. **Result: clean.**

**Step 0.7 re-derivation (three lines):** nothing moved under this diff — `main`'s tip is the
merge-base (0677441), zero landed files since branch, merge-tree clean. True overlap with `main`:
none. Sibling lane `chore/SCC-147-lens-budget` is live with commits; single shared file
`_artifacts/_main/INDEX.md` (both prepend a ledger row — the predicted conflict class, resolved by
keeping both rows, either landing order); 147 also rewrites `smh-code-review.md`, which does not
overlap this diff.

**Changes applied:** findings 1–6 above, at b50da78; walkthrough refreshed (this section, the
evidence rewrites, the checklist). Nothing else changed.

## Your Actions

- ~~The branch is local-only until review~~ pushed; review PASS @ b50da78; close-out invoked by
  the operator mid-review and executed under that sign-off.
- **Proposed NEW ticket (operator's call, not minted) — enlarged by the review:** the incident
  branch-prefix taxonomy still has stale/unguarded copies outside this lane's scope:
  1. `merge-target-guard.sh:51` — dead `incident-*` carve-out comment, no case arm; real
     `claude/incident-*` matches `claude/*)` → STORY, so an emergency LOCAL merge of an incident
     hotfix to `main` is refused with wrong instructions (low reach — incident merges land via
     GitHub PR — but SCC-148's shape verbatim). SOP §gate-table row 1304 rides the same fix.
  2. Remaining consumers of the "claude/* on origin = story work" claim (compound finding 2):
     `cicd-boot-sprint-memory.md:100` · `cicd-merge-epic-workingtrees` Step 1 (inventory→prune —
     the escalating arm) · `cicd-update-sprint-memory.md:237` (an incident branch satisfies its
     "HEAD must be claude/*" precondition). The two worst arms (resume; close-workingtree's
     delete step) were fixed in this lane.
- Assessed, from your ticket note: "preflight runs twice" does not hold against current source —
  `task_preflight.py` is invoked exactly once in the flow (`/smh-close-task-merge-tree` Step 1);
  `/smh-code-review` never calls it. The close-out's Step 4 child re-check is a documented
  second *layer* (board-reachability), not a second run. No change made.
