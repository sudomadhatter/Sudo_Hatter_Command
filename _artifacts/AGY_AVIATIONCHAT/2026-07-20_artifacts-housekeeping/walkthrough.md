---
IsArtifact: true
ArtifactMetadata:
  title: Walkthrough — AGY _artifacts housekeeping (homeless sessions → _main + placement-law update)
  type: walkthrough
  date: 2026-07-20
---

# Walkthrough — AGY `_artifacts/` housekeeping

Three homeless session folders sat at the `_artifacts/` root of AGY_AVIATIONCHAT. Per Daniel's directive they
now live in `_main/` (the holding bucket — a session stays there until it has a home or one is made), the
sprint dependency map references all three, and the placement law is updated everywhere it is written down.

## What changed

### 1. The moves (git mv, staged in the AGY repo)
| Old (root) | New |
|---|---|
| `_artifacts/2026-07-13_profile-idor-fix/` | `_artifacts/_main/2026-07-13_profile-idor-fix/` |
| `_artifacts/2026-07-13_security-fail-closed-hardening/` | `_artifacts/_main/2026-07-13_security-fail-closed-hardening/` |
| `_artifacts/2026-07-19_adk-2.5-upgrade/` | `_artifacts/_main/2026-07-19_adk-2.5-upgrade/` |

Inside the moved files every `../../` project-root link became `../../../` (one level deeper). Historical
pasted `git add` commands keep their old paths — they are records of commands already run.

### 2. Live references repointed (AGY)
`_bmad-output/planning-artifacts/epics.md` · `_bmad-output/test-artifacts/test-design-epic-19.md` ·
`_bmad/bmm/stories/story-19.1-runtime-pins-explicit-key-auth.md` ·
`_bmad-output/implementation-artifacts/sprint-status.yaml` · `_bmad-output/active-context/active-context.md` ·
`_bmad/bmm/stories/security-fail-closed-hardening.md` — all now point at `_artifacts/_main/…`.

### 3. Combined into `sprint-dependency-map.md` (`_my_resources/_quick_reference/`)
- **Epic 19 track**: source-artifact note linking the VERIFIED upgrade plan (phases, the two real breaking
  changes, the Phase-3 wipe gate).
- **§C security row**: links to both 2026-07-13 security session folders at their new home.
- **References & Sources of Truth**: three new entries (Epic 19 plan, S-1/S-2 walkthrough, S-3/S-4 walkthrough).

### 4. Placement law updated — "no homeless folders at the `_artifacts/` root; `_main/` is the holding bucket"
- **AGY**: `_artifacts/INDEX.md` header + `README.md` + `AGENTS.md` (local law); `_main/INDEX.md`
  (header, 3 new rows, fixed the drifted 2026-07-03 artifact list); `_main/README.md` **rewritten** (was a
  broken 3-line stub). New INDEX rows added for all three sessions (they had never been logged).
- **Canon + template propagation (18 files via one scripted pass)**: `.agents/rules/artifacts-always-first.md`,
  `docs/workspace-standard.md`, `.agents/templates/project-template/AGENTS.md`,
  `sudo-dev-story-tests.md` (`.agents/commands` + `.agents/workflows` + `.opencode/commands`) — in the lobby
  master AND the AGY + Fresh vendored copies. Also swapped "Daniel's" → "the operator's" in the one rule line
  touched (per the no-personal-name rule). Fresh's `_artifacts/` README/INDEX/AGENTS hand-mirrored
  (living-template rule).

### Not changed (deliberate)
- The autopilot engines' root-fallback for non-epic story ids (`autopilot-dev-story*.ps1` ×3 + `autopilot_mobile.md`
  reuse-glob) — behavior change across three drifting engines; flagged as follow-up, not slipped into housekeeping.
- Historical INDEX rows / pasted commands keep old paths (history is immutable).
- B-L-WorldWide copies (not on the maintained-projects allowlist).
- Lobby `_artifacts/README.md` one-off rule — lobby one-offs already land inside a bucket (the bucket IS the home).

## Verification (real output)
- `git mv` staged all 3 renames in the AGY repo (branch `main_debug`).
- Post-pass grep for the old paths: only historical pasted-command text remains (the moved walkthroughs' own
  `## Your Actions` + one epic_16 walkthrough referencing a *different* relocated folder).
- Propagation check: `grep -c "holding bucket"` = expected count in all 18 canon/template files; the only
  remaining "at the root." is the story bullet's intentional "Epic-scoped, not date-prefixed at the root."

## Task Checklist
- [x] Move 3 homeless session folders into `_artifacts/_main/` (git mv)
- [x] Fix relative links inside moved files (`../../` → `../../../`)
- [x] Update AGY `_artifacts` control files (INDEX, README, AGENTS, `_main/` INDEX + README)
- [x] Repoint stale references (epics, story-19.1, sprint-status, active-context, test-design-epic-19, security story)
- [x] Combine the 3 sessions into `sprint-dependency-map.md` as linked references
- [x] Propagate the placement rule (master rule / workspace-standard / template / command — lobby + AGY + Fresh)
- [x] Log session (this folder + lobby INDEX row + AGY INDEX rows)

## Your Actions
1. **Commit AGY** (branch `main_debug`; the 3 renames are already staged, the doc edits are not):
   ```bash
   cd Projects/AGY_AVIATIONCHAT
   git add -A _artifacts/ _bmad-output/ _bmad/bmm/stories/ _my_resources/_quick_reference/sprint-dependency-map.md .agents/ .opencode/ docs/workspace-standard.md
   git commit -m "chore(artifacts): relocate homeless root sessions into _main holding bucket + placement-law update

   profile-idor-fix, security-fail-closed-hardening, adk-2.5-upgrade -> _artifacts/_main/;
   live refs repointed; sprint-dependency-map now links all three; INDEX/README/AGENTS +
   vendored rule/standard/command updated: nothing homeless at the _artifacts root."
   ```
2. **Commit the lobby** (master rule/standard/template/command + Fresh mirrors + this session):
   ```bash
   git add .agents/ .opencode/commands/sudo-dev-story-tests.md docs/workspace-standard.md _artifacts/ Projects/Fresh_Workspace_BMAD/
   git commit -m "chore(rules): _main is the holding bucket — no homeless folders at a project _artifacts root (canon + Fresh mirror)"
   ```
3. Optional follow-up: decide whether the three autopilot engines' non-epic root-fallback should also route to
   `_main/` (needs the fix in all three engines + the mobile command).
