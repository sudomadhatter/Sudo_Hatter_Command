---
name: agy-database-import-is-an-init-step
description: "backend/database.py runs db = get_db() at module scope, so importing it needs an initialized Firebase app AND live ADC creds — any backend/scripts module must initialize_app() ABOVE that import, and the routers conftest hides the breakage"
metadata: 
  node_type: memory
  type: project
  originSessionId: 2007a161-79d4-4c7d-9f5b-330e3df9b16b
  modified: 2026-07-30T16:35:23.973Z
---

**2026-07-30 (story 21.7 ③).** `backend/database.py` ends with `db = get_db()` at **module scope**
(`:56`). `get_db()` raises `RuntimeError` unless a Firebase app already exists (`:29-34`), then resolves
**live ADC credentials** to build the client.

So `from backend.database import get_db` is **not an import — it is an initialization step with a hard
precondition.** Any module in `backend/scripts/` that imports it must call
`firebase_admin.initialize_app()` **above that import line**. That is what the `# noqa: E402` markers on
those imports are quietly protecting, in `seed_demo_profile.py` and `backfill_school_members.py` alike.

**The trap: the contract tests cannot see you break this.** Files under `backend/tests/routers/` run
under a conftest that neutralises the live GCP client tree `backend.main` builds at import — which is
*why* story contract files live there rather than in `backend/tests/`. The side effect is that **no test
in those files can observe its subject failing to import**, and none can be written that runs in CI,
because a real import needs GCP credentials the runner does not have.

This is not hypothetical. ③ deleted `seed_demo_profile.py`'s module-scope `initialize_app()` as
dual-role-hygiene cleanup (the module is imported by 21.8 and by its own tests, so import-time global
state looked wrong). `python -m backend.scripts.seed_demo_profile` died with `RuntimeError` before
argparse ran — and **all 32 contract tests stayed green.** It was caught by smoke-running `--help`,
which is the operator's own first step, not by anything in the suite.

**How to apply:**
- Before "cleaning up" a module-scope side effect in `backend/scripts/`, check whether it precedes a
  `backend.database` import. If it does, it is load-bearing. Leave it and write down why.
- **Smoke-run any CLI you touch**: `backend\.venv\Scripts\python.exe -m backend.scripts.<mod> --help`.
  `--help` exits before any Firestore call, so it is safe against production and still exercises the
  whole import chain. A green suite over a dead entrypoint is the failure class
  `tests-must-gate-for-real` exists to catch.
- Where you need the invariant *gated*, assert it on **source order** — `initialize_app(` must appear
  above `from backend.database import` — because that is the only form that runs in CI. `IMPORT-001` in
  `backend/tests/routers/test_story_21_7_demo_profile_seed.py` is the worked example, and it was
  mutation-checked.
- `firebase_admin.get_app()` in a `try`/`except ValueError` is the public idiom
  (`firebase_user_manager.py:31-34`). Probing `firebase_admin._apps` reaches into a private attribute.
- The repo-root `sys.path.insert` these scripts copy from each other **is** genuinely redundant under
  `python -m` (the root must already be importable for `-m` to resolve the module at all) — that half of
  the cleanup is safe. It is only the Firebase init that must stay.

Related: [[agy-typecheck-is-enforced-nowhere]], [[agy-ruff-changed-files-is-a-hard-gate]],
[[stubbed-children-make-green-vacuous]] (same family — a harness that mocks the thing it is meant to
prove), [[e2e-gate-fiction-test-guardrails]], [[agy-canonical-test-venv]].
