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
| `split_sprint_status.py` | move board narrative to history, provably losslessly (Wave 4) | `split_sprint_status.py verify --sha <src> --project P` |

`split_sprint_status.py` ran the AGY migration 2026-08-03 (baseline `0752c437`): board 363,334 → 62,040 B in four staged applies, each `verify`d **byte-identical** by reconstructing the original from (board + history + manifest) — never peeking at the blob — and comparing against `git show <sha>:<path>`, the LF stream (the worktree stream varies by machine — `* text=auto`). Narrative now lives in `_bmad-output/history/<epic>/<key>.md` + `CHANGELOG.md`; the board carries bare `key: status`, a ≤120-char note on live rows only, enforced by `workflow_lint.check_board_note_budget` (a note on a `NO_NOTE_STATUSES` row is an ERROR; `story_status.py set` drops it on the flip automatically).

`gate_receipt.py` has no `--result` flag by design: it EXECUTES the gate and writes the receipt from the real exit code, so a verdict cannot be handed in. All flags precede `--`; everything after it is the gate command verbatim. Staleness compares **trees, not SHAs** — a branch that lands via a merge commit has a new HEAD and identical content, and calling that stale is how a hard gate earns a permanent `--advisory`.

`workflow_lint.py --staged [--fix]` is the **pre-commit encoding gate** (Wave 5): staged files only, encoding only, so it stays fast enough not to get disabled. Install with `git-hooks/install-encoding-hook.ps1 [-All]`. It resolves the hook dir from **`core.hooksPath`** first — the lobby, AGY and Fresh all set it to `.githooks`, so writing to `.git/hooks` installs a file git never reads; the first version of this installer did exactly that and reported success in three of four repos. It refuses to clobber a foreign `pre-commit` hook, and `scripts/git-hooks/DISABLE` (untracked) is the kill switch. `--fix` repairs only *unambiguous* cp1252 round-trips; everything less certain is reported, never rewritten.

A file that legitimately **carries** those bytes as data — the detector's own constants, its fixtures, a doc quoting them — declares `wf-lint: allow-encoding-literals` and is skipped. Without it the gate blocks every commit that touches the gate.

Tests: `python .agents/scripts/tests/run_all.py` (94 cases across 5 files, stdlib only, no pytest). One test file per script. Each script is covered by the defect that motivated it, plus a positive control — a checker that reports nothing looks identical whether it is clean or dead, and a checker that reports *everything* gets muted. Both failures are represented.

## Top-level contents
<!-- auto-listed by /update-maps-indexes — refresh via /update-maps-indexes; do not hand-edit entries -->
- `__pycache__/`
- `check_maps.py`
- `check-repo-map-drift.ps1`
- `generate_doc_graph.py`
- `generate_repo_map.py`
- `new-project.ps1`
- `sync-agents.ps1`
