---
description: Fast-track dev flow on the real quick-dev engine (`bmad-quick-dev`, one-shot route) — clarify intent and FIX acceptance criteria, implement, then a mandatory tiered review gate (independent adversarial reviewer always; acceptance auditor + clean-code machine floor + scoped tests on code; link/anchor + SOP-currency on docs). Stops for human review. Carries an EJECT tripwire back to the full ①②③ lane.
platforms: [opencode, antigravity, claude, codex, zoo]
---

# /cicd-quick-dev — Fast-Track Development (fast lane, guarded)

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push `main`, never force-push
> - `.agents/rules/artifacts-always-first.md` — **§ When to Skip, the `/cicd-quick-dev` bullet, covers this lane: invoking this
>   command IS the "skip the plan" instruction.** The closing `walkthrough.md` is NOT skipped.
> - `.agents/rules/000-PLAN-FIRST-GATE.md` — the gate this command is exempt from **only while the
>   work stays in this lane**; a fired EJECT (Step 1.5) re-arms it in full
> - `.agents/rules/worktree-per-story.md` — a worktree for every commit-producing lane, `chore/*`
>   included (SCC-62); §"cwd is not intent" is why Step 0 pins the repo from command output
> - `.agents/rules/tests-must-gate-for-real.md` — Step 3's gate goes vacuously green three ways: an
>   empty diff, a missing tool reported as a skip, and a piped exit code
> - `.agents/rules/work-consolidation.md` — where a finding too big for this lane GOES: its own
>   ticket → an open thematic parent → the open rolling ticket → mint. Never a pile in the walkthrough
> - `.agents/rules/code-standards.md` §6.5 — **disposition**: you are the assessor, not the
>   lens. All three YES to act — is it REAL (a concrete failure, not a *"may be"*) · does it
>   change BEHAVIOUR · is it in THIS diff. "It's cheap" is not a reason
> - `.agents/rules/reproduce-before-you-fix.md` — **when the quick fix is a BUG fix**: the five gates
>   (reproduce → minimize → pin a test seen red → falsify one hypothesis at a time → minimal fix → prove
>   by reverting). Its G3 stop conditions fire the EJECT tripwire below.

Thin orchestrator for SMALL work — a fix, a docs/config change, a task that does not earn the full
development pipeline.

**Accuracy over speed.** What this lane drops is the *pipeline* — the ATDD red phase, the full suite, the
three-reviewer panel, the revert-and-re-derive loops. It does **not** drop the rigour: a worktree,
acceptance criteria fixed before the code, an eject tripwire, an independent adversarial review, an
objective machine floor, and a human gate at the end.

> Flow position: worktree → `bmad-quick-dev` (one-shot route) → review gate → [STOP for human review;
> close-out is the human's].

## Step 0 — Resolve the target project (FIRST — before any other step)
Bind the target per `.agents/rules/smh-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override → `.agents/active-project.txt` → else **STOP and ask** — never guess, never operate on the
lobby. Set `PROJECT_ROOT` and **echo exactly** `Target: Projects/<name>` before any work; every path and
child tool call resolves under `PROJECT_ROOT`.

## Step 0.5 — Key, worktree, branch, ticket (before the first edit)

**Pin the ticket key you are working, before any tool has answered anything.** Every branch and every
commit must carry the repo's key (`.agents/jira.conf`), or the armed `commit-msg` hook refuses the
commit. Story lane: the story's `jira_key:` frontmatter. Ad-hoc lane: the ticket you were handed —
read its `ACCEPTANCE` block, it is Step 1's first AC source there:

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
local ref is a cache a sibling lane has already moved past:

```bash
L=$(pwd)                                                     # the lobby — pin it BEFORE any cd (command-shape.md §Absolute fills)
cd "$PROJECT_ROOT" && git worktree list                      # reuse this fix's tree if it exists
cd "$PROJECT_ROOT" && git fetch origin                       # ⛔ the base is origin/…, never a bare local ref
# story lane — off the story's EPIC branch:
cd "$PROJECT_ROOT" && git worktree add .claude/worktrees/<slug> -b claude/<KEY>-<slug> origin/epic/<KEY>-<epic-slug>
# ad-hoc lane — no epic applies (a truly ad-hoc fix outside any sprint): git-policy.md's chore lane, off main:
cd "$PROJECT_ROOT" && git worktree add .claude/worktrees/<slug> -b chore/<KEY>-<slug> origin/main
cd "$PROJECT_ROOT"/.claude/worktrees/<slug> && git branch --unset-upstream   # an origin/… start-point sets upstream to the BASE branch
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
cd "$PROJECT_ROOT"/.claude/worktrees/<other-slug> && git diff --name-only <that lane's base>...HEAD   # origin/epic/<…> for a story tree, origin/main for a chore tree
cd "$PROJECT_ROOT"/.claude/worktrees/<other-slug> && git status --short
```

Any file in both their set and your intended set is a **landing-order dependency**. Say which lane
should land first and what happens to your work if it does not. Carry it into the walkthrough's
`## Evidence`.

⛔ **A worktree is not optional on either case, and this line used to say `no worktree`.**
`worktree-per-story` has required one for **every commit-producing lane** since SCC-62, and its lane
table names `chore/<JIRA-KEY>-<slug>` explicitly. Worse, the exemption that lets this command skip the
plan at all — `artifacts-always-first` § When to Skip, the `/cicd-quick-dev` bullet — is **conditional on the worktree/chore
branch existing**, so working without one voids this lane's own carve-out.

⛔ **This lane does not merge, and it never touches `main`.** Step 4 is the end: branch pushed, work
reported, and the landing is a **separate, operator-invoked act through a door**. Invoking a door IS
the sign-off; a spoken "looks good" is not, and no agent merges to `main` on its own initiative
(`git-policy.md` § The road to `main`, SCC-183). Which door exists depends on the repo:

| Lane | Door |
|---|---|
| story lane on `claude/*` | the epic branch, at close-out — `/cicd-close-story-merge-tree`, then the epic ships via `/cicd-push-e2e` |
| chore lane in a **project repo**, diff reaches a deployable path (`backend/ frontend/ firebase/ functions/ mobile/ .github/`) | `/cicd-push-e2e` — `ship_preflight.py` admits the `chore/*` under the **light gate** (SCC-211); nothing deployable → it refuses and names the PR door |
| chore lane in a **project repo**, nothing deployable in the diff | `/smh-close-task-merge-tree Projects/<name>` — the PR door, with the project named in `$ARGUMENTS`. `task_preflight.py` derives `LANE: LOCAL`, and it opens the PR and STOPS (`git-policy.md` § The write gate, `main` row) |

⚠ **Which door is derived from the DIFF, not chosen:** both doors read the same deployable-path list
and refuse each other's lane, so the branch decides. Project repos publish no `main-write-gate`, so
the PR merge there is the operator's click with no server-side gate — still the operator's, still
never yours.

⛔ **There is still no command-centre row, and that is not an omission.** This command binds
`smh-target-resolution.md` — exactly ONE project, **never the lobby** — so command-centre chore work
is unreachable from here by construction; it belongs to `/smh-quick-dev` or `/smh-quick-fix`. The
`smh-` door appears above **only with `Projects/<name>` as its argument** (its Step 0 takes a
`Projects/` path and the subject stays `PROJECT_ROOT`): a bare invocation binds the lobby, which is
the one thing target resolution forbids.

⭐ **The gap SCC-205 recorded here is CLOSED (SCC-211).** This paragraph used to say a project repo's
ad-hoc `chore/*` lane had no door of its own. `ship_preflight.py` now admits a deployable `chore/*`
under the light gate and refuses the rest by name, and `task_preflight.py` takes the non-deployable
half as `LANE: LOCAL` — two doors, selected by the diff. Report the pushed branch and the door its
diff selects; **still never merge by hand.**

## Step 0.7 — Probe the review runtime, and record it (SCC-177)

Ask this runtime whether it can fan out to subagents — do not answer from what usually happens,
because a headless pipeline or a platform with no subagent tool makes the answer `inline`, and both
are invisible until a lens fails to launch three steps later. The answer goes into the walkthrough
header Step 4 writes, on its own line, above everything else, and into the engine's `review_runtime`
input in Step 3:

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

⛔ **Here, not at Step 4 — the probe must precede the review it describes.** Recorded afterwards it is
read off the roster that already exists, which makes the check circular: the header can only ever
agree with the states it was derived from. Recorded here it is an independent claim, and
`walkthrough_roster.py` blocks the close-out when the roster disagrees with it (`inline` + a lens
reporting `ok` is the contradiction it catches).

## Step 1 — Clarify, fix the ACs, and route
Invoke the **`bmad-quick-dev`** skill with `$ARGUMENTS`. Its `step-01-clarify-and-route` does the
intent check, story-key resolution, epic-context load, and the version-control sanity check.

**⊕ Before leaving Step 1, capture an explicit acceptance-criteria list** — 2–6 checkable statements,
echoed in the chat. This is the accuracy baseline: the one-shot route writes its spec *after* the code,
so without this there is nothing to audit the diff against. If the intent will not reduce to checkable
ACs, that is not a quick fix — eject.

**Do NOT create a story file on the ad-hoc lane.** A story id / epic story keeps BMAD's normal story
handling; an ad-hoc fix mints **no story file and no epic key** (`artifacts-always-first` §2 quick-fix
bucket) — hanging one off a finished epic silently reopens it.

## Step 1.5 — ⛔ EJECT TRIPWIRE (check here, and again as you go)
**STOP and hand off to the full lane (`/cicd-write-story-tests` ①) if any of these is true:**
- Step 1 routes to **plan-code-review** rather than one-shot. The skill judges blast radius; "this needs
  the planning route" IS the eject signal — it is a truer measure than counting files.
- The change touches a **protected surface** — auth/tenancy walls, payments, PII handling, DB schema or
  security rules, a cross-boundary API/SSE contract. Risk, not size, decides this one.
- The intent will not reduce to checkable ACs (Step 1), or a review finding in Step 3 is bigger than a
  trivial patch.

Report the one-line reason; keep the worktree and everything written, discard nothing.

⛔ **A fired eject RE-ARMS the plan-first gate** (`artifacts-always-first.md` § When to Skip, the `/cicd-quick-dev` bullet — the one
`000-PLAN-FIRST-GATE.md` defers to rather than restating).
Invoking this command IS the "skip the plan" instruction — but only for as long as the work stays in
this lane. The moment the tripwire fires, the exemption is spent: the full lane needs an
`implementation_plan.md` and the operator's literal `approved` before another project file is
modified. Ejecting is not a licence to keep editing under the fast lane's carve-out.

## Step 2 — One-shot implementation
Let the skill's `step-oneshot.md` run: implement the clarified intent directly, then its own review and
spec trace. Commits happen **inside the worktree, explicit paths only** — never `git add -A` — and every
commit subject leads with the repo's Jira key from `.agents/jira.conf`, or the armed `commit-msg` hook
refuses it. ⛔ **Backticks in `-m "…"` EXECUTE.** A message quoting a shell command runs it. Use
`git commit -F <file>` whenever the message contains a backtick. Never push `main`.

## Step 3 — ⭐ Review gate (mandatory — never skipped, never "assumed clean")
Runs **after** the work. **Pin the diff first, from command output** — `step-oneshot.md` writes no
`baseline_commit`, so "the diff since the baseline" names a scope nothing defines:

```bash
WORKTREE=<the tree Step 0.5 opened, or "$PROJECT_ROOT" when this lane reuses the checkout>
# ⛔ BIND IT. `cd ""` exits 0 without erroring (bash and zsh both), so the && chain runs against the cwd, and cwd
# resets to the shared main checkout between tool calls, so an unbound WORKTREE pins the
# diff of a tree that is not this lane's and reports normally (`worktree-per-story`
# §"cwd is not intent").
BASE_REF=origin/main                                  # ad-hoc chore lane
# ⛔ A STORY LANE FORKS FROM THE EPIC, NOT FROM main. `merge-base HEAD origin/main` on a
# `claude/*` branch returns where the EPIC left main, so the diff carries every sibling
# story already landed on the epic branch - other lanes' work, reviewed and reported as
# this one's. Name the epic the tree was cut from:
#   BASE_REF=origin/epic/<JIRA-KEY>-<slug>            # story lane
cd "$WORKTREE" && git fetch origin --quiet
BASE=$(cd "$WORKTREE" && git merge-base HEAD "$BASE_REF")
cd "$WORKTREE" && git diff --name-only "$BASE"...HEAD       # committed
cd "$WORKTREE" && git diff --name-only                      # plus uncommitted
cd "$WORKTREE" && git diff --name-only --cached             # plus staged
```

**An empty set is a STOP, not a pass** (`tests-must-gate-for-real`): a gate that reads nothing
reports green having checked nothing. Tiered by what that set touched:

**Every lane — the house review engine, not a bare lens**
Invoke the **`code-review-engine`** skill, the same engine `/cicd-code-review` and `/smh-code-review`
run. It fans the lenses out into their own clean contexts (that is what zeroes the builder's bias —
an agent reviewing its own reasoning anchors on it), verifies what they find, then triages.

| Input | What you pass |
|---|---|
| `REPO` | `PROJECT_ROOT` from Step 0 |
| `WORKTREE` | the tree Step 0.5 opened |
| `DIFF` | the set pinned above, taken in that worktree |
| `HEAD_SHA` | `cd "$WORKTREE" && git rev-parse HEAD`, taken **now** |
| `review_mode` | `full` **when you wrote the Step 1 ACs to a file** (below); `no-spec` only when you genuinely have no acceptance list |
| `STORY_FILE` | that AC file — required for `full`, and the thing the Acceptance Auditor reads |
| `ARTIFACT_DIR` | the Step 4 walkthrough's folder |
| `DEFERRED_WORK` | the project's `deferred-work.md`, when it has one |
| `lens_budget` | `standard` — the interactive budget; a human is sitting in front of this lane. **This command does not define the caps; step-01 of the engine does, once.** Naming nothing is not neutral: it silently selects the autopilot's budget (SCC-147) |
| `review_runtime` | `fan-out` or `inline` — **the Step 0.7 answer, never what you expect.** If subagents are unavailable the engine runs inline and DROPS the Blind Hunter rather than faking it |

⛔ **`no-spec` DOES NOT AUDIT YOUR ACs — it drops that lens entirely.** step-01 § *Skipped-by-mode
is not the same as dead*: the Acceptance Auditor runs in `review_mode: full` **only**, and a
spec-less review correctly reports `4/4` with `acceptance-auditor` on `lenses_na`. So passing
`no-spec` and expecting the Step 1 ACs to be checked gets a walkthrough that records an acceptance
audit which never happened. **Write the Step 1 AC list to a file in `ARTIFACT_DIR` and pass it as
`STORY_FILE` with `review_mode: full`** — on this lane that list IS the spec, exactly as the plan is
the spec on the Task lane. With no list, `no-spec` is honest and the acceptance check is yours by
hand, below.

**Record the roster the engine returns, all four fields** — `review-runtime`, `lenses_run`,
`lenses_counted: <n>/<applicable>`, `lenses_na` — **plus the two record lines (SCC-231/233):**
the engine's `dispositions:` line verbatim, and a `drift:` line reading
`drift: no Declared Change Set — plan-exempt lane (the eject re-arms the plan gate)` — this lane
has no plan to reconcile BY DESIGN, and `walkthrough_roster.py` blocks a lane that says nothing. A dropped Blind Hunter is legal and a silent one is
not: `lenses_na` is the only place a drop can land, so a review that omits it is indistinguishable
from one where every lens ran. **`4/4` is never written `4/5`** — the denominator is what was
*applicable*, not the roster's length.

⛔ **This replaced a bare `bmad-review-adversarial-general` call.** That is not "less BMAD" — the
engine *runs* the BMAD lenses (the adversarial reviewer under a hunter contract deliberately starved
of context, beside `bmad-review-edge-case-hunter`) with a roster, verification and triage that a bare
call has none of. A hand-rolled review reports the same verdict SHAPE as a full one and is
indistinguishable from it in the artifact.

**Code touched — add all three**
- **Acceptance auditor** — the diff against the **Step 1 ACs**. Each AC → where it is satisfied; anything
  in the diff beyond the ACs is drift: cut it or name why it stays.
- **`/cicd-clean-code-audit`** — the objective machine floor (ruff / eslint / pyrefly / tsc). This half can
  **FAIL**; the judgment half caps at CONCERNS.
- **Scoped tests** — the test file(s)/suite covering the touched module, and the **WHOLE** endpoint/module
  suite when a shared handler changed (a new read on a shared endpoint silently breaks sibling tests).
  Paste the **actual** output. Bug fixes add ONE pinning regression test.

**Docs / config only — no lint floor (there is nothing to lint)**
- Link + anchor check on every path and `#L` anchor touched. ⛔ **Prose here on purpose.**
  `check_links.py` is a LOBBY script and a thin project does not carry it — a project's
  `.agents/scripts/` holds only `git-hooks/` and `tests/`. The `smh-*` doors name the command
  because they run in the command centre; naming it here would cite a file that is not on the
  target (SCC-285).
- **SOP-currency check** — a usage-surface change (`.agents/commands/`, `.agents/rules/`,
  `.agents/scripts/`, git hooks, root `AGENTS.md`) must move
  `docs/_scc_sops_prds/workflows_testing_SOP.md` in the same commit, or the armed gate
  rejects the commit.

⛔ **You are the ASSESSOR, not the lens** (`code-standards` §6.5). Every lens is told to be
exhaustive and grades its own work, so it will always return something — that is raw material, not a
work queue. Three questions, all three YES to fix: **is it REAL** (a concrete failure, not a *"may
be"*) · **does it change BEHAVIOUR** · **is it in THIS diff**. "It's cheap" is not a reason.

Classify what survives **patch / defer / reject**; auto-fix patches NOW, in this lane; drop noise
with a one-line reason. **`defer` is not a parking lot** (operator rulings 2026-08-15): a finding may be
deferred ONLY against a named structural blocker — another live lane owns the file, the fix lives in
another repo, or it waits on a decision the operator has not taken — and the deferred-work entry names
that blocker; "pre-existing" or "bigger than this lane" is not one. A finding worth fixing with no
blocker is a patch, or it is the EJECT tripwire (Step 1.5) firing. **Anything bigger than a trivial
patch → HALT** (and see Step 1.5). Re-run the affected check after applying fixes and paste the output.

## Step 4 — Artifacts, then stop
- **Ad-hoc lane, FIRST: settle `close_command` in `task.yaml`.** The diff exists now, so the door is
  a read rather than a guess. Run `cd "<the tree>" && git diff --name-only origin/main...HEAD`, match it
  against the deployable-path list in Step 0.5's door table, and **rewrite the `TBD`** —
  `cicd-push-e2e` if anything deployable is in the set, `smh-close-task-merge-tree` if not. The
  close-out reads that field; leaving it `TBD` sends the operator to a door the preflight will refuse.
- The **spec** the skill wrote is the working doc (it carries the Suggested Review Order).
- **Story lane only:** the skill syncs `sprint-status.yaml` and advances the story to **`review`** on its
  way out. That is the normal dev→review flip (`story-status-flip-contract`) — `done` stays yours. On the
  ad-hoc lane there is no story key, so the sync skips silently.
- Write a **thin `walkthrough.md`** in the owning `_artifacts/` store — story work →
  `epic_<E>/<story>/`; ad-hoc → `quick_fixes/quick-fix-<track>.<n>-<slug>/` (read that folder's
  `INDEX.md` for the next free number and append the row by hand; **create the folder + its `INDEX.md`
  if this is the repo's first quick fix** — the lobby has none yet, AviationChat does). It **links** the spec rather than
  restating it, and carries `review-runtime:` (the header from Step 0.7, one line) →
  `## Task Checklist` → `## Evidence` (AC→evidence + pasted totals + SHA) →
  `## Code Review (<date>)` with the canonical **`Verdict: PASS|CONCERNS|FAIL|WAIVED @ <sha>`** line →
  `## Your Actions`. Post clickable Markdown links to every artifact in the chat.

## Step 4.5 — File the Dev Record on the ticket (AUTOMATIC, never ask)
This lane **closes its own branch**, and the ad-hoc chore lane never reaches
`/cicd-close-story-merge-tree` at all — so this is the only place its knowledge gets recorded. Before
SCC-49 it died in the walkthrough. Runs AFTER Step 4 so the walkthrough it points at exists. The key
was **pinned at Step 0.5 as `EXPECTED_KEY`** and is read back from there — the story's `jira_key:`
frontmatter on the story lane, the ad-hoc lane's `task.yaml` on the other. Never re-derive it here.

```bash
python3 .agents/scripts/jira_feed.py devrecord --key <JIRA-KEY> --story <THE ONE SLUG> \
       --project <PROJECT> --stage quick-dev --walkthrough <the Step 4 walkthrough> \
       --outcome "<what shipped, one line>" --verdict "<the Step 3 verdict>" \
       --decision "<a ruling made while fixing>" --pitfall "<what nearly bit>" \
       --followon "<only what Step 3 deferred against a NAMED blocker - never a pile>" --apply
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

## Done
Stop here. Never land on the epic branch (close-out's job), never touch `main`, never transition the
ticket. Display the spec path, the walkthrough link, the key changes, the review-gate output, and the
branch + its push state. Then invite the operator to review and invoke **the door Step 0.5's table
names for this lane** — `/cicd-close-story-merge-tree` on the story lane; `/cicd-push-e2e` or
`/smh-close-task-merge-tree Projects/<name>` on the ad-hoc lane, by what the diff touched. Invoking it
IS the sign-off.
