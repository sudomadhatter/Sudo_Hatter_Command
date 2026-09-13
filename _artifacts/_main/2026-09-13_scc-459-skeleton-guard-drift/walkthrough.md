# SCC-459 — the skeleton's guards were a hand-shortened copy, and nothing compared them

**Lane:** `chore/SCC-459-skeleton-guard-drift` · **Repos:** `Sudo_Hatter_Command` (this lane) and
`Projects/sudo-project-skeleton` (its own PRs #2 and #3, both merged)
**Plan:** [implementation_plan.md](implementation_plan.md) · **Ticket:** [SCC-459](tickets/SCC-459.md)

---

## What was wrong

`Projects/sudo-project-skeleton` is the repo every new project is cloned from. Four of its git-hook
guards were **hand-shortened copies** of the command centre's, and nothing in any repo compared
them. Measured 2026-09-13 against `origin/main` of all three repos, counting only lines that
execute:

| guard | lobby | AviationChat | skeleton |
|---|---|---|---|
| `merge-target-guard.sh` | 169 | 169 | **124** |
| `mint-push-token.sh` | 90 | 90 | **72** |
| `pre-push-main-approval.sh` | 115 | 116 | **95** |
| `pre-push-merge-backstop.sh` | 94 | 87 | **73** |
| **total** | **468** | **462** | **364** |

AviationChat tracked the lobby line-for-line; the skeleton was **104 executable lines behind**. Two
of the four differed only in message text — diagnostically weaker, behaviourally equal — but three
gaps were real, and the first was live:

1. ⛔ **The skeleton told the reader to run `git reset --hard`.** `pre-push-merge-backstop.sh`'s
   refusal banner printed `git reset --hard origin/$1` — the pre-SCC-180 text. On 2026-08-15 an
   agent read that banner as the instruction it looks like, ran it in a shared checkout, and
   destroyed three sessions' uncommitted work. The lobby's copy prints `--keep`, offers `--soft`,
   and bans `--hard` by name. **Every new project was being handed the pre-incident instruction.**
   Not a missing line — a wrong one.
2. **The backstop scanned a narrower candidate set.** The lobby adds `refs/heads/epic` when the lane
   being pushed is a `chore/*`; the skeleton had no `SCOPES` variable at all, so a chore lane that
   fast-forwarded an epic carried that epic's unlanded commits to the remote with nothing looking.
3. **`merge-target-guard.sh` exited silently when it could not classify a merge.** No `UNJUDGED` /
   `ANY_NAMED` / `INCIDENT_SEEN`, no block saying why it declined or which backstop still covered
   it — so an unjudged merge was indistinguishable from an approved one. Gone with it: the SCC-97
   signature banner for chore-onto-sibling-chore, the exact shape of the 2026-08-11 production merge
   that printed success and was caught only by suspicion.

And a fourth, from the port checklist: the guards printed `.agents/rules/git-policy.md`, a path a
clone does not carry — its rules folder holds only an `INDEX.md`, by design.

**Separately, the setup half was broken in the mirror-image way.** `new-project.ps1` armed
`core.hooksPath` so the hooks *ran*, then created **no `*-ENFORCE` marker at all**, and named only
`JIRA-ENFORCE` in closing prose for the reader to `touch` by hand. A project that wanted enterprise
protection got warn-only gates and was told nothing.

---

## What shipped

### Part A — the four guards are a real port again (skeleton PR #2)

Each file is the lobby's at `a2642da2116ed96d21ee9d4bc03a3991a45f329e` with **exactly two declared
departures**: a provenance header (source path, source sha, and why the duplicate is compelled —
git runs hooks in the repo they gate), and four reworded rule citations naming the centre's rule
instead of a path the clone lacks. Code-only diff against the lobby is now those four lines; it was
197 deletions. Executable lines: **169 / 90 / 115 / 94 — exact parity.** `sh -n` clean on all six
hooks in the folder.

### Part B — the pointer bump (this lane, `e66329ba`)

`6c76fd97` → `18f55ab2`: **8 commits, 20 files, 2,096 insertions, 58 deletions.** The plan estimated
3 commits and 1,260 lines; the skeleton's own PRs landed in between. The span also carries the whole
of SCC-441 — the routed CI gate, both epic toggles, the ruleset recipes — which merged in that repo
as its PR #1 and had never been recorded here.

### Parts C and D — one question, two postures

Operator ruling: *"We add Jira, we have the full protections of an enterprise dev system. For no
Jira this is a quick dev project … it's just for fun and doing things quickly."*

| | Jira = yes | Jira = no (the default) |
|---|---|---|
| What it is | the full enterprise dev system | a quick project, for speed |
| `jira.conf` | written, site verified against `acli` before the clone | nothing written |
| The three `*-ENFORCE` markers | all three armed in the scaffold commit | none |
| Branches | `chore/<KEY>-<slug>`, the lane ceremony | `chore/<slug>`, or just commit on `main` |
| Reaching `main` | a pull request, the full gate | push it |

`/smh-new-project` asks both questions once and passes the answers to `new-project.ps1` as
arguments. The Jira answer is validated **before the clone** — same reasoning as the existing name
check, since a half-made project is worse than none.

Also wired: `scripts/rename-project.py`, which shipped in the skeleton from the start and which
**nothing ever called**.

### Part E — the acceptance rows are re-runnable

`test_repo_template.py` **T6** builds the two postures on **one repo shape**, so the markers are the
only difference. `test_command_surfaces.py` **CS-26** adds 10 rows over the door, the script and the
skeleton README.

⛔ **CORRECTION, made at close-out against evidence.** The plan's audit finding 2 said *nothing
anywhere tested `new-project.ps1`*, derived from `ls .agents/scripts/tests/test_new_project*.py`
returning *No such file or directory*. **That was wrong.** `test_teaching_edition.py` drives the real
script end to end through three cases — *named local skeleton becomes an independent project with
hooks and HEAD* · *successful scaffold prints project-local optional Jira setup* · *failed scaffold
commit cannot be reported as a created project*. All three went **red** on this lane's Part D and are
green now. A filename search is not a coverage measurement; the gate is. Part E still earns its
place — nothing covered the two postures or the door's interview — but the premise was overstated.

⛔ **CS-26's absent-submodule arm had to be rebuilt at close-out, and it was the very shape this
lane warns about.** The first cut failed outright when the skeleton was not checked out, on the
`pwsh` rule — *named and non-passing, never a skip*. That is right on a workstation, where
`git submodule update --init` complies. **A CI runner is the case that reasoning never met:**
`actions/checkout@v4` clones no submodules and several declared ones are private, so the remedy
there is not merely unrun but **unavailable** — and the row turned `main-write-gate` red on the lane
that introduced it, which is a check that can never be satisfied. It now follows SCC-118's existing
ruling (`t9_inconclusive`): **strict everywhere the remedy is actionable, inconclusive only on a
runner, keyed on the env var the platform declares rather than inferred from the symptom.** Both
arms proven by control, README restored byte-for-byte afterwards.

### Outside the plan, on the operator's word mid-build

`main-write-gate.yml` no longer runs on a draft PR, and fires on `ready_for_review`.
`test_main_write_gate_ci.py` pins the pairing as an implication with a mutant per half.

---

## Decisions

- **The source is the lobby, not AviationChat** — proven by AviationChat's own provenance headers,
  which name the command centre as their source. Both projects are consumers of the same files.
- **No automated parity detector in this lane** (operator ruling): *"keep this ticket direct and fix
  what's needed, not create something new."* An earlier draft added a port manifest, a
  `template_parity.py` and its test. Cut — it was new machinery that did not make a clone work.
- **The provenance header is the drift mechanism this lane ships, and it is evidence-backed.**
  AviationChat's copies carry one and sit 10 lines from the lobby; the skeleton's carried none and
  sat 197. Visibility on inspection is what the measurement says works.
- **No local ticket key for a boardless project.** An earlier draft invented a date-derived key.
  Struck on measurement: the guards classify a branch by PREFIX alone
  (`merge-target-guard.sh:158-167`), so `chore/nav-fix` behaves exactly as `chore/NOVA-7-nav-fix`.
- **The "no" posture needed no code**, and that was measured rather than asserted. This lane *names*
  it so a reader can tell a designed state from an unfinished one, then stops.
- **Arming is all three markers or none.** `JIRA-ENFORCE` alone gates commit messages while the
  merge guard and the main-push gate stay warn-only, silently — the half-armed shape.

## Pitfalls

- **A stamp can outlive the document it stamps.** `/smh-self-audit` ran once, into the first plan
  commit `91224cbc`, and four commits rewrote the plan while `Audit verdict: GO` sat unqualified.
  Worse, when the detector was cut I hand-edited that audit's own Scope Ledger paragraph — editing a
  check's findings instead of re-running the check. The operator caught it. The section was replaced
  wholesale, and the re-run found two high findings on surfaces the first audit never saw.
- **The door has FIVE surfaces, not two.** `.agents/commands/`, `.opencode/commands/`, and three
  **generated** launchers (`.agents/skills/`, `.claude/skills/`, `.roo/commands/`) that each embed
  the door's `description:` verbatim. `sync-agents` must re-run in the same commit. `CS-02` and
  `CS-18 Q` already pin this — mutant verified.
- **The Zoo launcher truncates a description at 135 characters** (`sync-agents.ps1:522-529`). The
  first emit shipped an ellipsis into the menu; the description was shortened to 128.
- **A submodule with `ignore = all` has no drift signal.** `.gitmodules:32` sets it on
  `sudo-project-skeleton`, so the pointer failing to move for eight commits never appeared in
  `git status`. The gap had to be measured deliberately.
- **A worktree's submodules are uninitialised.** `git submodule status` showed a leading `-` and the
  directory was empty; Part A would have edited nothing, or the wrong checkout.
- **`main-write-gate` was red by design for a lane's whole life.** It fails on one line —
  `[FAIL] close-out receipts` — because the PR road opens on the first push and the receipt is
  written here, at close-out. Seven identical failure emails on this lane before the operator asked.
  A check that is red by design trains its reader to ignore it.
- **Half the draft fix is worse than none of it.** A `draft == false` job filter without
  `ready_for_review` in the trigger types leaves a PR opened as a draft permanently unmergeable —
  PR #105's shape. The predicate is written as an implication so the *pairing* is what is pinned.
- **ABSENT and FAILED are different, and conflating them let Part D destroy what it improved.**
  The first cut of the rename call threw when `scripts/rename-project.py` was missing — *after* the
  clone, leaving exactly the half-made project the pre-clone checks exist to prevent. `-SkeletonUrl`
  is overridable, so the clone source is not guaranteed to ship it. Caught by three
  `test_teaching_edition.py` cases going red. Absent is now loud and non-fatal (and the closing
  report says the placeholders were not substituted); present-but-non-zero still throws.
- **A doc edit can break a generator anchored on its literal text.** The teaching-edition manifest
  carries a `lineTransforms` rule pinned to the SOP's `/smh-new-project` row, which this lane
  rewrote — so the export threw *"Line-transform anchor missing"* and four teaching-edition rows
  went red in CI. The anchor is now read **off the SOP itself** rather than retyped, since a
  retyped anchor is how an anchor drifts in the first place.
- **`json.dumps` escapes non-ASCII by default, and that silently half-applied the repair.** The
  manifest stores literal em-dashes; the escaped form matched nothing, so the `contains` key moved
  and the `replacement` did not — which would have shipped a stale door description to the public
  teaching edition. Caught by asserting both halves moved after re-parsing.
- **A test earned its keep on its first run.** `CS-26 J` caught the skeleton README and the door
  asking the two setup questions in different words — two paths meant to be indistinguishable. It
  also forced skeleton PR #3, because #2 had merged one commit earlier.

## Follow-ons

- **AviationChat carries 5 dead `.agents/rules/` paths** of the same class this lane fixed in the
  skeleton. Its armed commit-msg gate rejects an `SCC` key by design, so the repair needs an `AVCH`
  ticket. Named in the plan's `## Your Actions`.
- **An automated parity detector remains unbuilt, and is blocked on infrastructure rather than
  design:** the lobby's `main-write-gate.yml` checks out no submodules, so the skeleton is an empty
  directory on every runner, and the skeleton has no test harness at all. Either would have to be
  built first. Recorded in `living-template-sync.md`.

---

## Gates

```
run_all.py                            94/95   (workstation)
run_all.py  GITHUB_ACTIONS=true       95/95   (the runner's view — what CI sees)
workflow_lint.py --toolkit-only       0 errors, 0 warnings, 8 info
check_maps.py --depth3-only --strict  clean (no output)
declared_change_set.py parse          26 entries, 0 incomplete, ZERO NEW files
task_preflight.py                     0 errors, LANE: LOCAL, "clear to close out and merge"
test_command_surfaces.py              355/355
test_repo_template.py                 60/60
test_main_write_gate_ci.py            64/64
test_teaching_edition.py              74/74
```

⭐ **The one workstation red is `test_sops_prds_folder.py` T9, and it is not this lane's.** Its
failure message is **byte-identical** in the clean shared lobby at `a2642da2`. Two prose references
to `.agents/workflows/` — a surface SCC-394 retired — sit in accurate *historical* narration, and the
path resolver cannot tell a deliberately-dead citation from a broken one. It is inconclusive on a
runner by `t9_inconclusive`'s own ruling, which is why the runner column is 95/95 and why CI has
been green on it all along. Nothing was rewritten to silence it: the history is correct as written.

**Mutation evidence, every restore verified byte-for-byte:**

| mutant | rows it took down |
|---|---|
| revert one launcher's `description:` | `CS-02`, `CS-18 Q` — named the file |
| disarm the "yes" fixture | `T6` YES ×2 |
| leave the "no" fixture armed | `T6` NO ×2 |
| drop the workflow's draft filter | `skips a DRAFT pull request` |
| drop `ready_for_review` from the types | `a draft filter ALWAYS ships with ready_for_review` |
| remove the skeleton README, off a runner | `CS-26 J` — red, remedy named |
| remove the skeleton README, on a runner | `CS-26 J` — inconclusive, correctly green |

**No `Verdict:` stamp.** No `/smh-code-review` ran on this lane, so there is no review record to
cite and none is invented.

⭐ **The close-out found four defects the build had not.** Three were mine and are fixed above (the
rename guard, the manifest anchor, the `json.dumps` escaping); the fourth was CS-26's own
absent-submodule arm. All four were caught by gates going red, none by inspection — which is the
property this ticket exists to establish, applied to the ticket itself.

---

## Your Actions`.
- **An automated parity detector remains unbuilt, and is blocked on infrastructure rather than
  design:** the lobby's `main-write-gate.yml` checks out no submodules, so the skeleton is an empty
  directory on every runner, and the skeleton has no test harness at all. Either would have to be
  built first. Recorded in `living-template-sync.md`.

---

## Gates

```
run_all.py                            93/95 files passed
workflow_lint.py --toolkit-only       0 errors, 0 warnings, 8 info
check_maps.py --depth3-only --strict  clean (no output)
declared_change_set.py parse          24 entries, 0 incomplete, ZERO NEW files
test_command_surfaces.py              355/355
test_repo_template.py                 60/60
test_main_write_gate_ci.py            64/64
```

The two reds — `test_sops_prds_folder.py` T9 and `test_teaching_edition.py` — **reproduce
identically in the clean shared lobby at `a2642da2`** and are environment-bound: both need
submodules this checkout does not carry. Neither is this lane's.

**Mutation evidence, every restore verified byte-for-byte:**

| mutant | rows it took down |
|---|---|
| revert one launcher's `description:` | `CS-02`, `CS-18 Q` — named the file |
| disarm the "yes" fixture | `T6` YES ×2 |
| leave the "no" fixture armed | `T6` NO ×2 |
| drop the workflow's draft filter | `skips a DRAFT pull request` |
| drop `ready_for_review` from the types | `a draft filter ALWAYS ships with ready_for_review` |

**No `Verdict:` stamp.** No `/smh-code-review` ran on this lane, so there is no review record to
cite and none is invented.

---

## Your Actions

- [x] The merge itself — lands via this branch's PR
