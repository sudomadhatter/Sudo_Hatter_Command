---
IsArtifact: true
ArtifactMetadata:
  title: Close-out RECONCILES the operator's task list before it asks finish to close
  type: implementation_plan
  date: 2026-08-23
  ticket: SCC-298
  parent: SCC-293
  lane: chore/SCC-298-reconcile-actions
---

# SCC-298 — the close-out verifies the task list instead of reading it

**The defect, in one sentence.** `jira_feed.py finish` decides `Done` from what the walkthrough's
`## Your Actions` section *claims*, and nothing in this system has ever checked whether a row's
claim is still true — so a ticket sits at `Review Required` over work that was finished days ago.

**Measured, not hypothetical.** SCC-288 was held for a day by one row, `C0`. The token existed,
authenticated, and the plan was already attached to the ticket. The row was open because an agent
did not tick it, and `finish` has no way to tell "not done" from "not ticked".

> **Operator, 2026-08-23:** *"agents are terrible at checking off those task lists, especially when
> its a user task, even if I tell them."* And the ruling on how a row gets ticked: **evidence where
> a check exists; where none does, ask the operator and tick on their word — recorded either way.**

**The precedent this generalises is already in the file.** SCC-175 stopped reading the *merge* row
off a tick and started **computing** it from the repo, for exactly this reason: *"a tick is a CLAIM,
and `finish --apply` is what writes `Done` to Jira on the strength of it."* That fix covered one row.
This lane gives every other row the same treatment — the difference being that most rows have no
`git merge-base` to ask, so the check is derived per row and the answer is recorded beside it.

---

## Acceptance — every item checkable by a command

| # | Acceptance | The assertion that proves it |
|---|---|---|
| **A1** | `reconcile-actions --walkthrough <f>` lists every open `- [ ]` row under `## Your Actions` with its 1-based line number, and exits **3** while any remain / **0** when none do. No board, no network. | `test_jira_feed.py` case: fixture with 2 open rows → exit 3 and both line numbers on stdout; tick both → exit 0 |
| **A2** | `--tick <line> --evidence "<text>" --source measured\|operator` flips **that one row** to `- [x]`, writes the proof inline, and leaves every other byte of the file unchanged. | case: assert the post-tick file differs from the pre-tick file on **exactly one line**, that line reads `- [x] … — verified <date> (measured): <evidence>`, and the sibling row is byte-identical |
| **A3** | The tick is **refused** (exit 2, **nothing written**) on: a line that is not an open row · empty evidence · generic evidence · a **ceremony** row (SCC-193) · a **merge** row (SCC-175). | five cases, each asserting non-zero exit **and** `read_bytes()` unchanged |
| **A4** | **All four doors that call `finish --apply`** run reconcile before it, and the passage is byte-identical in all four. | a case in `test_command_surfaces.py` extracts the `<!-- reconcile-law -->` block from each of the four command files and asserts all four are **byte-equal** and non-empty; `workflow_lint.py --toolkit-only` exits 0 |
| **A5** | End to end: a walkthrough whose only open row was already done reconciles to clear, and `open_actions()` then returns `[]` so `finish` would close. | case chaining `--tick` then `open_actions()` == `[]` |
| **A6** | `completion-not-illusion.md` carries the law, and all four doors name the rule as in force. | the rule file gains the clause; `grep -c 'completion-not-illusion'` ≥ 1 in each of the four doors |
| **A7** | The new cases are **not vacuous** — every mutant drawn from the new code is killed by a NAMED case. | `mutation_sweep.py --table …/sweep.json` reports every declared mutant KILLED, and the closing unfiltered full-file run is green |

⛔ **A6 is a wiring check, not a prose pin.** Per `prose-pinning-guards-are-vacuous`, no test asserts
the sentence's words. What is checked is that the doors *reference the rule* — a doc→doc edge a
rename would break — and the sentence itself is doc law a human reads.

---

## Design

### The verb

```
jira_feed.py reconcile-actions --walkthrough <path>
jira_feed.py reconcile-actions --walkthrough <path> --tick <line> \
    --evidence "<what proves it>" --source measured|operator
```

**Exit codes reuse this file's existing contract exactly** — `0` did it / nothing open · `3` HELD,
rows still open · `2` the artifact is wrong, nothing written. A new code here would mean the same
condition answers differently depending on which verb found it.

### Why the line number IS the stable id

Ticking rewrites `- [ ]` to `- [x]` **in place**: same line, same line count. So every line number
printed by the list stays valid for the whole reconcile pass, and `--tick` re-reads the file and
re-validates the target before every write. A stale number cannot silently hit the wrong row — it
hits a row that is no longer open, which is refusal 1.

### The five refusals, and which existing helper each reuses

| # | Refused | Why | Reuses |
|---|---|---|---|
| 1 | `--tick` at a line that is not an **open** row under `## Your Actions` | a stale or mistyped number must not tick a neighbour | `_unfenced` + `_OPEN_ITEM_RE` + the `_collect` section walk |
| 2 | empty / whitespace evidence | an empty proof is the empty-input-reads-as-pass shape `tests-must-gate-for-real` bans | — |
| 3 | **generic** evidence — normalised < 16 chars, or < 3 words, or an exact match in the contentless deny-set (`done`, `verified`, `confirmed`, `yes`, `ok`, `it works`, `n/a`, …) | a row ticked with the word "done" records nothing a later reader can check | — |
| 4 | a **ceremony** row | SCC-193: those are the agent's to RUN, not the operator's to decide; ticking one launders it into settled | `ceremony_rows()` |
| 5 | a **merge** row | SCC-175: `finish` computes it from the repo. A hand tick here is exactly the self-certification that fix closed | `is_merge_row()` |

⛔ **Refusal 5 is not in the ticket's plan and is being added deliberately.** Without it the new verb
hands back the affordance SCC-175 spent a lane removing. It costs one `if`.

⚠️ **Refusal 3 is a FLOOR, not a content judge, and the code will say so.** No check can tell a real
measurement from a plausible sentence. What it can do is refuse the forms that carry nothing and make
the writer type something specific. **The real guard is that the evidence lands in the file**, in the
lane's own commit, where a human and the review both read it.

### What a ticked row looks like

```
- [x] **C0 — store the Jira API token.** — verified 2026-08-23 (measured): keychain item `sudo-jira`
```

Same line, so `_ANY_ROW_RE` still matches it and `_collect`'s continuation window still closes on it.
Nothing about the existing parse changes.

### Where the doors change

⚠️ **AUDIT FINDING F2 — it is FOUR doors, not two.** The plan's first draft named the two single-lane
close doors. `grep -rn "jira_feed\.py finish"` over `.agents/commands/` finds **four** bodies that
actually invoke `finish --apply` and close a ticket:

| Door | The `finish` call | Already runs `check-actions`? |
|---|---|---|
| `smh-close-task-merge-tree.md` | `:538` | yes, `:368` |
| `cicd-close-story-merge-tree.md` | `:295` | yes, `:150` |
| `smh-merge-multiple-workingtrees.md` | `:347` | yes, `:345` |
| `cicd-merge-epic-workingtrees.md` | `:250` | no |

Leaving the two merge doors out would let the defect survive on the path that produces the **most**
held tickets — a consolidated epic lands three lanes at once through them. All four get the step.

All four get the identical instruction: **derive a check per open row, run it, tick on the measured
result; where no machine check exists, ask the operator and tick on their word, quoted. A row that
is neither proved nor answered stays open and is reported.**

⚠️ **AUDIT FINDING F1 — "byte-identical" had no check behind it.** `test_twin_parity.py:147` puts
both close doors in `NOT_PAIRED` (*"the Task DOOR - it opens a PR against main and stops"*), and
blocks B and C loop over `PAIRS` — so a `twin-law` marker in these files is **never compared**. The
original A4 (`grep -c`) proved only that the string appears. So the passage is fenced by a literal
marker and a real equality case is written:

```
<!-- reconcile-law -->
… the passage …
<!-- /reconcile-law -->
```

`test_command_surfaces.py` extracts that block from all four files and asserts they are byte-equal
and non-empty. ⛔ **Non-empty matters**: four files each carrying an empty marker pair are also
"all equal", which is the anti-vacuity shape `tests-must-gate-for-real` bans. Promoting the doors
into `PAIRS` is deliberately NOT done — the file records that as *"a design of its own"*, and it
would drag every other shared passage in two large bodies into scope.

---

## Build order

1. **RED** — the six cases in `test_jira_feed.py`, run and pasted failing, against a verb that does
   not exist yet. Read *which line raised*: an `AttributeError` on a missing verb is a real red here
   only because the assertion is about the verb; anything dying in fixture setup is not.
2. **GREEN** — `reconcile-actions` in `jira_feed.py`: `reconcile_rows()` (list + line numbers),
   `evidence_ok()` (the floor), `tick_row()` (the single-line rewrite), `cmd_reconcile_actions()`.
3. The **four** door steps, fenced by `<!-- reconcile-law -->` and byte-identical, plus the `test_command_surfaces.py` equality case.
4. `completion-not-illusion.md` clause 4.
5. SOP paragraph + changelog row (the `sop_currency` gate refuses the commit without it).
6. Receipt-stamped `run_all.py`, then the mutant sweep.

## Declared Change Set

- NEW `_artifacts/_main/2026-08-23_reconcile-actions/implementation_plan.md` — this file → plan
- NEW `_artifacts/_main/2026-08-23_reconcile-actions/task.yaml` — lane manifest → plan
- NEW `_artifacts/_main/2026-08-23_reconcile-actions/walkthrough.md` — evidence, verdict, Your Actions → close
- NEW `_artifacts/_main/2026-08-23_reconcile-actions/sweep.json` — the mutant table → build step 6
- EDIT `_artifacts/_main/INDEX.md` — the session row → plan
- EDIT `.agents/scripts/jira_feed.py` — the `reconcile-actions` verb and its three helpers → A1, A2, A3
- EDIT `.agents/scripts/tests/test_jira_feed.py` — the six RED cases → A1, A2, A3, A5
- EDIT `.agents/scripts/INDEX.md` — the `jira_feed.py` row enumerates the verbs; a new one makes it stale (F3) → A1
- EDIT `.agents/scripts/tests/test_command_surfaces.py` — the four-door byte-equality case (F1) → A4
- EDIT `.agents/commands/smh-close-task-merge-tree.md` — the reconcile step before `finish` → A4, A6
- EDIT `.agents/commands/cicd-close-story-merge-tree.md` — the same step, byte-identical → A4, A6
- EDIT `.agents/commands/smh-merge-multiple-workingtrees.md` — the same step (F2) → A4, A6
- EDIT `.agents/commands/cicd-merge-epic-workingtrees.md` — the same step (F2) → A4, A6
- EDIT `.agents/rules/completion-not-illusion.md` — clause 4, the unverified open box → A6
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — the reconcile step in the close-out section → gate + A4
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — the SCC-298 row → gate

## Out of scope, named so it is a decision and not an omission

- **R4 / R5 / R6 / R7** — the four findings still open from SCC-288's review. They are a separate
  lane under SCC-293 and touch different files (`check_maps.py`, `jira_ticket.py`,
  `generate_doc_graph.py`). Folding them in here is the scope creep the lane rules exist to stop.
- **Auto-ticking.** The verb never derives evidence by itself. It records what a caller measured or
  what the operator said. An agent that could both invent the check and pass it is back to
  self-certifying, which is the whole thing this ticket exists to stop.

---

## Self-Audit (2026-08-23)

**Level: LEDGER+BLAST** — the Declared Change Set touches a rule (`completion-not-illusion.md`), a
script others import (`jira_feed.py`), four command/door surfaces, and the SOP. **Mode: PRE-WORK.**
Repo `Sudo_Hatter_Command`, branch `chore/SCC-298-reconcile-actions`, plan
`_artifacts/_main/2026-08-23_reconcile-actions/implementation_plan.md`, ticket **SCC-298**.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every helper the plan names resolves in jira_feed.py (open_actions :1746 · _unfenced
             :1711 · _OPEN_ITEM_RE :1703 · _collect :1773 · ceremony_rows :2210 · is_merge_row
             :1876 · _ANY_ROW_RE :1873 · cmd_finish :2367 · cmd_check_actions :2341)
             the two line anchors are real: smh :538 and cicd :295 are the `finish` calls
             declared_change_set.py parse -> present true, 16 entries, incomplete []
             stdlib only (re, pathlib, datetime); every doc line writes `python3` with the PC note
             lane fit: zero deployable paths in the set -> /smh-close-task-merge-tree is the door
             Scope Ledger: 4 NEW artefacts x acceptance row
             test strategy vs tests-must-gate-for-real (SCC-145)
read:        .agents/scripts/jira_feed.py · .agents/scripts/declared_change_set.py ·
             .agents/commands/smh-close-task-merge-tree.md ·
             .agents/commands/cicd-close-story-merge-tree.md ·
             .agents/rules/completion-not-illusion.md · .agents/scripts/INDEX.md
verdict:     findings below (F3, F4)
```

```
lens:        2 Parity + Blast
checks_run:  `env -u GITHUB_TOKEN git fetch origin main` FIRST, then git worktree list + per-tree
             diff --name-only origin/main...HEAD + status --short
             command-file row: all four platform doors exist for BOTH close commands (.agents/skills,
             .claude/skills, .agents/workflows, .opencode/commands) - no rename, so no orphaning
             rule row: grep completion-not-illusion in workflow_lint.py _RULE_POINTERS -> ZERO hits
             script row: grep jira_feed in .githooks/ -> zero direct; the caller is
             .agents/scripts/git-hooks/post-commit-jira-start.sh:119, and it calls `start`, not
             `finish` - untouched by this lane. scripts/INDEX.md:22 DOES enumerate the verbs
             twin row: test_twin_parity.py PAIRS/NOT_PAIRED membership for both close doors
             SOP row: both halves in the same commit - planned, and the changelog row with it
             usage-surface row: .agents/scripts/*.py + .agents/commands/*.md + .agents/rules/*.md
             are all sop_currency surfaces; one commit carries them and the SOP together
             risk_seam.py classify --repo <this tree>
read:        .agents/scripts/tests/test_twin_parity.py · .agents/scripts/workflow_lint.py ·
             .agents/scripts/INDEX.md · .githooks/{commit-msg,post-commit} ·
             .agents/commands/{smh-merge-multiple-workingtrees,cicd-merge-epic-workingtrees}.md ·
             docs/_scc_sops_prds/workflows_testing_SOP.md
verdict:     findings below (F1, F2)
```

```
lens:        3 Pre-Mortem
checks_run:  the silent one, the other-path one, the sibling-lands-first one - attached to F1 and F2
read:        (attaches to anchored findings only; originates nothing)
verdict:     narratives attached to F1 and F2; nothing unattached
```

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/scripts/tests/test_twin_parity.py:147` | `"smh-close-task-merge-tree.md": "the Task DOOR - it opens a PR against main and stops "` | **F1.** Both close doors sit in `NOT_PAIRED`, and blocks B/C loop over `PAIRS` — so a `twin-law` marker in them is never compared. A4's `grep -c` proved the string appears, not that the passages match. **Breaks acceptance row A4 as written.** | **high** |
| `.agents/commands/smh-merge-multiple-workingtrees.md:347` | ``then **`jira_feed.py finish --key <KEY> --walkthrough <that lane's walkthrough> --apply`**, then`` | **F2.** **Four** doors call `finish --apply`, not two — the second being `cicd-merge-epic-workingtrees.md:250`. A ticket closed through either merge door would skip reconcile entirely. | **high** |
| `.agents/scripts/INDEX.md:22` | ``| `jira_feed.py` | … | `jira_feed.py check-actions --walkthrough <path>` |`` | **F3.** The row enumerates the verbs by example. A new verb makes the map agents read to *find* a verb stale, and the row was not in the Declared Change Set. | medium |
| the plan's `## Declared Change Set` | `- NEW _artifacts/_main/2026-08-23_reconcile-actions/sweep.json — the mutant table → build step 6` | **F4.** Scope Ledger: `sweep.json` is created by the plan and **no acceptance row required it** — and per `tests-must-gate-for-real` (SCC-145) a plan naming no way to prove its checks non-vacuous is missing that step. | medium |

**Pre-Mortem narratives** (attached, never originating):

- **F1 — the silent one.** Someone later edits the reconcile step in `smh-close-task-merge-tree.md`
  alone. Nothing fails, nothing reports. The `cicd` door keeps the old text, a story lane reconciles
  by different rules than a task lane, and it surfaces months later as *"why did this ticket close
  without evidence?"* — the `sudo-commands-have-ap-twins-that-drift` scar, on the door that writes
  `Done`.
- **F2 — the other-path one.** The operator lands three lanes at once through
  `/smh-merge-multiple-workingtrees`, which is the normal shape for a consolidated epic. Every one of
  those tickets closes without reconcile, and the held-ticket problem this ticket exists to fix is
  untouched on the path that produces the most of them.

**All four are baked into the plan above**, inline and marked `⚠️ AUDIT FINDING`: A4 is now a
byte-equality case over a `<!-- reconcile-law -->` fence in four files, A7 is the mutation row F4
demanded, and the Declared Change Set grew from 12 entries to 16.

### Observations (uncounted, no severity)

- **O1.** `workflow_lint.py:70` `_RULE_POINTERS` carries no `completion-not-illusion` row. One keyed
  on `jira_feed\.py finish` would flag **eight** bodies, six of which only mention the verb in prose
  — and the rule's own frontmatter (`.agents/rules/completion-not-illusion.md:6`) says *"no glob can
  catch it, because the trigger is what the operator ASKS"*. A machinery-keyed pointer is the wrong
  instrument for this rule by its own design. Out of scope, recorded so it is a decision.
- **O2.** `risk_seam.py classify` returned `{"status": "unclassified", "root": "<this worktree>"}` —
  expected and permanently correct in the command centre (SCC-289: the centre is markdown, a code
  graph parses code). Every judgement in Lens 2 came from the diff, not the classifier.
- **O3.** SCC-298's description uses the SCC-288 Part C fast-read shape (Why / Plan / Done / Files),
  so its acceptance content sits under `Plan`, not a heading named `ACCEPTANCE`. Five bullets, each
  naming a concrete observable — the Scope Ledger precondition is met on substance.

### Landing-order dependency

`SCC-280` (`claude/teaching-edition`, `.claude/worktrees/SCC-280-teaching-edition`) holds
**uncommitted** edits to `docs/_scc_sops_prds/workflows_testing_SOP.md` — the one file both lanes must
stage, because `sop_currency` is per-commit. It also holds `.agents/scripts/tests/test_twin_parity.py`,
and this lane reasons about that file (F1) without editing it.

**This lane should land first**: it is smaller and depends on nothing of theirs. If theirs lands
first, `git merge origin/main` in this tree and re-resolve two independently appended SOP paragraphs
— text-level only, no shared machinery.

```
Audit verdict: GO
```
