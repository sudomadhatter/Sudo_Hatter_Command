# /smh-adviser-board — Roster Reference (POINTER)

**This document is retired as a source. The roster now lives in the command's own folder**, where the
board actually reads it:

| What you want | Where it lives now |
| --- | --- |
| The house discipline — refuse the binary frame, the balcony, the 3A trap, the instrument bank | `.agents/commands/adviser-board/THIRD-SIDE.md` |
| Filter charters — blind spot owned, when to seat, **when NOT to seat**, pool | `.agents/commands/adviser-board/TEAMS.md` |
| The 43-mind roster index — one row each, with `Sees` and `Best against` | `.agents/commands/adviser-board/ROSTER.md` |
| A single mind's full signature | `.agents/commands/adviser-board/minds/<slug>.md` |
| The Operator Doctrine carried into every spawn | `.agents/commands/adviser-board/DOCTRINE.md` |
| The ~250-word statement contract | `.agents/commands/adviser-board/CARD.md` |
| The spawn templates — recon, the Round-0 menu, the R1–R4 rounds, call-outs — and §7, the inline protocol for surfaces that cannot spawn | `.agents/commands/adviser-board/SPAWNS.md` |
| The protocol itself | `.agents/commands/smh-adviser-board.md` |

## Why it moved (SCC-331, 2026-08-26)

The old command carried its whole roster inline — about 450 of its 690 lines — which meant every session
loaded 43 minds' worth of signature whether it seated them or not. The folder makes the load lazy: the
orchestrator reads only `ROSTER.md` (one line per mind) to cast, and **the filter's own subagent opens
its one mind's card**. Seat one mind, open one file.

**The filter rework (SCC-340, 2026-08-28)** made one filter = one mind = one subagent: the hidden
5-cycle caucus became four visible rounds (R1 READ / R2 ATTACK / R3 BALCONY / R4 SETTLE), the cast gate
ends in a Round-0 top-3 menu per seated filter, and the stage rooms lost their special status —
Execution Reality and Sales are ordinary filters on the same gate.

The cards also carry three sections this document never had, and they are what make the board work:

- **`Collides with`** — named minds and the axis of collision. This is what the orchestrator reads to
  rank the Round-0 top-3 menu, so the seated mind is a genuine position on the filter rather than a
  name off the pool.
- **`What they concede to`** — what actually changes this mind's position. Without it, the settle round
  is theatre: a mind either never moves or moves arbitrarily.
- **`Reaches for`** — that mind's own third-side instruments, in its own phrasing. The instrument travels
  with the mind, so the question bank is never a checklist anyone ticks.

## Making a roster change

Edit the files above directly — there is no longer a mirror to keep in sync.

- **Reword a mind** → edit `minds/<slug>.md`. If the change alters what they are best against, update
  their `ROSTER.md` row too. If it alters *when you would reach for them* or *who they collide with*,
  update their line in `ROSTER.md` § **Reach for them when** — that index is what the orchestrator
  actually casts on, and the collision names there are the only ones it can see (SCC-333).
- **Add a mind** → write `minds/<slug>.md` against the eight-section contract, add a `ROSTER.md` row,
  add a line under the right filter in § **Reach for them when** (a *situation*, plus their `Collides:`
  names), and add them to a pool in `TEAMS.md`. Name at least two existing minds in their `Collides
  with`, and add yourself to *their* cards where the collision is mutual — the situation index and the
  cards must agree, because the orchestrator reads the index and the filter's spawn reads the cards.
- **Add or retire a filter** → `TEAMS.md`, including its *when NOT to seat* clause, then re-home its
  minds in `ROSTER.md`.
- **Add an instrument** → `THIRD-SIDE.md`, and put it on the card of whoever reaches for it.

Then run `/smh-sync-agents` to regenerate the launcher doors, and stage
`docs/_scc_sops_prds/workflows_testing_SOP.md` if the change alters how the command is used —
`sop_currency.py` reads `.agents/commands/` recursively, persona cards included.

## The research this came from

The original 35-mind research (`Sudo Brainstorm Team.md`) and the implementation plan
(`smh-adviser-board-PLAN.md`) were retired to git history. Their content — anchors, moves, and the
Third-Side question bank — was carried into the persona cards and `THIRD-SIDE.md`, then extended: eight
minds were added for the Execution Reality room (Kelly Johnson, Ohno, Boyd, Eisenhower, Brunelleschi,
Deming, Hopper) and Sales (Hopkins), and every mind gained the three new sections above.

The 2026-08-26 rework plan, with its 23 numbered decisions, is at
`_my_resources/open_tasks/plan_adviser-board-rework.md`.
