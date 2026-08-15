---
IsArtifact: true
ArtifactMetadata:
  title: SCC-162 — the lightweight lane
  type: implementation_plan
  date: 2026-08-15
---

# SCC-162 — Define the lightweight lane

**Ticket:** SCC-162 (Task, `In Progress`) · **Lane:** `chore/SCC-162-lightweight-lane` · **Base:** `main` @ `0b163d1`

## 1. Goal, in one sentence

When the operator asks for one specific thing that cannot break anything, an agent should do it —
ticket, edit, push — instead of opening the full Task ceremony. Today nothing in the loaded law says
that, so the agent either runs the whole pipeline or improvises. This ticket writes the lane down,
gives it a door, and makes the "does this qualify?" question a fact rather than a judgement.

**Where it came from.** SCC-161 was a doc-only edit that got a plan-first STOP, a worktree, a
self-audit and a RED assertion before the operator said *"we are editing a doc thats all"* and
*"we need to have a path outside the workflow too, not everything is a full quick dev… this does not
touch anything that can break. so we don't need to over engineer it."* That ruling is currently held
only in a memory file. A memory is recall, not law — it is not loaded on every platform, it is not
gated, and it cannot be pointed at from the lane chooser. This ticket promotes it.

**Self-consistency check, and it is the interesting one:** *this ticket does not qualify for its own
lane.* It changes rules, a command and (under D3) a script — three surfaces the qualification test
excludes by name. So SCC-162 correctly runs the full Task lane, which is why you are reading a plan.
If the test said otherwise, the test would be wrong.

## 2. The four decisions

Each is a design fork. I have made a call on all four and stated the reasoning; **D2's name and D3's
scope are the two I would most expect you to overrule**, and they are repeated as open questions in §7.

### D1 — Where the lane is written: `artifacts-always-first.md` § "When to Skip". Not a new rule.

The plan-first gate's exemptions are a **closed list**, and both rules that own it say — in their own
words — that a second copy is the failure mode:

- [`000-PLAN-FIRST-GATE.md:133`](.agents/rules/000-PLAN-FIRST-GATE.md) — *"The exemption list lives in
  ONE place… It is not duplicated here on purpose — two copies of a gate's exemptions drift apart, and
  each one reads authoritative."*
- [`000-PLAN-FIRST-GATE.md:10-13`](.agents/rules/000-PLAN-FIRST-GATE.md) — naming `/cicd-quick-dev`
  inline *"is what put this rule and that command in direct contradiction."*

A new `.agents/rules/lightweight-lane.md` would be exactly that second copy, and it would add weight
to a protocol tier already at ~44 KB. The lane becomes a full entry in the existing list, shaped like
`/cicd-quick-dev`'s — which already carries its own conditions and its own record shape, so the
precedent for "an entry that is more than one line" is set.

### D2 — The door: a command. Recommended name `/smh-just-do-it`.

**Why a command and not only a phrase.** Every entry on the closed list works the same way: *invoking
the command IS the instruction*. That shape is deliberate — it means the operator authored the
exemption, not the agent. A phrase-only lane would leave an agent deciding whether your prose
qualified, which is the self-authorizing exemption
[`000-PLAN-FIRST-GATE.md:92-97`](.agents/rules/000-PLAN-FIRST-GATE.md) forbids by name.

**Why the phrase stays anyway.** The skip list already has entry 3 — *"Daniel explicitly says 'skip
the plan, just do it'"* — and its defect is not that it exists, it is that it dead-ends: it tells the
agent to skip the plan and then says nothing about what to do instead. That is precisely the hole
SCC-161 fell into. So **both doors, one definition**: entry 3 is rewritten to point at the lane, so
saying it gets you identical behaviour to typing it. You never have to remember a command; the
command exists so the lane is discoverable, diagrammable and testable.

`/smh-just-do-it` matches the words already in the rule and the words you actually say. Alternates:
`/smh-light`, `/smh-do`. Naming law (SCC-63): `smh-*` family — the one allowed to act on the repo you
are standing in — hyphens only, no `sudo-`.

### D3 — The qualification test: a script, `lane_qualify.py`.

The acceptance line says *"a qualification test an agent can apply **mechanically**."* Written as
prose, the test needs path lists that already exist in two scripts, and a third prose copy of a list
is the documented drift failure — [`sop_currency.py`](.agents/scripts/sop_currency.py) exists because
a doc and a script disagreed about one command line for months, and
[`prose-pinning-guards-are-vacuous`] is the memory of guards that pinned a description instead of the
wiring and scored 323/323 on a file that meant the opposite.

> ⚠️ **AUDIT FINDING (F3, medium) — the first draft of this section was both over-costed and
> subtly wrong; this is the corrected design.** Two facts found by reading the scripts rather than
> assuming: `task_preflight.DEPLOY_DIRS` is a **public constant**, and
> `sop_currency.classify(path)` is a **public function** that already returns *"why this path is a
> usage surface, or None"*. So the classifier is ~40 lines, not ~120 — which removes the reason to
> cut it. But `classify()` **exempts `.agents/scripts/tests/`** (correctly, for its own question:
> editing a test does not change what the operator types). Reusing it as the safety test would
> therefore rate an edit to the **enforcement suite** as LIGHT. *"Does this need a SOP update?"* and
> *"can this break something?"* are not the same question, and conflating them is how the lane would
> have been handed the test suite.

The rule is therefore blunt on purpose — **anything under `.agents/` is never LIGHT** — because a
single line has no exemption subtleties to get wrong:

| Verdict | When |
|---|---|
| `HANDOFF` | any path in `task_preflight.DEPLOY_DIRS` (imported, repo-aware) → `/cicd-push-e2e`'s road, never a Task |
| `TASK` | any path under `.agents/`, `.githooks/`, `_bmad*`, or root `AGENTS.md` — **or an empty path set** |
| `LIGHT` | everything else — `docs/`, `_my_resources/`, `README`, `_artifacts/` |

```
python3 .agents/scripts/lane_qualify.py --paths <paths>   →  LIGHT | TASK | HANDOFF
```

> ⚠️ **AUDIT FINDING (F2, high) — empty input must not read as LIGHT.** *"A check whose empty input
> reads as a pass"* is a named Phase-2 tripwire, and here it is the whole ballgame: an agent that
> declares no paths would be handed the lane. Empty → `TASK`, and the test asserts it.

`sop_currency.classify()` is still used — as a **drift cross-check in the test**: every path it flags
as a usage surface must also come back non-`LIGHT`. That way a future widening of its list cannot
silently widen this lane, without this script depending on its exemptions.

It reads and prints; it never edits, never branches, never merges. Cost: ~40 lines plus
`test_lane_qualify.py` (auto-discovered by `run_all.py:43`, so no wiring).

### D4 — Close-out: `/smh-close-task-merge-tree`, unchanged. No third door to `main`.

**This is already true mechanically — I checked the code rather than reasoning about it**, and it is
the one decision on the ticket that needs no new work:

- No review verdict is **not** a blocker. [`task_preflight.py:1076`](.agents/scripts/task_preflight.py)
  — *"no review Verdict line in this task's own walkthrough — the full gate runs."* It returns `None`,
  which means the close-out declines the review's shortcut and runs the whole gate itself. That is the
  safe direction, and it is exactly what you want from a lane that skipped the review.
- The preflight **already anticipates a plan-less Task lane**.
  [`task_preflight.py:894-896`](.agents/scripts/task_preflight.py) —
  *"`artifacts-always-first` exempts the plan on this lane; it never exempts the walkthrough."*
- A walkthrough **is** required, with `## Your Actions`, or the close-out errors
  ([`task_preflight.py:917`](.agents/scripts/task_preflight.py) and `:929`).

A lighter merge door would be a **third** route to `main` beside `/cicd-push-e2e` and this one. That
is new law that can touch production, so it would need its own quoted ruling
([`blocking-gates-need-a-quoted-ruling`]), and it would weaken the gate that
[`main-merge-needs-operator-verbatim-approval`] hardened on SCC-37. **The lane drops the ceremony
before the merge, never the merge gate.** Nothing in `task_preflight.py` changes in this diff — and
that "no diff" is itself an assertion below.

## 3. The lane, as it will read

**Qualifies only if ALL FOUR hold** (any one fails → the full `/smh-quick-dev` lane):

1. `lane_qualify.py` returns `LIGHT` — no deployable path, no enforcement or usage surface.
2. **You named the work this turn.** A specific, bounded ask. Scope the agent inferred, widened, or
   carried over from a previous turn does not qualify.
3. It is **not** a new gate, a rule change, or anything that can refuse a commit or block a merge.
4. It is **not** a story, and it has no deployable path — i.e. it is Task-shaped to begin with.

**What it KEEPS** — every item is mechanically enforced today, which is why none of them are droppable:

| Kept | Enforced by |
|---|---|
| a Jira key + `chore/<KEY>-<slug>` branch off `main`, in its own worktree | the armed commit hook refuses a keyless commit |
| explicit-path commits, pushed before hand-back | `git-policy.md`; [`commit-and-push-are-one-action`] |
| the SOP-currency gate where it applies (`[sop-ok]` = the logged opt-out) | `sop_currency.py`, armed |
| a lean `walkthrough.md` carrying `## Your Actions` | `task_preflight.py:929` errors without it |
| `task.yaml` beside it | `task_preflight.py:283` warns without it |
| close-out via `/smh-close-task-merge-tree`, on your verbatim merge words | SCC-37 minter |

**What it DROPS:** `implementation_plan.md` and the approval STOP · `/smh-self-audit` · the RED-first
assertion and its mutation step · `/smh-code-review` and its verdict · `/smh-plan-task` ·
`/smh-label-tasks`. And one behaviour, stated as a prohibition because it is the one that actually
annoyed you: **do not ask "shall I mint a ticket / open a lane / write a plan?"** — asking is the
over-engineering. Mint, cut, do, push, hand back.

### The EJECT — the lane's only tripwire

> ⚠️ **AUDIT FINDING (F1, high) — the first draft had no eject, and every other exemption in this
> system has one.** The qualification test runs against the paths an agent *intends* to touch,
> before any file exists. An agent that under-declares its scope gets `LIGHT` and nothing ever
> re-checks. `/cicd-quick-dev` ejects on risk, the Task lane ejects on a deployable path — and
> `artifacts-always-first.md:278` already states the consequence in general terms: *"A fired
> tripwire re-arms this gate."*

**Before the walkthrough is written, re-run the check against the REAL diff:**

```bash
python3 .agents/scripts/lane_qualify.py --paths $(git diff --name-only main...HEAD)
```

Anything other than `LIGHT` and the lane **ejects**: stop, the plan-first gate re-arms, and the work
continues on the full `/smh-quick-dev` lane with a plan and your `approved`. Nothing already
committed is thrown away — the branch is the same branch; only the ceremony owed changes. This is
what makes condition 1 a fact rather than a promise: **an under-declared scope is caught by the
diff, not by the agent's honesty.**

## 4. Files touched, in execution order

Each step names the assertion that proves it.

| # | File | Change | Assertion |
|---|---|---|---|
| 1 | [`.agents/scripts/lane_qualify.py`](.agents/scripts/lane_qualify.py) *(new, D3)* | classify paths → `LIGHT`/`TASK`/`HANDOFF`, importing `task_preflight.DEPLOY_DIRS` | see row 2 |
| 2 | [`.agents/scripts/tests/test_lane_qualify.py`](.agents/scripts/tests/test_lane_qualify.py) *(new)* | six assertions | `backend/x.ts` → `HANDOFF` · `.agents/scripts/x.py` and `.agents/rules/y.md` → `TASK` · `.agents/scripts/tests/z.py` → `TASK` (**the F3 regression** — `sop_currency` exempts it, this must not) · **empty input → `TASK`** (the F2 regression) · `docs/z.md` → `LIGHT` · **drift cross-check**: every path `sop_currency.classify()` flags comes back non-`LIGHT`. Joins `run_all` by auto-discovery (`run_all.py:43`) |
| 3 | [`.agents/rules/artifacts-always-first.md`](.agents/rules/artifacts-always-first.md) | new "When to Skip" entry = the lane; entry 3 (the phrase) rewritten to point at it | grep: the four qualification conditions appear in exactly ONE rule file; `000-PLAN-FIRST-GATE.md` still holds no copy of the list |
| 4 | [`.agents/commands/smh-just-do-it.md`](.agents/commands/smh-just-do-it.md) *(new)* | the door: qualification check → ticket → branch → do → gates → push → lean walkthrough → hand back | `workflow_lint.py --toolkit-only` clean (frontmatter, no `platforms: []`, INDEX row) |
| 5 | [`.agents/commands/INDEX.md`](.agents/commands/INDEX.md) | one row | same lint |
| 6 | [`docs/_scc_sops_prds/workflows_testing_SOP.md`](docs/_scc_sops_prds/workflows_testing_SOP.md) | §5 chooser diagram + the lanes table (three → four) · a new §9 subsection · §4 lifecycle map · §17 call graph + "where each command stops for you" · §18 one diagram · §19 reference row · Contents | `test_sops_prds_folder.py` T3 (links) + T4 (command refs resolve to a real master) — 61/61; and the SOP is in this same commit, so `sop_currency.py` passes without `[sop-ok]` |
| 7 | [`AGENTS.md`](AGENTS.md) | the ⛔ ARTIFACTS block's parenthetical exemption pointer gains the lane | `workflow_lint`; link check |
| 8 | `/smh-sync-agents` | generate the launcher skill + opencode/Antigravity mirrors | `test_command_surfaces.py` — one door per platform, both directions |

**Not touched, deliberately:** `task_preflight.py`, `.githooks/`, `main_write_gate.py`, and every
close-out command. Asserted by `git diff --name-only main` at the end.

## 5. Verification plan

```bash
python3 .agents/scripts/tests/run_all.py                                   # 28 files + test_lane_qualify
python3 .agents/scripts/workflow_lint.py --toolkit-only
python3 .agents/scripts/tests/test_sops_prds_folder.py                     # 61/61
python3 .agents/scripts/check_maps.py --depth3-only --strict
python3 .agents/scripts/tests/test_command_surfaces.py                     # after the sync
git diff --name-only main -- .agents/scripts/task_preflight.py .githooks/  # must print NOTHING
```

Run bare, never piped — a piped gate reports `tail`'s exit code
([`piping-a-gate-hides-its-exit-code`]).

## 6. Risks

1. **The lane becomes the default and swallows real work.** Mitigated by condition 2 (you named it)
   plus the machine test — an agent cannot talk itself into `LIGHT` when a path says otherwise.
2. **The SOP edit is the big one.** Section 5 is the chooser every lane decision starts from, and
   SCC-161 has just rebuilt this document. Six sections change; the anchor test is what proves the
   Contents and cross-references still resolve.
3. **`lane_qualify.py` importing from two scripts couples three files.** That is the point — the
   alternative is a third copy that drifts — but it means a future edit to either list changes this
   verdict. The drift test in step 1 is there to make that loud rather than silent.

## 7. Open questions — I need your call on these

1. **The command name.** `/smh-just-do-it` (recommended — it is the phrase already in the rule and
   the one you actually use), `/smh-light`, or `/smh-do`.
2. **D3: script or prose?** ~~The cuttable half.~~ **The audit changed my answer — I now recommend
   keeping it, and the cut is no longer worth offering.** It costs ~40 lines, not ~120 (both inputs
   are already public in existing scripts), and finding F3 showed the prose version is the one that
   goes wrong: the obvious shortcut would have rated an edit to the *enforcement suite* as safe. A
   rule an agent can negotiate with is precisely what SCC-161 proved does not hold.
3. **May the lightweight lane ever touch `.agents/rules/`?** My call is **no** — a rule is law, and
   law changes get a plan. Worth your confirmation, because it means "fix a typo in a rule file" takes
   the full lane, which is arguably the same over-engineering this ticket exists to kill. (A narrow
   carve-out — prose-only edits that change no gate, no path and no instruction — is possible, but it
   reintroduces a judgement call, which is what condition 1 was designed to remove.)

---

## Self-Audit (2026-08-15)

**Right-size: FULL.** The plan touches a rule, the door law, four platform surfaces, and adds a script
other scripts' constants feed — every trigger in the Full list fires. All phases walked.

- **Phase 0 — scope + checkable list.** Change set named (8 files, §4). Acceptance taken from the
  ticket's ACCEPTANCE block, tightened to 7 checkable items (the seventh — *the lane ejects when the
  real diff stops qualifying* — is new, added by finding F1). Traceability run both directions: every
  acceptance item has a step; the one step with no direct item (`AGENTS.md`, row 7) traces to *"one
  place agents load"* via the ⛔ ARTIFACTS block that names the exemption list, and is kept.
- **Phase 0 lane check — LOCAL.** No deployable path. Confirmed against
  `task_preflight.py:871` — the command centre has no deployable surface at all, so this can only
  ever be Task work. Closes through `/smh-close-task-merge-tree`. ✅
- **Phase 1 — blast radius.** New command → four doors + `commands/INDEX.md` (104 rows) + the
  `_RULE_POINTERS` lint (`workflow_lint.py:70` — a command body containing `git commit`/`git
  worktree` must cite `git-policy` / `worktree-per-story`; **this command body will contain both, so
  both pointers are mandatory**). New script → `scripts/INDEX.md` row + its test; **no hook calls it**,
  so nothing fires at commit time. Rule edit is **additive to an existing section** — no citation
  anywhere is invalidated, checked because a rename would have hit every command that cites
  `artifacts-always-first`. SOP + usage surfaces land in the same commit, so `sop_currency` passes
  without `[sop-ok]`. Nothing under `_artifacts/_memory/` is touched.
- **Phase 1 — sibling lanes.** `git worktree list`: this lane and `main` only. **No landing-order
  dependency.** SCC-161 (which rebuilt the SOP this plan edits in six places) is already **merged** —
  base `0b163d1` contains it, so the trace is against the current document, not a stale one.
- **Phase 2 — over-engineering gate.** Two tripwires fired; both survive with justification recorded
  (F4, F5). Two more were caught and fixed rather than justified (F1, F2). One design was found wrong
  and rewritten (F3). No new rule file — D1 refuses one on the gate's own stated grounds.
- **Phase 3 — pre-mortem.** Eight rows walked; three findings survived (F2 empty-input, F6 fresh
  clone, F7 `python3`/`python`). Rollback: every change is additive on a `chore/*` branch and revertible;
  the only irreversible act already taken is the ticket's move to `In Progress`.

### Findings

| # | Where | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| F1 | §3 (lane definition) | **High** | Qualification runs on *intended* paths before any file exists. An agent under-declares its scope, gets `LIGHT`, and nothing re-checks — the lane silently swallows work that needed a plan. | **Fixed in plan** — new § "The EJECT": re-run against `git diff --name-only main...HEAD` before the walkthrough; not `LIGHT` → the gate re-arms and the work continues on `/smh-quick-dev`. New acceptance item #7. |
| F2 | §2 D3 | **High** | Empty path set reads as `LIGHT`. A named Phase-2 tripwire (*"a check whose empty input reads as a pass"*) and the one input an agent controls completely. | **Fixed in plan** — empty → `TASK`, pinned by a test case. |
| F3 | §2 D3 | Med | Design was wrong *and* over-costed. `sop_currency.classify()` exempts `.agents/scripts/tests/` — correct for its own question, fatal for this one: the shortcut would rate an edit to the **enforcement suite** as LIGHT. Cost was also ~3× over, which had wrongly made this the "cuttable half". | **Fixed in plan** — rule is now *anything under `.agents/` is never LIGHT*; `classify()` demoted to a drift cross-check in the test. Open question 2 rewritten; the cut is withdrawn. |
| F4 | §2 D2 | Med | Phase-2 tripwire: **a new command where an existing one could take a flag.** `/smh-quick-dev --light` is the obvious simpler alternative. | **Justified, kept.** A flag makes the plan-first exemption depend on an argument *the agent chooses* — an agent authoring its own exemption, which `000-PLAN-FIRST-GATE.md:92-97` forbids by name. The carve-out mechanism in this system is **command identity**, and it has to stay that. |
| F5 | §2 D3 | Med | Phase-2 tripwire: **a new script where an existing one could grow a subcommand.** `task_preflight.py` already answers a LOCAL/HANDOFF question. | **Justified, kept.** That script is the *merge* gate (1289 lines, imports four modules); this is a *plan-time* question asked before any diff exists, and `task_preflight` does not hold the usage-surface half. Coupling them would make a plan-time classifier a dependency of the close-out. Shrunk to ~40 lines by F3. |
| F6 | §3 (what it KEEPS) | Low | On a **fresh clone** `core.hooksPath` is unset, so the keyless-commit refusal the lane leans on is silently OFF — every "kept" guarantee degrades to prose, and nothing says so. | **Bake into the rule at build time** — one line: the lane's guarantees assume armed hooks; a fresh machine arms them via the migrations kit. |
| F7 | §5 | Low | Verification block is `python3`-only. The PC has only `python`; the SOP text written in step 6 is read on both machines. | **Noted for the build** — plan-local commands stay as-is (this Mac), but the SOP prose must not hard-code either form. |
| F8 | §2 D3 | Low | `HANDOFF` is unreachable in the lobby (`task_preflight.py:871` — no deployable surface here). Not dead code (the lane may run in a project repo), but a command body implying the lobby can hand off would be wrong. | **Noted for the build.** |

**Sibling-lane landing order:** none — this is the only live lane.

### Four gates

- **Verification strategy present?** ✅ Every acceptance item names the command that proves it (§4
  assertions + §5). Six named test cases exist before the script does.
- **Anything irreversible?** One: SCC-162 → `In Progress`, already done, trivially reversible. No
  delete, no rename, no force-push, no `main` merge in this plan — the merge is a separate,
  operator-invoked act.
- **Any step vague enough that the builder will guess?** The SOP edit (row 6) spans six sections and
  is the loosest step. Tightened by naming all six and pinning them to the anchor test.
- **Convention fit?** ✅ `smh-*` naming law (SCC-63), one door per platform (SCC-66), artifacts under
  `_artifacts/_main/<date>_<slug>/`, exemptions in one closed list, no third door to `main`.

Audit verdict: GO
