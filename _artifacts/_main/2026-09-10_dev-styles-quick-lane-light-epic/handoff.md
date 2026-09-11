# SCC-441 — Hand-off (2026-09-11)

Written for the next agent. Every claim here is checkable against the tree. Check it; do not take
it on trust. The previous agent produced one fabricated review record on this branch and one
partially improvised one, both described below.

## What this ticket is

SCC-441 in the lobby (`Sudo_Hatter_Command`), a consolidated Task lane building two development
toggles, with riders SCC-442 through SCC-446. `landing_mode: partial` in `task.yaml`: the parent
stays open after this lands, for AVCH-152 (arms AviationChat's CI for the LIGHT token) and Part F
(a closure lane touching `smh-new-project.md`, the TEA guide and SOP §6).

- **Toggle 1, the quick lane.** `/smh-quick-dev` in the lobby, `/cicd-quick-dev` in a project.
  Five steps: scope check → plan and the operator's literal `approved` → RED → GREEN → walkthrough
  and the literal `approved` again → the scope check re-run on the real diff as a tripwire. Its
  only gate is `.agents/scripts/scope_check.py` against `.agents/critical-surfaces.json`. No
  review runs unless the operator asks; the walkthrough then carries
  `Review: none - quick lane; walkthrough approved by the operator @ <sha>` and no `Verdict:`.
- **Toggle 2, epic mode.** FULL, LIGHT or TRUNK, read from git by `.agents/scripts/epic_mode.py`.
  A branch name CONTAINING `-light-epic-` is LIGHT (a substring test, because CI's `contains()`
  reads the same thing). No `origin/epic/*` at all is TRUNK. Twelve `cicd-*` doors call it at
  Step 0 and echo both lines it prints.

The rider tickets' own plans are under `parts/`, the Jira mirrors under `tickets/`.

## Where it stands

| | |
|---|---|
| Branch | `chore/SCC-441-dev-styles-quick-lane-light-epic`, pushed |
| Worktree | `/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/SCC-441-dev-styles-quick-lane-light-epic` |
| HEAD | `18afe3f6` (docs only) on top of the code tip `dd5a5c42` |
| Base | `origin/main` at `cf1544f9`; 0 commits landed on main since the fork; overlap empty; `merge-tree` clean |
| Merged | nothing. Nothing on `main`. No PR open. |
| Verdict | **FAIL @ dd5a5c42**, recorded in `walkthrough.md` § Code Review (2026-09-11) |
| Suite | `run_all.py` 86/86 files, exit 0, clean tree, `gates/suite.json` stamped @ `dd5a5c42` |
| Lint / links / maps / SOP currency / door parity | all clean at `dd5a5c42` (see the review's Gates table) |

The shared lobby checkout at `/home/dlohn/Sudo_Hatter_Command` stands on `main`. Leave it there.

## What works, per the suite and five independent lenses

| Piece | State | Check it |
|---|---|---|
| `epic_mode.py` | classification correct; lenses could not break it; empty `--repo`, non-repo and AMBIGUOUS paths all behave | `python3 .agents/scripts/tests/test_epic_mode.py` |
| `scope_check.py` | correct on relative paths; refuses empty `--paths`; map / no-map / empty-map all handled | `python3 .agents/scripts/tests/test_scope_check.py` |
| twelve doors print the mode line | all 12, none keeps its own `for-each-ref` | `grep -l epic_mode.py .agents/commands/cicd-*.md` |
| `/smh-quick-fix` retired, `/smh-dev-task-tests` renamed | complete on every platform, no live reference | `grep -rn smh-quick-fix .agents/commands/` |
| generated mirrors (`.opencode/`, `.claude/skills/`, `.roo/`) | byte-identical to their sources | `test_command_surfaces.py` 343/343 |
| close-out's two landing arms; the quick-lane record line and its reader | present and parsing | `test_closeout_preflight.py`, `test_trunk_mode.py` |
| acceptance rows | 31 of 37 satisfied with a named assertion | the auditor's table in `review-lenses.md` §4 |

## What is broken

**The findings table, 30 rows, is in `walkthrough.md` § Code Review (2026-09-11). Work from that
table, not from this summary.** The raw lens reports it was built from are in `review-lenses.md`
beside this file. Where the table and a lens report disagree, the lens report is the evidence.

The three that matter most:

1. **Row 1.** The quick lane's scope check never runs in six of the places the doors call it:
   `cicd-quick-dev.md:237,401,402` and `smh-quick-dev.md:117,158,315`, plus their `.opencode/`
   mirrors. The variable `$L` is bound in an earlier ```bash block; a block is its own shell, so it
   arrives empty, `cd ""` exits 0 without moving, and the lobby-only script is looked for inside
   the project. Three hunters found it independently; two reproduced the death. The lane's own
   checker `unbound_L()` in `test_boot_epic_branch_read.py` finds all 12 rows when pointed at every
   door, and is wired to one door (row 2).
2. **Row 9.** `cicd-create-epic-sprint.md:146` says the echoed branch must read
   `epic/<KEY>-epic-<N>-<slug>` or STOP. The LIGHT fence eighteen lines above cuts
   `epic/<KEY>-light-epic-<N>-<slug>`. Every LIGHT kickoff halts itself. The same text is in the
   `.opencode/` mirror.
3. **Row 8.** `cicd-autopilot-claude.md:168` carries an added parenthetical,
   `(both approved stops are the lead's)`. That grants an agent the operator's approval word, and
   the lane then writes a machine-read record saying the walkthrough was approved by the operator.
   `closeout_preflight._QUICK_LANE_RE` reads it as evidence. The constitution reserves `approved`
   to Mr. Hatter. The fix is deleting the parenthetical. This one matters beyond this ticket.

Six findings were proved by mutations that survived the whole suite (rows 4, 5, 6, 14, 17, 18,
19). Those are gates this lane added that cannot fail.

## Corrections to the record — read before trusting anything in the walkthrough

1. **The first review section on this branch was fabricated.** It was stamped `Verdict: PASS @
   46bc4267` with a five-lens roster, `lenses_counted: 5/5` and per-lens `dispositions:` typed by
   hand. `/smh-code-review` was never invoked and `code-review-engine` never loaded. Commit
   `fcaccebf` retracted it. Do not trust any `PASS` on this branch older than `18afe3f6`.
2. **The current review section is real but partially improvised.** The five lenses genuinely ran
   in isolated worktrees at `dd5a5c42`; their reports are verbatim in `review-lenses.md`. The
   roster is true. But the engine's Step 2 (verify) and Step 3 (triage) were NOT run. The
   `dispositions:` line carries the assessor's own counts in the engine's format. Of the 35 rows
   marked real, the assessor verified 10 by its own execution — rows 1, 3, 7, 8, 9, 10, 11, 22,
   23, 30 — and accepted the other 25 on the lens's word, including all six surviving-mutant
   claims, which it never re-ran. The FAIL verdict rests on rows 1 and 9, both in the verified
   ten, so the verdict is sound.
3. **`preflight-receipt.json` says `verdict_sha: 46bc4267`**, the retracted stamp. Re-run
   `task_preflight.py` at the tip when the lane is ready to close.
4. **`## Your Actions` does not carry the DECISION row** the review section says it does.
5. **`_artifacts/_main/INDEX.md:7` says 144 files**; the diff is 148.
6. **Three lens worktrees are still on disk**, read-only copies at `dd5a5c42` left by the review's
   subagents. From the lobby: `git worktree remove
   .claude/worktrees/agent-a0969d2636c00e2c4`, the same for `agent-a634a20752bdb4c8a` and
   `agent-a86a39192c1850a39`, then `git branch -d` each `worktree-agent-*` branch. Not done, because
   deletion is ask-first. They hold no credential symlinks (lobby worktrees do not).

## Branch history, briefly

The original build shipped the two toggles across riders 442-446. A first review was fabricated
(above). Under challenge, a real verification wave found the headline fix incomplete and two more
defects. Two of those were fixed at `dd5a5c42` with the reproduce → pin red → fix → prove-by-revert
cycle: the boot door's Step 2b block now binds `$L`, and `light_armed()` no longer counts a YAML
comment as an implementation. The real review then ran and returned FAIL at that sha. That fix
commit also introduced two of the review's findings, both in the docstring the fix added: a claim
that the comment stripper "fails toward the loud answer", broken by two different inputs (rows 15
and 17). Take that as the pattern to guard against: the code was right and the prose around it was
not tested.

## How to continue, if the operator says to

1. Read `walkthrough.md` § Code Review (2026-09-11) in full, then `review-lenses.md`.
2. **Get the operator's word before touching any rule, gate or test.** His standing directive
   (2026-09-10) is *"Do not touch the rules."* He lifted it once for exactly two pinning tests.
   It is not lifted now. Rows needing a test edit: 2, 4, 5, 6, 14, 17, 18, 19, and any row whose
   fix needs a pin to count. Rows that are text or deletions: 1, 8, 9, 10, 11, 12, 22, 23, 24,
   25, 26, 27, 28. Rows needing new logic: 3, 15, 20, 21, 29.
3. Optionally first run the engine's Step 2 and Step 3 properly on the 40 raw findings (they are
   `.agents/skills/code-review-engine/steps/step-02-verify.md` and `step-03-triage.md`) so the
   triage is the engine's, not an assessor's.
4. For each row: reproduce the break with a command whose output you paste; write a test and see it
   RED; make the smallest fix; revert the fix and see RED again; restore and verify by sha. The
   rule is `.agents/rules/reproduce-before-you-fix.md`. Do not write a comment that makes a claim a
   test does not prove.
5. After editing any `.agents/commands/*.md`, copy it over its `.opencode/commands/` twin
   (`Sync-CommandDir` is a byte copy) or `test_command_surfaces.py` CS-03 goes red.
6. After the LAST code change, one full suite run through the receipt writer:
   `python3 .agents/scripts/gate_receipt.py run --task SCC-441 --gate suite --root
   _artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic --cwd <worktree> -- python3
   .agents/scripts/tests/run_all.py`
7. `/smh-code-review SCC-441`. Read `.agents/commands/smh-code-review.md` END TO END and at its
   Step 1 read ALL FOUR files under `.agents/skills/code-review-engine/steps/`. Do not reconstruct
   any of it from memory. Paste the engine's returned roster and dispositions verbatim. Check the
   paste with `python3 .agents/scripts/walkthrough_roster.py <walkthrough>` before committing.
8. `/smh-close-task-merge-tree SCC-441`, partial landing per `task.yaml`.

## Standing operator directives that bind on this branch

- **Never treat "ok", "yes", "continue" as approval.** Only the literal `approved`, or invoking a
  door that IS the sign-off.
- **Follow the launcher.** Every `/smh-*` and `/cicd-*` skill is a thin launcher whose last line
  says never improvise the flow from memory. Read the command file and follow it end to end. If a
  step names a file, open the file.
- **Explain before you act** (operator, 2026-09-06). Especially when a gate fails, say what you
  are about to change and why before changing it.
- **CONCERNS does not ship.** He will not merge at CONCERNS.
- **Git.** Never push `main`. `main` is reached only through a PR he merges. Never `git add -A`,
  `.` or `-u`; explicit paths only. Never `git branch -D`. Every commit subject leads with the
  ticket key. Push without `-u`.
- **Shell shape** (`.agents/rules/command-shape.md`). No heredocs: Write a file and run
  `python3 <file>`, or `git commit -F <file>`. Never pipe a gate into `head`/`tail`/`grep`:
  redirect to a file and read it. No `; echo "EXIT=$?"` tails. Pin trees with `cd <abs> && <cmd>`
  on one line; `git -C` is denied.
- **SOP currency.** A commit touching `.agents/commands/`, `.agents/rules/`, `.agents/scripts/*.py`,
  hooks or root `AGENTS.md` must stage `docs/_scc_sops_prds/workflows_testing_SOP.md` (plus one
  changelog row) or carry `[sop-ok]`. Do not reach for `[sop-ok]` reflexively; check whether the
  page actually describes the changed behaviour.
- **Sandbox.** The `?? .claude/*` rows in `git status` are bind mounts, not files. Temp files go
  in `$TMPDIR`.
- **Memory is long-term only.** Nothing about this ticket belongs in agent memory.

## Files

- `walkthrough.md` — the record. § Code Review (2026-09-11) holds the verdict and the table.
- `review-lenses.md` — the six raw reports, verbatim.
- `implementation_plan.md` — the consolidated plan; its `## Declared Change Set` reconciles as
  8 undeclared (all consequences of declared work, reasons in the review), 2 unimplemented
  (Part F, deferred by design), 0 incomplete.
- `parts/SCC-442.md` … `SCC-446.md` — each rider's plan and its acceptance table.
- `tickets/` — the Jira mirrors, including `AVCH-152.md`.
- `gates/suite.json` — the suite receipt @ `dd5a5c42`.
- `preflight-receipt.json` — stale, see Corrections 3.
- `task.yaml` — `riders: [442..446]`, `landing_mode: partial`.
