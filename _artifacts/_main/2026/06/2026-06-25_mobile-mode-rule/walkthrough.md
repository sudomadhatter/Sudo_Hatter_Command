---
IsArtifact: true
ArtifactMetadata:
  title: Mobile-mode rule — walkthrough
  type: walkthrough
  date: 2026-06-25
---

# Mobile-mode rule — walkthrough

**TL;DR.** Added a `mobile-mode.md` lane so the command center adapts when driven from a phone:
agent commits/pushes (asks before PR), tap-to-approve replaces typed "approved", artifacts go
TL;DR-first, and verification runs in-container instead of on Daniel's phone. Five existing rules got
one-line pointers to it. No code, no app to test — this is governance markdown.

## What changed, file by file
- **NEW `.agents/rules/mobile-mode.md`** — the lane. Activates auto on a remote/cloud container (web or
  phone) or when Daniel says "mobile". Four overrides:
  1. **Git** — commit/push own files (keeps `git-policy` safe-commit mechanics: explicit paths, never
     `git add -A`, verify staged set); **ask before the PR**; "Your Actions" becomes "review PR #N".
  2. **Approval** — plan inline TL;DR-first, then tap **Approve / Change** via `AskUserQuestion`; a tap IS the gate.
  3. **Artifacts** — same set, but TL;DR-first and terse; chat replies stay short (summary + link).
  4. **Verification** — agent runs tests/app in-container and pastes a short result; never asks Daniel to run locally.
- **`.agents/rules/INDEX.md`** — added the `mobile-mode.md` row (on-demand, auto on web/mobile).
- **`.agents/rules/git-policy.md`** — pointer under "Default" → mobile lane.
- **`.agents/rules/artifacts-always-first.md`** — pointer at "The Gate" → tap-to-approve.
- **`.agents/rules/constitution.md`** — pointers on the approval + git hard-stop lines.
- **`AGENTS.md`** — §3 pointer: web/mobile session → also load `mobile-mode.md`.

## What fought back
Nothing — it went clean. One useful discovery: `.claude/` and `.opencode/` only carry `commands` +
`skills`, **not** `rules`. Rules are read straight from `.agents/rules/`, so the planned `/sync-agents`
step was unnecessary (and that script is PowerShell, not runnable in this Linux container).

## Tests
No automated tests apply (markdown rules). Verification was a manual re-read + a dry-run of the mobile
task flow against the new lane — consistent, every override names the desktop rule it supersedes.

## Your Actions
This is a web/mobile session, so per the new lane I committed and pushed to
`claude/optimistic-einstein-km4ucj` for you. **No terminal command needed.**
- **Review:** the pushed branch / draft PR (link in chat).
- The draft PR was opened only after your tap-confirm.
