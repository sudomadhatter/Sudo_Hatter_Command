# SCC-271 — implementation plan

**Ticket:** SCC-271 (Subtask, Part B of SCC-262) · **Lane:** `chore/SCC-271-jira-feed-write-truth`
**Tree:** `.claude/worktrees/SCC-271-jira-feed-write-truth` · **Base:** `origin/main` @ `9d7863b`
**Lane type:** `/smh-quick-dev` (TASK — `lane_qualify` refused the light lane: toolkit paths)

---

## 1. Why this lane exists

Both defects were hit in one session, on SCC-269's own record-filing, by following the ceremony
exactly as written. They share one surface: **`jira_feed.py` writing to a ticket and then
misreporting what it wrote.** One cries loss that did not happen; the other causes a defect it
does not report.

## 2. Defect 1 — `index-row` reports its own correct write as data loss, and exits 2

**Measured.** `index-row --key SCC-262 --line "Part A - SCC-269 …" --apply` printed
`⛔ SCC-262's description was REPLACED and the read back is MISSING 1 line(s)` naming
`(empty - this cycle has taken no work yet)`, told the reader this is *"data loss, not a
formatting difference"* and to *"restore the ticket before doing anything else"* — then exited **2**.
Hand read-back: the INDEX was intact. Nothing was lost.

**Mechanism** — three lines, all correct on their own:

| Where | What it does |
|---|---|
| `jira_feed.py:2792` | `keep = [ln for ln in before.splitlines()]` — snapshots **every** prior line |
| `jira_feed.py:2744` | `kept = [ln for ln in body if not _INDEX_PLACEHOLDER_RE.match(ln)]` — `index_append` **deliberately** drops the placeholder; that is its documented job |
| `jira_feed.py:2822` | falsifies the read-back against `keep` — which still contains the line the command just intentionally removed |

The guard is asking "did every line survive?" when the command's own contract is "every line
survives **except** the placeholder I am replacing."

**Live confirmation, incidental:** filing this very ticket's Part B row onto SCC-262 — which now
carries a real Part A row and no placeholder — exited **0**: `67 prior line(s) intact`. The defect
fires on the **first** row of a fresh rolling ticket and only there.

**Why it is worth a lane.** (a) Exit 2 — a caller chaining on `&&` reads a good write as failure.
(b) The instruction it prints is to undo a correct write. (c) It fires on the most predictable use
of the command, and this guard is the one place `work-consolidation.md` puts a *mechanism* instead
of a policy — because real index loss (SCC-164's Part E row) is silent and unrecoverable. **A guard
that cries wolf on first use is a guard being trained out of the system.**

### Fix B1

Falsify against **what `index_append` composed**, not against everything that was there. `after` is
already computed locally at `:2801`, so the honest question is *"did the write land as composed?"*

```python
# :2822 — replace
lost = [ln for ln in keep if ln.strip() and ln.strip() not in
        {x.strip() for x in now.splitlines()}]

# with
seen_now = {x.strip() for x in now.splitlines()}
intended = {x.strip() for x in after.splitlines() if x.strip()}
lost    = [ln for ln in keep if ln.strip() and ln.strip() in intended
           and ln.strip() not in seen_now]
dropped = [ln for ln in keep if ln.strip() and ln.strip() not in intended]
```

- **The teeth are untouched.** A line that was in `before` **and** in `after` (i.e. one
  `index_append` promised to keep) but is missing from `now` — a concurrent writer's lost row, or
  acli mangling the field — still lands in `lost` and still exits 2 with the same message.
- **`dropped` is reported, not swallowed.** The success line at `:2836` gains
  `· replaced the INDEX placeholder` when `dropped` is non-empty. A deliberate deletion the operator
  cannot see is the same class of problem as the one this guard exists to catch.
- Deliberately **not** hardcoding `_INDEX_PLACEHOLDER_RE` into the guard: the guard should verify the
  composer's intent generically, so a future change to what `index_append` drops needs no second edit
  here.

## 3. Defect 2 — `--append-new` manufactures the state `check` calls a defect, and the ban lives only in prose

**Measured.** On SCC-269, `devrecord … --append-new` posted a **second** Dev Record under the **same**
story id. Both partials had to be deleted by hand and one complete record re-posted.

**Mechanism.** `cmd_devrecord:1045` — `if prior and not args.append_new:` → update, `else:` → create.
`find_devrecord(comments, story)` (`:614`) **already filters by story id**, so `prior` is non-`None`
*only when the id matches*. Therefore:

- **`--append-new`'s only reachable effect is "one id, two records"** — which `record_story_id`'s own
  docstring (`:634`) calls *"the failure SCC-49 wrote `check` for"*, and which `cmd_check` reports as
  a defect.
- The **legitimate** two-records case (two lanes, two different ids) **needs no flag**: `prior` is
  `None` and it creates anyway.

**The system already knows this — seven times, in prose, enforced by nobody:**

`smh-close-task-merge-tree.md:553, :600` · `smh-quick-dev.md:474` ·
`smh-merge-multiple-workingtrees.md:339` · `cicd-close-story-merge-tree.md:369` ·
`cicd-quick-dev.md:376` · `cicd-merge-epic-workingtrees.md:249` ·
`docs/_scc_sops_prds/workflows_testing_SOP.md:2204`

The flag's own `--help` says only *"post a SECOND record instead of updating (rare)"* — it does not
mention that every command in the system forbids it.

### Fix B2

Make the code enforce what the prose already says. At `:1045`, before the create branch:

```python
if prior and args.append_new:
    wf.die(f"{args.key} already carries a Dev Record for `{args.story}` and --append-new "
           f"would post a SECOND one under the SAME id - that is the two-records-one-id "
           f"state `check` reports as a defect (SCC-113). Drop the flag to UPDATE it in "
           f"place; or, if the existing record was filed under the wrong slug, delete that "
           f"comment and re-post under `{args.story}`.")
```

- Two lanes / two ids: `prior` is `None`, untouched.
- `--append-new` on a ticket with **no** prior record: `prior` is `None`, creates as before.
- `--help` updated to state the ban and the remedy.

**Considered and rejected: deleting the flag.** Cleaner in isolation, but it makes all seven
"never `--append-new`" lines reference a flag that no longer exists — stale docs across six command
bodies plus the SOP (which fires the SOP-currency gate). Keeping the flag and refusing the banned
case leaves every existing sentence **true and now enforced**, for a one-function blast radius.

**Not a defect, recorded so it is not re-litigated:** the second record also lacked its `Outcome`
line. That was operator error in the invoking call — no `--outcome` passed — not a code fault
(`render_devrecord:537` emits `Outcome` only when given one).

## 4. Assert-first — the RED cases, written before the fix

In `.agents/scripts/tests/test_jira_feed.py`, using the existing stubbed-`acli` harness (the
SCC-170 block at `:480` and the devrecord block at `:589` are the patterns).

| # | Assertion | Today |
|---|---|---|
| 1 | `index-row` onto an INDEX holding **only** the placeholder → exit **0**, row present, output carries **no** "data loss"/"MISSING" text | **RED** — exit 2 |
| 2 | …and the success line **says** it replaced the placeholder | **RED** — not reported |
| 3 | `devrecord --append-new` over a matching prior → exit **2**, refuses, names the remedy; ticket still carries **exactly one** record | **RED** — exit 0, two records |
| 4 | **Control (teeth):** a real prior row goes missing → still exit 2, still names the line, still says REPLACED | green, must stay green |
| 5 | **Control:** `--append-new` with **no** prior record still creates | green, must stay green |
| 6 | **Control:** `devrecord` without the flag still updates in place, one record | green (`:624-628`), must stay green |

**Mutants** (`mutation_sweep` table for this lane): revert B1 → case 1 red; revert B2 → case 3 red.
Each mutant must kill exactly the case that pins it.

### ⚠ One test is REWRITTEN, and that is called out on purpose

`test_jira_feed.py:631-633` currently asserts *"`--append-new`: opts out of the one-record rule"*
(exit 0, two comments). Fix B2 inverts that. **It is rewritten, not deleted** — it pinned a footgun;
it now pins the guard. Editing a test to match new behaviour is exactly how a vacuous green gets
made, so: the walkthrough states the inversion explicitly, and mutant B2 proves the new assertion
fails without the fix.

**Sequencing risk to verify during implementation:** that block currently leaves the stub ticket with
**2** comments, and later cases in the same block (the `swallow` negative at `:637`) run against that
state. After B2 it will hold **1**. Checked: no later assertion in the block counts comments — but
this is re-verified by running the file, not by reading it.

## Declared Change Set

- EDIT `.agents/scripts/jira_feed.py` — `cmd_index_row` read-back falsified against `after` + the success line reports a deliberate replacement; `cmd_devrecord` refuses `--append-new` over a matching prior; the `--append-new` `--help` string → B1, B2, B3
- EDIT `.agents/scripts/tests/test_jira_feed.py` — new placeholder-replacement block, new `--append-new` refusal block, and the inversion of the existing `:631` assertion → acceptance 1, 2, 3, 4
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — the `--append-new` ban at `:2204` gains one clause: it is now enforced by the script (exit 2), not only by instruction → ⚠️ AUDIT FINDING 1, acceptance 7
- EDIT `.agents/scripts/INDEX.md` — the `devrecord` prose at `:47` gains one clause for the refusal → observation 1 (optional; drop if it reads as padding)

## 5. Blast radius

| Touched | Not touched |
|---|---|
| `.agents/scripts/jira_feed.py` — `cmd_index_row` read-back + success line; `cmd_devrecord` guard; one `--help` string | `index_append` itself (correct as written) · `find_devrecord` · `cmd_check` · the update-in-place path · the no-INDEX-heading early return · the empty-description refusal |
| `.agents/scripts/tests/test_jira_feed.py` — 2 new blocks, 1 assertion inverted | any command body · the SOP · any rule |

> ⚠️ **AUDIT FINDING 1 — this paragraph was wrong, and it would have stopped the build at the first
> commit.** `sop_currency.py:77` lists `(".agents/scripts/", (".py", ".ps1"), "the safety-net
> scripts")` as a gated surface, and `_EXEMPT_PREFIXES` at `:82` exempts **only**
> `.agents/scripts/tests/`. So editing `jira_feed.py` trips the **armed** commit-msg gate: the commit
> is rejected unless `docs/_scc_sops_prds/workflows_testing_SOP.md` is staged in the same commit.
> **The SOP genuinely needs the edit** — after B2 a command that used to succeed exits 2, which is an
> operator-facing behaviour change, so the ban at `:2204` gains a clause saying it is now enforced.
> `[sop-ok]` is **not** the right answer here; it is the logged opt-out for changes that carry no
> usage consequence, and this one does. The SOP is now in the Declared Change Set above.

## 6. Steps

1. Write the six assertions above. **Run them. Prove 1–3 are RED** against unmodified code — paste
   the failure output into the walkthrough.
2. Apply B1 (`cmd_index_row`), then B2 (`cmd_devrecord` + `--help`).
3. Re-run: 1–3 green, 4–6 still green.
4. Mutant sweep: one mutant per fix; each kills its own case; restore verified.
5. Gates, bare: `run_all.py` · `workflow_lint.py --toolkit-only`.
6. Walkthrough + `task.yaml` + `_main/INDEX.md` row + Dev Record. Hand back for
   `/smh-close-task-merge-tree`.

> ⚠️ **AUDIT FINDING 3 — absorb `main` before step 6's ledger row.** The live SCC-269 lane's change
> set includes `_artifacts/_main/INDEX.md`, the same ledger this lane appends to. **SCC-269 lands
> first** (pushed, PR-ready, review-complete). If this lane writes its row without absorbing `main`
> after that merge, the absorb conflicts on the ledger — and resolving it carelessly drops SCC-269's
> row, which is precisely the index-loss class this ticket exists to fix. Order: 269 merges →
> `git fetch origin && git merge origin/main` here → *then* append this lane's row.

## 7. What could make this the wrong fix

- **B1** — if any caller *depends* on exit 2 from a placeholder replacement (nothing found; the only
  callers are command bodies that treat non-zero as a stop).
- **B2** — if a real workflow needs two records under one id. Searched: every mention forbids it, and
  `check` flags it. If one is found during implementation, B2 becomes a **warning** rather than a
  refusal and the plan is amended and re-stopped.

---

## Self-Audit (2026-08-22)

**Level: LEDGER+BLAST** — the Declared Change Set touches a script other surfaces import, and its
test. Mode: PRE-WORK. Subject: this plan, `chore/SCC-271-jira-feed-write-truth` @ `9d7863b`.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every path/line the plan names exists and reads as quoted (jira_feed.py:1045, :2744,
             :2792, :2822, :2836, :614, :634, :537, :2698; test_jira_feed.py:480, :589, :631-633)
             · declared_change_set.py parse on this plan
             · both-machine spelling (python3 on Mac, python on PC; stdlib only, no venv)
             · lane fit: no deployable path in the change set -> /smh-close-task-merge-tree is the
               right door
             · Scope Ledger precondition: SCC-271 carries 7 acceptance rows, each naming a concrete
               observable (exit codes, absent output text, one-record counts, mutant kills)
             · Scope Ledger: the plan creates NO new source artefact - the two new test blocks land
               in an existing file - so the CREATES x acceptance table is empty and produces no
               finding by construction
read:        .agents/scripts/jira_feed.py · .agents/scripts/tests/test_jira_feed.py ·
             .agents/scripts/declared_change_set.py (CLI) · acli jira workitem view SCC-271
verdict:     findings below (1 of 3)
```

```
lens:        2 Parity + Blast
checks_run:  a script -> hook callers: `grep -rln 'jira_feed' .githooks/` EMPTY; .githooks/post-commit
               delegates only to .agents/scripts/git-hooks/post-commit-jira-start.sh, which uses the
               `start` verb - neither changed function is reachable from a hook. CLEAN
             · a script -> its test: test_jira_feed.py exists, is in the change set. CLEAN
             · a script -> scripts/INDEX.md:47 describes devrecord's one-record behaviour. Prose stays
               true after B2 (it becomes enforced rather than merely stated). Observation, not finding
             · the SOP / usage surface -> sop_currency.py:71-82. FINDING 1
             · a file existing in >1 repo -> `find Projects -name jira_feed.py` EMPTY (thin projects
               carry rules+skills only, no scripts). The port rule is NOT engaged. CLEAN
             · twins -> jira_feed.py is a single script, not a cicd/smh pair. Its seven command-body
               callers all say "never --append-new" - consistent, nothing to port. CLEAN
             · command file / command name / rule / gate-arming / path move / _artifacts/_memory ->
               none in the change set. CLEAN, one line each
             · sibling worktrees, after `git fetch origin main`: SCC-269 (cf90e73) and SCC-270
               (9d7863b, empty set). FINDING 3
             · risk_seam.py classify -> {"status":"unclassified"} (placeholder; informs, never gates)
read:        .githooks/{post-commit,commit-msg,pre-commit,pre-push} · .agents/scripts/sop_currency.py ·
             .agents/scripts/INDEX.md · docs/_scc_sops_prds/workflows_testing_SOP.md:2200-2208 ·
             git worktree list + per-tree `diff --name-only origin/main...HEAD`
verdict:     findings below (2 of 3)
```

```
lens:        3 Pre-Mortem  (bounded: attaches narratives to anchored findings, originates none)
checks_run:  the silent one · the other-machine one · the fresh-clone one · the sibling-lands-first one
read:        findings 1-3 above
verdict:     narratives attached to findings 1 and 3; nothing unattached (nothing discarded)
```

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/scripts/sop_currency.py:77` | `(".agents/scripts/", (".py", ".ps1"), "the safety-net scripts")` — with `_EXEMPT_PREFIXES = (".agents/scripts/tests/",)` at `:82` | Editing `jira_feed.py` trips the **armed** commit-msg gate. §5 said "No command or SOP edit is expected", so the build would have reached its **first commit** and been rejected. *Pre-mortem — the silent one:* the tempting recovery is `[sop-ok]`, which is a **logged** opt-out; using it for a change that really does alter operator-facing behaviour is how a gate gets hollowed out one honest-looking commit at a time. | **HIGH** |
| the plan file itself — `declared_change_set.py parse` | `{"present": false, "entries": [], "incomplete": []}` | No `## Declared Change Set` block. `/smh-code-review`'s drift check compares the declared set against the real diff; with nothing declared it has nothing to compare and the review's own scope check **passes vacuously** — the failure mode is a green that means nothing. | **HIGH** |
| `git -C .claude/worktrees/SCC-269-workspace-standard-reconcile diff --name-only origin/main...HEAD` | `_artifacts/_main/INDEX.md` (also `docs/workspace-standard.md`, `router.md`, that lane's session files) | Both lanes append to the same ledger. *Pre-mortem — sibling-lands-first:* SCC-269 merges first; this lane absorbs `main`, hits a conflict on `_main/INDEX.md`, and a careless resolution drops SCC-269's row — **the exact index-loss class this ticket was opened to fix**. | **MED** |

All three are **baked into the plan inline** (`⚠️ AUDIT FINDING 1` in §5, the new
`## Declared Change Set` block, `⚠️ AUDIT FINDING 3` in §6).

### Observations (uncounted, no severity)

1. `.agents/scripts/INDEX.md:47` — *"`devrecord` keeps **exactly one** Dev Record per ticket by
   finding the existing one and updating it in place"*. Still true after B2, and one clause would
   make it complete (it now also refuses the bypass). Added to the change set as optional; drop it
   if it reads as padding.
2. `.claude/worktrees/SCC-270-code-review-graph-swap` exists at `origin/main` with an **empty**
   change set — no overlap today. If it begins touching `.agents/scripts/`, Lens 2 needs re-running
   (it is the lens that expires).
3. The `--append-new` inversion means this lane **rewrites an existing green assertion**
   (`test_jira_feed.py:631-633`). The plan already flags it and pins it with a mutant; noted here so
   the reviewer sees it was deliberate and not a convenience edit.

```
Audit verdict: GO
```

**Not NO-GO:** neither NO-GO ground is met — no finding breaks an acceptance row, and none collides
with the constitution, git policy or the port rule (the port rule is not engaged: no second copy of
this script exists). Finding 1 is a hard-gate *collision* that is fully resolved by a plan amendment,
which is what the audit is for, and it is now amended.

## Approval

⛔ **Not approved yet.** The gate opens on the operator typing `approved`, unprompted. No file
outside `_artifacts/` is edited before then.
