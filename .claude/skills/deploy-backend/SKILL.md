---
name: deploy-backend
description: Land backend changes on main through the gated merge, trigger CI/CD, and verify Cloud Run deployment. Use when the user says "deploy backend", "push and verify", or "ship it".
---

# Deploy Backend to Cloud Run

Backend changes reach production one way: a gated merge to `main` (epic branch via `/sudo-push-e2e`, or a `chore/*`/`claude/incident-*` branch merged with Daniel's sign-off) → CI/CD auto-deploys → verify on Cloud Run. This skill covers the deploy-and-verify half; it never invents its own path onto `main`.

## Environment

| Key | Value |
|-----|-------|
| **Project** | `aviationchat` |
| **Region** | `us-east1` (all infra — AR + Cloud Run) |
| **Service** | `aviationchat-backend` |
| **Service URL** | `https://aviationchat-backend-856831340418.us-east1.run.app` |
| **AR Repo** | `us-east1-docker.pkg.dev/aviationchat/aviationchat-repo` |
| **CI/CD Trigger** | Push to `main` with paths: `backend/**`, `Dockerfile`, `.github/workflows/deploy-backend.yml` |
| **Pipeline Time** | ~5-8 minutes (quality gate + Docker build + push + deploy) |

## Workflow

> [!CAUTION]
> ## 🛑 MANDATORY HUMAN GATE — NO EXCEPTIONS
>
> **You MUST stop and ask for explicit permission before executing ANY git push command (Steps 2, 3, or any cherry-pick/sync).** This is non-negotiable.
>
> **Before pushing, you MUST:**
> 1. Present a summary: what branch, what commits, what will deploy
> 2. Ask: *"Ready to push? Please confirm."*
> 3. **WAIT for the user to say yes/confirmed/approved/go**
>
> **Trigger words like "deploy", "push", "ship it" in the ORIGINAL request are NOT automatic authorization.** They invoke this skill — they do NOT pre-authorize the push. You still stop and ask.
>
> **If you push without asking, you have violated the most critical directive of this skill.**

### Step 1: Run Tests Locally

// turbo
```powershell
python -m pytest backend/tests/ -v --tb=short -k "not test_orchestrator_mercy_rule_on_attempt_4 and not TestMercyMCQHelpers and not test_mercy_rule_emits_mcq and not test_surrender_triggers_mcq and not test_mcq_correct_answer_advances and not test_start_prep_idempotent"
```

> [!IMPORTANT]
> Do NOT push if tests fail. The CI/CD quality gate will reject it. The `-k` filter matches the exclusions in `deploy-backend.yml` — keep them in sync.

### Step 2: Commit on Your Branch

```powershell
git add <files>            # explicit paths only — never -A / . / -u
git commit -m "<message>"
```

### Step 3: Reach Main Through the Gate

CI/CD only triggers on `main`, and `main` is reached only through the branch model
(`.agents/rules/git-policy.md`):

- **Epic work** → the epic merges via **`/sudo-push-e2e`** (full gate + Daniel's sign-off). That
  command owns the merge, the push, and the deploy watch — hand off to it.
- **Hotfix / ad-hoc backend change** → on your `chore/*` (or `claude/incident-*`) branch, with tests
  green (Step 1), present the summary and get Daniel's confirmation, then:

```powershell
git checkout main
$env:GITHUB_TOKEN = ""; git pull --ff-only origin main
git merge <branch> --no-ff
$env:GITHUB_TOKEN = ""; git push origin main     # fires the deploy
git branch -d <branch>
```

> [!WARNING]
> Never `git checkout main && git checkout <branch> -- <files>` to hand-copy changes onto `main` —
> that mints untracked duplicate commits and bypasses the gate. Merge the branch or use
> `/sudo-push-e2e`; nothing else touches `main`.

### Step 4: Diagnose (if failure email arrives)

**Don't wait and hope.** Check AR immediately:

// turbo
```powershell
gcloud artifacts docker images list us-east1-docker.pkg.dev/aviationchat/aviationchat-repo --include-tags --limit=3
```

| AR has new image? | Meaning | Action |
|---|---|---|
| **No** | Quality gate or Docker build failed | Run tests locally (Step 1) |
| **Yes, but no new revision** | Deploy step failed | Run manual deploy to see exact error (Step 4b) |
| **Yes, and new revision** | Success! | Verify (Step 5) |

**Step 4b — Manual deploy to reveal the error:**

```powershell
gcloud run deploy aviationchat-backend `
  --image us-east1-docker.pkg.dev/aviationchat/aviationchat-repo/aviationchat-backend:latest `
  --region=us-east1 --project=aviationchat `
  --allow-unauthenticated `
  --set-env-vars "GCP_PROJECT_ID=aviationchat" `
  --set-env-vars "CORS_ORIGINS=https://aviationchat.org" `
  --set-secrets "GEMINI_API_KEY=GEMINI_API_KEY:latest,JWT_ADMIN_SECRET=JWT_ADMIN_SECRET:latest,DEEPGRAM_API_KEY=DEEPGRAM_API_KEY:latest" `
  --memory 1Gi --cpu 1 --timeout 3600 `
  --session-affinity --concurrency 40 `
  --min-instances 0 --max-instances 5
```

> **min-instances:** `0` = DEV posture (2026-07-18 cost decision — no 24/7 warm instance;
> `BackendWarmup.tsx` pings `/health` on every app open to mask the cold start).
> 🔴 Flip back to `1` before user beta — see the PRE-BETA OPS GATE note in
> `_bmad-output/implementation-artifacts/sprint-status.yaml`.

This deploys the already-built image and shows the **exact error** if it fails. It also unblocks you immediately if CI/CD is slow.

### Step 5: Verify Deployment with Google Cloud

**Always run all three checks after every push to main.** Don't assume success.

#### 5a. Check Artifact Registry for New Image

// turbo
```powershell
gcloud artifacts docker images list us-east1-docker.pkg.dev/aviationchat/aviationchat-repo --include-tags --limit=3
```

✅ **Pass:** New image with the commit hash tag matching your push.
❌ **Fail:** No new image → CI/CD quality gate or Docker build failed. Re-run Step 1.

#### 5b. Check Cloud Run Active Revision

// turbo
```powershell
gcloud run revisions list --service=aviationchat-backend --region=us-east1 --project=aviationchat --limit=3
```

✅ **Pass:** Latest revision shows `ACTIVE yes` with a timestamp within the last 10 minutes.
❌ **Fail:** No new revision despite new AR image → deploy step failed. Run Step 4b manual deploy.

#### 5c. Health Check

// turbo
```powershell
Invoke-RestMethod -Uri "https://aviationchat-backend-856831340418.us-east1.run.app/health" -Method GET
```

✅ **Pass:** Returns `status: ok`.
❌ **Fail:** Timeout or error → revision is crashing. Check logs: `gcloud run services logs read aviationchat-backend --region=us-east1 --project=aviationchat --limit=20`

#### 5d. Check Cloud Run Error Logs

// turbo
```powershell
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=aviationchat-backend AND severity>=ERROR" --project aviationchat --limit 5 --format="table(timestamp,textPayload)" 2>&1 | Select-Object -First 30
```

✅ **Pass:** No new errors since deploy, or only known non-critical errors (e.g., Gemini Live `GoAway` session timeout).
❌ **Fail:** New import errors, crash loops, or 500s → rollback or hotfix.

> [!TIP]
> **Known non-critical errors:** Sully/Igor `GoAway` (1008 policy violation) — this is Gemini Live's session duration limit. The client didn't close cleanly after timeout. Not a deployment issue.

#### 5e. Frontend Production Build Check

Always verify the frontend builds cleanly after any change. This catches Vercel build failures before they happen.

// turbo
```powershell
npx next build 2>&1 | Select-Object -Last 15
```

✅ **Pass:** Exit code 0, all routes generated.
❌ **Fail:** TypeScript or build errors → fix before pushing.

> [!IMPORTANT]
> **For frontend-only changes:** Steps 5a and 5b won't show new AR images (frontend deploys via Vercel, not Docker). Still run **5c** and **5e** to confirm backend health and frontend build parity, then verify via `git log --oneline -3 origin/main` and a live check of [aviationchat.org](https://aviationchat.org).

## Lessons Learned (2026-05-05)

### 1. Comma in `--set-env-vars` Breaks gcloud
`gcloud` uses comma as the key-value separator. A value like `https://a.com,https://b.com` gets split.

**Fix:** Use `^@^` delimiter syntax: `--set-env-vars "^@^KEY1=val1@KEY2=val2"` — or just remove the comma.

### 2. New AR Repos Need IAM Bindings
Creating a new Artifact Registry repo doesn't inherit project IAM. The CI/CD service account needs explicit grants:

```powershell
gcloud artifacts repositories add-iam-policy-binding aviationchat-repo `
  --location=us-east1 --project=aviationchat `
  --member="serviceAccount:856831340418-compute@developer.gserviceaccount.com" `
  --role="roles/artifactregistry.writer"
```

### 3. Deploy Needs 4 IAM Roles
The CI/CD service account (`856831340418-compute@developer.gserviceaccount.com`) requires:

| Role | Why |
|------|-----|
| `roles/run.admin` | Deploy Cloud Run services |
| `roles/iam.serviceAccountUser` | Act as the runtime SA |
| `roles/secretmanager.secretAccessor` | Mount secrets like `GEMINI_API_KEY` |
| `roles/artifactregistry.writer` | Push Docker images |

### 4. Empty Commits Don't Trigger CI/CD
The workflow has a path filter. Must touch `backend/**`, `Dockerfile`, or the workflow file itself.

### 5. Don't Build Docker Locally
No Docker Desktop on this machine. The CI/CD pipeline handles builds. If you need to unblock, deploy the already-built image from AR (Step 4b).

### 6. Check AR First, Not Revisions
When diagnosing failures, **check AR images first**. If images exist, the problem is in the deploy step — not code. This saves 5+ minutes of guessing.
