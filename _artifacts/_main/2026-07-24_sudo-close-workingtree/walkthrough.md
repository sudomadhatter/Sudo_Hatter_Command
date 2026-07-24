# Walkthrough - `/sudo-close-workingtree` Command & Worktree Pruning Pipeline

Created and synchronized the new `/sudo-close-workingtree` command across all agent surfaces (Claude, Opencode, Antigravity/Gemini, Codex) and project repositories. Integrated Step 8 auto-pruning into `/sudo-update-sprint-memory`.

## Changes Implemented

### Master Toolkit (`.agents/`)

- **Created [sudo-close-workingtree.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/commands/sudo-close-workingtree.md)**:
  - Command definition with mandatory safety gate: `git merge-base --is-ancestor claude/<story-slug> origin/main_debug`.
  - Automatically shifts directory out of `.claude/worktrees/<slug>` before removing local worktree.
  - Removes local worktree (`git worktree remove`) and deletes both local branch (`git branch -d`) and remote GitHub branch (`git push origin --delete`).
- **Created Workflow & Skill Mirrors**:
  - [sudo-close-workingtree.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/workflows/sudo-close-workingtree.md)
  - [SKILL.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/skills/sudo-close-workingtree/SKILL.md)
- **Updated Rules**:
  - [worktree-per-story.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/rules/worktree-per-story.md) and [git-policy.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/rules/git-policy.md) updated to document automatic worktree & branch pruning post-landing.
- **Updated [/sudo-update-sprint-memory](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/.agents/commands/sudo-update-sprint-memory.md)**:
  - Added **Step 8: Auto-Prune Merged Worktree & Branch**, invoking `/sudo-close-workingtree` immediately following Step 7 landing on `main_debug`.

---

### Platform & Project Synchronization

Executed `/sync-agents` across all agent platforms and child projects:
- **Claude**: `.claude/commands/` updated (21 commands).
- **Opencode**: `.opencode/commands/` + global cache `~/.config/opencode/commands` updated (47 commands).
- **Antigravity/Gemini**: Global cache `~/.gemini/antigravity/global_workflows` updated.
- **Codex**: Global prompts `~/.codex/prompts` + skills mirror `~/.codex/skills` updated.
- **Projects**: Vendored `.agents/` synced across all 7 projects:
  - `AGY_AVIATIONCHAT`
  - `Fresh_Workspace_BMAD`
  - `OpenChat-Openrouter`
  - `B-L-WorldWide`
  - `BRKN_Tattoos`
  - `NEXGen-Films`
  - `RAG_Pipeline_AC`

---

## Verification Results

### Automated Tests & Verification
1. **Sync Verification**:
   - `sync-agents.ps1` completed cleanly with 0 errors across all 7 projects and all 4 platform global caches.
2. **Safety Gate Verification**:
   - Tested `git merge-base --is-ancestor claude/21-12-fail-closed-admin-roles origin/main_debug` on an unmerged branch. Returned exit code `1`, correctly blocking deletion.

---

## Your Actions

The `/sudo-close-workingtree` command is now live across all platforms and projects.

When closing out a story via `/sudo-update-sprint-memory`, Step 8 will automatically invoke `/sudo-close-workingtree` after landing on `main_debug`. You can also manually run `/sudo-close-workingtree <story-slug>` at any time to verify and clean up any completed worktrees or remote branches.
