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
- [x] Adversarial review (5 lenses) + 16 findings applied — see `## Code Review`
  - The review corrected the guide on its own subject matter: `keyway push` edits `.gitignore`
    unprompted, `sync` is bidirectional and production-defaulting, and `-e` means `--exclude` on `scan`
- [x] Prove the folder's *other* gates bind this doc — 4-mutant sweep, 4/4 killed
- [x] File the AviationChat follow-on (**AVCH-57**)
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

**The vault is not yet initialised. Two commands, and only you can run them:**

```bash
cd /Users/sudohatter/Sudo_Hatter_Command
keyway login     # opens the browser for GitHub OAuth — needs your session
keyway init      # links this repo to its vault
```

`keyway login` is a browser OAuth flow that cannot complete without you, and it links an account to an
external service — not something to initiate on your behalf. Repeat `login` once on the PC too;
credentials live in the OS keyring and do not travel.

⛔ **Do NOT then run a bare `keyway push`, for two separately-verified reasons.**

1. **It edits your `.gitignore`.** Observed live during this lane's review: `keyway push` prints
   `✓ Added .env* to .gitignore`, appends `.env*`, and creates an empty `.env` — unprompted, with no
   `-y`, before authentication. That is the exact edit this lane refused to make by hand. A blanket
   `.env*` is broader than the deliberate `**/.env` and would also ignore the tracked `.env.example`.
   **Run `git diff .gitignore` after your first push and revert it.**
2. **The lobby's root `.env` is 5,680 bytes of live master configuration, not sandbox values.** A bare
   push files all of it into `development`, which the guide defines as the environment *every*
   developer can read. Sort production keys out first and push each environment explicitly with `-e`
   (`push` is the one command whose `--help` advertises no default).

Both are now documented in the guide (§4 and §8) and the skill, so nobody rediscovers them the hard way.

## 6. Follow-ons — filed, not just named

**① AVCH-57 — stand up the Keyway vault for AviationChat.** *(filed 2026-08-14)*
The SCC-37 description opens *"AviationChat updates."* **SCC-37 is an SCC key and can only carry
command-centre work** — AGY's armed `commit-msg` hook rejects a foreign key outright, and cross-repo
work needs a ticket per repo. The review's acceptance lens was right that naming it in a walkthrough
about to be archived is not tracking it, so it is now a real ticket carrying the scope, the
production-access decision, the "is Secret Manager better for AGY *runtime* secrets" question, and
the three verified CLI hazards so nobody rediscovers them.

**② Not yet filed — no parity or link guard over the skills surface** (review R17/R18).
Two gaps, one surface, both **pre-existing and wider than this lane**, which is why they were not
fixed inside it:
- Nothing asserts `.agents/skills/<n>/` and `.claude/skills/<n>/` stay byte-identical.
  `test_command_surfaces.py`'s mirror sweep covers `.opencode/commands` + `.agents/workflows` and
  iterates **commands**; a hand-authored skill with no command is outside it entirely. So an edit made
  to the Claude copy — the one Claude's loader actually reads — is silently reverted by the next
  `/smh-sync-agents`, with nothing reporting the disagreement.
- A backticked repo path inside a `SKILL.md` is checked by nothing: T9 scans only
  `docs/_scc_sops_prds/`, and `check_maps` prunes dot-directories. The guide→skill direction *is*
  covered; the skill→guide pointer this lane added is not. Relocate the guide and both doors point at
  a dead path while `run_all` stays green.

The fix already exists 40 lines away — `test_review_engine.py`'s master↔cache byte-compare — scoped to
one skill. Generalising it plus running `unresolved_paths` over `.agents/skills/*/SKILL.md` is a
self-contained Task. **Left to the operator to prioritise rather than filed unilaterally**, since it
changes an enforcement surface and competes with SCC-154, which is rewriting adjacent machinery now.

**③ Machine-cache propagation, deliberately deferred until after the merge.** The in-repo doors
(master + `.claude/skills/`) are updated and byte-identical. The opencode/Antigravity machine caches
live outside the repo, and running `/smh-sync-agents` **from an unmerged lane would publish
unreviewed content to machine-global caches**. Correct order: land on `main`, then sync from `main`.

## Code Review (2026-08-14)

Verdict: PASS @ ff3ce03
Suite evidence measured at the same sha (`run_all.py` bare, in-lane, after the last content change).

**Scope:** the 9-file `main...HEAD` diff — a new operator guide, the keyway skill + its Claude mirror,
the SOPs INDEX, the folder manifest test, the artifacts ledger, and this lane's own artifacts.
**Method:** `code-review-engine`, 5 lenses in parallel, each in its own clean context, `lens_budget:
standard`, `review_mode: full`.

```
lenses_run:      5/5   (Blind ok · EdgeCase ok · Literal ok · Acceptance ok · TestAdequacy ok)
lenses_na:       none
severity_floor:  CONCERNS  (raised to PASS after fixes applied — see dispositions)
notes:           no EVIDENCE_PACK supplied; diff spilled to a file (54 KB, over the 9k inline cap);
                 all 9 files handed to the literal lens, nothing withheld, no top-up spent.
```

⛔ **A lens mutated the tree while probing.** The Literal-Correctness lens ran `keyway push` in the
lane to determine its default environment; the command appended `.env*` to `.gitignore` and created an
empty `.env`. The lens disclosed this, reverted both, and the revert was independently verified here
(`git status` clean, no `.env`, no `.env*` in `.gitignore`, main checkout untouched). **That accident
produced the single most valuable finding of the review** — see R1.

### Findings

| # | file:line | severity | failure scenario | disposition |
|---|---|---|---|---|
| R1 | guide §4/§8 · skill §F | **important** | `keyway push` appends `.env*` to `.gitignore` and creates `.env` **unprompted, before auth** — observed live. The docs told the reader never to make that edit while the tool makes it for them; §5 of this walkthrough then instructed the operator to run exactly that command. A blanket `.env*` also swallows the tracked `.env.example`. | **applied** — hazard documented in guide §4 + §8 and the skill's flag table; `keyway push` **removed** from the operator's action list |
| R2 | guide §9 | **important** | "A healthy result is 6 passed. Two warnings are normal" — arithmetically impossible over 6 checks, and 6/6 is unreachable while §8 calls the `.gitignore` warning permanent. An operator chasing 6/6 has exactly one lever: editing `.gitignore` — the damage the whole lane exists to prevent. Found independently by 3 lenses. | **applied** — corrected to `5 passed, 1 warning` as healthy, with the pre-login `4 passed, 2 warnings` distinguished and "Not logged in" explicitly called *real* |
| R3 | guide §6.1 vs §6.3 vs §6.4 | **important** | §6.1 asserted "there is no second list to maintain"; §6.3 then instructs the reader to configure per-environment roles in the Keyway dashboard — a second surface — and §6.4's offboarding never cleared it. The guide's own named failure mode, created by its own procedure. Found independently by 3 lenses. | **applied** — §6.1 reframed (GitHub decides *membership*, dashboard decides *scope*); offboarding is now **three** steps with the dashboard check as 1b, mirrored into the skill |
| R4 | skill §E | **important** | `keyway sync` documented as "push the vault into the provider". Ground truth: it is **bidirectional** (`--pull` overwrites the vault from the provider), defaults to **`-e production`** — the only command that does — and prompts interactively with no provider argument, so it blocks forever headless. `--allow-delete` was absent from a table headed "Destructive Flags — Verified". | **applied** — section rewritten with all three traps; `--allow-delete` and the bidirectional/production-default warnings added to both flag tables |
| R5 | guide header | **important** | Banner claimed "every command and flag was run against the live binary". Only `--version` and `doctor` were executed; everything else was `--help`-verified, and with no vault the rest *could not* have run. An over-claim in the one line a reader calibrates trust from. | **applied** — narrowed to "flags checked against `--help`", with behavioural claims marked vendor-sourced and the one directly-observed behaviour (§8) called out |
| R6 | guide §4 · walkthrough §5 | **important** | Bare `keyway push` files the lobby's root `.env` — 5,680 bytes of live master config — into `development`, which the guide itself defines as readable by *every developer*. The seeding step contradicted the environment boundary two sections later. | **applied** — sort-before-push guidance added; `-e` now always explicit (`push` advertises no default) |
| R7 | guide §5 · skill §F | **important** | `-e` means `--exclude` on `scan` and `--env` on five other commands, both shipped on one page. `keyway scan -e production` silently excludes a *directory* named `production` and exits 0 — a leak check green for the wrong reason. | **applied** — `--exclude` written in full, with an explicit warning; added to the skill's hazard table |
| R8 | artifacts ×3 | **suggestion** | Plan, walkthrough and ledger all claimed six commands were added to the skill; `logout` was in the guide but **not** in the skill. The audit trail overstated what shipped. | **applied** — `logout` added to the skill; all six now verified present by grep |
| R9 | guide §5 | **important** | `keyway set KEY=value` example writes a live credential into shell history, scrollback and agent logs — a durable plain-text copy, in the guide whose premise is that copies have no leash, surviving the rotation it was run to perform. | **applied** — inline form removed from examples and documented as a hazard |
| R10 | guide §9 | **suggestion** | `--prune` recovery said "restore with `keyway set`", but `set` prompts for a value nobody has if the vault held the only copy — which §6.5 actively encourages. | **applied** — rewritten as regenerate-at-provider, cross-referenced to §6.4 step 3 |
| R11 | guide §6.6/§8 + ledger | **suggestion** | `.gitignore:42` pinned by line number in prose; no checker can validate a line number (T9's `PATH_LIKE` rejects the `:`), so it rots silently in the one section arguing you should verify rather than trust. | **applied** — line number dropped from the assertion; retained only inside the captured `git check-ignore` output, where it is evidence of a moment |
| R12 | skill §7 ×2 | **nitpick** | "Point **Daniel** there" — a personal name in a `.agents/` body served to every platform, against this system's generic-referent convention. | **applied** — now "the operator" |
| R13 | SOPs INDEX | **nitpick** | New row inserted above `sentry_…`, breaking the table's alphabetical order (`sentry` < `sharing` < `smh`). | **applied** — moved between `sentry` and `smh` |
| R14 | `machine_setup_card.md` | **suggestion** | The manifest test's own justification for keeping this doc in `_scc_sops_prds/` is "install lives in the setup card; the procedure lives here" — but the card had no pointer back, so a fresh-machine reader never learns the procedure exists. | **applied** — pointer added, including the §8 warning before a first push |
| R15 | ticket AC | **suggestion** | "Evaluate options (GCP Secret Manager, Vault)" — dispatched as settled by SCC-152, but neither string appears anywhere in the record, so the question has no durable answer. | **applied** — §10 now records why Keyway over Secret Manager and Vault, and the trade accepted |
| R16 | walkthrough §5 | **nitpick** | Said "two commands", listed three. | **applied** |
| R17 | skills surface | **suggestion** | No test asserts `.agents/skills/<n>/` and `.claude/skills/<n>/` stay byte-identical; `test_command_surfaces.py`'s mirror sweep covers `.opencode/commands` + `.agents/workflows` and iterates *commands*, and this skill has no command. Drift is silent, and sync-agents would revert an edit made to the Claude copy. | **deferred** — real and pre-existing, affects every hand-authored skill, not this diff. Belongs in its own Task; noted in §6 |
| R18 | skill body | **suggestion** | The skill→guide pointer sits in `.agents/skills/`, outside T9's scan set and pruned from `check_maps`, so relocating the guide leaves both doors pointing at a dead path with `run_all` green. The reverse direction *is* covered. | **deferred** — same ticket as R17; the asymmetry is a gap in the *guard surface*, not in this content |
| R19 | ticket AC | **suggestion** | The AGY/AviationChat half has no filed ticket, so closing SCC-37 leaves it recorded only in an archived walkthrough. | **applied** — AVCH ticket filed, see §6 |
| R20 | ticket AC | — | "Set up" marked Done with the vault uninitialised. | **dismissed with reasoning** — `keyway login` is a browser OAuth flow that cannot complete without the operator's session and links an account to an external service. Deferring it is correct; it is surfaced as the first thing in §5 and in the final report, not buried |

### Gate results

| Gate | Command | Result |
|---|---|---|
| Enforcement suite | `python3 .agents/scripts/tests/run_all.py` (bare, in-lane) | **25/25 files passed, exit 0** |
| Toolkit lint | `python3 .agents/scripts/workflow_lint.py --toolkit-only` | **0 errors, 0 warnings**, 8 info (pre-existing BOMs) |
| Folder manifest | `test_sops_prds_folder.py` (bare) | **61/61, exit 0** |
| Map/index drift | `test_check_maps.py` | **27/27** |
| Assertion evidence | 4-mutant sweep, restore from copies | **4/4 killed** — T9 (dead prose path), T3 (dead link), T4 (fake command), T2 (missing INDEX row), each naming this doc; **61/61 re-asserted after restore** |
| SOP currency | `_SURFACES` read directly | **does not fire** — diff touches `docs/`, `.agents/skills/`, and the exempt `.agents/scripts/tests/` |
| Link + anchor | T3 + T9 over the folder | green, and proven to bind by M1/M2 above |
| Door parity | `diff` master vs `.claude` mirror | byte-identical; skill has no command, so no launcher doors apply |
| `py_compile` | on the edited test | OK |

### Step 0.7 — blast radius re-derived against current `main`

- **Nothing moved.** `merge-base` == `main` == `origin/main` == `a4a6112`; **0 files** landed on `main`
  since this lane branched, so no reference this diff depends on was relocated. Nothing to absorb.
- **True overlap with `main`: none.** `merge-tree --write-tree` returns a clean tree oid, no conflict.
- **Sibling lane dependency — real.** `chore/SCC-154-gate-edges` is live and shares exactly one file:
  `_artifacts/_main/INDEX.md`, an append-only ledger both lanes add a row to. Whoever lands second
  reconciles by **keeping both rows**, never by taking one side. **SCC-37 should land first:** SCC-154
  rewrites the close-out machinery itself (`task_preflight.py`, `gate_receipt.py`,
  `smh-close-task-merge-tree.md`, `merge-target-guard.sh`, `pre-push-merge-backstop.sh`), and a lane
  that changes commit/push machinery lands last by rule.

### Clean-Code Gate

Machine floor imported from the gate table above (`run_all`, `workflow_lint`, `py_compile`, link+anchor)
rather than re-run. Judgment pass over the toolkit conventions:

| Check | Result |
|---|---|
| Comment contract | n/a — one `.py` line added (a set member + inline rationale); docstring updated to match |
| Generic referent in `.agents/` bodies | **fixed this pass** (R12) |
| Manifest three-edit contract | honoured: file + INDEX row + `EXPECTED`, both prose counts moved 11→12 |
| Prose-pinning / vacuous guards | none added — this lane pins no new literals |
| Bloat / drift beyond the acceptance list | none; every changed file traces to a plan deliverable or a review finding |

**Changes applied:** 16 of 20 findings fixed in this pass; 2 deferred to a named follow-on (R17/R18),
1 dismissed with reasoning (R20), 1 closed by filing a ticket (R19).
