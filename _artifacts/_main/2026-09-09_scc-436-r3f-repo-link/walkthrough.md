# Walkthrough — SCC-436: Full Poimandres (pmndrs) 3D Toolset & Component Catalog Integration

**Ticket:** SCC-436 (Task under Epic SCC-33)  
**Branch:** `chore/SCC-436-r3f-repo-link`  
**Worktree:** `/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/SCC-436-r3f-repo-link`  
**Date:** 2026-09-09  

---

## Overview

Expands Caterpillar's design engineering toolbox from narrow optical glass snippets to the complete **Poimandres (`pmndrs`)** 3D ecosystem. Equips [`.agents/skills/visual-fx-3d/`](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/visual-fx-3d/SKILL.md) with a comprehensive component encyclopedia ([`CATALOG.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/visual-fx-3d/CATALOG.md)) and working production component recipes ([`RECIPES.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/visual-fx-3d/RECIPES.md)) covering all 8 major domains and 100+ components across React Three Fiber, Drei, Postprocessing, Rapier physics, and Leva live tweak dials. Adds explicit clickable links to [`pmndrs/react-three-fiber`](https://github.com/pmndrs/react-three-fiber), [`pmndrs/drei`](https://github.com/pmndrs/drei), [`pmndrs/postprocessing`](https://github.com/pmndrs/postprocessing), and [`pmndrs/react-three-rapier`](https://github.com/pmndrs/react-three-rapier) across the `/smh-designer` command and the house frontend UI design guide.

---

## Task Checklist

- [x] **Authored Poimandres Tool Catalog (`CATALOG.md`):** Complete encyclopedia of 100+ components across 8 domains (Core Canvas, Staging/HDRIs, Camera/Scroll Controls, Advanced Materials, Spatial HTML, glTF pipeline, Post-processing, Rapier physics).
- [x] **Authored Production Recipes (`RECIPES.md`):** Copy-pasteable component examples for each tool category (Scroll-driven storytelling, HDRI product staging, VisionOS optical glass, spatial HTML buttons, cinematic post-processing, physics collisions, live tweak GUI).
- [x] **Updated `visual-fx-3d/SKILL.md`:** Embedded direct repo links and pointers to `CATALOG.md` and `RECIPES.md`.
- [x] **Updated `/smh-designer` Command:** Added direct repo link `https://github.com/pmndrs/react-three-fiber` in Pillar 4 and Capabilities Menu `[3D]`.
- [x] **Updated `frontend_UI_design_guide.md`:** Synchronized Pillar 4, Section 4.B, and Section 7 with the full Poimandres suite.
- [x] **Synchronized Agent Mirrors:** Ran `pwsh .agents/scripts/sync-agents.ps1` to propagate to `.claude/`, `.opencode/`, etc.
- [x] **Verified Automated Test Suites:** `check_maps.py`, `test_command_surfaces.py`, `test_permission_parity.py`.

---

## Evidence

### 1. New Artifacts & Documentation
- **`CATALOG.md` in `visual-fx-3d`:** 8 domains, package directory, props tables, and import paths.
- **`RECIPES.md` in `visual-fx-3d`:** 8 complete runnable component examples.
- **Direct GitHub Repo Links:**
  - [`pmndrs/react-three-fiber`](https://github.com/pmndrs/react-three-fiber)
  - [`pmndrs/drei`](https://github.com/pmndrs/drei)
  - [`pmndrs/postprocessing`](https://github.com/pmndrs/postprocessing)
  - [`pmndrs/react-three-rapier`](https://github.com/pmndrs/react-three-rapier)

### 2. Multi-Platform Propagation (`sync-agents.ps1`)
```
sync-agents: master=.agents
sync-agents: target=.claude/worktrees/SCC-436-r3f-repo-link (lobby=True)
sync-agents: launcher skills -> 26 generated
sync-agents: .claude/skills -> 69 skill dirs
sync-agents: .opencode/commands -> 60 cmds
sync-agents: done.
```

---

## Suite Ledger

| Test Suite | Command | Result |
|---|---|---|
| Command Surfaces | `python3 .agents/scripts/tests/test_command_surfaces.py` | PASS |
| Permission Parity | `python3 .agents/scripts/tests/test_permission_parity.py` | PASS |
| Map & Link Integrity | `python3 .agents/scripts/check_maps.py` | PASS |

---

## Your Actions

- None (all changes are self-contained documentation, catalog, and skill tooling).

