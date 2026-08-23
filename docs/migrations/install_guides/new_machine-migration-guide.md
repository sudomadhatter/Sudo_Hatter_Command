# Env Migration Guide — setting up secrets on a new machine

**Audience:** the AI agent (or human) setting up a fresh computer for the
Sudo_Hatter_Command lobby and its sub-projects.
**You need exactly two things:** this document, and the operator's `master.env`
file (hand-carried — it is never in git).

**Where this kit lives:** `docs/migrations/` — this guide, both
`*-EnvMaster.ps1` scripts, `rename-fix.ps1`, the `auth_keys/_secrets/` vault, and the
companion guide `python_vytest-updates-other-machines.md` (venv rebuild — §5). It sits
under `docs/` on purpose (moved there by SCC-89): this is what a fresh machine
follows, so it must be **scanned and kept current**, not parked somewhere the
drift-checkers are forbidden to look. **Never delete it** once a machine is set
up. Using it is always in-bounds — the operator pointing you here IS the
instruction to read the guides and run the scripts.

---

## 1. The mental model

Every secret in this system lives in gitignored files (`**/.env`,
`**/auth_keys/`), so **cloning the repos gives you zero credentials**. All of
them are bundled into one hand-carried file:

```
docs/migrations/auth_keys/_secrets/master.env   <- gitignored; the operator copies this over manually
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
> `grep -c '^# >>> FILE:' docs/migrations/auth_keys/_secrets/master.env`

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
   `docs/migrations/auth_keys/_secrets/master.env` (create the `_secrets` folder
   if needed), or leave it on the USB stick and pass its path with `-MasterPath`.
4. **Run the restore script** from the lobby root:

   ```powershell
   powershell -File docs\migrations\scripts\Restore-EnvMaster.ps1
   # or: powershell -File docs\migrations\scripts\Restore-EnvMaster.ps1 -MasterPath D:\master.env
   ```

   It writes every file to its original path, creates missing dirs, and backs
   up any existing-but-different file as `<name>.pre-restore.bak`.

   **On macOS / Linux use the twin script instead** — it resolves the lobby root
   itself, so it runs from anywhere:

   ```bash
   bash docs/migrations/scripts/restore-env-master.sh --dry-run   # look first
   bash docs/migrations/scripts/restore-env-master.sh             # then apply
   ```

   > ⛔ **Do not run the `.ps1` on macOS, even under `pwsh`.** It is
   > path-separator-bound — it joins `'docs\migrations\auth_keys\_secrets\master.env'`
   > and does `$relPath.Replace('/', '\')`, so it would hunt for one literal
   > back-slashed filename and write `backend\.env` as a single file rather than
   > nesting it into `backend/`. The `.sh` is a verified twin (byte-identical
   > output on the same master); it also strips the CRLF a Windows-exported
   > `master.env` carries, and `chmod 600`s what it writes. §6's manual restore
   > remains the fallback if you have neither.
5. **Verify** (§4). Do not skip this.
6. **Delete the master from any transfer medium** (USB stick, download folder)
   once verified. Keep only `docs/migrations/auth_keys/_secrets/master.env` on the
   machine.

## 4. Verification checklist (agent: run every line)

```powershell
# a) Every restored file must be IGNORED by its own repo — none may show as untracked.
git -C . status --short                                   # lobby: no .env, no _secrets/ anywhere
git check-ignore -v docs/migrations/auth_keys/_secrets/master.env   # must print a .gitignore rule
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

### 4b. The five gates — the machine is not "done" until all five are green

Secrets landing correctly proves the **restore** worked, not that the machine can **build and test**.
Those are different claims, and on 2026-08-06 the Mac passed §4 in full while three of these five
could not run at all. Run every one and match the count — a suite that collects 0 tests and exits 0
looks exactly like a suite that passed.

| # | Gate | Command (from the repo root) | Expected 2026-08-06 |
|---|------|------------------------------|---------------------|
| 1 | Backend unit | `backend/.venv/bin/python -m pytest backend/tests -n 8` | 3025 passed / 35 skipped |
| 2 | Frontend unit | `(cd frontend && npm test)` | 581 passed / 1 skipped |
| 3 | Firestore rules | `(cd firebase/tests && npm test)` | 70 pass / 0 fail |
| 4 | Backend emulator | `node backend/tests/e2e_emulator/run-emulator-e2e.mjs` | 39 passed |
| 5 | E2E journeys | `(cd frontend && npm run test:e2e)` | 31 passed |

Gates 3–5 all need Java + `firebase/tests/node_modules`, and gate 5 also needs the Playwright
browsers — see §5. Gates 4 and 5 discover Java themselves; strip `JAVA_HOME` deliberately
(`env -u JAVA_HOME …`) at least once to prove the discovery works and you are not leaning on a
shell export that automation will not have.

The lobby has a sixth, separate gate for the workflow-enforcement scripts:

```bash
python3 .agents/scripts/tests/run_all.py      # Mac;  on the PC: python .agents/...
                                              # expect "6/6 files passed"  (124 checks, ~10 s)
```

> ⛔ **This is where a POSIX-only failure will surface first.** The toolkit was authored on Windows,
> where `os.chmod` only toggles the read-only attribute — so a test that restored a file with bare
> `stat.S_IWRITE` (0o200, *write-only*) passed there for months and died on macOS with
> `PermissionError` the moment it read the file back. One bad line took down the whole gate. Fixed
> 2026-08-06 in `test_story_status.py`; expect more of the same shape, and fix the **master**
> `.agents/` copy first, then propagate to the maintained projects.

## 5. Beyond .env — per-machine setup the master can NOT carry

These are machine-local logins/toolchains, not files. Walk the operator
through each as needed:

- ### ⛔ **The commit gates — do this FIRST, it is one command** *(added 2026-08-08, SCC-31)*

  ```bash
  git config --global core.hooksPath .githooks
  ```

  **Why this leads the list.** Every commit gate we have — the Jira key check, the encoding
  check, and the SOP-currency check — is armed by git's `core.hooksPath`, and that setting is
  **local config: it does NOT travel with a clone.** Unset, git reads `.git/hooks`, finds an
  empty directory, and **every gate is silently off while the repo looks completely normal.**
  There is no warning, no output, and nothing in `git status` to notice. A machine can run for
  weeks producing unkeyed commits and stale docs, and the first symptom is a Jira board with
  holes in it.

  Setting it **globally with a RELATIVE value** is the fix, and the relative part is the trick:
  git resolves it against *each repo's own working-tree root*, so this one command arms every
  clone on the machine — the lobby, every project, and every repo you clone later — while
  staying a harmless no-op in any repo that has no `.githooks/` directory. A per-repo
  `git config core.hooksPath .githooks` also works but has to be repeated forever, which is how
  it ended up set in three of four repos here.

  **Verify it fires** (from the lobby, on a throwaway branch — a rejected commit is a no-op,
  your staged files are untouched):

  ```bash
  git checkout -b tmp/gate-check
  git commit --allow-empty -m "no key here"     # expect: REJECTED, "No Jira work-item key"
  git commit --allow-empty -m "SCC-1 probe"     # expect: accepted
  git checkout - && git branch -D tmp/gate-check
  ```

  If the first one *succeeds*, the gates are not armed on this machine — re-run the config
  command and check `git config --global core.hooksPath` reads `.githooks`.

- **Python's name differs per OS.** The Mac has **only `python3`** (no bare `python`, not even in
  a login shell); a python.org install on Windows has **only `python`**; `py` is the Windows
  launcher. Docs are written `python3` — on the PC, drop the `3`. **Nothing to install and nothing
  to alias**: every hook probes `python3 → python → py`, so the gates work on either OS untouched.
  Only the commands *you type* differ.

- ### ⛔ **Jira board access — `acli` + ONE API token** *(added 2026-08-22, SCC-294)*

  Full procedure: [`jira-api-token-setup.md`](jira-api-token-setup.md). Do not improvise it —
  it carries the traps.

  **Why it sits beside the commit gates rather than with the logins below.** Every ticket this
  system mints, moves, describes or closes goes through `acli`, and `acli` needs a credential the
  credential store holds and git cannot carry. Unset, an agent reports *"I have no Jira
  integration"* — which is false, the CLI **is** the integration — and then quietly stops writing
  the board while everything else looks normal. Same silent-failure shape as an unarmed
  `core.hooksPath`, and the first symptom is the same: a board with holes in it.

  The **same** token is the only way to upload a file to a ticket: `acli`'s `workitem attachment`
  has `list` and `delete` and no `add` (measured on 1.3.22-stable). Store it once, under the name
  `sudo-jira`, and both consumers read it.

  ```bash
  acli jira auth status      # the whole check: expect a site, an email, and api_token
  ```

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
- **code-review-graph** (the code graph): machine-local, does not travel. **Neither the CLI nor the
  index arrives with a clone** — both are per-machine:
  ```bash
  # Mac
  brew install pipx && pipx ensurepath
  pipx install code-review-graph
  # Windows PC
  python -m pip install --user pipx && python -m pipx ensurepath && pipx install code-review-graph
  #   set PYTHONUTF8=1 for this server; keep fastmcp >= 3.2.4

  code-review-graph build      # from EACH repo root you work in (lobby + AGY)
  code-review-graph status     # confirm built_at_commit == current_sha
  ```
  > ⛔ **The tracked `.mcp.json` names the command portably (`code-review-graph serve`), and that is
  > not always enough for a GUI-launched editor.** `launchctl getenv PATH` is unset on macOS, so an
  > editor started from the Dock spawns children with only `/usr/bin:/bin:/usr/sbin:/sbin` — no
  > `~/.local/bin`, where pipx puts the console script. The server then never starts and the session
  > simply has no graph tools, with no error anywhere. **Do not "fix" the tracked file** — it is
  > correct for a terminal and for CI. Add a **local-scope** override instead, which outranks project
  > scope (precedence: local > project > user), in `~/.claude.json` under
  > `projects["<repo path>"].mcpServers`:
  >
  > ```json
  > "code-review-graph": {
  >   "command": "/Users/<you>/.local/bin/code-review-graph",
  >   "args": ["serve"]
  > }
  > ```
  >
  > Set for the lobby and AGY on the Mac. Verify without launching a session by piping the JSON-RPC
  > handshake into `code-review-graph serve` — expect **30 tools**. ⚠️ macOS has **no `timeout`**
  > binary; a smoke test that uses it exits 127 and prints nothing, which reads exactly like a dead
  > server. Use `perl -e 'alarm(60); exec "code-review-graph","serve"'`. ⚠️ And the handshake needs
  > `{"jsonrpc":"2.0","method":"notifications/initialized"}` **between** `initialize` and
  > `tools/list` — without it the server answers the handshake and lists nothing, which looks
  > identical to a failure. The full probe is in `docs/code-review-graph.md`.
- **opencode**: one of the four platforms the toolkit syncs to, and **none of it travels** (2026-08-06,
  the Mac). A clone brings the repo-side surface only — `opencode.json`, `.opencode/commands/` (47) and
  `.opencode/agent/` (13) — which is why the config looks complete while the machine has no opencode at
  all. Three separate machine-local pieces:
  ```bash
  brew install sst/tap/opencode     # 1. the CLI. Nothing else installs it
  pwsh -File .agents/scripts/sync-agents.ps1 -GlobalsOnly   # 2. the ~/.config/opencode/commands cache
  opencode auth login               # 3. provider credentials — INTERACTIVE, cannot be scripted
  ```
  > **The global command cache is what makes `/cicd-*` work outside a synced repo.** Step 2 is the same
  > `/smh-sync-agents -GlobalsOnly` used on Windows; it also refreshes the Antigravity workflows, the Codex
  > prompts and the 56 bmad-* Codex skills. Expect `opencode global -> 47 cmds`.
  >
  > ⛔ **`sync-agents.ps1` could not do step 2 on macOS before 2026-08-06 — and it failed in the two ways
  > that hide themselves.** `$env:USERPROFILE` is Windows-only, so `Join-Path $null` **threw** and took
  > the whole global stage down *after* the local sync had already printed its success lines; and
  > `robocopy` does not exist off Windows, so the codex-skills mirror died having created exactly **one**
  > skill directory — a half-built cache that looks deliberate. Both are fixed (Windows still takes the
  > robocopy path verbatim). If a global cache is ever empty here, re-run with `-WhatIf` and read the
  > *whole* output — the failure is never on the last line.
  >
  > ⚠️ **Credentials are the one step nobody can do for you.** They live in
  > `~/.local/share/opencode/auth.json`, are machine-local like every other login in this section, and
  > `opencode auth login` is a TUI — an agent cannot run it. Until it is done, `opencode models` lists
  > only the free `opencode/*` tier and every pinned agent fails. The `.opencode/agent/opus-*` files and
  > `/cicd-autopilot-opencode` pin **`openrouter/…`** models, so the provider to authenticate is **OpenRouter**
  > unless that pin changes. Verify with `opencode auth list`, then `opencode models | grep openrouter`.
  >
  > ⚠️ **opencode gets no MCP servers from this repo — on any platform.** It reads `mcp` out of
  > `opencode.json`, and ours has no such key; the `.opencode/mcp.json` file sitting next to it is read by
  > nothing. So code-review-graph and md-feedback are Claude-only today. Confirm with
  > `opencode debug config | grep '"mcp"'` (no match = none loaded). Pre-existing and shared with Windows,
  > not a Mac gap — listed here so nobody re-diagnoses it as one.
  >
  > Health-check the whole surface without starting a session — `opencode debug config` must show the
  > `instructions` list, `skills.paths`, and all 12 agents.
  >
  > ⛔ **`.opencode/agent/INDEX.md` used to load as a PHANTOM AGENT** (fixed 2026-08-07). opencode
  > registers every `.md` in that directory as an agent definition, so the folder's own map file became
  > a selectable agent named `INDEX` (mode `all`) whose entire prompt is a list of its sibling files. It
  > was present in six projects. The command surface never had this bug because
  > `.agents/commands/INDEX.md` declares `platforms: []` and `Sync-CommandDir` filters on that — but
  > `Sync-Dir` is a plain tree copy, so `-ExcludeFiles 'INDEX.md'` had to be stated explicitly. Agent
  > count is **12**, not 13; if you see 13, the exclusion has regressed.
- **Codex CLI**: the fourth platform. Its two caches (`~/.codex/prompts`, `~/.codex/skills`) are filled
  by the same `-GlobalsOnly` sync as opencode's, so they can be fully populated on a machine where the
  CLI itself is **not installed** — which reads as "Codex is set up" when nothing can invoke it. Install
  and authenticate separately (2026-08-07, the Mac):
  ```bash
  brew install --cask codex        # a plain BINARY cask — no .pkg, so no interactive sudo
  codex login status               # expect "Not logged in" on a fresh box
  codex login                      # INTERACTIVE browser OAuth — an agent cannot run this
  codex doctor                     # auth ✓ + runtime/install/search/git all ✓
  ```
  > ⚠️ There is **no OpenAI key anywhere in `master.env`** — the bundle carries Anthropic, Gemini and
  > Z.ai keys only. So the API-key route is not available from the migration kit and `codex login`
  > (ChatGPT account, browser) is the only path. Same shape as `gh auth login`: it needs a real
  > terminal, and backgrounding it just wedges.
  >
  > `codex doctor` also reports `⚠ websocket — Responses WebSocket failed; HTTPS fallback may still
  > work`. That appeared on a healthy fresh install here and is not a blocker; re-check it only if
  > sessions actually misbehave after login.
- **Git identity**: `user.name` / `user.email` live in `~/.gitconfig` — machine-local, never in a
  clone. With nothing set, git **invents** one from the hostname (`sudohatter@Sudos-MacBook-Pro.local`)
  and commits happily, so nothing fails and nothing warns. Those commits are orphans: GitHub cannot
  match the address to the account, so they show no avatar, earn no contribution square, and split
  `git shortlog` into two people. Seven commits were already pushed that way on 2026-08-06 before
  anyone noticed. Set it **before the first commit**, and confirm it against the history you are
  joining rather than from memory:
  ```bash
  git log --pretty="%ae" | sort | uniq -c | sort -rn | head   # the address this repo actually uses
  git config --global user.name  "sudomadhatter"
  git config --global user.email "sudomadhatter@gmail.com"
  ```
  > Already-pushed commits keep the wrong author — rewriting them means a force-push over shared
  > history, so leave them unless the contribution graph genuinely matters.
- **Java / `JAVA_HOME`**: the Firebase emulators (Firestore + Auth) are Java, and **nothing on macOS
  points at the JDK for you.** Homebrew's `openjdk@17` is keg-only and is NOT registered with
  `/usr/libexec/java_home`, so that helper answers *"Unable to locate a Java Runtime"* next to a
  perfectly good install. Export it explicitly — **in `~/.zshenv`, not `~/.zshrc`**:
  ```bash
  export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
  ```
  > ⛔ **`~/.zshrc` is interactive-only.** Agents, git hooks, npm scripts and anything run as
  > `zsh -c` never source it, so the variable is there when you test by hand and gone in every
  > automated path — the tests then fail *only* under automation, on the same machine that just
  > passed. `~/.zshenv` is read by **every** zsh. This is the second variable on this Mac to be lost
  > exactly this way (Node 22's PATH was the first). Verify all three modes, never one:
  > ```bash
  > for m in -c -lc -ic; do zsh $m 'echo $JAVA_HOME'; done
  > ```
- **Firebase emulator harness**: `firebase/tests/node_modules` is a **separate `npm install`** from
  the frontend's, and three different suites resolve `firebase-tools` out of it — the TEA-12 rules
  suite, the backend emulator tier, and the TEA-16 E2E journeys. Miss it and all three die at once
  with `firebase-tools not found`, which reads like a broken repo rather than a skipped install:
  ```bash
  (cd Projects/AGY_AVIATIONCHAT/firebase/tests && npm install)
  ```
  > ⚠️ That install rewrites `package-lock.json` with pure npm-version metadata churn (`peer` flags,
  > a nested optional `picomatch`). **Discard it** (`git checkout -- firebase/tests/package-lock.json`)
  > — committing it just starts a diff war with the Windows machine.
  >
  > The emulator JARs themselves are a separate machine-local download into `~/.cache/firebase/`.
  > Nothing fetches them ahead of time; the first `emulators:exec` pulls them, so budget a slow
  > first run rather than assuming it hung.
- **Playwright browsers**: `npm install` gets the *library*; the ~90 MB browser binaries are a
  machine-local cache in `~/Library/Caches/ms-playwright` that no clone carries:
  ```bash
  (cd Projects/AGY_AVIATIONCHAT/frontend && npx playwright install chromium)
  ```
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
  work with `/cicd-park`, run `/cicd-resume` to recreate worktrees from the
  pushed branches — do not expect `git worktree list` to show anything.

## 6. Manual restore (no script available)

Open `master.env`. For each `# >>> FILE: <path>` … `# <<< END FILE: <path>`
pair: create `<path>` (relative to lobby root, create parent folders), paste
the lines between the markers verbatim (excluding the marker lines), save as
UTF-8 without BOM. Then run §4.

## 7. Keeping the master fresh (old machine / ongoing)

Any time a secret is added, rotated, or a new project gains a real `.env`:

```powershell
powershell -File docs\migrations\scripts\Export-EnvMaster.ps1
```

It re-scans everything (lobby `.env`, all real `.env`/`.env.local`/
`.env.production` under `Projects/`, all `auth_keys/` contents; skips
`.env.example`, `node_modules`, venvs, worktrees) and rewrites
`docs/migrations/auth_keys/_secrets/master.env` with a fresh manifest. It refuses
to run if the output isn't gitignored.

## 8. Security rules (non-negotiable)

- `master.env` and everything in any `_secrets/` folder is **never committed, never
  emailed, never pasted into a chat, never cloud-synced in plaintext**.
  Transfer via USB stick or a password-manager secure note/attachment.
- Never print secret **values** in agent output or logs — key names only.
- If the master may have been exposed (lost USB, pasted somewhere), treat
  every credential in it as burned and rotate them all.
