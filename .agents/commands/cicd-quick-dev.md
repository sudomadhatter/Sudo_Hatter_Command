---
description: The quick lane for a project — small, non-critical work with TDD kept and the ceremony cut. Five steps — scope check against the repo's critical surfaces (an overlap is a soft stop only the operator's word lifts), a plan and the literal `approved`, RED then GREEN, a walkthrough and the literal `approved`, then the close-out tripwire on the real diff. Self-audit and code review run only when asked; no `Verdict:` stamp unless a review ran. Never closes out.
platforms: [opencode, antigravity, claude, codex, zoo]
---

# /cicd-quick-dev — the quick lane (a project; TDD kept, ceremony cut)

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` § Two toggles, and the rails that never move — **this door IS the
>   quick lane, defined there once for both levels**; the rails hold here as everywhere: explicit
>   paths only (never `git add -A`/`.`/`-u`), never push `main`, never force-push
> - `.agents/rules/critical-surfaces.md` — the lane's **line**: five surfaces, each repo's paths in
>   its own `.agents/critical-surfaces.json`, `scope_check.py` answering from paths. An overlap is a
>   SOFT stop and only the operator's quoted word lifts it; the script never asks
> - `.agents/rules/000-PLAN-FIRST-GATE.md` — **this lane carries a plan** (Step 2) and the gate binds
>   in full; what the lane drops is the self-audit and the review verdict unless the operator asks
> - `.agents/rules/artifacts-always-first.md` — the plan and the closing `walkthrough.md`, both in the
>   owning `_artifacts/` store; neither is skipped
> - `.agents/rules/worktree-per-story.md` — a worktree for every commit-producing lane, `chore/*`
>   included (SCC-62); §"cwd is not intent" is why Step 0 pins the repo from command output
> - `.agents/rules/tests-must-gate-for-real.md` — Step 3's gate goes vacuously green three ways: an
>   empty diff, a missing tool reported as a skip, and a piped exit code
> - `.agents/rules/work-consolidation.md` — where a finding too big for this lane GOES: its own
>   ticket → an open thematic parent → the open rolling ticket → mint. Never a pile in the walkthrough
> - `.agents/rules/code-standards.md` §6.5 — **only when the operator asks for the audit (Step 2) or
>   the review (Step 4)**: you are the assessor, not the lens — is it REAL · does it change BEHAVIOUR
>   · is it in THIS diff, all three YES to act. "It's cheap" is not a reason
> - `.agents/rules/reproduce-before-you-fix.md` — **when the quick fix is a BUG fix**: the five gates
>   (reproduce → minimize → pin a test seen red → falsify one hypothesis at a time → minimal fix → prove
>   by reverting). Its G3 stop conditions send the work to the full lane.

Thin orchestrator for SMALL, NON-CRITICAL project work — a UI fix, a document or file update, a
task that does not earn the full ①②③ pipeline.

**TDD stays. What this lane cuts is ceremony the operator did not ask for** (operator ruling,
2026-09-10): no self-audit and no review verdict unless asked, no lens roster, no engine. What it
keeps: a worktree, a scope check against a written list, a plan and the literal `approved`, the
assertion seen red then green, a walkthrough and the literal `approved`, and a tripwire on the real
diff at the door. The line between this lane and the full one is a file, not a feeling.

> Flow position: worktree → scope check → plan + `approved` → RED → GREEN → walkthrough + `approved`
> → tripwire → [STOP; close-out is the operator's door].

## Step 0 — Resolve the target project, and print the epic mode (FIRST — before any other step)
Bind the target per `.agents/rules/smh-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override → `.agents/active-project.txt` → else **STOP and ask** — never guess, never operate on the
lobby. Set `PROJECT_ROOT` and **echo exactly** `Target: Projects/<name>` before any work; every path and
child tool call resolves under `PROJECT_ROOT`.

Then **the epic mode, from the git query, never from belief** (`git-policy.md` § The epic's mode,
SCC-446):

```bash
L=$(pwd)                                                             # the lobby — pin it BEFORE any cd (command-shape.md §Absolute fills)
cd "$PROJECT_ROOT" && env -u GITHUB_TOKEN git fetch origin --prune
cd "$L" && python3 .agents/scripts/epic_mode.py --repo "$PROJECT_ROOT"   # PC: `python`  ⛔ the script lives in the LOBBY — the `cd "$L"` is what finds it after the fetch's cd, and it leaves you back in the lobby for the steps below
```

**Echo both lines it prints** — `TRUNK` / `FULL <branch>` / `LIGHT <branch>`, then the landing cost.
The mode decides Step 0.5's base and Step 5's tripwire base; the lane never changes it and **never
proposes cutting a light epic** — the mode is the operator's, chosen once at kickoff. `AMBIGUOUS`
(more than one live epic on origin) is a STOP.

## Step 0.5 — Key, worktree, branch, ticket (before the first edit)

**Pin the ticket key you are working, before any tool has answered anything.** Every branch and every
commit must carry the repo's key (`.agents/jira.conf`), or the armed `commit-msg` hook refuses the
commit. Story lane: the story's `jira_key:` frontmatter. Ad-hoc lane: the ticket you were handed —
read its `ACCEPTANCE` block, it is Step 2's first source:

```bash
EXPECTED_KEY="AVCH-00"     # the ticket you MEAN
acli jira workitem view "$EXPECTED_KEY"; echo "acli exit: $?"
```

**Read that exit code — a non-zero is TWO different things, and only one of them is a stop.** The key
was refused (wrong project prefix, a key that does not exist) → **STOP and ask**; the board was
unreachable (no credential store in a sandboxed shell, no network) → **carry on with the key you were
handed**, and say in the walkthrough that the ticket was never read back. This is the same distinction
the `jira_feed.py start` table below draws between exit `2` and exit `4`, and it has to be drawn here
too: `acli` returns non-zero for both, and treating a dead uplink as a bad key sends you to mint a
duplicate ticket for work that already has one.

No ticket **handed to you at all** → **STOP and ask.** Never invent a key; a keyless branch cannot be
committed, closed, or found again.

Per `worktree-per-story`: reuse an existing `claude/<JIRA-KEY>-<slug>` tree for this fix, else open
one. The base is a **remote-tracking ref after a fetch, never a bare local `main` or epic ref** — a
local ref is a cache a sibling lane has already moved past — and **the base is the Step 0 mode's**:

```bash
L=$(pwd)                                                     # the lobby — pin it BEFORE any cd (command-shape.md §Absolute fills)
cd "$PROJECT_ROOT" && git worktree list                      # reuse this fix's tree if it exists
cd "$PROJECT_ROOT" && git fetch origin                       # ⛔ the base is origin/…, never a bare local ref
# story lane, FULL or LIGHT epic — off the story's EPIC branch (the name Step 0 printed). ⛔ `--no-track`: an
# origin/… start-point would set the lane's upstream to the EPIC, and a bare `git push` then suggests the
# banned `HEAD:epic/` push (worktree-per-story G3):
cd "$PROJECT_ROOT" && git worktree add --no-track .claude/worktrees/<slug> -b claude/<KEY>-<slug> origin/epic/<KEY>-<mode>-<N>-<epic-slug>
# story lane, TRUNK — no epic branch exists; the story lane is cut from origin/main and lands on main by PR (SCC-423):
cd "$PROJECT_ROOT" && git worktree add --no-track .claude/worktrees/<slug> -b claude/<KEY>-<slug> origin/main
# ad-hoc lane — no story applies (a truly ad-hoc fix outside any sprint): git-policy.md's chore lane, off main:
cd "$PROJECT_ROOT" && git worktree add --no-track .claude/worktrees/<slug> -b chore/<KEY>-<slug> origin/main
cd "$PROJECT_ROOT"/.claude/worktrees/<slug> && git branch --unset-upstream   # belt and braces: no upstream until the lane's own first push
cd "$L" && python3 .agents/scripts/link-worktree-assets.py "$PROJECT_ROOT"/.claude/worktrees/<slug>   # PC: `python`  ⛔ the script lives in the LOBBY — the cd "$L" is what finds it after the cds above
BRANCH=$(cd "$PROJECT_ROOT"/.claude/worktrees/<slug> && git rev-parse --abbrev-ref HEAD)
echo "Lane: $BRANCH"
```

Echo the case and the branch **from `rev-parse`, never from memory.** Every path and command from here
binds to that tree. Quick fixes are NOT exempt — this is what keeps them tangle-free, rollbackable,
and landable through a door.

`link-worktree-assets.py` links `node_modules`, `auth_keys/`, `.venv`, `.env` — at the repo root and
one level down (`backend/.env`, `frontend/node_modules`) — into the tree. Without them pytest,
uvicorn, `next dev` and the emulators fail on cwd-relative lookups, and Step 3 reports an
environmental red as a real one. A linked `.env` is **shared state**: re-run with `--copy-env` if this
lane will change it. ⛔ `--unlink` runs BEFORE any `git worktree remove` — a recursive delete through a
junction eats the shared targets (`/cicd-prune-worktree` does this).

**Write the lane's manifest — `task.yaml` beside the walkthrough folder, on the AD-HOC lane** (the
story lane's spec is its story file). It is what makes Step 4.5's slug a read rather than a retype,
and the door reads the same file:

```yaml
task_key: <KEY>
primary_repo: Projects/<name>
branch: chore/<KEY>-<slug>
close_command: TBD          # ⛔ see below — settled at Step 4, not here
secondary_repos: []
```

⛔ **`close_command` is the one field you cannot know yet.** The door is *derived from the diff*
(the door table below), and at the moment you write this file there is no diff — a `chore/*` lane that turns out to touch
`backend/` ships through `/cicd-push-e2e`, and one that does not goes through
`/smh-close-task-merge-tree`. Writing either one now is a guess that the close-out then reads as a
decision. Leave it `TBD` and **rewrite the line at Step 4**, once `git diff --name-only` has answered.

**Move the ticket to `In Progress` — now, at the tree, not at the merge (SCC-113):**

```bash
python3 .agents/scripts/jira_feed.py start --key <KEY> --apply    # PC: `python`
```

Idempotent, so a re-run or a resumed lane is a no-op. **Read its exit code — four outcomes:**

| Exit | Means | What you do |
|---|---|---|
| `0` | moved, or already `In Progress` | carry on |
| `3` | **left alone** — the ticket is `Blocking` / `In Review` / `Deferred` | **stop and ask.** You are opening a lane on a ticket that is waiting on something; say which and confirm that is intended |
| `2` | **the board refused it** — a `Done` key (so the key is wrong), or a move that did not land | **stop.** Never work a closed ticket's key; mint one at the `jira.md` §Who-mints-tickets seam |
| `4` | **the board was unreachable** — transport, not a verdict | **carry on and retry later.** ⛔ Do *not* mint a ticket: nothing here says your key is wrong. Sandboxed shells cannot reach the credential store (`jira.md` top), and the operator commits from planes |

**⭐ Read the sibling lanes now, not at merge time.** Several lanes run at once and their uncommitted
work is invisible to `grep`:

```bash
cd "$PROJECT_ROOT" && git worktree list
cd "$PROJECT_ROOT"/.claude/worktrees/<other-slug> && git diff --name-only <that lane's base>...HEAD   # origin/epic/<…> for a story tree on a FULL or LIGHT epic, origin/main for a chore tree or a TRUNK story tree
cd "$PROJECT_ROOT"/.claude/worktrees/<other-slug> && git status --short
```

Any file in both their set and your intended set is a **landing-order dependency**. Say which lane
should land first and what happens to your work if it does not. Carry it into the walkthrough's
`## Evidence`.

⛔ **A worktree is not optional on either case, and this line used to say `no worktree`.**
`worktree-per-story` has required one for **every commit-producing lane** since SCC-62, and its lane
table names `chore/<JIRA-KEY>-<slug>` explicitly; the quick lane opens a worktree too — it is a rail,
not ceremony (`git-policy.md` § The rails).

⛔ **This lane does not merge, and it never touches `main`.** Step 5 is the end: branch pushed, work
reported, and the landing is a **separate, operator-invoked act through a door**. Invoking a door IS
the sign-off; a spoken "looks good" is not, and no agent merges to `main` on its own initiative
(`git-policy.md` § The road to `main`, SCC-183). Which door exists depends on the repo:

| Lane | Door |
|---|---|
| story lane on `claude/*`, FULL or LIGHT epic | the epic branch, at close-out — `/cicd-close-story-merge-tree` opens the PR into the epic; the epic ships via `/cicd-push-e2e` |
| story lane on `claude/*`, TRUNK | `/cicd-close-story-merge-tree`'s trunk arm — a PR into `main` the operator merges (SCC-423) |
| chore lane in a **project repo**, diff reaches a deployable path (`backend/ frontend/ firebase/ functions/ mobile/ .github/`) | `/cicd-push-e2e` — `ship_preflight.py` admits the `chore/*` under the **light gate** (SCC-211); nothing deployable → it refuses and names the PR door |
| chore lane in a **project repo**, nothing deployable in the diff | `/smh-close-task-merge-tree Projects/<name>` — the PR door, with the project named in `$ARGUMENTS`. `task_preflight.py` derives `LANE: LOCAL`, and it opens the PR and STOPS (`git-policy.md` § The write gate, `main` row) |

⚠ **Which door is derived from the DIFF, not chosen:** both doors read the same deployable-path list
and refuse each other's lane, so the branch decides. Project repos publish no `main-write-gate`, so
the PR merge there is the operator's click with no server-side gate — still the operator's, still
never yours.

⛔ **There is still no command-centre row, and that is not an omission.** This command binds
`smh-target-resolution.md` — exactly ONE project, **never the lobby** — so command-centre work
is unreachable from here by construction; it belongs to `/smh-quick-dev`, the same lane turned
inward on the command centre. The `smh-` door appears above **only with `Projects/<name>` as its
argument** (its Step 0 takes a `Projects/` path and the subject stays `PROJECT_ROOT`): a bare
invocation binds the lobby, which is the one thing target resolution forbids.

⭐ **The gap SCC-205 recorded here is CLOSED (SCC-211).** This paragraph used to say a project repo's
ad-hoc `chore/*` lane had no door of its own. `ship_preflight.py` now admits a deployable `chore/*`
under the light gate and refuses the rest by name, and `task_preflight.py` takes the non-deployable
half as `LANE: LOCAL` — two doors, selected by the diff. Report the pushed branch and the door its
diff selects; **still never merge by hand.**

## Step 0.7 — Probe the review runtime, and record it (SCC-177)

Ask this runtime whether it can fan out to subagents — do not answer from what usually happens,
because a headless pipeline or a platform with no subagent tool makes the answer `inline`, and both
are invisible until a lens fails to launch later. The answer goes into the walkthrough header Step 4
writes, on its own line, above everything else — and, if the operator asks for a review at Step 4,
into `/cicd-code-review`'s `review_runtime` input:

<!-- twin-law: review-runtime-probe -->
⛔ **The probe asks ONE question: does a subagent tool exist in this runtime? (SCC-203)** Yes →
`fan-out`. No → `inline (no subagent tool)`. ⭐ *Am I permitted?* is **already answered — the
operator invoked a `/` command, and a command IS a user request**; the standing directive
*"Do not call the AgentTool unless the user requested it"* is **satisfied by that invocation**, so you
never stop to ask and never quietly downgrade. ⛔ If you still believe you cannot, you may not
record a bare `inline` — write `inline (blocked: <what blocked you, verbatim>)`. A bare `inline`
from a runtime that HAS the tool is indistinguishable from one that never had it, and that
indistinguishability is the whole defect.
<!-- /twin-law -->

```
review-runtime: fan-out
```

⛔ **Here, not at Step 4 — the probe must precede any review it describes.** Recorded afterwards it is
read off a roster that already exists, which makes the check circular: the header can only ever
agree with the states it was derived from. Recorded here it is an independent claim, and when a
review does run, `walkthrough_roster.py` blocks the close-out if the roster disagrees with it
(`inline` + a lens reporting `ok` is the contradiction it catches).

## Step 1 — Scope check: the line, from paths (`critical-surfaces.md`)

Name the files you intend to touch — the planned set, from the ticket's `ACCEPTANCE` block and your
reading of the code — and run the check **from the lobby** (the script lives there, like
`link-worktree-assets.py`):

```bash
cd "$L" && python3 .agents/scripts/scope_check.py --repo "$PROJECT_ROOT" --paths <the planned set>   # PC: `python`
```

**Read line 1, the word, never the exit code.** `CLEAR` → print the line and continue to Step 2.
`OVERLAP` → **STOP.** Print every overlap line the script printed (`<path>  <surface>: <why>`), say in
one sentence what it would take to do this work in the full lane (① `/cicd-write-story-tests` → ②
→ ③), and **wait**. `ERROR` → the check did not run (no paths, a map that does not parse); fix the
input and run it again — silence is unknown scope, never clear.

⛔ **The only thing that moves the lane past an `OVERLAP` is the operator's word, in this turn,
quoted verbatim into Step 2's plan** as `**Scope override (<date>):** "<his exact words>" — covers:
<the overlapping paths>`. "ok", "continue", "go ahead" are not it (`000-PLAN-FIRST-GATE` § What is
NOT approval), and the plan's own `approved` is not it either — an approval of a plan is not an
approval of the surface it touches. There is no agent override and no `--force`; the script never
asks. A repo with no `.agents/critical-surfaces.json` prints `MAP: none` and is checked against
the generic set — say so in the walkthrough, and name the map as the fix (AVCH-152 lands
AviationChat's).

⛔ **This step never proposes a lighter road.** Not a light epic, not "just this once", not the
lightweight lobby lane. The answer to an overlap is the operator's word or the full lane.

**Do NOT create a story file on the ad-hoc lane.** A story id / epic story keeps BMAD's normal story
handling; an ad-hoc fix mints **no story file and no epic key** (`artifacts-always-first` §2 quick-fix
bucket) — hanging one off a finished epic silently reopens it.

## Step 2 — Plan, then the literal `approved`

Write `implementation_plan.md` in the lane's artifact folder — the owning `_artifacts/` store per the
project's `_artifacts/AGENTS.md`: story work → `epic_<N>/<story>/`, ad-hoc →
`quick_fixes/quick-fix-<track>.<n>-<slug>/` (read that folder's `INDEX.md` for the next free number
and append the row by hand; **create the folder + its `INDEX.md` if this is the repo's first quick
fix**). Short, and complete:

```markdown
# <KEY> — <one line>

**Goal:** <what changes for the user, one sentence>
**Scope check:** CLEAR @ <date>   |   OVERLAP — **Scope override (<date>):** "<the operator's words>" — covers: <paths>

## The assertion
<the test that proves it — file, name, what it asserts; for a docs change: the link check on every path touched>

## The change
- <file> — <what, one line each>

## Declared Change Set
- EDIT `<path>` - <why> → <the assertion or acceptance row it serves>
- NEW `<path>` - <why> → …
```

Present the key points inline in chat with a clickable link to the file, then **STOP and wait for the
literal word `approved`.** "ok", "looks good", "continue" are not it (`000-PLAN-FIRST-GATE`). A
correction narrows the plan and you stop again.

**`/cicd-self-audit` runs only if the operator asks.** When he does, it appends its section and its
`Audit verdict:` to this plan and a NO-GO stops the lane exactly as on the full lane. When he does
not, the plan carries no audit section and says nothing about one — an absent audit is a decision,
not a gap.

## Step 3 — RED, then GREEN (the same TDD as the full lane)

**The assertion first, seen red.** Write the test the plan named into the project's suite (or, for a
bug fix, the ONE pinning regression test from `reproduce-before-you-fix` G3) and run it **bare, never
piped**; paste the red line into the walkthrough's `## Evidence`. A docs change uses the link check
as its floor: every path and `#L` anchor touched resolves. ⛔ **Prose here on purpose** —
`check_links.py` is a LOBBY script and a thin project does not carry it; run it from `$L` against
`PROJECT_ROOT`, or check by hand, and say which.

**Then the change, until it is green.** Commits happen **inside the worktree, explicit paths only** —
never `git add -A` — and every commit subject leads with the repo's Jira key from `.agents/jira.conf`,
or the armed `commit-msg` hook refuses it. ⛔ **Backticks in `-m "…"` EXECUTE.** A message quoting a
shell command runs it. Use `git commit -F <file>` whenever the message contains a backtick. Never
push `main`.

**Then the same floor CI will run**, on the changed files, bare: the scoped suite for the touched
module (the **WHOLE** endpoint/module suite when a shared handler changed — a new read on a shared
endpoint silently breaks sibling tests), and the project's lint gate on the changed files (`ruff`,
`pyrefly`, `eslint`, `tsc` — whichever the project's PR gate lists). Paste the **actual** totals.
**An empty diff is a STOP, not a pass** (`tests-must-gate-for-real`): a gate that reads nothing
reports green having checked nothing.

No lens, no roster, no engine. If a finding you make while building is bigger than this lane — a
second independently shippable deliverable, a G3 stop in `reproduce-before-you-fix` — say so in one
line and hand the work to the full lane (① `/cicd-write-story-tests`); keep the worktree and
everything written, discard nothing.

## Step 4 — Walkthrough, then the literal `approved`

- **Ad-hoc lane, FIRST: settle `close_command` in `task.yaml`.** The diff exists now, so the door is
  a read rather than a guess. Run `cd "<the tree>" && git diff --name-only origin/main...HEAD`, match it
  against the deployable-path list in Step 0.5's door table, and **rewrite the `TBD`** —
  `cicd-push-e2e` if anything deployable is in the set, `smh-close-task-merge-tree` if not. The
  close-out reads that field; leaving it `TBD` sends the operator to a door the preflight will refuse.
- **Story lane only:** advance the story to **`review`** on the way out (`story_status.py`, the
  normal dev→review flip — `story-status-flip-contract`); `done` stays the operator's. On the ad-hoc
  lane there is no story key, so nothing flips.
- Write a **thin `walkthrough.md`** beside the plan. It carries `review-runtime:` (the Step 0.7
  header, one line, above everything else) → `## Task Checklist` → `## Evidence` (the assertion:
  the red line, then the green totals, the lint totals, the sha; the scope-check line; any
  landing-order dependency from Step 0.5) → `## Your Actions` (**required even when empty** — an
  unchecked `- [ ]` is something only the operator can DECIDE and holds the ticket out of `Done`;
  ⛔ never the ceremony's own steps, SCC-193, which `jira_feed.py check-actions` hard-refuses).
  Post clickable Markdown links to the plan and the walkthrough in the chat.
- **`/cicd-code-review` runs only if the operator asks.** When it runs, it appends `## Code Review
  (<date>)` with its roster and its `Verdict: … @ <sha>` line exactly as on the full lane, and the
  close-out reads that verdict. **When it does not run, the walkthrough carries ONE record line
  instead, in `## Evidence`, and no `Verdict:` line at all:**

  ```
  Review: none - quick lane; walkthrough approved by the operator @ <sha>
  ```

  ⛔ Never write a `Verdict:` stamp to stand in for a review that did not run: the stamp pulls in
  the roster gate (`walkthrough_roster.py`, SCC-173) for lenses that never launched, and the
  close-out blocks on the contradiction. The record line is what `closeout_preflight.py` reads
  as "no review, by design"; a walkthrough with neither line is still refused there.

Then **STOP and wait for the literal word `approved`** on the walkthrough. That word is the
operator's acceptance of the work as shown; it is not the landing (Step 5's door is).

## Step 4.5 — File the Dev Record on the ticket (AUTOMATIC, never ask)
This lane hands its branch to a door, and the ad-hoc chore lane never reaches
`/cicd-close-story-merge-tree` at all — so this is the only place its knowledge gets recorded. Before
SCC-49 it died in the walkthrough. Runs AFTER Step 4's `approved` so the walkthrough it points at is
the one the operator saw. The key was **pinned at Step 0.5 as `EXPECTED_KEY`** and is read back from
there — the story's `jira_key:` frontmatter on the story lane, the ad-hoc lane's `task.yaml` on the
other. Never re-derive it here.

```bash
python3 .agents/scripts/jira_feed.py devrecord --key <JIRA-KEY> --story <THE ONE SLUG> \
       --project <PROJECT> --stage quick-dev --walkthrough <the Step 4 walkthrough> \
       --outcome "<what shipped, one line>" --verdict "<the review's verdict, or: none (quick lane)>" \
       --decision "<a ruling made while fixing>" --pitfall "<what nearly bit>" \
       --followon "<only what went to work-consolidation's homes - never a pile>" --apply
```

**Exactly one Dev Record per ticket.** The script finds an existing record and UPDATES it in place, so
a story that later goes through `/cicd-close-story-merge-tree` ends with one current record instead of
two partial ones — **never pass `--append-new` here.**

⛔ **`--story` is the fork risk, and `<id-or-slug>` was the fork.** `devrecord` decides
update-vs-create from the **slug**, never from `--key`, so two surfaces spelling one lane two ways
give one ticket two records — and `check` then blesses the pair as "two lanes". That is AVCH-59,
measured 2026-08-15. `/cicd-close-story-merge-tree` passes `--story <id>`, meaning the **BMAD story id**,
so this step must pass **the same story id, character for character** — never the branch slug, never a
free-text description. On the ad-hoc lane there is no story id: pass the **branch slug** from
`chore/<JIRA-KEY>-<slug>`, and pass that identical string at every later surface.
⭐ **On the ad-hoc lane, READ it — do not retype it.** Step 0.5 writes that lane a `task.yaml`
carrying `branch: chore/<KEY>-<slug>`, which is the same file `/smh-close-task-merge-tree` reads and
the same source `devrecord` defaults from — so the slug is typed once, at the tree, and every later
surface reads it. That is what makes the anti-fork guard live on this side (AVCH-59 was one ticket
with two records because two surfaces spelled one lane differently). The story lane has no
`task.yaml` and needs none: its story id IS the shared identifier.

**`jira_feed.py devrecord` reads the ticket back** and exits 2 if the comment is not there; a non-zero exit means the record did NOT land, so report that rather than
success. No ticket key at all (a fix outside any ticket) → say so in the Done report and skip;
**never invent a key.** Full acli reference: `.agents/rules/jira.md`.

## Step 5 — The tripwire on the real diff, then STOP

The same check as Step 1, on what you **actually** changed — committed, after the lane's last commit
— against the base the Step 0 mode gave the lane:

```bash
cd "$L" && python3 .agents/scripts/scope_check.py --repo "<the tree>" --diff origin/epic/<KEY>-<mode>-<N>-<epic-slug>   # story lane, FULL or LIGHT
cd "$L" && python3 .agents/scripts/scope_check.py --repo "<the tree>" --diff origin/main                                # chore lane, or a TRUNK story lane
```

`CLEAR` → print the line, and the `DIFF: <n> file(s)` line under it, into the walkthrough's
`## Evidence`. `OVERLAP` → every overlapping path is either covered by a `Scope override` the plan
already carries (print it, pass) or it is not — and **an uncovered overlap EJECTS the lane**: hand
the work to ① `/cicd-write-story-tests`, keep the worktree and every commit, discard nothing.

⛔ **A fired eject RE-ARMS the plan-first gate in full** (`000-PLAN-FIRST-GATE.md`): the full lane
needs its own `implementation_plan.md`, the self-audit, and the operator's literal `approved` before
another project file is modified. An under-declared Step 1 is caught here by the diff, never by the
agent's memory of what it meant to touch.

Then **STOP here.** Never land on the epic branch (close-out's job), never touch `main`, never
transition the ticket. Display the plan link, the walkthrough link, the key changes, the scope-check
lines, and the branch + its push state. Then invite the operator to invoke **the door Step 0.5's
table names for this lane** — `/cicd-close-story-merge-tree` on the story lane (the PR into the epic,
or into `main` in TRUNK mode); `/cicd-push-e2e` or `/smh-close-task-merge-tree Projects/<name>` on
the ad-hoc lane, by what the diff touched. Invoking it IS the sign-off.
