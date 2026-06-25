# Active Context — clean-bmad-workspace

> Continuity brief for the home base's `clean-bmad-workspace` workspace. "pick up" reads this.

## 1. Current state (2026-06-24)
clean-bmad-workspace has been **converted to the home-base `.agents` format** — the first project
conversion (router.md had it as "first conversion (next)"). It is now the reference pattern for the 6
queued projects. Full session: `2026-06-24_agents-format-conversion/` (plan · playbook · walkthrough).

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
- Live **opencode routing test** on clean-bmad (the real proof) — not yet run.
- Fate of the 3 preserved old workflows (promote to master / archive).
- Commit + push (clean-bmad repo + home-base master toolkit changes) — agents don't push; see walkthrough.
- Then: apply the playbook to aviationChat-AGY (convert LAST per router) + the other queued projects.
