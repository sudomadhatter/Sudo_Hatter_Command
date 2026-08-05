# Env Migration Guide — setting up secrets on a new machine

**Audience:** the AI agent (or human) setting up a fresh computer for the
Sudo_Hatter_Command lobby and its sub-projects.
**You need exactly two things:** this document, and the operator's `master.env`
file (hand-carried — it is never in git).

**Where this kit lives:** `_my_resources/migrations/` — this guide, both
`*-EnvMaster.ps1` scripts, `rename-fix.ps1`, the `_secrets/` vault, and the
companion guide `python_vytest-updates-other-machines.md` (venv rebuild — §5). It sits
in the personal area on purpose: it is new-machine-only, not day-to-day
infrastructure, so it stays out of the top level and can be deleted outright
once a machine is set up rather than left to go stale. The lobby's read-only
posture for `_my_resources/` does not apply while you are running this guide —
the operator pointing you here IS the instruction to use it.

---

## 1. The mental model

Every secret in this system lives in gitignored files (`**/.env`,
`**/auth_keys/`), so **cloning the repos gives you zero credentials**. All of
them are bundled into one hand-carried file:

```
_my_resources/migrations/_secrets/master.env   <- gitignored; the operator copies this over manually
```

The master is a plain-text concatenation of every real env/credential file,
each wrapped in a marker pair:

```
# >>> FILE: Projects/AGY_AVIATIONCHAT/backend/.env
JWT_ADMIN_SECRET=...
...
# <<< END FILE: Projects/AGY_AVIATIONCHAT/backend/.env
```

Paths are relative to the lobby root, forward-slashed. A `MANIFEST` comment at
the top lists every bundled file. Restoring = splitting the blocks back out to
those paths. A script does it for you (§3), or you can do it by hand (§6).

## 2. What's in the bundle (inventory as of 2026-07-24)

| File (relative to lobby root) | What it powers |
|---|---|
| `.env` | Lobby-wide aggregate: GLM/Z.ai key, GitHub PATs, Gemini key, GCP project, Vertex Search IDs, Firebase web config, Sentry, Telegram, Anthropic key, incident-pipeline settings |
| `Projects/AGY_AVIATIONCHAT/auth_keys/.env` | AGY backend GCP/Vertex/Gemini config + `GOOGLE_APPLICATION_CREDENTIALS` pointer |
| `Projects/AGY_AVIATIONCHAT/auth_keys/service-account.json` | GCP service-account key the pointer above targets |
| `Projects/AGY_AVIATIONCHAT/backend/.env` | Incident pipeline: Sentry webhook/auth, GitHub token, Telegram bot, Anthropic key, JWT admin secret |
| `Projects/AGY_AVIATIONCHAT/frontend/.env.local` | Firebase web config, backend URL, site password |
| `Projects/AGY_AVIATIONCHAT/frontend/.env.production` | Production backend URLs (no secrets, but must exist for builds) |
| `Projects/BRKN_Tattoos/frontend/.env.local` | Resend API key |

The export script auto-discovers, so a newer `master.env` may contain more
files than this table — **the manifest inside the master is the source of
truth**, this table is orientation.

Note: `GOOGLE_APPLICATION_CREDENTIALS` values are deliberately **relative
paths** — nothing inside any env file needs editing for a new machine. If you
ever see an absolute `C:\Users\...` path in one, fix it to relative.

## 3. New-machine setup — do it in this order

**Order matters:** clone first, restore second. The restore script creates
missing directories, and `git clone` refuses to clone into a non-empty folder.

1. **Clone the lobby** to the same layout the operator uses (ask if unclear;
   the historical location is `~\.gemini\antigravity\scratch\Sudo_Hatter_Command`).
2. **Clone each sub-project repo** the operator works on into `Projects/`
   using the exact folder names from the master's manifest (e.g.
   `Projects/AGY_AVIATIONCHAT`, `Projects/BRKN_Tattoos`). Every sub-project is
   its own independent repo — the lobby repo does not contain them.
3. **Place the operator's copy of `master.env`** at
   `_my_resources/migrations/_secrets/master.env` (create the `_secrets` folder
   if needed), or leave it on the USB stick and pass its path with `-MasterPath`.
4. **Run the restore script** from the lobby root:

   ```powershell
   powershell -File _my_resources\migrations\Restore-EnvMaster.ps1
   # or: powershell -File _my_resources\migrations\Restore-EnvMaster.ps1 -MasterPath D:\master.env
   ```

   It writes every file to its original path, creates missing dirs, and backs
   up any existing-but-different file as `<name>.pre-restore.bak`.

   **On macOS / Linux use the twin script instead** — it resolves the lobby root
   itself, so it runs from anywhere:

   ```bash
   bash _my_resources/migrations/restore-env-master.sh --dry-run   # look first
   bash _my_resources/migrations/restore-env-master.sh             # then apply
   ```

   > ⛔ **Do not run the `.ps1` on macOS, even under `pwsh`.** It is
   > path-separator-bound — it joins `'_my_resources\migrations\_secrets\master.env'`
   > and does `$relPath.Replace('/', '\')`, so it would hunt for one literal
   > back-slashed filename and write `backend\.env` as a single file rather than
   > nesting it into `backend/`. The `.sh` is a verified twin (byte-identical
   > output on the same master); it also strips the CRLF a Windows-exported
   > `master.env` carries, and `chmod 600`s what it writes. §6's manual restore
   > remains the fallback if you have neither.
5. **Verify** (§4). Do not skip this.
6. **Delete the master from any transfer medium** (USB stick, download folder)
   once verified. Keep only `_my_resources/migrations/_secrets/master.env` on the
   machine.

## 4. Verification checklist (agent: run every line)

```powershell
# a) Every restored file must be IGNORED by its own repo — none may show as untracked.
git -C . status --short                                   # lobby: no .env, no _secrets/ anywhere
git check-ignore -v _my_resources/migrations/_secrets/master.env   # must print a .gitignore rule
git -C Projects/AGY_AVIATIONCHAT status --short           # no .env*, no auth_keys/
git -C Projects/BRKN_Tattoos status --short               # no .env.local

# b) Spot-check that keys actually landed (names, never print values):
Select-String -Path .env -Pattern '^[A-Z_]+=' | Measure-Object            # expect ~35+ lines
Test-Path Projects/AGY_AVIATIONCHAT/auth_keys/service-account.json        # True

# c) The service-account pointer resolves (run from AGY root):
#    auth_keys/.env has GOOGLE_APPLICATION_CREDENTIALS=auth_keys/service-account.json
```

If any restored file shows up in `git status`, **stop** — fix the `.gitignore`
before doing anything else. Never commit your way past it.

## 5. Beyond .env — per-machine setup the master can NOT carry

These are machine-local logins/toolchains, not files. Walk the operator
through each as needed:

- **gcloud**: `gcloud auth login` + `gcloud auth application-default login`,
  set the project from `GCP_PROJECT_ID` in `.env`.
- **GitHub CLI**: `gh auth login` (the PATs in `.env` are for the incident
  pipeline, not a substitute for gh auth).
- **Firebase CLI**: `firebase login`.
- **Java 17 (Temurin)** on PATH / `JAVA_HOME` — required by the Firestore
  rules-emulator test suite.
- **Python venvs**: rebuild per project; AGY's canonical test venv is
  `Projects/AGY_AVIATIONCHAT/backend/.venv` (never the repo root one).
  **For AGY, do NOT wing this** — follow the companion guide in this folder:
  [`python_vytest-updates-other-machines.md`](python_vytest-updates-other-machines.md).
  It carries the required interpreter (**3.11**, not whatever is newest — pytest
  will NOT warn you on the wrong one), the exact rebuild commands, and the
  verification walkthrough (machine-wide suite lock added 2026-08-01; the gate
  runs **parallel** — `-n auto --dist loadfile` — since 2026-08-03).
  > **Nothing extra to install.** `pytest-xdist`, `filelock`, `pytest-timeout`
  > and `pytest-cov` are all pinned in `backend/requirements.txt`, so the one
  > `pip install -r backend/requirements.txt` in the companion guide is the whole
  > job. Timings differ per machine because `-n auto` = core count — that is not
  > a signal, so don't chase it.
  > ⚠️ **Name it `.venv`, and keep it directly under `backend/`.** Several backend
  > tests are source-grep gates that walk `backend/` and read every `.py` they
  > find. They skip virtualenvs **by directory name** — `.venv*` plus a fixed
  > list. A venv named anything else (`env311`, `pyenv`, `venv3`) is walked and
  > read instead: **16,586 files / ~273 MB per test** rather than 217. Serially
  > that is merely slow; under `pytest -n auto` it blows the 300s timeout, and
  > pytest-timeout kills and respawns the worker on each trip — roughly **40
  > minutes of `node down` churn with no error message that names the cause**.
  > This cost two debugging sessions (2026-08-01/03); the fix and the full
  > mechanism are quick fix 1.1 in AGY's
  > `_artifacts/quick_fixes/quick-fix-1.1-xdist-tail-hang/walkthrough.md`. The
  > guard `test_scan_never_walks_a_colocated_virtualenv` now fails loudly and
  > names the directory instead, but only if you run the suite.


- **node_modules**: `npm install` per frontend.
- **GitNexus index**: machine-local, does not travel — re-index the repos you
  work in.
- **Claude auto-memory**: machine-local **by default** — `~/.claude` is not a
  repo, not a link, and not cloud-synced, so memory dies on the box that wrote
  it. Fix it once per machine:
  ```powershell
  powershell -File .agents\scripts\link-memory.ps1 -All          # dry run FIRST
  powershell -File .agents\scripts\link-memory.ps1 -All -Apply
  ```
  macOS uses the twin: `bash .agents/scripts/link-memory.sh --all [--apply]`.
  This junctions (symlinks on macOS) `~/.claude/projects/<slug>/memory/` to the
  repo's `_artifacts/_memory/`, so memory commits and travels like everything
  else.
  > ⚠️ **ORDER MATTERS ACROSS MACHINES.** The first machine to link **seeds**
  > the shared store; every later machine finds it populated and moves its own
  > local memory **aside to a backup** rather than merging. So link the machine
  > with the **newest** memories first, commit + push, then do the others. The
  > scripts never delete or merge — they back up and report — but if a stale
  > machine seeds first, everyone pulls stale memory.
  > ⚠️ The memory slug is **derived from the workspace's absolute path**, so a
  > rename re-points it — see `rename-fix.ps1`'s header and §3 of this folder's
  > `INDEX.md`. Skipping that step is what stranded 15 memory files here.
- **Git worktrees**: never travel between machines. If the operator parked
  work with `/sudo-park`, run `/sudo-resume` to recreate worktrees from the
  pushed branches — do not expect `git worktree list` to show anything.

## 6. Manual restore (no script available)

Open `master.env`. For each `# >>> FILE: <path>` … `# <<< END FILE: <path>`
pair: create `<path>` (relative to lobby root, create parent folders), paste
the lines between the markers verbatim (excluding the marker lines), save as
UTF-8 without BOM. Then run §4.

## 7. Keeping the master fresh (old machine / ongoing)

Any time a secret is added, rotated, or a new project gains a real `.env`:

```powershell
powershell -File _my_resources\migrations\Export-EnvMaster.ps1
```

It re-scans everything (lobby `.env`, all real `.env`/`.env.local`/
`.env.production` under `Projects/`, all `auth_keys/` contents; skips
`.env.example`, `node_modules`, venvs, worktrees) and rewrites
`_my_resources/migrations/_secrets/master.env` with a fresh manifest. It refuses
to run if the output isn't gitignored.

## 8. Security rules (non-negotiable)

- `master.env` and everything in any `_secrets/` folder is **never committed, never
  emailed, never pasted into a chat, never cloud-synced in plaintext**.
  Transfer via USB stick or a password-manager secure note/attachment.
- Never print secret **values** in agent output or logs — key names only.
- If the master may have been exposed (lost USB, pasted somewhere), treat
  every credential in it as burned and rotate them all.
