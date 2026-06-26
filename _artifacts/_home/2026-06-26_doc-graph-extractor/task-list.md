# Task List — Doc-Wiring Graph Extractor

- [x] Confirm the gap & approach (GitNexus blind to doc refs; build owned vs adopt graphify) — approved
- [x] Ground the parser in real link syntaxes (backtick refs 100+, md links 43+, wikilinks 0)
- [x] Write `.agents/scripts/generate_doc_graph.py` (mirror `generate_repo_map.py` conventions)
- [x] Run → produce `_docs/doc-graph.md` + `_docs/doc-graph.json`
- [x] Verify: known hub (constitution in=20), `.agent/` stale refs caught, idempotent re-run
- [x] De-noise dangling (broken-path vs bare-name) + ambiguous (drop generic basenames) + cap report
- [x] Add 1-line pointer in `_docs/repo-map.md` curated header
- [x] Write walkthrough.md + task-list.md; append `_artifacts/INDEX.md` row
- [ ] **Daniel:** review broken-path finds; commit (cmd in walkthrough)
- [ ] **Optional:** `--ignore bmad` for a toolkit-only view; decide SessionStart drift nag (D2)
