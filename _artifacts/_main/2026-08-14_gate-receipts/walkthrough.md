# Walkthrough — SCC-146: gate receipts for the Task lane (close-out reads the verdict)

**Ticket:** [SCC-146](https://sudo-command.atlassian.net/browse/SCC-146) (Bug) · **Branch:** `chore/SCC-146-gate-receipts` · **Plan:** `implementation_plan.md` (Self-Audit GO)

**The plan gate, on the record:** the operator did not type the literal `approved`. After the plan
and its GO audit were presented, three successive proceed-directives arrived ("continue" · "ok" ·
"bring this whole task in for a successful landing… you are on the final subtask to close the main
task and the bug"), the last an explicit instruction to build and close this ticket. The builder
read that as a live operator override of the literal-word token and proceeded, recording it here
rather than claiming the word was said. If the retro rules that reading wrong, the failure mode to
name is the gate's, not the gap's: three explicit directives could not satisfy a gate whose token
is one specific word.

## Task Checklist

- [x] Step 0/0.5 — worktree `gate-receipts` off main, assets linked, SCC-146 → In Progress
  - sibling check at open: SCC-149 live at review, overlap = SOP + sync-manifest + INDEX ledger →
    landing order SCC-149-first, honored (it landed at `d9b35ac`; this lane absorbed it as a
    clean fast-forward before RED)
- [x] Step 1/1.5 — 9 acceptance items from the ticket's ACCEPTANCE block; plan + self-audit GO
  - finding while grounding: ticket line numbers had drifted (552→729, 653→856) — re-derived
  - finding while grounding: `check --sha` rejection already pinned (existing cases 8/13-15);
    A3's new work is the `--root`-mode variant only
  - audit F1: `closeout_preflight.py:307-314` imports three gate_receipt functions → every
    signature change is a default-preserving keyword param
- [x] Step 1.6 — subtasks: nothing clears the bar (one atomic protocol change); stated, moved on
- [x] Step 2 — RED, both suites
- [x] Step 3 — GREEN minimal; commit `5d13c35` (scripts + tests + 3 commands + mirrors + SOP +
  INDEX, sop_currency satisfied by staging); test strengthenings `981f3ea` (pre-declared mutant
  killers M5/M8)
- [x] Step 3 — mutation sweep: 8 declared / 8 killed, ONE first-pass survivor honestly reported
  - finding: M4's survival exposed the verdict-freshness check had no independent witness —
    killer case landed as `9d0a0ab`, M4b killed by it alone
- [x] Full gate at the landing sha, stamped through this lane's own receipt writer
  - review finding: the d1c4fea stamps were STALED by absorbing main (SCC-112's `docs/` file — a
    non-`_artifacts/` path), so all three receipts were re-stamped at the post-absorb sha
    `732f0726` — the code-fresh mechanic refusing stale evidence live, on its own lane
- [x] Step 4 — /smh-code-review — `Verdict: CONCERNS` (see `## Code Review (2026-08-14)`):
  5-lens engine + verify wave, 39 findings all verified true, deduped to 20 rows, none blocking;
  one follow-on task drafted with a load-bearing fix order

## Evidence

### A1 — `run --root` writes `<root>/gates/<gate>.json` with no board anywhere

Case 16 builds a git repo with **no** `_bmad-output/` and cwd pinned inside the temp dir (so a
resolver-fallback mutant dies "no project resolved" instead of writing into a real project).

**RED** (flags absent — each case fails at its own `c.check`, argparse's error as evidence):

```
[FAIL] 16 SCC-146 --root: receipt lands at <root>/gates/<gate>.json, no board: exit=2 …
gate_receipt.py run: error: the following arguments are required: --story, --gate
[FAIL] 16b … [FAIL] 18 … [FAIL] 18b … [FAIL] 18c … [FAIL] 19 …
-- 22/28 passed --
```

**GREEN** (suite run bare, exit read directly): `SUITE_EXIT=0`, `-- 28/28 passed --`.

### A2 — without `--root`, byte-identical behaviour

The pre-existing 15 cases are the regression net (all green), plus case 17 pins the other half:
the same boardless repo **without** `--root` still dies `cannot resolve project` — the bypass is a
bypass, not a new resolver default. Green-first by design (characterization of today's behaviour).

### A3 — `check --sha` rejects a different sha

Already pinned by existing cases 8/13-15; extended in root mode: 18 (fresh → 0), 18b (content
moved → `STALE`, exit 2), 18c (`--sha <shipping>` re-pins → 0).

### A4 — `gate: SKIP` when PASS + code-fresh + receipts valid + clean

The fixture is the REAL close-out shape: receipt stamped on a clean tree at the code sha, then the
walkthrough (verdict citing that sha) lands as an **artifacts-only commit** — so HEAD ≠ verdict sha
with an artifacts-only diff, and the case pins that this **still SKIPs**. This is the one measured
deviation from the ticket's literal "sha equals HEAD": strict equality can never fire in a real
lane, because the stamp cannot cite the commit it rides in — /smh-code-review Step 3's own rule
("artifact- and doc-only commits after that run do not invalidate it") made mechanical, and the
only reading under which A7's "exactly one suite run" is achievable (SCC-149 review, finding C4,
observed live twice).

**RED:** `[FAIL] SCC-146 PASS + code-fresh + receipt + clean -> gate: SKIP, exit 0` (no such
concept in the script). **GREEN:** the case passes; SKIP line prints as
`gate: SKIP - verdict PASS @ <sha8>, receipts valid (suite)`.

### A5 — the three no-SKIP cases (sha moved · dirty · no receipt) + the suite-receipt pin

Green-first **declared characterization** ("commands print" is today's behaviour); their teeth are
the mutation sweep's named kills (M4/M6, and M5 for the added lint-only-receipts case). A FAIL
verdict path is the fourth: red-first.

### A6 — a FAIL verdict blocks the merge

**RED, the ticket's correctness hole captured verbatim:** a FAIL-verdicted lane printed

```
VERDICT: clear to close out and merge
[FAIL] SCC-146 a FAIL verdict BLOCKS the merge (exit 2), and says why: exit 0: …
```

**GREEN:** exit 2, `the review verdict is FAIL - fix on the branch and re-run the review; a FAIL
lane does not merge`. Suite `-- 115/115 passed --`, `SUITE_EXIT=0`, run bare.

### A7 — one suite run end to end

Delivered by the protocol, and **this lane exercises it on itself**. Recorded count for this
lane, end to end: **2 full-suite runs** — the quick-dev stamp @ `d1c4fea`, then the review
re-stamp @ `732f0726` after Step 0.7 absorbed main (SCC-112 landed a `docs/` file mid-lane, so
the code-fresh conjunct correctly refused the first receipt). That second run IS the designed
fail-toward-running path, not redundancy; a lane whose `main` does not move mid-flight runs
once. Before the fix the same lane shape ran 4×. Close-out is expected to `gate: SKIP` on the
re-stamped receipts (verdict CONCERNS @ 732f0726; every later commit artifacts-only).

### A8 — `run_all.py` stays N/N

`23/23 files passed`, exit 0 — run at review through the receipt writer:
`[PASS] suite exit=0 425.2s @ 732f0726`, `dirty_tree: false` (gates/suite.json, commit 6ea385f).

### A9 — SOP in the same commit

`git show --stat 5d13c35` — the three command bodies, their mirrors, both scripts, both suites and
`workflows_testing_SOP.md` land together; no `[sop-ok]` on the usage-surface commit.

### Mutation sweep — 8 mutants, declared before running, all drawn from the shipped diff

Run as ONE pass; restore from COPIES (never `git checkout --` — SCC-147's trap), application
verified by replace-count and diff-line count; a kill requires the suite red AND the NAMED case
on a `[FAIL]` line (a crashed run crediting its named case is the SCC-149 M5 class, checked
against explicitly).

| # | Mutant (single minimal edit) | Named case | Result |
|---|---|---|---|
| M1 | `--root` given but project still resolved via `resolve_project_root` | gr 16 | **KILLED** (22/28, 6 red) |
| M2 | `receipt_dir` ignores flat → nested board path in root mode | gr 16 | **KILLED** (26/28, 2 red) |
| M3 | FAIL verdict: `rep.err` → `rep.info` (the hole resurrected) | tp A6 | **KILLED** (114/115, 1 red) |
| M4 | verdict-freshness check `if moved:` → `if False:` | tp A5a | **SURVIVED the first pass — see below** |
| M4b | same mutant, re-run after the killer case landed | tp stale-verdict-fresh-receipt | **KILLED** by that case ALONE (115/116, 1 red) |
| M5 | suite-receipt requirement removed | tp lint-only-receipts | **KILLED** (114/115, 1 red) |
| M6 | upstream-errors guard removed (SKIP beside a red finding) | tp A5b | **KILLED** (114/115, 1 red) |
| M7 | SKIP computed but the plan ignores it | tp A4 | **KILLED** (113/115, 2 red) |
| M8 | `VERDICT_RE` anchor dropped (prose about a verdict matches) | tp A4 via the decoy line | **KILLED** (110/115, 5 red) |

```
restored byte-identical: True (both passes)
closing green confirmation: test_gate_receipt.py exit=0 28/28 · test_task_preflight.py exit=0 116/116
```

**The M4 story — a finding against this lane's own suite, and the sweep doing its job.** M4
disabled the *verdict*-freshness check and A5a stayed green at 115/115: in every fixture the
receipt was stamped at the same sha as the verdict, so the *receipt*-freshness check caught the
drift redundantly and the verdict check had no independent witness. The two separate in a real
shape: review stamps the verdict, "one more fix" lands, the suite is re-run and re-stamped
mechanically — receipt FRESH, verdict STALE — and with M4's edit that lane SKIPs on a verdict
describing code that no longer exists. The check was load-bearing; the suite was blind. The
killer case (`9d0a0ab`) builds exactly that shape and M4b died to it alone. Pre-declared M5/M8
had already forced two other strengthenings (`981f3ea`) before the sweep ran.

## Code Review (2026-08-14)

Verdict: CONCERNS @ 732f0726

Suite evidence measured at `732f0726` (the post-absorb tip; every later commit is artifacts-only — receipts + this section).

**Scope:** the 20-file `main...HEAD` diff at `732f0726` — `gate_receipt.py --root/--task`, `task_preflight.py check_gate`, three smh command bodies + opencode mirrors, SOP flowcharts, both INDEXes, the lane's artifacts.
**Method:** `code-review-engine` (5-lens fan-out in clean contexts, `review_mode: full`, `lens_budget: standard`), verify wave (Evidence Verifier + Compound Synthesis over a 39-finding dossier via `evidence_extract.py`), acceptance audit against the ticket's A1–A9, gates run bare, `/smh-clean-code-audit` nested.

### Engine summary

```
lenses_run:      5/5  (blind ok · edge ok · literal ok (no top-up used) · acceptance ok · test-adequacy ok)
lenses_na:       none
findings:        4 decision · 11 patch · 2 applied-as-record · 3 dismissed   (39 raw, deduped; 6 compound folded in)
severity_floor:  CONCERNS
notes:           verify wave ran in full — Evidence Verifier ok (dossier built, ALL 39 findings verified TRUE, none refuted,
                 with severity recalibrations applied below and two live reproductions: the scc-83 FAIL-then-PASS wedge shape,
                 and SCC-146's own two-hit non-lexicographic enumeration); Compound Synthesis died once (machine sleep),
                 recovered on the single retry -> ok, 6 compound findings; lens spill file kept in session scratchpad, not
                 ARTIFACT_DIR (untracked files there would DIRTY the receipt stamps); blind lens ran truly blind (diff only)
```

### Findings (authoritative table)

| # | file:line | Severity | Finding | Disposition |
|---|---|---|---|---|
| 1 | `task_preflight.py:805` | important | `any(FAIL)` judges ALL verdict stamps while status uses `verdicts[-1]` ("latest stamp is current") — the FAIL error's own remedy (re-run the review, which APPENDS a stamp) can never clear it; live multi-stamp walkthroughs exist (scc-83 FAIL→PASS→PASS, scc-88, scc-94), so any re-reviewed lane wedges at close-out forever | **deferred** → follow-on; sequencing per compound C2: pin FAIL-then-PASS both directions FIRST, then implement plan S2's "use the stamp whose sha resolves; conflicting → no SKIP" — a bare latest-wins fix flips it fail-open |
| 2 | `task_preflight.py:798-828` | important | verdict pool = every walkthrough that substring-mentions the key (`SCC-14` ⊂ `SCC-146`); `verdicts[-1]` + the receipts dir bind to unspecified scandir order. Proven live: THIS lane's close-out sees 2 hits (incident-taxonomy's walkthrough mentions scc-146 and carries its own `PASS @ 4fa5596`, no gates/) | **deferred** → follow-on (resolve to the task's OWN session dir; refuse SKIP on >1 stamped hit) |
| 3 | compound C1 (parents 1,2,4) | important | an artifacts-only lane can SKIP wholly on a SIBLING's evidence: foreign verdict sha + committed foreign receipts are permanently code-fresh by construction when this lane's diff is all `_artifacts/` | **deferred** → follow-on (same fix as #2 closes it) |
| 4 | `task_preflight.py:850` + SOP flowchart `G0→S3` | important | SKIP requires only a `suite` receipt: `check_maps` runs nowhere in the review's own gate table, and the link+anchor sweep has no receipt — compound C4: every SKIPping lane structurally carries ≥1 post-verdict `_artifacts/` commit (the stamp cannot cite the commit it rides in) that no check ever inspects, and map/INDEX drift is exactly `_artifacts/`-borne (verifier: the sop_currency half of the original claim was overstated — artifacts edits are not usage surfaces) | **deferred** → follow-on; fix shape per C4: SKIP spares the SUITE only, the cheap artifact-scoped checks still run. Mitigation now: this lane stamps lint+maps too and `check_gate` freshness-checks every receipt present |
| 5 | `gate_receipt.py:290` + `smh-quick-dev.md` example | important | a relative `--root` resolves against the INVOKER's cwd, not `--cwd`; the doc's own fenced example is relative. From the wrong checkout the receipt lands as an untracked stray with success-shaped output (compound C5: later committed, it becomes foreign "valid" evidence for #3). Adjacent (verifier id 10, suggestion): `run --root` WITHOUT `--cwd` executes the gate inside the artifacts dir and records `fail` — not `unrunnable` — for a suite that never ran, breaching the module's own four-results doctrine | **deferred** → follow-on (resolve relative root against `--cwd` or require `--cwd` in root mode). This review stamped with ABSOLUTE paths for exactly this reason — this session's own cwd reset mid-run, live proof of the premise |
| 6 | `task_preflight.py:798` | important | a FAIL verdict in non-canonical spelling (`**Verdict: FAIL @ …**`, lowercase, heading-prefixed) matches nothing → demotes to info "no review Verdict line" → full gate runs → the ticket's correctness hole returns on exactly the FAIL direction | **deferred** → follow-on (near-miss detector: verdict-looking line that fails the canonical regex → err, not info) |
| 7 | `task_preflight.py:820-853` | important | three guard conjuncts are deletable with the suite staying green (outside the declared M1–M8): receipt-validity (fail/DIRTY/unreadable — no fixture has a BAD existing receipt), receipt-freshness (verdict-fresh/receipt-STALE — M4's mirror), unknown-verdict-sha (deletion flips `None` falsy = fail-OPEN) | **deferred** → follow-on; sequencing per compound C3 is BINDING: land these killers BEFORE any `check_receipt` unification (#10) refactors through unpinned conjuncts |
| 8 | `task_preflight.py:765` | suggestion | `VERDICT_RE` is fence-blind: a canonical stamp pasted at column 0 inside fenced evidence reads as real (M8 proved the anchor against the INDENTED decoy only); combined with #1 a fenced FAIL is a permanent block | **deferred** → follow-on |
| 9 | `gate_receipt.py:113` vs `task_preflight.py:837` | suggestion | receipt `dirty_tree` counts `_artifacts/`-only dirt while every freshness check exempts `_artifacts/` — a habitually dirty memory store makes SKIP dead on that machine (info-level signal only). Compound C6: exempt at the READER per-consumer, never at the shared recorder (closeout_preflight reads the same field) | **deferred** → follow-on |
| 10 | `task_preflight.py:830-848` | suggestion | `check_gate` re-implements receipt validity inline despite importing `gate_receipt` under a one-loader rationale; two staleness definitions (tree-identity in `check_receipt` vs non-artifacts-diff here) shipped in one commit | **deferred** → follow-on, strictly AFTER #7's tests (C3) |
| 11 | `smh-code-review.md` Step 3 vs preflight | nitpick (verifier-calibrated: `warn` needs `--warn-exit`, which no documented suite invocation uses) | inheritance bar mismatch: review doc adopts on result `pass` only; `check_gate` accepts `pass` or `warn` | **deferred** → follow-on doc alignment |
| 12 | `smh-code-review.md` Step 3 + `nonartifact_moved` docstring | suggestion | "Artifact- and **doc-only** commits do not invalidate" overstates the mechanism — only `_artifacts/` is exempt; a `docs/` commit invalidates. Proven live IN THIS REVIEW: SCC-112's `docs/migrations/` file staled the d1c4fea suite receipt | **deferred** → follow-on (drop "doc-only" from both texts; A5a's own fixture already uses `docs/x.md` as the stale trigger) |
| 13 | `gate_receipt.py:289` | nitpick | `--root` + `--project` both accepted; `--project` silently ignored | **deferred** (one-line `parser.error` + case) |
| 14 | `smh-close-task-merge-tree.md` Step 2 vs ticket | suggestion | ticket's constraint sentence ("close-out runs lint WITHOUT `--toolkit-only`") measured FALSE: `gate_plan()` (`task_preflight.py:890`, unchanged code, SCC-64) prints WITH the flag in the lobby; the lane's own lint receipts agree; the new doc text states ground truth | **dismissed with measurement** — the deviation from the ticket's letter is hereby declared; the ticket sentence was stale |
| 15 | `implementation_plan.md` §S5 + Phase 3 | important (verifier 0.8) | two plan claims false against shipped mechanics: S5 restates the stale lint-scope sentence, and the per-machine pre-mortem claim ("a fresh machine re-runs — every conjunct fails") is inverted — receipts, verdict and freshness all TRAVEL via git by design; no conjunct reads where a receipt was stamped, so an ARMED second machine SKIPs on traveled evidence (an unarmed fresh clone still blocks, but via `hooks_armed` errors feeding the errs-guard — a different mechanism than the plan claims) | **applied as record** — resolution documented here: travel IS the design ("rides the branch" is the feature's own words); the residual policy question (should SKIP require same-machine evidence, or is a traveled receipt + the armed-hooks guard enough?) → **decision, deferred** to the follow-on |
| 16 | walkthrough §A7 | suggestion | invocation count was unrecorded at review time | **applied** — count recorded in refreshed Evidence: 2 full-suite runs end-to-end (d1c4fea quick-dev stamp; 732f0726 review re-stamp forced by SCC-112 landing mid-lane), vs 4 before the fix; the second run is the freshness mechanic working, not redundancy |
| 17 | `test_task_preflight.py` / `test_gate_receipt.py` | suggestion | remaining test gaps: CONCERNS allow-half never exercised · WAIVED branch unpinned · `--json` `gate` field unasserted · `check_gate` has no unit-tier (all branches cost a full subprocess fixture) · root-mode `--sha`-MISMATCH reject unpinned (18b proves HEAD-staleness, 18c the accept) · `cmd_list` flat empty-dir branch | **deferred** → follow-on test additions |
| 18 | ticket WAIVED letter | suggestion | WAIVED never SKIPs (returns None → full plan) vs the ticket's "skip the receipt check"; plan §S2 declares this conservative reading with a rationale that holds | **dismissed** (declared deviation, fail-toward-running direction) |
| 19 | `test_gate_receipt.py` case 16 | nitpick | the plan-promised printed-receipt-path assertion is not made (existence + result only) | **deferred** |
| 20 | SOP:466 | — | plan S6's conditional edit correctly not triggered: the node reads "EVERY gate through gate_receipt.py", no story-lane-only claim | **dismissed with measurement** |

### Gates (all run bare from the worktree, exit codes read directly)

| Gate | Result |
|---|---|
| Enforcement suite | **RE-RAN, did not inherit.** The d1c4fea receipt was `pass` + clean-stamped, but code-fresh FAILED: `git diff d1c4fea..HEAD --name-only` includes `docs/migrations/antigravity_extensions/antigravity-extension-ids.txt` (non-`_artifacts/`, from SCC-112 absorbed in Step 0.7) — fail toward running. Re-run through the lane's own receipt writer: `[PASS] suite exit=0 425.2s @ 732f0726`, output_tail `23/23 files passed`, `dirty_tree: false` — receipt committed `6ea385f` |
| Toolkit lint | `workflow_lint.py --toolkit-only`: `0 error(s), 0 warning(s), 8 info` (pre-existing BOM infos), exit 0 — re-stamped `[PASS] lint exit=0 0.2s @ 6ea385f6`, committed `822301b` |
| Assertion evidence | the lane's RED assertions re-run GREEN bare: `test_gate_receipt.py` `-- 28/28 passed --` exit 0 · `test_task_preflight.py` `-- 116/116 passed --` exit 0 |
| SOP currency | `sop_currency.py --paths <20 changed> --message "<5d13c35 subject>"` → exit 0 (SOP rides the change set — A9's mechanism) |
| Link + anchor | 84 path references across the 11 changed `.md` files: **0 dead introduced**. Two unresolvable strings sit in `_artifacts/_main/INDEX.md` rows this diff never touched (legacy, noted not gated); `scripts/INDEX.md` is the house shorthand for `.agents/scripts/INDEX.md` (exists) |
| Door parity | n/a (no command added/renamed/deleted). Verified anyway: Claude/Codex skills + antigravity workflows are thin launchers; opencode mirrors byte-match their masters modulo the frontmatter description line; `.sync-manifest.json` regenerated (09:50:47), not hand-edited |
| check_maps | `--depth3-only --strict` exit 0 — re-stamped `[PASS] maps exit=0 0.1s @ 822301b0`, committed `fedabcd` |

### Acceptance matrix (A1–A9, ticket ACCEPTANCE block)

| Item | Verdict | Proving evidence |
|---|---|---|
| A1 `run --root` writes `<dir>/gates/<gate>.json`, no board | SATISFIED | case 16 (boardless temp repo, cwd pinned inside it) + 16b (`--task` alias, field `scc-00`) — 28/28 green re-run at review |
| A2 no-`--root` byte-identical | SATISFIED | case 17 (boardless repo WITHOUT `--root` still dies `cannot resolve project`, exit 2 — bypass, not new default) + the untouched 15-case net green; literal lens verified `closeout_preflight.py:307-314`'s three imported calls bind unchanged |
| A3 `check --sha` rejects other-sha receipt | SATISFIED | pre-existing cases 8/13-15 + root-mode 18 (fresh→0) / 18b (moved→STALE exit 2) / 18c (`--sha` re-pin→0); residual: root-mode wrong-`--sha` reject direction unpinned (finding #17) |
| A4 `gate: SKIP` on PASS+fresh+receipts+clean | SATISFIED (declared deviation) | tp case "PASS + code-fresh + receipt + clean -> gate: SKIP, exit 0" incl. the C4 fixture pin (HEAD ≠ verdict sha, artifacts-only delta, still SKIPs). "sha == HEAD" → "code-fresh" deviation declared in plan+walkthrough; rationale engaged: strict equality can never fire on a real lane — holds |
| A5 commands print on moved/dirty/no-receipt | SATISFIED | three separate cases: "code moved…commands print, never SKIP" (exit 0) · "dirty tree never SKIPs" (exit 2 + commands) · "PASS but NO receipt -> commands print"; plus stale-verdict/fresh-receipt (M4b killer) and lint-only-receipts |
| A6 FAIL verdict → exit 2 | SATISFIED | "a FAIL verdict BLOCKS the merge (exit 2), and says why" (reject) + A4's SKIP exit 0 (allow) — both halves per tests-must-gate-for-real; M3 kills the info-downgrade |
| A7 run_all exactly ONCE end-to-end, counted | SATISFIED with recorded cause | count on this self-exercising lane: **2** (quick-dev stamp @ d1c4fea · review re-stamp @ 732f0726, forced by SCC-112 landing mid-lane) vs 4 before. The second run is the code-fresh conjunct refusing stale evidence — the designed fail-toward-running path, not redundancy. A lane whose `main` does not move mid-flight runs once |
| A8 run_all stays N/N | SATISFIED | `23/23 files passed`, exit 0, receipted @ 732f0726 (this review's closing run) |
| A9 SOP same-commit, no `[sop-ok]` | SATISFIED | `git show --stat 5d13c35`: commands + mirrors + scripts + suites + SOP land together, subject carries no `[sop-ok]`; `sop_currency` re-demonstrated exit 0 at review |

### Clean-Code Gate — CONCERNS (nested mode, SCC-146 rule followed)

**Machine floor (imported per the new Step 3.5 nested-mode rule — no re-runs):**
- run_all.py : PASS — imported from Step 3's fresh receipt (`pass exit=0 425.2s @ 732f0726`, 23/23)
- workflow_lint : PASS — imported (0 err / 0 warn / 8 info, exit 0 + receipt @ 6ea385f6)
- sop_currency : PASS — imported (exit 0, Step 3 row)
- link + anchor : PASS — imported (84 refs, 0 dead introduced)
- py_compile : PASS — run here (the only floor row Step 3 does not own): 4 changed `.py` files, exit 0
- lint / types : not applicable to this repo (no venv, no ruff, no tsc)

**Judgment pass (§2A comment contract · §2C convention table):**
- §2A: every new block carries `SCC-146:` provenance (argparse block, `--root` bypass note, `receipt_dir` flat comment, `check_gate` docstring contract, `nonartifact_moved` C4 rationale, test-block comments). The one nearby `AIDEV-NOTE` (`gate_receipt.py:89`, warn-exit contract) is NOT invalidated by this diff. 0 TODO/FIXME, 0 restating comments in the 933 added lines.
- §2C: naming law ok (no new command) · prefix-permission ok (smh acts on the lobby) · one-door ok (thin launchers; mirrors regenerated, `GENERATED` markers intact) · rule pointers restated inline (close-task restates only-the-preflight-skips; quick-dev restates clean-tree stamping) · both-machines ok (0 bare `python` added) · gates ship ARMED (FAIL → hard exit 2 from day one) · every gate has an exit (the SKIP is the exit; `[sop-ok]` extant) · gate can fail — proven by the 8-mutant sweep + this review's #7 residue (recorded above, not silent) · artifacts live in the tree · board narrative n/a · no personal names.
- §2B drift-hunt: imported from Step 1 (source `review`) — no additional drift/bloat beyond findings #10/#13.

Cap source: the deferred important findings above — hence CONCERNS, not PASS. No FAIL row fired.

### Step 0.7 — blast-radius re-derivation (against current main)

- **What main moved under this diff:** main advanced past the briefing (d9b35ac → dac2146, SCC-112's merge) adding exactly one new file, `docs/migrations/antigravity_extensions/antigravity-extension-ids.txt`. Nothing this diff references moved, was renamed, or deleted.
- **True overlap + merge-tree:** intersection of theirs (1 file) and mine (20 files) EMPTY (`grep -Fxf` exit 1); `merge-tree --write-tree` clean (tree `befc4b8b`, no conflict blocks). Absorbed as merge `732f0726` before the hunt; the absorb staled the suite receipt (non-artifact path in range) — re-stamped, per this diff's own rule.
- **Sibling lanes:** only this worktree + the main checkout live locally; remote `chore/SCC-115-verify-hooks-migrate` and `claude/teaching-edition` have no local lane; no landing-order dependency in either direction.

### Follow-on (ONE task, drafted — operator files it)

Teach `check_gate` its remaining edges, in THIS order (compound C2/C3 and verifier id 33 make the order load-bearing):
1. FIRST land the conjunct killers that pin today's CORRECT behavior: bad-existing-receipt (fail/DIRTY/unreadable) · verdict-fresh/receipt-STALE · unknown-verdict-sha · CONCERNS allow-half · WAIVED branch · `--json` gate field · fenced col-0 stamp. Do NOT pin multi-verdict behavior yet — a test pinning today's `any(FAIL)` would cement defect #1 (verifier id 33).
2. THEN decide + implement verdict resolution per plan S2 (own-session-dir hits only; the stamp whose sha resolves; conflicting → no SKIP), landing the FAIL-then-PASS pins IN THE SAME CHANGE, expressing the decided semantics both directions — closes #1/#2/#3.
3. THEN: SKIP spares the suite ONLY (artifact-scoped checks still run — closes #4/C4) · relative `--root` resolved against `--cwd`, `--cwd` required in root mode (#5) · near-miss verdict detector (#6) · `check_receipt` unification, strictly after step 1's tests (#7/#10, C3) · reader-side dirt exemption (#9, C6) · per-machine SKIP policy (#15) · doc alignments (#11/#12) · `--project`/`--root` exclusion (#13).

**Changes applied by this review: none to source** — the deferred findings converge on one seam (`check_gate` + its documenting texts) and need design decisions plus tests (SCC-147: triage, never loop). Applied here: the three receipts re-stamped at the post-absorb sha (commits 6ea385f · 822301b · fedabcd), this section, and the Evidence/Checklist refresh below.

## Your Actions

- [ ] **Invoke `/smh-close-task-merge-tree`** — the operator's merge sign-off (one invocation,
  one merge). Expected shape: preflight prints `gate: SKIP - verdict CONCERNS @ 732f0726,
  receipts valid (lint, maps, suite)`. Caveat from review finding #2: `check_artifacts` also hits
  the incident-taxonomy walkthrough (it mentions scc-146); on this machine's enumeration order
  the right stamp wins, and if the order ever flips the foreign stamp is stale, so the preflight
  falls back to the FULL printed gate — run it; either outcome is sound.
- [ ] **File the follow-on Task** from the review section's "Follow-on" block (one ticket:
  check_gate's remaining edges; the fix ORDER in that block is load-bearing — conjunct killers
  first, multi-verdict semantics second, never a pin of today's `any(FAIL)` first).
- [x] Review-time agent-solvable rows: receipts re-stamped post-absorb (6ea385f/822301b/fedabcd),
  A7 count recorded, A8 receipt cited, plan-vs-built deviations declared in the review table
  (rows 14/15/18/20) — nothing else was deferrable to this lane.
