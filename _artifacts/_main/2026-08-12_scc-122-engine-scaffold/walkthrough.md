---
IsArtifact: true
ArtifactMetadata:
  title: SCC-122 walkthrough - engine scaffold
  type: walkthrough
  date: 2026-08-12
---

# SCC-122 — Engine scaffold walkthrough

Lane: `chore/SCC-122-engine-scaffold` · tree `.claude/worktrees/scc-122-engine-scaffold`
Ticket: SCC-122 (Subtask of SCC-116) · Plan: [implementation_plan.md](implementation_plan.md)
Landed: `4ce6948` — pushed to `origin/chore/SCC-122-engine-scaffold`

## Task Checklist

- [x] Lane opened: worktree + branch off `main` @ `0fcd093`; assets linked
- [x] Board moved to `In Progress`
  - `jira_feed.py start --key SCC-122` **refused with exit 2** — *"SCC-122 is a Subtask, start the
    parent it belongs to"* ([jira_feed.py:1070](../../../.agents/scripts/jira_feed.py#L1070)). The
    script's remedy was followed: the parent **SCC-116** carries the In Progress state. This is the
    board's design, not a workaround — subtasks are tracked through their parent.
- [x] Acceptance list fixed (6 checkable items) — plan §Acceptance
- [x] Plan written and self-audited → **Audit verdict: GO**
- [x] Operator approval received (literal `approved`)
- [x] RED written first and seen failing — `test_review_engine.py`, 79/80 failing, exit 1
  - The audit's F1 finding drove the design: every negative control proves the file EXISTS and is
    non-empty *before* asserting a token is absent. Proof it worked — at RED those rows read
    `file missing or empty` and **FAILED**, rather than passing on an absent file.
- [x] GREEN — the engine authored, 80/80, exit 0 at `4ce6948`
- [x] **Code review found the guard could not fail on content, and it was rebuilt**
  - Inverted stubs scored a clean 80/80 against the first version. Every rule is now pinned as a
    relationship (table row, anchored bullet) and ships a counter-example the check must reject.
    The engine markdown gained the fixes for eleven further findings — the severity axis was
    contradictory between two files, a recovered-inline lens was being scored as a dead one, three
    write targets were named but undeclared, and the skill was a live menu entry with prose-only
    containment. All 21 findings closed; see `## Code Review`.
- [x] Full floor on the landing code: `run_all.py` 17/17 files exit 0 · `workflow_lint
      --toolkit-only` 0 errors 0 warnings exit 0
- [x] Sync idempotency proven (a second `-NoGlobals` run changes only the manifest timestamp;
      hand-authored skill untouched) — not in the plan; added because a non-idempotent sync would
      break cache parity on the next operator's run
- [x] Committed with explicit paths, pushed
  - The push was refused once by the permission layer, then succeeded on the single retry.
- [x] Epic plan landed at its canonical path; main's untracked copy removed after byte-verification

## Evidence

**Final state, measured after the code review's fixes.** Every command was run **bare** — a piped
gate returns the pipe's exit code. The first-commit totals (80 rows) are superseded; the review
found the guard could not fail on content, and the table below is the rebuilt one.

| # | Acceptance item | Proving assertion | Result |
|---|---|---|---|
| 1 | Structure exists (SKILL.md + 4 steps) | 5 structure rows | PASS |
| 2 | Caller contract in SKILL.md | 12 pinned rows — each required input asserted as a `\| yes \|` table row, plus the menu-invocation guard — each with a counter-example | PASS |
| 3 | step-01 fan-out + failure contract + NA-vs-dead | 12 pinned rows incl. the 3-state end-state table (`ok` / `recovered-inline` / `dead`) | PASS |
| 4 | step-03 triage + severity machinery | 20 pinned rows incl. every mapping-table row asserted as a relationship | PASS |
| 5 | step-04 records only | 12 pinned rows + 5 boundary bullets asserted verbatim + 7 vendor-identifier bans × **every** `.md` in the engine (rglob, not a fixed list) | PASS |
| 6 | Registered + cache parity | INDEX caller-only row · INDEX master=cache · published · same file set · byte-identical | PASS |
| — | **the guard can fail** | 68 counter-example rejection proofs + the replayed stub attack | PASS |

**RED — before any step file existed** (`python3 test_review_engine.py`, exit **1**):

```
== review engine (SCC-122 scaffold) ==
[FAIL] SKILL.md exists with a body: .../.agents/skills/code-review-engine/SKILL.md
[FAIL] step-01-review.md exists with a body
...
[FAIL] SKILL.md carries no HALT marker: file missing or empty
[FAIL] steps/step-04-record.md carries no vendor review skill: file missing or empty
[FAIL] engine is published to the Claude cache
-- 1/80 passed --
```

The single row green at RED — *"skills INDEX master and cache are identical"* — was a true
precondition (both trees were already in sync), not a vacuous pass. Every other row failed **in its
assertion**, not in setup: the run completed and printed all 80 rows.

That first RED was honest but **weak**, and the code review proved why: all 78 failures had a
single cause — the files did not exist. Not one content assertion had been shown to reject
wrong-but-present content. The rebuilt guard replaces that with per-check discrimination proofs.

**GREEN — the rebuilt guard, on the code that lands** (exit **0**):

```
-- 233/233 passed --      (165 content + structure + ban + parity rows, 68 of them
                           counter-example proofs that each check rejects its own negation)
```

**The guard proven able to fail — three independent ways:**

```
1. the review's stub attack replayed (files present, instructing the opposite)  exit 1  (~120 red)
2. an extra file injected into the Claude cache  -> parity rejects it           exit 1
3. every check's counter-example applied in memory -> that check goes red       68/68
   restored, unmutated                                                          exit 0  233/233
```

**The floor, on the landing code, run bare:**

```
python3 .agents/scripts/tests/run_all.py            -> 17/17 files passed        exit 0
python3 .agents/scripts/workflow_lint.py --toolkit-only
                                                    -> 0 error(s), 0 warning(s), 8 info   exit 0
python3 -m py_compile .agents/scripts/tests/test_review_engine.py                exit 0
```

**SOP currency — run for real, and proven non-vacuous:**

```
sop_currency.py --paths <the 16 changed files> --message "<the commit subject>"   exit 0
sop_currency.py --paths .agents/commands/smh-code-review.md ...                   exit 1
    x The SOP quick-reference was not updated with this change.
```

The diff earns no SOP edit: `.agents/skills/` is not a surface, and `.agents/scripts/tests/` plus
`INDEX.md` are explicitly exempt ([sop_currency.py:81-82](../../../.agents/scripts/sop_currency.py#L81)).
The control run proves the gate still refuses a genuine surface change, so exit 0 above means
"nothing an operator types changed", not "the gate is asleep".

**Link + anchor:** 14 markdown files in the diff · 24 bare-path instructions resolved (the step
files' `./step-0N-*.md` NEXT pointers and every `.agents/…` reference) · **0 broken**.

**Added-line scan:** no secrets, no debug output, no commented-out code, no bare `except`, no
absolute or `C:/` paths, no `TODO`/`FIXME`. The eight `token` matches are the English word in prose.

## Code Review (2026-08-12)

Verdict: PASS @ <PENDING-SHA>
Suite evidence measured at the same sha: `run_all.py` 17/17 files exit 0 · `workflow_lint
--toolkit-only` 0 errors 0 warnings exit 0 · `test_review_engine.py` 233/233 exit 0.

**Scope** — the 16-file diff `main...HEAD` plus the review fixes below (engine markdown, its cache
copy, the guard test, both INDEX files, the sync manifest, two artifact plans).
**Method** — clean-room adversarial lens in a subagent with no conversation context (diff first,
plan only afterwards), acceptance audit against the plan's 6-item checkable list, the
command-centre gate, and the clean-code gate. **One lens, ran clean, no degradation.**

### ⛔ The review's headline finding, and why the first commit was not shippable

The adversarial lens broke the new guard in one move. It replaced all five engine markdown files
with keyword-stuffed stubs instructing the **opposite** of every rule — *"skip Blind Hunter"*,
*"do not retry, do not go inline"*, *"Drop every finding… Flip the story to Done and merge"* — and
`test_review_engine.py` reported a clean **80/80**.

That is the house's own `tests-must-gate-for-real` failure: **a check that cannot fail is a
finding**, and this check was the *only* mechanical guard on the surface. The RED at `4ce6948` was
real but proved only *"files absent → red"*; not one content assertion had ever been shown to
reject wrong-but-present content. The plan's own audit predicted this hazard (finding F2,
"source-greps count prose") and then applied the defence to the five negative controls only,
leaving ~35 positive checks wide open to it.

**The repair, in three parts:**

1. **Checks bind a relationship, not a vocabulary.** `critical` and `FAIL` both appearing somewhere
   proves nothing; `^| `critical`, in … | **FAIL** |` proves the mapping, because the table row is
   where the meaning lives.
2. **Every check ships a counter-example and is proven to reject it.** 68 rows of the suite are now
   discrimination proofs: each rule's negation is applied in memory and the check must go red — and
   the counter-example must actually apply, so the proof can never be vacuous.
3. **Prohibitions are asserted positively.** Banning behaviour words fails in a file whose job is to
   forbid them ("it never merges" contains "merges"), so step-04's boundary is held by requiring its
   five bullets verbatim. A stub saying "flip the story to Done and merge" cannot also carry
   *"It never advances a story's state"*.

**Re-proof:** the exact stub attack was replayed against the rebuilt guard — **exit 1**, ~120 red
rows — and the restored engine returns **233/233 exit 0**.

### Findings

| # | file:line | Severity | Finding | Disposition |
|---|---|---|---|---|
| C-1 | test_review_engine.py:64-155 | critical | Inverted stubs scored 80/80 — the guard could not fail on content | **applied** — rebuilt around pinned relationships |
| C-2 | test_review_engine.py:75-118 | critical | ~35 positive checks were unordered, unattributed keyword greps; 12 verified to pass against their own negation | **applied** — line-anchored patterns + 68 counter-example proofs |
| C-3 | test_review_engine.py:121 | critical | Ban scan iterated a hard-coded 5-name list; a `step-05` carrying every banned token passed | **applied** — scans `MASTER.rglob("*.md")`, asserts coverage ⊇ known files |
| I-1 / I-7 | BANNED map | important | Bans encoded the vendor's *identifiers*, not the forbidden *behaviour* — "set the story's Status to Done" passed all seven | **applied** — five boundary bullets asserted verbatim, positively |
| I-2 | SKILL.md:57 vs step-03:76 | important | Severity axis inverted between the two files; "never above the floor" forbade a caller escalating to FAIL | **applied** — axis stated once (`none` < `CONCERNS` < `FAIL`), "above/below" removed, cap-vs-floor equivalence spelled out |
| I-3 | step-03:62 vs :78 | important | §4 dropped dismissals, §5 said both are recorded, step-04 implemented neither | **applied** — decided: `dismiss` counted, `defer` recorded; step-04 matches |
| I-4 | step-03:74 | important | Dead-lens row capped a review that had been fully recovered inline | **applied** — row now reads "still `dead` after retry AND inline rerun"; a 3-state table added to step-01 |
| I-5 | step-01:37, step-04:7,20 | important | Three write targets named but undeclared, while SKILL.md forbids deriving inputs — the engine could only stop | **applied** — `FINDINGS_SINK`/`ARTIFACT_DIR`/`DEFERRED_WORK` added as optional inputs with an explicit absent-input rule |
| I-6 | step-03:71 | important | Plan said "*confirmed* critical→FAIL"; build dropped "confirmed", so unverified assertions could FAIL | **applied** — decided and documented: scaffold stage gates exactly as hard as the path it replaces, so SCC-124 measures real behaviour |
| I-8 | plan:82 | important | Red-first proved wiring, not discrimination — all 78 reds had one cause | **applied** — per-check counter-examples are now the red-first evidence |
| I-9 | SKILL.md | important | Skill is a live menu entry on Claude and Codex; "not standalone" was prose only | **applied** — first-instruction guard refuses menu invocation and returns; asserted |
| S-1 | test:46 | suggestion | `\bHALT\b` under `re.I` banned the English word "halt" | **applied** — that pattern is now case-sensitive |
| S-4 | SKILL.md:4 | suggestion | `allowed-tools` granted `Bash`+`Edit` — merge/push/in-place-fix — contradicting the declared boundary | **applied** — narrowed to `Read, Write, Glob, Grep, Task`, asserted |
| S-5 | SKILL.md:47 | suggestion | `<n>/<total>` made a spec-less review read as degraded (3/4) | **applied** — `<n>/<applicable>` + a separate `lenses_na` line |
| S-6 | step-04:17 | suggestion | Deferred findings rendered as a ticked box — unresolved work shown as done | **applied** — unchecked, asserted |
| S-7 | step-02:7 | suggestion | Self-gating rules governed machinery that does not exist yet | **applied** — moved into a marked "when SCC-127 lands" block |
| S-2, S-3 | test:58,77 | suggestion | 200-char body floor trivially cleared; `\bfull\b` missing `re.I` and matching ordinary prose | **applied** — superseded by structural checks; mode row now asserts both modes in one pinned row |
| N-1 | test:68,147 | nitpick | Detail strings on the wrong checks; "missing" printed for a short file | **applied** |
| N-2 | test:134 | nitpick | INDEX check was a bare substring — a row saying "RETIRED" would pass | **applied** — requires the caller-only clause |
| N-3 | plan:107 | nitpick | `.sync-manifest.json` sat outside the plan's stated surgical boundary | **applied** — boundary amended |

Reviewer-verified clean, recorded because it is evidence: the negative controls' anti-vacuity design
(a deleted step file fails its bans rather than satisfying them) · master↔cache duplication is the
right call and the parity check is sound in every direction · the alias map matches the plan exactly
· the vendor skill is untouched · `run_all` auto-discovery claim accurate · the predicted untracked
merge collision was in fact avoided.

### Acceptance audit

| Item | Where the diff satisfies it | Proving assertion |
|---|---|---|
| 1 structure | 5 engine files | 5 structure rows |
| 2 caller contract | SKILL.md contract table | 12 pinned rows (each required input as a `\| yes \|` row) + counter-examples |
| 3 fan-out + failure contract + NA-vs-dead | step-01 | 12 pinned rows incl. the 3-state end-state table |
| 4 triage + severity | step-03 | 20 pinned rows incl. the full mapping table |
| 5 records only | step-04 + bans | 12 pinned rows + 5 boundary bullets + 7 bans × every engine `.md` |
| 6 registered + parity | INDEX both trees, cache | 5 rows; parity proven able to fail by injection |

**Beyond the list:** `.sync-manifest.json` (generated by the required sync — boundary amended per
N-3) and the SCC-116 epic plan (landing hygiene, declared in the plan's design decisions). Nothing
else. No drift.

### Clean-Code Gate — PASS

```
run_all.py     : PASS  17/17 files, exit 0
workflow_lint  : PASS  0 error(s), 0 warning(s), 8 info, exit 0
sop_currency   : PASS  exit 0 on the changed set; exit 1 on a control surface path (non-vacuous)
py_compile     : PASS  test_review_engine.py, exit 0
link + anchor  : PASS  24 bare-path instructions + 9 refs re-swept after the rewrite, 0 broken
door parity    : n/a   no command added, renamed or deleted; no stray opencode/antigravity door
lint / types   : not applicable to this repo (no venv, no ruff, no tsc)
```

Added-line scan: no secrets, no debug output, no commented-out code, no bare `except`, no absolute
or `C:/` paths, no unowned TODO. Comment contract: the test's docstring carries SCC-122 provenance
and the reasoning for its shape.

### Step 0.7 — blast radius re-derived against current `main`

1. **Nothing moved.** `main` is still at `0fcd093`, the merge-base — zero files landed while this
   was built, so every path and skill reference the diff names still resolves. Re-verified anyway:
   both lens skills exist on disk.
2. **True overlap: none.** `git merge-tree --write-tree` writes a clean tree with no conflict
   messages. `origin/main` == local `main`, so there is nothing to absorb.
3. **Sibling lanes: none live** — `git worktree list` shows only `main` and this lane. No
   landing-order dependency.
