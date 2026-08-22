---
name: keyway-secrets
description: Cross-platform secrets management and team environment variable sharing using Keyway (keyway CLI). Covers Mac & Windows installation, vault initialization, pulling/pushing .env files, zero-disk in-memory execution (keyway run), and team sharing via GitHub OAuth and Keyway Organizations.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Keyway Secrets Management & Team Sharing

> **Cross-platform secrets synchronization and team sharing via GitHub-backed encrypted vaults.**
> Native macOS Keychain and Windows Credential Manager integration with zero plain-text leaks.

---

## 🎯 When to Use This Skill

- Setting up or syncing `.env` files across machines (**PC ↔ Mac**).
- Sharing environment variables and secrets securely with **team members** without sending raw `.env` files.
- Running applications with secrets injected **directly into RAM** (`keyway run`) without creating plain-text files on disk that AI agents or scripts could leak.
- Scanning repositories for accidentally committed API keys and credentials (`keyway scan`).
- Rotating individual secrets in development, staging, or production (`keyway set`).

---

## 📦 1. Installation by Platform

### 🍎 macOS (Recommended: Homebrew)
Homebrew provides a native Go binary with fast startup (~10x faster than Node) and zero dependencies:
```bash
brew install keywaysh/tap/keyway
```

**Alternative (Direct Shell Script):**
```bash
curl -fsSL https://keyway.sh/install.sh | sh
# Installs binary to /usr/local/bin/keyway
```

**Alternative (npm):**
```bash
npm install -g @keywaysh/cli
```

---

### 🪟 Windows (Recommended: Global npm)
```powershell
npm install -g @keywaysh/cli
```

**Alternative (Manual Executable):**
1. Download `keyway-win-x64.exe` from [GitHub Releases](https://github.com/keywaysh/cli/releases/latest).
2. Rename to `keyway.exe` and place in a directory on your system `PATH` (e.g. `C:\Program Files\Keyway\`).

---

### 🔍 Verify Installation (Both Platforms)
```bash
keyway --version
# Expected output: keyway version 0.5.x

keyway doctor
# Checks CLI version, auth state, GitHub repo detection, API connectivity,
# env file presence and .gitignore rules. Run this FIRST whenever anything is wrong.
```

> [!WARNING]
> **`keyway doctor`'s `.gitignore` check is a known false positive in this system.** It does naive
> literal matching and cannot read the recursive glob form, so it reports *"Missing .env patterns"*
> against a `.gitignore` that ignores `.env` via `**/.env`. **Never edit `.gitignore` on the strength
> of that warning** — verify with `git check-ignore -v .env`, which is git itself answering, and
> which prints the exact rule and line number when the file IS ignored.

> [!NOTE]
> **Installation and login are per-machine.** This system runs on a Mac and a PC; credentials live in
> the OS keyring, so they cannot travel. A machine that has never run `keyway login` is not logged in,
> regardless of what the other machine has done.

---

## 🔐 2. Authentication & Vault Setup

### Step 1: Login via GitHub OAuth
```bash
keyway login
```
- Opens your default web browser for GitHub OAuth authentication.
- Cryptographic session tokens are stored securely in the system keyring (**macOS Keychain** on Mac, **Windows Credential Manager** on PC).

### Step 2: Initialize Repository Vault
In the root of your project repository (e.g. `Sudo_Hatter_Command` or `Projects/AGY_AVIATIONCHAT`):
```bash
keyway init
```
- Links the local repository to its cloud-encrypted vault on Keyway.
- Requires admin/write access to the GitHub repository.

---

## 🚀 3. Pushing & Pulling Secrets

### Pushing Secrets to the Vault
```bash
# Push local .env to the 'development' environment (default):
keyway push

# Push to a specific environment (e.g. production, staging):
keyway push -e production

# Push a custom file:
keyway push -f .env.production -e production

# Prune mode (removes vault secrets that are missing in your local file):
keyway push --prune
```
> [!NOTE]
> `keyway push` is **additive by default**. Existing secrets in the vault that are not in your local file are safely preserved unless `--prune` is explicitly passed.

### Pulling Secrets to Local Disk
```bash
# Pull 'development' secrets into your local .env:
keyway pull

# Pull 'production' secrets into a specific file:
keyway pull -e production -f .env.production
```

---

## ⚡ 4. Advanced Operations & Best Practices

### A. Zero-Disk In-Memory Execution (`keyway run`)
The most secure method for running applications locally, in CI/CD, or with AI coding agents:
```bash
# Run web frontend (Node/Next.js):
keyway run -- npm run dev

# Run Python backend:
keyway run -- python backend/main.py

# Run specific environment:
keyway run -e production -- ./deploy.sh
```
- **How it works:** Keyway fetches secrets directly from the vault into process memory (RAM).
- **Security:** No `.env` file is written to disk, preventing AI agents, watchers, or malware from reading raw secrets.

### B. Single Secret Updates (`keyway set`)
Quickly add or rotate a single secret without modifying `.env` files:
```bash
# Interactive masked input:
keyway set STRIPE_SECRET_KEY

# Direct key-value assignment:
keyway set OPENAI_API_KEY=sk_live_123456789

# Set for specific environment:
keyway set DATABASE_URL="postgresql://..." -e production
```

### C. Environment Diffing (`keyway diff`)
Compare variable keys between environments:
```bash
keyway diff development production
# With values shown (use with caution):
keyway diff development production --show-values
```

### D. Leak Scanning (`keyway scan`)
Audit your codebase for accidentally committed secrets:
```bash
keyway scan
keyway scan ./backend
keyway scan --json                 # machine-readable, for CI
keyway scan -e node_modules        # exclude noisy directories
keyway scan --show-all             # include probable false positives
```

### E. Provider Sync (`keyway connect` / `sync`) — ⛔ bidirectional, production-default
```bash
keyway connect vercel              # or: railway
keyway connections                 # list what is connected
keyway sync vercel --push -e development   # vault -> provider; name BOTH explicitly
keyway disconnect vercel
keyway logout                      # clear stored credentials on this machine
```

> [!WARNING]
> **Three traps, all verified against 0.5.3's `--help`:**
> 1. **`sync` is bidirectional.** `--push` sends vault → provider; `--pull` sends provider → **vault**,
>    overwriting your secrets. With neither flag the direction is not stated by the CLI — never rely on it.
> 2. **`sync` defaults to `-e production`** (`default: production`), while `pull`, `run` and `set` all
>    default to `development`. It is the ONE command whose bare form touches live infrastructure.
> 3. **With no provider argument it prompts interactively** — so a bare `keyway sync` blocks forever in
>    a headless or agent context.

### F. ⛔ Destructive Flags — Verified Against 0.5.3
| Flag | Effect | Hazard |
|---|---|---|
| `keyway push` (any) | **Writes to `.gitignore` and creates `.env`** | ⛔ Observed live, unprompted, before auth: prints `✓ Added .env* to .gitignore` and appends `.env*`. Always `git diff .gitignore` after a first push. A blanket `.env*` also swallows the tracked `.env.example`. |
| `keyway push --prune` | Deletes vault secrets absent from the local file | A stale or partial local `.env` **silently deletes teammates' keys**. Push is additive by default precisely so this must be opted into. |
| `keyway sync --allow-delete` | Deletes secrets at the **provider** | The `--prune` of the provider world, on a command that defaults to `production`. |
| `keyway scan -e <x>` | On `scan`, `-e` is `--exclude`, **not** `--env` | `keyway scan -e production` excludes a directory named `production` and reports clean — a leak check that exits 0 for the wrong reason. Write `--exclude` in full. |
| `keyway pull --force` | Replaces the whole env file instead of merging | Destroys local-only overrides. |
| `keyway set -l` | Writes to the local file, **not** the vault (legacy) | Looks like a vault update. It is not — teammates receive nothing. |
| `keyway diff --show-values` | Prints live secret values | A disclosure on any shared screen or recording. |
| `-y` / `--yes` | Skips the confirmation prompt | The prompt is the last guard before `--prune`. Never pair them reflexively. |

---

## 👥 5. Team Sharing & Access Control

Keyway uses **GitHub as the single source of truth** for team access:

```
GitHub Repository / Organization
         │
         ├── Add Collaborator / Team Member on GitHub
         │
         ▼
Keyway Cloud Vault (Automatic Sync)
         │
         ├── Developer runs: `keyway login`
         ├── Developer navigates to repo clone
         └── Developer runs: `keyway pull` or `keyway run -- npm start`
```

### How to Share with Your Team:
1. **GitHub Permissions**:
   - Add your teammate as a collaborator on the GitHub repository or organization.
   - Keyway automatically detects their access upon login.
2. **Teammate Onboarding**:
   - The teammate clones the repo.
   - Installs CLI (`brew install keywaysh/tap/keyway` on Mac, `npm install -g @keywaysh/cli` on Windows).
   - Runs `keyway login` and `keyway pull` (or `keyway run`).
3. **Revoking Access — this is TWO steps, and the second is the one that gets skipped**:
   - **Step 1 — revoke.** Removing a user from the GitHub repository or organization instantly ends
     their ability to pull secrets or decrypt the vault.
   - **Step 1b — clear their Keyway dashboard role.** If per-environment RBAC (item 4) was used, the
     role assignment lives outside GitHub. Check it rather than assuming removal covered it.
   - **Step 2 — rotate.** ⛔ **Revocation does not reach backwards.** If they ever ran `keyway pull`,
     a plain-text `.env` is still on their laptop and cutting GitHub access does nothing to it.
     Regenerate every credential they could have pulled at the provider, then `keyway set <KEY>` to
     put the new value in the vault. Production first, then staging.
   - Doing step 1 alone is the most common way a vault-based setup still gets breached. It is also
     the strongest reason to make `keyway run` the team default over `keyway pull` — secrets that
     never touched disk leave nothing to rotate.
4. **Keyway Organizations (Web Dashboard)**:
   - Visit [app.keyway.sh](https://app.keyway.sh) to configure granular Role-Based Access Control (RBAC), restricting `production` vault access to senior leads while granting `development` access to all developers.

---

## 🔄 6. Keyway vs. Master Migrator (`env_master.py`)

| Feature | Keyway (`keyway`) | Master Migrator (`env_master.py`) |
|---|---|---|
| **Primary Role** | Live cloud synchronization & team sharing | Cold offline backup & fresh machine disaster recovery |
| **Network** | Requires internet & GitHub auth | 100% offline & local filesystem |
| **Scope** | Repository `.env` variables | Multi-project bundle (`.env`, `auth_keys/`, GCP service accounts) |
| **Execution** | Supports in-memory RAM execution (`keyway run`) | Restores files directly to workspace hierarchy |
| **Revocable** | **Yes** — remove GitHub access (then rotate, §5.3) | No — it is a file copy |

---

## 📖 7. The Operator Guide

The human-facing version of this page — install → auth → daily loop → **correct team usage** →
failure modes, written for the operator rather than for an agent — is
`docs/_scc_sops_prds/sharing_keys_secrets_secure.md`. Point the operator there rather than restating it.
