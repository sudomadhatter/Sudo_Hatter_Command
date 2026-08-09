---
name: memory-store-is-read-by-every-platform
description: "SCC-65: root AGENTS.md §7 routes EVERY model on EVERY machine to `_artifacts/_memory/MEMORY.md` at session start — READ-ONLY outside the sanctioned write flows. 20 KB index cap gated in run_all; compaction is propose-only."
metadata:
  type: project
---

Since 2026-08-09 (SCC-65) the memory store is **every platform's** memory, routed from root
`AGENTS.md` §7 — not just Claude's:

- **The repo path is canonical**: `_artifacts/_memory/`. It travels via git, so it is identical on
  both machines and readable by Codex, opencode, and Antigravity. Claude's `~/.claude/...` path is
  a per-machine symlink *into* it — a convenience, never the mechanism
  ([[portable-memory-store-dot-slug-trap]], [[two-machines-mac-and-pc]]).
- **Every session, every platform: read `MEMORY.md` first**, then open the full files relevant to
  the task. Verify a recalled fact against the live repo before acting on it.
- **READ-ONLY for everyone** except the sanctioned writers (Claude harness auto-memory,
  `/sudo-update-sprint-memory`). A dirty memory file you did not write is another session's work in
  flight — park or leave it; never sweep, delete, or commit it under your task.
- **Gated, not policed**: `tests/test_memory_store.py` (in `run_all`) enforces index ≤ 20 KB, every
  index link resolves, no orphan files (`README.md` exempt by name), frontmatter present.
- **Compaction is judgment, so it is propose-only**: `/update-maps-indexes` **Step 3.9** proposes
  retirements/merges/compressions for approval and checks this machine's harness link. The gate
  makes rot loud; it never edits a memory body. Auto-compaction by whatever model is running would
  destroy exactly the recall the store exists for.

The index had ~1.2 KB of headroom at landing, so the cap will trip by design — the answer is a
Step 3.9 compaction proposal, **not** raising the cap.
