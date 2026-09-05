---
name: env-migration-kit
description: "Machine-migration kit lives in docs/migrations/ (moved there 2026-08-11 from _my_resources/migrations/, SCC-89) — master.env bundle + scripts + new_machine-migration-guide.md (secrets) + python_vytest-updates-other-machines.md (venv rebuild + vitest lock notes, its §5 companion; renamed from python-311-test-infra-other-machines.md)"
metadata: 
  probe: "test -e docs/migrations/scripts"
  node_type: memory
  type: project
  originSessionId: 2878ccd7-de5c-40d1-89a3-f9cb34a15cc0
  modified: 2026-08-02T02:57:11.340Z
---

Built 2026-07-24 for Daniel's new-computer transition. All secrets are gitignored (`**/.env`, `**/auth_keys/`, `_secrets/`), so a fresh clone has zero credentials — they travel ONLY via the hand-carried bundle.

- `auth_keys/_secrets/master.env` — **moved 2026-08-08** (operator relocated the bundle under `docs/migrations/auth_keys/`, alongside per-project key folders like `AGY-AviationChat/`; everything under `**/auth_keys/` is gitignored). All 7 secret files (lobby .env, AGY auth_keys/.env + service-account.json + backend/.env + frontend/.env.local + .env.production, BRKN frontend/.env.local) concatenated with `# >>> FILE:` / `# <<< END FILE:` markers + manifest header. NEVER commit/paste/print values.
- `Export-EnvMaster.ps1` / `Restore-EnvMaster.ps1` (in `docs/migrations/scripts/` since the SCC-26 reorg) — rebuild / split the master (export auto-discovers new projects, refuses if output not gitignored; restore backs up differing files as .pre-restore.bak). **Their default path was WRONG from SCC-26 until SCC-89** (2026-08-11): all three scripts plus `restore-env-master.sh` walked up two levels for the lobby root while sitting three deep, and defaulted to a `_secrets/` folder the operator had already moved. Both bugs are fixed — the default is now `docs/migrations/auth_keys/_secrets/master.env` and the root walk is three. `-MasterPath` still overrides for a USB copy.
- `new_machine-migration-guide.md` — the secrets doc handed to the new-machine agent (renamed 2026-08-01 from env-migration-guide.md; order: clone repos FIRST, then restore; verification checklist; per-machine logins gcloud/gh/firebase/Java).
- `python_vytest-updates-other-machines.md` — the venv/interpreter companion (its §5 points here; renamed 2026-08-01 from python-311-test-infra-other-machines.md): AGY needs Python 3.11 specifically, and pytest will NOT warn on a wrong-interpreter venv — carries the rebuild commands + 4-check verification, plus the vitest suite-lock notes (that side needs zero per-machine work — it travels via git).

Pairs with `/sudo-park`/`/sudo-resume` for branches/worktrees (those handle git state; this kit handles secrets). All GOOGLE_APPLICATION_CREDENTIALS values are deliberately relative paths — keep them that way.
