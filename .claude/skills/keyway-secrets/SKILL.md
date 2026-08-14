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
```

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
```

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
3. **Revoking Access**:
   - Removing a user from the GitHub repository or organization instantly revokes their ability to pull secrets or decrypt the vault.
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
