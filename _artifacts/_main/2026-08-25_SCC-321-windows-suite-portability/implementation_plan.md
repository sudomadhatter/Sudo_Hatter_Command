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

## 9. Complete — 61/61 on Windows

**Every file in §9's original classification is green.** Three consecutive full-suite runs at
**61/61**, on Windows 11 Home 25H2, python 3.11.9, `sh` at `C:\Git\bin\sh.exe`. The lane opened at
43/61.

### 9.1 The classification was wrong in an instructive way

The original six classes described *symptoms*. Two root causes accounted for most of them, and
neither was in the table:

| Root cause | Files it explained |
|---|---|
| **Text-mode newline translation** — `Path.write_text` and `subprocess(text=True, input=…)` both emit CRLF on Windows | `main_push_gate` and most of what looked like "assorted assertion failures" |
| **A stub binary Windows cannot see or launch** — `PATHEXT`, and no shebang support | `jira_ticket`, `risk_seam`, `ship_preflight` — two of which ran **zero cases** |

⭐ **The lesson worth keeping: a file reported as ONE failure may have run NOTHING.** `run_all`'s
file-level count cannot distinguish "one bad assertion" from "died at import". Four files in this
lane were in the second state, and their symptoms named the wrong cause every time.

### 9.2 Live defects found — in shipped code, not in tests

Each of these was **silent by construction**, which is why a suite nobody ran on this machine did
not surface them:

| Where | Defect | Consequence on Windows |
|---|---|---|
| `guard-cwd-escape.py` | containment test compared raw strings and appended a **forward** slash | **Every `cd` refused.** `ask` is auto-DENY in headless mode, so the guard blocked `cd .agents/scripts` inside its own repo |
| `allow-readonly-chain.py` | `cd_ok` spelled "absolute" as `startswith("/")` | The hook could **never** grant an in-workspace `cd` — it fails safe, so the only symptom is the prompt it exists to remove, on every command |
| `main_write_gate.py` | local `git()` decoded with the **locale** codec, not UTF-8 | A non-ASCII artifacts path came back mangled, matched nothing, and **the lane was never judged** — a close-out reaching `main` with nothing looking at it |
| `mutation_sweep.py` | restore handler on `SIGTERM`, which Windows **never delivers** | An interrupted sweep left a **live mutant on disk** — verbatim the SCC-144 incident the mechanism exists to prevent |
| `risk_seam.py` | `"/" not in subject`; `.exists()` on an extensionless pipx path | Test-link count read 0 (= "no data", so `untested` listed everything); the tool reported **absent** on a machine that has it |
| `_pf_fixtures.py` | launcher frozen inside the POSIX branch only | Shared `$ACLI_BIN` shipped **writable**, under a comment saying it was frozen |
| `_repo_template.py` | `str(root)` vs git's **backslash-escaped** config value; exec-bit selector | Every template shipped a live path back to itself; **nothing was ever frozen** |
| `link-worktree-assets.py` | `str(rel)` in printed output | The same asset printed two different ways on the two machines |

### 9.3 Two recurrences of lessons this house had already written down

- **"Absolute has two spellings"** — diagnosed under SCC-171/172, fixed in the push-gate scripts and
  quoted verbatim in `test_main_push_gate`'s own case C5. It recurred in **`run-hook.sh`** and in
  **`allow-readonly-chain.cd_ok`**, neither of which had a guard.
- **"`encoding="utf-8"` is load-bearing on the PC"** — fixed in `wf_common.git` under SCC-160, with a
  comment explaining it. `main_write_gate.py`'s own local `git()` never got it.

⭐ Both are copies that drifted from a fixed sibling. The fix landed where it was found; nothing
carried it to the other call sites.

### 9.4 Where a platform fork was right, and where it was wrong

The rule applied throughout: **fork behaviour, converge data.**

- **Fork** where the platforms genuinely differ and no code changes that — a uid root cannot exist on
  Windows, `PATHEXT` has no POSIX equivalent, `CreateProcess` appends `.exe` and nothing else, `:` is
  illegal in a Windows filename, a junction is not a symlink. Both arms assert something real; neither
  is a skip.
- **Converge** where the divergence was accidental — line endings, stdin translation, output
  separators. The Mac was already right. Forking there would mean writing CRLF and then teaching
  every consumer to strip `\r`: preserving the bug and paying for it at every reader, forever.

⛔ **And a fork that is not gated is a regression.** Three separator rewrites were written
unconditionally at first. On POSIX a backslash is a legal **filename** character, so rewriting it
there is not a separator fix but a path rewrite: `/ws\x` is a sibling file at `/`, and canonicalising
it to `/ws/x` reads as *inside* a workspace rooted at `/ws`. A one-machine fix that widens the other
machine's security guard is worse than the bug it closed. Gated in `433bf8fa` and `4f411e75`.

### 9.5 Flake, caught by not trusting one green

`test_mutation_sweep` passed alone, passed once under `run_all`, and failed the next run — twice, in
opposite directions. Both were the harness racing a real subprocess under 61-way concurrency: once
"the mutant had not been written yet", once "the restore had not finished, and the kill-on-timeout
manufactured the residue the case denies". Windows are generous now, and **each race is its own named
failure** rather than a red about the code. Verified with three consecutive clean full-suite runs.

---

## 10. ⛔ The Mac is the control, and it has NOT been run

**Nothing here is certified until `python3 .agents/scripts/tests/run_all.py` is green on the Mac at
this branch.** §5 binds it and every commit message on this lane repeats it.

The risk is auditable rather than guessed:

| Class | Mac impact | Count |
|---|---|---|
| Guarded by an early `return` on `os.name`, or an untouched `else` arm | Cannot execute — byte-identical | most |
| Same bytes, different code (`run_stdin_lf`, the `C:` path build, shim quoting) | POSIX text mode never translated, so the wire bytes are unchanged | 3 |
| **Mac behaviour genuinely changes** | needs the control run | **2** |

The two: **`sh_with_path`** (the shim now joins `$PATH` inside the shell rather than via `env=` — plain
POSIX, but it is the Mac's path changing) and **`risk_seam._cli`** (`shutil.which(path=…)` instead of
`.exists()`, so a *non-executable* file at `~/.local/bin/code-review-graph` is now skipped — strictly
more correct, and pipx sets the exec bit).

⛔ **This is an argument, not a measurement.** Run the Mac.
