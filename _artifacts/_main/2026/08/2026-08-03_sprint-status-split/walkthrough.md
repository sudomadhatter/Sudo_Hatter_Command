<!-- wf-lint: allow-encoding-literals — quotes a cp1252 digraph as an example, same as the plan. -->
---
IsArtifact: true
ArtifactMetadata:
  title: "Walkthrough — Wave 4: sprint-status.yaml split"
  type: walkthrough
  date: 2026-08-03
---

# Walkthrough — Wave 4: split state from narrative

Plan: [`implementation_plan.md`](implementation_plan.md) (audited; verdict **NO-GO as written · GO
conditional on F1 · F2 · F4** — all three landed before a byte was moved).

## What shipped

`sprint-status.yaml` carried **363,334 bytes of which 9,721 were state.** It is now **62,040 bytes**
(−83 %) of bare `key: status` rows, epic banners, doctrine comments, and a real `last_updated:` key.
Row narrative lives in `_bmad-output/history/<epic>/<key>.md`; the change log in
`_bmad-output/history/CHANGELOG.md`; `migration-manifest.json` maps every moved byte home.

| Stage | Moves | Board after |
|---|---|---|
| 4.0 freeze — `.pre-split` (`-text`), baselines captured to files | — | 363,334 |
| 4.3 terminal rows | 199 tails | 140,952 |
| 4.4a CHANGE LOG + both stale `# last_updated` comments; real key promoted | 47 lines + 2 | 67,755 |
| 4.4b comments — 339 candidates triaged, reviewed, **all-KEEP** | 0 | 67,755 |
| 4.5 active rows over cap (moved whole; 9 under-cap dated rulings stay inline) | 10 tails | **62,040** |

**Every stage `verify --sha 0752c437` → byte-identical.** Reconstruction rebuilds the original from
(board + history + manifest) *without reading the blob*, then compares against
`git show 0752c437:<path>` — the LF stream, the only one identical on every machine.

## Suite Ledger

| Scope | Command | Result | Why this run |
|---|---|---|---|
| toolkit | `tests/run_all.py` | 5 files / 94 → **98** cases green | entry baseline, then after each ③ fix |
| board | `split_sprint_status.py verify --sha 0752c437` | byte-identical | after every stage, and again post-③ |
| project | `workflow_lint.py --project AGY_AVIATIONCHAT` | 0 errors, 3 warnings | identical to the 4.0 pre-migration baseline |
| project | `story_status.py check` | surfaces agree everywhere | dual-surface integrity |

Application stacks (`backend/` pytest, frontend vitest) are **out of scope and deliberately not run**:
the diff touches `.agents/`, `.claude/`, `.opencode/`, `.gitattributes` and `_bmad-output/` only — zero
application files. Stated rather than skipped silently.

---

## Code Review (2026-08-03)

**Verdict: PASS @ `d6e1a6db` (AGY) · `055401b`+ (lobby)**
Full-suite evidence measured on `d6e1a6db` by ③'s own run (there is no ② certification — this is a
`_main/` initiative track, not a story). Reconstruction re-verified at the same SHA.

**Scope** — Wave 4 across two repos: lobby `.agents/scripts/` (the tooling) + AGY `_bmad-output/` (the
migrated data) + 5 re-pointed commands and their vendored copies. Excluded as another session's work:
`_my_resources/migrations/**` and lobby `.gitattributes` (commits `e67f484`…`e45496e`).

**Method** — hunted the diff before re-reading the plan. Data integrity probed by execution
(manifest ↔ filesystem reconciliation), not by reading. **Honest limitation: this is not a clean room.**
I wrote the code under review in this same session, so builder's bias cannot be zeroed out by
instruction. Compensating: every finding below was produced by *running* something — ruff, a constant
census, a manifest/filesystem diff, the gate receipts — not by re-reading my own prose. A genuinely
independent ③ on a different model would still be worth having on the split tool.

**Deviations from the command, stated not buried**
- Step 0 binds `Projects/AGY_AVIATIONCHAT`, but the majority of the diff is **lobby** code. The command
  assumes a child-project story; this is a two-repo `_main/` track. Reviewed both surfaces.
- No worktree (Step 0.5) and no `_artifacts/epic_<E>/<story>/` — correct for a `_main/` track per
  `followon-fixes-are-not-a-new-story`; the verdict lands in this initiative walkthrough instead.
- Steps 3.2–3.5 (`bmad-testarch-trace` / `nfr` / `test-review`) target application code against
  `l1_coverage_min`; there is no application code in this diff. Not run, and that is a scope fact,
  not a skipped gate.
- Review layers ran **inline in this context rather than as parallel subagents** — permitted
  explicitly by the subagent-failure contract ("a lens is a prompt, not a privileged tool; losing the
  parallelism costs time, not coverage"). No layer went unexamined, so the CONCERNS cap does not apply.

### Findings

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| R1 | `split_sprint_status.py:50` + `workflow_lint.py:274` | **MED** | `NOTE_CAP = 120` declared **twice** — the splitter DECIDES by it, the lint JUDGES by it. Change one and the migration emits a board that fails its own gate. Identical to audit F3, in the same file pair, and `wf_common`'s own docstring already argues why it is fatal. | ✅ **Fixed** — single `wf.NOTE_CAP`; both import it |
| R2 | `split_sprint_status.py:335` | **MED** | `stage_changelog` fell back to a **hardcoded `'2026-08-03'`** when no `# last_updated:` comment existed to inherit. Every future project's migration would stamp the day this tool was written into the one field a reader trusts for staleness. | ✅ **Fixed** — takes the source commit's date (`%cs`). AGY inherited its real comment, so the migrated board is unaffected |
| R5 | `gate_receipt.py:73` | **MED** | `workflow_lint` exits 1 for warnings and 2 for errors, but every non-zero collapsed to `fail` — so the lint receipt read `lint fail exit=1` on a run with **zero errors**. A verdict citing that either blocks honest work or gets ignored: audit F4's shape, and precisely the exit-1-vs-exit-2 ambiguity the Wave 4 audit left open under "Four gates". | ✅ **Fixed** — fourth result `warn` via `--warn-exit N`; non-blocking, never a pass. Three controls incl. **2d: exit 2 is still `fail`** (no laundering) and **2e: no flag, no behaviour change** |
| R3 | `workflow_lint.py:296` | LOW | `check_board_note_budget` emitted one error per violating row — 199 on an unmigrated board. A flood mutes a check exactly as silence does; that is the muting failure this wave keeps guarding against. | ✅ **Fixed** — capped at 10, remainder **counted** never dropped; own test case |
| R4 | `split_sprint_status.py:112`, `workflow_lint.py:299` | LOW | `wf._KEY_RE` (private) reached from two other modules. | ✅ **Fixed** — promoted to public `KEY_RE`, private name kept as alias |
| R6 | `gate_receipt.py:73` | LOW | The `warn` change shipped with no provenance marker — a §1 comment-contract gap in a non-obvious block. | ✅ **Fixed** — provenance + an `AIDEV-NOTE` pinning why it is one code, not a set |
| — | `split_sprint_status.py` ×4, `test_split_sprint_status.py` ×1 | INFO | `PLW1510` — `subprocess.run` without `check=`. | **Dismissed with rationale** — every site inspects `returncode` and dies with the real stderr, which is strictly more useful than a `CalledProcessError` |
| — | `story_status.py:121`, `test_story_status.py:97` | INFO | `DTZ011` — `date.today()` without tz. | **Dismissed** — a board date stamp is a local calendar date; UTC would be wrong at the edges |

### Gate results — each citing its receipt

```
        lint  warn       exit=1    d6e1a6db
 reconstruct  pass       exit=0    d6e1a6db
status-drift  pass       exit=0    d6e1a6db
       suite  pass       exit=0    d6e1a6db
```

- `suite: pass @ d6e1a6db` (`gates/wave-4-board-split/suite.json`) — 5 files / **98 cases**, 24.3 s
- `reconstruct: pass @ d6e1a6db` — byte-identical to `0752c437:<board>` (363,334 B)
- `status-drift: pass @ d6e1a6db` — frontmatter and board agree everywhere
- `lint: warn @ d6e1a6db` — **0 errors, 3 warnings**, all three pre-existing and none from Wave 4:
  two rule-pointer warnings on `sudo-update-scrum-board.md` (another session's file) and 19.1's
  implementation plan 1.4× over budget (flagged in the Wave 1 audit). Byte-identical to the 4.0
  pre-migration baseline — this is the *warn* state R5 created so the evidence reads honestly.

### Clean-Code Gate

Machine floor: `python -m ruff check` on the 7 changed scripts. **The lobby has no ruff config**, so
this is ruff's *default* rule set, not the project's floor (AGY's ruff gate binds `backend/`) — stated
because a default-config run is weaker evidence than a configured one, and pretending otherwise is the
kind of fake green `tests-must-gate-for-real` exists to stop.

```
.agents\scripts\split_sprint_status.py:76:9: PLW1510 `subprocess.run` without explicit `check`
.agents\scripts\split_sprint_status.py:82:9: PLW1510 ...
.agents\scripts\split_sprint_status.py:416:9: PLW1510 ...
.agents\scripts\split_sprint_status.py:424:9: PLW1510 ...
.agents\scripts\tests\test_split_sprint_status.py:67:9: PLW1510 ...
Found 5 errors.
```

Down from 28 (structural findings fixed: `ISC004` implicit concat — which is what surfaced R2 —
`SIM102`, `PLC3002`). The 5 survivors are the dismissed `PLW1510` set above. Remaining findings in
`test_workflow_lint.py`, `wf_common.py` and `workflow_lint.py:77` are **inherited Wave 1/3 debt on
untouched lines** — noted, not gated on, per the diff-scoping rule.

Comment contract (§1): no banned patterns (`except:`, commented-out code, unowned TODO) in new code;
provenance carried throughout via `Wave 4 / audit Fn` references; no `AIDEV-*` anchor was invalidated
or rewritten. R6 was the one gap and is fixed.

### Data integrity (probed, not assumed)

```
stages: ['terminal','changelog','comments','active'] | spans: 3 | tails: 209 | insertions: 1
history .md files: 210   empty: 0
manifest dests: 210      missing: []      orphans: []
longest surviving inline note: 90 chars (cap 120)
```

209 tails = 199 terminal + 10 active. 3 spans = 1 changelog + 2 stale `last_updated` comments.
Manifest and filesystem reconcile exactly in both directions.

### Changes applied

Six findings fixed in-review across four commits (`ed531e1`, INDEX correction, `055401b`, R6), each
re-tested; suite 94 → **98** cases. Reconstruction re-verified byte-identical after every fix. All
four repos clean and `0 0` with origin.

## Your Actions

- [ ] **Operator — the live test.** The next real story's `/sudo-update-sprint-memory` exercises the
      CHANGELOG re-point and the automatic note-drop end to end. Nothing else proves those two.
- [ ] **Operator — drop `.pre-split`** after one sprint (364 KB, `-text`, in `_bmad-output/`).
- [ ] **⏳ Standing:** remove `--advisory` from the close-out receipt gate at the close of the first
      full sprint (ruling 2026-08-02, unchanged by this wave).
- [x] Independent-③ caveat recorded rather than papered over — see **Method** above. *(agent)*
- [x] Fresh/NEXgen boards are pre-split and exempt from the note rules until they migrate; the check
      fails safe on a project with no `_bmad-output/history/`. *(agent, tested)*
