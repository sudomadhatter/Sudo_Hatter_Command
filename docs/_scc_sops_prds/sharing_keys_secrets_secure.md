# Sharing Keys & Secrets Securely — the Keyway guide

**What this page is for:** getting an API key, a database URL, or any other secret from your machine
onto a teammate's machine — or onto your *other* machine — **without it ever existing in a chat
message, an email, or a file somebody forgot to delete.**

Verified against **Keyway 0.5.3** on macOS, 2026-08-14. Every command and flag below was run against
the live binary, not copied from vendor docs.

> **The one-line version.** Secrets live in an encrypted cloud vault. **Your GitHub account is your
> key.** If you can push to the repo, you can read its secrets; if you lose repo access, you lose
> secret access. Nobody hands anybody a credential ever again.

---

## 1. Why this exists — the problem with `.env` files

A `.env` file is just a text file full of live credentials. It works fine until the moment you need a
second person or a second machine, and then every option is bad:

| The old way | What actually goes wrong |
|---|---|
| Paste keys into Slack/Discord/email | Permanent, searchable, backed up on someone else's servers, and screenshotted into oblivion. You cannot un-send it. |
| Zip the `.env` and share a drive link | The link outlives the person. Nothing tells you who downloaded it or when. |
| "Just ask me and I'll read it out" | Doesn't scale past two people, and it always happens at 11pm. |
| Commit it "just to the private repo" | It is now in git history **forever**, on every clone, including ones made by people who later left. |

The failure they share: **a copied secret has no leash.** Once it leaves your machine you can never
again answer "who has this?" or take it back. A vault fixes exactly that — nobody gets a copy to keep,
they get *access that can be switched off*.

---

## 2. The model — three moving parts

```
   ┌──────────────────────┐
   │  GitHub repo access  │   ← the ONLY access-control list. Add/remove people HERE.
   └──────────┬───────────┘
              │  Keyway reads your GitHub identity to decide what you may open
              ▼
   ┌──────────────────────┐
   │  Encrypted vault     │   ← the secrets themselves, per repo, split into environments
   │  (development /      │      (development, staging, production)
   │   staging /          │
   │   production)        │
   └──────────┬───────────┘
              │  keyway pull  →  writes a .env on disk
              │  keyway run   →  injects into RAM only, no file  ★ preferred
              ▼
   ┌──────────────────────┐
   │  Your running app    │
   └──────────────────────┘
```

Three things follow from this picture, and they are the whole discipline:

1. **You never grant access in Keyway.** You grant it on GitHub. Keyway just reads that.
2. **The vault is per repository**, and split by environment — so "everyone can run the app locally"
   and "two people can touch production" are the same system with different answers.
3. **`keyway run` is safer than `keyway pull`**, because a secret that never touches disk cannot be
   committed, backed up, indexed by a search tool, or read by an AI agent with filesystem access.

---

## 3. Install

### macOS — Homebrew (recommended)

```bash
brew install keywaysh/tap/keyway
```

Native Go binary, no runtime dependency, fast startup.

### Windows — npm

```powershell
npm install -g @keywaysh/cli
```

Or download `keyway-win-x64.exe` from the project's GitHub releases, rename it to `keyway.exe`, and
put it on your `PATH`.

### Verify — on either machine

```bash
keyway --version      # -> keyway version 0.5.3
keyway doctor         # full environment check, see §9
```

> ⚠️ **Two machines, two installs.** This system runs on a Mac *and* a PC. Installing Keyway on one
> does nothing for the other, and neither does logging in — credentials are stored in the OS keychain,
> which is per-machine by definition. Do §3 and §4 once **per machine**.

---

## 4. One-time setup, per repo

```bash
keyway login          # opens your browser for GitHub OAuth
keyway init           # links THIS repo to its vault (run from the repo root)
```

`keyway login` stores a session token in **macOS Keychain** / **Windows Credential Manager** — not in
a dotfile, so it is not something you can accidentally commit or sync to a backup.

`keyway init` needs write access to the GitHub repo, because creating a vault is an administrative act
on that repo. Run it once per repo, by one person; everyone else just logs in and pulls.

**Seed the vault the first time** by pushing whatever you already have:

```bash
keyway push                          # pushes ./.env into the 'development' environment
keyway push -f .env.production -e production
```

---

## 5. The commands you will actually use

| Command | What it does | When |
|---|---|---|
| `keyway run -- <cmd>` | Runs `<cmd>` with secrets injected **into memory only** | ★ every day — the default |
| `keyway pull` | Writes the vault into a local `.env` | when a tool *demands* a real file |
| `keyway push` | Uploads your local file into the vault | after adding a new key |
| `keyway set KEY` | Adds/rotates **one** secret, prompted and masked | rotating a single key |
| `keyway diff a b` | Compares which keys exist in two environments | "why does staging break?" |
| `keyway scan` | Greps the codebase for leaked credentials | before any push, and in CI |
| `keyway doctor` | Checks install, auth, connectivity, ignore rules | when something is weird |

### The daily loop

```bash
keyway run -- npm run dev            # frontend
keyway run -- python backend/main.py # backend
keyway run -e production -- ./deploy.sh
```

Nothing is written to disk. Close the terminal and the secrets are gone from the machine.

### Adding a new secret

```bash
keyway set STRIPE_SECRET_KEY                  # prompts, input is masked
keyway set DATABASE_URL="postgres://..." -e production
```

Prefer this over editing `.env` and running `keyway push` — it touches exactly one key, so it cannot
accidentally wipe or resurrect a neighbour.

---

## 6. ⭐ Using it correctly with a team

This is the part that matters. The tool is easy; the *discipline* is what keeps you safe.

### 6.1 Access is granted on GitHub, never in Keyway

Adding a collaborator to the GitHub repo (or the org team that owns it) is what grants vault access.
There is no second list to maintain, and that is deliberate — **two access lists always drift**, and
the drift is invisible until an ex-contractor still has your Stripe key.

### 6.2 Onboarding a teammate — the whole checklist

You do step 1. They do steps 2–5.

1. **You:** add them as a collaborator on the GitHub repo, with the least role that lets them work.
2. **Them:** clone the repo.
3. **Them:** install the CLI (§3).
4. **Them:** `keyway login`.
5. **Them:** `keyway run -- npm run dev` — it just works. No file was sent to them, ever.

Notice what is *absent*: you never send them anything, so there is no artifact to leak, and no step
where you have to remember to revoke something later.

### 6.3 Split by environment, and be stingy with production

Use the three environments as a permission boundary, not just as labels:

| Environment | Who should have it | Contains |
|---|---|---|
| `development` | every developer | test keys, sandbox credentials, local database URLs |
| `staging` | developers + QA | staging-only credentials |
| `production` | **the smallest possible number of people** | live keys that move real money and touch real user data |

Configure per-environment roles in the Keyway web dashboard at **app.keyway.sh**. The rule of thumb:
**a developer should be able to run the app all day without ever holding a production credential.**
If everyone has production, you have not improved on emailing the `.env` — you have just automated it.

> **⛔ This matters more here than in most systems.** Production for this system's projects touches
> real NDA-signed user data. A leaked production credential is not an inconvenience, it is a
> disclosure incident.

### 6.4 Offboarding — and the step everyone forgets

Removing someone from the GitHub repo or org **instantly** revokes their ability to pull or decrypt
the vault. That is the easy half.

> ### ⛔ Revocation does not un-copy what they already had.
>
> If a departing teammate ever ran `keyway pull`, a plain-text `.env` is sitting on their laptop right
> now, and cutting their GitHub access does nothing to it. **Revocation stops future reads. It does
> not reach backwards.**

So offboarding is **two** steps, always:

1. Remove them from the GitHub repo/org. *(stops future access)*
2. **Rotate every secret they could have pulled** — regenerate the key at the provider, then
   `keyway set <KEY>` to put the new value in the vault. *(neutralises copies they already hold)*

Skipping step 2 is the single most common way a vault-based setup still gets breached. Rotate first
for production, then staging; development sandbox keys are usually low enough risk to batch.

This is also the strongest practical argument for §6.5.

### 6.5 Prefer `keyway run` over `keyway pull` — as a team norm

Every `keyway pull` creates a durable plain-text copy that outlives the reason you made it. Every
`keyway run` does not. If the team's habit is `run`, then §6.4 step 2 shrinks from "rotate everything"
to "rotate what's actually exposed," and an offboarding stops being an emergency.

Pull when a tool genuinely cannot start without a file on disk. Otherwise, don't.

### 6.6 Never commit the `.env`, and prove it rather than trusting it

`.env` is already ignored in this repo — `.gitignore:42` carries `**/.env`. Confirm on any repo before
you trust it:

```bash
git check-ignore -v .env     # prints the rule that ignores it; silence + exit 1 means NOT ignored
```

Add `keyway scan` to CI so a leaked key fails the build rather than being discovered later:

```bash
keyway scan
keyway scan --json           # machine-readable, for a pipeline
keyway scan -e node_modules  # exclude noisy directories
```

### 6.7 Announce key changes; the vault is shared mutable state

`keyway push` and `keyway set` change what *everyone* gets on their next pull. Two habits prevent
confusing breakage:

- Tell the team when you add or rotate a key, so a colleague whose app suddenly breaks knows why.
- When someone reports "it works for me but not for them," reach for `keyway diff` before guessing:

```bash
keyway diff development production            # which KEYS differ
keyway diff development production --keys-only
```

Use `--show-values` only when you truly must, and never in a shared screen-share or a recorded call —
it prints live secrets to the terminal.

---

## 7. The dangerous flags — read once, remember forever

| Flag | What it does | Why it bites |
|---|---|---|
| `keyway push --prune` | Deletes vault secrets that are **not** in your local file | If your local `.env` is stale or partial, this **silently deletes** your teammates' keys from the vault. Push is additive *by default* for exactly this reason — `--prune` opts out of the safety. |
| `keyway pull --force` | Replaces your whole env file instead of merging | Blows away local-only overrides you forgot you had. |
| `keyway diff --show-values` | Prints real secret values | Fine alone at your desk. A disclosure on a screen-share. |
| `keyway set -l` | Writes to the local file instead of the vault (legacy) | Looks like it updated the vault. It did not. Your teammates get nothing. |
| `-y` / `--yes` | Skips the confirmation prompt | The prompt is the last thing standing between `--prune` and a bad afternoon. Do not pair them out of habit. |

---

## 8. Known false alarm — the `.gitignore` warning

`keyway doctor` reports:

```
⚠ .gitignore: Missing .env patterns in .gitignore
```

**On this repo, that is wrong — ignore it.** Keyway's doctor does naive literal string matching and
does not understand the recursive glob form. This repo ignores `.env` via `**/.env`, which is both
correct and deliberately broader than the literal Keyway looks for. Proof:

```bash
$ git check-ignore -v .env
.gitignore:42:**/.env	.env
```

Do **not** "fix" the ignore file on the strength of this warning. Its patterns are deliberately chosen
and commented, including the non-obvious cases (`.env.local`, and the `.pre-restore.bak` copies the
migration scripts leave behind). Trust `git check-ignore`, which is git itself answering, over a
third-party tool's guess about git.

---

## 9. When something is wrong — `keyway doctor` first

```bash
keyway doctor
```

Checks the CLI version, whether you are authenticated, that the GitHub repo is detected, API
connectivity, whether an env file exists, and the ignore rules. A healthy result on a set-up machine
is 6 passed. Two warnings are normal and expected:

- *"Not logged in"* — you have not run `keyway login` **on this machine** yet (§3's two-machine note).
- *".gitignore missing .env patterns"* — the false positive in §8.

| Symptom | Cause | Fix |
|---|---|---|
| `command not found: keyway` | Not installed on *this* machine | §3 |
| "Not logged in" after logging in elsewhere | Credentials are per-machine by design | `keyway login` here too |
| Teammate can't pull | They lack GitHub access, or never ran `keyway login` | Check the GitHub collaborator list first |
| Secrets missing after a colleague's push | Someone ran `--prune` against a stale file | Restore the key with `keyway set` |
| App can't see the variables | Ran the app directly rather than through Keyway | `keyway run -- <cmd>` |

Other commands that exist and are occasionally useful: `keyway logout`, `keyway connect` /
`keyway connections` / `keyway sync` / `keyway disconnect` (push secrets straight into Vercel or
Railway), and `keyway completion` (shell autocomplete).

---

## 10. Keyway vs. the migration kit — they solve different problems

Both move secrets around, and it is worth being clear that neither replaces the other:

| | **Keyway** | **`docs/migrations/scripts/env_master.py`** |
|---|---|---|
| Purpose | live sharing between **people** and machines | cold backup + **fresh-machine** disaster recovery |
| Needs network | yes — GitHub auth + API | no, fully offline |
| Scope | one repo's environment variables | the whole multi-project bundle: `.env` files, `auth_keys/`, GCP service-account JSON |
| Can revoke | **yes** — remove GitHub access | no, it is a file copy |
| Run it | daily | once per new machine |

**Use Keyway for anything a second person touches. Use the migration kit when setting up a machine
from scratch,** where you have no network trust yet and need service-account files that were never in
a `.env` to begin with. Setup context lives in
`docs/migrations/install_guides/machine_setup_card.md`.

---

## 11. Quick reference

```bash
# --- setup (once per machine, then once per repo) ---
brew install keywaysh/tap/keyway     # macOS
npm install -g @keywaysh/cli         # Windows
keyway login                         # GitHub OAuth, per machine
keyway init                          # per repo, from the repo root

# --- daily ---
keyway run -- npm run dev            # ★ secrets in RAM, nothing on disk
keyway run -e production -- ./deploy.sh
keyway set NEW_API_KEY               # add/rotate one secret, masked
keyway diff development production   # what differs
keyway scan                          # leak check
keyway doctor                        # health check

# --- occasionally ---
keyway pull                          # only when a tool needs a real file
keyway push                          # after editing .env by hand (additive)

# --- offboarding a teammate: BOTH steps ---
# 1. remove them from the GitHub repo/org
# 2. rotate every secret they could have pulled  -> keyway set <KEY>
```

---

## Related

- `.agents/skills/keyway-secrets/SKILL.md` — the agent-facing version of this page.
- `docs/migrations/install_guides/machine_setup_card.md` — new-machine setup, including Keyway.
- `docs/_scc_sops_prds/workflows_testing_SOP.md` — the main operator quick reference.
- Vendor documentation: <https://docs.keyway.sh> · dashboard: <https://app.keyway.sh>
