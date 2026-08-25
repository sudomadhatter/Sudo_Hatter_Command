# Implementation plan — make the enforcement suite run on Windows

**Date:** 2026-08-25 · **Ticket:** SCC-321 · **Epic:** SCC-33 (CI/CD For Sudo Dev System)
**Workspace:** `_main` (lobby) · **Lane:** `TASK` (`.agents/scripts/**` is toolkit — full lane)

---

## 1. The situation, measured

`python .agents/scripts/tests/run_all.py` on **clean `main`**, this PC:

```
43/61 files passed        <- with bash resolving to WSL
44/61 files passed        <- with C:\Git\bin ahead of system32 (Git Bash)
43/61 files passed        <- AFTER Developer Mode on (step 1 done)
```

⚠️ **Step 1 landed but the headline number did not move — and the reason is not a failed fix.** The
composition changed:

| | File | Why |
|---|---|---|
| ✅ **fixed** | `test_workflow_lint` | Developer Mode. Real, verified. |
| ❌ **new** | `test_check_maps` | **Self-inflicted, not portability.** Writing this very plan created `_artifacts/_main/2026-08-25_SCC-321-windows-suite-portability/` without its `INDEX.md` row. Costs one line to repair. |
| ❌ **new** | `test_flight_recorder` | PATH-dependent (class 3b). Present all along; the earlier 17-file list was taken from the **44/61** run, where `C:\Git\bin` was on PATH and `sh` resolved. |

**So the honest read of step 1 is +1, not 0** — and the baseline for the remaining work is **17
genuine Windows failures**, not 18. Recording this because a flat 43→43 looks like the step did
nothing, and repeating it would be the wrong lesson to draw.

**Every one of those 17–18 failures is Windows-only.** They pass on the Mac. The suite was authored
there, and this machine has not been driving it, so nothing ever forced the portability question.

⛔ **The consequence, stated plainly: no lane worked on this PC has ever had a fully green gate.**
`run_all.py` is what `/smh-close-task-merge-tree` and `/cicd-push-e2e` run before anything lands, so
on this machine the gate has always been "green except the usual 18" — which is indistinguishable
from a real regression, and trains everyone to wave it through.

## 2. Root causes — six classes, measured not guessed

| # | Class | Evidence | Tests |
|---|---|---|---|
| 1 | **Symlink privilege** — ✅ **RESOLVED 2026-08-25** | `OSError [WinError 1314] A required privilege is not held`. Developer Mode now **on**; a non-elevated `os.symlink` succeeds | ~~`test_workflow_lint`~~ **now passes** |
| 1b | **POSIX permission semantics** — *was misfiled under class 1* | `chmod`'d executable stays writable; *"the freeze is not holding"*, *"a scenario mutated a SHARED inode"*. `os.chmod` on Windows only toggles the read-only **attribute**, and not for the owner. Developer Mode did **not** touch this | `test_repo_template` |
| 2 | **POSIX-only API** | `AttributeError: module 'os' has no attribute 'getuid'` | `test_allow_scratchpad` |
| 3 | **Windows absolute path unrecognized** | `run-hook.sh:33` matches only `/*`. `C:\…` falls to the relative branch and gets `$ROOT/` prefixed → *"not found — skipped"* | `test_allow_readonly_chain` (E2E case) |
| 3b | **Hardcoded POSIX shell name** | `subprocess.run(["sh", …])` → `FileNotFoundError [WinError 2]`. **`sh` is not on PATH on this machine at all** (Git Bash ships `C:\Git\bin\sh.exe`; that dir is not on PATH). PATH-dependent, which is why it was absent from the 44/61 list | `test_flight_recorder` |
| 4 | **Path separators & the drive-letter colon** | `FAILED: a colon in the path: the importer is still tagged [importer]` — a `C:` drive letter breaks colon-delimited parsing; `cd …/wfscripts-x/.agents && ls` mixes `\` and `/` | `test_cwd_escape_hook`, `test_evidence_extract`, `test_sops_prds_folder` |
| 5 | **Windows file locking** | `PermissionError [WinError 32] The process cannot access the file because it is being used by another process` — POSIX lets you unlink an open file; Windows does not | `test_mutation_sweep` |
| 6 | **Unclassified — need individual diagnosis** | assorted assertion failures | `test_gate_receipt`, `test_hooks_armed`, `test_install_git_hooks`, `test_jira_ticket`, `test_link_worktree_assets`, `test_main_write_gate_ci`, `test_risk_seam`, `test_ship_preflight`, `test_suite_runner` |

### The one piece of good news

`run-hook.sh` was tested three ways directly. A **relative** path — which is what
`.claude/settings.json` actually wires — dispatches and runs correctly (exit 0, silent). So **the live
hooks on this machine are not broken.** Only the absolute-path form fails, which is what the test
harness passes. Class 3 is a genuine portability bug worth fixing, but it is not a live outage, and
the plan should not be sold as if it were.

## 3. Machine-level findings — separate from the code, and real

Three environment defects found while diagnosing. **None is a test bug; all three would mislead
anyone judging a failure.**

| Finding | State | Note |
|---|---|---|
| **`bash` resolves to WSL** | `C:\WINDOWS\system32\bash.exe`. Git Bash exists at `C:\Git\bin\bash.exe` but that dir is **not on PATH** | WSL sees `/mnt/c`, Git Bash sees `/c` — verified by running both. Every `.sh` in this repo is written for Git Bash. Putting Git Bash first fixed exactly **one** test (43→44) |
| **`python` ≠ `python3`** | `python` → 3.11.9 (**AGY's venv — `VIRTUAL_ENV` is active in this shell**); `python3` → **3.14.0** at `C:\Python314`. The venv ships no `python3.exe` | A script probing `python3` first gets a different interpreter with different site-packages than one probing `python`. Four Pythons are on PATH (venv 3.11, 3.14, 3.11, 3.10) |
| **Developer Mode** ✅ **ON as of 2026-08-25** | `AllowDevelopmentWithoutDevLicense = 1`; verified by a **non-elevated** `os.symlink` succeeding, not by the flag alone | Operator-only (HKLM). ⛔ **On Windows 11 22H2+ it lives under Settings → *System* → For developers**, NOT Privacy & security — that older path is what every Win10-era doc says and it sends you to a page that does not exist. `ms-settings:developers` opens it directly. This box is **Home**, so `secpol.msc` is absent and Developer Mode is the only non-elevated route to the symlink privilege |

⛔ **Do NOT "fix" the bash problem by reordering the global PATH.** Putting `C:\Git\bin` ahead of
`system32` changes what `bash` means for every program on the machine, WSL included. The house rule
already says the right answer, and `run-hook.sh`'s own header states it: **"NEVER name one platform's
binary. Probe, in preference order, every time."** The fix belongs in the callers.

## 4. Approach

**Fix the environment first, re-measure, then fix only what remains.** With `bash` pointing at WSL and
`python3` at a different interpreter than `python`, some failures are environment and some are code,
and the failure text does not distinguish them. Changing test code to accommodate a misconfigured PATH
would bake the misconfiguration into the suite.

Order:

1. **Operator enables Developer Mode** (admin). Re-measure. Expect class 1 to clear (2 files).
2. **Align `python3`** so the probe order cannot select a different interpreter than `python`.
3. **Re-run and re-classify.** Only then is the remaining list genuinely code.
4. **Fix class by class, RED first**, smallest blast radius outward:
   - `run-hook.sh:33` — accept `[A-Za-z]:[\\/]*` as absolute alongside `/*` (class 3). Small, isolated, and it is a live dispatcher, so it goes first and alone.
   - `os.getuid` → a portable guard (class 2).
   - Path handling → `pathlib` / `os.sep`, and stop splitting on `:` where a drive letter can appear (class 4).
   - File locking → close handles before unlink, `ignore_errors` on teardown (class 5).
   - Class 6 individually.
5. **Both machines must stay green.** Every change is a twin-platform change; a fix that greens Windows
   by breaking the Mac is a regression. The Mac run is the control and must be re-run before this lands.

## 5. Scope boundary

**In:** `.agents/scripts/tests/**`, `.agents/hooks/run-hook.sh`, and any script the tests prove is
platform-bound. **Out:** product code, and the `main` write gate (`.githooks/pre-push` is pure `sh` by
design and stays that way).

⛔ **A test that genuinely cannot run on a platform gets an explicit, NAMED skip — never a silent one,
and never a loosened assertion.** The entire value of this suite is that it fails loudly; "make it
green" is not the goal, "make it true on both machines" is.

## 6. Verification

- `run_all.py` → **61/61 on Windows**, and still 61/61 on the Mac.
- Both counts recorded in the walkthrough, per machine, naming the interpreter and the bash each resolved to.
- `docs/migrations/` gains the machine-prep steps that came out of §3, so the next machine does not
  rediscover this — the same gap SCC-320 just closed for Keyway.

## 7. Out of scope, recorded

- **SCC-320** — committed at `734cd509`, **unpushed**; the push was blocked by the auto-mode classifier.
- Lobby vault: 37 secrets in `development`, 0 in `production`; `Sudo_Hatter_Command` is public, so
  whether Keyway gates the vault on push or on read is an open vendor question.
- `.DS_Store` is tracked on `main` despite `.gitignore:77`; `chore/SCC-305-sop-start-here-table` already deletes it.
- `link-worktree-assets.py` does not cover `docs/migrations/auth_keys/`, so a fresh worktree reads
  `master.env` as a dead path in `check_maps`.

---

## 8. Landed so far — and two findings the diagnosis did not predict

**Approved 2026-08-25. Lane `chore/SCC-321-windows-suite-portability`.**

### 8.1 `run-hook.sh` — the absolute-path fix (class 3)

Measured before: a **relative** path dispatches, a **POSIX absolute** path dispatches, a **Windows
absolute** path prints `not found — skipped` about a file that exists. After: all four spellings
dispatch, and a genuinely missing file still reports — the control that proves the check did not
simply become unconditional.

⚠️ **The pattern needed testing, not reasoning.** The obvious spelling `[A-Za-z]:\\*` **does not
work**: the parser collapses `\\` to `\`, glob then reads `\*` as a literal asterisk, and it matches
nothing — silently. `[A-Za-z]:[\\/]*` is correct, verified in **both** bash-as-sh and dash.

⭐ **This bug was already diagnosed in this house, and recurred.** `test_main_push_gate.py`'s own case
C5 describes it exactly — *"an absolute `C:/…` answer does not match `/*`, so the repo root is glued
in front of it and the token goes somewhere that cannot exist"* — found in the push-gate scripts under
SCC-171/172. Those scripts were fixed and given a guard. `run-hook.sh` had the same line and no guard.

### 8.2 `_harness.posix_sh()` — one resolver, fifteen call sites (class 3b)

⛔ **`subprocess.run(["sh", …])` RAISES on Windows rather than returning a bad exit code**, so a whole
file died at the first such call and was reported as *one* failure. It was really "none of this ran" —
`test_allow_scratchpad` was scored 0 cases while showing the same red as a file with one bad
assertion. Nothing in `run_all`'s output distinguishes those two.

`posix_sh()` prefers `sh` on PATH, then derives Git Bash from `git --exec-path` (right whether git is
in `C:\Git` or `C:\Program Files\Git`), and ⛔ **rejects `System32\bash.exe`** — the WSL launcher,
which mounts this drive at `/mnt/c` and cannot read a `C:\` argument. `test_main_push_gate` had
half-built this already (`shutil.which("sh") or shutil.which("bash") or "bash"`) and then ignored its
own answer at eleven other call sites, with a `bash` tail that would have selected WSL.

### 8.3 ⛔⛔ FINDING — the main write gate was never behaviourally tested on this PC

`test_main_push_gate.py:277` was a bare `if os.name == "nt": return c.finish()`. **Unmarked,
unexplained, and it made the file print `15/15 passed`, exit 0** — on a machine that had tested none
of the gate's refusal ladder, none of the token path, and no real `git push`. This is the most
safety-critical gate in the system, and on this machine it was certified by static greps alone.

`tests-must-gate-for-real` §5 names this exactly: *a check that reports green having verified nothing
is worse than no check, because the green is believed.*

**Measured with a real shell resolved: 69 of 85 cases pass on Windows.** The 16 that fail are
POSIX-bound **fixtures** — e.g. a fake path chosen because it is unwritable on POSIX, which is
perfectly writable here — not platform limits. So this is owed work, not a wall. The silent return is
now a **named failing check**, deliberately red: it must stop reading as green before it is fixed.

### 8.4 Counts

| Run | Files | Note |
|---|---|---|
| baseline | 43/61 | |
| + Developer Mode | 43/61 | +1 real, −1 self-inflicted, −1 PATH-dependent (§1) |
| + INDEX repair | 44/61 | clean baseline: 17 genuine failures |
| + this commit | 44/61 | `test_flight_recorder` fixed; `test_main_push_gate` now honestly red |

⚠️ **The flat 44 is not stagnation and must not be read as it.** Inside those files: `flight_recorder`
green, `allow_readonly_chain` **145/149** (only the Windows-path `cd` cases left, class 4),
`allow_scratchpad` **145/186 running where 0 ran before**, `main_push_gate` **69/85 reachable**. The
file-level count is too coarse to show any of that, which is worth remembering when judging the next
step by it.

## 9. Remaining, classified

| Class | Work | Files |
|---|---|---|
| 1b | `os.chmod` on Windows toggles only the read-only attribute — the fixture "freeze" does not hold | `test_repo_template` |
| 2 | 41 uid-root ALLOW cases: on Windows the hook grants via `.claude/scratchpad-root`, not a uid root | `test_allow_scratchpad` |
| 3c | 16 POSIX-bound gate fixtures (§8.3) | `test_main_push_gate` |
| 4 | Windows path / drive-letter colon in command parsing | `test_allow_readonly_chain` (block Q), `test_cwd_escape_hook`, `test_evidence_extract`, `test_sops_prds_folder` |
| 5 | `WinError 32` — unlink of an open file | `test_mutation_sweep` |
| 6 | Undiagnosed | `test_gate_receipt`, `test_hooks_armed`, `test_install_git_hooks`, `test_jira_ticket`, `test_link_worktree_assets`, `test_main_write_gate_ci`, `test_risk_seam`, `test_ship_preflight`, `test_suite_runner` |

---

## ⛔ Awaiting approval

Per the ARTIFACTS gate this stops here. **Step 1 needs the operator regardless** — Developer Mode
cannot be enabled from this session.
