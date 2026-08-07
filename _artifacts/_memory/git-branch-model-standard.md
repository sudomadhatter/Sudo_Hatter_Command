---
name: git-branch-model-standard
description: "The dev branch standard across all repos — main_debug is the integration branch, main is protected production."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7cbf0af7-f318-47fc-85c4-cb46222b1d60
  modified: 2026-08-01T03:04:43.388Z
---

Daniel declared (2026-06-27): **`main_debug` → `main` is THE dev standard for every repo** — home base (`Sudo_Hatter_Command`), aviationChat (`AGY_AVIATIONCHAT`), and clean-workspace (`Fresh_Workspace_BMAD`). "all rules need to reflect this."

- All day-to-day work flows through **`main_debug`** (shared integration): `claude/*` session branch → PR → `main_debug`. This is the "one place to send everything."
- **`main` is LIVE PRODUCTION — never work on it, never auto-target it.** Promotion `main_debug` → `main` is Daniel's deliberate, manual decision when he's happy it won't break production.
- Write-approval gate keys on the **owner branches** (`main_debug` + `main`); `main` is extra-protected. Approve a merge into `main_debug` by invoking `/merge_main_debug`.

**Refinement (Daniel, 2026-07-14): "main should NEVER be ahead of main_debug."** The invariant is one-directional — `main_debug` always ⊇ `main`; `main` only ever advances by **fast-forward from `main_debug`**, never by its own commits. If `main` drifts ahead (e.g. a story got committed straight to `main` as its own hash — 8.19.11 did: `main` had `0312e23a`, `main_debug` had the same content as `5ec364ef`), reconcile by `git merge main` INTO `main_debug` (absorbs main's commit; clean when content already matches), then `git checkout main && git merge --ff-only main_debug` so they're identical again. Observed 2026-07-14: a direct `git push origin main` from the owner account **succeeded** (`0312e23a..34381bdd`), so on AGY_AVIATIONCHAT `main` is **convention-protected, not GitHub-branch-protection-blocked for the owner** — the "never work on main" rule is discipline, not a hard gate. What DOES belong on both branches: everything (dev tooling/artifacts included) is fine on `main` — it costs nothing at deploy (see [[agy-cloud-run-deploys-backend-only]]).

**Recurred 2026-07-25 on AGY, and the "clean merge" expectation above is WRONG.** `main` was pushed 3
commits ahead (11.19 Gemini-3.6 + an admin PWA icon) — the operator's own words: *"that was a mistake
pushing only to main."* So this is a **repeating** drift, not a one-time 8.19.11 slip. The reconcile
`git merge origin/main` into `main_debug` did **not** come through clean: the code content was already on
`main_debug` via another path, but `active-context.md` **conflicted**, because both branches had pruned
that file independently. Expect a conflict on the board files (`active-context.md`, `sprint-status.yaml`)
even when every line of *code* already matches — and resolving it is not mechanical, see
[[active-context-pointer-budget]] for the obligation-loss hazard that resolution carries.

**How to apply:** check `git rev-list --left-right --count origin/main...main_debug` at close-out, not just
before a promote. A non-zero left number means main drifted and someone's push bypassed the model; fix it
in the same pass rather than letting the gap grow — AGY was 114 commits the other way when this was found,
which means nothing shipped since the drift is in production.

**Fresh_Workspace_BMAD was fully INVERTED, and repaired 2026-07-31.** Not drift-by-a-few-commits: Fresh's
`main_debug` **died 2026-06-29** while `main` carried 75 commits of real work (every toolkit sync landed on
`main`), so `main` was 75 ahead / `main_debug` 19 ahead, trees differing by 1811 files. **A repo can be
inverted, not just drifted — check the dates, not only the counts.** Before resolving, verify what is
stranded: here nothing was — the 1239 `main_debug`-only files were the pre-6.9.0 BMAD layout
(`.agent/skills`, `_bmad/bmm`) plus the pre-2026-07-14 command surface (`1_update-maps` →
`update-maps-indexes`), and `BMAD_CCPS_workspace_guide.md` had MOVED to `_my_resources/research_docs/`
(check for moves before calling a file lost). Repair that needs **no force-push and discards nothing**:
`git merge --no-commit --no-ff main` into `main_debug` (expect ~100 conflicts), then
`git read-tree -u --reset main` to force the merge result to main's exact tree, then commit — a real merge
commit with both parents and main's byte-identical tree, pushed as a fast-forward. Prefer this over
`git branch -f` + `--force-with-lease` (the auto-mode classifier blocks the force-push anyway, correctly).
⚠️ On Windows, do the merge in a worktree at a SHORT path (`C:/fmd`): a worktree under the scratchpad path
fails with `fatal: Could not reset index file to revision 'HEAD'` — deep BMAD skill paths exceed 260 chars.

**The mechanical CAUSE of main-drift is which branch the shared checkout stands on.** Fresh's inversion
wasn't a policy failure — its hook, `git-policy.md`, and AGENTS.md gates were all present and current
(verified 07-31, identical to the lobby master). It drifted because `git rev-parse --abbrev-ref HEAD` in
the shared checkout said `main`, so every agent and human who opened the repo was already standing there
and `git push` went to `main` by default. The hook gates *approval*, not *destination*. **Diagnostic to run
across repos: `git rev-parse --abbrev-ref HEAD` per checkout — every one should read `main_debug`.** Fixed
07-31 by checking Fresh out on `main_debug` (zero file churn once the trees matched). Note all four repos'
GitHub default branch (`origin/HEAD`) is `main` — **operator-confirmed as deliberate 07-31: the clone lands
on production, and changes go to `main_debug`.** So the checkout-branch fix is per-clone, not inherited.

**That design had one live foot-gun, fixed 2026-07-31.** `/sudo-resume` Step 1 merely *commented* on the
branch (`git status -sb`) and then ran `git pull --ff-only origin main_debug`. On a fresh machine HEAD is
`main`, so that pull fast-forwards **`main` itself** to everything on `main_debug` — an unreviewed promote
of every unshipped commit into production (AGY carries 160+), succeeding **silently** because it genuinely
is a fast-forward. Step 1 now checks HEAD and `git checkout main_debug` BEFORE pulling. **General rule: a
bare `git pull origin main_debug` is only safe once you have verified HEAD is `main_debug`** — never infer
the branch from a status line you printed but did not act on.

**Why:** one consistent, safe model everywhere so production stays deployable and nothing breaks; avoids the per-project drift that had Fresh on a main-only model. Keeping `main` a pure fast-forward of `main_debug` means promotion is always a clean, reviewable advance with no divergence to untangle.

**How to apply:** when handing Daniel commit/push commands, target `main_debug` (or a `claude/*` branch → PR), never `main`. The canonical source of truth now lives in `.agents/rules/git-policy.md` § "Branch model — main_debug → main" (synced to every workspace), enforced by `.agents/hooks/require-push-approval.py` (gates both branches, deployed to every `.claude/hooks/` by `/sync-agents`). See also [[git-policy-no-self-commit]].

**Submodule gitlinks are INVISIBLE in the lobby (found 2026-08-06).** `.gitmodules` sets
`ignore = all` on all eight `Projects/*` entries, so the lobby's `git status` structurally cannot
report gitlink drift — it reads perfectly clean while the recorded pointers lag behind commits that
are already pushed. Only `git submodule status` shows it (a leading `+` = the working tree is ahead
of the recorded sha). This is deliberate config (it keeps child-repo churn out of the lobby's
status); do NOT "fix" it. It does mean the pointers move ONLY when someone explicitly
`git add Projects/<name>`, and a `git push` in a submodule never bumps the superproject.

**Why it bites:** a fresh clone plus `git submodule update --init` checks out the RECORDED sha, so
stale gitlinks silently hand a new machine older code — the exact failure the migration kit exists
to prevent.

**How to apply:** after committing inside any submodule, run `git submodule status | grep '^+'` in
the lobby and `git add` every path it lists. Never trust the lobby's `git status` for this.
