---
IsArtifact: true
ArtifactMetadata:
  title: Antigravity IDE Extension Migration Guide Walkthrough
  type: walkthrough
  date: 2026-08-11
---

# Walkthrough — Antigravity IDE Extension Migration Guide

Status: Complete

Branch: shared checkout (`main`); no commit or push requested or performed

Baseline SHA: `50e357b677341b6025fcc79ad1c100198fd613a5`

## Task Checklist

- [x] Inspect the migration-doc layout and existing cross-machine conventions.
  - The `docs/migrations` relocation was already in flight, so no existing migration file was modified.
- [x] Write and present the implementation plan for approval.
- [x] Add the Windows-to-Mac Antigravity IDE extension migration guide to the explicitly supplied `docs/migrations/install_guides` folder.
- [x] Cover PC export, safe upload, Mac comparison, missing-only installation, verification, and troubleshooting.
- [x] Verify PowerShell and Bash command-block syntax.
- [x] Confirm the requested root path exists and the superseded subfolder path does not.

## Evidence

| Requirement | Evidence |
|---|---|
| Export extension inventory on Windows | Guide Part 1 uses `agy-ide --list-extensions`, validates `publisher.extension` syntax, sorts, deduplicates, and writes UTF-8 without BOM. |
| Upload information for use on the Mac | Guide Part 2 provides a durable private-repository route and a one-time direct file-upload route. |
| Install only missing Mac extensions | Guide Parts 3–4 normalize CRLF, compare sorted inventories with `comm -23`, and loop only over the missing set. |
| Avoid unsafe cross-OS copying | Opening and exception sections prohibit copying `extensions.json` or Windows extension packages. |
| Work around this Mac's stale shortcut | Mac steps use the verified application-bundle command path instead of the broken `agy-ide` symlink. |
| Verify completion | Guide Part 5 recalculates the difference; empty output is the stated success condition. |

Static checks: `6` PowerShell blocks parsed successfully; `6` Bash blocks passed `bash -n`; guide is `278` lines.

Path check: final `docs/migrations/install_guides` file present; superseded migration-root path absent.

Git SHA at verification: `50e357b677341b6025fcc79ad1c100198fd613a5`.

## Suite Ledger

| Scope | Command | Duration | Result | Why this run |
|---|---|---:|---|---|
| PowerShell snippets | PowerShell AST parser over fenced `powershell` blocks | <1 s | PASS — 6 blocks | Prove Windows examples are syntactically valid without executing migration actions. |
| macOS snippets | Extract fenced `bash` blocks and pipe to `bash -n` | <1 s | PASS — 6 blocks | Prove Mac examples are syntactically valid. |
| File placement | `test` checks for requested and superseded paths | <1 s | PASS | Prove the operator's path correction was applied. |
| Focused status | `git status --short -- <task paths>` | <1 s | PASS | Confirm the guide and artifacts while avoiding conclusions about another lane's relocation work. |

## Your Actions

- Open the completed guide when you are on the Windows PC and follow Part 1 to create the extension manifest.
- No commit, push, merge, extension installation, or external upload was performed in this session.
