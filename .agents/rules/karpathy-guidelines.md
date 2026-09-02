---
name: karpathy-guidelines
description: "Universal behavioral principles to reduce common LLM coding mistakes. Derived from Andrej Karpathy's observations, adapted with project-specific lessons."
trigger: always_on
# Floor tier (rules/INDEX.md): loaded every session, unconditionally. No `paths:` —
# a path-scoped rule is on-demand by definition, and this one must bind before the
# first reply, not after the file that would have triggered it.

---

# Behavioral Principles

Tradeoff: These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.
- Read the relevant context files (active-context, component specs) BEFORE writing any code.
- Investigate root cause before proposing fixes — address "why does the architecture allow this bug?" before patching a symptom.
  **When something is reported broken, load `.agents/rules/reproduce-before-you-fix.md` and work its five gates** — that rule is where this line is spelled out (reproduce → pin a test seen red → falsify → minimal fix → prove by reverting).

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Read or grep the file first — never edit blind.
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create dead code, remove it. When your changes make a comment wrong, fix it. But don't touch anything orthogonal to your task.

## 4. Goal-Driven Execution

**Define success before coding. Verify with evidence, not claims.**

- Before starting, state what "done" looks like — concrete acceptance criteria.
- Write or identify tests that will prove the change works.
- Run tests after changes and paste actual terminal output — never claim results without evidence.
- One targeted debug log saves three blind guesses. When you can't observe runtime behavior, instrument and ask the user to report back.
- Don't stack multiple speculative fixes — if you change 3 things and it works, you don't know which one mattered.

## 5. Read the Docs, Don't Guess

**Your training data is a snapshot — the real behavior may have changed. Before fixing, configuring, or calling anything based on what you "know," verify against the current source.**

This fires in **three** situations, not just the obvious one:

1. **Unfamiliar interface** — an MCP tool, CLI flag, API, or library method you haven't used before. STOP. Don't guess and don't pattern-match from memory; a wrong flag or param fails silently or does the wrong thing.
2. **Error or unexpected behavior** — an error message, deprecation warning, config that isn't working, or behavior that doesn't match what you expected. **Search the vendor's docs for the error text or the feature in question before hypothesizing.** The answer is usually already documented; your memory of it is what's wrong.
3. **Troubleshooting / debugging** — before proposing a fix for any issue involving a third-party tool, library, framework, or service, **check the provider's current documentation first.** Your recall of "how Firebase auth works" or "how WSL networking is configured" may be months or years out of date. One web search saves three blind guesses.

For all three:
- Find the authoritative source first. Prefer **first-party documentation from the vendor/company's own website**, official docs, or the tool's own `--help` / README / source. Use the **web search tool** to locate it when it isn't already on disk.
- Match the docs to the **version you're actually on** — interfaces drift, and a remembered signature may be stale (see `dependency-awareness`).
- Only act once you've confirmed the current, real behavior from a first-party source. "It's probably `X`" is not confirmation — it is stale memory dressed as knowledge.
