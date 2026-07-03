# TEA Method & `sudo-` Workflows — Training Guide (worked from the AviationChat retrofit)

**What this is.** A hands-on training doc: how to run the TEA testing method and the `sudo-` dev-flow workflows we built, taught through a real, completed run. The whole AviationChat test-architecture retrofit (principles P1–P10) is **done** — so this is no longer a progress tracker; it's the "here's how to do it again" playbook, with one full story (**TEA-9**, the local TIA gate) walked end-to-end as the example.

**Two companion docs — read them in this order:**
1. **The reference card** → `_my_resources/diagrams_guides/system/testing_work_flows_tea_sudo.md` — the *concepts* (risk matrix, P0–P3, test levels, "good test" definition, the 9 TEA workflows, the L1–L4 pyramid). Keep it open; this guide does **not** re-teach those.
2. **This guide** → the *operating procedure*: which flow to pick per story, the `sudo-` loop walked through a real story, and how to actually run every test tier (unit, coverage, the local TIA gate, the E2E journeys, the Firestore-rules emulator, temp-0/evals).

**Who owns it:** Daniel (Lead). Working anchor: `AGY_AVIATIONCHAT`.

> **Status — retrofit COMPLETE (2026-07-03).** TEA-1..18 + tea-9 all closed; the foundation (determinism guard, coverage floor, schema tripwires, adversarial guards, temp-0 tier, local eval-drift runner, E2E journey pack, Firestore-rules suite, codified standards, and the local TIA gate) is in place. The final P1–P10 scorecard is Appendix A; the decisions we locked are Appendix B.

---

## 1. The two cadences (don't confuse them)

TEA has a **planning layer** and an **execution layer**, and they run on different clocks.

| Layer | Command | Cadence | Produces |
|---|---|---|---|
| **Test design** (planning) | `bmad-testarch-test-design` (Murat drives it via `/tea`) | **Once per scope** — an epic, or a whole-app retrofit | A P0–P3 risk map + scoped stories with ACs |
| **The `sudo-` loop** (execution) | ① `/sudo-write-story-tests` → ② `/sudo-dev-story-tests` → ③ `/sudo-code-review` → `/sudo-update-sprint-memory` | **Once per story** | RED tests → green code → a gate verdict → a closed story |

**Do I re-run the whole thing for a new epic? No.** The retrofit paid down a whole untested app at once — a one-time Brownfield cost. A new epic is much lighter: one scoped `test-design` pass, then the `sudo-` loop per story. Test design is **risk-proportional** — a high-stakes epic (FAA accuracy, Sully safety, auth) earns the full design pass; a low-risk one (a settings page) skips to the loop with a one-line risk note.

```
New epic
  └─ bmad-testarch-test-design      (scoped to THAT epic — fast)
       └─ per story:  /sudo-write-story-tests → /sudo-dev-story-tests
                      → /sudo-code-review → /sudo-update-sprint-memory
```

---

## 2. Pick the right flow per story type (the most useful finding)

The full `sudo-` loop is the **deluxe** path, not the only path. `/sudo-code-review` internally re-runs suite + trace + nfr + test-review *per story* — but for a **test-only** story there's no production diff for a 3-layer adversarial review to hunt in, and the trace may already be current from a wave-level audit. Match the flow to the story, not the habit:

| Story type | Minimum flow | What you skip | Never skip |
|---|---|---|---|
| **Test-only gap** (backfill missing coverage) | `bmad-testarch-automate` → `bmad-testarch-test-review` | Full 3-layer `bmad-code-review` (no prod diff); per-story trace + nfr | Keyless full-suite run as the zero-new-regression proof; the `/sudo-update-sprint-memory` close-out |
| **E2E new-dev** (new browser-level pack) | `bmad-testarch-automate` (it levels the tests) → `bmad-testarch-test-review` | `bmad-testarch-framework` — do **not** re-scaffold an existing Playwright setup | Specs must run green in their isolated harness |
| **Normal feature** (product code changes) | `bmad-testarch-atdd` (red) → `bmad-dev-story` (green) → `bmad-code-review` | The wrappers' plan/self-audit ceremony *if* the story is small and off the P0 surface | An implement step in the middle — atdd→review alone builds nothing |
| **P0-surface feature** (touches a P0 family — auth, tenancy, FAA fidelity, grading integrity, safety overrides) | The **full** `sudo-` loop ①②③ + close-out | Nothing | The armed gate (`sudo-tests.yaml`) exists precisely for these |
| **Wave / epic boundary** | Re-run `bmad-testarch-trace` (Edit mode on the last matrix) + `nfr` once | Running trace/nfr per-story in between | — |

> **The one escalation rule:** if a "test-only" story turns out to need a behavior-preserving *extraction* to make something testable (the TEA-3 / TEA-4 pattern — pulling a decision out of a big method so a test can reach it), that is a **production change** — bump it up to the feature row and add `bmad-code-review`.

---

## 3. Worked example — TEA-9, the local TIA gate, start to finish

TEA-9 was the **last** story of the retrofit: build a **local pre-push Test Impact Analysis gate** — run only the tests a working diff can break, with a full-suite fail-safe, gated on the code index being fresh. It's a good teaching example because it exercises the **full** `sudo-` loop *and* shows the pure/impure test split, a fail-safe design, and how adversarial review catches "green but silently wrong."

### ① `/sudo-write-story-tests` — story + RED tests first

Wrote the story (`_bmad/bmm/stories/tea-9-tia-ci.md`) and a **failing** spec for the pure decision layer: `backend/tests/tia/test_tia_select.py` — 12 tests, all red because the module `backend.tia.select` didn't exist yet. The red phase is the proof-of-test: a spec that fails *before* the code exists proves the test actually pins something.

**Design decisions locked in the story up front (so ② couldn't drift):**
- **Local pre-push gate, not CI** — the GitNexus index is machine-local and absent from a CI runner (Appendix B, B5).
- **Freshness = `indexed_commit == HEAD`** — a dirty working tree is *not* stale (uncommitted changes are the intended input to a pre-push check).
- **Selection is file-level** (`git diff --name-only` → a test-map), *not* an `impact()` call — sidestepping that `impact()`/`detect_changes()` are MCP-only and under-select on attribute-dispatch. GitNexus is used **only** for the freshness check.

### ② `/sudo-dev-story-tests` — plan → self-audit → build to green

Delivered a clean **pure/impure split** (the TEA-7 precedent — test the brain, keep the I/O thin):

- **`backend/tia/select.py` — the pure brain (fully tested).** `Selection` (frozen dataclass); reasons `STALE_INDEX` / `IMPACT_ERROR` / `EMPTY_SELECTION` / `SELECTED`; `is_index_fresh` (HEAD-equality, dirty ignored); `decide_selection`; a `HUB_FILES` denylist (`agent.py`, `mastery_service.py`, `database.py`, `model_runtime.py`, `registry.py`); `map_changes_to_tests` → `ChangeMap`; `plan_run`. The 12 red tests went green, and `test_tia_mapping.py` (16 more) was added — **28 structural tests total**, all asserting sentinels/enums/sets, zero live model.
- **`backend/tia/gate.py` — the impure runner (thin I/O, reviewed not unit-tested).** Reads `node .gitnexus/run.cjs status` for indexed-vs-current commit, runs `git diff`, dispatches pytest.
- **`scripts/tia_gate.ps1` — the Windows launcher** (thin; all logic lives in `backend/tia/`).

**The fail-safe ladder** — the load-bearing idea. TIA is an *optimization with a full-suite floor*, never a hole:

```
STALE_INDEX  ─┐
IMPACT_ERROR ─┤
EMPTY_SELECTION ─┤─► RUN_ALL  (the full suite is the real gate)
hub-file edited ─┤
any unmapped file ─┘
   fresh + ok + non-empty + all-mapped ─► SELECTED  (run just the affected tests)
```

### ③ `/sudo-code-review` — the gate + adversarial review

The pure layer reviewed clean. The adversarial pass on the impure runner found **two defects the green tests couldn't** — the reason a P0-surface story gets a human-grade review, not just a passing suite:

- **F-CR1 (fixed):** `_dispatch` captured pytest output via `capture_output=True` and **discarded it** → the developer saw no test results. Fixed with a `_stream()` helper (inherited stdio) so pytest prints straight to the terminal.
- **F-CR2 (fixed):** `--include-e2e` was a **no-op** that contradicted its own help text. Fixed to actually dispatch `npm run test:e2e` on opt-in.

All four gate checks PASS (suite baseline-diff-aware · trace · nfr · test-review). **Verdict: PASS** (artifact: `_bmad-output/implementation-artifacts/sudo-code-review-tea-9-tia-ci.md`, HEAD `9825e91`). Evidence recorded: 28/28 TIA tests green post-fix (0.17s); a live `--dry-run` still failed safe (`RUN_ALL` / `STALE_INDEX`, indexed `1fc85d1` ≠ head `9825e91`); the ② full-suite baseline was **2316 passed / 2 skipped / 0 failed** — and since the edit is confined to the untested-but-reviewed `gate.py` (imported by nothing; `select.py` untouched), that's **0 new regressions**.

### Close-out — `/sudo-update-sprint-memory`

Daniel's invocation **is** the sign-off. Because the verdict wasn't FAIL, the story flipped `review → done` in **both** the story frontmatter and `sprint-status.yaml`; learnings routed to memory; active-context pruned. TEA-9 was the last story, so **this close-out closed the entire retrofit.**

### What TEA-9 teaches (the transferable lessons)

- **Pure/impure split:** put the decisions in a pure module and test *those* exhaustively; keep I/O in a thin runner and cover it with review + one integration proof. Don't chase 100% on glue code.
- **Fail-safe > clever:** an under-inclusive optimization is worse than a slow-but-correct full suite. Every doubt path routes to `RUN_ALL`.
- **Green ≠ correct:** structural tests can't catch "output discarded" or "flag is a no-op." Adversarial review does. Keep the full loop for P0-surface work.
- **Assert structure, never prose** (`agent_bearing: true`): sentinels, enums, counts, sets — never string-match a model's words.

---

## 4. What you own vs what the agents do

The loop is two lanes. Agents do the mechanical, repeatable work; the judgment calls are yours. When a command **stops and asks**, that seam is working as designed — don't let an agent guess across it.

**Your lane (human judgment):**
- **Rank the risk.** You confirm which ACs are P0 vs P1/P2; the agent proposes, the priority call is yours.
- **Resolve not-found components.** Decide build/rename/drop for any target the repo lacks — never scaffold tests for something that doesn't exist.
- **Set the coverage number.** Pick the first floor at the *measured* baseline; it may only ratchet **up** (B1).
- **Curate FAA adversarial fixtures + judge rubrics (P6/P8).** Aviation-regulatory judgment — the agents run them; you author what counts as "wrong."
- **Decide ruleset sync scope (P9/P10).** Project-local vs propagate to the lobby. Default project-local; editing master `.agents/` auto-syncs everywhere, so **ask first** (B4 — do not `/sync-agents` on a hunch).
- **Do the L4 review.** `/sudo-update-sprint-memory` treats *your invocation* as the sign-off that flips a story `review → done`; only objectively-red gate tests block you.

**The agents' lane (mechanical):**
- `bmad-testarch-test-design` — drafts the risk-based epic plan you then rank.
- `/sudo-write-story-tests` → `bmad-testarch-atdd` — the failing (red) acceptance tests, one per AC, before code.
- `/sudo-dev-story-tests` → `bmad-dev-story` + `/sudo-self-audit` + `bmad-testarch-automate` — plan, self-audit, implement to green, expand.
- `/sudo-code-review` — adversarial review + full suite (NEW regressions only) + trace + nfr + test-review → one verdict artifact.
- `bmad-testarch-ci` — scaffolds CI changes (used sparingly here; the TIA gate is deliberately local, B5).

---

## 5. Running the tests — the operational reference

All paths are project-root-relative: `Projects/AGY_AVIATIONCHAT/`. Run backend pytest with **`backend/.venv`** (the root `.venv` misses `pytest-cov` and produces a spurious failure).

### 5.1 The keyless full-suite proof (L1 is offline)

The zero-new-regression proof every story owes. Forcing the key empty proves L1 makes **no** live LLM calls (the TEA-2 `_no_live_llm` autouse guard raises `LiveLLMCallBlocked` on any unmocked call unless a test is marked `@pytest.mark.live`).

*Bash:*
```bash
GEMINI_API_KEY="" GOOGLE_API_KEY="" pytest backend/tests/ -v --tb=short
```
*PowerShell:*
```powershell
$env:GEMINI_API_KEY=''; $env:GOOGLE_API_KEY=''; pytest backend/tests/ -v --tb=short
```
Expect all green (or only grandfathered legacy red) and **zero** errors mentioning `google.genai`, `429`, `quota`, or `DefaultCredentialsError`. A test that fails *only* when the key is empty is making a live call and is mis-tiered — mark it `@pytest.mark.live` and move it under the excluded `manual/`, don't feed it a real key.

### 5.2 Coverage (the ratchet)

Branch coverage is scoped to the orchestration risk surface (`backend/agents/specialist` + `backend/routers`). Baseline is 54.02% (`l1_coverage_min: 0.54`; CI `--cov-fail-under=54`), ratcheting **up only** toward 100% on the P0 surface.

```bash
pytest backend/tests/ --cov --cov-branch --cov-report=term-missing --cov-report=html
# open htmlcov/index.html
```

### 5.3 The local TIA gate (what TEA-9 shipped)

A **fast local pre-push pre-check** — run only the tests your diff can break, fail-safe to the full suite. **Not** the merge gate (the full suite stays that).

```powershell
./scripts/tia_gate.ps1 -DryRun          # print the decision, run nothing
./scripts/tia_gate.ps1                    # run the selected tests (or full suite)
./scripts/tia_gate.ps1 -IncludeE2E        # also run the emulator journeys inline
./scripts/tia_gate.ps1 -Base main_debug   # diff base (default: main_debug)
```

If the GitNexus index is behind HEAD (e.g. after pulling work committed on another machine), it prints `STALE_INDEX` and runs everything — re-index with `node .gitnexus/run.cjs analyze` to re-enable fast selective runs. (This gate operationalizes the standing rule in memory `gitnexus-verify-index-fresh-after-pull`.)

### 5.4 The E2E journeys — how to run them

> **Canonical README:** `Projects/AGY_AVIATIONCHAT/frontend/e2e/journeys/README.md` (the TEA-16 "GAP-7 authenticated E2E journey pack"). Reproduced below so it's not lost again.

Playwright E2E for the P0/P1 **learner** journeys, on a Firebase **Auth + Firestore emulator** harness — authenticated journeys run deterministically with no real credentials, no live LLM, no backend.

```bash
cd frontend
npm run test:e2e                 # all journeys
npm run test:e2e -- auth-wall    # one spec (filter by name)
npm run test:e2e -- --headed     # watch it run
```

`npm run test:e2e` → `e2e/run-e2e.mjs`, which:
1. **auto-discovers a Java 17 JRE** (Adoptium, at `C:/Program Files/Eclipse Adoptium`) for the emulators — **set `JAVA_HOME` yourself if Java lives elsewhere** (memory `firestore-rules-tests-need-java`); if none is found it errors out;
2. **reuses the `firebase-tools`** already installed for the TEA-12 rules suite (`firebase/tests/node_modules`) — no new frontend dependency (if missing, `npm install` in `firebase/tests` first);
3. wraps `playwright test --config playwright.journeys.config.ts` inside `firebase emulators:exec --only auth,firestore --project demo-agy`, so the emulators are live for seeding and the whole run, then torn down.

A **fresh** Next dev server boots on **port 3100** with `NEXT_PUBLIC_USE_FIREBASE_EMULATOR=true` (never reused), so the client `connectAuthEmulator` / `connectFirestoreEmulator` calls fire and the CSP allows the emulator ports — both gated on that flag, zero production impact.

**Seeded learners** (via `e2e/global-setup.ts` + `e2e/support/learner.ts`):
- **`learner@e2e.test`** — ENTITLED (`entitled` custom claim) → beta agents unlocked.
- **`locked@e2e.test`** — un-entitled → the beta lock fires.
- Both get a Firestore `users/{uid}` profile so the dashboard treats onboarding as done.

**Journeys covered:** (1) **auth-wall** — unauth deep-link to `/dashboard` bounces to landing; authed learner is not evicted. (2) **entitlement-lock** — un-entitled learner hitting the Specialist funnel gets the closed-beta popup → `/earlyaccess`. (3) **verification-ordering** — the fast Specialist answer renders **before** the FAA-verified inline Sources badge (the FR39-E ordering invariant).

**Documented follow-ups (not covered):** the full 4-step lesson progression beyond the ordering slice; Voice (Sully/Igor WebSocket) journeys — the 4030 entitlement close is unit-covered (TEA-15); an E2E would need a mock WS server.

### 5.5 The Firestore-rules emulator suite (TEA-12)

Security-rules deny/allow matrix via `@firebase/rules-unit-testing`. **Local-only, out of the PR gate.** Needs Java 17 on PATH:

```bash
# set JAVA_HOME first (silent Temurin MSI doesn't add it) — see memory firestore-rules-tests-need-java
cd firebase/tests && npm test        # 61/61 green; non-vacuity via the emulator's PERMISSION_DENIED logs
```

### 5.6 temp-0 determinism + L3 evals (manual / nightly, never the PR gate)

- **temp-0 (TEA-6):** `pytest backend/tests/integration_temp0 -m temp0 -v` — real agent, temperature 0, asserts `routing_tag` is stable across runs. Needs a live key; **skips** without one (`@temp0` + `@live`, in `norecursedirs` so it never rides the gate).
- **L3 eval drift (TEA-7):** `backend/evals/drift.py` + `run_nightly.ps1` (Task Scheduler) — flags fewer-passes / PASS→FAIL / negative-control-inverse / error-spike. **Local by design** (B5 — the live key stays off CI). The must-FAIL negative control (`NC_01` in `answer_leak.json`) proves the judge is awake.

---

## 6. Quick reference

### Command cheat-sheet

| Command / workflow | One-line job | When |
|---|---|---|
| `/tea` (Murat) | Master Test Architect persona; drives the TEA workflows | Design; strategy consults |
| `bmad-testarch-test-design` | Risk-rank the epic P0–P3; emit the strategy doc | Once per epic |
| `bmad-testarch-framework` | One-time test-bench bootstrap (Playwright/pytest) | Project setup (often redundant now) |
| `bmad-testarch-ci` | Scaffold CI pipeline (TIA selection, nightly job) | Rarely — TIA is local here (B5) |
| `bmad-testarch-atdd` | Write RED acceptance tests before code | inside `/sudo-write-story-tests` ① |
| `bmad-testarch-automate` | Expand coverage at the right level | ② + standalone for brownfield gaps |
| `bmad-testarch-trace` | Traceability matrix + PASS/CONCERNS/FAIL verdict | ③ + wave boundaries |
| `bmad-testarch-nfr` | NFR audit (perf/security/reliability) | ③ when `nfr`/`agent_bearing` |
| `bmad-testarch-test-review` | 0–100 test-quality/flake score | ③ |
| `/sudo-boot-sprint-memory` | Boot: where am I, what's next, which command (read-only) | Session start; sets the active project |
| `/sudo-write-story-tests` | ① Create story + write failing tests | After boot picks a story |
| `/sudo-dev-story-tests` | ② Plan → self-audit → implement → automate | After ① |
| `/sudo-code-review` | ③ Review + the test gate → one verdict | After ② |
| `/sudo-update-sprint-memory` | Close-out: flip → done, route learnings, prune | Closing a story/session |
| `regulatory-verification-protocol` | FAA citation-accuracy doctrine | Before authoring adversarial fixtures |

### The `sudo-tests.yaml` dial (final values)

Located at `_bmad-output/sudo-tests.yaml`. Its **presence** arms the gate; absent → `/sudo-code-review` returns WAIVED.

| Key | Value | What it does |
|---|---|---|
| `required_tiers` | `[L1, L2]` | Tiers that must be present + green (deterministic, free). **L3 intentionally not required** (costs tokens / live key). A missing required tier → FAIL. |
| `l1_coverage_min` | `0.54` | Advisory coverage floor in the wrapper; the real teeth are CI `--cov-fail-under=54`. **Only ever goes UP** (B1). |
| `agent_bearing` | `true` | Arms the Test-Adequacy auditor + the "no string-match on probabilistic output" rule. |
| `nfr` | `true` | Runs the NFR audit (reliability = fallback/circuit-breaker; security = prompt-injection/answer-leak). |
| `waive` | `false` | `false` = gate LIVE. `true` forces WAIVED without deleting the file (greppable bypass breadcrumb). |
| `standards` | `…/testing-standards.md` | The Always-On testing policy (TEA-8): matrix + P0 surface + the agent-bearing rule. Project-local (B4). |
| `tier_map` | `…/ai-test-tiers.md` | Doc map of existing tests per tier + the ratchet plan (not read by the gate). |
| `baseline` | `at-opt-in` | The suite at opt-in is the red baseline; only regressions NEW to a story fail. Records git HEAD per verdict. |

### Where artifacts land

- **Strategy:** `test-design-epic-{n}.md` (+ system-level `test-design-qa.md`) under `{test_artifacts}`.
- **① RED tests:** new story in `_bmad/bmm/stories/`; failing test files; `atdd-checklist-{story}.md`.
- **② Dev:** `implementation_plan.md`; implemented code; green + expanded tests.
- **③ Gate:** verdict at `_bmad-output/implementation-artifacts/sudo-code-review-<story>.md` (verdict + each check + actual output + story id + git HEAD); updated `_artifacts/<epic>/<story>/walkthrough.md`; `traceability-matrix.md`; `nfr-assessment.md`; `test-review.md`.
- **Coverage:** `htmlcov/index.html` (local). **E2E:** `frontend/e2e/journeys/`. **Adversarial evals:** `backend/evals/scenarios/*.json` → `backend/evals/reports/`.
- **Close-out:** updated `active-context.md`, `sprint-status.yaml`, story frontmatter, component specs/rules, Claude memory.

---

## Appendix A — What the retrofit delivered (final P1–P10 scorecard)

| Principle | State | Where it lives |
|---|---|---|
| **P1** Determinism isolation (L1 mocks all LLM calls) | ✅ TEA-2 | `_no_live_llm` autouse guard in root `conftest.py`; keyless suite green, 0 live leaks |
| **P2** Coverage discipline (measurable branch floor) | ✅ TEA-5 | `pytest-cov` + `[tool.coverage]` scoped to specialist+routers; 54.02% baseline; CI `--cov-fail-under=54` |
| **P3** Behavioral-trigger testing | ✅ TEA-3 | 14 L1 tests: Sully depth-≥3 override + telemetry + `confidence_reset` (via a behavior-preserving extraction) |
| **P4** Variance control (temperature 0.0) | ✅ TEA-6 | `temperature` kwarg on `evaluate()`; `backend/tests/integration_temp0/` (`@temp0`+`@live`, never in the gate) |
| **P5** Schema-contract enforcement | ✅ TEA-1 | 11 L1 `ValidationError` tripwires on `SocraticExecutorResponse` + `SullyResponse` |
| **P6** Adversarial / negative testing | ✅ TEA-4 (gate) + TEA-18 (L3 set) | In-gate empty-dossier → `sources==[]` guard; FAA input-adversarial fixtures + `NC_FAA_01` wired |
| **P7** Test Impact Analysis | ✅ TEA-9 | **Local** pre-push gate (`backend/tia/` + `scripts/tia_gate.ps1`) with full-suite fail-safe — deliberately **not** CI (B5) |
| **P8** Semantic-eval separation (nightly L3) | ✅ TEA-7 | Local `backend/evals/drift.py` + `run_nightly.ps1`; no GitHub nightly by design (B5) |
| **P9** Machine-enforced standards | ✅ TEA-8 | `testing-standards.md` (project-local, B4), wired via `sudo-tests.yaml standards:` + `AGENTS.md` |
| **P10** Test-first for agentic code | ✅ TEA-8 | The `sudo-` loop is this; L1+L2-by-default codified; a pre-commit hard-stop is a future ratchet |

Also delivered outside P1–P10: **TEA-12** (Firestore-rules emulator suite, 61/61), **TEA-16** (E2E journey pack), **TEA-17** (P1 unit stragglers).

## Appendix B — Decisions we locked

| # | Decision | Rationale |
|---|---|---|
| **B1** | The coverage floor only ever ratchets **UP** | Set it above today's real number and every story fails the gate → people switch it off. |
| **B2** | FAA adversarial fixtures are **human-authored/ratified** first | Regulatory judgment is Daniel's lane; verify against primary FAA sources, not memory (memory `domain-gated-fixtures-web-verify`). |
| **B4** | Testing standards are **project-local**, not synced to the lobby | Prove it in AviationChat first; editing master `.agents/` auto-syncs everywhere — do **not** `/sync-agents` on a hunch. |
| **B5** | The TIA gate + eval-drift runner are **local, never CI** | The GitNexus index is machine-local/absent from a CI runner, and the live key stays off CI. The full suite remains the merge gate. |

---

*Companion (concepts & command reference): `_my_resources/diagrams_guides/system/testing_work_flows_tea_sudo.md`. This guide can be relocated next to it (out of `open_tasks/`) now that the retrofit is closed — it's a reference, not an open task.*
