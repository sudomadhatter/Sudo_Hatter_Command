# SCC-285 — the rebuttal quotes a directive that does not exist

**Ticket:** SCC-285 (Bug, epic SCC-33) · **Branch:** `chore/SCC-285-agenttool-directive-quote`
**Lane:** ejected here from `/smh-quick-fix` — `lane_qualify` returned `TASK` (toolkit paths).

## The defect, in one paragraph

Five house commands rebut a session directive by quoting it as
*"do not use subagents unless the user requested it"*. **That string does not exist.** The real
directive, hardcoded in the Claude Code binary as constant `dkm` and injected under feature name
`tengu_heron_brook`, reads:

> `Do not call the AgentTool unless the user requested it`

The difference is load-bearing: the real one **names the tool**. An agent reading its own system
prompt, then a command rebutting a paraphrase that does not match it, takes the gap as an escape
hatch. It did exactly that on 2026-08-22 — `_artifacts/_main/2026-08-22_code-review-graph-swap/walkthrough.md:227`:

> `review-runtime: inline (blocked: … "Do not call the AgentTool unless the user requested it". …`
> `and the directive names that tool specifically.)`

The third door worked — the refusal was recorded, not laundered. The refusal should not have happened.

**Not fixable at the source.** `uVo()` gates injection on the model carrying capability
`opus_5_prompt_bundle` with kill-switch `tengu_fennel_godwit` false. No env var, no settings key, no
managed-settings file (all verified absent). Only Anthropic can change or disable the text. The house
side is the only side we own.

## Scope — 8 occurrences, 5 files, two classes

| Class | What it is | Sites |
|---|---|---|
| **A — the rebuttal** | the operative *"this is satisfied"* sentence | `cicd-code-review.md:201` · `smh-code-review.md:172` · `cicd-dev-story-tests.md:105` · `cicd-quick-dev.md:188` · `smh-quick-dev.md:78` |
| **B — the narration** | recounting the SCC-203 incident | `cicd-code-review.md:190` · `smh-code-review.md:161` · `cicd-dev-story-tests.md:102` |

Class B is fixed too. Leaving a second paraphrase in the same file is how the first one came back,
and a guard that must whitelist exceptions is a guard nobody trusts.

⛔ **`cicd-quick-dev.md:188` ↔ `smh-quick-dev.md:78` sit inside the `review-runtime-probe`
twin-law block.** They must change **byte-identically** or `test_twin_parity.py` fails. That is a
feature: it is the gate proving both twins moved.

## Acceptance — every item checkable

| # | Statement | The assertion that proves it |
|---|---|---|
| A1 | No paraphrase of the directive remains in `.agents/commands/` | `grep -rniE "subagents? unless" .agents/commands/` returns **0** |
| A2 | Every rebuttal site quotes the directive verbatim, naming `AgentTool` | new test asserts the exact string present at all 5 Class-A sites |
| A3 | A permanent guard **fails** while any paraphrase is present | `test_directive_quote.py` seen RED, then GREEN, then mutation-swept |
| A4 | The `review-runtime-probe` twin-law block stays identical across twins | `test_twin_parity.py` exits 0 |
| A5 | Generated doors regenerated, never hand-edited | `workflow_lint.py --toolkit-only` exits 0; `.opencode/` matches masters |
| A6 | The usage-surface change carries its SOP doc in the same commit | armed `sop_currency.py` commit-msg gate accepts without `[sop-ok]` |
| A7 | The lane leaves its record | `walkthrough.md` + `task.yaml` present; `task_preflight.py --expect-key SCC-285` passes |

## Steps

1. **RED first.** Write `.agents/scripts/tests/test_directive_quote.py`. ⚠️ **AUDIT FINDING F3** —
   `run_all.py` **auto-discovers** `test_*.py` (`run_all.py:53`), so it needs no wiring and must not
   be edited.
   Two halves, both required:
   - **fails** when any paraphrase variant appears anywhere under `.agents/commands/`
   - **fails** when a Class-A site does *not* carry the verbatim string
   The second half is what stops the guard being satisfied by deletion. Run it, paste the real RED,
   and read *which* line raised — a check that dies in setup is not a red. → A1, A2, A3
2. **GREEN.** Rewrite the 8 sites. Class A quotes the directive verbatim and names the tool; Class B
   quotes the same string as what was misread. Twin pair edited identically. Surgical — no adjacent
   reflow. → A1, A2
3. **Twin + lint.** `test_twin_parity.py`, then `/smh-sync-agents` to regenerate `.opencode/` doors,
   then `workflow_lint.py --toolkit-only`. → A4, A5
4. **Suite through the receipt writer**, on a clean tree, per SCC-146. → A3
5. **Mutation sweep** via `mutation_sweep.py` with a declared table — mutants drawn from the guard's
   own source, not from its cases. → A3
6. **SOP currency.** ⚠️ **AUDIT FINDING F2** — the doc is `docs/_scc_sops_prds/workflows_testing_SOP.md`
   (`sop_currency.py:60`), **not** the `_my_resources/` quick-reference page. Stage it in the same
   commit. `[sop-ok]` is **not** used on this lane. → A6

## Declared Change Set

- NEW `.agents/scripts/tests/test_directive_quote.py` — the permanent guard → A1, A2, A3
- EDIT `.agents/commands/cicd-code-review.md` — lines 190, 201 → A1, A2
- EDIT `.agents/commands/smh-code-review.md` — lines 161, 172 → A1, A2
- EDIT `.agents/commands/cicd-dev-story-tests.md` — lines 102, 105 → A1, A2
- EDIT `.agents/commands/cicd-quick-dev.md` — line 188, inside twin-law → A1, A2, A4
- EDIT `.agents/commands/smh-quick-dev.md` — line 78, inside twin-law → A1, A2, A4
- EDIT `.opencode/commands/cicd-code-review.md` — regenerated by sync, never hand-edited → A5
- EDIT `.opencode/commands/smh-code-review.md` — regenerated by sync, never hand-edited → A5
- EDIT `.opencode/commands/cicd-dev-story-tests.md` — regenerated by sync, never hand-edited → A5
- EDIT `.opencode/commands/cicd-quick-dev.md` — regenerated by sync, never hand-edited → A5
- EDIT `.opencode/commands/smh-quick-dev.md` — regenerated by sync, never hand-edited → A5
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — SOP currency, same commit → A6
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one provenance row → A6
- EDIT `.agents/.sync-manifest.json` — written by sync-agents, not by hand → A5
- EDIT `_artifacts/_main/INDEX.md` — the session row `check_maps.py` requires → A7
- NEW `_artifacts/_main/2026-08-22_scc-285-agenttool-directive-quote/sweep.json` — the mutant table → A3
- NEW `_artifacts/_main/2026-08-22_scc-285-agenttool-directive-quote/gates/suite.json` — the gate receipt → A3
- NEW `_artifacts/_main/2026-08-22_scc-285-agenttool-directive-quote/implementation_plan.md` — this plan → A7
- NEW `_artifacts/_main/2026-08-22_scc-285-agenttool-directive-quote/walkthrough.md` — the record → A7
- NEW `_artifacts/_main/2026-08-22_scc-285-agenttool-directive-quote/task.yaml` — the manifest → A7

⚠️ **AUDIT FINDING F4** — `.agents/workflows/`, `.claude/skills/` and `~/.codex/prompts/` carry **zero**
occurrences of the paraphrase (measured). Only `.opencode/commands/` does, in exactly the five files
above. The speculative glob bullet that stood here is deleted.

## Out of scope, named

- **Fix B** (the `UserPromptSubmit` hook that injects the request on review-command turns). Real, and
  the operator chose A. Separate lane.
- **The neutralized-lens gap** — the harness flagged two of four AVCH-73 lens returns as
  `instruction-shaped pattern(s): settings-json`, and `code-review-engine` has no doctrine for it.
  Unrelated surface, and it is a finding for the rolling ticket, not this lane.
- **Turning the directive off.** Not ours; verified no local lever exists.

## Landing-order note

Sibling lane `chore/claude/teaching-edition` (SCC-280) is live and touches `.agents/commands/` —
but `smh-tour.md` / `smh-training.md`, **zero overlap** with my five. It also has
`.agents/scripts/tests/test_twin_parity.py` in its diff. Per `lane-collision-is-gates-not-files`,
zero file overlap is not zero risk: before close-out I run **my** guard against **their** blobs and
`test_twin_parity.py` from **their** copy against mine. No landing-order dependency expected; if
their twin-parity edit changes the block grammar, mine lands after theirs.

---

## Self-Audit (2026-08-22)

**Level: LEDGER+BLAST** — the Declared Change Set touches a command/door surface, a twin-law pair,
a new script, and more than one platform. Mode: **PRE-WORK**.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every named path/script/door resolved on disk; Declared Change Set parsed with
             declared_change_set.py; run_all.py discovery mechanism read at source; sop_currency.py
             surface list + SOP_DOC constant read at source; lane-fit check for deployable paths;
             Scope Ledger over every NEW entry
read:        .agents/scripts/tests/run_all.py:11,53 · .agents/scripts/sop_currency.py:60,69-83 ·
             .agents/scripts/declared_change_set.py:11-16,56 · .agents/scripts/tests/test_twin_parity.py:170-187 ·
             .agents/commands/{cicd,smh}-code-review.md · cicd-dev-story-tests.md · {cicd,smh}-quick-dev.md ·
             .agents/scripts/INDEX.md · the plan itself
verdict:     findings below
```

```
lens:        2 Parity + Blast
checks_run:  four platform doors grepped for the paraphrase; commands/INDEX.md rows (no rename, so
             no row moves); twin pairs identified and the twin-law block boundaries confirmed;
             sop_currency surface match for .agents/commands/*.md; sibling worktrees enumerated
             against a FETCHED origin/main; risk_seam.py classify on the declared paths
read:        .opencode/commands/ (5 hits) · .agents/workflows/ (0) · .claude/skills/ (0) ·
             ~/.codex/prompts/ (0) · .agents/commands/INDEX.md (6 rows, none renamed) ·
             git worktree list · git -C .claude/worktrees/SCC-280-teaching-edition diff --name-only
verdict:     findings below
```

```
lens:        3 Pre-Mortem
checks_run:  silent-failure narrative attached to F1; other-machine / stale-memory narrative
             attached to F2; no unattached output produced
read:        (attaches only — originates nothing, per the bound)
verdict:     clean (2 narratives attached to anchored findings)
```

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `implementation_plan.md` § Declared Change Set | `declared_change_set.py parse` returned `"entries": []` with **15** `incomplete` bullets — *"the left side is not `<OP> <path>`"* | **F1.** `/smh-code-review` Step 2 diffs the real diff against the declared set. An empty parse means it compares against nothing and reports no drift — a green that lies. Silent: nothing fails today. | important |
| `.agents/scripts/sop_currency.py:60` | `SOP_DOC = "docs/_scc_sops_prds/workflows_testing_SOP.md"` | **F2.** The plan named `_my_resources/_quick_reference/sudo_workflows_testing.md`, which **does not exist** on disk. A6 as written was unsatisfiable; the commit would be refused by the armed gate and the lane would reach for the `[sop-ok]` it forbids itself. | important |
| `.agents/scripts/tests/run_all.py:11` | *"Test files are auto-discovered (`test_*.py`), so a new one joins the suite with no wiring."* (confirmed at `:53`, `HERE.glob("test_*.py")`) | **F3.** The plan declared `EDIT run_all.py` to "register the new test". That edit must never happen — a declared path with no diff is drift at review Step 2. | important |
| `.opencode/commands/`, `.agents/workflows/`, `.claude/skills/`, `~/.codex/prompts/` | grep for the paraphrase: **5 hits, all under `.opencode/commands/`**; zero in the other three | **F4.** The plan's glob bullet `.agents/workflows/*.md, .claude/skills/*/SKILL.md — EDIT (if the bodies carry it)` was both unparseable and false. A conditional bullet cannot be diffed against a real change set. | suggestion |

**All four are baked into the plan inline** (`⚠️ AUDIT FINDING` markers) and the Declared Change Set
has been rewritten to the op-first grammar — it now parses **15 entries / 0 incomplete**.

### Scope Ledger

| CREATES (op `NEW`) | acceptance row requiring it |
|---|---|
| `.agents/scripts/tests/test_directive_quote.py` | A1, A2, A3 |
| `…/implementation_plan.md` | A7 |
| `…/walkthrough.md` | A7 |
| `…/task.yaml` | A7 |

No empty acceptance cell. **A7 was added by this audit** — the three ceremony artifacts were created
by the plan with no row requiring them, which is the ledger's finding shape; the permitted fix is
*add the row* or *delete the artefact*, and the lane contract requires the artifacts.

**Caller count** — `test_directive_quote.py`'s caller is `run_all.py`, which pre-exists this plan and
discovers it automatically. Not a single-caller artefact of this plan's own making.

**Precondition:** SCC-285's description carries a 3-item numbered ask; the plan reduces it to 7
acceptance rows, each with a concrete observable. Precondition met.

### Observations (uncounted, no severity)

- `risk_seam.py classify` returns `{"status": "unclassified"}` — normal for a fresh worktree with no
  graph built. Per the command's own note, the command centre's `test_links` is `0` anyway, so an
  `untested` list here would carry no information.
- `.agents/scripts/INDEX.md` carries no rows for `test_twin_parity.py` or `test_self_audit_contract.py`,
  and there is no `.agents/scripts/tests/INDEX.md`. A new test file therefore needs no INDEX row —
  the Lens 2 "script → `scripts/INDEX.md`" scar does not bind inside `tests/`.
- `.agents/commands/INDEX.md` holds 6 rows matching the five files, but **no command is renamed**, so
  the SCC-63/SCC-66 rename scars do not apply.

### Landing-order dependency

`chore/claude/teaching-edition` (SCC-280) is live and edits `.agents/commands/smh-tour.md` and
`smh-training.md` — **zero overlap** with this lane's five command files. It also carries
`.agents/scripts/tests/test_twin_parity.py` in its diff. Per `lane-collision-is-gates-not-files`,
that is a **gate** overlap, not a file one: before close-out this lane runs its own guard against
their blobs and their `test_twin_parity.py` against its own. **No landing order is forced**; if their
edit changes the twin-law block grammar, this lane lands second.

### Pre-Mortem narratives (attached, non-originating)

- **F1 — the silent one.** Nothing fails today. The plan ships, the review's drift check compares
  the diff against an empty declared set, prints no drift, and the lane closes green having never
  checked the thing the block exists to check.
- **F2 — the other-machine one.** The wrong SOP path did not come from nowhere: the shared memory
  index still names `_my_resources/_quick_reference/sudo_workflows_testing.md`. The next agent — on
  the PC, in a fresh clone, with no worktree open — makes this identical error and burns the same
  cycle. Correcting the memory entry is **out of this lane** (the store is read-only outside its own
  flows); it is carried to `## Your Actions` as a follow-on.

```
Audit verdict: GO
```

**Why GO and not NO-GO.** All four findings are clerical values inside a plan whose shape holds: a
mis-typed block grammar, a stale path constant, an unnecessary edit, and a speculative bullet. None
requires re-scoping, and all four are corrected above with their anchors quoted. The two NO-GO
grounds — a consequence that breaks an acceptance row **and cannot be fixed in place**, or a failed
Scope Ledger precondition — are not met. F2 did break A6 as written; it is fixed in the same pass,
and A6 now names the path the gate actually reads.
