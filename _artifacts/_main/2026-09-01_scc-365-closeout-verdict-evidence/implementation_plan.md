# SCC-365 — Close-out accepts a `Verdict: PASS` no suite ever backed

**Lane:** `chore/SCC-365-closeout-verdict-evidence` · worktree `.claude/worktrees/scc365-closeout-verdict`
**Repo:** `Sudo_Hatter_Command` (lobby) — `closeout_preflight.py` is run against BOTH repos via `--project`, so fixing it here covers AviationChat too.
**review-runtime:** fan-out

---

## 1. What is actually broken

`closeout_preflight.py` is the only mechanical thing standing between a story's `Verdict: PASS`
and its close-out. It reads the verdict and reports it, and it never asks the verdict to show
its work. Measured in the live script, not inferred:

| Gap | Line | What the code does |
|---|---|---|
| 1 — verdict never compared to evidence | `:341` | `PASS`/`CONCERNS` → `rep.info(...)`. Only `FAIL` errors. |
| 2 — the receipt check is off by default | `:626`, `:578` | `--require-gates` defaults to `""`; `check_gates` returns on its first line when empty. |
| 3 — a missing receipt only warns | `:583-585` | `rep.warn("gates", "<gate>: no receipt ...")`, carrying *"advisory for one sprint"* — a ruling dated **2026-08-02** that expired and was never revisited. |

Net: a walkthrough carrying `Verdict: PASS` with no receipt file at all prints
`VERDICT: clear to close out`. That is the AVCH-106 shape.

Note the asymmetry the ticket calls out and the code confirms: a receipt that **exists** and
records fail/stale DOES error (`gr.check_receipt`). Only a receipt that was **never written**
slips through — the gate is strict about evidence it can see and silent about evidence that is
absent, which is backwards.

> ⚠️ **AUDIT FINDING (Lens 3, HIGH) — there is a fourth gap, and it is the one that would have
> made the other three cosmetic.** `.agents/commands/cicd-update-sprint-memory.md:215` is the step
> that actually decides the `done` flip, and it reads, verbatim:
> *"**WAIVED / missing / stale** (verdict on an old HEAD) → flip. **Fail-open: a gate-read error
> never blocks close-out.**"* — five lines under its own copy of the same expired ruling
> (`:208`, *"⏳ Remove `--advisory` at the close of the first full sprint after this landed
> (ruling 2026-08-02)"*). So today the new error would print at Step 0.6 and be overruled by
> prose at Step 4, the story would flip to `done`, and the flip would then permanently disarm the
> new check for every downstream re-run. **Gap 4 is in scope by the ticket's own words** — bullet
> 2 says *retire the expired 2026-08-02 ruling* — and it is retired in both places or in neither.

---

## 2. The design decision the ticket did not name — and it is the one that matters

The ticket's bullet 3 says *"decide and enforce a default for `--require-gates`."* The obvious
reading — set `default="suite"` — **is wrong, and it would get this gate disarmed within a week.**

`closeout_preflight.py` has four callers, not one:

| Caller | Passes `--require-gates`? | Runs when the story is… |
|---|---|---|
| `cicd-close-story-merge-tree.md:86` | `[optional]` ← the hole | `review` (pre-flip) |
| `cicd-merge-epic-workingtrees.md:73` | yes, mandatory | `review` (pre-flip) |
| `cicd-update-sprint-memory.md:82` | **no** | `review` (pre-flip) |
| `cicd-prune-worktree.md:43` | **no** | **`done`** (post-flip) |

Measured against the live AviationChat tree: `_bmad-output/gates/` holds ten story receipt dirs.
Epic 23 alone has **13** story lanes, and `23-1` and `23-2` carry `Verdict: PASS` with no receipt
at all. A hardcoded `default="suite"` makes `/cicd-prune-worktree` refuse on them, and the only
remedy the error could name is *"re-run the suite"* on a `done` story whose lane is already gone.
This file documents that exact failure mode twice, at `OVERVIEW_CUTOFF` and at
`walkthrough_roster.CUTOFF`: **a gate whose refusal has no reachable fix is a gate that gets
disarmed, and then nothing is checked at all.**

**The date cutoff those two use does not work here.** `roster.lane_date()` reads a `YYYY-MM-DD`
prefix off the artifact folder — and story lanes do not have one. The live convention is
`_artifacts/epic_23/story-23-9-<slug>/`; `lane_date` returns `None` for all 13 epic-23 lanes and
every epic-16 story lane. A date cutoff is inert here: it either exempts everything or blocks
everything.

**So the scope limiter is the board status, and it is a better one.** The question a cutoff is
trying to answer is *"is the remedy reachable?"* — and the board answers it directly.

> ⚠️ **AUDIT FINDING (Lens 2 + Lens 3, `wf_common.py:34`) — "non-terminal" was the wrong set.**
> `TERMINAL = {"done", "descoped"}`, but `ALL_STATUSES` also holds `deferred`, `deferred-v3` and
> `optional`, and the live AVCH board carries **13 `deferred`/`deferred-v3` rows**. A story
> reviewed and then parked has a pruned lane and no reachable remedy — the exact failure this
> section argues against. Blast radius today is zero (none of the 16 non-terminal keys carries a
> `Verdict:` line), so this is a scope correction, not a live bug.
>
> **The correct set is the FLIP-ELIGIBLE states, and the house already defines it.**
> `cicd-update-sprint-memory.md:204`: *"Idempotent: only `ready-for-dev`/`in-progress`/`review`
> advance; never downgrade."* Those are exactly `wf.PROGRESS_ORDER` strictly between `backlog`
> and `done`, so the rule is expressible against the existing vocabulary with no new set to keep
> in sync: `0 < wf.STATUS_RANK.get(status, -1) < wf.STATUS_RANK["done"]`. `backlog`, `deferred*`,
> `optional`, `descoped` and `done` all fall out exempt, each for the same reason: **no lane is
> live, so no suite can be run.**

> A story in a flip-eligible state is being closed right now, and running the suite through
> `gate_receipt.py` is one command away. Every other state either has no lane yet or had its lane
> pruned.

**And the required evidence is derived from the claim, not hardcoded:** a verdict of
`PASS`/`CONCERNS` is a claim that a gate was green, so `suite` joins the required list. A
walkthrough with no verdict, or `FAIL`/`WAIVED`, demands nothing new — the same verdict
vocabulary `verdict_receipt.py` (SCC-363) gates at commit time, which deliberately leaves `FAIL`
and `WAIVED` alone.

> ⚠️ **AUDIT FINDING (Lens 3, `verdict_receipt.py:60-65`) — do not oversell that parity.** That
> gate is *"THIS GATE RUNS IN THE COMMAND CENTRE ONLY … AGY_AVIATIONCHAT has no verdict stage."*
> The shared thing is the **verdict vocabulary**, not the coverage. In AviationChat, and on any
> machine where `core.hooksPath` was never set, `closeout_preflight` is the **only** enforcement
> point — which is the argument for making it hard, and for closing Gap 4.

---

## 3. The other thing the audit found: `--require-gates suite,ruff,pyrefly` demands receipts nothing writes

> ⚠️ **AUDIT FINDING (Lens 1 watch-item, promoted to blocking on verification) — HIGH.**
> `/cicd-code-review.md:356` stamps exactly one gate:
> `gate_receipt.py run --story <id> --gate suite --cwd <worktree> -- <the real command>`.
> Nine of the ten live AGY story receipt dirs hold `suite.json` **alone**; only `19-1` also holds
> `ruff.json` and `pyrefly.json`.
>
> So the moment a missing receipt becomes an ERROR, both doors that pass
> `--require-gates suite,ruff,pyrefly` — `cicd-close-story-merge-tree.md:86` (which this ticket is
> making mandatory) and `cicd-merge-epic-workingtrees.md:73` (already mandatory) — hard-block
> **every** close-out, on two receipts the review step has never written.
>
> **Fix: both doors demand `--require-gates suite`** — what the system actually stamps — with one
> line saying extra gates are named only when that lane stamped them. Demanding evidence nobody
> produces is how a gate gets deleted, not how it gets obeyed.

---

## 4. Acceptance — every row is a command, not a sentence

| | Statement | The assertion that proves it |
|---|---|---|
| **A** | A flip-eligible story whose walkthrough records `Verdict: PASS` with **no** `suite` receipt makes the preflight exit **2**, with `--require-gates` omitted entirely | `test_closeout_preflight.py` case `EV1`: run the script on the fixture, assert exit 2 and an `[ERROR] gates` row naming `suite` |
| **B** | The same story **with** a usable, current `suite` receipt exits with no `gates` error — and the AVCH-106 replay is refused while its fixed twin passes | cases `EV2` (green receipt → no gates error) and `EV6` (AVCH-106 fixture refused; same fixture + receipt accepted) |
| **C** | A `done` story, **and** a `deferred` one, with a `PASS` and no receipt gain **no** new error — `/cicd-prune-worktree` stays usable on closed and parked history | case `EV3`, both statuses |
| **D** | `FAIL` and `WAIVED` acquire no receipt demand (parity with `verdict_receipt.py`) | case `EV4` |
| **E** | With `--require-gates <g>` passed explicitly, a **missing** receipt for `<g>` is an `[ERROR]`, not a `[WARN]`, and the message names both the directory it searched and the command that fixes it | case `EV5`: assert the row is ERROR, exit 2, and the message contains the receipt dir and `gate_receipt.py run` |
| **F** | The close-out door's preflight **invocation** carries `--require-gates suite` **unbracketed**, and both doors stop demanding `ruff,pyrefly`; pinned on the resolved call, not the file | `test_command_surfaces.py` case `CS-14 C2`, reusing `joined_invocation` over **both** doors' resolved calls and asserting `"[--require-gates" not in call` **and** `"--require-gates" in call` **and** `"ruff" not in call and "pyrefly" not in call` |
| **G** | A story resolved by its **long** board key finds the same receipt as the short id — the mis-lookup Lens 3 reproduced live no longer exists | case `EV7`: same fixture, both `--story` spellings, identical `gates` rows |

> ⚠️ **AUDIT FINDING (Lens 2 + Lens 3, `test_command_surfaces.py:2365-2366`) — row F was vacuous
> as first written.** `CS-14 C` asserts only `bool(call) and "--require-gates" in call`, and the
> **bracketed** form already contains that substring: run against the unmodified door,
> `joined_invocation` returns `'… \        [--require-gates suite,ruff,pyrefly]'` and the assertion
> is **True today**. A faithful reuse cannot go red, which is the exact `M20` shape the comment
> above `CS-14 C` warns about. F now asserts the **bracket's absence**, which is the change.

> ⚠️ **AUDIT FINDING (Lens 3, `closeout_preflight.py:679-680`) — HIGH, reproduced live on
> AviationChat.** `main()` passes the raw `args.story` to `check_gates` while every other check
> gets the resolved board `key`, and `gr.receipt_dir` keys off that raw string. Measured:
> `--story 23-9` → `[ERROR] gates: suite: STALE - passed at 808dce60` (receipt found);
> `--story 23-9-flight-status-drawer-polish-active-curriculum` → `[WARN ] gates: suite: no
> receipt` — same tree, same story, and `check_artifacts` resolved the walkthrough correctly both
> times. Today that is a harmless warning. **This plan promotes it to a blocking false refusal**,
> and the long form is reachable: `/cicd-prune-worktree` Step 0.2 resolves a long slug before
> Step 0.3 asks for "the id". Fixed in-lane as acceptance row **G** — the lane's own change
> creates the hazard, so the lane closes it.

Killed-mutant requirement rides on all seven: one mutant per code change, drawn **from the code**,
each naming the case that must kill it, run as one sweep through `mutation_sweep.py`.

---

## 5. Steps

1. **RED first.** Write `EV1`–`EV7` in `test_closeout_preflight.py` and `CS-14 C2` in
   `test_command_surfaces.py` against the unmodified script and doors. Paste the red. Read *which
   line raised* — a fixture that dies in setup is not a red.

   > ⚠️ **AUDIT FINDING (Lens 2, HIGH) — the existing suite goes red too, and the first plan did
   > not say so.** The shared `lane_repo` fixture in `test_closeout_preflight.py` is exactly the
   > shape this change blocks: board `30-1-fresh: review`, walkthrough `**Verdict: PASS**`, and
   > `_bmad-output/gates/30-1` does not exist. Under the change, `rep.counts()` becomes non-zero
   > and `main()` prints `BLOCKED - resolve the errors above` instead of a `STALE` verdict, so
   > **`FR0` (:751), `FR2` (:764), `FR5` (:794), `FR6` (:828) and `MEM3` (:879) all fail** —
   > they assert on `rc == 1` and on the substring `STALE`. `run_all.py` (step 6) fails with them.
   > **Re-base those five as part of this step**, and say in the walkthrough which changed and
   > why; a pre-existing case that must move is evidence the change has teeth, but only if it is
   > moved deliberately and named. Baselines to beat, measured before any edit:
   > `test_closeout_preflight.py` **69/69**, `test_command_surfaces.py` **274/274**.

2. **Gap 3** — in `check_gates`, the missing-receipt branch becomes `rep.err`, and the expired
   2026-08-02 comment goes with it. **Keep the explicit branch rather than delegating to
   `gr.load_receipt`:** its string is `"{gate}: NO RECEIPT - the gate has no evidence it ran"`,
   which names no command and no directory, and a blocking error whose remedy is unnamed is the
   thing §2 says gets routed around. The new message names the directory searched and the
   `gate_receipt.py run …` line that fills it.
3. **Gap 5 (row G)** — resolve the receipt directory against what is on disk before reading it:
   try `wf.norm_id(story)`, and where that directory is absent, match the existing directories
   under `wf.GATES_REL` with `wf.slug_matches` (which already carries the `21-8` vs `21-8b`
   separator guard). Exactly one match wins; zero or several fall back to the literal so the
   error names the directory it actually searched.
4. **Gaps 1 + 2** — `check_artifacts` returns the set of verdicts it read; a new
   `require_evidence_gate(require, claimed, status, rep)` prepends `suite` when the story is
   flip-eligible and a `PASS`/`CONCERNS` was claimed, emitting one `info` row saying why. It
   prepends **only when `suite` is not already required**, so the two doors that name it
   explicitly do not get the row twice. `main` threads the two together — `check_artifacts` is
   already called before `check_gates`, and `board[key]["status"]` is already in scope.
5. **Gap 4 (the flip door)** — `cicd-update-sprint-memory.md`: drop `--advisory` and the expired
   ⏳ line at `:205-208`, and delete `Fail-open: a gate-read error never blocks close-out.` at
   `:215`. A missing or unreadable receipt now holds the flip, exactly as `FAIL` does.
6. **The doors** — unbracket the flag at `cicd-close-story-merge-tree.md:86` and narrow **both**
   doors to `--require-gates suite` (§3). Add the missing `# PC: \`python\`` annotation to the
   close-out door's preflight invocation — the file annotates `jira_feed.py` three lines below and
   `/cicd-prune-worktree` annotates its own call, so this one line is why the PC's only pre-flip
   enforcement point never runs. Fix the script's own stale docstring usage line (`:10` still
   advertises `[--require-gates ruff,pytest]`).
7. **The opencode mirrors — THREE doors, not two.** `cicd-close-story-merge-tree`,
   `cicd-update-sprint-memory` **and** `cicd-merge-epic-workingtrees` each have a **byte-identical**
   `.opencode/commands/` copy (`diff -q` silent on all three: 31659 B, 22872 B, 27721 B), and
   `test_command_surfaces.py` CS-03 returns `ok` only when `body == brain`. Edit both halves of each
   identically or `run_all.py` goes red. (`.agents/workflows/`, `.roo/commands/` and
   `.claude/skills/` are thin launchers — `grep -c "require-gates"` is 0 on each and they are
   unaffected.)
8. **SOP currency** — `workflows_testing_SOP.md:2443` describes what `closeout_preflight.py`
   catches. It now catches one more thing; the row is updated in the same commit. `sop_currency.py`
   is armed, `_SURFACES` covers `.agents/commands/*.md` and `.agents/scripts/*.py`, and
   `_EXEMPT_PREFIXES = (".agents/scripts/tests/",)` exempts the two test files. No `[sop-ok]`.
9. **Discharge the standing memory obligation this lane closes.**
   `_artifacts/_memory/workflow-enforcement-scripts.md:38` reads *"⏳ Flip owed: drop `--advisory`
   from the close-out receipt gate after the first full sprint."* Step 5 performs that flip, so the
   line becomes false the moment this lands and would tell every future session a discharged
   obligation is still open. Struck through the **Claude harness memory flow** — a sanctioned writer
   per `AGENTS.md` §7 — and carried onto this lane by that section's four-step procedure (write it,
   copy it into this worktree, restore the shared checkout, commit it here with explicit paths). No
   gate reds on it; the fix is currency, not enforcement.
10. **Prove it** — full `run_all.py` through `gate_receipt.py run --gate suite` on the clean tree,
   then the mutation sweep, then `/smh-code-review`.

---

## 6. What this does NOT do

- **No date cutoff, no backfill.** Closed and parked history is exempt by status, permanently, and
  no walkthrough is rewritten.
- **`--require-gates` keeps `default=""`.** The baseline is derived from the verdict claim. A
  caller that names extra gates still gets them checked, strictly, as before.
- **`task_preflight.py` is untouched.** The Task lane already answers this correctly — verified:
  `if not receipts: rep.info(… "the full gate runs (fail toward running, never toward
  trusting)")`. Only the story lane reports without running anything, which is why only the story
  lane has this hole.
- **`Projects/sudo-command-center` is out of scope.** Lens 2 found a second copy of
  `closeout_preflight.py` there carrying the identical expired ruling — but it is a **separate git
  repo** (a teaching-edition export with keys rewritten, `SCC-210` → `HISTORY-210`), nothing in
  `.agents/` regenerates it, and it is already behind by more than this change. Per
  `cross-repo-work-needs-a-ticket-per-repo`, refreshing it is that repo's own ticket, not this
  lane's.

---

## Declared Change Set

- EDIT `.agents/scripts/closeout_preflight.py` — gaps 1, 2, 3, 5 and the stale docstring usage line → A, C, D, E, G
- EDIT `.agents/scripts/tests/test_closeout_preflight.py` — cases EV1–EV7, the AVCH-106 replay fixture, and the five re-based FR/MEM cases → A, B, C, D, E, G
- EDIT `.agents/scripts/tests/test_command_surfaces.py` — case CS-14 C2, the non-vacuous door pin → F
- EDIT `.agents/commands/cicd-close-story-merge-tree.md` — unbracket and narrow the flag, add the PC annotation → F
- EDIT `.opencode/commands/cicd-close-story-merge-tree.md` — the byte-identical mirror CS-03 compares → F
- EDIT `.agents/commands/cicd-merge-epic-workingtrees.md` — narrow to `--require-gates suite` → F
- EDIT `.opencode/commands/cicd-merge-epic-workingtrees.md` — the byte-identical mirror CS-03 compares → F
- EDIT `.agents/commands/cicd-update-sprint-memory.md` — retire the expired ruling's twin and the fail-open clause → A, E
- EDIT `.opencode/commands/cicd-update-sprint-memory.md` — the byte-identical mirror CS-03 compares → A, E
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — the `closeout_preflight.py` row now names the evidence check → F
- NEW `_artifacts/_main/2026-09-01_scc-365-closeout-verdict-evidence/sweep.json` — the mutant table → A, C, D, E, G
- NEW `_artifacts/_main/2026-09-01_scc-365-closeout-verdict-evidence/walkthrough.md` — the close record → A, B, C, D, E, F, G
- NEW `_artifacts/_main/2026-09-01_scc-365-closeout-verdict-evidence/task.yaml` — the lane manifest, read by the close-out → A

## Sibling lanes

Three live lanes, not two. `chore/SCC-358-memory-and-sync` (`_artifacts/_memory/` only) and
`chore/SCC-366-claude-permission-fix` (`.claude/settings.json`, 0 commits). **Zero intersection
with this plan's declared set — no landing-order dependency; any lane may land first.**

---

## Self-Audit (2026-09-01)

**Level:** LEDGER+BLAST (a script others import, two door surfaces, the SOP) · **Mode:** PRE-WORK ·
**Runtime:** fan-out, three lenses blind to each other · **Round:** 1 of 2

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every path/script/command/rule/door the plan names resolved; all 11 line-number citations verified against the real files
             declared_change_set.py parse -> present:true, 8 entries, incomplete:[] , exit 0
             portability: no bare python/python3 in plan text; every edited file stdlib-only; no venv
             lane fit: no backend|frontend|firebase|functions|mobile|.github path -> local lane, door is /smh-close-task-merge-tree
             six design claims (a)-(f) re-measured: (a) TRUE (b) TRUE (c) MIXED-FALSE (d) TRUE (e) TRUE (f) TRUE
             mutation strategy vs tests-must-gate-for-real.md 94-97 / 110-115: SATISFIED
             scope ledger precondition met (6 acceptance rows, each a named case + assertion); 3 NEW artefacts, 0 empty acceptance cells; caller counts run
read:        implementation_plan.md (full) · acli jira workitem view SCC-365
             .agents/scripts/{closeout_preflight,gate_receipt,verdict_receipt,wf_common,walkthrough_roster,task_preflight,mutation_sweep}.py
             .agents/scripts/tests/test_command_surfaces.py:520-545,590-705,2302-2375
             .agents/commands/{cicd-close-story-merge-tree,cicd-merge-epic-workingtrees,cicd-prune-worktree,cicd-update-sprint-memory,smh-close-task-merge-tree}.md
             .opencode/commands/cicd-close-story-merge-tree.md · .agents/workflows/cicd-close-story-merge-tree.md
             docs/_scc_sops_prds/workflows_testing_SOP.md:2438-2450 · .agents/rules/tests-must-gate-for-real.md:88-128
             Projects/AGY_AVIATIONCHAT/_bmad-output/gates/** · _artifacts/epic_23/** · _artifacts/epic_16/**
verdict:     findings below
```

```
lens:        2 Parity + Blast
checks_run:  enumerated every closeout_preflight.py reference -> 4 invoking doors + 2 opencode mirrors + INDEX + rules + 8 tests
             false-block sweep on the LIVE AGY board: 16 non-terminal story keys x (Verdict? / suite receipt?)
             re-measured the plan's live numbers: _bmad-output/gates/ = 11 dirs (10 story), epic 23 = 13 children
             baselines: test_closeout_preflight.py 69/69 · test_command_surfaces.py 274/274
             probed the lane_repo fixture under --require-gates suite -- reproduced the row the plan turns into an ERROR
             traced the verdict computation at closeout_preflight.py:683-698 to see which assertions collapse
             four-door parity: byte-size + diff -q + grep across .opencode / .agents/workflows / .roo / .claude/skills
             ran joined_invocation (CS-14 C's own helper) against the UNMODIFIED close door
             twin check: task_preflight.check_gate gate-skip logic, lines 1319-1470, in full
             cross-repo find for closeout_preflight.py; diffed the second copy; read port-checklist.md
             sop_currency arming (SOP-ENFORCE marker + _SURFACES + _EXEMPT_PREFIXES) and the SOP row at :2443
             gr.receipt_dir id normalization; sibling worktrees after env -u GITHUB_TOKEN git fetch origin main; risk_seam classify
read:        as lens 1, plus .agents/scripts/{sop_currency.py,INDEX.md}
             .agents/scripts/tests/{test_closeout_preflight,test_command_surfaces,test_door_preflight_order}.py
             .agents/rules/port-checklist.md · .roo/commands/ · .claude/skills/cicd-close-story-merge-tree/SKILL.md
             Projects/sudo-command-center/.agents/scripts/closeout_preflight.py:427-431
             Projects/AGY_AVIATIONCHAT/_bmad-output/implementation-artifacts/sprint-status.yaml
verdict:     findings below
```

```
lens:        3 Pre-Mortem
checks_run:  N1 SILENT   - Report.err/warn/info/counts/exit_code/print_human + the --json branch; what each caller is told to do with exit 2
             N2 OTHER-MACHINE - verdict_receipt.py SCOPE header; python3-vs-python on the exact invocation being edited; receipts are git-TRACKED
             N3 FRESH-CLONE  - SCC-363 is a core.hooksPath hook; the SOP records hooks as inert on a fresh clone
             N4 SIBLING      - git worktree list + full diff of every live lane vs origin/main
             N5 BYPASS       - walked cicd-close-story-merge-tree Step 0.6 -> 1 -> 4, then the save door's flip rule; wf.TERMINAL vs the live board's 16 non-terminal keys
             N6 NO-REMEDY    - diffed the deleted string (:585) against the replacement (gate_receipt.py:349); REPRODUCED a false "no receipt" live
read:        as lenses 1-2, plus .agents/scripts/story_status.py · .agents/scripts/tests/run_all.py
             LIVE RUNS: closeout_preflight.py x4 against AGY_AVIATIONCHAT (23-9 short id, 23-9 full key, 23-1, board enumeration)
verdict:     findings below
```

### Findings — sorted by severity, then corroboration

| # | anchor | literal text read | consequence | severity |
|---|---|---|---|---|
| 1 `x2` | `.opencode/commands/cicd-close-story-merge-tree.md:86` | `       [--require-gates suite,ruff,pyrefly]` | The opencode mirror is a byte-identical full copy (both 31659 bytes, `diff -q` silent). `test_command_surfaces.py` CS-03 iterates `MIRRORS = (".opencode/commands", ".agents/workflows")` and `door_verdict` returns `ok` only `if body == brain`. Editing only the brain turns CS-03 RED, failing step 9's own `run_all.py`. Lens 1 and Lens 2 independently. | HIGH |
| 2 `x2` | `.agents/commands/cicd-update-sprint-memory.md:215` (with `:205-208`) | `**WAIVED / missing / stale** … → flip. Fail-open: a gate-read error never blocks close-out.` · `⏳ Remove \`--advisory\` at the close of the first full sprint after this landed (ruling 2026-08-02).` | The step that decides the flip carries the SAME expired ruling and an explicit fail-open. The new error prints at Step 0.6 and is overruled by prose at Step 4; the story flips to `done`, which permanently disarms the check for every downstream re-run. The AVCH-106 shape survives the fix. Lens 2 and Lens 3 independently. | HIGH |
| 3 | `.agents/scripts/tests/test_closeout_preflight.py:751, :764, :794, :828, :879` | `rc_def == 1 and not findings(out_def, "ERROR")` · `"STALE" in v_nf` · `"STALE" in v_bad and "FAILED" in v_bad` · `"STALE" in v_w` · `rc_clean == 1 and rc_mem == 2 and rc_both == 2` | The shared `lane_repo` fixture is exactly the blocked shape — board `30-1-fresh: review`, `**Verdict: PASS**`, no `_bmad-output/gates/30-1`. Under the change `main()` prints `BLOCKED` instead of a `STALE` verdict, so FR0, FR2, FR5, FR6 and MEM3 fail. The plan's change set was purely additive and named none of them. | HIGH |
| 4 `x2` | `.agents/scripts/tests/test_command_surfaces.py:2365-2366` | `bool(call) and "--require-gates" in call` | Acceptance F cannot go red: run against the UNMODIFIED door, `joined_invocation` returns `'… \\        [--require-gates suite,ruff,pyrefly]'`, so the substring assertion is already True. A faithful reuse is a vacuous pin — the exact `M20` shape the comment above `CS-14 C` warns about. Lens 2 and Lens 3 independently. | HIGH |
| 5 | `.agents/scripts/closeout_preflight.py:679-680` | `check_gates(project, args.story,` — every other check on `:649-681` is passed the resolved `key` | REPRODUCED live on AviationChat: `--story 23-9` → `[ERROR] gates: suite: STALE - passed at 808dce60`; `--story 23-9-flight-status-drawer-polish-active-curriculum` → `[WARN ] gates: suite: no receipt`. Same tree, same story. Today a harmless warning; this plan promotes it to a blocking false refusal, and `/cicd-prune-worktree` Step 0.2 resolves the long form. | HIGH |
| 6 | `.agents/commands/cicd-code-review.md:356` | `python3 .agents/scripts/gate_receipt.py run --story <id> --gate suite --cwd <worktree> \` | The review step stamps `suite` and nothing else; 9 of the 10 live AGY receipt dirs hold `suite.json` alone. Both doors passing `--require-gates suite,ruff,pyrefly` would hard-block every close-out on two receipts nothing writes. Raised by Lens 1 as a watch item, promoted after verification. | HIGH |
| 7 `x2` | `.agents/scripts/wf_common.py:34` | `TERMINAL = {"done", "descoped"}` · `ALL_STATUSES = … \| {"descoped", "deferred", "deferred-v3", "optional"}` | "Non-terminal" over-scopes: the live board carries 13 `deferred`/`deferred-v3` rows whose lanes are pruned, so the remedy is not one command away. Zero live blast (none carries a `Verdict:` line), so a scope correction rather than a live bug. Lens 2 and Lens 3 independently. | MEDIUM |
| 8 | `.agents/scripts/gate_receipt.py:349` vs `.agents/scripts/closeout_preflight.py:585` | new `rep.err("gates", f"{gate}: NO RECEIPT - the gate has no evidence it ran")` vs deleted `rep.warn("gates", f"{gate}: no receipt (gate_receipt.py run ...)")` | Step 2 as first written deleted the only string naming a remedy and replaced it with a blocking error that names no command and no directory — with finding 5 live, the reader cannot tell "missing" from "looked in the wrong place". | MEDIUM |
| 9 | `.agents/commands/cicd-close-story-merge-tree.md:84` vs `:156` | `:84` `python3 .agents/scripts/closeout_preflight.py …` (no annotation) · `:156` `… # PC: \`python\`` | On the PC the sole pre-flip enforcement point never runs — `command not found`, then the agent proceeds to Step 1 with no preflight evidence. The plan already edits line 86 of that same invocation. | MEDIUM |
| 10 | `_artifacts/_main/…/implementation_plan.md` (the folder name) | `2026-09-01_scc365-closeout-verdict-evidence` | The folder dropped the key's hyphen, so `task_preflight.py:1255` (`if lower in str(p.parent…)` with `lower = "scc-365"`) cannot resolve the lane by path — measured False, while sibling controls `2026-08-31_scc-360-zoo-fix` match. Free to fix before the lane is built. | MEDIUM |
| 11 | `_artifacts/_main/…/implementation_plan.md` §2 | `stories 23-1 through 23-8 carry \`Verdict:\` lines and no receipt at all` | FALSE as measured with the script's own `cp._VERDICT_RE`: only 23-1 and 23-2 carry a verdict with no receipt; 23-3..23-8 carry no `Verdict:` line at all. The design conclusion is unaffected (all 13 are terminal), but the motivating evidence was overstated 4x. | LOW |
| 12 | `step 3` (original numbering) | `**The error itself still comes from step 2's single path**, so a \`PASS\` with no receipt produces one error row, not two.` | `closeout_preflight.py:581` is `for gate in require:` with no dedupe, so a door naming `suite` explicitly would emit the identical row twice once `suite` is also prepended. | LOW |
| 13 | `Projects/sudo-command-center/.agents/scripts/closeout_preflight.py:427-431` | `# WARN, not ERROR: ruling 2026-08-02 keeps the receipt gate advisory for one` | A second copy of the script exists in another repo carrying the identical expired ruling, so `port-checklist.md`'s mechanical trigger fires and the plan answered none of its six checks. | LOW |
| 14 | `_artifacts/_main/…/implementation_plan.md` (Declared Change Set) | `- NEW \`…/task.yaml\` — the lane manifest → F` | The manifest is mapped to acceptance row F, which is about door parity. `declared_change_set.py` accepts it; cosmetic only. | LOW |

### Observations (uncounted)

- All 11 of the plan's line-number citations verified correct, including the two beyond the ticket
  (`closeout_preflight.py:10`, `workflows_testing_SOP.md:2443`). The "four callers" count is exact.
- Design claims re-measured TRUE: `wf.TERMINAL`, `lane_date` returning `None` for every live story
  lane, `gate_receipt.load_receipt` already erroring on absence, `verdict_receipt.py` gating exactly
  `PASS|CONCERNS`, and `check_artifacts` running before `check_gates` with `board[key]["status"]`
  already in scope. No new plumbing needed for the design.
- The twin claim holds verbatim: `task_preflight.check_gate` is
  `rep.info(… "the full gate runs (fail toward running, never toward trusting)")` on every receipt
  miss. Nothing owed there.
- `test_door_preflight_order.py` and `test_gate_receipt.py` have **zero** `closeout_preflight`
  references; `test_walkthrough_roster.py` calls `check_artifacts()` directly and never `main()`.
  Blast is confined to the two files already declared.
- `sop_currency.py` is armed and will demand the SOP for this diff; `_EXEMPT_PREFIXES` exempts the
  two test files. Plan step 8 names the right row.
- `risk_seam.py classify` → `{"status": "unclassified", "tiers": {}, "root": "<this worktree>"}` —
  correct for the command centre (SCC-289), and `root` resolved to the lane's tree, not `main`.
- Baselines before any edit: `test_closeout_preflight.py` **69/69**, `test_command_surfaces.py`
  **274/274**. Every red from here is attributable to this lane.
- `FR4` (`"STALE" not in v_def`) stays green but goes **vacuous** under a `BLOCKED` verdict — worth
  a sentence at re-base rather than a silent pass.

### Sibling landing order

`env -u GITHUB_TOKEN git fetch origin main`, then `git worktree list` → **three** live lanes:
`chore/SCC-358-memory-and-sync` (`_artifacts/_memory/` ×2, clean), `chore/SCC-366-claude-permission-fix`
(`.claude/settings.json`, 0 commits), and this one. **Zero intersection with this plan's declared
set. No landing-order dependency — any lane may land first.**

Audit verdict: NO-GO

**Why NO-GO, and what happens next.** Findings 1, 3, 4 and 6 each break an acceptance row or the
step-9 gate the plan depends on, which is the rule's first NO-GO ground. Findings 2 and 5 are
structural: one leaves the fix overruled by prose two steps later, the other ships a reachable false
refusal that this lane's own change creates. All fourteen have been absorbed into §§1–6 above as
`⚠️ AUDIT FINDING` blocks, the acceptance list has grown a row **G**, the Declared Change Set has
grown from 8 entries to 12, and the lane folder has been renamed to carry the key's hyphen. Round 2
re-audits the amended plan.

---

### Round 2 — amendment verification (2026-09-01)

One lens, targeted: does the amendment close the six blocking findings, and did it introduce
anything new? Not a re-run of round 1 — settled findings were not re-litigated.

```
lens:        R2 Amendment Verification
checks_run:  A1 diff -q close door brain vs .opencode mirror (31659 B each, silent); grep -c --require-gates across .agents/workflows, .roo/commands, .claude/skills (0 each); repo-wide grep -rl
             A2 diff -q cicd-update-sprint-memory brain vs mirror (22872 B each, silent); read :198-222 raw to confirm :205-208 and :215 carry the exact strings step 5 deletes
             A3 read lane_repo in full; extracted EVERY c.check in test_closeout_preflight.py whose assertion references rc; audited ov_repo, build(), the 16 OV cases, FX, EK0-EK4, SAMETREE, VR, SCC-211; grepped all 6 test files referencing closeout_preflight for main()/check_gates callers
             A4 re-implemented joined_invocation and ran it against BOTH unmodified doors; scored the old assertion, each new half, and the conjunction; mutant probe on an unbracketed-but-not-narrowed door
             A5 read wf_common.py:170-181; hand-evaluated slug_matches for the three collision cases; ran the proposed literal-then-slug resolver over the 11 live AGY receipt dirs with 12 probes; wrong-pick probe on a synthetic epic-level dir
             A6 grepped every `gate_receipt.py run` and every `--gate` in .agents/commands/; listed all 11 live AGY receipt dirs and their files
             B1 hand-evaluated the STATUS_RANK expression over all 9 ALL_STATUSES + an out-of-vocabulary string + empty
             B2 grepped --advisory / Fail-open / suite,ruff,pyrefly / ruff,pyrefly across .agents/scripts/tests/ and repo-wide
             B3 ran workflow_lint.py --toolkit-only
             B4 grepped workflows_testing_SOP.md for suite,ruff,pyrefly and advisory; read the :2443 row and the :1226 hit
read:        implementation_plan.md (full, incl. the round-1 Self-Audit)
             .agents/commands/{cicd-close-story-merge-tree,cicd-merge-epic-workingtrees,cicd-update-sprint-memory,cicd-code-review,cicd-dev-story-tests}.md
             .opencode/commands/{cicd-close-story-merge-tree,cicd-merge-epic-workingtrees,cicd-update-sprint-memory}.md
             .agents/scripts/wf_common.py:29-35,160-195 · .agents/scripts/tests/test_closeout_preflight.py (all 986 lines swept for rc)
             .agents/scripts/tests/test_command_surfaces.py:588-712,2210-2260,2316-2380
             docs/_scc_sops_prds/workflows_testing_SOP.md:1220-1230,2438-2452 · Projects/AGY_AVIATIONCHAT/_bmad-output/gates/** (11 dirs, per-file)
verdict:     findings below
```

**Closure — five of six clean, one closed with a gap:**

| # | finding | status | evidence |
|---|---|---|---|
| 1 | opencode mirror of the close door | **CLOSED** | declared at plan `:243`; `diff -q` silent, both 31659 B; the other three surfaces carry the flag 0 times |
| 2 | the flip door's fail-open | **CLOSED** | brain **and** mirror declared; `diff -q` silent, both 22872 B; `:206-207` `--advisory`, `:208` the ⏳ line, `:215` the fail-open — exactly where the plan says |
| 3 | the five re-based cases | **CLOSED** | named with line numbers at plan `:173-176`; the sweep found **no sixth case** — `ov_repo` shares the blocked shape but every OV assertion filters to the `overview` section, `FX` drives `check_artifacts` in-process and never reaches `check_gates`, EK0/EK1/EK4 already expect `rc == 2`, and SCC-211's verdict assertion is negative so it survives `BLOCKED` |
| 4 | vacuous CS-14 C2 | **CLOSED, gap → NEW-2** | measured on the unmodified door: old assertion **True today** (the vacuity, confirmed), new conjunction **False today** — the bracket half has teeth |
| 5 | `check_gates` taking raw `args.story` | **CLOSED** | `slug_matches` hand-evaluated: long key vs `23-9` → True (the reproduced bug closes); `21-8` vs `21-8b` → False; `21-8b` vs `21-8` → False. Symmetric, so no ordering trap. Over the 11 live dirs the long key resolves to `23-9`, and `23-1` falls back to the literal so the error names the right directory |
| 6 | the flag demanding receipts nothing writes | **CLOSED** | every `gate_receipt.py run` in `.agents/commands/` stamps `--gate suite` and nothing else (`cicd-code-review.md:356`, `cicd-dev-story-tests.md:272`, `smh-quick-dev.md:340`, `smh-code-review.md:326`); **nothing in the system stamps `ruff` or `pyrefly`** |

**The flip-eligible expression is correct for every value in the vocabulary** —
`0 < wf.STATUS_RANK.get(s, -1) < wf.STATUS_RANK["done"]` is True for exactly
`ready-for-dev` (1), `in-progress` (2), `review` (3); False for `backlog` (0), `done` (4), and for
`descoped` / `deferred` / `deferred-v3` / `optional` / out-of-vocabulary / empty (all rank -1).

**Nothing else moved:** no test in `.agents/scripts/tests/` pins any removed string (zero hits for
`Fail-open` and `suite,ruff,pyrefly`; the three `--advisory` hits are `test_gate_receipt.py:102,103,169`,
exercising that script's own surviving flag). `workflow_lint.py --toolkit-only` → **exit 0, 0 errors,
0 warnings, 8 info**, so a later red is attributable. The SOP carries zero `suite,ruff,pyrefly`, and
`:2443` genuinely omits the receipt check, so step 8's edit is additive.

### New findings — all three absorbed above

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.opencode/commands/cicd-merge-epic-workingtrees.md:73` | `         --require-gates suite,ruff,pyrefly` | Finding 1's exact shape on the door the amendment itself added. Byte-identical to its brain (27721 B, `diff -q` silent) but undeclared, and step 7 still said "both edited doors" when the amendment made it three. CS-03 would go red. **Absorbed:** declared in the change set, step 7 rewritten to three doors. | HIGH |
| plan acceptance row **F** | `asserting "[--require-gates" not in call **and** "--require-gates suite" in call` | Row F pinned the unbracketing but not the narrowing: `"--require-gates suite"` is a **substring** of `"--require-gates suite,ruff,pyrefly"`, so the conjunction stays True for a door left demanding all three — and against the *merge* door it is already True today, so nothing would go red there at all. **Absorbed:** F now asserts `"ruff" not in call and "pyrefly" not in call`, over **both** doors' resolved calls. | HIGH |
| `_artifacts/_memory/workflow-enforcement-scripts.md:38` | `⏳ Flip owed: drop \`--advisory\` from the close-out receipt gate after the first full sprint.` | Step 5 performs that flip, leaving the memory store telling every future session an obligation is still owed that this lane discharged. No gate reds on it. **Absorbed:** new step 9 strikes the line through the Claude harness memory flow — a sanctioned writer per `AGENTS.md` §7 — carried onto this lane by that section's four-step procedure. | LOW |

Audit verdict: GO

**Why GO after a NO-GO, stated so it can be overruled.** Round 1 was a genuine NO-GO: it changed the
design — the status set, a fourth gap, the door narrowing, a new acceptance row. Round 2's three
findings changed **no design at all**: one `EDIT` line in the change set, one clause in an assertion,
and one stale memory line, each verified against the tree by the lens that raised it and each already
absorbed above. A third round would be auditing a two-line edit, which is the accretion the amendment
rule at the top of `/smh-self-audit` exists to forbid. The plan as it now stands carries no anchored
finding whose consequence breaks an acceptance row or a hard gate.
