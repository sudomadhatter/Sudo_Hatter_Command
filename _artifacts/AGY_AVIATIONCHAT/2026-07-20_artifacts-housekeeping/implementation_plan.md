---
IsArtifact: true
ArtifactMetadata:
  title: Plan — AGY _artifacts housekeeping (homeless sessions → _main)
  type: implementation_plan
  date: 2026-07-20
  approval: Daniel's direct instruction IS the approved plan (explicit move + combine + fix-indexes directive)
---

# Plan — AGY `_artifacts/` housekeeping

Daniel's directive (verbatim intent): anything in `Projects/AGY_AVIATIONCHAT/_artifacts/` with **no home
folder goes in `_main/`** until it has one or one is made; the three named sessions get **combined into
`sprint-dependency-map.md`** as references; then **fix all the indexes and READMEs** to reflect the structure.

## Steps
1. `git mv` the 3 homeless root sessions into `_artifacts/_main/`:
   `2026-07-13_profile-idor-fix/` · `2026-07-13_security-fail-closed-hardening/` · `2026-07-19_adk-2.5-upgrade/`.
2. Fix relative links inside the moved files (`../../` → `../../../`; historical pasted git commands left as history).
3. Repoint every live reference to the old paths: `epics.md`, `test-design-epic-19.md`, `story-19.1`,
   `sprint-status.yaml`, `active-context.md`, `security-fail-closed-hardening.md`.
4. Weave the 3 artifacts into `_my_resources/_quick_reference/sprint-dependency-map.md` (Epic 19 source-plan
   note, security-row artifact links, References entries).
5. Update the placement law in AGY's `_artifacts/` control files (INDEX header, README, AGENTS local law,
   `_main/` INDEX + README — README was a broken 3-line stub, rewritten).
6. Propagate the policy ("no homeless at the root — `_main/` is the holding bucket") to canon + the living
   template: `.agents/rules/artifacts-always-first.md`, `docs/workspace-standard.md`,
   `.agents/templates/project-template/AGENTS.md`, `sudo-dev-story-tests` (commands + workflows copies) —
   lobby master + AGY + Fresh vendored copies (18 files); Fresh `_artifacts/` README/INDEX/AGENTS hand-mirrored.
7. Log the session (this folder + lobby INDEX row + AGY project INDEX rows).
