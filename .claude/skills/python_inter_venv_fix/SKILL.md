---
name: python_inter_venv_fix
description: "Ground truth for this project's Python environment: which interpreter, which venv, which version. Use when the VS Code interpreter is wrong, imports show unresolved, Pylance/pyright/pyrefly can't resolve fastapi/google.adk, a test failure smells environmental rather than logical, or pytest dies before running any test (tmp_path / basetemp errors)."
---

# Python environment — ground truth

## The canonical environment (memorize this, it is the whole skill)

| | |
|---|---|
| **Interpreter** | `backend/.venv/Scripts/python.exe` — the *only* venv in this repo |
| **Python version** | **3.11** — matches CI (`pr-check.yml`), prod (`Dockerfile`), and ruff `target-version = "py311"` |
| **Enforced by** | `requires-python = ">=3.11,<3.12"` in `pyproject.toml` + a CI assert step |
| **Run tests as** | `backend/.venv/Scripts/python.exe -m pytest backend/tests -n auto --dist loadfile -q` |

Verify in one command — paste the output, don't assert from memory:

```bash
backend/.venv/Scripts/python.exe -c "import sys, fastapi, google.adk, pydantic; print(sys.version); print(sys.executable); print('deps OK')"
```

`sys.version` must start with **3.11**, and `sys.executable` must be under the **current** workspace.

---

## ⚠️ Two things this skill used to teach that are now WRONG

This skill was written for a repo state that no longer exists. If you have an older copy cached,
or you find these patterns anywhere, they are bugs:

### 1. "pyrefly.toml must stay ABSOLUTE with double backslashes" — **REVERSED**

`pyrefly.toml` is now **relative** and must stay that way:

```toml
project-includes = ["backend/**/*.py"]
search-path = ["."]
```

Absolute paths there are what pinned the config to one machine, broke the laptop lane, and are the
reason the `code-standards` §6 backend type check went unwired in CI for so long. `code-standards`
§5 bans machine-absolute paths in config. The file carries an `AIDEV-NOTE` saying so, ending
*"Do not reintroduce an absolute path or an interpreter pin."* Pyrefly resolves the interpreter from
the environment it is invoked with — that is what keeps CI and `backend/.venv` on the same one.

**Following the old instruction would re-break CI.**

### 2. "There may also be a stray root `.venv` — ignore it" — **IT'S GONE**

The duplicate root `.venv` was deleted on 2026-08-01. It was a partial environment missing
`pytest-cov`, and running the suite through it produced a spurious `test_pytest_cov_is_installed`
failure that looked exactly like a product regression. That phantom cost real time twice, and one
occurrence got written into `sprint-status.yaml` as a standing *"TEA-5 env gap"* known-failure note
that then misled two later close-outs before anyone caught it.

There is now exactly one venv. If you ever see a root `.venv` reappear, **delete it** — do not
work around it.

---

## Symptom → cause, in the order these actually happen now

### Pytest dies before running anything: `tmp_path` errors, "could not create `%TEMP%/pytest-of-<user>`"

**The most common real environment failure in this repo, and it has nothing to do with the venv.**

Looks catastrophic — dozens of setup errors at once, often with a pytest-bdd wrapper failure riding
along. It is the sandbox/OS denying pytest its default temp root, not your code and not your
interpreter.

Confirm it is environmental, then work around it:

```bash
# 1. Prove it's the temp root, not the tests — run ONE tmp_path test with a local base
backend/.venv/Scripts/python.exe -m pytest <one_tmp_path_test> --basetemp=./.pytest-tmp -q

# 2. If that passes, re-run the real suite with the same override
backend/.venv/Scripts/python.exe -m pytest backend/tests -n auto --dist loadfile -q --basetemp=./.pytest-tmp
```

**Put the basetemp somewhere disposable and gitignored — never inside `_artifacts/`.** A previous
run wrote it into a story's artifact folder and left directories git could not even stat, so
`warning: could not open directory … Permission denied` polluted every later `git status` in that
lane for two sessions.

The condition is intermittent. `%TEMP%` being writable today does not mean it will be next run.

### Imports unresolved / wrong interpreter in VS Code

The repo config is correct and portable — `pyrefly.toml`, `pyrightconfig.json`,
`backend/pyrightconfig.json` and `.vscode/settings.json` carry **no** machine-absolute paths
(re-verified 2026-08-01: repo-wide grep for a hardcoded user path in config returns zero hits).

So if the interpreter is wrong, it is almost certainly **VS Code's cached per-workspace pick**,
which lives outside the repo and will not auto-correct:

1. `Ctrl+Shift+P` → **Python: Select Interpreter** → `.\backend\.venv\Scripts\python.exe`
2. `Ctrl+Shift+P` → **Developer: Reload Window** (pyrefly does not hot-reload its config)
3. Still broken? `Ctrl+Shift+P` → **Python: Clear Cache and Reload Window**

Do **not** "fix" this by editing config paths. If you genuinely find a stale absolute path, that is
a §5 violation — fix it to a relative/`${workspaceFolder}` form, never to a new absolute one.

### A test fails for you but passes elsewhere (or vice versa)

Check the interpreter *first*, before debugging the test:

```bash
backend/.venv/Scripts/python.exe -c "import sys; print(sys.version, sys.executable)"
```

Wrong version or wrong path explains more "regressions" in this repo's history than any real bug.
Note that git worktrees under `.claude/worktrees/` may carry their **own** `backend/.venv` — check
which one you are actually invoking.

### Tracebacks naming a directory that doesn't exist

Cosmetic. `.pyc` bytecode compiled at an older venv location keeps the old `co_filename`, so some
frames print a dead path. Rebuilding the venv clears it. Ignore it while debugging — the line
numbers are still correct.

---

## Rebuilding the venv (rare — and it is disruptive)

Only when the venv is genuinely corrupt or on the wrong Python.

> **Check for live consumers first.** Worktrees under `.claude/worktrees/` may share this single
> venv, and other agent sessions may be running the suite out of it right now. Deleting it
> mid-run produces unattributable false-REDs in someone else's lane — see the
> `parallel-autopilot-shared-tree-gate` learning.
>
> ```powershell
> Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
>   Where-Object { $_.CommandLine -like "*AGY_AVIATIONCHAT*backend\.venv*" }
> ```
> Wait until that returns nothing.

```powershell
Remove-Item -LiteralPath backend\.venv -Recurse -Force
py -3.11 -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install --upgrade pip
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Then confirm the two pinned CI gate tools landed — both are hard gates and a silent miss is
expensive:

```bash
backend/.venv/Scripts/ruff.exe --version      # must be 0.16.0
backend/.venv/Scripts/pyrefly.exe --version   # must be 1.1.1
```

## Committing (provide the command — never run git yourself)

```powershell
git add .vscode/settings.json pyrefly.toml pyrightconfig.json backend/pyrightconfig.json
git commit -m "fix(env): <what you actually changed>"
```

## Related

- `.agents/rules/code-standards.md` §5 (no machine-absolute paths in config), §6 (ruff + pyrefly machine floor)
- `_artifacts/_main/2026-08-01_python-env-fix/` — the 3.11 migration, the symptom evidence behind this rewrite, and why the old guidance was inverted
