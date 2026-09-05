---
name: memory-store-is-read-by-every-platform
description: "SCC-65: root AGENTS.md §7 routes EVERY model on EVERY machine to `_artifacts/_memory/MEMORY.md` at session start — READ-ONLY outside the sanctioned write flows. 25 KB index cap gated in run_all; the gate itself raises MEMORY AUDIT DUE at 90% and the agent must ask (SCC-68)."
metadata:
  type: project
---

Since 2026-08-09 (SCC-65) the memory store is **every platform's** memory, routed from root
`AGENTS.md` §7 — not just Claude's:

- **The repo path is canonical**: `_artifacts/_memory/`. It travels via git, so it is identical on
  both machines and readable by Codex, opencode, and Antigravity. Claude's `~/.claude/...` path is
  a per-machine symlink *into* it — a convenience, never the mechanism
  ([[portable-memory-store-dot-slug-trap]], [[one-pc-windows-and-wsl]]).
- **Every session, every platform: read `MEMORY.md` first**, then open the full files relevant to
  the task. Verify a recalled fact against the live repo before acting on it.
- **READ-ONLY for everyone** except the sanctioned writers (Claude harness auto-memory,
  `/sudo-update-sprint-memory`). A dirty memory file you did not write is another session's work in
  flight — park or leave it; never sweep, delete, or commit it under your task.
- **Gated, not policed**: `tests/test_memory_store.py` (in `run_all`) enforces index ≤ 25 KB, every
  index link resolves, no orphan files (`README.md` exempt by name), frontmatter present.
- **⚠ The gate triggers its own remedy (SCC-68).** At **90 % of cap** — below it, while the run still
  PASSES — it prints a `MEMORY AUDIT DUE` block with a derived candidate worklist. A script can
  print, it cannot ask, so §7 binds the *agent*: see that block → **STOP and ask the operator**
  whether to run `/memory-audit`. Never compact on your own judgment, never raise the cap.
- **Compaction is judgment, so it is per-item approved**: **`/memory-audit`** ground-truths each
  candidate against the live repo (does the rule/script it names still exist? is the `CLOSED` thing
  actually gone? do its wiki-links resolve?), proposes retire/merge/compress with bytes freed, and
  applies only what is approved. It also checks this machine's harness link.

**Why it moved off `/update-maps-indexes` Step 3.9:** hanging upkeep on a *map* workflow meant it
never ran — nobody opens a map command because memory feels heavy, and the index reached 99.5 % of
cap with its remedy parked where no one had a reason to go. Upkeep must trigger from something that
runs on its own schedule. Related: [[one-door-per-platform-per-command]], [[active-context-pointer-budget]].
