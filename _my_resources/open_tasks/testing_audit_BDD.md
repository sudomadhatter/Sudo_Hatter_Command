# Testing Audit & BDD Readiness Assessment (`testing_audit_BDD`)

**Date:** 2026-07-09 · **Auditor:** Claude (Fable 5), senior-dev audit run from the command center
**Scope:** AGY_AVIATIONCHAT (primary) · Fresh_Workspace_BMAD · the shared `/sudo` + `/autopilot` testing pipeline in `.agents/`
**Trigger:** Daniel's open task — *"verify all the /test-automatic are run and the story tests are actually indexed and running for the full test suite — I missed that step on some of them I think"* — plus the TDAD/BDD go-forward decision (`_my_resources/open_tasks/tdad_stack_install_guide.md`).

---

## 0. Executive Summary — the six verdicts

| # | Question | Verdict |
|---|---|---|
| 1 | **Is the TEA setup healthy?** | **YES, genuinely strong** — armed gate (`waive: false`), full artifact chain, gate trajectory FAIL (5/29) → CONCERNS (7/02) → **PASS (7/03, P0 weighted 100%)**, coverage floor ratcheted to 54% branch and enforced in CI. Three named holes: NFR audit never executed, E2E journeys never wired into CI, and doc staleness (details §2). |
| 2 | **Did devs run `/bmad-testarch-atdd` without `/bmad-testarch-automate`?** | **YES — confirmed on 13 of 14 Epic-8 ATDD stories.** Only 8.23.2 has an automate expansion pass. But see verdict 3 — the consequence is different from the suspicion. |
| 3 | **Are those stories' tests missing from the CI lifecycle?** | **NO — this is the good news.** CI runs the *full* suite (no test selection), so every collected test is in CI by default. All 6 red-phase `.red.test.tsx` files and ~95 ATDD-fingerprint backend files run green in `pr-check.yml` today. What the 13 stories are missing is *expansion depth* (edge/API/contract coverage the ATDD pass didn't reach), not CI inclusion. |
| 4 | **So is the CI lifecycle sound?** | **NO — but the holes are elsewhere** (§4.5): ① `pr-check.yml` only triggers on PRs → `main`, while the working branch model integrates on `main_debug` → **the integration branch has no automated CI gate at all**; ② `deploy-backend.yml` deploys to Cloud Run on push with **zero tests**; ③ the 3 P0 E2E journey specs (tea-16's deliverable) are excluded from CI's Playwright run and their runner is called by no workflow — despite the 7/03 PASS gate crediting the E2E level as MET. |
| 5 | **Do we need to go back and add BDD to existing work?** | **NO mass retrofit.** Forward-only adoption + a narrow, risk-based backfill of the P0 (A1–A9) surfaces as they get touched. Reasoning + the pilot plan in §5. |
| 6 | **Is Fresh_Workspace_BMAD ready for TDAD?** | **Ready-but-empty scaffold.** pytest-bdd pinned, TEA installed (template-state), zero tests/stories/CI. Two bootstrap items before first story: `sudo-tests.yaml` (else the gate auto-WAIVES) and a CI workflow. |

**Top 5 actions (full plan in §6):**
1. Extend `pr-check.yml` to `branches: [main, main_debug]` — one line; puts the whole suite gate on the branch where integration actually happens.
2. Gate `deploy-backend.yml` on the backend test job before deploying.
3. Wire the E2E journeys pack into CI (emulator job or nightly) — it's P0 acceptance coverage currently credited but never executed in CI.
4. Backfill `/bmad-testarch-automate` risk-based on the P0-surface subset of the 13 skipped stories (not all 13), then add an automate-evidence check to the review gate so this can't silently recur.
5. Run `bmad-testarch-nfr` once — it is armed (`nfr: true`) but has never produced an assessment artifact.

---

## 1. Method & evidence trust

- Three parallel ground-truth sweeps (TEA artifact inventory; AGY test estate vs CI; pipeline spec + Fresh_Workspace), then direct verification of every load-bearing claim (workflow triggers, gate dial, verdict census, per-story artifact census) by reading the files.
- **Content/front-matter dates were trusted over filesystem mtimes** — the whole `_bmad-output` tree was bulk-touched 2026-07-08.
- Doc claims were treated as claims, not facts (sprint docs drift): the gate-PASS/E2E discrepancy in §2.4 was caught exactly this way.
- Tooling caveat that affected this audit and will affect future ones: **from a lobby session, the Glob tool silently returns empty under `Projects/` even when `path` points inside the project and the files are not ignored by the project's own git** (the lobby `.gitignore`'s `Projects/` rule bleeds through). The Grep tool works when pointed inside a project; Glob does not. Two findings in this audit were nearly missed to this false-negative; `bash find` was used to ground-truth. Recommend extending the ROOT-LAW §4 search-gate note (currently Grep-only) to cover Glob.

---

## 2. TEA setup assessment

### 2.1 Configuration & the gate dial (current, verified on disk)

| Item | AGY_AVIATIONCHAT | Fresh_Workspace_BMAD |
|---|---|---|
| TEA module | v6.9.0, installed 2026-06-29, `_bmad/tea/config.yaml` | v6.2.2, installed 2026-03-28, **template-state** (`{{USER_NAME}}` placeholder) |
| Outputs root | `_bmad-output/test-artifacts/` (test-design / traceability / test-reviews subdirs) | exists, empty (INDEX.md only) |
| Gate opt-in `sudo-tests.yaml` | **PRESENT & armed**: `required_tiers: [L1, L2]`, `l1_coverage_min: 0.54`, `agent_bearing: true`, `nfr: true`, `waive: false`, `baseline: at-opt-in` | **ABSENT → `/sudo-code-review` auto-WAIVES** (gate never runs) |
| Coverage enforcement | Authoritative floor = CI `--cov-fail-under=54` in `pr-check.yml` (branch coverage, orchestration surface; baseline 54.02% measured 2026-06-29, ratchet-up-only) | none |
| Testing standards | `testing-standards.md` + `ai-test-tiers.md` codified (TEA-8, project-local by design B4) | none |

### 2.2 The artifact chain — what exists (AGY)

All under `Projects/AGY_AVIATIONCHAT/_bmad-output/test-artifacts/` unless noted:

- **test-design:** `test-design-architecture.md`, `test-design-qa.md`, `test-design-progress.md`, handoff doc.
- **Traceability + gates (bmad-testarch-trace):** 3 generations — 2026-05-29 **FAIL** (bannered STALE), 2026-07-02 **CONCERNS** (P0 84.1% weighted; produced the GAP-1..7 → tea-12..18 worklist), **2026-07-03 PASS** (P0 weighted 100%, all gaps + TIA closed, ~2,316 backend + 332 frontend tests green, all four levels recorded MET — but see §2.4 on the E2E level).
- **ATDD (bmad-testarch-atdd):** 14 checklists, all Epic 8 (8.19.5–8.23.2), + 6 committed frontend red-phase files (`*.red.test.tsx`).
- **Automate (bmad-testarch-automate):** 7 summaries — TEA-13/14/15/16/17/18 + story 8.23.2 only.
- **test-review:** 8 files (tea-8, tea-12..14, tea-16..18, + generic).
- **Review verdicts:** `_bmad-output/implementation-artifacts/sudo-code-review-*.md` — **all 14 Epic-8 ATDD stories + tea-1..11 + 15-2** are present. Epic-8 verdicts: 6 PASS / 8 CONCERNS (all ship-able) / 0 FAIL / 0 WAIVED.
- **Session ledger:** `_artifacts/tea/` tea-1..tea-18 folders + INDEX; TEA academy notes (`tea-academy/Daniel/`).
- **NFR (bmad-testarch-nfr): NOTHING.** Zero assessment artifacts in either project (see §2.4).

### 2.3 What's working well

1. **The gate has real teeth and was really used.** Every Epic-8 story and every TEA story carries a verdict artifact with tier results and suite output. Nothing was rubber-stamped WAIVED.
2. **Risk-based doctrine is coherent and followed.** The MIN-FLOW split (test-only gap stories = automate → test-review; feature stories = full loop; P0 surface = full loop, never waived) is ratified in sprint-status and matches the artifact record for the TEA-N series exactly.
3. **Coverage discipline is live, honest, and ratcheted** — 0.0 grandfather → measured 54.02% baseline → CI-enforced 54 floor, with 100%-on-P0 recorded as destination, not pretended as current.
4. **Determinism tiers are enforced by design**: `norecursedirs` keeps live-key tiers (`manual/`, `evals/`, `integration_temp0/`) out of the PR gate; the TEA-2 no-live-LLM guard + `live`/`temp0` markers exist.
5. **The trace matrix maps FRs → real file:line evidence** — the 07-02 audit classified ~47 FR families into P0 A1–A9 / P1 B1–B9 and mapped them to actual tests.

### 2.4 TEA gaps (named, with evidence)

| Gap | Evidence | Severity |
|---|---|---|
| **NFR audit never executed** despite `nfr: true` arming it in every review | Zero `nfr-assessment.md` anywhere; every `*nfr*` hit is skill template/knowledge. Reviews either skipped gate sub-step 4 or never persisted it. | **High** — the dial claims perf/security/reliability auditing that has never happened. |
| **E2E level credited as MET while the journeys pack is not in CI** | 7/03 gate PASS records all levels MET; `frontend/playwright.config.ts` has `testIgnore: ['**/journeys/**']`; CI runs `npx playwright test` (default config, 4 generic specs); journeys runner `e2e/run-e2e.mjs` appears in no workflow. tea-16's own never-skip condition was "specs must run green in the blocking frontend-e2e CI job" — not met. | **High** — P0/P1 acceptance journeys (auth-wall, entitlement-lock, verification-ordering) execute only when someone runs them locally. |
| **bmad-testarch-framework / -ci never produced artifacts** — CI is hand-maintained | No framework/CI scaffold outputs; TIA exists only as the local `scripts/tia_gate.ps1` (TEA-9) | Medium — fine in itself, but it means CI wiring has no owner in the pipeline (§4.4). |
| **Doc staleness / drift** | `tea_testing_guide.md` header still says CONCERNS/84.1% (superseded by 7/03 PASS); its §9 still quotes `l1_coverage_min: 0.0` (now 0.54); `_artifacts/Fresh_Workspace_BMAD/active-context.md` body is actually an AGY TEA-15 brief (mislabeled location). | Medium — this system's docs steer agents; stale steering re-creates exactly the class of gap this audit chased. |
| **Fresh_Workspace_BMAD gate would silently WAIVE** | No `sudo-tests.yaml` → `/sudo-code-review` Step 2 short-circuits to WAIVED | Medium now, High the day real work starts there. |

---

## 3. The test estate vs what CI actually runs (AGY ground truth)

### 3.1 Inventory

| Layer | On disk | Collected/run by CI |
|---|---|---|
| Backend pytest (`backend/tests/`) | **184 `test_*.py` files** (~2,316 tests) | ~177 files — everything except `manual/` (4), `evals/` (2), `integration_temp0/` (1), excluded via `norecursedirs` **by design** |
| Backend strays (`backend/` root) | 4 legacy files: `test_orchestrator.py`, `test_reasoner.py`, `test_router_latency.py`, `test_swarm.py` (May 19, pre-`tests/` layout) | **Never collected** (outside `testpaths`) |
| Non-collected naming | `backend/tests/diag_raw_api.py`, `diag_verifier.py`, `diag_verifier_quick.py` | Never collected (don't match `test_*.py`) — fine if intentional, worth renaming to make intent explicit |
| Frontend vitest | **57 spec files** (~332 tests), incl. all 6 ATDD `*.red.test.tsx` | All 57 run (`vitest run`, excludes only `e2e/**`) |
| Playwright E2E — default config | 4 specs (`chat`, `hanger-talk`, `sudo_admin`, `sudo_admin_management`) | Run in CI (`npx playwright test`) |
| Playwright E2E — **journeys** config | 3 specs (`auth-wall`, `entitlement-lock`, `verification-ordering`) — needs Firebase emulators + Java | **Not run by any workflow** (local `npm run test:e2e` / `tia_gate.ps1 -IncludeE2E` only) |

Runtime skips inside the collected suite: exactly **one hard skip** — `backend/tests/services/test_study_context_v2.py:202` (`Circular import: backend.routers.hr ↔ backend.main — needs source fix`) — plus 2 conditional self-skips on absent local data fixtures (`test_schemas_quiz_bank.py:394`, `test_ingest_quiz_banks.py:87`). Frontend/E2E: **zero** active `.skip`/`.todo`/`xfail`. Two files whose *docstrings* claim "every test skipped" (`test_create_school.py`, `test_sudo_admin_shell.py`, `e2e/sudo_admin.spec.ts`) are in fact un-skipped and running — stale comments from the red phase, worth deleting.

### 3.2 What each workflow actually does

| Workflow | Trigger | Tests |
|---|---|---|
| `pr-check.yml` (the quality gate) | `pull_request` → **`[main]` only**, paths `backend/** frontend/**` | pytest full suite + `--cov --cov-branch --cov-fail-under=54` (hard gate); `vitest run` (hard); `npx playwright test` default pack (hard); ruff + ESLint report-only |
| `deploy-backend.yml` | push → `main`, paths backend/Dockerfile | **ZERO tests** → docker build → Cloud Run deploy (no-traffic) → `/health` smoke → promote |
| `deploy-frontend.yml` | push → `main` | vitest with **`continue-on-error: true`** (advisory only) + build |
| `deploy-rules.yml`, `firestore-backup.yml` | — | no tests |

### 3.3 The branch-model hole (biggest single finding of the audit)

The working git model is: `claude/*` session branches → PRs into **`main_debug`** (merged via `/merge_main_debug`) → Daniel manually promotes `main_debug` → `main`.

- `pr-check.yml` fires only on PRs targeting `main`. **PRs into `main_debug` match no workflow — they merge with no CI run at all.** (`/merge_main_debug`'s "not red" check passes trivially when there are no checks.)
- If the `main_debug` → `main` promotion is a direct push (not a PR), `pr-check` never fires there either — and `deploy-backend`/`deploy-frontend` then ship that push, backend with zero tests.
- Net: **in the normal flow, the only test gates are local** (`/sudo-code-review`'s suite run, `tia_gate.ps1`). The CI gate exists but sits on a path traffic doesn't take.
- *Caveat:* GitHub branch-protection/required-check settings aren't visible from disk; verify none compensate. The workflow files alone say the integration branch is ungated.

### 3.4 Not-in-CI ledger — verdict per item

| Item | In CI? | Verdict |
|---|---|---|
| `manual/`, `evals/`, `integration_temp0/` tiers | No | **By design** (live-key / L3 / nightly tiers) — but no scheduled runner exists anywhere (local `run_nightly.ps1` only, accepted as B5). Revisit deliberately, don't drift into it. |
| E2E journeys pack (3 specs) | No | **HOLE** — P0 acceptance coverage, gate-credited, never CI-executed. |
| 4 legacy `backend/test_*.py` strays | No | **Rot** — delete or fold into `backend/tests/`. |
| 3 `diag_*.py` scripts | No | OK if diagnostic-only; rename/move to make intent explicit. |
| 1 hard-skipped test (circular import) | Collected, skipped | **Debt with a named source fix** — fix `backend.routers.hr ↔ backend.main`. |
| Backend push-deploys | — | **HOLE** — `deploy-backend.yml` has no test job. |
| PRs → `main_debug` | — | **HOLE** — no workflow triggers (§3.3). |

---

## 4. The ATDD → automate investigation (Daniel's question, answered precisely)

### 4.1 What the pipeline spec says should happen

Per `.agents/commands/sudo-dev-story-tests.md` (and the `_AP` autopilot variant), **the automate pass is not optional and not a separate human step** — it is Step 4 *inside* step ②:

> "## Step 4 — Automate (expand coverage) — Invoke the **`bmad-testarch-automate`** skill to expand API / UI / contract coverage around what was built — closing gaps the ATDD pass did not reach."

So the suspicion "devs ran atdd then failed to run automate" translates to: *step ② was run in a way that skipped (or didn't persist) its own Step 4.*

### 4.2 Per-story pipeline compliance (ground truth from artifacts)

All 14 Epic-8 ATDD-series stories, plus the TEA-N gap stories:

| Story | ① ATDD red (checklist) | ② plan + self-audit + walkthrough | ②-Step-4 automate summary | ③ gate verdict |
|---|---|---|---|---|
| 8.19.5 admin school portal | ✓ | ✓ | **✗** | CONCERNS |
| 8.19.6 sudoadmin shell | ✓ | ✓ | **✗** | CONCERNS |
| 8.19.7 relocate operator surfaces | ✓ | ✓ | **✗** | CONCERNS |
| 8.19.8 school+admin management | ✓ | ✓ | **✗** | PASS |
| 8.20.1 cost meter | ✓ | ✓ | **✗** | PASS |
| 8.20.2 per-student spend API | ✓ | ✓ | **✗** | CONCERNS |
| 8.20.3 cost dashboard UI | ✓ | ✓ | **✗** | PASS |
| 8.20.4 per-surface cost | ✓ | ✓ | **✗** | PASS |
| 8.21.1 grading dataset API | ✓ | ✓ | **✗** | PASS |
| 8.21.2 grading dataset UI | ✓ | walkthrough only | **✗** | PASS |
| 8.22.1 graph-RAG exam ingestion | ✓ | ✓ | **✗** | CONCERNS |
| 8.22.2 curriculum brain graph | ✓ | ✓ (autopilot run 2026-07-03) | **✗** | CONCERNS |
| 8.23.1 exam insights API | ✓ | ✓ | **✗** | CONCERNS |
| **8.23.2 exam insights view** | ✓ | ✓ | **✓** (ran automate after red went 7/7 green) | CONCERNS |
| TEA-13..18 (gap stories) | — (MIN FLOW: no ATDD by doctrine) | — | ✓ all six | test-review PASS |

**Score: 13 of 14 feature stories skipped the automate expansion.** The TEA-N series is *not* a violation — MIN FLOW for test-only stories is automate→test-review without ATDD, and that's exactly what the record shows.

### 4.3 Are those 13 stories' tests in the CI lifecycle? YES.

This is where the suspicion inverts. Because `pr-check.yml` runs the **entire** suite (no test-impact selection, no marker filter), any test that pytest/vitest collects is in CI automatically:

- All 6 `*.red.test.tsx` red-phase files are collected by vitest's default include and run in CI (verified un-skipped).
- ~95 of 184 backend test files carry ATDD fingerprints (`ATDD RED-phase` docstrings, `Source: _bmad/bmm/stories/story-*.md`); they were driven green and run in CI.
- The only ATDD-origin tests NOT in CI sit in the deliberately excluded tiers (`integration_temp0/`) or the journeys pack (§3.4) — neither is an Epic-8 story casualty.
- Every one of the 14 stories passed through the ③ gate, which runs the full suite locally and records the output.

**So: no story tests were orphaned from CI by the missing automate step.** The full-suite CI design acted as a safety net.

### 4.4 What was actually lost, and the root cause

What the 13 stories are missing is what automate *produces*: **breadth around the happy path** — edge/boundary cases, API/contract negatives, component-level coverage the red-phase ATDD scaffolds didn't reach. The ACs are covered (trace matrix proves it); the walls around them are thinner than the doctrine intends. Cost caps (8.20.x → P0 family A6), grading data-moat surfaces (8.21.x → A5), and the sudo-admin auth surfaces (8.19.x → A2/A3) deserve that breadth most.

Root cause is a missing enforcement seam, twice over:

1. **The ③ gate doesn't check that automate ran.** It verifies tiers green + no new regressions + trace coverage — a story can sail through with zero expansion evidence. All 14 did.
2. **Nothing in the pipeline wires or verifies CI.** No flow step invokes `bmad-testarch-ci`; tests enter CI only because CI happens to run everything. The day the local TIA gate (`tia_gate.ps1`) or any selection mechanism is promoted into `pr-check.yml`, un-mapped tests start silently dropping out — the exact failure Daniel feared, deferred rather than absent.

### 4.5 Verdict on the suspicion

> **Right instinct, wrong failure mode.** The automate step was indeed skipped on 13 of 14 feature stories — but full-suite CI kept their tests in the lifecycle, so the damage is missing expansion coverage, not orphaned tests. The genuinely orphaned things are elsewhere: the E2E journeys pack (never in CI despite being gate-credited), the ungated `main_debug` integration branch, and the test-less backend deploy. Fix those three and add an automate-evidence check to the gate, and both the suspected and the actual failure modes close.

---

## 5. BDD readiness & the retro-fit decision

### 5.1 Where BDD stands today

- **Zero Gherkin anywhere**: no `.feature` files, no `pytest_bdd` imports, no step definitions, no `tests/features/` or `tests/bdd/` dirs — in either project.
- **The rails are already laid**: `pytest-bdd>=7.0.0` pinned in both projects' `backend/requirements.txt` (so it installs in CI), pytest-bdd 8.1.0 verified in both venvs, aider 0.86.2 global, and — importantly — **`/sudo-bdd-tests` (the Vision Lock) is already wired as step ①b inside `/sudo-write-story-tests`**, emitting `.feature` → `backend/tests/features/` and steps → `backend/tests/bdd/`. The autopilot track mirrors it.
- pytest-bdd is additive: `.feature` scenarios register as ordinary pytest items, so **new BDD tests are automatically inside `pr-check`'s full-suite run** — no CI change needed for Layer 1.

### 5.2 Do we go back and retrofit BDD onto existing work? **No — and here's the reasoning.**

1. **BDD's value in TDAD is prospective, not archival.** The Vision Lock exists to stop an *agent about to build something* from misreading intent. For ~300 done stories, the building already happened; the intent is now pinned by ~2,600 green tests and a traceability matrix with file:line evidence. A retroactive `.feature` file restates what tests already assert — cost without drift-protection.
2. **The conversion is not free or safe.** Translating green pytest suites into scenario+step-def pairs is churn across a PASS-state suite protected by a ratcheted coverage floor. Any regression introduced by test refactoring is pure loss.
3. **The trace matrix already does BDD's documentation job for done work** — AC → test mapping is exactly what a `.feature` file would encode, and it exists, audited, at P0 100% weighted.
4. **The 13 automate-skipped stories are a coverage-depth gap, not a contract gap** — the fix is automate passes (§6 P1-4), not Gherkin. Don't conflate the two backfills.

### 5.3 What TO do instead (forward-only + targeted ratchet)

1. **Forward-only from the next story**: every new story in both tracks goes through `/sudo-bdd-tests` → `.feature` contract → ATDD red from the contract. The machinery is already in place; it just has to be *exercised once* to prove the loop.
2. **Pilot on the next real Epic 8/9 story** — exactly the TDAD guide's own "What's Next #1" (one `.feature` for an existing Epic-8 story surface to prove the pattern end-to-end before autopilot relies on it). Success criteria: the `.feature` runs red under pytest-bdd, aider/dev drives it green, `pr-check` collects it with zero config change.
3. **Risk-based backfill as a ratchet, not a project**: when a story next *touches* a P0 family surface (A1–A9: FAA citation fidelity, auth/session, entitlement/tenancy, mastery state machine, grading integrity, cost caps, safety overrides, Part 141 logging, privacy/consent), the Vision Lock step also writes the `.feature` contract for the invariant being touched. Over time the P0 surface accretes living contracts without a big-bang conversion. This mirrors the coverage-floor doctrine that already works here: ratchet up, never big-bang.
4. **Fresh_Workspace_BMAD adopts BDD from story #1** — it has zero legacy, so it's the pure TDAD proving ground. Bootstrap first (§6 P2-9).

### 5.4 TDAD integration notes (so the rollout doesn't snag)

- **Stack-doctrine mismatch to expect:** the `bmad-testarch-atdd`/`framework` skill checklists are Playwright/Cypress-oriented, while the TDAD Layer-1 flow is pytest-bdd/Python. The skills work, but their fixture/scaffold suggestions will occasionally speak the wrong dialect — worth a customize-override pass (`bmad-customize`) when the pilot runs. ✅ **Landed 2026-07-09:** `_bmad/custom/bmad-testarch-atdd.toml` + `bmad-testarch-automate.toml` in AGY + Fresh (pytest-bdd dialect pin; automate `on_complete` persists `automation-summary-<story>.md` — the ③ gate check-5 evidence). All three repos carry them — lobby included (direct BMAD skill runs from the lobby seat bind `{project-root}` to the lobby; the sudo flow itself always binds to the child project).
- **Aider (Layer 2) is autopilot-only by design** — keep it out of `requirements.txt` (already documented in `requirements-tdad.txt`).
- **The clean-room adversarial reviewer (TDAD Phase 5) is designed, not built** — current `/sudo-code-review` carries session context. Fine for now; noted so it isn't assumed done.

---

## 6. Prioritized remediation plan

**P0 — close the real CI holes (this week, small diffs):**

| # | Action | How |
|---|---|---|
| P0-1 | **Gate `main_debug`.** | `pr-check.yml` line 9: `branches: [main]` → `[main, main_debug]`. Verify GitHub branch-protection required-checks after. One line; the whole suite then guards the branch integration actually uses. |
| P0-2 | **Gate the backend deploy.** | Add a test job to `deploy-backend.yml` (pytest, same command as pr-check) with `needs:` ordering before deploy. Decide deliberately whether `deploy-frontend.yml`'s advisory vitest (`continue-on-error: true`) should stay advisory. |
| P0-3 | **Put the journeys pack in CI.** | Either a `frontend-e2e-journeys` job in pr-check (needs Firebase emulators + Java setup — `e2e/run-e2e.mjs` already wraps `firebase emulators:exec`) or, if too slow for PRs, a scheduled workflow. Until then the E2E level in any future gate re-run should be marked PARTIAL, not MET. |

**P1 — close the process gaps (next 1–2 weeks):**

| # | Action | How |
|---|---|---|
| P1-4 | **Backfill automate, risk-based — not all 13.** | Run `/bmad-testarch-automate` (standalone brownfield mode) → `/bmad-testarch-test-review` per cluster, priority order: 8.20.x (cost caps, A6) → 8.21.x (grading moat, A5) → 8.19.x (sudo-admin auth surfaces, A2/A3) → 8.22.x/8.23.x (P1). This is the same MIN FLOW already proven on TEA-13..18. |
| P1-5 | **Run the NFR audit once.** | `bmad-testarch-nfr` against the armed dial — reliability (fallback chain + circuit breaker in `backend/core/model_runtime.py`) and security (prompt-injection / answer-leak) first. Persist `nfr-assessment.md` where the spec expects it. If reviews are meant to skip NFR, flip `nfr: false` so the dial tells the truth. |
| P1-6 | **Close the enforcement seam.** ✅ **DONE 2026-07-09** | Shipped same day as this audit (Daniel-approved): `sudo-dev-story-tests` Step 4 now requires persisted automate evidence + a 4th mandatory close-out checkbox; `sudo-code-review` gained gate check 5 (missing evidence → verdict capped at CONCERNS, `tea-*`/MIN-FLOW exempt, pre-2026-07-09 stories grandfathered); same fix in both `_AP` autopilot variants. Propagated via `/sync-agents`, verified hash-identical across lobby + AGY + Fresh + global caches. Session: `_artifacts/_main/2026-07-09_automate-evidence-gate/`. |
| P1-7 | **Housekeeping.** | Fix the circular import (`backend.routers.hr ↔ backend.main`) and un-skip `test_study_context_v2.py:202`; delete or relocate the 4 legacy `backend/test_*.py` strays; rename `diag_*.py` if they're keepers; delete the three stale "every test is skipped" docstrings. |

**P2 — the BDD/TDAD rollout (as capacity allows):**

| # | Action | How |
|---|---|---|
| P2-8 | **BDD pilot story** (§5.3-2) | Next Epic 8/9 story through the full Vision-Lock loop; confirm `.feature` collection in pr-check with zero config change. |
| P2-9 | **Fresh_Workspace bootstrap checklist** ✅ **DONE 2026-07-09** (core) | Shipped in the `fresh-template-bootstrap` session: `sudo-tests.yaml` ARMED (ratchet-from-zero floors), `pr-check.yml` gating PRs to **main + main_debug** (P0-1 lesson baked in), AGY guard layer hand-vendored (`_bmad/custom/` tomls + resolver scripts + `000-PLAN-FIRST-GATE` rule — `/sync-agents` excludes `_bmad/`), first `.feature` + self-binding steps green (1 passed), TDAD dialect tomls in. REMAINING (minor): TEA `{{USER_NAME}}`-style config placeholders / v6.2.2→6.9 core alignment. Session: `_artifacts/Fresh_Workspace_BMAD/2026-07-09_fresh-template-bootstrap/`. |
| P2-10 | **Nightly decision, made deliberately** | Either codify "nightly is local by design (B5)" in `testing-standards.md`, or add `nightly-evals.yml` (needs `GEMINI_API_KEY` secret + eval fixtures). Current state is fine but undocumented as a decision. |
| P2-11 | **De-stale the docs** | Update `tea_testing_guide.md` header (7/03 PASS supersedes CONCERNS; `l1_coverage_min` 0.54), fix the mislabeled `_artifacts/Fresh_Workspace_BMAD/active-context.md`, extend ROOT-LAW §4 to cover the Glob blind spot (§1). |

---

## 7. Appendix — evidence index

| Claim | Evidence |
|---|---|
| Gate dial current values | `Projects/AGY_AVIATIONCHAT/_bmad-output/sudo-tests.yaml` (read 2026-07-09) |
| pr-check trigger + commands | `.github/workflows/pr-check.yml` lines 7–16 (branches: [main]), line 57 (pytest + cov-fail-under=54) |
| Backend deploy has no tests | `.github/workflows/deploy-backend.yml` (jobs: deploy only) |
| pytest collection rules | `pyproject.toml [tool.pytest.ini_options]` — `testpaths=["backend/tests"]`, `norecursedirs=["manual","evals","integration_temp0","__pycache__"]` |
| Journeys excluded from CI | `frontend/playwright.config.ts` `testIgnore: ['**/journeys/**']`; `run-e2e.mjs` referenced by no workflow |
| Automate is Step 4 of step ② | `.agents/commands/sudo-dev-story-tests.md` lines 75–77; `_AP` variant implement-mode Step 3 |
| Gate is opt-in / WAIVED-if-absent | `.agents/commands/sudo-code-review.md` Step 2 |
| 14 ATDD checklists / 7 automate summaries | `_bmad-output/test-artifacts/atdd-checklist-*`, `automation-summary*` |
| All 14 verdicts exist (6 PASS / 8 CONCERNS) | `_bmad-output/implementation-artifacts/sudo-code-review-8.*.md` (grep census 2026-07-09) |
| Gate chronology FAIL→CONCERNS→PASS | `test-artifacts/traceability/gate-decision-{2026-07-02,2026-07-03}.json`, stale `gate-decision.json` (05-29) |
| One hard skip | `backend/tests/services/test_study_context_v2.py:202` |
| BDD zero-state + pinned dep | no `.feature`/`pytest_bdd` hits repo-wide; `backend/requirements.txt:54` |
| Fresh_Workspace empty state | `backend/tests/` = INDEX + `__init__.py`; no `.github/workflows`; `_bmad/bmm/stories/` empty; no `sudo-tests.yaml` |
| TEA-N MIN FLOW doctrine | `sprint-status.yaml` line 62; `_my_resources/open_tasks/tea_testing_guide.md` §0 |

*Compiled from three parallel ground-truth sweeps + direct file verification, 2026-07-09. Filesystem mtimes in `_bmad-output` are unreliable (bulk-touched 2026-07-08); all dates above are content dates.*
