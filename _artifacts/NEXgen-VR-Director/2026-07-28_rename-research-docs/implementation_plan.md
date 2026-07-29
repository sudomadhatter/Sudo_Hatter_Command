---
IsArtifact: true
ArtifactMetadata:
  title: "Repair NEXgen VR Director research_docs references"
  type: implementation_plan
  date: 2026-07-28
---

# Implementation Plan — Repair NEXgen-VR-Director `research_docs` References

## Goal

Bring NEXgen-VR-Director documentation into agreement with Daniel's completed folder rename from `_my_resources/docs/` to `_my_resources/research_docs/`.

## Scope

1. Update `_my_resources/README.md` so its personal-area inventory names `research_docs/`.
2. Update the provenance link in `docs/workspace-standard.md` from `_my_resources/docs/master-implementation-plan.md` to `_my_resources/research_docs/master-implementation-plan.md`.
3. Leave the remaining `docs/` mentions unchanged: they refer to the project's distinct verified-reference shelf. Leave historical artifact-ledger text unchanged as immutable history.

## Execution Order

1. Make the two targeted Markdown replacements only.
2. Search the project for `_my_resources/docs` in slash and backslash forms to ensure no live old-path references remain.
3. Confirm that each resulting `research_docs` reference resolves to the renamed directory or file.

## Verification

- `rg` reports no remaining `_my_resources/docs` or `_my_resources\\docs` references in the project.
- The two changed lines name `research_docs/` exactly.
- No markdown-feedback control blocks are touched.

## Open Questions

None. The target directory already exists, and the repository scan identified exactly these two live references.
