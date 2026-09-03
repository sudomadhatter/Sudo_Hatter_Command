# Implementation Plan — bring the WSL box to reference green, then write the Linux column

**Date:** 2026-09-03 · **Workspace:** `_main` · **Project touched:** AGY_AVIATIONCHAT (gitignored files only until step 7)
**Status:** awaiting `approved`

## What is wrong, in one paragraph

This WSL box fails 40 backend tests under the documented command (`pytest backend/tests -n auto
--dist loadfile -q`), every one a Firestore `403 PermissionDenied`. The reference machines (Windows,
Mac) run the same command and get 0 failed. The difference is not code: it is that
`Projects/AGY_AVIATIONCHAT/auth_keys/` does not exist here. `backend/main.py:22` loads
`auth_keys/.env` at import, and that file carries `GOOGLE_APPLICATION_CREDENTIALS` pointing at
`auth_keys/service-account.json`; without it `google.auth.default()` raises, `conftest.py` swaps in
`AnonymousCredentials`, and every real Firestore call is refused. The emulator run earlier today was a
diagnostic detour — it is not how the house runs this suite.

Every missing piece already exists on the Windows side of this same machine, readable from WSL at
`/mnt/c/Sudo_Hatter_Command` and `/mnt/c/Users/dlohn/AppData/Roaming/gcloud`. No USB stick, no
re-login for the credentials that are files.

## Inventory (measured 2026-09-03)

| Piece | Windows (`/mnt/c/...`) | WSL (this box) | Documented step |
|---|---|---|---|
| `docs/migrations/auth_keys/_secrets/master.env` | present, 2026-08-14, 7 FILE blocks | **absent** | INDEX step 4 |
| lobby `.env` | present | **absent** | step 3 |
| AGY `auth_keys/.env`, `service-account.json` | present (SA re-issued **2026-09-03**, newer than bundle) | **absent** | step 3 |
| AGY `auth_keys/librarian-service-account.json` | present | **absent** — and **not in the bundle** | step 3 (gap) |
| AGY `backend/.env` | present | present, byte-identical | step 3 |
| AGY `frontend/.env.local`, `.env.production` | present | **absent** | step 3 |
| gcloud ADC (`application_default_credentials.json`, `authorized_user`, quota project `aviationchat`) | present | **absent**; `gcloud` CLI absent | step 6 |
| Keyway | installed + logged in | **absent** | step 6c |
| `gh`, `acli`, Node 22, Java 17, backend `.venv` (3.11) | — | ✅ present and authenticated | steps 5, 6, 6b |
| AGY `_my_resources/` | 278 files | 251 tracked files; the 27 missing are untracked audio/video media | not a test input |

## Steps

1. **Hand-carry the bundle** — `cp` the Windows `master.env` to the same gitignored path in this lobby
   (`**/_secrets/` is ignored at `.gitignore:57`). Confirm `git status` stays clean.
2. **Restore** — `bash docs/migrations/scripts/restore-env-master.sh --dry-run`, read the list, then
   run it live. Expected writes: lobby `.env`, AGY `auth_keys/.env`, `auth_keys/service-account.json`,
   `frontend/.env.local`, `frontend/.env.production`, BRKN `frontend/.env.local`; `backend/.env`
   reports `unchanged`. `chmod 600` everything it wrote.
3. **Overlay the two files the bundle is behind on** — copy the live Windows
   `auth_keys/service-account.json` (issued today, differs from the bundle's copy) and
   `auth_keys/librarian-service-account.json` (never in the bundle) into WSL `auth_keys/`, mode 600.
4. **ADC** — `install -m 600` the Windows ADC file to `~/.config/gcloud/application_default_credentials.json`.
   This is the exact file `gcloud auth application-default login` would have produced. The `gcloud`
   CLI itself needs `sudo apt` and is Mr. Hatter's line to run (not needed for the suite).
5. **Prove it** — run the documented command from the AGY root with `backend/.venv/bin/python`.
   Done means `0 failed`. Paste the tail.
6. **Keyway** (step 6c) — `npm install -g @keywaysh/cli` (asking first, per dependency law), then
   `keyway login` is Mr. Hatter's browser step; finished state is `keyway doctor` → `5 passed, 1 warning`.
7. **Write it down** — mint one SCC Task; in a `chore/SCC-<n>-linux-column` worktree add a **Linux/WSL**
   column to the machine table in [`docs/migrations/INDEX.md`](../../../docs/migrations/INDEX.md) and a
   short WSL block in the new-machine guide: `python3`, use the `.sh` scripts, the bundle and ADC come
   across `/mnt/c` when WSL shares a Windows box, Java is `openjdk-17-jdk-headless` from apt,
   `firebase-tools` is the repo-local 13.x under `firebase/tests/node_modules` (never the global 15.x,
   which demands Java 21). Also close the bundle gap: add `librarian-service-account.json` to what
   `env_master.py --export` discovers, and re-export so the Mac inherits a complete bundle.

## Not doing

- Not installing `gcloud` or running `sudo` — those are the operator's lines.
- Not syncing the 27 untracked media files (4.5 GB of lesson video; no test reads them).
- Not committing anything before step 7; steps 1–6 touch only gitignored / home-directory files.

## Risk

Step 3 overwrites nothing (the files do not exist here). Step 2's only surprise candidate is BRKN's
`frontend/.env.local` — the project is cloned here, so it lands in place. The credentials copied are
Mr. Hatter's own, moving between two OSes on one physical machine; none enter git.
