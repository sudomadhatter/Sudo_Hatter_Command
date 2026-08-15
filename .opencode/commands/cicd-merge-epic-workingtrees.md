---
description: One-shot close-out for ALL of an epic's live story worktrees — read every tree, check each story, fix/merge in dependency order with per-lane test gates, land on the epic branch, flip each story to done, run the combined gate, then prune every tree and branch. Invoked directly or from /cicd-update-sprint-memory when several lanes are live.
platforms: [opencode, antigravity]
---

# /cicd-merge-epic-workingtrees — Close Out ALL Parallel Story Lanes in One Shot

> **Rules in force for this command:**
> - `.agents/rules/worktree-per-story.md` — one worktree per story, resolve-or-STOP, never delete through a junction
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never
>   force-push; every branch and every commit carries the repo's Jira key (armed 2026-08-07).
>   This command merges every live lane and pushes to the shared epic branch, so it is the one
>   place where a single `git add -A` sweeps another lane's in-flight work into your commit.

Up to four story lanes (sometimes more) run at once, and lanes of one epic descend on the same
surfaces. Closing them one-by-one without looking sideways ships what no single lane ever saw: two
lanes editing one function, the same fix landed twice, board files colliding, and **semantic breaks
git cannot see** — each lane green alone, red combined (a renamed fixture, a moved mount, a changed
contract a sibling's test pins). This command is the whole close-out for the SET: reconcile → land
in order → flip each story `done` → combined gate → prune everything.

**Invoking it — directly, or via `/cicd-update-sprint-memory` on the multiple-worktrees signal — IS
the operator's sign-off** for landing AND flipping every story confirmed in Step 1 (the per-set form
of close-out's Step 4/7 contract). Per story, **only an objectively-red test gate blocks**: a lane
that cannot go green is surfaced and skipped, never landed around silently — every other lane still
completes. When this command finishes there is NOTHING left owed on the set: boards updated, stories
`done`, trees and branches pruned.

## Step 0 — Resolve the target project (FIRST)
Bind per `.agents/rules/smh-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override (remainder = epic id / lane list) → `.agents/active-project.txt` → else **STOP and ask**.
Echo exactly `Target: Projects/<name>` before any work.

## Step 1 — Read ALL the trees: inventory & confirm the set
1. `git fetch origin`, then **both** listings — trees AND branches, they disagree after prunes and
   machine switches: `git worktree list` + `git branch -a --list "*claude/*"`. A branch alive on
   origin with no local tree is still a lane (re-create its worktree if it belongs to the set — a
   re-created tree has ONLY tracked files: restore gitignored assets per the project's known
   pitfalls before trusting its test runs). **`claude/incident-*` matches are EXCLUDED from the
   inventory:** they are the incident pipeline's (`/cicd-mobile-error-team`), never story lanes —
   never fix, merge, land or PRUNE one here (SCC-149).
2. Map each lane → story id → board row + story frontmatter status → review verdict: the
   `Verdict: … @ <sha>` line in the lane's `_artifacts/epic_<E>/<story>/walkthrough.md`
   `## Code Review` section (pre-2026-08-02 stories: fall back to
   `_bmad-output/implementation-artifacts/sudo-code-review-<story>.md`; either may be absent). Read the
   sprint map's **LANDING RULE** if one is posted — it may already name the set and the order.
3. Present the set (lane · story · status · verdict · proposed order) and **confirm with the
   operator**: membership default = every live lane of the named epic. Excluded lanes stay
   untouched. A lane whose change a sibling already carries (same fix shipped twice) is flagged
   now and lands as a verified no-op or is dropped — the operator's call.

## Step 2 — Check each tree: pre-flight per lane
Inside each worktree:
- `git status` clean — uncommitted work gets committed HERE first (explicit paths; this command
  never commits one lane's files from another lane's tree).
- **Close-out eligibility, per the close-out contract:** story at `ready-for-dev`/`in-progress`/
  `review` advances; `done` lanes are prune-only. Verdict **FAIL** (objectively red) → that lane is
  BLOCKED: report it, keep it out of the landing order, close out the rest. PASS / CONCERNS /
  WAIVED / missing verdict → proceeds (CONCERNS recorded on its board line).

## Step 3 — The overlap map (BEFORE any merge)
Pairwise across the set (`git diff --name-only <A>...<B>` per pair, plus each lane vs
`origin/epic/<JIRA-KEY>-<slug>` — the epic's own branch), classify every file touched by ≥2 lanes:
- **Code overlaps** — read both hunks; same-function edits get an owner + resolution decided NOW,
  not mid-conflict. Dependency edges (one lane creates a module/predicate a sibling imports)
  dictate order: **creator lands before importer**; an operator ruling on the board outranks any
  guess.
- **Board files** — `sprint-status.yaml`, `active-context.md`, the sprint map collide by
  construction. Resolution is always: **keep BOTH sides' facts** — parallel lanes record different
  true things; picking a winner erases someone's work (the 2026-07-31 committed-conflict-marker
  incident on active-context.md is the standing example).
- **Test surfaces** — sibling red files are per-story and safe; shared fixtures, conftest,
  registration files (the `registry.py` class) entangle. Note which suites re-run after which
  landings; a sibling's **green-first tripwires must STAY green** through every landing.
Output: one table — lane → order → overlaps → owner/resolution. Fewest-overlaps-first where
dependencies don't dictate.

## Step 4 — Fix, close, land — sequentially, verified INSIDE each worktree
For each eligible lane, in the Step 3 order:
1. **Merge the epic branch into the lane, in the lane:** `git merge origin/epic/<JIRA-KEY>-<slug>` — it now
   carries every previously-landed sibling, so each merge is the rolling reconcile. Resolve conflicts
   HERE per the Step 3 plan. ⛔ Never check the epic branch out in the shared checkout to resolve
   anything.
   **Expect ONE conflict block spanning the set's story-status lines in `sprint-status.yaml` at
   every lane merge** — adjacent lines, different lanes, by construction (the one-line-per-entry
   CHANGE LOG in `_bmad-output/history/CHANGELOG.md` auto-merges; the status lines don't — and
   post-split they are BARE `key: status` rows, so the block is small). The resolution is
   mechanical, never judgment:
   keep the TRUNK's lines for already-landed siblings (their `done` is newer) + this LANE's own
   line. First proven 2026-08-01 on the {21.9, 21.10, 21.11} set — memory
   `multi-lane-closeout-board-merge-shape`.
2. **Post-merge gate, still inside the worktree:** this story's red file(s) (now green), the
   touched-surface tier for its stack, and already-landed siblings' red files on shared surfaces
   (their tripwires stay green). Project's canonical runners (testing-standards / pitfalls — e.g.
   AGY: `backend\.venv\Scripts\python.exe -m pytest` scoped · `npx vitest run <paths>`), suites
   **sequentially, never several lanes' at once** (concurrent runs starve each other and fake
   failures). **Red → fix in THIS worktree** (explicit paths), commit, re-run; a lane that cannot
   go green is skipped per Step 2 and the set continues.
3. **Close the story out, in the worktree, so the edits ride its landing** — the per-story
   obligations of `/cicd-update-sprint-memory` Steps 1–4 + 6, scoped to this story: verify the
   claimed work on disk (grep-check); flip the story to `done` in BOTH the story frontmatter and
   `sprint-status.yaml` (print `Closing <story>: <old> → done`); add the story's own CHANGE-LOG
   line to `_bmad-output/history/CHANGELOG.md` (own line, newest-first, never re-joined — the log
   left the board in the Wave 4 split); reduce its active-context entry to a ≤3-line
   pointer; route learnings to their homes and queue memory writes; confirm the walkthrough's
   `## Your Actions` records what lands. Commit — EXPLICIT PATHS ONLY, `git diff --cached --stat`
   shows only this story's files.
4. **Land:** `git push origin HEAD:epic/<JIRA-KEY>-<slug>`; verify the remote moved. Rejected (remote moved
   again) → re-merge, re-gate, re-land — never force. ⛔ Do NOT push the `claude/*` branch itself;
   it is the rollback point until Step 6 deletes it.

## Step 5 — Combined gate on the reconciled epic branch
*(No shared-checkout reconcile is owed — it stands on `main` and only moves when the epic merges;
the old "N stories behind" fast-forward died with `main_debug` on 2026-08-07.)*
1. Run the COMBINED surface once on the updated epic branch: the union of all landed stories' test
   files + the standard tier per stack touched (+ `/cicd-e2e` if the set is headed to a promote). An
   integration break no single lane caused is fixed HERE — directly on the epic branch, explicit
   paths, follow-on-fix convention (no new story, no new worktree) — and the combined surface
   re-run to green.
2. Run `/cicd-prune-context` ONCE for the whole set (not per lane); write the queued memory files +
   `MEMORY.md` pointers; then the close-out catch question — **once, and only if the set routed
   ZERO learnings automatically (SCC-133)**: *"Set closed. Any manual learnings, new bugs, or
   sprint-objective changes to add?"* When something was routed, print the routed list instead of
   asking.

## Step 6 — Prune EVERY tree and branch (AUTOMATIC — only after Step 5 is green)

⛔ **Every per-lane command here takes an explicit `--repo`/`--branch` (or `git -C <tree>`).** This command
is the one that runs with the MOST sibling trees open at once, so a default resolved from `cwd` is most
likely to land on the wrong lane — and it prunes, which is not what you want aimed at a guess
(`worktree-per-story.md` → *"`cwd` is not intent"*). Confirm each invocation echoed the slug you meant
before it removes anything.

For each landed lane: `/cicd-close-workingtree <story-slug>` — verify merged, remove
`.claude/worktrees/<slug>`, delete local + remote `claude/<JIRA-KEY>-<slug>`. ⛔ Prune NOTHING before the
combined gate is green — the worktrees are the rollback points. Blocked/skipped lanes keep their
trees and are reported, not pruned.

## Done — the one-shot report
Per story: landed SHA range · verdict · `→ done` flip · pruned ✓. Set-level: overlaps resolved
(file → resolution) · per-lane and combined test evidence · memory writes · anything skipped and
WHY (a blocked lane, an excluded lane, a live-QA carryover). **This command ends at the epic
branch — it does NOT merge to `main`.** The epic reaches `main` exactly one way: `/cicd-push-e2e`
(full gate + Daniel's sign-off), which also deletes the epic branch after the merge.

Optional additional input: $ARGUMENTS
