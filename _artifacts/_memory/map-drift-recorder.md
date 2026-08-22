---
name: map-drift-recorder
description: "Commit-time recorder journals map/INDEX drift so the SessionStart nag + /update-maps-indexes (was /1_update-maps until 2026-07-14) arrive pre-scoped; machine-local cache, git-diff stays truth."
metadata: 
  node_type: memory
  type: project
  originSessionId: 495d159d-0caa-4c24-a8cf-a403d4584edc
---

Built 2026-07-06 (lobby). A `post-commit` hook (`.githooks/post-commit`, enabled per-repo via
`git config core.hooksPath .githooks`) calls `.agents/scripts/record_map_changes.py --commit HEAD`,
which classifies each commit's changes into the update-maps judgment categories (toolkit-change,
session-added, rename, toplevel-added, delete) and appends ONE line to `docs/.maps-journal.jsonl`.

**Consumers:** the SessionStart 4th hook (`record_map_changes.py --nag`) prints the classified tail since
the anchor; `/update-maps-indexes` (renamed from `/1_update-maps` 2026-07-14, see
the 2026-07-14 command restructure) Step 0.0 reads it for a pre-scoped worklist. `check_maps.py --set-anchor` now
also CONSUMES the journal (rolls reconciled lines into `.maps-journal-archive.jsonl` — a move, not a delete).

**Why:** the nag/workflow used to re-derive "what changed" from scratch every time; the journal caches the
classification so the agent (slow, token-costing layer) arrives knowing what needs what.

**How to apply:** it's a CACHE, never truth — every consumer runs a freshness guard (journal's last sha ==
HEAD?); if a commit bypassed the recorder (another machine, `--no-verify`, rebase) the nag says "behind HEAD"
and you fall back to `check_maps.py`'s `git diff <anchor>..HEAD` (ground truth). Journal is gitignored
(machine-local, like [[gitnexus-index-not-actually-live]]). Same verify-not-trust discipline as
[[gitnexus-verify-index-fresh-after-pull]].

**Owed:** propagation to `Projects/<name>` repos (each needs the vendored script + `.githooks/post-commit` +
`core.hooksPath` set) — MVP is lobby-only. Also fixed a pre-existing cp1252/emoji crash in `check_maps.py`'s
depth-3 SessionStart nag (added a UTF-8 stdout reconfigure; it was silently dying on any depth-3 drift here).
