---
IsArtifact: true
ArtifactMetadata:
  title: SCC-77 — the main write gate
  type: implementation_plan
  date: 2026-08-10
---

# SCC-77 — Enforce the `main` write gate

**Branch** `chore/SCC-77-main-write-gate` · **Lane** LOCAL · **Cut from** `main` @ `9a6a026`
**Reconciled onto** `main` @ `48e95c5` (73 commits absorbed 2026-08-11 — see the walkthrough)

> **Status: AS BUILT.** This document was approved as a plan on 2026-08-10 and has been rewritten to
> describe what actually shipped. Where the build diverged from the plan, the divergence is called out
> in-place rather than quietly edited over — those are the entries worth reading.

---

## The problem

`git-policy.md` documented a `main` write gate. **It had never executed once on this machine.**

| Layer | Claimed | Found |
|---|---|---|
| `pre-push` git hook | — | **did not exist**, in either repo |
| `require-push-approval.py` | "forces the approval prompt on any `git push` targeting `main`" | wired as `powershell -Command "python …"`; this Mac has **neither** — only `pwsh`, `python3` → **exit 127, silent** |
| 4× SessionStart hooks | continuity · drift · INDEX · journal | same defect, all dead |
| AGY `.claude/hooks/` | — | directory absent |
| `core.hooksPath` (SCC) | — | **absolute** — cannot survive a clone to the PC |

That is the whole explanation for six merges riding one sign-off (SCC-64 → SCC-69). The rule was
enforced by reading, which is exactly the weakness it describes.

## The door set (operator ruling, 2026-08-10)

Two commands plus the operator. This is what `git-policy.md`, both command bodies, and the ticket
already said — **no rule doc's door table needed changing.**

| Destination | Doors |
|---|---|
| `main` | `/cicd-push-e2e` · `/smh-close-task-merge-tree` · the operator's direct "approved" |
| epic branch | `/cicd-update-sprint-memory` — **never `main`** |

The only surface carrying a third-door reading was the SOP's SCC-71 block. Correcting it was in
scope; by the time of the reconcile, SCC-91's restructure had **already removed** that sentence.

## Architecture — two layers, one authoritative

**Layer A — `.githooks/pre-push`. This is the gate.** Pure POSIX `sh`. Runs on both machines, under
every agent platform, and in the operator's own terminal.

**Layer B — the Claude `PreToolUse` hook. UX only.** Repaired, but nothing depends on it. If it dies
again the gate still holds.

> ⭐ **The design rule that falls out of the bug:** the enforcement layer may not depend on the class
> of thing that broke it. That is why Layer A has no interpreter in its path at all.

## The token contract

**Path** `$(git rev-parse --git-common-dir)/main-push-approval` — the *common* dir, so every worktree
shares exactly one token and a sign-off cannot be minted in one lane and spent in another; under
`.git/`, so it never travels with a clone and can never land in a commit.

**Fields** `branch` · `tip` (sha at mint) · `command` · `key` · `minted` (epoch)

**Gate order** — each step its own refusal message:

| # | Check | Refused when |
|---|---|---|
| 1 | armed | `MAIN-PUSH-ENFORCE` deleted or `DISABLE` present → passes through |
| 2 | destination | not `refs/heads/main` (whole-ref) → exits 0 immediately |
| 3 | exists | no token |
| 4 | fresh | minted > 30 min ago |
| 5 | **same commit** | **token names one sha, push carries another** |
| 6 | delete | anything that would delete `main` — unconditional |

**Every refusal also discards the token**, so a failed sign-off is spent rather than left to match a
later push by accident. On success the token is consumed *before* the push — there is no `post-push`
hook, so that is the only available order, and it fails safe.

---

## Files as built

### New

| Path | Role |
|---|---|
| `.githooks/pre-push` | dispatcher; carries the SCC-32 worktree guard (missing script → warn + allow) |
| `.agents/scripts/git-hooks/pre-push-main-approval.sh` | the gate |
| `.agents/scripts/git-hooks/mint-push-token.sh` | the minter |
| `.agents/scripts/git-hooks/MAIN-PUSH-ENFORCE` | tracked arm flag |
| `.agents/scripts/tests/test_main_push_gate.py` | 36 assertions; auto-discovered by `run_all.py` |
| `.agents/hooks/run-hook.sh` (+ `.claude/hooks/` copy) | interpreter shim that **announces** rather than exiting 127 |
| `.agents/hooks/session-start-context.sh` | inline PowerShell hook ported to `sh` |

### Modified

| Path | Change |
|---|---|
| `.claude/settings.json` | all 5 hook commands off `powershell`/`python` |
| `.agents/commands/cicd-push-e2e.md` | mint step before Step 4's push |
| `.agents/commands/smh-close-task-merge-tree.md` | mint step before Step 3's push |
| `.agents/rules/git-policy.md` | Enforcement rewritten; the honest limits put in writing; cross-ref to SCC-97 |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | the built gate documented at both stale sites |
| `_artifacts/_memory/git-branch-model-standard.md` + `MEMORY.md` | the branch model corrected |
| *(git config)* | `core.hooksPath` absolute → **relative** |

---

## Divergences from the approved plan — and why

1. **The minter is `sh`, not Python.** The plan said `.agents/scripts/mint_push_token.py`. Making the
   *enforcement* path depend on an interpreter would reproduce the exact bug inside the fix. Now
   nothing in the gate path needs Python at all.
2. **`run-hook.sh` and `session-start-context.sh` were added.** The plan treated the settings repair
   as a rewiring job. Two of the five hooks were PowerShell *logic*, not just a bad interpreter name,
   so they had to be ported. The shim also fixes the *class* of bug: no hook can exit 127 silently
   again.
3. **Defect 6 was in a different file than stated.** The false *"AGY keeps its own identical copy"*
   sentence is at **line 67 of the memory file**, not `git-policy.md:67` — two line-67s were conflated
   during the survey. `git-policy.md` never carried the claim. Fixed in the right place.
4. **A `.gitignore` fix was made, then superseded.** `**/node_modules/` (trailing slash) matches
   directories only, but worktree assets are *symlinks* — so `task_preflight.py` counted the link as
   uncommitted and **blocked a clean lane**. Fixed here; at the reconcile, SCC-73 turned out to have
   found the same bug independently and fixed it better (keeping both forms). **Took theirs.**
5. **One SOP fix became unnecessary.** SCC-91's restructure had already deleted the three-door
   sentence. Independent confirmation the reading was right.
6. **SCC-97 landed while parked, and reinforces this.** It asks you to assert `HEAD` is `main`
   immediately before merging. `mint-push-token.sh` already **refuses to mint unless `HEAD` is
   `main`**, and runs between merge and push — so on the two door lanes that assertion is mechanical.
   Cross-referenced in `git-policy.md`.

---

## Acceptance — the checkable list

Authority: SCC-77's `ACCEPTANCE` block. Every item names the assertion that proves it.

| # | Item | Proven by |
|---|---|---|
| 1 | `pre-push` exists, executable, refuses an unapproved push to `main` — by a **real** `git push`, not only stdin | `test_main_push_gate.py` — installed ×6, *"REAL git push to main is refused with no token"*, *"nothing reached the remote"* |
| 2 | Token single-use: consumed on success **and** discarded on every refusal | *"the token is consumed"*, *"replaying the same push is refused"*, *"a refused token is discarded too"* |
| 3 | Token for a different sha is refused (the SCC-71 shape) | *"token minted for another sha is refused"* |
| 4 | Stale + malformed refused; deleting `main` refused unconditionally | *"token older than 30 min…"*, *"malformed token…"*, *"deleting main is always refused"* |
| 5 | Only `refs/heads/main`, whole-ref | *"non-main ref passes"*, *"`epic/main-fix` does not trip the match"* |
| 6 | All three disarm paths work and are loud | *"disarmed … passes through"*, *"DISABLE kill switch passes through"*; `--no-verify` documented in the gate header, SOP and `git-policy.md` |
| 7 | Both doors mint after the merge, before the push; `/cicd-update-sprint-memory` does not | mint steps in both command bodies; *"minter refuses when HEAD is not main"*; *"the refusal does NOT name update-sprint-memory as a door"* |
| 8 | No interpreter anywhere in the gate path | `pre-push`, the gate and the minter are `sh`, `sh -n` clean; no `python`/`powershell` token in any of the three |
| 9 | `settings.json` names no single-platform binary; all 5 hooks execute; a hook that can't run announces it | *"no hook command is bound to one platform's binaries"*; all four SessionStart hooks run (hook 3 surfaced real INDEX drift); `run-hook.sh` prints and exits 0 |
| 10 | `core.hooksPath` set **and** relative | *"core.hooksPath is set"*, *"is RELATIVE"*, *"resolves to a dir holding pre-push"* |
| 11 | `run_all.py` green with the new file; lint 0 errors | `run_all.py` **14/14 exit 0**; `workflow_lint --toolkit-only` **0 errors, 0 warnings, exit 0** |
| 12 | SOP moves in the same commit; `git-policy.md` carries the canonical statement incl. what it does *not* buy | armed `sop_currency` passed each commit; `test_sops_prds_folder.py` **57/57**; limits written into both |

**Out of scope, deliberately:** AGY (own AVCH ticket — enforcement is repo-local); `gh pr merge` and
the GitHub web UI (SCC-75); making the token unforgeable (explicitly *not* a goal — see below).

## What this does not buy — stated, not hidden

**An agent can write files, so an agent can forge a token.** This is not a security boundary against a
determined agent and must not be described as one. It converts a *silent* violation into a
*deliberate, traceable* one, and it closes the real SCC-71 failure: a close-out command whose body
stays in context and still reads valid on task six. Written into `git-policy.md`, the SOP, the gate's
own header, and the ticket.

## Verification

```
run_all.py                    14/14  exit 0      (13/13 on main + this lane's file)
workflow_lint --toolkit-only  0 errors, 0 warnings, exit 0
test_main_push_gate.py        36/36  exit 0
test_sops_prds_folder.py      57/57  exit 0
task_preflight --expect-key   clear to close out and merge · LANE LOCAL
```

Plus the live proof on this repo: `git push` of the chore branch passes freely; `git push origin
HEAD:main` is refused with no token.

## Still owed — nothing minted, placement is the operator's

- **SCC-74** — `git_walkthrough_settings.md` still names `/cicd-push-e2e` as `main`'s only door.
- **SCC-75** — one child: `claude/incident-<id>` vs `task_preflight.py`'s `incident/` guard; the
  incident lane lands via GitHub PR; `gh pr merge` ungated.
- **New AVCH ticket** — AGY needs this gate; it does not propagate.
