---
name: jira
description: "How ANY agent on this machine reads and writes the live Jira board: the authenticated `acli` CLI — no MCP, no API config, plain shell. Load whenever the board comes up outside a sudo command (what's In Progress? move this ticket, mint a ticket, JQL). Carries the command cheat-sheet, the flag traps, the ticket↔file join, the label vocabulary, and the guardrails (never invent a key; minting happens at two wired seams; placement is the operator's)."
trigger: model_decision
triggers: [jira, ticket, the board, backlog, sprint, acli, in progress, what's next, to do next]
# Intent-shaped: no glob can catch it, because the trigger is what the operator ASKS,
# not what gets opened. Antigravity judges `description:` against the request;
# `.agents/hooks/rule-trigger.py` matches these keywords and injects a pointer.

---

# Jira operations — the board is one shell command away

**The fact every platform misses:** Jira is fully reachable from this machine RIGHT NOW via
**`acli`**, already authenticated — the API token lives in the OS credential store (the macOS
keychain on the Mac, the Windows equivalent on the PC), **never** in a repo file, a commit, or chat.
There is no MCP server and none is needed: if you can run a bash command, you can read and write the
board. "I have no Jira integration" is false by design — the CLI *is* the integration, chosen
precisely so every platform (Claude Code, Gemini, opencode, Codex, Antigravity) shares one tool with
zero per-platform config.

**Verify — never assume, and never hardcode a path.** Both the binary's location and the credential
store are per-machine; this rule is read on the Mac AND the Windows PC (`two-machines-mac-and-pc`).
One command answers "can I reach the board?" identically on every machine and every platform:

```bash
acli jira auth status      # ✓ Authenticated + site + account, or a clear failure
```

⛔ **An `acli` failure is a fact about YOUR SHELL, not about the board.** A sandboxed tool call
cannot reach the OS credential store, so `acli` fails there while working perfectly in the same repo
unsandboxed. Read that failure as *"I could not see the board"* — **never** as any of these:

| The wrong conclusion | What it actually was |
|---|---|
| "no such ticket / the board says X" | you never reached the board |
| "the CLI is no longer authenticated" | your shell couldn't reach the store; `auth status` unsandboxed says otherwise |
| "I can't mint, so I'll reuse an existing key" | see Guardrail 1 — this is how a closed ticket gets reopened by accident |

**Re-run unsandboxed before you believe it.** This produced a wrong conclusion twice on 2026-08-09 —
the second time from an agent that had correctly diagnosed the sandbox cause minutes earlier.

## The map

Site: `https://sudo-command.atlassian.net` — two team-managed projects:

| Key | Project | Repo |
|---|---|---|
| `SCC` | Sudo Command Center | `Sudo_Hatter_Command` (the lobby — **this repo**) |
| `AVCH` | Aviation Chat | `Projects/AGY_AVIATIONCHAT` |

Each repo declares its own key in `.agents/jira.conf`; the armed commit-msg hook rejects the wrong
project's key.

**Statuses are per board, and the two boards do not match** (verified live 2026-08-09 — read this
table, do not assume a shared set):

| Status | SCC | AVCH | Notes |
|---|---|---|---|
| `To Do` | ✅ | ✅ | the backlog — everything not yet chosen |
| **`To Do Next`** | ✅ | — | **the operator's hand-picked queue.** See §The queue below |
| `In Progress` | ✅ | ✅ | |
| `In Review` | — | ✅ | ⭐ **blocked-on-operator ONLY** — the ticket needs something from the operator the agent cannot do (ruling 2026-08-14). Never a resting state for finished work: merge-ready work stays `In Progress`, parked, until the operator's word closes it |
| **`Blocking`** | ✅ | — | ⛔ the name is `Blocking`, **not** `Blocked` |
| `Deferred` | — | ✅ | To Do **category** on purpose — a Done-category status would make descoped work read as shipped. Descoped = `Deferred` + the `descoped` label |
| `Done` | ✅ | ✅ | |

⛔ **`Blocked` does not exist on either board.** `transition --status "Blocked"` fails outright;
the real status is **`Blocking`** (live on SCC-23 and SCC-46). Where a board has no blocked status
at all, the `blocked` **label** alone carries the signal.

**A status missing from a board is not an error — it is not installed there yet.** Every rule below
is written per-board-optional: query the status, and if the board returns nothing for it, fall
through to the next rank silently. Adding a column in the Jira UI is therefore the **whole** install
— no rule edit, no code change.

## The queue — how "what's next?" is answered

**`To Do Next` is the operator's hand-picked queue and it outranks `To Do`** (ruling 2026-08-09).
Any "what's next?", "what should I work on?", or session-boot answer walks these ranks **in order**
and stops at the first that returns anything:

| Rank | Status | What it means |
|---|---|---|
| 1 | `In Progress` | already started — finish it before starting anything |
| 2 | **`To Do Next`** | **the operator chose these, deliberately, by hand** |
| 3 | `To Do` | the backlog — only when the two above are empty |

`Blocking` is **never** a candidate. Surface those separately as impediments, with what each is
waiting on, and never propose one as the next thing to pick up.

**One query per rank, stop at the first that returns rows.** ⛔ Do not try to rank inside the JQL —
`ORDER BY CASE WHEN …` is **not valid JQL** (`when` is a reserved word; it fails to parse). Verified
2026-08-09.

```bash
P=SCC   # or AVCH
acli jira workitem search --fields "key,summary,status" --jql "project = $P AND status = \"In Progress\" ORDER BY key"
acli jira workitem search --fields "key,summary,status" --jql "project = $P AND status = \"To Do Next\"  ORDER BY key"
acli jira workitem search --fields "key,summary,status" --jql "project = $P AND status = \"To Do\"       ORDER BY key"
acli jira workitem search --fields "key,summary,status" --jql "project = $P AND status = \"Blocking\"    ORDER BY key"  # impediments, reported separately
```

**Why the fall-through is safe** (verified 2026-08-09): a status a board does not have returns
**exit 0 with zero rows** — `status = "To Do Next"` against AVCH is silent today, not an error,
because the name is registered site-wide. Only a name that exists on **no** board exits 1. So an
empty rank is genuinely "nothing queued", and a non-zero exit is a real failure worth reporting.

⛔ **Never answer a "what's next" question from `_my_resources/open_tasks/todo_list.md`.** It is
retired as an agent source (ruling 2026-08-09) — it is the operator's personal notes, it is stale,
and it duplicates tickets that already exist. Read the board.

**On a BMAD project, `To Do Next` overrides the computed pick.** `/cicd-boot-sprint-memory` derives
the next story from `sprint-status.yaml`; that YAML lags **by design** (② and ③ never write it, only
close-out does). A card the operator placed in `To Do Next` beats a stale computed recommendation —
report the override explicitly rather than silently replacing one with the other.

## Work-item types — and the ONE thing that decides them

**Everything is parented. The parent is therefore NOT the discriminator** (operator ruling
2026-08-08 — this is the rule an agent gets wrong first, so read it before minting anything).

There are **two kinds of Epic** and they are indistinguishable in Jira's UI:

| Kind of epic | How you recognize it | What its children are |
|---|---|---|
| **BMAD epic** | summary carries the BMAD number — `Epic 19 — ADK 2.x Runtime Upgrade`; it has a matching epic in the project's `epics.md` and rows on `sprint-status.yaml` | **`Story`** — each carries a BMAD number (`19.1`, `12.3.4`) and **has a story file** in `_bmad/bmm/stories/` |
| **Grouping epic** | no BMAD number — `CI/CD Improvment`, `New Epic Feature or Fix`, `Thin toolkit` | **`Task`** — chore/toolkit/ad-hoc work with **no story file and no BMAD epic**, filed under the umbrella so it does not float loose |

**The five types, and how each is decided:**

| Type | What it is | How it is recognized |
|---|---|---|
| **`Epic`** | a container — BMAD epic *or* grouping epic | minted by hand; never computed |
| **`Story`** | BMAD sprint work: a planned story in `epics.md` + `sprint-status.yaml`, under a BMAD epic. **Debug stories are Stories** — they run the same loop, they just fix rather than build | a **dotted BMAD number** (`19.2`, `12.3.4`) **OR** a **`debug-` id** (`debug-4.1-hr-date-fixes`) **OR** a **story file** in `_bmad/bmm/stories/` |
| **`Task`** | workflow / IDE / rules / skills / toolkit work — **not** a story, filed under a grouping epic because Jira offers no other container | none of the above |
| **`Subtask`** | one piece of a single `Task`'s job, big enough to earn **its own branch and its own worktree** — ⭐ see §Subtasks | its **parent's type** is a `Story`/`Task` rather than an `Epic`. A board read, never a string test |
| **`Bug`** | **TEMPORARY.** A `Story` **or** a `Task` found to be broken wears `Bug` and comes back out of a finished status until the fix lands. Same ticket, same number, same story file — flagged. ⛔ **Never a `Subtask`** — see §Subtasks | never computed — **raised** by an audit or by hand, **cleared at close-out** |

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
**`/cicd-live-testing-team` is the wired entry point** (Step 3.5) — it is the one command that flies
the running app and files a researched bug doc per symptom, so it already holds exactly what `trace`
needs. Any other audit can call the same two verbs; nothing about them is that command's private.

⛔ **Nothing else may retype a `Bug`.** It carries the same number and the same story file it always
did, so every rule here reads it as a mistype — and "correcting" it mid-flight **erases the only
signal that the work is broken.** Exactly one thing clears it: `jira_feed.py devrecord --closing`,
run by whichever close-out owns the ticket (`/cicd-close-story-merge-tree` Step 4 for a Story,
`/smh-close-task-merge-tree` Step 4 for a Task), because close-out is the one moment anything can know
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
| **`Story`** | `claude/<KEY>-<slug>` off the epic branch | `/cicd-close-story-merge-tree` | it lands on the **epic** branch, never `main` |
| **`Task`** | `chore/<KEY>-<slug>` off `main` | **`/smh-close-task-merge-tree`** (SCC-49) | close-out reads a sprint board, flips a story status and lands on an epic branch — a Task has **none of the three**, so the command has nothing to operate on |
| **`Subtask`** | `chore/<KEY>-<slug>` off `main` — **its own**, exactly like a Task | **`/smh-close-task-merge-tree`** | nothing else: a subtask is a leaf that ships code, so it lands its own branch as it finishes. Its **parent** closes LAST, and `task_preflight.py` refuses the parent while any child is still open (SCC-119). ⭐ **Riders — the DEFAULT when able (SCC-170, was the SCC-156 exception):** a subtask whose work rides the parent's consolidated lane ships **no branch of its own** — declare it under `riders:` in the parent lane's `task.yaml`, and the parent's close ceremony transitions it to `Done` first, parent last, as an agent write. **Who decides: the agent, and it says why** — `work-consolidation.md` rule 2, one lane when the subtasks share a repo and a lane class, separate lanes when they genuinely run in parallel. It is no longer "when the operator orders it" |
| **`Epic`** | `epic/<KEY>-<slug>` off `main` | `/cicd-push-e2e` | — |

`/smh-close-task-merge-tree` files the same **one** Dev Record through `jira_feed.py devrecord` and moves
the ticket to `Done` itself, and it **does** pass `--closing` — a Task can be flagged `Bug` exactly
like a Story, so the Task lane has to clear it too, restoring `Task` rather than `Story`. Before it
merges, `task_preflight.py` re-asks the type question **from the diff**: a
`chore/*` branch that touches `backend/ · frontend/ · firebase/ · functions/ · mobile/ · .github/` is
refused and handed to `/cicd-push-e2e`, because a change reaching deployable code is a product change
whatever its ticket type says.

**Auditing the board:** `python3 .agents/scripts/jira_feed.py audit --jira-project <PROJ> --project
<P>` reports every ticket whose type disagrees with this table; `--apply` converts them and reads
each one back. It **never retypes a `Bug`** — a bulk pass cannot tell "still broken" from "fixed",
and that judgment is not the rule's to make. Only close-out knows, so only `devrecord --closing`
clears it. **Subtasks are no longer skipped** (SCC-119): they were passed over as "containers",
which was wrong twice — a subtask is a leaf, and skipping meant nothing ever checked the things
that actually rot. It now checks **placement** instead of type (no parent · parented to an `Epic` ·
nested under another subtask · a parent lagging its children) and **never auto-fixes any of them**,
because re-parenting is a board move and the right parent is the operator's call.

**Label vocabulary** — a card holds ONE status but stacks labels, which is exactly why these are
labels (a story can be quick-dev-eligible AND blocked at once). **Two writers, and which one owns a
label is not cosmetic:**

| Label | Means | Written by |
|---|---|---|
| `quick-dev` | ships via one light lane (`/cicd-quick-dev`, or `/smh-quick-dev` for Task work) instead of the full ①②③ loop | ① `/cicd-write-story-tests` at pickup, **and** the labelling pass — see below |
| `blocked` | waiting on a linked blocker (the `Blocks` link names WHAT; pair with the `Blocking` status where the board has it) | ① `/cicd-write-story-tests`, at pickup |
| **`parallel-ok`** | in the approved set the last check computed — safe to run beside **every other** 🟢 under that parent | ⭐ **the labelling pass, and nothing else** |
| **`user-tasks`** | merged, but the walkthrough leaves something only the operator can decide — read the "User tasks" comment | ⭐ **`jira_feed.py finish`, at close-out** (SCC-155) |
| **`bugs-and-updates`** | **the ROLLING ticket** — the one always-open `Bugs and Updates - <YYYY-MM>` Task that discovered work files under as a Subtask when no thematic parent fits (`work-consolidation.md` rule 1, rung 3). Exactly ONE open at a time; find it by this label before you mint anything | by hand, on the Task that opens the cycle (SCC-191) |

**The labelling pass is one engine behind two commands**, and which one you run is decided by the
parent, not by preference:

| Parent | Command | Children it assesses |
|---|---|---|
| a **BMAD epic** | `/cicd-label-tasks <EPIC-KEY>` | Stories, grounded by story file / plan / branch diff |
| a **Task** | `/smh-label-tasks <TASK-KEY>` | its Subtasks, grounded by `task.yaml` plan / branch diff / description |

Point either at the other's parent and it refuses by name and hands you across. ⛔ The old
`/cicd-parallel-check` is **retired** (SCC-155) — nothing answers to that name.

⛔ **`parallel-ok` is meaningless without its stamp, and ① must never write it** (operator ruling
2026-08-09, SCC-56). It is a property of a **set at a moment**, not of one story: ① mints 19.1's
ticket before 19.2's file exists, so it has nothing to compare against and never re-evaluates.
Proof it never worked — **zero** tickets across both boards carried it. The fix was the writer, not
the field: a parent-scoped pass recomputes the set and **rewrites every child's label in one go**,
so it is self-correcting on re-run. **A `parallel-ok` whose parent comment stamp
(`verified <date> against N children: …`) no longer matches that parent's current children is stale
— re-run, never trust.** `label_tasks.py check --parent <KEY>` answers that in one call.

⭐ **`quick-dev` has TWO writers, and that is deliberate** (SCC-155). ① still mints it at pickup for
a story the labelling pass has never swept — otherwise a story picked up before any sweep would
carry nothing. When the pass DOES run it is authoritative for the children it assessed, and it
rewrites them the same self-correcting way as `parallel-ok`. **A child the pass left unassessed
keeps its label untouched** — the engine carries "unassessed" as a distinct state from "not
eligible", so a re-run never strips a label off work marked by hand.

Filter any of them:
`acli jira workitem search --jql "project = AVCH AND labels = quick-dev AND status != Done"`.

## Subtasks — the ticket you were handed is the top-level one

⭐ **Operator ruling 2026-08-12 (SCC-119).** When you are handed a ticket and your plan breaks it into
several pieces of real work, those pieces go **underneath it as `Subtask`s** — not beside it as more
`Task`s. Flatten them into siblings under the grouping epic and the one fact that mattered is
destroyed: *these are all one job.* This writes down what the board already did by hand — SCC-38,
SCC-98 and SCC-116 each parent their own set, and SCC-116's own description says
*"make all the tasks sub tasks to these two tasks for organization."*

### The hierarchy — three levels, and it does not nest

| Level | Type | Parent must be |
|---|---|---|
| 1 | `Epic` | — (top) |
| 0 | `Story` · `Task` · `Bug` | an `Epic` |
| **−1** | **`Subtask`** | a **`Story` or `Task`** — never an `Epic` |

⛔ **A `Subtask` cannot have children.** `hierarchyLevel: -1` is the floor. A subtask that turns out to
need its own breakdown has exactly two legal moves: keep that breakdown as a **checklist inside it**, or
**promote it to a `Task`** and re-parent. Trying to nest returns an opaque Jira error, so decide here.

⛔ **The parent is still not the discriminator — the parent's TYPE is.** Everything on this board is
parented (§Work-item types), so *having* a parent says nothing. Parent is an `Epic` → the ticket is a
`Story`/`Task`. Parent is a `Story`/`Task` → it is a `Subtask`. That is a **board read**, which is why
`work_type()` does not and cannot answer it.

### The ONE test — does a durable breakdown already exist in the tree?

| Lane | What already holds the breakdown | Subtasks? |
|---|---|---|
| **BMAD Story** (AVCH) | the story file's `Tasks / Subtasks` section **+** its `sprint-status.yaml` row | ⛔ **NEVER** |
| **Command-centre Task** (SCC) | `implementation_plan.md` in the tree, **attached to the ticket**, and the ticket's own `## Plan` checklist | ✅ **the only place it can live** |

This is the same question `work_type()` already asks (*is this BMAD sprint work?*), so it adds no new
axis. A story's breakdown is already written down and machine-joined (`jira_key:` frontmatter, a YAML
row key that never changes); mirroring it onto the board makes a **second copy that nothing syncs**, and
it drifts on the first edit of either side. A Task has no such file — it has a plan in `_artifacts/`,
which is the same thing one rung lower, and the ticket carries the OUTLINE of it, never the plan itself.
**The live boards already match this rule exactly: AVCH has zero subtasks, SCC has fourteen.**

### The threshold — its own branch AND its own worktree, or it is not a ticket

A piece earns a `Subtask` when it earns **its own `chore/<KEY>-<slug>` branch in its own worktree**.
One worktree = one branch = one key = one ticket = one gate run = one merge — the unit this whole system
is already keyed to: Atlassian's GitHub app joins commits **by branch name**, `task_preflight.py
--expect-key` binds branch↔ticket, and `post-commit-jira-start.sh` parses the key **out of the branch**.

**A ticket with no branch is a row nothing will ever write to** — no commits, no Dev Record, no
transitions. That is board noise, which is the thing this rule exists to prevent. Everything under the
threshold stays a checklist line in the parent's `ACCEPTANCE` block or in `implementation_plan.md`.
**Three edits in one commit are not three subtasks.**

### Minting them — propose, then stop

Subtasks are minted **exactly like the Tasks they hang under: by hand, with raw `acli`.** There is no
`jira_feed.py` seam and deliberately so — `mint` exists to render a description *from a story file*, and
a subtask has none.

```bash
acli jira workitem create --project SCC --type Subtask --parent <PARENT-TASK-KEY> \
  --summary "…" --description-file <(python3 .agents/scripts/jira_ticket.py outline <rider>.md)
```

⛔ **`--description-file`, never `--description`** — the shape below is ADF, and a `--description`
string cannot carry a checklist. Write each rider's outline beside the plan
(`_artifacts/_main/<folder>/tickets/<KEY>.md`), render it, and mint from that.

⛔ **The agent PROPOSES the set and writes nothing until the operator says go**, and it proposes only
**after the `implementation_plan.md` is approved.** Minting off a first read of the ticket is
speculative work (guardrail 3), and placement stays the operator's (guardrail 2). Print one line per
subtask naming the branch each will get, then stop.

### The description is the FAST READ — the plan lives in the tree

⛔ **A ticket description is not the place for an implementation plan**, and putting one there fails
three ways at once: it hits Jira's size limit, it goes stale the moment the plan is edited in the tree,
and **nobody reads it.** The operator's ruling (2026-08-22): *"those need to be fast reads in the
description of what the plan is, not the plan. The plan should always be in the artifacts and attached
to the ticket."*

So: **the tree is the spec, the description is the outline, and the plan is an ATTACHMENT.**

| Section | What goes in it |
|---|---|
| `Why:` | ONE paragraph, before any heading. The **problem**, not the solution. |
| `## Plan` | a checklist, **4–8 lines**. Renders as real Jira checkboxes. One line per thing that will be observably done — a file, a script, a gate. |
| `## Done` | empty at mint (`(filled at close-out)`); filled from the walkthrough when the lane closes. |
| `## Files` | the plan's repo path + its GitHub `blob/` link. The plan file itself is attached. |

The outline lives beside the plan as `_artifacts/_main/<folder>/tickets/<KEY>.md` — in the tree, in the
lane's diff, reviewable — and `.agents/scripts/jira_ticket.py` is what renders and writes it:

```bash
jira_ticket.py outline  tickets/SCC-291.md                        # the dry run; no network
jira_ticket.py describe --key SCC-291 --outline tickets/SCC-291.md
jira_ticket.py attach   --key SCC-291 --file <plan>.md            # REST; acli CANNOT attach
jira_ticket.py done     --key SCC-291 --outline tickets/SCC-291.md \
                        --tick 1,3 --done-line "what shipped"      # at close-out
```

⚠ **`attach` needs an Atlassian API token and nothing else does.** `acli jira workitem attachment` has
`list` and `delete` and no `add`, and acli's own stored credential is a wrapped copy that 401s against
REST. Resolution is `$JIRA_API_TOKEN` → OS store item `sudo-jira` → **exit 5 printing the one-time
setup**. Until that is done `describe` and `done` still work, so the fast-read shape lands either way.
Setup: `docs/migrations/install_guides/jira-api-token-setup.md`.

⛔ **`done` rewrites the OUTLINE FILE and re-renders from it** — it never edits the description in
place. The tree stays the source; a ticket edited directly disagrees with the tree the first time
either is touched, and only one of them is under version control.

### Lifecycle

| Moment | What happens |
|---|---|
| first commit on `chore/<SUBTASK-KEY>-<slug>` | `post-commit` → `jira_feed.py start` moves **the subtask** to `In Progress`. **The child only** — there is no cascade, so `start` keeps one board write and one verdict |
| subtask close-out | `/smh-close-task-merge-tree`, unchanged — it lands its own branch and goes `Done` on its own. **Rider path (SCC-170 — the default when able):** worked in the parent's consolidated lane → no branch, no own close-out; the parent lane's `task.yaml` declares it under `riders:` and the parent's ceremony transitions it to `Done` first. The agent picks the mode and records why (`work-consolidation.md` rule 2) |
| **found broken** | ⭐ **flag the PARENT, never the subtask.** A subtask is **never** labelled `Bug`; breakage is recorded on the ticket that owns the job. `jira_feed.py flag` refuses a subtask and names its parent in the refusal |
| **parent close-out** | ⛔ **refused while any child is not `Done` or `Deferred`** (`task_preflight.py`). The parent closes **LAST** — that is the moment the whole job is done. A declared **rider** does not refuse: the preflight WARNS with the exact transition the ceremony will run, and the close-out flips riders first, parent last. ⭐ **Partial landing (SCC-170):** a consolidated lane that must ship early writes `landing_mode: partial` and trims `riders:` to the subset actually on the branch — the trimmed riders flip, the **parent stays open**, and the rest becomes the next lane. `task_preflight.py` refuses a declared rider that is named in no commit subject on the lane |

**`Deferred` is the escape hatch, and it is not a `--force` flag.** A child that is genuinely out of
scope gets descoped properly (`Deferred` + the `descoped` label) and stops blocking. A gate with no
legitimate exit gets `--no-verify`'d into oblivion; fixing the board leaves a trail, a bypass flag does
not.

**A parent that lags its children is reported by `jira_feed.py audit`, not fixed by a write verb.**
`audit` also reports a subtask with **no parent**, one parented **straight to an `Epic`**, and one
**nested under another subtask** — none of which it will auto-fix, because re-parenting is a board move
and *which* parent is a judgment about the work.

⚠️ **Two `acli` facts that will bite anyone extending this** (both measured against the live board,
2026-08-12): `parent` is **rejected** as a `--fields` value on `workitem search` (exit **1**) but
accepted on `workitem view`, where it returns the parent's own `issuetype` and `status` too — so one
`view` answers every placement question. And `parent = <KEY>` **is** valid JQL. Beware the trap that
joins those: a bad key and a genuinely childless parent **both return zero rows**, and only the exit
code tells them apart. Never read row count alone.

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

> ⭐ **Who writes, and when — the universal law (operator ruling 2026-08-14; every lane, every
> project).** The operator acts in **WORDS** — `approved`, "its done", or invoking a command — and
> the **agent performs every board write**, always inside the ceremony those words triggered, never
> on its own judgment. A flow that leaves the operator a manual Jira edit is **broken by
> definition**: stop and say the flow is broken, never hand the edit back. Status-as-gate gates the
> AGENT, not the operator. And read every status rule as **WHEN** (inside which ceremony the write
> happens), never **WHO** (human vs agent) — the WHO-misreading is how a ban on agent
> self-certification once became operator data entry (SCC-156: an agent refused to flip a finished
> rider subtask and assigned the operator the edit).

```bash
acli jira workitem comment create --key SCC-14 --body "…"        # TRAP: needs --key
acli jira workitem transition --key SCC-14 --status "In Review" --yes  # TRAP: needs --key; --yes skips the interactive confirm
acli jira workitem create --project SCC --type Task --summary "…" --description "…"
#   children of an epic: add --parent <EPIC-KEY>; --type Epic works too; --label "a,b" at create
#   ALWAYS create bare (no --assignee) — default-assignee is why everything once showed "assigned to Daniel"
acli jira workitem edit --key SCC-14 --labels "quick-dev,parallel-ok"   # REPLACES the label set
acli jira workitem link create --out SCC-10 --in SCC-14 --type Blocks   # reads: SCC-10 blocks SCC-14
```

> ⛔ **`--yes` is not decoration, and dropping it is silent.** Written without it —
> `acli jira workitem transition --key SCC-14 --status "Done"` — acli stops on an interactive
> confirm, which an agent's non-interactive shell can never answer. Three shipped call sites
> omitted it (`/cicd-push-e2e`, `/smh-close-task-merge-tree`, `/smh-merge-multiple-workingtrees`);
> `Done` was landing on luck until SCC-113. `tests/test_jira_feed.py` now fails if any
> `workitem transition` under `.agents/` is missing it — anchored to the **command span** on the
> matched line, so neither this paragraph nor a trailing `# …--yes…` comment reads as coverage for a
> real call site. **Scope is `.agents/` only:** `docs/_scc_sops_prds/jira_manual.md` still shows the
> un-flagged form, deliberately — it is the *by hand at a terminal* row, where a human can answer
> the prompt.

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
python3 .agents/scripts/jira_feed.py start     --key SCC-113 --apply
python3 .agents/scripts/jira_feed.py finish    --key SCC-155 --walkthrough <path> --apply
```

- **`mint`** (① Step 1.6) dedupes on the BMAD number, renders the **description from the story file**
  (statement + ACs + lane rulings + file path), creates it bare and parented, then re-reads the ticket
  and exits 2 if the description did not land. Prints `JIRA_KEY=<KEY>`.
- **`devrecord`** (close-out Step 4, `/cicd-quick-dev` Step 3.5) files THE Dev Record — decisions,
  pitfalls, follow-ons, outcome, evidence. **Exactly one per ticket:** an existing record is updated in
  place, never stacked, so the branch-closer and the story-closer cannot leave two partial records.
- **`check`** answers "does this ticket carry both halves?" — exit 2 if not.
- **⭐ `finish`** (SCC-155) writes the close-out's `Done` — **unless** the lane's walkthrough still
  owes the operator something. It reads the unchecked `- [ ]` items under `## Your Actions` and
  either closes (exit 0), or **HOLDS** (exit 3): posts them as a "User tasks" comment, adds the
  `user-tasks` label, and walks the `Awaiting Review` → `In Review` ladder, falling through
  silently on a board that carries neither (SCC does not, today — the label is the signal until a
  column is installed, which is a Jira-UI change and zero code). **It fails CLOSED**: a missing
  walkthrough or a missing `## Your Actions` section is a refusal (exit 2), never a clean close —
  an absent section is not evidence that nothing is owed. Exit 4 is transport, as with `start`.
  The auditable exit is the checkbox: tick the item to `- [x]`, commit, re-run. No force flag.
- **`trace`** (SCC-54) reads git history — `blame` on a `file:LINE`, `git log --no-merges` on the
  file — and ranks the tickets whose commits touched it, blame first. **No network, no board write**,
  and it only ever proposes keys from the project(s) in this repo's `.agents/jira.conf`.
- **`flag`** (SCC-54) is the raise half of the `Bug` rule, above. Needs `--reason`; reads the type
  and the status back after writing them. It refuses an `Epic` (a container is never broken work)
  **and a `Subtask`** — the latter for a different reason, so the two refusals say different things:
  a subtask is a **leaf**, and the ruling is that breakage is recorded on the ticket that owns the
  job, so the refusal **names the parent to flag instead** (SCC-119).
- **`start`** (SCC-113) is the seam that did not exist: work has begun, so the ticket reads
  `In Progress`. **Idempotent** — already there is a no-op, so the `post-commit` recorder firing on
  every commit and two lanes holding one key cannot fight over the board. It moves **only out of
  `To Do` / `To Do Next`**, the same narrowness as `flag`'s "only out of `Done`": `Blocking` is an
  impediment, `In Review` is blocked on the operator (something the agent cannot do — see the
  status table), `Deferred` is descoped, and starting any of them erases the only signal it
  carries. A **`Done`** ticket is **refused** — guardrail 1 in
  reverse, because a ticket you are starting cannot already be finished. An **`Epic` is allowed**
  here and refused by `flag`; that difference is deliberate (an epic under development is genuinely
  in progress; an epic is never itself broken work).
  **A `Subtask` is ACCEPTED** (SCC-119) — it used to be refused here, and that refusal was a live
  defect rather than a guard: a subtask carries its own branch, so `start` exited 2 on a real lane,
  the `post-commit` marker (written only on exit 0) never landed, and the recorder re-hit the board
  on **every commit** while the ticket sat in `To Do` for the whole build. SCC-123 shipped that way.
  **Four exit codes, because the caller must tell them apart:** `0` moved or already there
  (settled) · **`3` left alone — NOT settled, ask again** · `2` the board REFUSED it (a `Done` key,
  a move that did not land) · **`4` the board was UNREACHABLE** — transport, not a
  verdict, so retry rather than concluding anything about the key. Collapsing `4` into `2` told an
  agent on a dead uplink to mint a duplicate ticket.
  The `post-commit` recorder writes its once-per-branch marker **only on `0`**; collapsing `3` into
  `0` silenced a lane whose ticket was `Blocking` when it opened and returned to `To Do` an hour
  later — the very failure this seam exists to prevent.

Two rules that bind on YOU, not the script: **nothing is invented** (a missing story section renders
`(none found ...)` and warns — do not paper over it), and **the buckets are yours to fill.** The
walkthrough scrape underneath is a safety net, not the source: close-out has just finished routing the
session's learnings, so pass them with `--decision` / `--pitfall` / `--followon`. A record that says
`(none recorded)` on a story that fought back means the routing was thin, not that nothing happened.

## Who mints tickets — two wired seams

Agents MAY mint (operator ruling 2026-08-07): every ticket carries its provenance — the BMAD number
in the summary, the board row / spec pointer in the description — so nothing lands untraceable.

- **Epics** → `/cicd-create-epic-sprint` **Step 1a**, at kickoff (the operator is in the room) — and
  the look-before-you-mint search is part of that step, not a separate one.
- **Stories** → `/cicd-write-story-tests` ① Step 1.6, at pickup: child of the epic ticket, bare,
  labels from ①'s lane/parallel/blocked ruling, `jira_key:` stamped into the story frontmatter.
- **Toolkit/chore work** → mint the repo's chore ticket before cutting `chore/<KEY>-<slug>`.
- ⭐ **Subtasks** → `/smh-quick-dev`, **after** the plan is approved: the agent proposes the set and
  **stops**; the operator's go is what writes it. Raw `acli`, parented to the Task. See §Subtasks.

Outside these seams: status + comments only. Never mint speculative work — a ticket asserts a
decision already made. There is no "maybe" bucket anywhere: a finding is fixed in its lane,
dismissed with a reason, or deferred against a NAMED structural blocker in the deferred ledger —
and the operator purges unrecognized tickets on sight.

⭐ **Review findings are the canonical speculative case — and a review never produces a ticket**
(operator rulings 2026-08-15, both). The review's own triage decides which findings are actually
relevant to implement (`code-review-engine` step-03, the relevance gate) and most little ones die
there with a one-line reason — the hunters have finding-goals, so their volume is a success
metric, never a work queue. **Every survivor is fixed in the same lane, in the same thread,
before the verdict.** The only other disposition is a `defer` naming one structural blocker
(another live lane owns the file · another repo · an open decision) in the deferred ledger —
never a ticket. Banned in every form: a residue ticket carrying the unfixed pile, a "proposed"
or "decided" ticket the operator is asked to rule on, and a walkthrough action row assigning
either to the operator. The first cut of this rule allowed the "proposed decided ticket" leg;
the operator ruled it the same loop under a new name ("we need the fixes made in thread not a
ticket made every story thats an endless loop that never finishes").

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
   **And it must be an OPEN ticket.** Borrowing a `Done` ticket's key because the new work is
   adjacent — same files, a follow-on, *"no Jira state will be changed anyway"* — is the same defect
   wearing a reason. Two mechanisms make that promise false:
   - Atlassian's GitHub app links every commit on a `<prefix>/<KEY>-<slug>` branch (§The ticket ↔ file
     join). A closed ticket silently accumulates branches and commits dated after its close.
   - `jira_feed.py devrecord` keeps **exactly one** Dev Record per ticket and updates it **in place**.
     A close-out under a borrowed key **overwrites the record of the work that earned the ticket.**

   The armed commit-msg hook checks the *project* prefix, never the *status* — **it will not catch
   this.** One read is the whole guard, and it costs nothing:
   ```bash
   acli jira workitem view <KEY> --fields "status"     # Done? then it is not your key
   ```
   Can't mint? That is the sandbox trap at the top of this file, not a licence to reuse — re-run
   unsandboxed, then mint at the §Who mints tickets seam. Minting is one command and always available.
2. **Placement stays the operator's.** Machinery mints at the two seams, moves status, and posts
   evidence — sprint/backlog placement, priorities, and board layout are human decisions.
3. **Bare-state board.** Only OPEN work gets tickets. Never resurrect finished epics as tickets —
   done work is file history (`sprint-status.yaml`, `epics.md`), not board rows.
4. **Don't double-move.** These transitions are already automated — **at both ends of the lifecycle
   since SCC-113**, which is the ticket that closed the start seam:

   | When | What moves it | To |
   |---|---|---|
   | **first commit on `chore/ · claude/ · epic/`** | **the `post-commit` recorder** → `jira_feed.py start` | **`In Progress`** |
   | worktree-open, Task lane | `/smh-quick-dev` Step 0.5 → `jira_feed.py start` | `In Progress` |
   | story pickup, ① | `/cicd-write-story-tests` Step 1.6.4 → `jira_feed.py start` | `In Progress` |
   | story close-out | `/cicd-close-story-merge-tree` Step 4 | `Done` |
   | task close-out | `/smh-close-task-merge-tree` Step 4 | `Done` |
   | epic merge | `/cicd-push-e2e` Step 6.5 | `Done` |
   | found broken | `jira_feed.py flag` | **out of** `Done` |
   | **close-out HELD by open operator actions** | `jira_feed.py finish` (both task close-outs) | **`Review Required`** → `Awaiting Review` → `In Review`, first one the board carries; **none installed → no move at all**, the `user-tasks` label carries the signal |

   The three `In Progress` writers are all the same idempotent verb, so they cannot fight: whichever
   fires first moves it, the rest are no-ops. Outside this table, transition a ticket only when the
   operator asks.
   **The labelling pass is not a writer** — `/cicd-label-tasks` and `/smh-label-tasks` write the
   `parallel-ok` / `quick-dev` **labels** and one comment on the parent, and deliberately transition
   nothing.
   **`jira_feed.py finish` is two rows, not one**, and the second is why it earned its own line
   above: on a clean walkthrough it writes the `Done` that the two task-close-out rows name, and on
   a held one it writes a **review status instead** and refuses `Done` outright. That review row was
   missing here while the code already wrote it — an undeclared writer against a table this
   guardrail calls closed (SCC-155). It never moves a ticket the operator has already parked on one
   of those rungs, and it never moves one backwards. Placement stays the operator's (guardrail 2);
   "these three are safe together" is not a reason to move a card.
5. **The token stays in the OS credential store.** Never echo, copy, or persist it anywhere — and
   never bake a binary path or a store name into a doc. Both are per-machine, this file is read on
   the Mac and the Windows PC, and a hardcoded Mac path is what teaches a PC agent it has no Jira.
