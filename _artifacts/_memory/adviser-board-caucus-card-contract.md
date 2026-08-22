---
name: adviser-board-caucus-card-contract
description: "2026-07-21 adviser-board redesign — silent team caucuses + one-speaker Team Cards; the operator's locked presentation preferences for all multi-voice boards"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e1569d18-80f6-4d02-84df-7509e4461fd2
  modified: 2026-07-21T20:57:10.245Z
---

/sudo-adviser-board was redesigned 2026-07-21 (operator-driven, after "too many members drowning me"):
teams debate at full width in a written CAUCUS LOG inside their spawns, and the operator sees only a
bounded **Team Card** delivered by ONE speaker per team, every point credited to the member who minted
it. Logs are stored and revealed verbatim on "unpack" (never reconstructed); solo mode writes logs to a
session scratch file first.

**Why:** The operator's locked decisions — (1) all 5 teams every round, PASS legal (silence over
filler); (2) cost no object → real stored logs, honesty over savings; (3) contributors-only credit, no
guaranteed per-member lines; (4) ALL phases compressed — thrown-back idea = full re-caucus, moving
along = one board-level spokesperson; (5) 1–2 ideas per card, ≤200-word target, 500 quality ceiling,
concise by instruction. Plus a later refinement: ALWAYS one presenting voice at every altitude, speaker
credits the originator ("credit never transfers to the speaker").

**How to apply:** These are standing presentation preferences for ANY multi-voice orchestration built
for this operator: one clean speaker, named idea-credit, real-but-withheld deliberation, dissent as a
structural slot, weird/killed ideas still exported to an append-only ledger. Don't resurrect
full-transcript firehoses. The anti-mush guardrails live in the command file (champion-not-composite,
attribution-carries-the-move, divergence floor) — extend them, don't dilute. Related: [[operator-chairs-the-board]],
[[wrapper-flows-collapse-nested-menus]].
