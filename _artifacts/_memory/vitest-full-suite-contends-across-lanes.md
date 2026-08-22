---
name: vitest-full-suite-contends-across-lanes
description: "BOTH suite locks now ENFORCED (pytest conftest.py + vitest globalSetup) — same-stack full runs queue, scoped runs never wait; but the locks are per-STACK, so a backend+frontend overlap still contends (blew the 15s ErrorBoundary timeout). Kill-the-chain + persistent-log lessons still bind."
metadata: 
  node_type: memory
  type: project
  originSessionId: 368aa7c1-d8da-4c4a-a0b7-13c22673ad08
  modified: 2026-08-02T02:49:58.798Z
---

AGY frontend full-suite `npx vitest run` runs fine alone but on multi-team days several lanes launch it concurrently → tinypool workers from 3+ lanes burn all cores and every run crawls/looks hung (observed 2026-07-04: runs still going at 17+ min that normally finish in minutes; workers at 2,000+ CPU-seconds). Daniel's ratified handling ([[autopilot-manual-takeover-check-liveness]] is the same kill-the-chain family):

**How to apply:**
- Per-lane verification = SCOPED runs only (`npx vitest run <story test files>` — ~8s even under contention). ONE full-suite run, serialized (post-mortem by Daniel or by whichever lane goes last); record the deferral honestly in the story/walkthrough as an AC-3 deviation.
- Stopping a bg vitest: `TaskStop` kills only the shell — the detached node worker chain survives and keeps burning cores. Enumerate `node.exe` with cmdline matching `import-meta-resolve` + the project path, attribute by StartTime to YOUR run windows, and `Stop-Process` only yours; other lanes' workers look identical (don't kill on CPU alone — the permission classifier will rightly block untargeted kills; Daniel saying "kill yours" is the authorization).
- Diagnose hung-vs-starved by sampling `Get-Process node` CPU twice: climbing ≈ starved-but-working, flat ≈ hung.
- Don't pipe bg runs through `| tail` — it buffers everything, so the output file stays 0 bytes and you lose interim progress; use `--reporter=dot` with direct output instead. **This applies verbatim to pytest** (re-learned the hard way 2026-08-01, three times in one night: every `| tail` run that died — session restart, kill — lost its failure names). Long runs: `> persistent.log 2>&1` in the scratchpad, tail the FILE; the log then survives even a Claude-session death.
- **Background shells die when the operator closes/reopens the chat** — the whole process tree (wrapper + pytest + workers) is a child of the Claude Code process. A run killed at 98% by a chat reload looks like `node down`+`OSError` teardown, not a test failure. Detached `Start-Process` with a log file is the escape when a run must survive the session.
- **BOTH sides are now enforced, not advisory** (2026-08-01): AGY's root `conftest.py` takes a machine-wide `filelock` for directory-level pytest runs, and `frontend/vitest.global-setup.ts` (wired via `globalSetup` in vitest.config.ts, commit cae06a78) does the same for full `vitest run`s — zero-dep `mkdir` lock + owner-PID liveness check (a kill -9'd holder is reclaimed in ~5s; `AGY_SUITE_LOCK=0` bypasses both; watch mode never locks). Concurrent big runs QUEUE (0-CPU, healthy); scoped runs never wait. Proven live: pytest 3 collisions/3 clean, vitest full battery runtime-verified (queue+handoff, scoped-no-wait, reclaim, bypass, exact green baseline 82/1 files 552/1 tests).
- **The locks are per-STACK, deliberately** — a backend pytest run and a frontend vitest run still share the box. Measured cost (2026-08-01): a concurrent backend suite pushed the frontend run 222s→322s and that alone blew the 15s testTimeout on a test that takes 2.1s alone. The flake tracks TOTAL box load, not the spec — ~85% of frontend wall clock is jsdom setup + module transform (environment 1339s / import 286s vs tests 217s), so the real fix is per-file setup cost, not more timeout. Don't cross-couple the locks without measuring first: full serialization of both stacks would roughly double multi-lane close-out time.
