# Diagrams & Guides — Index

Reference guides and system diagrams for the Sudo_Hatter_Command home base.

## Guides
- [gitnexus-usage-guide.md](system/gitnexus-usage-guide.md) — how to use the GitNexus code‑knowledge‑graph (ask‑me‑in‑English → I query the graph: impact / context / trace / detect_changes), plus re‑index chore, limits, and the license tripwire.

## System
- [system/complete-system-overview.md](system/complete-system-overview.md) — full system overview.
- [system/updated_folder_file_structure_diagram.md](system/updated_folder_file_structure_diagram.md) — current folder/file structure diagram.
- [system/git_walkthrough_settings.md](system/git_walkthrough_settings.md) — git walkthrough + settings.
- [system/autopilot_bmad_dev_loop.md](system/autopilot_bmad_dev_loop.md) — the `/autopilot_claude` autonomous dev+QA pipeline: four-stage relay, two-session continuity, resilience + hard-stop gate, and the concurrency model (run many stories at once). Mermaid throughout.
- [workflows_tea_testing/sudo_workflows_testing.md](workflows_tea_testing/sudo_workflows_testing.md) — the TEA-gated `sudo-` **human-lane** dev flow: the per-story command sequence (boot → write-story-tests → dev-story-tests → code-review+gate → update-sprint-memory), where each BMAD TEA agent fires, the opt-in test gate, and the L1–L4 testing pyramid. Also covers the **incident lane's headless E2E dispatch** (§10) — when to fire a real `repository_dispatch` drill vs. the interactive `/sudo-incident-response` runbook drill, how to ask for it, and the 2026-07-14 apostrophe-parse lesson. Companion to the autopilot (`_AP`) loop above. Mermaid throughout.
- [workflows_tea_testing/tea_testing_guide.md](workflows_tea_testing/tea_testing_guide.md) — the deep TEA reference: BMAD Test Architect agents, ATDD red→green contract, test levels/priorities matrix, NFR + trace + gate mechanics.
- [workflows_tea_testing/tdad_stack_install_guide.md](workflows_tea_testing/tdad_stack_install_guide.md) — install/setup guide for the TDAD (test-driven agentic dev) stack.
