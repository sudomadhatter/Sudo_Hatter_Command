---
type: walkthrough
story: SCC-55
date: 2026-08-09
branch: chore/SCC-55-jira-docs-refresh
---

# SCC-55 — the two Jira human docs, brought up to the system they describe

Both were written 2026-08-07 and never touched again. Everything from SCC-41 through SCC-54 landed
after them, so the guide's "not built yet" ledger was listing shipped work and the manual was
teaching a rule that had been reversed. **Every claim below was checked against the live board or
the repo, not against memory.**

## What was actually stale

### `jira_integration_guide.md`

| § | It said | Reality |
|---|---|---|
| §12 | "NOT BUILT: the `acli` wrapper in `.agents/scripts/`" | `jira_feed.py`, **seven verbs**, shipped SCC-49 |
| §12 | "NOT BUILT: `/sudo-*` wiring — kickoff minting, push-e2e transitioning" | both wired: `/sudo-write-story-tests` Step 1.6, `/sudo-push-e2e` Step 6.5 |
| §12 | "NOT BUILT: tickets for your open work" | `SCC` 30 · `AVCH` 30 |
| §12 | "the 16 onboarding sample tickets are still present" | deleted — `SCC-1`…`SCC-3` don't resolve |
| §11 | filters `AVCH Deferred` 10003 / `SCC Deferred` 10004 | **both ids are gone.** Live set is 10005/10006/10007/10009/10010 |
| §3 | 8 parts | missing `jira_feed.py`, `task_preflight.py`, and 2 of the 3 armed commit hooks |
| §6 | one lifecycle | there are **three** lanes; the Task lane was absent entirely |
| — | no type model, no `Bug` lifecycle | the two central rules of the current system |

### `jira_manual.md`

The worst line in either doc, §2.2 step 3:

> "`Task` for plumbing, `Story` for user-facing… **The Story/Task line is soft; pick one and stay
> consistent.**"

That is now backwards. The type is computed by `work_type()` and **it decides which close-out command
can reach the ticket at all** — pick wrong and the ticket is stranded, because the command that would
close it has nothing to operate on. Replaced with §2.2.1, a decision diagram and the two-kinds-of-epic
trap.

Also missing: the `Bug` flag (§2.6, new — *you never create a Bug ticket*), the `Blocking` status,
`/close-task-merge-tree` (§3.8, new), and 2 of the 3 hooks that can now refuse a commit.

## The saved filters — asked, executed, two repaired

I first reported the filters by **reading their JQL**. On the operator's challenge — *"do any of the
filters work?"* — I ran all five. **None of them returned useful work.** Reading a query is not
running it, and that gap is the whole lesson here: a filter that runs cleanly and returns the wrong
list is indistinguishable from one that works.

| Filter | Id | Before | After | Verdict |
|---|---|---|---|---|
| `Deferred` | 10010 | 30 irrelevant rows | **16** | **REPAIRED** — JQL was `created >= -30d`, a *recently created* view wearing the wrong name. Replaced the retired 10003/10004 pair and picked up the wrong query on the way |
| `Blocked` | 10007 | 0 | **2** | **REPAIRED** — matched only `labels = blocked`, and no ticket carries a label. Two tickets are genuinely blocked (`SCC-23`, `SCC-46`, status `Blocking`) and it found neither. Now `(labels = blocked OR status = Blocking)` |
| `Descoped` | 10009 | 0 | 0 | **Correct, and correctly empty** — `deferred-work.md`: *"assume every entry is parked, not queued."* Nothing has been terminally killed |
| `Quick-Dev` | 10005 | 0 | 0 | **Correct, awaiting input** — written at story pickup by `jira_feed.py mint`; every current ticket predates that seam |
| `Parallel-OK` | 10006 | 0 | 0 | same |

**The root cause behind three of them is not the filters: not one ticket across either board carries
a single label.** Editing JQL cannot fix that, and for two of the three it needs no fixing — they
populate themselves at the next story pickup. Old JQL recorded above for rollback; `acli jira filter
update --id <id> --jql '<old>'` reverses either edit.

**Not acted on — a label backfill.** Deciding which existing tickets are `quick-dev` or `parallel-ok`
is a lane ruling, not something derivable from the board. Left for the operator.

## Findings I did not act on

**Two dead entries in `diagrams_guides/INDEX.md`** — `system/gitnexus-usage-guide.md` and
`system/updated_folder_file_structure_diagram.md`. Both pre-existing; neither file exists anywhere in
the tree. Whether those docs should be written or the rows deleted is a call I don't own. A third,
`system/git_walkthrough_settings.md`, **was** a relocation — the file lives in `_quick_reference/` —
so that one I repointed.

**A stray status on AVCH: `Open Epics`**, holding exactly one item (`AVCH-14`, the `12.3` umbrella
story). A board column that became a status. Harmless, but it means "everything open" is not
`status != Done` on that board. Recorded in both status tables; not changed.

## Three errors caught in my own copy

0. **I published board counts that were silently truncated.** `acli jira workitem search` pages at
   **30** by default and says nothing about it. `project = SCC` returned 30, `project = AVCH`
   returned 30, and I wrote both into the guide as totals. Both were wrong — the real figures are
   **SCC 37** (5 Epics + 32 Tasks) and **AVCH 40** (8 Epics + 21 Stories + 11 Tasks). Caught only
   because `project IN (SCC, AVCH)` *also* returned exactly 30, which cannot be true of a union.
   **`--paginate` is not optional when you are counting anything.** Corrected in three places.


1. **The work-type diagram had a dangling node pair.** The `Epic` question was drawn as an orphan
   fragment with no edge into the main decision. Restructured so the container question is asked
   first. Caught by structural validation, not by reading it.
2. **My `flag` example used `SCC-42`, which is a live ticket** about GitNexus audit effectiveness —
   the example would have read as if a real ticket were broken. Switched to `AVCH-57`, this page's
   established placeholder, and verified it does not resolve.

Related: both docs used **`AVCH-40` as the epic-key example**, and `AVCH-40` is live and is a
**Story** (`22.3 — Golden RAG Retrieval`). Harmless before; actively misleading now that §6 makes the
Epic/Story distinction load-bearing. Swapped to `AVCH-18` (`Epic 19 — ADK 2.x Runtime Upgrade`), a
real Epic, across 7 references — which also fixes the `create --type Story --parent AVCH-40` example,
since parenting a Story to a Story was the wrong shape.

## Evidence

| Claim | Proof |
|---|---|
| Enforcement suite green | `run_all.py` → **8/8 files** |
| Lint | 1 ERROR, pre-existing (`19-5-adk-agent-evaluation-stage-2`, AGY epic-19) — untouched |
| Every mermaid block valid | 14 blocks (9 guide + 5 manual) structurally checked; the 4 new/reworked ones round-tripped through the renderer → `valid: true` |
| Links | 3 broken in `INDEX.md`, all pre-existing (confirmed against `HEAD`); 1 repointed, 2 reported above. Zero broken in either Jira doc |
| Every backticked repo path resolves | 0 missing |
| Every ticket key audited | 22 keys checked live: real ones used correctly, placeholders confirmed non-resolving |
| Board counts (paginated) | `SCC` 37 = 5 Epic + 32 Task · `AVCH` 40 = 8 Epic + 21 Story + 11 Task |
| Every saved filter **executed**, not read | 5/5 run; 2 repaired and re-run to confirm (16 and 2 results) |
| The `--fields` whitelist trap | now recorded in both docs — guide §12 gotcha 2, manual §6 |

`Verdict: PASS @ HEAD` — docs only, no deployable surface in this repo.

## Your Actions

**Nothing blocking.** Two optional calls:

1. **A label backfill.** `Quick-Dev` and `Parallel-OK` will populate on their own from the next story
   pickup. If you want them useful *now*, the labels have to go onto existing tickets by hand — and
   which tickets are quick-dev-eligible is your ruling, not something I can read off the board.
2. **The two dead `INDEX.md` rows** — documents written, or rows removed.

And one thing to carry forward: **`acli` search pages at 30 silently.** Any count taken without
`--paginate` is a floor, not a total.
