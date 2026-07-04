---
description: Merge feature branch into main, push to trigger CI/CD, and optionally deploy backend to Cloud Run
---

# /1_push-to-main-and-deploy — Merge, Push, and Deploy

Execute the workflow defined in @.agents/workflows/1_push-to-main-and-deploy.md.

**opencode execution notes:**
- Step 0 (pre-flight): run the backend pytest suite (with the documented voice-agent mock exclusions) and `npx next build` for the frontend. Do NOT proceed if either fails.
- Step 1: ensure the feature branch is committed and pushed to `origin`.
- Step 2: checkout `main`, `git pull origin main`, merge the feature branch with `--no-ff`.
- 🛑 **MANDATORY HUMAN GATE (Step 2):** `git push origin main` is gated by `permission.bash` `ask` AND the workflow's explicit human-gate. STOP, summarize the commits + files about to be pushed, and wait for Don's explicit confirmation before pushing to `main`.
- Step 3: checkout back to the feature branch to keep the workspace isolated.
- Step 4 (optional/debug): manual `gcloud run deploy` of the backend to Cloud Run. `gcloud *` is `permission.bash` `ask` — Don confirms. Use the exact image, region (us-east1), project (aviationchat), secrets, and resource flags from the canonical workflow.
- Step 5: verify — list active Cloud Run revisions, hit the `/health` endpoint (expect `{"status":"ok"}`), and read container logs if it fails. Firebase App Hosting auto-deploys the frontend on push to `main`; verify at https://aviationchat.org.
- Step 6: update `_bmad-output/active-context/active-context.md` with the deployment record.
- Honor @.agents/rules/constitution.md hard stops: you do NOT run `git commit` or `git push` autonomously — provide commands for Don, and the `git push origin main` specifically requires his explicit confirmation per the workflow's human gate.
- Reference: @.agents/skills/deploy-backend/SKILL.md for broader deploy context.

Optional additional input (feature branch name): $ARGUMENTS
