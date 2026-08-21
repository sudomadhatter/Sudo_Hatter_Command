---
IsArtifact: true
ArtifactMetadata:
  title: SCC-201 cycle 3 — the board-machinery bug list
  type: implementation_plan
  date: 2026-08-20
---

# SCC-201 cycle 3 — three subtasks, one lane: the readers and gates that half-fire silently

**Lane:** `chore/SCC-201-bugs-updates-cycle-3` (worktree `.claude/worktrees/SCC-201-bugs-updates-cycle-3`, cut from `origin/main` @ `db253fc`)
**Ticket:** SCC-201, the rolling "Bugs and Updates" ticket, run as ONE consolidated lane.
**Riders:** SCC-242 · SCC-206 · SCC-243 — all three close with the parent. Cycle 4 (SCC-244) already holds the `running-bug-list` baton.

review-runtime: fan-out

## Goal

Four defects, three files, one theme: **a mechanism runs half of itself and reports success.**
`finish` cannot answer for a story lane and says nothing about why. `open_actions` folds a ticked
item's prose into the open box above it and posts the result to the board as owed work.
`lane_qualify` returns two verdicts its own callers have no instruction for. And `roll_the_cycle`
clones the next rolling ticket, then leaves three edits nobody is told about.

Every one is in the machinery that writes to the board or the artifacts. None is cosmetic.

## Measured — re-grepped in THIS tree at `db253fc`, not copied from the tickets

| What | Where |
|---|---|
| the hardcoded landing target | `jira_feed.py:1789-1790` — `fetch origin main`, then `merge-base --is-ancestor tip origin/main` |
| `MERGE_DOORS` | `:1666` — `("/smh-close-task-merge-tree", "/cicd-push-e2e")`. **`/cicd-close-story-merge-tree` is absent** |
| `merge_row_state` / `is_merge_row` / `lane_tip` | `:1754` / `:1683` / `:1713` |
| the story door's ban on `finish` | `cicd-close-story-merge-tree.md:320-324`, plus `:159-164` which asserts no second refusal fires on that lane |
| `open_actions` / `_collect` | `:1594` / `:1621`; the unowned fold is `:1641` — `items[-1] += " " + s` |
| `cmd_index_row` | `:2481` |
| `roll_the_cycle` | `:1313`; the verbatim-copy ruling and its backtick reason at `:1364-1370` |
| `lane_qualify` verdicts | `lane_qualify.py:83` — **five**: `LIGHT`(0) `LIGHT-VCS`(0) `TASK`(1) `HANDOFF`(2) `NOT-COMMAND-CENTRE`(3) |
| the two verdict tables | `cicd-non-crit-pr-push.md:41-43` and `smh-non-crit-pr-push.md:31-33` — **three rows each.** `LIGHT-VCS` and `NOT-COMMAND-CENTRE` are missing from BOTH |

⚠️ **AUDIT FINDING (Lens 1, anchored `lane_qualify.py:107-112` + `.agents/scripts/INDEX.md:57`).**
`NOT-COMMAND-CENTRE` is **not a gap** — it is a settled operator scope ruling, and teaching the
qualifier a project arm re-litigates it. ⛔ **`lane_qualify.py` is NOT edited by this lane.**
The reframe: the verdict's own reason is *"Product work uses the cicd-\* lanes"*, and
`/cicd-non-crit-pr-push` **IS** a cicd-\* lane — so that verdict is its EXPECTED answer, not a
refusal. The defect is entirely that its table never says so, and that neither table lists
`LIGHT-VCS`. Rows M–R were rewritten on that basis.

⭐ **Two corrections to the tickets as filed, from this measurement.** SCC-243 says one verdict is
unlisted; it is **two**, and on **both** twins. And SCC-242's DO 8 must not ask for the clone to be
rewritten — `:1364-1370` records a deliberate ruling that summary and description are copied
verbatim *because building a `--description` is how backticks execute*. The fix is the missing
`say()`, never the copy.

## Acceptance → the assertion that proves it (RED first, every row)

| # | Acceptance | Assertion — must fail first | Rider |
|---|---|---|---|
| A | a tip that is an ancestor of a NON-main ref reads as merged | `merge_row_state(wt, landing_ref="origin/epic/SCC-33-x")` → satisfied | SCC-242 |
| B | **control** — the default is byte-identical to today | no flag, no manifest key → compares against `origin/main`; every existing case stays green | SCC-242 |
| C | an unresolvable landing ref HOLDS | a ref git cannot resolve → `satisfied: False`, and the reason NAMES the ref. Fails closed, never open | SCC-242 |
| D | a story merge row is recognised as one | `is_merge_row("… /cicd-close-story-merge-tree")` → True. **This is why the ref fix alone would ship a no-op** | SCC-242 |
| E | the message names the ref it used | the `why` string carries the resolved ref, not a hardcoded `origin/main` | SCC-242 |
| F | the story door instructs `finish`, and its own text agrees | `cicd-close-story-merge-tree.md` calls `finish --landing-ref "$EPIC"`, and `:159-164` no longer claims no second refusal fires | SCC-242 |
| G | `index-row` leaves a TRUE index | first append replaces the `(empty …)` placeholder and indents to the section; a second append keeps both rows | SCC-242 |
| H | a clone announces what it did NOT do | after `roll_the_cycle` clones, the output names the summary bump, the INDEX clear and the PREDECESSOR update as still owed | SCC-242 |
| I | a ticked item ends the continuation window | `- [ ]` + wrapped `- [x]` → the open item's text ONLY | SCC-206 |
| J | HTML comments are invisible to the reader | an indented `<!-- … -->` body folds into no item | SCC-206 |
| K | **control** — a real continuation still rides along | an indented line under a genuinely open item is still appended (guards against "fixing" this by deleting the fold) | SCC-206 |
| L | **control** — the refusal path does not shift | no unchecked items → `[]`; no section at all → `None` | SCC-206 |
| M | the cicd- command documents the verdict it will ALWAYS get | `cicd-non-crit-pr-push.md` Step 0.5 carries a `NOT-COMMAND-CENTRE` row reading *expected here — this IS a cicd-\* lane; carry on to the path check below*, quoting the ruling. Fails today: undocumented | SCC-243 |
| N | that command names what it refuses, from the authority | the body names every member of `task_preflight.PRODUCT_DIRS` (plus firestore rules and `.github/`) as disqualifying; the assertion IMPORTS `PRODUCT_DIRS` and fails if any member is unnamed. Fails today | SCC-243 |
| O | `LIGHT-VCS` is listed wherever it can be returned | both tables gain the `--no-file-changes` row. Fails today: missing from both | SCC-243 |
| P | **a table can never fall behind the script again** | a test reads `lane_qualify.VERDICTS` and the verdict rows of EVERY command that calls it, and fails when any caller's table is missing one. Today the diff is 2 on smh- and 2 on cicd- | SCC-243 |
| R | the twins' one legitimate divergence is DECLARED | the cicd- table carries a row the smh- table must not (`NOT-COMMAND-CENTRE` = expected), and the asymmetry is declared with the repo's own auditable marker — `<!-- twin-divergence: <id> — <reason> -->` in the command body (`test_twin_parity.py:55,176`), never by editing the test | SCC-243 |
| Q | every new case is mutation-proven | each case declared against a mutant it alone kills; sweep table committed | all |

**P is the row that stops recurrence.** A–O are repairs; P is what keeps them repaired.

## Declared Change Set

- EDIT `.agents/scripts/jira_feed.py` — landing ref + MERGE_DOORS + _collect ownership + HTML comments + index-row append + roll_the_cycle say() → A, B, C, D, E, G, H, I, J, K, L
- EDIT `.agents/scripts/tests/test_jira_feed.py` — new blocks for the closer, the reader, the index and the cycle → A, B, C, D, E, F, G, H, I, J, K, L, Q
- EDIT `.agents/commands/cicd-close-story-merge-tree.md` — Step 4 calls finish; the ban block and the no-second-refusal sentence are corrected → F
- EDIT `.agents/scripts/tests/test_command_surfaces.py` — CS-13's transition guard learns the second verb, and learns that a MENTION is not a call → F, Q
- EDIT `.agents/scripts/INDEX.md` — the router said `DEPLOY_DIRS` where `lane_qualify` imports `PRODUCT_DIRS`; SCC-118's trap described backwards → N
- EDIT (generated) `.agents/.sync-manifest.json` — sync output; conflicted on the SCC-240 absorb and was resolved by regenerating → M, P
- EDIT `.agents/scripts/tests/test_lane_qualify.py` — the caller/verdict parity block + the PRODUCT_DIRS naming assertion → M, N, O, P, Q
- EDIT `.agents/commands/cicd-non-crit-pr-push.md` — NOT-COMMAND-CENTRE + LIGHT-VCS rows, and the PRODUCT_DIRS refusal list → M, N, O, P, R
- EDIT `.agents/commands/smh-non-crit-pr-push.md` — LIGHT-VCS row → O, P, R
- EDIT (generated) `.opencode/commands/cicd-close-story-merge-tree.md` — sync mirror → F
- EDIT (generated) `.opencode/commands/cicd-non-crit-pr-push.md` — sync mirror → M, P
- EDIT (generated) `.opencode/commands/smh-non-crit-pr-push.md` — sync mirror → M, P
- EDIT (generated) `.agents/workflows/cicd-non-crit-pr-push.md` — sync mirror (this one EMBEDS the body) → M, P
- EDIT (generated) `.agents/workflows/smh-non-crit-pr-push.md` — sync mirror (this one EMBEDS the body) → M, P

Measured: `.opencode/commands/*` is a byte copy of the command. `.agents/workflows/*` embeds a
short body (5631 vs 5794 bytes for non-crit) but is a thin launcher for a long one (868 bytes for
the 26 KB story door), so the story door's workflow does NOT change. `SKILL.md` doors are ~1 KB
launchers and change only if frontmatter does — none here.

## Amendment 1 — discovered while building row F (2026-08-20)

⭐ **Row F could not land without a second file, and the reason is the finding itself.**
`test_command_surfaces.py`'s CS-13 C2 asserts *"the story door actually moves the Jira ticket"* by
grepping for one needle — `acli jira workitem transition`. Replacing that call with
`jira_feed.py finish --apply` (which transitions AND reads the status back, so it is strictly the
safer mechanism) turned C2 red. The guard pins the **mechanism** it was written against, not the
**behaviour** it names — the same shape as every other defect on this lane.

Widening the needle then exposed the second half: the door's own prose explains that Step 4b runs
`finish`, and that sentence lives in Step 2, **ahead of the landing push**. C3 promptly reported the
door writing `Done` before it lands — a guard inverted by the sentence describing it
(`comment-literals-invert-source-grep-tests`). The fix is that an invocation carries an argument:
`--key` is required, and required of **both** verbs, since the acli needle always had the same blind
spot. Four new cases (C2b, C6 ×2, C7 ×2) pin it, and C7 is the one the mutant kills.

⛔ **No new ticket.** This is row F's own surface, discovered by building row F, so it rides row F —
per the operator's standing ruling that discovered work folds into the lane it was found in.

## Amendment 2 — two corrections from building rows M–R (2026-08-20)

⭐ **The gap is 1 on `smh-`, 2 on `cicd-` — not 2 and 2.** Re-measured against
`lane_qualify.VERDICTS` by the row-P parser itself: `smh-quick-fix.md` already lists all five;
`smh-non-crit-pr-push.md` was missing `LIGHT-VCS` only; `cicd-non-crit-pr-push.md` was missing
`LIGHT-VCS` **and** `NOT-COMMAND-CENTRE`. The plan's *"2 on smh- and 2 on cicd-"* was wrong.
Row P's assertion is unchanged; only the expected diff is.

⛔ **Row N named the wrong authority, and the correction matters.** The plan said the body must name
`PRODUCT_DIRS` *"plus firestore rules and `.github/`"* as **disqualifying**. Measured: there is no
firestore-rules constant — `firebase/` in `PRODUCT_DIRS` already covers it — and `.github/` is
**deliberately NOT deployable** in `lane_qualify` (SCC-118: it is a `TOOLKIT_PREFIXES` member, so it
routes to `TASK`, not `HANDOFF`). What shipped names `task_preflight.PRODUCT_DIRS` + `CI_DIR` for the
command's own deployable check, imported and never re-typed.

⭐ **And the defect is bigger than SCC-243 as filed.** `NOT-COMMAND-CENTRE` is returned at
`lane_qualify.py:107-112`, **before a single path is read** — so in a child project, which is the only
place `/cicd-non-crit-pr-push` runs, `--paths backend/api.py` and `--paths docs/notes.md` return the
identical answer (measured against `Projects/AGY_AVIATIONCHAT`). Its `TASK` and `HANDOFF` rows could
never fire. Documenting the verdict alone would have left Step 0.5 qualifying **nothing**, so the
command gained the deployable-path check that actually runs there. ⛔ **`lane_qualify.py` is still not
edited** — the ruling stands; the missing work was always the caller's.

## DO NOT

- **Do not change the default landing target.** No flag and no manifest key must behave exactly as today (row B is that control).
- **Do not let an unresolvable ref pass.** A gate with a silent open arm is the empty-input-reads-as-pass shape the house bans.
- **Do not relax the roster contiguity rule or weaken any `strip_fenced`** — SCC-154 paid for those.
- **Do not fix SCC-206 by deleting the continuation fold.** `smh-quick-dev.md` publishes ride-along as a machine contract; row K is the control that catches it.
- **Do not rewrite `roll_the_cycle`'s verbatim copy.** The ruling and its reason are at `:1364-1370`. Add the `say()`, nothing else.
- **Do not touch SCC-240's surface** — `walkthrough_roster.py`, `declared_change_set.py`, `.agents/skills/code-review-engine/**`, `smh-code-review.md`, `cicd-code-review.md`. That lane is live.
- **Do not give `lane_qualify.py` a project arm.** The centre-only scope is the operator's ruling, recorded at `.agents/scripts/INDEX.md:57` and derived (not asserted) in `is_command_centre`. Quote it; do not re-open it.
- **Do not flatten the non-crit twins.** They are a declared pair (`test_twin_parity.py:95`) with ONE legitimate divergence here. Record it (row R); do not port the cicd- row into the smh- table.
- **Do not hand-edit generated surfaces.** One `/smh-sync-agents` run writes them.
- **Do not `git add -A`.** Explicit paths, verified with `git diff --cached --stat`.

## RED first

**Start with D.** `is_merge_row("The merge itself — lands via /cicd-close-story-merge-tree")` returns
False today. That single red proves the landing-ref fix alone would have shipped a no-op, which is
the finding the whole of SCC-242 turns on.

**Then P**, for the same reason at the other end: extract today's `VERDICTS` set and today's two
tables and watch the diff be non-empty, twice.

**Then I**, using SCC-206's own reproduced input shape.

⛔ Paste the actual failing output and read which line raised it. A check that dies in setup looks
identical to one that fails its assertion, and only one of those is a real failure.

⛔ Assertions must run on both machines: one has no bare `python`, the other has no `python3`.

## Sibling lanes — landing order is decided, not discovered

| Lane | Its files | Overlap with mine |
|---|---|---|
| `chore/SCC-240-self-diagnosing-readers` | `walkthrough_roster.py`, `declared_change_set.py`, both review command bodies, 3 code-review-engine files, 3 test files | **zero files** |
| `chore/SCC-235-dual-surface-blast-radius` | artifacts + `_artifacts/_memory/` only | **zero files** |

⛔ **Zero file overlap is not zero collision.** SCC-240 edits command bodies, so it runs
`/smh-sync-agents` and rewrites `.opencode/commands/` and `.agents/workflows/`. This lane rewrites
three of the same generated directories from a different base. Whichever lands second gets a red on
files neither lane hand-edited.

⛔ **SUPERSEDED — operator ruling, 2026-08-20 (later): THIS LANE LANDS FIRST.** *"I will make 240 to that since you are done first"* — SCC-201 finished first, so SCC-240 rebases onto it and absorbs the regenerated mirrors. The collision is unchanged in kind; only which lane pays it moves. Nothing in the build changes — the mirrors in this lane are `/smh-sync-agents` output from this lane's own bodies.

~~**Operator ruling (2026-08-20): SCC-240 lands FIRST.**~~ This lane then absorbs `origin/main`,
re-runs the sync, and re-gates before its own PR. That absorb happens before the review, never at
the merge.

⛔ SCC-235 has uncommitted `_artifacts/_memory/` files. They are another session's. Never staged,
swept, or committed under this lane's key.

## Risks

1. **`merge_row_state` is on the path that writes `Done` to Jira.** Row B is not optional politeness — it is the assertion that this lane cannot silently change how every existing Task lane closes.
2. **`_collect` is shared by `banned_action_rows()` and `check-actions`,** so SCC-206's blast radius is the whole `## Your Actions` machine contract, not just `finish`. The full `test_jira_feed.py` block runs, never just the new cases.
3. **`lane_qualify` gaining a project arm changes which lane child-project work routes to.** Row N is the guard: a deployable path must never come back `LIGHT`.

---

## Self-Audit (2026-08-20)

**Level: LEDGER+BLAST** — the Declared Change Set touches two scripts others import, three
command/door surfaces, and a declared twin pair. All three lenses run.

```
lens:        1 Repo Reality
checks_run:  all 12 declared paths exist on disk · every cited line number re-read and quoted
             · declared_change_set.py parse -> 12 entries, incomplete: [] · Scope Ledger (zero
             NEW ops, so the CREATES table is empty by construction) · acceptance precondition
             (SCC-242 8 rows, SCC-206 5, SCC-243 5 - all name observables) · lane fit: no
             deployable path (backend/ frontend/ firebase/ functions/ mobile/ .github/) in the set
read:        .agents/scripts/jira_feed.py:1313,1594,1621,1641,1666,1683,1713,1754,1789-1790,2481
             · .agents/scripts/lane_qualify.py:83,100-112 · .agents/commands/cicd-non-crit-pr-push.md:41-43
             · .agents/commands/smh-non-crit-pr-push.md:31-33 · .agents/scripts/INDEX.md:23,57
             · .agents/scripts/tests/test_twin_parity.py:95,125-147 · .agents/commands/INDEX.md
verdict:     findings below
```

```
lens:        2 Parity + Blast
checks_run:  five platform doors present for each of the three changed commands (15/15 ok)
             · commands/INDEX.md names all three · jira_feed.py caller in
             .agents/scripts/git-hooks/post-commit-jira-start.sh:119 · lane_qualify.py callers
             enumerated · scripts/INDEX.md rows read for both scripts · twin-pair registry read
             · risk_seam.py classify · sibling worktrees after fetch
read:        .agents/scripts/git-hooks/post-commit-jira-start.sh:119 · .agents/scripts/INDEX.md:23,57
             · .agents/scripts/tests/test_twin_parity.py:95 · git worktree list + per-tree diff
verdict:     findings below
```

```
lens:        3 Pre-Mortem
checks_run:  attached failure narratives to F1 and F2 only. Originated nothing (bounded by contract).
read:        the two findings above
verdict:     narratives attached
```

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/scripts/lane_qualify.py:107-112` | `if not is_command_centre(repo): return ("NOT-COMMAND-CENTRE", f"… this is a project repo, not the command centre. Product work uses the cicd-* lanes, however small it looks")` | **Rows M, N and O are built on a false premise.** `NOT-COMMAND-CENTRE` is not a gap in the qualifier — it is a **settled operator scope ruling**, recorded at `.agents/scripts/INDEX.md:57` as *"the operator's scope ruling was 'only for the smh / commands… not normal cicd work', and it is derived rather than asserted"*. Teaching it a project arm **re-litigates that ruling**. The real defect is one caller: `/cicd-non-crit-pr-push` calls a qualifier explicitly scoped to exclude it | **BLOCKER** |
| `.agents/scripts/tests/test_twin_parity.py:95` | `("cicd-non-crit-pr-push.md", "smh-non-crit-pr-push.md"),` | The two are a **declared pair**, which is how the centre-only call got into the cicd- body — the smh- body was ported without noticing the qualifier cannot answer for a child project. So "port the same table to both" (rows M and P as written) is **wrong**: here the twins must legitimately DIVERGE, and the divergence has to be recorded rather than flattened | important |
| `.agents/commands/cicd-non-crit-pr-push.md:41-43` and `.agents/commands/smh-non-crit-pr-push.md:31-33` | both tables list exactly `LIGHT` · `TASK` · `HANDOFF` | `LIGHT-VCS` (the `--no-file-changes` escape, `lane_qualify.py:83`) is missing from **both**. This one IS a real symmetric gap and survives F1 — it is the half of SCC-243 that stands | important |

### Observations (uncounted — no check behind them)

- `risk_seam.py classify` returns `{"status": "unclassified", "tiers": {}}`. That is the pinned placeholder behaving as contracted (`gates_audit()` False for every return), not a gap.
- `.agents/commands/INDEX.md` names `cicd-close-story-merge-tree` four times and each non-crit command once. Nothing is orphaned.

### Pre-Mortem narratives (attached, not originated)

- **F1, the silent one.** Had this shipped, `lane_qualify` would return `LIGHT` for a child project's `docs/` edit — and the next agent, reading a qualifier that now answers for projects, would route a `frontend/` change through it too. The blast radius is not this command; it is the ruling that keeps product work off the light lane.
- **F2, the sibling-lands-first one.** `test_twin_parity.py` compares the pair. Porting one table and not the other turns that test red on `main` for whichever lane lands second — and the red would name a file this lane never intended to change.

### Sibling landing-order dependency

`chore/SCC-240-self-diagnosing-readers` shares **zero files** but rewrites `.opencode/commands/`
and `.agents/workflows/` through its own `/smh-sync-agents` run, as this lane does.
**Operator ruling: SCC-240 lands first**; this lane absorbs `origin/main` and re-syncs before its
review, never at the merge. `chore/SCC-235-…` holds uncommitted `_artifacts/_memory/` files that
are another session's — never staged under this key.

```
Audit verdict: NO-GO
```

**Ground:** an anchored finding whose consequence breaks acceptance rows M, N and O.
The plan is repaired below and re-audited.

---

## Self-Audit — second pass, on the repaired plan (2026-08-20)

**Level: LEDGER+BLAST.** Re-run after the NO-GO. Only the repaired rows were re-checked; Lens 1's
path and anchor sweep and Lens 2's door/caller sweep stand from the first pass, unchanged.

```
lens:        1 Repo Reality (re-check)
checks_run:  lane_qualify.py is ABSENT from the Declared Change Set · declared_change_set.py parse
             -> 11 entries, incomplete: [] · every NEW claim in rows M-R re-read against the tree
             · Scope Ledger still empty (zero NEW ops) · lane fit unchanged: no deployable path
read:        task_preflight.py:111-113 - `PRODUCT_DIRS = ("backend/", "frontend/", "firebase/",
             "functions/", "mobile/")`, `CI_DIR = ".github/"`; imported live, both tuples printed
             · lane_qualify.py:83 - VERDICTS imported live, five keys returned
             · test_twin_parity.py:55,176 - `<!-- twin-divergence: <id> — <reason> -->`
verdict:     clean
```

```
lens:        2 Parity + Blast (re-check)
checks_run:  the row-R mechanism is the command-body marker, not a test edit — so
             test_twin_parity.py was REMOVED from the change set · the twins now diverge by one
             declared row with an auditable marker, which is the repo's own escape hatch rather
             than a new one · no script others import is edited any more except jira_feed.py,
             whose only hook caller (post-commit-jira-start.sh:119) calls `start`, a subcommand
             this lane does not change
read:        test_twin_parity.py:55 - "The escape hatch is AUDITABLE, not silent"
             · .agents/scripts/git-hooks/post-commit-jira-start.sh:119
verdict:     clean
```

```
lens:        3 Pre-Mortem (re-check)
checks_run:  the F1 narrative is now moot - the ruling is quoted in DO NOT rather than re-opened.
             The F2 narrative is answered: the twins diverge by ONE marked row, so twin parity
             reads it as declared rather than as drift. Originated nothing.
read:        the repaired rows M-R and the two new DO NOT entries
verdict:     clean
```

### What the repair changed

| Was | Is | Why |
|---|---|---|
| `lane_qualify.py` gains a project arm (M, N, O) | **not edited at all** | the centre-only scope is a settled ruling (`INDEX.md:57`), and the verdict's own reason — *"Product work uses the cicd-\* lanes"* — makes `NOT-COMMAND-CENTRE` the EXPECTED answer for a cicd-\* lane, not a refusal |
| port the same verdict table to both twins | one declared divergence + one symmetric fix | `test_twin_parity.py:95` pairs them; the cicd- body gains a row the smh- body must not, marked with `twin-divergence`. `LIGHT-VCS` is the half that IS symmetric |
| `test_twin_parity.py` edited for R | command body carries the marker | `:55` — the escape hatch is a comment in the body, auditable; editing the test would be the suppression it exists to prevent |

Declared Change Set: **11 entries, `incomplete: []`**, `lane_qualify.py` absent, five acceptance
rows (M, N, O, P, R) re-grounded in text quoted above.

### Findings

None. Every first-pass finding is either fixed in the plan or converted to a DO NOT that quotes
the ruling it protects.

### Observations (uncounted)

- `PRODUCT_DIRS` vs `DEPLOY_DIRS` is itself a shipped incident (`lane_qualify.py:65-66`, SCC-118: `DEPLOY_DIRS` appends `.github/`). Row N names `PRODUCT_DIRS` **plus** `.github/` explicitly rather than importing the combined tuple, so the builder cannot repeat that confusion by reaching for the shorter import.

```
Audit verdict: GO
```
