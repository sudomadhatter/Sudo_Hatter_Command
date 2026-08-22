---
name: cicd-update-sprint-memory
description: 'Command center → child project. The story SAVE — code-verify the claimed work, route every learning to its home, update the board / story file / active-context, flip the closed story to done, and hold the context budget. It performs NO landing, NO ticket write and NO prune: that is the door, /cicd-close-story-merge-tree, which invokes this as its Step 1. Use when the user says "save the session" / "update sprint memory".'
---

# /cicd-update-sprint-memory — command center launcher (the story SAVE)

Command-center (lobby) entry point for the session/story save. It saves into a CHILD project under `Projects/`
(e.g. `AGY_AVIATIONCHAT`), never the lobby — except the memory write, which is global.

⭐ **Since SCC-210 this command does exactly what its name says and nothing more.** It used to be the whole
story close-out — it landed the branch, moved the Jira ticket, filed the Dev Record and called the prune — so the
command an operator typed to close a story was named after a side effect. Those steps live in
**`/cicd-close-story-merge-tree`**, which invokes this as its Step 1. Everything written here is a FILE write that
rides the story branch, which is what makes it safe to run before a landing.

**Execute now:** read `.agents/commands/cicd-update-sprint-memory.md` (relative to the repo root) and
follow it END TO END. Its **Step 0** resolves which child to target — a leading `$ARGUMENTS` project name,
else the `.agents/active-project.txt` pointer, else it asks Daniel. Pass `$ARGUMENTS` through verbatim.
