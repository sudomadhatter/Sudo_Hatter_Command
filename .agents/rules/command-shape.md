---
name: command-shape
description: "How to SHAPE a shell command so the platform allowlists can match it and its exit code stays readable. Load when a command you are about to run is compound (cd chains, && sequences), when a gate/test/script run is being piped or tailed, or when an approval prompt fires on a command you believed was allowlisted. Three bans: no cd-chains, no exit-echo tails, no piped gates."
trigger: model_decision
triggers: [allowlist, permission prompt, approval prompt, command shape, compound command, cd chain, exit code, run the gate, always proceed]
# Intent-shaped: the trigger is the act of composing a shell command, not a file being opened.
# Antigravity judges `description:`; `.agents/hooks/rule-trigger.py` matches the keywords above.
---

# Command shape — run gates BARE, or no allowlist can ever say yes

**The fact under all three bans:** every command allowlist this system runs on — Claude Code's
`permissions.allow` rules, Zoo Code's `zoo-code.allowedCommands`, opencode's `permission.bash`
map — is a **prefix matcher over the whole command string**. `git status` can be pre-approved;
`cd X && git status` can not, because the string starts with `cd`, and no finite rule set can
enumerate every compound spelling. A compound command is therefore an approval prompt **by
construction** — the "Always Proceed still prompts every command" pain is mostly self-inflicted
command shape, on every platform at once.

## The three bans

1. **No `cd X && …` chains.** Address the tree instead: `git -C <path> …`, absolute paths, or the
   tool's own working-directory parameter. Chains also break more than allowlists: in worktree
   lanes, a shell's cwd can silently reset to the MAIN checkout between calls, so a chained
   relative path can read the wrong tree even when it runs.
2. **No `; echo "EXIT=$?"` (or `&& echo OK`) tails.** The tail unmatches the prefix rule, and the
   shell's reported status becomes the `echo`'s — a dead gate can exit 0 behind it. The harness
   already shows you the exit code; asking for it again only destroys it.
3. **No piping a gate.** `pytest | tail`, `run_all.py | grep FAIL`, `gate.sh | tee log` all report
   the LAST command's status — the pipe hides the gate's own exit code (and `head` can kill the
   gate mid-run with SIGPIPE). Run gates bare and read the full output; if output must be captured,
   redirect (`> file 2>&1`) rather than pipe, then read the file.

## What is already handled — don't over-correct

- **Read-only chains** (`ls A && ls B`, grep/cat/find sequences) are legitimate and pass on Claude
  Code via the `.agents/hooks/allow-readonly-chain.py` hook (SCC-287). The other platforms have no
  such hook — so default to bare commands everywhere and let the hook be a bonus, not a habit.
- **Command substitution and redirects inside ONE simple command** (`git commit -F <file>`,
  `KEY=$(git rev-parse …)`) are fine; the bans are about compounding *commands*, not arguments.

## Why this is a rule and not a settings fix

SCC-346 promoted the stable allowlists into tracked settings on every platform. That work is
defeated retroactively by any agent that composes `cd repo && python3 gate.py; echo "EXIT=$?"` —
three approved operations spelled as one unapprovable string. The allowlists cover the vocabulary;
this rule keeps the grammar inside what they can match.
