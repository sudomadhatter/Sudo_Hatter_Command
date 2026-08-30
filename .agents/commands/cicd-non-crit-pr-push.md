---
description: Fast-track non-critical project changes (docs, memory files, notes, quick references) using the project's standing ticket and standing branch chore/<KEY>-standing-push directly to PR. Auto-provisions the Standing Push Ticket and persistent branch if they do not already exist in the project.
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
| `NOT-COMMAND-CENTRE` | **expected here — carry on to the path check below.** This IS a `cicd-*` lane |
| `LIGHT` | carry on |
| `LIGHT-VCS` | carry on — a **declared** git-hygiene action (`--no-file-changes`) that edits no files |
| `TASK` | **stop.** This touches product code or build tooling — use `/cicd-quick-dev` or the story loop |
| `TASK-LIGHT` | **stop.** Same road as `TASK` — a small measured toolkit edit still isn't this lane's work (SCC-302) |
| `HANDOFF` | **stop.** Deployable product change — route to `/cicd-push-e2e` |

<!-- twin-divergence: lane-verdict-not-command-centre — the smh- twin reads NOT-COMMAND-CENTRE as a STOP ("you are in a child project"); here it is the EXPECTED answer, because a child project is exactly where this lane runs. Same verdict, opposite instruction, on purpose (SCC-243). -->

⛔ **`NOT-COMMAND-CENTRE` is what you will get, every time, and it is NOT a refusal.** Its own reason
says *"Product work uses the cicd-\* lanes"* — and this **is** a `cicd-*` lane. A thin project carries
`.agents/rules/`, `.agents/skills/` and an `INDEX.md` but **no `.agents/commands/`**, and that absence
is the whole test `lane_qualify` applies. The centre-only scope is a settled operator ruling
(`.agents/scripts/INDEX.md:57`); do not ask for the script to be taught a project arm.

⛔ **But read what that costs, because it is the real hazard here.** That verdict is returned
**before a single path is examined** (`lane_qualify.py:107-112`), so in a child project the `TASK`
and `HANDOFF` rows above **cannot fire** — measured 2026-08-20: `--paths backend/api.py` and
`--paths docs/notes.md` return the identical answer against the same project. Step 0.5 alone
qualifies **nothing** here. The check below is the one that actually runs:

```bash
python3 -c "import sys; sys.path.insert(0, '.agents/scripts'); \
from task_preflight import PRODUCT_DIRS, CI_DIR; \
h=[p for p in sys.argv[1:] if p.startswith(PRODUCT_DIRS + (CI_DIR,))]; \
print('HANDOFF: ' + ', '.join(h) if h else 'no deployable path — carry on'); \
sys.exit(1 if h else 0)" <every path you will touch/commit>
```

*(PC: `python`, not `python3`. Run it from the command centre — the constants live there, not in the
thin project.)*

**Any output starting `HANDOFF:` and this lane is over** — route to `/cicd-push-e2e` and say so in
one line. ⛔ **The prefixes are IMPORTED, never re-typed here.** They are
`backend/` · `frontend/` · `firebase/` · `functions/` · `mobile/` (`task_preflight.PRODUCT_DIRS`)
plus `.github/` (`CI_DIR`), and a copy of that list in prose is a list that goes stale in silence —
`tests/test_lane_qualify.py` imports the constant and fails if any member goes unnamed above.

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
cd "$REPO" && git fetch origin main
# If switching branches with uncommitted work, stash first or checkout:
cd "$REPO" && git checkout "chore/${KEY}-standing-push" 2>/dev/null && cd "$REPO" && git pull origin main || \
cd "$REPO" && git checkout -B "chore/${KEY}-standing-push" origin/main
```

---

## Step 3 — Stage files explicitly

⛔ **Never use wildcard staging (`git add .`, `git add -A`, `git add -u`).**

```bash
cd "$REPO" && git add <explicit/path/1> <explicit/path/2>
cd "$REPO" && git diff --cached --stat
```

---

## Step 4 — Commit with project Jira prefix

Commit the staged changes with the project's standing key `<KEY>` and `[sop-ok]`:

```bash
cd "$REPO" && git commit -m "${KEY} <summary of changes> [sop-ok]"
```

---

## Step 5 — Push to GitHub

Push to `origin/chore/<KEY>-standing-push`:

```bash
cd "$REPO" && env -u GITHUB_TOKEN git push origin "chore/${KEY}-standing-push" --force-with-lease
```

---

## Step 6 — Open the Pull Request

Open the Pull Request targeting `main`:

```bash
gh pr create --repo "$(cd "$REPO" && git remote get-url origin)" --base main --head "chore/${KEY}-standing-push" \
  --title "${KEY} <summary of changes>" --body "${KEY}: Routine non-critical project update."
```

---

## Step 7 — Verify main-write-gate Check

Check GitHub Actions CI status for the PR:

```bash
gh pr checks <PR-number> --repo "$(cd "$REPO" && git remote get-url origin)"
```

Wait until `main-write-gate` reports `pass` (🟢).

---

## Step 8 — Report PR Link

Print the PR link and status back to the operator:
- **Project:** `$(basename "$REPO")`
- **Standing Ticket:** `<KEY>`
- **PR URL:** `https://github.com/<owner>/<repo>/pull/<number>`
- **Status:** `main-write-gate passed` (🟢)

---

## Step 9 — Return checkout to main

Immediately switch the child project's checkout back to `main` so the workspace is not left on the standing branch:

```bash
cd "$REPO" && git checkout main
```

---

## Step 10 — Pull landed changes after operator merge

Once the operator merges the PR on GitHub, pull the merge commit into local `main`:

```bash
cd "$REPO" && git pull origin main
```

Optional additional input (target project, summary, or file paths): $ARGUMENTS

