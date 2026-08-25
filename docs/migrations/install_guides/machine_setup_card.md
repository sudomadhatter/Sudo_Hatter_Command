# New machine — the 60-second card

> **What this is.** The short list for getting a machine (Mac or PC) from "repo cloned" to "safe to
> work in." Full setup — secrets, venvs, toolchains — is the
> [migrations kit](../INDEX.md); start there for a *fresh* box. **This card is the part
> people skip**, because nothing visibly breaks when you skip it.

---

## 1. Arm the commit gates — **one command, do it first**

```bash
# Run the automated installer (arms lobby + projects and verifies all gates):
powershell -File docs/migrations/scripts/Install-GitHooks.ps1   # Windows
bash docs/migrations/scripts/install-git-hooks.sh             # Mac

# Or arm one repo by hand:
python3 docs/migrations/scripts/arm_hooks_include.py .   # PC: python

# NEVER `git config core.hooksPath .githooks` — see below.
```

**Why this is first.** Every gate we have — the Jira key check, the encoding check, and the
SOP-currency check — is switched on by git's `core.hooksPath`. That setting is **local: it does not
travel with a clone.** Unset, git looks in `.git/hooks`, finds an empty folder, and **every gate is
off while the repo looks completely normal.** No warning, nothing in `git status`. You find out weeks
later from a Jira board with holes in it.

Set **globally with a relative value** (or via the installer above), and git resolves it against each
repo's *own* root — so one command arms the lobby, every project, and every repo you clone in future,
and does nothing at all in repos that have no `.githooks/`.

**Prove it works** (a rejected commit is a no-op — your files are untouched):

```bash
git checkout -b tmp/gate-check
git commit --allow-empty -m "no key here"     # must be REJECTED
git commit --allow-empty -m "SCC-1 probe"     # must be accepted
git checkout - && git branch -D tmp/gate-check
```

If the first one succeeds, the gates are **not** armed — re-run the config command.

---

## 2. Know which Python this box answers to

| Machine | The name that exists |
|---|---|
| **Mac** | **only `python3`** — no bare `python`, not even in your own shell |
| **PC** (python.org install) | **only `python`** — `py` also works as the launcher |

Docs are written `python3`; **on the PC, drop the `3`.** Nothing to install, nothing to alias — the
hooks probe `python3 → python → py` themselves, so the gates work on either box untouched. This
only affects commands *you* type.

Smoke-test the toolkit:

```bash
python3 .agents/scripts/tests/run_all.py     # PC: python .agents/scripts/tests/run_all.py
# expect: 6/6 files passed   (124 checks, ~10 s)
```

---

## 3. Restore the things git deliberately doesn't carry

| | Where it comes from |
|---|---|
| `.env` · `auth_keys/` · service accounts | The master bundle (`docs/migrations/auth_keys/_secrets/master.env`) → restore via `python docs/migrations/scripts/env_master.py --restore` (or `Restore-EnvMaster.ps1` / `restore-env-master.sh`). Gitignored. |
| Python venvs | Rebuilt per project — never cloned. AGY's is `backend/.venv` on **3.11**; follow the companion guide, don't wing it. |
| CLI logins | `acli`, `gcloud`, `gh`, `firebase`, `keyway` — each is a per-machine login. **Two of them have their own page, because both can look installed while being unusable:** `acli` is the whole Jira integration, and with no credential an agent reports "no Jira integration" and silently stops writing the board — [`jira-api-token-setup.md`](jira-api-token-setup.md), one token, also the only way to attach a file. **`keyway` is the live secrets vault, and its install and its login are separate acts** — [`keyway-setup.md`](keyway-setup.md), which also covers adding and removing teammates. Verify it with `keyway doctor`: `5 passed, 1 warning` is the finished state. `gcloud`, `gh` and `firebase` are ordinary logins. |
| Shell env (Mac) | Anything a *script* needs goes in `~/.zshenv`, **not** `.zshrc` — `.zshrc` is read only by interactive shells, so agents and hooks can't see it. |

---

## 4. Then pick the work back up

```
/cicd-resume                 # pulls everything down, rebuilds your working setup
/cicd-boot-sprint-memory     # loads the sprint, tells you the next move
```

---

> **The one idea behind all of this:** git moves *branches and files*. It does not move your git
> **settings**, your **environment**, or your **secrets**. Everything on this card lives outside the
> repo, which is exactly why it's invisible — and why "works on the desktop, not the Mac" is almost
> always one of these four rather than a bug in the code.
