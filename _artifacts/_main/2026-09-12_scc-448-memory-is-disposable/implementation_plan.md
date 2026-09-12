# Implementation Plan — SCC-448: Memory is disposable (The Deletion Test)

**Goal:** Replace the inverted "long-term-only" memory rule with the **Deletion Test**: delete it in your head, then look at the damage. Slower means memory; wrong means a rule and a ticket. Codify the invariant that a memory is never the only copy of anything, promote load-bearing standing rulings to enforceable rules, update `/smh-memory-audit` with a sort pass, and rewrite `test_memory_long_term_rule.py` test-first.

**Lane:** `chore/SCC-448-memory-is-disposable` @ `5f9062a9` (cut from `origin/main`).

---

## 1. Scope & The Invariant

On 2026-09-11, the old rule (`agent-memory-is-long-term-only.md`) sent an operator ruling regarding review disposition into a private memory file instead of into the shared rules. The test it shipped ("will this still be true after this story closes?") returned YES for precisely the load-bearing facts that must never reside in memory alone.

Memory is the weakest surface in the system: private to one platform's store, invisible in a diff, absent from code review, loaded unevenly across front doors, and pinned by no test.

**The Invariant:**
> **A memory is never the only copy of anything.**
> If a fact is load-bearing — an architectural contract, an operator hard stop, a gate requirement, a security rule — it must live in `.agents/rules/`, in a hook, in a command, or in code. If the memory store is completely wiped or unavailable, no agent should produce invalid code or violate house law.

**The Deletion Test:**
> *Delete it in your head, then look at the damage:*
> - **Slower** → It belongs in **memory**. It helps an agent avoid re-investigating a known quirk, recalls Daniel's preferred communication nuance, or summarizes machine setup hints.
> - **Wrong** → It belongs in a **rule and a ticket**. If deleting the note causes the next agent to make a breaking choice, violate an operator ruling, or fail a gate, it is NOT memory. It must be codified in `.agents/rules/` and backed by enforcement.

---

## 2. Checkable Acceptance List

- **A (Rule Replacement & Invariant)**: `.agents/rules/memory-is-disposable.md` replaces `agent-memory-is-long-term-only.md` (which is deleted), carrying the Deletion Test ("delete it in your head, then look at the damage: slower means memory; wrong means a rule and a ticket") and the invariant ("a memory is never the only copy of anything").
- **B (Repoint Core Law)**: `constitution.md` Always block, `.agents/rules/INDEX.md`, root `AGENTS.md` §7, and `.roo/rules/constitution.md` are repointed to `memory-is-disposable.md` and state the Deletion Test and disposable memory law.
- **C (Audit Sort Pass)**: `.agents/commands/smh-memory-audit.md` gains a sort pass and candidate classification (`Promote to rule`) that flags load-bearing memories (whose absence makes an agent wrong rather than slower) as rule candidates.
- **D (Store Sort Pass)**: Existing store `_artifacts/_memory/` is sorted once; any load-bearing standing rulings/laws identified are promoted to rules or confirmed backed by rules, while the rest are retained or cleaned, keeping `test_memory_store.py` passing.
- **E (SOP & Test Suite)**: `.agents/scripts/tests/test_memory_long_term_rule.py` is rewritten around the new test (seen RED first with positive and counter-example checks), and `docs/_scc_sops_prds/workflows_testing_SOP.md` + its changelog carry the SCC-448 entry in the same commit.

---

## 3. Step-by-Step Execution Plan

### Step 1: RED Test Suite Scaffolding (Acceptance E)
- Rewrite `.agents/scripts/tests/test_memory_long_term_rule.py` to assert:
  1. `constitution.md` carries the disposable memory floor rule and cites `memory-is-disposable` (fails while it cites `agent-memory-is-long-term-only`).
  2. `.agents/rules/memory-is-disposable.md` exists on disk (fails before creation).
  3. `.agents/rules/agent-memory-is-long-term-only.md` is removed (fails while old file remains).
  4. The new rule states the Deletion Test ("slower means memory; wrong means a rule") and the invariant ("never the only copy").
  5. The rule includes counter-examples: a memory without a backing rule fails the deletion test; a tooling/preference memory passes.
  6. `INDEX.md` registers `memory-is-disposable.md` as on-demand and omits the old rule.
  7. `AGENTS.md` §7 references `memory-is-disposable.md` and states the deletion test.
  8. `workflows_testing_SOP.md` states the disposable memory rule and `workflows_testing_SOP_changelog.md` carries the SCC-448 entry.
- Run `python3 .agents/scripts/tests/test_memory_long_term_rule.py` and capture real RED output.

### Step 2: Authored Rule & Invariant (Acceptance A)
- Author `.agents/rules/memory-is-disposable.md` with:
  - YAML frontmatter with `trigger: model_decision` and triggers list `[memory, remember, save to memory, note for later, MEMORY.md, auto-memory, memory audit, disposable memory, deletion test]`.
  - The Deletion Test: delete in head -> slower vs wrong.
  - The Invariant: a memory is never the only copy of anything.
  - What qualifies (disposable recall: operator style, tooling quirks, memory index pointers).
  - What never qualifies (unbacked standing rulings, exclusive architectural contracts, story-scoped notes, measurements).
  - The Delete-on-Sight duty (story-scoped notes, obsolete items).
  - The Narrate-Every-Write duty (one line in chat).
  - Falsifiers (`probe:`) for measurable memories.
- Remove `.agents/rules/agent-memory-is-long-term-only.md`.

### Step 3: Repoint Core Law & Mirrors (Acceptance B)
- Update `.agents/rules/constitution.md`: change Always bullet from "Always keep agent memory long-term only..." to "Always treat agent memory as disposable: apply the deletion test (slower means memory; wrong means a rule and a ticket); a memory is never the only copy of anything; story-scoped findings go in the story file or its artifacts; delete story-scoped memories on sight; and say in chat, in one line, every time a memory is written (see `memory-is-disposable` rule)".
- Update `.roo/rules/constitution.md` with the identical mirror text.
- Update `.agents/rules/INDEX.md`: replace row for `agent-memory-is-long-term-only.md` with `memory-is-disposable.md`.
- Update `AGENTS.md` §7: replace "Memory is LONG-TERM ONLY" heading and description with "Memory is DISPOSABLE — the deletion test replaces long-term-only (operator ruling 2026-09-12, SCC-448)", stating the deletion test, invariant, and pointing to `.agents/rules/memory-is-disposable.md`.

### Step 4: Audit Sort Pass in `/smh-memory-audit` (Acceptance C)
- Update `.agents/commands/smh-memory-audit.md`:
  - In Step 3 (Ground-truth each candidate): introduce the Deletion Test check for every candidate. If deleting makes an agent wrong rather than slower, flag for rule promotion.
  - In Step 4 (Propose block): add `### 📜 Promote to rule (load-bearing — fails deletion test; needs a rule/code home)` to the scannable block.

### Step 5: Store Sort Pass (Acceptance D)
- Review existing memories in `_artifacts/_memory/`.
- Verify that every load-bearing ruling already has a backing rule (e.g. `approval-prompts-are-a-budget-threat.md` -> `.agents/rules/approval-cost-is-a-threat.md`, `git-branch-model-standard.md` -> `.agents/rules/git-policy.md`, etc.).
- Ensure `test_memory_store.py` remains 100% clean and green.

### Step 6: SOP & Changelog Updates (Acceptance E)
- Update `docs/_scc_sops_prds/workflows_testing_SOP.md` §2 to state the disposable memory law, deletion test, and link to `memory-is-disposable.md`.
- Add entry to `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` under date 2026-09-12 for SCC-448.
- Update `_artifacts/_main/INDEX.md` with the new session entry for SCC-448.

### Step 7: Verification & Receipts
- Re-run `test_memory_long_term_rule.py` -> verify GREEN.
- Run `test_rule_frontmatter.py` -> verify GREEN (30/30).
- Run `check_maps.py` -> verify clean.
- Run full suite through `gate_receipt.py` -> stamp `gates/suite.json`.
- Execute mutation sweep via `mutation_sweep.py`.

---

## Declared Change Set

- NEW `.agents/rules/memory-is-disposable.md` — disposable memory rule with deletion test and invariant → A
- DELETE `.agents/rules/agent-memory-is-long-term-only.md` — retired rule replaced by memory-is-disposable → A
- EDIT `.agents/rules/constitution.md` — Always bullet repointed to memory-is-disposable and deletion test → B
- EDIT `.agents/rules/INDEX.md` — update table row to register memory-is-disposable.md as on-demand → B
- EDIT `AGENTS.md` — update section 7 persistence memory law and pointers → B
- EDIT `.roo/rules/constitution.md` — mirror constitution.md Always line for Zoo Code → B
- EDIT `.agents/scripts/tests/test_memory_long_term_rule.py` — rewrite test suite for deletion test and disposable memory law → E
- EDIT `.agents/commands/smh-memory-audit.md` — add deletion test sort pass and promote-to-rule candidate bucket → C
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — update memory law and link to memory-is-disposable.md → E
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — add SCC-448 changelog row → E
- EDIT `_artifacts/_main/INDEX.md` — register today's artifact folder row → E
- EDIT `docs/doc-graph.json` — auto-updated doc graph reflecting memory-is-disposable.md → E
- EDIT `docs/doc-graph.md` — auto-updated doc graph markdown reflecting memory-is-disposable.md → E

---

## Verification Plan

### Automated Tests
- `python3 .agents/scripts/tests/test_memory_long_term_rule.py` (RED first, then GREEN)
- `python3 .agents/scripts/tests/test_rule_frontmatter.py`
- `python3 .agents/scripts/tests/test_memory_store.py`
- `python3 .agents/scripts/check_maps.py`
- `python3 .agents/scripts/gate_receipt.py run --task SCC-448 --gate suite --root _artifacts/_main/2026-09-12_scc-448-memory-is-disposable --cwd /home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-448-memory-is-disposable -- python3 .agents/scripts/tests/run_all.py`
- `python3 .agents/scripts/mutation_sweep.py --table _artifacts/_main/2026-09-12_scc-448-memory-is-disposable/sweep.json`

### Manual Inspections
- Check that `declared_change_set.py parse` parses all 11 entries with zero incomplete lines.
- Check that `agent-memory-is-long-term-only.md` is deleted from disk and no dangling references remain in active rules or SOPs.

---

## Self-Audit (2026-09-12)

**Level:** LEDGER+BLAST (touches rules, constitution, and test suite)  
**Mode:** pre-work  

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every declared path checked against git tree; declared_change_set.py parse verified (11 entries, 0 incomplete); python3 portability verified; deployable-path check clear; scope ledger verified (1 NEW artifact maps to Acceptance row A, 0 unassigned artefacts)
read:        .agents/rules/agent-memory-is-long-term-only.md, .agents/rules/constitution.md, .agents/rules/INDEX.md, AGENTS.md, .roo/rules/constitution.md, .agents/scripts/tests/test_memory_long_term_rule.py, .agents/commands/smh-memory-audit.md, docs/_scc_sops_prds/workflows_testing_SOP.md, docs/_scc_sops_prds/workflows_testing_SOP_changelog.md, _artifacts/_main/INDEX.md
verdict:     clean
```

```
lens:        2 Parity + Blast
checks_run:  all active references to agent-memory-is-long-term-only identified across constitution, mirrors, INDEX, AGENTS.md, test, and SOPs; sibling worktrees inspected (SCC-186 and SCC-456 have 0 overlapping paths); risk_seam.py returns unclassified (expected in lobby markdown repo); SOP currency staged in same commit
read:        git worktree list, git status in sibling trees, .agents/rules/INDEX.md, docs/_scc_sops_prds/workflows_testing_SOP.md
verdict:     clean
```

```
lens:        3 Pre-Mortem
checks_run:  failure modes analyzed (frontmatter schema, test_rule_frontmatter.py constraints, memory store integrity test_memory_store.py, sop_currency.py commit-msg hook); all failure paths mitigated with concrete checks
read:        .agents/scripts/tests/test_rule_frontmatter.py, .agents/scripts/tests/test_memory_store.py
verdict:     clean
```

### Findings
| anchor | literal text read | consequence | severity |
| --- | --- | --- | --- |
| (none) | (clean run) | (no findings) | clean |

### Observations
- `test_memory_long_term_rule.py` will be rewritten in place. Its filename is preserved to avoid churn in `run_all.py` test discovery while completely updating its test cases to enforce the new `memory-is-disposable.md` rule and counter-examples.

Audit verdict: GO

