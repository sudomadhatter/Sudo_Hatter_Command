# SCC-39 — Centralized Master .env Configuration & Migration Kit

**Lane:** `chore/SCC-39-master-env-home-machine` · cut from `main` @ `0904253`  
**Parent:** Grouping Task · **Lane:** LOCAL · **Close:** `/smh-close-task-merge-tree`

---

## 1. Problem & Context

Fresh machine setup and disaster recovery require carrying secrets (`.env` files, Firebase/GCP credentials, and service accounts) across machines securely without leaking them to Git. Previously, `Export-EnvMaster.ps1` was untested and captured stale `.bak` and `.example` files, and no platform-agnostic engine or automated test suite existed to validate bundling, path safety, and restore idempotency.

**Ticket SCC-39 Goal:** Create a centralized master `.env` configuration in `Sudo_Hatter_Command` for the home machine, providing a single source of truth for environment variables and robust migration tooling.

---

## 2. What Was Built

1. **Root `.env.example` Template** — [`.env.example`](file:///c:/Sudo_Hatter_Command/.env.example):
   - Created clean, sanitized documentation template for all system environment variable keys (AI APIs, GitHub PATs, GCP/Firebase, Sentry, Telegram, Routine).

2. **Cross-Platform Engine** — [`docs/migrations/scripts/env_master.py`](file:///c:/Sudo_Hatter_Command/docs/migrations/scripts/env_master.py):
   - Python 3.10+ CLI supporting `--export`, `--restore`, `--verify-only`, and `--dry-run`.
   - Rejects unsafe path traversal (`..` or absolute paths).
   - Enforces `0o600` permissions on POSIX.
   - Automatically skips `.example`, `.bak`, `.venv`, and `node_modules`.
   - Created master vault bundle at `docs/migrations/auth_keys/_secrets/master.env` (gitignored, 12 files bundled).

3. **Updated PowerShell Exporter** — [`docs/migrations/scripts/Export-EnvMaster.ps1`](file:///c:/Sudo_Hatter_Command/docs/migrations/scripts/Export-EnvMaster.ps1):
   - Added regex exclusion to filter out `*.bak` and `*.example` files.

4. **Integration Test Suite** — [`.agents/scripts/tests/test_env_master.py`](file:///c:/Sudo_Hatter_Command/.agents/scripts/tests/test_env_master.py):
   - **26/26 checks passing** covering discovery, export formatting, parse errors, path traversal rejection, restore idempotency, backup creation (`.pre-restore.bak`), and live repository validation.

5. **Updated Migration Runbooks**:
   - [`docs/migrations/INDEX.md`](file:///c:/Sudo_Hatter_Command/docs/migrations/INDEX.md): Steps 3 and 4 updated to reference `env_master.py`.
   - [`docs/migrations/install_guides/machine_setup_card.md`](file:///c:/Sudo_Hatter_Command/docs/migrations/install_guides/machine_setup_card.md): Section 3 updated with restore commands.

---

## 3. Evidence & Verification

| # | Acceptance Requirement | Result |
|---|---|---|
| 1 | Single source of truth master .env bundle created | Generated `docs/migrations/auth_keys/_secrets/master.env` containing 12 secret files. |
| 2 | Master vault is gitignored | `git check-ignore docs/migrations/auth_keys/_secrets/master.env` -> confirmed gitignored. |
| 3 | Automated test suite validating bundle and restore | `test_env_master.py`: **26/26 PASSED**. |
| 4 | Clean template authored in lobby | [`.env.example`](file:///c:/Sudo_Hatter_Command/.env.example) authored and verified. |
| 5 | Runbooks and setup cards updated | `docs/migrations/INDEX.md` and `machine_setup_card.md` aligned. |

### Test Suite Output
```
== test_env_master (SCC-39) ==
[PASS] discovers root .env
[PASS] discovers project backend .env
[PASS] discovers auth_keys service-account.json
[PASS] ignores node_modules .env
[PASS] ignores .env.example files
[PASS] ignores .bak files
[PASS] total discovered count matches expected
[PASS] export_master returns 0
[PASS] master.env file created
[PASS] master.env contains manifest header
[PASS] master.env contains root .env marker
[PASS] master.env contains secret content
[PASS] master.env contains end marker
[PASS] parse_master_bundle succeeds with 0 errors
[PASS] parsed 3 entries
[PASS] rejects relative path traversal (..)
[PASS] rejects absolute paths
[PASS] first restore returns 0
[PASS] restored root .env
[PASS] restored content matches
[PASS] second restore returns 0 (idempotent)
[PASS] restore after modification returns 0
[PASS] created .pre-restore.bak
[PASS] backup contains modified value
[PASS] restored file overwritten with vault value
[PASS] live master.env passes verification
-- 26/26 passed --
```

---

## 4. Your Action Required

- [x] Template `.env.example` created.
- [ ] Review secrets copied into root `.env` or subproject `.env` files if any new keys are needed.
- [ ] Approve merge and close-out of **SCC-39** via `/smh-close-task-merge-tree`.
