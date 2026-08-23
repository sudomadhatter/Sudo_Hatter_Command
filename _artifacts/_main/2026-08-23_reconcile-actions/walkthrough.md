---
IsArtifact: true
ArtifactMetadata:
  title: Close-out RECONCILES the operator's task list before it asks finish to close
  type: walkthrough
  date: 2026-08-23
  ticket: SCC-298
  parent: SCC-293
  lane: chore/SCC-298-reconcile-actions
---

review-runtime: fan-out

# SCC-298 — the close-out verifies the task list instead of reading it

**What shipped.** `jira_feed.py reconcile-actions`, and a mandatory step in front of every door
that closes a ticket. `finish` decided `Done` from what `## Your Actions` **claimed**; nothing had
ever checked whether a row's claim was still true. SCC-288 sat at `Review Required` for a day over
one box whose API token already existed, authenticated, and had attached the file.

> **Operator, 2026-08-23:** *"agents are terrible at checking off those task lists, especially when
> its a user task, even if I tell them."* And the ruling on how a row gets ticked: **evidence where
> a machine check exists; where none does, ask and tick on their word — recorded either way.**

**The precedent was already in the file.** SCC-175 stopped reading the *merge* row off a tick and
started **computing** it from the repo — *"a tick is a CLAIM, and `finish --apply` is what writes
`Done` to Jira on the strength of it."* That covered one row. This is that ruling for every other
row, with the difference that most rows have no `merge-base` to ask, so the check is derived per
row and its **answer** is written into the file beside it.

## Task Checklist

- [x] **Step 0 — repo, ticket, runtime probe.** `Sudo_Hatter_Command`; SCC-298 (Subtask under
      SCC-293); `review-runtime: fan-out` recorded here before the review it describes.
- [x] **Step 0.5 — worktree, upstream unset, ticket to In Progress.**
      `chore/SCC-298-reconcile-actions`; `jira_feed.py start` exit 0.
  - ⚠️ `git worktree add … origin/main` **auto-tracked `origin/main`**. `branch --unset-upstream`
    ran immediately — an unnoticed `git push` on that branch targets `main`.
- [x] **Step 1 — six checkable acceptance rows** (A7 added by the audit → seven).
- [x] **Step 1.5 — plan written, self-audited, `approved` received.** Audit verdict **GO** with
      four anchored findings, all baked into the plan before the stop.
  - ⚠️ **F1 (high)** — *"byte-identical in both doors"* had **no check behind it**.
  - ⚠️ **F2 (high)** — it is **four** doors that call `finish --apply`, not two.
  - ⚠️ **F3 (medium)** — `.agents/scripts/INDEX.md:22` enumerates the verbs; it was not declared.
  - ⚠️ **F4 (medium)** — Scope Ledger: `sweep.json` created with no acceptance row behind it.
- [x] **Step 1.6 — no subtasks.** Nothing earns its own branch, and a `Subtask` cannot have
      children (`hierarchyLevel -1` is the floor).
- [x] **Step 2 — RED, and the RED caught its own vacuity.** 15/27 → tightened → **6/27**.
- [x] **Step 3 — GREEN.** Block **83/83** after the review; `test_jira_feed.py` **502/502**;
      `test_command_surfaces.py` **214/214**.
  - ⚠️ **The suite caught an assumption I had not checked**: `.opencode/commands/*` are FULL
    copies of the brain, not thin launchers. Four went stale; `/smh-sync-agents -NoGlobals` fixed
    them. `.agents/workflows/` and the launcher skills *are* thin — git saw no change in either.
  - ⚠️ **The sweep found a real defect**: mutant **M2** survived. The contentless deny-set was
    **35/37 unreachable**, and the case meant to cover it was exercising the floor instead.
- [x] **Step 3 — sweep.** **30/30 killed** (16 before the review, 14 added for its findings),
      restore verified byte-identical, both closing full-file runs green.
- [x] **Step 3.5 — eject tripwire clear.** No deployable path in the diff, no story shape, no
      NO-GO. Every acceptance row reduced to a command.
- [x] **Step 4 — review gate.** `/smh-code-review`, five lenses, `fan-out`. **Verdict: CONCERNS**
      @ `2804483`. 16 findings applied in-lane, 2 dismissed with reasons; drift 0/0/0.
  - ⚠️ **Two CRITICAL findings, both reproduced, both in code this lane had called green** — a
    newline in `--evidence` closing tickets over unchecked rows, and the reconcile step placed
    after the merge in all four doors. The RED run, a 16-mutant sweep and 456 cases were green
    over both.
  - ⚠️ **A lens's mutation sweep silently reverted my concurrent edits** in the shared worktree,
    and one of my reads caught the file mid-mutation. Committed history verified clean after.

## Evidence

**Shipping sha `2804483`.** Twelve commits on `chore/SCC-298-reconcile-actions`; the
first four built it, the rest are the review's. The `## Code Review` section below is the
authoritative record of what changed and why.

| sha | what |
|---|---|
| `f2093fa` | the verb, the four door passages, the rule clause, the SOP, both INDEX rows |
| `645837d` | the opencode mirrors the suite caught going stale |
| `ed52202` | the three cases the mutant table found missing, and the table |
| `854d350` | the deny-set the sweep proved was 35/37 unreachable |

### RED — and reading *which line raised*, which is the whole point

First run of the block against a `jira_feed.py` that had never heard of the verb:

```
[FAIL] A1 an open section EXITS 3 - the same HELD code `finish` uses: exit=2: usage: jira_feed.py [-h]
jira_feed.py: error: argument verb: invalid choice: 'reconcile-actions' (choose from 'outline', …)
…
[PASS] A3a a line that is already ticked is not an open row: exit=2: … invalid choice: 'reconcile-actions'
[PASS] A3a … - and NOTHING was written: the file changed on a refusal
-- 15/27 passed --
```

⛔ **Twelve of those fifteen passes were fiction.** Every refusal case asserted `code == 2` — and
**argparse exits 2 on an unknown verb.** Nothing ran, so nothing was written either. A case that is
green *before* the feature exists cannot fail when the feature breaks
(`red-test-can-die-before-its-assertion`). The same shape sank A1's two negative rows (*"the string
is absent"* is trivially true of empty output) and A2's *"the original text survives"* (the
**untouched** row also contains that text).

Tightened: every refusal must carry a `jira-feed: REFUSED` marker the verb owns, and every negative
row is bound to the exit code that proves the verb ran. **The honest red:**

```
-- 6/27 passed --
FAILED: A1 an open section EXITS 3 …, A1 …line number, A1 …SETTLED row is not listed, A1 …AGENT's
own checklist rows are invisible, A1 a section with nothing open EXITS 0, A2 the tick exits 0, A2
EXACTLY ONE line changed…, A2 the row is now ticked, A2 …original text survives, A2 …SOURCE is
recorded…, A2 …evidence itself is in the file, A3a…, A3b…, A3c…, A3d…, A3e…, A3f…, A3 (control)…,
A5 the only open row reconciles, A5 …`open_actions` is now CLEAR, A5 …so the list exits 0
```

### GREEN, per acceptance row

| Row | Assertion | Result |
|---|---|---|
| **A1** | open section exits 3, every open row named `L<n>`, settled rows and the agent's own `## Task Checklist` invisible; empty section exits 0 | **PASS** — and `A1c` pins the fail-closed direction: **no section at all is a refusal**, listing *and* ticking |
| **A2** | exactly one line changes, it is the one asked for, it is now `- [x]`, the source and the evidence are both in it | **PASS** — `len(before) == len(after) and diff == [L_C0 - 1]` |
| **A3** | five refusals, each exit 2 **with the `REFUSED` marker** and `read_bytes()` unchanged | **PASS** — plus `A3g` (floor alone), `A3h` (companion flags), `A3i` (the deny-set polices itself), and the **control** that a real operator row with real words is ACCEPTED |
| **A4** | the `<!-- reconcile-law -->` block extracted from all four doors is non-empty, >200 chars, and byte-equal | **PASS** — `CS-17`, 2/9 → **9/9**; all four blocks measure **1743** chars |
| **A5** | tick the only open row → `open_actions()` returns `[]`, so `finish` would close | **PASS** |
| **A6** | rule carries the law; all four doors cite it | **PASS** — `CS-17 F` × 4 |
| **A7** | every mutant killed by a NAMED case | **PASS** — **16/16** |

### The gates, at `854d350`

| Gate | Result |
|---|---|
| `run_all.py` **through the receipt writer** | **PASS exit 0, 92.3 s @ `854d3501`**, `dirty_tree: false` — receipt at `gates/suite.json` |
| `test_jira_feed.py` | **502/502** (was 456 before the review's cases) |
| `test_command_surfaces.py` | **214/214** (was 207/208 — the stale-mirror catch) |
| `mutation_sweep.py --table sweep.json` | **30/30 killed**; *"restore verified: bytes match, nothing was committed"*; both closing unfiltered full-file runs exit 0 |
| `workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, 8 info (pre-existing BOM notes) |
| maps ratchet on every commit | passed from a **worktree**, with **no `[maps-ok]`** — SCC-288's R9 fix holding |

### The two defects this lane found in its own work

**1. The RED lied, and the count was what hid it.** 15/27 looked like a healthy red. Twelve of the
passes were argparse's exit code being mistaken for the verb's. Reading *which line raised* — the
instruction the command gives and the one that is easiest to skip — is what surfaced it.

**2. `_GENERIC_EVIDENCE` was 35/37 unreachable, and only a mutant could see it.** M2 gutted the set
to `()` and the suite stayed green, because the length/word floor beneath it already refuses
anything under 16 characters or 3 words — so `done`, `ok`, `verified`, `n/a` never reached the set
at all. The case meant to cover it (`A3d`, ticking with `"done"`) was **exercising the floor**. Two
guards, one tested, and the untested one was almost entirely dead code wearing a guard's clothes.

Fixed in three places rather than by re-aiming the test alone: the set is now **19 long contentless
phrases**, every one ≥16 chars and ≥3 words — the one shape a floor structurally cannot see; `A3i`
asserts that property so the set **polices itself**; `A3d` was re-aimed at `"confirmed by operator"`
(21 chars, 3 words), which only the set can refuse. ⛔ Kept **exact-match** deliberately: a fuzzy
content test would refuse real operator quotes, and **a false refusal HOLDS a ticket** — the exact
failure this feature exists to end.

### Two decisions taken beyond the ticket, recorded so they are decisions

- **The verb refuses the MERGE row** (SCC-175). Not in the ticket's plan. Without it, this verb
  hands back the affordance SCC-175 spent a lane removing: `finish` computes that row from the
  repo, and a hand tick is the self-certification that fix closed. One `if`.
- **`/smh-sync-agents` ran with `-NoGlobals`.** The unswitched sync also publishes to the machine
  caches, and this lane has not landed — publishing an unmerged branch would put a door on the
  operator's menu that no `main` contains.

### Honest about the three cases written green

`A3g`, `A1c` and `A3h` were written **green, not red**: designing the mutant table asked whether
anything could see three behaviours, and nothing could, but the behaviour was already implemented
when the question was asked. A characterization check written green is honest; a green check
presented as a red is not. The sweep (M3, M11, M13) is what proves they bite.

## Landing — the gate run at the shipping sha, and the detour that delayed it

The `Verdict: CONCERNS @ 2804483` above stands for that sha. Between it and the landing, this lane
absorbed `origin/main` twice, so the preflight refused the suite SKIP (*"code moved since the verdict
(4 non-artifact files) — the full gate runs"*) and every gate was re-walked at the landing sha:

| Gate at the landing sha | Result |
|---|---|
| `tests/run_all.py` | **59/59 files, exit 0** |
| `workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, 8 info — exit 0 |
| `check_maps.py --depth3-only --strict` | exit 0 |
| `check_links.py --base origin/main` | 16 files, 205 path claims — clean, exit 0 |
| `task_preflight.py --fetch` | **clear to close out and merge**, `LANE: LOCAL` |

⭐ **This close-out found `main` red and stopped to fix it.** The first absorb of `origin/main`
brought in SCC-299 (`4e5e09f`, PR #66), whose new `is_scratchpad()` matched the bare
`/tmp/claude-<uid>` **parent of every session** — so `test_cwd_escape_hook.py` was 46/51 and the
cwd-escape guard had stopped refusing real escapes. This lane's suite went 58/59 on inherited code.
It was fixed on its own lane rather than folded in here, because this lane's verdict is stamped at a
sha and mixing another ticket's regression in would invalidate that stamp: SCC-299 flagged `Bug`,
fixed, landed as PR #67 @ `bfdf379`, closed `Done`. Only then did this lane re-absorb and go green.

⛔ **Two other things this landing hit, both now filed as SCC-300.** The OS sandbox denies every
write under `.claude/hooks/` and `.claude/skills/` at any depth regardless of `allowWrite`, so
`git merge` died on `unable to unlink old '.claude/hooks/guard-cwd-escape.py'` and had to be re-run
with the sandbox off; and `gh pr create` fails TLS as a Go CLI under the same sandbox. Neither is a
defect in this lane's work, and neither is fixable from inside this repo.

## Your Actions

- [ ] **The merge itself** — lands via this branch's PR against `main`.
- [ ] **Decide when your opencode and Antigravity menus should pick up the changed doors.** This
      lane synced only the in-repo mirrors (`-NoGlobals`), deliberately, because it had not landed.
      The machine-global caches still carry the pre-SCC-298 text, and opencode needs a restart to
      rebuild its catalog either way.

---

## Code Review (2026-08-23)

Verdict: CONCERNS @ 2804483
Suite evidence measured @ `23c47d73` — `run_all.py` **59/59 files, exit 0**, 85.6 s, clean tree.

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none

dispositions:    per-lens: blind=7/2/0 · edge=8/0/0 · literal=5/0/0 · acceptance=8/0/0 · test-adequacy=12/0/0 (a multi-lens finding counts once per contributing lens; 5 anchors were reached by 2+ lenses and are merged in the table below)
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — seven generated files (four `.opencode` mirrors, the sync manifest, the doc-graph pair) were undeclared at first pass and are now named in the block with their reasons

**Scope:** `origin/main...HEAD`, 24 files. **Method:** `review_level: standard`, `review_runtime:
fan-out`, `lens_budget: standard`. Five lenses in parallel clean contexts; the Blind Hunter was fed
the diff text from outside the repo and never opened it. `lenses_na: none` because `review_mode`
was `full` — the plan's acceptance table is the spec — so every lens was applicable and every one ran.

**Changes applied: many — see the table.** Every finding that survived the relevance gate was fixed
in this lane before this verdict. No finding left as future work; no ticket minted.

### Why CONCERNS and not PASS

Every gate is green at the shipping sha and every acceptance row is evidenced. The verdict is
CONCERNS because of **what the review had to find**, not what remains: two of the findings were
**critical and reproduced**, both in code this lane had already declared green, and the lane's own
RED run, its 16-mutant sweep and a 456-case suite were all green over them. A verdict of PASS would
say the process caught its own defects. It did not — the fan-out did.

### Findings

| # | file:line | severity | failure scenario | disposition |
|---|---|---|---|---|
| F1 | `jira_feed.py` `evidence_ok`/`tick_row` (edge ×1, literal ×1) | **critical** | Evidence containing a newline was written verbatim. A line starting `## ` ends the section for `_collect`; a stray fence hides the rest of the file. `open_actions` returns `[]` not `None`, `finish` takes the "nothing owed" path and **closes the ticket over unchecked rows** — while the verb prints *"is now CLEAR"*. Reproduced twice. | **applied @ `815a4b0`** — `_CONTROL_RE` refuses any control char; `--date` validated the same way |
| F2 | 4 × `.agents/commands/*.md` (acceptance, blind, literal) | **critical** | The reconcile step sat beside the `finish` call — inside `smh-close-task-merge-tree` **Step 4**, whose first line is *"After the merge, never before"*, with Step 5 pruning the worktree. `cmd_finish` reads the **working tree**, so the tick clears the hold and Jira goes `Done` while the landed copy keeps `- [ ]`. The lane would have shipped the defect it exists to fix. | **applied @ `dafa066`** — moved into each door's pre-landing window; `CS-17 G` asserts the order and was **proven to bite** |
| F3 | `jira_feed.py` `cmd_reconcile_actions` (blind) | **important** | The verb counted the MERGE row as open — a row it refuses to tick and that `finish` clears from the repo. Almost every walkthrough has one, so it could essentially never reach 0 and would report a finished lane as HELD. Live in this lane's own dogfood run. | **applied @ `815a4b0`** — the count is settleable rows only |
| F4 | `jira_feed.py` `tick_row` (blind, edge) | **important** | The listing's own *"DELETE the row"* tag shifts every row below it; the next tick then settles a **different** obligation with evidence that was never about it, and `--tick`'s only guard was "is this line open" — which it is. | **applied @ `815a4b0`** — `--expect` verifies the row, banner warns to re-list after a delete, docstring names its precondition |
| F5 | `jira_feed.py` `tick_row` (acceptance) | **important** | The proof was appended to the checkbox line, splicing machine text through the middle of a wrapped row and orphaning the rest. Fires on **this lane's own walkthrough**. | **applied @ `dafa066`** — `_collect` carries the row's end line |
| F6 | `jira_feed.py` read/write path (edge, literal, blind) | **important** | The verb rewrites the whole file through a lossy reader: an undecodable byte became **U+FFFD permanently**, a BOM was swallowed, CRLF was rewritten wholly to LF. All three reproduced. | **applied @ `815a4b0`** — `wf.read_exact`/`write_exact`, the pair the repo already ships for this |
| F7 | `jira_feed.py` `tick_row` (edge, literal) | **important** | Evidence naming a merge door **manufactured** a merge row out of an ordinary one, so `finish` re-opened a row the file never contained. | **applied @ `815a4b0`** |
| F8 | `jira_feed.py` `tick_row` (edge) | **important** | `splitlines` breaks on `\v \f \x85    `; `rstrip("\r\n")` knew two of them, so an exotic separator was dropped on write — two rows welded and the open one below vanished. | **applied @ `815a4b0`** — the terminator comes from the line, via the reader's own splitter |
| F9 | `test_command_surfaces.py` CS-17 (acceptance) | **important** | Presence, length, byte-equality and a law citation cannot see **order** — all six rows were green over F2. `source-grep-guards-cannot-see-order`, in a guard written in this lane while that memory was on screen. | **applied @ `dafa066`** — `CS-17 G`, with an anti-vacuity row because `-1 < 5` is True |
| F10 | `jira_feed.py` `_EVIDENCE_TRIM` (test-adequacy) | **important** | Emptying the decoration strip survived all 462 cases: the code's own claim that *"a deny-set is defeated by adding a full stop"* was unpinned. | **applied @ `815a4b0`** — `A3n` |
| F11 | `jira_feed.py` `_TICK_RE` (test-adequacy) | **important** | Narrowing it to `^(- )\[\s\]` survived 462 cases — every fixture was a flush `- [ ]`, so the two regexes' agreement was untested. | **applied @ `815a4b0`** — `A2e` |
| F12 | `jira_feed.py` (test-adequacy ×3) | suggestion | Three guards with no case at all: the missing-walkthrough refusal, the listing's guidance tags, and the `-- verified` marker + date. Each survived as a mutant. | **applied @ `815a4b0`** — `A1g`, `A1h`, `A2f` |
| F13 | `jira_feed.py` `evidence_ok` (test-adequacy) | suggestion | The punctuation-only branch decided nothing — `if False:` survived, because the floor already refuses anything normalising to `""`. | **applied @ `815a4b0`** — **deleted**, not kept with a nicer message |
| F14 | `jira_feed.py` `open_actions` (test-adequacy) | suggestion | SCC-155's "every section, not just the first" fix existed in **two copies** with nothing asserting they agreed. | **applied @ `815a4b0`** — `open_actions` delegates; `A1i` pins it |
| F15 | `test_command_surfaces.py` `CLOSING_DOORS` (test-adequacy) | suggestion | A hand-written four-name tuple cannot enforce §4's *"every command that runs `jira_feed.py finish`"*; a fifth door would pass in silence. | **applied @ `815a4b0`** — derived from the tree by the real call |
| F16 | plan `## Design`, `INDEX.md`, SOP fence (acceptance, blind) | suggestion | The plan described the em-dash marker and a deny-set of short words the lane does not ship; an unescaped `\|` truncated the INDEX row at `--source measured`; a run of spaces replaced a `\` continuation in the SOP. | **applied @ `815a4b0`, `2804483`** |
| — | `_MIN_EVIDENCE_CHARS`/`_WORDS` (blind) | suggestion | **dismissed — relevance leg 1.** The floor refuses `exit 0` and `HTTP 200`. Deliberate: those name no subject, so they are not checkable by a later reader, and the refusal message says exactly how to fix it. One reword, no blocked flow. The tension with *"over-refusing is not recoverable"* is real and is recorded rather than resolved by loosening the floor. |
| — | blank line before the block in one door (blind) | nitpick | **dismissed — moot.** The block moved in F2; all four now sit at a paragraph boundary. |

### Gates at the shipping sha

| Gate | Result |
|---|---|
| `run_all.py` via `gate_receipt` | **PASS, exit 0, 85.6 s @ `23c47d73`**, `dirty_tree: false` |
| `test_jira_feed.py` | **502/502** · the SCC-298 block **83/83** |
| `test_command_surfaces.py` | **214/214** · `CS-17` **17/17** |
| `mutation_sweep.py --table sweep.json` | **30/30 killed**, restore verified byte-identical, both closing unfiltered runs exit 0 |
| `workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, 8 info |
| `check_links.py --base origin/main` | exit 0, clean |
| `sop_currency.py` | exit 0 |
| `declared_change_set.py diff` | undeclared 0 · unimplemented 0 · incomplete 0 |

### Acceptance matrix

| Row | Proving assertion | Result |
|---|---|---|
| A1 | exit 3 with padded `L<n>` per open row; settled rows and `## Task Checklist` invisible; empty section exits 0; **`A1e`** a merge row alone exits 0 like `finish`; **`A1c`** no section is a refusal both ways | **satisfied** |
| A2 | one line changes for a flat row, **`A2b`** two for a wrapped one with the count preserved; **`A2c`** BOM/CRLF/undecodable bytes survive; **`A2e`** indent and `*` bullets; **`A2f`** marker and caller's date | **satisfied** |
| A3 | seven refusals, each `exit 2` **with the `jira-feed: REFUSED` marker** and `read_bytes()` unchanged, plus an accept-control | **satisfied** |
| A4 | `CS-17` A–G over a **derived** door set: non-empty block, >200 chars, byte-equal, names the verb, cites the law, **and ordered before the landing** | **satisfied** |
| A5 | tick the only open row → `open_actions()` `[]` → re-list exits 0 | **satisfied** |
| A6 | clause 4 in the rule; `CS-17 F` × 4 | **satisfied** |
| A7 | `mutation_sweep` **30/30**, every mutant drawn from the code and killed by a NAMED case | **satisfied** |

### Step 0.7 — re-derivation

1. **Nothing this diff references moved.** `origin/main` is still `0ec1fe4` — the exact base this lane branched from, so zero files landed while it was built. All ten repo paths the diff names were re-resolved and exist.
2. **True overlap: none.** `merge-base..origin/main` is empty; `git merge-tree --write-tree HEAD origin/main` returned a clean tree (`413b2f37`) with no conflict messages.
3. **One live sibling: SCC-280** (`claude/teaching-edition`), uncommitted, touching `docs/_scc_sops_prds/workflows_testing_SOP.md` and `.agents/.sync-manifest.json` — both of which this lane also stages. **This lane should land first**: it is complete and pushed, theirs is mid-flight. If theirs lands first, `git merge origin/main` here and re-resolve two independently appended SOP paragraphs — text-level only, no shared machinery.

### Clean-Code Gate

Machine floor imported from the gates above (SCC-146) rather than re-run. Ran only what they did not:

| Check | Result |
|---|---|
| `py_compile` on all three changed `.py` files | clean, exit 0 |
| Secrets / credential literals in the diff | none |
| `TODO`/`FIXME`/`XXX`/`HACK` introduced | none |
| Comment contract (§2A) | every new guard carries the measured failure that motivated it, and names it as measured rather than feared |
| Convention table (§2C) | `python3` with the PC note on every doc command line; stdlib only; explicit paths in every commit |
| Drift / bloat (imported from Step 1) | one deletion on merit — `evidence_ok`'s punctuation-only branch (F13) |

⚠️ **Two process observations, recorded because they cost real work.**

1. **Lens subagents write to the lane's working tree.** Two of them ran `mutation_sweep.py` and hand-edited `jira_feed.py` to test whether cases notice — correct behaviour for the instruction *"prefer executing to reasoning"*, which I wrote. One sweep's restore **silently reverted my concurrent edits**, and one of my reads caught the file mid-mutation and reported a defect that did not exist. Committed history was verified clean afterwards: zero `if False:` residue across all commits. A reviewing lens needs its own copy or its own worktree.
2. **`/smh-sync-agents` cannot complete under the sandbox** — it is denied writes into `.claude/`. The `.opencode` mirrors are byte-for-byte copies of the command bodies, so its exact copy step was performed for the four moved doors; `CS-03` door parity (11/11) is the proof.
