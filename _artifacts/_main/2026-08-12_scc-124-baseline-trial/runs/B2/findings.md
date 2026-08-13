# Run B2 — house `code-review-engine` (pack-primed, steps 01–04)

Caller contract: identical to B1 (REPO/WORKTREE=fixture @ e6354d3, review_mode=full,
EVIDENCE_PACK=runs/B2/pack_used.txt hash-verified = frozen, FINDINGS_SINK=this file).

Step-01: 4/4 lenses ok, parallel, pack-primed. Step-02: pass-through (SCC-127 pending).
Step-03: 32 raw diff-findings → 22 unique (10 merges); severities normalized.

## Findings (unresolved first)

- [ ] [Review][Decision] Case A hard-couples the suite to per-machine git config (fresh clone = red for environment) [test_hooks_armed.py:436] — important; blind
- [ ] [Review][Decision] claims_gates reads jira.conf from filesystem against the module's index doctrine (test P depends on it) [hooks_armed.py:128] — suggestion; blind
- [ ] [Review][Patch] Flag/script tracking-state mismatch family reads ARMED: flag rm'd from disk while hooks read disk; inner scripts git-rm'd from index with dispatchers tracked; orphan flag skipped (violates AC2) [hooks_armed.py:122,175-177] — important; blind+edge+acceptance
- [ ] [Review][Patch] NOT CLEAR verdict branch unreachable — and zero test coverage would have exposed it (pin or delete) [task_preflight.py:341] — important; blind+acceptance+test
- [ ] [Review][Patch] Tests D/F/N chmod-based → red on Windows [test_hooks_armed.py:103] — important; edge
- [ ] [Review][Patch] `~`-prefixed core.hooksPath not expanded → false block on a correctly armed machine [hooks_armed.py:145] — important; edge
- [ ] [Review][Patch] AC6 pins `--global` remedy the code deliberately rejects; case B substring can't prove the remedy prints [hooks_armed.py REMEDY] — important; blind+acceptance
- [ ] [Review][Patch] Tracked non-hook/nested file under .githooks/ becomes a required executable (pathspec `*` crosses `/`) [hooks_armed.py:121] — suggestion; blind+edge
- [ ] [Review][Patch] Unset hooksPath → 1+N errors printing "(None)" [hooks_armed.py:140] — suggestion; blind+edge
- [ ] [Review][Patch] Non-repo / nonexistent --repo misdiagnosed "no hooks tracked" [hooks_armed.py:71,91] — suggestion; blind+edge
- [ ] [Review][Patch] Never-claimed-gates repo has no e2e printed-verdict test (M4 warn-downgrade proven only at unit seam) [test_task_preflight.py] — suggestion; test
- [ ] [Review][Patch] is_executable() nt branch untested from the Mac [hooks_armed.py:103] — suggestion; test
- [ ] [Review][Patch] git_root() subdir walk-up fix unpinned [hooks_armed.py:91] — suggestion; test
- [ ] [Review][Patch] AC4's named fixture (hooksPath unset) never driven through preflight stdout [test_task_preflight.py] — nitpick; acceptance
- [ ] [Review][Patch] TOCTOU: file deleted between is_file() and stat() crashes scan mid-close-out [hooks_armed.py:105] — nitpick; edge
- [ ] [Review][Patch] Corrected two-cause wrong-key message not pinned (old substring only) [test_task_preflight.py:188] — nitpick; test
- [ ] [Review][Patch] hooks_armed --json output never validated [hooks_armed.py:263] — nitpick; test
- [ ] [Review][Patch] Test Q hardcodes --expect-key SCC-110; assertions ignore exit + findings [test_hooks_armed.py:621] — nitpick; blind
- [ ] [Review][Patch] Preflight JSON carries findings twice in divergent shapes [task_preflight.py:318] — nitpick; blind
- [ ] [Review][Patch] INDEX.md trailing space + row/paragraph order broken + 2,300-char wall [.agents/scripts/INDEX.md:9] — nitpick; blind
- [ ] [Review][Defer] AC3 extraction rejected-on-evidence; acceptance row never updated [test_main_push_gate.py] — suggestion; acceptance — documented deviation
- [ ] [Review][Defer] Walkthrough self-contradicts 59/59 vs 58/58 [walkthrough] — suggestion; blind+acceptance — landed record debt

DEFERRED_WORK bullets (no path supplied — returned here): AC3 acceptance-row drift ·
59/59-vs-58/58 contradiction — from: code review of SCC-110 trial re-run B2 (2026-08-12).

## Engine summary

```
lenses_run:      4/4   (blind ok · edge ok · acceptance ok · test-adequacy ok)
lenses_na:       none
findings:        2 decision · 18 patch · 2 defer   (0 dismissed)
severity_floor:  CONCERNS   (important findings in decision/patch; no critical)
notes:           verification pass not yet installed (SCC-127) — all findings verification: none.
                 EVIDENCE_PACK supplied, hash-verified; blind lens observed the pack's
                 task_preflight.py section truncates at the 16k char cap mid-line (showing 11 of
                 686 lines for that file) — cap behavior, recorded for SCC-125/126 tuning.
                 Trial containment: findings are evidence, not fixes (landed history).
```
