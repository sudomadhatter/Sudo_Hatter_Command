---
IsArtifact: true
ArtifactMetadata:
  title: Command-Center Workflow Memory and Graph Runtime
  type: implementation_plan
  date: 2026-08-07
---

# Command-Center Workflow Memory and Graph Runtime

## Goal and evidence

Give the command center the close-out discipline BMAD stories have without mixing their memory. Lobby work now
depends on manual artifact prose: `active-context.md` is 25,131 bytes (over 20 KB), duplicates historical
PICK UP/HAND OFF blocks, and has no lobby close-out or CI workflow. `doc-graph.json` is stale/report-only, while
epic kickoff records only P0-P3 and quick-dev classifies itself after implementation starts.

Use a deterministic adaptation of GraphRAG because workflow entities are already structured. Borrow durable
Task/Artifact semantics from A2A, a versioned refinement ledger from Prime Agent, and an attention inbox from
OpenWorker; import none of their runtimes. Markdown/git stay canonical; JSON/JSONL and Python provide compact
queries and checks.

## Target architecture

```text
approved command-center change
  -> deterministic close-out reads plan + walkthrough + diff + gate receipts
  -> append-only workflow event + recurrence fingerprint
  -> compact active-context projection / grep-only pitfalls / improvement candidate
  -> typed workflow graph build
  -> local-neighborhood query or quick/full route
  -> CI and staged checks prove graph, close-out receipt, skills and scripts agree
```

Rules/commands describe judgment; stdlib Python owns parsing, routing, state transitions, fingerprints,
budgets, graph generation and validation. No vendor runtime or automatic global rule mutation is added.

## Phase 1 — Two close-outs, no routine questions

1. Update `.agents/commands/sudo-update-sprint-memory.md` and
   `.agents/commands/sudo-merge-epic-workingtrees.md` to remove the unconditional manual-learnings question.
   Preserve their existing automatic learning routing, project `active-context.md` update/prune, red-test
   blocker, landing and cleanup behavior. Update `.agents/skills/sudo-update-sprint-memory/SKILL.md` to state
   that close-out applies without a final question.
2. Add lobby-only command/skill `sudo-update-command-center-memory`. It runs automatically after approved
   changes to rules, commands, skills, workflows, scripts, hooks, CI/CD, routing, or structure and never asks
   for “anything else.”
3. Add `.agents/scripts/command_center_closeout.py`. Inputs are the session plan/walkthrough and repository
   diff; optional improvement signals live inside the walkthrough, not a third session document. Atomically:
   - records a versioned event under `_artifacts/_main/workflow-events/YYYY-MM.jsonl`;
   - fingerprints retries, recurring file/command clusters, CI failures, drift and rule violations;
   - refreshes only live PICK UP/HAND OFF pointers in `_artifacts/_main/active-context.md` and enforces 20 KB;
   - routes long-tail failures to `_artifacts/_main/known-pitfalls.md`;
   - updates `improvement-candidates.json` with evidence, count, graph nodes, proposed target and rollback.
4. Promotion: occurrence 1 records evidence; 2 creates a candidate; 3 or post-fix regression becomes
   action-required. Never silently rewrite trusted rules. Failure under an existing rule recommends executable
   enforcement before more prose.
5. Anchor the automatic lobby close-out in root `AGENTS.md`, `.agents/AGENTS.md`,
   `.agents/rules/constitution.md`, `.agents/rules/artifacts-always-first.md`, and
   `docs/workspace-standard.md`; update indexes. Keep lobby and story launchers separate.

## Phase 2 — Typed workflow GraphRAG and early lane routing

1. Add compact command frontmatter: workflow id/kind, inputs, outputs, requires, next, ejects-to, guarded-by
   and surfaces. Markdown remains authoritative.
2. Add `.agents/scripts/workflow_graph.py` to build and query `docs/workflow-graph.json` and
   `docs/workflow-graph.md`. Node types: command, skill, rule, script, gate, artifact, surface, story lane,
   failure pattern and outcome. Edge types: invokes, requires, produces, next, ejects-to, touches,
   guarded-by, conflicts-with, failed-with and succeeded-with. Queries return a capped local neighborhood,
   not the whole toolkit. Retain `generate_doc_graph.py` for prose-link health; do not pretend it is runtime
   GraphRAG.
3. Add `.agents/scripts/workflow_router.py` with an explainable `quick|full` classifier. Hard-full surfaces:
   auth/tenancy, payments/PII, schema/security rules, migrations, deployment/CI, cross-boundary API/SSE,
   multi-service or irreversible changes. Unclear ACs, cross-stack scope, >3 files, >150 lines, or unknown also
   select full. P-level remains independent test risk.
4. Update `sudo-create-epic-sprint` command/skill to classify every story automatically during epic/story
   writing, record `lane=quick|full` plus reason in the board/test-design record, and route accordingly.
   Update `sudo-boot-sprint-memory` to honor it.
5. Repair `.agents/commands/sudo-quick-dev.md`: remove its illegal planning-gate bypass; distinguish a sprint
   quick story (epic worktree) from an ad-hoc quick fix (chore branch, no story/worktree); keep the runtime
   eject tripwire and eject before further implementation.

## Phase 3 — Executable enforcement, CI and propagation

1. Extend `workflow_lint.py`/`wf_common.py` with toolkit-only checks for typed metadata, edges, graph freshness,
   lane metadata, forbidden close-out questions, quick-dev/plan-law agreement, and staged close-out receipts.
2. Add tests: `test_command_center_closeout.py`, `test_workflow_graph.py`, and
   `test_workflow_router.py`; extend `test_workflow_lint.py` with positive and negative controls. Fixtures must
   prove recurrence thresholds, rollback, compact retrieval, hard-full rules, unknown->full, ejection, and
   stale graph/receipt failures.
3. Add `.github/workflows/toolkit-checks.yml` for pull requests and `main`: stdlib test suite, toolkit lint,
   map check, and graph freshness. The lobby currently has no independent CI gate.
4. Update `.agents/scripts/INDEX.md`, `.agents/commands/INDEX.md`, `.agents/skills/INDEX.md`,
   `docs/repo-map.md`, `docs/workspace-standard.md`, and the Fresh Workspace living-template front door where
   the structure contract requires. Run `/sync-agents` only after master files are green; never hand-edit
   mirrors.
5. Forward-test the revised close-out, epic kickoff and quick-dev skills with fresh subagents using raw
   fixtures, then run the routing canary on each supported surface.

## Verification

```bash
python3 .agents/scripts/tests/run_all.py
python3 .agents/scripts/workflow_lint.py --toolkit-only
python3 .agents/scripts/workflow_graph.py build --check
python3 .agents/scripts/check_maps.py --root .
pwsh .agents/scripts/sync-agents.ps1 -WhatIf
```

Also run temp-repo close-out/rollback/receipt fixtures; route quick, protected and ambiguous fixtures; prove
byte-identical graph regeneration; inspect CI; run `/sync-agents`, maintained-workspace lint and the routing
canary.

## Boundaries and implementation prerequisites

- Do not install or vendor OpenWorker, Prime Agent, Microsoft GraphRAG, or an A2A server in this phase.
- Do not store full transcripts or model reasoning; store evidence pointers, outcomes and fingerprints.
- Existing unrelated dirty files remain untouched and must never be swept into this change.
- Before implementation, resolve an SCC Jira key and create the required `chore/SCC-…` branch off `main`.
  The current shared checkout is dirty on `main`; implementation must wait until that can be done without
  stashing, reverting or absorbing another lane's work.
- Material scope expansion requires a revised plan.

## Research references

- Microsoft GraphRAG: https://github.com/microsoft/graphrag
- A2A task/artifact reliability: https://a2a-protocol.org/latest/specification/
- Prime Agent architecture/refinement: https://github.com/PrimeIntellect-ai/prime-agent
- OpenWorker risk/inbox patterns: https://github.com/andrewyng/openworker
