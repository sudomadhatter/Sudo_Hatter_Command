---
type: implementation_plan
story: SCC-49
date: 2026-08-08
branch: chore/SCC-49-jira-dev-feed
---

# SCC-49 — Feed dev knowledge back into the Jira ticket

**The ticket:** ① `/sudo-write-story-tests` must give the Jira story a short outline of what it is
about; `/sudo-update-sprint-memory` must add the notes, pitfalls and decisions made *as the story was
actually developed*. "We want the record here too."

**Today (verified):** ① mints with `--summary` only — no `--description` flag anywhere in the body, so
every story ticket on the board is a bare title. Close-out Step 4.5 posts one line (verdict +
walkthrough path). Neither half of SCC-49 exists. The epic mint (`/sudo-create-epic-sprint` Step 1.5)
has the same hole.

**Approach (operator ruling 2026-08-08):** script-backed, not prose. House law — *an instruction may
only be deleted after a script enforces it* (`scripts/INDEX.md`). Prose alone is the exact failure mode
that produced `story_status.py`.

## Scope

| In | Out |
|---|---|
| Story mint gets a rendered description (①) | `/sudo-quick-dev` ad-hoc chore lane (never reaches close-out — separate ticket) |
| Close-out posts a Dev Record comment | Changing ticket type Task → Story (board shape is the operator's) |
| Epic mint gets a description (`/sudo-create-epic-sprint`) | Backfilling descriptions on the ~20 existing bare tickets |

## The build

### 1. `.agents/scripts/jira_feed.py` (new, stdlib-only, ~450 lines)

Four verbs. `acli` is located via `--acli` / `$ACLI_BIN` / `PATH` so the tests can inject a stub.

| Verb | Does | Called from |
|---|---|---|
| `outline` | renders a ticket description from the **story file** (title + story statement + ACs + lane rulings + file path), or from `epics.md` with `--epic N`. Render-only, no network. | (inspection / `--out`) |
| `mint` | dedupe-search by BMAD number → reuse or create with `--description-file`, then **read the ticket back** and fail if the description did not land. Backfills a description onto a reused bare ticket. | ① Step 1.6 |
| `devrecord` | renders the **Dev Record** comment (decisions · pitfalls · follow-ons · outcome · evidence), posts it, reads the comment list back and fails if the marker is absent. | close-out Step 4.5 |
| `check` | is this ticket carrying a description AND a Dev Record? Flattens Atlassian ADF. `wf.Report` exit 0/1/2. | close-out verify; `closeout_preflight` later |

**Where the content comes from.** The outline is *mechanical* — the story file already holds the story
statement and the ACs, so the script reads them and nothing is invented. The Dev Record is *authored* —
close-out has just finished Step 3's learning routing, so it passes the buckets in as repeatable
`--decision` / `--pitfall` / `--followon` flags; the walkthrough scrape (`## Close-Out Handoff`,
`## Code Review` verdict, `## Suite Ledger`) is the safety net underneath, never the only source.
An empty bucket renders `- (none recorded)` and warns on stderr; `--strict` makes it a hard fail.

**Why read-back verification.** A posted comment that silently failed looks identical to one that
worked. Both write verbs re-read the ticket and exit non-zero if what they claimed to write is not
there.

### 2. Command bodies

- `.agents/commands/sudo-write-story-tests.md` Step 1.6 — mint through `jira_feed.py mint`; the dedupe
  search and the `--description` become the script's job, the lane/parallel/blocked ruling stays the
  agent's judgment and is passed as flags.
- `.agents/commands/sudo-update-sprint-memory.md` Step 4.5 — rewrite: transition, then
  `jira_feed.py devrecord --apply` with the Step 3 buckets, then `check`. The one-line comment becomes
  the structured record.
- `.agents/commands/sudo-create-epic-sprint.md` Step 1.5 — epic mint gets `outline --epic N`.

### 3. Tests — `.agents/scripts/tests/test_jira_feed.py`

Auto-discovered by `run_all.py`. Fake project tree + a **stub `acli`** (records argv, returns canned
JSON). Cases: outline renders ACs · missing story file → exit 2 · no ACs → placeholder, not a lie ·
epic outline from `epics.md` · devrecord merges flags with the walkthrough scrape · `--strict` on an
empty bucket → exit 2 · **post succeeds but read-back finds no marker → exit 2** (the load-bearing
negative) · `check` on a bare ticket → exit 2 · positive control: fully-populated ticket → exit 0.

### 4. Docs (the SOP-currency gate is ARMED — a commit touching `commands/`/`scripts/` without it is rejected)

`_my_resources/_quick_reference/sudo_workflows_testing.md` §5 (the safety net) + `.agents/rules/jira.md`
(the new verbs alongside the raw acli cheat-sheet) + `.agents/scripts/INDEX.md` (the script table).

## Risks

1. **Walkthrough parsing is free-form.** Mitigated by flags-first: the script never depends on the
   scrape, it only supplements. Empty buckets are reported, never faked.
2. **`acli` shape drift.** Verified today against the live site: `--description-file`, `--body-file`,
   `--json`, `comment list --json` all exist; description comes back as ADF and is flattened.
3. **Ticket-type question left open.** SCC-49 says "as a Story under the epic". Every existing ticket
   is `Task` parented to the Epic, and the type scheme is a board decision — flagging, not changing.

## Verification

`python3 .agents/scripts/tests/run_all.py` green (7 files), plus one **live** end-to-end against SCC-49
itself: `jira_feed.py devrecord --key SCC-49 --apply` posting this session's own record, then `check`
confirming it landed.
