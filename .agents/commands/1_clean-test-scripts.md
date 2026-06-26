---
description: List and clean up accumulated temp files in _test_scripts/. Shows contents, asks what to keep, deletes only on approval.
---

# /1_clean-test-scripts — Clean _test_scripts/

Execute the workflow defined in @.agents/workflows/1_clean-test-scripts.md.

**opencode execution notes:**
- Step 1: list contents of `_test_scripts/` with sizes and modified dates. Do NOT delete anything yet.
- Step 2: present the list to Don. Ask which to keep / delete / archive.
- Step 3: Only after explicit confirmation per file (or per group), delete. Each `Remove-Item` will trigger the permission gate.
- Per @.agents/rules/constitution.md "⚠️ Ask First: Before deleting any file."
- If Don wants bulk delete, confirm the bulk list once and proceed.

Optional additional input: $ARGUMENTS
