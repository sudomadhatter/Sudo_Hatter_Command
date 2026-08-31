---
description: Read the agent's own chat threads, find the terminal commands that stopped for approval, and print the allow rows that would have...
platforms: [opencode, antigravity, claude, codex, zoo]
---

# /smh-llm-approvals — grow the allow list from what actually got blocked

**The problem, in one sentence:** Zoo Code stops and asks before running a terminal command it
does not recognise, and the only way to stop it asking is for somebody to read the thread by eye,
work out which prefix would have covered the command, and add that prefix by hand.

**Why Zoo and not everyone.** Claude Code puts a *don't ask again* button in its own approval
prompt, so its allow list grows as you work. Zoo has no such button. Its decisions live in VS
Code's `globalState` database, the tracked settings file seeds that store **once** on a fresh
machine, and denies never seed at all — so the list only ever grows when a human sits down and
grows it. Zoo is the platform that cannot help itself, and it is the one this door serves.

⛔ **This door PRINTS. It writes no list, on any platform.** Not the tracked settings file, not
the memento, not `.claude/settings.json`. You pick the rows; a door that edits an approval list
is a door that can approve things on its own behalf.

---

## Step 1 — run the reader

```bash
python3 .agents/scripts/llm_approvals.py            # PC: python
```

`--limit N` reads the newest N threads (default 20).

It prints the store root it scanned, how many threads it read, how many commands stopped for
approval, and then one proposed row per family with the commands that row would unblock.

**A zero-result run still prints all of that**, deliberately. "Nothing was blocked" and "the door
is pointed at the wrong store" are the same empty screen otherwise, and the root it names is what
tells the two apart — a worktree and the lobby genuinely resolve different counts.

## Step 2 — read the rows, and know what you are widening

Each row is the **shortest prefix that ends on a whole word** and would have let its command
through. Shortest is not the same as safest, and the floor is the reason:

> Measured against the live lists, the shortest *character* prefix that unblocks
> `npx create-next-app my-app` is the single letter `n`. It trips none of the 78 destructive
> commands this repo tests against — and it silently auto-approves `npm publish`, `node evil.js`,
> `nc -l 4444` and `netsh advfirewall set allprofiles state off`. So a row never stops inside a
> word it did not finish, and `npx` is what you are offered.

Three kinds of command never reach the list at all: one the lists already allow (the row that
fixed it landed since), one the deny list refuses (this door grows the allow list; the deny list
is the fence), and a duplicate of a row already shown.

## Step 3 — apply the ones you want

Add the rows you picked to `zoo-code.allowedCommands` in `.vscode/settings.json`, then:

```bash
python3 .agents/scripts/zoo_permissions_apply.py --apply     # PC: python
```

**Quit VS Code fully first.** It flushes its own `globalState` on exit and would overwrite the
write — the apply script refuses to run while VS Code is up, and says so. The closing `--status`
must read *in sync with tracked file*. Full background:
[zoo-code-permissions-guide.md](../../docs/migrations/zoo-code-permissions-guide.md).

---

## And for Claude — a hand-off, not a writer

The same run also reads your recent Claude sessions and prints a **paste-ready block** for an
agent that can edit `.claude/settings.json`. Claude Code cannot edit its own settings, so the
block is the deliverable: hand it to another agent and it does the edit.

It names **one** store — the `.claude/settings.json` of the repo you ran the door in, as an
absolute path. This workspace holds several of those files and they all differ, so "add it to
`.claude/settings.json`" names nothing anyone can act on.

Two things worth knowing about how the rules are derived, both found by running this against real
sessions rather than by reading the code. A refusal often carries several commands (a `cd`, then
a `git`, then a `python3`), so every one of them gets a rule — one rule for the first would have
you approving the same block again tomorrow for the second. And a leading `VAR=value` is shell
setup, not a command: naming it produces a rule that matches exactly one string nobody will type
again.

---

## What this door does NOT do

- It does not touch the **deny** list. Allows may be broad; denies are the fence.
- It does not apply anything. Step 3 is yours, and `zoo_permissions_apply.py` is a separate
  command with its own refusals.
- It does not run per project. The store is per machine, so the rows are too.

Optional additional input: $ARGUMENTS
