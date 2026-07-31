# /update-personal-sprint-map — Personal Sprint Ticket Board Manager

Updates `_my_resources/_quick_reference/sprint-dependency-map.md` in the target project workspace. This file is Daniel's **personal ticket board** for tracking active work, required `/slash` commands, live testing items, blockers, and operational launch gates.

> Flow position: Standalone / maintenance command — run whenever stories change state, after epic kickoff, or when checking open work tickets.

> **REBUILD TO TEMPLATE.** Every run regenerates the document from scratch using the template in Step 3.
> Do NOT preserve sections from the existing file that are not in the template (settled rulings tables,
> epic status tables, pipeline specs, historical context paragraphs — all of that is reference material
> that lives in the sources of truth, not on an action board). The board must be lean enough to scan in
> 30 seconds and answer: "what do I do next, what can run in parallel, what's blocked."

## Step 0 — Resolve Target Project

Determine the target project:
0. **Self (sub-project fast path)** — if the current working directory is inside a project under `Projects/` (or has no `Projects/` subfolder), `PROJECT_ROOT = .`.
1. **Inline override** — if `$ARGUMENTS` names a folder under `Projects/`, set `PROJECT_ROOT = Projects/<name>`.
2. **Active pointer** — else read `.agents/active-project.txt`; if it names a folder under `Projects/`, use it.
3. **Ask** — else ask Daniel which project to update.

Echo `Target: <PROJECT_ROOT>` before continuing.
The target document is `{PROJECT_ROOT}/_my_resources/_quick_reference/sprint-dependency-map.md`.
If `_quick_reference/` does not exist, create it.

## Step 1 — Parse Current Workspace State

Read the following sources in `{PROJECT_ROOT}`:
1. `_bmad-output/implementation-artifacts/sprint-status.yaml` (master status of epics and stories)
2. `_bmad/bmm/stories/` (story spec files and acceptance criteria)
3. `_bmad-output/active-context/active-context.md` (live testing tasks, owed deployments, blocking human input)
4. Recent git commits and branches (to verify review vs landed status)

## Step 2 — Ticket Board Rules & Mapping Logic

Map every item according to the following strict rules:

### 1. Open Stories & Next `/slash` Commands
For every story in an active epic (`in-progress` or `backlog`):
- **Story in Backlog** (no story file in `_bmad/bmm/stories/` yet):
  - Next Command: `/sudo-write-story-tests <story-id>`
- **Story Ready for Dev** (story file exists, ATDD red tests proven):
  - Next Command: `/sudo-dev-story-tests <story-id>`
- **Story In Progress** (dev loop underway):
  - Next Command: `/sudo-dev-story-tests <story-id>`
- **Story In Review** (code written, awaiting review):
  - Next Command: `/sudo-code-review <story-id>`
- **Story Review Passed / Ready to Land**:
  - Next Command: `/sudo-update-sprint-memory`

### 1b. Parallelism (CRITICAL)
- Check the dependency graph: stories that have **no dependency on each other** should be marked
  with `‖` (parallel) in the Ready for Development table and called out explicitly in the execution spine
  under a `### ⚡ Can run in parallel` sub-heading.
- Always check git worktrees (`git worktree list`) — an existing worktree means work is in flight even if
  the YAML hasn't caught up. A worktree with zero divergent commits from `main_debug` is premature and
  should be flagged for pruning.

### 2. Stories Requiring Live Testing or Blocking Agent Input
- List any completed/staged stories that require Daniel to manually test on staging/Cloud Run, perform voice/UI checks, or provide design decisions before the story can fully close.

### 3. Blocking Stories & Reasons
- List stories that cannot proceed due to dependencies, unverified gates, or external blockers, with explicit "Blocked by: <reason/story>".

### 4. Closed Stories (Active Epics Only)
- List stories marked `done` ONLY if they belong to an epic that is still `in-progress`.

### 5. Automatic Epic Pruning Rule (CRITICAL)
- **WHEN AN ENTIRE EPIC IS DONE**: Once an epic's status in `sprint-status.yaml` turns to `done` (all stories completed), **DELETE all closed stories belonging to that completed epic from `sprint-dependency-map.md`**.
- Historical records for completed epics live permanently in `epics.md`, `sprint-status.yaml`, and story files. The map remains lean and manageable.

### 6. Daniel-Owned Operations & Launch Gates
- Operations, environment secrets, Firestore rules/TTL policy deploys, legal reviews, or manual tasks owned by Daniel.
- **Strip completed ✅ items.** Only open/pending work belongs on the board. Completed operator actions
  are historical — they live in `active-context.md` and `sprint-status.yaml`, not here.

## Step 3 — Format and Write `sprint-dependency-map.md`

Format the markdown document using house style:

```markdown
---
title: Personal Sprint Ticket Map
type: quick-reference
last_checked: YYYY-MM-DD
---

# Personal Sprint Ticket Map

Live ticket board — open stories, next commands, human verification, and blockers. Completed epics are pruned automatically.

## Active Front — Epic <N>: <Title>

<Summary of stories, priorities, and current focus>

Execution spine:
1. **<Story ID> (<P-level>)** — <title> ⚡ *[STATUS]*: <notes> → Next: `<next-command>`
...

## Ready for Development

| Priority | Work | Status & Worktree | Next Command |
|---|---|---|---|
| 1 | **<Story ID>** | <details> | `<next-command>` |

## Awaiting Live Testing or Human Input

| Work | What remains / Required action |
|---|---|
| **<Story ID>** | <human test or verification owed> |

## Blocked Stories

| Work | Blocker / Reason |
|---|---|
| **<Story ID>** | <blocker reason> |

## Closed Stories (Active Epics Only)

- **<Story ID>**: ✅ <summary of fix/review>

*(Note: Closed stories are automatically pruned from this board once their parent Epic is fully completed.)*

## Needs Triage or Follow-on

| Item | Next step |
|---|---|
| **<Item>** | <next step> |

## Daniel-Owned Operations and Launch Gates

- **<Category>**: <description>

## Sources of Truth

- [Sprint status](../../_bmad-output/implementation-artifacts/sprint-status.yaml)
- [Active context](../../_bmad-output/active-context/active-context.md)
```

## Step 4 — Output Summary
Report the updated ticket map path and summarize:
- Active front and open stories count
- Next recommended `/slash` command
- Items awaiting live testing / blocking tasks
- Any pruned closed epics
