---
description: Fast-track non-critical command center changes (docs, memory files, notes, quick references) using standing ticket SCC-186 and...
platforms: [opencode, antigravity, claude, codex]
---

# /smh-non-crit-pr-push — Standing Non-Critical PR Push (SCC-186)

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), every commit carries Jira key `SCC-186`
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
| `TASK` | **stop.** This touches toolkit/code paths (`.agents/**`, `tests/**`) — use `/smh-quick-dev` or standard task lane |
| `HANDOFF` | **stop.** Deployable code — route to product lane (`/cicd-push-e2e`) |
| `NOT-COMMAND-CENTRE` | **stop.** Standing ticket SCC-186 is for the command centre only |

---

## Step 1 — Sync standing branch with latest main

Switch to or reset the standing branch `chore/SCC-186-standing-push` based on latest `origin/main`:

```bash
git fetch origin main
# If switching branches with uncommitted work, stash first or checkout:
git checkout chore/SCC-186-standing-push && git pull origin main
# Or create/reset if starting fresh:
git checkout -B chore/SCC-186-standing-push origin/main
```

---

## Step 2 — Stage files explicitly

⛔ **Never use wildcard staging (`git add .`, `git add -A`, `git add -u`).**

```bash
git add <explicit/path/1> <explicit/path/2>
git diff --cached --stat
```

---

## Step 3 — Commit with SCC-186 prefix

Commit the staged changes with the standing key `SCC-186` and `[sop-ok]` (since non-critical changes don't alter usage surfaces):

```bash
git commit -m "SCC-186 <summary of changes> [sop-ok]"
```

---

## Step 4 — Push to GitHub

Push to `origin/chore/SCC-186-standing-push`:

```bash
env -u GITHUB_TOKEN git push origin chore/SCC-186-standing-push --force-with-lease
```

---

## Step 5 — Open the Pull Request

Open the Pull Request targeting `main`:

```bash
gh pr create --base main --head chore/SCC-186-standing-push --title "SCC-186 <summary of changes>" --body "SCC-186: Routine non-critical update."
```

---

## Step 6 — Verify main-write-gate Check

Check GitHub Actions CI status for the PR:

```bash
gh pr checks <PR-number>
```

Wait until `main-write-gate` reports `pass` (🟢).

---

## Step 7 — Report PR Link

Print the PR link and status back to the operator:
- **PR URL:** `https://github.com/<owner>/<repo>/pull/<number>`
- **Status:** `main-write-gate passed` (🟢)
- **Standing Ticket:** `SCC-186`

Optional additional input (summary or specific file paths): $ARGUMENTS
