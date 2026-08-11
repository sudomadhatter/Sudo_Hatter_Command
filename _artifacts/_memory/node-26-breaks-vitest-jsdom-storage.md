---
name: node-26-breaks-vitest-jsdom-storage
description: "Node 26 breaks vitest's jsdom env — localStorage undefined in tests; run Node 22 LTS; green elsewhere may be stale node_modules/Node, not a healthy stack"
metadata: 
  node_type: memory
  type: project
  originSessionId: eafbef40-5e30-4001-b696-a23ece42c00d
  modified: 2026-08-06T23:34:11.545Z
---

Node 26.7.0 breaks vitest's jsdom **global injection**: `localStorage`/`sessionStorage` never reach the
test globals, so every file touching them dies in `beforeEach` with
`TypeError: Cannot read properties of undefined (reading 'clear')`. On the new Mac (2026-08-06) this
looked like 18 real test failures across 4 AGY frontend files — including a red file dying
PRE-ASSERTION (see [[red-test-can-die-before-its-assertion]]).

Clean-room matrix (probe project, zero repo code): vitest 4.1.5 AND 4.1.10 × jsdom 27 AND 28.1.0 → all
broken on Node 26; identical probe green on Node 22.23.2. Raw jsdom on Node 26 is fine — the break is
vitest's window→global copy.

**Why:** `brew install node` gives current (26), not LTS. The suite's green history on other machines
proves nothing about a fresh install — node_modules and Node versions don't travel via git.

**How to apply:** On any machine where vitest shows storage-flavored failures the other machines don't,
check `node --version` FIRST. Fix at the LINK, not with a PATH export:
`brew unlink node && brew link --force --overwrite node@22`. ⛔ The first attempt here was a `~/.zshrc`
PATH line, which is **interactive-only** — scripts, agent-run commands, hooks and GUI-spawned processes
all still got Node 26, so the suite passed by hand and failed in automation on the same machine. Verify
all three modes, not one: `for m in -c -lc -ic; do zsh $m 'node --version'; done`. After the switch AGY
frontend ran `581 passed / 1 skipped / 0 failed`. Recorded in the migration kit's vitest section
(`_my_resources/migrations/install_guides/python_vytest-updates-other-machines.md`). Related: [[agy-frontend-vitest-harness]].
