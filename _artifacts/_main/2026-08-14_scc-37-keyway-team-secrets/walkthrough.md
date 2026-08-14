# Walkthrough — SCC-37: secure secrets sharing (Keyway) + the operator guide

**Branch:** `chore/SCC-37-keyway-team-secrets` · **Date:** 2026-08-14

---

## 1. Task Checklist

- [x] Install and verify Keyway on the Mac (it was PC-only)
- [x] Ground-truth the SCC-152 skill against the live 0.5.3 binary
- [x] Author the operator guide `docs/_scc_sops_prds/sharing_keys_secrets_secure.md`
- [x] Satisfy the folder's three-edit manifest contract (file + INDEX row + `EXPECTED`)
- [x] Correct and extend `.agents/skills/keyway-secrets/SKILL.md`; mirror to the Claude door
- [x] Prove the manifest contract actually binds the new doc (mutation)
- [x] Full enforcement suite green
- [ ] **`keyway login` + `keyway init`** — left to the operator, see §5

## 2. What Was Built

**The guide — `docs/_scc_sops_prds/sharing_keys_secrets_secure.md`.** Eleven sections: why `.env`
handoff fails, the three-part access model, per-platform install, one-time setup, the daily command
set, **correct team usage**, the destructive flags, the verified false alarm, `doctor`-first
troubleshooting, Keyway vs. the offline migration kit, and a copy-paste quick-reference card.

The team section is the substance of the request and carries four rules:
- GitHub repo access **is** the access-control list — there is never a second list to drift.
- Environments are a permission boundary, not labels; a developer should be able to work all day
  without ever holding a production credential.
- **Offboarding is revoke *then* rotate.** Cutting GitHub access stops future reads but cannot
  un-copy a `.env` someone already pulled.
- `keyway run` over `keyway pull` as a team norm — it is what makes the rotation step small.

**The skill.** Six real commands were missing (`doctor`, `connect`, `connections`, `sync`,
`disconnect`, `logout`), as were the destructive flags. The skill's revocation line was the one
genuine *correctness* defect: it said removing GitHub access "instantly revokes their ability to
pull secrets," full stop, which reads as sufficient. It now carries the rotate step.

## 3. Evidence

| Check | Result |
|---|---|
| `keyway --version` | `keyway version 0.5.3` at `/opt/homebrew/bin/keyway` (installed this lane) |
| `keyway doctor` | 4 passed, 2 warnings, 0 failed — repo detected as `sudomadhatter/Sudo_Hatter_Command` |
| `test_sops_prds_folder.py` bare | **61/61 passed, exit 0** |
| Manifest contract binds the new doc | **mutation → RED**: `T1 manifest matches: unexpected=['sharing_keys_secrets_secure.md']`, 60/61. Restored **from a copy**, re-asserted **61/61**. |
| `test_check_maps.py` | **27/27** (F2 caught this lane's missing `_artifacts/_main/INDEX.md` row; main was 27/27 clean, so the failure was genuinely mine) |
| `run_all.py` **in the lane**, bare | **25/25 files passed, exit 0** |
| `workflow_lint.py --toolkit-only` | **0 errors, 0 warnings**, 8 info (pre-existing BOM notes) |
| `py_compile` on the edited test | OK |

⛔ **One gate run in this lane was invalid before it was valid, and the cause is worth recording.**
An earlier `cd` to the main checkout — made to take a clean baseline — **persisted across subsequent
commands**, so a `run_all` reporting `25/25` and a `git status` reporting a clean tree were both
measured against `main`, which does not contain any of this work. Two things exposed it: the status
showed none of the seven changed files, and the count was identical to the baseline. Every gate was
re-run with an explicit `cd` inside a subshell and every git call with `-C`, and the lane's branch was
echoed from `rev-parse` rather than believed. This is the CWD-resolution trap this repo already
records for `task_preflight`, met one layer down: **a gate that resolves its subject from the working
directory will confidently green-light the wrong tree.**

⛔ **A related trap was avoided by construction:** `run_all.py` was first run piped to `tail`, which
made the reported `EXIT=0` **tail's** exit code, not the gate's — and that run had in fact FAILED
(`24/25`). Gates here are run bare, redirected to a file, with `$?` read from the gate itself.

⛔ **The mutation was restored from a filesystem copy, not `git checkout --`.** The edit being
defended was uncommitted, so a checkout would have restored from `HEAD` and reverted the fix itself —
the trap recorded twice in this repo's history. Green was re-asserted *after* the restore, which is
the only thing that distinguishes a real kill from a restore that silently undid the work.

## 4. Two findings that changed what I did

**The guide's location.** The request named `_my_resources/_quick_reference/`. That folder was vacated
by SCC-74 and `test_sops_prds_folder.py` T6 hard-fails on any `.md` placed there — writing it as asked
would have turned `run_all` red for every lane in the repo. More importantly `_my_resources/` is
excluded from repo-map regen, `check_maps.py` and GitNexus **by design**, so the guide would have
rotted unwatched, which is the exact failure SCC-74 existed to fix. Asked; the operator chose
`docs/_scc_sops_prds/`.

**The `.gitignore` warning is a false positive — and acting on it would have caused the damage.**
`keyway doctor` reports `.gitignore` missing `.env` patterns. `git check-ignore -v .env` returns
`.gitignore:42:**/.env`, i.e. it is already ignored. Keyway does literal matching and cannot read the
recursive glob. Had I trusted the tool's own report, I would have edited a deliberately-commented
ignore file to fix a problem that does not exist. **No `.gitignore` change was made**, and the false
alarm is documented in both the guide (§8) and the skill so nobody else acts on it either.

## 5. Your Actions

**The vault is not yet initialised — two commands, and only you can run them:**

```bash
cd /Users/sudohatter/Sudo_Hatter_Command
keyway login     # opens the browser for GitHub OAuth — needs your session
keyway init      # links this repo to its vault
keyway push      # seeds the vault from the existing .env
```

`keyway login` is a browser OAuth flow that cannot complete without you, and it links an account to an
external service — not something to initiate on your behalf. Repeat `login` once on the PC too;
credentials live in the OS keyring and do not travel.

## 6. Follow-on — needs its own ticket

The SCC-37 description opens *"AviationChat updates."* **SCC-37 is an SCC key and can only carry
command-centre work** — AGY's armed `commit-msg` hook rejects a foreign key outright, and cross-repo
work needs a ticket per repo. Standing up an AGY vault (`keyway init` inside
`Projects/AGY_AVIATIONCHAT`, plus deciding who holds its production environment) therefore needs its
own **AVCH** ticket. Named here rather than silently dropped.

## Code Review

_Pending — `/smh-code-review`._

Verdict: _pending_
