---
name: landing-is-not-closeout
description: "A story branch can land on its epic branch with its close-out never run — shipped code sitting behind a `review` board, or behind NO board key at all. Check the board against git after any merge; a merge commit is not a status flip."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d66e2178-5d8a-4ad6-a3d7-69ee9388dda2
  modified: 2026-07-27T04:31:41.084Z
---

`/sudo-update-sprint-memory` is Steps 1–6 (verify · route learnings · flip status · prune) **then** Step 7
(land the branch) and Step 8 (prune the worktree). Those halves can come apart: **Steps 7–8 can run on their
own**, leaving the code merged, the worktree and branch pruned, and the board still reading `review`.

Happened to **Story 21.6** — merged to `main_debug` at `bbf18f12` on 2026-07-25 with worktree and branch
cleanly deleted, but `sprint-status.yaml` and the story frontmatter still said `review` a day later. The
operator caught it, not the tooling.

**Why it matters:** the board — not git — is what the next session reads. `/sudo-boot-sprint-memory` will
happily re-offer a shipped story as the next thing to work, and a `review` line invites someone to re-run ③
on code that already landed on the epic branch. See [[sprint-dependency-map-recommends-stale-work]] for the same
class of failure one layer up.

**How to apply:**
- When asked to close out a story, **check git first**: `git log --oneline | grep <story>` and
  `git merge-base --is-ancestor <story-sha> epic/<key>-<slug>` (the story's epic branch; against `main`
  if the epic has already merged and its branch is gone). If the code already landed, Steps 7–8 are done —
  do not try to re-land it, and do not stop just because HEAD is the epic branch and Step 7's `claude/*`
  precondition fails. That precondition exists to stop *story work* being committed in the shared checkout;
  bookkeeping for an already-landed story is a different thing. Commit the close-out paths explicitly
  (never `git add -A` — the shared checkout usually carries other sessions' dirt) and say plainly that
  is what you did.
- The story branch being **gone** is evidence the landing succeeded, not evidence the close-out did.
- A CONCERNS verdict with deferred soft findings (missing automate artifact, undischarged manual tier) is
  exactly the shape that gets landed-then-forgotten — those findings are the close-out's job, so an
  un-run close-out silently drops them.

## The worse variant: a MISSING key, not a stale one (debug-2.2, found 2026-07-27)

**debug-2.2** shipped 2026-07-22 — code, tests, ③ review with 11 findings applied, `/sudo-e2e` 28/28,
all committed at `f60e2c18` — and the close-out never ran. It had **no `debug-2-2-…` key in
`sprint-status.yaml` at all**; the board went `debug-2-1` → `debug-2-3`. Same for debug-2.3 before it,
inside the same epic, so this is **recurring, not a one-off**.

**Why a missing key is worse than a stale one:** every drift check compares keys that *exist*. Nothing
fires on absence. And the one surface that was correct — the story file frontmatter, reading `done` — is
the thing that makes it silent, because nothing reads story frontmatter for planning. The board and the
story file disagreed for five days and no tool could notice.

Downstream, all live for five days: `sprint-dependency-map.md` listed the story under **"Ready to start"**
with `/sudo-write-story-tests` as its next command (i.e. every planning surface was recommending that
already-shipped work be rebuilt from scratch), `epic-debug-2` sat `in-progress`, and `active-context.md`
still carried it as `[READY] … (live bug)`.

**How to apply:** when a story looks unstarted, **grep git before believing the board** — a story file
reading `done` with no matching YAML key is the signature. Conversely when closing out, verify your key
actually exists afterwards (`yaml.safe_load` the file and look it up by name), because writing a line
into a 400-line file and *thinking* you did is exactly how this repeats.

Sibling of [[story-status-flip-contract]] (who flips) and [[close-out-command-is-daniels-signoff]]
(the invocation IS the sign-off — act, never punt).
