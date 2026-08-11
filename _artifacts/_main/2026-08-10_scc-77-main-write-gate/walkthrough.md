---
IsArtifact: true
ArtifactMetadata:
  title: SCC-77 — the main write gate
  type: walkthrough
  date: 2026-08-10
---

# SCC-77 — the `main` write gate

**Branch** `chore/SCC-77-main-write-gate` · **Lane** LOCAL · **Base** `main` @ `9a6a026`
**Reconciled onto** `main` @ `48e95c5` (73 commits, 2026-08-11)

---

## Task Checklist

- [x] Establish the real door set from primary sources, not from either agent's prose
- [x] `pre-push` gate + dispatcher + tracked arm flag (pure `sh`)
- [x] Single-use token: minter + contract + consumption
- [x] Wire both `main` doors to mint at their sign-off step
- [x] Repair the exit-127 hook wiring (all 5 hooks)
- [x] `core.hooksPath` absolute → relative
- [x] Test suite, incl. a real `git push` at a real remote
- [x] Docs: `git-policy.md`, the SOP, the memory store
- [x] Rewrite the SCC-77 Jira description (it named two retired commands)
- [ ] Merge — **operator's, not mine**

---

## What was actually wrong

The gate `git-policy.md` documented **had never executed once on this machine.**

| Layer | Claimed | Found 2026-08-10 |
|---|---|---|
| `pre-push` git hook | — | **did not exist**, in either repo |
| `require-push-approval.py` | "forces the approval prompt on any `git push` targeting `main`" | wired as `powershell -Command "python …"`; this Mac has **neither** — only `pwsh`, `python3` → **exit 127, silent** |
| 4× SessionStart hooks | continuity, drift, INDEX, journal | same defect, all dead |
| AGY `.claude/hooks/` | — | directory absent |
| `core.hooksPath` (SCC) | — | **absolute**, where AGY's is relative — see the correction below |

That is the whole explanation for six merges riding one sign-off (SCC-64 → SCC-69). Nothing was
ever there to stop them. The rule was enforced by reading, which is the weakness it describes.

**Evidence the repair works:** the moment the hooks could run, SessionStart hook 3 immediately
reported real depth-3 INDEX drift that had been invisible for days. It had been failing silently.

## The door set — and the misreading that started this

Ruled by the operator 2026-08-10, matching what `git-policy.md:70`, both command bodies, and the
ticket already said:

| Destination | Doors |
|---|---|
| `main` | `/cicd-push-e2e` · `/smh-close-task-merge-tree` · the operator's direct "approved" |
| epic branch | `/cicd-update-sprint-memory` — **never `main`** |

`/cicd-update-sprint-memory` pushes to `epic/<KEY>-<slug>` at
[cicd-update-sprint-memory.md:255](../../../.agents/commands/cicd-update-sprint-memory.md#L255) and
says outright at
[:263](../../../.agents/commands/cicd-update-sprint-memory.md#L263) that *"`main` is untouched."*

The **only** surface carrying the wrong model was the SOP's SCC-71 block: it makes the
one-typing-one-merge point about both close-outs, and the sentence after it (*"Every other merge to
`main` …"*) turns that into a door list. That is what sent the previous attempt building a gate
around `epic/*` — branches nobody pushes to. Corrected in place.

## The design

**Two layers, and only the first counts.** The gate is `.githooks/pre-push` — pure POSIX `sh`, no
Python, no PowerShell, no interpreter probe. The Claude `PreToolUse` hook is repaired too, but
nothing depends on it. A gate that rests on one platform's binaries is what just failed, so the
replacement rests on nothing.

**The token** lives at `$(git rev-parse --git-common-dir)/main-push-approval` — the *common* dir, so
every worktree on the machine shares exactly one and a sign-off can't be minted in one lane and spent
in another; under `.git/`, so it never travels and can never be committed.

Six checks, each with its own refusal message: armed → destination (whole-ref, so `epic/main-fix`
never trips) → exists → fresh (30 min) → same commit → **one merge** → **named branch** →
never delete or rewind `main`.

⛔ **The first cut of this gate did not stop SCC-71, and this document claimed it did.** The
adversarial review reproduced it: merge six branches into `main` locally, mint once, push once — the
sha check passes the whole way, six merges land on one approval, and the approval line names one of
them. **A token authorises a push; what needs authorising is a merge.** That is the reasoning error,
and it is worth recording because it looks correct right up until someone batches.

⭐ **What actually holds the line is `one merge`:** `main` must advance by exactly one merge commit
sitting directly on top of what the remote already has, and that merge's second parent must be the
branch the token names. Batching breaks the first (the previous merge sits in between); a force-push
rewind breaks it too, which closed a second hole — `delete` was refused while `reset --hard` +
`--force`, the same destructive outcome, was approved. The minter refuses the batch as well, so the
error surfaces where the message can still name the fix.

Every refusal also **discards** the token, so a failed sign-off is spent rather than left lying
around for a later push to match by accident.

The token is consumed *before* the push. There is no `post-push` hook, so that is the only available
order — and it fails safe: a rejected push (remote moved) needs a fresh sign-off, which is right,
because re-running the door command re-runs the preflight against the remote that moved.

## The reconcile — 73 commits absorbed (2026-08-11)

This lane was parked while five other Task lanes landed. `origin/main` moved 73 commits. **Every
file of the gate itself is a new file, so all of it merged clean**; three files conflicted.

| Conflict | Resolution |
|---|---|
| `.gitignore` | **Took theirs.** SCC-73 hit the identical symlink-vs-directory bug independently and fixed it *better* — keeping both the slashed and slashless forms instead of replacing one. Mine was superseded; the finding below still stands. |
| `MEMORY.md` | **Union.** My rewritten branch-model pointer replaces the stale line; SCC-97's `nothing-guards-the-merge-target` row keeps its place. |
| the SOP | **Accepted the move, re-placed the content.** SCC-91 restructured it as a teaching document (970 → 1694 lines) at `docs/_scc_sops_prds/workflows_testing_SOP.md`. My 53 lines were **re-placed into the new structure, not pasted**, at *both* sites that still claimed the gate was unbuilt — `:726` and the SCC-71 block. Precedent: SCC-94 did exactly this on this same file. |

**Two things the reconcile settled:**

- The restructure had **already removed** the three-door sentence that misread
  `/cicd-update-sprint-memory` as a `main` door. That fix was no longer needed — independent
  confirmation the reading was right.
- **SCC-97 and SCC-77 turn out to reinforce each other.** SCC-97 asks you to assert `HEAD` is `main`
  immediately before merging. `mint-push-token.sh` already **refuses to mint unless `HEAD` is
  `main`**, and it runs between the merge and the push — so on the two door lanes that assertion is
  now mechanical. Cross-referenced in `git-policy.md` rather than left for someone to rediscover.
- The SOP-move disarm trap I flagged **was caught** — `sop-currency.sh:26` now points at the new
  path. Confirmed on main, not assumed.

## Evidence

At the merged tree `47c0cd1`:

```
run_all.py                     14/14   exit 0     (13/13 on main + this lane's file)
workflow_lint --toolkit-only   0 errors, 0 warnings, exit 0
test_main_push_gate.py         51/51   exit 0     (36 before the review round)
test_sops_prds_folder.py       57/57   exit 0     (the SOP gate that did not exist pre-merge)
task_preflight --expect-key    clear to close out and merge · LANE LOCAL
```

The two lint warnings present pre-merge are gone — main fixed them. This lane adds none.

**Pre-merge run, retained for the record** (at `8e2ee83`, against the old main): `run_all` 12/12,
`test_main_push_gate` 36/36, lint 0 errors / 2 pre-existing warnings, `test_memory_store` 16/16.

**Live, on this repo, not in a fixture:**

```
$ git push -u origin HEAD                    # chore branch
 * [new branch]      HEAD -> chore/SCC-77-main-write-gate        # passes freely

$ git push --dry-run origin HEAD:main        # no token
  ⛔ PUSH TO main REFUSED — no approval token.
     main is reached exactly three ways (.agents/rules/git-policy.md): …
error: failed to push some refs
```

The test suite additionally runs a **real `git push` at a real bare remote** — refused with no
token, nothing reaching the remote; then minted, pushed, landed, token consumed. Everything short of
that can pass while git never invokes the hook at all, which is precisely the failure that shipped.

## Decisions taken while building

- **The minter is `sh`, not Python** (the plan said `.py`). Zero interpreter dependency anywhere in
  the gate path. Making the *enforcement* layer depend on the class of thing that broke it would
  reproduce the bug inside the fix — the same reasoning `sop-currency.sh` already documents.
- **`run-hook.sh` announces when it cannot run**, rather than exiting 127. The root failure was not
  "wrong binary", it was **silence**. A hook that can't launch must say so.
- **Defect 6 corrected in the right file.** The false *"AGY keeps its own identical copy"* sentence is
  in the **memory** file, line 67 — not `git-policy.md:67`. I had conflated two line-67s in the
  earlier survey. `git-policy.md` never carried that claim.
- **`.agents/hooks/INDEX.md` hand-edited** (2 filenames) despite its "refresh via
  `/smh-update-maps-indexes`" banner. Running the full command mid-task would have pulled unrelated
  repo-wide changes into this diff. The entries are plain filenames; the ban exists to stop prose.

## Pitfalls worth carrying

- **`git push --dry-run` on an up-to-date branch does not run `pre-push` at all** — git skips the hook
  when there is nothing to push. My first end-to-end attempt returned "Everything up-to-date, exit 0"
  and proved precisely nothing. Test the gate only against a branch with real commits ahead.
- **A dry-run that *does* reach the hook still spends the token.** There is no way for the hook to
  know it is a dry run. Mint immediately before the real push, never to "test" it.
- **`core.hooksPath` is per-machine and does not travel.** The PC needs `git config core.hooksPath
  .githooks` set independently or it is silently ungated. The suite now asserts it is set *and*
  relative.
- ⛔ **I gave a false reason for making `core.hooksPath` relative, and the review caught it.** I wrote
  that *"an absolute path cannot survive a clone to the other machine."* Neither form survives a
  clone — `core.hooksPath` lives in `.git/config`, which git never carries, so the value is
  per-machine either way. The real trade-off is the opposite of what I implied: **relative makes git
  resolve `.githooks/` per worktree**, so a worktree cut before this gate existed is ungated *and
  silent*. Absolute would gate every worktree uniformly at the cost of breaking if the repo moves.
  Relative is still the choice — it matches AGY and keeps each lane testable — but it is a trade-off,
  not a free win, and the suite now reports which worktrees are ungated instead of implying none are.
- ⭐ **A trailing slash in `.gitignore` matches directories ONLY — and worktree assets are symlinks.**
  `**/node_modules/` ignored the real directory in the shared checkout and **missed the symlink**
  `link-worktree-assets.py` creates in every worktree. `task_preflight.py` counted that link as an
  uncommitted change and returned `BLOCKED` for a lane that was completely clean. It blocked this
  one. Fixed by dropping the trailing slash on `node_modules`, `.venv`, `venv` — verified no
  previously-tracked path becomes ignored. **This affected every worktree lane, not just this task.**

## Known limits — documented in `git-policy.md` and the SOP, not hidden

1. **An agent can write files, so an agent can forge a token.** This is not a security boundary
   against a determined agent and must not be described as one. It converts a silent violation into a
   deliberate, traceable one, and it closes the actual SCC-71 failure: a close-out command whose body
   stays in context and still reads valid on task six.
2. **`gh pr merge` and the GitHub web UI never reach a local hook.** Structurally out of reach → SCC-75.

## Your Actions

**Landed on the branch** (`chore/SCC-77-main-write-gate`, pushed to origin) — commits `c007594`..HEAD.

**Owed to you — I have minted nothing; placement is yours (`jira.md` guardrail 2):**

| Where | What |
|---|---|
| **SCC-74** (procedures consolidation) | [`docs/_scc_sops_prds/git_walkthrough_settings.md:299`](../../../docs/_scc_sops_prds/git_walkthrough_settings.md#L299) still says `main` = **`/cicd-push-e2e` only** — it predates `/smh-close-task-merge-tree`, and now that the gate is armed it contradicts an *enforced* mechanism rather than just a written rule. Re-verified against current `main` at review time, still stale. Left here deliberately: it is SCC-74's file by the operator's routing, and fixing it in this diff would be scope drift. |
| **SCC-75** (Security · Auth · Testing) | One child: the incident lane creates `claude/incident-<id>` while `task_preflight.py` guards `incident/`; the incident lane lands via GitHub PR; `gh pr merge` is ungated and no local hook can see it. |
| **New AVCH ticket** | AGY needs this same gate — two files + `core.hooksPath`. It does **not** propagate: enforcement is repo-local by design. |

**The merge is yours.** The branch is pushed, gates are green, and the preflight is clear. Per SCC-71
this hands back here — invoking `/smh-close-task-merge-tree` is the sign-off, and it will now mint the
token that lets the push through. This branch is the gate's first real customer.

---

## Code Review (2026-08-11)

Verdict: PASS @ 3a6c3933b2b7d0623a0bffec79e14bb5a8b1c16f
Suite evidence measured at the same sha: `run_all.py` 14/14 exit 0 · `test_main_push_gate.py` 57/57
exit 0 · `workflow_lint --toolkit-only` 0 errors 0 warnings exit 0 · `test_sops_prds_folder.py`
57/57 exit 0 · `sop_currency` exit 0.

**Scope** — 19 files, `main...HEAD`, reviewed at `3fe5454`/`3a6c393` (the three gate scripts are
byte-identical across those, so every finding holds at the tip).
**Method** — `/smh-code-review` end to end: blast-radius re-derivation, a clean-room adversarial pass
in a subagent with no conversation context, acceptance audit against the ticket's `ACCEPTANCE` block,
the command-centre gate, and the clean-code floor.

> ⛔ **This review found a CRITICAL defect that invalidated the change's headline claim.** It is
> fixed, evidenced and regression-tested — but the verdict reads PASS only because of the fix, not
> because the first cut was sound. Anyone reading this later should read finding 1 before trusting
> the gate.

### Findings

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| 1 | `pre-push-main-approval.sh:107` | **CRITICAL** | The token authorised a **push**, not a **merge**. Merge six branches into `main` locally → mint once → push once: the sha check passes the whole way and **six merges land on one approval**. Reproduced against a real bare remote: 6 merges on the remote, one token, the approval line naming one of them. The claim *"the check that would have caught SCC-71"* was false in five documents. | **applied** — `main` must now advance by exactly ONE merge sitting on the remote's tip, whose second parent is the branch the token names. Minter refuses a stacked batch too. 5 tests. |
| 2 | `pre-push-main-approval.sh:72` | HIGH | `delete` was refused while `reset --hard main~5 && push --force` — the same destructive outcome — was **approved**. Verified: remote rewound, five merges destroyed. | **applied** — same one-merge invariant covers it. 2 tests; remote tip verified unchanged. |
| 3 | `.githooks/pre-push:13` | HIGH | `core.hooksPath` is relative → git resolves `.githooks/` **per worktree**. A worktree cut before this gate exists is ungated and **silent** (the dispatcher's warning only fires when the dispatcher itself is present). | **partially applied** — inherent to per-worktree resolution; cannot be fully closed from inside the repo. Suite now enumerates every worktree and reports which are ungated; documented in `git-policy.md` + SOP. Merging this lane gates the main checkout. |
| 4 | `pre-push-main-approval.sh:98` | HIGH | `$(( ))` recursively expands its operands, so `minted=z[$(cmd)]` **executes `cmd`** during a legitimate push. Verified: `CODE-EXECUTION-HAPPENED` printed from the token file. Forging a token is in the threat model; arbitrary code execution is not. | **applied** — digits-only string validation before any arithmetic. |
| 5 | `pre-push-main-approval.sh:98` | MEDIUM | `minted=now` resolves to the script's own `now` variable → age 0 → **never expires**. Verified approved. The test that claimed to cover this used `NOTANUMBER` (→ 0 → ancient → stale), so it passed while the property it named was false. | **applied** — same fix; both cases now tested. |
| 6 | `mint-push-token.sh:28` | MEDIUM | `shift 2` with `$# < 2` returns non-zero **without shifting** → infinite loop. Both door commands template `--key <JIRA-KEY>` as the trailing arg, so a dropped substitution hangs the minter *after* the merge and *before* the push. | **applied** — `need()` guard before every shift. |
| 7 | `test_main_push_gate.py:113` | MEDIUM | A check that cannot fail: `epic/main-fix` does not contain `refs/heads/main` as a substring, so a substring implementation passes it too. | **applied** — now also asserts `main-backup` and `mainx`, which are the discriminating cases. |
| 8 | `test_main_push_gate.py:89` | MEDIUM | The RELATIVE assertion's stated reason was **false** — `core.hooksPath` never travels with a clone in either form. And mandating relative is what *causes* finding 3. | **applied** — assertion replaced with per-worktree gating; the false rationale corrected in the walkthrough rather than deleted. |
| 9 | `.claude/settings.json:20` | MEDIUM | The revived PreToolUse hook returns `ask` for the door commands' own push line, and `ask` is an auto-DENY in auto mode → headless close-out merges, mints, then is denied, leaving `main` merged-but-unpushed with a token expiring in 30 min. No test exercised the hook at all. | **applied** — layer 2 stands down when a valid token already covers the push; fails toward asking. 6 tests. |
| 10 | plan/walkthrough | LOW | Stale `36/36` evidence figures after the suite grew. | **applied** — now 57/57, with the pre-review figure kept as history. |
| 11 | `implementation_plan.md:150` | LOW | Acceptance item 6 cited *documentation* as proof of behaviour, and `--no-verify` is silent by construction, not "loud". | **applied** — `--no-verify` is now tested; "and are loud" dropped from the claim. |
| 12 | `test_main_push_gate.py:107` | LOW | Dead code — `old = ... HEAD~0`, never referenced. | **applied** — deleted. |

**Confirmed correct** (probed, recorded so nobody re-spends the time): `exit 1` inside the `while
read` loop genuinely fails the hook · `IFS='='` preserves `=` inside values · `git push --all` is
gated · relative-vs-absolute `--git-common-dir` handling is right in both worktrees and the main
checkout · the suite copies the real scripts per run, so there is no forkable copy to drift.

### Step 0.7 — re-derivation against current `main`

- **What moved under this diff:** nothing. `merge-base == main` (`48e95c5`); all 73 commits were
  absorbed before review. Of 64 distinct repo paths the diff references, 2 were stale — both mine,
  both artifacts, both fixed. The rest resolve.
- **True overlap + `merge-tree`:** empty intersection, clean tree, no conflicts.
- **Sibling landing order:** no other lanes live. No dependency.

### Clean-Code Gate

| Check | Result |
|---|---|
| `run_all.py` | **14/14, exit 0** |
| `workflow_lint --toolkit-only` | **0 errors, 0 warnings, exit 0** |
| `sop_currency` | **exit 0** |
| `py_compile` | OK (hook ×2, test) |
| `bash -n` **and** `/bin/sh -n` | OK on all 6 shell files — the gate must run under `/bin/sh`, not only bash |
| Link + anchor | **139 links in the diff, 0 dead, 0 out-of-range anchors** |
| Door parity | N/A — no command added, renamed or deleted |
| Secrets / debug / commented-out code / bare `except` | none across 693 added non-artifact lines |

**Negative control (a gate must be able to fail):** sabotaging the tip check reds exactly *"token
minted for another sha is refused"*; restoring returns green, file byte-identical. An earlier
scan produced a **vacuous** pass — a bad git pathspec left the input file empty — and was redone
against 693 real lines. Both are recorded because a green that cannot go red is the failure this
whole toolkit exists to remove.

### Changes applied

All 12 findings dispositioned; 11 fully applied, finding 3 partially (inherent limit, now reported
by the suite instead of implied away). The suite grew 36 → 57 assertions, all of them added because
something got past the previous set.
