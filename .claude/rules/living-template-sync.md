---
name: living-template-sync
description: "The clone source for new projects is the sudo-project-skeleton REPO (thin — no vendored toolkit). Fires when you change the front-door pattern, the folder layout, the enforcement set, or the thin-project floor at the home base: those are per-workspace and do NOT propagate by any automatic mechanism, so they must be hand-mirrored into the skeleton or every new project starts stale. Toolkit/rule edits do NOT need mirroring — projects read them from the center."
trigger: glob
globs: [AGENTS.md, ".agents/templates/**", "_bmad/custom/**"]
paths:
  - "AGENTS.md"
  - ".agents/templates/**"
  - "_bmad/custom/**"
# Path-scoped. `globs:` is Antigravity's field; `paths:` is Claude Code's, and Claude
# loads this file ONLY when it reads a file matching one of them. Both lists are the
# same set on purpose — one classification, two readers (test_rule_frontmatter.py).

---

# Living Template — keep the skeleton repo current

**`sudomadhatter/sudo-project-skeleton` is the one clone source for new projects.** `/smh-new-project`
clones it, strips its history, and git-inits. If the skeleton drifts behind the home base, every new
project starts stale — and unlike the old model, **nothing detects that for you**.

> **History (2026-08-07, SCC-25 + SCC-31).** `Projects/Fresh_Workspace_BMAD` was the living template
> until it was retired: de-listed from `maintained-projects.txt`, frozen on disk, and left deliberately
> stale. The `/smh-sync-agents` Fresh drift-check that used to warn you was deleted with the project-vendor
> path. There is no automated detector now — this rule is the whole mechanism.

## What propagates, and what does NOT

| Change at the home base | Reaches a new project how |
|---|---|
| A shared rule, `/` command, skill, workflow, script | **Automatically — nothing to do.** Under the thin model (`project-law.md`) projects carry no toolkit copy; sessions run from the center, so every project already sees the current version. This is the whole win of centralization. |
| Front door: root `AGENTS.md`, `CLAUDE.md`/`GEMINI.md`, `README.md` | **Hand-mirror into the skeleton.** Per-workspace content; keep it generic — `<PROJECT_NAME>` / `{{PLACEHOLDER}}` where a real project fills in. |
| Folder layout, the thin-project floor, `.gitignore` | **Hand-mirror.** If `check_maps.py`'s floor gains a required file, the skeleton must ship it or every clone lints red on day one. |
| The enforcement set — `.githooks/`, `.agents/scripts/git-hooks/`, `jira.conf.example` | **Hand-mirror.** These are repo-local by design and never synced. A fix to a hook script at the center does not reach the skeleton on its own. |
| `.agents/INDEX.md` template stub, the BMAD `_bmad/custom/*.toml` (incl. the INLINED plan-first gate) | **Hand-mirror.** The gate text lives inline in the tomls; edit the canonical rule first, then mirror it into the skeleton's two tomls. |

## The obligation

After changing anything in the right-hand "hand-mirror" rows: **clone the skeleton fresh, apply the
change, and verify it still passes the thin floor** —

```bash
python3 .agents/scripts/check_maps.py --root <path-to-fresh-clone>   # must be [ok] clean
```

A clone should need only placeholder fills, never structural setup. If the clone lints red, a new
project would have shipped that red.

## Why this rule survived centralization

Centralization removed the *toolkit* propagation problem entirely — that is now automatic. What it did
NOT remove is the **template** problem: a clone source is a snapshot, and snapshots rot. This rule is
what keeps the snapshot honest, and it is now purely manual, so it has to be a rule rather than a tool.
