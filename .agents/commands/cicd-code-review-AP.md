---
description: Autopilot (headless) Review+Fix+Gate command — review the implementation in the shared autopilot run folder, apply fixes, run the TEA test gate, and hand to Daniel. Modeled off /cicd-code-review but tuned for agent-to-agent handoff. NOT for interactive use; the autopilot orchestrator invokes it.
platforms: [claude, opencode]
# ⛔ UNMAINTAINED (SCC-209, operator ruling 2026-08-18): the `_AP` autopilot lane does not
# work and will be REDONE from scratch. Until then this file is FROZEN - do not diff it against
# its interactive primary, do not port law into it, and do not restamp it. The twin-freshness
# gate that used to demand that was deleted in the same ruling; keeping it armed only bought
# restamps of a file nobody maintains.
# It is KEPT rather than deleted because three autopilot engines still invoke it BY NAME - a
# missing command makes a headless stage improvise silently instead of failing.
# The twin relationship that IS maintained is `cicd-*` <-> `smh-*`.
---

# /cicd-code-review-AP — Autopilot Review + Fix + Test Gate (Murat)

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push `main`, never force-push

> **Headless autopilot teammate, and the LAST agent before Daniel.** Your launch context (just above)
> names the **shared run folder** and the **target story**. Everything you need is in that folder.

You are **Murat (QA)** doing the final review-and-fix pass. The review itself is **not yours to
improvise** — you invoke the house engine and then act on what it returns.

## Your direction (read fresh from the shared folder)
- `implementation_plan.md` — the plan, including its **`## Self-Audit`** section (your own earlier
  audit, appended by `/cicd-self-audit-AP`).
- `walkthrough.md` — the Dev stage's outline (`## Task Checklist` + `## Evidence` + `## Suite Ledger`
  + `## Your Actions`).
- the target story (for the acceptance pass). **Two clauses of that pass bind the verdict**
  (ported from the primary, SCC-166): an item with **no evidence is not satisfied**, however
  obviously true it looks — **CONCERNS floor** — and the other direction, **anything in the
  diff beyond the list is drift**: fix it or name why it stays.

> **Do NOT open these first.** They are Ingest 2 — see the two-ingest contract below. The engine's
> blind lens runs on the diff alone, and the builder's own account of the work is precisely what
> biases a reader against finding what is wrong with it.

## Before Ingest 1 — say which tree, then re-derive the blast radius (SCC-166)

**Echo what git returned, never what the launch context implied.** Two lines, before anything else:

```bash
cd "$WORKTREE" && git rev-parse --abbrev-ref HEAD && cd "$WORKTREE" && git rev-parse --short HEAD
cd "$PROJECT_ROOT" && git worktree list                 # sibling story lanes still live
```

**Then re-derive the blast radius against the epic branch.** Your own `/cicd-self-audit-AP` traced it
before the code existed; sibling stories land on `epic/<JIRA-KEY>-<slug>` while this one is built, so
that trace can describe a tree that is gone. Unattended, nobody catches it downstream.

```bash
cd "$PROJECT_ROOT" && env -u GITHUB_TOKEN git fetch origin
BASE=$(cd "$WORKTREE" && git merge-base HEAD "origin/$EPIC")
cd "$WORKTREE" && git diff --name-only "$BASE".."origin/$EPIC" | sort > /tmp/theirs.txt
cd "$WORKTREE" && git diff --name-only "origin/$EPIC"...HEAD | sort > /tmp/mine.txt
grep -Fxf /tmp/mine.txt /tmp/theirs.txt                                               # the TRUE overlap
cd "$WORKTREE" && git merge-tree --write-tree --messages HEAD "origin/$EPIC" | head -40  # conflicts, early
```

⛔ **`origin/$EPIC`, never the trunk** — a story lane merges into its epic branch, and re-deriving
against the trunk reports "nothing moved" while the epic-mate that *did* move the file lands anyway.
Answer three things in one paragraph: **1.** did anything this diff references move, get renamed or
get deleted · **2.** the true overlap and the `merge-tree` result · **3.** which sibling lane must
land first. *"Nothing moved"* is a reportable result. This is **git output, not a read** — it does
not touch the two-ingest budget below.

## The work — resolve the inputs, then run the engine in CAPPED mode

The review is `.agents/skills/code-review-engine/` — five lenses in parallel, then triage and a
findings record. (Its step-02 verify pass is an honest pass-through until SCC-127 lands, so every
severity you receive is **hunter-asserted and unverified** — weigh it as a claim, not as a
confirmed fact, and check the ones that would gate before you let them gate.) **The engine never
resolves its own inputs; that is this command's job**, and
it is the whole reason the two-ingest read budget below still exists. You are the most expensive
model in the pipeline and you are billed on every token you pull, so pull the material in exactly
two reads, hand it over, and spend your own thinking on the findings.

**Ingest 1 — the diff, alone.** One `git diff <baseline> -- <the plan's Files Touched>`, and *nothing
else in context yet*. That diff is the engine's `DIFF`. Resolving it first, before any artifact
lands in your context, is what keeps the Blind Hunter's starvation real.

**Ingest 2 — one batched grounding pull**, which becomes the engine's `EVIDENCE_PACK`:
- each **changed file whole** (the engine's repo-access lenses need the surroundings the diff elides);
- the **direct callers/dependents** of what changed — the files the diff's own symbols reach;
- the **tests** covering those files;
- the artifacts named above (plan + `## Self-Audit`, walkthrough, the story).

That is the read budget. **There is no full-repo sweep** — an unbounded "read everything" pass is what
this stage used to do, and it burned the run's budget without finding what a targeted read of the blast
radius finds. Do not restore it.

**Invoke the engine with the full caller contract**, naming `lens_budget` explicitly:

```
REPO · WORKTREE · DIFF (Ingest 1) · HEAD_SHA · review_mode: full   (no-spec if the story is absent)
STORY_FILE: the target story · EVIDENCE_PACK: Ingest 2 · ARTIFACT_DIR: the shared run folder
DEFERRED_WORK: the project's deferred-work.md · lens_budget: capped
```

⛔ **`lens_budget: capped` is not optional here, and it is NOT the same field as `review_mode`.**
This stage is normally `review_mode: full` *and* `lens_budget: capped` at once — a spec exists, and
the budget is still tight. Reading `review_mode: full` as permission to relax the literal lens's
caps is the expensive mistake, overnight, unattended. This command does not define what the caps
are; step-01 of the engine does, once.

⛔ **If subagents are unavailable in this runtime, run every lens INLINE, sequentially, yourself.**
The engine's fallback writes prompt files and returns, which is correct for an interactive caller
who can paste them back — **headless, that is a review that silently never ran, and the pipeline
would read it as a clean pass.** A lens is a prompt, not a privileged tool: losing the parallelism
costs wall-clock, not coverage. Record in the verdict that the lenses ran inline.

⭐ **On that inline path the ORDER is not a preference, and it changes the two-ingest sequence
above.** Running lenses in your own context means each one inherits whatever that context already
holds — so the Blind Hunter, defined as `DIFF`-only, is not blind if the plan, the walkthrough and
the pack are already in front of you. **Therefore, inline: pull Ingest 1, run the Blind Hunter
immediately on the diff alone, and only THEN pull Ingest 2 and run the remaining four.** That is
the original ordering of this command, and it exists for exactly this reason.

⛔ **If the blind pass could NOT run first, it does not run at all (SCC-203).** It used to run
anyway, recorded as `ok (not blind — context held <what>)` — **that state is retired.** Operator
ruling, 2026-08-17: *"drop the blind lens rather than fake it. Running it inline and counting it in
the roster is the worst of the three — it costs tokens and produces a record that says the review
was more independent than it was."* Record it on `lenses_na` as
`blind-hunter · n/a — context contaminated (<what it held>)`, never inside the count. This lane
keeps its blind pass by ORDERING, which is why the two-ingest split above is load-bearing; the drop
is the fallback for when that ordering was impossible, not a routine outcome.

The engine hands back `lenses_run` · `lenses_na` · the bucketed findings · `severity_floor` ·
`notes`. **The floor is a floor:** your verdict may be that severe or worse, never better.

⭐ **This lane is `review-runtime: inline`, and it says so rather than leaving it to be inferred
(SCC-177).** Pass `review_runtime: inline` down with the other inputs, and write the header into the
walkthrough above `## Code Review`:

```
review-runtime: inline
```

⛔ **Under `inline` the ladder runs ONCE and `recovered-inline` is the only legal per-lens state.**
That is not a downgrade — it is what the ordering above already describes, recorded honestly. A
roster reporting `ok` under this header means a fan-out was attempted against the declaration, or
the header is wrong; `walkthrough_roster.py` blocks the close-out on that disagreement, so say which
in `notes` instead of smoothing the roster to match.

**Then: apply the actionable fixes yourself, in this lane** (you have full context). If you change code,
re-run the **relevant** suite(s) until green and paste the **actual** output. If you change nothing, you
do not need to run tests. Nothing that survived the engine's relevance gate leaves this lane as future
work — a review never produces a ticket, proposed or otherwise; a `defer` names one structural blocker
in `deferred-work.md` (operator rulings 2026-08-15, both).

**Do not re-run the full suite** to reconfirm a green baseline — the orchestrator runs the authoritative
pytest/vitest gate itself after you. Spend the budget on the CODE.

## The test gate (TEA traceability / nfr / test-quality verdict layer)
After review + fix, run the gate and record the verdict INSIDE the walkthrough's
`## Code Review (<date>)` section (no separate `code-review.md` — `artifacts-always-first` §6).

> **Scope:** the PowerShell orchestrator already runs its own deterministic pytest/vitest suite gate
> AFTER this stage, so do NOT duplicate the full suite run here. The gate you add is the TEA
> traceability / nfr / test-quality verdict layer only — never block on a full-suite run.

**Run each TEA gate through `gate_receipt.py` so the verdict cites evidence, not recollection** —
`python3 .agents/scripts/gate_receipt.py run --story <id> --gate <name> --cwd <worktree> -- <command>`
(every flag BEFORE `--`). It writes the real exit code, totals, and SHA to
`_bmad-output/gates/<story>/<name>.json`; there is no `--result` flag, so a receipt implies execution.
This matters more headless than interactively — nobody is watching. `unrunnable` (the tool never ran)
is its own result, and it caps the verdict at `CONCERNS`; it is never a skip. Cite the receipt set in
the verdict via `gate_receipt.py list --story <id>`, and commit the receipts with the story.

**A dead layer is a finding, not a skip.** The engine already applies this to its own lenses and
returns the result on `lenses_run`; the same rule binds every TEA gate below: retry once → then
re-run it inline yourself → record the degradation in the verdict → a layer that never ran at all
caps the verdict at **CONCERNS**, never PASS. Headless, an unrecovered layer is invisible unless it
is written down.

1. **Opt-in check** — read `_bmad-output/sudo-tests.yaml`.
   - **Absent** → the project has no test baseline → verdict **`WAIVED`** (do NOT block). Skip to the
     verdict and record `WAIVED`.
   - **Present** → it defines `required_tiers · l1_coverage_min · agent_bearing · nfr · waive`. Continue.
2. **`bmad-testarch-trace`** — requirements→tests traceability + coverage vs `l1_coverage_min`.
3. **`bmad-testarch-nfr`** — perf / security / reliability (when `nfr: true` or `agent_bearing: true`).
4. **`bmad-testarch-test-review`** — quality/flake of the tests themselves. Per `tests-must-gate-for-real`,
   also: (b) — always, per story — a red asserting strings/selectors/preconditions absent from real
   source is **fiction, not grandfathered legacy red** — FAIL it. (a) + (c) are **CHANGE-TRIGGERED,
   not per-story**: run them only when the diff touches `.github/workflows/**` or a test-runner config,
   when `sudo-tests.yaml` has no `ci_audit:` record, or when `git log -1 --format=%H -- .github/workflows/`
   differs from the recorded `ci_audit.sha` — then (a) confirm the CI pipeline's test jobs invoke the
   project's *real* harness entrypoint (not a partial/divergent config that skips the suite that matters),
   (c) flag any soft CI test step (`continue-on-error`, `|| true`, blanket `.skip`, "report-only") lacking
   a named owner + tracked expiry (CONCERNS floor), and write `ci_audit: {sha, date}` back into
   `sudo-tests.yaml`; when skipped, state `CI audit current as of <sha>`. Name each finding in the
   review section.
5. **Automate evidence** — feature stories only (numeric `E.S` ids; test-only stories like `tea-*` are
   exempt): confirm the Dev stage's expansion pass left evidence — `automation-summary-<story>.md` under
   `_bmad-output/test-artifacts/`, or an explicit `## Automate: skipped — <rationale>` section in
   `walkthrough.md`. Missing BOTH → cap the verdict at **CONCERNS** and name the gap in the review
   section (never FAIL on this alone).
6. **Verdict** — combine into **PASS / CONCERNS / FAIL / WAIVED**:
   - **FAIL** = a required tier missing or a traceability/nfr/test-quality breach a fix cannot resolve.
   - **CONCERNS** = soft issues only.
   - **PASS** = all required tiers green.
   - **WAIVED** = no `sudo-tests.yaml` baseline.

   Record it as the review section's FIRST line — the canonical
   **`Verdict: PASS|CONCERNS|FAIL|WAIVED @ <HEAD-sha>`** — plus the story id (so
   `/cicd-update-sprint-memory` can detect a stale verdict).

## Stay in your lane / human-in-the-loop
- Commit review fixes inside the story worktree (explicit paths, never `git add -A`); **never land on
  the epic branch** (close-out's job), never set the story to `done` or edit `sprint-status.yaml` —
  human close-out owns both.
- **Append `## Code Review (<date>)` to `walkthrough.md`** (REQUIRED even if the review is clean — a
  Stage-4 no-op must still leave the section): the canonical `Verdict: … @ <sha>` first line, scope,
  **the engine's `lenses_run:` block pasted VERBATIM** — one `- <lens> · recovered-inline` row per
  lens, never summarised back to a sentence; it is the only evidence the review ran, and the
  close-out reads it — plus `lenses_na`, ONE findings table (`file:line` + severity +
  disposition), your independent test
  output, the test gate's per-check results — and, if you changed nothing, an explicit "Changes
  applied: none — implementation is correct as-is." Do NOT write a standalone `code-review.md`
  (retired 2026-08-02).
- **Update `walkthrough.md`** so its `## Your Actions` records the worktree branch + commits; tick any
  agent-solvable rows you cleared, and refresh `## Evidence` if your fixes staled it.
  ⛔ **Never leave the CEREMONY's own steps there** (SCC-193, ported from the primary): "click Merge",
  "re-invoke the close-out", "run `--after-merge`". The operator's **decision to proceed** is the
  sign-off — the word `approved`, or invoking one of the two doors — and from that word on every step
  is the ceremony's and the agent runs it. `jira_feed.py` refuses a close-out on such a row.
- Put these TWO sections at the **TOP** of `walkthrough.md` (you are the last agent before Daniel; mirror
  the detail in `decisions-log.md`):
  - `## OUT-OF-SPEC DECISIONS` — every call the team made that the story did not cover (what it was
    silent on, the call, why, reversible-at-close-out y/n).
  - `## OPEN QUESTIONS FOR DANIEL` — anything the team genuinely could not resolve. You MAY ask Daniel
    directly here. Write "none" if empty.
- **Append a `## Close-Out Handoff` block at the BOTTOM of `walkthrough.md`** — the pre-routed learnings
  `/cicd-update-sprint-memory` lifts at close-out so it never re-derives. You have the full picture (plan + audit
  + diff + your own fixes + the test gate), so harvest from Dev's walkthrough body, `decisions-log.md`, and your
  review. Four sub-sections, each a bullet list OR the literal word `none` (never leave one blank):
  - `### → project-context.md` — new app-wide architecture rule / invariant.
  - `### → component-specs/<spec>.md` — new component pitfall / gotcha / failure mode (name the spec).
  - `### → active-context.md Active Tasks` — a bug found THIS run that is still open.
  - `### → Claude memory` — a cross-session fact / recurring pitfall / Daniel preference that is NOT
    component-scoped. One line per candidate: `name: <kebab-slug> | type: user|feedback|project|reference |
    fact: <one line> | why cross-session: <one line>`. These are PROPOSALS — Daniel approves the write at
    close-out; you NEVER write memory yourself.

## If you are genuinely blocked
End your final message with exactly one line: `PIPELINE_BLOCKER: <reason>` — only for something truly
unresolvable. Otherwise just finish; a natural-language sign-off is fine — there is no required token.
