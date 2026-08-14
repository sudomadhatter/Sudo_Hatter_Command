# SCC-147 — interactive review callers name `lens_budget: standard`

**Ticket:** SCC-147 · **Lane:** `chore/SCC-147-lens-budget` · **Off:** `main` @ `0677441`
**Plan:** `implementation_plan.md` (this folder), audited GO before any edit.
**Parallel lane:** SCC-148 (`task_preflight` incident misroute) — disjoint file set, landing order free.

## Task Checklist

- [x] Step 0 — repo + lane resolved from `rev-parse`; SCC-147 moved to In Progress at the tree.
  - Sibling-lane read found `chore/SCC-145-mutation-doctrine` live at session start. **It landed on
    `main` mid-lane** (the operator said so), so the lane was fast-forwarded onto `0677441` before
    the first edit rather than absorbing a merge later.
- [x] Step 1 — checkable list fixed from the ticket's own ACCEPTANCE block (A1–A5 in the plan).
- [x] Step 1.5 — plan written, `/smh-self-audit` run (Full), **verdict GO**, two of its own findings
  baked back into the plan before work started (the AP-twin note had to be rewritten whole, not
  patched; the case delta was +8, not the +6 first written).
- [x] Step 1.6 — subtasks: **nothing clears the bar.** Four small edits in one commit are not four
  branches.
- [x] Step 2 — RED first, on the guard, before either command was touched.
- [x] Step 3 — GREEN: one row per interactive caller, twin note rewritten, doors regenerated.
  - **The removal proof was run twice, because the first run was invalid.** See Evidence.
  - The AP-twin stamp gate (SCC-82) and the artifacts INDEX gate both fired on this work and both
    were satisfied properly rather than silenced. See Evidence.
- [x] Step 3.5 — eject tripwire checked: no deployable path, not story work, list stayed checkable.
- [ ] Step 4 — review gate (`/smh-code-review`) — appended below when it runs.

## Evidence

### The defect, stated against the source

`.agents/skills/code-review-engine/steps/step-01-review.md:153-161` defines `lens_budget` once and
says, in as many words, that **a caller naming none gets `capped`** — the safe default, chosen
because the cost of guessing wrong the other way is an unbounded overnight spend nobody is watching.
`SKILL.md:32` repeats the default in the input table.

`/cicd-code-review-AP` named `capped` explicitly. Neither interactive caller named anything:

| Caller | Before | Effect |
|---|---|---|
| `/cicd-code-review` Step 1 table | no `lens_budget` row | silently ran the autopilot budget |
| `/smh-code-review` Step 1 table | no `lens_budget` row | same — rewired to the engine in SCC-128, same omission |

Nothing was unsafe (the caps still bound). What was lost is the **one top-up** the literal-correctness
lens can earn by naming the file it wants and why — the thing it is supposed to have when a human is
sitting in front of the review. **The ticket's second acceptance item is answered by measurement:
`/smh-code-review` carried the identical omission**, so it got the identical fix.

### A1 + A2 — the rows exist, in the callers' own invocation tables

`.agents/commands/cicd-code-review.md:50` and `.agents/commands/smh-code-review.md:137`. Each row
**names** the budget and deliberately does **not** restate the caps — step-01 owns those numbers,
because a cap each caller repeats is a cap that drifts.

### A3 — the guard reads the CALLERS' bodies, not step-01's claim about them

`test_review_engine.py`: `CALLER_FILES` grows from one entry to three; two `CHECKS` tuples key to
`.agents/commands/cicd-code-review.md` and `.agents/commands/smh-code-review.md`.

This is SCC-126's finding **F7** applied to its own follow-on: a rule about a caller that lives only
in the callee's file is a rule nothing enforces — reverting the caller left all 440 cases green while
the wiring was gone. Every pre-existing `lens_budget` check in this file asserts step-01's *text*.
Those still pass when a caller silently drops its budget, which is exactly how this defect survived.

The counter-example for each new check is **`capped`**, not a nonsense string. `capped` is the exact
value these two silently inherited, and a row that says `capped` reads as deliberate — so the check
has to **reject** it, not merely notice an absent word.

**RED** (`red-01-guard.txt`, bare, `EXIT=1`) — and it is an assertion failure, not a setup death; it
names the missing row per caller:

```
-- 749/755 passed --
[FAIL] interactive caller /cicd-code-review: invocation table passes lens_budget standard
[FAIL]   ^ counter-example applies: .agents/commands/cicd-code-review.md: '| `lens_budget` | `standard`' not present, so the proof would be vacuous
[FAIL]   ^ counter-example is rejected: check survives its own counter-example — it cannot fail on content
[FAIL] interactive caller /smh-code-review: invocation table passes lens_budget standard
[FAIL]   ^ counter-example applies: .agents/commands/smh-code-review.md: '| `lens_budget` | `standard`' not present, so the proof would be vacuous
```

**GREEN** (`green-01-guard.txt`, bare, `EXIT=0`): `-- 755/755 passed --`.

### A4 — the guard fails when the budget line is removed — and the first proof of that was INVALID

⛔ **This is the finding this lane produced against itself, and it is worth more than the fix.**

The first removal sweep ran while the fix was **still uncommitted**. The restore step was
`git checkout -- <file>`, which restores from `HEAD` — and `HEAD` did not yet contain the row. So
`git checkout` reverted **the fix**, not the mutation. The consequences, visible in the recorded
output:

- the second caller's red **also carried the first caller's failure**, because the first caller was
  never actually restored;
- the closing "both restored — guard must be green again" run came back **red**, asserting the
  opposite of what the line above it claimed;
- the working tree was left with **both rows silently gone**, which `grep -c` confirmed.

Had the sweep stopped after the first mutant — the common shape — it would have read as a clean
kill, and the fix would have been quietly absent from the commit. **A restore that restores the wrong
thing is indistinguishable from a passing proof** unless the sweep also re-asserts green at the end,
which is precisely why `RESTORE` is one of the four named techniques in `tests-must-gate-for-real.md`
§ Mutation Testing (SCC-145, landed on `main` two commits before this lane started).

Re-run against the **committed** fix (`4319722`), so restore returns to the fixed state
(`red-02-removal-proof.txt`) — each mutant killed **independently**, each restore verified green
before the next mutant is applied:

```
=== MUTANT: delete the lens_budget row from .agents/commands/cicd-code-review.md ===
dropped 1 line(s) -- mutation applied
guard EXIT=1  (1 = KILLED)          -- 752/755 passed --
[FAIL] interactive caller /cicd-code-review: invocation table passes lens_budget standard
RESTORED -> guard EXIT=0  -- 755/755 passed --

=== MUTANT: delete the lens_budget row from .agents/commands/smh-code-review.md ===
dropped 1 line(s) -- mutation applied
guard EXIT=1  (1 = KILLED)          -- 752/755 passed --
[FAIL] interactive caller /smh-code-review: invocation table passes lens_budget standard
RESTORED -> guard EXIT=0  -- 755/755 passed --
```

Each mutant asserts that the mutation actually applied (`dropped 1 line(s)`, and the script raises if
the count is anything but 1) — SCC-129's lesson that a mutant declared but never seeded scores a
green self-proof.

**INVERT sweep** (`red-03-invert-proof.txt`), the code-derived mutant the ticket did not name: flip
the **value** rather than delete the row. This is the realistic drift — a later editor sets `capped`
deliberately and the row still reads as configured. Both killed, both restored green:

```
=== MUTANT: standard -> capped in .agents/commands/cicd-code-review.md ===
guard EXIT=1  (1 = KILLED)   -- 752/755 passed --   RESTORED -> EXIT=0  755/755
=== MUTANT: standard -> capped in .agents/commands/smh-code-review.md ===
guard EXIT=1  (1 = KILLED)   -- 752/755 passed --   RESTORED -> EXIT=0  755/755
```

**4 mutants declared, 4 killed, 0 survivors, tree clean after each.**

### A5 — no drift left behind, and two gates fired on this work

**The AP twin.** `cicd-code-review-AP.md`'s divergence note read *"the primary passes none and takes
the `capped` default … raised as a follow-on against /cicd-code-review, not patched from inside its
twin."* **This ticket IS that follow-on**, so patching only its first line would have left a live
pointer to work that was now done. Bullet 1 was rewritten whole. "THREE divergences remain" stays
true — the **values** still diverge, which is the point.

**The SCC-82 stamp gate then refused the commit's successor, correctly.** `workflow_lint` reported:

```
[FAIL] SCC-82 G the live repo's AP twins report nothing:
  ['cicd-code-review-AP.md: ap_reconciled names fb3a9ba, but cicd-code-review.md is now at 4319722 - diff the twin and restamp']
```

That stamp is an auditable claim — *"I read the primary at this sha and there is nothing to port"* —
and it is deliberately not a mute switch. So the diff was actually taken
(`git diff fb3a9ba..HEAD -- .agents/commands/cicd-code-review.md`): **one hunk**, the new
`lens_budget` row. Nothing to port, because the twin already names `capped` in its own contract
block. Restamped to `43197223063bc249e6994694530b46b76dbd5c9b` **with that reasoning written into
the comment above it**, per the linter's own "every stamped twin records WHY" check.

**The doors.** `.opencode/commands/` copies are full bodies and were regenerated by `sync-agents`
(both carry the row — verified by `grep -c`). The `.agents/workflows/` Antigravity mirrors are
**thin launchers by design** (the 12k-char cap) and carry no table rows at all — verified, not
assumed: `grep -c review_mode` returns 0 there too, so this is the shape of every mirror, not a gap
in this one.

**The artifacts ledger.** `check_maps` failed with `_artifacts/_main/INDEX.md: missing row for
2026-08-14_scc-147-lens-budget/` — added.

### Gate at the landing sha

Filled in below, every command run **bare** (a piped gate reports the pipe's exit code, not the
gate's — and `${PIPESTATUS[0]}` is bash-only, which bit this session once already in `zsh`).

## Your Actions

- Review and close out with `/smh-close-task-merge-tree` — invoking it is the merge sign-off.
- **Nothing is owed to the SOP.** `workflows_testing_SOP.md:1689` already stated the intended split
  ("Typed by hand it runs `standard`"); this lane made the commands match the page, so the commit
  carries `[sop-ok]` with that justification in the log rather than a no-op doc edit.
