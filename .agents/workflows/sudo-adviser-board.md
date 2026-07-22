---
description: 'Convene the Adviser Board — historical minds in 5 challenge teams (First Principles, Ground Truth, Ruin & Ripple, Unconventional Leverage, Human Needs) + an on-call Real-World marketing squad. Teams debate in private caucuses, deliver full narrative presentations to the chair (500–2,000 words each), then file distilled member-credited Team Cards as the minutes; full deliberation stored and unpacked verbatim on demand. Flips assumptions, sees around corners, surfaces what people NEED, not what they want. Operator-chaired: phases (Brainstorm → Plan → Market → Brief) advance only on the operator''s word.'
platforms: [antigravity]
---

# /sudo-adviser-board — Antigravity launcher

Thin launcher: the full board (roster with historical cognitive signatures, open-table norms, Third-Side
question bank, spawn templates, phased arc) lives in **`.agents/commands/sudo-adviser-board.md`** — it
exceeds Antigravity's 12k workflow limit, so this wrapper stays slim on purpose. Do NOT inline the body
here; on any edit, update the command file (single source of truth) instead.

**Execute now:**

1. Read `.agents/commands/sudo-adviser-board.md` (relative to the repo root) and follow it END TO END.
2. Pass the user's arguments through verbatim (topic + optional `--solo` / `--model <m>` flags).
3. If subagent spawning is unavailable on this surface, run in `--solo` mode (roleplay all voices in one
   response) and announce it.
4. Session briefs save to `_my_resources/board_sessions/YYYY-MM-DD-<topic-slug>.md` in the current repo.

Quick orientation (details in the command file): 5 challenge teams — 🔬 First Principles (Kepler, Feynman,
Tesla, Turing) · 🩺 Ground Truth (Semmelweis, Snow, Wegener, Nightingale) · 🌊 Ruin & Ripple (Mandelbrot,
Taleb, Munger, Bastiat) · 🧬 Unconventional Leverage (Margulis, Nakamoto, Ravikant, Fuller) · 🎯 Human
Needs (Drucker, Schwartz, Rubin, Diogenes, Houellebecq) — plus the 📣 Real-World marketing squad (a team
of equals: Hormozi, Godin, Vaynerchuk, Brunson + dual-hats) and a 10-mind bench. Arc: **Brainstorm → Plan
→ Market → Brief** — the operator chairs; phases advance only on the operator's word, and the board never
pushes the pace.
