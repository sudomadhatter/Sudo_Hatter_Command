---
description: Regenerate the shareable teaching edition from this lobby and publish it to Projects/sudo-command-center — export to scratch, leak-scan, clear the tracked tree so deletions are real, show the operator the diff, then commit on top.
platforms: [opencode, antigravity, claude, codex, zoo]
---

# /smh-publish-teaching-edition — refresh the copy the team pulls

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only; `main` is never an agent's; the operator merges the PR
> - `.agents/rules/constitution.md` — never hardcode secrets; ask before deleting; a public repo is an irreversible surface
> - `.agents/rules/living-template-sync.md` — the teaching edition is GENERATED; the skeleton still is not

**What this is for.** `Projects/sudo-command-center` is the command centre your team clones. It is a
**sanitized export of this lobby**, produced by `.agents/scripts/export-teaching-edition.ps1` from
`.agents/scripts/teaching-edition/lobby.manifest.json` — never hand-maintained, and nothing ever
flows back from it. Team members keep current with `git pull`; they add their own work with
`/smh-new-project` against the skeleton. This door is how the copy they pull gets refreshed.

⛔ **THE PUBLISHED REPO IS PUBLIC.** The leak scan inside the exporter is the only thing standing
between this workspace and the internet. It checks every exported byte — **contents AND file
paths** — for the operator's name, handles, machine name, client names and every value in the live
`.env`. No step here may skip, weaken, narrow or work around it. If it reports a hit, **stop and
report**; do not "fix" the hit by adding an exemption.

⛔ **NEVER FORCE-PUSH AND NEVER RE-INIT THE PUBLISHED REPO.** Every team clone is pinned to that
history. This door only ever commits **on top**. A rewritten history breaks every clone your team
has, silently, at their next pull.

---

## Step 0 — Bind, and refuse an unreproducible snapshot

```bash
LOBBY=$(git rev-parse --show-toplevel)
cd "$LOBBY"
git status --short > /tmp/te-status.txt 2>&1
git rev-list --count @{upstream}..HEAD > /tmp/te-ahead.txt 2>&1
```

**Refuse and stop** if either is non-empty / non-zero:

| State | Why it refuses |
|---|---|
| the lobby tree is dirty | the export would snapshot uncommitted work; nobody could ever reproduce what was published |
| `HEAD` is ahead of its upstream | the stamp would name a commit that exists on no remote, so the provenance line points at nothing |

Both are about the **provenance stamp**, not tidiness: the export writes
`.teaching-edition-source` carrying the lobby sha, and a sha nobody else can resolve is worse than
no sha at all.

⛔ **Run this from the lobby's own checkout, not a worktree**, unless the worktree is what you
intend to publish. The stamp records whatever `HEAD` you run against.

## Step 1 — Export to a scratch directory OUTSIDE the lobby

```bash
SCRATCH=$(mktemp -d)/teaching-edition
pwsh -File .agents/scripts/export-teaching-edition.ps1 \
  -Manifest .agents/scripts/teaching-edition/lobby.manifest.json \
  -Target "$SCRATCH" > /tmp/te-export.txt 2>&1
```

⛔ **The scratch directory must be outside the lobby, and this is forced by the engine, not chosen.**
`export-teaching-edition.ps1` refuses a target inside the source tree — *"Target must be outside the
source tree to prevent recursive self-copy"* — and the published repo lives at
`Projects/sudo-command-center`, which **is** inside it. It also refuses a non-empty target. So the
export can never be written straight to its destination, and a repo-local `scratch/` is refused too.
Temp-then-publish is the only shape available.

Read the tail of `/tmp/te-export.txt`. It must end with **`TEACHING EDITION VALID`**. Anything else
— a leak hit, a missing overlay source, a missing line-transform anchor, a failed validator — is a
**stop**. Report what it said and fix the cause; never re-run with a guard removed.

## Step 2 — Clear the TRACKED tree, then copy the export in

**This step is the whole point of this door.** The exporter cannot write into a non-empty target, so
the old way of publishing was to copy the export over the repo — and **a copy adds and overwrites but
never removes**. That is how 84 files `main` had deleted were still in every team clone, including a
whole retired command surface a reader could still invoke.

```bash
PUB="$LOBBY/Projects/sudo-command-center"
cd "$PUB"
git ls-files -z | xargs -0 rm -f
cp -a "$SCRATCH/." "$PUB/"
```

⛔ **`git ls-files -z | xargs -0 rm -f` — enumerated by git, never by the shell.** This removes
exactly what git knows about and nothing else. A `rm -rf *` in that directory would also destroy the
reader's untracked files, and aimed one level wrong it eats `.git` and the history every team clone
depends on. Tracked-only. Never a glob. Never `-r`.

⛔ **Untracked files in the published tree SURVIVE this on purpose.** A reader's own notes, their
`.env`, their `Projects/` work — none of it is tracked, so none of it is touched.

## Step 3 — Show the operator the diff, counted THREE ways

```bash
cd "$PUB"
git add -A
git status --porcelain > /tmp/te-diff.txt 2>&1
```

⛔ **`git add -A` is correct HERE and nowhere else in this system.** The house ban exists because a
wildcard sweeps up other parallel work; this tree has no parallel work — it is a generated artifact
whose entire contents were just replaced wholesale, and the deletions are the payload. Staging
explicit paths would mean enumerating thousands of generated files. This is the one door with that
carve-out, and it applies to `Projects/sudo-command-center` only.

Print the three counts **separately**, because the deletions are what the operator most needs to see:

```bash
awk '{print $1}' /tmp/te-diff.txt | sort | uniq -c
```

Then **STOP and hand it to Mr. Hatter** with:

- the three counts — added / modified / **deleted**
- the deleted paths, in full if there are fewer than 40, else grouped by top folder
- the source sha from `.teaching-edition-source`
- the leak-scan line from the export log (needles checked, hits = 0)

⛔ **Publishing to a public repo stays a deliberate human act.** Do not commit, do not push, do not
open the PR until he has read the deletions and said the word.

## Step 4 — Commit on top and open the PR

Only after his word:

```bash
cd "$PUB"
git commit -m "chore: refresh teaching edition from lobby <short-sha>"
git push origin HEAD
gh pr create --base main --head "$(git rev-parse --abbrev-ref HEAD)" \
  --title "chore: refresh teaching edition from lobby <short-sha>" \
  --body "<the three counts from Step 3, the deleted paths, and the source sha>"
```

⛔ **No `--force`. No `--force-with-lease`. No `git init`. No orphan branch.** If the push is
rejected, the remedy is to fetch and rebase-or-merge like any other repo — never to overwrite. A
rejected push here means someone else published; find out who and what before doing anything.

Hand the operator the PR link and stop. **He merges it.**

## Step 5 — Bump the lobby's submodule pointer

After he merges, in the lane you are working in:

```bash
cd "$LOBBY"
git add Projects/sudo-command-center
git commit -m "<KEY>: bump the published teaching edition pointer"
```

The pointer commit is what records, in the lobby's own history, which published snapshot this lobby
produced. Without it the lobby says nothing about what the team is running.

---

## What this door does NOT do

- It never edits a file inside `Projects/sudo-command-center` by hand. Every byte there is generated;
  a hand edit is deleted by the next export and, worse, **bypasses the leak scan on a public repo.**
  Something wrong in the published edition is a bug in the lobby master or in the manifest — fix it
  there and re-export.
- It never merges its own PR.
- It never adds a leak-scan exemption to get past a hit.
- It never touches `Projects/sudo-project-skeleton`. That is a second living template with its own
  manifest and no detector yet; it gets its own ticket.
