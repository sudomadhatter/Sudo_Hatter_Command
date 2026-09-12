# Implementation Plan: Add Response Discipline Protocol to operator-profile.md

**Date:** 2026-09-12  
**Artifact Store:** `_artifacts/_main/` (home-base work)  
**Target:** `.agents/rules/operator-profile.md`

## Overview

Add a new "Response Discipline" section to [`operator-profile.md`](.agents/rules/operator-profile.md:1) that codifies 4 anti-defensive behavioral rules for Claude model responses: stateless execution (no apologies for past errors), no defensive receipts, zero CYA disclaimers, and professional conciseness (no "Great", "Certainly", "successfully", etc.).

## Why operator-profile.md?

This protocol governs **how to communicate** with Mr. Hatter and the tone/discipline of every response. The file already contains:
- Who Mr. Hatter is (Jobs/Woz contract)
- 9 speaking obligations (#9: close the loop — a finding without a fix is a bill)
- Self-check passes (opening & ending)

The new protocol addresses complementary communication issues: defensive behavior, disclaimers, self-grading language. It belongs in operator-profile because it's about **how you speak**, not what you build (which would be karpathy-guidelines) or what you're forbidden from doing (which would be constitution).

## Placement

Insert as new section **"## Response Discipline"** between:
- **After:** "## How to speak to him" (currently ends at line 91)
- **Before:** "## Downstream rules this explains" (currently starts at line 92)

This keeps it adjacent to but separate from the 9 obligations — they're structural communication patterns; this is tone/execution discipline.

## Content to Add

```markdown
## Response Discipline

**Stateless Execution:** Never apologize, defend past mistakes, or explain your thought process for an error. If corrected, output only the revised execution.

**No Defensive Receipts:** Do not leave notes or comments proving you followed an instruction. Your outputs are not in dialogue with prior versions of yourself.

**Zero CYA (Cover Your Ass):** Stop exactly at the requested solution. Do NOT generate unsolicited warnings, caveats, edge-case disclaimers, or lists of "next steps" and "things to consider" unless they represent an immediate, catastrophic risk to the build.

**Professional Conciseness:** Use plain, declarative sentences. State the facts and stop. Do not open with agreement, praise, or conversational filler ("Great", "Certainly", "Okay", "Sure"). Do not grade your own work — avoid words like "successfully" or "perfectly".

> This eliminates the mental overhead of reading through fabricated urgency or irrelevant problems. It forces responses to function as silent utility: the execution and nothing else.
```

## Changes

**File:** `.agents/rules/operator-profile.md`

1. Insert new section "Response Discipline" after line 91 (end of "How to speak to him" section)
2. Shift "Downstream rules this explains" and "The self-check" sections down accordingly
3. No other modifications to existing content

## Verification

1. Read the modified file to confirm placement and formatting
2. Run `tests/run_all` to verify the rule file doesn't break frontmatter tests
3. Confirm the section appears in the correct location relative to the 9 obligations

## Notes

- This is a floor-tier rule (loaded every session), so the change takes effect immediately
- The protocol aligns with existing house doctrine: operator-profile already bans "Great", "Certainly" openings (mentioned in AGENTS.md §RULES)
- The conciseness rule reinforces obligation #9 (close the loop) by eliminating trailing disclaimers
