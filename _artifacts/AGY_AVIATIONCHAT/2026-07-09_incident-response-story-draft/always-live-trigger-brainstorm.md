---
IsArtifact: true
ArtifactMetadata:
  title: "Always-Live Incident Agent — trigger architecture brainstorm"
  type: implementation_plan
  date: 2026-07-09
---

# Always-Live Incident Agent — how to make it fire without your PC

> Daniel's correction (memo, 2026-07-09): NOT a `/` command. A dedicated agent, always live,
> triggered by the Sentry report (front OR back end), independent of the desktop being on.
> Delivery: an email/notification carrying a FULL report + solution → Daniel opens mobile
> Claude Code on his phone → accepts → fix lands.

## The invariant pipeline (same in every option)

```
  frontend crash ──► Sentry (16.3 adds this)  ┐
  backend crash ───► Sentry (live today) ─────┤
                                              ▼
                                   [ TRIGGER  — the decision ]
                                              ▼
                              headless Claude triage agent
                    (Sentry issue → logs → code path → build history)
                                              ▼
                     incident report + proposed fix (± fix pre-built)
                                              ▼
                 notification: email / GitHub push / SMS  ──► Daniel's phone
                                              ▼
                mobile Claude Code (or GitHub mobile) → ACCEPT → fix PR → merge
```

Sentry is the single funnel for both ends — that's why 16.3 (frontend Sentry) is a hard
prerequisite for "the site crashed" coverage, not an optional extra. Front and back end each get a
Sentry project + alert rule pointing at the SAME trigger.

---

## Option A — GitHub Actions pipeline (recommended backbone)

**Trigger:** two phases, same workflow file.
- *Phase 1 (zero new infra):* `schedule:` cron every 10–15 min → poll Sentry API for new unresolved
  error/fatal issues since the last run marker. Latency ≤ ~15 min after the alert email.
- *Phase 2 (instant):* Sentry alert-rule webhook → **tiny relay** (a ~50-line GCP Cloud Function:
  verify Sentry signature → call GitHub `repository_dispatch` with the issue id) → workflow fires
  in seconds. (Needed because Sentry webhooks can't attach the GitHub auth header themselves.)

**Runner:** `anthropics/claude-code-action` in agent mode with a custom `prompt` — verified to
support `schedule` + `repository_dispatch` triggers and headless MCP config.

**Auth/billing:** requires `ANTHROPIC_API_KEY` as a repo secret (Console/API billing per incident,
ballpark $0.5–3 per triage). Subscription OAuth tokens are reportedly **not permitted in CI**
(flagged: source was secondary — verify at setup).

**Data access — A's unique advantage:** this repo **already has Workload Identity Federation to
GCP** for deploys (`deploy-backend.yml`). Add `roles/logging.viewer` to that identity and the
triage agent gets Cloud Run logs **securely, with infrastructure you already trust** — no
service-account keys anywhere. Sentry via `SENTRY_AUTH_TOKEN` secret. Repo checked out = full code
+ `_artifacts/` build history available.

**Output/delivery:** report committed to a `claude/incident-<id>` branch + a **GitHub Issue with
the full report as the body** → GitHub emails you AND pushes to the GitHub mobile app instantly.
Optional: also send direct email via the Epic-13 Workspace SMTP, and/or Twilio SMS for fatals.

**Accept from phone:** two depths (see "How deep" below) — either open mobile Claude Code →
"implement the fix plan from issue #N" (the existing mobile-mode lane: agent works on its own
`claude/*` branch, PR to `main_debug`, you tap-approve), or, at full depth, the fix PR already
exists and acceptance = review + merge in the GitHub mobile app.

**Ops profile:** zero idle cost, zero servers you babysit, GA product (not beta). Cron phase can
ship this week; relay phase is one small approved-plan session.

## Option B — Claude Code Routines (first-party "hook", newest)

Every routine gets a **dedicated HTTPS fire endpoint** (`POST …/routines/{id}/fire` + bearer
token, `text` = the alert payload) → a cloud-hosted Claude Code session spins up with repo access
and runs the runbook. Returns a **session URL** — and that's the killer UX: the notification link
opens the LIVE session on your phone; you're not reading a dead report, you're standing inside the
agent that did the work, and "accept" is just telling it to proceed.

**Caveats (why it's not the backbone yet):**
- Research preview behind a beta header — breaking changes possible.
- Sentry webhooks can't set a bearer header → still likely needs the same tiny relay.
- The Anthropic sandbox has **no GCP identity** → the Cloud-Logging leg degrades (Sentry token via
  env works; `gcloud` does not) unless we mint credentials for it — which WIF-on-Actions does
  more safely today.
- Billing/auth details in preview.

**Verdict:** pilot it as the *interactive acceptance surface* riding on top of A, or adopt it fully
once it matures — the architecture (Sentry → relay → trigger → agent) is identical either way, so
switching later costs almost nothing.

## Option C — Agent SDK service on Cloud Run (own everything)

A small FastAPI + `claude-agent-sdk` container (same stack as the app), scale-to-zero on Cloud Run.
Sentry webhook wakes it directly (no relay — it IS the relay), it triages with **native GCP
access** (logging viewer + read-only Firestore via its service account), emails the full report
through the Epic-13 Workspace mail, opens the GitHub issue/branch via PAT.

- **Pros:** best data access, native email, no third-party runner, instant, full control.
- **Cons:** most code to build and OWN (webhook signature verification, secrets, updates, the
  agent loop itself); a new production service in your GCP project; API-key billing.

**Verdict:** the right *eventual* home if the incident agent becomes a product-grade subsystem;
overkill as the first move.

---

## How deep before "accept"? (applies to every option)

- **Level 1 — triage + fix plan** (report ends with an implementation-plan-shaped fix). Accept =
  open mobile Claude Code, say go; the fix is implemented under your eyes in the mobile lane.
  Cheaper per incident; wrong-root-cause costs a report, not a build.
- **Level 2 — triage + fix built + tests run + PR open.** The email literally contains the
  solution; accept = merge. Constitution-safe (agent writes only to its own `claude/incident-*`
  branch; merging into `main_debug` stays your button). Costs more tokens per incident and a wrong
  hypothesis wastes a build.

**Recommendation:** same pipeline, prompt flag decides. Start Level 1 for the first few incidents
(calibrate trust via the drill), then flip to Level 2. Daniel's memo ("emailed a solution… accept
it") is Level 2 as the target state.

## Notification menu (stackable)

1. **GitHub Issue** (report = issue body) → GitHub email + mobile-app push. Free, instant, zero
   new secrets. **Baseline.**
2. **Direct email** with the full report from `team@aviationchat.org` (Epic-13 Workspace SMTP,
   already live) → matches "I want to be emailed a solution" verbatim. One SMTP secret in CI.
3. **Twilio SMS/WhatsApp** for fatal-severity only (Twilio account already connected at claude.ai;
   headless leg = Twilio REST + secret). The wake-you-up tier.
4. *(Option B only)* the Routine **session URL** — tap → you're in the live agent session.

## Revised epic slice (Epic 16 — approved "yes" by memo)

| Story | What | Status of decision |
|---|---|---|
| 16.1 | The **triage brain**: runbook prompt + report template + forced-failure drill (the part every option shares; manually invocable for testing only — not the product) | shape agreed, de-emphasize `/` command |
| 16.2 | The **always-live trigger + delivery**: chosen option (A/B/C), relay if needed, notifications, mobile-acceptance lane | ⬅ THE decision |
| 16.3 | **Frontend Sentry**: `@sentry/nextjs` + ErrorBoundary capture + FE Sentry project + alert rule into the same funnel | CONFIRMED in scope (memo: "for sure") |
| 16.4 | (optional) Notification hardening: severity tiers, SMS, Level-2 flip | later |

## Recommendation (one line — superseded by the decision below)

**A as the backbone now** (cron first, relay upgrade after) + **Level 1→2 progression** +
**GitHub-issue + direct-email notifications**, with **B (Routines) piloted as the phone-side
acceptance surface** once the backbone proves itself — and **16.3 is non-negotiable** or the "site
crashed" half of the mission never fires the pipeline at all.

---

## ✅ DECISION — Daniel, 2026-07-09 (chip answers)

1. **Webhook from day one — no cron phase.** "We are not going to come back and upgrade this
   later, so why wait?"
2. **Option B (Claude Code Routines) is the PRIMARY runtime.** "I trust the beta… if it doesn't
   work we can roll it back to something more proven." → Option A (GitHub Actions) is built as the
   **dormant rollback lane**; the relay's `TARGET` switch is the whole migration (one env flip).
3. **Level 2 from day one.** Every incident arrives with the fix already built + tests run + PR
   open; accepting = merge. "No reason to wait — we are not trying to keep rebuilding something."
4. **Notifications: GitHub issue only** (email + mobile-app push). No SMTP leg, no SMS.
5. **Build-history (`_artifacts`) lookup is CONDITIONAL** — only when the agent is struggling to
   understand what broke, "it has the resources to go look at the way we built it" — not on every
   incident.

Design consequence worth naming: the Routines sandbox has no GCP identity, so the **relay
(GCP-native Cloud Function) pre-fetches the ±15-min Cloud Run log excerpt** and ships it in the
fire payload — the primary lane keeps its logs leg without handing credentials to the beta.
