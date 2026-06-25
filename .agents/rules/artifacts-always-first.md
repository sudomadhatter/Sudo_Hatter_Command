---
name: artifacts-always-first
description: "The single source of truth for the plan-first artifact protocol. Create implementation_plan.md and get explicit approval BEFORE modifying ANY project file. Track with the live TodoWrite task list. Close with walkthrough.md (includes Your Actions). No exceptions."
activation: Always On
---

# Artifacts — Always First

> **Shared memory.** All artifacts go to the home-base store `_artifacts/<workspace>/…` (where
> `<workspace>` is the project name, or `_home` for root/cross-project work). This one store is
> written by ALL tools — Claude, opencode, Antigravity/Gemini — so any agent can read past chats and
> work. Each session also appends one line to `_artifacts/INDEX.md` (date · workspace · slug ·
> summary · status), and continuity lives in `_artifacts/<workspace>/active-context.md`.

## The Lean Artifact Set

Keep it minimal — only these per session:

1. **Task list** — DURING work, the live `TodoWrite` list is the single tracker (Daniel watches it
   update live). AT COMPLETION, snapshot the final list into a **`task-list.md`** artifact so the
   finished checklist is persisted and reviewable after the TodoWrite panel is gone (see §5b). Do NOT
   hand-maintain a parallel `task.md` during work — TodoWrite is the live tracker; `task-list.md` is
   only its end-state snapshot.
2. **`implementation_plan.md`** — the plan Daniel signs off on (the "approved" gate).
3. **`walkthrough.md`** — the closing doc. It MUST include a **"Your Actions"** section (manual
   steps + the exact git commit command). Do NOT write a separate `your-action-required.md`.
4. **`task-list.md`** — the end-of-session snapshot of the completed TodoWrite list (see §5b).
5. **`bug-list.md`** — ONLY for debugging / live-testing sessions. A simple bug list.
6. **`code-review.md`** — whenever a code review runs (see §6).
7. **`self-audit-stress-test.md`** — whenever the `/1_self-audit-stress-test` pre-dev audit runs
   (see §7). Inline-only findings are NOT sufficient — the audit is always persisted.

> Do NOT create: a parallel hand-maintained `task.md` during work, `your-action-required.md`,
> index/`00_artifacts-list.md` files, or the verbose `debug-watch-log.md`. (`task-list.md` is the
> allowed completion snapshot — it is NOT the same as a live `task.md`.) The rest of the flow is
> identical for normal dev and stories.

## The Rule

**Do NOT modify any project file until Daniel has approved a plan in the current conversation.**

"Project file" means EVERYTHING in the working tree: source code, story files,
`sprint-status.yaml`, configs, YAML, `.env`, `package.json`. The ONLY exception is the shared
`_artifacts/` memory folder itself.

## The Gate

The approval phrase is: **"approved"**

NOT approval: "ok", "sure", "looks good", "continue", "ready-for-dev", "let's go".

A plan from a prior session is NOT pre-approved. Re-present it and get fresh sign-off.

## The Sequence

### 1. Research (read-only)
Read, grep, run non-mutating commands. Understand the problem. Write to NO project file.

### 2. Create the artifact folder + plan
Folder: `_artifacts/<workspace>/<YYYY-MM-DD>_<slug>/` — date FIRST, slug LAST so they sort
chronologically (e.g. `2026-05-29_epic-9-ios-shell-meta`). `<workspace>` = the project name, or
`_home` for root-level work. Slug: lowercase, hyphen-separated, max 6 words, from Daniel's first
concrete request. Also append a one-line entry to `_artifacts/INDEX.md`.

Start the **TodoWrite task list** (this is the task tracker — no `task.md` file), then write
`implementation_plan.md` (goal, every file touched with links, execution order, open questions,
verification plan). Use the `Write` tool. Frontmatter on every artifact file:

```markdown
---
IsArtifact: true
ArtifactMetadata:
  title: <title>
  type: implementation_plan | walkthrough | bug_list | code_review | self_audit | task_list
  date: <YYYY-MM-DD>
---
```

Present the plan's key points **inline in the chat** AND link the artifact. Daniel signs off
on a plan he can see in the conversation, not just a file on disk.

### 3. STOP — wait for the gate phrase
Do nothing else. Do not "prepare" files, update story status, or touch `sprint-status.yaml`
until you hear **"approved"**.

**Granularity:** every story AND every code-touch gets its own plan + sign-off. An
epic-level plan is NOT a license to implement stories without per-story approval.

### 4. Execute
Now — and only now — modify project files. Update the TodoWrite list (`pending` → `in_progress`
→ `completed`) as you go so Daniel can watch progress live.

### 5. Write `walkthrough.md` (after completion)
A dev journal, not a diff dump: what you did step by step, what fought back and how you
solved it (say so plainly if it went clean), what changed file-by-file and why, **actual
test output pasted** (never fabricated), and any deviations from the plan. End with a
**"Your Actions"** section — Daniel's manual steps + the exact `git add / commit / push` command.
(No separate `your-action-required.md`.)

### 5b. Write `task-list.md` (after completion — snapshot the task list)
When the work is done, snapshot the final `TodoWrite` list into `task-list.md`. It is just the
end-state checklist — every task with its final status (`[x]` done / `[ ]` deferred, with a one-line
reason for anything not completed). Frontmatter `type: task_list`. This is a quick-scan record of
exactly what was tackled, so Daniel can see the list after the live TodoWrite panel is gone. Keep it
terse — it is the list, not a second walkthrough.

### 6. Write `code-review.md` (whenever a code review runs)
**Any code review — `/code-review`, `bmad-code-review`, or an ad-hoc review — MUST be saved as
a `code-review.md` artifact in the current session's `_artifacts/<workspace>/<YYYY-MM-DD>_<slug>/` folder**
(use `code-review-N.md` if a session runs more than one). Presenting findings only inline in the
chat is NOT sufficient. The artifact captures: scope (files/diff reviewed), method/effort, every
finding (file:line, severity, failure scenario, suggested fix), and a disposition checklist
(addressed / deferred) so the review is reviewable the same way plans and walkthroughs are.
Frontmatter `type: code_review`.

### 7. Write `self-audit-stress-test.md` (whenever the pre-dev audit runs)
**Every run of the `/1_self-audit-stress-test` workflow — on a plan, a story, or another agent's
audit — MUST be saved as a `self-audit-stress-test.md` artifact in the current session's
`_artifacts/<workspace>/<YYYY-MM-DD>_<slug>/` folder** (use `self-audit-stress-test-N.md` if a session
runs more than one). Presenting findings only inline in the chat is NOT sufficient. The artifact
captures: targets reviewed, audit level (Skip/Light/Full), the Phase 0–4 walk, every finding
(`file:line`, severity, failure scenario, suggested fix), and the final Go / No-Go verdict.
This persists even though the audit writes no code — it audits a *plan*, and the plan's reviewer
needs the audit on disk, not just in chat. Frontmatter `type: self_audit`.

## When to Skip
- **Investigatory requests** ("explain how X works", "where is Y?") — no artifacts needed.
- **Trivial one-liners** (typo, comment fix) — mention what you changed; skip the full cycle.
- **Daniel explicitly says** "skip the plan, just do it" — still write a walkthrough after.

## Hard Stops
- NEVER modify any project file before `implementation_plan.md` is approved.
- NEVER skip the artifact folder for a "quick" change (outside the Skip cases above).
- NEVER claim the walkthrough is done without actual test output.
- NEVER finish a `walkthrough.md` without its "Your Actions" section + the git commit command.
- NEVER close out a task without snapshotting the final task list into `task-list.md` (§5b).
- NEVER commit mid-work or `git add -A` (sweeps other teams' work). At close-out you MAY commit your OWN work via explicit paths, then **ask before `git push`** — see the `git-closeout-commits` rule. The "Your Actions" git command is still documented either way.
- NEVER deliver code-review findings inline-only — always persist them as a `code-review.md` artifact.
- NEVER deliver `/1_self-audit-stress-test` findings inline-only — always persist them as a
  `self-audit-stress-test.md` artifact (`type: self_audit`), even though the audit writes no code.

## Why this matters
Artifact files are Daniel's primary interface for reviewing session work, and the shared `_artifacts/`
store is the cross-project memory every agent reads. Skipping this breaks the entire collaboration model.
