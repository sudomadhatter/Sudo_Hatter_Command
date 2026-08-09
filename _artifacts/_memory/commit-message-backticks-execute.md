---
name: commit-message-backticks-execute
description: "Backticks inside a double-quoted `git commit -m \"...\"` are bash COMMAND SUBSTITUTION — a message quoting a git command executes it. On 2026-08-09 it silently created and switched to a branch. Write messages containing backticks to a file and use -F."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 63b6a0a8-7c68-4b96-a542-187c8ce6bea3
  modified: 2026-08-09T17:58:40.541Z
---

**`git commit -m "... \`git checkout -b foo\` ..."` RUNS the backticked command.** Bash substitutes
before git ever sees the string, so the message loses that text (replaced by the command's stdout,
usually empty) **and** the side effect lands.

Observed 2026-08-09 (SCC-62, skeleton repo): a commit message describing the fix quoted the README line
it was replacing — `` `git checkout -b main_debug` `` — inside `-m "..."`. Bash created the branch,
switched to it, and the commit landed on `main_debug`, **the exact branch that commit was deleting**.
The message was corrupted to "the setup step literally ran , plus …".

**Why this system is unusually exposed:** Sudo_Hatter_Command is a git-workflow toolkit. Commit messages
here routinely quote `git` commands, branch names, and script invocations — the highest-risk content
there is. Any `$(...)`, `` ` ` ``, or bare `$VAR` in a double-quoted `-m` has the same problem.

**How to apply:** if a commit message contains a backtick, `$`, or `!`, write it to a file and use
`git commit -F <file>` (or `--amend -F`). Never reach for `-m "..."` with shell metacharacters. Single
quotes also neutralize it, but they break on any apostrophe, so the file is the reliable habit.

**Why it is recoverable but must not be ignored:** it announces itself (`Switched to a new branch 'x'`
appears between the `git add` and `[branch sha]` lines) — but only if you READ the commit output instead
of assuming success. Recovery while unpushed: `git checkout <intended-branch>` →
`git merge --ff-only <accidental>` → `git commit --amend -F <file>` → `git branch -D <accidental>`, then
prove it with `git branch --list` and `git ls-remote --heads origin`.

Relates to [[commit-and-push-are-one-action]] and [[piping-a-gate-hides-its-exit-code]] — all three are
the same lesson: the shell is a participant in your command, and its exit code or side effects are not
the ones you assumed.
