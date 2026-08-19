# SCC-197 Wave 2 — twin-parity logic and the guard that enforces it

**Lane** `chore/SCC-197-wave2-twin-parity` · worktree `.claude/worktrees/SCC-197-wave2-twin-parity`
**Base** `origin/main` @ `fd22097` · **Riders** SCC-209 (Part A) · SCC-205 (Parts B–E)
**Landing mode** full — this landing closes SCC-197.

> ⛔ **Re-grep every line number in this document before acting on it.** All were measured at
> `fd22097`. Numbers drift. A prior ticket was discarded because its prescription rested on numbers
> nobody re-measured.

---

## 1. Context — what you are working on and why

The repo carries two command families that are the same development system pointed at different
subjects:

- **`.agents/commands/cicd-*.md`** — real project work: front end, back end, agent code in Python,
  prompting. Story lanes, epic branches, sprint boards.
- **`.agents/commands/smh-*.md`** — that same system turned inward on this repo.

**The standard is the shared law, not either family.** Today the law is more *complete* on the smh
side, for one reason: that is where development happened while the system was being built. Nothing
in the repo ever compared the two families, so law written into one never propagated to the other.

⛔ **The direction is inverting.** Project work is becoming the primary use, so new law will land on
the cicd side and smh will fall behind. Any mechanism built here must be **symmetric** — pointed at
neither family.

**A difference is a missing-parity defect until proven otherwise.** A difference is legitimate only
when the subject forces it:

| Legitimate | Not legitimate |
|---|---|
| merge target (epic branch vs `origin/main`) | "the fast lane deserves a weaker review" |
| spec source (story file + certification vs `implementation_plan.md`) | "that is how the other family does it" |
| target resolution (cicd binds exactly one project, never this repo) | "BMAD covers it" |
| tooling (this repo has no venv, no ruff, no tsc) | being merely older on one side |
| story / board / sprint ceremony | |

### Scope of this lane

This lane builds the **mechanism** that keeps the families aligned. It does not port command content.

| Ticket | Owns | Not this lane |
|---|---|---|
| **SCC-209** | stop maintaining the `_AP` twins (Part A) | |
| **SCC-205** | the vehicle, the guard, the hoists (Parts B–E) | |
| SCC-210 | close-out rebalance and rename | ✗ |
| SCC-211 | `/cicd-push-e2e` production door | ✗ |
| SCC-212 | 84 command content ports | ✗ |

Findings were produced by two adversarial sweeps, each finding re-measured against `fd22097` and
passed through a skeptic tasked to refute, then filtered by a three-question disposition test
(is it real · does it change behaviour · is it in scope). 172 confirmed became 126 real fixes.
The items below are the subset that is mechanism.

---

## 2. Part A — SCC-209 · stop maintaining the `_AP` twins

### Context

`workflow_lint.py` enforces freshness between each `*-AP.md` file and its primary via an
`ap_reconciled: <sha>` stamp. The `_AP` lane is being abandoned, so that enforcement is now pure
cost — and it is **armed**: the check fires the moment any cicd primary is committed without its
twin. Editing `cicd-code-review.md` in a later part would turn the gate red and force a restamp of a
file already declared abandoned.

**Part A runs first for that reason.** It is not sequencing preference; it defuses a trap.

### DO

- Delete `AP_RECONCILED` (`:192–193`), `check_ap_twins()` (`:196–252`), the single call site
  (`:523`), and both helpers that die with it — `_last_commit_ts` (`:180–184`) and
  `_last_commit_sha` (`:186–190`). Those helpers have exactly four references tree-wide: two
  definitions and two uses, both inside `check_ap_twins`.
- Delete the AP-twin test block in `test_workflow_lint.py` **in the same commit**. `:310` and `:402`
  call the function by attribute; removing the definition alone raises `AttributeError`.
- Strip `ap_reconciled:` from `cicd-code-review-AP.md:63` and `cicd-self-audit-AP.md:17`, and replace
  each restamp instruction and its reconciliation log with a single line marking the file
  unmaintained and slated for rewrite. Apply the marker to all three `*-AP.md` files.
- Correct the one command body that advertises `-AP twin drift` as part of the gate it runs.
- Edit `_artifacts/_memory/sudo-commands-have-ap-twins-that-drift.md` **surgically**: remove the
  `_AP` obligation, keep the cicd/smh twin law, and correct its claim that hoisting keeps bodies
  under a byte threshold — oversized bodies now receive an auto-generated thin launcher, so byte
  count is no longer an argument for hoisting.
- Stage the SOP doc in the same commit as any `.agents/commands/` or `.agents/scripts/` change.
- Run `/smh-sync-agents` at the end of the part.

### DO NOT

- **Do not delete the three `*-AP.md` files.** Three autopilot engines still invoke them by name.
  This part removes the *obligation*, not the files.
- **Do not leave a no-op stub** in place of `check_ap_twins`. Delete it.
- **Do not strip the stamps before the check and its tests are gone.** Doing so empties a dict that
  `test_workflow_lint.py:427` requires to be truthy.
- **Do not trust the line numbers above without re-grepping.** An earlier draft of this work named
  `:495–499` for the helpers; those lines are `main()`, and following it would delete working code.

### Success looks like

- `grep -c 'check_ap_twins\|AP_RECONCILED\|ap_reconciled\|_last_commit_sha\|_last_commit_ts' .agents/scripts/workflow_lint.py` → `0`
- `run_all.py` exits 0; `workflow_lint.py --toolkit-only` exits 0
- Three `*-AP.md` files still present, all three carrying the unmaintained marker
- `grep -rn 'ap_reconciled' .agents/commands/` → empty

### Failure looks like

- The suite dies with `AttributeError` because the function was removed and its tests were not.
- A later part edits a cicd primary, the gate reds, and someone restamps an abandoned file to clear it.
- An autopilot engine invokes a command that no longer exists, and the stage improvises silently
  instead of failing — an agent runs with no specification and writes artifacts that look normal.

---

## 3. Part B — the vehicle

### Context

`cicd-code-review.md` and `cicd-self-audit.md` carry **no "Rules in force for this command" block at
all**. They are the only 2 of 26 commands without one; both smh twins have one.

That block is the mechanism by which a rule reaches a command. Its absence is why those two inherit
none of the hoisted law in Part E — and it lints clean today, because the pointer check only warns
when a body matches one of five *machinery* patterns, none of which covers disposition, gate
vacuity, piped exit codes, or both-machines.

**Nothing in Part E can land before this exists.** There is nowhere for a pointer to sit.

### DO

- Add a "Rules in force for this command" block to both files, mirroring their smh twins' pointer
  sets minus subject-forced entries, plus `smh-target-resolution.md`, which is the cicd-only pointer.

### DO NOT

- Do not add pointers to rules those commands do not actually obey. A block padded with irrelevant
  rules trains agents to skip reading it.

### Success looks like

- `grep -c 'Rules in force for this command'` → `1` in each file
- `workflow_lint.py --toolkit-only` still exits 0

### Failure looks like

- Part E hoists law into a rule, and the two cicd commands that most need it still cite nothing —
  the hoist reads as complete while changing nothing for the family it was meant to fix.

---

## 4. Part C — safety defects in `cicd-quick-dev`

### Context

This command performs real project work and is roughly two ticket-generations behind its twin.

### DO

- **C1** — Step 0.5 (`:37`) describes a `chore/<KEY>-<slug>` branch off `main`, with **no worktree**,
  "merged back to `main` in the same session", naming **no door**. Its own Done section says never to
  touch `main`. Remove the same-session merge language and name the real door. Note that no
  chore-lane door currently exists for a project repo; **state that gap, do not invent a command to
  fill it.**
- **C2** — remove `no worktree`; a worktree is required for every commit-producing lane, and this
  command's own plan-skip exemption is conditional on the worktree existing, so the line voids its
  own carve-out.
- **C3** — state that a fired eject re-arms the plan-first gate, and list that gate in the
  rules-in-force block.
- **C4** — route the review through the house review engine, naming `lens_budget: standard`
  explicitly. Both interactive callers already name it. Naming nothing is not neutral: it silently
  selects the autopilot's budget.
- **C5** — stop passing `--story` unconditionally to the Dev Record call; the record is found by
  slug, and passing it creates a second record for one ticket.

### DO NOT

- **Do not read C4 as removing BMAD.** The house engine *runs* the BMAD lenses — one of them is
  `bmad-review-adversarial-general` plus a hunter contract, deliberately starved of context, beside
  `bmad-review-edge-case-hunter`. Today this command calls one lens bare and hand-rolls the rest.
  Routing through the engine means **more** BMAD, under contract, with triage.
- Do not mint a new command to close the chore-lane door gap. Record it; it is a separate decision.

### Success looks like

- No same-session `main` merge language anywhere in the file; the real door is named
- No `no worktree`; the worktree rule is cited
- `code-review-engine` invoked, `lens_budget` named
- `--story` no longer passed unconditionally

### Failure looks like

- An agent follows the literal step list and merges to production.
- A lane commits without a worktree and collides with a sibling lane already holding those files.
- The review runs one lens with no contract and no triage, and reports the same verdict shape as a
  full review — indistinguishable in the artifact from one that actually ran.

---

## 5. Part D — the guard

### Context

`workflow_lint.py --toolkit-only` exits **0** at `fd22097` while all 172 findings are live in the
tree. Nothing in the repo compares the two families. That is the root cause, and this part is the fix.

### DO

- Build a **scoped-region** check modelled on the existing precedent at
  `test_review_engine.py:1257–1333`, which compares one subject-independent paragraph across two
  files. Reuse its six parts: a pinned pair list · a derived-set completeness guard so the list
  cannot silently go stale · a marked-by-literal extractor · equality after whitespace normalisation
  · per-clause presence rows so equality cannot be vacuous agreement · two counter-examples, one
  perturbation that must break equality and one law-less input that must extract empty.
- Assert **two** things, not one:
  1. **Symmetry** — every shared-law marker present in one twin is present in the other. A marker
     with no counterpart fails, naming which family lacks it.
  2. **Identity** — where both carry the marker, the regions are byte-identical after whitespace
     normalisation.
- Ship an **auditable escape hatch**: a `twin-divergence` marker carrying a reason, honoured by the
  extractor, and **counted and printed** so an intentional asymmetry is a recorded decision.
- Make the failure message name both files, the diverged clause, and the one-line remedy.
- Build the pair list from the cross-family duplicates already declared in
  `.agents/commands/INDEX.md`, and add the two pairs it omits (`label-tasks`, and
  `merge-epic-workingtrees` ↔ `merge-multiple-workingtrees`).
- Home it in a new `test_twin_parity.py`, auto-discovered by `run_all.py`. State why it is not folded
  into `test_review_engine.py`: that file is scoped to the review engine, this check spans six pairs
  across dev, audit, review and landing.
- Put the § 1 context into the script's header, so the guard explains what it protects.

### DO NOT

- **Do not re-aim the existing `ap_reconciled` stamp at these pairs.** It derives the primary from
  the twin and scans only the twin's text, so it is one-directional — the cicd file could drift under
  a green stamp. Its comparand is also whole-file, so every commit touching one side's
  subject-specific text would invalidate it, producing reflexive restamping. Part A deletes it anyway.
- **Do not rely on identity alone.** Identity only compares regions both files already mark. The
  failure that caused this ticket was law written into one family and absent from the other — no
  counterpart region exists, so identity sits green through the entire failure. Symmetry is the layer
  that catches it.
- **Do not scatter reciprocal notes into six command bodies.** That creates six hand-maintained facts.
  Promote the existing central declaration instead.
- Do not widen the check to whole files. That would force subject-specific law to match and break
  both commands.

### Success looks like

- Deleting a shared clause from one family member of a declared pair makes `run_all.py` exit
  non-zero. It exits **0** today — that zero is the bug.
- A new `cicd-*`/`smh-*` name-counterpart absent from the pair list fails the completeness row.
- An intentional divergence is visible in the run output, not silent.

### Failure looks like

- The guard passes because both files are missing the same law — a vacuous green.
- Someone renames a marked phrase, the shared region silently shrinks, and the guard keeps passing
  over a smaller and smaller surface. Only the completeness guard catches this; keep it.
- The guard has no legitimate exit, so the first person who needs one bypasses the gate entirely.

---

## 6. Part E — hoist the shared laws

### Context

Some obligations exist in one family and nowhere in the other, or exist only inside a skill step that
no rule owns. A hoisted rule plus a pointer replaces N copies and shrinks the content-port backlog in
SCC-212, which is why this part precedes it.

Byte count is **not** a justification for hoisting. Oversized command bodies receive an
auto-generated thin launcher, so size is handled. Hoist only for single-source-of-truth value.

### DO

Hoist four laws, each into a rule that already exists:

1. **The three-question disposition test** (is it real · does it change behaviour · is it in scope;
   plus "it is cheap" is not a reason) — currently lives **only** in
   `code-review-engine/steps/step-01-review.md:336–366`, owned by no rule, carried by none of the
   four audit commands. → **`code-standards.md`**, which already owns the FAIL-vs-CONCERNS split and
   is the one rule both clean-code audits already bind.
2. **"A gate that cannot fail is a finding"** → `tests-must-gate-for-real.md` (measured absent today).
3. **"Run gates bare"** — a pipe returns the pipe's exit code → `tests-must-gate-for-real.md`
   (measured absent today).
4. **Both-machines awareness** — the two machines differ on `python3` versus `python`, and on
   absolute path shapes → `code-standards.md` § 5, which already states the underlying rule.

Then:

- Add a pointer row to `workflow_lint.py`'s rule-pointer check so a command that produces findings
  and cites no disposition rule goes **red**. Key the row on the **machinery**, never the concept —
  a concept-keyed row previously matched six unrelated bodies and none of the three that mattered.
- Add the memory-store clause drafted in `DRAFT-memory-law.md` to `artifacts-always-first.md`.

### DO NOT

- **Do not create new rule files.** All four targets exist.
- **Do not let a pointer replace the inline obligation.** A pointer that removed the restatement is
  itself a finding: agents follow the literal step list, so a bare pointer gets skipped. Rule,
  pointer, and restatement — all three.
- **Do not hoist the disposition test into `artifacts-always-first.md`.** Measured: only 2 of the 6
  finding-producing commands bind that rule, and both are smh. It governs *where* findings are
  written, not *how* they are judged.

### Success looks like

- Each hoisted law resolves from a rule **and** is restated inline in at least one command that must
  obey it — `grep` proves both halves.
- A finding-producing command citing no disposition rule makes `workflow_lint --toolkit-only` exit
  non-zero. It exits 0 today.
- `grep -rln "_artifacts/_memory" .agents/rules/` returns more than one file. It returns 1 today.

### Failure looks like

- The law is written into a rule nothing loads, and every command carries on as before.
- A discipline is recorded in the memory store instead of a rule. It looks enforced, nothing enforces
  it, and when the entry is pruned the problem returns while the record says it was handled.

---

## 7. What is deliberately not touched

Three findings were rejected during verification because acting on them would damage working
commands. Do not reopen them:

- A claim that one command is the **only** one in either family lacking a test-gate citation —
  measurably false; another command also has zero. The underlying gap is real and is fixed on its
  own merits.
- A claim that both clean-code audits describe an unbounded fix queue — the very next sentence,
  byte-identical in both, already bounds it with `applied / deferred / dismissed`. Part E adds
  **above** that sentence; it does not edit it.
- A claim that one command copies a resolution ladder instead of citing the rule — it already cites
  it, and inline restatement is mandated, not a defect.

Six differences in one pair and seven in another were classified subject-forced. Leave them, and
state in the walkthrough what was left different and why.

---

## 8. Acceptance → the assertion that proves it

| # | Acceptance | Assertion (must fail first) |
|---|---|---|
| 1 | AP enforcement gone | the five-symbol grep on `workflow_lint.py` → 0 |
| 2 | Suite still green | `run_all.py` exits 0; `workflow_lint --toolkit-only` exits 0 |
| 3 | AP files kept, marked | 3 files present, 3 carry the marker, no `ap_reconciled` in `.agents/commands/` |
| 4 | The vehicle exists | `Rules in force` present in both cicd files |
| 5 | No same-session main merge | phrase absent; real door named |
| 6 | Worktree required | `no worktree` absent; worktree rule cited |
| 7 | Review routes to the engine | engine invoked; `lens_budget` named |
| 8 | **The guard fails on real drift** | perturbing a shared clause makes `run_all.py` exit non-zero — exits **0** today |
| 9 | The guard cannot go stale | an unlisted name-counterpart fails the completeness row |
| 10 | The guard catches one-sided law | a marker in one twin with no counterpart fails |
| 11 | Each hoisted law is reachable | resolves from a rule **and** restated inline |
| 12 | Disposition is enforced | uncited finding-producer makes the lint exit non-zero — exits 0 today |
| 13 | Memory has a rule | `grep -rln "_artifacts/_memory" .agents/rules/` returns > 1 — returns 1 today |
| 14 | Mutation-proven | every new assertion declared against a mutant it alone kills |

## 9. RED first

Nothing is edited until something fails.

Start with **#8**: perturb a shared clause and watch `run_all.py` exit **0**. That zero is the defect
this lane exists to remove. Then #1, #3, #4, #5, #6, #7, #12, #13 as greps returning the wrong count now.

Paste the actual failing output, and read **which line raised it** — a check that dies in setup looks
identical to one that fails its assertion, and only one of those is a real failure.

⛔ Assertions must run on **both machines**: one has no bare `python`, the other has no `python3`.
Write them interpreter-neutral or provide both forms.

Declare the mutant table before mutating, draw every mutant from the code rather than from your own
cases, and run the sweep as one scripted pass rather than one mutant at a time.
