---
IsArtifact: true
ArtifactMetadata:
  title: Antigravity IDE Extension Migration Guide
  type: implementation_plan
  date: 2026-08-11
---

# Implementation Plan — Antigravity IDE Extension Migration Guide

## Goal

Add a practical guide for exporting the installed Antigravity IDE extension IDs from the Windows PC, uploading that inventory through the shared `Sudo_Hatter_Command` Git repository, and installing only the missing extensions on this Mac.

## File to Add

- [`docs/migrations/install_guides/antigravity-ide-extension-migration.md`](../../../docs/migrations/install_guides/antigravity-ide-extension-migration.md) — the Windows-to-Mac export, upload, import, verification, and troubleshooting procedure. This is the final location explicitly supplied by the operator.

The existing [`docs/migrations/INDEX.md`](../../../docs/migrations/INDEX.md) is part of an uncommitted folder relocation already in progress in the shared checkout. This task will not modify that other lane's file. Its normal map/index reconciliation can inventory the new guide after the relocation lands.

## Guide Content

1. Explain the distinction between Antigravity IDE extensions and Gemini/Antigravity agent plugins or skills.
2. On Windows, locate or enable the `agy-ide` command and export unversioned `publisher.extension` IDs.
3. Save the portable manifest at `docs/migrations/antigravity_extensions/antigravity-extension-ids.txt` in the PC clone.
4. Explain that the manifest contains extension IDs only and is safe to commit; it must never contain credentials or copied extension folders.
5. Upload through Git with explicit-path staging, commit, and push commands, while noting that the repository's normal Jira-key commit gate still applies.
6. On the Mac, pull the repository, compare the PC manifest with the extensions already installed locally, and install only missing IDs using Antigravity IDE's real application command.
7. Include a direct-command fallback because this Mac's `agy-ide` PATH shortcut currently points to a stale installer-volume location.
8. Verify the final list, describe expected cross-platform exceptions, and explain that extension logins or machine-specific dependencies may still need separate setup.
9. Add troubleshooting for `agy-ide` not found, an extension unavailable from Antigravity's gallery, version/platform mismatches, and blank lines in the manifest.

## Execution Order

1. Draft the new guide in the existing `install_guides` folder.
2. Use the current Antigravity IDE CLI names and paths already verified on this Mac.
3. Check every Windows PowerShell and macOS shell command for quoting and cross-platform safety.
4. Confirm that no secret values, tokens, copied extension binaries, or machine-specific absolute paths are proposed for Git upload.
5. Review the focused diff for the new guide only.

## Verification

- Confirm the guide file is the only migration-document change made by this task.
- Confirm the Windows export produces one unversioned extension ID per line.
- Confirm the Mac comparison prevents unnecessary reinstall attempts.
- Confirm the Mac install command uses the verified Antigravity IDE binary path when `agy-ide` is unavailable.
- Confirm all repository and local-file paths shown in the guide are platform-correct.
- Run Markdown/link checks that can target the new file without rewriting the migration index or other in-flight files.

## Scope and Safety

- No extension installation will be performed in this session; the deliverable is the guide.
- No existing migration file will be edited because the folder relocation is already in flight.
- No Git commit, push, merge, deletion, or external upload is included in this implementation step.
- The guide will recommend extension IDs rather than copying `extensions.json` or extension directories, because those contain OS-specific paths and platform metadata.

## Open Questions

None. The requested direction is explicit: Windows PC is the source; this Mac is the destination; Git is the recommended upload/transfer channel.
