---
description: Safely verify a story branch has been merged into main_debug, prune its local git worktree, and delete both local and remote (GitHub) branches.
---

# /sudo-close-workingtree — Close & Prune Merged Worktree & Branches

Safely clean up a story worktree and its associated git branches (`claude/<story-slug>`) after the story has been completed and landed on `main_debug`.

## Step 0 — Resolve target project and story slug
1. **Target Project**:
   - Sub-project fast path: If this repo has no `Projects/` subfolder, `PROJECT_ROOT = .`.
   - Else, resolve project via inline override in `$ARGUMENTS`, active pointer in `.agents/active-project.txt`, or ask Daniel. Set `PROJECT_ROOT = Projects/<name>`.
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

- **If `git merge-base` returns exit code 0**: The branch is fully merged into `origin/main_debug`. Proceed to Step 2.
- **If `git merge-base` returns non-zero**: **STOP IMMEDIATELY!**
  Print: `❌ Refusing to delete: claude/<story-slug> is NOT fully merged into origin/main_debug.`
  Instruct: `Land the story first using /sudo-update-sprint-memory or git merge to origin/main_debug.`

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
   Check if the directory `.claude/worktrees/<story-slug>` still exists on disk. If it exists:
   ```powershell
   Remove-Item -Recurse -Force "PROJECT_ROOT/.claude/worktrees/<story-slug>" -ErrorAction Ignore
   ```

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
