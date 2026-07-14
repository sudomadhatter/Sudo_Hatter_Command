---
description: Ship committed changes to production (main) via merge or cherry-pick, trigger CI/CD, and deploy backend to Cloud Run.
---

# /1_push-to-main-and-deploy — Merge, Push, and Deploy

This workflow guides the agent through shipping verified commits from the development line (`main_debug` or a feature branch) to the production line (`main`).

## 🛑 MANDATORY RULES (Before You Start)
1. **Never commit/push autonomously**: Always write the exact git commands for the human to approve/run, OR propose them via execution tools so the human can review and approve them individually.
2. **Clear GITHUB_TOKEN on push**: When proposing or running `git push` or `git pull` from the agent terminal, always clear the environment variable first (e.g., prefix with `$env:GITHUB_TOKEN = ""` in PowerShell or `env -u GITHUB_TOKEN` in Bash) to prevent authentication failures from invalid session tokens.
3. **Pre-flight Gate**: You MUST run Step 0 (Verification) successfully. If any test or build fails, STOP and report the error. Do not proceed to deployment.

---

## Step 0: Pre-flight Verification (All Projects)
Run these checks before touching the production branch:
1. **Backend Tests**: Run the pytest suite (excluding voice-agent mocks if applicable).
2. **Frontend Build**: Run the production build compiler (`npm run build` or `npx next build`) in the `frontend` directory to ensure no compilation errors exist.

---

## Step 1: Commit and Push Development Branch
Ensure all active work on `main_debug` or your feature branch is committed and pushed:
```powershell
# In PowerShell:
git status
git add <explicit-file-paths>
git commit -m "<semantic-message>"
$env:GITHUB_TOKEN = ""; git push origin <branch-name>
```

---

## Step 2: Merge or Cherry-pick to Production (main)

Decide which path to take based on the state of `main_debug`:
*   **Path A (Merge)**: Use this if `main_debug` contains NO other unreleased or in-progress changes, and you want to merge everything.
*   **Path B (Cherry-pick)**: Use this if `main_debug` has other unfinished features, and you ONLY want to ship the specific commits you just verified.

### Path A: Merge Branch
```powershell
# 1. Switch to production and pull latest
git checkout main
$env:GITHUB_TOKEN = ""; git pull origin main

# 2. Merge branch (using --no-ff to preserve history metadata)
git merge <branch-name> --no-ff

# 🛑 HUMAN GATE: Summarize the commits + changed files to the user first.
# 3. Push to origin main to trigger frontend App Hosting CI/CD
$env:GITHUB_TOKEN = ""; git push origin main
```

### Path B: Cherry-pick Specific Commits
```powershell
# 1. Identify the commit SHAs from your dev branch:
git log -n 5 --oneline

# 2. Switch to production and pull latest
git checkout main
$env:GITHUB_TOKEN = ""; git pull origin main

# 3. Cherry-pick the target commit(s)
git cherry-pick <commit-sha-1> <commit-sha-2>

# 🛑 HUMAN GATE: Summarize the cherry-picked commits to the user first.
# 4. Push to origin main to trigger frontend App Hosting CI/CD
$env:GITHUB_TOKEN = ""; git push origin main
```

---

## Step 3: Switch Back to Dev Line
Always return your working tree to the development branch to keep the workspace isolated:
```powershell
git checkout <dev-branch-name-or-main_debug>
```

---

## Step 4: Deploy Backend (Optional / Cloud Run)
If the changes include backend modifications, deploy them to GCP Cloud Run:
1. Run the project's backend deployment script (e.g. `.\deploy_secrets.ps1` or `gcloud run deploy`).
2. Target the correct region (e.g. `us-east1` for AviationChat) and project ID (`aviationchat`).

---

## Step 5: Verification & Ledger Update
1. **Verify Live Site**: Hit the `/health` endpoint on the backend and verify the frontend at `https://aviationchat.org` (or the active custom domain).
2. **Update Ledger**: Update `_artifacts/INDEX.md` (and the home-base `INDEX.md` if working from home base) with a row for this deployment.
3. **Update Active Context**: Update `active-context.md` under the project-local BMAD state folder with the deployment details.

---
*Reference: `@.agents/skills/deploy-backend/SKILL.md` for full GCP authentication and pipeline specs.*

Optional additional input (feature branch name): $ARGUMENTS
