# SCC-369 — Nag the agent, don't rewrite the rule

**Lane:** `chore/SCC-369-shape-nag` · worktree `.claude/worktrees/scc369-shape-nag`
**Ticket:** SCC-369 (Task, one consolidated lane, no subtasks)
**Base:** `origin/main` @ `645ea5e7`

---

## What is broken, in one paragraph

`command-shape.md` is standing law that reaches every platform and is obeyed by none of them.
It is summarized in `AGENTS.md` §6, restated in `zoo-team.md` for every Zoo seat, keyworded into
`rule-trigger.py`, and it fired twice as a `UserPromptSubmit` injection during the session that
measured this — while that same session violated it repeatedly. Measured over 25 Claude sessions
and 8,355 Bash calls, **1,946 commands broke that one rule: 23.3% of every Bash call made in
the transcripts.** The cost is not abstract: of 1,247 `git -C` invocations, **521 named a verb the
allow list cannot pre-approve**, and each is an approval stop that would have been silent in the
`cd <abs> && git <verb>` shape the rule already mandates. Compounding it, `AGENTS.md` §6 still
carries the **pre-SCC-351** text and says *"use `git -C`"* — the exact spelling Zoo auto-denies —
so an agent obeying the front door faithfully manufactures the prompts.

## The design call

The reflex fix is to write the rule again, more forcefully, in another place. That is measurably
the thing that does not work: five copies already exist. The operator's ruling (2026-09-01) is to
**nag instead** — inject the correction at the moment of the mistake, citing the rule file so the
agent is sent back to the law rather than handed a restatement.

**Why a nag binds where prose does not.** Prose sits in context competing with everything else and
is read *before* the mistake. A nag arrives *at* the mistake, attached to the exact command that
was wrong. It is not an instruction to weigh; it is a fact about what just happened, and there is
nothing to rationalize past.

**Channel, established by probe rather than assumption** (this session):

| Channel | Reaches the model? |
|---|---|
| `PostToolUse` → `hookSpecificOutput.additionalContext` | ✅ verbatim |
| `PostToolUse` → `systemMessage` | ❌ |
| hook stderr, exit 0 | ❌ |
| `PreToolUse` → `allow` + `permissionDecisionReason` | ❌ |

`PostToolUse` is also the correct *safety* choice, not a compromise: it runs after the command, so
it can never block, slow, or wedge a headless session. Measured cost ~36 ms against an existing
~145 ms `PreToolUse` chain, entirely off the critical path.

⛔ **Two hard limits this plan will not cross.**
1. **Never `permissionDecision: "ask"`** — it becomes an auto-DENY in auto mode and strands
   headless runs (`hook-ask-becomes-autodeny-in-auto-mode`).
2. **A nag cannot protect against a destructive command** — it speaks after the damage. `git add -A`
   (4 hits) and `git worktree remove --force` (18 hits) stay `PreToolUse` concerns and are
   explicitly OUT of scope here.

## Scope ledger

| # | Change | File(s) | Reaches |
|---|---|---|---|
| 1 | §6 gate reconciled to the rule | `AGENTS.md` | all four platforms |
| 2 | root entry files added to the `git -C` scan | `.agents/scripts/tests/test_zoo_permissions.py` | suite |
| 3 | the nag hook + its registration | `.agents/hooks/shape-guard.py`, `.claude/settings.json` | Claude Code only |
| 4 | the measurement + its controls | `.agents/scripts/shape_scan.py`, `.agents/scripts/tests/test_shape_scan.py` | both platforms |
| 5 | the ruling promoted to law | `.agents/rules/command-shape.md` §Nag, `.agents/rules/INDEX.md` | all four platforms |
| 6 | Zoo allow-list drift reconciled | `.vscode/settings.json` | Zoo, both machines |
| — | SOP + changelog (required by `sop-currency` for 1, 5) | `docs/_scc_sops_prds/workflows_testing_SOP.md` + changelog | the operator |

## Declared Change Set

- EDIT `AGENTS.md` — §6 COMMAND-SHAPE GATE still carries the pre-SCC-351 `git -C` text → A
- EDIT `.agents/scripts/tests/test_zoo_permissions.py` — widen the `git -C` scan to the root entry files → A
- NEW `.agents/hooks/shape-guard.py` — the PostToolUse nag; always allows, cites the rule → B
- NEW `.agents/scripts/tests/test_shape_guard.py` — the nag's positive, negative and `allow`-mutant batteries → C
- EDIT `.claude/settings.json` — register the hook under `PostToolUse` → B
- NEW `.agents/scripts/shape_scan.py` — the measurement over both stores → E
- NEW `.agents/scripts/tests/test_shape_scan.py` — the six negative and five positive controls → E
- EDIT `.agents/rules/command-shape.md` — add §Nag, the operator's ruling as law → F
- EDIT `.agents/rules/INDEX.md` — the §Nag row → F
- EDIT `.vscode/settings.json` — reconcile the 143 store-only allow entries → G
- EDIT `docs/migrations/zoo-code-permissions-guide.md` — the guide's own count line is asserted against the tracked lists by `test_guide_currency`, so promoting eight rows makes this edit mandatory, not optional; it also records WHY the store was reset rather than merged → G
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — required by `sop-currency` for the `AGENTS.md` and rule edits → H
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — the one-line change record → H
- EDIT `_artifacts/_main/INDEX.md` — this lane's row → H
- EDIT `.agents/hooks/INDEX.md` — the new hook's row; that file calls itself the MASTER index → B
- EDIT `.agents/scripts/INDEX.md` — the new script's row → E
- EDIT `.agents/scripts/tests/test_rule_frontmatter.py` — §Nag's six checks; the plan's RED-first section named this file but the ledger did not list it → F
- EDIT `docs/doc-graph.json` — GENERATED by the `refresh-maps` pre-commit hook whenever a rule or doc edit moves a node; declared so the drift check reads it as expected output, not an undeclared write → H
- EDIT `docs/doc-graph.md` — GENERATED alongside the json by the same hook, same reason → H
- EDIT `.agents/hooks/guard-cwd-escape.py` — REVIEW FIX: its remedy 2 told the model to use `git -C`, so an agent obeying that PreToolUse guard was immediately nagged by the new PostToolUse one; two hooks in one settings file steering opposite ways → B
- EDIT `docs/migrations/install_guides/new_machine-migration-guide.md` — REVIEW FIX: three RUNNABLE `git -C … status --short` lines survived in a bash fence while the changelog claimed the guidance was the same everywhere → A

⛔ `.claude/hooks/` is NOT in this set, and the reason is **not** that it is absent. It is a
GENERATED MIRROR: `.agents/hooks/INDEX.md:3` — *"MASTER here — mirrors to `.claude/hooks/` and
project vendored copies via `/smh-sync-agents`"*. Editing the mirror by hand is the thing that is
forbidden; it is excluded because `/smh-sync-agents` owns it, not because it does not exist.

## Sibling lanes — landing order (read at Step 0.5, not at merge)

`chore/SCC-367-retire-slash-cmd-updating` is live and already in review (its four keyed
`lens-SCC-367-*` trees are cut). Its diff and mine **truly overlap** on three paths:

| Shared path | Their change | Mine |
|---|---|---|
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | retires `/smh-slash-command-updating` from §3 | adds the §Nag usage note |
| `_artifacts/_main/INDEX.md` | their lane row | my lane row |
| `docs/doc-graph.json` · `.md` | regenerated cache | regenerated if the rule edit moves a node |

**SCC-367 lands first** — it is further along, and its change is a retirement that mine must not
resurrect. **If it does not land first:** my SOP edit conflicts on §3 and my INDEX row conflicts on
position. Both are additive and resolve by taking both sides; neither is semantic. Mitigation:
write the SOP and INDEX edits **last** in this lane, and absorb `origin/main` immediately before
the review gate rather than at close-out (`lane-collision-is-gates-not-files` — zero file overlap
would still require re-running their gates on my blobs, and here the overlap is real).

## RED first — the assertion for each item

Assert-first is the house standard, so every item below names the check that must **fail** before
the change and pass after. Mutants are listed where absence alone would be satisfiable.

**1 · `AGENTS.md` §6.** New check in `test_zoo_permissions.py`: the root entry files carry no
`git -C` outside a blockquote. Fails today on `AGENTS.md:172`. **Mutant:** re-inserting `git -C`
into `CLAUDE.md` must also go red, proving the scan is not pinned to one filename.

**2 · Scan widening.** The same check IS item 2 — it is written once and covers both. Its control:
a fixture entry file containing `> git -C` in a blockquote must stay GREEN, so teaching prose is
not swept up (the existing exemption behaviour).

**3 · `shape-guard.py`.** `test_shape_guard.py` drives the hook with crafted payloads:
- a piped gate → exactly one nag naming `command-shape.md` rule 3
- an exit-echo tail → one nag naming rule 2
- a `git -C` invocation → one nag naming rule 1, and naming the `cd <abs> && git` remedy
- a clean command → **silence** (the negative control; a nag that fires on everything is noise)
- a `grep "git -C"` and a heredoc body containing `git add -A` → **silence** (the two false
  positives that beat the first scanner)
- malformed JSON on stdin → exit 0, no output (fails open, per `guard-cwd-escape.py`)
- ⛔ **registered through `run-hook.sh`, never a bare interpreter.** `test_shape_guard.py` asserts
  the `.claude/settings.json` entry matches the `sh "$CLAUDE_PROJECT_DIR/.agents/hooks/run-hook.sh"`
  form the other four use, and that no rule names `python3`/`python` directly. `run-hook.sh:11-13`:
  *"NEVER name one platform's binary. Probe, in preference order, every time."* The session probe
  that proved the channel was registered as `python3 <path>` — shipping that shape reproduces
  SCC-77 exactly: on the PC (`python`, no `python3`) it exits **127 in silence**, and a hook that
  fails to launch is indistinguishable from a hook with nothing to say.
- the test spawns the hook with `sys.executable`, never a hardcoded interpreter (`run_all.py:77`)
- **the decision is asserted to be `allow` in every case, including every hit.** This is the
  load-bearing one: a mutant flipping it to `ask` must fail the suite, because `ask` auto-denies.

**4 · `shape_scan.py`.** `test_shape_scan.py` reuses the six negative and five positive controls
already written and proven this session. The negative battery is the point — the first cut counted
a `grep` *for* `"git -C"` as a use of it, and heredoc bodies as commands.

**5 · The rule.** `test_rule_frontmatter.py` already gates rule shape; add a check that
`command-shape.md` carries the §Nag section and that `rules/INDEX.md` has its row.

**6 · Zoo drift.** `zoo_permissions_apply.py --status` must close reading *in sync with tracked
file* on both lists. Today: `allowedCommands: 255 (143 store-only)`.

## Blast radius, measured not inferred

- **Items 1, 2, 5** are text and a test — no runtime behaviour changes anywhere.
- **Item 3** adds one `PostToolUse` entry. It cannot deny (asserted by test), cannot block, and
  fails open. Worst realistic failure is a spurious nag, which costs one line of context.
- **Item 4** is a new script nothing else calls; it reads two stores read-only.
- **Item 6** is the only item that changes what an agent may *run*. It is additive-to-tracked only
  — the 143 store-only entries get reviewed and either promoted into `.vscode/settings.json` or
  dropped. ⛔ **Per `/smh-llm-approvals`, no row is added that Zoo's deny list refuses, and
  `deniedCommands` is not touched.** Any drop is a row the operator names.

## Risks and the answer to each

| Risk | Answer |
|---|---|
| The nag becomes noise and gets ignored | The negative controls: a clean command must produce silence. Scope stays at three rules — measured at 23.3% of every Bash call — and does not grow without a new measurement. |
| Item 6 silently narrows what Zoo may run, mid-lane | Report the 143 first, act only on the operator's named picks; `deniedCommands` untouched. |
| The hook slows a headless run | `PostToolUse` is off the critical path; ~36 ms measured; fails open on any exception. |
| `AGENTS.md` edit desyncs the SOP | `sop-currency` gate forces the SOP + changelog into the same commit. Not opted out with `[sop-ok]` — items 1 and 5 are real usage changes. |
| Six items in one lane is too coarse to review | They share `command-shape.md` as their subject and overlap in `test_zoo_permissions.py` and `.claude/settings.json`; splitting would collide on the same files (`work-consolidation` rule 2). |

## Acceptance

| | Statement | Proved by |
|---|---|---|
| A | `AGENTS.md` §6 states the per-piece law and the `cd <abs> &&` pin; no `git -C` outside a blockquote in any root entry file | item 2's check + its mutant |
| B | A piped gate, an exit-echo tail and a `git -C` each produce exactly one nag naming their rule | `test_shape_guard.py` |
| C | A clean command, a `grep` for the string, and a heredoc body produce **no** nag | the negative battery |
| D | The hook returns `allow` on every path, and a mutant returning `ask` fails the suite | `test_shape_guard.py` |
| E | `shape_scan.py` reproduces the baselines: Claude 6.88 / 11.92 / 5.65 %, Zoo 19.03 / 4.45 / 3.64 % | `test_shape_scan.py` controls + a live run |
| F | `command-shape.md` carries §Nag and `rules/INDEX.md` its row | `test_rule_frontmatter.py` |
| G | `zoo_permissions_apply.py --status` reads *in sync* on both lists | the closing status run |
| H | Whole gate green | `python3 .agents/scripts/tests/run_all.py` bare, exit 0 |

## Out of scope, and why

- **A nag for `git add -A` / `worktree remove --force`.** Destructive; a `PostToolUse` nag speaks
  after the damage. They belong in a `PreToolUse` guard, and at 4 and 18 hits in 8,355 calls they
  are a risk problem, not a time problem.
- **Any nag for Zoo seats.** Zoo has no hook surface at all — the permissions guide states it
  plainly and that is why `zoo_notify.py` polls the thread store. Item 4 gives Zoo *measurement*,
  which is what makes "are they doing better" answerable; item 6 gives it a correct fence. Neither
  is a nag, and this plan does not pretend otherwise.

---

## Self-Audit (2026-09-01)

**Level: LEDGER+BLAST** — the Declared Change Set touches a rule, a hook, scripts others will
import, and more than one platform, so all three lenses run.
**Mode:** PRE-WORK. **Runtime:** inline (single model; the lenses were run in sequence, so their
agreement is NOT independent corroboration and no finding below is sorted by it).

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every path/script/rule the plan names exists on disk
             declared_change_set.py parse -> 13 entries, incomplete: []
             two-machine interpreter reachability for every command the plan runs
             lane fit: no deployable path in the set -> /smh-close-task-merge-tree is the door
             Scope Ledger precondition: ticket acceptance rows >= 2, each with an observable
             Scope Ledger: 4 NEW artefacts x acceptance row, empty cells
read:        .agents/hooks/INDEX.md · .agents/scripts/INDEX.md:18 · .agents/hooks/run-hook.sh
             .agents/scripts/tests/run_all.py:3-10,77 · acli jira workitem view SCC-369
verdict:     findings below
```

```
lens:        2 Parity + Blast
checks_run:  rule change -> citing commands + workflow_lint.py _RULE_POINTERS
             new hook -> ships ARMED (registered in settings.json)? indexed?
             new script -> .githooks/ callers + its test + scripts/INDEX.md
             SOP/usage surface -> both halves in the same commit
             twins: no cicd-/smh- sibling exists for any path in the set
             sibling worktrees: fetch, then per-tree diff --name-only origin/main...HEAD
             risk_seam: command centre returns `unclassified` by design (SCC-289) - not run as a gate
read:        .agents/scripts/workflow_lint.py:70-143 · git worktree list
             .claude/worktrees/retire-slash-cmd-updating diff (21 paths)
verdict:     findings below
```

```
lens:        3 Pre-Mortem (bounded - attaches narrative, originates nothing)
checks_run:  attached the other-machine narrative to F1; the next-reader narrative to F2/F3;
             the sibling-lands-first narrative to the landing-order section
read:        this plan's Declared Change Set and RED-first section
verdict:     clean (no unattached output)
```

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/hooks/run-hook.sh:11-13` | "NEVER name one platform's binary. Probe, in preference order, every time." | The probe that proved the nag channel registered it as `python3 <path>`. Shipping that shape exits **127 in silence** on the PC and reproduces SCC-77 — the bug that let six merges reach `main` on one sign-off. Breaks acceptance B on one of the two machines. | **HIGH** |
| `.agents/hooks/INDEX.md:3` | "MASTER here — mirrors to `.claude/hooks/` and project vendored copies via `/smh-sync-agents`" | A new hook absent from its own master index is invisible to the next reader; and the plan's stated reason for excluding `.claude/hooks/` ("does not exist") was wrong, which would invite someone to hand-edit the generated mirror. | MEDIUM |
| `.agents/scripts/INDEX.md:18` | "\| `declared_change_set.py` \| which files did the plan DECLARE it would touch …" | `shape_scan.py` was created by the plan with no `scripts/INDEX.md` row, so the one place a reader looks up "what scripts exist" would not list the measurement this whole ticket is judged by. | MEDIUM |
| SCC-369 board description (pre-fix) | `acli jira workitem view SCC-369` returned Key/Summary/Status only — **no description, no acceptance rows** | Scope Ledger precondition failed, which is a NO-GO ground on its own: a ticket with no acceptance rows makes the ledger match everything and produce a green that lies. | **HIGH — fixed during this audit** |

**All four are resolved in this same amendment**: the change set gained `.agents/hooks/INDEX.md`
and `.agents/scripts/INDEX.md`; item 3's RED-first list gained the `run-hook.sh` assertion and the
`sys.executable` rule; the `.claude/hooks/` exclusion now states the real reason; and
`jira_ticket.py describe` rendered the acceptance rows onto SCC-369 before this verdict was written.

### Observations (uncounted, no severity)

- `command-shape` is **absent** from `workflow_lint.py:70` `_RULE_POINTERS`, so no command body that
  pipes a gate is required to cite its law. Adding the row is aligned with this ticket's thesis but
  would warn across many existing command files at once — a separate, larger piece of work. Not in
  scope here, and deliberately not converted into a finding.
- `shape_scan.py`'s only caller is its own test. Precedent for an operator-invoked script with no
  code caller: `zoo_permissions_apply.py`, which is likewise absent from `scripts/INDEX.md`. Noted
  rather than raised, per the caller-count rule being falsifiable and this being intended.

### Sibling landing-order dependency

`chore/SCC-367-retire-slash-cmd-updating` (in review) overlaps on
`docs/_scc_sops_prds/workflows_testing_SOP.md`, `_artifacts/_main/INDEX.md` and the `doc-graph`
caches. **SCC-367 lands first.** Full analysis and mitigation in § Sibling lanes above.

```
Audit verdict: GO
```
