# SCC-119 — Subtask rule: the ticket you were handed is the top-level unit

**Ticket:** SCC-119 `Sub task rule` (Task, `To Do Next`) · **Lane:** Task (`/smh-quick-dev` → `/smh-close-task-merge-tree`)
**Branch:** `chore/SCC-119-subtask-rule` off `main`, own worktree · **Date:** 2026-08-12 · **Status:** awaiting approval

---

## 1. Ground truth — the pattern is already live, and the code refuses it

Read off the board 2026-08-12, not assumed:

| Parent (Task) | Children (Subtask) | Parent status |
|---|---|---|
| SCC-116 `Research deepcode review` | SCC-122 … SCC-129 (8) | `In Progress` |
| SCC-38 `Assess Prime Freatures for CI/CD` | SCC-130 … SCC-134 (5) | `To Do Next` |
| SCC-98 `Harden /smh-merge-multiple-workingtrees` | SCC-120 (1) | — |

**SCC-116's own description already states the rule:** *"make all the tasks sub tasks to these two tasks for
organization."* SCC-119 promotes a hand practice to law. **AVCH carries zero Subtasks** — the two boards
already differ exactly along the split this plan formalizes.

**Six places in the toolkit fight the pattern. One is a proven live defect:**

| Site | Behaviour today | Consequence |
|---|---|---|
| `jira_feed.py:1070` `start` | `wf.die("… is a Subtask - start the parent it belongs to")` → **exit 2** | ⛔ **Live defect.** `post-commit-jira-start.sh` writes its once-per-branch marker **only on exit 0**. On `chore/SCC-123-evidence-extract` it never marked → re-fired a board round-trip on **every commit** of that branch, silently (both streams are `>/dev/null`), and SCC-123 read `To Do` for its whole build. That is the exact failure SCC-113 was built to close, returning through the type check. |
| `jira_feed.py:1157` `flag` | refuses: *"a container is never a Bug"* | Factually wrong for Subtask — `hierarchyLevel: -1` is a **leaf**. It ships code and breaks like any Task, but cannot be flagged. |
| `jira_feed.py:820` `devrecord --closing` | restores a flagged ticket via `work_type()`, which returns only `Story`\|`Task` | A flagged Subtask restores as a **`Task`** — silently promoted out of its parent. Same defect class as the SCC-49 restore-only-to-`Story` bug that stranded Tasks as permanent `Bug`s. |
| `jira_feed.py:859` `audit` | `if have in ("Epic","Subtask","Sub-task"): continue  # containers` | Wrong reason, and nothing ever checks the invariants that do matter for a subtask. |
| `work_type()` / `mint` | cannot produce a Subtask at all | No wired seam — all 14 on the board are hand-made. |
| `smh-quick-dev.md:91` | exit `2` = *"a `Done` key …, **a Subtask**, or a move that did not land"* → **"stop.** … mint one at the seam" | The documented instruction on meeting a Subtask key is to **abandon the ticket and mint a duplicate**. |

`task_preflight.py` is clean by accident: it is local-only (branch name + `jira.conf`), never reads the
board, so it is type-agnostic — which is why SCC-123 still merged.

**Two `acli` facts, hit directly, worth recording:** `parent` is **rejected** on `workitem search --fields`
(*"field 'parent' is not allowed"*) but **accepted** on `workitem view --fields`, and `parent = SCC-116`
works as JQL. `view --json` without `--fields` returns only `assignee, description, issuetype, status,
summary` — a parent read **must** name the field.

---

## 2. The rule (new §Subtasks in `.agents/rules/jira.md`)

### 2.1 Hierarchy — three levels, and it does not nest

| Level | Type | Parent must be |
|---|---|---|
| 1 | `Epic` | — |
| 0 | `Story` · `Task` · `Bug` | an `Epic` |
| **−1** | **`Subtask`** | a **`Story` or `Task`** — never an `Epic` |

⛔ **A Subtask cannot have children.** A subtask that turns out to need its own breakdown has two legal
moves: keep the breakdown as a checklist inside it, or promote it to a `Task` and re-parent its siblings.

⛔ **The parent is still not the type discriminator.** Everything is parented (jira.md §Work-item types).
What decides `Subtask` is the **parent's type**: parent is an `Epic` → the ticket is `Story`\|`Task`;
parent is a `Story`\|`Task` → the ticket is a `Subtask`. That is the only reliable read, and it is one
`view --fields parent` call.

### 2.2 The ONE test — does a durable decomposition artifact already exist in the tree?

| Lane | What already holds the breakdown | Subtasks? |
|---|---|---|
| **BMAD Story** (AVCH) | the story file's `Tasks / Subtasks` section + its `sprint-status.yaml` row | ⛔ **NEVER** |
| **Command-centre Task** (SCC) | nothing — the ticket description **is** the spec | ✅ **the only place it can live** |

This is the same question `work_type()` already asks (*is this BMAD sprint work?*), so it adds no new
axis to the type system. A Story's breakdown is already written down and machine-joined (`jira_key:`
frontmatter, a YAML row key that never changes) — mirroring it onto the board makes a second copy that
nothing syncs and that drifts on the first edit of either side. A Task has no such file: flatten its
pieces into sibling Tasks under the grouping epic and the fact that they are **one job** is destroyed.

### 2.3 The threshold — a piece earns a Subtask when it earns its own branch AND its own worktree

One worktree = one branch = one key = one ticket = one gate run = one merge. That is the unit the whole
machinery is already keyed to: Atlassian's GitHub app links commits **by branch name**, `task_preflight.py
--expect-key` binds branch↔ticket, and `post-commit-jira-start.sh` parses the key **out of the branch**.

**A ticket with no branch is a row nothing will ever write to** — no commits, no Dev Record, no
transitions. That is board noise, which is the thing this rule exists to prevent. Everything below the
threshold stays a checklist line in the parent's `ACCEPTANCE` block or in `implementation_plan.md`.
Three edits in one commit are not three subtasks.

### 2.4 The mint seam — agent proposes, operator approves

A **fourth** entry in jira.md §Who mints tickets, and the only one that stops:

> **Subtasks** → `/smh-quick-dev`, **after** the `implementation_plan.md` is approved. The agent prints
> the proposed set — one line per subtask, each naming the branch it will get — and **writes nothing to
> the board until the operator says go.** Minting from a first read of the ticket is speculative work
> (guardrail 3) and placement stays the operator's (guardrail 2).

Both live cases already worked this way: SCC-116's children were minted from
`_artifacts/_main/2026-08-12_scc-116-house-review-engine/implementation_plan.md`.

### 2.5 Lifecycle

| Moment | What happens |
|---|---|
| first commit on `chore/<SUBTASK-KEY>-<slug>` | `post-commit` → `start` moves **the subtask** to `In Progress`. **The child only** — see the cascade ruling below |
| subtask close-out | `/smh-close-task-merge-tree` — unchanged; a subtask lands its own branch and goes `Done` on its own, exactly like a Task (SCC-122 and SCC-123 already did) |
| **found broken** | ⭐ **flag the PARENT, never the subtask** (operator ruling 2026-08-12). A subtask never wears `Bug`; breakage is recorded on the ticket that owns the job |
| **parent close-out** | **refused while any child is not `Done`** (`task_preflight.py`). The parent closes **last** — that is the moment the whole job is done |

> ✅ **F6 RESOLVED — the parent cascade is CUT (operator ruling 2026-08-12).** `start` on a subtask
> moves **only that subtask**. It stays one board write and one verdict, which is what
> `post-commit`'s write-the-marker-only-on-settled logic and the `0/2/3/4` exit contract both depend
> on. Change #5's `audit` reports *"parent is behind its children"* instead — the board still gets
> told, and nothing new can fail silently.

> ⭐ **The `Bug` ruling, and what it deletes (operator ruling 2026-08-12).** A subtask is **never**
> labeled `Bug`. If work under a parent turns out broken, the flag goes on **the parent** — the main
> ticket that owns the job. Three consequences, all simplifications:
> 1. `flag` keeps refusing subtasks. Only its **reason** changes: *"a container is never a Bug"* is
>    factually wrong (a subtask is a leaf, `hierarchyLevel: -1`) and must be replaced with the real
>    rule — *flag the parent that owns this job*.
> 2. **The §5 spike is DELETED.** It existed only to find out whether Jira permits a
>    `Subtask → Bug` conversion across its hierarchy boundary. Under this ruling nothing ever attempts
>    that conversion, so the question never gets asked. **This ticket now needs zero live board writes.**
> 3. Change #4 collapses from *restore a flagged subtask* to *never re-type one* — a guard, not a
>    feature. It is still required: today `work_type()` would answer `Task` and silently promote a
>    subtask out of its parent.

---

## 3. Change set

| # | File | Change |
|---|---|---|
| 1 | `.agents/rules/jira.md` | New §Subtasks (§2 above). Amend the §Work-item types table with the `Subtask` row; amend §Who mints tickets with the fourth seam; amend the §Guardrail 4 don't-double-move table with the parent cascade. **Law lives here** — it already owns the type table, the mint seams and the close-out routing; a separate rule file would split one law across two docs and give the INDEX two overlapping triggers. |
| 2 | `.agents/scripts/jira_feed.py` `start` | **Delete the `Subtask` refusal (L1070) — that is the whole change.** No cascade (F6 cut): one board write, one verdict, so `post-commit`'s marker logic is untouched. |
| 3 | `.agents/scripts/jira_feed.py` `flag` | **Still refuses `Subtask` — only the reason changes.** Replace *"a container is never a Bug"* (false: a subtask is a leaf) with the operator's rule: **flag the parent that owns the job**, and name the parent key in the message so the redirect is actionable. Keep the `Epic` refusal as-is. |
| 4 | ~~`devrecord --closing` guard~~ | ⛔ **CUT at build time — no code change. Test only.** Re-read against source: the restore block is `if have == "Bug":`. Under the operator's ruling a subtask **never** carries `Bug`, so a subtask never enters that branch — **the guard I planned defends a state our own rule makes unreachable**, which is Phase 2's *"error handling for states that cannot occur"* tripwire firing on my own plan. The only path in is a human hand-setting `Bug` in the Jira UI. **Disposition: no code; add a characterization test** pinning that a subtask through `devrecord --closing` is not re-typed, so a future edit cannot quietly introduce the promotion. Zero risk, zero surface. |
| 5 | `.agents/scripts/jira_feed.py` `audit` | Stop skipping Subtasks as "containers". Check the invariants instead: has a parent · parent is `Story`\|`Task` (not `Epic`, not `Subtask`) · parent not `Done` while the child is open. Keep the `Bug` hands-off skip. |
| 6 | ~~`mint --parent-key`~~ | ⛔ **CUT at build time.** `mint` exists to **render a description from a story file** — that is its whole job, and a subtask has no story file, so `--parent-key` would have meant a second description source and a new create path. And it is not how this board works today: **Tasks are already minted with raw `acli`** (jira.md §Who mints: *"mint the repo's chore ticket before cutting `chore/…`"*), never through `mint`. A subtask is minted the same way its parent was. Phase 2 tripwire — *a flag no acceptance item requires*. **Disposition: document the exact `acli` form in jira.md §Subtasks instead.** AC4 is satisfied by the propose-then-approve **step**, not by a new flag. |
| 7 | `.agents/scripts/task_preflight.py` | Parent gate. **New dependency: this script currently makes zero board calls.** Soft-fail on transport — unreachable board = `warn`, never `err` (same contract as `start`'s exit 4: transport is not a verdict, and the operator commits from planes → `github-408-on-satellite-uplink`). A reachable board reporting open children is a hard `err`. ⚠️ **AUDIT FINDING F3 + F8 — as first drafted this is a gate that cannot fail. Three corrections are binding, see §4a.** |
| 8 | `.agents/commands/smh-quick-dev.md` | Drop *"a Subtask"* from the Step 0.5 exit-2 row. New step after plan approval: propose the subtask set, stop for the operator, mint on go. |
| 9 | `.agents/commands/smh-close-task-merge-tree.md` | State the parent-last ordering as a step (`restate-alwayson-obligations-in-command-bodies` — agents follow the literal step list, so the obligation cannot live only in the rule). |
| 10 | `docs/_scc_sops_prds/workflows_testing_SOP.md` | **Mandatory, not optional.** #1–#9 change usage surfaces (`commands/*.md` · `rules/*.md` · `scripts/*.py`), so the armed `sop_currency.py` commit-msg gate **REJECTS** the commit without this doc staged in the SAME commit. ⚠️ **AUDIT FINDING F1** — the first draft named `_my_resources/_quick_reference/sudo_workflows_testing.md`, **which does not exist.** The gate's target is pinned at `sop_currency.py:60` (`SOP_DOC`). Building to the old path = a rejected commit with no obvious cause. |
| 11 | `.agents/scripts/INDEX.md` | ⚠️ **AUDIT FINDING F4 — missing from the first draft.** L40 documents `work_type()`, the *parent is never the tell* doctrine and `devrecord --closing`'s "restores to `Story` **or `Task`**"; L46 states `task_preflight.py` "resolves the repo **without** a board" and "reads and reports only". Changes #4, #5, #6 and #7 make all three sentences false. An INDEX that lies is worse than one that is silent. |
| 12 | `.agents/scripts/tests/test_jira_start_hook.py` | ⚠️ **AUDIT FINDING F2 (partial) — missing from the first draft.** The dedicated post-commit-recorder test. The marker-on-settled-only path is exactly what the Subtask refusal breaks, so the fix needs a case here, not only in `test_jira_feed.py`. |
| 13 | **8 platform doors** — `.claude/skills/`, `.agents/skills/`, `.opencode/commands/`, `.agents/workflows/` × {`smh-quick-dev`, `smh-close-task-merge-tree`} | ⚠️ **AUDIT FINDING F5 — missing from the first draft.** All 8 exist and were verified present. One door per platform per command (SCC-66): editing a command body without regenerating its doors leaves Codex/opencode/Antigravity reading the old steps. Regenerate via `/smh-sync-agents`; do not hand-edit. |

---

## 4. Gate (assert-first — the check fails BEFORE the fix)

`tests/test_jira_feed.py` and `tests/test_task_preflight.py`, run by `tests/run_all.py`:

1. `start` on a Subtask key returns `0`, not `2` — **must be seen red first** (it is the live defect).
   ⚠️ **AUDIT FINDING F2 — an existing test pins the WRONG behaviour and will go red.**
   `test_jira_feed.py:905` asserts verbatim: `c.check("start: a Subtask is refused", code == 2 and …)`.
   That assertion must be **INVERTED, not supplemented** — and the builder must be told, or the
   correct red reads as a regression and gets "fixed" back to the defect. Rewrite it as
   `"start: a Subtask is accepted — it is a leaf that carries a branch (SCC-119)"`, and keep the
   neighbouring `TEST-5` Epic case untouched (an Epic is still allowed, for different reasons).
2. `start` on a Subtask moves the parent too; a parent already `In Progress` is a no-op.
3. `flag` accepts a Subtask; still refuses `Epic`.
4. `devrecord --closing` on a flagged Subtask restores **`Subtask`** — asserted against a mutant that restores `Task`.
5. `mint --parent-key` refuses a `Subtask` parent (no nesting), a `Done` parent, and an `Epic` parent.
6. `audit` reports a parentless Subtask and an `Epic`-parented Subtask; still skips `Bug`.
7. `task_preflight` errs on a parent with open children; **warns** (not errs) when the board is unreachable.
8. `smh-quick-dev.md`'s exit-2 row no longer names Subtask — asserted on the **parsed table row**, not a
   bare grep (`comment-literals-invert-source-grep-tests`, `source-grep-guards-cannot-see-order`).

Every gate bare, never piped (`piping-a-gate-hides-its-exit-code`). Machine floor per `/smh-clean-code-audit`:
`run_all.py` · `workflow_lint.py` · `sop_currency.py` · `py_compile` · link+anchor.

### 4a. ⚠️ AUDIT FINDINGS F3 + F8 — the parent gate as drafted CANNOT FAIL. Three binding corrections.

Phase 2's *"a gate that cannot fail"* tripwire fires. The child query has **two** verified paths that
pass without checking anything, and no legitimate exit. Measured against the live board 2026-08-12:

| Probe | Exit | Rows |
|---|---|---|
| `--jql "parent = SCC-119"` (childless parent) | **0** | none |
| `--jql "parent = SCC-116"` (8 children) | **0** | 8 |
| `--jql "parent = SCC-116" --fields "key,parent"` | **1** | — *(`field 'parent' is not allowed` on search)* |
| `--jql "parent = SCC-99999"` (bad key) | **1** | — |

1. **Check the exit code, never the row count.** *"No children"* and *"the query failed"* are both
   **zero rows**, and they are opposite facts. Exit 1 must be an ERROR, never a pass. The
   `--fields "key,parent"` row is how this gets hit by accident — asking for `parent` is the natural
   thing to write when checking parentage, and it exits 1 every time.
2. **A `Deferred` child must not block — that IS the escape hatch.** Count children that are neither
   `Done` nor `Deferred`. A gate with no legitimate exit gets `--no-verify`'d into oblivion (Phase 3),
   and descoping through `Deferred` + the `descoped` label is the mechanism jira.md already defines.
   No `--force` flag: the escape is *fix the board*, which is auditable, not *bypass the gate*.
3. **The transport warn must be loud and must reach the VERDICT line.** `task_preflight.py` prints
   `clear to close out and merge` whenever the error count is zero — the exact reason `hooks_armed.py`
   findings were folded in as ERRORs (`scripts/INDEX.md:22`). A silent "couldn't reach the board" warn
   leaves that clean line standing over a check that never ran. It must name the unchecked ticket.

**Tests:** exit-1 → ERROR (asserted against a mutant that returns pass); a `Deferred` child does not
block; a childless parent passes for the *right* reason; the transport warn appears in VERDICT output.

---

## 5. ~~Spike~~ — DELETED by the `Bug` ruling (2026-08-12)

The spike asked whether `acli jira workitem edit --type Bug` can convert a **Subtask** — a change that
crosses Jira's subtask↔standard hierarchy boundary, which Atlassian normally refuses outside a move
operation. `acli` exposes no read-only probe (`view` has no `--expand editmeta`, and `--fields` cannot
reach it), so the only way to find out was **two scratch tickets and a live write**.

**The operator's ruling removes the question rather than answering it:** a subtask is never labeled
`Bug`, so nothing in this system ever attempts that conversion. Recorded here rather than deleted
outright, because *"can a subtask become a Bug?"* is the obvious next question for whoever reads
`flag`'s refusal — and the answer is **we deliberately never ask.**

⭐ **This ticket now requires ZERO live board writes to build and test.** Every gate in §4 runs against
the existing `acli` stub in `tests/`.

---

## 6. Acceptance criteria

**Confirmed with the operator in chat 2026-08-12** (F9 discharged). SCC-119 carries no `ACCEPTANCE`
block, so this list is Phase 0.3 authority 3 — written by the audit, stated in plain language, agreed.

| # | Done means… | Proved by |
|---|---|---|
| **AC1** | The rule is written into `jira.md`: the ticket you are handed is the top-level one, and work an agent breaks out of it goes underneath as subtasks. Carries the hierarchy, the no-nesting floor, the parent's-type discriminator and the lifecycle. | inspection + `workflow_lint.py` |
| **AC2** | **The story lane never does this.** A story file already holds its breakdown, so mirroring it would make a second copy nothing keeps in sync. | rule text; AVCH stays at zero subtasks |
| **AC3** | A piece earns a subtask only if it earns **its own branch and its own worktree**. Anything smaller stays a checklist line. | rule text |
| **AC4** | The agent **proposes** the subtask set after the plan is approved and writes nothing to the board until the operator says go. | `/smh-quick-dev` step; `mint --parent-key` validation (nesting, `Done` and `Epic` parents refused) |
| **AC5** | **Working on a subtask no longer breaks the board** — it reads `In Progress` like any other ticket, and the `post-commit` marker is written. *(The SCC-123 defect cannot recur.)* | `test_jira_feed.py` (inverted L905) + `test_jira_start_hook.py` |
| **AC6** | **The parent cannot close while any child is still open** — the whole job closes together at the end. | `test_task_preflight.py`, incl. §4a's exit-code and `Deferred` cases |
| **AC7** | **Subtasks are never labeled `Bug`.** Breakage is recorded on the main ticket, and `flag` says so. | `test_jira_feed.py`: `flag` refuses with the parent-redirect reason; `devrecord --closing` never re-types a subtask |
| **AC8** | Nothing instructs an agent to stop and mint a duplicate when it meets a subtask key, and the gates pass. | parsed-table assert on `smh-quick-dev.md`; `run_all.py` · `workflow_lint.py --toolkit-only` · `sop_currency.py`, all bare |

---

## 7. Scope notes

**SCC-119 gets NO subtasks — and that is the rule working.** The doc and the machinery must land
together (a rule the code refuses is a lie; code with no rule is unexplained), and one gate covers both,
so the whole change is one branch in one worktree. The threshold does not mean *subtask everything*.

**Out of scope:** back-filling the 14 existing Subtasks (they already sit correctly); any AVCH change
(the story lane's answer is *never*, which is its current state — the rule only writes it down);
retiring the grouping epics.

---

## 8. Self-Audit (2026-08-12)

**Mode:** PRE-WORK · **Repo:** `Sudo_Hatter_Command` @ `main` (echoed from `rev-parse`) · **Ticket:** SCC-119
**Right-size: FULL** — the plan touches a **rule** (`jira.md`), a **gate/hook** (`task_preflight.py`,
the `post-commit` recorder's marker path), a **script other scripts import** (`jira_feed.py`, called by
git-hooks and 7 command bodies), and **more than one platform surface** (8 doors).

**Phases walked:**
- **0 — scope / checkable list.** Change set re-derived: **13 items**, up from the 10 drafted (F1, F4, F5). Lane check **clear** — nothing touches `backend/ frontend/ firebase/ functions/ mobile/ .github/`, so `/smh-close-task-merge-tree` is the correct close-out, confirmed at plan time. Traceability both directions: no AC without a step; change #10 (SOP) traces to no AC but is gate-mandated, allowed.
- **1 — blast radius.** `jira_feed.py`'s caller set is **7 command bodies + 4 test files + 2 rules + `scripts/INDEX.md` + the post-commit hook**, far wider than the 2 commands drafted. `workflow_lint.py` `_RULE_POINTERS` holds only `git-policy` / `worktree-per-story` / `smh-target-resolution` — **no jira entry, no lint change owed** (cleared). All 8 platform doors verified present on disk (F5). Story-lane callers (`cicd-update-sprint-memory`, `cicd-write-story-tests`) share the `devrecord` code path — change #4 must be a **provable no-op** for `Story`/`Task`, since the story lane's answer is *never subtasks*.
- **2 — over-engineering.** Two tripwires fired: *generalizing beyond the acceptance list* (F6, the cascade) and *a gate that cannot fail* (F3). Cleared: no new command, no new rule file (jira.md extended deliberately, reason stated), no new script, no clone-and-tweak, no flag without an item behind it.
- **3 — pre-mortem.** Vacuous-green **CONFIRMED by measurement**, not suspected (F3 table). Escape hatch was **absent** (F8). Four platform caches **CONFIRMED at risk** (F5). Other-machine row clear — no new shell-outs; `python3`/`python` handled by the existing hook probe. Fresh-clone row clear — no new hook ships; the fix makes an *existing* recorder work. Rollback: no history rewrite, no delete; board writes are gated behind the propose-approve seam and the §5 spike.

### Findings

| # | Where | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| **F1** | plan §3 #10 vs `sop_currency.py:60` | **HIGH** | Plan named `_my_resources/_quick_reference/sudo_workflows_testing.md` — **the file does not exist.** Builder edits a path that isn't there; the armed commit-msg gate rejects the commit and the cause is invisible. | **FIXED in plan** → `docs/_scc_sops_prds/workflows_testing_SOP.md` (135 KB, exists) |
| **F2** | `test_jira_feed.py:905` | **HIGH** | `c.check("start: a Subtask is refused", code == 2 …)` pins the defect. The fix turns this green test red; a builder reads a correct red as a regression and reverts the fix. | **FIXED in plan** → §4.1, invert don't supplement; `test_jira_start_hook.py` added as change #12 |
| **F3** | plan §3 #7 | **HIGH** | Parent gate passes on zero rows. Verified: a bad key **and** the natural `--fields "key,parent"` both exit **1** with zero rows — identical to "no children". A wrong key reads as a clean pass. | **FIXED in plan** → §4a.1, gate on exit code, mutant-tested |
| **F8** | plan §3 #7 | MED | No legitimate exit for a descoped child → the gate gets `--no-verify`'d. | **FIXED in plan** → §4a.2, `Deferred` children don't block; no `--force` flag |
| **F4** | `.agents/scripts/INDEX.md:40,46` | MED | L40 documents the `work_type()` restore doctrine, L46 says `task_preflight.py` works "without a board" and "reads and reports only". Changes #4–#7 make all three false; the INDEX becomes an authoritative lie. | **ADDED** as change #11 |
| **F5** | 8 door dirs | MED | Editing 2 command bodies without regenerating doors leaves Codex / opencode / Antigravity running the old steps — including the "stop on a Subtask" instruction this ticket exists to delete. | **ADDED** as change #13, via `/smh-sync-agents` |
| **F6** | plan §2.5 cascade | MED | Second board write inside `start`, traceable to no ticket AC; breaks the one-verdict contract the `post-commit` marker depends on; "reported, never fatal" makes it silently skippable. | **CUT recommended** — `audit` reports parent-behind-children instead. **Operator decision** |
| **F9** | plan §6 AC1–AC8 | MED | SCC-119 carries **no `ACCEPTANCE` block** (its description is one sentence). Phase 0.3 authority 3 applies: the audit wrote the ACs, so they must be **echoed and confirmed** — an unconfirmed list is not a gate. | **Echoed below.** Confirm or amend |
| **F7** | `jira_feed.py:1070` | LOW | The `start` refusal is broken shipped work from SCC-113. Folding the fix silently into SCC-119 loses the signal; jira.md's own rule says a Task found broken wears `Bug`. | **Operator's call** — `flag` SCC-113, or note it in SCC-119's Dev Record |

**Sibling-lane landing order: NO dependency.** `chore/SCC-124-baseline-trial` holds only
`_artifacts/_main/2026-08-12_scc-124-baseline-trial/**` (committed) plus an untracked `runs/` dir;
`SCC-124-fixture-e6354d3` is a clean detached fixture. **Zero file overlap** with all 13 change items.
Either lane may land first.

### Four quick gates

- **Verification strategy present?** ✅ after revision — §4 names 8 assertions and §4a adds 4 more, each
  with the command that proves it. Before revision the parent gate had no falsifiable check at all.
- **Anything irreversible?** ⚠️ Yes, three: minting subtasks (board rows — gated by the propose-approve
  seam), the §5 `flag` spike (live board writes — already gated on operator sign-off), and Jira
  transitions. None rewrite history; all are reversible by hand. Gated, not blocked.
- **Any step vague enough that the builder will guess?** ⚠️ Was: "add a parent gate" (fixed by §4a's
  three rules) and "restore by parent type" — change #4 must state that a `Story`/`Task` under an
  `Epic` is **unchanged**, or a builder may re-type story-lane tickets. Tighten at build time.
- **Convention fit?** ✅ Law extends `jira.md` rather than forking a rule file; artifacts in
  `_artifacts/_main/<date>_<slug>/`; obligations restated as command **steps**
  (`restate-alwayson-obligations-in-command-bodies`); table-parse asserts over bare greps
  (`comment-literals-invert-source-grep-tests`); doors regenerated, never hand-edited.

### AC confirmation owed (F9)

AC1 rule text · AC2 `start` accepts Subtask **+ cascade — pending F6** · AC3 `flag` + `devrecord`
restore · AC4 `mint --parent-key` validation · AC5 `audit` invariants · AC6 parent gate · AC7 no command
says stop-on-Subtask · AC8 gate green bare. **Confirm, amend, or drop AC2's cascade half.**

```
Audit verdict: NO-GO   (superseded — see the resolution below)
```

### Resolution — all three unblocks answered 2026-08-12

| Unblock | Operator's answer | Effect on the plan |
|---|---|---|
| **F6** cascade | **Cut.** Subtasks sit under the parent; the parent is what closes at the end when the job is done. | `start` = delete the refusal, nothing more. One board write, one verdict; `post-commit`'s marker logic untouched. `audit` reports parent-behind-children instead. |
| **F9** acceptance list | **Confirmed**, restated in plain language in §6. | §6 rewritten as 8 plain statements, each with the check that proves it. |
| **§5 spike** | **Deleted by ruling** — a subtask is never labeled `Bug`; breakage goes on the main ticket. | No `Subtask → Bug` conversion is ever attempted, so the hierarchy-boundary question is never asked. `flag` keeps refusing, with the *correct* reason. Change #4 collapses to a guard. ⭐ **Zero live board writes to build or test this ticket.** |

**F7 closed with it:** the `start` defect will be recorded in SCC-119's Dev Record rather than flagged
as a `Bug` against SCC-113 — consistent with the same ruling, and lower ceremony for a defect whose fix
is landing in the very next commit.

**Net effect: the change set got smaller.** Change #2 lost the cascade, #3 became a message fix, #4
became a guard, and §5 vanished. F1–F5 and F8 were corrected in place. **No rebuild of Phases 1–3 is
owed** — every correction was re-derived from source rather than from the draft, and none widened the
blast radius.

```
Audit verdict: GO
```
