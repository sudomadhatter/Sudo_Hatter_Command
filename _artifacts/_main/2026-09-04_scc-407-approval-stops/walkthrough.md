---
IsArtifact: true
ArtifactMetadata:
  title: SCC-407 — the approvals door was measuring the wrong event
  type: walkthrough
  date: 2026-09-04
---

# SCC-407 — the approvals door was measuring the wrong event

**Lane:** `chore/SCC-407-approval-stops` · main checkout
**Ticket:** [SCC-407](https://sudo-command.atlassian.net/browse/SCC-407) (Bug)
**Base:** `origin/main` @ `56069a92`

---

## What this means for you, Mr. Hatter

**`/smh-llm-approvals` was reading the one event that costs you nothing, and blind to every event
that costs you money.**

Step 1 harvested Claude transcripts for a `tool_result` carrying `is_error` and the text *"doesn't
want to proceed with this tool use"*. That is a command **you refused** — you said no, the work
stopped, nothing was spent. But the door exists to find the *trivial* command that stopped and
waited, which you then **approved**. And a granted approval writes **nothing at all** to the
transcript, so there was no record for the old reading to find.

That is why it told you "nothing to harvest" earlier tonight. It was not a threshold that needed
tuning. It was pointed at the opposite event.

| | old Step 1 | measured reality, same 20 sessions |
|---|---:|---:|
| commands it found | **1** | **56** stops |
| your time | not measured | **1h 02m** waiting |
| classifier refusals | never looked | **7** |

**And the wait is the cheaper half of the bill.** Every stop breaks the prompt cache. The turn
resumes cold and the whole context is charged again — so an interruption bills twice: once in your
attention, once on the invoice. That is why the new report ranks by **time waited**, not by count.
The expensive stop is the one you were away from, not the one that happens often.

The top row it finds is `git branch` — **19 stops, 25m49s**. That is already fixed by
[PR #165](https://github.com/sudomadhatter/Sudo_Hatter_Command/pull/165), which is a useful
cross-check: the new instrument independently ranked first the row the other lane picked.

## What shipped

**[`.agents/scripts/approval_stops.py`](../../../.agents/scripts/approval_stops.py)** — read-only,
exits 0, three signals because none is sufficient alone:

| signal | proves | insufficient alone because |
|---|---|---|
| **latency** — gap between a Bash `tool_use` and its `tool_result` | a human was asked, observed | `gh pr checks --watch` blocks ten minutes with nobody asked |
| **coverage** — replay against the rendered `.claude/settings.json` | predicts the next stop | says nothing about cost already paid |
| **classifier** — the `denied by the Claude Code auto mode classifier` error | a refusal class the old step never looked for | fired 7× in this window |

Latency **and** uncovered together is the high-confidence set: it waited, and there is a reason it
would.

**The report only carries rows one allow rule would fix.** Shell scaffolding (`for i`, `set -e`,
`done`), Python heredoc bodies (`import json`), self-explaining waits (`timeout 900`, `--watch`)
and wrapped continuation fragments (`-rl '^riders:'`) are dropped **by name**. A list whose rows
cannot be acted on is longer without being more useful.

**[`.agents/commands/smh-llm-approvals.md`](../../../.agents/commands/smh-llm-approvals.md)** Step 1
now calls the script, and carries a ⛔ block naming the old instruction so it cannot drift back.
The `.opencode` mirror was re-synced to match.

## Four bugs of mine the tests caught before this shipped

Each was found by a control case, not by reading the code:

1. **`\d` instead of `\d+`.** `\b(timeout\s+\d|…)\b` matched `timeout 9` inside `timeout 900`, then
   failed the word boundary against the second `0`. The filter that existed to drop those rows left
   them at the **top** of the ranking, reading as real findings. Case `E` pins three digits.
2. **`\b--watch` can never match.** `\b` needs a word character on one side; the space and the `-`
   are both non-word. Every `--watch` run was credited as an operator stop. Same case.
3. **First-line-only lost real commands.** My second fix for heredoc noise kept only line 1 — so
   `set -e` on line 1 and the real command on line 2 reported the scaffolding and dropped the
   command. Case `F2` is the control that caught it; the fix discriminates by `_PREAMBLE` instead
   of by line number.
4. **Fragments ranked as commands.** `-rl '^riders:'`, the second half of a wrapped `grep`, ranked
   **first at 18m27s**. Case `G`.

## The operator's own eight stops — the ground truth that corrected this

Mr. Hatter supplied his eight real stops with the reason each one was not an allow-list problem.
The first cut of this script would have found **one** of them, and would have actively **hidden**
#3. His table, verbatim:

| # | what stopped | why the allow list didn't help |
|---|---|---|
| 1 | `Skill(code-review-engine)` | no skill-grant kind exists in `families.json` |
| 2 | venv python probe, absolute path, sandbox off | escalation gate, not the allow list |
| 3 | `git worktree remove --force … && git branch -d …`, sandbox off | `Bash(git worktree remove *)` was **already allowed**; escalation gate fired anyway |
| 4–8 | five identical `sleep 60; cat …; gh pr view 154 …` | hard harness ban; remedy is Monitor, not a permission row |

**Three whole classes, none of which one allow row can fix.** The report now separates them,
because the remedy differs and mixing them is what makes a list unactionable:

| class | his stops | count in the live window | remedy |
|---|---|---:|---|
| not covered by the allow list | — | 36 · 1h03m | one allow row |
| **allowed, stopped by the escalation gate** | 2, 3 | 78 · 1h07m | the sandbox boundary, not a rule |
| **no grant kind exists** (`Skill`, `Agent`) | 1 | 70 (count only) | `families.json` cannot express it yet |
| **harness ban** | 4–8 | 21 | a different tool (Monitor), never a rule |

**#3 is the one that matters most, because it was a false negative I had shipped.** The command was
already on the allow list, so `covered()` returned true and the scan stayed silent — while he sat
there. The escalation gate is a **second, independent gate**, and coverage says nothing about it.

## Three more bugs his list exposed

5. **`sleep` was filtered before it was classified.** `sleep 60; …` matched the self-explaining
   filter first, so his five identical retries vanished into that bin instead of reporting with
   their Monitor remedy. Ban now outranks self-explaining (case `E`/`M`).
6. **Escalation stops went through `report_head` and were discarded.** That helper returns None
   when every segment is covered — which is exactly the shape of an escalation stop. It now has
   its own bucket (case `L`).
7. **`Agent(general-purpose)` was charging him 11h37m.** 63 subagent runs, counted as though he
   had been waiting on every one. That fabricated figure sat at the top of a report whose only
   value is being believable about cost. Non-Bash tools are now **counted, never timed** (case `N`).

## Evidence

```
python3 .agents/scripts/tests/test_approval_stops.py   -> 14/14
python3 .agents/scripts/tests/run_all.py              -> 73/74
```

`test_approval_stops.py` builds **synthetic** transcripts, so it binds on CI too — a test reading
the live `~/.claude/projects/` would pass vacuously forever on a machine where that directory is
empty. Case `A0` is the control that proves the harness can see a stop at all; without it every
other case could pass by finding nothing.

The one red is `CS-22 B` — two *other* lanes' stale worktrees in the file walk. Local-only, red on
`origin/main` with none of this diff present, invisible to CI.

## Your Actions

- [x] The merge itself — lands via this branch's PR
- [ ] Run `python3 .agents/scripts/approval_stops.py` whenever you want the current list; it is the
      Step 1 of `/smh-llm-approvals` now, so invoking the door does it for you

## What this does NOT do

It proposes no rules and computes no prefixes — SCC-354 stands. It reports what stopped you and
what it cost; you pick.
