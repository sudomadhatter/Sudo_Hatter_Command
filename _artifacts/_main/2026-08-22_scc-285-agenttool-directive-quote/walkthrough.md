review-runtime: fan-out

# SCC-285 — the rebuttal quoted a directive that does not exist

**Ticket:** SCC-285 (Bug, epic SCC-33) · **Branch:** `chore/SCC-285-agenttool-directive-quote`
**Lane:** `/smh-quick-fix` → **EJECTED** (`lane_qualify` = `TASK`, toolkit paths) → `/smh-quick-dev`.

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
- [x] Mutation sweep — 5/5 killed, each by its declared case
  - the sweep found a hole in the guard itself (M5) **before** it shipped; A4 was added for it
  - hit SCC-284 live: `mutation_sweep` rejects `"mutated": ""`, so the deletion mutant was
    re-expressed as a shortening

## Evidence

| Acceptance | Assertion | Result |
|---|---|---|
| A1 no paraphrase remains | `test_directive_quote.py` block B | **RED** listed all 8 sites → **GREEN** |
| A2 every rebutter quotes it verbatim | block C, 5 files | **RED** 5/5 failing → **GREEN** |
| A3 the guard can fail | blocks A + D, then the sweep | 17/17; **5/5 mutants killed** |
| A4 twin-law identical | `test_twin_parity.py` | **65/65 passed**, exit 0 |
| A5 doors regenerated | `sync-agents.ps1 -NoGlobals` | 59 opencode cmds; only the 5 real files moved |
| A6 SOP in the same commit | armed `sop_currency.py` commit-msg gate | **accepted, no `[sop-ok]`** |
| A7 the lane leaves its record | this file + `task.yaml` | present |

**RED (`436a66e^`)** — `-- 10/16 passed --`, `FAILED: B1 …, C1 ×5`, B1 naming
`cicd-code-review.md:190,201 · cicd-dev-story-tests.md:102,105 · cicd-quick-dev.md:188 ·
smh-code-review.md:161,172 · smh-quick-dev.md:78`. Every `D` counter-example passed at RED — the
guard's own machinery was proven working before the tree was touched.

**GREEN** — `-- 17/17 passed --`, exit 0.

**Sweep** — table at `sweep.json`; all five drawn from the guard's **source**, not from its cases:

| Mutant | Killed by |
|---|---|
| M1 BAN narrowed to the one wording that shipped | `D2 BAN fires on the OTHER shipped variant` |
| M2 BAN loses the singular form | `D3 BAN fires on the singular form` |
| M3 `norm()` stops collapsing wraps | `D6 REQUIRE survives a mid-quote line wrap` |
| M4 REQUIRE accepts `Agent tool` for `AgentTool` | `D7 REQUIRE rejects a near-miss paraphrase` |
| M5 REBUTTERS shortened | `A4 the rebutter list is populated` |

`-- restore verified: bytes match, nothing was committed --` · unfiltered re-run exit 0.

**Why the guard has two halves.** A ban-only guard is satisfied by **deleting** the rebuttal — which
removes the sentence that makes the fan-out legal, strictly worse than the bug. BAN + REQUIRE, and
block D fails both directions before either is believed.

## Gates

| Gate | Result |
|---|---|
| `run_all.py` **through `gate_receipt.py`** | **PASS exit=0, 69.0s @ `15bfa72e`**, `dirty_tree: false`. Receipt at `gates/suite.json`. The first stamp (`436a66e`) was **red** — that is the mechanism working, not a failure: it caught the missing `_artifacts/_main/INDEX.md` row, which was added and re-stamped. |
| `test_directive_quote.py` | 17/17, exit 0 (RED 10/16 first) |
| `test_twin_parity.py` | 65/65, exit 0 |
| `test_check_maps.py` | 27/27, exit 0 |
| `mutation_sweep.py` | **5/5 killed**, restore verified, unfiltered re-run exit 0 |
| `workflow_lint.py --toolkit-only` | **0 errors, 0 warnings, 8 info** (BOMs on vendored `testarch-*`, pre-existing), exit 0 |
| `check_maps.py` bare | **exit 1 — none of it mine**, proven below |

⛔ **All gates run bare, never piped** — a `| tail` reports the pipe's exit code, not the gate's.

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
