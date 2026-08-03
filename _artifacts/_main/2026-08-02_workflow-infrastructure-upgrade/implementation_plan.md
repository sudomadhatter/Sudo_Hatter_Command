---
IsArtifact: true
ArtifactMetadata:
  title: "Implementation Plan — Workflow Infrastructure Upgrade (verify, don't trust)"
  type: implementation_plan
  date: 2026-08-02
---

# Implementation Plan — Workflow Infrastructure Upgrade

> **Goal:** cut the cost of running the ①②③+close-out loop **without losing a single check**, by
> converting prose-that-an-agent-must-follow-carefully into **scripts that verify**. Grounded in a
> full observed run of `/sudo-code-review` + `/sudo-update-sprint-memory` on story 21.8b (2026-08-02).

## The governing principle

**An instruction may only be deleted after a script enforces it.** Every phase below is therefore
ordered: *build the check → prove it fires → then shrink the prose.* Efficiency is the second-order
effect of verification, never a trade against it. Any step that removes a rule without first
mechanising it is out of scope by construction.

## Measured baseline (2026-08-02, this machine)

| Surface | Measurement | Implication |
|---|---|---|
| `sprint-status.yaml` | 855 lines · **348 KB** · longest line **16,343 chars** · 47 lines >2 KB · 541 of 855 lines are comments · 259 real keys | **~96 % narrative, ~4 % state.** Exceeds the Read tool's limit — it is no longer readable by the agents that depend on it |
| `.agents/commands/` | **55 files · 327 KB** | Read in full on every invocation |
| `.agents/rules/` | 21 files · 108 KB | |
| Preamble duplication | target-resolution in **17** commands · git-policy in **11** · worktree-resolution in **7** | One edit to a shared rule today means 17 edits |
| Artifacts per story | **13 surfaces**; suite totals appear in ≥4 | Already addressed by Plan A (below) |
| Gate enforcement | 0 machine-checkable | `tests-must-gate-for-real` is honour-system |
| Status surfaces | 2 (story frontmatter + board key), **0 enforcement** | Drifted again on 21.8b; 3 memory entries already exist about it |

## ⚠️ Coordination — this plan does NOT stand alone

`_artifacts/_main/2026-08-02_story-artifact-token-optimization/implementation_plan.md` ("**Plan A**")
is written, unexecuted, and already solves artifact sprawl (13 docs → 2, ~50 % output-token cut). It
was **not** applied to 21.8b — that story still wrote a standalone verdict file.

Plan A and this plan **edit four of the same files**: `sudo-code-review.md`, `sudo-update-sprint-memory.md`,
`sudo-merge-epic-workingtrees.md`, the three `_AP` twins, plus the three autopilot engines and the
`/sync-agents` regeneration. Two independent passes = guaranteed conflict and double the review cost.

**Ruling required (see Open questions): these land as ONE coordinated rollout, Plan A first.** This plan
covers only what Plan A does not — **status integrity, the board data model, gate receipts, command
diet, and close-out preflight.**

---

## Wave 1 — Scripts only, zero command edits, zero conflict risk — ✅ **DONE 2026-08-03, `63c211c`**
*(shipped with 3 defects and 1 omission — see `## Self-Audit (2026-08-03)`: F2 · F3 · F5 must be fixed
before Wave 3 wires these scripts into close-out; F6 is the unbuilt check.)*

All new files under `.agents/scripts/` (existing precedent: `check_maps.py`, `record_map_changes.py`,
`generate_repo_map.py`). **Python 3.11 is on PATH; no `yq`/`jq` exists on this machine, so everything is
line-oriented stdlib Python — no new dependencies.** Each is independently useful *before* any command
references it, so Wave 1 can land and be exercised by hand with nothing else changed.

### 1.1 `workflow_lint.py` — the regression net for every later phase
Build this **first**; it is what proves the later waves broke nothing.

Checks, each exiting non-zero on failure:
- every `.agents/commands/*.md` has frontmatter with a non-empty `platforms:` (catches the
  `platforms: []` → syncs-to-nowhere trap)
- every command appears in `commands/INDEX.md`; every INDEX entry resolves
- the three `_AP` twins exist and their step-lists match their primaries (drift detector)
- board file: five zones present, ≤150 lines, `🎯 Right now` ≤8 lines, every relative link resolves,
  zero strikethrough, no `descoped`/`deferred` item in a queue row
- `active-context.md` ≤ 20 KB
- `sprint-status.yaml`: every key line parses; no duplicate keys; no key whose story file is missing
- mojibake scan (`â€`, `Â`, `â•`) across board + context + status files
- `--json` mode for CI, human summary by default

**Verification:** run against today's tree; it must reproduce the two real defects this session found by
hand (the status drift, the mojibake) and produce no false positives on files known good.

### 1.2 `story_status.py` — kill the drift class permanently
The highest ratio of *bug-class eliminated* to *effort spent* in the whole plan.

```
story_status.py check <project>            # every story where frontmatter ≠ board key; exit 1 if any
story_status.py set   <project> <id> <s>   # ATOMIC dual write; refuses on pre-existing disagreement
                                           # refuses downgrades (done → review); prints before→after
story_status.py get   <project> <id>
```

- Resolves story files in **both** naming forms (`story-21.8b-*.md` and `story-21-8b-*.md`) — the
  documented split that has bitten before.
- `set` writes the story frontmatter **and** the board key in one operation, or neither.
- Wired later (Wave 3) into close-out Step 4, board-rebuild Step 1, and `workflow_lint`.

**Verification:** re-create the 21.8b condition on a scratch branch (frontmatter `review`, board
`ready-for-dev`); `check` must flag it and `set` must refuse until `--reconcile` is passed.

### 1.3 `gate_receipt.py` — turn `tests-must-gate-for-real` into an actual gate
Two modes; **`run` is the real target** because it makes fabrication structurally impossible:

```
gate_receipt.py run --story <id> --gate suite -- <the real command>
     # EXECUTES it, captures exit code + stdout, parses totals, records git HEAD,
     # writes _bmad-output/gates/<story>/<gate>.json. A receipt therefore IMPLIES execution.

gate_receipt.py check --story <id> --require suite,ruff,pyrefly,emulator --sha <HEAD>
     # non-zero if any required gate is missing, failed, or was measured on a DIFFERENT sha
```

Receipt: `{gate, result, exit_code, sha, totals, command, duration_s, timestamp}`. Committed with the
story, so the evidence rides the branch through the merge.

This is the piece that closes the gap the whole `tests-must-gate-for-real` rule exists for: today a
verdict claiming `3023 passed` is unfalsifiable after the fact. With `run`, the SHA binding also makes
the ③ staleness rule automatic rather than remembered.

**Verification:** run a deliberately failing suite → receipt records `fail`, `check` exits non-zero.
Amend a commit → `check` exits non-zero on the SHA mismatch without re-running anything.

### 1.4 `closeout_preflight.py` — one call replacing ~10
Today's close-out Steps 0.5/1/2 cost roughly ten tool calls and a large slice of context. One script:

- `git fetch` + ahead/behind for **both** the worktree branch and the shared checkout (the Step 7b drift)
- worktree sweep with LIVE/LOST/HUSK classification (the existing `close-workingtree` logic, reused)
- story status on both surfaces (calls 1.2)
- code-verify: greps the story's File List against HEAD, prints ✅/❌/⚠️ per claim
- `active-context` byte budget
- gate receipt check (calls 1.3)
- **epic-children terminal check** — the question I had to infer today: are all of this epic's children
  terminal, and does `epics.md` diff 1:1 against the keys?
- prints one compact block, `--json` available

**Verification:** run against the just-closed 21.8b state; every line must match what was established by
hand this session.

---

## Wave 2 — Execute Plan A (artifact consolidation) — ✅ **DONE 2026-08-03, `7cb52ef`**

Follow `_artifacts/_main/2026-08-02_story-artifact-token-optimization/implementation_plan.md` exactly as
written. No changes proposed here. It lands first because it **reduces** the file surface Wave 3 edits
(the verdict file disappears, review output moves into the walkthrough) — doing it after Wave 3 would
mean editing the same command sections twice.

> ⚠️ **AUDIT FINDING (2026-08-03) — this wave was already executed before Wave 1 landed.** Commit
> `7cb52ef` covers Plan A steps #1–#10 (rule, 8 commands, 3 `_AP` twins, constitution, autopilot
> reference + all three engines, regenerated workflows and platform copies). Steps #11–#12 verified
> complete after the fact: `artifacts-always-first.md` is byte-identical (19,199 B) across the lobby and
> all three maintained projects, and AGY `_artifacts/AGENTS.md:22` carries the two-doc close. The
> remaining `self-audit-stress-test.md` references in the toolkit are all retirement notices or
> legacy-fallback clauses — Plan A's own verification grep passes. **Do not re-run this wave.** The next
> unexecuted wave is 3.

---

## Wave 3 — One coordinated pass over the command files

Each command file is opened **once** and receives all of its changes together. Diff the `_AP` twin in
the same edit; regenerate workflows via `/sync-agents` at the end, never by hand.

### 3.1 Extract the shared preamble
New `.agents/rules/command-preamble.md` with anchored sections: `§TARGET` (project resolution),
`§WORKTREE` (story-tree resolution + resume), `§GIT` (explicit paths, never `add -A`, never `main`),
`§ECHO` (the `Target:` / `Worktree:` conventions).

Each command's Step 0 / 0.5 collapses to one line:
`Preamble: apply .agents/rules/command-preamble.md §TARGET §WORKTREE §GIT.`

Applies to the 17 / 7 / 11 commands measured above. **Expected: 327 KB → ~230 KB (-30 %).**
`workflow_lint` gains a check that no command re-inlines a preamble section.

### 3.2 Wire the Wave-1 scripts in
| Command | Change |
|---|---|
| `sudo-update-sprint-memory` | Step 1–2 → `closeout_preflight.py`; Step 4 flip → `story_status.py set`; add a **hard gate**: `gate_receipt.py check` must pass before `done` |
| `sudo-code-review` | each gate runs under `gate_receipt.py run`; verdict cites the receipt set |
| `sudo-update-scrum-board` | Step 1 calls `story_status.py check` and renders drift instead of the agent noticing |
| `sudo-close-workingtree` | sweep + gates delegate to the shared preflight functions |

### 3.3 Two rules that were missing, both found this session
- **Subagent-failure contract** (`sudo-code-review` Step 2): on a layer failure — retry once → re-run
  that lens inline → record the degradation in the verdict → **an unrecovered layer caps the verdict at
  CONCERNS.** Today the command only says "report which failed"; two of four layers died on 21.8b and
  recovery was improvised.
- **Epic-closure rule** (`sudo-update-sprint-memory` Step 4): when the just-closed story leaves every
  child of its epic terminal, diff `epics.md` against the keys and close the epic in the same pass —
  with the explicit note that live-verify debts do not hold an epic open. I inferred this today; it
  should not be inference.

---

## Wave 4 — Split state from narrative (the big context win, the biggest risk)

`sprint-status.yaml` becomes machine-readable state; its 541 comment lines and 47 multi-kilobyte rows
move to history.

**Target shape**
- `sprint-status.yaml` — status definitions + `development_status:` with `key: status` and an optional
  **≤120-char** inline note. Estimated **348 KB → ~25 KB**, and readable again.
- `_bmad-output/history/<epic>/<story>.md` — the per-story narrative currently trailing each key.
- `_bmad-output/history/CHANGELOG.md` — the change log, newest first, one `##` section per entry.

**`split_sprint_status.py`, and why it is safe**
Line-oriented regex, never a YAML round-trip (a round-trip would reflow 855 hand-tuned lines and
destroy the comment structure). The migration is **provably lossless**:

1. snapshot the pre-migration file
2. move each narrative span, recording every byte range → destination in `migration-manifest.json`
3. **`--verify` reconstructs the original from (new file + history files + manifest) and diffs it
   byte-for-byte against the snapshot.** The migration is not "done" until that diff is empty.
4. keep `sprint-status.yaml.pre-split` in-tree for one sprint as the rollback

Then re-point readers: grep the toolkit for `sprint-status.yaml` and update every consumer that reads
narrative rather than state.

**Risk: HIGH** — most-read file in the system. Placed last deliberately, so `workflow_lint` (1.1) and
the preflight (1.4) already exist to prove nothing regressed.
**Lever:** this is also the single biggest context win. It can move to Wave 2 if the win is wanted
sooner; the cost is doing it without the lint harness in place. My recommendation is to keep it last.

---

## Wave 5 — Hygiene and propagation

- **Encoding normaliser** + pre-commit hook (`scripts/git-hooks/`, alongside the existing
  `board-stale-stamp.sh`). Mojibake has been losing the "normalise lines you touch" race for months;
  a hook wins it permanently.
- `workflow_lint` into the project's pre-commit hook and `pr-check.yml`.
- Propagate to `Fresh_Workspace_BMAD` (the living template) and each maintained project's
  `_artifacts/AGENTS.md`.
- Memory: new entry for the receipt contract + the "verify, don't trust" principle; update
  `sudo-commands-have-ap-twins-that-drift` and the board-drift entries to point at the scripts that now
  prevent them.

---

## Effort and payoff

| Wave | Scope | Est. sessions | Risk | Payoff |
|---|---|---|---|---|
| 1 | 4 new scripts, no command edits | 2 | **Low** — additive, nothing depends on them yet | Drift + gate enforcement available immediately, by hand |
| 2 | Plan A as written | 1–2 | Low-Med | ~50 % artifact-token cut |
| 3 | One pass over ~20 commands + 3 twins + sync | 2 | Medium | -30 % command bytes; scripts wired; 2 missing rules added |
| 4 | Board split | 1–2 | **High** (mitigated by lossless verify + rollback copy) | 348 KB → ~25 KB; file readable again |
| 5 | Hooks, template, memory | 1 | Low | Hygiene stops regressing |

**Net expected:** roughly half the tokens per story from Plan A, a further large cut from Waves 3–4 on
every command invocation and every board read, and — the part that matters — **three enforcement points
that today do not exist**: status can no longer drift, a gate can no longer be claimed without being
run, and a stale verdict is detected rather than remembered.

## What is deliberately NOT in scope

- The review methodology itself — four adversarial layers found three real HIGH defects on 21.8b; it works.
- BMAD internals (house rule: fix the rule, not BMAD internals).
- TEA test-artifacts — kept standalone by operator ruling 2026-08-02 (recorded in Plan A).
- Any new runtime dependency. Everything is stdlib Python 3.11 + git.

## Verification strategy (per wave, non-negotiable)

1. **Wave 1** — each script reproduces a defect this session found by hand, and produces no false
   positive on a known-good file.
2. **Wave 2** — Plan A's own dry-run: one story closed end-to-end producing two docs.
3. **Wave 3** — `workflow_lint` green before and after; one full ①②③+close-out on the next real story,
   comparing tool-call count and context against today's run as the recorded baseline.
4. **Wave 4** — the byte-for-byte reconstruction diff must be empty; board rebuild and close-out both
   run green against the split file before the `.pre-split` copy is dropped.
5. **Wave 5** — hook fires on a deliberately mojibake'd commit.

## Rulings — operator, 2026-08-02 ("approved")

1. **ONE coordinated rollout, Plan A first** — ruled yes. Wave order stands: 1 (scripts) → 2 (Plan A)
   → 3 (command pass) → 4 (board split) → 5 (hygiene).
2. **Wave 4 stays LAST** — ruled.
3. **Receipt gate: ADVISORY for one sprint, then HARD** — ruled. Mechanics: `gate_receipt.py check`
   defaults hard; Wave 3 wires close-out with `--advisory`. ⏳ **Flip owed:** at the close of the first
   full sprint after Wave 3 lands, remove `--advisory` from the close-out wiring. Check this line at
   every close-out until it is done, then strike it.

---

## Self-Audit (2026-08-03)

**Right-size: FULL** — the plan touches a shared data model (`sprint-status.yaml`), a state machine (the
status-flip contract), and a symbol with ~20 consumers (the command surface). Audited *after* Wave 1
shipped and *before* Wave 3, so it is half conformance-check, half pre-dev gate.

- **Phase 0 (scope · right-size · traceability)** — walked each Wave-1 promise (§1.1–§1.4) against the
  delivered script; 22 of 24 promised checks exist, one is missing (F6), one deviates deliberately (F9).
  Wave 2's own step list traced against `git show 7cb52ef` → already complete (F1).
- **Phase 1 (blast radius)** — traced the four scripts against their real consumers: `_bmad-output/gates/`
  is **not** gitignored in AGY (`check-ignore` → not ignored, 318 files already tracked under
  `_bmad-output/`), so receipts do ride the branch as designed; the risk that killed the whole receipt
  contract is cleared. Three consumer breaks found instead (F2, F3, F5).
- **Phase 2 (over-engineering gate)** — no tripwire fires. Four scripts, stdlib-only, no new dependency,
  no abstraction without a second caller; `wf_common` earns its existence at 4 importers. The one
  *under*-engineering finding (F7) is the opposite failure: a new hard rule with no enforcement.
- **Phase 3 (pre-mortem)** — "shipped and silently corrupted state": the dominant mode is a checker that
  **cannot fire** looking identical to a clean tree (F3), followed by a checker that fires **wrongly** and
  gets muted (F2, F5). Both were verified by execution against the real AGY tree, not by reading.

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| F1 | `implementation_plan.md:133` | HIGH | Wave 2 reads "execute Plan A"; it landed as `7cb52ef`. Acting on the plan re-edits 37 files a second time. | **Plan corrected** — Wave 2 marked DONE inline |
| F2 | `closeout_preflight.py:125` | HIGH | No legacy-verdict fallback (Plan A mandates one). Verified: `--story 17.2` → *"the review step has not run"* → BLOCKED, while `sudo-code-review-17.2.md` sits on disk. Every pre-08-02 story false-blocks; the preflight gets muted. | **FIX in Wave 3, before wiring** |
| F3 | `closeout_preflight.py:35` | HIGH | Branch matched by story slug, but AGY branches are descriptive (`claude/xdist-tail-hang`, `Epic-7`). Every story reports INFO *"already cleaned up"* — a check that cannot fire, reading as a clear. Unmerged commits get stranded (`landing-is-not-closeout`). | **FIX** — resolve from the worktree / Close-Out Handoff block; "no branch" → WARN, never INFO |
| F4 | `closeout_preflight.py:122` | MED | Bare `startswith` with no separator guard: `--story 21.8` matches **both** `story-21-8-master-demo-mode` and `story-21-8b-demo-data-quarantine` (verified). A sibling's verdict can block — or satisfy — the wrong flip. | **FIX** — reuse `find_story_files`' `want + "-"` discipline |
| F5 | `gate_receipt.py:150` vs `:81` | MED | `run` records `git_head(--cwd or project)`; `check` has no `--cwd`, no `--sha` (the plan specified one), and compares by **equality**. A receipt taken in a story worktree, or on a branch that landed via a merge commit, always reads STALE → Wave 3's hard gate blocks every honest receipt → `--advisory` becomes permanent. | **FIX before Wave 3 wiring** — accept `--sha`; use ancestor+diff staleness like `check_artifacts:149` |
| F6 | `implementation_plan.md:122` | MED | §1.4 promises "greps the story's File List against HEAD, ✅/❌/⚠️ per claim". Not built — 8 checks shipped, not this one. Claimed File Lists stay unverified at close-out. | **Build in Wave 3, or strike the bullet** |
| F7 | Plan A `implementation_plan.md:81-84` | MED | New hard budgets (plan ≤8 KB, walkthrough ≤10 KB) are enforced by nothing; `workflow_lint` checks only `active-context`. By this plan's own governing principle an unenforced budget rots. Scope also unruled: **this plan is 15.4 KB**, ~2× the story budget — do `_main/` initiative plans count? | **Add to `workflow_lint` in Wave 3 + rule the `_main/` scope question** |
| F8 | `Projects/*/.agents/scripts/` | LOW | Wave 1 scripts are vendored into all three maintained projects but **untracked** there (identical bytes; AGY's `scripts/INDEX.md` also modified). `commit-and-push-are-one-action` unsatisfied in three child repos. | **Operator call** — commit per repo, or exclude `scripts/` from vendoring |
| F9 | `implementation_plan.md:64` | INFO | §1.1 specifies "`_AP` step-lists match their primaries". Twins are single-pass headless adaptations with their own prose headings, so step-sequence comparison is pure noise. Shipped as primary-reference + git-recency drift instead. | **Accepted deviation** — recorded here |

**Four gates**
- *Verification strategy present?* Yes, per-wave and non-negotiable — **except** Wave 3's "compare tool-call
  count against today's run as the recorded baseline": no baseline artifact was ever written, so the
  comparison has nothing to compare to. **Flag** — record the baseline before Wave 3 starts, or drop the claim.
- *Irreversible / destructive?* Only Wave 4's split; mitigated by byte-for-byte reconstruction + a
  `.pre-split` copy held one sprint. Adequate as written.
- *Any step vague enough the dev will guess?* Yes — §3.2 "wire the scripts in" never says what a close-out
  does with **exit 1 (warnings) vs exit 2 (errors)**. That distinction *is* ruling #3. **Tighten before Wave 3.**
- *Quality fit?* Yes — the scripts match the existing `.agents/scripts/` precedent, stdlib-only, ASCII output.

**Audit verdict: NO-GO** for Wave 2 as written (already executed — F1). **GO for Wave 3**, conditional on
F2 · F3 · F5 being fixed first: all three live in scripts Wave 3 wires into close-out, and wiring a
checker that false-blocks (F2), cannot fire (F3), or always reads stale (F5) converts an enforcement
point into an ignored one — the precise failure this plan exists to end.

<!-- CHECKPOINT id="ckpt_mscl3u61_ncq5zo" time="2026-08-03T02:02:40.633Z" note="auto" fixes=0 questions=0 highlights=0 sections="" -->
