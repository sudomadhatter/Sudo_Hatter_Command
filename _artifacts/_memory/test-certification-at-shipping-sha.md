---
name: test-certification-at-shipping-sha
description: "The ②→③ full-suite handoff is now a typed contract (certification-<story>.json + Rule 4), not pasted prose; per-story floor is 2 full runs and xdist is the only lever left."
metadata: 
  node_type: memory
  type: project
  originSessionId: 188cc8d4-fd46-4a29-ada3-f8934ab750ee
  modified: 2026-08-04T01:16:16.975Z
---

Landed 2026-08-02 across the lobby + AGY / Fresh / NEXgen.

**The contract.** `tests-must-gate-for-real.md` **Rule 4** owns test certification: scoped/blast-radius runs are *feedback*; the full suite is *certification* and runs exactly once, at the shipping SHA — **after** `bmad-testarch-automate`, never before it (expansion stales earlier totals). ② Step 4.5 emits `_bmad-output/test-artifacts/certification-<story>.json` (`{story, sha, utc, stacks:{<stack>:{cmd, passed, skipped, failed, seconds}}}`); ③ Step 3 compares its `sha` to `git rev-parse HEAD` — match + `failed: 0` → inherit; absent / mismatched / missing stack / any failure → run the full suite. ③ refreshes the JSON to its own SHA after its final run. Artifact/doc-only commits don't void a pair. Headless `_AP` lanes carry Rule 4 but emit **no** JSON by design — the orchestrator gates on its own independent run.

**Numbers worth keeping (AGY, story 21.8b).** One full backend suite = **278 s serial**. ③ must re-run the full suite whenever it changes anything (in 21.8b it added 11 tests), so the **per-story floor is 2 full runs ≈ 9.3 min** — reordering cannot go below it. Per story ②+③ went ~17 min → ~11 min.

**Why:** the old ordering cost one extra full run per story, every story. But the audit also corrected the research that proposed the fix — its headline "③'s inheritance is silently dead, 0% hit-rate" was contradicted by the very walkthrough it cited (③ *did* inherit; the agent had paid a second run in ② to make the pair valid). **Read the baseline artifact, never the plan's summary of it.**

**How to apply:** more than one mandated full-suite run in ② is a defect against the command, not a retro note. The ~9.3 min floor was cut by the 2026-08-03 flip to parallel gates (`-n auto --dist loadfile`): the full suite now runs ~206–286 s instead of ~278 s serial at 3000+ tests, and scales with cores — see [[agy-canonical-test-venv]] · [[governance-gate-scans-venv]]. Related: [[sudo-commands-have-ap-twins-that-drift]], [[source-grep-guards-cannot-see-order]], [[agy-canonical-test-venv]].
