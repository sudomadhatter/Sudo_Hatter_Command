# workflow-events — INDEX (the flight recorder)

> **Not sessions — EVENTS.** Every other `_artifacts/` bucket holds one folder per work session.
> This one holds one JSON file per *ceremony event*, written by
> [`flight_recorder.py`](../../../.agents/scripts/flight_recorder.py) as
> `<YYYY-MM>/<JIRA-KEY>_<sha7>.json`, and read by
> [`main_write_gate.py`](../../../.agents/scripts/main_write_gate.py) — the flight event plus the
> preflight receipt are how the system tells a close-out ceremony that was **run** from one that was
> **narrated**. The month folders below are the buckets; they are not sessions and hold no
> `implementation_plan.md` or `walkthrough.md`.

| Bucket | What it holds | Events |
| --- | --- | --- |
| `2026-09/` | September ceremonies. Opened by SCC-365's close-out on 2026-09-01. | 1 |
| `2026-08/` | August ceremonies — the month the flight recorder went live, alongside the armed `main` write gate (SCC-118) and the ledger-rides-the-PR change (SCC-358). | 40 |

**Why this file exists (SCC-367).** `check_maps.py --depth3-only --strict` requires an `INDEX.md` in
any `_artifacts/` bucket holding two or more date-prefixed folders. This bucket held one until
`2026-09/` opened on 2026-09-01, at which point the requirement fired and nothing had created the
INDEX — the drift was reported at every session start and blocked the next close-out gate to run,
which was SCC-367's. Added there rather than deferred, since a missing index is not something a
later lane inherits more cheaply.

⛔ **Do not hand-add rows for individual events.** The month buckets are the unit here; the events
inside them are machine-written and machine-read, and one row per event would be a 41-row table
nobody maintains. A new month gets a new row.
