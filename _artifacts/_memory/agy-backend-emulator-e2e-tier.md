---
name: agy-backend-emulator-e2e-tier
description: AGY backend emulator E2E tier (debug-1.8) — pytest -m emulator vs real Firestore emulator; sibling conftests install session-wide global mocks so naive suites test MOCKS in the gate job; structural defences + pytest fixture-ordering trap + keyless-isolated-run edge.
metadata: 
  node_type: memory
  type: project
  originSessionId: a101c9a4-732c-403d-896e-509a9c1f24b9
  modified: 2026-07-26T03:19:00.681Z
---

AGY has a **backend** emulator E2E tier (story debug-1.8, done 2026-07-21) alongside [[agy-learner-e2e-harness]]'s frontend journeys: `backend/tests/e2e_emulator/` drives the profile write path (`set_field`, `redeem_seat`, `/chat/hr/finalize`) against a REAL Firestore emulator client. Run: `node backend/tests/e2e_emulator/run-emulator-e2e.mjs` locally; CI = the `backend-e2e` hard-gate job in pr-check.yml (`pytest backend/tests -m emulator` inside `emulators:exec`; `EXPECT_FIRESTORE_EMULATOR=1` makes an absent emulator FAIL, never skip).

**Why:** debug-1.5 shipped a P0 write path whose "E2E" was a hand-written FakeFirestore — its deep-merge was our belief about Firestore asserted against itself. The real client confirmed D1's recursive-merge assumption, the sentinels, and the D-4 flip race fix (zero production bugs found — the fake was faithful, now proven not hoped).

**How to apply (any new real-client suite in this repo):**
1. Sibling conftests (`routers/`, `agents/`, `services/`) install **session-wide global mocks at import time** (`google.cloud.firestore.Client` → MagicMock; `sys.modules["backend.database"]` → fake module) and never revert. A full-tree run (what CI does) loads them ALL — a naive suite goes green against mocks. Defend structurally: import the client from its **defining module** (`google.cloud.firestore_v1.client`), patch `get_db` on the **consumer** modules (they bound the name at import), have the fixture **self-assert reality** before yielding. Verify with the FULL-TREE `-m emulator` run, never only the isolated dir.
2. **pytest ordering trap (probe-proven):** session-scoped fixtures are set up BEFORE a function-scoped autouse gate can `pytest.skip()` — a session fixture that touches the emulator ERRORS on keyless/emulator-less machines instead of skipping. Skip-gated suites need such fixtures function-scoped or self-guarding.
3. Set `_db`/patches to the client INSTANCE, never reset-to-None — real `get_db()` rebuilds from `GCP_PROJECT_ID` (default `aviationchat`) while tests read `demo-agy` = split-brain.
4. Isolated-dir runs on keyless machines fail at collection (`database.py` import-time singleton → DefaultCredentialsError) — full-tree is immune (agents/ fake loads first); README documents it. Don't "fix" by adding another global mock.
5. **Invoke the tier by DIRECTORY + `-k`, never by a single file path** (confirmed 2026-07-25, story 21.3 ①). `pytest backend/tests/e2e_emulator/test_<one>.py` ERRORS every test at setup with *"Firebase Admin not initialized. Call firebase_admin.initialize_app() before get_db()"* — collecting one file changes import order, and nothing initializes firebase before `backend/database.py`'s module-level `db = get_db()` runs. The official runner passes the DIRECTORY and appends your args, so `run-emulator-e2e.mjs -k <slug>` is the shape that works. Same import-time-singleton root cause as (4), different trigger and a different error string. **Diagnose with a control run** of an already-landed emulator test (e.g. `test_member_access_emulator_e2e.py`) before blaming your new file — it fails identically single-file and passes directory-form.

Bound every test: `pytestmark = pytest.mark.timeout(120)` (a wedged emulator = ~6h CI hang otherwise). Policy copy: testing-standards.md §5.
