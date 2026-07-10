# Sentry Error-Response Team — visual overview & quick reference

> **What this is:** AviationChat's automated incident-response system (Epic 16). When production
> breaks — frontend or backend — a cloud Claude agent investigates, **builds the fix on its own
> hotfix branch**, and the full report lands on Daniel's phone. Accepting the fix = the standard
> hotfix flow: **pull the branch, test it locally, merge it into `main`, then rebase `main_debug`
> onto the released hotfix**. The investigation + build run with Daniel's desktop off; only the
> final test-merge-rebase is hands-on. `main_debug` (open, untested work) is **rebased, never
> merged into** — its unfinished work simply replays on top of the shipped fix.
>
> Designed + approved 2026-07-09. Stories: `Projects/AGY_AVIATIONCHAT/_bmad/bmm/stories/story-16-*.md` ·
> Decision record: `_artifacts/AGY_AVIATIONCHAT/2026-07-09_incident-response-story-draft/always-live-trigger-brainstorm.md`

---

## 1. The big picture — crash to merged fix

```mermaid
flowchart TD
    FE["Frontend crash<br/>(browser — wired by 16.3)"] --> SENTRY
    BE["Backend crash<br/>(Cloud Run — live today)"] --> SENTRY
    SENTRY["Sentry<br/>org: aviationchat<br/>alert rule fires webhook"] --> RELAY

    RELAY{"RELAY<br/>GCP Cloud Function<br/>1 verify Sentry signature<br/>2 dedupe by incident id<br/>3 pre-fetch Cloud Run logs<br/>4 route by TARGET switch"}

    RELAY -- "TARGET = routines<br/>(PRIMARY)" --> ROUTINE["Claude Code ROUTINE<br/>cloud session, beta<br/>runs the triage runbook"]
    RELAY -- "TARGET = github<br/>(ROLLBACK, dormant)" --> GHA["GitHub Actions<br/>claude-code-action<br/>same runbook, proven GA"]

    ROUTINE --> WORK
    GHA --> WORK

    WORK["THE AGENT'S WORK — Level 2<br/>investigate root cause<br/>branch from main @ live release SHA<br/>build the fix + run test suite<br/>push branch claude/incident-XXX (NO PR)"]

    WORK --> ISSUE["GitHub Issue = full report<br/>+ branch name + live session URL"]
    ISSUE --> PHONE["Daniel's phone<br/>email + GitHub app push"]
    PHONE --> DECIDE{"Daniel decides"}
    DECIDE -- "accept" --> LOCAL["Pull branch locally · test the fix<br/>merge branch → main (goes LIVE)<br/>rebase main_debug onto main"]
    DECIDE -- "interrogate first" --> CHAT["Tap session URL<br/>talk to the agent live"] --> DECIDE
    DECIDE -- "reject" --> CLOSE["Delete branch / tell agent to redo"]

    style SENTRY fill:#7b2d8e,color:#fff
    style RELAY fill:#1a73e8,color:#fff
    style ROUTINE fill:#d97706,color:#fff
    style GHA fill:#374151,color:#fff
    style WORK fill:#065f46,color:#fff
    style LOCAL fill:#166534,color:#fff
```

**The agent can NEVER push to `main`.** It only ever writes its own `claude/incident-*` branch;
going live is Daniel's deliberate local test → merge-to-`main` → rebase-`main_debug`, always.

---

## 2. One incident, step by step (the phone experience)

```mermaid
flowchart TD
    A["1 · AviationChat (live, main) throws a crash<br/>event carries stack trace + release SHA"]
    B["2 · Sentry receives it<br/>fires the 11.5 alert email (the wake-up) AND the webhook"]
    C["3 · Relay (GCP Fn)<br/>verify signature · dedupe · fetch ±15min logs"]
    D["4 · Relay fires the agent<br/>with issue id + log excerpt"]
    E["5 · Agent runs the triage runbook<br/>Sentry issue · logs · code path · build history IF struggling"]
    F["6 · Agent branches claude/incident-XXX from main @ live SHA<br/>builds fix · runs full test suite"]
    G["7 · Agent pushes the branch (NO PR)<br/>+ opens Issue 'incident' = full report + branch + session URL"]
    H["8 · Report lands on Daniel's phone<br/>email + app push"]
    I["9 · (optional) tap session URL — interrogate the agent live"]
    J["10 · Daniel pulls the branch locally<br/>tests the fix actually works"]
    K["11 · Daniel merges the branch into main → fix is live"]
    L["12 · Daniel rebases main_debug onto main<br/>open work replays on top of the hotfix"]

    A --> B --> C --> D --> E --> F --> G --> H --> I --> J --> K --> L

    style A fill:#7b2d8e,color:#fff
    style C fill:#1a73e8,color:#fff
    style F fill:#065f46,color:#fff
    style K fill:#166534,color:#fff
```

The incident lane **never merges into `main_debug`** — after the fix merges to `main`,
`main_debug` is *rebased* onto `main`, so its open untested work simply replays on top of the
shipped hotfix (the standard hotfix-branch sync, minus the textbook merge-into-dev).

---

## 3. Branch model — where the fix flows

```mermaid
flowchart LR
    MAIN["main<br/>LIVE PRODUCTION<br/>= what Sentry monitors"]
    DEBUG["main_debug<br/>open + untested work<br/>NEVER MERGED INTO"]
    INC["claude/incident-XXX<br/>agent's own hotfix branch<br/>cut from main @ crash SHA"]

    MAIN -- "crash comes from here" --> INC
    INC -- "agent pushes the branch (never PRs, never merges)" --> INC
    INC -- "Daniel tests locally, then merges to main" --> MAIN
    MAIN -- "Daniel rebases main_debug onto main<br/>(open work replays on top of the hotfix)" --> DEBUG

    style MAIN fill:#991b1b,color:#fff
    style DEBUG fill:#1e40af,color:#fff
    style INC fill:#065f46,color:#fff
```

✅ **The flow (Daniel, 2026-07-09) — standard hotfix pattern:** a **new hotfix branch** fixes the
problem → Daniel tests it → **merges it to `main`** (live) → **rebases `main_debug` onto `main`**.
`main_debug` (open, untested work) is only ever *rebased* — the hotfix is never merged *into* it,
so its unfinished work stays isolated and simply replays on top of the shipped fix. The agent only
ever writes its own `claude/incident-*` branch — it never PRs and never pushes to `main`, so the
standing "never PR to main" rule needs **no carve-out**; it holds as written. (Rebase assumes
`main_debug` is Daniel's to rewrite — force-push after, standard for a private integration branch.)

---

## 4. The build plan — Epic 16 story map

```mermaid
flowchart TD
    S1["16.1 — Triage Runbook (ready-for-dev)<br/>the BRAIN: .github/claude/incident-triage.md<br/>5 steps + report template + local drill"]
    S2["16.2 — Always-Live Pipeline (backlog)<br/>relay + Routine + Level-2 fix PR<br/>+ dormant rollback lane + phone drill"]
    S3["16.3 — Frontend Sentry (backlog)<br/>@sentry/nextjs + ErrorBoundary<br/>browser crashes join the funnel"]
    S4["16.4 — candidates (later)<br/>branch auto-cleanup · severity tiers ·<br/>SMS · Routines GA migration"]

    S1 --> S2 --> S4
    S1 -.parallel ok.-> S3
    S3 -.one alert rule plugs in.-> S2
```

**Dev order:** 16.1 → 16.2, with 16.3 in parallel any time. Epic close-out live-QA = forced FE +
BE crashes → two full reports on the phone.

---

## 5. Quick reference

### Components & where they live

| Piece | Home | Job |
|---|---|---|
| Triage runbook | `.github/claude/incident-triage.md` (16.1) | The 5-step brain both lanes execute |
| Relay | GCP Cloud Function, project `aviationchat` (16.2) | Verify → dedupe → fetch logs → route |
| Primary lane | Claude Code **Routine** (beta) | Cloud agent session; live session URL bonus |
| Rollback lane | `.github/workflows/incident-response.yml` (dormant) | Proven GA path, same runbook |
| Delivery | GitHub Issue `incident` + ready `claude/incident-*` branch | Report + push + email to phone |
| Drill harness | `/sudo-incident-response` command | Testing only — NOT the product |

### Switches & secrets (names only — values never in repo)

| Name | Where | Does |
|---|---|---|
| `TARGET` = `routines` \| `github` | relay env | **The rollback**: one flip migrates lanes |
| `INCIDENTS_PAUSED` | relay env | Kill switch for alert storms |
| `SENTRY_AUTH_TOKEN` | secret | Headless Sentry reads + FE source maps |
| `ANTHROPIC_API_KEY` | GH secret | Fallback-lane billing (subscription tokens don't work in CI) |
| Routine bearer + Sentry webhook secret | relay secrets | Trigger auth |

### Guardrails (non-negotiable)

- Agent **never PRs and never pushes to `main` or `main_debug`** — it writes only its own `claude/incident-*` branch. Going live is Daniel's local test → merge to `main` → rebase `main_debug`.
- Dedupe by Sentry short-id — one issue, one triage, ever.
- Real test output pasted in every PR; no secrets or PII in any report (user ids arrive pre-hashed).
- Rollback lane is **drilled**, not hoped for; Sentry's plain alert email keeps firing regardless.

### Decision log (Daniel, 2026-07-09)

| Decision | Call |
|---|---|
| Trigger | Webhook from day one — no polling phase |
| Runtime | **Routines beta = primary** ("I trust the beta"); GH Actions built as drilled rollback |
| Fix depth | **Level 2 from day one** — fix pre-built + tests run on a hotfix branch; accept = pull it, test, merge to `main`, then rebase `main_debug` onto it |
| Notification | GitHub issue only (email + app push) |
| Build-history lookup | Conditional — only when the agent is struggling |
| Branch | **New `claude/incident-*` hotfix branch fixes `main`** (live) → Daniel tests → merges to `main` → **rebases `main_debug` onto `main`**; `main_debug` (open untested work) is *rebased, never merged into* — no PR, no back-merge |
