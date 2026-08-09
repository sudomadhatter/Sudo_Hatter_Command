# SCC-68 — Walkthrough: the memory gate now triggers its own remedy

**Date:** 2026-08-09 · **Repo:** Sudo_Hatter_Command (lobby) · **Branch:**
`chore/SCC-68-memory-audit-trigger` · **Lane:** LOCAL

---

## What changed, in one line

Memory upkeep moved from a workflow nobody had a reason to open (`/update-maps-indexes` Step 3.9)
to the gate that runs on **every close-out on every machine** — and the audit it triggers now
ground-truths each memory against the live repo instead of just counting bytes.

## The finding that drove it

Step 3.9 was written, correct, and had **never run**. The store sat at **20,378 / 20,480 bytes —
99.5% of cap, 102 bytes of headroom**, which is less than one index line: the next memory anyone
wrote on either machine would have turned `run_all` red.

The mechanism was sound and the *placement* was fatal. Nobody reaches for a **map** command because
memory feels heavy. Upkeep hung off an unrelated command's coattails, so the remedy was parked
somewhere no one had a reason to go — and the only thing that ever surfaced the problem was the
operator noticing a number in conversation.

**The generalizable lesson:** upkeep has to trigger from something that runs on its own schedule.
Attaching it to a command a human must choose to invoke is the same as not having it.

## The seam: a script cannot ask

The ask is deliberately two parts, and the split is worth seeing rather than believing in:

| Half | Where | What it does |
|---|---|---|
| **The imperative** | `tests/test_memory_store.py` | prints a loud `MEMORY AUDIT DUE` block — bytes, percentage, headroom, and a derived candidate worklist |
| **The ask** | root `AGENTS.md` §7 | binds *every platform*: see that block → **STOP and ask the operator** whether to run `/memory-audit` |

A test script runs headless, inside hooks, inside `run_all` — it has stdout and an exit code, and
nothing else. Pretending otherwise would have produced a trigger that fires into a void. This is the
same shape that fixed the close-out in SCC-64: **the machine states the fact, and the obligation is
literal so a weak model cannot infer its way around it.**

The block prints **after** the test tally, on purpose — it is the last thing on screen and survives
a `| tail` (see [[piping-a-gate-hides-its-exit-code]] for why that mattered).

## Decisions

| Decision | Ruling | Why |
|---|---|---|
| **Trigger at 90%**, run still PASSES | `TRIGGER_PCT = 0.90` | The trigger exists so the hard cap never trips. Firing only at 100% means the first signal is already a red blocking unrelated close-outs — and a gate that reddens unrelated work teaches "some reds are fine," the exact rot SCC-64 named. |
| **Over-cap stays a hard fail** | unchanged | It is what forced this conversation. |
| **No auto-compaction** | unchanged | A model summarizing away a hard-won pitfall is silent, permanent loss of exactly the recall the store exists for. |
| **Never raise the cap** | written into both the command and §7 | 20 KB ≈ 5,000 tokens charged to every session on every platform *before a single useful token*. If it will not fit, the index is carrying content that belongs in the memory files. |
| **`/memory-audit`, not `/sudo-memory-audit`** | non-`sudo` family | `sudo-target-resolution.md` binds `sudo-*` to "exactly ONE target — never the lobby." The store is in the lobby. The naming is the permission. |

## Signals, not verdicts

The gate hands the audit a worklist so it opens on evidence rather than a blank page — on the real
store: **11** `CLOSED`/`RETIRED`/`FIXED` index rows · **8** dangling `[[link]]` targets · **20**
memory bodies over 4 KB.

Every one of those can be legitimate, and the code says so in its own docstring: a `CLOSED` row
whose lesson still bites stays, and a dangling `[[link]]` is the *sanctioned* way to mark a memory
worth writing later. Shipping these as verdicts would have built a machine that deletes true things
on a heuristic.

## What makes the audit worth running

Byte-trimming is the least of it. **Every memory makes a claim about the system, and claims outlive
their subjects in silence.** Step 3 of `/memory-audit` verifies each one: does the rule/script/flag
it names still exist on disk? Is the thing it calls `CLOSED` actually gone? Is the ticket state it
asserts still the ticket's state? Do its `[[links]]` resolve?

A candidate that fails its check is a retirement. A candidate that passes is kept **no matter how
old — age is not the criterion, truth is.** The worst artifact in a memory store is not a stale
entry; it is a row marked `RETIRED` whose subject is still live, because whichever the model reads
first wins.

## Verification

| Gate | Result |
|---|---|
| `tests/test_memory_store.py` | **16/16** (was 8/8) — trigger fires at 91%, silent at 89%, and 91% is provably *not* a failure |
| `tests/run_all.py` | **11/11 files, exit 0** — with the `MEMORY AUDIT DUE` block visible in the suite output |
| `tests/test_command_surfaces.py` | **13/13** — all four doors generated for `/memory-audit` |
| `workflow_lint.py --toolkit-only` | **0 errors**, 2 known pre-existing warnings (rule-pointer on `sudo-merge-epic-workingtrees.md`, `_AP` twin drift on `sudo-self-audit.md`) |
| `sync-agents.ps1 -WhatIf` | **zero deletes proposed** before the real run — the SCC-66 near-miss habit, kept |

Doors on disk: `.agents/skills/memory-audit/` (Codex) · `.claude/skills/memory-audit/` (Claude) ·
`.opencode/commands/memory-audit.md` · `.agents/workflows/memory-audit.md` (Antigravity).

## Follow-ons

- **The audit has not been run yet.** It ships already firing at 99.5%, which is the intended
  dogfood: the first `/memory-audit` should take the index back under the 90% band. Until then the
  block prints on every close-out — correctly.
- Platform caches are per-machine: **`/sync-agents` still owed on the PC**, and Codex snapshots its
  skill catalog at chat start.
- Two `workflow_lint --toolkit-only` warnings remain pre-existing and out of scope.
