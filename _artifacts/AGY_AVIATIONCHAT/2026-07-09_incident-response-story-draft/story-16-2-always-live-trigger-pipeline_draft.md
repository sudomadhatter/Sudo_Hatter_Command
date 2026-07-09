---
IsArtifact: true
ArtifactMetadata:
  title: "16.2 — Always-Live Trigger & Delivery (Routines-first, rollback-ready)"
  type: story
  date: 2026-07-09
Status: draft
Epic: 16 — Automated Incident Response
Story: 16.2
created: 2026-07-09
depends_on: story 16.1 (the runbook it executes)
source: _artifacts/AGY_AVIATIONCHAT/2026-07-09_incident-response-story-draft/ (decision record: always-live-trigger-brainstorm.md §DECISION)
---

# Story 16.2: Always-Live Trigger & Delivery — Routines-first, rollback built in

> **THE story of the epic**, shaped by Daniel's decisions (2026-07-09): **webhook from day one**
> (no polling phase), **Claude Code Routines as the primary runtime** ("I trust the beta… if it
> doesn't work we can roll it back to something more proven"), the **GitHub Actions lane built
> dormant as that rollback** (one switch-flip away), **Level 2 from day one** (the fix arrives
> already built — accepting = merge), **GitHub issue as the sole notification**.

## Story

As **the engineering owner reachable only by phone when production breaks**,
I want **a Sentry alert to instantly fire a cloud Claude agent that investigates, builds the fix
on its own branch, and opens the PR — with the full report reaching my phone as a GitHub issue**,
so that **accepting a production fix is reading a report and tapping merge, with my desktop
powered off the whole time.**

## Architecture (agreed)

```
Sentry alert rule fires        (BE: python-fastapi · FE: the 16.3 project)
      │ webhook (Sentry can't attach auth headers itself)
      ▼
RELAY — small GCP Cloud Function (project aviationchat)
  1. verify Sentry webhook signature
  2. dedupe: existing GitHub issue labeled incident:<short-id> → drop
  3. pre-fetch ±15-min Cloud Run log excerpt (its service account holds roles/logging.viewer)
  4. TARGET switch:
       TARGET=routines (default) → POST the Routine's /fire endpoint (bearer) with issue-id + logs
       TARGET=github  (rollback) → GitHub repository_dispatch → dormant Actions lane
      ▼
Claude executes .github/claude/incident-triage.md (Story 16.1)
  LEVEL 2: branches from MAIN at the event's release SHA (the code that is LIVE) ·
  builds the fix on claude/incident-<short-id> · runs the test suite ·
  opens a PR to **main** with the report as its body  (it can NEVER merge)
      ▼
GitHub issue labeled `incident` — body = the full report → email + mobile-app push
      ▼
Daniel, on the phone: reviews the report + PR → merge = acceptance
  (Routines bonus: the issue footer carries the live session URL — tap to stand inside
   the agent session and interrogate it before merging)
```

**Why the relay pre-fetches logs:** the Routines sandbox has no GCP identity. Fetching the log
excerpt in the relay (which is GCP-native anyway) keeps the logs leg alive in the primary lane
without handing GCP credentials to a beta product.

## Acceptance Criteria

1. **The relay exists** (GCP Cloud Function, project `aviationchat`): verifies the Sentry
   signature, dedupes by `incident:<short-id>` issue label, pre-fetches the log excerpt, and
   dispatches per `TARGET`. **The `TARGET` env var IS the rollback mechanism** — flipping it is
   the entire migration, no code change.
2. **The Routine is live**: fire endpoint + bearer token; on fire it executes the 16.1 runbook
   with the payload (Sentry issue id + log excerpt); repo access via the GitHub connection.
   Task 0 verifies the beta's current auth/billing model and pins the beta header version used.
3. **Level 2 execution, guarded — targets `main` (Daniel, 2026-07-09: "main is live and will be
   the one that needs to be monitored and pushed to")**: the incident branch is cut from `main`
   at the event's release SHA (the exact code that is live — Sentry's release tag carries it);
   fix implemented on `claude/incident-<short-id>` only; full test suite run with real output in
   the PR; **PR opened against `main`**, never self-merged; nothing the pipeline does can push to
   `main` or `main_debug` directly — merging to `main` stays the owner's deliberate manual
   action, now deliverable from the phone. The PR body flags the required **back-merge**: after
   merging the hotfix to `main`, sync it into `main_debug` so the next promotion doesn't revert
   it (exact command in the footer; automating the back-merge is a 16.4 candidate).
4. **Delivery**: GitHub issue labeled `incident` + `incident:<short-id>`, body = the complete
   report (16.1 template), footer = acceptance instructions + the PR link + (Routines lane) the
   live session URL. GitHub's native email + app push are the notification — no other channels.
5. **The rollback lane exists DORMANT and is proven**: `.github/workflows/incident-response.yml`
   on `repository_dispatch` runs `claude-code-action` (agent mode, `ANTHROPIC_API_KEY` secret)
   with the same runbook, logs via the repo's existing Workload Identity Federation +
   `roles/logging.viewer`. A **rollback drill** passes: flip `TARGET=github`, force a failure,
   the pipeline completes end-to-end — the fallback is tested, not theoretical.
6. **Guards**: dedupe idempotent across retries; `INCIDENTS_PAUSED` relay env var as kill switch;
   per-run turn/cost cap; report inherits the runbook's no-secrets/no-PII rules.
7. **E2E phone drill gates `done`**: forced P1 (Story-11.5 smoke pattern), desktop untouched →
   issue + push arrive on the phone → Daniel reviews the report + ready-made PR from the phone
   and merges (or rejects, which is also a pass — the gate is accuracy + deliverability, not
   merge). Frontend leg joins the epic close-out live-QA once 16.3 ships.

## Tasks / Subtasks

- [ ] Task 0 — Preflight with Daniel (ask-first gates live here): verify Routines beta (endpoint
      auth, billing model, GitHub repo connection, beta-header pinning); create secrets (Sentry
      webhook secret, routine bearer, `ANTHROPIC_API_KEY` for the fallback lane); approve the two
      IAM grants (relay SA + WIF identity → `roles/logging.viewer`)
- [ ] Task 1 — Relay function (AC: 1, 6): signature check, dedupe, log pre-fetch, `TARGET` switch,
      kill switch; deploy + unit tests
- [ ] Task 2 — Routine setup (AC: 2, 3, 4): fire endpoint wiring, runbook invocation, Level-2
      prompt contract (branch/tests/PR), issue creation + footer
- [ ] Task 3 — Dormant fallback workflow (AC: 5): Actions workflow + WIF logging auth, same
      runbook, same delivery
- [ ] Task 4 — Sentry alert rules (both projects when 16.3 lands): webhook action → relay URL
- [ ] Task 5 — Drills (AC: 5, 7): primary E2E phone drill + rollback drill; verdicts + report
      links in Completion Notes

## Dev Notes

- **Beta risk, eyes open (Daniel's call):** Routines ships behind an experimental beta header —
  breaking changes are possible. That risk is priced in by AC-5: the proven lane sits one env
  flip away, and the runbook (16.1) is lane-agnostic by design.
- **Dedupe key = Sentry short-id** (stable per issue, safe in branch/label names).
- **Org-wide by contract**: the relay accepts alerts from any project in org `aviationchat` —
  16.3's frontend project plugs in by adding one alert rule (Task 4), zero pipeline changes.
- **Cost profile**: idle = ~$0 (relay is pennies; nothing runs without an incident). Per incident
  at Level 2 = triage + build + tests (ballpark a few dollars; exact routine billing confirmed in
  Task 0). `INCIDENTS_PAUSED` caps a runaway alert storm; dedupe caps repeats.
- **Security**: no service-account keys anywhere (relay uses its runtime SA; fallback uses WIF);
  Sentry signature verified before anything fires; bearer token + webhook secret live in the
  relay's secret config, never in the repo.
- **Constitution alignment + the deliberate `main` carve-out**: the pipeline writes only to its
  own `claude/incident-*` branches + issues. The standing rule "never PR/merge to `main`" is
  **amended by Daniel (2026-07-09) for this lane only**: production crashes come FROM `main` (the
  live deploy), so incident-fix PRs target `main` — and the merge (= the promotion decision that
  rule protects) remains his manual, per-action button, unchanged in spirit. `main_debug` stays
  the normal dev lane; hotfixes back-merge into it. The 16.2 dev session must reconcile
  `git-policy.md` / project `AGENTS.md` §8 wording with this carve-out so future agents don't
  fight the pipeline. Test output in the PR must be real (pasted), per house rules.
- **What "monitoring main" means mechanically**: Sentry watches the deployed service, which is
  built from `main`; every event carries the deploy's `GIT_SHA` release tag → triage checks out
  that SHA, so the agent reads and fixes the code that actually crashed, not the newer
  `main_debug` state.

## References

- [Source: always-live-trigger-brainstorm.md — options + ✅ DECISION block (Daniel, 2026-07-09)]
- [Source: story-16-1-sentry-incident-triage-agent_v2.md — the runbook contract]
- [Source: .github/workflows/deploy-backend.yml — existing WIF identity to extend]
- [Source: _bmad/bmm/stories/story-11-5-production-alert-wiring.md — smoke pattern + alert chain]
- [Verified 2026-07-09 via claude-code-guide: Routines fire endpoint (beta); claude-code-action
  agent mode on repository_dispatch; API-key-only auth for CI]
