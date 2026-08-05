---
name: worktrees-do-not-inherit-gitignored-assets
description: "A fresh git worktree gets only TRACKED files — credentials, .env and node_modules are gitignored, so every test lane fails there until they are copied/junctioned in; and opening the tree late lets a parallel session's sweep commit capture your work."
metadata: 
  node_type: memory
  type: project
  originSessionId: d77c4200-27cd-4119-8549-a3444604ba67
  modified: 2026-07-27T13:22:37.487Z
---

A new `git worktree add` tree contains **only tracked files**. Everything gitignored is absent, and in AGY that is exactly what the test lanes need. Confirmed 2026-07-25 (story 21.3 ①) — three gaps, each with its own confusing failure:

- **`auth_keys/`** and **`backend/.env`** missing → every emulator test ERRORs at setup with *"Firebase Admin not initialized"*. Copy both in. Re-verify with `git check-ignore -v` **inside the worktree** (`.gitignore:31 auth_keys/`, `.gitignore:25 .env`) — they stay ignored there, so copying real production credentials in cannot leak them into a commit.
- **`frontend/node_modules`** missing → vitest cannot start. A directory junction to the main checkout works **for vitest and for `firebase/tests`** : `New-Item -ItemType Junction -Path <wt>/frontend/node_modules -Target <main>/frontend/node_modules`. (`cmd //c mklink /J` from the Bash tool mis-parses; use PowerShell.)
  ⛔ **But the junction BREAKS the E2E gate** (2026-07-27). Next/Turbopack refuses it outright — *"Symlink node_modules is invalid, it points out of the filesystem root"* — so `next dev` never boots, Playwright reports *"Process from config.webServer was not able to start"*, and the gate exits **non-zero having run ZERO journeys**. That reads as a code failure and is not one. If the lane runs Playwright/Next, do a real **`npm ci` in the worktree** (~2 min, ~1000 packages) instead of junctioning. Related trap: a `next dev` running in the SHARED checkout holds `frontend/.next/dev/lock` and blocks any E2E run started there (*"Unable to acquire lock … is another instance of next dev running?"*) — run the gate from a worktree rather than killing the operator's dev server.
- **`backend/.venv`** — don't recreate it; invoke the main checkout's interpreter in place (`<main>/backend/.venv/Scripts/python.exe`) with cwd set to the worktree. Same for `firebase/tests/node_modules/firebase-tools`: run the main checkout's `firebase.js` with `--config <worktree>/firebase.json`.

⛔ **Tearing the worktree down is where those junctions turn destructive** (2026-07-26, 21.3 close-out).
`Remove-Item -Recurse -Force <worktree>` **follows a junction and deletes the TARGET** — i.e. the main
checkout's real `node_modules`, which every other live worktree also points at. Always enumerate reparse
points first (`Get-ChildItem -Recurse -Force -Directory | Where-Object { $_.LinkType }`), remove each with
`cmd /c rmdir "<link>"` (unlinks only, never the target), prove none remain, and only then delete the
directory — then verify the targets still exist and are non-empty. This is now baked into
`/sudo-close-workingtree` Step 3, but the trap applies to any hand-rolled cleanup.

⚠️ **A fresh worktree's FIRST run of any suite is not evidence — re-run it warm before believing a failure OR a pass.** Cold caches (no Vite cache, no `.next` build, OS file cache cold over ~4,700 files) produced **two** fabricated results in one session on 2026-07-27:

| Suite | First run (cold) | Re-run (warm) |
|--|--|--|
| `vitest run src/components` | **1526s**, 7 phantom "errors", 8 files silently never ran (38 of 46 discovered) | **75s**, 0 errors, 45 files, 313 passed |
| `/sudo-e2e` full gate | **27/28** — a P0 hot-mic assertion on a **5-second poll** failed at 12.5s | **28/28**, same assertion at 5.3s |

Both were 100% artefact — the branch was byte-identical. The E2E one is the dangerous shape: it failed a *privacy* assertion, so it reads as a genuine, serious regression. What distinguishes artefact from real defect is cheap — re-run the same spec **in isolation** (passes → not a missing dependency) and re-run the full suite **warm** (passes → cold artefact). Timing is the tell: the cold run was ~35% slower per journey while running *fewer* journeys. Do not reach for "flaky test" or "machine-bound" as the explanation without that second run — see [[sudo-admin-jsdom-oom-machine-bound]], where an "environmental OOM" turned out to be a real mock bug.

**Why it matters beyond convenience:** the lanes fail in ways that look like *your* code is broken. Before blaming a new test file, run an already-landed test as a control — if it fails identically, it is the environment. See [[agy-backend-emulator-e2e-tier]] for the single-file-vs-directory trap that looks the same.

**Open the tree BEFORE the first project-file edit**, not after. [[git-branch-model-standard]]'s worktree-per-story rule exists because parallel sessions share one checkout: on 2026-07-25 an unrelated session's `git add -A` sweep commit ("reorganize project structure") captured a half-finished story file and a `sprint-status.yaml` edit onto `main_debug` while a story was still being written in the shared tree. Recovery is `git diff > patch` → `git worktree add` → `git apply` in the tree → `git checkout --` the shared copy; the branch then carries the authoritative version and supersedes the swept one on merge. Don't hand-patch `main_debug` to "fix" the artefact.
