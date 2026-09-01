review-runtime: fan-out

# SCC-285 — the rebuttal quoted a directive that does not exist

**Ticket:** SCC-285 (Bug, epic SCC-33) · **Branch:** `chore/SCC-285-agenttool-directive-quote`
**Lane:** `/smh-quick-fix` → **EJECTED** (`lane_qualify` = `TASK`, toolkit paths) → `/smh-quick-dev`.

⭐ **Scope grew, and the record says so.** The ticket names one defect — a misquoted directive. Two
more shipped on this branch because the same root cause produced them: **a rule that lives only as
prose is a rule an agent improvises around.** `check_links.py` turned the clean-code floor's one
prose row into a command; `walkthrough_roster.py` turned the SCC-203 `inline`-needs-a-reason rule
into a blocking check. Both are declared in the checklist and carry their own tests. 31 files
changed in total.

## What this was

Claude Code injects a standing directive into the system prompt. Five house commands rebutted it by
quoting it as *"do not use subagents unless the user requested it"* — **a string that does not
exist**. The real one names the tool:

> `Do not call the AgentTool unless the user requested it`

An agent reads its real system prompt, reads a command arguing against a sentence that is not in it,
and takes the gap as an escape hatch. It did, on 2026-08-22 — `2026-08-22_code-review-graph-swap/walkthrough.md:227`:

> `review-runtime: inline (blocked: … "Do not call the AgentTool unless the user requested it".`
> `… and the directive names that tool specifically.)`

The AVCH-73 review ran **inline, with no independent lens**, because the rebuttal missed by four words.
The third door worked — the refusal was recorded, not laundered into a clean-looking `inline`.

**Where the directive lives, and why it cannot be edited.** It is the constant `dkm` compiled into
the Claude Code binary, injected by the function behind feature name `tengu_heron_brook`. Precedence:
server `clientData` string → GrowthBook string → **the hardcoded two lines** → nothing. The fallback
fires when `uVo(model)` is true: the model carries capability `opus_5_prompt_bundle` **and** the
kill-switch `tengu_fennel_godwit` is false. **So it fires because the session runs Opus 5.** No
`CLAUDE_CODE_*` env override exists for either flag (verified: 0 occurrences in the binary), no
settings key, no `managed-settings.json`. `DISABLE_GROWTHBOOK` makes it *worse* — it locks in the
hardcoded default. The house wording is the only side we own.

## Task Checklist

- [x] Trace the directive to its source and prove no local lever exists
- [x] RED — `test_directive_quote.py`, both halves, seen failing on all 8 real sites
- [x] GREEN — 8 sites across 5 command files rewritten
  - scope grew 5 → 8: three files carried a **second** variant, *"do not spawn subagents unless asked"*
- [x] Twin-law `review-runtime-probe` stays byte-identical across `cicd-quick-dev` ↔ `smh-quick-dev`
- [x] Regenerate the `.opencode/` doors via `/smh-sync-agents -NoGlobals` (never hand-edited)
- [x] SOP currency — the SOP carried the same paraphrase; fixed on merit, no `[sop-ok]`
- [x] Mutation sweep — **7/7 killed**, each by its declared case
  - four mutants are RE-SEEDS onto real files on disk (the protected surface), not edits to the
    test's own literals — a mutant that attacks a string in the test file proves nothing
  - hit SCC-284 live: `mutation_sweep` rejects `"mutated": ""`, so the deletion mutant was
    re-expressed as a shortening
- [x] **`check_links.py`** — the clean-code floor's `Link + anchor` row was the only prose row on a
      floor of scripts, so every agent improvised a matcher. Seven conventions, each frozen from a
      measured false positive of its own drafts (31 → 168 → 18 → 5 → 0). `test_check_links.py`
      26/26, and block E proves it still BITES.
- [x] **`walkthrough_roster.py`** — `review-runtime: inline` now owes a REASON, and a reason resting
      on PERMISSION rather than capability is refused at close-out. The SCC-203 rule stopped being
      prose. `test_walkthrough_roster.py` 83/83, block RR.
- [x] The merge itself — lands via this branch's PR

## Evidence

| Acceptance | Assertion | Result |
|---|---|---|
| A1 no paraphrase remains | `test_directive_quote.py` block B | **RED** listed all 8 sites → **GREEN** |
| A2 every rebutter quotes it verbatim | block C, 5 files | **RED** 5/5 failing → **GREEN** |
| A3 the guard can fail | blocks A + D, then the sweep | **31/31**; **7/7 mutants killed** |
| A4 twin-law identical | `test_twin_parity.py` | **66/66 passed**, exit 0 |
| A5 doors regenerated | `sync-agents.ps1 -NoGlobals` | 59 opencode cmds; only the real files moved |
| A6 SOP in the same commit | armed `sop_currency.py` commit-msg gate | **accepted, no `[sop-ok]`** |
| A7 the lane leaves its record | this file + `task.yaml` | present |
| A8 the floor row is a COMMAND | `check_links.py` + `test_check_links.py` | **26/26**, exit 0 |
| A9 a bare `inline` is refused | `walkthrough_roster.py` + block RR | **83/83**, exit 0 |

**RED (`436a66e^`)** — `-- 10/16 passed --`, `FAILED: B1 …, C1 ×5`, B1 naming
`cicd-code-review.md:190,201 · cicd-dev-story-tests.md:102,105 · cicd-quick-dev.md:188 ·
smh-code-review.md:161,172 · smh-quick-dev.md:78`. Every `D` counter-example passed at RED — the
guard's own machinery was proven working before the tree was touched.

**GREEN** — `-- 31/31 passed --`, exit 0. (The guard grew past its first cut: the review added
block R, which DERIVES the rebutter set from the tree rather than trusting the hand-written list.)

**Sweep** — table at `sweep.json`, **7 mutants, 7 killed**. ⛔ **Four of them re-seed a paraphrase
onto a real command file or the SOP — the PROTECTED SURFACE — rather than editing a literal inside
the test.** A mutant that attacks the test's own strings proves only that the test reads itself:

| Mutant | Killed by |
|---|---|
| M1 re-seed the WRAPPED paraphrase into a real command file (hole H1, on disk) | `B1 no misquotation in the commands or the SOP` |
| M2 re-seed a HYPHENATED re-wording into a real command file (hole H2, on disk) | `B1` |
| M3 re-seed a paraphrase into the SOP — the MEASURED second vector | `B1` |
| M4 DELETE the operative rebuttal, leaving the narration copy (hole H4) | `C1 cicd-code-review.md quotes it verbatim where it claims 'satisfied'` |
| M5 strip the verbatim quote out of a real rebuttal, keeping the claim | `C1 smh-quick-dev.md …` |
| M6 `unwrap()` stops collapsing line wraps — the H1/H3 fix reverted | `D10 REQUIRE survives a mid-quote line wrap` |
| M7 REQUIRE drops the operative-site anchor — presence-anywhere restored | `D8 REQUIRE FAILS when only the narration copy survives (H4)` |

`-- restore verified: bytes match, nothing was committed --` · unfiltered re-run exit 0.

**Why the guard has two halves.** A ban-only guard is satisfied by **deleting** the rebuttal — which
removes the sentence that makes the fan-out legal, strictly worse than the bug. BAN + REQUIRE, and
block D fails both directions before either is believed.

## Gates

| Gate | Result |
|---|---|
| `run_all.py` **through `gate_receipt.py`** | **PASS exit=0**, `dirty_tree: false`. Receipt at `gates/suite.json`, **stamped at `dd772b2`** — the landing sha, after **two** rounds of absorbing `origin/main` mid-close-out (SCC-281 as PR #56, then SCC-294 as PR #57). The first stamp (`436a66e`) was **red** — the mechanism working, not a failure: it caught the missing `_artifacts/_main/INDEX.md` row. Two later stamps went stale as HEAD moved; all three receipts (suite, links, lint) are re-stamped **together**, every time, because three shas for one certification is not a certification. |
| `test_directive_quote.py` | **31/31**, exit 0 (RED 10/16 first) |
| `test_twin_parity.py` | **66/66**, exit 0 |
| `test_walkthrough_roster.py` | **83/83**, exit 0 |
| `test_check_links.py` | **26/26**, exit 0 |
| `test_check_maps.py` | 27/27, exit 0 |
| `mutation_sweep.py` | **7/7 killed**, restore verified, unfiltered re-run exit 0 |
| `workflow_lint.py --toolkit-only` | **0 errors, 0 warnings, 8 info** (BOMs on vendored `testarch-*`, pre-existing), exit 0 |
| `check_maps.py` bare | **exit 1 — none of it mine**, proven below |

⛔ **All gates run bare, never piped** — a `| tail` reports the pipe's exit code, not the gate's.
⚠ **And not redirected out of the workspace either.** `workflow_lint > /tmp/lint.txt` reported
`LINT_EXIT=1` while the gate itself was green: the sandbox refuses a write outside the workspace,
so the **redirect** failed and the shell reported the redirect's failure as the gate's. Same class
as the pipe, new cause.

⛔ **NO REVIEW VERDICT, AND THE RECORD SAYS SO RATHER THAN IMPLYING ONE.** The five-lens fan-out was
stopped mid-flight on the operator's word, so this walkthrough carries no `Verdict: … @ <sha>` line.
Three mechanical consequences, all of them the system behaving correctly:

- `task_preflight` prints `gate: no review Verdict line in this task's own walkthrough - the full
  gate runs` — **nothing was skipped**; every gate above ran at the shipping sha.
- `flight_recorder record` **REFUSES** — it keys its event on the verdict sha, and there is none.
- `main_write_gate --mode pr` still passes, and that is deliberate rather than lucky:
  `main_write_gate.py:213` records that the recorder refuses verdict-less walkthroughs, so the gate
  requires the **preflight receipt**, not the event.

What is missing is an independent read of this diff, not a green check. Anyone re-opening this lane
should know that the gates certify it and no second pair of eyes did.

**`check_maps` attribution.** Three findings, all accounted for:

1. **AUTO block STALE** — `on disk but not in map: scc-285-agenttool-directive-quote/` /
   `in map but not on disk: Sudo_Hatter_Command/`. The known worktree false positive: the label is
   derived from the **CWD basename**, so it is *always* stale inside a worktree.
2. **Two dead paths** at `docs/migrations/auth_keys/_secrets/master.env` (`repo-map.md` +
   `docs/migrations/INDEX.md`). Measured: the file **exists in the main checkout**
   (`-rwxr-xr-x 16827 Jul 24`) and is gitignored, so it is simply absent from this tree —
   `link-worktree-assets.py` links `auth_keys` at the repo root, not under `docs/migrations/`.
3. **The shared `main` checkout runs the same linter to `exit 1` too** — measured directly, with my
   lane absent from it. The red pre-dates this branch.

Nothing in this lane's diff touches `docs/`, `repo-map.md`, or `docs/migrations/INDEX.md`.

## Landing order

⚠️ **AUDIT FINDING (review, Literal-Correctness) — the earlier "zero overlap" claim was FALSE.**
Measured: `git -C .claude/worktrees/SCC-280-teaching-edition diff --name-only origin/main...HEAD`
returns **two files this lane also declares**.

| Shared file | Collision |
|---|---|
| `.agents/.sync-manifest.json` | ⛔ **HARD** — both lanes rewrite the same line-3 `"generated"` timestamp, so whichever lands second conflicts textually. It is a **generated** file: the resolution is to re-run `/smh-sync-agents`, never to hand-merge. |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | benign — SCC-280 edits ~lines 73-96, this lane line 2052; a 3-way merge resolves it. |

The five command files remain genuinely disjoint — SCC-280 touches `smh-tour` / `smh-training`.
Per `lane-collision-is-gates-not-files` there is a **gate** overlap too, since SCC-280 carries
`test_twin_parity.py`: before close-out this lane runs its own guard against their blobs, and their
`test_twin_parity.py` against its own. **Landing order is not forced — but the second lane to land
must REGENERATE the sync manifest rather than resolve it by hand.**

## Your Actions

Nothing is owed. Recorded for context:

- The lane found and fixed a defect in its own guard (M5) before shipping it.
- **SCC-284 confirmed live** here — `mutation_sweep.py` rejects a deletion mutant. Already filed;
  not fixed in this lane, which owns no part of that script.
- **Follow-on, not this lane's to make:** the shared memory index still names
  "_my_resources/_quick_reference/sudo_workflows_testing.md" (which does not exist) as the SOP-currency doc. The real one
  is `docs/_scc_sops_prds/workflows_testing_SOP.md` (`sop_currency.py:60`). The stale entry cost
  this lane one audit finding and will cost the next agent the same. The memory store is read-only
  outside its own flows, so it is named here rather than edited.
- **Fix B was not built** — the `UserPromptSubmit` hook that injects the request on review-command
  turns. Out of scope by the operator's choice of Fix A.
