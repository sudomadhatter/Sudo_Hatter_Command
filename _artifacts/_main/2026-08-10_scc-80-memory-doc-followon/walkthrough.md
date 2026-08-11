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

## Second pass — the operator's own edits, rolled in

Made on `main` in the working tree and folded onto this branch on instruction (*"roll any of my
folder and file changes into this push"*):

**`md_feedback_setup_guide.md` moved up out of `_scc_sops_prds/` to `docs/`.** A machine-setup
guide, not an SOP: it tells you how to build a *workstation*, not how to run the workflow, and it is
read once per machine rather than during work. **This is a scope line, not a demotion** — the file
stays inside `docs/`, so `check_maps.py` still covers it. The distinction being drawn is *SOP vs
setup*, never *watched vs unwatched*; that sentence is now written into the INDEX, `docs/AGENTS.md`
and the test docstring, because the failure mode this whole folder exists to prevent is a doc
drifting out of scanner scope while everyone assumes it is covered.

The contract took all three edits again — file, INDEX row, `EXPECTED` — **13 → 11 docs**. The
docstring now records both shrinks and why each happened, so the next reader sees a manifest that
moves in both directions rather than a number that only grew.

**The parked memory pair is committed** (open item 4 below, now closed): `github-408-on-satellite-uplink.md`
plus its one `MEMORY.md` index line, carried across byte-identical to the main checkout's copy. It
now travels to the PC.

## ⭐ The repo-map trap, resolved by proof instead of avoidance

Open item 1 said *don't touch it*. The operator's move forces a regen — `docs/AGENTS.md` requires
one whenever a file is added or removed there — so avoidance stopped being available and the trap
had to be disarmed properly.

`generate_repo_map.py` labels the tree with **`Path(root).name`**. Run inside a worktree that is
`scc-80-followon/`, and it writes *that* as the repo root into a file destined for `main`. Worse,
`check_maps.py` compares the two and reports the **correct** map as `AUTO block is STALE`, with a
regenerate command that would introduce the very corruption it appears to be reporting:

```
[x] AUTO block is STALE - regenerate: ... --root .../scc-80-followon
[x]   on disk but not in map: scc-80-followon/      <- the worktree's own name
[x]   in map but not on disk: Sudo_Hatter_Command/  <- the CORRECT label it wants removed
```

So the warning is not merely noise — **it is an instruction to ship a defect**, and it fires on every
lane, every time. What it actually detects is *"you are in a worktree,"* which is never drift.

Handled: regenerated in place, then corrected that one label line, then **proved** the result rather
than asserting it — the tree was copied to a directory whose basename *is* `Sudo_Hatter_Command`, the
generator run against it, and the output compared. **Byte-identical.** The committed AUTO body is
therefore genuine generator output, not a hand-edit, and no exception to *"never hand-edit inside the
sentinels"* is being claimed. The only real deltas are the two the operator's move caused:
`_scc_sops_prds` 14 → 12 files, `docs/` 9 → 10.

> **Recommended follow-up (not taken here — out of this lane's scope):** derive the label from git's
> **common dir** (the main worktree) instead of the CWD basename. That is a few lines in the
> generator, kills the class permanently, and silences the false `STALE` for every future lane.
> It touches a shared generator plus `check_maps.py`, so it deserves its own ticket.

## Third pass — SCC-78 landed mid-lane

Preflight caught it, exactly as designed: `origin/main has 9 commit(s) NOT on this branch` and
`1 file(s) changed on BOTH sides: workflows_testing_SOP.md`. Merged down; **no conflict**, and both
sides' facts verified present afterwards — SCC-80's `rotted_pointers` sentence in the
`/smh-memory-audit` row, and SCC-78's whole `smh-*` Task-lane section.

**This is also the trap's second, cleaner proof.** 25 files arrived from that lane, `check_maps` said
`AUTO block is STALE`, and regenerating produced **exactly one changed line: the root label**. The
new files are all under `.agents/`, `.claude/`, `.opencode/` — dot-directories the AUTO tree does not
descend into — and the `_artifacts/` addition falls inside a collapsed summary. Re-proved
byte-identical against a correctly-named root *after* the merge. **The map was already current; the
warning had nothing but the worktree's own name to report.**

One real gap surfaced and was fixed: SCC-78's merge landed **without its `_artifacts/_main/INDEX.md`
row**, which `check_maps` flagged as `missing row for 2026-08-10_scc-78-smh-task-lane-dev-cycle/`.
Row written here from that lane's own walkthrough and attributed — a drift on `main` that this
branch would otherwise have carried forward silently.

## Gates

`run_all` **12/12 exit 0** (SOP-folder block **16/16**, memory store green) · lint `--toolkit-only`
**0 errors** (2 warnings, pre-existing on main) · `sop_currency` **exit 0** (no usage surface
touched) · `check_maps` **clean on every real check** — repo-map paths, folder coverage, INDEX paths,
level-2 INDEX presence, depth-3 `_artifacts` INDEX, structure conformance. The one remaining
`check_maps` line is the worktree label phantom documented above, now also written to memory as
[`check-maps-stale-is-false-in-worktrees`](../../_memory/check-maps-stale-is-false-in-worktrees.md)
so the next lane inherits the cure rather than the warning.

## ⚠ Handed back — open items

1. ~~**Pre-existing repo-map drift**~~ — **CLOSED in the second pass.** It was never drift on `main`;
   it was the worktree label trap described above. Regenerated and proved byte-identical. The
   underlying generator flaw remains and is written up as a recommended follow-up ticket.
2. **`tea_testing_guide.md`** — titled *"**AviationChat** Test-Architecture Retrofit"*, 84
   project-specific hits in 926 lines. An AGY field guide the lobby now gates. Whether it belongs
   here is an architecture call needing an **AVCH** ticket.
3. **AGY's `sudo_workflows_testing.md`** still at the old path/name — recorded as open drift in
   `sop-currency.md`; needs an AVCH ticket.
4. ~~**The parked pair**~~ — **CLOSED in the second pass**, committed here on operator instruction.
5. **`rollout`** — an untracked 15-byte file at the repo root containing `YES - COMPLETE`. Nothing in
   the toolkit writes it and no commit has ever touched it; it looks like a shell redirect that caught
   an answer meant for a prompt. **Left untracked and undeleted** — not this lane's to remove, and a
   stray file is cheaper than guessing wrong about one.
