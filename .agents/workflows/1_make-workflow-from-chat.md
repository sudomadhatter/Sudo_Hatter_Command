---
description: Distill the current chat into a reusable workflow file — extracts problem-solving process, decisions, and code into a reproducible workflow.
---

# /1_make-workflow-from-chat — Chat-to-Workflow Extraction

Execute the workflow defined in @.agents/workflows/1_make-workflow-from-chat.md.

**opencode execution notes:**
- Analyze the entire preceding chat (not just $ARGUMENTS).
- Distill: problem statement, architectural decisions made, the actual fix/feature, edge cases discovered, tests added.
- Output target: a new file under `.agents/workflows/<descriptive-name>.md` with the same frontmatter shape as existing workflow files (`description:` + body).
- **Also create the opencode mirror**: copy/adapt the new file to `.opencode/commands/<descriptive-name>.md` so it becomes a slash command in opencode too. The opencode mirror should reference `@.agents/workflows/<descriptive-name>.md` (the pattern used by all other workflow ports in `.opencode/commands/`).
- After both files exist, run `/slash_command_updating` to sync to the global directory.
- Save a copy/summary into `_artifacts/<chat-slug>/walkthrough.md` so the extraction itself is auditable.

Optional additional input (focus area or naming hint): $ARGUMENTS
