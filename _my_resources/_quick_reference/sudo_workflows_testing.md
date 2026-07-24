# The Sudo Dev System — Quick Reference

> One page: how we build, the commands you type, and how we test. Updated **2026-07-24** (added
> `/autopilot-claude`, `/sudo-park`, `/sudo-resume`, `/sudo-close-workingtree`, `/sudo-mobile-error-team`, and `/clean-code-audit`).

> Deep material lives in [tea_deep_reference.md](tea_deep_reference.md) — go there for full call-graphs, the method
> curriculum, and the TEA fragment library.

---

## 1. The map — how everything connects

```mermaid
flowchart TD
    BOOT["/sudo-boot-sprint-memory\nsession boot — where am I, what is next"] --> KICK["/bmad-create-epics-and-stories\nONCE per epic: epic + stories + sprint board\n+ interactive P0-P3 risk scoring"]
    KICK --> ONE["① /sudo-write-story-tests\nstory file + BDD Vision Lock\n+ RED acceptance tests"]
    ONE --> TWO["② /sudo-dev-story-tests\nplan → STOP self-audit gate\n→ implement → expand coverage"]
    TWO --> THREE["③ /sudo-code-review\nadversarial review + TEST GATE\nPASS / CONCERNS / FAIL / WAIVED"]
    THREE -.->|"Step 3.5"| CLEAN["/clean-code-audit\nmachine floor + taste audit"]
    THREE --> CLOSE["/sudo-update-sprint-memory\nclose-out — YOUR sign-off flips story to done\n+ lands on main_debug"]
    CLOSE --> CLOSEWT["/sudo-close-workingtree\nStep 8: verify merge, prune worktree,\npurge folder, delete branches"]
    CLOSEWT -.->|"next story"| ONE
    CLOSEWT --> SHIP["/sudo-push-e2e\nrun /sudo-e2e → green → promote to main"]
    SHIP --> PROD["Production\nCloud Run backend + App Hosting frontend"]
    PROD -.->|"errors"| SEC["Security / Error team\nSentry → GitHub Action triage\n→ issue + fix branch → Telegram page"]
    SEC -.->|"live incident response"| MOBERR["/sudo-mobile-error-team\nphone/desktop responder: re-diagnose\n→ rollback/fix card → CI gate → close loop"]
    MOBERR -.->|"feeds a bug/story"| ONE
    SEC -.->|"feeds a bug/story"| ONE
    LIVE["/sudo-live-testing-team\nyou fly the app, agent watches logs\n→ researched bug docs"] -.->|"feeds a bug/story"| ONE
    AP["/autopilot-claude / /autopilot_claude\nrobot runs 4-stage story loop for you"] -.->|"alternate lane for ①②③"| TWO
    PARK["/sudo-park\npark worktree branches to origin"] <--> RESUME["/sudo-resume\nrestore surface on new machine"]
```

---

## 2. The development style in 60 seconds

**Test-first, human-gated, story-driven.** Every piece of work is a BMAD **story**. A story starts
with **failing acceptance tests** (the contract), code exists only to turn them green, and an
**adversarial review + test gate** stands between "coded" and "done". You are the only one who can
flip a story to `done` — agents flip to `review`, close-out is your sign-off.

Three lanes run or manage the work:
- **Manual lane** — you type the ①②③ commands and steer each gate.
- **Autopilot lane** — `/autopilot-claude` (`/autopilot_claude`) runs the same stages headlessly (Dev plans/implements, QA audits on Opus then reviews/fixes on Fable) and stops at `review` for you.
- **Machine handoff lane** — `/sudo-park` and `/sudo-resume` make work portable across desktop, laptop, and mobile without touching `main_debug`.

Bugs found outside the loop (live testing, production Sentry errors) are turned into **researched
bug docs** first or handled via `/sudo-mobile-error-team`, then enter the story loop. Nothing ships to `main` without the **e2e gate**.

---

## 3. Your `/` commands (the human lane)

### The story loop (daily drivers)
| Command | What it does |
|---|---|
| `/sudo-boot-sprint-memory` | Session boot — reads sprint + context, tells you the next story and which command to run. |
| `/bmad-create-epics-and-stories` | **Once per epic**: writes the epic + stories, builds the sprint board, then risk-scores every story P0–P3 with you. |
| ① `/sudo-write-story-tests` | Creates the next story + locks behaviors (BDD Vision Lock) + writes the RED acceptance tests. |
| ② `/sudo-dev-story-tests` | Plans, **stops at the self-audit gate** (you pick: run here / other model / fresh team), implements to green, expands coverage. |
| ③ `/sudo-code-review` | Adversarial code review, clean-code audit (Step 3.5), then test gate (suite + trace + NFR + test-review) → verdict. |
| `/clean-code-audit` | Standalone or Step 3.5 of ③: audits diff vs `code-standards.md` (ruff/eslint/pyrefly/tsc floor + comment contract/AI-drift pass). |
| `/sudo-update-sprint-memory` | Close-out: flips story to `done` (your sign-off — only red tests block), saves learnings, prunes context, lands on `main_debug`, and auto-invokes `/sudo-close-workingtree` (Step 8). |
| `/sudo-close-workingtree` | Verifies story branch is merged to `origin/main_debug`, removes local worktree, and deletes local & remote GitHub `claude/*` branches. |

| `/sudo-bdd-tests` | Standalone BDD Vision Lock session (① runs it for you; use solo to re-lock behaviors). |
| `/sudo-self-audit` | Standalone pre-dev plan audit (② runs it for you; use solo to pressure-test any plan). |
| `/sudo-quick-dev` | Fast lane for small fixes — story + direct dev + light sanity audit. Skips the heavy gates. |

### Machine handoff & portability (switching boxes)
| Command | What it does |
|---|---|
| `/sudo-park` | Park before switching machines — commits & pushes every active story worktree branch and main checkouts (lobby + project) to origin, writes resume card to `active-context.md`. Never pushes story work onto `main_debug`. |
| `/sudo-resume` | Resume sprint on new machine — fetches origin, restores/tracks story branches (`git worktree add --track` on desktop, checkout on mobile), reads handoff card, hands off to `/sudo-boot-sprint-memory`. |

### Shipping
| Command | What it does |
|---|---|
| `/sudo-e2e` | Runs the real end-to-end suite (emulator-backed, seeded users). Green = safe to promote. |
| `/sudo-push-e2e` | The one shipping command: push `main_debug` (path A), full merge → `main` (B), or cherry-pick features → `main` (C). **B and C refuse to run until `/sudo-e2e` is green.** Then Cloud Run deploy + live verify + ledger. |
| `/merge_main_debug` | Approve + squash-merge the active PR into `main_debug` (never `main`). |

### Debugging & incident response
| Command | What it does |
|---|---|
| `/sudo-live-testing-team` | Boots backend+frontend, watches backend logs while **you fly the app**, coaches you through DevTools checks, files researched bug docs that feed the story loop. Writes no code. |
| `/sudo-mobile-error-team` | Mobile/phone-first error team responder for live production incidents (Sentry P1 alert → GitHub issue → machine fix branch). Re-diagnoses, presents rollback vs fix-forward decision card, gates minimal fix on CI, closes loop (requires your approval). |

### Autopilot (robot lane launchers)
| Command | What it does |
|---|---|
| `/autopilot-claude` / `/autopilot_claude` | The 4-stage Dev/QA robot loop on the claude CLI (Plan → Audit on Opus → Implement → Review+Fix on Fable). |
| `/autopilot_mobile` | Same pipeline on the Workflow engine — works from Claude Code web/mobile interface. |
| `/autopilot_opencode` / `glm` / `deepseek` | Engine variants (opencode binary / GLM dev lane / DeepSeek). |

### Toolkit upkeep
| Command | What it does |
|---|---|
| `/update-maps-indexes` | Reconciles repo-maps, every INDEX.md, every AGENTS.md + README reference (dead paths, renamed commands, stale contents-lists), context hygiene, and the open-tasks list across the lobby + maintained projects. |
| `/sync-agents` | Pushes the master `.agents` toolkit to all 4 platforms (Claude, opencode, Antigravity, Codex) + the maintained projects (`-Maintained`). |
| `/slash_command_updating` | Thin alias: refresh just the machine-global command caches. |
| `/new-project` | Scaffold a new project workspace under `Projects/`. |
| `/webm-alpha-video` | Green-screen MP4 → transparent WebM utility. |

### Not in your menu (on purpose)
| Name | Why you don't see it |
|---|---|
| `sudo-*_AP` (three of them) | **Robot-only** — the autopilot engines invoke these inside each project. Never human-typed; excluded from the lobby menus and global caches. |
| `/security_team_aviationchat` | The **incident-drill harness** (was `sudo-incident-response`). Used to fire-drill the runbook. The *live human responder* is `/sudo-mobile-error-team`, and the *automated pipeline* is the GitHub Action (§9). |

---

## 4. The story loop, step by step

| # | Step | Command | Under the hood |
|---|------|---------|----------------|
| — | Orient | `/sudo-boot-sprint-memory` | reads active-context + sprint-status |
| 1 | Epic kickoff (once) | `/bmad-create-epics-and-stories` | create-epics → sprint-planning → `testarch-test-design` (interactive P0–P3, one story at a time) |
| 2 | Write RED tests | ① `/sudo-write-story-tests` | create-story → BDD Vision Lock (**mandatory** — contract or recorded waiver) → `testarch-atdd` |
| 3 | Plan + audit + build | ② `/sudo-dev-story-tests` | BDD gate → plan → **⛔ STOP: self-audit** (you choose the lane) → implement → `testarch-automate` |
| 4 | Review + gate | ③ `/sudo-code-review` | adversarial review → `/clean-code-audit` (Step 3.5) → full suites (pytest + vitest) → `testarch-trace` → `testarch-nfr` → `testarch-test-review` |
| 5 | Close out | `/sudo-update-sprint-memory` | reads ③'s verdict; flips `review` → `done`, lands on `main_debug`, auto-calls `/sudo-close-workingtree` (Step 8) |


**Status contract:** dev/orchestrator set `review`; only your close-out sets `done`.

### Clean code audit (Step 3.5 of ③ or standalone)
`/clean-code-audit` checks the diff against `.agents/rules/code-standards.md`:
- **Machine floor (objective — can FAIL)**: `ruff`, `eslint`, `pyrefly`, `tsc` on changed lines + bans (bare `except:`, `any` in TS, committed secrets, leftover debug prints).
- **Judgment pass (taste — caps at CONCERNS)**: comment contract (Story AC provenance, `AIDEV-NOTE` anchor hygiene) + AI-drift bans (single-caller abstractions, re-implementing existing helpers, scope creep).

### The test gate (heart of ③)
Opt-in per project and baseline-diff aware — legacy red is grandfathered; only **NEW** regressions fail:

```yaml
# _bmad-output/sudo-tests.yaml  (a project that turns the gate on)
required_tiers: [L1, L2, L3]   # which pyramid tiers must be present
l1_coverage_min: 85            # deterministic coverage floor
agent_bearing: true            # story touches agent behavior → L3 judge required
nfr: false                     # also run the NFR audit
waive: false                   # hard override (force WAIVED)
```

| Verdict | Means |
|---|---|
| **PASS** | all required tiers green |
| **CONCERNS** | soft issues only |
| **FAIL** | NEW regression OR a required tier missing |
| **WAIVED** | no baseline — gate off for this project |

---

## 5. Shipping — the e2e gate

**Branch model:** `main_debug` is where we build; `main` is live. `main` only ever receives from
`main_debug` and must **never end up ahead** of it.

| `/sudo-push-e2e` path | Ships | Gate |
|---|---|---|
| **A · debug** | push `main_debug` | pytest + frontend build |
| **B · main** | merge everything → `main` | A's gate **+ `/sudo-e2e` green** |
| **C · cherry** | picked commits → `main` | A's gate **+ `/sudo-e2e` green**, then back-merge `main` → `main_debug` (keeps the branch model true) |

`/sudo-e2e` is also a solo command — run it any time you want end-to-end confidence without shipping.

---

## 6. How we test — the method (the learning section)

### 6.1 Risk first: P0–P3 decides how much testing a story earns
**Risk = Probability × Impact.** Scored interactively at epic kickoff, one story at a time.

| Priority | Meaning | Example |
|---|---|---|
| **P0 — Critical** | business fails if broken | auth/tenancy walls, privacy defaults, payments |
| **P1 — High** | core workflow pain | grading events, admin role enforcement |
| **P2 — Medium** | workaround exists | pagination, overlays |
| **P3 — Low** | cosmetic | tooltips, hover states |

| Priority | Unit | Integration | E2E | Manual | Coverage target |
|---|:---:|:---:|:---:|:---:|:---:|
| **P0** | ✅ | ✅ | ✅ | ✅ | **100%** |
| **P1** | ✅ | ✅ | ✅ | — | **80%** |
| **P2** | — | ✅ | — | ✅ | **50%** |
| **P3** | — | — | — | ✅ | **20%** |

> The review question is always: *"what P-level is the decision this test pins?"* A PR with 0% P0
> and 100% P3 coverage is a red flag regardless of line count.

### 6.2 Test levels: what each layer catches
| Level | Covers | Speed | Example shape |
|---|---|---|---|
| **Unit** | one function/class, no external deps | ms | schema defaults |
| **Integration** | components together (DB/service mocked at the edge) | medium | writer + `mock_db` |
| **E2E** | the full running stack — real HTTP, real browser, emulator auth | slow | seeded learner logs in and completes a flow |

A P0 behavior is deliberately covered at **all three** levels. Testability order: isolated first
(schema), full-stack last (API/browser).

### 6.3 The L1–L4 pyramid (how we test *AI* code specifically)
Deterministic code gets real coverage; generative LLM output gets **soft assertions** — never
string-matching.

```mermaid
flowchart TD
    L1["L1 — Deterministic (LLM mocked)\nrouting · telemetry · SSE · plumbing\nreal coverage, floor from sudo-tests.yaml"] --> L2["L2 — Constrained LLM\ntemperature 0 · JSON-schema compliance"]
    L2 --> L3["L3 — LLM-as-judge\ngroundedness · rubric scoring\nzero-hallucination citations"]
    L3 --> L4["L4 — Human\nyou, at close-out and live testing"]
```

| Tier | Written in | Checked at |
|---|---|---|
| L1 deterministic | ① `atdd` + ② `automate` | ③ suite run |
| L2 constrained | ② `automate` | ③ gate |
| L3 judge | ①/② (agent-bearing stories) | ③ `trace` / `nfr` |
| L4 human | — | close-out + `/sudo-live-testing-team` |

### 6.4 ATDD · BDD · Automate — the three words, plainly
- **ATDD** (①): write the story's acceptance tests **before any code**, and prove they FAIL (red).
  Red-first is the point — a test that never failed proves nothing.
- **BDD Vision Lock** (inside ①): the *conversation* where we pin exact expected behaviors as
  Given/When/Then cases **inside the story's red test files** — so the contract is in the tests,
  not in a separate doc. (A standalone `.feature` file is opt-in only.)
- **Automate** (②, after green): expand coverage around the now-working code — edge cases,
  contracts, the tests ATDD didn't need yet.
- Retrofit caveat: tests added to *already-correct* code (test-debt stories) pass green-first as
  regression tripwires — don't fake a red.

### 6.5 What a good test is (the bar)
1. Deterministic — re-running to "clear" a flake is a bug, not a workaround
2. No hard sleeps — wait on conditions, never on time
3. Stateless + parallelizable — each test builds and tears down its own world
4. Self-cleaning — no manual DB resets
5. Low-maintenance — set state via APIs, not UI click-chains
6. Lives near its source — mirrored test tree
7. Mocks match the **production shape** — a mock value the backend never emits is a vacuous green

### 6.6 CI/CD — what runs where
| Gate | Where | When |
|---|---|---|
| PR check (pytest + vitest + bdd) | GitHub Actions | every PR to `main_debug` |
| TIA pre-push gate | local hook | pre-push test selection (falls back to full suite if the index is stale) |
| **E2E gate** | local, `/sudo-e2e` via `/sudo-push-e2e` | **before anything lands on `main`** |
| Deploy | App Hosting CI/CD (frontend) + Cloud Run (backend) | on push to `main` |
| Incident pipeline | GitHub Action | on Sentry error (production, after deploy) |

---

## 7. TEA BMAD tools — when to reach for each

`/tea` activates **Murat**, the Test Architect persona, for strategy consults. The workflows:

| Workflow | Fires | Job |
|---|---|---|
| `testarch-test-design` | epic kickoff (inside `/bmad-create-epics-and-stories`) | risk-score P0–P3 with you → test plan |
| `testarch-atdd` | ① | write the failing acceptance tests |
| `testarch-automate` | ② | expand coverage on working code |
| `testarch-trace` | ③ | requirements → tests matrix + coverage verdict |
| `testarch-nfr` | ③ (agent/NFR stories) | perf / security / reliability evidence audit |
| `testarch-test-review` | ③ | quality + flake audit of the tests themselves |
| `testarch-framework` | one-time | initialize a test bench (Playwright/Cypress/pytest) |
| `testarch-ci` | one-time | scaffold the CI quality pipeline |
| `bmad-teach-me-testing` | on demand | the TEA academy — structured learning sessions |

You rarely call these directly — the sudo commands call them in order. Reach for them solo when you
want just one piece (e.g. `/testarch-trace` to see coverage without a full review).

---

## 8. The autopilot lane (robot runs the loop)

Four stages, continuous chats, model-pinned (Dev chat + split QA gates on Opus and Fable for `/autopilot-claude`), same artifacts contract every time:

| Stage | Robot command | Produces |
|---|---|---|
| 1 Plan | `/sudo-dev-story-tests_AP plan` | `implementation_plan.md` |
| 2 Audit | `/sudo-self-audit_AP` (Opus) | `self-audit-stress-test.md` |
| 3 Implement | `/sudo-dev-story-tests_AP implement` | code + tests + `walkthrough.md` |
| 4 Review+Fix | `/sudo-code-review_AP` (Fable) | `code-review.md` + fixes |

Green regression-only gate → story flips to `review` (never `done` — that's still you). Resumable:
re-run and finished stages auto-detect. The engines live per-project in `scripts/`; the `_AP`
commands live only inside the projects where the robots run.

---

## 9. The security / error team (automated incident response)

Production incident workflow consists of three layers:

1. **Automated Incident Pipeline:** Sentry error → GitHub Action runs triage runbook (`.github/claude/incident-triage.md`) → GitHub issue (`incident:<id>`) + `claude/incident-<id>` fix branch → Telegram page with TL;DR + prompt.
2. **Live Human Responder (`/sudo-mobile-error-team`):** Run from phone or desktop to re-diagnose independently, present a rollback vs fix-forward decision card, write surgical hotfix + regression test, gate on real CI, and close the incident loop (requires your explicit sign-off).
3. **Fire-Drill Harness (`/security_team_aviationchat`):** Used to drill and test the runbook against sample issues to ensure the pipeline stays healthy.

Full picture + diagrams: [security/sentry_error_response_team.md](../security/sentry_error_response_team.md).

---

## 10. Where the depth lives

| Want | Go to |
|---|---|
| Full call-graphs, method curriculum, worked examples, 42 TEA fragments | [tea_deep_reference.md](tea_deep_reference.md) |
| Incident/security system in full | [security/sentry_error_response_team.md](../security/sentry_error_response_team.md) |
| Workspace layout + artifact rules | `docs/workspace-standard.md` |
| This system's front door | `AGENTS.md` (lobby root) |
