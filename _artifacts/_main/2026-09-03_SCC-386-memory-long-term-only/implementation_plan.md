# Implementation Plan — SCC-386: Global .agents Rule: Agent Memory is Long-Term Only

On 2026-09-04 an agent saved two auto-memory notes regarding Epic 24 gate failures (CI scope mismatches, direct-push landing) that were already recorded in the story file and audit, and would go stale once AVCH-119 lands. Mr. Hatter ruled that memory holds only what must be remembered long term (operator preferences, machine/tooling quirks, standing rulings). Temporary findings tied to one story or fix belong in that story's file or `_artifacts/` walkthrough, and story-scoped memories must be deleted on sight.

This task establishes this ruling as shared law across all platforms and projects.

## User Review Required

> [!IMPORTANT]
> - **Floor Rule Addition**: Adding a mandatory bullet to `.agents/rules/constitution.md` (§Always) mandating that memory is long-term only, story-scoped facts live in the story or its artifacts, story-scoped memories are deleted on sight, and every memory write is narrated in chat in one line.
> - **New Conditional Rule**: Creating `.agents/rules/agent-memory-is-long-term-only.md` defining the qualifying test ("still true and still useful after this story closes?"), qualification categories, prohibited entries, delete-on-sight duty, and narrate-every-write duty.
> - **Store Sweep**: Existing memory stores (`~/.claude` memory, `_artifacts/_memory/`, and `Projects/AGY_AVIATIONCHAT/_artifacts/_memory/`) have been audited; findings and deletions are recorded in the walkthrough.

## Open Questions

None — the ticket requirements and operator ruling are fully specified and verified against existing memory stores.

## Acceptance Criteria & Checkable List

- **A1**: `.agents/rules/constitution.md` carries a floor bullet requiring long-term-only memory, story-scoped findings in story/artifacts, deletion of story-scoped memories on sight, and one-line chat narration on every memory write.
- **A2**: `.agents/rules/agent-memory-is-long-term-only.md` exists with intent-shaped trigger frontmatter, detailing the qualification test, qualifying vs prohibited items, delete-on-sight duty, and narrate-every-write duty.
- **A3**: `.agents/rules/INDEX.md` registers `agent-memory-is-long-term-only.md` under `on-demand`, and `AGENTS.md` §7 references the rule.
- **A4**: `sudo-project-skeleton` template compatibility verified clean (`python3 .agents/scripts/check_maps.py --root Projects/sudo-project-skeleton`).
- **A5**: `docs/_scc_sops_prds/workflows_testing_SOP.md` updated with long-term memory requirements, and `workflows_testing_SOP_changelog.md` updated in the same commit.
- **A6**: Existing memory stores swept, any story-scoped notes pruned, and findings recorded in the walkthrough.
- **A7**: Test suite `.agents/scripts/tests/test_memory_long_term_rule.py` written test-first (seen RED), then GREEN, and full test suite passes.

## Declared Change Set

- EDIT `.agents/rules/constitution.md` — add long-term memory floor rule → A1
- NEW `.agents/rules/agent-memory-is-long-term-only.md` — conditional rule for long-term memory law → A2
- EDIT `.agents/rules/INDEX.md` — register agent-memory-is-long-term-only rule → A3
- EDIT `AGENTS.md` — reference long-term memory law in §7 persistence contract → A3
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — document memory rules for operator and agents → A5
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — changelog entry for SCC-386 → A5
- NEW `.agents/scripts/tests/test_memory_long_term_rule.py` — assertion test for memory rule and floor compliance → A1, A2, A3, A7

## Proposed Changes

### Rule Definitions & Floor Law

#### [MODIFY] [.agents/rules/constitution.md](file:///home/dlohn/Sudo_Hatter_Command/.agents/rules/constitution.md)
Add the floor bullet under `## ✅ Always`:
- Always keep agent memory long-term only: memory holds only facts that outlive the current story (operator preferences, machine/tooling quirks, standing rulings); story-scoped findings go in the story file or its artifacts; delete story-scoped memories on sight; and say in chat, in one line, every time a memory is written (see [`agent-memory-is-long-term-only`](agent-memory-is-long-term-only.md) rule).

#### [NEW] [.agents/rules/agent-memory-is-long-term-only.md](file:///home/dlohn/Sudo_Hatter_Command/.agents/rules/agent-memory-is-long-term-only.md)
Create new on-demand intent-triggered rule:
- Frontmatter: `trigger: model_decision`, `triggers: [memory, remember, save this, note for later, MEMORY.md, auto-memory, memory audit]`.
- The One Test: "Will this still be true and still be useful after this story closes?"
- What qualifies: operator preferences/profile, recurring machine/tooling quirks, standing rulings.
- What never qualifies: measurements, bug mechanisms, temporary gate mismatches / CI failures.
- Delete-on-sight duty: remove story-scoped or stale notes immediately during reviews or audits.
- Narrate-every-write duty: state in chat in one line what was saved on every memory write.

#### [MODIFY] [.agents/rules/INDEX.md](file:///home/dlohn/Sudo_Hatter_Command/.agents/rules/INDEX.md)
Add entry for `agent-memory-is-long-term-only.md` under `on-demand`.

#### [MODIFY] [AGENTS.md](file:///home/dlohn/Sudo_Hatter_Command/AGENTS.md)
Update §7 (Persistence / Memory) to state the long-term memory rule and point to `.agents/rules/agent-memory-is-long-term-only.md`.

### SOP & Documentation

#### [MODIFY] [docs/_scc_sops_prds/workflows_testing_SOP.md](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/workflows_testing_SOP.md)
Update the memory section (§2 / lines 236–247) to explain long-term memory requirements, the delete-on-sight duty, and narrate-every-write duty.

#### [MODIFY] [docs/_scc_sops_prds/workflows_testing_SOP_changelog.md](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/workflows_testing_SOP_changelog.md)
Add changelog entry for SCC-386.

### Automated Testing

#### [NEW] [.agents/scripts/tests/test_memory_long_term_rule.py](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/tests/test_memory_long_term_rule.py)
Automated test suite asserting:
- `constitution.md` carries the floor rule.
- `agent-memory-is-long-term-only.md` exists and contains required triggers and sections.
- `INDEX.md` and `AGENTS.md` correctly reference the rule.
- `test_rule_frontmatter.py` passes cleanly.

## Verification Plan

### Automated Tests
1. `python3 .agents/scripts/tests/test_memory_long_term_rule.py` — verify test fails RED before implementation, then passes GREEN.
2. `python3 .agents/scripts/tests/test_rule_frontmatter.py` — verify all rule frontmatter checks pass.
3. `python3 .agents/scripts/tests/test_memory_store.py` — verify memory store integrity.
4. `python3 .agents/scripts/check_maps.py --root Projects/sudo-project-skeleton` — verify skeleton template passes cleanly.
5. `python3 .agents/scripts/declared_change_set.py diff _artifacts/_main/2026-09-03_SCC-386-memory-long-term-only/implementation_plan.md` — verify change set matches actual diff with zero undeclared drift.
6. `python3 .agents/scripts/tests/run_all.py` — verify entire suite passes.

### Manual Verification
- Review existing memory stores to confirm no story-scoped notes remain.

## Self-Audit (2026-09-03)

### Lens 1: Repo Reality & Scope Ledger
- `checks_run`: Verified existence of all 5 target EDIT paths on disk; verified NEW target paths do not collide; verified declared_change_set.py parse outputs 7 valid entries and 0 incomplete.
- `read`: .agents/rules/constitution.md, .agents/rules/INDEX.md, AGENTS.md, docs/_scc_sops_prds/workflows_testing_SOP.md, docs/_scc_sops_prds/workflows_testing_SOP_changelog.md.
- `verdict`: clean

### Lens 2: Parity & Blast Radius
- `checks_run`: Inspected sibling worktrees (git worktree list); inspected thin-project template sudo-project-skeleton; confirmed no deployable product paths (backend/, frontend/, firebase/) are in scope.
- `read`: Projects/sudo-project-skeleton/AGENTS.md, Projects/sudo-project-skeleton/.agents/rules/INDEX.md.
- `verdict`: clean

### Lens 3: Pre-Mortem
- `checks_run`: Analyzed failure modes around rule frontmatter requirements (test_rule_frontmatter.py), armed SOP-currency commit-msg gate, and memory store integrity (test_memory_store.py).
- `read`: .agents/scripts/tests/test_rule_frontmatter.py, .agents/scripts/git-hooks/pre-commit-sop-currency.py.
- `verdict`: clean

### Audit verdict: GO

**Approval (2026-09-04):** "approved" — recorded at <pending>
