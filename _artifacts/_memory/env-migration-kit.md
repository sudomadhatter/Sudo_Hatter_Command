---
name: env-migration-kit
description: "Machine-migration kit lives in _my_resources/migrations/ (moved 2026-08-01) — master.env bundle + scripts + new_machine-migration-guide.md (secrets) + python_vytest-updates-other-machines.md (venv rebuild + vitest lock notes, its §5 companion; renamed from python-311-test-infra-other-machines.md)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 2878ccd7-de5c-40d1-89a3-f9cb34a15cc0
  modified: 2026-08-02T02:57:11.340Z
---

Built 2026-07-24 for Daniel's new-computer transition. All secrets are gitignored (`**/.env`, `**/auth_keys/`, `_secrets/`), so a fresh clone has zero credentials — they travel ONLY via the hand-carried bundle.

- `auth_keys/_secrets/master.env` — **moved 2026-08-08** (operator relocated the bundle under `_my_resources/migrations/auth_keys/`, alongside per-project key folders like `AGY-AviationChat/`; everything under `**/auth_keys/` is gitignored). All 7 secret files (lobby .env, AGY auth_keys/.env + service-account.json + backend/.env + frontend/.env.local + .env.production, BRKN frontend/.env.local) concatenated with `# >>> FILE:` / `# <<< END FILE:` markers + manifest header. NEVER commit/paste/print values.
- `Export-EnvMaster.ps1` / `Restore-EnvMaster.ps1` (in `_my_resources/migrations/scripts/` since the SCC-26 reorg) — rebuild / split the master (export auto-discovers new projects, refuses if output not gitignored; restore backs up differing files as .pre-restore.bak). **⚠ Both still hardcode the pre-move `_my_resources/migrations/_secrets/master.env` path** — on a restore, pass `-MasterPath` explicitly or have the operator repoint the scripts (their layout is operator-owned).
- `new_machine-migration-guide.md` — the secrets doc handed to the new-machine agent (renamed 2026-08-01 from env-migration-guide.md; order: clone repos FIRST, then restore; verification checklist; per-machine logins gcloud/gh/firebase/Java).
- `python_vytest-updates-other-machines.md` — the venv/interpreter companion (its §5 points here; renamed 2026-08-01 from python-311-test-infra-other-machines.md): AGY needs Python 3.11 specifically, and pytest will NOT warn on a wrong-interpreter venv — carries the rebuild commands + 4-check verification, plus the vitest suite-lock notes (that side needs zero per-machine work — it travels via git).

Pairs with [[sudo-park]]/[[sudo-resume]] for branches/worktrees (those handle git state; this kit handles secrets). All GOOGLE_APPLICATION_CREDENTIALS values are deliberately relative paths — keep them that way.
