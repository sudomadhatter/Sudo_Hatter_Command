# SCC-318 — Bugs and Updates, cycle 9 (consolidated lane)

**Lane:** `chore/SCC-318-bugs-cycle-9` · **Riders:** SCC-335, SCC-359, SCC-364
**Plan:** [implementation_plan.md](implementation_plan.md) · **Manifest:** [task.yaml](task.yaml)

Cycle 9's three remaining subtasks, run as ONE lane per `work-consolidation.md` rule 2. Part A
(SCC-334) had already shipped separately under SCC-333 and its key was later deleted from the board.

## What each part was, and what closed it

### SCC-335 — every acli seam decoded with the machine's locale ✅

The one that had already destroyed operator data: it corrupted SCC-318's own description on
2026-08-27. Six `subprocess.run` calls reached `acli` with `text=True` and no `encoding=`, so they
decoded with `locale.getencoding()`. `acli` is a Go binary and always writes UTF-8, so on any box
whose locale is not UTF-8 every description read came back mojibake — and since
`edit --description` **replaces** the whole field, a read-modify-write wrote the mojibake back.
`U+2B50` is lossy that way (UTF-8 `E2 AD 90`; cp1252 has no mapping for `0x90`) and cannot be
recovered from the written text at all.

Pinned all six: `jira_feed.acli` (the seam every verb rides, and the one `task_preflight` imports
rather than duplicating), `label_tasks.acli`, and four sites in `jira_ticket.py`.

The read-back guard was reporting a *mangled* line as a *deleted* line and telling the operator to
"restore the ticket from the text above" — the text above being the damaged copy, so obeying it
made the corruption permanent. It now separates the two by ASCII skeleton, names the codepoints
that changed, and says explicitly not to re-run or hand-edit from the read-back.

### SCC-364 — close-out rewrote a tree it was about to prune ✅

`jira_ticket.py done` does two things: it rewrites the ticket outline **in the tree**, then it
writes the board. `/smh-close-task-merge-tree` called it at Step 4, *after* the merge — where the
lane is merged, the door's own SCC-175 rule bans post-merge commits, and Step 5 prunes the tree. The
file write could never land, and nothing said so, because `done` exits 0 on the board half. So
`main` kept an all-unticked Plan forever while the step's prose claimed the tree was the source.

Fixed with no new code, because `jira_ticket.py` already had both halves: Step 3 now calls
`done --local` (tree only) inside the door's existing "commit this before the PR" window, so the
ticked outline rides the PR; Step 4 calls `describe`, which renders the landed outline to the board
and touches no file.

### SCC-359 — the approval-sha check that can never pass ✅

`/smh-quick-dev` Step 1.5 condition 3 demanded `git log -1 --format=%h -- <plan>` **equal** the sha
on the `— recorded at <sha>` line. `/smh-plan-task` Step 5 requires that line to carry the sha of
the commit that recorded it — unknowable until that commit exists — so the planner writes
`<pending>`, commits, and stamps the sha in a **second** commit. The plan's last touch is therefore
always the stamp, never the recorded sha, and the condition could never pass for a lane that
followed the convention. An agent reading Step 1.5 literally stops a lane the operator has already
approved.

Fixed on the **reader**, because the other remedy is circular: any scheme that records a sha *into*
the plan file changes the plan file, so "last touch equals recorded" cannot hold whichever sha is
chosen. Step 1.5 now falls through to `git diff <recorded>..<last touch> -- <plan>` and passes a
**stamp-only successor** — a diff touching the `— recorded at` line and nothing else. The no-sha
tooth is untouched: a missing operand is still a re-armed gate.

Applied to all three places the contract lives, so writer, reader and law cannot drift apart:
`smh-plan-task.md` Step 5 (what the second commit may contain), `smh-quick-dev.md` Step 1.5 (what
it will accept), `000-PLAN-FIRST-GATE.md` §3 (the law both cite).

**Twin check, answered so nobody repeats the search:** `/cicd-quick-dev` carries **no** approval-sha
box. Grepped `.agents/commands/` for `recorded at`, `git log -1 --format=%h` and "unchanged since" —
the contract appears in exactly three files, all named above. There is no twin to port to.

**A third measurement, produced by this lane itself.** SCC-359 cited SCC-347 and SCC-358. Recording
this lane's own approval reproduced it a third time: `fbd4ac20` recorded, `6126fe6d` stamped, and
the entire delta is one line — `<pending>` → the sha. It is in this branch's history as evidence.

## Constraints and decisions, recorded as they were met

- **SCC-335 is not Windows-only, as its ticket claimed — it is LOCALE-only.** `LC_ALL=C` plus
  `PYTHONUTF8=0` makes `locale.getencoding()` return `US-ASCII` on this Mac (measured), which
  reproduces the live corruption here. The test forces the locale rather than skipping on POSIX: a
  test the author can never watch fail is not a test.
- **Two fixture defects, both the family `test_jira_feed.py` already documents** — *a stub more
  generous than the tool it stands in for cannot fail on the bug it exists to catch.* The stub
  emitted `print(json.dumps(...))`, whose `ensure_ascii=True` default put every non-ASCII character
  on the wire as a pure-ASCII escape, so the first six cases **passed on a bug that was fully
  present**. Measured against the live board: real acli emits raw `e2 9b 94` / `e2 ad 90` and no
  `\uXXXX` escape appears in 7,753 bytes. The stub now writes raw UTF-8 through `sys.stdout.buffer`,
  which also models Go's locale independence.
- **The armed pre-commit encoding gate blocked the first commit, correctly.** Three raw `U+FFFD`
  characters written as test literals; `workflow_lint` cannot tell a deliberate literal from a
  corrupted byte and should not try. Switched to escapes.
- **`CS-19` was already taken** by SCC-357's block, so SCC-364's case block is `CS-23`. Caught by
  running the filter and seeing two blocks match.
- **The old "tree stays the source" sentence is now a reserved marker.** `CS-23 E` fails if Step 4
  carries it again, so the door's explanation of the fix deliberately does not quote it — a comment
  that reproduces the banned string inverts the guard (the CS-16 scar).
- **`[sop-ok]` used once, on the SCC-335 commit**, with the reasoning in the log: nothing about a
  subprocess decode is a usage surface. SCC-364 *does* move one, and stages the SOP with it.

## Task Checklist

Every row is an acceptance step from [implementation_plan.md](implementation_plan.md), with the
assertion that proves it. Pitfalls sit under the task that produced them.

- [x] **B1** — pin `encoding="utf-8"` on `jira_feed.acli()`, the seam every verb rides
  - the pin goes on the PARENT only; `acli` is Go and ignores a locale env pin, so pinning the child would have looked like a fix and changed nothing
- [x] **B2** — the same pin on `label_tasks.py`
- [x] **B3** — the same pin on `jira_ticket.py`'s four `subprocess.run` sites
  - `task_preflight.py` needed no edit: it holds no subprocess of its own and reaches the board through `jira_feed.acli_json`, by stated design
- [x] **B4** — the read-back guard names WHICH characters changed, not only that lines went missing
  - skeletons under 8 characters are not matched, so a genuinely deleted line is never mis-reported as a formatting difference
- [x] **B5** — byte-identity: a read-modify-write that adds no row leaves every pre-existing line unchanged
  - **the fixture lied first.** `print(json.dumps(...))` defaults to `ensure_ascii=True`, so the stub put every non-ASCII character on the wire as an ASCII escape and six cases passed on a bug that was fully present. Measured the live board — real `acli` emits raw `e2 9b 94` / `e2 ad 90`, zero escapes in 7,753 bytes — and rewrote the stub to emit raw UTF-8 through `sys.stdout.buffer`.
  - the armed pre-commit encoding gate blocked the first commit over three literal `U+FFFD` test characters. It was right to: it cannot tell a deliberate literal from a corrupted byte. Switched to `"\ufffd"` escapes.
- [x] **C1** — re-sequence the close-out door: `done --local` before the PR, `describe` after the merge
  - the retired sentence "the tree stays the source" is now a **reserved marker**; CS-23 E fails if Step 4 carries it again, so the door's own explanation deliberately does not quote it
- [x] **C2** — CS-16 D/E stay green (the call moved, it did not leave)
- [x] **C3** — mutation control: deleting `--local` from the door's Step 3 fence turns CS-23 A red
- [x] **D1** — `smh-quick-dev.md` Step 1.5 accepts a stamp-only successor
- [x] **D2** — `smh-plan-task.md` Step 5 states what that second commit may contain
- [x] **D3** — one case pins that the writer and the reader AGREE, across both doors
- [x] **D4** — `000-PLAN-FIRST-GATE.md` carries the same exemption, so law and doors cannot drift
  - `CS-19` was already SCC-357's label; `--case CS-19` matched two blocks. Renumbered to CS-23.

## Evidence

**Measured at `e0d73919` — the sha the lenses reviewed and the sha on the gate receipt. Same value; the review and the evidence describe the same code.**

| # | Acceptance item | The assertion that proves it | Result |
|---|---|---|---|
| B1 | `jira_feed.acli()` decodes UTF-8 whatever the locale | `test_jira_feed.py --case "SCC-335"` A1–A6, run under `LC_ALL=C PYTHONUTF8=0` against a stub emitting raw UTF-8 | PASS |
| B2 | `label_tasks.py` same seam pinned | SCC-335 E1 (AST walk over every `subprocess.run` reaching acli) | PASS |
| B3 | `jira_ticket.py` four sites pinned | SCC-335 E1, same walk — 6 calls reached, 0 unpinned | PASS |
| B4 | the guard names changed CHARACTERS, not lost lines | SCC-335 D1–D4: exit 2, message carries "character" + "encoding" + a `U+XXXX` pair, and does NOT say "restore the ticket" | PASS |
| B5 | byte-identity on a no-row round trip | SCC-335 A5, plus A6 as the anti-vacuity control (the new row did land) | PASS |
| C1 | `done --local` runs BEFORE the PR | CS-23 A/B — position-aware over the door's fenced code: `done --local` at 28287, `gh pr create` at 30358 | PASS |
| C2 | CS-16 D/E still green | full suite, 71/71 files | PASS |
| C3 | deleting `--local` turns CS-23 red | mutation run, captured red, reverted | PASS |
| D1 | Step 1.5 admits the stamp commit | CS-24 A | PASS |
| D2 | Step 5 says what the stamp commit may contain | CS-24 B | PASS |
| D3 | writer and reader agree | CS-24 A/B/C across all three files | PASS |
| D4 | the law carries the same exemption | CS-24 C | PASS |

**Actual totals, pasted:**

```
python3 .agents/scripts/tests/run_all.py
71/71 files passed
[PASS] suite exit=0 85.5s @ e0d73919   (receipt: gates/suite.json)

python3 .agents/scripts/tests/test_jira_feed.py --case "SCC-335"      -- 14/14 passed --
python3 .agents/scripts/tests/test_command_surfaces.py --case "CS-23" --  7/7  passed --
python3 .agents/scripts/tests/test_command_surfaces.py --case "CS-24" --  8/8  passed --
```

**A third live measurement of the SCC-359 defect, produced by this lane itself:** `fbd4ac20`
recorded, `6126fe6d` stamped, delta exactly one line. It joins SCC-347 and SCC-358 in this
branch's history as evidence that the old equality check could never hold for a conforming lane.

## Your Actions

- [x] **The merge itself** — lands via this branch's PR.

- [x] **Verify the SCC-335 fix on the Windows PC — DONE 2026-09-01**, in the SCC-338 pickup sweep
      ([walkthrough](../2026-09-01_SCC-338-pc-pickup/walkthrough.md)). All three commands ran on the
      PC, and the three output lines are below verbatim:

      STEP 1  cp1252
      STEP 2  U+26D4 0 U+2B50 0 U+FFFD 1
      STEP 3  U+26D4 1 U+2B50 1 U+FFFD 0

      Read in order: step 1 confirms this machine's Python really does default to **cp1252**, so it
      IS the box that produced the original corruption and the test is not vacuous. Step 2 is the
      negative control on the exact old line — the two real codepoints are **gone** and a U+FFFD
      replacement character stands where one of them was, which is the bug reproducing live rather
      than being argued about. Step 3 runs the same read through the shipped `jira_feed.acli()`
      seam and both codepoints come back **intact with zero replacements**. That closes acceptance
      A on the machine that caused it. Counts only, never rendered characters, per the warning
      below.

      Original instructions, kept as the record: full copy-paste steps are in
      [SCC-335](https://sudo-command.atlassian.net/browse/SCC-335)'s description under
      **PC VERIFICATION** - three read-only commands, nothing is written to the board.
      Step 1 prints the machine's Python encoding, step 2 is the negative control on the old
      line and must print `U+26D4 0 U+2B50 0`, step 3 runs the shipped seam and must print
      `U+26D4 1 U+2B50 1 U+FFFD 0`. Paste the three output lines back; that closes SCC-335
      acceptance A on the machine that produced the corruption.
      Check the **counts**, never the rendered characters - the PowerShell console mis-renders
      correct UTF-8 and can make mojibake look clean
      (memory `powershell-console-fakes-mojibake`), so an eyeball pass proves nothing.

## Code Review (2026-09-01)

review-runtime: fan-out
Verdict: PASS @ e0d73919
Suite evidence measured at: e0d73919 (clean tree, 71/71, exit 0) — the same sha the lenses reviewed at 86f29f1c plus the review's own fixes; re-run and re-stamped after the last code change.

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none
lens_isolation:  worktree — each repo-reading lens got its own `git worktree add --detach` copy of the repo under review at 86f29f1c; the blind hunter got no tree, its repo access withheld by instruction rather than by sandbox. The builder tree was clean before launch and carried only the builder's own four files after: no lens wrote to it.
dispositions:    per-lens: blind-hunter=8/1/0 · edge-case-hunter=2/0/0 · literal-correctness-hunter=6/0/0 · acceptance-auditor=9/0/0 · test-adequacy-auditor=8/0/0
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — reconciled twice: four generated doors were undeclared at first pass and are now declared, and the review's own 20 edits were declared in a second amendment.

**Scope.** The 20-file diff at 86f29f1c, re-taken after `origin/main` was absorbed. **Method.** Five lenses in parallel, each in its own clean context and its own worktree copy, then assessment, then every survivor fixed in this lane.

**The tail, in one line (operator ruling 2026-08-17):** 34 findings came back, 33 were assessed real and fixed here, 1 was dismissed as superseded by another fix. That survival rate is unusually high and worth saying plainly — the lenses mostly did not speculate, they reproduced. Three of them independently built the same mutant and watched a guard bless it.

**Changes applied: substantial.** Two defects were behaviour-changing and would have shipped.

### Findings

| file:line | severity | failure scenario | disposition |
|---|---|---|---|
| `.agents/commands/smh-close-task-merge-tree.md:396-445` | **critical** | `done --local` writes the outline into the worktree; nothing between it and `gh pr create` commits it, and the line before the PR asserts the branch is already clean and pushed. `main` keeps the unticked outline — the SCC-364 defect relocated, not closed — while Step 4's `describe` reads the ticked *worktree* copy and writes it to the board, so board and branch disagree. Step 5's `git worktree remove` then exits 128 on the dirty tree, after the merge, where this door bans commits. Reproduced end to end in a throwaway repo by two lenses. | applied @ 63a40b90 |
| `.agents/scripts/jira_feed.py:3177` | **important** | A mangled row whose ASCII skeleton is under 8 characters (`⛔ blocked` = 7) is declined by the matcher, then promoted to "confirmed deletion" by `gone = lost − changed`, and handed the retired *"restore the ticket from the text above"* advice — pointed at the damaged copy. SCC-335 acceptance C not delivered for the house's own row shape. Reproduced by three lenses and by the assessor. | applied @ 63a40b90 |
| `.agents/scripts/tests/test_jira_feed.py` (SCC-335 block) | **important** | Regress the acli stub to `print(json.dumps(...))` *and* revert `encoding="utf-8"` — the bug fully present — and eleven behavioural rows pass. Every one of them is load-bearing on a stub property nothing asserted. | applied @ 63a40b90 |
| `.agents/scripts/tests/test_command_surfaces.py` (CS-24) | **important** | Leave `stamp-only successor` in the prose and restore the original unpassable `[ "$LAST" = … ] \|\| exit 1` inside Step 1.5's fence: CS-24 goes 8/8 green on the literal SCC-359 defect. The rows read prose; the bug lives in the fence. | applied @ 63a40b90 |
| `.agents/commands/smh-quick-dev.md` (Step 1.5) | **important** | The new fence printed a diff and left an agent to judge "does this touch only the approval line?" — a boolean replaced by a prose judgment, the shape `cheap-models-rationalize-past-prose` names. A stamp commit carrying a body edit read as legal. | applied @ 63a40b90 |
| `.agents/scripts/tests/test_jira_feed.py` (E1) | **important** | The seam guard missed `universal_newlines=True` (an exact alias for `text=True`), missed `from subprocess import run` entirely, and swept a hardcoded four-file list. A lens got the original defect past it twice. Widening it exposed the same defect in 28 more seams. | applied @ 63a40b90 |
| `.agents/scripts/tests/test_jira_feed.py` (E2) | important | The declared anti-vacuity control was a text grep for `"subprocess.run"`, computed independently of the walk. Break the matcher and E1 passes vacuously with E2 still green. | applied @ 63a40b90 |
| `.agents/scripts/tests/test_command_surfaces.py` (CS-16 D/E) | suggestion | This diff's own explanatory paragraph put the literal `jira_ticket.py done` into the door's prose, making CS-16 D/E satisfiable without any invocation: a lens deleted the entire Step 3 fence and CS-16 stayed 7/7 green. | applied @ 63a40b90 |
| `.agents/scripts/tests/test_jira_ticket.py` (JT-C/JT-D) | suggestion | The whole SCC-364 re-sequencing rests on two prose claims — `describe` writes no file, `done --local` touches no board — and neither was asserted anywhere. JT-D set no `ACLI_BIN` at all. | applied @ 63a40b90 |
| `.agents/scripts/jira_feed.py:3178-3190` | suggestion | Candidates were never consumed, so two lost lines sharing one ASCII skeleton both matched the same surviving line — a real deletion beside a mangled twin reported "nothing was deleted". | applied @ 63a40b90 |
| `.agents/scripts/jira_feed.py:3288` | suggestion | The message whose entire subject is *which characters changed* routed through `ascii_out`, which folds every non-ASCII character to `?`. The two lines the operator must compare printed as `??" Part A` against `???????? Part A`. | applied @ 63a40b90 |
| `.agents/scripts/verdict_receipt.py:146`, `gate_receipt.py:245` (+26 more) | suggestion | The same locale-decode defect outside the acli four. `verdict_receipt` decodes walkthroughs, which are full of `⛔`/`⭐`; `gate_receipt` decodes suite output it writes into a committed receipt. | applied @ 63a40b90 |
| `_artifacts/…/gates/suite.json` | important | Stamped at `a5d4c1fa`, four commits and one `origin/main` absorb behind the tip, asserting `70/70` where the tip is `71/71`. Stale by the repo's own `same_tree` rule. | applied — re-run and re-stamped |
| `_artifacts/…/tickets/` | suggestion | The close-out ticks one outline per rider; only `SCC-364.md` existed, so `load()` would exit 2 on the other three keys. | applied @ 63a40b90 |
| `_artifacts/…/implementation_plan.md` | important | Four generated doors changed and none was declared; the review's own 20 edits then needed declaring too. | applied @ 63a40b90 |
| `_artifacts/…/walkthrough.md` | important | No `## Task Checklist`, no `## Evidence`, no captured RED output — the record `/smh-quick-dev` Step 5 mandates. | applied @ 63a40b90 |
| `.agents/scripts/jira_ticket.py:224` | nitpick | The 14-line comment sat at `try:` level while its statement sat at `try:`+4; and its acli rationale was applied verbatim to two keychain seams that are not acli (`security`, and PowerShell 5.1, which writes an OEM code page). | applied @ 63a40b90 |
| `.agents/scripts/tests/test_jira_feed.py` (E-block comment) | nitpick | The comment claimed `task_preflight.py` was "asserted to STAY that way rather than scanned"; the loop scanned it and asserted nothing of the kind. | applied @ 63a40b90 |
| CS-23 is a markdown offset grep; nothing exercises `done --local` or `describe` at runtime | — | dismissed — superseded by the JT-C/JT-D runtime assertions, which close the substance directly. |

### The one that was mine, not a lens's

Writing the replacement for finding 5, I shipped `grep -qv` as the verdict. **The Mac's `grep` is ugrep, not BSD or GNU grep, and its `-q` with `-v` returns the inverted exit code** — 1 when lines are selected, 0 on empty input. The gate passed the illegal case and stopped the legal one. Caught by running it against three throwaway repos before believing it. It counts now (`grep -vc`), which has one meaning on every grep and on both machines, and `CS-24 G` fails if `-qv` ever comes back. Recorded in the memory store as `agent-shell-grep-is-not-the-gate-grep` (it lives outside this repo, so it takes no link).

### Gates

| Gate | Result |
|---|---|
| Enforcement suite | `71/71 files passed`, exit 0 @ 63a40b90. The 11 `[FAIL]` lines in the log are the tests' own captured negative controls — one is labelled `on purpose`. |
| Toolkit lint | `0 error(s), 0 warning(s), 8 info` — the 8 are UTF-8 BOMs in vendor `testarch-*` commands, untouched by this diff. |
| Assertion evidence | `--case "SCC-335"` 21/21 · `--case "CS-23"` 9/9 · `--case "CS-24"` 12/12 · `--case "CS-16"` 8/8 · `test_jira_ticket.py` 46/46 |
| SOP currency | pass — the SOP records the Step 1.5 change in the same commit |
| Link + anchor | `check_links.py --base origin/main` — clean, 167 path claims |
| Door parity | `sync-agents.ps1 -Status` — clean, every invocable file matches its master |
| `check_maps --depth3-only --strict` | clean (the close-out's own gate) |

### Mutants — every new guard proven to fail

| mutant | result |
|---|---|
| drop `encoding="utf-8"` from `jira_feed.acli` | SCC-335 8/14 — A1–A5 and E1 red |
| regress the stub to `ensure_ascii=True` | SCC-335 F1/F2 red |
| break the AST matcher's module name | SCC-335 E2 red (E1 passes vacuously — the point) |
| add an unpinned `universal_newlines` seam | SCC-335 E1 red |
| delete `--local` from the door's Step 3 **fence** | CS-23 A and B red |
| delete `--local` from the door's **prose** | CS-23 stays green — the fenced projection working |
| delete the new commit fence | CS-23 F and G red |
| restore the unpassable equality inside Step 1.5's fence | CS-24 E and F red |
| rename `stamp-only successor` in Step 1.5 | CS-24 A red, B and C green |
| delete the door's whole Step 3 fence | CS-16 D and E red (were green before this fix) |

### Step 0.7 — re-derivation

1. **Nothing this diff references moved, was renamed, or was deleted on `main`.** `git diff --name-only <merge-base>..origin/main` is empty: the lane's merge-base *is* `origin/main` at `51c47707`, so the lane already contains all of main.
2. **True overlap: none.** The intersection is empty and `git merge-tree --write-tree --messages HEAD origin/main` returned a clean tree (`ae17d585`) with zero conflict messages. The earlier SCC-372 collision was resolved at `a1c3fca8` by regenerating the sync manifest, never hand-merging, and both lanes' SOP rows were verified present.
3. **No sibling lanes are live.** `git worktree list` shows only the main checkout and this lane, so there is no landing-order dependency left.

### Clean-Code Gate

Machine floor imported from the gates above rather than re-run (SCC-146). `py_compile` clean on all 20 changed `.py` files. Comment contract: the three new `⛔`/`⭐` blocks each name the ticket, the measurement and the failure they prevent. Convention: bullets not tables in the declared set, checkbox rows in `## Your Actions`, unfenced roster lines. Diff-scoped — legacy debt in untouched files noted, not gated on. **No findings beyond those in the table above.**
