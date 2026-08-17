# Walkthrough — SCC-164 second half · the gate cluster

review-runtime: inline

**What changed, in one line:** the five parts SCC-164 declared but did not build — the PC token path,
the three main-gate fail-opens, the post-merge tick, the `reset --hard` remedy, and the unenforced
blind review — are built, and SCC-164 closes.

---

## Step 0 — the probe, recorded before any code (Rule 3)

`review-runtime: inline`. This session carries a standing directive that the subagent tool is not to
be used, so fan-out is **unavailable**, not merely unchosen. Under Part I's contract that makes
`recovered-inline` the only legal per-lens state for this lane. The lane is therefore the first live
fixture of the parser it builds.

## Step 0.7 — re-derivation against SCC-183

Recorded in full in [`implementation_plan.md`](implementation_plan.md) § *What SCC-183 changed, part
by part*. Three lines, as Part E7 requires:

1. **What moved:** SCC-183 (PR #11 `819f981`, PR #12 `bc3a851`) deleted the lobby's local
   merge-to-main road and replaced it with a pull request the operator clicks.
2. **What that changes for this lane:** nothing dissolved. C and D lose their lobby *stakes* (no
   lobby command merges locally any more) but keep their live blast radius — `/cicd-push-e2e` in
   project repos, and the PC. G gains a second defect: the door now contradicts itself.
3. **What was re-measured:** the door's Step 4 tick instruction (`:493-498`), the `/cicd-push-e2e`
   carve-out in `test_door_preflight_order.py:284-290`, the lobby-vs-AGY diff on all four gate
   files, and — second pass, 2026-08-16 — **three stale line anchors** in the approved plan
   (L's SOP pass-fixture `:862` → `:934`, L's `git-policy.md` recovery paragraph → `:324`, G's
   deleted-instruction target `:434-438` → `:493-498`), plus the merge-row corpus split that
   inverts F27's premise (7 mandated rows vs 5 legacy, across 92 walkthroughs). Both recorded in
   the plan's § Stale anchors and § Part 9 corrections. **L is not overlap-free** — the first pass
   recorded it as untouched; the banner is, its two fixtures are not.

---

## Build log

| # | Part | Key | Commit | What shipped |
|---|---|---|---|---|
| 1 | **C** | SCC-171 | `91909b5` `b39bcff` | the token path as git gives it, on both scripts; a mint that verifies the write actually happened |
| 2 | **G** | SCC-175 | `f6d7928` `e50bcc9` | the merge row is **computed** from ancestry, not trusted from a tick; the door's contradictory Step 4 instruction deleted |
| 3 | **L** | SCC-180 | `5f25937` `124ce8e` | the backstop stops printing `git reset --hard`; `--keep`/`--soft` with the reason, and the detector got its own floor |
| 4 | **D1+D2** | SCC-172 | `f538e2e` | non-merge push refused · unresolvable token branch refused · the ZERO-remote arm refused, each on its own reason |
| 5 | **E+I** | SCC-173 SCC-177 | `f239bb0` `c54f1b4` `205d40a` `e1bcbbc` | the roster parser, both preflights wired, the engine's return block reshaped, both review commands writing it verbatim, the runtime probed at Step 0 |
| 6 | **ARMING 3** | SCC-163 | `3ac4b3c` | `--strict-actions` armed on a measured zero false-positive count |
| 7 | **D3** | SCC-172 | `c4d2abf` | ⛔ last edit of the lane (F22): a stale worktree may push its lane, never `main` |

### Mutation sweeps — every declared mutant killed by its declared case

| Part | Table | Result |
|---|---|---|
| C | `sweep-partC.json` | 4/4 |
| G | `sweep-partG.json` | 4/4 |
| E+I | `sweep-partEI.json` | **11/11** |
| L | `sweep-partL.json` | 3/3 |
| D | `sweep-partD.json` | **6/6** (D-6 is D3, swept last against the live hook, byte-restore verified) |

**28 mutants, 0 survivors.** Two of them exist *because* the sweep found the guard was vacuous:
`RH1b` (RH1 reports the same empty list whether the tree is clean or the detector is blind) and the
`W-B` import fix (a block that cannot run alone cannot kill a mutant alone).

### The D3 drill, in a scratch repo with a real bare remote

Run before the suite case existed, because `.githooks/pre-push` goes live for this worktree the
moment it is saved (F22):

| Tree state | Push | Result |
|---|---|---|
| gate scripts **missing** | `main` | ⛔ REFUSED — remote never received `main` |
| gate scripts **missing** | `chore/SCC-999-x` | ✅ ALLOWED — branch arrived |
| gate scripts present, **armed** | `main`, no token | ⛔ REFUSED by the real gate (`no approval token`) |

---

## Evidence

| Claim | The assertion that proves it |
|---|---|
| A `Verdict:` with no roster blocks | `test_walkthrough_roster.py` E1 · mutant EI-1 |
| PASS + a dead lens is a contradiction; CONCERNS + dead is not | E2 / E2b / E2c · mutant EI-2 |
| The dated cutoff scopes, it does not warn | E4a–d · mutant EI-4 |
| Step 0.7's three lines are counted | E7 / E7b / E7c · mutant EI-5 |
| `inline` + a lens `ok` is a disagreement | I3a–d · mutant EI-6 |
| Both header spellings are read | I3e / I3f · mutant EI-7 |
| The gate **blocks**, not just parses | W-B1 (real `check_artifacts`, severity read) · mutant EI-8 |
| A re-reviewed FAIL→PASS lane is not blocked by its cleared FAIL | W-B4 (real `check_gate`) · mutant EI-9 |
| A fenced roster is an example, not a roster | P-F1–4 · mutant EI-10 |
| The **last** roster governs | P-R1–3 · mutant EI-11 |
| The engine's published shape is the shape the gate reads | `test_review_engine.py` § 5 round-trip |
| A stale worktree may push its lane, never `main` | `test_main_push_gate.py` D3–D3e · mutant D-6 |
| `--strict-actions` refuses by default, and the opt-out is logged | `test_jira_feed.py` B7 / B8–B8d |

**Full enforcement suite: 33/33 files passed**, measured at `e1bcbbc`.

### The ARMING clause 3 measurement, in full

The operator's ruling armed `--strict-actions` *"when the count is clean"*. Measured 2026-08-16
across all **145** tracked walkthroughs with `jira_feed.banned_action_rows`:

| Corpus | Walkthroughs | Hits | Verdict |
|---|---|---|---|
| post-cutoff (folder date ≥ 2026-08-15) | 11 | **0** | **0 false positives → the condition is met** |
| legacy (everything earlier) | 134 | 3 | all 3 TRUE positives — the detector is not vacuous |

The three legacy hits are `2026-08-12_scc-123-evidence-extract`, `2026-08-13_scc-128-rewire-callers`
and `2026-08-14_gate-receipts`; each really does hand ticket work to the operator. Flag flipped.

---

## Code Review

review-runtime: inline

lenses_run:
- blind-hunter · recovered-inline — fan-out unavailable; ran first on the diff alone, before the plan
- edge-case-hunter · recovered-inline — fan-out unavailable
- acceptance-auditor · recovered-inline — fan-out unavailable; audited against the approved plan's Parts 8–12 + § ARMING
- test-adequacy-auditor · recovered-inline — fan-out unavailable
- literal · recovered-inline — fan-out unavailable
lenses_counted: 5/5
lenses_na: none

**Method.** `review-runtime: inline` was declared at Step 0 *before* any code, so this is the
declared runtime rather than a description of what happened to occur. Under Part I's own contract
the ladder ran once, blind lens first on the diff alone, and `recovered-inline` is the only legal
per-lens state — which is why every row reads that way and none reads `ok`. **This lane is the first
live fixture of the parser it built**, and the gate it must pass is the one it wrote.

### Findings

| # | Where | Severity | Failure scenario | Disposition |
|---|---|---|---|---|
| 1 | `walkthrough_roster.py` `parse()` | **HIGH** | A roster existing only inside a ``` example satisfied `closeout_preflight` (raw text) while `task_preflight` (strips fences) refused the identical file. The Step 4 instructions this lane wrote *teach* the roster fenced, so copying the example closed a lane that ran nothing | **applied** @ `e1bcbbc` — fence walker moved into the parser; P-F1–4 |
| 2 | `walkthrough_roster.py` `parse()` | **HIGH** | The parser read the FIRST `lenses_run:` block. A re-review appends, so a lane that did exactly what a dead-lens refusal asked was judged on the roster its re-review replaced — the remedy could never clear it | **applied** @ `e1bcbbc` — last roster governs; P-R1–3, with P-R3 proving "last" is not "most favourable" |
| 3 | `task_preflight.py:1173` | **HIGH** | `roster.judge(…, found[0][0])` where the rest of `check_gate` reads `found[-1]`. A re-reviewed FAIL→PASS lane was blocked by the FAIL its own remedy had cleared — the `any(FAIL)`-over-all-hits defect the docstring records as fixed | **applied** @ `c54f1b4` — `found[-1][0]`; W-B4 against the real `check_gate` |
| 4 | `test_walkthrough_roster.py` W block | MEDIUM | `task_preflight` was imported inside block W, so `--case W-B` skipped the import and crashed *after* the first case failed. The sweep read it as "exit 1 with no `FAILED:` line" and refused to score two mutants | **applied** @ `205d40a` — every block verified runnable standalone |
| 5 | `test_git_hooks.py` RH block | MEDIUM | RH1 asserts "no imperatives found" — which is also what a **blind** detector reports. Breaking one line of `payload()` left RH1–RH4 green while the guard could no longer fail | **applied** @ `124ce8e` — RH1b/RH1c, the detector's own floor |
| 6 | `test_git_hooks.py` `make_pushable` | MEDIUM | The fixture installed the backstop but not the approval script, modelling a stale worktree by accident. D3 correctly refused its `main` pushes and three ALLOW controls read that refusal as the backstop's | **applied** @ `c4d2abf` — script installed and left disarmed |
| 7 | `walkthrough_roster.py` `_RUNTIME_RE` | LOW | The contract names the input `review_runtime`; the header is `review-runtime`. A header carrying the underscore was invisible — `runtime` came back `None`, I3 never fired, and the gate reported clean | **applied** @ `c54f1b4` — both spellings read; I3e/I3f |

**Findings 1, 2 and 3 are one class found three times**: *which occurrence governs when a document
can be appended to, and what is documentation rather than data.* Two of the three were introduced by
this lane. The third was pre-existing at the call site this lane added. None was filed as a ticket —
all seven were fixed in thread, per the operator's ruling of 2026-08-15.

### Gates

| Gate | Result |
|---|---|
| `run_all.py` (enforcement suite) | **33/33 files passed** @ `e1bcbbc` |
| Mutation sweeps, 5 tables | **28/28 killed by declared case**, 0 survivors |
| `workflow_lint --toolkit-only` | clean; AP twin diffed, reconciled and restamped to `c54f1b4` |
| Door parity (`.agents` ↔ `.opencode`) | `test_command_surfaces.py` 92/92 |
| SOP currency | armed gate satisfied on every usage-surface commit; `[sop-ok]` used only on test-only commits |
| Skills cache parity | `.claude/skills/code-review-engine` byte-identical to master |

Verdict: PASS @ e1bcbbc

Suite evidence measured on `e1bcbbc` — the same sha. No code or test file changed after it; the
only later commit is this walkthrough, which `nonartifact_moved` exempts by design.

---

## Your Actions

⭐ **This section exists now, before any build, on purpose.** SCC-183's Step 3 refuses to open the
PR without it *and* without the merge row below, and `jira_feed.py finish` refuses to close without
it — an absent section is not evidence that nothing is owed. Both are cheap here and expensive five
minutes before a landing: this exact omission held SCC-183 itself at `Review Required`, at this very
step.

- [x] **The merge itself** — lands via this branch's PR. Number-free by design: the PR number is
  assigned when the PR opens, which is *after* this commit is pushed. The number and merge sha go on
  the ticket at Step 4, on the `--after-merge SCC-164` re-invocation.

  ⭐ **Ticked here, and `finish` does not take the tick's word for it (SCC-175, this lane).** The row
  is now **computed** from ancestry — `jira_feed.py finish` resolves the manifest's branch, checks
  whether its tip is an ancestor of the merge, and re-opens the row with a `[WARN]` if a `- [x]`
  claims a merge that did not happen. So this box is a claim the door verifies, not a promise it
  trusts.

**Nothing else is owed.** Every finding this lane's review produced was fixed in thread (seven of
them, § Code Review). No residue ticket, no deferred row, no decision held open.

### ⛔ Two rows were removed from this section, and the removal is recorded rather than silent

The first draft of this section carried two more `- [ ]` rows: *"Click **Merge** on the PR"* and
*"Then re-invoke `/smh-close-task-merge-tree --after-merge SCC-164`"*. **Neither was an operator
task, and writing them here was an authoring error.**

`## Your Actions` is a machine contract (SCC-155): an unchecked box means *something only the
operator can do that is still outstanding*. Those two rows were **the ceremony's own steps** —
the second one describing the very command that would later read the section. So `finish` did
exactly what it is built to do and HELD the ticket at `Review Required` on two items that were
already satisfied: the click had happened (`6ec9dc0`), and the re-invocation was running at the
moment it read them.

⭐ **The merge row above already carried both facts**, which is the point — it is `- [x]` and
SCC-175 *computes* whether that tick is true from ancestry. The extra rows added no evidence and
one impossible-to-satisfy dependency.

⛔ **Why an agent removed them, when the door says open boxes are the operator's.** That rule
(`smh-close-task-merge-tree.md` Step 4) stops an agent ticking the operator's **genuine** tasks to
force a close. It is not cover for an agent leaving its own bad data in the file for the operator to
clear. These rows were authored by the agent, describe agent steps, and were wrong on the day they
were written — correcting them is fixing a mistake, not closing a task. The removal rides its own
lane and its own PR (`chore/SCC-164-closeout-rows`), so the operator's click still gates it and the
edit is reviewable rather than slipped in after the merge.

**The general defect this is an instance of** is filed as SCC-192 under the rolling ticket SCC-190:
a close-out that is hand-run rather than invoked leaves no trace, and this section is where that
absence surfaced.

---

## Follow-on, and it is not a finding

⭐ **Nothing in this system tells an agent to check whether a lane is already taken, and that is the
gap this lane was cut through.** Six subtasks were moved to `In Progress` and a branch was cut while
another session held the documentation work on the same ticket. Git carried no signal — no branch, no
worktree, no PR, no assignee. `ListAgents` was the only thing that would have shown four live
sessions, and no rule requires running it.

This is recorded here rather than fixed here: it is a change to lane-cutting law across every
`/smh-*` and `/cicd-*` entry point, which is its own ticket and its own review — not a rider on a
gate-cluster landing. **It is the operator's call whether it gets filed**, which is exactly the class
of thing `## Your Actions` is for, and deliberately *not* the class `banned_action_rows` refuses:
this is a product decision about workflow law, not a review finding being handed over as ticket work.
