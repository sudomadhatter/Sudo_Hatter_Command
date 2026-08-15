---
IsArtifact: true
ArtifactMetadata:
  title: SCC-38 lane walkthrough — flight recorder (SCC-133) + autopilot done-means-green (SCC-134) + folded SCC-130
  type: walkthrough
  date: 2026-08-15
---

# SCC-38 lane — walkthrough

**Branch:** `chore/SCC-38-flight-recorder-autopilot-spec` · **Riders:** SCC-133, SCC-134 (operator
ruling: *"we will run them both in one branch. one then the other"*) · **Plan:**
[implementation_plan.md](implementation_plan.md) (`Audit verdict: GO`, `approved` received verbatim).

## Task Checklist

- [x] C1 — first commit: master plan `## Delta (2026-08-15)` + `open_tasks` proposal → 12-line pointer (`193d8ba`)
- [x] A1 — `flight_recorder.py record`: one event file, verdict-sha keyed, idempotent (`93dacb2`)
- [x] A2 — `candidates`: distinct-task ladder, `--json`
- [x] A3 — `surface`: silent-empty / one proposal per action-required rung / real hook run against a seeded repo
  - hook resolves the script beside itself (`$HERE/../scripts/…`) so the test can point `CLAUDE_PROJECT_DIR` at a temp repo and still exercise the real hook; `python3 || python`
- [x] A4 — door bound: `/smh-close-task-merge-tree` **Step 2.5** (pre-merge, artifacts-only commit); `/cicd-boot-sprint-memory` Step 3 line; SOP node + paragraph; scripts INDEX row; doors regenerated
- [x] A5 — manual-learnings question conditional in `cicd-update-sprint-memory` + `cicd-merge-epic-workingtrees`
- [x] B1 — `autopilot_bmad_dev_loop.md` §6a Done-means-green (five principles + "red gates stay human-in-the-loop, dropped not deferred") (`41f0ba2`)
- [x] `task.yaml` with `riders: [SCC-133, SCC-134]` (`aa5a8d3`); receipts chained clean (`828f95b` suite · `d5a2f8f` lint · `7f32ed2` maps)
- [x] Mutant sweep 13/13 killed; one test gap it exposed (rules-prefix) pinned first (`5fe9393`)
  - the suite receipt predates `5fe9393` (a test-file commit) → re-stamped after the review's last code-touching change, per SCC-156's one-re-stamp rule

## Evidence

Each acceptance item → the assertion → RED then GREEN. Suite file: `.agents/scripts/tests/test_flight_recorder.py`
(three `--case` blocks A1/A2/A3).

| Item | Assertion | RED (before) | GREEN (after) |
|---|---|---|---|
| A1 record | `--case A1`: one `workflow-events/2026-08/SCC-901_<sha7>.json`; `sha` = verdict sha ≠ `tip`; `changes` = lane files only after `main` moved on; fingerprints `rule-edited:.agents/rules/r.md`, `gate-red:lint` (not suite), `mention:gate_receipt.py` + `mention:/smh-code-review`, no `verdict:` on PASS; replay (and replay after an artifacts commit moved HEAD) writes nothing + says "already recorded"; no walkthrough → exit 2; no Verdict → exit 2 | `27/31` FAIL — `can't open file '…/flight_recorder.py'` (script absent; the 4 passes were the negative-shaped checks, vacuous on empty data) | `32/32 passed` |
| A2 candidates | `--case A2`: 3 distinct tasks → `action-required` (3 tasks, 3 shas, "commission the script"); same task twice → counts ONCE (2 distinct → `candidate`); 1 → `evidence`; `fingerprints: []` → no rung; `--json` parses | same RED run | same GREEN run |
| A3 surface + hook | `--case A3`: empty → no stdout, exit 0; malformed file → exit 0; seeded → exactly one PROPOSAL line naming SCC-11/12/13; **the real `session-start-context.sh` run with `CLAUDE_PROJECT_DIR=<temp repo>` emits it and exits 0**, and still prints its standing gate text | RED: 29/31 after the script existed but before the hook was wired — `A3 SessionStart hook emits …` FAIL | GREEN after the hook edit |
| A4 door | `smh-close-task-merge-tree.md` Step 2.5 present; `workflow_lint --toolkit-only` → `0 error(s), 0 warning(s)`; `check_maps --depth3-only --strict` exit 0; sync-agents regenerated 4 opencode mirrors + 2 workflows + `.claude/hooks/` copy; SOP-currency gate accepted the commit with the SOP staged | Step 2.5 absent | present @ `93dacb2` |
| A5 conditional question | `grep -n "manual learnings" .agents/commands/cicd-update-sprint-memory.md cicd-merge-epic-workingtrees.md` | `ask Daniel (always, …)` / `ask … once:` — unconditional | `CONDITIONALLY (SCC-133) … only when Step 3 routed ZERO learnings` / `once, and only if the set routed ZERO learnings` |
| B1 spec | `grep -c "Done-means-green" docs/_scc_sops_prds/autopilot_bmad_dev_loop.md`; `test_sops_prds_folder.py` | `0` | `1` (§6a, lines 313–362); folder test `61/61 passed` |
| C1 folded | `grep -c "Delta (2026-08-15)"` master plan; `wc -l` proposal | `0` · `135` | `1` · `12`, both pointer links resolve |

**Suite (through the receipt writer, clean tree):** `28/28 files passed`, exit 0, 104.9 s @ `aa5a8d3` →
`gates/suite.json`; lint `0/0` @ `828f95b` → `gates/lint.json`; maps exit 0 @ `d5a2f8f` → `gates/maps.json`.

**Mutant sweep (declared before mutating; every mutant an edit to a real line; one run; sha256-verified restore; `git status` clean after):**

| Mutant | Edit | Killer case | Verdict | Evidence |
|---|---|---|---|---|
| M1 | event keyed on HEAD instead of the verdict sha | A1 | KILLED | `A1 file name = <KEY>_<verdict sha7>.json: SCC-901_e357f31.json` |
| M2 | ladder floor 3 → 4 | A2 | KILLED | `A2 3 distinct tasks -> action-required` |
| M3 | distinct-task count → raw count | A2 | KILLED | `A2 same task twice counts ONCE` |
| M4 | `surface` exits 1 | A3 | KILLED | `A3 empty ledger -> no output, exit 0` |
| M5 | `RULES_PREFIX` widened to `.agents/` | A1 | KILLED | `A1 rule-edited fires ONLY under .agents/rules/` (the case added for it) |
| M6 | gate-red reads `pass` as red | A1 | KILLED | `A1 fingerprint gate-red only for the failing receipt` |
| M7 | changes two-dot instead of three-dot | A1 | KILLED | `A1 changes = the lane's own files, three-dot` |
| M8 | verdict fingerprint on PASS | A1 | KILLED | `A1 no verdict fingerprint for a PASS` |
| M9 | hook no longer calls `surface` | A3 | KILLED | `A3 SessionStart hook emits the proposal line` |
| M10 | dry run writes | A1 | KILLED | `A1 dry-run writes nothing, exits 0` |
| M11 | slash-command mention dropped from the regex | A1 | KILLED | `A1 fingerprint mention: script + command` |
| M12 | malformed event re-raises in `load_events` | A3 | KILLED | `A3 seeded -> exactly one PROPOSAL line` (surface's outer catch swallows the raise but then prints nothing) |
| M13 | idempotency check removed | A1 | KILLED | `A1 replay writes nothing and says so` |

13/13 killed. Closing green: `test_flight_recorder.py` bare → `32/32 passed`.

## Decisions

- Keyed on the walkthrough's verdict sha, not HEAD — HEAD moves the moment the event is committed; a resumed close-out must not double-write (audit F1).
- One file per event, no materialised candidates view — sibling lanes never conflict; the ladder is recomputed on read (F2, F3).
- Bound PRE-merge as Step 2.5 — a post-merge write is a `main` write outside the token (F1).
- Renamed from the master plan's `command_center_closeout.py` to `flight_recorder.py` — a "closeout" name beside `closeout_preflight.py` that only records is a trap.
- The red-gate auto-fix loop for autopilot is DROPPED, not deferred — v2 is human-in-the-loop on TESTS RED by design; recorded in §6a and the master plan Delta.
- Cross-link from the autopilot commands to §6a CUT (F4) — a command-surface touch the ticket did not ask for.

## Pitfalls

- `run_script` merges stderr into stdout, so a `[warn]` line for a malformed event file counted as "output" in the A3 line-count check — the test filters `[warn]` lines; the warning itself is correct behaviour.
- Lint/maps receipts stamped over an uncommitted suite receipt read `DIRTY` — chain them (commit each receipt, then stamp the next), exactly as SCC-160's log shows.
- A mutant that widens `RULES_PREFIX` survived the first table on paper — the original A1 check only asserted the rules file was present, not that the script was absent; pinned before the sweep ran.

## Your Actions

Everything above landed on the branch. Nothing is owed to you by this lane except the merge word.

- The first real event will be **this lane's own close-out** (`flight_recorder.py record --task SCC-38 …` at Step 2.5) — the ledger is born empty on purpose.
- Proposal, not owed (SCC-160): a mechanical guard that refuses the merge when Step 2.5 was skipped would be **new law needing its own quoted ruling** — not shipped; today the numbered step + the Evidence row are the net.
