# /sudo-push-e2e — Gate, Merge the Epic, Deploy

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never force-push

The one shipping command. It merges a finished **epic branch** (`epic/<slug>`) into **`main`** — live
production — and it **refuses to touch `main` until the full gate is green**. Invoking this command IS
Daniel's per-merge sign-off for the one epic it ships; the push-approval hook still prompts on the
final push, and that prompt is expected, not an error.

**Branch model (never violate):** `main` is the only long-lived branch. Epics integrate on short-lived
`epic/<slug>` branches and reach `main` only through this command. After the merge, the epic branch is
**deleted** — nothing accumulates. (The old `main_debug` integration branch was retired 2026-08-07;
any doc still describing "promotion from main_debug" predates that.)

## 🛑 MANDATORY RULES (Before You Start)
1. **The gate is not optional**: a red gate STOPS the command. Report what failed; do not "push anyway".
2. **Clear GITHUB_TOKEN on push/pull**: prefix with `$env:GITHUB_TOKEN = ""` (PowerShell) or
   `env -u GITHUB_TOKEN` (Bash) to prevent stale-session auth failures.
3. **On a deploying repo, a push to `main` IS a production deploy.** Know the rollback path (previous
   Cloud Run revision / previous hosting release) before you push, not after.

## Step 0 — Resolve the target project (FIRST — before anything else)
Bind the target per `.agents/rules/sudo-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override → `.agents/active-project.txt` → else **STOP and ask** — never guess, never operate on the
lobby. Set `PROJECT_ROOT` and **echo exactly** `Target: Projects/<name>`. All git/test commands below run
inside `PROJECT_ROOT`.

## Step 1 — Resolve the epic branch
From `$ARGUMENTS` (an `epic/<slug>` name) or by discovery:
```bash
git fetch origin
git branch -a --list '*epic/*'          # live epic branches, local + origin
```
- **Exactly one live epic branch** → that's the candidate; confirm it with Daniel by name.
- **Several** → show them with `git log --oneline main..<branch> | head` each and decide together.
- **None** → nothing to ship; if Daniel is pointing at a `chore/*` branch, this command can merge it
  with the **light gate** only (his direct ask IS that approval) — otherwise stop.

Sanity: every story on the board for this epic should be `done`. If stories are still open, STOP and
name them — `/sudo-merge-epic-workingtrees` or the story close-outs come first.

## Step 2 — Sync the epic branch with main (BEFORE gating)
Hotfixes can land on `main` mid-epic (incident lane). Absorb them first so the gate tests what will
actually ship:
```bash
git checkout epic/<slug>
git pull --ff-only origin epic/<slug>       # be current with the remote epic
git merge origin/main                        # absorb production; conflicts surface HERE, not on main
```
A conflict is a STOP-and-resolve-together, never a force. If this merge brought in changes, the gate
below runs on the post-merge tree — that is the point.

## Step 3 — Run the gate (on the epic branch)
**Light gate (always):**
1. Backend: full pytest suite via the canonical venv (`backend/.venv` — never the global interpreter).
2. Frontend: production build (`npm run build` / `npx next build` in `frontend/`) — zero compile errors.
3. CI/CD credentials: check what the deploy workflows actually reference. WIF-based workflows
   (workload_identity_provider in the yml) need no stored secrets; otherwise verify required secrets
   (`gh secret list`) and variables (`gh variable list`). Missing → STOP and warn.

**Full gate (any epic merge):**
4. Run **`/sudo-e2e`** — it must finish **green**. Its report is the promotion evidence; link it in the
   ledger row (Step 6).

Any failure → **STOP**. Summarize the failures, file/link the evidence, and suggest the lane
(`/sudo-quick-dev` or the ①②③ story loop). Do not proceed.

## Step 4 — Merge to main
```bash
git checkout main
$env:GITHUB_TOKEN = ""; git pull --ff-only origin main
git merge epic/<slug> --no-ff -m "merge: epic/<slug> -> main (gated: suite + build + e2e green)"
# 🛑 summarize the commits + changed files for Daniel before pushing
$env:GITHUB_TOKEN = ""; git push origin main    # hook prompts — this is the expected approval moment
```
The `--no-ff` merge commit records the epic as one reviewable unit on `main`'s first-parent history.
If the push is rejected (remote moved), STOP and report — never force.

## Step 5 — Watch the deploy + verify live
On repos with CI/CD, the push just fired the deploy workflows:
```bash
gh run list --limit 5                 # watch to completion — all must conclude success
```
Then verify live: backend `/health` (expect 200), the production frontend URL, and on Cloud Run
confirm the serving revision via the RELEASE track (other fields lie about what's serving). A failed
deploy is an incident: fix forward on a `chore/*` branch or roll back the revision — decide with
Daniel, immediately.

## Step 6 — Prune the epic branch + update the ledger
The epic shipped; its branch is done:
```bash
git branch -d epic/<slug>
$env:GITHUB_TOKEN = ""; git push origin --delete epic/<slug>
git rev-list --left-right --count main...origin/main    # must be 0 0
```
1. **Ledger**: add a row to `PROJECT_ROOT/_artifacts/INDEX.md` (and the home-base INDEX if run from
   the lobby) — what shipped, the merge SHA, gate evidence link (the `/sudo-e2e` report).
2. **Active context**: record the deployment in the project's `active-context.md`.
3. Finish standing on `main`, clean, `0 0` — state it per repo touched.

Optional additional input (project · epic branch): $ARGUMENTS
