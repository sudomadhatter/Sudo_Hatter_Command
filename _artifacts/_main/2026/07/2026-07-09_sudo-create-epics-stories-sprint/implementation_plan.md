---
IsArtifact: true
ArtifactMetadata:
  type: implementation_plan
  date: 2026-07-09
  slug: sudo-create-epics-stories-sprint
  author: Claude (Opus 4.8)
  workspace: _main (home-base toolkit)
---

# Implementation Plan — `/sudo-create-epics-stories-sprint` (epic kickoff) + workflow-doc sync

## 1. Goal & background

Align the sudo flow to Daniel's clean **8-step agile enterprise dev cycle** and update the source-of-truth
doc (`tea_testing_work_flows_sudo.md`). The flow is **two phases**: an **epic kickoff** (once) + the
**per-story loop** (repeat). Mapping shows only two gaps — everything else already exists:

| # | Daniel's step | Command | Status |
|---|---|---|---|
| — | orient (where am I / next) | `/sudo-boot-sprint-memory` | exists |
| **1** | Epic + stories + sprint | `/sudo-create-epics-stories-sprint` | **NEW (this plan)** |
| **2** | Map test levels (P0–P3) | folded in as the NEW command's **final interactive step** | **NEW (this plan)** |
| 3 | Write failing test | `/sudo-write-story-tests` | exists |
| 4 | Dev implementation plan | `/sudo-dev-story-tests` → Step 1 | exists |
| 5 | Self-audit stress test | `/sudo-dev-story-tests` → Step 2 | exists |
| 6 | Code the story | `/sudo-dev-story-tests` → Steps 3–4 | exists |
| 7 | Code review + run tests | `/sudo-code-review` | exists |
| 8 | Close out + git push + log learnings | `/sudo-update-sprint-memory` + Daniel's commit | exists |

Decided in-session:
- **Keep `/sudo-boot-sprint-memory` separate** (read-only orientation ≠ backlog write).
- **Fold test-design (step 2) into the kickoff command** as its **final HARD STOP**: interactive, per-story
  P0–P3 labeling where Claude states its recommendation + *why* + one-line context + the levels that P-level
  earns, and Daniel confirms/overrides **each story one at a time**.
- Build the command across all 3 repos **and** update the workflow doc in this pass.

## 2. How a sudo command is authored + propagated (verified from the sync script)

- Hand-author **two** master files: `.agents/commands/<name>.md` (logic) + `.agents/skills/<name>/SKILL.md`
  (Claude launcher). `/sync-agents` generates the rest (`.agents/workflows/` Antigravity mirror, `.claude/skills/`
  copy, `.opencode/`, global caches). `platforms: [opencode, antigravity]` matches every sibling sudo command.

## 3. Files to create / change

### 3a. NEW `.agents/commands/sudo-create-epics-stories-sprint.md` (the logic)

```markdown
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
   **no** `Projects/` subfolder, you ARE the project: set `PROJECT_ROOT = .` and skip to the binding rule.
   Do NOT read `active-project.txt`, parse `$ARGUMENTS` for a project name, or ask which project.
1. **Inline override** — if `$ARGUMENTS` begins with a name matching a folder under `Projects/`, that is the
   target; consume that first token (the remainder is the real argument — requirements source, focus, …).
   Write the name alone into `_my_resources/active-project.txt` (overwrite) so later commands inherit it.
2. **Active pointer** — else read `_my_resources/active-project.txt`; if it names a folder under `Projects/`, use it.
3. **Ask** — else STOP and ask Daniel *"Which project are we working in? (e.g. AGY_AVIATIONCHAT)"* — never guess.

Set `PROJECT_ROOT = Projects/<name>` and **echo exactly** `Target: Projects/<name>` before any work.

**Binding rule (applies to EVERY step below):** every "THIS repo", every `{project-root}`, and every bare
path (`_bmad-output/…`, `_bmad/…`, `_artifacts/…`, story files, `sprint-status.yaml`) resolves **under
`PROJECT_ROOT`**. When you invoke any nested `bmad-*` skill, bind its `{project-root}` to `PROJECT_ROOT` and
read/write only there. If a needed path is missing under `PROJECT_ROOT`, STOP and say so — never fall back to the lobby.

## Step 1 — Create the epic and its stories
Invoke the **`bmad-create-epics-and-stories`** skill for the requirements in `$ARGUMENTS` (a PRD, a fix-list
path, or a described scope — e.g. `_my_resources/open_tasks/fix_list_admin_sudoadmin.md`). It writes the epic
+ its user stories with acceptance criteria. Confirm the epic + story files exist before continuing. If the
skill stops for input (missing requirements source, ambiguous scope), surface it and STOP — never guess.

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
   - **Why** — the Probability × Impact reasoning in a line or two (what breaks, how much it hurts).
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
```

### 3b. NEW `.agents/skills/sudo-create-epics-stories-sprint/SKILL.md` (the Claude launcher)

```markdown
---
name: sudo-create-epics-stories-sprint
description: 'Command center → child project. Epic kickoff — create the epic + its stories, generate the sprint board, then interactively risk-score every story P0–P3 (test levels) with Daniel. Phase A, before the per-story dev loop. Use when the user says "create the epics and sprint" / "kick off the epic" / "sudo create epics stories sprint" from the command center.'
---

# /sudo-create-epics-stories-sprint — command center launcher (Phase A / epic kickoff)

Command-center (lobby) entry point that turns a batch of requirements into an epic, its stories, a populated
sprint board, and a Daniel-confirmed P0–P3 risk map — the step BEFORE `/sudo-write-story-tests`. Runs against
a CHILD project under `Projects/`, never the lobby.

**Execute now:** read `.agents/commands/sudo-create-epics-stories-sprint.md` (relative to the repo root) and
follow it END TO END. Its **Step 0** resolves which child to target — a leading `$ARGUMENTS` project name,
else the `_my_resources/active-project.txt` pointer, else it asks Daniel — then binds every path under that
project's root. Its **Step 3 is an interactive hard stop**: risk-score each story P0–P3 with Daniel, one at a
time. Pass `$ARGUMENTS` through verbatim; the leading token may name the project, e.g.
`AGY_AVIATIONCHAT _my_resources/open_tasks/fix_list_admin_sudoadmin.md`.
```

### 3c. UPDATE `_my_resources/diagrams_guides/tea_testing/tea_testing_work_flows_sudo.md` (lobby only — not synced)

Daniel-directed edit (protected area, explicit go-ahead). Surgical changes:
- **§9** (9 workflows table + mermaid): change `test-design` "Fires" to *"epic kickoff — final interactive
  step of `/sudo-create-epics-stories-sprint`"*; redraw the mermaid so test-design sits in the kickoff, feeding ①.
- **§10** (sudo orchestrators table): add a row for `/sudo-create-epics-stories-sprint` (Phase A / epic
  kickoff: stories + sprint + interactive P0–P3 risk-score).
- **§11** (the sudo dev flow): add the **two-phase** framing + the **8-step** mapping table (from §1 here);
  update the mermaid to `BOOT → KICKOFF → ① → ② → ③ → close → commit`; add the kickoff row to the step table
  (calls: `create-epics-and-stories → sprint-planning → testarch-test-design`); replace the "> Epic setup
  (once per epic): run testarch-test-design at sprint planning" note with the kickoff command doing it as its
  interactive final step.
- Leave `tea_testing_guide.md` / `_strategy.md` untouched (out of scope; their staleness is a separate item).

## 4. Propagation sequence (after approval)

1. **Author** 3a + 3b in the **LOBBY master** (`c:\Sudo_Hatter_Command\.agents\`).
2. **Dry-run** `& ".agents/scripts/sync-agents.ps1" -WhatIf` — confirm workflow-mirror + `.claude/skills`
   creation for the new command; report the preview.
3. **Real lobby sync** `& ".agents/scripts/sync-agents.ps1"` (lobby surfaces + globals).
4. **Project syncs** (dry-run then real):
   `-Target "Projects/AGY_AVIATIONCHAT"` and `-Target "Projects/Fresh_Workspace_BMAD"` — vendor master
   `.agents/` (incl. the new command) into each + regenerate surfaces.
5. **Gap check** — if a project sync doesn't vendor `.agents/skills/<name>/`, hand-copy the two master files
   into that project's `.agents/` and re-sync (fallback only, confirmed by the dry-run).
6. **Update the doc** (3c) — lobby-only single-file edit; no propagation.

## 5. Verification plan

- Command + SKILL launcher present in **all three** repos' `.agents/`; `.claude/skills/<name>/SKILL.md` and
  `.agents/workflows/<name>.md` present in all three.
- Report the per-surface counts `sync-agents.ps1` prints for each run.
- Doc: §9/§10/§11 reflect the kickoff command + interactive test-design; the two mermaids render (validate
  syntax); the 8-step table present.
- No changes to sibling commands, `bmad/`, or project-owned `rules/`/`skills/` (additive only).

## 6. Resolved decisions + one remaining optional

- **Name**: `sudo-create-epics-stories-sprint` (kept). **Requirements input**: explicit source; STOP+ask if
  missing. **test-design**: folded as the interactive final hard stop (per Daniel).
- **OPTIONAL, not in this plan unless approved**: refresh the other 6 sudo commands' one-line "Flow position:"
  headers to include the new kickoff step (6 master files → sync propagates). Cosmetic consistency only; left
  out to keep this change focused. Say the word and I'll fold it in.
