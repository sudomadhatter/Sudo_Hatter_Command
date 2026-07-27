---
description: Update personal sprint map — rebuilds the workspace's sprint-dependency-map.md as a clean ticket board (lanes, next command per story, operator queue, blockers) from sprint-status.yaml.
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
| Small, contained, **not** a P0 surface | Quick-dev queue | `/sudo-quick-dev <slug>` |
| Unblockable by dev (dependency, external, decision) | Blocked | `—` + explicit *Blocked by:* |
| `descoped` / `deferred` | **Epic status only** | 🛑 never a lane, never a recommendation |

**Hard rules**
- A `descoped` or `deferred` story is **never** in Ready, In flight, or Do next.
- A `done` story that still owes anything (deploy, backfill, live verify) **stays visible** in the
  Operator queue. Do not let `done` hide a live obligation.
- Authz / PII / P0 surfaces are **never** quick-dev — route them to `/sudo-write-story-tests`.
- If the YAML and reality disagree, follow the YAML in the status column and **flag the drift inline**
  on that row. Never silently "correct" the YAML in the board.

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
Parallel-safe beside it: **`<command>`** (<lane>) · **`<command>`** (<lane>).

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

⛔ **NEVER emit a "Quick-dev queue" section.** It existed until 2026-07-27 and was deleted because a
separate section for actionable dev work is a trap in two directions: it splits the "what do I work on
next" answer across two tables, and — being off to the side — nobody reconciles it, so it goes stale while
still reading as authoritative. Its two surviving rows were BOTH wrong: one recommended `/sudo-quick-dev`
on a story that was already `done` and only owed a manual live pass (operator-queue work), the other stayed
listed after its fix had shipped. **Quick-dev tickets are dev work → the Ready-for-dev table.** If a ticket
is not dev work, it belongs in the Operator queue or the Pipeline, never in a lane of its own.

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

## Step 6 — Report

Print the board path, then: active epic(s) · counts per lane · the single recommended next command ·
operator-owed count with 🔴 count · any drift found between the YAML and git · any epic collapsed.
