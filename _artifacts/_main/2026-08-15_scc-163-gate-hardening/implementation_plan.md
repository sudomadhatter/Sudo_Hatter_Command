# SCC-163 — Gate hardening ×2: the ff blind spot in the merge-target backstop, and the unenforced `## Your Actions` rule

- **Ticket:** SCC-163 (Task) · **Lane:** `chore/SCC-163-gate-hardening` · **Base:** `main` @ `8ae2e25`
- **Tree:** `.claude/worktrees/SCC-163-gate-hardening`
- **Date:** 2026-08-15 · **LANE: LOCAL** — this repo has no deployable surface.
- **Lane class, mechanically:** `lane_qualify.py --paths <scope>` → `TASK` ("this changes the
  development system, so it takes the full lane"). Not the lightweight lane. Plan → audit → RED →
  review → close-out.

## ⭐ Operator rulings — 2026-08-15, verbatim

Both open decisions are now **settled**. Recorded here because §B.0.b is a gate-arming question, and
`blocking-gates-need-a-quoted-ruling` requires the operator's own words rather than a derived
corollary:

> **Q1 (B.0) — host `jira_feed.py`, ship WARN, `--strict-actions` built and disarmed?**
> **Operator:** *"1. yes"*
>
> **Q2 (A3) — widen the `:105` ref filter, or document the omission?**
> **Operator:** *"2. A3. no we dont need it."*

**What Q1 authorises, precisely:** the detector lands in `jira_feed.py`, wired into `finish`, and it
ships **WARN**. `--strict-actions` is **built and disarmed**. ⛔ This is *not* a ruling that the gate
ships armed — arming it is a separate act of law needing its own quoted words, exactly as the ticket
states.

**What Q2 settles:** the `:105` ref filter is **not widened**. The omission is documented in the file
with its reason, which is the branch A3 explicitly permits. The residual `epic:chore` / `epic:epic`
ff-gap is recorded in the code as deliberate, not left silent.

## Why one lane and not two subtasks

Operator ruling, verbatim, 2026-08-15: *"add it to the SCC-163 I want to keep as much on one ticket
as possible."* Part A and Part B share **no files**, so each proves independently and either can land
alone if the other stalls — but they land on one branch, under one key. Per `/smh-plan-task` Step 2,
*one lane is the normal answer for most Tasks*; nothing is minted on the board.

---

# PART A — the merge-target backstop is blind to `epic/*`

## A.0 The defect, re-derived from the code (not from the ticket)

`pre-push-merge-backstop.sh:176` enumerates the candidate foreign lanes:

```sh
for other in $(git for-each-ref --format='%(refname:short)' refs/heads/chore refs/heads/claude 2>/dev/null); do
```

`refs/heads/epic` is absent. So when a `chore/*` lane fast-forwards an epic branch into itself, the
epic's unlanded commits are contained in the pushed sha and **nothing enumerates the epic to notice**.
The commit-msg guard cannot help: a fast-forward writes no commit, which is the entire reason this
backstop exists (SCC-144).

**The judge table says this pairing is REFUSE.** `merge-target-guard.sh:204` — notation is
`target:source`:

```
chore:chore|chore:epic|chore:story) echo refuse ;;
```

So `chore ← epic` is already law. Part A makes the backstop enforce law the guard already states.

## A.1 ⛔ Why a blanket widening is wrong — the constraint that shapes the whole fix

A4 is the hard half. Reading the same table for every arm that involves an epic:

| pairing (`target:source`) | verdict | line | what it means for the containment loop |
|---|---|---|---|
| `chore:epic` | **refuse** | 204 | an epic inside a `chore/*` lane is foreign unlanded work → **must enumerate** |
| `story:epic` | allow | 205 | a story lane absorbing **its own epic** is the everyday move → **must not enumerate** |
| `incident:epic` | allow | 179 | *"absorbing main (or an epic) into it is the everyday mid-incident move"* → **must not enumerate** |
| `epic:main` / `epic:story` | allow | 201 | pushed ref is `epic/*` → never reaches the loop (filter at :105) |
| `main:epic` | allow | 199 | pushed ref is `main` → never reaches the loop (filter at :105) |

Adding `refs/heads/epic` to the loop unconditionally would false-red **every story lane that has
absorbed its epic**, and every incident lane that absorbed one — the exact regression class this file
has already paid for twice (SCC-154's ordered `case` arm, SCC-159's incident widening, both recorded
in its header). So:

> **The fix is one ordered `case` arm on the lane class, mirroring the `BASES` switch directly above
> it: enumerate `refs/heads/epic` for `chore/*` only.**

`claude/incident-*` must be excluded **explicitly and above** `claude/*`, for the third time in this
file, because `case` is first-match and the story glob swallows incident names.

## A.2 The `:105` ref-filter decision (A3) — RECOMMENDATION: document, do not widen

Line 105 restricts which *pushed* refs are judged at all:

```sh
refs/heads/chore/*|refs/heads/claude/*) ;;
*) continue ;;
```

A pushed `epic/*` is therefore never judged, which leaves `epic:chore` and `epic:epic` (both **refuse**
at :202) escaping by fast-forward. That is a real residual gap. I recommend **documenting it in the
file rather than widening**, for three reasons:

1. **It is not what was reproduced.** The ticket's reproduction is `chore ← epic`. Widening adds a
   second new behaviour with its own regression surface on the same commit.
2. **Widening cannot reuse the same enumeration.** For a pushed `epic/*`, `refs/heads/claude` must be
   *excluded* (`epic:story` is allow, and stories landing on the epic is what an epic **is**) —
   so it needs its own third enumeration set and its own four green cases.
3. **`/cicd-push-e2e` pushes epic branches on the shipping path.** This file's own header rules that
   *a false red costs more than a miss*.

A3 authorises exactly this: *"either widened or documented, in the file, as a deliberate omission with
the reason."*

> ⭐ **RULED, 2026-08-15 — operator: *"2. A3. no we dont need it."*** The filter is **not widened**.
> Step A-4 documents the omission in the file, naming `epic:chore` / `epic:epic` and why the
> enumeration cannot be shared. The residual gap is recorded as deliberate, never silent.

## A.3 Steps, each naming the assertion that proves it

| # | Step | Assertion (`test_git_hooks.py`) |
|---|---|---|
| A-1 | **RED first.** Add the reproduction: scratch repo + bare remote, backstop ARMED, `chore/SCC-1-lane` ff-merges `epic/SCC-1-thing`, push. | new case **`EP1`**: push is **REFUSED** (non-zero) and stdout carries the standard `PUSH REFUSED — this lane is carrying another lane's unlanded work` banner. **Must fail before A-2 exists** — captured in the walkthrough. (**A1, A2**) |
| A-2 | Add the lane-class arm: `refs/heads/epic` enumerated for `chore/*` only; incident arm above `claude/*`. | `EP1` flips GREEN. (**A3**) |
| A-3 | **Green cases for the four ALLOW pairings.** | **`EP2`** story lane carrying its own epic → ALLOWED · **`EP3`** incident lane carrying an epic → ALLOWED · **`EP4`** pushed `epic/*` carrying a story → ALLOWED (proves the `:105` filter still declines) · **`EP5`** pushed `main` → ALLOWED. (**A4**) |
| A-4 | Document the `:105` omission in the file, naming `epic:chore` / `epic:epic` and why the enumeration cannot be shared. | **`EP6`**: the file contains the omission rationale — pinned to the **wiring** (the `case` arm's ref list), never to prose. See "How the guards are written" below. (**A3**) |
| A-5 | Update `docs/_scc_sops_prds/workflows_testing_SOP.md` — the backstop's refusal surface changes. | `sop_currency.py` exits 0 with **no `[sop-ok]`** in the message. |

## A.4 Mutation sweep — declared now, drawn FROM THE CODE (A5, the SCC-144 rule)

Written before the code exists, and drawn from the lines the fix will add, never from the cases:

| # | Mutant (revert / invert a line of the FIX) | Must kill |
|---|---|---|
| A-M1 | Delete `refs/heads/epic` from the `chore/*` enumeration | `EP1` |
| A-M2 | Move `refs/heads/epic` to the unconditional enumeration (blanket widening) | `EP2` **and** `EP3` |
| A-M3 | Move the `claude/incident-*)` arm **below** `claude/*)` | `EP3` |
| A-M4 | Widen the `:105` filter to accept `refs/heads/epic/*` without a matching enumeration set | `EP4` |

Zero survivors required.

---

# PART B — nothing mechanically enforces what may go in `## Your Actions`

## B.0 ⛔ THE OPEN DECISION — surfaced here, NOT assumed (the ticket's explicit instruction)

The ticket left two questions open and forbade assuming them. **Both are now ruled** — operator,
2026-08-15: *"1. yes"* to the recommendation below in full. The reasoning is kept because it is the
evidence the ruling was made on.

### B.0.a WHERE it runs — ⭐ RULED: `jira_feed.py`

`workflow_lint.py` is the wrong host, and this is measurable rather than a preference:

- **`--staged` is deliberately encoding-only.** Its own docstring (`workflow_lint.py:444`): *"A full
  lint here would make every commit slow and the hook would be disabled within a week."* Adding a
  walkthrough check there fights a documented design decision.
- **`--toolkit-only` deliberately excludes `_artifacts/`** (`workflow_lint.py:118` — *"`_artifacts/`
  (history…)"*), and every walkthrough lives there.
- **`jira_feed.py` already owns all three primitives.** `YOUR_ACTIONS` (:1241), `open_actions()`
  (:1306), and `_unfenced()` (:1271) — which **is** B4's helper (the ticket calls it
  `strip_fenced`; that is its name in `check_gate`, ported here as `_unfenced` under SCC-154/155).
  Reuse it; do not re-derive it.

**Design: one detector, one home.** `jira_feed.py` gains
`banned_action_rows(text) -> list[(row, reason)]`, wired into **`finish`** (where the damage happens),
plus a `check-actions --walkthrough <path>` subcommand as the manual/inspection entry point — the same
function exposed, which is also what makes the B.1 corpus run reproducible.

> ⚠️ **AUDIT FINDING B-F1 (major, applied).** The first draft of this section also wired the detector
> into `/smh-code-review` Step 5 at authoring time. **Cut.** It traces to **no acceptance item**
> (B1–B6 never ask for it), and it breaches **SCOPE B**, which names `jira_feed.py` *or*
> `workflow_lint.py` plus the test file — command bodies are not in it. It would also drag in a
> command-body edit → `/smh-sync-agents` → four platform caches → the `cicd-code-review` twin and its
> `-AP` twin. That is a second lane's worth of blast radius bought for a hypothetical. If the
> operator wants the authoring-time call site, it is a follow-on with its own key.

### B.0.b BLOCK or WARN — ⭐ RULED: ship **WARN**, arming flag built and disarmed

1. **The ticket says so.** *"The operator's ruling recorded above authorises the WORK and its
   placement on this ticket; it is NOT a ruling that the gate ships armed."* Per
   `blocking-gates-need-a-quoted-ruling`, arming needs its own quoted words.
2. **A block at `finish` fires AFTER the merge.** The work is already on `main`; blocking converts
   *"ticket held on Review Required"* into *"close-out errors with the work landed"* — strictly worse.
3. **The detector is a heuristic over English prose, and the corpus says so** (B.1 below): the
   ticket's phrase list read literally is **~50 % false-positive on real walkthroughs.**

So: `finish` prints a loud, distinct `⛔ BANNED ACTION ROW` block naming the row and the remedy, and
**still holds the ticket exactly as it does today** (behaviour unchanged, diagnosis added). A
`--strict-actions` flag makes it refuse; it **ships disarmed**, so arming later is a flag flip on one
invocation, not a code change and a release.

> ⚠ **Warn-only has a known failure mode in this system** — `vscode-hides-git-hook-output`: a
> warn-only hook looks like clean success. Mitigation is in the assertion, not the intention: **`B7`
> pins that the banner is printed on the real fixture**, so a silent warn is a red test.

## B.1 ⭐ The corpus, measured BEFORE the rule exists (B1) — and it changes the design

Ran `jira_feed.open_actions()` over every `.md` under `_artifacts/`: **101 walkthroughs carry a
`## Your Actions` section; 25 unchecked rows exist across them.** Then ran the ticket's B2 phrase list
literally (`mint|file|open…ticket|fold…into|rule on|rule the|decide whether|your call|board placement`):

**8 of 25 rows flagged. At most 4 are true positives.**

| Row (truncated) | Naive | Correct | Why |
|---|---|---|---|
| `**SOP-nag ticket (optional, your call…)**` | FLAG | **FLAG** | proposes a residue ticket — banned shape |
| `Decide whether finding 13 earns a ticket` | FLAG | **FLAG** | banned shape, by name |
| `**File the follow-on Task** from the review section's…` | FLAG | **FLAG** | banned shape, by name |
| `**Rule the landing order.** Recommended: SCC-126 lands first` | FLAG | **allow** | merge sequencing — a main-merge call |
| `**Decide whether the CONCERNS is worth clearing before the merge.**` | FLAG | **allow** | a pre-merge product decision |
| `**Rule on A1.** It is not delivered…` | FLAG | **allow** | acceptance dispute — the operator's own call |
| `**Rule on A2's missed target.** 68.57 s against ≤ 60 s` | FLAG | **allow** | acceptance dispute |
| `**Rule on A6's phrasing**` | FLAG | **allow** | acceptance dispute |

**Conclusion that shapes the code:** *"rule on" / "decide whether" / "your call" are not triggers on
their own.* B3 already demands the **VERB+OBJECT** pair for ticket keys; the corpus proves the same
requirement applies to the bare verbs. The detector fires only when a trigger verb is paired with a
**ticket-work object** — `ticket`, `<KEY>` in a create/place context, `Task` as a Jira type, `board
placement`, `fold … into <KEY>`, `mint`, `earns a ticket` — and never on a verb alone.

## B.2 Steps, each naming the assertion that proves it

Tests extend **`test_jira_feed.py`** — one red file per tier; extend, never fork.

| # | Step | Assertion |
|---|---|---|
| B-1 | **RED first, with the real fixture.** Vendor AVCH-58's pre-correction section into `.agents/scripts/tests/fixtures/` — it lives at `9674880d` in **AGY_AVIATIONCHAT**, a *different repo*, so a test cannot `git show` it. Captured verbatim, 3 rows. | **`B1`**: row 1 is flagged. Fails before B-2 exists. (**B1**) |
| B-2 | Implement `banned_action_rows()` — trigger verb **×** ticket-work object, over `_unfenced` lines. | `B1` GREEN. (**B2**) |
| B-3 | **The three named cases from B3.** | **`B2`** `"Merge AVCH-59 to main"` → **not** flagged · **`B3`** `"Move SCC-99 to Done"` → **not** flagged · **`B4`** `"Mint a ticket for the N deferred items"` → **flagged**. (**B3**) |
| B-4 | **The corpus is the regression suite.** Pin the 5 real allow-rows from B.1 as negative controls, and AVCH-58 rows 2–3 (status notes) with them. | **`B5`**: all 7 unflagged. (**B3, B5**) |
| B-5 | Fenced examples are not rows — reuse `_unfenced`. | **`B6`**: a `- [ ]` banned-shape row inside a ``` fence is **not** flagged. (**B4**) |
| B-6 | Say **in the code** that status-note rows are deliberately out of scope, naming AVCH-58 rows 2–3. | comment pinned beside the detector; `B5` is its live proof. (**B5**) |
| B-7 | Wire into `finish` (warn) + `check-actions` subcommand; `--strict-actions` built, disarmed. | **`B7`**: on the real fixture `finish` **prints the banner** and **still exits as it does today** · **`B8`**: `--strict-actions` refuses. (**B.0.b**) |
| B-8 | Update `docs/_scc_sops_prds/workflows_testing_SOP.md` **and** the `jira_feed.py` row in `.agents/scripts/INDEX.md:17`, which enumerates the subcommands (audit finding B-F2). | `sop_currency.py` exit 0, no `[sop-ok]`; `check_maps.py --depth3-only --strict` exit 0. |

## B.3 Mutation sweep — declared now, drawn FROM THE CODE (B6)

| # | Mutant | Must kill |
|---|---|---|
| B-M1 | Delete the `_unfenced` call (read raw lines) | `B6` |
| B-M2 | Invert the allow-list (treat merge/transition objects as banned) | `B2` **and** `B3` |
| B-M3 | Drop the object requirement — fire on the trigger verb alone | `B5` |
| B-M4 | Drop the verb requirement — fire on a bare ticket key | `B2` |

Zero survivors required.

---

## How the guards are written (both parts)

`prose-pinning-guards-are-vacuous` (SCC-125) and `comment-literals-invert-source-grep-tests`: **pin
the wiring, never the description**, and **the mutant must be shown to fail first**. Every assertion
above is behavioural — it drives the real script or the real function and reads its verdict. The one
structural check (`EP6`) pins the `case` arm's ref list, not the sentence explaining it.

## Non-goals — stated so they cannot be quietly absorbed

- **The two review-lens findings the ticket rules out are not chased**: the SQUASH_MSG false-red and
  `main ← story` by fast-forward. Both were re-tested against the live scripts and neither reproduces
  here; the latter is real in AGY and is **AVCH-59's** job.
- **Rows 2 and 3 of AVCH-58 are not detected** (B5) — real defects, not reliably machine-detectable.
- **No port to AGY on this lane.** AVCH-54 re-ports after this lands; porting first carries the escape
  into AGY byte-for-byte.

## Risks

| Risk | Mitigation |
|---|---|
| Part A false-reds a story lane absorbing its epic | `EP2`/`EP3` are green cases; A-M2 must kill them |
| Part B false-reds an honest walkthrough | measured at plan time (B.1); 7 real rows pinned as negative controls; ships **warn** |
| The two parts entangle at review | they share no files; each proves independently |

## The gate this lane must pass

`run_all.py` · `workflow_lint.py --toolkit-only` · `check_maps.py --depth3-only --strict` ·
`sop_currency.py` · `test_git_hooks.py` · `test_jira_feed.py` · the declared mutation sweeps.

---

## Self-Audit (2026-08-15)

**Mode:** PRE-WORK · **Right-size:** **FULL** — the plan touches a gate/hook
(`pre-push-merge-backstop.sh`), a script other scripts import (`jira_feed.py`), and their tests.
**Repo/branch, from command output:** `Repo: SCC-163-gate-hardening | Branch: chore/SCC-163-gate-hardening`.

| Phase | Walked — what was checked and cleared |
|---|---|
| **0** Scope + checkable list | Change set named (4 files + 2 doc/index surfaces). Acceptance list taken from the ticket's **ACCEPTANCE A/B** blocks (authority 1). Traceability run **both ways**: every A1–A5 and B1–B6 maps to a step; **one step traced to no acceptance item → cut (B-F1)**. Lane check: no deployable path (`backend/ frontend/ firebase/ functions/ mobile/ .github/`) — matches `lane_qualify` → `TASK`. |
| **1** Blast radius | `hooks_armed.py:102` maps `MERGE-TARGET-ENFORCE` → `merge-target-guard.sh`/`commit-msg`; Part A adds **no flag** → unaffected. `flight_recorder.py:69` imports only `_SCRAPE_HEADS, scrape_bucket` → unaffected. `task_preflight.py:922` is a **third reader** of `## Your Actions` (presence only, never row content) → no edit required. `.agents/scripts/INDEX.md:17` enumerates jira_feed's subcommands → **edit required (B-F2)**. **Sibling lanes: none** — `git worktree list` shows only `main` and this tree, so no landing-order dependency exists. |
| **2** Over-engineering (STRICT) | Tripwires walked. **"New script where an existing script grows a subcommand"** → satisfied: subcommand, not a new script. **"Generalizing for N when the work is N=1"** → **FIRED on the two-call-site design → CUT (B-F1)**. **"A gate that cannot fail"** → warn-only is a live risk, answered by pinning the banner in `B7` rather than by intent. No new command, no new rule file, no clone-and-tweak. |
| **3** Pre-mortem | **Other machine** — every command is `python3`/`sh`; tests inherit the harness's interpreter handling. **Fresh clone** — Part A ships no new arming marker; `MERGE-TARGET-ENFORCE` already exists, so nothing is silently OFF. **Fires on someone else's commit** — Part A reuses the existing banner, which already names the remedy. **Escape hatch** — `git push --no-verify`, already documented in the file header. **Empty input** — a walkthrough with zero banned rows yields an empty list and no banner; non-vacuous because `B1`/`B4` prove a positive fires. **Four platform caches** — not reached, once B-F1 is cut. **Rollback** — Part A is one `case` arm, Part B is warn-only; both revert cleanly, nothing irreversible. |

### Findings

| # | Where | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| **B-F1** | plan §B.0.a (as drafted) | **Major** | Wiring the detector into `/smh-code-review` Step 5 traces to no acceptance item and breaches SCOPE B; it pulls in a command-body edit, a four-platform sync, and two twins — scope creep discovered at review, not at plan. | **CUT — applied inline** in §B.0.a |
| **B-F2** | `.agents/scripts/INDEX.md:17` | Minor | The `jira_feed.py` row lists its subcommands; adding `check-actions` without updating it leaves the script index lying, and `check_maps --strict` is in the gate. | **Folded into step B-8** |
| **A-F1** | plan §A.2 | Info | The `:105` omission is a *recommendation*, not a settled call — A3 permits either. Left open deliberately and surfaced at the stop. | Operator's call |
| **A-F2** | `test_git_hooks.py`, `test_jira_feed.py` | Info | Part B changes `finish`'s stdout, which finish-adjacent fixtures (`_pf_fixtures.py:39`, `test_task_preflight.py:465`) sit near. | Baselines recorded: **129/129** and **197/197** — any drop is a regression, not a new normal |

### Four quick gates

- **Verification strategy present?** ✅ Every acceptance item names a case ID and the command that runs it; both mutation sweeps are declared **before** code exists, drawn from the fix's own lines (A5/B6, the SCC-144 rule).
- **Anything irreversible?** ✅ No. No delete, no rename, no history rewrite, no `main` merge on this lane. The one Jira transition already happened (`To Do Next → In Progress`).
- **Any step vague enough that the builder will guess?** One was — *"flag rows that ask the operator to rule on work"* — and §B.1 replaces it with a measured rule (verb **×** ticket-work object) plus 7 pinned negative controls drawn from the live corpus.
- **Convention fit?** ✅ Tests extend the existing red file per tier rather than forking; guards pin **wiring, not prose** (SCC-125); the incident arm keeps its load-bearing position above `claude/*`.

**Audit verdict: GO** — conditional on the two operator rulings below. The plan is safe to build once
B.0 is answered; nothing in Part A waits on anything.

## ⛔ STOP — the rulings are in; the plan approval is not

| Owed | State |
|---|---|
| **B.0 ruling** (host + arming) — the ticket forbade assuming it | ✅ **RULED** 2026-08-15 — *"1. yes"* |
| **A3** — widen `:105` or document the omission | ✅ **RULED** 2026-08-15 — *"2. A3. no we dont need it."* |
| **Approval of this plan** (`000-PLAN-FIRST-GATE`) | ⛔ **STILL OWED** |

⛔ **The rulings are not the approval.** `000-PLAN-FIRST-GATE` names *"answering your clarifying
question"* as one of the things that is **not** approval — alongside "ok", "looks good", "continue",
and being told to do the work. The operator answered two design questions; nothing has authorised the
build. That distinction is the whole gate: an agent that reads a settled design question as
permission is the failure mode the rule was written for.

**Nothing else blocks.** Both parts are fully specified, the audit is GO, the lane is pushed and
clean, and no sibling lane is live. On the word, the build order is: Part A (`EP1` RED → arm →
`EP2`–`EP6` → sweep), then Part B (`B1` RED on the vendored fixture → detector → `B2`–`B8` → sweep),
then the SOP and `scripts/INDEX.md` in the same commit as their surfaces.
