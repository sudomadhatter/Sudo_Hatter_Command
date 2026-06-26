# Walkthrough — Doc-Wiring Graph Extractor

**Date:** 2026-06-26 · **From:** home base (lobby) · **Plan:** [implementation_plan.md](implementation_plan.md) (approved, D1–D3 all as recommended)

## What this was

A follow-on from comparing GitNexus vs graphify (see memory [[tooling-gitnexus-shannon-tracks]]). The one real
gap graphify highlighted — **doc-to-doc "what references what," which GitNexus can't see** (it extracts headings,
not references) — is now filled the *owned* way: a deterministic, no-LLM, ~$0 script, instead of bolting on
graphify's token-costed LLM layer.

## What was built

- **`.agents/scripts/generate_doc_graph.py`** — new generator, mirrors `generate_repo_map.py` exactly (stdlib
  only, sentinel-splice into a curated/auto doc, ASCII-safe, same `--root`/`--output`/`--ignore` arg style).
  Walks `.agents/`, extracts `.md` references from the two patterns that actually dominate the toolkit
  (backtick/inline path tokens + markdown links; **no** `[[wikilinks]]` — verified zero in `.agents/`),
  resolves each against the real file set, emits the graph.
- **`_docs/doc-graph.md`** — human report (curated header + regenerated AUTO body): hubs, broken-path refs,
  unresolved bare names, ambiguous refs, orphans-by-dir. Tables capped at 60 rows.
- **`_docs/doc-graph.json`** — complete machine-readable `{nodes, edges, dangling, external, ambiguous}`.
- **`_docs/repo-map.md`** — 1-line pointer added in the curated GitNexus note (the gap it flags now has a fix).

## Resolution model (why the report is trustworthy)

Each reference resolves to one of: **resolved** (in-scope edge) · **external** (real file outside `.agents/`,
e.g. lobby `router.md` — *not* broken) · **ambiguous** (bare name matches >1 file) · **dangling** (nothing).
The key signal split, added during verification: a dangling target that names a **real directory path**
(`dir/file.md`) is a **likely-broken link** (signal); a **bare filename** — or a root-relative `/name.md`,
which is the bmad output-file pattern — is usually a **generated-artifact name** a workflow mentions (noise).

## Verification (all pass)

| Check | Result |
|---|---|
| Runs clean, writes both outputs | ✅ 979 docs, 2427 edges |
| Known hub correct | ✅ `rules/constitution.md` in=20 (the load-bearing rule) |
| Catches the stale `.agent/` (singular) refs from memory | ✅ 3 surfaced (`bmad-sm.md → .agent/gemini.md` + 2 ambiguous) |
| De-noised broken-path signal | ✅ 79 broken-path (was 208 raw) vs 431 bare-name folded into a collapsed count |
| Idempotent re-run | ✅ curated header preserved, only AUTO block + json change |
| Readable size | ✅ 22 KB md (was 483 KB before de-noising); full data in json |

**Real finds worth a look (report-only — nothing auto-fixed):**
- `opencode-agents/bmad-sm.md → .agent/gemini.md` — a genuine stale `.agent/` (singular) ref.
- `commands/1_update-maps.md` & `rules/prose-formatting.md → docs/repo-map.md` — home-base map is `_docs/repo-map.md`
  (these may be intentional *project*-relative refs; worth confirming).

## Decisions locked (from the plan)
- **D1** scope = `.agents/` only (`--root` configurable). · **D2** manual on-demand (no SessionStart nag yet).
  · **D3** master in `.agents/scripts/`, not vendored.

## Known limitations / future tweaks (v1 is report-only by design)
- Basename fallback can mask a wrong path-prefix when the filename also exists elsewhere — so a few `.agent/`
  refs land in *ambiguous* rather than *broken*. For an exhaustive `.agent/`-prefix sweep, grep is still cleaner.
- `bmad/` (vendored tree) dominates counts; run with `--ignore bmad` to focus on the hand-authored toolkit.
- No SessionStart drift hook yet (D2) — re-run manually after editing rules/workflows.

## Your Actions (git — I ran nothing per the never-commit policy)

Review, then from the home base:
```bash
git add .agents/scripts/generate_doc_graph.py _docs/doc-graph.md _docs/doc-graph.json _docs/repo-map.md _artifacts/_home/2026-06-26_doc-graph-extractor/ _artifacts/INDEX.md
git commit -m "feat(home): owned doc-wiring graph extractor for the .agents/ toolkit (the prose layer GitNexus misses)"
```
Optional next: decide the broken-path finds above; consider `--ignore bmad`; decide whether to promote a
`check-doc-graph-drift.ps1` SessionStart nag (D2).
