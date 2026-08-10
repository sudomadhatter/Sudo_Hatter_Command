---
name: agy-canonical-test-venv
description: "AGY's canonical test venv is backend/.venv, on PYTHON 3.11 since 2026-08-01 (3.14 was silent drift — pytest never checks requires-python). Root .venv deleted AGAIN; runner flags live in the requirements.txt runner-note, serial-canonical until the xdist tail-hang closes."
metadata: 
  node_type: memory
  type: project
  originSessionId: 30744fcc-6564-4642-9fca-b7b7aacb854f
  modified: 2026-08-04T01:16:02.850Z
---

## 2026-08-01 — realigned to Python 3.11 (was silently 3.14)

Every local gate had drifted to **3.14** while CI, prod (`Dockerfile`) and ruff all target **3.11** —
undetectable because `pyproject.toml` declared no `requires-python`, and **pytest never checks that
declaration** (only pip and the CI assert step do). Fixed: `backend/.venv` rebuilt from 3.11.9 at the
CURRENT workspace path, `requires-python = ">=3.11,<3.12"` declared, CI asserts it pre-install. The
honest caveat (desktop team's A0 sweep of 245 transcripts): **zero observed failures were ever
3.14-caused** — the migration is CI/prod-parity insurance; the symptom people actually hit was the
stray root venv below. On OTHER machines the stale-venv trap re-opens silently — the walkthrough is
`_my_resources/migrations/install_guides/python_vytest-updates-other-machines.md` (renamed 2026-08-01 from
python-311-test-infra-other-machines.md; now also carries the vitest suite-lock notes).

**Runner flags now live in ONE place**: the runner AIDEV-NOTE in `backend/requirements.txt` (specs
reference it, never hardcode). **PARALLEL is gate-canonical since 2026-08-03** — `-n auto --dist
loadfile`, matching `pr-check.yml`; the tail-hang that held it serial is closed (see
[[governance-gate-scans-venv]]).
Big dir-level runs self-serialize machine-wide via the conftest suite lock — a queued run sits at
~0 CPU and is healthy, not hung.

AGY_AVIATIONCHAT's **canonical venv is `backend/.venv`** — it holds the full pinned deps incl. `pytest-cov==7.1.0` (pinned `backend/requirements.txt:48`, the TEA-5 coverage instrument, active in CI `pr-check.yml:57`). All project config (pyrefly.toml, both pyrightconfig.json, .vscode/settings.json) points at `backend\.venv`. The root `.venv` was officially **deleted 2026-05-30 and should NOT exist** (active-context "Known V2 Pitfalls": "Don't recreate a root venv"). A stray, incomplete root `.venv` has reappeared and **lacks pytest-cov**.

Running the keyless backend suite with that **stray root `.venv`** produces one spurious failure — `backend/tests/test_coverage_instrument.py::test_pytest_cov_is_installed` (`ModuleNotFoundError: pytest_cov`). It is NOT a real gap: `backend/.venv` passes it (2 of 2) and the full keyless suite is green there (2161p/2s/0f, 2026-07-03).

**Why:** the sprint-status tea-8 close-out misrecorded this exact spurious failure as a recurring "pytest-cov not installed, TEA-5 env gap," which then misled the tea-13 session into rationalizing a wrong-venv artifact as a known pre-existing failure. Corrected in the log 2026-07-02.

**How to apply:** run AGY pytest with `backend/.venv/Scripts/python.exe -m pytest backend/tests -o addopts=""` (add `GEMINI_API_KEY=""` for the keyless gate per TEA-2's guard; `JAVA_HOME` only for the tea-12 rules emulator — see [[firestore-rules-tests-need-java]]). If the ONLY failure is `test_pytest_cov_is_installed`, you used the stray root venv — re-run in `backend/.venv` before calling it a regression; consider deleting the stray root `.venv`. Relates to [[test-debt-stories-are-characterization]].
