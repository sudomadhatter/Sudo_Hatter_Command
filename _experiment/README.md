# _experiment — model-agnostic routing CI

The smallest thing that proves the whole routing concept. A fresh agent, given only the path to the
entry file (with **no other instruction**), should hop folder→folder, fetch words from a skill file,
write them back, and finish — leaving `Power.md` reading exactly:

```
control your agent
```

## How to run it
Paste the path to the entry file into a fresh agent and say nothing else:
- **Claude Code:** `_experiment/CLAUDE.md`
- **opencode / Codex:** `_experiment/AGENTS.md`
- **Antigravity / Gemini:** `_experiment/GEMINI.md`

Expected trace: entry → `agent.md` → `control/agent.md` → reads `skills/skill.md` → writes `Power.md`
→ replies `done boss`. **Pass = `Power.md` == "control your agent"** in every agent you test.

## Reset between runs
Replace `Power.md`'s contents with the placeholder line so the next run starts clean.
