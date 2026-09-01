# Walkthrough — SCC-331: rework `/smh-adviser-board` into an orchestrator-cast board

**Ticket:** SCC-331 · **Date:** 2026-08-26 · **Lane:** `chore/SCC-331-adviser-board-rework`
**Workspace:** `_main` (lobby) · **Lane class:** `LOCAL` · **Landed:** PR #93, merge sha `548e9b31`

---

## What shipped

The command went from **690 lines to 274**, and the thing it used to hard-code — who sits on the
board — moved out into a lazily-loaded folder of **43 persona cards** across **7 pools**.

| Before | After |
|---|---|
| All five teams convened every round, 500–2,000 words each | An orchestrator casts **3–5 load-bearing lenses**, 3 minds each |
| No orchestrator; every lens spoke whether or not it was relevant | Casting is a decision, and it is made per question |
| Spawn template **forbade tools** — the board had never read the project it advised on | Recon agents ground the board in the named project first |
| Straight to debate | A cheap **Read round proves comprehension** before anyone argues |
| Personas inline in a 690-line command | `adviser-board/minds/` — opened only for **seated** minds |
| Sessions in `_my_resources/board_sessions/` | Relocated to `_artifacts/board_sessions/` |

**Pools:** First Principles · Ground Truth · Ruin & Ripple · Unconventional Leverage · Human Needs ·
Execution Reality *(stage room)* · Sales *(stage room)*.

**Supporting contracts**, all new, all under `.agents/commands/adviser-board/`:
`TEAMS.md` (charters) · `ROSTER.md` (index) · `DOCTRINE.md` · `CARD.md` (the return contract) ·
`SPAWNS.md` (the spawn contract) · `THIRD-SIDE.md` (third-side thinking as house discipline).

Totals across the lane: **64 files changed, +5,615 / −1,669**, over 12 commits.

## Decisions

- **Casting is the product.** The old board's failure was not verbosity, it was that *every* lens
  spoke regardless of relevance. An orchestrator that seats 3–5 lenses is what makes the output
  worth reading; trimming word counts alone would not have.
- **Comprehension before debate.** A Read round that proves the board actually loaded the project
  is cheap, and it is the only thing standing between "advice" and confident invention. The old
  spawn template forbade tools outright, so the board had *never once* read what it advised on.
- **Personas are data, not command body.** Moving 43 cards into `minds/` and opening only the
  seated ones is what let the command shrink 690 → 274 without losing anything.
- **Third-side thinking became house discipline**, not an adviser-board-local trick.
- **Hand-owned means fix it by hand.** The Antigravity door's 415-char description was cut to 121
  against the 135-char menu budget rather than exempted.

## Pitfalls this lane hit

- **A generated door went stale and only CI caught it.** `.opencode/commands/smh-adviser-board.md`
  still carried the *pre-rework 690-line* command; `main_write_gate` was red on it. Re-synced from
  the brain via `sync-agents.ps1 -NoGlobals` until byte-identical.
- **A hand-authored door no gate covered.** `.agents/skills/smh-adviser-board/SKILL.md` still
  described the *retired* board — five teams, 500–2,000 word presentations, the old sessions path —
  and that file is Claude's and Codex's actual entry point. **Deleted so the generator owns it**;
  the hand-authored exemption existed for a ~52k body that no longer exists. This is the
  `one-door-per-platform-per-command` law biting where the door was hand-maintained.
- **Not every surface can spawn subagents.** Antigravity/Gemini workflows cannot, and the old
  one-liner told them to "run in --solo mode" without defining it. `SPAWNS.md` §7 now specifies a
  real **inline protocol**, gated on a *capability test* rather than a platform allow-list.

## Verdict

**PASS** — landed on `main` via PR #93 at `548e9b31`; `main_write_gate` green after the two
stale-door fixes above.

## Follow-on owed

- **This close-out ran 15 hours late.** The code landed on 2026-08-26 and then nothing else ran:
  no Dev Record, no ticket move, no prune. The worktree sat on disk as the only evidence.
  Recorded as the pitfall it is — a landing is not a close-out.

## Your Actions

**Nothing owed on this ticket.** SCC-331's deliverable landed on `main` in PR #93 (`548e9b31`).
The Dev Record is filed, the ticket is moved, and the worktree plus both branches are pruned —
all inside this ceremony, all agent steps.

This walkthrough folder is close-out paperwork, not SCC-331 scope, so it rides the standing-push
lane (`SCC-186`, `chore/SCC-186-standing-push`) like every other doc-only change. Its merge click
belongs to that ticket, not this one.
