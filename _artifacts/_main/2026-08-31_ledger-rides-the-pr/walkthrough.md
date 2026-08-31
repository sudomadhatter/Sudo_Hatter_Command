# SCC-358 — the close-out ledger rides the PR

review-runtime: fan-out

Lane `chore/SCC-358-ledger-rides-the-pr` · 2026-08-31 · Plan: [implementation_plan.md](implementation_plan.md) · Manifest: [task.yaml](task.yaml)

## What this closes

`/cicd-push-e2e` was the last close-out door that wrote its bookkeeping **after** the merge, standing
on `main`, as a new direct push. That stopped being possible the day both repos went to an armed
server-side ruleset (lobby SCC-118 id 20756052; AviationChat AVCH-111 id 21963341, armed 2026-08-31):
a required check means a pull request is the only road in, so the post-merge write is a direct push
the gate refuses **by design**. It was found the hard way at the AVCH-111 close-out, where the ledger
commit needed its own operator approval and a hand-built `--no-ff` merge just to land.

**The law is not new — this was the last door without it.** `/smh-close-task-merge-tree` commits its
flight event pre-merge at Step 2.5 and carries an outright ban on post-merge commits, an instruction
that *"used to say the opposite, and that instruction was the whole of SCC-175"* — whose refusal
banner's `reset --hard` remedy then destroyed three other sessions' uncommitted work (SCC-180).
`/cicd-close-story-merge-tree` rides its board writes on the story branch. This ports the same law to
the third door.

## Task Checklist

| | Item |
|---|---|
| ✅ | `CS-21` in `test_command_surfaces.py` — **13 checks plus 15 controls**, written RED first, then rebuilt after the review found nine of them vacuous |
| ✅ | `cicd-push-e2e.md` — new **Step 3.5**, the bookkeeping committed on the epic branch before `gh pr create` |
| ✅ | `cicd-push-e2e.md` — Step 4's gated-tip sentence qualified for the one artifacts-only commit |
| ✅ | `cicd-push-e2e.md` — Step 3's `(Step 6)` cross-reference repointed to `(Step 3.5)` *(audit finding F2)* |
| ✅ | `cicd-push-e2e.md` — Step 5.5's PRD reconcile records to the ticket comment only, with the reason it cannot ride the PR |
| ✅ | `cicd-push-e2e.md` — Step 6 is prune + verify, carrying the ban and naming SCC-175 / SCC-358 |
| ✅ | `cicd-push-e2e.md` — Step 6.5's comment gains the slot for the Step 5.5 PRD line |
| ✅ | `commands/INDEX.md` — the routing index no longer describes a post-merge ledger *(audit finding F1)* |
| ✅ | `workflows_testing_SOP.md` — currency row, the command-atlas diagram (new `S35` node), and a §7 paragraph |
| ✅ | `workflows_testing_SOP_changelog.md` — one row, dated, ticket-keyed |
| ⚠ | `.opencode/commands/cicd-push-e2e.md` re-mirrored **in-lane, by byte copy, not by running the sync** — see `## Evidence

⭐ **The check IDs below are the SHIPPED ones.** The first draft's `D`/`F1`/`F2` were retired by the
review rebuild; the RED transcript further down is preserved verbatim with its original names, which
is why the two sets differ. Nothing was renamed to look tidier.

| AC | Assertion, as shipped | Result |
|---|---|---|
| AC-1 | `A` (Step 3.5 INSTRUCTS both writes, prose-scoped, negation rejected) · `A3` (and pushes them) · `B` (two-sided order: Step 3 → Step 3.5 → `gh pr create`) | RED → GREEN |
| AC-2 | `C1` (the WHOLE post-merge region writes nothing) · `C2` (no new tail step may be appended) | RED → GREEN |
| AC-3 | `A1` (the key is on the `git commit` LINE) · `A2` (explicit paths, never `git add -A`) | RED → GREEN |
| AC-4 | `E` (Step 6 states the ban, with its scars in the SAME paragraph) · `F` (Step 6 instruments whether Step 3.5 ran) | RED → GREEN |
| AC-5 | `G` (Step 5.5 records every outcome to the ticket) · `I` (the SOP's Epic currency row is ticket-only) | RED → GREEN |
| AC-6 | `C1` (the region ban covers `home-base INDEX`) | RED → GREEN |
| — | `H` — the routing index teaches the new order, positively *(added by the self-audit as F1, rebuilt as a positive by the review)* | RED → GREEN |

⚠ **AC-5's literal as PLANNED was unshippable, and this is recorded rather than quietly swapped.**
The plan said grep `"and the ledger row"` in *both* files. The door never contained that string (its
text was `"in the Step 6 ledger row and in…"`), so the planned assertion would have passed against
the unedited door — a vacuous RED. The shipped checks use a different construction, and after the
review they are positive claims rather than bans on a retired sentence.

⚠ **AC-6 nearly lost its guard in the rebuild.** The retired `G` banned `"home-base INDEX"` inside
Step 6; the new region check bans the two write PATHS, which that phrase does not contain. Caught
while reconciling this table against the shipped block, and closed by adding the phrase to `C1` with
its own control and mutant (`N15`).

**The RED, at `13ffe716` — nine real failures, four controls green, C1 the predicted standing guard.**
Check names here are the first draft's:

```
$ python3 .agents/scripts/tests/test_command_surfaces.py --case "CS-21"
[FAIL] CS-21 A Step 3.5 writes BOTH the ledger row and active-context: ... <no Step 3.5 section at all>
[FAIL] CS-21 B ORDER Step 3.5 -> gh pr create
[PASS] CS-21 C1 the --after-merge half instructs no `git commit`
[FAIL] CS-21 C2 Step 6 owns NEITHER the ledger row nor active-context: ... ## Step 6 — Prune the epic branch + update the ledger
[FAIL] CS-21 D Step 3.5 commits with the JIRA key in the subject
[FAIL] CS-21 E Step 6 carries the post-merge commit ban, with its scars named
[FAIL] CS-21 F1 the door's reconcile no longer records to the ledger row
[FAIL] CS-21 F2 ...and neither does the SOP's currency table
[FAIL] CS-21 G Step 6 no longer hand-appends to the home-base INDEX
[FAIL] CS-21 H commands/INDEX.md does not describe a post-merge ledger
[PASS] CS-21 CONTROL a door with no Step 3.5 fails A
[PASS] CS-21 CONTROL bookkeeping placed AFTER the PR fails B
[PASS] CS-21 CONTROL a commit with no <JIRA-KEY> fails D
[PASS] CS-21 CONTROL a ban with no scars named fails E
-- 5/14 passed --
```

⭐ **Each red names its own reason, which is the check that the red is real.** `A` reports *"no
Step 3.5 section at all"* and `C2` quotes the live Step 6 heading — neither is a setup failure
wearing a red's clothes (`red-test-can-die-before-its-assertion`).

**The GREEN, after the review rebuild:**

```
$ python3 .agents/scripts/tests/test_command_surfaces.py --case "CS-21"
-- 28/28 passed --
```

⛔ **The first draft's sweep (8 mutants, 8/8 killed) is NOT reproduced here, because the review
proved it certified nothing.** All eight were existence mutants aimed at the very literals the checks
grepped; the rebuilt 15-mutant sweep in `## Code Review` is the one that means something. The retired
table is in this lane's git history at `9b19b47d` and is left there rather than dressed up.

### ⚠ The correction the gate made, recorded because the plan got it wrong

The plan's step S8 concluded that `sync-agents.ps1` was a **no-op** for this lane, reasoning that the
door's `description:` frontmatter was unchanged and the platform launchers are thin pointers carrying
only that description. That was right about the launchers and **wrong about opencode**: the
`.opencode/commands/` mirror is a **full byte copy of the brain**, so any body edit stales it. The
suite caught it — `every mirror door still says what its brain says: 1 drifted`.

It is re-mirrored here by byte copy rather than by running the sync, and that is a deliberate call
with a reason: `sync-agents.ps1 -WhatIf` showed the full run regenerates all ~70 doors **and writes
the machine-global caches** (`~/.config/opencode/commands`, `~/.gemini/antigravity/global_workflows`).
Run from an unmerged lane, that publishes unlanded work into every other project's menu. The mirror
was verified byte-identical to the brain at `origin/main` before the copy, so the result is exactly
what the sync would have produced for this file and nothing else. **The real `/smh-sync-agents`
belongs after the merge, run from `main`** — it is listed in `## Your Actions`.

### The full suite

```
$ python3 .agents/scripts/tests/run_all.py     (before the fixes)
65/67 files passed  FAILED: test_check_maps.py, test_command_surfaces.py
```

Both reds were this lane's own and both were legitimate: `test_command_surfaces.py` was the opencode
mirror above, and `test_check_maps.py` F2 was this session folder missing its ledger row in
`_artifacts/_main/INDEX.md` — which is a pleasing way for the ledger ticket to be caught. Both fixed.

The green run of the code that actually lands is stamped through the receipt writer, and the receipt
rides this branch at [gates/suite.json](gates/suite.json):

```
$ python3 .agents/scripts/gate_receipt.py run --task SCC-358 --gate suite \
      --root _artifacts/_main/2026-08-31_ledger-rides-the-pr --cwd <worktree> \
      -- python3 .agents/scripts/tests/run_all.py
[PASS] suite exit=0 85.7s @ cbae5cc2
        receipt: gates/suite.json
```

⚠ **That receipt predates the review fixes and was RE-STAMPED after them.** The receipt that ships
is the second run, on the code that actually lands:

```
[PASS] suite exit=0 85.1s @ 5592311d
        receipt: gates/suite.json
```

Standing gates, all bare, all exit 0: `workflow_lint --toolkit-only` (0 errors, 0 warnings) ·
`check_maps --depth3-only --strict` · `check_links --base origin/main` (clean).

## Code Review (2026-08-31)

review-runtime: fan-out
lens_isolation: worktree — each repo-reading lens got its own `git worktree add --detach` copy of the lobby at `294c78aa`, cut by hand and VERIFIED before launch; the Blind Hunter got no tree, by design
lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted: 5/5
lenses_na: none
findings: 0 decision · 37 patch · 0 defer   (2 noise-dismissed · 0 relevance kills)
dispositions: per-lens: blind-hunter=8/2/0 · edge-case-hunter=8/0/0 · literal-correctness-hunter=7/0/0 · acceptance-auditor=7/0/0 · test-adequacy-auditor=7/0/0
severity_floor: none
drift: undeclared=4 · unimplemented=0 · incomplete=0 - the Acceptance Auditor reconciled the diff against the plan's `## Declared Change Set` and found four files the list did not name: `.opencode/commands/cicd-push-e2e.md` (the S8 correction — the mirror is a full byte copy, not a thin launcher), `_artifacts/_main/INDEX.md` (this session's ledger row, which `test_check_maps` F2 demanded), and `docs/doc-graph.json` + `docs/doc-graph.md` (regenerated and staged by the armed pre-commit hook, never hand-edited). All four are now declared in the plan; nothing declared went unimplemented and `declared_change_set.py parse` reports `incomplete: []`.
notes: every finding fixed in-lane before the verdict — no defer, no residue ticket. The sweep was rebuilt from 8 existence mutants to 15 narrowings/paraphrases/inversions; 15/15 killed.

Verdict: PASS @ 5592311d

⛔ **The review found the first guard substantially vacuous, and it PROVED it rather than asserting
it.** Three lenses independently reproduced the same class of hole, and the test-adequacy lens
returned nine surviving mutants, each re-run against the full unfiltered file. The worst restored
**this lane's own defect** — the ledger write back in Step 6, reworded — with all 67 suite files
green. Others put the write in Step 6.5 or in a brand-new `## Step 7`; inverted Step 3.5 while
keeping every literal the checks grep; deleted the JIRA key from the commit fence while the prose
kept it; and deleted the ⛔ ban outright while both ticket numbers survived in the paragraph below.

**The root cause was one mistake made ten times: the checks pinned retired SENTENCES.** That is the
`prose-pinning-guards-are-vacuous` failure this lane's own plan cites, walked into anyway. Two
structural errors kept it invisible. The four controls **retyped** each predicate instead of calling
it, so they proved "an expression of this shape can be false" and never "the shipped check can fail"
— measured: weakening the live `ipr > i35` to `ipr >= 0` left all four controls green. And the sweep
was 8 existence mutants with **zero narrowings**, aimed at the very literals the checks read, so it
certified that the checks agreed with themselves at two points and nothing about their edges.

**The rebuild changes their shape, not their count.** Every predicate is now a named function that
the live check *and* its control both call, so weakening a predicate turns its own control red — the
pattern the door-parity block one screen up already had right. Negatives became positives or
structure wherever a paraphrase could dodge them: `C1` reads the whole post-merge region instead of
one section, `C2` pins the step-heading set so no new tail step can appear, `A` reads prose with
fences stripped *and rejects negation*, `A1` wants the key on the commit line, `E` wants the ban's
imperative in the same paragraph as its scars, and `H`/`I` assert what those files must SAY rather
than banning one sentence they must not. 13 checks, 15 controls, 28/28.

### The door moved too, because the new guard refused it

Three of these came from lenses RUNNING the door rather than reading it:

- **Step 3.5 now PUSHES what it commits.** The Edge Case Hunter built a fixture repo, made only the
  bookkeeping commit, and ran the door's own Step 1.5: `VERDICT: BLOCKED — merging an unpushed branch
  puts commits on production that exist on one disk` (exit 2). A session ending between Step 3.5 and
  Step 4 was unresumable, halted by a hazard the step had created. The sibling door this law was
  ported from pushes inside the same block; **the port had dropped it.**
- **Step 3.5 is idempotent, and writes in the PENDING tense.** Re-entry before the merge is ordinary
  — a red check, requested changes, a closed PR — and two number-free rows are indistinguishable. And
  a row saying the epic *shipped*, written five steps before anything deploys, becomes a false record
  on `main` the moment a deploy is rolled back, which Step 6 then forbids correcting.
- **Step 5.5's third branch gained its verbatim line.** Step 6.5's comment carries the PRD line
  unconditionally, so the one branch that defined none left an agent holding a mandatory slot with
  nothing to fill it — which it fills by inventing one.
- **Step 6 instruments whether Step 3.5 ran at all**, and names the remedy lane, instead of leaving
  it to an agent's notice in a door that instruments everything else.

### Two findings where the assessment DISAGREED with the label

**The Blind Hunter's `important` "the unkeyed absorb merge refuses every epic PR" — dismissed on
evidence.** It had no repo access, said so, and capped its own confidence honestly. I read the gate
the door actually runs under: `check_commit_keys` lists commits with `git rev-list --no-merges`, with
a comment saying merge commits are skipped because git writes their message. **The refusal cannot
happen.** What survived is smaller and real: my own sentence said the gate reads "every commit", and
the true word is *non-merge* — a reader would have re-derived it wrongly. The Literal-Correctness
Hunter opened the same file independently and reached the same conclusion.

**The Blind Hunter's `nitpick` "Step 4 names two locations where there is one" — dismissed as
factually wrong.** Its premise is that active-context lives under `_artifacts/`. True in the lobby,
false in a project: AviationChat's sits at `_bmad-output/active-context/active-context.md`. The
second clause is load-bearing precisely because this door runs in projects.

### One contradiction the review surfaced that nothing else would have

Step 4's `ⓘ` — untouched by this lane — still said AviationChat's `main` carried **no branch
protection and no ruleset at all**, measured 2026-08-31. Step 3.5, added the same day, says the
ruleset refuses the post-merge push. Same file, same repo, same date, opposite facts. Both were true
in sequence: the 404 was measured that morning, and AVCH-111 armed the ruleset that afternoon. The
note now says so, so a reader can tell which is current.

### The rebuilt sweep

```
$ python3 .agents/scripts/mutation_sweep.py --table _artifacts/_main/2026-08-31_ledger-rides-the-pr/sweep.json
-- sweep: 15 mutant(s) over 3 file(s) @ 5592311d --
KILLED  N1  the active-context INSTRUCTION is deleted; only the `git add` mention survives
KILLED  N2  Step 3.5 is INVERTED — every literal kept, the instruction reversed
KILLED  N3  the key is dropped from the FENCE only, surviving in the prose below
KILLED  N4  the explicit paths become a sweeping `git add -A`
KILLED  N5  the push is dropped — the shape ship_preflight BLOCKS on a resumed run
KILLED  N6  ORDER — the gate no longer precedes the bookkeeping
KILLED  N7  the retired write is reinstated in Step 6.5, one section over from Step 6
KILLED  N8  the AVCH-111 defect restored as a brand-new tail step
KILLED  N9  the ban is DELETED; both ticket numbers survive in the paragraph below
KILLED  N10 the ban is INVERTED while keeping its scars
KILLED  N11 Step 6's instrument is removed — a skipped Step 3.5 becomes unnoticeable
KILLED  N12 the reconcile is recorded to the ledger row again, REWORDED
KILLED  N13 the SOP currency row reinstates the ledger with a CHANGED CONNECTIVE
KILLED  N14 the routing index is REWORDED back to the retired order
KILLED  N15 the LOBBY hand-append creeps back into the post-merge region (AC-6)
-- restore verified: bytes match, nothing was committed, and `git diff --quiet 5592311d` is clean --
-- full file, unfiltered: python3 .agents/scripts/tests/test_command_surfaces.py -> exit 0 --
        | -- 274/274 passed --
-- sweep clean: 15/15 killed by their declared case --
```

⭐ **Two mutants did not die on the first run, and the difference between them is the lesson.** `N2`
was a **real survivor** — check `A` read presence, so an inverted instruction keeping every literal
passed the guard written to catch exactly that; `A` now rejects negation on the naming line. `N6` was
a **defective mutant, not a weak check** — it inserted a marker *before* Step 3.5, so the real Step 3
still preceded the bookkeeping and the order genuinely held; re-aimed at the gate's heading, it dies.
A survivor and a bad mutant read identically in a transcript, which is why both are named here.

### The lens-isolation trap this review nearly walked into

Three of the four directories the fan-out wanted were **stale copies from the AVCH-111 review** —
same `lens-*` names, sha `449fa4f4`, no `.agents/commands/` in them at all, because they were
AviationChat worktrees. The SCC-313 probe caught it: `git rev-parse --show-toplevel` named the right
directory while `git rev-parse HEAD` named the wrong sha. Unchecked, three of five lenses would have
reviewed **a different repository** while the roster recorded `lens_isolation: worktree`. Fresh trees
were cut under unique names and each verified to be at `294c78aa` *and* to contain the change before
any lens launched.


## Your Actions

Everything in this lane's scope landed and is proven above. Two things are genuinely yours.

- [x] The merge itself — lands via this branch's PR
- [ ] Run `/smh-sync-agents` **after this lands, from `main`**, so the machine-global command caches
      (`~/.config/opencode/commands`, `~/.gemini/antigravity/global_workflows`) pick up the reworked
      door. It is deliberately not run from this lane: the sync writes machine-global caches, and
      doing that from an unmerged branch publishes unlanded work into every other project's menu.
      This is also the standing item you flagged this session.

**Raised once, with its remedy, and already filed — not left as a bill.**
[SCC-359](https://sudo-command.atlassian.net/browse/SCC-359) (Subtask of the rolling ticket SCC-318):
`/smh-quick-dev` Step 1.5 condition 3 can never pass for a lane that follows `/smh-plan-task` Step 5's
own convention. Step 5 requires the approval line to carry the sha of the commit that recorded it —
not knowable until that commit exists — so the planner writes `<pending>`, commits, then stamps the
real sha in a **second** commit. The last-touch sha is therefore always the stamp commit, never the
recorded one. Measured twice: SCC-347 (recorded `acb02585`, stamped `cf198990`) and this lane
(recorded `4fdedf2f`, stamped `13ffe716`), and in both the entire delta between the two shas is the
one placeholder line. It did not block this lane, because your approval was given live in this
session rather than read off disk.
