# Update `/cicd-live-testing-team` to Track & Persist Running Bug List in Project Artifacts

## Overview
During live testing sessions (e.g. AVCH-97 TESTPILOT runs or cross-project testing), the operator reports observations and symptoms conversationally across turns. We need `/cicd-live-testing-team` to systematically:
1. Maintain the running bug list directly inside the **conversation chat stream** on every turn so the operator always has the current live state without opening files.
2. Persist and update that running bug list in the active project's own chat artifacts at `PROJECT_ROOT/_artifacts/debugging/<YYYY-MM-DD>_live-testing/bug-list.md` (e.g., [`Projects/AGY_AVIATIONCHAT/_artifacts/debugging/...`](file:///home/dlohn/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/_artifacts/debugging/) for AviationChat, or the corresponding project for others).
3. Ensure detailed recon bug docs (`<n>-<slug>.md`) and Playwright evidence link directly to and from this central session `bug-list.md`.

## User Review Required
> [!IMPORTANT]
> - This update enhances `.agents/commands/cicd-live-testing-team.md` Steps 0, 2, 3, and 4.
> - Per `sop-currency.md`, `docs/_scc_sops_prds/workflows_testing_SOP.md` is updated in the same change to reflect this protocol.
> - Following the edit, `pwsh .agents/scripts/sync-agents.ps1` propagates the updated launcher and command mirrors to all agent platforms.

## Proposed Changes

### Command Center Master Toolkit

#### [MODIFY] [`.agents/commands/cicd-live-testing-team.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/commands/cicd-live-testing-team.md)
- **Step 0 / Step 1**: Specify initialization of the session artifact folder and master running list:  
  `PROJECT_ROOT/_artifacts/debugging/<YYYY-MM-DD>_live-testing/bug-list.md`  
  (dynamically resolved to the target project's `_artifacts/`, never the lobby root).
- **Step 2 (The co-pilot loop)**: Add explicit rule:
  - Whenever a finding, symptom, or bug is reported or captured:
    1. **In-Chat**: Print/update the running bug list markdown table in the conversation chat message.
    2. **In-Artifact**: Persist the update to `PROJECT_ROOT/_artifacts/debugging/<YYYY-MM-DD>_live-testing/bug-list.md`.
    3. Monotonically number each item (`Finding 1`, `Finding 2`, etc.) with status (`Reported`, `Diagnosing`, `Triaged`, `Fixed`).
- **Step 3 (Recon bug docs)**: Clarify that detailed individual bug docs (`<n>-<slug>.md`) and Playwright evidence files sit alongside and link to/from `bug-list.md`.
- **Step 4 (Close out)**: Ensure `bug-list.md` is finalized, linked in `PROJECT_ROOT/_artifacts/debugging/INDEX.md` and `PROJECT_ROOT/_artifacts/INDEX.md`.

---

### Procedural Documentation (PRD/SOP)

#### [MODIFY] [`docs/_scc_sops_prds/workflows_testing_SOP.md`](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/workflows_testing_SOP.md)
- Update the `/cicd-live-testing-team` entry in §3 and §12 to state that the command maintains a dual in-chat and project-artifact running bug list (`bug-list.md`).

---

## Verification Plan

### Automated Tests
- Run `python3 .agents/scripts/tests/run_all.py` to confirm all enforcement suites (rule frontmatter, map check, memory store) pass.
- Run `pwsh .agents/scripts/sync-agents.ps1` to verify clean mirror synchronization.

### Manual Verification
- Verify `PROJECT_ROOT/_artifacts/debugging/2026-09-07_live-testing/bug-list.md` in AviationChat accurately tracks the current 3 findings.
- Confirm `bug-list.md` is rendered in this conversation chat stream.

