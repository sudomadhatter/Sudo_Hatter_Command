---
IsArtifact: true
ArtifactMetadata:
  title: SCC-113 — the In Progress seam
  type: implementation_plan
  date: 2026-08-11
---

# SCC-113 — Nothing moves a ticket to `In Progress`

**Branch** `chore/SCC-113-jira-in-progress-seam` · **Lane** LOCAL · **Cut from** `main` @ `48e95c5`
**Ticket** SCC-113, under SCC-12 (*Jira — system rules and workflows*)

---

## The problem

The board never shows work in flight. Verified live 2026-08-11 against `sudo-command.atlassian.net`:
of the **five** transition seams in the toolkit, four write `Done` and exactly **one** writes
`In Progress`.

| Seam | Writes | Site |
|---|---|---|
| `/cicd-write-story-tests` ① Step 1.6.4 | → `In Progress` | `cicd-write-story-tests.md:89` |
| `/cicd-update-sprint-memory` Step 4.5 | → `Done` (story) | `cicd-update-sprint-memory.md:161` |
| `/cicd-push-e2e` Step 6.5 | → `Done` (epic) | `cicd-push-e2e.md:123` |
| `/smh-close-task-merge-tree` Step 4 | → `Done` (task) | `smh-close-task-merge-tree.md:229` |
| `/smh-merge-multiple-workingtrees` | → `Done` (task) | `smh-merge-multiple-workingtrees.md:225` |

The single `In Progress` writer is the **BMAD Story lane**. Per `jira.md` §Work-item types, every
non-epic SCC ticket is a **`Task`** — so in the command centre nothing is ever visible as in flight:
a `chore/*` lane sits in `To Do` while it is built, then teleports to `Done` at merge.

**The `Done` end is not broken.** SCC-83, 88, 89, 90, 91, 93, 94, 95, 96 and 97 all read `Done` on the
live board. This is a front-end hole, not a pipeline failure.

### Two defects found in the same pass

**1. Three of the four `Done` calls omit `--yes`.** `acli jira workitem transition` prompts for an
interactive confirm without `-y` (verified against `--help`). `jira.md:268` already flags this as a
trap and `jira_feed.py` passes it correctly, but the three command bodies do not. `Done` is landing
today by luck.

**2. The start seam is the only ticket write that is prose rather than a script.** SCC-49 ruled that
every seam goes through `jira_feed.py` *"because each one had a silent failure mode that prose could
not hold"* — `mint`, `devrecord`, `check`, `trace` and `flag` all read the ticket back and exit 2.
The sole exception is the one that is not happening. **That is the root cause, not the missing wire.**

## The design ruling (operator, 2026-08-11)

**The trigger does not hang on a command.** `/smh-quick-dev` is not always run, and a fix that depends
on remembering to run it re-creates the defect. Work provably starts when **the first commit lands on
a keyed branch** — whatever path got there, including a bare `git commit` with no workflow at all.

**Both layers ship.** The hook is the safety net; the command body moves the ticket earlier and
visibly when the command *is* used.

**Scope: all three keyed prefixes** — `chore/`, `claude/` and `epic/`.

> ⚠️ **AUDIT FINDING F-2 — what that scope actually buys *in this repo*.** `claude/*` and `epic/*`
> keyed branches overwhelmingly live in **AGY**, not the lobby, so here the hook will realistically
> fire on `chore/SCC-*` almost exclusively. All three prefixes still ship — it is one regex
> alternation and it is correct the day a keyed `claude/`/`epic/` branch does appear here — but this
> lane does **not** deliver board-wide coverage, and must not be reported as if it does. The AGY half
> is F-1's separate AVCH ticket.

### Why `post-commit` and not `commit-msg`

The armed key gate refuses to grow, in its own header:

> *"A live 'does AVCH-57 exist?' call would put a network round-trip on every commit and would fail
> closed on a plane. Do not grow this hook — a slow hook is a disabled hook."*
> — `commit-msg-jira.sh`

`post-commit` carries the opposite contract, equally explicit:

> *"post-commit fires AFTER the commit is sealed, so it can never block or corrupt a commit; every
> error is swallowed so a broken recorder is invisible to your workflow."*
> — `.githooks/post-commit`

A network call is safe there. It is already the map-drift recorder; a Jira recorder is the same shape.

---

## Architecture

**Layer A — `jira_feed.py start`.** The verb. Single contract, same read-back discipline as its four
siblings. Everything else calls this; nothing else calls `acli transition` for a start.

**Layer B — `post-commit` recorder.** The safety net. Catches every path.

**Layer C — `/smh-quick-dev` Step 0.5.** The visible move at worktree-open.

> **The design rule:** Layer B may never be the only thing that works, and may never block a commit.
> If the hook is off (a machine with no `core.hooksPath`), Layer C still moves the ticket whenever the
> command is used. If the command is skipped, Layer B catches it. Neither is load-bearing alone.

### `start` — the status rules

It moves **only out of a `To Do`-category status**, mirroring `flag`'s "only out of `Done`" narrowness.
A verb that moves from anywhere can erase real state.

| Current status | What `start` does | Exit |
|---|---|---|
| `To Do`, `To Do Next` | transition → `In Progress`, read back | 0 / 2 on failure |
| `In Progress` | no-op, says so — **idempotent**, two lanes cannot fight | 0 |
| `Blocking`, `In Review`, `Deferred` | leaves it, prints why | 0 |
| **`Done`** | **refuses loudly** — a `Done` ticket means the key is wrong (`jira.md` guardrail 1, in reverse) | 2 |
| `Subtask` type | refuses | 2 |

**`Epic` is allowed** — the operator scoped `epic/` in. This is the one place `start` deliberately
differs from `flag`, which refuses containers: an epic under active development *is* in progress,
whereas an epic is never itself a bug.

### The hook — one call per branch, ever

`.githooks/post-commit` delegates to a new `.agents/scripts/git-hooks/post-commit-jira-start.sh`,
matching how `commit-msg` already delegates to two scripts.

1. `git-hooks/DISABLE` kill switch → exit 0 (same as every other hook).
2. `.agents/jira.conf` → `JIRA_KEYS`; no conf, no gate.
3. Branch must match `^(chore|claude|epic)/(<KEY>-<n>)-`; otherwise exit 0.
4. **Marker short-circuit:** `$(git rev-parse --git-dir)/jira-started-<KEY>` exists → exit 0, **no
   network.** This is what makes it one call per branch rather than one per commit.
5. Interpreter probe `python3 → python → py` (the SCC-49 order the other hooks use).
6. `jira_feed.py start --key <KEY> --apply`; **write the marker only on exit 0.**
7. Swallow everything. A failure costs a retry on the next commit, never a commit.

**Offline is self-healing by construction:** the call fails, the marker is not written, the next
commit tries again.

### Known trade-off, stated rather than hidden

The hook runs **inline**, so the first commit on a branch waits on one `acli` round-trip (~1–2s).
Backgrounding it would hide every failure, and macOS has no `timeout(1)` without coreutils. Once per
branch is the price for a recorder whose failures are visible when you look. If it ever bites, the
fix is the marker written optimistically, not a detached process.

---

## Landing order — SCC-77 is live and overlaps

`chore/SCC-77-main-write-gate` is **10 commits ahead of `main`, unlanded**, and edits two of my four
target files:

| File | SCC-77 hunk | My hunk | Collision |
|---|---|---|---|
| `cicd-push-e2e.md` | ~84–104 (push token) | 123 (`--yes`) | no overlap |
| `smh-close-task-merge-tree.md` | ~201–220 (push token) | 229 (`--yes`) | **adjacent — within 9 lines** |

**SCC-77 should land first.** It ships the `pre-push` main gate that will govern this lane's own
merge, so building under the regime that will exist beats discovering the mint-token step at merge
time. If it does **not** land first, nothing here is lost — both my edits are a single flag on a
single line — but they must be **re-verified against the merged file after absorbing `origin/main`,
never assumed.** `/smh-close-task-merge-tree` pulls `--ff-only` before merging, which is where that
re-check happens.

---

## Steps — each names the assertion that proves it

| # | Step | Assertion (written FIRST, seen RED) | AC |
|---|---|---|---|
| 1 | `start` verb in `jira_feed.py` + `add_parser("start")` | `test_jira_feed.py`: `To Do` → exits 0, stub state reads `In Progress` | 1 |
| 2 | Read-back + exit 2 | stub configured to refuse the transition → exit 2, message names the ticket | 1 |
| 3 | Idempotence | run twice; second exits 0 and prints "already", stub records **one** transition call | 2 |
| 4 | `Done` refusal | stub status `Done` → exit 2, output carries "not your key" | 3 |
| 5 | Status-table rules | `Blocking` / `In Review` / `Deferred` → exit 0, no transition recorded; `Epic` type → allowed | 3 |
| 6 | `post-commit-jira-start.sh` + dispatch from `.githooks/post-commit` | new `test_jira_start_hook.py`: real temp git repo, fake `acli` on PATH, commit on `chore/TEST-1-x` → status moves | 4 |
| 7 | Marker short-circuit | second commit on the same branch → stub records **zero** further calls; marker file exists | 5 |
| 8 | Offline retry | stub forced to fail → no marker written, commit still succeeds (exit 0), next commit retries | 5, 6 |
| 9 | Prefix scope | commits on `chore/`, `claude/`, `epic/` all fire; `main` and an unkeyed branch fire nothing | 4 |
| 10 | `/smh-quick-dev` Step 0.5 gains the `start` call | `workflow_lint.py --toolkit-only` exits 0; the call is present in the brain | 7 |
| 11 | `--yes` on all three `Done` sites | grep assertion in the enforcement suite: every `workitem transition` in `.agents/` carries `--yes` | 8 |
| 12 | `jira.md` — guardrail 4 rewritten, seam list + status table reconciled | link/anchor check clean; guardrail 4 enumerates the shipped set | 9 |
| 13 | SOP currency + door sync | `workflows_testing_SOP.md` updated in the same commit; `/smh-sync-agents` regenerates 4 doors each; `run_all.py` green | 10 |

**Step 11 is a guard, not a one-line fix.** A grep assertion over `.agents/` is what stops the fourth
site from being added without `--yes` next year. Per `comment-literals-invert-source-grep-tests`, it
must ignore comment lines, or a comment quoting the bad form satisfies it.

## Blast radius

**Written:** `jira_feed.py` · `tests/test_jira_feed.py` · `tests/test_jira_start_hook.py` (new) ·
`git-hooks/post-commit-jira-start.sh` (new) · `.githooks/post-commit` · `smh-quick-dev.md` ·
`cicd-push-e2e.md` · `smh-close-task-merge-tree.md` · `smh-merge-multiple-workingtrees.md` ·
`cicd-write-story-tests.md` · `rules/jira.md` · `workflows_testing_SOP.md` · generated doors.

**Not written:** `commit-msg-jira.sh` (must not grow — its own header forbids it) · `task_preflight.py`
(a start check at merge time is the wrong end) · **any AVCH-side file.**

> ⚠️ **AUDIT FINDING F-1 — AGY inherits NOTHING from this lane.** An earlier draft of this plan said
> the toolkit sync would carry it. It will not: `sync-agents.ps1:360-362` states that `jira.conf`,
> `.githooks/` and `.agents/scripts/git-hooks/` are **repo-local enforcement, never centralized**, and
> the project-vendor path was deleted 2026-08-07 — nothing copies into a project at all. AGY also has
> **no `jira_feed.py`** (its `.agents/scripts/` is `INDEX.md` + `git-hooks/` + `tests/`), so the AGY
> install is not a file copy: the script has to get there, or the hook has nothing to call. That is
> real work under its **own AVCH ticket**, per `cross-repo-work-needs-a-ticket-per-repo`. Fold
> **F-6** (AGY's drifted `python`-first probe) into that ticket.

## Rollback

Delete the marker files, revert the merge. Nothing is destructive: the hook only ever moves a ticket
`To Do → In Progress`, and the reverse is one `acli transition` by hand. No history rewrite, no delete.
The one irreversible act in this lane is **board writes on real tickets during testing** — every test
drives the stub `acli`, and no test may touch the live board.

---

## Self-Audit (2026-08-11)

**Right-size: FULL.** It touches a rule (`jira.md`), a hook (`.githooks/post-commit`), a script other
things import (`jira_feed.py`), and more than one platform surface — four of the Phase 0 triggers.

| Phase | Walked | Result |
|---|---|---|
| **0** Scope + checkable list | change set named (13 files); acceptance list taken from SCC-113's `ACCEPTANCE` block (authority 1); traced both directions | every AC maps to a step and every step to an AC — **no orphans, no creep** |
| **0** Lane check | change set touches no `backend/ frontend/ firebase/ functions/ mobile/ .github/` | **Task lane confirmed** — closes via `/smh-close-task-merge-tree` |
| **1** Blast radius | door parity (4/command), `jira_feed.py` callers, `_RULE_POINTERS`, transition call sites, sop-currency trigger, sibling lanes | **two HIGH findings** — see table |
| **2** Over-engineering | 10 tripwires walked | one fired (new script); **justified, kept** — see F-4 |
| **3** Pre-mortem | 8 rows | the propagation row is what produced F-1 |

### Findings

| # | Site | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| **F-1** | `task.yaml:5` + plan §Blast radius | **HIGH** | The plan claims *"AGY inherits this via the toolkit sync — no AVCH-side code change."* **False.** `sync-agents.ps1:360-362` states it outright: *"`jira.conf`, `.githooks/`, and `.agents/scripts/git-hooks/` are repo-local ENFORCEMENT: git runs hooks in the repo they gate, so they live there permanently and are **never centralized**"* — and the whole vendor path was deleted 2026-08-07, so nothing copies into a project at all. Shipping this and believing AGY is covered means every `AVCH` ticket keeps the exact defect this lane closes, invisibly. | **FIXED IN PLAN.** `secondary_repos` comment corrected; AGY coverage is explicitly **out of scope** and owed its own **AVCH ticket** (`cross-repo-work-needs-a-ticket-per-repo`). |
| **F-2** | plan §Design ruling (scope) | **HIGH** | AGY's `.agents/scripts/` holds only `INDEX.md`, `git-hooks/`, `tests/` — **there is no `jira_feed.py` there.** So an AGY hook has nothing to call without vendoring the script (against the thin model) or hard-coding a cross-repo path (per-machine, breaks on the PC). Consequence for *this* lane: `claude/*` and `epic/*` keyed branches overwhelmingly live in **AGY**, so in the lobby the hook will realistically only ever fire on `chore/SCC-*`. The operator's chosen 3-prefix scope is **half-deliverable here**, and the plan did not say so. | **KEEP all three prefixes** (one regex alternation, correct if a keyed `claude/`/`epic/` branch ever appears here) but **state the limit plainly** rather than implying board-wide coverage. The AVCH ticket carries the other half. |
| **F-3** | plan §The hook, step 4 | MED | *"`$(git rev-parse --git-dir)` … is per-worktree, that's fine"* is an **assumption**. If it resolves to the shared `.git` instead, two lanes on two branches share one marker and the second branch never fires. | **Becomes an assertion**, not a claim: Step 7's test asserts the marker path contains the worktree segment and that a second branch in a second worktree still fires. |
| **F-4** | plan §Architecture (new file) | MED | **Phase-2 tripwire fired:** *a new script where an existing one grows*. `.githooks/post-commit` currently **inlines** its logic, so the split is not automatic precedent. | **KEPT, justified:** the assertion in Step 6 has to *drive* the hook logic directly, exactly as `test_main_push_gate.py` drives `pre-push-main-approval.sh` and `commit-msg` delegates to two testable scripts. An inlined 20-line hook is not directly testable. The tripwire is answered, not waived. |
| **F-5** | plan Step 11 | MED | The `--yes` grep guard can pass vacuously two ways this repo has already been bitten by: a **comment** quoting the bad form matches first (`comment-literals-invert-source-grep-tests`), and `jira.md:268` legitimately contains the *correct* form as a cheat-sheet line, so a naive "does the good form exist" check is satisfied by a file I am not guarding. | Guard must **strip comment lines**, scan `.md` **and** `.py`, and assert **per call site** (every `workitem transition` occurrence carries `--yes`) rather than "the good form appears somewhere". Red-first: run it against current `main` and **see it fail 3×** before the fix. |
| **F-6** | `Projects/AGY_AVIATIONCHAT/.githooks/post-commit:11` | LOW | Pre-existing drift, **out of scope**: AGY still has the two-branch `python`-first probe the lobby replaced with `python3 → python → py` (SCC-49) and documented as *"two probe orders in one repo is how they drift."* Harmless on this Mac; wrong on a machine whose `python` is Python 2. | **Report only.** Fold into the AVCH ticket from F-1; do not touch another repo from this lane. |
| **F-7** | `/smh-self-audit` Step 0 echo | LOW | In a worktree, `basename $(git rev-parse --show-toplevel)` prints the **lane** name (`scc-113-jira-in-progress-seam`), not `Sudo_Hatter_Command` — the same class as `check-maps-stale-is-false-in-worktrees`. Cosmetic here (the plan header states the repo correctly), but it is a label that can mislead a later reader. | Note only; no change in this lane. |

### Pre-mortem rows that mattered

- **The other machine** ✅ — every hook path uses the `python3 → python → py` probe; no bare `python`, no absolute path, no PowerShell in the enforcement path.
- **A fresh clone** ⚠️ — `core.hooksPath` is per-machine, so on the PC the hook is silently OFF until `git config core.hooksPath .githooks` is run. **This is why Layer C (the command body) is not optional** — it is the layer that still works with the hook dead. Stated in §Architecture as a design rule.
- **Empty input** ✅ — no `jira.conf` → exit 0; no key in the branch → exit 0; both are correct silence, and neither is a gate that reads empty as pass (the hook is a **recorder**, and the plan says so; the only real *gate* here is Step 11's grep, which F-5 forces to fail red first).
- **A sibling lane lands first** ⚠️ — SCC-77, handled in §Landing order.
- **Rollback / irreversible** ⚠️ — the one irreversible act is a **live board write**. Every test drives the stub `acli` via `--acli`; no test touches the real board. Called out in §Rollback.
- **The four platform caches** ✅ — Step 13 runs `/smh-sync-agents`; five command brains change, so 20 doors regenerate.

### Four gates

- **Verification strategy present?** ✅ — 13 steps, each naming the assertion that proves it and the AC it serves.
- **Anything irreversible?** ⚠️ — live-board writes; gated to the stub (above). The Jira transitions themselves are one-command reversible.
- **Any step vague enough to be guessed?** One was — Step 11's guard. F-5 tightens it to a per-call-site, comment-stripped, red-first assertion.
- **Convention fit?** ✅ — verb on the existing script rather than a new one; hook delegates to a testable script as `commit-msg` already does; artifacts in `_artifacts/_main/<date>_<slug>/`; doors regenerated, never hand-edited.

### Landing-order dependency

`chore/SCC-77-main-write-gate` — 10 commits ahead of `main`, unlanded, edits `cicd-push-e2e.md` and
`smh-close-task-merge-tree.md`. Its hunks are the push-token block (~84–104, ~201–220); mine are the
`--yes` one-liners (123, 229) — **adjacent within 9 lines in one file, no overlap.** SCC-77 should
land first. If it does not, both my edits must be **re-verified against the merged file** after
`/smh-close-task-merge-tree` pulls `--ff-only`, never assumed.

```
Audit verdict: GO
```

**GO with F-1 and F-2 already folded into the plan above** — the AGY half is now explicitly a separate
AVCH ticket rather than an assumed freebie, and F-3/F-5 convert two assumptions into assertions before
any code is written. Nothing outstanding blocks the build.
