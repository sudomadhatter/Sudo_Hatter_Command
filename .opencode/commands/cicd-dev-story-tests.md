---
description: Develop a story test-first — plan, then STOP at the self-audit gate (`continue` = audit here; `changed` = human switched the model, audit then stop to switch back; a pasted file path = another team's blind audit), implement, then auto-expand coverage. Step ② of the sudo dev flow.
platforms: [opencode, antigravity]
---

# /cicd-dev-story-tests — Plan → Self-Audit → Implement → Automate (②)

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push `main`,
>   never force-push; every commit leads with the repo's Jira key; ⛔ backticks in `-m "…"` EXECUTE — use `-F <file>`
> - `.agents/rules/worktree-per-story.md` — the story builds in a `claude/<JIRA-KEY>-<story-slug>` tree cut
>   from the EPIC branch, never `main`; §"Resuming" is why Step 0.6 re-enters, absorbs and links BEFORE it plans
> - `.agents/rules/000-PLAN-FIRST-GATE.md` — no project file is modified before the plan exists and the Step 2
>   stop has been answered; a fired Step 3.5 eject re-arms it in full
> - `.agents/rules/artifacts-always-first.md` — §2 the story folder + the plan's `## Declared Change Set`;
>   §5 the walkthrough outline; §7 the audit is appended INTO the plan, never a standalone file
> - `.agents/rules/tests-must-gate-for-real.md` — ①'s reds must fail for the RIGHT reason (Rule 1), Step 4.5
>   certifies at the shipping SHA (Rule 4), and Step 4's mutants follow its **§ Mutation Testing**. Loaded
>   HERE, at the command that writes the assertions — it used to arrive only at ③ (SCC-145)
> - `.agents/rules/reproduce-before-you-fix.md` — **when the story is a BUG fix**: reproduce → minimize → pin
>   a test seen red → falsify one hypothesis at a time → minimal fix → prove by reverting
> - `.agents/rules/work-consolidation.md` — rule 1, where a defect met while building GOES: this story's own
>   checklist → an open thematic parent → the open rolling ticket (found by LABEL) → mint, and say what you looked at
> - `.agents/rules/code-standards.md` — the AI-drift ban *no scope creep beyond the story* (surgical changes),
>   and §6.5 disposition: act on a finding only if it is REAL, changes BEHAVIOUR and is in THIS diff

Thin orchestrator — builds the story against ①'s red tests and ends with expanded coverage. Project-scoped
(targets THIS repo).

> Flow position: `cicd-write-story-tests` → **`cicd-dev-story-tests`** → `cicd-code-review`.

## Step 0 — Resolve the target project (FIRST — before any other step)
Bind the target per `.agents/rules/smh-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override (remainder = the real argument: story id, focus…) → `.agents/active-project.txt` → else **STOP
and ask** — never guess, never operate on the lobby. Set `PROJECT_ROOT` and **echo exactly**
`Target: Projects/<name>` before any work. Every bare path below resolves under `PROJECT_ROOT` (nested
`bmad-*`/`1_*` skills bind their `{project-root}` to it); a needed path missing under `PROJECT_ROOT` →
STOP and say so, never fall back to the lobby.

## Step 0.5 — Resolve & create the artifact folder (BEFORE any sub-skill writes a file)
Per `artifacts-always-first` §2, everything this flow produces lands in ONE story-scoped folder — set it
now: numeric `E.S` → `ARTIFACT_DIR = PROJECT_ROOT/_artifacts/epic_<E>/story-<E>-<S>-<short-title>/`
(create `epic_<E>/` if missing; reuse the existing folder on a resume) · TEA / non-numeric id →
`PROJECT_ROOT/_artifacts/tea/<story-slug>/` · no story id → `PROJECT_ROOT/_artifacts/_main/<YYYY-MM-DD>_<slug>/`
(the holding bucket; never a dated folder at the `_artifacts/` root). **Echo** `Artifacts: <ARTIFACT_DIR>`
before Step 1; pass it explicitly to each sub-skill and **never** let one mint its own root-level or
date-stamped folder.

## Step 0.6 — Re-enter the story worktree, absorb the epic branch, link assets, read the siblings (fresh-chat resume)
Before any planning or edit: `git -C "$PROJECT_ROOT" worktree list` (`worktree-per-story` → "Resuming").
A `claude/<JIRA-KEY>-<story-slug>` tree exists → **cd into it and re-bind everything below under it** — story file,
① red tests, `ARTIFACT_DIR`, test commands (they commonly live ONLY in that tree; skipping this plans
blind or opens a duplicate). None → first work session; `bmad-dev-story` opens one at first edit, off the
EPIC branch. Echo the case (`Worktree: reused <path>` / `none yet — opens at first edit`). Then, in order:

1. **Reusing a tree cut earlier? Absorb the EPIC branch FIRST, before the first edit.** A tree cut at ①
   and picked up days later is branched from an epic branch its sibling lanes have since moved:
   ```bash
   git -C <tree> fetch origin && git -C <tree> merge --no-edit origin/epic/<JIRA-KEY>-<slug>
   ```
   Conflicts here are cheap and yours; the same conflicts at ③'s absorb are on the epic branch's
   doorstep. A conflict → resolve it in the tree and note it in the plan; never `--hard`, never force
   (`git-policy`).
2. **Link the gitignored assets.** A worktree inherits no `.env`, `backend/.venv`, `auth_keys/` or
   `node_modules`, and pytest / uvicorn / `next dev` / the emulators resolve them relative to CWD — so
   Step 3's scoped suites and Step 4.5's certification cannot run in an unlinked tree, and running them
   in the shared checkout certifies the wrong tree. Idempotent: a resumed lane re-runs it safely; the
   prune's `--unlink` (`/cicd-prune-worktree`) is its pair.
   ```bash
   python3 .agents/scripts/link-worktree-assets.py "$PROJECT_ROOT"/.claude/worktrees/<story-slug>   # PC: `python`
   ```
   On the none-yet path, run it the moment `bmad-dev-story` opens the tree.
3. **Read the sibling lanes NOW, not at review time.** Other `claude/*` trees on this epic carry
   uncommitted work `grep` cannot see:
   ```bash
   git -C "$PROJECT_ROOT" worktree list
   git -C <each-other-tree> diff --name-only origin/epic/<JIRA-KEY>-<slug>...HEAD
   git -C <each-other-tree> status --short
   ```
   Any file in both their set and your intended set is a **landing-order dependency**: say which lane
   should land first and what happens to your work if it does not, and carry it into the plan (Step 1's
   `## Declared Change Set` is the list it is checked against).

## Step 0.7 — BDD contract gate (HARD — before any planning or code)
The BDD Vision Lock is a standing phase of this flow: **a story may not be planned or implemented without
its locked behavior contract or a recorded waiver.** Check the story frontmatter, then verify on disk (a
flag with no file behind it fails the gate):
- **`bdd: locked`** AND every `bdd_contract:` path exists on disk (BDD scenarios inside the story's ATDD red
  files — the default — or opt-in `.feature` files) → proceed; those contracts are part of the ① red set
  Step 3 drives green. A `locked` record whose cited files are missing **fails the gate** — fix the
  frontmatter or re-lock, never wave it through (Epic 17.7 shipped a `locked` record backed by zero files).
- **`bdd: waived — <rationale>`** (explicit, human-approved) → proceed; note the waiver in the plan.
- **Neither** (incl. stories predating this gate, no `bdd:` key) → **STOP. Do not plan or code.** Run
  **`/cicd-bdd-tests`** now (interactive — human in the loop); continue only once the story carries a real
  contract or waiver. Never grandfather silently, never author the "lock" yourself.

## Step 0.8 — ⭐ Probe the review runtime and RECORD it (before any plan — SCC-177 / SCC-203)
**Can this session fan out to subagents?** Answer from THIS runtime, never from what usually happens — a
headless pipeline or a platform with no subagent tool is `inline`, and both are invisible until a lens
fails to launch. ⛔ **The probe is a capability, never a policy.** *Does a subagent tool exist here?* is
the whole question; *am I permitted to use it?* is a different one, and answering it here is how a
session directive (*"Do not call the AgentTool unless the user requested it"*) got read as *"this runtime is inline"* and a
whole review ran inside the builder's own context (SCC-203). ⭐ ***Am I permitted?* is already
answered — the operator invoked a `/` command, and a `/` command IS a user request**; the directive
*"Do not call the AgentTool unless the user requested it"* is **satisfied by that invocation**. Never stop to
ask, never quietly downgrade. ⛔ If you still believe you cannot, you may not record a bare `inline` —
write `inline (blocked: <what blocked you, verbatim>)`, because a bare `inline` from a runtime that HAS
the tool is indistinguishable from one that never had it, and that is the whole defect.

Write the answer as the **first line of the walkthrough header** Step 5 creates:

```
review-runtime: fan-out
```

It records ②'s runtime. ③ (`/cicd-code-review` Step 0.9) re-probes in its own session and overwrites
the line if its runtime differs; a ③ that skips its probe inherits this one, and `walkthrough_roster.py`
blocks the close-out when the roster disagrees with the header (`inline` + a lens reporting `ok`, or
`fan-out` + a lens `recovered-inline`).

## Step 1 — Plan
Invoke **`bmad-dev-story`** in PLAN mode for the story in `$ARGUMENTS`. Produce its `implementation_plan.md`
**into `ARTIFACT_DIR`** — not the BMAD stories dir, not the `_artifacts/` root. The plan carries the
**`## Declared Change Set` block** (`artifacts-always-first.md` §2 Create the artifact folder + plan, SCC-226): one path per
bullet, `NEW`/`EDIT`/`DELETE`, `→ <the AC it serves>` — Step 1.5's drift check reconciles the real
diff against exactly this list.

## Step 2 — Self-audit STOP gate (MANDATORY — stop the moment the plan is written)
The plan exists; **STOP before the audit and before any code.** This stop lets the human switch the model
for the audit, or hand it to another team (a different LLM, blind).
**You can NEVER switch the model yourself — never offer to.** Only the human can (e.g. `/model`).

Post the gate message — short, ALWAYS with the clickable plan link (never a bare path):

> "Plan ready → **[implementation_plan.md](<ARTIFACT_DIR>/implementation_plan.md)**
> **1.** `continue` — audit runs here · or switch your model first, then say `changed`
> **2.** handoff to another team — paste the audit file's path here when it's done."

Then **WAIT — modify NO project file, write NO code.** The reply IS the trigger:

- **`continue`** — no model change. Run **`/cicd-self-audit`** on the plan here (pre-dev adversarial
  stress-test). **Persist by appending `## Self-Audit (<date>)` INTO the plan** (with its
  `Audit verdict:` line) — inline-only findings do NOT satisfy the protocol, and a standalone audit
  file is retired (`artifacts-always-first` §7). ⛔ **Then READ the `Audit verdict:` line. A `NO-GO`
  stops the lane** — fix the plan and re-audit; do not proceed on a `NO-GO` and do not re-run it hoping
  for a different answer; a `NO-GO` the plan cannot cure without re-scoping fires Step 3.5. On **`GO`**
  go straight on (Step 2.5 → 3 → 4 → 5) — **no second gate**.
- **`changed`** — the human ALREADY switched the model; the audit lane. Run **`/cicd-self-audit`** now (on
  the switched model), persist + fold as above — then **STOP AGAIN**: *"Audit done — switch back, then say
  `continue`."* WAIT before Step 2.5/3 — **never implement on the audit-switched model.** This switch-back
  gate exists ONLY after `changed`.
- **A pasted file path** — another team ran the audit blind; the path IS the handoff. Read it and
  append its content into the plan's **`## Self-Audit (<date>)`** section (source noted in the
  heading); fold its findings into the affected plan sections, then proceed — no further stops.
- **Explicit "skip the audit"** — confirm once; on yes, add the one-line `## Self-Audit` section to
  the plan — `Audit: skipped by human decision (<date>)` — so the Step 5 checklist stays honest, and
  proceed.

**`continue` always means: on a `GO` verdict, run the remainder (Step 2.5 → 3 → 4 → 5) without further
stops** — subject only to Step 2.5's real-questions rule and the `changed`-path switch-back stop above.
The verdict is read on every path (`continue`, `changed`, a pasted audit); a `NO-GO` is never run past.

## Step 2.5 — Gate: ask first, but ONLY if you have questions
A **conditional** gate — not a mandatory approval stop. After the plan + audit, decide honestly whether you
have real questions: a genuine ambiguity, a decision only the human can make, contradictory ACs, or a plan
concern the audit raised that you can't safely resolve yourself.
- **Have questions → STOP before any code.** Ask concisely in chat (web/mobile: the tap-to-approve chip) and
  wait. Modify NO project file until resolved. This gate OVERRIDES bmad-dev-story's no-pause directive — but
  only here, and only because you have questions.
- **No questions → go straight to Step 3.** Don't manufacture one; an unambiguous plan just gets built.

## Step 3 — Implement
Invoke **`bmad-dev-story`** in IMPLEMENT mode: apply the audit, write the code, and drive the ① red tests —
**including the BDD contract scenarios from the Vision Lock (Step 0.7)** — to green. Run **scoped** suites
while you iterate (the story's files + touched modules), and finish this step with one targeted
**blast-radius pass** over the suites your changed files share — fail fast on collateral while context is
hot. If a test fails, find root cause before fixing.

**Run the ① reds FIRST and paste the actual RED output — before the first edit.** Then read WHICH LINE
RAISED: a red that dies in setup (a fixture that throws, a missing conftest env var, a bad import) looks
identical to one that fails its assertion, and only the second is a real red. A setup death is a fixture
defect — fix it, re-run, see the red on its assertion, and only then drive it green
(`tests-must-gate-for-real` Rule 1; memory `red-test-can-die-before-its-assertion`).

**Do NOT run the full suite in this step** (`tests-must-gate-for-real` Rule 4 — scoped runs are *feedback*,
the full suite is *certification*). Step 4 adds tests, which stales any totals produced now; **Step 4.5 owns
the one certification run.**

**Every ① red ends green or is quarantined — never shipped red (`tests-must-gate-for-real`).** A red that
can't go green is the tell ① handed you **fiction** — it asserts what the design never had (copy absent from
source, an auth-gated page assumed "public"). Fix it to the real contract or drop it with a one-line note;
never delete-to-force-green.

> ⭐ **A defect met while building is NOT automatically a new ticket (`work-consolidation.md` rule 1).**
> Look for a home, in order, before you mint: (1) **this story's own scope** — a line in the story file's
> `Tasks / Subtasks` checklist, fixed here; (2) an **open thematic parent** on the project's board (the
> project from `.agents/jira.conf`); (3) the project's **open rolling `Bugs and Updates` ticket, found by
> LABEL** (`labels IN (bugs-and-updates, running-bug-list)`), never by a remembered key; (4) mint — only
> for a lane in its own right, and only after saying in ONE line what you looked at. ⛔ **Never a
> `Subtask` under the story** — `jira.md` §Subtasks: a BMAD Story's breakdown lives in its story file
> and board row (**NEVER** subtasks); rungs 2–3 file under a Task, rung 1 is a checklist line. Judgment,
> not a gate — the unstated choice is what is banned. Record the decision in the walkthrough under the
> task that met it.

## Step 3.5 — ⛔ EJECT TRIPWIRE (check here, and again as you go)
**STOP and hand the work over if any of these is true:**
- **The work is Task-shaped** — no story id, no board row, no epic branch (toolkit, rules, docs, config).
  Hand it to `/smh-quick-dev` (it acts on the repo you are standing in).
- **The audit returned `NO-GO` and the plan cannot be fixed without re-scoping** (Step 2), or **the
  built scope has diverged from the story's ACs** — they no longer describe what can be built. Route to
  `bmad-correct-course`; never re-scope silently inside the story.
- **A finding is bigger than a trivial patch** — a Step 4 coverage gap, a Step 4.5 red, or a
  blast-radius failure that needs design rather than a fix.

Report the one-line reason; keep the worktree and everything written. Discard nothing. A fired eject
re-arms `000-PLAN-FIRST-GATE` in full — the re-scoped story needs a new plan and a new Step 2 stop.

## Step 4 — Automate (expand coverage)
Invoke **`bmad-testarch-automate`** to expand API / UI / contract coverage around what was built — closing
gaps the ATDD pass missed. **Leave evidence:** persist its summary as
`_bmad-output/test-artifacts/automation-summary-<story>.md`; if expansion is genuinely N/A, write a
`## Automate: skipped — <rationale>` section into the walkthrough instead. A silent skip is an unfinished
Step 4 — the Step 5 checklist and the ③ gate verify this.

**Structural reds are wiring proofs, never behavior proofs.** If ① left structural-only guard/wiring reds
(source-contains asserts), behavioral coverage is **owed here**, not optional, with a **positive control**
on every scenario — and a test you have never seen fail is a claim, not a check. Prove every new check
non-vacuous by **mutation**, per `tests-must-gate-for-real` **§ Mutation Testing**:
- **Declare the mutant table BEFORE you mutate** — one row per mutant: the mutant · the file · **the NAMED
  case it must kill** — and run it as **ONE sweep**, never one mutant at a time.
- **Draw every mutant from a decision in the source under test, never from your own cases** —
  case-derived mutants prove only that the suite agrees with itself (SCC-144: 14 case-derived all
  killed, 24 of 25 code-derived survived). Pick the technique by shape: **RELOCATE** a guard below the
  write it protects (same-file structural + behavioral; never DELETE it); **INVERT** one decision for a
  gate, hook or shell check; sweep **narrowings** too, not only deletions.
- **Restore in a `finally`/trap and re-check `git status` when the sweep ends**, then run the affected
  test files **bare, unfiltered, once** — the closing green is not the kills.
- **A surviving mutant is a finding; a mutant whose edit is not in the original text is DEFECTIVE** and
  counts as a survivor until re-aimed. Record the finished table (mutant · file · case · outcome) in
  the walkthrough. (`mutation_sweep.py` is bound to the lobby harness — `--case`, exit 3, `FAILED:`
  lines — and does not drive pytest/vitest; the declared table and the sweep discipline are what you owe.)

⛔ **Never write an assertion after the edit and present it as a red.** A characterization check written
green is honest — label it `characterization` in the walkthrough's `## Evidence`; a green check
presented as a red is not.

## Step 4.5 — Certify at the shipping SHA (the ONE full-suite run)
Governed by `tests-must-gate-for-real` Rule 4 — certification is measured at the SHA that ships, and nothing
before this step counts. In order:

1. **Machine floor, ONCE, over the final changed-file set** — ruff + pyrefly on changed files (both HARD
   gates lint WHOLE files, so inherited debt in a file you touched is yours). If `--fix` altered anything,
   re-run the story contract set.
2. **Commit** (explicit paths, never `git add -A`) — the SHA has to exist before a run can name it.
   ⛔ **Backticks in `-m "…"` EXECUTE.** A message quoting a shell command runs it. Use `git commit -F
   <file>` whenever the message contains a backtick.
3. **ONE full-suite run per touched stack — THROUGH THE RECEIPT WRITER, stamp-first.** The first full
   run of the landing code goes through `gate_receipt.py`; ⛔ do **not** run the runner bare "to check"
   and then again through the writer — one suite paid for twice, and only the second run is evidence.
   ```bash
   python3 .agents/scripts/gate_receipt.py run --story <id> --gate suite \
          --project "$PROJECT_ROOT" --cwd <worktree> \
          -- <the canonical runner>     # EVERY flag precedes `--`; after it is the command verbatim
   ```
   ⛔ **`--cwd` and `--project` are different questions, and only one of them is answered by
   `--cwd`.** `--cwd` says *where the runner executes*; `--project` says *where the receipt is
   written*. Left unbound, the project resolves from the shell's cwd — the shared checkout — so the
   receipt lands in a tree that does not contain the sha it just recorded. "Commit it with the story"
   is then impossible, and ③'s `gate_receipt.py list --story <id>` prints `(no receipts)` from the
   worktree, which that step reads as a finding against a run that actually happened. (The Task lane
   uses `--root <the task's _artifacts dir>` instead; the two are mutually exclusive.)
   backend: `backend/.venv` pytest with the project's canonical runner flags (the runner AIDEV-NOTE in
   `backend/requirements.txt` is the ONE source of truth). E2E tier touched → the **FULL-TREE** emulator
   run; `-k`/single-file emulator runs are debug-only and **never citable**. The receipt records the
   true exit code, the totals parsed from the tool's own summary line, the SHA, and whether the tree was
   DIRTY — commit it with the story. **A red receipt is the mechanism working**: fix, re-commit,
   re-stamp; only the LAST receipt is the certification. Stamp on a clean tree (item 2 first) — a
   receipt over uncommitted code records `DIRTY` and inherits as invalid, correctly. Still **paste the
   actual output** — the receipt is additional evidence, never a substitute for reading the run.
4. **Emit the certification handoff — DERIVED from the receipt, never typed** —
   `_bmad-output/test-artifacts/certification-<story>.json`, one `stacks` entry per stack you ran:
   `{"story","sha","utc","stacks":{"<stack>":{"cmd","passed","skipped","failed","seconds"}}}`, every
   number copied from the receipt's totals and `sha` (③ reads this file AND `gate_receipt.py list
   --story <id>`; a pair that disagrees is a finding) — **and**
   paste the actual output + `git rev-parse HEAD` into the walkthrough. **INVARIANT: the totals MUST come
   from a run at exactly that SHA.** Any code or test change after it voids the pair (repeat from 2);
   artifact/doc-only changes are exempt. ③ compares this `sha` to the HEAD under review — match → it
   inherits your green; miss → it pays for the full suite again.
5. **Finalize the automate summary's suite-result line NOW** — summary, JSON, and walkthrough carry the
   SAME pair; never two documents with divergent totals. **Re-run nothing this run subsumes** — a hedge is
   a Suite Ledger row that needs a written "why."

## Step 5 — Close-out artifacts (MANDATORY — never skip, even on "just do it")
The Always-On **`artifacts-always-first`** rule governs this step. Before reporting Done, `ARTIFACT_DIR`
MUST hold the TWO living docs, each carrying the `IsArtifact: true` + `ArtifactMetadata` frontmatter
(correct `type:`):

- [ ] **`implementation_plan.md`** (`type: implementation_plan`) — from Step 1, frontmatter present
      (§2), **including its `## Self-Audit (<date>)` section** with the `Audit verdict:` line (appended
      at Step 2 — a standalone audit file is retired per §7; a missing section = Step 2 never ran).
- [ ] **`walkthrough.md`** (`type: walkthrough`) — the ONE closing doc, outline-first (§5):
      `review-runtime: fan-out|inline` as the header's first line (Step 0.8) → header →
      **`## Task Checklist`** (final TodoWrite snapshot as the outline — pitfalls, findings, and
      plan-vs-built deviations indented ONLY under the tasks that fought back; clean tasks bare) →
      **`## Evidence`** (the ONE AC→evidence matrix — each AC row carries its ① RED output (the line
      that raised) then the GREEN output, or `characterization` where a check was born green — + the
      **actual pasted** certification totals + SHA)
      → a **`## Suite Ledger`** section (below) → **`## Your Actions`** (what landed — worktree branch +
      commits — plus anything still on the human). ③ appends `## Code Review` later — never pre-write
      it. **Required even when told to "skip the plan, just do it" — the walkthrough is never
      skippable.**
- [ ] **`## Suite Ledger`** — one row per suite invocation this story:
      `scope · command · duration · result · why this run`. The Step-4.5 certification row carries the SHA.
      The table is **per story, not per command** — ③ appends its own rows to it. This is how a redundant
      run becomes visible: a hedge re-run has to write down its "why."
- [ ] **Certification handoff (Step 4.5)** — `_bmad-output/test-artifacts/certification-<story>.json` exists
      and its `sha` equals the current HEAD (artifact/doc-only commits after it are exempt).
- [ ] **Automate evidence (Step 4)** — `_bmad-output/test-artifacts/automation-summary-<story>.md` exists,
      OR the walkthrough carries an explicit `## Automate: skipped — <rationale>` section. (Lives with the
      TEA outputs, not `ARTIFACT_DIR`.) A silent skip fails this checklist.

Post a clickable Markdown link to every artifact in the chat that same turn — never a bare path.

## Done
Report: plan-vs-built deltas, audit findings applied, tests now green (paste output), coverage added, and
the two Step-5 artifact links. Hand to `cicd-code-review`. The dev step **may advance the story to
`review`** — bmad-dev-story's Step 9 does this and we let it. **Never flip to `done`** — Daniel's call at
close-out via `/cicd-close-story-merge-tree`, whose `/cicd-update-sprint-memory` save owns the flip.
**Git:** commit freely inside the story worktree (explicit paths, never `git add -A`; `-F <file>` when
the message holds a backtick); do NOT land it on
the epic branch — Step 3 of `/cicd-close-story-merge-tree` owns that push (→ `worktree-per-story`).

Optional additional input: $ARGUMENTS
