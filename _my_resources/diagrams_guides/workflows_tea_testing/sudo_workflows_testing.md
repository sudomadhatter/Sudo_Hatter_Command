# TEA Testing — Quick Reference Guide

**Owner:** Daniel (Lead — Tech Lead / Engineering Manager)
**Source:** TEA Academy (Teach Me Testing, 7/7 sessions) + the `sudo-` dev-flow walkthrough, consolidated.
**Working anchor:** Epic 8 — Evolution Engine (`AGY_AVIATIONCHAT`)
**What this is:** the single page to keep open while writing tests, reviewing PRs, or running the dev loop. Two halves:
> **Part A — The Method** (TEA concepts: what to test, how much, what "good" means).
> **Part B — The Machine** (the `/` commands and the `sudo-` flow that execute the method).

---

## ⚡ The `/` command workflow — new epic → developed

The exact sequence, top to bottom, from a fresh epic to a shipped story. Run it from the **command center** (lobby); the leading token targets the child project (e.g. `AGY_AVIATIONCHAT`). **Phase A runs once per epic; Phase B repeats per story (P0 first).** Full detail in §11.

```
# ── Orient (start of every session) ───────────────────────────
/sudo-boot-sprint-memory <PROJECT>           # where am I? what's next? (read-only)

# ── Phase A · Epic kickoff — ONCE per epic ────────────────────
/sudo-create-epics-stories-sprint <PROJECT> <requirements-source>
#   → epic + stories → sprint board → interactive P0–P3 risk-score (one story at a time)

# ── Phase B · Per-story loop — REPEAT per story, P0 first ──────
/sudo-write-story-tests    <story>   # ① BDD Vision Lock (MANDATORY, waiver-recorded) + ATDD red tests (must fail now)
/sudo-dev-story-tests      <story>   # ② BDD gate → plan → self-audit → build to green → automate
/sudo-code-review          <story>   # ③ adversarial review + TEST GATE → PASS/CONCERNS/FAIL
/sudo-update-sprint-memory <story>   # close-out = your sign-off → flip to done → you git commit
```

| # | Agile step | Command |
|---|------------|---------|
| — | Orient — where am I / what's next | `/sudo-boot-sprint-memory` |
| **1–2** | Epic + stories + sprint, then map test levels (P0–P3) | `/sudo-create-epics-stories-sprint` |
| **3** | Write the failing test | `/sudo-write-story-tests` |
| **4–6** | Dev plan → self-audit → code the story | `/sudo-dev-story-tests` |
| **7** | Code review + run tests | `/sudo-code-review` |
| **8** | Close out + git push + log learnings | `/sudo-update-sprint-memory` |

> **P0 first.** The kickoff's Step 3 risk-scores every story with you; work the P0s through Phase B before P1/P2. Nothing is committed by an agent — you run `git commit` after each close-out.

---

## 🔎 What each thin `/` command actually fires (the full call-graph)

Every `/sudo-*` you type is a **thin launcher**: the `.claude/skills/sudo-*/SKILL.md` just says "read `.agents/commands/sudo-*.md` and follow it end-to-end." That `.agents/commands/` file is the real script — it resolves the target project, then calls the underlying **BMAD + TEA skills** in order. Below is what's under the hood for each one, so you know exactly what's running when you fire a command.

> **Every command shares Step 0:** resolve the child project (`$ARGUMENTS` name → `.agents/active-project.txt` pointer → ask you), echo `Target: Projects/<name>`, and bind every path under it. Never touches the lobby. Omitted below to avoid repetition.

---

### `/sudo-boot-sprint-memory` — Orient (read-only, no sub-skills)
Doesn't call other commands — it just **reads state** and tells you what to run next.
```
1. active-context.md        → Sprint Objective · Stable (don't-touch) · Broken · In Play · Pitfalls
2. component-specs/          → Invariants of any in-scope spec
3. sprint-status.yaml        → story counts + the NEXT story to pick up + which sudo- step it needs
4. confirm guardrails        → G2 spec-compliance · G3 targeted-edits · G5 agent-authority · G6 get_db() · G8 research-first
                              → then STOPS. Discovery only — waits for your instruction.
```

### `/sudo-create-epics-stories-sprint` — Phase A epic kickoff (calls 3 skills)
```
1. bmad-create-epics-and-stories   → writes the epic + its user stories with acceptance criteria (ACs)
2. bmad-sprint-planning            → lands those stories in sprint-status.yaml as `ready-for-dev`
3. bmad-testarch-test-design       → risk-analyzes (Risk = Probability × Impact), THEN…
   ⛔ INTERACTIVE HARD STOP        → as Murat (Test Architect), walks you through P0–P3 ONE story at a time
                                     (recommended P-level + why + what-it-is + levels-it-earns; you confirm/override each)
```

### `/sudo-write-story-tests` ① — story prep + red tests (calls 3 skills)
```
1. bmad-create-story    → writes the story file under _bmad/bmm/stories/ with its ACs
2. /sudo-bdd-tests      → BDD Vision Lock (MANDATORY): interactive w/ Murat until behaviors are 100% locked,
                          then stack-appropriate contracts — strict pytest-bdd .feature + step defs for
                          backend (backend/tests/features/, /bdd/); BDD-structured vitest/Playwright
                          scaffolds for frontend. Sole escape = a RECORDED waiver (no behavior surface,
                          you confirm, frontmatter records it). Either way the story leaves ① carrying
                          `bdd: locked` (+ contract paths) or `bdd: waived — <rationale>` in frontmatter.
3. bmad-testarch-atdd   → writes the remaining unit/component acceptance tests that MUST FAIL now (red phase)
                          (pulls the test-design P-levels so P0 ACs get priority coverage)
                          → leaves tests staged & red. Does NOT implement.
```

### `/sudo-dev-story-tests` ② — build to green (calls bmad-dev-story twice + 2 skills)
```
0.5 resolve ARTIFACT_DIR              → _artifacts/epic_<E>/<story>/ (all artifacts land here)
0.7 BDD contract gate (HARD)          → story frontmatter must carry `bdd: locked` (+ contract files ON DISK)
                                        or `bdd: waived — <rationale>`; NEITHER (incl. pre-gate stories) →
                                        STOP, run /sudo-bdd-tests first. No plan, no code without it.
1.  bmad-dev-story (PLAN mode)        → writes implementation_plan.md into ARTIFACT_DIR
2.  /sudo-self-audit  (AUTOMATIC)     → adversarial pre-dev stress-test of the plan (see its breakdown below)
                                        → folds findings back in + persists self-audit-stress-test.md
2.5 conditional gate                 → only STOPS to ask if you have a real question; else proceeds
3.  bmad-dev-story (IMPLEMENT mode)   → writes the code, drives the ① red tests → GREEN, pastes actual test output
4.  bmad-testarch-automate            → expands API/UI/contract coverage on what was built (automation-summary-<story>.md)
5.  close-out artifacts (MANDATORY)   → implementation_plan.md · self-audit-stress-test.md · walkthrough.md
                                        → MAY flip story to `review`. NEVER flips to `done`, NEVER commits.
```

### `/sudo-self-audit` — adversarial pre-dev audit (fires inside ②; no sub-skills, 5 phases)
Audits the **plan, not a diff** — catches flaws while fixing them is still free.
```
Phase 0  Right-size + AC traceability  → Skip / Light / Full; map every AC ↔ plan step (gap = under-deliver; extra = scope creep)
Phase 1  Blast-radius trace            → GitNexus impact()/context() if indexed, else grep — who breaks if this changes;
                                         contract two-sidedness (SSE/API/DB/signature); reinvention check
Phase 2  Over-engineering gate (STRICT)→ default NO-GO: new abstraction/flag/dep for N=1, "might need", clone-and-tweak → CUT
Phase 3  Pre-mortem scenarios          → happy · rehydration · error/timeout · concurrency · bad-auth · exhaustiveness · AI-hallucinated edge
Phase 4  Verdict                       → SAFE / NEEDS-REVISION / UNSAFE + Go/No-Go; bakes fixes inline into the plan
```

### `/sudo-code-review` ③ — review + TEST GATE (calls bmad-code-review + the gate chain)
```
1. bmad-code-review              → clean-room adversarial review of the diff (AI drift, over-eng, bloat, logic flaws);
                                    applies actionable fixes itself + re-runs suites
2. gate opt-in check             → read _bmad-output/sudo-tests.yaml — ABSENT → verdict WAIVED (skip gate)
3. gate checks (baseline-diff, fail only on NEW regressions):
     • /1_run-all-tests-back_front   → pytest + vitest
     • bmad-testarch-trace           → requirements→tests traceability + coverage vs l1_coverage_min
     • bmad-testarch-nfr             → perf / security / reliability (when nfr:true or agent_bearing:true)
     • bmad-testarch-test-review     → quality/flake of the tests themselves
     • automate-evidence check       → confirms ②'s expansion pass left evidence (else caps at CONCERNS)
4. Verdict → PASS / CONCERNS / FAIL / WAIVED  → writes sudo-code-review-<story>.md (+ current git HEAD ref)
5. reflects the review back INTO walkthrough.md
                                    → NEVER commits, NEVER flips story status.
```

### `/sudo-update-sprint-memory` — close-out / sign-off (no sub-skills, 6 steps)
Running this **IS your sign-off.** Only objectively-red tests can block the flip.
```
1. read state + this session's artifacts (plan + walkthrough; lift ## Close-Out Handoff if present)
2. code-verify the work you just closed (grep the fix in the files it touched)
3. route each learning to 1 of 4 homes:
     app-wide rule → project-context.md · component gotcha → component-specs/ · open bug → active-context.md · cross-session fact → Claude memory
4. APPLY: flip story `review → done` (in story file + sprint-status.yaml)
     → ONLY a FAIL verdict (new red regression) blocks. PASS/CONCERNS/WAIVED/stale/missing all close it.
5. prune active-context.md (≈250-line cap; drop stale pitfalls & old completed tasks) — automatic, never asks
6. write validated Claude memories + ask you for any manual learnings
                                    → then YOU run `git commit`.
```

---

**One-liner dictionary of every underlying skill these call:**

| Underlying skill / command | What it does |
|----------------------------|--------------|
| `bmad-create-epics-and-stories` | Break a requirements source into an epic + user stories with ACs |
| `bmad-sprint-planning` | Generate/populate `sprint-status.yaml` from the epic's stories |
| `bmad-testarch-test-design` | Risk-score stories P0–P3 (Probability × Impact); the interactive kickoff step |
| `bmad-create-story` | Write ONE story file with its ACs under `_bmad/bmm/stories/` |
| `/sudo-bdd-tests` | Interactive BDD Vision Lock (MANDATORY phase of ①) → stack-appropriate contracts (`pytest-bdd` BE / BDD-structured vitest-Playwright FE) or a recorded waiver; ② hard-gates on the frontmatter record |
| `bmad-testarch-atdd` | Write **failing** (red) acceptance tests before any code |
| `bmad-dev-story` | The dev engine — PLAN mode writes the plan; IMPLEMENT mode writes code to green |
| `bmad-testarch-automate` | Expand coverage on existing code (passes immediately) |
| `bmad-code-review` | Adversarial clean-room review of the diff; applies fixes |
| `/1_run-all-tests-back_front` | Run the full pytest + vitest suites (the gate's runner) |
| `bmad-testarch-trace` | Requirements→tests traceability matrix + coverage verdict |
| `bmad-testarch-nfr` | Audit non-functional evidence (perf / security / reliability) |
| `bmad-testarch-test-review` | Score the tests on the 5 quality dimensions |

---

Glossary / one-line cheat sheet

| Term | One line |
|------|----------|
| **TEA** | Method/playbook on top of your tools — makes expert testing repeatable |
| **P0–P3** | Risk priority = Probability × Impact; P0 = ship-blocker, P3 = cosmetic |
| **AAA** | Arrange → Act → Assert; the shape of every test |
| **DoD** | No flaky, no hard waits, stateless, self-cleaning, low-maintenance, near source |
| **ATDD** | Test-first (red → green); the failing test is the proof-of-test |
| **BDD Vision Lock** | Mandatory ① phase: interactive behavior lock w/ Murat → Given/When/Then contract (or **recorded** waiver) stamped in story frontmatter; ② refuses to dev without it |
| **Automate** | Coverage expansion on existing code (passes immediately) |
| **Use-site patch** | Patch the name as the module-under-test looks it up — not the definition |
| **Factory** | `_make_event(...)` — defaults + overrides; one update point |
| **Trace gate** | Requirements → tests → GREEN/YELLOW/RED ship decision |
| **5 dimensions** | Determinism · Isolation · Assertions · Structure · Performance |
| **L1–L4** | Deterministic → Constrained LLM → LLM-judge → Human |
| **TEST GATE** | The opt-in, baseline-diff gate inside `/sudo-code-review` (③) |

---

# PART A — THE METHOD

## 0. The one-paragraph mental model

**TEA (Test Architecture Enterprise)** is a *method/playbook* layered on top of your existing tools (pytest, vitest, Playwright) — **not a replacement** for them. It is 9 workflows + a knowledge-fragment library + quality standards. The whole point is to make expert testing decisions *repeatable* so you don't have to be a testing expert to test well. Tests are **designed** before they're written, **maintained** like production code, and **allocated by risk** — not by line count.

> **The Lead reframe:** stop asking *"do we have enough tests?"* Ask *"do we have the **right** tests at the **right** priority levels, and are the P0 gates green?"*

**Engagement models (pick the entry point that matches team maturity):**
`Lite` (30-min quick start, immediate value) → `Solo` → `Integrated` → `Enterprise` → `Brownfield` (retrofit an existing untested codebase). Start at **Lite**; the same first move — `testarch-test-design` to risk-score P0–P3 — also bootstraps the Brownfield case.

---

## 0.5 TEA method — the quick-reference card

Everything the method asks of you, on one screen. Keep this open; drop into §1–§8 only when you need the prose, code, or Epic 8 examples behind a line. (§16 is the even-terser one-line glossary.)

**The reframe** — stop asking *"do we have enough tests?"* Ask *"do we have the **right** tests at the **right** priority, and are the P0 gates green?"*

**What TEA is** — a *method/playbook* on top of your runners (pytest, vitest, Playwright), **not** a replacement: 9 workflows + a 42-fragment knowledge library + quality standards that make expert testing decisions repeatable. Adopt at the entry point matching team maturity: `Lite` (30-min) → `Solo` → `Integrated` → `Enterprise` → `Brownfield` (retrofit). **Start at Lite.**

**The move (run on any feature / PR / module) — §1**
```
1. What can break?   → list the decisions the code makes (defaults · auth · transforms · ordering · privacy flags)
2. What P-level?     → Risk = Probability × Impact
3. Start at P0, work down.   100% P0 FIRST · 100% total is NEVER the goal.
```
A test exists to **guard a decision that would hurt if it silently broke.** No hurt → probably no test.

**Risk → priority → allocation — §2**

`Risk = Probability × Impact` · **Probability** = how likely to fail (rendering → logic → auth/privacy) · **Impact** = damage if it does (cosmetic → workaround → data-loss/security).

| P-level | Meaning | Levels it earns | Coverage |
|---------|---------|-----------------|:--------:|
| **P0 — Critical** | business fails if broken (privacy default, tenancy wall, auth) | Unit + Integration + E2E + Manual | **100%** |
| **P1 — High** | major user pain / core workflow | Unit + Integration + E2E | **80%** |
| **P2 — Medium** | inconvenience, workaround exists | Integration + Manual | **50%** |
| **P3 — Low** | minimal / cosmetic | Manual / skip | **20%** |

**Test levels (the pyramid) — §3** · spread a P0 across all three, cheapest/most-isolated first.

| Level | Covers | Speed |
|-------|--------|-------|
| **Unit** | isolated function/class, no deps | ms |
| **Integration** | multiple components / DB / service | medium |
| **E2E** | full workflow, real HTTP / browser | slow |

**Definition of Done — a "good" test — §4** · the ceiling, not just "tests pass":
`no flaky` · `no hard waits/sleeps` (react to state) · `stateless & parallelizable` · `self-cleaning` (finally) · `low-maintenance` (no brittle selectors) · `near the source` (mirrored tree).

**Test shape — AAA — §5** · **Arrange → Act → Assert.** One test guards one decision that matters.

**Patterns that matter — §6**
- **Fixture composition** — setup/teardown once, compose by deps, cleanup in `finally` (runs even on crash).
- **Mock-first / network-first** — set the mock up **before** the action (kills races).
- **⚠️ Use-site patch** — patch where the module-under-test *looks the name up* (import site), not where it's defined. The #1 Python mock bug.
- **Data factory** — `_make_event(...)`: defaults + overrides → one update point per schema change.
- **Step-file architecture** — self-contained JIT-loaded micro-files, progress tracked externally, resumable.

**TDD mode — know which you're asking for — §7**

| | **ATDD** (test-first) | **Automate** (coverage expansion) |
|-|-----------------------|-----------------------------------|
| Order | Test → Code (Red → Green) | Code → Test (passes immediately) |
| Use case | new feature, TDD discipline | brownfield gap / regression debt |

Red-green loop: **Red** (failing test) → **Green** (minimal code) → **Refactor** (stays green) → **Repeat**.

**Quality & gate — §8**
- **Test Review — 5 dimensions** (0–100 each, avg = overall): **Determinism · Isolation · Assertions · Structure · Performance.**
- **Trace gate:** load AC → discover tests → map → analyze gaps → verdict. 🟢 all P0/P1 covered → **ship** · 🟡 P1 gaps → **Lead assesses** · 🔴 any P0 gap → **do NOT ship**.
- **Metrics — track vs. vanity:** ✅ P0/P1 coverage %, flakiness, exec time, determinism. ❌ total line coverage, test count, file count.
- **"How much is enough?"** = enough to hold every P0/P1 gate GREEN.

---

## 1. "Where do I start?" — the decision tree

This is the answer to the most common beginner question. Run it on any feature, PR, or untested module.

```
1. What can break here?
   └─ List the decisions the code makes:
      defaults · auth checks · data transforms · ordering · privacy flags

2. What's the P-level of each decision?
   └─ Risk = Probability × Impact   (see §2)

3. Start at P0, work down.
   └─ 100% P0 coverage FIRST.  100% total coverage is NEVER the goal.
```

A test exists to **guard a decision that would hurt if it silently broke.** If breaking it wouldn't hurt, you probably don't need the test.

**Epic 8 example:** `GradingEvent.consent.export_eligible` defaults to `False`. If that silently flipped to `True`, student data becomes export-eligible without consent → a privacy breach. That's a P0 decision → it gets a dedicated test. Start there, not with the tooltip.

---

## 2. Risk Matrix — P0–P3 (the allocation engine)

**Risk = Probability × Impact.** Score each, prioritize where the product is highest.

| Dimension | Low | Medium | High |
|-----------|-----|--------|------|
| **Probability** (how likely to fail) | simple rendering | normal business logic | auth, privacy, complex transforms |
| **Impact** (what happens if it fails) | cosmetic only | user inconvenience, workaround exists | data loss, security, business failure |

| Priority | Meaning | Epic 8 examples |
|----------|---------|-----------------|
| **P0 — Critical** | Business fails if broken | `consent.export_eligible` default (privacy); tenancy wall (`test_tenancy_gate.py`); auth token validation |
| **P1 — High** | Major user pain, core workflows | grading event emitted on checkride; admin role claims enforced |
| **P2 — Medium** | Inconvenience, workaround exists | dataset pagination; graph overlays |
| **P3 — Low** | Minimal/cosmetic impact | tooltip animations, hover states |

**Test Priorities Matrix — which levels each P-level earns:**

| Priority | Unit | Integration | E2E | Manual | Coverage target |
|----------|:----:|:-----------:|:---:|:------:|:---------------:|
| **P0** | ✅ | ✅ | ✅ | ✅ | **100%** |
| **P1** | ✅ | ✅ | ✅ | — | **80%** |
| **P2** | — | ✅ | — | ✅ | **50%** |
| **P3** | — | — | — | ✅ | **20%** |

> **Lead code-review language:** *"What P-level is the decision this test pins?"* A PR with 0% P0 and 100% P3 coverage is a red flag regardless of line count.

---

## 3. Test Levels — the coverage pyramid

| Level | Covers | Speed | Epic 8 example |
|-------|--------|-------|----------------|
| **Unit** | isolated function/class; no external deps | ms | `test_grading_event.py` — schema defaults |
| **Integration** | multiple components; DB/service interaction | medium | `test_grading_event_writer.py` — writer + `mock_db` |
| **E2E** | full user workflow; real HTTP/browser stack | slow | `test_grading_event_dataset_api.py` — full HTTP via `TestClient` |

The P0 grading event is covered at **all three levels by design** — that's deliberate allocation, not accident:

```
P0: GradingEvent consent.export_eligible
├── Unit:        test_grading_event.py            ← schema defaults, no deps
├── Integration: test_grading_event_writer.py     ← write path, mock_db
└── E2E:         test_grading_event_dataset_api    ← full HTTP, admin governance
```

**Testability order:** test what's isolated first (schema), build up to full-stack (API). If a unit test needs no infra, it comes first.

---

## 4. Definition of Done — what a "good test" actually is

The **ceiling**, not just the floor of "tests pass":

1. **No flaky tests** — deterministic pass/fail. Re-running to see if it "clears" is a *bug*, not a workaround.
2. **No hard waits/sleeps** — `waitFor(condition)` not `sleep(5000)`. React to state; never guess timing.
3. **Stateless & parallelizable** — each test sets up and tears down its own world (the `get_db()` patch pattern in conftest is the reference impl).
4. **Self-cleaning** — tests delete/deactivate what they create; no manual DB resets.
5. **Low maintenance** — avoid brittle selectors; set state via APIs, not UI clicks.
6. **Near the source** — `grading_event.py` → `tests/.../test_grading_event.py` in a mirrored tree.

---

## 5. Test anatomy — Arrange → Act → Assert

Every test has the same shape. A test guards **one decision that matters.**

```python
def test_minimal_construct_defaults(self):
    # ARRANGE + ACT — construct the object
    event = GradingEvent(
        input=GradingEventInput(),
        label=GradingEventLabel(verdict="pass"),
        provenance=GradingEventProvenance(
            grader_name="checkride", served_model="gemini-3.5-flash", origin="exam"
        ),
    )
    # ASSERT — pin the decisions that would hurt if they broke
    assert event.event_id and len(event.event_id) == 32
    assert event.consent.export_eligible is False      # ← the P0 privacy guard
    assert event.consent.consent_status == "unknown"
```

---

## 6. Architecture & Patterns

### 6.1 Fixture composition
Define setup/teardown once, name it, compose by declaring dependencies. DRY + auto-cleanup even on crash + isolation (fresh instance per test).

```python
@pytest.fixture
def client_and_svc():
    import backend.routers.admin_auth as admin_auth_mod
    svc = AdminAuthService()
    admin_auth_mod._admin_auth_service = svc
    client = TestClient(app)
    try:
        yield client, svc
    finally:                                  # ← cleanup runs even if the test crashes
        admin_auth_mod._admin_auth_service = None
```
*Review Q:* "Is this setup duplicated, or centralized in a fixture? Does cleanup happen in `finally`?"

### 6.2 Mock-first / network-first
Set up the mock/intercept **before** triggering the action. Eliminates race conditions — the mock must exist before the code runs.

### 6.3 ⚠️ Patch at the import/use site, NOT the definition site
**The single most common Python mock bug.** Patch the name *as the module under test looks it up*, not where it's defined.

```python
# ❌ WRONG — definition site; the router's local name still points to the real function
patch("backend.services.grading_event_governance.query_grading_events")

# ✅ RIGHT — use site; the router resolves THIS name at call time
GOV_QUERY = "backend.routers.admin_governance.query_grading_events"
patch(GOV_QUERY)
```
*Review Q:* "Does this patch target the import site in the module under test, not the definition module?"

### 6.4 Data factories
Factory function with sensible defaults + keyword overrides → one update point when the schema changes.

```python
def _make_event(*, origin="teaching", grader="socratic", verdict="pass", ...) -> GradingEvent:
    return GradingEvent(...)

event      = _make_event()                 # all defaults
exam_event = _make_event(origin="exam")    # override only what matters
```
*Design smell:* if `_make_event()` needs 40 lines to build a "minimal" valid object, the **schema** is over-complicated.

### 6.5 Step-file architecture
Break complex workflows into micro-files: self-contained, loaded just-in-time, state tracked in a progress file, resumable from any point. (This very guide's TEA workflows run on it.) **Test analogy:** each test file = a self-contained step; fixtures = JIT setup; CI status = progress tracking; `-k`/`.only` = resume from any test.

---

## 7. TDD — ATDD vs. Automate

**The red phase is proof-of-test:** a test that passes *before* the code exists proves nothing.

| | **ATDD** (test-first) | **Automate** (coverage expansion) |
|-|----------------------|-----------------------------------|
| Order | Test → Code | Code → Test |
| Phase | Red → Green | Tests pass immediately |
| Use case | new feature, TDD discipline | brownfield coverage debt, gap-filling |
| Risk if skipped | implementation drift | unknown regressions |

**The red-green loop:** `Red` (write failing test) → `Green` (minimal code to pass) → `Refactor` (clean up, tests stay green) → `Repeat`. *Minimal means minimal* — let tests drive scope.

**Epic 8 live example (ATDD):** `test_faa_grounding_guard.py` was written (red) before `agents/specialist/agent.py` was wired up (green) — the FAA Grounding Guard story (TEA-4).

> **Lead frame:** know which mode you're asking your team for. "Write a failing test that drives the implementation" (ATDD) ≠ "we have working code, add coverage" (Automate). Different conversations, different success criteria.

---

## 8. Quality & Trace — auditing and the release gate

### 8.1 Test Review — 5 dimensions (0–100 each; overall = average)

| Dimension | Asks | Red flag |
|-----------|------|----------|
| **Determinism** | passes/fails consistently? | re-running to see if it "clears" |
| **Isolation** | runs independently? | passes alone, breaks in parallel |
| **Assertions** | checks are meaningful? | `assert resp is not None` (trivially true) |
| **Structure** | readable & organized? | 200-line test, no fixture composition |
| **Performance** | fast enough for feedback? | 45-min CI devs skip |

> A low **Isolation** score with everything else high is usually an *architecture* problem — shared fixture state or a missing `finally` cleanup.

### 8.2 Trace — requirements → tests → release gate

`Load acceptance criteria → Discover tests → Map criteria → Analyze gaps → Gate decision`

| Gate | Condition | Action |
|------|-----------|--------|
| 🟢 GREEN | all P0/P1 AC covered; gaps are P2/P3 | ship |
| 🟡 YELLOW | some P1 gaps | Lead assesses risk |
| 🔴 RED | **any P0 gap** | do NOT ship |

**Epic 8:** `test_tenancy_gate.py` is a Trace artifact — the tenancy wall (`scoped_user_query`) is a P0 AC ("no cross-school data leakage"). Delete it → Trace returns RED. That's why it's a CI merge-blocker.

### 8.3 Metrics — track vs. vanity

| ✅ Track (risk-based) | ❌ Vanity (misleading) |
|----------------------|------------------------|
| P0/P1 coverage % | total line coverage % |
| flakiness rate | number of tests |
| test execution time | test file count |
| determinism score | — |

> **"How much is enough?"** = *enough to hold every P0/P1 gate GREEN.* Line coverage tells you nothing; gate color tells you everything.

---

# PART B — THE MACHINE

## 9. The 9 TEA workflows & when each fires

```mermaid
flowchart TD
    TD["testarch-test-design<br/>(epic kickoff — final interactive step, risk P0–P3)"] --> ATDD["testarch-atdd<br/>(① write RED tests)"]
    ATDD --> AUTO["testarch-automate<br/>(② expand coverage)"]
    AUTO --> TRACE["testarch-trace<br/>(③ gate: requirements→tests + verdict)"]
    TRACE --> NFR["testarch-nfr<br/>(③ gate: perf/security/reliability)"]
    NFR --> TR["testarch-test-review<br/>(③ gate: test quality/flake)"]
    FW["testarch-framework + testarch-ci<br/>(one-time project setup)"]
    TEACH["teach-me-testing<br/>(learning — this guide's source)"]
```

| Workflow | Fires | Job |
|----------|-------|-----|
| **test-design** | epic kickoff — final interactive step of `/sudo-create-epics-stories-sprint` | risk-score the epic's work P0–P3 **with Daniel, one story at a time** → tells ① which ACs deserve the heaviest tests |
| **atdd** | ① per story | write acceptance tests that MUST fail now (red) |
| **automate** | ② per story | expand API / UI / contract coverage on existing code |
| **trace** | ③ gate | map requirements → tests, coverage vs. floor, GREEN/YELLOW/RED verdict |
| **nfr** (nfr-assess) | ③ gate (if NFR/agent-bearing) | audit perf / security / reliability evidence |
| **test-review** | ③ gate | flake & quality audit of the tests themselves |
| **framework** | one-time | initialize the test bench (Playwright/Cypress/pytest) |
| **ci** | one-time | scaffold the CI/CD quality pipeline & gates |
| **teach-me-testing** | on demand | the TEA Academy (what produced this guide) |

---

## 10. Slash-command reference (`/` commands)

### TEA Test Architect — the persona
| Command | Does |
|---------|------|
| `/tea` | Activate **Murat**, the Master Test Architect & Quality Advisor — quality, NFR & test-strategy consult. Pass intent inline for direct dispatch. |

### TEA workflow commands (the 8 raw workflows)
| Command | Description |
|---------|-------------|
| `/testarch-test-design` | Create system-level or epic-level test plan (risk P0–P3). |
| `/testarch-framework` | Initialize test framework (Playwright/Cypress). |
| `/testarch-ci` | Scaffold CI/CD quality pipeline. |
| `/testarch-atdd` | ATDD — write **failing** acceptance tests before implementation. |
| `/testarch-automate` | Expand test automation coverage for existing code. |
| `/testarch-trace` | Generate traceability matrix + coverage analysis. |
| `/testarch-nfr` | Audit NFR evidence for performance, security, reliability. |
| `/testarch-test-review` | Review test quality against best practices (5 dimensions). |

### Learning
| Command | Does |
|---------|------|
| `/bmad-teach-me-testing` | The TEA Academy — 7 self-paced sessions. (Re-run Session 7 anytime to explore the 42 knowledge fragments.) |

### The `sudo-` dev-flow orchestrators (human lane — thin wrappers that call the TEA workflows in order)
| Command | One-line job |
|---------|--------------|
| `/sudo-boot-sprint-memory` | Where am I? What story is next? Which command do I run? (read-only) |
| `/sudo-create-epics-stories-sprint` | **Phase A / epic kickoff** — create the epic + stories → sprint board → interactive P0–P3 risk-score (one story at a time). |
| `/sudo-write-story-tests` | ① Create the story → **BDD Vision Lock (mandatory)** → write its **failing** acceptance tests. |
| `/sudo-bdd-tests` | ①-inner (also standalone) — interactive Vision Lock w/ Murat → stack-appropriate BDD contracts or a **recorded** waiver, stamped into story frontmatter. |
| `/sudo-dev-story-tests` | ② **BDD contract gate (hard)** → plan → auto self-audit → build → drive tests green → automate. |
| `/sudo-self-audit` | Adversarial pre-dev audit of the plan (fires automatically inside ②). |
| `/sudo-code-review` | ③ Review the diff + run the **TEST GATE** → PASS/CONCERNS/FAIL/WAIVED. |
| `/sudo-update-sprint-memory` | Close-out: verify verdict, flip story → `done`, route learnings, prune. |
| `*_AP` variants | Autopilot lanes (`sudo-dev-story-tests_AP`, `sudo-code-review_AP`, `sudo-self-audit_AP`) — same ideas, different engine. `dev_AP` plan-stage enforces the BDD gate too: contract-or-waiver missing → `PIPELINE_BLOCKER` (headless lanes never author the lock themselves). |

### Supporting test commands
| Command | Does |
|---------|------|
| `/1_run-all-tests-back_front` | Run pytest + vitest (the gate's test runner in ③). |
| `/1_clean-test-scripts` | Tidy/remove scratch test scripts. |
| `/1_live_testing_team` | Live / manual QA lane. |

### Ops drill command — outside the per-story loop
Not part of the ①②③ dev flow — a standalone **incident-response drill** (Epic 16). Fire it any time to
exercise the production triage runbook; it never touches the sprint board.

| Command | Does |
|---------|------|
| `/sudo-incident-response [issue-id\|latest]` | **Drill harness** (16.1) for the Sentry incident-triage runbook (`.github/claude/incident-triage.md`). Thin — carries no triage logic: resolves the project → loads its runbook → runs it verbatim (**interactive lane**, Sentry MCP) → drops an `incident-report.md` under `_artifacts/debugging/`. **Drill:** force a P1 (`_test_scripts/sentry_smoke_test.py`) then run `/sudo-incident-response latest`; a pass = the report names the planted failure, the right file, and a sane fix. The runbook is the product; this is only its test rig. Full picture: [security/sentry_error_response_team.md](../security/sentry_error_response_team.md). |

---

## 11. The `sudo-` dev flow — the human-driven story loop

The `sudo-` commands are **thin orchestrators** — they don't reimplement anything; they *call* the BMAD + TEA workflows in the right order and bake a **test gate** into review.

**Two phases, eight steps.** An **epic kickoff** runs once; the **per-story loop** repeats:

| # | Step | Command |
|---|------|---------|
| — | Orient (where am I / what's next) | `/sudo-boot-sprint-memory` |
| **1** | Epic + stories + sprint | `/sudo-create-epics-stories-sprint` |
| **2** | Map test levels (P0–P3) | ↳ its final interactive step |
| **3** | Write failing test | `/sudo-write-story-tests` |
| **4** | Dev implementation plan | `/sudo-dev-story-tests` → plan |
| **5** | Self-audit stress test | `/sudo-dev-story-tests` → self-audit |
| **6** | Code the story | `/sudo-dev-story-tests` → build + automate |
| **7** | Code review + run tests | `/sudo-code-review` |
| **8** | Close out + git push + log learnings | `/sudo-update-sprint-memory` + commit |

Steps 1–2 are the once-per-epic kickoff; 3–8 repeat per story.

```mermaid
flowchart TD
    BOOT["/sudo-boot-sprint-memory<br/>boot + story pick-up"] --> KICK["/sudo-create-epics-stories-sprint<br/>(once per epic)<br/>epics + stories + sprint + risk-score P0–P3"]
    KICK --> W["① /sudo-write-story-tests<br/>write RED tests (BDD Vision Lock + ATDD)"]
    W --> DEV["② /sudo-dev-story-tests<br/>plan → self-audit → build → automate"]
    DEV --> CR["③ /sudo-code-review<br/>review + TEST GATE → verdict"]
    CR --> GATE{"verdict?"}
    GATE -->|"PASS / CONCERNS / WAIVED"| UPD["/sudo-update-sprint-memory<br/>flip story → done, save learnings, prune"]
    GATE -.->|"FAIL — fix & re-review"| DEV
    UPD --> COMMIT["git commit (Daniel)"]
    UPD -.->|"next story"| W
```

| Step | Command | Calls (TEA workflows) |
|------|---------|------------------------|
| boot | `sudo-boot-sprint-memory` | — (reads active-context + sprint-status, recommends next command) |
| kickoff | `sudo-create-epics-stories-sprint` | `bmad-create-epics-and-stories` → `bmad-sprint-planning` → `bmad-testarch-test-design` (interactive P0–P3, one story at a time) |
| ① | `sudo-write-story-tests` | `bmad-create-story` → `/sudo-bdd-tests` (BDD Vision Lock, **mandatory** — contract or recorded waiver) → `testarch-atdd` |
| ② | `sudo-dev-story-tests` | **BDD contract gate** → `bmad-dev-story` (plan) → `sudo-self-audit` → `bmad-dev-story` (implement) → `testarch-automate` |
| ③ | `sudo-code-review` | `bmad-code-review` → `/1_run-all-tests-back_front` → `testarch-trace` → `testarch-nfr` → `testarch-test-review` |
| close | `sudo-update-sprint-memory` | — (reads ③'s verdict; only command that flips a story to `done`) |

> **Epic kickoff (once per epic):** `/sudo-create-epics-stories-sprint` bundles this — it ends with an interactive `testarch-test-design` pass where you risk-score every story P0–P3 one at a time. Same first move to retrofit an untested codebase.

### The TEST GATE (the heart of ③)
Opt-in and baseline-diff aware: a project with no `_bmad-output/sudo-tests.yaml` baseline **auto-WAIVED** (never blocks a test-less project); legacy red is grandfathered — only **NEW** regressions fail.

```yaml
# _bmad-output/sudo-tests.yaml  (per project that turns the gate on)
required_tiers: [L1, L2, L3]   # which pyramid tiers must be present
l1_coverage_min: 85            # deterministic branch/line coverage floor
agent_bearing: true            # story touches agent behavior → L3 judge required
nfr: false                     # also run the NFR audit
waive: false                   # hard override (force WAIVED)
```

| Verdict | Means |
|---------|-------|
| **PASS** | all required tiers green |
| **CONCERNS** | soft issues only |
| **FAIL** | NEW regression OR a required tier missing |
| **WAIVED** | no baseline (gate off) |

> Close-out (`sudo-update-sprint-memory`) only *reads* the verdict — it never re-runs tests. ③ is the only place a ship/no-ship decision is made.

---

## 12. The testing pyramid — L1–L4 (which tier each station exercises)

Deterministic code gets real coverage; generative LLM output gets **soft assertions**, never string-matching.

```mermaid
flowchart TD
    subgraph L1["L1 — Deterministic (mocked LLM)"]
      a["routing · SAR telemetry · SSE · citation plumbing<br/>real coverage ≥ l1_coverage_min"]
    end
    subgraph L2["L2 — Constrained LLM"]
      b["temperature 0 · JSON-schema compliance"]
    end
    subgraph L3["L3 — LLM-as-judge"]
      c["cosine-similarity · F1 groundedness · judge rubrics<br/>'never reveal the answer' · zero-hallucination citation"]
    end
    subgraph L4["L4 — Human"]
      d["Daniel reviews at close-out"]
    end
    a --> b --> c --> d
```

| Tier | Written / run by | When |
|------|------------------|------|
| L1 deterministic | `testarch-atdd` (①) + `testarch-automate` (②); run by `/1_run-all-tests-back_front` (③) | every story |
| L2 constrained | `testarch-automate` (②); checked in the gate (③) | every story |
| L3 judge | authored via `atdd`/`automate`; scored in `testarch-trace` / `nfr` (③) | agent-bearing stories |
| L4 human | `sudo-update-sprint-memory` close-out + live-test gate | close-out |

---

## 13. Lead code-review checklist (consolidated)

Print this. It's the whole curriculum compressed into the questions you ask on a PR.

**Risk & coverage**
- [ ] What P-level is each new decision, and does coverage match the matrix (P0 = all 3 levels; P3 = manual/skip)?
- [ ] Is there 100% P0 coverage? (Not "is line coverage high?")
- [ ] Would removing any of these tests leave a P0 gate RED?

**Test quality (the 5 dimensions)**
- [ ] Deterministic — no flaky tests, no `sleep()`/hard waits?
- [ ] Isolated — stateless, parallelizable, self-cleaning (`finally`)?
- [ ] Meaningful assertions — pins a real decision, fails for the right reason?
- [ ] Readable structure — setup centralized in fixtures, data built via factories?
- [ ] Fast enough that the team won't skip the suite?

**Patterns**
- [ ] Mocks patch the **import/use site** in the module under test, not the definition module?
- [ ] Mock set up **before** the action (mock-first)?
- [ ] Test lives near its source in the mirrored tree?

**Mode**
- [ ] New feature: was there a **failing** test before the implementation (ATDD red phase)?
- [ ] Coverage work: do new tests pass immediately (Automate)?

---

## 14. Epic 8 anchor index (verified real files)

| File | Level | Teaches |
|------|-------|---------|
| [test_grading_event.py](../../../Projects/AGY_AVIATIONCHAT/backend/tests/schemas/test_grading_event.py) | Unit | AAA shape; P0 privacy default `consent.export_eligible is False`; scores high on all 5 review dimensions |
| [test_grading_event_writer.py](../../../Projects/AGY_AVIATIONCHAT/backend/tests/services/test_grading_event_writer.py) | Integration | `mock_db` + `writer(mock_db)` fixture composition; `_make_event()` factory |
| [test_grading_event_dataset_api.py](../../../Projects/AGY_AVIATIONCHAT/backend/tests/routers/test_grading_event_dataset_api.py) | E2E | `client_and_svc` fixture (auto-cleanup); `GOV_QUERY` **use-site** patch; `TestClient` API pattern |
| [test_tenancy_gate.py](../../../Projects/AGY_AVIATIONCHAT/backend/tests/routers/test_tenancy_gate.py) | E2E | P0 Trace artifact; CI merge-blocker; RED gate if removed |
| [test_faa_grounding_guard.py](../../../Projects/AGY_AVIATIONCHAT/backend/tests/agents/specialist/test_faa_grounding_guard.py) | — | Live ATDD example (TEA-4): test written red before `agent.py` green |
| [firestore.rules.test.js](../../../Projects/AGY_AVIATIONCHAT/firebase/tests/firestore.rules.test.js) | Integration (emulator) | Security-rules testing (TEA-12): `@firebase/rules-unit-testing` `assertFails`/`assertSucceeds` deny/allow matrix against the real Firestore emulator; **local-only, out of the PR gate** (needs Java 17 — set `JAVA_HOME` per shell); non-vacuity via the emulator's own `PERMISSION_DENIED` logs |

> Paths in this section are relative to this guide's location. Inside the project repo, they are `backend/tests/...` (or `firebase/tests/...` for the rules suite).

---

## 15. TEA knowledge-fragment library (42 fragments)

Session 7 is a returnable reference. Re-run `/bmad-teach-me-testing` → Session 7 to deep-dive any fragment. Highest-value for a Lead: **Configuration & Governance** and **Quality Frameworks**.

**1. Testing Patterns (9)**
`fixture-architecture` · `fixtures-composition` · `network-first` · `data-factories` · `component-tdd` · `api-testing-patterns` · `test-healing-patterns` · `selector-resilience` · `timing-debugging`

**2. Playwright Utils (19)**
`overview` · `api-request` · `network-recorder` · `intercept-network-call` · `recurse` · `log` · `file-utils` · `burn-in` · `network-error-monitor` · `contract-testing` · `pactjs-utils-overview` · `pactjs-utils-consumer-helpers` · `pactjs-utils-provider-verifier` · `pactjs-utils-request-filter` · `pact-mcp` · `pact-consumer-framework-setup` · `pact-consumer-di` · `playwright-cli` · `visual-debugging`

**3. Configuration & Governance (6)**
`playwright-config` · `ci-burn-in` · `selective-testing` · `feature-flags` · `risk-governance` · `adr-quality-readiness-checklist`

**4. Quality Frameworks (5)**
`test-quality` · `test-levels-framework` · `test-priorities-matrix` · `probability-impact` · `nfr-criteria`

**5. Authentication & Security (3)**
`email-auth` · `auth-session` · `error-handling`

---

## Reference links

**TEA documentation**
- Overview: https://bmad-code-org.github.io/bmad-method-test-architecture-enterprise/
- Testing as Engineering: …/explanation/testing-as-engineering/
- Risk-Based Testing: …/explanation/risk-based-testing/
- Test Quality Standards: …/explanation/test-quality-standards/
- Fixture Architecture: …/explanation/fixture-architecture/
- Network-First Patterns: …/explanation/network-first-patterns/
- Step-File Architecture: …/explanation/step-file-architecture/
- Workflows — Test Design / ATDD / Automate / Test Review / Trace: …/how-to/workflows/run-<name>/
- Knowledge base (42 fragments): https://github.com/bmad-code-org/bmad-method-test-architecture-enterprise/tree/main/src/agents/bmad-tea/resources/knowledge

**Local companions**
- TEA Academy session notes + certificate: `Projects/AGY_AVIATIONCHAT/_bmad-output/test-artifacts/tea-academy/Daniel/`
- Master command set: `.agents/commands/INDEX.md`
- Autopilot (`_AP`) lanes: `autopilot_bmad_dev_loop.md`
- Artifact/persistence model: `.agents/rules/artifacts-always-first.md`

---

*Generated from TEA Academy (7/7 complete) + the `sudo-` TEA-gated dev-flow walkthrough. The `sudo-` commands are thin orchestrators over the TEA workflows; the gate in ③ is the only ship/no-ship decision point.*

<!-- CHECKPOINT id="ckpt_mrefjgkp_cqegiw" time="2026-07-10T04:22:41.833Z" note="auto" fixes=0 questions=0 highlights=0 sections="" -->
