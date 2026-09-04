# Implementation Plan — SCC-37: secure secrets sharing (Keyway) + the operator guide

**Ticket:** SCC-37 (Task) — *Set up database to share secrets securely.*
**Branch:** `chore/SCC-37-keyway-team-secrets` · **Lane:** `.claude/worktrees/keyway-team-secrets`
**Date:** 2026-08-14

---

## 1. What the ticket actually asks for

> Stand up a secure secrets-sharing mechanism via a database instead of env files or manual
> handoff. Evaluate options (e.g. GCP Secret Manager, Vault) and implement the secure path.

The evaluation half is **already settled and shipped**: SCC-152 (merged `cf487a2`) chose **Keyway**
and authored `.agents/skills/keyway-secrets/SKILL.md`. Re-opening the option comparison would be
filing a settled decision as a gap. So SCC-37's remaining work is **implementation + the operator
page**, not selection.

## 2. Ground truth measured before planning (not assumed)

| Claim | How it was checked | Result |
|---|---|---|
| Keyway installed on the Mac | `brew install keywaysh/tap/keyway`; `keyway --version` | **now 0.5.3** — was absent; the PC had it, the Mac did not |
| Vault exists for the lobby | `keyway doctor` | **No** — `Authentication: Not logged in` |
| Lobby repo detected | `keyway doctor` | `sudomadhatter/Sudo_Hatter_Command` |
| `.gitignore` missing `.env` | `keyway doctor` says **missing**; `git check-ignore -v .env` | **FALSE POSITIVE** — `.gitignore:42` (`**/.env`) already ignores it |
| Skill's command list complete | `keyway --help` against the live 0.5.3 binary | **No** — missing `doctor`, `connect`, `connections`, `sync`, `disconnect`, `logout` |
| Skill's flags accurate | `keyway <cmd> --help` for all 8 documented verbs | Accurate, but **incomplete** — `pull --force`, `push -y`, `scan --json/--exclude`, `set -l` undocumented |

⛔ **The `.gitignore` finding is the one that would have caused damage.** `keyway doctor` does naive
literal matching and cannot read the `**/` glob form. Acting on its warning would have meant editing
a deliberately-commented ignore file (its comments explain why both slash forms are needed) to fix a
problem that does not exist. Evidence beats the tool's own report — no change is made there.

## 3. Scope boundary — this is an SCC lane, so it is the lobby only

The ticket description opens with *"AviationChat updates"*, but **SCC-37 is an SCC key and can only
carry command-centre work.** Cross-repo work needs a ticket per repo; a project's armed `commit-msg`
hook rejects a foreign key outright. Standing up an AGY vault therefore needs its **own AVCH ticket**
and is explicitly **out of scope here** — recorded in the walkthrough as a named follow-on, not
silently dropped.

## 4. Deliverables

1. **`docs/_scc_sops_prds/sharing_keys_secrets_secure.md`** — the operator guide. Placed here, not in
   `_my_resources/_quick_reference/`, on the operator's answer to a direct question: that folder was
   vacated by SCC-74 and `test_sops_prds_folder.py` T6 hard-fails on any `.md` in it, and everything
   in `_my_resources/` is excluded from every drift-checker by design, so a guide there would rot
   unwatched. Covers install → auth → daily use → **correct team usage** → failure modes.
2. **The three-edit manifest contract** that folder requires: the file, an `INDEX.md` row, and the
   filename added to `EXPECTED` in `.agents/scripts/tests/test_sops_prds_folder.py` (11 → 12 docs,
   including the two prose counts that state the number).
3. **`.agents/skills/keyway-secrets/SKILL.md` corrected** against the live binary — add the six
   missing commands and the undocumented flags, and correct anything the PC-authored version
   asserts that 0.5.3 does not do.
4. **Artifact record** — this plan, `task.yaml`, `walkthrough.md`, and the `_artifacts/_main/INDEX.md`
   row.

## 5. What I deliberately do NOT do

- **`keyway login` / `keyway init` are left to the operator.** Login is a GitHub OAuth browser flow
  that cannot complete without their session, and it links an account to an external service — an
  outward-facing action I do not initiate unilaterally. The guide gives the exact two commands and
  what to expect; the walkthrough records the vault as **not yet initialised**.
- **No `.gitignore` edit** — see §2.
- **No secret values are ever printed** — key names only, per the migrations law.

## 6. Verification

- `.agents/scripts/tests/run_all.py` **bare** (never piped — a pipe reports the pager's exit code).
- Every backticked path in the new doc must resolve (T9) and every `/command` must have a real master
  (T4); these are checked by the suite, not by eye.
- `keyway --version` and `keyway doctor` output captured in the walkthrough as install evidence.

## 7. Gate check

The SOP-currency gate watches `.agents/commands/`, `.agents/rules/`, `.agents/scripts/git-hooks/`,
`.githooks/`, and `.agents/scripts/*.py|.ps1`. This lane touches `docs/`, `.agents/skills/`, and
`.agents/scripts/tests/` (an **exempt** prefix), so **the gate does not fire** and no `[sop-ok]` opt-out
is needed. Verified by reading `_SURFACES` in `.agents/scripts/sop_currency.py`, not assumed.
