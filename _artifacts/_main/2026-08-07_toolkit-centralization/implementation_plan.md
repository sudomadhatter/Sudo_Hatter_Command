---
IsArtifact: true
ArtifactMetadata:
  title: Toolkit Centralization — thin projects, command-center-only rules/commands
  type: implementation_plan
  date: 2026-08-07
---

# Toolkit Centralization — implementation plan

**Goal:** the command center becomes the ONLY home of workflow rules, commands, skills, and sync;
projects hold only project-relevant content (code, `_bmad/` + `_bmad-output/`, `_artifacts/`,
`_my_resources/`, docs, and their OWN project law). Removes ~10,400 vendored toolkit files across
repos and ends the per-project sync fan-out (23% of AGY's recent commits were sync noise).
**Umbrella plan:** each phase below runs as its own quick-dev with its own per-phase approval.

## Target architecture
- **Command center owns:** `.agents/` master (rules/commands/skills/workflows/scripts/templates),
  lobby `.claude/`+`.opencode/` synced copies, machine-global caches (opencode, Antigravity,
  Codex). `/sync-agents` = lobby + globals only; platform filtering + manifest unchanged.
- **Thin project owns:** `AGENTS.md` (map), `CLAUDE.md`/`GEMINI.md` 2-line pointers,
  **`.agents/rules/` + `.agents/skills/` (tier-2 project law, below)** with `.agents/INDEX.md`,
  `_bmad/` (stories + custom tomls, BMAD identity), `_bmad-output/`, `_artifacts/`,
  `_my_resources/`, `docs/` (incl. `repo-map.md`), code + stack configs, `.gitignore`
  (keeps ignoring `.claude/` — worktrees stay machine-local there).
- **Deleted from projects:** vendored `.agents/{commands,workflows,scripts,opencode-agents,hooks,
  templates,reference,bmad,AGENTS.md,CLAUDE.md,GEMINI.md,active-project.txt,maintained-projects.txt,
  project-own.txt,.sync-manifest.json}`, all non-project `.agents/skills+rules`, tracked `.claude/`,
  `.opencode/`, `.gemini/`, `.antigravity/`, `opencode.json`, `.mcp.json`, `.githooks/`.

## Tier-2 project law (rules AND skills)
- A project's `.agents/` holds ONLY its own law: `rules/` + `skills/` + one `.agents/INDEX.md`
  router (same Load/Trigger columns as the lobby's: floor = load at bind; protocol = before first
  write in that project; on-demand = trigger). Paths keep the `.agents/...` convention so every
  existing reference (AGY routing table, tomls) survives unchanged.
- **The center AUTHORS project law**: a project-specific learning/rule/skill is written into THAT
  project's tier-2, never the master; `/sudo-update-sprint-memory`'s learning-routing step gains
  this destination. Project skills are loaded by PATH via the INDEX (not slash-registered) —
  slash-invocable-everywhere stays master-only.
- AGY domain skills move home from master (declutters every other session):
  `3_voice-ai-development, 4_sse-streaming-patterns, 5_adk_skills, 6_dual-store-rag-patterns,
  agent-handoff-patterns, gcp-cloud-run, gemini-live-api, hr-agent-schema-guide,
  rag-implementation, regulatory-verification-protocol, specialist_agents_team, deploy-backend,
  troubleshoot-cloudrun-deployment` (final list confirmed in P3).

## ⛔ The always-check guarantee (the main threat)
Binding a project MUST load its law. Five anchors, one mechanism, so it cannot be skipped:
1. `.agents/rules/sudo-target-resolution.md` **§BIND** (every /sudo-* routes through it): after
   binding PROJECT_ROOT, read `PROJECT_ROOT/.agents/INDEX.md` and honor its Load column; missing
   INDEX in a converted project → STOP and say so.
2. New master rule **`.agents/rules/project-law.md`** — the tier-2 contract + authoring duty.
3. **`constitution.md`** (floor, always loaded) gains the one-line law: "binding a project = loading
   its `.agents/INDEX.md` law — no exceptions."
4. Lobby + project **`AGENTS.md`** anchor it inline (same conditional-rule/anchored-law pattern §3
   already uses); project AGENTS.md §4 lists its floor rules.
5. **`check_maps.py` floor**: a converted project without `.agents/INDEX.md` is a lint ERROR —
   absence can never silently no-op.
BMAD lanes: the custom tomls' persistent_facts gain "check {project-root}/.agents/INDEX.md".

## Phases
**P1 — Law (lobby only).** Write `project-law.md`; §BIND addition; constitution line; lobby
`AGENTS.md` §2/§4/§8 + `router.md` "converted" redefinition; `docs/workspace-standard.md` thin-
project floor. Verify: anchors grep-present; `check_maps.py` lobby pass.

**P2 — Enforcement (lobby scripts).** `check_maps.py`: new project floor (require AGENTS.md,
pointers, `docs/repo-map.md`, `_artifacts/` INDEX, `.agents/INDEX.md`; ERROR on stale vendor dirs
listed above). `sync-agents.ps1`: delete -Maintained fan-out + project-vendor + project -Target
stages (flag → explanatory error); header rewrite. `new-project.ps1` + `/new-project` command:
clone `https://github.com/sudomadhatter/sudo-project-skeleton` → strip `.git` → `git init` → set
`_bmad` identity → print router.md + .gitmodules manual rows. Verify: `-WhatIf` sync run;
`tests/run_all.py`; `check_maps --all` (expected STALE-VENDOR reds = P3/P4 worklist).

**P3 — AGY pilot.** Pre-flight: `git worktree list` empty, status clean, autopilot idle.
(a) Inline the plan-first gate text into `_bmad/custom/bmad-dev-story.toml` +
`bmad-quick-dev.toml` (no path survives both machines AND worktrees; full rule still lives at
lobby). (b) Both engines `scripts/autopilot-dev-story*.ps1`: `claude`/opencode child launches with
**cwd = lobby**, project passed as leading $ARGUMENTS token; master autopilot docs updated.
(c) Build tier-2: `.agents/INDEX.md` + keep 7 own rules (`adk_file_formating,
constitution.project, credential-resolution, prompt-tdd, pyrefly-paths,
useEffect-dep-array-stability, voice-agent-architecture`); move the domain skills in from master.
(d) Promote `autopilot_glm.md` to master commands. (e) Rewrite `AGENTS.md` (22 toolkit refs).
(f) Delete the vendor set; keep pointers; `.gitignore` keeps `.claude/`; unset `core.hooksPath`
(note for Windows too). Verify: `check_maps --root` green; `/sudo-boot-sprint-memory AGY` smoke;
bmad-quick-dev dry-run shows the inlined gate firing; dead-ref grep sweep (excluding
`_artifacts/`, `_bmad-output/` history); commit+push `main_debug`, `0 0` + clean.

**P4 — NEXgen-VR-Director + RAG_Pipeline_AC.** Same pattern. VR: 2 tomls + 2 engines + 8 own
rules. RAG: no tomls/hooks/engines; 2 own rules (`constitution.project, credential-resolution`);
strip partial vendor. Verify + push each.

**P5 — Skeleton repo (`sudo-project-skeleton`).** Strip its ~2,500 vendor files to the thin
template: template `AGENTS.md`, pointers, `.agents/INDEX.md` stub, tomls with inlined gate, keep
`_bmad/` module + `_bmad-output/` + `_artifacts/` + `_my_resources/` skeletons + stack
(backend/frontend/firebase). README = clone quick-start. Verify: fresh clone →
`check_maps --root` green; `/new-project` dry-run; push (its own repo).

**P6 — Freeze + sweep.** Remove `Fresh_Workspace_BMAD` from `maintained-projects.txt` (frozen
archive of the old shape; router status row updated). Docs: `system-builder.md`, lobby repo-map
regen, `/update-maps-indexes`. Memory rewrites: `fresh-workspace-living-template`,
`maintained-projects-allowlist`, `toolkit-sync-covers-agents-not-docs`,
`autopilot-engine-is-project-local`, `autopilot-mobile-mirrors-claude`,
`sudo-commands-have-ap-twins`, `check-maps-all-false-stale-agy`, `command-center-sudo-skills`.
Final no-skeletons audit: ref-grep across lobby + 3 projects + skeleton; full `/sync-agents`;
end-to-end sudo smoke on AGY. Push everything, per-repo `0 0` + clean.

## Open decisions (recommendation first)
1. **/autopilot_mobile**: cloud clones ONE repo → can't see the lobby. **Park it** (deprecation
   banner in command + skill; revisit if ever needed). Alt: rework later against Remote Control.
2. **Project githooks**: **drop** (already inert on this Mac — `core.hooksPath` unset; map lint
   runs deliberately via `/update-maps-indexes`). Alt: SUDO_HOME env indirection.
3. **B-L / BRKN / NEXGen-Films / OpenChat**: stay frozen as-is, old vendor and all (not on the
   maintained list; untouched by design).

## Risks / skeleton-prevention
- **Silent gates:** the two quiet failures (plan-first toml gate, push-approval hook) get positive
  verification in P3 (dry-run must SHOW the gate text) before any deletion commits.
- **Strip order:** fix reachers (tomls, engines, AGENTS.md) BEFORE deleting what they reached.
- **Live worktrees:** P3/P4 pre-flight refuses to run with open story lanes.
- **History is immutable:** `_artifacts/`/`_bmad-output/` docs referencing old paths stay as-is.
- **Windows machine:** changes arrive via git pull; then re-run `/sync-agents` (globals) + unset
  per-project `core.hooksPath`; verify one sudo flow there before the next sprint.
- **Fresh keeps old vendor deliberately** — off the maintained list so the new lint never flags it.

## Verification (summary)
Per phase above; system-level: `python .agents/scripts/check_maps.py --all` green after P4;
`pwsh .agents/scripts/sync-agents.ps1 -WhatIf` shows zero project targets; AGY story flow ① → ③
runs end-to-end from the lobby; skeleton clone passes floor lint.
