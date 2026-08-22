---
IsArtifact: true
ArtifactMetadata:
  title: Worktree-per-story · agents commit and land their own stories
  type: implementation_plan
  date: 2026-07-22
---

# Implementation Plan — Agents work in worktrees, commit, and land their own stories

**Workspace:** home base, propagating to `AGY_AVIATIONCHAT` + `Fresh_Workspace_BMAD`
**Status:** AWAITING APPROVAL — nothing outside `_artifacts/` touched.

## What this is

Agents were forbidden to commit or push. Now they're allowed — inside a worktree, on their own branch,
landing once at your sign-off. **Remove the old restriction, state the new rules, done.** Most of the
file list below is deleting one stale sentence per file.

## Why the deletions can't be skipped

The restriction isn't written once. It's in `git-policy.md`, in three `AGENTS.md` GATES sections, in
the constitution's hard stops — and, most importantly, in a **SessionStart echo string in all three
`settings.json` files** that injects *"GIT: hand Daniel the exact command; never commit/push yourself"*
into every session at boot. Rewrite the rule but leave that string, and the agent obeys the string.
That's why "remove the restriction" touches more than one file.

## The new rules, stated

1. **Worktree per story.** Story or dev work opens its own worktree off `main_debug` before the first
   file is edited. One story, one worktree, one `claude/*` branch. Automatic — no asking. Read-only
   sessions don't need one.
2. **Commit freely inside it.** Explicit paths only — `git add -A` / `.` / `-u` stay banned. Verify the
   staged set before committing.
3. **One landing.** `/sudo-update-sprint-memory` — or your "approved" in the moment — merges
   `origin/main_debug` into the story branch *inside the worktree* and pushes the result to
   `main_debug`. One story, one clean push. The shared checkout is never touched, so nobody else's
   uncommitted work rides along.
4. **`main` is yours.** Only when you ask directly or run `/sudo-push-e2e`.

## Change list

| File | Change |
|---|---|
| `rules/git-policy.md` | **The main edit.** Repair corruption (its body appears twice — truncated dupe at 1–77 ahead of the real copy at 79–169) and rewrite: the worktree lane is the policy, not an exception on the old one. |
| `rules/worktree-per-story.md` | **NEW**, protocol tier — the four rules above, plus exemptions. |
| `rules/INDEX.md` | Protocol-tier line + row; the `git-policy` row still reads *"you NEVER commit/push."* |
| `commands/sudo-update-sprint-memory.md` + `workflows/` twin | **New Step 7 — land it.** Plus two stale lines: *"'commit owed' is NOT a blocker — agents never commit"* and *"the exact git command — agents never commit."* |
| `hooks/require-push-approval.py` | One conditional: `git commit` while HEAD is `main`/`main_debug` → **ask** (your call from the last question). Pushes unchanged. |
| `.claude/settings.json` ×3 | `"worktree": { "baseRef": "head" }` — today it defaults to `fresh`, which means `origin/main`, which is why worktrees branch off production. Plus the SessionStart echo string. |
| `AGENTS.md` ×3 | Lobby §6; `AGY_AVIATIONCHAT` L95–98 (*"agents **NEVER commit/push**"*); `Fresh_Workspace_BMAD` L75–84. |
| `rules/constitution.md` L19 · `rules/artifacts-always-first.md` ×4 | One-line each. "Your Actions" stops being a `git add` block. |
| `rules/bmad_code_review_sudo_fix.md` L47 | Live bug — tells agents to remind you with `git add -A && git commit && git push`. |
| 6 story-flow commands + workflow twins + 2 BMAD guard tomls | One line each: *"never `git commit`/`push`"* → commit in the worktree. |
| `Projects/AGY_AVIATIONCHAT/` · `Projects/Fresh_Workspace_BMAD/` | Hand-copy the above. Verified byte-identical today for `git-policy`, the hook, and both close-out copies; I re-check each file before overwriting and **report instead of copying** anything that has drifted. |

## Cut from my first draft

- **The `git merge` gate and the `EnterWorktree` base guard.** You asked for the commit gate; I invented
  the other two. `baseRef: head` plus a line in the rule covers the base, and an agent isn't going to
  spontaneously merge in the shared checkout once the rule says work happens in worktrees. Also drops
  the new hook matcher — the hook keeps matching `Bash` only.
- **The `/update-maps-indexes` rewording.** Not story work, nobody's confused by it. Left alone.
- **The 7-payload test matrix** → 3 (below).

## Verification

1. `git-policy.md` reads once end-to-end; no frontmatter mid-file.
2. Hook: commit on `main_debug` → ask · commit on `claude/x` → pass · push `claude/x` → pass. Output pasted.
3. All three `settings.json` parse as valid JSON.
4. Re-grep all three repos for `never commit` / `git add -A` — zero survivors outside the deliberate
   exceptions (`/sudo-push-e2e`, `/update-maps-indexes`, autopilot).
5. **Live proof is the next story** — until one runs the lane end to end, this is written policy, not
   proven policy.

**Nothing here is committed or pushed. This one lands by your hand.**

<!-- CHECKPOINT id="ckpt_mrwzminj_5sclyl" time="2026-07-23T04:04:47.983Z" note="auto" fixes=0 questions=0 highlights=0 sections="" -->
