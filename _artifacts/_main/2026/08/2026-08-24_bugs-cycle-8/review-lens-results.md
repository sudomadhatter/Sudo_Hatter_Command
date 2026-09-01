# SCC-305 review — raw lens returns (persisted for compaction; triage pending)

Session state at persist time (2026-08-24):
- Flow position: /smh-code-review Step 1 — lens fan-out IN FLIGHT. 2 of 5 returned (below).
- Outstanding lenses (background agents, results will arrive as task-notifications):
  edge-case-hunter, literal-correctness-hunter, test-adequacy-auditor.
- Steps already done: 0/0.5/0.7 (nothing landed on main; 0 overlap; merge-tree clean; no sibling
  lanes; review_level=standard), 0.9 (review-runtime: fan-out), Step 3 gates ALL GREEN
  (suite inherited PASS @ 046294b2 via gates/suite.json; lint 0 err/0 warn/8 info; links clean;
  sop_currency exit 0; assertions 7/7+4/4+19/19; py_compile ok; door parity n/a).
- Remaining: triage all 5 lens returns (dedupe by anchor), fix survivors in thread, Step 2
  acceptance matrix (import Acceptance Auditor), Step 3.5 fold, Step 4 verdict section appended
  to walkthrough.md (lenses_run/dispositions/drift lines, Step 0.7 sub-heading), Step 5 refresh,
  then jira_feed.py devrecord --key SCC-305 --stage quick-dev.
- HEAD at review start: ef5de92. Branch chore/SCC-305-bugs-cycle-8, pushed 0 0.

## Lens: acceptance-auditor (returned ok)

Per-item: A DELIVERED · B DELIVERED · C DELIVERED · D DELIVERED · E DELIVERED · F DELIVERED ·
G PARTIAL (G3 only: walkthrough.md did not exist when the lens read the tree — it was written
minutes later and carries the G3 sibling-commands line; closes on re-check) · H1 DELIVERED ·
H2 DELIVERED · I DELIVERED.

DRIFT rows it reported:
1. docs/doc-graph.json + docs/doc-graph.md regenerated (701→704 edges) — undeclared; benign
   (pre-commit maps hook regenerates them; keep, name why).
2. 7 sync-cache files undeclared (.claude/rules/code-standards.md, .claude/skills/code-review-
   engine/steps/step-01-review.md, .opencode/commands/{cicd-code-review,cicd-dev-story-tests,
   smh-quick-dev,smh-quick-fix}.md, .agents/.sync-manifest.json) — byte-mirrors of declared
   source edits, produced by the declared sync step; keep, name why.
3. Declared-but-absent: .agents/workflows/{smh-quick-dev,cicd-dev-story-tests,cicd-code-review}.md
   — thin launchers, sync had nothing to regenerate; unused declarations (unimplemented rows).
4. SOP rows were used (predicted unused) — not drift.

## Lens: blind-hunter (returned ok) — 17 findings verbatim-condensed

1. cicd-code-review.md:371-399 | important | prose says _artifacts/-only commit leaves cert
   valid while the stated arbiter is literally `git diff --quiet <sha> <HEAD>` (same_tree),
   which such a commit fails → contradiction inside my new F text.
2. memory_store_check.py:106-126 | important | check_delta overwrites the baseline BEFORE the
   report is acted on — one-shot shout; a confirming re-run is silent and evidence is gone.
3. memory_store_check.py | suggestion | delta compares NAMES only; content REVERT with same
   names is unguarded while docstring claims "remove or revert".
4. gate_receipt.py lane_receipts_root | suggestion | --cwd outside ANY git repo falls back to
   main checkout silently (top empty → return project); bad-path typo recreates SCC-317.
5. gate_receipt.py -q pattern | suggestion | MULTILINE over whole output; inner pytest-style
   line from a meta-test could be quoted as totals for the outer gate.
6. link-worktree-assets.py other_linked_worktrees | suggestion | counts EVERY registered
   worktree, not only asset-linked ones → block may never be removed (X4 holds only in lab).
7. step-01-review.md recipe | important | recipe symlinks SHARED venv into lens trees (write
   surface) and never removes lens worktree registrations (pollutes `git worktree list`).
8. step-01-review.md | suggestion | lens copies cut at story-sha; uncommitted builder changes
   invisible; no clean-tree requirement stated.
9. jira.md:250 | important | `labels IN (a,b)` is OR; post-handoff TWO open tickets match and
   the row says "find the open one" with no tiebreak (file into STARTED cycle = bugs-and-updates
   one; successor holds baton only) — needs one tiebreak sentence.
10. test_gate_receipt.py W4 | suggestion | `repo.name in out` vacuous: fixture named "repo" and
    die message contains the word "repo" in prose → names-both-trees only half-pinned.
11. test_memory_store_check.py I5 | suggestion | hook checks are bare substring greps —
    commented-out call or early exit 1 passes.
12. link-worktree-assets.py _split_managed_block | suggestion | missing END sentinel absorbs
    user content below BEGIN into the managed block (deleted on removal) and drops last line.
13. link-worktree-assets.py write_exclude_entries | suggestion | shared-file read-modify-write
    without locking; concurrent lane links can lose entries (intermittent SCC-310 symptom).
14. .githooks/post-* + I-5 claim | important | hooks ship lobby-only; the three project repos'
    stores get no hook coverage while SOP/changelog say "guarded now" — overclaim; scope the
    claim or note per-repo install owed.
15. cicd-dev-story-tests.md placeholder grep | suggestion | any legit `{{` in a story file
    (code sample) fails Step 5 forever; no escape hatch stated.
16. gate_receipt importer path | suggestion | close-out/preflight readers resolving receipts
    from the MAIN checkout won't find lane receipts (importer path untested here).
17. memory_store_check.py baseline corrupt-read | suggestion | JSON corrupt → previous=[] and
    immediate overwrite → silent exactly when storage misbehaves.

## Triage notes (pre-drafted, to finish after remaining lenses return)

Disposition discipline: code-standards §6.5 (REAL · BEHAVIOUR · THIS diff, all three YES to fix).
Likely fixes in thread: #2 (real: preserve evidence — only advance baseline when no regression,
or persist gone-set until acknowledged... simplest honest fix: report BEFORE overwriting and
keep the union/previous list when gone-files detected), #1 (rewrite the two sentences so the
_artifacts/ exemption is stated as the task_preflight code-fresh rule, not as same_tree magic),
#9 (add one tiebreak sentence to jira.md row: two rows during handoff window → file into the
bugs-and-updates one), #14 (scope the claim: hooks armed in the lobby; project repos covered
when their own .githooks gain the same shims — add Your Actions row or note), #4 (refuse when
--cwd is not inside any git working tree instead of silent fallback).
Likely dismiss/observe: #3 (names-only delta is the ticket's own acceptance c definition —
count dropped or row unresolved; content-revert explicitly out of scope; fix docstring wording
at most), #5 (theoretical; totals are quoted-verbatim by design), #6 (conservative keep is safe;
the block is harmless while any worktree exists), #8/#7 (recipe guidance; venv symlink is the
AVCH-34 working approach the ticket itself prescribes — add a read-only caveat sentence at most),
#10/#11 (test-strength suggestions; mutation sweep already killed the load-bearing mutants),
#12/#13 (edge cases outside this diff's acceptance; note), #15 (grep scope: acceptance says the
placeholder literals; `{{` is also the template's own fill syntax — could narrow to the DAR
section; judgment), #16 (out of this lane's diff — importer behavior unchanged by design,
receipts under --root/task lane unaffected; story-lane close-out reads worktree receipts via
--cwd... verify claim before dismissing), #17 (corrupt-baseline: same fix family as #2).

## Lens: test-adequacy-auditor (returned ok) — 11 findings

1. test_memory_store_check.py:117 | important | I3c never asserts the delta run's EXIT code —
   the `code = 2` decision is un-gated; a regression printing MISSING but returning 0 passes.
2. memory_store_check.py | important | (dup of blind #2 by anchor) baseline overwritten in the
   detecting run — one-shot shout; no test pins the SECOND run after damage.
3. test_memory_store_check.py:136 (I5) | important | source greps only: exec bit never checked,
   hook never executed (`sh -n` absent), `exit 0` grep can match a comment/early exit.
4. gate_receipt.py:125 | important | (dup of blind #4) `not top` → --cwd in NO git repo silently
   falls back to --project; only different-repo (W4) tested.
5. memory_store_check.py:131 | important | `if not store.is_dir(): return 0` applies to an
   EXPLICIT --store too — a typo'd --store path exits 0 silent; carve-out only justified for
   the hook's no-flag case.
6. test_gate_receipt.py:517 | suggestion | `sub = repo/"subdir"` is a DEAD FIXTURE — W3 passes
   --cwd str(repo), the subdir case was dropped untested.
7. test_memory_store_check.py:81 | suggestion | I2b equality not identity for INDEX_CAP —
   re-duplication would stay green.
8. test_link_worktree_assets.py:312 | suggestion | X1 doesn't assert anything was LINKED —
   ASSETS drift would make X1–X4 vacuously green (only sweep M4 distinguishes today).
9. link-worktree-assets.py:108 | suggestion | root-anchoring `"/" + r` un-gated by any case;
   unanchored entry would also hide real nested paths as dirt.
10. memory_store_check.py:101 | suggestion | (dup of blind #17) corrupt baseline → previous=[]
    → silent re-baseline; untested.
11. implementation_plan.md I-5 row | suggestion | (dup of blind #14) hooks lobby-only vs
    "all four stores covered" claim.

Cross-lens corroboration (same anchor, sorts to top of band):
- baseline one-shot overwrite (blind#2 + TA#2) x2 important
- --cwd non-repo silent fallback (blind#4 + TA#4) x2 (sugg+important)
- hooks lobby-only vs I-5 claim (blind#14 + TA#11 + plan row) x2 important
- I5 grep weakness (blind#11 + TA#3) x2
- corrupt baseline (blind#17 + TA#10) x2 suggestion

## Lens: edge-case-hunter (returned ok) — 12 findings

1. gate_receipt.py:60 | important | VERIFIED: -q regex fully matches "2 failed, retrying in 30s"
   and "3 passed checks done, next poll in 5s" — fabricated totals from progress/retry lines.
2. gate_receipt.py:76 | important | VERIFIED: _totals takes FIRST match; "3 passed in 1.0s" beats
   a later real "10 passed, 2 failed in 9.0s" — inner/first suite quoted as whole gate's totals.
   (Banner pattern never hit this: the banner is the run's final line.)
3. gate_receipt.py:60 | suggestion | "no tests ran in 0.12s" still unmatched (no leading count).
4. gate_receipt.py:131 | suggestion | non-git --project → common_proj empty → die blames --cwd
   ("DIFFERENT repo") for the project's missing .git — wrong flag blamed.
5. gate_receipt.py:455 | suggestion | receipts stamped under OLD behavior (in P) are orphaned:
   new check --cwd W looks only in W → NO RECEIPT for a valid receipt, one transition, no pointer.
6. link-worktree-assets.py:94 | important | VERIFIED: missing END sentinel absorbs user patterns
   below BEGIN into managed entries + drops file's last line; last-lane unlink then DELETES the
   user's own exclude patterns. (Corroborates blind #12, promoted by verification.)
7. link-worktree-assets.py:126 | suggestion | stale registered worktree (pruned-shell house trap)
   counts as "other" → block never removed (corroborates blind #6, TA anchor).
8. link-worktree-assets.py:106 | suggestion | non-UTF-8 legacy info/exclude → UnicodeDecodeError
   traceback AFTER symlinks created → lane linked-but-unexcluded + crash.
9. memory_store_check.py:104 | important | baseline one-shot overwrite (x3 now: blind#2, TA#2) +
   VS Code hides hook output → shout unseen, evidence gone; no --no-update/read-only re-ask.
10. memory_store_check.py:107 | important | FALSE ALARM class: legit checkout to an older branch
    in the MAIN checkout (routine) removes newer store files → full ⛔ shout exit 2 for a correct
    operation; also fires after every approved memory-audit retirement → ignored-in-a-week risk.
11. memory_store_check.py:107 | important | names-only delta: content REVERT with same names
    silent (corroborates blind #3, promoted to important by this lens).
12. memory_store_check.py:105 | suggestion | read-only git dir → baseline never established →
    delta permanently inert, indistinguishable from healthy; no warning.

## Lens: literal-correctness-hunter (returned ok) — 5 findings

Verified clean: wf.same_tree + gate_receipt.check_receipt exist as cited; --python-interpreter-path
is a real pyrefly flag; AGY pyrefly.toml states the no-pin rationale; both example bullets parse
1 entry / 0 incomplete; new JQL matches work-consolidation.md:77; hooks executable, flags match
argparse; -q regex matches both claimed forms; no stale SCC-190 pointers; template.md carries the
`{{...}}` placeholders the grep matches.

1. cicd-code-review.md:377 | important | (corroborates blind#1 → x2 important) prose says an
   `_artifacts/`-only commit "leaves the certification valid" while naming `same_tree` as the
   arbiter that "cannot disagree" — same_tree is a whole-tree diff with NO _artifacts carve-out;
   the guarantee is false the first time it is exercised (mirror .opencode identical).
2. cicd-dev-story-tests.md:340 | suggestion | `(2 fills:` literal exists NOWHERE in tree, packs,
   or the cited AGY incident story — half the "fixed literals" grep is unattested dead weight.
3. walkthrough.md:66 | suggestion | F1 evidence "grep -c same_tree … 0 → 2" does not reproduce —
   actual count 3; evidence figure drifted.
4. smh-quick-dev.md:242 (+quick-fix:68, step-01:675, mirrors) | suggestion | "per jira.md §labels"
   — no heading/anchor named "labels" exists; pointer resolves to nothing.
5. implementation_plan.md:180 | suggestion | (matches acceptance drift row 3) three
   .agents/workflows/* declared EDIT rows are thin launchers sync never rewrites — permanently
   `unimplemented` rows.

All 5 lenses returned. Triage executed in-session (see walkthrough Code Review section).
