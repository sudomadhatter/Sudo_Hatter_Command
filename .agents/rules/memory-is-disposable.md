---
name: memory-is-disposable
description: "Agent memory is disposable: the deletion test replaces long-term-only. Slower means memory; wrong means a rule and a ticket. A memory is never the only copy of anything. Load when reading, writing, auditing, or pruning agent memory."
trigger: model_decision
triggers: [memory, remember, save to memory, note for later, MEMORY.md, auto-memory, memory audit, disposable memory, deletion test]
---

# Memory Is Disposable — The Deletion Test

Memory is the weakest surface this system has: private to one platform's store, invisible in a diff,
absent from code review, loaded unevenly across front doors, and pinned by no test. On 2026-09-11, the
retired rule (`agent-memory-is-long-term-only.md`) sent a live operator ruling regarding review
disposition into a private memory file instead of into the shared rules, and it was deleted on sight.
The test it shipped ("will this still be true after this story closes?") returned YES for precisely the
load-bearing facts that must never live in memory alone.

A fact whose loss would make the next agent WRONG is not a memory. It is law that nothing enforces.

> **Operator ruling (2026-09-12, SCC-448):** *"Memory is disposable: the deletion test replaces
> long-term-only, and anything load-bearing becomes a rule. A memory is never the only copy of
> anything."*

## The One Invariant

> **A memory is never the only copy of anything.**

If a fact is load-bearing — an architectural contract, an operator hard stop, a gate requirement, or a
security boundary — it must live in `.agents/rules/`, in a hook, in a command, or in code. If the memory
store is completely wiped or unavailable tomorrow, no agent should produce invalid code or violate house
law. Memory is a disposable recall cache, never an authority.

## The Deletion Test

Before saving, auditing, or keeping ANY memory — auto-memory, manual note, or close-out routing — apply
the **Deletion Test**:

> **Delete it in your head, then look at the damage:**
>
> - **Slower** → It belongs in **memory**. It helps an agent avoid re-investigating a known quirk, recalls
>   Mr. Hatter's preferred communication nuance, or summarizes machine setup hints.
> - **Wrong** → It belongs in a **rule and a ticket**. If deleting the note causes the next agent to make a
>   breaking choice, violate an operator ruling, or fail a gate, it is NOT memory. It must be codified in
>   `.agents/rules/` and backed by enforcement.

## What Qualifies for Memory (Disposable Recall)

Memory is an expensive shared context cost paid by every future session on every platform. Only disposable
recall that passes the Deletion Test belongs here:

1. **Operator preferences and nuances**: how Mr. Hatter thinks, directs work, reviews, and
   communicates (the Jobs/Woz division of labor, BLUF, narrative first, directness).
2. **Tooling and machine quirks**: persistent toolchain behavior that recurs across stories and
   projects (Windows vs WSL/Ubuntu side differences, `acli` syntax traps, SDK idiosyncrasies, shell
   quoting pitfalls).
3. **Index pointers**: disposable summaries of rules or architecture that already exist in code or rules.

## What Never Qualifies (Prohibited in Memory)

The following must **never** be saved to agent memory:

- **Unbacked standing rulings**: durable architectural, testing, or workflow decisions that govern future
  lanes. These must be authored as rules in `.agents/rules/` under an appropriate ticket.
- **Exclusive copies of contracts**: any requirement where memory would be the sole documentation.
- **Story tasks & intermediate notes**: task checklists, in-flight status, or temporary observations
  (these live in the story file or `_artifacts/`).
- **Measurements**: benchmark numbers, execution times, character counts, or byte savings from a run.
- **A bug's mechanism**: root-cause explanations of a defect being patched. The fix, its test, and the
  story record capture that permanently.
- **Gate mismatches & temporary failures**: CI mismatches, broken checks, or pipeline failures that a
  ticket is actively fixing.

## A Measurable Memory Carries Its Own Falsifier (`probe:`)

A memory whose claim is *measurable* — it names an absolute or `~/` path, a binary, a version, or a
tool's behaviour — **must** carry a `probe:` line in its frontmatter:

```yaml
metadata:
  probe: 'grep -q microsoft-standard-WSL2 /proc/version'
```

- Write it in **single quotes**.
- The probe **must be able to fail** (not a tracked path's existence; anchored to the claim).
- Probes **observe only** (read-only; no mutating or network commands).
- A ruling or preference needs no probe.

## The Delete-on-Sight Duty

Story-scoped notes and unbacked standing rulings rot into deceptive distractions that cause agents to fight
ghost issues or follow un-gated conventions.

Whenever you read, review, or audit a memory store (the lobby `_artifacts/_memory/`, local platform stores,
or project stores):
- If you find a note that is story-scoped, obsolete, or tied to a single resolved fix,
  **delete it on sight** (and remove its entry from `MEMORY.md` in the same commit).
- If you find an unbacked standing ruling that fails the Deletion Test, **promote it to a rule and ticket**,
  then delete or reduce the memory note to a pointer.
- ⛔ **Never delete another session's in-flight uncommitted memory** (`AGENTS.md` §7 authorship gate).

## The Narrate-Every-Write Duty

Every time an agent writes, creates, or updates a memory file (including automatic memory captured by
platform harnesses), it must:
- **State in chat, in one line, exactly what was saved.**
- This keeps memory generation visible to Mr. Hatter in real time so invalid notes or unbacked rules can
  be challenged and pruned immediately.

