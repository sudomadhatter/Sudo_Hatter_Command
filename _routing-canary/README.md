# _routing-canary — model-agnostic routing regression check

The smallest thing that proves the whole routing concept still works — in any tool. A fresh agent,
given only the path to the entry file (with **no other instruction**), should hop folder→folder, fetch
words from a skill file, write them back, and finish — leaving `Power.md` reading exactly:

```
control your agent
```

If it does, this tool can follow the adapter→route→fetch-from-skill→write-back→handoff pattern the
whole system depends on. (Formerly `_experiment/` — renamed because it is a permanent canary, not a
throwaway experiment.)

## When to run it (the triggers)

This is a **regression check**, not a one-time demo. Re-run it when:
- you change routing **structure** — root `AGENTS.md`, `router.md`, or the adapter/skill pattern;
- you **qualify a new tool** — a new LLM or CLI you want to drive the system;
- after any change that could affect how an agent hops folders or reads skills.

A green run proves the *mechanism* works in that tool. It does **not** prove your real workspaces route
correctly — for that, run the cold-route test ("work on X" from a fresh session and confirm it lands in
the right workspace).

## How to run it

Paste the path to the entry file into a fresh agent and say nothing else:
- **Claude Code:** `_routing-canary/CLAUDE.md`
- **opencode / Codex:** `_routing-canary/AGENTS.md`
- **Antigravity / Gemini:** `_routing-canary/GEMINI.md`

Expected trace: entry → `agent.md` → `control/agent.md` → reads `skills/skill.md` → writes `Power.md`
→ replies `done boss`. **Pass = `Power.md` == "control your agent"** in every agent you test.

## Reset between runs

Replace `Power.md`'s contents with the placeholder line so the next run starts clean.
