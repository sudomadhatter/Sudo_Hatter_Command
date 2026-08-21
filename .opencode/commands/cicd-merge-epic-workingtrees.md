---
description: One-shot close-out for ALL of an epic's live story worktrees — read every tree, check each story, fix/merge in dependency order with per-lane test gates, land on the epic branch, flip each story to done, run the combined gate, then prune every tree and branch. Invoked directly or from /cicd-close-story-merge-tree when several lanes are live.
platforms: [opencode, antigravity]
---

# /cicd-merge-epic-workingtrees — Close Out ALL Parallel Story Lanes in One Shot

> **Rules in force for this command:**
> - `.agents/rules/worktree-per-story.md` — one worktree per story, resolve-or-STOP, never delete through a junction
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never
>   force-push; every branch and every commit carries the repo's Jira key (armed 2026-08-07).
>   This command merges every live lane and pushes to the shared epic branch, so it is the one
>   place where a single `git add -A` sweeps another lane's in-flight work into your commit.
>   §"Pin the merge TARGET, not just the source" — `-C` on every call, assert before you merge: with N
>   trees open, a bare `git` after a `cd` runs in whichever checkout the shell reset to (see Step 4)
> - `.agents/rules/jira.md` — the Dev Record contract and `jira_feed.py finish` (ticket moves are the
>   agent's, inside this operator-invoked close-out)

Up to four story lanes (sometimes more) run at once, and lanes of one epic descend on the same
surfaces. Closing them one-by-one without looking sideways ships what no single lane ever saw: two
lanes editing one function, the same fix landed twice, board files colliding, and **semantic breaks
git cannot see** — each lane green alone, red combined (a renamed fixture, a moved mount, a changed
contract a sibling's test pins). This command is the whole close-out for the SET: reconcile → land
in order → flip each story `done` → combined gate → prune everything.

**Invoking it — directly, or via `/cicd-close-story-merge-tree` on the multiple-worktrees signal — IS
the operator's sign-off** for landing AND flipping every story confirmed in Step 1 (the per-set form
of the flip-and-land contract the solo path splits across two commands — the save's Step 4 flip, the
door's Step 3 landing). Per story, **only an objectively-red test gate blocks**: a lane
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
2. Map each lane → story id → **commits ahead** (`git -C <project> rev-list --count
   origin/epic/<JIRA-KEY>-<slug>..claude/<JIRA-KEY>-<slug>` — from output, never memory) → board row +
   story frontmatter status → review verdict: the
   `Verdict: … @ <sha>` line in the lane's `_artifacts/epic_<E>/<story>/walkthrough.md`
   `## Code Review` section (pre-2026-08-02 stories: fall back to
   `_bmad-output/implementation-artifacts/sudo-code-review-<story>.md`; either may be absent). Read the
   sprint map's **LANDING RULE** if one is posted — it may already name the set and the order.
   **⚠ "Ready" does not mean committed.** A lane reported finished can have **zero commits**, its work
   sitting uncommitted in a tree. `rev-list --count … == 0` with a dirty tree means the lane has not
   been built yet in any sense git can see — it needs commit, artifacts and `/cicd-code-review` before
   it is in the set at all. That is not the "trailing artifacts" case Step 2 commits for you.
3. Present the set (lane · story · status · verdict · proposed order) and **confirm with the
   operator**: membership default = every live lane of the named epic. Excluded lanes stay
   untouched. A lane whose change a sibling already carries (same fix shipped twice) is flagged
   now and lands as a verified no-op or is dropped — the operator's call.

## Step 2 — Check each tree: pre-flight per lane (mechanical, AUTOMATIC — the same script the solo door runs)
Inside each worktree, `TREE` pinned from Step 1's `git worktree list` output:
- `git -C "$TREE" status` clean — uncommitted work gets committed HERE first (explicit paths; this
  command never commits one lane's files from another lane's tree). A lane at **0 commits ahead**
  (Step 1's column) is the exception: it was never built — send it back, do not commit it into the set.
- **Run the preflight, every target pinned:**

  ```bash
  python3 .agents/scripts/closeout_preflight.py --story <id> --project <PROJECT> \
         --expect-key <JIRA-KEY> --branch claude/<JIRA-KEY>-<slug> --worktree "$TREE"
  ```

  `--expect-key` is required — the resolved branch must carry the key you named, because with N trees
  open `cwd` is not intent — and `--branch`/`--worktree` are not optional here either. **Check the
  target line it echoes against the lane you meant BEFORE reading its verdict**; a mismatch is a STOP,
  not a lane to skip. **Exit 2 = BLOCKED — that lane leaves the landing order. Exit 1 = warnings: read
  them, they do not block.**
  ⛔ **ONE exit-2 row is EXPECTED at this step and is NOT a block: `landed`.** It asks whether the lane
  is already an ancestor of the epic branch, and it is not — Step 4 is what lands it. If the ONLY error
  is `landed` naming the branch you pinned, the lane proceeds. `landed` naming a **different** branch is
  the wrong-lane case; an `intent`, `sync`, `worktrees`, `artifacts`, `status` or `gates` error blocks.
- **Close-out eligibility, per the close-out contract:** story at `ready-for-dev`/`in-progress`/
  `review` advances; `done` lanes are prune-only. Verdict **FAIL** (objectively red) → that lane is
  BLOCKED: report it, keep it out of the landing order, close out the rest. PASS / CONCERNS /
  WAIVED → proceeds (CONCERNS recorded on its board line). **No `Verdict:` line → BLOCKED** — the
  preflight's `artifacts` row says so (its only exemption is the pre-2026-08-02 standalone-file
  fallback); name `/cicd-code-review` as what produces it.

<!-- twin-law: merge-empty-set-stop -->
⛔ **An empty eligible set is a STOP with a named reason, never a pass.** "All lanes landed" after
zero merges is the gate that cannot fail.
<!-- /twin-law -->
Print zero lanes landed and why per lane; Steps 3–7 do not run and the set is never reported closed.

## Step 3 — The overlap map (BEFORE any merge)
Pairwise across the set (`git -C <project> diff --name-only <A>...<B>` per pair, plus each lane vs
`origin/epic/<JIRA-KEY>-<slug>` — the epic's own branch), classify every file touched by ≥2 lanes.
**Seven classes, and only the board one is mechanical:**

| Class | Looks like | Resolution law |
|---|---|---|
| **code overlap** | two lanes edit one function / module | Read both hunks; same-function edits get an owner + resolution decided NOW, not mid-conflict. Dependency edges (one lane creates a module/predicate a sibling imports) dictate order: **creator lands before importer**; an operator ruling on the board outranks any guess. |
| **board file** | `sprint-status.yaml` · `active-context.md` · the sprint map · `_bmad-output/history/CHANGELOG.md` | Collide by construction. **Keep BOTH sides' facts, never pick a winner** — parallel lanes record different true things; picking a winner erases someone's work (the 2026-07-31 committed-conflict-marker incident on active-context.md is the standing example). |
| **test surface** | sibling red files · shared fixtures, `conftest`, registration files (the `registry.py` class) | Sibling red files are per-story and safe; shared fixtures entangle. Note which suites re-run after which landings; a sibling's **green-first tripwires must STAY green** through every landing. |
| **rewrite vs edit** | one lane rewrote a doc another lane edited a paragraph of | ⚠ **NOT mechanical, and git cannot tell you.** The paragraph the edit changed no longer exists, so *both* automatic resolutions are wrong. **Re-author** the edit into the new structure. |
| **modify / delete** | one lane deletes a file another lane edited | ⚠ **A decision, not a strategy.** Ordering does not rescue it — both orders end with the file deleted. Rule which side wins, and **prove the surviving content exists at its destination BEFORE accepting the deletion** (`git show <branch>:<path>`, or the named replacement). |
| **gate or script** | `.githooks/` · `.github/workflows/` · hook config · the project's test-runner entry point · gate scripts · anything a gate imports | ORDER MATTERS. State which version must win BEFORE merging, and re-run the gate that file feeds after each landing that touches it. |
| **generated** | lockfiles, sync manifests, mirrors, tool-written INDEXes | Resolved by **REGENERATING**, never by hand-merge. |

**⚠ `git diff` cannot see untracked files, so this map UNDERCOUNTS.** Run `git -C "$TREE" status
--porcelain` per lane and fold anything untracked into the map **as if it were already committed**,
because at merge time it will be.

Output: one table — lane → commits ahead → order → overlaps (class) → owner/resolution → cross-repo
dependency. Fewest-overlaps-first where dependencies don't dictate — with two overrides that outrank
the count:

<!-- twin-law: merge-machinery-last -->
**⭐ A lane that changes commit or push machinery lands LAST.** Once it lands it changes the rules
for every merge after it — a pre-push approval hook landed mid-sequence turns the rest of the
session into a different procedure.
<!-- /twin-law -->
Here that is the **gate or script** class above (`.githooks/`, `.github/workflows/`, the runner every
4.2 gate calls); the gate it feeds re-runs after it lands.

<!-- twin-law: merge-cross-repo-order -->
**Cross-repo dependencies are part of the order.** A lane whose deletion's destination is an
**unmerged branch in another repo** lands AFTER that branch merges there. Get this wrong and the
content exists on no merged branch in either repo, and nothing says so.
<!-- /twin-law -->
Name that other repo's branch and its merge state in the table row.

Dump the table, the order and every conflict decision to the set's artifact folder before Step 4 — a
landing runs long enough to be compacted.

## Step 4 — Fix, close, land — sequentially, verified INSIDE each worktree
For each eligible lane, in the Step 3 order — `TREE=<that lane's worktree path>`, copied from Step 1's
`git worktree list` output, and **`git -C "$TREE"` on EVERY git call in this step; never a bare `git`
after a `cd`** (`git-policy.md` §"Pin the merge TARGET"). The cwd resets to the shared checkout between
tool calls, and that checkout stands on `main`: a bare merge here merges the epic branch into `main`,
and the bare push in 4.4 lands `main`'s tip on the shared epic branch every sibling then absorbs —
reporting success both times. That is the 2026-08-11 shape that put a merge commit on a sibling's
branch, and the output is indistinguishable from a correct one.

1. **Merge the epic branch into the lane, in the lane:** `git -C "$TREE" merge origin/epic/<JIRA-KEY>-<slug> --no-edit`
   — it now carries every previously-landed sibling, so each merge is the rolling reconcile. Resolve
   conflicts HERE using the Step 3 table. **A conflict in a file the Step 3 map did not classify is a
   finding, not a judgement call: STOP, re-derive the map for the remaining lanes (the untracked
   fold-in is the usual cause), and only then continue.** ⛔ Never check the epic branch out in the
   shared checkout to resolve anything.
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
   AGY: `<VENV>/python -m pytest` scoped, substituting `<VENV>` with `backend/.venv/bin` on POSIX
   or `backend/.venv/Scripts` on Windows — **check which exists, never hardcode either**
   (`code-standards` §6) · `npx vitest run <paths>`), suites
   **sequentially, never several lanes' at once** (concurrent runs starve each other and fake
   failures). **Red → fix in THIS worktree** (explicit paths), commit, re-run; a lane that cannot
   go green is skipped per Step 2 and the set continues.
   **Run every gate BARE and read its exit code** — piping to `tail`/`head` returns the *pipe's*
   status, so a red suite reads as green.
   An **artifacts-only** absorb at 4.1 keeps the lane's `Verdict:` valid. A code, script **or doc**
   change during the absorb — only `_artifacts/` is exempt; a `docs/` commit invalidates (SCC-154) —
   **VOIDS it**, and this gate is the re-measurement: it was measured against an epic branch that no
   longer exists. **Append the re-measurement to the walkthrough; never edit the old verdict away** —
   a pre-absorb `FAIL` left standing is the most useful line in the record. The shape:

   ```markdown
   ## Post-absorb re-measurement (<date>, landing set <story ids in order>)

   **Verdict: <PASS|CONCERNS> @ <post-absorb sha>** — re-measured after absorbing
   `origin/epic/<JIRA-KEY>-<slug>` at <sha> (<what landed there>). The pre-absorb `Verdict: … @ <sha>`
   above is **left standing on purpose**.

   <Artifacts-only absorb? say so and stop here. Otherwise one bullet per conflicted file naming the
   resolution and WHY.>

       <the canonical runner, scoped>   -> <files>, N/N cases, exit 0
   ```

   4.3's flip and 4.5's Dev Record read **this** verdict.
3. **Close the story out, in the worktree, so the edits ride its landing** — the per-story
   obligations of `/cicd-update-sprint-memory` Steps 1–4 + 6, scoped to this story: verify the
   claimed work on disk (grep-check); flip the story to `done` in BOTH the story frontmatter and
   `sprint-status.yaml` (print `Closing <story>: <old> → done`); add the story's own CHANGE-LOG
   line to `_bmad-output/history/CHANGELOG.md` (own line, newest-first, never re-joined — the log
   left the board in the Wave 4 split); reduce its active-context entry to a ≤3-line
   pointer; route learnings to their homes and queue memory writes; confirm the walkthrough's
   `## Your Actions` records what lands — and passes
   `python3 .agents/scripts/jira_feed.py check-actions --walkthrough <this lane's walkthrough>`
   **now, before the commit**: 4.5's `finish` refuses (exit 2) on the same rows, and after 4.4 the
   only fix is a commit on a branch that has already landed. Commit with `git -C "$TREE" add <paths>`
   and `git -C "$TREE" commit -F <msg-file>` — EXPLICIT PATHS ONLY, `git -C "$TREE" diff --cached
   --stat` shows only this story's files.
4. **Land — assert the tree, then push, then prove the remote moved:**

   ```bash
   test "$(git -C "$TREE" rev-parse --abbrev-ref HEAD)" = "claude/<JIRA-KEY>-<slug>" || { echo 'WRONG TREE — STOP'; exit 1; }
   git -C "$TREE" push origin HEAD:epic/<JIRA-KEY>-<slug>
   git -C "$TREE" log --oneline -1 origin/epic/<JIRA-KEY>-<slug>     # must be THIS lane's merge sha
   ```

   Rejected (remote moved again) → re-merge, re-gate, re-land — never force. ⛔ Do NOT push the
   `claude/*` branch itself; it is the rollback point until Step 6 deletes it. ⛔ A push that did not
   return 0 means 4.5 does not run — the ticket never moves ahead of the landing.
5. **Dev Record, then the ticket — per lane, at ITS landing, never batched** (the order the solo
   door's Step 4 runs: a ticket reading `Done` over a stopped landing is a lie on the board; a
   landing whose record lags is one command from correct). Read `jira_key:` from the story frontmatter:

   ```bash
   python3 .agents/scripts/jira_feed.py devrecord --key <KEY> --story <id> --project <PROJECT> \
          --outcome "review -> done, landed on epic/<JIRA-KEY>-<slug> @ <sha>" \
          --decision "<…>" --pitfall "<…>" --followon "<…>" \
          --evidence "<4.2 totals @ post-absorb sha>" --closing --apply      # updates in place — never --append-new
   python3 .agents/scripts/jira_feed.py finish --key <KEY> --apply \
          --walkthrough "<this lane's walkthrough>" --landing-ref "origin/epic/<JIRA-KEY>-<slug>" --status Done
   python3 .agents/scripts/jira_feed.py check --key <KEY> --story <id>          # scoped: this lane filed one
   python3 .agents/scripts/jira_feed.py check --key <KEY> --project <PROJECT>   # unscoped: the only run that sees a FORKED record (SCC-174)
   ```

   ⛔ **`--landing-ref` is not optional on a story lane.** `finish` defaults to `origin/main`, where no
   story is an ancestor until the epic ships, so a bare `finish` HOLDS a finished story forever
   (SCC-242). **`finish` writes the `Done`, and per lane it may refuse to:** exit `0` closed · `3`
   **HELD** (open `- [ ]` rows under `## Your Actions`, posted to the ticket with the `user-tasks`
   label) · `2` the walkthrough is wrong, nothing written — fix it · `4` transport, retry. **A held
   lane does not stop the run** — its code is on the epic; carry it into the Step 7 report as
   *landed, ticket awaiting the operator* and go on to the next lane. ⛔ Never fall back to a bare
   `acli … transition --status "Done"` on a held lane. One Dev Record per ticket; a story with no
   `jira_key` skips this item and says so in the report — never invent a key.

## Step 5 — Combined gate on the reconciled epic branch
*(No shared-checkout reconcile is owed — it stands on `main` and only moves when the epic merges;
the old "N stories behind" fast-forward died with `main_debug` on 2026-08-07.)*
1. Run the COMBINED surface once on the updated epic branch: the union of all landed stories' test
   files + the standard tier per stack touched (+ `/cicd-e2e` if the set is headed to a promote). An
   integration break no single lane caused is fixed HERE — directly on the epic branch, explicit
   paths, follow-on-fix convention (no new story, no new worktree) — and the combined surface
   re-run to green.
   Run it **BARE** — never through `tail`/`head`; the pipe's exit code is what you would read. Then
   the arithmetic: **the case totals must be additive — `<epic branch before the set> + <each lane's
   4.2 delta> = <combined>`** — or name which lane displaced which and why that was correct. It is the
   cheapest real check in the step: non-additive totals mean one lane's tests displaced another's at a
   4.1 resolution, and the merge ate coverage no review would ever see.
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

For each landed lane: `/cicd-prune-worktree <story-slug>` — verify merged, remove
`.claude/worktrees/<slug>`, delete local + remote `claude/<JIRA-KEY>-<slug>`. ⛔ Prune NOTHING before the
combined gate is green — the worktrees are the rollback points. Blocked/skipped lanes keep their
trees and are reported, not pruned.

## Step 7 — Verify, THEN report (never report an unverified success)
Every ✓ below comes from a command you ran HERE, not from intent. `<project>` is the project's shared
checkout; it holds no local `epic/*` branch by contract, so compare against the REMOTE ref:

```bash
git -C <project> fetch origin
git -C <project> log --oneline -1 origin/epic/<JIRA-KEY>-<slug>          # the LAST lane's merge sha, by name
git -C <project> merge-base --is-ancestor <each landed lane's tip> origin/epic/<JIRA-KEY>-<slug> && echo landed
git -C <project> status --short                                          # empty — nothing rode into the shared checkout
git -C <project> worktree list                                           # only expected trees; a HUSK here blocks the next `worktree add`
git -C <project> branch -a --list 'claude/*'                             # only deliberately-retained lanes (`claude/incident-*` excluded)
```

Per story: landed SHA range · pre- and post-absorb verdict · `→ done` flip · Jira: Dev Record filed,
`<KEY> → Done` or *HELD — <rows>* · pruned ✓. Set-level: overlaps resolved
(file → resolution) · per-lane and combined test evidence · memory writes · anything skipped and
WHY (a blocked lane, an excluded lane, a live-QA carryover). **This command ends at the epic
branch — it does NOT merge to `main`.** The epic reaches `main` exactly one way: `/cicd-push-e2e`
(full gate + Daniel's sign-off), which also deletes the epic branch after the merge.

Optional additional input: $ARGUMENTS
