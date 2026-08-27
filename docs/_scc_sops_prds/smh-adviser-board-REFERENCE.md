# /smh-adviser-board — Roster Reference (POINTER)

**This document is retired as a source. The roster now lives in the command's own folder**, where the
board actually reads it:

| What you want | Where it lives now |
|---|---|
| The house discipline — refuse the binary frame, the balcony, the 3A trap, the instrument bank | `.agents/commands/adviser-board/THIRD-SIDE.md` |
| Team charters — blind spot owned, when to seat, **when NOT to seat**, pool, default triad | `.agents/commands/adviser-board/TEAMS.md` |
| The 43-mind roster index — one row each, with `Sees` and `Best against` | `.agents/commands/adviser-board/ROSTER.md` |
| A single mind's full signature | `.agents/commands/adviser-board/minds/<slug>.md` |
| The Operator Doctrine carried into every spawn | `.agents/commands/adviser-board/DOCTRINE.md` |
| The ~250-word card contract | `.agents/commands/adviser-board/CARD.md` |
| The six spawn templates, and §7 — the inline protocol for surfaces that cannot spawn | `.agents/commands/adviser-board/SPAWNS.md` |
| The protocol itself | `.agents/commands/smh-adviser-board.md` |

## Why it moved (SCC-331, 2026-08-26)

The old command carried its whole roster inline — about 450 of its 690 lines — which meant every session
loaded 43 minds' worth of signature whether it seated them or not. The folder makes the load lazy: the
orchestrator reads only `ROSTER.md` (one line per mind) to cast, and **the team subagent opens its own
three persona cards**. Seat three minds, open three files.

The cards also carry three sections this document never had, and they are what make the board work:

- **`Collides with`** — named minds and the axis of collision. This is what the orchestrator reads to
  build a triad on two independent axes, so the third mind is a genuine third position rather than a
  tiebreaker sitting between the other two.
- **`What they concede to`** — what actually changes this mind's position. Without it, cycle 4 is
  theatre: a mind either never moves or moves arbitrarily.
- **`Reaches for`** — that mind's own third-side instruments, in its own phrasing. The instrument travels
  with the mind, so the question bank is never a checklist anyone ticks.

## Making a roster change

Edit the files above directly — there is no longer a mirror to keep in sync.

- **Reword a mind** → edit `minds/<slug>.md`. If the change alters what they are best against, update
  their `ROSTER.md` row too, since that is what the orchestrator casts and swaps on.
- **Add a mind** → write `minds/<slug>.md` against the eight-section contract, add a `ROSTER.md` row, and
  add them to a pool in `TEAMS.md`. Name at least two existing minds in their `Collides with`, and add
  yourself to *their* cards where the collision is mutual.
- **Add or retire a lens** → `TEAMS.md`, including its *when NOT to seat* clause, then re-home its minds
  in `ROSTER.md`.
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
