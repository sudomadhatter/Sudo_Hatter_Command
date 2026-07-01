# Active Context — Fresh_Workspace_BMAD

> Continuity brief for the home base's `Fresh_Workspace_BMAD` workspace. "pick up" reads this.

## 1. Current state (2026-06-25)
Fresh_Workspace_BMAD is now the **AGY quick-start project skeleton** — the repo Daniel clones to start a new
project. Identity re-cast from "aviationChat clone" → a generic skeleton that **keeps the AGY stack**
(FastAPI/ADK · Next/React · Firebase — Daniel uses it on almost all projects) but is organized/indexed/governed
like the home base. Still workspace-standard compliant + repo-map indexed, now with a **hybrid auto-updating
repo-map** (a SessionStart hook injects the map + runs a detect-only drift nag).
Latest session: `2026-06-25_quickstart-skeleton-reshape/` (plan · walkthrough · task-list · settings.json.proposed).
- AGENTS.md ROOT LAW/MAP/routing re-cast to the skeleton (9-section + stack rows kept; +re-index/drift row).
  README rewritten to the real tree + clone→rename→build flow. `_bmad-output/project-context.md` dead
  `.agent/gemini.md` refs genericized. `docs/repo-map.md` regenerated + curated header rewritten.
- **New `scripts/check-repo-map-drift.ps1`** (tested: silent when current, nags a new folder, exit 0) + a
  proposed `.claude/settings.json` SessionStart hook — **Daniel applies the hook himself** (auto-mode blocks the
  agent editing startup config); full file saved as `2026-06-25_quickstart-skeleton-reshape/settings.json.proposed`.

**Prior (2026-06-25):** workspace-standard cleanup — AGENTS.md→9-section, repo-map built, vendored
`workspace-standard.md`+generator, `_01_My/`→`_my_resources/` (protected), `_claude_artifacts/` deprecated,
corrected the "off-limits/another team" mischaracterization. Session: `2026-06-25_workspace-standard-cleanup/`.

**Prior (2026-06-24):** converted to the home-base `.agents` format — first project conversion; the reference
pattern for the queued projects. Session: `2026-06-24_agents-format-conversion/`.

## 2. What the new format looks like here
- Root: thin `CLAUDE.md` + `GEMINI.md` ("Read AGENTS.md") + a generic Layer-2 `AGENTS.md` map.
- `.agents/` (plural) = single vendored toolkit; `.claude/` + `.opencode/` are synced copies.
- Rules load by path from `.agents/rules/` (no `.claude/rules/` anymore). `.agent/` (singular) is gone.
- `opencode.json` → least-context `instructions` (AGENTS.md + constitution + karpathy), `.agents/skills`.

## 3. Decisions baked in
- **Git: agents NEVER commit/push** — print the command, Daniel pushes. Resolved at source: master
  `git-policy.md` is the canonical never-commit rule (replaced `git-closeout-commits.md`); Fresh_Workspace_BMAD's
  `AGENTS.md` just defers to it (verbose override removed after re-sync).
- **Rules self-route now:** all 12 master rules carry `description:` frontmatter triggers, and each toolkit
  dir (`rules/commands/workflows/skills`) has an `INDEX.md` router ("when to use which"). Vendored here.
- **Autopilot is "doc + shared placement":** model-agnostic doc in master `.agents/workflows/`; engine
  stays Claude/Opus-4.8 and harness-independent (spawns its own `claude` workers). Script stays
  project-local (`$RepoRoot = $PSScriptRoot\..` binding — do NOT move it).
- **Keep Fresh_Workspace_BMAD generic** — it's the template/sandbox; no aviationChat domain values.

## 4. Pitfalls learned (apply to the next 6 conversions)
- Before deleting `.agent/`, copy out any unique non-vendored files (Fresh_Workspace_BMAD had 3 in `.agent/workflows/`,
  one git-untracked). Preserved here in `2026-06-24_.../_preserved-from-old-.agent/`.
- Rewrite `opencode.json` paths or the first opencode session won't boot.
- BMAD owns `_bmad/`, `.agents/bmad/`, `bmad-*` skills/commands — never customize those; new vendored set
  wins over old `.agent/skills`.

## 5. Open / pending (Daniel)
- **Apply the SessionStart hook** — replace `.claude/settings.json` with
  `2026-06-25_quickstart-skeleton-reshape/settings.json.proposed` (agent was blocked from self-editing startup
  config). That switches ON the hybrid auto-updating repo-map.
- **Commit + push BOTH repos** (Fresh_Workspace_BMAD + home-base) — agents don't push; exact commands in
  `2026-06-25_quickstart-skeleton-reshape/walkthrough.md`. (If the prior `workspace-standard-cleanup` commit is
  still pending, fold both into one.)
- **WS7 follow-up (offered):** promote `check-repo-map-drift.ps1` → master `.agents/scripts/` and wire the
  *home base's* own SessionStart hook to it, so home base + projects share one drift mechanism.
- **Prune aviationChat skills from the vendored `.agents/` set** — define a generic-skeleton sync profile at
  master + `/sync-agents` (biggest remaining aviationChat-DNA removal; anti-fork, master-level).
- **Master pass (DONE 2026-06-27):** repointed the `1_*` commands + `scripts/autopilot-dev-story.ps1` off
  `_claude_artifacts/` → `_artifacts/` (master `.agents/` + every synced copy), converted fresh-workspace to the
  **project-local `_artifacts/`** model (AGENTS.md §5/§7/§9 + a new `docs/file_structure_rules/README.md` + an
  `_artifacts/` scaffold, mirroring aviationChat), updated the project-template, and deleted the dead
  `_claude_artifacts/` store.
- **aviationChat milestone (separate track):** apply the workspace-standard recipe to the live aviationChat repo
  (its own assessment + plan + approval).
- Tiny/optional: genericize the "sully" example slug in `scripts/autopilot-dev-story.ps1:168`; re-run
  `_routing-canary/` + a cold-route test ("work on a new project").
