# Run A2 — incumbent `bmad-code-review` (steps 2–4 under the run-to-completion rule)

Layers: 4/4 ok (blind, edge, acceptance, test-adequacy — parallel subagents).
Triage per vendor step-03: 37 raw → 27 unique (9 merges + 1 family fold), classified.

**Summary: 3 decision-needed · 20 patch · 3 defer · 1 dismissed.**

| # | src | title | loc | sev | bucket |
|---|---|---|---|---|---|
| 1 | blind+edge+acceptance | Tracking-state mismatches read ARMED: script rm'd from index w/ flag tracked; flag rm'd from disk while hooks read disk; violates AC2 | hooks_armed.py:174 | important | patch |
| 2 | blind | ARM_FLAGS `via` dispatcher hook never validated — gate+flag tracked, dispatcher untracked → ARMED, nothing dispatches | hooks_armed.py:64,174 | important | patch |
| 3 | blind+edge+acceptance | NOT CLEAR verdict branch unreachable dead code | task_preflight.py verdict | important | patch |
| 4 | blind+edge | Tests D/F/N chmod-based, red on Windows | test_hooks_armed.py:104 | important | patch |
| 5 | blind+edge | pathspec `.githooks/*` crosses `/` — nested/non-hook tracked files become required executables | hooks_armed.py:121 | important | patch |
| 6 | blind+edge | non-repo `--repo` misdiagnosed "no hooks tracked" | hooks_armed.py:71 | suggestion | patch |
| 7 | blind | claims_gates reads filesystem not index (test P depends on it) | hooks_armed.py:128 | suggestion | decision_needed |
| 8 | blind+edge | unset hooksPath → N+1 errors printing "(None)" | hooks_armed.py:150 | suggestion | patch |
| 9 | blind | cases A/Q assert live per-machine state — fresh clone = red | test_hooks_armed.py:79 | suggestion | decision_needed |
| 10 | blind | case Q hardcodes --expect-key SCC-110 AND ignores exit code | test_hooks_armed.py:264 | suggestion | patch |
| 11 | blind+test | CLI exit contract unasserted: case J discards rc (vacuously passes if CLI crashes); warn-only exit-1 path never driven | hooks_armed.py:273 | important | patch |
| 12 | blind | POSIX-only remedies (`touch`, `chmod +x`) printable on Windows | hooks_armed.py:182 | nitpick | patch |
| 13 | blind | `check(repo, rep)` — untyped rep crossing module boundary | hooks_armed.py:211 | nitpick | patch |
| 14 | blind | preflight JSON nests hooks.hooks + duplicates armed bool | task_preflight.py:321 | nitpick | patch |
| 15 | blind | INDEX.md trailing space in backticks + single-paragraph wall duplicating docstring | .agents/scripts/INDEX.md:9 | nitpick | patch |
| 16 | edge | `~` in core.hooksPath not expanded → false NOT ARMED | hooks_armed.py:145 | suggestion | patch |
| 17 | edge | CLI exit(2) vs check() WARN disagree on never-claimed repo | hooks_armed.py:236 | suggestion | decision_needed |
| 18 | acceptance | AC6 pins `--global` remedy the code deliberately rejects; spec never amended | hooks_armed.py REMEDY | important | patch |
| 19 | acceptance | AC3 extraction not performed; 57/57 invariant moved (documented deviation) | test_main_push_gate.py | suggestion | defer |
| 20 | acceptance | no-.githooks repo still gets "clear" line (spec said FAILURE never a pass) — pinned intended by test L | task_preflight.py | suggestion | dismiss |
| 21 | acceptance | walkthrough 59/59 vs 58/58 self-contradiction | walkthrough | nitpick | defer |
| 22 | acceptance | test_closeout_preflight.py never evidenced bare | walkthrough gates | nitpick | defer |
| 23 | test | is_executable() nt branch zero coverage on any platform | hooks_armed.py:112 | important | patch |
| 24 | test | hooks_armed --json shape untested | hooks_armed.py:263 | suggestion | patch |
| 25 | test | assertions couple to prose msg text instead of machine `code` field | test_hooks_armed.py | suggestion | patch |
| 26 | test | absolute core.hooksPath branch untested | hooks_armed.py:165 | suggestion | patch |
| 27 | test | git_root() fallback/subdir path untested | hooks_armed.py:91 | nitpick | patch |

Trial containment: findings are evidence, not fixes — nothing applied (landed history).
