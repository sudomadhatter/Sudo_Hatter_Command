---
description: Safely verify a story branch has been merged into its epic branch, preserve any uncommitted work, then prune EVERY stale worktree on disk and delete both local and remote (GitHub) branches. Sweeps all trees, not just the named slug.
---

# /sudo-close-workingtree — Close & Prune Merged Worktree & Branches

Safely clean up story worktrees and their git branches (`claude/<JIRA-KEY>-<story-slug>`) after a story has landed on
its epic branch (`epic/<JIRA-KEY>-<slug>`).

**Order is load-bearing and the numbering enforces it: SWEEP → PRESERVE → UNLINK → REMOVE → DELETE BRANCH.**
Every out-of-order variant of this command has destroyed something. Do not reorder, and do not skip a step
because the tree "looks empty" — every incident below started with a tree that looked empty.

## Step 0 — Resolve target project and story slug
1. **Target Project** — bind per `.agents/rules/sudo-target-resolution.md` §STD: self fast-path →
   `$ARGUMENTS` override → `.agents/active-project.txt` → else ask the operator. Set `PROJECT_ROOT`.
2. **Target Story Slug**:
   - If `$ARGUMENTS` provides a story slug or branch name (e.g. `21-12-fail-closed-admin-roles` or `claude/21-12-fail-closed-admin-roles`), strip any `claude/` or `.claude/worktrees/` prefix to extract `<story-slug>`.
   - Otherwise, if standing inside a worktree `.claude/worktrees/<story-slug>`, extract `<story-slug>` from current working directory.
   - Otherwise, read the active story slug from `PROJECT_ROOT/_bmad-output/implementation-artifacts/sprint-status.yaml`.

Echo `Target: Projects/<name> | Story: <story-slug>` before proceeding.

## Step 0.6 — Preflight first (fast pre-check — it does NOT replace the gates below)

```bash
python .agents/scripts/closeout_preflight.py --story <id> --project <PROJECT> --fetch [--branch <name>]
```

One call answers Steps 1 and 1.6's questions mechanically: is the branch an ancestor of
the epic branch, is every repo `0/0` and clean, and is each registered worktree LIVE / LOST (registered,
no directory) / HUSK (directory, no `.git` — the state that blocks the next `worktree add`).
**Exit 2 → stop here.** A `landing was NOT verified` warning is not a pass — resolve it before anything
is removed.

⛔ **It does not authorize deletion.** The preflight reads; it never writes. Steps 1.7 (authorization),
2 (preserve uncommitted work) and 3a (unlink every reparse point BEFORE any recursive remove) are
data-loss gates the script does not cover — run them in full, exactly as written. Deleting through a
junction destroys the shared `backend/.venv` and `node_modules` **targets**, not just the links.

## Step 1 — Safety Verification Gate (MANDATORY)
In `PROJECT_ROOT`:
```bash
# 1 · Fetch latest remote refs
Remove-Item Env:\GITHUB_TOKEN -ErrorAction Ignore; git fetch origin

# 2 · Resolve the story's epic branch (exactly one live epic/* is the normal case)
git for-each-ref --format='%(refname:short)' refs/remotes/origin/epic/*

# 3 · Verification check: confirm story branch has landed on origin/epic/<JIRA-KEY>-<slug>
git merge-base --is-ancestor claude/<JIRA-KEY>-<story-slug> origin/epic/<JIRA-KEY>-<slug>
```

- **Exit code 0**: the branch is fully merged into `origin/epic/<JIRA-KEY>-<slug>`. Proceed to Step 1.6.
- **Non-zero**: **STOP IMMEDIATELY!**
  Print: `❌ Refusing to delete: claude/<JIRA-KEY>-<story-slug> is NOT fully merged into origin/epic/<JIRA-KEY>-<slug>.`
  Instruct: `Land the story first using /sudo-update-sprint-memory or git merge to origin/epic/<JIRA-KEY>-<slug>.`

**Record this result per branch.** Step 5 deletes branches, and it may ONLY delete a branch that passed this
check. A tree can be safe to remove while its branch is not safe to delete — those are different questions.

> *(The old Step 1.5 shared-checkout reconcile died with `main_debug` on 2026-08-07 — the shared checkout
> stands on `main` and only moves when an epic merges via `/sudo-push-e2e`. Nothing to backstop here.)*

## Step 1.6 — SWEEP every worktree on disk FIRST (before removing anything)

⚠️ **This runs BEFORE any removal, and it covers LIVE worktrees, not just orphans.** The slug you were
invoked with is not the scope — the disk is. A registered worktree belonging to some *other* story is
invisible to every slug-scoped step below, and a stale one is precisely what makes an agent "pick up the
wrong tree".

Two failure modes this catches, both observed **2026-07-27** in a single run where the target slug's own
tree was perfectly clean:
- a **dead 21.5 husk** — invisible to `git worktree list` because a previous close-out pruned the
  registration but left the folder, still holding live junctions to the shared `.venv` and both
  `node_modules`; it sat in the IDE side panel for a full day.
- a **live 21.4 tree holding 1,197 uncommitted lines** — a story file, an implementation plan and both
  red-phase test tiers from a `/sudo-write-story-tests` run that never committed.

```powershell
$root = "PROJECT_ROOT/.claude/worktrees"
if (Test-Path $root) {
  # Registered worktree paths, normalised for comparison.
  $known = @((git worktree list --porcelain) -match '^worktree ' -replace '^worktree ','' |
             ForEach-Object { $_.Replace('/','\').TrimEnd('\') })
  foreach ($d in @(Get-ChildItem $root -Force -Directory -EA SilentlyContinue)) {
    # NOTE: $d, not $_ — an inner Where-Object rebinds $_ to ITS OWN item. The original version of
    # this sweep wrote `$known | Where-Object { ... "*$($_.Name)*" }`, which compared each path
    # string against itself; strings have no .Name, so the pattern collapsed to "**", every
    # directory looked known, and the sweep printed NOTHING while a real husk sat on disk.
    $isKnown = @($known | Where-Object { $_ -ieq $d.FullName.TrimEnd('\') }).Count -gt 0
    $hasGit  = Test-Path (Join-Path $d.FullName '.git')
    $dirty   = if ($hasGit) { @(git -C $d.FullName status --short).Count } else { 'n/a' }
    $state   = if (-not $hasGit) { 'HUSK' } elseif ($isKnown) { 'LIVE' } else { 'LOST' }
    Write-Output "$state  $($d.Name)  (registered=$isKnown, .git=$hasGit, uncommitted=$dirty)"
  }
}
```

⛔ **Never assign to a lowercase alias of an outer variable** (`$p = Join-Path $P …`). PowerShell variable
names are **case-insensitive**, so `$p` and `$P` are ONE variable — a loop written that way overwrites its
own root path on the first iteration and every later check silently reads a bogus path. On 2026-07-27 that
produced a false "shared assets MISSING" report that briefly looked like the delete had eaten `.venv`.

**Classify every row and carry the list into the steps below:**

| State | Meaning | Action |
|---|---|---|
| **HUSK** | no `.git` — dead folder from an earlier bad close-out | Step 3 unlink-then-delete. Step 2 does not apply (git cannot read it) — say so, don't skip silently. |
| **LOST** | has `.git` but unregistered — a live worktree git lost track of | **STOP and report.** Never delete. |
| **LIVE**, uncommitted = 0 | registered, clean | Remove **only if** its branch passed Step 1. Otherwise leave it and name it. |
| **LIVE**, uncommitted > 0 | registered, holds unsaved work | **Step 2 FIRST.** Preserve, push, then remove. Never `--force` past it. |

Report every directory found, its state, and what you did with it — **including the ones you left alone and
why**. A tree you decided to keep is a decision, and an unreported decision reads as an oversight.

## Step 1.7 — Close-out authorization gate (what makes cleanup APPROVED)

**A worktree exists only while a story is being worked.** Cleaning one up is authorized by the story being
**closed out** — not merely merged. Step 1 proved the code landed; that is a different question from
whether the operator finished the story. This step answers the second one, and it is what replaces
deference with a lookup: if the gate passes, **act — do not ask.**

This also closes a failure you have already been bitten by: **debug-2.2 sat merged-but-not-closed-out for
five days** while every planning surface recommended rebuilding it. Under merge-base alone its tree would
have been pruned, erasing the last on-disk hint that the close-out never ran.

Per tree, in order — first match wins:

1. **Story file frontmatter reads `Status: done`** (`_bmad/bmm/stories/<story>.md`; grep BOTH dot and dash
   forms of the id) → **AUTHORIZED.** This is the authority — only a human close-out writes `done`
   (`story-status-flip-contract`: dev sets `review`).
2. **Board key exists in `sprint-status.yaml` and reads `done`** → corroborated. Say so.
3. **Board key ABSENT** → check the CHANGE LOG for the slug.
   - Found → **AUTHORIZED**, and **state in the report that no board key exists.** Standalone quick-dev
     tickets legitimately have none (prior art: `security-profile-idor-fix`, `gemini-key-pytest-env`), but
     a missing key is otherwise indistinguishable from the debug-2.2 failure, and a missing key fires no
     drift check anywhere. Naming it is the only thing that surfaces it.
   - Not found → **STOP** (below).
4. **Status is `review` / `in-progress` / `backlog`, or nothing corroborates** → **STOP.** Print:
   `❌ <slug> is merged but not closed out (status: <x>). Run /sudo-update-sprint-memory first, then re-run.`
   Leave the tree and the branch exactly as they are.

⛔ **This gate has exactly two outcomes: AUTHORIZED, or a STOP with a named reason and the fix.** There is
no third "the board looks ambiguous, checking with you" branch — that is the punt-hatch this gate exists to
remove, and re-introducing it recreates the very problem it was written for. Ambiguity resolves to the STOP
in (4), stated as a refusal, never as a question.

**Normal path cost: zero.** `/sudo-update-sprint-memory` Steps 1–7 flip the status, write the board and
land the code before Step 8 ever calls this command — so the gate is satisfied by construction. It only
bites when the prune is run standalone against something that was never actually closed out. Which is
exactly when it should.

## Step 2 — PRESERVE uncommitted work before ANY removal (MANDATORY — data-loss gate)

⛔ **`git worktree remove --force` DISCARDS uncommitted and untracked files without a prompt.** Step 1's
merge-base check proves the *branch* landed; it says nothing about work in the tree that was never
committed. Those are different questions and historically only one of them was being asked. The 1,197-line
21.4 tree above would have been destroyed silently, and nothing downstream would ever have reported a loss.

For **every** worktree Step 1.6 marked for removal:

```bash
git -C .claude/worktrees/<slug> status --short      # ANY output = unsaved work
```

- **Empty** → nothing at risk, proceed.
- **Any output** → **do NOT remove yet.** Commit it to its own branch and push, so the work becomes
  reproducible instead of unique to that disk:
  ```bash
  git -C .claude/worktrees/<slug> add <explicit paths>     # never `git add -A`
  git -C .claude/worktrees/<slug> commit -m "wip(<story>): preserve uncommitted work before worktree prune"
  git -C .claude/worktrees/<slug> push -u origin claude/<JIRA-KEY>-<slug>
  ```
  Then say plainly in the report that you committed someone else's in-flight work, what it was, and that
  the story's status is **unchanged** — a preservation commit is not progress and must never be reported as
  it, on the board or anywhere else.
- **Cannot push** (no remote, detached HEAD, conflict) → **STOP and report.** Never remove a tree whose only
  copy of the work is local.

⛔ **A branch you just pushed preserved work to is NOT deletable.** Flag it for Step 5 — deleting it throws
away the thing you just saved.

## Step 2.5 — Exit the worktree directory if you are inside it
If `cwd` is inside any `PROJECT_ROOT/.claude/worktrees/<slug>` you are about to remove, shift `cwd` out to
`PROJECT_ROOT` so the directory is unlocked. A shell sitting inside is the most common cause of the
"being used by another process" failure in Step 3.

## Step 3 — Unlink junctions, THEN remove the worktree

**This order is mandatory and is the reverse of what feels natural.**

`git worktree remove --force` de-registers the worktree but **leaves the directory on disk when reparse
points are present** — observed 2026-07-27 on `story-21-4`: it returned success, dropped the registration,
and left the folder holding three live junctions. Removing first therefore MANUFACTURES the exact HUSK
Step 1.6 exists to catch, *and* strips the `git worktree list` entry that would have told you it was still
there.

### 3a · Unlink every reparse point (ALWAYS FIRST)

⛔ **`Remove-Item -Recurse` FOLLOWS junctions and deletes the TARGET.** A story worktree does not inherit
gitignored assets, so lanes junction shared assets back to the **main checkout** (see
`worktree-per-story.md`). A naive recursive delete walks straight through those junctions and destroys the
real asset in `PROJECT_ROOT` — breaking the shared checkout *and* every other live worktree pointing at it.

**Never work from a list of "the junctions I created."** Two independent reasons that list is wrong:
- Known shared-asset links are **at least** `frontend/node_modules`, `firebase/tests/node_modules` **and
  `backend/.venv`** — `.venv` was missing from this command until 2026-07-27 and is the one that orphaned
  the 21.5 tree.
- **Tools create junctions on their own.** Next.js/Turbopack plants them under
  `frontend/.next/dev/node_modules/` (e.g. `import-in-the-middle-*`, `require-in-the-middle-*`) simply by
  running the dev server or the E2E gate. Observed 2026-07-27: 2 of 3 reparse points in a worktree were
  created by Next, not by any lane.

**Therefore: always ENUMERATE, never assume. The scan is the authority.**

```powershell
$wt = "PROJECT_ROOT/.claude/worktrees/<slug>"
# enumerate every reparse point (junction/symlink) and unlink it.
# .Delete() on the DirectoryInfo removes the LINK only, never the target, and unlike
# `cmd /c rmdir` it cannot be mis-parsed by a shell wrapper.
foreach ($l in @(Get-ChildItem $wt -Recurse -Force -Directory -EA SilentlyContinue |
                 Where-Object { $_.LinkType })) {
  Write-Output "unlinked: $($l.FullName)  ->  $($l.Target)"; $l.Delete()
}
# prove none remain BEFORE anything recursive touches this path
$left = @(Get-ChildItem $wt -Recurse -Force -Directory -EA SilentlyContinue | Where-Object { $_.LinkType })
if ($left.Count) { Write-Output "ABORT - reparse points still present"; $left | Select-Object FullName }
```

### 3b · Remove the worktree and prune

```bash
git worktree remove --force .claude/worktrees/<slug>     # skip for a HUSK — no registration exists
git worktree prune
```

### 3c · Delete the leftover directory (only once 3a proved zero reparse points)

```powershell
Remove-Item -Recurse -Force $wt -Confirm:$false -ErrorAction Stop
```

`-ErrorAction Ignore` is deliberately NOT used: a failure here must be visible, not swallowed.

**If the delete fails with *"being used by another process"***, the unlink half has already made the husk
harmless (no reparse points left). Do **not** retry in a loop and do **not** report success — name the
leftover path, say the junctions are unlinked so it is now safe to delete by hand, and carry it in the
report. Common holders: an editor file-watcher, or a shell whose `cwd` is still inside (Step 2.5).

## Step 4 — Verify the shared assets SURVIVED

Run this before touching any branch. The unlink in 3a and a destructive follow-through look identical to a
bare existence check for the moment between them, so **probe, don't just `Test-Path`**:

```powershell
PROJECT_ROOT/backend/.venv/Scripts/python.exe --version              # must print a version
@(Get-ChildItem PROJECT_ROOT/frontend/node_modules -Force).Count     # must be non-zero
@(Get-ChildItem PROJECT_ROOT/firebase/tests/node_modules -Force).Count
```

Any failure here → **STOP and report immediately.** A destroyed shared asset breaks every other lane on the
machine, and it is recoverable only if someone knows it happened.

## Step 5 — Delete branches — ONLY those that passed Steps 1 AND 1.7

**Order is REMOTE first, local second — the reverse fails.** A landed branch's close-out commits are
never pushed to `claude/*` (the landing pushes `HEAD:epic/<JIRA-KEY>-<slug>` only), so a PARKED branch's local tip
is ahead of its upstream. `git branch -d` checks merged-into-**upstream** when an upstream exists — and
refuses. Deleting the remote first removes the upstream, so `-d` falls back to the merged-into-HEAD
check and succeeds honestly (observed 2026-08-01: all three set-close-out `-d`s failed remote-last,
all three succeeded remote-first).

```bash
# Remote FIRST: ONLY if the branch is actually on origin — i.e. it was PARKED.
git ls-remote --heads origin claude/<JIRA-KEY>-<story-slug>                    # empty → nothing to delete, say so
Remove-Item Env:\GITHUB_TOKEN -ErrorAction Ignore; git push origin --delete claude/<JIRA-KEY>-<story-slug>

git branch -d claude/<JIRA-KEY>-<story-slug>                                   # -d first; see the HEAD caveat below
```

⚠️ **The merged-into-HEAD fallback checks `main` now** (the shared checkout stands there), and `main`
does not contain the story until its epic merges via `/sudo-push-e2e` — so `-d` can honestly refuse on
a branch that HAS landed. In exactly that case, Step 1's recorded `merge-base --is-ancestor …
origin/epic/<JIRA-KEY>-<slug>` pass IS the merged proof: delete with `git branch -D` and cite that pass in the
report. No recorded Step 1 pass → never `-D`.

⛔ **Delete a branch ONLY if it passed Step 1 (landed) AND Step 1.7 (closed out).** Removing a *tree* is
cheap — the branch recreates it. Deleting the *branch* of an unlanded story destroys the only copy of that
work, including anything Step 2 just preserved. Step 1.6 deliberately reaches trees belonging to **other**
stories; those branches have not been checked and must **not** be deleted.

- Landed + closed out → delete local; delete remote **only if `ls-remote` finds it**.
- Landed, not closed out → Step 1.7 already STOPped. Nothing is deleted.
- Not landed, tree removed → **keep both branches**, and report: *"tree pruned; branch `claude/<JIRA-KEY>-<slug>`
  retained — restore with `/sudo-resume`."*
- `git branch -d` refuses → check WHY before reaching for `-D`. With the remote already deleted (the
  order above), a refusal is either the expected HEAD-is-`main` caveat above (Step 1 passed → `-D` with
  the cited proof) or the branch genuinely never landed — go back to Step 1. (If you ran it remote-last,
  the refusal is probably just the upstream check — delete the remote and retry `-d` once.)

**Most story branches will not exist on origin at all, and that is correct.** Per `git-policy.md` → "The
landing", the landing pushes `HEAD:epic/<JIRA-KEY>-<slug>` and **not** the branch; a story branch reaches origin only
via `/sudo-park`. So an absent remote branch is the normal case — report it as *"never pushed (not
parked) — nothing to delete"*, not as a failure. A remote branch that IS present means this story was
parked, and deleting it here is what stops `/sudo-resume` from later offering a story that is already done.

⛔ **Never sweep `claude/*` on origin wholesale.** `incident-*` branches come from the Epic-16 incident
pipeline, not story flow, and are outside this command entirely.

## Step 6 — Verify, THEN report (never report an unverified success)

⛔ **Prove each claim before printing it.** The 21.5 close-out reported a clean removal while the directory
was still on disk holding three live junctions — because the report was written from intent, not from a
check. Every ✅ below must come from a command you actually ran in this step:

```powershell
Test-Path "PROJECT_ROOT/.claude/worktrees/<slug>"              # must be False
git worktree list                                              # must not list it
git branch --list claude/<JIRA-KEY>-<slug>                                # empty IF you deleted it
git ls-remote --heads origin claude/<JIRA-KEY>-<slug>                     # empty IF you deleted it
Get-ChildItem "PROJECT_ROOT/.claude/worktrees" -Force -Directory   # every remaining row must be one
                                                               # you deliberately KEPT and named
```

If a check fails, print ❌ for that line with the actual state — a partial cleanup reported as complete is
worse than no cleanup, because nothing will look again.

Print summary:
`🧹 Closed workingtree & pruned branches for <story-slug>:`
- `✅ Local worktree removed: .claude/worktrees/<story-slug>` *(verified absent)*
- `✅ Local branch deleted: claude/<JIRA-KEY>-<story-slug>` *(or "retained — not landed")*
- `✅ Remote GitHub branch deleted: origin/claude/<JIRA-KEY>-<story-slug>` *(or "retained" / "never pushed")*
- `✅ Shared assets intact: frontend/node_modules · firebase/tests/node_modules · backend/.venv` *(probed)*
- `🧹 Swept: <every tree found, its state, and its disposition — or "none">` *(from Step 1.6)*
- `💾 Preserved: <what was committed and pushed, and to which branch — or "nothing uncommitted">` *(Step 2)*
