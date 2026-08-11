---
description: Session boot / BMAD story pick-up — reads active-context + sprint-status, loads in-scope component specs, surfaces the next story and which cicd- command to run, confirms guardrails before work begins. Pairs with /cicd-update-sprint-memory (the close-out save).
platforms: [opencode, antigravity]
---

# /cicd-boot-sprint-memory — Session Boot + Story Pick-Up

Self-contained — no external workflow file. Project-scoped: reads THIS repo's `_bmad-output/`.
Quick-start to ground yourself at the beginning of any session.
Discovery only — after completion, **do NOT start coding; wait for Daniel's next instruction.**

## Step 0 — Resolve the target project (FIRST — before any other step)
Bind the target per `.agents/rules/smh-target-resolution.md` **§ASK** + §BIND: self fast-path →
`$ARGUMENTS` override (this command is the normal place to set the session's active project) → else do
NOT silently reuse the pointer — **ASK Daniel** *"Active project is `<pointer, or none>`. Which project
this session?"* with the `Projects/` list (a project he already named in this chat counts — don't
re-ask). Never guess, never operate on the lobby. Set `PROJECT_ROOT` and **echo exactly**
`Target: Projects/<name>` before any work; every bare path below resolves under `PROJECT_ROOT`, and a
needed path missing there → STOP and say so.

> **If the answer is the lobby (`SCC` / `Sudo_Hatter_Command`), this command does not apply — answer
> anyway, don't dead-end.** The command centre has no `_bmad-output/`, no sprint YAML and no story
> files, so every step below has nothing to read. That is not a missing feature: the lobby's work is
> **Tasks on the Jira board**, and the board is the whole queue there. Say so in one line, then run the
> queue read from `.agents/rules/jira.md` §The queue (`In Progress` → `To Do Next` → `To Do`, first
> non-empty rank wins; `Blocking` reported separately as impediments) and hand the operator the next
> card with `/smh-close-task-merge-tree` named as its close-out. Do **not** bind a project to work around
> this, and do **not** silently retarget to a project he didn't ask for.

## Step 1 — Read active context
Read `_bmad-output/active-context/active-context.md` and output a `<context>` block summarizing:
- **Sprint Objective** — what are we working on?
- **Stable** — what's tested and working (the "Do NOT Touch" set)?
- **Broken** — what's known-broken or in review?
- **In Play** — which files are currently being modified?
- **Pitfalls** — active-context only POINTS at them now: GREP `_bmad-output/active-context/known-pitfalls.md`
  for the next story's files/components and surface ONLY the matching entries — never bulk-load that file.

## Step 1.5 — Read THIS project's memory store (SCC-73)
Read `<PROJECT_ROOT>/_artifacts/_memory/MEMORY.md` — the project's own memory index — and open the
files relevant to the story you are about to pick up.

**Why this step exists.** The memory store is two-tier. The lobby index you loaded at session start
holds cross-project law; the facts that are true only inside *this* project are **relocated** into
its own store, so they are **not** in the index you already have. Skip this and the boot is missing
exactly the project-specific hazards it exists to surface — the harness quirks, the chokepoints, the
gotchas that cost someone a session the first time.

If the file does not exist, the project simply has no memories yet — say so in one line and move on.
It is a beginning, not a fault.

## Step 2 — Load in-scope component specs
For each spec flagged in-scope (or implied by the sprint objective), read it from
`_bmad-output/component-specs/` and note its **Invariants** section. If none are flagged, say:
> "No component specs flagged in-scope. I'll load specs as needed based on what we work on."

## Step 2b — Sprint status & the next story (the story "pick up")
Read `_bmad-output/implementation-artifacts/sprint-status.yaml` — post-split (Wave 4, 2026-08-03) it is
~62 KB of bare `key: status` rows and fits one read. **Row narrative is NOT there anymore**: what
happened on a story lives in `_bmad-output/history/<epic>/<key>.md` (and the change log in
`_bmad-output/history/CHANGELOG.md`) — read those only for the specific rows you need. Report, compactly:
- **Story states** — counts by status (`ready-for-dev` / `in-progress` / `review` / `done`).
- **Next story to pick up** — the top `ready-for-dev` (or the current `in-progress`), with its file under
  `_bmad/bmm/stories/`. ⛔ A `descoped` or `deferred` story is **never** recommended, whatever its
  position in the YAML.
- ⭐ **The board's `To Do Next` OVERRIDES that computed pick.** Run the rank-2 read from
  `.agents/rules/jira.md` §The queue for this project's Jira key:
  `acli jira workitem search --fields "key,summary,status" --jql 'project = <KEY> AND status = "To Do Next" ORDER BY key'`.
  Anything it returns is what the **operator chose by hand**, and it wins — the YAML lags *by design*
  (② and ③ never write it, only close-out does), so a stale computed row must never displace a card he
  placed himself. A board without the column returns **zero rows and exit 0**, not an error — fall
  straight through to the YAML pick and say nothing about it. When the two disagree, **report both**
  ("board says `<key>`; the YAML's next `ready-for-dev` is `<id>`") and lead with the board — never
  silently swap one for the other.
- **Next command** — which `cicd-` step it needs: not-started → `/cicd-write-story-tests`; mid-dev →
  `/cicd-dev-story-tests`; built & awaiting review → `/cicd-code-review`. For a story the YAML calls
  `review`, **never recommend close-out off that status** — resolve it from the artifact:
  - ⛔ **Read the verdict — never infer it — and a stale verdict is not a verdict.** A lane's verdict
    lives in its `_artifacts/epic_*/story-*/walkthrough.md` under `## Code Review`, first line
    `Verdict: PASS | CONCERNS | FAIL | WAIVED @ <sha>` (since 2026-08-02). Pre-2026-08-02 lanes keep a
    standalone `sudo-code-review-<story>.md` / `code-review.md` — **read-only history**; fall back to it,
    never write a new one. No `## Code Review` section and no legacy file = the review never ran,
    whatever the YAML says → `/cicd-code-review <id>`.
  - Then check the SHA. `PASS`/`WAIVED` whose `@ <sha>` **is** that branch's current HEAD →
    `/cicd-update-sprint-memory`. `@ <sha>` that is **not** HEAD → code landed after the review →
    `/cicd-code-review <id>`, **never** close-out. `FAIL`/`CONCERNS` → `/cicd-code-review <id>`.
  - ⛔ Two or more lanes of the same epic sitting at a fresh pass are **ONE** recommendation —
    `/cicd-merge-epic-workingtrees <epic>` — not N× `/cicd-update-sprint-memory`.
- ⛔ **A story with a LIVE WORKTREE is in flight — the YAML does not get a vote.** The YAML lags by
  design: ② and ③ never write it, only close-out does. Map the story file's `Status:` straight to the
  recommendation; never send a story whose tree already exists back to ① `/cicd-write-story-tests`.
- **Worktree** — run `git worktree list` and report whether the next/in-play story already has a
  `claude/<JIRA-KEY>-<story-slug>` tree (`worktree-per-story` → "Resuming"). If it does, say so with its path and branch
  (*"Story <id> → worktree open at `<path>` on `claude/<JIRA-KEY>-<slug>` — the next `cicd-` step re-enters it, does not
  open a new one"*); the story file and red tests may live ONLY in that tree, so any resumed dev/smh-review work
  must `cd` in first.
- **⚠️ No worktree is NOT proof of a fresh start — check the remote before you say so.** Worktrees are
  machine-local (`.claude/worktrees/` is not in the repo), and Daniel works one sprint across desktop,
  laptop, and mobile. Whenever `git worktree list` shows nothing for the next story, ALSO run
  `git ls-remote --heads origin 'refs/heads/claude/*'`. A `claude/<JIRA-KEY>-<story-slug>` branch on origin means the
  step was already done on another machine — report it as **"exists on origin, not on this machine"** and
  point at `/cicd-resume` to re-create the working surface. Only when BOTH are empty may you say the next
  step opens a worktree at first edit.
Read-only — cross-check against live files; never edit anything.

> **⛔ This is NOT the master "pick up."** The home-base `pick up` trigger (`AGENTS.md` §7 / `router.md`)
> is the continuity behavior for ALL work — code OR not (research, docs, routing). This step is the
> BMAD-story/sprint-scoped sibling and does NOT replace or modify it.

## Step 3 — Confirm guardrails active this session
- **Component-spec compliance** — check specs before modifying spec'd components.
- **Targeted edits only** — no full-file rewrites.
- **Agent authority boundaries** — each agent has a single responsibility.
- **Shared-resource singleton** — one client per shared resource (DB / auth / cache), via the
  project's factory (per the constitution).
- **Research-first** — read files before editing them.

## Step 4 — Ready
Say:
> "Context loaded. [Sprint objective]. [N in review / all clear]. Next: [story id] → run [cicd- command]. Ready — what's the plan?"
Then stop and wait. (Close the session later with `/cicd-update-sprint-memory`.)

Optional additional input: $ARGUMENTS
