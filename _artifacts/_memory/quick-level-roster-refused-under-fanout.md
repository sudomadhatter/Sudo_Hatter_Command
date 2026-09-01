---
name: quick-level-roster-refused-under-fanout
description: "walkthrough_roster.py refuses ANY n/a lens under a fan-out header — the SCC-232 quick level's \"skipped-by-mode\" rows cannot pass close-out; verify with --gate at review time, not close-out."
metadata: 
  node_type: memory
  type: project
  originSessionId: c33ae508-bf38-4af6-b51d-7fce58c51203
  modified: 2026-08-31T23:01:28.826Z
---

**The mismatch (found 2026-08-31, AVCH-101 re-review):** the engine's SCC-232 contract says a
quick-level review records its three skipped lenses on `lenses_na` as `n/a — skipped-by-mode
(level: quick)`. But `walkthrough_roster.py --gate` refuses ANY `n/a` row under
`review-runtime: fan-out` ("a dropped lens is legal only under `inline`") — it has no
skipped-by-mode carve-out. So every quick-level story review written to contract is refused at
close-out. AVCH-101's first ③ hit exactly this; the team ran the script bare (which passes —
"roster reads") and never ran `--gate`.

**Why:** the gate script predates or never absorbed SCC-232's two-level roster; bare mode checks
readability only, `--gate` checks legality.

**How to apply:** after writing any ③ verdict, run `walkthrough_roster.py <walkthrough> --gate
--verdict <V>` in the same session — never only the bare form. If a quick-level review is
genuinely wanted, know its roster will be refused until the script grows a skipped-by-mode
carve-out (a lobby fix, SCC-keyed — not fixable from a project lane). Practical workaround: run
the full standard roster (which is usually what the radius demanded anyway — [[audit-findings-need-a-file-anchor]]).
Related: a walkthrough with TWO `Verdict:` stamps resolves differently in the two readers —
`--gate` judges the LAST, `closeout_preflight` reads the FIRST — so neutralize a superseded
stamp's `Verdict:` prefix when re-reviewing.
