# SCC-318 — Bugs and Updates, cycle 9 (consolidated lane)

**Lane:** `chore/SCC-318-bugs-cycle-9` · **Riders:** SCC-335, SCC-359, SCC-364
**Mode:** consolidated (`work-consolidation.md` rule 2) — one tree, one plan, one gate at the tip,
one close-out under SCC-318 with the three riders flipping first.

## Why these three, together

They are the whole remaining body of cycle 9. Part A (SCC-334) shipped separately under SCC-333 and
its key was later deleted from the board. The three left share no source file with each other, so
they are safe in one tree; two of them (SCC-359, SCC-364) both land cases in
`test_command_surfaces.py`, which is the only sequencing constraint in the set.

**Build order — measured, not preferred:**

1. **SCC-335** first. It is the only one that can still destroy operator data, and its files
   (`.agents/scripts/*.py`) are disjoint from the other two.
2. **SCC-364** second. Doc + one test block.
3. **SCC-359** third. Doc + one test block, appended after SCC-364's so the two edits to
   `test_command_surfaces.py` never collide.

---

## Part B — SCC-335 · `jira_feed.py` corrupts non-ASCII on Windows

### The defect, restated from the code

Every `acli` call in `jira_feed.py` funnels through **one** seam,
`.agents/scripts/jira_feed.py:126-129`:

```python
return subprocess.run([binary, *args], capture_output=True, text=True,
                      errors="replace", timeout=timeout)
```

`text=True` with no `encoding=` decodes with `locale.getencoding()`. On the Mac that is UTF-8 and
the code is correct; on the PC that is **cp1252**, and `acli` (a Go binary) always writes UTF-8. So
every description read on Windows is mojibake, and because `edit --description` replaces the whole
field, the mojibake is what gets written back. That is how SCC-318's own description was corrupted
on 2026-08-27.

`errors="replace"` does not save it — it is what turned `⭐` (UTF-8 `E2 AD 90`) into `U+FFFD`,
because cp1252 has no mapping for `0x90`. That half is **lossy** and unrecoverable from the written
text.

### Steps, each with the assertion that proves it

| # | Step | Assertion (RED first) |
|---|---|---|
| B1 | Pin `encoding="utf-8"` on the `acli()` seam in `jira_feed.py`. One line — every verb (`start`, `finish`, `devrecord`, `comment`, `index-row`, `check`) rides it. | A test spawns a **stub `acli`** that emits `⛔` and `⭐` as UTF-8 bytes on a cp1252-locale child, and asserts `field_text` returns both codepoints unchanged. RED today. |
| B2 | Same pin on `label_tasks.py:147-148` (identical seam, same defect). | The same round-trip case, parameterised over both modules. |
| B3 | Same pin on `jira_ticket.py`'s four `subprocess.run` sites (`:226`, `:245`, `:253`, `:311`) — acceptance D's sibling audit, and `task_preflight.py` checked and reported either way. | A case that greps every `subprocess.run(...)` in `.agents/scripts/*.py` reaching `acli` and fails on any that sets `text=True` without `encoding=`. This is the guard that stops the defect coming back. |
| B4 | Read-back guard names **which characters changed**, not only that lines went missing (acceptance C). Today `cmd_index_row`'s `lost` list reports a mangled line as a *deleted* line, and the natural next move — re-run, or hand-edit from the mangled copy — makes the corruption permanent. | A case feeds a read-back whose lines came back mojibake and asserts the message contains the phrase distinguishing **changed characters** from **deleted lines**, and names at least one differing codepoint. |
| B5 | Byte-identity: reading a description and writing it back with no row added leaves the field unchanged (acceptance A). | A case round-trips a description containing both codepoints through `field_text` → `index_append(before, row)` and asserts every pre-existing line is byte-identical. |

⛔ **What B1 must NOT become.** `_harness.py:245-265` (SCC-321) records the trap: pinning the parent
to UTF-8 while the child writes cp1252 mis-decodes in the *opposite* direction. That risk is real for
Python children and is why `run_script` also passes `PYTHONIOENCODING`. It does **not** apply here:
`acli` is a Go binary and Go's runtime always emits UTF-8, so pinning the parent alone is the whole
fix. This paragraph goes in the code comment, because the next reader will otherwise "fix" it back.

### Verification that needs the PC

B1–B5 all run green on the Mac against a locale-forced fixture, which is the honest way to test a
Windows bug from darwin. **One live confirmation still has to happen on the PC**: run
`jira_feed.py index-row --key SCC-373 --line "..." --apply` against the real board and read the
description back with `⛔`/`⭐` intact. That is a `## Your Actions` row, not a blocker for this lane.

---

## SCC-364 · close-out Step 4 rewrites a tree it is about to prune

### The defect, restated from the code

`.agents/commands/smh-close-task-merge-tree.md:581-598` runs, **after the merge**:

```bash
python3 .agents/scripts/jira_ticket.py done --key <KEY> --outline <path> --tick 1,2,3,4 ...
```

and its prose claims *"the tree stays the source, so the board and the branch cannot disagree"*.
`cmd_done` (`jira_ticket.py:427-465`) does two things: it **rewrites the outline file** and then
writes the board. At Step 4 the file write is unreachable — the lane is merged, the door's own
SCC-175 rule bans post-merge commits, and Step 5 prunes the tree. So `main` keeps the unticked
outline forever while the prose says the opposite.

### The fix, and why this one

The ticket offers two remedies. Take the second — **move the outline tick pre-PR** — because it is
the one that keeps the invariant the prose is claiming, and it needs **no new code**: the split
already exists in the script.

- **Step 3 (pre-PR, on the branch, committed with the rest of the lane):**
  `jira_ticket.py done --local` — ticks the Plan boxes, appends the Done lines, rewrites the
  `Files` link to `blob/main/`. `--local` already means "rewrote the file, the board was not
  touched" (`jira_ticket.py:462-464`). The edit lands on `main` through the PR like every other
  write in this lane.
- **Step 4 (post-merge, board only):** `jira_ticket.py describe --key <KEY> --outline <path>` —
  `cmd_describe` (`:420-424`) renders the already-ticked outline to the description and touches no
  file.

| # | Step | Assertion (RED first) |
|---|---|---|
| C1 | Re-sequence Step 3 / Step 4 in `smh-close-task-merge-tree.md`; correct the "tree stays the source" paragraph to say where the tick actually happens. | A `test_command_surfaces.py` case asserting the close-out door's **fenced code** calls `done --local` *before* its PR step and `describe` *after* the merge — position-aware, per `source-grep-guards-cannot-see-order`. |
| C2 | Keep CS-16 D/E green (`jira_ticket.py done` + `--tick` + `blob/main/` must still appear in the door). | Existing CS-16 block re-run; it passes because the call moved rather than left. |
| C3 | Mutation control: deleting the `--local` flag from the door's Step 3 fence must turn C1 RED. | Run the mutant, capture the red, revert. |

---

## SCC-359 · the approval-sha check can never pass

### The defect, restated from the two doors

`smh-quick-dev.md:211-214` — condition 3 of the approval gate:

> `git log -1 --format=%h -- <the plan>` **must equal that sha**

`smh-plan-task.md:274-277` — the writer's convention: the approval line carries *the sha of the
commit that recorded it*, which is not knowable until that commit exists. So the planner writes
`<pending>`, commits, then stamps the real sha in a **second** commit. The plan's last-touch sha is
therefore always the stamp commit, never the recorded one. Measured twice — SCC-347 (recorded
`acb02585`, stamped `cf198990`) and SCC-358 (recorded `4fdedf2f`, stamped `13ffe716`) — and in both
the entire delta between the two shas is one line, `<pending>` → the sha.

The condition's **intent** (no substantive edit after approval) holds; its **literal check** fails,
and an agent reading Step 1.5 literally stops a lane the operator already approved.

### The fix, and why this one

The ticket offers two remedies. Take the first — **Step 1.5 accepts a stamp-only successor commit**
— because the second is circular: any scheme that records a sha *into the plan file* changes the
plan file, so "last touch equals recorded" can never hold no matter which sha is chosen.

New condition 3, machine-checkable:

```bash
LAST=$(git log -1 --format=%h -- <the plan>)
# passes outright, or the delta since the recorded sha touches ONLY the approval line:
[ "$LAST" = "<recorded>" ] || git diff <recorded>..$LAST -- <the plan>   # must be the `— recorded at` line and nothing else
```

**No sha on the line still means the gate re-arms and you stop** — a missing operand is never a
pass, and that half of the condition is untouched.

**Twin check, answered:** `/cicd-quick-dev` carries **no** approval-sha box — grepped for
`recorded at`, `git log -1 --format=%h` and "unchanged since" across `.agents/commands/`, and the
contract appears in exactly three files: `000-PLAN-FIRST-GATE.md:83`, `smh-quick-dev.md:212`,
`smh-plan-task.md:275`. There is no twin to port to; that finding goes in the walkthrough so the
next reader does not re-run the search.

| # | Step | Assertion (RED first) |
|---|---|---|
| D1 | Rewrite `smh-quick-dev.md` Step 1.5 condition 3 to the stamp-tolerant form above. | See D3. |
| D2 | Add the matching note to `smh-plan-task.md` Step 5 — the stamp commit is expected, and it may change **only** the approval line. | See D3. |
| D3 | A `test_command_surfaces.py` case pinning that the **writer and the reader agree**: the door that mandates the two-commit stamp and the door that checks it must both name the stamp-only exemption. | RED today — `smh-quick-dev.md` says "must equal" with no exemption, so the case fails on the reader side before the edit. |
| D4 | Update `000-PLAN-FIRST-GATE.md:83`, which summarises the same comparison, so law and door do not drift. | The same case reads all three files, not two. |

---

## Declared Change Set

⚠️ **AUDIT FINDING F1 (fixed here).** This block was first written as a Markdown table and
`declared_change_set.py parse` returned `"entries": []` against it — `present: true`, nothing read.
The parser takes **bullets** (`declared_change_set.py:56`, the `ATTEMPT` regex), so a table is
invisible exactly the way `## Your Actions` is invisible to `reconcile-actions` when written as one.
Rewritten as bullets and re-parsed.

- EDIT `.agents/scripts/jira_feed.py` — pin the acli seam to UTF-8; teach the read-back guard to name changed characters → B1, B4
- EDIT `.agents/scripts/label_tasks.py` — same seam, same pin → B2
- EDIT `.agents/scripts/jira_ticket.py` — four subprocess sites pinned → B3
- EDIT `.agents/scripts/tests/test_jira_feed.py` — the round-trip, guard-message and byte-identity cases → B1, B2, B4, B5
- NEW `.agents/scripts/tests/fixtures/acli_utf8_stub.py` — stub acli emitting U+26D4 and U+2B50 as UTF-8 bytes → B1, B2
- EDIT `.agents/scripts/tests/test_command_surfaces.py` — the no-unpinned-seam guard, the close-out order case, the writer/reader agreement case → B3, C1, D3, D4
- EDIT `.agents/commands/smh-close-task-merge-tree.md` — tick pre-PR, board-only render post-merge → C1
- EDIT `.agents/commands/smh-quick-dev.md` — Step 1.5 condition 3 accepts a stamp-only successor → D1
- EDIT `.agents/commands/smh-plan-task.md` — Step 5 states what the stamp commit may contain → D2
- EDIT `.agents/rules/000-PLAN-FIRST-GATE.md` — the law's summary of the same comparison → D4
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — C1 moves a usage surface, so the armed `sop_currency.py` gate requires this in the same commit → C1
- NEW `_artifacts/_main/2026-09-01_SCC-318-bugs-cycle-9/walkthrough.md` — the lane record → the record

`.agents/scripts/task_preflight.py` needs **no edit** — checked: it holds no `subprocess.run` of
its own and reaches the board through `jira_feed.acli_json` (`:760`), by deliberate design
(`:60-62`, "ONE acli resolution path in this repo, not two"). B1 fixes it for free. B3's grep guard
covers it anyway, so a future local seam there cannot reintroduce the defect unnoticed.

## Gate

ONCE, at the tip, through `gate_receipt.py`: the enforcement suite + `workflow_lint` +
`sop_currency` + `py_compile` + link/anchor. Per part, that part's own test file with its RED→GREEN
capture. `work-consolidation.md` rule 3 — one block, read together.

## Out of scope, said out loud

- The SOP page (`docs/_scc_sops_prds/workflows_testing_SOP.md`) changes only if a **usage surface**
  moves. C1 moves one, so the SOP edit is in scope for that part and the `sop_currency` gate will
  say so; nothing else here changes how a command is typed.
- SCC-373's INDEX stays empty. Findings this lane discovers go to SCC-373 as new subtasks, not into
  SCC-318, which is now the running cycle.

## Approval

Audit verdict: GO
Approved: (awaiting the operator) — recorded at <pending>

---

## Self-Audit (2026-09-01)

**Level: LEDGER+BLAST** — the plan touches a rule, a script two hooks call, three command doors,
a test surface and the SOP. Mode: PRE-WORK.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every path/script/rule/door the plan names exists on disk (13/13 OK)
             `declared_change_set.py parse` against the plan block
             both-machine spelling: plan is written python3, PC drops the 3 (INDEX.md:67)
             lane fit: no deployable path (backend/ frontend/ firebase/ functions/ mobile/ .github/) in the set
             Scope Ledger: NEW rows x the acceptance row requiring each
             Scope Ledger precondition: each rider carries >=2 acceptance rows with concrete observables
read:        .agents/scripts/{jira_feed,label_tasks,jira_ticket,task_preflight,declared_change_set}.py
             .agents/scripts/tests/{test_jira_feed,test_command_surfaces,_harness}.py
             .agents/commands/{smh-close-task-merge-tree,smh-quick-dev,smh-plan-task,cicd-quick-dev}.md
             .agents/rules/{000-PLAN-FIRST-GATE,work-consolidation}.md
             acli jira workitem view SCC-335 / SCC-359 / SCC-364
verdict:     findings below (F1, F2 — both fixed in this pass)
```

```
lens:        2 Parity + Blast
checks_run:  command-file rows: three doors edited by BODY, no rename -> four platform launchers
               are thin (SCC-370) and carry no body text, so no door edit follows
             twin check: PAIRS has (cicd-quick-dev.md, smh-quick-dev.md); the only twin-law marker
               in smh-quick-dev.md is review-runtime-probe at :74-83, and Step 1.5 is at :178 —
               outside it, so D1 engages no parity law
             NOT_PAIRED registry carries smh-close-task-merge-tree.md (:161) and smh-plan-task.md
               (:164) — no twin obligation for C1 or D2
             rule row: `_RULE_POINTERS` (workflow_lint.py:70-100) has rows for git-policy,
               worktree-per-story, smh-target-resolution, work-consolidation, port-checklist,
               code-standards — and NONE for 000-PLAN-FIRST-GATE, so D4 triggers no pointer work
             script row: .githooks/post-commit -> .agents/scripts/git-hooks/post-commit-jira-start.sh:119
               calls `jira_feed.py start --apply` on every keyed commit
             gate row: no gate or hook ships changed ARMED state
             SOP row: C1 moves a usage surface -> SOP staged in the same commit (declared)
             >1 repo row: none of these files exists outside this repo
             sibling worktrees: `env -u GITHUB_TOKEN git fetch origin main`, then git worktree list
               and per-tree diff/status
             risk_seam.py classify -> {"status":"unclassified","root":".../scc318-bugs-cycle-9"}
read:        .agents/scripts/tests/test_twin_parity.py, workflow_lint.py, .githooks/post-commit,
             .agents/scripts/git-hooks/post-commit-jira-start.sh, .agents/scripts/INDEX.md
verdict:     findings below (F3)
```

```
lens:        3 Pre-Mortem
checks_run:  attached failure narratives to F1, F2 and F3 only; originated nothing
read:        (the anchored findings above)
verdict:     clean — no unattached output
```

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| the plan file, `## Declared Change Set` (as first written) — `declared_change_set.py parse` returned `{"present": true, "entries": [], "incomplete": []}` | a Markdown table, `\| Kind \| Path \| → acceptance row \|` | **F1.** The block existed and read as empty. `/smh-code-review`'s drift check (SCC-231) reconciles the diff against `entries`, so all 12 files would have surfaced as *undeclared drift* and the review would stall on phantom findings — or waive the whole set. Same shape as `your-actions-must-be-checkbox-rows`: a table is invisible to the machine reader. **Pre-mortem (the silent one):** parse exits 0 either way, so nothing announces it until review. **FIXED in this pass** — rewritten as bullets, re-parsed: 12 entries, 0 incomplete. | high |
| `acli jira workitem view SCC-364` — description is `Why: … Remedy: … Anchor: …` with no `## Plan` block | no acceptance rows at all | **F2.** The Scope Ledger precondition (≥2 acceptance rows, each naming a concrete observable) failed for one of the three riders, which is a stated NO-GO ground. **Pre-mortem (the close-out one):** `task_preflight.py` verifies a rider against the lane's commits, but nothing can verify a rider whose acceptance is prose — close-out would flip SCC-364 Done on faith. **FIXED in this pass** — outline written to `tickets/SCC-364.md`, 7 checkable rows, pushed with `jira_ticket.py describe` and read back. | high |
| `.claude/worktrees/scc372-sync-vscode`, `git status --short` | ` M docs/_scc_sops_prds/workflows_testing_SOP.md` *(and `.agents/commands/INDEX.md`, `.agents/scripts/tests/test_twin_parity.py`)* | **F3.** SCC-372's live lane holds **uncommitted** edits to the same SOP file C1 must stage. Not a file conflict yet — it is uncommitted, so `origin/main` does not show it. **Pre-mortem (the sibling-lands-first one):** whichever lane merges second, built on plan-time `main`, silently drops the other's SOP rows. **Not fixed here — it is SCC-372's work, not this lane's.** Landing order below. | medium |

### Landing-order dependency

`docs/_scc_sops_prds/workflows_testing_SOP.md` is in both this lane's declared set and SCC-372's
working tree. **This lane lands FIRST** — it is the smaller SOP edit (one step-order paragraph) and
SCC-372 is still In Progress with its command not yet committed. If SCC-372 lands first instead,
this lane must `git fetch origin && git merge origin/main` before staging the SOP, and diff that
file specifically. Either way the second lane re-absorbs; neither may edit the SOP from a stale base.

### Observations (uncounted — judgment, no check behind them)

- `jira_feed.py` sits on the **post-commit path** (`post-commit-jira-start.sh:119`), so B1 ships to
  every keyed commit on both machines. B1 adds a keyword argument inside `acli()` and changes no
  signature, so no hook caller breaks — but it means the PC gets the fix the moment this lands,
  which is the fastest route to the live confirmation SCC-335 wants.
- `cicd-quick-dev.md` carries **no** approval-sha box — zero hits for `recorded at`,
  `git log -1 --format=%h` and "unchanged since". This corroborates the plan's twin-check answer
  from the other direction, and is why D1/D2 port to nothing.
- `risk_seam.py` returns `unclassified` and names the lane tree as `root`. Correct and permanent for
  the command centre (SCC-289) — the tiers mean nothing here and every Lens 2 judgment above came
  from the diff, not the classifier.

```
Audit verdict: GO
```
