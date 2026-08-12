# Step 2 — Verify

A hunter asserts. This step is where an assertion becomes evidence, or dies.

## What this step does TODAY — the whole behavior, said plainly

The verification roles (Evidence Verifier and Compound Synthesis) land in **SCC-127**, together
with the `evidence_extract.py --findings` dossier they consume. Until then this step is an honest
pass-through, and that is its complete specification:

1. Carry every step-1 finding forward **unchanged**, marked `verification: none`.
2. Set no `revised_severity` on anything — step 3 will therefore score on hunter-asserted severity.
3. Add this line to the engine's returned `notes`: `verification pass not yet installed (SCC-127)`.

That note is not decoration. A reader of the record must be able to tell a finding nobody checked
from a finding an independent role confirmed — and until the roles exist, every finding is the
former. Overstating this is the one failure this step can have today.

⛔ **Do not improvise the verification roles.** A verifier invented on the spot has neither the
evidence dossier nor the independence that makes the role worth running, and its confident output
would be indistinguishable in the record from the real thing. Marking a finding `verified` here is
a fabricated record, not a shortcut.

## When SCC-127 lands — not yet in force

⚠ **The rules in this section describe behavior that does not exist yet.** They are recorded here
so the contract is known in advance; an agent running this step today follows the section above and
ignores this one.

- **0 findings from step 1 → skip the whole step.** No wave runs, no tokens spent, no wall-clock
  added, so a clean diff costs exactly what it costs today.
- **Fewer than 2 findings → no compound pass.** Compound synthesis exists to find what emerges from
  findings *interacting*; with one finding there is nothing to interact with.
- Both roles consume `evidence_extract.py --findings` output, and a verifier-revised severity flows
  into step 3, where it outranks the hunter's assertion.

## NEXT

Read fully and follow `./step-03-triage.md`.
