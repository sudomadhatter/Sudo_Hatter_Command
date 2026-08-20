---
description: Autopilot Dev-Story Loop (v2, CLAUDE) - autonomous dev/QA team across THREE sessions (Dev plans+implements in one continuous chat; QA audits then reviews+fixes in two separate one-shot chats - Stage 2 audit on Opus, Stage 4 final review on Fable, both at max effort). Resilient (retries transient errors), resumable (just re-run; finished stages auto-detect), human-in-the-loop (never crashes on agent output). CLAUDE-ONLY (needs the claude CLI). The /cicd-autopilot-opencode variant is a separate, opencode-native pipeline.
platforms: [claude]
---

# /cicd-autopilot-claude - Autonomous Story Pipeline (v2: dev chat + split QA gates)

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push `main`, never force-push
> - `.agents/rules/worktree-per-story.md` — one story, one worktree, one `claude/*` branch off the epic branch
> - `.agents/rules/smh-target-resolution.md` — bind ONE target, never operate on the lobby

> **CLAUDE-ONLY.** This drives headless `claude -p` subprocesses with exact `--model` pinning and
> session continuity (`--session-id` / `--resume`). It cannot run under Gemini/opencode and is
> intentionally NOT mirrored there.
>
> **TDAD/aider Integration Note:** This headless flow is being integrated with `aider` and `pytest-bdd`. 
> For any exact setup syntax or flags regarding the sandbox or BDD physics, explicitly reference the 
> official [aider-chat](https://github.com/Aider-AI/aider) and [pytest-bdd](https://github.com/pytest-dev/pytest-bdd) git repositories.

Launch the autopilot pipeline for the story in `$ARGUMENTS` (a story id like `11.16`, or a path),
optionally prefixed by a project name when run from the command center (e.g. `AGY_AVIATIONCHAT 11.16`).

## What to do

### Step 0 - Resolve the target project (FIRST - before anything else)
This command runs from the **command center (lobby)** and drives the autopilot inside exactly ONE child
project under `Projects/`, never the lobby itself. Resolve the target now (same pattern as the `/cicd-*`
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
before any work. Call the story argument that remains after this step `<STORY>` (= `$ARGUMENTS` minus any
consumed project token). **Binding rule:** the PowerShell script, every `_artifacts/...` path, the story
lookup, and the debrief all resolve **under `PROJECT_ROOT`**. The `.ps1` self-anchors to its own project
(it derives its repo root from its own location), so only the *paths you pass it* need the prefix - no
script change is required. When `PROJECT_ROOT` is `.`, every `<PROJECT_ROOT>/...` path below reduces to the
original in-project form.

### Step 0.5 - The epic branch must be checked out (the worktree's base)

The engine opens the story's own git worktree before Stage 1 — `.claude/worktrees/<story-slug>/` on
`claude/<JIRA-KEY>-<story-slug>` — and cuts it from **the epic branch**, per `worktree-per-story.md`
("NEVER branch a story worktree from `main`"). It takes that base from `PROJECT_ROOT`'s **current
branch**, exactly as a human's flow leaves it.

So before launching: run `git -C <PROJECT_ROOT> rev-parse --abbrev-ref HEAD`.
- An `epic/*` branch → good, that is the base.
- Anything else → either check the epic branch out there first, or pass `-EpicBranch epic/<KEY>-<slug>`.
  The script refuses to start otherwise rather than guess — a story cut from `main` cannot be landed.

The epic branch is also where the **Jira key** comes from: BMAD's epic number and the Jira epic key do
not track each other (BMAD epic 19 lives on `epic/AVCH-18-adk-2x-runtime`), so nothing about the story
id can be arithmetic-ed into a key.

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

   For a cheap plan+audit trial, append `-MaxStage 2`. **Model overrides:** `-DevModel` (Stages 1+3),
   `-AuditModel` (Stage 2), `-ReviewModel` (Stage 4) — defaults Dev `claude-opus-4-8`, audit
   `claude-opus-4-8`, review `claude-fable-5`. **Effort overrides:** `-DevEffort`/`-AuditEffort`/
   `-ReviewEffort` (defaults: `medium`/`max`/`max`; levels `low|medium|high|xhigh|max`).
   See the ladder table below — effort, not the prompt wording, is the depth control on these models.
   **Resume a crashed run:** `-ResumeFrom <N>` (1-4) (or just re-run with no flags - completed stages
   are auto-skipped by artifact presence, and the saved session ids are reused). **Preview the resume
   plan + session ids for $0:** `-DryRun`. **Retry budget:** `-MaxRetries` (default 3).
   **Per-stage runaway cap:** `-MaxStageCost` (default $15, 0 disables) — enforced inside each CLI call
   via `--max-budget-usd`, so one stuck stage halts itself (CRASHED-resumable) instead of burning far
   past the run-level `-MaxCost` (default $40).
   **Worktree + landing:** `-EpicBranch epic/<KEY>-<slug>` overrides the base branch (default: whatever
   `PROJECT_ROOT` currently has checked out — see Step 0.5). `-JiraKey <KEY>` pins the story's work item
   instead of looking it up. `-NoJira` skips the board update, `-NoCommit` skips the orchestrator's
   commit, and `-NoWorktree` runs in the shared checkout (debugging only — see the escape hatch below).

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
   - On `REVIEW INCOMPLETE` -> the gate was green but Stage 4 appended no `## Code Review` section to
     `walkthrough.md` (the QA review leg no-op'd). The story was NOT flipped. Tell Daniel to re-run
     `-ResumeFrom 4` to redo the review.
   - On `>>> WORKTREE - opened for story ...` / `re-bound to the existing tree` -> the story's isolated
     tree is open (or a resume found the existing one). Every path from here on is under it.
   - On `>>> STORY STATUS - ... flipped to review` -> the gate was green AND the review artifact exists, so
     the orchestrator advanced the story to `review` (story file + sprint-status). Daniel still owns review->done.
   - On `>>> COMMIT - <sha> on claude/...` -> the orchestrator committed the tree on its own green gate.
     Nothing was pushed. If instead you see `COMMIT REJECTED`, a git hook refused it and the work is left
     **staged** in the tree — report the hook's message; nothing is lost.
   - On `>>> JIRA - <KEY> moved to In Review` -> the board now matches the tree. `! JIRA - no work item
     resolved` means the story has no ticket; the run is still fine, the board just was not touched.

5. When the watch ends, mark the last stage `completed`, read the canonical artifact folder — which is
   **inside the story worktree**, at
   `<PROJECT_ROOT>/.claude/worktrees/<story-slug>/_artifacts/epic_<epic>/<date>_autopilot-<id>/` — and
   give the final debrief: total cost, artifacts
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

A 4-stage chain across **three sessions**, handing off via artifacts in the one shared folder
`_artifacts/epic_<epic>/<date>_autopilot-<id>/`. The Dev team does its codebase deep-dive once and **resumes
its own chat** for Stage 3 (so it never re-researches); the two QA gates run on different models in their own
one-shot sessions. Each stage runs a dedicated headless `_AP` command that carries its behavior (the script
just points it at the shared folder):

| Stage | Session | Teammate | Model | Effort | Command -> artifact |
|---|---|---|---|---|---|
| 1 Plan | dev (new) | Amelia (Dev) | `claude-opus-4-8` | `medium` | `/cicd-dev-story-tests-AP plan` -> `implementation_plan.md` |
| 2 Audit | audit (new) | Murat (QA) | `claude-opus-4-8` | **`max`** | `/cicd-self-audit-AP` -> appends `## Self-Audit` into `implementation_plan.md` |
| 3 Implement | dev (resume) | Amelia (Dev) | `claude-opus-4-8` | `medium` | `/cicd-dev-story-tests-AP implement` (applies audit, develops, tests) -> `walkthrough.md` |
| 4 Review+Fix | review (new) | Murat (QA) | `claude-fable-5` | **`max`** | `/cicd-code-review-AP` (reads plan incl. audit + walkthrough + diff, reviews, applies fixes, retests) -> appends `## Code Review` (Verdict line) into `walkthrough.md`, hands to Daniel |

**Why this ladder:** both QA gates run at **maximum effort** — they're the last checks before the human —
but they no longer share a model or a session. The pre-dev **audit runs Opus** (Fable is 2× Opus per token,
and the audit's value lives in its written artifact, so it buys full depth at half the price), while the
**final gate before the human stays Fable 5**. They're decoupled on purpose: a resumed session on a *different*
model is a model-scoped cache **miss**, so Fable would re-read Opus's whole transcript at full price —
continuity buys nothing once the models differ. Instead Stage 4 opens fresh and reads the distilled artifacts.
Thinking is always-on, so `--effort` (not "think hard" keywords) is the depth control; three model flags now
(`-DevModel`, `-AuditModel`, `-ReviewModel`), each with its own session.

## Guardrails (already built into the script - do not override)

- **Never crashes on agent output (human-in-the-loop).** There are no verdict-token gates; a stage is
  "done" iff its artifact lands in the shared folder. The run only **PAUSES** (gracefully, "needs
  Daniel") on an explicit `PIPELINE_BLOCKER` (truly unresolvable: contradictory ACs, missing dependency,
  human-only call). The audit's findings + fixes always flow into Stage 3.
- **QA owns the loop close:** Stage 4 reviews AND applies fixes itself - no separate fix stage. As the
  last agent before the human, it writes **OUT-OF-SPEC DECISIONS** + **OPEN QUESTIONS FOR DANIEL** at the
  top of `walkthrough.md` (and may ask Daniel directly there), and appends a **`## Close-Out Handoff`** block
  at the bottom — the pre-routed learnings (incl. memory candidates) that `/cicd-update-sprint-memory` lifts at close-out.
- **Sessions:** three deterministic session ids (generated up front, saved to `_pipeline/sessions.json`,
  labeled `autopilot-<story>-dev` / `-audit` / `-review`) so a crash is still resumable. The **dev**
  session is reused across Stages 1+3 (`--session-id` then `--resume`, so the Dev team never re-researches);
  the **audit** (Stage 2) and **review** (Stage 4) sessions are each one-shot `--session-id` calls on
  different models. There is NO "do not research" instruction - the agents still investigate anything they
  need, and Stage 4 grounds itself by reading the plan + audit + walkthrough + diff off disk.
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
- **One story, one worktree.** Before Stage 1 the engine opens (or re-binds to) the story's own tree at
  `.claude/worktrees/<story-slug>/` on `claude/<JIRA-KEY>-<story-slug>`, cut from the epic branch. Every
  stage's cwd, both test suites, the `git diff` baseline reads, the story file, `sprint-status.yaml` and
  the whole run folder live under it. Two things this buys, and they are the point:
  **isolation** (concurrent stories can no longer see — or red-test against — each other's half-finished
  edits; before this the only guard was a prompt line asking agents to ignore files they did not
  recognise), and **a landable result** (`/cicd-close-story-merge-tree` Step 3 requires a `claude/*` HEAD,
  so before this it would refuse to close an autopilot story at all). A resume re-binds to the SAME tree,
  matched on the story slug — it never cuts a second one. Pruning stays `/cicd-prune-worktree`'s job.
- **Gitignored assets do not travel into a worktree**, so the engine bootstraps them: `auth_keys/` and
  the `.env` files are copied in, `frontend/node_modules` is junctioned at the shared checkout's copy,
  and the test gate falls back to the shared checkout's `backend/.venv` interpreter. A venv and
  `node_modules` are toolchain, not source — pytest still collects from the worktree's cwd.
- **Concurrency-safe (run as many stories at once as you want).** Every run is keyed by its story id:
  its own worktree, a per-story monitoring log (`_autopilot-run-<story>.log`) so concurrent runs never
  cross-wire, and a per-story lockfile (`<run-folder>/_pipeline/.run.lock`) that refuses to start a
  SECOND run of the SAME story while one is live. Different stories run fully in parallel; the same
  story can't double-run.
- A missing handoff artifact is a **hard stop** (CRASHED, resumable), never a silent "continue to the next
  stage" — so a corrupted stage (e.g. Stage 1 producing no plan) halts immediately instead of burning
  spend on empty downstream stages. Re-run with no flags to resume; finished stages auto-skip.
- **The orchestrator commits; the agents never touch git.** On a clean COMPLETE the script stages
  **explicit paths** (enumerated and printed — never `git add -A`/`.`/`-u`) and commits inside the
  worktree with a Jira-keyed subject, so the armed `commit-msg` gate passes. It **never pushes**, never
  touches `main`, and never marks a story `done` — landing and closing are `/cicd-close-story-merge-tree`'s.
  A hook that rejects the commit leaves the work **staged**, and the hook's own message is printed.
  `-NoCommit` skips it.
- **The ticket moves too.** On green the orchestrator files the Dev Record through the command center's
  `jira_feed.py` (rendered FROM `walkthrough.md`, read back to prove it landed) and moves the work item
  to **In Review** — never to Done. It finds the ticket the way `jira_feed.py mint` dedupes: a summary
  whose first token is this exact BMAD id. No ticket found → warns and skips; `-JiraKey <KEY>` forces it,
  `-NoJira` turns it off.

## After it completes - Daniel's close-out (not automated)

1. Review `walkthrough.md` - start with **OUT-OF-SPEC DECISIONS** + **OPEN QUESTIONS FOR DANIEL** at
   the top - AND `decisions-log.md` (every choice the team made on your behalf). Both are in the run
   folder **inside the story worktree**; so is the code. The ticket is at **In Review** with its Dev Record.
2. Answer any open questions. The story is already at **`review`** and the work is already **committed**
   on its `claude/*` branch. Run `/cicd-close-story-merge-tree` — it runs the `/cicd-update-sprint-memory`
   save (which flips `review -> done`), lands the branch on the epic branch, and prunes the tree via
   `/cicd-prune-worktree`.
3. Nothing to commit by hand. If the run reported `COMMIT REJECTED`, the work is staged in the tree —
   read the hook message, fix it, and commit there.

> **Escape hatch (debugging the engine, not stories):** `-NoWorktree` runs every stage in the shared
> checkout, the pre-AVCH-50 behaviour. Isolation is gone, nothing is committed, and close-out will refuse
> to land the result. Do not use it for real story work.
