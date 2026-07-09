# Sentry Error-Response Team — visual overview & quick reference

> **What this is:** AviationChat's automated incident-response system (Epic 16). When production
> breaks — frontend or backend — a cloud Claude agent investigates, **builds the fix**, opens the
> PR, and the full report lands on Daniel's phone. Accepting the fix = tapping merge. Desktop off
> the whole time.
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

    WORK["THE AGENT'S WORK — Level 2<br/>investigate root cause<br/>branch from main @ live release SHA<br/>build the fix + run test suite<br/>open PR to main"]

    WORK --> ISSUE["GitHub Issue = full report<br/>+ PR link + live session URL"]
    ISSUE --> PHONE["Daniel's phone<br/>email + GitHub app push"]
    PHONE --> DECIDE{"Daniel decides"}
    DECIDE -- "accept" --> MERGE["Tap MERGE on the PR<br/>fix goes LIVE on main"]
    DECIDE -- "interrogate first" --> CHAT["Tap session URL<br/>talk to the agent live"] --> DECIDE
    DECIDE -- "reject" --> CLOSE["Close PR / tell agent to redo"]

    style SENTRY fill:#7b2d8e,color:#fff
    style RELAY fill:#1a73e8,color:#fff
    style ROUTINE fill:#d97706,color:#fff
    style GHA fill:#374151,color:#fff
    style WORK fill:#065f46,color:#fff
    style MERGE fill:#166534,color:#fff
```

**The agent can NEVER merge.** The merge button is Daniel's, always.

---

## 2. One incident, step by step (the phone experience)

```mermaid
sequenceDiagram
    autonumber
    participant App as AviationChat (live, main)
    participant Sen as Sentry
    participant Rel as Relay (GCP Fn)
    participant Agent as Claude agent (cloud)
    participant GH as GitHub
    participant Dan as Daniel's phone

    App->>Sen: crash event (stack trace + release SHA)
    Sen->>Dan: alert email (existing 11.5 chain — the wake-up)
    Sen->>Rel: webhook fires
    Rel->>Rel: verify signature · dedupe · fetch ±15min logs
    Rel->>Agent: fire with issue id + log excerpt
    Agent->>Agent: triage runbook — Sentry issue, logs,<br/>code path, build history IF struggling
    Agent->>GH: branch claude/incident-XXX from main @ live SHA
    Agent->>Agent: build fix + run full test suite
    Agent->>GH: open PR to main (report + real test output as body)
    Agent->>GH: open Issue "incident" = full report + PR + session URL
    GH->>Dan: email + app push
    Dan->>Agent: (optional) tap session URL, ask questions
    Dan->>GH: tap MERGE = acceptance → fix is live
    Dan->>GH: back-merge main → main_debug (footer command)
```

---

## 3. Branch model — where the fix flows

```mermaid
flowchart LR
    MAIN["main<br/>LIVE PRODUCTION<br/>= what Sentry monitors"]
    DEBUG["main_debug<br/>the build/dev lane"]
    INC["claude/incident-XXX<br/>agent's own branch<br/>cut from main @ crash SHA"]

    MAIN -- "crash comes from here" --> INC
    INC -- "PR (agent opens, never merges)" --> MAIN
    MAIN -- "back-merge the hotfix<br/>(so next promotion keeps it)" --> DEBUG
    DEBUG -- "normal promotion<br/>(Daniel's manual decision, unchanged)" --> MAIN

    style MAIN fill:#991b1b,color:#fff
    style DEBUG fill:#1e40af,color:#fff
    style INC fill:#065f46,color:#fff
```

⚠️ **Deliberate carve-out (Daniel, 2026-07-09):** the standing "never PR to main" rule is amended
for THIS lane only — incident fixes target `main` because that's the live branch that crashed.
The merge stays Daniel's per-action button, so the spirit of the rule is unchanged.

---

## 4. The build plan — Epic 16 story map

```mermaid
flowchart TD
    S1["16.1 — Triage Runbook (ready-for-dev)<br/>the BRAIN: .github/claude/incident-triage.md<br/>5 steps + report template + local drill"]
    S2["16.2 — Always-Live Pipeline (backlog)<br/>relay + Routine + Level-2 fix PR<br/>+ dormant rollback lane + phone drill"]
    S3["16.3 — Frontend Sentry (backlog)<br/>@sentry/nextjs + ErrorBoundary<br/>browser crashes join the funnel"]
    S4["16.4 — candidates (later)<br/>auto back-merge · severity tiers ·<br/>SMS · Routines GA migration"]

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
| Delivery | GitHub Issue `incident` + PR to `main` | Report + push + email to phone |
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

- Agent **never merges**; can't push to `main` or `main_debug` — only its own `claude/incident-*` branch.
- Dedupe by Sentry short-id — one issue, one triage, ever.
- Real test output pasted in every PR; no secrets or PII in any report (user ids arrive pre-hashed).
- Rollback lane is **drilled**, not hoped for; Sentry's plain alert email keeps firing regardless.

### Decision log (Daniel, 2026-07-09)

| Decision | Call |
|---|---|
| Trigger | Webhook from day one — no polling phase |
| Runtime | **Routines beta = primary** ("I trust the beta"); GH Actions built as drilled rollback |
| Fix depth | **Level 2 from day one** — fix pre-built, tests run, PR open; accept = merge |
| Notification | GitHub issue only (email + app push) |
| Build-history lookup | Conditional — only when the agent is struggling |
| Branch | **Monitors + fixes `main`** (live); `main_debug` stays the build lane; back-merge flagged per PR |
