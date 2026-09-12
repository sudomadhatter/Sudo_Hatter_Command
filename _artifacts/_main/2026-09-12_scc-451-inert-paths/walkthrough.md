review-runtime: fan-out

# SCC-451 — The inert-path exemption

**What changed for you:** you can push a map file again without skipping the gate. The standing-push
doors asked *"what folder is this in"*; they ask *"does anything read this file when the system
runs"*. `frontend/scripts/INDEX.md` now goes straight out, and `frontend/public/INDEX.md` — which is
served on production — still does not.

Lane `chore/SCC-451-inert-paths`, cut from `origin/main` @ `4e2bbc89`. PR
[#215](https://github.com/sudomadhatter/Sudo_Hatter_Command/pull/215).

## Task Checklist

- [x] **Plan + `/smh-self-audit`** — LEDGER+BLAST, three lenses, `Audit verdict: GO`, four findings,
      two baked into the plan before any code.
- [x] **RED first** — `test_inert_paths.py` written against a seam that did not exist;
      `AttributeError: module 'task_preflight' has no attribute 'deployable_paths'`.
- [x] **The predicate** — `load_inert` · `inert_paths` · `deployable_paths` in `task_preflight.py`.
- [x] **The tier** — `ceremony_tier`, `ENTRY_POINT_GLOBS`, `MANIFEST_NAMES`, the critical-surface veto.
      - ⚠ **Caught by the tests, in my own code:** the first draft read `scope_check.load_map` and
        ignored its error return, so an **unreadable critical-surfaces map fell through to `tiny`** —
        a fail-toward-permissive hole in the one rule described as an absolute veto. Now `full`,
        pinned.
- [x] **The four callers** — `check_scope`, `lane_qualify`, `ship_preflight.check_lane`, both
      standing-push door bodies.
- [x] **The two dead ends** — the door reads `epic_mode.py`; `ship_preflight` names the project door.
      - ⚠ **The plan was wrong about `ship_preflight`.** It said to key on `surface` (empty → the
        lobby door, non-empty → the project door). Measured: the empty case **returns earlier**, so
        that conditional was dead code. The second refusal is now unconditional and names
        `/cicd-non-crit-pr-push`.
- [x] **Quick-dev Step 1.5** — both doors size the ceremony and short-circuit an all-inert diff.
- [x] **The rule** — `artifacts-always-first` § When to Skip gains the mechanical exemption.
      - ⚠ Two hooks caught two real mistakes here: `test_permission_parity.py` H5 matched **my** new
        bullet instead of the LLM-approvals one because mine named that command first; and
        `refresh_maps.py` refused the commit because I wrote a live AviationChat path
        (`backend/knowledge/aviationchat_pitch.md`) into a lobby rule, where it resolves nowhere.
- [x] **Ports, maps, SOP** — four `.opencode/` mirrors byte-equal, `scripts/INDEX.md`,
      `_artifacts/_main/INDEX.md`, the SOP's §8a and lane table, one changelog line, the doc graph.
- [x] **The floor** — 92/92, lint 0/0, maps `[ok]`.
- [x] **Two holes in my own predicate, found before the review landed** (`6463df0a`).
      - ⚠ **The `lstrip("./")` scar, reproduced in new code.** `lstrip` takes a character *set*, so
        `.agents/rules/README.md` normalised to `agents/rules/README.md`, `LAW_PREFIXES` could never
        match, and **a rule file was declared inert** — `README.md` is one of the two defaults. The
        existing law-guard pin passed **vacuously** (it used files matching no declared glob, so it
        would have passed with the guard deleted). Now `_norm_rel()`, a loop, never a character set.
      - ⚠ **"nothing ships" was never the test for "all inert".** Both quick-dev doors read an empty
        `ships:` as the short-circuit past the plan, the literal `approved` and the RED/GREEN — and
        the lobby has no product dirs at all, so **every lobby diff satisfied it**, including an edit
        to the law. `all_inert()` asks the real question; an empty path list is `False`.
- [x] **The code review's six findings** (`b01dbe25`) — each reproduced by the lens in its own copy,
      each seen red as a pin here, then fixed; every one of the lens's own reproduction commands
      re-run on this tree afterwards. Detail in the Code Review section below.

## Evidence

**RED, before any implementation** — the seam did not exist, which is the right reason to fail:

```
AttributeError: module 'task_preflight' has no attribute 'deployable_paths'
  File "…/tests/test_inert_paths.py", line 113, in main
    got = tp.deployable_paths(repo, paths)
```

**GREEN** — `python3 .agents/scripts/tests/test_inert_paths.py`:

```
-- 94/94 passed --
```

46 at the first commit, 54 after my own two, 87 after the Edge Case Hunter's six, 94 after the
Test-Adequacy Auditor's five. Every added assertion was seen red against the code as it stood before
its fix — and for the last five, red against the specific mutant it exists to kill.

| # | Acceptance | The assertion that proves it |
|---|---|---|
| A | `inert_paths()` on the six measured paths | block A — all six, plus the control that `inert_paths` answers about the file rather than its folder |
| B | served guard and law guard, both directions | block B — `frontend/public/INDEX.md`, `frontend/static/README.md` and the trailing-slash form `frontend/public/` stay deployable **even when declared**; `.agents/rules/README.md` is never inert (a README, so the guard is the only thing holding — the first pin used files matching no glob and passed vacuously); a runtime-loaded doc survives `*.md`, `?*.md`, `[a-z]*.md` and `*[.]md` because each is refused against the canaries at load |
| C | the declaration cannot widen itself | block C — self-listing returns deployable; absent → defaults; **malformed → `()`**, and a map file hands off again while it is broken |
| D | an all-inert diff clears the door | block D (`check_scope` → `LOCAL`) **and live** below |
| E | ceremony sizes to the non-inert part | block E — one component + six INDEX files is a one-file ceremony, `tiny` at 12 lines where the raw 7-file count would not be; and the cap binds where nothing ships — block H, 40 lobby rule files at 10 lines → `quick` |
| F | no dead end remains | block F — the door names `epic_mode.py` and `/cicd-quick-dev`; `test_epic_mode.py` roster 12 → 13; `test_ship_preflight.py` SP-F now requires the project door and **refuses the lobby one** |
| G | `ceremony_tier` vetoes | block G — critical surface, manifest, CI config, **an unreadable map**, **a repo with no map at all** and **a map that declares nothing** (both through the same `GENERIC` fallback `scope_check` itself uses), each `full` at one line |
| H | an entry point is never `tiny` | block H — `app/layout.tsx`, `app/dashboard/page.tsx`, `main.py` at 3 lines → `full`; and six App-Router shapes at depth, where the fixed-depth globs failed — `…/app/api/chat/route.ts`, `…/app/(app)/dashboard/layout.tsx`, `…/app/(marketing)/blog/[slug]/page.tsx` among them; two controls, that `…/components/page.tsx` and `…/lib/page.helper.ts` are ordinary files; no line evidence → `quick`; structural → `quick` |
| I | the doors call the seam | block I — all four call `deployable_paths`, both quick lanes call `ceremony_tier`, none re-types `startswith(PRODUCT_DIRS` |

**Live, against the real AviationChat repo — the path that started this ticket:**

```
$ <the door's own fenced check> "<…>/Projects/AGY_AVIATIONCHAT" frontend/scripts/INDEX.md
carved out (inert): frontend/scripts/INDEX.md
no deployable path — carry on
```

Before this lane that printed `HANDOFF: frontend/scripts/INDEX.md` and exited 1, into a door that
refuses in TRUNK mode.

**The floor, bare:**

```
test_inert_paths.py              -- 87/87 passed --
run_all.py                       92/92 files passed          (exit 0)
workflow_lint.py --toolkit-only  -- 0 error(s), 0 warning(s), 8 info --
check_maps.py                    All maps & INDEXes agree with disk. [ok]
```

HEAD at the time of these runs: `b01dbe25` — re-measured after the review's fixes, not carried
forward from the first commit.

## Code Review (2026-09-12)

### Step 0.7 — re-derivation against the tree as it stands now

- **What moved under this lane:** `origin/main` advanced from `4e2bbc89` to `a2cbeb1a` (PRs 214 and
  216, both SCC-186 standing-push) and was merged into this branch at `0db93838`, bringing three
  files — `.vscode/settings.json`, `docs/migrations/vscode_sync/settings.json`, and one install
  guide. None is touched by this lane.
- **What that changes here:** nothing in the predicate, the tier, the callers or the doors. No file
  in the merge appears in this lane's 26-file diff, so there is no hunk either side could have
  resolved differently and no re-review of a merged region is owed.
- **What was re-measured after it, not carried forward:** the whole floor, on the merged tree —
  `test_inert_paths.py` 94/94, `test_ship_preflight.py` 121/121, `run_all.py` 92/92 files,
  `workflow_lint.py --toolkit-only` 0 errors, `check_maps.py` `[ok]`, plus all five mutants
  re-killed and the tree proven restored.

review-runtime: fan-out
lens_isolation: worktree
lenses_run:
- edge-case-hunter · ok
- test-adequacy-auditor · recovered-inline — killed mid-run by an operator interrupt after batch A (15 of 45 mutants); batch A's results were recovered from its transcript and every survivor was fixed and re-verified by the caller on the real tree
lenses_counted: 2/2
lenses_na: acceptance · n/a — skipped-by-mode (no-spec)
findings: 14 fix (0 dropped — no reproduction · 0 recorded)
dispositions: per-lens: edge-case-hunter=9/0/9 · test-adequacy-auditor=5/0/5 · incomplete=30 mutants never run (batch B onward) — the coverage gap is named in the verdict, not hidden
drift: none — `git diff --name-only origin/main...HEAD` is 26 files, every one declared in the plan's Declared Change Set except that plan and its `task.yaml`

**What the two lenses cost and bought.** The Edge Case Hunter found nine defects, each with a
reproduction it had already run in its own copy; two I had found independently an hour before, one
was half-fixed, six needed code. The worst was that the "absolute veto" on critical surfaces **did
not run at all in six of the nine projects** — `load_map` returns a falsy value for an unmapped repo
and the veto was written `if rows and overlaps(...)`, so Step 1 of `/cicd-quick-dev` called an auth
file critical while Step 1.5 called it `tiny`, in the same command.

The Test-Adequacy Auditor asked the different question — *do these tests catch a broken gate?* — by
mutating the source 45 ways. It is the reason this section is worth reading: **two of my pins were
vacuous**, passing with the guard they named deleted.

| id | the mutant | why the suite missed it |
|---|---|---|
| R4 | `ship_preflight: ships = changed` (predicate bypassed) | every case used a real source file or a path outside the product dirs; both route identically with the carve-out gone, so the lane's whole subject was untested at that caller |
| N5 | served-guard directory arm dropped | the pin used `frontend/public/`, which matches **neither default glob**, so it never reached the guard — it passed with the guard deleted |
| N9 | declared rows ignored, `GENERIC` always | every veto pin used `auth`, which the GENERIC fallback matches too, so the repo's own map was never the thing being read |
| R3 | `lines <= TINY_MAX_LINES` → `<` | every pin used 3 lines or 40+; the threshold was never tested at the threshold |
| N2 | `not g` dropped from the glob refusal | an empty glob was never declared, and `PurePosixPath(x).match("")` raises |

All five are fixed and **each was seen RED against its own mutant and green against the real code**,
by [verify_mutants.py](.claude/worktrees/SCC-451-inert-paths/_artifacts/_main/2026-09-12_scc-451-inert-paths/review/verify_mutants.py), which restores the file in a `finally` and re-runs both
suites to prove the tree came back:

```
KILLED | R4 · KILLED | R3 · KILLED | N2 · KILLED | N5 · KILLED | N9
-- restored tree --  test_inert_paths.py exit=0 · test_ship_preflight.py exit=0
```

⚠ **The coverage this review did NOT buy.** The Test-Adequacy lens was killed by an operator
interrupt 4 minutes into batch B. **Mutants 16–45 were never run.** Batch A's 15 results were
recovered from the lens's transcript rather than from a report it filed. The five survivors above
are what one third of the mutation set found; the remaining two thirds are unmeasured, and the
verdict below is CONCERNS for exactly that reason and no other.

Verdict: CONCERNS @ b01dbe25 — every finding from both lenses is fixed and re-verified, the floor is
green (94/94 · 121/121 · 92/92 files · lint 0/0 · maps ok), and the only open item is mutation
coverage: 30 of 45 mutants never ran. Re-run them in SCC-452's lane, which reopens this same
function.

## Your Actions

**What landed:** one predicate in `task_preflight.py` read by all four doors and both preflights; the
lobby's `.agents/inert-paths.json` as the canonical schema; `ceremony_tier` with the critical-surface
veto and the entry-point exclusion; two routing dead ends closed; the rule, the SOP and the maps in
the same commit.

**Decisions made while building, so you can overrule any of them:**

- A **malformed** declaration means *nothing* is inert, not the defaults. The pre-ticket plan said
  defaults; the ticket corrected it and I kept the ticket's version. Absence is a decision,
  corruption is not.
- The lobby **does** get an `inert-paths.json`, which the plan said it would not. Two reasons: the SOP
  names the path and `test_sops_prds_folder.py` T9 fails a prose path that resolves nowhere; and
  AVCH-153 must clone a file it can read rather than a shape it infers. It changes no behaviour here —
  the lobby has no deployable surface.
- `ceremony_tier`'s critical-surface veto reuses `scope_check.load_map` and `overlaps` rather than
  matching patterns itself. Two matchers would be two answers.

- [ ] **This is a PARTIAL landing — SCC-451 stays OPEN.** `task.yaml` declares
      `landing_mode: partial` with empty `riders:`, because neither open subtask's work is in this
      diff and a rider is a claim that it is. Step one — the predicate, the guards and
      `ceremony_tier` — is what landed.
      - **SCC-452** — step two: replace the line-count `tiny` arm with a measured
        reverse-dependency reach score. **Deliberately a subtask so SCC-451 cannot read Done before
        it lands**, and that guard is intact: this close flips no rider and leaves the parent open.
        It is the next `chore/SCC-451-<slug>` lane, with SCC-452 as its `riders:` entry.
        ⚠ The entry-point exclusion in `_is_entry_point()` must survive that lane — `app/layout.tsx`
        has reach **0** and wraps every screen, so a reach score alone would quietly re-admit every
        entry point to `tiny`.
      - **SCC-453** — the toolchain manifest (`code-review-graph` is a bare PATH command that
        silently fails to start on any machine where nobody installed it by hand). Different
        subject from inert paths; it is a subtask of SCC-451 only by mis-parenting. **Your call**
        whether it moves to SCC-33 or stays; it blocks nothing either way now.
- [ ] **`test_repo_template.py` has a git-maintenance race that reddens CI at random** — it hit run
      `34703459646` on this PR and passed on the identical re-run (1 red in 4 runs of the same code;
      my diff touches no template file). `sh("git","commit",…)` at `:82` makes git spawn
      `run_auto_maintenance()`, which creates and deletes `.git/objects/maintenance.lock`; `leaks()`
      at [test_repo_template.py:94](.agents/scripts/tests/test_repo_template.py#L94) walks the clone
      and calls `p.stat()` **outside** the `try/except OSError` that guards only `read_text()`, so a
      file that vanishes between `is_file()` and `stat()` escapes the block as a `FileNotFoundError`.
      **Remedy:** `git config gc.auto 0 maintenance.auto false` in the fixture's `git init` at `:74`
      — remove the cause, not the symptom. Not fixed here: it is outside this lane's subject and the
      review ran on a fixed diff.
- [ ] **Move the credential-free ruleset receipt from SCC-451 to AVCH-153.** The lobby has no
      `arm_rulesets.py` — both copies live in AviationChat and the skeleton, so that half cannot be
      built here. SCC-451 cannot close honestly while its description claims lobby work that does not
      exist.
- [ ] **Decide on `Projects/sudo-command-center`.** Its two standing-push doors differ from the
      masters by placeholder lines only and re-sync mechanically as a separate push to that repo. Its
      two **quick-dev** doors are a different command entirely — that repo's `smh-quick-dev.md` is the
      old `/smh-dev-task-tests` body, 404 lines out, untouched since 2026-09-04. That is its own
      ticket, not a row hidden inside this lane.
- [ ] **`origin/claude/teaching-edition` shares four files with this lane** (`workflows_testing_SOP.md`,
      its changelog, `.agents/scripts/INDEX.md`, `.agents/commands/INDEX.md`), 51 files, idle eight
      days. This lane lands first; that branch resolves on top.
