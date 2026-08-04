# scripts — INDEX

Maintenance scripts (MASTER here): `check_maps.py` (drift linter), `generate_repo_map.py` (repo-map generator), `sync-agents.ps1` (toolkit sync), `new-project.ps1` (workspace scaffolder), `generate_doc_graph.py` (doc graph). Mirrored to project vendored copies via `/sync-agents`.

**Workflow-enforcement scripts** (Wave 1, 2026-08-03) — these turn checklist prose into executable checks, so a command can say "run the check" instead of asking an agent to hold eight invariants in its head. Stdlib-only Python 3.11, no `yq`/`jq`.

| Script | Answers | Typical call |
|---|---|---|
| `wf_common.py` | shared paths, board parsing, drift detection, git helpers | (imported, not run) |
| `workflow_lint.py` | is the toolkit + a project self-consistent? | `workflow_lint.py --project AGY_AVIATIONCHAT` |
| `story_status.py` | do a story's TWO status surfaces agree — and flip both atomically | `story_status.py set 21.8b done` |
| `gate_receipt.py` | did this gate actually run, at this commit? | `gate_receipt.py run --story 21.8b --gate ruff -- ruff check backend/` |
| `closeout_preflight.py` | is this story safe to close out? | `closeout_preflight.py --story 21.8b --project AGY_AVIATIONCHAT` |

`gate_receipt.py` has no `--result` flag by design: it EXECUTES the gate and writes the receipt from the real exit code, so a verdict cannot be handed in. All flags precede `--`; everything after it is the gate command verbatim. Staleness compares **trees, not SHAs** — a branch that lands via a merge commit has a new HEAD and identical content, and calling that stale is how a hard gate earns a permanent `--advisory`.

`workflow_lint.py --staged [--fix]` is the **pre-commit encoding gate** (Wave 5): staged files only, encoding only, so it stays fast enough not to get disabled. Install it per clone with `git-hooks/install-encoding-hook.ps1 [-All]` — `.git/` never travels, so every machine installs once. It refuses to clobber an existing `pre-commit` hook, and `scripts/git-hooks/DISABLE` (untracked) is the kill switch. `--fix` repairs only *unambiguous* cp1252 round-trips; everything less certain is reported, never rewritten.

Tests: `python .agents/scripts/tests/run_all.py` (64 cases, stdlib only, no pytest). One test file per script. Each script is covered by the defect that motivated it, plus a positive control — a checker that reports nothing looks identical whether it is clean or dead, and a checker that reports *everything* gets muted. Both failures are represented.

## Top-level contents
<!-- auto-listed by /update-maps-indexes — refresh via /update-maps-indexes; do not hand-edit entries -->
- `__pycache__/`
- `check_maps.py`
- `check-repo-map-drift.ps1`
- `generate_doc_graph.py`
- `generate_repo_map.py`
- `new-project.ps1`
- `sync-agents.ps1`
