---
name: similarity-gate-needs-both-bands-measured
description: "A similarity-threshold gate (ROUGE/embedding/fuzzy) is only real if the same-input variance band and the cross-input similarity band DO NOT OVERLAP — measuring only same-input variance proves the gate won't flap and says nothing about whether it can discriminate."
metadata:
  node_type: memory
  type: reference
---

⛔ **Deriving a similarity threshold from same-input variance alone produces a gate that cannot
fail.** That measurement answers *"will this flap on unchanged code?"* It does **not** answer
*"can this tell a right answer from a wrong one?"* — and those are different questions with
different measurements.

**Measure BOTH bands before you trust the number:**

| Band | How | What it bounds |
|---|---|---|
| **same-input variance** | re-run the SAME case N times, score against its own golden | how LOW a correct answer can score |
| **cross-input similarity** | score each golden against the OTHER cases' goldens | how HIGH a wrong answer can score |

**A threshold exists only if the bands are disjoint.** If `max(cross) >= min(same)`, no cutoff
separates "same behavior, re-rolled" from "wrong question, plausible-looking answer", and the gate
is decorative whatever number you pick.

Measured 2026-08-24 on AGY story 19.5 (`backend/agents/greeting/evals/`), ROUGE-1 F, threshold 0.4:

```
same-input  (correct, re-rolled):  min 0.595 · mean 0.672 · max 0.832
cross-input (wrong question):      min 0.648 ·              max 0.712     <- OVERLAPS
```

Two of three baseline cases therefore **could not fail**: serving the cold-open golden in answer to
"How do I sign up?" scores 0.707 against a 0.4 bar and passes. The 0.4 had been derived carefully —
from `mean − 3σ` of the same-input table — and that derivation was sound for the question it asked.

**The root cause was upstream of the metric, and that is the transferable part.** All three cases
were captured at `turn_count=1`, where the agent's prompt orders the same opening response *whatever
the user asked* — so the goldens recorded ONE behavior three times and the metric was being asked to
distinguish cases the system does not distinguish. A false code comment (`turn 1 = "the steady-state
sales instruction"`, when turn 1 was the opening state of a 5-turn machine) is what justified
capturing them all there.

**How to apply:** before trusting any similarity gate, score the goldens **against each other** — it
is one cheap pass and it is the half everyone skips. If they score high, the cases are not
independent coverage and no threshold will make them so: fix the CAPTURE (distinct inputs that
genuinely produce distinct behavior), never the cutoff. Record the limit at the artifact AND at the
code anchor so a downstream story cannot read a green as coverage it never had. Same family as
[[stubbed-children-make-green-vacuous]] and [[prose-pinning-guards-are-vacuous]] — a check that
passes for the wrong reason — and it is the measurement half of
[[tests-must-gate-for-real]]'s "prove a new check both REJECTS and ALLOWS".
