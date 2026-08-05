---
name: autopilot-manual-takeover-check-liveness
description: "Before/while manually finishing a crashed autopilot story, repeatedly verify no orchestrator is alive — resumes relaunch mid-cleanup and overwrite run-folder files; two lanes CAN converge if code is final"
metadata: 
  node_type: memory
  type: project
  originSessionId: 30de0369-2770-48ff-bef5-20f81142fc67
---

During the 8.22.2 manual takeover (2026-07-04), the "crashed" autopilot came back TWICE while the
manual /sudo-dev-story-tests lane was mid-cleanup: killing the orchestrator PID tree wasn't final
(a fresh `autopilot-dev-story.ps1` resume launched minutes later from another terminal) and it
overwrote `_RUN-STATUS.md` twice and wrote its own `walkthrough.md`/`code-review.md`.

**Why:** the run folder is the autopilot's state machine — any live orchestrator treats missing
stage artifacts as "mine to write". A manual lane writing the same files is a silent two-writer race.

**How to apply:**
- Before writing into a run folder, check `_RUN-STATUS.md`'s `Orchestrator PID` AND `Get-Process` it;
  re-check after long waits (suite runs) — the PID line changing = a new resume is live.
- Kill the WHOLE chain (`taskkill /PID <pid> /T /F`) and note the parent may be a terminal that
  relaunches; verify nothing respawns before proceeding.
- If a resume slips through anyway, don't panic-kill: diff what it wrote. In the 8.22.2 case the
  lanes CONVERGED (code untouched, my consolidated test file adopted by its stage 3/4, its review
  verdict PASS) — reconcile artifacts instead of redoing work.
- **QA'ing a suspected two-lane story after the fact (17.7, 2026-07-13):** the tell is an
  ARTIFACT-VS-TREE COUNT MISMATCH, not merge conflicts. Product code converged to one coherent
  implementation, but a last-writer-wins overwrite of `test_admin_dashboard.py` silently dropped
  lane B's 2 R-1 coercion tests — story record said "47 passed"/singular test while the ③ review +
  automation summary said "49"/"+2". Method: cross-diff every artifact's claimed File-List/test-list
  against the tree, grep for the named tests, then RUN the gate suite for the true count; restore
  from the automation summary's spec (it documents each test's name + non-vacuity property).
- Related: [[autopilot-has-three-drifting-engines]], [[autopilot-glm-hybrid-lane]].
