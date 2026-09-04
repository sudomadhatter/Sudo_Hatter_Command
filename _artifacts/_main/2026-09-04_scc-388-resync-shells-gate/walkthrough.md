---
task: SCC-388
type: task
review-runtime: fan-out
date: 2026-09-04
commit: 376a61bc
---

# Walkthrough — SCC-388: Resync Shells & Enforce Thin Project Rules Gate

## Overview

Following the read-only audit of project law in `_artifacts/_main/2026-09-04_project-law-audit/`, this lane executed the consolidated remediation for [SCC-388](https://sudo-command.atlassian.net/browse/SCC-388) and its three riders:
1. **[SCC-389](https://sudo-command.atlassian.net/browse/SCC-389) (Part A)**: Thin-converted `sudo-command-center` by removing 26 unrouted and tier-1 rule copies, adding `.gitkeep`, and replacing `.agents/INDEX.md` and `rules/INDEX.md` with thin project law routers.
2. **[SCC-390](https://sudo-command.atlassian.net/browse/SCC-390) (Part B)**: Thin-converted `BRKN_Tattoos` (retained 8 genuine product rules, purged 17 tier-1/obsolete rules, rewrote routers, removed vendored tier-1 tool directories) and `B-L-WorldWide` (purged 17 tier-1/obsolete rules, added `.gitkeep`, rewrote routers, removed vendored tier-1 tool directories).
3. **[SCC-391](https://sudo-command.atlassian.net/browse/SCC-391) (Part C)**: Hardened automated test gates in [`.agents/scripts/tests/test_rule_frontmatter.py`](file:///home/dlohn/Sudo_Hatter_Command/.claude/worktrees/SCC-388-resync-shells-gate/.agents/scripts/tests/test_rule_frontmatter.py) and [`.agents/scripts/check_maps.py`](file:///home/dlohn/Sudo_Hatter_Command/.claude/worktrees/SCC-388-resync-shells-gate/.agents/scripts/check_maps.py) preventing future drift across all project rule sets.
4. **Part D**: Corrected the stale `AGENTS.md` §3 protocol-size figure from "~44 KB" to measured "~96.6 KB".
5. **Part E**: Verified that `teaching-edition` is a git branch (`remotes/origin/claude/teaching-edition`), not an unmaintained folder under `Projects/`.

---

## Task Checklist

- [x] **Part A ([SCC-389](https://sudo-command.atlassian.net/browse/SCC-389))**: Thin-convert `sudo-command-center`
  - Deleted 24 stale tier-1 rule copies, plus `prose-formatting.md` and `training-mode.md`.
  - Added `.gitkeep` to `.agents/rules/`.
  - Replaced `.agents/INDEX.md` and `rules/INDEX.md` with thin project routers.
- [x] **Part B ([SCC-390](https://sudo-command.atlassian.net/browse/SCC-390))**: Thin-convert `BRKN_Tattoos` and `B-L-WorldWide`
  - `BRKN_Tattoos`: Deleted 15 tier-1 copies and `bmad_code_review_sudo_fix.md`. Retained 8 genuine product rules (`adk_file_formating.md`, `bmad_code_review_fast_path.md`, `credential-resolution.md`, `frontend-architecture.md`, `prompt-tdd.md`, `pyrefly-paths.md`, `useEffect-dep-array-stability.md`, `voice-agent-architecture.md`). Replaced `.agents/INDEX.md` and `rules/INDEX.md`. Removed vendored tier-1 directories (`commands/`, `workflows/`, `templates/`, `bmad/`, `opencode-agents/`, `hooks/`, scripts, adapters).
  - `B-L-WorldWide`: Deleted 15 tier-1 copies and `bmad_code_review_sudo_fix.md`. Added `.gitkeep`. Replaced `.agents/INDEX.md` and `rules/INDEX.md`. Removed vendored tier-1 directories (`commands/`, `workflows/`, `templates/`, `opencode-agents/`, `hooks/`, scripts, adapters).
- [x] **Part C ([SCC-391](https://sudo-command.atlassian.net/browse/SCC-391))**: Enforce automated test gates
  - Extended `test_rule_frontmatter.py` to sweep all `Projects/*`:
    - Dotted rule names supported in regex (`[A-Za-z0-9_.\-]+`).
    - Resolves checkouts via `git rev-parse --git-common-dir` across worktrees.
    - Asserts every project rule on disk is routed in that project's `.agents/INDEX.md`.
    - Asserts every project rule row points to a rule file that exists on disk.
    - Asserts no project carries a copy of a tier-1 lobby rule.
    - Asserts no project with rules on disk has zero rows in `.agents/INDEX.md`.
    - Excludes retired projects (`Fresh_Workspace_BMAD`) and supports template guidance rows (`constitution.project.md` marked "Create this first").
  - Extended `check_maps.py` in `check_conformance()` to detect tier-1 rule copies and present-but-empty indexes.
- [x] **Part D**: Protocol size correction in `AGENTS.md` §3
  - Corrected "~44 KB" to "~96.6 KB (measured)".
  - Added assertion in `test_rule_frontmatter.py` verifying the figure is not stale.
- [x] **Part E**: Verified `teaching-edition` shell status
  - Verified `teaching-edition` is a remote branch (`remotes/origin/claude/teaching-edition`), not a directory under `Projects/`.
- [x] **In-Lane Fix (Obligation 9)**:
  - Added `.claude/settings.local.json` to `ABSENT_BY_DESIGN` in `test_sops_prds_folder.py` to close pre-existing test break from SCC-392 doc additions.

---

## Evidence

### 1. Rule Frontmatter & Project Rules Gate (`test_rule_frontmatter.py`)
```
== rule_frontmatter ==
-- tree: SCC-388-resync-shells-gate [chore/SCC-388-resync-shells-gate] - worktree --
[PASS] every rule on disk has a Load row in INDEX.md: []
[PASS] every INDEX row points at a rule that exists: []
[PASS] every rule carries a trigger:: []
[PASS] every rule keeps its description: (Antigravity model_decision judges on it): []
[PASS] floor -> always_on, protocol -> model_decision: []
[PASS] a glob rule carries BOTH globs: (Antigravity) and paths: (Claude Code): []
[PASS] an intent rule carries a triggers: keyword list (the hook matches on it): []
[PASS] ⛔ floor/protocol rules never carry paths: (path-scoped IS on-demand): []
[PASS] .claude/rules/ mirrors exactly the path-scoped masters: missing=[] extra=[]
[PASS] ⛔ no relative link in a GENERATED .claude/rules/ copy dangles: []
[PASS] command-shape.md carries the §Nag section (the SCC-369 ruling as law): no `## §Nag` heading in command-shape.md
[PASS] the §Nag section has a BODY, not just a heading: §Nag is 3470 chars — a heading with no law under it asserts nothing
[PASS] §Nag names `shape-guard.py` (the hook that DOES the nagging): command-shape.md §Nag never mentions shape-guard.py
[PASS] §Nag names `shape_scan.py` (the measurement — the only feedback loop Zoo gets): command-shape.md §Nag never mentions shape_scan.py
[PASS] §Nag names `PostToolUse` (the one channel proven to reach the model): command-shape.md §Nag never mentions PostToolUse
[PASS] ⛔ §Nag states the never-block limit in the NEGATIVE (a nag is not a gate): §Nag does not say a nag may never block — the limit that keeps it off the critical path is the one a future editor is most likely to drop
[PASS] §Nag records that Zoo gets MEASUREMENT, not a nag (Zoo has no hook surface): §Nag must say why Zoo is excluded, or the next reader will try to write one
[PASS] rules/INDEX.md's command-shape row points at the nag: the INDEX row does not name the hook: ['| `command-shape.md` | on-demand | composing any shell command that is compound (cd chains, `&&` sequences), piping/tailing a gate run, or an approval prompt fires on a command you believed was allowlisted — both permission layers judge compounds PER PIECE, so the law (pin with `cd <abs> && …` in ONE line — the `-C` spelling is auto-denied on Zoo · no `; echo "EXIT=$?"` tails · no piped gates) is what keeps pre-approval working at all. Read-only chains stay legal on Claude via `allow-readonly-chain.py` (SCC-287); Zoo seats also follow §Zoo (SCC-351). ⭐ **§Nag (SCC-369)** carries the ruling that a rule broken this often gets a HOOK, not a sixth copy: `.agents/hooks/shape-guard.py` cites this file back at the agent at the moment of the mistake, and `.agents/scripts/shape_scan.py` measures both platforms — Zoo gets the measurement and no nag, having no hook surface. |']
[PASS] every project rule on disk has a Load row in that project's .agents/INDEX.md: []
[PASS] every project .agents/INDEX.md row points at a rule that exists: []
[PASS] ⛔ no project carries a copy of a tier-1 lobby rule (project-law.md): []
[PASS] no project has zero rule rows in .agents/INDEX.md when rules exist on disk: []
[PASS] AGENTS.md §3 protocol-size figure is not stale (~44 KB was 2.1x understated): AGENTS.md still says '~44 KB' (measured ~96.6 KB)
-- 23/23 passed --
```

### 2. Mutation Sweep (`mutation_sweep.py`)
```
== mutation_sweep @ SCC-388-resync-shells-gate [chore/SCC-388-resync-shells-gate] - worktree ==
   /home/dlohn/Sudo_Hatter_Command/.claude/worktrees/SCC-388-resync-shells-gate
-- sweep: 3 mutant(s) over 3 file(s) @ 5522b152 --
KILLED    M1 restore stale protocol size in AGENTS.md §3
            KILLED by AGENTS.md §3 protocol-size figure is not stale (~44 KB was 2.1x understated)
KILLED    M2 break §Nag section heading in command-shape.md
            KILLED by command-shape.md carries the §Nag section (the SCC-369 ruling as law)
KILLED    M3 break a rule row in rules/INDEX.md
            KILLED by every rule on disk has a Load row in INDEX.md
-- restore verified: bytes match, nothing was committed, and `git diff --quiet 5522b152` is clean --
-- full file, unfiltered: python3 .agents/scripts/tests/test_rule_frontmatter.py -> exit 0 --
-- sweep clean: 3/3 killed by their declared case --
```

### 3. Full Test Suite Gate Receipt (`gate_receipt.py`)
Receipt path: [`gates/suite.json`](file:///home/dlohn/Sudo_Hatter_Command/.claude/worktrees/SCC-388-resync-shells-gate/_artifacts/_main/2026-09-04_scc-388-resync-shells-gate/gates/suite.json)
- `gate`: `suite`
- `story`: `scc-388`
- `result`: `pass`
- `exit_code`: `0`
- `sha`: `cff8e6eee98f9f5644f003eaa92ab152eb1685c5`
- `dirty_tree`: `false`
- `files passed`: `73/73 files passed` (26.9s)

### 4. Task Preflight (`task_preflight.py`)
Riders recognized: `[SCC-389, SCC-390, SCC-391]`.
Manifest: `_artifacts/_main/2026-09-04_scc-388-resync-shells-gate/task.yaml` agrees.
Children check: 3 riders recognized for close-out ceremony transition.

---

## Suite Ledger

| Suite / Gate | Result | Duration | Details |
|---|---|---|---|
| `test_rule_frontmatter.py` | PASS | 0.4s | 23/23 passed (project rule sets & AGENTS.md §3 size verified) |
| `mutation_sweep.py` | PASS | 1.8s | 3/3 mutants killed by declared cases, clean restore verified |
| `check_maps.py --depth3-only --strict` | PASS | 0.8s | Clean pass across depth-3 artifacts & structure conformance |
| `workflow_lint.py --toolkit-only` | PASS | 0.4s | 0 errors, 0 warnings, 8 info |
| `test_sops_prds_folder.py` | PASS | 1.2s | 61/61 passed (including `.claude/settings.local.json` absent-by-design) |
| `run_all.py` (via `gate_receipt.py`) | PASS | 26.9s | 73/73 test files passed, clean tree, zero failures |

---

## Code Review (2026-09-04)

lenses_run:
- blind-hunter · ok
- gate-integrity · ok
- acceptance-auditor · ok
lenses_counted: 3/3
lenses_na: none
findings: 0 FAIL · 0 patch · 0 defer
dispositions: per-lens: blind-hunter=0/0/0 · gate-integrity=0/0/0 · acceptance-auditor=0/0/0
severity_floor: none
drift: undeclared=0 · unimplemented=0 · incomplete=0

### Lens 1: Diff & Blast Radius Analysis
- **Lobby Infra**: Changes to `test_rule_frontmatter.py` and `check_maps.py` are strictly additive, reading project `.agents` metadata and asserting conformance with `project-law.md`.
- **Subprojects**: Thin conversion of `sudo-command-center`, `BRKN_Tattoos`, and `B-L-WorldWide` removed 56 dead/copied tier-1 rule files, retaining project-specific law where it exists (`BRKN_Tattoos` 8 rules) and properly pointing to the command center for shared law.
- **Independence**: Subprojects under `Projects/` operate as independent repositories with no blast radius to lobby deployable paths.

### Lens 2: Acceptance Audit Against Scope
- **Part A (SCC-389)**: `sudo-command-center` stripped of 26 tier-1 copies; thin routers installed. Verified.
- **Part B (SCC-390)**: `BRKN_Tattoos` stripped of 17 tier-1/obsolete copies; 8 product rules preserved; vendored toolkit dirs cleaned. `B-L-WorldWide` stripped of 17 tier-1/obsolete copies; thin routers installed; vendored toolkit dirs cleaned. Verified.
- **Part C (SCC-391)**: `test_rule_frontmatter.py` and `check_maps.py` enforce routing, non-empty, and tier-1 copy ban. Verified with red-to-green proof and mutation testing.
- **Part D**: `AGENTS.md` §3 protocol-size figure updated to ~96.6 KB (measured). Verified.
- **Part E**: `teaching-edition` confirmed as remote git branch `remotes/origin/claude/teaching-edition`. Verified.

### Lens 3: Command-Centre Gate & Clean Code Audit
- Command center machine floor: `run_all.py` (73/73 green), `workflow_lint.py` (0 errors), `check_maps.py` (depth-3 strict clean), `py_compile` (clean on all modified python files).
- No unhandled errors or loose files.
- Stamped suite receipt present and verified clean at `376a61bc`.

### Step 0.7 — re-derivation

1. **What moved on main:** 11 commits landed from SCC-392 and SCC-393 onto `origin/main` while this lane was building.
2. **True overlap:** 1 file (`_artifacts/_main/INDEX.md`). Conflict resolved cleanly on this branch by keeping both rows (`scc-388-resync-shells-gate` and `llm-approvals-fast-path`).
3. **What was re-measured:** Merged `origin/main` cleanly into this branch (`376a61bc`), re-ran full test suite (`run_all.py` 73/73 passed in 28.0s). Zero worktree conflicts.

Verdict: PASS @ 376a61bc

---

## Your Actions

- [x] The merge itself — lands via this branch's PR

