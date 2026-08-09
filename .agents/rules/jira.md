---
name: jira
description: "How ANY agent on this machine reads and writes the live Jira board: the authenticated `acli` CLI — no MCP, no API config, plain shell. Load whenever the board comes up outside a sudo command (what's In Progress? move this ticket, mint a ticket, JQL). Carries the command cheat-sheet, the flag traps, the ticket↔file join, the label vocabulary, and the guardrails (never invent a key; minting happens at two wired seams; placement is the operator's)."
---

# Jira operations — the board is one shell command away

**The fact every platform misses:** Jira is fully reachable from this machine RIGHT NOW via
**`acli`** (`/opt/homebrew/bin/acli`), already authenticated — the API token lives in the macOS
keychain, **never** in a repo file, a commit, or chat. There is no MCP server and none is needed:
if you can run a bash command, you can read and write the board. "I have no Jira integration" is
false by design — the CLI *is* the integration, chosen precisely so every platform (Claude Code,
Gemini, opencode, Codex, Antigravity) shares one tool with zero per-platform config.

## The map

Site: `https://sudo-command.atlassian.net` — two team-managed projects:

| Key | Project | Repo |
|---|---|---|
| `SCC` | Sudo Command Center | `Sudo_Hatter_Command` (the lobby — **this repo**) |
| `AVCH` | Aviation Chat | `Projects/AGY_AVIATIONCHAT` |

Each repo declares its own key in `.agents/jira.conf`; the armed commit-msg hook rejects the wrong
project's key. Statuses: `To Do` · `In Progress` · `In Review` · `Done` · `Deferred` · `Blocked`
(once added per board in the UI — until then the `blocked` label alone carries the signal) —
**Deferred sits in the To Do category on purpose** (a Done-category status would make descoped work
read as shipped). Descoped work = `Deferred` + the `descoped` label.

## Work-item types — and the ONE thing that decides them

**Everything is parented. The parent is therefore NOT the discriminator** (operator ruling
2026-08-08 — this is the rule an agent gets wrong first, so read it before minting anything).

There are **two kinds of Epic** and they are indistinguishable in Jira's UI:

| Kind of epic | How you recognize it | What its children are |
|---|---|---|
| **BMAD epic** | summary carries the BMAD number — `Epic 19 — ADK 2.x Runtime Upgrade`; it has a matching epic in the project's `epics.md` and rows on `sprint-status.yaml` | **`Story`** — each carries a BMAD number (`19.1`, `12.3.4`) and **has a story file** in `_bmad/bmm/stories/` |
| **Grouping epic** | no BMAD number — `CI/CD Improvment`, `New Epic Feature or Fix`, `Thin toolkit` | **`Task`** — chore/toolkit/ad-hoc work with **no story file and no BMAD epic**, filed under the umbrella so it does not float loose |

**The four types, and how each is decided:**

| Type | What it is | How it is recognized |
|---|---|---|
| **`Epic`** | a container — BMAD epic *or* grouping epic | minted by hand; never computed |
| **`Story`** | BMAD sprint work: a planned story in `epics.md` + `sprint-status.yaml`, under a BMAD epic. **Debug stories are Stories** — they run the same loop, they just fix rather than build | a **dotted BMAD number** (`19.2`, `12.3.4`) **OR** a **`debug-` id** (`debug-4.1-hr-date-fixes`) **OR** a **story file** in `_bmad/bmm/stories/` |
| **`Task`** | workflow / IDE / rules / skills / toolkit work — **not** a story, filed under a grouping epic because Jira offers no other container | none of the above |
| **`Bug`** | **TEMPORARY.** A `Story` **or** a `Task` found to be broken wears `Bug` and comes back out of a finished status until the fix lands. Same ticket, same number, same story file — flagged | never computed — **raised** by an audit or by hand, **cleared at close-out** |

**The `Bug` lifecycle — two doors in, one door out.** All three moves are one script (SCC-54):

```
an audit finds a live bug  ->  jira_feed.py trace --path <file>:<line>     (PROPOSES, never writes)
                               jira_feed.py flag  --key <K> --reason "..." --apply
the operator finds one     ->  the same `flag` call, typed by hand
the fix lands, close-out   ->  jira_feed.py devrecord --key <K> --closing --apply
```

`flag` does the whole flip and proves it landed: `Story|Task -> Bug`, `Done -> To Do`, and a **Bug
flag** comment carrying the reason, the evidence, and *what the ticket was* so the restore is
auditable. It is **idempotent** — a ticket already flagged is a no-op, so two testers finding the
same bug cannot fight over the board — and it **only moves a ticket out of `Done`**: one sitting
`In Progress` or `In Review` was never finished, and shoving it back to `To Do` would erase real
state to record something the type already says. It refuses an `Epic` outright.

⛔ **`trace` proposes; only a human hands a key to `flag`.** They are two verbs so that they cannot
be one. The trace answers *"which ticket last touched this line"*, which is **not** the same question
as *"which ticket introduced this bug"* — a later unrelated edit takes the blame outright. A wrong
answer pulls an innocent ticket out of `Done`, and nothing restores the board's history of having
been right. `flag` therefore takes `--key` and only `--key`; it will not read a trace.

**Both raisers are legitimate**, and the audit is the primary one: it is the path that finds bugs
nobody has noticed yet. The manual flip is the same operation done by a human who spotted it first.
**`/sudo-live-testing-team` is the wired entry point** (Step 3.5) — it is the one command that flies
the running app and files a researched bug doc per symptom, so it already holds exactly what `trace`
needs. Any other audit can call the same two verbs; nothing about them is that command's private.

⛔ **Nothing else may retype a `Bug`.** It carries the same number and the same story file it always
did, so every rule here reads it as a mistype — and "correcting" it mid-flight **erases the only
signal that the work is broken.** Exactly one thing clears it: `jira_feed.py devrecord --closing`,
run by whichever close-out owns the ticket (`/sudo-update-sprint-memory` Step 4.5 for a Story,
`/close-task-merge-tree` Step 4 for a Task), because close-out is the one moment anything can know
the fix landed. The bulk `audit` **cannot** tell "still broken" from "fixed", so it reports Bugs and
moves on.

⛔ **It restores to `Story` OR `Task`, whichever the rule says the ticket is** — never always `Story`.
The first cut restored only to `Story`, so a flagged **Task** hit a "does not look like BMAD sprint
work" warning and **stayed a `Bug` permanently**, with nothing left in the system able to clear it.
Task work breaks exactly as easily as story work.

**Why Story needs THREE signals, not one.** The **number** is true *before* the story file exists —
backfilled rows are minted from `epics.md` long before ① picks them up, and `19.2` sitting in
`backlog` is a planned sprint story, not toolkit work. The **`debug-` marker** carries the ids that
have no dotted number of their own. The **file** catches the rest (`tea-16-…`). Any one is enough;
no single one survives the real board, which is how this rule was wrong twice before it was pinned.

**Worked example — the AVCH board is the reference shape:**

```
AVCH-18  Epic  "Epic 19 — ADK 2.x Runtime Upgrade"      <- BMAD epic
  AVCH-33..36, 45   Story   "19.1 — …" … "19.5 — …"     <- numbered; 19.2/19.4 have no file YET
AVCH-13  Epic  "Epic 12 — PPL Curriculum Activation"    <- BMAD epic
  AVCH-14, 15, 16   Story   "12.3 — …", "12.3.4 — …"
AVCH-43  Epic  "CI/CD Improvment"                       <- GROUPING epic, no BMAD number
  AVCH-44, AVCH-46  Task    "Separate front/back end"   <- workflow work, no BMAD story
```

⚠️ **A debug story does NOT belong here.** An earlier version of this example filed `debug-4.1` as a
`Bug` under the grouping epic, which contradicted the type table above it twice over — a debug story
is a **`Story`**, and it lives under its own **BMAD epic**, because it runs the ordinary story loop
and only fixes rather than builds. `Bug` is a *flag on a ticket that turned out to be broken*, not a
category of work. Corrected 2026-08-09 (SCC-53).

**SCC is the pure case:** the command centre has **no** `_bmad/bmm/stories/` and no sprint board, so
every one of its 27 non-epic tickets is a `Task` under one of its five grouping epics. The rule
produces that with no per-project switch.

`jira_feed.py mint` **derives** the type rather than defaulting it, so it cannot drift back — a
fixed default is how the whole board ended up `Task`. It warns when sprint work has no `--epic-key`.
`--type` overrides whenever the operator reclassifies.

**The type decides which close-out can reach it.** This is the practical consequence of the table
above, and the reason `Task` needed a command of its own:

| Type | Branch | Closes out with | Why the other one cannot |
|---|---|---|---|
| **`Story`** | `claude/<KEY>-<slug>` off the epic branch | `/sudo-update-sprint-memory` | it lands on the **epic** branch, never `main` |
| **`Task`** | `chore/<KEY>-<slug>` off `main` | **`/close-task-merge-tree`** (SCC-49) | close-out reads a sprint board, flips a story status and lands on an epic branch — a Task has **none of the three**, so the command has nothing to operate on |
| **`Epic`** | `epic/<KEY>-<slug>` off `main` | `/sudo-push-e2e` | — |

`/close-task-merge-tree` files the same **one** Dev Record through `jira_feed.py devrecord` and moves
the ticket to `Done` itself, and it **does** pass `--closing` — a Task can be flagged `Bug` exactly
like a Story, so the Task lane has to clear it too, restoring `Task` rather than `Story`. Before it
merges, `task_preflight.py` re-asks the type question **from the diff**: a
`chore/*` branch that touches `backend/ · frontend/ · firebase/ · functions/ · mobile/ · .github/` is
refused and handed to `/sudo-push-e2e`, because a change reaching deployable code is a product change
whatever its ticket type says.

**Auditing the board:** `python3 .agents/scripts/jira_feed.py audit --jira-project <PROJ> --project
<P>` reports every ticket whose type disagrees with this table; `--apply` converts them and reads
each one back. It **never retypes a `Bug`** — a bulk pass cannot tell "still broken" from "fixed",
and that judgment is not the rule's to make. Only close-out knows, so only `devrecord --closing`
clears it.

**Label vocabulary** — a card holds ONE status but stacks labels, which is exactly why these are
labels (a story can be quick-dev-eligible AND blocked at once). All three are ruled by ①
`/sudo-write-story-tests` at story pickup:
`quick-dev` = ships via `/sudo-quick-dev` instead of the full ①②③ loop ·
`parallel-ok` = no file overlap with the epic's other in-flight stories, safe to run beside them ·
`blocked` = waiting on a linked blocker (the `Blocks` link names WHAT; pair with the `Blocked`
status where the board has it). Filter any of them:
`acli jira workitem search --jql "project = AVCH AND labels = quick-dev AND status != Done"`.

## Reading the board

```bash
acli jira auth status                                   # am I logged in, and as whom?
acli jira workitem view SCC-14                          # TRAP: view takes the key POSITIONALLY
acli jira workitem search --jql "project = SCC AND status = 'In Progress' ORDER BY key"
acli jira project list --limit 20                       # TRAP: needs --recent/--limit/--paginate
acli jira board search                                  # board ids (it's NOT `board list`)
acli jira board list-sprints --id 2 --limit 5
```

"Work on / look at everything set to <status>" is a fully supported ask: run the JQL search, then
join each ticket to its local counterpart (join rules below).

## Writing to the board

```bash
acli jira workitem comment create --key SCC-14 --body "…"        # TRAP: needs --key
acli jira workitem transition --key SCC-14 --status "In Review" --yes  # TRAP: needs --key; --yes skips the interactive confirm
acli jira workitem create --project SCC --type Task --summary "…" --description "…"
#   children of an epic: add --parent <EPIC-KEY>; --type Epic works too; --label "a,b" at create
#   ALWAYS create bare (no --assignee) — default-assignee is why everything once showed "assigned to Daniel"
acli jira workitem edit --key SCC-14 --labels "quick-dev,parallel-ok"   # REPLACES the label set
acli jira workitem link create --out SCC-10 --in SCC-14 --type Blocks   # reads: SCC-10 blocks SCC-14
```

Smart Commits (`#comment` / `#time` / `#transition` in a commit message) also work and cost zero
automation quota — but the branch-name join already links commits, so use them sparingly.

## What the dev flow WRITES onto a ticket — `jira_feed.py` (SCC-49)

Raw `acli` is above and stays valid for anything ad-hoc. But the three seams where the dev flow feeds a
ticket go through **`.agents/scripts/jira_feed.py`**, because each one had a silent failure mode that
prose could not hold:

```bash
python3 .agents/scripts/jira_feed.py outline   --story 12.3.4 --project P [--epic 12] [--out FILE]
python3 .agents/scripts/jira_feed.py mint      --story 12.3.4 --project P --jira-project AVCH \
                                               --epic-key AVCH-13 --lane full --apply
python3 .agents/scripts/jira_feed.py devrecord --key AVCH-15 --story 12.3.4 --project P \
                                               --decision "..." --pitfall "..." --apply
python3 .agents/scripts/jira_feed.py check     --key AVCH-15 --story 12.3.4
python3 .agents/scripts/jira_feed.py trace     --path backend/x.py:42 --path frontend/y.tsx
python3 .agents/scripts/jira_feed.py flag      --key AVCH-15 --reason "..." --evidence "..." --apply
```

- **`mint`** (① Step 1.6) dedupes on the BMAD number, renders the **description from the story file**
  (statement + ACs + lane rulings + file path), creates it bare and parented, then re-reads the ticket
  and exits 2 if the description did not land. Prints `JIRA_KEY=<KEY>`.
- **`devrecord`** (close-out Step 4.5, `/sudo-quick-dev` Step 3.5) files THE Dev Record — decisions,
  pitfalls, follow-ons, outcome, evidence. **Exactly one per ticket:** an existing record is updated in
  place, never stacked, so the branch-closer and the story-closer cannot leave two partial records.
- **`check`** answers "does this ticket carry both halves?" — exit 2 if not.
- **`trace`** (SCC-54) reads git history — `blame` on a `file:LINE`, `git log --no-merges` on the
  file — and ranks the tickets whose commits touched it, blame first. **No network, no board write**,
  and it only ever proposes keys from the project(s) in this repo's `.agents/jira.conf`.
- **`flag`** (SCC-54) is the raise half of the `Bug` rule, above. Needs `--reason`; reads the type
  and the status back after writing them.

Two rules that bind on YOU, not the script: **nothing is invented** (a missing story section renders
`(none found ...)` and warns — do not paper over it), and **the buckets are yours to fill.** The
walkthrough scrape underneath is a safety net, not the source: close-out has just finished routing the
session's learnings, so pass them with `--decision` / `--pitfall` / `--followon`. A record that says
`(none recorded)` on a story that fought back means the routing was thin, not that nothing happened.

## Who mints tickets — two wired seams

Agents MAY mint (operator ruling 2026-08-07): every ticket carries its provenance — the BMAD number
in the summary, the board row / spec pointer in the description — so nothing lands untraceable.

- **Epics** → `/sudo-create-epic-sprint` Step 1.5, at kickoff (the operator is in the room).
- **Stories** → `/sudo-write-story-tests` ① Step 1.6, at pickup: child of the epic ticket, bare,
  labels from ①'s lane/parallel/blocked ruling, `jira_key:` stamped into the story frontmatter.
- **Toolkit/chore work** → mint the repo's chore ticket before cutting `chore/<KEY>-<slug>`.

Outside these seams: status + comments only. Never mint speculative work — a ticket asserts a
decision already made; "maybe" items live in the deferred ledgers, and the operator purges
unrecognized tickets on sight.

## The ticket ↔ file join (all literal strings — no magic)

- **Branch names** carry the key immediately after the prefix (`epic|claude|chore/<JIRA-KEY>-<slug>`);
  Atlassian's GitHub app links every commit on a correctly-named branch.
- **Story files** (`_bmad/bmm/stories/`) carry `jira_key:` in their frontmatter — that is the
  machine join from a ticket back to the file (and the YAML row key, which NEVER changes).
- **Jira summaries** carry the BMAD number (`Epic 12 — …`, `12.3.4 — …`) — the human join.

## Guardrails

1. **Never invent a key.** A key comes from an existing ticket, a branch name, or the create output
   of a ticket you just minted at one of the two seams — never from imagination. A well-formed wrong
   key is worse than none — it silently decorates the wrong ticket.
2. **Placement stays the operator's.** Machinery mints at the two seams, moves status, and posts
   evidence — sprint/backlog placement, priorities, and board layout are human decisions.
3. **Bare-state board.** Only OPEN work gets tickets. Never resurrect finished epics as tickets —
   done work is file history (`sprint-status.yaml`, `epics.md`), not board rows.
4. **Don't double-move.** Four transitions are already automated: `/sudo-push-e2e` Step 6.5 moves the
   EPIC ticket at merge; `/sudo-update-sprint-memory` Step 4.5 moves the STORY ticket at close-out;
   `/close-task-merge-tree` Step 4 moves the TASK ticket to `Done`; and `jira_feed.py flag` moves a
   ticket **out of `Done`** when it is found broken. Outside those, transition a ticket only when the
   operator asks.
5. **The token stays in the keychain.** Never echo, copy, or persist it anywhere.
