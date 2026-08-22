---
name: cicd-close-story-merge-tree
description: 'Command center → child project. THE DOOR you type to close ONE story out: preflight, run the sprint-memory save, commit the close-out edits, LAND the story on its EPIC branch, and only THEN file the Dev Record and move the Jira ticket, then prune the worktree. Invoking it IS Daniel''s sign-off for THIS story''s landing, and that sign-off is spent by it. Use when the user says "close out the story" / "land this story" / "close out".'
---

# /cicd-close-story-merge-tree — command center launcher (the story close-out door)

Command-center (lobby) entry point for closing ONE story out. It saves into a CHILD project under `Projects/`
(e.g. `AGY_AVIATIONCHAT`), never the lobby — except the memory write, which is global.

**What it owns.** The order is the safety property: everything the save writes is a FILE write that rides the story
branch, so a landing that stops publishes nothing — while the Jira ticket write rides no branch and cannot be taken
back, which is why it happens only after the landing push returns 0 (SCC-210).

⛔ It lands on the **epic branch** and stops. `main` is reached only via `/cicd-push-e2e`.

**Execute now:** read `.agents/commands/cicd-close-story-merge-tree.md` (relative to the repo root) and
follow it END TO END. Its **Step 0** resolves which child to target — a leading `$ARGUMENTS` project name,
else the `.agents/active-project.txt` pointer, else it asks Daniel. Pass `$ARGUMENTS` through verbatim.
