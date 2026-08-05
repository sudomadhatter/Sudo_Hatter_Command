---
name: overseer-jobs-paused-by-design
description: "Both AviationChat overseer Cloud Scheduler jobs are PAUSED on purpose (2026-07-17, Daniel's call) — do not \"fix\" them back on; OIDC pins now ship via deploy yaml"
metadata: 
  node_type: memory
  type: project
  originSessionId: d45b647a-dc77-4633-bc2e-fff603503352
---

2026-07-17: Daniel wants the nightly overseer OFF for now but ready to toggle on. Both Cloud Scheduler jobs in `aviationchat`/us-east1 are **PAUSED** — their daily 401/403 failure spam was most of the "Google Cloud error messages."

**Why:** `overseer-nightly` (POST `/internal/run-overseer`, OIDC) got daily 403s because the backend fails closed without `INTERNAL_OIDC_AUDIENCE`/`PROBE_OIDC_AUDIENCE`/`PROBE_OIDC_SA`; those pins now ship in `.github/workflows/deploy-backend.yml` (commit ba59621b, single source of truth — never console). `nightly-overseer-trigger` is a stale duplicate hitting the old `/api/admin/run-overseer` with unusable auth (daily 401) — superseded, kept only because paused; candidate for deletion with Daniel's OK.

**How to apply:**
- Do not resume, delete, or "repair" these jobs when spotted in an audit — paused IS the desired state.
- To turn the overseer on: `gcloud scheduler jobs resume overseer-nightly --location us-east1 --project aviationchat` (a deploy carrying ba59621b must have run first, so the pins are live; audience = the service's canonical run.app URL, SA = 856831340418-compute@developer.gserviceaccount.com).
- Leave `nightly-overseer-trigger` paused/dead — resuming it can only 401.

Related: [[fah-secret-needs-viewer-role]], [[incident-pipeline-16-2-operations]]
