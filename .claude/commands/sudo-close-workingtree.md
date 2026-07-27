---
description: Safely verify a story branch has been merged into main_debug, preserve any uncommitted work, then prune EVERY stale worktree on disk and delete both local and remote (GitHub) branches. Sweeps all trees, not just the named slug.
---

# /sudo-close-workingtree — Close & Prune Merged Worktree & Branches

Safely clean up story worktrees and their git branches (`claude/<story-slug>`) after a story has landed on
`main_debug`.

**Order is load-bearing and the numbering enforces it: SWEEP → PRESERVE → UNLINK → REMOVE → DELETE BRANCH.**
Every out-of-order variant of this command has destroyed something. Do not reorder, and do not skip a step
because the tree "looks empty" — every incident below started with a tree that looked empty.

## Step 0 — Resolve target project and story slug
1. **Target Project** — bind per `.agents/rules/sudo-target-resolution.md` §STD: self fast-path →
   `$ARGUMENTS` override → `.agents/active-project.txt` → else ask the operator. Set `PROJECT_ROOT`.
2. **Target Story Slug**:
   - If `$ARGUMENTS` provides a story slug or branch name (e.g. `21-12-fail-closed-admin-roles` or `claude/21-12-fail-closed-admin-roles`), strip any `claude/` or `.claude/worktrees/` prefix to extract `<story-slug>`.
   - Otherwise, if standing inside a worktree `.claude/worktrees/<story-slug>`, extract `<story-slug>` from current working directory.
   - Otherwise, read the active story slug from `PROJECT_ROOT/_bmad-output/implementation-artifacts/sprint-status.yaml`.

Echo `Target: Projects/<name> | Story: <story-slug>` before proceeding.

## Step 1 — Safety Verification Gate (MANDATORY)
In `PROJECT_ROOT`:
```bash
# 1 · Fetch latest remote refs
Remove-Item Env:\GITHUB_TOKEN -ErrorAction Ignore; git fetch origin

# 2 · Verification check: confirm story branch has landed on origin/main_debug
git merge-base --is-ancestor claude/<story-slug> origin/main_debug
```

- **Exit code 0**: the branch is fully merged into `origin/main_debug`. Proceed to Step 1.5.
- **Non-zero**: **STOP IMMEDIATELY!**
  Print: `❌ Refusing to delete: claude/<story-slug> is NOT fully merged into origin/main_debug.`
  Instruct: `Land the story first using /sudo-update-sprint-memory or git merge to origin/main_debug.`

**Record this result per branch.** Step 5 deletes branches, and it may ONLY delete a branch that passed this
check. A tree can be safe to remove while its branch is not safe to delete — those are different questions.

## Step 1.5 — Backstop: is the shared checkout actually current? (catches the silent drift)
You are already standing in `PROJECT_ROOT`, so check the thing the landing push cannot update:

```bash
git rev-list --left-right --count main_debug...origin/main_debug     # -> "<ahead> <behind>"
```

`git push origin HEAD:main_debug` moves the remote but never `refs/heads/main_debug`, so a shared checkout
that is **behind** means a landing skipped `/sudo-update-sprint-memory` Step 7b — and the drift compounds one
story per landing until a `pull --ff-only` refuses on the board files.

- **`0 0`** → clean, proceed to Step 1.6.
- **behind only** → run `git-policy.md` → **"Reconcile the shared checkout"** now (stash if dirty →
  `merge --ff-only` → pop; a pop conflict is a **STOP**). Then re-check it reads `0 0`.
- **ahead > 0** → real divergence, **STOP and report** — never fast-forward over local commits.

Note the local branch may legitimately be behind *at this instant* if you were invoked standalone rather
than by Step 8; reconciling is still correct. Do NOT skip this because "Step 7 already pushed" — the push
is exactly what does not do it.

⚠️ Deleting the local branch (Step 5) with `git branch -d` checks it is merged into **HEAD**, not into
`origin/main_debug`. On a stale `main_debug` that check fails on a branch that HAS landed. Reconciling here
first is what makes `-d` succeed honestly instead of tempting a `-D`.

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
  red-phase test tiers from a `/sudo-write-story-tests` run that never committed.

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
    $dirty   = if ($hasGit) { @(git -C $d.FullName status --short).Count } else { 'n/a' }
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

## Step 2 — PRESERVE uncommitted work before ANY removal (MANDATORY — data-loss gate)

⛔ **`git worktree remove --force` DISCARDS uncommitted and untracked files without a prompt.** Step 1's
merge-base check proves the *branch* landed; it says nothing about work in the tree that was never
committed. Those are different questions and historically only one of them was being asked. The 1,197-line
21.4 tree above would have been destroyed silently, and nothing downstream would ever have reported a loss.

For **every** worktree Step 1.6 marked for removal:

```bash
git -C .claude/worktrees/<slug> status --short      # ANY output = unsaved work
```

- **Empty** → nothing at risk, proceed.
- **Any output** → **do NOT remove yet.** Commit it to its own branch and push, so the work becomes
  reproducible instead of unique to that disk:
  ```bash
  git -C .claude/worktrees/<slug> add <explicit paths>     # never `git add -A`
  git -C .claude/worktrees/<slug> commit -m "wip(<story>): preserve uncommitted work before worktree prune"
  git -C .claude/worktrees/<slug> push -u origin claude/<slug>
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
PROJECT_ROOT/backend/.venv/Scripts/python.exe --version              # must print a version
@(Get-ChildItem PROJECT_ROOT/frontend/node_modules -Force).Count     # must be non-zero
@(Get-ChildItem PROJECT_ROOT/firebase/tests/node_modules -Force).Count
```

Any failure here → **STOP and report immediately.** A destroyed shared asset breaks every other lane on the
machine, and it is recoverable only if someone knows it happened.

## Step 5 — Delete branches — ONLY those that passed Step 1

```bash
git branch -d claude/<story-slug>                                   # -d, never -D
Remove-Item Env:\GITHUB_TOKEN -ErrorAction Ignore; git push origin --delete claude/<story-slug>
```

⛔ **Delete a branch ONLY if it passed Step 1's merge-base check.** Removing a *tree* is reversible — the
branch can recreate it via `/sudo-resume`. Deleting the *branch* of an unlanded story destroys the only
copy of that work, including anything Step 2 just preserved. The sweep in Step 1.6 deliberately reaches
trees belonging to other stories; their branches have **not** been checked and must **not** be deleted.

- Branch landed (Step 1 exit 0) → delete local + remote.
- Branch not landed, tree removed → **keep both branches**, and report: *"tree pruned; branch
  `claude/<slug>` retained on origin — restore with `/sudo-resume`."*
- `git branch -d` refuses → do **not** reach for `-D`. It means the branch is not merged into HEAD; go back
  to Step 1.5.

## Step 6 — Verify, THEN report (never report an unverified success)

⛔ **Prove each claim before printing it.** The 21.5 close-out reported a clean removal while the directory
was still on disk holding three live junctions — because the report was written from intent, not from a
check. Every ✅ below must come from a command you actually ran in this step:

```powershell
Test-Path "PROJECT_ROOT/.claude/worktrees/<slug>"              # must be False
git worktree list                                              # must not list it
git branch --list claude/<slug>                                # empty IF you deleted it
git ls-remote --heads origin claude/<slug>                     # empty IF you deleted it
Get-ChildItem "PROJECT_ROOT/.claude/worktrees" -Force -Directory   # every remaining row must be one
                                                               # you deliberately KEPT and named
```

If a check fails, print ❌ for that line with the actual state — a partial cleanup reported as complete is
worse than no cleanup, because nothing will look again.

Print summary:
`🧹 Closed workingtree & pruned branches for <story-slug>:`
- `✅ Local worktree removed: .claude/worktrees/<story-slug>` *(verified absent)*
- `✅ Local branch deleted: claude/<story-slug>` *(or "retained — not landed")*
- `✅ Remote GitHub branch deleted: origin/claude/<story-slug>` *(or "retained" / "never pushed")*
- `✅ Shared assets intact: frontend/node_modules · firebase/tests/node_modules · backend/.venv` *(probed)*
- `🧹 Swept: <every tree found, its state, and its disposition — or "none">` *(from Step 1.6)*
- `💾 Preserved: <what was committed and pushed, and to which branch — or "nothing uncommitted">` *(Step 2)*
