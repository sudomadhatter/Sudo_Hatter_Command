# Step 2 — Verify (retired; this step is a pass-through)

**This step runs nothing.** The Evidence Verifier and the Compound Synthesis role are retired.

## Why it was retired, measured

The wave was built on a good instinct — a hunter asserts, and something should turn an assertion
into evidence. It did not pay for itself. Across the 18 reviews on disk that ran it, the wave refuted **2
findings in 18 reviews**, while costing a full second fan-out of wall-clock and tokens on every
review that collected a finding at all.

The instinct was right and the placement was wrong. Verification was happening **after** the finding
was written, by a reader who had neither the file open nor the reasoning in context — the most
expensive possible moment to discover that a finding was imaginary. SCC-447 moved it to the two
places where it is cheap and where it binds:

1. **The lens proves it before it reports it.** Every `critical` or `important` now carries
   `reproduce:` and `expected_wrong_output:`, and the lens runs that command in its own worktree
   copy. If it does not fail as predicted, the lens deletes the finding — at the moment it is
   cheapest to abandon. Step 1 carries the contract.
2. **The caller re-runs it on the real tree.** A lens's own copy may have drifted (SCC-295), so the
   receipt that actually binds is written by the caller, outside this engine —
   step 3's **reproduction gate** is what replaces this wave.

A wave that refuted 2 findings in 18 reviews cannot be defended against a gate that drops every
unreproduced `critical` and `important` outright.

## What to do here

Carry every finding from step 1 to step 3 unchanged, with
`verification: none` on each one. Do not re-grade, do not re-word, do not dedupe — dedupe is step
3's, and re-grading here is how a severity label became a second opinion nobody could audit.

Then add `verify wave: retired (SCC-447)` to the engine's returned `notes` so the record says why
this step produced nothing, and read `steps/step-03-triage.md`.

⛔ **Do not reinstate a verification role here without a measurement.** The bar is the one the wave
failed: show, over reviews on disk, that a second reading refutes findings the reproduction gate
does not already drop. An argument that it *might* is what built the wave the first time.
