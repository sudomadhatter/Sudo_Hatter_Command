---
IsArtifact: true
ArtifactMetadata:
  title: SCC-80 walkthrough - 15 rotted memory pointers corrected, a superseded doc retired, and the gap that hid both
  type: walkthrough
  date: 2026-08-10
---

# SCC-80 — Walkthrough: the upkeep gap nobody could see

**Date:** 2026-08-10 · **Repo:** Sudo_Hatter_Command (lobby) · **Lane:** Task (LOCAL)
**Branch:** `chore/SCC-80-memory-and-doc-followon` · **Commit:** `1477751`

> **⛔ NOT merged.** Pushed, gated and handed back for the operator to invoke
> `/smh-close-task-merge-tree`. One invocation authorises one merge; SCC-74's does not carry.

## The question that produced this

*"Verify how we upkeep these so they don't get stale ever — we did this already, correct?"*

**For the docs, yes.** SCC-74 built three overlapping mechanisms, and they work.
**For memory, no — and this ticket is the proof.**

`test_memory_store.py` validated the **index** (links resolve, no orphans, ≤25 KB) and triggered the
audit on **size alone**. Neither ever read a memory **body**. So the store could sit at **79 % of
cap, pass every check on every machine, and route every reader to folders deleted months ago.** It
was doing exactly that, **fifteen times**, and only a hand audit found it.

## What was corrected

15 pointers across 13 memory bodies — **zero retirements**. Every lesson was still true; only the
paths rotted. `MEMORY.md` was deliberately never touched (it carries no stale path), so another
session's uncommitted index line stayed parked.

- **6** broken *by* the SCC-74 move
- **6** pre-existing (`migrations/install_guides/` relocations, `mermaid-diagram-standards` is a
  **skill** not a rule, `active-project.txt` moved to `.agents/`, an archived plan path)
- **1** dead pointer dropped, lesson kept

## ⭐ Two of my own proposals were wrong

Reading full context reversed them, which is what *"the signals are not verdicts"* means:

- `agy-story-files-canonical-dir` — past-tense narrative about a failure, and an **AGY** path. Keep.
- `agy-has-real-nda-users` — the memory itself says `_my_resources/backups` is *"gitignored — they
  contain PII."* **Absent by design**, like the `DISABLE` kill switch. Keep. I had proposed dropping
  it without reading the parenthetical.

## The gap, closed

New `rotted_pointers()` surfaces body-path rot in the audit worklist. **Advisory, never a failure** —
and that is the design, not a hedge: `Projects/<name>/` is an **empty stub in every git worktree**,
so project paths cannot be ground-truthed there. Measured **10 of 11 hits false** that way. It now
returns nothing rather than a worklist that is mostly wrong — a signal with that hit-rate is one
people learn to skip, which is the failure this whole file exists to prevent.

Verified both directions: fires on a planted dead path; silent on the kill switch, gitignored
caches, retired surfaces, `epic-N` templates and AGY paths; **0 against the corrected store** when
ground-truthed from the main checkout where `Projects/` is populated.

## Docs

`complete-system-overview.md` retired into `file_folder_structure+maintaining.md`. **No doc in the
folder duplicates another textually** (0 pairs share 2+ substantial sentences) — but 7 of its 10
sections had a counterpart in the survivor, same subject different wording, which is precisely why a
prose-overlap test found nothing. It was decaying too: §8 named a script that does not exist, §9 was
a *completed* rollout plan. Its Glossary survives as §10a.

**The manifest contract worked as designed** — INDEX row, `EXPECTED` set and the file all moved
together, 13 → 12 docs, and the suite stayed green.

**Deliberately NOT merged:** `jira_manual` + `jira_integration_guide`. They declare a mutual boundary
(*how you drive it* / *why it is built that way*) and cross-reference each other; merging yields a
73 KB doc forcing GUI work through hook internals.

## Gates

`run_all` **12/12** · memory gate **16/16** · **50 links, 0 dead** · lint **0 errors** (2 warnings,
pre-existing on main).

## ⚠ Handed back — open items

1. **Pre-existing repo-map drift on `main`** (small file-count deltas) — **not this lane's**, and a
   worktree *cannot* fix it: regenerating there writes the worktree's own directory name as the repo
   root. That is the SCC-74 bug (fixed at `05938cf`). It must be regenerated from the main checkout.
   ⛔ Do not "fix" the worktree's `AUTO block is STALE` warning — it is false there by construction.
2. **`tea_testing_guide.md`** — titled *"**AviationChat** Test-Architecture Retrofit"*, 84
   project-specific hits in 926 lines. An AGY field guide the lobby now gates. Whether it belongs
   here is an architecture call needing an **AVCH** ticket.
3. **AGY's `sudo_workflows_testing.md`** still at the old path/name — recorded as open drift in
   `sop-currency.md`; needs an AVCH ticket.
4. **The parked pair** in the main checkout (`MEMORY.md` +1 line and
   `github-408-on-satellite-uplink.md`) is still uncommitted, so that memory does not travel to the
   PC. Not mine to commit under an audit.
