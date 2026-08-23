# Jira access on a new machine — `acli` + the API token

**What this buys you:** every command in this system that touches the board — minting a ticket,
moving it, writing its description, closing it out — runs through `acli`, and `acli` needs one
credential. The **same** credential also unlocks the one thing `acli` cannot do: **uploading a file
to a ticket**. One token, stored once, read by both.

**Why it is a per-machine step.** The token lives in the machine's own credential store, never in a
repo file, never in a commit, never in chat. Git carries nothing here. A fresh clone on a fresh box
has **no board access at all**, and — like an unarmed `core.hooksPath` — *nothing announces it*: the
agent simply reports "I have no Jira integration", which is false, and every board write silently
stops happening.

> ⛔ **`acli` failing is a fact about your shell, not about the board.** A sandboxed tool call cannot
> reach the OS credential store, so `acli` fails there while working perfectly in the same repo
> unsandboxed. Re-run unsandboxed before concluding anything. Full rule: `.agents/rules/jira.md`.

---

## 0 · Do I need this?

| Situation | Do this? |
|---|---|
| **Fresh machine / fresh clone** | **Yes — all of §1–§5.** Nothing on the board works until you do. |
| **`acli jira auth status` already says ✓ Authenticated** | **§2–§3 only.** You have board access but probably *not* a re-readable token — see the box in §3. |
| **You only read the board, never attach files** | §1–§4 is enough. §5 is the attachment half. |

---

## 1 · Install `acli`

| OS | Command |
|---|---|
| **macOS** | `brew tap atlassian/acli` then `brew install acli` |
| **Windows** | the MSI / `winget` package from Atlassian's installer page |
| **any** | official instructions: https://developer.atlassian.com/cloud/acli/guides/install-acli/ |

Confirm it answers, and note the version — §5's limits are version-dependent:

```bash
acli --version
```

⛔ **Do not bake the binary's path into anything.** It differs per machine (`/opt/homebrew/bin/acli`
here, elsewhere entirely on the PC). Every script probes for it; a hardcoded Mac path is exactly what
teaches a Windows agent it has no Jira.

---

## 2 · Create ONE API token

An Atlassian API token is a password you generate **for programs instead of people**. You make it
once, in a browser, and it is the only step in this guide a human must do — nothing can generate it
for you.

1. Go to **https://id.atlassian.com/manage-profile/security/api-tokens**
2. **Create API token** → label it `sudo-jira` → choose the longest expiry offered
3. **Copy it**, and leave the tab open until §3 is finished

⛔ **Atlassian shows the token exactly once.** Close that tab early and the only remedy is to make
another one.

⛔ **Take the plain, unscoped token** ("Create API token"), not the scoped variant. Basic auth — what
both `acli` and the REST calls use — expects the unscoped kind.

**Write the expiry date on the board** (a comment on the setup ticket is enough). A token that
expires silently looks exactly like a broken script six months from now.

---

## 3 · Store it in the machine's credential store

**The item name is `sudo-jira` on every machine.** That is the one thing here that does *not* vary —
scripts look the token up by that name, so a machine that calls it something else has a token nothing
can find. The *store* differs per OS; the *name* is a contract.

### macOS

Copy the token to the clipboard first (§2 step 3), then:

```bash
security add-generic-password -U -a "<your-atlassian-email>" -s sudo-jira -w "$(pbpaste)"
```

`-U` means "update if it already exists" — without it the store refuses a second write, and you get
to keep the broken value. **Clear the clipboard afterwards** (`pbcopy </dev/null`).

> ⛔ **DO NOT use the interactive prompt form — `-w` with no value. It silently truncates.**
> Measured here 2026-08-22: a pasted token came back out of the keychain at **exactly 128
> characters** and returned **401**. 128 is the prompt's fixed buffer, and an Atlassian token is
> longer than that. The keychain itself is innocent — storing a 200-character value through `-w
> <value>` reads back at 200. **The prompt is the thing that loses your token, it says nothing while
> doing it, and a truncated token fails exactly like a wrong one.**

**Why `$(pbpaste)` and not the token typed out.** Your shell history records the command *text* —
`-w "$(pbpaste)"` — never what it expanded to, so nothing is written to disk. The expanded value does
sit in the process's arguments for the few milliseconds the command runs, which is visible to other
users on a shared box; on a single-user machine that is the right trade against a prompt that
corrupts the value outright.

**Check what actually landed before trusting it:**

```bash
T=$(security find-generic-password -s sudo-jira -a "<your-atlassian-email>" -w); echo "${#T} chars"; unset T
```

**Under ~150 characters means truncated** — redo it from the clipboard. Never paste the token into a
terminal prompt again once you know this.

### Windows

```powershell
# once per machine, if the module is not already there
Install-Module Microsoft.PowerShell.SecretManagement, Microsoft.PowerShell.SecretStore -Scope CurrentUser
Register-SecretVault -Name SudoStore -ModuleName Microsoft.PowerShell.SecretStore -DefaultVault

Set-Secret -Name sudo-jira        # prompts; paste the token
```

**No-install fallback, one session only:** `$env:JIRA_API_TOKEN = '<paste>'`. Helpers check the
environment variable first, then the store — so this works, but it dies with the window.

> ⚠️ **Already authenticated to `acli`, and think you can skip this?** You can't. `acli` stores its
> own **wrapped** copy under its own service name, keyed to an internal account id. Measured
> 2026-08-22: feeding that stored value to `/rest/api/3/myself` as basic auth returns **401**. It
> works from inside `acli` and nowhere else. The token you store here is the *original*, and it is
> what every other consumer reads.

---

## 4 · Point `acli` at the stored token

`acli jira auth login --token` reads from **standard input**, so the token goes store → CLI without
ever appearing on a command line, in history, or on screen:

```bash
EMAIL="<your-atlassian-email>"
security find-generic-password -s sudo-jira -a "$EMAIL" -w \
  | acli jira auth login --site "sudo-command.atlassian.net" --email "$EMAIL" --token
```

```powershell
# Windows
$EMAIL = "<your-atlassian-email>"
Get-Secret -Name sudo-jira -AsPlainText | acli jira auth login --site "sudo-command.atlassian.net" --email $EMAIL --token
```

`acli jira auth login --web` (browser OAuth) also works and skips the token — but then §5 has nothing
to read, so you would still do §2–§3. One token for both is the point.

**Check it:**

```bash
acli jira auth status      # expect: ✓ Authenticated + site + email + api_token
```

That command is also how you recover the account email on a machine that already works — read it from
there rather than typing it from memory. **It is the email you sign in to Atlassian with, which is
not necessarily the email git commits under.**

---

## 5 · Verify the token itself — without ever printing it

`acli` working proves the CLI half. This proves the REST half, which is what attachments use:

```bash
EMAIL=$(acli jira auth status | awk '/Email:/{print $2}')
TOKEN=$(security find-generic-password -s sudo-jira -a "$EMAIL" -w)
printf 'user = "%s:%s"\n' "$EMAIL" "$TOKEN" \
  | curl -s -K - -H "Accept: application/json" \
      "https://sudo-command.atlassian.net/rest/api/3/myself" \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print("OK:", d.get("displayName"), d.get("emailAddress"))'
unset TOKEN
```

Expect one `OK: …` line.

**A 401 on a token you just created is almost always truncation, not a wrong token** — check its
length first (§3), before you go hunting the email or re-issuing. Other causes, in order of
likelihood: paired with the wrong email (the *Atlassian* account email, which need not be your git
email), expired, revoked.

⛔ **Note what that snippet does NOT do: put the token in `-u user:token`.** Command-line arguments
are visible to any process listing while the call is in flight. Piping a curl config on stdin
(`-K -`) keeps it out of `argv` entirely. Use this shape anywhere you hand the token to a program.

---

## 6 · What the token unlocks that `acli` cannot do

**Uploading an attachment.** Measured on **acli 1.3.22-stable, 2026-08-22**:

```
acli jira workitem attachment  →  list | delete      (no add, no upload)
```

So a ticket gets its plan file the only way there is — the REST endpoint, with the stored token:

```
POST https://sudo-command.atlassian.net/rest/api/3/issue/<KEY>/attachments
     header    X-Atlassian-Token: no-check      <- required; the call 403s without it
     body      multipart form field named "file"
     auth      basic, <atlassian-email>:<api-token>
```

**Re-check this after upgrading `acli`.** If a later version grows an `add` verb, the token stops
being required for attachments — but stays required for anything else calling REST directly.

**Everything else needs nothing beyond §4.** Reading the board, minting tickets, editing
descriptions, transitioning statuses, JQL — all of that is `acli`, and it is already working.

---

## 7 · Rotate, revoke, expire

| When | Do |
|---|---|
| **Token expired** or you want a fresh one | §2 again, then §3 **with `-U`**, then §4 again — `acli`'s wrapped copy does *not* update itself |
| **Machine lost or shared by mistake** | Revoke it at https://id.atlassian.com/manage-profile/security/api-tokens — takes effect immediately, everywhere |
| **New machine** | New token. Do **not** carry one machine's token to another; revoking then costs you both |

---

## 8 · Security rules (non-negotiable)

- **The token is password-equivalent for the whole Atlassian account** — full read/write across Jira
  and Confluence, and it is *not* scoped down. Treat it exactly like the contents of `_secrets/`.
- **Never** commit it, paste it into a chat or an agent transcript, screenshot it, or write it to a
  file in any repo. It belongs in the OS credential store and nowhere else.
- **Never echo it.** Read it into a variable at the moment of use and `unset` it after. Print key
  *names*, never values — the same rule the `.env` bundle lives under.
- **An agent must never ask you to paste the token to it.** If one does, that is a bug: the correct
  ask is always "run §3 yourself, then tell me it's done."

---

## What has actually been run

Same convention as the rest of this kit: an unticked row is **untested**, not "fine".

| Step | Status |
|---|---|
| §1 install (macOS, `brew tap atlassian/acli`) | ✅ verified on the Mac 2026-08-22 — `/opt/homebrew/bin/acli` → `1.3.22-stable` |
| §1 install (Windows) | ⛔ **not run** — path and package manager unverified from here |
| §3 macOS store | ✅ **run 2026-08-22, and it is why the ⛔ box exists** — the interactive `-w` prompt truncated a real token to 128 chars; `-w "$(pbpaste)"` round-trips a 200-char value intact |
| §3 Windows `Set-Secret` | ⛔ **not run** |
| §4 `acli` login + `auth status` | ✅ verified on the Mac 2026-08-22 — ✓ Authenticated, `api_token` |
| §5 REST verify | ⚠️ **only failure paths measured so far** — `acli`'s own stored credential returns 401 (which is why §3 exists), and so does a prompt-truncated token. The success path is still unproven on this machine |
| §6 attachment limits | ✅ measured on 1.3.22-stable 2026-08-22 — `list` / `delete` only |

## Related

- `.agents/rules/jira.md` — how agents actually use the board once this is done: the command
  cheat-sheet, the per-board status tables, the guardrails on who may move a ticket
- [`new_machine-migration-guide.md`](new_machine-migration-guide.md) §5 — the other per-machine
  logins that the secrets bundle cannot carry (gcloud, gh, firebase, Java, Node)
