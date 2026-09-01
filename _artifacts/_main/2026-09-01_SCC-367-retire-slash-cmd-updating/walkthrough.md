# SCC-367 — Retire `/smh-slash-command-updating` into `/smh-sync-agents`

**Lane:** `chore/SCC-367-retire-slash-cmd-updating` · **Merged base:** `origin/main` @ `645ea5e7`
**Ticket:** [SCC-367](https://sudo-command.atlassian.net/browse/SCC-367)
**Plan:** [implementation_plan.md](implementation_plan.md) (carries the Self-Audit, verdict GO)

review-runtime: fan-out

## What shipped

`/smh-slash-command-updating` is retired. It was a **self-described thin alias**: its entire body was
`sync-agents.ps1 -GlobalsOnly`, and its own closing bullet told the operator to prefer plain
`/smh-sync-agents`, which runs that pass *and* the local doors. A command whose documentation ends by
recommending a different command was costing six generated door files, three INDEX rows, an SOP menu
row, a `NOT_PAIRED` decision row and a comment in the sync engine.

**Retiring one command in this repo is a six-file job**, and that is the part nothing was checking:
the master plus five generated doors (`.agents/commands`, `.agents/workflows`, `.agents/skills`,
`.claude/skills`, `.opencode/commands`, `.roo/commands`), plus a scatter of live references. The sync
manifest can only purge the two surfaces it recorded, so the remainder was hand work.

**The one non-redundant thing the alias held moved rather than died.** It was the only door explaining
the **SCC-332 law**: the two machine-global caches read from *different* sources, because Antigravity
**truncates** any workflow over 12,000 chars instead of rejecting it — so it must receive thin
launchers from `.agents/workflows/` while opencode takes full bodies from `.agents/commands/`. That is
now a `-GlobalsOnly` section of `/smh-sync-agents`, pinned by assertion so a future "simplify" edit
cannot quietly drop the reason and leave a bare source list.

## Assertions — both seen RED before green

| Assertion | Baseline | After the change | Proof it has teeth |
|---|---|---|---|
| `CS-22` (`test_command_surfaces.py`) — no door survives, no live file names it, the doc graph carries no node, and `/smh-sync-agents` carries the ported law | **RED 1/5** | **GREEN 10/10** (with controls) | A listed all 6 doors; B listed 15 live files and shrank to 0 as each was cleaned |
| `A0c` (`test_twin_parity.py`) — every `NOT_PAIRED` row names a command that still exists | **GREEN**, measured at 35 keys / 0 missing | **GREEN** | went **RED** on the delete (`['smh-slash-command-updating.md']`), green again on the cleanup — a real mutation, not a claim |

⛔ **The pre-mortem was already written down in this repo, and it shaped the assertion.** `CS-18`'s own
L/M commentary records that `$IsLobby` is false in a worktree, so a lane's sync leaves mirrors and
machine caches untouched *while every source-side check stays green*. A `CS-22` that scanned only
`.agents/commands/` would have gone green the instant the master was deleted, with two full-body
mirrors of `/smh-sync-agents` still naming the dead command. So it scans **all six door surfaces plus
the live doc set**. It caught `.opencode/commands/smh-sync-agents.md` exactly as predicted.

⭐ **The guard has a line-scoped history hatch, and that is a design decision, not a loophole.** Two
sites legitimately name the retired command: the `commands/INDEX.md` rename ledger, and the SCC-56
filter passage. A guard with no hatch would have pressured the next agent into **deleting the record
of why the rename happened**. So a line may name a retired command if that same line also marks it
retired (the word `retired`, or the retiring ticket key). Two controls prove the hatch cannot excuse a
live menu row.

## What the pre-work audit caught

Three misses, all one shape: **the file being edited has five generated copies of itself.** Two carry
full bodies and named the retired command; a generated `docs/doc-graph.json` held 25+ entries pointing
at files about to be deleted. All three were absent from the first Declared Change Set and would have
surfaced as undeclared drift at review. The audit also failed its own Scope Ledger precondition — the
ticket had been minted with a placeholder description and no acceptance rows — which was closed during
the audit rather than logged back to the operator.

## Fixed in the lane, not billed

`_artifacts/_main/INDEX.md` carried an **orphaned merge-conflict marker** (`||||||| 85cf2499`, line 8)
committed on `origin/main`, with no matching `<<<<<<<` or `>>>>>>>`. Found while adding this lane's
own INDEX row to that same file; removed here.

## Out of scope — named, not silently dropped

`Projects/sudo-command-center` carries a copy of seven of these files, which fires `port-checklist.md`.
Measured rather than assumed: **5 commits, unrelated git history** (no shared ancestor with the lobby),
already **326 lines** apart on `sync-agents.ps1` and **730** on the SOP, last touched 2026-08-24, not
in `maintained-projects.txt`. It is a separate published skeleton product with its own GitHub remote,
not a mirror. Aligning it is its own ticket in its own key space.

## Evidence

- Enforcement suite, run bare (a pipe hides the exit code): **68/68 files, exit 0** — re-run on the
  merged tree at `b7878074` after absorbing `origin/main` @ `645ea5e7`.
- Blast radius re-derived at review: 3 files landed on `main` while this was built, all
  `_artifacts/_memory/*`, **zero overlap**, `merge-tree` clean, no sibling lanes live.
- `declared_change_set.py parse`: **21 entries, 0 incomplete**, and zero files in the diff undeclared.

---

## Code Review (2026-09-01)

review-runtime: fan-out
lens_isolation: worktree — four repo-reading lenses each got their own `git worktree --detach` copy of the LOBBY at the sha under review, keyed `lens-SCC-367-*` per SCC-313; the Blind Hunter got no tree, only the diff text. Each tree's `git rev-parse --show-toplevel` was probed and named itself.

lenses_run:
- Blind Hunter · ok
- Edge Case Hunter · ok
- Literal-Correctness Hunter · ok
- Acceptance Auditor · ok
- Test-Adequacy Auditor · ok

lenses_counted: 5/5
lenses_na: none

### Step 0.7 — blast radius re-derived against CURRENT `main`

- **What moved:** `origin/main` advanced `1adaffae → 645ea5e7` while this lane was built — three
  files, all `_artifacts/_memory/*` (`MEMORY.md`, `cheap-models-rationalize-past-prose.md`,
  `nag-the-agent-dont-rewrite-the-rule.md`), landed by the SCC-186 standing-push lane.
- **What it changes here: nothing.** The true overlap with this lane's 25 files is **empty**
  (`grep -Fxf` returned no rows), this diff neither reads nor names any memory file, and
  `git merge-tree --write-tree` produced a clean tree with no conflict messages. `git worktree list`
  shows no sibling lane live, so there is no landing-order dependency to order.
- **What was re-measured after absorbing it:** `main` was merged in at `b7878074` and the **whole**
  floor re-run on the merged tree, not the pre-merge one — suite 68/68 exit 0, `check_links` clean,
  `workflow_lint` 0/0, `sop_currency` 0, plus `CS-22` and `A0c` re-run by name. The receipt behind
  the verdict is stamped at `60ac25af`, later than the absorb, on a clean tree.

### The tail, in one line (operator ruling 2026-08-17)

**37 raw findings came back across five lenses. They dedupe to 23 distinct anchors: 18 were assessed
real and fixed in this lane, 1 became a required close-out step, 1 was a misreading worth clarifying,
1 is raised as its own ticket, and 2 were dismissed** — one measured false, one provably wrong.
(An earlier draft of this line said "31 / 14"; that was an eyeball count made before the last two
lenses landed, and it undercounted. The numbers here are counted from the five reports.)

drift: undeclared=0 · unimplemented=0 · incomplete=0 — reconciled, not clean on the first pass: `test_sops_prds_folder.py` arrived UNDECLARED during review (the SOP edit tripped its T4, so the retired name needed a `DISCUSSED_AS_RETIRED` entry) and was added to the Declared Change Set rather than left to surface at the gate. Three artifact paths — `task.yaml`, `gates/suite.json`, `preflight-receipt.json` — are close-out products the ceremony writes after the plan, and the parser exempts them.

dispositions: per-lens: blind-hunter=5/3/0 · edge-case-hunter=6/0/0 · literal-correctness=8/0/0 · acceptance-auditor=5/1/0 · test-adequacy=8/1/0

**The retirement itself drew no findings from any lens.** The Acceptance Auditor diffed the deleted master against the ported `-GlobalsOnly` section clause by clause and reported all eleven substantive elements surviving, the port *richer* than the original; `declared_change_set.py diff` returned zero drift across every path. Every real finding was in the **guard I wrote**, not in the work it guards.

### The two whose ASSESSMENT disagreed with their label — the calibration signal

- **Blind Hunter #1, labelled `important`, DISMISSED.** It argued the ported section pushed the Antigravity door toward the 12,000-char truncation cap. Measured: **10,247 of 12,000**, `CS-18 B` green across all 40 doors, and the engine auto-emits a thin launcher above 11,500 bytes — two independent mechanisms. The lens is starved of repo access by design and could see neither. Its own decisive check (`wc -c`) was the right one and it named it; the answer was simply "under".
- **Blind Hunter #6, labelled `suggestion`, DISMISSED as WRONG.** It claimed `A0c` closes the fossil hole for `NOT_PAIRED` while leaving `PAIRS` exposed. `A0` at `test_twin_parity.py:314` already guards `PAIRS` by the identical mechanism. Same starvation cause.
- **Edge Case Hunter #6, labelled `nitpick`, dismissed as a MISREADING but acted on anyway.** It read the `A0c` comment's "35 keys" as describing HEAD (34). The sentence was accurate — 35 keys all resolving on `origin/main`, before the delete — but it misread cleanly enough to be worth disambiguating, so the comment now names both counts in order.

### What was fixed — every one reproduced red first

**The controls were theatre.** Three CONTROL rows could not fail for any input: `"-GlobalsOnly" not in sync_cmd.replace("-GlobalsOnly", "")` is `True` by the semantics of `str.replace`, independent of the file. Two lenses reproduced it on five inputs including the empty string. Worse, the controls exercised **re-typed copies** of the predicates rather than the predicates themselves — the Edge Case Hunter deleted the cap clause from E's live expression, put the tree in the exact SCC-332 state E exists to refuse, and watched E *and both its controls* pass. Fixed: one `law_stated()` and one `names_it_unexcused()`, called by the assertion and by its controls.

**The history hatch excused live doors.** Keyed on the word `retired`, which is ambient prose here — `/smh-sync-agents` itself says "both are retired and fail loudly". Re-keyed to the retiring **ticket**, then narrowed again when a reviewer laundered a routing row through a second table cell: **a `|`-delimited row is now never excused, on structure alone**, whatever words it carries. History ledgers are prose; menus are rows. Two controls pin both directions.

**The scan was blind to the repo's brain.** `LIVE_DIRS` held five directories and no root files, so `AGENTS.md` — which `CLAUDE.md` names the single source of truth — was never opened, nor `.claude/rules/` or `_bmad/`. Reproduced: a live routing row in `AGENTS.md` plus a live reference in `.claude/rules/` left the whole suite at 68/68. Now scans the full live surface plus root `*.md`: **1,735 files**, asserted non-vacuous by `CS-22 B0`.

**Two things I had written that were simply false.** The block's rationale claimed `$IsLobby` is false in a worktree; it is **true** — `$HomeRoot` derives from `$PSScriptRoot` and `$Target` defaults to it, and this lane's own sync had printed `lobby=True` in front of me. Rationale restated from the engine's source, and the real reason named instead: `.opencode/` and `.roo/` hold full bodies, so a retired command can hide in a *different* command's prose. And I had **truncated a historical line** to satisfy my own guard, contradicting `sync-agents.ps1:496` — the exact sin the guard's comment says it exists to prevent. The fourth name is restored, marked with its ticket.

**The bookkeeping error that mattered most.** I renamed the guard `CS-19` → `CS-22` and left ten references behind in the plan and ticket. `CS-19` is a real, passing, unrelated block (SCC-357): `--case CS-19` returns **8/8 green** about PRD reconciliation. Anyone verifying acceptance rows A and B by running what they named would have been handed a pass by the wrong assertion. Corrected in both, and the live ticket re-rendered.

**Anti-vacuity, three registries.** `CS-22 C` passed with `doc-graph.json` moved out of the tree; `CS-22 B` could pass having read zero bytes; `RULE_SITES` — a tuple **this diff edits** — silently dropped members pointing at deleted files, so the diff's own edit to it was unenforced. All three now assert their inputs exist. `CS-18 J0` is the new one, and it is the third registry of a class this lane had already guarded twice (`A0`, `A0c`).

**Mutation evidence — five mutants that previously survived, all now killed:** a routing row in `AGENTS.md`; a reference in `.claude/rules/code-standards.md`; a table row laundered by a stray `retired` cell; a partial-delete skills *directory* holding only `notes.txt`; and a fossil path restored to `RULE_SITES`.

### Evidence @ `b7878074`

| Gate | Result |
|---|---|
| `run_all.py` (bare) | **68/68 files, exit 0** |
| `workflow_lint.py --toolkit-only` (bare) | **0 errors, 0 warnings**, exit 0 |
| `check_links.py --base origin/main` (bare) | **clean**, exit 0 |
| `sop_currency.py` over the real path set | exit 0 |
| `CS-22` (assertion evidence) | **15/15**, exit 0 — from 1/5 red at the start |
| `A0c` (assertion evidence) | green, exit 0 — green → red on delete → green on cleanup |
| Blast radius re-derived | 3 files landed on `main` (`_artifacts/_memory/*`), **zero overlap**, merge-tree clean, no sibling lanes |

### ⛔ Required close-out step — the lane cannot do it itself

Both machine-global caches still hold the retired command, and each holds a **pre-port** copy of `/smh-sync-agents`:

```
~/.gemini/antigravity/global_workflows/smh-slash-command-updating.md   (2061 bytes)
~/.config/opencode/commands/smh-slash-command-updating.md              (2134 bytes)
```

They live outside the repo, so no repo-scoped assertion can see or purge them and no worktree sync writes them. **After this lands, run `/smh-sync-agents` from the lobby checkout** — its mirror-exact purge clears both.

### Fixed at the close-out gate, not deferred

`check_maps.py --depth3-only --strict` — one of the three gates the preflight selected — went red on
a **missing `_artifacts/_main/workflow-events/INDEX.md`**. Not this lane's doing: `2026-09/` opened
when SCC-365's close-out landed on `main` earlier the same day, tipping that bucket to two
date-prefixed folders and firing the depth-3 INDEX requirement. It had been reported at every session
start since, and it blocked the next close-out to run — which was this one. Written here rather than
deferred, because a missing index is not something a later lane inherits more cheaply. The file
documents what the bucket actually is (one JSON per ceremony event, not one folder per session) and
says explicitly that month buckets are the unit, so nobody later builds a 41-row table.

### Raised once, with the remedy, and deliberately NOT built here

- **Make the Antigravity launcher universal.** The 11,500-byte threshold leaves 15 of 39 doors as full bodies still living under the cap, which is why this keeps resurfacing. Dropping the threshold to 0 **deletes** the `else` branch (~14 lines) and makes the cap structurally unreachable rather than measured-safe. Its own ticket.
- **A conflict-marker guard.** `_artifacts/_main/INDEX.md:8` carried `||||||| 85cf2499` on `origin/main`; this lane removed it, but nothing prevents the next one. Remedy: a suite row rejecting any tracked line matching `^(<{7}|\|{7}|>{7})\s` outside the two docs that teach the markers. Its own ticket — repo hygiene is a different subject from command retirement.

### The commit gates refused this review twice, and both refusals were correct

- **`sop_currency`** rejected it: `/smh-sync-agents` changed and the page documenting it had not.
  The honest fix was not `[sop-ok]` — the SOP genuinely needed to say this command now owns the
  globals-only pass, carries the SCC-332 law, and **must be run from the lobby checkout**, since a
  worktree sync never writes the machine caches. That close-out step now lives on the page the
  operator actually reads, instead of only in this walkthrough.
- **`verdict-receipt` (SCC-363)** rejected it: a `Verdict:` stamp with no suite receipt behind it.
  It refused, and **the receipt then caught a real regression** — the SOP edit had broken
  `test_sops_prds_folder.py` T4 (*"every command reference resolves"*), a fourth independent guard
  that fires when a doc names a `/command` with no master. The suite was **67/68 at the moment the
  PASS was written.** Fixed properly via that check's own `DISCUSSED_AS_RETIRED` exemption — which
  exists precisely so a doc whose subject IS a retirement may name it — with the reason recorded
  beside the entry. There is deliberately no `--result` flag on `gate_receipt.py`; the result comes
  from a real exit code, and that is the only reason this was caught rather than asserted.
- ⭐ **The two new guards then collided, which is the design working.** The `DISCUSSED_AS_RETIRED`
  entry is a line in `.agents/`, so `CS-22 B` flagged it — correctly, since the marker sat in the
  comment above rather than on the line. Resolved by putting the marker on the entry line, which is
  what a line-scoped hatch is for. Both green together.

**Receipt:** `gates/suite.json` — `result: pass`, `exit_code: 0`, `dirty_tree: false`,
**68/68 files** in 103.2 s at `60ac25af`. Stamped by `gate_receipt.py`, which has no
`--result` flag: the outcome comes from a real exit code or it does not exist.

Verdict: PASS @ 60ac25af

## Your Actions

⛔ **One item, and it is the only thing this lane could not do for itself.**

- [ ] **Run `/smh-sync-agents` from the lobby checkout** (not a worktree) once this lands. Both
      machine-global caches still hold `smh-slash-command-updating.md`, and each holds a **pre-port**
      copy of `/smh-sync-agents`. They live outside the repo, so no repo-scoped assertion can see or
      purge them and no worktree sync writes them. The sync's mirror-exact purge clears both.
      Verify with: `ls ~/.gemini/antigravity/global_workflows/smh-slash-command-updating.md
      ~/.config/opencode/commands/smh-slash-command-updating.md` → both absent.

**Not actions — DECISIONS, held open deliberately, nothing minted without the operator's word:**

- **Make the Antigravity launcher universal.** The 11,500-byte threshold leaves **15 of 39** doors as
  full bodies still living under the 12,000-char cap, which is why this topic has now cost thinking
  time in three tickets. Dropping the threshold to 0 **deletes** the mirror function's `else` branch
  (~14 lines) and makes the cap structurally unreachable rather than measured-safe. One number, and
  `CS-18 B` retires with it.
- **A conflict-marker guard.** `_artifacts/_main/INDEX.md:8` carried `||||||| 85cf2499` on
  `origin/main`; this lane removed it, but nothing stops the next one. Remedy: a suite row rejecting
  any tracked line matching `^(<{7}|\|{7}|>{7})\s` outside the two docs that teach the markers.
