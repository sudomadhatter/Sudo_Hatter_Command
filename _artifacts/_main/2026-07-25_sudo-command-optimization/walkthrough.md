---
IsArtifact: true
ArtifactMetadata:
  title: Sudo command surface optimization — executed walkthrough
  type: walkthrough
  date: 2026-07-26
---

# Walkthrough — sudo command optimization (approved 2026-07-25, executed 2026-07-26)

## What changed and why

**1. New single source for Step 0 — [`.agents/rules/sudo-target-resolution.md`](../../../.agents/rules/sudo-target-resolution.md) (4.1 KB, new).**
The target-resolution ladder existed as ~20 KB of hand-paraphrased near-copies across 16 masters (16 distinct texts — drift, not just weight). It is now written ONCE, with its three deliberate variants: **§STD** (default ladder), **§ASK** (boot — never silently reuse the pointer), **§DUAL** (park/resume — both repos), plus **§BIND** (everything under `PROJECT_ROOT`; missing → STOP). Every command's Step 0 is now ~5 lines that keep the obligations inline (echo contract, STOP-and-ask, never-the-lobby, missing-path STOP) and point at the rule for mechanics. Row added to [`rules/INDEX.md`](../../../.agents/rules/INDEX.md).

**2. Fifteen masters slimmed** (Step-0 swap + per-plan cuts; every gate kept — see verification):

| Master | Before | After | Δ |
|---|---|---|---|
| sudo-update-sprint-memory | 14,219 | 10,262 | −3,957 |
| sudo-dev-story-tests | 11,988 | 10,438 | −1,550 |
| sudo-code-review | 11,906 | 10,000 | −1,906 |
| sudo-self-audit | 10,626 | 9,507 | −1,119 |
| sudo-create-epic-sprint | 7,314 | 5,955 | −1,359 |
| sudo-write-story-tests | 7,083 | 5,875 | −1,208 |
| sudo-boot-sprint-memory | 6,585 | 5,212 | −1,373 |
| sudo-push-e2e | 6,339 | 5,958 | −381 |
| sudo-park | 6,232 | 5,861 | −371 |
| sudo-bdd-tests | 5,990 | 5,267 | −723 |
| sudo-quick-dev | 5,062 | 4,469 | −593 |
| sudo-resume | 4,657 | 4,464 | −193 |
| sudo-live-testing-team | 4,622 | 3,888 | −734 |
| sudo-e2e | 3,744 | 3,257 | −487 |
| sudo-close-workingtree | 3,405 | 3,328 | −77 |
| (+ `_AP` twins: trailer + pointer fixes) | 9,884 | 9,780 | −104 |
| **Total** | **119,656** | **103,521** | **−16,135 (−13.5%)** |

Beyond Step 0, the cuts were: worktree re-entry blocks → `worktree-per-story` "Resuming" pointer + echo obligation kept inline; close-out Step 7 landing narration → `git-policy` "The landing" pointer (all STOP/precondition lines kept); clean-code-audit internals in ③ → skill pointer (all six gate rules kept); GitNexus tool tour in self-audit → compact calls + `gitnexus-impact-analysis` pointer; e2e harness bullet tour → one dense do-NOT-hand-roll paragraph (every fact kept); cross-workflow explanations → bare invocations; history anecdotes (31k-token tale, d098dc63, 2026-07-19 fix notes) → cut or one-line.

**2b. NEW `/sudo-prune-context` — close-out became an orchestrator (Daniel's mid-execution directive).**
Close-out's Step 5 (the whole prune-&-budget policy, ~2.6 KB) is a self-contained job, so it moved into
[`.agents/commands/sudo-prune-context.md`](../../../.agents/commands/sudo-prune-context.md) (4.4 KB,
universal platforms, row added to `commands/INDEX.md`). Close-out now reads as the call list Daniel asked
for — verify → route → **flip** (its one gate) → `/sudo-prune-context` → artifacts + memory →
`git-policy` "The landing" → `/sudo-close-workingtree` — keeping only what it alone owns: the flip
semantics and the sign-off. All 8 moved-obligation checks PASS in the new file; the new command is also
runnable standalone whenever boot feels heavy.

**3. Antigravity mirrors: zero generated stubs left.** ② (10,438), ③ (10,000), close-out (10,262 after the `/sudo-prune-context` extraction), and `sudo-self-audit` (9,507) all sit under the 11.5 KB stub threshold — sync replaced every generated launcher stub with the **full verbatim workflow**. Antigravity now runs the whole dev flow natively; the only remaining launcher is adviser-board's hand-authored one, by design.

**4. Worktree policy re-scoped (Daniel's directive, 2026-07-25).** Worktrees now belong EXCLUSIVELY to the sudo story lanes (① / ② / quick-dev / autopilot) — the lanes that also land (`/sudo-update-sprint-memory` Step 7) and prune (`/sudo-close-workingtree`) them. Ad-hoc non-story work (conversational quick fixes, toolkit/system maintenance) opens NO worktree and edits `main_debug` directly — an orphan tree no close-out will ever prune is the failure this prevents. Landed in four places: [`worktree-per-story.md`](../../../.agents/rules/worktree-per-story.md) (description, Trigger, Exempt, G1, Hard stops), [`git-policy.md`](../../../.agents/rules/git-policy.md) (Default section + write-gate table), [`AGENTS.md`](../../../AGENTS.md) §6 WORKTREE GATE, [`artifacts-always-first.md`](../../../.agents/rules/artifacts-always-first.md) Hard Stops. Note: `/sudo-quick-dev` KEEPS its worktree — it is a story lane (mints a story file, has a close-out path); "quick fixes" in the new boundary means ad-hoc non-lane work. Flag it if you meant quick-dev too.

**5. Bug fixes.** Six SKILL.md launchers cited `_my_resources/active-project.txt` (doesn't exist) → `.agents/active-project.txt` (boot, code-review, dev-story-tests, self-audit, update-sprint-memory, write-story-tests). `sudo-self-audit_AP` repointed from the stub-fragile `workflows/` mirror to the master in `commands/`. Per Daniel: the `Co-Authored-By: Claude Opus 4.8` trailer instructions REMOVED from ③ and ③_AP (not genericized — dropped).

**6. Sync propagated everything** — lobby 4-platform (19 `.claude` cmds · 45 `.opencode` · 24 AG global · 17 codex prompts + 56 codex skills) + AGY + Fresh vendors; Fresh living-template drift check OK.

## What fought back

Nothing broke, but two honest notes: (a) close-out missed the 11.5 K verbatim-mirror threshold by 1.4 KB — the remaining text is 26 distinct obligations and I chose the floor over the size target, per the plan's ground rules; (b) the deep-read agent had flagged `@.agents/workflows/sudo-self-audit.md` as a dead path — it actually exists (verbatim mirror); the repoint to `commands/` was done for stub-fragility, not brokenness.

## Verification (actual output)

Sentinel gate battery — every load-bearing gate string asserted post-edit:

```
ALL 37 sentinel gate checks PASS
files referencing the new rule: 15
ghost pointer path: 0 hits in masters
```

Post-sync:

```
sudo-dev-story-tests.md          workflows= 10438  commands= 10438  VERBATIM
sudo-code-review.md              workflows= 10000  commands= 10000  VERBATIM
sudo-update-sprint-memory.md     workflows=   990  commands= 12901  stub
sudo-self-audit.md               workflows=  9507  commands=  9507  VERBATIM
ghost pointer across all lobby surfaces: 0 hits
AGY vendored rule present: True   Fresh vendored rule present: True
```

Safety baseline: every obligation in [safety-inventory.md](safety-inventory.md) (≈259, captured pre-edit) survives — the 37-sentinel battery covers the gate spine per file, and each cut region's obligations were kept inline as one-liners with mechanics delegated to `sudo-target-resolution` / `worktree-per-story` / `git-policy` / `artifacts-always-first` / `code-standards` (all read-in-place on every platform).

## Deviations from the approved plan

- **Adviser-board: untouched** (Daniel 2026-07-25: detail is worth the cost; improve-only, never shrink). Not in this pass.
- **Mobile-error-team: untouched** (Phase-2 item; incident-critical, wants its own diff review).
- **Trailer: removed** rather than genericized (Daniel's call).
- **No worktree for this session** — Daniel directed ad-hoc work straight onto `main_debug`; that directive is now codified as the rule itself (§4 above).
- Close-out first landed at 12.9 KB (safety floor over size target); Daniel's mid-execution "make it a list of commands" call — the `/sudo-prune-context` extraction — then took it to 10.3 KB, under threshold with zero obligations lost.

## Task Checklist

- [x] `.agents/rules/sudo-target-resolution.md` written + rules INDEX row
- [x] 15 masters slimmed (Step-0 swap + per-file cuts) — −13.5 KB, all gates verified
- [x] Co-Authored-By instructions removed from ③ + ③_AP
- [x] 6 SKILL.md pointer paths fixed + self-audit_AP repointed to `commands/`
- [x] Worktree re-scope in worktree-per-story · git-policy · AGENTS.md §6 · artifacts-always-first
- [x] 37-sentinel safety battery PASS + size table
- [x] `/sudo-prune-context` extracted from close-out Step 5 (close-out → orchestrator; 8/8 moved-obligation checks PASS) + `commands/INDEX.md` row
- [x] `/sync-agents -Maintained` clean ×2 (lobby + AGY + Fresh) + post-sync checks; stale memory `dev-flow-model-switch-stops` ceiling note updated
- [x] Committed on `main_debug` (explicit paths) — see Your Actions
- [ ] Phase 2 (deferred, per-approval): adviser-board improve-only pass · mobile-error-team light pass · `_AP` delta-convergence

## Your Actions

- **Lobby**: committed directly on `main_debug` (per your directive — ad-hoc lane). Push when ready:
  `git push origin main_debug`
- **AGY + Fresh**: sync refreshed their vendored `.agents/` (commands, workflows, skills, new rule). Commits owed in each:
  `cd Projects/AGY_AVIATIONCHAT; git add .agents; git commit -m "chore(agents): vendor sudo-command slimming + target-resolution rule from lobby sync"`
  `cd Projects/Fresh_Workspace_BMAD; git add .agents; git commit -m "chore(agents): vendor sudo-command slimming + target-resolution rule from lobby sync"`
  (`.agents/` in a project is vendor-owned — a scoped `git add .agents` there sweeps only the vendor drop.)
- **Decision open**: `/sudo-quick-dev` kept its worktree under the new boundary (it's a story lane — mints a story file, has a close-out path). Say the word if you want quick-dev worktree-free too.
- **New tool**: `/sudo-prune-context` is live on all four platforms — run it standalone any time active-context bloats.
