# SCC-197 wave 2 — walkthrough

**Lane** `chore/SCC-197-wave2-twin-parity` · **Base** `origin/main` @ `86daaaf`
**Riders** SCC-209 (Part A) · SCC-205 (Parts B–E) · **Landing mode** full — this landing closes SCC-197.
**Plan** [implementation_plan.md](implementation_plan.md) · **Ports backlog** [ports-backlog.md](ports-backlog.md)

---

## Part A — SCC-209 · stop maintaining the `_AP` twins

**Operator ruling, 2026-08-18, verbatim:** *"remove updating the _AP workflows we just desided that
they dont work and we will completely redo them at a later time. So lets stop waisting time on those
and focus on keeping the twins (cicd and smh) up to date."*

### Why it ran first

Not sequencing preference — it defuses a trap. `workflow_lint.check_ap_twins()` was **armed**: it
fires the moment any `cicd-*` primary is committed without its twin restamped. Parts B–E edit
`cicd-code-review.md`, `cicd-self-audit.md` and `cicd-quick-dev.md`, so running Part A second would
have turned the gate red mid-lane and forced a restamp of a file already declared abandoned.

### What changed

| File | Change |
|---|---|
| `.agents/scripts/workflow_lint.py` | Deleted `_last_commit_ts`, `_last_commit_sha`, `AP_RECONCILED` and `check_ap_twins()` (75 lines) plus the single call site in `main()`. The two helpers had exactly four tree-wide references — two definitions, two uses, both inside the deleted function. |
| `.agents/scripts/tests/test_workflow_lint.py` | The SCC-82 AP-twin block (165 lines, cases A–G) deleted **in the same commit** — it called the function by attribute, so removing the definition alone raises `AttributeError`. Replaced by ONE assertion that all three `*-AP.md` files carry the `UNMAINTAINED` marker. |
| `.agents/commands/cicd-code-review-AP.md` · `cicd-self-audit-AP.md` | The `ap_reconciled:` stamp and its 60-/14-line reconciliation log replaced by the unmaintained marker. |
| `.agents/commands/cicd-dev-story-tests-AP.md` | Marker added (it never carried a stamp). |
| `.agents/commands/smh-clean-code-audit.md` | Its gate table advertised `` `-AP` twin drift `` as something `workflow_lint --toolkit-only` checks. It no longer does — a command that advertises a check that does not exist teaches agents the gate is wider than it is. |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | The `ap_reconciled:` row marked RETIRED, pointing at the marker instead. |
| `_artifacts/_memory/sudo-commands-have-ap-twins-that-drift.md` + `MEMORY.md` | Surgically edited: the `_AP` obligation replaced by the abandonment ruling; the `cicd`/`smh` twin law kept intact. Its claim that hoisting keeps bodies under a byte threshold corrected — an oversized body now gets an auto-generated thin launcher, so size is no longer an argument for hoisting. |

### What was deliberately NOT done

- **The three `*-AP.md` files are kept, not deleted.** Three autopilot engines still invoke them by
  name; a missing command makes a headless stage improvise silently instead of failing — an agent
  running with no specification, writing artifacts that look normal.
- **No no-op stub** left behind in place of `check_ap_twins`.
- The line numbers in the plan were **re-measured** before acting. The lane also absorbed `origin/main`
  first (`fd22097` → `86daaaf`, SCC-215), which had moved two of the rules the later parts touch.

### RED first — the assertions, and what they returned before the edit

`assert-partA.sh` (in this folder) is the scripted pass. Before any edit:

```
FAIL | A1 workflow_lint.py carries no AP-twin machinery  (got '11', want '0')
FAIL | A2 test_workflow_lint.py carries no AP-twin block  (got '9', want '0')
FAIL | A3 no command file carries an ap_reconciled stamp  (got '2', want '0')
PASS | A4 the three -AP files are still present
FAIL | A5 all three -AP files carry the UNMAINTAINED marker  (got '0', want '3')
FAIL | A6 no command advertises AP-twin drift as part of its gate
EXIT=1
```

After: all six PASS, `EXIT=0`.

⛔ **A2's assertion is keyed on the machinery, not the concept.** The first draft of the replacement
comment named the deleted identifiers in prose, which made the grep match its own comment — the
`comment-literals-invert-source-grep-tests` failure. The comment was reworded to describe the check
rather than name it.

### What the RED caught

The deletion broke a **later, unrelated** block: `real = Path(__file__).resolve().parents[3]` was
bound inside the SCC-82 block and reused by the SCC-128 resurrection-lint block 40 lines below.
`run_all.py` returned `NameError: name 'real' is not defined` — a file that dies at import looks
identical in a summary to one whose assertion failed, and only one of those is a real failure. The
binding was restored with a comment saying who else reads it.

Two more files went red for real reasons and both were expected consequences, not surprises:
`test_command_surfaces.py` (the `.opencode` mirror door for the edited command — cleared by
`/smh-sync-agents`) and `test_check_maps.py` (this lane's own artifact folder had no
`_artifacts/_main/INDEX.md` row — added).

### Gates

| Gate | Result |
|---|---|
| `python3 .agents/scripts/tests/run_all.py` | **33/33 files passed, exit 0** |
| `python3 .agents/scripts/workflow_lint.py --toolkit-only` | **0 errors, 0 warnings, exit 0** |
| `assert-partA.sh` | 6/6 PASS, exit 0 |
| `/smh-sync-agents` | exit 0 — 21 launcher skills, 56 opencode commands, 35 antigravity workflows |

---

## SCC-205 — Parts B–E · the vehicle, the safety defects, the guard, the hoists

**Scope, per the plan:** this lane builds the **mechanism** that keeps the two families aligned. It
does not port command content — that is SCC-212's 84-item backlog, which lands *after* Part E because
a hoisted rule plus a pointer replaces N copies and shrinks it.

### Part B — the vehicle

`cicd-code-review.md` and `cicd-self-audit.md` carried **no "Rules in force for this command" block at
all**, which is the mechanism by which a rule reaches a command — so nothing hoisted in Part E could
have reached them. Both now carry one, mirroring their smh twins minus subject-forced entries, plus
`smh-target-resolution.md`, the cicd-only pointer.

⚠ **A plan claim corrected by measurement.** The plan said these were "the only 2 of 26 commands
without one". Re-measured at `86daaaf`: **12 cicd and 5 smh commands** lack it. The two named are
still the two Part E needs, so the fix stands unchanged — but the class is larger than the plan said,
and the rest belongs to SCC-212 rather than being quietly swept in here.

### Part C — the safety defects in `cicd-quick-dev` (the command doing real project work)

| # | Was | Now |
|---|---|---|
| **C1** | Step 0.5 authorised a chore branch *"merged back to `main` in the same session with Daniel's sign-off"*, naming **no door** — while the file's own Done section says "never touch `main`". An agent reading it literally merges to production. | The same-session merge language is gone. A door table names what actually exists per lane, and the paragraph states plainly that this lane never merges. |
| **C1b** | — | ⚠ **The gap is stated, not filled.** `/cicd-push-e2e` ships an `epic/*` branch and `/smh-close-task-merge-tree` refuses a deployable diff — so a **project repo's ad-hoc `chore/*` lane has no close-out door**. Recorded; no command invented to fill it. |
| **C2** | `no worktree`. | Gone. `worktree-per-story` has required one for every commit-producing lane since SCC-62 — and this command's plan-skip exemption is *conditional on the worktree existing*, so the line voided its own carve-out. |
| **C3** | A fired eject left the plan-first exemption open. | It **re-arms** the gate, stated in the step and in the rules-in-force block. |
| **C4** | Called `bmad-review-adversarial-general` **bare** — one lens, no roster, no verification, no triage — and gated on "the diff since the skill's `baseline_commit`", which `step-oneshot.md` never writes. | Routed through the house `code-review-engine` with the full input table and `lens_budget: standard` named explicitly. The diff is pinned from command output first, and an empty set is a STOP. |
| **C5** | `--story <id-or-slug>` — a free-text slug, while `/cicd-update-sprint-memory` passes `--story <id>`. Two spellings of one lane give one ticket two records, and `check` blesses the pair as "two lanes" (AVCH-59, measured 2026-08-15). | One named source per lane, identical at every later surface. ⚠ The durable fix — reading it from a `task.yaml` as the smh side does — is **recorded, not built**: no `cicd-*` command writes a `task.yaml` at all, so `devrecord`'s anti-fork default cannot fire on this side. That belongs with the close-out rebalance (SCC-210). |

⛔ **C4 is MORE BMAD, not less.** The engine *runs* the BMAD lenses — the adversarial reviewer under a
hunter contract deliberately starved of context, beside `bmad-review-edge-case-hunter` — with a
roster, a verification pass and triage that a bare call has none of.

⭐ **Wiring it caught its own omission.** `test_review_engine.py` derives the engine's caller set from
the tree and compares it to a pinned list; making `cicd-quick-dev` a caller turned that row **red**
(`unpinned: ['.agents/commands/cicd-quick-dev.md']`). Without it the new caller would have named no
budget and silently inherited the autopilot's `capped` — the exact SCC-147 defect. Pinned as
`QUICK_CMD`, and the roster/budget rows now cover it.

### Part D — the guard, and the zero that was the bug

`workflow_lint --toolkit-only` exited **0** with 172 confirmed drift findings live in the tree.
Nothing in the repo compared the two families. That is the root cause — structural, not careless.

`.agents/scripts/tests/test_twin_parity.py` (auto-discovered by `run_all.py`) asserts **two** things
over six declared pairs, not one:

- **SYMMETRY** — a law marked in one twin has a counterpart in the other. This is the layer that
  catches the failure that caused the ticket. **Identity alone sits green through that entire
  failure**, because when law is written into one family and absent from the other, no counterpart
  region exists to compare.
- **IDENTITY** — where both mark it, the regions are byte-identical after whitespace normalisation.

A shared region is fenced by a literal (`<!-- twin-law: <id> -->` … `<!-- /twin-law -->`), which keeps
the comparand **narrow on purpose**: widening it to whole files would force subject-specific law to
match and break both commands. The escape hatch is auditable rather than silent —
`<!-- twin-divergence: <id> — <reason> -->` is honoured, **counted and printed**, so an intentional
asymmetry is a recorded decision. Two laws are fenced today: `disposition` across the clean-code pair
and `roster` across the code-review pair.

The pair list is **pinned**, because names differ where the subject does
(`cicd-merge-epic-workingtrees` ↔ `smh-merge-multiple-workingtrees`) — and a completeness row derives
the counterpart set **from the tree** so the list cannot silently go stale. `smh-quick-fix` is
recorded in `NOT_PAIRED` with its reason rather than faked into a pair.

**Mutation sweep — 7/7 killed** (`sweep-partD.sh`, one scripted pass, every mutant drawn from the
code):

```
M1  one twin's shared law edited (identity)                KILLED
M2  new law in smh only (symmetry)                         KILLED
M2b new law in cicd only (symmetry, other direction)       KILLED
M3  one twin's fence removed (symmetry)                    KILLED
M4  unpinned name-counterpart (completeness)               KILLED
M5  extractor gutted to return {} (anti-vacuity)           KILLED
M6  PAIRS emptied (anti-vacuity)                           KILLED
```

M2b exists because **the direction of drift is about to invert.** Operator, 2026-08-17: *"we will
usually be working with cicd since the goal is to use the command center for projects."* A guard that
only catches smh-ahead-of-cicd would go blind exactly when it starts to matter. The file's header
carries that warning in full, so whoever reads it in 2027 measures which half carries the law rather
than inferring it from which half was ahead in 2026.

⛔ **Not the retired `ap_reconciled` stamp re-aimed at these pairs.** It derived the primary from the
twin and scanned only the twin's text — one-directional, so the cicd file could drift under a green
stamp — and its comparand was whole-file, so every subject-specific edit invalidated it and produced
reflexive restamping. Part A deleted it anyway.

### Part E — the hoists

Four laws hoisted into rules that already exist. **No new rule files**, and every one is a rule **plus**
a pointer **plus** an inline restatement — a pointer that replaces the restatement is itself a finding,
because agents follow the literal step list.

| Law | Was | Now |
|---|---|---|
| **The three-question disposition test** (REAL? · changes BEHAVIOUR? · in THIS diff? · "it's cheap" is not a reason) | Lived **only** in `code-review-engine/steps/step-01-review.md`, owned by no rule, carried by none of the audit commands — while both clean-code audits described an unbounded fix queue. | `code-standards.md` **§6.5**, which already owns the FAIL-vs-CONCERNS split. Restated identically in both clean-code audits (fenced as the `disposition` twin law), pointed at from both self-audits. |
| **A gate that cannot fail is a finding** | Absent from `tests-must-gate-for-real.md`; a FAIL trigger on smh and absent from the cicd ladder entirely, so a report-only job shipped at worst CONCERNS. | Rule 5, plus the cicd FAIL-ladder row and a judgment-pass scan line. |
| **Run gates bare** | Nowhere in the rule. | Rule 6 — a pipe returns the *pipe's* exit code, and `set -o pipefail` is not on by default. |
| **Both machines** | `code-standards.md` §5 stated the underlying rule nowhere; the cicd clean-code audit had no `C:/` check and no bare-`python` check. | §5 row + a judgment-pass scan line. |
| **The memory store** | `grep -rln "_artifacts/_memory" .agents/rules/` returned **1**. | A full clause in `artifacts-always-first.md`: the store is **recall, not law** — prunable, unenforced, advisory, and it creates false coverage. With the test *"if this memory vanished, would something BREAK or would someone look it up?"* and the never-sweep-another-lane's-memory rule. |

⛔⛔ **And one measured defect the hoist exposed: the cicd machine floor could not run on this
machine.** `code-standards.md` §6 and `cicd-clean-code-audit.md` Step 1 both hardcoded
`backend/.venv/Scripts/python.exe` and `Scripts/pyrefly.exe` — the **Windows** layout. Verified on
disk: AGY's `backend/.venv` has `bin/`, not `Scripts/`. Under the audit's own rule a missing tool *"is
a finding, not a skip"*, so **every Mac run of the most-used audit reported its own floor unrunnable**
— or the agent substituted bare `python`, which the same command forbids. Either way the objective
half did nothing while the run looked normal. Both now resolve `<VENV>` per machine, POSIX first.

**The lint row that makes it stick.** `workflow_lint`'s rule-pointer check gained a row: a command
that produces findings and cites no disposition rule goes **red**. Keyed on the **machinery** (the
`applied / deferred / dismissed` triage vocabulary and the FAIL ladder), never on the concept — a
concept-keyed row previously matched six unrelated bodies and none of the three that mattered.
**Proven to reject and allow**: dropping the pointer from `cicd-clean-code-audit.md` produced
`rule-pointers: ... producing findings but never points at code-standards.md`, exit **1**; restoring
it returned exit **0**.

### Re-measured and NOT acted on

- **C6 (`lenses_na` in neither caller) is already fixed.** The ticket lists it as ⛔ "THIS ONE IS
  OURS, from SCC-203". Measured at `86daaaf`: **both** `cicd-code-review.md` and `smh-code-review.md`
  carry `lenses_na` and `lenses_counted` three times each, with the 4/4-never-4/5 rule stated. It was
  closed during SCC-203's own landing, after the audit was written. No edit made.
- The three findings the plan's §7 rejected during verification stay rejected; the bounded-queue
  sentence in both clean-code audits was **not** edited — the disposition text was added **above** it.

### Gates

| Gate | Result |
|---|---|
| `python3 .agents/scripts/tests/run_all.py` | **34/34 files passed, exit 0** (33 before — `test_twin_parity.py` is the new file) |
| `python3 .agents/scripts/workflow_lint.py --toolkit-only` | **0 errors, 0 warnings, exit 0** |
| `assert-scc205.sh` | 16/16 PASS, exit 0 — and **16/16 FAIL** against the pre-edit commit `49153af` |
| `sweep-partD.sh` | **7/7 mutants killed**, tree restored, baseline and final both exit 0 |
| `/smh-sync-agents` | exit 0 |

⛔ Every gate was run **bare**, exit code read immediately — the rule this lane just wrote. The first
run of the lint in this session was piped through `tail` and lost its exit code entirely.

---

## SCC-205 follow-on — the both-machines class, swept and guarded

**Operator, 2026-08-18:** *"yeah we are on a mac now so thats not good."*

The Part E hoist fixed the venv path in **two** places (`code-standards.md` §6 and
`cicd-clean-code-audit.md` Step 1). A sweep of every authored surface found **five more live
invocations** — the fix was right and the scope was not.

| Surface | What it was, and why it mattered |
|---|---|
| ⛔⛔ `cicd-close-workingtree.md` Step 4 | `backend/.venv/Scripts/python.exe --version` — the probe that verifies shared assets **survived**, sitting on the **destructive** path. The very next line says *"Any failure here → STOP and report immediately. A destroyed shared asset breaks every other lane."* On the Mac the path does not exist, so **every Mac close-out would report a destroyed venv that was never touched.** A probe that cries wolf on the one step guarding an irreversible delete is a probe people learn to skip. |
| `cicd-merge-epic-workingtrees.md` | the per-lane post-merge test gate, `Scripts\python.exe -m pytest` — the gate that decides whether a lane lands. |
| `cicd-live-testing-team.md` | `Scripts\uvicorn` — the backend never starts. |
| `cicd-mobile-error-team.md` | `Scripts\python.exe -m pytest`. |
| `troubleshoot-cloudrun-deployment/SKILL.md` | `.venv\Scripts\python.exe -m pytest`. |
| `smh-clean-code-audit.md` | descriptive only (it names the cicd floor to say the lobby has none of it) — corrected for accuracy. |

**11 hardcoded occurrences before, 0 after** (measured by the `E6` assertion against `49153af`).

### The guard, because a fix with no guard is what let this rot

`workflow_lint.check_both_machines()` warns on a hardcoded `.venv/Scripts` with **no POSIX arm on the
line beside it**, over `.agents/{commands,rules,skills}`.

⛔ **The line-pair off-switch is the whole design.** A file may legitimately name the Windows path
three ways — as the Windows **arm of a conditional**, as **prose explaining the rule**, or as a **test
fixture** — and all three carry the POSIX spelling within a line of the hit, while a hardcoded
invocation does not. Keying on the *file* would exempt whole documents; keying on the *line pair* asks
the question the rule actually cares about: *did the author think about the other machine HERE.*
Getting this wrong is the `comment-literals-invert-source-grep-tests` disease, where the guard fires on
the document that states the law correctly.

**Seven cases, and the three look-alikes are each a negative control** — plus `G`, which runs the
detector over the **live tree**, because all six fixture rows could be green with the whole class back
on `main`.

**Mutation proof:** deleting the two-line off-switch turns **B, C, D, E and G** red at once — the
controls are not vacuous agreement, and `G` catches the real regression. Restored: 47/47.

### Gates

| Gate | Result |
|---|---|
| `run_all.py` | **34/34 files passed, exit 0** (`test_workflow_lint.py` 40 → 47 cases) |
| `workflow_lint.py --toolkit-only` | **0 errors, 0 warnings, exit 0** — silent on the fixed tree |
| `assert-scc205.sh` | **18/18 PASS**; E6 was `11` and E7 was `0` against `49153af` |
| mutation on `check_both_machines` | off-switch removed → 5 rows red, restored → 47/47 |
| `/smh-sync-agents` | exit 0 |

---

## Code Review (2026-08-18)

Verdict: CONCERNS @ 531047f
Suite evidence measured at the post-fix HEAD (see the Evidence row below) — the `Verdict:` sha above
is the reviewed sha; every finding below was fixed in-thread after it.

review-runtime: fan-out

```
lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · recovered-inline — first attempt stalled >600s on a foreground
  full-suite run and was killed; retried with a no-full-suite constraint and returned
- acceptance-auditor · recovered-inline — same stall, same cause, same retry
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:
- none — review_mode: full, so every lens was applicable
```

**Why CONCERNS and not PASS.** The gate the lane shipped to stop silent drift was itself
substantially unguarded, and review measured it rather than arguing it. **Every finding below was
real, changed behaviour, and was in this diff** — the three-question disposition test admitted them
all, which is the point of running it rather than a reason to be lenient. They are fixed; CONCERNS
stands because the volume in one lane's own safety machinery is itself the signal.

### The one that mattered most: 13 of 17 mutants survived

The Test-Adequacy Auditor did not read my mutation proof — it wrote its own 17-mutant sweep and ran
it. My proof was **one mutant, and it was a widening**. Every *narrowing* survived: `check_both_machines`
could be cut to one directory, lose its Windows-backslash spelling, have its window widened, be
downgraded to `info`, or be **unwired from `main()` entirely**, all with the file green.

⭐ That is the difference between "I proved my check can fail" and "I proved my check can fail **the
way it will actually break**." A widening mutant only ever tests the off-switch.

| Finding | Now |
|---|---|
| ⛔ `check_both_machines` **crashed the linter** on a `.md` directory or dangling symlink — reproduced twice. The sibling check 30 lines below carries both guards *with a comment saying why*; I copied its `rglob` and dropped them, and mine runs FIRST, so it took down the defensively-written ones | both guards restored, two crash fixtures |
| The off-switch accepted the bare **word** `POSIX`, so deleting a conditional's first clause left a trailing comment that exempted the hardcode | off-switch is a real `.venv/bin` path; `wordonly.md` fixture |
| The ±1-line window **false-positived on correct code** — a PowerShell probe with the brace on its own line (this lane's own probe, reformatted) and a bash conditional split by comments | window ±4; both shapes are negative controls |
| Scope was markdown in 3 dirs, while the rule it cites names committed **scripts** | `.py/.ps1/.sh` + `scripts/`; fixtures for each |
| The new rule-pointer row had **zero tests, a DEAD arm** (0 hits tree-wide) and keyed on an **em-dash**, so `cicd-code-review.md` (`- **FAIL** =`) was exempt on punctuation — 3 of 6 files covered, asymmetrically, on a parity ticket | 4 measured arms, punctuation-agnostic; **all 8 twins fire** when the pointer is dropped |
| `assert-partA.sh` **ignored `--red` and returned green against every ref** — Part A's RED claim was not reproducible by the artifact left to reproduce it | real `--red`, unknown flags refused (exit 2); 5/6 red at `86daaaf` |
| `test_twin_parity` E6 was a **tautology** (set arithmetic on a literal); gutting A1 left it green | drives the real predicate against a fixture tree |
| A1 was **blind to differently-named twins** — the shape `PAIRS` documents as normal. `cicd-zzprobe`+`smh-yyprobe` joined the tree green. `NOT_PAIRED` was **dead code** | every family command is pinned or recorded with a reason; both shapes caught |
| A **duplicate `twin-law` id masked real drift**; an **empty fence** passed identity *and* the anti-vacuity count; an **unclosed fence swallowed the next region** | all three refused and reported |
| E1 was **hash-seed flaky** (2 reds in 6 runs once a second law is fenced) | pinned; stable across 6 seeds |
| Symmetry and identity **could be hard-wired true** — the counter-examples tested a *copy* of the predicates | one shared implementation, called by both; loop directionality pinned |
| `B*` anti-vacuity was **aggregate**, hiding that 8 of 12 symmetry rows compare `{}` to `{}` | the fenced set is declared; scope is a decision |
| ⛔ **`review_mode: no-spec` promises a lens the engine does not run** — the Acceptance Auditor is `full`-only, so the walkthrough would record an acceptance audit that never happened | `full` + the AC list as `STORY_FILE`, with the trap stated |
| `$WORKTREE` unbound — and `git -C ""` **does not error**, it silently uses cwd | bound, with the reason |
| The diff base was `origin/main` while its own comment said "the epic branch" — a story lane would review every sibling's work | `BASE_REF`, epic on a story lane |
| `$PROJECT_ROOT` broke `cicd-close-workingtree`'s own placeholder convention, re-arming the false alarm on the destructive path | reverted to the placeholder |
| `"$VENV"` was assigned in one block and used in another — shell state does not survive tool calls, so each row expanded to `/ruff check` → 127 | `<VENV>` substitute-me placeholder |
| The both-machines fix wrote **POSIX shell into a ```powershell fence** | real PowerShell probe |
| `.claude/skills/…` door stayed **stale at HEAD** carrying the exact literal this lane removes — and *nothing in the suite compares an authored skill to its door* | fixed, and **CS-04** added: proven to reject and allow |
| Part E added two scan rows to the cicd audit and **none to its twin** — drift created by the lane building the drift guard | ported back |
| The SOP row described the ±1-line design the rewrite replaced | rewritten to the shipped design |
| A door-table row named an `smh-` door from a `cicd-` command that binds "never the lobby" | removed, with the reason |
| "§ When to Skip case 4" — the section has **no numbered cases** | cited by bullet name |

### Rejected after measurement — two mutants left alive, deliberately

- **A row's assertion replaced by `True`.** Drawn from the guard's own assertion expression, not from
  the code under test. Every check in this repo "survives" that, and no test can catch it; chasing it
  is turtles. Recorded, not chased.
- **Reverting E1's pin.** The defect is *latent* — it needs a second law fenced into that pair before
  it flakes — so it correctly does not red today. The pin is still right.

⭐ **The sweep also caught a fix that never applied.** One `replace()` silently no-oped after an
earlier rename, so E1 stayed flaky while I believed it was pinned — surfaced only because the sweep
reported the mutant `DEFECTIVE` ("removed nothing") rather than `KILLED`. **Every edit script in this
lane now asserts its anchor.** That is the repo's own rule earning its keep: *a mutant that removes
nothing is DEFECTIVE, not a coverage gap.*

### Deferred against a named structural blocker

**The `-AP` law assertions in `test_review_engine.py`.** Part A removed the AP obligation from
`workflow_lint`, but eight live law assertions against `cicd-code-review-AP.md` remain there, and the
tree-derived `CALLER_FILES` row *requires* it to stay pinned — so when engine law next changes, the
suite reds until someone edits a file this lane declared frozen. **The trap was relocated, not
removed.** It cannot be closed here: the plan's Part A explicitly forbids deleting the `-AP` files,
and un-pinning them breaks the completeness row that exists to stop a silent caller. It needs the
operator's decision on the `_AP` rewrite. Blocker: *an open decision.* → `deferred-work.md`.

### Gates (all run bare, exit read immediately)

| Gate | Result |
|---|---|
| `python3 .agents/scripts/tests/run_all.py` | **34/34 files, exit 0** — `test_workflow_lint` 40 → 59 cases, `test_twin_parity` 27 → 48, `test_command_surfaces` +CS-04 |
| `python3 .agents/scripts/workflow_lint.py --toolkit-only` | **0 errors, 0 warnings, exit 0** |
| `assert-partA.sh` | 6/6 green · **5/6 RED at `86daaaf`** (A4 asserts preservation, correctly green in both states) · unknown flag → exit 2 |
| `assert-scc205.sh` | 18/18 green · 18/18 RED at `49153af` |
| `sweep-both-machines.py` | **9/9 killed**, each by a named case |
| `sweep-twin-parity.py` | **8/10 killed**; the two survivors rejected with reasons above |
| `sweep-partD.sh` | 7/7 killed |
| `/smh-sync-agents` | exit 0 — every door re-synced |
