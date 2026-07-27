---
description: Safely verify a story branch has been merged into main_debug, prune its local git worktree, and delete both local and remote (GitHub) branches.
---

# /sudo-close-workingtree — Close & Prune Merged Worktree & Branches

Safely clean up a story worktree and its associated git branches (`claude/<story-slug>`) after the story has been completed and landed on `main_debug`.

## Step 0 — Resolve target project and story slug
1. **Target Project** — bind per `.agents/rules/sudo-target-resolution.md` §STD: self fast-path →
   `$ARGUMENTS` override → `.agents/active-project.txt` → else ask Daniel. Set `PROJECT_ROOT`.
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

- **If `git merge-base` returns exit code 0**: The branch is fully merged into `origin/main_debug`. Proceed to Step 1.5.
- **If `git merge-base` returns non-zero**: **STOP IMMEDIATELY!**
  Print: `❌ Refusing to delete: claude/<story-slug> is NOT fully merged into origin/main_debug.`
  Instruct: `Land the story first using /sudo-update-sprint-memory or git merge to origin/main_debug.`

## Step 1.5 — Backstop: is the shared checkout actually current? (catches the silent drift)
You are already standing in `PROJECT_ROOT`, so check the thing the landing push cannot update:

```bash
git rev-list --left-right --count main_debug...origin/main_debug     # -> "<ahead> <behind>"
```

`git push origin HEAD:main_debug` moves the remote but never `refs/heads/main_debug`, so a shared checkout
that is **behind** means a landing skipped `/sudo-update-sprint-memory` Step 7b — and the drift compounds one
story per landing until a `pull --ff-only` refuses on the board files.

- **`0 0`** → clean, proceed to Step 2.
- **behind only** → run `git-policy.md` → **"Reconcile the shared checkout"** now (stash if dirty →
  `merge --ff-only` → pop; a pop conflict is a **STOP**). Then re-check it reads `0 0`.
- **ahead > 0** → real divergence, **STOP and report** — never fast-forward over local commits.

Note the local branch may legitimately be behind *at this instant* if you were invoked standalone rather
than by Step 8; reconciling is still correct. Do NOT skip this because "Step 7 already pushed" — the push
is exactly what does not do it.

⚠️ Deleting the local branch (Step 4) with `git branch -d` checks it is merged into **HEAD**, not into
`origin/main_debug`. On a stale `main_debug` that check fails on a branch that HAS landed. Reconciling here
first is what makes `-d` succeed honestly instead of tempting a `-D`.

## Step 2 — Exit worktree directory if currently inside it
If current working directory (`cwd`) is inside `PROJECT_ROOT/.claude/worktrees/<story-slug>`, shift `cwd` out to `PROJECT_ROOT` so the directory is unlocked for removal.

## Step 3 — Prune local git worktree & purge physical directory
In `PROJECT_ROOT`:
1. If `.claude/worktrees/<story-slug>` is listed in `git worktree list`:
   ```bash
   git worktree remove --force .claude/worktrees/<story-slug>
   ```
2. Run git worktree prune:
   ```bash
   git worktree prune
   ```
3. **Physical disk cleanup (prevent orphan folders in IDE side panel)**:

   ⛔ **Unlink junctions FIRST — `Remove-Item -Recurse` follows them and deletes the TARGET.** A story
   worktree does not inherit gitignored assets, so lanes junction `frontend/node_modules` and
   `firebase/tests/node_modules` back to the **main checkout** (see `worktree-per-story.md`). A naive
   recursive delete walks straight through those junctions and destroys the real `node_modules` in
   `PROJECT_ROOT` — breaking the shared checkout *and* every other live worktree pointing at it.

   ```powershell
   $wt = "PROJECT_ROOT/.claude/worktrees/<story-slug>"
   # 1 · enumerate every reparse point (junction/symlink) inside the tree
   Get-ChildItem $wt -Recurse -Force -Directory -EA SilentlyContinue |
     Where-Object { $_.LinkType } | ForEach-Object {
       cmd /c rmdir "$($_.FullName)"        # removes the LINK only, never the target
       Write-Output "unlinked: $($_.FullName)"
     }
   # 2 · prove none remain, THEN delete
   $left = Get-ChildItem $wt -Recurse -Force -Directory -EA SilentlyContinue | Where-Object { $_.LinkType }
   if ($left) { Write-Output "ABORT - reparse points still present"; $left | Select FullName }
   else { Remove-Item -Recurse -Force $wt -Confirm:$false }
   ```

   Then **verify the junction targets survived** (`frontend/node_modules` and `firebase/tests/node_modules`
   under `PROJECT_ROOT` still exist and are non-empty) before reporting success. `-ErrorAction Ignore` is
   deliberately NOT used on the delete: a failure here must be visible, not swallowed.

## Step 4 — Delete local and remote git branches
In `PROJECT_ROOT`:
```bash
# 1 · Delete local branch
git branch -d claude/<story-slug>

# 2 · Delete remote branch on GitHub
Remove-Item Env:\GITHUB_TOKEN -ErrorAction Ignore; git push origin --delete claude/<story-slug>
```

## Step 5 — Report outcome
Print summary:
`🧹 Closed workingtree & pruned branches for <story-slug>:`
- `✅ Local worktree removed: .claude/worktrees/<story-slug>`
- `✅ Local branch deleted: claude/<story-slug>`
- `✅ Remote GitHub branch deleted: origin/claude/<story-slug>`
