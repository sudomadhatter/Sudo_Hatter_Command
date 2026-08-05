---
name: eval-harness-negative-control-convention
description: "AGY's backend/evals/ negative-control convention is `_negative_control:true` + `synthetic_transcript` + an `NC_` id prefix — NOT an `expect_fail` field (TEA-4's draft guessed that and it would be silently ignored). A negative control SKIPS the real agent and feeds the synthetic transcript straight to the judge; it must FAIL every run."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 069c9ef5-0386-4e53-b567-4a51d69d62c5
---

In AviationChat's behavioral eval harness (`backend/evals/`), a **must-FAIL negative control** (proving the LLM judge can actually catch a bad transcript, not vacuously green everything) uses this exact convention — verified in code, not guessable:

- Scenario carries **`"_negative_control": true`** + a non-empty **`"synthetic_transcript"`** string, and its `id` **starts with `NC_`**.
- `loader.py` (`_validate_scenario`, ~line 74) REQUIRES the synthetic transcript when `_negative_control` is set, else it raises.
- `run.py` (`_run_scenario`, ~line 91-94) sees `_negative_control` + `synthetic_transcript` and **skips the real agent driver entirely** — the synthetic transcript is graded by the judge directly (no tokens for the agent, only the judge).
- `drift.py` (`_is_negative_control`, ~line 138) keys off the `NC_` id prefix and applies the **inverse rule**: an `NC_*` that stops FAILing is drift ("judge asleep").
- The `script` list is allowed to be empty for a negative control.

**The trap:** there is **no `expect_fail` field** — the harness never reads it. TEA-4's drafted `NC_FAA_01` used `expect_fail: true` and expected the real Reasoner to run against an empty dossier; that would have silently fallen through to the live driver and NOT behaved as a must-FAIL control. TEA-18 reshaped it to the real convention (modeled on `answer_leak.json::NC_01`), and added a keyless loader tripwire (`test_incorrect_faa_query_suite_loads_and_wires_negative_control`) that asserts `_negative_control`+`synthetic_transcript` present and `expect_fail` absent, so a future revert trips red.

**How to apply:** any new eval negative control → `_negative_control:true` + `synthetic_transcript` (shaped like the driver's real transcript output — for `run_reasoner` that's the `Fast answer submitted / Reasoner status / ... / Sources returned` block from `drivers.py`) + `NC_` id. The judge (`judge.py::grade`) is fully suite-agnostic (rubric+transcript only, no per-suite map) so new suites drop in without judge changes. Related: [[domain-gated-fixtures-web-verify]], [[tea-retrofit-active-initiative]].
