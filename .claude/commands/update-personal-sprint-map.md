---
description: Update personal sprint map — rebuilds the workspace's sprint-dependency-map.md as a clean ticket board (lanes, next command per story, VERIFIED parallel matrix, quick-dev candidates, operator queue, blockers) from sprint-status.yaml.
platforms: [opencode, antigravity, claude, codex]
---

# /update-personal-sprint-map — Sprint Ticket Board Manager

Rebuilds `_my_resources/_quick_reference/sprint-dependency-map.md` in the target workspace.

This document is a **ticket board, not a journal.** It answers one question — *what do I work on next,
and what command runs it* — and nothing else. Every run produces the **same section order, the same
tables, the same status vocabulary.** Uniformity is the point: the operator scans it, never reads it.

> Flow position: standalone maintenance. Run after any story changes state, after an epic kickoff,
> after a live-testing pass, or any time the board looks stale.

## Step 0 — Resolve target project

0. **Self** — if the working directory is inside a project under `Projects/` (or has no `Projects/`
   subfolder), `PROJECT_ROOT = .`.
1. **Inline** — if `$ARGUMENTS` names a folder under `Projects/`, `PROJECT_ROOT = Projects/<name>`.
2. **Pointer** — else read `.agents/active-project.txt`.
3. **Ask** — else ask the operator which project to update.

Echo `Target: <PROJECT_ROOT>`. Target doc: `{PROJECT_ROOT}/_my_resources/_quick_reference/sprint-dependency-map.md`
(create `_quick_reference/` if missing).

## Step 1 — Read state (YAML first, always)

1. `_bmad-output/implementation-artifacts/sprint-status.yaml` — **the master.** Dump `development_status`
   and enumerate **every epic key it contains.**
2. `_bmad/bmm/stories/` — which stories have files. Check **both `story-21.5-*.md` and `story-21-5-*.md`**;
   both naming forms are in use.
3. `_bmad-output/active-context/active-context.md` — owed live tests, deploys, blocking input.
4. `git log --oneline -20` + `git branch -a` + `git worktree list` — catch stories that moved without the
   YAML being flipped.
5. `_my_resources/Open_Tasks/*.md` — live bug/triage docs that own tickets the YAML does not track.
6. `_bmad-output/test-artifacts/test-design-epic-*.md` — the **risk P-level per story**. It drives two
   board decisions: quick-dev eligibility (Step 2) and how loudly a parallel verdict matters (Step 2.5).
7. For every live worktree: its story file's frontmatter (`blocked_by:`, `bdd_contract:`) and any
   `_artifacts/epic_*/story-*/implementation_plan.md` — a ② plan's "Modify [file]" lines are that lane's
   own declaration of its edit sites, and Step 2.5 consumes them.

⛔ **Never inherit the previous board's epic list.** Build the epic list fresh from the YAML every run.
A prior version of this board silently omitted a whole live epic and recommended a closed story and a
deferred epic for five days. Enumerating from the YAML is the only thing that prevents it.

## Step 2 — Lane + next-command mapping

Sort every open item into exactly one lane. **Every row carries its next command** — that is the point
of the board. If an item has no command, write `—` and say who owns it.

| YAML / observed state | Lane | Next command |
|---|---|---|
| `backlog`, no story file | Ready for dev | `/sudo-write-story-tests <id>` |
| `backlog`/`ready`, story file + reds exist | Ready for dev | `/sudo-dev-story-tests <id>` |
| `in-progress` (dev loop live) | In flight | `/sudo-dev-story-tests <id>` |
| `review` (code written) | In review | `/sudo-code-review <id>` |
| review PASS, not landed | In review | `/sudo-update-sprint-memory` |
| `done` but owes a live test / deploy / decision | Operator queue | `—` (operator) |
| Risk-scored **P2/P3** + small + contained (or an unscored follow-on that is) | **Ready for dev**, Lane = `quick-dev` | `/sudo-quick-dev <id-or-slug>` |
| Unblockable by dev (dependency, external, decision) | Blocked | `—` + explicit *Blocked by:* |
| `descoped` / `deferred` | **Epic status only** | 🛑 never a lane, never a recommendation |

**Hard rules**
- A `descoped` or `deferred` story is **never** in Ready, In flight, or Do next.
- A `done` story that still owes anything (deploy, backfill, live verify) **stays visible** in the
  Operator queue. Do not let `done` hide a live obligation.
- **Quick-dev is a P2/P3 lane.** A story risk-scored **P0 or P1** in the epic's test-design takes the
  full ①②③ loop, always — no matter how small the diff looks. Authz / PII / data-integrity surfaces
  are **never** quick-dev regardless of score. Unscored follow-ons qualify only when small, contained,
  and off those surfaces; `/sudo-quick-dev`'s EJECT tripwire is the backstop, not the gate.
- ⛔ **The board never says "parallel" outside the Parallel-lanes table, and ✅ only comes from
  Step 2.5.** No prose like "zero dependencies", no ‖ markers on unverified rows. On 2026-07-31 this
  board asserted "21.11 has zero dependencies on 21.8 — can run in parallel" for a story that had **no
  story file** — its ① then found both stories edit `check_cost_cap` at the same spot. Unknown
  surfaces = ⚠️ unverified = scheduled as serialized.
- ⛔ **A story with a LIVE WORKTREE is IN FLIGHT — the YAML does not get a vote.** Before writing any lane,
  run `git worktree list` and read the `Status:` line of each live tree's story file. **Those two win.**
  The YAML lags **by design**: neither `/sudo-dev-story-tests` (②) nor `/sudo-code-review` (③) ever writes
  `sprint-status.yaml` — only close-out does (`story-status-flip-contract`). So an actively-developed story
  reads `backlog` there for its entire life.
  **This is the single worst bug this board can have.** On 2026-07-27 it put 21.4 — story written, tests
  written, implementation done, sitting in code review — under *Ready for dev* with
  `/sudo-write-story-tests` as its next command, i.e. it instructed the reader to rebuild the story from
  scratch on top of another lane's live worktree. Map story-file `Status:` straight to the lane:
  `review` → **In flight**, next `/sudo-code-review <id>`. Never `①` on a story whose tree already exists.
- If the YAML and reality disagree **for anything other than a live worktree**, follow the YAML in the
  status column and **flag the drift inline** on that row. Never silently "correct" the YAML in the board.

## Step 2.5 — Verify every parallel claim (MANDATORY — parallelism is a verdict, not a vibe)

For every pair of lanes the board could offer together (each in-flight lane × each other in-flight or
ready lane in the active epic), derive a verdict **fresh this run**:

1. **Extract each story's touch-set** — the real source files it changes — from, in order of authority:
   - `git diff --name-only main_debug...<branch>` for a live branch (code already written wins);
   - the worktree's `implementation_plan.md` "Modify/Add [file]" lines (a ② plan is the lane's own
     declaration of its edit sites — this is what would have caught 21.8 → 21.11);
   - the story file's Dev Notes surfaces-map / Tasks paths.
   Board and planning artifacts (`_bmad-output/`, `_bmad/`, `_artifacts/`, `_my_resources/`) do not
   count as overlap — every lane touches those; only source paths decide.
2. **Check contract edges** — `blocked_by:` frontmatter, and grep each story file for the other's id.
   A story that imports a symbol the other story **creates** is 🔒 serialized even with zero file
   overlap today (the module will exist by the time both land — add/add on a new file has no merge base).
3. **Intersect and rule:**
   - Intersection empty AND no contract edge → ✅ **parallel** — evidence line: `no shared source
     files (checked <date>: <which inputs were read>)`.
   - Any shared file or contract edge → 🔒 **serialize** — name the shared file/function and which
     story goes first.
   - Either story has **no story file yet** → ⚠️ **unverified** — its surfaces are unknown until ①
     grounds them. ⚠️ schedules as 🔒. Never promote ⚠️ to ✅ by assumption; the fix is to run ①.
4. Verdicts are **point-in-time**: a new `implementation_plan.md` appearing in a lane's worktree can
   flip yesterday's ✅ to 🔒, which is why this step re-runs on every rebuild.

## Step 3 — Write the board (this skeleton, this order, every time)

Omit a section only when it is genuinely empty **except** Blocked and Operator queue — those always
render, showing `**None.**` when empty. That absence is information.

```markdown
---
title: Sprint Ticket Board
type: quick-reference
last_checked: YYYY-MM-DD
---

# Sprint Ticket Board — <PROJECT>

> **Reconciled YYYY-MM-DD** against `sprint-status.yaml`. **The YAML wins** any disagreement.
> Current state only — history lives in git.

## At a glance

| | |
|---|---|
| **Do next** | `<the one command>` |
| Active epic(s) | <Epic N — Title> |
| Ready for dev | <n> · In flight <n> · In review <n> |
| Blocked | <n or None> |
| Operator owed | <n> (<n> 🔴) |
| Deferred / terminal | <list or None> |

## ▶ Do next

**`<command>`** — <one line: why this one>.
Runnable beside it: only ✅ rows below — **`<command>`** (<story>) · or *none verified*.

## 🧵 Parallel lanes — verified this run, never assumed

| Pair | Verdict | Evidence / shared surface | Order |
|---|---|---|---|
| <A> ↔ <B> | ✅ parallel | no shared source files (checked YYYY-MM-DD: diffs + plans + story surfaces) | — |
| <A> ↔ <C> | 🔒 serialize | both edit `<file>` (`<function>`) | <C> waits for <A> |
| <A> ↔ <D> | ⚠️ unverified | <D> has no story file — surfaces unknown until ① | treat as 🔒 |

## 🔴 Blocked

| Story | Title | Blocked by | Clears when | Next command |
|---|---|---|---|---|
| **<id>** | <title> | <blocker> | <condition> | `<cmd>` or `—` |

## 🟢 Ready for dev

**Quick-dev tickets go HERE, in this table — they are dev work, so they belong with the dev work.** Use the
Lane column; the next command carries the difference (`/sudo-quick-dev <slug>` vs
`/sudo-write-story-tests <id>`). There is no separate quick-dev section — see the ⛔ note below.

| Story | Title | Lane | Story file | Depends on | Next command |
|---|---|---|---|---|---|
| **<id>** | <title> | full ①②③ | ✅ / ❌ spec in `epics.md` L<n> | — | `/sudo-write-story-tests <id>` |
| <ticket> | <title> | quick-dev | <spec / brief link> | — | `/sudo-quick-dev <slug>` |

## 🔵 In flight

| Story | Title | Stage | Where | Next command |
|---|---|---|---|---|
| **<id>** | <title> | ①/②/③ + verdict | branch / worktree | `<cmd>` |

## 🟣 In review — awaiting verification

| Story | Title | What's owed | Owner | Next command |
|---|---|---|---|---|
| **<id>** | <title> | <the one action> | operator / dev | `<cmd>` or `—` |

## 👤 Operator queue — not dev work

| # | Pri | Action | Closes |
|---|---|---|---|
| 1 | 🔴 | <imperative action> | <story / gate> |

## ⚡ Quick-dev recommendations

Two kinds of rows, one lane: (a) **backlog stories risk-scored P2/P3** in the epic's test-design —
candidates for the fast loop; (b) small unscored follow-ons / one-file debugs. **P0 and P1 stories are
NEVER here** — full ①②③ always; authz / PII / data-integrity never, regardless of score. The
`/sudo-quick-dev` EJECT tripwire returns anything that grows teeth to the full loop.

| Ticket | P | Brief / spec | Next command |
|---|---|---|---|
| **<story id>** <title> | P2 | spec in `epics.md` § <id> | `/sudo-quick-dev <id>` |
| <follow-on name> | — | [`<doc>`](<path>) | `/sudo-quick-dev <slug>` |

⚠️ **Staleness guard.** The old quick-dev section (deleted 2026-07-27) went stale because it was not
reconciled on each run. This command rebuilds the ENTIRE board every run — including this section.
If a ticket here is already `done`, **delete the row.** If a ticket here only owes a live test (no code),
it belongs in the Operator queue, not here.

## 📋 Pipeline — specced, not yet a story

| Ticket | Lane | Spec / brief | Next command |
|---|---|---|---|
| <name> | full ①②③ / quick-dev | [`<doc>`](<path>) | `<cmd>` |

## 🔒 Settled rulings — do not re-raise

| Ruling | Decided | Recorded in |
|---|---|---|
| <ruling in one affirmative line> | YYYY-MM-DD | <docstring / decision record> |

## 📊 Epic status

| Epic | Title | Status | Open | Note |
|---|---|---|---|---|
| <N> | <title> | `in-progress` | <n> | <one line or —> |

## ✅ Closed this cycle

- **<id>** <title> — <outcome in one line>

## Sources of truth

- [sprint-status.yaml](../../_bmad-output/implementation-artifacts/sprint-status.yaml) — **wins**
- [active-context.md](../../_bmad-output/active-context/active-context.md)
- [Open tasks](../Open_Tasks/)
```

## Step 4 — Style contract (what keeps it clean)

**Do**
- One line per cell. A cell that needs two sentences belongs in a linked doc — link it.
- Imperative, present tense: *"Deploy firestore.rules + run the backfill"*, not *"the rules deploy is owed"*.
- Priority chips only: 🔴 blocks launch/security · 🟡 needed soon · 🟢 whenever.
- Link every brief rather than restating it: `[`debug_7_24.md`](../Open_Tasks/debug_7_24.md) § Bug 6`.
- Keep the whole board **under ~250 lines**. Over that means detail belongs in a linked doc.

**Never**
- ⛔ Narrative or session history — no *"this landed after…"*, no *"what this changes"*, no dated
  play-by-play. Git holds history.
- ⛔ Struck-through rows, superseded tables, or "historical — do not read" blocks. **Delete them.**
- ⛔ Quoting conversations. A ruling is one affirmative line in Settled rulings; the verbatim quote
  lives in the decision record it links to.
- ⛔ Filing a settled decision under anything that reads like a gap, limitation, or open question —
  that framing is exactly what gets a closed story re-proposed. It goes in **Settled rulings**, stated
  affirmatively, and any dead story is called **terminal**.
- ⛔ Re-explaining a rule the board already states once.

**Collapsing finished work.** When an epic is fully `done` with nothing owed, collapse it to **one row**
in Epic status (`Status: done`, `Open: 0`) and drop its individual story rows. Do not delete the epic
outright — a vanished epic reads as an omission and gets re-investigated. If any of its stories still
owes something, that item moves to the Operator queue and stays visible.

## Step 5 — Check before writing

1. Every epic in the YAML appears exactly once in Epic status.
2. No `descoped` / `deferred` story appears in any work lane.
3. Every lane row has a next command or an explicit `—` with an owner.
4. Every `done`-but-owing item is in the Operator queue.
5. Every referenced path resolves.
6. Zero strikethrough, zero "historical" blocks, under ~250 lines.
7. **Every use of the word "parallel" on the board traces to a ✅ row in Parallel lanes**, and every
   ✅ row carries its evidence line. No ⚠️ pair is offered as runnable-beside anywhere.
8. **No P0/P1 story appears in quick-dev** — cross-check every ⚡ row against the test-design P-levels.

## Step 6 — Report

Print the board path, then: active epic(s) · counts per lane · the single recommended next command ·
parallel verdicts (`<n> ✅ · <n> 🔒 · <n> ⚠️`) with any 🔒 named · quick-dev candidates count ·
operator-owed count with 🔴 count · any drift found between the YAML and git · any epic collapsed.
