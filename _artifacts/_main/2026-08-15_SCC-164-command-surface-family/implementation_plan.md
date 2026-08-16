# SCC-164 — Command-surface correctness family: thirteen parts, one lane, one gate, one close-out

> **Rev 2 (2026-08-15).** The independent PRE-WORK self-audit below returned NO-GO with 25 findings
> (F1–F25); every one is adopted into the plan text in this revision and each inline note is marked
> `✅ ADOPTED`. Two of them (F6, F7) were the operator's call under the lane's rule 1 ("act on the
> obvious answer, write the choice down"): they are DECIDED below and named again at § STOP so the
> word `approved` covers them knowingly. Re-audit of the touched phases follows the original audit.

**Lane:** `chore/SCC-164-command-surface-family` · worktree `.claude/worktrees/SCC-164-command-surface-family` ·
cut from `origin/main` @ `a0aceaf` (the SCC-163 merge) on 2026-08-15 · LANE: LOCAL (this repo has no
deployable surface) · closes through `/smh-close-task-merge-tree --expect-key SCC-164`.
**Manifest:** [task.yaml](task.yaml) declares all thirteen subtasks as `riders:` — the close ceremony flips
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
>
> *"I dont see a case in enterprise dev where a warn should make it to prod ?"* — the substance of the
> arming ruling, unprompted.
>
> *"yes you can use those as my words update the plan so we dont have to do that at all"* — adopting
> **"A4 blocks, E3 blocks, arm strict-actions when the count is clean"** as the operator's own words.
> ⭐ **The arming question is RULED and CLOSED. No lane stops for it again.**

**What the last line authorises, precisely:** writing this plan. It is **not** build approval
(`000-PLAN-FIRST-GATE`: being told to do the work, and answering a question, are named as *not*
approval). See § STOP.

## Why one lane, and how it is still safe

Thirteen subtasks on one branch is deliberate (rule 2) and legal (`riders:`). What keeps it safe:

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

## ⭐ ARMING — RULED 2026-08-15. Nothing stops for this again.

> **Operator, verbatim:** *"I dont see a case in enterprise dev where a warn should make it to prod ?"*
> … *"yes you can use those as my words update the plan so we dont have to do that at all"* — adopting
> **A4 blocks, E3 blocks, arm strict-actions when the count is clean.**

**Provenance, stated plainly** (`blocking-gates-need-a-quoted-ruling` bars a derived corollary from
becoming law): the plan's first draft recommended WARN for E3 and the operator **rejected it on his own
reasoning** — the enterprise-prod line above, which matches house law already on record
(`vscode-hides-git-hook-output`: a warn-only hook looks like clean success, and that is how a wrong-key
commit reached a project's `main` on 2026-08-07). The wording below was proposed by this plan and
**adopted verbatim by the operator**. That adoption is what makes it law.

**What it authorises, precisely — three things, no interpretation needed:**
1. **A4 ships ARMED and BLOCKING** as a `run_all` test.
2. **E3 ships ARMED and BLOCKING** in the shared preflight parser. There is no `--strict-lenses`
   opt-in to build: blocking IS the shipped behaviour. The dated cutoff (E4) is the scope limiter, not
   a warn tier. **What blocks, precisely (F4):** `PASS` + any lens `dead` → contradiction → block;
   `CONCERNS` + `dead` → consistent (the CONCERNS floor IS the hatch) → passes; `FAIL` blocks on its
   own; roster MISSING with a post-cutoff `Verdict:` → UNKNOWN → block. Under a declared
   `review-runtime: inline` header, `recovered-inline` is the only legal per-lens state (F20).
3. **SCC-163's `--strict-actions`, already built and disarmed, ARMS** — conditionally, and Part E owns
   the condition: re-run that detector over the post-cutoff walkthrough corpus, record the
   false-positive count in the walkthrough, and flip the flag **if the count is zero**. If it is not
   zero, the detector is tuned until it is; the count and the decision go in the walkthrough either
   way. WARN was its measurement window; this ruling ends the window.

⛔ **Consequence the dev team must accept, not route around:** a lane whose review did not truly run
cannot close. The escape is the inline ladder — run the lenses inline, record `recovered-inline`, take
the CONCERNS floor — never a bypass. There is no `--force`, and adding one is out of scope.

| Check | Where it runs | RULED | Why |
|---|---|---|---|
| **A4** — a bare `main` used as a diff / rev-list / merge-base / worktree-base operand in `.agents/commands/*.md` | a run_all test, `test_stale_base_refs.py` (the label pass already anticipated that filename), with an explicit **allowlist** for the occurrences A2 judges correct-as-LOCAL | **BLOCKS** — as every run_all test does. It is a regression guard over toolkit text that is GREEN at landing; a guard that only warns is the SCC-125 vacuous shape. It sits on no shipping path today because nothing reintroduces the pattern except a future edit, which is exactly what it should stop | not `workflow_lint`: `--toolkit-only` is the right scope but lint is per-file style; the allowlist needs a test |
| **E3** — a **PASS** Verdict with a `dead` lens is a contradiction (**CONCERNS + dead is CONSISTENT** — the engine's designed floor, `step-01-review.md:398`, and the escape this ruling promises); a MISSING roster where a Verdict exists post-cutoff is UNKNOWN | the walkthrough-roster parse lives **once** and both preflights call it (`closeout_preflight.py` for story lanes, `task_preflight.py` for Task lanes — the ticket names the first; smh lanes close through the second) | **BLOCKS.** (Recommendation CHANGED 2026-08-15 after the operator asked *"I don't see a case in enterprise dev where a warn should make it to prod"* — and the house already agrees: `vscode-hides-git-hook-output` records that a warn-only hook looks like clean success and let a wrong-key commit reach a project's main.) The first draft said WARN to match SCC-163 Part B; that precedent's reasons do NOT transfer — it fires AFTER the merge, it is a heuristic over prose with a measured ~50% false-positive class, and it had a legacy problem. E3 fires BEFORE the merge, reads structured data (roster present? lens `dead`?) with no false-positive class, and the dated cutoff already removes the legacy risk. A block strands only a lane that skipped its review or misrecorded it — the inline ladder + `recovered-inline` + the CONCERNS floor is the built-in escape; there is no `--force` | dated cutoff per E4: roster required only where a `Verdict:` line exists AND its date ≥ the day E lands; 130/142 walkthroughs have no roster, 97 have no Verdict at all — the lightweight lane has none by design |

**No ask remains.** The ruling above is complete and quoted; the third clause's *condition* (a clean
false-positive count) is measurable by Part E and needs no further word. Every other decision in this
plan is settled below.

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
6. **Look for a home first.** Anything discovered that this lane cannot land goes as the next
   lettered subtask under SCC-164 (or whichever open parent covers that surface), with an index row
   and a read-back. If nothing fits, mint — and say in one line what you looked at. Judgment, not a
   gate (operator, 2026-08-15: *"the goal is the agent looks first and tries … this is not black and
   white"*).
7. ⛔ **Never `git reset --hard` in the lobby's main checkout — it is never a clean tree.** It hosts
   `_artifacts/_memory/`, which every session on this machine writes, so a reset there eats OTHER
   sessions' work: the SCC-163 close-out destroyed two MEMORY.md rows, a 1,869-char AVCH-59 memory
   section and the SCC-169 tick, none of them its own. Recovery is `git pull --ff-only`, or
   `git reset --keep` (refuses instead of discarding), or `git reset --soft HEAD~1` to undo a local
   commit. Part L fixes the banner that printed `--hard`; Part G removes the reason it gets read.
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
| 9 | G + L | SCC-175 + SCC-180 | two halves of ONE incident (the post-merge tick → the refused push → the `--hard` remedy that ate three sessions' work); G removes the reason the banner is read, L makes the banner safe. With/before D: once D1 lands, the post-merge tick is refused outright |
| 10 | D | SCC-172 | the main gate itself; last of the script parts; D3 (`.githooks/pre-push`) is the LAST edit of the lane (F22) |
| 11 | E + I | SCC-173 + SCC-177 | same files (review commands + engine); E records, I sequences |

> ✅ ADOPTED (rev 2) — ⚠️ AUDIT FINDING (2026-08-15, F1): **Part L (SCC-180) has NO Part section** — the title says thirteen, the manifest declares thirteen riders, but Parts 1–11 cover twelve subtasks and L appears only in this row, rule 7 and § Risks. A builder reaching this row has no steps, no RED, no mutants, no files for L1–L5 (the imperative-vs-prose distinction with the SOP:862 fixture, `git-policy.md`'s recovery paragraph, the SOP row, `--keep` fixture repo ×2), and the close-out would flip SCC-180 to Done with nothing built. Add `# Part 12 — L (SCC-180)` and place it at row 9 WITH G as this row and the ticket order (SCC-164: `G+L`) both say — rows 9 and 12 disagree today; and § Risks says "twelve-part".

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

**Settled by the operator's words (2026-08-15):**
- Consolidated lane **when able** — same repo, same lane class — and the agent decides and says why;
  the per-subtask-tree mode stays for genuinely parallel work. Not a mandatory default, not opt-in
  ceremony: judgment.
- Commit key on a consolidated lane: **the subtask's key per commit**, parent key on the merge.
  Reason: each child's Jira dev panel shows its own commits, and per-part revert works.

**Steps, each naming the assertion that proves it**
1. `.agents/rules/work-consolidation.md` — the six rules (find-a-home; one lane + riders; batch
   verification; artifact-first; two stops; verify-the-outcome), each as a CHECK with the command
   that answers it. Router row in `.agents/rules/INDEX.md`. — asserted by (F12): **`workflow_lint.py`
   `_RULE_POINTERS` gains a row** `("work-consolidation", "consolidating", <regex matching a
   `riders:` write or a "one worktree … subtasks" step>)` so every command that consolidates must cite
   the rule — RED = the row added FIRST, `workflow_lint --toolkit-only` names `smh-plan-task.md`,
   `smh-close-task-merge-tree.md`, `smh-quick-dev.md` as pointing nowhere; GREEN once the bodies
   cite it — plus `check_maps.py --depth3-only --strict` resolving the new INDEX row's path. A rule
   has no launcher door, so no door-parity claim. **`.agents/rules/jira.md:213` and `:347` are
   reconciled in the same commit (F13)** — riders stop being the "operator orders" exception and
   both rules say the same thing: consolidation is the agent's judgment, said out loud, and the
   riders are declared in `task.yaml` at cut time.
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
   for UNDECLARED children. **Mechanism (F5): `landing: partial` in `task.yaml`.** Without it, an
   open undeclared child BLOCKS exactly as today (`test_task_preflight.py:623/:642` stay green and
   binding). With it, `check_children` WARNS naming every undeclared open child, the ceremony flips
   the declared riders only, and the parent STAYS OPEN — and the manifest's `riders:` MUST have been
   TRIMMED to the landed subset first (a rider whose work is not on the branch is a declaration
   error: exit 2 naming it, checked by `git -C <repo> log $(git merge-base origin/main HEAD)..HEAD
   --grep=<KEY>` — range and repo stated, F29). — asserted by
   extending `test_task_preflight.py`: `landing: partial` + declared subset + open undeclared
   sibling → WARN + proceed (RED today: exit 2); no `landing:` + same fixture → block (existing
   `:623`, the negative control); `landing: partial` + a declared rider with no commit on the lane →
   exit 2 naming it.
4. A one-line **"look for a home first"** reminder where discovery happens — the code-review-engine
   triage (`steps/step-01-review.md` residue), `/smh-quick-dev`, `/smh-quick-fix`. A reminder in the
   step list, not a check: the operator ruled this is judgment ("not black and white"), and minting
   is fine when nothing fits.
5. `docs/_scc_sops_prds/workflows_testing_SOP.md` — the consolidated-lane section (sop_currency will
   demand it). Memory `discovered-work-becomes-a-lettered-part.md` reconciled (done in the lane's
   first commit; index rows restored — see § Residue).
6. Re-sync generated launcher skills (one door per platform per command).
7. **The parent-index write is READ BACK (F23, SCC-170's one mechanical guard):** `jira_feed.py`
   grows `index-row --key <parent> --line "<row>" --apply` — reads the description, appends the row,
   writes it, reads it back and exits 2 if the read-back does not contain every pre-existing line
   plus the new one (a data-loss guard, not a policy gate — `acli edit --description` REPLACES the
   field and SCC-164's E7 was lost that way). RED with the existing `acli` stub in
   `test_jira_feed.py`: a stub that drops a line on write → exit 2 naming the missing line;
   negative control: faithful stub → exit 0. `/smh-quick-dev` Step 1.6 and the SCC-170 rule name it
   as the way a lettered part is added.

**RED first:** step 3's partial-landing case (`landing: partial` + open undeclared child) fails
against current `task_preflight.py` — exit 2, because the key is unknown to it and the child is
undeclared. Step 1's `_RULE_POINTERS` row fails `workflow_lint` on three commands. Step 7's dropped-
line stub exits 0 today (there is no read-back). Capture all three red. The rule text itself is
prose on purpose and gets no assertion.

> ⚠️ AUDIT FINDING (rev 2, F26): the `_RULE_POINTERS` RED must be stated at its real severity and against the real tree. (a) `check_rule_pointers` emits `rep.warn` (workflow_lint.py:90-93) and `Report.exit_code()` returns **1** for warnings (wf_common.py:359-361); it DOES run under `--toolkit-only` (workflow_lint.py:500-503). So the RED is *exit 1 + the file named* — real and observable, and **binding on this lane only because § Gate demands `0/0`**; on the wider path a lint warning is CONCERNS (smh-code-review.md:200, :304), advisory in a receipt (`--warn-exit 1`, gate_receipt.py:216-221), and `run_all` never lints the live repo's rule pointers (test_workflow_lint.py:398-405 checks only ap-twins live). Say so; do NOT promote the row to `rep.err` — that would be new blocking law for all five rows and is outside the ruling. (b) The regex sketch is wrong on a0aceaf: `riders:` matches ONLY `smh-close-task-merge-tree.md` today (not `smh-plan-task` / `smh-quick-dev`, which gain the write in step 2), and "one worktree" matches six unrelated cicd bodies (autopilot ×2, merge-epic-workingtrees, park, resume, update-sprint-memory) → false warns that break the tip's `0/0`. Key the row on the manifest write it governs — a literal `riders:` (and, once step 2 lands, `landing:`) — and capture RED in two steps: row added + the step text written WITHOUT the citation → lint names exactly those files → cite → GREEN. The RED is captured after the step text lands, not on the current tree.

> ✅ ADOPTED (rev 2) — ⚠️ AUDIT FINDING (2026-08-15, F5): this RED is already GREEN. `test_task_preflight.py:603` (declared rider → warn, not error), `:623` (undeclared open child still BLOCKS) and `:642` (a rider next to an undeclared open sibling → block stands) are the exact two cases step 3 names — RED never goes red, so partial landing (§2h: riders flip, undeclared children stay open, parent stays open) is never built, and `check_children` today BLOCKS that state (exit 2). Name the mechanism (e.g. `landing: partial` in `task.yaml`, or `--partial`) and re-aim: RED = manifest declares partial + open UNDECLARED children → preflight passes with WARN and the ceremony flips riders only, parent stays open; today exit 2. The mutant "a rider that is not a child → declaration error" tests behaviour no step adds — add the step or drop the mutant. At the cut line, `riders:` is TRIMMED to the landed subset before the preflight ("never declare a ticket whose work is not real").

**Mutants (from the code, declared now):** delete the `landing:` read in `check_children` → the
partial case must BLOCK (kills the RED case) · drop the trimmed-riders check → a rider with no commit
on the lane passes (kills the declaration-error case) · delete the `_RULE_POINTERS` row → lint
passes a command that consolidates without citing the rule (kills step 1's case) · drop the read-back
compare in `index-row` → the dropped-line stub exits 0 (kills step 7's case).

**Files:** `.agents/rules/work-consolidation.md`, `.agents/rules/INDEX.md`,
`.agents/commands/{smh-plan-task,smh-close-task-merge-tree,smh-quick-dev,smh-quick-fix,smh-self-audit,cicd-code-review,cicd-quick-dev}.md`,
`.agents/skills/code-review-engine/steps/step-01-review.md`, `.agents/scripts/task_preflight.py` (partial landing),
`.agents/scripts/tests/test_task_preflight.py`, `.agents/scripts/workflow_lint.py` (`_RULE_POINTERS`),
`.agents/rules/jira.md` (`:213`, `:347`), `.agents/scripts/jira_feed.py` (`index-row`),
`.agents/scripts/tests/test_jira_feed.py`, `docs/_scc_sops_prds/workflows_testing_SOP.md`,
`_artifacts/_memory/{MEMORY.md,discovered-work-becomes-a-lettered-part.md}` (already committed), launcher skills.

> ✅ ADOPTED (rev 2) — ⚠️ AUDIT FINDING (2026-08-15, F12 + F13): (a) `test_rules_index` does not exist (no test asserts a rule is routed in `rules/INDEX.md`; `workflow_lint` checks commands/INDEX only and `_RULE_POINTERS` covers three rules), and a rule has no launcher/door — name the real assertion (`check_maps` resolves the INDEX row's path, nothing more) or add a rules-INDEX coverage case; decide `_RULE_POINTERS` explicitly (add `work-consolidation`, or say why not). (b) `jira.md:213` and `:347` still say riders are the *"operator orders"* exception — the new rule makes consolidation agent judgment; add `.agents/rules/jira.md` to this list and reconcile, or the two rules diverge on who decides.

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
(extend), `.agents/commands/smh-quick-dev.md`, `docs/_scc_sops_prds/workflows_testing_SOP.md` (its row).

> ⚠️ **INPUT TO PART 3, found building Part 2 (2026-08-15):** the restore check must compare against a
> PRE-SWEEP SNAPSHOT of the file, not against HEAD. Part 2's hand sweep used `git diff --quiet` and
> reported `⛔ DIRTY` on a correctly-restored file, because the fix under test was still uncommitted —
> which is the normal state of every sweep, since a sweep runs on the code you just wrote. A HEAD-based
> check is a false alarm on every real run, and a check that always cries wolf gets ignored. K's own
> negative control: a sweep over an UNCOMMITTED change that restores correctly must report CLEAN.

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
(3) dirty-start refusal + interrupt-restore cases + **an EMPTY table is a REFUSAL, exit 2 (F21) — a
sweep of nothing is not a clean sweep**. (4) negative control: clean sweep exits 0 with the
table. (5) `smh-quick-dev.md:299-306`, `tests-must-gate-for-real.md:68-99`, the SOP sweep row point at
the script.

**Mutants:** drop the `git diff --quiet` → kills (1) · drop the dirty-start refusal → kills (3) · drop
the empty-table refusal → kills (3)'s third case.

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
**Test shape (F15):** the allowlist is keyed on `(file, exact operand line TEXT, reason)` — never a
line number; the scan asserts it read **≥ 10 command files** (an empty glob from the wrong CWD is a
FAIL, never a count of 0); the failure message names `file:line` and both remedies (`origin/main`
after `git fetch`, or an allowlist row with a reason).

> ✅ ADOPTED (rev 2) — ⚠️ AUDIT FINDING (2026-08-15, F15): key the allowlist on (file, exact operand line TEXT, reason), never on a line NUMBER — a number breaks on the next edit above it and lets a NEW bare-main hit at the old line pass. And assert the scanned set is non-empty (≥ 10 files): an empty glob from the wrong CWD must FAIL, not count 0 and pass. The failure message names file:line and both remedies (`origin/main` after `git fetch`, or an allowlist row with a reason).

**Mutants:** re-insert one bare `main...HEAD` in a command → the test must fail · widen the allowlist
to a file glob → the test must fail (allowlist is per-line, with a reason) · point the scan at an
empty dir → the test must fail (non-empty assertion).

**Files:** the ten command files above, `.agents/scripts/tests/test_stale_base_refs.py` (new;
`run_all.py` auto-discovers `test_*.py` — nothing to register), `docs/_scc_sops_prds/workflows_testing_SOP.md`.

> ✅ ADOPTED (rev 2) — ⚠️ AUDIT FINDING (2026-08-15, F10): `run_all.py` auto-discovers `test_*.py` (run_all.py:11, :43) — nothing to register; drop it from this list rather than edit the gate runner for nothing.

# Part 5 — B (SCC-166): cicd-code-review gains its twin's two steps, ADAPTED

**Settled here (B1):** the story lane's integration ref is `origin/<epic-branch>` resolved from the
story's branch (`story/<key>` → its epic per the branch model), NOT main — copying smh's Step 0.7
verbatim would plant the very bug Part A removes.

**Steps:** (1) Step 0.7 blast-radius re-derivation vs `origin/<epic>` — three lines mandatory: what
the epic moved under this diff, true overlap + merge-tree result, sibling landing-order dependency;
"nothing moved" is a reportable result. (2) Step 2 acceptance audit against the story's checkable
list. (3) `cicd-push-e2e.md:13` AND `:134` — generic referent. **B3 is SCOPED (F7, decided under
rule 1):** the personal-name grep → 0 applies to **the files this part edits**
(`cicd-code-review.md`, `cicd-push-e2e.md`), asserted per file. The toolkit-wide count (213 at
a0aceaf: commands 95 · rules 69 · workflows 24 · skills 16 · scripts 5, incl. `operator-profile.md`
where the name IS the subject) is RECORDED in the walkthrough and NOT swept here — the memory
`no-personal-name-in-directives` names the toolkit-wide sweep a separate, confirm-scope task, and a
~30-file sweep with an allowlist is not a rider of a review-step ticket. Reason stated at § STOP so
`approved` covers it; the operator may widen it with a word.
(4) Step 0 resolves repo + lane "from command output, never from belief". (5) `workflow_lint
--toolkit-only` clean; launcher skills re-synced.

> ✅ ADOPTED as SCOPED (rev 2) — ⚠️ AUDIT FINDING (2026-08-15, F7): "B3 grep of `.agents/` for the personal name → 0" is unreachable from this step: 213 hits at a0aceaf (commands 95 · rules 69 · workflows 24 · skills 16 · scripts 5 — e.g. `cicd-mobile-error-team.md` ×14, `cicd-park.md`, `cicd-autopilot-claude.md`, `rules/operator-profile.md` where the name IS the subject), and `cicd-push-e2e.md` carries it at :13 AND :134. The memory `no-personal-name-in-directives` names the toolkit-wide sweep a separate, confirm-scope task. Pick one, in the plan: scope B3 to the files Part 5 edits (per-file check → 0), or plan the ~30-file sweep with an allowlist for `operator-profile.md` — the operator's call.

**RED:** a heading-parity check (smh Step 0.7 / Step 2 present, cicd absent) fails today; the
per-file personal-name grep over `cicd-push-e2e.md` is non-zero today (2 hits).

**Mutants:** delete the new Step 0.7 → parity check fails · put `main` back as the ref → A's test fails.

**Files:** `.agents/commands/cicd-code-review.md`, `.agents/commands/cicd-push-e2e.md`, launcher skills,
`.agents/scripts/tests/test_command_surfaces.py` (extend), `docs/_scc_sops_prds/workflows_testing_SOP.md`
(its row — SCC-166's `[sop-ok]`-citing-SCC-165 clause was written for TWO lanes; on ONE lane the SOP
row rides this part's own commit).

# Part 6 — H (SCC-176): the plan-time port checklist

**Steps:** (1) `.agents/rules/port-checklist.md` — the six checks (git-common-dir/--git-path as git
gives it · echo→printf · exit-code-vs-outcome on writes, `|| exit` on redirects · no `.agents/rules/`
path assumptions in thin repos · python3-vs-python and per-machine `core.hooksPath` · hooks repo-local,
port needs its own project key), each with the command that answers it. INDEX row. (2) `/smh-plan-task`,
`/smh-self-audit`, `/cicd-self-audit` run it when the plan's SCOPE names a file that exists in more
than one repo, or the ticket says "port" — the trigger is a diff of the two copies. (3) **The
mechanical piece is ONE thing (F16), stated plainly: H ships as a rule + command prose, and the only
wired check is a `_RULE_POINTERS` row** `("port-checklist", "porting", <regex matching
"port" as a step verb / "exists in more than one repo">)` so a command that talks about porting
must cite the rule. RED = the row first, `workflow_lint --toolkit-only` names `smh-plan-task.md`,
`smh-self-audit.md`, `cicd-self-audit.md`; GREEN once they cite it. There is NO claim that the
audit's reading of a plan is machine-checked — it is prose an agent executes, and the plan says so.
(4) **Retro run over C and D on the current lobby scripts** — a manual reading, recorded as a table in
the walkthrough; it must catch C's two divergences, or the checklist is wrong. (5) header says it
applies in both directions. Items 4 and 6 of the six CITE `project-law.md` (thin repos; repo-local
enforcement) rather than restate it.

> ⚠️ AUDIT FINDING (rev 2, F26): the sketched trigger (`"port" as a step verb`) matches **6 files today and none of the three H edits** — `cicd-e2e.md:28` ("port 3100"), `cicd-live-testing-team.md:24` (`--port`), `smh-code-review.md:213` ("Port the rule verbatim"), `cicd-autopilot-deepseek4.md:49/:51`, and both AP twins — while `smh-plan-task`, `smh-self-audit`, `cicd-self-audit` do not say "port" until step (2) writes it. As sketched, RED names the wrong files and the tip can never reach `0/0`. Key the row on the exact phrase step (2) introduces (e.g. `port-checklist` / "exists in more than one repo") and capture RED after that step text lands without the citation (see Part 1's F26 note for the severity: WARN / exit 1, binding here via § Gate's `0/0`, never promoted to an error).

> ✅ ADOPTED (rev 2) — ⚠️ AUDIT FINDING (2026-08-15, F16): `/smh-self-audit` is prose an agent executes — "the audit's check reads the plan for the section" and the mutant "delete the trigger from `smh-self-audit`" are source-grep / prose pins, vacuous by this plan's own § How the guards are written; H4's retro-run is a manual reading. Either name the mechanical piece (a small script, e.g. `port_check.py --plan <path> --a <repo> --b <repo>`: asserts the plan carries the section whenever the two copies differ) and pin ITS wiring, or state plainly that H ships as a rule + command prose and drop the RED/mutant claims. Items 4 and 6 of the six already live in `project-law.md` (thin repos; repo-local enforcement) — cite, do not restate.

**Mutants:** delete the `_RULE_POINTERS` row → lint passes a porting command that cites nothing (kills
(3)). No other mutant is claimed — the rest of H is prose by design.

**Files:** `.agents/rules/port-checklist.md`, `.agents/rules/INDEX.md`,
`.agents/commands/{smh-plan-task,smh-self-audit,cicd-self-audit}.md`, `.agents/scripts/workflow_lint.py`
(`_RULE_POINTERS`), `docs/_scc_sops_prds/workflows_testing_SOP.md` (its row).

# Part 7 — F (SCC-174): jira_feed check stops blessing a forked Dev Record   ⛔ CUT LINE AFTER THIS

**Settled here (F3):** the ONE slug source is the lane's `task.yaml` `branch:` slug. `devrecord`
defaults `--story` from it and WARNS when a passed slug matches no manifest; `smh-quick-dev` and the
close-out's Step 4 both say "the manifest's branch slug".

**Steps:** (1) RED — two Dev Records on one key with differing ids and ONE manifest/branch → `check`
must exit non-zero; today exit 0 (`cmd_check` at a0aceaf is `:1795`, the explain-away `:1839-1863` —
F9). (2) an id is a lane only if a `task.yaml` `branch:` **anywhere in the COMMITTED tree
(`git ls-files '_artifacts/**/task.yaml'`, F17)** or a `chore/<KEY>-<slug>` branch (local or
`origin/`) claims it; otherwise FORK → exit 1 naming both ids and the newest. (3) F3 defaulting + warn. (4) negative control:
two manifests, two branches, one key → exit 0, existing line. Note SCC-163 just landed a Your-Actions
detector in `finish` — F touches `check`, not `finish`; no conflict, but re-read the file at a0aceaf.

**Mutants:** revert the manifest lookup → kills (1) · drop the origin/ branch arm → a landed-and-pruned
follow-on lane reads as a fork (kills (4)).

**Files:** `.agents/scripts/jira_feed.py`, `.agents/scripts/tests/test_jira_feed.py`,
`.agents/commands/smh-close-task-merge-tree.md`, `.agents/commands/smh-quick-dev.md`,
`docs/_scc_sops_prds/workflows_testing_SOP.md` (its row).

# Part 8 — C (SCC-171): the token path as git gives it, and mint that cannot lie

**Steps:** (1) RED — a `git` shim earlier on PATH answering `--git-common-dir` with a `C:/…` absolute
path (delegating everything else to real git); drive `mint-push-token.sh` and assert the token path ==
the reported path; fails today (`case … /*)` prepends the repo root). (2) delete the `case` block in
both scripts (both already `cd "$REPO_ROOT"`, which is what makes a relative answer safe). (3) C3 —
`|| exit 2` on the mint redirect; a failed write prints no minted banner; one case. (4) GREEN in a
main checkout AND a worktree.

**Mutants:** restore the `case` block → kills (1) · drop `|| exit 2` → kills (3).

**Files:** `.agents/scripts/git-hooks/mint-push-token.sh`,
`.agents/scripts/git-hooks/pre-push-main-approval.sh`, **`.agents/scripts/tests/test_main_push_gate.py`
(extend — it owns mint + main-approval; ONE red-file per tier, F11)**,
`docs/_scc_sops_prds/workflows_testing_SOP.md` (its row).
**PC (F25):** the C1 shim is a POSIX `git` script and the hook runs under `sh` (the file already
resolves `sh_bin` at `:80`); on Windows the case runs only when `sh`/`bash` resolves, else it SKIPS
with the reason printed — the same guard the file's INSTALLED half already uses (SCC-110).

> ✅ ADOPTED (rev 2) — ⚠️ AUDIT FINDING (2026-08-15, F11): the file that owns `mint-push-token.sh` + `pre-push-main-approval.sh` cases is `.agents/scripts/tests/test_main_push_gate.py`, not `test_git_hooks.py` — extend it (ONE red-file per tier). PC note: a POSIX `git` shim on PATH is not a `git.cmd`; state the case's behaviour on the PC (skip-with-reason or a `.cmd` twin).

# Part 9 — G (SCC-175): nothing writes to main after the merge; the merge box is computed

**Three live instances, all in the tree:** SCC-169 (tick left uncommitted on the main checkout,
later wiped by a reset), SCC-162 (merged 8ae2e25, held at Review Required), **SCC-163 (merged
a0aceaf, tick committed as d29b3d8, refused, then `reset --hard origin/main` — which destroyed
unrelated uncommitted work in the main checkout; held at Review Required)**.

**Settled here:** G-ii. `jira_feed.py finish` treats "The merge itself" as SATISFIED when
`git merge-base --is-ancestor <lane-tip> origin/main` (`git fetch` first), never by a tick string.
**Lane tip resolution, in order (F6a):** the manifest's `branch:` as a local ref → as `origin/<branch>`
→ the walkthrough's `Verdict: … @ <sha>` (a pruned lane's tip lives there; SCC-163's `eb9030b` and
SCC-162's `31ce965` are both ancestors of origin/main — verified) → else UNRESOLVABLE = HOLD naming
what it tried. It reads the COMMITTED tree, never the working tree — precisely
`git -C <toplevel of the walkthrough path> show HEAD:<walkthrough relpath>` (F18). Step 4's tick instruction (`smh-close-task-merge-tree.md:434-438`) is deleted; after Step 3's
push nothing commits. The merge sha lives on the Jira Dev Record (already does).

> ⚠️ AUDIT FINDING (rev 2, F27): `finish` has NO notion of a merge row today — `open_actions` (jira_feed.py:1306-1340) returns every open `- [ ]` under `## Your Actions`. G-ii therefore needs a RECOGNISER, and the string "The merge itself" is not what the live corpus says: SCC-163's row is `- [ ] **Merge and close out** — /smh-close-task-merge-tree --expect-key SCC-163` (walkthrough.md:250); SCC-162's was `**Land it**`. A literal match HOLDS SCC-163 and the scoped live acceptance fails. Define it fail-safe: an open row is the merge row only if it names a merge DOOR (`/smh-close-task-merge-tree` or `/cicd-push-e2e`) or reads merge/land + main/close-out; it is SATISFIED only when that recogniser fires AND the ancestor check passes; every other open row still holds. Pin SCC-163's real row text as the fixture, plus a negative fixture (`- [ ] decide whether to merge X` with no door → still holds).

**Steps:** (1) RED — open merge box + lane tip that IS an ancestor of origin/main → `finish` must not
HOLD; today it does. (2) G-ii. (3) HEAD-not-working-tree: an uncommitted tick must NOT satisfy it.
(4) negative control: tip NOT on origin/main → still HOLDS; a walkthrough with no branch, no `origin/`
and no `Verdict @ sha` → HOLD naming the three misses. (5) Step 4 rewritten; grep the ceremony
for any commit after the push → none. (6) **Live acceptance — SCOPED to SCC-163 (F6b/c):**
`jira_feed.py finish --key SCC-163 --walkthrough <its walkthrough on main>` **WITHOUT `--apply`**,
mid-lane, as the evidence: it must report the merge box SATISFIED (tip `eb9030b` via the Verdict
fallback, ancestor of origin/main) and nothing else owed. The `--apply` that moves SCC-163 to Done
runs **inside this lane's close-out ceremony** — the operator-invoked `/smh-close-task-merge-tree
--expect-key SCC-164`, immediately after the merge lands — and the walkthrough names it under
`## Your Actions` as `- [x]` once done. **SCC-162 is NOT in scope:** its merge rows were ticked on the
lane (8b69275) and the one open box on main is `- [ ] Try the lane on something real`
(walkthrough.md:199), a REAL operator item G-ii must not clear; SCC-162 closes on the operator's word.
SCC-169's wiped tick needs nothing.


> ✅ ADOPTED (rev 2) — ⚠️ AUDIT FINDING (2026-08-15, F6): step (6) cannot pass as written. (a) `chore/SCC-162-lightweight-lane` and `chore/SCC-163-gate-hardening` are PRUNED, local and remote (`git branch -a` at a0aceaf shows neither), so "lane tip from the manifest's `branch:`" resolves nothing and G-ii cannot compute `--is-ancestor` for either. Define the fallback: the walkthrough's `Verdict: … @ <sha>` (31ce965 and eb9030b are both ancestors of origin/main — verified) or the merge commit's `^2`. (b) SCC-162 is NOT held over the merge box: its merge rows were ticked on the lane (8b69275) and the one open box on main is `- [ ] Try the lane on something real` (walkthrough.md:199) — a real operator item G-ii must not clear. Scope the live acceptance to SCC-163; SCC-162 closes on the operator's word. (c) `finish --apply` is a Jira transition to Done; run `finish` WITHOUT `--apply` mid-lane as the acceptance evidence, and take the `--apply` for SCC-163 inside an operator-invoked ceremony (this lane's close-out, or the operator's word this session) — say which.
**Mutants:** revert the ancestor check → kills (1) · read the working tree → kills (3) · drop the
Verdict-sha fallback → the pruned-lane fixture HOLDS (kills the fallback case).

**Files:** `.agents/scripts/jira_feed.py`, `.agents/scripts/tests/test_jira_feed.py`,
`.agents/commands/smh-close-task-merge-tree.md`, `docs/_scc_sops_prds/workflows_testing_SOP.md` (its row).

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
**`.agents/scripts/tests/test_main_push_gate.py` (extend — never fork into `test_git_hooks.py`, F11)**,
`docs/_scc_sops_prds/workflows_testing_SOP.md` (its row).
⛔ **`core.hooksPath=.githooks` is RELATIVE (F22): the moment `.githooks/pre-push` is saved in this
worktree it is LIVE for this lane's own pushes.** D3 is therefore the LAST edit of the whole lane:
prove it in the scratch repo, commit, push once — with Part 11 already pushed before it.

> ✅ ADOPTED (rev 2) — ⚠️ AUDIT FINDING (2026-08-15, F11 + F22): the main-write gate's cases live in `.agents/scripts/tests/test_main_push_gate.py` (12 refs to mint/pre-push-main-approval; `test_git_hooks.py` has one, for the BACKSTOP) — D's cases EXTEND `test_main_push_gate.py`, never fork into test_git_hooks (`red-file-hosts-expansions`). And `core.hooksPath=.githooks` is a RELATIVE path, so this worktree's own edited `.githooks/pre-push` is LIVE for this lane's "push after every part" the moment it is saved — build D3 last, prove it in the scratch repo, push once.

# Part 11 — E (SCC-173) + I (SCC-177): the blind review is recorded, enforced, and sequenced

**E4, measured 2026-08-15:** 142 walkthroughs, 12 with `lenses_run`, **130 without**; only 45 carry a
`Verdict:` at all (44 by closeout_preflight's lenient regex, 34 by task_preflight's strict one; the
lightweight lane has none by design). ⇒ **dated cutoff (F19)**: the lane's date is the artifact
folder's `YYYY-MM-DD` prefix; a roster is required only where the READER'S OWN `Verdict:` regex
matches AND that date ≥ the day E lands; older → legacy WARN, no backfill.
Zero in-flight breakage: the only open lane is this one.

> ⚠️ AUDIT FINDING (rev 2, F28): "the day E lands" makes this lane's own walkthrough (folder `2026-08-15_…`) LEGACY if E lands on any later day — the lane that builds E3 would be the first one it does not bind. Pin the cutoff as the literal `2026-08-15` (the plan date) in the parser: deterministic on both machines and a fresh clone, and this lane is the first one covered.

**Steps — E:** (1) RED — a walkthrough with `Verdict: PASS @ sha` and no `lenses_run:` → the preflight
must not read it as clean; today it does. (2) the engine's return block (roster + per-lens
`ok | recovered-inline | dead` + `notes`) is WRITTEN into the walkthrough's `## Code Review` by
`/smh-code-review` Step 4 and `/cicd-code-review` Step 4 — not narrated. (3) ONE roster parser,
called by both `closeout_preflight.py` and `task_preflight.py`: **PASS + a `dead` lens =
contradiction → block; CONCERNS + `dead` = consistent (the designed floor, `step-01-review.md:398`);
FAIL blocks anyway; missing roster (post-cutoff, Verdict present) = UNKNOWN → block (F2/F4).** Ships
ARMED and BLOCKING per § ARMING — there is no `--strict-lenses`. A one-line correction is posted as a
comment on SCC-173 (its E3 text carries the PASS/CONCERNS slip) when this part lands. (4) **E7** — the same parse asserts Step 0.7's three
re-derivation lines exist ("nothing moved" is a line). (5) negative control: all lenses `ok` passes.

> ✅ ADOPTED (rev 2) — ⚠️ AUDIT FINDING (2026-08-15, F2 + F4): (a) the parenthetical in step (3) — *"WARN + `--strict-lenses` disarmed recommended"* — is the FIRST draft's recommendation and contradicts § ARMING clause 2: **E3 BLOCKS; there is no `--strict-lenses` to build.** Ignore the parenthetical. (b) The contradiction test as written ("PASS/CONCERNS + a `dead` lens") contradicts the engine's own contract at `step-01-review.md:398`: a lens still `dead` after retry + inline rerun **raises the floor to CONCERNS** — CONCERNS + dead is the DESIGNED end state, and it is the escape hatch § ARMING promises. Under BLOCK as written, a lane with a dead lens could never close. Correct rule: **PASS + dead = contradiction; CONCERNS + dead = consistent; FAIL blocks anyway; missing roster (post-cutoff, Verdict present) = UNKNOWN = block.** SCC-173 E3's text carries the same slip — correct the subtask when this is adopted.
**Steps — I:** (6) `/smh-quick-dev` Step 0 probes and RECORDS `review-runtime: fan-out | inline`
in the walkthrough header; **the story lane's counterpart (F24) is `/cicd-code-review` Step 0**,
which probes and records the same header if the story's walkthrough does not carry it yet (I's SCOPE
names no dev-side cicd command, and the review is where the fan-out happens);
(7) the engine reads it — `inline` runs the ladder ONCE, blind lens first on the diff alone, roster
says `recovered-inline`; never fan-out → fail → inline → fan-out again; **I3's wiring (F20): the
roster parser flags header `inline` + any lens `ok` — under `inline`, `recovered-inline` is the
only legal state, so a fan-out attempted against the declaration shows in the data;** (8) the blind lenses may start
at the frozen-diff commit, concurrently with the receipt run; walkthrough records lens sha == receipt
sha. (9) `test_review_engine.py:140`'s prose pin is replaced by wiring: a fixture walkthrough round-trips
through the parser.

**Mutants:** delete the roster from a PASS fixture → parser must flag · mark one lens `dead` under
PASS → contradiction · mark one lens `dead` under CONCERNS → must PASS (negative control) · delete
one Step 0.7 line → E7 flags · header `inline` + a lens `ok` → I3 flags.

**Files:** `.agents/scripts/walkthrough_roster.py` (new — the ONE parser, F31), imported by both
`.agents/scripts/closeout_preflight.py` and `.agents/scripts/task_preflight.py`, `.agents/skills/code-review-engine/{SKILL.md,steps/step-01-review.md}`,
`.agents/commands/{smh-code-review,cicd-code-review,smh-quick-dev}.md`,
`.agents/scripts/tests/{test_review_engine.py,test_closeout_preflight.py,test_task_preflight.py}`,
`docs/_scc_sops_prds/workflows_testing_SOP.md` (its row).

# Part 12 — L (SCC-180): the backstop stops printing `git reset --hard` — lands WITH Part 9 (G)

**Defect:** `.agents/scripts/git-hooks/pre-push-merge-backstop.sh:95` prints
`git reset --hard origin/$1  # ONLY if this lane was already pushed` inside its refusal banner. An
agent ran it in the lobby's MAIN CHECKOUT (2026-08-15, reflog HEAD@{0} and HEAD@{5}) and destroyed
three other sessions' uncommitted work — the main checkout hosts `_artifacts/_memory/`, so it is
never a clean tree. There is no git hook for `reset`; the only fix is to stop printing it. Full text on
[SCC-180](https://sudo-command.atlassian.net/browse/SCC-180).

**Steps:** (1) RED — `test_git_hooks.py` (it owns the BACKSTOP, F11) gains a check that finds
`reset --hard` printed as a REMEDY in `.agents/` + `docs/`: an imperative (a printed command line, a
fenced step) FAILS; prose that names it as the thing NOT to do PASSES — pinned with BOTH fixtures
(`pre-push-merge-backstop.sh:95` must fail it, `workflows_testing_SOP.md:862` must pass it — the
comment-literal blindness case). Captured red with the count. (2) L-i/L-ii: the banner prints
`git reset --keep origin/$1  # refuses rather than discarding local changes` and one line of WHY
("never `--hard` here — the main checkout carries other sessions' uncommitted memory edits");
`git reset --soft HEAD~1` named for undoing a local commit. (3) GREEN — the drill still works: a
fixture repo where the lane was already pushed and the tree is CLEAN resets as intended; where the
tree is DIRTY, `--keep` refuses and the dirt survives — two cases, the second is the point. (4)
`git-policy.md`'s recovery paragraph names `--keep`/`--soft`; the SOP recovery row; L-iii — no
instruction under `.agents/` or `docs/` prints `reset --hard` as a step (the check from (1) is the
sweep). (5) Arming: rides A4's ruling — a run_all regression guard over toolkit text, GREEN at
landing, BLOCKS (L4).

**Mutants (from the code):** restore `--hard` in the banner → kills (1) · delete the imperative-vs-
prose distinction → SOP:862 false-positives, kills (1)'s pass fixture · drop the DIRTY fixture →
(3)'s second case is vacuous, so it stays.

**Files:** `.agents/scripts/git-hooks/pre-push-merge-backstop.sh`, `.agents/scripts/tests/test_git_hooks.py`
(extend), `.agents/rules/git-policy.md`, `docs/_scc_sops_prds/workflows_testing_SOP.md` (its row).
No overlap with any other part (the backstop is touched by nothing else); lands in the same push as
Part 9.

---

## How the guards are written (every part)

Pin the **WIRING**, never the prose: a fixture that round-trips through the parser, a shim that drives
the script, a structural check on a command's step list. Source-grep guards are blind three ways
(comment literals invert them; they cannot see order; prose pins are vacuous — SCC-125). Every mutant
table above is drawn **from the code**, declared here before the code exists (SCC-144).

## Non-goals — stated so they cannot be quietly absorbed

- The smh-* and cicd-* families do NOT converge; the audited "found correct" list on SCC-164 stays.
- No AGY/AVCH file is touched; hooks are repo-local; AGY is AHEAD on C/D and stays so.
- No check ships ARMED beyond what § ARMING (RULED and CLOSED 2026-08-15) authorises: A4, E3, and
  L's guard under A4's shape; `--strict-actions` on a clean count.
> ✅ ADOPTED (rev 2) — ⚠️ AUDIT FINDING (2026-08-15, F3): "§ THE ONE OPEN DECISION" is a dangling reference — the ruling is § ARMING, above, and it is CLOSED.
- No new Task keys. Discovered work → the next lettered subtask under SCC-164, with an index row.
- No post-merge write to main, ever, including "just the tick".

## Risks

- **A thirteen-part lane is long.** Push after every part; a part is a unit. The cut line is real.
- **D touches `.githooks/pre-push`** — the live gate, and `hooksPath` is relative so the edit is live
  in this worktree on save. Scratch repo only; the LAST edit of the lane; one push after it.
- **Two machines.** Every `python3` in this plan is `python` on the PC; the gate block below is
  written for the Mac this lane runs on.
- **F and G both edit `jira_feed.py` right after SCC-163 changed it.** Build on `a0aceaf`, not on
  memory of the file.
- **The main checkout is never a clean tree.** It hosts `_artifacts/_memory/`, which every session
  on this machine writes. Any recovery run there — `reset`, `clean`, `checkout --` — eats other
  sessions' work. Use `git reset --keep` (Part L), never `--hard`.
- **Untracked memory copies in the lobby's main checkout** (`_artifacts/_memory/{devrecord-…, discovered-work-…, grep-reads-…}.md`) are identical to this lane's committed versions. `git merge`
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

**SOP rule for every commit (F14):** `sop_currency.py:72-77` classifies `.agents/commands/`,
`.agents/rules/`, `.agents/scripts/*.py` and `.agents/scripts/git-hooks/` as usage surfaces, and every
part touches one. **Each part's commit stages its own SOP row** in the SCC-164 family section of
`workflows_testing_SOP.md` (a few lines per part; the section grows part by part). `[sop-ok]` is
reserved for a commit whose diff touches NO usage surface (a tests-only or walkthrough-only commit),
and each use is named in the walkthrough. **Launcher re-sync:** every part that edits a command body
(1, 2, 3, 4, 5, 6, 7, 9, 11) re-runs `/smh-sync-agents` before its commit so the four doors travel with
the command; `test_command_surfaces.py` at the tip proves parity once.

> ✅ ADOPTED (rev 2) — ⚠️ AUDIT FINDING (2026-08-15, F14): the armed `sop_currency` gate classifies `.agents/commands/`, `.agents/rules/`, `.agents/scripts/*.py` and `.agents/scripts/git-hooks/` as usage surfaces (sop_currency.py:72-77). EVERY per-part commit in this plan touches one, yet only Parts 1, 3, 4, 6 list the SOP in their files — the commits for Parts 2, 5, 7, 8, 9, 10, 11 are REJECTED at commit time unless the SOP row rides the same commit, and this block forbids `[sop-ok]`. Rule for the builder: each part's commit stages its own SOP row (add the SOP to those seven file lists), or this gate line changes — one or the other, decided before Part 2's commit.

## Close-out

`/smh-close-task-merge-tree --expect-key SCC-164` from the lobby's main checkout after the pre-merge
`rm` above. It flips the thirteen riders, then the parent, files ONE Dev Record on SCC-164 (merge sha)
and the ceremony's pointer on each rider. SCC-163 closes under Part G's live acceptance (step 6
there): the evidence run mid-lane without `--apply`, the `--apply` inside this ceremony after the
merge lands. SCC-162 stays open on its real operator item. Merge sign-off is the operator's verbatim words in
that turn — never solicited.

## Residue absorbed by this lane's first commit

The three memory files (`devrecord-story-slug-forks-the-record.md`,
`discovered-work-becomes-a-lettered-part.md`, `grep-reads-the-branch-you-are-parked-on.md`) and their
three MEMORY.md index rows, lost from the main checkout by the SCC-163 close-out's `reset --hard` and
restored here from this session's record. **RECOVERED 2026-08-15** from the authoring session's transcript (`git fsck` found no dangling blob —
unstaged work never becomes a git object): the 1,869-character AVCH-59 section of
`preflight-resolves-repo-from-cwd.md` ("⛔ Passing both flags is NOT enough — `--repo` must be the
WORKTREE"), restored on this lane. It also answers the `README.md` question below: that memory
records it as **another lane's uncommitted file**, so leave it alone. The untracked `README.md` at the repo root is NOT this
lane's; provenance unknown; left untouched.

## Self-audit

Owed by the team that runs this: `/smh-self-audit` on this plan, PRE-WORK mode, before any code —
recorded below this line in the same file. The author of this plan is not its auditor.

## ⛔ STOP — one thing owed

| Owed | State |
|---|---|
| **The arming ruling** (§ ARMING — A4 / E3 / strict-actions) | ✅ **RULED and CLOSED 2026-08-15** — A4 blocks, E3 blocks (PASS+dead; CONCERNS+dead passes), strict-actions arms on a clean count |
| **Approval of this plan** (`000-PLAN-FIRST-GATE`: the word is `approved`) | ⛔ OWED — *"approved to write the whole plan"* authorised the writing, not the build |

**Two calls made under rule 1 that the word `approved` will cover knowingly** (either can be
overturned with a word before it):
- **F7 / B3 scope** — the personal-name grep → 0 is per-file over the two files Part 5 edits; the
  213-hit toolkit-wide sweep is recorded, not done (the memory names it a separate confirm-scope task).
- **F6 / live acceptance** — SCC-163 only; evidence run without `--apply` mid-lane, `--apply` inside
  the close-out ceremony; SCC-162 stays open on `Try the lane on something real`.
- **F30 / L's guard rides A4** — Part 12's `reset --hard` regression guard ships ARMED under A4's
  shape (a run_all guard over toolkit text, green at landing) and SCC-180 L4; not a separately quoted
  ruling.
- **F26 / `_RULE_POINTERS` rows are WARN (exit 1), never promoted to `rep.err`** — binding on this
  lane through § Gate's `0/0`; CONCERNS elsewhere. Promotion would be new blocking law and is out.

> ✅ ADOPTED (rev 2) — ⚠️ AUDIT FINDING (2026-08-15, F3): this row contradicts § ARMING — the ruling is RULED and CLOSED (A4 blocks, E3 blocks, strict-actions arms on a clean count); "§ THE ONE OPEN DECISION" no longer exists as a heading. Read the row as **RULED**; the ONLY thing owed is the word `approved`.

Nothing else blocks. The lane is cut and pushed, the manifest declares the riders, the residue is
absorbed. On the word, the build order is § Build order, item 1 first.

## Self-Audit (2026-08-15)

**Mode:** PRE-WORK (a plan exists; nothing is built). **Right-size: FULL** — the plan touches two new rules,
the live main-write gate + `.githooks/pre-push`, scripts other scripts import (`jira_feed.py`,
`task_preflight.py`, `closeout_preflight.py`, `gate_receipt.py`), and every platform door of 14 commands.
**Auditor:** an independent session, not the plan's author. **Step 0 (from `git rev-parse`, not memory):**
`Repo: SCC-164-command-surface-family | Branch: chore/SCC-164-command-surface-family | HEAD: b6c6fb8`
(= origin/main a0aceaf + 6 plan/memory commits; toolkit files read here equal a0aceaf). Plan audited: this
file. Ticket: SCC-164 (index) + 13 subtasks, each read via `acli jira workitem view` for its ACCEPTANCE block.
⚠ **Line refs below are to the plan as of b6c6fb8**, i.e. BEFORE this audit's 14 inline `⚠️ AUDIT FINDING`
lines were inserted (each insertion shifts what follows by one line).

**Phases walked, one line each**
- **Phase 0** — change set named (13 parts; ~35 files: 2 new rules, 1 new script, 2–3 new test files, 7 scripts/hooks, 14 commands, SOP, memory already committed). Checkable list = the 13 subtasks' ACCEPTANCE blocks (J1–J5, K1–K6, A1–A6, B1–B6, H1–H5, F1–F5, C1–C4, G1–G6, D-a–D-d, E1–E7, I1–I6, L1–L5; SCC-170 has ASSERT-FIRST + WHAT-MAKES-IT-WORK). Traceability: **L1–L5 → no plan step (F1)**; SCC-170's "parent-index write is READ BACK" guard → no step (F23); I1's "story lane's counterpart" → no step (F24); B3 → a step that cannot meet it (F7). Lane check: no deployable path (`backend/ frontend/ firebase/ functions/ mobile/ .github/`) is touched — Task lane, closes via `/smh-close-task-merge-tree`. ✅
- **Phase 1** — line citations verified against the tree: `gate_receipt.py:15-18/:98/:142-144/:169-173/:304` ✅ · `task_preflight.py:155-200` (expect-key vs branch key) ✅ · `riders:` mechanism (SCC-156) exists at `task_preflight.py:251-300, :571-680` ✅ · `--strict-actions` exists, disarmed, `jira_feed.py:1541, :1979` ✅ · `mint-push-token.sh:118-123` case block + unguarded redirect `:132-142` ✅ · `pre-push-main-approval.sh:43-48` case block, `:148-171` D1/D2 shape ✅ · `pre-push-merge-backstop.sh:95` prints `--hard` ✅ · `.githooks/pre-push:71-73` UNCHECKED fail-open ✅ · `smh-quick-dev.md:118, :281-306` ✅ · `smh-close-task-merge-tree.md:434-438` tick instruction ✅ · `smh-plan-task.md:99` ✅ · `cicd-push-e2e.md:13` ✅ (+ `:134`, unlisted) · `test_review_engine.py:139-141` prose pin ✅ · `step-01-review.md:352/:372/:382/:398` ✅ · **`jira_feed.py cmd_check :1652 / :1696-1720` STALE — those are 8ae2e25 numbers; at a0aceaf `cmd_check` is `:1795`, the explain-away `:1839-1863` (F9)**. Bare-`main` census reproduced: **20 hits / 10 files** exactly as listed ✅. E4 census: 142 walkthroughs ✅ · 12 `lenses_run` ✅ · Verdict 44 by closeout's lenient regex / 34 by task_preflight's strict one (plan says 45 — within noise; the parser must say which regex counts, F19). `test_stale_base_refs.py`, `mutation_sweep.py`, `work-consolidation.md`, `port-checklist.md` do not exist ✅. `run_all.py` **auto-discovers** `test_*.py` (F10). Doors: all 14 touched commands carry `.agents/commands` + `.agents/skills` + `.claude/skills` + `.opencode/commands` + `.agents/workflows` (cicd-mobile-error-team is claude-only by design); re-sync = `sync-agents.ps1`, `pwsh` present on this Mac. `_RULE_POINTERS` covers 3 rules; plan silent (F12). Script ownership: `test_main_push_gate.py` owns mint + main-approval, `test_git_hooks.py` owns the backstop (F11). Arming markers: `MAIN-PUSH-ENFORCE`, `SOP-ENFORCE`, `JIRA-ENFORCE`, `MERGE-TARGET-ENFORCE` present; `core.hooksPath=.githooks` set on this machine (relative — F22). SOP-in-same-commit: seven parts omit the SOP (F14). Memory rows: the lane's memory writes are already committed (recovery of another session's destroyed work + reconciliation, recorded in § Residue); the plan schedules no further memory edits ✅; the three untracked copies in the main checkout are identical to the lane's and § Risks already carries the `cmp`+`rm` step ✅. `jira.md:213/:347` carry the old rider wording (F13).
- **Phase 2** — tripwires: new rule ×2 — `work-consolidation` is operator-ordered (SCC-170's title) but overlaps `jira.md`'s rider rows (F13); `port-checklist` justified by H1 but items 4/6 already in `project-law.md` (cite, F16) · new script `mutation_sweep.py` — justified (K1: a command block cannot check itself) · **config flag no acceptance requires: `--strict-lenses` (F2) — CUT, the ruling forbids it** · **a gate that cannot fail: A4's empty-glob → count 0 → PASS (F15); mutation_sweep's empty table → "clean" exit 0 (F21)** · **rebuilding what exists: Part 1 step 3's RED cases are already GREEN (F5)** · prose pins presented as wiring: H's RED/mutants (F16) · clone-and-tweak: none — the smh⇄cicd divergence is stated (B1) ✅ · plan size proportional to 13 tickets ✅.
- **Phase 3** — pre-mortem: *other machine* — plan's gate block is `python3`-only (fine on the Mac; the PC runs `python`, say so once); C1's POSIX shim (F25) · *fresh clone* — the new checks are `run_all` tests and travel with the clone ✅; D3 is only live where `hooksPath` is set (already pinned by `test_main_push_gate` INSTALLED half) ✅ · *gate fires on someone else's commit* — A4's message must name the remedy (F15) · *escape hatch* — **E3 as written closes its own hatch (F4)**; D2's `--no-verify` for remote seeding is named ✅ · *empty input* — F15, F21; E3 missing roster = UNKNOWN ✅ · *four caches* — re-sync in Parts 1 and 5; parts 4, 6, 7, 9, 11 also edit command bodies and must re-sync too (state it once, in § Gate) · *sibling lands first* — none live (below) · *rollback* — per-part revert as a unit ✅; **irreversible: `finish --apply` = Jira transitions for SCC-162/163 mid-lane (F6), the 13 rider flips (ceremony-gated ✅), the live `.githooks/pre-push` (F22)**. Survivors: the silent one = A4 counting 0 files and passing; the other-machine one = the C1 shim; the fresh-clone one = none found.
- **Phase 4** — verdict below.

**Sibling lanes:** `git worktree list` from the main repo shows ONLY the main checkout (a0aceaf) and this
tree; `git branch -a` shows one other remote branch, `origin/claude/teaching-edition` (not a `chore/*`
lane, not checked out here). No landing-order dependency exists today. SCC-162's and SCC-163's lanes are
pruned local + remote (this is what breaks Part 9 step 6 — F6).

**Findings** (`file:line` · severity · failure scenario · disposition)

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| F1 | plan:1, :143 (no `# Part` for L / SCC-180); :61 "cut line", :439 "twelve-part" | **HIGH** | Builder reaches build-order row 12 with no steps, RED, mutants or files for L1–L5; the close-out flips SCC-180 to Done with nothing built. Rows 9 and 12 disagree on where L goes. | NEEDS-REVISION — add `# Part 12 — L (SCC-180)`; place with G. Inline note at row 12. |
| F2 | plan:401-402 (Part 11 step 3) vs :80-82 | **HIGH** | Builder builds a disarmed `--strict-lenses` the ruling forbids; E3 ships WARN. | NEEDS-REVISION — delete the parenthetical; E3 blocks. Inline. |
| F3 | plan:501 (STOP table row) + :433 (Non-goals) | MEDIUM | Dev team reads the last table first, stops for a ruling already given, or ships E3 WARN; "§ THE ONE OPEN DECISION" no longer exists. | NEEDS-REVISION — row → RULED; only `approved` is owed. Inline ×2. |
| F4 | plan:81-82, :98 (E3 "PASS/CONCERNS + dead = contradiction") vs `step-01-review.md:398` | **HIGH** | `dead` → CONCERNS floor is the engine's DESIGNED end state; under BLOCK a lane with a dead lens can never close and the promised escape (take the CONCERNS floor) is refused → `--no-verify` or forged `ok`. | NEEDS-REVISION — PASS+dead = contradiction; CONCERNS+dead = consistent; correct SCC-173 E3 too. Inline. |
| F5 | plan:193-195, :197-198 (Part 1 RED + mutant) vs `test_task_preflight.py:603, :623, :642` | **HIGH** | Both named RED cases are already GREEN; RED never reds; partial landing (§2h) never gets built and `check_children` still exits 2 on it; second mutant tests behaviour no step adds; cut-line `riders:` never trimmed. | NEEDS-REVISION — name the mechanism (`landing: partial` / `--partial`), re-aim RED, add or drop the mutant, trim riders at the cut. Inline. |
| F6 | plan:355-363 (Part 9 step 6) | **HIGH** | (a) both lanes PRUNED → tip unresolvable → G-ii can't compute; (b) SCC-162 held on `Try the lane on something real` (walkthrough:199), not the merge box; (c) `finish --apply` = Jira transition outside an operator-invoked ceremony. | NEEDS-REVISION — tip fallback (`Verdict @ sha` / merge `^2`); scope live acceptance to SCC-163; dry-run for evidence, `--apply` inside a ceremony. Inline. |
| F7 | plan:281-283 (B3 → 0) | MEDIUM | 213 hits in `.agents/` (95 in commands); one edit at `cicd-push-e2e.md:13` leaves 200+ and `:134`; the memory says the sweep is a separate confirmed-scope task. | NEEDS-REVISION — scope B3 to Part 5's files or plan the sweep + allowlist; operator's call. Inline. |
| F9 | plan:314-315 (`cmd_check :1652`, `:1696-1720`) | LOW | Stale 8ae2e25 numbers; at a0aceaf `:1795`, `:1839-1863` — a builder grepping lands in `cmd_flag`. | FIX citations. |
| F10 | plan:269-270 (`run_all.py` "registers it") | LOW | Auto-discovery (`run_all.py:11, :43`); a needless edit to the gate runner. | FIX — drop from list. Inline. |
| F11 | plan:341-342, :386-387 (`test_git_hooks.py (extend)`) | MEDIUM | `test_main_push_gate.py` owns mint + main-approval (12 refs); C/D cases in test_git_hooks fork the red-file. | NEEDS-REVISION — C/D extend `test_main_push_gate.py`; L extends `test_git_hooks.py`. Inline ×2. |
| F12 | plan:158-160 ("asserted by `test_rules_index` + door parity for the launcher") | MEDIUM | No such test; a rule has no door; the step's assertion is fictional; `_RULE_POINTERS` undecided. | NEEDS-REVISION — name the real assertion or add one; decide `_RULE_POINTERS`. Inline. |
| F13 | plan:200-205 (Part 1 files) vs `jira.md:213, :347` | MEDIUM | `jira.md` still says riders are the "operator orders" exception → two rules diverge on who decides. | NEEDS-REVISION — add `jira.md` to Part 1's files. Inline. |
| F14 | plan:212-213, :288-291, :327-328, :341, :366-367, :386-387, :415-420 (no SOP) vs :471 ("no `[sop-ok]`") | MEDIUM | `sop_currency.py:72-77` classifies commands/rules/scripts/git-hooks as usage surfaces → seven parts' commits REJECTED at commit time. | NEEDS-REVISION — SOP row in every part's commit, or authorise `[sop-ok]` per part; gate line and file lists must agree. Inline at § Gate. |
| F15 | plan:257-266 (A4 test + allowlist) | MEDIUM | Line-number-keyed allowlist breaks on the next edit and lets a new hit at the old line pass; empty glob → count 0 → PASS. | NEEDS-REVISION — key on (file, exact line text, reason); assert ≥10 files; message names remedies. Inline. |
| F16 | plan:295-306 (Part 6 H2/H3/H4 + mutants) | MEDIUM | `/smh-self-audit` is prose; "the audit's check" and "delete the trigger" are prose pins — vacuous by § How the guards are written; H4 is a manual read. | NEEDS-REVISION — name the mechanical piece (script) and pin its wiring, or state H ships as prose and drop the RED/mutant claims; cite `project-law.md` for items 4/6. Inline. |
| F17 | plan:318-321 (F2 manifest lookup) | LOW | Scope of "task.yaml `branch:`" unstated — current lane only → every LANDED lane's record reads FORK. | FIX — every `_artifacts/**/task.yaml` in the committed tree + local + `origin/` branches. |
| F18 | plan:349-352 (G "reads HEAD") | LOW | `--walkthrough` is a filesystem path; which repo's HEAD, resolved how, is unstated. | FIX — `git -C <toplevel-of-path> show HEAD:<rel>`. |
| F19 | plan:391-394 (E4 cutoff / census) | LOW | Date source (folder prefix vs Verdict commit) and the counting regex (44 lenient / 34 strict vs "45") unnamed. | FIX — cutoff = folder date; roster required when the reader's own Verdict regex matches. |
| F20 | plan:404-410 (I3 "detects") | LOW | The engine is a skill; only the roster carries evidence. | FIX — header `inline` + any lens `ok` → parser flags; `recovered-inline` is the only legal state under `inline`. |
| F21 | plan:227-241 (mutation_sweep) | LOW | An EMPTY table exits 0 as a "clean sweep". | FIX — empty table = refusal, one case. |
| F22 | plan:379-381 (D3 edits `.githooks/pre-push`) | LOW | `hooksPath` is relative → the worktree's edited hook is LIVE for this lane's own pushes on save. | FIX — build last, prove in scratch, push once. Inline (with F11). |
| F23 | SCC-170 "parent-index write is READ BACK after every edit" | LOW | Ticket's one mechanical guard has no plan step. | FIX — add a step or state the deliberate omission. |
| F24 | SCC-177 I1 "the story lane's counterpart" | LOW | Part 11 step 6 names `smh-quick-dev` only. | FIX — name `cicd-dev-story-tests` / `cicd-quick-dev`, or state the omission. |
| F25 | plan:332-335 (C1 PATH shim) | LOW | A POSIX `git` shim is not a `git.cmd`; PC behaviour unstated ("the other machine"). | FIX — skip-with-reason or a `.cmd` twin. Inline (with F11). |
| — | plan:251-256 (20/10 census), :396 (E4 142/12), :51-53 (key gates), :6-7 (riders exist), :83 (`--strict-actions` exists), :129-146 (overlap map) | — | Verified correct against the tree. | SAFE. |

**Four quick gates**
- **Verification strategy present?** Per part yes (RED / GREEN / mutants / negative control) — EXCEPT Part L (absent, F1), Part 1 step 1 (a named test that does not exist, F12), Part 6 (prose pins presented as wiring, F16), and Part 1 step 3 (a RED that is already green, F5).
- **Anything irreversible?** Yes — `finish --apply` transitions SCC-162/163 to Done mid-lane (F6: gate it inside a ceremony); the 13 rider flips + parent (inside `/smh-close-task-merge-tree`, operator-invoked ✅); the live `.githooks/pre-push` edit (F22); memory-store writes are already committed as recovery, recorded ✅. No delete, no history rewrite.
- **Any step vague enough that the builder will guess?** F5 (partial-landing mechanism), F15 (allowlist keying), F16 (H's mechanical trigger), F17 (manifest scope), F18 (which HEAD), F19 (cutoff date + regex), F20 (I3 wiring), F7 (B3 scope).
- **Convention fit?** Doors ✅ · artifacts in the tree ✅ · one-door-per-platform ✅ · red-file ownership ✗ (F11) · SOP-in-same-commit ✗ (F14) · rule-tier reconciliation ✗ (F13) · commit key policy ✅ (child key per commit, parent on the merge — verified against `commit-msg-jira.sh` + `task_preflight.py:193-200`).

**Per-item:** F1, F2, F4, F5, F6 → **UNSAFE as written** (each would build the wrong thing or a thing that cannot pass its own acceptance) · F3, F7, F11–F16 → NEEDS REVISION · F9, F10, F17–F25 → SAFE with the one-line fix · everything else → SAFE.

**What flips this to GO:** adopting the 14 inline `⚠️ AUDIT FINDING` lines as plan text (they are prescriptive; only F1 needs new prose — a Part 12 — and F6/F7 need the operator's word on SCC-162's remaining box and B3's scope), then re-running Phases 0 and 2 for Parts 1, 5, 6, 9, 11 and the new Part 12 only. No re-planning of the other parts is needed; the build order, the ruling, the census and the citations otherwise hold.

Audit verdict: NO-GO

## Self-Audit re-run (2026-08-15, rev 2)

**Mode:** PRE-WORK re-run of the phases rev 2 touched (Phase 0 + Phase 2 for Parts 1, 5, 6, 9, 11 and the
new Part 12; a Phase 4 consistency pass over the whole plan). Same auditor, same worktree; toolkit files
still equal a0aceaf. Adversarial only on the NEW text. Line refs = the plan as of rev 2 BEFORE this
section's four inline `⚠️ AUDIT FINDING (rev 2, F#)` lines were inserted.

**Phases re-walked, one line each**
- **Phase 0 (traceability)** — Part 12 now carries L1–L5 (RED with the SOP:862 pass fixture and backstop:95 fail fixture, `--keep` banner, DIRTY/CLEAN drill ×2, git-policy.md + SOP row, arming under A4's shape); F23 → Part 1 step 7 (`jira_feed.py index-row`, RED via the existing acli stub — the stub IS a real executable, test_jira_feed.py:14) ✅; F24 → Part 11 step 6 names `/cicd-code-review` Step 0 ✅; every ticket ACCEPTANCE item now traces to a step; `reset --hard` census re-measured: exactly 2 hits under `.agents/` + `docs/` (backstop:95 imperative, SOP:862 prose) — L1's count is 1 ✅. Lane check unchanged (no deployable path).
- **Phase 2 (tripwires, touched parts)** — Part 1: `landing: partial` is one manifest key, no flag; the declaration-error case is now a step ✅; `_RULE_POINTERS` rows are the house convention (no new gate class) but their **severity and regexes are mis-stated (F26)**. Part 5: B3 scoped per-file, sweep recorded not done ✅ (operator's call named at § STOP). Part 6: H honestly declared prose + one wired row ✅; **its regex is wrong on the tree (F26)**. Part 9: tip fallback ladder ✅ (Verdict sha → 31ce965 / eb9030b both ancestors of origin/main, verified again); HEAD read defined ✅; live acceptance scoped to SCC-163, dry-run mid-lane, `--apply` inside the close-out ✅; **the merge-row recogniser is undefined and the literal it names is not what SCC-163's walkthrough says (F27)**. Part 11: E3 = PASS+dead blocks / CONCERNS+dead passes / missing-roster-post-cutoff blocks / no `--strict-lenses` ✅; I3 wiring via the roster ✅; cutoff source named ✅ but the constant is relative to "the day E lands" (F28). Part 12: proportional, from the code, red-file ownership correct ✅. No clone-and-tweak, no unrequired flag, no gate that cannot fail among the new text.
- **Phase 4 (consistency pass)** — § ARMING clause 2, the ARMING table's E3 row, Part 11 step 3, Non-goals bullet 3 and the § STOP row all now say the same thing (PASS+dead blocks; CONCERNS+dead passes; missing roster post-cutoff blocks; no `--strict-lenses`) ✅ · build order rows 9–11 = G+L, D (D3 last), E+I; Part 12's heading says "lands WITH Part 9 (G)" ✅ · "thirteen" in the title, § Why one lane, § Risks, § Close-out ✅ · SOP-per-commit rule at § Gate + SOP listed in every part's files, `[sop-ok]` reserved for no-usage-surface commits, gate line agrees ✅ · red-file ownership: Parts 8 and 10 → `test_main_push_gate.py`, Part 12 → `test_git_hooks.py` ✅ · F6 scoping identical in Part 9, § Close-out and § STOP ✅ · F7 scoping identical in Part 5 and § STOP ✅ · F5 mechanism + trimmed riders in Part 1 step 3 ✅ (range of the `git log --grep` unstated — F29) · F12 → `_RULE_POINTERS` rows in Parts 1 and 6 ✅ (F26) · F23 → `index-row` ✅ · § STOP has one owed row and names the two rule-1 calls ✅. One coverage gap: L's arming rides A4 by shape and by SCC-180's own L4 clause; the operator's quoted words name A4/E3 only — list it beside the two rule-1 calls at § STOP so `approved` covers it by the word, not by inference (F30).

**The workflow_lint warn-vs-error question, answered from the code.** `check_rule_pointers` calls `rep.warn`
(workflow_lint.py:90-93). `wf_common.Report.exit_code()` returns `2 if errors else (1 if warnings else 0)`
(wf_common.py:359-361), and `main()` returns exactly that under `--toolkit-only` (workflow_lint.py:510-523),
after running `check_rule_pointers` inside the `if lobby:` block (:500-503). So a new row produces
**exit 1 and names the file** — a real, observable RED, but a WARN, not an ERROR. What treats it as red:
this plan's own gate line (`workflow_lint --toolkit-only # 0/0`) and `smh-quick-dev.md:141/:240`. What does
NOT: `smh-code-review.md:200/:304` (warnings → CONCERNS, errors → FAIL); a receipt stamped with
`--warn-exit 1` (`gate_receipt.py:216-221`: "advisory findings only … not blocking"); and `run_all`, which
never lints the live repo's rule pointers (test_workflow_lint.py:398-405 asserts only ap-twins on the live
tree). Conclusion: the plan need NOT say the row lands as an ERROR, and it must NOT — promoting
`check_rule_pointers` to `rep.err` would turn all five rows into a blocking gate on every close-out, which
is new law outside the quoted ruling. The plan needs one line saying: WARN / exit 1 / named file; binding on
this lane through § Gate's `0/0`; CONCERNS elsewhere. That line is F26 (inline, Parts 1 and 6).

**New findings** (`file:line` · severity · failure scenario · disposition)

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| F26 | plan:176-183 (Part 1 step 1), :227-231 (RED first), :365-373 (Part 6 step 3) | MEDIUM | (a) "fails `workflow_lint`" is stated without severity: it is a WARN / exit 1 (workflow_lint.py:90-93, wf_common.py:359-361), binding here only via § Gate's `0/0`, CONCERNS/advisory elsewhere; a builder may "fix" it by promoting to `rep.err` (new blocking law, five rows). (b) The regex sketches are wrong on a0aceaf: `riders:` matches only `smh-close-task-merge-tree.md`; "one worktree" matches six unrelated cicd bodies; `\bport\b` matches six files (cicd-e2e "port 3100", cicd-live-testing-team `--port`, smh-code-review:213, cicd-autopilot-deepseek4, two AP twins) and none of H's three commands — RED names the wrong files, and the tip's `0/0` becomes unreachable. | NEEDS-REVISION (baked in, inline ×2): state WARN/exit 1 + no promotion; key each row on the exact phrase the part introduces (`riders:`/`landing:`; `port-checklist` / "exists in more than one repo"); RED captured in two steps AFTER the step text lands without the citation. |
| F27 | plan:435-443 (Part 9 "Settled here"), :445-459 (steps 1, 6) | MEDIUM | `open_actions` (jira_feed.py:1306-1340) has no merge-row concept; SCC-163's live row is `**Merge and close out** — /smh-close-task-merge-tree --expect-key SCC-163` (walkthrough:250), SCC-162's was `**Land it**` — a literal "The merge itself" match HOLDS SCC-163 and the scoped live acceptance fails; a loose match could auto-satisfy an operator's real "decide whether to merge X" row. | NEEDS-REVISION (baked in, inline): fail-safe recogniser (names a merge door, or merge/land + main/close-out) AND ancestor check; SCC-163's real row as the fixture + a no-door negative fixture. |
| F28 | plan:497-501 (E4 cutoff "the day E lands") | LOW | If E lands after 2026-08-15 this lane's own `2026-08-15_…` walkthrough is legacy — the lane that builds E3 is the first it does not bind. | FIX (baked in, inline): pin the literal `2026-08-15`. |
| F29 | plan:206-208 (Part 1 step 3 `git log --grep=<rider-key>`) | LOW | Range and repo unstated — "grep reads the branch you are parked on". | FIX: `git -C <repo> log $(git merge-base origin/main HEAD)..HEAD --grep=<KEY>`. |
| F30 | plan:581-583 (Non-goals bullet 3), Part 12 step 5, § STOP | LOW | L's guard is armed by shape (A4) and by SCC-180 L4, not by the operator's quoted words (A4/E3 only). Not new law by the plan's own reasoning (a run_all regression guard, on no shipping path), but `blocking-gates-need-a-quoted-ruling` prefers the word to the inference. | FIX: add "L's guard rides A4" to § STOP's list of calls that `approved` covers knowingly. |
| F31 | plan:529-530 (Part 11 files "task_preflight.py (or a shared walkthrough_roster.py)") | LOW | "ONE parser called by both" already means a shared module; the "or" leaves the builder to guess. | FIX: `walkthrough_roster.py`, imported by both preflights. |
| — | Parts 5, 12, § Gate SOP rule, § STOP, § Close-out, build order, "thirteen", red-file ownership, F5/F6/F7/F12/F23/F24 adoptions | — | Verified consistent and correct against the tree. | SAFE. |

**Sibling lanes:** unchanged — only the main checkout (a0aceaf) and this tree; no landing-order dependency.

**Four quick gates (delta):** verification strategy — now present for every part, incl. Part 12 ✅ (F26 corrects two REDs' claimed subjects, F27 adds the fixture G2 needs) · irreversible — `--apply` for SCC-163 is inside the operator-invoked ceremony ✅; nothing else new · vague — F26 (regex), F27 (recogniser), F29 (range), F31 ("or") · convention fit — SOP-per-commit, red-file ownership, doors, prefix law all now hold ✅.

**Verdict.** The five UNSAFE items of the first audit (F1, F2, F4, F5, F6) are resolved in the text; the
remaining two MEDIUM findings (F26, F27) are fully specified corrections that change no scope, no ruling and
no acceptance item, and are baked into the plan as inline `⚠️ AUDIT FINDING (rev 2, …)` lines that the builder
reads as plan text (F26's severity line and F27's recogniser + fixture are binding). No decision is left for the
operator beyond the word `approved`, which § STOP names as covering the F6/F7 calls (add F30's L line to that list).

Audit verdict: GO
