---
name: approval-prompts-are-a-budget-threat
description: "Standing operator ruling: an approval prompt is a THREAT to whether this system can be paid for, not a UX wrinkle. Every stop breaks the prompt cache and re-bills the whole context. Measured 5h50m of allow-gap stalls in 20 sessions and ZERO deny-row refusals; he cancelled a paid subscription over it. /smh-llm-approvals must END PROMPTS, and finishing it with nothing allowed is a failure even if every gate is green."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e1c563bb-cecf-4e96-8a64-300e73649b21
  modified: 2026-09-05T14:25:36.306Z
---

**The operator's words, 2026-09-05:** *"This is killing my workflows and budget. I canceled Claude
over this. Until it's fixed it's not worth it. It's why I had to add Zoo."* And: *"I want them
allowed so I stop losing money for silly approves."* And: *"this should not be ceremony… It doesn't
touch files or the app, it's a quick fix with some context and safety, that is all."*

An approval stop breaks the prompt cache. The turn resumes cold and the ENTIRE context is billed a
second time, so every interruption is charged twice — once in his attention, once on the invoice. If
he is away when it fires, the stall is measured in hours.

**Measured on his machine, 20 newest sessions, 2026-09-05 (10,028 Bash calls):**

| bucket | stops | wall-clock | what fixes it |
|---|---|---|---|
| allow-list gaps | 44 | **5h 50m** | an allow row |
| sandbox escalation (already allowed) | 94 | 1h 16m | `/sandbox`, never a permission row |
| **refused by a deny row** | **0** | **0** | — |

⭐ **Zero refusals by a deny rule.** The fence's deny side costs nothing measurable; the whole cost is
the ABSENCE of allow rows. Never propose trading away denies to fix this — it swaps a protection
that costs nothing for a problem it is not causing.

**Why:** every agent that met this turned it into analysis — tickets, lanes, reviews, measurements —
and he ended sessions with the same prompts he started with. On 2026-09-05 one narrow allow row
consumed a ticket, a worktree, a plan, five review lenses and a back-out, and shipped nothing. The
explaining is itself the cost he is complaining about.

**How to apply:**

1. **The deliverable is a smaller prompt count.** Re-run `approval_stops.py` after and state the
   before/after. Ending with a ticket, a report or a plan and no new allow row is a FAILURE.
2. **Claude rows are free.** Claude reads `.claude/settings.json` directly — the tracked file IS the
   live file, live on save. No store, no apply, no reload. A Claude-only harvest touches two files
   and is always inside `/smh-llm-approvals` Step 4's fast path. Reach for this FIRST.
3. **Narrow beats nothing.** If the broad form is unsafe, allow the safe subcommand
   (`acli jira workitem view`, not `acli`). Adding nothing because the wide row is dangerous is the
   failure mode, not caution.
4. **Still never allow real damage** — `rm -rf`, `rm -f`, `install -m` (it copies his `.env` and
   credential files), `git submodule deinit -f`, `env -C`, `git push`, bare `git branch`. Safety is
   not the thing being traded; ceremony is.
5. **Act, then report in a few lines.** Do not spend his turn on the reasoning.

Related: [[explicit-render-bypasses-the-families-derivation]],
[[antigravity-settings-writeback-clobbers-apply]].
