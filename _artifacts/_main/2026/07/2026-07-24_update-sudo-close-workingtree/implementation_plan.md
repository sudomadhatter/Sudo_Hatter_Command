---
IsArtifact: true
ArtifactMetadata:
  title: "Update /sudo-close-workingtree with physical directory cleanup"
  type: implementation_plan
  date: 2026-07-24
  UserFacing: true
  RequestFeedback: true
  Summary: "Plan to update /sudo-close-workingtree command and workflow to purge physical orphan worktree directories from disk after git unlinking."
---

# Update `/sudo-close-workingtree` to Purge Physical Worktree Directories

## Summary
When running `git worktree remove`, Git unlinks the worktree from Git metadata. However, on Windows, if untracked build artifacts or file handles remain, Git leaves the physical directory behind on disk (e.g. `.claude/worktrees/<story-slug>`). This causes the folder to linger in the IDE side panel.

This plan updates `/sudo-close-workingtree` to include a mandatory physical disk cleanup check to delete any remaining orphan folder.

## User Review Required
> [!NOTE]
> Step 3 of `/sudo-close-workingtree` will use `git worktree remove --force` followed by `git worktree prune` and a fallback `Remove-Item -Recurse -Force` check on the directory path if it still exists.

## Proposed Changes

### Master Toolkit (`.agents`)

#### [MODIFY] [sudo-close-workingtree.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/commands/sudo-close-workingtree.md)
Update Step 3 to add `--force` to `git worktree remove` and add explicit PowerShell/Bash physical directory removal logic (`Remove-Item -Recurse -Force "PROJECT_ROOT/.claude/worktrees/<story-slug>"`).

#### [MODIFY] [sudo-close-workingtree.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/workflows/sudo-close-workingtree.md)
Keep the workflow file synchronized with the command file in `.agents/commands/`.

### Synchronization & Propagation

#### [RUN] `/sync-agents`
Run the agent sync script (`& ".agents/scripts/sync-agents.ps1" -Maintained`) to propagate the updated `/sudo-close-workingtree` command across global caches and maintained projects.

## Verification Plan

### Manual Verification
1. Inspect `.agents/commands/sudo-close-workingtree.md` and `.agents/workflows/sudo-close-workingtree.md` to ensure Step 3 includes physical directory removal.
2. Run sync script to propagate changes.
