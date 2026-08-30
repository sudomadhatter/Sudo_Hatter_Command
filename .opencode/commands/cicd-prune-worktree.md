---
description: The story lane's disk utility — it MOVES NO CODE. Verify a story branch has already been merged into its epic branch, preserve any uncommitted work, then prune EVERY stale worktree on disk and delete both local and remote (GitHub) branches. Sweeps all trees, not just the named slug. Called by /cicd-close-story-merge-tree and by /cicd-merge-epic-workingtrees; type it yourself only when a cleanup was skipped or failed.
---

# /cicd-prune-worktree — Prune a Merged Worktree & Its Branches

> **Named for its job (SCC-210).** Its old name read like a close-out; this is not one. It verifies a landing that
> has already happened and then cleans up. The command that closes a story out is
> **`/cicd-close-story-merge-tree`**, and this is its last step.

Safely clean up story worktrees and their git branches (`claude/<JIRA-KEY>-<story-slug>`) after a story has landed on
its epic branch (`epic/<JIRA-KEY>-<slug>`).

**Order is load-bearing and the numbering enforces it: SWEEP → PRESERVE → UNLINK → REMOVE → DELETE BRANCH.**
Every out-of-order variant of this command has destroyed something. Do not reorder, and do not skip a step
because the tree "looks empty" — every incident below started with a tree that looked empty.

## Step 0 — Resolve target project and story slug
1. **Target Project** — bind per `.agents/rules/smh-target-resolution.md` §STD: self fast-path →
   `$ARGUMENTS` override → `.agents/active-project.txt` → else ask the operator. Set `PROJECT_ROOT`.
2. **Target Story Slug**:
   - If `$ARGUMENTS` provides a story slug or branch name (e.g. `21-12-fail-closed-admin-roles` or `claude/21-12-fail-closed-admin-roles`), strip any `claude/` or `.claude/worktrees/` prefix to extract `<story-slug>`.
   - Otherwise, if standing inside a worktree `.claude/worktrees/<story-slug>`, extract `<story-slug>` from current working directory.
   - Otherwise, read the active story slug from `PROJECT_ROOT/_bmad-output/implementation-artifacts/sprint-status.yaml`.

3. **Story id and Jira key** — Step 0.6's preflight **requires** `--story` and `--expect-key`, and neither
   falls out of a slug: `21-12-fail-closed-admin-roles` carries an id but no key, and the `claude/` strip in
   step 2 above discards the only place a key would have been. Resolve both, in this order:
   - **Handed to you by the caller** (`/cicd-close-story-merge-tree` Step 5 and
     `/cicd-merge-epic-workingtrees` both bind them) → use those, and echo that you did.
   - **Standalone** → read `jira_key:` from the story file's frontmatter, and the id from the same file
     (`_bmad/bmm/stories/story-<id>-*.md` under `PROJECT_ROOT`).
   - **Neither resolves** → **STOP and ask** which story this is. Do **not** invent a key and do **not** drop
     the flag: an invented key makes the intent check answer about a lane that does not exist, and a dropped
     one is `error: the following arguments are required: --expect-key`, exit 2 — which is also this script's
     BLOCKED code, so a usage mistake reads as a blocked lane.

Echo `Target: Projects/<name> | Story: <story-slug> | <id> | <JIRA-KEY>` before proceeding.

## Step 0.6 — Preflight first (fast pre-check — it does NOT replace the gates below)

```bash
python3 .agents/scripts/closeout_preflight.py --story <id> --project <PROJECT> \
       --expect-key <JIRA-KEY> --branch <name>
```

**Pass `--expect-key` and `--branch` explicitly, and check the target it echoes before reading its result.**
Since SCC-210 the key check is mechanical rather than a habit: the resolved branch must carry the key you named,
or the preflight errors — the same guard `task_preflight.py` has required since the 2026-08-09 failure. A verdict
carrying **STALE** was computed against the last fetch, not the remote — the line names which remedy applies
(a failed fetch is an uplink to fix; `--no-fetch` is a flag to drop, and only if you passed it), so fix what it
names before removing anything. This command
runs when worktrees are open by definition, and that is exactly when `cwd` stops matching intent — the
script walks up from `cwd` for `.git` and defaults to that repo's `HEAD`, so a sibling lane that moved the
shared checkout silently becomes the target, with every check reported honestly about the wrong branch
(`worktree-per-story.md` → *"`cwd` is not intent"*). Resolved slug ≠ the slug you echoed in Step 0 →
**STOP**.

One call answers Steps 1 and 1.6's questions mechanically: is the branch an ancestor of
the epic branch, is every repo `0/0` and clean, and is each registered worktree LIVE / LOST (registered,
no directory) / HUSK (directory, no `.git` — the state that blocks the next `worktree add`).
**Exit 2 → stop here.** A `landing was NOT verified` warning is not a pass — resolve it before anything
is removed.

⛔ **It does not authorize deletion.** The preflight reads; it never writes. Steps 1.7 (authorization),
2 (preserve uncommitted work) and 3a (unlink every reparse point BEFORE any recursive remove) are
data-loss gates the script does not cover — run them in full, exactly as written. Deleting through a
junction destroys the shared `backend/.venv` and `node_modules` **targets**, not just the links.

## Step 1 — Safety Verification Gate (MANDATORY)
In `PROJECT_ROOT`:
```bash
# 1 · Fetch latest remote refs
Remove-Item Env:\GITHUB_TOKEN -ErrorAction Ignore; git fetch origin

# 2 · Resolve the story's epic branch (exactly one live epic/* is the normal case)
git for-each-ref --format='%(refname:short)' 'refs/remotes/origin/epic/*'

# 3 · Verification check: confirm story branch has landed on origin/epic/<JIRA-KEY>-<slug>
git merge-base --is-ancestor claude/<JIRA-KEY>-<story-slug> origin/epic/<JIRA-KEY>-<slug>
```

- **Exit code 0**: the branch is fully merged into `origin/epic/<JIRA-KEY>-<slug>`. Proceed to Step 1.6.
- **Non-zero**: **STOP IMMEDIATELY!**
  Print: `❌ Refusing to delete: claude/<JIRA-KEY>-<story-slug> is NOT fully merged into origin/epic/<JIRA-KEY>-<slug>.`
  Instruct: `Land the story first using /cicd-close-story-merge-tree or git merge to origin/epic/<JIRA-KEY>-<slug>.`

**Record this result per branch.** Step 5 deletes branches, and it may ONLY delete a branch that passed this
check. A tree can be safe to remove while its branch is not safe to delete — those are different questions.

> *(The old Step 1.5 shared-checkout reconcile died with `main_debug` on 2026-08-07 — the shared checkout
> stands on `main` and only moves when an epic merges via `/cicd-push-e2e`. Nothing to backstop here.)*

## Step 1.6 — SWEEP every worktree on disk FIRST (before removing anything)

⚠️ **This runs BEFORE any removal, and it covers LIVE worktrees, not just orphans.** The slug you were
invoked with is not the scope — the disk is. A registered worktree belonging to some *other* story is
invisible to every slug-scoped step below, and a stale one is precisely what makes an agent "pick up the
wrong tree".

Two failure modes this catches, both observed **2026-07-27** in a single run where the target slug's own
tree was perfectly clean:
- a **dead 21.5 husk** — invisible to `git worktree list` because a previous close-out pruned the
  registration but left the folder, still holding live junctions to the shared `.venv` and both
  `node_modules`; it sat in the IDE side panel for a full day.
- a **live 21.4 tree holding 1,197 uncommitted lines** — a story file, an implementation plan and both
  red-phase test tiers from a `/cicd-write-story-tests` run that never committed.

```powershell
$root = "PROJECT_ROOT/.claude/worktrees"
if (Test-Path $root) {
  # Registered worktree paths, normalised for comparison.
  $known = @((git worktree list --porcelain) -match '^worktree ' -replace '^worktree ','' |
             ForEach-Object { $_.Replace('/','\').TrimEnd('\') })
  foreach ($d in @(Get-ChildItem $root -Force -Directory -EA SilentlyContinue)) {
    # NOTE: $d, not $_ — an inner Where-Object rebinds $_ to ITS OWN item. The original version of
    # this sweep wrote `$known | Where-Object { ... "*$($_.Name)*" }`, which compared each path
    # string against itself; strings have no .Name, so the pattern collapsed to "**", every
    # directory looked known, and the sweep printed NOTHING while a real husk sat on disk.
    $isKnown = @($known | Where-Object { $_ -ieq $d.FullName.TrimEnd('\') }).Count -gt 0
    $hasGit  = Test-Path (Join-Path $d.FullName '.git')
    $dirty   = if ($hasGit) { @(cd $d.FullName && git status --short).Count } else { 'n/a' }
    $state   = if (-not $hasGit) { 'HUSK' } elseif ($isKnown) { 'LIVE' } else { 'LOST' }
    Write-Output "$state  $($d.Name)  (registered=$isKnown, .git=$hasGit, uncommitted=$dirty)"
  }
}
```

⛔ **Never assign to a lowercase alias of an outer variable** (`$p = Join-Path $P …`). PowerShell variable
names are **case-insensitive**, so `$p` and `$P` are ONE variable — a loop written that way overwrites its
own root path on the first iteration and every later check silently reads a bogus path. On 2026-07-27 that
produced a false "shared assets MISSING" report that briefly looked like the delete had eaten `.venv`.

**Classify every row and carry the list into the steps below:**

| State | Meaning | Action |
|---|---|---|
| **HUSK** | no `.git` — dead folder from an earlier bad close-out | Step 3 unlink-then-delete. Step 2 does not apply (git cannot read it) — say so, don't skip silently. |
| **LOST** | has `.git` but unregistered — a live worktree git lost track of | **STOP and report.** Never delete. |
| **LIVE**, uncommitted = 0 | registered, clean | Remove **only if** its branch passed Step 1. Otherwise leave it and name it. |
| **LIVE**, uncommitted > 0 | registered, holds unsaved work | **Step 2 FIRST.** Preserve, push, then remove. Never `--force` past it. |

Report every directory found, its state, and what you did with it — **including the ones you left alone and
why**. A tree you decided to keep is a decision, and an unreported decision reads as an oversight.

## Step 1.7 — Close-out authorization gate (what makes cleanup APPROVED)

**A worktree exists only while a story is being worked.** Cleaning one up is authorized by the story being
**closed out** — not merely merged. Step 1 proved the code landed; that is a different question from
whether the operator finished the story. This step answers the second one, and it is what replaces
deference with a lookup: if the gate passes, **act — do not ask.**

This also closes a failure you have already been bitten by: **debug-2.2 sat merged-but-not-closed-out for
five days** while every planning surface recommended rebuilding it. Under merge-base alone its tree would
have been pruned, erasing the last on-disk hint that the close-out never ran.

Per tree, in order — first match wins:

1. **Story file frontmatter reads `Status: done`** (`_bmad/bmm/stories/<story>.md`; grep BOTH dot and dash
   forms of the id) → **AUTHORIZED.** A human's word is behind that write — dev only ever sets `review`
   (`story-status-flip-contract`).
   ⛔ **But `done` no longer implies the code LANDED, and this gate cannot see the difference (SCC-210).**
   The flip is written by `/cicd-update-sprint-memory`, which is invocable on its own and performs no
   landing, no ticket write and no prune — so a lane can legitimately read `done` with its code still only
   on the local `claude/*` branch. Before this rebalance the same command also landed and moved the ticket,
   which is what made `done` a proxy for "closed out"; it is not one now. So when this gate authorises on
   `Status: done` **alone**, confirm the landing yourself before removing anything — the branch is an
   ancestor of its epic branch (`git merge-base --is-ancestor`), which is exactly what Step 2's merge check
   below asks. Authorisation says a human meant to close this; the merge check says the code survived it.
2. **Board key exists in `sprint-status.yaml` and reads `done`** → corroborated. Say so.
3. **Board key ABSENT** → check the CHANGE LOG for the slug.
   - Found → **AUTHORIZED**, and **state in the report that no board key exists.** Standalone quick-dev
     tickets legitimately have none (prior art: `security-profile-idor-fix`, `gemini-key-pytest-env`), but
     a missing key is otherwise indistinguishable from the debug-2.2 failure, and a missing key fires no
     drift check anywhere. Naming it is the only thing that surfaces it.
   - Not found → **STOP** (below).
4. **Status is `review` / `in-progress` / `backlog`, or nothing corroborates** → **STOP.** Print:
   `❌ <slug> is merged but not closed out (status: <x>). Run /cicd-close-story-merge-tree first, then re-run.`
   Leave the tree and the branch exactly as they are.

⛔ **This gate has exactly two outcomes: AUTHORIZED, or a STOP with a named reason and the fix.** There is
no third "the board looks ambiguous, checking with you" branch — that is the punt-hatch this gate exists to
remove, and re-introducing it recreates the very problem it was written for. Ambiguity resolves to the STOP
in (4), stated as a refusal, never as a question.

**Normal path cost: zero.** `/cicd-close-story-merge-tree` Steps 1–3 flip the status, write the board and
land the code before its Step 5 ever calls this command — so the gate is satisfied by construction. It only
bites when the prune is run standalone against something that was never actually closed out. Which is
exactly when it should.

## Step 2 — PRESERVE uncommitted work before ANY removal (MANDATORY — data-loss gate)

⛔ **`git worktree remove --force` DISCARDS uncommitted and untracked files without a prompt.** Step 1's
merge-base check proves the *branch* landed; it says nothing about work in the tree that was never
committed. Those are different questions and historically only one of them was being asked. The 1,197-line
21.4 tree above would have been destroyed silently, and nothing downstream would ever have reported a loss.

For **every** worktree Step 1.6 marked for removal:

```bash
cd .claude/worktrees/<slug> && git status --short      # ANY output = unsaved work
```

- **Empty** → nothing at risk, proceed.
- **Any output** → **do NOT remove yet.** Commit it to its own branch and push, so the work becomes
  reproducible instead of unique to that disk:
  ```bash
  cd .claude/worktrees/<slug> && git add <explicit paths>     # never `git add -A`
  cd .claude/worktrees/<slug> && git commit -m "wip(<story>): preserve uncommitted work before worktree prune"
  cd .claude/worktrees/<slug> && git push -u origin claude/<JIRA-KEY>-<slug>
  ```
  Then say plainly in the report that you committed someone else's in-flight work, what it was, and that
  the story's status is **unchanged** — a preservation commit is not progress and must never be reported as
  it, on the board or anywhere else.
- **Cannot push** (no remote, detached HEAD, conflict) → **STOP and report.** Never remove a tree whose only
  copy of the work is local.

⛔ **A branch you just pushed preserved work to is NOT deletable.** Flag it for Step 5 — deleting it throws
away the thing you just saved.

## Step 2.5 — Exit the worktree directory if you are inside it
If `cwd` is inside any `PROJECT_ROOT/.claude/worktrees/<slug>` you are about to remove, shift `cwd` out to
`PROJECT_ROOT` so the directory is unlocked. A shell sitting inside is the most common cause of the
"being used by another process" failure in Step 3.

## Step 3 — Unlink junctions, THEN remove the worktree

**This order is mandatory and is the reverse of what feels natural.**

`git worktree remove --force` de-registers the worktree but **leaves the directory on disk when reparse
points are present** — observed 2026-07-27 on `story-21-4`: it returned success, dropped the registration,
and left the folder holding three live junctions. Removing first therefore MANUFACTURES the exact HUSK
Step 1.6 exists to catch, *and* strips the `git worktree list` entry that would have told you it was still
there.

### 3a · Unlink every reparse point (ALWAYS FIRST)

⛔ **`Remove-Item -Recurse` FOLLOWS junctions and deletes the TARGET.** A story worktree does not inherit
gitignored assets, so lanes junction shared assets back to the **main checkout** (see
`worktree-per-story.md`). A naive recursive delete walks straight through those junctions and destroys the
real asset in `PROJECT_ROOT` — breaking the shared checkout *and* every other live worktree pointing at it.

**Never work from a list of "the junctions I created."** Two independent reasons that list is wrong:
- Known shared-asset links are **at least** `frontend/node_modules`, `firebase/tests/node_modules` **and
  `backend/.venv`** — `.venv` was missing from this command until 2026-07-27 and is the one that orphaned
  the 21.5 tree.
- **Tools create junctions on their own.** Next.js/Turbopack plants them under
  `frontend/.next/dev/node_modules/` (e.g. `import-in-the-middle-*`, `require-in-the-middle-*`) simply by
  running the dev server or the E2E gate. Observed 2026-07-27: 2 of 3 reparse points in a worktree were
  created by Next, not by any lane.

**Therefore: always ENUMERATE, never assume. The scan is the authority.**

Cross-platform, Mac AND PC — the same enumerate-then-prove logic, scripted (SCC-62; the center's
script, run from the command-center root):

```bash
python3 .agents/scripts/link-worktree-assets.py --unlink PROJECT_ROOT/.claude/worktrees/<slug>   # PC: python
```

It enumerates every reparse point WITHOUT descending through any, unlinks each (the link only, never
the target), then re-scans and refuses to report success while any remain. A non-zero exit → STOP,
exactly as the ABORT below. The PowerShell equivalent, for PC when you need it by hand:

```powershell
$wt = "PROJECT_ROOT/.claude/worktrees/<slug>"
# enumerate every reparse point (junction/symlink) and unlink it.
# .Delete() on the DirectoryInfo removes the LINK only, never the target, and unlike
# `cmd /c rmdir` it cannot be mis-parsed by a shell wrapper.
foreach ($l in @(Get-ChildItem $wt -Recurse -Force -Directory -EA SilentlyContinue |
                 Where-Object { $_.LinkType })) {
  Write-Output "unlinked: $($l.FullName)  ->  $($l.Target)"; $l.Delete()
}
# prove none remain BEFORE anything recursive touches this path
$left = @(Get-ChildItem $wt -Recurse -Force -Directory -EA SilentlyContinue | Where-Object { $_.LinkType })
if ($left.Count) { Write-Output "ABORT - reparse points still present"; $left | Select-Object FullName }
```

### 3b · Remove the worktree and prune

```bash
git worktree remove --force .claude/worktrees/<slug>     # skip for a HUSK — no registration exists
git worktree prune
```

### 3c · Delete the leftover directory (only once 3a proved zero reparse points)

```powershell
Remove-Item -Recurse -Force $wt -Confirm:$false -ErrorAction Stop
```

`-ErrorAction Ignore` is deliberately NOT used: a failure here must be visible, not swallowed.

**If the delete fails with *"being used by another process"***, the unlink half has already made the husk
harmless (no reparse points left). Do **not** retry in a loop and do **not** report success — name the
leftover path, say the junctions are unlinked so it is now safe to delete by hand, and carry it in the
report. Common holders: an editor file-watcher, or a shell whose `cwd` is still inside (Step 2.5).

## Step 4 — Verify the shared assets SURVIVED

Run this before touching any branch. The unlink in 3a and a destructive follow-through look identical to a
bare existence check for the moment between them, so **probe, don't just `Test-Path`**:

```powershell
# ⛔ The venv bin dir is PER-MACHINE - POSIX puts it in bin/, Windows in Scripts/ (code-standards §6).
# ⛔ PROJECT_ROOT is a PLACEHOLDER you substitute, exactly as everywhere else in this file -
# NOT a PowerShell variable. Nothing binds one, and pwsh expands an undefined variable inside
# a double-quoted string to EMPTY, so `$PROJECT_ROOT/...` would probe `/backend/...`, fail on
# both machines, and trip the STOP below on the one step guarding an irreversible delete.
$PY = "PROJECT_ROOT/backend/.venv/bin/python3"
if (-not (Test-Path $PY)) { $PY = "PROJECT_ROOT/backend/.venv/Scripts/python.exe" }
& $PY --version                                                      # must print a version
@(Get-ChildItem PROJECT_ROOT/frontend/node_modules -Force).Count     # must be non-zero
@(Get-ChildItem PROJECT_ROOT/firebase/tests/node_modules -Force).Count
```

⛔ **This probe hardcoded the WINDOWS path until SCC-205, and it sits on the DESTRUCTIVE path.** On the
Mac `Scripts/python.exe` does not exist, so the probe failed, and the very next line says *"Any failure
here → STOP and report immediately... A destroyed shared asset breaks every other lane."* Every Mac
close-out would have reported a destroyed venv that was never touched — and a probe that cries wolf on
the one step guarding an irreversible delete is a probe people learn to skip.

Any failure here → **STOP and report immediately.** A destroyed shared asset breaks every other lane on the
machine, and it is recoverable only if someone knows it happened.

## Step 5 — Delete branches — ONLY those that passed Steps 1 AND 1.7

**Order is REMOTE first, local second — the reverse fails.** A landed branch's close-out commits are
never pushed to `claude/*` (the landing pushes `HEAD:epic/<JIRA-KEY>-<slug>` only), so a PARKED branch's local tip
is ahead of its upstream. `git branch -d` checks merged-into-**upstream** when an upstream exists — and
refuses. Deleting the remote first removes the upstream, so `-d` falls back to the merged-into-HEAD
check and succeeds honestly (observed 2026-08-01: all three set-close-out `-d`s failed remote-last,
all three succeeded remote-first).

```bash
# Remote FIRST: ONLY if the branch is actually on origin — i.e. it was PARKED.
git ls-remote --heads origin claude/<JIRA-KEY>-<story-slug>                    # empty → nothing to delete, say so
Remove-Item Env:\GITHUB_TOKEN -ErrorAction Ignore; git push origin --delete claude/<JIRA-KEY>-<story-slug>

git branch -d claude/<JIRA-KEY>-<story-slug>                                   # -d first; see the HEAD caveat below
```

⚠️ **The merged-into-HEAD fallback checks `main` now** (the shared checkout stands there), and `main`
does not contain the story until its epic merges via `/cicd-push-e2e` — so `-d` can honestly refuse on
a branch that HAS landed. In exactly that case, Step 1's recorded `merge-base --is-ancestor …
origin/epic/<JIRA-KEY>-<slug>` pass IS the merged proof: delete with `git branch -D` and cite that pass in the
report. No recorded Step 1 pass → never `-D`.

⛔ **Delete a branch ONLY if it passed Step 1 (landed) AND Step 1.7 (closed out).** Removing a *tree* is
cheap — the branch recreates it. Deleting the *branch* of an unlanded story destroys the only copy of that
work, including anything Step 2 just preserved. Step 1.6 deliberately reaches trees belonging to **other**
stories; those branches have not been checked and must **not** be deleted.

- Landed + closed out → delete local; delete remote **only if `ls-remote` finds it**.
- Landed, not closed out → Step 1.7 already STOPped. Nothing is deleted.
- Not landed, tree removed → **keep both branches**, and report: *"tree pruned; branch `claude/<JIRA-KEY>-<slug>`
  retained — restore with `/cicd-resume`."*
- `git branch -d` refuses → check WHY before reaching for `-D`. With the remote already deleted (the
  order above), a refusal is either the expected HEAD-is-`main` caveat above (Step 1 passed → `-D` with
  the cited proof) or the branch genuinely never landed — go back to Step 1. (If you ran it remote-last,
  the refusal is probably just the upstream check — delete the remote and retry `-d` once.)

**Most story branches will not exist on origin at all, and that is correct.** Per `git-policy.md` → "The
landing", the landing pushes `HEAD:epic/<JIRA-KEY>-<slug>` and **not** the branch; a story branch reaches origin only
via `/cicd-park`. So an absent remote branch is the normal case — report it as *"never pushed (not
parked) — nothing to delete"*, not as a failure. A remote branch that IS present means this story was
parked, and deleting it here is what stops `/cicd-resume` from later offering a story that is already done.

⛔ **Never sweep `claude/*` on origin wholesale.** `claude/incident-*` branches come from the Epic-16
incident pipeline, not story flow — they MATCH the `claude/*` glob and are outside this command
entirely: delete only the one story branch you verified merged, never a listing (SCC-148).

## Step 6 — Verify, THEN report (never report an unverified success)

⛔ **Prove each claim before printing it.** The 21.5 close-out reported a clean removal while the directory
was still on disk holding three live junctions — because the report was written from intent, not from a
check. Every ✅ below must come from a command you actually ran in this step:

```powershell
Test-Path "PROJECT_ROOT/.claude/worktrees/<slug>"              # must be False
git worktree list                                              # must not list it
git branch --list claude/<JIRA-KEY>-<slug>                                # empty IF you deleted it
git ls-remote --heads origin claude/<JIRA-KEY>-<slug>                     # empty IF you deleted it
Get-ChildItem "PROJECT_ROOT/.claude/worktrees" -Force -Directory   # every remaining row must be one
                                                               # you deliberately KEPT and named
```

If a check fails, print ❌ for that line with the actual state — a partial cleanup reported as complete is
worse than no cleanup, because nothing will look again.

Print summary:
`🧹 Closed workingtree & pruned branches for <story-slug>:`
- `✅ Local worktree removed: .claude/worktrees/<story-slug>` *(verified absent)*
- `✅ Local branch deleted: claude/<JIRA-KEY>-<story-slug>` *(or "retained — not landed")*
- `✅ Remote GitHub branch deleted: origin/claude/<JIRA-KEY>-<story-slug>` *(or "retained" / "never pushed")*
- `✅ Shared assets intact: frontend/node_modules · firebase/tests/node_modules · backend/.venv` *(probed)*
- `🧹 Swept: <every tree found, its state, and its disposition — or "none">` *(from Step 1.6)*
- `💾 Preserved: <what was committed and pushed, and to which branch — or "nothing uncommitted">` *(Step 2)*
