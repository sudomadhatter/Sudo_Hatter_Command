---
name: stale-cloud-run-revision-fakes-prod-incident
description: "A Sentry event tagged environment=production can come from a 0%-traffic stale Cloud Run revision, not the live one — always compare the event's `release` against the serving revision's GIT_SHA before believing an incident report"
metadata: 
  node_type: memory
  type: project
  originSessionId: a1f6ddbe-82ac-4307-9a35-1b9c4418f9b7
  modified: 2026-07-30T17:23:05.811Z
---

**Check the event's `release` against the LIVE revision's `GIT_SHA` before acting on any AGY Sentry
incident.** `environment` is hardcoded `"production"` in `backend/observability/sentry_init.py`, and
`server_name` reads `localhost` on Cloud Run — so neither tag distinguishes the serving revision from a
stale one. `release` (which is `os.getenv("GIT_SHA")`) is the only discriminator.

**The mechanism (found 2026-07-30, cleaned up same day).** `deploy-backend.yml` deploys `--no-traffic
--tag sha-<short>` so it can smoke-test the new revision at its tag URL, then promotes with
`--to-latest`. The tag was never removed. Consequences, both invisible from the sprint board:

1. Every tagged revision stays a **publicly reachable** endpoint serving historical code — the service
   grants `run.invoker` to `allUsers`, and `curl https://sha-<old>---<host>/health` returned 200.
2. **A revision's autoscaling config is immutable.** Three revisions deployed before the 2026-07-18
   min-instances-0 cost decision kept `minScale=1` forever, each holding a warm 1vCPU/1Gi instance at
   **0% traffic**. That decision only ever applied to new revisions and could not be applied retroactively.

Revision `00037-gux` (release `34381bdd`, 07-14) predated *both* the `logger.critical`→`warning` fix
(07-14, `583f463`) and the OIDC pins being bound in the workflow (07-17, `ba59621`), so every instance
recycle re-emitted two Sentry **fatals** from 16-day-old code. Four incident triages
(`_artifacts/debugging/2026-07-1{3,4}_*`) chased prod config that was already correct — the live revision
had all five bindings the whole time. Only the *newest* revision can be assumed to be the code running.

**How to apply:** on any AGY Sentry incident, first run
`gcloud run services describe aviationchat-backend --region us-east1 --project aviationchat
--format='value(status.traffic)'` and compare `GIT_SHA` to the event's `release`. If they differ, the
report is describing dead code. Fixed forward: the workflow now untags after promotion and prunes to the
3 newest revisions. Related: [[agy-cloud-run-deploys-backend-only]], [[overseer-jobs-paused-by-design]],
[[sentry-api-access-aviationchat]], [[incident-pipeline-16-2-operations]].
