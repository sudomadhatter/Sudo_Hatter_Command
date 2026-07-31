---
IsArtifact: true
ArtifactMetadata:
  title: Project-first artifact locality with Sudo-managed exceptions
  type: implementation_plan
  date: 2026-07-30
---

# Project-first artifact locality with Sudo-managed exceptions

## Outcome

Replace the current cwd-based artifact rule with an explicit ownership rule:

> If a task belongs to a standalone product project, every session artifact and conversation record belongs
> in that project's own `_artifacts/`, regardless of where the chat was launched or which tool ran it.
> Workspaces explicitly registered as Sudo-managed exceptions continue to use the home-base artifact store.

The home base keeps:

- operating-system and cross-project governance work under `_artifacts/_main/`;
- explicitly registered Sudo-managed workspace histories under `_artifacts/<workspace-name>/`;
- lightweight portfolio/open-task notes under `_my_resources/`;
- historical ledger notes that point to project-owned records.

`Fresh_Workspace_BMAD` and `OpenChat-Openrouter` are the only Sudo-managed exceptions. They retain their
home-base artifact buckets. Every other current or future folder under `Projects/` is project-owned unless
Daniel explicitly adds another exception.

This plan is intentionally stored under home-base `_artifacts/_main/` because it changes the shared
operating system and workspace-routing contract. It is not a NEXgen product artifact.

## Root cause

The current canonical rule says artifacts go "where you work FROM." A standalone project session launched
from Sudo_Hatter_Command is therefore routed into a lobby project bucket, while the same session launched
inside its repository is routed project-local. This creates two histories and breaks portability.

Folder location is not sufficient to determine ownership: Fresh Workspace is a living duplication template,
and OpenChat is fully managed by Sudo Hatter even though both folders are under `Projects/`.

The invariant is repeated in:

- the root operating contract and home-base `_artifacts/` local law;
- the canonical artifact rule and workspace-structure skill;
- the canonical workspace standard and project copies;
- the project template and living template;
- new-project scaffolding and map/continuity maintenance;
- several project front doors and project-local artifact laws.

Moving NEXgen alone would repeat the 2026-07-29 transfer without removing the cause. The invariant and its
exception model must change together.

## New routing contract

1. Determine the **artifact owner**, not the current directory.
2. Maintain one explicit Sudo-managed exception registry in `router.md`.
3. Register `Fresh_Workspace_BMAD` as `sudo-managed exception - living template`.
4. Register `OpenChat-Openrouter` as `sudo-managed exception`.
5. Treat that two-entry registry as the complete exception list. Every directory under `Projects/` that is
   not on the exception list is automatically project-owned and uses `Projects/<name>/_artifacts/`.
6. Standalone story work follows the project's epic/story bucket; debugging follows its debugging bucket;
   planning, research, architecture, UX, TEA, and ad-hoc work use project-local `_main/` unless local law
   names a better home.
7. If a standalone project lacks `_artifacts/`, create the project-local store; never fall back to a lobby
   project bucket.
8. Shared command-center and cross-project work uses `_artifacts/_main/`; registered exceptions use their
   named Sudo-managed buckets.
9. Tool identity does not override ownership.
10. Home-base project notes may remain in protected `_my_resources/` shelves, but they are pointers or
    notes—not session artifacts or authoritative project documents.
11. New workspaces automatically default to project-owned artifacts. A Sudo-managed exception must be
    deliberately added to the exception registry; it is never inferred from a name, missing feature, or
    nonconformance.

## Current workspace result

| Workspace under `Projects/` | Artifact ownership |
| --- | --- |
| `AGY_AVIATIONCHAT` | project-owned |
| `B-L-WorldWide` | project-owned |
| `BRKN_Tattoos` | project-owned |
| `Fresh_Workspace_BMAD` | Sudo-managed exception - living template |
| `NEXGen-Films` | project-owned |
| `NEXgen-VR-Director` | project-owned |
| `OpenChat-Openrouter` | Sudo-managed exception |
| `RAG_Pipeline_AC` | project-owned |

AGY, BRKN Tattoos, NEXgen VR, and RAG Pipeline already have project-local `_artifacts/` stores. B-L
WorldWide and NEXGen Films do not; create a minimal project-local artifact store for each as part of this
change. OpenChat intentionally receives no project-local store. Fresh Workspace's local `_artifacts/`
content is duplicable scaffold material; its live operational/session history remains in the Sudo-managed
home-base bucket.

## Migration scope

Migrate only the two standalone product projects whose histories are currently split:

| Lobby source | Project-local destination | Session folders | Root files |
| --- | --- | ---: | --- |
| `_artifacts/AGY_AVIATIONCHAT/` | `Projects/AGY_AVIATIONCHAT/_artifacts/_main/` | 6 | `INDEX.md`, `README.md` |
| `_artifacts/NEXgen-VR-Director/` | `Projects/NEXgen-VR-Director/_artifacts/_main/` | 4 | `active-context.md` |

No destination session-name collisions exist.

For each migrated project:

- build a SHA-256 source manifest;
- move every dated session folder into project-local `_main/`;
- preserve unique root-level history as a named legacy snapshot in a project-local migration record;
- merge only current state into the project's live continuity brief where appropriate;
- reconcile the project-local artifact ledger;
- build a destination manifest and compare hashes;
- remove the now-empty lobby source bucket only after file count, byte count, and hashes pass.

Do not migrate or delete:

- `_artifacts/Fresh_Workspace_BMAD/` — authoritative Sudo-managed history for the living template;
- `_artifacts/OpenChat-Openrouter/` — authoritative Sudo-managed history for OpenChat.

These buckets are intentional exceptions, not legacy leakage.

## Canonical rule and tooling changes

### Home-base authority

- `AGENTS.md`
- `router.md`
- `_artifacts/AGENTS.md`
- `_artifacts/README.md`
- `.agents/rules/artifacts-always-first.md`
- `.agents/skills/workspace-structure/SKILL.md`
- `docs/workspace-standard.md`

Remove cwd-based routing, establish the exception registry, prohibit lobby buckets for every non-exempt
project, and document the notes-only allowance.

### Templates and scaffolding

- `.agents/templates/project-template/AGENTS.md`
- `.agents/templates/project-template/_artifacts/`
- `.agents/scripts/new-project.ps1`
- `.agents/commands/new-project.md`
- `.agents/workflows/new-project.md`

New projects are born with a project-local artifact store. Scaffolding stops creating a home-base named
bucket by default. A Sudo-managed workspace requires explicit addition to the exception registry.

### Maintenance behavior

- `.agents/scripts/check_maps.py`
- `.agents/commands/update-maps-indexes.md`
- `.agents/workflows/update-maps-indexes.md`

Home-base continuity discovery inspects `_artifacts/_main/` plus only registered Sudo-managed exception
buckets. Project-mode behavior remains project-local.

### Living template and existing front doors

- Keep Fresh Workspace itself Sudo-managed while updating its duplicable template content so a newly cloned
  standalone project defaults to project-owned artifacts. State that Fresh's exception does not transfer to
  clones.
- Keep OpenChat Sudo-managed and do not create a competing project-local artifact history.
- Bootstrap minimal project-local artifact stores for B-L WorldWide and NEXGen Films.
- Update every other project under `Projects/` as project-owned, including NEXgen, AviationChat, BRKN
  Tattoos, B-L WorldWide, NEXGen Films, and RAG Pipeline.
- Update project contracts/local laws that explicitly tell agents to check or write a lobby project bucket.
- Update affected live file-structure guides.
- Run the master sync so changed rules, skills, scripts, commands, workflows, and templates are propagated
  to conformant surfaces.

Historical completed stories and archived artifacts are not rewritten. Live documents that depend on moved
artifacts are repointed; historical narrative references receive a superseding migration note.

## Safety

- Resolve and print every absolute source and destination before moving.
- Verify every recursive move target remains inside the named source bucket or matching project.
- Never overwrite a destination; stop on any collision.
- Hash every source file before movement and every destination file afterward.
- Remove a migrated lobby bucket only after file count, byte count, and SHA-256 content match.
- Preserve the Fresh Workspace and OpenChat exception buckets.
- Preserve unrelated home-base artifacts, `_my_resources/`, and dirty work in every repository.
- No commit, push, deployment, dependency change, or application-code change.

## Verification

1. Grep active rules for the retired cwd invariant, ambiguous "check both" instructions, and automatic
   creation of home-base buckets for standalone projects.
2. Expected live-rule result: zero cwd-based routes; archived occurrences are reported separately.
3. Confirm the only project-named lobby buckets are the registered exceptions:
   `Fresh_Workspace_BMAD` and `OpenChat-Openrouter`.
4. Confirm AGY and NEXgen session files exist project-local with identical hashes and no source duplicate.
5. Confirm all six project-owned workspaces have local artifact stores and neither exception is routed to a
   project-local operational history.
6. Run focused disposable tests for `new-project.ps1` and `check_maps.py`; create no real project.
7. Run workspace/map conformance checks on the lobby and affected conformant workspaces.
8. Run cold-route simulations:
   - "work on NEXgen" → `Projects/NEXgen-VR-Director/_artifacts/...`;
   - "work on AviationChat" → `Projects/AGY_AVIATIONCHAT/_artifacts/...`;
   - "maintain the Fresh template" → `_artifacts/Fresh_Workspace_BMAD/...`;
   - "work on OpenChat" → `_artifacts/OpenChat-Openrouter/...`;
   - "change shared Sudo rules" → `_artifacts/_main/...`.
9. Verify canonical and vendored rule copies match where exact parity is required.
10. Confirm the exception registry contains exactly Fresh Workspace and OpenChat, and every other current
    or future `Projects/` directory follows the project-owned default without requiring registration.

## Completion record

Close with one home-base `walkthrough.md` containing:

- migration manifest results for AGY and NEXgen;
- evidence that both Sudo-managed exception buckets were preserved;
- every changed live-rule surface;
- propagation and routing-audit results;
- the final task checklist;
- a `## Your Actions` section confirming no git delivery occurred unless separately authorized.

## Approval boundary

Approval authorizes:

- the project-owned artifact rule and explicit Sudo-managed exception mechanism;
- registration of Fresh Workspace and OpenChat as the current exceptions;
- application of the project-owned default to everything under `Projects/` that is not an exception;
- creation of minimal project-local artifact stores for B-L WorldWide and NEXGen Films;
- migration of only AGY and NEXgen lobby buckets into their matching repositories;
- deletion of only those two migrated source buckets after hash verification;
- master rule/tool/template changes and propagation to affected conformant workspaces;
- continuity, ledger, conformance, and walkthrough updates required by the migration.

Approval does not authorize application code changes, dependency installation, commits, pushes, PRs,
deployment, full conversion of nonconformant workspaces, or migration of Fresh Workspace or OpenChat.
