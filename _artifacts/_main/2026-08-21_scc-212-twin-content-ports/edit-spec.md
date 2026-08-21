---
IsArtifact: true
ArtifactMetadata:
  title: "SCC-212 — edit spec: every live finding, its HEAD anchor and its text"
  type: implementation_plan
  date: 2026-08-21
---

# SCC-212 — edit spec (re-measured at `origin/main` @ `295abe5`)

Companion to `implementation_plan.md`. Seven read-only re-measurement passes (one per target file)
re-anchored every backlog finding on the CURRENT text — the backlog's line numbers were taken at
`fd22097` and are stale everywhere. This file is the build spec: one section per target file, one
entry per live finding, **anchor = verbatim HEAD text**, **new text = ready to paste**. Where the
backlog's own edit is wrong at HEAD, the entry says so and what replaces it.

Conventions: `WT` = the lane's worktree. smh source lines are quoted where the wording is carried;
only subject-forced words change (epic branch vs `origin/main`, story file vs plan, `--story <id>`,
`PROJECT_ROOT` binding). `⛔ FENCE` marks a region that becomes `<!-- twin-law: <id> -->` on BOTH
sides.

---

## 1 · `cicd-dev-story-tests.md` (14 live) + `cicd-write-story-tests.md` + `git-policy.md`

### E1 — DEV-14 + DEV-15 + DEV-16 (+ DEV-01 pointer) · rules-in-force block
Replace `:8-9`:
```
> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push `main`, never force-push
```
with:
```
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
```
Lint: E4 introduces the literal `NO-GO`, which `_RULE_POINTERS` maps to `code-standards` → **E1 and E4 land together.**
Also: extend `test_command_surfaces.py` `LOADERS` with `"cicd-dev-story-tests.md"` and fix its comment (the block now exists).

### E2 — DEV-10 + DEV-11 + DEV-12 · Step 0.6 rewritten
Replace the whole Step 0.6 (`:33-38`, heading `## Step 0.6 — Re-enter the story worktree if one already exists (fresh-chat resume)` through `` case (`Worktree: reused <path>` / `none yet — opens at first edit`). ``) with:
````
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
````
Source smh-quick-dev `:100, :105-113, :139-149`. Backlog's `cicd-close-workingtree.md:228` is a dead name → `/cicd-prune-worktree`.

### E2b — DEV-12 sibling · `cicd-write-story-tests.md`
Insert after `:29` `` `story-<id-dashed>-<short-name>`, e.g. `story-21-3-student-archive`. `` (end of list item 2, before `**Ordering caveat:**`):
```
3. **Either way, link the gitignored assets** — `python3 .agents/scripts/link-worktree-assets.py
   "$PROJECT_ROOT"/.claude/worktrees/<story-slug>` (PC: `python`). A tree has no `.env`, `backend/.venv`,
   `auth_keys/` or `node_modules` of its own and the runners resolve them relative to CWD, so Step 3's
   reds cannot even be run red without it. Idempotent on a re-entered tree; `/cicd-prune-worktree`
   runs the `--unlink` half before the tree is removed.
```

### E3 — DEV-04 · new Step 0.8 (probe BEFORE the plan)
Insert after `:51` `contract or waiver. Never grandfather silently, never author the "lock" yourself.` and before `## Step 1 — Plan`:
````
## Step 0.8 — ⭐ Probe the review runtime and RECORD it (before any plan — SCC-177 / SCC-203)
**Can this session fan out to subagents?** Answer from THIS runtime, never from what usually happens — a
headless pipeline or a platform with no subagent tool is `inline`, and both are invisible until a lens
fails to launch. ⛔ **The probe is a capability, never a policy.** *Does a subagent tool exist here?* is
the whole question; *am I permitted to use it?* is a different one, and answering it here is how a
session directive (*"do not spawn subagents unless asked"*) got read as *"this runtime is inline"* and a
whole review ran inside the builder's own context (SCC-203). ⭐ **Subagents are the DEFAULT, and
invoking an audit or a review IS that request** — never stop to ask for them, never quietly downgrade
to `inline`. Only a runtime with no subagent tool at all is `inline`.

Write the answer as the **first line of the walkthrough header** Step 5 creates:

```
review-runtime: fan-out
```

It records ②'s runtime. ③ (`/cicd-code-review` Step 0.9) re-probes in its own session and overwrites
the line if its runtime differs; a ③ that skips its probe inherits this one, and `walkthrough_roster.py`
blocks the close-out when the roster disagrees with the header (`inline` + a lens reporting `ok`, or
`fan-out` + a lens `recovered-inline`).
````
Plus replace `:160` `` - [ ] **`walkthrough.md`** (`type: walkthrough`) — the ONE closing doc, outline-first (§5): header → `` with `` - [ ] **`walkthrough.md`** (`type: walkthrough`) — the ONE closing doc, outline-first (§5): `review-runtime: fan-out|inline` as the header's first line (Step 0.8) → header → ``.
Sibling (code-review §6 E7): `cicd-code-review.md:133-134` "the dev-side commands do not carry this header … (F24)" becomes false — reword to "② records its own; ③ re-probes and overwrites".

### E4 — DEV-06 (+ DEV-09 shared NO-GO)
Replace `:73-77`:
```
- **`continue`** — no model change. Run **`/cicd-self-audit`** on the plan here (pre-dev adversarial
  stress-test). **Persist by appending `## Self-Audit (<date>)` INTO the plan** (with its
  `Audit verdict:` line) — inline-only findings do NOT satisfy the protocol, and a standalone audit
  file is retired (`artifacts-always-first` §7). Then go straight on (Step 2.5 → 3 → 4 → 5) — **no
  second gate**.
```
with:
```
- **`continue`** — no model change. Run **`/cicd-self-audit`** on the plan here (pre-dev adversarial
  stress-test). **Persist by appending `## Self-Audit (<date>)` INTO the plan** (with its
  `Audit verdict:` line) — inline-only findings do NOT satisfy the protocol, and a standalone audit
  file is retired (`artifacts-always-first` §7). ⛔ **Then READ the `Audit verdict:` line. A `NO-GO`
  stops the lane** — fix the plan and re-audit; do not proceed on a `NO-GO` and do not re-run it hoping
  for a different answer; a `NO-GO` the plan cannot cure without re-scoping fires Step 3.5. On **`GO`**
  go straight on (Step 2.5 → 3 → 4 → 5) — **no second gate**.
```
Replace `:89-90`:
```
**`continue` always means: run the remainder (Step 2.5 → 3 → 4 → 5) without further stops** — subject only
to Step 2.5's real-questions rule and the `changed`-path switch-back stop above.
```
with:
```
**`continue` always means: on a `GO` verdict, run the remainder (Step 2.5 → 3 → 4 → 5) without further
stops** — subject only to Step 2.5's real-questions rule and the `changed`-path switch-back stop above.
The verdict is read on every path (`continue`, `changed`, a pasted audit); a `NO-GO` is never run past.
```

### E5 — DEV-05 (Step 3 half) + DEV-15 box
Insert after `:106` `hot. If a test fails, find root cause before fixing.`:
```

**Run the ① reds FIRST and paste the actual RED output — before the first edit.** Then read WHICH LINE
RAISED: a red that dies in setup (a fixture that throws, a missing conftest env var, a bad import) looks
identical to one that fails its assertion, and only the second is a real red. A setup death is a fixture
defect — fix it, re-run, see the red on its assertion, and only then drive it green
(`tests-must-gate-for-real` Rule 1; memory `red-test-can-die-before-its-assertion`).
```
Insert after `:115` `never delete-to-force-green.`:
```

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
```

### E6 — DEV-09 · new Step 3.5
Insert before `## Step 4 — Automate (expand coverage)`:
```
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

```

### E7 — DEV-03 + DEV-17 · mutation doctrine replaces the single RELOCATE sentence
Replace `:124-127`:
```
**Structural reds are wiring proofs, never behavior proofs.** If ① left structural-only guard/wiring reds
(source-contains asserts), behavioral coverage is **owed here**, not optional — and you prove it non-vacuous
by **RELOCATING** the guard, never by deleting it, with a **positive control** on every scenario. Full
contract → `tests-must-gate-for-real` Rule 4.
```
with:
```
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
```
Leave `:108` and `:130` (Rule 4 = certification) as they are — those citations are correct.

### E8 — DEV-02 · Step 4.5 items 3–4 go through the receipt writer
Replace `:137-147` (from `3. **ONE full-suite run per touched stack** — backend:` through `inherits your green; miss → it pays for the full suite again.`) with:
````
3. **ONE full-suite run per touched stack — THROUGH THE RECEIPT WRITER, stamp-first.** The first full
   run of the landing code goes through `gate_receipt.py`; ⛔ do **not** run the runner bare "to check"
   and then again through the writer — one suite paid for twice, and only the second run is evidence.
   ```bash
   python3 .agents/scripts/gate_receipt.py run --story <id> --gate suite --cwd <worktree> \
          -- <the canonical runner>     # EVERY flag precedes `--`; after it is the command verbatim
   ```
   backend: `backend/.venv` pytest with the project's canonical runner flags (the runner AIDEV-NOTE in
   `backend/requirements.txt` is the ONE source of truth); frontend: vitest. E2E tier touched → the
   **FULL-TREE** emulator run; `-k`/single-file emulator runs are debug-only and **never citable**. The
   receipt lands in `_bmad-output/gates/<story>/suite.json` with the true exit code, totals parsed from
   the tool's own summary line, the SHA, and whether the tree was DIRTY — commit it with the story.
   **A red receipt is the mechanism working**: fix, re-commit, re-stamp; only the LAST receipt is the
   certification. Stamp on a clean tree (item 2 first) — a receipt over uncommitted code records `DIRTY`
   and inherits as invalid, correctly. Still **paste the actual output** — the receipt is additional
   evidence, never a substitute for reading the run.
4. **Emit the certification handoff — DERIVED from the receipt, never typed** —
   `_bmad-output/test-artifacts/certification-<story>.json`, one `stacks` entry per stack you ran:
   `{"story","sha","utc","stacks":{"<stack>":{"cmd","passed","skipped","failed","seconds"}}}`, every
   number copied from the receipt's totals and `sha` (③ reads this file AND `gate_receipt.py list
   --story <id>`; a pair that disagrees is a finding). Paste the output + `git rev-parse HEAD` into the
   walkthrough. **INVARIANT: the totals MUST come from a run at exactly that SHA.** Any code or test
   change after it voids the pair (repeat from 2); artifact/doc-only changes are exempt. ③ compares this
   `sha` to the HEAD under review — match → it inherits your green; miss → it pays for the full suite again.
````
Verify before landing: `gate_receipt.py run --story` exists (`:358`, `--task` alias) and the receipt path it writes on a story lane.

### E9 — DEV-01 · command half + rule half
`cicd-dev-story-tests.md` replace `:136` `` 2. **Commit** (explicit paths, never `git add -A`) — the SHA has to exist before a run can name it. `` with:
```
2. **Commit** (explicit paths, never `git add -A`) — the SHA has to exist before a run can name it.
   ⛔ **Backticks in `-m "…"` EXECUTE.** A message quoting a shell command runs it. Use `git commit -F
   <file>` whenever the message contains a backtick.
```
and replace `:185` `` **Git:** commit freely inside the story worktree (explicit paths, never `git add -A`); do NOT land it on `` with `` **Git:** commit freely inside the story worktree (explicit paths, never `git add -A`; `-F <file>` when the message holds a backtick); do NOT land it on ``.

`.agents/rules/git-policy.md` insert after the "Safe-commit mechanics" bullet ending `` key** (`SCC-11 fix(sync): …`). The `commit-msg` hook rejects a subject without one. ``:
```
- ⛔ **Backticks in `-m "…"` EXECUTE.** The shell expands `` `…` `` inside double quotes before git ever
  sees the message, so a subject that quotes a command name runs it. Use `git commit -F <file>` (or a
  single-quoted `-m`) whenever the message contains a backtick. Recorded house incident —
  `_artifacts/_memory/commit-message-backticks-execute.md`.
```

### E9b — QD-C1 rule residue · `git-policy.md:30-32`
Replace `` `chore/<JIRA-KEY>-<slug>` branch off `main`, merged back to `main` in the same session with `` / `` Daniel's per-action sign-off. The gate is per-repo: `` with `` `chore/<JIRA-KEY>-<slug>` branch off `origin/main`, in its own worktree, closed out through its door — `/smh-close-task-merge-tree` (a pull request the operator merges) or, when the diff reaches a deployable path, `/cicd-push-e2e`; invoking the door IS the sign-off (see the write gate below). The gate is per-repo: ``. The same file's `:36-40` and `:70` already say this; `:30-32` is the last copy of the pre-SCC-211 law.

### E10 — DEV-05 Evidence half
Replace `:163` `` **`## Evidence`** (the ONE AC→evidence matrix + the **actual pasted** certification totals + SHA) `` with `` **`## Evidence`** (the ONE AC→evidence matrix — each AC row carries its ① RED output (the line that raised) then the GREEN output, or `characterization` where a check was born green — + the **actual pasted** certification totals + SHA) ``.

SOP: ② gains two real STOPs (NO-GO, eject) — the SOP's ② paragraph gets one sentence; `[sop-ok]` would be a misstatement.

---

## 2 · `cicd-merge-epic-workingtrees.md` (14 live) + 3 fences into `smh-merge-multiple-workingtrees.md`

Backlog edits WRONG at HEAD: MERGE-03's preflight call omits `--expect-key` (required since SCC-210; argparse exits 2) and `--fetch` is now default; its "exit 2 = BLOCKED" read blocks every healthy lane (the `landed` row is `err` for any lane not yet an ancestor of the epic — carry the solo door's "ONE exit-2 row is EXPECTED" reading, `cicd-close-story-merge-tree.md:100-110`); "missing verdict → proceeds" cannot survive a script that errors on it (`closeout_preflight.py:324`). MERGE-08 points at `/cicd-update-sprint-memory` Step 4.5 — SCC-210 deleted it; the Jira half is `/cicd-close-story-merge-tree` Step 4a/b/c, using `jira_feed.py finish --landing-ref origin/epic/…` (SCC-242), not raw `acli … transition`. MERGE-06 names `/cicd-close-workingtree` (dead → `/cicd-prune-worktree`, pinned by CS-13 D1) and compares against a local `epic/*` ref the shared checkout never holds.

### E0 — rules block (MERGE-01, MERGE-08)
After `:13` `>   place where a single \`git add -A\` sweeps another lane's in-flight work into your commit.` extend the git-policy bullet and add two:
```
>   §"Pin the merge TARGET, not just the source" — `-C` on every call, assert before you merge: with N
>   trees open, a bare `git` after a `cd` runs in whichever checkout the shell reset to (see Step 4).
> - `.agents/rules/worktree-per-story.md` §"`cwd` is not intent" — every repo, branch and tree below is
>   pinned from command output, never from where you stand
> - `.agents/rules/jira.md` — the Dev Record contract and `jira_feed.py finish` (ticket moves are the agent's)
```
(`worktree-per-story` already exists at `:9` — merge the §-pointer into that bullet rather than duplicating.)

### E1 — MERGE-15 · commits-ahead column
Replace `:43` `2. Map each lane → story id → board row + story frontmatter status → review verdict: the` with:
```
2. Map each lane → story id → **commits ahead** (`git -C <project> rev-list --count
   origin/epic/<JIRA-KEY>-<slug>..claude/<JIRA-KEY>-<slug>` — from output, never memory) → board row +
   story frontmatter status → review verdict: the
```
Append after `:47` `…it may already name the set and the order.`:
```
   **⚠ "Ready" does not mean committed.** A lane reported finished can have **zero commits**, its work
   sitting uncommitted in a tree. `rev-list --count … == 0` with a dirty tree means the lane has not
   been built yet in any sense git can see — it needs commit, artifacts and `/cicd-code-review` before
   it is in the set at all. That is not the "trailing artifacts" case Step 2 commits for you.
```

### E2 — MERGE-03 + MERGE-09 · Step 2 becomes the mechanical preflight
Replace `:53-60` (`## Step 2 — Check each tree: pre-flight per lane` through `  WAIVED / missing verdict → proceeds (CONCERNS recorded on its board line).`) with:
````
## Step 2 — Check each tree: pre-flight per lane (mechanical, AUTOMATIC — the same script the solo door runs)
Inside each worktree, `TREE` pinned from Step 1's `git worktree list` output:
- `git -C "$TREE" status` clean — uncommitted work gets committed HERE first (explicit paths; this command
  never commits one lane's files from another lane's tree). A lane at **0 commits ahead** (Step 1's
  column) is the exception: it was never built — send it back, do not commit it into the set.
- **Run the preflight, every target pinned:**

  ```bash
  python3 .agents/scripts/closeout_preflight.py --story <id> --project <PROJECT> \
         --expect-key <JIRA-KEY> --branch claude/<JIRA-KEY>-<slug> --worktree "$TREE"
  ```

  `--expect-key` is required — the resolved branch must carry the key you named, because with N
  trees open `cwd` is not intent — and `--branch`/`--worktree` are not optional here either.
  **Check the target line it echoes against the lane you meant BEFORE reading its verdict**; a
  mismatch is a STOP, not a lane to skip. **Exit 2 = BLOCKED — that lane leaves the landing order.
  Exit 1 = warnings: read them, they do not block.**
  ⛔ **ONE exit-2 row is EXPECTED at this step and is NOT a block: `landed`.** It asks whether the
  lane is already an ancestor of the epic branch, and it is not — Step 4 is what lands it. If the
  ONLY error is `landed` naming the branch you pinned, the lane proceeds. `landed` naming a
  **different** branch is the wrong-lane case; an `intent`, `sync`, `worktrees`, `artifacts`,
  `status` or `gates` error blocks.
- **Close-out eligibility, per the close-out contract:** story at `ready-for-dev`/`in-progress`/
  `review` advances; `done` lanes are prune-only. Verdict **FAIL** (objectively red) → that lane is
  BLOCKED: report it, keep it out of the landing order, close out the rest. PASS / CONCERNS /
  WAIVED → proceeds (CONCERNS recorded on its board line). **No `Verdict:` line → BLOCKED** — the
  preflight's `artifacts` row says so (the only exemption is its own pre-2026-08-02 standalone-file
  fallback); name `/cicd-code-review` as what produces it.

<!-- twin-law: merge-empty-set-stop -->
⛔ **An empty eligible set is a STOP with a named reason, never a pass.** "All lanes landed" after
zero merges is the gate that cannot fail.
<!-- /twin-law -->
Print zero lanes landed and why per lane; Steps 3–7 do not run and the set is never reported closed.
````
⛔ FENCE `merge-empty-set-stop` — smh `:113-114` carries the two sentences verbatim; wrap them there.

### E3 — MERGE-02 + MERGE-07 + MERGE-05 + MERGE-16 + MERGE-14(undercount) · ONE Step 3 table
Replace `:62-77` (`## Step 3 — The overlap map (BEFORE any merge)` through `dependencies don't dictate.`) with:
````
## Step 3 — The overlap map (BEFORE any merge)
Pairwise across the set (`git -C <project> diff --name-only <A>...<B>` per pair, plus each lane vs
`origin/epic/<JIRA-KEY>-<slug>` — the epic's own branch), classify every file touched by ≥2 lanes.
**Seven classes, and only the board one is mechanical:**

| Class | Looks like | Resolution law |
|---|---|---|
| **code overlap** | two lanes edit one function / module | Read both hunks; same-function edits get an owner + resolution decided NOW, not mid-conflict. Dependency edges (one lane creates a module/predicate a sibling imports) dictate order: **creator lands before importer**; an operator ruling on the board outranks any guess. |
| **board file** | `sprint-status.yaml` · `active-context.md` · the sprint map · `_bmad-output/history/CHANGELOG.md` | Collide by construction. **Keep BOTH sides' facts, never pick a winner** — parallel lanes record different true things; picking a winner erases someone's work (the 2026-07-31 committed-conflict-marker incident on active-context.md is the standing example). |
| **test surface** | sibling red files · shared fixtures, `conftest`, registration files (the `registry.py` class) | Sibling red files are per-story and safe; shared fixtures entangle. Note which suites re-run after which landings; a sibling's **green-first tripwires must STAY green** through every landing. |
| **rewrite vs edit** | one lane rewrote a doc another lane edited a paragraph of | ⚠ **NOT mechanical, and git cannot tell you.** The paragraph the edit changed no longer exists, so *both* automatic resolutions are wrong. **Re-author** the edit into the new structure. |
| **modify / delete** | one lane deletes a file another lane edited | ⚠ **A decision, not a strategy.** Ordering does not rescue it — both orders end with the file deleted. Rule which side wins, and **prove the surviving content exists at its destination BEFORE accepting the deletion** (`git show <branch>:<path>`, or the named replacement). |
| **gate or script** | `.githooks/` · `.github/workflows/` · hook config · the project's test-runner entry point · gate scripts · anything a gate imports | ORDER MATTERS. State which version must win BEFORE merging, and re-run the gate that file feeds after each landing that touches it. |
| **generated** | lockfiles, sync manifests, mirrors, tool-written INDEXes | Resolved by **REGENERATING**, never by hand-merge. |

**⚠ `git diff` cannot see untracked files, so this map UNDERCOUNTS.** Run `git -C "$TREE" status
--porcelain` per lane and fold anything untracked into the map **as if it were already committed**,
because at merge time it will be.

Output: one table — lane → commits ahead → order → overlaps (class) → owner/resolution → cross-repo
dependency. Fewest-overlaps-first where dependencies don't dictate — with two overrides that outrank
the count:

<!-- twin-law: merge-machinery-last -->
**⭐ A lane that changes commit or push machinery lands LAST.** Once it lands it changes the rules
for every merge after it — a pre-push approval hook landed mid-sequence turns the rest of the
session into a different procedure.
<!-- /twin-law -->
Here that is the **gate or script** class above (`.githooks/`, `.github/workflows/`, the runner
every 4.2 gate calls); the gate it feeds re-runs after it lands.

<!-- twin-law: merge-cross-repo-order -->
**Cross-repo dependencies are part of the order.** A lane whose deletion's destination is an
**unmerged branch in another repo** lands AFTER that branch merges there. Get this wrong and the
content exists on no merged branch in either repo, and nothing says so.
<!-- /twin-law -->
Name that other repo's branch and its merge state in the table row.

Dump the table, the order and every conflict decision to the set's artifact folder before Step 4 — a
landing runs long enough to be compacted.
````
⛔ FENCES `merge-machinery-last` (smh `:178-180`) and `merge-cross-repo-order` (smh `:182-184`) — verbatim there; wrap.

### E4 — MERGE-01 + MERGE-14 · Step 4 header and 4.1
Replace `:80` `For each eligible lane, in the Step 3 order:` with:
```
For each eligible lane, in the Step 3 order — `TREE=<that lane's worktree path>`, copied from Step 1's
`git worktree list` output, and **`git -C "$TREE"` on EVERY git call in this step; never a bare `git`
after a `cd`** (`git-policy.md` §"Pin the merge TARGET"). The cwd resets to the shared checkout between
tool calls, and that checkout stands on `main`: a bare merge here merges the epic branch into `main`,
and the bare push in 4.4 lands `main`'s tip on the shared epic branch every sibling then absorbs —
reporting success both times. That is the 2026-08-11 shape that put a merge commit on a sibling's
branch, and the output is indistinguishable from a correct one.
```
Replace `:81-84` (`1. **Merge the epic branch into the lane, in the lane:**` through `   anything.`) with:
```
1. **Merge the epic branch into the lane, in the lane:** `git -C "$TREE" merge origin/epic/<JIRA-KEY>-<slug> --no-edit`
   — it now carries every previously-landed sibling, so each merge is the rolling reconcile. Resolve
   conflicts HERE using the Step 3 table. **A conflict in a file the Step 3 map did not classify is a
   finding, not a judgement call: STOP, re-derive the map for the remaining lanes (the untracked
   fold-in is the usual cause), and only then continue.** ⛔ Never check the epic branch out in the
   shared checkout to resolve anything.
```

### E5 — MERGE-04 + MERGE-12 · 4.2 tail
Insert after `:101` `   go green is skipped per Step 2 and the set continues.`:
````
   **Run every gate BARE and read its exit code** — piping to `tail`/`head` returns the *pipe's*
   status, so a red suite reads as green.
   An **artifacts-only** absorb at 4.1 keeps the lane's `Verdict:` valid. A code, script **or doc**
   change during the absorb — only `_artifacts/` is exempt; a `docs/` commit invalidates (SCC-154) —
   **VOIDS it**, and this gate is the re-measurement: it was measured against an epic branch that no
   longer exists. **Append the re-measurement to the walkthrough; never edit the old verdict away** —
   a pre-absorb `FAIL` left standing is the most useful line in the record. The shape:

   ```markdown
   ## Post-absorb re-measurement (<date>, landing set <story ids in order>)

   **Verdict: <PASS|CONCERNS> @ <post-absorb sha>** — re-measured after absorbing
   `origin/epic/<JIRA-KEY>-<slug>` at <sha> (<what landed there>). The pre-absorb `Verdict: … @ <sha>`
   above is **left standing on purpose**.

   <Artifacts-only absorb? say so and stop here. Otherwise one bullet per conflicted file naming the
   resolution and WHY.>

       <the canonical runner, scoped>   -> <files>, N/N cases, exit 0
   ```
   4.3's flip and 4.5's Dev Record read **this** verdict.
````

### E6 — MERGE-08 (half 1) · check-actions before the 4.3 commit, `-C` on the commit
Replace `:109-110` (`` `## Your Actions` records what lands. Commit — EXPLICIT PATHS ONLY, `git diff --cached --stat` `` / `   shows only this story's files.`) with:
```
   `## Your Actions` records what lands — and passes
   `python3 .agents/scripts/jira_feed.py check-actions --walkthrough <this lane's walkthrough>`
   **now, before the commit**: 4.5's `finish` refuses (exit 2) on the same rows, and after 4.4 the
   only fix is a commit on a branch that has already landed. Commit with `git -C "$TREE" add <paths>`
   and `git -C "$TREE" commit -F <msg-file>` — EXPLICIT PATHS ONLY, `git -C "$TREE" diff --cached --stat`
   shows only this story's files.
```

### E7 — MERGE-01 (assert + push) + MERGE-08 (half 2) · 4.4 and new 4.5
Replace `:111-113` (`4. **Land:**` through `   it is the rollback point until Step 6 deletes it.`) with:
````
4. **Land — assert the tree, then push, then prove the remote moved:**

   ```bash
   test "$(git -C "$TREE" rev-parse --abbrev-ref HEAD)" = "claude/<JIRA-KEY>-<slug>" || { echo 'WRONG TREE — STOP'; exit 1; }
   git -C "$TREE" push origin HEAD:epic/<JIRA-KEY>-<slug>
   git -C "$TREE" log --oneline -1 origin/epic/<JIRA-KEY>-<slug>     # must be THIS lane's merge sha
   ```

   Rejected (remote moved again) → re-merge, re-gate, re-land — never force. ⛔ Do NOT push the
   `claude/*` branch itself; it is the rollback point until Step 6 deletes it. ⛔ A push that did not
   return 0 means 4.5 does not run — the ticket never moves ahead of the landing.
5. **Dev Record, then the ticket — per lane, at ITS landing, never batched** (the order the solo
   door's Step 4 runs: a ticket reading `Done` over a stopped landing is a lie on the board; a
   landing whose record lags is one command from correct). Read `jira_key:` from the story frontmatter:

   ```bash
   python3 .agents/scripts/jira_feed.py devrecord --key <KEY> --story <id> --project <PROJECT> \
          --outcome "review -> done, landed on epic/<JIRA-KEY>-<slug> @ <sha>" \
          --decision "<…>" --pitfall "<…>" --followon "<…>" \
          --evidence "<4.2 totals @ post-absorb sha>" --closing --apply      # updates in place — never --append-new
   python3 .agents/scripts/jira_feed.py finish --key <KEY> --apply \
          --walkthrough "<this lane's walkthrough>" --landing-ref "origin/epic/<JIRA-KEY>-<slug>" --status Done
   python3 .agents/scripts/jira_feed.py check --key <KEY> --story <id>          # scoped: this lane filed one
   python3 .agents/scripts/jira_feed.py check --key <KEY> --project <PROJECT>   # unscoped: the only run that sees a FORKED record (SCC-174)
   ```

   ⛔ **`--landing-ref` is not optional on a story lane.** `finish` defaults to `origin/main`, where no
   story is an ancestor until the epic ships, so a bare `finish` HOLDS a finished story forever
   (SCC-242). **`finish` writes the `Done`, and per lane it may refuse to:** exit `0` closed · `3`
   **HELD** (open `- [ ]` rows under `## Your Actions`, posted to the ticket with the `user-tasks`
   label) · `2` the walkthrough is wrong, nothing written — fix it · `4` transport, retry. **A held
   lane does not stop the run** — its code is on the epic; carry it into the Step 7 report as
   *landed, ticket awaiting the operator* and go on to the next lane. ⛔ Never fall back to a bare
   `acli … transition --status "Done"` on a held lane. One Dev Record per ticket; a story with no
   `jira_key` skips this item and says so in the report — never invent a key.
````
Flags verified at HEAD: `devrecord --story --key --project --outcome --decision --pitfall --followon --evidence --closing --apply`; `finish --key --walkthrough --status --landing-ref --apply`; `check --key --story --project`; `check-actions --walkthrough`.

### E8 — MERGE-11 + MERGE-12 · Step 5.1 tail
Insert after `:122` `   re-run to green.`:
```
   Run it **BARE** — never through `tail`/`head`; the pipe's exit code is what you would read. Then
   the arithmetic: **the case totals must be additive — `<epic branch before the set> + <each lane's
   4.2 delta> = <combined>`** — or name which lane displaced which and why that was correct. It is the
   cheapest real check in the step: non-additive totals mean one lane's tests displaced another's at a
   4.1 resolution, and the merge ate coverage no review would ever see.
```

### E9 — MERGE-06 · verify before the report
Replace `:142-143` (`## Done — the one-shot report` / `` Per story: landed SHA range · verdict · `→ done` flip · pruned ✓. Set-level: overlaps resolved ``) with:
````
## Step 7 — Verify, THEN report (never report an unverified success)
Every ✓ below comes from a command you ran HERE, not from intent. `<project>` is the project's shared
checkout; it holds no local `epic/*` branch by contract, so compare against the REMOTE ref:

```bash
git -C <project> fetch origin
git -C <project> log --oneline -1 origin/epic/<JIRA-KEY>-<slug>          # the LAST lane's merge sha, by name
git -C <project> merge-base --is-ancestor <each landed lane's tip> origin/epic/<JIRA-KEY>-<slug> && echo landed
git -C <project> status --short                                          # empty — nothing rode into the shared checkout
git -C <project> worktree list                                           # only expected trees; a HUSK here blocks the next `worktree add`
git -C <project> branch -a --list 'claude/*'                             # only deliberately-retained lanes (`claude/incident-*` excluded)
```

Per story: landed SHA range · pre- and post-absorb verdict · `→ done` flip · Jira: Dev Record filed,
`<KEY> → Done` or *HELD — <rows>* · pruned ✓. Set-level: overlaps resolved
````
Keep the `/cicd-prune-worktree` literal at `:137` (CS-13 D1 pins it).

smh side: wrap `:113-114`, `:178-180`, `:182-184` with the three fence ids (6 marker lines, no wording change). `test_twin_parity.py` `FENCED_TODAY` += both filenames. Size: 11,350 B → ~18 KB → the Antigravity mirror flips to a thin launcher on sync (designed).

---

## 3 · `cicd-quick-dev.md` (8 live) + 1 fence into `smh-quick-dev.md`

Backlog WRONG at HEAD: QD-C1/QD-C14 — SCC-205 wrote "there is none" for the project-repo chore door; SCC-211 (`73c6f9c`) then created both doors (`git-policy.md:70`, `ship_preflight.py` light gate for a deployable chore diff; `/smh-close-task-merge-tree Projects/<name>` for a non-deployable one, `task_preflight.py` LANE LOCAL). QD-C14's story half must name `/cicd-close-story-merge-tree` (SCC-210), not the save. QD-C4's header slot is now `:221-227` and the probe must precede Step 3. QD-C12's rider is already folded at `:248-249`.

Pins to preserve: `test_declared_change_set.py:218` `RE-ARMS the plan-first gate`; `:219` `no Declared Change Set — plan-exempt lane`; `:217` asserts the literal `## Declared Change Set` is ABSENT from this file; `test_review_engine.py:85` QUICK_CMD caller.

### Edit 1 — QD-C9 + QD-C7 + QD-C11 + QD-C8 (+ QD-C2 mechanics) · Step 0.5 opening
Replace `:44-50` (`## Step 0.5 — Worktree (before the first edit)` through `through the normal close-out.`); keep `:52-57` (trim its last sentence "Link the gitignored assets…", now covered) and `:59-63`:
````
## Step 0.5 — Key, worktree, branch, ticket (before the first edit)

**Pin the ticket key you are working, before any tool has answered anything.** Every branch and
every commit must carry the repo's key (`.agents/jira.conf`), or the armed `commit-msg` hook
refuses the commit. Story lane: the story's `jira_key:` frontmatter. Ad-hoc lane: the ticket you
were handed — read its `ACCEPTANCE` block, it is Step 1's first AC source there:

```bash
EXPECTED_KEY="AVCH-00"     # the ticket you MEAN
acli jira workitem view "$EXPECTED_KEY"
```

No ticket at all → **STOP and ask.** Never invent a key; a keyless branch cannot be committed,
closed, or found again.

Per `worktree-per-story`: reuse an existing `claude/<JIRA-KEY>-<slug>` tree for this fix, else
open one. The base is a **remote-tracking ref after a fetch, never a bare local `main` or epic
ref** — a local ref is a cache a sibling lane has already moved past:

```bash
git -C "$PROJECT_ROOT" worktree list                      # reuse this fix's tree if it exists
git -C "$PROJECT_ROOT" fetch origin                       # ⛔ the base is origin/…, never a bare local ref
# story lane — off the story's EPIC branch:
git -C "$PROJECT_ROOT" worktree add .claude/worktrees/<slug> -b claude/<KEY>-<slug> origin/epic/<KEY>-<epic-slug>
# ad-hoc lane — no epic applies (a truly ad-hoc fix outside any sprint): git-policy.md's chore lane, off main:
git -C "$PROJECT_ROOT" worktree add .claude/worktrees/<slug> -b chore/<KEY>-<slug> origin/main
git -C "<the new tree>" branch --unset-upstream           # an origin/… start-point sets upstream to the BASE branch
python3 .agents/scripts/link-worktree-assets.py .claude/worktrees/<slug>   # PC: `python`
BRANCH=$(git -C "<the new tree>" rev-parse --abbrev-ref HEAD)
echo "Lane: $BRANCH"
```

Echo the case and the branch **from `rev-parse`, never from memory.** Every path and command from
here binds to that tree. Quick fixes are NOT exempt — this is what keeps them tangle-free,
rollbackable, and landable through a door.

`link-worktree-assets.py` links `node_modules`, `auth_keys/`, `.venv`, `.env` — at the repo root
and one level down (`backend/.env`, `frontend/node_modules`) — into the tree. Without them
pytest, uvicorn, `next dev` and the emulators fail on cwd-relative lookups, and Step 3 reports an
environmental red as a real one. A linked `.env` is **shared state**: re-run with `--copy-env` if
this lane will change it. ⛔ `--unlink` runs BEFORE any `git worktree remove` — a recursive delete
through a junction eats the shared targets (`/cicd-prune-worktree` Step 3 does this).

**Move the ticket to `In Progress` — now, at the tree, not at the merge (SCC-113):**

```bash
python3 .agents/scripts/jira_feed.py start --key <KEY> --apply    # PC: `python`
```

Idempotent, so a re-run or a resumed lane is a no-op. **Read its exit code — four outcomes:**

| Exit | Means | What you do |
|---|---|---|
| `0` | moved, or already `In Progress` | carry on |
| `3` | **left alone** — the ticket is `Blocking` / `In Review` / `Deferred` | **stop and ask.** You are opening a lane on a ticket that is waiting on something; say which and confirm that is intended |
| `2` | **the board refused it** — a `Done` key (so the key is wrong), or a move that did not land | **stop.** Never work a closed ticket's key; mint one at the `jira.md` §Who-mints-tickets seam |
| `4` | **the board was unreachable** — transport, not a verdict | **carry on and retry later.** ⛔ Do *not* mint a ticket: nothing here says your key is wrong. Sandboxed shells cannot reach the credential store (`jira.md` top), and the operator commits from planes |

> **The `post-commit` hook does this too, and that is deliberate, not redundant.** The hook fires on
> the first commit of any `chore/ · claude/ · epic/` branch, so work started without this command
> still shows on the board. This call moves it *earlier* — at the tree, before the first commit —
> and visibly. Neither layer is load-bearing alone: `core.hooksPath` is per-machine, so on a fresh
> clone the hook is silently OFF until it is set, and this line is what still works.

**⭐ Read the sibling lanes now, not at merge time.** Several lanes run at once and their
uncommitted work is invisible to `grep`:

```bash
git -C "$PROJECT_ROOT" worktree list
git -C <each-other-tree> diff --name-only <that lane's base>...HEAD   # origin/epic/<…> for a story tree, origin/main for a chore tree
git -C <each-other-tree> status --short
```

Any file in both their set and your intended set is a **landing-order dependency**. Say which lane
should land first and what happens to your work if it does not. Carry it into the walkthrough's
`## Evidence`.
````
Then `:232-234` ("The key is already in hand: …") → "pinned at Step 0.5 as `EXPECTED_KEY`".
Verified: `jira_feed.py start` returns exactly 0/2/3/4; `link-worktree-assets.py` takes `worktree`, `--repo`, `--unlink`, `--copy-env`; `jira.md` anchor `## Who mints tickets — two wired seams` exists.

### Edit 2 — QD-C4 · new Step 0.7 + header line
Insert AFTER Step 0.5's section ends (immediately before `## Step 1`), so the file reads 0 → 0.5 → 0.7 → 1:
````
## Step 0.7 — Probe the review runtime, and record it (SCC-177)

Ask this runtime whether it can fan out to subagents — do not answer from what usually happens,
because a headless pipeline or a platform with no subagent tool makes the answer `inline`, and
both are invisible until a lens fails to launch three steps later. The answer goes into the
walkthrough header Step 4 writes, on its own line, above everything else, and into the engine's
`review_runtime` input in Step 3:

<!-- twin-law: review-runtime-probe -->
⛔ **The probe is a **capability**, never a **policy** (SCC-203).** *Does a subagent tool exist in
this runtime?* is the whole question; *am I permitted to use it?* is a different one, and answering
it here is how a session directive — *"do not spawn subagents unless the user asks"* — got read as
*"this runtime is inline"*, ran an entire review inside the builder's own context, and had the flow
record it as legitimate. ⭐ **Subagents are the DEFAULT, and invoking a review IS that request** —
you never stop to ask for them, and never quietly downgrade to `inline` to avoid asking. Only a
runtime with no subagent tool at all is `inline`.

```
review-runtime: fan-out
```
<!-- /twin-law -->

⛔ **Step 0.7, not Step 4 — the probe must precede the review it describes.** Recorded afterwards it is
read off the roster that already exists, which makes the check circular: the header can only ever
agree with the states it was derived from. Recorded here it is an independent claim, and
`walkthrough_roster.py` blocks the close-out when the roster disagrees with it (`inline` + a lens
reporting `ok` is the contradiction it catches).
````
Then `:221` walkthrough spec: prepend `` `review-runtime:` (the header from Step 0.7, one line) → `` before `` `## Task Checklist` ``; `:161` "Try one throwaway subagent" → "the Step 0.7 answer".
⛔ FENCE `review-runtime-probe` — smh-quick-dev `:74-84` (the ⛔ paragraph + the ```review-runtime: fan-out``` block): wrap in place, no wording change. `FENCED_TODAY` += both filenames.

### Edit 3 — QD-C10 · backtick hazard
After `:115-117`'s `refuses it.` append: `⛔ **Backticks in `-m "…"` EXECUTE.** A message quoting a shell command runs it. Use `git commit -F <file>` whenever the message contains a backtick.`

### Edit 4 — QD-C1 (door row) + QD-C14 (Done) · the door that exists since SCC-211
Replace the table row `| chore lane in a **project repo** | ⚠ **there is none — state that and hand back** |` plus `:75-80` (`⚠ **The gap, recorded rather than filled:**` through `ticket.`) with:
```
| chore lane in a **project repo**, diff reaches a deployable path (`backend/ frontend/ firebase/ functions/ mobile/ .github/`) | `/cicd-push-e2e` — `ship_preflight.py` admits the `chore/*` under the **light gate** (SCC-211); nothing deployable → it refuses and names the PR door |
| chore lane in a **project repo**, nothing deployable in the diff | `/smh-close-task-merge-tree Projects/<name>` — the PR door, with the project named in `$ARGUMENTS` (its Step 0 takes a `Projects/` path; the subject stays `PROJECT_ROOT`, never the lobby). `task_preflight.py` derives `LANE: LOCAL` and it opens the PR and STOPS (`git-policy.md` § The write gate, `main` row) |

⚠ **Which door is derived from the diff, not chosen:** both doors read the same `PRODUCT_DIRS` and
refuse each other's lane. Project repos publish no `main-write-gate`, so the PR merge there is the
operator's click with no server-side gate — still the operator's, still never yours.
```
Rewrite `:69-73` ("Naming that door in a routing table … is an invitation to bind the lobby") to: the smh door is named here ONLY with `Projects/<name>` as its argument; bare invocation binds the lobby, which target resolution forbids.
Replace `:265-267` (Done) with:
```
Stop here. Never land on the epic branch, never touch `main`, never transition the ticket. Display
the spec path, the walkthrough link, the key changes, the review-gate output, and the branch + its
push state. Then invite the operator to review and invoke the door Step 0.5's table names for this
lane — `/cicd-close-story-merge-tree` on the story lane; `/cicd-push-e2e` or
`/smh-close-task-merge-tree Projects/<name>` on the ad-hoc lane, by what the diff touched. Invoking
it IS the sign-off.
```

### Edit 5 — QD-C12 durable half · `task.yaml` on the ad-hoc lane (ADOPTED)
The non-deployable door is `/smh-close-task-merge-tree`, which reads `task.yaml` and from which `devrecord --story` defaults (`jira_feed.py:2869-2870`). Add the smh `:447-453` manifest block to Step 0.5's ad-hoc path with `primary_repo: Projects/<name>`, `close_command: smh-close-task-merge-tree`; rewrite `:255-258` ("no `cicd-*` command writes a `task.yaml` at all … Recorded, not fixed here") — it becomes false.

---

## 4 · `cicd-create-epic-sprint.md` (6 live, file unchanged since the sweep)

Backlog WRONG at HEAD: PAIR-06's wholesale move breaks the mint — `jira_feed.py outline --epic N` dies without the `## Epic N` heading in `epics.md` (`:318-325`), which the moved step writes; resolution: dedupe + mint bare in Step 1a (requirements source as description), cut keyed in 1b, write `epics.md` in Step 2, backfill the outline with `acli jira workitem edit --key … --yes --description-file` (the `jira_feed.py:843-844` pattern) before the Step 2 commit. The test-design path at `:103` (`test-design/…`) is wrong — the epic-level output is `_bmad-output/test-artifacts/test-design-epic-<N>.md` (`workflow.yaml:56`, six real AGY files). `:26` "epic + story files" — no story files are written (`bmad-create-epics-and-stories` writes only `epics.md`). PAIR-02's source moved to `smh-plan-task.md:234-236`. PAIR-01(b): after the reorder it is Step 3 the operator's word opens.

### Edit A — PAIR-01(a) · rules-in-force block
Replace `:6-8` (`# /cicd-create-epic-sprint — Epic Kickoff: Stories + Sprint + Risk-Score (Phase A)` + blank + `Thin orchestrator — calls three existing BMAD/TEA skills back-to-back so a batch of requirements arrives as`) with the H1, then:
```
> **Rules in force for this command:**
> - `.agents/rules/000-PLAN-FIRST-GATE.md` — `epics.md` and `sprint-status.yaml` are project files
>   (§ What Counts as a Project File). The Step 2 checkpoint is this command's gate: it opens on the
>   operator's word alone, and a correction restarts the wait (§ What is NOT Approval)
> - `.agents/rules/artifacts-always-first.md` § Hard Stops — no project file is edited for a
>   commit-producing lane before its lane is open; that is why the branch is cut in Step 1, before
>   the epic is written
> - `.agents/rules/git-policy.md` — the epic branch is cut from `origin/main` at kickoff; explicit
>   paths only, never `git add -A`; `git status --short` empty + `0 0` before the work is called
>   finished
> - `.agents/rules/worktree-per-story.md` § "cwd is not intent" — every git call below is bound
>   with `-C "$PROJECT_ROOT"`, and the branch is echoed from command output, never from belief
> - `.agents/rules/jira.md` — the acli reference: the Epic is created bare, with an outline (SCC-49),
>   and its key is read from output, never invented
> - `.agents/rules/work-consolidation.md` rule 1 — look for a home before you mint: the Epic dedupe
>   search in Step 1 and the one-line "what I looked at" sentence
> - `.agents/rules/smh-target-resolution.md` §STD + §BIND — Step 0 binds `PROJECT_ROOT`
```
then the original `Thin orchestrator …` line.

### Edit B — PAIR-02/05/06/07/08 · ONE replace of `:23-103`
From `## Step 1 — Create the epic and its stories` through `   (`_bmad-output/test-artifacts/test-design/…`) and reflect the P-level onto each story.` inclusive, replace with:
````
## Step 1 — Key the epic and cut its branch (BEFORE any project file is written)
<!-- JIRA-HOOK: epic/story tickets mint here when the branch is cut (epic + stories → Jira, ids recorded on the sprint board). Separate story; not built yet. -->
Per `git-policy.md`, every epic integrates on its own short-lived branch; per
`artifacts-always-first.md` § Hard Stops, no project file is edited for a commit-producing lane before
its lane is open. So the branch comes FIRST, and **every artifact from here on — `epics.md`, the board,
the test design — is authored on that branch, inside `$PROJECT_ROOT`.**

**1a. The key — look before you mint.** `<JIRA-KEY>` is the EPIC's Jira ticket (one of the repo's keys
in `.agents/jira.conf` — the armed commit-msg hook rejects the wrong project's key). A re-run (this
command has two human stops, so a stall and restart is the normal case) or a backfilled board already
has the row, and a second Epic for the same BMAD epic is two rows, one of which nothing will ever move
again. `jira_feed.py mint` does this search for stories; the Epic mint has no script, so the look is
written here (`work-consolidation.md` rule 1):

```bash
acli jira workitem search --jql "project = <PROJ> AND type = Epic AND statusCategory != Done" \
     --fields key,summary --limit 50
```

**Say in ONE line what you looked at and why no open Epic covers this one** — or which key does, in
which case reuse it and skip the mint. That sentence is the whole enforcement mechanism. If no ticket
exists, **mint it now** (operator ruling 2026-08-07 — the human is already in the room at kickoff, no
separate ask), bare (no `--assignee`), carrying the requirements source as its description:

```bash
acli jira workitem create --project <PROJ> --type Epic --summary "Epic <N> — <title>" \
     --description "Epic <N> — <title>. Source: <requirements path from \$ARGUMENTS>. Outline follows at Step 2."
```

Read the key from the create output — **never invent a key, never cut the branch unkeyed.** The full
outline is backfilled in Step 2, once `epics.md` carries the Epic (SCC-49 — a summary-only ticket is a
title, not a ticket; it is complete by the end of Step 2, never left that way). Story tickets are NOT
minted here: ① `/cicd-write-story-tests` mints each story's ticket at pickup (its Step 1.6, through
`jira_feed.py mint`), so the board fills as work actually starts. Full acli reference: `.agents/rules/jira.md`.

**1b. The branch.** Cut it from up-to-date `origin/main` and push it so it lives on origin. Every call
is bound to the repo Step 0 resolved — a bare `git checkout -b` acts on whatever tree the shell is
standing in, which is the lobby checkout (`worktree-per-story.md` § "cwd is not intent"):

```bash
git -C "$PROJECT_ROOT" fetch origin
git -C "$PROJECT_ROOT" checkout -b epic/<JIRA-KEY>-<slug> origin/main   # re-run and origin/epic/<JIRA-KEY>-<slug> exists? `checkout epic/<JIRA-KEY>-<slug>` instead — never a second cut
git -C "$PROJECT_ROOT" push -u origin epic/<JIRA-KEY>-<slug>
BRANCH=$(git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD); echo "Epic branch: $BRANCH"
```

The echoed line must read `Epic branch: epic/<JIRA-KEY>-<slug>` — anything else → STOP. Story worktrees
(`/cicd-write-story-tests` ①) branch FROM this branch — it must exist, with the kickoff's output pushed
onto it, before the first one opens. The epic reaches `main` only via `/cicd-push-e2e`, which deletes
the branch after the merge.

## Step 2 — Create the epic and its stories — then STOP
Invoke the **`bmad-create-epics-and-stories`** skill for the requirements in `$ARGUMENTS` (a PRD, a
fix-list path, or a described scope — e.g. `_my_resources/open_tasks/fix_list_admin_sudoadmin.md`). It
writes the epic + its user stories with acceptance criteria into
`_bmad-output/planning-artifacts/epics.md` (stories live in that file; no per-story files are written
here — ① creates those). Confirm the new `## Epic <N>` section and its stories are in `epics.md` before
continuing. If the skill stops for input (missing requirements source, ambiguous scope), surface it and
STOP — never guess.

**FLOW CONTRACT (how this orchestration runs):** the nested BMAD skill
is a 4-step workflow whose step files each end in their own `[C]`-continue menu. Those menus exist for
STANDALONE greenfield use — do **NOT** surface them one-by-one during this orchestration; that turns one
kickoff into five stalls. When `$ARGUMENTS` names an already-approved requirements source (a signed-off
plan / fix-list), drive the skill's internal steps straight through (auto-continue its menus), appending per
the brownfield precedent (namespaced `E<N>-FR*` requirements; Epic 17/18 section format in `epics.md`).
This command has exactly **TWO human checkpoints**:
  1. ONE consolidated review after the epic is written — epic definition + full story list + AC digest
     in a single message — then **STOP and wait.** The operator's word opens Step 3; nothing else
     does. Per `000-PLAN-FIRST-GATE`, these are **not** approval: "ok" · "looks good" · "continue" ·
     clicking an option you wrote · being told to do the work · answering your clarifying question ·
     the operator **correcting** the epic + story set (a correction narrows it — edit `epics.md`,
     re-present the set, and stop again). Do not write the board on any of them;
  2. the Step 4 per-story risk-scoring (the designed hard stop).
A nested skill stopping on a REAL gap (missing source, contradictory scope) still surfaces + STOPs — this
contract removes ceremony, never judgment.

**On the operator's word — backfill the outline, then commit and push** (explicit paths, the Jira key
leads the subject, `-F` never `-m` — backticks in `-m "…"` EXECUTE):

```bash
python3 .agents/scripts/jira_feed.py outline --epic <N> --project <PROJECT> --out epic-outline.txt   # PC: `python`
acli jira workitem edit --key <JIRA-KEY> --yes --description-file epic-outline.txt
rm epic-outline.txt
printf '%s\n' "<JIRA-KEY> docs(epic): Epic <N> — <title>: epic + stories" > epic-commit-msg.txt
git -C "$PROJECT_ROOT" add _bmad-output/planning-artifacts/epics.md
git -C "$PROJECT_ROOT" diff --cached --stat                       # ONLY epics.md; anything else → unstage it
git -C "$PROJECT_ROOT" commit -F epic-commit-msg.txt
git -C "$PROJECT_ROOT" push origin HEAD:epic/<JIRA-KEY>-<slug>
```

`outline --epic` renders the goal and the story list straight out of `epics.md` — nothing invented.
⛔ Never `git add -A` / `.` / `-u` — the shared checkout may carry the operator's own uncommitted work.

## Step 3 — Generate the sprint board — then commit and push it
Land the new epic + story keys in `_bmad-output/implementation-artifacts/sprint-status.yaml` as **`backlog`**
— NOT `ready-for-dev` (the board's state machine: a story flips to `ready-for-dev` only when
`/cicd-write-story-tests` ① creates its story file). Follow house style: the epic's
comment block (STATUS · Source · order/deps), one commented line per story key (P-levels appended after
Step 4), `epic-<N>-retrospective: optional`, and a dated entry PREPENDED to the `# last_updated:` journal
line. For a single-epic append, edit the YAML directly per house style — invoking the full
`bmad-sprint-planning` skill is only warranted when regenerating the whole board. Confirm the keys appear,
then:

```bash
printf '%s\n' "<JIRA-KEY> chore(board): Epic <N> rows on sprint-status.yaml (backlog)" > epic-commit-msg.txt
git -C "$PROJECT_ROOT" add _bmad-output/implementation-artifacts/sprint-status.yaml
git -C "$PROJECT_ROOT" diff --cached --stat                       # ONLY the board
git -C "$PROJECT_ROOT" commit -F epic-commit-msg.txt
git -C "$PROJECT_ROOT" push origin HEAD:epic/<JIRA-KEY>-<slug>
```

## Step 4 — Risk-score the backlog (test levels) — INTERACTIVE HARD STOP
This is the final step and a **hard stop** — you WORK WITH Daniel to label every story, one at a time.

1. Invoke the **`bmad-testarch-test-design`** skill to risk-analyze the epic's stories (Risk = Probability ×
   Impact, per the TEA Test Priorities Matrix).
2. Assume the **Test Architect (Murat)** persona and walk Daniel through the P-level decision **ONE STORY AT
   A TIME**. For EACH story present:
   - **Your recommended P-level** (P0 / P1 / P2 / P3) — your opinion, stated first.
   - **Why** — the Probability × Impact reasoning in a line or two (what breaks, and how much it hurts).
   - **What it is** — one line of plain-language context on the feature/decision being scored.
   - **Levels it earns** — P0 = Unit+Integration+E2E+Manual (100%) · P1 = Unit+Integration+E2E (80%) ·
     P2 = Integration+Manual (50%) · P3 = Manual/skip (20%).
3. Give Daniel a way to **confirm or override each label individually** (the tap-to-answer question UI; the
   recommended P-level is the default first choice). ONE tap-screen carrying every story as its OWN question
   (recommendation + why + levels on each) satisfies "one at a time" — each story gets an individual
   decision (Epic 17/19 precedent: "interactive chips"). What is forbidden is deciding on the human's
   behalf: never record a P-level that wasn't explicitly confirmed. **STOP and wait** for the decisions.
   This is the hard stop.
4. Record the confirmed P-levels + test-level allocation into the test-design artifact
   (`_bmad-output/test-artifacts/test-design-epic-<N>.md` — the skill's epic-level output) and reflect
   the P-level onto each story in `epics.md` and onto its board line. Then commit and push all three:

   ```bash
   printf '%s\n' "<JIRA-KEY> docs(tea): Epic <N> risk-scored - P-levels on test design, epics and board" > epic-commit-msg.txt
   git -C "$PROJECT_ROOT" add _bmad-output/test-artifacts/test-design-epic-<N>.md \
                             _bmad-output/planning-artifacts/epics.md \
                             _bmad-output/implementation-artifacts/sprint-status.yaml
   git -C "$PROJECT_ROOT" diff --cached --stat                    # ONLY those three
   git -C "$PROJECT_ROOT" commit -F epic-commit-msg.txt
   git -C "$PROJECT_ROOT" push origin HEAD:epic/<JIRA-KEY>-<slug>
   rm epic-commit-msg.txt
   ```
````
⚠ Step 4 items 1–3 are the existing text carried verbatim — re-diff against HEAD at build time so the operator-facing wording (the Murat persona, the tap-screen ruling) is not altered by the move.

### Edit C — PAIR-05 close · the finished check in Done
After `:109` `Leave it there — **do NOT start writing tests or code** (that's `/cicd-write-story-tests`).` add:
````

Before the report, prove the kickoff is on origin (`git-policy.md` — `0 0` + clean, or the work is not
finished; an unverified "pushed" is how this hides):

```bash
git -C "$PROJECT_ROOT" status --short                                              # must be empty
git -C "$PROJECT_ROOT" rev-list --left-right --count epic/<JIRA-KEY>-<slug>...origin/epic/<JIRA-KEY>-<slug>   # must be "0 0"
```

State both results in the report, with `Epic branch: <from rev-parse>` and the commit range landed.
````
Report line `:106-107`: add `the epic branch + commit range pushed,` after `the epic id + title,`.

---

## 5 · `cicd-clean-code-audit.md` (5 live) + `memory-sweep` fence into `smh-clean-code-audit.md`

Backlog WRONG at HEAD: QD-C1/QD-C2 "append at :87 / extend :135" would DUPLICATE what Part E already added (`:130-134`, `:161-163`) — the defect now is PLACEMENT: the two scan rows sit in Step 2B, which `:122-124` skips on embedded runs. QD-C1 cites §3 — at HEAD the gate-cannot-fail rule is §5, run-bare §6. QD-C3's `PROJECT_ROOT/` prefix is redundant under `:40` and breaks fence identity.

### E1 — QD-C5 (HIGH) · unstaged edits join the set
Replace `:58-59`:
```
git diff --name-only "${BASE}...HEAD"           # story branch vs the branch it forked from
git diff --name-only --cached                   # plus staged, if mid-work
```
with:
```
git diff --name-only "${BASE}...HEAD"           # story branch vs the branch it forked from
git diff --name-only                            # plus uncommitted - saved edits nobody staged yet
git diff --name-only --cached                   # plus staged, if mid-work
```

### E2 — QD-C4b · §BIND STOP clause
Replace `:40` `` Every bare path and every command below resolves **under `PROJECT_ROOT`**. `` with:
```
Every bare path and every command below resolves **under `PROJECT_ROOT`** (per
`.agents/rules/smh-target-resolution.md` §STD + §BIND); a needed path missing under `PROJECT_ROOT` →
STOP, never fall back to the lobby.
```
(matches `cicd-code-review.md:37-38` verbatim). Do not touch the header row at `:10`.

### E3 — QD-C3 · never-sweep-memory guard · ⛔ FENCE `memory-sweep`
Insert between `:64` `` prevent (`tests-must-gate-for-real` §2). `` and `:66` `---`, and REPLACE smh `:74-76` with the identical bytes:
```
<!-- twin-law: memory-sweep -->
⛔ **Never sweep another session's memory into this diff** (`artifacts-always-first` §"The memory
store"). Dirty files under `_artifacts/_memory/` belong to whatever wrote them — the store is shared
and two-tier since SCC-73, the lobby's index plus each project's own, so a sibling lane's uncommitted
entry shows up in a `git status` here. Report them as present and out of scope; they are parked or
left, never committed under this lane's key.
<!-- /twin-law -->
```
Add the pointer row to both rules-in-force blocks: `> - `.agents/rules/artifacts-always-first.md` §"The memory store" — never sweep another session's memory into this diff`. ⚠ `test_twin_parity.py` E1 is pinned on `disposition`, so a second law in this pair is safe — run the file bare afterwards to confirm.

### E4 — QD-C1 + QD-C2 · MOVE the two scan rows from Step 2B into Step 1's always-run list
Cut `:130-134` (`- **Does it run on both machines?** …` through `this one is not a judgment call.`), paste after `:108` `- commented-out code`; change `:103` `**Also scan the changed lines for the §2 banned patterns that linters miss:**` → `**Also scan the changed lines for what no linter catches:**`; extend the both-machines bullet's first clause to `A hardcoded absolute or `C:/…` path where `Path(__file__).parent` belongs, a `;` path separator, …`. Wording `a new gate that cannot fail` and `both machines` preserved (`assert-scc205.sh` greps them).

Size: 11,397 B → ~12,050 B → Antigravity mirror flips to a launcher on sync (designed).

---

## 6 · `cicd-code-review.md` (7 live) + `smh-code-review.md` (DEFERRED_WORK row + `rederive-record` fence)

Backlog WRONG at HEAD: QD-C2's premise inverted — since SCC-210/242 the STORY door runs `check-actions` (`cicd-close-story-merge-tree.md:150`) and `finish --landing-ref` (`:295`), so the refusal claim is TRUE; only "nothing BEFORE the door checks it" remains → fold into QD-C1. QD-C1's "delete the ledger-row sentence" drops a true fact (`MERGE_DOORS` includes the story door; `finish` judges door-named rows by ancestry) → replace, don't delete; its example `/cicd-update-sprint-memory` is the save, not the door. QD-C3's `$WORKTREE`/`$EPIC` are bound LATER at HEAD (`:79`, `:86`) → the bindings move up. QD-C5: the guard list is now inline `(a)/(b)` prose at `:321-330` → lands as `(c)`. QD-C4's "in three lines" does not match `walkthrough_roster.py` E7, which counts list rows under a HEADING matching `0.7|re-deriv` → the port must mandate the sub-heading. QD-C6: `HEAD_SHA` is read from `$PROJECT_ROOT` at `:44` — worse than the backlog said.

Fence state: `review-level`, `declared-drift`, `roster`, `record-lines` identical both sides (the `FENCED_TODAY` comment lists three — stale by `record-lines`; fix the comment). Heading trap: do NOT put "target"/"project" in the new Step 0.6 heading (`Step 0\b` matches `Step 0.6` in the `smh-target-resolution` row).

### E1 — QD-C3 + QD-C7 · new Step 0.6
Insert between `:60` `…Echo the story's ①②③ step-state before Step 1.` and `:62` `## Step 0.7 — ⭐ Re-derive the blast radius against the **current epic branch** (MANDATORY)`:
````
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

Echo the file count. **An empty set is a STOP, not a pass** — Step 3.5 restates it at the gate, but
by then the engine, the acceptance audit and the whole test gate have already run on nothing.

⛔ **`git -C ""` does NOT error** — git documents it as "leave the current working directory
unchanged" — so an unassigned `$WORKTREE` silently measures whatever tree the shell is standing in:
the shared checkout Step 0.5 just told you is empty or stale, and the redirects in Step 0.7 still
create their two `/tmp` files, so the overlap reads clean (`preflight-resolves-repo-from-cwd`).
⛔ The ref is `origin/$EPIC`, never the trunk (SCC-165 — Step 0.7 says why).

Dirty files under `_artifacts/_memory/` are **named separately and left alone** — another session's
memory store is never swept, deleted, or committed under this story (`artifacts-always-first`
§ "The memory store": the project store is git-tracked, so it materialises in every story worktree).
````
Companion: replace `:79` (`EPIC=<epic/JIRA-KEY-slug> …`) and `:80-86` (`# ⛔ BIND THE TREE …` through `WORKTREE=<…>`) with one line `# $WORKTREE and $EPIC — bound in Step 0.6 from command output; reuse them, never re-derive from cwd`. Keep `:78` and `:359-360`.

### E2 — QD-C6 · DIFF row + ⚠ note
Replace `:178` with `` | `DIFF` | the `origin/$EPIC...HEAD` diff from Step 0.6, **re-taken in that worktree after Step 0.7 absorbed `origin/$EPIC`** — committed work only | ``. In `:179` `` taken **now** — `` → `` taken **now, after Step 0.7's absorb** — ``. After `:185` (the `review_runtime` row) insert:
```
⚠ **Step 0 read `HEAD_SHA` from `PROJECT_ROOT` — the shared checkout — and before Step 0.7 absorbed
`origin/$EPIC`.** Re-read both it and the diff here, in `$WORKTREE`, or the engine reviews a tree that
no longer exists and your verdict cites a commit that is no longer the tip — the exact invariant Step
0.7 opens by stating.
```

### E3 — QD-C5 · the cannot-fail guard as (c)
`:321-322` `**Two guards (per` → `**Three guards (per`; append after `:330` `…do not grandfather it, FAIL and fix/delete it.`:
`(c) **A check that cannot fail is a finding.** If the diff adds a gate, a guard or a CI step, prove it **rejects** the case it must reject *and* **allows** the case it must allow — `tests-must-gate-for-real` § Mutation Testing (INVERT the decision). One half is not a gate.`
No "run gates bare" line (cicd routes gates through `gate_receipt.py`, shell=False).

### E4 — QD-C4 · two Step 4 bullets · ⛔ FENCE `rederive-record`
Fix the stray comma at `:444` (`…whatever the prose says,` → `.`), insert after it `- the acceptance matrix from Step 1.5 — every acceptance item → its proving assertion;` and after `:445` (the `### Clean-Code Gate` bullet):
```
<!-- twin-law: rederive-record -->
- **Step 0.7's re-derivation**, under its own `### Step 0.7 — re-derivation` sub-heading as three
  numbered lines — what the landing ref moved under this diff, the true overlap + `merge-tree` result,
  and any sibling-lane landing-order dependency. "Nothing moved" is a reportable result; silence is
  not — `walkthrough_roster.py --gate` counts list rows under a heading matching `0.7`/`re-deriv`
  (E7) and refuses fewer than three.
<!-- /twin-law -->
```
smh `:440-442` (`- **Step 0.7's re-derivation**, in three lines — what `main` moved …`) → replace with the identical fenced block ("the landing ref" keeps both sides byte-identical). The `FENCED_TODAY` comment for this pair gains `rederive-record`.

### E5 — QD-C1 (+ QD-C2 folded) · ceremony paragraph `:468-474`
Replace the seven lines from `⛔ **And NEVER the ceremony's own steps** (SCC-193). "Click Merge on the PR", "then re-invoke` through `this branch's PR`, which SCC-175 checks against ancestry rather than against its tick.` with:
```
  ⛔ **And NEVER the ceremony's own steps** (SCC-193). "Land the branch on the epic", "then
  re-invoke `/cicd-close-story-merge-tree <story>`", "run the preflight" — the operator's
  **decision to proceed** is the sign-off (the word `approved`, or invoking the door —
  `/cicd-close-story-merge-tree`, or `/cicd-merge-epic-workingtrees` for a set), and from that
  word on every step is the ceremony's and the agent runs it. On this lane the door enforces it
  twice: its Step 2 runs `jira_feed.py check-actions` before the close-out commit, and its Step 4b
  runs `jira_feed.py finish --landing-ref "origin/$EPIC"` after the landing (SCC-210, SCC-242) —
  both **refuse** such a row. Nothing earlier does: neither this command nor
  `closeout_preflight.py` reads the rows, so a ceremony row you leave here is caught, but at the
  price of a branch already landed on the epic. The story door writes no PR ledger row; a row that
  names a door or opens with `the merge itself` is judged by `finish` against the ancestry of
  `origin/$EPIC`, never against its tick.
```
Evidence: `jira_feed.py:1725-1727` `MERGE_DOORS`, `MERGE_PHRASE`; `:1837 merge_row_state`; `:1817 resolve_landing_ref`.

### E6 — QD-C9 · `smh-code-review.md` DEFERRED_WORK row
After `:184` `` | `ARTIFACT_DIR` | `_artifacts/_main/<YYYY-MM-DD>_<slug>/` inside this tree | `` insert `` | `DEFERRED_WORK` | `_artifacts/_main/deferred-work.md` — the same file Step 1 names as the only legal sink for a `defer` | ``. (cicd already carries its row at `:183`.)

### E7 — DEV-04 sibling · `:133-134`
"the dev-side commands do not carry this header … (F24)" → "② (`/cicd-dev-story-tests` Step 0.8) records its own runtime; this step re-probes and overwrites the line when ③ runs in a different session".

---

## 7 · `cicd-self-audit.md` (1 live — QD-C2 sibling-lane binding)

Four of five are settled by the SCC-225 rewrite (tripwire list and Light/Full ladder deleted by an approved plan; STOP-on-no-plan exists at `:56-57`; constitution scan deleted on BOTH sides by name) — dismissed, not gaps.

Replace `:156-158`:
```
- **Sibling lanes:** fetch the base first (a stale remote ref inflates every sibling's apparent
  set), then `git worktree list` + per-tree `diff --name-only` — a file in both sets is a
  landing-order dependency: name the order and the cost of violating it.
```
with:
```
- **Sibling lanes** (`worktree-per-story` §"Am I alone in this repo?"): story lanes are `claude/*`
  worktrees off ONE epic branch, several at a time, and a sibling's uncommitted tree is invisible
  to grep from here. Bind every call — a bare `git` here reads the lobby, not the project:
  `env -u GITHUB_TOKEN git -C "$PROJECT_ROOT" fetch origin <epic-branch>` first (a stale remote
  ref inflates every sibling's apparent set), then `git -C "$PROJECT_ROOT" worktree list`, then
  per tree `git -C <tree> status --short` + `git -C <tree> diff --name-only
  origin/<epic-branch>...HEAD`. The ref is the story's EPIC branch (`epic/<KEY>-<slug>`), never
  `origin/main`. A file in both their set and this plan's declared set is a **landing-order
  dependency**: name which lane lands first and what happens to this work if it does not.
```
Port, not fence: the ref and the `$PROJECT_ROOT` binding are subject-forced (the parity test's own legitimate-divergence list).

---

## 8 · Test + SOP + sync edits

- `test_twin_parity.py` `FENCED_TODAY` += `"cicd-quick-dev.md", "smh-quick-dev.md"` (`# twin-law: review-runtime-probe`) and `"cicd-merge-epic-workingtrees.md", "smh-merge-multiple-workingtrees.md"` (`# twin-law: merge-*`); comment for the code-review pair gains `record-lines, rederive-record`; clean-code comment gains `memory-sweep`.
- `test_command_surfaces.py` `LOADERS` += `"cicd-dev-story-tests.md"`; its comment rewritten (the story lane now loads the rule).
- `docs/_scc_sops_prds/workflows_testing_SOP.md`: the ② paragraph gains the NO-GO/eject STOPs; the `test_twin_parity.py` row gains the fence count and the four fenced pairs; the kickoff paragraph notes the branch-first order + commits.
- `pwsh .agents/scripts/sync-agents.ps1` once at the end; `test_command_surfaces.py` bare.
- `_artifacts/_main/INDEX.md`: one row for this folder.
