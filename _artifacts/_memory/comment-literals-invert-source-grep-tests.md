---
name: comment-literals-invert-source-grep-tests
description: "Structural tests that grep SOURCE are matched by COMMENTS too — three shapes: a comment inverts an ORDER assertion, satisfies a PRESENCE check (blessing an unguarded writer), or trips a NEGATIVE pin. Parse with ast, don't grep."
metadata: 
  node_type: memory
  type: project
  originSessionId: b6ccc87b-141e-4a68-bece-581776a22e3d
  modified: 2026-08-03T01:29:58.335Z
---

AGY's ①-lane structural pins assert on **function source text**, not behaviour — because the thing being
pinned (call order, threading, an import position) has no runtime observable. The idiom:

```python
body = _create_session_source()                       # file read, not inspect.getsource
assert body.index("demo_master.reset_master_demo") < body.index("create_task(warm_context")
call_at = body.index("demo_master.reset_master_demo")
assert "to_thread" in body[max(0, call_at - 120) : call_at]
```

**The trap:** the source string includes **comments**. Write a comment *above* the pinned call that
mentions the literal the test indexes on — the natural thing to do when documenting *why* the ordering
matters — and `index()` returns the **comment's** offset instead of the call's. The ordering assertion
then compares a comment position against a code position and **passes vacuously**, or inverts outright.

Hit on 2026-07-31 (story 21.8 ③) while applying a `code-standards` §1 finding. R-1 was precisely that
`create_session`'s reset block had two load-bearing orderings and **no anchor comment**. The obvious fix —
"keep this ABOVE the `create_task(warm_context)` spawn" — would have broken `test_d1_002`, and an
`AIDEV-NOTE` naming `demo_master.reset_master_demo` would have broken `test_d1_004`'s 120-char window.
Both were caught before writing, not by a red.

**Why it is nasty:** the failure mode is a **silent green**, and it fires on the exact change the comment
contract asks you to make — so §1 compliance and the ①-lane pins are in direct tension unless you know.
`inspect.getsource` has the same exposure; a file-read extraction (used here because decorators confuse
`getsource`) is no safer.

## The second shape, and it is worse — a comment SATISFIES a presence check (2026-08-02, 21.8b ③)

Shape one (above) makes a real guard's test fail or pass vacuously. Shape two **blesses an unguarded
writer**, permanently, inside the very gate that exists to catch it. Story 21.8b's tree-sweeping CI gate
asked:

```python
GUARD_TOKEN = "demo_quarantine."
if _CORPUS_LITERAL.search(src) and GUARD_TOKEN not in src:   # ← offender
```

A module could pass by **mentioning** the guard in a docstring — or merely citing the FILENAME
`demo_quarantine.py`, which contains the token verbatim. `# guarded elsewhere, see
backend/services/demo_quarantine.py` is enough. The fix is to **parse, not grep**: walk the `ast` for a
real `Attribute` access whose `value` is the imported module `Name`, and pin BOTH directions in a
self-validation test (this gate had one for its regex half and none for its guard half — the untested
half was the broken one).

**Third shape — a NEGATIVE pin keyed to one call form is bypassable via its sibling.** The same story
carved `_phase0_sar_sweeper` OUT of the quarantine and pinned it with
`assert "is_quarantined_uid(" not in src`. The gathers wire `is_quarantined_profile(`, so the exact harm
the carve-out prevents could have been introduced through the other door with the tripwire still green.
**Pin the module, not the function** (`assert "demo_quarantine" not in src`).

**How to apply:**
- Before adding a comment near a source-asserted call site, **grep the story's red file for
  `body.index(` / `getsource` / `in src`** and list every literal it pins. Write around those literals.
- **Writing a presence/absence gate: use `ast`, never `in src`.** A token that appears in prose, a
  filename, or an import path is not a call. Ask "could a module pass this by *talking about* the
  guard?" — if yes, it is not a gate.
- **A negative pin must name the narrowest thing that cannot be renamed around** — the module, not one
  of its functions.
- Every structural sweep needs a self-validating test **per matcher**, not one for the file.
- Prefer prose that cannot collide: "the pre-warm spawn below", "the master reset" — not the symbol.
- After adding comments to any file with structural pins, **re-run that story's contract file**. Machine
  floor (ruff/pyrefly) cannot see this; only the tests can, and only if they still fail for the right reason.
- Writing the test: anchor on the **last** occurrence (`rindex`) or strip comment lines before indexing, so
  a future anchor comment cannot silently take over the match.

Related: [[red-file-hosts-expansion-tests]], [[red-test-can-die-before-its-assertion]],
[[stubbed-children-make-green-vacuous]], [[relocating-drops-mount-guards]].
