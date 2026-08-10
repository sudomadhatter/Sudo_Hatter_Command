# SCC-77 — the `main` write gate

**Branch** `chore/SCC-77-main-write-gate` · **Lane** LOCAL · **Base** `main` @ `9a6a026`

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
| `core.hooksPath` (SCC) | — | **absolute** — cannot survive a clone to the PC |

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
never trips) → exists → fresh (30 min) → **same commit** → never delete `main`.

⭐ **The "same commit" check is the one that would have caught SCC-71.** The token records the sha it
was minted for, so work committed *after* the sign-off is refused — which is exactly the shape of six
merges on one approval. Every refusal also **discards** the token, so a failed sign-off is spent
rather than left lying around for a later push to match by accident.

The token is consumed *before* the push. There is no `post-push` hook, so that is the only available
order — and it fails safe: a rejected push (remote moved) needs a fresh sign-off, which is right,
because re-running the door command re-runs the preflight against the remote that moved.

## Evidence

```
test_main_push_gate.py            36/36   exit 0
run_all.py                        12/12   exit 0
workflow_lint --toolkit-only      0 errors, 2 warnings   (both pre-existing — identical to SCC-63's baseline)
test_memory_store.py              16/16   exit 0
```

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
| **SCC-74** (procedures consolidation) | `git_walkthrough_settings.md:299` still says `main` = `/cicd-push-e2e` **only**, predating `/smh-close-task-merge-tree`. **And:** [sop-currency.sh:26](../../../.agents/scripts/git-hooks/sop-currency.sh#L26) is `[ -f _my_resources/_quick_reference/sudo_workflows_testing.md ] \|\| exit 0` — **moving that file into `_scc_sops_prds/` silently disarms the armed SOP gate.** Same bug class as the exit-127 hooks. The hook's path must move in the same commit. |
| **SCC-75** (Security · Auth · Testing) | One child: the incident lane creates `claude/incident-<id>` while `task_preflight.py` guards `incident/`; the incident lane lands via GitHub PR; `gh pr merge` is ungated and no local hook can see it. |
| **New AVCH ticket** | AGY needs this same gate — two files + `core.hooksPath`. It does **not** propagate: enforcement is repo-local by design. |

**The merge is yours.** The branch is pushed, gates are green, and the preflight is clear. Per SCC-71
this hands back here — invoking `/smh-close-task-merge-tree` is the sign-off, and it will now mint the
token that lets the push through. This branch is the gate's first real customer.
