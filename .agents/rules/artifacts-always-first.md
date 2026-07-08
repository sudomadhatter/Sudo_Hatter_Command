---
name: artifacts-always-first
description: "The single source of truth for the plan-first artifact protocol. Create implementation_plan.md and get explicit approval BEFORE modifying ANY project file. Track with the live TodoWrite task list. Close with ONE walkthrough.md that holds the narrative + Task Checklist + Your Actions (no separate task-list.md / your-action-required.md). No exceptions."
activation: Always On
---

# Artifacts — Always First

> **Shared memory.** Artifacts go **where you work FROM** (your cwd). **From the home base** → home-base
> `_artifacts/`: project work → a per-project bucket `_artifacts/<project>/…` (**create it if missing**, else
> reuse); main / home-base / cross-project work → `_artifacts/_main/…` (formerly `_home`); either way append a
> row to `_artifacts/INDEX.md`. **From inside a project** (`Projects/<name>/` is cwd) → that project's own
> `_artifacts/` + its `active-context.md`/`INDEX.md` (its rules, not this ledger). The store is written by ALL
> tools — Claude, opencode, Antigravity/Gemini — so any agent can read past chats. **opencode** writes under its
> own `_artifacts/opencode/` namespace, applying the **same rules inside it** (`opencode/<project>/`,
> `opencode/_main/`, `opencode/<project>/<epic>/<story>/`). Full model → `docs/workspace-standard.md`.
>
> **⛔ The store is ALWAYS `_artifacts/`.** The old names `_claude_artifacts/` and `_opencode_artifacts/` are
> **RETIRED/DELETED** — **never create them**, whatever tool or skill you are running (`/bmad-dev-story`,
> `/bmad-quick-dev`, autopilot, or a hand session). If an instruction or a story's `source:` line mentions
> `_claude_artifacts/`, that is dead history — write to `_artifacts/` (a story → `_artifacts/epic_<E>/<story>/`).

## The Lean Artifact Set

Keep it minimal — only these per session:

1. **Task list** — DURING work, the live `TodoWrite` list is the single tracker (Daniel watches it
   update live). AT COMPLETION, the final checklist is captured as a **`## Task Checklist` section
   INSIDE `walkthrough.md`** (see §5) — never a separate file. Do NOT hand-maintain a parallel
   `task.md` during work, and do NOT write a standalone `task-list.md`: TodoWrite is the live tracker;
   its end-state lives in the walkthrough.
2. **`implementation_plan.md`** — the plan Daniel signs off on (the "approved" gate).
3. **`walkthrough.md`** — the SINGLE closing doc; it holds everything final. It MUST end with a
   **`## Task Checklist`** section (the final TodoWrite snapshot) and then a **`## Your Actions`**
   section (manual steps + the exact git commit command). Do NOT split these off into separate
   `task-list.md` or `your-action-required.md` files — extra closing docs are wasted space and time.
4. **`bug-list.md`** — ONLY for debugging / live-testing sessions. A simple bug list.
5. **`code-review.md`** — whenever a code review runs (see §6).
6. **`self-audit-stress-test.md`** — whenever the `/sudo-self-audit` pre-dev audit runs
   (see §7). Inline-only findings are NOT sufficient — the audit is always persisted.

> Do NOT create: a parallel hand-maintained `task.md` during work, a standalone `task-list.md`, a
> separate `your-action-required.md`, index/`00_artifacts-list.md` files, or the verbose
> `debug-watch-log.md`. The final task checklist AND the "Your Actions" steps both live as sections
> inside `walkthrough.md` — one closing doc, not three. The rest of the flow is identical for normal
> dev and stories.

> **🔗 Link every artifact — and every file — in the chat, always.** The moment you write or update ANY
> artifact (plan, walkthrough, bug-list, code-review, self-audit) — or name / hand over ANY file or path —
> post a **clickable Markdown link `[label](relative/path)`** in the chat that same turn, with a one-line
> note of what it is. Daniel reviews from the conversation — a file he can't open from chat may as well not
> exist. This is the always-on **"clickable links, never bare paths"** rule from `constitution.md`, applied
> to the artifact set (and every file path alongside it).

## The Rule

**Do NOT modify any project file until Daniel has approved a plan in the current conversation.**

"Project file" means EVERYTHING in the working tree: source code, story files,
`sprint-status.yaml`, configs, YAML, `.env`, `package.json`. The ONLY exception is the shared
`_artifacts/` memory folder itself.

## The Gate

The approval phrase is: **"approved"**

NOT approval: "ok", "sure", "looks good", "continue", "ready-for-dev", "let's go".

> **On web/mobile**, typing "approved" is replaced by a **tap-to-approve chip** (`AskUserQuestion`) — a
> tap on Approve IS the gate. See `mobile-mode.md` → Override 2.

A plan from a prior session is NOT pre-approved. Re-present it and get fresh sign-off.

## The Sequence

### 1. Research (read-only)
Read, grep, run non-mutating commands. Understand the problem. Write to NO project file.

### 2. Create the artifact folder + plan

**Pick the location by where you work FROM (your cwd):**
- **When running as opencode**, prepend `opencode/` to every home-base path below. Project work goes to
  `_artifacts/opencode/<project-folder-name>/`; main / cross-project work goes to `_artifacts/opencode/_main/`;
  stories go to `_artifacts/opencode/<project-folder-name>/<epic>/<story>/`. **Never write opencode artifacts directly
  to `_artifacts/_main/` or `_artifacts/<project>/`.** An opencode session run from inside a project still follows
  the project's own `_artifacts/` rules (opencode namespace applies only at the home base).
- **From the home base** (`Sudo_Hatter_Command/` is cwd) → home-base `_artifacts/` (not opencode):
  + project work → a per-project bucket `_artifacts/<project-folder-name>/…` (e.g. `_artifacts/AGY_AVIATIONCHAT/`,
    `_artifacts/Fresh_Workspace_BMAD/`; **create the bucket if it isn't there yet, else reuse it**);
  + main / home-base / cross-project work (the standard, master `.agents/`, the router, lobby wiring) →
    `_artifacts/_main/…` (formerly `_home`). Append a row to `_artifacts/INDEX.md`.
- **From inside a project** (`Projects/<name>/` is cwd) → project-local `Projects/<name>/_artifacts/…` + that
  project's own `active-context.md`/`INDEX.md` (follow its rules, not the home-base ledger). There is no
  *cross-project* `_main` here — but the project keeps a **local `_main/`** for its own system/infrastructure
  work (the agent system, rules, scripts, CI). Story work nests under `epic_<N>/`; random one-offs are dated at
  the root.

**Then find the parent and name the folder by task type — pick the FIRST that matches (in either location):**
- **Story** (work tied to a story id `E.S`) → `epic_<E>/<story>/` — an **epic folder houses all of its
  stories** (create `epic_<E>/` if it isn't there yet), so stories group under their parent epic
  (e.g. `epic_14/story-14.6-graph-insight/`, or an autopilot run `epic_14/2026-06-27_autopilot-14-6/`).
  Epic-scoped, not date-prefixed at the root. This holds for **any** story — whether the autopilot, a BMAD
  flow, or Daniel devs it by hand; the parent is decided by the story id, **not** by the tool.
- **System / infrastructure** ("systems things": the agent system, rules, scripts, CI, cross-cutting config)
  → `_main/<YYYY-MM-DD>_<slug>/` (for opencode, under `opencode/_main/…`).
- **Random one-off** (everything else) → `<YYYY-MM-DD>_<slug>/` at the root — date FIRST, slug LAST so they
  sort chronologically (e.g. `2026-06-25_artifacts-policy-finish`). Slug: lowercase, hyphen-separated, max 6
  words, from Daniel's first concrete request.

**File names within a folder:** dated output → `YYYY-MM-DD_<slug>.md`; versioned drafts →
`<slug>_draft.md` → `<slug>_v2.md` → `<slug>_final.md`. Memory / active-context sections are
**numbered** (e.g. `5.2`) so agents skip-to-N instead of reading the whole file.

Start the **TodoWrite task list** (this is the task tracker — no `task.md` file), then write
`implementation_plan.md` (goal, every file touched with links, execution order, open questions,
verification plan). Use the `Write` tool. Frontmatter on every artifact file:

```markdown
---
IsArtifact: true
ArtifactMetadata:
  title: <title>
  type: implementation_plan | walkthrough | bug_list | code_review | self_audit
  date: <YYYY-MM-DD>
---
```

> **On mobile/web runs** (`CLAUDE_CODE_REMOTE=true`), also add **`mobile: true`** under `ArtifactMetadata`
> and prefix the artifact's title + `INDEX.md` row with **📱**, so mobile-made artifacts are findable later
> for a desktop re-pass — see `mobile-mode.md` Override 3.

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

### 5. Write `walkthrough.md` (after completion — the ONE closing doc)
A dev journal, not a diff dump: what you did step by step, what fought back and how you
solved it (say so plainly if it went clean), what changed file-by-file and why, **actual
test output pasted** (never fabricated), and any deviations from the plan. This is the **single**
closing document — it carries everything final, in this order:

1. **The narrative** above (what changed & why + pasted test output).
2. **`## Task Checklist`** — the final `TodoWrite` snapshot: every task with its end status
   (`[x]` done / `[ ]` deferred, one-line reason for anything not finished). Terse — it is the list,
   not a second walkthrough; it replaces the old standalone `task-list.md`.
3. **`## Your Actions`** (LAST) — Daniel's manual steps + the exact `git add / commit / push` command.

Do NOT split the checklist or the actions into separate files (`task-list.md`,
`your-action-required.md`) — one doc holds the walkthrough, the task list, and the actions.

### 6. Write `code-review.md` (whenever a code review runs)
**Any code review — `/code-review`, `bmad-code-review`, or an ad-hoc review — MUST be saved as
a `code-review.md` artifact in the current session's `<YYYY-MM-DD>_<slug>/` folder**
(use `code-review-N.md` if a session runs more than one). Presenting findings only inline in the
chat is NOT sufficient. The artifact captures: scope (files/diff reviewed), method/effort, every
finding (file:line, severity, failure scenario, suggested fix), and a disposition checklist
(addressed / deferred) so the review is reviewable the same way plans and walkthroughs are.
Frontmatter `type: code_review`.

### 7. Write `self-audit-stress-test.md` (whenever the pre-dev audit runs)
**Every run of the `/sudo-self-audit` workflow — on a plan, a story, or another agent's
audit — MUST be saved as a `self-audit-stress-test.md` artifact in the current session's
`<YYYY-MM-DD>_<slug>/` folder** (use `self-audit-stress-test-N.md` if a session
runs more than one). Presenting findings only inline in the chat is NOT sufficient. The artifact
captures: targets reviewed, audit level (Skip/Light/Full), the Phase 0–4 walk, every finding
(`file:line`, severity, failure scenario, suggested fix), and the final Go / No-Go verdict.
This persists even though the audit writes no code — it audits a *plan*, and the plan's reviewer
needs the audit on disk, not just in chat. Frontmatter `type: self_audit`.

## MD Feedback / Review Protocol
When Daniel says **"review"** (or asks to review a document/plan), EVERY agent must:
1. Immediately return to the Markdown document you were just working on.
2. Check the `md-feedback` MCP server (or read the file's `<!-- USER_MEMO -->` blocks) for Daniel's highlights, fixes, and questions.
3. Address the fixes, answer the questions, and if applicable, use the MCP tools to resolve them. **NEVER manually edit the `<!-- USER_MEMO -->` HTML blocks with standard file write tools. You MUST use the MCP server tools (`apply_memo`, `batch_apply`, etc.) to update them, or you will corrupt the document's tracking hashes.**

## When to Skip
- **Investigatory requests** ("explain how X works", "where is Y?") — no artifacts needed.
- **Trivial one-liners** (typo, comment fix) — mention what you changed; skip the full cycle.
- **Daniel explicitly says** "skip the plan, just do it" — still write a walkthrough after.

## Hard Stops
- NEVER modify any project file before `implementation_plan.md` is approved.
- NEVER manually edit MD Feedback HTML blocks (`<!-- USER_MEMO -->`, `<!-- PLAN_CURSOR -->`, `<!-- CHECKPOINT -->`). You MUST use the `md-feedback` MCP tools to resolve feedback to avoid breaking document hashes.
- NEVER skip the artifact folder for a "quick" change (outside the Skip cases above).
- NEVER write/update an artifact — or name a file or path in chat — without posting a clickable Markdown
  link to it that same turn (see the "Link every artifact — and every file — in the chat" rule above).
- NEVER claim the walkthrough is done without actual test output.
- NEVER finish a `walkthrough.md` without its `## Task Checklist` and `## Your Actions` sections (the git commit command lives in the latter).
- NEVER write the final task checklist or the "Your Actions" steps as separate files — they are sections inside `walkthrough.md` (§5).
- NEVER run `git commit`/`git push` yourself — the `walkthrough.md` "Your Actions" section hands Daniel the exact command. The ONLY exception: Daniel explicitly delegates a specific commit/push to you in that moment (then: your own files only, explicit paths, never `git add -A`). Full policy → the `git-policy` rule.
- NEVER deliver code-review findings inline-only — always persist them as a `code-review.md` artifact.
- NEVER deliver `/sudo-self-audit` findings inline-only — always persist them as a
  `self-audit-stress-test.md` artifact (`type: self_audit`), even though the audit writes no code.

## Why this matters
Artifact files are Daniel's primary interface for reviewing session work, and the shared `_artifacts/`
store is the cross-project memory every agent reads. Skipping this breaks the entire collaboration model.
