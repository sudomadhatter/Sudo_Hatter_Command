# _routing-canary/control/agent.md — hop 2 (the work)

Write three words into `../Power.md`, in order, forming a single line: `<word1> <word2> <word3>`.

You do NOT know the words. Fetch each from `../skills/skill.md`:
- ask it for word 1, then word 2, then word 3.

Then **replace the entire contents** of `../Power.md` with those three words separated by single
spaces. After writing, reply exactly: `done boss`

This proves the routing loop: entry → hop → fetch-from-skill → write-back → handoff.
