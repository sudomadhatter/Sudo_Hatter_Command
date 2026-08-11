# SCC-83 — Remediation plan (round 2)

**Why this exists:** `/smh-code-review` returned **FAIL @ `6cdca82`**. Four HIGH findings, one of
which is that the gate this ticket shipped **does not gate** — its primary detection arm never
executes in any checkout that exists. Full verdict in `walkthrough.md` § *Code Review (2026-08-11)*.

**Everything below is measured, not reasoned.** The reason round 1 failed is that I verified a
program I had not committed; every design choice here is preceded by the probe that decided it, and
the numbers are quoted inline so a reviewer can re-run them.

---

## ⭐ The reframe: four HIGHs, one root cause

H1, H3, and half of M3 are not independent bugs. They are three symptoms of one property:

> **The checker's answer depended on where you were standing.**

`Projects/*` are separate, gitignored repos. A `git worktree` does not carry gitignored content, so
every lane sees them as **empty stubs** while `main` sees them populated. Round 1 accepted that as a
fact of life and built machinery to cope with it — a `strict` mode to suppress the unprovable, and an
`rglob` that searched the whole tree to recover what the suppression lost. Both were coping
mechanisms, and both failed in the way coping mechanisms do:

| Coping mechanism | What it actually did |
|---|---|
| `strict=not stubbed` | 9 stubs in a lane, **1 in `main`** (an uninitialised submodule) → `False` **everywhere** → the primary arm is dead code (**H1**) |
| `rglob` to recover coverage | +18.3s per `run_all`, and it descended into `.claude/worktrees/` and **cited a sibling lane's copy as the fix target** (**H3**) |

**Fix the standing-point and both mechanisms become unnecessary.** A worktree's `.git` file names
the main checkout — `git rev-parse --git-common-dir` → `/Users/sudohatter/Sudo_Hatter_Command/.git`,
whose parent holds the populated `Projects/`. **Verified: it resolves, and `Projects/` is there.**
This is the same cure as the repo-map label bug already recorded in memory
(`check-maps-stale-is-false-in-worktrees`) — a tool that asks *CWD* what repo it is in gets a
different answer per lane; one that asks *git* gets the same answer everywhere.

### Measured effect

| Configuration | shipped (`strict=False`) | `strict=True` | **after D1** |
|---|---|---|---|
| Worktree (9 stubs) | 0 findings | 14 findings | **1** |
| `main` model (8 populated) | 0 findings | 1 finding | **1** |

The two rows agreeing **is the deliverable.** That equality is the property whose absence let H1
hide: round 1's two "independent confirmations" were the same weak-mode run twice, and nothing
compared a lane's answer to `main`'s.

And the surviving finding is real: 13 of the 14 are AGY-owned (`_bmad-output/…`, `_bmad/bmm/…`) and
resolve once the projects are visible. **One does not — `_artifacts/opencode/`** — and it turns out
to be the same class as the regression I shipped. See D5.

---

## D1 — Resolve project roots from git, not from CWD  *(H1, M3, L6)*

**Change.** `_scan_roots()` derives the main checkout from `git rev-parse --git-common-dir` and reads
`Projects/` there. `ROOT` stays CWD-based (the docs under audit are the ones in *this* tree — that is
correct and must not change); only the *project* roots move.

**Delete the `strict` parameter entirely.** Not "make it per-token" as the review proposed — once
coverage no longer varies by lane there is no mode to switch. A mode driven by untracked state (one
stray `.DS_Store` in a stub flips an entire run) is the defect; a per-token version of it would be a
smaller defect of the same kind.

**The residual stub is handled per-token by code that already exists.** `Fresh_Workspace_BMAD` is an
uninitialised submodule in *both* checkouts, so it is not a lane artefact — it is genuinely absent on
this machine. `_is_stub_project()` already skips explicit `Projects/<stub>/…` tokens, which is the
only form a stubbed project can own. Bare tokens are lobby-relative claims and stay checkable.

**Degraded mode must be able to fail.** A fresh clone on the PC may have no `Projects/` at all
(memory: `two-machines-mac-and-pc`). Today that path prints a coverage note through `c.check(…, True)`
— a print dressed as a passing check (**L5**). Replace it with a **real** check: if any doc references
the interior of a project that is not checked out, that is a FAIL, not a note. Reduced coverage then
cannot hide a defect, and the check count stops being inflated.

**L6** rides along: `_scan_roots()` currently evaluates `any(d.iterdir())` twice per entry and returns
a list mixing `Path` and `str`. One evaluation, two homogeneous lists.

---

## D2 — One pruned index, built once  *(H3, L4)*

**Change.** Replace per-token `r.rglob(leaf)` with a single pruned `os.walk` per root, built once per
run, yielding exact-case `paths: set[str]`, `leaves: dict[str, str]`, and `heads: set[str]`.
Resolution becomes set membership — no filesystem call per token.

**Measured:** 9 roots, 20,447 entries → **0.12 s**, 10,793 paths, 4,390 leaves. Against **+18.3 s**
for the `rglob` it replaces.

Prune set: `.git`, `node_modules`, `.venv`, `venv`, `__pycache__`, `dist`, `build`, `.next`,
`.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.turbo`, `coverage`, **`worktrees`**.

Two things fall out for free:

- **The sibling-lane citation cannot recur.** `worktrees` is pruned — **verified: no
  `.claude/worktrees/` path leaks into the index.**
- **L4 is fixed structurally.** macOS is case-insensitive, so `(r / "DOCS/foo.md").exists()` is
  `True` today and a wrong-case path passes silently. Exact-case set membership cannot do that. This
  is the fix a case-check bolted onto `Path.exists()` would only have approximated.

---

## D3 — Strikethrough stops at the end of its line  *(H2)*

**Change.** `STRUCK` becomes `~~[^~\n]*~~`, applied **per line** rather than to the whole document.

Today `~~[^~]*~~` spans newlines and runs over the file before tokenizing, so one unbalanced `~~`
plus any later strikethrough blanks everything between them — **a whole-file off-switch reachable by
a typo**, in the gate written to stop silent misses. A `~~~` fence is eaten whole.

**Measured:** the folder is balanced today — `file_folder_structure+maintaining.md` has 2
occurrences, `sentry_error_response_team.md` has 8, both even, no `~~~` fences. **So this is latent,
not live.** Worth saying plainly: no current finding is being suppressed by it. It ships anyway
because the failure mode is silent and the trigger is a typo.

**Controls:** an unbalanced `~~` with a live dead path several lines below (must still fire); a
`~~~` fence (must not swallow); the existing per-token control stays.

---

## D4 — Cut the dead alternations and stop claiming coverage that does not exist  *(H4)*

The review's headline: deleting `NOT_A_PATH` entirely leaves the suite **34/34 PASS**. The control
written to make it falsifiable controls nothing, and the module comment — *"Every class below has a
control"* — is false.

**Measured which alternations can ever fire**, against the lobby plus all 8 populated projects:

| Class | Verdict |
|---|---|
| `origin\|upstream\|epic\|chore\|claude\|story\|incident\|main\|HEAD` | **dead** — no such directory exists in any root, so the first-segment rule kills these first |
| `openrouter\|anthropics\|google\|openai` | **dead** — same |
| `^@` (npm scopes) | **dead** — same |
| `^/(api\|ws\|v\d)/` | **unreachable** — `PATH_LIKE` requires a leading word char |
| `[*?\[\]]` (globs) | **unreachable** — those chars are not in `PATH_LIKE`'s class |
| `\s` (prose) | **unreachable** — same |
| `\.\.\.` (ellipsis) | **LIVE** — `docs/...` matches `PATH_LIKE` and `docs/` exists |

**Change.** Delete the six dead alternations; keep `\.\.\.`. Rewrite the comment to name the two
filters that actually do the work — `PATH_LIKE`'s character class and the first-segment rule — since
that is what a maintainer needs to know.

**Controls, built so a mutation is visible:** the retained class gets a fixture root where its head
*does* exist, so `NOT_A_PATH` is the only thing that can kill it — delete the alternation and the
fixture goes red. A second fixture pins the *reason* the deleted classes stay silent (`PATH_LIKE` /
first-segment), so removing them cannot silently widen the net later.

This is the "no skeletons" call applied to my own code: six alternations that look like
defence-in-depth and are decoration, plus a comment asserting coverage that was never there.

---

## D5 — Prospective paths need a class  *(M2 + the one real finding)*

The review flagged M2 as a regression I introduced — I took the detector's first `rglob` hit as a
remediation instruction and rewrote `tea_testing_guide.md`'s options A and B to **identical** paths
while line 603 still reads *"Option A changes every project."* That is live on the branch and wrong.

Reading the surviving real finding shows it is **the same class**, not a coincidence:

```
file_folder_structure+maintaining.md:174
  - opencode → the same rules, inside an `_artifacts/opencode/` namespace created on first use
```

Both are **create-me** paths — correct sentences about files that do not exist *yet*, by design.
`ABSENT_BY_DESIGN` had no class for them, so the only way to make the checker quiet was to make the
doc wrong. **That is the inversion the allow-list exists to prevent, and it caught me.**

**Change.**
1. **Revert M2** — restore `.agents/rules/testing-standards.md` (option A, lobby) and
   `Projects/AGY_AVIATIONCHAT/.agents/rules/testing-standards.md` (option B, project-local), so the
   two options differ again and line 603 is true. *(The third hunk in that file — the `cicd-` →
   `sudo-` historic-artifact revert — is correct and stays.)*
2. Extend the allow-list to carry a **prospective** class, one written reason per entry, covering
   those two paths and `_artifacts/opencode/`. The existing narrowness fixture (a non-listed sibling
   in the same directory must still fire) already covers it against becoming a blanket off-switch.
3. **L2** rides along: keys are compared as exact strings today, so `docs/x/` and `docs/x` behave
   differently. Normalise the trailing slash on both sides.

---

## D6 — The remaining findings

| # | Change |
|---|---|
| **M1** | The MOVED-vs-gone fixture's ternary evaluates to literal `True`, so the one working arm has **zero** coverage. Assert the set *and* the reason string; use `det()` so it stops printing detail on PASS. |
| **M4** | Two false claims shipped in `INDEX.md`. *"exactly 2 non-backticked tokens"* — **measured: 242**, of which the overwhelming majority are prose slashes (`Dev/QA`, `and/or`, `PASS/CONCERNS/FAIL`, `7/7`). *"fenced blocks"* is impossible — `CODE_SPAN` requires backticks. Replace both with the honest justification, which is stronger than the fake count: widening the net to non-backticked tokens trades a handful of real checks for hundreds of false ones, so the backtick convention **is** the boundary. Also replace the "25 from a lane vs 12 from main" note — D1 makes it **1 and 1**. |
| **M5** | The A3c control asserts on a token killed by the first-segment rule, not by `_is_stub_project` (which only handles `Projects/<name>/…`, so the implicit form can never reach it). The `mkdir` is inert and the comment claims otherwise. Relabel A3c as the first-segment control it is; A3c-bis remains the real `_is_stub_project` control. |
| **L1** | Two adjacent string literals in `unresolved_paths` — the second is a dead expression, not a docstring. Merge into one. |
| **L3** | Windows-separator paths (`docs\foo.md`) fail `PATH_LIKE` and are skipped in silence. This repo is read on **two machines** (memory: `two-machines-mac-and-pc`). Normalise `\` → `/` before matching so they are checked rather than ignored. |
| **L5** | Folded into D1 — the coverage note becomes a real check. |
| **L6** | Folded into D1. |

---

## Acceptance — round 2

Round 1's acceptance list was satisfiable by a gate that did nothing. These are written so that
cannot happen again.

| # | Criterion | How it is proven |
|---|---|---|
| **B1** | ⭐ **Same answer from a lane and from `main`.** | T9 run against both root-sets prints an identical finding set. This is the check whose absence hid H1. |
| **B2** | No mode switch remains. | `strict` is gone from the signature and the call site; `grep` proves it. |
| **B3** | The primary arm executes. | The real run reports `_artifacts/opencode/` before D5's allow-list entry lands, and is silent after — the arm demonstrably fires and demonstrably stops. |
| **B4** | Mutation-visible fixtures. | Deleting `NOT_A_PATH`, the `moved ->` arm, or the retained alternation each turns the suite **red**. Verified by actually deleting each and re-running. |
| **B5** | H2 cannot blank a file. | Unbalanced `~~` and `~~~` fence fixtures. |
| **B6** | Index is pruned and fast. | No `.claude/worktrees/` path in the index; `run_all` wall-clock recorded before and after. |
| **B7** | M2 reverted. | Options A and B carry distinct paths; line 603 is true again. |
| **B8** | Gates green. | `run_all` exit 0, `workflow_lint --toolkit-only` **0 errors 0 warnings**, `sop_currency` exit 0, `task_preflight` clear. |
| **B9** | No claim in `INDEX.md` that is not measured. | Every number in the new text traceable to a probe in this plan. |

**B4 is the one that matters.** Round 1's fixtures were green against code that did nothing; the
only way to know a fixture controls something is to break the thing and watch it go red.

---

## Landing order

`chore/SCC-73-memory-relocation` committed mid-review and **conflicts** with this lane on
`_artifacts/_main/INDEX.md` — both add a row at the table head (confirmed by `merge-tree`, not
predicted). Trivial: keep both rows. Whoever lands second merges `main` down first; if SCC-73 lands
before this, I merge down and re-run the gates before close-out.
`chore/SCC-77-main-write-gate`: no overlap.

## Out of scope (unchanged, still owed)

Ticket the repo-map generator's CWD-derived label (same root cause as D1, different script) ·
`tea_testing_guide.md` residency is an AVCH architecture call · AGY's stale `sudo_workflows_testing.md`
is an AVCH ticket.
