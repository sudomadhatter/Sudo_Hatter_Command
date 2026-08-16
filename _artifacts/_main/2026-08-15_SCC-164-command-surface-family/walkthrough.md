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
- [ ] **Part 4 · A / SCC-165** — a bare `main` is a stale ref (20 operands)
- [ ] **Part 5 · B / SCC-166** — cicd-code-review gains its twin's two steps, ADAPTED
- [ ] **Part 6 · H / SCC-176** — the plan-time port checklist
- [ ] **Part 7 · F / SCC-174** — jira_feed check stops blessing a forked Dev Record ⛔ CUT LINE
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

## Your Actions

_Filled in at the end of the lane._
