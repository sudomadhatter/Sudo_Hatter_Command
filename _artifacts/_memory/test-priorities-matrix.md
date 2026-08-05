---
name: test-priorities-matrix
description: "AGY's canonical Test Priorities Matrix (Daniel, 2026-06-29) — per P-level, which test LEVELS are required (Unit/Integration/E2E/Manual) + the COVERAGE target: P0 100%, P1 80%, P2 50%, P3 20%. The destination policy the TEA coverage ratchet climbs toward (TEA-5 only set a coarse day-one floor)."
metadata:
  node_type: memory
  type: project
  originSessionId: 73ca08eb-87a8-432b-af19-3522ff5d8898
---

Daniel's authoritative **Test Priorities Matrix** for AGY_AVIATIONCHAT (given 2026-06-29) — the per-priority test-level + coverage targets the TEA retrofit ratchets toward:

| Priority | Unit | Integration | E2E | Manual | Coverage target |
|----------|------|-------------|-----|--------|-----------------|
| **P0** | ✅ | ✅ | ✅ | ✅ | **100%** |
| **P1** | ✅ | ✅ | ✅ | — | **80%** |
| **P2** | — | ✅ | — | ✅ | **50%** |
| **P3** | — | — | — | ✅ | **20%** |

**Why:** this is the north star for the whole TEA initiative. It makes "we want 100% on P0" precise (the P0 row) and defines the FULL ratchet structure — not just coverage %, but which test *levels* each priority earns. TEA-5 installed the coverage *instrument* + a day-one *coarse* floor (54% over the whole `agents/specialist`+`routers` surface, CI `--cov-fail-under`); this matrix is the *destination*, expressed PER PRIORITY, not as one global number.

**How to apply:**
1. **A single `--cov-fail-under` is only a day-one proxy.** The real gate identifies P0/P1/P2/P3 code and floors each at its target (P0=100%, P1=80%, P2=50%, P3=20%) — per-file/per-group coverage, not one global %. coverage.py's single `--cov-fail-under` can't express this → the follow-up needs per-group runs (or a per-file-threshold tool).
2. **Levels, not just %.** P0 needs Unit+Integration+E2E+Manual; P1 needs Unit+Integration+E2E; P2 Integration+Manual; P3 Manual. E2E for P0/P1 needs E2E tooling (more installs — Ask-First; Daniel flagged "we still need to install more software to do all the e2e").
3. **This matrix is the content for TEA-8** (`testing-standards.md`, the Always-On rule) — the natural place to codify it project-wide. There is also a generic BMAD `test-priorities-matrix.md` under `.claude/skills/bmad-testarch-trace/resources/knowledge/`; Daniel's version above is the project-authoritative instantiation.
4. **The P0-coverage follow-up stories** climb the P0 files (`sully_spike_websocket.py` 34%, `specialist/agent.py` 54%) to 100% + add the missing levels. The P0 *guard branches* (TEA-3 override, TEA-4 FAA abstain) are already covered + floor-protected; the rest is plumbing.

Relates to [[tea-retrofit-active-initiative]], [[recon-reframes-story-scope]], [[test-debt-stories-are-characterization]].
