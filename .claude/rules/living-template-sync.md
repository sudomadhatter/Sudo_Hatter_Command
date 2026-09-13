---
name: living-template-sync
description: "The clone source for new projects is the sudo-project-skeleton REPO (thin — no vendored toolkit). Fires when you change the front-door pattern, the folder layout, the enforcement set, the PR gate's shape, or the thin-project floor at the home base: those are per-workspace and do NOT propagate by any automatic mechanism, so they must be hand-mirrored into the skeleton or every new project starts stale. Toolkit/rule edits do NOT need mirroring — projects read them from the center."
trigger: glob
globs: [AGENTS.md, ".agents/templates/**", "_bmad/custom/**", ".github/**"]
paths:
  - "AGENTS.md"
  - ".agents/templates/**"
  - "_bmad/custom/**"
  - ".github/**"
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
| The PR gate and its classifier — a project's `pr-check.yml` under `.github/workflows/`, its `.github/scripts/`, the ruleset recipes under `.github/rulesets/` | **Hand-mirror.** CI is repo-local and never synced. When a project changes the shape of the gate (the diff classifier, a per-job `if:`, a ruleset), the skeleton gets the same shape by hand, with placeholders where the project's names go. The lobby's own `main-write-gate.yml` is not part of this row — the skeleton does not ship the lobby's gate. |
| `.agents/INDEX.md` template stub, the BMAD `_bmad/custom/*.toml` (incl. the INLINED plan-first gate) | **Hand-mirror.** The gate text lives inline in the tomls; edit the canonical rule first, then mirror it into the skeleton's two tomls. |

## There are TWO living templates, and only one of them is detected

They are easy to confuse and they fail differently, so the distinction is stated here rather than
left to be rediscovered.

| Template | What it is | Kept current by | Detector |
|---|---|---|---|
| `sudo-project-skeleton` | the clone source for a NEW project | **hand-mirroring**, the table above | **none** — this rule is the whole mechanism |
| `sudo-command-center` | the PUBLISHED teaching edition the team pulls | **generated** by `/smh-publish-teaching-edition` in the source command centre; never hand-edited | `teaching_edition_staleness.py`, armed at SessionStart |

**The teaching edition is not hand-mirrored and must never be.** Every byte under
`Projects/sudo-command-center` is a sanitized export of this lobby. A hand edit there is deleted by
the next export and — because it never passed the exporter — it **bypasses the leak scan on a public
repo**. Something wrong in the published edition is a bug in the lobby master or in
`lobby.manifest.json`; fix it there and re-export.

Its staleness is now measurable: the export stamps `.teaching-edition-source` with the lobby sha, and
in the source command centre `teaching_edition_staleness.py` reads it from
`.agents/hooks/session-start-context.sh` and says one line when the copy the team pulls has gone
stale. It reports and never blocks.

**The skeleton still has no detector.** That is the open half of this rule, and it is the same engine
away: a second manifest sourced from a real project. Until then, the table above is enforced by
nothing but this page.

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
