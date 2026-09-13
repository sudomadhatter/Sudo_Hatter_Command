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

### Two constraints, measured - they are why a detector is NOT in this lane

- **The lobby's CI does not check out submodules.** `main-write-gate.yml` uses a plain
  `actions/checkout@v4` with no `submodules:` key, so `Projects/sudo-project-skeleton` is an empty
  directory on every runner.
- **The skeleton has no test infrastructure at all.** `.agents/scripts/tests/` does not exist there -
  `ls` returns *No such file or directory*.

An automated parity gate could run in neither place without new CI config (an Ask First item) or a new
test harness in the skeleton. Both are real work with their own goal, and neither makes a fresh clone
function. This lane ships the header instead and leaves the gate to its own ticket.

## Decisions taken

1. **The source is the lobby, not AviationChat** — proven by AviationChat's own provenance headers.
   Both projects are consumers of the same lobby files.
2. **NO AUTOMATED DETECTOR IN THIS LANE - operator ruling, 2026-09-13:** *"keep this ticket direct
   and fix what's needed, not create something new. A clear goal: a standing project we can close,
   that is ready to go out of the box after set up."* An earlier draft added a port manifest, a
   `template_parity.py` checker and its test. That is new machinery, it does not make a clone work,
   and it serves a different goal. **Cut, and named as its own ticket in `## Your Actions`.**
3. **The provenance header is the drift mechanism this lane ships, and it is evidence-backed.**
   AviationChat's copies carry one and sit at 10 lines from the lobby; the skeleton's carry none and
   sit at 197. Visibility on inspection is what the measurement says actually works, it costs four
   comment blocks, and it creates nothing new to maintain.
4. **One lane, no subtasks.** Same repo pair, same lane class, strictly sequential. A ticket with
   no branch is a row nothing writes to.

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

## Part B — bump the lobby's skeleton pointer (AUDIT FINDING 3)

The lobby's `origin/main` records `6c76fd97` for `Projects/sudo-project-skeleton`; the skeleton's own
`origin/main` is `4510e05`. Between them: `15 files changed, 1260 insertions(+), 7 deletions(-)` —
the whole of SCC-441, merged in that repo as its PR #1, never recorded here. **The detector reads the
pointer, not this machine's checkout**, so without this bump it is green here and red everywhere
else.

⚠️ **AUDIT FINDING 4 (baked) — the landing order changes.** The lobby PR carries the detector **and**
this bump in one commit, and lands **after** the skeleton PR. There is then no window in which `main`
holds a detector pointed at a pre-repair tree.

---

## Part C — one question, two postures (operator ruling, 2026-09-13)

> *"We want this simple. We add Jira, we have the full protections of an enterprise dev system. For
> no Jira this is a quick dev project and we are not worried about prod or anything else — it's just
> for fun and doing things quickly."*
> *"no Jira no PRs I have no problem with that … so now we don't need a local ticket."*
> *"the agent ask at the beginning; if they say no it tells them they can change this at any time and
> drops it. there is no nag."*

**One question at setup sets the whole posture. There is no third state and nothing to configure.**

| | **Jira = yes** | **Jira = no** (the default) |
|---|---|---|
| What it is | the full enterprise dev system | a quick project, for fun and speed |
| `jira.conf` | written, `JIRA_SITE` + `JIRA_KEYS`, `acli` site verified to match | **nothing written** |
| The three `*-ENFORCE` markers | **all armed by setup** | **none** |
| Branches | `chore/<KEY>-<slug>`, the lane ceremony, the PR road | `chore/<slug>`, or just commit on `main` |
| Reaching `main` | a PR, the full gate | **push it** |

### Why the "no" side needs NO code — measured

An unarmed gate is already frictionless, by construction:

- `pre-push-main-approval.sh:38` — `[ -f .agents/scripts/git-hooks/MAIN-PUSH-ENFORCE ] || exit 0`.
  No marker, instant exit 0. No token, no prompt, nothing.
- `merge-target-guard.sh:10` and `pre-push-merge-backstop.sh:57` — same shape; without the marker
  they warn at most and never block.
- `jira.conf.example` — *"no jira.conf means no keys to check, so commits pass untouched."*

⭐ **So the quick-dev posture is what the skeleton already does today.** This lane does not build it;
it **names** it, so a reader knows it is the designed state rather than an unfinished one — and then
stops, per the ruling: one sentence, *"No board. You can add one any time — copy
`.agents/jira.conf.example` and follow its four steps"*, and drop it. No nag, no file, no key.

⭐ **"We can turn this on at any time" is a property of the design, not a promise.** Switching
postures later is: write `jira.conf`, verify the site, `touch` the three markers. Nothing has to
be undone first, because the "no" posture wrote nothing — which is exactly why it writes nothing.

### The "yes" side is the half that is actually broken

**Nothing arms the markers — ever.** `new-project.ps1` arms `core.hooksPath` (via
`Arm-HooksInclude.ps1`) so the hooks *run*, then creates no marker at all, and its closing text names
only `JIRA-ENFORCE`, in an optional block, for the reader to `touch` by hand. All three markers are
absent from the skeleton while present in the lobby and AviationChat. **So a project that answers
"yes" and wants enterprise protection still gets warn-only gates, silently.** That is the fix Part C
ships: on a "yes", setup arms all three.

### No key is needed on the "no" side, and none is invented

An earlier draft of this plan invented a local date-derived key so a boardless project had something
to name branches after. Struck — the guards classify a branch by its PREFIX and nothing else
(`merge-target-guard.sh:158-167`: `main` / `epic/*` / `chore/*` / `claude/incident-*` / `claude/*`),
so `chore/nav-fix` behaves exactly as `chore/NOVA-7-nav-fix` does, and `mint-push-token.sh` already
prints `${KEY:-<no key>}`. Nothing needs a key.

### The mode: TRUNK is already automatic

`epic_mode.py:5` — `TRUNK  no origin/epic/* at all`. A fresh clone has no epic branches, so it is
trunk from the first commit with no configuration. Adding Jira later does not change that either;
`LIGHT` and `FULL` arrive when someone cuts an `epic/<KEY>-…` branch, which is a choice, not a
migration.

---

## Part D — the setup interview, and the README as the agent's brief

**Two questions, asked once, at clone time.**

1. **What is the project called?** → run `scripts/rename-project.py`, which substitutes it across the
   **24 files** carrying `{{PROJECT_NAME}}` / `{{USER}}` / `{{PLACEHOLDER}}`. ⭐ That script
   **already exists in the skeleton and `new-project.ps1` has never called it** — the rename is
   documented as manual README step 2 and nothing automates it. Part D wires it.
2. **Do you have a Jira board for this project?**
   - **Yes** → write `jira.conf`, set `JIRA_SITE` + `JIRA_KEYS`, run `acli jira auth status` and
     **require the site it prints to match** (`smh-new-project.md:55-58` — a key prefix alone is half
     an address), then arm **all three** markers.
   - **No — the default** → say the one sentence and stop. Write nothing, arm nothing, ask nothing
     again.

⚠️ **AUDIT FINDING 1 (baked) — this door has FIVE surfaces, not two.** `ls` finds
`.agents/commands/`, `.opencode/commands/`, `.agents/skills/smh-new-project/SKILL.md`,
`.claude/skills/smh-new-project/SKILL.md` and `.roo/commands/smh-new-project.md`. The last three are
generated (*"launcher (GENERATED by sync-agents; do not edit)"*) and each embeds the door's
`description:` frontmatter verbatim. Part D changes what the door does, so that description changes
and three menus would advertise the old behaviour — SCC-66's scar, where a door edit orphans the
platform caches. **Re-run `sync-agents` in the SAME commit** and stage the three regenerated files;
they are declared below.

### The README is rewritten FOR THE AGENT

The skeleton's `README.md` is eight manual steps written for a human (`### 1. Clone` … `### 8. Initial
Commit & Push`, with `## Jira Integration (Optional)` at `:126`). It becomes the brief for **the agent
that sets up the clone**: the two questions first, the two postures table, what each answer arms, and
the one sentence said on a "no". The manual steps stay beneath as the fallback. A clone set up by
hand, by `/smh-new-project`, or by an agent that only read the README must land in the same state.

⚠️ **Out of lane, named once with its remedy:** `epic_mode.py:110` still says *"the skeleton every new
project clones ships no classifier either"*. SCC-441 landed the routed gate and both epic toggles
there, so that sentence is now false. One-line docstring correction, riding Part D's commit.

---

## Part E — the cases that make G, H, I and J re-runnable (AUDIT FINDING 2)

⚠️ **Without this part, the four rows that prove the whole ticket are a one-time transcript.** Zero
`NEW` rows also meant zero new tests, and `ls .agents/scripts/tests/test_new_project*.py` returns *No
such file or directory* — nothing anywhere exercises `new-project.ps1`, which has ten callers. The
pre-mortem is the ticket's own disease one level up: six months on, the interview silently stops
arming the markers on a "yes" and the suite stays green because nothing ever asked.

**The harness already exists, so this adds no file.** `test_repo_template.py:485-490` builds fixture
repos with `gh.make_repo(...)` and already asserts
`(armed / ".agents/scripts/git-hooks/MERGE-TARGET-ENFORCE").is_file()` against an `arm=False`
control — the exact shape acceptance G and H need. Cases are added to **existing** files:

- `test_repo_template.py` — the two postures: a "yes" fixture carries all three markers and refuses
  both a wrong-target merge and an untokened push to `main`; a "no" fixture carries none, writes no
  `jira.conf`, and pushes to `main` with no token and no prompt. **Both halves, per that file's own
  rule** — asserting only that the legal path succeeds is satisfied by a repo running no hook at all.
- `test_command_surfaces.py` — the door asks both questions, names all three markers on the "yes"
  branch, calls `scripts/rename-project.py`, and says the one sentence on the "no" branch; and the
  skeleton README names the same two questions and the same three markers, which is acceptance J.

⛔ **Each case is seen RED first** — against the current door and the current fixture, before Part C
and Part D are written.

---

## Acceptance

| # | Statement | Check |
|---|---|---|
| A | The skeleton no longer instructs `git reset --hard` | `grep -c 'reset --hard' <skeleton>/.agents/scripts/git-hooks/pre-push-merge-backstop.sh` → `0`, seen non-zero first |
| B | The skeleton's backstop scans `epic/*` for a chore lane | `grep 'refs/heads/epic' …/pre-push-merge-backstop.sh` resolves, seen absent first |
| C | An unclassifiable merge source is reported, not silent | the declined-to-judge block present; a fixture merge with an unnamed source prints a reason |
| D | No guard names a rule path the target lacks | `grep -c '\.agents/rules/' <skeleton>/.agents/scripts/git-hooks/*.sh` → `0`, seen `2` first |
| E | The four guards are at parity with the lobby | code-only counts (`grep -vE '^\s*(#\|$)' \| wc -l`) read **169 / 90 / 115 / 94**, matching the lobby exactly; seen 124/72/95/73 first |
| F | Every guard says where it came from | each of the four carries a provenance header naming its lobby path and the source sha; `grep -c` → 4, seen `0` first |
| G | ⭐ **"Yes" gets the enterprise system** | a fixture setup answering yes: all three `*-ENFORCE` markers exist, `jira.conf` written and the `acli` site verified; a wrong-target merge is refused with `exit 1` and a push to `main` without a token is refused. Seen warn-only first |
| H | ⭐ **"No" gets a quick project, with zero friction** | a fixture setup answering no: no `jira.conf`, no markers, and a commit pushed straight to `main` succeeds with no token and no prompt. Plus: grep proves no door, guard or hook emits a board-absence warning anywhere |
| I | The rename actually runs | `scripts/rename-project.py` is invoked by the setup; zero `{{PROJECT_NAME}}` / `{{USER}}` / `{{PLACEHOLDER}}` tokens remain in the 24 files afterwards, seen non-zero first |
| J | The README briefs the AGENT | the two questions are its first section with both postures; a setup done from the README alone lands in the same state as one done by `/smh-new-project` (test asserts both name the same two questions and the same three markers) |
| K | Nothing else moved | `run_all.py` green; `workflow_lint --toolkit-only` 0 errors; `check_maps --depth3-only --strict` clean |

## Declared Change Set

- EDIT `Projects/sudo-project-skeleton/.agents/scripts/git-hooks/pre-push-merge-backstop.sh` — the `--keep` remedy, the `epic/*` scope, the declined-to-judge note, the provenance header → A, B, E, F
- EDIT `Projects/sudo-project-skeleton/.agents/scripts/git-hooks/merge-target-guard.sh` — the declined-to-judge path, the SCC-97 banner, the reworded rule references, the provenance header → C, D, E, F
- EDIT `Projects/sudo-project-skeleton/.agents/scripts/git-hooks/mint-push-token.sh` — refusal text to parity, the provenance header → E, F
- EDIT `Projects/sudo-project-skeleton/.agents/scripts/git-hooks/pre-push-main-approval.sh` — refusal text to parity, the reworded rule reference, the provenance header → D, E, F
- EDIT `Projects/sudo-project-skeleton/README.md` — the AGENT's brief: the two questions, the two-posture table, what each answer arms, the sentence said on a "no" → G, H, I, J
- EDIT `Projects/sudo-project-skeleton/.agents/scripts/INDEX.md` — `:7` says "ships disarmed" of Jira ONLY; say it of all three, and that this is the quick-dev posture → H, J
- EDIT `.agents/commands/smh-new-project.md` — the two-question interview; on yes arm all three markers; on no, one sentence and stop → G, H, I, J
- EDIT `.opencode/commands/smh-new-project.md` — mirror → J
- EDIT `.agents/scripts/new-project.ps1` — ask both questions; call `scripts/rename-project.py`; on yes arm all three markers; on no write nothing → G, H, I
- EDIT `.agents/scripts/epic_mode.py` — `:110` claims the skeleton ships no classifier; SCC-441 landed one → J
- EDIT `.agents/rules/living-template-sync.md` — the provenance header is the skeleton's drift-visibility mechanism; no automated detector yet → F, K
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — the two postures and the setup interview → J, K
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one row → K
- EDIT `.agents/skills/smh-new-project/SKILL.md` — regenerated by `sync-agents`, same commit (AUDIT FINDING 1) → J
- EDIT `.claude/skills/smh-new-project/SKILL.md` — regenerated, same commit → J
- EDIT `.roo/commands/smh-new-project.md` — regenerated, same commit → J
- EDIT `.agents/scripts/tests/test_repo_template.py` — the two-posture fixture cases (AUDIT FINDING 2) → G, H
- EDIT `.agents/scripts/tests/test_command_surfaces.py` — the door asks both questions and the README matches → I, J

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

1. RED first, pasted: `reset --hard` present · `refs/heads/epic` absent · the declined-to-judge
   block absent · `.agents/rules/` count `2` · both markers absent · code-only counts 124/72/95/73.
2. Repair Part A; the same commands, now green; counts `169/90/115/94`; four provenance headers.
3. Part B: the pointer bump, and `git ls-tree` on the lane showing `4510e05`.
4. **Acceptance H end to end — the quick posture.** Clone the skeleton into a scratch dir, run the
   setup answering **no**: zero placeholder tokens remain, no `jira.conf`, no markers, and a commit
   pushed straight to `main` succeeds with no token and no prompt. Paste the transcript.
5. **Acceptance G end to end — the enterprise posture.** Same clone, answering **yes** with a real
   key: all three markers armed, the `acli` site verified, a wrong-target merge refused with
   `exit 1`, and an untokened push to `main` refused. Paste both refusals.
6. The Part E cases seen RED against the current door and fixture, then green after Parts C and D;
   a mutant per case (disarm one marker on the "yes" path; make the "no" path write a `jira.conf`)
   with every restore verified byte-for-byte.
7. `run_all.py`, `workflow_lint --toolkit-only`, `check_maps --depth3-only --strict`,
   `check_links --base origin/main`.

**Two repos land separately, in this order.** The skeleton's files are its own repo and its own PR,
and land FIRST. The lobby PR then carries the setup changes and the Part B pointer bump together, so
`main` never points at a pre-repair skeleton.

## Your Actions

- **Approve or redirect this plan.** Nothing outside `_artifacts/` has been written.
- **Two things need your word specifically.**
  1. ✅ **RULED 2026-09-13 — audit finding 2 is settled, and the scope grew with it.** The switch is
     *who issues the keys*, not Jira on/off: local date-derived keys by default, trunk mode (already
     automatic), both non-Jira gates armed from the clone, and a two-question setup interview that
     records its answers. See Parts C and D. Nothing further is owed here.
  2. Whether AviationChat's 5 dead rule paths get an `AVCH` ticket now or wait. They cannot ride this
     lane — its commit gate rejects an `SCC` key by design (port check 6).
  3. Whether the **close-out ceremony running boardless** gets its own ticket. Part C makes the
     GUARDS board-independent, which is what the ruling asked for; running `/smh-close-task-merge-tree`
     on a project with no board is a separate job - nine lobby scripts take a key, and `jira_feed.py`
     already has `ACLI_UNREACHABLE` and a `need_board=False` path to build on.
  4. Whether the **automated parity detector** gets its own ticket, now that it is cut from here. The
     remedy is named and sized: a declared port manifest plus a checker, blocked today by the two
     measured constraints above, so one of those must be solved first. Until then the provenance
     header is what makes drift visible - the same mechanism that kept AviationChat at 10 lines.

---

## Self-Audit (2026-09-13) — RE-RUN, replacing the stale section

⛔ **The prior section was stale and is deleted, not amended.** It was written against the FIRST plan
commit `91224cbc`; four commits rewrote the plan after it (`1885cb97`, `58aa843f`, `d1122209`,
`84a71ecd`) while its `Audit verdict: GO` line sat unqualified. Worse, when the parity detector was
cut I **hand-edited that audit's own Scope Ledger paragraph** to say its three `NEW` rows were gone —
editing a check's findings instead of re-running the check. The operator caught it. Nothing below is
carried over; every line is re-derived against `84a71ecd`.

**Level:** LEDGER+BLAST (a command file, four hooks, two scripts, a rule, a usage surface, files in
two repos). **Mode:** PRE-DEV.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  the Declared Change Set parses; every EDIT path exists; every NEW path absent; lane fit;
             both-sides commands; the Scope Ledger re-run honestly at zero NEW rows
read:        declared_change_set.py parse -> "present": true, 13 entries, 0 incomplete
             NEW rows: NONE.  missing EDIT paths: none.  deployable-dir hits: none
             acceptance rows in the plan: 11, each with a pasted observable
             both sides: the four guards are `#!/bin/sh`; new-project.ps1 is pwsh, already the door's
               documented tool; no python fork added anywhere
verdict:     findings below (2)
```

⭐ **Scope Ledger — the table is EMPTY, and that is a complete result.** The ledger scores every
artefact a plan CREATES against the acceptance row requiring it; this plan's change set carries
**zero `NEW` rows**, so there is nothing to score and the over-engineering question is answered
structurally rather than by opinion. **Precondition:** eleven acceptance rows, each with a command or
an inspection. The TICKET still carries an INTENDED OUTCOME rather than a formal ACCEPTANCE block —
non-blocking, as at SCC-456.

```
lens:        2 Parity + Blast
checks_run:  the command-file row (all platform doors + commands/INDEX.md); the script row (callers,
             test, scripts/INDEX.md); the rule row; the gate/hook row (ships ARMED?); the SOP row
             (both halves, same commit); the >1-repo row (the port section, re-verified); sibling
             worktrees
read:        ⛔ SURFACES -> finding 1. `ls` finds FIVE smh-new-project surfaces, the plan declares TWO:
               .agents/commands/smh-new-project.md          (declared)
               .opencode/commands/smh-new-project.md        (declared)
               .agents/skills/smh-new-project/SKILL.md      (NOT declared)
               .claude/skills/smh-new-project/SKILL.md      (NOT declared)
               .roo/commands/smh-new-project.md             (NOT declared)
             the three launchers are generated - ".claude/skills/smh-new-project/SKILL.md:6
               `/smh-new-project - launcher (GENERATED by sync-agents; do not edit)`" - and each
               carries the door's `description:` frontmatter verbatim
             commands/INDEX.md names the door twice; test_twin_parity.py:177 carries its
               NOT_PAIRED row (`_ONE_SUBJECT + " (scaffolds a new project)"`), unaffected
             ⛔ TESTS -> finding 2. `ls .agents/scripts/tests/test_new_project*.py` -> No such file.
               new-project.ps1 has TEN callers (AGENTS.md, .agents/INDEX.md, the door,
               validate_teaching_edition.py, test_teaching_edition.py, hooks_armed.py,
               scripts/INDEX.md, two overlay tour docs, a migration guide) and no test of its own
             the fixture harness EXISTS: test_repo_template.py:485-490 builds repos via
               `gh.make_repo(...)` and asserts
               `(armed / ".agents/scripts/git-hooks/MERGE-TARGET-ENFORCE").is_file()` against an
               `arm=False` control - the exact shape acceptance G and H need
             test_repo_template.py reads FIXTURES, not the real skeleton (no `sudo-project-skeleton`
               reference in it), so nothing in the lobby suite goes red on this lane's skeleton edits
               - which is precisely why finding 2 matters
             epic_mode.py: 23 caller files, test_epic_mode.py exists, and it asserts NOTHING about
               the docstring line this plan corrects -> the one-line edit is safe. CLEARED
             hooks_armed.py names new-project.ps1 only in a COMMENT (`:70`), no code dependency. CLEARED
             SOP: sop_currency.py:72-77 lists `.agents/commands/` (.md), `.agents/scripts/git-hooks/`
               and `.agents/scripts/` (.py AND .ps1) as usage surfaces - so new-project.ps1 and the
               door BOTH demand the SOP in the same commit. The plan carries both SOP rows. CLEARED
             rule row: living-template-sync.md has 10 citers and is absent from workflow_lint's
               _RULE_POINTERS; editing a rule's body adds no pointer obligation. CLEARED
             siblings: git worktree list -> the shared lobby @ a2642da2 [chore/SCC-186-standing-push]
               and this lane. Neither declares a file in this plan's set. No landing-order dependency
             risk_seam.py: `unclassified`, permanent and correct for the command centre (SCC-289)
             port section: all six checks re-verified unchanged; the four guards are the same files
               the first audit saw, and Part A's scope did not move
verdict:     findings below (1, 2)
```

```
lens:        3 Pre-Mortem  (bounded - attaches narratives, originates nothing)
checks_run:  the stale-cache case; the never-re-run case; the re-audit case itself
read:        finding 1 -> the door is edited, the two declared surfaces land, and three generated
             launchers keep the OLD description in every menu that reads skills rather than commands
             - Claude, Codex, Antigravity and Roo. The door works; its advertisement lies. SCC-66's
             scar exactly ("a rename orphans four caches")
             finding 2 -> the lane proves G, H and I once, by hand, in a scratch directory, and the
             transcript goes into the walkthrough. Six months later new-project.ps1 is edited for an
             unrelated reason, the interview silently stops arming the markers on a "yes", and the
             suite stays green because nothing ever asked. That is the same failure this ticket is
             REPAIRING, one level up - the skeleton drifted for exactly this reason
             the re-audit itself -> a stamp that outlives the document it stamped is the generic form
             of both findings, and it is what the operator's question caught
verdict:     findings below (attached to 1, 2)
```

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `ls` over the five surfaces · `.claude/skills/smh-new-project/SKILL.md:6` | `/smh-new-project - launcher (GENERATED by sync-agents; do not edit)` and, in its frontmatter, `description: "Scaffold a new project workspace under Projects/ by cloning the thin skeleton — no vendored toolkit."` | The plan declares **2 of 5** surfaces. Part D changes what the door does, so its `description:` changes and three generated launchers go stale in every skills-reading menu. **Baked** — Part D re-runs `sync-agents` in the same commit and the three regenerated files join the change set. | **high** |
| `ls .agents/scripts/tests/test_new_project*.py` · `test_repo_template.py:485-490` | `No such file or directory` · `(armed / ".agents/scripts/git-hooks/MERGE-TARGET-ENFORCE").is_file() and not (bare / ...).exists()` | **Acceptance G, H and I describe fixture runs that nothing will ever re-run** — zero `NEW` rows also means zero new tests, and the change set declares no test at all. The harness already exists and already asserts on these exact markers. **Baked** — the cases are added to that EXISTING file, so the plan still creates nothing. | **high** |
| `sop_currency.py:72-77` | `(".agents/commands/", (".md",), …)` · `(".agents/scripts/", (".py", ".ps1"), …)` | Both the door and `new-project.ps1` are usage surfaces, so the SOP must ride the same commit. The plan already carries both SOP rows. **No action — recorded as cleared.** | cleared |
| `test_epic_mode.py` · `hooks_armed.py:70` | no `classifier` assertion · `see .githooks/post-commit and new-project.ps1` (a comment) | The `epic_mode.py` docstring correction breaks no pin, and `hooks_armed.py` has no code dependency on the script this plan edits. **No action — recorded as cleared.** | cleared |

### Observations

- The first audit's four findings re-checked against `84a71ecd`: the lane's submodule is still
  uninitialised (`-6c76fd97`, still baked in Part A step 0); the stale pointer is still 3 commits and
  1,260 lines (Part B); the landing order is still stated. The arming finding is **superseded** by the
  operator's ruling and is now Part C, correctly restated — it is no longer a finding but a design.
- Nothing in the lobby's suite reads the real skeleton, so this lane's Part A repairs are provable
  only by the fixture cases finding 2 asks for.

### Sibling landing-order dependencies

None inside the lobby. **Cross-repo:** skeleton PR → lobby PR (carrying the setup changes and the
Part B pointer bump together).

Audit verdict: GO
