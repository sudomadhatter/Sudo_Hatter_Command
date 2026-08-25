---
name: monkeypatch-raising-false-fabricates-surfaces
description: "monkeypatch.setattr(..., raising=False) on a guard fixture CREATES a missing attribute — so when a library bump renames the guarded surface, the guard nets nothing while its own tests stay green (they read the attribute AFTER patching, i.e. the fixture's own output)."
metadata:
  type: feedback
---

**`raising=False` turns a guard's target list into self-fulfilling prophecy.** AVCH's determinism
guard patched four `google.genai` surfaces with `raising=False`; its verification test read
`getattr(cls, name)._tea2_guard` — an attribute the fixture itself had just created. Rename a
surface in a genai bump and: setattr fabricates the old name, the guard test passes, the REAL
surface goes unguarded, and live LLM calls flow in "deterministic" tests. Found at 19.1's review
(2026-08-24); all four surfaces verified present at 2.19.0, then flipped to `raising=True` — a
renamed surface now fails loudly at the first guarded test.

**Why:** a test whose subject is the fixture's own output cannot fail for the reason it exists —
same family as [[stubbed-children-make-green-vacuous]] and [[source-grep-guards-cannot-see-order]].

**How to apply:** default `raising=True` on any setattr whose target is a THIRD-PARTY surface; use
`raising=False` only for attributes you are deliberately inventing. If the guarded library is being
version-bumped, grep the conftest for `raising=False` first — it is exactly where the bump's
breakage hides.
