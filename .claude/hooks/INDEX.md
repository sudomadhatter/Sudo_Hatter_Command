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

## Top-level contents
<!-- auto-listed by /smh-update-maps-indexes — refresh via /smh-update-maps-indexes; do not hand-edit entries -->
- `allow-scratchpad.py`
- `guard-cwd-escape.py`
- `log-rule-load.sh`
- `require-push-approval.py`
- `rule-trigger.py`
- `run-hook.sh`
- `session-start-context.sh`
