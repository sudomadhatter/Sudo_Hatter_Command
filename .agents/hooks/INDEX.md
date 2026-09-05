# hooks — INDEX

PreToolUse/PostToolUse hooks (e.g. `require-push-approval.py`). MASTER here — mirrors to `.claude/hooks/` and project vendored copies via `/smh-sync-agents`.

⚠ **This is the Claude-only layer and nothing depends on it.** The `main` write gate is
`.githooks/pre-push` (pure `sh`, no interpreter) — see `.agents/rules/git-policy.md` § "The write
gate". These hooks prompt earlier and read better; if they die, the gate still holds. That
separation exists because every hook here was wired to `powershell`/`python` — neither of which
exists on the Mac — and exited 127 in silence for weeks (SCC-77).

## The two rule-activation hooks

`.agents/rules/` reaches the agent two ways and, until SCC-277, only one of them worked. These close
the other half and then prove it fired.

| File | Event | What it does |
|---|---|---|
| `rule-trigger.py` | `UserPromptSubmit` | Matches the prompt against each rule's `triggers:` keyword list and prints **at most three pointers** — path and one-line description, never the rule body. This is the INTENT trigger: "the suite is red" reads no file, so `paths:` can never fire, and twelve rules carry a `triggers:` list that nothing read before this. |
| `log-rule-load.sh` | `InstructionsLoaded` (`path_glob_match`) | Appends each loaded instruction file to `${TMPDIR:-/tmp}/claude-rule-loads.log`. A **probe, not a gate** — the only way to observe that the FILE trigger (`paths:` → `.claude/rules/`) actually fired, instead of assuming it. |

Matching is **word-set**, not substring: every word of a trigger must appear in the prompt, in any
order. `reproduce-before-you-fix` lists `red suite`; an operator writes "the suite is red". A
substring matcher misses the phrasing people actually use.

Both fail open — see the ⚠ above. `test_rule_trigger.py` pins the pointer cap, the ranking, the
word-set matcher, and two ways of failing open (a malformed rule, a tree with no rules at all).
The end-to-end check is `_routing-canary/README.md` § "Probe 2".

## The two auto-allow hooks, and the line between them

Both remove approval prompts and neither can ever add one: their only outputs are `allow` and
SILENCE. They cover **different shapes**, and the split is deliberate.

| File | Covers | Allow-list is over |
|---|---|---|
| `allow-scratchpad.py` | ONE simple command, no shell metacharacter at all, every argument inside this session's disposable scratchpad | **paths** — so a construct it misparses is a write in the wrong place, which is why it refuses every metacharacter (SCC-263, fourteen escapes) |
| `allow-readonly-chain.py` | a COMPOUND command — pipes, `&&`, `;`, newlines — where every atom is a read-only verb AND already matches one of the operator's own `permissions.allow` rules | **verbs and flags** — every verb on it reads, so quotes and separators can be admitted, paid for by an exact quote-aware split and a per-verb flag allow-list |

⭐ **`allow-readonly-chain.py` grants nothing new, and that is testable rather than asserted.**
Condition (B) requires each atom to match a rule the operator already wrote, so every atom would
auto-approve on its own as a separate call. It removes the prompt on running them in one call.
Measured over one session: 19% → 39% of Bash calls auto-approved, 94 prompts removed of 375.

⚠ **The general lever is `/sandbox`, not either of these.** With sandboxing on,
`autoAllowBashIfSandboxed` (default true) auto-allows every command that runs inside it, whatever
its shape — no verb list at all. These two hooks are what works while it is off, or where a
command must run outside it.

## The nag hooks — the ones that speak AFTER the call

| File | Event | What it does |
| --- | --- | --- |
| `shape-guard.py` | `PostToolUse` | Points the agent back at `.agents/rules/command-shape.md` when a Bash call breaks it — a piped gate (rule 3), a `; echo "EXIT=$?"` tail (rule 2), or the `git -C` spelling (rule 1). It **cites the rule and names the remedy**; it does not restate the law. (SCC-369) |
| `closeout-nag.py` | `PostToolUse` | Nags an agent back to `.agents/rules/git-policy.md` and the lane close-out command (`/smh-close-task-merge-tree` or `/cicd-close-story-merge-tree`) when a `git push` targets `main`, a checkout/merge onto `main` is attempted, or a `git push` / `gh pr create` fails. (SCC-381) |

**Why these are `PostToolUse` and every other hook here is not.** The law they enforce was already
on every platform and was violated repeatedly across sessions. Distribution was never the gap, so the answer is not another copy of
the rule; it is a message at the moment of the mistake (SCC-369, SCC-381). Running
after the call means they **cannot block, slow, or wedge a headless session** — the strongest safety
property in this directory, bought by giving up the ability to prevent anything.

⛔ **They must never block, and `test_shape_guard.py::test_never_blocks` and `test_closeout_nag.py::test_never_blocks` are what hold that.**
`permissionDecision: "ask"` becomes an auto-DENY in auto mode, and a PostToolUse `decision: "block"`
feeds an error to the model; either would strand a headless run over a style note.

⛔ **A nag cannot protect against a destructive command** — it speaks after the damage. `git add -A`
and `git worktree remove --force` are deliberately *not* nagged; they belong to the PreToolUse
guards above.

⭐ **The channel was established by probe, not assumption:** `hookSpecificOutput.additionalContext`
reaches the model verbatim, while `systemMessage`, hook stderr, and a `PreToolUse` allow +
`permissionDecisionReason` all do not.

## Top-level contents
<!-- auto-listed by /smh-update-maps-indexes — refresh via /smh-update-maps-indexes; do not hand-edit entries -->
- `allow-readonly-chain.py`
- `allow-scratchpad.py`
- `closeout-nag.py`
- `guard-cwd-escape.py`
- `log-rule-load.sh`
- `require-push-approval.py`
- `rule-trigger.py`
- `run-hook.sh`
- `session-start-context.sh`
- `shape-guard.py`

