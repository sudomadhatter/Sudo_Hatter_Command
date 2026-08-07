# Diagrams & Guides — Index

Reference guides and system diagrams for the Sudo_Hatter_Command home base.

## Guides
- [gitnexus-usage-guide.md](system/gitnexus-usage-guide.md) — how to use the GitNexus code‑knowledge‑graph (ask‑me‑in‑English → I query the graph: impact / context / trace / detect_changes), plus re‑index chore, limits, and the license tripwire.

## System
- [system/complete-system-overview.md](system/complete-system-overview.md) — full system overview.
- [system/updated_folder_file_structure_diagram.md](system/updated_folder_file_structure_diagram.md) — current folder/file structure diagram.
- [system/git_walkthrough_settings.md](system/git_walkthrough_settings.md) — git walkthrough + settings.
- [system/autopilot_bmad_dev_loop.md](system/autopilot_bmad_dev_loop.md) — the `/autopilot_claude` autonomous dev+QA pipeline: four-stage relay, two-session continuity, resilience + hard-stop gate, and the concurrency model (run many stories at once). Mermaid throughout.
- [system/jira_integration_guide.md](system/jira_integration_guide.md) — **Jira: how work becomes an auditable record** (set up 2026-08-07). The two-channel model (why running out of tokens never stops production), the BMAD-number↔Jira-key join, the full story lifecycle, branch/commit conventions, Smart Commits, the `commit-msg` gate and its two modes, the honest enforcement picture (GitHub Free = alarm, not lock), `acli` cheat-sheet, status mapping incl. `Deferred` + `descoped`, token handling, and a live-vs-not-built ledger. Seven mermaid diagrams.
- [workflows_tea_testing/sudo_workflows_testing.md](workflows_tea_testing/sudo_workflows_testing.md) — **THE quick reference** (rewritten 2026-07-14, post-rename): the whole dev system on one page — the lifecycle map, every human-lane `/` command by lane (story loop ①②③, shipping via `/sudo-push-e2e` + the `/sudo-e2e` gate, `/sudo-live-testing-team` debugging, autopilot launchers, toolkit upkeep), the test gate + verdicts, the P0–P3 risk matrix + L1–L4 pyramid explained for learning, TEA tool cheat-sheet, and the security/error team overview. Two mermaid diagrams.
- [workflows_tea_testing/tea_deep_reference.md](workflows_tea_testing/tea_deep_reference.md) — the deep archive the quick reference was carved from (2026-07-14): full command call-graphs, the TEA method curriculum, Epic-8 anchor index, the 42-fragment library, and the incident lane's headless E2E dispatch details (incl. the apostrophe-parse lesson). Header carries the old→new command-name map.
- [workflows_tea_testing/tea_testing_guide.md](workflows_tea_testing/tea_testing_guide.md) — the deep TEA reference: BMAD Test Architect agents, ATDD red→green contract, test levels/priorities matrix, NFR + trace + gate mechanics.
- [workflows_tea_testing/tdad_stack_install_guide.md](workflows_tea_testing/tdad_stack_install_guide.md) — install/setup guide for the TDAD (test-driven agentic dev) stack.
