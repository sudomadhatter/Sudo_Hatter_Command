# Run B1 — house `code-review-engine` (pack-primed, steps 01–04)

Caller contract: REPO/WORKTREE=fixture @ e6354d3 · DIFF=inputs/diff.patch · HEAD_SHA=e6354d3 ·
review_mode=full · STORY_FILE=inputs/spec copy · EVIDENCE_PACK=runs/B1/pack_used.txt (hash-verified
= frozen) · FINDINGS_SINK=this file · ARTIFACT_DIR=runs/B1/ · DEFERRED_WORK absent.

Step-01: 4/4 lenses ok, parallel, pack-primed. Step-02: pass-through (SCC-127 pending), all
findings `verification: none`. Step-03: 34 raw → 25 unique (9 merges); severities normalized
(edge lens emitted no severity field → falls to `suggestion` per the unrecognized rule, except
where a merge partner asserted higher — revised-severity precedence does not apply, none exists).

## Findings (unresolved first)

- [ ] [Review][Decision] Live-repo cases A/Q + main_push cross-check couple the hermetic suite to per-machine git config (fresh clone = red for an environment reason) [test_hooks_armed.py:80] — important; blind+test
- [ ] [Review][Patch] Flag/script tracking-state mismatches read ARMED: script gone from INDEX with flag tracked (blind), flag gone from DISK while hooks read flags from disk (edge, cites pre-push-main-approval.sh:38), violates AC2 "reports every flag found" (acceptance) [hooks_armed.py:174] — important; blind+edge+acceptance
- [ ] [Review][Patch] `claims_gates` never demands the claimed gate's script be tracked — jira.conf + bare dispatcher + zero gate scripts certifies ARMED; the diff's own make_repo fixture proves it [hooks_armed.py:128 / test_task_preflight.py:705] — important; blind
- [ ] [Review][Patch] NOT CLEAR verdict branch unreachable (check() softens only no_hook_dir∧¬claims; BLOCKED always wins) [task_preflight.py verdict] — important; blind+acceptance
- [ ] [Review][Patch] Tests D/F/N chmod-based → guaranteed red on Windows (two-machine system; no os.name guard) [test_hooks_armed.py:103] — important; blind+edge
- [ ] [Review][Patch] AC6 remedy: plan still mandates asserting `--global` while shipped code forbids it; case B substring assertion cannot prove the remedy prints [hooks_armed.py REMEDY] — important; blind+acceptance
- [ ] [Review][Patch] is_executable() nt branch has zero regression coverage (fixed a HIGH; a revert stays green on the Mac) [hooks_armed.py] — important; test
- [ ] [Review][Patch] `~`-prefixed core.hooksPath not expanded → valid armed setup reads NOT ARMED [hooks_armed.py:145] — suggestion; edge
- [ ] [Review][Patch] Test fixtures inherit global/system git config (GIT_CONFIG_GLOBAL not nulled) → cases B/J/K spuriously fail on machines with global hooksPath [test_hooks_armed.py:86] — suggestion; edge
- [ ] [Review][Patch] Unset hooksPath → N+1 stacked errors interpolating "(None)" [hooks_armed.py:150] — suggestion; blind+edge
- [ ] [Review][Patch] Tracked non-hook/subdir file under .githooks/ → false NOT-EXECUTABLE blocking ERROR; nested paths flattened [hooks_armed.py:121] — suggestion; blind+edge
- [ ] [Review][Patch] Non-repo dir misdiagnosed "no hooks tracked" with inapplicable remedy [hooks_armed.py:71] — suggestion; blind+edge
- [ ] [Review][Patch] Preflight JSON carries findings twice in two shapes (+hooks_armed bool duplicates hooks.armed) [task_preflight.py:318] — suggestion; blind
- [ ] [Review][Patch] git binary absent → uncaught FileNotFoundError traceback [hooks_armed.py:93] — suggestion; edge
- [ ] [Review][Patch] AC4's named fixture (hooksPath unset, hooks tracked) never driven e2e through preflight stdout [test_task_preflight.py] — suggestion; acceptance
- [ ] [Review][Patch] git_root() subdir walk-up fix unpinned by any test [hooks_armed.py git_root] — suggestion; test
- [ ] [Review][Patch] CLI exit-code contract 0/1/2 + `--json` output unasserted (case J discards rc) [hooks_armed.py main] — suggestion; test
- [ ] [Review][Patch] Test Q hardcodes --expect-key SCC-110; passes only because preflight emits JSON regardless [test_hooks_armed.py:264] — nitpick; blind
- [ ] [Review][Patch] Case labels A…K,M,N,O,P,L,Q scrambled; walkthrough cross-refs compound it [test_hooks_armed.py:538] — nitpick; blind
- [ ] [Review][Patch] INDEX.md row/paragraph order mismatch + trailing space in backticked usage [.agents/scripts/INDEX.md:9] — nitpick; blind
- [ ] [Review][Patch] Absolute-hooksPath and flag-not-owed scan() branches untested [hooks_armed.py:165,195] — nitpick; test
- [ ] [Review][Defer] Walkthrough self-contradicts: 59/59 vs 58/58 for test_main_push_gate [walkthrough] — important; blind+acceptance — landed record debt
- [ ] [Review][Defer] AC3 extraction rejected-on-evidence; plan artifact never amended, 57/57 invariant moved [test_main_push_gate.py] — important; acceptance — documented deviation, adjudicated in the landed review
- [ ] [Review][Defer] SOP re-pins a literal census (646/16) right after declaring counts non-authoritative [workflows_testing_SOP.md:1248] — nitpick; blind — standing operator question (count-nag ticket)
- [ ] [Review][Defer] test_closeout_preflight.py never evidenced bare despite Step 6 naming it [walkthrough gates] — nitpick; acceptance — evidence debt on a landed story

DEFERRED_WORK bullets (caller supplied no path — returned here per SKILL.md):
- 59/59-vs-58/58 walkthrough contradiction · AC3 acceptance row vs shipped deviation · SOP census literal · closeout_preflight bare-run evidence — all from: code review of SCC-110 trial re-run (2026-08-12).

## Engine summary

```
lenses_run:      4/4   (blind ok · edge ok · acceptance ok · test-adequacy ok)
lenses_na:       none
findings:        1 decision · 20 patch · 4 defer   (0 dismissed)
severity_floor:  CONCERNS   (important findings in decision/patch; no critical)
notes:           verification pass not yet installed (SCC-127) — all findings hunter-asserted,
                 verification: none; EVIDENCE_PACK supplied and hash-verified; DEFERRED_WORK
                 absent, bullets returned above; STORY_FILE has no tasks section — no story write.
                 Trial containment: findings are evidence, not fixes (landed history).
```
