---
IsArtifact: true
ArtifactMetadata:
  title: SCC-210 — rebalance the cicd close-out (walkthrough)
  type: walkthrough
  date: 2026-08-20
---

review-runtime: fan-out

# SCC-210 — Rebalance the cicd close-out

**Ticket:** [SCC-210](https://sudo-command.atlassian.net/browse/SCC-210) · **Lane:** `chore/SCC-210-close-out-rebalance`
· **Plan:** [implementation_plan.md](implementation_plan.md) (with `## Self-Audit`, verdict GO)
· **Base:** `origin/main` @ `fe0f211` · **Door:** `/smh-close-task-merge-tree`

**What shipped, in one line:** three commands, each doing the job its name describes — and the Jira `Done`
write now happens only after the landing push returns 0.

| Command | What it is now |
|---|---|
| `/cicd-close-story-merge-tree` | **the door** you type to close ONE story out: preflight → the save → commit → land on the epic branch → Dev Record → ticket → prune |
| `/cicd-update-sprint-memory` | keeps its name, slimmed to **the save**: learnings routed, board / story / active-context updated, story flipped `done`, context budget held. No landing, no ticket write, no prune |
| `/cicd-prune-worktree` | **the disk utility** (was the janitor). Moves no code |

**The defect this kills.** The ticket transition sat ~100 lines and three reachable STOPs before the landing
push. A transition is a **remote** write — it rides no branch — so a stopped landing left the code on one disk
under a ticket that read `Done`. The board flip and the story-file write **stay in the save**, precisely because
they are **file** writes that ride the story branch: a landing that stops publishes none of them. That asymmetry
is the whole design, and it is now stated in both command bodies.

## Task Checklist

- [x] Cut the lane, move SCC-210 to `In Progress`, write the plan
- [x] `/smh-self-audit` — LEDGER+BLAST, three lenses, **GO**, three findings baked into the plan
  - F1 · the drift check is per-file, so a "row class" note covered nothing → declared all 28 regenerated mirrors by path
  - F2 · `.claude/` contains `worktrees/`, where sibling lanes' checkouts still carry the old name → excluded from the sweep
  - F3 · CO-02's STOP needed a corpus measurement first → measured: **120 AGY story walkthroughs, 0 refused**
- [x] **RED first** — CS-13 (`test_command_surfaces.py`) and CP-EK/CP-FR/CP-MEM (`test_closeout_preflight.py`)
  - CS-13 opened at **10/30**, with C3 naming the defect in its own output: `push@[258] transitions@[161]`
  - Adversarially verified by four blind lenses; **seven** defects found in the assertions and all fixed
    - both lenses independently: adding a `c.block` guard enrolled the file in `test_suite_runner.py`'s ORPHAN sweep and broke it → the whole file is now block-wired (97/97)
    - three rows printed the FAILURE rationale on PASS — the transcript contradicting its own verdict
    - an unguarded `read()` aborted 16 sibling rows during this ticket's own rename window
    - `--expect-key` was asserted in prose only → added **H3**, which reads the script; it caught the doc/script drift immediately
    - the anti-vacuity floor (150 vs 1596 files) survived losing six of seven sweep roots → now per-root
    - `.githooks` was a declared root reading **zero** files (git hooks are extensionless) → now covered
    - three over-broad predicates that would false-red on correct text → anchored
- [x] Rename the utility (`git mv`, history preserved) + its hand-authored skill door
- [x] Create the door from the old body (`git mv`), restructure it, author its skill door
- [x] Re-create the slimmed save, and state in it *why* its writes are safe before a landing
- [x] `closeout_preflight.py` — CO-05 `--expect-key` (required), CO-06 fetch default-on + STALE on the verdict line, CO-07 memory dirt named apart
  - the RED caught a real implementation bug: `check_sync` had no `return fresh`, so `fresh` was `None` and a successful fetch reported STALE
- [x] Re-point every caller — six disjoint lanes, ~45 authored files, each hit routed by MEANING, not replaced
- [x] Rewrite the SOP: §7's altitude table, both §7 diagrams, three subsections, three command-atlas entries (redrawn step by step from the real commands), the system map, the hooks diagram, and ~20 prose rows
- [x] One `/smh-sync-agents` run + `generate_doc_graph.py` — all four platform doors, all three names
- [x] Gates green, mutation sweep, walkthrough
  - the enforcement suite caught one more self-inflicted defect: CS-13's needle constant was itself an
    `acli … workitem transition` line without `--yes`, so `test_jira_feed.py`'s guard indicted it. Assembled at runtime.

## Evidence

| # | Acceptance | Assertion | RED | GREEN |
|---|---|---|---|---|
| A | Three commands under their final names | CS-13 A1–A4 | A1/A2/A4 failed; only the old names existed | PASS |
| B | The retired name cannot return | CS-13 B1–B3 + per-root anti-vacuity | 26 files carried it | PASS · 1605 files across 7 roots, no root reading nothing |
| C | **The board cannot lie** | CS-13 C1–C5 | `push@[258] transitions@[161]` — transition **before** the push | PASS · transition after the push, both controls green |
| D | Multi-lane still prunes | CS-13 D1–D2 | merge-epic named the retired utility | PASS |
| E | The save is genuinely slimmed | CS-13 E ×5 + 2 controls | `git push`@258, `workitem transition`@161, `devrecord`@169 | PASS · all five clean |
| F | Every door resolves | CS-13 F ×3 | 10 of 15 surfaces missing | PASS · 15/15 after one sync |
| G | The SOP tells the truth | CS-13 G1–G3 + control | the "almost never type" claim at SOP:601 | PASS · claim gone, both names present |
| H | Callers pin the lane (CO-04/05) | CS-13 H1–H3 · CP-EK ×3 | `--expect-key` did not exist | PASS · mismatch errors, no-key warns, script and docs agree |
| I | Freshness on the verdict (CO-06) | CP-FR ×5 | `--no-fetch` was not a flag | PASS · STALE on the verdict line; default stays fresh |
| J | Memory named apart (CO-07) | CP-MEM ×3 | one undifferentiated "commit before closing out" | PASS · own class, park-or-leave ruling, exit code unmoved |
| K | CO-02 / CO-08 / CO-09 folded in | CS-13 K1–K3 | all three absent | PASS |

**Suite, through the receipt writer, on the shipping code:**

```
[PASS] suite exit=0 123.5s @ 50961bed
39/39 files passed
```

Receipt: `gates/suite.json` (`result: pass`, `exit_code: 0`). ⛔ **The first run of this gate was RED at
38/39** and the file it named was `test_jira_feed.py` — see the last row of the Task Checklist. That is the
gate doing its job: nothing in review would have found it, because the defect was a string constant in a
test that invokes nothing.

**Static + structural:**

- `workflow_lint.py --toolkit-only` → **0 errors, 0 warnings, 8 info** — byte-identical to the pre-ticket baseline.
- `test_check_maps.py` → green (this lane's own `_artifacts/_main/INDEX.md` row was owed; the gate said so by name).
- `test_command_surfaces.py` → **168/168**, including all of CS-01..CS-12 untouched.
- `test_closeout_preflight.py` → **40/40**; `test_suite_runner.py` → **97/97**; `test_twin_parity.py` → **58/58**.
- Dangling `.agents/commands/*.md` references across `.agents/ docs/ AGENTS.md _bmad/`: **0**.
- SOP in-file anchors: **0 unresolved before, 0 after** (37 → 38; this lane added one and broke none).
- The retired name outside `_artifacts/` and `_my_resources/`: **0 files**.

**CO-02's precondition, measured before arming the STOP:** `jira_feed.py check-actions` over
`Projects/AGY_AVIATIONCHAT/_artifacts/epic_*/**/walkthrough.md` — **120 walkthroughs, 0 refused**.

## Mutation sweep — 15 mutants, 15 killed

Two tables (`mutation_sweep.py` takes one test file per table), every mutant drawn **from the code**, never
from the cases. Both runs verified their restore against the pre-sweep sha *and* the pre-sweep bytes, and
finished with the full file unfiltered.

**[sweep-preflight.json](sweep-preflight.json) — 7/7 killed** (`test_closeout_preflight.py`)

| # | The mutant | Killed by |
|---|---|---|
| M1 | a branch carrying the WRONG key only warns | EK1 |
| M2 | a branch with NO key segment goes quiet (info, not warn) | EK3 |
| M3 | the unfetched path is a FOOTNOTE (info) again | FR3 |
| M4 | `--no-fetch` no longer costs freshness | FR2 |
| M5 | the verdict line stops reading freshness | FR2 |
| M6 | memory dirt folded back into the generic count | MEM1 |
| M7 | the memory row splits but LOSES the park-or-leave ruling | MEM2 |

**[sweep-doors.json](sweep-doors.json) — 8/8 killed** (`test_command_surfaces.py`)

| # | The mutant | Killed by |
|---|---|---|
| N1 | the ticket moves BEFORE the landing push (the original defect, restored) | C3 |
| N2 | the door's preflight stops pinning the lane | H1 |
| N3 | the door stops refusing a bad `## Your Actions` before the landing | K1 |
| N4 | the Dev Record check reverts to the SCOPED form (blind to a fork) | K2 |
| N5 | the sign-off stops being spent by one close-out (SCC-71) | K3 |
| N6 | the landing creeps back into the SAVE | E |
| N7 | the doors document a flag the SCRIPT does not accept | H3 |
| N8 | the retired janitor name comes back into an authored command | B1 |

⭐ **The first doors run left N5 and N7 SURVIVING, and both were the same defect wearing two costumes: a row
satisfied by a MENTION of the thing rather than the thing.** K3 read the whole door file, so deleting the spend
clause from the landing step still passed on the frontmatter `description:` — a menu blurb, not an instruction
followed at the moment of the landing. H3 read a bare substring, so renaming the argparse flag to `--expectkey`
still passed on the module's own usage docstring — the exact doc/script drift H3 exists to detect, reproduced
inside H3. K3 now reads the step body (as C3 and K1 already did); H3 now asserts the declaration. Re-run: 8/8.

## Suite Ledger

| Scope | Command | Result | Why this run |
|---|---|---|---|
| CS-13 only | `test_command_surfaces.py --case "CS-13"` | 10/30 | the RED, before any edit |
| whole file | `test_command_surfaces.py` | 144/164 — all 20 failures in CS-13 | prove no pre-existing row broke |
| preflight | `test_closeout_preflight.py` | 32/40 → 40/40 | RED → GREEN on CO-05/06/07 |
| full enforcement suite | `gate_receipt.py run --gate suite -- run_all.py` | 38/39 @ `072b779` | caught the needle self-match |
| full enforcement suite | `gate_receipt.py run --gate suite -- run_all.py` | 39/39 @ `f92e4bf`, exit 0 | green before the review |
| review fixes | `test_closeout_preflight.py` · `test_command_surfaces.py` | 40/40 → **47/47** · 168/168 → **172/172** | 7 + 4 rows added, each written against a surviving mutant |
| mutation | `mutation_sweep.py --table sweep-review-preflight.json` | **7/7 killed**, restore verified | the review's two reproduced defects + four vacuous gates |
| mutation | `mutation_sweep.py --table sweep-review-doors.json` | **3/3 killed**, restore verified | the CS-13 predicate fixes |
| full enforcement suite | `gate_receipt.py run --gate suite -- run_all.py` | **39/39 @ `50961be`, exit 0** | the landing evidence |
| mutation | `mutation_sweep.py --table sweep-preflight.json` | 7/7 killed, restore verified | prove the preflight rows can fail |
| mutation | `mutation_sweep.py --table sweep-doors.json` | 6/8 → **8/8** killed | two survivors found and fixed |

## Your Actions

**What landed.** Branch `chore/SCC-210-close-out-rebalance`, commits `ce6c109..50961be` (7 — four building,
three from the review), `0 0` with origin after the push. `main` untouched. 98 files: three command bodies, three skill doors, one script, ~45 authored
callers, the SOP, and the regenerated mirrors from one `/smh-sync-agents` run.

**Decided while building, and worth knowing:**

- **The ticket contradicted itself and §6 won.** Finding CO-01 asked for `jira_feed.py finish` in the story
  door; §6 DO-NOT forbade it. Re-measured: `finish` hardcodes `origin/main` ([jira_feed.py:1789-1790](../../../.agents/scripts/jira_feed.py#L1789-L1790)),
  and a story lands on `epic/<KEY>-<slug>`, so it would report "held" forever while the status file already
  read `done`. The door transitions with `acli`, and CO-01's real intent — the `## Your Actions` refusal —
  arrives instead as Step 2's `check-actions`, which reads only the walkthrough. **Follow-on, not minted:**
  teach `finish` a landing-target argument and both families share one closer.
- **Only ONE name retired.** `cicd-update-sprint-memory` still exists, so the ~100 references to it could not
  be replaced — each had to be routed by meaning. Every surviving mention was re-read at the end: all of them
  mean the save.
- **The twins stay unpaired, on the record.** `cicd-close-story-merge-tree` and `smh-close-task-merge-tree`
  look like a pair and are not: a story lands on its epic branch, a Task opens a PR against `main`, and their
  bodies share no law fences today. Recorded in `NOT_PAIRED` with that reason rather than forced into `PAIRS`.
- **One reference is in another repo.** `Projects/AGY_AVIATIONCHAT/.agents/scripts/git-hooks/pre-push-main-approval.sh:10`
  names the old command in a comment. Different repo, needs an `AVCH` key — a follow-on, not this lane's diff.

## Your Actions

- [x] The merge itself — lands via this branch's PR

---

## Code Review (2026-08-20)

Verdict: PASS @ 50961bed
Suite evidence measured at `50961bed` — the same sha the lenses' fixes landed on, and the sha on `gates/suite.json`.

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok — truncated by the 20-file cap; the 42 withheld paths were named to it, and it spent its one earned top-up on cicd-merge-epic-workingtrees.md
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none

dispositions:    per-lens: blind-hunter=5/0/2 · edge-case-hunter=6/0/0 · literal-correctness-hunter=8/1/0 · acceptance-auditor=11/4/0 · test-adequacy-auditor=7/2/0 · compound-synthesis=6/1/0
drift:           undeclared=0 · unimplemented=5 · incomplete=0 — three malformed declaration bullets repaired and six regenerated launcher mirrors declared (both were `incomplete`/`undeclared` at first run); the five `unimplemented` rows are plan overreach, each re-checked and annotated in the plan rather than deleted

**Scope.** `origin/main...HEAD`, 101 files (62 authored, 39 generated mirrors), re-taken after Step 0.7 absorbed `origin/main` at `485e24f`.
**Method.** Five lenses in parallel clean contexts, then an Evidence Verifier and a Compound Synthesis role concurrently over a programmatically-extracted dossier; 46 raw findings + 7 compound. Every "REPRODUCED" claim was re-run by the verifier rather than taken on trust. Two findings were refuted on the evidence and killed.

### Findings

| # | file:line | severity | failure scenario | disposition |
|---|---|---|---|---|
| 1 | `closeout_preflight.py:189` | important | `.stdout.strip()` ate the leading space off the FIRST porcelain line, so an unstaged `" M _artifacts/_memory/MEMORY.md"` read as `artifacts/_memory/…`, missed the memory class, and got the generic *"commit before closing out"* — the exact instruction CO-07 added the split to prevent, on its own most common shape | applied @ `16bc222` |
| 2 | `closeout_preflight.py:189` | suggestion | no `-c core.quotepath=false`, so a memory path with a non-ASCII byte is octal-quoted past the class test — the same misroute by a second route | applied @ `16bc222` |
| 3 | `closeout_preflight.py:48` | suggestion | `find_branches` uses `--all`, so a sibling lane resolvable only as `origin/claude/SCC-99-x` had its key eaten by `^[a-z]+/` and reported as keyless: a blocking wrong-lane ERROR downgraded to a non-blocking WARN | applied @ `16bc222` |
| 4 | `test_closeout_preflight.py` (CP-EK) | important | nothing pinned `required=True` on `--expect-key`; the one-token edit to `required=False` left all 39 suite files green, and the mutant then printed `VERDICT: clear to close out` for a run aimed at a sibling lane — the 2026-08-09 failure restored | applied @ `16bc222` (EK0, asserted through `_spawn` so `run_cp`'s retry cannot soften it) |
| 5 | `test_command_surfaces.py` (CS-13 E) | important | `instructs()` scanned the whole line for a negation cue, so a real landing instruction reading *"When there is no conflict, run `git push …`"* was exempted by a stray `" no "` — all five E rows printed `clean` with the landing back in the save | applied @ `16bc222` (clause-scoped + 2 controls) |
| 6 | `test_command_surfaces.py` (CS-13 K3) | suggestion | the row read only that the spend clause existed somewhere in the step body; cutting it from the landing step and leaving a note in Step 6 kept it green — a rule read after the act it governs | applied @ `16bc222` (pinned to the push's step section) |
| 7 | `test_command_surfaces.py` (CS-13 G1/G2) | suggestion | bare substring presence over the SOP; survived the SOP being scrubbed of all 53 references and given one HTML comment | applied @ `16bc222` (heading anchor + reference floor + 2 controls) |
| 8 | `closeout_preflight.py:473` | suggestion | the `--worktree` term of the freshness fold had no test — the string never appeared in the file — and dropping `and fresh` turned STALE into "clear to close out" on the door's own invocation shape | applied @ `16bc222` (FR6) |
| 9 | `closeout_preflight.py:493` | suggestion | both STALE arms could print the same remedy; every shipped caller meets the failed-fetch arm and would be told to drop a flag it never passed | applied @ `16bc222` (FR5) |
| 10 | `test_closeout_preflight.py` (CP-MEM) | suggestion | the memory-only run's output was bound and never read, so a fabricated `"0 uncommitted change(s)"` row survived all three MEM rows | applied @ `16bc222` (MEM4) |
| 11 | `cicd-close-story-merge-tree.md:135` | suggestion | *"The same refusal fires again at Step 4"* is false — Step 4's three commands never read `## Your Actions`, and `finish` is banned on this lane by the same file. An agent told a net exists skips the one gate that is real | applied @ `11bcd03` |
| 12 | `cicd-close-story-merge-tree.md:139` | important | the `claude/*` HEAD precondition sat AFTER the only commit (the command it replaced checked it first). A door run from the shared checkout on `main` writes the whole close-out onto `main`, then STOPs — the act the STOP's own sentence forbids. `--expect-key` does not catch it: a bare `main` carries no key, so it WARNs at exit 1 | applied @ `11bcd03` |
| 13 | `cicd-close-story-merge-tree.md:189` | important | the merge-gate totals and the landing line are written AFTER the only commit, so the landed walkthrough carries neither and the tree is dirty at Step 5 — where the prune preserves it by pushing `claude/<KEY>-<slug>`, the push Step 3 forbids, then rules that branch not deletable, and `/cicd-resume` later offers a story reading `done` | applied @ `11bcd03` (commit + push the record) |
| 14 | `cicd-close-story-merge-tree.md:236` | important | a bare `acli … transition` with no exit check, and Step 4c's `jira_feed.py check` never reads `status` — a failed transition sails through, the tree is pruned, and Step 6 prints `Done` over a ticket at `In Review`, on the command whose purpose is that the board cannot lie | applied @ `11bcd03` (`\|\| STOP` + read-back) |
| 15 | `cicd-close-story-merge-tree.md:70` | important | Step 0.6 said *"Exit 2 = BLOCKED"* over a preflight whose `landed` row is red on every normal close-out — Step 3 is what lands it. Read literally, the door stops before Step 1, every time. Reproduced on a fixture: `VERDICT: BLOCKED`, exit 2 | applied @ `11bcd03` (that row named expected; every other error still blocks) |
| 16 | `cicd-prune-worktree.md:32` | important | Step 0.6 requires `--story` and `--expect-key`; Step 0 bound neither, and its own `claude/` strip discards the only place a key would be. The standalone prune dead-ends on argparse exit 2 — which is also this script's BLOCKED code, so a usage mistake reads as a blocked lane | applied @ `11bcd03` |
| 17 | `cicd-prune-worktree.md:160` | important | Step 1.7 authorises a destructive prune on *"only a human close-out writes `done`"*. This split made that false: the save writes `done` and lands nothing | applied @ `11bcd03` (gate now says so and asks for the merge check) |
| 18 | `cicd-update-sprint-memory.md:37` | important | standalone, the save flips `done` on both file surfaces while nothing anywhere moves the ticket — the rebalance's own defect pointing the other way | applied @ `11bcd03` (flip stays; the command now prints what is still owed and names the door) |
| 19 | `cicd-close-story-merge-tree.md:49` | suggestion | `<JIRA-KEY>` is bound to the STORY's ticket, then reused in `epic/<JIRA-KEY>-<slug>`, which carries the EPIC's. A story on another epic CREATES a new remote epic branch, returns 0, and the ticket moves on the strength of it | applied @ `11bcd03` (`$EPIC` resolved from `git branch --list`) |
| 20 | `cicd-close-story-merge-tree.md:275` | nitpick | told the caller to pass `--repo`, which `closeout_preflight.py` does not define (that flag is the Task lane's), and omitted `--expect-key`, which it requires | applied @ `11bcd03` |
| 21 | `cicd-close-story-merge-tree.md:100`, `cicd-prune-worktree.md:38` | nitpick | the STALE remedy unconditionally said *"re-run without `--no-fetch`"*; no shipped caller passes that flag, so the reachable arm is the failed uplink | applied @ `11bcd03` (both remedies named) |
| 22 | `cicd-update-sprint-memory.md:203` | nitpick | listed the door's four steps as land → ticket → Dev Record → prune while asserting the order is the safety property; the door's order is land → Dev Record → ticket → prune | applied @ `11bcd03` |
| 23 | `workflows_testing_SOP.md:2422` | suggestion | a new row claimed the door refuses on a `FAIL` verdict; no door branch stops the landing on FAIL (the save refuses the flip) | applied @ `11bcd03` |
| 24 | `workflows_testing_SOP.md:1752`, `:2996`, `:3041` | suggestion | the tool row named neither `--expect-key` nor the STALE state; merge-epic's `Calls:` listed a script it never invokes; the prune atlas node showed an invocation that now dies on a required flag | applied @ `11bcd03` |
| 25 | `tea_deep_reference.md:47` | nitpick | *"Nothing is committed mid-story"* is false — three command bodies mandate mid-story commits inside the worktree. What is true is that nothing reaches a remote | applied @ `11bcd03` |
| 26 | `closeout_preflight.py:9` | nitpick | the module usage line paired an AVCH story id with an SCC key, which the new intent check refuses | applied @ `16bc222` |
| 27 | `implementation_plan.md` §2 | nitpick | ticket §5 DO 5 (a prune-only entry point) was not built and the reason was unrecorded, so it read as dropped scope | applied @ `11bcd03` (premise re-measured and the reasoning written down) |
| 28 | `implementation_plan.md` § Declared Change Set | important | three declaration bullets put their `→` mapping on a continuation line and the parser rejected them; six regenerated launcher mirrors were undeclared | applied @ `11bcd03` — drift now `incomplete=0 undeclared=0` |
| 29 | `gates/suite.json` | nitpick | the receipt was STALE at the shipping sha and the walkthrough cited a third sha | applied @ `50961be` (re-stamped; the ledger below corrected) |
| 30 | 8 blocks in the 3 changed `.py` files | nitpick | explanatory comment blocks the review added carried no ticket key (clean-code §2A) | applied @ `50961be` |

**Dismissed, with reasons — 8:** `/cicd-merge-epic-workingtrees` files no Dev Record and moves no ticket (real, but its `Steps 1–4 + 6` scope line is untouched by this diff and predates the split; recorded in the SOP entry instead of widening scope) · `cicd-code-review.md:454`'s `finish` promise (pre-existing, written generically across both lanes, and still true on the Task lane) · the door's git history not following the file it replaced (no runtime effect) · one-commit-per-step not followed (process; the 25 killed mutants are stronger evidence than commit shape) · `--json` payload untested (no consumer exists) · `check_intent`'s both-resolved WARN branch untested (exit code unaffected either way) · CS-13 E banning five spellings rather than the act (a semantic ban has no implementation today; the negation half was fixed) · the personal name in the door's sign-off line (verbatim-carried, and 62 files under `.agents/` share it — a house-wide convention question, not this lane's).

**Relevance-killed — 2:** the Blind Hunter's claim that `/cicd-merge-epic-workingtrees` would die on the new required flag (it never invokes the preflight — verified by grep; only the SOP line was wrong, and that is finding 24) and its claim that three door-surface trees were absent from the change set (they are tracked and present — an artefact of the filtered diff it was handed, not the lens's error).

### Gates

| Gate | Result |
|---|---|
| Enforcement suite | `39/39 files passed`, exit 0 @ `50961bed` — through `gate_receipt.py run`, `result: pass`, `dirty_tree: false` |
| Toolkit lint | `workflow_lint.py --toolkit-only` → `0 error(s), 0 warning(s), 8 info` (the 8 are UTF-8 BOMs on vendor `testarch-*` files; byte-identical to the pre-ticket baseline) |
| Assertion evidence | `test_closeout_preflight.py` **47/47** (was 40/40) · `test_command_surfaces.py` **172/172** (was 168/168) · `test_twin_parity.py` 58/58 · `test_jira_feed.py` 343/343 |
| Mutation | `sweep-review-preflight.json` **7/7 killed**, restore verified · `sweep-review-doors.json` **3/3 killed**, restore verified — every mutant is the code exactly as it shipped before the review, so a survivor would mean a fix went unpinned |
| SOP currency | staged in `11bcd03`; the two comment-only commits carry `[sop-ok]` |
| Link + anchor | 80 changed `.md` files swept — **0 dangling paths, 0 dead anchors, 0 unknown commands.** (The first pass reported 13/62/54; every one was the checker's own bug — placeholder strings, rules mistaken for commands, a base path off by one, and a slug rule that stripped the leading space GitHub keeps. Each class was re-verified by hand against ground truth.) |
| Door parity | 15/15 surfaces for all three names after one `sync-agents` run; CS-13 F ×3 green |

### Acceptance matrix

| Ticket §10 | Delivered | The assertion that proves it |
|---|---|---|
| 1 · three commands under their new names | yes | CS-13 A1–A4; B1 sweeps 1608 files across 7 roots for the retired name, 0 hits, with a per-root anti-vacuity row |
| 2 · retired names cannot return | yes | CS-13 B1/B2/B3 + mutant N8 |
| 3 · **the board cannot lie** | yes | CS-13 C3 — `push@[223] transitions@[266]`, controls C4/C5 both directions, mutant N1 killed |
| 4 · multi-lane still prunes | reinterpreted, with the reason recorded | CS-13 D1 (merge-epic names the utility) + D2 (the utility carries no landing push). DO 5's premise — that the utility could double-land — is false; plan §2.1b now says so |
| 5 · sprint-memory genuinely slimmed | yes | CS-13 E ×5 + 4 controls + mutant N6 **and** review mutant S1, the negation-cue shape the original sweep could not express |
| 6 · every door resolves | yes | CS-13 F ×3, 15/15 on disk |
| 7 · the SOP tells the truth | yes | CS-13 G1/G2 now anchored to the heading each command owns, plus G3's claim check; four stale SOP lines corrected in this review |
| CO-01…CO-09 | all nine applied; CO-01 deliberately follows §6 | the ticket contradicts itself; `jira_feed.py finish` hardcodes `origin/main` ([jira_feed.py:1789-1790](../../../.agents/scripts/jira_feed.py#L1789-L1790)) and would hold every story forever. Verified against source by the acceptance auditor, which also corrected the ticket's own reasoning: the hold is conditional on a merge-shaped row, not universal — the decision stands either way |

### Clean-Code Gate — PASS

| Check | Result |
|---|---|
| `py_compile` | PASS — `closeout_preflight.py`, `test_closeout_preflight.py`, `test_command_surfaces.py` |
| machine floor | imported from Gates above (`run_all`, `workflow_lint`, link+anchor) — not re-run |
| committed secret · debug print · commented-out code · bare `except` · absolute/`C:` path · bare `python` · `\|\| true` · unowned TODO · `/sudo-` door · underscore in a command name | 0 hits across 672 added lines |
| comment contract §2A | 12 explanatory blocks added; **8 carried no ticket key** → fixed @ `50961be`. No `AIDEV-NOTE` invalidated. |
| §2B drift/bloat | imported from Step 1 (source `review`) — not re-walked |
| convention table §2C | naming law ✓ · prefix-is-permission ✓ · one door per platform ✓ · no hand-edited generated file ✓ · rule pointers restated not replaced ✓ · both machines (`python3` throughout) ✓ · gates ship armed ✓ · every gate has an exit (`[sop-ok]`) ✓ · **a gate must be able to fail — this was the review's largest finding class, four rows, all now mutation-proven** ✓ · artifacts in the tree ✓ · no board narrative ✓ · prose consequence-first ✓ |
| personal name in an `.agents/` body | 1 line, verbatim-carried from the command being renamed; 62 files under `.agents/` share it. Dismissed as a house-wide convention question, not this lane's |

### Step 0.7 — the blast radius, re-derived against current `main`

- **What `main` moved under this diff:** nothing this diff references. Two files landed since the merge-base `fe0f211` — `_artifacts/_memory/MEMORY.md` and `_artifacts/_memory/naming-a-ticket-is-not-a-mint-order.md` (PR #29, SCC-186). Every repo path, `#L` anchor, script flag and `/command` this diff names still resolves; re-checked after the absorb.
- **True overlap and merge result:** **zero** overlapping files. `merge-tree --write-tree` returned a tree with no conflict messages; the absorb landed as an ordinary merge commit at `485e24f` touching only those two memory files.
- **Sibling-lane landing order:** one lane live — `chore/SCC-235-dual-surface-blast-radius`, at planning only (2 artifact files, no code). Its plan targets `blast_analyzer.py`, `tia_provider.py`, `wf_common.py` and a new `blast-radius.md` rule; **no overlap with this diff, and no landing-order dependency in either direction.**
