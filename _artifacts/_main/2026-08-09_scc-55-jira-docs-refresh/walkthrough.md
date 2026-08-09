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

## Findings I did not act on

**⚠️ Saved filter 10010 `Deferred` does not filter deferred work.** Its JQL is
`created >= -30d order by created DESC` — a *recently created* view wearing the wrong name. It
replaced the old 10003/10004 pair and picked up the wrong query on the way. It wants
`status = Deferred ORDER BY project ASC, key ASC`.

**Left as found.** Saved filters are operator-owned (guardrail 2: *placement stays the operator's*),
and this is one edit in the UI. Both docs now record the real JQL to use instead, and the guide flags
the filter itself.

**Two dead entries in `diagrams_guides/INDEX.md`** — `system/gitnexus-usage-guide.md` and
`system/updated_folder_file_structure_diagram.md`. Both pre-existing; neither file exists anywhere in
the tree. Whether those docs should be written or the rows deleted is a call I don't own. A third,
`system/git_walkthrough_settings.md`, **was** a relocation — the file lives in `_quick_reference/` —
so that one I repointed.

## Two errors caught in my own copy

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
| Board counts | `SCC` 5 Epic + 25 Task · `AVCH` 5 Epic + 18 Story + 7 Task |
| The `--fields` whitelist trap | now recorded in both docs — guide §12 gotcha 2, manual §6 |

`Verdict: PASS @ HEAD` — docs only, no deployable surface in this repo.

## Your Actions

**One, and it takes fifteen seconds.** Fix saved filter **10010**'s JQL in the Jira UI to
`status = Deferred ORDER BY project ASC, key ASC`. Until then the `Deferred` filter shows you
everything created in the last 30 days, which is not the same list and never will be.

Optional: decide whether the two dead `INDEX.md` rows want documents written or rows removed.
