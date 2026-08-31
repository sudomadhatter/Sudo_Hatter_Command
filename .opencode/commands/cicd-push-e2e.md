---
description: "The ONE shipping command — gate a finished epic branch (epic/<JIRA-KEY>-<slug>) and OPEN A PULL REQUEST into main, refusing until the full gate is green: enforcement suite + build + /cicd-e2e GREEN. It never merges: invoking it IS the operator's per-merge sign-off, and their click on Merge pull request is how that decision reaches GitHub. Absorbs origin/main into the epic first so conflicts never land on production. Re-invoked as --after-merge <KEY> it verifies the merge with plain git, watches the deploy, verifies live, prunes the epic branch and moves the epic ticket. Use when the user says 'ship it' / 'push the epic' / 'sudo push e2e'."
---

# /cicd-push-e2e — Gate the Epic, Open the PR, Deploy

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never force-push;
>   every branch and every commit carries the repo's Jira key (armed 2026-08-07)

The one shipping command. It gates a finished **epic branch** (`epic/<JIRA-KEY>-<slug>`) and opens a
**pull request** into **`main`** — live production — and it **refuses to open that PR until the full
gate is green**. Invoking this command IS the operator's per-merge sign-off for the one epic it ships.

⭐ **It never merges.** The gate runs here, on this machine, where the suites and the E2E harness
live; the merge happens on GitHub, on the operator's click. Re-invoke it as
`--after-merge <JIRA-KEY>` and it verifies that merge with plain git, watches the deploy, verifies
live, prunes the branch and moves the ticket (Step 4.5 onward).

⭐ **That sign-off is a DECISION, given in exactly one of three forms: the word `approved`, invoking
`/smh-close-task-merge-tree`, or invoking `/cicd-push-e2e`** (operator ruling, 2026-08-17). The
**decision to proceed is the sign-off**, and from that word on every step below is the ceremony's
and you run it — including Step 4's PR, which carries that same invocation as its authority, and the
whole `--after-merge` half, which is the agent's work and never a chore handed back.

**Branch model (never violate):** `main` is the only long-lived branch. Epics integrate on short-lived
`epic/<JIRA-KEY>-<slug>` branches and reach `main` only through this command. The key sits immediately
after the prefix and must be one of the repo's keys in `.agents/jira.conf` — the armed commit-msg hook
rejects commits carrying the wrong project's key. After the merge, the epic branch is **deleted** —
nothing accumulates. (The old `main_debug` integration branch was retired 2026-08-07; any doc still
describing "promotion from main_debug" predates that. Pre-Jira branches named plain `epic/<slug>` may
still exist — **rename one to carry its real key before it ships** (Step 1.5 refuses a keyless
branch: production would otherwise carry a merge no ticket joins to); never invent a key.)

## 🛑 MANDATORY RULES (Before You Start)
1. **The gate is not optional**: a red gate STOPS the command. Report what failed; do not "push anyway".
2. **Clear GITHUB_TOKEN on push/pull**: prefix with `$env:GITHUB_TOKEN = ""` (PowerShell) or
   `env -u GITHUB_TOKEN` (Bash) to prevent stale-session auth failures.
3. **On a deploying repo, the merge of this PR IS a production deploy.** Know the rollback path
   (previous Cloud Run revision / previous hosting release) before you open the PR, not after — the
   operator clicks on the strength of what you hand them.

## Step 0 — Resolve the target project (FIRST — before anything else)
Bind the target per `.agents/rules/smh-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override → `.agents/active-project.txt` → else **STOP and ask** — never guess, never operate on the
lobby. Set `PROJECT_ROOT` and **echo exactly** `Target: Projects/<name>`. All git/test commands below run
inside `PROJECT_ROOT`.

## Step 0.6 — Pin the ticket you MEAN (before any tool has answered anything)
```bash
EXPECTED_KEY=<the epic's Jira key>     # the ticket you MEAN, never one read back off a branch
```
A key derived from the branch you are about to resolve cannot disagree with it — pinning it here
is what makes Step 1.5's match a real comparison. No ticket → **STOP and ask.**

## Step 1 — Resolve the epic branch
From `$ARGUMENTS` (an `epic/<JIRA-KEY>-<slug>` name) or by discovery:
```bash
git fetch origin
git branch -a --list '*epic/*'          # live epic branches, local + origin
```
- **Exactly one live epic branch** → that's the candidate; Step 1.5 confirms it mechanically.
- **Several** → show them with `git log --oneline origin/main..<branch> | head` each and decide together.
- **None** → nothing to ship; if the operator is pointing at a `chore/<JIRA-KEY>-<slug>` branch, **the
  diff decides, not the ask**: Step 1.5 admits it here under the **light gate** only when it touches a
  **deployable** path (`backend/ frontend/ firebase/ functions/ mobile/ .github/`). Nothing deployable →
  it refuses, and that lane closes out through `/smh-close-task-merge-tree`, which owns the Task ceremony
  this door does not have. (Ruling 2026-08-07: chore branches carry their own ticket key too.)

Extract the epic's Jira key from the branch name — it drives Step 6.5. A branch with no key is a
pre-Jira epic: rename it first (see the branch model above), and never invent a key.

A chore lane that legitimately stays here **substitutes `chore/<JIRA-KEY>-<slug>` for
`epic/<JIRA-KEY>-<slug>`** in Step 2's checkout, Step 4's merge message and mint `--branch`, and both
Step 6 prune lines; Step 6.5 moves the chore ticket and the child-story sanity check does not apply.

Sanity: every story on the board for this epic should be `done`. If stories are still open, STOP and
name them — `/cicd-merge-epic-workingtrees` or the story close-outs come first.

## Step 1.5 — Pre-flight (mechanical — from the LOBBY, before anything is written)
```bash
BRANCH=<the branch Step 1 resolved>
python3 .agents/scripts/ship_preflight.py --repo "$PROJECT_ROOT" --branch "$BRANCH" \
        --expect-key "$EXPECTED_KEY"                                    # PC: `python`
```
⛔ **Standing in the lobby, not in `PROJECT_ROOT`** — a thin project carries no
`.agents/scripts/*.py`, so the same line run there is *No such file*, which reads as "no pre-flight
here". **Read the header before the verdict**: it echoes the branch the script actually resolved, and
a key that is not `$EXPECTED_KEY` means you are pointed at another lane. **Exit 2 → STOP.**

It answers shape · intent · clean-and-`0 0` · the lane. The clean check is the one that earns the
step: uncommitted work in the checkout makes Step 3 gate a tree Step 4's merge will not carry, so
what ships was never gated — and nothing else in this file would say so.

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
4. Run **`/cicd-e2e`** — it must finish **green**. Its report is the promotion evidence; link it in the
   ledger row (Step 6).

Any failure → **STOP**. Summarize the failures, file/link the evidence, and suggest the lane
(`/cicd-quick-dev` or the ①②③ story loop). Do not proceed.

## Step 4 — Push the gated tip, open the PR, and STOP
<!-- JIRA-HOOK: the epic's Jira tickets transition to Done at Step 6.5, after the merge is verified. -->

**The tip you push is the tree Step 3 just gated** — Step 2 absorbed `origin/main` into it, so the
commit going to the remote is exactly what went green. Push it, then open the pull request against
`main`:

```bash
cd "$PROJECT_ROOT" && env -u GITHUB_TOKEN git push origin epic/<JIRA-KEY>-<slug>
```

Then the PR, with the gate's own evidence in the body — the operator decides from what the gate
said, so the numbers travel with the request rather than living in a chat scrollback:

```bash
cd "$PROJECT_ROOT" && gh pr create --base main --head epic/<JIRA-KEY>-<slug> \
   --title "<JIRA-KEY> ship epic/<JIRA-KEY>-<slug>" --body-file <the evidence file>
```

The body carries four lines and nothing else: the backend suite total, the frontend build result,
`E2E GATE: GREEN <n>/<n>` with the report path (`frontend/playwright-report/`), and the epic's
ticket link. **The last line `gh` prints is the PR URL.** Print it and **STOP.**

**No `gh` on this machine?** Nothing is blocked — the tip is pushed, so the PR opens in a browser.
Build the URL from command output, never from memory:

```bash
cd "$PROJECT_ROOT" && git remote get-url origin      # -> the owner/repo
# https://github.com/<owner>/<repo>/compare/main...epic/<JIRA-KEY>-<slug>?expand=1
```

⛔ **STOP means stop.** Do not merge it another way, do not mint a token, do not offer to. **The
operator's decision to proceed is the sign-off — and their invocation this turn IS that decision, in
one of the ruling's three forms — while the click on *Merge pull request* is how it reaches
GitHub.** A link nobody has merged is not a merge running late; it is a merge that has not been
authorised. Waiting is correct behaviour, on every platform, on either machine.

**What guards the merge is on GitHub, not here — and how much guarding there is depends on the
repo.** A project that has filed its own server-side gate ticket publishes a required check, and
GitHub refuses the merge button until it is green. A project that has not yet is guarded by the
local gates this door already ran plus the operator's own reading of the PR. Either way **the token
is structurally absent, not bypassed**: a merge performed on GitHub's servers never touches a
machine here, so there is no local push for a hook to gate (SCC-118's finding, read forwards). If a
required check is present and red, **STOP** — never disable the ruleset to get past it.

> ⓘ **Why this road replaced the local merge (SCC-347).** The old Step 4 checked out `main`, merged
> `--no-ff`, minted a single-use token and pushed. That shape was already retired on the Task door
> (SCC-183) for a reason that applies here identically — a dozen hand-typed git commands in a shared
> checkout, each judged separately by the agent's permission layer, with the state left stranded
> halfway when one was denied. And the token it minted guarded the one road nobody was taking:
> measured 2026-08-31, `Projects/AGY_AVIATIONCHAT` `main` carried **no branch protection and no
> ruleset at all** (`gh api repos/{owner}/{repo}/branches/main/protection` → 404 *Branch not
> protected*), so a merge made through the GitHub UI — what a web or mobile session does — was
> guarded by nothing, while the local hook diligently guarded a push that had stopped happening.
> The PR road puts the operator's click where the authorisation belongs and leaves the server-side
> check as each project's own ticket to file.

## Step 4.5 — Resuming after the operator's click: `--after-merge <JIRA-KEY>`

When Step 4 handed back a link, this command is **paused, not finished**. Once the operator has
merged, re-invoke it to run everything below and nothing above:

```bash
/cicd-push-e2e --after-merge <JIRA-KEY>
```

⛔ **AND CHECK THAT THE DOOR YOU ARE READING IS THE CURRENT ONE.** This resume half runs after a
merge that may have changed this very file:

```bash
BEHIND=$(cd "$PROJECT_ROOT" && git rev-list --count HEAD..origin/main)
```

If `BEHIND` is not `0`, the text you are following may be the pre-merge copy — read the current one
(`git show origin/main:.agents/commands/cicd-push-e2e.md`) and follow that.

Verify the merge with **plain git** — no `gh` required, so this half works on any machine:

```bash
cd "$PROJECT_ROOT" && env -u GITHUB_TOKEN git fetch origin main
cd "$PROJECT_ROOT" && git merge-base --is-ancestor epic/<JIRA-KEY>-<slug> origin/main \
  || { echo "NOT merged yet — STOP"; exit 1; }
cd "$PROJECT_ROOT" && git log -1 --format=%s origin/main        # -> "Merge pull request #N from ..."
cd "$PROJECT_ROOT" && git checkout main
cd "$PROJECT_ROOT" && env -u GITHUB_TOKEN git pull --ff-only origin main
```

The PR number comes off that merge subject; the merge sha is `git rev-parse --short origin/main`.
Both go in Step 6.5's record.

⛔ If the ancestor check fails, **STOP** — nothing below runs, no ticket moves, no branch is pruned.
A close-out that reports `Done` on an unmerged PR is the same lie as one that reports it on a failed
merge. It is also why this door needs squash and rebase merges **disabled** on the repo: either
rewrites the commit, so the branch tip would not be an ancestor of `main` and a real landing would
read as a failure.

## Step 5 — Watch the deploy + verify live
The merge just fired the deploy workflows:
```bash
gh run list --limit 5                 # watch to completion — all must conclude success
```
Then verify live: backend `/health` (expect 200), the production frontend URL, and on Cloud Run
confirm the serving revision via the RELEASE track (other fields lie about what's serving). A failed
deploy is an incident: fix forward on a `chore/*` branch or roll back the revision — decide with the
operator, immediately.

## Step 6 — Prune the epic branch + update the ledger
The epic shipped; its branch is done:
```bash
cd "$PROJECT_ROOT" && git branch -d epic/<JIRA-KEY>-<slug>
cd "$PROJECT_ROOT" && env -u GITHUB_TOKEN git push origin --delete epic/<JIRA-KEY>-<slug>
git rev-list --left-right --count main...origin/main    # must be 0 0
```
1. **Ledger**: add a row to `PROJECT_ROOT/_artifacts/INDEX.md` (and the home-base INDEX if run from
   the lobby) — what shipped, the PR number, the merge SHA, gate evidence link (the `/cicd-e2e` report).
2. **Active context**: record the deployment in the project's `active-context.md`.
3. Finish standing on `main`, clean, `0 0` — state it per repo touched.

## Step 6.5 — Move the epic's Jira ticket
Skip if Step 1 found no key (pre-Jira epic, or a repo with no `.agents/jira.conf`). Otherwise the
merge IS the epic shipping, and the operator's invocation of this command IS the sign-off — record it:
```bash
acli jira workitem comment create --key <JIRA-KEY> \
  --body "Merged to main via PR #<N> at <merge-sha>. Gate: pytest + build + /cicd-e2e green (<evidence-link>). Deploy verified live."
acli jira workitem transition --key <JIRA-KEY> --status "Done" --yes
```
(`comment create` needs `--key`; `transition` too — `view` is the only one that takes the key
positionally. **`--yes` is not optional**: without it acli stops on an interactive confirm no
agent shell can answer, and this line shipped without it until SCC-113.) Full acli reference:
`.agents/rules/jira.md`. Transition the EPIC ticket only — child stories were already moved one-by-one at their
close-outs by `/cicd-close-story-merge-tree`. If Step 1's sanity check was honest, they are all `Done`
before this runs; if the transition fails because children are open, that is the sanity check telling
you it was skipped — go run the close-outs, do not force the epic.

Sprint/backlog placement stays the operator's — this step changes STATUS and posts evidence, nothing
else.

Optional additional input (project · epic branch · `--after-merge <JIRA-KEY>`): $ARGUMENTS
