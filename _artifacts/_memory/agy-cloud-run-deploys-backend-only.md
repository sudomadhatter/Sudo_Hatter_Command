---
name: agy-cloud-run-deploys-backend-only
description: "AGY backend Cloud Run image is built from a Dockerfile that only COPYs backend/ — dev/tooling/doc files in git never reach the deployed image, so they cost $0 on Cloud Run regardless of branch."
metadata: 
  node_type: memory
  type: project
  originSessionId: de3a05bc-cc41-4b67-a62f-0c5af1ac8be0
---

**Daniel's recurring worry "am I paying to store `.agents`/`_artifacts`/`_bmad`/`_my_resources`/docs on Google Cloud?" → NO.** The `aviationchat-backend` Cloud Run service (region `us-east1`) is built from the repo-root `Dockerfile`, which does **only** `COPY backend/requirements.txt` + `COPY backend/ ./backend/` — nothing outside `backend/` is ever baked into the image. So none of the dev/tooling/doc trees reach the deployed container or Artifact Registry, **on any branch**. Belt-and-suspenders: `.dockerignore` AND `.gcloudignore` also exclude `.agents/`, `_bmad/`, `_bmad-output/`, `_artifacts/`, `docs/`, `*.md`, `frontend/`, `backend/tests/`, `scripts/`, etc. (`.gcloudignore` is missing `.claude/` + `_my_resources/` non-md, so those upload to Cloud Build transiently — harmless, since the Dockerfile only bakes `backend/`; tighten only if you want a leaner upload).

**Consequence for the branch model:** it's fine to keep everything (dev tooling + artifacts + docs) on `main` — it changes the Cloud Run bill by $0. So "keep main app-code-only" is a *cleanliness preference*, not a cost requirement; don't gitignore these (Daniel syncs machines via GitHub and needs them). See [[git-branch-model-standard]].

**Deploy facts:** backend = `aviationchat-backend` (us-east1, Dockerfile, single-worker invariant Story 11.7 — never raise `--workers` without re-auditing in-memory caches). Frontend = `firebase-frontend` (App Hosting, `frontend/apphosting.yaml`). Other services: `sentry-incident-relay`, `ext-firestore-send-email-processqueue`. Secrets are injected as Cloud Run env vars, NOT baked (`auth_keys/` is dockerignored).
