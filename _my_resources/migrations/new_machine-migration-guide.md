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

## 2. What's in the bundle (inventory as of 2026-07-24 — **re-verified 2026-08-04**)

> ✅ Confirmed accurate against a real master on the Desktop restore: the bundle carried **exactly these
> 7 blocks**, no more, no fewer. The table below was written before several current projects existed
> (`RAG_Pipeline_AC`, `NEXgen-VR-Director`, `Fresh_Workspace_BMAD`, `OpenChat-Openrouter`,
> `NEXGen-Films`, `B-L-WorldWide`) and it is still correct — those projects simply carry no real
> secrets yet. Count the markers before trusting it on any future master:
> `grep -c '^# >>> FILE:' _my_resources/migrations/_secrets/master.env`

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

1. **Clone the lobby** to the same layout the operator uses. Current location on
   the existing machines is **`C:\Sudo_Hatter_Command`** (drive root, verified
   2026-08-04). An older `~\.gemini\antigravity\scratch\Sudo_Hatter_Command`
   path appears in historical notes — that layout is dead; do not recreate it.
   The absolute path matters beyond taste: Claude Code's memory slug is derived
   from it (see step 8 / `link-memory.ps1`), so matching the other machines keeps
   the slug — and therefore the memory junction — identical everywhere.
2. **Clone the sub-projects — use the submodule machinery, not manual clones.** Every
   `Projects/<name>` is registered in the lobby as a **gitlink (mode 160000)** with its URL in
   `.gitmodules`, so one command brings them all down at the exact commits the lobby expects:

   ```bash
   git submodule update --init --recursive          # all of them
   git submodule status                             # '-' prefix = still not initialized
   ```

   Manual `git clone` per project also works, but you must use the **exact** folder names from
   `.gitmodules` — a typo produces a folder the lobby doesn't recognise and no tool will notice.

   > ⛔ **FIRST verify `.gitmodules` parity — this is the failure that actually happened.** A path can
   > be a gitlink with **no `.gitmodules` mapping**. Then `submodule update --init` has no URL to clone
   > from and **silently skips it**, leaving an empty folder forever, on every machine. On 2026-08-04
   > `NEXgen-VR-Director` and `BRKN_Tattoos` were both in this state; `git submodule status` didn't even
   > report it, because it **died** on the first unmapped path before reaching the second. Check parity
   > BEFORE trusting any clone step:
   >
   > ```bash
   > git ls-files -s Projects/ | awk '{print $4}' | sort > /tmp/links.txt
   > git config -f .gitmodules --get-regexp path | awk '{print $2}' | sort > /tmp/maps.txt
   > diff /tmp/links.txt /tmp/maps.txt && echo "parity OK"
   > ```
   >
   > `<` lines = gitlink with no mapping → **add the `[submodule]` block to `.gitmodules`** (that is the
   > fix; nothing else will work). `>` lines = mapping with no gitlink → a dead entry, delete it
   > (`AGY_JETCHAT` was one — the repo 404s).

   > ⚠️ **Verify this — a MISSING clone looks exactly like a present one.** The lobby records each
   > `Projects/<name>` as a gitlink (mode 160000). If the clone never happened, the folder can still
   > exist with files in it, and `git` commands run inside it **silently operate on the LOBBY repo**
   > instead of erroring. That is how a restored secret can land in a directory that belongs to no
   > repo at all. On the Desktop 2026-08-04, two of eight were in this state — `BRKN_Tattoos` (which
   > the master restores a secret into) and `NEXgen-VR-Director` (which is in
   > `.agents/maintained-projects.txt`, so the step-8 memory linker targets it and its
   > `_artifacts/_memory` could never be committed). Check every one:
   >
   > ```bash
   > cd Projects && for p in */; do p=${p%/}
   >   [ -e "$p/.git" ] && echo "OWN REPO  $p" || echo "NO .git   $p  <- not cloned"
   > done
   > ```
   >
   > Anything reported `NO .git` still needs cloning before steps 3, 5 or 8 mean anything for it.
   >
   > **Never let a tool write into an un-cloned folder.** `sync-agents.ps1 -Maintained` and
   > `check_maps.py --all` now both refuse and print the `submodule update --init` remedy (guards added
   > 2026-08-04, after a sync wrote 601 toolkit files into NEXgen's empty placeholder). If you script
   > anything new that walks `maintained-projects.txt`, copy that guard — a directory existing is
   > **not** proof the project is here.
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

> ⛔ **The restore's OWN backups escape the ignore rules — check them explicitly.** Both restore
> scripts write `<name>.pre-restore.bak` beside every file they overwrite, and that suffix defeats
> exact-name patterns: `.env.local` does **not** match `.env.local.pre-restore.bak`. On the
> 2026-08-04 Desktop restore this left a live Firebase API key in an untracked
> `frontend/.env.local.pre-restore.bak`. `auth_keys/` copies happened to be safe only because the
> whole directory is ignored. Run this after every restore:
>
> ```bash
> git status --short | grep -iE '\.env|_secrets|auth_keys|service-account|\.bak'   # expect NOTHING
> ```
>
> Fixed 2026-08-04 by adding `*.pre-restore.bak` to AGY's `.gitignore` and `**/*.pre-restore.bak`
> plus `**/.env.local` to the lobby's. **A new project restored into for the first time will not have
> those rules** — re-run the grep there rather than assuming.

> ⚠️ **A restored file showing as ` M` (modified, tracked) is usually just line endings.**
> `frontend/.env.production` is tracked on purpose (URLs, no secrets). The restore scripts write LF
> while the working tree is CRLF, so it reads as modified with an **empty** content diff. Confirm
> before acting — `git show HEAD:<path> | tr -d '\r'` against `tr -d '\r' < <path>` — and if they
> match, `git checkout -- <path>` rather than committing a whitespace-only change.

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
  > ⚠️ **Pin Node to 22 LTS first.** `brew install node` gives the current major (26 as of
  > 2026-08-06), which breaks vitest's jsdom environment — see the ⛔ box in the vitest section of
  > [`python_vytest-updates-other-machines.md`](python_vytest-updates-other-machines.md).
- **GitNexus**: machine-local, does not travel. **Neither the CLI nor the index arrives with a
  clone** — both are per-machine (2026-08-06, the Mac):
  ```bash
  npm i -g gitnexus                 # the CLI itself; nothing else installs it
  gitnexus analyze                  # run from EACH repo root you work in (lobby + AGY)
  gitnexus list                     # confirm both repos registered, commit == HEAD
  ```
  > ⛔ **The MCP registration is Windows-only in git — a Mac gets NO gitnexus tools until you
  > override it locally.** The tracked lobby `.mcp.json` launches the server as
  > `cmd /c gitnexus mcp`; `cmd` does not exist on macOS, so the server silently never starts.
  > **Do not "fix" the tracked file** — bare commands break Claude Code on native Windows, which
  > genuinely needs the `cmd /c` wrapper. Instead add a **local-scope** override, which outranks
  > project scope (precedence: local > project > user), in `~/.claude.json` under
  > `projects["<repo path>"].mcpServers`:
  >
  > ```json
  > "gitnexus": {
  >   "command": "/opt/homebrew/bin/node",
  >   "args": ["/opt/homebrew/lib/node_modules/gitnexus/dist/cli/index.js", "mcp"]
  > }
  > ```
  >
  > ⛔ **Use those ABSOLUTE paths — `"command": "gitnexus"` is a second silent failure on macOS.**
  > `launchctl getenv PATH` is unset here, so a GUI-launched editor spawns children with only
  > `/usr/bin:/bin:/usr/sbin:/sbin` — no `/opt/homebrew/bin`. Naming `gitnexus` bare fails to resolve,
  > and even an absolute `/opt/homebrew/bin/gitnexus` still dies, because its `#!/usr/bin/env node`
  > shebang looks `node` up on that same stripped PATH (`env: node: No such file or directory`).
  > Invoking the real node binary against the CLI script sidesteps both. Proved with
  > `env -i PATH=/usr/bin:/bin`: bare and absolute-shim both fail, this form returns 17 tools.
  >
  > Set for the lobby and AGY on the Mac. Verify without launching a session by piping an
  > `initialize` + `tools/list` JSON-RPC pair into `gitnexus mcp` — expect 17 tools and a
  > `repoCount` matching `gitnexus list`. ⚠️ macOS has **no `timeout`** binary; a smoke test that
  > uses it exits 127 and prints nothing, which reads exactly like a dead server. Use
  > `perl -e 'alarm(40); exec "gitnexus","mcp"'`.
  >
  > ⚠️ **`gitnexus analyze` rewrites tracked skill docs** (`.claude/skills/gitnexus/*/SKILL.md`) to
  > match the installed version. Upstream those to the `.agents/` master before committing, or the
  > next `/sync-agents` reverts them — and keep every machine on the same gitnexus version, or they
  > will flip-flop the same three files forever.
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
