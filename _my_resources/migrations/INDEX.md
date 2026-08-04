# `_my_resources/migrations/` — machine setup & one-off migrations

**Disposable by design.** Everything here is new-machine / rename-day material, not day-to-day
infrastructure. It lives in the personal area (out of the top level) so it can be deleted outright
once a migration is done, instead of sitting at the root going stale.

**Read-only posture does NOT apply here while a migration is running.** `_my_resources/` is normally
protected, but the operator pointing an agent at this folder IS the instruction to use it — read the
guides, run the scripts.

> **Agent setting up ANY machine — laptop, desktop, Mac, or a fresh clone: start at §1 and go in
> order.** The path is the **same on every machine**; §1's table has a column per OS where the
> commands differ. Two rules that catch people out:
>
> - **A faster machine does not get a shorter checklist.** Every step in §1 is *correctness* (right
>   interpreter, right secrets, right venv name), not performance. The only thing that legitimately
>   varies with hardware is the `-n` worker count in step 5, and that doc tells you to measure it.
> - **§2 is macOS-only.** Skip it on Windows. On a Mac read it BEFORE step 3 — the secrets restore
>   script does not work there.
>
> Do not read §3 or §4 — historical records for unrelated tasks, nothing to do with machine setup.

---

## 1 · New machine — the ordered path

| # | Step | File / command | Windows | macOS |
|---|---|---|---|---|
| 1 | Read the whole procedure first (clone → restore → verify) | [`new_machine-migration-guide.md`](new_machine-migration-guide.md) | ✅ | ✅ |
| 2 | Clone both repos (lobby + every project you work in) | that guide, §3 | ✅ | ✅ |
| 3 | Restore every `.env` / `auth_keys/` from the master bundle | [`Restore-EnvMaster.ps1`](Restore-EnvMaster.ps1) | ✅ | ⛔ **see §2** — use the guide's §6 manual restore |
| 4 | The secret bundle step 3 reads | `_secrets/master.env` — **gitignored, hand-carried, never committed** | ✅ | ✅ |
| 5 | Rebuild the AGY Python venv + verify the test infra | [`python_vytest-updates-other-machines.md`](python_vytest-updates-other-machines.md) | ✅ | ✅ (use its macOS column) |
| 6 | Per-machine logins & toolchains — gcloud, gh, firebase, Java 17, Node, GitNexus re-index | that guide, §5 | ✅ | ✅ |
| 7 | Scrum-board stale-stamp git hooks (per machine, per project — AGY today) | [`git-hooks-board-stale-install.md`](git-hooks-board-stale-install.md) | ✅ | needs `pwsh` (installer is `.ps1`) |

```powershell
# step 3, from the LOBBY ROOT (not from this folder) — Windows only
powershell -File _my_resources\migrations\Restore-EnvMaster.ps1
```

**Step 5 is not optional on a fast machine.** It is a *correctness* step, not a performance one — CI
and prod run Python 3.11, and a drifted venv makes local green a lie on that machine only. A faster
box does not get a reduced checklist; it gets its own `-n` value. That doc says so in full.

---

## 2 · ⛔ macOS: two things in this kit are Windows-bound

Both are known, neither is subtle, and hitting them blind wastes an afternoon.

| What | Why it breaks on macOS | Do this instead |
|---|---|---|
| **`Restore-EnvMaster.ps1`** (step 3) | Even under `pwsh` it is path-separator-bound: it joins `'_my_resources\migrations\_secrets\master.env'` and does `$relPath.Replace('/', '\')`, so on macOS it looks for one literal back-slashed filename and would write `backend\.env` as a single file rather than nesting it | Use **§6 "Manual restore"** in `new_machine-migration-guide.md` — it is written for exactly this case. (Or ask for the script to be made separator-agnostic; the change is small but must not regress Windows.) |
| **`rename-fix.ps1`** | Windows-only *by design* — it rewrites `%USERPROFILE%` and `.claude\settings.json` paths | Not applicable on a Mac. Do not run it. |

**Also install on macOS**, beyond what §5 of the guide lists: `python3.11` ·
`brew install --cask temurin@17` (Firestore rules-emulator suite) · `node` · **`pwsh`**
(`brew install --cask powershell`) only if you intend to run any `.ps1` here.

Everything else in the kit — the guides, the Python/vitest companion, the git-hooks doc — is
cross-platform once `pwsh` is present.

---

## 3 · Old machine / ongoing

| Task | File |
|---|---|
| Re-bundle every secret after adding or rotating one | [`Export-EnvMaster.ps1`](Export-EnvMaster.ps1) |
| Rename-day: move projects into `Projects/` + repair absolute paths | [`rename-fix.ps1`](rename-fix.ps1) (dry-run by default; `-Apply` to write) — **Windows only** |

## 4 · One-off migration records (historical — NOT machine setup)

- [`propagate-autopilot-glm-hybrid.md`](propagate-autopilot-glm-hybrid.md) +
  [`autopilot-glm-hybrid.patch`](autopilot-glm-hybrid.patch) — the GLM hybrid-lane autopilot port.
  Kept because the autopilot engine is **project-local** (each project under `Projects/` has its own
  `scripts/autopilot-dev-story.ps1`, and they are not synced), so this is the record for propagating
  the change into the next project. Nothing to do when setting up a machine.

---

## Rules

- **All three `.ps1` files run from the LOBBY ROOT, not from this folder.** Each derives the lobby
  root as two levels up from its own location — moving them again breaks that, so fix the
  `Split-Path` chain if you ever do.
- **`_secrets/` is never committed, emailed, pasted into a chat, or cloud-synced in plaintext.**
  It is covered by the `**/_secrets/` rule in the lobby `.gitignore`; `Export-EnvMaster.ps1` refuses
  to run if that rule ever stops matching.
- Never print secret **values** in agent output — key names only.
- This folder uses `INDEX.md` as its single entry point, per the workspace standard (Tier 3 leaf
  content: `INDEX.md` and/or `README.md`, never `AGENTS.md`). There is deliberately **no** `README.md`
  here — a second entry point is a second thing to keep in sync.

## Related

- Maintaining the home base itself (`/new-project`, `/sync-agents`) → `docs/system-builder.md`
- Parking / resuming work across machines → `/sudo-park`, `/sudo-resume`
