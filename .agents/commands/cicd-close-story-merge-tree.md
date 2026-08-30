---
description: Close out ONE story — THE DOOR. Preflight, run the sprint-memory save, commit the close-out edits, LAND the story on its EPIC branch, and only THEN file the Dev Record and move the Jira ticket, then prune the worktree. Invoking it IS Daniel's sign-off for THIS story's landing, and that sign-off is spent by it. Run LAST when closing a story.
platforms: [opencode, antigravity, zoo]
---

# /cicd-close-story-merge-tree — Story Close-Out (the door)

> **Rules in force for this command:**
> - `.agents/rules/worktree-per-story.md` — one worktree per story, resolve-or-STOP, never delete through a junction
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never force-push, never `main`;
>   the sign-off is **per-action and never carries forward**
> - `.agents/rules/jira.md` — the board is `acli`; the agent performs every board write, inside the ceremony the
>   operator's words triggered
> - `.agents/rules/artifacts-always-first.md` — the walkthrough is the closing doc; `## Your Actions` is a machine contract

**This is the command you type to close a story out.** It is named for its job: it merges the story's tree into
the epic branch and closes the story. Self-contained, project-scoped — targets THIS repo's `_bmad-output/`.

**What it owns, and what it delegates.** The *save* — routing learnings, updating the board and the story file,
pruning active-context — is `/cicd-update-sprint-memory`'s job, and this command invokes it at Step 1 rather than
restating it. What is left here is the part that only a door can do, in the only order that is safe:

```
preflight → SAVE (/cicd-update-sprint-memory) → commit → LAND on the epic branch → ticket + Dev Record → prune
```

⭐ **The order is the point (SCC-210).** The ticket write is a **remote** write: it rides no branch, so nothing
undoes it if a later step stops. The board flips, the story file and `active-context.md` are **file** writes that
ride this branch, so a stopped landing publishes none of them. That asymmetry is why the Jira transition sits at
**Step 4, after the push returns 0** — and why it used to sit ~100 lines and three STOPs before it, leaving code
on one disk under a ticket that read `Done`.

⛔ **This command does not touch `main`.** It lands on the **epic branch** and stops. The epic reaches production
exactly one way: `/cicd-push-e2e`.

## Step 0 — Resolve the target project (FIRST — before any other step)
Bind the target per `.agents/rules/smh-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override → `.agents/active-project.txt` → else **STOP and ask** *"Which project are we closing out?"* —
never guess, never operate on the lobby. Set `PROJECT_ROOT` and **echo exactly** `Target: Projects/<name>`
before any work; every bare path below resolves under `PROJECT_ROOT`, and a needed project path missing
there → STOP and say so. ONE exception to §BIND: Step 1's Claude auto-memory write always targets Daniel's
global memory dir.

**Echo the story and the branch you MEAN, before any script has answered anything.** Everything below binds to
these two strings, and Step 0.6 checks the preflight resolved the same ones:

```bash
STORY=<id>            # the story you are closing
KEY=<JIRA-KEY>        # its ticket, from the story frontmatter's `jira_key:`
EPIC=<epic-branch>    # `epic/<EPIC-KEY>-<slug>`, from `git branch --list 'epic/*'` — see below
BRANCH=$(git -C "<the story worktree>" rev-parse --abbrev-ref HEAD)   # from command output, never memory
echo "Closing: $STORY | $KEY | $EPIC | $BRANCH"
```

⛔ **`$KEY` is the STORY's ticket; the epic branch carries the EPIC's.** `git-policy` spells both branch
templates with the same `<JIRA-KEY>` placeholder, and they do not mean the same key: `claude/<JIRA-KEY>-<slug>`
is this story's, `epic/<JIRA-KEY>-<slug>` is its parent epic's. Resolve `$EPIC` from
`git branch --list 'epic/*'` (exactly one live epic branch is the normal case) — never by substituting `$KEY`
into the template. Getting that wrong does not fail loudly at the push: it CREATES a new remote
`epic/<story-key>-<slug>`, returns 0, and Step 4 then moves the ticket to `Done` on the strength of it.

## Step 0.5 — Sync the branch BEFORE the save reads or edits the board (parallel-lane safety)
Step 1 reads **and rewrites** `sprint-status.yaml` + `active-context.md`. Do that on a stale base and you
author every board edit against an old file, then discover it at Step 3's merge — on the two hottest files
in the repo. So absorb the story's EPIC branch FIRST, inside the worktree (`epic/<JIRA-KEY>-<slug>` —
exactly one live `epic/*` branch is the normal case):

```bash
git fetch origin epic/<JIRA-KEY>-<slug>
git rev-list --count HEAD..origin/epic/<JIRA-KEY>-<slug>    # >0 → behind
git merge origin/epic/<JIRA-KEY>-<slug>                     # CONFLICT → STOP and report, never force
```

Echo `Base: current with origin/epic/<JIRA-KEY>-<slug> @ <sha>`. Step 3 re-merges as a cheap safety net; this one is
what makes the board edits land clean. If another lane closed out while you worked, its board line is now
in front of you — **read it before you write yours**, and never delete a line you did not add.

## Step 0.6 — Preflight: one call instead of ten (AUTOMATIC, never ask)

Run it before reading anything. It answers, mechanically, every question Steps 1–5 used to
answer by hand — and each of those has been silently wrong at least once:

```bash
python3 .agents/scripts/closeout_preflight.py --story <id> --project <PROJECT> \
       --expect-key <JIRA-KEY> --branch <name> --worktree <path> \
       [--require-gates suite,ruff,pyrefly]
```

⛔ **`--expect-key`, `--branch` and `--worktree` are NOT optional, and the brackets used to say otherwise.**
This command runs when worktrees are open by definition, and that is exactly when `cwd` stops matching intent —
the script walks up from `cwd` for `.git` and guesses branches from ids and worktrees, so a sibling lane that
moved the shared checkout silently becomes the target, with every check reported honestly about the **wrong**
branch (`worktree-per-story.md` → *"`cwd` is not intent"*). Prose cannot catch that, which is why `--expect-key`
is now mechanical: the resolved branch must carry the key you named, or the preflight errors. It is the same
check `task_preflight.py` has required since the 2026-08-09 failure.

**Check the target the script echoes BEFORE you read its verdict.** Resolved story/branch ≠ the one Step 0
echoed → **STOP**, and say which it resolved versus which you meant.

It reports: did the code land on the epic branch · is every repo `0/0` and clean · are the registered
worktrees LIVE/LOST/HUSK · do both status surfaces agree · does the walkthrough carry a `Verdict:`
(with the pre-2026-08-02 standalone-file fallback) · is that verdict stale against HEAD · does the
story's **File List** still exist in the tree · is `active-context` inside budget · did the required
gates actually run at this commit · can the epic close.

**Exit 2 = BLOCKED — resolve before flipping anything. Exit 1 = warnings: read them, they do not
block.** A warning that says *"landing was NOT verified"* means exactly that — it is not a pass.

⛔ **ONE exit-2 row is EXPECTED here, and reading it as a block stops the door on every normal close-out.**
The `landed` check asks whether the story branch is already an ancestor of the epic branch. At Step 0.6 it is
not — **Step 3 is what lands it** — so a healthy lane reports
`[ERROR] landed: claude/<KEY>-<slug> has N commit(s) NOT on epic/… - closing out now would strand them`
and the run exits 2. That row is this command's *reason to exist*, not its refusal. **Every OTHER error blocks
and this one does not**, so read the rows, never the exit code alone: an `intent` error means you are aimed at
another lane, a `sync` error means uncommitted or unpushed work, a `worktrees`/`status`/`gates` error means the
evidence is not there. If the ONLY error is `landed` naming the branch Step 0 echoed, proceed. If `landed`
names a **different** branch, STOP — that is the wrong-lane case.

A verdict line carrying **STALE** means the comparison was made against the last fetch, not the remote. It says
which remedy applies, and they are different acts: *"the fetch was asked for and FAILED"* is an uplink to fix
(the default, since fetching is on), while *"re-run WITHOUT `--no-fetch`"* only appears if you passed that flag.
Fix what the line names before you land anything. Paste the block into the close-out summary; it IS the
evidence for Steps 1, 3 and 5.

## Step 1 — The SAVE: invoke `/cicd-update-sprint-memory` (AUTOMATIC, never ask)

Invoke **`/cicd-update-sprint-memory`** against the same `PROJECT_ROOT` (it inherits the binding — no
re-resolution) and hand it the Step 0.6 block, which is its evidence too: it must not re-run the preflight.

It does the whole save, and it is the ONLY thing that does: read this session's state and artifacts ·
code-verify the claimed work on disk · route every learning to its home · apply the updates · **flip the
story to `done`** (and close the epic if every child is terminal) · prune and budget active-context via
`/cicd-prune-context` · write the memory files · print the `Session save applied:` summary.

**Your invocation of THIS command is the sign-off it acts on.** Only an objectively-red `FAIL` verdict blocks
the flip; a pending live-test or "stays review until X" note does not, and neither does a commit owed.

⛔ **Everything it writes is a FILE write, and that is what makes this order safe.** The board, the story
frontmatter and `active-context.md` all ride this branch, so if Step 3 stops, none of them is published. Nothing
in Step 1 reaches the remote. The one write that *would* — the Jira ticket — is deliberately not here.

Carry its report lines (the routed learnings, `active-context: ~X / 5,000 tokens`, the story flip
`Closing <story>: review → done`) into this command's own summary at Step 6.

## Step 2 — Fix `## Your Actions`, then commit the close-out edits

<!-- reconcile-law -->
⛔ **RECONCILE `## Your Actions` BEFORE this lane lands, and before you ask `finish` to close.**
`finish` decides `Done` from what that section **claims**, and until SCC-298 nothing had ever
checked whether a row's claim was still true — so a ticket sat at `Review Required` over work that
was finished. SCC-288 sat for a day on one box whose token already existed, authenticated, and was
attached. Law: `.agents/rules/completion-not-illusion.md` §4 — **an unverified open box is not
evidence of owed work.**

```bash
python3 .agents/scripts/jira_feed.py reconcile-actions --walkthrough <the walkthrough>   # PC: `python`
```

Exit `3` lists every open row with its line number. **Take each one, in this order:**

1. **Derive the check and RUN it.** A keychain item, a live endpoint, a file on disk, a board
   field — most rows have one. Tick on what it returned:
   `--tick <line> --evidence "<what you ran and what it returned>" --source measured`
2. **No machine check exists? ASK the operator** and tick on their word, quoted:
   `--tick <line> --evidence "<their words>" --source operator`
3. **Neither proved nor answered → it STAYS OPEN**, and you report it. That is a row genuinely
   holding the ticket, and it is the only kind that should.

⛔ **Never tick a row you have not checked.** The verb refuses empty and contentless evidence, a
line that is not an open row, a **ceremony** row (SCC-193 — the agent RUNS those; delete it) and
the **merge** row (SCC-175 — `finish` computes that one from the repo). It never derives evidence
by itself: an agent that could both invent the check and pass it is self-certifying.

⛔ **Commit the ticked walkthrough NOW, on this lane, in the commit that lands — never after.**
`finish` reads the **working tree** for these rows (only the merge row is read from `HEAD`), so an
uncommitted tick satisfies it and the ticket goes `Done` — while the copy that actually lands still
reads `- [ ]`, in a worktree the close-out is about to prune. An open box on a closed ticket is the
exact state §4 exists to forbid, and this is the one window where avoiding it costs nothing.
<!-- /reconcile-law -->

**First the refusal, because here is the only place fixing it is free.**

```bash
python3 .agents/scripts/jira_feed.py check-actions --walkthrough <the story walkthrough> \
  || { echo 'fix `## Your Actions` BEFORE the landing'; exit 1; }
```

It refuses a row that hands the operator **ticket work** (SCC-163) or **the ceremony's own steps** (SCC-193) —
"click Merge", "re-invoke the close-out", "run `--after-merge`". From the operator's word on, those are yours to
run, not theirs to do. `/cicd-code-review` promises this refusal happens on the close-out path; until SCC-210
no step on that path performed it.

⛔ **Fix it HERE anyway, even though a second pass now exists.** Step 4b runs `jira_feed.py finish`, which reads
`## Your Actions` again and refuses on the same two families — so this lane is no longer the single point it was
before SCC-242, when `finish` was banned here and this really was the only pass. What has not changed is the
**price**: this refusal costs an edit to an uncommitted file, and Step 4's costs a commit on a branch that has
already landed on the epic. The net below is real; it is just an expensive one to fall into.

**Then the branch precondition, BEFORE the commit — because a commit is the thing you cannot take back.**

```bash
git -C "<the story worktree>" rev-parse --abbrev-ref HEAD    # must be claude/<KEY>-<slug>
```

HEAD must be a **`claude/*`** branch inside the story worktree — **and never `claude/incident-*`**, which
satisfies the glob but is the incident pipeline's lane (`/cicd-mobile-error-team`), not story work (SCC-149):
an incident HEAD is a **STOP** — report it and hand off; nothing below runs. If HEAD is the epic branch or
`main`, this story was not worked in a worktree — **do NOT land it.** Report it and stop.

⛔ **This check sits HERE, ahead of the commit, and not at Step 3 where the push is.** Step 1 rewrote
`sprint-status.yaml`, the story file and `active-context.md`; committing those and *then* discovering HEAD is
`main` has already written this story's close-out onto the shared checkout — the exact act the STOP's own
sentence forbids (*"never rescue it by committing in the shared checkout"*). The preflight does not catch it
either: a bare `main` carries no key segment, so `--expect-key` WARNs rather than errors, and exit 1 does not
block. Order is the guard.

Then commit — **EXPLICIT PATHS ONLY** (board, story file, active-context, artifacts). `git diff --cached --stat`
must show ONLY this story's files; `git add -A` / `.` / `-u` are banned, and the worktree does not repeal that.

## Step 3 — Land the story on the EPIC branch (the one sanctioned push)
<!-- JIRA-HOOK: ticket-moved check runs here BEFORE the landing push — the story's Jira ticket must be in the required status or the landing stops. Separate story; not built yet. -->

**Daniel invoking this command IS the sign-off for this push.** ⛔ **And it is spent by it.** This sign-off
covers **THIS story's landing** only: a second story needs its own invocation, and a landing offered on the
strength of an earlier one is refused. The invocation stays in your context and will still *read* as valid on the
next story in the same session — that is exactly how one sign-off once rode six merges (`git-policy.md`
§"per-action and never carries forward", SCC-71).

Run it LAST, after Steps 1–2 wrote the board, story file, and `active-context.md` — so those edits ride the story
branch and land with it.

⚠️ **Several sibling worktrees live** (operator says so, `git worktree list` shows sibling story lanes, or
a LANDING RULE is posted on the board): STOP this solo flow — read `.agents/commands/cicd-merge-epic-workingtrees.md`
and follow IT end to end: it runs this command's close-out per story itself (fix → merge → land → flip
`done` → combined gate → prune ALL trees) in one shot; nothing returns here.

**Precondition — re-read HEAD.** Step 2 checked it before committing anything, which is where the guard has
to live; re-read it here because the push is the irreversible half and a step boundary is not a lock:
`git -C "<the story worktree>" rev-parse --abbrev-ref HEAD` must still be the `claude/*` branch Step 0 echoed.
Anything else → **STOP**, per Step 2's rules.

Then execute `git-policy.md` → **"The landing"**, inside the worktree: merge
`origin/epic/<JIRA-KEY>-<slug>` (CONFLICT → **STOP and report**; never force-push,
never blind-rebase), **then the MERGE GATE — prove the tree that ships, not the one ③ reviewed** (the solo
counterpart of `/cicd-merge-epic-workingtrees` Step 5's combined gate): run
`git diff --name-only <③-verdict suite SHA>..HEAD -- backend/ frontend/`.
- **Empty** → the merge changed no code under you (fast-forward / doc-only drift): ③'s green already
  describes this exact tree — inherit it, say `Merge gate: inherited ③ green @ <sha>`, and push.
- **Non-empty** → the epic branch moved code since ③'s run, so the merged tree has NEVER been tested: run the
  full suite of the touched stacks on it NOW (parallel flags; the conftest suite lock serializes the box) and
  paste totals into the walkthrough. **Red → STOP: no push, nothing lands** — the board/status flips from
  Steps 1–2 ride this branch, so a stopped landing publishes nothing, **and Step 4 never runs, so the ticket
  never moves.** Report the failing tests + which epic-branch commits collided
  (`git log <suite-SHA>..origin/epic/<JIRA-KEY>-<slug> --oneline`); the fix is a follow-on
  on the branch, then re-gate.
Then `git push origin HEAD:epic/<JIRA-KEY>-<slug>` — THE landing.

⛔ **Do NOT push `claude/<JIRA-KEY>-<story-slug>` to origin.** The local branch is the rollback point and survives a
failed landing push intact. A story branch reaches origin **only** via `/cicd-park` — that is park's whole
purpose, and `/cicd-resume` reads the origin `claude/*` list to find in-flight work on a cold machine.
Pushing here made park redundant and filled that listing with landed-and-dead branches. If this story WAS
parked, its branch is already on origin and Step 5 deletes it there.

- **`main` is untouched.** Only Daniel, directly or via `/cicd-push-e2e`.
- **Report** the branch, the commit range that landed, and the epic-branch sha — same into the walkthrough's
  `## Your Actions` (Step 1 wrote the section; this is the line it was waiting for).
- ⛔ **Then COMMIT that write, and push it to the epic branch too — a second, tiny landing.** Everything Step 3
  puts in the walkthrough (the merge-gate totals above, this landing line) is written **after** Step 2's
  commit, so without this the walkthrough that actually lands carries neither, and the tree is left dirty:

  ```bash
  git -C "<the story worktree>" add <the story walkthrough>
  git -C "<the story worktree>" commit -m "<KEY> docs(walkthrough): record the landing"
  git -C "<the story worktree>" push origin HEAD:epic/<EPIC-KEY>-<slug>
  ```

  **A dirty tree here is not cosmetic — it reverses two of this command's own rules.** Step 5's
  `/cicd-prune-worktree` treats uncommitted work as data to preserve: it commits the tree and runs
  `git push -u origin claude/<KEY>-<slug>`, which is the push the paragraph above forbids, and then declares
  that branch **not deletable** — so the prune cannot finish, a landed-and-dead `claude/*` branch sits on
  origin, and `/cicd-resume` later offers a story the board already reads `done`. Leave the tree clean and
  none of that fires.
- Landing push rejected (remote moved) → **STOP and report.** Re-sync and re-land, never force. ⛔ **The ticket
  does not move** — Step 4 runs only after a push that returned 0.
- **No shared-checkout reconcile is owed.** It stands on `main`, which moves only when the epic merges via
  `/cicd-push-e2e`. (The old reconcile died with `main_debug` on 2026-08-07.)

## Step 4 — File the Dev Record, THEN move the ticket (AUTOMATIC, never ask)

**After the landing, never before.** A ticket that reads `Done` while the landing stopped is a lie on the board;
a landing that succeeded while the record lags is one command away from correct. Take the recoverable failure.
This is the same order `/smh-close-task-merge-tree` Step 4 uses on the Task lane, and the whole reason the two
families now have one shape.

Read `jira_key:` from the story's frontmatter, then do all three halves:

**a. File the Dev Record** — SCC-49. A verdict line is a receipt, not a record: the decisions, the
pitfalls and what is still owed lived only in the walkthrough, so Jira could say a story shipped but
never what building it taught. **Step 1's routing produced those buckets — carry them here.** Pass
them in; the walkthrough scrape underneath is a safety net, never the source:

```bash
python3 .agents/scripts/jira_feed.py devrecord --key <KEY> --story <id> --project <PROJECT> \
       --outcome "review -> done, landed on epic/<JIRA-KEY>-<slug> @ <sha>" \
       --decision "<a ruling made while building, and why>" \
       --pitfall  "<a failure mode the next agent would hit>" \
       --followon "<what is still owed, or the deferral>" \
       --evidence "<suite totals @ sha>" --closing --apply
```

`--closing` also **clears a `Bug` flag**. A ticket arrives here typed `Bug` when something found it
broken and pulled it back out of `Done` — an audit that traced a live bug to it, or the operator by
hand. Either way that means the fix you just landed IS that bug, so the type goes back to what the
rule says it is (`Story` here, `Task` on the other lane — **never always `Story`**). Close-out is the
only moment anything can know the fix landed, which is why the bulk `audit` leaves Bugs alone and why
nothing else clears one.

Repeat a flag per item. It lifts the `Verdict:` line and the walkthrough path itself, then **reads the
ticket back and exits 2 if the comment is not there** — an acli call that silently no-ops is
indistinguishable from one that worked. **One Dev Record per ticket:** if `/cicd-quick-dev` already
filed one for this story, this UPDATES it in place rather than stacking a second. A bucket you leave
empty renders `(none recorded)` and warns — that is honest, but on a story that fought back it means
Step 1's routing was thin, so go back and read the walkthrough before accepting it.

**b. Move the ticket** to match the flip — `Done` for a close-out, `In Review` for a story left at `review`.
**Run the closer, and give it the ref this story actually landed on** (SCC-242):

```bash
python3 .agents/scripts/jira_feed.py finish --key <KEY> --apply \
  --walkthrough "<the story walkthrough>" \
  --landing-ref "origin/epic/<JIRA-KEY>-<slug>" \
  --status "<Status>"
```

| exit | what it means | what you do |
|---|---|---|
| `0` | closed — `## Your Actions` was clear and the merge row is satisfied by the repo | report `<KEY> → <Status>` |
| `3` | **HELD** — open operator rows, posted to the ticket, status moved along the review ladder | report *awaiting you*, and name the rows |
| `2` | the **artifact** is wrong (no walkthrough, no section, a banned or ceremony row) — **nothing was written** | fix the walkthrough, re-run |
| `4` | the **board** would not take the write | transport, not a verdict — retry |

⛔ **`--landing-ref` is not optional on this lane, and omitting it is worse than not running the
verb at all.** Its default is `origin/main`, and a story's tip is not an ancestor of `main` until the
epic itself ships — so a bare `finish` answers **HELD** forever while the story file already reads
`done`, which is a two-surface divergence dressed as a gate. That defect is why this step used to ban
the verb outright. Pass the epic ref and the same check becomes the one that can actually see this
landing. An unresolvable ref **HOLDS and names itself** — it never reads as a merge.

⛔ **This is also the SECOND `## Your Actions` refusal, and it is the reason to run the verb rather
than transition by hand.** Step 2's `check-actions` is cheap and early; this one reads the walkthrough
*as it landed*. Between them a row can be added by the very commits Step 2 approved.

If the story has no Jira key, skip this verb entirely and say so in the Step 6 summary — `finish`
requires a key and there is nothing here to invent one from.

⭐ **`--yes` and the read-back are now the script's, not yours — that is the point of running the verb.**
`finish` sends `--yes` (without it acli stops on an interactive confirm no agent shell can answer; three
shipped call sites omitted it and `Done` was landing on luck until SCC-113, and `tests/test_jira_feed.py`
fails if any `workitem transition` under `.agents/` is missing it), then **re-reads `status` and returns `4`
if it did not move**. Hand-transitioning here gives up both guards.

⛔ **Read the exit code — because nothing downstream does.** This command exists so the board cannot read
`Done` over unlanded code; the mirror failure is just as real. A transition can fail for ordinary reasons — no
workflow path from the current status, an expired credential, a sandboxed shell that cannot reach the OS
keychain. Step 4c's `jira_feed.py check` does **not** close the gap: it reads the description and the Dev
Record comments and never looks at `status`. So a failed transition would sail past it, Step 5 would prune the
tree and the branch, and Step 6 would print `<KEY> → Done` — with the ticket still at `In Review` and the
rollback point deleted. The exit-code table above is what stands between those two states.

⛔ **`4` and `2` are not the same failure and must not be reported the same way.** `4` is transport: the
walkthrough is fine, nothing is wrong to fix, retry when the board is reachable. `2` means the artifact is
wrong and **nothing was written**. Collapsing them sends you hunting for a defect in a file that is correct.

If the close does not land, **stop with the code landed and say so plainly.** That state is one command from
correct and is recoverable; a pruned worktree over a wrong board is not.

⛔ **And it happens HERE, after Step 3's push returned 0 — never earlier.** This transition is the one write in
the whole close-out that rides no branch, so it is the one write a later STOP cannot undo. It is also why
`--landing-ref` must name the epic: run before the push, or pointed at `main`, the merge row cannot be
satisfied and the verb holds a story that is finished.

⭐ **`jira_feed.py finish` was BANNED here until 2026-08-20, and the ban is lifted (SCC-242).** The reason
was real: its merge check was hardcoded to `origin/main`, so on a lane that lands on `epic/<KEY>-<slug>` it
answered "held" forever while the story status file already read `done`. The door routed around it with raw
`acli`, and the `## Your Actions` refusal that came with the verb was lost with it. `finish` now takes
`--landing-ref` and **resolves** its target — explicit flag, then the manifest's `landing_ref:`, then
`origin/main` — so Step 4b above calls it. ⛔ **Two things had to change, not one:** the ref alone was a no-op,
because `MERGE_DOORS` did not recognise a row naming `/cicd-close-story-merge-tree` and `merge_row_state`
returned `None` before any comparison ran. If you ever see this door's merge row silently ignored, check that
list first.

**c. Verify — twice, and the second one is not redundant:**

```bash
python3 .agents/scripts/jira_feed.py check --key <KEY> --story <id>
python3 .agents/scripts/jira_feed.py check --key <KEY> --project <PROJECT>
```

The **scoped** run (`--story`) answers "does this lane's record exist". The **unscoped** run is the one that can
see a **FORKED Dev Record** (SCC-174): the scoped branch returns before the duplicate and FORK arms ever run, so
a ticket carrying one lane's record filed under two slugs reads as "one Dev Record" and the fork ships. If the
unscoped run reports a fork, an id on the ticket is claimed by no manifest and no branch: **delete the record
filed under the slug that is not a lane and re-post with the branch's slug** — never `--append-new` past it.
Paste both lines into the Step 6 summary; that is the evidence the ticket carries every half.

If the story has no `jira_key` yet (pre-Jira story) or the project has no Jira project, note that in
the Step 6 summary and continue — never invent a key. Full acli reference: `.agents/rules/jira.md`.

## Step 5 — Prune the merged worktree & branches (AUTOMATIC)

Immediately after Step 3's landing succeeded and Step 4 recorded it:
1. Invoke `/cicd-prune-worktree <story-slug>` to verify the merge, remove the local worktree
   (`.claude/worktrees/<story-slug>`), and delete both the local and remote GitHub branches
   (`claude/<JIRA-KEY>-<story-slug>`). **Hand it `$STORY`, `$KEY` and `$BRANCH` — the three strings Step 0
   bound** — so its own Step 0.6 preflight can run `--expect-key <KEY> --branch <BRANCH>` instead of
   resolving a default from `cwd`, which is a guess. (`--repo` is **not** one of them: `closeout_preflight.py`
   takes `--project`, and `--repo` belongs to the Task lane's `task_preflight.py`.)
2. Confirm both local disk and remote origin are clean.

⛔ **Its Step 1.7 authorization gate reads `Status: done`, and on this path Step 1 wrote that before anything
landed — so on this path the gate is satisfied by construction and proves nothing.** What actually authorises
the prune here is Step 3's push returning 0 and Step 4b's read-back, which you have just done. Do not skip
either on the strength of the gate: since the save can write `done` on its own, `done` no longer implies a
close-out ran. The gate still earns its place standalone, against a tree nobody closed out at all.

## Step 6 — Verify, THEN report (never report an unverified success)

Every ✅ below must come from a command you actually ran in this step, not from intent:

```bash
git rev-parse --abbrev-ref HEAD                                   # still the story branch, or gone with its tree
git log --oneline -1 origin/epic/<JIRA-KEY>-<slug>                # the landing is on the remote
git worktree list                                                 # the story tree is gone
```

Print:

`✅ Story <id> closed:`
- `Saved: <the /cicd-update-sprint-memory summary — learnings routed, active-context ~X / 5,000>`
- `Flip: <story> review → done` *(both surfaces, or neither)*
- `Merge gate: <inherited ③ green @ sha | re-run totals>`
- `Landed: <commit range> → epic/<JIRA-KEY>-<slug> @ <sha>` *(`main` untouched)*
- `Jira: Dev Record filed (one record) · <KEY> → Done · check scoped + unscoped, exit 0`
- `Pruned: claude/<JIRA-KEY>-<story-slug> local + remote · tree removed` *(or why it was retained)*
- `Still owed: <the --followon items, or "nothing">`

Optional additional input: $ARGUMENTS
