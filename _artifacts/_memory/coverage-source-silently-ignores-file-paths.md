---
name: coverage-source-silently-ignores-file-paths
description: "coverage.py [tool.coverage.run] source takes DIRS/packages only — a single .py path there is silently ignored (module-not-imported warning, zero lines measured); single modules go in source_pkgs, and a pin that greps the config text is not a gate."
metadata: 
  node_type: memory
  type: reference
  originSessionId: d57e9da6-d3b3-4b3d-93ef-2bcf512c4037
  modified: 2026-07-21T01:19:58.321Z
---

**2026-07-20 (AGY story debug-1.5 ③ review).** Adding one module to the coverage scope,
`[tool.coverage.run] source = [..., "backend/services/profile_service.py"]`, measured **nothing**.
`source` accepts **directories and package names only**; a file path in it is accepted by the TOML
parser and then silently dropped. The only signal is a `CoverageWarning: Module ... was never imported
(module-not-imported)` buried in pytest's warnings summary, and the module is simply **absent from the
coverage table** — not 0%, absent. Correct form for a single module:

```toml
source      = ["backend/agents/specialist", "backend/routers"]   # dirs
source_pkgs = ["backend.services.profile_service"]               # dotted MODULE name
```

**Why it matters twice over:** the repo's coverage tripwire (`test_coverage_instrument.py`) asserted the
required entry was *present as a string in pyproject* — so it passed green through a full CI-parity run
while the P0 chokepoint it was pinning contributed zero statements to `--cov-fail-under`. A gate that
checks its own config is spelled correctly, not that the config does anything: the same vacuous-green
family as [[e2e-gate-fiction-test-guardrails]] and the `tests-must-gate-for-real` rule.

**How to apply:** when scoping coverage to a single module, use `source_pkgs` with a dotted name, never a
path in `source`. After ANY coverage-scope edit, confirm the module actually appears as a row in the
`term-missing` table and that no `module-not-imported` warning fired — the number moving is the proof, not
the config diff. When you pin config in a test, assert the config *resolves* (dir exists / module is
importable), not that a string is present, and verify the pin bites by breaking it once.
