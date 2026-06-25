# Active Context — clean-bmad-workspace

> Continuity brief for the home base's `clean-bmad-workspace` workspace. "pick up" reads this.

## 1. Current state (2026-06-25)
clean-bmad-workspace is now **fully workspace-standard compliant + repo-map indexed** — the rehearsal that
proves the recipe before it's applied to the live aviationChat project. It is **Daniel's clean-shell
clone-template** (NOT another team's — the old "off-limits" notes were corrected this session).
Session: `2026-06-25_workspace-standard-cleanup/` (plan · walkthrough · task-list).
- AGENTS.md rewritten to the 9-section standard; `docs/repo-map.md` built (curated header + generated body);
  vendored `docs/workspace-standard.md` + `scripts/generate_repo_map.py`.
- `_01_My/` → **`_my_resources/`** (protected personal area: agents don't edit/reference unless Daniel
  says/links — see its README + AGENTS.md §8). `_claude_artifacts/` marked deprecated (folder kept until the
  master repoint pass).

**Prior (2026-06-24):** converted to the home-base `.agents` format — first project conversion; the reference
pattern for the queued projects. Session: `2026-06-24_agents-format-conversion/`.

## 2. What the new format looks like here
- Root: thin `CLAUDE.md` + `GEMINI.md` ("Read AGENTS.md") + a generic Layer-2 `AGENTS.md` map.
- `.agents/` (plural) = single vendored toolkit; `.claude/` + `.opencode/` are synced copies.
- Rules load by path from `.agents/rules/` (no `.claude/rules/` anymore). `.agent/` (singular) is gone.
- `opencode.json` → least-context `instructions` (AGENTS.md + constitution + karpathy), `.agents/skills`.

## 3. Decisions baked in
- **Git: agents NEVER commit/push** — print the command, Daniel pushes. Resolved at source: master
  `git-policy.md` is the canonical never-commit rule (replaced `git-closeout-commits.md`); clean-bmad's
  `AGENTS.md` just defers to it (verbose override removed after re-sync).
- **Rules self-route now:** all 12 master rules carry `description:` frontmatter triggers, and each toolkit
  dir (`rules/commands/workflows/skills`) has an `INDEX.md` router ("when to use which"). Vendored here.
- **Autopilot is "doc + shared placement":** model-agnostic doc in master `.agents/workflows/`; engine
  stays Claude/Opus-4.8 and harness-independent (spawns its own `claude` workers). Script stays
  project-local (`$RepoRoot = $PSScriptRoot\..` binding — do NOT move it).
- **Keep clean-bmad generic** — it's the template/sandbox; no aviationChat domain values.

## 4. Pitfalls learned (apply to the next 6 conversions)
- Before deleting `.agent/`, copy out any unique non-vendored files (clean-bmad had 3 in `.agent/workflows/`,
  one git-untracked). Preserved here in `2026-06-24_.../_preserved-from-old-.agent/`.
- Rewrite `opencode.json` paths or the first opencode session won't boot.
- BMAD owns `_bmad/`, `.agents/bmad/`, `bmad-*` skills/commands — never customize those; new vendored set
  wins over old `.agent/skills`.

## 5. Open / pending (Daniel)
- **Commit + push BOTH repos** (clean-bmad repo + home-base) — agents don't push; exact commands in
  `2026-06-25_workspace-standard-cleanup/walkthrough.md`.
- **Next milestone:** clean-bmad verified ✓ → apply the same recipe to the live **aviationChat** project
  (its own assessment + implementation_plan + approval).
- **Master pass (deferred):** repoint vendored cmds + `scripts/autopilot-dev-story.ps1` off `_claude_artifacts/`
  → home-base `_artifacts/` (check the engine's `$RepoRoot` first), then delete `_claude_artifacts/`.
- Optional: live opencode routing test + re-run `_routing-canary/` (AGENTS.md renumber = routing-structure change).
- Fate of the 3 preserved old workflows (promote to master / archive).
