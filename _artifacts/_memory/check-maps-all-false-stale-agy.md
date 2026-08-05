---
name: check-maps-all-false-stale-agy
description: "check_maps.py --all falsely reports AGY's AUTO block STALE; the fan-out freshness regen ignores _bmad/_my_resources only if you pass them."
metadata: 
  node_type: memory
  type: project
  originSessionId: 36e93b31-9d8e-4b70-b909-cb5dda553460
---

`python .agents/scripts/check_maps.py --all` (the `/1_update-maps` fan-out) reports **AGY_AVIATIONCHAT's AUTO block as STALE even when the map is current**. Cause: the freshness check regenerates the map in memory with a *default* ignore set that does NOT include AGY's documented `_bmad,_my_resources`, so the `_bmad/` and `_my_resources/` subtrees (e.g. `_my_resources/PRPs_Personal/Voice Agents`, `_my_resources/_docs/audits`) show as "on disk but not in map."

**Verify before regenerating:** re-lint that one workspace with its documented ignore —
`python .agents/scripts/check_maps.py --root Projects/AGY_AVIATIONCHAT --ignore _bmad,_my_resources` → if it's clean, the `--all` STALE is a false positive. Confirm independently by re-running the generator (`--ignore _bmad,_my_resources --mode content`) and diffing: identical output = current.

**Why:** the `--all` fan-out doesn't read each map's per-workspace documented `--ignore` (it lives in the map header / `mode=content` sentinel); it applies one default. AGY is the only conformant project that needs the extra `_bmad`.

**How to apply:** during `/1_update-maps`, treat an AGY-only AUTO STALE in the `--all` report with suspicion — re-lint with `--ignore _bmad,_my_resources` before spending a regen+commit on it. A real tool fix would have `--all` honor each map's documented ignore. See [[autopilot-engine-is-project-local]] for the "lobby tool, per-project reality" pattern.
