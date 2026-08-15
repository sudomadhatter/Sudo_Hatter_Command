# Implementation Plan — SCC-155 — plan-the-whole-Task + labeling surface v2 + user-tasks close-out

**v2 (2026-08-14) — revised on the operator's correction:** `/cicd-parallel-check` was the first
try and RETIRES once its replacements are green (logic reused, command deleted); the smh labeler's
unit is **a parent Task with all its Subtasks planned**, not the queue; and a new one-shot planner
(the Task lane's analog of "write all the stories first") plans the whole Task + subtasks, updates
the tickets, cuts the worktrees, then runs the parallel labeling. v1's queue-default (old D2) is
CUT.

- **Ticket:** SCC-155 (Task, no ACCEPTANCE block — checkable list derived + echoed for confirmation)
- **Repo:** `Sudo_Hatter_Command` (lobby) — all surfaces lobby-owned · **Branch:**
  `chore/SCC-155-label-tasks` · worktree `.claude/worktrees/label-tasks`
- **Sibling lanes:** none live at plan time

## The evolved shape (what this lane builds)

The BMAD side already has its sequence: *write all the epic's stories* (`/cicd-create-epic-sprint`,
①) → *label the set* → dev lanes. This lane gives the Task side the SAME sequence and evolves the
labeling surface to match how the process has grown:

| | BMAD / avch side | Task / smh side |
|---|---|---|
| plan the whole set | `/cicd-create-epic-sprint` + ① (exists) | **`/smh-plan-task` (NEW — cluster B)** |
| label the set | **`/cicd-label-tasks` (NEW — replaces `/cicd-parallel-check`)** | **`/smh-label-tasks` (NEW)** |
| dev one lane | `/cicd-dev-story-tests` | `/smh-quick-dev` (reuses the cut tree + plan) |
| close the set | `/cicd-merge-epic-workingtrees` | `/smh-merge-multiple-workingtrees` / `/smh-close-task-merge-tree` |

## Acceptance list (echoed for operator confirmation)

1. **A1 — one labeling engine, two commands.** `parallel_check.py` evolves into
   `.agents/scripts/label_tasks.py` (git mv — history preserved; set math, acli plumbing, stamp
   mechanics, staleness check reused, never copied): **story mode** serving `/cicd-label-tasks`
   (BMAD epic → grounded stories, umbrella/Done exclusions as today) and **task mode** serving
   `/smh-label-tasks` (parent `Task` → `Subtask` children; grounding ladder branch-diff →
   subtask plan → ticket text; ambiguity counts as an edit — fail toward 🔒). Both stamp
   **`parallel-ok` AND `quick-dev`** (add to winners/eligible, strip from the rest, preserve
   unmanaged labels; absent `quick_dev` key in a touch-set = label untouched) and post the stamped
   verdict comment on the parent (both modes have one now). Proven by
   `tests/test_label_tasks.py` (the renamed + extended `test_parallel_check.py`), RED first for
   every NEW behavior; existing behavior rides the rename green (characterization, said plainly).
2. **A2 — `/smh-plan-task` plans the whole Task in one shot.** New command: resolve the parent
   Task → propose the subtask breakdown and **STOP for the operator's go (SCC-119 guardrail —
   propose, never mint unbidden)** → mint `Subtask`s → per subtask: cut
   `chore/<SUBKEY>-<slug>` worktree + link assets, write its `implementation_plan.md` into that
   lane, run `/smh-self-audit` on it, commit + push the lane branch (unpushed = stranded on one
   machine), update the ticket (description gains the checkable list + the plan's in-tree path —
   the tree stays the single source of truth) → finish by invoking `/smh-label-tasks` on the
   parent and print the parallel table. Checkable: after a run, every subtask has a plan committed
   on its own pushed branch, a ticket carrying it, and a labeling verdict.
3. **A3 — batch approval is recorded evidence, never self-written.** The planner ends at a STOP
   presenting all plans + audit verdicts + the parallel table; when the operator approves the set,
   their **verbatim message** is recorded into each plan's audit section (the SCC-37 quote
   pattern). `000-PLAN-FIRST-GATE.md` gains a narrow clause: a recorded batch approval at
   `/smh-plan-task` covers exactly the plans it lists, and `/smh-quick-dev` on such a lane skips
   straight to Step 2 (RED) **iff the plan is unchanged since the recorded approval** (any edit →
   the gate re-arms). Checkable by reading the rule + the quick-dev step + a recorded section.
4. **A4 — open operator actions hold the ticket out of Done** (unchanged from v1). `jira_feed.py
   finish`: unchecked `- [ ]` under `## Your Actions` → post "User tasks" comment + `user-tasks`
   label + status ladder `Awaiting Review` → `In Review` (neither installed → label alone), refuse
   `Done`, distinct exit; none open → `Done` as today. **Fail closed**: missing walkthrough or
   missing section = REFUSAL, its own exit code. Dry-run default, `--apply` to write, `--yes` on
   every transition. Both close-out docs route `Done` through it and name the auditable escape
   (flip to `- [x]`, re-run). Proven in `test_jira_feed.py`, RED first.
5. **A5 — the retirement is complete, LAST.** After A1–A2 are green: `cicd-parallel-check.md`
   deleted; its four doors gone after `/smh-sync-agents`; `commands/INDEX.md` + `scripts/INDEX.md`
   rows updated; live references repointed — `cicd-write-story-tests.md`, `jira.md` (label table:
   writers of `parallel-ok`/`quick-dev` become the two new commands; ① keeps minting `quick-dev`
   at pickup for unswept stories), `smh-target-resolution.md` (the variance note),
   `000-PLAN-FIRST-GATE.md`, the SOP. Checkable: the reference sweep that found 28 files returns
   only history (`_artifacts/` walkthroughs) and the memory store. Memory-store rows
   (`parallel-ok-is-a-set-property.md`, MEMORY.md index) are READ-ONLY outside the memory flows —
   listed in MY walkthrough's Your Actions as a `- [ ]` for the operator/memory-audit.
6. **A6 — documented + green.** SOP updated in the same commits (armed gate); suite green via
   `gate_receipt.py`; mutation sweep declared from the diff, one pass, restore in a trap.

## Design decisions (correctable at the gate)

- **D1 — names:** `/cicd-label-tasks` + `/smh-label-tasks` (the ticket's "/(tag)-label-tasks";
  one name shape across families even though the cicd units are stories — the doc says so) and
  `/smh-plan-task` for the planner (subject = the whole Task; rename freely).
- **D2 (v2) — the smh labeling unit is a parent Task's Subtask set.** Comment + staleness stamp on
  the parent Task, exactly like the epic side. No queue mode, no bare `--keys` — the v1 audit
  called them considered scope; the correction settles it.
- **D3 — `quick-dev` on SCC subtasks** = small enough for one light `/smh-quick-dev` lane
  (checkable acceptance derivable, no further breakdown, no deployable paths). Agent judgment with
  an evidence line, never a parser's.
- **D4 — story-side `quick-dev` guideline** (in `/cicd-label-tasks` Step 2): grounded + small
  touch-set (≲3 source files, no new subsystem) + risk P2/P3 where scored + no cross-story
  `imports` edge. The labeling pass is authoritative when run; ① still mints at pickup.
- **D5 — walkthrough contract** (A4): unchecked `- [ ]` under `## Your Actions` is the whole
  contract — convention written into `smh-quick-dev.md` Step 5 + SOP; prose never holds a ticket.
- **D6 — status ladder**: attempt-and-fall-through; a missing status is "not installed", never an
  error. Installing `Awaiting Review` on SCC/AVCH is a Jira-UI operator action (a `- [ ]`).
- **D7 — planner cuts trees at plan time** (the correction's ask). Consequence, named: a 🔒 lane
  started days later sits on a stale base — its `/smh-quick-dev` run absorbs `main` at pickup
  (line added to that command); trees never travel machines (`/cicd-park` already covers).
- **D8 — engine rename over new-file:** `git mv parallel_check.py label_tasks.py` + extend. One
  engine, one test file, no drift twins; the sweep (28 files) is sized and step 9 owns it.

## Steps

| # | Step | Proves | RED instrument (FIRST) |
|---|---|---|---|
| 1 | `git mv` engine + test; extend tests: task-mode enumeration (Subtask children), task grounding ladder + fail-toward-🔒, `quick_dev` stamp add/strip/absent-key-untouched, parent comment in task mode | A1 | new cases RED (task mode + quick-dev absent); rename rides green, labeled characterization |
| 2 | `label_tasks.py`: task mode + `quick_dev` carry-through (story mode untouched except stamp generalization) | A1 | step 1 GREEN |
| 3 | `test_jira_feed.py` new cases (v1 step 5 list: hold/close/ladder/fail-closed/dry-run/`--yes`) | A4 | RED — verb absent |
| 4 | `jira_feed.py finish` | A4 | step 3 GREEN |
| 5 | `smh-label-tasks.md` + `cicd-label-tasks.md` command docs (charter, MANDATORY RULES, grounding tables, staleness `check`) + INDEX rows | A1 | `workflow_lint.py --toolkit-only` RED on missing doors/INDEX before sync |
| 6 | `smh-plan-task.md` command doc (breakdown-STOP → mint → per-subtask plan/audit/tree/push/ticket → invoke labeler → batch-approval STOP with verbatim recording) + INDEX row | A2, A3 | lint RED before sync |
| 7 | `000-PLAN-FIRST-GATE.md` narrow batch clause + `smh-quick-dev.md` (Step 0.5 reuse-tree absorb-main line · Step 1.5 recorded-batch-approval path · Step 5 checkbox convention) | A3, D5, D7 | inspection against the rule text; lint link checks |
| 8 | Close-out docs route `Done` through `finish` + escape hatch (both files) | A4 | inspection + the step-3 tests |
| 9 | RETIREMENT: delete `cicd-parallel-check.md`, repoint the live references (①, `jira.md`, `smh-target-resolution.md`, `000`, SOP), INDEX rows | A5 | re-run the sweep — only history + memory rows remain |
| 10 | `/smh-sync-agents` (new doors emitted, retired doors REMOVED) + SOP section | A5, A6 | lint exits 0; `sop_currency` green |
| 11 | Suite via `gate_receipt.py` on clean tree; declared mutation sweep | A6 | receipt + mutant table in walkthrough |

## Sequencing — ONE lane, no subtasks (operator ruling, this session: "no sub task we need to one
shot this")

Clusters: **A** = labeling engine + two label commands (steps 1–2, 5) · **B** = planner + batch
rule (6–7) · **C** = finish seam (3–4, 8) · retirement (9) last, per the correction. B invokes A's
command; retirement needs A green; C is independent (shares only the SOP ledger). All of it lands
on `chore/SCC-155-label-tasks` in this lane, committed cluster-by-cluster in that order. Step 1.6's
question is pre-answered by the ruling — nothing gets minted; the clusters stay checklist lines
here. (The v2 audit's proportionality flag is settled the same way: the size is accepted
explicitly, and the mitigations are the cluster-ordered commits + the per-cluster RED→GREEN
evidence trail.)

## Out of scope

- The cicd-side user-tasks seam (`/cicd-update-sprint-memory`) — follow-on if wanted.
- Board columns (`Awaiting Review`) — Jira UI, operator-only.
- Memory-store edits — read-only law; handed to the operator/memory-audit at close.
- Any deployable path — none; tripwire re-checked each step.

## Risks

- `acli … edit --labels` REPLACES the set — every writer preserves unmanaged labels (pinned by tests).
- The 000 rule edit is the highest-blast-radius line in the lane — the clause must be NARROW
  (batch approval exists only as a recorded verbatim quote covering listed plans, re-armed by any
  plan edit) or the plan-first gate erodes.
- Two close-out docs duplicate the Step-4 shape — one commit covers both or the multi-lane variant
  writes `Done` over open user tasks.
- Board-unreachable vs status-not-installed stay distinguishable in `finish` (exit-4 discipline).
- Retirement leaves a live caller behind (the SCC-63 lesson) — step 9's proof is the re-run sweep,
  not belief.

## Self-Audit (v1, 2026-08-14 — pre-correction; kept as record)

Ran FULL against the v1 plan (three clusters, queue-default smh labeler, parallel-check extended
not retired). Verdict was **GO** with four findings, all baked forward into v2: INDEX rows
(→ steps 5–6), `finish` fail-closed contract (→ A4), the auditable escape hatch (→ step 8),
dry-run default (→ A4). Phase 1/2/3 detail superseded by v2 below where the correction changed the
ground; the unchanged cluster-C analysis stands.

## Self-Audit v2 (2026-08-14 — post-correction)

**Mode:** PRE-WORK · **FULL** (now also edits `000-PLAN-FIRST-GATE.md` — the strictest rule in the
repo — plus a retirement). Subject re-pinned: `Repo: label-tasks (worktree) | Branch:
chore/SCC-155-label-tasks`.

- **Phase 0** — change set re-named (see steps); checkable list A1–A6 re-fixed, traceability both
  directions re-walked (every step ↔ an item; retirement gained its own item so it cannot silently
  drop). Lane check: still no deployable path. ✅
- **Phase 1** — the retirement sweep is MEASURED: 28 files reference the old name; live surfaces =
  1 command + 4 doors + 2 INDEXes + 3 rules + ① + SOP; the rest is history (stays) and the memory
  store (read-only → operator hand-off). Doors are generated, so delete-then-sync removes them —
  hand-deleting is the drift trap. `000-PLAN-FIRST-GATE.md` referencing parallel_check was found
  ONLY by the sweep — belief said it wouldn't. ✅
- **Phase 2** — tripwires re-walked: **three new commands** where v1 had one → each traces to an
  acceptance item the operator's correction dictated (planner = the correction's explicit ask; two
  labelers = the "(tag)-label-tasks" pair; net command count +2 after the retirement). The 000
  clause is the one true scope-add → justified as the only honest way batch approval can exist
  without the planner writing "approved" itself (the exact bypass the rule bans); kept NARROW.
  Queue/`--keys` modes CUT (correction settled the v1 note). Plan size vs scope: proportionate
  only under the subtask split — flagged, proposal owed at 1.6. ✅
- **Phase 3** — new rows walked: **trees cut at plan time** → stale-base risk named in D7 with the
  absorb-at-pickup mitigation IN the plan; **batch approval** → the recorded-quote design keeps the
  operator's words as the only approval artifact (planner never writes the word); **retirement
  half-done** → step 9's proof is re-running the measured sweep; empty-input, escape-hatch,
  dry-run, both-machines, fresh-clone rows unchanged from v1. Residual risks, named: a
  pre-convention walkthrough closing as clear (v1, unchanged, mitigated by landing the convention
  here); a subtask minted outside the planner never gets a plan/tree — the labeler grounds it as
  ticket-text-only and fails it toward 🔒, which is the designed answer.

| Finding | Severity | Failure scenario | Disposition |
|---|---|---|---|
| v2-1 — 000 batch clause could widen the gate | HIGH | "batch" gets read as standing approval; the plan-first gate erodes repo-wide | clause text pinned in A3: listed plans only, verbatim quote required, any plan edit re-arms; reviewed as its own diff hunk |
| v2-2 — retirement before replacements green | MED | board loses its only `parallel-ok` writer mid-lane | step order is the control: 9 runs only after 1–2 + 5 are green; operator's "once we complete these new ones" is the sequencing law |
| v2-3 — planner minting without operator go | HIGH | subtask spam on the board; SCC-119 guardrail broken by automation | the breakdown-STOP is a numbered step in the command with the guardrail cited; minting appears AFTER it |
| v2-4 — stale plan under recorded approval | MED | a lane builds against an edited plan carrying an old quote | quick-dev's batch path requires plan-unchanged-since-approval (A3); re-arm on edit |

**Four quick gates:** verification strategy present (per-step RED column) · irreversible steps
gated (Jira writes behind `--apply`; the delete is step 9, provable + revertable via git; merges
stay with close-out) · vaguest step tightened (the 000 clause text, findings v2-1/v2-4) ·
convention fit (door law via sync incl. door REMOVAL, INDEX rows, SCC-37 quote pattern reused,
SCC-119 propose-then-stop, artifacts in-tree).

Audit verdict: GO
