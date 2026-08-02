# `_my_resources/migrations/` — machine setup & one-off migrations

**Disposable by design.** Everything here is new-machine / rename-day material, not day-to-day
infrastructure. It lives in the personal area (out of the top level) so it can be deleted outright
once a migration is done, instead of sitting at the root going stale.

**Read-only posture does NOT apply here while a migration is running.** `_my_resources/` is normally
protected, but the operator pointing an agent at this folder IS the instruction to use it — read the
guide, run the scripts.

## New machine — start here
| Step | File |
|---|---|
| 1. The whole procedure (clone → restore → verify) | `new_machine-migration-guide.md` (renamed 2026-08-01 from `env-migration-guide.md`) |
| 2. Rebuild every `.env` / `auth_keys/` file from the master | `Restore-EnvMaster.ps1` |
| 3. The hand-carried secret bundle it reads | `_secrets/master.env` — **gitignored, never committed** |
| 4. AGY test-infra companion (its §5 points here) — Python 3.11 venv rebuild + 4-check verification; the vitest suite lock needs no per-machine work | `python_vytest-updates-other-machines.md` |

```powershell
# from the LOBBY ROOT (not from this folder)
powershell -File _my_resources\migrations\Restore-EnvMaster.ps1
```

## Old machine / ongoing
| Task | File |
|---|---|
| Re-bundle every secret after adding or rotating one | `Export-EnvMaster.ps1` |
| Rename-day: move projects into `Projects/` + repair absolute paths | `rename-fix.ps1` (dry-run by default; `-Apply` to write) |

## One-off migration records (historical)
- `autopilot-glm-hybrid.patch` + `propagate-autopilot-glm-hybrid.md` — the GLM hybrid-lane autopilot
  port, kept for propagating to the other autopilot engines.
- `research_docs/` — background notes for the above.

## Rules
- **All three `.ps1` files run from the LOBBY ROOT, not from this folder.** Each derives the lobby
  root as two levels up from its own location — moving them again breaks that, so fix the
  `Split-Path` chain if you ever do.
- **`_secrets/` is never committed, emailed, pasted into a chat, or cloud-synced in plaintext.**
  It is covered by the `**/_secrets/` rule in the lobby `.gitignore`; `Export-EnvMaster.ps1` refuses
  to run if that rule ever stops matching.
- Never print secret **values** in agent output — key names only.

## Related
- Maintaining the home base itself (`/new-project`, `/sync-agents`) → `docs/system-builder.md`
- Parking / resuming work across machines → `/sudo-park`, `/sudo-resume`
