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

> ### ✅ First live execution: Desktop, 2026-08-04 — steps 1–7 (NOT the whole kit)
> Until then this kit had been **written but never run** — every step was transcribed from a working
> session rather than replayed. Running it surfaced **six defects that each stop the run cold**, now
> fixed in place. If you are on a machine that has not been set up since, expect the corrected text:
>
> | Where | Defect | Symptom if you hit the old text |
> |---|---|---|
> | python companion, step 2 | `PYTHONUTF8=1` missing | pip installs **zero** packages; `pip check` still says "No broken requirements found" |
> | python companion, Phase 1 | `Rename-Item` given a path as `-NewName` | `represents a path or device name` — the venv swap never happens |
> | python companion, Phase 4 | "delete parked venvs once green" | circular: a venv parked under `backend/` is what **prevents** green (2 failed / 3022 passed) |
> | python companion, CHECK 3 | named a file that cannot pass standalone | 9 failed / 3 errors on a perfectly good venv — sends you hunting a phantom |
> | this guide, §4 | restore's own `.pre-restore.bak` copies escape the ignore rules | a live Firebase API key left sitting untracked |
> | this guide, §3 | assumed every `Projects/<name>` is a clone | 2 of 8 had no `.git`; git commands there silently hit the **lobby** |
>
> Two of those (`PYTHONUTF8`, `Rename-Item`) are hard stops on **any** Windows machine. Note also that
> the laptop's ☑ in the python companion's machine table predates the 2026-08-03 change that causes the
> first one — so that ☑ certifies a procedure it never ran. **Treat an unticked box as untested, and a
> ticked one as tested only for the text as it stood that day.**
>
> **Exactly what was and was NOT executed** — do not read the ✅ above as blanket coverage:
>
> | Asset | Status |
> |---|---|
> | `Restore-EnvMaster.ps1` | ✅ **run for real** — 7 files restored, 4 backed up, §4 verified |
> | `python_vytest-…md` (5-min fix + CHECK 1–4) | ✅ **run for real** — venv rebuilt, gate `3024 passed / 35 skipped / 0 failed`, `-n` swept |
> | `git-hooks-board-stale-install.md` | ✅ **run for real** — installed, stamped real drift, reverted clean |
> | `restore-env-master.sh` | ⚠️ **`--dry-run` only, and under Git Bash on WINDOWS — never on macOS.** It parsed all 7 markers and classified create-vs-backup correctly, so its parsing and root-resolution are sound. Its **writing** path (`chmod 600`, backups, CRLF strip on real output) is still unproven. First Mac to run it should use `--dry-run` first and report |
> | `Export-EnvMaster.ps1` | ⛔ **NOT run.** Deliberately — it *rewrites* `_secrets/master.env`, and re-generating the operator's hand-carried bundle to test a script is not a safe experiment mid-setup. Still unverified |
> | `rename-fix.ps1` | ⛔ **NOT run** (no rename happened). Its stale project list was fixed by inspection against the real tree, not by executing it. `-Apply` remains untested |
> | `.agents/scripts/link-memory.ps1` | ⚠️ **dry run only** — plan read correctly (would seed 25 files, junction 4 workspaces). `-Apply` deliberately NOT run: this machine's memories are stale, so seeding from here would push stale memory to every other machine. The machine holding the NEWEST memories must link first |
> | `link-memory.sh` | ⛔ **NOT run** — macOS only |
>
> ⚠️ **Two projects had no `.git` at all** (`BRKN_Tattoos`, `NEXgen-VR-Director`) — see §3 step 2 of the
> guide. Git commands inside an un-cloned project silently operate on the **lobby** instead of failing,
> so this does not announce itself.

---

## 1 · New machine — the ordered path

| # | Step | File / command | Windows | macOS |
|---|---|---|---|---|
| 1 | Read the whole procedure first (clone → restore → verify) | [`new_machine-migration-guide.md`](new_machine-migration-guide.md) | ✅ | ✅ |
| 2 | Clone both repos (lobby + every project you work in) | that guide, §3 | ✅ | ✅ |
| 3 | Restore every `.env` / `auth_keys/` from the master bundle | Windows → [`Restore-EnvMaster.ps1`](Restore-EnvMaster.ps1) · macOS/Linux → [`restore-env-master.sh`](restore-env-master.sh) | ✅ | ✅ **use the `.sh`** |
| 4 | The secret bundle step 3 reads | `_secrets/master.env` — **gitignored, hand-carried, never committed** | ✅ | ✅ |
| 5 | Rebuild the AGY Python venv + verify the test infra | [`python_vytest-updates-other-machines.md`](python_vytest-updates-other-machines.md) | ✅ | ✅ (use its macOS column) |
| 6 | Per-machine logins & toolchains — gcloud, gh, firebase, Java 17, Node, GitNexus re-index | that guide, §5 | ✅ | ✅ |
| 7 | Scrum-board stale-stamp git hooks (per machine, per project — AGY today) | [`git-hooks-board-stale-install.md`](git-hooks-board-stale-install.md) | ✅ | needs `pwsh` (installer is `.ps1`) |
| 8 | **Link the Claude auto-memory store** so memory travels via git instead of dying on this box | `.agents/scripts/link-memory.ps1` · macOS → `link-memory.sh` | ✅ | ✅ **use the `.sh`** |

```powershell
# step 8 — Windows, from the LOBBY ROOT. Dry run first; -Apply only once the plan reads right.
powershell -File .agents\scripts\link-memory.ps1 -All
powershell -File .agents\scripts\link-memory.ps1 -All -Apply
```
```bash
# step 8 — macOS. Finds the lobby root itself, so run it from anywhere.
bash .agents/scripts/link-memory.sh --all            # look first
bash .agents/scripts/link-memory.sh --all --apply    # then apply
```

> **⚠️ Step 8 has an ORDER dependency across machines — get this wrong and you strand memory.**
> The **first machine to link SEEDS** the shared store; every machine after it finds the store populated
> and moves its own local memory **aside to a backup** instead of merging. So **link the machine holding
> the NEWEST memories first**, commit + push, and only then link the others. The scripts never delete or
> merge — they back up and report — but a stale machine seeding first means everyone pulls stale memory.
>
> **On macOS, run the dry run and read it before `--apply`.** The slug rule was derived from Windows
> paths; the script verifies the directory it computed actually exists and tells you to stop if nothing
> matches. If it prints that warning, report it rather than forcing it.

```powershell
# step 3 — Windows, from the LOBBY ROOT (not from this folder)
powershell -File _my_resources\migrations\Restore-EnvMaster.ps1
```
```bash
# step 3 — macOS / Linux. Finds the lobby root itself, so run it from anywhere.
bash _my_resources/migrations/restore-env-master.sh --dry-run   # look first
bash _my_resources/migrations/restore-env-master.sh             # then apply
```

**Step 5 is not optional on a fast machine.** It is a *correctness* step, not a performance one — CI
and prod run Python 3.11, and a drifted venv makes local green a lie on that machine only. A faster
box does not get a reduced checklist; it gets its own `-n` value. That doc says so in full.

---

## 2 · macOS notes

| What | Situation |
|---|---|
| **Secrets restore** | ✅ **Solved — use [`restore-env-master.sh`](restore-env-master.sh).** `Restore-EnvMaster.ps1` cannot do this on macOS even under `pwsh`: it joins `'_my_resources\migrations\_secrets\master.env'` and does `$relPath.Replace('/', '\')`, so it would hunt for one literal back-slashed filename and write `backend\.env` as a single file instead of nesting it. Rather than change a working Windows script, the `.sh` is its **twin** — same markers, same backups, same refusals, **verified byte-identical output** on the same master. It also strips the CRLF that a Windows-exported `master.env` carries (a naive shell read would append `\r` to every secret), adds `--dry-run`, and `chmod 600`s what it writes. |
| **`rename-fix.ps1`** | ⛔ Windows-only *by design* — it rewrites `%USERPROFILE%` and `.claude\settings.json` paths. Not applicable on a Mac; do not run it. |
| **`link-memory.sh`** | ✅ **Use this, not the `.ps1`.** Twin of `link-memory.ps1`: symlink instead of junction, `~/.claude/projects/` instead of `%USERPROFILE%\.claude\projects\`, everything else identical. The macOS slug shape is **inferred from Windows paths** — a POSIX path's leading `/` should render as a leading `-`. The script verifies the computed directory exists and **refuses rather than guessing** if nothing matches, so run the dry run and read it. One command settles it for good: `ls ~/.claude/projects/`. |
| **`.ps1` files generally** | Need `pwsh` (`brew install --cask powershell`). Only `Export-EnvMaster.ps1` and the git-hooks installer are likely to matter. |

> **Keep the twin pairs in sync.** If either half changes, change both — they are twins by contract, and
> the whole point is that a Mac and a Windows box end up with identical files. **Two pairs live under this
> rule now:** `Restore-EnvMaster.ps1` / `restore-env-master.sh`, and
> `.agents/scripts/link-memory.ps1` / `link-memory.sh`.

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
| **Rename-day, STEP 2 — re-point the memory junction** | `.agents/scripts/link-memory.ps1 -All -Apply` (macOS: `link-memory.sh --all --apply`) |

> **⚠️ Renaming without step 2 silently strands memory — this has already happened twice.**
> Claude Code's memory slug is derived from the workspace's absolute path (`:` `\` `/` `_` → `-`), so a
> rename changes the slug and orphans everything under the old one. `rename-fix.ps1` repairs
> `.claude\settings.json` but knows nothing about `projects/<slug>/memory/`. Two dead stores on this
> machine prove the gap: **13 files** under `c--AGY-Projects-aviationChat-AGY` and **2** under
> `c--Sudo-Hatter-Command-Projects-aviationChat-AGY`, both from past renames.
>
> Once the store is junctioned into the repo, a rename costs **nothing but re-running the linker** — the
> data was never in the slug directory to begin with. That is the entire point of the junction.

## 4 · One-off migration records (historical — NOT machine setup)

- [`propagate-autopilot-glm-hybrid.md`](propagate-autopilot-glm-hybrid.md) +
  [`autopilot-glm-hybrid.patch`](autopilot-glm-hybrid.patch) — the GLM hybrid-lane autopilot port.
  Kept because the autopilot engine is **project-local** (each project under `Projects/` has its own
  `scripts/autopilot-dev-story.ps1`, and they are not synced), so this is the record for propagating
  the change into the next project. Nothing to do when setting up a machine.

---

## Rules

- **The `.ps1` files run from the LOBBY ROOT, not from this folder.** Each derives the lobby root as
  two levels up from its own location — moving them again breaks that, so fix the `Split-Path` chain
  if you ever do. (`restore-env-master.sh` resolves its own location, so it runs from anywhere — but
  it makes the same two-levels-up assumption, so it moves with them.)
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
