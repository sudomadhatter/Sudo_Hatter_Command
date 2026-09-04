---
name: smh-close-task-merge-tree
description: Close out TASK work — a `chore/<JIRA-KEY>-<slug>` branch that never got an epic and a story, so BMAD's `/cicd-close-story-merge-tree` cannot close it. Preflights mechanically (branch shape, clean+pushed, main absorbed, and THE LANE — did anything deployable change?), runs the gate the lane selects, then OPENS A PULL REQUEST AND STOPS: it never merges. The operator's DECISION to proceed is the sign-off (the word approved, or invoking this command or /cicd-push-e2e); their click on Merge pull request is how that decision reaches GitHub, gated by the main-write-gate check. Re-invoked as `--after-merge <KEY>` it verifies the merge with plain git, files the Jira Dev Record, moves the Task to Done, and prunes the worktree AND the branch (SCC-62 — unlink assets before removing the tree; a recursive delete through a junction eats the shared targets). Refuses the moment a deployable path is in the diff and hands the work to `/cicd-push-e2e`.
---

# Close Task Merge Tree

Native skill entry point for the non-BMAD Task close-out. The workflow body stays in one canonical file
so its safety gates cannot drift between command surfaces.

**Execute now:** read `.agents/commands/smh-close-task-merge-tree.md` relative to the repository root and
follow it **END TO END**, passing the user's arguments through verbatim. **The operator's DECISION to
proceed is the sign-off** — the word `approved`, or invoking this command or `/cicd-push-e2e` — and from
that word on every step is the ceremony's and you run it (their click on *Merge pull request* is how the
decision reaches GitHub, never work they owe). If the command file is absent, STOP and report the missing
canonical workflow; never reconstruct the close-out from memory.

⛔ **On `--after-merge`, check that the door you are reading is CURRENT** (SCC-193 C). This command is
the one most likely to be reading a file its own lane just rewrote:

```bash
BEHIND=$(cd "$REPO" && git rev-list --count HEAD..origin/main)
```

If that is not `0`, this checkout is **behind origin/main by N** and the door text you are following
may be the PRE-merge copy — read `git show origin/main:.agents/commands/smh-close-task-merge-tree.md`
and follow that instead.
