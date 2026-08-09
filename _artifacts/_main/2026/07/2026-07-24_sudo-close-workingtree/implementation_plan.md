# Implementation Plan - `/sudo-close-workingtree` Command & Worktree Pruning Pipeline

Establish a safe, automated workflow (`/sudo-close-workingtree`) to verify story branch merging onto `main_debug`, prune local git worktrees (`.claude/worktrees/<slug>`), and delete both local and remote GitHub branches (`claude/<slug>`). Integrate this directly into `/sudo-update-sprint-memory` and propagate across all agents (Claude, Opencode, Antigravity/Gemini, Codex) and top project workspaces (`AGY_AVIATIONCHAT`, `Fresh_Workspace_BMAD`, `OpenChat-Openrouter`, etc.).

## Proposed Changes

### Master Toolkit (`.agents/`)

#### [NEW] [sudo-close-workingtree.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/commands/sudo-close-workingtree.md)
Create the new command definition in `.agents/commands/sudo-close-workingtree.md`:
- Resolves project root (`PROJECT_ROOT`) and target story slug (`$ARGUMENTS` or current worktree / active story).
- **Safety Gate**: Verifies `git merge-base --is-ancestor claude/<story-slug> origin/main_debug`. Aborts if unmerged.
- **Directory Shift**: Moves `cwd` out of `.claude/worktrees/<slug>` to `PROJECT_ROOT` before removal.
- **Worktree Pruning**: Runs `git worktree remove .claude/worktrees/<slug>`.
- **Branch Deletion**: Deletes local branch `git branch -d claude/<story-slug>` and remote GitHub branch `git push origin --delete claude/<story-slug>`.
- **Reporting**: Logs confirmation of cleaned worktree and remote branch.

#### [NEW] [sudo-close-workingtree.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/workflows/sudo-close-workingtree.md)
Create the workflow mirror file in `.agents/workflows/sudo-close-workingtree.md`.

#### [NEW] [SKILL.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/skills/sudo-close-workingtree/SKILL.md)
Create the skill definition in `.agents/skills/sudo-close-workingtree/SKILL.md`.

#### [MODIFY] [sudo-update-sprint-memory.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/commands/sudo-update-sprint-memory.md)
- Add **Step 8: Prune Merged Worktree & Branch**.
- Automatically invokes `/sudo-close-workingtree <slug>` immediately after Step 7 landing on `main_debug`.

#### [MODIFY] [worktree-per-story.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/rules/worktree-per-story.md)
- Update "Close-out — the landing" to explain that merged worktrees and branches are cleaned up via `/sudo-close-workingtree` post-landing rather than accumulating indefinitely.

#### [MODIFY] [git-policy.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/rules/git-policy.md)
- Update branch lifecycle guidelines to detail post-landing branch and worktree deletion upon verification.

---

### Synchronization Across Platforms & Projects

#### [EXECUTE] Multi-platform Sync Script
- Run `& ".agents/scripts/sync-agents.ps1"` to mirror commands and skills across:
  - Local tool dirs (`.claude/`, `.opencode/`)
  - Machine-global caches (`~/.config/opencode/commands`, `~/.gemini/antigravity/global_workflows`, `~/.codex/prompts`, `~/.codex/skills`)
  - All projects under `Projects/` (`AGY_AVIATIONCHAT`, `Fresh_Workspace_BMAD`, `OpenChat-Openrouter`, `B-L-WorldWide`, `BRKN_Tattoos`, `NEXGen-Films`, `RAG_Pipeline_AC`).

---

## Verification Plan

### Automated Verification
1. Run `& ".agents/scripts/sync-agents.ps1" -Maintained -Status` to verify 100% clean sync across all platform surfaces and projects.
2. Run `/sudo-close-workingtree` dry-run logic on an unmerged branch to verify safety refusal.
3. Test `/sudo-close-workingtree` on a merged story branch in `AGY_AVIATIONCHAT` to verify clean removal of worktree, local branch, and remote GitHub branch.

### Manual Verification
1. Check `git worktree list` in `Projects/AGY_AVIATIONCHAT` to confirm worktree folder removal.
2. Check `git branch -r` to confirm GitHub branch deletion.
