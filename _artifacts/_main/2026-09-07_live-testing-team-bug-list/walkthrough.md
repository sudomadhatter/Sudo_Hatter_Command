# Walkthrough — Live Testing Running Bug List & Jira Traceability Protocol

## Overview
Updated `/cicd-live-testing-team` and `workflows_testing_SOP.md` so that during live testing sessions across any workspace, the agent maintains a live running bug list in two synchronized surfaces:
1. **In the conversation chat stream**: Printed and updated every turn so the operator has the live status immediately in view without opening files.
2. **In the active project's own artifact store**: Persisted to `PROJECT_ROOT/_artifacts/debugging/<YYYY-MM-DD>_live-testing/bug-list.md`.
3. **In Jira Ticket Minting**: When minting or flagging tickets on the Jira board, the running `bug-list.md` path/URI and captured Playwright evidence are explicitly linked in the ticket description.

## Task Checklist
- [x] Update [`.agents/commands/cicd-live-testing-team.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/commands/cicd-live-testing-team.md) Steps 0, 2, 3, 3.5, 4.
- [x] Update [`docs/_scc_sops_prds/workflows_testing_SOP.md`](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/workflows_testing_SOP.md) §3 and §12.
- [x] Run `pwsh .agents/scripts/sync-agents.ps1` to mirror command to Claude Code, OpenCode, Codex, Antigravity, and Zoo Code.
- [x] Update [`_artifacts/_main/INDEX.md`](file:///home/dlohn/Sudo_Hatter_Command/_artifacts/_main/INDEX.md) and [`_artifacts/INDEX.md`](file:///home/dlohn/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/_artifacts/INDEX.md).
- [x] Verify full test suite: `python3 .agents/scripts/tests/run_all.py --on-main` passed 82/82 files.

## Evidence
- **Test Suite Results**: `82/82 files passed` on `run_all.py --on-main`.
- **Sync Output**: `sync-agents: .opencode\commands -> 61 cmds`, `sync-agents: .claude\skills -> 70 skill dirs`, `sync-agents: zoo surfaces -> 52 launchers`.
- **AviationChat Initial Ledger**: [`Projects/AGY_AVIATIONCHAT/_artifacts/debugging/2026-09-07_live-testing/bug-list.md`](file:///home/dlohn/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/_artifacts/debugging/2026-09-07_live-testing/bug-list.md).

## Your Actions
None required for this command update. The running bug list for AviationChat is stationed below and ready for when local testing resumes.
