---
name: repo-local-enforcement-never-centralizes
description: Git hooks, jira.conf, and BMAD tomls live in the repo they gate — centralizing them disarms them; a thin conversion that strips them deletes enforcement, not duplication.
metadata:
  probe: "test -e .agents/jira.conf"
  type: project
---

Three file classes are permanently **repo-local**, exempt from the thin-project model
([[thin-projects-center-owns-workflow-law]]):

| File | Why it cannot move |
|---|---|
| `.githooks/*` + `.agents/scripts/git-hooks/*` | **Git runs hooks in the repo they gate.** A hook at the center never fires for a commit in a project. Carries the armed Jira commit gate + tracked `JIRA-ENFORCE`. |
| `.agents/jira.conf` | **Project identity** — names the Jira key this repo answers to (AGY→`AVCH`, lobby→`SCC`). One shared copy makes every gate reject its own tickets and accept another project's, while reading perfectly plausibly. |
| `_bmad/custom/*.toml` | BMAD loads them from inside the project; no center path survives both sides + a worktree. **The plan-first gate is INLINED in them** for exactly this reason. |

**Why:** 2026-08-07 the thin-floor lint's `vendor_markers` listed `.githooks` and `.agents/scripts` —
it would have ordered the AGY conversion to **delete the armed audit trail**. Caught on paper in the
re-audit (F8), never executed.

**How to apply:** the test is *does something inside the repo execute or read this file at runtime?* If
yes it stays, however "shared" its content looks. `check_maps.py` deliberately does not flag them, and
probes `.agents/scripts` by toolkit sentinel files rather than the bare directory. Per-project **config**
(`.mcp.json`, `.opencode/mcp.json`, `.claude/settings.json`) is the same class — config, not vendor.
`core.hooksPath` is per-clone AND per-machine; git never carries it.
