---
description: "The ONE shipping command — gate a finished epic branch (epic/<JIRA-KEY>-<slug>) and OPEN A PULL REQUEST into main, refusing until the full gate is green: enforcement suite + build + /cicd-e2e GREEN. It never merges: invoking it IS the operator's per-merge sign-off, and their click on Merge pull request is how that decision reaches GitHub. Absorbs origin/main into the epic first so conflicts never land on production. Re-invoked as --after-merge <KEY> it verifies the merge with plain git, watches the deploy, verifies live, prunes the epic branch and moves the epic ticket. Use when the user says 'ship it' / 'push the epic' / 'sudo push e2e'."
---

# /cicd-push-e2e — Gate the Epic, Open the PR, Deploy

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never force-push;
>   every branch and every commit carries the repo's Jira key (armed 2026-08-07)

The one shipping command. It gates a finished **epic branch** (`epic/<JIRA-KEY>-<slug>`) and opens a
**pull request** into **`main`** — live production — and it **refuses to open that PR until the full
gate is green**. Invoking this command IS the operator's per-merge sign-off for the one epic it ships.

⭐ **It never merges.** The gate runs here, on this machine, where the suites and the E2E harness
live; the merge happens on GitHub, on the operator's click. Re-invoke it as
`--after-merge <JIRA-KEY>` and it verifies that merge with plain git, watches the deploy, verifies
live, prunes the branch and moves the ticket (Step 4.5 onward).

⭐ **That sign-off is a DECISION, given in exactly one of three forms: the word `approved`, invoking
`/smh-close-task-merge-tree`, or invoking `/cicd-push-e2e`** (operator ruling, 2026-08-17). The
**decision to proceed is the sign-off**, and from that word on every step below is the ceremony's
and you run it — including Step 4's PR, which carries that same invocation as its authority, and the
whole `--after-merge` half, which is the agent's work and never a chore handed back.

**Branch model (never violate):** `main` is the only long-lived branch. Epics integrate on short-lived
`epic/<JIRA-KEY>-<slug>` branches and reach `main` only through this command. The key sits immediately
after the prefix and must be one of the repo's keys in `.agents/jira.conf` — the armed commit-msg hook
rejects commits carrying the wrong project's key. After the merge, the epic branch is **deleted** —
nothing accumulates. (The old `main_debug` integration branch was retired 2026-08-07; any doc still
describing "promotion from main_debug" predates that. Pre-Jira branches named plain `epic/<slug>` may
still exist — **rename one to carry its real key before it ships** (Step 1.5 refuses a keyless
branch: production would otherwise carry a merge no ticket joins to); never invent a key.)

## 🛑 MANDATORY RULES (Before You Start)
1. **The gate is not optional**: a red gate STOPS the command. Report what failed; do not "push anyway".
2. **Clear GITHUB_TOKEN on push/pull**: prefix with `$env:GITHUB_TOKEN = ""` (PowerShell) or
   `env -u GITHUB_TOKEN` (Bash) to prevent stale-session auth failures.
3. **On a deploying repo, the merge of this PR IS a production deploy.** Know the rollback path
   (previous Cloud Run revision / previous hosting release) before you open the PR, not after — the
   operator clicks on the strength of what you hand them.

## Step 0 — Resolve the target project (FIRST — before anything else)
Bind the target per `.agents/rules/smh-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override → `.agents/active-project.txt` → else **STOP and ask** — never guess, never operate on the
lobby. Set `PROJECT_ROOT` and **echo exactly** `Target: Projects/<name>`. All git/test commands below run
inside `PROJECT_ROOT`.

## Step 0.6 — Pin the ticket you MEAN (before any tool has answered anything)
```bash
EXPECTED_KEY=<the epic's Jira key>     # the ticket you MEAN, never one read back off a branch
```
A key derived from the branch you are about to resolve cannot disagree with it — pinning it here
is what makes Step 1.5's match a real comparison. No ticket → **STOP and ask.**

## Step 1 — Resolve the epic branch
From `$ARGUMENTS` (an `epic/<JIRA-KEY>-<slug>` name) or by discovery:
```bash
git fetch origin
git branch -a --list '*epic/*'          # live epic branches, local + origin
```
- **Exactly one live epic branch** → that's the candidate; Step 1.5 confirms it mechanically.
- **Several** → show them with `git log --oneline origin/main..<branch> | head` each and decide together.
- **None** → nothing to ship; if the operator is pointing at a `chore/<JIRA-KEY>-<slug>` branch, **the
  diff decides, not the ask**: Step 1.5 admits it here under the **light gate** only when it touches a
  **deployable** path (`backend/ frontend/ firebase/ functions/ mobile/ .github/`). Nothing deployable →
  it refuses, and that lane closes out through `/smh-close-task-merge-tree`, which owns the Task ceremony
  this door does not have. (Ruling 2026-08-07: chore branches carry their own ticket key too.)

Extract the epic's Jira key from the branch name — it drives Step 6.5. A branch with no key is a
pre-Jira epic: rename it first (see the branch model above), and never invent a key.

A chore lane that legitimately stays here **substitutes `chore/<JIRA-KEY>-<slug>` for
`epic/<JIRA-KEY>-<slug>`** in Step 2's checkout, Step 3.5's commit and push, Step 4's push and the PR's `--head`,
Step 4.5's ancestor check, and both Step 6 prune lines; Step 6.5 moves the chore ticket and the child-story sanity check does not apply.

Sanity: every story on the board for this epic should be `done`. If stories are still open, STOP and
name them — `/cicd-merge-epic-workingtrees` or the story close-outs come first.

## Step 1.5 — Pre-flight (mechanical — from the LOBBY, before anything is written)
```bash
BRANCH=<the branch Step 1 resolved>
python3 .agents/scripts/ship_preflight.py --repo "$PROJECT_ROOT" --branch "$BRANCH" \
        --expect-key "$EXPECTED_KEY"                                    # PC: `python`
```
⛔ **Standing in the lobby, not in `PROJECT_ROOT`** — a thin project carries no
`.agents/scripts/*.py`, so the same line run there is *No such file*, which reads as "no pre-flight
here". **Read the header before the verdict**: it echoes the branch the script actually resolved, and
a key that is not `$EXPECTED_KEY` means you are pointed at another lane. **Exit 2 → STOP.**

It answers shape · intent · clean-and-`0 0` · the lane. The clean check is the one that earns the
step: uncommitted work in the checkout makes Step 3 gate a tree Step 4's merge will not carry, so
what ships was never gated — and nothing else in this file would say so.

## Step 2 — Sync the epic branch with main (BEFORE gating)
Hotfixes can land on `main` mid-epic (incident lane). Absorb them first so the gate tests what will
actually ship:
```bash
git checkout epic/<JIRA-KEY>-<slug>
git pull --ff-only origin epic/<JIRA-KEY>-<slug>       # be current with the remote epic
git merge origin/main                        # absorb production; conflicts surface HERE, not on main
```
A conflict is a STOP-and-resolve-together, never a force. If this merge brought in changes, the gate
below runs on the post-merge tree — that is the point.

## Step 3 — Run the gate (on the epic branch)
**Light gate (always):**
1. Backend: full pytest suite via the canonical venv (`backend/.venv` — never the global interpreter).
2. Frontend: production build (`npm run build` / `npx next build` in `frontend/`) — zero compile errors.
3. CI/CD credentials: check what the deploy workflows actually reference. WIF-based workflows
   (workload_identity_provider in the yml) need no stored secrets; otherwise verify required secrets
   (`gh secret list`) and variables (`gh variable list`). Missing → STOP and warn.

**Full gate (any epic merge):**
4. Run **`/cicd-e2e`** — it must finish **green**. Its report is the promotion evidence; link it in the
   ledger row (Step 3.5).

Any failure → **STOP**. Summarize the failures, file/link the evidence, and suggest the lane
(`/cicd-quick-dev` or the ①②③ story loop). Do not proceed.

## Step 3.5 — Record the landing on the lane, BEFORE the PR

⛔ **The bookkeeping rides the PR. It is written HERE, on the epic branch, never after the merge.**
`main` is reached through a pull request with a green `main-write-gate`, so a bookkeeping commit made
afterwards is a **direct push that the ruleset refuses by design** — measured at the AVCH-111
close-out on 2026-08-31, where the ledger commit needed its own operator approval and a hand-built
`--no-ff` merge just to land. Written here it lands with the merge, for free. This is the same law
`/smh-close-task-merge-tree` Step 2.5 and `/cicd-close-story-merge-tree` Step 2 already carry.

⭐ **Write it in the PENDING tense, because nothing has shipped yet.** At this point the PR is not
open, the operator has not clicked, and Step 5 has not watched a single deploy. A row that says the
epic *shipped* is a claim about the future, and if Step 5's deploy goes red or gets rolled back,
`main` carries a false record that Step 6 then forbids you to correct. So the row records **what was
gated and what is pending**, and the **deploy outcome goes on the ticket at Step 6.5**, where it is
known.

1. **Ledger**: add a row to `PROJECT_ROOT/_artifacts/INDEX.md` — what this epic contains, that it is
   **gated green and pending the operator's merge**, and the gate evidence link (the `/cicd-e2e`
   report from Step 3). **Copy the columns already in use; never add or reorder them** — every
   ledger here has a free-prose column, and the evidence link goes in that, not in a new one.

   ⭐ **Number-free on purpose.** The PR number does not exist yet — it is assigned when Step 4 opens
   the PR, which is *after* this commit is pushed — and the merge SHA does not exist until the
   operator clicks. Neither ledger carries a column for either. **Both go on the ticket at Step 6.5**
   (`Merged to main via PR #<N> at <merge-sha>`), where both are known. Do not "fix" this by moving
   the row back after the merge; that is the refusal above.

   ⚠ **A repo with no Jira key has no Step 6.5** (that step skips itself — see it), so for those the
   PR number and merge SHA live only in git history and on GitHub. That is accepted, and it is why
   this row names the epic branch and the gate evidence, which ARE knowable here.

2. **Active context**: record in the project's `active-context.md` that this epic is gated and
   awaiting the merge — again pending, not past tense.

3. **⭐ Already have a row for this epic? EDIT IT — never append a second.** This step is reached
   again whenever the PR is not merged first time: the check reds and you push a fix, the operator
   asks for changes, `merge: false` stops Step 4.5, or the PR is closed and reopened. All of those
   re-enter at Step 0 and walk through here. A second row is indistinguishable from the first,
   because both are number-free. Amend the row and `git commit --amend` the bookkeeping commit.
   (`/smh-close-task-merge-tree` Step 2.5 is idempotent for exactly this reason.)

4. **Commit both on the epic branch, then PUSH — with EXPLICIT paths and the key leading the
   subject:**

```bash
cd "$PROJECT_ROOT" && git add _artifacts/INDEX.md <the active-context path>
cd "$PROJECT_ROOT" && git commit -F <message-file>    # subject: "<JIRA-KEY> chore(ship): ..."
cd "$PROJECT_ROOT" && env -u GITHUB_TOKEN git push origin epic/<JIRA-KEY>-<slug>
```

⛔ **The push is part of this step, not Step 4's job.** Commit without pushing and the branch is
`1 ahead / 0 behind` — which is exactly what `ship_preflight.py` **BLOCKS** on (*"merging an unpushed
branch puts commits on production that exist on one disk"*, exit 2). A session that ends between here
and Step 4 would then be unresumable, halted by a hazard this step created. Step 4's push becomes a
harmless no-op.

⛔ **`<JIRA-KEY>` in the subject is not style — it is what keeps the PR landable.**
`main_write_gate.py --mode pr` validates the key on every **non-merge** commit in the range, reading
the whole message (`%B`), so one unkeyed bookkeeping commit refuses the entire pull request — the
epic included. (Merge commits are exempt by `--no-merges`, which is why Step 2's absorb is safe.)
⛔ **`git commit -F <file>`, never `-m "…"`:** backticks inside a `-m` string are executed by the
shell before git ever sees them. ⛔ **Explicit paths only — never `git add -A`, `.` or `-u`**; this
tree may hold other lanes' work.

## Step 4 — Push the gated tip, open the PR, and STOP
<!-- JIRA-HOOK: the epic's Jira tickets transition to Done at Step 6.5, after the merge is verified. -->

**The tip you push is the tree Step 3 gated, plus Step 3.5's artifacts-only commit** — Step 2
absorbed `origin/main` into it, so the code going to the remote is exactly what went green, and
the one commit added since changes only markdown under `_artifacts/` and the active-context. That
is the same carve-out `/smh-close-task-merge-tree` Step 2.5 makes, for the same reason: an
artifacts-only commit cannot alter what the gate tested. Push it, then open the pull request against
`main`:

```bash
cd "$PROJECT_ROOT" && env -u GITHUB_TOKEN git push origin epic/<JIRA-KEY>-<slug>
```

Then the PR, with the gate's own evidence in the body — the operator decides from what the gate
said, so the numbers travel with the request rather than living in a chat scrollback:

```bash
cd "$PROJECT_ROOT" && gh pr create --base main --head epic/<JIRA-KEY>-<slug> \
   --title "<JIRA-KEY> ship epic/<JIRA-KEY>-<slug>" --body-file <the evidence file>
```

The body carries four lines and nothing else: the backend suite total, the frontend build result,
`E2E GATE: GREEN <n>/<n>` with the report path (`frontend/playwright-report/`), and the epic's
ticket link. **The last line `gh` prints is the PR URL.** Print it and **STOP.**

**No `gh` on this machine?** Nothing is blocked — the tip is pushed, so the PR opens in a browser.
Build the URL from command output, never from memory:

```bash
cd "$PROJECT_ROOT" && git remote get-url origin      # -> the owner/repo
# https://github.com/<owner>/<repo>/compare/main...epic/<JIRA-KEY>-<slug>?expand=1
```

⛔ **STOP means stop.** Do not merge it another way, do not mint a token, do not offer to. **The
operator's decision to proceed is the sign-off — and their invocation this turn IS that decision, in
one of the ruling's three forms — while the click on *Merge pull request* is how it reaches
GitHub.** A link nobody has merged is not a merge running late; it is a merge that has not been
authorised. Waiting is correct behaviour, on every platform, on either machine.

**What guards the merge is on GitHub, not here — and how much guarding there is depends on the
repo.** A project that has filed its own server-side gate ticket publishes a required check, and
GitHub refuses the merge button until it is green. A project that has not yet is guarded by the
local gates this door already ran plus the operator's own reading of the PR. Either way **the token
is structurally absent, not bypassed**: a merge performed on GitHub's servers never touches a
machine here, so there is no local push for a hook to gate (SCC-118's finding, read forwards). If a
required check is present and red, **STOP** — never disable the ruleset to get past it.

> ⓘ **Why this road replaced the local merge (SCC-347).** The old Step 4 checked out `main`, merged
> `--no-ff`, minted a single-use token and pushed. That shape was already retired on the Task door
> (SCC-183) for a reason that applies here identically — a dozen hand-typed git commands in a shared
> checkout, each judged separately by the agent's permission layer, with the state left stranded
> halfway when one was denied. And the token it minted guarded the one road nobody was taking:
> measured 2026-08-31, `Projects/AGY_AVIATIONCHAT` `main` carried **no branch protection and no
> ruleset at all** (`gh api repos/{owner}/{repo}/branches/main/protection` → 404 *Branch not
> protected*), so a merge made through the GitHub UI — what a web or mobile session does — was
> guarded by nothing, while the local hook diligently guarded a push that had stopped happening.
> The PR road puts the operator's click where the authorisation belongs and leaves the server-side
> check as each project's own ticket to file.
>
> ⭐ **That 404 was closed LATER THE SAME DAY, and this paragraph is history, not current state.**
> AVCH-111 armed AviationChat's ruleset on 2026-08-31 (id `21963341`, required check
> `main-write-gate`, strict, zero bypass actors); the lobby's has been active since SCC-118. So a
> green-checked PR is now the only road to `main` on both, which is exactly why Step 3.5 exists.
> Read the two dates together: the 404 is what the PR road was built to fix, not what is true now.

## Step 4.5 — Resuming after the operator's click: `--after-merge <JIRA-KEY>`

When Step 4 handed back a link, this command is **paused, not finished**. Once the operator has
merged, re-invoke it to run everything below and nothing above:

```bash
/cicd-push-e2e --after-merge <JIRA-KEY>
```

**Run Step 0 to bind `PROJECT_ROOT`, then everything below and nothing else.** Step 0 is the only
place that binding happens and every command in this half is `cd "$PROJECT_ROOT" && …`; skipped, an
unbound variable makes `cd "" && git …` a silent no-op in the lobby and the whole resume half runs
against the wrong repo.

⛔ **THE KEY DOES NOT CARRY THE SLUG, AND EVERY COMMAND BELOW NEEDS THE FULL REF.** You were
re-invoked with a bare `<JIRA-KEY>` — often days later, plausibly on the other machine, with none of
Step 1 in context. Resolve the branch from the key rather than guessing at it: a wrong slug makes
the ancestor check below fail on a ref that does not exist, and its `|| STOP` reports a real, merged
landing as *"NOT merged yet"*.

```bash
BRANCH=$(cd "$PROJECT_ROOT" && git branch -a --list "*epic/<JIRA-KEY>-*" \
         | head -1 | sed 's|^[* ]*||; s|^remotes/[^/]*/||')
echo "Resuming: $BRANCH"          # empty -> the branch is already pruned; STOP and ask
```

⛔ **FETCH BOTH REPOS FIRST — `origin/main` is a LOCAL ref in each, and the merge you are resuming
from happened on a remote.** Until they are updated, each still names the pre-merge tip:

```bash
cd "$PROJECT_ROOT" && env -u GITHUB_TOKEN git fetch origin main   # the project — for the merge proof
env -u GITHUB_TOKEN git fetch origin main                         # the LOBBY — for the check below
```

⛔ **AND CHECK THAT THE DOOR YOU ARE READING IS THE CURRENT ONE.** This resume half runs after a
merge that may have changed this very file:

```bash
BEHIND=$(git rev-list --count HEAD..origin/main)                  # the LOBBY, deliberately
```

If `BEHIND` is not `0`, the text you are following may be the pre-merge copy — read the current one
(`git show origin/main:.agents/commands/cicd-push-e2e.md`) and follow that.

⛔ **That check reads the LOBBY, not `PROJECT_ROOT`, and the distinction is the whole point.** This
door FILE lives in the command centre; a thin project has no `.agents/commands/` at all (its
`.agents/INDEX.md` lists that directory among the ones deleted at conversion). Pointed at the
project, the check measures a repo whose ahead/behind says nothing about this file, and its own
remedy — `git show origin/main:.agents/commands/…` — fails there with *path does not exist*. The
sibling this was modelled on gets it right for free, because on the Task door `$REPO` **is** the
lobby. ⓘ And it is worth nothing without the fetch above it, which is where it sat until this
review: unfetched, `HEAD..origin/main` is empty for exactly the epic that just changed this file, so
the guard reported `0` and the agent followed the copy it was warning about.

Verify the merge with **plain git** — no `gh` required, so this half works on any machine:

```bash
cd "$PROJECT_ROOT" && git merge-base --is-ancestor "$BRANCH" origin/main \
  || { echo "NOT merged yet — STOP"; exit 1; }
cd "$PROJECT_ROOT" && git log -1 --format=%s origin/main        # -> "Merge pull request #N from ..."
cd "$PROJECT_ROOT" && git checkout main
cd "$PROJECT_ROOT" && env -u GITHUB_TOKEN git pull --ff-only origin main
```

The PR number comes off that merge subject; the merge sha is `git rev-parse --short origin/main`.
Both go in Step 6.5's record.

⛔ If the ancestor check fails, **STOP** — nothing below runs, no ticket moves, no branch is pruned.
A close-out that reports `Done` on an unmerged PR is the same lie as one that reports it on a failed
merge.

⛔ **It is also why this door needs squash and rebase merges DISABLED on the repo — and why you
verify that at Step 4, before you hand over the link, rather than discovering it here.** Either
setting rewrites the commit, so the branch tip is not an ancestor of `main`, and a landing that
actually succeeded reads back as *"NOT merged yet"*: the deploy is live, the ticket stays open, the
branch stays unpruned, and the ceremony stalls on a ship that worked. The same measurement that
motivated this whole road — a project `main` with no protection and no ruleset — says these
settings are unmanaged too, so do not assume them:

```bash
cd "$PROJECT_ROOT" && gh api repos/{owner}/{repo} \
  --jq '{squash: .allow_squash_merge, rebase: .allow_rebase_merge, merge: .allow_merge_commit}'
```

`squash` or `rebase` true → say so when you hand over the link, and tell the operator to use
*Create a merge commit*. `merge` false is a **STOP**: the button this door depends on is disabled.

## Step 5 — Watch the deploy + verify live
The merge just fired the deploy workflows:
```bash
gh run list --limit 5                 # watch to completion — all must conclude success
```
Then verify live: backend `/health` (expect 200), the production frontend URL, and on Cloud Run
confirm the serving revision via the RELEASE track (other fields lie about what's serving). A failed
deploy is an incident: fix forward on a `chore/*` branch or roll back the revision — decide with the
operator, immediately.

## Step 5.5 — Reconcile the PRD against what actually shipped (SCC-357)

**This is the only moment the comparison is possible.** Until now the epic was a plan; now it is a
merge. The PRD says what was **wanted**; `docs/project_overview_guide.md` — kept current story by
story at `/cicd-update-sprint-memory` Step 3.5 — says what was **built**. ⛔ **The PRD is never
rewritten from the guide** (operator ruling, 2026-08-31): that would turn a requirements document
into a second, more expensive copy of the guide. What happens here is a **reconcile**, and it has
exactly three legal outcomes, each with its own recorded line.

**The guide's delta across this epic is the index into the PRD** — it is small precisely because
the stories kept it current, which is why this step costs minutes instead of a re-read of a
100 KB PRD:

```bash
cd "$PROJECT_ROOT" && git diff <merge-sha>^1..<merge-sha> -- docs/project_overview_guide.md
```

- ⛔ **No guide in this project yet** → there was nothing to index the PRD with, and saying the epic
  shipped as specified would certify a comparison that structurally could not happen. Record
  `PRD: not reconciled - <project> has no overview guide yet` in the Step 6.5 ticket comment and
  move on. (Live state for
  AviationChat until its own guide ticket lands, so this is the common branch today, not an edge.)
- **Empty delta, guide present** → the epic shipped as specified. Record it in the Step 6.5 ticket
  comment, exactly: `PRD: unchanged - epic shipped as specified (guide delta empty)`.

  > ⓘ **Why the ticket and not the ledger row (SCC-358).** The ledger row is written at Step 3.5,
  > before the PR opens. This reconcile diffs `<merge-sha>^1..<merge-sha>`, so it cannot exist until
  > the merge does — it is the one thing in this ceremony that genuinely cannot ride the PR. The
  > ticket comment is therefore its only durable home, and it is where the PR number and merge SHA
  > already land.
- **Non-empty** → open **only** the PRD sections this epic's requirements map to
  — the epics ledger in the project's BMAD planning artifacts carries the story-to-requirement
  join, so let it name the sections; never open the whole PRD.
  Compare each against the guide's delta.
  - **No divergence** — the guide gained detail the PRD never claimed either way → record the same
    `PRD: unchanged` line, naming what you compared.
  - **A real divergence** — the PRD states X and the system does Y → that is a **requirements
    change**, and requirements changes are work. Open `chore/<PROJECT-KEY>-<slug>-prd-reconcile`
    and run **`/bmad-correct-course`** on it: it produces the sprint-change-proposal and edits the
    PRD and, where the invariant moved, the architecture folder. That lane lands through this same
    PR door. **Record it in the Step 6.5 ticket comment, exactly:**
    `PRD: reconciled - divergence routed to /bmad-correct-course on <the lane>`.

⛔ **All three branches produce a verbatim `PRD:` line, and that is not decoration.** Step 6.5's
ticket comment carries `<the Step 5.5 PRD line, verbatim>` unconditionally, so a branch with no
defined line leaves an agent holding a mandatory slot and nothing to put in it — which it fills by
inventing one. A fabricated reconcile record on a shipped epic is worse than no record.

⛔ **Never edit the PRD in place on `main`.** You are standing on `main` at this point in the
ceremony, and a requirements edit is not a side effect of a deploy — it is reviewable work that
takes its own lane, its own gate and its own pull request, like everything else here.

ⓘ **Why the epic and not the story.** A story is too small to tell a requirements change from an
implementation detail — mid-epic discovery already has a door (`/bmad-correct-course`, run the
moment a story finds the requirement wrong). The epic is the unit that was *specified*, so it is
the unit that can be *checked against its specification*. And it is bounded: one reconcile per
ship, indexed by a diff the stories already paid for.

## Step 6 — Prune the epic branch, and commit NOTHING
The epic shipped; its branch is done:
```bash
cd "$PROJECT_ROOT" && git branch -d epic/<JIRA-KEY>-<slug>
cd "$PROJECT_ROOT" && env -u GITHUB_TOKEN git push origin --delete epic/<JIRA-KEY>-<slug>
cd "$PROJECT_ROOT" && git rev-list --left-right --count main...origin/main    # must be 0 0
```
Finish standing on `main`, clean, `0 0` — state it per repo touched.

**First, confirm the bookkeeping actually landed** — instrument it, do not leave it to notice:

```bash
cd "$PROJECT_ROOT" && git log origin/main -1 --format=%h --grep="<JIRA-KEY>" -- _artifacts/
```

Empty means Step 3.5 never ran for this epic — reachable whenever the PR was opened by an older copy
of this door. **Do not fix it here.** Open `chore/<JIRA-KEY>-bookkeeping` and send it through this same PR
door; that is the one sanctioned route, and it is named here so you do not have to invent it.

⛔ **DO NOT COMMIT ANYTHING HERE — never run `git commit` while standing on `main`. This step used
to say the opposite, and that instruction is the whole of SCC-175 and SCC-358.** Every write it used
to make now happens at **Step 3.5**, on the epic branch, before the PR opens. A commit made here is a
direct push into a branch guarded by a required check, and the gate refuses it.

SCC-175 was the same bug on the Task door: it produced a non-merge commit on `main`, the write gate
correctly refused it, and the refusal banner's `reset --hard` remedy then destroyed three other
sessions' uncommitted work (SCC-180). SCC-358 is this door being the last one to learn it — found
when an epic's bookkeeping was stranded behind an armed ruleset and needed a separate operator
approval plus a hand-built `--no-ff` merge to land.

If you reach this step and find something genuinely unrecorded, it does **not** get a commit on
`main`: it goes on a `chore/*` branch through this same PR door, like every other change.

## Step 6.5 — Move the epic's Jira ticket
Skip if Step 1 found no key (pre-Jira epic, or a repo with no `.agents/jira.conf`). Otherwise the
merge IS the epic shipping, and the operator's invocation of this command IS the sign-off — record it:
```bash
acli jira workitem comment create --key <JIRA-KEY> \
  --body "Merged to main via PR #<N> at <merge-sha>. Gate: pytest + build + /cicd-e2e green (<evidence-link>). Deploy verified live. <the Step 5.5 PRD line, verbatim>"
acli jira workitem transition --key <JIRA-KEY> --status "Done" --yes
```
(`comment create` needs `--key`; `transition` too — `view` is the only one that takes the key
positionally. **`--yes` is not optional**: without it acli stops on an interactive confirm no
agent shell can answer, and this line shipped without it until SCC-113.) Full acli reference:
`.agents/rules/jira.md`. Transition the EPIC ticket only — child stories were already moved one-by-one at their
close-outs by `/cicd-close-story-merge-tree`. If Step 1's sanity check was honest, they are all `Done`
before this runs; if the transition fails because children are open, that is the sanity check telling
you it was skipped — go run the close-outs, do not force the epic.

Sprint/backlog placement stays the operator's — this step changes STATUS and posts evidence, nothing
else.

Optional additional input (project · epic branch · `--after-merge <JIRA-KEY>`): $ARGUMENTS
