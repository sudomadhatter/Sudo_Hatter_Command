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

```
run_all.py                     15/15 files, 572 checks      EXIT=0
workflow_lint.py --toolkit-only  0 errors, 0 warnings       EXIT=0
test_main_push_gate.py         59/59  (was 57/57)           EXIT=0
test_sops_prds_folder.py       57/57                        EXIT=0
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

## Your Actions

- Review and close out with `/smh-close-task-merge-tree` — invoking it **is** the merge sign-off,
  and it authorises exactly one merge.
- `chore/SCC-113-jira-in-progress-seam` is live with **zero commits and a dirty tree**. No file
  overlap with this lane at the last read, but `git diff` cannot see untracked work — **re-derive
  before landing.**
