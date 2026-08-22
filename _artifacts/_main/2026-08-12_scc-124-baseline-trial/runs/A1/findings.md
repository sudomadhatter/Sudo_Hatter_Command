# Run A1 — incumbent `bmad-code-review` (steps 2–4 under the run-to-completion rule)

Layers: 4/4 ok (blind, edge, acceptance, test-adequacy — parallel subagents).
Triage per vendor step-03: normalized, deduped (33 raw → 29 unique; 4 merges), classified.

**Summary: 3 decision-needed · 20 patch · 5 defer · 1 dismissed.**

| # | src | title | loc | sev (asserted) | bucket |
|---|---|---|---|---|---|
| 1 | blind+edge | Tests D/F/N chmod-based, guaranteed red on Windows | test_hooks_armed.py:103 | important | patch |
| 2 | blind+edge | git-rm'd gate script w/ tracked flag reads ARMED (vacuous green twin of H2) | hooks_armed.py:174 | important | patch |
| 3 | blind | NOT CLEAR verdict branch unreachable (BLOCKED always wins) | task_preflight.py verdict | important | patch |
| 4 | blind | scan() early-return on empty expected skips layers 2–3 | hooks_armed.py:132 | important | patch |
| 5 | blind+edge | pathspec `.githooks/*` crosses `/`; subdir/README → false NOT-EXECUTABLE block | hooks_armed.py:121 | suggestion | patch |
| 6 | blind | CLI exit(2) vs check() WARN disagree on never-claimed repo | hooks_armed.py:251 | suggestion | decision_needed |
| 7 | blind | unset hooksPath cascades N+1 errors, misleading "(None)" text | hooks_armed.py:150 | suggestion | patch |
| 8 | blind | claims_gates reads filesystem while module doctrine is "the index" (test P depends on it) | hooks_armed.py:128 | suggestion | decision_needed |
| 9 | blind | Test Q hardcodes --expect-key SCC-110 against live repo | test_hooks_armed.py:264 | nitpick | patch |
| 10 | blind+test | live-repo cases A/Q couple hermetic suite to machine state (fresh clone = red) | test_hooks_armed.py:80 | suggestion | decision_needed |
| 11 | blind | git_root() fallback misreports non-repo as "no hooks tracked" | hooks_armed.py:71 | nitpick | patch |
| 12 | blind | preflight JSON nests hooks.hooks; flags list under-counts orphans | task_preflight.py json | nitpick | patch |
| 13 | blind | SOP re-pins a hardcoded suite census (646/16) that will restale | workflows_testing_SOP.md:1248 | nitpick | defer |
| 14 | edge | `~` in core.hooksPath not expanded → valid armed setup reads NOT ARMED | hooks_armed.py:145 | important | patch |
| 15 | edge | missing-flag remedy prints `touch` — does not exist on Windows | hooks_armed.py:180 | suggestion | patch |
| 16 | edge | git binary absent → uncaught FileNotFoundError traceback | hooks_armed.py:93 | suggestion | patch |
| 17 | acceptance | AC3 extraction rejected-on-evidence; plan artifact never amended, 57/57 invariant moved | test_main_push_gate.py | important | defer |
| 18 | acceptance | AC6: `--global` remedy removed vs spec; case B substring assertion can't prove remedy printed | hooks_armed.py REMEDY | important | patch |
| 19 | acceptance | Step 6 named test_closeout_preflight.py bare — absent from gate evidence | walkthrough gates | important | defer |
| 20 | acceptance | no-gates repo still gets unqualified "clear" line (spec said FAILURE, never a pass) | task_preflight.py verdict | suggestion | dismiss — pinned intended (test L), policy call recorded in landed walkthrough |
| 21 | acceptance | AC4 fixture (hooksPath unset) never driven e2e through preflight stdout | test_task_preflight.py | nitpick | patch |
| 22 | acceptance | walkthrough claims 59/59 AND 58/58 for same suite | walkthrough | nitpick | defer |
| 23 | acceptance | AC7 pins 15/15; shipped evidence 16/16 | plan | nitpick | defer |
| 24 | test | CLI exit-code contract 0/1/2 untested (case J discards rc) | hooks_armed.py main() | important | patch |
| 25 | test | git_root() subdir walk-up — applied review fix with no regression test | hooks_armed.py git_root | important | patch |
| 26 | test | is_executable() nt branch untested on any platform | hooks_armed.py | important | patch |
| 27 | test | absolute core.hooksPath branch untested | hooks_armed.py scan | suggestion | patch |
| 28 | test | hooks_armed --json branch never runs in tests | hooks_armed.py main | suggestion | patch |
| 29 | test | rewritten dual-cause error text unasserted (old substring only) | test_task_preflight.py:188 | nitpick | patch |

Trial containment: findings are evidence, not fixes — nothing applied (landed history). No story
status exists to touch; stop at presentation per the run-to-completion rule.
