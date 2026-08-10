# SCC-78 — the Task-lane dev cycle (`/smh-quick-dev`, `/smh-self-audit`, `/smh-code-review`, `/smh-clean-code-audit`)

**Ticket:** SCC-78 · **Branch:** `chore/SCC-78-smh-task-lane-dev-cycle` · **Lane:** LOCAL (no deployable
path in the diff) · **Repo:** Sudo_Hatter_Command (the command centre)

**What shipped.** The four `smh-*` counterparts of the `cicd-*` dev loop, so command-centre Task work
has a defined way to be *built* and *reviewed* — not just closed out. The `cicd-*` family is
BMAD-paired by construction: it binds `smh-target-resolution.md` (exactly ONE project, never the
lobby) and every step assumes a story file, a sprint board, an epic branch and a status flip. Task
work has none of those and lives **in** the lobby.

---

## Task Checklist

- [x] **`/smh-self-audit`** — pre-work adversarial audit for a plan with no story file and no story ACs
  - Phase 0 substitutes a **checkable list** for story ACs, in authority order: the ticket's
    `ACCEPTANCE` block → the operator's stated intent → written and confirmed
  - Phase 1's blast radius is rebuilt for the toolkit: a command rename orphans four platform caches, a
    rule change strands every command citing it, a script change breaks a hook that fires on someone
    else's commit, a moved file leaves links that resolve to nothing and look fine
  - Adds a **sibling-lane read** (`git worktree list` + each tree's diff) — the failure mode that bit
    this very task; see Pitfalls
- [x] **`/smh-clean-code-audit`** — the command centre's machine floor
  - Ground-truthed the floor rather than copying it: **no `ruff`, no venv, no `pyrefly`, no `tsc`, no
    `npm` in this repo.** Verified by `command -v` and `python3 -m ruff --version`
  - Floor is `run_all.py` · `workflow_lint.py --toolkit-only` · `sop_currency.py` · `py_compile` ·
    `bash -n` / pwsh parse · link+anchor · **door parity**
  - Judgment half checks the conventions the SOP defines — naming law, one-door law, gates ship armed,
    every gate needs an auditable exit, both machines (`python` vs `python3`)
- [x] **`/smh-quick-dev`** — the assert-first dev cycle
  - Keeps the enterprise half: worktree → checkable list → plan → `/smh-self-audit` → literal
    `approved` → **RED before any edit** → GREEN → review gate → STOP
  - The RED tier table is the load-bearing idea: a script gets a real test; a *doc or folder move* gets
    a machine-verifiable assertion written first (link resolves, INDEX matches disk, gate rejects, grep
    returns zero)
- [x] **`/smh-code-review`** — the Task-lane verdict, and it **calls `/smh-clean-code-audit` at Step
      3.5** (the operator's explicit ask on this ticket)
  - Blind hunt on the diff FIRST, plan/walkthrough only after · acceptance audit · the gate · Step 3.5
    · one `Verdict:` line into the walkthrough
- [x] `.agents/commands/INDEX.md` — new **Task dev lane** group row
- [x] `_my_resources/_quick_reference/sudo_workflows_testing.md` — new §3 subsection with the four
      commands, the lane-choice rule, and a flow diagram
- [x] All 16 platform doors generated via `sync-agents.ps1 -NoGlobals` (4 commands × 4 platforms)

---

## Evidence

**Measured at:** `c0e0f44` on `chore/SCC-78-smh-task-lane-dev-cycle` — the sha every gate result below
was measured on, and the last commit containing code. The only later commit on this branch is this
artifact update, which per the lane's own rule does not invalidate the evidence. No receipts on this
lane: `gate_receipt.py` resolves a BMAD board and exits in the command
centre (`die("no project resolved")`, `wf_common.resolve_project_root`). That limit is now written into
`/smh-code-review` Step 3 rather than left to be rediscovered.

| Acceptance item (from the ticket) | Proving assertion | Result |
|---|---|---|
| Both commands exist in `.agents/commands/` with `smh-` prefix, hyphens only (SCC-63) | `workflow_lint.py --toolkit-only` naming-law check | **PASS** — 0 errors |
| Neither binds `smh-target-resolution.md`; both act on the repo you are standing in | lint's `_RULE_POINTERS` target-resolving probe does not fire on any of the four; each Step 0 resolves `REPO` from `git rev-parse --show-toplevel` | **PASS** |
| Neither requires a story file, sprint board, epic branch, or status flip | no `sprint-status.yaml`, no `epic/`, no `review`→`done` in any of the four bodies | **PASS** |
| Generated launcher skills for Claude + Codex per SCC-66; sync-agents propagates | `test_command_surfaces.py` — 13/13 | **PASS** (was RED before the sync — see below) |
| SOP documents both in the command menu | new §3 subsection + `Start here` row; `sop_currency.py` staged in the same commit | **PASS** |
| `workflow_lint.py --toolkit-only` passes; `run_all` stays green | see below | **PASS** |
| *(added by the operator)* `/smh-code-review` exists, adjusted for the command centre | `.agents/commands/smh-code-review.md` | **PASS** |
| *(added by the operator)* `/cicd-clean-code-audit` is called by the review command; duplicated and adjusted to the SOP's standards | `/smh-code-review` Step 3.5 invokes `/smh-clean-code-audit`, whose standard is the SOP + `code-standards.md` | **PASS** |

### RED → GREEN (door parity)

The one genuinely testable behaviour in this task, and it ran in the right order. **RED**, before the
sync — the four commands existed with no launchers:

```
[FAIL] every claude/codex-eligible command has its skill door: 8 missing:
       ['smh-clean-code-audit (codex)', 'smh-clean-code-audit (claude)', 'smh-code-review (codex)',
        'smh-code-review (claude)', 'smh-quick-dev (codex)', 'smh-quick-dev (claude)']
[FAIL] every opencode-eligible command has its mirror: 4 missing:
       ['smh-clean-code-audit', 'smh-code-review', 'smh-quick-dev', 'smh-self-audit']
[FAIL] every antigravity-eligible command has its workflow mirror: 4 missing:
       ['smh-clean-code-audit', 'smh-code-review', 'smh-quick-dev', 'smh-self-audit']
-- 10/13 passed --
```

**GREEN**, after `sync-agents.ps1 -NoGlobals`:

```
sync-agents: antigravity workflow mirror -> 30 commands in .agents/workflows/
sync-agents: launcher skills -> 17 generated in .agents/skills/ (hand-authored skills untouched)
sync-agents: .claude\skills     -> 51 skill dirs (3 claude-only launcher(s))
sync-agents: .opencode\commands -> 52 cmds

11/11 files passed
```

Door census, verified per command per platform — 16/16 present:

```
smh-self-audit         claude=Y agents=Y opencode=Y workflow=Y
smh-quick-dev          claude=Y agents=Y opencode=Y workflow=Y
smh-code-review        claude=Y agents=Y opencode=Y workflow=Y
smh-clean-code-audit   claude=Y agents=Y opencode=Y workflow=Y
```

### Gate

```
python3 .agents/scripts/tests/run_all.py            -> 11/11 files passed
python3 .agents/scripts/workflow_lint.py --toolkit-only
                                                    -> 0 error(s), 2 warning(s), 8 info
```

Both warnings are **pre-existing and unrelated** to this diff — `cicd-merge-epic-workingtrees.md`
missing a `git-policy` pointer, and the `cicd-code-review-AP` twin timestamp. They were present on
`main` at `9a6a026` before this branch was cut. The 8 infos are the testarch BOMs, also pre-existing.

---

## Pitfalls

- **`gate_receipt.py` cannot run in the command centre.** It calls `wf.resolve_project_root`, which
  needs a directory holding the BMAD board file and otherwise calls `die()`. Copying
  `/cicd-code-review`'s receipt contract into the Task lane would have produced a command that fails on
  its own gate step. Written up as a stated limit in `/smh-code-review` Step 3.
- **`/cicd-clean-code-audit` run in the lobby is a floor made of holes.** Every one of its four checks
  (`ruff`, `eslint`, `pyrefly`, `tsc`) is absent here, so all four report SKIPPED — which under that
  command's own rule means nothing was checked, while reading as a pass. This is the concrete reason
  the duplicate the operator asked for is not cosmetic.
- **SCC-74 landed mid-task, and it moved the SOP out from under two of these commands.** It renamed the
  SOP PRD to `docs/_scc_sops_prds/workflows_testing_SOP.md` and repointed `sop_currency.SOP_DOC` with
  it. `/smh-clean-code-audit` and `/smh-code-review` both named the **old** path as the standard they
  load — so on `main` they would have instructed the agent to read a file that does not exist. Caught
  by the post-merge audit, repointed in `467367d`. `chore/SCC-77-main-write-gate` is still live and
  also edits the SOP doc.
- **My own two files used the wrong artifact path form** (`_main/<date>-<slug>` instead of
  `<date>_<slug>`), caught by re-reading against `artifacts-always-first` and the real folder names on
  disk. Fixed before commit; the sync was re-run because the opencode mirrors are verbatim copies.

---

## Self-Audit (2026-08-10)

**Run retroactively, and that is itself finding SA-1.** `/smh-self-audit` is a **pre-work** gate by
contract — its Step 0 says *"No plan file yet → STOP"*, and there is no `implementation_plan.md` for
SCC-78 because the plan gate was skipped. The audit was therefore run against **the ticket's SCOPE +
ACCEPTANCE block as the plan** (which Phase 0 already names as the authority for the checkable list)
and against the shipped change set. Per `artifacts-always-first` §7 the section belongs in the plan; with
no plan it lands here, above the review, which is the deviation this note records.

**Right-size: Full.** The change set touches the command menu, the door law, four platform surfaces and
the SOP PRD — three of the Phase 0 "Full" triggers.

**Phases walked**

- **Phase 0 — scope + checkable list.** 25 files. Acceptance recovered from the ticket, including the
  two items added by the operator mid-flight (`/smh-code-review`; duplicate and repoint the clean-code
  audit). Both traced to shipped work. No plan step without an acceptance item.
- **Phase 1 — blast radius.** The overlap sweep is where the value was. Against post-SCC-74 `main`: my
  25 files vs main's 53, **true intersection = 2** (`.agents/.sync-manifest.json`,
  `.agents/commands/INDEX.md`). `git merge-tree` predicted exactly one conflict, in the generated
  manifest. Confirmed against the real merge.
- **Phase 2 — over-engineering.** One tripwire fired and was **justified, not cut**: clone-and-tweak
  across families. `/smh-clean-code-audit` and `/smh-code-review` duplicate their `cicd-*` twins. The
  justification is mechanical, not stylistic — see CR-2 below.
- **Phase 3 — pre-mortem.** The "a sibling lane lands first" row is what caught SA-2. The "four platform
  caches" row is what caught SA-3.

**Findings**

| # | file:line | Severity | Failure scenario | Disposition |
|---|---|---|---|---|
| SA-1 | *(process)* | CONCERNS | The lane's own plan-first gate was skipped, so this audit ran retroactively against the ticket instead of a plan. A retroactive audit cannot change a decision that is already built. | accepted — recorded, not hidden |
| SA-2 | `smh-clean-code-audit.md:20`, `smh-code-review.md:139` | **FAIL** | Both named the SOP by its **retired** pre-SCC-74 location under `_my_resources/_quick_reference/` (path deliberately not written out here — it no longer resolves). SCC-74 moved it. On `main` both commands would tell the agent to read a file that does not exist — and it is the *standard-defining* reference, so the audit half silently loses its standard. | **applied** — repointed to `docs/_scc_sops_prds/workflows_testing_SOP.md` in `467367d` |
| SA-3 | `sync-agents.ps1:894` | **FAIL (pre-existing, widened here)** | Antigravity's **global** cache receives the full command body, not the thin launcher. 9 files now exceed the 12k cap there and are silently dropped by Antigravity — 4 of them mine. | **deferred** — needs its own ticket; see Your Actions #1 |
| SA-4 | walkthrough | CONCERNS | The walkthrough still cited the pre-SCC-74 SOP path. | applied |
| SA-5 | SOP §5 | CONCERNS | Says the suite is "202 checks across 7 files"; it is **12 files** today. Out of this lane's scope. | deferred |

```
Audit verdict: GO   (after SA-2 was applied; GO was NOT available before it)
```

---

## Code Review (2026-08-10)

```
Verdict: CONCERNS @ 467367d
```

Suite evidence measured on `467367d` — the same sha as HEAD at review time, post-merge. No receipts:
`gate_receipt.py` resolves a BMAD board and exits in the command centre, so the contract here is pasted
output plus this recorded sha (the limit is stated in `/smh-code-review` Step 3).

**Scope** — 25 files on `chore/SCC-78-smh-task-lane-dev-cycle`, plus the absorbed SCC-74 merge.
**Method** — diff hunted before the plan and walkthrough were opened; acceptance audited against the
ticket's ACCEPTANCE block; the command-centre gate; `/smh-clean-code-audit` at Step 3.5.

**Findings**

| # | file:line | Severity | Category | Finding | Disposition |
|---|---|---|---|---|---|
| CR-1 | `smh-clean-code-audit.md:20`, `smh-code-review.md:139` | FAIL | dead-reference | see SA-2 — the standard each command loads had moved | applied |
| CR-2 | *(design)* | PASS-with-note | cross-family duplicate | The duplication the operator asked for is justified **mechanically**: `ruff`, `eslint`, `pyrefly` and `tsc` are absent here (`command -v` returns nothing; no venv, no `package.json`), so `/cicd-clean-code-audit` yields four SKIPPED checks — under its own rule, nothing checked, presenting as a pass. Named as a deliberate duplicate in both bodies. | kept |
| CR-3 | `sync-agents.ps1:894` | FAIL (pre-existing) | door-parity | see SA-3 — repo-local mirror emits a 1,113 B launcher; the global cache gets the 13,042 B body | deferred |
| CR-4 | *(tooling)* | CONCERNS | gate-has-no-tool | Both new commands mandate a "link + anchor" check with **no implementation behind it**. Written ad-hoc for this review; the first cut produced 15 false positives out of 16 by reading `<name>` and `*.md` placeholders as real paths. A gate defined only in prose is one an agent will improvise or skip. | deferred — see Your Actions #2 |
| CR-5 | *(process)* | CONCERNS | evidence-order | The first gate run of this session executed in the **main checkout**, not the worktree, because `cwd` reset after a failed command. It produced a clean-looking but meaningless main-vs-main result. Caught by re-deriving branch state with explicit `git -C`. This is exactly what Step 0's "echo from command output, never from belief" exists to prevent — the discipline held, the habit did not. | applied — every later measurement uses `git -C <worktree>` |

**Gate**

| Check | Result |
|---|---|
| `run_all.py` | **12/12 files passed** (includes SCC-74's new `test_sops_prds_folder.py`) |
| `workflow_lint.py --toolkit-only` | **0 errors**, 2 warnings, 8 info — all pre-existing on `main` |
| Link + anchor (my changed docs) | **53 real references, 0 dead** (15 placeholders skipped) |
| Door parity (repo-local) | **16/16** — 4 commands × 4 platforms |
| opencode mirrors vs masters | in sync, all 4 |
| Antigravity global cache | ⛔ **FAIL** — see CR-3 |
| SOP currency | satisfied — the SOP moved with the surface in the same commit |
| Acceptance items | 8/8 evidenced, including the operator's two mid-flight additions |

**Independent validation worth recording:** SCC-74's new `test_sops_prds_folder.py` checks that every
command reference inside the SOP folder resolves (T4) and that the folder has no dead relative links
(T3). My new SOP section passed both **without being written for them** — an independent gate, authored
by another lane, confirming this lane's doc edit.

### Clean-Code Gate — CONCERNS

**Machine floor**

```
run_all.py        : PASS  — 12/12 files passed
workflow_lint     : PASS  — 0 error(s), 2 warning(s), 8 info   (warnings pre-existing on main)
sop_currency      : PASS  — SOP moved with the surface
py_compile        : n/a   — no .py in this diff
link + anchor     : PASS  — 53 refs, 0 dead
door parity       : PASS repo-local (16/16) · FAIL global cache (CR-3)
lint / types      : not applicable to this repo (no venv, no ruff, no tsc)
```

No secrets, no debug output, no commented-out code, no bare `except:`, no bare `python` in an operator-
typed command. Verdict held at **CONCERNS** by CR-3, CR-4 and CR-5; nothing blocks the merge.

---

## Your Actions

1. **⛔ File a ticket for the Antigravity global-cache bug (CR-3 / SA-3).** `sync-agents.ps1` emits a
   thin launcher into `.agents/workflows/` for any command over 11.5 KB (line 526) — but the machine-
   global target at line 894 copies the **raw command body**. Nine commands now sit over Antigravity's
   12k cap in `~/.gemini/antigravity/global_workflows` and are silently dropped there: mine ×4, plus
   `cicd-close-workingtree`, `cicd-code-review`, `cicd-dev-story-tests`, `cicd-update-sprint-memory`,
   `smh-close-task-merge-tree`. This is the **same failure class as SCC-56** — Antigravity missing
   commands, silently. The fix looks small: publish the global Antigravity cache from
   `.agents/workflows/` (which already holds the launchers) instead of `.agents/commands/`. Not done
   here — it changes a usage surface and needs its own RED test. **I did not create the ticket; say the
   word and I will.**
2. **Consider making the link + anchor check a real script (CR-4).** Two new commands mandate it and
   nothing implements it. `.agents/scripts/` is the right home, `<placeholder>`/glob skipping is the
   one non-obvious requirement, and `run_all.py` is the natural gate.
3. **Fix the SOP §5 count (SA-5)** — "202 checks across 7 files" is now 12 files. One line; left alone
   because SCC-74 owns that sweep.
4. **`/smh-quick-dev` is still unexercised.** You said the next task audits it — worth noting that its
   Step 1.5 plan gate is the one control that would have prevented SA-1 here.
5. **Close-out is yours** — `/smh-close-task-merge-tree`, and typing it is the merge sign-off.
