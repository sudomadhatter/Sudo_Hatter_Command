---
IsArtifact: true
ArtifactMetadata:
  title: SCC-281 — Bugs and Updates, cycle 6 (one consolidated lane)
  type: implementation_plan
  date: 2026-08-22
---

# SCC-281 — Bugs and Updates, cycle 6 (one consolidated lane)

**Ticket:** SCC-281 (Task, `In Progress` since 2026-08-22) · **Branch:** `chore/SCC-281-bugs-cycle-6`
**Worktree:** `.claude/worktrees/scc-281-bugs-cycle-6` · **Base:** `origin/main` @ `a634c35`
**Riders:** SCC-282 (A) · SCC-283 (B) · SCC-284 (C) — all three carried forward verbatim from SCC-262
(SCC-264/265/266), found at SCC-244's close-out on 2026-08-22.
**Successor minted:** SCC-293 (cycle 7) — cloned by `jira_feed.py start`, retitled, INDEX emptied,
PREDECESSOR names SCC-281. It holds `running-bug-list`; SCC-281 holds `bugs-and-updates`. Read back
live: exactly two rows, one label each.

**Consolidation decision (work-consolidation.md rule 2, stated as the rule requires):** one lane, one
branch, one close. Same repo, same lane class (`.agents/scripts/*.py` + their tests + two command/rule
bodies), no parallelism worth a second tree, and the operator's instruction is verbatim *"one shot the
ticket on one working tree"*. Each part's commits name its SUBTASK key in the subject so each child's
Jira dev panel shows its own commits. No `landing_mode:` line — this landing closes the parent.

**review-runtime: fan-out** (the Agent tool exists in this runtime; probed at Step 0).

---

## Recon — every anchor re-verified against `origin/main@a634c35`, not the carried-forward text

| Part | Ticket's anchor (as of 2026-08-22) | Re-derived today | Verdict |
|---|---|---|---|
| A | `task_preflight.py:336` `re.match(r"\s*([A-Z][A-Z0-9]+-\d+)\b", …)` | `:336`, unchanged; `lane_commit_keys()` at `:319`; the consumer at `:725-731` | REAL |
| A | live proof `d9d9a9d` | `git log -1 --format=%s d9d9a9d` → `SCC-244 rider SCC-253: scripts/INDEX.md names a lever …` — SCC-253 is the second key | REAL |
| B | `task_preflight.py:955-995` three-way split, "everything else" errors | `_check_tree_dirt()` at `:951-997`: `mem` / `mine` / `rest`; `rest` → `rep.err("sync", … uncommitted change(s) …)` at `:973` | REAL |
| C | `mutation_sweep.py:137` `if not m.get(k)` | `:137`, unchanged; `original == mutated` refusal at `:140`; apply at `:252` is `before.replace(original, mutated, 1)` — an empty `mutated` already *works* as a deletion once the loader lets it through | REAL |
| C | SCC-244 `sweep.json` M16/M23/M26 are inert substitutes | `_artifacts/_main/2026-08-21_scc-244-bugs-updates-cycle-4/sweep.json`: M16 → `status -sb`, M23 → `pass`, M26 → `cat "<path>"` | REAL |

**One convention conflict the ticket did not name, resolved here:** `work-consolidation.md` rule 2's
table says rider commits carry *"the SUBTASK's key per commit"*; `git-policy.md:307` says *"lead the
subject with the repo's Jira key"*; SCC-244 in practice wrote `SCC-244 rider SCC-253: …` (parent first).
All three are legitimate, and the reader must accept all three. The fix is in the reader (every key in
the subject counts), and the convention text gains one sentence saying so — it does not pick a winner.

## Sibling lanes read at Step 0.5 (landing-order dependencies)

| Lane | Overlap with this lane's Declared Change Set | Consequence |
|---|---|---|
| `chore/SCC-285-agenttool-directive-quote` | `.agents/.sync-manifest.json` (if `/smh-sync-agents` is run here) | mechanical; whichever lands second re-syncs. No source overlap |
| `claude/teaching-edition` (SCC-280, dirty tree) | `.agents/.sync-manifest.json` only | same |
| `chore/SCC-287-readonly-chain-allow` · `chore/SCC-288-graph-to-projects` | none | — |

No sibling touches `task_preflight.py`, `mutation_sweep.py`, their tests, `smh-close-task-merge-tree.md`
or `work-consolidation.md`. **Build order is C → A → B** (smallest and independent first; B is the
only part that adds a new mechanism).

---

## Acceptance list (from the three tickets' ACCEPTANCE blocks, verbatim in substance, each checkable)

**Part C — SCC-284 (`mutation_sweep.py`)**
- C1 A mutant declaring `"mutated": ""` loads, applies as a deletion, and is scored like any other.
- C2 A mutant with the `mutated` key genuinely ABSENT still refuses, with a message that distinguishes absent from empty.
- C3 `"original": ""` still refuses (a mutant that inserts from nowhere has no unique anchor).
- C4 SCC-244's M16, M23, M26 become real deletions (`"mutated": ""`) and that sweep still comes back 27/27.
- C5 Enforcement suite green.

**Part A — SCC-282 (`task_preflight.py` rider evidence)**
- A1 `lane_commit_keys()` finds a key named ANYWHERE in the subject; the verbatim subject of `d9d9a9d` is a regression fixture proving SCC-253 is found in it.
- A2 A mutant reverting to leading-key-only turns the new case red.
- A3 The partial-landing block in `smh-close-task-merge-tree.md` says how a rider earns its evidence, so the requirement is discoverable BEFORE the commits are written.
- A4 Enforcement suite green.

**Part B — SCC-283 (`task_preflight.py` dirt classifier)**
- B1 A dirty path whose content matches a live sibling worktree's committed copy is reported as that lane's working copy, naming the branch, and does not error (exit ≠ 2).
- B2 A dirty path matching NO live lane still errors exactly as today — positive control.
- B3 A dirty path on a live lane's branch whose content DIFFERS from the committed copy still errors.
- B4 (added by the self-audit) A dirty path in the LANE tree that matches `main`'s committed copy — an uncommitted revert — still errors; the base branch is never a "sibling lane".
- B5 Enforcement suite green.

---

## Steps

### Step 1 — Part C: RED, then the loader learns "absent" from "empty"
**RED** (`tests/test_mutation_sweep.py`, new block `K6 · a DELETION mutant is legal; an absent field is not`):
three cases on the existing throwaway-repo fixture — (C1) table with `"mutated": ""` over the
`PATTERN` line → sweep runs, reports `KILLED`, exit 0, source byte-identical after; (C2) table whose
mutant has no `mutated` key → exit 2 and the message names `mutated` as *absent*, not *empty*; (C3)
`"original": ""` → exit 2. Run with `--case "K6"`, paste the red (C1 today reads `is missing mutated`).
**GREEN** (`mutation_sweep.py:137-141`): split the one falsy test into (i) `absent = [k for k in FIELDS
if k not in m]` → `… is missing <k> (absent)`, (ii) `empty = [k for k in ("id","file","original","case")
if not m.get(k)]` → `… has an EMPTY <k>`; `mutated` is allowed to be `""` and the docstring/template at
`:24-25` says *`"" = delete the anchor`*. Keep `original == mutated` at `:140` (catches `""`/`""`).
**C4**: edit SCC-244's `sweep.json` M16/M23/M26 to `"mutated": ""`, verify each anchor still occurs
exactly once on this tree, run that sweep through `mutation_sweep.py`, paste `27/27`. If a deletion
would leave an empty Python block (M23 is an `if` body inside a loop — check the enclosing block), that
is a kill-by-SyntaxError and the table must instead say so; record the finding rather than fake it.

### Step 2 — Part A: RED, then every key in the subject counts
**RED** (`tests/test_task_preflight.py`, existing block `SCC-170 partial landing …`, two new cases):
(A1a) riders committed as `SCC-11 rider SCC-21: …` / `SCC-11 rider SCC-22: …` (parent key LEADS) with
`landing_mode: partial` → today exit 2 *"lead(s) no commit here"*; must become exit 1 + *"clear to close
out"*. (A1b) a pure-function case: `task_preflight.subject_keys("SCC-244 rider SCC-253: scripts/INDEX.md
names a lever that is worth two seconds [sop-ok]") == {"SCC-244","SCC-253"}` — the verbatim `d9d9a9d`
subject as a fixture; plus, when `git cat-file -e d9d9a9d` succeeds in the repo under test, the live
subject is read and asserted equal to the fixture (skipped with a printed note on a shallow clone).
**GREEN**: factor `subject_keys(line) -> frozenset[str]` (`re.findall(r"\b([A-Z][A-Z0-9]+-\d+)\b", …)`)
and have `lane_commit_keys()` union it per subject. Docstring line 1 changes from *"leads a commit
subject"* to *"is named in a commit subject"*. Error text at `:728` changes *"lead(s) no commit here"* →
*"is named in no commit subject here"* (the existing case asserts `"work is not real"`, untouched).
**A3**: `smh-close-task-merge-tree.md` partial-landing step 1 gains: *"A rider earns its evidence by
being NAMED in at least one commit subject on the lane — `SCC-244 rider SCC-253: …` and `SCC-253 fix: …`
both count; the key need not lead."* `work-consolidation.md` rule 2 "Commits" row gains the same clause.
Regenerated mirrors (`.opencode/commands/`, `.agents/workflows/`) via `/smh-sync-agents`.

> ⚠️ **AUDIT FINDING (Lens 2, anchored):** the OLD semantics are pinned in prose in five places, not
> two — `work-consolidation.md:173` *"refuses a rider that leads no commit"*, `jira.md:356` *"refuses a
> declared rider that leads no commit on the lane"*, `smh-plan-task.md:164` *"refuses a rider that leads
> no commit there"*, `smh-close-task-merge-tree.md:492`, `workflows_testing_SOP.md:1639`. Fixing the
> reader and leaving three of them reading *"leads"* teaches the retired rule on every platform. **All
> five change to *"is named in no commit subject"*** (one-word edits; `smh-plan-task.md` is a command,
> so its mirrors regenerate with the others). ⚠ `jira.md` is DIRTY on the `claude/teaching-edition`
> tree (SCC-280) — a landing-order dependency on one line in a different section; whichever lands
> second absorbs a trivial merge. Recorded so it is not a surprise at close-out.

### Step 3 — Part B: RED, then the fourth bucket
**RED** (`tests/test_task_preflight_contract.py`, new block `SCC-283 · a live sibling lane's working
copy is not unswept dirt`): fixture = `make_repo` + `branch(repo, "chore/SCC-11-thing", …)`; a sibling
branch `chore/SCC-12-other` checked out in `git worktree add <t>/wt`, which commits `.claude/x.json`
(content X) with `--no-verify`; back in `repo`, write the same path with content X (untracked `??`).
(B1) `preflight(repo)` → exit ≠ 2, output names `chore/SCC-12-other` and the words *working copy*.
(B2) positive control: a second untracked file no lane has → exit 2, *uncommitted change(s)*. (B3) the
sibling path rewritten with content Y → exit 2. Today B1 reads exit 2 — paste it.
**GREEN** (`task_preflight.py` `_check_tree_dirt`): new helper `sibling_lane_copies(repo, tree, lines)
-> dict[path, branch]` — parse `git worktree list --porcelain` (reuse the `worktree_holding` idiom in
`wf_common.py:447`), skip the tree being measured, and for each `rest` line with status ` M`/`M `/`??`
compare the working-copy bytes to `git show <branch>:<path>` (`cat-file -e` first). Matching paths leave
`rest` and are reported `rep.warn("sync", "<label>: <path> is chore/SCC-12-other's working copy
(byte-identical to its committed copy) - leave it alone; it is not this lane's dirt")`. Everything else
is unchanged: `mem` first, `mine` by exact path, `rest` errors. Renames and deletions are never matched
(a deletion cannot equal a committed blob). Comment block names SCC-283, SCC-180 (the reset --hard that
ate three sessions) and SCC-246 (the authorship answer for `_artifacts/_memory/`).

> ⚠️ **AUDIT FINDING (Lens 2 + Lens 3 narrative, anchored):** `wf_common.py:465` `trees_to_measure()`
> applies `_check_tree_dirt` to *every* tree that could reach the landing — the shared checkout AND the
> lane's own worktree. Measured from the lane's worktree, the "siblings" list would contain the MAIN
> checkout on `main`. A file this lane changed and committed, then reverted by hand in the working copy
> to main's content, is dirty AND byte-identical to `main:<path>` — the helper as first written would
> call that *"main's working copy"* and wave an uncommitted revert through. That is permissive in
> exactly the direction SCC-180 punished. **Bake-in:** `sibling_lane_copies()` compares ONLY against
> worktrees whose branch is a LANE branch (`chore/` · `claude/` · `epic/`), never the base branch and
> never the branch being landed (a second tree on this lane's own branch is `check_worktree`'s
> warning, not a sibling). A fourth test case (B4) pins it: a dirty revert-to-main in the lane tree
> still errors.

### Step 4 — mutants, suite, SOP, artifacts (rule 3: one block)
- `sweep.json` for THIS lane, drawn from the code (⚠ the numbering below was the plan's; the FINAL table in `sweep.json` and the walkthrough is authoritative — it grew to 17 across two review rounds): M1 `findall`→`match` (kills A1a), M2 `subject_keys`
  returns only `group(1)` (kills A1b), M3 loader `k not in m` → `not m.get(k)` (kills C1), M4 absent-
  message loses the word *absent* (kills C2), M5 `sibling_lane_copies` compares to `b""` instead of the
  blob (kills B3), M6 the helper returns `{}` (kills B1), M7 the matched paths are NOT removed from
  `rest` (kills B1), M8 `original` dropped from the empty-check (kills C3). Run as one sweep.
- Suite once, on the committed tip, through `gate_receipt.py run --task SCC-281 --gate suite`.
- `docs/_scc_sops_prds/workflows_testing_SOP.md` staged in the SAME commit as each usage-surface
  change (deletion mutants; rider evidence wording; the new preflight warning class). No `[sop-ok]`.
- `walkthrough.md` with `## Your Actions`; `_artifacts/_main/INDEX.md` row; Dev Record via
  `jira_feed.py devrecord --key SCC-281 --stage quick-dev`. Then `/smh-code-review`, then STOP for the
  close-out.

---

## Declared Change Set

### Scripts and their tests
- EDIT `.agents/scripts/mutation_sweep.py` — loader distinguishes ABSENT from EMPTY; `"mutated": ""` is a legal deletion; template comment says so → C1, C2, C3
- EDIT `.agents/scripts/tests/test_mutation_sweep.py` — block K6: deletion legal, absent refused, empty original refused → C1, C2, C3
- EDIT `.agents/scripts/task_preflight.py` — `subject_keys()` + `lane_commit_keys()` read every key; `sibling_lane_copies()` + fourth bucket in `_check_tree_dirt()`; discovered in the build: the porcelain output is split BEFORE stripping (first-line ` M` parse bug, B5/B6); review round: base-blob predicate, own-lane owner, prunable skip, staged remedy, blob-id compare (B7–B15) → A1, B1, B2, B3
- EDIT `.agents/scripts/tests/test_task_preflight.py` — parent-key-leads riders pass; `d9d9a9d` verbatim subject fixture → A1, A2
- EDIT `.agents/scripts/tests/test_task_preflight_contract.py` — block SCC-283: sibling copy warns, unknown errors, differing errors → B1, B2, B3

### Command and rule bodies (usage surfaces — SOP staged with them)
- EDIT `.agents/commands/smh-close-task-merge-tree.md` — partial-landing step 1 says how a rider earns its evidence → A3
- EDIT `.agents/rules/work-consolidation.md` — rule 2 "Commits" row: the key need not lead; `:173` "leads" → "is named in" → A3
- EDIT `.agents/rules/jira.md` — `:356` one-word wording fix, "leads no commit" → "is named in no commit subject" → A3
- EDIT `.agents/commands/smh-plan-task.md` — `:164` same one-word wording fix → A3
- EDIT `.opencode/commands/smh-close-task-merge-tree.md` — regenerated mirror → A3
- EDIT `.opencode/commands/smh-plan-task.md` — regenerated mirror → A3
- EDIT `.agents/.sync-manifest.json` — regenerated by the sync → A3
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — deletion mutants, rider evidence, the sibling-copy warning → C1, A3, B1

### Evidence record

> Reconciled after the build: the `.agents/workflows/` Antigravity mirrors are thin launchers and did not change when the sync ran, so their two rows are removed rather than left as phantom EDITs.

- EDIT `_artifacts/_main/2026-08-21_scc-244-bugs-updates-cycle-4/sweep.json` — M16/M23/M26 become real deletions → C4
- NEW `_artifacts/_main/2026-08-22_scc-281-bugs-cycle-6/implementation_plan.md` — this plan → all
- NEW `_artifacts/_main/2026-08-22_scc-281-bugs-cycle-6/task.yaml` — manifest, `riders: [SCC-282, SCC-283, SCC-284]` → all
- NEW `_artifacts/_main/2026-08-22_scc-281-bugs-cycle-6/sweep.json` — this lane's mutant table → A2 and the rest
- NEW `_artifacts/_main/2026-08-22_scc-281-bugs-cycle-6/walkthrough.md` — evidence, review, Your Actions → all
- NEW `_artifacts/_main/2026-08-22_scc-281-bugs-cycle-6/gates/suite.json` — receipt → C5, A4, B5
- EDIT `_artifacts/_main/INDEX.md` — one row → all

## Out of scope, deliberately
- No change to which key *should* lead a rider's commit — three conventions coexist and the reader now accepts all three.
- No attempt to classify a sibling's UNCOMMITTED work (B3 says that still errors; the authorship answer for memory files stays SCC-246's).
- `.agents/workflows/` Antigravity mirrors only if the sync regenerates them; nothing hand-edited there.

---

## Self-Audit (2026-08-22)

**Level: LEDGER+BLAST** (the Declared Change Set touches two scripts other gates import, one rule, two
command bodies and four generated mirrors) · **Mode: PRE-WORK** · Repo `scc-281-bugs-cycle-6` worktree,
branch `chore/SCC-281-bugs-cycle-6` (from `git rev-parse`).

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every declared path exists on disk (15/15 `ok`, ls loop pasted in session)
             `declared_change_set.py parse <plan>` -> "incomplete": []  (re-run after the audit bake-ins)
             both-machine commands: python3 stdlib only (no venv, no bare `python`)
             lane fit: no deployable path in the set (scripts/tests/commands/rules/docs/artifacts only)
             Scope Ledger: 5 NEW artefacts x acceptance rows - every NEW bullet carries a row
             acceptance precondition: 13 rows across three tickets, each with a concrete observable
read:        .agents/scripts/task_preflight.py:319-339, :695-731, :951-997
             .agents/scripts/mutation_sweep.py:24-25, :118-146, :222-256
             .agents/scripts/wf_common.py:447-483
             .agents/scripts/tests/_pf_fixtures.py:53-260, test_task_preflight.py:745-850,
             test_task_preflight_contract.py:184-200, :485-530, test_mutation_sweep.py:1-110, :91-326
             .agents/scripts/tests/_harness.py:99-182
             _artifacts/_main/2026-08-21_scc-244-bugs-updates-cycle-4/sweep.json (M16/M23/M26; anchors count=1 each on this tree)
             .agents/scripts/jira_feed.py:298-311 (M23's deletion leaves a valid block - `current = [...]` follows)
verdict:     clean
```

```
lens:        2 Parity + Blast
checks_run:  command file -> doors: .agents/workflows/, .claude/skills/, .opencode/commands/ all present; commands/INDEX.md names it (4 refs)
             rule -> citers: 7 command bodies cite work-consolidation; workflow_lint.py:87-88 arm matches `riders:` / `landing_mode: partial` - added prose does not touch either token
             scripts -> .githooks/ callers: none (merge-target-guard.sh:163 is a comment); scripts/INDEX.md rows :21 and :26 stay true
             lane_commit_keys / _check_tree_dirt external callers: none outside task_preflight.py
             pinned message text: grep "lead(s) no commit|leads no commit" -> 5 prose sites + the code (finding 1)
             twin: cicd-close-story-merge-tree.md carries NO riders/partial block (grep -i partial|riders -> 0 rows) - story lanes have no riders by design (jira.md §Subtasks: the story lane's answer is NEVER); no port owed
             SOP: same-commit rule acknowledged in Step 4; tests/ is exempt, so RED-only commits need no SOP
             risk_seam.py classify -> "unclassified" (normal; no graph at this sha)
             sibling worktrees: fetched origin; 4 trees read (diff --name-only origin/main...HEAD + status --short) - overlap only on .agents/.sync-manifest.json (scc-285, SCC-280) and now jira.md (SCC-280 dirty tree)
read:        .agents/scripts/workflow_lint.py:82-88 · .agents/commands/cicd-close-story-merge-tree.md (grep) · .agents/scripts/INDEX.md:21,26
             .agents/rules/jira.md:356 · .agents/commands/smh-plan-task.md:164 · .agents/rules/work-consolidation.md:173 · docs/_scc_sops_prds/workflows_testing_SOP.md:1639
             .agents/scripts/wf_common.py:465-483 (trees_to_measure)
verdict:     findings below
```

```
lens:        3 Pre-Mortem (bounded - attaches only to anchored findings)
checks_run:  other-platform narrative attached to finding 1; permissive-direction narrative attached to finding 2
read:        the two anchors above
verdict:     findings below (attached, none originated)
```

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/scripts/wf_common.py:465` | `def trees_to_measure(repo: Path, branch: str, …)` — "Always the repo the caller named; plus the tree that actually holds `branch`" | Step 3's helper, measured from the lane tree, would see the MAIN checkout as a sibling and wave through an uncommitted revert-to-main — permissive in the SCC-180 direction. **Baked in:** compare only against `chore/`·`claude/`·`epic/` worktrees, never the base branch or this branch; new case B4 | medium |
| `.agents/rules/jira.md:356` (+ `smh-plan-task.md:164`, `work-consolidation.md:173`) | "`task_preflight.py` refuses a declared rider that leads no commit on the lane" | the reader's semantics change and three prose sites keep teaching "leads" — on Codex/Antigravity, which read the rule and command text, the retired rule survives. **Baked in:** all five sites re-worded; `jira.md` overlap with SCC-280 recorded as a landing-order note | low |

### Observations (uncounted)
- `sibling_lane_copies()` runs one `git cat-file -e` + one `git show` per dirty path per lane worktree. Four lanes × a handful of dirty paths is negligible; a 40-file dirty tree on the PC would add a few seconds. Bounded by `rest` (already an error state), so no design change.
- The RED commits are tests-only and exempt from the SOP gate; every GREEN commit that touches a script, command or rule must stage `workflows_testing_SOP.md` or the armed `commit-msg` refuses it. The lane expects that refusal on any slip and treats it as the gate working.
- `.claude/settings.json` (the ticket's sharp case) is tracked and was last committed under SCC-277; the B1 fixture uses a neutral `.claude/x.json` so the test does not depend on that file's history.

**Sibling landing-order dependencies:** `.agents/.sync-manifest.json` (scc-285, SCC-280 — mechanical, whichever lands second re-syncs) · `.agents/rules/jira.md:356` vs SCC-280's dirty `jira.md` (one line, different section — trivial absorb either way).

Audit verdict: GO
