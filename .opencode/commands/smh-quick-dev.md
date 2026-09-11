---
description: The quick lane for the command centre — small, non-critical toolkit work with TDD kept and the ceremony cut. Five steps — scope check against the lobby's critical surfaces (an overlap is a soft stop only the operator's word lifts), a plan and the literal `approved`, RED then GREEN, a walkthrough and the literal `approved`, then the close-out tripwire on the real diff. Self-audit and code review run only when asked; no `Verdict:` stamp unless a review ran. Acts on the repo you are standing in; ejects to /smh-dev-task-tests. Hands off to /smh-close-task-merge-tree. Use when the operator names one specific thing — a guide, a reference fix, a small rule edit — or says "quick dev this".
platforms: [opencode, antigravity, claude, codex, zoo]
---

# /smh-quick-dev — the quick lane (the command centre; TDD kept, ceremony cut)

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` § Two toggles, and the rails that never move — **this door IS the
>   quick lane, defined there once for both levels**; the rails hold here as everywhere: explicit
>   paths only (never `git add -A`/`.`/`-u`), never push `main`, never force-push; every branch
>   and every commit carries the repo's Jira key
> - `.agents/rules/critical-surfaces.md` — the lane's **line**: five surfaces, the lobby's paths in
>   `.agents/critical-surfaces.json` (its gates), `scope_check.py` answering from paths. An overlap
>   is a SOFT stop and only the operator's quoted word lifts it; the script never asks
> - `.agents/rules/000-PLAN-FIRST-GATE.md` — **this lane carries a plan** (Step 2) and the gate binds
>   in full; what the lane drops is the self-audit and the review verdict unless the operator asks
> - `.agents/rules/artifacts-always-first.md` — a Task's artifacts live in
>   `_artifacts/_main/<YYYY-MM-DD>_<slug>/`; the plan and the closing `walkthrough.md` are never skipped
> - `.agents/rules/worktree-per-story.md` — every commit-producing lane opens a worktree, Task lanes
>   included (SCC-62); §"cwd is not intent" is why the branch below is pinned from command output
> - `.agents/rules/tests-must-gate-for-real.md` — Step 3's red must fail for the RIGHT reason, and its
>   gates go vacuously green three ways: an empty diff, a missing tool reported as a skip, a piped
>   exit code
> - `.agents/rules/work-consolidation.md` — where a finding too big for this lane GOES: this lane's
>   own ticket → an open thematic parent → the open **rolling** ticket (`Bugs and Updates - <YYYY-MM>`,
>   rule 1) → mint. Never a pile in the walkthrough
> - `.agents/rules/code-standards.md` §6.5 — **only when the operator asks for the audit (Step 2) or
>   the review (Step 4)**: you are the assessor, not the lens — is it REAL · does it change BEHAVIOUR
>   · is it in THIS diff, all three YES to act. "It's cheap" is not a reason
> - `.agents/rules/reproduce-before-you-fix.md` — **when the work is a BUG fix**: reproduce → minimize
>   → pin a test seen red → falsify one hypothesis at a time → minimal fix → prove by reverting. Its
>   G3 stop conditions send the work to `/smh-dev-task-tests`

The quick lane, turned inward on the command centre. The same five steps as `/cicd-quick-dev` in a
project; the subject is **where you are standing**, and the lobby is a legitimate subject.

**TDD stays. What this lane cuts is ceremony the operator did not ask for** (operator ruling,
2026-09-10): no self-audit and no review verdict unless asked, no lens roster, no mutant sweep.
What it keeps: a worktree, a scope check against a written list, a plan and the literal `approved`,
the assertion seen red then green, the lobby floor run bare, a walkthrough and the literal
`approved`, and a tripwire on the real diff at the door. The line between this lane and
`/smh-dev-task-tests` is a file, not a feeling — and not a size: a one-line rule edit that touches
a gate is `/smh-dev-task-tests` work; a forty-line guide that touches nothing critical is this lane's.

> Flow position: worktree → scope check → plan + `approved` → RED → GREEN → walkthrough + `approved`
> → tripwire → **[STOP, hand back]** → the operator's `/smh-close-task-merge-tree`. It never merges
> and never closes its own ticket.

---

## Step 0 — Resolve the repo (FIRST) — from command output, never from belief

The subject is **where you are standing**, not a pointer. If `$ARGUMENTS` names a folder under
`Projects/` or a path, use that; otherwise the current repo. Do **not** read
`.agents/active-project.txt` — this lane's whole point is that the command centre is a legitimate
subject, and that pointer names a child.

```bash
REPO=$(cd "<the path you resolved>" && git rev-parse --show-toplevel)
echo "Repo: $(basename "$REPO")"
L=$(pwd)                                   # the lobby — pin it BEFORE any cd (command-shape.md §Absolute fills)
```

**Pin the ticket key you are working, before any tool has answered anything.** Every branch and
every commit must carry the key, or the armed `commit-msg` hook refuses the commit. Handed a key?
Use it — never mint a second. No key at all → **look for a home before you mint**
(`work-consolidation.md` rule 1): an open parent whose surface this belongs to (then it is the next
lettered Subtask, index row via `jira_feed.py index-row`), else the open rolling ticket (`Bugs and
Updates - <YYYY-MM>`, found by both labels `bugs-and-updates` + `running-bug-list`), and mint only
for work that is a lane in its own right. ⛔ **Never ask "shall I mint a ticket / open a lane?"** —
the operator's ask IS the decision; say in one line what you looked at, then do it.

```bash
EXPECTED_KEY="SCC-00"     # the ticket you MEAN
acli jira workitem view "$EXPECTED_KEY"      # read its ACCEPTANCE block — Step 2 needs it
```

**⭐ Probe the review runtime here, at Step 0, and record it (SCC-177).** Ask this runtime whether it
can fan out to subagents — do not answer from what usually happens, because a headless pipeline or
a platform with no subagent tool makes the answer `inline`, and both are invisible until a lens
fails to launch later. The answer goes into the walkthrough header Step 4 writes, on its own line,
above everything else — and, if the operator asks for a review at Step 4, into `/smh-code-review`'s
`review_runtime` input:

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

⛔ **Step 0, not Step 4 — the probe must precede any review it describes.** Recorded afterwards it is
read off a roster that already exists, which makes the check circular. Recorded here it is an
independent claim, and when a review does run, `walkthrough_roster.py` blocks the close-out if the
roster disagrees with it.

## Step 0.5 — Worktree and branch (before the first edit)

Per `worktree-per-story` + SCC-62, every commit-producing lane isolates — the quick lane included; the
tree is a rail, not ceremony (`git-policy.md` § The rails). `/smh-close-task-merge-tree` Step 5
prunes it.

```bash
cd "$REPO" && git worktree list                                   # reuse this task's tree if it exists
cd "$REPO" && git fetch origin                                    # ⛔ the base is origin/main, never a bare `main`
cd "$REPO" && git worktree add --no-track .claude/worktrees/<slug> -b chore/<KEY>-<slug> origin/main
cd "<the new tree>" && git branch --unset-upstream                # belt and braces: no upstream until the lane's own first push
cd "$L" && python3 .agents/scripts/link-worktree-assets.py .claude/worktrees/<slug>   # PC: `python`  ⛔ the script lives in the LOBBY
BRANCH=$(cd "<the new tree>" && git rev-parse --abbrev-ref HEAD)
echo "Lane: $BRANCH"
```

Echo the branch **from `rev-parse`, never from memory.** Every path and command from here binds to that
tree. **Move the ticket to `In Progress` — now, at the tree, not at the merge (SCC-113):**

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

**⭐ Read the sibling lanes now, not at merge time.** Several `chore/*` lanes run at once and their
uncommitted work is invisible to `grep`:

```bash
git worktree list
cd <each-other-tree> && git diff --name-only origin/main...HEAD
cd <each-other-tree> && git status --short
```

Any file in both their set and your intended set is a **landing-order dependency**. Say which lane
should land first and what happens to your work if it does not. Carry it into the plan.

---

## Step 1 — Scope check: the line, from paths (`critical-surfaces.md`)

Name the files you intend to touch — the planned set, from the ticket's `ACCEPTANCE` block and the
operator's ask — and run the check from the lobby:

```bash
cd "$L" && python3 .agents/scripts/scope_check.py --repo "$REPO" --paths <the planned set>   # PC: `python`
```

**Read line 1, the word, never the exit code.** `CLEAR` → print the line and continue to Step 2.
`OVERLAP` → **STOP.** Print every overlap line the script printed (`<path>  <surface>: <why>`), say in
one sentence what it would take to do this work on `/smh-dev-task-tests` (a plan, `/smh-self-audit`,
`approved`, RED, GREEN, the mutant sweep, `/smh-code-review`), and **wait**. `ERROR` → the check did
not run (no paths, a map that does not parse); fix the input and run it again — silence is unknown
scope, never clear.

⛔ **The only thing that moves the lane past an `OVERLAP` is the operator's word, in this turn,
quoted verbatim into Step 2's plan** as `**Scope override (<date>):** "<his exact words>" — covers:
<the overlapping paths>`. "ok", "continue", "go ahead" are not it (`000-PLAN-FIRST-GATE` § What is
NOT approval), and the plan's own `approved` is not it either — an approval of a plan is not an
approval of the surface it touches. There is no agent override and no `--force`; the script never
asks. In the lobby the critical surface is the gates: `.github/`, the hooks, the preflights, the
permission fence — a change there is `/smh-dev-task-tests` work unless the operator says otherwise.

⛔ **This step never proposes a lighter road.** There is no lighter road: the lightweight lane
(`/smh-quick-fix`, no plan, no `approved`) is retired — this lane is what replaced it, and its plan
is a paragraph, not a ceremony. `lane_qualify.py` is no longer called by any dev door (only the two standing-push doors still
qualify `LIGHT` with it): it answered
size, and a lane with a plan and `approved` does not need a size verdict.

## Step 2 — Plan, then the literal `approved`

Write `implementation_plan.md` into `_artifacts/_main/<YYYY-MM-DD>_<slug>/`, with `task.yaml` beside
it. Short, and complete:

```markdown
# <KEY> — <one line>

**Goal:** <what changes for the operator, one sentence>
**Scope check:** CLEAR @ <date>   |   OVERLAP — **Scope override (<date>):** "<the operator's words>" — covers: <paths>

## The assertion
<the test that proves it — file, name, what it asserts; for a docs change: the link check on every path touched>

## The change
- <file> — <what, one line each>

## Declared Change Set
- EDIT `<path>` - <why> → <the assertion or acceptance row it serves>
- NEW `<path>` - <why> → …
```

```yaml
task_key: SCC-00
primary_repo: Sudo_Hatter_Command
branch: chore/SCC-00-<slug>
close_command: smh-close-task-merge-tree
secondary_repos: []
```

Present the key points inline in chat with a clickable link to the file, then **STOP and wait for the
literal word `approved`.** "ok", "looks good", "continue" are not it (`000-PLAN-FIRST-GATE`). A
correction narrows the plan and you stop again.

> **⭐ Already approved as part of a batch? (SCC-155)** If this lane came from `/smh-plan-task`, its
> plan already carries a `**Batch approval (<date>):** "<the operator's words>"` line naming this
> subtask's key and ending `— recorded at <sha>`. Run the intact check `/smh-dev-task-tests` Step 1.5
> carries (the count of changed lines that are not the approval line must be zero); on
> `APPROVAL-INTACT` go straight to Step 3.

**`/smh-self-audit` runs only if the operator asks.** When he does, it appends its section and its
`Audit verdict:` to this plan and a NO-GO stops the lane exactly as on `/smh-dev-task-tests`. When
he does not, the plan carries no audit section and says nothing about one — an absent audit is a
decision, not a gap.

## Step 3 — RED, then GREEN (the same TDD as the full lane)

**The assertion first, seen red.** Pick the tier the work actually has — the discipline is identical,
only the instrument changes:

| The work is… | The RED is… |
|---|---|
| a **script** (`.agents/scripts/*.py`) | a real test in `.agents/scripts/tests/test_<name>.py`, run via `run_all.py` |
| a **command or a rule** | `workflow_lint.py --toolkit-only` reporting the specific error, or the specific missing door, before you fix it |
| a **move / rename / delete** | `check_links.py` listing the references that will break, captured **before** the move |
| a **doc or structure** | a machine-verifiable assertion: this path exists, this INDEX row matches disk, this link resolves, this grep returns zero |

Run it bare, never piped, and paste the red line into the walkthrough's `## Evidence`. ⛔ A red that
asserts strings or paths that do not exist in real source is fiction, not a red. If the work is
already done when you arrive, say so plainly — a characterization check written green is honest; a
green check presented as a red is not.

**Then the change, until it is green.** Surgical: the plan is the scope, anything beyond it is
drift — cut it or name why it stays. Commit **inside the worktree, explicit paths only** (`git add
-A`/`.`/`-u` are banned), every subject leading with the ticket key; ⛔ backticks in `-m "…"`
EXECUTE — use `git commit -F <file>`. A usage-surface change stages the SOP doc in the SAME commit
(`sop-currency`); `[sop-ok]` is the auditable exit when nothing an operator types changed. Generated
surfaces (`.opencode/commands/`, `.roo/commands/`, GENERATED skills) are never hand-edited — edit
the command, run `/smh-sync-agents`. Push before you hand back: unpushed is stranded.

**Then the lobby floor, bare** — the same gates every lane runs:

```bash
python3 .agents/scripts/tests/run_all.py                        # the enforcement suite
python3 .agents/scripts/workflow_lint.py --toolkit-only
python3 .agents/scripts/check_maps.py --depth3-only --strict     # if you moved or added docs
python3 .agents/scripts/check_links.py --base origin/main         # every path claim the diff touched
```

Paste the **actual** totals. **An empty diff is a STOP, not a pass** (`tests-must-gate-for-real`).
No lens, no roster, no mutant sweep — if a finding you make while building is bigger than this
lane (a second independently shippable deliverable, a G3 stop in `reproduce-before-you-fix`, a
surface the scope check should have caught), say so in one line and hand the work to
`/smh-dev-task-tests`; keep the worktree and everything written, discard nothing.

## Step 4 — Walkthrough, then the literal `approved`

Write a **thin `walkthrough.md`** beside the plan. It carries `review-runtime:` (the header from Step
0, one line, above everything else) → `## Task Checklist` → `## Evidence` (the assertion: the red
line, then the green totals, the gate totals, the sha; the scope-check line; any landing-order
dependency from Step 0.5) → `## Your Actions` (**required even when empty** — an unchecked `- [ ]` is
something only the operator can DECIDE and holds the ticket out of `Done`; ⛔ never the ceremony's
own steps, SCC-193). Post clickable Markdown links to the plan and the walkthrough in the chat.

**`/smh-code-review` runs only if the operator asks.** When it runs, it appends `## Code Review
(<date>)` with its roster and its `Verdict: … @ <sha>` line exactly as on `/smh-dev-task-tests`, and
the close-out reads that verdict. **When it does not run, the walkthrough carries ONE record line
instead, in `## Evidence`, and no `Verdict:` line at all:**

```
Review: none - quick lane; walkthrough approved by the operator @ <sha>
```

⛔ Never write a `Verdict:` stamp to stand in for a review that did not run: the stamp pulls in the
roster gate (`walkthrough_roster.py`, SCC-173) for lenses that never launched. A lane with no
verdict is read as benign by `task_preflight.py` (it runs the full machine gate itself, the
stronger check for a small diff), and `closeout_preflight.py` reads the record line as "no review,
by design".

Then **STOP and wait for the literal word `approved`** on the walkthrough. That word is the
operator's acceptance of the work as shown; it is not the merge (`/smh-close-task-merge-tree` is).

## Step 4.5 — File the Dev Record on the ticket (AUTOMATIC, never ask)

```bash
python3 .agents/scripts/jira_feed.py devrecord --key <KEY> \
       --stage quick-dev --walkthrough <the walkthrough> \
       --outcome "<what shipped, one line>" --verdict "<the review's verdict, or: none (quick lane)>" \
       --decision "<a ruling made while building>" --pitfall "<what nearly bit>" \
       --followon "<only what went to work-consolidation's homes - never a pile>" --apply
```

**Exactly one Dev Record per ticket** — the script finds an existing record and UPDATES it. ⛔ **It
finds it by the SLUG, not by `--key`, so do not pass `--story` (SCC-174):** the slug is read from the
`task.yaml` you wrote in Step 2, the same source `/smh-close-task-merge-tree` uses. **Never pass
`--append-new`.** It reads the ticket back and exits 2 if the comment is not there; a non-zero exit
means the record did **not** land — report that, not success.

## Step 5 — The tripwire on the real diff, then STOP

The same check as Step 1, on what you **actually** changed — committed, after the lane's last commit:

```bash
cd "$L" && python3 .agents/scripts/scope_check.py --repo "<the tree>" --diff origin/main
```

`CLEAR` → print the line, and the `DIFF: <n> file(s)` line under it, into the walkthrough's
`## Evidence`. `OVERLAP` → every overlapping path is either covered by a `Scope override` the plan
already carries (print it, pass) or it is not — and **an uncovered overlap EJECTS the lane** to
`/smh-dev-task-tests`: keep the worktree and every commit, discard nothing.

⛔ **A fired eject RE-ARMS the plan-first gate in full** (`000-PLAN-FIRST-GATE.md`): the full lane
needs its own `implementation_plan.md`, `/smh-self-audit`, and the operator's literal `approved`
before another file is edited. An under-declared Step 1 is caught here by the diff, never by the
agent's memory of what it meant to touch.

Then **STOP here.** Do **NOT** merge to `main`, do **NOT** transition the ticket, do **NOT** prune the
branch. That is `/smh-close-task-merge-tree`, and **invoking it is the operator's per-merge
sign-off** — one invocation authorises exactly one merge, and it never carries forward to the next
task. Print: the plan link · the walkthrough link · the RED→GREEN evidence · the scope-check lines ·
the branch and its push state · anything still owed. Then hand back.

Optional additional input (the specific ask, a ticket key, or a repo): $ARGUMENTS
