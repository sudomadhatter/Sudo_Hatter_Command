---
IsArtifact: true
ArtifactMetadata:
  title: Mobile-mode rule for the command center
  type: implementation_plan
  date: 2026-06-25
---

# Mobile-mode rule — implementation plan

**TL;DR.** The command center is now driven from a phone, but the rules were written for a desktop dev
loop. Two of them fight the phone (git "hand me the terminal command", typed "approved"). Add one new
`mobile-mode.md` lane + light pointers so the system adapts on web/mobile. Approved via plan mode.

## Decisions (confirmed with Daniel)
- Git on mobile: agent commits + pushes; **asks before opening a PR**.
- Approval gate on mobile: **tap-to-approve chip** (`AskUserQuestion`) replaces typed "approved".
- Shape: new `mobile-mode.md` as source of truth + one-line pointers in the rules it overrides.

## Files
- NEW `.agents/rules/mobile-mode.md` — the lane (4 overrides: git, approval, artifacts, verification).
- `.agents/rules/INDEX.md` — add the row.
- `.agents/rules/git-policy.md` — pointer under "Default".
- `.agents/rules/artifacts-always-first.md` — pointer at "The Gate".
- `.agents/rules/constitution.md` — pointers on the approval + git hard-stop lines.
- `AGENTS.md` — §3 pointer for web/mobile sessions.
- Re-sync `.agents/` → `.claude/` / `.opencode/` (`/sync-agents`).

## Verification
Re-read mobile-mode end-to-end; confirm pointers resolve; dry-run a mobile task (plan → tap → commit/push
own files → ask before PR); confirm sync.
