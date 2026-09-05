---
name: toolkit-installed-but-deliberately-unmaintained
description: B-L-WorldWide and BRKN_Tattoos carry a frozen July sudo toolkit on purpose — RULED not-maintained 2026-08-03; never re-file as a gap.
metadata: 
  probe: "test -e .agents/maintained-projects.txt"
  node_type: memory
  type: project
  originSessionId: 188cc8d4-fd46-4a29-ada3-f8934ab750ee
  modified: 2026-08-04T02:03:58.574Z
---

The lobby tracks 8 project gitlinks, but `.agents/maintained-projects.txt` lists only **three**:
`AGY_AVIATIONCHAT`, `Fresh_Workspace_BMAD`, `NEXgen-VR-Director`.

Two of the unlisted five are **not inert** — they have the toolkit installed and will look like a
propagation gap on any sweep:

| Project | sudo cmds | State |
|---|---|---|
| `B-L-WorldWide` | 12 | frozen at 2026-07-23, has `sudo-boot-sprint-memory` |
| `BRKN_Tattoos` | 13 | frozen at 2026-07-17, has `sudo-boot-sprint-memory` |

Their copies predate the 2026-08-02 two-doc restructure, so they still infer a review verdict from
`sprint-status.yaml`. **That is accepted.** Daniel, 2026-08-03, asked directly whether to add them:
**"no to them."**

**Why:** upkeep cost is per-project and these are not active workspaces. `maintained-projects.txt`
says it plainly — *"Never hand-loop over Projects/* — that touches repos we deliberately do not keep
current."* An installed toolkit is not evidence of intent to maintain.

**How to apply:** when a propagation/audit sweep surfaces them, report as **ruled out of scope**, not as
a finding. Adding them = two lines in `maintained-projects.txt` + `/sync-agents -Maintained`, and only
Daniel makes that call. (Separate, still open: `BRKN_Tattoos` has a gitlink with no `.gitmodules`
mapping, so `git submodule status` errors on it — a hygiene bug, not a toolkit question.)

Related: [[maintained-projects-allowlist]] · [[settled-decisions-are-not-gaps]] ·
[[platforms-empty-list-means-nowhere]]
