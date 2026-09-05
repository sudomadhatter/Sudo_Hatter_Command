# SCC-415 — Stop the approval prompts at their measured cause: unmatchable command shapes

**Ticket:** SCC-415 (subtask of SCC-411, the open rolling ticket) · **Branch:** `chore/SCC-415-approval-sandbox-harvest` · **Lane:** the lobby, same working tree (operator's instruction)

## Why

Measured over the 20 newest Claude sessions (10,527 Bash calls), the operator spent **15 hours**
waiting on Bash calls that were sandboxed, matched an allow rule, hit no violation and were refused by
nothing — and still stopped. Classified by the SHAPE of the command:

| Shape | Calls | Operator time |
|---|---|---|
| heredoc — `python3 - <<'PY' … PY`, `git commit -F - <<'MSG'` | 54 | **7h 17m** |
| leading `VAR=` assignment — `S=/tmp/…; python3 …` | 40 | **5h 44m** |
| `$( )` substitution / shell control flow | 11 | 26m |
| genuinely long-running search or suite (runtime, not a stop) | 111 | 1h 31m |

**Thirteen of the fifteen hours are two shapes the prefix matcher cannot read.** `Bash(python3:*)`
matches `python3` and then sees a body it cannot judge; no rule begins with `S=`. Both fall through to
the auto-mode classifier, which takes 20–80 s per call and escalates to the operator. In this very
session: `cd <abs> && …` compounds — 57 calls — never waited once; the eight slowest Bash calls were all
heredocs; `Write` to a file never prompted (10/10); `Agent` launches never prompted (8/8).

Three earlier diagnoses were wrong and are corrected in this lane, because each will mislead the next
agent into repeating this session: the sandbox escalation gate (the command's and the rule's measured
table say `/sandbox` fixes 94 stops — it fixes none of them), `excludedCommands` (the opposite of the
fix), and the stale memory note (real, but 76 calls / 67 min, not the cause).

## What "done" looks like — acceptance rows

- **A.** A Bash call containing a heredoc (`<<`) is **refused before the permission gate** by a
  `PreToolUse` hook, with a reason that names the reshape (Write the script to a file; run
  `python3 <path>`; for a commit message, `git commit -F <file>`). The operator is never asked.
  Pinned by a test seen RED before the hook existed.
- **B.** A leading run of `NAME=<literal>` assignments is stripped and the remainder **auto-allowed**
  when, on its own, it already matches one of the operator's allow rules — the same "nothing new"
  proof `allow-readonly-chain.py` uses (SCC-287). A `NAME=$(…)`, a backtick, or a remainder carrying
  any separator is NOT stripped and falls through silently to the normal flow. Pinned by tests seen red.
- **C.** The hook never emits `permissionDecision: "ask"` on any path (an `ask` is an auto-DENY in auto
  mode and would strand a headless run). Pinned; a mutant introducing `ask` is killed.
- **D.** `approval_stops.py` carries heredoc, leading-`VAR=` and `$( )` in its harness-ban table with
  the remedy, so `/smh-llm-approvals` Step 1 names the AGENT's shape as the cause and never proposes an
  allow row for them; the "ALLOWED but stopped by the escalation gate" label is corrected to say what it
  measures — a covered command that still waited — and no longer points at `/sandbox`.
- **E.** `command-shape.md` gains rule 5 (heredoc → file) and rule 6 (leading `VAR=`), and its
  "already handled" bullet stops claiming `VAR=$(…)` is fine on Claude. The measured tables in
  `smh-llm-approvals.md` and `approval-cost-is-a-threat.md` are corrected. `sandbox_widen.py`'s
  docstring stops asserting the sandbox diagnosis (its `allowWrite` widening for tool caches stays —
  harmless, and the E2E tier's `npm ci` needs it). The hook is listed in `.agents/hooks/INDEX.md`.
- **F.** The SOP's hook table and the changelog carry the new hook in the same commit (`sop-currency`).
- **G.** Proof, in order: `run_all.py` green including the new test file; the 20-session classifier
  re-run shows the 94 heredoc/`VAR=` calls under "shape the harness bans" with the remedy; and a LIVE
  heredoc sent from this session comes back as an instant deny to the agent, with no prompt to the
  operator. If hooks only load at session start, G's live half is proven at the next session start
  and the walkthrough says so.
- **H.** (operator's direction, 2026-09-05: *"for both gemini and zoo I just call a script to update
  it in the terminal, lets just do that"*) Claude gets the third apply script the other two platforms
  already have — `claude_permissions_apply.py --status | --apply`. `--apply` merges the TRACKED
  `.claude/settings.json` allow rows into `~/.claude/settings.json` (user scope, so the rules hold in
  every repo on the machine — additive, never a prune unless `--prune`, per SCC-414), and widens
  `sandbox.filesystem.allowWrite` with the tool-cache paths (absorbing `sandbox_widen.py`, which is
  deleted). It is the ONE file an agent is barred from writing, so the script is the operator's, run
  once per machine like `antigravity_permissions_apply.py`. Backs up first; idempotent; prints what
  changed. It never touches `excludedCommands` (operator ruling: that is the opposite of the fix).

## The design — `.agents/hooks/shape-block.py`

`PreToolUse`, `Bash` only, wired in `.claude/settings.json` beside `allow-readonly-chain.py`.
Decision order, first match wins:

1. **Heredoc anywhere → DENY.** Reason cites `command-shape.md` rule 5 and the reshape. This is a
   block, not a nag, on purpose: `shape-guard.py` speaks *after* the command, and here the operator's
   click IS the damage — the same reason `git add -A` is a `PreToolUse` concern (rule's §Nag, limit 2).
2. **Leading literal assignments → strip, then prove.** Regex-strip `^(\s*[A-Za-z_]\w*=<literal>\s*;?\s*)+`
   where `<literal>` has no `$`, backtick, `(`, `)` or separator. If the remainder is ONE atom — no
   `;`, `&&`, `||`, `|`, newline, `$(`, backtick — and `already_allowed(remainder)` (imported from
   `allow-readonly-chain.py` via `importlib`, never copied) → ALLOW with a reason naming the rule that
   matched. Anything else → silent.
3. **Silent** (exit 0, no output) → the normal permission flow, unchanged.

Fails open on any exception, like every sibling hook. Never `ask`.

**The one tradeoff worth the operator's attention:** deny-not-nag means an agent that insists on a
heredoc is bounced every time until it reshapes — one extra model turn per bounce, zero clicks. The
alternative (allow heredocs) is a blank cheque for arbitrary code and is refused.

## Declared Change Set

Rows A–G are the acceptance rows above.

- NEW `.agents/hooks/shape-block.py` → A, B, C
- NEW `.agents/scripts/tests/test_shape_block.py` → A, B, C, G
- EDIT `.claude/settings.json` → A (the `PreToolUse` wiring; `permission_render.py` round-trips the whole file, so the entry survives every render)
- EDIT `.agents/scripts/approval_stops.py` → D
- EDIT `.agents/rules/command-shape.md` → E
- EDIT `.agents/commands/smh-llm-approvals.md` → E
- EDIT `.agents/rules/approval-cost-is-a-threat.md` → E
- NEW `.agents/scripts/claude_permissions_apply.py` → H
- NEW `.agents/scripts/tests/test_claude_permissions_apply.py` → H
- EDIT `.agents/scripts/claude_permissions_status.py` → H (its docstring said an apply "must never exist"; it now points at the user-scope one)
- DELETE `.agents/scripts/sandbox_widen.py` → H (absorbed; created in this lane an hour earlier, never merged)
- EDIT `.agents/hooks/INDEX.md` → E
- EDIT `.agents/scripts/INDEX.md` → H (the script inventory)
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` → F
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` → F
- EDIT `.agents/scripts/tests/test_allow_readonly_chain.py` → A — only if its WIRING block pins the exact `PreToolUse` hook set; declared now so it is not drift if it does

Not project files (no declaration): the two memory notes written today are corrected to the measured
numbers. The SCC-415 ticket summary is corrected from "sandbox harvest" to the shape cause.

## Out of scope, and why

- The 3 real sandbox violations (Firestore network from a probe) — `sandbox_widen.py` is the
  operator-run half; not the cause of the prompts.
- The `$( )` bucket (8 calls, 15 min) — classified and named by D, not blocked; the house doors are full
  of `VAR=$(cd X && git …)` reads and blocking them is a separate, larger reshape.
- Zoo and Antigravity — no hook surface; `shape_scan.py` measures them.
- The AVCH-80 lane (ruff fixes uncommitted, pyrefly 22 errors) — a different repo and ticket.
