---
name: worktree-per-story
description: "Fires when ANY lane starts work that will produce commits — the trigger is concurrency, not work type (SCC-62, 2026-08-09). One lane, one worktree, opened BEFORE the first edit, committed freely inside, landed and pruned by its own close-out. The BASE still differs by lane: a sudo story lane takes `claude/<KEY>-<slug>` off the story's EPIC branch (never main) and is pruned by /cicd-close-story-merge-tree Step 5 (which calls /cicd-prune-worktree); ad-hoc/Task work takes `chore/<KEY>-<slug>` off main and is pruned by /smh-close-task-merge-tree Step 5. Carries the `⛔ Your tree is your world` hard stop (never touch or report another lane's files) and `⛔ cwd is not intent`. Read-only sessions and a single watched trivial edit are exempt. Pairs with git-policy.md."
---

# Worktree Per Story

> **Why this exists.** Several teams run in parallel against one checkout. Their edits interleave in the
> same files, `git status` becomes a soup of everybody's work, and whoever pushes last inherits all of
> it — so a commit titled "formalize the TEA framework" ships four unrelated sessions and the message
> can only honestly describe one of them. A worktree per story ends that. Each story gets an isolated
> tree, commits only its own files, and lands as one clean push.

## The standing environment — parallel teams are the NORM

Up to **four story lanes — sometimes more — run this system at once**: separate sessions, separate
models, sometimes separate platforms (Claude Code, opencode, Antigravity, Codex, an autopilot engine),
all against the same project repo. One story = one worktree = one `claude/<JIRA-KEY>-<story-slug>` branch is what
makes that survivable. Assume from your first command that you are NOT alone in the repo:

- **The shared checkout is a lobby, not your desk.** It stands on `main` — production — and stays
  there. Its `git status` can still show other lanes' dirty files and half-landed syncs. Never sweep,
  revert, or "fix" a file you did not change — report it and move on. (G2's explicit-paths rule exists
  precisely so several lanes can share one checkout without committing each other's work.)
- **The epic branch moves under you.** Another lane can land on `epic/<JIRA-KEY>-<slug>` mid-session, so your
  branch base is stale by default — merge `origin/epic/<JIRA-KEY>-<slug>` into the story branch before landing
  (the landing sequence in `git-policy.md`); never assume the base you opened on.
- **The board files are everyone's files.** `sprint-status.yaml`, `active-context.md`, and the sprint
  map are edited by EVERY lane — the #1 merge-conflict surface (2026-07-31: a three-block conflict
  soup was committed to active-context.md exactly this way). Resolve by keeping BOTH sides' facts —
  parallel lanes record different true things; picking a winner erases someone's work.
- **Sibling lanes collide on shared surfaces.** Two lanes have shipped the same fix from one triage
  doc; two stories have planned edits to the same function. Before landing, re-diff your branch
  against the live sibling `claude/*` branches, and honor any set-wide LANDING RULE posted on the
  project's sprint board — while one is active, no lane lands alone.

## Trigger — will this lane commit? Then it opens a worktree

**A worktree opens when a lane starts work that will produce commits — ANY lane, BEFORE the first
project file is edited.** Automatic; the agent does not ask each time, and does not first work out what
*kind* of work this is.

> **Why the trigger is concurrency, not work type.** This rule used to gate on the lane: sudo story
> lanes got a tree, ad-hoc work was *forbidden* one. That split does not match the hazard. A chore lane
> running beside a story lane collides exactly as hard as two story lanes — and it was the one told to
> sit in the shared checkout. Worse, the old wording made the agent **self-classify** ("am I in a sudo
> story lane?") and ended with *"unsure? you're not"* — which routed every ambiguous case into the
> shared checkout, the one place it must not go. **Removing the classification removes the failure.**
> The old ban existed to prevent orphan trees that no close-out would prune; that is now handled —
> `/smh-close-task-merge-tree` Step 5 prunes its own tree, exactly as `/cicd-prune-worktree` Step 3 does.
> (2026-08-09, SCC-62. Twice in one day this went wrong: SCC-61 exists because a close-out preflight
> resolved a sibling lane's branch; SCC-58 then opened onto a checkout standing on SCC-61's branch with
> 11 dirty files.)

**The tree is the default. What differs by lane is the BRANCH and its BASE — never whether you isolate:**

| Lane | Branch | Base — this does NOT change | Closed + pruned by |
|---|---|---|---|
| Sudo story lane (① · ② · `/cicd-quick-dev` · autopilot) | `claude/<JIRA-KEY>-<story-slug>` | the story's **epic branch** (`epic/<JIRA-KEY>-<slug>`) — **never `main`** | `/cicd-close-story-merge-tree` (Step 1 runs `/cicd-update-sprint-memory`'s save → Step 3 lands → Step 5 prunes via `/cicd-prune-worktree`) |
| Ad-hoc / Task work (toolkit, rules, docs, config) | `chore/<JIRA-KEY>-<slug>` | `main` | `/smh-close-task-merge-tree` (merge → Step 5 prunes branch **and** tree) |

```
EnterWorktree  →  .claude/worktrees/<slug>/  on branch  claude/<JIRA-KEY>-<story-slug>  or  chore/<JIRA-KEY>-<slug>
```

⛔ **A story lane still branches from its epic branch, never from `main`.** SCC-62 changed *who gets a
tree*, not *what they branch from* — a story cut from `main` loses every sibling's work in the epic and
breaks the landing sequence. The epic branch is cut from `main` at epic kickoff
(`/cicd-create-epic-sprint`); if it doesn't exist yet, that step was skipped — go back and run it. The
`worktree.baseRef: "head"` setting makes **`EnterWorktree`** inherit the current HEAD, so that door —
and only that door — needs you to **check out the base branch before opening the worktree**, and then
to go **back to `main`** the moment the tree is open (the shared checkout stands on `main`; see "no
reconcile after a landing" below). If you are somewhere else, get there first — or say so out loud if
you are deliberately stacking on another story's branch. `git worktree add` takes its base as an
OPERAND and needs neither trip:

```
git -C <repo> worktree add .claude/worktrees/<slug> -b claude/<JIRA-KEY>-<story-slug> origin/epic/<JIRA-KEY>-<slug>
```

**Bring the gitignored assets with you.** A worktree does not inherit `.env`, `auth_keys/` or
`node_modules` — they are not in git, so there is nothing for `git worktree add` to copy, and reading
them by absolute path does not help: pytest, uvicorn, `next dev` and the emulators resolve them
**relative to cwd**. After opening a tree in any repo that has them, run (PC: `python`, not `python3`):

```
python3 .agents/scripts/link-worktree-assets.py .claude/worktrees/<slug>
```

It links rather than copies, so the cost is seconds, not gigabytes. Two things it will tell you: a
symlinked `.env` is **shared state** across lanes (good for key rotation, one collision surface back —
use `--copy-env` if this lane will change it), and shared `node_modules` is fine for dev but the E2E
tier must run its own `npm ci`. ⛔ **`--unlink` before the tree is removed** — a recursive delete through
a junction destroys the shared target, not just the link. Both close-outs do this in their prune step.

### Exempt — no worktree needed

- **Read-only sessions** — questions, recon, code reading, reviews that write no project file.
- **A single trivial edit the operator is watching** — a one-line doc/config fix in the moment. If it
  grows a second file, open the tree.
- **`/cicd-push-e2e`** — it operates *on* branches (`epic/<JIRA-KEY>-<slug>` → `main`), so it must run in the
  main checkout.
- **Daniel says otherwise** — an explicit "just do it here" in the moment wins.

### ⛔ Your tree is your world

Isolation stops lanes from overwriting each other. It does **not** stop you from wandering into another
lane's work and treating it as yours — which is the other half of the damage, and the more common half.

- **Never sweep, revert, stage, commit, or "fix" a file you did not change.** Not even if it is
  obviously broken. Report it in one line and move on.
- **Never file another lane's in-flight state as a finding** — a half-edited file in the shared checkout
  is work in progress, not a defect.
- **Never merge, rebase onto, or delete a branch that is not yours**, and never check out a branch in
  the shared checkout to "have a look" — that moves HEAD under whoever is standing there.
- The shared checkout stands on `main`. If you find it on someone else's branch, that is a live lane:
  leave it exactly as you found it. (See `⛔ cwd is not intent` below — this is why a close-out must
  never resolve its target from cwd.)

### Am I alone in this repo? — ask, don't assume

Three commands, before the first edit. This catches the common case; **it is not what makes isolation
safe** — the worktree default is. `git worktree list` is per-repo and machine-local: it cannot see a
second *session* on the same branch, and shows nothing at all on a freshly-cloned machine.

```
git worktree list                              # other trees on THIS machine
git branch --list 'chore/*' 'claude/*'         # other lanes' branches
git status --short                             # someone else's dirty files
```

## Resuming — a fresh chat picks the story back up

A worktree outlives the chat that opened it. A **new session** — fresh context, a `/compact`, a
different model, or simply a different chat window — that resumes an in-flight story must **re-enter the
existing worktree**: not open a second one, and not work in the shared checkout. Before `EnterWorktree`
fires (and at the top of any `cicd-*` step that will read or edit story files), look first:

```
git worktree list        # is there already a  claude/<JIRA-KEY>-<story-slug>  tree?
```

- **A tree for this story slug exists** → that IS your workspace. `cd` into it and bind every path — story
  file, ① red tests, `_artifacts/…`, test commands — under it. Its branch already carries the ① / earlier-②
  commits, and **the story file and red tests often live ONLY in that tree, never in the shared checkout** —
  so a session that skips this step is blind to the very work it was invoked to continue, and will either
  re-do ① or wrongly report the story missing.
- **No tree yet** → this is the first work session; open one per the Trigger above.

Never open a second worktree for a slug that already has one, and never fall back to editing in the shared
checkout because the tree "looked empty" from where you happened to be standing. Match by the `<story-slug>`
in the branch/path, not by cwd.

## ⛔ `cwd` is not intent — pin `--repo` and `--branch` on every script

**The moment more than one lane exists, where you are standing stops being evidence of what you meant.**
`cwd` resets to the shared checkout at slash-command boundaries, at a `/compact`, and whenever a tool call
starts fresh. Every repo-resolving script in this toolkit — `task_preflight.py`, `closeout_preflight.py`,
`jira_feed.py`, `check_maps.py` — finds its target by **walking up from `cwd` looking for `.git`**, and
defaults `--branch` to whatever `HEAD` that repo happens to be on. In a lobby that a sibling lane has moved
off `main`, both defaults resolve to **that lane's work**.

**This does not fail loudly. It cannot.** The script has no way to know which story or ticket you meant, so
there is no mismatch for it to detect: it runs every check honestly and reports a clean result *about the
wrong branch*. On 2026-08-09 a Task close-out drew `VERDICT: clear to close out and merge` for a sibling's
in-flight `chore/*` branch; merging it would have put another lane's unfinished work on `main` under the
wrong ticket.

So, whenever a worktree is open anywhere in the repo — which is the standing condition here, not the
exception:

- **Pass `--repo <path>` and `--branch <name>` explicitly.** They read as optional because the script can
  guess. The guess is precisely what breaks under parallel lanes. (`task_preflight.py` goes further
  since SCC-64: `--expect-key` is **required**, and a branch whose key does not match blocks
  mechanically — the discipline here still covers every other script.)
- **Derive any `Repo | Branch` line you print from command output** — `git -C "$REPO" rev-parse
  --abbrev-ref HEAD` — never from memory. An echo written from belief can only confirm the belief; it
  cannot catch a wrong one, which is the only thing it is there for.
- **Check the script's echoed target before reading its verdict.** Name the Jira key you intend to act on
  *first*, then confirm the script resolved that same key. Mismatch → **STOP**, and say which branch it
  resolved versus which you meant.

The same shape bites in reverse when reading results: a gate piped to `head`/`tail` reports the **pipe's**
exit code, not the gate's, so a failed gate prints `exit=0`. Run gates unpiped, or capture with
`out=$(cmd); rc=$?`.

## Inside the worktree — commit freely

The worktree is your box. Commit your own work as you go; no approval, no handing Daniel a command.
The safe-commit mechanics from `git-policy.md` still apply in full:

| Gate | Rule |
|---|---|
| **G1 · Location** | **Every** commit-producing lane commits inside its own worktree — a story lane on `claude/*`, ad-hoc/Task work on `chore/*` (see Trigger). HEAD at `main` while you are about to commit means you are in the shared checkout: open the worktree first. (The `require-push-approval.py` hook prompts on `main` either way.) |
| **G2 · Scope** | `git add <explicit paths>` only. **`git add -A` / `.` / `-u` are banned** — they sweep other teams' work into your commit. Verify with `git diff --cached --stat` that only your files are staged. |
| **G3 · Push** | No pushes to the epic branch during development — the landing at close-out is the one sanctioned push there. Pushing your own `claude/*` branch is free at any time. |
| **G4 · `main`** | Never. Only Daniel, via `/cicd-push-e2e` (epic merge) or a direct in-the-moment ask (chore merge). |

## Artifacts are authored in the tree

Every file a story step writes — story file, red tests, implementation plan, self-audit, walkthrough,
automation summary, the ③ verdict — is authored INSIDE the story's worktree, rides the story branch,
and lands with the close-out merge. Never write a story-scoped artifact to the shared checkout. The
reader's corollary: a story's artifacts live in ITS tree — absence there means that step never ran. A
lookalike found in the shared checkout or a sibling tree is ANOTHER lane's work; reading it as this
story's evidence is how a session derails (2026-08-01: a sibling's ③ verdict sitting in the shared
checkout read as "this story's review is done", and the confusion cost the actual run).

## Close-out — the landing

The story lands on its **epic branch** as **one clean push**, triggered by either:

- **`/cicd-close-story-merge-tree`** — invoking it IS Daniel's sign-off (its Step 3 does the landing), or
- **Daniel's in-the-moment "approved"** — per-action, never carries to the next story.

**Several sibling lanes live at close-out time** (the standing multi-team case, or a LANDING RULE posted
on the project's sprint board): the set goes through **`/cicd-merge-epic-workingtrees`** — the one-shot
close-out for ALL live lanes: overlap map, dependency-ordered merges with per-lane test gates, landing,
each story flipped `done`, the combined gate, then every tree and branch pruned. No lane lands alone
while a set is declared.

Close-out runs **inside the worktree**, so its `sprint-status.yaml`, `active-context.md`, and story-file
edits ride the story branch and land with the story — instead of sitting in the shared tree waiting to
be hunk-picked out of somebody else's diff. The landing sequence itself is in `git-policy.md`
("The landing"): merge `origin/epic/<JIRA-KEY>-<slug>` into the story branch *inside the worktree*, then
`git push origin HEAD:epic/<JIRA-KEY>-<slug>`. Never check out the epic branch in the shared checkout to merge.

The shared checkout needs **no reconcile after a landing** — it stands on `main`, which only moves when
the epic merges via `/cicd-push-e2e`. (Under the retired `main_debug` model the shared checkout fell one
story behind per landing and needed a mandatory fast-forward; that whole failure mode died with the
long-lived integration branch.)

Afterwards, once the landing on the epic branch is verified, the worktree and git branch
(`claude/<JIRA-KEY>-<story-slug>`) are pruned via `/cicd-prune-worktree` (auto-invoked by
`/cicd-close-story-merge-tree` Step 5) to keep local disk and remote GitHub clean. The epic branch itself
is pruned later, by `/cicd-push-e2e`, after the epic merges to `main`.

## Hard stops

- NEVER edit a project file for a commit-producing lane before its worktree is open — story and Task
  lanes alike (SCC-62). Every tree is pruned by the close-out that owns it (`/cicd-close-story-merge-tree`
  Step 5 for a story, `/smh-close-task-merge-tree` Step 5 for a Task); an unpruned tree means a close-out
  was skipped, not that the tree was illegal to open.
- NEVER branch a story worktree from `main` — stories branch from the epic branch.
- NEVER `git add -A` / `.` / `-u`, inside a worktree or out.
- NEVER check out the epic branch in the shared checkout to merge a story — land from inside the
  worktree; the shared checkout stays on `main`.
- NEVER push to `main`. That is Daniel's, via `/cicd-push-e2e`.
