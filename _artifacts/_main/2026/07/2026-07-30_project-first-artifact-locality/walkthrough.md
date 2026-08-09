---
IsArtifact: true
ArtifactMetadata:
  title: Project-first artifact locality walkthrough
  type: walkthrough
  date: 2026-07-30
---

# Project-first artifact locality walkthrough

## Outcome

Artifact placement is now ownership-first:

- Every current or future directory under `Projects/` is project-owned by default.
- Project history always goes to `Projects/<name>/_artifacts/`, regardless of cwd or agent/tool.
- The complete Sudo-managed exception registry contains only:
  - `Fresh_Workspace_BMAD`
  - `OpenChat-Openrouter`
- Home-base and cross-project system work remains under `_artifacts/_main/`.

The workspace-structure skill drove the default local-store/template shape. The architectural-propagation
checklist drove the live-surface audit, maintained-project parity checks, stale-rule grep, and migration
verification.

## Rule and tooling changes

Updated the home-base authority:

- root `AGENTS.md` and `router.md`;
- `_artifacts/AGENTS.md`, `_artifacts/README.md`, and `_artifacts/_main/README.md`;
- canonical `artifacts-always-first` rule and `workspace-structure` skill;
- canonical `docs/workspace-standard.md`;
- `check_maps.py` so lobby continuity reads `_main` plus only router-registered exceptions;
- `new-project.ps1` so new workspaces create project-local `_artifacts/_main`, never a Sudo project bucket;
- the generic project template, including a new project-local `_artifacts/` skeleton.

Updated maintained workspace front doors and local laws:

- AviationChat is project-owned with one authoritative local history.
- NEXgen VR is project-owned with one authoritative local history.
- Fresh Workspace is explicitly Sudo-managed; its repository-local `_artifacts/` is clone scaffold content,
  and the exception does not transfer to clones.

The canonical rule, structure skill, map checker, and workspace standard were vendored byte-identically to
AviationChat, Fresh Workspace, and NEXgen VR.

## Artifact migration

### AviationChat

- Former source: `_artifacts/AGY_AVIATIONCHAT/`
- Destination: `Projects/AGY_AVIATIONCHAT/_artifacts/_main/`
- Files verified: 18
- Bytes verified: 146677
- Manifest SHA-256:
  `15737F9D94BA41CB9F8DE982C1394E50FA8ECDD334776EE3201228D1E3B56FD8`
- Source removed after verification: yes
- Six dated sessions moved; legacy bucket `INDEX.md` and `README.md` preserved in the migration record.

### NEXgen VR

- Former source: `_artifacts/NEXgen-VR-Director/`
- Destination: `Projects/NEXgen-VR-Director/_artifacts/_main/`
- Files verified: 9
- Bytes verified: 57266
- Manifest SHA-256:
  `922EE87BC2F76497B1B67083566A32B6FE4A5EEC812F59CF5C4D14DDC67BDE49`
- Source removed after verification: yes
- Four dated sessions moved; legacy `active-context.md` preserved in the migration record.

The migrated session contents were not rewritten. Historical self-references therefore remain historical,
while live project indexes point to the new project-local paths.

## Preserved Sudo-managed folders

The Sudo `_artifacts/` root now has exactly:

- `_main/`
- `Fresh_Workspace_BMAD/`
- `OpenChat-Openrouter/`

The root store itself was not deleted because it is the required home for Sudo system history and both
explicit exceptions.

## Verification

- Canonical parity: 12/12 comparisons passed (four canonical files across three maintained projects).
- Exception parser result: exactly `Fresh_Workspace_BMAD` and `OpenChat-Openrouter`.
- Active-rule grep: zero cwd-based, "check both," or home-base fallback instructions across the live
  authority and the three maintained workspace front doors.
- Migration fingerprints: both recomputed destination fingerprints match the pre-move source fingerprints.
- Deleted-source check: both former Sudo project buckets are absent.
- New-project check:
  - creates project-local `_artifacts/_main`: yes;
  - creates a home-base project bucket: no;
  - template contains artifact law and index: yes.
- Python syntax: `check_maps.py` parsed successfully.
- Depth-3 artifact check: lobby, Fresh Workspace, and NEXgen VR returned clean.
- `git diff --check`: clean in the lobby and all three project repositories.

The supported `sync-agents.ps1` command encountered an unrelated Windows permission denial while attempting
to refresh the protected `merge_main_debug.md` workflow. The four files in this task were therefore copied
narrowly to the three projects and then SHA-256 checked for exact parity. No protected workflow was changed.

The full map/index linter still reports pre-existing repo-map freshness and unrelated AviationChat
debugging/Epic 21 index rows. Those findings do not affect artifact ownership, exception routing, migrated
content, or canonical parity and were not expanded into this task.

## Task Checklist

- [x] Replace cwd-based placement with ownership-first placement.
- [x] Make all non-exempt `Projects/` workspaces project-owned by default.
- [x] Register only Fresh Workspace and OpenChat as Sudo-managed exceptions.
- [x] Update new-project scaffolding and the generic project template.
- [x] Sync and hash-verify the rule across AviationChat, Fresh Workspace, and NEXgen VR.
- [x] Hash, move, and re-verify the AviationChat Sudo artifacts.
- [x] Hash, move, and re-verify the NEXgen VR Sudo artifacts.
- [x] Delete only the two verified obsolete Sudo project buckets.
- [x] Preserve `_main`, Fresh Workspace, and OpenChat.
- [x] Reconcile live migration indexes and continuity.
- [x] Run focused routing, syntax, hash, index, and diff verification.

## Your Actions

No commit, push, PR, deployment, dependency change, or application-code change occurred. The rule and
migration changes remain uncommitted across the Sudo Hatter, AviationChat, Fresh Workspace, and NEXgen VR
repositories. Existing unrelated NEXgen BMAD/PRD/UX/TEA changes and the unrelated Sudo
`_my_resources/open_tasks/project_setup_bmad` path were preserved.
