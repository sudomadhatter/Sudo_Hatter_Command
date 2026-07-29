---
IsArtifact: true
ArtifactMetadata:
  title: "NEXgen VR Director research_docs reference repair walkthrough"
  type: walkthrough
  date: 2026-07-28
---

# NEXgen-VR-Director `research_docs` Reference Repair

Updated the two live references left behind by the rename from `_my_resources/docs/` to `_my_resources/research_docs/`:

1. `_my_resources/README.md` now inventories `research_docs/`.
2. `docs/workspace-standard.md` now uses the renamed directory in its rollout-source path.

No generic `docs/` references were changed; those identify the project's separate verified-reference shelf. No markdown-feedback control blocks were present.

## Verification

The old-path audit passed:

```text
===== old-path audit =====
PASS: no live old-path references found.
===== resulting references =====
Projects/NEXgen-VR-Director/_my_resources/README.md:5:- `research_docs/` — personal workspace/method guides.
Projects/NEXgen-VR-Director/docs/workspace-standard.md:10:  - _my_resources/research_docs/master-implementation-plan.md                                    # the rollout
```

The follow-up existence check found a pre-existing issue: `research_docs/` contains three files, but none is `master-implementation-plan.md`.

```text
PASS: Projects/NEXgen-VR-Director/_my_resources/research_docs
MISSING: Projects/NEXgen-VR-Director/_my_resources/research_docs/master-implementation-plan.md
```

The directory contains `BMAD_CCPS_workspace_guide.md`, `implementation-plan_folder-as-workspace-routing-system.md`, and `NEXgen-VR-Director.md`. No existing file establishes which one, if any, should replace the missing master-plan source, so that link is left as migrated rather than redirected speculatively.

## Task Checklist

- [x] Locate all live references to the renamed personal-documents directory.
- [x] Update the two stale references to `research_docs/`.
- [x] Verify no live old-path references remain.
- [x] Investigate the missing file exposed by existence validation.
- [ ] Resolve the missing `master-implementation-plan.md` target — requires Daniel's direction on the intended source document.

## Your Actions

No commit was created. If the provenance link must resolve, identify the intended document in `research_docs/` (or provide the missing master-plan file) for a separately approved follow-up.
