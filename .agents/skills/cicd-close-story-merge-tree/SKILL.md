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

⛔ On a **FULL or LIGHT** epic it lands by a pull request into the **epic branch** (which it merges itself —
the epic's ruleset decides which checks run) and stops. On **TRUNK** it opens the pull request into `main`
and STOPS — `main` is reached only through a PR the operator merges, here or via `/cicd-push-e2e`. It reads the
mode from `epic_mode.py` at Step 0, never from belief.

**Execute now:** read `.agents/commands/cicd-close-story-merge-tree.md` (relative to the repo root) and
follow it END TO END. Its **Step 0** resolves which child to target — a leading `$ARGUMENTS` project name,
else the `.agents/active-project.txt` pointer, else it asks Daniel. Pass `$ARGUMENTS` through verbatim.
