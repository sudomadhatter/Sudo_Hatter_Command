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

## §Nag — when a rule keeps being broken, nag; do not write it again

**The operator's ruling (2026-09-01, SCC-369):** *"To correct an agent that keeps deviating from a
rule we can add a nag instead of adding more and more rules to hope they listen. The nag is more
effective than making more rules for the same thing in more places."* And the reason it works:
*"it's the perfect way to point an agent back to the rule they are not doing."*

**This rule is the case that proved it.** It already reached every platform — summarized in
`AGENTS.md` §6, restated in `zoo-team.md` for every Zoo seat, keyworded into
[`rule-trigger.py`](../hooks/rule-trigger.py), and firing as a `UserPromptSubmit` injection — and was
still broken in **1,933 of 7,858 Bash calls across 25 sessions: 98.9% of every detectable violation
in the transcripts.** Of 1,247 `git -C` invocations, 521 named a verb no allow rule can pre-approve,
so each was an approval stop that would have been silent in the shape rule 1 already mandates.
Distribution was never the gap. Compliance was, and a sixth copy would have changed nothing.

**The mechanism.** [`shape-guard.py`](../hooks/shape-guard.py) is a `PostToolUse` hook that reads the
command which just ran and, when it breaks rules 1–3 above, emits one line per broken rule **citing
this file by path** and naming the remedy. It sends the agent back to the law; it never restates it.

**Why a nag binds where prose does not.** Prose sits in context competing with everything else and is
read *before* the mistake. A nag arrives *at* the mistake, attached to the exact command that was
wrong. It is not an instruction to weigh — it is a fact about what just happened, and there is
nothing to rationalize past.

⛔ **Three limits, each load-bearing:**

1. **A nag may never block.** `permissionDecision: "ask"` becomes an auto-DENY in auto mode and would
   strand a headless run over a style note. `shape-guard.py` emits neither `decision` nor
   `permissionDecision` on any path, and `test_shape_guard.test_never_blocks` turns red if that ever
   changes — a mutant introducing either key is killed by that case.
2. **A nag cannot protect against a destructive command** — it speaks *after* the damage. `git add -A`
   and `git worktree remove --force` stay `PreToolUse` concerns and must never be moved here.
3. **`PostToolUse` → `hookSpecificOutput.additionalContext` is the only channel that reaches the
   model.** Established by probe, not assumption: `systemMessage`, hook stderr, and a `PreToolUse`
   `allow` with `permissionDecisionReason` were each tried and none of them arrived.

⛔ **Zoo Code gets no nag, because Zoo has no hook surface at all** — it contributes no notification,
sound or event hook, which is the same fact that forces `zoo_notify.py` to poll the thread store.
What Zoo gets instead is **measurement**: [`shape_scan.py`](../scripts/shape_scan.py) reads both
stores with this hook's own detector, so *"are the Zoo seats doing better"* is answerable with a
number rather than an impression. Baseline at 2026-09-01, as rules 3 / 2 / 1 — **Claude 9.49 / 9.36 /
5.79 %** over 8,122 commands, **Zoo 19.03 / 4.45 / 3.64 %** over 247.

**Before adding a nag for any other rule, measure it first.** The scope here is three rules because
those three were 98.9% of the violations. A nag that fires on rare or debatable shapes becomes noise,
and noise trains the agent to ignore every nag — including the ones that matter.
