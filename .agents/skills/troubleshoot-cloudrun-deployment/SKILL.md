---
name: troubleshoot-cloudrun-deployment
description: "Comprehensive troubleshooting guide for Cloud Run deployments. Use this skill when CI/CD fails, manual pushes are rejected, or when Google Cloud refuses to run the pushed code due to compilation errors, runtime crashes, or upload size limits."
---

# Troubleshooting Cloud Run Deployments & Pipeline Failures

## 🛑 When to Use This Skill
Use this guide when:
- GitHub Actions CI/CD pipelines fail during `gcloud run deploy` or `gcloud builds submit`.
- Local manual deployments to Cloud Run fail or get rejected by Google Cloud.
- You suspect the code pushed to `main` contains an error that Google Cloud doesn't like (compilation failure or runtime crash).
- The pipeline times out or fails before building due to massive file uploads (e.g., large assets).

---

## 🔌 Phase 1: Connect and Read the Error Logs

Before fixing anything, you must ask Google Cloud **why** it rejected the push. Deployments fail in one of two places: **Cloud Build** (it couldn't compile your code) or **Cloud Run** (it compiled, but crashed when starting).

### 1. Check Cloud Build History (Compilation Errors)
If the deployment didn't even reach Cloud Run, it died in Cloud Build.
```powershell
# List the recent builds to spot failures
gcloud builds list --project=aviationchat --limit=5
```
*If you see a `FAILED` status, copy its ID.*

### 2. Read Specific Build Logs
Pull the exact error logs to see what code Google Cloud rejected during the build:
```powershell
# Replace <BUILD_ID> with the ID from the step above
gcloud builds log <BUILD_ID> --project=aviationchat
```
*Look for Python Syntax errors, missing dependencies in `requirements.txt`, Dockerfile errors, or "Archive Size" limits.*

### 3. Check Cloud Run Revisions (Runtime Errors)
If the build succeeded but the app still isn't working, check if Cloud Run rejected the container during startup.
```powershell
# List the last 5 revisions
gcloud run revisions list --service aviationchat-backend --region us-east1 --project aviationchat --limit 5
```

### 4. Read Cloud Run Service Logs
If a revision failed to route traffic or crashed on boot, pull the runtime logs to see the stack trace:
```powershell
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=aviationchat-backend AND severity>=ERROR" --project=aviationchat --limit=10
```
*Look for missing Environment Variables, `ModuleNotFoundError`, Port binding issues, or failing health checks.*

---

## 🛠️ Phase 2: Diagnosing and Fixing the Root Cause

### Scenario A: Google Cloud Rejected the Code (Build/Runtime Errors)
If the logs show a code error, Google Cloud is protecting the live environment from a bad push.
1. **Replicate Locally**: Run the local test suite to catch the exact error.
   ```powershell
   .venv\Scripts\python.exe -m pytest backend/tests/ -v
   ```
2. **Fix the Code**: Address the syntax error, missing dependency, or logic bug locally.
3. **Push to Main**: Commit and push the fix to `main` to trigger the CI/CD pipeline again.

### Scenario B: Upload Size Limits (Infrastructure Error)
If the build logs indicate a timeout during "Uploading sources" or report an archive size error (e.g., 4.5+ GiB), the pipeline is trying to upload massive local files (like videos or datasets).
1. Check directory sizes locally:
   ```powershell
   Get-ChildItem -Directory | Select-Object Name, @{Name="Size(MB)";Expression={(Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB}}
   ```
2. Update `.gcloudignore` to exclude bloated directories (e.g., `docs/`, `webapp_images/`).

---

## 🚀 Phase 3: How to Manually Deploy if CI/CD Fails

If GitHub Actions is broken and you need to get the `main` branch live immediately, you can bypass the CI/CD pipeline and force a manual deployment from your local machine.

### Step-by-Step Manual Deployment

**1. Verify Local Code Integrity First**
Ensure the local code runs without errors before forcing a push to Google Cloud.

**2. Execute the Manual Deploy Command**
Run the following command from the root of the project. It uses the local source code, builds the container in Cloud Build, pushes it to Artifact Registry, and deploys it to Cloud Run.

```powershell
gcloud run deploy aviationchat-backend `
  --source . `
  --region us-east1 `
  --project aviationchat `
  --platform managed `
  --allow-unauthenticated `
  --set-env-vars "GCP_PROJECT_ID=aviationchat" `
  --set-env-vars "CORS_ORIGINS=https://aviationchat.org" `
  --set-secrets "GEMINI_API_KEY=GEMINI_API_KEY:latest" `
  --memory 1Gi `
  --cpu 1 `
  --timeout 3600 `
  --session-affinity `
  --concurrency 40 `
  --min-instances 1 `
  --max-instances 5
```

**3. Confirm Deployment**
Once the terminal reports `Routing traffic.....done`, run a quick health check to verify the new code is live:
```powershell
(Invoke-WebRequest -Uri https://aviationchat-backend-856831340418.us-east1.run.app/health).Content
```

---

## ✅ End-of-Task Checklist
If this troubleshooting skill was used, ensure the following is completed before closing the task:
- [ ] Error logs were successfully read via `gcloud logging` or `gcloud builds log` to identify the rejection reason.
- [ ] The root cause (Code Error or Upload Size) was identified and fixed locally.
- [ ] A manual or automated deployment was successfully completed.
- [ ] If `.gcloudignore` was modified, the user was instructed to commit it.
