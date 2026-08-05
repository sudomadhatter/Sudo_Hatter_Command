---
name: real-gemini-key-leaks-into-pytest-env
description: "FIXED 2026-07-27 — AGY's test conftests now assign dummy API keys unconditionally, so a real exported GEMINI_API_KEY can no longer reach the pytest env; a failure here now means something re-introduced setdefault"
metadata: 
  node_type: memory
  type: project
  originSessionId: a1f6ddbe-82ac-4307-9a35-1b9c4418f9b7
  modified: 2026-07-27T16:02:25.069Z
---

**Status: CLOSED 2026-07-27** by story `gemini-key-pytest-env` (21.6 ③ finding N3). This memory is kept
because the diagnostic is still worth knowing and because the *operator half* is still owed.

`backend/tests/routers/test_hr_profile_single_writer.py::test_no_live_model_call_can_escape_this_suite`
asserts `os.getenv("GEMINI_API_KEY") == "test-dummy-key"`. It used to fail on a full-tree run with a real
`AIzaSy…` value, because both `backend/tests/routers/conftest.py` and `backend/tests/e2e_emulator/conftest.py`
seeded the key with `os.environ.setdefault` — a no-op when the var is already set — and their comments
documented that deference as a feature. **Both now assign unconditionally**, so the assertion holds by
construction and an exported key is overwritten rather than preserved.

**Why it matters that this is closed:** on a leaking machine the failure printed the real key as the
assertion's actual value, which reads like the story under development broke something. It was
misattributed that way **twice**. If this test fails again, the cause is no longer "the environment" —
it means someone re-introduced `setdefault`, or added a THIRD conftest that seeds keys. Check that first.

**The generalisable lesson: `setdefault` is the wrong idiom for seeding a secret in a test env.** Its
entire purpose is to defer to an existing value, which is precisely the leak. When the value must be
fake, assign. Non-secrets can legitimately keep `setdefault` — `GCP_PROJECT_ID` / `FIRESTORE_DATABASE` in
the emulator conftest deliberately still do, and that asymmetry is commented in place.

**Scope correction worth remembering.** The scare was oversized in the original filing. TEA-2's autouse
`_no_live_llm` guard already patches the google-genai SDK classes, so an unmarked test reaching a real
`generate_content` raises `LiveLLMCallBlocked` whether or not a key is present — the suite was never
silently billing the live model. The real harm was a production secret sitting in the test process plus
the misleading assertion. Relatedly, N3 prescribed "add a `@pytest.mark.live` opt-out" that
[[test-live-guard-needs-live-marker]] had **already built** — a review finding can prescribe machinery the
repo already has, so recon before scoping one.

**How to apply:** the fix is environment-proof, so nothing here blocks work. **Still owed by the operator:**
rotate the exposed key (it reached a test process — treat it as exposed), and find the shell that exports
it. As of 2026-07-27 it is NOT a shell/user/machine-level env var on the desktop, so look at the laptop, a
sourced `.env`, or a terminal profile. To reproduce or re-verify the fix, simulate rather than wait for the
machine that leaks: export a fake `AIzaSy…` value and run the test — it fails pre-fix, passes post-fix.
Related: [[test-live-guard-needs-live-marker]], [[agy-canonical-test-venv]], [[red-test-can-die-before-its-assertion]].
