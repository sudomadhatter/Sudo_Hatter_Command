# SCC-73 Phase 1 — walkthrough

**Lane:** `chore/SCC-73-memory-relocation` · **Repo:** Sudo_Hatter_Command · **Base:** `ef0af3a`
**Close command:** `/smh-close-task-merge-tree`

## Task Checklist

- [x] **S0 — merged `main` down.** Lane was cut at `3536443`; SCC-82 landed mid-audit taking `main` to
      `ef0af3a` and touching three files in this change set or its gate set.
  - *finding:* the merge also moved the lint bar — `workflow_lint --toolkit-only` went from "0 errors,
    2 pre-existing warnings" to **0 errors, 0 warnings**. Acceptance tightened to match (R2).
- [x] **S1 — RED, assertion-shaped.** 8 failing / 2 passing against the real repo.
  - *finding:* the harness evaluates `check(name, ok)` eagerly, so a test calling a not-yet-written
    helper crashes instead of reporting. Wrote the RED as a probe against **existing** functions so
    every failure names what is absent rather than that something is unwired.
- [x] **S2 — GREEN, the fan-out.** `maintained_project_names()` / `project_stores()` / `pointer_problems()`
      / `backpointer_problems()` / `project_store_signals()`.
  - *finding (design-changing):* a project is a **separate repo with its own armed hook** — AGY's
    `jira.conf` is `JIRA_KEYS="AVCH"`, so an SCC-keyed commit there is rejected. A hard failure would
    red `run_all` in the lobby for a defect nobody in the lobby may repair. Split by **ownership**:
    hard-fail what this repo owns, `[SIGNAL]` what another repo owns.
  - *finding:* NEXgen has a store directory and **no index**. A naive fan-out calls `check_store()` on
    it, gets "unreadable by contract", and reds every unrelated lane. Absence is now a **named skip**.
- [x] **S4 — the Phase 2 note** in `audit_block()`, printed where the question is actually live.
- [x] **S6 — `AGENTS.md` §7** — the two-tier law, landed **before** S3 per audit finding F2.
  - *finding:* §7 makes the store read-only outside two sanctioned flows and a `chore/*` lane is
    neither, so S3 would have violated standing law. §7 now separates **content** (read-only) from
    **structure** (sanctioned when it is the declared subject of a ticket).
- [x] **S3 — the `## Project stores` pointer section** in the lobby index.
  - *finding:* `check_store()` resolves every markdown `.md` link by **basename** against the store, so
    linking a project's `MEMORY.md` reads as a dead link to a file that plainly exists. Backticked
    paths only. ⭐ The comment written to warn about this **tripped the check itself** — the comment is
    scanned too. Rewritten without the literal.
- [x] **S5 — the command surface.** Relocate disposition + cross-repo mechanics in `/smh-memory-audit`;
      Step 1.5 project-index read in `/cicd-boot-sprint-memory`; `commands/INDEX.md` row corrected.
  - *finding (F4):* that row still advertised the **20 KB** cap — stale since SCC-69 raised it to 25 KB
    — and listed 3 of 4 dispositions. The linter checks only that a command is *mentioned*, never that
    the prose is true, so it rotted invisibly. Same class of failure this ticket exists to fix.
- [x] **S7 — docs + indexes.** SOP (same commit, as the armed gate requires), `workspace-standard.md`
      PATH CONTRACT gained a per-project row, `_artifacts/_main/INDEX.md` gained its session row.
- [x] Doors regenerated via `sync-agents` (never hand-edited); `run_all` + lint green.
  - *finding:* the relocation section took the command past the generator's 11,500 B threshold, so
    Antigravity's door **changed kind** — verbatim mirror → launcher stub. Sanctioned, but reading
    that stub is what exposed the next one.
  - *finding:* a launcher carries the command's frontmatter `description:` verbatim, and it still
    advertised *"retire / merge / compress"* — **every** platform's menu entry claimed three
    dispositions for a command with four. The same rot fixed in `commands/INDEX.md` one commit
    earlier, sitting one field above it. Both descriptions corrected and re-synced.
- [x] **Review gate — a blocker found and killed before landing.** The adversarial layer proved this
      branch turned `run_all` RED on `main`: `audit_signals` read a module global, so a hermetic
      fixture inherited AGY's cross-repo defect. Green in a worktree, red on main — the exact failure
      the ownership split exists to prevent, reintroduced by the wiring. Reproduced, fixed with an
      explicit opt-in param, and pinned by a regression test asserted against the live repo.
  - *finding:* my "proved before landing" evidence had measured the wrong function. Retracted.
  - *finding:* three more soundness holes in checks that read as sound — the back-pointer token was
    also the project's own path, the "section" was the rest of the file, and name matching was raw
    containment. All three now have fixtures that must fire.

## Evidence

**A4 / A6 — the fan-out and the pins.** RED first, against the real repo:

```
== SCC-73 RED probe (pre-implementation) ==
    maintained projects on the tracked allowlist: ['AGY_AVIATIONCHAT', 'NEXgen-VR-Director']
[FAIL] A4 the gate fans out over maintained project stores: test_memory_store.py never reads the allowlist - only REAL_STORE (the lobby) is gated
[FAIL] A4 every project store with an index is actually checked today: UNGATED: AGY_AVIATIONCHAT (15 memories)
[FAIL] A4 a project with a store dir but NO index must be a named skip, not a failure: naive fan-out would RED: no MEMORY.md index in .../NEXgen-VR-Director/_a
[FAIL] A2 the lobby index carries a `## Project stores` section: no such heading in MEMORY.md
[FAIL] A2 the section names `AGY_AVIATIONCHAT`: not named anywhere in the index
[FAIL] A2 the section names `NEXgen-VR-Director`: not named anywhere in the index
[FAIL] A2 `AGY_AVIATIONCHAT`'s index carries the mirror back-pointer to the lobby store: project index never names the lobby store
[FAIL] A5 audit_block names SCC-73 Phase 2 as the remedy when the levers are spent: the block tells you to compact - which SCC-69 proved is exhausted
[PASS] A6 INDEX_CAP is unchanged at 25 KB: 25600
[PASS] A6 TRIGGER_PCT is unchanged at 0.90: 0.9
-- 8 failing --
exit=1
```

*(A6 passes green in the RED and is labelled honestly: it is a **characterization pin** guarding an
operator ruling against future drift, not a behavior this lane adds.)*

**GREEN — in the lane (`Projects/` is an empty stub here, which is the point):**

```
-- 34/34 passed --
[COVERAGE] project stores read this run: 0
[SKIP] project store not gated - AGY_AVIATIONCHAT: submodule not checked out - not gated here (git submodule update --init -- Projects/AGY_AVIATIONCHAT)
[SKIP] project store not gated - NEXgen-VR-Director: submodule not checked out - not gated here (git submodule update --init -- Projects/NEXgen-VR-Director)
LANE exit=0
```

**⚠ RETRACTED — the original "main-tree behavior, proved before landing" claim was false.** It probed
`project_stores` / `check_store` / `project_store_signals` directly and never ran `main()`. The suite
*was* red on `main` at that moment (see the Code Review section, finding 1): `audit_signals` reached
for a module-global `REPO_ROOT`, so a hermetic fixture inherited AGY's missing back-pointer. The probe
answered a real question and not the one the heading claimed. Corrected evidence, after the fix:

```
BLOCKER REGRESSION CHECK
  hermetic fixture, REPO_ROOT=main -> []          (was: AGY's back-pointer signal -> fixture FAILED)

MAIN-TREE HARD GATES (these can block)
  check_store(lobby)           -> CLEAN
  pointer_problems(post-merge) -> CLEAN

MAIN-TREE ADVISORY (loud, never blocking)
  [SIGNAL] `AGY_AVIATIONCHAT`'s MEMORY.md never names the lobby store (`Sudo_Hatter_Command/_artifacts/_memory/`)

  coverage: ['AGY_AVIATIONCHAT'] | skips: ['NEXgen-VR-Director: no memory store yet - nothing to gate']
```

**The gates, run bare (never piped — a pipe reports the pipe's exit code):**

```
run_all exit=0        -- 12/12 files passed
lint    exit=0        -- 0 error(s), 0 warning(s), 8 info
```

**Index size:** 20,390 B → **21,296 B** — **83.2 %** of the 25 KB cap; trigger at 90 % untouched. The
section costs **906 B** and is what makes it safe to remove far more than that in the first sweep.
*(Corrected: this first read "21,107 B / 82 % / ~700 B" — wrong in all three figures, in the one
document whose thesis is measurement discipline. Caught by the adversarial review, not by me.)*

## Code Review (2026-08-11)

```
Verdict: CONCERNS @ <FINAL-SHA>
```

Suite evidence measured on the same sha; every gate below was re-run after the last code change.

**Scope** — 17 files, `main...HEAD`, no uncommitted work but untracked `.opencode/node_modules`.
**Method** — Step 0.7 re-derivation vs current `main`; clean-room adversarial layer in a subagent with
no conversation context (hunted the diff before reading the plan); acceptance audit; command-centre
gate; `/smh-clean-code-audit`.

**Step 0.7 — re-derivation.** *(1)* Nothing this diff references moved: `BASE == main == ef0af3a`,
zero files landed since S0, so the pre-work trace still describes the live repo. *(2)* True overlap
**none**; `merge-tree` returns a clean tree, no conflicts. *(3)* Live siblings: `SCC-77` (`8e2ee83`)
and `SCC-83` (`ef0af3a`, still pre-work). **SCC-83 shares `workflows_testing_SOP.md`** — different
sections, so whoever lands second merges `main` down and re-runs the gate; its new prose-path gate
(A3b/A3c) already permits the project-relative path class this lane introduces, checked against their
plan rather than assumed.

### Findings

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| 1 | `test_memory_store.py` `audit_signals` | **HIGH** | **Blocker — this branch turned `run_all` RED on `main` the moment it landed.** `audit_signals` reached for the module-global `REPO_ROOT` and appended `project_store_signals` unconditionally, so the hermetic fixture *"a healthy store produces NO candidates"* inherited AGY's missing back-pointer. Green in a worktree (`Projects/` empty), red on main — blocking every unrelated lane over a defect this repo is forbidden to fix. Verbatim the failure the ownership-split comment claims to prevent, reintroduced by the wiring. | **applied** — `repo` is now an explicit opt-in param, `None` by default. **Reproduced before fixing and pinned by a regression test** asserting the fixture stays clean *against the live repo*. |
| 2 | `walkthrough.md` Evidence | **HIGH** | The block headed *"main-tree behavior, proved before landing"* probed `check_store`/`project_store_signals` directly and never ran `main()` — it answered a real question, not the one the heading claimed, while the suite was red. | **applied** — retracted in place, re-measured, corrected evidence pasted. |
| 3 | `test_memory_store.py` `backpointer_problems` | **HIGH** | Matched `"_artifacts/_memory"` — **also the project's own store path**. A project index saying only *"my memories live in `_artifacts/_memory/`"* passed a check meant to prove it points somewhere *else*. The fixture used that exact ambiguous literal as its "good" case, so it could never catch it. | **applied** — discriminating `LOBBY_BACKPOINTER` sentinel; the ambiguous case is now a pinned fixture that must FIRE. |
| 4 | `test_memory_store.py` `pointer_problems` | MED | `split(heading)[1]` is the rest of the file, not the section — ~99 % of a 21 KB index counted as "in" the section, so one future memory row naming a project path would have anaesthetized the only hard tier-two check permanently. | **applied** — `_section()` bounds at the next `## `; empty-section-rescued-by-later-rows is a pinned fixture. |
| 5 | `test_memory_store.py` `pointer_problems` | MED | Raw substring containment: a longer sibling (`NEXgen-VR-Director`) satisfies a shorter allowlisted name (`NEXgen`), so a genuinely missing signpost reads as present. Latent today, armed by the next name added. | **applied** — line-anchored word-boundary match; pinned by fixture. |
| 6 | `maintained_project_names` | MED | Missing allowlist → `[]` → **both tiers silently disarm**, with output visually identical to a healthy worktree run. | **applied** — `None` (loud) vs list; absent allowlist is now a named skip and a pointer-check failure. |
| 7 | `smh-memory-audit.md` Step 0 | MED | Step 0 still said *"there is one store"* and to stop — halting the agent before it reached the relocation flow the command now owns. | **applied** — Step 0 rewritten: binds the lobby, reads one store, may write to two. |
| 8 | `AGENTS.md` vs `workspace-standard.md` | MED | Law documents disagreed: *"both gated"* vs *"never blocking"*. | **applied** — AGENTS.md now states one blocks, one reports, and why. |
| 9 | `AGENTS.md` §7 | MED | The structural carve-out was **self-authorizing** — satisfied by writing the ticket title — and "structural" was undefined, in the one rule protecting memory from invisible edits. | **applied** — defined by enumeration (3 acts) and bound to explicit operator approval. |
| 10 | `maintained-projects.txt` header | LOW | Undocumented two-file coupling: adding a name reds `run_all` in every checkout unless the index is edited too. | **applied** — written into the header where you stand when adding a name. |
| 11 | `walkthrough.md` index figures | LOW | Claimed 21,107 B / 82 % / ~700 B; actual **21,296 B / 83.2 % / 906 B** — wrong in all three, in the document whose thesis is measurement. | **applied** — re-measured and corrected, with the error left visible. |
| 12 | `.agents/workflows/smh-memory-audit.md` | LOW | A platform door **changed kind** (verbatim mirror → launcher stub) when the command crossed the generator's 11,500 B threshold. Sanctioned mechanism, but the blast radius recorded only *"doors 8/8 present"* — present, yes; same kind, no. | **applied** — recorded here and in the checklist. This is also what exposed the stale-description defect. |
| 13 | `test_memory_store.py` (perf) | LOW | `project_stores()` re-reads every project store several times per run; O(stores × files) as the tier grows. | **deferred** — 1 store / 17 files today; revisit when a third project store gains content. |
| 14 | RED probe (scratchpad) | LOW | Two probe assertions were tautological (`False if gated else True`) or aimed at a function the design never calls, so the probe is not valid re-run evidence. | **dismissed as a gate, recorded as a lesson** — the permanent suite is the evidence; the probe was a one-shot absence demonstration and is not committed. |

**Layer health:** the adversarial layer ran (no retry needed) and produced findings 1–13; nothing was
skipped or degraded. Its two dropped findings — frontmatter-description drift and one duplicate — had
already been fixed at `bc1ddfd` before it reported.

### Gates

| Gate | Result |
|---|---|
| Enforcement suite | `run_all.py` — **12/12 files, exit 0** |
| Toolkit lint | `--toolkit-only` — **0 errors, 0 warnings, 8 info, exit 0** |
| Assertion evidence | `test_memory_store.py` **39/39, exit 0** in-lane; post-merge simulation of the hard gates **CLEAN**; blocker regression reproduced red then pinned green |
| SOP currency | **exit 0** — SOP staged in the same commit; `[sop-ok]` **not** taken (the boot row genuinely needed the update) |
| py_compile | **PASS** |
| Link + anchor | **0 dead introduced** — every flagged path is a branch name, prose shorthand, or a by-design submodule path |
| Door parity | **4/4 both commands**; none added, renamed or deleted; one door legitimately changed *kind* (finding 12) |
| Lint / types | **not applicable to this repo** — no venv, no ruff, no tsc |

### Acceptance matrix

| # | Item | Proving assertion | Status |
|---|---|---|---|
| A1 | Relocate is a fourth disposition with cross-repo mechanics | `smh-memory-audit.md` Step 5 block; all 4 doors carry it; lint 0/0 | **met** |
| A2a | Lobby index signposts every maintained project | `pointer_problems` — hard fail, fires on missing section / omitted name / empty section / substring collision | **met** |
| A2b | Each project index carries the mirror back-pointer | `backpointer_problems` ships and fires correctly; **AGY's line is not written** — blocked by the `AVCH`-only hook | **NOT met — owed, and the reason the verdict is CONCERNS** |
| A3 | Boot reads the bound project's index | `cicd-boot-sprint-memory.md` Step 1.5 + description; lint 0/0 | **met** |
| A4 | Fan-out over checked-out stores; absence is a named skip | fixtures both directions + `[COVERAGE]`/`[SKIP]` disclosure; main-tree sim reads AGY, skips NEXgen by name | **met** |
| A5 | `audit_block` names Phase 2 | asserted substring `SCC-73 Phase 2` | **met** |
| A6 | Cap and trigger unchanged | `INDEX_CAP == 25*1024`, `TRIGGER_PCT == 0.90` pinned | **met** |

**Drift check (the other direction):** nothing in the diff falls outside the acceptance list. The three
files the pre-work audit added (F4/F5/F6) each correct a document this change made untrue.

### Clean-Code Gate — CONCERNS

**Machine floor** — run_all **PASS** (12/12, exit 0) · workflow_lint **PASS** (0 errors, 0 warnings) ·
sop_currency **PASS** (exit 0) · py_compile **PASS** · link+anchor **PASS** (0 dead) · door parity
**PASS** (4/4) · lint/types **n-a to this repo**.

**Changed-line scan:** no committed secret, no debug print beyond the deliberate `[COVERAGE]`/`[SKIP]`/
`[SIGNAL]` reporting lines, no commented-out code, no bare/broad `except`, no absolute or `C:/` path,
no unowned TODO, no bare `python` (the one operator-typed command is dual-form `python3` / PC `python`).

**Judgment pass:** comment contract satisfied — 8 ticket-keyed provenance comments, no stale
`AIDEV-NOTE`. Convention table clean: naming law (no new commands, no `/sudo-` refs), prefix-permission
(`smh-*` acts on the lobby, `cicd-*` binds a project), one door per platform, generated surfaces
regenerated not hand-edited, rule pointers already present, both-machines spelling, artifacts in the
tree, no personal name in `.agents/` bodies. **Findings 13 and 14 above are the residual CONCERNS**,
plus finding 16 from the review — the block comment asserting the split "is not a hedge" was, for one
commit, contradicted by the code; re-verified true after finding 1's fix.

### Why CONCERNS and not PASS

**A2b is not delivered.** The mirror back-pointer needs a commit in `Projects/AGY_AVIATIONCHAT`, whose
`jira.conf` is `JIRA_KEYS="AVCH"` — an `SCC`-keyed commit there is rejected by the armed hook. That is
a repo boundary discovered mid-build, not an oversight, and the lane ships the *detection* for it. But
an acceptance item without evidence does not get called satisfied, so the verdict stays below PASS.

**Not FAIL:** every gate is green on the changed set, the blocker was found, reproduced, fixed and
pinned before landing, and no reference this diff depends on has moved.

## Your Actions

**Owed, and NOT in this lane — both need an `AVCH` ticket, because that repo rejects `SCC` keys:**
1. **AGY's mirror back-pointer** — one line in `Projects/AGY_AVIATIONCHAT/_artifacts/_memory/MEMORY.md`
   naming the lobby store. Until it lands, the lobby gate prints it as a `[SIGNAL]` on every run.
2. **An AGY-side memory gate.** AGY's 15 memories had no gate at all before this; they now have
   *detection from the lobby*, which is advisory by design. The durable fix lives in that repo.

**The first relocation sweep is deliberately not here.** Moving the ~31 AGY rows is per-item operator
approval — a working session with `/smh-memory-audit`, after this machinery lands.

**Landing order:** `chore/SCC-83-sop-content-audit` shares `workflows_testing_SOP.md` with this lane and
is still pre-work; whoever lands second merges `main` down and re-runs the gate. Its new prose-path gate
(A3b/A3c) already permits the project-relative path class this lane's pointer section introduces —
checked against their plan, not assumed. Separately, `chore/SCC-77-main-write-gate` still edits
`_my_resources/_quick_reference/sudo_workflows_testing.md`, a path SCC-74 relocated; that lane has a
conflict waiting regardless of this work.
