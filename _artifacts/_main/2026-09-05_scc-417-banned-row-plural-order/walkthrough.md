---
IsArtifact: true
ArtifactMetadata:
  title: "SCC-417 — The banned-row gate catches 'your call' in either order, the plural, and another board's tickets"
  type: walkthrough
  date: 2026-09-05
---

# Walkthrough — SCC-417

**Ticket:** [SCC-417](https://sudo-command.atlassian.net/browse/SCC-417) (subtask of SCC-411, the September rolling ticket) · **Lane:** `chore/SCC-417-banned-row-plural-order` off `origin/main` @ `b029aeff` · **Shipping SHA:** `e0027c49` (the planned code at `df805f16`; the review's fixes at `725cd738` and `e0027c49`) · **Plan:** [implementation_plan.md](implementation_plan.md) (approved 2026-09-05 against `567d3040`, recorded at `df805f16`) · **Mutants:** [mutants.json](mutants.json) · **Suite receipt:** [gates/suite.json](gates/suite.json) · **PR:** [#178](https://github.com/sudomadhatter/Sudo_Hatter_Command/pull/178)

On 2026-09-05 `jira_feed.py finish` held SCC-416 at Review Required on one `## Your Actions` row that read "on your call — its own AVCH tickets", and `check-actions` printed no banner: the entry meant to catch a ticket decision handed to the operator required "ticket" BEFORE "your call" and never matched the plural, and no entry knew a row that files work as another board's tickets. This lane makes the gate see all three shapes. The your-call entry is now one entry with both orders and `tickets?`, the same 40-character window on each arm; a seventh entry catches `its/their own <BOARD> tickets` with a case-sensitive project token, because the list compiles under `re.I` and "its own two tickets" is an honest row. The verbatim SCC-416 row went in RED first and is now flagged. The review then found, and reproduced, two more things: three decisions inside the new regexes could be reverted without any case noticing, and the same row with the key in backticks or bold — the house style — still slipped through, which turned out to be the reader's defect rather than one entry's, since every entry that joins two words was blind to markup between them. Both were fixed in the lane before the verdict: five more pins and five more mutants, and one line in `banned_action_rows` that flattens inline markup in the text the patterns see, so the shipped regexes are exactly what the plan approved. Seven near-miss rows pin where each widening stops, ten code-derived mutants each die by their named case, and the shipped list produces zero new hits and loses none across all 194 tracked walkthroughs with a `## Your Actions` section. The SOP passage that tells the operator which row classes the gate refuses names the fourth class in the same commit as the code.

## Task Checklist

- [x] Plan written and self-audited GO (three findings baked in); the operator's `approved` recorded in the plan (given against `567d3040`, recorded at `df805f16`).
- [x] RED: the verbatim SCC-416 row as B5.4x and three single-shape B11 pins, seen red on the unfixed tree — `-- 89/93 passed --`, exactly the four expected failures; the six B12 near-miss rows were green on the unfixed tree, as designed (they guard the widening, they do not motivate it).
- [x] GREEN: the your-call entry rewritten for both orders and the plural (§2.1); the another-board's entry added last (§2.2) — `-- 93/93 passed --` filtered, `-- 535/535 passed --` for the whole file, at `df805f16`.
- [x] Negative controls: B5 (7 real operator calls), B10 (4 noun-sense rows) and B12 (near-misses) green; origin/main's list versus the shipped list over the corpus: **0 new hits, 0 lost, 194 walkthroughs**.
- [x] Revert-proof: five mutants declared and swept 5/5 at `df805f16`; after the review, ten mutants swept **10/10 killed by their declared case**, restore verified, at `725cd738` and again at `e0027c49`.
- [x] SOP currency: the `## Your Actions` passage in [workflows_testing_SOP.md](../../../docs/_scc_sops_prds/workflows_testing_SOP.md) names the fourth refused class; one changelog row, newest first; no `[sop-ok]` on the code commit. The two review commits carry `[sop-ok]` with their reason (they widen a class the SOP already names; nothing is used differently).
  - The changelog's newest row (SCC-414) had been written as a bullet with middle-dot separators directly under the table header, which ends the table there; it is the row it meant to be now. Same file, one line, in this lane's diff.
- [x] Review gate (`/smh-code-review`, five lenses fan-out + the verify wave): 36 findings (31 from the lenses, 5 compound), 23 real and applied, 13 dismissed by name — see `## Code Review`.
  - Fixed in the lane at `725cd738`: the reversed arm's plural (R2), the forward arm's window (R3), `their` (R4) and the singular (M10) each pinned; the B11 create/mint row back to one entry (R5); the plan's `## Approval` and §2.2 counts, and INDEX row 23, stated exactly (R6–R8); a first, per-entry markup tolerance (R1).
  - Fixed at `e0027c49`: the Compound Synthesis role showed R1 had patched a reader defect at one regex — the creation and fold entries were blind to the same markup, and R1 relabelled a bolded creation row under the wrong reason. `banned_action_rows` now flattens inline markup before the pattern walk (R9); the another-board's entry is the approved regex again; two more B11 pins; M6 re-aimed.
- [x] Records: [INDEX.md:23](../../../.agents/scripts/INDEX.md) no longer says `--strict-actions` "ships disarmed"; the depth-3 `_artifacts/_main/INDEX.md` row for this folder added (`test_check_maps.py` F2 had gone red on the missing row: `34/35` → `35/35`).

## Evidence

### Acceptance matrix

| Row | Observable | Proof at `e0027c49` |
|---|---|---|
| A | the verbatim SCC-416 row is flagged by `check-actions` | B5.4x: `[FAIL]` on the unfixed tree, `[PASS]` after §2.1 (RED/GREEN pastes below); the auditor's run of `check-actions` over the `604a12b0` walkthrough: exit 1, banner `hands a ticket decision to the operator (matched: 'your call - its own AVCH tickets')` |
| B | "ticket"/"tickets" and "your call" are flagged in either order | B11 `tickets (plural) + your call`, `your call + ticket (reversed)` and `tickets (plural) + your call, reversed`: RED then GREEN; M1 (reversed arm dropped), M2 (plural dropped on both arms) and M7 (plural dropped on the reversed arm only) killed by exactly those cases |
| C | a row naming another board's tickets as the home is flagged | B11 `another board's tickets as the home`, `…key in backticks`, `…bold around own..ticket`, `…plural owner`: RED then GREEN; M3 (entry deleted), M6 (the reader's markup flattening removed), M9 (`their` dropped), M10 (singular dropped) killed by them |
| D | no honest row is newly flagged | B12.1–B12.7 green; B5 (7) and B10 (4) unchanged; origin/main's list vs the shipped list: `194 walkthrough(s)`, `NEW hits: 0; LOST hits: 0`; M4 (case-sensitivity dropped) killed by B12.5, M5 (reversed window 40 → 400) by B12.6, M8 (forward window 40 → 400) by B12.7 |
| E | each widening is revert-proved | `mutation_sweep.py` @ `e0027c49`: `10/10 killed by their declared case`, `restore verified: bytes match` |
| F | the enforcement suite is green at the shipping sha | `gates/suite.json`: `pass @ e0027c49`, `79/79 files passed`, 26.9 s · `workflow_lint.py --toolkit-only` → `0 error(s), 0 warning(s), 8 info` |

### RED — the unfixed tree, `python3 .agents/scripts/tests/test_jira_feed.py --case "legacy B"`

```
[FAIL] B5.4x · a REAL banned row from the same corpus IS flagged: **AviationChat, after recovery, on your call — its own AVCH tickets, none of it ...
[FAIL] B11 · the 'tickets (plural) + your call' shape is flagged on its own: if only a multi-shape row covers this pattern, deleting the pattern is invisible: Whether the residue gets its own tickets is your call
[FAIL] B11 · the 'your call + ticket (reversed)' shape is flagged on its own: if only a multi-shape row covers this pattern, deleting the pattern is invisible: Your call whether the residue becomes a ticket
[FAIL] B11 · the 'another board's tickets as the home' shape is flagged on its own: if only a multi-shape row covers this pattern, deleting the pattern is invisible: That work is AviationChat's, on its own AVCH tickets
-- 89/93 passed --
FAILED: B5.4x · a REAL banned row from the same corpus IS flagged, B11 · the 'tickets (plural) + your call' shape is flagged on its own, ...
```

(B12.1–B12.6 `[PASS]` on the same run: the near-misses are green before the widening, as they must be.)

### GREEN — after §2.1 and §2.2 (`df805f16`), then after each review commit

```
$ python3 .agents/scripts/tests/test_jira_feed.py --case "legacy B"      # df805f16
-- 93/93 passed --
$ python3 .agents/scripts/tests/test_jira_feed.py                        # df805f16
-- 535/535 passed --
$ python3 .agents/scripts/tests/test_jira_feed.py --case "legacy B"      # 725cd738 (+4 B11, +1 B12)
-- 98/98 passed --
$ python3 .agents/scripts/tests/test_jira_feed.py --case "legacy B"      # e0027c49 (+2 B11)
-- 100/100 passed --
$ python3 .agents/scripts/tests/test_jira_feed.py                        # e0027c49
-- 542/542 passed --
```

The review's own RED: each of the four regex-pin gaps was reproduced by an in-memory mutant that left the `df805f16` suite green (reversed arm singular-only; forward window 40 → 200; `their` dropped; another-board's plural-only), and the markup gap by live rows returning `[]` from `banned_action_rows` — "its own `AVCH` tickets", "its **own AVCH ticket**", and then, from the compound role, "**Mint** its own AVCH key" and "into **AVCH-54**", which R1 had not touched. The pins added at `725cd738` and `e0027c49` are the rows that turn those red; the sweep below is the proof.

### The revert-proof — `python3 .agents/scripts/mutation_sweep.py --table _artifacts/_main/2026-09-05_scc-417-banned-row-plural-order/mutants.json --repo .`

At `df805f16`, the five planned mutants: `5/5 killed by their declared case`, restore verified. At `725cd738`, ten: `10/10`. At `e0027c49`, the ten re-anchored on the approved regex text and the reader line:

```
-- sweep: 10 mutant(s) over 1 file(s) @ e0027c49 --
KILLED    M1
            KILLED by your call + ticket (reversed)
KILLED    M2
            KILLED by tickets (plural) + your call
KILLED    M3
            KILLED by another board's tickets as the home
KILLED    M4
            KILLED by B12.5
KILLED    M5
            KILLED by B12.6
KILLED    M6
            KILLED by another board's tickets, key in backticks
KILLED    M7
            KILLED by tickets (plural) + your call, reversed
KILLED    M8
            KILLED by B12.7
KILLED    M9
            KILLED by another board's tickets, plural owner
KILLED    M10
            KILLED by another board's ticket, bold around own..ticket
-- restore verified: bytes match, nothing was committed, and `git diff --quiet e0027c49` is clean --
-- sweep clean: 10/10 killed by their declared case --
```

| Mutant | Decision mutated | Named case |
|---|---|---|
| M1 | NARROW: drop the reversed arm | B11 `your call + ticket (reversed)` |
| M2 | NARROW: drop the plural on both arms | B11 `tickets (plural) + your call` |
| M3 | DELETE the another-board's entry | B11 `another board's tickets as the home` |
| M4 | WIDEN: drop the scoped `(?-i:…)` | B12.5 "its own two tickets" |
| M5 | WIDEN: reversed arm's window 40 → 400 | B12.6 (85 characters apart) |
| M6 | REMOVE the reader's markup flattening (review R1, re-aimed by R9) | B11 `another board's tickets, key in backticks` (the bold-verb and bold-key pins die with it) |
| M7 | NARROW: drop the plural on the reversed arm only (review R2) | B11 `tickets (plural) + your call, reversed` |
| M8 | WIDEN: forward arm's window 40 → 400 (review R3) | B12.7 (107 characters apart) |
| M9 | NARROW: drop `their` (review R4) | B11 `another board's tickets, plural owner` |
| M10 | NARROW: another-board's entry to the plural only | B11 `another board's ticket, bold around own..ticket` |

### The corpus — origin/main's `_BANNED_PATTERNS` versus the shipped list

The definitive measurement loads origin/main's copy of `jira_feed.py` as a module and runs both lists through `banned_action_rows` over every tracked `*walkthrough*.md` that `jira_feed.open_actions` reads as carrying a `## Your Actions` section (a read-only probe in the session scratchpad; per the SCC-145 ruling, sweep scripts stay out of the tree). Re-run at `e0027c49`:

```
origin/main list: 6 entries; shipped list: 7 entries
-- corpus: 194 walkthrough(s) with a ## Your Actions section --
-- files with a banned row: origin/main 3, shipped 3 --
-- NEW hits under the shipped list: 0; LOST hits: 0 --
```

The plan-time probe (candidates swapped in over the live list; 6 must-flag rows, 14 must-not-flag rows — the six near-misses, four of the seven B5 rows, the four B10 rows; the suite itself runs all seven) measured the same 0 new hits before any edit, and again at `df805f16`. The Compound Synthesis role's own measurement (246 files with the section as it counted them, 67 open rows): 0 new and 0 re-reasoned under every markup-handling shape it tried, and B12.5 ("its own two tickets") holds under all of them.

### The floor at the shipping sha

- `python3 .agents/scripts/gate_receipt.py run --task SCC-417 --gate suite --root <this folder> --cwd <this worktree> -- python3 .agents/scripts/tests/run_all.py` → `[PASS] suite exit=0 26.9s @ e0027c49`, `79/79 files passed` ([gates/suite.json](gates/suite.json); the `[DIRTY TREE]` mark names the sandbox's `.claude/*` mount points and this walkthrough, nothing outside `_artifacts/`)
- `python3 .agents/scripts/workflow_lint.py --toolkit-only` → `-- 0 error(s), 0 warning(s), 8 info --`
- `python3 .agents/scripts/sop_currency.py --paths <changed> --message …` → exit 0, silent, on all three commits (code commit: the SOP and its changelog moved with the code; the two review commits: `[sop-ok]`, reason in the body)
- `python3 .agents/scripts/check_links.py --base origin/main` → `7 markdown file(s), 166 path claim(s) checked`; 2 unresolved, both PRE-EXISTING rows outside this diff (`workflows_testing_SOP.md:4067`, `..._changelog.md:28`) naming `.claude/settings.local.json`, a gitignored per-machine file (`.gitignore:58`) that is absent on this machine (inside the sandbox the same run reads `clean`, because the sandbox mounts a device at that path); 0 dead claims introduced by this diff, 0 bad anchors
- `python3 .agents/scripts/tests/test_check_maps.py` → `-- 35/35 passed --` with the INDEX row
- `python3 -m py_compile` on the two edited `.py` files → ok

review-runtime: fan-out

## Code Review (2026-09-05)

Verdict: PASS @ e0027c49
Suite evidence measured on HEAD @ e0027c49 (`gates/suite.json`, 79/79 files, 26.9 s). The lenses hunted the diff at `df805f16`; the survivors were applied in `725cd738` and, after the verify wave's compound finding, `e0027c49` — the sha this verdict names — and the sweep, the suite and the corpus were re-measured there.

review_level: standard — a gate surface (`jira_feed.py`) and a rule surface (the SOP) are in the radius; nothing this diff references moved on `main`.
lens_isolation:  worktree — the repo under review is the lobby itself, so `isolation: "worktree"` gave each repo-reading lens its own copy at `df805f16` (each echoed `git rev-parse --show-toplevel` and HEAD as its first line, and `git status` after: nothing written); the Blind Hunter got no tree
lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na: none
findings:        0 decision · 23 patch · 0 defer   (4 noise-dismissed · 9 relevance kills)
dispositions:    per-lens: blind-hunter=1/1/1 · edge-case-hunter=3/0/0 · literal-correctness-hunter=5/0/1 · acceptance-auditor=8/0/1 · test-adequacy-auditor=5/1/4 · compound=1/2/2
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — `declared_change_set.py diff` at e0027c49 over `origin/main...HEAD`: present, all three lists empty (the `_artifacts/` INDEX row and this walkthrough are carved out on both sides)
severity_floor:  none at e0027c49 — at df805f16 it was CONCERNS (five `important` survivors, all in the patch bucket; one more, the compound finding, at the verify wave); every one was applied before the verdict
notes:           verify wave: ran — Evidence Verifier launched with the dossier (`evidence_extract.py`, 31 packages, joined by index) in its own worktree copy at df805f16 and still running when this record was committed; its per-finding results land in a follow-up artifacts-only commit (every finding it verifies was already reproduced by its lens or by the assessor, as the table says) · compound synthesis ran with the dossier (5 compound findings: 1 applied as R9, 2 dismissed as moot against the patch as actually written, 2 relevance kills) · the Literal-Correctness patch material (15.7 KB) was spilled to the session scratchpad rather than `ARTIFACT_DIR`, because a lens's worktree copy is cut from HEAD and an uncommitted file under `ARTIFACT_DIR` would not have reached it · no lens or role wrote to the tree

**Scope:** `origin/main...HEAD` — `.agents/scripts/jira_feed.py`, its tests, the SOP passage and changelog, two INDEX rows, and this lane's artifacts (10 files, 435 insertions, 8 deletions at `e0027c49`; the code and docs half is 5 files, 86 insertions, 8 deletions).
**Method:** the house engine under fan-out: five lenses in parallel clean contexts (the Blind Hunter starved to the diff text alone), then an Evidence Verifier and a Compound Synthesis role over a programmatic dossier (`evidence_extract.py`, 31 packages), then triage under the assessor ruling of 2026-08-17.

The assessor's line: 36 findings came back (31 from the lenses, 5 compound); 23 were assessed real and applied in two patches (`725cd738`, `e0027c49`); the other 13 were dismissed under the ruling — 4 as noise (one refuted by the mutation sweep's own kill record, three already handled or moot against the patch as written) and 9 as true-but-not-worth-implementing, each named in the table. Calibration worth carrying forward: the four regex-pin gaps were graded anywhere from `nitpick` to `important` across lenses and assessed as one class (a decision in a shipped gate that no case could see reverted); and the one finding that changed the design came from the compound role, not a lens — five lenses each saw the markup miss at the one entry they were pointed at, and only the synthesis asked why the reader let markup through at all.

### Findings

| # | file:line | sev | Failure scenario | src | Disposition |
|---|---|---|---|---|---|
| 1 | `.agents/scripts/jira_feed.py:2160` | important | The key in the house markup — "its own \`AVCH\` tickets", "its **own AVCH ticket**" — passes the another-board's entry; `finish` prints no banner and parks the ticket, the SCC-416 symptom. Reproduced (three live rows → `[]`). | blind+edge+literal | applied @ `725cd738` as a per-entry tolerance (R1), then re-placed in the reader @ `e0027c49` (R9, row 22); two B11 pins; M6 |
| 2 | `.agents/scripts/jira_feed.py:2154` | important | The reversed arm's plural is pinned by no case alone: the SCC-416 row is reversed AND plural but the another-board's entry also catches it, so a reversed-singular mutant left the suite green. Reproduced. | edge+test-adequacy+literal | applied @ `725cd738` — B11 `tickets (plural) + your call, reversed`; M7 |
| 3 | `.agents/scripts/jira_feed.py:2154` | important | The forward arm's 40-character window is pinned by nothing (40 → 400 survived); the plan promised a near-miss on each side and B12 had only the reversed one. Reproduced. | edge+test-adequacy+literal+acceptance | applied @ `725cd738` — B12.7, a forward pair 107 characters apart; M8 |
| 4 | `.agents/scripts/jira_feed.py:2160` | important | `their` in `(?:its\|their)` is exercised by no case; dropping it survived. Reproduced. | test-adequacy+literal | applied @ `725cd738` — B11 `another board's tickets, plural owner`; M9 |
| 5 | `.agents/scripts/jira_feed.py:2160` | important | The another-board's singular `ticket` is pinned by nothing of its own: the only singular row in B11 belongs to the creation entry (first match wins), so a plural-only narrowing survived. Reproduced. | test-adequacy | applied @ `725cd738` — the bold singular pin is the another-board's entry's alone; M10 |
| 6 | `.agents/scripts/tests/test_jira_feed.py:2286` | suggestion | The new entry also matched the B11 create/mint row ("Mint its own AVCH ticket"), voiding that block's one-entry-per-row invariant; entry ORDER is pinned by nothing. | test-adequacy+acceptance | applied @ `725cd738` — the row says "key", the AVCH-58 phrase the creation entry was built on (entry 0 alone again); the ordering half dismissed — relevance leg 1: first-match order changes only the reason line, the refusal is identical |
| 7 | `.agents/scripts/tests/test_jira_feed.py:2339` | nitpick | The B12 comment said the reversed pair sits 80 characters apart; measured 85. | literal+acceptance | applied @ `725cd738` — the comment says 85 and names the forward pair too |
| 8 | `_artifacts/_main/INDEX.md:7` | important | Acceptance F was red at `df805f16`: `test_check_maps.py` F2 on the missing depth-3 row for this folder (`run_all` 76/79 in a clean clone; the other two reds fail identically at `604a12b0` — no github remote, empty `Projects/` submodule — environment). | acceptance | applied @ `725cd738` — the row is committed; receipt `79/79` |
| 9 | `walkthrough.md` | important | Acceptance E had no record at `df805f16`: no walkthrough, no sweep table in the folder. | acceptance | applied — this file; the ten-mutant sweep recorded above |
| 10 | `implementation_plan.md:133` | nitpick | `## Approval` read Pending and Approved in one section and named the wrong sha as the record. | acceptance | applied @ `725cd738` — one state; given against `567d3040`, recorded at `df805f16` |
| 11 | `.agents/scripts/INDEX.md:23` | nitpick | The row said "the shapes run in either order, in the plural" — true of one entry only. | acceptance | applied @ `725cd738` — names which entry widened |
| 12 | `implementation_plan.md:51` | nitpick | §2.2's counts did not add up as written (14 must-not rows vs "every" B5 and B10 control = 17; 6 must-flags unnamed) and the corpus method was unstated. | acceptance | applied (record commit) — counts and method stated exactly; the probe scripts stay out of the tree per SCC-145 |
| 13 | `.agents/scripts/jira_feed.py:2161` | nitpick | The reason "another board's tickets" also fires on the home key ("its own SCC tickets"). Reproduced. | blind | dismissed — relevance leg 1: the row is refused either way; only the banner's phrase differs |
| 14 | `.agents/scripts/tests/test_jira_feed.py:2302` | suggestion | An earlier entry might claim the B11 reversed row, so the reversed arm could be unpinned (confidence 0.6, no repo access). | blind | dismissed — noise: refuted; M1 (reversed arm dropped) is killed by exactly that case in every sweep |
| 15 | `.agents/scripts/jira_feed.py:2156` | suggestion | No test reads the reason strings; a swapped reason is invisible. | test-adequacy | dismissed — relevance: a pin on prose; the refusal does not depend on the phrase |
| 16 | `.agents/scripts/jira_feed.py:2160` | suggestion | Making `own` optional is a widening no near-miss can see. | test-adequacy | dismissed — relevance leg 1: no realistic edit drops the anchor the entry is named for |
| 17 | `.agents/scripts/jira_feed.py:2160` | nitpick | `{2,10}` bounds unpinned in every direction. | test-adequacy | dismissed — relevance leg 1: every board here is 3–4 letters (the lens said so itself) |
| 18 | `.agents/scripts/jira_feed.py:2154` | nitpick | The `\b` anchors are unpinned; "ticketing" would flag without the reversed arm's trailing one. | test-adequacy | dismissed — relevance leg 1: dropping a `\b` is not a realistic edit; "ticketing" measured clean today |
| 19 | `walkthrough.md` | suggestion | The sweep table was not recorded anywhere at `df805f16`. | test-adequacy | dismissed — noise: already handled; this file existed uncommitted when the lens ran |
| 20 | `.agents/scripts/jira_feed.py:2160` | suggestion | Any all-caps word passes the project token: "its own JIRA tickets" / "its own QA tickets" are refused as another board's work. Reproduced. | literal | dismissed — relevance leg 1: 0 hits over 194 walkthroughs and 67 open rows, by two independent measurements; a stoplist is a widening with no measured need |
| 21 | `workflows_testing_SOP_changelog.md:22` | nitpick | The SCC-414 row repair is not in the Declared Change Set wording ("one row"). | acceptance | dismissed — relevance: recorded in the Task Checklist; the declared set is per file and the file is declared |
| 22 | `.agents/scripts/jira_feed.py:2191` (`banned_action_rows`) | important | Markup blindness is the reader's, not one entry's: `_collect` hands every entry the raw markdown, so "**Mint** its own AVCH key" (creation) and "into **AVCH-54**" (fold) returned nothing, and R1's per-entry tolerance turned a bolded creation row into a refusal under the another-board's reason. Reproduced. | compound | applied @ `e0027c49` (R9) — `_INLINE_MARKUP` flattens `` ` ``, `*`, `_` in the text the patterns see, the row is returned verbatim; the another-board's entry is the approved regex again; B11 `create/mint, verb in bold` and `fold into <KEY>, key in bold`; M6 re-aimed at the reader line |
| 23 | `mutants.json` (M3) | suggestion | A tolerance edit would zero M3's anchor and the sweep's uniqueness pre-check would abort the run, so a stale sweep table could ship as evidence. | compound | dismissed — noise: already handled; every anchor was re-set in the same patch and the sweep ran 10/10 at `725cd738` and again at `e0027c49` |
| 24 | `.agents/scripts/jira_feed.py:2160` | suggestion | A key-only tolerance misses the corpus spelling "its **own AVCH ticket**" (bold opening before `own`). | compound | dismissed — noise: moot; R1 already placed the tolerance before `own` (the bold-own pin), and R9 flattens the whole row |
| 25 | `docs/_scc_sops_prds/workflows_testing_SOP.md:1039` | suggestion | The fourth row class is never the banner the operator reads for its own motivating row: a both-shape row prints the your-call reason (first match wins). | compound | dismissed — relevance: the refusal is correct and the banner names a true reason; the SOP promises the row and a why, not which class of several |
| 26 | `.agents/scripts/jira_feed.py:2160` | nitpick | Markup handling multiplies the forms of the all-caps side ("its own **JIRA** tickets") that B12.5 does not guard. | compound | dismissed — relevance leg 1: forward risk only; 0 hits, the same measurement as row 20 |

### Acceptance audit (Step 2)

Imported from the Acceptance Auditor (source `review`) and re-checked at `e0027c49`: rows A–F as in the matrix under `## Evidence`. The auditor's own reproductions: `check-actions` over the `604a12b0` walkthrough refuses with the your-call reason; the three planned B11 shapes match one entry each (`[5]`, `[5]`, `[6]`); the another-board's entry sits last; the SOP passage, changelog row and code share one commit with no `[sop-ok]`; nothing under `.agents/` or `docs/` beyond the five declared files. Its two `not satisfied` rows (E, F) were the record lagging the code by one commit; both are closed (rows 8 and 9 above). Drift: `declared_change_set.py diff` → `undeclared=0 · unimplemented=0 · incomplete=0`.

### Gates (Step 3)

| Gate | Result |
|---|---|
| Enforcement suite | `[PASS] suite exit=0 26.9s @ e0027c49` · `79/79 files passed` · receipt [gates/suite.json](gates/suite.json), stamped after the last code-touching change |
| Toolkit lint | `-- 0 error(s), 0 warning(s), 8 info --` |
| Assertion evidence | `--case "legacy B"` → `-- 100/100 passed --` (the four RED pins, the seven review pins, all named) |
| SOP currency | exit 0 on all three commits: the code commit moved the SOP and changelog with the code; the two review commits carry `[sop-ok]` with the reason (a class the SOP already names, now seen through markup) |
| Link + anchor | `7 markdown file(s), 166 path claim(s) checked`; 2 unresolved, both pre-existing rows naming the gitignored per-machine `.claude/settings.local.json` (absent on this machine; the sandbox mounts a device there, which is why the sandboxed run read clean); 0 introduced by this diff |
| Door parity | n/a — no command added, renamed or deleted |

### Clean-Code Gate — PASS

**Machine floor** (imported from Step 3, not re-run)
- run_all.py       : PASS — 79/79 files, exit 0 @ e0027c49 (receipt)
- workflow_lint    : PASS — 0 errors, 0 warnings
- sop_currency     : PASS — silent exit 0 on all three commits
- py_compile       : PASS — `.agents/scripts/jira_feed.py`, `.agents/scripts/tests/test_jira_feed.py`
- link + anchor    : PASS — 166 claims, 0 dead claims introduced by this diff (2 pre-existing rows name a gitignored per-machine file)
- door parity      : n/a — no commands in the diff
- lint / types     : not applicable to this repo (no venv, no ruff, no tsc)

**Findings**
| # | file:line | Severity | Category | Finding | Disposition |
|---|-----------|----------|----------|---------|-------------|
| — | — | — | comment-contract | Every new block carries `SCC-417:` and its reason; the reader's new lines carry `SCC-417 review:` and the three rows that reproduced it; no `AIDEV-*` note sits in the edited region to invalidate; no TODO; no comment restates the code. The pre-existing creation-entry comment ("All-caps only") is outside this diff and untouched. | none |
| — | — | — | conventions | No command or door changed; the gate ships armed (refused by default) and keeps its exit (`--warn-actions`); artifacts live in the tree; no personal name in any directive; both machines (`python3` here, `python` on the PC, stdlib only, `(?-i:…)` needs ≥ 3.6 and the file already needs ≥ 3.10). | none |

The AI-drift half is Step 1's, imported: the only scope beyond the plan is the review's own patches, each line of which closes a reproduced gap in this lane's gate; the one new module constant (`_INLINE_MARKUP`) has one caller and replaces three character classes in a regex; no new file, nothing re-implemented.

### Step 0.7 — re-derivation

1. Nothing this diff references moved, was renamed or was deleted on `main`: `git diff --name-only b029aeff..origin/main` is empty (0 files landed on `main` since the fork), and every path the diff names — the SOP passage, `INDEX.md`, the Part B test block, `mutation_sweep.py` — resolves at HEAD.
2. True overlap: 0 files; `git merge-tree --write-tree --messages HEAD origin/main` writes tree `de94d936` with no conflict messages; `risk_seam.py classify --repo .` answers `unclassified` (the command centre carries no code graph — the expected answer here).
3. Live sibling lanes: none — `git worktree list` shows the lobby on `main` and this lane only. Landing order: `origin/claude/teaching-edition` (a branch with no worktree here, tip `8b42390f`) also edits the SOP and its changelog; this lane lands first, and if it does not, both changelog rows are kept on absorb.

Changes applied: the review patches at `725cd738` (rows 1–11) and `e0027c49` (row 22), and the record fixes in this commit (row 12). The `## Evidence` totals above are the post-fix runs at `e0027c49`.

## Your Actions

- [x] The merge itself — lands via this branch's PR (#178).
