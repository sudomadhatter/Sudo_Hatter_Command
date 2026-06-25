---
description: Autopilot Dev-Story Loop (v2) - autonomous dev/QA team in TWO continuous chats (Dev plans+implements, QA audits+reviews+fixes). Resilient (retries transient errors), resumable (just re-run; finished stages auto-detect), human-in-the-loop (never crashes on agent output). CLAUDE-ONLY (needs the claude CLI).
---

# /autopilot - Autonomous Story Pipeline (v2: two continuous teams)

> **CLAUDE-ONLY.** This drives headless `claude -p` subprocesses with exact `--model` pinning and
> session continuity (`--session-id` / `--resume`). It cannot run under Gemini/opencode and is
> intentionally NOT mirrored there.

Launch the autopilot pipeline for the story in `$ARGUMENTS` (a story id like `11.16`, or a path).

## What to do

1. Confirm a story identifier was provided in `$ARGUMENTS`. If empty, ask which story and stop.

2. **Create a live TodoWrite list mirroring the pipeline** so Daniel watches it advance in the panel.
   Items (trim to match `-MaxStage`): `Stage 1 - Plan (Dev)`, `Stage 2 - Audit (QA)`,
   `Stage 3 - Implement (Dev)`, `Stage 4 - Review+Fix (QA)`. Mark Stage 1 `in_progress`,
   the rest `pending`.

3. Run the orchestrator under the **Monitor** tool so each stage transition streams into the chat as
   a live notification (Monitor avoids the foreground timeout AND drives the todo updates below).
   Call Monitor with:

   - **command:** `LOG="_claude_artifacts/_autopilot-run.log"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/autopilot-dev-story.ps1 -Story $ARGUMENTS > "$LOG" 2>&1 & APID=$!; tail --pid=$APID -f -n +1 "$LOG" | grep --line-buffered -E ">>> STAGE|done in|PAUSED|TESTS|AUTOPILOT|Total cost|CRASHED|retrying|MODEL MISMATCH"`
   - **description:** `autopilot $ARGUMENTS - stage progress (tailing _autopilot-run.log)`
   - **persistent:** `true`  (tail exits when the script PID dies)

   This **tails a real log file** instead of piping the live PowerShell straight through `grep` (the old
   way swallowed every startup error and could make a healthy run look dead). The FULL transcript is
   always at `_claude_artifacts/_autopilot-run.log` — if the run errors before the first stage, read that
   log to see exactly why. The `grep` here only filters what STREAMS into the chat; the log keeps
   everything. Stage transitions still arrive as live notifications, so the TodoWrite updates below work
   exactly as before.

   For a cheap plan+audit trial, append `-MaxStage 2`. Model overrides: `-DevModel`/`-AuditModel`.
   **Resume a crashed run:** `-ResumeFrom <N>` (1-4) (or just re-run with no flags - completed stages
   are auto-skipped by artifact presence, and the saved session ids are reused). **Preview the resume
   plan + session ids for $0:** `-DryRun`. **Retry budget:** `-MaxRetries` (default 3).

4. **As each Monitor notification arrives, advance the TodoWrite list** so it updates live:
   - On `>>> STAGE N/4 - ...` -> mark Stage N-1 `completed` and Stage N `in_progress`.
   - On `>>> STAGE N/4 ... SKIPPED - artifact present` -> mark Stage N `completed` (resumed run; that
     stage was already done on disk).
   - On `done in Xs | cost $Y` -> note that stage's cost (the running total prints at the end).
   - On `retrying` -> a transient API error; the stage is auto-retrying. Leave it `in_progress`.
   - On `PAUSED - needs Daniel` -> a `PIPELINE_BLOCKER`; mark the current stage paused and stop advancing.
     This is the team asking for a human decision, NOT a crash.
   - On `CRASHED` -> a genuine error (e.g. the API failed after retries); mark the stage blocked, stop,
     and tell Daniel to re-run with no flags (finished stages auto-detect from the folder and skip).
   - On `TESTS RED` -> the post-Stage-4 suite failed; report it. The work is on disk; not a crash.

5. When the watch ends, mark the last stage `completed`, read the canonical artifact folder
   `_claude_artifacts/<date>_autopilot-<id>/`, and give the final debrief: total cost, artifacts
   written, and - most importantly - the **OUT-OF-SPEC DECISIONS** and **OPEN QUESTIONS FOR DANIEL**
   sections at the top of `walkthrough.md` plus `decisions-log.md` (the choices the team made on
   Daniel's behalf, and anything QA is asking him). State whether it finished all stages (**COMPLETE**),
   **PAUSED** on a `PIPELINE_BLOCKER` (needs Daniel), or **CRASHED** on a genuine error (re-run with no
   flags; finished stages auto-detect from the folder and skip). The full transcript is at
   `_claude_artifacts/_autopilot-run.log`, and `_RUN-STATUS.md` in the folder shows the final state.

> **On-demand status** also works anytime: while a run is going, just ask "status" and Claude reads
> `_RUN-STATUS.md` - which is now re-stamped after every stage with the running cost + current stage.

## What this runs (for context)

A 4-stage chain across **two persistent sessions**, handing off via artifacts in the one shared folder
`_claude_artifacts/<date>_autopilot-<id>/`. Each team does its codebase deep-dive once and **resumes its
own chat** for its second stage (so it never re-researches). Models come from `-DevModel`/`-AuditModel`
(both default `claude-opus-4-8`); each stage runs a dedicated headless `_AP` command that carries its
behavior (the script just points it at the shared folder):

| Stage | Session | Teammate | Command -> artifact |
|---|---|---|---|
| 1 Plan | dev (new) | Amelia (Dev) | `/bmad-dev-story_AP plan` -> `implementation_plan.md` |
| 2 Audit | qa (new) | Murat (QA) | `/1_self-audit-stress-test_AP` -> `self-audit-stress-test.md` |
| 3 Implement | dev (resume) | Amelia (Dev) | `/bmad-dev-story_AP implement` (applies audit, develops, tests) -> `walkthrough.md` |
| 4 Review+Fix | qa (resume) | Murat (QA) | `/bmad-code-review_AP` (verifies + reviews + applies fixes + retests) -> `code-review.md`, hands to Daniel |

## Guardrails (already built into the script - do not override)

- **Never crashes on agent output (human-in-the-loop).** There are no verdict-token gates; a stage is
  "done" iff its artifact lands in the shared folder. The run only **PAUSES** (gracefully, "needs
  Daniel") on an explicit `PIPELINE_BLOCKER` (truly unresolvable: contradictory ACs, missing dependency,
  human-only call). The audit's findings + fixes always flow into Stage 3.
- **QA owns the loop close:** Stage 4 reviews AND applies fixes itself - no separate fix stage. As the
  last agent before the human, it writes **OUT-OF-SPEC DECISIONS** + **OPEN QUESTIONS FOR DANIEL** at the
  top of `walkthrough.md` and may ask Daniel directly there.
- **Session continuity:** each team resumes its own chat (`--session-id` on the first call, `--resume`
  on the second). The two session ids are deterministic (generated up front, saved to
  `_pipeline/sessions.json`) so a crash is still resumable. Sessions are **persisted** (this is the
  cost of continuity) but **labeled** `autopilot-<story>-dev` / `-qa` - 2 named sessions in history,
  not 5 unlabeled ones. There is NO "do not research" instruction - continuity is a convenience, the
  agents still investigate anything they need.
- **Resilience:** transient API errors (stream idle timeout, overloaded, 429/503/529) are retried
  (`-MaxRetries`, default 3, with backoff) before a stage fails. A genuine hard failure (e.g. the API
  dies after retries) stamps `CRASHED` in `_RUN-STATUS.md` (never leaves "IN PROGRESS"); recover by just
  re-running with no flags - finished stages auto-detect from the folder and skip. `_RUN-STATUS.md` is
  re-stamped after every stage with the running cost + current stage; its final state is one of
  COMPLETE / PAUSED / TESTS-RED / CRASHED.
- **New-dependency policy (A):** the team self-installs + pins a needed dependency, logs it in
  `decisions-log.md`, and banners it under "NEW DEPENDENCIES" in the walkthrough - never silently.
- All stages run `--permission-mode bypassPermissions` (full autonomy on this repo).
- The pipeline **never** runs `git commit`/`push` and **never** marks the story `done`.

## After it completes - Daniel's close-out (not automated)

1. Review `walkthrough.md` - start with **OUT-OF-SPEC DECISIONS** + **OPEN QUESTIONS FOR DANIEL** at
   the top - AND `decisions-log.md` (every choice the team made on your behalf).
2. Answer any open questions; run `/1_ccps_update-active-context` to close the story.
3. Commit when satisfied.
