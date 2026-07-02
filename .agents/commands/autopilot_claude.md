---
description: Autopilot Dev-Story Loop (v2, CLAUDE) - autonomous dev/QA team in TWO continuous chats (Dev plans+implements, QA audits+reviews+fixes). Resilient (retries transient errors), resumable (just re-run; finished stages auto-detect), human-in-the-loop (never crashes on agent output). CLAUDE-ONLY (needs the claude CLI). The /autopilot_opencode variant is a separate, opencode-native pipeline.
platforms: [claude]
---

# /autopilot_claude - Autonomous Story Pipeline (v2: two continuous teams)

> **CLAUDE-ONLY.** This drives headless `claude -p` subprocesses with exact `--model` pinning and
> session continuity (`--session-id` / `--resume`). It cannot run under Gemini/opencode and is
> intentionally NOT mirrored there.

Launch the autopilot pipeline for the story in `$ARGUMENTS` (a story id like `11.16`, or a path),
optionally prefixed by a project name when run from the command center (e.g. `AGY_AVIATIONCHAT 11.16`).

## What to do

### Step 0 - Resolve the target project (FIRST - before anything else)
This command runs from the **command center (lobby)** and drives the autopilot inside exactly ONE child
project under `Projects/`, never the lobby itself. Resolve the target now (same pattern as the `/sudo-*`
commands):
- **Self fast-path (check this FIRST):** if this repo has **no** `Projects/` subfolder, you ARE the project
  - set `PROJECT_ROOT = .` and skip the rest of Step 0 (this is the autopilot run from *inside* a project).
- **Inline override:** if `$ARGUMENTS` begins with a name matching a folder under `Projects/`, that is the
  target; **consume that first token** (the remainder is the real story id/path). Write the name alone into
  `_my_resources/active-project.txt` (overwrite) so later commands inherit it.
- **Active pointer:** else read `_my_resources/active-project.txt`; if it names a folder under `Projects/`, use it.
- **Ask:** else STOP and ask Daniel *"Which project are we working in? (e.g. AGY_AVIATIONCHAT)"* - never
  guess, never run the autopilot against the lobby.

Set `PROJECT_ROOT` (= `Projects/<name>`, or `.` via the fast-path) and **echo** `Target: <PROJECT_ROOT>`
before any work. Call the story argument that remains after this step `<STORY>` (= `$ARGUMENTS` minus any
consumed project token). **Binding rule:** the PowerShell script, every `_artifacts/...` path, the story
lookup, and the debrief all resolve **under `PROJECT_ROOT`**. The `.ps1` self-anchors to its own project
(it derives its repo root from its own location), so only the *paths you pass it* need the prefix - no
script change is required. When `PROJECT_ROOT` is `.`, every `<PROJECT_ROOT>/...` path below reduces to the
original in-project form.

1. Confirm a story identifier remains in `<STORY>` after Step 0. If empty, ask which story and stop.

2. **Create a live TodoWrite list mirroring the pipeline** so Daniel watches it advance in the panel.
   Items (trim to match `-MaxStage`): `Stage 1 - Plan (Dev)`, `Stage 2 - Audit (QA)`,
   `Stage 3 - Implement (Dev)`, `Stage 4 - Review+Fix (QA)`. Mark Stage 1 `in_progress`,
   the rest `pending`.

3. Run the orchestrator under the **Monitor** tool so each stage transition streams into the chat as
   a live notification (Monitor avoids the foreground timeout AND drives the todo updates below).
   Call Monitor with:

   Substitute `<PROJECT_ROOT>` and `<STORY>` below with the values resolved in Step 0 before calling
   Monitor (when `PROJECT_ROOT` is `.` the paths reduce to the original in-project form):

   - **command:** `LOG_SLUG=$(printf '%s' "<STORY>" | tr -c 'A-Za-z0-9' '-' | sed 's/--*/-/g; s/^-//; s/-$//'); LOG="<PROJECT_ROOT>/_artifacts/_autopilot-run-$LOG_SLUG.log"; powershell.exe -NoProfile -File "<PROJECT_ROOT>/scripts/autopilot-dev-story.ps1" -Story "<STORY>" > "$LOG" 2>&1 & APID=$!; tail --pid=$APID -f -n +1 "$LOG" | grep --line-buffered -E ">>> STAGE|TEST GATE|STORY STATUS|done in|PAUSED|AUTOPILOT|Total cost|CRASHED|retrying|MODEL MISMATCH|! WARNING|TESTS|COST CEILING|REVIEW INCOMPLETE"`
   - **description:** `autopilot <STORY> - stage progress (per-story log <PROJECT_ROOT>/_artifacts/_autopilot-run-<story>.log)`
   - **persistent:** `true`  (tail exits when the script PID dies)

   This **tails a real log file** instead of piping the live PowerShell straight through `grep` (the old
   way swallowed every startup error and could make a healthy run look dead). The global log is now
   **per-story** — `_artifacts/_autopilot-run-<story>.log` (the `<story>` slug is derived from
   `$ARGUMENTS`), so two autopilots running at once never cross-wire each other's stream into one file.
   The FULL transcript is always at that per-story path — if the run errors before the first stage, read
   that log to see exactly why. The `grep` here only filters what STREAMS into the chat; the log keeps
   everything. Stage transitions still arrive as live notifications, so the TodoWrite updates below work
   exactly as before. The filter now also streams the `>>> TEST GATE` heartbeat (so the ~100s gate phase
   after Stage 4 isn't a silent gap that looks hung) and the `>>> STORY STATUS` flip; the `WARNING` token
   is anchored to the script's own `! WARNING` prefix so it no longer false-fires on pytest's
   `DeprecationWarning` noise during the gate. (The run folder ALSO keeps its own self-contained copy of
   the transcript at `<run-folder>/_pipeline/run.log` — the per-story global log above is just the stable,
   known-upfront path to tail live.)

   For a cheap plan+audit trial, append `-MaxStage 2`. Model overrides: `-DevModel`/`-AuditModel`
   (defaults: Dev `claude-opus-4-8`, QA `claude-fable-5`).
   **Resume a crashed run:** `-ResumeFrom <N>` (1-4) (or just re-run with no flags - completed stages
   are auto-skipped by artifact presence, and the saved session ids are reused). **Preview the resume
   plan + session ids for $0:** `-DryRun`. **Retry budget:** `-MaxRetries` (default 3).
   **Per-stage runaway cap:** `-MaxStageCost` (default $15, 0 disables) — enforced inside each CLI call
   via `--max-budget-usd`, so one stuck stage halts itself (CRASHED-resumable) instead of burning far
   past the run-level `-MaxCost` (default $40).

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
   - On `>>> TEST GATE - baseline snapshot ...` -> BEFORE Stage 3 the orchestrator records the pre-existing
     red tests (~100s, once) so the final gate can ignore already-broken tests and fail only on regressions
     THIS run introduces. Heartbeat, not a hang.
   - On `>>> TEST GATE - ...` -> after Stage 4, the orchestrator is independently re-running the suites
     (pytest / vitest, ~100s). This is the heartbeat for that phase; the run is NOT hung. Leave Stage 4
     `completed` and wait for the gate result.
   - On `>>> TEST GATE - backend GREEN vs baseline (...)` -> the suite has pre-existing failures but the
     story introduced ZERO new ones; this is a PASS. The run proceeds to the story flip.
   - On `TESTS RED` -> the post-Stage-4 gate found NEW failures vs the pre-run baseline (true regressions
     from this run, listed in the log); report them. The work is on disk; not a crash. Re-run `-ResumeFrom 4`.
   - On `REVIEW INCOMPLETE` -> the gate was green but Stage 4 wrote no `code-review.md` (the QA review leg
     no-op'd). The story was NOT flipped. Tell Daniel to re-run `-ResumeFrom 4` to redo the review.
   - On `>>> STORY STATUS - ... flipped to review` -> the gate was green AND the review artifact exists, so
     the orchestrator advanced the story to `review` (story file + sprint-status). Daniel still owns review->done.

5. When the watch ends, mark the last stage `completed`, read the canonical artifact folder
   `<PROJECT_ROOT>/_artifacts/epic_<epic>/<date>_autopilot-<id>/`, and give the final debrief: total cost, artifacts
   written, and - most importantly - the **OUT-OF-SPEC DECISIONS** and **OPEN QUESTIONS FOR DANIEL**
   sections at the top of `walkthrough.md` plus `decisions-log.md` (the choices the team made on
   Daniel's behalf, and anything QA is asking him). State whether it finished all stages (**COMPLETE**),
   **PAUSED** on a `PIPELINE_BLOCKER` (needs Daniel), or **CRASHED** on a genuine error (re-run with no
   flags; finished stages auto-detect from the folder and skip). On a clean **COMPLETE**, also tell Daniel
   the story was auto-advanced to **`review`** (story file + sprint-status) — he owns the `review -> done`
   flip. The full transcript is at `<PROJECT_ROOT>/_artifacts/_autopilot-run-<story>.log` (and a self-contained copy in
   `<run-folder>/_pipeline/run.log`), and `_RUN-STATUS.md` in the folder shows the final state.

> **On-demand status** also works anytime: while a run is going, just ask "status" and Claude reads
> `_RUN-STATUS.md` - which is now re-stamped after every stage with the running cost + current stage, and
> carries the **orchestrator PID** for a liveness check: if the headline still says `IN PROGRESS` /
> `TEST GATE` but that PID is not a running process, the run died mid-flight (a hard kill / closed
> terminal bypasses the `CRASHED` stamp) - treat it as crashed and re-run with no flags to resume.

## What this runs (for context)

A 4-stage chain across **two persistent sessions**, handing off via artifacts in the one shared folder
`_artifacts/epic_<epic>/<date>_autopilot-<id>/`. Each team does its codebase deep-dive once and **resumes its
own chat** for its second stage (so it never re-researches). Models come from `-DevModel`/`-AuditModel`
(Dev defaults `claude-opus-4-8`; QA defaults `claude-fable-5` — the strongest tier sits on the audit +
review+fix lane, the last gates before the human, and the two QA stages share one session so the
codebase deep-dive is paid once); each stage runs a dedicated headless `_AP` command that carries its
behavior (the script just points it at the shared folder):

| Stage | Session | Teammate | Command -> artifact |
|---|---|---|---|
| 1 Plan | dev (new) | Amelia (Dev) | `/sudo-dev-story-tests_AP plan` -> `implementation_plan.md` |
| 2 Audit | qa (new) | Murat (QA) | `/sudo-self-audit_AP` -> `self-audit-stress-test.md` |
| 3 Implement | dev (resume) | Amelia (Dev) | `/sudo-dev-story-tests_AP implement` (applies audit, develops, tests) -> `walkthrough.md` |
| 4 Review+Fix | qa (resume) | Murat (QA) | `/sudo-code-review_AP` (verifies + reviews + applies fixes + retests) -> `code-review.md`, hands to Daniel |

## Guardrails (already built into the script - do not override)

- **Never crashes on agent output (human-in-the-loop).** There are no verdict-token gates; a stage is
  "done" iff its artifact lands in the shared folder. The run only **PAUSES** (gracefully, "needs
  Daniel") on an explicit `PIPELINE_BLOCKER` (truly unresolvable: contradictory ACs, missing dependency,
  human-only call). The audit's findings + fixes always flow into Stage 3.
- **QA owns the loop close:** Stage 4 reviews AND applies fixes itself - no separate fix stage. As the
  last agent before the human, it writes **OUT-OF-SPEC DECISIONS** + **OPEN QUESTIONS FOR DANIEL** at the
  top of `walkthrough.md` (and may ask Daniel directly there), and appends a **`## Close-Out Handoff`** block
  at the bottom — the pre-routed learnings (incl. memory candidates) that `/sudo-update-sprint-memory` lifts at close-out.
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
- **Story-status flip (review only):** on a clean COMPLETE (all stages + a GREEN independent gate), the
  orchestrator advances the story to **`review`** — in BOTH the story `.md` and `sprint-status.yaml`,
  idempotently (only `ready-for-dev`/`in-progress` advance; `review`/`done` are left alone). This is the
  BMAD "Dev finishes -> review" step. It **never** flips to `done` (the human owns `review -> done`), and
  it is best-effort (a flip hiccup warns, never crashes a finished run). The agents themselves still never
  touch status — the orchestrator owns the flip, gated on its own green test result.
- **Concurrency-safe (run as many stories at once as you want).** Every run is keyed by its story id:
  a per-story monitoring log (`_autopilot-run-<story>.log`) so concurrent runs never cross-wire, and a
  per-story lockfile (`<run-folder>/_pipeline/.run.lock`) that refuses to start a SECOND run of the SAME
  story while one is live. Different stories run fully in parallel (each writes to its own story folder,
  log, and session store); the same story can't double-run.
- A missing handoff artifact is a **hard stop** (CRASHED, resumable), never a silent "continue to the next
  stage" — so a corrupted stage (e.g. Stage 1 producing no plan) halts immediately instead of burning
  spend on empty downstream stages. Re-run with no flags to resume; finished stages auto-skip.
- The pipeline **never** runs `git commit`/`push` and **never** marks the story `done`.

## After it completes - Daniel's close-out (not automated)

1. Review `walkthrough.md` - start with **OUT-OF-SPEC DECISIONS** + **OPEN QUESTIONS FOR DANIEL** at
   the top - AND `decisions-log.md` (every choice the team made on your behalf).
2. Answer any open questions. The story is already at **`review`** (the orchestrator flipped it on the
   green gate); run `/sudo-update-sprint-memory`, then flip `review -> done` when you're satisfied.
3. Commit when satisfied.
