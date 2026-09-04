# Run B3 — house `code-review-engine` (tie-break round, pack-primed)

Caller contract identical to B1/B2 (pack hash-verified = frozen). Step-01: 4/4 lenses ok.
Step-02: pass-through (SCC-127 pending). Step-03: 39 raw → 27 unique.

**Summary: 3 decision · 20 patch · 4 defer (0 dismissed) · severity_floor: CONCERNS.**

Same core set as every prior run (tracking-state vacuous-ARMED family · NOT CLEAR unreachable ·
D/F/N Windows · pathspec false-block · AC6 --global drift · N+1 "(None)" · non-repo misdiagnosis ·
`~` expansion · test-tier gaps: nt branch, CLI exits, --json, git_root · AC3/59-vs-58/AC7/SOP-census
defers · claims_gates-filesystem + live-repo-coupling + CLI-vs-check decisions).

New unique angles this round:
- **Verdict/exit-code mismatch if NOT CLEAR ever becomes reachable** — the branch prints a failure
  verdict while `rep.exit_code()` can return 0/1; automation reads success (edge).
- **"GATES: NOT ARMED" line prints directly above "clear to close out and merge"** for
  never-claimed repos — mixed signals on the surface this ticket exists to disambiguate (blind).
- **scan() early-return on empty `expected` suppresses layers 2–3** and empties the JSON
  inventories (blind; last seen in A1, missed by all of round 2).
- **Test L's first assertion verbatim-duplicates test P's** (blind).
- **hooksPath configured-but-nonexistent error branch untested** alongside the absolute-path
  branch (test).

notes: verification pass not yet installed (SCC-127); EVIDENCE_PACK supplied, hash-verified;
DEFERRED_WORK absent — defer bullets: AC3 row drift · 59-vs-58 contradiction · SOP census ·
AC7 pinned count. Trial containment: findings are evidence, not fixes.
