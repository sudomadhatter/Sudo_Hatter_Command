---
description: 'Convene the Adviser Board — a third-side thinking board of 43 historical minds. Recon grounds it in a real project, an orchestrator casts 3–5 lenses with THREE minds each chosen to collide, and their debates run in parallel, each returning one ~250-word card through a mandatory balcony beat. Refuses the binary frame: a reframe outranks an answer. Stages into Execution Reality and Sales on the operator''s word.'
platforms: [antigravity]
---

# /smh-adviser-board — Antigravity launcher

Thin launcher. The full board — the third-side discipline, team charters, 43-mind roster, operator
doctrine, card contract and spawn templates — lives in **`.agents/commands/smh-adviser-board.md`** and
the folder beside it, `.agents/commands/adviser-board/`. It exceeds Antigravity's 12k workflow limit, so
this wrapper stays slim on purpose. Do NOT inline the body here; on any edit, update the command file
(single source of truth) instead.

**Execute now:**

1. Read `.agents/commands/smh-adviser-board.md` (relative to the repo root) and follow it END TO END.
2. Pass the user's arguments through verbatim (topic + optional `--project <name>` / `--solo` /
   `--model <m>` flags).
3. If subagent spawning is unavailable on this surface, run in `--solo` mode (the orchestrator runs every
   room itself, writing each debate floor to a scratch file before that team's card) and announce it.
4. Session briefs save to `_artifacts/board_sessions/YYYY-MM-DD-<topic-slug>.md`.

Quick orientation, details in the command file. **This is a third-side board**: its job is to refuse the
binary frame and find the position nobody in the argument occupies — three minds per team is that
discipline made structural, because two can only give you A, B, or the midpoint.

Five debate lenses — 🔬 First Principles · 🩺 Ground Truth · 🌊 Ruin & Ripple · 🧬 Unconventional
Leverage · 🎯 Human Needs — plus two stage rooms convened on the operator's word: 🔧 **Execution
Reality** (the correct plan that never ships) and 📣 **Sales** (the thing that never reaches anyone).
Nobody is on a bench; whoever is not seated is observing and callable.

The round: recon → cast gate (the operator gavels) → a silent comprehension Read → parallel debates of
3–5 cycles pivoting on **the balcony** → one ~250-word card per team → one footer line and silence. The
operator chairs; nothing advances without his word, and the board never pushes the pace.
