---
description: Fast-track non-critical command center changes (docs, memory files, notes, quick references) using standing ticket SCC-186 (or...
platforms: [opencode, antigravity, claude, codex]
---

# /smh-non-crit-pr-push — Standing Non-Critical PR Push (SCC-186)

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), every commit carries Jira key `SCC-186` (or the project's standing key)
> - `.agents/rules/jira.md` — standing ticket `SCC-186` stays open forever; its Dev Record is the running log
> - `.agents/rules/000-PLAN-FIRST-GATE.md` — non-critical documentation and note updates are exempt from implementation plans
> - `_my_resources/_quick_reference/quick_push_git_main` — reference procedure for standing pushes

**Why this exists.** Operator ruling 2026-08-16 on SCC-186: *"I dont want another ticket at all, this is never ending."* One standing ticket (`SCC-186`) and standing branch (`chore/SCC-186-standing-push`) serve routine command-centre upkeep that has no risk and needs no ticket of its own: doc and index edits, memory files, `_artifacts` INDEX rows, notes, and quick references.

---

## Step 0 — Qualify. Confirm the changes are non-critical.

⛔ **Verify all paths before proceeding.**

```bash
REPO=$(git rev-parse --show-toplevel) && echo "Repo: $(basename "$REPO")"
python3 .agents/scripts/lane_qualify.py --repo "$REPO" --paths <every path you will touch/commit>
```

*(PC: `python`, not `python3`.)*

| Verdict | What you do |
|---|---|
| `LIGHT` | carry on |
| `LIGHT-VCS` | carry on — a **declared** git-hygiene action (`--no-file-changes`) that edits no files |
| `TASK` | **stop.** This touches toolkit/code paths (`.agents/**`, `tests/**`) — use `/smh-quick-dev` or standard task lane |
| `TASK-LIGHT` | **stop.** Same road as `TASK` — `/smh-quick-dev` — but the measured blast radius is small, so that lane may right-size its ceremony (SCC-302) |
| `HANDOFF` | **stop.** Deployable code — route to product lane (`/cicd-push-e2e`) |
| `NOT-COMMAND-CENTRE` | **stop.** You are in a child project — use `/cicd-non-crit-pr-push` |

⛔ **All five, because the script returns five** (SCC-243). A verdict the table does not list is a
verdict this command has no instruction for, and the agent then answers by judgement — which is the
one thing putting the question in a script was meant to prevent. `tests/test_lane_qualify.py` fails
if `lane_qualify.VERDICTS` ever grows a sixth and this table does not.

---

## Step 1 — Resolve or auto-provision the Standing Push Ticket

Read the primary Jira prefix from `.agents/jira.conf` (e.g. `SCC`):

```bash
PROJ=$(grep -E '^JIRA_KEYS=' .agents/jira.conf | cut -d'"' -f2 | awk '{print $1}')
echo "Project Key Prefix: $PROJ"
```

Search for an existing open Standing Push Ticket (default `SCC-186` in lobby):
```bash
KEY=$(acli jira workitem search --jql "project = $PROJ AND summary ~ 'Standing Push' AND status != Done" --fields "key" --limit 1 | grep -oE "$PROJ-[0-9]+" | head -n 1)
```

If no ticket is found, **auto-mint it immediately**:
```bash
if [ -z "$KEY" ]; then
  echo "No Standing Push Ticket found for $PROJ. Minting one now..."
  CREATE_OUT=$(acli jira workitem create --project "$PROJ" --type Task \
    --summary "Standing Push Ticket" \
    --description "STANDING LANE. Never closed. This is the Jira key for routine command-centre upkeep that has no risk and needs no ticket of its own: doc and index edits, memory files, _artifacts INDEX rows, quick references, typo and link fixes." \
    --label "standing-push")
  KEY=$(echo "$CREATE_OUT" | grep -oE "$PROJ-[0-9]+" | head -n 1)
fi
echo "Using Standing Ticket: $KEY"
```

---

## Step 2 — Sync standing branch with latest main

Switch to or reset the standing branch `chore/<KEY>-standing-push` based on latest `origin/main`:

```bash
git fetch origin main
# If switching branches with uncommitted work, stash first or checkout:
git checkout "chore/${KEY}-standing-push" 2>/dev/null && git pull origin main || \
git checkout -B "chore/${KEY}-standing-push" origin/main
```

---

## Step 3 — Stage files explicitly

⛔ **Never use wildcard staging (`git add .`, `git add -A`, `git add -u`).**

```bash
git add <explicit/path/1> <explicit/path/2>
git diff --cached --stat
```

---

## Step 4 — Commit with Jira prefix

Commit the staged changes with the standing key `<KEY>` and `[sop-ok]` (since non-critical changes don't alter usage surfaces):

```bash
git commit -m "${KEY} <summary of changes> [sop-ok]"
```

---

## Step 5 — Push to GitHub

Push to `origin/chore/<KEY>-standing-push`:

```bash
env -u GITHUB_TOKEN git push origin "chore/${KEY}-standing-push" --force-with-lease
```

---

## Step 6 — Open the Pull Request

Open the Pull Request targeting `main`:

```bash
gh pr create --base main --head "chore/${KEY}-standing-push" --title "${KEY} <summary of changes>" --body "${KEY}: Routine non-critical update."
```

---

## Step 7 — Verify main-write-gate Check

Check GitHub Actions CI status for the PR:

```bash
gh pr checks <PR-number>
```

Wait until `main-write-gate` reports `pass` (🟢).

---

## Step 8 — Report PR Link

Print the PR link and status back to the operator:
- **PR URL:** `https://github.com/<owner>/<repo>/pull/<number>`
- **Status:** `main-write-gate passed` (🟢)
- **Standing Ticket:** `<KEY>`

---

## Step 9 — Return checkout to main

Immediately switch the working checkout back to `main` so the workspace is not left on the standing branch:

```bash
git checkout main
```

---

## Step 10 — Pull landed changes after operator merge

Once the operator merges the PR on GitHub, pull the merge commit into local `main`:

```bash
git pull origin main
```

Optional additional input (summary or specific file paths): $ARGUMENTS

