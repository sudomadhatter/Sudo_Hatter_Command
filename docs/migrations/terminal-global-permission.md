# Terminal approvals, globally — every agent, every store (SCC-351)

**The one page for "which agent will ask, where its decision actually lives, and how to add an
approval that sticks."** Each agent carries its OWN store and its OWN matcher — there is no VS Code
master permission system governing extensions, and editing the wrong surface changes a display, not
a decision. Standing design (operator ruling, 2026-08-30): **allows are broad; denies are the
fence** — the deny list is the minimum set naming real damage, because under a broad allow an
un-denied spelling does not ask, it RUNS.

| Agent | Decision store | Matcher | Add an approval that sticks |
|---|---|---|---|
| **Claude Code** | `.claude/settings.json` (tracked `permissions.allow` rules) + `.claude/settings.local.json` (machine-local, gitignored, linked into worktrees) + `~/.claude/settings.json` | per-rule `Bash(prefix:*)` patterns, judged per command segment | add the rule to the right tier (tracked for the team, local for the machine); live immediately. Deep dive: [claude-terminal-permission.md](claude-terminal-permission.md) |
| **Zoo Code** (VS Code) | VS Code globalState `state.vscdb` — the tracked [`.vscode/settings.json`](../../.vscode/settings.json) `zoo-code.*` lists SEED it exactly once and never again | lowercase starts-with per command PIECE, longest prefix wins allow-vs-deny, tie → deny | edit the tracked lists → `python3 .agents/scripts/tests/test_zoo_permissions.py` must stay green → quit VS Code → `python3 .agents/scripts/zoo_permissions_apply.py --apply` (PC: `python`) → reopen. Deep dive: [zoo-code-permissions-guide.md](zoo-code-permissions-guide.md), SOP §13 row |
| **opencode** | its own config under `.opencode/` | WHOLE-string prefix (no per-piece split) — compounds rarely match | accept prompts, or add whole-string prefixes by hand. **Deliberately not automated** (SCC-354): a whole-string matcher has no useful prefix to propose — the row that unblocks one compound command unblocks that command and nothing else, so a proposer would emit one row per invocation and grow a list nobody can read. |
| **Codex** | `~/.codex/` config (`approval_policy` / sandbox), per machine | policy-level, not per-command lists | set the policy per machine. **Deliberately not automated** (SCC-354): there is no per-command list to grow — the policy is the whole decision, so there is nothing for a proposer to propose. |
| **Gemini / Antigravity** | retired — VS Code + Zoo replaced Antigravity (SCC-349); Gemini CLI keeps its own `~/.gemini` config | — | — |

**Command shape matters as much as the lists.** The house pin idiom is `cd <abs> && git <verb>` in
ONE compound line — `git -C` is auto-denied as a launder shape, fills are absolute, and a lobby
script called after any `cd` needs the lobby pinned first. The law: `.agents/rules/command-shape.md`
(§The law, §Absolute fills, §Zoo).

**Growing the lists without re-reading sessions by eye** is SCC-352: the `/smh-llm-approvals` door
reads recent agent threads, replays every command that stopped for approval through the real
matcher, and PROPOSES the minimal new allow rows per platform — the operator picks; nothing is ever
auto-added.
