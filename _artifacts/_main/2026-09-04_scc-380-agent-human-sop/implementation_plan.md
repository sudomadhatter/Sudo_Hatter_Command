---
IsArtifact: true
ArtifactMetadata:
  title: SCC-380 & SCC-381 Make Agent SOP, Human Flight Manual, and Close-Out Nag
  type: implementation_plan
  date: 2026-09-04
---

# Implementation Plan: SCC-380 & SCC-381 (Agent SOP, Human Quick-Ref & Close-Out Nag)

Bifurcate and optimize the command center documentation (SCC-380) and implement an authoritative close-out nag and command cockpit card (SCC-381) to eliminate agent confusion, prevent accidental pushes to `main`, and provide immediate guidance when close-out pushes or pull requests fail.

## User Review Required

> [!IMPORTANT]
> **Close-Out Protocol Hard Enforcement**:
> 1. Agents **never push directly to `main`**. Task work lands exclusively via a GitHub Pull Request created by `/smh-close-task-merge-tree`, merged on GitHub by Mr. Hatter, and resumed via `/smh-close-task-merge-tree --after-merge <KEY>`. Story work lands on `epic/*` branches via `/cicd-close-story-merge-tree`.
> 2. The new `closeout-nag.py` PostToolUse hook will intercept any attempted push/merge to `main` or any failed push/PR, immediately outputting actionable advice via `hookSpecificOutput.additionalContext` directing the agent to [.agents/rules/git-policy.md](file:///home/dlohn/Sudo_Hatter_Command/.agents/rules/git-policy.md) and the exact `/` command.
> 3. SCC-381 is consolidated into this lane as a rider under parent SCC-380 per `work-consolidation.md` Rule 2.

## Open Questions

None — the behavior and design strictly match the operator rulings and Jira description.

## Declared Change Set
- NEW `.agents/hooks/closeout-nag.py` — PostToolUse nag for close-out procedure, failed pushes/PRs, and illegal main pushes → AC-10
- NEW `.agents/scripts/tests/test_closeout_nag.py` — unit and regression test suite for closeout-nag.py → AC-11
- EDIT `.agents/hooks/INDEX.md` — register closeout-nag.py in hooks manifest → AC-12
- EDIT `.claude/settings.json` — wire closeout-nag.py under PostToolUse hook group → AC-13
- EDIT `.agents/commands/smh-close-task-merge-tree.md` — add prominent top cockpit card explaining the 5-step close-out rule and PR protocol → AC-14
- EDIT `.agents/commands/cicd-close-story-merge-tree.md` — add cockpit card clarifying epic-branch landing → AC-15
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — document closeout-nag.py in §10 Hooks & Nags architecture → AC-16
- EDIT `docs/_scc_sops_prds/operator_workflows_quickref.md` — add closeout-nag.py to Gates vs Nags triage table → AC-17
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — add SCC-381 entry to changelog → AC-18
- NEW `_artifacts/_main/2026-09-04_scc-380-agent-human-sop/task.yaml` — lane manifest declaring parent SCC-380 and rider SCC-381 → AC-19
- NEW `_artifacts/_main/2026-09-04_scc-380-agent-human-sop/tickets/SCC-380.md` — ticket outline for SCC-380 → AC-20
- NEW `_artifacts/_main/2026-09-04_scc-380-agent-human-sop/tickets/SCC-381.md` — ticket outline for SCC-381 → AC-21

## Proposed Changes

Work is performed inside the isolated worktree `.claude/worktrees/SCC-380-agent-human-sop` on branch `chore/SCC-380-agent-human-sop`.

---

### 1. Close-Out Nag Hook

#### [NEW] [.agents/hooks/closeout-nag.py](file:///home/dlohn/Sudo_Hatter_Command/.agents/hooks/closeout-nag.py)
- Event: `PostToolUse` for `tool_name == "Bash"`.
- Trigger conditions:
  - Any `git push` command targeting `main` (e.g. `git push origin main`, `git push -u origin main`, `git push origin HEAD:main`).
  - Any `git checkout main` or `git merge` attempted onto `main`.
  - Any failed `git push` or `gh pr create` (where returncode != 0 or output contains failure keywords).
- Emission:
  Emits `hookSpecificOutput.additionalContext` explaining:
  - **Standing Law:** Agents never push directly to `main`.
  - **Task Landing:** Use `/smh-close-task-merge-tree` to open PR (`gh pr create --base main --head "$BRANCH" --fill`), hand link to Mr. Hatter, and resume with `--after-merge <KEY>`.
  - **Story Landing:** Use `/cicd-close-story-merge-tree` (lands on `epic/*`, never `main`).
  - **Read Pointers:** [.agents/rules/git-policy.md](file:///home/dlohn/Sudo_Hatter_Command/.agents/rules/git-policy.md), [workflows_testing_SOP.md](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/workflows_testing_SOP.md) §3 and §10.
- Guarantees:
  - Fails open on any parse error or exception.
  - Never blocks (`decision: "block"` or `permissionDecision` never emitted).

#### [NEW] [.agents/scripts/tests/test_closeout_nag.py](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/tests/test_closeout_nag.py)
- Comprehensive test suite modeled on `test_shape_guard.py`:
  - Positive tests: push to main, failed git push, failed gh pr create, git checkout main && merge.
  - Negative tests: normal git push to chore/claude branch, clean gh pr view/checks, grepping for push commands, heredocs, non-bash tools.
  - Invariants: `test_never_blocks`, `test_fails_open`, `test_registered_through_run_hook`, `test_hook_is_indexed`.

#### [MODIFY] [.agents/hooks/INDEX.md](file:///home/dlohn/Sudo_Hatter_Command/.agents/hooks/INDEX.md)
- Register `closeout-nag.py` in the manifest.

#### [MODIFY] [.claude/settings.json](file:///home/dlohn/Sudo_Hatter_Command/.claude/settings.json)
- Register `closeout-nag.py` under `PostToolUse` alongside `shape-guard.py`.

---

### 2. Close-Out Slash Commands Cockpit Overhaul

#### [MODIFY] [.agents/commands/smh-close-task-merge-tree.md](file:///home/dlohn/Sudo_Hatter_Command/.agents/commands/smh-close-task-merge-tree.md)
- Add a high-visibility **RAPID COCKPIT CARD** at the top:
  - Bold declaration: **AGENTS NEVER PUSH DIRECTLY TO `main`**.
  - The 5-step rapid path: Preflight → Gates → PR (`gh pr create`) & Hand-back → Operator Merges on GitHub → Resume (`--after-merge <KEY>`).
  - Troubleshooting guide: what to do if the PR check fails or push is refused.

#### [MODIFY] [.agents/commands/cicd-close-story-merge-tree.md](file:///home/dlohn/Sudo_Hatter_Command/.agents/commands/cicd-close-story-merge-tree.md)
- Add clear top note reiterating that story work lands on the **epic branch**, never `main`.

---

### 3. Documentation & SOP Integration

#### [MODIFY] [workflows_testing_SOP.md](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/workflows_testing_SOP.md)
- Add `closeout-nag.py` under §10 PostTool Nags.
- Update Agent Fast-Lookup Router at the top to direct agents to closeout procedures.

#### [MODIFY] [operator_workflows_quickref.md](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/operator_workflows_quickref.md)
- Add `closeout-nag.py` to the Gates vs. Nags triage section.

#### [MODIFY] [workflows_testing_SOP_changelog.md](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/workflows_testing_SOP_changelog.md)
- Record SCC-381 entry.

---

### 4. Manifest & Tickets

#### [NEW] `_artifacts/_main/2026-09-04_scc-380-agent-human-sop/task.yaml`
- Declares parent `SCC-380` and rider `SCC-381`.

#### [NEW] `_artifacts/_main/2026-09-04_scc-380-agent-human-sop/tickets/SCC-380.md` and `SCC-381.md`
- Fast-read outlines for Jira tracking.

---

## Verification Plan

### Automated Tests
Run bare within the worktree:
```bash
python3 .agents/scripts/tests/test_closeout_nag.py
python3 .agents/scripts/tests/test_shape_guard.py
python3 .agents/scripts/tests/test_command_surfaces.py
python3 .agents/scripts/tests/test_sops_prds_folder.py
python3 .agents/scripts/tests/test_git_hooks.py
python3 .agents/scripts/tests/test_doc_graph.py
python3 .agents/scripts/tests/test_check_links.py
python3 .agents/scripts/sop_currency.py
python3 .agents/scripts/tests/run_all.py
```

### Manual Verification
- Test `closeout-nag.py` against sample payloads (push to main, failed push, allowed branch push).
- Verify `.claude/settings.json` parses cleanly.
- Verify `task_preflight.py` accepts the manifest and rider.

## Self-Audit (2026-09-04)

- **Right-size Level:** Full Task / Infrastructure Lane (`SCC-380` + rider `SCC-381`)
- **Phases Walked:**
  - **Phase 1: Architecture & Scope:** Bifurcated human flight manual from canonical machine SOP. Verified zero Mermaid blocks in `workflows_testing_SOP.md` and added fast-lookup least-context router.
  - **Phase 2: Hook Safety & Non-Blocking Contract:** Built `closeout-nag.py` adhering to `test_never_blocks` and `test_fails_open`. Never emits `decision` or `permissionDecision`. Evaluated payload extraction on `PostToolUse`.
  - **Phase 3: Command Cockpit Cards:** Embedded prominent 5-step close-out rule and PR protocol in `/smh-close-task-merge-tree` and epic-branch landing note in `/cicd-close-story-merge-tree`.
  - **Phase 4: Multi-Door Parity:** Propagated command edits across all mirrors (`.opencode/commands/`, `.roo/commands/`, `.claude/skills/`). Verified door parity with `test_command_surfaces.py`.
  - **Phase 5: Map Freshness & Graph:** Regenerated doc graph and verified zero broken links and zero map drift.
  - **Phase 6: Full Suite Gate:** Ran `run_all.py` bare across all 76 test suites. All 76 passed.

### Findings & Disposition

| Item | File:Line | Severity | Scenario | Disposition |
|---|---|---|---|---|
| F1 | `test_command_surfaces.py` | HIGH | Mirror drift on `.opencode/commands` after command card edit | FIXED — ran sync engine to propagate command masters to mirrors |
| F2 | `check_maps.py` | HIGH | Missing session row in `_artifacts/_main/INDEX.md` | FIXED — registered `2026-09-04_scc-380-agent-human-sop/` in session table |
| F3 | `docs/migrations/auth_keys` | LOW | Gitignored secret file missing in fresh worktree | MITIGATED — ran `link-worktree-assets.py`; `check_maps.py --depth3-only --strict` confirmed 35/35 green |

**Audit verdict: GO**

