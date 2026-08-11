---
IsArtifact: true
ArtifactMetadata:
  title: SCC-83 walkthrough - the prose nobody checked, and the two doctrines that had gone stale inside it
  type: walkthrough
  date: 2026-08-11
---

# SCC-83 — Walkthrough: a path check that found stale *law*

**Date:** 2026-08-11 · **Repo:** Sudo_Hatter_Command (lobby) · **Lane:** Task (LOCAL)
**Branch:** `chore/SCC-83-sop-content-audit` · **Base:** `ef0af3a`
**Subtasks:** SCC-84 · SCC-85 · SCC-86 · SCC-87

> **⛔ NOT merged.** Pushed, gated, handed back for `/smh-close-task-merge-tree`.

## Task Checklist

- [x] **SCC-87** — T9 added to `test_sops_prds_folder.py`, RED first, **16 controls**
  - Four of them exist because the RED found false-positive classes the plan had not predicted
- [x] **SCC-84/85/86** — all **12** genuine references fixed; **0 findings from a worktree AND from
      the main checkout**
- [x] **A8 / F4** — `INDEX.md` now states T9's scope, its environment-dependent reach, and that
      `git log` dates are meaningless in this folder
- [x] Gates: `run_all` 12/12 exit 0 · lint 0/0 exit 0 · `sop_currency` exit 0

## The question that produced this

*"Were you triggered to actually check the whole folder to make sure it's not stale?"*

**No — and nothing would have.** All three mechanisms answer *"does this pointer resolve."* None
answers *"is what this page says still true."* `check_maps` reads backticked paths **only inside
table rows**; T3 reads **markdown links**. A path in a sentence was seen by nothing.

## ⭐ The two findings that justify the whole ticket

Neither is a broken link. Both are **stale doctrine** that a path check walked me into.

**1. The artifact bucket rule taught the model that was inverted a fortnight earlier.**
`file_folder_structure+maintaining.md` said artifacts go *"where you work FROM (your cwd)"* — so a
project's history landed in the lobby whenever a chat happened to start there. That rule was
**inverted on 2026-07-30** (`project-first-artifact-locality`): location follows **ownership**,
project-local *even when the chat starts in the lobby*. The page taught the old model for twelve
days, and the only reason I looked at that paragraph is that a dead `_artifacts/AGY_AVIATIONCHAT/`
path sat inside it.

**2. The very next line named a source that was retired as an agent input.** It said *"pick up"*
surfaces `_my_resources/open_tasks/todo_list.md`. `AGENTS.md` §7 says **⛔ NOT from** that file —
retired 2026-08-09 because it is personal notes, it goes stale, and it duplicates live tickets.
**No path check could ever have caught this one** — the file exists. A human reading the paragraph
caught it, and the dead path is what put a human in the paragraph.

**3. And the SCC-63 over-rename had a survivor.** `tea_testing_guide.md` said
`cicd-code-review-tea-9-tia-ci.md`; the file on disk is `sudo-code-review-…`. Commit `3eea4d0`
fixed exactly this in 5 masters + 2 rules — **and missed this doc, because at that moment it lived
in `_my_resources/`, which the sweep is forbidden to scan.** The SCC-74 thesis demonstrating itself.

## ⭐ 181 → 28 → 12: the number was the hard part

| Sweep | Reported | Why it was wrong |
|---|---|---|
| First, crude | **181** | bare filenames counted as paths; run from a worktree where `Projects/` is an empty stub |
| Ground-truthed | 28 | separated bare names, project-relative, non-path tokens |
| T9, from a worktree | 25 | still counted things a stubbed project owns |
| **T9, from the main checkout** | **12** | the truth |

**The 25-vs-12 gap was nearly a shipped defect.** Fix the 12 and every lane would still have gone
red on 13 findings its author could not fix — which is how a gate gets ignored, then deleted. So
T9 asserts only what is provable **without** the projects when any is stubbed, and prints how many
it could not see. A reduced run is visible; it never reads as a clean one.

## The RED earned its keep four times

Every one of these was found by running it, not by designing it:

1. **Relative tokens.** `../workspace-standard.md` is correct and T9 called it dead — I resolved
   against the repo root instead of the containing file.
2. **The explicit `Projects/` form.** My A3c control covered `backend/…` (first segment absent) but
   `Projects/AGY_AVIATIONCHAT/scripts/` sails past it, because `Projects/` *does* exist. **The
   control had a hole in exactly the trap it was written for.**
3. **A shadowed parameter.** The mis-path lookup assigned `base = Path(t).name`, clobbering the
   `base` parameter after the first token. The suite crashed rather than lying — the good outcome.
4. **A fixture asserting the wrong target.** `../top.md` from `fx/docs` is `fx/top.md`; I had
   created `fx/docs/top.md`, so the control failed for its own reason, not the code's.

Three more classes surfaced when T9 ran against the real docs and flagged things that were **not
defects** — each now a control:

- **Struck-through paths.** Line 11 already read ``~~`…master-implementation-plan.md`~~ — **gone**``.
  Reporting it asks the author to delete the line recording the removal.
- **Provenance folders.** *"Consolidated from `_my_resources/_quick_reference/`"* is the doc doing
  its job. Exempt at folder level; a **file** under them is not — that is a live instruction to open
  something that moved, and two of those were real defects.
- **Runtime output.** `_artifacts/_autopilot-run.log` exists only while a run is live.

Same inversion as T4's `DISCUSSED_AS_RETIRED`, one tier down: **the literal appears most often in
the prose about its own removal.**

## Evidence

**RED** (worktree, after the controls were corrected):
```
T9 controls green: 13
[FAIL] T9 every prose path reference resolves:
    autopilot_bmad_dev_loop.md -> .claude/commands/cicd-autopilot-claude.md (moved -> .agents/commands/...)
    jira_integration_guide.md  -> _my_resources/_quick_reference/git_walkthrough_settings.md (moved -> docs/_scc_sops_prds/...)
    jira_integration_guide.md  -> _my_resources/_quick_reference/jira_manual.md (moved -> docs/_scc_sops_prds/...)
```
**GREEN**, both environments:
```
WORKTREE (9 stubs): 0 finding(s)      MAIN CHECKOUT: 0 finding(s), 1 stubbed
T9 controls green: 16 · -- 34/34 passed -- · run_all 12/12 exit 0
```

## Your Actions

Branch pushed, preflight to follow. **Landing-order:** `chore/SCC-77-main-write-gate` also touches
`workflows_testing_SOP.md`; `git merge-tree` verified clean either way — whoever lands second merges
main down.

**Still owed, unchanged and deliberately not done here:** whether `tea_testing_guide.md` belongs in
the lobby at all (48 project-relative refs) is an **AVCH** architecture call; AGY's stale
`sudo_workflows_testing.md` needs its own key in that repo.

---

## Code Review (2026-08-11)

Verdict: FAIL @ 6cdca82ff98f1473cee6896a30c3c4168cdb4f16
Suite evidence measured at the same sha (`run_all` 12/12 exit 0) — green, and **green is not the point**.

**Scope:** 11 files, 292 new lines of Python. **Method:** `/smh-code-review` end to end — Step 0.7
re-derivation, a clean-room adversarial pass in a subagent with no conversation context, acceptance
audit against A1–A8, the command-centre gate run bare.

### ⛔ Why FAIL, in one line

**Every gate is green and the gate does not gate.** The adversarial pass mutation-tested the code and
proved the primary arm never executes in any checkout that exists — the exact failure this file was
written to prevent, shipped inside the fix for it.

### Findings

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| H1 | `test_sops_prds_folder.py:534,314-325` | **HIGH** | `strict=not stubbed` is a **global** switch. Worktree: 9 stubs → `strict=False`. **Main checkout: `Fresh_Workspace_BMAD` is an uninitialised submodule → also `strict=False`.** So `out[t] = "resolves nowhere"` never runs anywhere; only the `moved ->` arm can fire. Independently reproduced: shipped mode **0/0** findings, `strict=True` **14/1**. Worse, the switch is driven by *untracked* state — one `.DS_Store` in a stub flips the whole run strict and every lane goes red on 14 findings its author cannot fix. | **open** — downgrade must be **per token** (drop only tokens whose head also exists in a *stubbed* project; keep `resolves nowhere` for lobby-only heads) |
| H2 | `:219,275` | **HIGH** | `STRUCK = ~~[^~]*~~` matches across newlines and is applied to the whole document before tokenizing. One unbalanced `~~` plus any later strikethrough blanks everything between them — proven: 6 dead references vanished. A `~~~` fence is eaten whole. **A whole-file off-switch reachable by a typo.** | **open** — `[^~\n]*`, apply per line, fixture the unbalanced case |
| H3 | `:303-304` | **HIGH** | `r.rglob(leaf)` per token across 9 roots: **+18.3s on every `run_all`** at the realistic defect count, and `[:1]` slices *after* full evaluation so it never short-circuits. It descends into `.claude/worktrees/` and **cited a sibling lane's transient copy as the remediation target** — I saw that string in my own output and did not act on it. | **open** — one pruned leaf index per run |
| H4 | `:185-191`, fixture `:411` | **HIGH** | **The plan's own headline finding F1 is not fixed.** Deleting `NOT_A_PATH` entirely leaves the suite **34/34 PASS**; 6 of its 7 alternations are provably dead. A3d — the control written to make it falsifiable — controls nothing. The module comment claiming *"every class below has a control"* is false. | **open** |
| M1 | `:455-459` | MED | The MOVED-vs-gone fixture's ternary evaluates to literal `True`; mutating the `moved ->` arm survives. The one working arm has **zero** coverage. Also prints detail on PASS, violating `det()` at `:137`. | **open** |
| M2 | `tea_testing_guide.md:599-603` | MED | **A regression I introduced.** Options A and B now carry identical paths and line 603 still says *"Option A changes every project."* `.agents/rules/testing-standards.md` was a **prospective** path ("write the rule here"); I took the detector's first `rglob` hit as a remediation instruction. Same inversion `ABSENT_BY_DESIGN` exists to prevent, with no exemption class for create-me paths. | **open — revert first** |
| M3 | `:292-294` | MED | Cross-root resolution accepts a lobby path because *some* project has that layout (`frontend/package.json` resolves in 6 roots). | **open** |
| M4 | `INDEX.md` new block | MED | Two shipped claims false: *"exactly 2 non-backticked tokens"* is **18** by T9's own filters (~9× off), and *"fenced blocks"* is impossible — `CODE_SPAN` requires backticks. | **open** |
| M5 | `:379` | MED | A3c asserts on a token killed by the first-segment rule, not by `_is_stub_project`. The `mkdir` is inert; the comment claims otherwise. | **open** |
| L1–L6 | various | LOW | Dead docstring (two adjacent literals); `ABSENT_BY_DESIGN` exact-string/asymmetric on trailing slash; Windows separators silently skipped; case-insensitive false negative; `:538` is a print dressed as a check, inflating 34/34; `_scan_roots` double-evaluates and returns a heterogeneous list. | **open** |

**Confirmed clean (not findings):** no catastrophic backtracking (40k-char inputs ≤1 ms) · `CODE_SPAN`
correctly bounds stray-backtick damage to one line · **T9 *is* correctly inside the `scannable` guard,
so plan finding F3 was genuinely honoured** · all five doc-fix targets resolve, including the
`cicd-` → `sudo-` historical-artifact revert.

### Acceptance audit

| Item | Evidence | Result |
|---|---|---|
| A1 no unresolved prose path | 0 findings both environments — **but both are weak-mode runs (H1)**, presented in the body as two independent confirmations when it is one | **NOT satisfied** |
| A2 fires on a planted dead path | fixture green | ✅ |
| A3a/A3b/A3c bare · project-relative · stub | green — **A3c is inert (M5)**; A3b/A3a real | ⚠ partial |
| A3d non-path classes | **controls nothing (H4)** | **NOT satisfied** |
| A4 by-design absences | both still absent on disk; narrowness fixture real. Plan said `_pipeline/*`; built `_artifacts/_autopilot-run.log` — undeclared deviation | ⚠ |
| A5 run_all auto-discovers | 12/12 exit 0 | ✅ |
| A6 lint baseline held | 0 errors 0 warnings exit 0 | ✅ |
| A7 SOP currency | exit 0 | ✅ |
| A8 freshness note | present in INDEX | ✅ |

### Step 0.7 — re-derivation against current `main`

1. **Nothing moved under this diff.** Zero files landed on `main` since the fork at `ef0af3a`.
2. **True overlap with `main`: none**; `merge-tree` clean.
3. **⚠ Landing order: `chore/SCC-73-memory-relocation` committed work mid-review and now CONFLICTS**
   with this lane on `_artifacts/_main/INDEX.md` (both add a row at the table head) — confirmed by
   `merge-tree` three-stage entries, not predicted. Trivial to resolve (keep both rows); whoever lands
   second merges main down. `chore/SCC-77-main-write-gate`: no overlap.

### Process note

My shell's cwd silently reset from the worktree to the main checkout mid-review, and one verification
probe ran in the wrong tree before I caught it. Step 3's evidence is unaffected (its `git rev-parse
HEAD` printed `6cdca82f`). **The earlier "12 findings from the main checkout" figure in this
walkthrough was measured with the default `strict=True` — a mode the shipped gate never runs in.**
That is how H1 hid: I verified a different program from the one I committed.

**Changes applied: none.** The four HIGHs are design-level, not trivial patches — `/smh-quick-dev`
Step 3.5's eject tripwire applies, so this is handed back rather than patched under a review.

## Round 2 — remediation (2026-08-11)

Plan: `remediation_plan.md` beside this file. Every design choice there is preceded by the probe
that decided it, because round 1 failed for verifying a program it had not committed.

### The reframe: four HIGHs, one root cause

H1, H3 and half of M3 were three symptoms of one property — **the checker's answer depended on where
you were standing.** `Projects/*` are separate gitignored repos, so a worktree sees empty stubs while
`main` sees them populated. Round 1 coped: a `strict` mode to suppress the unprovable, and an
`rglob` to recover what the suppression lost. Both coping mechanisms failed.

`_scan_roots()` now resolves project roots from `git rev-parse --git-common-dir` — the same cure as
the repo-map label bug. **`strict` is deleted outright**, not made per-token: once coverage stops
varying by lane there is no mode to switch, and a per-token version of a switch driven by untracked
state would be a smaller defect of the same kind.

| Configuration | shipped round 1 | `strict=True` | **round 2** |
|---|---|---|---|
| Worktree (9 stubs) | 0 findings | 14 | **7** |
| `main` (8 populated) | 0 findings | 1 | **7** |

Both columns measured with the allow-list **lifted**, keys *and* values compared. They are identical.

### What the mutation run found that I did not

B4 said a fixture only counts if breaking its target turns the suite red. The first run said
**7/12 caught** — five of my new fixtures controlled nothing:

- **`docs/...`** never reaches `NOT_A_PATH`: the token is `rstrip`'d of `.,;:)` first, so it becomes
  `docs/` and resolves. Only a *mid-path* elision is live. My H4 control tested the dead form.
- **H2's two halves were each sufficient**, so neither mutation was observable — the same
  belt-and-braces decoration I had just cut from `NOT_A_PATH`, re-introduced in the fix for it. Kept
  the newline-bounded regex, dropped the per-line application.
- **L2's fixture** ran in a temp root with no `_my_resources/`, so the first-segment rule killed the
  token before the allow-list was consulted.
- **H3** asserted nothing about un-pruning.

### A second lane/main asymmetry, found only because the first fix was fixtured

`_is_stub_project()` asked "is `<root>/Projects/<name>` empty?" — and in a lane *every one of them
is*. So explicit `Projects/<name>/…` tokens were skipped in a lane and checked from `main`. **The
out-of-band B1 probe missed it, because an allow-list entry happened to mask the only real example.**
Split into two jobs: no root named `<name>` → not checked out; otherwise resolve the remainder
*inside* that root, since the token is spelled lobby-relative while the project is its own checkout.

A related one: the `moved ->` target was reported relative to whichever root the index hit, so a lane
printed `_bmad-output/x.md` where `main` printed `Projects/AGY_AVIATIONCHAT/_bmad-output/x.md`. Same
file, two answers, and the lane's names nothing. Now always lobby-relative.

**The lesson, and it is the round-1 lesson again:** a suite that only ever runs in one checkout
cannot see an answer that changes with where you stand. So the equality is now **a fixture** — same
docs, same project root, two lobbies (one populated, one stubbed) — not a probe I ran by hand.

### Prospective paths were a missing class, not a doc defect

**M2 was mine.** I took the detector's first `rglob` hit as a remediation instruction and rewrote
`tea_testing_guide.md`'s options A and B to identical paths while line 603 still contrasted them.
Reverted.

Reading the one real finding showed the same class: `_artifacts/opencode/` is documented as *"created
on first use"*. Both are **create-me** paths, and `ABSENT_BY_DESIGN` had no class for them — so the
only way to quieten a correct sentence was to make the doc wrong. That is the inversion the
allow-list exists to prevent, committed by the person maintaining the list. Added as a second class,
each entry with its written reason; the narrowness control already covers it.

### Evidence

| Gate | Result |
|---|---|
| **Mutations caught** | **15/15**, baseline **45/45** green — including a mutation for every fix above |
| `run_all` | **12/12 exit 0** (bare, unpiped) |
| `workflow_lint --toolkit-only` | **0 errors, 0 warnings, exit 0** — baseline held |
| T9 lane vs main | **identical keys and values**, exemptions lifted |
| Index cost | 9 roots / 20,447 entries / **0.12 s** (replaces **+18.3 s** of `rglob`); lobby index 3,574 paths, not 20,597 |
| Both arms fire | with the 4 by-design entries lifted: 2 × `resolves nowhere`, 1 × `moved ->` |

### Two things I did NOT do, and why

- **The "reduced coverage must FAIL" check was wrong and I removed it.** It fired immediately on
  `tdad_stack_install_guide.md` naming `Projects/Fresh_Workspace_BMAD/backend/requirements.txt` — a
  declared submodule (`.gitmodules`, `ignore = all`) deliberately left uninitialised. The doc is
  right, the machine is right, nothing is broken. **A gate that goes permanently red on a correct
  state is the same disease as one that never fires.** It is now a named note that counts the
  affected docs — visible, not assertive. This walks back D1's claim in the plan; recording it here
  rather than quietly changing it.
- **`check_maps` AUTO-block drift is pre-existing on `main`, not this lane.** Verified from the main
  checkout itself (exit 1, correct `Sudo_Hatter_Command` label — so not the worktree false positive
  in `check-maps-stale-is-false-in-worktrees`). It arrived with SCC-73's merge at `50e357b`. Left for
  the close-out, from `main`, where regenerating cannot ship a lane name into the map.
