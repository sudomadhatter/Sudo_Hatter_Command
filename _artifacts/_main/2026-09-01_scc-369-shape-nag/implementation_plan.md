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
and 7,858 Bash calls, **1,933 violations of that one rule: 98.9% of every detectable violation in
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
| The nag becomes noise and gets ignored | The negative controls: a clean command must produce silence. Scope stays at three rules — measured at 98.9% of violations — and does not grow without a new measurement. |
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
| E | `shape_scan.py` reproduces the baselines: Claude 9.43 / 9.19 / 5.98 %, Zoo 19.03 / 4.45 / 3.64 % | `test_shape_scan.py` controls + a live run |
| F | `command-shape.md` carries §Nag and `rules/INDEX.md` its row | `test_rule_frontmatter.py` |
| G | `zoo_permissions_apply.py --status` reads *in sync* on both lists | the closing status run |
| H | Whole gate green | `python3 .agents/scripts/tests/run_all.py` bare, exit 0 |

## Out of scope, and why

- **A nag for `git add -A` / `worktree remove --force`.** Destructive; a `PostToolUse` nag speaks
  after the damage. They belong in a `PreToolUse` guard, and at 4 and 18 hits in 7,858 calls they
  are a risk problem, not a time problem.
- **Any nag for Zoo seats.** Zoo has no hook surface at all — the permissions guide states it
  plainly and that is why `zoo_notify.py` polls the thread store. Item 4 gives Zoo *measurement*,
  which is what makes "are they doing better" answerable; item 6 gives it a correct fence. Neither
  is a nag, and this plan does not pretend otherwise.
