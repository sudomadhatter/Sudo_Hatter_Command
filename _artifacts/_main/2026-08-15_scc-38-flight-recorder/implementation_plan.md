---
IsArtifact: true
ArtifactMetadata:
  title: SCC-38 lane — flight recorder (SCC-133) + autopilot done-means-green spec (SCC-134), one branch
  type: implementation_plan
  date: 2026-08-15
---

# SCC-38 lane — SCC-133 flight recorder, then SCC-134 autopilot spec, then the folded parent edits

**Branch:** `chore/SCC-38-flight-recorder-autopilot-spec` (operator ruling this session: *"we will run
them both in one branch. one then the other"*). SCC-133 and SCC-134 are `riders:` of this lane —
they close in `/smh-close-task-merge-tree` Step 4's rider step, right before the parent.

**Master plan (canonical, annotated not replaced):**
`_artifacts/_main/2026-08-12_scc-38-enforcement-flight-recorder/implementation_plan.md`. The 08-15
assessment (Jira SCC-38 description) struck SCC-130/131/132; this file is the *execution* plan for
what survived. Ticket bodies refreshed 2026-08-15 carry the same scope word-for-word.

## Ground truth read this session (worktree @ `0b46c62`)

- The close-out already posts a per-ticket **Dev Record** to Jira (`jira_feed.py devrecord`: it
  scrapes `walkthrough.md` for decisions / pitfalls / follow-ons via `_SCRAPE_HEADS`, and the
  `Verdict:` line via `_VERDICT_RE`). Nothing aggregates ACROSS tickets, and nothing is local or
  machine-readable. That gap is the recorder.
- Gate receipts already exist per lane at `<task-artifacts>/gates/<gate>.json` — `result`
  (`pass|warn|fail|…`), `sha`, `dirty_tree`, `command`, `recorded_at`. The recorder READS these; it
  never re-runs a gate.
- SessionStart = `.agents/hooks/session-start-context.sh` (POSIX sh, "read files, print text, exit
  0", never blocks). It is the lobby's boot surface. `/cicd-boot-sprint-memory` is the child-project
  boot and runs from the centre.
- 20 KB active-context budget is already lint-enforced (`workflow_lint.check_active_context`) and
  compacted by `/cicd-prune-context`; `docs/.maps-journal.jsonl` already journals map drift. **Struck
  from SCC-133** (already shipped): budget enforcement, PICK UP/HAND OFF refresh, and routing
  long-tail failures to a `known-pitfalls` file (the ledger IS the store, and the centre has none).
- The two "manual learnings" questions: `cicd-update-sprint-memory.md:224`,
  `cicd-merge-epic-workingtrees.md:120-122`.
- Autopilot spec: `docs/_scc_sops_prds/autopilot_bmad_dev_loop.md` §6 "Resilience model" (seven
  guarantees, each already earned by an incident) — that is where SCC-134's law block belongs.
- Sibling lanes: none (`git worktree list` = main only; SCC-160 landed at `0b46c62`).

## Design decisions (made here, so the audit can attack them)

1. **Name:** `.agents/scripts/flight_recorder.py`, not the master plan's `command_center_closeout.py`
   — a name beside `closeout_preflight.py` that says "close-out" but records is a trap for the next
   agent. The master plan's Delta section records the rename.
2. **Event schema (v1) — ONE FILE PER EVENT, `_artifacts/_main/workflow-events/<YYYY-MM>/<KEY>_<sha7>.json`**
   ⚠️ AUDIT FINDING F2 — *not* an append-only `.jsonl`: two sibling lanes appending to one file
   conflict at every landing (the class `smh-merge-multiple-workingtrees` has to special-case as
   "ledger"); one file per event never conflicts and makes idempotency a file-exists check. Keys:
   `task, sha, tip, trigger, when` (the sha's own commit date from git — **never wall clock**, so
   `record` is reproducible and tests are deterministic), `changes[]`
   (`git diff --name-only <base>...<sha>`, `--base main` — the lane's own diff, merge-base
   three-dot, so a mid-lane absorb of `main` does not pollute it), `evidence` (walkthrough
   rel-path, review verdict, receipts by gate → `result@sha`), `expected` (`{"verdict":"PASS"}`),
   `outcome` (`{"verdict": <actual>}`), `decisions[] pitfalls[] followons[]` (reused from
   `jira_feed` — same scrape, one truth), and `fingerprints[]`.
   ⚠️ AUDIT FINDING F1 — **`sha` is the walkthrough's `Verdict: … @ <sha>` sha, not HEAD.** The
   recorder binds PRE-merge (see decision 9), so HEAD moves by one artifacts-only commit the moment
   the event itself is committed; keyed on HEAD, a resumed close-out would write a second event
   whose `changes` is the first event — the exact double-write idempotency exists to stop. The
   verdict sha is the house's existing notion of "the code that landed" (the preflight's
   code-fresh check uses it), is stable across artifacts-only commits, and a genuinely new verdict
   (more code, re-review) is a genuinely new event. `tip` records HEAD for the audit trail. No
   `Verdict:` line → exit 2, nothing written (the door already blocks on that).
3. **Fingerprints are MECHANICAL, four families, no NLP:** `rule-edited:<path>` (a file under
   `.agents/rules/` in `changes` — the honest proxy for "the prose failed and someone rewrote it");
   `gate-red:<gate>` (a receipt whose `result` is not `pass`); `verdict:<X>` (a review verdict that
   is not PASS); `mention:<token>` (a script/command/rule name inside a pitfall bullet —
   `[\w\-]+\.(py|sh|ps1|md)` or `/(smh|cicd)-[\w-]+`). The master plan's "post-fix regression"
   rung trigger is **dropped** — nothing here can detect one mechanically, and a rung an agent
   asserts by hand is the vacuous-prose class SCC-125 measured.
4. **Ladder counts DISTINCT tasks per fingerprint:** 1 = `evidence`, 2 = `candidate`, ≥3 =
   `action-required`. ⚠️ AUDIT FINDING F3 — **no materialized `candidates.json`.** A derived file
   that every lane regenerates is a guaranteed merge conflict on every landing and a second copy
   that can drift; the ledger is small (one file per close-out) and the ladder is a few hundred
   microseconds to recompute. `candidates` prints the full ladder (human-readable, `--json` for
   machines); `surface` prints only the action-required rungs. Both compute from the event files,
   every time.
5. **SCC-160 alignment:** `surface` prints *proposals*. Every action-required line ends with the
   evidence pointer (tasks + shas) and nothing mints anything. The recorder supplies recurrence
   evidence; the review's relevance triage / the operator's word decide.
6. **Idempotent on `(task, sha)`:** a second `record --apply` for the same pair prints the stored
   event and writes nothing (prime-agent journaling rule; also what makes a resumed close-out safe).
7. **Fail-soft where the door needs it:** `record` refuses (exit 2) when the walkthrough is missing —
   the door already blocks on that — but a missing `gates/` dir is fine (some lanes have no receipts
   yet); `surface` **always exits 0** (a SessionStart hook must never block).
8. **Two consumers of `surface`, both real:** the SessionStart hook (mechanical, tested by running
   the hook) and one line in `/cicd-boot-sprint-memory` Step 3 (guardrails). Reader wiring or it is a
   write-only DB.
9. **`record` binds to `/smh-close-task-merge-tree` as Step 2.5 — after the gate is green,
   BEFORE the merge**, in the worktree, and its output is committed as one artifacts-only commit
   (`<KEY> chore(recorder): flight event @ <sha7>`) that rides the merge. ⚠️ AUDIT FINDING F1 —
   the master plan's "post-merge" placement would write an untracked file into `main`'s working
   tree after the merge, and committing it there is a direct commit on `main` outside the token
   the door just spent — the exact thing the write gate exists to refuse. Pre-merge keeps the
   ledger travelling like receipts do. Artifacts-only, so the SKIP machinery (content-based
   freshness) stays valid. A `record` failure never blocks the merge — report it, like a
   receipt.

## Steps — each acceptance item → the assertion that proves it

### SCC-133

| # | Step | RED (fails first) → GREEN |
|---|---|---|
| A1 | `flight_recorder.py record` — one event file + idempotent replay | `tests/test_flight_recorder.py --case "A1"`: temp repo with a `main` + a lane branch (a rule file edited, a walkthrough with `Verdict: PASS @ <sha>`, one `pass` receipt, one `fail` receipt); first `record --apply` → exactly one `workflow-events/<YYYY-MM>/<KEY>_<sha7>.json` with every schema key, `sha` = the verdict sha, `changes` = the lane's files only; second call (even after an extra artifacts commit moved HEAD) → still one file, output says already-recorded, exit 0. Negatives: no walkthrough → exit 2 + nothing written; walkthrough without a `Verdict:` line → exit 2. RED = script absent |
| A2 | `candidates` — fingerprints + ladder | `--case "A2"`: seed event files directly (the schema is the contract): 3 tasks sharing `rule-edited:X` → `action-required` carrying 3 tasks + 3 shas + the "commission the script" line; 2 sharing `gate-red:suite` → `candidate`; 1 → `evidence`; the SAME task at two shas counts ONCE. Negative control: an event with `fingerprints: []` produces no rung; `--json` output parses |
| A3 | `surface` + hook wiring | `--case "A3"`: empty ledger → no output, exit 0; seeded action-required → one line, exit 0. Then run `.agents/hooks/session-start-context.sh` with `CLAUDE_PROJECT_DIR=<temp repo>` and assert the proposal line is in its stdout and exit 0. RED = hook has no call |
| A4 | Bind to the door | `smh-close-task-merge-tree.md` Step 4 gains the `record` line; `workflow_lint --toolkit-only` exit 0; SOP + boot-sprint-memory Step 3 line ride the same commit; `test_command_surfaces` still green (door parity) |
| A5 | Conditional learnings question | inspection: both close-out files ask only when Step 3 routed nothing; grep pasted RED (unconditional wording) → GREEN |
| — | INDEX + scripts INDEX rows | `.agents/scripts/INDEX.md` gains the row; `_artifacts/_main/INDEX.md` gains this folder's row; `check_maps.py --depth3-only --strict` exit 0 |

### SCC-134

| # | Step | RED → GREEN |
|---|---|---|
| B1 | §6 of `autopilot_bmad_dev_loop.md` gains **"Done-means-green — the law the engines port"**: (1) a stage's gate is a script with an exit code, never self-assessment; (2) retries engine-owned, deterministic, hard-bounded, no agent authority to spawn more; (3) skip-if-unchanged; (4) park-with-receipt on exhaustion; (5) idempotent `(stage, sha)` resume — plus the explicit line that red gates STAY human-in-the-loop (dropped, not deferred). ⚠️ AUDIT FINDING F4 — the planned cross-link from `cicd-autopilot-claude.md` is CUT: it would touch a command surface (three autopilot commands + their doors) for a pointer the ticket does not ask for; `cicd-autopilot-deepseek4.md` already links the spec once. | `grep -c "Done-means-green" <spec>` = 0 (RED) → ≥1; link + anchor sweep over the touched files clean; SOP rides |

### Parent SCC-38 (folded SCC-130)

| # | Step | RED → GREEN |
|---|---|---|
| C1 | `## Delta (2026-08-15)` appended to the 08-12 master plan (struck subtasks, the rename, the two dropped items) ; `_my_resources/open_tasks/proposal_graphrag_executiblity.md` → ≤12-line pointer to the master plan | `grep -c "Delta (2026-08-15)"` 0 → 1; `wc -l` of the proposal ≥100 → ≤12 and its link resolves |

## Order of work

**C1 is the FIRST commit** (the ticket text says so, and the other team read it the same way) →
SCC-133 (A1→A5, one suite file, commit per green step) → SCC-134 (B1) → walkthrough, `task.yaml`
with `riders: [SCC-133, SCC-134]`, receipts, mutant sweep, `/smh-code-review`.

## Mutant table (declared before mutating; every mutant drawn from the CODE, killer named)

Filled in at Step 3 once the code exists — the rule (`tests-must-gate-for-real` § Mutation Testing)
is that rows name real edits to real lines. Planned families: idempotency reading HEAD instead of the
verdict sha (killer A1 replay-after-artifacts-commit); ladder threshold `>= 3` → `> 3` (killer A2
action-required); distinct-task count → raw count (killer A2 same-task-twice); `surface` returning
non-zero on empty (killer A3 empty); `rule-edited` prefix widened to `.agents/` (killer A2 negative
control); `gate-red` reading `pass` as red (killer A1's pass receipt); `changes` two-dot instead of
three-dot (killer A1 after a seeded absorb of main).

## Verification (all bare, exit codes read)

```bash
python3 .agents/scripts/tests/test_flight_recorder.py            # then through gate_receipt.py run
python3 .agents/scripts/gate_receipt.py run --task SCC-38 --gate suite --root <this folder> --cwd <tree> -- python3 .agents/scripts/tests/run_all.py
python3 .agents/scripts/workflow_lint.py --toolkit-only
python3 .agents/scripts/check_maps.py --root . --depth3-only --strict
```

## Boundaries

- Vendor nothing; stdlib only; no transcripts stored — pointers, outcomes, fingerprints.
- No auto-minting, no ticket rows, no candidate "queue" — proposals only (SCC-160).
- No engine edits (`Projects/*` autopilot .ps1) — SCC-134 is spec text; engine propagation is its
  own standing drift debt.
- No `.github/` change (eject tripwire) — the CI job is untouched.
- Generated surfaces via `/smh-sync-agents` only.

## Self-Audit (2026-08-15) — PRE-WORK, Full

**Repo:** `Sudo_Hatter_Command` · **Branch:** `chore/SCC-38-flight-recorder-autopilot-spec` (from
`rev-parse`) · **Ticket:** SCC-38 (riders SCC-133, SCC-134) · **Plan:** this file.

**Phase 0 — scope + checkable list.** Change set: NEW `.agents/scripts/flight_recorder.py` + NEW
`tests/test_flight_recorder.py` + `scripts/INDEX.md` row · EDIT `.agents/hooks/session-start-context.sh`
(one `surface` call) · EDIT `smh-close-task-merge-tree.md` (Step 2.5), `cicd-boot-sprint-memory.md`
(Step 3 line), `cicd-update-sprint-memory.md:224`, `cicd-merge-epic-workingtrees.md:120-122`
(conditional question) · EDIT `docs/_scc_sops_prds/autopilot_bmad_dev_loop.md` §6 ·
EDIT the 08-12 master plan (Delta) + `open_tasks/proposal_graphrag_executiblity.md` (→ pointer) ·
NEW `_artifacts/_main/workflow-events/` (born empty; first event is this lane's own close-out) ·
`_artifacts/_main/INDEX.md` row · SOP doc rides every usage-surface commit. Right-size: **Full**
(new script + a hook + command bodies). Checkable list = A1–A5, B1, C1 above; traceability both
ways clean after F4 cut the cross-link (a step tracing to no item). Lane check: no deployable path
(`.github/` untouched) → `/smh-close-task-merge-tree` is the door.

**Phase 1 — blast radius.** No sibling lanes (`git worktree list` = main only). New script: no
callers yet; its test + INDEX row ship with it. Touched commands have **no `-AP` twins** (only
code-review / dev-story-tests / self-audit do); their four doors regenerate via `/smh-sync-agents`
+ `test_command_surfaces` parity. `session-start-context.sh` has no test today — the A3 hook run IS
its first. `python3` vs `python`: the hook grows `command -v python3 || command -v python`.
`jira_feed` import from the recorder: module-level regexes only, no side effects at import (verified
by reading `_SCRAPE_HEADS` / `_VERDICT_RE` / `scrape_bucket`). Memory store untouched.

**Phase 2 — over-engineering.** New script vs a `jira_feed` subcommand: justified — `jira_feed` is
Jira-bound (acli, network) and 1,848 lines; the recorder is local, must run inside a SessionStart hook
in milliseconds with no credentials, and imports the two scrape helpers rather than cloning them.
Fired and CUT: F3 (materialized `candidates.json`), F4 (autopilot cross-link). Fired and REDESIGNED:
F1 (post-merge write / HEAD-keyed idempotency), F2 (append-only jsonl). Kept: `--json` on
`candidates` — required by A2's machine assertion, not "future flexibility". No new rule, no new
command, no flag without an item.

**Phase 3 — pre-mortem.**

| Scenario | Handled | |
|---|---|---|
| Other machine | hook uses `command -v python3 || command -v python`; script stdlib-only | ✅ |
| Fresh clone | SessionStart hook is `.claude/settings.json` (travels); no `core.hooksPath` dependency | ✅ |
| Fires on someone else's commit | nothing here is a commit gate | ✅ n/a |
| Escape hatch | `record` failure never blocks merge or `Done` — report like a receipt | ✅ |
| Empty input | `surface` on empty ledger prints nothing/exit 0 by design (a boot surface, not a gate) — the TEST carries the positive control | ✅ |
| Four caches | command edits → `/smh-sync-agents`, parity test | ✅ |
| Sibling lands first | none live; per-event files make future concurrent lanes conflict-free | ✅ |
| Rollback | all additive; `git revert` of the lane; no Jira transition until the door | ✅ |

Silent failure that survives the walk: a close-out that forgets Step 2.5 records nothing and looks
fine — mitigated by the door's numbered step + the walkthrough Evidence row; a mechanical guard is
NOT added here (a gate that blocks the merge on a missing recorder event is new law needing its own
quoted ruling — proposed in `## Your Actions` at close-out, not shipped).

**Findings table**

| Where | Sev | Failure scenario | Disposition |
|---|---|---|---|
| decision 9 (was Step 4 post-merge) | important | untracked ledger file left in `main`'s tree post-merge; committing it = direct main commit outside the token | REDESIGNED → Step 2.5 pre-merge, artifacts-only commit (F1) |
| decision 2 (was HEAD-keyed) | important | resumed close-out double-writes because committing the event moved HEAD | REDESIGNED → keyed on the walkthrough's verdict sha (F1) |
| decision 2 (was `.jsonl`) | moderate | two lanes' appends conflict at every landing | REDESIGNED → one file per event (F2) |
| decision 4 (`candidates.json`) | moderate | derived file conflicts + drifts | CUT → compute on read (F3) |
| B1 cross-link | minor | command-surface touch the ticket did not ask for | CUT (F4) |

Four gates: verification strategy present (every row names its command + output) ✅ · irreversible:
none — no delete, no rename, no transition, no main write ✅ · vague steps: Step 2.5's exact
wording is written at build time from the door's own style, mutant rows filled from the code ✅ ·
convention fit: naming law (`smh-`/`cicd-` untouched), artifacts folder, INDEX rows, receipts,
riders in `task.yaml` ✅.

Audit verdict: GO
