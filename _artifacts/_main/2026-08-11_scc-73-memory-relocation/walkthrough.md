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

**GREEN — main-tree behavior, proved before landing** (the environment the operator actually runs in,
where the submodules *are* populated):

```
stores read : ['AGY_AVIATIONCHAT']
skips       : ['NEXgen-VR-Director: no memory store yet - nothing to gate']
--- would any of this BLOCK the lobby? ---
  check_store(AGY_AVIATIONCHAT) -> CLEAN
--- advisory signals (loud, never blocking) ---
  [SIGNAL] `AGY_AVIATIONCHAT`'s MEMORY.md never names the lobby store (`_artifacts/_memory/`) - ...
```

**The gates, run bare (never piped — a pipe reports the pipe's exit code):**

```
run_all exit=0        -- 12/12 files passed
lint    exit=0        -- 0 error(s), 0 warning(s), 8 info
```

**Index size:** 20,390 B → **21,107 B** (82 % of the 25 KB cap; trigger at 90 % untouched). The section
costs ~700 B now and is what makes it safe to remove far more than that in the first sweep.

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
