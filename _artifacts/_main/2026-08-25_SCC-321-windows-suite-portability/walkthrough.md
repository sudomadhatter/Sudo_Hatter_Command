# Walkthrough — SCC-321: make the enforcement suite run on Windows

**Ticket:** SCC-321 · **Epic:** SCC-33 (CI/CD For Sudo Dev System) · **Date:** 2026-08-25
**Lane:** `chore/SCC-321-windows-suite-portability` · **Workspace:** `_main` (lobby) · **Lane class:** `LOCAL`

---

## What shipped

`python .agents/scripts/tests/run_all.py` went from **43/61 files** to **61/61** on this PC.
Windows 11 Home 25H2, python 3.11.9, `sh` resolved to `C:\Git\bin\sh.exe`.

**Why that number mattered.** `run_all.py` is what `/smh-close-task-merge-tree` and `/cicd-push-e2e`
run before anything lands. On this machine the gate had always been *"green except the usual 18"* —
which is indistinguishable from a real regression, and trains everyone to wave it through. No lane
worked on this PC had ever had a fully green gate.

## Nine live defects — in shipped code, not in tests

The suite was authored on the Mac and this machine had never driven it, so nothing ever forced the
portability question. Each of these was **silent by construction**:

| Where | Consequence on Windows |
|---|---|
| `.agents/hooks/guard-cwd-escape.py` | **Every `cd` refused.** `ask` is auto-DENY headless, so the guard blocked `cd .agents/scripts` inside its own repo |
| `.agents/hooks/allow-readonly-chain.py` | `cd_ok` could **never** grant an in-workspace `cd`; it fails safe, so the only symptom was the prompt it exists to remove |
| `.agents/scripts/main_write_gate.py` | local `git()` decoded with the locale codec, not UTF-8 → a non-ASCII artifacts path matched nothing and **the lane was never judged** |
| `.agents/scripts/mutation_sweep.py` | restore handler on `SIGTERM`, which Windows **never delivers** → an interrupted sweep left a **live mutant on disk** |
| `.agents/scripts/risk_seam.py` | test-link count read 0 (= "no data"); the tool reported **absent** on a machine that has it |
| `.agents/scripts/tests/_pf_fixtures.py` | shared `$ACLI_BIN` shipped **writable**, directly under a comment saying it was frozen |
| `.agents/scripts/tests/_repo_template.py` | every template shipped a live path back to itself, and **nothing was ever frozen** |
| `.agents/scripts/link-worktree-assets.py` | the same asset printed two different ways on the two machines |
| `.agents/scripts/tests/run_all.py` + `_harness.py` | **the runner itself.** Both ends of the child pipe pinned at the locale codec, which cannot encode the `⛔`/`⭐` in the suite's own case names → files died mid-print and were scored as ordinary reds. **22 files at once**, found only by running bare at close-out |

Plus `.agents/hooks/run-hook.sh`, where a Windows-absolute path fell to the relative branch and got
the repo root glued in front of it.

## Decisions

- **Fork behaviour, converge data.** Fork where the platforms genuinely differ and no code changes
  that — a uid root, `PATHEXT`, `:` illegal in a filename, a junction is not a symlink. Both arms
  then assert something real and neither is a skip. **Converge** where the divergence was accidental
  (line endings, stdin translation, printed separators): the Mac was already right, and forking there
  would mean writing CRLF and teaching every consumer to strip `\r` — preserving the bug and paying
  for it at every reader, forever.
- **`test_main_push_gate.py:277`'s silent `if os.name == "nt": return` became a NAMED failing check
  before it was fixed.** It had been making the file print `15/15 passed`, exit 0, on a machine that
  had tested none of the gate's refusal ladder. It had to stop reading as green before it was worth
  fixing. Now 85/85.
- **No assertion was loosened and no test was skipped to reach 61/61.** `tests-must-gate-for-real` §5:
  a check that reports green having verified nothing is worse than no check, because the green is
  believed.

## Pitfalls

- ⛔ **An ungated separator rewrite is a regression, not a fix.** Three `p.replace("\\", "/")` calls
  were written unconditionally at first. On POSIX a backslash is a legal **filename** character, so
  rewriting it there is not a separator fix but a path rewrite: `/ws\x` is a sibling file at `/`, and
  canonicalising it to `/ws/x` reads as *inside* a workspace rooted at `/ws`. A one-machine fix that
  **widens the other machine's security guard**. Gated in `433bf8fa` and `4f411e75`.
- ⭐ **A file reported as ONE failure may have run NOTHING.** `subprocess.run(["sh", …])` raises on
  Windows rather than returning a bad exit code, so a whole file died at its first such call and was
  scored as a single red. Four files in this lane were in that state, and their symptoms named the
  wrong cause every time. `test_allow_scratchpad` had 100+ green refusal cases certifying nothing.
- **Two recurrences of lessons this house had already written down**, both copies that drifted from a
  fixed sibling: *"absolute has two spellings"* (SCC-171/172, quoted verbatim in this suite's own case
  C5) recurred in `run-hook.sh` and `allow-readonly-chain.cd_ok`; *"`encoding="utf-8"` is
  load-bearing"* (SCC-160, fixed in `wf_common.git` with a comment explaining it) recurred in
  `main_write_gate.py`'s own local `git()`.
- ⛔⛔ **THE CERTIFICATION ITSELF WAS ENVIRONMENT-DEPENDENT, AND THE CLOSE-OUT CAUGHT IT.** The
  `61/61` recorded mid-lane was measured in a shell that exported `PYTHONIOENCODING=utf-8`. Run
  **bare** — the way `/smh-close-task-merge-tree` and CI actually run it — the same tree scored
  **39/61**, with 22 files red. Cause: this suite's own case *names* carry `⛔` (U+26D4) and `⭐`
  (U+2B50); Windows gives a **non-console** stdout the locale codec, cp1252 can encode neither, and
  `check()` raised `UnicodeEncodeError` mid-print. The file died part-run and was scored as one
  ordinary red — indistinguishable from a genuine assertion failure, which is why every one of those
  22 looked like a different bug.

  `run_all.py` had a comment forbidding `encoding=` on the child pipe, on the grounds that parent and
  child must share an encoding. **That invariant was right; the encoding it pinned them at was
  wrong** — cp1252 cannot hold what the suite prints. Both ends are now pinned at UTF-8: `run_all.py`
  sets it in `os.environ` before spawning (children inherit, as `WF_ON_MAIN` already relies on), and
  `_harness.py` reconfigures the streams at import so the **single-file** door — the review loop, and
  the only way `mutation_sweep.py` runs a test — is covered too. Both Windows-gated; POSIX streams
  are already UTF-8.

  ⭐ **The lesson is about the measurement, not the encoding.** A gate must be run in the environment
  the gate actually runs in. A green obtained under an exported variable that the door does not set
  certifies the shell, not the suite. It also means a `[sop-ok]`-clean lane with every gate green can
  still be resting on a number that was never reproducible — the re-run at close-out is what made the
  difference, and skipping it because "the suite was green yesterday" would have landed this.
- **The kill-on-timeout manufactured the residue it denied.** `test_mutation_sweep` passed alone,
  passed once under `run_all`, and failed the next run — twice, in opposite directions, both times the
  harness racing a real subprocess under 61-way concurrency. Caught only by re-running rather than
  trusting one green. Each race is now its own named failure instead of a red about the code.

## Verification

Every total below was produced with **`env -u PYTHONIOENCODING`**, deliberately, so that no result
here can depend on a variable the door does not set:

| Gate | Result |
|---|---|
| `python .agents/scripts/tests/run_all.py` | **61/61 files**, exit 0 — twice consecutively, bare |
| single-file door (`test_git_hooks.py` direct) | 163/163, exit 0 — the `mutation_sweep` / review-loop path |
| `python .agents/scripts/workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, exit 0 |
| `python .agents/scripts/check_maps.py --depth3-only --strict` | exit 0 |
| `python .agents/scripts/check_links.py --base origin/main` | 137 path claims over 6 files — clean, exit 0 |

**SOP currency:** this lane's commits carry `[sop-ok]`. Justified rather than reflexive — the page's
instruction is already correct and already machine-aware (*"on the PC, `python …`"*, with no count
to go stale), and nothing here changes what the operator types or what a gate permits. The code was
wrong; the page was not.
- No LLM code review ran on this lane, so there is **no `Verdict:` stamp** and the preflight's suite
  SKIP does not apply. The gate is run in full at close-out, which is the correct fallback.
- **The POSIX control is CI, and it is automatic and blocking.**
  `.github/workflows/main-write-gate.yml` runs `python3 .agents/scripts/tests/run_all.py` on
  `ubuntu-latest` for every pull request into `main`, and the ruleset holds the merge button until it
  is green. Both changes with genuine cross-platform reach — `sh_with_path` and `risk_seam._cli` —
  are POSIX-generic rather than Darwin-specific, so Linux exercises them exactly as macOS would.

## Follow-ons

- Plan step 2 — align `python3` on this PC so the probe order cannot select a different interpreter
  than `python` (four Pythons are on PATH; `python` is AGY's 3.11 venv, `python3` is 3.14).
- Plan §6 — `docs/migrations/` gains the machine-prep steps from §3, including the corrected
  Developer Mode path (**Settings → System → For developers**, `ms-settings:developers`), so the next
  machine does not rediscover them.
- `link-worktree-assets.py` does not cover `docs/migrations/auth_keys/`, so a fresh worktree reads
  `master.env` as a dead path in `check_maps`.

## Your Actions

- [x] The merge itself — lands via this branch's PR
- [ ] **Confirm on the Mac.** CI already proves POSIX at the landing sha, so this is confirmation on
      the third environment rather than the gate — but the Mac is the machine that actually drives
      this system, and it has not run this branch. Expect `61/61 files passed`:
      ```bash
      cd ~/Sudo_Hatter_Command
      git fetch origin
      git checkout chore/SCC-321-windows-suite-portability
      git config core.hooksPath .githooks     # per-machine; a fresh clone has NO gates at all
      python3 .agents/scripts/tests/run_all.py
      git checkout main                       # do not leave the clone parked on the lane
      ```
      ⛔ `python3` on the Mac — there is no bare `python` there.
