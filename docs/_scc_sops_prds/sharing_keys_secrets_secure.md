# Sharing Keys & Secrets Securely — the Keyway guide

**What this page is for:** getting an API key, a database URL, or any other secret from your machine
onto a teammate's machine — or onto your *other* machine — **without it ever existing in a chat
message, an email, or a file somebody forgot to delete.**

**Verified against Keyway 0.5.3 on macOS, 2026-08-14.** Every command name and flag below was checked
against the live binary's own `--help`, not copied from vendor docs. Where a statement describes
*behaviour* rather than a flag — what `login` stores, what `init` requires — it comes from vendor
documentation and is marked. The one behaviour that **was** observed directly is in §8, because it
bites.

> **The one-line version.** Secrets live in an encrypted cloud vault. **Your GitHub account is your
> key.** If you can push to the repo, you can read its secrets; if you lose repo access, you lose
> secret access. Nobody hands anybody a credential ever again.

---

## ⚡ Quick Start: Sharing Secrets with a Teammate in 2 Minutes

You never send a `.env` file, link, or password. Access is granted directly through GitHub permissions.

### 1. What You Do (Owner / Admin)
1. Add the teammate as a collaborator on GitHub ([AGY_AVIATIONCHAT Collaborators](https://github.com/sudomadhatter/AGY_AVIATIONCHAT/settings/access) or Sudo_Hatter_Command).
2. *(Optional)* Restrict `production` access in the [Keyway Dashboard](https://app.keyway.sh) so developers receive only `development` sandbox keys.

### 2. What Your Teammate Does (New Dev)
Send your teammate these 4 quick commands:
```bash
# 1. Clone the repo and enter it
git clone <repo-url> && cd <repo-dir>

# 2. Install the Keyway CLI
brew install keywaysh/tap/keyway      # macOS
npm install -g @keywaysh/cli          # Windows

# 3. Authenticate via GitHub (one-time browser OAuth)
keyway login

# 4. Run the app with secrets in RAM (zero files on disk)
keyway run -- npm run dev             # frontend
keyway run -- python backend/main.py  # backend
```

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
a dotfile, so it is not something you can accidentally commit or sync to a backup. *(Vendor-documented
behaviour, not observed here.)*

`keyway init` needs write access to the GitHub repo, because creating a vault is an administrative act
on that repo. Run it once per repo, by one person; everyone else just logs in and pulls.

### Seeding the vault — read §8 first, then sort before you push

> ### ⛔ `keyway push` writes to your `.gitignore` without asking.
>
> This was **observed directly** on 0.5.3, in this repo, before authenticating. A bare `keyway push`
> prints `✓ Added .env* to .gitignore` and `✓ Created .env file`, and appends `.env*` to the file. No
> prompt, no `-y` required. **Check `git diff .gitignore` after your first push and revert it if you
> did not want it** — this repo's ignore rules are deliberately chosen and commented, and a blanket
> `.env*` also swallows the tracked `.env.example` template.

⛔ **Sort your keys before the first push, not after.** Bare `keyway push` sends the whole file into
one environment. If your local `.env` mixes sandbox and live credentials — the lobby's root `.env` does —
then a bare push files live production keys into `development`, which §6.3 says **every developer**
can read. Split them first:

```bash
keyway push -f .env.development -e development   # be explicit; push advertises no default
keyway push -f .env.production  -e production
```

`keyway push` is the one documented command whose `--help` states **no** default environment, so name
`-e` explicitly rather than relying on one.

---

## 5. The commands you will actually use

| Command | What it does | When |
|---|---|---|
| `keyway run -e <env> -- <cmd>` | Runs `<cmd>` with secrets injected **into memory only** | ★ every day — the default |
| `keyway pull -e <env>` | Writes the vault into a local `.env` | when a tool *demands* a real file |
| `keyway push` | Uploads your local file into the vault | after adding a new key |
| `keyway set KEY` | Adds/rotates **one** secret, prompted and masked | rotating a single key |
| `keyway diff a b` | Compares which keys exist in two environments | "why does staging break?" |
| `keyway scan` | Greps the codebase for leaked credentials | before any push, and in CI |
| `keyway doctor` | Checks install, auth, connectivity, ignore rules | when something is weird |

### The daily loop

```bash
keyway run -e development -- npm run dev             # frontend
keyway run -e development -- python backend/main.py  # backend
keyway run -e production  -- ./deploy.sh
```

Nothing is written to disk. Close the terminal and the secrets are gone from the machine.

> ### ⛔ Always name `-e`. Without it, `run` and `pull` stop and wait for a human.
>
> `keyway run` with no `-e` does **not** quietly default to `development`. It draws an interactive
> menu and blocks until somebody presses a key:
>
> ```
> ┃ Environment:
> ┃ > development
> ┃   staging
> ┃   production
> ```
>
> At your own terminal that is a mild surprise — you pick one and carry on. Anywhere without a human
> attached it is a hang: a CI job, a `cron` entry, a script, or an AI agent will sit there until it
> is killed, with no error message and nothing in the log to explain it. The menu is drawn, nobody
> answers, and the run burns its entire timeout.
>
> This is the same behaviour §7 describes for `keyway sync`, and it is the reason **every** command
> in this guide names its environment explicitly. Treat "the docs say it defaults to development" as
> insufficient: the default decides which environment is *pre-selected in the menu*, not whether the
> menu appears.

### Adding a new secret

```bash
keyway set STRIPE_SECRET_KEY                  # prompts, input is masked  ← use this form
keyway set DATABASE_URL -e production         # same, for another environment
```

Prefer this over editing `.env` and running `keyway push` — it touches exactly one key, so it cannot
accidentally wipe or resurrect a neighbour.

> ⚠️ **Use the prompted form, not `keyway set KEY=value`.** The inline form works, but it writes the
> live secret into your shell history (`~/.zsh_history`, PowerShell's `ConsoleHost_history.txt`),
> your terminal scrollback, and any agent tool-call log. That is a durable plain-text copy of the
> credential — the exact thing §1 says a vault exists to prevent — and it survives the rotation you
> were probably running the command to perform.

---

## 6. ⭐ Using it correctly with a team

This is the part that matters. The tool is easy; the *discipline* is what keeps you safe.

### 6.1 Access is granted on GitHub, never in Keyway

Adding a collaborator to the GitHub repo (or the org team that owns it) is what grants vault access.
Keep GitHub as the list that decides **who is in at all** — that is deliberate, because **two access
lists always drift**, and the drift is invisible until an ex-contractor still has your Stripe key.

> **One honest qualification, because the rest of this section depends on it.** Keyway's web dashboard
> (§6.3) *can* hold per-environment roles, which is a second surface. Use it for **which environment
> an already-approved person may reach**, never as a way to grant someone access GitHub did not.
> Keep membership decisions in one place and scope decisions in the other, and **§6.4 makes you check
> both on the way out** — a role left behind in a dashboard is exactly the drift this rule is about.

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

So offboarding is **three** steps, always:

1. Remove them from the GitHub repo/org. *(stops future access)*
2. **Clear any per-environment role you gave them in the Keyway dashboard** (§6.3). If you never used
   the dashboard, there is nothing here to do — but check rather than assume, because this is the one
   surface GitHub removal does not obviously cover.
3. **Rotate every secret they could have pulled** — regenerate the key at the provider, then
   `keyway set <KEY>` to put the new value in the vault. *(neutralises copies they already hold)*

Skipping step 3 is the single most common way a vault-based setup still gets breached. Rotate first
for production, then staging; development sandbox keys are usually low enough risk to batch.

This is also the strongest practical argument for §6.5.

### 6.5 Prefer `keyway run` over `keyway pull` — as a team norm

Every `keyway pull` creates a durable plain-text copy that outlives the reason you made it. Every
`keyway run` does not. If the team's habit is `run`, then §6.4 step 2 shrinks from "rotate everything"
to "rotate what's actually exposed," and an offboarding stops being an emergency.

Pull when a tool genuinely cannot start without a file on disk. Otherwise, don't.

### 6.6 Never commit the `.env`, and prove it rather than trusting it

`.env` is already ignored in this repo — `.gitignore` carries `**/.env`. Confirm on any repo before
you trust it, rather than taking anyone's word (including this page's):

```bash
git check-ignore -v .env     # prints the rule that ignores it; silence + exit 1 means NOT ignored
```

Add `keyway scan` to CI so a leaked key fails the build rather than being discovered later:

```bash
keyway scan
keyway scan --json                  # machine-readable, for a pipeline
keyway scan --exclude node_modules  # exclude noisy directories
```

> ⚠️ **`-e` means something different on `scan`.** Everywhere else in this guide `-e` is `--env`
> (which environment). On `scan` alone, `-e` is `--exclude` (which directories to skip). So
> `keyway scan -e production` does **not** scan the production environment — it silently excludes any
> directory named `production` and reports clean. **Write `--exclude` in full on `scan`**, and never
> reach for `-e` there out of habit.

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

### 6.8 Doing it — the actual commands for changing and sharing access

Everything above says *what* the rules are. This is *how you carry them out*. Every command runs the
same on both sides.

These use the GitHub CLI, `gh`, which is already installed and authenticated on both sides. If you
would rather click than type, each one names the equivalent page in GitHub's web interface.

#### Who can read this vault right now?

Ask this before granting anything, and again before you rotate anything. It is the only honest
answer to "who has our keys" — and it is two questions, not one:

```bash
# 1. Who has accepted access
gh api repos/<owner>/<repo>/collaborators --jq '.[] | "\(.login) \(.role_name)"'

# 2. Who has been invited but has NOT accepted yet
gh api repos/<owner>/<repo>/invitations --jq '.[] | .invitee.login'
```

⛔ **Run both.** A pending invitation does **not** appear in the collaborator list, so checking only
the first gives you a clean-looking answer while somebody is one click away from full vault access.
An empty second list is the confirmation; skipping it is an assumption.

Web equivalent: **Settings → Collaborators and teams**, which shows both lists on one page.

#### Adding somebody

```bash
gh api --method PUT repos/<owner>/<repo>/collaborators/<username> -f permission=push
```

`permission` takes `pull` (read), `push` (read + write), or `admin`. **Give the least that lets them
do their job** — and understand what you are actually granting, which §2 stated and this makes
concrete: the GitHub role is the vault key. `push` on the repo is `read` on every secret in it.

They then run `keyway login` on their own machine and it works. You send them nothing.

Web equivalent: **Settings → Collaborators and teams → Add people**.

#### Changing what somebody can reach

There are **two separate levers**, and mixing them up is how access quietly drifts:

| Lever | Where | What it decides | Use it for |
|---|---|---|---|
| **GitHub role** | `gh api` above, or repo Settings | whether they are in **at all**, and for which repo | joining, leaving, read-vs-write |
| **Keyway environment role** | [app.keyway.sh](https://app.keyway.sh) | which **environments** an already-approved person may open | keeping `production` away from everyone but you |

The rule from §6.1 restated as a procedure: **membership decisions go on GitHub; scope decisions go
in the dashboard.** Never use the dashboard to grant somebody access GitHub did not, because then two
lists disagree and only one of them is the one you will remember to check.

To narrow someone from all-environments to development-only, you change the **dashboard** role — not
their GitHub permission. To remove them entirely, you change **GitHub** — see below.

#### Removing somebody — all three steps

```bash
# Step 1 - revoke future access
gh api --method DELETE repos/<owner>/<repo>/collaborators/<username>

# Step 1b - clear any per-environment role at app.keyway.sh (nothing to type; check, do not assume)

# Step 2 - find out what they could have taken
keyway diff development production --keys-only

# Step 3 - rotate every key from step 2: regenerate at the provider, then
keyway set <KEY> -e <env>
```

Step 2 is the one people skip, and it is what makes step 3 finishable rather than a vague dread.
`--keys-only` prints the **names** of every secret in each environment without printing a single
value, so it is safe to run on a shared screen and safe to paste into a checklist. That list *is*
your rotation worklist: anything on it, in an environment they could open, is now a credential of
unknown custody.

Repeat the whole sequence for **every repository they were on** — access is per repo, so removing
somebody from one leaves the others untouched.

> ### ⛔ Removal does not reach backwards, so step 3 is not optional
>
> §6.4 says this and it is worth saying twice in the place where the commands live. If they ever ran
> `keyway pull`, a plain-text `.env` is on their laptop right now. Step 1 stops the next read; it does
> nothing to the copy they already have. **Only rotation at the provider makes that copy worthless.**

#### One thing to confirm before trusting the model on a public repository

This guide's one-line summary is *"if you can push to the repo, you can read its secrets."* On a
**private** repository that is unambiguous, because only invited people can reach it at all.

On a **public** repository, read access is universal and push access is not — and those two things
being different is exactly the case the one-liner does not settle. Before putting any secret in a
public repository's vault, confirm with Keyway which of the two it actually gates on. Treat the
answer as unknown until you have it in writing from the vendor, rather than reasoning it out from
this page.

---

## 7. The dangerous flags — read once, remember forever

| Flag | What it does | Why it bites |
|---|---|---|
| `keyway push --prune` | Deletes vault secrets that are **not** in your local file | If your local `.env` is stale or partial, this **silently deletes** your teammates' keys from the vault. Push is additive *by default* for exactly this reason — `--prune` opts out of the safety. |
| `keyway sync --allow-delete` | Deletes secrets at the **provider** during a push | The `--prune` of the provider world, and worse-defaulted: `sync` defaults to **`-e production`** (see below), so the blast radius is live infrastructure. |
| `keyway sync` with no direction flag | `sync` is **bidirectional** | It is not "push to provider". `--push` sends vault → provider; `--pull` sends provider → **vault**, overwriting your secrets from Vercel/Railway. Name the direction every time. |
| `keyway pull --force` | Replaces your whole env file instead of merging | Blows away local-only overrides you forgot you had. |
| `keyway diff --show-values` | Prints real secret values | Fine alone at your desk. A disclosure on a screen-share. |
| `keyway set -l` | Writes to the local file instead of the vault (legacy) | Looks like it updated the vault. It did not. Your teammates get nothing. |
| `-y` / `--yes` | Skips the confirmation prompt | The prompt is the last thing standing between `--prune` and a bad afternoon. Do not pair them out of habit. |

> ⛔ **`keyway sync` is the one command that defaults to production.** Its `--help` reads
> `-e, --env string   Keyway environment (default: production)` — every other command here defaults to
> `development`. So a bare `keyway sync`, which the CLI's own examples encourage, operates on your
> **live** environment. Always name `-e` and the direction explicitly.

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

> ### ⛔ But `keyway push` will make that edit for you, unprompted.
>
> The warning above is advisory. **`keyway push` is not** — observed live on 0.5.3 in this repo: it
> printed `✓ Added .env* to .gitignore`, appended `.env*`, and created an empty `.env`, with no prompt
> and before any authentication. So "don't act on the warning" is not sufficient advice; the tool acts
> on it for you.
>
> **After your first `keyway push` in any repo, run `git diff .gitignore`** and revert the addition if
> you did not want it. A blanket `.env*` is broader than `**/.env` and would also ignore the tracked
> `.env.example` template this system ships.

---

## 9. When something is wrong — `keyway doctor` first

```bash
keyway doctor
```

Six checks: CLI version, authentication, GitHub repo detection, API connectivity, env-file presence,
and the ignore rules.

**On this repo, a fully set-up machine reads `5 passed, 1 warning, 0 failed`, and that is the healthy
state — not 6/6.** The one remaining warning is the `.gitignore` false positive from §8, which is
**permanent here** because Keyway cannot read the `**/` glob form and §8 forbids "fixing" it. Chasing
6/6 means editing `.gitignore`, which is the one action this page exists to prevent.

Before you have logged in on a machine you will see `4 passed, 2 warnings` — the extra warning is
*"Not logged in"*, and unlike the other one it is **real**: it means §4 has not been run **on this
machine** yet (§3's two-machine note). Do not learn to ignore that one.

| Symptom | Cause | Fix |
|---|---|---|
| `command not found: keyway` | Not installed on *this* machine | §3 |
| "Not logged in" after logging in elsewhere | Credentials are per-machine by design | `keyway login` here too |
| Teammate can't pull | They lack GitHub access, or never ran `keyway login` | Check the GitHub collaborator list first |
| Secrets missing after a colleague's push | Someone ran `--prune` against a stale file | **Regenerate at the provider**, then `keyway set <KEY>`. `set` prompts for a value — if the vault held the only copy, nobody has one to type, so treat this as the rotation in §6.4 step 3, not as an undo. |
| App can't see the variables | Ran the app directly rather than through Keyway | `keyway run -- <cmd>` |

Other commands that exist and are occasionally useful: `keyway logout` (clears stored credentials on
this machine), `keyway connect` / `keyway connections` / `keyway disconnect` / `keyway sync`
(**bidirectional** provider sync with Vercel or Railway — see the §7 warnings before using it), and
`keyway completion` (shell autocomplete).

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

### Why Keyway and not GCP Secret Manager or HashiCorp Vault

Recorded here because the question will be asked again, and because AGY already runs on GCP:

| Option | Why it was not chosen |
|---|---|
| **GCP Secret Manager** | Strong for *runtime* secrets a deployed service reads via IAM, and worth using there. But access is granted by GCP IAM, which is a **second identity system** to keep in step with GitHub, and there is no ergonomic "developer runs the app locally with the right `.env`" path — the daily loop this page exists for. |
| **HashiCorp Vault** | The most capable of the three and the most operational overhead: a server to run, seal/unseal to manage, policies to write. Disproportionate for a small team whose actual problem is "stop sending `.env` files to each other." |
| **Keyway** ✅ | The access list is **already** the GitHub repo, so there is no second identity system; `keyway run` gives a zero-disk local loop; setup is one install plus one `login` per machine. |

The trade accepted: a third-party hosted vault, and a smaller feature set than Vault. If runtime
secret management for deployed services becomes the problem, Secret Manager is the right tool for
*that* job and the two can coexist.

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
keyway set NEW_API_KEY               # add/rotate one secret, masked (never KEY=value)
keyway diff development production   # what differs
keyway scan                          # leak check  (--exclude, NOT -e, on this one)
keyway doctor                        # health check: 5 passed / 1 warning is healthy here

# --- occasionally ---
keyway pull                          # only when a tool needs a real file
keyway push -e development           # additive; always name -e, push has no default
git diff .gitignore                  # ⛔ after any first push: it edits .gitignore for you

# --- offboarding a teammate: ALL THREE steps ---
# 1. remove them from the GitHub repo/org
# 2. clear any per-environment role in the Keyway dashboard
# 3. rotate every secret they could have pulled  -> keyway set <KEY>
```

---

## Related

- `.agents/skills/keyway-secrets/SKILL.md` — the agent-facing version of this page.
- `docs/migrations/install_guides/machine_setup_card.md` — new-machine setup, including Keyway.
- `docs/_scc_sops_prds/workflows_testing_SOP.md` — the main operator quick reference.
- Vendor documentation: <https://docs.keyway.sh> · dashboard: <https://app.keyway.sh>
