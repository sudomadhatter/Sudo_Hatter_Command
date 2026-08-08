"""jira_feed.py must never invent ticket content, and must leave exactly ONE Dev Record.

The two defects this covers are the ones that motivated SCC-49 and the ones a hand-written
step reintroduces every time:

  * a ticket that reports success while carrying nothing (acli exits 0, the comment is not
    there) - covered by the `swallow` stub mode, the load-bearing negative here;
  * two Dev Records for one story, because /sudo-quick-dev closed the branch and then
    /sudo-update-sprint-memory closed the story and both posted.

Plus the positive control: a fully-fed ticket must report clean, or `check` is dead weight
that nobody will trust.

`acli` is stubbed. The stub is a real executable (shebang on POSIX, .bat on Windows) so the
production path - subprocess, --description-file, --json parsing, read-back - runs unchanged;
mocking at the Python level would prove nothing about the shape of what acli returns.
"""
from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path

from _harness import Cases, TempDir, run_script

BOARD_REL = Path("_bmad-output/implementation-artifacts/sprint-status.yaml")
EPICS_REL = Path("_bmad-output/planning-artifacts/epics.md")

STORY = """---
jira_key: TEST-7
Status: ready-for-dev
Epic: 9
bdd: locked
---

# Story 9.1: Widget Archive

## Story

As **an admin**,
I want **archived widgets to stay readable**,
so that **nothing is ever deleted.**

## Acceptance Criteria

- **AC-1 (archive):** archiving a widget sets `archived_at` and keeps the document.
- **AC-2 (list):** the roster hides archived widgets by default.

## Tasks
- do the thing
"""

STORY_NO_AC = """---
Status: ready-for-dev
---

# Story 9.2: Bare Story

## Story

As a nobody, I want nothing.

## Tasks
- none
"""

EPICS = """# Breakdown

## Epic List

### Epic 9: Widget Lifecycle
*Widgets get archived instead of deleted, everywhere.*

- 9.1 - Widget Archive
- 9.2 - Bare Story

---

### Epic 10: Something Else
*Not this one.*
"""

WALKTHROUGH = """# Walkthrough - 9.1

## Task Checklist
- [x] archive path

## Decisions made
- Archive is a flag, never a delete
- Roster filters server-side

## Pitfalls
- The list endpoint cached the pre-archive roster

## Code Review (2026-08-08)
Verdict: PASS @ abc1234
"""

STUB = r'''
import json, os, sys

state_path = os.environ["STUB_STATE"]
state = json.load(open(state_path, encoding="utf-8"))
args = sys.argv[1:]


def save():
    json.dump(state, open(state_path, "w", encoding="utf-8"))


def val(flag):
    return args[args.index(flag) + 1] if flag in args else None


def read(flag):
    p = val(flag)
    return open(p, encoding="utf-8").read() if p else ""


def adf(text):
    if not text:
        return None
    return {"type": "doc", "version": 1,
            "content": [{"type": "paragraph",
                         "content": [{"type": "text", "text": text}]}]}


head = args[:4]
if head[:3] == ["jira", "workitem", "view"]:
    print(json.dumps({"key": "TEST-7",
                      "fields": {"description": adf(state.get("description")),
                                 "summary": state.get("summary", "")}}))
elif head == ["jira", "workitem", "comment", "list"]:
    print(json.dumps({"comments": [{"id": c["id"], "body": adf(c["body"])}
                                   for c in state["comments"]]}))
elif head == ["jira", "workitem", "comment", "create"]:
    if not state.get("swallow"):
        state["comments"].append({"id": str(1000 + len(state["comments"])),
                                  "body": read("--body-file")})
        save()
    print("Comment added")
elif head == ["jira", "workitem", "comment", "update"]:
    for c in state["comments"]:
        if c["id"] == val("--id"):
            c["body"] = read("--body-file")
    save()
    print("Comment updated")
elif head[:3] == ["jira", "workitem", "search"]:
    print(json.dumps(state.get("search", [])))
elif head[:3] == ["jira", "workitem", "create"]:
    if not state.get("swallow_desc"):
        state["description"] = read("--description-file")
    state["create_args"] = args
    save()
    print("Created work item: TEST-99")
elif head[:3] == ["jira", "workitem", "edit"]:
    state["description"] = read("--description-file")
    state["edit_args"] = args
    save()
    print("Work item edited")
else:
    print("stub: unhandled " + " ".join(args), file=sys.stderr)
    sys.exit(9)
'''


def build(root: Path) -> tuple[Path, Path, Path]:
    """(project, acli-launcher, state-file)."""
    repo = root / "repo"
    (repo / BOARD_REL.parent).mkdir(parents=True)
    (repo / BOARD_REL).write_text("development_status:\n  9-1-widget: review\n",
                                  encoding="utf-8")
    (repo / EPICS_REL.parent).mkdir(parents=True)
    (repo / EPICS_REL).write_text(EPICS, encoding="utf-8")
    stories = repo / "_bmad/bmm/stories"
    stories.mkdir(parents=True)
    (stories / "story-9-1-widget.md").write_text(STORY, encoding="utf-8")
    (stories / "story-9-2-bare.md").write_text(STORY_NO_AC, encoding="utf-8")
    wt = repo / "_artifacts/epic_9/story-9-1-widget"
    wt.mkdir(parents=True)
    (wt / "walkthrough.md").write_text(WALKTHROUGH, encoding="utf-8")

    stub_py = root / "acli_stub.py"
    stub_py.write_text(STUB, encoding="utf-8")
    # A real executable on both machines: cmd.exe cannot run a shebang, /bin/sh cannot run
    # a .bat. Everything downstream of this is the production code path.
    if os.name == "nt":
        launcher = root / "acli.bat"
        launcher.write_text(f'@echo off\r\n"{sys.executable}" "{stub_py}" %*\r\n',
                            encoding="utf-8")
    else:
        launcher = root / "acli"
        launcher.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{stub_py}" "$@"\n',
                            encoding="utf-8")
        launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)
    return repo, launcher, root / "state.json"


def set_state(path: Path, **kw) -> None:
    state = {"description": "", "comments": [], "search": []}
    state.update(kw)
    path.write_text(json.dumps(state), encoding="utf-8")


def get_state(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    c = Cases("jira_feed")
    with TempDir() as tmp:
        repo, acli, state = build(tmp)

        def jf(*args: str) -> tuple[int, str]:
            os.environ["STUB_STATE"] = str(state)
            return run_script("jira_feed.py", args[0], "--project", str(repo),
                              "--acli", str(acli), *args[1:])

        # ── outline: rendered FROM the story file, never invented ──────────────
        code, out = jf("outline", "--story", "9.1", "--epic-key", "TEST-1", "--lane", "full")
        c.check("outline: exit 0", code == 0, out.strip()[:120])
        c.check("outline: carries the title", "Widget Archive" in out)
        c.check("outline: carries the story statement", "archived widgets to stay readable" in out)
        c.check("outline: carries both ACs",
                "AC-1 (archive)" in out and "AC-2 (list)" in out)
        c.check("outline: numbers the ACs", "1. AC-1" in out and "2. AC-2" in out)
        c.check("outline: points at the story file",
                "_bmad/bmm/stories/story-9-1-widget.md" in out)
        c.check("outline: carries the rulings",
                "Lane: full" in out and "Parallel-ok: no" in out and "Epic: TEST-1" in out)
        c.check("outline: carries the bdd record", "BDD: locked" in out)
        c.check("outline: drops non-bullet prose", "do the thing" not in out)

        code, out = jf("outline", "--story", "9.1", "--parallel-ok",
                       "--blocked-by", "TEST-4")
        c.check("outline: rulings reflect the flags",
                "Parallel-ok: yes" in out and "Blocked by: TEST-4" in out)

        # A story with no ACs must SAY so. Rendering a confident-looking outline with the
        # section quietly missing is the failure this whole script exists to prevent.
        code, out = jf("outline", "--story", "9.2")
        c.check("outline: no ACs -> says so, exit 0",
                code == 0 and "(none found in the story file)" in out, out.strip()[:160])
        c.check("outline: no ACs -> warns on stderr", "[WARN]" in out)

        code, out = jf("outline", "--story", "9.9")
        c.check("outline: unknown story -> exit 2", code == 2, out.strip()[:160])

        code, out = jf("outline", "--epic", "9")
        c.check("outline --epic: title + goal",
                code == 0 and "Epic 9 - Widget Lifecycle" in out
                and "archived instead of deleted" in out, out.strip()[:160])
        c.check("outline --epic: stops at the next epic", "Something Else" not in out)

        dest = tmp / "outline.txt"
        code, out = jf("outline", "--story", "9.1", "--out", str(dest))
        c.check("outline --out: writes the file",
                code == 0 and dest.is_file() and "Widget Archive" in dest.read_text(encoding="utf-8"))

        # ── devrecord: flags first, walkthrough scrape underneath ──────────────
        set_state(state)
        code, out = jf("devrecord", "--story", "9.1", "--key", "TEST-7",
                       "--decision", "Archive is a flag, never a delete",
                       "--followon", "Backfill the old rows")
        c.check("devrecord: scrapes the walkthrough's decisions",
                "Roster filters server-side" in out, out.strip()[:200])
        c.check("devrecord: scrapes the walkthrough's pitfalls",
                "cached the pre-archive roster" in out)
        c.check("devrecord: keeps the flag-supplied follow-on", "Backfill the old rows" in out)
        c.check("devrecord: does not duplicate a flag the walkthrough repeats",
                out.count("Archive is a flag, never a delete") == 1)
        c.check("devrecord: lifts the walkthrough verdict", "PASS @ abc1234" in out)
        c.check("devrecord: dry run posts nothing",
                code == 0 and get_state(state)["comments"] == [])

        code, out = jf("devrecord", "--story", "9.1", "--key", "TEST-7",
                       "--walkthrough", str(repo / "_artifacts/epic_9/story-9-1-widget/walkthrough.md"),
                       "--strict")
        c.check("devrecord --strict: empty bucket is a hard fail",
                code == 2 and "followons" in out, out.strip()[:200])

        # ── devrecord --apply: post, then PROVE it landed ──────────────────────
        set_state(state)
        code, out = jf("devrecord", "--story", "9.1", "--key", "TEST-7", "--apply",
                       "--outcome", "review -> done", "--followon", "none")
        c.check("devrecord --apply: exit 0 and one comment",
                code == 0 and len(get_state(state)["comments"]) == 1, out.strip()[:200])
        c.check("devrecord --apply: the comment carries the marker",
                "Dev Record - 9.1" in get_state(state)["comments"][0]["body"])

        # THE quick-dev requirement: quick-dev closes the branch and posts, then close-out
        # closes the story and posts. That must leave one record, not two.
        code, out = jf("devrecord", "--story", "9.1", "--key", "TEST-7", "--apply",
                       "--stage", "quick-dev", "--decision", "Second pass ruling",
                       "--followon", "none")
        after = get_state(state)["comments"]
        c.check("devrecord: a second post UPDATES, leaving exactly one record",
                code == 0 and len(after) == 1, f"{len(after)} comments")
        c.check("devrecord: the surviving record is the newer one",
                "Second pass ruling" in after[0]["body"] and "quick-dev" in after[0]["body"])
        c.check("devrecord: reports that it updated", "updated the existing" in out)

        code, out = jf("devrecord", "--story", "9.1", "--key", "TEST-7", "--apply",
                       "--append-new", "--followon", "none")
        c.check("devrecord --append-new: opts out of the one-record rule",
                code == 0 and len(get_state(state)["comments"]) == 2)

        # The load-bearing negative: acli exits 0 and records NOTHING. Indistinguishable
        # from success unless the ticket is read back.
        set_state(state, swallow=True)
        code, out = jf("devrecord", "--story", "9.1", "--key", "TEST-7", "--apply",
                       "--followon", "none")
        c.check("devrecord: silent acli no-op -> exit 2, not a false success",
                code == 2 and "NOT recorded" in out, out.strip()[:200])

        code, out = jf("devrecord", "--story", "9.1", "--apply", "--followon", "none")
        c.check("devrecord --apply without --key -> exit 2", code == 2, out.strip()[:120])

        # The command centre has no sprint board on purpose - toolkit chore work is not a
        # BMAD story - but it has tickets. A record must be fileable there or the one repo
        # where the workflow is built is the one repo whose tickets stay empty.
        chore = tmp / "boardless"
        (chore / "_artifacts/quick_fixes/quick-fix-1-1-thing").mkdir(parents=True)
        (chore / "_artifacts/quick_fixes/quick-fix-1-1-thing/walkthrough.md").write_text(
            "# Walkthrough\n\n## Pitfalls\n- The hook was never armed\n", encoding="utf-8")
        os.environ["STUB_STATE"] = str(state)
        code, out = run_script("jira_feed.py", "devrecord", "--project", str(chore),
                               "--acli", str(acli), "--story", "quick-fix-1.1-thing",
                               "--key", "TEST-7", "--decision", "d", "--followon", "f")
        c.check("devrecord: works in a repo with no sprint board",
                code == 0 and "The hook was never armed" in out, out.strip()[:200])

        # ── mint ───────────────────────────────────────────────────────────────
        set_state(state)
        code, out = jf("mint", "--story", "9.1", "--jira-project", "TEST",
                       "--epic-key", "TEST-1", "--lane", "quick-dev", "--parallel-ok",
                       "--apply")
        st = get_state(state)
        c.check("mint: exit 0 and echoes the key",
                code == 0 and "JIRA_KEY=TEST-99" in out, out.strip()[:200])
        c.check("mint: the created ticket carries the outline",
                "AC-1 (archive)" in st["description"])
        c.check("mint: parents to the epic",
                "--parent" in st["create_args"]
                and st["create_args"][st["create_args"].index("--parent") + 1] == "TEST-1")
        labels = st["create_args"][st["create_args"].index("--label") + 1]
        c.check("mint: labels follow the ruling",
                "quick-dev" in labels and "parallel-ok" in labels, labels)

        # A backfilled or re-run board already has the ticket. A second one is worse than
        # none - two rows, one of which nothing will ever move again.
        set_state(state, search=[{"key": "TEST-42",
                                  "fields": {"summary": "9.1 - Widget Archive"}}])
        code, out = jf("mint", "--story", "9.1", "--jira-project", "TEST", "--apply")
        st = get_state(state)
        c.check("mint: reuses the existing ticket instead of minting a twin",
                code == 0 and "reusing existing ticket TEST-42" in out
                and "create_args" not in st, out.strip()[:200])
        c.check("mint: backfills the outline onto the bare ticket",
                "backfilled" in out and "AC-1 (archive)" in st["description"])
        c.check("mint: the backfill edit is non-interactive (--yes)",
                "--yes" in st.get("edit_args", []))

        # A fuzzy `~` search returns the children too; 9.1 must not adopt 9.1.2's ticket.
        set_state(state, search=[{"key": "TEST-43",
                                  "fields": {"summary": "9.1.2 - A Child Story"}}])
        code, out = jf("mint", "--story", "9.1", "--jira-project", "TEST", "--apply")
        c.check("mint: a fuzzy search hit on a CHILD is not a reuse",
                code == 0 and "reusing" not in out
                and "create_args" in get_state(state), out.strip()[:200])

        set_state(state, swallow_desc=True)
        code, out = jf("mint", "--story", "9.1", "--jira-project", "TEST", "--apply")
        c.check("mint: description that never landed -> exit 2",
                code == 2 and "description is empty" in out, out.strip()[:200])

        set_state(state)
        code, out = jf("mint", "--story", "9.1", "--jira-project", "TEST")
        c.check("mint: no --apply is a dry run",
                code == 0 and "DRY RUN" in out and "create_args" not in get_state(state))

        # ── check ──────────────────────────────────────────────────────────────
        set_state(state)
        code, out = jf("check", "--key", "TEST-7")
        c.check("check: bare ticket -> exit 2, both halves named",
                code == 2 and "no outline" in out and "no Dev Record" in out,
                out.strip()[:200])

        # Positive control: a checker that never reports clean gets muted.
        set_state(state,
                  description="9.1 - Widget Archive. Acceptance criteria 1. AC-1 archive.",
                  comments=[{"id": "1", "body": "Dev Record - 9.1 (close-out)\nDecisions"}])
        code, out = jf("check", "--key", "TEST-7")
        c.check("check: fed ticket -> exit 0 (positive control)",
                code == 0 and "0 error(s)" in out, out.strip()[:200])

        set_state(state,
                  description="9.1 - Widget Archive. Acceptance criteria 1. AC-1 archive.",
                  comments=[{"id": "1", "body": "Dev Record - 9.1 (quick-dev)"},
                            {"id": "2", "body": "Dev Record - 9.1 (close-out)"}])
        code, out = jf("check", "--key", "TEST-7")
        c.check("check: two Dev Records -> warns, does not block",
                code == 1 and "there should be" in out, out.strip()[:200])
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
