---
description: Fast-track non-critical project changes (docs, memory files, notes, quick references) using the project's standing ticket and...
platforms: [opencode, antigravity, claude, codex]
---

# /cicd-non-crit-pr-push — Standing Non-Critical PR Push (Child Projects)

> **Rules in force for this command:**
> - `.agents/rules/smh-target-resolution.md` — operates on exactly ONE project under `Projects/<name>` (e.g. `Projects/AGY_AVIATIONCHAT`), never the lobby
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), every commit carries the project's Jira key
> - `.agents/rules/jira.md` — the project's Standing Push Ticket stays open forever; its Dev Record is the running log
> - `.agents/rules/000-PLAN-FIRST-GATE.md` — non-critical documentation and note updates are exempt from implementation plans

**Why this exists.** Routine upkeep in child projects (doc/index edits, memory files, `_artifacts` INDEX rows, notes, and quick references) has no risk and should not require creating a brand-new Jira ticket and full development ceremony every time. Each child project maintains one permanent Standing Push Ticket (e.g. `AVCH-XX`) and one reusable branch (`chore/<KEY>-standing-push`).

---

## Step 0 — Resolve the target project (FIRST)

Bind the target project per `.agents/rules/smh-target-resolution.md` §STD + §BIND:
```bash
# Target repository path (e.g. Projects/AGY_AVIATIONCHAT)
REPO=$(cd "<target-project-path>" && git rev-parse --show-toplevel)
echo "Target Repo: $(basename "$REPO")"
```

---

## Step 0.5 — Qualify. Confirm the changes are non-critical.

⛔ **Verify all paths before proceeding.**

```bash
python3 .agents/scripts/lane_qualify.py --repo "$REPO" --paths <every path you will touch/commit>
```

*(PC: `python`, not `python3`.)*

| Verdict | What you do |
|---|---|
| `LIGHT` | carry on |
| `TASK` | **stop.** This touches product code or build tooling — use `/cicd-quick-dev` or the story loop |
| `HANDOFF` | **stop.** Deployable product change — route to `/cicd-push-e2e` |

---

## Step 1 — Resolve or auto-provision the project's Standing Push Ticket

Read the project's primary Jira prefix from `$REPO/.agents/jira.conf` (e.g. `AVCH`):

```bash
PROJ=$(grep -E '^JIRA_KEYS=' "$REPO/.agents/jira.conf" | cut -d'"' -f2 | awk '{print $1}')
echo "Project Key Prefix: $PROJ"
```

Search for an existing open Standing Push Ticket:
```bash
KEY=$(acli jira workitem search --jql "project = $PROJ AND summary ~ 'Standing Push' AND status != Done" --fields "key" --limit 1 | grep -oE "$PROJ-[0-9]+" | head -n 1)
```

If no ticket is found, **auto-mint it immediately**:
```bash
if [ -z "$KEY" ]; then
  echo "No Standing Push Ticket found for $PROJ. Minting one now..."
  CREATE_OUT=$(acli jira workitem create --project "$PROJ" --type Task \
    --summary "Standing Push Ticket" \
    --description "STANDING LANE. Never closed. This is the Jira key for routine upkeep in this project that has no risk and needs no ticket of its own: doc and index edits, memory files, _artifacts INDEX rows, quick references, typo and link fixes." \
    --label "standing-push")
  KEY=$(echo "$CREATE_OUT" | grep -oE "$PROJ-[0-9]+" | head -n 1)
fi
echo "Using Standing Ticket: $KEY"
```

---

## Step 2 — Sync standing branch with latest main

Check out or reset the persistent branch `chore/<KEY>-standing-push` based on the project's latest `origin/main`:

```bash
git -C "$REPO" fetch origin main
# If switching branches with uncommitted work, stash first or checkout:
git -C "$REPO" checkout "chore/${KEY}-standing-push" 2>/dev/null && git -C "$REPO" pull origin main || \
git -C "$REPO" checkout -B "chore/${KEY}-standing-push" origin/main
```

---

## Step 3 — Stage files explicitly

⛔ **Never use wildcard staging (`git add .`, `git add -A`, `git add -u`).**

```bash
git -C "$REPO" add <explicit/path/1> <explicit/path/2>
git -C "$REPO" diff --cached --stat
```

---

## Step 4 — Commit with project Jira prefix

Commit the staged changes with the project's standing key `<KEY>` and `[sop-ok]`:

```bash
git -C "$REPO" commit -m "${KEY} <summary of changes> [sop-ok]"
```

---

## Step 5 — Push to GitHub

Push to `origin/chore/<KEY>-standing-push`:

```bash
env -u GITHUB_TOKEN git -C "$REPO" push origin "chore/${KEY}-standing-push" --force-with-lease
```

---

## Step 6 — Open the Pull Request

Open the Pull Request targeting `main`:

```bash
gh pr create --repo "$(git -C "$REPO" remote get-url origin)" --base main --head "chore/${KEY}-standing-push" \
  --title "${KEY} <summary of changes>" --body "${KEY}: Routine non-critical project update."
```

---

## Step 7 — Verify main-write-gate Check

Check GitHub Actions CI status for the PR:

```bash
gh pr checks <PR-number> --repo "$(git -C "$REPO" remote get-url origin)"
```

Wait until `main-write-gate` reports `pass` (🟢).

---

## Step 8 — Report PR Link

Print the PR link and status back to the operator:
- **Project:** `$(basename "$REPO")`
- **Standing Ticket:** `<KEY>`
- **PR URL:** `https://github.com/<owner>/<repo>/pull/<number>`
- **Status:** `main-write-gate passed` (🟢)

Optional additional input (target project, summary, or file paths): $ARGUMENTS
