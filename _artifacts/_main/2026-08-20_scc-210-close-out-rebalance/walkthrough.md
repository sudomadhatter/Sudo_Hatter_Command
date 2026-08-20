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
[PASS] suite exit=0 146.6s @ f92e4bf0
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
| full enforcement suite | `gate_receipt.py run --gate suite -- run_all.py` | **39/39 @ `f92e4bf`, exit 0** | the landing evidence |
| mutation | `mutation_sweep.py --table sweep-preflight.json` | 7/7 killed, restore verified | prove the preflight rows can fail |
| mutation | `mutation_sweep.py --table sweep-doors.json` | 6/8 → **8/8** killed | two survivors found and fixed |

## Your Actions

**What landed.** Branch `chore/SCC-210-close-out-rebalance`, commits `ce6c109..f92e4bf` (4), pushed, `0 0`
with origin. `main` untouched. 98 files: three command bodies, three skill doors, one script, ~45 authored
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
