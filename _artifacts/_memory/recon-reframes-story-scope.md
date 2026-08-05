---
name: recon-reframes-story-scope
description: "A 'build X' story's STATED scope can overestimate the work — recon-first repeatedly found the feature already existed (TEA-4: FAA guard already fired; TEA-7: eval harness already mature; tea-17: 'missing' FR45-F tests already existed under a different name). Ground-truth the live code BEFORE assuming greenfield; audit gap-verdicts can be search-term artifacts."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 73ca08eb-87a8-432b-af19-3522ff5d8898
---

Three times in the TEA retrofit, a story framed as "build X" turned out to be "X already exists":

- **TEA-4** (decision B2 framed it "build the empty-dossier FAA guard") — recon found the guard ALREADY fired in production (`agent.py` `total_chunks == 0` skip past the Reasoner); the real work was pinning the *uncovered* production `InvestigationDossier` branch + a behavior-preserving testability extraction.
- **TEA-7** (decision B5 framed it "build a local nightly eval runner") — recon found `backend/evals/` was ALREADY a mature harness (`run.py`/loader/judge/report + 4 suites + committed baselines); the real work was an automated *drift comparator* (`drift.py`) + green-first characterization of the untested `loader`/`report` plumbing + a thin scheduler wrapper.
- **tea-17** (audit A9 said FR45-F bug-report sanitization tests "could not be located — verify or add") — they ALREADY existed (`test_bug_reports.py::test_submit_sanitizes_messages` drives the real endpoint and asserts the ≤10-message cap, HTML-escape, 500-char truncation). The sweep missed them because the code comments say "AUDIT F7" — the string "FR45" appears nowhere in `backend/`. **Audit gap-verdicts can be search-term artifacts: the requirement's name and the code's name for the same thing drift apart.** Recon by BEHAVIOR (grep the route path, the function, the truncation constant), not by requirement ID.

**Why:** acting on the stated scope would have rebuilt existing, working code — wasteful and regression-risky — and missed the *actual* gap (the uncovered branch / the manual step). The stated scope reflects what the mentor/decision *imagined*, not what the repo *holds*.

**How to apply:** before scoping any "build X" story, ground-truth the live code first (Glob/Grep/read the modules; now also GitNexus `impact`/`context`/`query` since the index is live — see [[gitnexus-index-not-actually-live]]). State the recon finding explicitly in the story ("the harness/guard already exists; the real gap is …") and right-size the work — prefer a deterministic gate + green-first characterization over a rebuild. Relates to [[test-debt-stories-are-characterization]] (the test-nature side of the same coin) and [[tea-retrofit-active-initiative]].
