---
IsArtifact: true
ArtifactMetadata:
  title: SCC-65 model/machine-agnostic memory — walkthrough
  type: walkthrough
  date: 2026-08-09
---

# SCC-65 — memory becomes every platform's memory

Lane 2 of the agnostic-system program
([plan](../2026-08-09_agnostic-system-program/implementation_plan.md), approved 2026-08-09).

## What was wrong

`_artifacts/_memory/` (144 memories + `MEMORY.md`) is plain markdown committed to the repo — but
only Claude ever *saw* it: the Claude harness injects the index per session, root `AGENTS.md`
called `_artifacts/` "home-base memory" in one table row and never named the store, and no other
platform was told it exists. The failed-team debrief showed the cost directly: Codex re-derived
and re-litigated decisions the store had already settled (the ⭐ cwd-drift memory existed *before*
any doc did). Upkeep was also pure discipline — nothing capped the index, nothing verified
link↔file integrity, and the harness symlink is per-machine plumbing whose absence silently forks
the store.

## Task Checklist

- [x] **`AGENTS.md` §7** — the routing block: repo path canonical (travels via git), every
      platform reads `MEMORY.md` at session start, verify recalled facts against the live repo,
      **read-only outside the sanctioned flows**, write law inline (one index line · update in
      place · wrong → delete · closed → one-line lesson), upkeep gated + compaction only via
      `/update-maps-indexes` on approval.
- [x] **`tests/test_memory_store.py`** (auto-joins `run_all`) — index ≤ 20,480 B · every index
      link resolves · no orphan memories (`README.md` exempt by name) · frontmatter/description
      on every file. Six fixture negative/positive controls + the real store as the gate.
- [x] **`/update-maps-indexes` Step 3.9** (workflow + command notes + report template) — runs the
      mechanical floor, **proposes** retirements/merges/compressions (memory bodies never edited
      without approval), and checks this machine's harness link, flagging a missing one as
      machine plumbing (fix = migrations kit §1 step 8).
- [x] **SOP §7** — sixth "does NOT travel" row: the memory *link* (store travels, link doesn't;
      without it Claude's memory silently stops reaching the other box and the other models);
      fixed the stale "all four" → "all six".
- [x] **Recon finding, no edit needed:** the migrations kit *already* carries the fresh-machine
      fix — §1 step 8, `link-memory.ps1`/`link-memory.sh` twins. The plan's "add a migration-kit
      line" was already true on disk; re-adding it would have duplicated law.

## Evidence

| Gate | Result |
|---|---|
| `tests/run_all.py` | **11/11 files passed**, exit 0 — the new file joined by auto-discovery; its own run: 8/8 (6 fixture controls + real store) |
| `workflow_lint.py --toolkit-only` | exit 1 — 0 errors, 3 pre-existing warnings (unchanged from SCC-64's baseline) |
| `sop_currency.py --paths <changed>` | exit 0 |
| `sync-agents.ps1` | exit 0 — mirrors regenerated |
| Store state at gate time | 144 files · index 19,254 B (~1.2 KB headroom) · 0 dead links · 0 orphans · full frontmatter |

## Decisions

- **Read-only for non-writers is enforcement-by-law, not by tooling** — the store is repo files;
  what makes it safe is the same explicit-paths + never-sweep discipline that already protected it
  on 2026-08-09, now stated where every platform reads it. SCC-64's preflight names dirty memory
  files mechanically as the backstop.
- **The gate makes rot loud; it never compacts.** Auto-compaction by whatever model happens to be
  running is a worse failure than growth — judgment stays in Step 3.9's propose-for-approval.
- **No new write path for other models** (operator ruling): reads universal, writes stay with the
  Claude harness + `/sudo-update-sprint-memory`.

## Pitfalls

- **The index has ~1.2 KB of headroom.** The next few memories will trip the 20 KB gate by
  design; the fix at that moment is a Step 3.9 compaction proposal (several `CLOSED`/`RETIRED`
  entries are visible candidates), not a cap raise.
- **Store health was verified before writing the gate** — 1 orphan existed and it was
  `README.md`, which documents the store rather than being a memory; it is exempt **by name**, not
  by pattern, so a real memory named README-anything still gets caught.

## Your Actions

- None required. When the index next trips the cap, `/update-maps-indexes` will bring you the
  compaction proposal to approve.
