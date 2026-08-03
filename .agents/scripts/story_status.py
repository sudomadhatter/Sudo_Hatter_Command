"""story_status.py — atomic story-status writer + drift detector (Wave 1.2).

Story status lives on TWO surfaces (story frontmatter + sprint-status.yaml board key)
with no enforcement of agreement; the drift class has 3 memory entries and recurred on
21.8b (2026-08-02: file `review`, board `ready-for-dev`). This script kills it:

    story_status.py check [--project P]              # list every drifted story; exit 1 if any
    story_status.py get   <id> [--project P]
    story_status.py set   <id> <status> [--project P] [--reconcile] [--force]

`set` writes BOTH surfaces in one operation or neither. It refuses when the two surfaces
already disagree (pass --reconcile to overwrite both with the new value), and refuses
downgrades from `done` and entry into descoped/deferred states (pass --force — those are
operator rulings, not routine flips).

Byte-preserving edits: only the status token on the matched line changes; inline comments,
CRLF/LF, and any pre-existing mojibake bytes survive untouched (surrogateescape round-trip).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wf_common as wf


def resolve_key(project: Path, story_id: str) -> str:
    board = wf.parse_board(wf.read_text(project / wf.BOARD_REL))
    keys = [k for k in board if wf.is_story_key(k)]
    want = wf.norm_id(story_id)
    exact = [k for k in keys if wf.norm_id(k) == want]
    if exact:
        return exact[0]
    prefixed = [k for k in keys if wf.norm_id(k).startswith(want + "-")]
    if len(prefixed) == 1:
        return prefixed[0]
    if not prefixed:
        wf.die(f"no board key matches '{story_id}'")
    wf.die(f"'{story_id}' is ambiguous: {prefixed}")
    raise AssertionError


def cmd_check(project: Path) -> int:
    drift = wf.status_drift(project)
    if not drift:
        print(f"[OK] {project.name}: story frontmatter and board agree everywhere")
        return 0
    for d in drift:
        print(f"[DRIFT] {d['key']}: board={d['board']} vs "
              f"frontmatter={d['frontmatter']}  ({d['file']})")
    print(f"-- {len(drift)} drifted; fix each with: story_status.py set <id> <status> --reconcile")
    return 1


def cmd_get(project: Path, story_id: str) -> int:
    key = resolve_key(project, story_id)
    board = wf.parse_board(wf.read_text(project / wf.BOARD_REL))
    files = wf.find_story_files(project, key)
    fm = wf.frontmatter_status(wf.read_text(files[0])) if len(files) == 1 else "(no file)"
    print(f"{key}: board={board[key]['status']}  frontmatter={fm}")
    return 0


def cmd_set(project: Path, story_id: str, new_status: str,
            reconcile: bool, force: bool) -> int:
    key = resolve_key(project, story_id)
    board_path = project / wf.BOARD_REL
    board_text = wf.read_exact(board_path)
    board = wf.parse_board(board_text)
    cur_board = board[key]["status"]

    files = wf.find_story_files(project, key)
    if len(files) != 1:
        wf.die(f"{key}: expected exactly one story file, found {len(files)} "
               f"({[f.name for f in files]})")
    story_path = files[0]
    story_text = wf.read_exact(story_path)
    cur_fm = wf.frontmatter_status(story_text)
    if cur_fm is None:
        wf.die(f"{story_path.name}: no `Status:` line in frontmatter")

    # ── Refusals (each is a documented incident class, not caution theater) ────
    if wf.norm_id(cur_fm) != wf.norm_id(cur_board) and not reconcile:
        wf.die(f"{key} is DRIFTED (board={cur_board}, frontmatter={cur_fm}) - "
               f"re-run with --reconcile to overwrite BOTH with '{new_status}'")
    if new_status not in wf.ALL_STATUSES:
        wf.die(f"unknown status '{new_status}' (known: {sorted(wf.ALL_STATUSES)})")
    if new_status not in wf.STATUS_RANK and not force:
        wf.die(f"'{new_status}' is a RULING state, not a flow state - pass --force "
               f"only when the operator ruled it")
    if cur_board in wf.TERMINAL and new_status != cur_board and not force:
        wf.die(f"{key} is terminal ({cur_board}) - never downgrade without --force")
    if (cur_board in wf.STATUS_RANK and new_status in wf.STATUS_RANK
            and wf.STATUS_RANK[new_status] < wf.STATUS_RANK[cur_board] and not force):
        wf.die(f"refusing downgrade {cur_board} -> {new_status} (pass --force)")

    # ── Compute both new texts BEFORE writing either ───────────────────────────
    new_story = re.sub(r"^(Status:\s*)(.+?)\s*$", rf"\g<1>{new_status}",
                       story_text, count=1, flags=re.MULTILINE)
    key_re = re.compile(rf"^(  {re.escape(key)}:\s*)([a-z0-9-]+)(.*)$", re.MULTILINE)
    new_board, n = key_re.subn(rf"\g<1>{new_status}\g<3>", board_text, count=1)
    if n != 1:
        wf.die(f"board line for '{key}' not found for rewrite (parse drift?)")

    # An inline history note describes the OLD transition; carrying it past a flip would
    # make it a lie. Dropped on purpose - but never silently (git holds the original).
    note = (m.group(1) if (m := re.search(r"^Status:[^#\n]*#\s*(.+?)\s*$",
                                          story_text, re.MULTILINE)) else None)
    if note:
        print(f"[NOTE] dropping stale inline note from {story_path.name}: {note}")

    # ── Write both or neither (restore the first on a second-write failure) ────
    wf.write_exact(story_path, new_story)
    try:
        wf.write_exact(board_path, new_board)
    except BaseException:
        wf.write_exact(story_path, story_text)  # roll back surface one
        print(f"[ROLLBACK] board write failed - {story_path.name} restored to "
              f"'{cur_fm}'; NEITHER surface changed")
        raise

    # Post-write proof, never assumed.
    left = wf.status_drift(project)
    still = [d for d in left if d["key"] == key]
    state = "AGREE" if not still else f"STILL DRIFTED {still}"
    print(f"[SET] {key}: board {cur_board} -> {new_status}, "
          f"frontmatter {cur_fm} -> {new_status}  [{state}]")
    return 0 if not still else 2


def main() -> int:
    ap = argparse.ArgumentParser(description="Atomic story-status writer (Wave 1.2)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_check = sub.add_parser("check"); p_check.add_argument("--project")
    p_get = sub.add_parser("get")
    p_get.add_argument("id"); p_get.add_argument("--project")
    p_set = sub.add_parser("set")
    p_set.add_argument("id"); p_set.add_argument("status")
    p_set.add_argument("--project")
    p_set.add_argument("--reconcile", action="store_true",
                       help="overwrite BOTH surfaces even if they currently disagree")
    p_set.add_argument("--force", action="store_true",
                       help="allow downgrades / ruling states (operator call)")
    args = ap.parse_args()

    project = wf.resolve_project_root(args.project)
    if args.cmd == "check":
        return cmd_check(project)
    if args.cmd == "get":
        return cmd_get(project, args.id)
    return cmd_set(project, args.id, args.status, args.reconcile, args.force)


if __name__ == "__main__":
    sys.exit(main())
