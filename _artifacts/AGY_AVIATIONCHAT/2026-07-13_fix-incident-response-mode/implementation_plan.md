---
IsArtifact: true
ArtifactMetadata:
  title: "Fix Incident Response Mode & Inputs"
  type: implementation_plan
  date: 2026-07-13
  RequestFeedback: true
  UserFacing: true
  Summary: "Implementation plan to resolve the deprecated 'mode' and 'prompt_file' inputs in the GitHub Actions incident-response workflow by migrating to the anthropics/claude-code-action@v1 input schema."
---

# Fix Incident Response Mode & Inputs

## Goal Description

Resolve the action error `Invalid action input 'mode' @[.github/workflows/incident-response.yml:L53]`. This error occurs because the `mode` parameter has been deprecated and removed in version 1.x of the `anthropics/claude-code-action` GitHub Action. The action now automatically detects interactive vs automation (agent) mode. Additionally, `prompt_file` has been deprecated and replaced with `prompt`, which accepts direct text rather than a file path.

We will update the workflow file to read the prompt file content in a preceding step and pass it directly to the `prompt` input parameter.

## User Review Required

No major architectural decisions or breaking changes are introduced. This is a standard syntax fix aligning the workflow with the updated GitHub Action version.

## Open Questions

None.

## Proposed Changes

### Projects/AGY_AVIATIONCHAT

#### [MODIFY] [incident-response.yml](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/.github/workflows/incident-response.yml)

- Add a step `Read prompt from file` prior to the Claude Code step to load the triage runbook Markdown content using `cat` and output it to `$GITHUB_OUTPUT`.
- Remove the deprecated `mode: agent` input from `anthropics/claude-code-action@v1`.
- Replace `prompt_file: .github/claude/incident-triage.md` with `prompt: ${{ steps.read-prompt.outputs.body }}`.

## Verification Plan

### Automated Tests
- None. This is a GitHub Actions workflow file change. We can run a syntax check/lint if necessary, but the logic will be executed inside the GitHub Actions runner.

### Manual Verification
- Trigger the workflow manually or trigger a repository_dispatch event to verify the runner executes without input validation errors.
