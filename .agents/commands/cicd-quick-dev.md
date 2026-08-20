---
description: Fast-track dev flow on the real quick-dev engine (`bmad-quick-dev`, one-shot route) — clarify intent and FIX acceptance criteria, implement, then a mandatory tiered review gate (independent adversarial reviewer always; acceptance auditor + clean-code machine floor + scoped tests on code; link/anchor + SOP-currency on docs). Stops for human review. Carries an EJECT tripwire back to the full ①②③ lane.
platforms: [opencode, antigravity, claude, codex]
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

## Step 0.5 — Worktree (before the first edit)
Per `worktree-per-story`: run `git worktree list` under `PROJECT_ROOT`; reuse an existing
`claude/<JIRA-KEY>-<slug>` tree for this fix, else open one off the story's EPIC branch (`epic/<JIRA-KEY>-<slug>`).
No epic applies — a truly ad-hoc fix outside any sprint — then mirror `git-policy.md`'s chore lane
instead: a short-lived `chore/<JIRA-KEY>-<slug>` branch off `main`, **in its own worktree**. Echo the
case. Quick fixes are NOT exempt — this is what keeps them tangle-free, rollbackable, and landable
through the normal close-out.

⛔ **A worktree is not optional on either case, and this line used to say `no worktree`.**
`worktree-per-story` has required one for **every commit-producing lane** since SCC-62, and its lane
table names `chore/<JIRA-KEY>-<slug>` explicitly. Worse, the exemption that lets this command skip the
plan at all — `artifacts-always-first` § When to Skip, the `/cicd-quick-dev` bullet — is **conditional on the worktree/chore
branch existing**, so working without one voids this lane's own carve-out. Link the gitignored assets
into a fresh tree (`node_modules`, `.env`, `auth_keys`), or Step 3's scoped tests cannot run.

⛔ **This lane does not merge, and it never touches `main`.** Step 4 is the end: branch pushed, work
reported, and the landing is a **separate, operator-invoked act through a door**. Invoking a door IS
the sign-off; a spoken "looks good" is not, and no agent merges to `main` on its own initiative
(`git-policy.md` § The road to `main`, SCC-183). Which door exists depends on the repo:

| Lane | Door |
|---|---|
| story lane on `claude/*` | the epic branch, at close-out — `/cicd-update-sprint-memory`, then the epic ships via `/cicd-push-e2e` |
| chore lane in a **project repo** | ⚠ **there is none — state that and hand back** |

⛔ **There is no command-centre row, and that is not an omission.** This command binds
`smh-target-resolution.md` — exactly ONE project, **never the lobby** — so command-centre chore work
is unreachable from here by construction. It belongs to `/smh-quick-dev` or `/smh-quick-fix`, whose
door is `/smh-close-task-merge-tree`. Naming that door in a routing table an agent reads from a
`cicd-*` lane is an invitation to bind the lobby, which is the one thing target resolution forbids.

⚠ **The gap, recorded rather than filled:** `/cicd-push-e2e` ships an `epic/*` branch, and
`/smh-close-task-merge-tree` refuses a diff touching `backend/`, `frontend/`, `firebase/`,
`functions/`, `mobile/` or `.github/` and hands it to `/cicd-push-e2e` — so a project repo's ad-hoc
`chore/*` lane has **no close-out door of its own**. Report the pushed branch and the gap; **do not
invent a command to fill it, and do not merge by hand.** Closing it is its own decision, and its own
ticket.

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
refuses it. Never push `main`.

## Step 3 — ⭐ Review gate (mandatory — never skipped, never "assumed clean")
Runs **after** the work. **Pin the diff first, from command output** — `step-oneshot.md` writes no
`baseline_commit`, so "the diff since the baseline" names a scope nothing defines:

```bash
WORKTREE=<the tree Step 0.5 opened, or "$PROJECT_ROOT" when this lane reuses the checkout>
# ⛔ BIND IT. `git -C ""` does NOT error - it silently resolves against the cwd, and cwd
# resets to the shared main checkout between tool calls, so an unbound WORKTREE pins the
# diff of a tree that is not this lane's and reports normally (`worktree-per-story`
# §"cwd is not intent").
BASE_REF=origin/main                                  # ad-hoc chore lane
# ⛔ A STORY LANE FORKS FROM THE EPIC, NOT FROM main. `merge-base HEAD origin/main` on a
# `claude/*` branch returns where the EPIC left main, so the diff carries every sibling
# story already landed on the epic branch - other lanes' work, reviewed and reported as
# this one's. Name the epic the tree was cut from:
#   BASE_REF=origin/epic/<JIRA-KEY>-<slug>            # story lane
git -C "$WORKTREE" fetch origin --quiet
BASE=$(git -C "$WORKTREE" merge-base HEAD "$BASE_REF")
git -C "$WORKTREE" diff --name-only "$BASE"...HEAD       # committed
git -C "$WORKTREE" diff --name-only                      # plus uncommitted
git -C "$WORKTREE" diff --name-only --cached             # plus staged
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
| `HEAD_SHA` | `git -C "$WORKTREE" rev-parse HEAD`, taken **now** |
| `review_mode` | `full` **when you wrote the Step 1 ACs to a file** (below); `no-spec` only when you genuinely have no acceptance list |
| `STORY_FILE` | that AC file — required for `full`, and the thing the Acceptance Auditor reads |
| `ARTIFACT_DIR` | the Step 4 walkthrough's folder |
| `DEFERRED_WORK` | the project's `deferred-work.md`, when it has one |
| `lens_budget` | `standard` — the interactive budget; a human is sitting in front of this lane. **This command does not define the caps; step-01 of the engine does, once.** Naming nothing is not neutral: it silently selects the autopilot's budget (SCC-147) |
| `review_runtime` | `fan-out` or `inline` — **what you PROBED, never what you expect.** Try one throwaway subagent; if subagents are unavailable the engine runs inline and DROPS the Blind Hunter rather than faking it |

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
- Link + anchor check on every path and `#L` anchor touched.
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
- The **spec** the skill wrote is the working doc (it carries the Suggested Review Order).
- **Story lane only:** the skill syncs `sprint-status.yaml` and advances the story to **`review`** on its
  way out. That is the normal dev→review flip (`story-status-flip-contract`) — `done` stays yours. On the
  ad-hoc lane there is no story key, so the sync skips silently.
- Write a **thin `walkthrough.md`** in the owning `_artifacts/` store — story work →
  `epic_<E>/<story>/`; ad-hoc → `quick_fixes/quick-fix-<track>.<n>-<slug>/` (read that folder's
  `INDEX.md` for the next free number and append the row by hand; **create the folder + its `INDEX.md`
  if this is the repo's first quick fix** — the lobby has none yet, AviationChat does). It **links** the spec rather than
  restating it, and carries `## Task Checklist` → `## Evidence` (AC→evidence + pasted totals + SHA) →
  `## Code Review (<date>)` with the canonical **`Verdict: PASS|CONCERNS|FAIL|WAIVED @ <sha>`** line →
  `## Your Actions`. Post clickable Markdown links to every artifact in the chat.

## Step 4.5 — File the Dev Record on the ticket (AUTOMATIC, never ask)
This lane **closes its own branch**, and the ad-hoc chore lane never reaches
`/cicd-update-sprint-memory` at all — so this is the only place its knowledge gets recorded. Before
SCC-49 it died in the walkthrough. Runs AFTER Step 4 so the walkthrough it points at exists. The key is
already in hand: the story's `jira_key:` frontmatter on the story lane, or the `<JIRA-KEY>` in the
`chore/<JIRA-KEY>-<slug>` branch name on the ad-hoc lane.

```bash
python3 .agents/scripts/jira_feed.py devrecord --key <JIRA-KEY> --story <THE ONE SLUG> \
       --project <PROJECT> --stage quick-dev --walkthrough <the Step 4 walkthrough> \
       --outcome "<what shipped, one line>" --verdict "<the Step 3 verdict>" \
       --decision "<a ruling made while fixing>" --pitfall "<what nearly bit>" \
       --followon "<only what Step 3 deferred against a NAMED blocker - never a pile>" --apply
```

**Exactly one Dev Record per ticket.** The script finds an existing record and UPDATES it in place, so
a story that later goes through `/cicd-update-sprint-memory` ends with one current record instead of
two partial ones — **never pass `--append-new` here.**

⛔ **`--story` is the fork risk, and `<id-or-slug>` was the fork.** `devrecord` decides
update-vs-create from the **slug**, never from `--key`, so two surfaces spelling one lane two ways
give one ticket two records — and `check` then blesses the pair as "two lanes". That is AVCH-59,
measured 2026-08-15. `/cicd-update-sprint-memory` passes `--story <id>`, meaning the **BMAD story id**,
so this step must pass **the same story id, character for character** — never the branch slug, never a
free-text description. On the ad-hoc lane there is no story id: pass the **branch slug** from
`chore/<JIRA-KEY>-<slug>`, and pass that identical string at every later surface.
⚠ **The durable fix is not here.** On the `smh-` side the slug is read from the lane's `task.yaml`
so no one types it twice, and **no `cicd-*` command writes a `task.yaml` at all** (grep: zero hits) —
so `devrecord`'s anti-fork default cannot fire on this side and the guard is inert. Recorded, not
fixed here: it is a change to the story lane's manifest, and it belongs with the close-out rebalance.

**`jira_feed.py devrecord` reads the ticket back** and exits 2 if the comment is not there; a non-zero exit means the record did NOT land, so report that rather than
success. No ticket key at all (a fix outside any ticket) → say so in the Done report and skip;
**never invent a key.** Full acli reference: `.agents/rules/jira.md`.

## Done
Stop here. Do **NOT** run `/cicd-update-sprint-memory`, never land on the epic branch (close-out's job),
never touch `main`. Display the spec path, the walkthrough link, the key changes, and the review-gate
output, then invite Daniel to review and run `/cicd-update-sprint-memory` himself when satisfied.
