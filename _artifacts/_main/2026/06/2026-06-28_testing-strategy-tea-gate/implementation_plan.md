# Implementation Plan — Bulletproof Testing Strategy (TEA Gate)

**Date:** 2026-06-28
**Scope:** Home-base / toolkit-wide (`.agents/commands/`, `.agents/skills/bmad-code-review/`) + AviationChat reference tests
**Source of intent:** `_my_resources/open_tasks/testing_strategy_e2e.md` + brainstorm session

**Decisions locked (Daniel):**
- Toolkit-wide rollout; pragmatic L1–L3 (defer shadow/Istio/RLHF infra).
- The `sudo-` commands are **thin orchestrators that CALL existing TEA/BMAD workflows — we rewrite NO logic, only sequence it.**
- Flow = 4 `sudo-` commands. **No `/test-gate` and no `/qa-gate`** — the gate (suite + trace + nfr + test-review) is inlined directly into `sudo-code-review`.
- `sudo-write-story-tests` = `bmad-create-story` → `bmad-testarch-atdd` (create the story, then write its failing tests).
- `sudo-dev-story-tests` auto-runs `sudo-self-audit` immediately after the plan is written.
- Renames: `update-sprint-context` → `sudo-update-sprint-memory`; `1_self-audit-stress-test` → `sudo-self-audit`.
- Rename + **enhance** `boot-sprint-context` → `sudo-boot-sprint-memory` (Daniel-authored, commit 6f05470 — not vendor). Becomes the story-level "pick up": reads `sprint-status.yaml`, surfaces the next story + which `sudo-` command to run next. Recommend NOT renaming the `_AP` variants.
- Opt-in safety: `sudo-code-review` reads `_bmad-output/sudo-tests.yaml`; absent → `WAIVED` (no block). Present → teeth, only on new/changed code.
- Build manual flow first; autopilot lanes (claude/mobile/opencode) second.

---

## Build status — Phase A COMPLETE (2026-06-28)
Done: 3 new commands (`sudo-write-story-tests`, `sudo-dev-story-tests`, `sudo-code-review`) · 3 renames (`sudo-self-audit`, `sudo-update-sprint-memory` +verdict-check, `sudo-boot-sprint-memory` +pick-up) · Test-Adequacy lens in `bmad-code-review/step-02` · all canonical references updated (human cmds only; `_AP` kept) · `/sync-agents` to lobby + AGY_AVIATIONCHAT + Fresh_Workspace_BMAD + global caches · 18 local ghost files purged · doc-graph regenerated. Verified: zero stray old-name refs in master; globals clean; 6 sudo skills resolve.

**Build-time findings:**
1. **`1_run-all-tests-back_front` KEPT (not retired)** — its referenced workflow file never existed; the command carries pytest+vitest inline, so it IS the muscle. `sudo-code-review` calls it.
2. **`/sync-agents` does NOT ghost-purge local `.claude`/`.opencode` command dirs** (only global caches + project `workflows/`). Renames leave local ghosts — purged manually this run. *Follow-up candidate:* teach sync to mirror-purge local command dirs too.

## Build status — Phase B COMPLETE (2026-06-28)
Done: renamed `_AP` commands → `sudo-self-audit_AP` · `sudo-code-review_AP` (added TEA gate) · `sudo-dev-story-tests_AP` (wove atdd→implement→automate) — authored + adversarially verified via workflow (3 author + 3 verify agents, all clean). Old `_AP` files deleted; all references updated (autopilot_claude/opencode, workflows + INDEX, opus agents, lobby + AGY diagrams). AGY + Fresh PS scripts repointed (4 string edits each) + stale `/1_ccps_update-active-context` close-out → `/sudo-update-sprint-memory`. AGY mobile `workflow.js` stage refs repointed (mobile inherits testing parity by deferring to the `_AP` commands). `autopilot_opencode` = stub (no wiring). Synced lobby + AGY + Fresh + globals; purged ALL stale command ghosts from `.agents`+`.claude`+`.opencode` (the `.agents/commands/` source was the re-propagation culprit); fixed 2 live AGY files (`constitution.project.md`, `active-context.md`); doc-graph regenerated; full-tree Bash-verify clean (only `_bmad/stories` + `_archive` + `sprint-status.yaml` provenance remains, correctly left).

**Phase B finding (memory `sync-leaves-local-command-ghosts` updated):** the ghost SOURCE is `Projects/*/.agents/commands/` — a project sync mirrors it to `.claude`/`.opencode`, so purging only those re-creates them next sync. Purge all three dirs; verify with Bash (not the Grep tool — it's blind to `Projects/`).

**Not yet done:** AviationChat opt-in (`sudo-tests.yaml` + L1/L2/L3 reference tests) · CI (`bmad-testarch-ci`). The flow (human + all agent lanes) is fully wired; turning the gate's teeth on for AviationChat is the remaining step.

## Design principle (load-bearing)
The gate **keys on opt-in**: no `_bmad-output/sudo-tests.yaml` → `WAIVED` (today's behavior). Baseline present → teeth, and only on NEW/changed code (legacy red is grandfathered via the baseline-diff the autopilots already do). This makes BOTH the toolkit-wide rollout AND the 1.8M-line retrofit safe.

Pyramid: **L1** mocked-unit (routing/SAR telemetry/SSE/citation plumbing, real coverage) · **L2** temp-0 + JSON-schema · **L3** LLM-as-judge soft assertions (**the only net-new harness, in AviationChat**) · L4 = Daniel at close-out.

---

## The flow — 4 `sudo-` commands, run in sequence

```
EPIC SETUP (once per epic)
  bmad-sprint-planning ─► create-epics-and-stories ─► bmad-testarch-test-design (risk-score P0–P3)

PER STORY (run by hand, mirrors autopilot stages)
  ① sudo-write-story-tests   → bmad-create-story ─► bmad-testarch-atdd                [story + FAILING tests first]
  ② sudo-dev-story-tests     → bmad-dev-story(plan) ─► sudo-self-audit ─► bmad-dev-story(implement) ─► bmad-testarch-automate
  ③ sudo-code-review         → bmad-code-review ─► run suite ─► bmad-testarch-trace ─► nfr ─► test-review → VERDICT artifact
  ④ sudo-update-sprint-memory→ reads ③'s verdict, flips story→done, routes learnings, prunes active-context
       ╰─► git commit (Daniel)

PROJECT SETUP (once): bmad-testarch-framework (bench) · bmad-testarch-ci (CI gates)
SESSION BOOKENDS: sudo-boot-sprint-memory (open — story-level "pick up": sprint state + next story + next command) … sudo-update-sprint-memory (close)
```

---

## Command set after this work

| Command | Status | Calls / notes |
|---|---|---|
| `sudo-write-story-tests` | 🆕 | `bmad-create-story` → `bmad-testarch-atdd` |
| `sudo-self-audit` | ♻️ rename of `1_self-audit-stress-test` | unchanged behavior; called by `sudo-dev-story-tests` |
| `sudo-dev-story-tests` | 🆕 | `bmad-dev-story` (plan) → auto `sudo-self-audit` → `bmad-dev-story` (implement) → `bmad-testarch-automate` |
| `sudo-code-review` | 🆕 | `bmad-code-review` + run suite + `trace` + `nfr` + `test-review`; reads `sudo-tests.yaml`; writes verdict |
| `sudo-update-sprint-memory` | ♻️ rename of `update-sprint-context` | + verdict-check before done-flip; keeps all memory/prune jobs |
| `sudo-boot-sprint-memory` | ♻️ rename + enhance of `boot-sprint-context` | story-level "pick up": active-context + `sprint-status.yaml` + next story + next `sudo-` command |
| `bmad-code-review` (skill) | ✅ keep | review engine + new Test-Adequacy lens |
| `/test-gate`, `/qa-gate` | ❌ never built | folded into `sudo-code-review` |
| `1_run-all-tests-back_front` (command) | ✅ keep (build-time finding) | it IS the test muscle — its referenced workflow file never existed; the command carries pytest+vitest inline; `sudo-code-review` calls it |
| `..._AP` variants | ✅ unchanged | not renamed (agent-internal) |

---

## Work items — Phase A: Manual flow (do first)

### A1. `sudo-write-story-tests` (new)
Thin wrapper: `bmad-create-story` (create story file w/ ACs) → `bmad-testarch-atdd` (write failing acceptance tests from those ACs, staged before dev).

### A2. `sudo-self-audit` (rename of `1_self-audit-stress-test`)
Rename master file + frontmatter `description` + H1. Behavior unchanged. (Reference checklist below.)

### A3. `sudo-dev-story-tests` (new)
Thin wrapper: `bmad-dev-story` plan → **auto-invoke `sudo-self-audit`** → `bmad-dev-story` implement → `bmad-testarch-automate`.

### A4. `sudo-code-review` (new) — the gate lives here
Thin wrapper: `bmad-code-review` (+ Test-Adequacy lens) → read `_bmad-output/sudo-tests.yaml` (absent → `WAIVED`) → run suite (the `1_run-all-tests-back_front` muscle, baseline-diff aware) → `bmad-testarch-trace` → `bmad-testarch-nfr` → `bmad-testarch-test-review` → aggregate into **PASS/CONCERNS/FAIL/WAIVED** + write `_bmad-output/implementation-artifacts/sudo-code-review-<story>.md` (review + verdict + story id + HEAD ref for staleness). Config keys: `required_tiers · l1_coverage_min · agent_bearing · nfr · waive`.

### A5. `sudo-update-sprint-memory` (rename of `update-sprint-context`)
Rename master file + frontmatter + H1. Add: before `review→done`, read the `sudo-code-review` verdict — missing/stale/`FAIL` → don't flip (tell Daniel to run `sudo-code-review`); `CONCERNS` → flip+log; `PASS` → flip; `WAIVED` → unchanged; fail-open on gate error. Keep ALL existing jobs.

### A5b. `sudo-boot-sprint-memory` (rename + enhance of `boot-sprint-context`)
Rename master file + frontmatter + H1. **Keep** its current jobs (active-context brief, in-scope specs/invariants, guardrails). **Add** (read-only, then stop): read `_bmad-output/implementation-artifacts/sprint-status.yaml` → report story states (`ready-for-dev`/`in-progress`/`review`/`done`); surface the **next story** to start + its file under `_bmad/bmm/stories/`; and tell Daniel the next `sudo-` command ("story 11.16 ready → run `sudo-write-story-tests`"). Cross-check against live files; never edit. (Optional later: surface `test-artifacts/`/gate status per story.)

> **⛔ DO NOT touch the master "pick up" trigger.** "pick up" (defined in `AGENTS.md` §7 / `router.md` / `docs/workspace-standard.md`) is the home-base, model-agnostic continuity behavior for **all** work — code OR non-code (research, docs, routing). `sudo-boot-sprint-memory` is a NARROWER, BMAD-story/sprint-scoped command that lives ALONGSIDE it. This work edits NONE of the pick-up definition files. The "pick up for stories" framing is an analogy only — the two must stay separate.

### A6. Test-Adequacy lens
`.agents/skills/bmad-code-review/steps/step-02-review.md` (+`step-03-triage.md` if new category): 4th adversarial layer — deterministic logic mocked-unit-tested? generative output behind soft assertions not string-match? new agent behavior has an L3 judge case? Rides the synced skill → propagates everywhere.

### A7. Update the / commands — sync all surfaces  *(Daniel task: "update the /commands")*
`/sync-agents` mirrors master `.agents/commands/` to EVERY slash-command surface: local `.claude/` + `.opencode/`, the machine-global opencode + Antigravity caches, AND re-vendors into every `Projects/<name>/.agents/` + `.claude/` + `.opencode/` — **purging the renamed-command ghosts**. Then regenerate `docs/doc-graph`. This single step auto-propagates ALL command/skill changes (new + renamed) to all projects.

### A8. Per-project propagation  *(Daniel task: "make these same changes for all projects")*
**Command/skill changes propagate automatically** via A7's sync to all 4 projects (`AGY_AVIATIONCHAT`, `Fresh_Workspace_BMAD`, `Ingestion_pipeline_AvCh`, `OpenCode`) + the lobby. **Per-project residual = files sync does NOT overwrite** (edit by hand, Bash not Grep since `Projects/` is gitignored):
- **Autopilot engine scripts** referencing renamed commands (Phase B): lobby `scripts/autopilot-dev-story.ps1`; `AGY_AVIATIONCHAT/scripts/autopilot-dev-story.ps1` + `autopilot_mobile.workflow.js`; `Fresh_Workspace_BMAD/scripts/autopilot-dev-story.ps1`.
- Each project's `docs/doc-graph` regen if its docs name a renamed command.
- AviationChat only: author `sudo-tests.yaml` opt-in + the L1/L2/L3 reference tests.

---

## Rename-impact checklist (canonical files to hand-edit — NOT the sync outputs / history)

> Edit master `.agents/` + docs + `_my_resources/` only. `.claude/`, `.opencode/`, `Projects/**` are regenerated by `/sync-agents`. `_artifacts/**` is history — leave it. `docs/doc-graph.*` is regenerated.

**`update-sprint-context` → `sudo-update-sprint-memory`** (27 refs; canonical subset):
- `.agents/commands/update-sprint-context.md` (rename), `autopilot_claude.md`, `autopilot_mobile.md`, `bmad-code-review_AP.md`, `boot-sprint-context.md`, `commands/INDEX.md`
- `_my_resources/diagrams_guides/system/autopilot_bmad_dev_loop.md`

**`1_self-audit-stress-test` → `sudo-self-audit`** (39 refs; canonical subset):
- `.agents/commands/1_self-audit-stress-test.md` (rename), `autopilot_claude.md`, `autopilot_mobile.md`, `autopilot_opencode.md`, `bmad-code-review_AP.md`, `bmad-dev-story_AP.md`, `commands/INDEX.md`
- `.agents/workflows/autopilot_bmad_dev_loop.md`, `.agents/workflows/INDEX.md`
- `.agents/rules/artifacts-always-first.md`, `.agents/opencode-agents/opus-auditor.md`
- `_my_resources/diagrams_guides/system/autopilot_bmad_dev_loop.md`, `_artifacts/README.md` (flow desc, not history rows)

**`boot-sprint-context` → `sudo-boot-sprint-memory`** (17 refs; canonical subset):
- `.agents/commands/boot-sprint-context.md` (rename + enhance), the cross-reference inside `sudo-update-sprint-memory.md`, `commands/INDEX.md`

---

## Work items — Phase B: Autopilot lanes (do after manual flow proven)
Add the SAME TEA checks (`trace` + `nfr` + `test-review`) into each autopilot's existing review stage. No shared `/test-gate` command — the autopilot gates are separate code paths (PowerShell / workflow / opencode) and get the calls wired in directly.
- **`/autopilot_claude`** — gate in `scripts/autopilot-dev-story.ps1` (project-local, NOT synced → per-project edit, AviationChat first). Already baselines red + re-runs suites + flips→review. ADD the TEA trace/nfr verdict into that gate.
- **`/autopilot_mobile`** — gate in command **step 6 (synced markdown)**. ADD the TEA checks; preserve RUNNER-MISSING honesty (absent runner → CONCERNS/UNVERIFIED, never PASS).
- **`/autopilot_opencode`** — opencode-native lane; wire the TEA checks into its review (`opus-auditor`/`opus-reviewer`).
- Update the renamed-command references inside each autopilot's project-local script.

---

## AviationChat reference tests (proving ground — alongside Phase A opt-in)
`sudo-tests.yaml` opt-in. **L1 (pytest, mocked LLM):** Strategy-Roulette JIT injection on EVAL_INCORRECT; SAR negative-reward → correct tool ID (assert DB state); citation-interception plumbing. **L2:** structured-output JSON schema compliance. **L3 (judge):** zero-hallucination citation interception 100%; "never reveal the answer" frustrated-student; groundedness F1. Authored via `atdd`/`automate`.

## Retrofit strategy (1.8M-line backlog — do once)
1. `framework` + `ci` setup. 2. **System-level `test-design`** → P0–P3 risk map (highest-value single action; tells us WHERE to backfill). 3. Baseline-WAIVE gate ON (grandfather legacy red). 4. Backfill **P0 only**, top-down, time-boxed. 5. Below-P0 tested opportunistically when touched (boy-scout ratchet). No end date — stop the bleeding + harden crown jewels; steady-state flow ratchets the rest.

## Rollout order
Phase A: A1 → A2 → A3 → A4 → A5 → A6 → A7 (+A8 propagation) → AviationChat opt-in + L1 → first PASS/FAIL → add L2, L3. **Then** Phase B autopilots. *(Build-time correction: the `1_run-all-tests` command is KEPT, not retired — it's the inline muscle.)*

## Risk / verification
- Shared `.agents/` edits hit every project → mitigated by opt-in WAIVE + fail-open. Verify: no-baseline project runs all 4 `sudo-` commands exactly as today (all WAIVE). AviationChat w/ baseline + passing L1 → PASS, flips. Missing test → FAIL, flip blocked.
- Renames are wide (27 + 39 refs across 3 autopilot variants) → update all canonical refs + sync, or boot/autopilot close-out instructions break. This is the careful part.

## Out of scope (deferred)
Shadow testing, service-mesh mirroring, phantom registry, RLHF, Bazel/Nx TIA, full OpenTelemetry/Langfuse stack.
