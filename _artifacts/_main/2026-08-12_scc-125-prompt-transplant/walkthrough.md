# SCC-125 — Prompt transplant: FP gates on hunter lenses, adapted rubrics for auditors

**Ticket:** SCC-125 (Subtask of SCC-116) · **Lane:** `chore/SCC-125-prompt-transplant`
**Plan:** [implementation_plan.md](implementation_plan.md) (Audit verdict: GO) · **HEAD:** `2c503fd`

## Task Checklist

- [x] **Lane opened** — worktree off `main` @ `8c927dd`, assets linked, branch pinned from `rev-parse`.
  - ⚠ `jira_feed.py start --key SCC-125` returned **exit 2: "SCC-125 is a Subtask - start the
    parent it belongs to."** The parent SCC-116 is already `In Progress`, which is the state the
    seam wants. SCC-124 ran this identical shape end to end. Proceeded on that precedent; the
    formal Subtask rule is what the open SCC-119 lane is building, and is not this task's to fix.
- [x] **Plan written and audited** — Full audit, GO, three findings all dispositioned in the plan.
- [x] **RED seen first** on both instruments, output pasted below.
- [x] **GREEN** — step-01 rewritten; `build_pack` water-fills its budget.
- [x] **Cache parity** — byte-copied master → `.claude/`, verified mechanically by the guard.
  - Deliberately **not** via `/smh-sync-agents`: the sync engine and its manifest are both in the
    live SCC-135 lane's file set, and a sync run would have touched surfaces that lane owns.
- [x] **Full gate green, bare.**
- [x] **Review gate** — `/smh-code-review`, verdict below.
  - ⚠ The clean-room hunt found **two regressions and one vacuous guard** in the work above; all
    were fixed and the gate re-run. The pre-fix tree would have been a FAIL.
  - ⚠ **Mid-review, my shell's working directory silently reverted to the shared checkout** (on
    `main`) after a 120 s command was backgrounded, so a handful of relative-path verification
    commands measured the wrong tree — one reported `103/103` from `main` as if it were this lane.
    Caught by the case count not matching. Nothing was written to `main` (a stray `git stash` there
    found a clean tree and created nothing), the lane is intact, and **every gate result recorded
    below was re-run from an explicit absolute path.**

## Evidence

### A1–A6 · the transplanted prompt text — `test_review_engine.py`

The guard is that file's self-proving design: each check pins a **relationship** (an anchored line,
a table row, an exact clause), and ships a counter-example the test mutates in and requires the
check to reject. A check that survives its own negation is reported as a failure.

**RED — before the rewrite (bare):**
```
$ python3 .agents/scripts/tests/test_review_engine.py
-- 236/323 passed --
FAILED: step-01: the hunter contract binds hunter lenses, now and later, ^ counter-example applies,
^ counter-example is rejected, step-01: Gate 1 is a reachability proof, ... step-01: the recall cost
of a worthiness gate is recorded, ^ counter-example applies, ^ counter-example is rejected
```
29 of the 30 new checks failed, ×3 cases each (the check, "counter-example applies",
"counter-example is rejected") = 87 failures.

⚠ **One of the 30 was already green and is a characterization check, not a red-then-green.**
`the pack is a starting point, not the search space` was already in step-01 before this task. It is
kept because acceptance item A5 requires it to hold, but it never failed and is reported as
characterization rather than dressed up as proof. Everything else here was seen red first.

**Intermediate RED (worth recording — the guard caught the author).** After the rewrite, three
checks still failed:
```
[FAIL] step-01: an untraceable finding is speculation, not a finding
[FAIL]   ^ counter-example applies: 'it is NOT a finding — it is speculation' not present
[FAIL] step-01: the blind lens never lowers the bar to compensate
[FAIL] step-01: critical requires an exact failure scenario
```
Not a content failure — markdown reflow had split each pinned phrase across two lines. Fixed by
reflowing the prose so each stays contiguous. Recorded because it is exactly the failure mode the
"read WHICH line raised" discipline exists for: three reds that looked like missing rules.

**GREEN:**
```
$ python3 .agents/scripts/tests/test_review_engine.py
-- 323/323 passed --      (389/389 after the review added 23 routing + precedence checks)
```

⚠ **323/323 was not enough, and the review proved it.** Those rows pinned the prose describing the
hunter/auditor split but nothing that *routes* it, so a step-01 mutated to give every lens both
blocks still scored a clean 323/323. The rows added afterward bind the `How` cells, the routing
sentence and the assembly convention; all six mutations now fail the guard, individually and
combined. Recorded here rather than in the review section alone, because the honest reading of the
first GREEN is *"the guard did not yet cover the acceptance items it claimed to."*

### A7 · the pack budget — `test_evidence_extract.py`

Fixture: two oversized files (400 × 60-char lines each) then one small file last.

**RED:**
```
[FAIL] pack: every packed file keeps its header when the char cap bites: headers=['hog/first.py']
[FAIL] pack: the file packed LAST is not starved by the ones before it: the last file lost its
       whole body to earlier files
[FAIL] pack: two oversized files each keep a fair share of the budget: first=216 lines second=0 lines
[FAIL] pack: a share-truncated file says how much of it is shown: 0 truncation notice(s) for 2 cut files
-- 105/109 passed --
```
`first=216 second=0`, one header out of three — SCC-124's B2 meta-finding reproduced exactly.
The two counter-examples (total cap still holds; fixture really exceeds the budget) passed
throughout, so the red is the behavior and not the fixture.

**GREEN:**
```
$ python3 .agents/scripts/tests/test_evidence_extract.py
-- 109/109 passed --      (115/115 after the review added the F1/F2 regression cases)
```

⚠ **The first GREEN hid two regressions the review then found** — a one-line file packed as an
empty fence (F1) and roughly half the budget rounded away unspent (F2). Both are now covered:

```
F1/F2 repro, fixed code:  ### dist/bundle.js (showing part of line 1 of 1)
                          ### src/plain.py   (showing first 122 of 400)
                          empty fence: False · fences balanced: True · budget used 16000/16000
                          (was 8051/16000 with one file emitted as an empty fence)
```

⚠ **A pre-existing control changed, deliberately.** The single-big-file case asserted
`len(out.strip()) >= 16000`. That exact-byte equality was an artifact of the old `[:16000]` slice,
not the contract: line-boundary trimming lands just under the cap (15947). The control now asserts
the intent directly — the **char** cap bit, provable only by the file being cut below the 400-line
cap that would otherwise bound it. The reason is written beside the check, not just here.

### A8 · the whole gate, bare

```
python3 .agents/scripts/tests/run_all.py                 -> 21/21 files, 1262/1262 cases; exit 0
python3 .agents/scripts/workflow_lint.py --toolkit-only  -> 0 errors, 0 warnings, 8 info; exit 0
python3 -m py_compile (the 3 changed .py files)          -> OK
```
Case count 1091 → 1187 (+90 engine, +6 extractor) → **1262** after the review's fixes (+69 engine
routing/precedence, +6 extractor regression). Both gates run **bare** — piping one would have
reported the pipe's exit code, not the gate's. Final figures measured at `06c3b1e`, from an
absolute path, after the cwd incident noted in the checklist.

**SOP currency, with a positive control rather than an assumption:**
```
--paths <commit-1 set>  (skills + tests)          -> exit 0, silent — owes nothing
--paths <commit-2 set>, no [sop-ok] in message    -> exit 1, "Commit rejected." — the gate has teeth
```
`[sop-ok]` rides commit 2 only. It is the honest call: the SOP's own row for `evidence_extract.py`
says *"you never type it"* — no hook calls it and no operator invokes it — so no usage surface
moved. Scoping it to one commit keeps the record precise about which change claimed the exemption.

## Code Review (2026-08-12)

```
Verdict: PASS @ 06c3b1e
```
Suite evidence measured at the same sha: `run_all.py` 21/21 files, **1262/1262** cases, exit 0.

**Scope:** the five files this task owns, base `8c927dd`, after absorbing `origin/main` (`b3cdb99`).
**Method:** clean-room adversarial hunt in a subagent with zero conversation context (Opus, diff
first, artifacts only afterward) · acceptance audit against the Step 1 list · the command-centre
gate · `/smh-clean-code-audit` · plus a mutation sweep re-running the reviewer's own counter-tests.

**The review found real defects, including two regressions and one vacuous guard. All are fixed.**
This verdict is PASS on the *fixed* tree; it would have been FAIL on the tree that was reviewed —
`19` findings, `4` of them important enough to block. Nothing was dismissed for convenience.

### Findings

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| F1 | `evidence_extract.py:795` | **important** | A file whose first line exceeds its share (minified JS, a lock file, a base64 URI — all in `_TEXT_EXTENSIONS`) kept **zero** whole lines and rendered a header over an empty fence, telling the lens the file is empty. A **regression**: the old blob-slice at least handed over a prefix. | **applied** — a one-line file now degrades to a marked partial line (`showing part of line 1 of N`); a block that cannot fund even that is dropped with a note rather than emitted empty |
| F2 | `evidence_extract.py:786` | **important** | Water-filling on block size, but spending in whole-line increments, left the difference unallocated: the reviewer's repro used **8,051 of 16,000 chars** while the file being cut needed them. The docstring's "only the distribution changes" was false in that case. | **applied** — allocation now runs smallest-block-first and carries the residue forward, so the biggest file is served last with everything the others did not spend. Same repro now uses **16,000/16,000** |
| F3 | `test_review_engine.py` | **important** | **The guard was vacuous for A1/A2.** It pinned the prose *describing* the hunter/auditor split but nothing that *routes* it. The reviewer mutated step-01 to delete the hunter contract from the Edge Case Hunter's wiring, prime both auditors, and deny the asymmetry outright — **323/323 still passed.** | **applied** — 23 new rows bind the `How` cells, the routing sentence and the assembly convention. All six mutations now fail the guard, individually and combined |
| F4 | `step-01-review.md:13` | **important** | `## The evidence pack — repo-access lenses only` contradicted its own table: the Acceptance Auditor has no repo access yet was marked primed, and was handed an instruction ("verify against the live files in `REPO`") it cannot execute. | **applied** — the Acceptance Auditor is `**never** — cannot verify it`, excluded for a reason distinct from the Blind Hunter's. The heading is now true of the set it names |
| F5 | `step-01-review.md` vs the two `bmad-*` skills | **important** | The contract is stacked on vendor skills that instruct the opposite: one demands a minimum finding count and treats zero as suspicious (vs "when in doubt, DROP"); the other mandates a fixed four-field JSON shape with no severity and forbids judgment — so the Edge Case Hunter could never emit a `critical`, and triage maps unlabelled → `suggestion` → never gates. | **applied** — a new precedence section resolves all three collisions with the exact text to append. The vendor skills are still not edited |
| F6 | `test_evidence_extract.py:358` | suggestion | The changed control kept a cap but lost its **lower** bound, so a future bug emitting one line per file would stay green. | **applied** — restored as `15000 < len <= 16000` |
| F8 | `evidence_extract.py:783` | suggestion | On a six-file set every file gets a ~2.6k share of which header+context can be a third, so each lands a preamble rather than a readable extent. Real trade-off; the docstring argued the change as a pure win. | **applied** — the cost is now stated in the code comment and here |
| F9 | `step-01-review.md` | suggestion | Prompt text and third-person orchestrator commentary were interleaved with no marker. Append everything → the lens reads narration about itself; append only blockquotes → **the entire auditor rubric is orphaned**, since its operative rules were unquoted. | **applied** — an explicit assembly convention, and the auditor rules now also exist as second-person prompt text that actually reaches the lens |
| F10 | `step-01-review.md:99` | suggestion | `### Author intent` sat inside the hunter contract, but no hunter ever receives a spec — only the Acceptance Auditor does, and it was excluded from that section. Dead text as placed. | **applied** — promoted to a shared rubric both contracts append, and its trigger widened to the diff's own comments and docstrings, which a hunter *does* have |
| F11 | `step-01-review.md:17,139` | suggestion | "Neither gets the other's" while both auditor prompts said "use the severity rubric above" — a rubric inside the hunter contract. | **applied** — same promotion fixes it; the shared rubric is explicitly appended to both |
| F14 | `step-01-review.md:159` | nitpick | "+38.6 s **of that** [+33.0 s]" asserts a subset relation between a larger and a smaller number. Both figures are real but they are different measures (per-lens delta vs wall-clock delta). It is prompt text an agent reads. | **applied** — reworded to "+38.6 s slower … against a +33.0 s wall-clock delta" |
| F15 | `step-01-review.md:163` | nitpick | The new `## No noise filter` heading was inserted above the subagent-fallback paragraph and swallowed it into an unrelated section. | **applied** — moved under `## When a lens cannot be launched, or fails` |
| F16 | `step-01-review.md:22` | nitpick | "binds by role … inherits without an edit here" was false — there is no role column; a new hunter inherits only by editing its `How` cell in this very file. | **applied** — reworded to say the row *is* the wiring |
| F18 | `evidence_extract.py:807` | nitpick | The trailing `[:_PACK_MAX_CHARS]` could cut mid-block and undo the whole-line guarantee, in the one case it fires. | **applied** — deleted; every block is measured against its own share, so the bound holds by construction |
| F13 | worktree | nitpick | Uncommitted work + untracked artifacts at review time; the added docstring narrated the change rather than stating a constraint. | **applied** — rewritten as a constraint; all work committed |
| F19 | plan | nitpick | Plan A7 described a fixture shape that was not shipped, and the self-audit claimed it had verified every existing pack assertion when it had missed the one that changed. | **applied** — both corrected **in place with the error left visible**, not edited away |
| F7 · F17 · F12 | — | — | Reviewer confirmed the four new pack assertions are genuinely red on old code, that counter-example hygiene is clean, and flagged rationale stated in three places. | **F7/F17 no action; F12 dismissed** — each copy serves a different reader (code states the constraint, test states what the fixture reproduces, plan states the acceptance item) |

**The highest-value question, and the reviewer's answer.** I changed a pre-existing assertion, which
is exactly how a red gets made to pass. The reviewer ran the **final** test file against the
**pre-change** `evidence_extract.py` and got `104/109` — the replacement is **red on the old code,
for the right reason**: the old code's label said "showing first 400 of 450" while silently slicing
the body, so the label lied, and the new assertion catches that. Not a weakened guard. My own RED
block below records `105/109`, which understates the evidence; the fifth failure is the changed
control, and it is the strongest single proof that the change was legitimate.

### Gate results

| Gate | Output |
|---|---|
| Enforcement suite | `21/21 files passed`, **1262/1262** cases, exit 0 (bare) |
| Toolkit lint | `-- 0 error(s), 0 warning(s), 8 info --`, exit 0 (bare) |
| RED assertions re-run | engine `389/389`, extractor `115/115` |
| `py_compile` | OK, 3 changed `.py` |
| SOP currency | exit **1** without the marker (gate proven armed); `[sop-ok]` on the one commit that earns it |
| Link + anchor | 0 markdown links in the 2 changed docs; `step-02-verify.md` reference resolved by hand |
| Door parity | n/a — no command added, renamed or deleted |
| lint / types | not applicable to this repo (no venv, no ruff, no tsc) |

### Acceptance matrix

| Item | Proving assertion | Result |
|---|---|---|
| A1 FP gates on hunters only | 10 `CHECKS` rows + the wiring rows | ✅ |
| A2 auditors exempt, adapted rubrics | 5 prose rows + 3 prompt-text rows + 2 wiring rows | ✅ |
| A3 rubric, five moves, author intent | 7 rows incl. move 5 and the shared-rubric routing | ✅ |
| A4 pack to repo-access lenses only | 5 rows incl. both table cells and both exclusion reasons | ✅ |
| A5 starting point, not search space | 1 row | ✅ *characterization — already true pre-change* |
| A6 no noise filter | 3 rows incl. the recall figures | ✅ |
| A7 pack budget divided | 10 extractor cases, RED→GREEN, plus the F1/F2 regressions | ✅ |
| A8 cache parity + gate green | byte-parity check + the table above | ✅ |

No diff content falls outside the list.

### Step 0.7 — re-derivation against current `main`

1. **Nothing this diff references moved.** `step-02-verify.md`, both skill INDEXes and both `bmad-*`
   hunter skills all still resolve; verified by existence check, not assumption.
2. **True overlap: zero.** `origin/main` gained 28 files from SCC-135; `grep -Fxf` against my 5
   returns nothing, and `merge-tree` produced a clean tree. Absorbed as `b3cdb99`.
3. **Landing order.** `origin/main` carries SCC-135. Local `main` is **7 commits further** — SCC-119
   merged but **unpushed**. I absorbed `origin/main` deliberately, not local `main`: pulling another
   team's unpublished close-out into this lane would make this work depend on commits that are not
   public. Zero overlap either way, so no ordering constraint — but it means this lane's suite does
   not include SCC-119's tests, and the **combined** tree is first measured by the close-out's own
   gate. That is the contract, stated rather than discovered.

### Clean-Code Gate — PASS

**Machine floor**
- run_all.py : PASS — 21/21 files, 1262 cases, exit 0
- workflow_lint : PASS — 0 errors, 0 warnings, 8 info
- sop_currency : PASS — refuses without `[sop-ok]` (exit 1), which the one qualifying commit carries
- py_compile : PASS — 3 files
- link + anchor : PASS — 0 links, reference resolved manually
- door parity : n-a — no command touched
- lint / types : not applicable to this repo (no venv, no ruff, no tsc)

**Findings**

| # | file:line | Severity | Category | Finding | Disposition |
|---|---|---|---|---|---|
| 1 | `evidence_extract.py:718` | CONCERNS | comment-contract | extracted helper carried rationale but no ticket provenance | applied |
| 2 | `.claude/skills/…/step-01-review.md` | — | generated-files | cache updated by byte-copy, not `/smh-sync-agents` | **dismissed** — the engine is a hand-authored skill, its cache carries no `GENERATED` banner, the manifest is a name list already containing it, and byte-parity is enforced mechanically by the guard. A sync run would also have touched surfaces the then-live SCC-135 lane owned |

No secrets, no debug output, no commented-out code, no bare `except`, no absolute paths, no bare
`python`.

## Your Actions

1. **Review and close out** — `/smh-close-task-merge-tree` (invoking it is the merge sign-off).
   The lane is pushed and clean; the close-out re-runs the gate on the merged tree.
2. ⚠️ **The ticket is still `To Do`, and that is the SCC-119 defect, not an oversight.**
   `jira_feed.py start --key SCC-125` returns exit 2 for every Subtask, and `post-commit` writes its
   marker only on exit 0, so the lane re-hit the board on every commit with both streams swallowed.
   SCC-119 fixed exactly this and is merged on local `main` but **unpushed**; this lane predates it.
   The close-out moves the ticket to `Done` regardless.
3. **For the epic (SCC-128 or a follow-on), not for this lane:** the SCC-116 spec's shorthand
   *"pack the repo-access lenses only"* assumed the Blind Hunter was the only lens without repo
   access. The Acceptance Auditor has none either. The operative rule was implemented and both
   exclusions are now reasoned separately, but the spec sentence should be corrected at the source.

