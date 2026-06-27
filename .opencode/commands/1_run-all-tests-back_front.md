---
description: Run the complete backend (pytest) and frontend (vitest/jest) test suites and report results
---

# /1_run-all-tests-back_front — Full Test Suite

Execute the workflow defined in @.agents/workflows/1_run-all-tests-back_front.md.

**opencode execution notes:**
- Backend: `pytest` from project root (the `.venv` activation is handled by the workflow file).
- Frontend: `npm test` (or whatever the workflow specifies — defer to the canonical file).
- Per @.agents/rules/constitution.md "Always paste terminal output when reporting test results — no unsupported claims," paste the actual stdout/stderr in your response and in `_artifacts/<chat-slug>/walkthrough.md`.
- If any test fails, do NOT propose a fix until you've investigated root cause (constitution rule).

Optional additional input: $ARGUMENTS
