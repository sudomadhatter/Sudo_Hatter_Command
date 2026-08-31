---
name: command-shape
description: "How to SHAPE a shell command so the platform allowlists can match it and its exit code stays readable. Load when composing any compound command (&& sequences, worktree-pinned git), when a gate/test/script run is being piped or tailed, or when an approval prompt (or auto-refusal) fires on a command you believed was allowlisted. The law: pin with `cd <abs> && <cmd>` in ONE line (never git -C — Zoo auto-denies it), no exit-echo tails, no piped gates."
trigger: model_decision
triggers: [allowlist, permission prompt, approval prompt, auto-denied, command shape, compound command, cd chain, exit code, run the gate, always proceed]
# Intent-shaped: the trigger is the act of composing a shell command, not a file being opened.
# Antigravity judges `description:`; `.agents/hooks/rule-trigger.py` matches the keywords above.
---

# Command shape — pin with `cd … && …`, run gates BARE

**The fact under all of it (verified by executing Zoo v3.80.1's own extracted matcher, SCC-351):**
both major permission layers judge a compound command **per piece**. Zoo Code splits on newlines,
`&&`, `||`, `;`, `|` and matches each piece **lowercase, starts-with, longest prefix wins**; Claude
Code evaluates each segment against its pattern rules. So `cd <abs> && git status` is TWO matchable
pieces on both platforms — while `git -C <path> status` is ONE piece that starts `git -C`, which no
verb rule can ever see. Under a broad `git ` allow, `-C` would also ride PAST every verb deny, so
the tracked Zoo lists **auto-deny `git -C` and `git --git-dir` outright**. Full mechanics and the
canonical lists: [docs/migrations/zoo-code-permissions-guide.md](../../docs/migrations/zoo-code-permissions-guide.md).
(An earlier cut of this rule banned cd-chains and mandated `git -C` — that inverted on 2026-08-30
when the extracted matcher proved piece-splitting; the doors were rewritten in SCC-351.)

## The law

1. **Pin the tree in the SAME compound line: `cd <abs path> && git <verb> …`** — never `git -C`,
   and never a bare `git` that trusts an earlier call's `cd`. A shell's cwd can silently reset to
   the MAIN checkout **between** calls (worktree lanes, SCC-337); a pin that lives in the same
   line cannot go stale. Repeat the `cd` per line — every command self-contained.
2. **No `; echo "EXIT=$?"` (or `&& echo OK`) tails.** The tail adds an approvable-looking piece
   while the shell's reported status becomes the `echo`'s — a dead gate can exit 0 behind it. The
   harness already shows the exit code.
3. **No piping a gate.** `pytest | tail`, `run_all.py | grep FAIL`, `gate.sh | tee log` report the
   LAST command's status — the pipe hides the gate's own exit code (and `head` can kill the gate
   mid-run with SIGPIPE). Run gates bare; to capture, redirect (`> file 2>&1`) and read the file.

### Absolute fills, and the lobby pin (close-out review, SCC-351)

Two consequences of `cd <path> && …` that `git -C` never had, both measured in this lane's review:

- **Fills are ABSOLUTE.** A `cd` moves the shell, so the SECOND `cd <same-relative-path> && …`
  line in a fence runs from inside the first and dies. `PROJECT_ROOT` now binds absolute
  (`smh-target-resolution.md` §BIND), tree fills are `"$PROJECT_ROOT"/.claude/worktrees/<slug>`,
  and any other repeated fill is resolved once — `P=$(cd <fill> && pwd)` — then pinned as
  `cd "$P" && …` per line.
- **A lobby-relative script call after ANY `cd` needs the lobby pinned first.** The helper
  scripts live in the LOBBY's `.agents/scripts/`; once a fence (or an earlier fence — cwd
  persists between tool calls) has `cd`'d into a project or a worktree, a bare
  `python3 .agents/scripts/<tool>.py` resolves against a tree that does not carry the script.
  Capture `L=$(pwd)` at the top of the fence, before any `cd`, and pin the call:
  `cd "$L" && python3 .agents/scripts/<tool>.py …`. (`L=` is on the Zoo allow list.)

## §Zoo — extra shape rules for Zoo Code seats (mirrored from the guide §8)

- **One logical line per command.** No backslash continuations — the continuation lines become
  orphan pieces that match nothing and force a prompt.
- **No shell loops or multi-line `if` blocks** in terminal commands (`do …`/`fi` pieces match
  nothing). Iterate in python, or repeat the call.
- **No `$( … && … )` compounds** — a subshell body is scored as ONE unsplit piece, which both
  defeats matching and launders. Plain `VAR=$(cd X && git …)` for a door-printed read is fine.
- **Multi-line payloads go inside quotes or a heredoc** (they survive as one approvable piece), or
  write the script with the file tools and run `python3 <file>`.
- **Prefer the door text verbatim** — the doors are kept in this shape by the suite
  (`test_zoo_permissions.py` pins doors `git -C`-free and fires a destructive battery + the
  ceremony set against the tracked lists on every run).

## What is already handled — don't over-correct

- **Read-only chains** (`ls A && ls B`, grep/cat sequences) pass on Claude Code via the
  `.agents/hooks/allow-readonly-chain.py` hook (SCC-287) and on Zoo via the read-only allows.
- **Command substitution and redirects inside ONE simple command** (`git commit -F <file>`,
  `KEY=$(cd "$REPO" && git rev-parse …)`) are fine; the bans are about compounding *gates* and
  about shapes the matchers cannot see into.
- **opencode** still prefix-matches the WHOLE string, so compounds prompt there. Its surface is
  the BMAD wrapper set only — accept the prompt; do not reshape doors around it.

## Why this is a rule and not a settings fix

SCC-346 promoted stable allowlists into tracked settings on every platform; SCC-351 fixed the
decision store and proved the matcher. That work is defeated retroactively by any agent that
composes `python3 gate.py; echo "EXIT=$?"` or resurrects `git -C`. The lists cover the vocabulary;
this rule keeps the grammar inside what the matchers can say yes to.
