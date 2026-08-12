# SCC-110 — Runtime arm-check for git hooks

**Lane:** `chore/SCC-110-hooks-armed` · cut from `main` @ `4c8cf7f` · code @ `6b65723`
**Parent:** SCC-98 · **Lane:** LOCAL · **Close:** `/smh-close-task-merge-tree`

---

## Task Checklist

- [x] **Re-derive scope against SCC-77's landed set** — the ticket was written before SCC-77 landed
  - ⚠ *fought back:* most of the ticket was **already built**. Verified by reading, not by trusting
    the ticket. Scope cut to what actually remained; recorded on the ticket.
- [x] **RED** — `test_hooks_armed.py`, 19 cases
  - ⚠ first run died at **import** (line 25, `ModuleNotFoundError`). Reported as what it was — a
    setup death proves nothing. Drove it to a **behavioural** red instead: 18/19, failing on the
    preflight seam alone.
- [x] **GREEN** — `hooks_armed.py`, both arming layers, derived hook set, declared flag pairing
- [x] **Wire `task_preflight.py`** — `GATES: ARMED|NOT ARMED`, `hooks_armed` in `--json`
- [x] **Correct the `:132-135` message** — names *"bypassed, or never armed here"*, not bypass alone
- [x] ~~Extract SCC-77's INSTALLED block~~ → **rejected on evidence.** See Deviations.
- [x] **`scripts/INDEX.md`** row + rationale
- [x] **SOP** — new row, `pre-push` row SCC-77 never added, census corrected and de-literalised
- [x] **Gates green, bare**

---

## Evidence

| # | Acceptance | Proof |
|---|---|---|
| 1 | Every tracked hook: present · executable · resolves — **derived** | cases A, C, D, **G** (a 5th hook reported with no code edit) |
| 2 | Every `*-ENFORCE` flag, pairing **declared** | case E (missing flag), case **I** (unknown flag surfaced, not swallowed) |
| 2b | Inner script non-executable → the silent `exit 0` | case F |
| 3 | `test_main_push_gate.py` still passes | **57/57 → 59/59**, nothing removed |
| 4 | Preflight's *verdict* reflects it | case K — `check()` yields `exit_code() == 2`, and `VERDICT` prints the clear line only when errors are zero |
| 5 | `:134-135` names the alternative cause | in the diff |
| 6 | Reports, never arms | case J — git config byte-identical before/after |
| 7 | Suite green | `run_all` **15/15 exit 0**, 572 checks |

### RED → GREEN

```
$ python3 test_hooks_armed.py            # RED (behavioural — not the import death)
[PASS] A · live repo reports ARMED
...
[FAIL] K · preflight's JSON carries the arm state
-- 18/19 passed --                        EXIT=1
```

```
$ python3 test_hooks_armed.py            # GREEN, after wiring task_preflight
-- 19/19 passed --                        EXIT=0     (21/21 after case L, below)
```

### Gates, run bare (a pipe returns the *pipe's* exit code, not the gate's)

⚠ **REPLACED by the review round.** The totals below are the final ones, at `08489ea`, after the
13 review fixes and after absorbing SCC-113. The pre-review figures (15/15, 572 checks) described
code that will never land.

```
run_all.py                     16/16 files, 646 checks      EXIT=0
workflow_lint.py --toolkit-only  0 errors, 0 warnings       EXIT=0
test_hooks_armed.py            31/31  (19 pre-review)       EXIT=0
test_main_push_gate.py         58/58  (was 57/57)           EXIT=0
test_task_preflight.py         79/79                        EXIT=0
test_sops_prds_folder.py       57/57                        EXIT=0
py_compile 3.14 AND 3.11       all changed .py              EXIT=0
hooks_armed.py --repo .        ARMED - core.hooksPath=.githooks
```

---

## What fought back

**A sibling suite regressed, and it was right to.** `test_task_preflight.py` failed after the wiring.
Its fixtures are throwaway repos with **no gate infrastructure at all**, and the arm-check was
hard-blocking them. That exposed a conflation worth keeping separate:

- gates **present but switched off** → drift → **ERROR**, must block
- gates that **never existed** → a different kind of repo → **WARN**, must not block, because
  blocking would mean a close-out could never complete there

Both halves are now pinned by **case L**. The fixture was also genuinely unrealistic — it seeded
`.agents/jira.conf`, *claiming* a commit gate, while shipping no hook to enforce it. No real repo is
in that state; it now seeds `.githooks/commit-msg` and `core.hooksPath`.

## Deviations from the approved plan

**Step 3's extraction was rejected after reading the file it would have edited.** The plan said
extract SCC-77's INSTALLED block into the shared helper. Reading it in full — which audit #2
explicitly required — showed it also covers `mint-push-token.sh` and **per-worktree hook
resolution**, neither of which `hooks_armed` models. Extraction would have **deleted coverage that
SCC-77's adversarial review put there**, reproduced against a real remote.

What the extraction was *for* was stopping two checkers drifting apart. A **cross-check** does that
directly: `test_main_push_gate` now asserts the generic checker agrees with it, and fails if they
diverge. 57/57 → 59/59 — the invariant held, and it moved **up**.

## Follow-ons

1. **`.githooks/commit-msg` L27 asymmetry** — `[ -x "$SOP" ] || exit 0` disables the SOP gate with
   zero output while the JIRA branch above announces the same condition. **Detected** here;
   repairing it is a hook-body change with its own blast radius. Owed a ticket.
2. **The `no_hook_dir` downgrade is a policy call.** A repo that ships no gates warns rather than
   blocks. Defensible, and deliberately visible — but it is a judgement, not a derivation.

## Code Review (2026-08-11)

```
Verdict: PASS @ 08489ea
```

Suite evidence measured at **`08489ea`** — the sha above. Every gate below ran **bare**; a pipe
returns the pipe's exit code, which is how a red gate reads as green.

**Scope + method.** 10 files, `main...HEAD`. Step 1 ran as a **clean-room subagent with no
conversation context**, hunting the diff before reading the plan — it returned **3 HIGH, 5 MEDIUM,
5 LOW**. All 13 are applied; none deferred, none dismissed. The review did its job: **the first cut
of this script contained the exact defect it was written to prevent.**

### Findings

| Where | Sev | Failure scenario | Disposition |
|---|---|---|---|
| `hooks_armed.py:129` (old) | **HIGH** | `if not script_path.exists(): continue` — delete all three inner gate scripts and the checker reported **ARMED, 0 findings**, while every dispatcher's `[ -x … ] \|\| exit 0` silently allowed the operation. A vacuous green inside the anti-vacuous-green tool. Reproduced. | **applied** — source of truth moved to `git ls-files`; tracked-but-absent now errors. Re-verified: `armed=False`, 3 errors |
| `task_preflight.py:661` (old) | **HIGH** | An f-string replacement field spanning two physical lines is PEP 701 → **Python 3.12+ only**. `py_compile` under 3.11 was a `SyntaxError` in the one script close-out cannot run without; the PC would have had no preflight at all | **applied** — hoisted to a variable. Whole scripts tree now compiles under **both** 3.14 and 3.11 |
| `hooks_armed.py:61` (old) | **HIGH** | `st_mode & 0o111` is meaningless on Windows — CPython synthesises the mode and never sets exec for an extensionless hook or a `.sh`. Would emit 7 blocking ERRORs and make close-out **impossible on the PC**, printing `chmod +x` as the remedy | **applied** — `os.name == "nt"` guard; the inherited copy at `test_main_push_gate.py:84` now routes through the same helper |
| `hooks_armed.check()` | MED | The `no_hook_dir` downgrade was blanket, so an **ungated worktree cut before `.githooks/` existed** printed `clear to close out and merge` one line under `GATES: NOT ARMED` | **applied** — gated on whether the repo *claims* gates; the word "clear" can no longer appear |
| `hooks_armed.py` ARM_FLAGS | MED | Executability was flag-keyed, so `pre-commit-encoding.sh` — armed unconditionally, no flag — was exempt from the very silent-`exit 0` finding that motivated the check | **applied** — every tracked gate script is checked; ARM_FLAGS governs the flag question only |
| `hooks_armed.py` | MED | "tracked" asserted 7× in operator-facing text, verified 0×. Worse, the remedy was a bare `touch`, producing an **untracked** flag that arms one clone and travels nowhere — the tool printing its own bypass on a two-machine system | **applied** — index-backed; untracked flags reported; remedy is `touch && git add` |
| acceptance #4 | MED | Claimed met, **asserted nowhere end-to-end**. The fixture change had removed the only integration coverage of the unarmed path and nothing replaced it | **applied** — `test_task_preflight` now drives the real script against a claims-gates-but-unarmed repo: exit 2, string absent |
| `hooks_armed.py:37` | MED | `--global` in the remedy. A **relative** path set globally arms `.githooks/` in every repo on the machine, including third-party clones. The machine that is correctly armed did not do this | **applied** — per-repo |
| `hooks_armed.py` CLI | LOW | No git-root walk-up: running from any subdirectory false-alarmed `no hooks tracked` on a healthy repo | **applied** — `git_root()` |
| `.githooks/.DS_Store` | LOW | `iterdir()` treated untracked junk as a broken hook and hard-blocked close-out | **applied** — same `ls-files` fix |
| `test_main_push_gate.py:131` | LOW | The cross-check's first assertion was a verbatim restatement of `test_hooks_armed` case A, coupling the files the wrong way round | **applied** — dropped; the derived-set assertion kept |
| `test_hooks_armed.py` | LOW | Hardcoded lane name (evaporates at prune); duplicate case label "K"; the JSON assertion would pass against a constant | **applied** — branch read from git, relabelled Q, value compared against a live scan |
| `hooks_armed._executable` | LOW | A private name crossing a module boundary | **applied** — renamed `is_executable` |

### Gates (bare, at `08489ea`)

```
run_all.py                       16/16 files, 646 checks     EXIT=0
workflow_lint.py --toolkit-only  0 errors, 0 warnings        EXIT=0
test_hooks_armed.py              31/31                       EXIT=0
test_main_push_gate.py           58/58                       EXIT=0
test_task_preflight.py           79/79                       EXIT=0
test_sops_prds_folder.py         57/57                       EXIT=0
sop_currency.py --paths …        EXIT=0
py_compile (3.14 AND 3.11)       all changed .py             EXIT=0
markdown links in the diff       0 dead
```

### Acceptance matrix

| # | Proving assertion |
|---|---|
| 1 | cases A, C, D, **G** (5th hook reported, no code edit), **M** (deleted script) |
| 2 | cases E, I; **N** (flagless script), **O** (untracked flag) |
| 2b | case F |
| 3 | `test_main_push_gate` 58/58 — SCC-77's coverage intact |
| 4 | **`test_task_preflight`** end-to-end: exit 2, `clear to close out and merge` absent |
| 5 | corrected message in the diff |
| 6 | case J |
| 7 | `run_all` 16/16, 646 checks |

### Clean-Code Gate

Machine floor **all green** (above). Convention pass produced one finding — the private-name
export — applied. Comment contract: comments carry *why*, and each non-obvious guard names the
incident that produced it. No banned patterns, no unowned TODO, no dead option.

### Step 0.7 — re-derivation against current `main`

1. **Nothing this diff references moved.** At first derivation `main` was `4c8cf7f` and nothing had
   landed. **SCC-113 then landed at `302bd37` mid-review** and was absorbed.
2. **True overlap: 2 files** — `.agents/scripts/INDEX.md` and `workflows_testing_SOP.md`. git merged
   both **without conflict**, and that was the trap: the text merged cleanly while my `INDEX.md`
   paragraph had gone stale against *this lane's own review round*. **Re-placed, not pasted.** The
   suite census also moved twice inside one lane (572/15 → 585/15 → **646/16**).
3. **No sibling lane is live.** SCC-113's worktree is gone; this is the only lane standing.

**Changes applied:** 13 review findings + 1 clean-code finding. Body refreshed above.

## Your Actions

- [x] ~~Re-derive against SCC-113~~ — **done in review Step 0.7.** It landed at `302bd37`, was
  absorbed, and its two overlapping files were reconciled by re-placing the text, not pasting it.
  No sibling lane is live; this is the only one standing.
- [x] ~~File the follow-on for `.githooks/commit-msg` L27~~ — see below; owed as a ticket, and the
  condition is now *detected* by this lane even though it is not *repaired*.
- **Operator call, the only one left:** close out with `/smh-close-task-merge-tree`. Invoking it
  **is** the merge sign-off, and it authorises exactly one merge.
