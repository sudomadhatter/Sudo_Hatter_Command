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
   worktree does not inherit gitignored assets, so lanes junction shared assets back to the **main
   checkout** (see `worktree-per-story.md`). A naive recursive delete walks straight through those
   junctions and destroys the real asset in `PROJECT_ROOT` — breaking the shared checkout *and* every
   other live worktree pointing at it.

   **Never work from a list of "the junctions I created."** Two independent reasons the list is wrong:
   - Known shared-asset links are **at least** `frontend/node_modules`, `firebase/tests/node_modules`
     **and `backend/.venv`** — `.venv` was missing from this command until 2026-07-27 and is the one
     that orphaned the 21.5 tree.
   - **Tools create junctions on their own.** Next.js/Turbopack plants them under
     `frontend/.next/dev/node_modules/` (e.g. `import-in-the-middle-*`, `require-in-the-middle-*`) simply
     by running the dev server or the E2E gate. Observed 2026-07-27: 2 of 3 reparse points in a worktree
     were created by Next, not by any lane.

   **Therefore: always ENUMERATE, never assume.** The scan is the authority.

   ```powershell
   $wt = "PROJECT_ROOT/.claude/worktrees/<story-slug>"
   # 1 · enumerate every reparse point (junction/symlink) and unlink it.
   #     Use .Delete() on the DirectoryInfo — it removes the LINK only, never the target,
   #     and unlike `cmd /c rmdir` it cannot be mis-parsed by a shell wrapper.
   foreach ($l in @(Get-ChildItem $wt -Recurse -Force -Directory -EA SilentlyContinue |
                    Where-Object { $_.LinkType })) {
     $l.Delete(); Write-Output "unlinked: $($l.FullName)"
   }
   # 2 · prove none remain, THEN delete
   $left = @(Get-ChildItem $wt -Recurse -Force -Directory -EA SilentlyContinue | Where-Object { $_.LinkType })
   if ($left.Count) { Write-Output "ABORT - reparse points still present"; $left | Select FullName }
   else { Remove-Item -Recurse -Force $wt -Confirm:$false -ErrorAction Stop }
   ```

   Then **verify the junction targets survived** — `frontend/node_modules`, `firebase/tests/node_modules`
   **and `backend/.venv`** under `PROJECT_ROOT` still exist and are non-empty — before reporting success.
   `-ErrorAction Ignore` is deliberately NOT used on the delete: a failure here must be visible, not swallowed.

   **If the delete fails with *"being used by another process"***, the unlink half has already made the
   husk harmless (no reparse points left). Do **not** retry in a loop and do **not** report success —
   name the leftover path, say the junctions are unlinked so it is now safe to delete by hand, and carry
   it in the report. Common holders: an editor file-watcher, or a shell whose `cwd` is still inside
   (Step 2).

## Step 3.5 — Sweep for ORPHAN worktree directories (catches earlier bad close-outs)

A husk left by a *previous* close-out is invisible to `git worktree list` — git pruned the registration,
so nothing ever looks at the folder again. That is how the 21.5 tree survived a full day in the IDE side
panel, still holding live junctions to the shared `.venv` and both `node_modules`. Sweep every run, not
just for `<story-slug>`:

```powershell
$root = "PROJECT_ROOT/.claude/worktrees"
if (Test-Path $root) {
  $known = (git worktree list --porcelain) -match '^worktree ' -replace '^worktree ',''
  Get-ChildItem $root -Force -Directory | ForEach-Object {
    $isKnown = $known | Where-Object { $_.Replace('/','\') -like "*$($_.Name)*" }
    if (-not $isKnown) { Write-Output "ORPHAN: $($_.FullName)" }
  }
}
```

An orphan with **no `.git` entry inside it** is a dead husk — run the Step 3.3 unlink-then-delete on it.
Report every orphan found and what you did with it. A directory that still has `.git` is a live worktree
git lost track of: **STOP and report**, never delete it.

## Step 4 — Delete local and remote git branches
In `PROJECT_ROOT`:
```bash
# 1 · Delete local branch
git branch -d claude/<story-slug>

# 2 · Delete remote branch on GitHub
Remove-Item Env:\GITHUB_TOKEN -ErrorAction Ignore; git push origin --delete claude/<story-slug>
```

## Step 5 — Verify, THEN report (never report an unverified success)

⛔ **Prove each claim before printing it.** The 21.5 close-out reported a clean removal while the
directory was still on disk holding three live junctions — because the report was written from intent,
not from a check. Every ✅ below must come from a command you actually ran in this step:

```powershell
Test-Path "PROJECT_ROOT/.claude/worktrees/<story-slug>"        # must be False
git worktree list                                              # must not list it
git branch --list claude/<story-slug>                          # must be empty
git ls-remote --heads origin claude/<story-slug>               # must be empty
# shared assets must all still exist and be non-empty:
#   PROJECT_ROOT/frontend/node_modules · firebase/tests/node_modules · backend/.venv
```

If a check fails, print ❌ for that line with the actual state — a partial cleanup reported as complete is
worse than no cleanup, because nothing will look again.

Print summary:
`🧹 Closed workingtree & pruned branches for <story-slug>:`
- `✅ Local worktree removed: .claude/worktrees/<story-slug>` *(verified absent)*
- `✅ Local branch deleted: claude/<story-slug>`
- `✅ Remote GitHub branch deleted: origin/claude/<story-slug>` *(or "never pushed — nothing to delete")*
- `✅ Shared assets intact: frontend/node_modules · firebase/tests/node_modules · backend/.venv`
- `🧹 Orphans swept: <list, or "none">` *(from Step 3.5)*
