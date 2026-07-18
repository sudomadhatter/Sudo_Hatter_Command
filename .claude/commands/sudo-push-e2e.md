---
description: Push & promote with the E2E gate — push main_debug, or promote main_debug → main (full merge OR cherry-picked features). Nothing lands on main until /sudo-e2e is green. Then CI/CD + Cloud Run deploy + live verification.
---

# /sudo-push-e2e — Push, Gate, Promote, Deploy

The one shipping command. It moves verified work from the development line (`main_debug`) toward the
production line (`main`), and it **refuses to touch `main` until the end-to-end suite is green**.

**Branch model (never violate):** `main_debug` is the integration branch. `main` is only ever
*fast-forwarded or merged up from* `main_debug` — `main` must NEVER end up ahead. After any
cherry-pick promotion, reconcile so `main_debug` contains `main` again (Step 5).

## 🛑 MANDATORY RULES (Before You Start)
1. **Never commit/push autonomously**: write the exact git commands for the human to approve/run, OR
   propose them via execution tools so the human approves each one individually.
2. **Clear GITHUB_TOKEN on push/pull**: prefix with `$env:GITHUB_TOKEN = ""` (PowerShell) or
   `env -u GITHUB_TOKEN` (Bash) to prevent stale-session auth failures.
3. **The gate is not optional**: a red gate STOPS the command. Report what failed; do not "push anyway".

## Step 0 — Resolve the target project (FIRST — before anything else)
Run from the **command center** (the lobby), this operates on exactly ONE child project under
`Projects/`, never the lobby itself:
0. **Self (sub-project fast path)** — no `Projects/` subfolder here → you ARE the project:
   `PROJECT_ROOT = .`, skip ahead.
1. **Inline override** — if `$ARGUMENTS` begins with a name matching a folder under `Projects/`,
   that is the target; consume the token. Write it to `.agents/active-project.txt`.
2. **Active pointer** — else read `.agents/active-project.txt`.
3. **Ask** — else STOP and ask.

Set `PROJECT_ROOT` and **echo exactly** `Target: Projects/<name>`. All git/test commands below run
inside `PROJECT_ROOT`.

## Step 1 — Pick the path
From the remaining `$ARGUMENTS` (`debug` | `main` | `cherry [sha…]`) or by asking the human:

| Path | What ships | Gate required |
|---|---|---|
| **A · `debug`** — push `main_debug` only | commits already on `main_debug` → `origin/main_debug` | **Light**: backend pytest + frontend build |
| **B · `main`** — full promotion | everything on `main_debug` → merged into `main` | **FULL**: light gate **+ `/sudo-e2e` green** |
| **C · `cherry`** — feature promotion | chosen commit(s) cherry-picked onto `main` | **FULL**: light gate **+ `/sudo-e2e` green** |

Path B is for "main_debug is clean, ship it all". Path C is for "main_debug has unfinished work;
ship only these verified features". If unsure which, show `git log --oneline main..main_debug` and
decide together.

## Step 2 — Run the gate (BEFORE touching any branch)
**Light gate (all paths):**
1. Backend: full pytest suite via the canonical venv (`backend/.venv` — never the global interpreter).
2. Frontend: production build (`npm run build` / `npx next build` in `frontend/`) — zero compile errors.
3. CI/CD Credentials: Check that required remote credentials (secrets/variables) are configured. For Firebase deployments:
   - Run `Remove-Item env:GITHUB_TOKEN; gh secret list --repo <repo-nwo>` (or `env -u GITHUB_TOKEN` in Bash) and verify `FIREBASE_SERVICE_ACCOUNT` is present.
   - Run `Remove-Item env:GITHUB_TOKEN; gh variable list --repo <repo-nwo>` and verify `FIREBASE_PROJECT_ID` is present.
   If any required deployment credentials are missing, STOP and warn the user.

**Full gate (paths B and C, additionally):**
4. Run **`/sudo-e2e`** — the real end-to-end suite (emulator-backed, seeded users). It must finish
   **green**. Its report is the promotion evidence; link it in the ledger row (Step 7).

Any failure → **STOP**. Summarize the failures, file/link the evidence, and suggest the lane
(`/sudo-quick-dev` or the ①②③ story loop). Do not proceed.


## Step 3 — Commit & push the development branch (all paths)
```powershell
git status
git add <explicit-file-paths>            # never blanket-add; verify staged imports have staged modules
git commit -m "<semantic-message>"
$env:GITHUB_TOKEN = ""; git push origin main_debug
```
**Path A ends here** → jump to Step 6 (deploy is optional for debug pushes) and Step 7.

## Step 4 — Promote to main (paths B and C — human approves every command)
### Path B: full merge
```powershell
git checkout main
$env:GITHUB_TOKEN = ""; git pull origin main
git merge main_debug --no-ff             # preserve history metadata
# 🛑 HUMAN GATE: summarize the commits + changed files first
$env:GITHUB_TOKEN = ""; git push origin main   # triggers frontend App Hosting CI/CD
```
### Path C: cherry-pick features
```powershell
git log --oneline main..main_debug       # identify the SHAs together
git checkout main
$env:GITHUB_TOKEN = ""; git pull origin main
git cherry-pick <sha-1> <sha-2>
# 🛑 HUMAN GATE: summarize the cherry-picked commits first
$env:GITHUB_TOKEN = ""; git push origin main
```

## Step 5 — Reconcile the branch model (path C always; path B sanity-check)
Cherry-picks mint NEW SHAs on `main`, leaving `main` "ahead" — reconcile immediately:
```powershell
git checkout main_debug
git merge main                            # main_debug now contains main again
$env:GITHUB_TOKEN = ""; git push origin main_debug
```
Path B: verify `git log --oneline main_debug..main` is empty (it should be, after a clean merge).
Always finish back on `main_debug` — the working tree stays on the dev line.

## Step 6 — Deploy backend (if backend changed — Cloud Run)
Run the project's backend deploy (see `@.agents/skills/deploy-backend/SKILL.md` for auth + pipeline
specs). Target the correct region/project (AviationChat: `us-east1` / `aviationchat`).

## Step 7 — Verify live + update the ledger
1. **Live check**: backend `/health` + the production frontend URL.
2. **Ledger**: add a row to `PROJECT_ROOT/_artifacts/INDEX.md` (and the home-base INDEX if run from
   the lobby) — what shipped, which path, gate evidence link (the `/sudo-e2e` report for B/C).
3. **Active context**: record the deployment in the project's `active-context.md`.

Optional additional input (project · path `debug|main|cherry` · SHAs): $ARGUMENTS
