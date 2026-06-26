# Implementation Plan — Doc-Wiring Graph Extractor (`.agents/` toolkit)

**Date:** 2026-06-26
**Where from:** home base (lobby), cwd = `c:\Sudo_Hatter_Command`
**Owner:** Daniel · drafted by Claude
**Status:** ⛔ AWAITING APPROVAL (no code written yet)

---

## 1. Why (the gap, in your own words)

`_docs/repo-map.md` already admits it (lines 41–43):

> *"the markdown rule/workflow files yield few cross-file edges (GitNexus extracts headings, not doc references) … trust the files for 'what references what.'"*

GitNexus is **structurally blind to prose wiring**. This was the one real gap surfaced when we compared GitNexus vs graphify — and graphify "fixes" it only with a non-deterministic, token-costed LLM layer that breaks your *deterministic / ~$0 / swappable Tier-1* design. So we build it **owned, deterministic, $0** instead.

**Bonus deliverable:** resolving every reference against the real file set automatically catches the **dangling `.agent/` (singular) refs** flagged as OPEN in `[[tooling-gitnexus-shannon-tracks]]` (~50+ stale refs in `commands/`, `opencode-agents/`, `skills/`). One script → wiring map **+** broken-link report.

## 2. What it is

A new script `\.agents\scripts\generate_doc_graph.py` that mirrors the existing
`generate_repo_map.py` pattern exactly (stdlib-only Python, sentinel-splice into a
curated/auto doc, same `--root`/`--output`/`--ignore` arg style, ASCII-safe).

It walks a root (default `.agents/`), reads every `.md`, extracts outbound doc
references, resolves them against the indexed set, and emits the graph.

### Grounding data (verified 2026-06-26, this repo)
| Pattern | Regex | Count in `.agents/` | Handle? |
|---|---|---|---|
| Backtick ref `` `router.md` `` | `` `([^`]+\.md)` `` | 100+ (dominant) | ✅ |
| Markdown link `](rules/x.md)` | `\]\(([^)]+\.md[^)]*)\)` | 43+ | ✅ (strip `#anchor`) |
| Wikilink `[[x]]` | `\[\[…\]\]` | **0** | ❌ skip (memory-only, out of scope) |

### Resolution algorithm (per extracted target → file in set)
1. Target contains `/` → try path **relative to source file**, then **relative to root**.
2. Bare basename (`constitution.md`) → **basename match** across all indexed `.md`.
   - exactly 1 hit → **resolved** edge
   - 0 hits → **dangling** (broken ref — into the report)
   - >1 hits → **ambiguous** (record all candidates; surfaces duplicate-name collisions)
3. Self-refs and pure-anchor links (`#section`) are dropped.

## 3. Outputs (2 artifacts, mirroring graphify's `graph.json` idea — but owned)

1. **`_docs/doc-graph.md`** — human-readable, curated header + AUTO body between
   `<!-- DOC-GRAPH:AUTO-START/END -->` sentinels (same splice contract as repo-map). AUTO body =
   - **Hubs** — docs ranked by in-degree ("which doc is load-bearing / most-pointed-to")
   - **Orphans** — `.md` nothing references (dead-file candidates)
   - **Dangling refs** — `source → unresolved target` (the broken-`.agent/` finds)
   - **Ambiguous refs** — bare names that resolve to >1 file
2. **`_docs/doc-graph.json`** — machine-readable `{nodes:[…], edges:[{from,to,kind,status}]}`
   for agents / future MCP / drift tooling to consume. Deterministic, diff-friendly, git-committable.

## 4. Decisions to confirm (pick before I build)

- **D1 — Scope/root.** Default **`.agents/` only** (matches the `SUDO_COMMAND` index + the stated gap).
  Option: also fold in lobby front-doors (`AGENTS.md`, `router.md`, `_docs/*.md`). → *Recommend: `.agents/` for v1, `--root` configurable so the lobby docs can be added later.*
- **D2 — Drift hook.** A `check-doc-graph-drift.ps1` SessionStart nag (mirrors the repo-map one) **or**
  manual on-demand re-run? → *Recommend: ship generator now, run-on-demand + documented command; decide the nag after we see real output (avoid SessionStart noise).*
- **D3 — Vendoring.** repo-map vendors into every project; this one is home-base toolkit-specific.
  → *Recommend: master in `.agents/scripts/`, run from lobby, NOT vendored (revisit if a project wants its own doc graph).*

## 5. Files touched
| File | Action |
|---|---|
| `.agents/scripts/generate_doc_graph.py` | **new** — the extractor |
| `_docs/doc-graph.md` | **new** — generated (curated header hand-seeded once, AUTO body scripted) |
| `_docs/doc-graph.json` | **new** — generated sidecar |
| `_docs/repo-map.md` | **1-line edit** — curated header: add pointer "doc wiring → `doc-graph.md`" |
| `_artifacts/INDEX.md` | ledger row (on hand-off) |

*No existing script, rule, or workflow is modified. Generator is additive + read-only over the toolkit.*

## 6. Verification (definition of done)
1. `python .agents/scripts/generate_doc_graph.py` runs clean, writes both outputs.
2. **Known-true edges present:** `AGENTS.md → router.md`, `AGENTS.md → constitution.md`,
   `gitnexus-guide/SKILL.md → gitnexus-{exploring,debugging,impact-analysis,refactoring}`.
3. **Dangling report** surfaces the `.agent/` (singular) stale refs — cross-check the count is in the
   ~50+ ballpark the memory grep found (sanity, not exact).
4. Re-running is idempotent (only the AUTO block / json change; curated header untouched).
5. ASCII-only; runs under the same Python the repo-map generator uses.

## 7. Out of scope (v1)
Wikilink (`[[ ]]`) parsing · per-project vendoring · auto-fixing dangling refs (report only) ·
graph visualization (the `.json` can feed one later) · MCP exposure.

---
**On approval:** build §5, run §6, then write `walkthrough.md` + `task-list.md` here and append the INDEX row.
