# Walkthrough — SCC-320: the missing Keyway migration step, permissions, and the `run` hang

**Ticket:** SCC-320 · **Epic:** SCC-75 (Security · Auth · Testing) · **Origin:** SCC-157 · **Date:** 2026-08-25
**Lane:** `chore/SCC-320-keyway-permissions-docs` · **Workspace:** `_main` (lobby) · **Lane class:** `LOCAL`

---

## What shipped

Three things, all documentation, all found by actually setting Keyway up on the PC rather than by
reading the pages.

### 1. The migration kit had no Keyway step at all

`docs/migrations/` is the kit a fresh machine follows, and Keyway appeared in none of its eleven
ordered steps and none of its eight install guides. Adds
`docs/migrations/install_guides/keyway-setup.md`, wired into `INDEX.md` as **step 6c**.

⭐ **The missing piece was the success canary, and its absence had already cost a ticket.**
`keyway doctor` reads **`5 passed, 1 warning`** on a correctly set-up machine in this repo — never
6/6, because the `.gitignore` warning is a permanent false positive (`git check-ignore -v .env`
returns `.gitignore:44:**/.env`, which is git's own answer). Before login it reads
`4 passed, 2 warnings`. Nothing wrote that down, so nothing could tell a finished setup from an
unfinished one — and **SCC-150 ("Install and verify Keyway CLI on Main PC") was marked `Done` while
this machine had never run `keyway login`.** The install half happened; the login half did not. A
verification step is what turns *"I ran the command"* into *"the machine is set up."*

### 2. ⛔ `keyway run` / `pull` with no `-e` blocks forever in any headless shell

Measured on the PC, Keyway 0.5.3: bare `keyway run -- node probe.js` **timed out at 90 s** with an
arrow-key environment picker on stderr. The same call with `-e development` returned
`✓ Injected 37 secrets` immediately.

Both pages printed the bare form as **the daily loop** — the single most-copied command in either
document — so an agent or CI job following the documented instruction deadlocks with no error and
nothing in the log.

⭐ **It was a carry-across failure, not an unknown.** Both pages *already* documented this exact
hazard for a sibling command: *"with no provider argument it prompts interactively — so a bare
`keyway sync` blocks forever in a headless or agent context."* The trap was understood and written
down, and simply never carried to `run`. The docs also promise `pull` *"defaults to development"* —
true of the **value**, false of the **prompting**.

Corrected in place (never left beside a corrected twin) across the guide's §5, §7, §9 and §11, and
the skill's §3, §4A and §4F.

### 3. The permissions procedure the guide never had

The guide stated **that** access is granted on GitHub and **that** offboarding is three steps, but
showed no `gh` command, no dashboard click-path, and no way to answer *"who can read this vault right
now?"* — policy without procedure. New §6.8 in the guide, mirrored into the skill, covering: who can
read it now (collaborators **and pending invitations** — an unaccepted invite is invisible to the
first query), adding someone, the **two separate levers** for re-scoping (GitHub role = whether they
are in at all; dashboard RBAC = which environments), removal with all three steps, and
`keyway diff <env> <env> --keys-only` as the blast-radius read that turns *"rotate everything"* into
a finite worklist.

Grounded on the live board rather than invented: the team is exactly two people, and `sir-cooper`
(write) reaches three repos.

Also folds in the operator's `gemini_extensions/` → `antigravity_extensions/` rename, every
reference repaired.

## Decisions

- **Both files move together on the full lane.** `lane_qualify.py` returned `TASK` because
  `.agents/skills/keyway-secrets/SKILL.md` is a toolkit path. The operator doc alone qualifies
  `LIGHT`, but the two pages are twins by contract — the skill's §7 names the doc as *"the
  human-facing version of this page"* — so fixing only the `LIGHT` half would ship drift between them.
  The lane was decided by script, not by judgment.
- ⛔ **The public-repo question is FLAGGED, not answered.** The guide's one-line model is *"if you can
  push to the repo, you can read its secrets."* Push and read are the same thing on a private repo and
  wildly different on a public one, and `Sudo_Hatter_Command` **is public**. The pages state the rule
  they can actually verify and mark the public-repo case as needing vendor confirmation, rather than
  asserting a bound nobody here has tested.

## Pitfalls

- **`keyway doctor`'s `.gitignore` check is a false positive in this repo**, and acting on it would
  make things worse. It does naive literal matching and cannot read the recursive glob, so it reports
  *"Missing .env patterns"* against a `.gitignore` that ignores `.env` via `**/.env`. ⛔ Never edit
  `.gitignore` on the strength of it — `git check-ignore -v .env` is git itself answering, and prints
  the exact rule and line number.
- **`keyway scan -e <x>` is `--exclude`, not `--env`.** `keyway scan -e production` excludes a
  *directory* named `production` and reports clean — a leak check that exits 0 for the wrong reason.
- **Revocation does not reach backwards.** Removing someone from GitHub ends their ability to pull,
  and does nothing about the plain-text `.env` already on their laptop. Rotate as well as revoke —
  which is the strongest argument for making `keyway run` the team default over `keyway pull`, since
  secrets that never touch disk leave nothing to rotate.

## Verification

Every gate run bare with `env -u PYTHONIOENCODING`, so no result depends on a variable the door
does not set:

| Gate | Result |
|---|---|
| `python .agents/scripts/tests/run_all.py` | **61/61 files**, exit 0 |
| `python .agents/scripts/workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, exit 0 |
| `python .agents/scripts/check_maps.py --depth3-only --strict` | exit 0 |
| `python .agents/scripts/check_links.py --base origin/main` | exit 0, clean |
| Every corrected command form | **verified by execution, not by reading** — `-e development` returns `✓ Injected 37 secrets`; the bare form hangs |

⚠️ **`check_links` was red once, and the fix was to the prose, not to the checker.**
`docs/migrations/INDEX.md` described the project-local autopilot engine with a backticked
`scripts/autopilot-dev-story.ps1`, which the checker reads as a repo-relative path claim. The path is
**correct-by-design absent** here — autopilot engines live in `Projects/`, and the lobby holds the
spec only — and the line is pre-existing on `main`; this lane merely shifted its number. Reworded so
the prose no longer looks like a claim about this repo. ⛔ Nothing was added to an ignore list: a
checker taught to skip a shape stops finding the real hits of that shape (SCC-285).

⭐ **This lane could not be gated when it was written.** The enforcement suite answered **43/61** on
this PC at the time, which is why the commit sat unpushed. **SCC-321** fixed that — the suite is now
61/61 on Windows, green on Linux via CI, and 61/61 on the Mac — so this lane's gate is a real gate for
the first time. `origin/main` (including all of SCC-321) is absorbed here, resolved by keeping both
`INDEX.md` rows.

**SOP currency:** `sop-currency` correctly did **not** fire. Its trigger list is `.agents/commands/`,
`.agents/rules/`, `.agents/scripts/*.py|.ps1`, the git hooks and root `AGENTS.md`; `skills/` is on its
explicit *"not a usage change"* list, and this lane's operator doc is not `workflows_testing_SOP.md`.
No `[sop-ok]` was needed or used.

## Follow-ons

These are **SCC-157's**, recorded here so they are not lost — they are deliberately not this ticket's
obligations and do not hold it:

- **Vault hygiene** — 37 secrets in `development`, 0 in `production`, including `GITHUB_PAT_CLASSIC`
  and `ANTHROPIC_API_KEY`. Exposure is currently nil (only the owner has push here), but AGY carries a
  second collaborator with `write`. Splitting environments is a secrets decision with real blast
  radius and is the operator's call. It keeps SCC-157 open on its own merits.
- **The public-repo vault question** — needs a vendor answer, flagged in both pages rather than guessed.
- **SCC-150** reads `Done` over a machine that had never run `keyway login`. Worth reopening on its own
  merits; noted rather than acted on, because reopening another ticket is not this lane's work.
- `.DS_Store` is tracked on `main` despite `.gitignore:77`.

## Your Actions

- [x] The merge itself — lands via this branch's PR

Nothing else is owed on this ticket. The three open questions above belong to **SCC-157**, which stays
open for them; recording them here as obligations would hold SCC-320 over work that is not its own.
