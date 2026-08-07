---
name: followon-fixes-are-not-a-new-story
description: "Remediating a closed story's recorded findings is NOT a new story — no worktree, no board key. Fix on the epic branch (or a chore/* branch off main when no epic is live) with explicit-path commits. And don't leave recorded findings unfixed."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: db7ff31d-93b1-482f-8606-5d35ebbd0bfd
  modified: 2026-07-30T17:38:27.215Z
---

Operator, 2026-07-30, twice in one turn:
- **"nono worktree just fix it — this is not a new story"** (I had started `git worktree add` +
  `claude/story-21-4-followon-ghost-window` for post-close-out remediation).
- **"we are not leaving half finished work"** — said when I reported three ③ findings as *deferred /
  flagged / operator-owned* rather than fixed.

**Why:** the worktree-per-story machinery exists for STORIES — a story has a board key, a status, a
lifecycle. Follow-on remediation of findings already recorded against a closed story has none of that;
spinning up a worktree + branch for it is ceremony that buys nothing and leaves a stray branch behind.
And a finding recorded as "deferred" still reads as unfinished work to the person who has to ship it.

**How to apply:**
- Fix directly on the story's epic branch (no new story worktree); when no epic is live, take a
  short-lived `chore/*` branch off `main` and merge it back the same session with sign-off. Never in the
  shared `main` checkout. Commit with **explicit paths** (another lane's
  staged work often lives there — never `git add -A`), push, verify `0 0` + clean.
- Record it on the CLOSED story's board line and its ③ verdict as a dated FOLLOW-ON block, so the
  verdict stops reading as an outstanding obligation. No new board key.
- Before deferring a finding, look once more for the fix that keeps the operator's ruling AND removes
  the human step — see [[agy-school-identity-ghost-doc-window]], where "the operator must delete the old
  docs" turned out to have a code answer (retire by renaming) that honoured never-delete.
- "Flagged, not done" is a last resort, not a tidy outcome. If it genuinely must wait, say what would
  change the answer.

Related: [[close-out-command-is-daniels-signoff]], [[own-it-plainly-dont-make-excuses]],
[[commit-and-push-are-one-action]].
