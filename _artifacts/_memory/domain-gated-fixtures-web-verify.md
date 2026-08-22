---
name: domain-gated-fixtures-web-verify
description: "For a Daniel/domain-gated fixture (e.g. TEA-18 B2 FAA regs), discharge the gate by WEB-VERIFYING against primary sources — not by hand-authoring, and not by trusting model memory. Daniel's standing call: 'you can do this, just verify using FAA documents.'"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 069c9ef5-0386-4e53-b567-4a51d69d62c5
---

When a test fixture is blocked on **domain-expert ratification** (the AGY TEA "B2"-style gate — aviation/FAA regulatory content that a wrong value would poison), Daniel's standing preference is that **QA self-serves the gate by verifying against primary sources on the web**, rather than punting the ratification back to him or asserting the values from memory.

Established 2026-07-03 on **tea-18** (FAA input-adversarial negative controls). The story was flagged "Daniel authors/ratifies the CFI domain fixtures; QA wires." When asked, Daniel's actual call was: *"You can do this. just use the web to look up the information that verify using FAA documents it correct."* Discharged by fetching **eCFR (Cornell LII, `law.cornell.edu/cfr/text/14/...`)** for each anchor (61.57 / 91.215 / 91.155 / 91.103 / Part 91 index) — which also **caught an error in the draft** (night currency is 90 days, the draft said 30).

**Why:** Daniel trusts the agent to do rigorous primary-source verification; a human re-ratification is redundant friction when the sources are public and authoritative. Verifying (vs. trusting memory) is non-negotiable — the whole point of a hallucination-detection fixture is that its own anchors are exactly right.

**How to apply:** On a domain-gated fixture, don't stop at "Daniel must ratify." Offer to verify, and on his go-ahead fetch the authoritative primary source (eCFR/FAA for regs), confirm every real anchor AND every planted-wrong value, correct any draft errors you find, cite the sources in the artifact, then wire. eCFR (`ecfr.gov`) bot-blocks WebFetch (302 → `unblock.federalregister.gov`); use **Cornell LII** (`law.cornell.edu/cfr/text/14/<section>`) instead. Related: [[eval-harness-negative-control-convention]], [[recon-reframes-story-scope]], [[tea-retrofit-active-initiative]].
