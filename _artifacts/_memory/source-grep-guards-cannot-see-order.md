---
name: source-grep-guards-cannot-see-order
description: "A structural test asserting a function's SOURCE CONTAINS a guard call proves presence, never position — a guard relocated to AFTER the write it protects passes it identically."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 35302396-60ae-4be3-ac70-95e0eeced136
  modified: 2026-08-02T19:46:53.068Z
---

A structural red of the shape `assert "demo_quarantine.is_quarantined_uid(" in _func_source(...)`
proves the guard is **present in the function**. It says nothing about **where**. Move the guard
below the write it is supposed to prevent and the test stays green — while the corpus row is
created and only then "refused".

**Proven, not theorized (2026-08-02, story 21.8b ②).** Relocating one guard in
`_write_checkride_macro_feed` to after its `.set()`:

```
guard RELOCATED to after the write
FAILED ...test_guard_002_macro_feed_row_is_never_written_for_a_prospect
1 failed, 45 passed
```

All **four** ① structural reds stayed green under that mutation. Only the behavioral test fired.

**Why:** this is the same family as [[comment-literals-invert-source-grep-tests]] and
[[stubbed-children-make-green-vacuous]] — a test that asserts against the *shape of the code*
rather than the *effect of running it*. It is worth writing (it catches a whole guard being
deleted, and it is the only cheap way to gate five call sites at once), but it is a **wiring**
proof, never a **behavior** proof, and shipping only the structural half leaves the highest-cost
failure mode uncovered.

**How to apply:**
- When ① hands you a "source contains the guard" red, treat behavioral coverage of the same guard
  as **owed work in ②**, not as optional expansion. It belongs in the same red file per
  [[red-file-hosts-expansion-tests]].
- The behavioral test needs a **non-quarantined control in the same test**, or it passes against a
  helper that writes nothing at all — a bare `return` at the top of the function would be green.
- Prove non-vacuity by **relocating** the guard, not deleting it. Deleting it also reds the
  structural test, which hides whether the new test adds anything.
- Assert on the *store*, not on a MagicMock's call log where the write is a batch: a mock's
  `batch.commit()` succeeds whether or not the refs were ever valid.

Related: [[e2e-gate-fiction-test-guardrails]], [[test-debt-stories-are-characterization]].
