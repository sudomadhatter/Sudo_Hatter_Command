---
name: test-live-guard-needs-live-marker
description: "AGY's TEA-2 determinism guard (autouse _no_live_llm in repo-root conftest.py) blocks real genai calls for any test NOT marked @pytest.mark.live — and agent code that wraps model calls in a broad `except Exception` (e.g. SocraticTeacherAgent.evaluate) SWALLOWS the LiveLLMCallBlocked into a fallback → a live test missing @live passes VACUOUSLY without ever calling the model. Any live-key test must carry @pytest.mark.live."
metadata: 
  node_type: memory
  type: project
  originSessionId: 77a3b500-6d20-4967-864d-5ce661cd1562
---

In AGY_AVIATIONCHAT, the TEA-2 determinism guard is an **autouse** fixture `_no_live_llm` in the **repo-root `conftest.py`**. It patches the google-genai SDK surfaces (`AsyncModels.generate_content` etc.) to raise `LiveLLMCallBlocked` for **every test that is NOT marked `@pytest.mark.live`**, and it applies to the whole tree below the root — including sibling test dirs like `backend/tests/integration_temp0/`.

The trap (found + fixed in TEA-6, 2026-07-02): a genuine live-key integration test marked only `@pytest.mark.temp0` (or any non-`live` marker) will, when run **with** a key, hit the guard → `LiveLLMCallBlocked`. If the code under test wraps its model call in a broad `except Exception` (as `SocraticTeacherAgent.evaluate()` does — it returns an `EVAL_INCORRECT` fallback on any error), the guard exception is **silently swallowed**. Both runs return the identical fallback, so an assertion like `first.routing_tag == second.routing_tag` passes **trivially — the model was never called.** A false green that defeats the test's entire purpose.

**Why:** it fails as a *green*, not a red, so nothing flags it. `skipif no key` hides it in keyless/CI runs; it only bites the first time someone runs it with a real key (exactly when they're trusting the result). The determinism guard and the broad `except` are each individually correct — the bug is their interaction.

**How to apply:**
1. **Any test that is supposed to make a REAL genai call MUST be marked `@pytest.mark.live`** (in addition to any semantic marker like `temp0`). `live` is the ONLY marker the guard exempts (`conftest.py` `get_closest_marker("live")`). This is TEA-2's own prescribed contract (its docstring says so).
2. **Proof it actually ran live, not fallback:** check the runtime (a real call is seconds, a swallowed-guard fallback is instant) and/or a real-client side effect (e.g. the genai aiohttp DeprecationWarning). TEA-6's live AC3 took ~16.57s with the aiohttp warning = confirmed real.
3. Applies to the deferred **TEA-3b** (Gemini-Live marker injection), the **TEA-6 nightly wiring** of `integration_temp0/`, and any future live/`temp0` test. Markers stay distinct: `temp0` = nightly selector, `live` = "opt out of the guard" — a live determinism test needs BOTH.

Relates to [[tea-retrofit-active-initiative]], [[test-debt-stories-are-characterization]].
