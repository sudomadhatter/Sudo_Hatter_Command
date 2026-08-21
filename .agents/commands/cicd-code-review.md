---
description: Review + gate a story — re-derives the blast radius against the current EPIC branch (Step 0.7, because sibling stories land while you build), then an adversarial code review, an acceptance audit against the story's checkable list, the test gate (suite + TEA trace + nfr + test-review) and the clean-code gate (code-standards conformance), producing a PASS/CONCERNS/FAIL/WAIVED verdict. Step ③ of the sudo dev flow.
platforms: [opencode, antigravity]
---

# /cicd-code-review — Review + Test Gate + Clean-Code Gate (③)

> **Rules in force for this command:**
> - `.agents/rules/smh-target-resolution.md` §STD + §BIND — bind exactly ONE project and **never the
>   lobby**; this is the pointer the `smh-` twin does not carry, and it is why that twin cannot do
>   this work
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push
>   `main`, never force-push
> - `.agents/rules/worktree-per-story.md` §"cwd is not intent" — the diff and the artifacts are pinned
>   from command output; with sibling STORY lanes landing on the shared epic branch while you review, a
>   lookalike file in the shared checkout is another lane's, not evidence
> - `.agents/rules/artifacts-always-first.md` §6 — the verdict is a **section appended to the story's
>   `walkthrough.md`**, never a standalone review file
> - `.agents/rules/tests-must-gate-for-real.md` — an empty diff, a missing tool and a piped exit code
>   are the three ways this gate goes vacuously green
> - `.agents/rules/code-standards.md` — the standard the clean-code gate at Step 3.5 judges against,
>   and the owner of the FAIL-vs-CONCERNS split


Thin orchestrator — runs your adversarial review, then the test gate, then the clean-code gate, and
appends ONE `## Code Review (<date>)` verdict section to the story's `walkthrough.md` — the section
`cicd-update-sprint-memory` reads before flipping the story to `done` (no separate verdict file —
`artifacts-always-first` §6). Project-scoped (targets THIS repo). Both gates live HERE; there is no
separate `/test-gate`, `/qa-gate`, or `/lint-gate`.

> Flow position: `cicd-dev-story-tests` → **`cicd-code-review`** → `cicd-close-story-merge-tree`.

## Step 0 — Resolve the target project (FIRST) — from command output, never from belief
Bind the target per `.agents/rules/smh-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override → `.agents/active-project.txt` → else **STOP and ask** — never guess, never operate on the lobby.
Set `PROJECT_ROOT` and **echo exactly** `Target: Projects/<name>` before any work. Every bare path below
resolves under `PROJECT_ROOT` (nested `bmad-*`/`1_*` skills bind their `{project-root}` to it); a needed
path missing under `PROJECT_ROOT` → STOP, never fall back to the lobby.

Then say what you resolved **in the words git gave you**, not in the words you expected:

```bash
PROJECT_ROOT=$(git -C "<the target you bound>" rev-parse --show-toplevel)
BRANCH=$(git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD)
HEAD_SHA=$(git -C "$PROJECT_ROOT" rev-parse HEAD)
echo "Reviewing: $(basename "$PROJECT_ROOT") | $BRANCH @ ${HEAD_SHA:0:8}"
```

⛔ **Echo that from the commands.** A self-reported echo can only confirm a wrong belief, and with
sibling story lanes live the shared checkout is the wrong tree more often than not — a preflight once
printed *another* lane's branch as clear to merge and was believed
(`preflight-resolves-repo-from-cwd`).

## Step 0.5 — Re-enter the story worktree if one already exists (fresh-chat resume)
Before Step 1: `git worktree list` under `PROJECT_ROOT` (`worktree-per-story` → "Resuming"). A
`claude/<JIRA-KEY>-<story-slug>` tree exists → **cd into it and bind the diff, story file, tests, and suite commands
under it** (the built code often lives ONLY there — the shared checkout would audit an empty or stale
diff); echo `Worktree: reviewing in <path>`. None → review in `PROJECT_ROOT` as usual. Artifacts too:
this story's plan/walkthrough/verdict live in THIS tree — absent here = that step never ran; a lookalike
in the shared checkout is a SIBLING lane's, not evidence. Echo the story's ①②③ step-state before Step 1.

## Step 0.6 — Resolve the diff (committed work only)

Bind the two strings every step below reads — from command output, before anything measures:

```bash
WORKTREE=<the story tree Step 0.5 resolved, or "$PROJECT_ROOT" when none exists>
EPIC=<epic/JIRA-KEY-slug>      # from `git -C "$PROJECT_ROOT" branch -a --list '*epic/*'`, or the story's epic in the plan
env -u GITHUB_TOKEN git -C "$WORKTREE" fetch origin "$EPIC"        # a bare `$EPIC` is this checkout's LAST PULL
git -C "$WORKTREE" diff --name-only "origin/$EPIC"...HEAD          # the story's committed work
git -C "$WORKTREE" diff --name-only "origin/$EPIC"...HEAD | wc -l  # echo this count
git -C "$WORKTREE" status --short                                  # anything uncommitted (report it; it is not reviewed)
```

Echo the file count. **An empty set is a STOP, not a pass** — Step 3.5 restates it at the gate, but by
then the engine, the acceptance audit and the whole test gate have already run on nothing.

⛔ **`git -C ""` does NOT error** — git documents it as "leave the current working directory
unchanged" — so an unassigned `$WORKTREE` silently measures whatever tree the shell is standing in:
the shared checkout Step 0.5 just told you is empty or stale, and the redirects in Step 0.7 still
create their two `/tmp` files, so the overlap reads clean (`preflight-resolves-repo-from-cwd`).
⛔ The ref is `origin/$EPIC`, never the trunk (SCC-165 — Step 0.7 says why).

Dirty files under `_artifacts/_memory/` are **named separately and left alone** — another session's
memory store is never swept, deleted, or committed under this story (`artifacts-always-first`
§ "The memory store": the project store is git-tracked, so it materialises in every story worktree).

## Step 0.7 — ⭐ Re-derive the blast radius against the **current epic branch** (MANDATORY)

**The pre-work audit expires.** `/cicd-self-audit` traced this story's blast radius against the epic
branch as it stood when the plan was written. Sibling stories land on that branch while you build, so
by the time you get here that trace can describe a repo that no longer exists. **Every gate in Step 3
can be green while a landed story has moved a file this one depends on** — a green suite proves your
code runs, not that your references still resolve.

⛔ **The ref is the EPIC branch, never the trunk.** A story lane merges into `epic/<JIRA-KEY>-<slug>`;
that branch is the tree this work will actually meet, and the trunk is one merge further out.
Re-deriving against the trunk answers a question nobody asked: it reports "nothing moved" while the
epic-mate that *did* move the file lands anyway. That substitution is the stale-ref defect SCC-165
swept out of this command family — do not re-plant it here.

```bash
env -u GITHUB_TOKEN git -C "$PROJECT_ROOT" fetch origin
git -C "$PROJECT_ROOT" branch -a --list '*epic/*'        # normally exactly one live epic branch
# $WORKTREE and $EPIC — bound in Step 0.6 from command output; reuse them, never re-derive from cwd
BASE=$(git -C "$WORKTREE" merge-base HEAD "origin/$EPIC")
git -C "$WORKTREE" diff --name-only "$BASE".."origin/$EPIC" | sort > /tmp/theirs.txt  # landed while you built
git -C "$WORKTREE" diff --name-only "origin/$EPIC"...HEAD | sort > /tmp/mine.txt      # what you changed
grep -Fxf /tmp/mine.txt /tmp/theirs.txt                                               # the TRUE overlap
git -C "$WORKTREE" merge-tree --write-tree --messages HEAD "origin/$EPIC" | head -40  # conflicts, before they are real
git -C "$PROJECT_ROOT" worktree list                                                  # sibling story lanes still live
```

⚠ **`zsh` does not word-split an unquoted variable** the way `bash` does. Build file lists into a file
and expand with `$(cat …)`, or the whole list arrives as one argument and your sweep silently checks
nothing — a vacuous green in the tool you brought to prevent vacuous greens.

Then answer these three, in writing. **"Nothing moved" is a reportable result**, not a reason to skip
the step:

1. **Did anything this diff REFERENCES move, get renamed, or get deleted on the epic branch?**
   Re-resolve every repo path and `#L` anchor the diff names — especially the ones a component
   imports, a route registers, or a fixture loads. A reference an epic-mate moved out from under you
   is a **FAIL**, not a nit: the code still reads correctly and points at a file that is not there.
2. **What is the true overlap, and does the merge conflict?** Report the intersection and the
   `merge-tree` result. A conflict in a **generated** file (a lockfile, a build manifest, an INDEX the
   tooling writes) is resolved by **regenerating it**, never by hand-merging.
3. **Which sibling story lanes are still live, and does one of them need to land first?** Name the
   landing-order dependency and what happens to this story if the order is reversed.


<!-- twin-law: review-level -->
**Derive `review_level` HERE, from the radius you just measured (SCC-232) — derived, never
chosen.** The rule is fixed and defined once, in the engine's lens-roster contract (step-01 § The
two levels): **quick** when every answer above came back contained (nothing referenced moved · no
gate, hook, rule, or contract surface in the radius · ≤3 source files in the re-taken diff);
**standard** otherwise. Hand the engine `review_level` WITH the three written answers as its
grounding — a level without its radius evidence is a flag, and no caller gets one; the engine
defaults such a call to `standard`. (`lens_budget` is a different axis and neither re-declares
the other.)
<!-- /twin-law -->

**Absorb the epic branch now, before the verdict** — conflicts belong on this story branch, never on
the epic (`git-policy`). Re-run Step 3's gate **after** absorbing; a verdict measured on a pre-merge
sha is a verdict about code that will never exist.

## Step 0.9 — ⭐ Probe the review runtime and RECORD it (before the engine, SCC-177)

**Can this session fan out to subagents?** Answer it from this runtime, not from what usually
happens: a headless pipeline or a platform without a subagent tool makes the answer `inline`, and
both are invisible until a lens fails to launch. ② (`/cicd-dev-story-tests` Step 0.8) records its own
runtime into the same header; this step **re-probes in ③'s session and overwrites the line** when the
two differ, and a ② that skipped its probe leaves this as the only recording point (F24).

⛔ **The question is a **capability**, never a **policy** — and conflating the two silently gutted a
review on SCC-197 (SCC-203).** *Does a subagent tool exist in this runtime?* is the whole question.
*Am I permitted to use it right now?* is a different one, and answering it here is how a session
directive — *"do not spawn subagents unless the user asks"* — got read as *"this runtime is
inline"*. The entire review then ran in the builder's own context and the flow recorded it as a
legitimate outcome. The operator caught it by reading the chat; nothing in the system would have.

⭐ **Subagents are the DEFAULT, and invoking this command **IS** that request.** A review needs
clean-context lenses to be worth running, so the ask is built into the workflow rather than left to
the operator to remember. Where a directive gates subagent use on being asked, this step is the
asking — you do not stop and put the question to the operator, and you never quietly downgrade to
`inline` to avoid it. **Only a runtime with no subagent tool at all is `inline`.**

And if you are `inline` while holding this lane's plan and walkthrough, the engine **drops** the
Blind Hunter rather than faking it — see step-01 § *When the order CANNOT protect it*. A roster is
not allowed to claim a review was more independent than it was.

Write the answer into the story walkthrough's header, **above `## Code Review`**, exactly like this:

```
review-runtime: fan-out
```

⛔ **`inline` is a different review, not a slower one — which is why it is declared before the hunt
rather than discovered during it.** Under `inline` the engine runs the ladder ONCE, blind lens first
on the diff alone, and every lens comes back `recovered-inline`; a roster reporting `ok` under an
`inline` header is a contradiction that `walkthrough_roster.py` blocks on. Declaring it afterwards,
from the roster you already have, makes the check circular and buys nothing.

## Step 1 — Clean-Room Adversarial Code Review

Invoke the **`code-review-engine`** skill on the story's diff — the house review engine (SCC-116). It
runs the lens fan-out, verifies what the lenses find, triages it and records it; **you own everything
around it**: the inputs, the fixes, the gates and the verdict.

**Resolve every input before you invoke it — the engine resolves nothing itself, and a missing
required input is a stop, not a guess:**

| Input | What you pass |
|---|---|
| `REPO` | `PROJECT_ROOT` from Step 0 |
| `WORKTREE` | the tree Step 0.5 resolved (the story tree when one exists — the built code often lives ONLY there) |
| `DIFF` | the `origin/$EPIC...HEAD` diff from Step 0.6, **re-taken in that worktree after Step 0.7 absorbed `origin/$EPIC`** — committed work only |
| `HEAD_SHA` | `git rev-parse HEAD` in that worktree, taken **now, after Step 0.7's absorb** — this is the sha the engine records the review against, **not** necessarily the sha your verdict cites: you apply fixes below, and Step 4's verdict must cite the FINAL sha its full-suite evidence was measured on |
| `review_mode` | `full` when the story file exists; `no-spec` when it does not |
| `STORY_FILE` | the story file (`full` mode) |
| `ARTIFACT_DIR` | `_artifacts/epic_<E>/<story>/` **inside that worktree** |
| `DEFERRED_WORK` | the project's `deferred-work.md`, when it has one |
| `lens_budget` | `standard` — the interactive budget, because a human is sitting in front of this review. **This command does not define what the caps are; step-01 of the engine does, once** — a cap each caller repeats is a cap that drifts. Naming nothing is not neutral: it silently selects the autopilot's budget, which is why this row is explicit (SCC-147) |
| `review_runtime` | `fan-out` or `inline` — **what you PROBED at Step 0.9, never what you expect.** Pass it down and write the same value into the walkthrough header, so the roster the engine returns can be checked against the runtime that produced it |

⚠ **Step 0 read `HEAD_SHA` from `PROJECT_ROOT` — the shared checkout — and before Step 0.7 absorbed
`origin/$EPIC`.** Re-read both it and the diff here, in `$WORKTREE`, or the engine reviews a tree that
no longer exists and your verdict cites a commit that is no longer the tip — the exact invariant Step
0.7 opens by stating.

**Ordering (deliberate): the engine hunts the DIFF first — open ②'s `walkthrough.md` and plan only
AFTER its summary comes back**, for claimed evidence, plan-vs-built deviations, and the `## Your
Actions` rows. Reading the builder's story before the hunt imports exactly the bias the Blind Hunter
exists to zero out, and that lens is starved of context on purpose — never hand it the story.

**Then fix in thread — act on what it hands back, here.** Every `patch` is applied by you, in this
story lane, now; every `decision_needed` is walked with the operator now, in this thread, and
becomes a patch or a dismiss on their word — one they do not decide now stays an open DECISION row
in `## Your Actions` (Step 5; a decision is theirs and may hold the story, it is not a ticket) with
its `defer` bullet pointing at that row. If you change code, re-run the relevant suite(s) —
scoped, not full; the ONE full-suite run lands after your last change (Step 3.1) — and paste
actual output. **Nothing that survived the relevance gate leaves this lane as future work** — not
a residue ticket, not a "proposed" or "decided" ticket, not a ticket-ruling row (operator ruling
2026-08-15, second: "we need the fixes made in thread not a ticket made every story"). The only
exception is a `defer` naming one structural blocker (another live lane owns the file · another
repo · an open decision), written to the project's `deferred-work.md`.

**The engine returns a `severity_floor`, and it BINDS Step 4.** `none` < `CONCERNS` < `FAIL`: your
verdict may be the floor or anything more severe (your own gates add their own reasons), never
anything less. A confirmed `critical` finding is a FAIL; an `important` one is a CONCERNS floor.

**Failure and degradation are the engine's to report, and yours to carry into the verdict.** It owns
the per-lens contract — retry once, re-run inline, and only a lens still dead after both raises the
floor — and reports each lens as `ok | recovered-inline | dead` plus any lens that was `n/a` for the
mode. **Copy that line into the verdict as it came back.** "4 lenses ran" and "3 ran plus 1 rerun
inline" are different evidence and must read differently; a lens skipped because there is no spec is
not a degradation and never caps the verdict, while one that never ran at all is an unexamined
surface — and an unknown is not a pass, the same rule as a missing tool in Step 3.5.

## Step 1.5 — Acceptance audit  *(against the story's acceptance criteria, not against the code)*

Recover the story's checkable list — the story file carries it, `/cicd-write-story-tests` turned it
into assertions, and the ticket's own acceptance block is the authority behind both
(`acli jira workitem view <JIRA-KEY>`).

**No double audit.** In `full` mode the engine's Acceptance Auditor lens already walked the diff
against that story — **import its findings** into the matrix below (source `review`) rather than
re-deriving them. What stays yours is the matrix itself: every item paired with the assertion that
proves it, which is a claim about evidence a lens cannot make for you.

For **each item**: name where the diff satisfies it, and **the assertion that proves it**. Then the
other direction — **anything in the diff beyond the list is drift**: cut it, or name why it stays.

**Then the SECOND left-hand side (SCC-231) — the declared set.** The acceptance list says what
must be TRUE; the plan's `## Declared Change Set` block says which files were meant to MOVE — a
file edited that satisfies an acceptance row but was never declared is invisible to the
reconciliation above. Diff the block against the real diff:

```bash
python3 .agents/scripts/declared_change_set.py diff <the plan> \
        --changed $(git -C "$PROJECT_ROOT" diff --name-only --no-renames <the same base this review resolved>)   # PC: `python`
```

(`--no-renames` matters: with rename detection on, a renamed file surfaces only under its NEW
path, so the declared `DELETE` of its old path reads as a false `unimplemented` row — and the
answer would depend on the machine's git config.)

<!-- twin-law: declared-drift -->
- **`undeclared`** = files(diff) − files(declared): a file the plan never named was edited.
  One finding per file, severity **important**.
- **`unimplemented`** = files(declared) − files(diff): declared and untouched — plan
  overreach, or dropped scope. One finding per file, severity **suggestion**.
- **`incomplete`** = declaration attempts the grammar rejected (a star bullet, a glob path, a
  missing row mapping) — the diff verb carries them through. One finding per bullet, severity
  **important**: a rejected declaration means the block cannot be trusted as the declared set,
  and its paths will read as `undeclared` noise until the bullets are repaired.
- An absent BLOCK returns `present: false` — that is itself ONE finding at **important**:
  "no declared set to reconcile against". Never a silent skip; the vacuous green is the exact case
  this side exists to catch. (An absent plan FILE is a loud exit-2 error — a broken invocation,
  never a state to reconcile.)
- Paths under `_artifacts/`, `_bmad/`, `_bmad-output/`, `_my_resources/` are carved out on BOTH
  sides — planning surfaces never count as drift (Step 1's raw diff still shows them).
- **Declared checks reconcile like declared files.** The plan's promised assertions and recorded
  evidence are part of the declared set: a promised check that shipped weaker — a presence pin
  where a mutation was promised, a recorded number that never landed — is drift — cut it, or
  name why it stays.
- **No drift row auto-fails the verdict.** Every drift row takes the same contract as the first
  side: cut it, or name why it stays.
<!-- /twin-law -->

- An item with **no evidence** is not satisfied, however obviously true it looks. **CONCERNS floor.**
- An item whose evidence is *"I read it and it looks right"* is not evidence. Run something.
- No acceptance list recoverable anywhere → say so and cap the verdict at **CONCERNS**; a review with
  no contract to review against is an opinion. (`no-spec` mode is exactly this case, declared up
  front rather than discovered here.)

## Step 2 — Gate: opt-in check
Read `_bmad-output/sudo-tests.yaml`.
- **Absent** → the project has no test baseline → verdict **`WAIVED`** (do NOT block). Skip to Step 4.
- **Present** → it defines `required_tiers · l1_coverage_min · agent_bearing · nfr · waive`. Continue.

## Step 3 — Gate: run the checks (baseline-diff aware — fail only on NEW regressions)

**Run every gate through `gate_receipt.py` — the verdict then cites evidence, not recollection.**

```bash
python3 .agents/scripts/gate_receipt.py run --story <id> --gate suite --cwd <worktree> \
       -- <the real command>          # EVERY flag precedes `--`; after it is the command verbatim
```

It executes the command, records the true exit code, the parsed totals **from the tool's own summary
line**, the git SHA, and whether the tree was dirty, into `_bmad-output/gates/<story>/<gate>.json`.
There is **no `--result` flag** — a verdict cannot be handed in, so a receipt implies execution. Commit
the receipts with the story: the evidence then rides the branch through the merge, and close-out can
re-check it without re-running anything. Three results, not two — `unrunnable` (the tool never ran) is
distinct from `fail`, because per Step 3.5 a missing tool is a **finding, not a skip**.

1. **Suite — ONE full run, measured on the FINAL SHA (diff-scoped stacks).** Stacks in scope = the ones
   the diff touched (backend pytest via `backend/.venv` with the project's canonical runner flags — the ONE
   source of truth is the runner AIDEV-NOTE in `backend/requirements.txt`; frontend vitest). Run the OTHER stack only when the diff touched a shared cross-boundary surface (API/SSE
   schema, shared types/contract files) — otherwise skip it and say so (PR CI + `/cicd-e2e` still run
   both stacks before anything ships). The verdict needs the full suite green exactly ONCE, on the exact
   code that will land — never burn a full run proving greens on code you are about to change:
   - **Inherit ②'s baseline instead of re-running it — via a MECHANICAL check, not a judgment call.**
     ② Step 4.5 emits `_bmad-output/test-artifacts/certification-<story>.json`
     (`{story, sha, utc, stacks:{<stack>:{cmd, passed, skipped, failed, seconds}}}`). Read it and compare
     its `sha` to `git rev-parse HEAD` on the worktree under review:
     - **`sha` == HEAD and `failed: 0`** → adopt as the entry baseline. Cite the file. Do not re-run.
     - **File absent, `sha` mismatched, a touched stack missing from `stacks`, or any `failed` > 0** →
       run the full suite up front yourself. **Fail toward running, never toward trusting.**
     No file (a pre-contract story, or a lane that skipped ② Step 4.5) → fall back to ②'s pasted
     walkthrough totals + SHA under the same equality test; anything less specific than an exact SHA is a
     miss, not a partial credit.
   - **While reviewing/fixing, run scoped** — the story's contract file + the suites of the modules you
     touched.
   - **After your LAST code/test change, run the FULL suite once** and paste the real output; record
     `git rev-parse HEAD` beside it, and **refresh `certification-<story>.json` to your SHA** (you are now
     the certifying run). Artifact/doc-only commits after this run do NOT invalidate it — only code or test
     changes force a re-run. Changed nothing at all? Then ②'s inherited green (SHA verified) IS the
     evidence — spot-run the story's own test file as a cheap independent probe and cite both. This
     replaces the old "full suite on arrival" rule, which could land a final SHA whose full green was
     measured on a DIFFERENT (pre-fix) SHA — the new invariant is strictly stronger.
   - **Append your suite runs to the walkthrough's `## Suite Ledger`** (the table is per STORY, ②+③) —
     `scope · command · duration · result · why this run`.
   Compare against the red baseline; only failures NEW to this story count (legacy red is grandfathered). **Three guards (per
   `tests-must-gate-for-real`):** (a) **CI-entrypoint audit — change-triggered, not per-story.** Run it only
   when the diff touches `.github/workflows/**` or a test-runner config, when `sudo-tests.yaml` has no
   `ci_audit:` record, or when `git log -1 --format=%H -- .github/workflows/` differs from the recorded
   `ci_audit.sha`. When it runs: open the pipeline YAML and confirm each test job invokes the project's
   actual harness command (e.g. `npm run test:e2e`), not a divergent/partial config — a green CI check on
   a suite that never ran is a FAIL, not a pass — then write `ci_audit: {sha, date}` back into
   `sudo-tests.yaml`. When skipped, state `CI audit current as of <sha>` in the verdict. (b) Grandfathering is for *owned* legacy red
   only (known-flaky / quarantined-with-ticket) — a red that asserts strings, selectors, or preconditions
   absent from real source is **fiction, not legacy debt**; do not grandfather it, FAIL and fix/delete it.
   (c) **A check that cannot fail is a finding.** If the diff adds a gate, a guard or a CI step, prove
   it **rejects** the case it must reject *and* **allows** the case it must allow —
   `tests-must-gate-for-real` § Mutation Testing (INVERT the decision). One half is not a gate.
2. **`bmad-testarch-trace`** — gate coverage vs `l1_coverage_min`.
3. **`bmad-testarch-nfr`** — when `nfr: true` or `agent_bearing: true`.
4. **`bmad-testarch-test-review`**. Also scan the CI pipeline for
   *soft* test steps (`continue-on-error`, `|| true`, blanket `.skip`/`xfail`, "report-only") — on the
   SAME change-trigger as guard (a), never per-story: each is a
   hole that reads as green. Per `tests-must-gate-for-real`, a soft gate is legitimate only as a one-run
   window carrying a named owner + a tracked expiry task — flag any that lacks both (CONCERNS floor) and
   name it in the verdict.
5. **Automate evidence** — feature stories only (numeric `E.S` ids; test-only MIN-FLOW stories like
   `tea-*` are exempt): confirm ②'s expansion pass left evidence — `automation-summary-<story>.md` under
   `_bmad-output/test-artifacts/`, or an explicit `## Automate: skipped — <rationale>` section in the
   story walkthrough. Missing BOTH → cap the verdict at **CONCERNS** and name the gap in the verdict
   section (never FAIL on this alone — stories gated before 2026-07-09 predate the check).

## Step 3.5 — Gate: clean code (ALWAYS runs — independent of Step 2's opt-in)
Invoke the **`cicd-clean-code-audit`** skill on the story diff, bound to the same worktree Step 0.5 resolved
(its standard is `.agents/rules/code-standards.md`).

- **No double drift-hunt (inside ③ only).** Step 1's adversarial review already walked these hunks —
  run the machine floor + the comment contract (§2A) only, and IMPORT Step 1's drift/bloat findings
  into the findings table (source `review`) instead of re-running the §2B ban-hunt. The full two-half
  pass is for standalone `/cicd-clean-code-audit` runs.
- **Diff-scoped.** Only code THIS story wrote is in scope; legacy debt in untouched files is noted, never
  gated on — the same grandfathering the test gate already uses.
- **This gate does NOT depend on `sudo-tests.yaml`.** A project with no test baseline still has a code
  standard, so a `WAIVED` test gate (Step 2) never waives this one.
- **A missing tool is a finding, not a skip** — `No module named ruff` means the floor is unrunnable and
  the project breaks `tests-must-gate-for-real` §2. Report it and name the fix.
- **An empty diff is a STOP, not a pass.** If the changed-file set comes back empty, say so and stop — a
  vacuously green gate is exactly what this step exists to prevent.

Fold its findings table into the verdict section **verbatim**, with the actual command output pasted. Apply
the fixes you can make safely, then re-run the affected check and paste the new output.

## Step 4 — Verdict (append to the walkthrough — NO separate file)
Combine into **PASS / CONCERNS / FAIL / WAIVED** and **append a `## Code Review (<date>)` section to the
story's `walkthrough.md`** (`_artifacts/epic_<E>/<story>/` — **inside the worktree Step 0.5 resolved**,
never the shared checkout; it rides the story branch through the close-out merge). A standalone verdict
file is retired per `artifacts-always-first` §6 — pre-2026-08-02 stories keep
`_bmad-output/implementation-artifacts/sudo-code-review-<story>.md` as read-only history; never write a
new one. The section carries:
- FIRST line: the canonical **`Verdict: PASS|CONCERNS|FAIL|WAIVED @ <HEAD-sha>`** — this is what
  `cicd-update-sprint-memory` reads before flipping the story to `done` — plus one line naming the SHA
  the full-suite evidence was measured on and whose run it was (②'s inherited certification or ③'s
  own). Any code/test diff between that SHA and HEAD invalidates the verdict.
- ⛔ **the engine's `lenses_run:` block, pasted VERBATIM** — the header line, then one
  `- <lens> · ok | recovered-inline | dead` row per lens, a `—` note on every row that is not `ok`:

  ⛔ **Shown UNFENCED because that is how it must land (SCC-240).** `walkthrough_roster.py`
  strips code fences before it reads anything (SCC-154 — a canonical verdict pasted as evidence
  inside a fence once became the governing verdict), so a roster inside a code fence is a roster
  the gate cannot see. Copy these as PLAIN LINES.

  lenses_run:
  - blind-hunter · ok
  - edge-case-hunter · recovered-inline — fan-out returned nothing, rerun inline
  lenses_counted:  2/2
  lenses_na:
  - <lens> · n/a — <why it was not applicable in this review_mode>

  ⭐ **Check the paste HERE, not at close-out** — `python3 .agents/scripts/walkthrough_roster.py
  <the walkthrough>` *(PC: `python`)*. It prints the rows it actually read and answers **one**
  question: can this roster be READ? Exit 0 yes; exit 1 names which of three things went wrong —
  a fenced roster, a header whose rows are not contiguous with it, or no roster at all; exit 2
  is a bad path, never a verdict about content.
  ⛔ **Bare, it is deliberately NOT the whole close-out gate**, and that is what makes it usable
  here: at this moment `dispositions:`, `drift:`, Step 0.7 and the `Verdict:` line are still
  unwritten, so a full-gate run would refuse on a missing `dispositions:` line and send you to
  hunt a fence that is not there. Once the section is complete, `--gate` asks the fuller
  question — and before the stamp exists it needs `--verdict PASS|CONCERNS|FAIL|WAIVED`.
  ⛔ **A re-reviewed STORY lane must pass `--verdict`**: `--gate` judges the LAST `Verdict:`
  stamp (the re-review rule), while `closeout_preflight` reads the FIRST, so a FAIL-then-PASS
  file resolves differently in the two. Task lanes go through `task_preflight`, which reads the
  last and agrees.

<!-- twin-law: roster -->
  ⛔ **`lenses_na` and `lenses_counted` are part of the block, not optional trimmings (SCC-203).**
  The engine returns four roster fields and this step used to demand one. Since a contaminated
  Blind Hunter is **DROPPED** rather than faked, `lenses_na` is now the ONLY legal record that it
  was dropped — `blind-hunter · n/a — context contaminated (<what it held>)` — and `lenses_counted`
  is what keeps the drop out of the total. Omitting them is how a dropped lens becomes invisible,
  which is the exact failure the drop rule exists to make visible.
<!-- /twin-law -->

<!-- twin-law: record-lines -->
- ⛔ **two more machine-read lines, in the same section (SCC-231/233, law since 2026-08-20):**

  ```
  dispositions:    per-lens: <lens>=<survived>/<dismissed>/<relevance-killed> · …
  drift:           undeclared=<n> · unimplemented=<n> · incomplete=<n> — <dispositions live in the findings table, or name why there was no block to reconcile>
  ```

  `dispositions:` is pasted from the engine summary VERBATIM — the per-lens death counts are the
  SCC-233 record, and which lens's findings die at triage is computable only if they land here.
  `drift:` is the declared-set reconciliation result from this command's own step, in one line.
  `walkthrough_roster.py` reads both and the close-out preflights BLOCK a lane missing either —
  the measured base rate for prose-only record obligations is 12 of 142, so neither line is left
  to memory.
<!-- /twin-law -->

  **A `Verdict:` is the review's conclusion; this block is what shows the review happened.** Without
  it the verdict is the only record of itself, and a walkthrough with zero lenses run merges clean —
  the defect SCC-173 was raised on. `walkthrough_roster.py` reads it here at close-out. Do not
  summarise it, do not re-order the rows into prose, and never write a state a lens did not report.
- scope + method, one line each; then ONE findings table (`file:line` · severity · failure scenario ·
  disposition applied @ sha / deferred — blocked by other live lane · other repo · open decision / dismissed — a relevance kill
  carries its one-line reason, pure noise is count-only) — **the authoritative copy**; the story file links here,
  never restates. (The engine's step-04 may leave unresolved findings as `[ ] [Review]…` action items
  in `STORY_FILE` so the builder sees them — that is a worklist, not a second record, and it carries
  no dispositions. Where the two differ, this table is right; reconcile the story's boxes to it.)
- each gate check's result in one line + the **actual** suite totals (runs also ledgered in
  `## Suite Ledger`), each **citing its receipt** — `suite: pass @ <sha> (gates/<story>/suite.json)`.
  Run `gate_receipt.py list --story <id>` and paste the block; an `unrunnable` row is a finding that
  caps the verdict at CONCERNS, and a gate with no receipt was not run, whatever the prose says,
- a `### Clean-Code Gate` subsection carrying Step 3.5's findings table and its pasted tool output.
- the acceptance matrix from Step 1.5 — every acceptance item → its proving assertion;
<!-- twin-law: rederive-record -->
- **Step 0.7's re-derivation**, under its own `### Step 0.7 — re-derivation` sub-heading as three
  numbered lines — what the landing ref moved under this diff, the true overlap + `merge-tree` result,
  and any sibling-lane landing-order dependency. "Nothing moved" is a reportable result; silence is
  not — `walkthrough_roster.py --gate` counts list rows under a heading matching `0.7`/`re-deriv`
  (E7) and refuses fewer than three.
<!-- /twin-law -->
- **FAIL** = a new test regression, a required tier missing, **or** a Step 3.5 machine-floor error on a
  changed line / a banned pattern shipped (bare `except:`, `any`, a committed secret).
- **CONCERNS** = soft issues only — including Step 3.5's judgment findings (missing story provenance, a
  stale `AIDEV-NOTE` the diff should have updated, bloat, duplication, an unowned TODO).
- **PASS** = all required tiers green **and** the clean-code floor green on changed lines.
- **WAIVED** = no test baseline (Step 2). Step 3.5 still ran — report its result inside the waiver.

> The split is deliberate: objective checks block a story, taste does not. Taste gets recorded, argued,
> and fixed on its merits — never used to stall a story on a reviewer's preference.

## Step 5 — Refresh the walkthrough body + clear `## Your Actions` (REQUIRED)
The walkthrough (`_artifacts/epic_<E>/<story>/walkthrough.md`, in the worktree) is the **living source
of truth** — your Step 4 section is part of it, and the body around it must not go stale:
- If you changed code: refresh what your fixes staled — the `## Evidence` AC matrix + test counts,
  **REPLACE** the pasted totals with your final run (+ SHA — a re-run replaces, only the
  `## Suite Ledger` accretes), and tick the `## Task Checklist` rows your fixes completed (add an
  indented finding bullet under the task it belongs to). If you changed nothing, the Step 4 section
  says so ("Changes applied: none — implementation correct as-is").
- **`## Your Actions` triage:** attempt every agent-solvable row yourself — a deferred suite run, a
  missing artifact link, a doc fix — and tick it with a one-line note. Leave ONLY genuine human calls
  (product decisions, live checks — things only they can DECIDE). Refresh the branch/commit summary
  after your worktree commits.
  ⛔ **And NEVER the ceremony's own steps** (SCC-193). "Land the branch on the epic", "then
  re-invoke `/cicd-close-story-merge-tree <story>`", "run the preflight" — the operator's
  **decision to proceed** is the sign-off (the word `approved`, or invoking the door —
  `/cicd-close-story-merge-tree`, or `/cicd-merge-epic-workingtrees` for a set), and from that word
  on every step is the ceremony's and the agent runs it. On this lane the door enforces it
  twice: its Step 2 runs `jira_feed.py check-actions` before the close-out commit, and its Step 4b
  runs `jira_feed.py finish --landing-ref "origin/$EPIC"` after the landing (SCC-210, SCC-242) —
  both **refuse** such a row. Nothing earlier does: neither this command nor `closeout_preflight.py`
  reads the rows, so a ceremony row you leave here is caught, but at the price of a branch already
  landed on the epic. The story door writes no PR ledger row; a row that names a door or opens with
  `the merge itself` is judged by `finish` against the ancestry of `origin/$EPIC`, never against its
  tick.
  ⛔ A row assigning ANY ticket born from review findings — a residue ticket ("One follow-on
  ticket for the N deferred items"), a "proposed" ticket, a "decided" ticket to rule on — is the
  retired defect (operator rulings 2026-08-15, both), never a valid action row: the survivors were
  fixed in Step 1, a `defer` names its structural blocker in the ledger, and a review never
  produces a ticket. An open box born from a finding holds the story on the review ladder — that
  is the loop, not a feature.
- **Hard rule: NEVER finish `/cicd-code-review` with the walkthrough body left stale after applying fixes.**

## Stay in lane
Commit your review fixes inside the story worktree (explicit paths) — but **never land on the epic
branch** (close-out's job), and never flip the story status or edit `sprint-status.yaml`; that is `cicd-update-sprint-memory`'s job
(it reads the walkthrough's `Verdict:` line first), and `cicd-close-story-merge-tree` lands the branch in its Step 3. Updating
`walkthrough.md` (Steps 4–5) is IN lane — that is documenting the review, not flipping status.

Optional additional input: $ARGUMENTS
