---
name: fah-secret-needs-viewer-role
description: Firebase App Hosting build secrets need secretAccessor AND secretmanager.viewer; the fah/misconfigured-secret error hides the real missing permission
metadata: 
  node_type: memory
  type: project
  originSessionId: d45b647a-dc77-4633-bc2e-fff603503352
---

AviationChat frontend (App Hosting backend `firebase-frontend`, us-east4) deploy outage 2026-07-13→17: every rollout FAILED with `fah/misconfigured-secret` on `SENTRY_AUTH_TOKEN` even though the secret existed and the build SA had `roles/secretmanager.secretAccessor`.

**Why:** The FAH "preparer" build step resolves `versions/latest` via `secretmanager.versions.get` (metadata), which secretAccessor does NOT include — it lives in `roles/secretmanager.viewer`. Firebase's own `apphosting:secrets:grantaccess` grants BOTH roles; a manual gcloud grant of accessor-only reproduces this outage. The wrapper error message never names the missing permission — only the raw Cloud Build log does (`gcloud builds log <id> --region us-east4`: "Permission 'secretmanager.versions.get' denied").

**How to apply:**
- Any new FAH build secret: grant the build SA (`firebase-app-hosting-compute@aviationchat.iam.gserviceaccount.com`) both `secretAccessor` and `viewer` on that secret (or use `firebase apphosting:secrets:grantaccess`).
- "Push to main failed after N minutes" emails with a clean GitHub Actions history = App Hosting rollout failures. They are invisible in `gh run list`; check `firebaseapphosting.googleapis.com/v1beta/.../rollouts` (REST with gcloud token — firebase CLI is not installed on this machine). Build terminal-success state is `READY` (not SUCCEEDED); rollout success is `SUCCEEDED`.
- Manual retrigger without a push: POST builds?buildId=… `{"source":{"codebase":{"branch":"main"}}}` then POST rollouts?rolloutId=… `{"build":"<build name>"}`.

Related: [[overseer-jobs-paused-by-design]], [[sentry-api-access-aviationchat]]
