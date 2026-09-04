# Walkthrough — SCC-386: Agent Memory is Long-Term Only

Ticket: [SCC-386](https://sudo-command.atlassian.net/browse/SCC-386) · Branch: `chore/SCC-386-memory-long-term-only` · Date: 2026-09-04

## Task Checklist

- [x] Floor rule update: Added long-term memory mandate bullet to [`.agents/rules/constitution.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/rules/constitution.md) under `## ✅ Always`.
- [x] Authored conditional rule: Created [`agent-memory-is-long-term-only.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/rules/agent-memory-is-long-term-only.md) defining the one test ("still true and useful after story closes"), qualifying/prohibited categories, delete-on-sight duty, and one-line chat narration duty.
- [x] Registered on-demand rule: Added entry to [`.agents/rules/INDEX.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/rules/INDEX.md) with intent triggers.
- [x] Front-door anchoring: Updated [AGENTS.md](file:///home/dlohn/Sudo_Hatter_Command/AGENTS.md) §7 (Persistence / Memory) to anchor the long-term memory mandate and delete-on-sight policy.
- [x] SOP and changelog currency: Updated [`workflows_testing_SOP.md`](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/workflows_testing_SOP.md) §2 and added changelog entry in [`workflows_testing_SOP_changelog.md`](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/workflows_testing_SOP_changelog.md).
- [x] Assert-first test suite: Authored [`test_memory_long_term_rule.py`](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/tests/test_memory_long_term_rule.py) (18/18 passing).
- [x] Synchronized Zoo Code floor copy: Updated [`.roo/rules/constitution.md`](file:///home/dlohn/Sudo_Hatter_Command/.roo/rules/constitution.md) to match master.
- [x] Memory sweep: Audited `~/.claude/projects/*/memory/`, `_artifacts/_memory/`, and `Projects/AGY_AVIATIONCHAT/_artifacts/_memory/`; confirmed no ephemeral story-scoped notes remain.
- [x] The merge itself — lands via this branch's PR

## Evidence

### RED Test Output
```
== memory_long_term_rule ==
-- tree: scc-386-memory-long-term-only [chore/SCC-386-memory-long-term-only] - worktree --
[FAIL] constitution.md carries the long-term memory floor rule: constitution.md does not mention long-term memory
[FAIL] constitution.md requires story-scoped facts to live in the story or artifacts: constitution.md does not state that story-scoped facts go in the story or artifacts
[FAIL] constitution.md establishes the delete-on-sight duty for story-scoped memories: constitution.md does not mention deleting story-scoped memories on sight
[FAIL] constitution.md requires one-line chat narration on every memory write: constitution.md does not state the one-line chat narration duty
[FAIL] constitution.md links to agent-memory-is-long-term-only rule: constitution.md does not reference agent-memory-is-long-term-only
[FAIL] agent-memory-is-long-term-only.md exists on disk: missing file: .../.agents/rules/agent-memory-is-long-term-only.md
[FAIL] rule has YAML frontmatter: missing frontmatter delimiters
[FAIL] rule trigger is model_decision: trigger is not model_decision
[FAIL] rule frontmatter carries triggers keyword list: triggers list does not include memory keyword
[FAIL] rule articulates the one test: still true and useful after story closes: rule does not contain the qualifying test
[FAIL] rule enumerates qualifying categories (operator preferences, quirks, standing rulings): rule missing one or more qualifying categories
[FAIL] rule enumerates prohibited categories (measurements, bug mechanisms, temporary gate mismatches): rule missing one or more prohibited categories
[FAIL] rule defines delete-on-sight duty: rule does not specify delete-on-sight duty
[FAIL] rule defines narrate-every-write duty: rule does not specify narrate-every-write duty
[FAIL] INDEX.md registers agent-memory-is-long-term-only as on-demand: INDEX.md missing on-demand row for agent-memory-is-long-term-only.md
[FAIL] AGENTS.md section 7 incorporates the long-term memory mandate: AGENTS.md does not mention agent-memory-is-long-term-only in memory section
[FAIL] workflows_testing_SOP.md states long-term memory rule: workflows_testing_SOP.md missing long-term memory rule
[FAIL] workflows_testing_SOP_changelog.md carries SCC-386 entry: workflows_testing_SOP_changelog.md missing SCC-386 entry
-- 0/18 passed --
```

### GREEN Test Output
```
== memory_long_term_rule ==
-- tree: scc-386-memory-long-term-only [chore/SCC-386-memory-long-term-only] - worktree --
[PASS] constitution.md carries the long-term memory floor rule
[PASS] constitution.md requires story-scoped facts to live in the story or artifacts
[PASS] constitution.md establishes the delete-on-sight duty for story-scoped memories
[PASS] constitution.md requires one-line chat narration on every memory write
[PASS] constitution.md links to agent-memory-is-long-term-only rule
[PASS] .roo/rules/constitution.md mirrors the long-term memory rule
[PASS] agent-memory-is-long-term-only.md exists on disk
[PASS] rule has YAML frontmatter
[PASS] rule trigger is model_decision
[PASS] rule frontmatter carries triggers keyword list
[PASS] rule articulates the one test: still true and useful after story closes
[PASS] rule enumerates qualifying categories (operator preferences, quirks, standing rulings)
[PASS] rule enumerates prohibited categories (measurements, bug mechanisms, temporary gate mismatches)
[PASS] rule defines delete-on-sight duty
[PASS] rule defines narrate-every-write duty
[PASS] INDEX.md registers agent-memory-is-long-term-only as on-demand
[PASS] AGENTS.md section 7 incorporates the long-term memory mandate
[PASS] workflows_testing_SOP.md states long-term memory rule
[PASS] workflows_testing_SOP_changelog.md carries SCC-386 entry
-- 19/19 passed --
```

## Suite Ledger

| Scope | Command | Duration | Result | Why this run |
|---|---|---|---|---|
| targeted | `python3 .agents/scripts/tests/test_memory_long_term_rule.py` | 0.8s | PASS 19/19 | RED-to-GREEN verification of the new rule |
| full | `python3 .agents/scripts/tests/run_all.py --jobs 4` | 33.5s | PASS 73/73 @ `41517898` | Full suite certification at clean HEAD |

## Code Review (2026-09-04)

Verdict: PASS @ 41517898
Suite evidence measured on 41517898 (`gates/suite.json`, PASS exit 0).

review-runtime: fan-out
lens_isolation: worktree
lenses_run:
- test-adequacy-auditor · ok
- acceptance-auditor · ok
- literal-correctness-hunter · ok
- edge-case-hunter · ok
- blind-hunter · ok
lenses_counted: 5/5
lenses_na: none
findings: 0 decision · 4 patch · 0 defer (0 noise-dismissed · 0 relevance kills)
dispositions: per-lens: test-adequacy-auditor=4/0/0 · acceptance-auditor=0/0/0 · literal-correctness-hunter=2/0/0 · edge-case-hunter=5/0/0 · blind-hunter=4/0/0
severity_floor: none
drift: undeclared=0 · unimplemented=0 · incomplete=0 — clean
notes: all 19 long-term memory rule assertions pass; full standing suite (73/73) green.

### Findings Resolved

| Lens | Finding | Resolution |
|---|---|---|
| Blind Hunter / Literal / Edge Case | Dangling relative link `agent-memory-is-long-term-only.md` in `.roo/rules/` | Converted to code span `` `agent-memory-is-long-term-only` `` to match `constitution.md` conventions |
| Blind Hunter / Edge Case | Delete-on-sight concurrency hazard | Explicitly clarified that memory store deletions on active lanes stay on-branch and must not delete in-flight notes |
| Edge Case Hunter | Bag-of-words trigger hook noise on `save this` | Replaced with `save to memory` to prevent false positive rule loads on arbitrary files |
| Test-Adequacy Auditor | Mutation hole in `or` test and frontmatter masking | Switched to `and`, verified against markdown body, and added `.roo/rules/` mirror assertion |

### Step 0.7 — the blast radius, re-derived against current main

1. What moved: absorbed PR #146 (SCC-387 antigravity file read grants). No referenced rule or test files were deleted or renamed on main.
2. What it changes here: merge conflict in `_artifacts/_main/INDEX.md` was resolved cleanly by keeping both session rows in chronological order; `workflows_testing_SOP.md` auto-merged cleanly.
3. What was re-measured: `run_all.py` re-run at `41517898` with 73/73 files passing; suite receipt stamped at `gates/suite.json`; `review_level: quick` confirmed.

## Your Actions

No operator action required. Review and run close-out when ready.
