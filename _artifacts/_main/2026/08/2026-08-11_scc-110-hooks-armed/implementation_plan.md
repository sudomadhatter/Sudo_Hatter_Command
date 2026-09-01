# SCC-110 — Runtime arm-check for git hooks

**Lane:** `chore/SCC-110-hooks-armed` · cut from `main` @ `4c8cf7f`
**Parent:** SCC-98 · **Type:** Subtask · **Close command:** `smh-close-task-merge-tree`

---

## Why this is smaller than the ticket says

The ticket was written **before** SCC-77 landed. SCC-77 built most of it. Ground-truthed by reading
`test_main_push_gate.py` and `run-hook.sh`, not by re-reading the ticket.

**Already shipped by SCC-77 — do not rebuild:**

| Concern | Where it lives now |
|---|---|
| hook file exists · is **executable** (the chmod class) | `test_main_push_gate.py` INSTALLED block, ~L81-84 |
| `MAIN-PUSH-ENFORCE` present (armed vs warn-only) | same, L85 |
| `core.hooksPath` **is set**, with the remedy string | same, L87-90 |
| `core.hooksPath` **resolves** to a dir holding the hook | same, L91-93 |
| …for **every live worktree**, since `core.hooksPath` is relative | same, L95-119 |
| the silent exit-127 class (wrong interpreter, no output) | `.agents/hooks/run-hook.sh` |

SCC-77's per-worktree refinement is **better than what SCC-110 specced**. It came out of that lane's
adversarial review, reproduced against a real remote. Keep it verbatim; do not "simplify" it.

**Settled, not a gap:** `run-hook.sh`'s header states the Claude-hook layer is deliberately
non-load-bearing — *"the main write gate is `.githooks/pre-push` (pure sh, no interpreter at all)
precisely so that a repeat of the 127 bug degrades the prompt, never the gate."* The cross-platform
asymmetry is a decision with its rationale in the code. Out of scope.

---

## The two gaps that actually remain

**GAP 1 — Coverage.** The arm-check is hardcoded to `pre-push` + `MAIN-PUSH-ENFORCE`. On disk today:

```
.githooks/                          commit-msg  post-commit  pre-commit  pre-push
.agents/scripts/git-hooks/*ENFORCE  JIRA-ENFORCE  MAIN-PUSH-ENFORCE  SOP-ENFORCE
```

**3 of 4 hooks and 2 of 3 flags have no assertion at all.**

**GAP 2 — Reach.** The check runs in the *test suite*. It does not run where operators read the
verdict. `task_preflight.py:132-135` still says:

> `# The same rule the armed commit-msg hook enforces. If it were wrong the commits on`
> `# this branch could not exist, so reaching here means the hook was bypassed.`

That inference holds **only if the hook is armed**. On an unarmed clone the commits exist regardless,
the inference is false, and preflight goes on to print *"clear to close out and merge."*

---

## Acceptance — each item, and the assertion that proves it

| # | Acceptance | Assertion |
|---|---|---|
| 1 | Reports every tracked hook in `.githooks/`: present · executable · `hooksPath` resolves to it — **derived, not hardcoded** | `test_hooks_armed.py` seeds a temp repo with a 5th hook and asserts it is reported with **no code edit** |
| 2 | Reports every `*-ENFORCE` flag found, **and every armable script it can see**, treating flag→script as a *declared* pairing (see Audit #2 finding B — it is not derivable) | temp repo missing `JIRA-ENFORCE` → reported warn-only, non-zero |
| 2b | A hook's inner script present but **not executable** is reported — `.githooks/commit-msg` L27 does `[ -x "$SOP" ] \|\| exit 0`, exiting **silently** | temp repo with `sop-currency.sh` non-executable → non-zero, and the message names the silent path |
| 3 | `test_main_push_gate.py` calls the shared helper and still passes **57/57** | run it bare, paste the count |
| 4 | `task_preflight.py` surfaces `NOT ARMED` **in its top-line verdict**, not only in prose, and withholds the unqualified clear line | temp repo with `core.hooksPath` unset → `clear to close out and merge` absent from stdout **and** the overall verdict reflects it |
| 5 | The **error message** at `:134-135` names "or the gate was never armed" as an alternative cause | grep the corrected string — it must not assert bypass as the only explanation |
| 6 | **Reports only, never auto-arms**; remedy line present | assert `git config --global core.hooksPath .githooks` in failure output; assert repo config **unchanged** after a run |
| 7 | `run_all.py` stays green | 15/15 (14 today; the new file joins by glob, no wiring) |

---

## Steps

**1 · RED.** New `.agents/scripts/tests/test_hooks_armed.py`, stdlib-only, `_harness.Cases` + `TempDir`.
Fixtures: armed · `hooksPath` unset · resolves to an empty dir · hook present but **not executable** ·
`*-ENFORCE` missing · a 5th hook added (proves derivation) · **negative control:** a fully armed repo
reports clean. Run bare, paste the RED, read *which line raised*.

> ⚠️ **AUDIT FINDING (Phase 3 — empty input).** A repo with **no `.githooks/` at all** must be a
> FAILURE, never a pass. Derived-set logic that finds nothing to check and reports clean is a vacuous
> green — the precise failure class this ticket exists to close, reintroduced one level up. Add the
> fixture, and assert an empty derived set is non-zero.

**2 · GREEN — the helper.** New `.agents/scripts/hooks_armed.py`. Importable both ways with no new
plumbing: `_harness.py:15` already puts `.agents/scripts/` on `sys.path`, and Python puts a script's
own dir on `sys.path[0]`, so `task_preflight.py` imports its sibling directly. Returns structured
results; the callers decide how to present them.

> ⚠️ **AUDIT FINDING (Phase 1 — script row).** A new `.agents/scripts/*.py` needs its row in
> `.agents/scripts/INDEX.md`. Missing from the plan; add it in this step.

**3 · Extract, do not duplicate.** Repoint `test_main_push_gate.py`'s INSTALLED block at the helper.
**Characterization-first** — that file is 4 commits old and passed a hard adversarial review. Its
57/57 is the invariant; if the count moves, the extraction is wrong.

**4 · Wire `task_preflight.py`.** Report the arm state beside `LANE: LOCAL|HANDOFF`, and correct the
`:132-135` comment to state its precondition rather than assume it.

**5 · SOP.** `.agents/scripts/*.py` is a usage surface — `workflows_testing_SOP.md` stages in the
**same commit**, per the armed `sop_currency` gate. `[sop-ok]` is for the artifact stamp only.

**6 · Gates, run bare** (a pipe returns the *pipe's* exit code): `run_all.py` · `workflow_lint.py
--toolkit-only` · `test_main_push_gate.py` · **`test_task_preflight.py` and
`test_closeout_preflight.py`** — the direct tests of the file Step 4 edits — · `task_preflight.py`
itself against this lane.

---

## Overlap and landing order

`chore/SCC-113-jira-in-progress-seam` is **live with zero commits and a dirty tree** — the unready-lane
shape SCC-99 describes. It touches `.claude/hooks/INDEX.md`, `.agents/.sync-manifest.json`, and
generated `.opencode/` + `.agents/workflows/` doors.

Today the sets **do not overlap**. They would if this lane adds a command or touches the hook
inventory — neither is planned. `git diff` cannot see untracked work, so **re-derive before landing**;
SCC-113's commit set does not exist yet.

## Risks

- **Extraction breaks a 4-day-old reviewed test.** Mitigated by treating 57/57 as the invariant.
- **`task_preflight.py` is 661 lines and load-bearing.** Additive change only; no restructuring.
- **The helper becomes a second source of truth.** Exactly why Step 3 extracts rather than copies.

---

## Self-Audit (2026-08-11)

**Right-size: FULL** — the plan touches a script other scripts import (`task_preflight.py`), adds a
module a test imports, and concerns a gate. Mode: PRE-WORK. Nothing is built.

**Phase 0 — scope · checkable list · traceability.** Change set: NEW `hooks_armed.py` · NEW
`test_hooks_armed.py` · EDIT `test_main_push_gate.py` (extract) · EDIT `task_preflight.py` ·
EDIT `workflows_testing_SOP.md` (currency) · NEW artifact folder. All 7 acceptance items trace to a
step and every step traces back; the only step without an acceptance item is Step 5 (SOP), which is
the armed `sop_currency` gate's requirement, not scope creep. **Lane check: no deployable path in the
set — `LANE: LOCAL`, closes via `/smh-close-task-merge-tree`.**

**Phase 1 — blast radius.** ⭐ The premise was challenged first, since the plan's whole claim is that
most of the ticket is already built. **Verified by reading, not by trusting the plan:**
`test_main_push_gate.py` L81-119 does assert exists · executable · `MAIN-PUSH-ENFORCE` · `hooksPath`
set · resolves · per-worktree. `run-hook.sh` does fix the exit-127 class and does state the
Claude-only layer is deliberately non-load-bearing. Both "do not rebuild" claims are TRUE.
**GAP 1 was also challenged and survives:** `test_sop_currency.py` references `SOP-ENFORCE` only at
L106/L128, where it *writes* the marker into a temp fixture — it never asserts the real repo's flag.
No test asserts `commit-msg`, `pre-commit` or `post-commit` is installed. **3 of 4 hooks and 2 of 3
flags are genuinely unasserted.** Cleared in one line each: no command file, no command rename, no
rule, no file move, no `_artifacts/_memory/` write, no platform door change.

**Phase 2 — over-engineering.** One tripwire examined and **justified, not waved through**: *a new
script where an existing one grows a subcommand.* `hooks_armed.py` must be imported by both a test
and `task_preflight.py`; folding it into preflight would make every test importing it drag in 661
lines of unrelated machinery. A small dedicated module is the simpler thing, not the fancier one.
*Generalizing for N=1* does **not** fire — N is 4 hooks and 3 flags today. *Rebuilding what exists*
fired during drafting and is what produced the reframe.

**Phase 3 — pre-mortem.** Other machine: no bare `python` introduced; the helper runs under whatever
already invokes `run_all.py` and preflight. Fresh clone: the literal subject. Empty input: **caught,
see finding 3.** Escape hatch: report-only by design, so none needed — and no flag was added, since
no acceptance item asks for one. Four platform caches: N/A, no menu surface changes. Sibling lands
first: `chore/SCC-113-jira-in-progress-seam` is live with **zero commits and a dirty tree**; today the
sets do not intersect, but `git diff` cannot see untracked work — **re-derive before landing.**
Rollback: purely additive, one revert; nothing irreversible.

### Findings

| Where | Sev | Failure scenario | Disposition |
|---|---|---|---|
| Step 1 fixtures | **HIGH** | A repo with no `.githooks/` yields an empty derived set, nothing to check, and the reporter says clean — a vacuous green reintroducing this ticket's own failure class one level up | **Baked in** — fixture added; empty set must be non-zero |
| Acceptance #4 / Step 4 | **MED** | Preflight prints `NOT ARMED` in prose while its top line still reads as success. A warning nobody reads is not a gate — the exact reason `JIRA-ENFORCE` exists | **Baked in** — the verdict must reflect it, not only the prose |
| Step 2 | **MED** | A new `.agents/scripts/*.py` with no row in `scripts/INDEX.md`; the index silently drifts from disk | **Baked in** |
| Step 6 | **LOW** | `run_all.py` named but not `test_task_preflight.py` / `test_closeout_preflight.py`, the direct tests of the edited file | **Baked in** |

**Landing-order dependency:** none blocking. SCC-113 shares no file with this set *today*; its commit
set does not yet exist, so the check is owed again at close-out, not assumed from this reading.

**Four gates.** Verification strategy — present; every acceptance item names the command that proves
it. Irreversible — nothing; additive only, no delete, no rename, no transition. Vague steps — Step 3
was the risk ("extract") and is pinned by a hard invariant: 57/57 must not move. Convention fit —
artifacts location, `_harness` import seam, derive-don't-hardcode, and the SOP-currency pairing all
match existing law.

```
Audit verdict: GO
```

---

## Self-Audit #2 (2026-08-11) — second independent pass, operator-invoked

**Right-size: FULL.** Mode: PRE-WORK. Audit #1 was written by the same author as the plan; this pass
exists to attack **#1's conclusions**, not to repeat its walk. Phases 0 and 2 are skipped with cause —
scope and the over-engineering gate were settled and nothing has changed. Phases 1 and 3 re-run
against **source that #1 quoted but never opened.**

### ⛔ Finding A — Audit #1 mischaracterised `task_preflight.py:132-135`. So did the ticket.

The claim carried through three Jira comments and the plan: *preflight infers the hook ran, and
therefore prints "clear to close out and merge" on an unarmed clone.* **The code was never read.
Reading it now (L127-139) shows that is wrong.**

The comment sits inside `elif m.group(1) not in allowed:` — the **error** branch. It fires only when
the branch's project key does **not** match the repo, and the very next statements are `rep.err(...)`
and `return None`. The inference explains *why reaching an error path is surprising*; it never grants
a pass. **There is no false "clear to merge" here.**

What survives is smaller and real: the error text asserts *"a wrong-project key means these commits
skipped the hook"* as the sole explanation, when **"the gate was never armed on this machine"** is
equally consistent — and is the likelier cause on a fresh clone. That is a **message-accuracy** defect,
not a false-pass defect.

**Disposition:** acceptance item 5 rewritten from "correct the false inference" to "name the
alternative cause in the message." GAP 2's real content is unchanged and still stands on its own:
**preflight never reports arm state at all.** That was always the substantive gap; the "smoking gun"
framing was overstated and is withdrawn. The ticket is corrected too.

### ⛔ Finding B — "derive, don't hardcode" cannot be absolute. The flag→gate mapping is underivable.

`.githooks/commit-msg` dispatches **two** scripts: `commit-msg-jira.sh` (armed by `JIRA-ENFORCE`) and
`sop-currency.sh` (armed by `SOP-ENFORCE`). Two flags, two scripts, **one hook file.** `SOP-ENFORCE`
corresponds to no `.githooks/sop` — so no filename-derivation can answer "which gate does this flag
arm." Acceptance item 2 as written asked for something impossible.

**Disposition:** derive the two sets independently — hooks present in `.githooks/`, flags present in
`git-hooks/` — and treat the flag→script pairing as a small **declared** table with a comment saying
why it cannot be derived. Item 2 rewritten.

### ⭐ Finding C — a genuinely silent off-path, found while reading for Finding B.

`.githooks/commit-msg` L26-27:

```sh
SOP="$ROOT/.agents/scripts/git-hooks/sop-currency.sh"
[ -x "$SOP" ] || exit 0
```

If `sop-currency.sh` is missing **or merely not executable**, the hook exits **0 with no output.** The
JIRA branch immediately above it announces the same condition loudly (`⚠ jira commit gate not present
in this worktree`). The SOP gate does not — it just vanishes. That is this ticket's exact failure class,
sitting in the hook the ticket is about, and neither the plan nor Audit #1 saw it because both worked
from the ticket's description instead of the hook body.

**Disposition:** new acceptance item 2b. The arm-check must report inner-script executability, not only
the dispatcher's. Fixing `commit-msg`'s asymmetry itself is **out of scope** — it is a hook-body change
with its own blast radius; file it as a follow-on from the walkthrough.

### Findings

| Where | Sev | Failure scenario | Disposition |
|---|---|---|---|
| Plan + 3 Jira comments | **HIGH** | The stated justification for GAP 2 does not exist in the code; work sized against a fiction | **Corrected** — item 5 rewritten, ticket comment owed |
| Acceptance #2 | **MED** | Asks for a flag→gate mapping that cannot be derived; the builder would either guess or hardcode silently | **Baked in** — declared table, with the reason |
| `.githooks/commit-msg:27` | **MED** | A non-executable `sop-currency.sh` disables the SOP gate with zero output, while its sibling announces | **Baked in** as item 2b; hook fix is a follow-on |

**Phase 3 re-run (external-state rows only).** Fresh clone — Finding C makes this *worse* than #1
thought and the plan now covers it. Sibling lane — `chore/SCC-113-jira-in-progress-seam` still zero
commits, still dirty, still no intersection; re-derive at close-out. Platform caches — unchanged, N/A.

**Standing lesson for this lane: three of four findings across both audits came from opening a file
that had been quoted but not read.** Step 3's extraction is the remaining place that risk lives —
`test_main_push_gate.py` must be read in full before it is edited, not skimmed for the block to lift.

```
Audit verdict: GO
```

