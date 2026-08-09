---
IsArtifact: true
ArtifactMetadata:
  title: Worktree-per-story · agents commit and land their own stories
  type: walkthrough
  date: 2026-07-23
---

# Walkthrough — Agents work in worktrees, commit, and land their own stories

**Built:** 2026-07-22 → 07-23 · **Repos touched:** lobby, `AGY_AVIATIONCHAT`, `Fresh_Workspace_BMAD`
**Plan:** [implementation_plan.md](implementation_plan.md)

## What changed, in one line

Agents were forbidden to commit or push. Now they work in a worktree per story, commit freely inside
it, and land the story on `main_debug` as **one clean push** at Daniel's sign-off. `main` is unchanged —
still only reachable when Daniel asks directly or runs `/sudo-push-e2e`.

## The problem this fixes

`6ff0aad` — the last push before this work — is titled *"formalize TEA testing framework"* and actually
contains four unrelated sessions: the `sudo-create-epic-sprint` rename, the pipeline-conversion-and-SOP
session (plan still in flight), the AGY epic-21 demo-portal brief, and a doc-graph regen. `aab6491`
before it names three things joined by *"plus."* A commit can only be pushed once, so whoever pushed
last inherited every other team's dirty files and the message could only honestly describe one of them.

## The new lane

```
pre-flight: HEAD is main_debug
   ├─ EnterWorktree → .claude/worktrees/<slug>/ on claude/<slug>
   ├─ agent commits FREELY inside it (explicit paths; git add -A still banned)
   └─ /sudo-update-sprint-memory  ← Daniel's sign-off
         Steps 1–6 (story → done, board, learnings, prune) run INSIDE the worktree,
         so sprint-status.yaml + active-context edits ride the branch
         Step 7 — LAND IT:
            git fetch origin main_debug
            git merge origin/main_debug      # absorb INSIDE the worktree
            git push origin claude/<slug>    # free — rollback point
            git push origin HEAD:main_debug  # THE landing (hook prompts once)
```

## Decisions made during the build

**The landing merges from inside the worktree, never the shared checkout.** The obvious implementation —
`git checkout main_debug && git merge && git push` — is exactly wrong here, because the shared checkout
is where the other teams' uncommitted work lives; that merge either refuses or drags their files through
the landing. Pulling `origin/main_debug` *into* the story branch and pushing `HEAD:main_debug` never
touches the shared tree. Conflicts surface inside the isolated worktree, where the agent stops and
reports and nobody else's tree moves.

**`worktree.baseRef` set to `head`, because there is no third option.** The setting accepts only `fresh`
(= `origin/<default-branch>` = **`origin/main`**, the default, and the reason worktrees were branching
off production) and `head`. There is no "name a branch" value. `head` is correct as long as HEAD is
`main_debug` when the worktree opens, so `worktree-per-story.md` makes that a stated pre-flight check.

**The commit gate asks rather than denies** (Daniel's call, asked mid-build). The hook prompts instead of
hard-blocking, so Daniel keeps in-session override authority. Nothing in this design can hard-block him
in any case — see below.

**Cut from the first draft, as over-engineering:** a `git merge` gate, an `EnterWorktree` base-guard, and
the extra hook matcher. The hook still matches `Bash` only and gained exactly one conditional.

## Files changed

**Lobby master (`.agents/`)**

| File | Change |
|---|---|
| `rules/git-policy.md` | **Rewritten.** Repaired the corruption (its body appeared twice — truncated dupe at 1–77 ahead of the real copy at 79–169) and replaced the "never run git yourself" default with the worktree lane + a destination-keyed write gate. |
| `rules/worktree-per-story.md` | **NEW** protocol-tier rule — trigger, exemptions, the four gates (G1 location · G2 scope · G3 push · G4 `main`), close-out, hard stops. |
| `rules/INDEX.md` | Added to the protocol tier + a row; rewrote the now-false `git-policy` row. |
| `rules/constitution.md` | Hard stop L19 → the gate is *where a write lands*, not whether you run git. |
| `rules/artifacts-always-first.md` | ×4 — "Your Actions" is now what landed (branch + commits), not a `git add` block. |
| `rules/bmad_code_review_sudo_fix.md` | L47 told agents to remind Daniel with `git add -A && git commit && git push` — a live violation of the old policy too. |
| `commands/` + `workflows/sudo-update-sprint-memory.md` | **New Step 7 — Land the story**, incl. the `claude/*` precondition and the merge-inside-the-worktree sequence. Fixed the two stale "agents never commit" lines + the frontmatter description. |
| `commands/sudo-dev-story-tests.md` (+ `_AP`, + workflow) · `commands/sudo-code-review.md` (+ `_AP`, + workflow) · `commands/sudo-self-audit_AP.md` | Commit inside the worktree; never land — Step 7 owns that. |
| `bmad/custom/bmad-dev-story.toml` · `bmad-quick-dev.toml` | "Your Actions" wording, ×2 each. |
| `commands/` + `workflows/update-maps-indexes.md` | Kept hand-landing (multi-repo sweep, no single story branch) but stopped citing a `git-policy` default that no longer exists. |
| `hooks/require-push-approval.py` | Rewritten as a protected-branch write gate: pushes at `main_debug`/`main` still ask; **new** — `git commit` while HEAD is `main_debug`/`main` asks. Fails **open**. |

**Wiring**

| File | Change |
|---|---|
| `.claude/settings.json` ×3 (lobby, AGY, Fresh) | `"worktree": {"baseRef": "head"}` + rewrote the SessionStart boot string that injected *"never commit/push yourself"* into every session. |
| `.claude/hooks/` ×3 + `.agents/hooks/` ×3 | Hook deployed to all six copies. |
| `AGENTS.md` ×3 | Lobby §6 (new WORKTREE GATE + rewritten GIT WRITE APPROVAL); `AGY_AVIATIONCHAT` L95 (*"agents **NEVER commit/push**"*); `Fresh_Workspace_BMAD` L75–84. |
| `.opencode/commands/` ×3 | The three story-flow commands re-mirrored. |

**Found during the sweep, not in the plan**

- `AGY_AVIATIONCHAT/.agents/rules/constitution.project.md:46` — restated the old desktop default.
- `Fresh_Workspace_BMAD/.agents/rules/bmad_code_review_fast_path.md:73` — another
  `git add -A && … && git push` reminder, in the template new projects clone from.

## What fought back

**The drift check was wrong before it was right.** Comparing project copies against
`git show HEAD:<path>` reported all 32 files as DRIFTED — including files a direct `diff` had already
proven identical. Cause: `git show` emits LF, the working tree is CRLF. Normalizing with `tr -d '\r'`
showed the real answer: everything in sync except two files. Had I trusted the first result I'd have
skipped the entire propagation and reported a false "your projects have all diverged."

**Fresh's guard tomls were behind, not ahead.** They were the only genuine drift — and they turned out
to be *older* than the lobby, still referencing the retired `your-action-required.md` and the deleted
`_claude_artifacts/` store (the lobby fixed that on 2026-06-27). Since Fresh is the living template every
new project clones, I brought them current rather than preserving the staleness. **This is a bigger
change than the one-line "Your Actions" edit** the plan called for — flagged below.

## Verification (actual output)

Hook, 7 synthetic payloads against a real throwaway worktree (`claude/hook-gate-test`, created and
removed during the test):

```
push origin main_debug                            -> ASK
push origin HEAD:main_debug                       -> ASK
push origin claude/my-story                       -> PASS
commit IN shared checkout (HEAD=main_debug)       -> ASK
commit IN worktree (HEAD=claude/*)                -> PASS
commit outside any repo (fail-open)               -> PASS
git status (unrelated)                            -> PASS
```

Re-tested afterwards against the *deployed* `.claude/hooks/` copy that actually runs: `commit on
main_debug -> ASK`, `push claude/x -> PASS`.

```
git-policy.md frontmatter delimiters: 2   (was 4 — corruption repaired)
'# Git Policy' headings:              1   (was 2)

settings.json  OK baseRef=head  .claude/settings.json
settings.json  OK baseRef=head  Projects/AGY_AVIATIONCHAT/.claude/settings.json
settings.json  OK baseRef=head  Projects/Fresh_Workspace_BMAD/.claude/settings.json

worktree-per-story rule present + routed:  lobby yes/2 · AGY yes/2 · Fresh yes/2
parity: all 18 shared files identical across all 3 repos
```

Final sweep for the old law (`never commit/push`, `agents never commit`, `git add -A &&`,
`hand Daniel the exact command`) across all three repos: **CLEAN** — the only remaining hit is the
deliberate autopilot exception.

## Not proven yet

**No story has run this lane end to end.** The hook is tested, the JSON parses, the prose is consistent
— but "worktree opened → commits made → one clean landing on `main_debug`" has not happened once. Until
it does this is written policy, not proven policy. The next story is the real test.

## Task Checklist

- [x] `git-policy.md` — corruption repaired + rewritten to the worktree lane
- [x] `worktree-per-story.md` — new protocol-tier rule
- [x] `rules/INDEX.md` — protocol tier + row
- [x] Kill-list sweep — constitution, artifacts-always-first ×4, bmad_code_review_sudo_fix
- [x] Hook — commit-on-protected-HEAD gate, 7 payloads tested, 6 copies deployed
- [x] `settings.json` ×3 — `baseRef: head` + SessionStart boot string
- [x] `/sudo-update-sprint-memory` — Step 7 landing + 2 stale lines + description
- [x] Story-flow commands (6) + workflow twins + 2 guard tomls
- [x] `AGENTS.md` ×3 GATES sections
- [x] Propagation to AGY + Fresh — 18 files, parity verified
- [x] 2 unplanned survivors found and fixed (AGY `constitution.project.md`, Fresh `bmad_code_review_fast_path.md`)
- [ ] **Live proof** — deferred to the next story; cannot be done in this session

## Your Actions

**Nothing was committed or pushed.** This session ran in the lobby, not a worktree, because you said it
lands by your hand. Everything sits uncommitted in the working tree.

Three things need your decision:

1. **`B-L-WorldWide` was left untouched.** It has a `.opencode/commands/sudo-update-sprint-memory.md`
   carrying the old "agents never commit" law. You named AGY and Fresh; I didn't widen to a fourth repo
   without asking. Say the word and it takes two minutes.
2. **Fresh's two guard tomls got more than the planned one-line edit** — they were stale in ways beyond
   this task (retired `your-action-required.md`, deleted `_claude_artifacts/` store) and I brought them
   fully current. Revert if you'd rather they stay as they were.
3. **`mobile-mode.md` is untouched**, per your Rule 4. One clause in it still points at the
   "hand Daniel the command" default that no longer exists — cosmetic, behavior unaffected.

The landing command, when you want it:

```bash
git add <explicit paths>          # never -A; this tree holds other sessions' work
git diff --cached --stat          # verify before committing
git commit -m "feat(agents): worktree-per-story + agents land their own stories on main_debug"
git push origin main_debug
```
