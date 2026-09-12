review-runtime: fan-out

# Walkthrough — SCC-448: Memory is Disposable (The Deletion Test)

Replaces the inverted "long-term-only" memory rule with the **Deletion Test**: *delete it in your head, then look at the damage: slower means memory; wrong means a rule and a ticket.* Codifies the invariant that a memory is never the only copy of anything, updates `/smh-memory-audit` with a Deletion Test sort pass and a `Promote to rule` candidate and apply disposition, syncs all mirrors, and rewrites `test_memory_long_term_rule.py` with AST-compliant block guards and mutation sweep coverage.

---

## Task Checklist

- [x] **Step 1: Implementation Plan & Pre-Dev Audit**
  - Implementation plan authored at `_artifacts/_main/2026-09-12_scc-448-memory-is-disposable/implementation_plan.md`
  - 3-lens pre-dev self-audit completed (`Audit verdict: GO`)
  - Explicit approval received from Mr. Hatter
- [x] **Step 2: RED Phase (Test-First)**
  - Rewrote `.agents/scripts/tests/test_memory_long_term_rule.py` to assert deletion test invariants
  - Observed genuine RED phase with 24 failing checks
- [x] **Step 3: GREEN Phase (Implementation)**
  - Created `.agents/rules/memory-is-disposable.md` with `model_decision` trigger and full rule law
  - Deleted retired rule `.agents/rules/agent-memory-is-long-term-only.md`
  - Updated floor rules in `.agents/rules/constitution.md` and `.roo/rules/constitution.md`
  - Registered `memory-is-disposable.md` in `.agents/rules/INDEX.md` and purged retired rule
  - Updated `AGENTS.md` §7 with deletion test, invariant, and rule link
  - Updated `.agents/commands/smh-memory-audit.md` with Deletion Test pass and `Promote to rule` bucket
  - Synced mirrors via `sync-agents.ps1 -NoGlobals` (`.opencode/commands/smh-memory-audit.md` and manifest)
  - Updated SOP documentation in `docs/_scc_sops_prds/workflows_testing_SOP.md` and `workflows_testing_SOP_changelog.md`
  - Reconciled doc-graph via `refresh_maps.py --repair` and verified `check_maps.py` clean
  - Added mutation sweep table `sweep.json` and killed 5/5 mutants via `mutation_sweep.py`
  - Stamped full clean suite receipt via `gate_receipt.py` (93/93 files passed, exit 0)
- [x] **Step 4: Adversarial Code Review**
  - Cut scoped diff patch via `review_scope.py` (10 files scoped, 9 withheld)
  - Fan-out review executed across 3 lenses (Edge Case Hunter, Acceptance Auditor, Test-Adequacy Auditor)
  - Stamped reproduction receipts for findings f1 and f2 via `repro_receipt.py`
  - Fixed reproduced findings in-lane (Step 5 handling for Promote to rule in `smh-memory-audit.md`, disk-backed counter-examples in `test_memory_long_term_rule.py`, SOP command atlas update, and operator name normalization)
  - Verified 5/5 mutants killed by `mutation_sweep.py`
  - Re-stamped clean full suite gate receipt at `66ab1636` (exit 0, dirty_tree: false)
- [ ] **Step 5: Closeout & Merge**
  - Close task and merge chore worktree branch to main via `/smh-close-task-merge-tree`

---

## Evidence

### 1. Step 2 RED Phase Output
```
== memory_disposable_rule ==
-- tree: scc-448-memory-is-disposable [chore/SCC-448-memory-is-disposable] - worktree --
[FAIL] constitution.md carries the disposable memory floor rule: constitution.md does not establish memory as disposable
[FAIL] constitution.md states the deletion test (slower means memory; wrong means a rule): constitution.md does not state the deletion test
[FAIL] constitution.md establishes the invariant: never the only copy: constitution.md does not state the invariant that memory is never the only copy
[FAIL] constitution.md links to memory-is-disposable rule: constitution.md does not reference memory-is-disposable
[FAIL] .roo/rules/constitution.md mirrors the disposable memory rule: .roo/rules/constitution.md does not mirror the disposable memory rule
[FAIL] memory-is-disposable.md exists on disk: missing file: .../.agents/rules/memory-is-disposable.md
...
-- 5/29 passed, 24 FAILED --
```

### 2. Step 3 GREEN Phase Output
```
== memory_disposable_rule ==
-- tree: scc-448-memory-is-disposable [chore/SCC-448-memory-is-disposable] - worktree --
[PASS] constitution.md carries the disposable memory floor rule
[PASS] constitution.md states the deletion test (slower means memory; wrong means a rule)
[PASS] constitution.md establishes the invariant: never the only copy
[PASS] constitution.md requires story-scoped facts to live in the story or artifacts
[PASS] constitution.md establishes the delete-on-sight duty for story-scoped memories
[PASS] constitution.md requires one-line chat narration on every memory write
[PASS] constitution.md links to memory-is-disposable rule
[PASS] constitution.md does NOT link to retired agent-memory-is-long-term-only rule
[PASS] .roo/rules/constitution.md mirrors the disposable memory rule
[PASS] retired agent-memory-is-long-term-only.md is deleted from disk
[PASS] memory-is-disposable.md exists on disk
[PASS] rule has YAML frontmatter
[PASS] rule trigger is model_decision
[PASS] rule frontmatter carries triggers keyword list
[PASS] rule articulates the deletion test: slower means memory; wrong means a rule
[PASS] rule articulates the invariant: never the only copy of anything
[PASS] rule forbids load-bearing rulings from living exclusively in memory
[PASS] rule defines delete-on-sight duty
[PASS] rule defines narrate-every-write duty
[PASS] rule defines qualifying memory categories
[PASS] rule defines prohibited memory categories
[PASS] rule articulates slower-means-memory counter-example
[PASS] rule articulates wrong-means-rule counter-example
[PASS] counter-example 1: fact whose loss makes agent wrong must be a rule
[PASS] counter-example 2: fact whose loss only makes agent slower is memory
[PASS] INDEX.md registers memory-is-disposable as on-demand
[PASS] INDEX.md omits retired agent-memory-is-long-term-only
[PASS] AGENTS.md section 7 incorporates the disposable memory mandate
[PASS] AGENTS.md section 7 does NOT reference retired agent-memory-is-long-term-only
[PASS] smh-memory-audit.md contains the deletion test pass
[PASS] smh-memory-audit.md contains Promote to rule candidate classification
[PASS] smh-memory-audit.md contains Step 5 Promote to rule handling
[PASS] workflows_testing_SOP.md states disposable memory rule and deletion test
[PASS] workflows_testing_SOP_changelog.md carries SCC-448 entry
-- 34/34 passed --
```

### 3. Mutation Sweep Output
```
== mutation_sweep @ scc-448-memory-is-disposable [chore/SCC-448-memory-is-disposable] - worktree ==
   /home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-448-memory-is-disposable
-- sweep: 5 mutant(s) over 5 file(s) @ 6ea8c327 --
KILLED    M1 constitution.md deletion test phrase dropped
            KILLED by constitution.md states the deletion test (slower means memory; wrong means a rule)
            -- filter '1 · constitution.md': matched 1/6 blocks --
KILLED    M2 memory-is-disposable.md trigger changed from model_decision
            KILLED by rule trigger is model_decision
            -- filter '2 · memory-is-disposable.md exists & old rule deleted': matched 1/6 blocks --
KILLED    M3 AGENTS.md §7 disposable mandate removed
            KILLED by AGENTS.md section 7 incorporates the disposable memory mandate
            -- filter '4 · INDEX.md and AGENTS.md': matched 1/6 blocks --
KILLED    M4 smh-memory-audit.md Promote to rule bucket stripped
            KILLED by smh-memory-audit.md contains Promote to rule candidate classification
            -- filter '5 · smh-memory-audit.md': matched 1/6 blocks --
KILLED    M5 workflows_testing_SOP.md disposable memory rule removed
            KILLED by workflows_testing_SOP.md states disposable memory rule and deletion test
            -- filter '6 · SOP and changelog': matched 1/6 blocks --
-- restore verified: bytes match, nothing was committed, and `git diff --quiet 6ea8c327` is clean --
-- full file, unfiltered: python3 .agents/scripts/tests/test_memory_long_term_rule.py -> exit 0 --
-- 34/34 passed --

-- sweep clean: 5/5 killed by their declared case --
```

### 4. Clean Full Suite Receipt
Receipt file: `gates/suite.json` @ `66ab1636`
```json
{
  "gate": "suite",
  "story": "scc-448",
  "result": "pass",
  "exit_code": 0,
  "sha": "66ab16367fa29c5ac9c2ae0682ea312cabe55fdf",
  "dirty_tree": false,
  "dirty_paths": [],
  "totals": null,
  "command": [
    "python3",
    ".agents/scripts/tests/run_all.py"
  ],
  "cwd": "/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-448-memory-is-disposable",
  "duration_s": 32.6,
  "recorded_at": "2026-09-12T22:17:36+00:00"
}
```

---

## Code Review (2026-09-12)

Verdict: PASS @ ed8f3cf9
suite-sha: 66ab1636

lenses_run:
- edge-case-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · recovered-inline — subagent tool process substitution stall, rerun inline
lenses_counted: 3/3
lenses_na: none

dispositions: per-lens: edge-case-hunter=2/0/3 · acceptance-auditor=0/0/1 · test-adequacy-auditor=1/0/0
drift: undeclared=0 · unimplemented=0 · incomplete=0 — plan declared change set reconciled clean with zero drift

Scope: 10 files in diff patch (`diff.patch` scoped via `review_scope.py`, 9 planning/mirror files withheld).
Method: Clean-room adversarial review fan-out (Edge Case Hunter, Acceptance Auditor, Test-Adequacy Auditor) with `repro_receipt.py` gate validation and in-lane fixes.

| # | file:line | sev | lens | failure scenario | repro | disposition |
|---|---|---|---|---|---|---|
| 1 | .agents/commands/smh-memory-audit.md:127,143 | important | edge-case-hunter | Step 5 missing handling for Promote to rule | f1 | fixed @4698d43e · pin test_memory_long_term_rule.py:5 · repro f1 |
| 2 | .agents/scripts/tests/test_memory_long_term_rule.py:36-44,128-136 | important | edge-case-hunter | Block 3 counter-examples tests local helper without disk read | f2 | fixed @4698d43e · pin test_memory_long_term_rule.py:3 · repro f2 |

dropped — no reproduction: 0
recorded: 3 (f3 suggestion: workflows_testing_SOP.md smh-memory-audit section updated; f4 suggestion: test_memory_long_term_rule.py categories check added; f5 nitpick: memory-is-disposable.md operator name fixed to Mr. Hatter)

### Step 0.7 — re-derivation
1. **References check**: No files or anchors referenced in this diff were moved, renamed, or deleted on `origin/main` (`BASE == origin/main`, zero upstream commits landed during build).
2. **True overlap & merge-tree**: Intersection of changed files with landed commits is empty; `git merge-tree --write-tree --messages HEAD origin/main` cleanly resolved with tree sha `3ba7f73b30f20442fa06d24b4b24d11c4b5a3be6` and 0 conflicts.
3. **Sibling lanes**: Live worktrees `/home/dlohn/Sudo_Hatter_Command` (`chore/SCC-186-standing-push`) and `/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/SCC-456-export` (`chore/SCC-456-teaching-edition-export`) touch independent subsystems with zero overlapping paths and no landing-order dependencies on disposable memory.

### Command-Centre Gates

| Gate | Command | Result | Notes |
|---|---|---|---|
| Enforcement suite | `python3 .agents/scripts/tests/run_all.py` | PASS (93/93) | Stamped at `gates/suite.json` @ `66ab1636` (duration 32.6s, exit 0, dirty_tree: false) |
| Toolkit lint | `python3 .agents/scripts/workflow_lint.py --toolkit-only` | PASS (0 errors, 0 warnings) | Clean |
| Assertion evidence | `python3 .agents/scripts/tests/test_memory_long_term_rule.py` | PASS (34/34) | All block assertions green |
| SOP currency | `python3 .agents/scripts/sop_currency.py` | PASS (exit 0) | SOP §2 and command atlas updated in same commit |
| Link + anchor | `python3 .agents/scripts/check_links.py --base origin/main` | PASS (13 files, 242 claims checked) | Clean, zero broken links |
| Door parity | `sync-agents.ps1 -NoGlobals` | PASS (exit 0) | `.opencode/commands/smh-memory-audit.md` byte-identical to master |

### Clean-Code Gate

Imported Step 3 machine floor results:
- `py_compile`: Clean on `.agents/scripts/tests/test_memory_long_term_rule.py`.
- `workflow_lint`: 0 errors, 0 warnings.
- `check_links`: Clean (242 path claims verified).
- Diff scoped: Zero banned patterns, zero secrets, zero dead code introduced.

---

## Your Actions

- [x] The merge itself — lands via this branch's PR

