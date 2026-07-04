---
description: Interactive Firestore user data cleanup — list, wipe, or delete users from the aviationchat-database
---

# /1_firebase-user-cleanup — Firestore User Cleanup

Execute the workflow defined in @.agents/workflows/1_firebase-user-cleanup.md.

**opencode execution notes:**
- This is an **interactive, destructive** data operation on the Firestore `users` collection (database `aviationchat-database`). The backing script is `backend/scripts/firebase_user_manager.py` and uses `auth_keys/service-account.json` (resolved via the standard credential-resolution pattern).
- Step 1: run `python -m backend.scripts.firebase_user_manager list` and present a clean summary table to Don.
- Step 2: use the `ask_question` tool to offer the four operations (wipe / delete / batch-delete orphans / selective wipe by group).
- Step 3: identify target UID(s) from the audit table.
- Step 4: **ALWAYS dry-run first** (run the command WITHOUT `--confirm`) and show Don exactly what would be deleted.
- Step 5: only after Don explicitly approves the dry-run output, re-run WITH `--confirm` to execute.
- Step 6: re-run `list` to verify and report before/after state.
- The `--group` flag targets `learning` / `activity` / `personal` / `system` subcollection groups (see the workflow's reference table).
- Honor @.agents/rules/constitution.md "⚠️ Ask First: Before changing Firestore schemas, security rules, or database topology" — this workflow touches live user data, so the dry-run → explicit-approval gate is mandatory.
- Do NOT run `git commit` or `git push`; this workflow produces no code changes.

Optional additional input (UID or operation hint): $ARGUMENTS
