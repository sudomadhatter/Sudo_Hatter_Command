---
name: git-policy
description: "Git policy: main is the ONLY long-lived branch. Each epic gets a short-lived `epic/<JIRA-KEY>-epic-<N>-<slug>` branch off main (BOTH numbers: ticket AND sprint); story/dev work happens in its own git worktree on a `claude/*` branch off the epic branch, where the agent commits FREELY (explicit paths — never `git add -A`). The story lands on its epic branch on Mr. Hatter's in-the-moment 'approved' or via /cicd-close-story-merge-tree. The epic reaches `main` only through /cicd-push-e2e — full gate + E2E green + Mr. Hatter's sign-off."
trigger: model_decision
# Protocol tier (rules/INDEX.md): conditional, not floor. Every gate it carries is ALSO
# stated inline in AGENTS.md and constitution.md, so the stop binds even in a session
# that never opens this file — which is what makes it safe to leave conditional rather
# than load ~44 KB of protocol prose into every read-only session.

---

# Git Policy

> The single, canonical git rule for the whole workspace. **Agents commit and push their own work now.**
> This supersedes the old "never run git yourself — hand Mr. Hatter the command" default, which is gone:
> that default is what produced commits carrying four unrelated sessions at once.

## Branch model — epic branches → `main` (THE dev standard)

> The one source of truth for the branch model. Every workspace (home base + every project) uses it;
> per-workspace `AGENTS.md` GATES sections point here rather than restating it.
>
> **History note:** the previous standard (`main_debug` as a long-lived integration branch) was
> retired 2026-08-07 — every repo's `main_debug` was fast-forwarded into `main` and deleted. If a
> doc, memory, or artifact still says `main_debug`, it predates that migration; the artifact stays
> as history, but the procedure it describes is dead.

- **`main` is LIVE PRODUCTION and the ONLY long-lived branch — never work on it directly, never
  auto-target it, never branch a worktree straight from it for story work.** It stays deployable;
  on projects with CI/CD, a push to `main` IS a deploy.
- **Each epic gets one short-lived branch: `epic/<JIRA-KEY>-epic-<N>-<slug>`, cut from `main`** at
  epic kickoff (`/cicd-create-epic-sprint`). All of the epic's stories integrate there. This is the
  "one place to send everything" — scoped to the epic, not eternal.

  ⭐ **The name carries BOTH numbers, because they are different numbers and they do not track
  each other.** `<JIRA-KEY>` is the epic's **ticket** (`AVCH-18`); `epic-<N>` is its **sprint /
  BMAD epic number** (`epic-19`) — the one the board key, `sprint-status.yaml`, `epics.md` and
  `_artifacts/epic_<N>/` are all filed under. A branch naming only one of them forces every reader
  to hold the mapping in their head, and the two are close enough to look like a typo of each other:
  `epic/AVCH-18-…` sitting under artifacts filed at `epic_19/` reads as drift on every glance.

  ```text
  epic/AVCH-18-epic-19-adk-2x-runtime
       └ ticket  └ sprint  └ slug
  ```

  ⛔ **The `epic/` prefix is load-bearing — the sprint number goes in the SLUG, never in front of
  it.** Every `$EPIC` resolution in this system globs `epic/*` (`git branch --list 'epic/*'`,
  `for-each-ref 'refs/remotes/origin/epic/*'`), and `merge-target-guard.sh` classifies branches with
  a `case` arm that is literally `epic/*)`. A branch named `epic-19/AVCH-18-…` matches **none** of
  them: every resolution falls back to `origin/main` — the stale-ref defect SCC-165 swept out of this
  family — and the **armed** merge-target guard classifies it `unknown`. Measured 2026-08-24 while
  renaming Epic 19's branch: **147 references across 38 files**, including three git hooks,
  `main_write_gate.py`, `closeout_preflight.py`, `ship_preflight.py` and six test files. Keeping the
  prefix costs nothing and buys both numbers.
- **Story work happens in a worktree on a `claude/<JIRA-KEY>-<slug>` branch cut from the epic
  branch**, and lands back on the epic branch at close-out (see "The landing").
- **Ad-hoc work outside any epic** — quick fixes, toolkit/system maintenance — takes a short-lived
  `chore/<JIRA-KEY>-<slug>` branch off `origin/main`, **in its own worktree**, closed out through its
  door — `/smh-close-task-merge-tree` (a pull request the operator merges) or, when the diff reaches a
  deployable path, `/cicd-push-e2e`; **invoking the door IS the sign-off** (see the write gate below,
  and SCC-211 for which diff selects which). The gate is per-repo: the lobby runs
  `python3 .agents/scripts/tests/run_all.py` (it has **no E2E suite and never will** — no
  `frontend/`); deploying repos run the light gate (tests + build), and epic merges add `/cicd-e2e`.
  **Neither door decides the gate from prose, and neither is chosen — the DIFF selects it.**
  `task_preflight.py` derives the lane from the repo and the diff, and a `chore/*` branch that
  touches `backend/`, `frontend/`, `firebase/`, `functions/`, `mobile/` or `.github/` is refused
  outright and handed to `/cicd-push-e2e` (SCC-49, SCC-211) — a change that reaches deployable code
  is a product change no matter what its ticket is called. `ship_preflight.py` refuses the mirror
  case from the other side, so a lane cannot slip through both.

### Every branch and every commit carries a Jira key (armed 2026-08-07)

- **The key goes immediately after the prefix**: `chore/SCC-11-acli-wrapper`, never
  `chore/fix-SCC-11`. Atlassian's GitHub app joins on the key as a literal string and reads the
  **branch name** too — a correctly-named branch links every commit on it, including one whose
  message forgot the key.
- **The key must match the repo.** Each repo declares its project in `.agents/jira.conf`:
  `SCC` = the lobby, `AVCH` = AviationChat. An `SCC` key inside AviationChat is **rejected** — that
  is the guardrail working, not friction to route around.
- **`commit-msg` is in ENFORCE mode** (`.agents/scripts/git-hooks/JIRA-ENFORCE`, tracked). A commit
  with no valid key for that repo is refused outright. Merge/revert/fixup/squash messages and
  in-progress rebases are exempt. Bypass once with `--no-verify`; disarm by deleting the flag.
- **A rejected commit is a no-op** — the staged set is untouched, nothing to undo.
- **Operating the board itself** (reading tickets, JQL, transitions, minting) is its own rule:
  `.agents/rules/jira.md` — the `acli` cheat-sheet, flag traps, and the ticket↔file join. The board
  is reachable from any shell-capable agent; no MCP or per-platform config exists or is needed.
- **The epic reaches `main` exactly one way: `/cicd-push-e2e`** — the full gate (backend suite +
  frontend build + `/cicd-e2e` GREEN) plus Mr. Hatter's explicit sign-off, then **a pull request he
  merges**. The command opens the PR and stops; it never merges, and an agent never merges to
  `main` on its own initiative. Re-invoked as `--after-merge <KEY>` it verifies the landing with
  plain git and finishes the ceremony. The epic branch is deleted then: branches are short-lived by
  design; nothing accumulates.

## The write gate — keyed on WHERE a write lands, not on the act

| Destination | Permission |
|---|---|
| Your own `claude/*` story branch (commits **and** pushes) | **FREE** — no approval, loops/retries fine |
| The epic branch (`epic/*`) — a story landing | **Mr. Hatter's sign-off** — his in-the-moment "approved", or invoking `/cicd-close-story-merge-tree` (which IS the sign-off) |
| A `chore/*` branch (commits and pushes) | **FREE** — the merge back to `main` is what's gated |
| `main` | **A pull request the operator merges — in every repo (SCC-347).** In this repo the door is `/smh-close-task-merge-tree`; in project repos it is `/cicd-push-e2e`, shipping the epic, or a `chore/*` whose diff **reaches a deployable path** (`ship_preflight.py` derives which; a project `chore/*` touching nothing deployable takes the Task door instead). See below. Never on an agent's own initiative. |

Approval for an epic-branch landing is **per-action and never carries forward**. One "approved"
lands one story; the next needs its own.

### ⭐ The road to `main` — a pull request, and the operator's click (SCC-183, 2026-08-16)

**In this repo there is ONE road**, and no agent on any platform can travel it alone:

| Step | Who | What |
|---|---|---|
| open the PR | the agent, inside `/smh-close-task-merge-tree` or `/smh-merge-multiple-workingtrees` here, or `/cicd-push-e2e` in a project | `gh pr create --base main --head <branch> --fill` (the project door passes `--title` + `--body-file` instead, to carry its gate evidence) — or, with no `gh`, print the `compare/main...<branch>` URL. Then **STOP**. ⛔ Never a bare `gh pr create`: with neither `--fill` nor a title it prompts, and an agent shell has no TTY to answer |
| the gate | GitHub | **`main-write-gate`** must be green: the full enforcement suite plus a check that the source is `epic/*` or `chore/*` with a real ticket key |
| the merge | GitHub, on the operator's decision | the operator clicks *Merge pull request*. **Their decision to proceed is the sign-off**; the click is how it reaches GitHub, never work they owe |
| after | the agent, on re-invocation | `--after-merge <KEY>` — verify with `git merge-base --is-ancestor`, then Dev Record, ticket, prune |

⭐ **Since SCC-347 project repos take this road too.** `/cicd-push-e2e` gates the epic locally,
pushes the gated tip, opens the PR and stops; the operator's click merges it. What a project repo
may still lack is the **server-side** half — `main-write-gate` is published only once that project
files its own ticket in its own tracker (AVCH-111 for AviationChat), so the door deliberately does
**not** wait for a check that may never appear. Until a project has it, its PR is guarded by the
local gate this door ran plus the operator's reading of it — which is strictly more than the merge
had before, when the GitHub-side road was measured to have no protection and no ruleset at all.

⛔ **Why no token on this road, and why that is not a bypass.** The token proves *the operator said
yes* before **a machine here** pushes to `main`; it lives in `.git/` and is spent by
`.githooks/pre-push`. A merge performed on GitHub runs on GitHub's servers and **never touches a
machine here**, so there is no push for a local hook to gate — the token is *structurally absent*,
not evaded (SCC-118's own finding, read forwards; it is why `main-write-gate` was built server-side
in the first place). The click is the intent half, `main-write-gate` is the fitness half. Both
present, both required.

⭐ **The sign-off is the operator's DECISION TO PROCEED, and it is given in exactly one of three
ways: the word `approved`, or invoking `/smh-close-task-merge-tree`, or invoking
`/cicd-push-e2e`** (operator ruling, 2026-08-17). **From that word on, every step is the
ceremony's and the agent runs it** — the click, the `--after-merge` half, the Dev Record, the
transitions, the prune. The **decision to proceed is the sign-off**; the click on *Merge pull
request* is **how that decision reaches GitHub**, not a task the operator owes. So the merge is
never an item in `## Your Actions`, and never an open box.

⭐ **And the click is a STRONGER constraint on the agent than a sentence in a file.** A *document*
saying the sign-off happened sits in an agent's context and still
reads as valid on task six — which is precisely how one invocation rode six merges (SCC-71), and how
"you can move it to done" was read as merge permission (SCC-37). A click cannot be inferred from
context, stretched from an earlier turn, or performed by an agent that was never given the ability.

⛔ **Why the ceremony went, rather than growing another gate.** SCC-184 — docs only, every gate
green, suite 32/32 — could not reach `main` in a full session. The block was never a gate: it was
~15 hand-typed `git`/`gh` strings in the shared checkout, each judged separately by the agent's
permission layer, several denied, state stranded mid-ceremony. Measured, controlled pair, same op
and same target: `git merge X --no-ff` **allowed**, `git -C <path> merge X --no-ff` **denied** — and
the `-C` form was the one
[the merge-target rule](#-pin-the-merge-target-not-just-the-source--pin-every-call-and-assert-before-you-merge)
below mandated at the time (the pin idiom is now `cd "$REPO" && git …`, which both permission layers match per piece — SCC-351). **Obeying the safety law guaranteed the permission miss.** No gate could fix a
failure of shape, and adding a second road would have made the system bigger. So the local ceremony
was **deleted from the smh doors** instead.

⛔ **No agent merges to `main` in this repo. There is no eligibility test, no "small enough" class,
no self-merge.** An earlier cut of SCC-183 proposed one and it was withdrawn under three operator
constraints — it needed a per-machine allow-list edit (`.claude/settings.local.json` is gitignored,
so it would arm one machine), it changed the agent's own permission rules, and it worked for one
platform out of four. **Any future proposal to let an agent merge must clear all three.**

⛔ **No command may change which branch a checkout is on.** No `git checkout main`, no `switch`, in
any smh door. The operator works in those checkouts and leaves them wherever they like. Everything
here reads `origin/main` — a remote-tracking ref, true regardless of what any tree has checked out.

**Enforcement — two layers, and only the first one counts.**

1. ⭐ **`.githooks/pre-push` (SCC-77) — this is the gate.** It refuses any push landing on `main`
   without a single-use approval token, and spends the token on the way through. The two `main`
   doors mint it at their sign-off step (`.agents/scripts/git-hooks/mint-push-token.sh`), after the
   merge commit exists and immediately before the push. The token lives in the **common** git dir,
   so every worktree on the machine shares exactly one; it records the sha it was minted for, so
   anything committed after the sign-off is refused.

   ⛔ **And since SCC-37 the token carries APPROVAL EVIDENCE — the operator's verbatim words.**
   The recurrence the first cut missed: an agent reading standing context as consent ("you can
   move it to done" taken as a merge sign-off — ticket permission is never merge permission). The
   mint now refuses in any non-interactive shell without `--operator-approval '<their exact,
   this-turn words>'`; at a terminal the operator types the ticket key instead. The quote is
   recorded in the token, printed at mint, and printed again by the push gate — an inference
   stretched into an authorization has to survive being read back at every step. A token with no
   approval record is refused and consumed at the push.

   ⭐ **And it enforces ONE MERGE, which is the part that actually implements SCC-71.** A token
   authorises a *push*; what needs authorising is a *merge*. So `main` must advance by **exactly one
   merge commit sitting directly on the remote's current tip**, and that merge's second parent must
   be the branch the token names. Without this, merging six branches locally and then minting once
   lands all six on one approval — reproduced during SCC-77's own review. The same invariant refuses
   a force-push rewind, which is the destructive twin of the delete that was already refused.
   The minter refuses a stacked batch too, so it fails where the message can still name the fix.

   Armed by the tracked
   `.agents/scripts/git-hooks/MAIN-PUSH-ENFORCE`; bypass once with `git push --no-verify`.
   Pure POSIX `sh` **on purpose** — see below.

   ⛔ **A fresh clone ships this gate OFF**, and so does every other hook here — `core.hooksPath` is
   per-machine config that git never carries, so on a new checkout `.githooks/` is simply not
   consulted. **First command on any new clone:**

   ```bash
   python3 docs/migrations/scripts/arm_hooks_include.py .    # PC: python
   ```

   ⛔ NOT `git config core.hooksPath .githooks`. That writes the key into `.git/config`, and Claude Code's worktree setup parses that file, resolves the relative value to an ABSOLUTE one and writes it back to the SHARED config — after which every worktree runs the MAIN checkout's hooks instead of its own, so a lane's gates are not the gates being enforced on it. The installer puts the value in an INCLUDED file that git follows and a plain ini reader does not (SCC-323).

   It is **loudly** off rather than silently off: `run_all.py` asserts `core.hooksPath` is set *and*
   relative, so the enforcement suite stays RED until you arm it.

2. `require-push-approval.py` **PreToolUse hook** (canonical source `.agents/hooks/`, deployed to
   every `.claude/hooks/`) — prompts earlier and reads better, but it is Claude-only and nothing
   depends on it. `merge_pull_request` (+ GitHub write tools) is gated in `.claude/settings.json`.
   It only ever sees the **agent's** Bash tool; the operator's own terminal is never affected.

⛔ **Why layer 1 refuses to depend on an interpreter.** Layer 2 was, for weeks, the *entire* claimed
enforcement — and it had never executed once. `.claude/settings.json` invoked it as
`powershell -NoProfile -Command "python ..."` and the Mac has **neither** binary (only `pwsh` and
`python3`), so it exited 127 in silence on every push, as did all four SessionStart hooks. Six
merges reached `main` on one sign-off (SCC-64 → SCC-69, 2026-08-09) with nothing in the way. A git
hook is the only layer both machines, all four agent platforms, and the operator's own terminal
share — so the gate is `sh`, with no interpreter probe and no Python anywhere in its path.

3. ⭐ **The `main-write-gate` check on GitHub (SCC-118) — the half that is not on a machine.**
   Layers 1 and 2 both live on a computer and run at `git push`. A merge performed on GitHub's
   servers — the web **Merge pull request** button, or the REST API — never touches a computer, so
   those layers are not bypassed there: they are **absent**. PR #2 (`dabb3c3`, 2026-08-12) landed on
   `main` exactly that way, from a Claude Code web session, with nothing structurally able to look
   at it.

   A ruleset on `main` now requires a green check named `main-write-gate`
   (`.github/workflows/main-write-gate.yml`): the real enforcement suite, the toolkit lint, and
   `.agents/scripts/main_write_gate.py` — which checks the merge came from an `epic/*` or `chore/*`
   branch carrying a key this repo answers to, and, for a pre-flighted local merge, that `main`
   advances by exactly one merge commit of a real pushed branch. The **bypass list is empty on
   purpose** and must stay that way.

   ⛔ **This is NOT a copy of layer 1, and describing it as one is the mistake to avoid.** Layer 1
   enforces **authorisation** — one sign-off buys one merge — via a token under `.git/` that by
   design never leaves the machine. That half **cannot** cross to a server, and identity cannot
   stand in for it: the agent that merged PR #2 did so as `sudomadhatter (User)`, the operator's own
   account. There is no *who* to restrict, which is why the server-side lever had to be a status
   check. Layer 3 enforces **fitness**, not permission. Neither half covers the other's ground.

   Because a required check refuses a commit that carries no check, and a merge commit made locally
   has never been to GitHub, `/smh-close-task-merge-tree` pre-flights: it pushes that exact commit
   to a throwaway `gate/main-<sha>` ref, waits for the check, and only then mints the token and
   pushes `main` (checks attach to a commit, so the green travels with it). **Mint after the wait,
   never before** — the token's TTL is 30 minutes and a slow run would eat it.

   ⚠ **Scope: the CHECK is this repo only, today — the PR road is everywhere (SCC-347).**
   `/cicd-push-e2e` ships `epic/*` branches in *project* repos through a pull request as well, but
   those repos publish no such check, so it does not wait for one — a wait there would poll
   forever. Giving a project the server-side half is its own ticket in its own tracker.
   Break-glass if CI is down and `main` must move:
   `gh api -X PUT repos/{owner}/{repo}/rulesets/{id} -f enforcement=disabled` — the server-side twin
   of deleting `MAIN-PUSH-ENFORCE`.

**What this buys, and what it does not.** An agent can write files, so an agent can write a token.
This is not a security boundary against a determined agent and must not be described as one. It
converts a silent violation into a deliberate, traceable one, and it closes the drift failure this
rule keeps losing to — a close-out command whose body stays in context and still reads exactly as
valid on task six as on task one. Merges via `gh pr merge` or the GitHub web UI never reach a local
hook at all — the gap tracked under epic SCC-75, closed **for this repo** by SCC-118's layer 3
above. SCC-347 narrowed what remains open elsewhere: every repo now lands through a PR the
operator merges, so what a project still owes is the server-side CHECK on that PR, not a road.

## A commit is not done until it is pushed

**`git commit` and `git push` are ONE action. Never end a turn, a step, or a command with a commit sitting
unpushed.** An unpushed commit is invisible to every other machine and to the operator, who then has to
discover and push it by hand — which is exactly the manual sync this toolkit exists to remove.

This applies to **every repo you touched**, not just the one the work started in. A `/smh-sync-agents` run
writes to the lobby *and* each maintained project, so a change to one master file dirties three repos;
committing the one you were thinking about and leaving the other two is the common form of this failure.
Sync also runs *after* commits sometimes — re-check `git status` at the end and commit-and-push whatever
the sync just wrote.

**Close every piece of work with this, per repo touched:**

```bash
git status --short                                   # must be empty
git rev-list --left-right --count <branch>...origin/<branch>   # must be "0 0"
```

`0 0` + clean, in **every** repo, or the work is not finished. State the result per repo — an unverified
"pushed" is how this hides.

⛔ The only exception is a story branch mid-flight, which is governed by "The landing" below: its commits
stay local until the landing pushes `HEAD:epic/<JIRA-KEY>-<slug>`. That is about *which ref* receives the push, never
a licence to leave work uncommitted or a landing unpushed.

## The landing — one story, one clean push

The story lands on its **epic branch** at close-out (`/cicd-close-story-merge-tree` Step 3) or on
Mr. Hatter's in-the-moment "approved". It merges **from inside the worktree**, never by checking out the
epic branch in the shared checkout:

```bash
git fetch origin epic/<JIRA-KEY>-<slug>
git merge origin/epic/<JIRA-KEY>-<slug>        # absorb it INSIDE the worktree — conflicts surface here, isolated
git push origin HEAD:epic/<JIRA-KEY>-<slug>    # THE landing
```

⛔ **Do NOT push the story branch itself.** The **local** branch is the rollback point, and it survives
a failed landing push completely untouched. Pushing story branches on every landing is what left 10
stale `claude/*` on origin by 2026-07-27.

**A story branch reaches origin exactly one way: `/cicd-park`.** That is the entire point of park —
*"the ONLY thing that makes the work portable"* — and `/cicd-resume` reads `git ls-remote --heads origin
'refs/heads/claude/*'` to find in-flight work. The epic branch, by contrast, LIVES on origin — park
pushes it too, and resume checks it out on the new machine.

**The invariant this buys: a `claude/*` branch on origin means "parked, in-flight, on another machine."**
Nothing else. Keep it true — it is what makes `/cicd-resume` trustworthy on a cold machine.
(`claude/incident-*` branches come from the Epic-16 incident pipeline, not story flow; they are outside
this rule and must not be swept by it — they match the `claude/*` glob, so a resume reading that listing
must skip the `incident-` infix rather than treat it as parked story work.)

Checking out the epic branch in the shared checkout to merge is **wrong** — the shared checkout stands
on `main` and stays there; pulling story landings through it drags other teams' uncommitted work into
your merge. If the landing merge conflicts, it conflicts in the isolated worktree: **STOP and report**,
never force-push, never blind-rebase.

**Board files live on the epic branch too.** `sprint-status.yaml`, `active-context.md`, and story
files are edited in the story worktree (or on the epic branch directly at close-out) — never in the
shared `main` checkout, which only advances when the epic merges. This is what makes the shared
checkout boring: it is always exactly production.

## Safe-commit mechanics (always — inside the worktree too)

- **Commit your OWN work via explicit paths:** `git add path/one path/two …`.
- **NEVER `git add -A`, `git add .`, or `git add -u`** — they sweep other parallel work (other
  agents/teams, or Mr. Hatter's own uncommitted changes) into your commit. This is the most important rule,
  and the worktree does not repeal it.
- **Verify the staged set first:** `git diff --cached --stat` must show ONLY your files. If anything
  else appears, unstage it (`git restore --staged <path>`) before committing.
- **Scope the commit message** to your task/story only, and **lead the subject with the repo's Jira
  key** (`SCC-11 fix(sync): …`). The `commit-msg` hook rejects a subject without one.
- ⛔ **Backticks in `-m "…"` EXECUTE.** The shell expands `` `…` `` inside double quotes before git ever
  sees the message, so a subject that quotes a command name runs it. Use `git commit -F <file>` (or a
  single-quoted `-m`) whenever the message contains a backtick. Recorded house incident —
  `_artifacts/_memory/commit-message-backticks-execute.md`.
- **Hook output is invisible in VS Code's Source Control panel** — it goes to `View → Output → Git`.
  A commit made from the panel that a hook merely *warns* about looks like a clean success. This is
  how a wrong-key commit reached AviationChat's `main` on 2026-08-07, and it is why the gate is
  armed rather than warning.
- **If a push is rejected** (remote moved under you), **STOP and report.** Do not force-push, and do
  not blind-rebase while other uncommitted work sits in the tree.

### ⛔ Pin the merge TARGET, not just the source — pin every call, and assert before you merge

Every guard above protects the branch you are merging **from**. Nothing protects the branch you are
merging **onto**, and on 2026-08-11 that gap put a production merge commit on a sibling lane's
branch: `cd <worktree> && git checkout main` ran in one step, and a **bare** `git merge <lane>` ran
in a later one, by which point the working directory had reset to the shared checkout — which was
standing on `chore/SCC-89-…`. It reported success. The output, the changed-file list and the commit
message (`-> main`, because that is what was typed) were all indistinguishable from a correct merge.

- **A `cd` in an EARLIER call is not a lock.** The pin lives in the SAME compound line —
  `cd "$REPO" && git <verb> …` — never a bare `git` that trusts where a previous step left you.
  (The old `git -C` spelling is auto-denied by Zoo Code and banned in doors — `command-shape.md`.)
- **Assert the target immediately before merging**, and let it stop you:

  ```bash
  test "$(cd "$REPO" && git rev-parse --abbrev-ref HEAD)" = "main" || { echo "NOT ON main — STOP"; exit 1; }
  ```

- **On the two `main` lanes this assertion is already mechanical (SCC-77).**
  `mint-push-token.sh` **refuses to mint unless `HEAD` is `main`**, and it is called between the
  merge and the push — so a token cannot be minted from a sibling lane, and a merge that landed on
  the wrong branch cannot produce one. That covers `/cicd-push-e2e` and
  `/smh-close-task-merge-tree`. It does **not** cover a bare `git merge` typed by hand, which is why
  the assertion above stays the rule rather than the fallback.

- **Recovery, if it happens anyway — do not reset and do not force.** The merge commit is usually
  correct in every way except which pointer moved. Verify its tree carries nothing from the wrong
  branch (`git diff --name-only <main-tip> <sha>`), confirm its first parent is `main`'s tip
  (`git log -1 --format='%p' <sha>`), then `git merge --ff-only <sha>` from the tree that holds
  `main`. The sibling branch keeps its uncommitted work untouched.

- ⛔⛔ **And when a rewind genuinely is the answer, it is `--keep` or `--soft`. Never `--hard`.**
  This is not a preference — it is the most expensive thing that has happened in this repo. On
  2026-08-15 the merge backstop's refusal banner printed `git reset --hard origin/<branch>` as its
  remedy; an agent ran it in the lobby's **main checkout** and destroyed three other sessions'
  uncommitted work. The main checkout hosts `_artifacts/_memory/`, which every session on this
  machine writes, so **it is never a clean tree**, and **there is no git hook for `reset`** — no
  gate in this system can refuse it, before or after. The only defence is that nothing prints it.

  | Situation | The move | Why |
  |---|---|---|
  | the lane was already pushed and you want the remote's version | `git reset --keep origin/<branch>` | **refuses** if a file it would touch has local changes, instead of discarding it |
  | undo a local commit, keep the work | `git reset --soft HEAD~1` | moves the pointer only; the tree is not touched |
  | you are merely behind | `git pull --ff-only` | no rewind at all |

  `test_git_hooks.py` case **RH1** sweeps `.agents/` and `docs/` and fails on any line that prints
  `git reset --hard` as a step. It reads *instructions*, not mentions: this paragraph names the
  command in order to forbid it, and must keep passing (**RH3**). A guard that banned the string
  would force whoever hit it to delete the explanation, which is how the lesson gets lost. *(SCC-180.)*

See `_artifacts/_memory/nothing-guards-the-merge-target.md`.

### ⛔ A revert reads from a REF — `origin/main`, never a sha (SCC-184, measured 2026-08-16)

The rule above protects the branch you merge **onto**. This one protects the ref you **read from**,
and it is the same disease a third time: an operation that acts on the wrong ref and reports success.

Undoing work in a lane — `git checkout <thing> -- <path>` — is a **read**, and *which ref* decides
whether a sibling lane's landed work survives your merge. The two forms are not interchangeable:

| Form | What happens when the lanes meet |
| --- | --- |
| `git checkout origin/main -- <path>` | **SAFE under any later merge.** Your net diff against the merge-base is empty, so git resolves in the sibling's favour — whichever lane lands first, their work survives. |
| `git checkout <sha> -- <path>` — or a **stale local `main`**, or any ref captured before you absorbed | **DELETES whatever landed in between.** Clean merge, **no conflict**, nothing red, and it rides onto `main` inside an otherwise correct-looking lane. |

- **The safe form, and it is the only one worth memorising:**

  ```bash
  cd "$REPO" && git fetch origin
  cd "$REPO" && git checkout origin/main -- <paths>
  ```

- **`main` is not a synonym for `origin/main`.** A local `main` in a worktree is a *cached* pointer.
  It is stale from the moment a sibling pushes, and it is stale exactly when this matters.
- **Re-assert immediately before the close-out, not once at the start.** `main` moves while you
  build. If the revert is meant to be a no-op, prove it is still one:
  `cd "$REPO" && git diff origin/main -- <paths>` must be empty.
- **Why it is invisible:** git has no way to tell a deliberate revert from a stale read. Both are a
  legal write of older content. There is no conflict to raise, so nothing goes red — the only thing
  standing between you and it is which ref you typed.
- **Measured, not reasoned.** Both directions were run as synthetic three-way merges before this was
  written down, because the audit that found it had the mechanism backwards on the first pass. A
  claim about merge semantics is worth exactly as much as the merge you ran to check it.

See `_artifacts/_memory/revert-target-must-be-a-ref.md`.

## Sync-first — check the remote before you land

Phone and desktop share branches, so landing from a **stale** branch is what causes the
diverge → rejected-push tangle. Before the landing push:

1. **Fetch and compare:** `git fetch origin epic/<JIRA-KEY>-<slug>`, then check whether you are behind
   (`git rev-list --count HEAD..origin/epic/<JIRA-KEY>-<slug>` > 0).
2. **If behind, merge `origin/epic/<JIRA-KEY>-<slug>` into your story branch first** (the landing block above
   does this by default) so you never land on top of a stale base.
3. **If it will not merge cleanly**, **STOP and flag it** — hand Mr. Hatter the situation. Do NOT run a
   blind merge/rebase, and never force-push.

The same applies one level up: before `/cicd-push-e2e` merges an epic into `main`, it first merges
`origin/main` INTO the epic branch (absorbing any hotfixes that shipped mid-epic), re-gates, and only
then merges to `main` — so `main` never receives an unresolved conflict.

## Always

- **Clear the Dummy GitHub Token:** The Antigravity IDE automatically injects a dummy `GITHUB_TOKEN` into the agent's environment as a sandbox security measure. Because Git and the `gh` CLI prioritize this environment variable over the Windows Credential Manager, it causes authentication failures. **Before running any `git` or `gh` commands, you MUST clear this variable** by prefixing the command or running: `Remove-Item Env:\GITHUB_TOKEN -ErrorAction Ignore; <command>`.
- **Validate CI/CD credentials**: Before landing on a deployment-triggering branch (`main`), verify that the target repository's required secrets and variables are set up on GitHub using `gh secret list` and `gh variable list` (WIF-based workflows need neither — check what the workflow actually references). If credentials are missing, STOP and notify Mr. Hatter before proceeding.
- The `walkthrough.md` **"Your Actions"** section records what landed — the branch, the commit range,
  and **errands only**: what the operator must go and DO outside the chat (an epic promotion via
  `/cicd-push-e2e`, a live test). **Never a decision or a question** — ask those in the session
  (→ `artifacts-always-first` §6). It is no longer a `git add` command block, because the agent
  already ran it.

> **Web/mobile sessions** follow the same model with lighter mechanics — see `mobile-mode.md`
> → Override 1. It shares this rule's safe-commit mechanics and Sync-first.
