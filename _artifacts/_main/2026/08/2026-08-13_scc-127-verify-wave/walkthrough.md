---
IsArtifact: true
ArtifactMetadata:
  title: SCC-127 verify wave — walkthrough
  type: walkthrough
  date: 2026-08-13
---

# SCC-127 — Verify wave (walkthrough)

Lane: `chore/SCC-127-verify-wave` · worktree `.claude/worktrees/scc-127-verify-wave` · off `main`
@ `36e1ffe`. Epic: SCC-116 (house review engine). Plan + self-audit: `implementation_plan.md`
beside this file.

**What shipped.** `steps/step-02-verify.md` stops being an honest pass-through and becomes the
wave the engine was scaffolded for: an **Evidence Verifier** and a **Compound Synthesis** role,
launched as ONE concurrent batch, both fed the programmatic `evidence_extract.py --findings`
dossier, both self-gating on the finding count. Severity becomes evidence-forced — the verifier's
`revised_severity` reaches step 3, where the rule that it outranks the hunter's assertion was
already written and had nothing to act on. `steps/step-03-triage.md` loses its "step 2 is a
pass-through until SCC-127" caveat for the live rule and gains `compound` as a finding source.

## Task Checklist

- [x] Pin repo + lane from command output; move SCC-127 to `In Progress` (`jira_feed start` exit 0)
- [x] Read the sibling lanes before planning (SCC-126 live, SCC-128 empty)
- [x] Fix the checkable acceptance list A1–A10 from the ticket + the epic plan
- [x] Write `implementation_plan.md`; run `/smh-self-audit` → **GO**, 2 findings baked in
  - the embedded extractor command must carry the `python3`/`python` two-machine note, or a PC
    role subagent fails and "ran cold" records a fake reason
  - a gate-skipped wave must write a note, or 0-findings reads identically to all-confirmed
- [x] STOP for the literal `approved` (given 2026-08-13)
- [x] RED — 60 guard rows binding the WIRING, each with a counter-example proven to go red
- [x] GREEN — rewrite step-02, edit step-03, mirror both to the `.claude/` cache
  - one check failed for a real reason on first run: my line wrap split the phrase it pins
    (`gates exactly as hard as the path it replaces`) across a newline; rewrapped, not weakened
- [x] Full suite + toolkit lint bare, on the code that lands
- [x] Commit inside the worktree, explicit paths (`89a5423`, `6441e64`, `684c159`)
- [x] Review gate — `/smh-code-review` (section below)
  - ⛔ the hunt found the wave **did not actually work**: the instruction to run the extractor sat
    in orchestrator prose, which step-01's convention says never reaches a subagent, so both roles
    would have reviewed cold while the record claimed a dossier. Fixed in `49ea340`
  - two mutations survived the first guard set (gate-table column swap, role-heading swap); the
    guard now spans each heading to the prompt it routes, and both die
- [x] Re-run the floor on the fixed tree and re-prove the mutants (27/27 killed)

## Evidence

Measured at HEAD **`49ea340`** (`git rev-parse HEAD`) — the post-review-fix tree, which is the code
that will actually land. The artifact commit after it changes no code or test.

Check names below are the ones in the file at `49ea340`; several were renamed by the review fixes.

| Acceptance item | Proving assertion | Result |
|---|---|---|
| A1 — 0 findings → no wave | `step-02: zero findings skips the entire step` + the gate table row `\| 0 \| **does not run** \| **does not run** \|` | GREEN |
| A2 — <2 findings → no compound | `step-02: under two findings there is no compound pass` + gate row for `1` | GREEN |
| A3 — both roles consume `--findings`; join by index | `step-02: the extractor invocation is pinned inside the prompt` · `the dossier block is prompt text appended to BOTH roles` · `the role is TOLD to build the dossier, in its own prompt` · `the findings JSON carries the keys the extractor reads` · `the join is by index, never by title` · `the extractor is pointed at WORKTREE, never REPO` | GREEN |
| A4 — verifier framing + 4 questions + 5 output fields | 11 rows: `neither reviewer nor adversary` · `independent investigator` · Q1–Q4 · `verified` / `actual_behavior` / `revised_severity` / `revised_confidence` / `verification_notes` | GREEN |
| A5 — compound contract | 6 rows: `NEW findings only` · `contributing_findings` exact titles · confidence ≥ 0.6 · empty list valid | GREEN |
| A6 — extractor failure = cold, does NOT cap | `a failed extractor leaves that role running cold` · `a cold role does NOT cap the verdict` · `a dead script is not a dead role` · `the cold rule covers BOTH roles, and names which` | GREEN |
| A7 — role-failure contract inherited | `a failed role is retried once` · `rerun inline` · `only a still-dead role raises the floor` · `a gate-skipped role is not a dead role` · `a dead step-2 role raises the floor too` (step-03) · `an inline rerun is cold by construction and recorded so` | GREEN |
| A8 — no filter at this layer | `this step drops nothing` · `a refuted finding still reaches triage` · `the no-noise-filter law binds at this layer too` | GREEN |
| A9 — step-03 caveat retired | `grep -rn "pass-through until SCC-127\|verification pass not yet installed" .agents/skills/code-review-engine/ .claude/skills/code-review-engine/` → **no matches** | GREEN |
| A10 — suite + byte-identical cache | `run_all.py` 21/21 exit 0; `cache is byte-identical to master` | GREEN |

### RED → GREEN

**RED** — the new rows run against the still-unwritten step file (the assertions fail on absent
content; nothing dies in setup):

```
[FAIL] step-02: both roles run concurrently in one wave
[FAIL]   ^ counter-example applies: steps/step-02-verify.md: '**concurrently, in ONE wave**' not present, so the proof would be vacuous
[FAIL]   ^ counter-example is rejected: check survives its own counter-example — it cannot fail on content
[FAIL] step-02: the gate table gives 0 findings neither role
...
-- 380/554 passed --                                        EXIT 1   (174 failing = 58 rows x 3)
```

**GREEN** — after the step files were written and mirrored:

```
-- 554/554 passed --                                        EXIT 0
```

*(Those two blocks are the build's own RED→GREEN, at `6441e64`. The review fixes then took the file
to 193 rows / 626 cases — the final totals are in the table directly below and in the review
section.)*

### The gate, run bare (no pipes — a piped gate returns the pipe's exit code) @ `49ea340`

| Gate | Output | Exit |
|---|---|---|
| Enforcement suite | `21/21 files passed` · **1569/1569 cases** | **0** |
| Toolkit lint | `-- 0 error(s), 0 warning(s), 8 info --` | **0** |
| Assertion evidence | `-- 626/626 passed --` | **0** |
| SOP currency | no output (the diff carries no usage surface) | **0** |
| SOP currency — **positive control** | same script, `--paths .agents/commands/smh-code-review.md` → `Commit rejected.` | **1** |
| Link + anchor | 9 paths across 3 changed `.md` files, **0 dead** | — |
| Door parity | no command added/renamed/deleted (`git diff --name-only main...HEAD -- .agents/commands/` = 0) | n/a |

The SOP control matters: exit 0 on this diff is a real pass, not a vacuous one — the same script
rejects a commit the moment a usage surface is in the path list. The `[sop-ok]` in the commit
message is therefore belt-and-braces rather than load-bearing, and is recorded as such.

## Case-count arithmetic (nothing displaced anything)

Counted from the AST of both versions of the guard file rather than by hand:

| | rows total | step-02 rows | step-03 rows | file cases | suite cases |
|---|---|---|---|---|---|
| `main` @ `36e1ffe` | 115 | 5 | 18 | 392 | 1335 |
| the build @ `6441e64` | 169 | 56 | 21 | 554 | 1497 |
| after review fixes @ `49ea340` | 193 | 78 | 23 | 626 | 1569 |

The build added **60 rows and retired 6** (net +54); the review fixes added **24** more. Every row
contributes exactly 3 assertions, so the case deltas are +162 and +72 — and both land on the
measured suite totals exactly. The change is precisely additive at every step, so no commit
displaced another lane's tests.

⚠️ **Correction, recorded rather than rewritten:** the commit message on `89a5423` says *"58 new
guard rows"* and my first correction of it said 55. Both were hand counts and both were wrong; the
review's F11 caught it and the AST count settles it — **60 rows added, 6 retired, net +54**. The
INDEX row is corrected; the commit message stays as written, with this line as its erratum.

*(Counts above are the pre-review build. After the review fixes: **193 rows**, suite **1569 cases**
— see the Code Review section.)*

## Code Review (2026-08-13)

Verdict: PASS @ 49ea340
Suite evidence measured at `49ea340` — the post-fix tree, not the tree that was reviewed.

**Scope.** `git diff main...HEAD`, 7 files: the two engine step files, their two `.claude/` cache
mirrors, the guard test, and this session folder.
**Method.** Clean-room adversarial hunt in a subagent with **no** conversation context and no
sight of the plan until after its findings were formed (read-only; it was told so explicitly,
because a reviewer that mutates the shared checkout destroys sibling lanes' in-flight work).
Then the acceptance audit, the command-centre gate, an independent 27-mutant kill test, and the
clean-code pass.

### Findings

| file:line | severity | failure scenario | disposition |
|---|---|---|---|
| `step-02-verify.md:34-45,60,99` | **critical** | The instruction to RUN the extractor lived only in orchestrator prose. Step-01's convention says a subagent receives blockquoted text and nothing else, so **both roles would have been launched believing a dossier existed, and reviewed cold** — and the cold-run note would not have fired, because it was conditioned on the extractor *failing* rather than on it never being invoked. The record would have read as a warm, dossier-backed verification that never happened. | **applied** — the dossier is now a shared block appended to BOTH prompts (step-01's own shared-rubric idiom), so the instruction is prompt text |
| `test_review_engine.py:373-575` | important | Two one-edit mutations inverted the routing with all 554 cases green: swapping the gate table's two header cells (so "verifier runs alone at 1 finding" reads as its opposite), and swapping the two role headings (publishing the compound prompt as the verifier's, so nothing is ever verified). 21 rows matched text *inside* prompt blockquotes with nothing binding them to the heading that routes them. | **applied** — header row pinned; each heading spanned to the first line of the prompt it routes. Both mutations now die (M17, M18) |
| `step-02:150` vs `step-03:72,80` | important | Step-02 promised CONCERNS for a dead **role**; step-03's §5 table — which calls itself *"the single definition; every caller reads it rather than inventing its own"* — had a row only for a dead **lens**. The orchestrator would find no row and return `severity_floor: none`. The promise was unreachable. | **applied** — dead-role row added, with recovered/gate-skipped roles explicitly excluded |
| `step-02:34` vs `:148` | important | An inline rerun runs in the orchestrator's context, which has no Bash — so it is cold **by construction, forever** — yet was recorded as an ordinary `recovered-inline`, which step-01 defines as "coverage is complete". | **applied** — inline reruns are recorded `cold (no dossier)`; still not floor-raising, and the reason is written down |
| `step-02:38,60` | important | The pinned invocation passed a literal `"$REPO"` that no subagent can resolve (→ `--repo ""`, exit 2, cold review for a plumbing reason), and pointed at `REPO` rather than `WORKTREE`. In a lane the extractor would read **`main`'s copy of every file at the lane's line numbers**, so the verifier would truthfully refute correct findings. | **applied** — placeholders substituted by the orchestrator; `WORKTREE` mandated with the failure mode stated |
| `step-02:130-132` | important | A compound finding passes neither step-01's three hunter gates nor this step's verifier, yet a `critical` from it FAILs a merge on strictly less evidence than any other finding — against the engine's own axiom that verification is what makes severity load-bearing. | **applied as a written decision, not a behaviour change** — it may still gate, for the recall-first reason the no-noise-filter law gives, with an explicit instruction to revisit when a compound re-verify pass exists |
| `step-02:51-52` | suggestion | Extractor failure named only the verifier; Compound Synthesis depends on the same dossier and had no defined behaviour, so an orchestrator would improvise — possibly raising the floor, which the same paragraph forbids. | **applied** — the cold rule covers both roles and names which one ran cold |
| `step-02:11,21-22` | suggestion | The ≥2 compound gate counts raw findings, but dedupe is step-03's job, so two lenses reporting one issue trip the gate and compound is asked what a finding means "together" with its own duplicate. | **applied** — the raw count is stated as deliberate, with the boundary case's (cheap) outcome named |
| `step-02:24-27` | suggestion | `verify wave: skipped (0 findings)` is emitted identically for a clean diff and for a fan-out where **every lens died** — the exact conflation the paragraph's own argument forbids. | **applied** — a dead-lens variant of the note |
| `step-02:13-22`; test `:376-393` | nitpick | A 3-row table restated as two prose bullets, both pinned; and a check named "both modes' flags" pins one mode. | **partly applied** — check renamed to what it pins. The bullets stay: they carry the cost rationale the table cannot |
| `INDEX.md:7` | nitpick | Row claimed "58 new guard rows"; the real delta is 60 added / 6 retired / net +54. | **applied** — corrected from the AST count, with the erratum recorded rather than the history rewritten |

**11 findings: 10 applied, 1 partly applied. None dismissed.**

### Gate

| Gate | Output | Exit |
|---|---|---|
| Enforcement suite | `21/21 files passed` · **1569/1569 cases** | **0** |
| Toolkit lint | `-- 0 error(s), 0 warning(s), 8 info --` | **0** |
| Assertion evidence | `test_review_engine.py` **626/626** | **0** |
| SOP currency | no output on this path set | **0** |
| SOP currency — positive control | `--paths .agents/commands/smh-code-review.md` → `Commit rejected.` | **1** |
| Link + anchor | 9 paths across the changed `.md` files, 0 dead | — |
| Door parity | no command added/renamed/deleted | n/a |
| `py_compile` | clean | **0** |

**Mutation evidence — 27 mutants, 27 killed.** The 16 written during the build, plus the reviewer's
two survivors (M17 column swap, M18 heading swap), plus one per rule the fixes added (M19–M27).
Guard hygiene re-verified across all **193** rows: every regex matches its real file, every
counter-example kills its own check, and every counter anchor is unique in its file, so no
`.replace(…, 1)` can mis-target.

### Acceptance

A1–A10 all evidenced in the `## Evidence` matrix above; the review added no acceptance item and
found no drift (every file in the diff traces to an item or to the `check_maps` INDEX-row gate).

### Clean-Code Gate

Machine floor is the gate table above — suite, lint, `py_compile`, link/anchor, SOP currency, all
green. Judgment pass: no stale scaffold language survives anywhere in the engine or its guard
(`grep` for `scaffold` / `not yet installed` / `until SCC` / `pass-through` returns nothing);
step-02 honours step-01's blockquote convention (that was F1, now fixed and pinned); the guard
file's docstring still describes its actual design. No new abstraction, no new file, no flag.

### Step 0.7 — blast radius re-derived against current `main`

1. **Nothing this diff references moved.** `main` is unchanged since the lane's base `36e1ffe`:
   `git diff --name-only <base>..main` returns **0 files**.
2. **True overlap: 0 files. `merge-tree` is clean** (a tree sha, no conflict messages).
3. **Sibling lanes:** SCC-126 (literal lens) still holds *uncommitted* edits to
   `test_review_engine.py` and `step-01-review.md` — a **landing-order dependency**, either order.
   Whoever lands second re-merges the tests file (their rows are in the step-01 section, mine in
   step-02/03 — disjoint) and re-runs the suite; if SCC-126 also adds a `source` value to
   step-03 §1, both values belong on that line. SCC-128 (rewire callers) is still empty and
   depends on this lane semantically, not textually.

### Changes applied

The six blocking findings and four of the five soft ones, in `49ea340`. The walkthrough body above
was refreshed to match: the row-count correction now carries the AST-measured figures, and the
pre-review totals are labelled as such.

## Your Actions

- [ ] **Merge and close out** — `/smh-close-task-merge-tree` (that invocation is the merge sign-off;
      one invocation, one merge). Nothing else here is owed by the operator.

## Post-absorb re-measurement (2026-08-13, landing set 126→127→128)

**Verdict: PASS @ eeffd8f** — re-measured after absorbing `main` at `a4975bf` (SCC-126's literal
lens). The pre-absorb `Verdict: PASS @ 49ea340` above is **left standing on purpose**: it described
a `main` that no longer exists, and the record of what was true then is worth more than a tidy file.

The absorb was not doc-only, so the earlier verdict did not carry itself — four files conflicted and
three resolutions were judgement calls, written up in the merge commit `eeffd8f`:

- **`step-03-triage.md`** — 126 added `literal` to the finding `source` vocabulary, this lane added
  `compound`. **Either side winning orphans a source**, so both survive.
- **`test_review_engine.py`** — a true three-way hunk. This lane retires the five step-02
  pass-through checks (they pin text this lane deleted); 126 kept them, having no reason to know.
  Merged as: this lane's side in full + 126's 39 additions, the five superseded entries not
  restored. A naive union would have re-armed five checks against deleted text.
- **`_artifacts/_main/INDEX.md`** — ⚠ the first resolution **dropped SCC-137's pre-existing row**,
  which sat inside the conflict region because both lanes append at the same table head. `run_all`
  caught it — and the catcher was the `check_maps` missing-row gate SCC-137 itself shipped, firing
  on the loss of its own ledger row. Restored in date order.
- **Generated mirrors** — resolved by re-running `sync-agents`, never hand-merged.

```
python3 .agents/scripts/tests/run_all.py                -> 21/21 files, 1690/1690 cases, exit 0
python3 .agents/scripts/workflow_lint.py --toolkit-only -> 0 errors, 0 warnings, 8 info, exit 0
python3 .agents/scripts/check_maps.py --depth3-only --strict -> exit 0
```

**Case total exactly additive across both lanes: 1335 (main) + 121 (SCC-126) + 234 (this lane) =
1690.** Neither lane displaced the other's tests, despite both editing the same guard file.
