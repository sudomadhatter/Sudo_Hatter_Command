---
name: python_inter_venv_fix
description: "Quick-fix when VS Code 'Select Python Interpreter' won't connect to the project .venv, or imports show as unresolved / type-checking breaks. Almost always caused by config files pointing at a stale/old project path after the repo was moved or re-cloned. Use when the user says the interpreter is wrong, can't find the venv, or Pylance/pyright/pyrefly can't resolve imports."
---

# Python Interpreter / venv Quick-Fix

## When to use
The user reports any of:
- "Select Python Interpreter" can't find / won't connect to the `.venv`.
- VS Code picks the wrong interpreter (global Python instead of the project venv).
- Imports show as unresolved; Pylance / Pyright / pyrefly can't resolve `fastapi`, `google.adk`, etc.

## The #1 root cause (check this FIRST)
**Config files contain absolute paths to an OLD project location.** This repo has been moved
between folders (e.g. `c:\Sudo_Hatter_Command\Projects\aviationChat-AGY\` → the current
`c:\Users\dlohn\.gemini\antigravity\scratch\Sudo_Hatter_Command\Projects\AGY_AVIATIONCHAT\`). Hard-coded absolute paths in
the tooling configs die the moment the project folder changes, so VS Code is pointed at a venv
that no longer exists.

> The permanent cure is **portable paths** (`${workspaceFolder}` / relative), so it never breaks
> again on a move. Only `pyrefly.toml` must stay absolute (see the rule note below).

## Diagnose (read-only — confirm before editing)

1. Confirm the canonical venv exists locally and is populated:
   ```bash
   ls backend/.venv/Scripts/python.exe
   ls backend/.venv/Lib/site-packages | grep -iE "fastapi|google_adk|pydantic"
   ```
   Canonical interpreter for this project is **`backend/.venv`** (matches `pyrefly.toml`'s
   `project_includes = ["backend/**/*.py"]` and the `cd backend && pytest` convention).
   There may also be a stray root `.venv` — ignore it; `backend/.venv` is the live one.

2. Find every stale absolute path (proves the diagnosis):
   ```
   Grep pattern: Sudo_Hatter_Command   (or whatever the OLD base folder was)
   ```
   The four files that actually matter for interpreter/type-checking are below. (Many doc/skill/
   workflow/artifact hits will also appear — those are cosmetic and OUT of scope.)

## The fix — 4 git-tracked config files (all at repo root unless noted)

Replace the stale base path. Prefer **portable** forms so it survives the next move:

| File | Field(s) | Set to (portable) |
|---|---|---|
| `.vscode/settings.json` | `python.defaultInterpreterPath` | `${workspaceFolder}/backend/.venv/Scripts/python.exe` |
| `.vscode/settings.json` | `python.analysis.extraPaths` | `["${workspaceFolder}/backend", "${workspaceFolder}/backend/.venv/Lib/site-packages"]` |
| `pyrightconfig.json` (root) | `venvPath` | `"backend"` (relative to config dir; keep `venv: ".venv"`) |
| `backend/pyrightconfig.json` | `venvPath` | `"."` (relative to config dir; keep `venv: ".venv"`) |
| `pyrefly.toml` | `python-interpreter-path`, `search_path` (×2), `site_package_path` | **absolute**, current workspace — see note |

### ⚠️ pyrefly.toml stays ABSOLUTE
Project rule `.claude/rules/pyrefly-paths.md` mandates absolute, **double-backslash** native
Windows paths and warns that forward slashes / non-native paths cause *silent* config failures
(empty search roots). So for `pyrefly.toml`, repoint to the current absolute workspace, e.g.:
```toml
python-interpreter-path = "c:\\Users\\dlohn\\.gemini\\antigravity\\scratch\\AGY_AVIATIONCHAT\\backend\\.venv\\Scripts\\python.exe"
```
This is the one file to re-point if the project moves again. Get the current absolute path with
`pwd` and convert `/` → `\\`.

## Verify (paste actual output)
```bash
backend/.venv/Scripts/python.exe -c "import sys, fastapi, google.adk, pydantic; print(sys.executable); print(fastapi.__version__); print('deps OK')"
```
The printed `sys.executable` must point at the **current** workspace's `backend/.venv`.

## Tell the user to do these (config alone is not enough)
VS Code caches the *selected* interpreter in per-workspace storage **outside** the repo, so a
stale cached pick won't auto-switch even after the config is fixed:

1. `Ctrl+Shift+P` → **"Python: Select Interpreter"** → choose `.\backend\.venv\Scripts\python.exe`
   (or "Enter interpreter path…" if it's not auto-listed).
2. `Ctrl+Shift+P` → **"Developer: Reload Window"** (pyrefly does NOT hot-reload its config).
3. Still unresolved? `Ctrl+Shift+P` → **"Python: Clear Cache and Reload Window"**.

## Commit (provide the command — never run git yourself)
```powershell
git add .vscode/settings.json pyrefly.toml pyrightconfig.json backend/pyrightconfig.json
git commit -m "fix(env): repoint Python interpreter/type-checker config to current workspace path (portable)"
git push
```

## Related / deeper context
- Full diagnosis + post-mortem of the original two-venv consolidation:
  `_claude_artifacts/2026-05-30_python-env-cleanup/python-env-fix-runbook.md`
- This skill's origin session: `_claude_artifacts/2026-06-07_python-interpreter-stale-path/`
- Pyrefly path rule (why pyrefly stays absolute): `.claude/rules/pyrefly-paths.md`
- BMAD "Microsoft Store python3" noise (separate issue — `python3.exe` shim missing in venv):
  `Copy-Item backend\.venv\Scripts\python.exe backend\.venv\Scripts\python3.exe`
