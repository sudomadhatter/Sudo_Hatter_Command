# SCC-430 — Autopilot v3, the Claude half

**Ticket:** SCC-430 (Subtask of SCC-429)
**Lane:** `chore/SCC-430-autopilot-claude`, cut from `origin/main` at `d70347ba`
**Plan:** [implementation_plan.md](implementation_plan.md) — approved 2026-09-07, recorded at `dbb9c4b0`, stamped `c88f4f60`
**Spike:** [spike.md](spike.md)
**Date:** 2026-09-07

## What this closes, in one paragraph

The autopilot's lead session can now launch one headless `claude -p` child per workflow step, and
the child runs the **existing** door by name rather than a copy of it. Two acceptance rows are
closed: **A**, the S0 spike, which measured six tables against the real CLI and falsified three of
the design's assumptions before a line of the runner was written; and **B**, `autopilot_run.py`
and its negative control, which holds the five rules an LLM cannot keep about itself — a missing
door costs nothing, a reply without a `status` is a failure, a reviewer cannot inherit the
author's session, the door travels as a name and never as text, and the only budget ceiling that
can actually be enforced is the runner's own.

## Task Checklist

- [x] **Row A — the S0 spike.** Six tables measured on CLI 2.1.263, ~$2.06 spent, posted to SCC-430.
- [x] **Row A — the CLI upgrade** (2.1.258 → 2.1.263) on the operator's word; `--append-system-prompt-file` re-probed and found present, `--max-turns` confirmed absent and dropped.
- [x] **Row B — `autopilot_run.py`**, stdlib only, verb `run`, plus the seat renderer's pointer half.
- [x] **Row B — `test_autopilot_run.py`**, 35 cases across 8 blocks, every one seen RED first.
- [x] **Row B — the sandbox question closed** (spike Table 6): `CLAUDE_CONFIG_DIR` relocates the transcript store into a sandbox-writable path, so a sandboxed fork works and costs 92% less than its parent. No settings change, no escalation, no unsandboxed fallback.
- [x] **Row C — the seat renderer.** `render_seat()` builds the `--agents` JSON in memory from the master's frontmatter; the six masters carry `claude-model`, `claude-effort` and `claude-tools`; no `.claude/agents/` file is written.
- [ ] Row D — `jira_feed.py step`.
- [ ] Row E — the lead's door (**needs ruling 1**, the charter rows).
- [ ] Row F — one real AGY story (**needs a story choice**).
- [ ] Row G — the five old doors deleted (**needs ruling 3**).

## Evidence

### The RED run — every case failed against a naive stub first

The plan requires each row-B test to be seen red against "a stub that launches anyway". A naive
`autopilot_run.py` was written first, doing the plausible thing at every decision: launch the
child and let it sort itself out, trust the reply, resume whatever session is handy, paste the law
in so the child cannot miss it, and pass `--bare --permission-mode bypassPermissions`.

```
-- 11/35 passed --
FAILED: D1 a missing door exits 2, D2 ...and claude was NEVER launched, D4 anti-vacuity - a door
that EXISTS does launch claude, S1 a result with no status exits non-zero, S2 ...and the runner
reports it as failed, S3 stdout that is not JSON is failed, not a traceback, R1 a review on a
session id in the ledger exits 2, R2 ...before launching anything, R3 a review that forks another
session exits 2, R4 ...before launching anything, R5 a review wearing a seat exits 2, R6
anti-vacuity - an unseen, unforked, seatless review DOES launch, N1 no door or rule sentence
appears in the runner, N2 the runner never reads a door's body, F1 --bare is never passed, F2
bypassPermissions is never passed, F3 --permission-mode is auto, F8 stdin is closed at the launch
site, B2 ...and so is the seat JSON, across two renders, K2 ...and STILL carries --agents, or the
seat is silently dropped, C1 a run already over its ceiling exits 2, C2 ...before launching
anything (the CLI cap is soft - spike finding 2), C3 ...and the refusal prints what has been
spent, C4 anti-vacuity - under the ceiling it launches
```

Twenty-four failures, one per defect the suite exists to catch. `N1` fired on a single sentence of
`constitution.md` pasted into the stub, which is exactly the drift the rule forbids.

### The GREEN run — the real runner

```
-- 35/35 passed --
```

### Test Suite Ledger

| Suite | Scope | Result |
|---|---|---|
| `tests/test_autopilot_run.py` | the new file, alone | **35/35 passed** |
| `tests/test_autopilot_run.py` | after row C's seat cases | **87/87 passed** |
| `tests/run_all.py` | the whole workflow-script suite | **82/82 files passed** |
| `mutation_sweep.py` | 9 declared mutants, code-derived | **9/9 killed**, restore verified |
| `sync-agents.ps1 -Status` | is any launcher stale? | clean - every invocable file matches |
| `check_maps.py` | drift | all maps & INDEXes agree with disk |

### Anti-vacuity, deliberately

Four cases exist only to stop their neighbours passing for the wrong reason: `D4` (a door that
exists really does launch), `R6` (a clean review really does run), `C4` (under the ceiling it
launches) and `N0` (the drift corpus really holds 12,413 fragments to check against). Without them,
a runner that launched nothing at all would score green on the DOOR, REVIEW and CAP blocks.

### The mutation sweep — nine mutants, all code-derived

A test that has never failed is a claim. The row-B cases were seen red against the naive stub; the
row-C cases were not, so they were swept. Every mutant is drawn from a decision in
`autopilot_run.py`, never from reading the cases and asking what would break them.

| # | mutant | must kill | outcome |
|---|---|---|---|
| M1 | the seat's tools are never emitted | `T4 gnat: tools are the master's claude-tools` | KILLED |
| M2 | the prompt stops naming the master file | `T5 gnat: the prompt names the master file` | KILLED |
| M3 | every seat renders under one constant name | `T1 gnat: rendered under its own name` | KILLED |
| M4 | the seat's model is not carried | `T3 gnat: model is the master's claude-model` | KILLED |
| M5 | a missing door no longer stops the launch | `D2 ...and claude was NEVER launched` | KILLED |
| M6 | the reviewer may fork the author's session | `R3 a review that forks another session exits 2` | KILLED |
| M7 | the run-level ceiling never trips | `C2 ...before launching anything` | KILLED |
| M8 | a reply with no status defaults to done | `S1 a result with no status exits non-zero` | KILLED |
| M9 | a fork stops re-passing the seat | `K2 ...and STILL carries --agents` | KILLED |

`-- restore verified: bytes match, nothing was committed -- ` and the closing unfiltered run of the
whole file exited 0.

**The first pass was 8 killed and one SWEEP ERROR, and the error was the finding.** M3 makes
`render_seat` return `{"seat": ...}`; the parity cases indexed `rendered[seat_name]`, raised
`KeyError`, and the test **file** died mid-run — so the harness printed no `FAILED:` line, the kill
could not be attributed, and every case after that point went unscored. Reading it as a survivor
would have bought a test for a hole that did not exist; reading it as a kill would have certified a
file that silently stops scoring. Fixed at `c1610941` (`.get`, not `[]`), then re-swept 9/9.

## Decisions taken in this step

**The runner seeds its own Claude config directory, and that is what makes forking possible.**
`~/.claude/projects` is deny-listed by the sandbox, so a sandboxed child answers perfectly and
persists no transcript — and without a transcript there is nothing to fork, which costs the whole
layered saving. `CLAUDE_CONFIG_DIR` moves the store to `~/.local/share/autopilot-claude-home`,
which the sandbox already permits. Two seeds are required there: the OAuth credential, **symlinked
and never copied**, and the workspace trust flag. The trust flag turned out to be load-bearing for
cost rather than for warnings — untrusted, every fork read **zero** cached tokens while still
succeeding, so the bill was the only symptom. What it grants is the repository's own tracked
`.claude/settings.json` allow rows; it widens nothing beyond them, and it is written into the
autopilot's own directory, never into `~/.claude/settings.json` or the repo's.

**The reviewing and default models are pinned in the runner, not passed by the caller.** An
unpinned child inherits `claude-opus-5[1m]` and costs six to twenty times more for the least
valuable calls in a run (spike finding 4). Pinning them in the file means "the reviewer ran on the
author's model" is not something a caller can cause by forgetting a flag.

**`--run-cap-usd` exists because `--max-budget-usd` cannot be trusted.** The CLI's cap stops the
next turn, not the current one: probes capped at $0.05 spent $0.496 and $0.296. The runner sums its
ledger before launching and refuses over the ceiling, which is the only ceiling that holds.

## Deferred, and where it goes

**`claude-skills` is read but written on no master, deliberately.** Three keys is the whole
budget — `sync-agents.ps1` reads the header with `Get-Content -TotalCount 12` and a fourth and fifth
key push the closing `---` out of the window, at which point the seat vanishes from `.roomodes` with
no error anywhere. Skills lost the tie-break because the spike measured `skills:` having no effect
on a child's prefix (11,466 against 11,467 tokens) while accepting a made-up skill name in silence:
a populated list buys nothing measurable and could, if the key ever does restrict, cut a seat off
from the very door it was launched to run. The renderer still reads the key, so a master that grows
one needs no code change.

**The per-seat tool lists are the one thing row F will confirm or amend.** They mirror the Zoo
seat's `mode-groups` — read maps to Read/Grep/Glob plus the web pair, edit to Edit/Write/
NotebookEdit, command to Bash/TodoWrite — and `Task` is on no seat, because a headless child that
can spawn its own subagents is an unbounded bill with no ledger row. If a real door needs a tool no
seat carries, it will show up as a child that cannot finish, and the fix is a key on the master.

Whether a leading `/door-name` in a `-p` prompt expands to the door's launcher skill is proved by
row F's real story, where the plan places it.
