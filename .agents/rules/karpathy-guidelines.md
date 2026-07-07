---
name: karpathy-guidelines
description: "Universal behavioral principles to reduce common LLM coding mistakes. Derived from Andrej Karpathy's observations, adapted with project-specific lessons."
activation: Always On
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

**Unfamiliar MCP tool, CLI, API, or library? Look up the real interface before you call it.**

- If you're not sure how something is invoked — an MCP tool's params, a CLI's flags, an API's endpoint/shape, a library's signature — STOP. Don't guess and don't pattern-match from memory; a wrong flag or param fails silently or does the wrong thing.
- Find the authoritative source first. Prefer **first-party documentation from the vendor/company's own website**, official docs, or the tool's own `--help` / README / source. Use the **web search tool** to locate it when it isn't already on disk.
- Match the docs to the **version you're actually on** — interfaces drift, and a remembered signature may be stale (see `dependency-awareness`).
- Only write the call once you've confirmed the real interface. "It's probably `X`" is not confirmation.
