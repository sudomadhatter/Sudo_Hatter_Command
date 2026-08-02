---
description: Rebuild the workspace's sprint_scrum_board_map.md as an enterprise scrum board — Right-now brief, Parallel Approved Stories (verified set, grounded stories only), one work queue with a command per row, operator actions, reference tail. Replaces /update-personal-sprint-map.
platforms: [opencode, antigravity, claude, codex]
---

# /sudo-update-scrum-board — Scrum Board Manager

Rebuilds `_my_resources/_quick_reference/sprint_scrum_board_map.md` in the target workspace.

The board is an **efficiency tool, not a document.** The operator runs **2–4 teams at once** and scans
it top-down: *what's the goal → what runs next → what's approved to run in parallel → what's waiting on me.*
Every run produces the **same five zones in the same order**, hard-capped at **~150 lines**. Detail that
doesn't fit belongs in a linked doc — never in a sixth section.

> Flow position: standalone maintenance. Run after any story changes state, after an epic kickoff,
> after a live-testing pass, or any time the board looks stale.

## Step 0 — Resolve target project

0. **Self** — if the working directory is inside a project under `Projects/` (or has no `Projects/`
   subfolder), `PROJECT_ROOT = .`.
1. **Inline** — if `$ARGUMENTS` names a folder under `Projects/`, `PROJECT_ROOT = Projects/<name>`.
2. **Pointer** — else read `.agents/active-project.txt`.
3. **Ask** — else ask the operator which project to update.

Echo `Target: <PROJECT_ROOT>`. Target doc:
`{PROJECT_ROOT}/_my_resources/_quick_reference/sprint_scrum_board_map.md` (create `_quick_reference/`
if missing). If the legacy `sprint-dependency-map.md` still exists there, `git mv` it to the new name
first, then rebuild.

## Step 1 — Read state (YAML first, always)

1. `_bmad-output/implementation-artifacts/sprint-status.yaml` — **the master.** Dump `development_status`
   and enumerate **every epic key it contains.**
2. `_bmad/bmm/stories/` — which stories have files. Check **both `story-21.5-*.md` and `story-21-5-*.md`**;
   both naming forms are in use.
3. `_bmad-output/active-context/active-context.md` — owed live tests, deploys, blocking input.
4. `git log --oneline -20` + `git branch -a` + `git worktree list` — catch stories that moved without the
   YAML being flipped.
5. `_my_resources/Open_Tasks/*.md` — live bug/triage docs that own tickets the YAML does not track.
6. `_bmad-output/test-artifacts/test-design-epic-*.md` — the **risk P-level per story**. It drives
   quick-dev eligibility (Step 2) and lane risk (Step 2.5).
7. For every live worktree: its story file's frontmatter (`blocked_by:`, `bdd_contract:`) and any
   `_artifacts/epic_*/story-*/implementation_plan.md` — a ② plan's "Modify [file]" lines are that lane's
   own declaration of its edit sites, and Step 2.5 consumes them.

⛔ **Never inherit the previous board's epic list.** Build the epic list fresh from the YAML every run.
A prior board silently omitted a whole live epic and recommended a closed story and a deferred epic for
five days. Enumerating from the YAML is the only thing that prevents it.

## Step 2 — Classify every open item into exactly ONE zone

| Observed state | Zone / row | Command |
|---|---|---|
| **Live worktree exists** (any YAML state) | 🎯 In-flight line + a context line in 🧵 | story `Status: review` → `/sudo-code-review <id>` · else `/sudo-dev-story-tests <id>` |
| `backlog`, no story file | 🛠 queue · 🟢 ready | `/sudo-write-story-tests <id>` |
| `backlog`/`ready`, story file + reds exist | 🛠 queue · 🟢 ready | `/sudo-dev-story-tests <id>` |
| `review`, code written, review not yet run | 🛠 queue · 🟢 ready | `/sudo-code-review <id>` |
| Review PASS, not landed | 🛠 queue · 🟢 ready | `/sudo-update-sprint-memory` |
| Risk-scored **P2/P3** + small + contained (or an unscored follow-on that is) | 🛠 queue · 🟢 ready · Lane = quick-dev | `/sudo-quick-dev <slug>` |
| Unstartable by an agent (dependency, external, decision) | 🛠 queue · 🔴 blocked | `—` + *Blocked by* + owner + clears-when |
| Specced follow-on, not yet a story/ticket | 🛠 queue · 📋 pipeline | its future command |
| `done`/`review` but owes a LIVE action only the operator can perform | 👤 Your actions | `—` (operator) |
| `descoped` / `deferred` | 📚 Reference only | 🛑 never a queue row, never a recommendation |

**Hard rules** (each one paid for by an incident)

- ⛔ **A story with a LIVE WORKTREE is in flight — the YAML does not get a vote.** The YAML lags by
  design: ② and ③ never write it; only close-out does. On 2026-07-27 the board put a story that was
  sitting in code review under *Ready for dev* with `/sudo-write-story-tests` as its next command —
  i.e. it instructed the reader to rebuild the story on top of another lane's live worktree. Map the
  story file's `Status:` straight to the row; never ① a story whose tree already exists.
- ⛔ A `descoped` or `deferred` item is **never** in the queue and never recommended.
- **Quick-dev is a P2/P3 lane.** P0/P1 always takes the full ①②③ loop, no matter how small the diff
  looks. Authz / PII / data-integrity surfaces are **never** quick-dev regardless of score. The
  `/sudo-quick-dev` EJECT tripwire is the backstop, not the gate.
- A `done` story that still owes anything (deploy, backfill, live verify) **stays visible** in
  👤 Your actions. `done` never hides a live obligation.
- If the YAML and reality disagree for anything other than a live worktree, follow the YAML in the
  State column and **flag the drift inline** on that row. Never silently "correct" the YAML here.

## Step 2.5 — Parallel Approved Stories (the set is the verdict)

**Grounding gate.** A parallel verdict needs both sides' **touch-sets** — the source files each will
edit — and those exist only once a story is *grounded*: a live branch diff, an `implementation_plan.md`,
or a written story file with Dev Notes surfaces. **Ungrounded tickets are never approved.** The board's
answer for them is "write the story first", never a guess. (2026-07-31: the board asserted a story with
**no story file** was parallel-safe; its ① then found both stories editing `check_cost_cap` at the same
line.)

**The operator's lever: to develop an epic in parallel, write its stories first.** Grounded stories
unlock approval; nothing else does.

**Display rule — show the ANSWER, never the math.** The board never prints pairwise notation
("✅ vs C+D"), lane letters, or cross-references the reader must join. It prints one **approved list**
— membership means *safe beside every other approved row* — followed by a verdict table in which every
parallel-relevant ticket carries exactly **one** verdict:

| Verdict | Meaning |
|---|---|
| 🟢 approved | in the approved set — safe to run beside every other 🟢 |
| 🔒 after `<ticket>` | shares (or may share) files with that specific ticket — run after it lands |
| ⏳ waiting on `<story>` | an in-flight story's surfaces are unknown; clears the moment its ① plan lands |
| 📝 no story | ungrounded — `/sudo-write-story-tests <id>` unlocks it |

⛔ "Not yet checked" is not a verdict. Do the check this run or issue 🔒 with the suspected surface —
no ticket is ever left un-verdicted.

**Compute the approved set:**
1. **Candidates** = every in-flight story + every 🟢 ready row that is grounded.
2. **Touch-sets**, in order of authority: `git diff --name-only main_debug...<branch>` (code written
   wins) → the worktree's `implementation_plan.md` "Modify/Add [file]" lines → the story file's
   Dev Notes surfaces / task paths. Planning artifacts (`_bmad-output/`, `_bmad/`, `_artifacts/`,
   `_my_resources/`) never count as overlap — only source paths decide.
3. **Contract edges:** `blocked_by:` frontmatter; a story that imports a symbol the other story
   **creates** is 🔒 even with zero file overlap today (add/add on a new file has no merge base).
4. **Approved set** = the largest candidate set in which **every pair** is disjoint. Verify the pairs
   fresh each run; stamp the whole set once: `verified <date>: <which inputs were read>`.
5. An in-flight story whose surfaces are **unknown** (no plan landed yet) cannot approve anything that
   plausibly shares its ground — those tickets get ⏳ against it, upgraded the moment its plan lands.
   The in-flight story itself appears as a context line above the table, not as a verdict row.
6. Verdicts are **point-in-time** — a new plan appearing can flip yesterday's 🟢, which is why this
   step re-runs on every rebuild. Runtime caveat: full test suites contend across parallel work even
   with disjoint files — stagger suite runs.

## Step 3 — Write the board (this skeleton, this order, every time)

Blocked rows and 👤 Your actions always render (`**None.**` when empty — that absence is information).

```markdown
---
title: Sprint Scrum Board
type: quick-reference
last_checked: YYYY-MM-DD
---

# Sprint Scrum Board — <PROJECT>

> Reconciled YYYY-MM-DD against `sprint-status.yaml` — **the YAML wins** any disagreement.
> Current state only; history lives in git.

## 🎯 Right now

**Goal:** <one sentence — the sprint objective and why it matters>
**Do next:** `<command>` — <why, half a line>
**In flight:** <id — where / whose team> · or None
**Parallel approved:** <n> stories — run any of them together (🧵)
**Waiting on you:** <n> 🔴 — <the biggest one and what it closes> (full list 👤)
**Recently landed:** <one line>

## 🧵 Parallel Approved Stories — verified this run

**✅ Approved — run any of these at the same time** (verified YYYY-MM-DD: <inputs read>):
1. `<command>`
2. `<command>`

<in-flight context line, e.g. "<id> (other team) keeps running in its own worktree beside these.">

| Ticket | Verdict | Why |
|---|---|---|
| <id/slug> | 🟢 approved | <its only surface, one phrase> |
| <id/slug> | 🔒 after `<ticket>` | <the shared / unpinned surface> |
| <id/slug> | ⏳ waiting on `<story>` | <what clears it> |
| <pipeline ids> | 📝 no story | `/sudo-write-story-tests <id>` unlocks |

Every 🟢 is safe beside every other 🟢. **Parallel epic development = write its stories first.**

## 🛠 Work queue

| Ticket | Lane | State | Blocker / needs | Command |
|---|---|---|---|---|
| **<id>** | full ①②③ | 🟢 ready | — | `<cmd>` |
| <slug> | quick-dev | 🟢 ready | — | `/sudo-quick-dev <slug>` |
| <id> | full ①②③ | 🔴 blocked | <by what — clears when> (<owner>) | `—` |
| <name> | quick-dev | 📋 pipeline | spec: [`<doc>`](<path>) | `/sudo-quick-dev <slug>` |

## 👤 Your actions — agents can't do these

| # | Pri | Action | Closes |
|---|---|---|---|
| 1 | 🔴 | <imperative — staple any flip-condition to the action that triggers it> | <story / gate> |

## 📚 Reference

### Epic status

| Epic | Title | Status | Open | Note |
|---|---|---|---|---|
| <N> | <title> | `in-progress` | <n> | <one line> |
| <N> | <title> | `deferred` | — | <why parked, one line> |

✅ Done, nothing owed: <every done epic by number/name> (<n> epics)

### 🔒 Settled rulings — do not re-raise

| Ruling | Decided | Recorded in |
|---|---|---|
| <one affirmative line> | YYYY-MM-DD | <docstring / decision record> |

### Sources of truth

- [sprint-status.yaml](../../_bmad-output/implementation-artifacts/sprint-status.yaml) — **wins**
- [active-context.md](../../_bmad-output/active-context/active-context.md)
- [epics.md](../../_bmad-output/planning-artifacts/epics.md)
- [Open tasks](../Open_Tasks/)
```

## Step 4 — Style contract (what keeps it scannable)

**Do**
- One line per cell. A cell that needs two sentences belongs in a linked doc — link it.
- Imperative, present tense: *"Deploy firestore.rules + run the backfill"*.
- Priority chips only: 🔴 blocks launch/security · 🟡 needed soon · 🟢 whenever.
- Link every brief rather than restating it.
- **≤~150 lines total.** 🎯 Right now is **≤8 lines** and contains **no unique data** — every line is a
  pointer into a zone below, so it can never drift independently.

**Never**
- ⛔ Narrative or session history — git holds history.
- ⛔ Struck-through rows, superseded tables, or "historical" blocks. **Delete them.**
- ⛔ Quoting conversations. A ruling is one affirmative line in Settled rulings; the verbatim quote
  lives in the decision record it links to.
- ⛔ Filing a settled decision under anything that reads like a gap, limitation, or open question —
  that framing gets closed work re-proposed. Settled rulings, stated affirmatively; dead stories are
  **terminal**.
- ⛔ The words "parallel" / "beside" / "safe together" anywhere outside 🧵 Parallel Approved Stories
  (the 🎯 count line excepted — it only points at 🧵).
- ⛔ Pairwise notation, lane letters, or any verdict the reader must assemble by joining rows — the
  approved list and the one-verdict-per-ticket table are the only parallel displays.
- ⛔ Re-explaining a rule the board already states once.

**Collapsing finished work.** Fully-`done` epics with nothing owed collapse into the one ✅ line in
Epic status, **named explicitly** — a vanished epic reads as an omission and gets re-investigated.
Anything a done epic still owes lives in 👤 Your actions.

## Step 5 — Check before writing

1. Every epic in the YAML appears exactly once — as a table row or **by name** in the ✅ done line.
2. No `descoped` / `deferred` item anywhere in the queue or lanes.
3. Every 🟢 row has a command; every 🔴 row names its blocker, owner, and clears-when.
4. Every done-but-owing item is in 👤 Your actions.
5. Every 🟢 in the approved set traces to a fresh pairwise check under one dated stamp; every
   parallel-relevant ticket carries exactly one verdict (🟢 / 🔒 / ⏳ / 📝 — never "unchecked");
   nothing ungrounded is 🟢; parallel vocabulary appears nowhere else on the board.
6. 🎯 Right now is ≤8 lines and holds no data absent from the zones below.
7. Every referenced path resolves; zero strikethrough; ≤~150 lines.
8. No P0/P1 story in quick-dev — cross-check every quick-dev row against the test-design P-levels.

## Step 6 — Report

Print the board path, then: goal line · do-next command · approved-set size (`<n> approved, verified
<date>`) with any 🔒/⏳ named · queue counts (🟢 / 🔴 / 📋) · operator-owed count with 🔴 count · any
drift flagged between the YAML and git · any epic newly collapsed into the ✅ done line.
