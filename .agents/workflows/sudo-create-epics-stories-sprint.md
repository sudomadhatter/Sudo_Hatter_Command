---
description: Epic kickoff — create the epic + its stories, generate the sprint board, then interactively risk-score every story P0–P3 (test levels). Phase A of the sudo flow, before the per-story dev loop.
platforms: [opencode, antigravity]
---

# /sudo-create-epics-stories-sprint — Epic Kickoff: Stories + Sprint + Risk-Score (Phase A)

Thin orchestrator — calls three existing BMAD/TEA skills back-to-back so a batch of requirements arrives as
an epic, a populated sprint board, AND a Daniel-confirmed P0–P3 risk map in ONE pass. Runs BEFORE the
per-story dev loop. Project-scoped (targets THIS repo).

> Flow position: `sudo-boot-sprint-memory` → **`sudo-create-epics-stories-sprint`** →
> `sudo-write-story-tests` → `sudo-dev-story-tests` → `sudo-code-review` → `sudo-update-sprint-memory`.

## Step 0 — Resolve the target project (FIRST — before any other step)
Run from the **command center** (the lobby), this command operates on exactly ONE child project under
`Projects/`, never the lobby itself. Resolve the target now:
0. **Self (sub-project fast path — check this FIRST, and STOP here if it matches)** — if this repo has
   **no** `Projects/` subfolder, you ARE the project: set `PROJECT_ROOT = .` and skip straight to the
   binding rule. Do NOT read `active-project.txt`, parse `$ARGUMENTS` for a project name, or ask which
   project — cases 1–3 below are command-center-only (the lobby that hosts children under `Projects/`).
1. **Inline override** — if `$ARGUMENTS` begins with a name matching a folder under `Projects/`, that is
   the target; consume that first token (the remainder is the real argument — requirements source, focus, …).
   Write the name alone into `.agents/active-project.txt` (overwrite) so later commands inherit it.
2. **Active pointer** — else read `.agents/active-project.txt`; if it names a folder under
   `Projects/`, use it.
3. **Ask** — else STOP and ask Daniel *"Which project are we working in? (e.g. AGY_AVIATIONCHAT)"* —
   never guess, never operate on the lobby.

Set `PROJECT_ROOT = Projects/<name>` and **echo exactly** `Target: Projects/<name>` before any work.

**Binding rule (applies to EVERY step below):** every "THIS repo", every `{project-root}`, and every bare
path (`_bmad-output/…`, `_bmad/…`, `_artifacts/…`, story files, `sprint-status.yaml`) resolves **under
`PROJECT_ROOT`**. When you invoke any nested `bmad-*` skill, bind its `{project-root}` to `PROJECT_ROOT`,
run it against that directory, and read/write only there. If a needed path is missing under `PROJECT_ROOT`,
STOP and say so — never fall back to the lobby.

## Step 1 — Create the epic and its stories
Invoke the **`bmad-create-epics-and-stories`** skill for the requirements in `$ARGUMENTS` (a PRD, a
fix-list path, or a described scope — e.g. `_my_resources/open_tasks/fix_list_admin_sudoadmin.md`). It writes
the epic + its user stories with acceptance criteria. Confirm the epic + story files exist before continuing.
If the skill stops for input (missing requirements source, ambiguous scope), surface it and STOP — never guess.

## Step 2 — Generate the sprint board
Invoke the **`bmad-sprint-planning`** skill. It lands the new stories in
`_bmad-output/implementation-artifacts/sprint-status.yaml` as `ready-for-dev`. Confirm they appear before Step 3.

## Step 3 — Risk-score the backlog (test levels) — INTERACTIVE HARD STOP
This is the final step and a **hard stop** — you WORK WITH Daniel to label every story, one at a time.

1. Invoke the **`bmad-testarch-test-design`** skill to risk-analyze the epic's stories (Risk = Probability ×
   Impact, per the TEA Test Priorities Matrix).
2. Assume the **Test Architect (Murat)** persona and walk Daniel through the P-level decision **ONE STORY AT
   A TIME**. For EACH story present:
   - **Your recommended P-level** (P0 / P1 / P2 / P3) — your opinion, stated first.
   - **Why** — the Probability × Impact reasoning in a line or two (what breaks, and how much it hurts).
   - **What it is** — one line of plain-language context on the feature/decision being scored.
   - **Levels it earns** — P0 = Unit+Integration+E2E+Manual (100%) · P1 = Unit+Integration+E2E (80%) ·
     P2 = Integration+Manual (50%) · P3 = Manual/skip (20%).
3. Give Daniel a way to **confirm or override each label individually** (the tap-to-answer question UI; the
   recommended P-level is the default first choice). **STOP and wait** for his decision on each — do NOT
   batch them all silently or assume the recommendation. This is the hard stop.
4. Record the confirmed P-levels + test-level allocation into the test-design artifact
   (`_bmad-output/test-artifacts/test-design/…`) and reflect the P-level onto each story.

## Done
Report: the epic id + title, the stories created (ids + titles), sprint-status counts, and the confirmed
**P-level map** (story → P0–P3 + levels earned). Point to the next step:
> "Backlog risk-scored and sprint-ready. Next: `/sudo-write-story-tests <story>` for the top P0 (e.g. `<id>`)."
Leave it there — **do NOT start writing tests or code** (that's `/sudo-write-story-tests`).

Optional additional input: $ARGUMENTS
