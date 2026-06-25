---
description: End-of-session save — updates active-context, captures learnings into component specs, prunes stale data
---

# /1_ccps_update-active-context — Session End (G1 close-out)

Execute the workflow defined in @.agent/workflows/1_ccps_update-active-context.md.

**opencode execution notes:**
- `// turbo` directives are advisory only in opencode; use normal tool permissions.
- Primary target: `_bmad-output/active-context/active-context.md`.
- Capture: what changed this session, new pitfalls discovered, files now in/out of play, what's stable vs broken.
- Edits to `active-context.md` will trigger the `edit: ask` permission gate — confirm with Don before each write.
- Per @AGENTS.md End-of-Task Checklist, also ensure `_claude_artifacts/<chat-slug>/walkthrough.md` and `your-action-required.md` exist for this session.

Optional additional input: $ARGUMENTS
