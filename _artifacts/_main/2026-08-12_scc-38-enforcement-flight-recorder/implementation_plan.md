---
IsArtifact: true
ArtifactMetadata:
  title: SCC-38 executable enforcement + flight recorder (Prime Agent features, house-translated)
  type: implementation_plan
  date: 2026-08-12
---

# SCC-38 — Executable enforcement, flight recorder, CI (Prime-Agent features, house terms)

## Goal and evidence

Execute the surviving scope of `_artifacts/_main/2026-08-07_command-center-workflow-memory/
implementation_plan.md` (canonical; the `_my_resources/open_tasks/proposal_graphrag_executiblity.md`
copy becomes a pointer), re-centered on the operator's stated value (2026-08-12): **executable
enforcement for workflows, commands and rules** — scripts that fail, not prose that asks.

Source repo read in full this session (PrimeIntellect-ai/prime-agent @ `a3b3e75`, 2026-08-12):
it is a coding-agent *product*, not an importable framework — we vendor nothing and port four
designs: the refinement ledger schema (`src/core/refinement/refinement.ts` — events carry
`trigger/changes/evidence/outcome` + `expectedOutcome`, versioned entries, rollback), the
executable-skills philosophy (the skill IS code; markdown is discovery), the autonomous gate loop
(`--autonomous-gate`: a session cannot finish until its gate command exits 0; skip-if-unchanged),
and mutation idempotency journaling (repeated command returns its recorded result; uncertain ≠
replay). "Graph Engineering" does not exist in prime-agent (verified) — the graph here is scoped
to enforcement only.

Current-state evidence (verified 2026-08-12): no `.github/workflows/` (lobby has NO
machine-independent gate; hooks are per-machine — multiple dev machines = multiple chances for
silently-off gates); lobby `active-context.md` = 20,835 B (over the 20 KB budget today);
`workflow_graph.py` / `workflow_router.py` / `command_center_closeout.py` do not exist; the
manual-learnings question still sits in both close-outs (`cicd-update-sprint-memory.md:224`,
`cicd-merge-epic-workingtrees.md:120`).

**Operator rulings (2026-08-12):** graph = drift-lint only, no query surface · quick|full router
CUT to a future ticket · agent *messaging* dropped (runtime-bound); the gate loop + idempotency
are its cash-out · retries must be FRESH-context, seeded with already-paid artifacts, engine-owned
(never agent-spawned), hard-bounded · speed of the daily loop is inviolable.

## Target architecture

```text
command/skill/rule edit
  -> typed frontmatter (id, kind, inputs, next, ejects-to, guarded-by, surfaces)
  -> workflow_graph.py build --check     # drift lint: edges must agree with reality
  -> workflow_lint relationship checks   # dangling next:, AP-twin drift, unenforced "enforcement"
  -> run_all.py suite                    # local gate (per machine)
  -> .github/workflows/toolkit-checks    # the SAME suite, machine-independent (the backstop)

approved lobby change lands
  -> smh-update-command-center-memory (the close-out door invokes command_center_closeout.py)
  -> append-only event: trigger/changes/evidence/outcome + expectedOutcome @ SHA
  -> recurrence fingerprints -> promotion ladder -> "commission the script" recommendations at boot
```

Stdlib Python owns parsing, state, fingerprints, graph build, validation. Markdown/git stay
canonical. No vendor runtime. Never silently rewrite trusted rules.

## Subtasks (sequential, AFTER SCC-116 lands; each = `chore/<KEY>-<slug>` off main)

### SCC-130 — Currency pass (cheap, first)
Reconcile the 08-07 plan against current main: translate pre-SCC-63 names
(`sudo-update-sprint-memory`→`cicd-update-sprint-memory`, etc.; new close-out is
`smh-update-command-center-memory` per the SCC-63 translation note); STRIKE what already shipped
(quick-dev repair = done; the file-local enforcement layer = done: workflow_lint 480 lines,
16 test files, armed hooks, sop_currency, preflights, hooks_armed, door parity). Record the cuts
in the plan: agent messaging OUT · router CUT. Mark this folder's plan canonical; reduce the
open_tasks proposal copy to a pointer. Output: a strike-through-annotated copy + scope deltas
folded back into THIS plan if material.

### SCC-131 — Enforcement core (the payload)
1. Compact typed frontmatter on `.agents/commands/*` + hand-authored skills: workflow id/kind,
   inputs, outputs, next, ejects-to, surfaces, and **`guarded-by: <script>`** on every rule/command
   that claims mechanical enforcement.
2. `.agents/scripts/workflow_graph.py` — build `docs/workflow-graph.json` + `build --check`
   freshness/consistency gate. **Drift lint ONLY** — no query surface (operator ruling; revisit if
   the toolkit triples). `generate_doc_graph.py` stays what it is (prose-link health).
3. `workflow_lint.py`/`wf_common.py` relationship checks (the classes file-local greps can't see —
   two standing scars prove it): dangling `next:`/`ejects-to:` to retired names · `-AP` twin drift
   on shared content · a command claiming a gate it never invokes · **a rule with `guarded-by`
   pointing at a script that does not exist or has no test** · frontmatter/graph disagreement.
4. Tests with positive AND negative controls (a check that cannot fail is a finding).
Permanent tax accepted by the operator: new commands owe frontmatter or the lint fails — that tax
IS the consistency.

### SCC-132 — Lobby CI (the backstop that travels)
`.github/workflows/toolkit-checks.yml` on PRs + `main`: `run_all.py`, `workflow_lint.py
--toolkit-only`, `check_maps.py`, `workflow_graph.py build --check`. Rationale recorded in the
workflow file header: local gates are `core.hooksPath`-armed per machine; a fresh clone has none;
CI is the only machine-independent floor. Constraints: **gates pushes/PRs only — never local
work**; stdlib-only (no pip installs), so it runs in seconds and never flakes on dependencies.

### SCC-133 — Flight recorder (script-tracked, not agent-scraped)
1. `.agents/scripts/command_center_closeout.py` — deterministic close-out core. Atomically:
   append event to `_artifacts/_main/workflow-events/YYYY-MM.jsonl` (schema per prime-agent:
   `trigger`, `changes[]`, `evidence`, `outcome`, `expectedOutcome`, SHA, gate receipts);
   fingerprint recurrences (retries, file/command clusters, gate failures, drift); refresh live
   PICK UP/HAND OFF pointers in lobby `active-context.md` and enforce 20 KB; route long-tail
   failures to known-pitfalls; update `improvement-candidates.json` (evidence, count, proposed
   target, rollback pointer = the git SHA — git supplies before/after for free).
2. Promotion ladder: 1 occurrence = evidence · 2 = candidate · 3 or post-fix regression =
   action-required, phrased as **"this prose rule failed N×  — commission the script"**
   (executable enforcement before more prose, never silent rule rewrites).
3. New `smh-update-command-center-memory` command + skill — **bound to the close-out door**
   (invoked by /smh-close-task-merge-tree as a step; "runs automatically" is prose that cannot
   execute). Idempotent: re-invocation with an already-recorded (SHA, task) returns the recorded
   event instead of double-writing (prime-agent journaling rule).
4. **Reader wiring or it's a write-only DB:** action-required candidates surface in
   /cicd-boot-sprint-memory and the SessionStart hook summary.
5. Learnings question in both existing close-outs becomes **conditional**: ask only when the
   session routed zero learnings automatically (operator's don't-slow-me-down mandate, without
   deleting the one guaranteed human-input hook).

### SCC-134 — Autopilot gate-loop spec (done-means-green, fresh eyes)
Update the lobby autopilot spec (engines are project-local; the spec is the propagation layer —
existing engine-drift debt carries the port):
1. **A stage cannot declare itself done until its gate script exits 0.** The gate is a script with
   an exit code — never the agent's self-assessment.
2. Red gate → **the ENGINE spawns a FRESH one-shot session** (never a continuation of the failed
   context — the operator's fresh-eyes rule, mechanized). The fresh session is seeded with
   everything already paid for, re-derived nothing: story file · `implementation_plan.md` · the
   diff · the failing gate's full output · the prior attempt's walkthrough/summary · gate receipts
   (`gate_receipt.py` output). 
3. **Loop guards are structural, not behavioral:** the retry counter lives in the engine script
   (deterministic, max 2 fresh retries); the spawned agent has NO authority or instruction path to
   spawn further retries; skip-if-unchanged (a failed gate is not re-run when the workspace hash
   is unchanged — pure credit burn); budget caps per stage; on exhaustion the engine **PARKS** with
   a receipt (gate output + attempts + SHAs) for the operator instead of thrashing.
4. Idempotent resume note: stage completion recorded by (stage, SHA) — re-runs return the record.

## Verification

```bash
python3 .agents/scripts/tests/run_all.py                       # incl. new suites w/ negative controls
python3 .agents/scripts/workflow_lint.py --toolkit-only        # relationship checks live
python3 .agents/scripts/workflow_graph.py build --check        # byte-identical regen, fresh
python3 .agents/scripts/check_maps.py --root .
```
Plus: CI green on a real PR; a seeded rule with a dangling `guarded-by` FAILS the lint (negative
control); a temp-repo close-out fixture proves event append + fingerprint promotion + 20 KB
enforcement + idempotent re-invocation; boot surfaces a seeded action-required candidate.

## Boundaries

- Vendor nothing (no prime-agent, GraphRAG, A2A, OpenWorker runtimes). No transcripts/reasoning
  stored — evidence pointers, outcomes, fingerprints only.
- No query/GraphRAG surface on the workflow graph. No quick|full router (future ticket).
- No agent-to-agent messaging runtime; SCC-134's gate loop + journaling is the adopted substitute.
- Sequential AFTER SCC-116 (shared files: workflow_lint, tests/, SOP doc, INDEX files).
- sop_currency fires on every usage-surface subtask — `workflows_testing_SOP.md` rides the same
  commit each time; `[sop-ok]` is not appropriate for any of these.
- Existing unrelated dirty files are never swept in; material scope expansion = revised plan.
