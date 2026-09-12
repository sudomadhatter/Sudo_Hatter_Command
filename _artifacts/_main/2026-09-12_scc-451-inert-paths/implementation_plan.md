# SCC-451 — The inert-path exemption: one predicate for "does anything read this file at runtime"

**Goal:** a map file under a product folder stops being treated as a deployable product change, so
the standing-push doors accept it and the quick lane sizes its ceremony to the part of the diff that
actually ships. Today `frontend/scripts/INDEX.md` is refused by the push door and routed to a door
that refuses back, which is why the gate gets skipped by hand.

**Lane:** `chore/SCC-451-inert-paths` @ `4e2bbc89` (cut from `origin/main`, which was four PRs ahead
of the local `main` at `7d71c9a8`).

---

## Scope corrections found by measurement (before any code)

Three rows in the ticket cannot be built as written. Each is stated with what was measured and what
this plan does instead.

**1. The lobby has no `arm_rulesets.py`.** The ticket's receipt section says *"Applies to both repos:
the lobby's `arm_rulesets.py`, AviationChat's copy, and the skeleton's."* Measured:

```
find /home/dlohn/Sudo_Hatter_Command -name arm_rulesets.py
  Projects/sudo-project-skeleton/.agents/scripts/arm_rulesets.py
  Projects/AGY_AVIATIONCHAT/.agents/scripts/arm_rulesets.py
```

Two copies, neither in the lobby. The lobby's `.github/` holds `workflows/` and nothing else — it has
no rulesets to arm, because the lobby's `main` protection is the one ruleset nobody ever templated.
**The credential-free receipt is therefore not lobby work.** It belongs where the script lives, which
is AVCH-153's two repos. → **Recommendation: move the receipt rows from SCC-451 to AVCH-153**, whose
section 4 already owns the skeleton mirror. This plan does not build them.

**2. `Projects/sudo-command-center` is a submodule, and it is empty in this worktree.** Measured:
`.gitmodules` declares it with its own remote; `ls Projects/sudo-command-center/` in this tree returns
nothing, while the same path in the main checkout holds all four door bodies. A submodule's files
cannot ride a lobby commit. **The re-sync is a separate push to that repo**, done after this lane
lands so it copies the final text, and recorded in `## Your Actions`.

⚠️ **AUDIT FINDING 2 (baked): that re-sync splits in two, and only half of it is a port.** Measured
with `git diff --no-index --numstat` against the lobby masters:

```
cicd-non-crit-pr-push.md     7 / 7      placeholder lines only  -> mechanical re-sync
smh-non-crit-pr-push.md     10 / 10     placeholder lines only  -> mechanical re-sync
cicd-quick-dev.md          212 / 244
smh-quick-dev.md           404 / 235
```

The two quick-dev copies are not stale versions of the quick lane — that repo's
`smh-quick-dev.md:1-6` reads *"The TASK lane's dev cycle — assert-first development"*, which is the
`/smh-dev-task-tests` body filed under the quick-dev name. Replacing 400 lines of another repo
unreviewed is exactly what `port-checklist` exists to prevent. **This lane does not touch those two
files in that repo; they need their own ticket.**

**3. There is no mechanical runtime-loader detector, and this plan does not pretend otherwise.** The
ticket's guard *"nothing a runtime loader reads"* has no cheap implementation — finding
`backend/agents/greeting/agent.py:38` reading `knowledge/aviationchat_pitch.md` means parsing every
loader call in the repo. What actually protects that file is the **shape of the defaults**: they are
basenames (`INDEX.md`, `README.md`), and `aviationchat_pitch.md` matches neither. The risk is a
declaration widening to `*.md`, which would match the pitch, the rules and everything else. So the
guard is built at the **declaration** instead of at the scan: a bare-extension glob is refused at load
time with a printed reason. The pitch file is pinned as a control either way.

---

## The design

### One predicate, three functions, in `task_preflight.py` beside `PRODUCT_DIRS` (`:112-114`)

No new module — `code-standards` §2, and the four callers already import from here.

```python
DEFAULT_INERT = ("INDEX.md", "README.md")
SERVED_SEGMENTS = ("public", "static")      # a folder a web server hands out verbatim
LAW_PREFIXES = (".agents/rules/", ".agents/commands/")
INERT_REL = ".agents/inert-paths.json"

def load_inert(repo) -> tuple[str, ...]:
    """Globs for paths that sit under a product dir but nothing reads at runtime.
    Absent file -> DEFAULT_INERT. Malformed, unreadable, or carrying a bare-extension
    glob -> () — EMPTY, never a wide carve-out. This predicate fails toward ceremony."""

def inert_paths(repo, paths) -> list[str]:
    """The subset of `paths` that is inert. A path qualifies only if it matches a declared
    glob AND survives every hard guard: no SERVED_SEGMENTS segment, not under LAW_PREFIXES,
    and not INERT_REL itself."""

def deployable_paths(repo, paths) -> list[str]:
    """What still ships: the DEPLOY_DIRS prefix test, minus the inert subset. This is the
    function the four doors call; nobody re-implements the prefix test."""
```

**Why the guards run after the glob, not inside it.** A declaration can only ever *propose* a
carve-out. Served files, law files and the declaration itself are removed from the result no matter
what the file says — the same self-protection `scope_check.py:76-78` already applies to
`critical-surfaces.json` (*"a line that can widen itself is not a line"*). Three hard guards, three
pins.

**Why malformed returns empty rather than the defaults.** The plan this ticket came from said
malformed → defaults. That is wrong here and the ticket corrected it: a file that does not parse is a
file whose author's intent is unknown, and the safe reading of unknown intent is *no carve-out*. The
defaults are what an **absent** file means — absence is a decision, corruption is not.

**`PurePosixPath.match` is right-anchored**, proven on this interpreter in the prior session:
`frontend/scripts/INDEX.md` matches `INDEX.md`; `aviationchat_pitch.md` matches neither default;
`INDEX.md.bak` matches nothing. That is why the defaults are basenames and never extensions.

### `ceremony_tier(repo, paths, *, lines=None, structural=None) -> "tiny" | "quick" | "full"`

```
full   any path in critical-surfaces.json          (ABSOLUTE VETO, never overridden)
full   any path is a dependency manifest or CI config
full   any path matches ENTRY_POINT_GLOBS
tiny   the non-inert part is <= 50 lines across <= 5 files, and `structural` is False
quick  otherwise
```

**`lines=None` makes `tiny` unreachable, and that is the contract, not a gap.** The doors call this at
two different moments: quick-dev Step 1 has only a *planned* path set and no diff, while Step 5 and
both standing-push doors have a real one. A tier is never lowered on an assumption, so without line
evidence the best answer is `quick`. Pinned.

**The critical-surface veto reuses `scope_check.load_map()`** — it already parses the map, already
handles the unreadable case, and imports nothing from `task_preflight`, so there is no cycle.

**Entry points are a module constant, matched by pattern, and are never eligible for `tiny`.** This
is the most important line in the design and it is a hard exclusion, not a computation. Measured over
AviationChat's 146 frontend components: `app/layout.tsx` has a reverse-dependency reach of 0 and wraps
every screen in the app; `app/dashboard/page.tsx` has reach 0 and is an entire user journey. Nothing
imports a page — the router loads it — so any score built on reverse dependencies ranks the riskiest
files as the safest. SCC-452 replaces the line count with that score and **this exclusion still binds
there**, which is why it is a separate rule rather than part of the threshold.

```python
ENTRY_POINT_GLOBS = ("*/app/**/page.tsx", "*/app/**/layout.tsx", "*/app/**/route.ts",
                     "*/main.py", "*/asgi.py", "*/wsgi.py", "*/__main__.py")
MANIFEST_NAMES = ("package.json", "package-lock.json", "pyproject.toml", "poetry.lock",
                  "requirements.txt", "firebase.json", "next.config.ts")
```

⛔ The exact members are verified against both repos' trees at build time, not asserted from this
plan. A glob that matches nothing in either repo is dead config and gets dropped.

---

## Acceptance — every row is a command, and every row is seen RED first

| # | Statement | The assertion |
|---|---|---|
| A | `inert_paths()` answers the six measured paths correctly | `test_inert_paths.py::test_the_six_measured_paths` — `_my_resources/notes.md`, `_artifacts/_main/INDEX.md`, `docs/repo-map.md` are not deployable to begin with; `frontend/scripts/INDEX.md` and `backend/agents/INDEX.md` become inert; `frontend/src/components/Button.tsx` stays deployable |
| B | The served guard and the law guard each hold in both directions | `test_inert_paths.py::test_served_guard`, `::test_law_guard` — `frontend/public/INDEX.md` and `frontend/static/README.md` stay deployable even when declared; `.agents/rules/git-policy.md` is never inert; `frontend/scripts/INDEX.md` still is. Plus `::test_runtime_doc_control` — `backend/knowledge/aviationchat_pitch.md` is never inert under the defaults, and a `*.md` declaration is refused at load |
| C | The declaration cannot widen itself | `test_inert_paths.py::test_self_listing` — a fixture repo declaring `inert-paths.json` gets it back as deployable; a malformed file yields `()` not the defaults |
| D | An all-inert diff clears the standing-push door | the door's own fenced command, pasted, on `frontend/scripts/INDEX.md` → `no deployable path — carry on`, exit 0 (today: `HANDOFF`, exit 1) |
| E | Quick-dev's ceremony sizes to the non-inert part of a mixed diff | `test_command_surfaces.py` grep: both quick-dev bodies call `deployable_paths` at Step 1 and name the inert remainder; `test_inert_paths.py::test_mixed_diff` — one component + six INDEX files is a one-file ceremony |
| F | No dead end remains | `test_command_surfaces.py`: `cicd-non-crit-pr-push.md`'s HANDOFF line runs `epic_mode.py` and names `/cicd-quick-dev` for TRUNK; `test_ship_preflight.py` keeps the lobby handoff and gains the project case |
| G | `ceremony_tier()` returns `full` for a critical surface, a manifest and an entry point | `test_inert_paths.py::test_tier_vetoes` — three cases, each RED first |
| H | An entry point with reach 0 is NEVER `tiny` | `test_inert_paths.py::test_entry_point_never_tiny` — `frontend/src/app/layout.tsx` with `lines=3, structural=False` returns `full` |
| I | The four doors call `ceremony_tier`; nobody re-implements the threshold | `test_inert_paths.py::test_no_second_threshold` — grep the four door bodies for `50` / `<= 5 files` outside a call, and assert `ceremony_tier` appears in each |

**Control that must stay green:** `test_task_preflight.py`'s existing assertion that a product repo
still hands off the moment a diff touches `.github/` (`task_preflight.py:111` names it). The carve-out
narrows nothing about CI paths.

---

## The steps

1. **RED.** Write `test_inert_paths.py` with all nine groups above. Run `run_all.py` and paste the
   failures — every one must fail because the function does not exist or the guard is absent, not
   because of a typo in the fixture.
2. **GREEN, part one — the predicate.** `load_inert`, `inert_paths`, `deployable_paths` in
   `task_preflight.py`. Re-run.
3. **GREEN, part two — the tier.** `ceremony_tier`, `ENTRY_POINT_GLOBS`, `MANIFEST_NAMES`, the
   `scope_check.load_map` veto. Re-run.
4. **The four callers.** `check_scope` (`:1294`), `lane_qualify.py:148`, `ship_preflight.check_lane`
   (`:334`), and the two standing-push doors' fenced check. `test_lane_qualify.py:322-344` (N1) pins
   that the door body still names every member of `PRODUCT_DIRS + CI_DIR` and contains the strings
   `PRODUCT_DIRS` and `task_preflight` — the prose list at `:74-77` stays, only the fenced command
   changes.
5. **The two dead ends.** `cicd-non-crit-pr-push.md:73`'s HANDOFF reads `epic_mode.py` and names
   FULL/LIGHT → `/cicd-push-e2e`, TRUNK → `/cicd-quick-dev` then `/cicd-close-story-merge-tree` Arm B.
   `ship_preflight.py:339-343` keys on `surface` (already held at `:303`): empty → the lobby door as
   now, non-empty → the project door. `test_ship_preflight.py:260,270` pins the lobby case; it stays
   and gains the project case.
6. **The quick-dev ceremony sizing.** Both bodies' Step 1 computes the non-inert remainder and sizes
   Step 2/Step 3 to it; an all-inert diff short-circuits the plan + `approved` and the TDD, keeping
   the lean walkthrough and the Step 5 tripwire.
7. **The rule.** `artifacts-always-first.md` § "When to Skip" gains the inert exemption as a
   **mechanical** entry beside the existing prose one, naming `deployable_paths` as the test.
8. **Ports, maps and SOP, same commit.** The four `.opencode/commands/` mirrors re-mirrored
   (`git diff --no-index` exit 0); `workflows_testing_SOP.md` §5 (`:31`), §8a (`:1762`), §9a
   (`:116`, `:118`) and the refusals section, plus one changelog line — the SOP-currency gate demands
   they ride this commit because `.agents/commands/` and `.agents/scripts/` are usage surfaces.

   ⚠️ **AUDIT FINDING 1 (baked): `.agents/scripts/INDEX.md` rides this commit too.** Its
   `task_preflight.py` paragraph at `:68` states the lane derivation as *"the diff-vs-`origin/main`
   asks whether **this** change reached one. Touched ⇒ `HANDOFF`, hard exit 2,
   `/cicd-push-e2e`"* — this lane makes that false, because HANDOFF becomes *touched AND non-inert*.
   The `lane_qualify.py` paragraph at `:74` carries the same claim (*"Deployable comes from
   `task_preflight.PRODUCT_DIRS` by import"*). That map is how the next reader routes; leaving it
   describing the old predicate is how the dead end gets rebuilt.
9. **The floor.** `run_all.py` bare, `workflow_lint.py --toolkit-only`, `check_maps.py`,
   `check_links.py`.

---

## Declared Change Set

- EDIT `.agents/scripts/task_preflight.py` - `DEFAULT_INERT`, `SERVED_SEGMENTS`, `LAW_PREFIXES`, `INERT_REL`, `_GLOB_CANARIES`, `ENTRY_POINT_NAMES`, `ROUTER_DIRS`, `PY_ENTRY_NAMES`, `MANIFEST_NAMES`, `TINY_MAX_LINES`, `TINY_MAX_FILES`, `_norm_rel`, `load_inert`, `inert_paths`, `deployable_paths`, `all_inert`, `_is_entry_point`, `ceremony_tier`; `check_scope` calls the predicate → A, B, C, G, H
- EDIT `.agents/scripts/lane_qualify.py` - the `HANDOFF` hit list uses `deployable_paths` → A
- EDIT `.agents/scripts/ship_preflight.py` - `check_lane` uses `deployable_paths`; the handoff names the project door when the repo has a surface → A, F
- NEW `.agents/scripts/tests/test_inert_paths.py` - the nine assertion groups → A, B, C, D, E, F, G, H, I
- NEW `.agents/inert-paths.json` - the lobby's declaration; the canonical schema AVCH-153 clones → A, C
- EDIT `.agents/critical-surfaces.json` - the `ci` surface self-lists `inert-paths.json`, so editing the carve-out is a scope stop → C
- EDIT `.agents/scripts/tests/test_lane_qualify.py` - C3a/C3b: the carve-out at that caller, plus the served-folder control → A, B
- EDIT `.agents/scripts/tests/test_ship_preflight.py` - the project-case handoff assertion replaces the lobby one → F
- EDIT `.agents/scripts/tests/test_epic_mode.py` - the caller roster goes twelve → thirteen; the standing-push door is named → F
- EDIT `_artifacts/_main/INDEX.md` - this session's row (check 7) → A
- EDIT `docs/doc-graph.json` · `docs/doc-graph.md` - regenerated by `refresh_maps.py --repair` after the rule and SOP edits → A

**Deviations from the pre-approval set, and why.** `test_task_preflight.py` and
`test_command_surfaces.py` were declared and are **not** edited: every assertion they were to carry —
`check_scope` over an all-inert diff, the `.github/` control, the four-door greps and the TRUNK
routing line — is in `test_inert_paths.py` blocks D, F and I, where the subject lives. Splitting them
across three files would have put one predicate's pins in three places, which is the thing this
ticket is against. Four rows were **added**: the lobby declaration (the SOP names the path, and a
prose path that resolves nowhere fails `test_sops_prds_folder.py` T9), its self-listing row,
`test_epic_mode.py`'s roster count, and the two generated map files.

**Symbol drift after the build, and why.** The `task_preflight.py` row above is the post-review
list, not the pre-approval one. `ENTRY_POINT_GLOBS` **does not exist**: `PurePosixPath.match` is
right-anchored on whole components, so a fixed-depth glob list pinned exact segment counts and no
real App-Router handler (`app/api/<name>/route.ts`) could ever match it — replaced by
`ENTRY_POINT_NAMES` + `ROUTER_DIRS` + `PY_ENTRY_NAMES`, matched by filename inside a router folder at
any depth. `_GLOB_CANARIES` replaced a spelling blacklist that accepted `?*.md` and refused
`docs/*.md`. `all_inert`, `_norm_rel`, `_is_entry_point`, `TINY_MAX_LINES` and `TINY_MAX_FILES` are
new; each is named in the commit that added it with the defect it answers. **No file-level drift:
`git diff --name-only origin/main...HEAD` is 26 files, every one declared above except this plan and
its `task.yaml`.**
- EDIT `.agents/commands/cicd-non-crit-pr-push.md` - the fenced check calls `deployable_paths`; the HANDOFF line reads `epic_mode.py` → D, F
- EDIT `.agents/commands/smh-non-crit-pr-push.md` - the fenced check calls `deployable_paths` → D
- EDIT `.agents/commands/cicd-quick-dev.md` - Step 1 sizes the ceremony to the non-inert remainder → E, I
- EDIT `.agents/commands/smh-quick-dev.md` - same → E, I
- EDIT `.agents/rules/artifacts-always-first.md` - § "When to Skip" gains the mechanical inert exemption → E
- EDIT `.opencode/commands/cicd-non-crit-pr-push.md` - mirror → D
- EDIT `.opencode/commands/smh-non-crit-pr-push.md` - mirror → D
- EDIT `.opencode/commands/cicd-quick-dev.md` - mirror → E
- EDIT `.opencode/commands/smh-quick-dev.md` - mirror → E
- EDIT `.agents/scripts/INDEX.md` - the `task_preflight.py` and `lane_qualify.py` paragraphs state the lane derivation, which this lane changes (audit finding 1) → A, F
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` - §5, §8a, §9a, the refusals section → D, E, F
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` - one line → D

**Master count: 14** (the four `.opencode/` rows are mirrors, stripped by `review_scope.py`). Under
the 40-file split threshold, so this is one part.

**Not in this lane, and why:** the credential-free ruleset receipt (no `arm_rulesets.py` in the
lobby — correction 1), `Projects/sudo-command-center`'s re-sync (a submodule, correction 2), and
AviationChat's `.agents/inert-paths.json` (AVCH-153's repo, and it is blocked on this lane shipping
the schema).

---

## Verification

1. RED first, pasted: `run_all.py` on `test_inert_paths.py` before any edit to `task_preflight.py`.
2. `deployable_paths(repo, ["frontend/scripts/INDEX.md"]) == []`, and the same run's controls —
   `aviationchat_pitch.md`, `frontend/public/INDEX.md` and `.agents/inert-paths.json` all stay
   deployable.
3. The door's own fenced line, pasted, on the path that started this → `no deployable path — carry
   on`, exit 0.
4. `ceremony_tier` over the three veto cases and the entry-point case, each red then green.
5. `python3 .agents/scripts/tests/run_all.py` green — the whole lobby floor, bare.
6. `workflow_lint.py --toolkit-only`, `check_maps.py`, `check_links.py` green.

## Your Actions

- **Move the ruleset-receipt rows from SCC-451 to AVCH-153** (correction 1) — or say to leave them on
  SCC-451 as a cross-repo row and I will open the AviationChat lane separately.
- **`Projects/sudo-command-center`: the two standing-push doors re-sync** as their own push to that
  repo after this merges (placeholder lines only).
- **The two quick-dev doors in `sudo-command-center` hold the wrong command entirely** (audit finding
  2) — that repo's `smh-quick-dev.md` is the old `/smh-dev-task-tests` body. It needs its own ticket;
  say the word and I will mint it.
- **`origin/claude/teaching-edition` is eight days idle and shares four files with this lane** — this
  lane lands first and that branch resolves on top.

---

## Self-Audit (2026-09-12)

**Level:** LEDGER+BLAST — the declared set touches three gate scripts others import, four door
surfaces, one rule, the SOP, and files that exist in more than one repo. **Mode:** PRE-DEV.
**Subject:** this repo, `Sudo_Hatter_Command`, branch `chore/SCC-451-inert-paths` @ `4e2bbc89`.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every EDIT path exists; every NEW path is absent; the Declared Change Set parses;
             the plan's line anchors resolve to the text the plan claims; lane fit; both-sides
             commands; name collisions for the four new symbols; the Scope Ledger over the one NEW
read:        declared_change_set.py parse <this plan> -> "present": true, 19 entries, every bullet
               op-first, every bullet carrying a `→ <row>`
             all 20 EDIT paths present on disk; .agents/scripts/tests/test_inert_paths.py ABSENT
               (the one NEW)
             task_preflight.py:112-114 PRODUCT_DIRS / CI_DIR / DEPLOY_DIRS; :1244 deploy_surface;
               :1264 check_scope, whose HANDOFF at :1294-1299 reads
               `rep.err("scope", f"deployable path(s) changed: ...")`
             lane_qualify.py:148 `hits = [p for p in clean if p.startswith(PRODUCT_DIRS)]`
             ship_preflight.py:303 `surface = tp.deploy_surface(repo)`; :334-343 the light/handoff
               split ending `return "handoff"`
             cicd-non-crit-pr-push.md:62-68 the fenced check importing PRODUCT_DIRS + CI_DIR; :73-77
               "Any output starting `HANDOFF:` and this lane is over — route to /cicd-push-e2e"
             artifacts-always-first.md:318-325 "## When to Skip" and its four prose entries
             scope_check.py:61 MAP_REL, :76-78 the three self-listing rows, :141 load_map; its
               imports are argparse/json/os/sys/pathlib/wf_common — NO task_preflight, so the
               veto's reuse cannot cycle
             epic_mode.py --repo <this tree> -> "TRUNK" + "lands on main by a PR the operator
               merges" — the door's step-5 routing has a real source
             grep deployable_paths|inert_paths|ceremony_tier|load_inert across .agents/ .opencode/
               docs/ -> ZERO hits: no name collision, and nothing already claims these seams
             critical-surfaces.json: the `ci` key lists task_preflight.py, ship_preflight.py,
               scope_check.py and .agents/scripts/tests/ — this lane IS a critical surface, which is
               why it is on /smh-dev-task-tests and not the quick lane
verdict:     findings below (1, 4)
```

**Lane fit:** the declared set is `.agents/`, `.opencode/` and `docs/` only — zero deployable paths,
and `deploy_surface()` is empty in the lobby by construction. The close-out door is
`/smh-close-task-merge-tree`, which `task.yaml` already names. Correct door.

**Scope Ledger — every CREATE × the acceptance row that requires it:**

| NEW artefact | Required by | Caller count after the edit |
|---|---|---|
| `.agents/scripts/tests/test_inert_paths.py` | A, B, C, E, G, H, I | n/a — a test file is its own caller |

No empty acceptance cell. Caller counts for the new symbols, by grep after the edit:
`deployable_paths` → five (`check_scope`, `lane_qualify`, `ship_preflight.check_lane`, two door
bodies); `ceremony_tier` → four doors. Neither is a single-caller abstraction. `inert_paths` has one
internal caller plus the quick-dev remainder message — recorded as an Observation below, not a
finding: the ticket names it as the predicate and acceptance row A tests it directly.

**Scope Ledger precondition:** SCC-451 carries nine acceptance rows (A–I), each naming a concrete
observable. Met.

```
lens:        2 Parity + Blast
checks_run:  four-platform door parity; mirror byte-equality; cross-repo copies (port-checklist);
             twins; script callers in the hook dirs; rule pointers; the SOP/usage-surface rule;
             sibling worktrees and unmerged branches after a fetch; the code-graph risk seam
read:        git fetch origin (clean); git worktree list -> main @ 7d71c9a8 and this lane @ 4e2bbc89
               only. Two UNREGISTERED directories sit under .claude/worktrees/
               (SCC-439-retire-bmad-token-gate, scc-386-memory-long-term-only) that `git worktree
               list` does not report — stale dirs, not lanes; not touched by this plan
             git branch -r -> origin/main, origin/chore/SCC-431-zoo-remote,
               origin/claude/teaching-edition
             SCC-431: diff vs origin/main is FOUR files, all under _artifacts/ — zero overlap
             teaching-edition: 51 files, last commit 2026-09-04, overlaps this plan on
               docs/_scc_sops_prds/workflows_testing_SOP.md AND its changelog, plus
               .agents/scripts/INDEX.md and .agents/commands/INDEX.md -> finding 3
             mirrors: git diff --no-index .agents/commands/<door>.md .opencode/commands/<door>.md
               -> IDENTICAL for all four doors today; the plan re-mirrors all four
             platform doors: .claude/skills/<door>/SKILL.md exists for all four and is a THIN
               LAUNCHER ("GENERATED by sync-agents; do not edit", carries no steps) — it needs no
               edit unless a `description:` changes, and this plan changes none
             cross-repo: Projects/sudo-command-center is a SUBMODULE (.gitmodules, own remote) and
               is EMPTY in this worktree; populated in the main checkout. numstat vs the lobby
               masters: cicd-non-crit-pr-push 7/7, smh-non-crit-pr-push 10/10, cicd-quick-dev
               212/244, smh-quick-dev 404/235 -> finding 2
             Projects/sudo-command-center/.agents/commands/smh-quick-dev.md:1-6 reads
               "description: The TASK lane's dev cycle — assert-first development…" and
               "# /smh-quick-dev — The Task Lane's Dev Cycle (assert-first)" — that is the
               /smh-dev-task-tests body filed under the quick-dev NAME, not a stale quick lane
             hook callers: grep task_preflight|lane_qualify|ship_preflight in .githooks/ and
               .agents/scripts/git-hooks/ -> ONE hit, a comment in merge-target-guard.sh:163. No
               hook invokes these scripts, so no signature change can die on someone else's commit
             workflow_lint.py:70-90 _RULE_POINTERS — keyed on git verbs, worktree, Step 0 target,
               riders:/landing_mode:, and the port trigger. `artifacts-always-first` is NOT a
               pointer row, so editing that rule pulls in no pointer obligation
             .agents/scripts/INDEX.md:68 "…`deploy_surface()` asks whether the repo **has**
               `backend/ · frontend/ · …` at all …and the diff-vs-`origin/main` asks whether **this**
               change reached one. Touched ⇒ `HANDOFF`, hard exit 2, `/cicd-push-e2e`" -> finding 1
             risk_seam.py classify --repo <this tree> -> {"status": "unclassified", "tiers": {},
               "root": "<this worktree>"} — expected and permanent in the lobby (SCC-289: the centre
               is markdown and carries no code graph). Every judgement in this lens came from the
               diff and the tree
verdict:     findings below (1, 2, 3)
```

**Twins:** `cicd-*`/`smh-*` siblings exist for all four doors and the plan ports every change to
both, with the `.opencode/` mirror rows declared alongside. No divergence is introduced.

**SOP / usage surface:** `.agents/commands/` and `.agents/scripts/` are usage surfaces, so
`sop_currency.py` rejects the commit unless `workflows_testing_SOP.md` and its changelog ride it.
Both are declared. Verified against the measured SCC-441 pattern — this also means this lane cannot
run in parallel with any other lobby lane touching the same surfaces.

```
lens:        3 Pre-Mortem
checks_run:  the stale-map narrative; the other-repo narrative; the sibling-lands-after narrative —
             each attached to a finding an anchored lens already raised; nothing originated here
read:        finding 1: six months from now someone reads scripts/INDEX.md to learn how the lane
             question is answered, builds a fifth caller on "Touched ⇒ HANDOFF", and re-opens the
             dead end this ticket closes — the map outlived the code it describes
             finding 2: a mechanical "re-sync the ports" copies 404 lines of the WRONG command into
             a second repo unreviewed, and the next person to clone a command centre gets a
             /smh-quick-dev that is actually /smh-dev-task-tests
             finding 3: teaching-edition rebases onto a main that moved the SOP sections it also
             moved; the conflict lands on the operator's doorstep in a 51-file branch nobody has
             touched in eight days
verdict:     findings below (attached to 1, 2, 3)
```

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/scripts/INDEX.md:68` | "`deploy_surface()` asks whether the repo **has** `backend/ · frontend/ · …` at all … and the diff-vs-`origin/main` asks whether **this** change reached one. Touched ⇒ `HANDOFF`, hard exit 2, `/cicd-push-e2e`" | This lane makes that sentence false: HANDOFF will require *touched AND non-inert*. The map is the house's router for how the lane question is answered, and it is **undeclared** in the change set. **Baked** — added to the Declared Change Set and to step 8. | **high** |
| `Projects/sudo-command-center/.agents/commands/smh-quick-dev.md:1-6` · `git diff --no-index --numstat` | "The TASK lane's dev cycle — assert-first development" / `404 235` · `212 244` for the two quick-dev doors | The port-checklist demands the plan answer differing copies. Two copies differ by placeholders (7/7, 10/10) and are a mechanical re-sync; the two quick-dev copies hold **a different command entirely**. Re-syncing those inside this lane would be a 400-line unreviewed change to another repo. **Baked** — the port section below splits them and escalates the quick-dev pair to its own ticket. | **high** |
| `origin/claude/teaching-edition` @ `8b42390f` (2026-09-04) | overlapping paths: `docs/_scc_sops_prds/workflows_testing_SOP.md`, `…_changelog.md`, `.agents/scripts/INDEX.md`, `.agents/commands/INDEX.md` | 51 unmerged files, eight days idle, sharing four files with this plan. Landing order must be stated or the conflict is discovered at merge. **Baked** — landing-order section below. | medium |
| `.agents/commands/INDEX.md:56,58` | "\| **The quick lane** (a project; TDD kept, ceremony cut) \| `cicd-quick-dev` · `cicd-non-crit-pr-…`" | The routing table names the doors but describes no behaviour this lane changes, and no door is renamed or added. One row's phrasing ("TDD kept, ceremony cut") stays true. **No edit required** — recorded so the omission is deliberate rather than missed. | low |

### Observations (uncounted — belief, not check)

- `inert_paths()` has a single internal caller (`deployable_paths`) plus the quick-dev remainder
  message. It earns its name from acceptance row A, which tests the predicate directly, and from the
  ticket naming it. Worth re-checking at review if the remainder message does not materialise.
- The two unregistered directories under `.claude/worktrees/` (`SCC-439-…`, `scc-386-…`) are stale
  leftovers `git worktree list` does not report. Deleting them is an Ask-First action and is not
  this lane's business; flagged so the next `worktree prune` is not a surprise.
- `.agents/scripts/tests/` is itself on the lobby's critical-surfaces `ci` list, which is why this
  work is on the full Task lane rather than the quick lane. That is the map working as designed, not
  friction.

### Port section (port-checklist, the six checks) — files in more than one repo

| File | Copies | 1 git path as given | 2 printf | 3 verify file | 4 rules the target lacks | 5 both sides | 6 hooks / own key |
|---|---|---|---|---|---|---|---|
| `cicd-non-crit-pr-push.md`, `smh-non-crit-pr-push.md` | lobby · `.opencode/` (**byte-identical today**, verified) · `sudo-command-center` (7/7 and 10/10 — placeholder lines only) | n/a — a command body consumes no git output | n/a — no script output of its own | n/a — no file write | the command-center copy is a template for new centres and keeps its placeholders by design | the bodies print `python3` with the `(PC: python)` aside, kept verbatim | n/a — the template keeps its own key placeholders |
| `cicd-quick-dev.md`, `smh-quick-dev.md` | lobby · `.opencode/` (byte-identical) · `sudo-command-center` (**212/244 and 404/235 — the copy is the OLD `/smh-dev-task-tests` body under the quick-dev name**) | — | — | — | — | — | — |
| `task_preflight.py`, `lane_qualify.py`, `ship_preflight.py` | lobby ONLY — `find` confirms no second copy in any project; projects are thin and import nothing from here | n/a | n/a | n/a | n/a | stdlib only, no venv, both interpreter names | n/a |

⚠️ **AUDIT FINDING 2 (baked): the command-center port splits in two, and only half rides this work.**
The two **standing-push** doors differ by placeholder lines and re-sync mechanically — that is a
separate push to the `sudo-command-center` repo after this lane merges, recorded in `## Your
Actions`. The two **quick-dev** doors are not a port at all: that repo holds a different command
under the name, eight days stale, and replacing 400 lines of it unreviewed is precisely what the
port rule exists to prevent. **Escalated: it needs its own ticket, and this lane does not touch
those two files in that repo.**

### Sibling landing-order dependencies

- **`origin/claude/teaching-edition` → after this lane.** It shares `workflows_testing_SOP.md`, the
  SOP changelog, `.agents/scripts/INDEX.md` and `.agents/commands/INDEX.md`. This lane is a gate
  change and is small; teaching-edition is 51 files and idle. **This lane lands first and
  teaching-edition resolves on top.** If teaching-edition lands first instead, this lane re-cuts
  from the new `main` and the SOP hunks are re-applied — cheap, but it must be a decision rather
  than a surprise.
- **`origin/chore/SCC-431-zoo-remote`:** four artifact files, zero overlap. No dependency.

Audit verdict: GO
