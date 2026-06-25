---
description: "BMAD-compliant live QA pipeline — Scribe captures bugs → SM (Bob) writes story → PM (John) updates docs. Dev happens in a SEPARATE chat."
---

# Live QA & Bug Capture Pipeline

A structured loop where **you fly the app and dictate bugs**, and I capture them as your QA Scribe. When testing is done, we invoke the proper BMAD agents (SM → PM) to formalize the bugs into a story and update documentation. **Development happens in a separate chat.**

> [!IMPORTANT]
> **This workflow does NOT write code.** It produces a story artifact that a Dev agent implements in a new conversation. This is by design — Role Isolation prevents the Scribe/PM/SM from touching source code.

---

## Pipeline Overview

| Phase | Role | Agent/Skill | Trigger | Output |
|-------|------|-------------|---------|--------|
| 0 | Boot | (workflow) | `/1_live-user-QA-bugs` | Fresh artifacts, context loaded |
| 1 | Environment | (workflow) | Automatic | Backend + frontend running |
| 2 | **Scribe** | (you dictate, I log) | Continuous | `live-qa-log.md` filled with bugs |
| 3 | **SM (Bob)** | `bmad-agent-sm` → `bmad-create-story` | "Let's fix these" | Story in `_bmad/bmm/stories/` |
| 4 | **PM (John)** | `bmad-agent-pm` | After story approved | `active-context.md` + specs updated |
| 5 | Close | (workflow) | "wrap up" | Session summary, handoff instructions |
| — | **Dev** | `bmad-agent-dev` or `bmad-dev-story` | **NEW CHAT** | Code implementation |

---

## Phase 0: Session Boot + Housekeeping

### 0a. Load Context

Read `_bmad-output/active-context/active-context.md` and output a brief summary:
- Current sprint objective, what's working vs. broken, files in play, known pitfalls.

### 0b. Archive Existing Artifacts

Check the brain directory for `walkthrough.md`, `task.md`, and any `*-bugs.md` / `*-log.md` files.
- **Meaningful content** → rename with date suffix (e.g., `live-qa-log-2026-04-14.md`)
- **Empty stubs** → delete
- **User says skip/delete** → obey

### 0c. Create Fresh Artifacts

**`live-qa-log.md`** (in brain directory):
```markdown
# Live QA Bug Log

**Session Date:** {{date}}
**Tester:** Daniel (manual browser testing) | **Scribe:** Woz (logging)

---

## Open Bugs
*Standing by. Test the app and dictate bugs.*

## Resolved Bugs
*None yet.*
```

**`task.md`** (in brain directory):
```markdown
# Live QA Session — Task Tracker

## Active
- [/] Phase 2: Scribe Mode — logging bugs as discovered

## Completed
```

Confirm: > *"Context loaded. Fresh bug log ready. Starting dev environment now."*

---

## Phase 1: Start Development Environment

### 1a. Kill Zombie Processes

// turbo
```powershell
taskkill /F /IM uvicorn.exe 2>$null; taskkill /F /IM python.exe 2>$null; taskkill /F /IM node.exe 2>$null; Write-Host "Ports cleared."
```

### 1b. Start Backend

// turbo
```powershell
cd c:\Sudo_Hatter_Command\{{PROJECT_ID}}-AGY
backend\.venv\Scripts\uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Wait for: `Application startup complete`

### 1c. Start Frontend

// turbo
```powershell
cd c:\Sudo_Hatter_Command\{{PROJECT_ID}}-AGY\frontend
npm run dev
```

Wait for: `Local: http://localhost:3000/`

Confirm: > *"Dev environment is up. Head to `http://localhost:3000` and start testing. I'm in **Scribe Mode** 📋 — dictate bugs as you find them. Say **'Let's fix these'** when ready."*

**Troubleshooting:**
- `Module not found` → run from `c:\Sudo_Hatter_Command\{{PROJECT_ID}}-AGY`
- Frontend `Exit Code 1` → port in TIME_WAIT; wait 5s and retry
- Port 8000 occupied → `netstat -ano | findstr :8000`

---

## Phase 2: Scribe Mode — Bug Logging

> **You are a SCRIBE only.** Listen, log, confirm. Do NOT research root causes. Do NOT write code. Do NOT invoke skills.

For every bug dictated, append to `live-qa-log.md` under **Open Bugs**:

```markdown
### [Bx] — [Short Title]
- **[ ] Status:** Open
- **Observed Behavior:**
- **Expected Behavior:**
- **Suspected Area:** (page / route / agent / SSE / Firestore)
- **Severity:** High / Medium / Low
```

Reply: > *"Logged **[Bx]**. Keep going, or say **'Let's fix these'** when ready."*

If the user asks a question mid-testing, answer briefly, then return: *"Back in Scribe Mode."*

---

## Phase 3: Story Creation — Invoke SM (Bob)

> **Trigger:** "Let's fix these", "fix it", "ready to fix", or similar.
> **You MUST invoke the `bmad-agent-sm` skill now.** You are no longer the Scribe — Bob (SM) takes over.

### 3a. Handoff to Bob

**Invoke `bmad-agent-sm` with this context:**

> *"Bob, I have a `live-qa-log.md` artifact from a live QA session. I need you to use `bmad-create-story` (CS) to turn these bugs into a proper story spec. The bug log is in the brain artifacts directory. Please read it, group related bugs, do root cause research on the relevant source files, and generate the story in `_bmad/bmm/stories/`."*

### 3b. Bob's Responsibilities (via `bmad-create-story`)

Bob will:
1. Read the `live-qa-log.md` artifact
2. Group related bugs by component/area
3. Grep/read relevant source files for root cause analysis
4. Update each bug entry in `live-qa-log.md` with root cause + files involved
5. Generate a properly named story file in `_bmad/bmm/stories/` using the three-decimal convention:

```
story-[epic].[parent-story].[fix-seq]-[slug].md
```

| Part | Meaning | How to determine |
|------|---------|-----------------|
| `[epic]` | Active epic | From `active-context.md` |
| `[parent-story]` | Story whose feature area has the bugs | Most-affected story |
| `[fix-seq]` | Fix batch number | `.1` first round, `.2` second, etc. |
| `[slug]` | 2-4 word kebab-case description | |

**Examples:** `story-4.27.1-hanger-talk-display-fixes.md`, `story-4.17.2-socratic-loop-regression.md`

6. Present the story for user approval

### 3c. User Approves the Story

> *"Story written. Say **'Approve story'** to move to doc updates, or suggest changes."*

**Wait for explicit approval. Do NOT proceed without it.**

---

## Phase 4: Documentation Update — Invoke PM (John)

> **Trigger:** User approves the story.
> **Invoke `bmad-agent-pm` now.** Bob (SM) hands off to John (PM) for documentation.

### 4a. Handoff to John

**Invoke `bmad-agent-pm` with this context:**

> *"John, we just completed a live QA session and Bob wrote a bug-fix story: `[story filename]`. I need you to update our documentation to reflect what was found. Please:*
> 1. *Update `active-context.md` — add confirmed bugs to 'What's Broken', update 'Files Currently In Play'*
> 2. *Ghost check relevant component specs (`specialist-pipeline.md`, `socratic-teaching.md`, `admin-grading.md`, `frontend-sse.md`, `dashboard-mastery-ui.md`) — fix any stale entries*
> 3. *Update the PRD or epics list if the bugs reveal a gap"*

### 4b. John's Responsibilities

John will:
1. Read `active-context.md` and the new story
2. Update "What's Broken" and "Files Currently In Play" sections
3. Check relevant component specs for ghost entries or contradictions
4. Fix any stale documentation
5. Report what was updated

Report: > *"Docs updated. Ghost check complete. [X ghosts fixed / None found]."*

---

## Phase 5: Session Close & Dev Handoff

> **Trigger:** "wrap up", "we're done", "close session", or PM finishes doc updates.

### 5a. Update task.md

Mark all phases complete in the task tracker.

### 5b. Generate Handoff Summary

Present this to the user:

```
### ✅ QA Session Complete

**Bugs Logged:** [count — B1, B2, ...]
**Story Created:** [story filename + link]
**Docs Updated:** [list of files John touched]
**Ghost Fixes:** [count or 'None']

### 🤝 Your Next Steps
- [ ] Open a **new chat** for development
- [ ] Tell the dev: "Dev this story: [story filename]"
- [ ] Or invoke: `/bmad-dev-story` with the story file
- [ ] After dev is done, return here or start a new QA session

### ⚠️ Do NOT implement in this chat
This chat was PM/SM work. Dev must happen in a separate conversation
to maintain Role Isolation and prevent context contamination.
```

> *"Session wrapped. Story is ready for a dev agent in a **new chat**. Good flight! ✈️"*

---

## Quick Reference: Which Agent Does What

| Task | Agent | Skill to Invoke | Can Write Code? |
|------|-------|-----------------|-----------------|
| Log bugs | Scribe (you) | None — just listen and log | ❌ |
| Write story spec | Bob (SM) | `bmad-agent-sm` → `bmad-create-story` | ❌ |
| Update docs/PRD | John (PM) | `bmad-agent-pm` | ❌ |
| Implement fixes | Amelia (Dev) | `bmad-agent-dev` or `bmad-dev-story` | ✅ **NEW CHAT ONLY** |
| Review code | Quinn (QA) | `bmad-agent-qa` or `bmad-code-review` | ✅ (patches only) |
