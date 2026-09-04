# Run A3 — incumbent `bmad-code-review` (tie-break round)

Layers: 4/4 ok. Vendor triage: 38 raw → 27 unique.

**Summary: 2 decision-needed · 20 patch · 5 defer · 0 dismissed.**

Highlights (same core set as A1/A2): flag/script tracking-state family (blind found the
disk-vs-index mirror: flag rm'd from disk, hook reads disk, scan reads index) · NOT CLEAR branch
unreachable · D/F/N Windows reds · pathspec `.githooks/*` false-block · AC6 --global spec drift
(+ case B assertion can't prove the remedy prints) · nt-branch / CLI-exit+--json / git_root /
absolute-hooksPath test gaps · N+1 "(None)" · non-repo misdiagnosis · `~` expansion · git-absent
crash · Q hardcoded expect-key · touch remedy on Windows · INDEX hygiene · SOP census (defer) ·
AC3 invariant (defer) · closeout-preflight bare (defer) · 59vs58 (defer) · AC7 15/15 (defer) ·
AC4 fixture e2e gap.

New-in-A3 unique rows: ARM_FLAGS subset-skip path untested (partial-gate repo fixture missing);
claims_gates gate-scripts-only OR-arm unasserted; AC7 15/15-vs-16/16 pinned-count row.
Decision rows this round: claims_gates filesystem-vs-index policy; CLI-vs-check severity split.
(Live-repo suite coupling did NOT recur in A3's draws — recorded for the overlap table.)

Full raw lens outputs: this trial's git history (commit body of this run) + orchestrator log.
Trial containment: findings are evidence, not fixes.
