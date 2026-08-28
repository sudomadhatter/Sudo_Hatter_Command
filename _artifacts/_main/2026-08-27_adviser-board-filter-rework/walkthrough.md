# Walkthrough — Adviser Board filter rework (SCC-340)

<!-- twin-law: review-runtime-probe -->
review-runtime: inline (no subagent tool)

**Ticket:** [SCC-340](https://sudo-command.atlassian.net/browse/SCC-340) — Rework /smh-adviser-board to
one-filter-one-mind board rounds · **Subtasks (riders):** SCC-341 (a) · SCC-342 (b) · SCC-343 (c) ·
SCC-344 (d) · SCC-345 (e) — all worked in this lane per `work-consolidation.md` rule 2 (one repo, one
lane class; none earned its own branch).
**Branch:** `chore/SCC-340-adviser-board-filter-rework` off `origin/main` · **Plan:**
[implementation_plan.md](implementation_plan.md) · **Self-audit:** [self-audit.md](self-audit.md) (GO)

## Task Checklist

- [x] Read `/smh-quick-dev` command + approved plan + self-audit + floor/protocol rules
- [x] Mint SCC-340 + five Subtasks SCC-341..345 (a–e) as riders (operator asked for subtasks explicitly)
- [x] Worktree `chore/SCC-340-adviser-board-filter-rework` off `origin/main`; assets linked; SCC-340 → In Progress
- [x] RED first — `verify_board_filter.sh` written and run before any source edit: exit 1, ~90
      retired-vocabulary hits + 9 caucus-sense `floor` hits over the three surfaces (real source, real
      assertions — the gate failed on the actual retired model text)
- [x] Build per the Declared Change Set — all 15 rows landed; `minds/` untouched; no memory files edited
  - Finding: three self-referential negations of the retired model survived the first pass ("no hidden
    caucus", "no triads, no teams") — reworded to eliminate the terms entirely rather than allowlisting,
    so the grep gate needs no exception list.
  - Build decision: with Steps 3 and 7 deleted, the remaining steps were renumbered 0–6 (Round-0 cast
    menu is Step 2, board rounds Step 3, render Step 4, traffic Step 5, close Step 6). The plan keyed
    sections by their current names for identification; renumbering is the mechanical consequence of the
    two deletions, not a design change.
- [x] Door sync — `sync-agents.ps1 -NoGlobals` in the worktree; `.agents/skills/` master + `.claude/skills/`
      + `.opencode/commands/` regenerated; AG launcher (hand-authored, F6) body rewritten by hand in the
      same pass
- [x] GREEN — all five assertions pass, exit 0 (evidence below)
- [x] Commit `ebe7966` (explicit paths, ticket key in subject; SOP + changelog in the same commit per F3 —
      the armed `sop_currency.py` gate satisfied by update, not `[sop-ok]`)
- [x] Enforcement suite — first receipt run RED on one real finding (below); fixed; re-stamped GREEN
- [ ] Review gate — `/smh-code-review` is the operator's next step; nothing merged, nothing closed

### Suite finding that fought back

First `run_all` receipt (84.9s @ `ebe7966`): **FAIL — `_artifacts/_main/INDEX.md: missing row for
2026-08-27_adviser-board-filter-rework/`**. The artifacts-index test demands every folder under
`_artifacts/_main/` carry an INDEX row; this lane created the folder. Fixed by adding the row (with this
walkthrough linked), committed, suite re-stamped.

## Evidence

Instrument: [verify_board_filter.sh](verify_board_filter.sh) — vocabulary grep gate (plan §8.2 / row c),
floor adjudication, door parity (row d). Mutation sweep: N/A — no script or gate code changed; the
assertions are grep/cmp instruments over markdown, and the enforcement suite owns the machine floor.

**RED (before any source edit, worktree @ `007efd1`):** exit 1 —
`FAIL(vocab)` × ~90 across `.agents/commands/smh-adviser-board.md`, `adviser-board/{TEAMS,CARD,SPAWNS,ROSTER,DOCTRINE,THIRD-SIDE}.md`,
`.agents/workflows/smh-adviser-board.md` (default triads, caucus clause, stage rooms/change, three minds,
team vocabulary — all real source text) · `FAIL(floor)` × 9 (caucus-log senses in CARD/SPAWNS) ·
`PASS(door)` × 3 (doors still matched the unmodified brain — regression guards, expected green pre-edit).

**GREEN (after build + sync, worktree @ `ebe7966`):**

```
PASS(vocab): zero unjustified retired-vocabulary hits
PASS(floor): no caucus-log sense of 'floor'
PASS(door): opencode mirror byte-identical to brain
PASS(door): claude skill description matches brain description
PASS(door): AG launcher description 127 chars (budget 135)
verify-exit=0
```

**Enforcement suite (receipt [gates/suite.json](gates/suite.json)):** first run FAIL (INDEX row, above);
re-stamped **GREEN** on the fixed tree — includes `workflow_lint.py --toolkit-only` and `sop_currency.py`.

**Acceptance rows:**

- **(c) vocabulary grep gate** — GREEN above (machine-proven).
- **(d) door parity** — GREEN above (machine-proven).
- **(e) enforcement suite** — GREEN receipt (machine-proven).
- **(a) Round-0 cast menu** and **(b) four visible rounds** — these are live board sessions the chair
  flies; the command text that implements them is landed and grep-clean, but only a human can drive the
  dry-run/full session. Owed below.

## Code Review

Pending — `/smh-code-review` runs at the operator's word (review gate STOP; this lane does not invoke it
itself per the operator's directive).

## Your Actions

Everything the lane could prove by machine is proven above. Two acceptance rows need the chair's own
hands on the board:

- [ ] (a) Dry-run `/smh-adviser-board <topic>` on a real topic and confirm the Round-0 cast menu renders
  the top-3 mind picks per seated filter (one line each on the angle on THIS topic) with cut lines for
  refused filters, and that your picks seat exactly one mind per filter.
- [ ] (b) Run a full session and confirm R1 READ / R2 ATTACK / R3 BALCONY / R4 SETTLE render with one
  verbatim statement per filter (~250-word ceiling), the ⚖ line, ≤2 questions, and no hidden caucus
  spawns.

Then review and close out with `/smh-close-task-merge-tree` when satisfied.
