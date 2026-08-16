# SCC-164 — Command-surface correctness family: twelve parts, one lane, one gate, one close-out

**Lane:** `chore/SCC-164-command-surface-family` · worktree `.claude/worktrees/SCC-164-command-surface-family` ·
cut from `origin/main` @ `a0aceaf` (the SCC-163 merge) on 2026-08-15 · LANE: LOCAL (this repo has no
deployable surface) · closes through `/smh-close-task-merge-tree --expect-key SCC-164`.
**Manifest:** [task.yaml](task.yaml) declares all twelve subtasks as `riders:` — the close ceremony flips
each rider to Done, then the parent (SCC-156 mechanism, already built).
**Board:** [SCC-164](https://sudo-command.atlassian.net/browse/SCC-164) is the INDEX; every part's full
defect, evidence, acceptance and scope lives on its subtask. This plan carries the DECISIONS, the RED /
GREEN / mutant tables and the file lists — read the subtask for the why, read this for the how.

> **Handoff note for the team running this.** You are the third input into this plan, not the first —
> the AVCH-59 close-out retro and the SCC-163 self-audit both fed it, and both had the same finding:
> ~12 minutes of code inside ~100 minutes of lane time, spent on double reviews, avoidable suite runs,
> round-trips and rework. This lane is built to spend that time once. Read § Rules of the lane before
> touching a file.

## ⭐ Operator rulings — 2026-08-15, verbatim

> *"instead of sub task the agents added them as notes A, B, C, D..... We need to move these all to sub
> task"* — done; the parts are subtasks, the parent is an index.
>
> *"I just said I want to do as much as i can in one run on one workingtree/branch. i know its not the
> best coding practice but as slow as this is going I have no choice"* — this lane.
>
> *"every task we develop seems to find new bugs to fix, this as of now leads to 2 or 3 new task tickets
> for every one found. … Rules: 1. look for a ticket to add one issue fixes too 2. when able use one
> workingtree/branch to develope the whole ticket including subtasks. close it all out with one SCC or
> AVCH tag for git. then manually just move the subtasks to done."* — SCC-170, built first, so the lane
> runs under it.
>
> *"we are not developing 3 task for every 1 we try to fix."*
>
> *"then you are approved to write the whole plan so I can hand it off to the dev team"* — this document.

**What the last line authorises, precisely:** writing this plan. It is **not** build approval
(`000-PLAN-FIRST-GATE`: being told to do the work, and answering a question, are named as *not*
approval). See § STOP.

## Why one lane, and how it is still safe

Twelve subtasks on one branch is deliberate (rule 2) and legal (`riders:`). What keeps it safe:

- **Per-part commits, keyed by the subtask** (`SCC-178 fix(gate_receipt): …`). task_preflight compares
  `--expect-key` to the *branch* key only (`task_preflight.py:155-200`) and the commit-msg hook accepts
  any key of the repo's project, so child-keyed commits on a parent-keyed branch pass both gates — and a
  part that goes red at the end can be reverted as a unit and its subtask returned to To Do (SCC-170 §2g).
- **Per-part RED capture and its own tests** (cheap). The **full gate once**, at the tip, through the
  receipt writer. That single change is most of the payoff.
- **Build order = dependency + earliest in-lane payoff**, so the parts that make *this* lane cheaper
  land first (see § Build order).
- **Partial landing is legal** (SCC-170 §2h): if the lane must ship before every part is done, the
  merge lands, its riders flip, the parent STAYS OPEN, and the rest becomes `chore/SCC-164-<slug2>`
  with its own `task.yaml`. Cut line: after item 7.
- **Push after every part.** Branches travel between machines, worktrees do not — an unpushed part
  is stranded on the wrong laptop.

## ⛔ THE ONE OPEN DECISION — arming. Surfaced, not assumed. RECOMMENDATION given.

Three parts add a check that could sit on a shipping path: **A4** (the bare-`main` guard), **E3**
(the lens-roster reader), and SCC-163 Part B (already landed). `blocking-gates-need-a-quoted-ruling`
says a check that can block a shipping path is new law and needs the operator's own words.
**Nothing in the tickets authorises arming.** SCC-163 Part B set the precedent on 2026-08-15 —
*"1. yes"*: host it in `jira_feed.py`, ship **WARN**, `--strict-actions` **built and disarmed**;
workflow_lint ruled out from its own code for anything that reads `_artifacts/`.

| Check | Where it runs (recommended) | Blocks or warns (recommended) | Why |
|---|---|---|---|
| **A4** — a bare `main` used as a diff / rev-list / merge-base / worktree-base operand in `.agents/commands/*.md` | a run_all test, `test_stale_base_refs.py` (the label pass already anticipated that filename), with an explicit **allowlist** for the occurrences A2 judges correct-as-LOCAL | **BLOCKS** — as every run_all test does. It is a regression guard over toolkit text that is GREEN at landing; a guard that only warns is the SCC-125 vacuous shape. It sits on no shipping path today because nothing reintroduces the pattern except a future edit, which is exactly what it should stop | not `workflow_lint`: `--toolkit-only` is the right scope but lint is per-file style; the allowlist needs a test |
| **E3** — a PASS/CONCERNS Verdict with a `dead` lens is a contradiction; a MISSING roster is UNKNOWN | the walkthrough-roster parse lives **once** and both preflights call it (`closeout_preflight.py` for story lanes, `task_preflight.py` for Task lanes — the ticket names the first; smh lanes close through the second) | **WARN**, with `--strict-lenses` **built and disarmed** — matching SCC-163 Part B exactly (same shape: a reader of walkthrough content) | dated cutoff per E4: roster required only where a `Verdict:` line exists AND its date ≥ the day E lands; 130/142 walkthroughs have no roster, 97 have no Verdict at all — the lightweight lane has none by design |

**Ask (one message, alongside the build approval):** *"A4 blocks in run_all; E3 warns with the strict
flag disarmed"* — or your own words. ⛔ Whatever is ruled goes into this file under this heading,
verbatim, before either check is written. Every other decision in this plan is settled below.

## Rules of the lane (SCC-170's rules, applied to this lane from the first commit)

1. **Two stops only** — this plan's approval, and the merge sign-off. Everything else: act on the
   obvious answer, write the choice into the walkthrough, move on. Do not ask "post now or later",
   "keep it narrow", "should this be a ticket".
2. **Artifact-first.** A constraint, a conflict, a dead lens, a skipped step goes into the walkthrough
   the moment it is known. Chat is not a record.
3. **Declare the review runtime at Step 0** (`review-runtime: fan-out | inline`) in the walkthrough
   header, from a probe, before any code. Part I makes it law; this lane obeys it on day one.
4. **Stamp-first.** No bare "let me check" `run_all.py`. The receipt run IS the suite run.
5. **Sweep discipline** until Part K lands: pin the pre-sweep sha, restore, then
   `git diff --quiet -- <mutated files>` yourself — a mutated gate is committable (8681d83).
6. **Find a home, never mint.** Anything discovered that this lane cannot land goes as the next
   lettered subtask under SCC-164 (or the parent whose SCOPE names the file), with an index row and a
   read-back. Say "none found" out loud before minting anything.
7. **Never `git reset --hard` on the lobby's main checkout.** The SCC-163 close-out did, and it wiped
   every uncommitted edit there (memory rows, a memory file's edit, the SCC-169 tick). Recovery is
   `--ff-only`, never reset. Part G removes the reason anyone reaches for it.
8. **Every git call carries `-C`/`--repo`/`--branch`; echo the target from `rev-parse`.** Nothing
   guards the merge target.

## Build order

| # | Part | Key | Why here |
|---|---|---|---|
| 1 | Rule | SCC-170 | the lane runs under it |
| 2 | J | SCC-178 | every receipt run in THIS lane gets cheaper |
| 3 | K | SCC-179 | every part's sweep in THIS lane is checked |
| 4 | A | SCC-165 | wrong diffs stop; H's checklist and E7 depend on it |
| 5 | B | SCC-166 | story lane guarded; E's cicd half depends on it |
| 6 | H | SCC-176 | retro-run over C and D BEFORE they are built |
| 7 | F | SCC-174 | close-out board feed — ⛔ CUT LINE after this row |
| 8 | C | SCC-171 | PC token path — first of the gate/script parts |
| 9 | G | SCC-175 | with/before D: once D1 lands here, the post-merge tick is refused outright |
| 10 | D | SCC-172 | the main gate itself; last of the script parts |
| 11 | E + I | SCC-173 + SCC-177 | same files (review commands + engine); E records, I sequences |

Overlap map (why the order is what it is): C×D on `pre-push-main-approval.sh` · F×G on
`smh-close-task-merge-tree.md` Step 4 · E after A/B on `smh-code-review.md` / `cicd-code-review.md` ·
H after A on `smh-self-audit.md` · I with E on the engine · J and K on different lines of
`smh-quick-dev.md`. Gate/script parts last, as `/smh-merge-multiple-workingtrees` already orders them.

---

# Part 1 — SCC-170: the consolidation rule becomes law, and the riders default

**Defect (short):** the mechanism exists (`riders:`, SCC-156) but is the exception; `/smh-plan-task`
cuts a worktree per subtask; nothing routes discovered work to an existing parent; the operator is
the enforcement for "don't mint". Full text and brainstorm on
[SCC-170](https://sudo-command.atlassian.net/browse/SCC-170).

**Settled here (were "open" on the ticket):**
- Consolidated mode is the **DEFAULT** for a Task with subtasks that share a repo and a lane class;
  the per-subtask-tree mode stays for genuinely parallel work and is chosen by saying so.
- Commit key on a consolidated lane: **the subtask's key per commit**, parent key on the merge.
  Reason: each child's Jira dev panel shows its own commits, and per-part revert works.

**Steps, each naming the assertion that proves it**
1. `.agents/rules/work-consolidation.md` — the six rules (find-a-home; one lane + riders; batch
   verification; artifact-first; two stops; verify-the-outcome), each as a CHECK with the command
   that answers it. Router row in `.agents/rules/INDEX.md`. — asserted by
   `test_rules_index` (rule routed) + door parity for the launcher.
2. `/smh-plan-task` Step 2/3 — CONSOLIDATED MODE: one worktree, one branch keyed by the parent, N
   plan sections in one `implementation_plan.md`, `riders:` written into `task.yaml` at cut time,
   `/smh-label-tasks` output used as BUILD ORDER; the per-subtask-tree path stays as the named
   alternative. The worktree cut reads `origin/main` after `git fetch` (never bare `main` — A's
   subject) and immediately runs `git branch --unset-upstream` (a start-point of `origin/main` sets
   upstream to main; this lane hit it). — asserted by a structural test over the command body
   (the step exists in this order) and by SCC-156's rider test extended: a fixture `task.yaml` with
   `riders:` + a parent whose children are all riders → `check_children` WARNS, never blocks.
3. `/smh-close-task-merge-tree` Step 4 — riders become the DEFAULT wording, not "unless the operator
   ordered"; add **partial landing** (§2h): riders flip, parent stays open, walkthrough names the
   remaining children as the next lane's riders; the "any child still open → STOP" exit is reserved
   for UNDECLARED children. — asserted by extending `test_task_preflight.py`: declared riders subset
   + open undeclared sibling → block; declared subset only → warn + proceed.
4. The **find-a-home step** restated in the six discovery points: code-review-engine triage
   (`steps/step-01-review.md` residue), `/smh-quick-dev`, `/smh-quick-fix`, `/smh-self-audit`,
   `/cicd-code-review`, `/cicd-quick-dev` — the JQL written in, "none found" as the only licence.
   — asserted by one structural check that each of the six carries the step (pin the wiring: the
   step's command line, not a sentence).
5. `docs/_scc_sops_prds/workflows_testing_SOP.md` — the consolidated-lane section (sop_currency will
   demand it). Memory `discovered-work-becomes-a-lettered-part.md` reconciled (done in the lane's
   first commit; index rows restored — see § Residue).
6. Re-sync generated launcher skills (one door per platform per command).

**RED first:** step 3's partial-landing case fails against current `task_preflight.py` (it blocks on
any open child not declared — declared-subset-plus-parent-open is not a state it knows); step 4's
structural check fails on all six commands. Capture both red.

**Mutants (from the code, declared now):** delete `riders:` from the fixture → parent close must BLOCK
(kills the extended rider case) · remove the find-a-home step from one command → the structural check
must fail · restore "unless the operator ordered" wording → the wording test fails.

**Files:** `.agents/rules/work-consolidation.md`, `.agents/rules/INDEX.md`,
`.agents/commands/{smh-plan-task,smh-close-task-merge-tree,smh-quick-dev,smh-quick-fix,smh-self-audit,cicd-code-review,cicd-quick-dev}.md`,
`.agents/skills/code-review-engine/steps/step-01-review.md`, `.agents/scripts/task_preflight.py` (partial landing),
`.agents/scripts/tests/test_task_preflight.py`, `docs/_scc_sops_prds/workflows_testing_SOP.md`,
`_artifacts/_memory/{MEMORY.md,discovered-work-becomes-a-lettered-part.md}`, launcher skills.

# Part 2 — J (SCC-178): gate_receipt stops counting its own output as dirt

**Defect:** `gate_receipt.py:142-144` measures `git status --porcelain -z` over the whole tree; its
own receipt lands inside it at `<root>/gates/<gate>.json` (`:15-18, :98, :304`). First stamp reads
DIRTY, second full suite run to clear it. Two runs per lane, every lane.

**Steps:** (1) RED — fixture tree whose only dirt is a prior receipt under `<root>/gates/` → assert
`dirty_tree is False`; fails today. (2) Exclude paths under the receipt's own `gates/` dir from
`dirty_paths` — that dir only, never `_artifacts/`. (3) Negative control — a sibling file under
`<root>/` that is not `gates/`, and any code path, still DIRTY. (4) `smh-quick-dev.md:297-298`
re-worded: "commit first" stays; the second-run advice for receipt dirt goes.

**Mutants:** widen the exclusion to all of `_artifacts/` → kills (3) · remove the exclusion → kills (1).

**Files:** `.agents/scripts/gate_receipt.py`, `.agents/scripts/tests/test_task_preflight_receipts.py`
(extend), `.agents/commands/smh-quick-dev.md`.

# Part 3 — K (SCC-179): the mutation sweep gets a mechanical restore check

**Defect:** no sweep script; the sweep is prose (`smh-quick-dev.md:299-306`,
`tests-must-gate-for-real.md:68-99`); 8681d83 shipped a live mutant into the gate.

**Settled here:** K1 lands as a **script**, `.agents/scripts/mutation_sweep.py` — reads a declared
table (mutant id · file · original text · mutated text · the named case), refuses to start on a dirty
tree, pins the pre-sweep sha, applies each mutant, runs the named case, restores, and at the end
asserts `git diff --quiet -- <every mutated file>` against the pinned sha; non-zero exit naming the
file if anything survives; restore in `finally`. A command block cannot check itself, and "prose alone
is not an acceptable answer" (K1). K4: after the sweep, the script runs the FULL test file(s) owning
the mutated code once (not the scoped `--case` subset) — that is what would have caught 8681d83.

**Steps:** (1) RED — the check does not exist; the walkthrough records the absence, and a fixture
sweep with a deliberately non-restoring mutant must FAIL once the script exists. (2) the script.
(3) dirty-start refusal + interrupt-restore cases. (4) negative control: clean sweep exits 0 with the
table. (5) `smh-quick-dev.md:299-306`, `tests-must-gate-for-real.md:68-99`, the SOP sweep row point at
the script.

**Mutants:** drop the `git diff --quiet` → kills (1) · drop the dirty-start refusal → kills (3).

**Files:** `.agents/scripts/mutation_sweep.py` (new), `.agents/scripts/tests/test_mutation_sweep.py`
(new), `.agents/commands/smh-quick-dev.md`, `.agents/rules/tests-must-gate-for-real.md`,
`docs/_scc_sops_prds/workflows_testing_SOP.md`, `.agents/scripts/INDEX.md`.

# Part 4 — A (SCC-165): a bare `main` is a stale ref — 20 operands, judged one by one

**Measured 2026-08-15 at a0aceaf — 20 hits in 10 files** (the ticket said ~18 in 9; the sweep also
catches the worktree base and one in `cicd-push-e2e.md`):
smh-merge-multiple-workingtrees 5 · smh-code-review 5 · smh-quick-fix 2 · smh-quick-dev 2 ·
smh-self-audit 1 · smh-plan-task 1 (`:99`, the worktree base) · smh-label-tasks 1 · smh-clean-code-audit 1 ·
cicd-push-e2e 1 · cicd-mobile-error-team 1.

**Steps:** (1) RED — `test_stale_base_refs.py` scans `.agents/commands/*.md` for `main...`/`...main`,
`main..`/`..main`, `merge-base X main`, `worktree add … main`; fails with count 20, captured before
any edit. (2) ⛔ **A2 table** in the walkthrough — every hit, its ruling (`origin/main` after a fetch |
correct-as-LOCAL, allowlisted with the reason). Not all are wrong: a count that genuinely asks about
the local branch stays. **A blanket sed is a defect.** (3) edits per the table; `git fetch` precedes
the first `origin/main` use in each command. (4) GREEN — the test passes against the allowlist.
(5) A5 — diff the rendered steps: no behaviour changes but the ref. (6) A4 wiring per the RULING.
⛔ B1's trap: never plant `origin/main` where the integration ref is the epic branch (cicd-*).

**Mutants:** re-insert one bare `main...HEAD` in a command → the test must fail · widen the allowlist
to a file glob → the test must fail (allowlist is per-line, with a reason).

**Files:** the ten command files above, `.agents/scripts/tests/test_stale_base_refs.py` (new),
`.agents/scripts/tests/run_all.py` (registers it), `docs/_scc_sops_prds/workflows_testing_SOP.md`.

# Part 5 — B (SCC-166): cicd-code-review gains its twin's two steps, ADAPTED

**Settled here (B1):** the story lane's integration ref is `origin/<epic-branch>` resolved from the
story's branch (`story/<key>` → its epic per the branch model), NOT main — copying smh's Step 0.7
verbatim would plant the very bug Part A removes.

**Steps:** (1) Step 0.7 blast-radius re-derivation vs `origin/<epic>` — three lines mandatory: what
the epic moved under this diff, true overlap + merge-tree result, sibling landing-order dependency;
"nothing moved" is a reportable result. (2) Step 2 acceptance audit against the story's checkable
list. (3) `cicd-push-e2e.md:13` — generic referent; B3 grep of `.agents/` for the personal name → 0.
(4) Step 0 resolves repo + lane "from command output, never from belief". (5) `workflow_lint
--toolkit-only` clean; launcher skills re-synced.

**RED:** a heading-parity check (smh Step 0.7 / Step 2 present, cicd absent) fails today; the
personal-name grep is non-zero today.

**Mutants:** delete the new Step 0.7 → parity check fails · put `main` back as the ref → A's test fails.

**Files:** `.agents/commands/cicd-code-review.md`, `.agents/commands/cicd-push-e2e.md`, launcher skills,
`.agents/scripts/tests/test_command_surfaces.py` (extend).

# Part 6 — H (SCC-176): the plan-time port checklist

**Steps:** (1) `.agents/rules/port-checklist.md` — the six checks (git-common-dir/--git-path as git
gives it · echo→printf · exit-code-vs-outcome on writes, `|| exit` on redirects · no `.agents/rules/`
path assumptions in thin repos · python3-vs-python and per-machine `core.hooksPath` · hooks repo-local,
port needs its own project key), each with the command that answers it. INDEX row. (2) `/smh-plan-task`,
`/smh-self-audit`, `/cicd-self-audit` run it when the plan's SCOPE names a file that exists in more
than one repo, or the ticket says "port" — the trigger is a diff of the two copies. (3) RED — a plan
for a port lacking the section is flagged by the audit only after (2) exists; captured red.
(4) **Retro run over C and D on the current lobby scripts** — must catch C's two divergences, or the
checklist is wrong. (5) header says it applies in both directions.

**Mutants:** delete the trigger from `smh-self-audit` → the audit's check fails · remove one of the
six checks → the retro run over C stops catching it.

**Files:** `.agents/rules/port-checklist.md`, `.agents/rules/INDEX.md`,
`.agents/commands/{smh-plan-task,smh-self-audit,cicd-self-audit}.md`, tests, SOP.

# Part 7 — F (SCC-174): jira_feed check stops blessing a forked Dev Record   ⛔ CUT LINE AFTER THIS

**Settled here (F3):** the ONE slug source is the lane's `task.yaml` `branch:` slug. `devrecord`
defaults `--story` from it and WARNS when a passed slug matches no manifest; `smh-quick-dev` and the
close-out's Step 4 both say "the manifest's branch slug".

**Steps:** (1) RED — two Dev Records on one key with differing ids and ONE manifest/branch → `check`
must exit non-zero; today exit 0 (`cmd_check` :1652, the explain-away :1696-1720). (2) an id is a lane
only if a `task.yaml` `branch:` or a `chore/<KEY>-<slug>` branch (local or `origin/`) claims it;
otherwise FORK → exit 1 naming both ids and the newest. (3) F3 defaulting + warn. (4) negative control:
two manifests, two branches, one key → exit 0, existing line. Note SCC-163 just landed a Your-Actions
detector in `finish` — F touches `check`, not `finish`; no conflict, but re-read the file at a0aceaf.

**Mutants:** revert the manifest lookup → kills (1) · drop the origin/ branch arm → a landed-and-pruned
follow-on lane reads as a fork (kills (4)).

**Files:** `.agents/scripts/jira_feed.py`, `.agents/scripts/tests/test_jira_feed.py`,
`.agents/commands/smh-close-task-merge-tree.md`, `.agents/commands/smh-quick-dev.md`.

# Part 8 — C (SCC-171): the token path as git gives it, and mint that cannot lie

**Steps:** (1) RED — a `git` shim earlier on PATH answering `--git-common-dir` with a `C:/…` absolute
path (delegating everything else to real git); drive `mint-push-token.sh` and assert the token path ==
the reported path; fails today (`case … /*)` prepends the repo root). (2) delete the `case` block in
both scripts (both already `cd "$REPO_ROOT"`, which is what makes a relative answer safe). (3) C3 —
`|| exit 2` on the mint redirect; a failed write prints no minted banner; one case. (4) GREEN in a
main checkout AND a worktree.

**Mutants:** restore the `case` block → kills (1) · drop `|| exit 2` → kills (3).

**Files:** `.agents/scripts/git-hooks/mint-push-token.sh`,
`.agents/scripts/git-hooks/pre-push-main-approval.sh`, `.agents/scripts/tests/test_git_hooks.py` (extend).

# Part 9 — G (SCC-175): nothing writes to main after the merge; the merge box is computed

**Three live instances, all in the tree:** SCC-169 (tick left uncommitted on the main checkout,
later wiped by a reset), SCC-162 (merged 8ae2e25, held at Review Required), **SCC-163 (merged
a0aceaf, tick committed as d29b3d8, refused, then `reset --hard origin/main` — which destroyed
unrelated uncommitted work in the main checkout; held at Review Required)**.

**Settled here:** G-ii. `jira_feed.py finish` treats "The merge itself" as SATISFIED when
`git merge-base --is-ancestor <lane-tip> origin/main` (lane tip from the manifest's `branch:`;
`git fetch` first), never by a tick string; it reads the COMMITTED tree (HEAD), never the working
tree. Step 4's tick instruction (`smh-close-task-merge-tree.md:434-438`) is deleted; after Step 3's
push nothing commits. The merge sha lives on the Jira Dev Record (already does).

**Steps:** (1) RED — open merge box + lane tip that IS an ancestor of origin/main → `finish` must not
HOLD; today it does. (2) G-ii. (3) HEAD-not-working-tree: an uncommitted tick must NOT satisfy it.
(4) negative control: tip NOT on origin/main → still HOLDS. (5) Step 4 rewritten; grep the ceremony
for any commit after the push → none. (6) **Live acceptance:** re-run `finish` for SCC-162 and SCC-163
→ both close with no commit to main; record the run in the walkthrough. SCC-169's wiped tick needs
nothing.

**Mutants:** revert the ancestor check → kills (1) · read the working tree → kills (3).

**Files:** `.agents/scripts/jira_feed.py`, `.agents/scripts/tests/test_jira_feed.py`,
`.agents/commands/smh-close-task-merge-tree.md`.

# Part 10 — D (SCC-172): three fail-opens in the main-write gate, ported back from AGY

⛔ **Test in a scratch repo + bare remote, never against the live lobby remote.** AGY's
`test_main_write_gate.py` cases N1–N4, N4c, L and mutants M23–M26 are the working models — port them.

**Steps:** (1) RED ×3 against the current lobby scripts: plain non-merge commit + token naming a
never-existed branch → approved today (D1); bare remote with no main + three stacked merges + one
token → approved today (D2); `push origin main` from a stale worktree lacking the hook → allowed
UNCHECKED today (D3). (2) D1: unresolvable branch = REFUSAL; `^2` must exist unconditionally. D2: zero
remote sha = REFUSAL (seeding a remote is not a door; `--no-verify` is the one-off). D3:
`.githooks/pre-push` narrows the fail-open to non-main refs (the awk on `refs/heads/main`). (3) each
refusal names its OWN reason — pin the reason, not the shared banner (nine rungs print the same one).
(4) ⛔ allow-half controls: a stale worktree still pushes its own chore/claude branch; near-miss refs
(`main-backup`, `mainx`, `epic/*-main-fix`, `chore/*-main-gate`) still push freely.

**Mutants:** revert each of the three → at least one named case dies (M23–M26 shape).

**Files:** `.agents/scripts/git-hooks/pre-push-main-approval.sh`, `.githooks/pre-push`,
`.agents/scripts/tests/test_git_hooks.py`.

# Part 11 — E (SCC-173) + I (SCC-177): the blind review is recorded, enforced, and sequenced

**E4, measured 2026-08-15:** 142 walkthroughs, 12 with `lenses_run`, **130 without**; only 45 carry a
`Verdict:` at all (the lightweight lane has none by design). ⇒ **dated cutoff**: roster required only
where a `Verdict:` exists AND its lane's date ≥ the day E lands; older → legacy WARN, no backfill.
Zero in-flight breakage: the only open lane is this one.

**Steps — E:** (1) RED — a walkthrough with `Verdict: PASS @ sha` and no `lenses_run:` → the preflight
must not read it as clean; today it does. (2) the engine's return block (roster + per-lens
`ok | recovered-inline | dead` + `notes`) is WRITTEN into the walkthrough's `## Code Review` by
`/smh-code-review` Step 4 and `/cicd-code-review` Step 4 — not narrated. (3) ONE roster parser,
called by both `closeout_preflight.py` and `task_preflight.py`: PASS/CONCERNS + a `dead` lens =
contradiction; missing roster (post-cutoff, Verdict present) = UNKNOWN. Ships per the RULING (WARN +
`--strict-lenses` disarmed recommended). (4) **E7** — the same parse asserts Step 0.7's three
re-derivation lines exist ("nothing moved" is a line). (5) negative control: all lenses `ok` passes.
**Steps — I:** (6) `/smh-quick-dev` Step 0 probes and RECORDS `review-runtime: fan-out | inline`;
(7) the engine reads it — `inline` runs the ladder ONCE, blind lens first on the diff alone, roster
says `recovered-inline`; never fan-out → fail → inline → fan-out again; (8) the blind lenses may start
at the frozen-diff commit, concurrently with the receipt run; walkthrough records lens sha == receipt
sha. (9) `test_review_engine.py:140`'s prose pin is replaced by wiring: a fixture walkthrough round-trips
through the parser.

**Mutants:** delete the roster from a PASS fixture → parser must flag · mark one lens `dead` under
PASS → contradiction · delete one Step 0.7 line → E7 flags · declare `inline` and attempt fan-out →
I3 detects.

**Files:** `.agents/scripts/closeout_preflight.py`, `.agents/scripts/task_preflight.py` (or a shared
`walkthrough_roster.py`), `.agents/skills/code-review-engine/{SKILL.md,steps/step-01-review.md}`,
`.agents/commands/{smh-code-review,cicd-code-review,smh-quick-dev}.md`,
`.agents/scripts/tests/{test_review_engine.py,test_closeout_preflight.py,test_task_preflight.py}`.

---

## How the guards are written (every part)

Pin the **WIRING**, never the prose: a fixture that round-trips through the parser, a shim that drives
the script, a structural check on a command's step list. Source-grep guards are blind three ways
(comment literals invert them; they cannot see order; prose pins are vacuous — SCC-125). Every mutant
table above is drawn **from the code**, declared here before the code exists (SCC-144).

## Non-goals — stated so they cannot be quietly absorbed

- The smh-* and cicd-* families do NOT converge; the audited "found correct" list on SCC-164 stays.
- No AGY/AVCH file is touched; hooks are repo-local; AGY is AHEAD on C/D and stays so.
- No check ships ARMED without the quoted ruling under § THE ONE OPEN DECISION.
- No new Task keys. Discovered work → the next lettered subtask under SCC-164, with an index row.
- No post-merge write to main, ever, including "just the tick".

## Risks

- **A twelve-part lane is long.** Push after every part; a part is a unit. The cut line is real.
- **D touches `.githooks/pre-push`** — the live gate. Scratch repo only; the last thing built.
- **F and G both edit `jira_feed.py` right after SCC-163 changed it.** Build on `a0aceaf`, not on
  memory of the file.
- **Untracked memory copies in the lobby's main checkout** (`_artifacts/_memory/{devrecord-…,
  discovered-work-…, grep-reads-…}.md`) are identical to this lane's committed versions. `git merge`
  refuses to overwrite untracked files, so **the close-out's first act is `cmp` each pair, then `rm`
  the three untracked copies in the main checkout** — recorded here so no one meets the error blind.
  (Left in place on purpose: the memory store is read from the main checkout by every session on
  this machine.)
- **A2 is judgment.** Twenty rulings, one table, reviewed as a table. A sed is a defect.
- **The lens fan-out may be dead in the building session** (it was in SCC-162 and SCC-163). Declare
  it at Step 0 (rule 3 above), run inline once, record `recovered-inline`. Do not run it twice.

## The gate this lane must pass (once, at the tip, through the receipt writer)

```bash
W=.claude/worktrees/SCC-164-command-surface-family
python3 .agents/scripts/gate_receipt.py run --task SCC-164 --gate suite \
    --root _artifacts/_main/2026-08-15_SCC-164-command-surface-family -- \
    python3 .agents/scripts/tests/run_all.py                    # the full enforcement suite
python3 .agents/scripts/workflow_lint.py --toolkit-only         # 0/0
python3 .agents/scripts/check_maps.py --depth3-only --strict    # exit 0 (⛔ AUTO-STALE is false in a worktree — read the remedy, don't run it)
python3 .agents/scripts/sop_currency.py                          # exit 0, no [sop-ok] on usage-surface commits
python3 .agents/scripts/tests/test_command_surfaces.py           # door parity after the launcher re-sync
python3 .agents/scripts/task_preflight.py --expect-key SCC-164 --repo "$W" --branch chore/SCC-164-command-surface-family --fetch
```
Per part before its commit: that part's new test file(s) bare (exit code, not `| tail`), its RED
capture pasted, its sweep via `mutation_sweep.py` once Part K exists (by hand with the pinned-sha
check before that). Run every independent verification in ONE block (SCC-170 rule 3).

## Close-out

`/smh-close-task-merge-tree --expect-key SCC-164` from the lobby's main checkout after the pre-merge
`rm` above. It flips the twelve riders, then the parent, files ONE Dev Record on SCC-164 (merge sha)
and the ceremony's pointer on each rider. SCC-162 and SCC-163 close under Part G's live acceptance
(step 6 there), inside this lane, before the merge. Merge sign-off is the operator's verbatim words in
that turn — never solicited.

## Residue absorbed by this lane's first commit

The three memory files (`devrecord-story-slug-forks-the-record.md`,
`discovered-work-becomes-a-lettered-part.md`, `grep-reads-the-branch-you-are-parked-on.md`) and their
three MEMORY.md index rows, lost from the main checkout by the SCC-163 close-out's `reset --hard` and
restored here from this session's record. **Not recoverable:** an uncommitted edit to
`preflight-resolves-repo-from-cwd.md` (another session's; content unknown — likely the AVCH-59 retro's
"preflight aimed at the wrong tree" note). The untracked `README.md` at the repo root is NOT this
lane's; provenance unknown; left untouched.

## Self-audit

Owed by the team that runs this: `/smh-self-audit` on this plan, PRE-WORK mode, before any code —
recorded below this line in the same file. The author of this plan is not its auditor.

## ⛔ STOP — two things owed, one message can carry both

| Owed | State |
|---|---|
| **The arming ruling** (§ THE ONE OPEN DECISION — A4 / E3) | ⛔ OWED — recommended: *A4 blocks in run_all; E3 warns, strict flag disarmed* |
| **Approval of this plan** (`000-PLAN-FIRST-GATE`: the word is `approved`) | ⛔ OWED — *"approved to write the whole plan"* authorised the writing, not the build |

Nothing else blocks. The lane is cut and pushed, the manifest declares the riders, the residue is
absorbed. On the word, the build order is § Build order, item 1 first.
