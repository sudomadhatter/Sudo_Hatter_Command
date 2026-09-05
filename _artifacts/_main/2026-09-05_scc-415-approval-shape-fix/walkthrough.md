# SCC-415 — Walkthrough: the approval prompts have a measured cause, and it is command shape

**Ticket:** SCC-415 (subtask of SCC-411, the open rolling ticket) · **Branch:**
`chore/SCC-415-approval-sandbox-harvest` · **Commits:** `a0263a30` (allow-list harvest),
`08243868` (the hook, the apply script, the corrections) · **Plan:**
[implementation_plan.md](implementation_plan.md)

**The operator's words, verbatim, the same day:** *"why im approving 100 commands ? what is this"* ·
*"those are exclude commands. that does nothing to help me why are you excluding anything the whole
point is to make this so I dont have to approve them"* · *"stop and figure out why, last change or
im retiring all of the claude side"* · *"for both gemini and zoo I just call a script to update it in
the terminal, lets just do that"* · *"give me the script I can call to run once the
/smh-llm-approvals writes it"*.

## What was broken

Across the 20 newest Claude sessions (10,527 Bash calls) the operator spent **15 hours** waiting on
Bash calls that were sandboxed, matched an allow rule, hit no sandbox violation and were refused by
nothing. Classified by the SHAPE of the command:

| Shape | Calls | Operator time |
|---|---|---|
| heredoc — `python3 - <<'PY' … PY`, `git commit -F - <<'MSG'` | 54 | **7h 17m** |
| leading `VAR=` assignment — `S=/tmp/…; python3 …` | 40 | **5h 44m** |
| `$( )` substitution / shell control flow | 11 | 26m |
| genuinely long-running search or suite (runtime, not a stop) | 111 | 1h 31m |

`Bash(python3:*)` matches `python3` and then meets a body it cannot judge; no rule can begin with
`S=`. Either way the call drops to the auto-mode classifier (20–80 s) and then to the operator. In
the session that measured this: `cd <abs> && …` compounds never waited (57 of 57), `Write` never
prompted (10 of 10), `Agent` launches never prompted (8 of 8), and the eight slowest Bash calls were
all heredocs.

**Three diagnoses made earlier the same day were wrong, and each cost a session:**

1. *"It is the sandbox escalation gate — `/sandbox` fixes 94 stops."* It fixes none of them. The
   door's measured table, its rule, and a memory note all said this; all three are corrected.
2. *"Add the commands to `sandbox.excludedCommands`."* The opposite of the fix: excluding a command
   removes it from the sandbox, so it loses the `autoAllowBashIfSandboxed` auto-approval and needs a
   permission prompt instead. The operator rejected the edit; the apply script now asserts that key
   byte-identical across a run.
3. *"The stale memory note telling agents to run git with the sandbox off is the root cause."* Real —
   76 calls, 67 minutes — but a twentieth of the cost.

## What shipped

- **[`shape-block.py`](../../../.agents/hooks/shape-block.py)** — `PreToolUse`, Bash. A heredoc
  anywhere outside quotes is **denied before the permission gate**, with the reshape returned to the
  agent (write the payload with the Write tool; `python3 <file>` / `git commit -F <file>`). A leading
  run of `NAME=<literal>` is stripped and the remainder **allowed only when it already matches one
  of the operator's own allow rules on its own** — the same nothing-new proof as
  `allow-readonly-chain.py`, borrowed by import. Never an ask; fails open. Wired second in the single
  `PreToolUse` Bash group (`allow-scratchpad.py` pins itself first).
- **[`claude_permissions_apply.py`](../../../.agents/scripts/claude_permissions_apply.py)** — the
  Claude apply the other two platforms already had. `--apply` merges the tracked allow rows into
  `~/.claude/settings.json` (user scope, so a lobby row also holds in a project worktree) and widens
  `sandbox.filesystem.allowWrite` with the tool-cache paths. Additive, `--prune` opts in, backs up
  once, idempotent, `allow` rows only. **It is the one file no agent may write** — the classifier
  refuses it unconditionally (three identical refusals measured) — so the operator runs it, and
  `/smh-llm-approvals` now ends every run by printing that line. `sandbox_widen.py` is absorbed.
- **`approval_stops.py`** files heredoc, `VAR=$( )` and `VAR=` heads under "no row can fix it" with
  the remedy; the "sandbox escalation" heading is corrected.
- **`command-shape.md`** rules 5 and 6; the "`VAR=$( )` is fine" bullet corrected by the data; §Nag
  records why 5–6 are a block and not a nag.
- The door, its rule, `hooks/INDEX.md`, `scripts/INDEX.md`, the status script's docstring, the
  opencode mirror, the SOP hook tables and changelog — all carry the measured diagnosis.

## Proof

**Fence:** `run_all.py` **79/79** at `08243868` (the two new test files included: 20 + 9 cases).

**Live, from the session that built it** (the hook was hot the moment the tracked file was saved):

| Sent | Result |
|---|---|
| `cat <<'EOF' … EOF` | **refused by the hook**, reason returned to the agent, operator never asked — twice, once with the hook first in the chain and once in its final (second) position |
| `S=/tmp/claude-1001; ls -d "$S"` | ran straight through, no wait |
| `W=/home/…; ls "$W/.agents/hooks/shape-block.py"` | ran straight through, no wait |

**Re-classification of the same 20 sessions with the corrected script:**

| | before | after |
|---|---|---|
| not covered by the allow list | 13 | **0** |
| a shape the harness bans — no row can fix it | 22 | **194** (54 `<<'PY'`, 7 `<<'MSG'`, 34 `VAR=`, …) |

**Mutation sweep** (`mutation_sweep.py`, table declared before the run, tree clean at start,
restore verified against the pinned sha, closing unfiltered run 20/20):

| Mutant | Kind | Killed by |
|---|---|---|
| M1 the heredoc branch is disabled | existence | `test_heredoc_python_is_denied_and_names_the_reshape` |
| M2 the nothing-new proof is skipped | existence | `test_assignment_before_an_unallowed_command_falls_through` |
| M3 the decision becomes an ask | existence | `test_never_asks` |
| M4 the one-atom guard loses `$( )` | **width** | `test_assignment_before_a_remainder_with_substitution_falls_through` |
| M5 heredoc detection stops stripping quotes | **width** | `test_quoted_double_angle_is_not_a_heredoc` |
| M6 the literal class admits `$` | **width** | `test_assignment_with_dollar_var_falls_through` |

**6/6 killed by their declared case.**

## One more measurement, made while pushing

`git push -u` failed to write the upstream line — `could not lock config file .git/config: File
exists` — while the push itself succeeded. The lobby's `.git/config.lock` is a character device
(`crw-rw-rw- nobody nogroup 1, 3`): a sandbox mount artifact. So the earlier scratch-repo test was
too narrow: git works sandboxed in the lobby **except** writes to its `.git/config`. Push without
`-u`. The memory note now says exactly that.

## Suite Ledger

| scope | command | result | why this run |
|---|---|---|---|
| hook tests | `python3 .agents/scripts/tests/test_shape_block.py` | 17/19 → 19/19 → 20/20 | red on wiring + rule text before they existed; green after; width case added before the sweep |
| apply tests | `python3 .agents/scripts/tests/test_claude_permissions_apply.py` | 8/9 → 9/9 | red on wiring before it existed |
| fence | `python3 .agents/scripts/tests/run_all.py` | 75/79 → 79/79 | four consequences of the wiring / index / mirror / a test that pinned the old sentence, each fixed |
| sweep | `python3 .agents/scripts/mutation_sweep.py --table shape_block_sweep.json` | 6/6 killed | the width proof |

## Your Actions

- [x] The merge itself — lands via this branch's PR
- [ ] **Run the apply once per machine** — it is the only file no agent is permitted to write:
  `python3 ~/Sudo_Hatter_Command/.agents/scripts/claude_permissions_apply.py --apply`
  (`--status` first shows the 130 rows and 4 sandbox paths it adds — 206 tracked against 82 in user
  scope; the IDE stays open, then reload the window so the session re-reads the file). This machine
  now; the PC (`python`) the first time Claude opens there.

## Out of scope, named

The AVCH-80 lane (a different repo and ticket): its ruff fixes are uncommitted in its worktree and
pyrefly's 22 pre-existing errors still block that PR. The `$( )` shapes the house doors are full of
are classified and named, not blocked. Zoo and Antigravity have no hook surface; `shape_scan.py`
measures them.
