---
IsArtifact: true
ArtifactMetadata:
  title: Finish and transfer the NEXgen-VR-Director PRD
  type: implementation_plan
  date: 2026-07-29
---

# Implementation Plan — Finish and Transfer the NEXgen-VR-Director PRD

## Goal

Finalize the NEXgen-VR-Director PRD as a decision-ready V1 requirements document, then relocate every identified product-specific planning, brainstorming, and technical-research record from the home base into `Projects/NEXgen-VR-Director`. Preserve the home-base artifact history and the global Antigravity conversation logs as required by their respective protocols.

## Source Inventory and Destination Map

| Source | Destination | Action |
|---|---|---|
| [`_bmad-output/brainstorming/virtual-director/.memlog.md`](../../../_bmad-output/brainstorming/virtual-director/.memlog.md) | `Projects/NEXgen-VR-Director/_bmad-output/brainstorming/virtual-director/.memlog.md` | Move unchanged as session memory. |
| [`_bmad/output/brainstorming/virtual-film-previs-software/.memlog.md`](../../../_bmad/output/brainstorming/virtual-film-previs-software/.memlog.md) | `Projects/NEXgen-VR-Director/_bmad-output/brainstorming/virtual-film-previs-software/.memlog.md` | Move unchanged as the original research-question brainstorm. |
| [`_bmad-output/planning-artifacts/briefs/brief-NEXgen-VR-Director-2026-07-28/brief.md`](../../../_bmad-output/planning-artifacts/briefs/brief-NEXgen-VR-Director-2026-07-28/brief.md) | `Projects/NEXgen-VR-Director/_bmad-output/planning-artifacts/briefs/brief-NEXgen-VR-Director-2026-07-28/brief.md` | Move unchanged. |
| [`_bmad-output/planning-artifacts/briefs/brief-NEXgen-VR-Director-2026-07-28/.memlog.md`](../../../_bmad-output/planning-artifacts/briefs/brief-NEXgen-VR-Director-2026-07-28/.memlog.md) | `Projects/NEXgen-VR-Director/_bmad-output/planning-artifacts/briefs/brief-NEXgen-VR-Director-2026-07-28/.memlog.md` | Move unchanged. |
| [`_bmad-output/planning-artifacts/prds/prd-NEXgen-VR-Director-2026-07-28/prd.md`](../../../_bmad-output/planning-artifacts/prds/prd-NEXgen-VR-Director-2026-07-28/prd.md) | `Projects/NEXgen-VR-Director/_bmad-output/planning-artifacts/prds/prd-NEXgen-VR-Director-2026-07-28/prd.md` | Finalize, then move. |
| [`_bmad-output/planning-artifacts/prds/prd-NEXgen-VR-Director-2026-07-28/.memlog.md`](../../../_bmad-output/planning-artifacts/prds/prd-NEXgen-VR-Director-2026-07-28/.memlog.md) | `Projects/NEXgen-VR-Director/_bmad-output/planning-artifacts/prds/prd-NEXgen-VR-Director-2026-07-28/.memlog.md` | Move unchanged; retain the original decision history. |
| [`_my_resources/research_docs/NEXgen-VR-Director.md`](../../../_my_resources/research_docs/NEXgen-VR-Director.md) | `Projects/NEXgen-VR-Director/_my_resources/research_docs/NEXgen-VR-Director.md` | The target already holds an identical copy; verify its hash, then remove the home-base copy so the project owns the research record. |

The existing home-base records in [`_artifacts/NEXgen-VR-Director/`](../) remain in place. They are session history for work performed from the lobby, not product artifacts to relocate. The two recovered Antigravity transcript logs remain in the IDE's global conversation store; they are source context, not project files to copy into the repository.

## Planned Changes

1. Reconcile the PRD with its brief, technical research, brainstorming records, and recovered conversation decisions. The flow will require a director-approved scene breakdown before generation; a script view with structured scene-description inputs and guided controls; and a chat collaborator for rewriting, feedback, and optional shot recommendations.
2. Add the missing V1 requirements: PDF, `.fdx`, and plain-text imports; automatic dialogue/motion regeneration after script edits; a Wardrobe Room for manually assigning a newly introduced character; saved multi-shot sequences with continuous playback, pause-and-adjust, individual-shot exports, whole-scene MP4, and ZIP export; unlimited in-session edit undo/redo; automatic proxy prop placement plus user adjustment; professional lighting presets and key-light controls; ambient/SFX and user-supplied music controls; project save, delete, and restart; no offline mode; and one hero frame per page in the storyboard PDF.
3. Define the Live Director and Step Director modes: auto-detect the appropriate mode, provide manual override, and establish a clear wait-to-generate loop for lower-spec machines including M3/16 GB unified-memory systems. Preserve the product behavior while making the specific procedural-motion provider an architecture validation gate, not an unverified engineering commitment.
4. Strengthen acceptance conditions, non-functional requirements, safety/consent constraints for voice cloning, success counter-metrics, and the ownership/revisit condition for unresolved technical choices. Update frontmatter to `status: final` only after review.
5. Add the PRD’s required `.decision-log.md` in the destination run folder. It will record the finalization decision, the preserved source log, recovered conversation decisions, and the provider-validation constraint without rewriting or deleting the historic `.memlog.md`.
6. Replace the product placeholders in the destination’s `_bmad-output/project-context.md` and `_bmad-output/active-context/active-context.md` with the finalized product identity, confirmed planning state, and the files now in play. No implementation scaffolding, application code, dependency, or deployment configuration changes are included.
7. Move the six inventoried BMAD files into the destinations above, verify the already-copied technical-research file, and then remove its superseded home-base copy. Create only the required destination directories. Do not copy or leave duplicate product records behind.
8. Verify the transfer by comparing source/destination file hashes before removal, confirming every destination path, checking the PRD’s frontmatter and FR/UJ/SM ID continuity, and confirming that no NEXgen-specific product files remain in the source BMAD or research locations.

## Review and Verification

- Run the PRD quality rubric plus structural and prose reviews; resolve critical and high findings before finalization.
- Cross-check all PRD requirements against the existing brief, technical research, decision logs, and the two recovered Antigravity sessions.
- Use primary documentation to verify vendor claims. The current evidence supports UE5 Pixel Streaming and Chatterbox; no primary source was found for an NVIDIA product named “ARDY,” so the PRD will not represent it as confirmed.
- Verify all moved files with SHA-256 hashes and a targeted product-name search in both source and destination.
- Record actual command output, moved paths, and review results in `walkthrough.md`.

## Open Decision

The PRD will finalize the product behavior while treating the procedural-motion engine as a technical-validation gate rather than an assumed vendor integration. This preserves the vision without committing engineering to a dependency that could not be verified.
