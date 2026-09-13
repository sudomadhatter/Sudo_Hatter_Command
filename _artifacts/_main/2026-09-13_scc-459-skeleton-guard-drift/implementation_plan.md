# SCC-459 — the skeleton's guards are a hand-shortened copy, and nothing compares them

## Context

`Projects/sudo-project-skeleton` is the repo we clone to start a project. Four of its git-hook
guards are hand-shortened copies of the lobby's, and nothing in any repo compares them. Measured
2026-09-13 against `origin/main` of all three repos (lobby `a2642da2`, skeleton `f88f9ce`,
`AGY_AVIATIONCHAT` `1aa35485`), counting only lines that execute:

| guard (`.agents/scripts/git-hooks/`) | lobby | AVCH | skeleton |
|---|---|---|---|
| `merge-target-guard.sh` | 169 | 169 | **124** |
| `mint-push-token.sh` | 90 | 90 | **72** |
| `pre-push-main-approval.sh` | 115 | 116 | **95** |
| `pre-push-merge-backstop.sh` | 94 | 87 | **73** |
| **total** | **468** | **462** | **364** |

AviationChat tracks the lobby line-for-line — `git diff --no-index` against it is `10 insertions`,
and those ten are a provenance header. The skeleton is `197 deletions` on the same file.

⭐ **The 104 lines are NOT uniformly behavioural, and the ticket's headline overstates it.** Reading
the code-only diffs (`grep -vE '^\s*(#|$)'` on both sides, then `diff`) splits them cleanly:

| guard | verdict |
|---|---|
| `mint-push-token.sh` | **message text only.** Every condition, branch and exit code is identical, including the `[ -s "$TOKEN" ]` write-verify fix that AVCH-59 measured. Diagnostically weaker, behaviourally equal |
| `pre-push-main-approval.sh` | **message text only.** Same — every `refuse` fires on the same condition; the strings are shorter |
| `merge-target-guard.sh` | **real behaviour gap** |
| `pre-push-merge-backstop.sh` | **real behaviour gap, and one active defect** |

### The three real defects

1. ⛔ **The skeleton tells the reader to run `git reset --hard`.** `pre-push-merge-backstop.sh`'s
   refusal prints `git reset --hard origin/$1`. The lobby's copy prints `git reset --keep` and bans
   the other by name: *"Never `--hard` in a shared checkout — it carries other sessions' uncommitted
   work."* That ban exists because SCC-180: a refusal banner's `reset --hard` remedy destroyed three
   sessions' uncommitted work. **The skeleton ships the pre-SCC-180 instruction to every new
   project.** This is not a missing line; it is a wrong one.

2. **`pre-push-merge-backstop.sh` scans a narrower set of lanes.** The lobby builds
   `SCOPES="refs/heads/chore refs/heads/claude"` and **adds `refs/heads/epic` when the lane being
   pushed is a `chore/*`**. The skeleton hard-codes chore+claude. So a chore lane carrying an
   unlanded `epic/*` branch's commits is caught in the lobby and passes in the skeleton — the guard
   is genuinely blind to one of the three shapes it exists to catch.

3. **`merge-target-guard.sh` exits silently when it cannot classify.** The lobby carries
   `UNJUDGED` / `UNJUDGED_NAMES` / `ANY_NAMED` / `INCIDENT_SEEN` and a block that prints, in three
   worded arms, *why* it declined to judge and which backstop still covers the merge. The skeleton
   has none of it: an unclassifiable merge source produces no output at all, so it is
   indistinguishable from an approved one. Gone with it, the SCC-97 signature banner — the
   chore-onto-sibling-chore case, which is the exact shape of the 2026-08-11 production merge that
   printed success and was caught only by suspicion.

### A fourth defect, live in BOTH projects (port check 4)

The guards print `.agents/rules/git-policy.md` as a path. **Neither the skeleton nor AviationChat
carries that file** — both hold only their own tier-2 rules, per the thin model:

```
skeleton  .agents/rules/  -> INDEX.md            (that is the whole folder)
AGY       .agents/rules/git-policy.md            -> No such file or directory
```

Live count: **2 occurrences in the skeleton, 5 in AviationChat.** A byte-for-byte port would raise
the skeleton's to 6. Port-checklist check 4 is exactly this: *"A message that names
`.agents/rules/<x>.md` resolves in the lobby and resolves to nothing in the project. Point at the
centre's copy by name, or drop the path."* The repair must reword, not copy.

### Why it drifted: nothing compares them

AviationChat's copies carry a header — *"PORTED, UNCHANGED, FROM THE COMMAND CENTRE (AVCH-54,
2026-08-15) · source: `Sudo_Hatter_Command/.agents/scripts/git-hooks/merge-target-guard.sh` · at
sha: `df39c960`"* — so drift there is at least visible to a reader. The skeleton's copies carry no
header, no source, no sha, and no test. This is structurally the same failure `test_twin_parity.py`
was built for, in that file's own words: *"nothing in the repo compared the two families, so
`workflow_lint --toolkit-only` exited 0 with 172 confirmed drift findings live in the tree. That
zero was the bug."*

### Two constraints that decide the design, both measured

- ⛔ **The lobby's CI does not check out submodules.** `.github/workflows/main-write-gate.yml` uses a
  plain `actions/checkout@v4` with `fetch-depth` and `ref` and **no `submodules:` key**, so
  `Projects/sudo-project-skeleton` is an empty directory on every runner. A lobby-side CI gate on
  skeleton *content* is therefore structurally impossible without changing CI config — which is an
  Ask First item, and is not proposed here.
- ⛔ **The skeleton has no test infrastructure at all.** `.agents/scripts/tests/` does not exist
  there — `ls` returns *No such file or directory*. It cannot host a test today, and building it is
  its own lane.

Together these force the same answer SCC-456 reached for `.env`: **the check runs where the evidence
exists and reports a NAMED non-passing row where it does not.** That is the existing house pattern
(SCC-456 Part A guarded `pwsh` the same way), not a new invention.

## Decisions taken

1. **The source is the lobby, not AviationChat** — proven by AviationChat's own provenance headers.
   Both projects are consumers of the same lobby files.
2. ⭐ **NOT the teaching-edition export engine.** I proposed that engine before this measurement and
   it is the wrong tool: the export regenerates a whole repo into an empty target, and the skeleton
   is a hand-built template of 704 files (586 of them its own `_bmad/`) that must never be
   regenerated. The right precedent is `test_twin_parity.py` — a **parity check over a declared set**,
   with an auditable divergence escape.
3. **Byte-parity plus a substitution table, not fenced regions.** AviationChat already proves
   whole-file parity works at Δ10. Fences would be heavier and the guards have no natural region
   boundaries.
4. **One lane, no subtasks.** Same repo pair, same lane class, strictly sequential: the detector
   cannot be written until the files it declares are at parity. A ticket with no branch is a row
   nothing writes to.

---

## Part A — repair the four guards in the skeleton

⚠️ **AUDIT FINDING 1 (baked) — step 0, before any edit: this lane's worktree has NO skeleton.**
`git submodule status Projects/sudo-project-skeleton` in the lane returns
`-6c76fd9755a0a3d8bf1a32682eeb2925d232b00b` — the leading `-` is *uninitialised* — and the directory
is empty. Initialise it in the lane and work there; **never** edit the shared lobby's checkout
instead, which sits on another branch and would strand Part A's commits where this lane cannot push
them:

```bash
cd <lane worktree> && git submodule update --init Projects/sudo-project-skeleton
cd <lane worktree>/Projects/sudo-project-skeleton && git switch main && git merge --ff-only origin/main
```


Bring each to the lobby's **behaviour**, with two deliberate departures from byte-identity:

- a provenance header (AviationChat's proven shape: source path, source sha, and the note that the
  duplicate is compelled because git runs hooks in the repo they gate);
- every `.agents/rules/<x>.md` path reworded to name the command centre's rule **by name**, per port
  check 4 — including the 2 that already ship dead.

**The three defects above are the acceptance, not the line count.** `mint-push-token.sh` and
`pre-push-main-approval.sh` come to parity for the detector's sake and because a fuller refusal
message is the whole value of those guards, but neither changes what they allow or refuse.

⛔ **Seen RED first.** Each defect gets its pin written against the *current* skeleton file and run
before the repair: `reset --hard` present, `refs/heads/epic` absent from `SCOPES`, the
declined-to-judge block absent, `.agents/rules/` path count non-zero.

## Part B — the detector

**NEW `.agents/template-ports.json`** in the lobby — the declared set, mirroring the shape of
`.agents/critical-surfaces.json` (which this repo already uses for exactly this "a line that can
widen itself is not a line" problem):

```json
{ "ports": [
  { "source": ".agents/scripts/git-hooks/merge-target-guard.sh",
    "consumers": ["Projects/sudo-project-skeleton", "Projects/AGY_AVIATIONCHAT"],
    "why": "…" }
] }
```

**NEW `.agents/scripts/template_parity.py`** — for each declared port × consumer: strip the
provenance header, apply the declared substitutions, compare to the lobby's copy. Exit 0 clean,
2 on drift. Three properties, each pinned:

- **A consumer whose checkout is absent is a NAMED non-passing row**, never silence and never green.
  This is the CI case and it is the one that decides whether the check is worth anything.
- **The manifest cannot shrink itself out of the gate** — a diff that touches
  `.agents/template-ports.json` is always checked, the self-listing rule `scope_check.py` already
  applies to `critical-surfaces.json`.
- **The provenance sha is checked against the lobby's current sha for that file.** A port that is
  byte-identical to a *stale* source is still stale, and only the sha can say so.

**NEW `.agents/scripts/tests/test_template_parity.py`** — its arms, the absent-consumer row, the
self-listing, and a mutant per guard proving each pin fails when the guard is removed.

⚠ **AviationChat is declared as a consumer but its repairs are NOT in this lane.** Its 5 dead rule
paths need an `AVCH`-keyed commit: AviationChat's armed `commit-msg` gate rejects an `SCC` key by
design (port check 6), so an SCC lane physically cannot land there. The detector will report them;
the fix is one line of work under its own key. **Named here for your word, not done silently.**

---

## Part C — bump the lobby's skeleton pointer (AUDIT FINDING 3)

The lobby's `origin/main` records `6c76fd97` for `Projects/sudo-project-skeleton`; the skeleton's own
`origin/main` is `4510e05`. Between them: `15 files changed, 1260 insertions(+), 7 deletions(-)` —
the whole of SCC-441, merged in that repo as its PR #1, never recorded here. **The detector reads the
pointer, not this machine's checkout**, so without this bump it is green here and red everywhere
else.

⚠️ **AUDIT FINDING 4 (baked) — the landing order changes.** The lobby PR carries the detector **and**
this bump in one commit, and lands **after** the skeleton PR. There is then no window in which `main`
holds a detector pointed at a pre-repair tree.

---

## Part D — the two switches (operator ruling, 2026-09-13)

> *"there will not be a Jira board set up yet when we make a new project. We may clone it first. It
> should query the user to see if they plan to make a Jira board and then adjust if they are opting
> to not use one. Some of the quick projects for just front end I do I never make a Jira board and I
> still want to use the other features."*

**The ruling resolves audit finding 2, and the code already agrees with it.** Measured: `grep -c
'jira.conf\|JIRA_KEYS'` over all four guards returns **0, 0, 0, 0**. Not one of them reads a board.
`mint-push-token.sh` already declares the key optional — `[--key <JIRA-KEY>]` in its usage, `${KEY:-<no
key>}` in its banner, and the key match guarded by `if [ -n "$KEY" ]`. So branch protection and Jira
were never one feature; they were one *marker convention* that made them look like one.

**Two independent switches, and the mechanism already exists** — the three markers are three separate
files, so nothing new is invented here. What changes is which ones ship set, and whether the reader is
asked:

| Marker | Ships | Why |
|---|---|---|
| `MERGE-TARGET-ENFORCE` | **armed** | zero Jira references; a front-end project with no board still must not merge onto the wrong branch |
| `MAIN-PUSH-ENFORCE` | **armed** | same; the approval token has no key requirement |
| `JIRA-ENFORCE` | **off, and now ASKED** | it genuinely needs a board, and a fresh clone has none |

⭐ **The skeleton ships the two markers TRACKED, so a bare `git clone` is protected without running
the door.** The operator's *"We may clone it first"* is the case that decides this: arming only inside
`new-project.ps1` would leave every hand-cloned project unguarded, which is today's defect wearing a
different hat.

### `/smh-new-project` asks, instead of documenting

Today the door treats Jira as optional in **prose** (`smh-new-project.md:49-58`, `new-project.ps1:106-113`)
and never asks; and `new-project.ps1` **creates no ENFORCE marker at all** — it arms `core.hooksPath`
via `Arm-HooksInclude.ps1` so the hooks *run*, then leaves every gate in warn-only. The door gains one
question:

> **Will this project use a Jira board?**
>
> - **Yes** → walk the existing four steps now, while the project has no history: `jira.conf`,
>   `JIRA_SITE`, `JIRA_KEYS`, `acli jira auth status` with the site required to match, then
>   `touch .agents/scripts/git-hooks/JIRA-ENFORCE`.
> - **No** → write `.agents/jira.conf` carrying `JIRA_KEYS=""` and a dated line recording the
>   decision, and leave `JIRA-ENFORCE` absent.

⛔ **The "no" answer is RECORDED, not silence, and that is the whole point of writing it down.** Today
an absent `jira.conf` means two different things — *"asked, and this project does not use a board"* and
*"nobody has set it up yet"* — and no reader can tell them apart, so every agent that meets one assumes
the other. This is the same lesson as trunk mode, which is **read** from git (`epic_mode.py`) rather
than guessed. The conf already no-ops on an empty `JIRA_KEYS` (`jira.conf.example`: *"no jira.conf
means no keys to check, so commits pass untouched"*), so the recorded "no" costs nothing at runtime
and answers the question permanently.

⚠️ **What this lane does NOT claim to deliver.** Making the *whole flow* run without a board is a
larger, real question and it is **not** in this lane. Measured so the size is known rather than
guessed: nine lobby scripts take a `--key` / `--expect-key`, and `jira_feed.py` already carries the
beginnings of the answer — `ACLI_UNREACHABLE = 124` (`:123`) and a `need_board=False` path (`:1014`,
*"an ad-hoc chore fix has a ticket and a walkthrough but no board"*). Part D makes the GUARDS work
without a board, which is what the ruling asked for. The close-out ceremony running boardless is its
own ticket, named in `## Your Actions`.

---

## Acceptance

| # | Statement | Check |
|---|---|---|
| A | The skeleton no longer instructs `git reset --hard` | `grep -c 'reset --hard' <skeleton>/.agents/scripts/git-hooks/pre-push-merge-backstop.sh` → `0`, seen non-zero first |
| B | The skeleton's backstop scans `epic/*` for a chore lane | `grep 'refs/heads/epic' …/pre-push-merge-backstop.sh` resolves, seen absent first |
| C | An unclassifiable merge source is reported, not silent | the declined-to-judge block present; a fixture merge with an unnamed source prints a reason |
| D | No guard names a rule path the target lacks | `grep -c '\.agents/rules/' <skeleton>/.agents/scripts/git-hooks/*.sh` → `0`, seen `2` first |
| E | The four guards are at parity with the lobby | `template_parity.py --repo .` exit 0; code-only line counts 169/90/115/94 |
| F | Drift goes RED | mutate one lobby guard → `template_parity.py` exit 2 naming the file; restore → exit 0 |
| G | An absent consumer is a named non-passing row | run with the submodule path emptied → the row is printed and the run does not score green |
| H | The manifest cannot widen itself | a diff containing `.agents/template-ports.json` is still checked (test) |
| I | Nothing else moved | `run_all.py` green; `workflow_lint --toolkit-only` 0 errors; `check_maps --depth3-only --strict` clean |
| J | The skeleton ships the two non-Jira gates ARMED | `MERGE-TARGET-ENFORCE` and `MAIN-PUSH-ENFORCE` are tracked in the skeleton, seen absent first; a fixture clone refuses a wrong-target merge with `exit 1`, not `exit 0` |
| K | Jira stays off, and is ASKED | `JIRA-ENFORCE` absent; `/smh-new-project` body carries the question and both branches; `new-project.ps1` writes the recorded `jira.conf` on a "no" |
| L | A boardless project is distinguishable from an unconfigured one | after a "no", `.agents/jira.conf` exists with `JIRA_KEYS=""` and the dated decision line; the commit gate still no-ops (test) |

## Declared Change Set

- EDIT `Projects/sudo-project-skeleton/.agents/scripts/git-hooks/pre-push-merge-backstop.sh` — the `--keep` remedy, the `epic/*` scope, the declined-to-judge note, the provenance header → A, B, E
- EDIT `Projects/sudo-project-skeleton/.agents/scripts/git-hooks/merge-target-guard.sh` — the declined-to-judge path, the SCC-97 banner, the reworded rule references, the provenance header → C, D, E
- EDIT `Projects/sudo-project-skeleton/.agents/scripts/git-hooks/mint-push-token.sh` — refusal text to parity, the provenance header → E
- EDIT `Projects/sudo-project-skeleton/.agents/scripts/git-hooks/pre-push-main-approval.sh` — refusal text to parity, the reworded rule reference, the provenance header → D, E
- NEW `.agents/template-ports.json` — the declared port set → E, F, H
- NEW `.agents/scripts/template_parity.py` — the checker → E, F, G, H
- NEW `.agents/scripts/tests/test_template_parity.py` — its arms and mutants → F, G, H
- EDIT `.agents/scripts/INDEX.md` — two rows for the new script and its test → I
- EDIT `.agents/rules/living-template-sync.md` — the skeleton is now detected; say how → I
- NEW `Projects/sudo-project-skeleton/.agents/scripts/git-hooks/MERGE-TARGET-ENFORCE` — ships armed → J
- NEW `Projects/sudo-project-skeleton/.agents/scripts/git-hooks/MAIN-PUSH-ENFORCE` — ships armed → J
- EDIT `Projects/sudo-project-skeleton/README.md` — the arming steps name all three markers, not only Jira → J, K
- EDIT `Projects/sudo-project-skeleton/.agents/scripts/INDEX.md` — `:7` says "ships disarmed" of Jira ONLY; correct it → J, K
- EDIT `.agents/commands/smh-new-project.md` — the Jira question and both branches → K, L
- EDIT `.opencode/commands/smh-new-project.md` — mirror → K
- EDIT `.agents/scripts/new-project.ps1` — ask; write the recorded `jira.conf` on a "no"; never touch the two non-Jira markers, which now arrive armed from the clone → K, L
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` + `_changelog.md` — the new gate, and the two switches → I, K

## Port section — the six checks (port-checklist rule 5)

**Trigger proven**, `git diff --no-index --stat`, lobby vs each consumer:

| guard | vs skeleton | vs AviationChat |
|---|---|---|
| `merge-target-guard.sh` | `4 insertions(+), 197 deletions(-)` | `10 insertions(+)` |
| `mint-push-token.sh` | `7 insertions(+), 115 deletions(-)` | `41 insertions(+), 32 deletions(-)` |
| `pre-push-main-approval.sh` | `16 insertions(+), 147 deletions(-)` | `31 insertions(+), 28 deletions(-)` |
| `pre-push-merge-backstop.sh` | `6 insertions(+), 164 deletions(-)` | `12 insertions(+), 45 deletions(-)` |

| # | Check | Answer, with the output that produced it |
|---|---|---|
| 1 | A git-given path used as given | **clean.** `grep -n 'git-common-dir\|--git-path'` finds four sites; `grep -n 'case .*/\*)'` returns only `pre-push-main-approval.sh:45`, which is the comment *"USED AS GIT GIVES IT — no hand-rolled `case "$GIT_COMMON" in /*)` normalisation."* No normaliser exists in any of the four |
| 2 | `printf`, never `echo`, for escapes | **clean.** `grep -nE 'echo .*\\(c\|n\|t)'` returns nothing. The two hits from the rule's looser grep (`merge-target-guard.sh:332`, `pre-push-merge-backstop.sh:105`) are shell-escaped `\"` and `` \` `` — no escape sequence reaches `echo` |
| 3 | On a write, verify the FILE | **clean, and already ported.** The only redirect is `mint-push-token.sh:167 } > "$TOKEN"`, and **both** the lobby and the skeleton follow it with `if [ ! -s "$TOKEN" ]` before the success banner. AVCH-59's measured trap (the `if ! { … }` "fix" that no-ops on bash and macOS `/bin/sh`) is avoided on both sides |
| 4 | No rule path the target lacks | ⛔ **DEFECT, live in both.** 2 occurrences in the skeleton, 5 in AviationChat; `ls` proves neither repo carries `.agents/rules/git-policy.md`. Part A rewords the skeleton's; AviationChat's needs its own `AVCH` key (check 6) |
| 5 | Runs on both sides | **clean.** All four are `#!/bin/sh`, no `python`/`python3` fork in any of them. `core.hooksPath` in the skeleton reads `.githooks`, so this clone is armed — but that is **local config and does not travel with a clone**, which is why `.agents/jira.conf.example` step 3 tells a new project to set it per machine |
| 6 | Repo-local, and the target's own key | **clean, and it constrains the lane.** Both consumers carry their own `.githooks/` and `.agents/scripts/git-hooks/`; the skeleton ships `jira.conf.example` with `JIRA_KEYS=""`, so its commit gate no-ops and an `SCC`-keyed commit is accepted there (SCC-441 already landed that way). AviationChat's gate is armed to `AVCH` and **would reject this lane's commits** — the reason its repairs are named as a follow-on rather than folded in |

## Verification

1. RED first, all four pins, pasted: `reset --hard` present · `refs/heads/epic` absent · the
   declined-to-judge block absent · `.agents/rules/` count `2`.
2. Repair Part A; the same four commands, now green; code-only counts `169/90/115/94`.
3. `template_parity.py --repo .` → exit 0; mutate one lobby guard → exit 2 naming it; restore and
   verify the bytes and sha.
4. Empty the consumer path → the named non-passing row prints and the run does not score green.
5. `test_template_parity.py` under `run_all.py`; a mutant per pin, every restore verified.
6. `run_all.py`, `workflow_lint --toolkit-only`, `check_maps --depth3-only --strict`,
   `check_links --base origin/main`.

**Two repos land separately, in this order (AUDIT FINDING 4).** The skeleton's four files are its own
repo and its own PR, and land FIRST. The lobby PR then carries the detector **and** the Part C pointer
bump in one commit, so `main` never holds a detector aimed at a pre-repair tree.

## Your Actions

- **Approve or redirect this plan.** Nothing outside `_artifacts/` has been written.
- **Two things need your word specifically.**
  1. ✅ **RULED 2026-09-13 — audit finding 2 is settled.** The two non-Jira gates ship armed; Jira
     becomes a question `/smh-new-project` asks, with the "no" recorded rather than left silent. See
     Part D. Nothing further is owed here.
  2. Whether AviationChat's 5 dead rule paths get an `AVCH` ticket now or wait. They cannot ride this
     lane — its commit gate rejects an `SCC` key by design (port check 6).
  3. Whether the **close-out ceremony running boardless** gets its own ticket. Part D makes the
     GUARDS board-independent, which is what the ruling asked for; running `/smh-close-task-merge-tree`
     on a project with no board is a separate job — nine lobby scripts take a key, and `jira_feed.py`
     already has `ACLI_UNREACHABLE` and a `need_board=False` path to build on.

---

## Self-Audit (2026-09-13)

**Level:** LEDGER+BLAST (four hook files, two NEW scripts, a NEW declaration read by a gate, files
in three repos). **Mode:** PRE-DEV. **Subject:** the command centre, lane
`chore/SCC-459-skeleton-guard-drift` @ `a2642da2`.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every EDIT path exists / every NEW path is absent; the Declared Change Set parses;
             lane fit (no deployable path); both-sides commands; the Scope Ledger over the three
             NEW rows; the lane's own ability to perform Part A
read:        declared_change_set.py parse <this plan> -> "present": true, 10 entries, every bullet
               carrying an op and an acceptance row; no `incomplete`
             EDIT paths: all 8 present. NEW paths: all 3 absent (correct)
             lane fit: the declared set is .agents/** in two repos - no backend/ frontend/ firebase/
               functions/ mobile/ .github/ path, so this is Task work and lands via
               /smh-close-task-merge-tree. Clean
             both sides: all four guards are `#!/bin/sh` with no python fork; the NEW scripts are
               python3 stdlib, matching every other .agents/scripts/ gate
             ⛔ THE LANE CANNOT PERFORM PART A AS WRITTEN -> finding 1
             cd <lane worktree> && git submodule status Projects/sudo-project-skeleton
               -> "-6c76fd9755a0a3d8bf1a32682eeb2925d232b00b" (leading `-` = NOT INITIALISED)
             ls <lane worktree>/Projects/sudo-project-skeleton/ -> empty (2 entries: . and ..)
verdict:     findings below (1, 3, 5)
```

Scope Ledger — every `NEW` x the acceptance row that requires it: `.agents/template-ports.json` ->
E, F, H; `.agents/scripts/template_parity.py` -> E, F, G, H; `.agents/scripts/tests/test_template_parity.py`
-> F, G, H. **No empty acceptance cell.** Caller count for `template_parity.py` after the edit:
its test, plus direct invocation from the SOP-documented gate line - the same shape as
`teaching_edition_staleness.py`, which this repo already runs that way, so it is not a
single-caller abstraction invented by its own plan. **Precondition:** the plan carries nine
acceptance rows, each with a pasted observable; the TICKET carries an INTENDED OUTCOME rather than
a formal ACCEPTANCE block -> finding 5, non-blocking (SCC-456 closed the same way).

```
lens:        2 Parity + Blast
checks_run:  the gate/hook row (does it ship ARMED?); the script row (callers, test, INDEX); the
             >1-repo row (the port section's six checks, verified rather than trusted); twins;
             sibling worktrees and landing order; the submodule pointer the detector will read
read:        ⛔ ARMING -> finding 2. For each of JIRA-ENFORCE, MAIN-PUSH-ENFORCE, MERGE-TARGET-ENFORCE:
               lobby=present  skeleton=ABSENT  avch=present
             <skeleton>/.agents/scripts/git-hooks/merge-target-guard.sh:144
               `[ "$ENFORCE" = "1" ] || exit 0`   and :10
               `[ -f .agents/scripts/git-hooks/MERGE-TARGET-ENFORCE ] || ENFORCE=0`
             <skeleton>/.agents/scripts/INDEX.md:7 "Ships **disarmed**: no `jira.conf`, no
               `JIRA-ENFORCE` marker - commits pass unchecked."  <- names ONLY the Jira gate
             <skeleton>/README.md:134 "touch .agents/scripts/git-hooks/JIRA-ENFORCE" <- the arming
               steps name ONLY the Jira marker; the other two appear nowhere in the README
             mitigation measured, :128-144: a DISARMED guard still prints the full banner
               ("⚠ merge-target-guard: this merge is WRONG, but the gate is disarmed"), the
               target/source lines and the remedy, then exits 0. The repair therefore ADVISES even
               when it cannot block - finding 2 is real but not fatal to the lane
             ⛔ POINTER -> finding 3. git ls-tree origin/main Projects/sudo-project-skeleton
               -> 6c76fd9755a0a3d8bf1a32682eeb2925d232b00b
             <skeleton> git rev-parse origin/main -> 4510e05 "Merge pull request #1 from
               sudomadhatter/chore/SCC-441-ci-toggles"; recorded pointer is 3 commits behind and
               `git diff --stat 6c76fd97 origin/main` -> 15 files changed, 1260 insertions(+), 7
               deletions(-) (pr-check.yml +193, backend/tests/test_classify_changes.py +215, ...)
             defect claims re-verified against the skeleton's origin/main, not just its checkout:
               git diff --stat f88f9ce origin/main -- .agents/scripts/git-hooks/ -> EMPTY
             siblings: git worktree list -> the shared lobby @ a2642da2 [chore/SCC-186-standing-push]
               and this lane @ a2642da2. Neither declares any file in this plan's set: NO
               landing-order dependency inside the lobby. chore/SCC-431-zoo-remote is a local branch
               with no worktree (draft PR #193, plan only)
             twins: none - `.agents/scripts/git-hooks/*` has no cicd-/smh- pair
             risk_seam.py: `unclassified`, the permanent and correct answer for the command centre
               (SCC-289) - every judgement here comes from the files
             port section: all six re-run independently; checks 1, 2, 3, 5 and 6 confirmed as the
               plan states them, and check 4's defect count confirmed (skeleton 2, AviationChat 5,
               neither repo carrying .agents/rules/git-policy.md)
verdict:     findings below (2, 3, 4)
```

```
lens:        3 Pre-Mortem  (bounded - attaches narratives, originates nothing)
checks_run:  the fresh-clone case; the silent case; the other-tree case; the sibling-lands-first case
read:        finding 1 -> the builder opens the lane, `ls Projects/sudo-project-skeleton/` is empty,
             and the natural recovery is to edit the LOBBY's checkout instead, which is a different
             worktree on a different branch - Part A's commits then land nowhere this lane can push
             finding 2 -> a new project clones the skeleton, follows README:134, arms the Jira gate,
             and never learns the merge-target guard or the main-push approval gate exist. The
             repaired 104 lines print a warning nobody has configured their terminal to surface -
             the "warn-only reads as clean" scar this lens's own table names
             finding 3 -> the detector is written and passes locally against the skeleton checkout
             on disk (f88f9ce), lands, and then reads the POINTER (6c76fd97) on any other machine:
             a green here and a red there, from the same commit
             finding 4 -> the skeleton PR merges, the lobby PR is still open, and `main` carries a
             detector whose declared consumer is at a pointer that predates the repair: red on main
verdict:     findings below (attached to 1, 2, 3, 4)
```

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `<lane worktree>` · `git submodule status Projects/sudo-project-skeleton` | `-6c76fd9755a0a3d8bf1a32682eeb2925d232b00b` (leading `-`), and `ls` of that path returns empty | **Part A cannot be performed from this lane.** The four EDIT targets do not exist in the tree the plan is written for. **Baked** (Part A step 0 below). | **high** |
| `<skeleton>/.agents/scripts/git-hooks/merge-target-guard.sh:144` · `:10` · `INDEX.md:7` · `README.md:134` | `[ "$ENFORCE" = "1" ] \|\| exit 0` · `[ -f …/MERGE-TARGET-ENFORCE ] \|\| ENFORCE=0` · "Ships **disarmed**: no `jira.conf`, no `JIRA-ENFORCE` marker" · `touch .agents/scripts/git-hooks/JIRA-ENFORCE` | **All three arming markers are absent from the skeleton and the README arms only Jira**, so the merge-target and main-push gates are off in every cloned project and no document says so. Acceptance A/B/C can go green while nothing blocks. Mitigated, not cured: a disarmed guard still PRINTS. **Operator decision — baked into `## Your Actions`.** | **high** |
| lobby `git ls-tree origin/main Projects/sudo-project-skeleton` vs `<skeleton> git rev-parse origin/main` | `6c76fd97…` vs `4510e05` — `git diff --stat` between them: `15 files changed, 1260 insertions(+), 7 deletions(-)` | The lobby records a skeleton **3 commits and 1,260 lines stale** — SCC-441 merged there and the pointer never moved. The detector would read the wrong tree on every machine but this one. Same class as the `sudo-command-center` pointer closed this morning. **Baked** (new Part C). | **medium** |
| this plan · `## Verification` final paragraph | "The skeleton's PR lands first — the detector goes RED until it does." | The stated order leaves the detector red on `main`, because what the detector READS is the **pointer**, which lives in the lobby PR. **Baked** — the lobby PR carries the detector AND the bump, so there is no window. | **medium** |
| `acli jira workitem view SCC-459` | an `INTENDED OUTCOME` paragraph, no `ACCEPTANCE` block | The Scope Ledger's precondition is met by the PLAN's nine-row table rather than the ticket's. Non-blocking; recorded so the next reader does not re-derive it. | **low** |

### Observations

- Nine `worktree-agent-*` local branches exist in the lobby with no worktrees. Unrelated to this
  lane; not a finding, and not this lane's to prune.
- `mint-push-token.sh` and `pre-push-main-approval.sh` reaching parity is worth doing for the
  detector's sake, but the plan should not claim it fixes a defect — it does not, and the plan
  already says so.
- AviationChat's guards carry a provenance header and are still 32-45 lines divergent on two files;
  the header made drift *visible*, which is exactly why its drift is small and the skeleton's is not.

### Sibling landing-order dependencies

None inside the lobby. **Cross-repo:** skeleton PR → lobby PR (which carries the detector *and* the
pointer bump together, per the baked fix above).

Audit verdict: GO
