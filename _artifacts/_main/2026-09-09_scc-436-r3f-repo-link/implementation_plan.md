# Add Explicit pmndrs/react-three-fiber Repo Links to /smh-designer and visual-fx-3d

**Ticket:** SCC-436 (Task under Epic SCC-33)  
**Lane:** `chore/SCC-436-r3f-repo-link`  
**Date:** 2026-09-09  

## Goal
Add direct, clickable GitHub repository links to `https://github.com/pmndrs/react-three-fiber` and `@react-three/drei` across `/smh-designer`, `visual-fx-3d`, and the frontend UI design guide.

## Proposed Changes
- [MODIFY] `.agents/commands/smh-designer.md`: Add direct GitHub link `https://github.com/pmndrs/react-three-fiber` in Pillar 4 and in Capabilities Menu `[3D]`.
- [MODIFY] `.agents/skills/visual-fx-3d/SKILL.md`: Add direct GitHub links for `pmndrs/react-three-fiber` and `pmndrs/drei` in the overview and installation sections.
- [MODIFY] `docs/_scc_sops_prds/frontend_UI_design_guide.md`: Ensure direct GitHub links are embedded in Pillar 4 and Section 4.B.
- [SYNC] Run `sync-agents.ps1`.
- [TEST] Run `test_command_surfaces.py`, `test_permission_parity.py`, `check_maps.py`.
