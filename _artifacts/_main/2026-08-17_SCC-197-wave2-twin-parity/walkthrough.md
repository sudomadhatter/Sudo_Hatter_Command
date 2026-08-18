# SCC-197 wave 2 — walkthrough

**Lane** `chore/SCC-197-wave2-twin-parity` · **Base** `origin/main` @ `86daaaf`
**Riders** SCC-209 (Part A) · SCC-205 (Parts B–E) · **Landing mode** full — this landing closes SCC-197.
**Plan** [implementation_plan.md](implementation_plan.md) · **Ports backlog** [ports-backlog.md](ports-backlog.md)

---

## Part A — SCC-209 · stop maintaining the `_AP` twins

**Operator ruling, 2026-08-18, verbatim:** *"remove updating the _AP workflows we just desided that
they dont work and we will completely redo them at a later time. So lets stop waisting time on those
and focus on keeping the twins (cicd and smh) up to date."*

### Why it ran first

Not sequencing preference — it defuses a trap. `workflow_lint.check_ap_twins()` was **armed**: it
fires the moment any `cicd-*` primary is committed without its twin restamped. Parts B–E edit
`cicd-code-review.md`, `cicd-self-audit.md` and `cicd-quick-dev.md`, so running Part A second would
have turned the gate red mid-lane and forced a restamp of a file already declared abandoned.

### What changed

| File | Change |
|---|---|
| `.agents/scripts/workflow_lint.py` | Deleted `_last_commit_ts`, `_last_commit_sha`, `AP_RECONCILED` and `check_ap_twins()` (75 lines) plus the single call site in `main()`. The two helpers had exactly four tree-wide references — two definitions, two uses, both inside the deleted function. |
| `.agents/scripts/tests/test_workflow_lint.py` | The SCC-82 AP-twin block (165 lines, cases A–G) deleted **in the same commit** — it called the function by attribute, so removing the definition alone raises `AttributeError`. Replaced by ONE assertion that all three `*-AP.md` files carry the `UNMAINTAINED` marker. |
| `.agents/commands/cicd-code-review-AP.md` · `cicd-self-audit-AP.md` | The `ap_reconciled:` stamp and its 60-/14-line reconciliation log replaced by the unmaintained marker. |
| `.agents/commands/cicd-dev-story-tests-AP.md` | Marker added (it never carried a stamp). |
| `.agents/commands/smh-clean-code-audit.md` | Its gate table advertised `` `-AP` twin drift `` as something `workflow_lint --toolkit-only` checks. It no longer does — a command that advertises a check that does not exist teaches agents the gate is wider than it is. |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | The `ap_reconciled:` row marked RETIRED, pointing at the marker instead. |
| `_artifacts/_memory/sudo-commands-have-ap-twins-that-drift.md` + `MEMORY.md` | Surgically edited: the `_AP` obligation replaced by the abandonment ruling; the `cicd`/`smh` twin law kept intact. Its claim that hoisting keeps bodies under a byte threshold corrected — an oversized body now gets an auto-generated thin launcher, so size is no longer an argument for hoisting. |

### What was deliberately NOT done

- **The three `*-AP.md` files are kept, not deleted.** Three autopilot engines still invoke them by
  name; a missing command makes a headless stage improvise silently instead of failing — an agent
  running with no specification, writing artifacts that look normal.
- **No no-op stub** left behind in place of `check_ap_twins`.
- The line numbers in the plan were **re-measured** before acting. The lane also absorbed `origin/main`
  first (`fd22097` → `86daaaf`, SCC-215), which had moved two of the rules the later parts touch.

### RED first — the assertions, and what they returned before the edit

`assert-partA.sh` (in this folder) is the scripted pass. Before any edit:

```
FAIL | A1 workflow_lint.py carries no AP-twin machinery  (got '11', want '0')
FAIL | A2 test_workflow_lint.py carries no AP-twin block  (got '9', want '0')
FAIL | A3 no command file carries an ap_reconciled stamp  (got '2', want '0')
PASS | A4 the three -AP files are still present
FAIL | A5 all three -AP files carry the UNMAINTAINED marker  (got '0', want '3')
FAIL | A6 no command advertises AP-twin drift as part of its gate
EXIT=1
```

After: all six PASS, `EXIT=0`.

⛔ **A2's assertion is keyed on the machinery, not the concept.** The first draft of the replacement
comment named the deleted identifiers in prose, which made the grep match its own comment — the
`comment-literals-invert-source-grep-tests` failure. The comment was reworded to describe the check
rather than name it.

### What the RED caught

The deletion broke a **later, unrelated** block: `real = Path(__file__).resolve().parents[3]` was
bound inside the SCC-82 block and reused by the SCC-128 resurrection-lint block 40 lines below.
`run_all.py` returned `NameError: name 'real' is not defined` — a file that dies at import looks
identical in a summary to one whose assertion failed, and only one of those is a real failure. The
binding was restored with a comment saying who else reads it.

Two more files went red for real reasons and both were expected consequences, not surprises:
`test_command_surfaces.py` (the `.opencode` mirror door for the edited command — cleared by
`/smh-sync-agents`) and `test_check_maps.py` (this lane's own artifact folder had no
`_artifacts/_main/INDEX.md` row — added).

### Gates

| Gate | Result |
|---|---|
| `python3 .agents/scripts/tests/run_all.py` | **33/33 files passed, exit 0** |
| `python3 .agents/scripts/workflow_lint.py --toolkit-only` | **0 errors, 0 warnings, exit 0** |
| `assert-partA.sh` | 6/6 PASS, exit 0 |
| `/smh-sync-agents` | exit 0 — 21 launcher skills, 56 opencode commands, 35 antigravity workflows |
