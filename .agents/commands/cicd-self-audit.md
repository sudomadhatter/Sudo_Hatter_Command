---
description: Pre-dev plan/story audit — three lenses (Repo Reality + Scope Ledger, Parity + Blast, Pre-Mortem), the anchor rule (no anchor, no finding), coverage-not-findings reporting, and an amendment rule that forbids ever adding a fourth lens. Runs BEFORE coding: verifies the plan is on track against the codebase and the story's ACs — NOT a code audit (that is /cicd-code-review, later, on a real diff). Auto-invoked by /cicd-dev-story-tests right after the plan is written.
platforms: [opencode, antigravity]
---

# /cicd-self-audit — Pre-Dev Plan Audit (three lenses, anchored)

**The `cicd-` twin of `/smh-self-audit` — same contract, product mechanics.** Deliberate
divergences, stated as such: Step 0 **binds exactly one project, never the lobby**
(`smh-target-resolution`); the acceptance list is the **story's ACs**, not a ticket block; Lens 1
may use the code graph when fresh; Lens 3's failure narratives are product-shaped (state,
contracts, auth). Fix a shared idea in one twin, diff the other.

## ⛔ THE AMENDMENT RULE — carved here, above the lenses, on purpose

<!-- twin-law: audit-amendment -->
When a plan this audit cleared later breaks something, the fix is an amendment to a
**deterministic list** — the marker vocabulary, the anchor definitions, or the Scope Ledger
rules. **Adding a fourth lens is not a permitted response to a miss, ever. Delete instead.**
<!-- /twin-law -->
Months of lens accretion produced the 2026-08-18 failure this rebuild answers (8 lenses, 44
findings, ~half manufactured, the refutation pass killed unfinished — nothing delivered).
Production of findings is cheap and front-loaded; filtering is back-loaded and O(n) over an n the
production stage inflates. The anchor rule is the only filter that survived measurement, and it
runs at the source.

**Scope (operator, 2026-08-19):** a quick brainstorm to gate known agent issues **before wasting
time developing something that was never going to work**. It verifies the plan is on track. NOT a
full code audit — that is `/cicd-code-review`, later, on a real diff with real gates.

> **Rules in force for this command:**
> - `.agents/rules/smh-target-resolution.md` §STD + §BIND — bind exactly ONE project, **never the
>   lobby**; every path below resolves under `PROJECT_ROOT`
> - `.agents/rules/artifacts-always-first.md` §7 — the audit is **appended into the plan it
>   audited**, never standalone; §2 (Create the artifact folder + plan) defines the `## Declared
>   Change Set` block Lens 1 parses
> - `.agents/rules/000-PLAN-FIRST-GATE.md` — this audit runs BEFORE the literal `approved`
> - `.agents/rules/constitution.md` — Ask-First and surgical-change, audited in Lens 1
> - `.agents/rules/port-checklist.md` — the six checks Lens 2's cross-repo row demands; absence on
>   differing copies is a NO-GO (SCC-176)
> - `.agents/rules/worktree-per-story.md` §"cwd is not intent" — why Step 0 pins the target from
>   command output and Lens 2 reads the sibling lanes
> - `.agents/rules/code-standards.md` §6.5 — disposition: REAL · changes BEHAVIOUR · in THIS
>   plan's scope, all three YES before a finding stands
> - `.agents/rules/tests-must-gate-for-real.md` — the plan's test strategy is audited against it:
>   a plan naming no way to prove its checks non-vacuous is missing that step

## Step 0 — Resolve the target project (FIRST — before any lens)

Bind per `smh-target-resolution` §STD + §BIND: self fast-path → `$ARGUMENTS` override (remainder =
focus area) → `.agents/active-project.txt` → else **STOP and ask** — never guess, never the lobby.
(Auto-invoked from `/cicd-dev-story-tests`, the pointer is already set.) Set `PROJECT_ROOT`, echo
exactly `Target: Projects/<name>`, and resolve every bare path under it. Then pick, out loud:

- **Skip** — a one-line copy/doc/config tweak. Say so and stop.
- **PRE-DEV (the default).** No plan/story → **STOP**; auditing an invented plan is the failure
  this command exists to catch.
- **POST-DEV (retroactive).** Code already exists: audit the story's ACs + the actual change set,
  label the section `retroactive`.

## THE CONTRACT — anchor or it does not exist

An unanchored finding compares the plan to a counterfactual. An anchored one compares it to a file.

- **Every finding names an anchor with the literal text it read.** The grammar (its shape is
  spot-checked by `test_self_audit_contract.py`; the exist-conditions below are applied law at
  run time, not machine-enforced):
  anchor = `<path>:<line>` | `<path>` | `step <N>` — with the literal text read, quoted.
  The path must exist under `PROJECT_ROOT`; the step/AC number must exist in the plan or story.
  **No anchor, no finding — deleted, not demoted.**
<!-- twin-law: audit-coverage -->
- **The schema demands COVERAGE, not findings.** Each lens returns the fixed block:

  ```
  lens:        <1|2|3> <name>
  checks_run:  <the checks this lens executed, one line each>
  read:        <files/commands actually read, with paths>
  verdict:     clean | findings below
  ```

  **Full coverage with zero findings is a complete, successful run** — that sentence is what
  makes "I found nothing" a valid deliverable, and it is why no lens here is handed a
  `findings[]` array to fill.
<!-- /twin-law -->
- **Judgment is denied a severity:** beliefs with no check → `### Observations`, uncounted.
<!-- twin-law: audit-corroboration -->
- **Corroboration promotes, never demotes.** The anchor filter runs FIRST; corroboration runs on
  survivors only. Agreement between lenses is *salience, not truth* — correlated lenses sharing a
  model and a prompt frame are not independent samples. **Corroboration affects SORT ORDER only**:
  two lenses on one anchor sorts to the top of its severity band, flagged `x2`. Severity is set by
  consequence alone — a single lens finding a structural blocker is top severity. Dedupe key is
  the **shared anchor**, never the same topic (topic-merging manufactures fake corroboration), and
  the lenses run **blind** to each other's output.
<!-- /twin-law -->

## The two levels — scope of inquiry, never a verdict

| Level | Runs | Derived from the plan's `## Declared Change Set` — never a caller flag |
|---|---|---|
| **LEDGER** | Lens 1 only | docs/config-only, or ≤2 `EDIT` files touching no state machine, contract, auth, schema, or multi-consumer symbol |
| **LEDGER+BLAST** | all three | a state machine, an SSE/WebSocket or API contract, auth, a shared schema, a symbol with many consumers, both backend AND frontend, a file in more than one repo — or any `DELETE` |
| **anything else** | all three | the plan matches neither row cleanly, or the block is absent or unparseable — the default is the HEAVIER level, never agent preference (mirrors the engine's own default: step-01 § The two levels, standard is "the default whenever the level did not arrive") |

<!-- twin-law: audit-levels-shape -->
No minute budgets and no finding caps — both rejected as unscalable (parent ruling 5). The roster
of three plus the anchor rule is what replaced them: there is nothing left to run long on. State
the level in the output header.
<!-- /twin-law -->

## Lens 1 — Repo Reality (every level)

**Does the plan's world exist?** Under `PROJECT_ROOT`, quoting what you read:

1. Every path, symbol, endpoint, schema, and command the plan names → exists (graph or grep,
   quoted). Every AC maps to a plan step and every step back to an AC — an AC with no step
   under-delivers silently; a step with no AC feeds the Scope Ledger.
2. The `## Declared Change Set` block parses:
   `python3 .agents/scripts/declared_change_set.py parse <plan>` *(PC: `python`)*.
   Absent block or `incomplete` bullets **IS a finding** — `/cicd-code-review` Step 1.5's drift
   check depends on absence being loud.
3. Both-stacks flag: the plan modifies backend AND frontend → recommend the split (constitution
   Ask-First), anchored to the two file lists.
4. Reuse check: a helper/pattern the plan is about to build already exists → finding, anchored to
   the existing symbol's path.

### The Scope Ledger (inside Lens 1) — over-engineering as a ledger, never an opinion

**Precondition:** the story carries ≥2 ACs and each names a concrete observable — fewer, or an AC
with no observable, **is itself the finding** (a vague list makes the ledger match everything).

Every artefact the plan **CREATES** (op `NEW`; wholesale rewrites count) × the AC that requires
it. A finding exists **only when a row's acceptance cell is empty**, written exactly:
"`<path>` is created by plan step `<N>`; **no acceptance row requires it**" — never "`<path>` is
unnecessary"; the fix is delete-or-add-the-row and the audit does not pick. **Caller count** by
grep, printed, falsifiable. `EDIT` rows are in scope by definition. Elegance, abstraction level,
premature generality: not findings, no severity, not logged.

## Lens 2 — Parity + Blast (LEDGER+BLAST)

For each declared change, trace against the **current** codebase — graph-first when fresh, grep
as the normal fallback:

- **The code graph, gated:** `code-review-graph status --json` is the only ground truth of "indexed"
  (never a doc mention), and `built_at_commit` must equal `current_sha` before you trust an answer.
  Compare its `lastCommit` to `git rev-parse HEAD` — stale index = **lead, not authority**;
  grep-verify every `0`/LOW `impact()` (it misses attribute-dispatch). The pure-grep path is the
  NORMAL path (operator, 2026-08-19), not the degraded one.
- changed return / props / schema → every existing caller, consumer, query accounted for.
- **Contract two-sidedness:** one side of a paired contract (SSE event, API schema, DB shape,
  signature) changed → the plan names the other side, or that is the finding. The code graph cannot see
  shared-DB coupling — this row is manual.
- **Cross-repo port (SCC-176):** the file exists in more than one repo and the copies differ
  (`git diff --no-index`, exit 1 proves it) → the plan carries the six-check port section with
  command output, or **NO-GO**.
- **Twins and doors:** a paired surface (cicd/smh command, generated door) → divergence stated or
  ported.
- **Sibling lanes** (`worktree-per-story` §"Am I alone in this repo?"): story lanes are `claude/*`
  worktrees off ONE epic branch, several at a time, and a sibling's uncommitted tree is invisible to
  grep from here. **Bind every call — a bare `git` here reads the lobby, not the project:**
  `env -u GITHUB_TOKEN git -C "$PROJECT_ROOT" fetch origin <epic-branch>` first (a stale remote ref
  inflates every sibling's apparent set), then `git -C "$PROJECT_ROOT" worktree list`, then per tree
  `git -C <tree> status --short` + `git -C <tree> diff --name-only origin/<epic-branch>...HEAD`. The
  ref is the story's EPIC branch (`epic/<KEY>-<slug>`), never `origin/main` (SCC-165). A file in both
  their set and this plan's declared set is a **landing-order dependency**: name which lane lands
  first and what happens to this work if it does not.
- **Risk context (the code-graph seam):** `python3 .agents/scripts/risk_seam.py classify --repo
  "$WORKTREE" <declared paths>` *(PC: `python`)* informs this lens's depth. ⛔ **`--repo` is not
  optional here (SCC-289).** Without it the seam resolves the repo from CWD, which during a project
  audit run from the command centre is the CENTRE — and the centre carries no graph, so the answer
  is always `unclassified` and looks exactly like a project whose index was never built — per file, the highest risk score among its
  changed functions, how many flows it sits on, and which changed functions have no test.
  **Informs, never gates** — `gates_audit()` is False for every return by pinned contract, so audit
  semantics are identical whatever it says. `"status": "unclassified"` is a **normal result** (no
  graph, a stale graph, the tool absent, or a thin project with no `.agents/scripts/`), fixed with
  `code-review-graph update` if you want the context.
- ⛔ **Read `test_links` before `untested` — it is a per-repo number, and it decides whether the list
  means anything.** It counts TESTED_BY edges naming a real subject, and a link needs a **statically
  resolvable import**: a test that reaches its subject by `subprocess` or a runtime
  `sys.path.insert(...)` produces none. Measured 2026-08-22 — `AGY_AVIATIONCHAT` **3427**, the command
  centre **0**. A high count makes `untested` real signal (*where to look*, confirmed against the test
  file, never a finding on its own); a **0** means the graph has no test data at all, so it lists every
  changed function and you should ignore it outright. `risk` and `flows` are unaffected either way.

## Lens 3 — Pre-Mortem (LEDGER+BLAST) — bounded, and the bound is the point

Shipped, and it silently corrupted user state — why? **It CANNOT originate a finding.** It
attaches a product-shaped failure narrative — rehydration, the error/timeout path, concurrent
events, expired auth, the type-union edge, the hallucinated requirement — to a finding an
anchored lens already raised. Unattached output is **discarded**.

## Output — appended into the plan, never a standalone file

Append `## Self-Audit (<date>)`: level and mode (`retroactive` when POST-DEV) · one coverage
block per lens (fixed schema) · findings table `| anchor | literal text read | consequence |
severity |` sorted by severity then corroboration · `### Observations` (uncounted) · sibling
landing-order dependencies · the canonical line:

```
Audit verdict: GO | NO-GO
```

**NO-GO on exactly two grounds:** an anchored finding whose consequence breaks an AC or a hard
gate (constitution, port rule, tests-must-gate), or the Scope Ledger precondition failing. All
else is findings on a GO. Bake fixes inline (`⚠️ AUDIT FINDING`) so the dev reads them in context.
(The standalone `self-audit-stress-test.md` stays retired, 2026-08-02.)

## After the work is built

Lens 2 is the half that expires — traced against the epic branch of plan time while sibling
stories land. It re-runs automatically as `/cicd-code-review` Step 0.7; invoke this command
directly post-dev only when that is not enough (a lane resumed after days, the AC list itself in
doubt) — POST-DEV mode, Lens 2 + Lens 3's external rows, section labelled `retroactive`.

## Stay in lane

Audit and annotate the plan; write no implementation, touch no code the plan is about, transition
nothing. One product: a `## Self-Audit` section and a verdict.

Optional focus area: $ARGUMENTS
