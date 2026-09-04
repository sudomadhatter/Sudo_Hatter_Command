# Keyway — per-machine setup, and sharing access with the team

> **What this is.** Getting Keyway working on **this** machine, and granting or revoking somebody
> else's access to the vaults. Step **6c** of the [migrations kit](../INDEX.md).
>
> **What this is not.** The daily-use guide and the team discipline behind it —
> [`sharing_keys_secrets_secure.md`](../../_scc_sops_prds/sharing_keys_secrets_secure.md). Read that
> once; come back here per machine.

**Keyway is an encrypted cloud vault for environment variables, and your GitHub account is the key.**
If you can push to a repo, you can read its secrets. Nobody is ever sent a `.env` file again.

---

## ⛔ Why this step has its own page

Every other item in §3 of the [60-second card](machine_setup_card.md) fails loudly. This one does not.

**Install and login are two separate acts, and only the first is obvious.** Credentials live in the
OS keyring — Windows Credential Manager, macOS Keychain — which is per-machine *by definition*. So a
machine can have the CLI on its `PATH`, answer `keyway --version` correctly, and still be unable to
read a single secret. Nothing about that state looks wrong until something needs a key.

That is not hypothetical. **SCC-150 ("Install and verify Keyway CLI on Main PC") was marked `Done`
while that machine had never run `keyway login`.** The install happened; the login did not; there was
no stated success condition, so there was nothing to check the ticket against.

**Hence the rule this page exists to enforce: the step is finished when `keyway doctor` says so, not
when a command has been typed.**

---

## 1. Install — once per machine

| | Command |
|---|---|
| **Windows** | `npm install -g @keywaysh/cli` |
| **macOS** | `brew install keywaysh/tap/keyway` |

macOS gets a native Go binary (faster start, no Node dependency); Windows goes through npm. Either
way, confirm the CLI is on `PATH`:

```bash
keyway --version          # -> keyway version 0.5.3
```

## 2. Log in — once per machine

```bash
keyway login
```

This runs a **GitHub device flow**: it prints a short code and a URL, and waits for you to approve it
in a browser.

> ⚠️ **A human has to be present for this one.** The command blocks until somebody approves the code,
> and the code expires after a few minutes. It cannot be completed by a script, a CI job, or an agent
> working unattended — if you are setting up a machine remotely, this is the step that needs you.

`keyway login` stores its session token in the OS keyring, not in a dotfile, so there is nothing to
accidentally commit and nothing to sync to a backup.

## 3. Verify — **this is the step, not an optional extra**

```bash
keyway doctor
```

Read the count, not the individual lines:

| What it says | What it means |
|---|---|
| `4 passed, 2 warnings` | ⛔ **Not set up.** One of those warnings is *"Not logged in"* — go back to step 2 |
| **`5 passed, 1 warning`** | ✅ **Correct and finished.** This is the healthy state |
| `6 passed, 0 warnings` | Not achievable here — see below |

**The permanent warning is `.gitignore: Missing .env patterns`, and it is wrong.** Keyway's doctor
does naive literal string matching and cannot read the recursive glob form. This repo ignores `.env`
via `**/.env`, which is both correct and broader than the literal it looks for. Ask git itself:

```bash
git check-ignore -v .env       # -> .gitignore:44:**/.env   .env
```

⛔ **Never "fix" `.gitignore` to chase 6/6.** These ignore rules are deliberately chosen and
commented, and a blanket `.env*` would also swallow the tracked `.env.example` template.

## 4. Per repo — already done for ours

```bash
keyway init          # links a repo to its vault; run from the repo root
```

`keyway init` is a **one-time, one-person** act per repository — it needs write access to the GitHub
repo, because creating a vault is administrative. **The repos in this system are already initialised**,
so on a new machine you do not run it. Log in, and every vault you have access to is readable.

Confirm a vault resolves without printing a single value:

```bash
keyway diff development production --keys-only
```

## 5. Use it — always name `-e`

```bash
keyway run -e development -- npm run dev
keyway run -e development -- python backend/main.py
```

`keyway run` injects secrets **into memory only** — nothing is written to disk, so nothing can be
committed, backed up, indexed, or read by an agent with filesystem access. Prefer it over
`keyway pull`, which writes a real `.env`.

> ### ⛔ Without `-e`, `run` and `pull` stop and wait for a human
>
> The bare form does **not** quietly default to `development`. It draws an interactive menu and
> blocks until a key is pressed:
>
> ```
> ┃ Environment:
> ┃ > development
> ┃   staging
> ┃   production
> ```
>
> At your own terminal, a mild surprise. In CI, a `cron` job, a script, or an agent, it is a hang with
> no error and nothing in the log — the run burns its entire timeout waiting for an answer nobody is
> there to give. **Name `-e` on every invocation.** A documented default decides which entry is
> *pre-selected in the menu*, not whether the menu appears.

Two more that bite, in full in the [main guide](../../_scc_sops_prds/sharing_keys_secrets_secure.md) §7:
`keyway push` edits `.gitignore` unprompted on first run (`git diff .gitignore` afterwards), and on
`scan` alone `-e` means `--exclude`, not `--env`.

---

## 6. Sharing access — adding, changing, and removing people

**Access is granted on GitHub, never inside Keyway.** Keyway reads your GitHub identity to decide
what you may open, which is deliberate: two access lists always drift, and the drift stays invisible
until somebody who left still holds a live key.

These use `gh`, the GitHub CLI, which step 6 of the kit already installs and authenticates.

### Who can read this vault right now?

Ask before granting anything, and again before rotating anything. It is **two questions, not one**:

```bash
gh api repos/<owner>/<repo>/collaborators --jq '.[] | "\(.login) \(.role_name)"'
gh api repos/<owner>/<repo>/invitations   --jq '.[] | .invitee.login'
```

⛔ **Run both.** A pending invitation does not appear in the collaborator list — check only the first
and you get a clean-looking answer while somebody sits one click from full vault access.

Web equivalent: **Settings → Collaborators and teams**, which shows both on one page.

### Adding somebody

```bash
gh api --method PUT repos/<owner>/<repo>/collaborators/<username> -f permission=push
```

`permission` takes `pull` (read), `push` (read + write), or `admin`. **Grant the least that lets them
work**, and be clear about what you are handing over: the GitHub role *is* the vault key. `push` on
the repo is read on every secret in it.

They then run `keyway login` on their own machine and it works. You send them nothing — no file, no
link, no password. Nothing exists to leak.

### Changing what somebody reaches — two levers, kept apart

| Lever | Where | Decides | Use for |
|---|---|---|---|
| **GitHub role** | `gh api` above, or repo Settings | whether they are in **at all**, per repo | joining, leaving, read vs write |
| **Keyway environment role** | [app.keyway.sh](https://app.keyway.sh) | which **environments** an approved person may open | keeping `production` to the smallest possible number of people |

**Membership decisions go on GitHub; scope decisions go in the dashboard.** Never use the dashboard to
grant access GitHub did not — that is how two lists start disagreeing, and only one of them is the one
you will remember to check.

To narrow somebody to development-only, change their **dashboard** role. To remove them, change
**GitHub**.

### Removing somebody — all three steps

```bash
# 1. revoke future access
gh api --method DELETE repos/<owner>/<repo>/collaborators/<username>

# 1b. clear any per-environment role at app.keyway.sh  (check, do not assume)

# 2. find out what they could have taken
keyway diff development production --keys-only

# 3. rotate each key from step 2: regenerate at the provider, then
keyway set <KEY> -e <env>
```

Step 2 is the one people skip, and it is what makes step 3 finishable instead of a vague dread.
`--keys-only` prints secret **names** and no values, so it is safe on a shared screen and safe to
paste into a checklist. That list *is* the rotation worklist.

Repeat for **every repository they were on** — access is per repo.

> ### ⛔ Revocation does not reach backwards
>
> If they ever ran `keyway pull`, a plain-text `.env` is on their laptop right now, and cutting their
> GitHub access does nothing to it. Step 1 stops the next read; only rotation at the provider makes
> the copy they already hold worthless. **Skipping step 3 is the most common way a vault-based setup
> still gets breached** — and it is the strongest argument for making `keyway run` the team default,
> since secrets that never touch disk leave nothing to rotate.

### One thing to confirm before trusting the model on a public repository

The one-line rule is *"if you can push to the repo, you can read its secrets."* On a **private** repo
that is unambiguous. On a **public** one, read access is universal and push access is not — precisely
the case the one-liner does not settle. Before putting any secret in a public repository's vault,
confirm with Keyway which of the two it gates on, and treat the answer as unknown until you have it in
writing from the vendor.

---

## When something is wrong

| Symptom | Cause | Fix |
|---|---|---|
| `command not found: keyway` | not installed on **this** machine | §1 |
| "Not logged in" after logging in elsewhere | credentials are per-machine by design | `keyway login` here too |
| Command hangs forever, no output | no `-e`, and the environment menu is waiting | name `-e` — §5 |
| `.gitignore` warning that will not clear | known false positive | leave it — §3 |
| Teammate cannot pull | no GitHub access, or never ran `keyway login` | check the collaborator list first — §6 |
| App cannot see the variables | ran directly instead of through Keyway | `keyway run -e <env> -- <cmd>` |

## Related

- [`sharing_keys_secrets_secure.md`](../../_scc_sops_prds/sharing_keys_secrets_secure.md) — daily use, team discipline, the full dangerous-flags table
- [`../INDEX.md`](../INDEX.md) — the full ordered path for a new machine
- [`machine_setup_card.md`](machine_setup_card.md) — the 60-second version
- `.agents/skills/keyway-secrets/SKILL.md` — the agent-facing version of the same material
