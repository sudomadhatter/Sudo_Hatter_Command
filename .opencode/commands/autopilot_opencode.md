---
description: Autopilot Dev-Story Loop (OPENCODE engine) - autonomous dev/QA team in TWO continuous chats on the opencode engine (Dev on the selected default model, QA pinned to GLM 5.2 at max effort). Same 4-stage relay + artifact contract + test gate + story->review flip as /autopilot_claude, different worker binary. OPENCODE-ONLY (needs the opencode CLI). The /autopilot_claude variant is the Claude-engine sibling.
platforms: [opencode]
---

# /autopilot_opencode - Autonomous Story Pipeline (opencode engine)

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push `main`, never force-push
> - `.agents/rules/worktree-per-story.md` — one story, one worktree, one `claude/*` branch off the epic branch
> - `.agents/rules/sudo-target-resolution.md` — bind ONE target, never operate on the lobby

> **OPENCODE-ONLY.** This drives headless `opencode run` subprocesses. It is the opencode-native
> sibling of `/autopilot_claude` (which drives `claude -p`). Same relay, same artifact contract,
> same test gate, same story->review flip - only the worker call differs.

Launch the autopilot pipeline for the story in `$ARGUMENTS` (a story id like `11.16`, or a path),
optionally prefixed by a project name when run from the command center (e.g. `AGY_AVIATIONCHAT 11.16`).

## MODEL SPLIT (why this engine exists)

Both teams run on opencode. No Claude, no Anthropic provider, no API keys - opencode already serves
GLM 5.2.

- **Dev (Stages 1 & 3):** opencode's **selected default model**. The script OMITS `-m`, so the child
  inherits the default agent's configured model. To pin a specific Dev model for a run, pass
  `-DevModel openrouter/<model>` (forwarded as `-m`).
- **QA (Stages 2 & 4):** pinned to `openrouter/z-ai/glm-5.2` at `--variant max` (the strongest
  reasoning on the audit + review+fix lane - the last gates before the human). Override with
  `-QaModel` / `-QaVariant`.

This mirrors the Claude engine's own philosophy (workflow doc section 5b: "the asymmetry that
matters is effort, not model") - Dev at default effort, QA at max reasoning.

## What to do

### Step 0 - Resolve the target project (FIRST - before anything else)
This command runs from the **command center (lobby)** and drives the autopilot inside exactly ONE child
project under `Projects/`, never the lobby itself. Resolve the target now (same pattern as the `/sudo-*`
commands):
- **Self fast-path (check this FIRST):** if this repo has **no** `Projects/` subfolder, you ARE the project
  - set `PROJECT_ROOT = .` and skip the rest of Step 0 (this is the autopilot run from *inside* a project).
- **Inline override:** if `$ARGUMENTS` begins with a name matching a folder under `Projects/`, that is the
  target; **consume that first token** (the remainder is the real story id/path). Write the name alone into
  `.agents/active-project.txt` (overwrite) so later commands inherit it.
- **Active pointer:** else read `.agents/active-project.txt`; if it names a folder under `Projects/`, use it.
- **Ask:** else STOP and ask Daniel *"Which project are we working in? (e.g. AGY_AVIATIONCHAT)"* - never
  guess, never run the autopilot against the lobby.

Set `PROJECT_ROOT` (= `Projects/<name>`, or `.` via the fast-path) and **echo** `Target: <PROJECT_ROOT>`
before any work. Call the story argument that remains after this step `<STORY>`. **Binding rule:** the
PowerShell script, every `_artifacts/...` path, the story lookup, and the debrief all resolve **under
`PROJECT_ROOT`**. The `.ps1` self-anchors to its own project (it derives its repo root from its own
location), so only the *paths you pass it* need the prefix - no script change is required. When
`PROJECT_ROOT` is `.`, every `<PROJECT_ROOT>/...` path below reduces to the original in-project form.

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

   - **command:** `LOG_SLUG=$(printf '%s' "<STORY>" | tr -c 'A-Za-z0-9' '-' | sed 's/--*/-/g; s/^-//; s/-$//'); LOG="<PROJECT_ROOT>/_artifacts/_autopilot-run-$LOG_SLUG.log"; powershell.exe -NoProfile -File "<PROJECT_ROOT>/scripts/autopilot-dev-story-opencode.ps1" -Story "<STORY>" > "$LOG" 2>&1 & APID=$!; tail --pid=$APID -f -n +1 "$LOG" | grep --line-buffered -E ">>> STAGE|TEST GATE|STORY STATUS|done in|PAUSED|AUTOPILOT|Total cost|CRASHED|retrying|! WARNING|TESTS|COST CEILING|REVIEW INCOMPLETE"`
   - **description:** `autopilot <STORY> (opencode) - stage progress (per-story log <PROJECT_ROOT>/_artifacts/_autopilot-run-<story>.log)`
   - **persistent:** `true`  (tail exits when the script PID dies)

   This **tails a real log file**. The global log is **per-story** - `_artifacts/_autopilot-run-<story>.log`
   (the `<story>` slug is derived from `$ARGUMENTS`), so two autopilots running at once never cross-wire
   each other's stream. The FULL transcript is always at that per-story path - if the run errors before
   the first stage, read that log to see exactly why. The `grep` here only filters what STREAMS into the
   chat; the log keeps everything. (The `MODEL MISMATCH` token from the Claude engine is dropped here -
   the opencode event stream carries no `model` field, so the mismatch assertion is a no-op on this
   engine.) The run folder ALSO keeps its own self-contained copy of the transcript at
   `<run-folder>/_pipeline/run.log`.

   For a cheap plan+audit trial, append `-MaxStage 2`. For the trial that proves the opencode resume
   hop (Plan -> Audit -> Implement), append `-MaxStage 3`. Model overrides: `-DevModel` (default empty =
   opencode selected default) / `-QaModel` (default `openrouter/z-ai/glm-5.2`) / `-QaVariant` (default `max`).
   **Resume a crashed run:** `-ResumeFrom <N>` (1-4) (or just re-run with no flags - completed stages
   are auto-skipped by artifact presence, and the saved session ids are reused). **Preview the resume
   plan + session ids for $0:** `-DryRun`. **Retry budget:** `-MaxRetries` (default 3).
   **Per-stage runaway cap:** NOT AVAILABLE on this engine (opencode has no `--max-budget-usd`
   equivalent); only the run-level `-MaxCost` (default $40) bounds total spend BETWEEN stages.

4. **As each Monitor notification arrives, advance the TodoWrite list** so it updates live:
   - On `>>> STAGE N/4 - ...` -> mark Stage N-1 `completed` and Stage N `in_progress`.
   - On `>>> STAGE N/4 ... SKIPPED - artifact present` -> mark Stage N `completed` (resumed run).
   - On `done in Xs | cost $Y` -> note that stage's cost.
   - On `retrying` -> a transient API error; the stage is auto-retrying. Leave it `in_progress`.
   - On `PAUSED - needs Daniel` -> a `PIPELINE_BLOCKER`; mark the current stage paused and stop.
   - On `CRASHED` -> a genuine error (e.g. the API failed after retries); mark the stage blocked, stop,
     and tell Daniel to re-run with no flags (finished stages auto-detect from the folder and skip).
   - On `>>> TEST GATE - baseline snapshot ...` -> BEFORE Stage 3 the orchestrator records the pre-existing
     red tests (~100s, once). Heartbeat, not a hang.
   - On `>>> TEST GATE - ...` -> after Stage 4, the orchestrator is independently re-running the suites.
     Leave Stage 4 `completed` and wait for the gate result.
   - On `TESTS RED` -> the post-Stage-4 gate found NEW failures vs the pre-run baseline. Re-run `-ResumeFrom 4`.
   - On `>>> WORKTREE - opened for story ...` / `re-bound to the existing tree` -> the story's isolated
     tree is open (or a resume found the existing one). Every path from here on is under it.
   - On `>>> STORY STATUS - ... flipped to review` -> gate green + review artifact exists; story advanced.
   - On `>>> COMMIT - <sha> on claude/...` -> the orchestrator committed the tree on its own green gate;
     nothing was pushed. `COMMIT REJECTED` means a git hook refused it and the work is left **staged**.
   - On `>>> JIRA - <KEY> moved to In Review` -> the board now matches the tree.

5. When the watch ends, mark the last stage `completed`, read the canonical artifact folder — which is
   **inside the story worktree**, at
   `<PROJECT_ROOT>/.claude/worktrees/<story-slug>/_artifacts/epic_<epic>/<date>_autopilot-<id>/` — and
   give the final debrief: total cost, artifacts
   written, and - most importantly - the **OUT-OF-SPEC DECISIONS** and **OPEN QUESTIONS FOR DANIEL**
   sections at the top of `walkthrough.md` plus `decisions-log.md`. State whether it finished all stages
   (**COMPLETE**), **PAUSED** on a `PIPELINE_BLOCKER`, or **CRASHED** (re-run with no flags; finished
   stages auto-detect and skip). On a clean **COMPLETE**, also tell Daniel the story was auto-advanced
   to **`review`** - he owns the `review -> done` flip. The full transcript is at
   `<PROJECT_ROOT>/_artifacts/_autopilot-run-<story>.log` (and a self-contained copy in
   `<run-folder>/_pipeline/run.log`), and `_RUN-STATUS.md` in the folder shows the final state.

> **On-demand status** also works anytime: while a run is going, just ask "status" and the agent reads
> `_RUN-STATUS.md` - re-stamped after every stage with the running cost + current stage + the orchestrator
> PID for a liveness check.

## What this runs (for context)

A 4-stage chain across **two persistent sessions** on the opencode engine, handing off via artifacts in
the one shared folder `_artifacts/epic_<epic>/<date>_autopilot-<id>/`. Each team does its codebase
deep-dive once and **resumes its own chat** for its second stage (so it never re-researches):

| Stage | Session | Teammate | Command -> artifact |
|---|---|---|---|
| 1 Plan | dev (new) | Amelia (Dev) | `/sudo-dev-story-tests_AP plan` -> `implementation_plan.md` |
| 2 Audit | qa (new) | Murat (QA) | `/sudo-self-audit_AP` -> appends `## Self-Audit` into `implementation_plan.md` |
| 3 Implement | dev (resume) | Amelia (Dev) | `/sudo-dev-story-tests_AP implement` -> `walkthrough.md` |
| 4 Review+Fix | qa (resume) | Murat (QA) | `/sudo-code-review_AP` -> appends `## Code Review` (Verdict line) into `walkthrough.md` |

**Session continuity on opencode:** the `claude` engine pre-mints a UUID and passes `--session-id`.
opencode mints `ses_...` ids server-side, so this engine **captures the id from each "new" stage's
event stream**, persists it to `_pipeline/sessions.json`, and passes `--session <id>` on the resume
stage. Because the ids are read back from disk on a resume, a crashed run is still resumable.

## Honest gaps vs the Claude engine

- **NO per-stage cost cap.** opencode's `run` CLI has no `--max-budget-usd` equivalent, so `-MaxStageCost`
  does not exist on this engine. The run-level `-MaxCost` still bounds total spend BETWEEN stages, but a
  single runaway stage cannot self-halt mid-flight. Acceptable for v1; revisit if it burns.
- **Model-mismatch assertion is a no-op.** The opencode event stream (`--format json`) carries no `model`
  field, so served-vs-requested cannot be checked. The assertion hook is kept but never fires; a real
  mismatch would surface as a stage error or wrong-quality output instead.
- **`--variant max` is provider-specific.** If OpenRouter rejects `max` for GLM 5.2, the stage errors and
  retries (fall back to `-QaVariant high`). Confirmed at the first trial run.
- **Resume-context fidelity** is the make-or-break unknown: whether `opencode run --session <id>`
  faithfully replays the Dev plan context into Stage 3 the way `claude --resume` does. Verified at the
  `-MaxStage 3` trial; if it does not carry context, stop and reconsider.

## Guardrails (already built into the script - do not override)

Same as `/autopilot_claude`: never crashes on agent output (human-in-the-loop); QA owns the loop close
(Stage 4 reviews AND applies fixes); resilience (transient errors retry before failing; a hard failure
stamps `CRASHED`; `_RUN-STATUS.md` re-stamped after every stage; resumable - completed stages auto-detect
by artifact presence); the audit never hard-halts (findings flow into Stage 3); new-dependency policy
(self-install + pin + log + banner); all stages run `--auto` (full autonomy on this repo); story-status
flip to `review` only (never `done`); missing handoff artifact is a hard stop (CRASHED-resumable);
**never pushes and never touches `main`**.

Also the same as `/autopilot_claude`, and new here (read that command's Guardrails for the full text):

- **One story, one worktree** — `.claude/worktrees/<story-slug>/` on `claude/<JIRA-KEY>-<story-slug>`,
  cut from the epic branch, opened before Stage 1 and re-bound on resume. Every stage cwd, both suites,
  the story file, `sprint-status.yaml` and the run folder live under it. It is what makes the result
  landable at all: `/sudo-update-sprint-memory` Step 7 requires a `claude/*` HEAD.
- **Gitignored assets are bootstrapped in** (`auth_keys/`, the `.env` files, a `node_modules` junction),
  because they do not travel with a worktree.
- **The orchestrator commits** inside the tree on its green gate — explicit enumerated paths, Jira-keyed
  subject, no push — then files the Dev Record and moves the ticket to **In Review**.
- **Two gaps this engine had that the claude one never did, both closed in the same pass:** it now has
  the per-story `.run.lock` (nothing used to stop a double-run of the SAME story), and its test gate now
  finds `backend/.venv` — it looked only at a repo-root `.venv`, which does not exist in AviationChat, so
  this lane had never once found its own interpreter and silently fell through to system python.

## How to run it directly

```powershell
# Full run
.\scripts\autopilot-dev-story-opencode.ps1 -Story 13.4

# Cheap trial: plan + audit only (stop after Stage 2)
.\scripts\autopilot-dev-story-opencode.ps1 -Story 13.4 -MaxStage 2

# Resume-hop trial: Plan -> Audit -> Implement (proves the opencode --session resume)
.\scripts\autopilot-dev-story-opencode.ps1 -Story 13.4 -MaxStage 3

# See the resume plan + sessions, spend nothing
.\scripts\autopilot-dev-story-opencode.ps1 -Story 13.4 -DryRun

# Re-run only the review+fix leg (resumes the qa session)
.\scripts\autopilot-dev-story-opencode.ps1 -Story 13.4 -ResumeFrom 4
```

Or trigger via the slash command: **`/autopilot_opencode 13.4`**.

| Parameter | Default | Purpose |
|---|---|---|
| `-Story` | (required) | `"14.2"` or a path to the story `.md` |
| `-DevModel` | `""` (empty) | Dev model; empty = omit `-m` = opencode selected default. Pin with `openrouter/<model>`. |
| `-QaModel` | `openrouter/z-ai/glm-5.2` | QA model (pinned) |
| `-QaVariant` | `max` | opencode `--variant` for QA stages (`high` fallback) |
| `-MaxStage` | `4` | stop after this stage (1-4) |
| `-ResumeFrom` | `0` (auto) | force a start stage (1-4) |
| `-MaxRetries` | `3` | transient-error attempts per stage |
| `-MaxCost` | `40` | $ ceiling; halts if spend crosses it (`0` disables). No per-stage cap on this engine. |
| `-TestScope` | `auto` | independent gate: `auto`/`backend`/`frontend`/`both`/`none` |
| `-DryRun` | off | print the plan + sessions + the worktree that would be cut, no spend |
| `-EpicBranch` | (current branch) | the epic branch the story tree is cut from; must be an `epic/*` |
| `-NoWorktree` | off | debug only: run in the shared checkout; no isolation, no commit, cannot be closed out |
| `-JiraKey` | (looked up) | the story's work item, for the Dev Record + move to In Review |
| `-NoJira` / `-NoCommit` | off | skip the board update / skip the orchestrator's commit |

**Exit codes:** `0` complete - `2` paused on a blocker - `3` crashed (resume with `-ResumeFrom`) -
`4` test gate red (resume `-ResumeFrom 4`) - `5` cost ceiling hit (raise `-MaxCost`).

## After it completes - Daniel's close-out (not automated)

1. Review `walkthrough.md` - start with **OUT-OF-SPEC DECISIONS** + **OPEN QUESTIONS FOR DANIEL** at
   the top - AND `decisions-log.md` (every choice the team made on your behalf). Both are in the run
   folder **inside the story worktree**; so is the code. The ticket is at **In Review** with its Dev Record.
2. Answer any open questions. The story is already at **`review`** and the work is already **committed**
   on its `claude/*` branch. Run `/sudo-update-sprint-memory` — it lands the branch on the epic branch,
   flips `review -> done`, and prunes the tree.
3. Nothing to commit by hand. If the run reported `COMMIT REJECTED`, the work is staged in the tree.
