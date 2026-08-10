---
name: artifacts-always-first
description: "The single source of truth for the plan-first artifact protocol. Create implementation_plan.md and get explicit approval BEFORE modifying ANY project file. Track with the live TodoWrite task list. A session/story closes with TWO living docs: implementation_plan.md (+ appended ## Self-Audit) and walkthrough.md (outline ## Task Checklist + ## Evidence + ## Suite Ledger + appended ## Code Review + ## Your Actions). No standalone audit/smh-review files, no task-list.md / your-action-required.md. No exceptions."
---

# Artifacts — Always First

> **Shared memory follows ownership, never cwd or tool.** Work about a directory under `Projects/` goes to
> that project's own `_artifacts/`, even when the chat starts in the home base. Read the project's
> `_artifacts/AGENTS.md` FIRST; its local buckets win. The only alternative is an explicit Sudo-managed
> exception in the home router. The current complete exception set is `Fresh_Workspace_BMAD` and
> `OpenChat-Openrouter`; their operational history stays in the matching home-base `_artifacts/<name>/`.
> Main/home-base/cross-project work goes to `_artifacts/_main/`. The store is shared by Claude, opencode,
> Antigravity/Gemini, and Codex so every agent can read past sessions. Full model →
> `docs/workspace-standard.md`.
>
> **⛔ The store is ALWAYS `_artifacts/`.** The old names `_claude_artifacts/` and `_opencode_artifacts/` are
> **RETIRED/DELETED** — **never create them**, whatever tool or skill you are running (`/bmad-dev-story`,
> `/bmad-quick-dev`, autopilot, or a hand session). If an instruction or a story's `source:` line mentions
> `_claude_artifacts/`, that is dead history — write to `_artifacts/` (a story → `_artifacts/epic_<E>/<story>/`).

## The Lean Artifact Set

Keep it minimal — **TWO living docs** per session, hard-budgeted:

1. **Task list** — DURING work, the live `TodoWrite` list is the single tracker (Daniel watches it
   update live). AT COMPLETION its end-state becomes the walkthrough's **`## Task Checklist`** outline
   (§5) — never a separate file, never a hand-maintained parallel `task.md`.
2. **`implementation_plan.md`** — the plan Daniel signs off on (the "approved" gate) AND the pre-dev
   audit's home: `/cicd-self-audit` **appends its `## Self-Audit (<date>)` section here** (§7). A
   living pre-dev doc — no standalone audit file.
3. **`walkthrough.md`** — the SINGLE closing doc, outline-first (§5): header → **`## Task Checklist`**
   (the task outline — pitfalls/findings indented under the tasks that fought back) →
   **`## Evidence`** (the ONE AC→evidence matrix + LATEST suite totals + SHA) → **`## Suite Ledger`**
   → **`## Code Review (<date>)`** (appended by the review, §6) → **`## Your Actions`** (LAST — what
   landed + what's still on Daniel). Everything final lives here; the review appends, never forks.
4. **`bug-list.md`** — ONLY for debugging / live-testing sessions. A simple bug list.

**Dense, not short — and there is NO byte cap.** Both docs are re-read on every pass of the loop: the
dev writes the plan, `/cicd-self-audit` appends into it (§7), the reviewer reads it, close-out reads it
before flipping status. Every line is paid for repeatedly, so every line must earn it — a decision, a
constraint, a finding, or evidence. Cut restatement of the codebase, narrative filler, and context
already stated elsewhere. Test evidence is totals lines + SHA, never reporter dumps; a re-run REPLACES
the pasted totals (git keeps history) — only the `## Suite Ledger` accretes rows. Feels bloated →
compress in place (pointers to git / the story file), **never a new file**.

> ⛔ **Length is NEVER a reason to omit a finding, an AC, or a piece of evidence.** A plan that grew
> because the audit found eight real things is working correctly. Truncating substance to hit a number
> is the failure this rule exists to prevent — not the outcome it wants.
>
> *Hard caps (8 KB / 10 KB) were set 2026-08-02 and **removed 2026-08-08 (SCC-51, operator ruling).**
> They shipped in the same commit that made `implementation_plan.md` a TWO-author doc (plan + audit),
> and the number was never validated against a real audit; the first Full audit run under it had to
> compress its own findings to fit. The discipline stays, the number is gone.*

> Do NOT create: a parallel `task.md`, a standalone `task-list.md` / `your-action-required.md`,
> index/`00_artifacts-list.md` files, the verbose `debug-watch-log.md`, a standalone
> `self-audit-stress-test.md` (§7), or a standalone `code-review.md` /
> `cicd-code-review-<story>.md` (§6) — audits live IN the plan, reviews live IN the walkthrough.
> Stories closed before 2026-08-02 carry the old standalone files: valid history, read them there,
> never write new ones. TEA test-artifacts (`atdd-checklist-*`, `automation-summary-*`,
> `certification-*.json` under `_bmad-output/test-artifacts/`) are OUT of this set by design and stay
> standalone. The rest of the flow is identical for normal dev and stories.

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

**Pick the location by artifact ownership:**
- **Project-owned default:** work about any `Projects/<name>/` directory that is not in the exception
  registry goes to `Projects/<name>/_artifacts/…`, regardless of cwd or tool. If the project-local store is
  missing, create its standard skeleton; never create a home-base fallback bucket.
- **Sudo-managed exception:** work about a name explicitly listed in the home `router.md` exception registry
  goes to the matching home-base `_artifacts/<name>/…`. The complete current set is
  `Fresh_Workspace_BMAD` and `OpenChat-Openrouter`. An exception must be explicit; never infer one.
- **Home-base ownership:** main/home-base/cross-project work (the standard, master `.agents/`, router, lobby
  wiring) goes to `_artifacts/_main/…`.
- **Tool identity never changes ownership.** Claude, opencode, Antigravity/Gemini, and Codex all write to the
  same owning store. Do not create a tool-specific duplicate of project history.
- **For a project-owned store, open `Projects/<name>/_artifacts/AGENTS.md` BEFORE choosing a bucket.** That
  local law overrides the generic task-type list below and may define debugging, TEA, or structured-debug
  buckets. Continuity is the project's own brief (`active-context.md`, or
  `_bmad-output/active-context/active-context.md` in a BMAD project), not the home-base ledger. The project
  keeps a local `_main/` holding bucket for project infrastructure or work with no better home. Story work
  nests under `epic_<N>/`; nothing is dated at the project `_artifacts/` root.

**Then find the parent and name the folder by task type — pick the FIRST that matches (in either location):**
- **Story** (work tied to a story id `E.S`) → `epic_<E>/<story>/` — an **epic folder houses all of its
  stories** (create `epic_<E>/` if it isn't there yet), so stories group under their parent epic
  (e.g. `epic_14/story-14.6-graph-insight/`, or an autopilot run `epic_14/2026-06-27_autopilot-14-6/`).
  Epic-scoped, not date-prefixed at the root. This holds for **any** story — whether the autopilot, a BMAD
  flow, or Daniel devs it by hand; the parent is decided by the story id, **not** by the tool.
- **Quick fix** (**neither a story nor a bug-fix story**: infra/tooling/config repair, a recorded
  follow-on, one-off maintenance — anything that still deserves a record but does not earn a story)
  → the owning store's `quick_fixes/quick-fix-<track>.<n>-<slug>/`. **Operator ruling 2026-08-03.**
  - **Numbering is a standing, always-open track** — track `1`, items `1.1`, `1.2`, `1.3`, … continuing
    in order. **The track does not close at the end of a round** — that is the point of it; a new one
    opens as `2` only if a track is deliberately retired. Read the folder's `INDEX.md` for the next
    free number; never restart at `1.1`.
  - **Mint NO story file and NO epic key.** Do not create anything in `_bmad/bmm/stories/`, and never
    hang a quick fix off a `done` epic — that silently reopens it. Board tracking, when the work is
    worth tracking, is a single `quick-fix-<track>-<n>-<slug>` key in `sprint-status.yaml`.
  - One `walkthrough.md` in the folder is the whole record (no `implementation_plan.md`), plus a row
    in `quick_fixes/INDEX.md` — that INDEX is the numbering register, so **append its row by hand**;
    it is the exception to the batch-reconcile note below.
  - This is where `/cicd-quick-dev` work lands when it turns out not to be a story, and it is the
    home for the follow-on class in `followon-fixes-are-not-a-new-story`.
- **System / infrastructure** ("systems things": the agent system, rules, scripts, CI, cross-cutting config)
  → the owning store's `_main/<YYYY-MM-DD>_<slug>/`. A quick fix that happens to touch infra matches
  the quick-fix bucket ABOVE this one — first match wins.
- **No home yet / random one-off** (everything else) → `<YYYY-MM-DD>_<slug>/` — date FIRST, slug LAST so they
  sort chronologically (e.g. `2026-06-25_artifacts-policy-finish`); slug: lowercase, hyphen-separated, max 6
  words, from the operator's first concrete request. In a project-owned store it goes inside `_main/` — the
  holding bucket — until it has a home or you make one; never use a dated folder at the project's
  `_artifacts/` root.

> **The `INDEX.md` ledger is reconciled in batch — do NOT hand-append a row every session.** That machinery
> already exists: the SessionStart hook chain runs `check_maps.py --depth3-only` and
> `record_map_changes.py --nag`, and `/smh-update-maps-indexes` does the real pass (audits every `INDEX.md`,
> reconciles `AGENTS.md`/README pointers against disk). Getting the artifact into the **right folder** is the
> per-session obligation — the ledger catches up on its own, and it is run deliberately, on cheaper agents.
> Append a row by hand only when you are the only one who can write it: a session whose "What" needs context
> a mechanical reconciler cannot recover.

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
  type: implementation_plan | walkthrough | bug_list
  date: <YYYY-MM-DD>
---
```

> **On mobile/web runs** (`CLAUDE_CODE_REMOTE=true`), also add **`mobile: true`** under `ArtifactMetadata`
> and prefix the artifact's title + `INDEX.md` row with **📱**, so mobile-made artifacts are findable later
> for a desktop re-pass — see `mobile-mode.md` Override 3.

**Paste the plan FULLY inline in the chat** AND link the artifact. Not a summary, not "key points", not a
link with a teaser — the whole plan, in the conversation, so Daniel can approve or redirect without opening
a file. A link alone (or a digest of a plan he cannot see) is a **gate violation**, not a style choice:
he is being asked to approve something he has not been shown.

Only exception: a genuinely long plan may lead with the decisions and trade-offs in full and link the
exhaustive file-by-file appendix — the reasoning he must judge is never the part abbreviated. That is a
judgement about what he needs in front of him, never a byte count. Same principle as
`operator-profile.md`: narrative briefing first, compressed record second.

### 3. STOP — wait for the gate phrase
Do nothing else. Do not "prepare" files, update story status, or touch `sprint-status.yaml`
until you hear **"approved"**.

**Granularity:** every story AND every code-touch gets its own plan + sign-off. An
epic-level plan is NOT a license to implement stories without per-story approval.

### 4. Execute
Now — and only now — modify project files. Update the TodoWrite list (`pending` → `in_progress`
→ `completed`) as you go so Daniel can watch progress live.

### 5. Write `walkthrough.md` (after completion — the ONE closing doc)
An **outline, not a narrative** — the task list IS the structure; prose exists only where something
fought back. In this order:

1. **Header** (a few lines) — story/session link, status, branch + commit range.
2. **`## Task Checklist`** — the task outline (replaces the old narrative + checklist pair): the
   final `TodoWrite` snapshot, `[x]`/`[ ]` per task; under a task, ONLY indented bullets for what
   fought back — pitfalls hit, findings, plan-vs-built deviations, and how each was resolved. A task
   that went clean gets NO sub-bullets (clean is the default reading). Deferred `[ ]` rows carry a
   one-line reason.
3. **`## Evidence`** — the ONE AC→evidence matrix (the only copy anywhere — the story file and
   review link here, never restate), the LATEST full-suite totals + `git rev-parse HEAD` **actually
   pasted** (never fabricated; totals lines only), and a one-line static-checks result. A re-run
   REPLACES the totals; the Suite Ledger keeps the history.
4. **`## Suite Ledger`** — one row per suite invocation this story: `scope · command · duration ·
   result · why this run`. The certification row carries the SHA; the review step appends its rows.
5. **`## Code Review (<date>)`** — appended by the review step (§6), never pre-written by the dev.
6. **`## Your Actions`** (LAST) — what landed (the `claude/*` branch, the commit range, whether it
   reached the epic branch) plus anything still on Daniel: an epic promotion to `main` via
   `/cicd-push-e2e`, a live check, a decision.
   Also posted in chat. The review step attempts any agent-solvable row here and ticks it; only
   genuine human calls survive. Not a `git add` block — the agent commits its own work in the
   worktree and lands it at close-out (→ `git-policy` · `worktree-per-story`).

Do NOT split any section into a separate file — one doc holds the outline, the evidence, the review,
and the actions.

### 6. Append `## Code Review (<date>)` to `walkthrough.md` (whenever a code review runs)
**Any code review — `/cicd-code-review`, `/code-review`, `bmad-code-review`, or an ad-hoc review —
writes its findings INTO the session/story `walkthrough.md` as a `## Code Review (<date>)` section.**
Presenting findings only inline in the chat is NOT sufficient, and a standalone review file is no
longer the home. The section carries:
- the canonical verdict line — **`Verdict: PASS|CONCERNS|FAIL|WAIVED @ <reviewed-sha>`** — plus the
  SHA the suite evidence was measured on. This line is what `/cicd-update-sprint-memory` reads before
  flipping a story to `done`; any code/test diff between that SHA and HEAD invalidates the verdict.
- scope (files/diff reviewed) and method/effort — one line each,
- **ONE findings table** (the only copy anywhere — the story file links here, never restates):
  `file:line` · severity · failure scenario · disposition (applied / deferred / dismissed),
- each gate check's result in one line, with the actual suite totals (rows also go to
  `## Suite Ledger`).

No walkthrough exists yet (an ad-hoc review outside any session)? Create the session folder + a
minimal walkthrough and put the section in it. Multiple reviews append multiple dated sections.

> **Legacy:** stories closed before 2026-08-02 hold their review at
> `_bmad-output/implementation-artifacts/sudo-code-review-<story>.md` (epics 15+) or as
> `code-review.md` in the session folder (epics 11–12). Valid history — readers fall back there when
> a walkthrough has no `## Code Review` section. **Never write a NEW review to those paths.**

### 7. Append `## Self-Audit (<date>)` to `implementation_plan.md` (whenever the pre-dev audit runs)
**Every `/cicd-self-audit` run appends its result INTO the plan it audited** as a
`## Self-Audit (<date>)` section — presenting findings only inline in the chat is NOT sufficient, and
a standalone audit file is no longer the home. The section carries: the right-size level
(Skip/Light/Full), **one line per phase walked** (what was checked and cleared — the evidence the
audit actually ran), the findings table (`file:line` · severity · failure scenario · disposition),
and the canonical **`Audit verdict: GO | NO-GO`** line. Inline `⚠️ AUDIT FINDING` flags still go in
the affected plan sections so the dev reads them in context; the section is the summary + proof.
- **Blind-handoff lane:** an external team's audit gets appended into this section (source noted in
  the heading), not copied in as a standalone file.
- **Skip lane:** one line — `Audit: skipped by human decision (<date>)`.
The plan's frontmatter `type:` stays `implementation_plan`.

> **Legacy:** stories closed before 2026-08-02 keep `self-audit-stress-test.md` — valid history;
> never write a new one.

## MD Feedback / Review Protocol
When Daniel says **"review"** (or asks to review a document/plan), EVERY agent must:
1. Immediately return to the Markdown document you were just working on.
2. Check the `md-feedback` MCP server (or read the file's `<!-- USER_MEMO -->` blocks) for Daniel's highlights, fixes, and questions.
3. Address the fixes, answer the questions, and if applicable, use the MCP tools to resolve them. **NEVER manually edit the `<!-- USER_MEMO -->` HTML blocks with standard file write tools. You MUST use the MCP server tools (`apply_memo`, `batch_apply`, etc.) to update them, or you will corrupt the document's tracking hashes.**

## When to Skip
- **Investigatory requests** ("explain how X works", "where is Y?") — no artifacts needed.
- **Trivial one-liners** (typo, comment fix) — mention what you changed; skip the full cycle.
- **Daniel explicitly says** "skip the plan, just do it" — still write a walkthrough after.
- **`/cicd-quick-dev`** — **invoking that command IS the "skip the plan" instruction above**, the same way
  invoking `/cicd-update-sprint-memory` IS the close-out sign-off. It runs no `implementation_plan.md` and
  waits for no "approved"; its gate is the human review at the end. The exemption is conditional on its
  guards staying intact — the worktree/chore branch, the acceptance criteria fixed in Step 1, the EJECT
  tripwire, and the mandatory review gate. **A fired tripwire re-arms this gate:** the moment the work
  ejects to the full lane, it is no longer exempt and needs an approved plan like anything else.
  - Its record is **spec + thin walkthrough**: the spec the skill writes (in `_bmad-output/`) is the
    working doc; the `walkthrough.md` in the owning `_artifacts/` store **links** it rather than restating
    it, and still carries `## Task Checklist` → `## Evidence` → `## Code Review (<date>)` (with the
    canonical `Verdict:` line) → `## Your Actions`. The walkthrough is never skipped.

## Hard Stops
- NEVER modify any project file before `implementation_plan.md` is approved.
- NEVER manually edit MD Feedback HTML blocks (`<!-- USER_MEMO -->`, `<!-- PLAN_CURSOR -->`, `<!-- CHECKPOINT -->`). You MUST use the `md-feedback` MCP tools to resolve feedback to avoid breaking document hashes.
- NEVER skip the artifact folder for a "quick" change (outside the Skip cases above).
- NEVER place an artifact inside a project without first reading that project's `_artifacts/AGENTS.md` — it is
  the local law, it overrides §2's task-type list, and it names buckets this rule does not.
- NEVER write/update an artifact — or name a file or path in chat — without posting a clickable Markdown
  link to it that same turn (see the "Link every artifact — and every file — in the chat" rule above).
- NEVER claim the walkthrough is done without actual test output (totals + SHA in `## Evidence`).
- NEVER finish a `walkthrough.md` without its `## Task Checklist`, `## Evidence` (+ `## Suite Ledger`
  for story work), and `## Your Actions` sections (what landed + what's still on Daniel lives in the latter).
- NEVER write the task outline, evidence, review, or "Your Actions" as separate files — they are sections inside `walkthrough.md` (§5).
- NEVER let a living doc blow its budget (see The Lean Artifact Set) — compress in place; a re-run
  REPLACES pasted totals, only the `## Suite Ledger` accretes.
- NEVER edit a project file for a commit-producing lane before opening its worktree — story and Task lanes alike (SCC-62: story → `claude/*` off the epic branch, ad-hoc/Task → `chore/*` off `main`) — then commit your own work inside it freely (explicit paths, never `git add -A`). Landing on the epic branch needs Daniel's sign-off; `main` is his alone (via `/cicd-push-e2e` for an epic, `/smh-close-task-merge-tree` for a Task). Full policy → the `git-policy` + `worktree-per-story` rules.
- NEVER deliver code-review findings inline-only — append the `## Code Review (<date>)` section to the
  walkthrough (§6); never mint a standalone review file (legacy paths are read-only history).
- NEVER deliver `/cicd-self-audit` findings inline-only — append the `## Self-Audit (<date>)` section
  to the plan (§7); never mint a standalone audit file.

## Why this matters
Artifact files are Daniel's primary interface for reviewing session work, and the shared `_artifacts/`
store is the cross-project memory every agent reads. Skipping this breaks the entire collaboration model.
