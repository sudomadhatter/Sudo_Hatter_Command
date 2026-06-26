# implementation_plan.md — autopilot_opencode

> **Scope:** build the opencode-native autopilot dev-story loop in `Projects/aviationChat-AGY`.
> Worked **from the home base** (cwd = `C:\Sudo_Hatter_Command`), so this planning artifact lives at the
> home base under `_artifacts/opencode/aviationChat-AGY/`. The *run* artifacts produced when
> `autopilot_opencode` later executes against a story stay **project-local** at
> `Projects/aviationChat-AGY/_artifacts/<YYYY-MM-DD>_autopilot-<story>/` (per that project's AGENTS.md §5
> — project-local, travels with the repo).

---

## 1. Outcome (what "done" looks like)

A working `/autopilot_opencode <story>` command in aviationChat-AGY that takes a BMAD story from
`ready-for-dev` to `review` (never `done`) through a 4-stage relay, fully autonomously — no mid-loop
approval prompts. The primary opencode session (whatever model Daniel is chatting in) drives Stages 1
and 3 inline; Stage 2 (audit) and Stage 4 (review+fix) run as Task subagents with clean child-session
context. Stage 2 defaults to Claude Opus 4.8; Stage 4 defaults to the session model. Both are swappable
by editing one `model:` line in the agent frontmatter.

On a clean run: story auto-flips to `review` (story `.md` + `sprint-status.yaml`), artifacts land in the
canonical run folder, `_RUN-STATUS.md` stamps `COMPLETE`. Daniel comes back, reads the artifacts, runs
`/update-sprint-context` to close.

## 2. Architecture decision (locked)

In-process orchestration via opencode's native subagent primitive (Option A from the brainstorm). No
PowerShell engine, no headless `opencode run` subprocesses, no telemetry adapter. The primary session
is the orchestrator (LLM-as-control-flow for simple verdict branching only — the tax is small and
acceptable).

**Why not headless subprocesses (Option B):** would re-earn every resilience bug the Claude engine
already fixed (~1000-line script + telemetry adapter), cold-starts every stage (~$0.40 floor × 4),
and fights opencode's native subagent design. The subagent primitive already gives clean-context
child sessions + per-agent model pinning for free.

## 3. The 4-stage relay

| Stage | What | Default model | Swappable | Mechanism | Artifact |
|---|---|---|---|---|---|
| 1 Plan | plan the story | session model | n/a (it's the chat) | primary agent inline | `implementation_plan.md` |
| 2 Audit | pre-dev adversarial audit of the plan | Claude Opus 4.8 | yes — edit `model:` line | `autopilot-auditor` subagent (Task = clean child session) | `self-audit-stress-test.md` |
| 3 Implement | apply audit fixes, develop, test | session model | n/a | primary agent inline (context carries from S1) | code + `walkthrough.md` |
| 4 Review+Fix | clean-context review, apply fixes, retest | session model | yes — add a `model:` line to override | `autopilot-reviewer` subagent (Task = clean child session) | `code-review.md` + prepended walkthrough sections |

**Swap mechanics (the thing Daniel asked about):**
- Dev legs (S1, S3): no action. They're his session model. Change chat model → dev model changes.
- Audit (S2): edit `model:` line in `autopilot-auditor.md`. Default `openrouter/anthropic/claude-opus-4.8`.
- Review+Fix (S4): by default NO `model:` line → inherits the session model. Add a `model:` line to pin
  (e.g. to Claude for a hard review). Documented at the top of the agent file.

## 4. Autonomy model (Daniel's "don't ask me anything")

- **No approval gate at Stage 2→3.** Auditor's `Go` → proceed. `NEEDS-REVISION` → primary applies
  fixes inline, re-runs audit (max 2 retries), then proceeds. No "approved" prompt.
- **No `decision_needed` halts at Stage 4.** Reviewer makes judgment calls, applies fixes, documents
  every call under OUT-OF-SPEC DECISIONS + OPEN QUESTIONS at the top of `walkthrough.md`. Never stops
  to ask.
- **Only a genuine PIPELINE_BLOCKER pauses** (contradictory ACs, missing dependency — truly
  unresolvable). Stamps `PAUSED - NEEDS DANIEL`. Rare.
- **Green test gate:** auto-flip story to `review` (both story `.md` + `sprint-status.yaml`), never
  `done`. Best-effort (a flip hiccup warns, never crashes a finished run).
- **Red test gate:** leave story at `in-progress`, stamp `TESTS RED` in `_RUN-STATUS.md` + the
  walkthrough, park the work on disk. Daniel investigates, then re-runs or fixes manually.
- **Never `git commit`/`push`, never marks `done`.** Same guardrails as the Claude engine.

## 5. Artifact handoff folder (the communication backbone)

One canonical folder per run, mirroring `/autopilot_claude`'s proven contract so the pattern and
`INDEX.md` ledgering are identical:

```
_artifacts/<YYYY-MM-DD>_autopilot-<story>/          (project-local in aviationChat-AGY)
+-- implementation_plan.md      <- S1 (primary)
+-- self-audit-stress-test.md   <- S2 (auditor) -- findings + fixes
+-- walkthrough.md              <- S3 (primary) -- S4 prepends QA CLOSE-OUT + OUT-OF-SPEC + OPEN QUESTIONS
+-- code-review.md              <- S4 (reviewer) -- REQUIRED even on clean APPROVE
+-- decisions-log.md           <- any stage (story-silent calls)
+-- _RUN-STATUS.md             <- re-stamped per stage (IN PROGRESS / COMPLETE / PAUSED / TESTS RED)
+-- _pipeline/run.log          <- self-contained transcript
```

The artifact-presence map **is** the resume logic: `1=implementation_plan.md`,
`2=self-audit-stress-test.md`, `3=walkthrough.md`, `4=code-review.md`. A re-entry after a crash skips
stages whose artifact exists. **After each stage, the primary verifies the artifact landed in this
folder before proceeding** — the "agents use these for communicating" check.

QA owns the last mile: Stage 4 prepends two sections to the TOP of `walkthrough.md`:
- `## OUT-OF-SPEC DECISIONS (QA judgment calls - your review)` — every call the team made that the
  story didn't cover.
- `## OPEN QUESTIONS FOR DANIEL` — anything genuinely unresolved. The reviewer is *allowed to ask*
  here rather than forcing everything into a blocker.

## 6. Files to create/modify (all in aviationChat-AGY, all non-destructive)

1. **`.opencode/commands/autopilot_opencode.md`** — replace the current stub. Command body drives the
   4 stages: primary does S1/S3 inline, spawns subagents for S2/S4, branches on verdict, enforces
   artifact-presence gates, writes `_RUN-STATUS.md` per stage, creates a live TodoWrite list mirroring
   the pipeline.

2. **`.opencode/agent/autopilot-auditor.md`** — NEW file (leave `opus-auditor.md` untouched). Model-
   agnostic; `model: openrouter/anthropic/claude-opus-4.8` default (the swap point, documented at
   top). Read-only on source, write-only `self-audit-stress-test.md` to the run folder. Returns
   verdict (`Go`/`NEEDS-REVISION`/`UNSAFE`) + path + finding counts.

3. **`.opencode/agent/autopilot-reviewer.md`** — NEW file (leave `opus-reviewer.md` untouched). No
   `model:` line by default → inherits session model; add a line to swap. **Key difference from
   `opus-reviewer`: this one applies fixes itself** (edit permission on source + tests, runs suites
   after fixing, writes `code-review.md` even on clean APPROVE, prepends QA CLOSE-OUT to
   `walkthrough.md`). Clean context via Task child session.

4. **`.agents/workflows/autopilot_opencode.md`** — NEW reference doc (sibling to
   `autopilot_bmad_dev_loop.md`): the 4-stage relay, the swap mechanism, the artifact contract, the
   autonomy model, the resilience model.

5. **Constitution carve-out** — add a loop-only exception to
   `.agents/rules/constitution.md` (or a project-local `constitution.project.md`): within
   `autopilot_opencode`, the auditor `Go` verdict substitutes for the manual approval gate, and
   `decision_needed` findings do NOT halt (reviewer adjudicates and documents). All other hard stops
   remain in force.

## 7. Verification plan (after implementation)

- **ASCII + parse check** on the command + agent markdown files (no `.ps1`, but keep the discipline
  for frontmatter).
- **No-story invocation:** `/autopilot_opencode` with empty args → confirm it prompts for a story and
  stops.
- **Cheap trial:** plan+audit only (Stage 1→2) on a small story to prove the auditor subagent fires,
  the artifact lands in the canonical folder, and `_RUN-STATUS.md` stamps correctly.
- **Full trial:** one complete 4-stage run on a small story to prove the reviewer applies fixes, the
  test gate runs, and the story parks at `review`.

## 8. Out of scope (deliberately)

- No PowerShell engine, no headless `opencode run` subprocesses, no telemetry adapter.
- No runtime `-DevModel`/`-AuditModel` CLI flags (swap = one-line frontmatter edit, on Daniel's terms).
- No git commit/push, never flips to `done`.
- Leaves existing `opus-auditor.md`/`opus-reviewer.md` untouched (orphaned by the archived loop,
  non-destructive).
- No propagation to other projects (clean-bmad-workspace, home base) in this pass — build + prove in
  aviationChat-AGY first; sync later via the existing `.agents/` re-sync.

## 9. Risk callout

- **LLM-as-orchestrator.** The primary session drives stage transitions + verdict branching. If the
  session model is tired or weak, it can mis-route a stage. Mitigation: the control flow is simple
  (if verdict == "Go" proceed), the artifact-presence gate is the real authority (a stage is "done"
  iff its artifact lands on disk, not because the model said so), and a crashed run is resumable by
  re-entering and skipping stages whose artifact exists.
- **opencode Task subagent context isolation** is documented but not yet proven on this specific
  project's agents. The cheap trial (Stage 1→2) is the proof point — if the auditor's child session
  can't read the run folder, we'll catch it there before a full run.
