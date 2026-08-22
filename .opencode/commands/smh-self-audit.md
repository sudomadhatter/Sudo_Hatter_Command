---
description: Pre-work plan audit for TASK work — three lenses (Repo Reality + Scope Ledger, Parity + Blast, Pre-Mortem), the anchor rule (no anchor, no finding), coverage-not-findings reporting, and an amendment rule that forbids ever adding a fourth lens. A quick brainstorm that gates known agent issues before time is spent building the wrong thing — NOT a code audit (that is /smh-code-review, later, on a real diff). PRE-WORK by default; POST-DEV/retroactive audits the ticket's ACCEPTANCE block + change set. Acts on the repo you are standing in, so the command centre is a valid subject. Auto-invoked by /smh-quick-dev. Use when the user says "audit the task plan" / "smh self audit".
platforms: [opencode, antigravity, claude, codex]
---

# /smh-self-audit — Pre-Work Plan Audit (three lenses, anchored)

## ⛔ THE AMENDMENT RULE — carved here, above the lenses, on purpose

<!-- twin-law: audit-amendment -->
When a plan this audit cleared later breaks something, the fix is an amendment to a
**deterministic list** — the marker vocabulary, the anchor definitions, or the Scope Ledger
rules. **Adding a fourth lens is not a permitted response to a miss, ever. Delete instead.**
<!-- /twin-law -->
Months of exactly that accretion produced the 2026-08-18 failure this rebuild answers: 8 lenses,
each handed a `findings[]` schema, returned 44 findings (~half manufactured to succeed at the
assigned task); the back-loaded per-finding refutation pass was the slowest phase, unfinished at
35 minutes, killed — the run delivered nothing. Production of findings is cheap and front-loaded;
filtering is expensive, back-loaded, and O(n) over an n the production stage is incentivised to
inflate. The anchor rule below is the only filter that survived measurement, and it runs at the
source.

**What this is (operator scope statement, 2026-08-19, governing every decision here):** a quick
brainstorm to gate known agent issues and think outside the box **before wasting time developing
something that was never going to work**. It verifies the implementation plan is on track. It is
NOT a full code audit — that is `/smh-code-review`, which runs later on a real diff with real
gates.

> **Rules in force for this command:**
> - `.agents/rules/artifacts-always-first.md` — the audit is **appended into the plan**, never a
>   standalone file; §2 (Create the artifact folder + plan) also defines the `## Declared Change
>   Set` block Lens 1 parses
> - `.agents/rules/000-PLAN-FIRST-GATE.md` — this audit runs BEFORE the literal `approved`
> - `.agents/rules/constitution.md` — Ask-First and surgical-change; one of the hard gates the
>   NO-GO grounds name
> - `.agents/rules/worktree-per-story.md` §"cwd is not intent" — why Step 0 pins the repo from
>   command output, and why Lens 2 reads the sibling worktrees instead of trusting this tree
> - `.agents/rules/port-checklist.md` — the six checks Lens 2's cross-repo row demands; a plan
>   that skips the section on differing copies is a NO-GO, not a note (SCC-176)
> - `.agents/rules/code-standards.md` §6.5 — disposition: REAL · changes BEHAVIOUR · in THIS
>   plan's scope, all three YES before a finding stands
> - `.agents/rules/tests-must-gate-for-real.md` — the plan's test strategy is audited against it
>   in Lens 1: a plan naming no way to prove its checks non-vacuous is missing that step (SCC-145)

## Step 0 — Resolve the repo (FIRST) — from command output, never from belief

The subject is **where you are standing**, not a pointer. If `$ARGUMENTS` names a path, use it;
otherwise the current repo. Do **not** read `.agents/active-project.txt` — the command centre is
a legitimate subject here.

```bash
REPO=$(cd "<the path you resolved>" && git rev-parse --show-toplevel)
BRANCH=$(git -C "$REPO" rev-parse --abbrev-ref HEAD)
echo "Repo: $(basename "$REPO") | Branch: $BRANCH"
```

Name the plan you are auditing (its path) and the ticket key it belongs to. Then pick, out loud:

- **Skip** — a typo, a comment, a one-line doc tweak. Say so and stop; it does not need an audit.
- **PRE-WORK (the default).** No plan file → **STOP and say so.** Inventing a plan to audit is the
  failure this command exists to catch. Write the plan, come back.
- **POST-DEV (retroactive).** The work already exists. Do not invent a plan — audit the ticket's
  `SCOPE` + `ACCEPTANCE` block (`acli jira workitem view <KEY>`) plus the actual change set, and
  **label the run `retroactive`** in the section you write. See § After the work is built.

## THE CONTRACT — anchor or it does not exist

An unanchored finding compares the plan to a counterfactual. An anchored finding compares the
plan to a file.

- **Every finding names an anchor with the literal text it read.** The grammar (its shape is
  spot-checked by `test_self_audit_contract.py`; the exist-conditions below are applied law at
  run time, not machine-enforced):
  anchor = `<path>:<line>` | `<path>` | `step <N>` — with the literal text read, quoted.
  The path must exist on disk; the step number must exist in the plan.
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
- **Judgment is not banned — it is denied a severity.** A belief with no check behind it goes in
  a non-blocking `### Observations` list, never counted, never in the findings table.
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

| Level | Runs | When — derived from the plan's `## Declared Change Set`, never a caller flag |
|---|---|---|
| **LEDGER** | Lens 1 only | every path is docs/artifacts, or ≤2 files with op `EDIT`, no rule / gate / hook / script / door surface, no deployable path |
| **LEDGER+BLAST** | all three | anything touching a rule, a gate or hook, a script others import, a command/door surface, more than one platform, a file that exists in more than one repo — or any `DELETE` |
| **anything else** | all three | the plan matches neither row cleanly, or the block is absent or unparseable — the default is the HEAVIER level, never agent preference (mirrors the engine's own default: step-01 § The two levels, standard is "the default whenever the level did not arrive") |

<!-- twin-law: audit-levels-shape -->
No minute budgets and no finding caps — both rejected as unscalable (parent ruling 5). The roster
of three plus the anchor rule is what replaced them: there is nothing left to run long on. State
the level in the output header.
<!-- /twin-law -->

## Lens 1 — Repo Reality (every level)

**Does the plan's world exist?** Check against the tree, quoting what you read:

1. Every path, command, script, rule, and door the plan names → exists (`ls` / `grep`, quoted).
   Plan step numbers referenced anywhere → exist.
2. The `## Declared Change Set` block parses:
   `python3 .agents/scripts/declared_change_set.py parse <plan>` *(PC: `python`)*.
   An **absent block or `incomplete` bullets IS a finding** (anchor: the plan file itself) — the
   consumers (`/smh-code-review` drift check) depend on absence being loud.
3. Commands the plan intends to run exist on **both machines** — Mac has no bare `python`, the PC
   has no `python3`; stdlib only, no venv.
4. **Lane fit (wrong door) — at plan time, not at close-out:** the Declared Change Set touches a
   deployable product path (`backend/` `frontend/` `firebase/` `functions/` `mobile/` `.github/`)
   → say NOW which door ships it. Task lanes here land via `/smh-close-task-merge-tree`;
   deployable product work belongs in a project lane behind `/cicd-push-e2e`. The close-out
   preflight only discovers a wrong door after the work is built — this check is the plan-time
   tripwire.

### The Scope Ledger (inside Lens 1) — over-engineering as a ledger, never an opinion

**Precondition, upstream of everything:** the ticket carries ≥2 acceptance rows and each names a
concrete observable. Fewer, or a row with no observable, **is itself the finding** — a vague
acceptance list makes this ledger match everything and produce nothing, a green that lies.

One table: every artefact the plan **CREATES** (op `NEW` in the block; wholesale rewrites count)
× the acceptance row that requires it.

- A finding exists **only when a row's acceptance cell is empty**, and it is written exactly:
  "`<path>` is created by plan step `<N>`; **no acceptance row requires it**" — never "`<path>`
  is unnecessary". The fix is legitimately either *delete the artefact* or *add the row*, and the
  audit does not get to pick.
- **Caller count:** an artefact whose only caller is created by this same plan — countable by
  `grep`, printed, falsifiable by producing a second caller.
- `EDIT` rows are in scope by definition — the "you are touching too much" genre is dead here.
- Elegance, abstraction level, premature generality: **not findings**, no severity, not logged.

## Lens 2 — Parity + Blast (LEDGER+BLAST)

Toolkit work breaks by **reference and by convention**. Each row is a measured scar — check the
rows the Declared Change Set makes relevant, clear the rest in one line each:

| The plan changes… | Check, with output quoted | Scar |
|---|---|---|
| a command file | all four platform doors + `commands/INDEX.md` | SCC-66: a rename orphans four caches |
| a command **name** | every reference across `.agents/`, `docs/`, `_artifacts/`, `AGENTS.md` | SCC-63: renames leave live callers |
| a rule | its citing commands + `workflow_lint.py` `_RULE_POINTERS` | a command doing the thing must point at its law |
| a script | callers in `.githooks/` + its test + `scripts/INDEX.md` | a hook calling a changed signature dies on someone else's commit |
| a gate or hook | ships ARMED? arming marker in the diff? | VS Code hides hook output — warn-only reads as clean |
| a path move/rename/delete | every Markdown link + `#L` anchor repo-wide | relocated links are mis-pathed, not dead |
| the SOP or a usage surface | both halves in the SAME commit | armed `sop_currency.py` rejects otherwise |
| `_artifacts/_memory/` | is this the memory flow at all? | the store is read-only outside its own flows |
| a file existing in >1 repo | the plan's port section answers all six checks with command output — else **NO-GO** | SCC-176: three of four divergences were answerable at plan time |

**Twins:** a `cicd-*`/`smh-*` sibling exists → the plan says which diverges and why, or ports the
change to both. **Sibling worktrees:** `env -u GITHUB_TOKEN git fetch origin main` first — a bare `origin/main`
is this checkout's LAST PULL, and an unfetched base inflates every sibling's apparent change
set. Then `git worktree list`, then per tree
`git -C <tree> diff --name-only origin/main...HEAD` + `status --short` — any file in both their
set and this plan's declared set is a **landing-order dependency**: name which lane lands first
and what happens if it does not.

**Risk context (the code-graph seam):** `python3 .agents/scripts/risk_seam.py classify <declared
paths>` *(PC: `python`)* — where risk lives informs THIS lens's depth. It answers from the local
code graph: per file, the highest risk score among its changed functions, how many flows it sits on,
and which changed functions have no test. It **informs, never gates**: `gates_audit()` is False for
every possible return, by pinned contract, so the audit's semantics are identical whatever the
classifier says.

`"status": "unclassified"` is a **normal result, not a failure** — no graph, a graph built at a
different commit, or the tool not installed all return it, and the pure-Python path is the normal
path. `code-review-graph update` in that repo is the fix if you want the context.
⚠ `untested` reads the CALL GRAPH: a script exercised by spawning it as a subprocess reads as a test
gap even when it is thoroughly covered. Treat it as *where to look*, never as a finding on its own.

## Lens 3 — Pre-Mortem (LEDGER+BLAST) — bounded, and the bound is the point

Assume the plan shipped and quietly broke the operator's next session — why? The only genuinely
probabilistic lens, and the reason this command exists. **Bounded: It CANNOT originate a finding.**
It attaches a failure narrative — the silent one, the other-machine one, the fresh-clone one, the
sibling-lands-first one — to a finding an anchored lens already raised. Unattached output is
**discarded**, not demoted to an observation it never earned.

## Output — appended into the plan, never a standalone file

Append `## Self-Audit (<date>)` with: the level and mode (`retroactive` when POST-DEV) · one
coverage block per lens run (the fixed schema above) · the findings table
`| anchor | literal text read | consequence | severity |` sorted by severity then corroboration ·
`### Observations` (uncounted) · any sibling landing-order dependency · and the canonical line:

```
Audit verdict: GO | NO-GO
```

**NO-GO on exactly two grounds:** an anchored finding whose consequence breaks an acceptance row
or a hard gate (constitution, git policy, the port rule), or the Scope Ledger precondition failing.
Everything else is findings on a GO — this audit informs the operator's `approved`; it is not a
gate on it. Bake fixes into the plan inline (`⚠️ AUDIT FINDING` in the affected section) so the
builder reads them in context.

## After the work is built

Most of this audit does not go stale — one lens does:

| Lens | Post-dev? | Why |
|---|---|---|
| 1 — Repo Reality + Ledger | No | the decision is built; `/smh-code-review` Step 2 audits the diff against the acceptance list |
| 2 — Parity + Blast | **⭐ YES — the one that expires** | it was traced against the `main` of plan time; sibling lanes land while you build. Re-runs automatically as `/smh-code-review` Step 0.7 |
| 3 — Pre-Mortem | only the external-state rows | sibling-lands-first, platform caches, fresh clone |

Invoke directly post-dev only when Step 0.7's questions are not enough (a lane resumed after
days, `main` moved repeatedly, the acceptance list itself in doubt) — then POST-DEV mode, Lens 2
plus the external rows of Lens 3, and the section labelled `retroactive`.

## Stay in lane

Audit and annotate the plan; write no implementation, touch no file the plan is about, transition
no ticket. This command produces one thing: a `## Self-Audit` section and a verdict.

Optional additional input (a plan path, or a focus area): $ARGUMENTS
