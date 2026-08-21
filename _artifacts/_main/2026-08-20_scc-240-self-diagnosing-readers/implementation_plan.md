---
IsArtifact: true
ArtifactMetadata:
  title: SCC-240 — self-diagnosing readers (roster + declared-set)
  type: implementation_plan
  date: 2026-08-20
---

# SCC-240 — Machine-read artifact blocks: make the readers runnable, make the refusals say why, and stop teaching a form the parser rejects

**Lane:** `chore/SCC-240-self-diagnosing-readers` (worktree `.claude/worktrees/SCC-240-self-diagnosing-readers`, cut from `origin/main` @ `db253fc`)
**Ticket:** SCC-240 (Task, standalone — `In Progress` since this lane's Step 0.5)
**Review runtime probe (Step 0):** `review-runtime: fan-out` — this runtime has the `Agent` tool.

## Goal

Three readers gate a close-out on hand-written markdown blocks (`lenses_run:` roster, `dispositions:`/`drift:`, `## Declared Change Set`). Today: (1) the two review commands teach the roster **inside a code fence**, and `walkthrough_roster.strip_fenced` deletes fenced content before reading (SCC-154, deliberate) — so "paste VERBATIM" produces a roster the gate cannot see; (2) the refusal for a fenced roster and for a roster with a blank line after its header is the same sentence as "no roster at all"; (3) `declared_change_set.parse` reports a rejected bullet with no reason; (4) `walkthrough_roster.py` cannot be run — no `main()` — so nothing can be checked until the close-out refuses it. Measured on SCC-210: ~12 minutes per reviewed lane.

Target: every reader is runnable and says why it refused; no teaching surface shows a form its own parser rejects, and a test keeps it that way; `step-02-verify.md` says in one place who groups duplicate claims and when.

## Acceptance (from the ticket, verbatim rows) → the assertion that proves each

| # | Acceptance | Assertion (RED first) | Lives in |
|---|---|---|---|
| 1 | The roster reader is runnable | `python3 .agents/scripts/walkthrough_roster.py <good walkthrough>` prints the parse and exits 0; exits non-zero with the reason on a bad one; exit 2 on a missing file. Fails today: no `main()` | `test_walkthrough_roster.py` block **`F · the refusal says WHY`**, cases `F1`, `F1b`, `F1c` |
| 2 | A fenced roster is named as fenced | `judge()` on a walkthrough whose only roster sits in a fence returns a reason containing `code fence` and `SCC-154`. Fails today | same block, case `F2` |
| 3 | A non-contiguous roster is named as such | `judge()` on a walkthrough with a blank line after `lenses_run:` returns a reason containing `contiguous`. Fails today | same block, case `F3` |
| 4 | A genuinely absent roster reads as it does now | control: reason still contains ``NO `lenses_run:` roster`` and the fix text (`recovered-inline`, `## Code Review`) — the existing `E1`/`E1b` cases stay green unchanged | `E1`, `E1b` (existing) + `F4` (control asserts neither new phrase appears) |
| 5 | Every `incomplete` bullet carries a reason | a plan with the three rejection shapes yields three rows whose reason text is pairwise distinct: `no → row separator`, `left side is not <OP> <path>`, `empty row text`. Fails today: rows are the bare bullet | `test_declared_change_set.py` block **`R · every incomplete row carries a reason`**, cases `R1`–`R3` |
| 6 | No doc teaches an unparseable block | every teaching surface (`.agents/commands/*.md`, `.agents/skills/code-review-engine/**/*.md`) that carries a `lenses_run:` header line, fed to the REAL `walkthrough_roster.parse` **exactly as written** (the way "pasted VERBATIM" lands it), yields ≥1 lens. Fails today on both review commands (fenced → 0). Same for the `## Declared Change Set` taught form through `declared_change_set.parse` | NEW `test_doc_examples_parse.py`, block `D · taught roster parses as taught` + `C · taught declared set parses` |
| 7 | The verify wave's grouping owner is unambiguous | `step-02-verify.md`'s "You prepare the inputs" bullet names **who** groups (the orchestrator), **when** (after the self-gate count, before serialising) and that the JSON stays one object per finding — and the SCC-156 paragraph points back at it instead of stating a second rule. Fails today: the two paragraphs read as competing instructions | NEW `test_doc_examples_parse.py`, block `G · one grouping owner` |

Measured line numbers below were re-grepped on this lane's base (`db253fc`) — they match the ticket's `c896410` measurements: `judge` at `walkthrough_roster.py:223`, the message at `:254-257`, `parse`'s row collector at `:156-165`; `declared_change_set.parse` at `:90`, bare `incomplete.append(s)` at `:119`; the fenced examples at `smh-code-review.md:377-384`, `cicd-code-review.md:379-386`, `step-04-record.md:51-62`, `SKILL.md:68-79`; the two step-02 paragraphs at `step-02-verify.md:48-50` and `:70-86`.

## Design decisions (each one is a ruling the builder follows, not an option)

1. **Commands UNFENCE their roster example; engine docs KEEP the fence and add the instruction.** The two review commands show a **paste-ready** example with concrete lens names — the taught bytes must be the accepted bytes, so the fence goes. `SKILL.md` and `step-04-record.md` show the engine's **return template** with `<placeholders>`; two existing tests (`test_review_engine.py:1416` "SKILL.md publishes a fenced return block", `test_lens_roster_contract.py:167` "step-04 publishes the SAME fenced return block") extract it *by its fence* and round-trip it filled — so the fence stays there and a ⛔ line is added: *return these as plain lines, never inside a code fence; the caller pastes your return verbatim and `walkthrough_roster.py` strips fences before it reads (SCC-154) — a fenced roster is an absent roster.* The ticket offers exactly these two remedies; this plan picks one per site and says why.
   ⚠️ **AUDIT FINDING (Lens 1, anchored `test_review_engine.py:1416` + `test_lens_roster_contract.py:167`):** both extractors take the block *by its fence* — `^```\n([\s\S]*?^lenses_run:` and `^```\n(review-runtime:[\s\S]*?^lenses_run:` — so the ⛔ line goes **after the closing fence**, never inside it, and **no new fenced block** is introduced anywhere above line 68 of `SKILL.md` or above line 51 of `step-04-record.md`. Violating either turns two green pins red (and, through the byte-identical cache comparison, red twice).
2. **The review commands' Step 4 gains the self-check.** One line after the paste instruction in both twins: `python3 .agents/scripts/walkthrough_roster.py <walkthrough>` *(PC: `python`)* — *it must print the rows you just pasted and exit 0; if it names a fence or a blank line, fix the paste now, not at close-out.* This is the mechanism the ticket's item 1 exists for ("there is no way to check a block until the close-out refuses it"); a doc that teaches the right form is the one-time repair, the self-check is what catches the next wrong paste. ⛔ The line sits OUTSIDE every `<!-- twin-law -->` fence (the fenced example sits above `<!-- twin-law: roster -->`), so `test_twin_parity.py` is unaffected — and the change is ported to both twins anyway (Lens 2 twin rule). `cicd-code-review-AP.md` is FROZEN (SCC-209) and carries no header line — it is not a teaching site and is not edited.
3. **`incomplete` rows stay strings; the reason is appended.** Every consumer reads `incomplete` as a list of raw-bullet strings: `test_declared_change_set.py` (`any("INDEX.md" in raw ...)`), `/smh-self-audit` Lens 1 ("incomplete bullets IS a finding"), both review twins' drift step (`incomplete` severity *important* per bullet). A dict row would break all of them for no reader gain. Shape: `f"{bullet}  ← {reason}"`, reasons: `no → row separator`, `left side is not <OP> <path> (op NEW|EDIT|DELETE, ONE path)`, `empty row text after the arrow`. The second-heading parenthetical already carries its own reason and is unchanged.
   ⚠️ **AUDIT FINDING (Lens 1, anchored `declared_change_set.py:110-119`):** the loop has **four** rejection paths, not three — `arrows` empty · `b` is None · `b` matched but `row.strip()` empty · **`b` is None AND the row is empty**. Precedence, stated so the reason is deterministic: **left-side failure wins** over an empty row (the author fixes the left first; the arrow is there). Case `R4` pins that fourth shape (`- foo → ` with no op) to the left-side reason.
4. **`parse()` grows two diagnostic flags; `judge()` branches on them.** `roster_header_fenced: bool` (a `lenses_run:` header matches in the RAW text and none survives `strip_fenced`) and `roster_header_empty: bool` (a header survives stripping and collects zero rows). `parse` stays total — flags are data, `judge` decides — so the CLI prints them too. Precedence in `judge` when `lenses == []`: empty-header (the more specific: a real header was found) → fenced → absent (today's message, byte-identical). `strip_fenced` and the contiguity rule are **not touched** (ticket DO NOT).
5. **The CLI.** `walkthrough_roster.py <walkthrough> [--verdict PASS|CONCERNS|FAIL|WAIVED]`: reads the file, takes the LAST `Verdict:` stamp with a lenient regex (this is a self-check, not a gate — both preflights keep their own strict/lenient readers and call `judge` as before), prints the parse as JSON plus each reason line, exits 0 when `judge` says ok, 1 when it refuses, 2 when the file is missing. `--verdict` lets a caller check a section before the stamp is written. Stdlib only, `argparse`, no new imports beyond `argparse`/`json`/`sys`.
6. **step-02 says it once.** The "You prepare the inputs" bullet becomes: *group first — apply the SCC-156 claim-grouping below AFTER the self-gate has read the raw count and BEFORE you serialise; then serialise the step-1 findings as a JSON list, **in step-1 order**, one object per finding, carrying the keys the extractor reads: `title` · `file_path` · `line_start` · `body` · `evidence`; the PROMPT names the groups (which indices share one question).* The SCC-156 paragraph's lead sentence gains *"— the orchestrator does this, at the point the dossier bullet above names; the roles receive groups, they never form them."* Every pinned phrase in `test_review_engine.py:569-625` is preserved verbatim (`as a JSON list, **in step-1 order**`, `carrying the keys the extractor reads: \`title\` · \`file_path\` ·\n\`line_start\` · \`body\` · \`evidence\``, the dossier-block heading, the extractor line).
7. **Generated surfaces are regenerated, never hand-edited.** After the command + engine edits: `pwsh .agents/scripts/sync-agents.ps1` **run from the worktree** (the script resolves `$HomeRoot` from its own location, `sync-agents.ps1:78-79`, so the worktree's mirrors are what it writes). Expected regenerated files: `.opencode/commands/{smh,cicd}-code-review.md`, `.agents/workflows/{smh,cicd}-code-review.md`, `.claude/skills/code-review-engine/{SKILL.md,steps/step-02-verify.md,steps/step-04-record.md}`. `test_command_surfaces.py` "every mirror door still says what its brain says" and `test_review_engine.py` "cache is byte-identical to master" are the RED that proves the sync ran.
8. **SOP currency.** The CLI is a new thing an operator can type and `walkthrough_roster.py`'s refusals change → `docs/_scc_sops_prds/workflows_testing_SOP.md` is staged in the same commit: row `walkthrough_roster.py` (SOP:1773) gains the CLI and the three-way refusal; the SCC-231 note (SOP:520-527) gains one sentence on `incomplete` reasons. `.agents/scripts/INDEX.md` gains the `walkthrough_roster.py` row it never had (Lens 2: a script with a CLI needs its INDEX row).

## Declared Change Set

- NEW `.agents/scripts/tests/test_doc_examples_parse.py` — the taught-form scan, the declared-set scan, the grouping-owner pin → 6, 7
- EDIT `.agents/scripts/walkthrough_roster.py` — diagnostic flags in `parse`, three-way refusal in `judge`, `main()` + `if __name__` → 1, 2, 3, 4
- EDIT `.agents/scripts/declared_change_set.py` — reason appended to every `incomplete` row → 5
- EDIT `.agents/scripts/tests/test_walkthrough_roster.py` — block `F` (CLI, fenced, contiguity, control) → 1, 2, 3, 4
- EDIT `.agents/scripts/tests/test_declared_change_set.py` — block `R` (three distinct reasons) → 5
- EDIT `.agents/commands/smh-code-review.md` — unfence the Step 4 roster example, add the self-check line → 6
- EDIT `.agents/commands/cicd-code-review.md` — same edit, twin → 6
- EDIT `.agents/skills/code-review-engine/SKILL.md` — ⛔ plain-lines return instruction under "What the engine returns" → 6
- EDIT `.agents/skills/code-review-engine/steps/step-04-record.md` — same instruction under §2 → 6
- EDIT `.agents/skills/code-review-engine/steps/step-02-verify.md` — one grouping owner, one place → 7
- EDIT (generated) `.opencode/commands/smh-code-review.md` — sync output → 6
- EDIT (generated) `.opencode/commands/cicd-code-review.md` — sync output → 6
- EDIT (generated) `.agents/workflows/smh-code-review.md` — sync output → 6
- EDIT (generated) `.agents/workflows/cicd-code-review.md` — sync output → 6
- EDIT (generated) `.claude/skills/code-review-engine/SKILL.md` — sync output → 6
- EDIT (generated) `.claude/skills/code-review-engine/steps/step-04-record.md` — sync output → 6
- EDIT (generated) `.claude/skills/code-review-engine/steps/step-02-verify.md` — sync output → 7
- EDIT `.agents/scripts/INDEX.md` — row for `walkthrough_roster.py` (CLI) → 1
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — SOP currency: the CLI, the three-way refusal, the `incomplete` reasons → 1, 2, 5

*(Planning-dir files — this plan, `walkthrough.md`, `task.yaml`, `gates/suite.json`, `sweep.json` — are carved out of the drift diff by `declared_change_set.PLANNING` and are not declared here.)*

## Execution order

1. **RED** — write `test_doc_examples_parse.py` (blocks `D`, `C`, `G`), block `F` in `test_walkthrough_roster.py`, block `R` in `test_declared_change_set.py`. Run each with `--case` and paste the red. Read which line raised: `D` must fail on `len(lenses) >= 1`, not in file discovery; `F1` must fail on the subprocess exit code (no `main()` → the module runs and exits 0 doing nothing — so `F1b` asserts stdout carries the parse JSON, which is what fails today); `R1` must fail on the distinct-reasons comparison.
2. **GREEN scripts** — `walkthrough_roster.py` (flags, judge branches, CLI), `declared_change_set.py` (reasons). Re-run `F`, `R` green; run both files whole.
3. **GREEN docs** — the two commands (unfence + self-check line), `SKILL.md` + `step-04` (⛔ line), `step-02` (grouping owner). Re-run `D`, `G` green.
4. **Sync** — `pwsh .agents/scripts/sync-agents.ps1` from the worktree; `git status` shows exactly the seven generated files above changed (anything else is reported, not committed blind).
5. **INDEX + SOP** — the two rows/sentences.
6. **Commit** (explicit paths, `-F` message files, key first): C1 `SCC-240 test(readers): RED — taught roster forms, refusal reasons, grouping owner`; C2 `SCC-240 feat(readers): walkthrough_roster CLI + three-way refusal; declared_change_set incomplete reasons` (+ SOP + INDEX staged — usage surface); C3 `SCC-240 docs(review): unfence the taught roster, add the Step 4 self-check, one grouping owner in step-02 [+ sync]` (+ SOP staged). Push after C1 and after C3.
7. **Receipt** — `gate_receipt.py run --task SCC-240 --gate suite --root _artifacts/_main/2026-08-20_scc-240-self-diagnosing-readers --cwd <worktree> -- python3 .agents/scripts/tests/run_all.py` on the clean tree after C3; then `workflow_lint.py --toolkit-only`, `check_maps.py --depth3-only --strict`, `test_sops_prds_folder.py`.
8. **Mutation sweep** — table below as `sweep.json`, run through `mutation_sweep.py`.
9. **Review gate** — `/smh-code-review`; then walkthrough, `task.yaml`, Dev Record.

## Mutant table (declared BEFORE mutating; every mutant drawn from the code, not from the cases)

| id | file | original (exactly once) | mutated | must be killed by (case / block) |
|---|---|---|---|---|
| M1 fence case never fires | `walkthrough_roster.py` | the `roster_header_fenced` computation (`head_raw and not head_stripped`) | `False` | `F2` / `F · the refusal says WHY` |
| M2 the two new messages swapped | `walkthrough_roster.py` | the `contiguous` reason string | the fence reason string | `F3` / `F · the refusal says WHY` |
| M3 CLI always exits 0 | `walkthrough_roster.py` | `return 0 if ok else 1` | `return 0` | `F1c` / `F · the refusal says WHY` |
| M4 one reason for every rejection | `declared_change_set.py` | the `no → row separator` reason | the `empty row text` reason | `R1` / `R · every incomplete row carries a reason` |
| M5 the smh example re-fenced | `.agents/commands/smh-code-review.md` | the unfenced `  lenses_run:` example's first line (with its new preceding line) | the same lines wrapped back in ```` ``` ```` | `D1` / `D · taught roster parses as taught` |
| M6 grouping owner deleted | `step-02-verify.md` | `group first` sentence | the pre-fix sentence | `G1` / `G · one grouping owner` |

## Sibling lanes (read at Step 0.5)

`git worktree list` → one sibling: `chore/SCC-235-dual-surface-blast-radius` @ `dae82f8`. Its diff vs `origin/main`: `_artifacts/_main/2026-08-19_scc-235-dual-surface-blast-radius/{implementation_plan.md,task.yaml}`; uncommitted: `_artifacts/_memory/MEMORY.md`, `_artifacts/_memory/audit-findings-need-a-file-anchor.md`. **Zero overlap** with this declared set; no landing-order dependency either way.

## Both machines

Stdlib only. The CLI is invoked as `python3` (Mac) / `python` (PC); the tests spawn it through `sys.executable`. No new dependency, no venv.

## Open questions

None that block. One ruling recorded rather than asked: the CLI's verdict reader is lenient on purpose (a self-check that refused a not-yet-stamped section would be useless at the moment it is needed), and `--verdict` exists for exactly that moment.

## Self-Audit (2026-08-20)

**Level:** LEDGER+BLAST (the set touches scripts others import, two command/door surfaces, an engine skill, generated mirrors and the SOP). **Mode:** PRE-WORK. **Repo:** `SCC-240-self-diagnosing-readers` (worktree of the command centre) · **Branch:** `chore/SCC-240-self-diagnosing-readers` — both from `git rev-parse` output. **Risk context (seam):** `risk_seam.py classify` → `{"status": "unclassified", "tiers": {}}` — placeholder, informs only.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every declared path ls'd (18 EDIT paths EXIST, the 1 NEW path is ABSENT — correct for a NEW)
             declared_change_set.py parse <plan> → present:true · 19 entries · incomplete:[]
             both machines: stdlib only; CLI via python3/python; tests spawn it through sys.executable
             lane fit: no backend/ frontend/ firebase/ functions/ mobile/ .github/ path in the set → /smh-close-task-merge-tree is the door
             every cited line re-grepped on db253fc (judge :223, message :254-257, row collector :156-165, dcs parse :90, bare append :119, fenced examples smh:377-384 / cicd:379-386 / step-04:51-62 / SKILL:68-79, step-02 :48-50 + :70-86)
             Scope Ledger precondition: ticket carries 7 acceptance rows, each with a concrete observable → holds
             Scope Ledger: NEW `.agents/scripts/tests/test_doc_examples_parse.py` ← rows 6, 7 (cell filled); caller count: 2 — this plan's commands AND `run_all.py:53` auto-discovery (`HERE.glob("test_*.py")`), so the artefact has a caller this plan did not create
read:        implementation_plan.md (this file) · walkthrough_roster.py · declared_change_set.py · test_walkthrough_roster.py · test_declared_change_set.py · test_lens_roster_contract.py · test_review_engine.py:55-100,140-175,565-625,1408-1480 · smh-code-review.md:340-445 · cicd-code-review.md:362-450 · step-02-verify.md (full) · step-04-record.md:1-75 · SKILL.md:40-95 · sop_currency.py:55-110 · run_all.py:53 · acli jira workitem view SCC-240
verdict:     findings below
```

```
lens:        2 Parity + Blast
checks_run:  command file → four doors exist for BOTH review commands (.claude/skills/<c>/SKILL.md · .opencode/commands/<c>.md · .agents/workflows/<c>.md · .agents/skills/<c>/SKILL.md — 8/8 present); commands/INDEX.md rows :51 (smh) and :47 (cicd) — no rename, rows unchanged
             command NAME → unchanged; no reference sweep owed
             a script → .githooks/ callers of either reader: none (grep) · tests exist for both · scripts/INDEX.md: `declared_change_set.py` row at :16, **no `walkthrough_roster.py` row** — the plan's EDIT of INDEX.md covers it
             gate or hook → none changed; no arming marker in the set
             the SOP / usage surface → commands, scripts and the engine skill are surfaces (sop_currency.py:69-77); `.agents/scripts/tests/` is EXEMPT (:83) → C1 (tests only) needs no SOP; C2 and C3 stage the SOP — consistent
             twins → cicd-code-review.md + smh-code-review.md both edited identically; the edit sits OUTSIDE every <!-- twin-law --> fence (the example ends at the line before `<!-- twin-law: roster -->`), so test_twin_parity.py is unaffected either way
             file in >1 repo → `ls Projects/*/.agents/scripts/{walkthrough_roster,declared_change_set}.py` → none (thin model holds); the port-checklist row does not apply
             sibling worktrees → fetched; one sibling (SCC-235 @ dae82f8): diff = its own _artifacts folder (2 files), status = 2 _memory files; intersection with this set = ∅
             generated surfaces → sync-agents.ps1:78-79 derives $HomeRoot from $PSScriptRoot, so running the WORKTREE's copy regenerates the worktree's mirrors (decision 7 holds); pwsh present at /opt/homebrew/bin/pwsh
read:        .githooks/ (grep) · .agents/commands/INDEX.md · .agents/scripts/INDEX.md:1-22 · sop_currency.py:55-110 · sync-agents.ps1:78-128 · test_twin_parity.py (PAIRS :88-91, law markers :174-175) · test_command_surfaces.py:540-560,620-660 · git worktree list · git -C <SCC-235> diff --name-only origin/main...HEAD · status --short
verdict:     findings below
```

```
lens:        3 Pre-Mortem (bounded — attaches narratives to Lens 1/2 findings only)
checks_run:  the silent one · the other-machine one · the fresh-clone one · the sibling-lands-first one — each asked of the two anchored findings
read:        the findings table below; sync-agents.ps1:80-92 (machine-home resolution); _harness.py:27-52 (--case semantics, for the sweep narrative)
verdict:     narratives attached below; nothing originated here
```

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/scripts/tests/test_review_engine.py:1416` | `contract = re.search(r"^```\n([\s\S]*?^lenses_run:[\s\S]*?)^```", texts[SKILL], re.M)` | the SKILL.md return block is located BY ITS FENCE; a ⛔ line placed inside the fence, or any new fence introduced above `SKILL.md:68`, changes what the round-trip reads — a green pin goes red (and again in the cache-identity check). **Baked into decision 1** (⚠️ AUDIT FINDING). Pre-mortem: the failure is LOUD (two reds), not silent — safe direction; the fresh-clone and other-machine variants are identical because the pin reads the file, not the environment | suggestion |
| `.agents/scripts/tests/test_lens_roster_contract.py:167` | `m = re.search(r"^```\n(review-runtime:[\s\S]*?^lenses_run:[\s\S]*?)^```", STEP04, re.M)` | same mechanism for step-04: the fenced block must still OPEN with `review-runtime:` — the ⛔ line goes after the closing fence. **Baked into decision 1.** | suggestion |
| `.agents/scripts/declared_change_set.py:110-119` | `arrows = list(ARROW.finditer(s))` … `if b and row.strip(): … continue` … `incomplete.append(s)` | the plan named THREE reasons for what is FOUR rejection paths (`b` None AND row empty is the fourth); without a stated precedence two builders produce two different reasons for one bullet. **Baked into decision 3**: left-side failure wins; case `R4` pins it. Pre-mortem: this one IS the silent kind — a wrong-but-present reason reads as diagnosed — which is why R4 exists rather than a comment | suggestion |

### Observations (uncounted)

- `scripts/INDEX.md` has never had a `walkthrough_roster.py` row (library-only until now); the EDIT in the declared set adds it. Not a finding against the plan.
- The unfenced command example keeps its two-space list indentation; `_ROSTER_HEAD_RE`/`_ROSTER_ROW_RE`/`_NA_HEAD_RE` all accept leading whitespace (`^\s*` / `^[>\-*#\s]*`), so a verbatim paste of the indented rows parses. The `lenses_na:` placeholder row `- <lens> · n/a — <why…>` is a template row (`<lens>` fails `[A-Za-z0-9]`), so a literal paste of it is silently ignored by `_NA_ROW_RE` — pre-existing, and the ticket's DO NOT list excludes folding in neighbouring findings; recorded here so it is not lost.
- Running the sync from the worktree also rewrites the machine-global caches (`~/.config/opencode`, `~/.gemini/...`) from the LANE's masters. If the lane were abandoned, those caches would carry its text until the next sync from `main`. Harmless for a lane that lands; noted because it is the one write this plan makes outside the repo.
- The mutation sweep filters by BLOCK label and attributes by CASE name (`_harness.py:27-99`); the table in this plan names both. `M5` mutates a `.md` (the smh example) — `mutation_sweep.py` is text-replacement and file-agnostic, so that is legal.

### Sibling landing-order dependency

None. SCC-235's change set and this plan's declared set share no file.

Audit verdict: GO
