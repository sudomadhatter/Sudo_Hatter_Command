# DRAFT — clause for `.agents/rules/artifacts-always-first.md`

Not yet applied. Lands as SCC-205 Part E, acceptance #13.

Home: that rule already owns `_artifacts/`, the memory store lives at `_artifacts/_memory/`, and its
`protocol` load class fires on "any session that may modify files" — which is exactly the agent about
to write a memory.

---

## § The memory store — what it is for, and what it must never carry

`_artifacts/_memory/` is **recall**, not law. Every platform reads its index at session start, on
both machines. That reach is why misusing it is dangerous rather than merely untidy.

### Why this clause exists

A memory has four properties that make it unable to hold an obligation:

1. **Prunable** — `/smh-memory-audit` retires, merges and compresses entries against a 25 KB index
   cap. An obligation stored here is one compaction from gone.
2. **Unenforced** — no gate reads it. Nothing goes red when it is ignored, so the failure is silent.
3. **Advisory by contract** — recalled entries arrive as background context and describe what was
   true when written, not what is true now.
4. **Creates false coverage** — the dangerous case is not a missing memory. It is a present one that
   makes an unfixed problem look handled.

### DO

- Record **context**: how the system is used, what has been decided, why a shape is the way it is.
- Record **gotchas**: a trap that cost real time and is not visible from the code — `echo` truncates
  at `\c`; one machine has no `python3`, the other has no bare `python`.
- Record **pointers**: where a thing lives, which ticket settled a question.
- Record **a pointer to a rule**. A memory saying *"this law lives in `<rule>`"* is correct and
  encouraged. The rule carries the law; the memory only helps you find it.

### DO NOT

- **Do not put an obligation in a memory.** If a thing must be *followed* — a gate, a test, a
  required step, a discipline — it is a rule, with a pointer a linter can check.
- **Do not write a memory instead of a fix.** Writing "remember to do X" is not doing X.
- **Do not treat an existing memory as proof something is handled.** A memory that reads like law is
  a signal the law has no rule yet — a defect to close, not coverage.

### The test, before writing one

> If this memory disappeared tomorrow, would something **break** — or would someone merely have to
> look it up again?

- **Break** → it is a rule. Writing a memory instead is the failure this clause exists to stop.
- **Look it up** → a memory is correct.

### Success looks like

- Every obligation resolves from a rule file, and any memory touching it is a pointer to that rule.
- `grep -rln "_artifacts/_memory" .agents/rules/` returns this rule among its hits.
- A new memory can be justified in one line as context, gotcha, or pointer.

### Failure looks like

- A real defect is closed with a memory. Months later the memory is pruned or simply not loaded on
  one platform, the defect resurfaces, and the record says it was addressed.
- An agent reads a memory describing a discipline, assumes a rule enforces it, and skips the check.
- The store grows toward its cap carrying law, so the audit is forced to choose between deleting an
  obligation and deleting genuine recall.

**The specific failure that produced this clause:** a discipline that had no rule was written into a
memory. Nothing went red. The store then looked like it was enforcing something that nothing enforced.
