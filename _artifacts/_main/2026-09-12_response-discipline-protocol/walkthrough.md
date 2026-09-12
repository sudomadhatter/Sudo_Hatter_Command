# Walkthrough: Response Discipline Protocol Added

**Date:** 2026-09-12  
**Files Modified:** [`.agents/rules/operator-profile.md`](.agents/rules/operator-profile.md:92)

## What Was Done

Added a new "Response Discipline" section to [`operator-profile.md`](.agents/rules/operator-profile.md:92) containing 4 behavioral rules that eliminate defensive patterns in Claude model responses:

1. **Stateless Execution** — no apologies or explanations for past errors
2. **No Defensive Receipts** — no proof-I-followed-the-instruction comments
3. **Zero CYA** — stop at the solution, no unsolicited disclaimers/warnings/next-steps
4. **Professional Conciseness** — plain declarative sentences, no "Great"/"Certainly", no self-grading ("successfully")

## Placement

Inserted as new section between:
- Line 91: end of "How to speak to him" (the 9 obligations)
- Line 104: start of "Downstream rules this explains"

This placement keeps response discipline adjacent to but separate from the speaking obligations — they govern structural communication patterns, while this addresses tone and execution discipline.

## Why operator-profile.md?

The protocol belongs here because it governs **how to communicate** with Mr. Hatter. The file already contains:
- Who Mr. Hatter is (Jobs/Woz contract)
- 9 speaking obligations
- Self-check passes

The new protocol addresses complementary issues: defensive behavior, CYA disclaimers, self-grading language. It's about **how you speak**, not what you build (karpathy-guidelines) or what's forbidden (constitution).

## Load Tier

[`operator-profile.md`](.agents/rules/operator-profile.md:1) is a **floor-tier rule** (loaded every session, unconditionally per [`.agents/rules/INDEX.md`](.agents/rules/INDEX.md:10)). The change takes effect immediately in all sessions.

## Verification

Suite run initiated: `python3 .agents/scripts/tests/run_all.py --on-main` (still running, awaiting completion to confirm no breakage of frontmatter tests or other rule integrity checks).

The modification preserves all existing content — only inserts the new section, shifting subsequent sections down.

## Alignment with Existing Doctrine

The protocol reinforces existing house rules:
- Bans on "Great", "Certainly" openings already mentioned in root `AGENTS.md` §RULES
- Professional conciseness reinforces obligation #9 (close the loop) by eliminating trailing disclaimers
- Stateless execution aligns with the no-mental-diffs principle (obligation #5)
