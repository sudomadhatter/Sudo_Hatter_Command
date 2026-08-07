# /sudo-push-e2e — Gate, Merge the Epic, Deploy

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never force-push;
>   every branch and every commit carries the repo's Jira key (armed 2026-08-07)

The one shipping command. It merges a finished **epic branch** (`epic/<JIRA-KEY>-<slug>`) into
**`main`** — live production — and it **refuses to touch `main` until the full gate is green**.
Invoking this command IS Daniel's per-merge sign-off for the one epic it ships; the push-approval hook
still prompts on the final push, and that prompt is expected, not an error.

**Branch model (never violate):** `main` is the only long-lived branch. Epics integrate on short-lived
`epic/<JIRA-KEY>-<slug>` branches and reach `main` only through this command. The key sits immediately
after the prefix and must be one of the repo's keys in `.agents/jira.conf` — the armed commit-msg hook
rejects commits carrying the wrong project's key. After the merge, the epic branch is **deleted** —
nothing accumulates. (The old `main_debug` integration branch was retired 2026-08-07; any doc still
describing "promotion from main_debug" predates that. Pre-Jira branches named plain `epic/<slug>` may
still exist — ship them as-is; never invent a key.)

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
From `$ARGUMENTS` (an `epic/<JIRA-KEY>-<slug>` name) or by discovery:
```bash
git fetch origin
git branch -a --list '*epic/*'          # live epic branches, local + origin
```
- **Exactly one live epic branch** → that's the candidate; confirm it with Daniel by name.
- **Several** → show them with `git log --oneline main..<branch> | head` each and decide together.
- **None** → nothing to ship; if Daniel is pointing at a `chore/<JIRA-KEY>-<slug>` branch, this command
  can merge it with the **light gate** only (his direct ask IS that approval) — otherwise stop.
  (Ruling 2026-08-07: chore branches carry their own ticket key too.)

Extract the epic's Jira key from the branch name — it drives Step 6.5. A branch with no key is a
pre-Jira epic: note that, skip Step 6.5, and never invent a key.

Sanity: every story on the board for this epic should be `done`. If stories are still open, STOP and
name them — `/sudo-merge-epic-workingtrees` or the story close-outs come first.

## Step 2 — Sync the epic branch with main (BEFORE gating)
Hotfixes can land on `main` mid-epic (incident lane). Absorb them first so the gate tests what will
actually ship:
```bash
git checkout epic/<JIRA-KEY>-<slug>
git pull --ff-only origin epic/<JIRA-KEY>-<slug>       # be current with the remote epic
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
git merge epic/<JIRA-KEY>-<slug> --no-ff -m "merge: epic/<JIRA-KEY>-<slug> -> main (gated: suite + build + e2e green)"
# 🛑 summarize the commits + changed files for Daniel before pushing
$env:GITHUB_TOKEN = ""; git push origin main    # hook prompts — this is the expected approval moment
```
The `--no-ff` merge commit records the epic as one reviewable unit on `main`'s first-parent history,
and because the branch name (with its key) is in the message, Jira links the merge commit to the epic
ticket automatically. (The commit-msg hook exempts merges — the key riding in the branch name is what
makes the join work.) If the push is rejected (remote moved), STOP and report — never force.

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
git branch -d epic/<JIRA-KEY>-<slug>
$env:GITHUB_TOKEN = ""; git push origin --delete epic/<JIRA-KEY>-<slug>
git rev-list --left-right --count main...origin/main    # must be 0 0
```
1. **Ledger**: add a row to `PROJECT_ROOT/_artifacts/INDEX.md` (and the home-base INDEX if run from
   the lobby) — what shipped, the merge SHA, gate evidence link (the `/sudo-e2e` report).
2. **Active context**: record the deployment in the project's `active-context.md`.
3. Finish standing on `main`, clean, `0 0` — state it per repo touched.

## Step 6.5 — Move the epic's Jira ticket
Skip if Step 1 found no key (pre-Jira epic, or a repo with no `.agents/jira.conf`). Otherwise the
merge IS the epic shipping, and Daniel's invocation of this command IS the sign-off — record it:
```bash
acli jira workitem comment create --key <JIRA-KEY> \
  --body "Merged to main at <merge-sha> via /sudo-push-e2e. Gate: pytest + build + /sudo-e2e green (<evidence-link>). Deploy verified live."
acli jira workitem transition --key <JIRA-KEY> --status "Done"
```
(`comment create` needs `--key`; `transition` too — `view` is the only one that takes the key
positionally.) Full acli reference: `.agents/rules/jira.md`. Transition the EPIC ticket only — child stories were already moved one-by-one at their
close-outs by `/sudo-update-sprint-memory`. If Step 1's sanity check was honest, they are all `Done`
before this runs; if the transition fails because children are open, that is the sanity check telling
you it was skipped — go run the close-outs, do not force the epic.

Sprint/backlog placement stays Daniel's — this step changes STATUS and posts evidence, nothing else.

Optional additional input (project · epic branch): $ARGUMENTS
