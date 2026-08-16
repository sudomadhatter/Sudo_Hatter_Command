# SCC-164 — Command-surface correctness family: walkthrough

**Lane:** `chore/SCC-164-command-surface-family` · worktree `.claude/worktrees/SCC-164-command-surface-family` ·
cut from `origin/main` @ `a0aceaf` · LANE: LOCAL (this repo has no deployable surface) ·
manifest [task.yaml](task.yaml) declares thirteen riders · plan [implementation_plan.md](implementation_plan.md).

**review-runtime: fan-out** — probed at Step 0, before any code (lane rule 3, Part I's law on day one).
The independent PRE-WORK self-audit ran as a clean-context subagent and returned in ~14 min; a second
re-audit turn resumed the same agent with its context intact. Subagent spawn is LIVE in this session, so
the review's blind lenses fan out and a dead lens is a finding, not a `recovered-inline`.

**Plan approval:** operator, 2026-08-15, verbatim — *"perfect. approved"* — following the plan's rev 2
(§ STOP named the two calls it covers knowingly: B3 scoped per-file, and the live acceptance scoped to
SCC-163). The arming ruling was closed separately, quoted in § ARMING.

## Task Checklist

- [x] **Step 0–1.5 · plan, audit, approval** — plan rev 1 written on the lane; independent
      `/smh-self-audit` (PRE-WORK, FULL) returned **NO-GO** with 25 findings; all 25 adopted into the
      plan text as rev 2 (`7ac8f35`); re-audit of the touched phases returned **GO** with 6 further
      findings (F26–F31), all baked in. Operator approval received.
  - Finding that fought back hardest: **F4** — E3 as first written ("PASS/CONCERNS + a `dead` lens is a
    contradiction") would have made the engine's own designed end state unclosable. `step-01-review.md:398`
    raises the floor to CONCERNS when a lens stays dead after the inline retry — that IS the escape hatch
    § ARMING promises, and blocking it would have left `--no-verify` or a forged roster as the only ways
    out. Corrected to: PASS + dead blocks; CONCERNS + dead passes.
- [x] **Part 1 · SCC-170** — the consolidation rule becomes law, riders default, partial landing
- [x] **Part 2 · J / SCC-178** — gate_receipt stops counting its own output as dirt
- [x] **Part 3 · K / SCC-179** — mutation sweep gets a mechanical restore check
- [x] **Part 4 · A / SCC-165** — a bare `main` is a stale ref (**25** operands: 4 ruled local, 21 fixed)
- [x] **Part M · SCC-182** — a `cd` out of the workspace retargets every later relative path (discovered mid-lane, minted as Part M)
- [x] **Part 5 · B / SCC-166** — cicd-code-review gains its twin's two steps, ADAPTED (**6** personal-name lines, not the 2 the plan measured; AP twin re-diffed and restamped)
- [x] **Part 6 · H / SCC-176** — the plan-time port checklist (the sketched `\bport\b` key matched **7** unrelated bodies and none of the three; re-keyed on the phrase step 2 introduces)
- [x] **Part 7 · F / SCC-174** — jira_feed check stops blessing a forked Dev Record; the slug now has ONE source and three Task surfaces stopped typing it (the sweep found a case that never reached the code it named) ⛔ CUT LINE
- [ ] **Part 8 · C / SCC-171** — the token path as git gives it
- [ ] **Part 9 · G / SCC-175 + Part 12 · L / SCC-180** — no post-merge write to main; the `--hard` remedy
- [ ] **Part 10 · D / SCC-172** — three fail-opens in the main-write gate
- [ ] **Part 11 · E / SCC-173 + I / SCC-177** — the blind review recorded, enforced, sequenced

## Evidence

_Each acceptance item → the assertion that proves it, RED output then GREEN output. Filled in per part._

### Part 1 · SCC-170 — the consolidation rule becomes law   `e856a33`

| Acceptance | Assertion | RED → GREEN |
|---|---|---|
| the rule exists and every consolidating command cites it | `workflow_lint._RULE_POINTERS` gains a `work-consolidation` row | row added FIRST → lint exit 1 naming `smh-plan-task.md` and `smh-close-task-merge-tree.md` as pointing nowhere → `0 error(s), 0 warning(s)` once the bodies cite it |
| a parent whose children are all riders does not block | `test_task_preflight.py`, `landing_mode: partial` block (12 cases + 1 control) | **157/157** |
| the parent's index row survives its own edit | `test_jira_feed.py`, `index-row` block (6 cases) | **241/241** |

**The defect this part introduced, and what caught it.** The manifest key was first written as
`landing:`. `task.yaml` ALREADY has a `landing:` key — nested inside each `secondary_repos:` entry
(`independent-task` / `retain-on-epic`) — and `manifest_field`'s `^\s*` idiom matched the indented
line, so every cross-repo manifest read as declaring an unknown landing mode and **five green SCC-94
cases went red**. Fixed by renaming to `landing_mode` with a column-0-anchored regex (no `\s*`), and
the collision is now pinned as its own negative-control case. Nothing found it by review — the
pre-existing suite did, which is the argument for running the whole file rather than the new block.

**Guard hazard cleared while writing it.** The first anti-argparse guard read
`code == 2 and "invalid choice" not in out`; argparse actually emits `unrecognized arguments`, so the
assertion passed while the feature did not exist. Widened to `"usage: jira_feed.py" not in out`
(cf. `prose-pinning-guards-are-vacuous`).

### Part 2 · J / SCC-178 — gate_receipt stops counting its own output as dirt

**RED, captured before any edit** (`test_gate_receipt.py`, new `SCC-178` block, 4 of 9 failing —
each one printing the receipt directory as the dirt it was measuring):

```
[PASS] J0 the first stamp on a clean tree is clean (baseline, not the bug): paths=[]
[FAIL] J1 a tree whose ONLY dirt is a prior receipt is NOT dirty: paths=['_artifacts/_main/2026-08-15_j/gates/']
[FAIL] J2 dirty_paths never names a path under the receipt's own gates/: paths=['_artifacts/_main/2026-08-15_j/gates/']
[FAIL] J3f the story lane gets the same exemption (_bmad-output/gates/<story>/): paths=['_bmad-output/gates/']
[FAIL] J3g ...but ANOTHER story's receipts are not this writer's output: paths=['_bmad-output/gates/']
-- 39/43 passed --
```

**GREEN:** `-- 43/43 passed --`, and `test_task_preflight.py` **157/157** /
`test_task_preflight_receipts.py` **38/38** on the reader side (the consumers of `dirty_paths`).

| Acceptance | Assertion | Result |
|---|---|---|
| J1 only-dirt-is-a-prior-receipt → not dirty | `J1` | RED above → `paths=[]` |
| J2 `dirty_paths` never names the own gates dir | `J2` | `paths=[]` |
| J3 any OTHER path still DIRTY | `J3a` sibling file under `<root>/` · `J3b` modified code · `J3c` dirt elsewhere under `_artifacts/` · `J3d` a sibling merely NAMED like `gates` · `J3g` another story's receipts | all green, each naming the surviving path |
| J4 `smh-quick-dev.md` re-worded | the "commit first" line now says the receipt is not its own dirt | done, + the SOP's `gate_receipt.py` row |

**Found by the RED, not predicted by the plan: git COLLAPSES an untracked directory to one entry.**
A story lane whose whole `_bmad-output/gates/` is new reports the **ancestor**, not the writer's
`_bmad-output/gates/<story>/` — and that ancestor also holds *other stories'* receipts. A plain
prefix exemption could only have been wrong in one of two directions: too narrow (J3f stays red) or
too wide (J3g exempts somebody else's output). So ancestor entries are re-read with
`-uall` scoped by pathspec and filtered file-by-file. J3f and J3g are the two halves of that, and
`J3g` now reports `['_bmad-output/gates/21-8b/one.json', '_bmad-output/gates/21-8b/two.json']` —
the expansion visible in the assertion's own output.

**Mutation sweep** — the plan's two, plus two drawn from the code as written. All four killed by the
case named for them, and the restore verified by re-running the file green:

| Mutant | Must kill | Result |
|---|---|---|
| M1 widen the exemption to all of `_artifacts/` | J3c | KILLED (also took 9c, 9d) |
| M2 remove the exemption entirely | J1 | KILLED |
| M3 drop the trailing-slash dir-boundary anchor | J3d | KILLED |
| M4 exempt a collapsed ANCESTOR instead of expanding it | J3g | KILLED |

⚠️ The sweep's own restore check printed `⛔ DIRTY` on a correctly-restored file: it used
`git diff --quiet`, which compares to HEAD, while the fix under test was still uncommitted — the
normal state of every sweep. Recorded as an input to **Part 3 (SCC-179)**, whose whole subject is
that check: snapshot the pre-sweep content, never HEAD.

### Part 3 · K / SCC-179 — the sweep's rules stop being self-reported

**RED, captured before any code:** `-- 1/18 passed --` with `mutation_sweep.py` absent. Four of the
first-cut cases passed **vacuously** — a missing script also exits 2 and touches nothing, so
"an empty table is refused (exit 2)" and "the file was restored" were both true of a script that did
not exist. Tightened before building: the refusals now pin their *reason* text, and the
restore assertions are bound to output proving a sweep actually ran. RED after tightening: `1/18`.

**GREEN:** `-- 22/22 passed --`.

| Acceptance | Assertion | Result |
|---|---|---|
| K1 mechanical end-state check | `K5c` bytes · `K2e` nothing reached history · the pinned-sha diff | green |
| K2 residue fails the check | `K2b` survivor · `K2c` misattributed kill · `K2d` exit 3 · `K2f` silent runner · `K3c2` residue refused next run | green |
| K3 dirty start · interrupt · empty table | `K3a`+`K3a2` · `K3b`+`K3b2` (SIGTERM) · `K3c` (SIGKILL) · `K3d` · `K3e`/`K3e2` anchors | green |
| K4 full file runs unfiltered | `K4a`, and `K4b` reproduces 8681d83 exactly — every scoped case green, the full run red, the sweep fails | green |
| K5 clean sweep exits 0 | `K5a`/`K5b` | green |

**The design changed twice, both times because the sweep swept itself.**

*Round 1 — 0/8 killed.* Not one mutant died, and the reasons were four separate defects:

1. **`kills` was one field doing two jobs in two namespaces.** The harness *selects* by `c.block()`
   label; attribution *reads* the case name off the `FAILED:` line. Declaring `K2e` as the filter
   matched no block, the harness exited 3, and the sweep correctly refused to call it a kill. Split
   into `case` (attribution) and `block` (selection).
2. **K2c was vacuous** — its filter selected only the case the mutant does not break, so the run
   exited 0 and the assertion held whether or not attribution existed.
3. **K2d was too loose** — any "sweep error" satisfied it, so deleting the exit-3 clause fell through
   to the no-`FAILED:`-line branch and still read as an error.
4. **K3f did not exist.** Every fixture table held ONE mutant, so nothing noticed when the per-mutant
   restore was dropped.

*Round 2 — 7/10.* Three survivors, three more real defects:

5. **`judge` read `failed[0]`, the WRONG line.** This script's own suite spawns sweeps whose fixture
   runners print their own `FAILED:` lines, so the first one belongs to a nested process; the
   harness's own summary is printed **last**. A genuine kill was being reported as unattributable.
6. **A mutant that does not APPLY read as a kill.** With the restore dropped, the stale mutation
   keeps failing the same case and the sweep banks a second kill it never earned. The doctrine
   already said this ("a mutant that removes nothing is DEFECTIVE — a SKIP that counts as a
   survivor"); it is checked now because the symptom is silent.
7. **No case ever ran a runner that fails SILENTLY** — non-zero with no `FAILED:` line — so the whole
   attribution requirement could be deleted unnoticed. `K2f`.

*Round 3 — 10/11.* **M11 is a DOCUMENTED SURVIVOR, not an oversight.** It removes the
did-it-apply check, and no single-fault scenario can reach it: the check only fires when a restore
has *already* failed, and the restore is verified independently. It is kept as second-line defence
because the failure it converts is silent — a wrong answer that looks like a clean sweep — and it is
recorded here rather than deleted, because deleting the mutant that embarrasses the design is how a
sweep starts agreeing with itself.

Also fixed from reading the sweep's own output: the echoed tail of the full unfiltered run is now
prefixed `| `, because that tail is another process's output and can carry its own
`-- SWEEP FAILED --` banner directly above a passing verdict.

### Part 4 · A / SCC-165 — a bare `main` is a stale ref

**The count is 25, not the plan's 20.** The plan measured by hand at `a0aceaf`; the scan finds
four more `rev-list --left-right --count main...origin/main` sync-checks (which are **correct**
and become the allowlist) and one `merge-tree --write-tree --messages HEAD main` that the plan's
pattern list did not name. Leaving that last one would have been the vacuous shape: a guard
shipping green three lines above the identical live defect. `merge-tree` is now a scanned pattern.

**RED, captured before any edit** — `-- 22/23 passed --`, the one failure naming all 21:

```
[PASS] the scan read at least 10 command files (an empty glob is a FAIL): read 63 from .agents/commands
[FAIL] no command diffs, counts or cuts against a bare local `main`: 21 unruled operand(s)
      cicd-mobile-error-team.md:147  [range-left]  ... git diff main...claude/incident-<id>
      cicd-push-e2e.md:44            [range-left]  ... git log --oneline main..<branch> | head
      smh-code-review.md:81          [cmd-operand] BASE=$(git -C "$REPO" merge-base HEAD main)
      smh-code-review.md:85          [cmd-operand] ... merge-tree --write-tree --messages HEAD main
      smh-plan-task.md:158           [cmd-operand] ... worktree add ... -b chore/<SUBKEY>-<slug> main
      … 16 more …
      REMEDY: `origin/main` preceded by `git fetch origin main` in that command — or, if the line
      genuinely asks about the LOCAL branch, an ALLOWED row in this file carrying the reason.
```

**GREEN:** `-- 23/23 passed --`; full floor `31/31 files passed`.

#### ⛔ A2 — every hit, judged one by one

| File | Line | Operand | Ruling |
|---|---|---|---|
| cicd-mobile-error-team | 147 | `git diff main...claude/incident-<id>` | **FIX** — incident branches fork from main; the existing `fetch` named only the incident branch, so main was never refreshed. Fetch now names both |
| cicd-push-e2e | 44 | `git log --oneline main..<branch>` | **FIX** — `git fetch origin` already runs at :40 |
| cicd-push-e2e | 125 | `rev-list --left-right --count main...origin/main` | **ALLOW** — the `0 0` sync check; the left operand IS the question |
| smh-clean-code-audit | 60 | `diff --name-only main...HEAD` | **FIX** + a fetch (the command had none) |
| smh-close-task-merge-tree | 518 | `…main...origin/main` | **ALLOW** — sync check |
| smh-code-review | 58 | `diff --name-only main...HEAD` (Step 0.5) | **FIX** + a fetch — Step 0.5 runs *before* Step 0.7's fetch |
| smh-code-review | 81 | `merge-base HEAD main` | **FIX** — ⚠ it sits one line under `fetch origin main`, which updates `origin/main` and **not** local `main`. The fetch made it look safe |
| smh-code-review | 82 · 83 | `"$BASE"..main` · `main...HEAD` | **FIX** |
| smh-code-review | 85 | `merge-tree … HEAD main` | **FIX** — found by widening the scan, not by the plan |
| smh-code-review | 132 | prose: "the `main...HEAD` diff" | **FIX** — the table documents the input; stale prose re-teaches the defect |
| smh-label-tasks | 71 | `diff --name-only main...chore/<KEY>-<slug>` | **FIX** + a fetch — grounding a label on a stale diff reads a lane as touching files it does not |
| smh-merge-multiple-workingtrees | 81 · 89 | `rev-list --count main..<branch>` (+ its prose) | **FIX** + a Step 1 fetch |
| smh-merge-multiple-workingtrees | 139 · 140 | `…..main` · `main..."chore/…"` | **FIX** — the step is *titled* "Staleness against **current** `main`"; a stale base defeated its whole purpose |
| smh-merge-multiple-workingtrees | 150 | `diff --name-only main...<branch>` (overlap map) | **FIX** |
| smh-merge-multiple-workingtrees | 299 · 366 | `…main...origin/main` | **ALLOW** ×2 — both sync checks, after `checkout main` + `pull --ff-only` |
| smh-plan-task | 158 | `worktree add … -b chore/<SUBKEY>-<slug> main` | **FIX** — see below |
| smh-quick-dev | 73 · 118 | `worktree add … main` · `diff main...HEAD` | **FIX** |
| smh-quick-fix | 70 · 117 | `worktree add … main` · `diff main...HEAD` | **FIX** |
| smh-self-audit | 126 | `diff --name-only main...HEAD` | **FIX** + a fetch |

**Sighted, deliberately NOT fixed here:** `cicd-clean-code-audit.md:49`, `BASE=${BASE:-main}`. It is
not in operand position so the scan does not see it, and it is a *fallback* for a story lane whose
real base is its `epic/*` branch — B1's trap. It belongs to the cicd parts (5/6), not to A. **Closed in Part 6** — see *The A2 sighting, closed* below.

**⚠ The fix for `worktree add` is three lines, not one — and a blanket ref-swap would have been a
regression.** `smh-plan-task.md:117` already carried the correct idiom for the consolidated lane and
it says why: `git worktree add -b <lane> origin/main` **sets the new branch's upstream to
`origin/main`**, so a later bare `git push` from that lane targets **main**. Every fixed
`worktree add` now carries the fetch, the `origin/main` start-point, **and**
`git branch --unset-upstream`. Swapping only the ref would have traded a stale base for lanes
wired to push at main — a strictly worse defect, and the file that documented the hazard was one
of the three that still had it.

**A5 — rendered-step diff:** refs, the added fetches, and the two `--unset-upstream` lines. No step
gained, lost or reordered a behaviour. **A4 — arming:** `run_all.py` auto-discovers `test_*.py`
(`run_all.py:11,:43`), so the guard ships **BLOCKING** with nothing to register, per § ARMING.

**Mutation sweep** — the plan's three, plus one drawn from the code:

| Mutant | Must kill | Result |
|---|---|---|
| M1 re-insert a bare `main...HEAD` in a command | the live scan | KILLED |
| M2 widen the allowlist key to the file alone | `...one changed character does NOT inherit the exemption` | KILLED — ⚠ **not** by the case declared for it. Keying on the file alone also exempts the changed-character line in the SAME file, so that case fires first. The sweep refused the kill until the declaration matched the killer |
| M3 point the scan at an empty dir | the `≥ 10 files` floor | KILLED |
| M4 drop the `(?<![\w/.-])` guard | every `origin/main` re-lights | KILLED |

### ⚠️ Part 4 turned up a regression Parts 1–3 had already landed

`run_all.py` was **red at the lane tip** — `test_command_surfaces.py` and `test_suite_runner.py` —
and green on `origin/main`. Neither had been noticed, because Parts 1–3 ran their own files rather
than the floor. Two separate causes:

1. **The ORPHAN walker (`test_suite_runner.py`).** `test_gate_receipt.py` and `test_jira_feed.py`
   carried **zero** `c.block(` guards on `origin/main`, which kept them out of the walker's `wired`
   set entirely. Parts 1 and 2 each added **one** block — which opts the whole file in and exposes
   every legacy `c.check` as an orphan: 34 and 180 of them. A partially-wired file is the genuine
   hazard the walker names (an unguarded check runs under **every** `--case` filter and can be
   credited with a kill it did not make), so weakening the walker was not on the table. Both files
   are now fully wired into four named regions. Setup stays outside the guards; the multi-line
   string fixtures were left un-indented so no fixture text changed. Proof the wiring is behaviour-
   neutral: check names and verdicts **byte-identical** to the pre-wiring capture, `43/43` and
   `241/241` unchanged, every block runs standalone, and the partitions are exact —
   24+10+9 = 43, 152+79+10 = 241.
2. **Door drift (`test_command_surfaces.py`).** 13 mirrors stale; Parts 1–3 edited command bodies
   without re-syncing. Regenerated with `sync-agents.ps1 -NoGlobals` — local surfaces only, so a
   mid-lane body is never pushed to the machine-wide opencode/Antigravity/Codex caches.

### Part M · SCC-182 — a `cd` out of the workspace retargets every later relative path

**Discovered mid-lane, minted as a lettered PART, not a new ticket** (SCC-170's rule). Looked
first: all 13 riders A–L, none covers it; the parent index row was written at an asserted anchor
and read back — all 13 prior rows and every heading survived.

**The defect.** Bash cwd persists between calls *until* one ends outside the workspace root. The
harness then resets it to the **primary working directory** — the MAIN checkout, never the
worktree — and every later relative path reads main. Nothing errors: the same path exists in both
trees and both are valid git repos, so the wrong answer is well-formed. It cost this lane twice:
`mutation_sweep.py` was **written into main** (Part 3), and main's 333-line `test_gate_receipt.py`
was read as the lane's 463-line one (Part 4). The tell was arithmetic — 333 + 130 = 463.

**The law already existed.** `implementation_plan.md:134`, lane rule 8. Stated, never enforced,
and silent about *file* reads — the half that actually bit. Same shape as Part E.

**The remedy is measured, not assumed** — run on this lane before a line of the hook was written:

```
( cd /tmp && … )   →  after the call, cwd UNCHANGED, no reset
cd /tmp && …       →  reset to the main checkout
```

**RED, and the vacuity it hid.** First capture `18/37`. Then: *an absent hook prints nothing,
which is indistinguishable from "allowed"* — every M2/M3/M5 allow-case was passing against a
script that did not exist. Binding them to `exit 0` took RED to **3/37**, exposing 15 vacuous
passes. **GREEN 39/39**; floor **32/32**.

**Live check, against the exact command that caused the bug:**

| Command | Verdict |
|---|---|
| `cd /tmp && … git -C <main> worktree add …` (the Part 4 offender) | **ASKED** |
| `( cd /tmp && … )` | allowed |
| `git -C /abs/worktree status` | allowed |

**Mutation sweep — 6/6, and three of them failed FIRST and were real gaps:**

| Mutant | Must kill | Result |
|---|---|---|
| N1 ignore paren depth | M2 subshell | KILLED |
| N2 drop the `~`/`-`/bare-`cd` arm | M4 | KILLED |
| N3 stop skipping comments | M4 apostrophe | **SURVIVED first** → the case I declared was inert. A comment only matters when it contains an apostrophe, which opens a quote that swallows the later real `cd`. New case added |
| N4 stop skipping heredoc bodies | M5 heredoc | KILLED |
| N5 outer catch-all `raise`s | M6 unparseable | **SURVIVED first** → aimed at an *inner* try that the outer handler already subsumed (`allow()` raises SystemExit, which `except Exception` misses). Unreachable-by-behaviour, so unkillable. Deleted the inner one and re-aimed at the outer |
| N6 `startswith(root)` without the `/` boundary | M4 sibling | **SURVIVED first** → a sibling named `<root>-sibling` read as *inside*. The fixture never tested the boundary. New case added |

**Arming:** `permissionDecision: "ask"`, matching `require-push-approval.py`'s house rule. Note
`ask` resolves to an auto-DENY in auto mode — wanted here, since the point is to stop the command
*before* it retargets the tree. It **fails open** on anything it cannot judge. Operator ruling,
verbatim 2026-08-16: *"this is a reocurring error we need to fix"* / *"no not memory a real fix"*.
⚠ It arms on **landing**: `$CLAUDE_PROJECT_DIR` is the main checkout, so the worktree's
`settings.json` has no effect until this lane merges.

# Part 5 — B (SCC-166): the story lane gains its twin's two steps, adapted

**The gap, measured.** `/smh-code-review` carried a **Step 0.7 blast-radius re-derivation** and a
**Step 2 acceptance audit**; `/cicd-code-review` carried neither. Both are absent for no reason —
the hazard is the same one branch further in. Sibling *stories* land on the epic branch while a
story is built, so the blast radius `/cicd-self-audit` traced that morning can describe a tree that
no longer exists: every gate green, and a reference an epic-mate moved out from under you.

**⛔ The adaptation is the whole part.** A Task lane merges into `main`, so smh re-derives against
`origin/main`. A story lane merges into `epic/<JIRA-KEY>-<slug>`. Copy-pasting smh's step would have
re-derived against a branch the story never meets — it reports *"nothing moved"* while the epic-mate
that did move the file lands anyway. That is the exact stale-ref defect **Part 4 (SCC-165) had just
swept out of this command family**, re-planted three lines under the guard that removes it. So the
ref is pinned **both ways**: `origin/$EPIC` must be present *and* `origin/main` must be absent.

**Ground truth vs the plan.** The plan said `cicd-push-e2e.md` carried the personal name at `:13`
and `:134` — **two** lines. It carries **six**: `:13, :43, :45, :118, :134, :148`. All six now read
*the operator*; `:46`'s *"his direct ask"* became *"their direct ask"* in the same pass. The
toolkit-wide count at this commit is **220 occurrences across 64 files** (the plan recorded 213 at
`a0aceaf`), and it stays out of scope by the plan's own F7 ruling — `rules/operator-profile.md` is a
file where the name IS the subject, so a blanket sweep needs an allowlist and its own ruling.

## What changed

| File | Change |
|---|---|
| `.agents/commands/cicd-code-review.md` | Step 0 heading + a `rev-parse` echo block ("from command output, never from belief"); **new Step 0.7** (blast radius vs `origin/$EPIC`, three written answers, absorb-before-verdict); **new Step 1.5** (acceptance audit, CONCERNS floor, drift direction); frontmatter description updated to name both |
| `.agents/commands/cicd-push-e2e.md` | six named-human referents → *the operator*; one gendered pronoun → *their* |
| `.agents/scripts/tests/test_command_surfaces.py` | **wired into blocks `CS-01`…`CS-10`**, then extended with **`CS-11`** — the review-twin contract |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | a ⓘ block under `### ③ /cicd-code-review`; the `test_command_surfaces.py` row now names CS-11 |
| launcher mirrors | `.opencode/commands`, `.agents/workflows`, `.claude/skills` re-synced (`-NoGlobals`) |

**Step 1.5, not Step 2.** cicd's `## Step 2` is the gate's opt-in check. Renumbering it to reach
literal parity with smh would have moved a heading two other files cite, to buy nothing: the
contract is that the audit runs **after the blind hunt and before the verdict**, and `1.5` is that
position. CS-11 pins the heading's *substance*, never its number.

## The lane trap this part had to clear first

`test_command_surfaces.py` had **zero** `c.block(` calls, which is what keeps a file *outside* the
ORPHAN walker's wired set. Adding one block for CS-11 would have opted the file in and turned its
**57 existing checks into orphans** — the same trap Parts 1 and 2 sprang on `test_gate_receipt.py`
and `test_jira_feed.py`, discovered only when the lane tip went red while every part's own file was
green. So the file was **fully wired first**, along its own `# ── … ──` section comments, with the
three cross-section values (`sync_ps1`, `hand_owned`, `SOURCELESS`) hoisted above the first block so
a filtered run cannot `NameError`. Proven behaviour-neutral:

```
python3 .agents/scripts/tests/test_command_surfaces.py   -> 57/57, verdict BYTE-IDENTICAL to pre-wiring
python3 ... --case "CS-07"                               -> 4/4,  filter 'CS-07': matched 1/10 blocks
python3 ... --case "CS-99"                               -> exit 3 (NO_MATCH, not a false kill)
python3 .agents/scripts/tests/test_suite_runner.py       -> 62/62 (ORPHAN walker clean, file now wired)
```

## RED → GREEN

RED, before a single command file was touched (`red-part5.txt`): **10/15**, five failures, one per
defect —

```
[FAIL] cicd-code-review.md carries the blast-radius re-derivation, with all three answers: no such section
[FAIL] ⭐ cicd's blast radius re-derives against the EPIC branch, and never origin/main
[FAIL] cicd-code-review.md carries the acceptance audit, with its floor and the drift direction: no such section
[FAIL] cicd-code-review.md Step 0 resolves its target from command output, never from belief
[FAIL] cicd-push-e2e.md names a generic referent, not a person: 6 line(s): [13, 43, 45, 118, 134, 148]
```

GREEN after the edits: **CS-11 18/18**, whole file **75/75**, floor **32/32 files**,
`workflow_lint --toolkit-only` → `0 error(s), 0 warning(s), 8 info`.

**What CS-11 pins, and why it is not a prose grep.** Every item is a command the step *runs* or a
shape it must *produce* — `merge-base`, `merge-tree`, `worktree list`, and three numbered answers —
never a phrase. A wording pin is satisfied by a paraphrase that runs nothing, which is this repo's
own `prose-pinning-guards-are-vacuous` lesson reproduced inside the guard. The section is read with
`md_section`, heading-anchored and bounded at the next `## `, so a step that drifts *after* the
verdict it governs cannot pass on a file-wide match.

## Mutants — 8/8 killed, restore verified

`sweep-part5.json`. Five behavioural, three CODE-DERIVED from the guard's own source.

| Mutant | Kills | Result |
|---|---|---|
| B1 the trap itself: `merge-base HEAD origin/main` back in Step 0.7 | `never origin/main` | KILLED |
| B2 Step 0.7's heading stops naming the blast radius | blast-radius parity | KILLED |
| B3 the acceptance audit drops back out | acceptance parity | KILLED |
| B4 Step 0 resolves from belief again | Step 0 echo | KILLED |
| B5 one named human returns to the shipping command | generic referent | KILLED |
| B6 CODE-DERIVED `blast_gaps` stops requiring the three answers | its control | KILLED |
| B7 CODE-DERIVED `story_ref_ok` keeps the positive arm, drops the trap arm | its control | KILLED |
| B8 CODE-DERIVED `name_hits` goes blind | its control | KILLED |

`-- restore verified: bytes match, nothing was committed, and git diff --quiet 604b124a is clean --`

## The AP twin — read, two things ported, one recorded as not porting

Editing the primary made `test_workflow_lint.py` red on its own: *`cicd-code-review-AP.md:
ap_reconciled names 91e6095, but cicd-code-review.md is now at 604b124`*. That linter is the only
thing standing between the two bodies and silent divergence (`sudo-commands-have-ap-twins-that-drift`),
and its rule is **re-diff and restamp — never just bump the sha**. The reading:

| The primary gained | Ports? | Why |
|---|---|---|
| Step 0.7 blast radius vs `origin/$EPIC` | **yes**, compressed | The hazard is *worse* unattended, not smaller — a sibling story lands and nobody is watching. It is **git output, not a read**, so it does not touch the twin's two-ingest budget, and the twin's "no full-repo sweep" ban is about READS |
| Step 0's `rev-parse` echo | **yes**, two lines | The orchestrator hands this twin `REPO`/`WORKTREE`; echoing what git returned is what makes a wrong tree visible instead of assumed |
| Step 1.5 acceptance audit | **not as a section** | The twin already runs the acceptance pass through the engine's Acceptance Auditor in `review_mode: full`. What ported is the two clauses that **bind the verdict** — no evidence is not satisfied (CONCERNS floor), diff-beyond-the-list is drift — because those are law, not habit text. Same reading the SCC-160 stamp used for the "never produces a ticket" sentence |
| the frontmatter description | no | The twin has its own |

**Left deliberately:** the twin's line 41 still names one human. The generic-referent sweep is
SCOPED by the plan's F7 ruling to the two files this part edits; the toolkit-wide pass is a separate
confirm-scope task. Recorded in the stamp header so the next reader does not re-discover it as new.

**B7 is why the controls were refactored mid-part.** The first cut wrote its controls as literals
(`"origin/main" in <a string I built>`), which proves the literal and not the rule: drop the
`origin/main` arm from the live check and a restated control stays green while the guard goes blind.
`story_ref_ok` and `name_hits` are now pure functions called by the live checks **and** by their
controls, so B7 and B8 have something to kill. Same discipline the own-list controls in `CS-08`
already followed.


# Part 6 — H (SCC-176): the plan-time port checklist

## The gap

Every lobby↔project port so far — AVCH-54, then AVCH-59 — cost an afternoon and found the **same
class** of defect: the centre's copy is subtly wrong the moment it runs in a **submodule**, on
**Windows**, inside a **worktree**, in a **thin** repo. All four AVCH-59 divergences came from one
short list, and **two of them are Part C of this very ticket**. Nothing at plan time asked those
questions, so they surfaced at review, or in production on the other machine.

H is the answer, and it is honest about what it is: **a rule plus prose in three commands, with
exactly one mechanical piece.** An agent executes the checklist; nothing machine-reads a plan and
judges whether the six questions were answered. The plan says so (F16 adopted, rev 2), this
walkthrough says so, and the SOP says so — rather than implying a gate that does not exist.

## The one thing that IS mechanical, and why its key had to change

The wired piece is a `workflow_lint._RULE_POINTERS` row: a command that describes a port must **cite
the rule**. It is a **WARN / exit 1**, binding on this lane only through the tip's `0/0` — never
promoted to `rep.err`, which would be new blocking law and needs the operator's own words.

The plan sketched the key as *"port" as a step verb*. Audit F26 called it wrong, and the tree agrees:

| Candidate key | Command files it matches today |
|---|---|
| `\bport\b` (the sketch) | **7** — `cicd-autopilot-deepseek4.md`, `cicd-code-review-AP.md`, `cicd-e2e.md` ("port 3100"), `cicd-live-testing-team.md` (`--port`), `cicd-self-audit-AP.md`, `smh-adviser-board.md`, `smh-code-review.md` ("Port the rule verbatim") — and **none** of the three H edits |
| `exists in more than one repo` | 0 before this part; the exact phrase step (2) writes into all three |
| `git diff --no-index` | 0 before this part; the command that ANSWERS the trigger |

The plan's audit measured 6; the tree at `96f5372` says **7** — `smh-adviser-board.md` was not on the
audit's list. Recorded, not silently matched.

Keyed on the sketch, RED would have named seven files that have nothing to do with porting, and the
tip could never have reached `0/0` — the row would have been *disarmed* rather than satisfied. The
shipped row carries **both** honest arms: the trigger condition as the commands state it, **and** the
command that answers it, so a command that words the trigger differently but still tells an agent to
diff two copies is not silently exempt. Same lesson as SCC-170's row one line above it: **key on the
machinery, never on the concept.**

## What changed

| File | Change |
|---|---|
| `.agents/rules/port-checklist.md` | **new** — six checks, each with the command that answers it; the header states it runs in **both** directions (H5); items 4 and 6 **cite** `project-law.md` rather than restating the thin-repo and repo-local-enforcement law |
| `.agents/rules/INDEX.md` | router row — the trigger, the six checks in one line, and the lint row |
| `.agents/scripts/workflow_lint.py` | the `("port-checklist", "porting", …)` row, with the rejected key recorded in its own comment |
| `.agents/commands/smh-plan-task.md` | MANDATORY RULE **5** — a port gets its own plan section, and the diff **proves** the trigger before the breakdown is proposed; rules-in-force bullet |
| `.agents/commands/smh-self-audit.md` | a Phase 1 blast-radius row — differing copies with no section is a **NO-GO**, not a note; rules-in-force bullet |
| `.agents/commands/cicd-self-audit.md` | the same, as a closing paragraph of Phase 1 (this file carries no rules-in-force block, so the citation is inline) |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | the top pointer table gains a row; §9 gains the passage, which names the WARN severity and says plainly which part is prose |
| `.agents/scripts/tests/test_command_surfaces.py` | **CS-12** — 13 checks |
| the four door caches | regenerated by `sync-agents.ps1`; `CS-03` caught all four as stale before the commit |

## RED → GREEN, in two captures

The part has two red states because it has two claims, and each needed its own.

1. **`red-part6.txt`** — CS-12 written first, against a tree with no rule, no row and no command
   text: **3/13**. The three that passed are the negative controls, which is what a negative control
   is supposed to do on an empty tree — and exactly why they cannot be the only evidence.
2. **`red-part6-lint.txt`** — the row and the trigger text landed, the **citation deliberately
   withheld**. `workflow_lint --toolkit-only` named **exactly three files, and only those three**:

   ```
   [WARN ] rule-pointers: cicd-self-audit.md: porting but never points at `.agents/rules/port-checklist.md`
   [WARN ] rule-pointers: smh-plan-task.md:   porting but never points at `.agents/rules/port-checklist.md`
   [WARN ] rule-pointers: smh-self-audit.md:  porting but never points at `.agents/rules/port-checklist.md`
   -- 0 error(s), 3 warning(s), 8 info --
   ```

   That capture is F26's correction shown working: the sketched key would have printed seven wrong
   names here and none of these three.

GREEN: CS-12 **13/13**, `workflow_lint --toolkit-only` `0 error(s), 0 warning(s), 8 info`,
`check_maps.py --depth3-only --strict` exit 0 (the new INDEX row's path resolves), `run_all.py`
**32/32**.

## Where CS-12 lives, and the file that is still unwired

The natural home for a `check_rule_pointers` test is `test_workflow_lint.py`. It has **zero**
`c.block(` calls, so it sits outside the ORPHAN walker's wired set entirely — adding one block would
opt its 57 existing checks in **as orphans**, the same trap Part 5 cleared on
`test_command_surfaces.py`. The sweep forces the issue rather than merely preferring it:
`mutation_sweep.py:228` passes `m["block"] or m["case"]` to `--case` **unconditionally**, so a mutant
aimed at an unwired file exits 3 (`NO_MATCH`) and is scored a sweep error, never a kill.

CS-12 went into `test_command_surfaces.py` instead, which is already fully wired and is the right
owner on the merits: the contract is *a command surface that describes a port must cite the rule*.
The block imports `workflow_lint` and calls the **real** `check_rule_pointers` over fixture trees, so
the row's wiring is what is pinned, not a restatement of its regex — delete the row and the two
WIRING checks go down with it. A control that re-implemented the pattern would keep passing with the
row gone; that vacuity is what B7 taught this lane one part ago.

**Owed, not done:** `test_workflow_lint.py` is the largest unwired test file this lane has touched,
and `check_rule_pointers` had **no** coverage at all before CS-12 — Part 1 added a row to an untested
function. Wiring that file is a follow-on, not Part 6's scope.

## H4 — the retro run, over Parts C and D, on the current lobby scripts

H4's contract: run the checklist over the code Parts C and D will change, **before** they are built.
If it does not catch C's two divergences, the checklist is wrong — not the scripts. Measured at
`96f5372`:

| # | Check | `mint-push-token.sh` | `pre-push-main-approval.sh` | Verdict |
|---|---|---|---|---|
| 1 | path used as git gave it | **:119-122** `case "$GIT_COMMON" in /*)` | **:44-47** the same block | ⭐ **CAUGHT — this is C1**, in both scripts. AGY's copies have already dropped it; the lobby's are the stale side |
| 2 | `printf`, not `echo` | :145 `\"$APPROVAL\"` | :179 `\"$t_approval\"` | clean — an escaped quote inside a double-quoted string, not an escape `echo` interprets. One line, answered |
| 3 | verify the FILE, not `$?` | **:135-142** `{ … } > "$TOKEN"` with no `\|\| exit`, and the *minted* banner at :144 prints regardless | no redirect | ⭐ **CAUGHT — this is C3** |
| 4 | no `.agents/rules/` path a thin repo lacks | none | :4, :56 | correct **here** (the lobby carries `git-policy.md`); AGY's copy already adapted it to name the centre's path at its :61-66. The check's job was to make someone look, and the look confirms the divergence is intentional in both directions |
| 5 | both machines | none | :15 only — the **comment** recording the `python`/`python3` 127 incident; no live invocation | clean, and the comment is the precedent this item exists for |
| 6 | repo-local hooks, target's own key | — | — | satisfied: the AVCH-59 → lobby port back is carrying an **SCC** key (this ticket), a ticket per repo |

**Two divergences required, two found, both from Part C.** H4 passes, and the retro doubles as Parts
8 and 10's line-numbered work list.

## H5 in both directions, proved by the run above

The checklist's header states it, and this retro is the proof: the fix flows **AGY → lobby** here.
AGY's `mint-push-token.sh:128-141` already carries the corrected form *and the comment explaining
why* (`--git-common-dir` answers absolute in a submodule on both platforms, and git-for-windows
spells that `C:/…`, which no `/*` glob matches). A one-way checklist would have been skipped on
exactly the half this ticket is.

## The A2 sighting, closed — and why the scan could not see it

Part 4 sighted `cicd-clean-code-audit.md:49` by hand and recorded it as belonging "to the cicd parts
(5/6), not to A". Part 6 is the last cicd part, so it is ruled here rather than dropped.

**Why the A sweep missed it is the interesting half.** `test_stale_base_refs.py`'s `_BARE` carries a
`(?<![\w/.-])` lookbehind, and that lookbehind is what makes the scan precise — it is why
`origin/main` (the fix), `_main` (`_artifacts/_main/`) and `<epic-branch-or-main>` (a placeholder) do
not fire. It also rejects the `-` in `${BASE:-main}`. The scan was therefore **structurally blind to
the shell default-value operator**: the one place a bare `main` hides while looking like a fallback
rather than an operand. A human reading the file found it; the guard built to find it could not.

Two patterns were added, and `_BARE` is deliberately **not reused** by the first:

| Pattern | Catches | Hits on the tree before the fix |
|---|---|---|
| `ref-default` — `:-\s*main(?![\w/.-])` | `${BASE:-main}`, `${EPIC:-main}` | **1**, and only that one |
| `ref-assign` — `(BASE\|EPIC\|TARGET\|TRUNK\|REF)="?main` | assignment position, which is operand position one line later | 0 |

RED is `red-part6-a2.txt` — one unruled operand, named with its line. The fix is B1's shape, not A's:
a story lane's base is its **epic branch**, so the line now fetches first, prefers
`refs/remotes/origin/epic/*` over the local head (a local epic head is only as fresh as the last pull,
and sibling stories land there while the audit runs), and falls back to `origin/main` rather than a
bare `main`. **23/23.**


## The AP twin — read, nothing to port

`cicd-self-audit-AP.md` delegates: *"running the pre-dev adversarial audit defined in
`@.agents/commands/cicd-self-audit.md`, adapted for unattended autopilot use"* — it overrides only
I/O, lane boundaries and the blocker token, and names no phases of its own. The Phase 1 paragraph
therefore reaches the autopilot lane through the reference it already carries; a second copy here
would be the drift the stamp exists to prevent. **Re-diffed, nothing ported, restamped with that
reasoning** — never a bare bump.


# Part 7 — F (SCC-174): a forked Dev Record stops reading as "the designed state"

## The gap, and why it is worse than a missing check

`jira_feed.py devrecord` decides *update this record* vs *post a new one* from the **slug**, never
from `--key`. So the same lane spelled two ways is two records. Then `check` looked at two ids and
said:

> `2 Dev Records, one per lane (…) — a follow-on lane rides the ticket it came from, so this is the
> designed state`

— exit 0. It only ever **warned** once the two ids **matched**. Read that twice: the gate was blind
precisely when the bug happens (the slugs differ) and loud only after it had been fixed. It answered
*"are these two lanes?"* when the question is *"is this one lane filed twice?"* — Part D's shape,
in the board feed instead of the push hook.

It is not hypothetical. **AVCH-59, 2026-08-15:** `/smh-quick-dev` filed under `main-write-gate`; the
close-out passed `avch-59-main-write-gate` — **the branch slug, which is exactly what the ceremony's
own text asked for.** Two records, `check` exit 0, and ~7 calls to detect, fix, verify and delete.

## What settles it: the repo, not the strings

The id strings cannot tell the two situations apart, so F2 stops asking them. **An id is a lane only
if the repo can prove it**, from two sources:

| Source | What it covers | What breaks if you drop it |
|---|---|---|
| a `branch:` in any `task.yaml` **git tracks** | the durable half — a landed lane's manifest is committed forever | every landed lane's record reads as a fork the moment a second lane joins the ticket (**F17**) |
| a **prefixed** ref, `refs/heads` **and** `refs/remotes/*` | an unlanded lane (local branch, manifest not yet committed) and a landed one (local branch pruned, `origin/` survives) | either half alone turns a real lane into a fork |

An id nothing claims is a **FORKED Dev Record** → exit 1, naming the orphan id and which record is
newest, with the remedy: delete the record filed under the slug that is not a lane, re-run the block.
Never `--append-new` past it.

**Two decisions inside that are load-bearing, and each has a test that fails without it:**

- **`git ls-files`, never `Path.glob("**/task.yaml")`.** The glob is the obvious shape and it is
  wrong *here*: this repo is the lobby, where `Projects/` is gitignored and holds **other repos'**
  manifests and `.claude/worktrees/` holds a **second copy of this repo's own tree**. A glob reads
  both and hands back slugs that prove nothing about this repo's lanes. The fixture therefore carries
  an untracked manifest under a gitignored dir *and* a plain uncommitted one — the two
  implementations cannot both pass.
- **`lane_slugs` returns `None`, not an empty set, when the repo cannot answer.** *"No lane exists"*
  is a verdict; *"this is not a git checkout"* is a missing instrument. Blessing a pair because the
  evidence could not be **read** is the same defect in a new coat, so that path warns and says so.

## F3 — the slug has ONE source, and three surfaces stopped typing it

`--story` is now optional and defaults to the `branch:` in the manifest for the branch you are
standing on; a *different* slug WARNS and names both. **`/smh-quick-dev`, `/smh-quick-fix` and
`/smh-close-task-merge-tree` all drop the flag** — the ceremony text and what quick-dev files under
can no longer disagree, because they read the same file. (`/smh-quick-fix` was not on the plan's file
list; leaving a third Task surface saying `--story <branch-slug>` would have left the divergence F3
exists to end.)

A **BMAD story lane still passes its story id and is deliberately silent.** It matches no manifest
and never should; warning there would put a false alarm on every story close-out in the system. That
is narrower than F3's literal words (*"WARN when a passed slug matches no manifest"*) and it is the
half of those words that is true.

**The tracked/untracked split.** `lane_slug_here` may read an **untracked** manifest; `lane_slugs`
may not. The difference is the anchor: the first intersects the manifests with the branch you are
**on**, so a manifest git has not seen yet can only ever name *your* lane — and `/smh-quick-fix`
writes its `task.yaml` in the same breath as the Dev Record, so demanding a commit first would kill
the default on the one lane that most needs it. The fork verdict has no such anchor, so it trusts
nothing git is not tracking.

## Evidence

**RED first — `red-part7.txt`, 4/13.** And the four passes are the point: three of them are the
*negative controls* (two manifested lanes, an `origin/`-only lane, a manifest-only lane), all green
against a `check` that exited 0 on **everything**. A negative control that passes before the code
exists is doing its job and is worthless as proof — which is exactly why it cannot be the only
evidence. The nine reds named the fork verdict, the orphan naming, "newest", the untracked case, the
non-git case, and all three F3 clauses.

GREEN **17/17** in the block · **257/257** in the file · suite **32/32** · lint **0 error(s), 0
warning(s)**.

**Mutation sweep — `sweep-part7.json`, 9/9 killed by their declared case**, restore verified against
pinned sha `7d3c181b`. And the first run did **not** come back clean:

> ⛔ **F3c SURVIVED.** The mutant removed the manifest cross-check in `lane_slug_here`, so any
> prefixed branch would count as a lane. The case declared against it — *"no manifest for this
> branch → `--story` is still REQUIRED"* — ran on the non-git fixture, where `git rev-parse` fails
> and the **branch guard** answered first. The cross-check was never reached, so the case passed with
> the mutant in place. Fixed by adding the case that actually reaches it: a real git repo, standing
> on a prefixed branch that no manifest declares. The old case stays, retitled to say what it really
> proves (*"off a git checkout entirely"*).

That is the sweep earning its keep in the shape SCC-179 built it for: a case that names a line it
never executes reads exactly like coverage.

## One legacy assertion RETARGETED, not deleted

`check: two lanes, two story ids -> exit 0 (the designed state)` (SCC-113) now reads **exit 1, not
blessed**. Its fixture is a plain directory, not a git checkout, so it can no longer answer the
question — and *"cannot answer"* must not read as *"designed state"*. The designed-state control
moved into the new block, backed by committed manifests and real refs. SCC-113's grouping-not-counting
fix is untouched and still what gets a genuine two-lane ticket past the duplicate arm.

## Read as a gate change

`check` exit 1 **already** blocked the close-out — `smh-close-task-merge-tree.md` says
`check --key <KEY>   # must exit 0`, and the check has warned on two records under one id since
SCC-49. F arms no new blocking path; it makes an existing one answer the question it was written for,
on the acceptance the ticket itself states (F1: *"must exit non-zero"*). Not a § ARMING item, and no
operator ruling is owed for it.

## Known limit — loud, not silent

A BMAD story id is not a branch slug, so two of them on one ticket would read as a fork. Ids are
branch slugs and story numbers, and a story ticket carries one story, so the shape does not occur
today. Noted rather than guarded — the same call `record_story_id` already made about parentheses in
an id, and the failure is a warning naming both ids, not a silent wrong answer.


## Your Actions

**This lane lands PARTIALLY, at the plan's declared cut line (after Part 7 / F).** `task.yaml`
carries `landing_mode: partial` and `riders:` is trimmed to the eight subtasks whose work is
actually on this branch. **SCC-164 stays open** and closes at the next lane's ceremony.

⚠ SCC-173 and SCC-180 each *lead commits here* — `f36245a`, `1e69af6`, `94e226c` — so the
preflight's mechanical rider check would have accepted them. They are plan and residue-recovery
commits; neither part is **built**. Declaring them would have flipped two subtasks to `Done` over
work that does not exist, which is exactly what *"never declare a ticket whose work is not real"*
forbids. They stay open.

**Landed and declared (8):** SCC-170 · SCC-178 · SCC-179 · SCC-165 · SCC-182 · SCC-166 · SCC-176 ·
SCC-174.

**Carried to the next lane (6) — the main-write gate cluster:**

| Part | Key | What is owed |
|---|---|---|
| 8 · C | SCC-171 | the PC token path as git gives it; mint that cannot lie. **Work list already measured** by Part 6's H4 retro run: `mint-push-token.sh:119-122` and `pre-push-main-approval.sh:44-47` (C1), `mint-push-token.sh:135-144` (C3 — redirect with no `\|\| exit`, banner at `:144` unconditional). AGY's copy at `:128-141` already carries the corrected form; the fix flows **project → lobby** |
| 9 · G | SCC-175 | no post-merge write to `main` |
| 12 · L | SCC-180 | the `--hard` remedy made safe — **and its `# Part 12` plan section still does not exist** (audit F1); write it first |
| 10 · D | SCC-172 | three fail-opens in the main-write gate. **D3 (`.githooks/pre-push`) is the LAST edit of that lane** (F22) |
| 11 · E | SCC-173 | the blind review recorded and enforced — E3 **BLOCKS** per § ARMING |
| 11 · I | SCC-177 | the review sequenced |

Next lane: `chore/SCC-164-main-write-gate` (or its own key), with those six as its `task.yaml`
`riders:`. The § ARMING ruling already covers A4, E3 and `--strict-actions`, so **no new operator
ruling is owed** to build them.

- [ ] **The merge itself** — `/smh-close-task-merge-tree`, on the operator's invocation.
