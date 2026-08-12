# Step 2 — Verify

A hunter asserts. This step is where an assertion becomes evidence, or dies.

## Self-gating — this step is free when there is nothing to do

- **0 findings from step 1 → skip the whole step.** No wave runs, no tokens spent, no wall-clock
  added. A clean diff costs exactly what it costs today.
- **Fewer than 2 findings → no compound pass.** Compound synthesis exists to find what emerges from
  findings *interacting*; with one finding there is nothing to interact with.

## Scaffold stage — what this step does TODAY, said plainly

The verification roles (Evidence Verifier and Compound Synthesis) land in **SCC-127**, together
with the `evidence_extract.py --findings` dossier they consume. Until then this step is an honest
pass-through:

1. Carry every step-1 finding forward **unchanged**, marked `verification: none`.
2. Set no `revised_severity` on anything — step 3 will therefore score on hunter-asserted severity,
   which is exactly the behavior the caller gets today from the vendor path.
3. Add one line to the engine's returned `notes`: `verification pass not yet installed (SCC-127)`.

That note is not decoration. A reader of the record must be able to tell a finding nobody checked
from a finding an independent role confirmed — and until the roles exist, every finding is the
former. Overstating this is the one failure this step can have at scaffold stage.

⛔ Do not improvise the verification roles here. A verifier invented on the spot has neither the
evidence dossier nor the independence that makes the role worth running, and its confident output
would be indistinguishable in the record from the real thing.

## NEXT

Read fully and follow `./step-03-triage.md`.
