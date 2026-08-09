# Plan — Move memory compaction out of `/update-maps-indexes`, trigger it from the gate

**Date:** 2026-08-09 · **Repo:** Sudo_Hatter_Command (lobby) · **Lane:** Task (LOCAL)
**Ticket:** SCC-<new> — created at execution, never invented here
**Branch:** `chore/SCC-<new>-memory-audit-trigger`

---

## The ask

> "Take that out of `/update-maps-indexes` and instead have the test gate trigger the same
> assessment… so when it triggers it asks me if I want to audit the memory. Then it can do exactly
> that compact where it can assess dead rules or ones and clean up the memory."

Three moves: **relocate** the judgment half out of the maps workflow · **trigger** it from the gate
that already runs everywhere · make the audit **cross-check the project**, not just count bytes.

## Why the current shape failed the test

Step 3.9 is real and correct — and it has never once run at the moment it was needed. It only
fires when someone chooses to run `/update-maps-indexes`, which is a *map* workflow; nobody reaches
for it because memory got heavy. So the store filled to 99.5% of cap with the remedy sitting in a
workflow no one had a reason to invoke. **Upkeep hung off an unrelated command's coattails.** The
gate, by contrast, runs in `run_all` on every close-out on both machines. That is where a trigger
belongs.

## One honest mechanical limit, stated up front

**A test script cannot prompt.** `test_memory_store.py` runs inside `run_all`, inside hooks,
headless, on two machines. It has stdout and an exit code, nothing else. So "it asks me" is
implemented as a two-part contract, and I want you to see the seam rather than believe in a dialog
box that does not exist:

1. **The gate emits the imperative** — a loud, unmissable `⚠ MEMORY AUDIT DUE` block naming the
   command, the numbers, and a pre-built candidate worklist.
2. **Root `AGENTS.md` §7 binds every platform to surface it** — when that block appears, STOP and
   ask the operator whether to run `/memory-audit` now. Baked in as a literal obligation, because
   inferior models follow literal step lists and infer nothing (the whole point of this program).

The agent does the asking. The gate makes ignoring it impossible.

## Design decisions (made, not deferred)

| Decision | Ruling | Why |
|---|---|---|
| **Trigger threshold** | **90 %** (18,432 B) → notice, run still PASSES | The trigger exists so the hard cap *never trips*. Firing only at 100 % means the first signal is already a red run_all blocking unrelated close-outs. |
| **Over-cap behavior** | **Stays a hard fail** | It is what forced this conversation. Softening it teaches "some reds are fine" — the exact rot SCC-64 named. |
| **Auto-compaction** | **Still never** | Unchanged ruling. A cheap model summarizing away a hard-won pitfall is silent permanent loss. Gate detects; you decide. |
| **Command family** | non-`sudo` → **`/memory-audit`** | `sudo-*` binds "exactly ONE target, never the lobby." The store *is* in the lobby. Same family as `/sync-agents`, `/update-maps-indexes`. |
| **Harness-link check** | **moves too** | 3.9's step 3 (per-machine symlink) goes with the rest — one command owns the memory concern end to end. |

## The audit's actual work — why it needs the project, not just the store

Byte-trimming is the least of it. Each memory makes a **claim about the repo**, and a claim outlives
its subject silently. So `/memory-audit` ground-truths every candidate:

- the memory names a rule/script/command/flag → **does it still exist on disk?**
- it says `CLOSED` / `RETIRED` / `FIXED` → **is the subject actually gone?**
- its `[[wikilinks]]` → **do they resolve, or point at memories since deleted?**
- two memories cover one idea → **merge candidate**
- last git touch older than N months + subject unchanged → **stale candidate**

Each becomes one proposed line — *retire* · *merge into `<other>`* · *compress to one-line lesson* —
with **bytes freed** shown, then **STOP for per-item approval**. Nothing is deleted without your word;
git is the undo.

## Changes

**Gate — `.agents/scripts/tests/test_memory_store.py`**
- Add `TRIGGER = 0.90` band: over → print the `⚠ MEMORY AUDIT DUE` block, still exit 0.
- Compute the **candidate worklist mechanically** so the audit starts with evidence, not a blank
  page: `CLOSED`/`RETIRED`/`FIXED` index rows, dead `[[wikilinks]]`, oversized bodies. Printed as
  signals; the script never judges or edits.
- Retarget the over-cap message from `/update-maps-indexes` → `/memory-audit`. Docstring rewritten.
- New fixture controls for the trigger band (fires at 91 %, silent at 89 %) — the detector must be
  provably alive, both ways, as with every other check in this file.

**New — `.agents/commands/memory-audit.md`**
Steps: run the floor → build candidates (gate signals + git last-touch + wikilink graph) →
**ground-truth each against the repo** → propose with bytes freed → **STOP** → apply only approved
items (delete file + index line, or rewrite the line) → verify this machine's harness link →
re-run the gate → report before/after bytes.

**Relocations**
- `.agents/workflows/update-maps-indexes.md`: delete Step 3.9 + the `#### 🧠 Memory store` report
  block; leave a one-line pointer so the knowledge isn't orphaned.
- `.agents/commands/update-maps-indexes.md:25`: drop the reconcile from its description.
- `AGENTS.md` §7: the compaction sentence retargets to the trigger→ask contract.

**Surfaces + law**
- `.agents/commands/INDEX.md` row · `/sync-agents` to generate the doors (launcher skill for
  Claude+Codex, opencode mirror, Antigravity workflow — SCC-66 door model).
- `.agents/scripts/tests/test_command_surfaces.py:139` gains `memory-audit`.
- `_my_resources/_quick_reference/sudo_workflows_testing.md` — SOP currency is an **armed gate**;
  §3 door row + the §7 memory-link row (line 623) both name `/update-maps-indexes` today.
- `_artifacts/_memory/memory-store-is-read-by-every-platform.md` — **updated in place** (it
  currently records Step 3.9 as the mechanism). No new memory file: at 102 B headroom, adding one
  would fail the very gate being changed.

## Verification

`run_all` N/N · `workflow_lint --toolkit-only` · link/anchor check · `sop_currency` exit 0 ·
`task_preflight --expect-key SCC-<new>` clear · **then dogfood**: run `/memory-audit` on the real
store and take the index back under the trigger band. That last step is the proof — the trigger
fires today at 99.5 %, so this ships already firing.

## Risks

- **Concurrent lanes share one store** (recorded pitfall). The audit reads and rewrites `MEMORY.md`
  — a dirty file another session wrote gets **parked, never swept**. The command says so explicitly.
- **Deletion is real.** Mitigated by per-item approval + git, and by the audit never touching a
  memory body without approval.
- The 3 known pre-existing `workflow_lint --toolkit-only` warnings stay out of scope.

## Not in scope

The `/` command-naming rethink (your parked ticket) · raising the 20 KB cap · any change to who may
write memory.
