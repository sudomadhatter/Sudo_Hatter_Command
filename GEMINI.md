# Entry — Sudo_Hatter_Command (Gemini / Antigravity)

**CRITICAL MANDATE:** You MUST read and strictly follow all instructions, rules, and workflows defined in `AGENTS.md` located in this exact folder. This is a hard directive. You are strictly prohibited from ignoring the `AGENTS.md` file or its contents. It is the absolute single source of truth for all workflows, protocols, and behavioral rules in this system. Do not proceed with any task until you have fully assimilated the rules in `AGENTS.md`.

## GEMINI SPECIFIC HARD RULES:
1. **SYNC MAINTAINED PROJECTS ONLY**: NEVER run `sync-agents` across all `Projects/*` directories or hand-loop over `Projects/`. Sync MUST ONLY target the lobby or use `& ".agents/scripts/sync-agents.ps1" -Maintained` which restricts multi-project sync strictly to `.agents/maintained-projects.txt` (the top maintained projects: `AGY_AVIATIONCHAT`, `Fresh_Workspace_BMAD`).
2. **WORKTREE ENFORCEMENT BEFORE CODE EDITS**: Before editing any project source files for a story, feature, or fix, Gemini MUST create and switch into a dedicated git worktree branched from the story's epic branch (e.g. `git worktree add -b claude/<slug> .claude/worktrees/<slug> epic/<epic-slug>`). NEVER edit project files directly on `main` or an epic branch.
3. **EXPLICIT GIT COMMITS ONLY**: NEVER use wildcard staging (`git add -A`, `git add .`, `git add -u`). Always stage explicit file paths and verify `git diff --cached --stat` before committing.

