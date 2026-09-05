---
name: nag-the-agent-dont-rewrite-the-rule
description: "When an agent keeps deviating from a rule, add a PostToolUse nag that points it back at the rule file — never another copy of the rule in another place. Restating law in a fifth location changes nothing; a message injected at the moment of the mistake does."
metadata:
  probe: "test -e .agents/hooks/guard-cwd-escape.py"
  node_type: memory
  type: feedback
  originSessionId: ba4e43b2-b8f7-48f3-b17a-23f1396a6d8b
  modified: 2026-09-01T00:00:00.000Z
---

The operator's ruling, 2026-09-01: **to correct an agent that keeps deviating from a rule, add a
nag — do not add the rule again in more places hoping it listens.**

**The measurement that produced it.** `command-shape.md` was already standing law on every
platform: summarized in `AGENTS.md` §6, restated in `zoo-team.md` for every Zoo seat, keyworded
into `rule-trigger.py`, and it fired twice as a `UserPromptSubmit` injection during the session
that measured this. A scan of 25 sessions / 7,858 Bash calls (negative + positive control
batteries both green) still found **1,933 violations of that one rule — 98.9% of every detectable
violation in the transcripts**. Of 1,247 `git -C` invocations, **521 named a verb the allow list
cannot pre-approve**, and every one of those would have been silent in the `cd <abs> && git <verb>`
shape the rule already mandates. Distribution was never the gap. Compliance was, and the expensive
model failed it exactly like the cheap ones ([[cheap-models-rationalize-past-prose]]).

**Why a nag works where prose does not.** Prose lives in context, competing with everything else in
context, and is read *before* the mistake. A nag arrives *at* the mistake, unmissable, attached to
the exact command that was wrong. It cannot be argued past because it is not an instruction to
weigh — it is a fact about what just happened.

**How to apply.** A `PostToolUse` hook, `hookSpecificOutput.additionalContext`. Verified by probe
this session — that field reaches the model verbatim; `systemMessage`, hook stderr, and
`PreToolUse` `permissionDecision: allow` + `permissionDecisionReason` **all fail to reach it**.
A newly registered hook loads mid-session, no restart.

- **Cite the rule file in the message**, don't just restate the fix — the point is to send the
  agent back to the law it skipped.
- **`PostToolUse`, not `PreToolUse`.** It runs after the command, so it can never block, slow, or
  wedge a headless session. Cost measured at ~36 ms, entirely off the critical path (the existing
  four-hook `PreToolUse` chain is ~145 ms).
- ⛔ **Never `permissionDecision: "ask"`** — it becomes an auto-DENY in auto mode and strands
  headless runs ([[hook-ask-becomes-autodeny-in-auto-mode]]).
- ⛔ **A nag cannot protect against a destructive command** — it speaks after the damage. `git add -A`
  and `git worktree remove --force` belong in a `PreToolUse` guard, not here
  ([[worktree-remove-force-eats-untracked-memories]]).
- **Rank candidates by measurement, never by impression.** Scan the transcripts, and build negative
  controls first — the first cut of that scanner counted a `grep "git -C"` as a use of `git -C` and
  heredoc bodies as commands ([[audit-findings-need-a-file-anchor]]).

Template: `.agents/hooks/guard-cwd-escape.py` — including its fails-open discipline, which is about
crashes only and never about staying quiet on a real hit.

Related: [[zoo-approvals-decision-store]] · [[one-door-per-platform-per-command]]
