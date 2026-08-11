# SCC-73 Phase 1 — Relocation + two-way pointers

**Lane:** `chore/SCC-73-memory-relocation` · **Repo:** Sudo_Hatter_Command · **Base:** main @ `3536443`
**Close command:** `/smh-close-task-merge-tree`

---

## The decision this implements

The memory index is at **20,011 bytes / 80 %** of the 25 KB cap, and SCC-69 already proved compaction is
spent (a full audit of 145 memories freed **633 bytes**). The remaining lever is not loading everything.

**Operator ruling, 2026-08-11: relocate, do not re-index.** Project-scoped memories move to the project's
own store; the lobby keeps a thin pointer. Rejected alternative: splitting the index inside the lobby
(thin root + category files, files staying put) — it solves the cap but freezes a fork, because
project-launched lanes read only their own repo's store and would never see the lobby's category.

**Why relocation and not a new write rule.** The Claude harness bakes an absolute lobby path into its
memory instruction per session; repo law cannot redirect it. So a relocation sweep must exist *anyway*
to catch Claude's own writes. Once it exists, rerouting the other write paths buys nothing and costs
real risk (submodule commits in every close-out, law changed in three commands, a new way to strand
uncommitted work). **The backstop is the mechanism.** Write paths are therefore UNCHANGED — the lobby
store becomes the inbox, and the audit relocates what has settled.

**The fork is already real, and this un-forks it.** `Projects/AGY_AVIATIONCHAT/_artifacts/_memory/` holds
**15** memories written by lanes launched inside AGY (every repo reads its own store); the lobby holds
**26** more `agy-*` files. Which home a fact landed in depends only on which directory the agent was
standing in. One home per fact is the goal; the sweep keeps healing it.

**Cap stays 25 KB / 90 % trigger — unchanged, deliberately.** Phase 2 (thin root + category index files)
stays parked; its trigger is the audit block printing that Phase 1's levers are spent.

---

## Acceptance — every item checkable (no ACCEPTANCE block on the ticket; from operator intent this session)

| # | Statement | The assertion that proves it |
|---|---|---|
| **A1** | `/smh-memory-audit` carries **relocate** as a fourth disposition (retire / merge / compress / relocate) with cross-repo move mechanics and per-item approval | `workflow_lint.py --toolkit-only` exits 0 **with 0 errors AND 0 warnings** (R2 — SCC-82 drove the baseline to zero; a warning is now a visible regression); grep the command body for the disposition + the `git rm`(lobby)/`git add`(project) mechanics + the both-repos-pushed step |
| **A2** | The lobby index carries a `## Project stores` pointer section, and each present project index carries the mirror back-pointer | new test: the section exists and names **every project on the tracked `.agents/maintained-projects.txt` allowlist**; path *resolution* is asserted only for stores actually checked out — see ⚠️ AUDIT FINDING F1 |
| **A3** | `/cicd-boot-sprint-memory` reads the bound project's `MEMORY.md` after Step-0 binding | grep the command body for the read step under `PROJECT_ROOT`; `workflow_lint --toolkit-only` **0 errors AND 0 warnings** (R2) |
| **A4** | The memory gate fans out over **checked-out** maintained project stores; an uninitialized submodule is a **named skip, never a red** | test both ways: a seeded defect in a present project store FIRES; an empty/absent project dir stays silent and names itself; `run_all.py` green in this worktree **and** in the main tree |
| **A5** | `audit_block()` prints the Phase 2 pointer, so the note surfaces exactly when the 90 % alarm fires | assert the substring `SCC-73 Phase 2` (and that compaction/relocation are named as spent) in `audit_block()` output |
| **A6** | The cap and trigger are unchanged | assert `INDEX_CAP == 25 * 1024` and `TRIGGER_PCT == 0.90` — a pin against future drift |

**Explicitly NOT in this lane:** the first sweep itself. Moving the ~31 AGY rows is per-item operator
approval — a working session with `/smh-memory-audit` after this machinery lands, not a commit here.

---

## Two findings from Step 0 that shaped this plan

**1. A correction to what I told the operator.** I claimed the two-way pointers would be validated for
free by SCC-80's rotted-pointer detector. **They would not be.** `rotted_pointers()` skips `EXEMPT`
(`MEMORY.md`, `README.md`), so index bodies are never path-scanned. A2's validation is **new code**, not
a freebie. Scope grows by one small check; the claim was wrong and is corrected here.

**2. Submodules do not populate in a worktree.** Verified in this lane: `Projects/AGY_AVIATIONCHAT/` is an
empty stub, so the AGY store does not exist here. A gate that hard-failed on a missing project store
would red **every worktree run of `run_all`** — the suite every other lane depends on. Absence must be a
named skip.

Both point the same way, and the precedent is already in the codebase twice:
`rotted_pointers()` returns `{}` when the sibling is not checked out ("10 of 11 hits were false that
way"), and `check_maps.fan_out_targets()` already walks lobby → maintained projects and returns
`(path, reason)` skips that name an uninitialized submodule. **A4 reuses `fan_out_targets`' shape rather
than reinventing it** — silent is wrong; *named* is right.

---

## Steps

**S0 — merge `main` down FIRST (R1).** This lane was cut at `3536443`; `main` is now `ef0af3a` —
**SCC-82 landed mid-audit** and it touched `workflow_lint.py`, its test, `_artifacts/_main/INDEX.md`
and the SOP: three of those are in this change set or its gate set. The plan's own landing-order rule
("whoever lands second merges `main` down and re-runs the gate") now binds **this** lane. Do this
before the first RED, or every baseline below is measured against a repo that no longer exists.

**S1 — RED for the gate fan-out (A4, A6).** Extend `.agents/scripts/tests/test_memory_store.py`:
fixtures for a project store with a seeded defect (fires) and an empty/uninitialized project dir
(silent, named). Pin the cap + trigger. Run; paste RED.

**S2 — GREEN: fan the gate out.** Resolve maintained projects via `check_maps`' allowlist helper; run
`check_store()` over each **checked-out** store; report skips by name. Closes pre-existing debt — AGY's
15 memories are ungated today.

**S3 — RED then GREEN for the pointer contract (A2).** Test asserting the lobby `## Project stores`
section exists and names every project on the **tracked allowlist** (F1 — never "every checked-out
project", which is vacuous in a worktree); resolution asserted only for present stores; plus the mirror
line in each present project index. Then write the sections. *(Lobby index edit is additive — see the
SCC-77 note.)*

> ⚠️ **AUDIT FINDING F2 — the law forbids this step as written, and S6 must fix it first.** `AGENTS.md`
> §7 makes `_artifacts/_memory/` **READ-ONLY except through two sanctioned flows** (the Claude harness
> auto-memory and `/cicd-update-sprint-memory`'s learning-routing step). A `chore/*` lane is neither, so
> writing the pointer section here violates the standing law — and deferring it to the sweep instead
> lands A2's test failing on `main`. **Resolution: S6 lands first** and draws the line explicitly —
> editing memory **content** stays read-only; a **structural** change to the index, made under a
> ticket, is sanctioned. Then S3 writes the section under that clause. Do not reorder these two.

**S4 — RED then GREEN for the Phase 2 note (A5).** Assert the substring in `audit_block()`; then write it.

**S5 — the command surface (A1, A3).** Edit `.agents/commands/smh-memory-audit.md` (relocate disposition
+ mechanics) and `.agents/commands/cicd-boot-sprint-memory.md` (project-index read). Regenerate doors
with `/smh-sync-agents` — generated surfaces are never hand-edited. Lint to 0 errors.
**F7:** keep the A1 mechanics block **git-only** — a hard-coded `python3` is unrunnable on the PC.
**F4 (added by the audit):** `.agents/commands/INDEX.md:56` also changes — its row still says *"90 % of
the **20 KB** cap"* (stale since SCC-69 raised it to 25 KB) and *"retire / merge / compress"* (3 of the 4
dispositions). The linter only checks that a command is *mentioned* in INDEX.md, never that the prose is
true, so this rotted invisibly — which is the same class of failure this ticket exists to fix.

**S6 — the law (A1). Lands BEFORE S3 (see F2).** `AGENTS.md` §7: the two-tier model — lobby =
cross-project **and inbox**; project store = settled project history; relocation happens **only** inside
`/smh-memory-audit`, per item, on the operator's word — **plus the content/structure line F2 requires.**
Restate the obligation as a step, per the Always-On rule.

**S7 — SOP, indexes + review gate.** `docs/_scc_sops_prds/workflows_testing_SOP.md` in the same commit
(usage surface changed; the armed gate refuses otherwise). Plus two index rows the audit found missing:
**F5** `docs/workspace-standard.md:176` — the PATH CONTRACT row describes ONE canonical store, and after
this project stores are first-class; **F6** `_artifacts/_main/INDEX.md` — a row for this session folder
(SCC-78 landed without its row and SCC-80 had to add it; `check_maps` flags the gap). Then
`/smh-code-review`.

---

## Landing-order dependencies (read from the live lanes, not from grep)

| Lane | Overlap | Call |
|---|---|---|
| `chore/SCC-77-main-write-gate` | `_artifacts/_memory/MEMORY.md` | **No conflict.** SCC-77 rewrites exactly one row (Git branch model, Toolkit section); this lane appends a new `## Project stores` section. Different lines → git auto-merges. Either order works; second to land merges main down first. |
| `chore/SCC-82-workflow-lint-zero-warnings` | `docs/_scc_sops_prds/workflows_testing_SOP.md` | **Real overlap.** Both stage the SOP. Different sections (SCC-82 = workflow_lint; this = memory audit + boot), so a textual auto-merge is likely but not guaranteed. **Whoever lands second merges main down and re-runs the gate.** |

**⚠ Flagged for the operator, not this lane's to fix:** `chore/SCC-77-main-write-gate` edits
`_my_resources/_quick_reference/sudo_workflows_testing.md` — a path SCC-78 **relocated**; it no longer
exists on main. That lane has a merge conflict waiting regardless of this work.

---

## Risks

- **A relocated memory is invisible to a lobby session until someone looks at the pointer.** Mitigated by
  A2's pointer section (the signpost stays in the index every session loads) and A3 (project lanes read
  their own store at boot). Residual: a lobby session working *on* AGY must follow the pointer. Accepted
  — that is the cost of not loading everything, and it is the whole point of the change.
- **A sweep that moves a cross-cutting fact is a real loss of reach.** Mitigated by per-item approval —
  nothing auto-moves, ever. The `⛔ Read first` tier and cross-cutting hazards stay in the lobby by rule.
- **Cross-repo moves are two commits in two repos**, and `ignore = all` on the submodule means the lobby's
  `git status` will not show a dirty AGY store. The A1 mechanics must commit **and push** both, and say so.

---

## Self-Audit (2026-08-11)

**Mode:** PRE-WORK · **Right-size: FULL** — the change touches a gate that runs inside `run_all`, the root
law (`AGENTS.md` §7), two commands across four platform doors each, and the SOP. Any one of those alone
would force Full.

**Phase 0 — scope, right-size, checkable list, traceability.** Change set named: 6 hand-edited files
(`test_memory_store.py`, 2 command bodies, `AGENTS.md`, `MEMORY.md`, the SOP) + 3 index rows the audit
added (F4/F5/F6) + 8 regenerated doors + the artifact folder. Traceability runs clean **both** ways —
every acceptance item maps to a step (A1→S5+S6, A2→S3, A3→S5, A4→S1+S2, A5→S4, A6→S1) and no step
traces to nothing (S7 is the SOP/index obligation the gates impose, not creep). **Lane check: no
deployable path** (`backend/`, `frontend/`, `firebase/`, `functions/`, `mobile/`, `.github/`) is in the
change set — this closes through `/smh-close-task-merge-tree`, correctly.

**Phase 1 — blast radius.** Doors **8/8 present** for both commands, so `/smh-sync-agents` regeneration
covers them and `test_command_surfaces.py` gates parity. `run_all` **auto-discovers** `test_*.py` — no
wiring. `_RULE_POINTERS` **cleared**: `smh-memory-audit.md:8` already cites `git-policy` (so adding git
mechanics will not trip the lint) and `cicd-boot-sprint-memory.md:80` already cites
`worktree-per-story`; the boot change adds a read, no git verbs. The reference sweep found **three sites
the plan had missed** (F4, F5, F6) and the blast-radius table's own `_artifacts/_memory/` row raised the
law conflict (F2).

**Phase 2 — over-engineering gate (STRICT).** Ten tripwires walked; **two fired.** *Generalizing for
N when N=1* — the pointer section and fan-out serve "every maintained project" while only AGY's store
has content today. **JUSTIFIED, and stated rather than assumed:** the allowlist already carries two
projects, and the ticket names two by hand plus *"model has permission to create these as needed"* —
N>1 is the requirement, not a hypothetical. *A gate that cannot fail* — **F1**, revised. Neither *new
script* nor *clone-and-tweak* fired, specifically because the plan reuses `check_maps.fan_out_targets`
and follows `rotted_pointers()`' absence precedent instead of writing new machinery.

**Phase 3 — pre-mortem.** Eight rows walked. *The gate fires on someone else's commit* drove **F3** and
was **measured, not reasoned**: `check_store()` against AGY's live store returns **0 problems**, 3,304 B
(13 % of cap), `audit_due` False — so newly gating it cannot red an unrelated lane. *Empty input reads
as PASS* is **F1**. *The other machine* is **F7**. *Rollback:* this lane is additive text and test code
with nothing irreversible — the cross-repo file **moves live in the sweep, not here**, and are `git mv`
in two repos under per-item approval. *Fresh clone:* no new hook ships, so no `core.hooksPath` exposure.

### Findings

| # | Where | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| **F1** | plan A2 / A4 | **HIGH** | "names every **checked-out** project" is vacuous in a worktree — zero are checked out there, so the assertion passes trivially. Worktrees are where nearly all work happens, so the pointer contract would be enforced almost nowhere while reading green. | **REVISED in A2/S3.** Assert against the tracked `maintained-projects.txt` allowlist (present in every checkout); only path *resolution* skips when a store is absent. Fan-out skips must be **named and asserted**, never silent. |
| **F2** | `AGENTS.md` §7 vs S3 | **HIGH** | §7 makes the store READ-ONLY outside two sanctioned flows; a `chore/*` lane is neither. Writing the pointer section here violates standing law — but deferring it to the sweep lands A2's test **failing on `main`**. | **RESOLVED by ordering.** S6 lands first and draws the line: memory **content** stays read-only; a **structural** index change under a ticket is sanctioned. S3 then writes the section under that clause. |
| **F3** | fan-out ↔ AGY store | MED → **CLEARED** | A newly-gated store carrying a pre-existing defect turns `run_all` red on the next unrelated commit, by someone who never touched memory. | **MEASURED CLEAN** (0 problems / 3,304 B / not due). Safe to land; re-measure in S1 as the RED baseline. |
| **F4** | `.agents/commands/INDEX.md:56` | MED | Row still says *"90 % of the **20 KB** cap"* — stale since SCC-69 — and lists 3 of the 4 dispositions. The linter checks only that a command is *mentioned*, never that the prose is true. | **ADDED to S5.** |
| **F5** | `docs/workspace-standard.md:176` | MED | The PATH CONTRACT row describes a single canonical store; after this, project stores are first-class. A reader following the contract learns a model the system no longer has. | **ADDED to S7.** |
| **F6** | `_artifacts/_main/INDEX.md` | LOW | No row for this session folder → `check_maps` flags the gap post-merge. Precedent: SCC-78 landed without its row and SCC-80 had to add it. | **ADDED to S7.** |
| **F7** | S5 / A1 mechanics | LOW | A mechanics block hard-coding `python3` is unrunnable on the PC. | **Keep the block git-only** (noted in S5). |

**Sibling-lane landing order** — unchanged from the plan's table and re-verified live: `SCC-77` touches
one `MEMORY.md` row (auto-merges against this lane's new section); `SCC-82` shares
`workflows_testing_SOP.md` (**real overlap**, different sections — whoever lands second merges `main`
down and re-runs the gate). ⚠ Separately, `SCC-77` still edits the pre-SCC-74 SOP path
`_my_resources/_quick_reference/sudo_workflows_testing.md`, which no longer exists on `main` — that
lane has a conflict waiting **regardless of this work**, and it is the operator's to know about, not
this lane's to fix.

**Four gates.** *Verification strategy:* present — every acceptance item names the command that proves
it, strengthened by F1. *Irreversible:* nothing in this lane; the sweep's cross-repo moves are `git mv`
in two repos under per-item approval. *Vague enough to guess:* S3/S6 were, and F2 pins the order. *
*Convention fit:* naming law untouched, doors regenerated not hand-edited, artifacts under
`_artifacts/_main/<date>_<slug>/`, SOP in the same commit.

```
Audit verdict: GO
```

**GO with all seven findings baked in above.** The two HIGH findings are fixed in the plan text, not
merely noted: F1 changed what A2 asserts, and F2 changed the order S6 and S3 must land in.

---

## Self-Audit — re-run (2026-08-11)

**Why this ran.** Not a repeat: the command's own rule is that when findings are baked into a plan you
**"re-run only the phases the change touched"** — and the first pass appended its verdict without doing
that. The revisions had expanded the change set by three files (F4/F5/F6) whose blast radius was never
traced. **Still PRE-WORK; nothing is built.** Phases re-run: **1** (full — the one that goes stale),
**3** external-state rows, **0** traceability for the revised A2, **2** for the expanded change set only.
Phases deliberately skipped: 0's right-sizing and 2's full tripwire walk — settled, and re-asking is the
theatre this command warns against.

**And `main` moved while the first audit was being written**, which is precisely the staleness this
re-run exists to catch.

| # | Finding | Sev | Disposition |
|---|---|---|---|
| **R1** | Lane is based on `3536443`; `main` is now `ef0af3a` — **SCC-82 landed mid-audit**, touching `workflow_lint.py`, its test, `_artifacts/_main/INDEX.md` and the SOP. Three sit in this change set or its gate set, so every baseline in the plan was measured against a repo that no longer exists. | **HIGH** | **New S0**: merge `main` down before the first RED. The plan's own "whoever lands second merges down" rule now binds this lane. |
| **R2** | The lint bar moved. Measured on current `main`: `0 error(s), 0 warning(s), 8 info — exit 0`; SCC-82's merge states *"the baseline is now zero."* A1/A3 said only *"exits 0"*, which stayed true **with** warnings — so a warning this change introduced would have landed invisibly. *(The `commands-index` warning recorded in the first pass's baseline was an artifact of the stale worktree; it is fixed on `main`.)* | **HIGH** | **A1/A3 tightened** to 0 errors **and** 0 warnings. |
| **R3** | **A sibling lane that did not exist during the first audit**: `chore/SCC-83-sop-content-audit`, based on `ef0af3a`. It rewrites prose across `docs/_scc_sops_prds/` (28 unresolved refs, including the stale *"13-doc manifest"* inside `workflows_testing_SOP.md`) and ships a **new gate**, `test_sop_prose_paths.py`, that reads backticked paths **in prose** — the exact construct A2's pointer section is made of. | **HIGH** | **Semantic collision resolved favourably, verified in their plan:** its **A3b** keeps project-relative paths quiet and **A3c** *"degrades to silence when `Projects/` is unpopulated"* — explicitly permitting the path class A2 introduces. (Third independent instance of this precedent, after `rotted_pointers()` and `fan_out_targets()`.) **Textual overlap is real** on the SOP: different sections, second to land merges down. **New obligation:** if SCC-83 lands first, every backticked path S7 writes into the SOP must resolve or be project-relative. |
| **R4** | My own baked-in F5/F6 added rows to two **tables** that could carry project paths unresolvable in a worktree — a self-inflicted version of the bug this system keeps hitting. | MED → **CLEARED** | **Measured, not assumed:** `_artifacts/**/INDEX.md` is an explicit **narrative-ledger exemption** from path-existence linting (SCC-74, `_NARRATIVE_LEDGER_ROOT`), and `docs/workspace-standard.md` is neither the repo-map CURATED block nor an `INDEX.md`, so it is not path-checked at all. Both rows are safe as written. |
| **R5** | `chore/SCC-77-main-write-gate` unchanged at `8e2ee83`, tree clean. Its pre-SCC-74 SOP-path conflict still stands. | LOW | Unchanged, still the operator's to know, still not this lane's to fix. |

**Phase 0 (traceability only).** The revised A2 still maps to S3; the three added files map to S5/S7; the
new S0 traces to R1. No acceptance item is stepless and no step is orphaned.

**Phase 2 (expanded change set only).** Did F4/F5/F6 introduce creep? **No.** Each is a correction to a
document the change makes untrue — a stale cap figure, a PATH CONTRACT describing a model that no longer
holds, a missing ledger row the artifacts law requires. No new abstraction, no new file beyond index
rows, nothing built for a hypothetical.

**Phase 3 (external-state rows).** *A sibling lane lands first* — now real, twice (R1 landed, R3 pending);
handled by S0 and the SOP landing-order note. *Four platform caches* — unchanged, 8/8 doors present.
*Fresh clone* — unchanged, no new hook ships.

```
Audit verdict: GO
```

**GO.** Two findings changed the plan text again — R1 added a prerequisite step, R2 tightened two
acceptance assertions — and R3's collision was checked against the other lane's actual plan rather than
assumed. Nothing here reverses the first pass; it corrects what a moving `main` invalidated.
