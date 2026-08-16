# Walkthrough — SCC-164 second half · the gate cluster

review-runtime: inline

**What changed, in one line:** the five parts SCC-164 declared but did not build — the PC token path,
the three main-gate fail-opens, the post-merge tick, the `reset --hard` remedy, and the unenforced
blind review — are built, and SCC-164 closes.

---

## Step 0 — the probe, recorded before any code (Rule 3)

`review-runtime: inline`. This session carries a standing directive that the subagent tool is not to
be used, so fan-out is **unavailable**, not merely unchosen. Under Part I's contract that makes
`recovered-inline` the only legal per-lens state for this lane. The lane is therefore the first live
fixture of the parser it builds.

## Step 0.7 — re-derivation against SCC-183

Recorded in full in [`implementation_plan.md`](implementation_plan.md) § *What SCC-183 changed, part
by part*. Three lines, as Part E7 requires:

1. **What moved:** SCC-183 (PR #11 `819f981`, PR #12 `bc3a851`) deleted the lobby's local
   merge-to-main road and replaced it with a pull request the operator clicks.
2. **What that changes for this lane:** nothing dissolved. C and D lose their lobby *stakes* (no
   lobby command merges locally any more) but keep their live blast radius — `/cicd-push-e2e` in
   project repos, and the PC. G gains a second defect: the door now contradicts itself.
3. **What was re-measured:** the door's Step 4 tick instruction (`:493-498`), the `/cicd-push-e2e`
   carve-out in `test_door_preflight_order.py:284-290`, and the lobby-vs-AGY diff on all four gate
   files.

---

## Build log

*(filled as each part lands — artifact-first, Rule 2)*
