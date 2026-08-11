"""jira_feed.py must never invent ticket content, and must leave exactly ONE Dev Record.

The two defects this covers are the ones that motivated SCC-49 and the ones a hand-written
step reintroduces every time:

  * a ticket that reports success while carrying nothing (acli exits 0, the comment is not
    there) - covered by the `swallow` stub mode, the load-bearing negative here;
  * two Dev Records for one story, because /cicd-quick-dev closed the branch and then
    /cicd-update-sprint-memory closed the story and both posted.

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
import subprocess
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir, run_script

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
    vkey = args[3] if len(args) > 3 else "TEST-7"
    fields = {"description": adf(state.get("description")),
              "summary": state.get("summary", ""),
              "status": {"name": state.get("statuses", {}).get(vkey, "To Do")},
              "issuetype": {"name": state.get("types", {}).get(vkey, "Task")}}
    # `--fields` is a WHITELIST on the real acli, so this stub honours it (SCC-54). It did
    # not, and that gap hid a live defect for two tickets: production asked for a field list
    # with `issuetype` missing from it, read `issuetype` out of the answer, and got nothing -
    # while every test here passed, because the stub handed back the whole shape regardless.
    # A stub more generous than the tool it stands in for cannot fail on the bug it exists
    # to catch.
    want = val("--fields")
    if want:
        keep = [w.strip() for w in want.split(",")]
        fields = {k: v for k, v in fields.items() if k in keep}
    print(json.dumps({"key": vkey, "fields": fields}))
elif head[:3] == ["jira", "workitem", "transition"]:
    # Record EVERY call, landed or not. Two SCC-113 assertions need the count rather than
    # the end state: `start` must be idempotent (a second run makes no second call), and
    # the post-commit hook must make exactly ONE call per branch (the marker short-circuit).
    # An end-state check cannot tell "did not call" from "called and it was already right".
    state.setdefault("transitions", []).append(
        {"key": val("--key"), "status": val("--status"), "yes": "--yes" in args})
    if not state.get("stuck_status"):
        state.setdefault("statuses", {})[val("--key")] = val("--status")
    save()
    print("Work item transitioned")
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
    if "--type" in args:
        state.setdefault("types", {})[val("--key")] = val("--type")
        state.setdefault("retyped", []).append(val("--key"))
    else:
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


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)


def commit(repo: Path, subject: str) -> None:
    git(repo, "add", "-A")
    # --no-verify: this fixture must not inherit the MACHINE's commit-msg hook, which rejects
    # a subject with no Jira key - and one of these commits deliberately has none.
    git(repo, "commit", "-q", "--no-verify", "-m", subject)


def make_trace_repo(root: Path) -> Path:
    """A real git history whose subjects carry keys. `trace` reads git, never Jira.

    Shaped to carry every signal the ranking has to separate: a line whose blame is younger
    than the file's first commit, a MERGE subject repeating a key its own commit already
    carries, a foreign project's key, and a commit with no key at all."""
    repo = root / "traced"
    (repo / ".agents").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    git(repo, "config", "commit.gpgsign", "false")
    (repo / ".agents/jira.conf").write_text('JIRA_KEYS="SCC"\n', encoding="utf-8")
    src = repo / "widget.py"

    src.write_text("alpha = 1\nbeta = 2\ngamma = 3\n", encoding="utf-8")
    commit(repo, "SCC-10 feat: add the widget")
    src.write_text("alpha = 1\nbeta = 22\ngamma = 3\n", encoding="utf-8")
    commit(repo, "SCC-11 fix: beta was wrong")

    git(repo, "checkout", "-q", "-b", "side")
    src.write_text("alpha = 1\nbeta = 22\ngamma = 33\n", encoding="utf-8")
    commit(repo, "SCC-12 fix: gamma was wrong too")
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "--no-ff", "-q", "-m", "merge: SCC-12 -> main", "side")

    src.write_text("alpha = 1\nbeta = 22\ngamma = 33\ndelta = 4\n", encoding="utf-8")
    commit(repo, "AVCH-9 chore: a key from the OTHER project")
    (repo / "orphan.md").write_text("nothing to see\n", encoding="utf-8")
    commit(repo, "chore: no ticket on this one at all")
    return repo


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

        # Type turns on WHETHER THIS IS BMAD SPRINT WORK - never on having a parent. EVERY
        # ticket is parented: BMAD epics hold numbered stories, GROUPING epics ("CI/CD
        # Improvment") hold workflow/rules/skills work because Jira offers no other container.
        # Both look identical in Jira, so keying off the parent types every chore as a Story.
        c.check("mint: a story file backs it -> Story",
                st["create_args"][st["create_args"].index("--type") + 1] == "Story",
                st["create_args"][st["create_args"].index("--type") + 1])

        set_state(state)
        code, out = jf("mint", "--story", "9.1", "--jira-project", "TEST", "--apply")
        st = get_state(state)
        c.check("mint: still a Story with no epic key - the story file decides, not the parent",
                st["create_args"][st["create_args"].index("--type") + 1] == "Story",
                st["create_args"][st["create_args"].index("--type") + 1])
        c.check("mint: ...but it warns that a BMAD story belongs under its BMAD epic",
                "belongs under its BMAD epic" in out, out.strip()[:160])

        # The chore case: grouping-epic work has no story file, so the operator types it.
        set_state(state)
        code, out = jf("mint", "--story", "9.1", "--jira-project", "TEST",
                       "--type", "Task", "--epic-key", "TEST-1", "--apply")
        st = get_state(state)
        c.check("mint: an explicit --type wins (chore work under a grouping epic)",
                st["create_args"][st["create_args"].index("--type") + 1] == "Task")

        set_state(state)
        code, out = jf("mint", "--story", "9.1", "--jira-project", "TEST",
                       "--type", "Bug", "--epic-key", "TEST-1", "--apply")
        st = get_state(state)
        c.check("mint: --type passes any board type through",
                st["create_args"][st["create_args"].index("--type") + 1] == "Bug")

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

        # ── the type rule, all four arms ──────────────────────────────────────
        # `Bug` is deliberately absent from the computed vocabulary. It is TEMPORARY: a Story
        # or Task found broken wears it until the fix lands, carrying the same number and story
        # file as before - so a rule that "corrects" it erases the signal that it is broken.
        # Pinned as a table because this rule was WRONG TWICE before the real board settled
        # it: first keyed on the epic parent (which would type every chore Task a Story,
        # since everything is parented), then on the story file alone (which typed 19.2 a
        # Task - a planned sprint story whose file is not written until pickup).
        import jira_feed  # noqa: E402 - the tests run scripts/ on sys.path
        table = [
            ("19.2", False, "Story", "a dotted number, file not written until pickup"),
            ("12.3.4", True, "Story", "number and file"),
            ("tea-16-eval", True, "Story", "no dotted number, but a real story file"),
            ("debug-1.1", True, "Story", "a debug story is an ordinary BMAD story"),
            ("debug-4.1", False, "Story", "the debug marker stands in for the dotted number"),
            ("Separate", False, "Task", "workflow/IDE/rules/skills work"),
            ("quick-fix-1.1", False, "Task", "ad-hoc fix, no BMAD story behind it"),
        ]
        for head, has_file, want, why in table:
            got = jira_feed.work_type(head, has_file)
            c.check(f"type rule: {head} (file={str(has_file).lower()}) -> {want}",
                    got == want, f"got {got} - {why}")

        # ── --closing clears the Bug flag, back to Story OR Task ───────────────
        # A Bug is a TEMPORARY flag on broken work, raised by an audit that traced a live bug
        # to the ticket that introduced it, or by the operator by hand. When the fix lands the
        # bug is GONE and the ticket goes back to being what it always was. Close-out is the
        # only moment anything can know that - which is why the bulk audit must not guess.
        set_state(state, types={"TEST-7": "Bug"})
        code, out = jf("devrecord", "--story", "9.1", "--key", "TEST-7", "--apply",
                       "--closing", "--outcome", "review -> done", "--followon", "none")
        st = get_state(state)
        c.check("closing: a fixed Bug on sprint work goes back to Story",
                code == 0 and st["types"]["TEST-7"] == "Story"
                and "the bug is gone" in out, out.strip()[:200])

        set_state(state, types={"TEST-7": "Story"})
        code, out = jf("devrecord", "--story", "9.1", "--key", "TEST-7", "--apply",
                       "--closing", "--followon", "none")
        c.check("closing: an ordinary Story is not re-typed",
                code == 0 and "retyped" not in get_state(state), out.strip()[:160])

        # THE regression (SCC-53). The first cut restored ONLY to Story: a flagged Task hit a
        # "does not look like BMAD sprint work" warning and STAYED a Bug, with nothing else in
        # the system able to clear it - a permanent Bug on the board. Task work can be found
        # broken exactly as easily as a story, so it must restore to Task.
        set_state(state, types={"TEST-7": "Bug"})
        code, out = jf("devrecord", "--story", "chore-thing", "--key", "TEST-7", "--apply",
                       "--closing", "--followon", "none")
        c.check("closing: a fixed Bug on TASK work goes back to Task, not stranded",
                code == 0 and get_state(state)["types"]["TEST-7"] == "Task"
                and "the bug is gone" in out, out.strip()[:200])

        set_state(state, types={"TEST-7": "Bug"})
        code, out = jf("devrecord", "--story", "9.1", "--key", "TEST-7", "--apply",
                       "--followon", "none")
        c.check("closing: without --closing the Bug flag stands",
                code == 0 and get_state(state)["types"]["TEST-7"] == "Bug")

        # ── audit: report + migrate types, and NEVER touch a Bug ───────────────
        def board(*rows):
            """rows: (key, type, summary)"""
            set_state(state,
                      search=[{"key": k, "fields": {"issuetype": {"name": t},
                                                    "summary": s}} for k, t, s in rows],
                      types={k: t for k, t, _ in rows})

        board(("T-1", "Task", "9.1 - Widget Archive"),
              ("T-2", "Task", "Separate the front end"),
              ("T-3", "Epic", "CI/CD Improvment"))
        code, out = run_script("jira_feed.py", "audit", "--project", str(repo),
                               "--acli", str(acli), "--jira-project", "TEST")
        c.check("audit: flags a numbered ticket typed Task",
                code == 1 and "T-1: Task -> Story" in out, out.strip()[:200])
        c.check("audit: leaves un-numbered chore work as Task", "T-2: Task -> " not in out)
        c.check("audit: ignores Epics entirely", "T-3" not in out)
        c.check("audit: a dry run writes nothing", "retyped" not in get_state(state))

        board(("T-1", "Task", "9.1 - Widget Archive"),
              ("T-2", "Task", "Separate the front end"))
        code, out = run_script("jira_feed.py", "audit", "--project", str(repo),
                               "--acli", str(acli), "--jira-project", "TEST", "--apply")
        st = get_state(state)
        c.check("audit --apply: converts and reads the ticket back",
                code == 0 and st.get("retyped") == ["T-1"]
                and st["types"]["T-1"] == "Story", out.strip()[:200])

        # THE load-bearing case. A Bug is a Story or Task flagged as broken - same number, same
        # story file - so every rule here reads it as a mistype. "Correcting" it erases the one
        # signal that the work is broken. This pass cannot tell "still broken" from "fixed";
        # only close-out can, so only `devrecord --closing` may clear it.
        board(("T-1", "Bug", "9.1 - Widget Archive"),
              ("T-2", "Task", "Separate the front end"))
        code, out = run_script("jira_feed.py", "audit", "--project", str(repo),
                               "--acli", str(acli), "--jira-project", "TEST", "--apply")
        st = get_state(state)
        c.check("audit: NEVER retypes a Bug, even when it looks like a mistyped Story",
                "retyped" not in st and st["types"]["T-1"] == "Bug", out.strip()[:200])
        c.check("audit: says why the Bug was left alone",
                "left for close-out" in out and code == 0, out.strip()[:200])

        # ...and the same for a Bug over TASK work, which the first cut could never clear.
        board(("T-1", "Bug", "Separate the front end"),
              ("T-2", "Task", "Something else"))
        code, out = run_script("jira_feed.py", "audit", "--project", str(repo),
                               "--acli", str(acli), "--jira-project", "TEST", "--apply")
        c.check("audit: leaves a Bug over TASK work alone too",
                "retyped" not in get_state(state)
                and get_state(state)["types"]["T-1"] == "Bug", out.strip()[:200])

        board(("T-1", "Story", "9.1 - Widget Archive"),
              ("T-2", "Task", "Separate the front end"))
        code, out = run_script("jira_feed.py", "audit", "--project", str(repo),
                               "--acli", str(acli), "--jira-project", "TEST")
        c.check("audit: a correct board reports clean (positive control)",
                code == 0 and "every type agrees" in out, out.strip()[:200])

        # ── trace: propose the ticket behind a path. Reads git, NEVER the board ──
        traced = make_trace_repo(tmp)

        def tr(*args: str) -> tuple[int, str]:
            os.environ["STUB_STATE"] = str(state)
            return run_script("jira_feed.py", "trace", "--project", str(traced), *args)

        # THE load-bearing negative for this verb: it must not be able to touch Jira at all.
        # `--acli` points at a binary that does not exist, so any board call would die.
        code, out = tr("--path", "widget.py:2", "--acli", str(tmp / "no-such-acli"))
        c.check("trace: never calls acli (a bad --acli cannot break it)",
                code == 0, out.strip()[:200])
        c.check("trace: blame on the exact line names the ticket that WROTE it",
                "SCC-11" in out and "blame widget.py:2" in out, out.strip()[:240])
        c.check("trace: says out loud that it is a proposal",
                "THIS IS A PROPOSAL" in out)
        c.check("trace: hands over the exact flag command, best candidate first",
                "flag --key SCC-11" in out, out.strip()[:240])

        code, out = tr("--path", "widget.py", "--json")
        data = json.loads(out[out.index("{"):])
        keys = [c_["key"] for c_ in data["candidates"]]
        c.check("trace --json: carries every keyed commit on the file",
                set(keys) == {"SCC-10", "SCC-11", "SCC-12"}, str(keys))
        # jira.conf says JIRA_KEYS="SCC". Commit prose says "AVCH-9" all the time; proposing a
        # ticket in another project would flag a ticket this repo cannot even close.
        c.check("trace: a foreign project's key is never proposed", "AVCH-9" not in out)
        by_key = {c_["key"]: c_ for c_ in data["candidates"]}
        # `merge: SCC-12 -> main` repeats a key its own commit already carries. Counting both
        # double-weights whichever ticket merged last, for no added information.
        c.check("trace: a merge subject does not double-count its branch's key",
                by_key["SCC-12"]["hits"] == 1, json.dumps(by_key["SCC-12"]["why"]))
        c.check("trace: a file-only hit is marked as the weaker signal",
                by_key["SCC-11"]["blame"] is False, "no :LINE was given")

        # Line 3 was last written by SCC-12; the file's newest keyed commit is AVCH-9 and its
        # oldest is SCC-10. Ranking must follow the LINE, or the "strong" signal is decoration.
        code, out = tr("--path", "widget.py:3", "--json")
        top = json.loads(out[out.index("{"):])["candidates"][0]
        c.check("trace: blame follows the LINE, and ranks above file-only hits",
                top["key"] == "SCC-12" and top["blame"] is True, json.dumps(top)[:240])

        code, out = tr("--path", "orphan.md")
        c.check("trace: no keyed commit -> exit 1, and says so",
                code == 1 and "no ticket proposed" in out, out.strip()[:200])

        code, out = tr("--path", "widget.py:2", "--path", "ghost.py:9")
        c.check("trace: a path that does not exist warns and is skipped, not fatal",
                code == 0 and "ghost.py: not a file" in out, out.strip()[:240])

        # ── flag: the RAISE half. Story|Task -> Bug, and out of Done ────────────
        set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "Done"},
                  summary="a shipped task")
        code, out = jf("flag", "--key", "TEST-7", "--reason", "the roster 500s on load")
        c.check("flag: dry run renders and writes nothing",
                code == 0 and "DRY RUN" in out
                and get_state(state)["types"]["TEST-7"] == "Task"
                and not get_state(state)["comments"], out.strip()[:200])

        code, out = jf("flag", "--key", "TEST-7", "--reason", "the roster 500s on load",
                       "--evidence", "500 on GET /roster", "--found-by", "live-testing",
                       "--apply")
        st = get_state(state)
        c.check("flag: a shipped Task becomes a Bug",
                code == 0 and st["types"]["TEST-7"] == "Bug", out.strip()[:240])
        c.check("flag: a Done ticket comes back out of Done",
                st["statuses"]["TEST-7"] == "To Do", out.strip()[:200])
        body = "\n".join(x["body"] for x in st["comments"])
        c.check("flag: the ticket carries WHY, not just the flag",
                "the roster 500s on load" in body and "500 on GET /roster" in body)
        # Close-out recomputes the type from the rule, but a human reading the board later
        # needs to see what it WAS - otherwise a flagged ticket has no record of its own kind.
        c.check("flag: the comment records what it was, so the restore is auditable",
                "shipped as a **Task**" in body and "restores it to `Task`" in body)
        c.check("flag: the comment is not mistaken for the Dev Record",
                "dev record" not in body[:400].lower())

        # Every case above reads `issuetype` and `status` back through `--fields`, which is a
        # WHITELIST on the real acli - and `issuetype` was missing from production's list for
        # two tickets (SCC-54). It passed anyway, because the stub returned the whole shape no
        # matter what was asked for. This is the positive control for the fix: the stub must
        # actually be strict, or every read-back case above is testing nothing.
        os.environ["STUB_STATE"] = str(state)
        probe = subprocess.run([str(acli), "jira", "workitem", "view", "TEST-7",
                                "--fields", "key,summary", "--json"],
                               capture_output=True, text=True)
        c.check("fields whitelist: the stub is STRICT, so the read-back cases mean something",
                '"issuetype"' not in probe.stdout and '"status"' not in probe.stdout,
                "a stub more generous than acli hid this defect twice")

        # Idempotent: two testers finding the same bug must not fight over the board.
        before = len(get_state(state)["comments"])
        code, out = jf("flag", "--key", "TEST-7", "--reason", "same bug, found again",
                       "--apply")
        c.check("flag: an already-flagged ticket is a no-op, not a second flag",
                code == 0 and "already flagged" in out
                and len(get_state(state)["comments"]) == before, out.strip()[:200])

        # THE round trip - raise and clear are one mechanism or neither works.
        code, out = jf("devrecord", "--story", "chore-thing", "--key", "TEST-7", "--apply",
                       "--closing", "--followon", "none")
        c.check("round trip: flag -> Bug -> close-out restores Task",
                code == 0 and get_state(state)["types"]["TEST-7"] == "Task"
                and "the bug is gone" in out, out.strip()[:240])

        # In flight, not finished: shoving it back to To Do would erase real state to record
        # something the type already says.
        set_state(state, types={"TEST-8": "Story"}, statuses={"TEST-8": "In Review"})
        code, out = jf("flag", "--key", "TEST-8", "--reason", "AC-2 never worked", "--apply")
        c.check("flag: a ticket still in flight keeps its status",
                code == 0 and get_state(state)["statuses"]["TEST-8"] == "In Review"
                and "nothing to reopen" in out, out.strip()[:240])
        c.check("flag: a Story is flagged exactly like a Task",
                get_state(state)["types"]["TEST-8"] == "Bug")

        set_state(state, types={"TEST-9": "Epic"}, statuses={"TEST-9": "Done"})
        code, out = jf("flag", "--key", "TEST-9", "--reason", "whatever", "--apply")
        c.check("flag: an Epic is refused - a container is never broken work",
                code == 2 and "container is never a Bug" in out
                and get_state(state)["types"]["TEST-9"] == "Epic", out.strip()[:200])

        # acli exits 0 on a transition it did not perform - the same swallow the whole script
        # exists to catch, one verb further on.
        set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "Done"},
                  stuck_status=True)
        code, out = jf("flag", "--key", "TEST-7", "--reason", "still broken", "--apply")
        c.check("flag: a transition that silently no-ops is reported, not assumed",
                code == 2 and "still Done" in out, out.strip()[:240])

        # ── start: the OTHER end of the lifecycle (SCC-113) ────────────────────
        # Four seams wrote `Done` and exactly one wrote `In Progress` - the BMAD story lane -
        # so on a board where every non-epic ticket is a Task, nothing was ever visible as in
        # flight. This is that seam, as a verb rather than a prose step, because the prose one
        # is the one that never ran.

        set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "To Do"})
        code, out = jf("start", "--key", "TEST-7")
        c.check("start: renders without --apply and writes NOTHING",
                code == 0 and not get_state(state).get("transitions")
                and get_state(state)["statuses"]["TEST-7"] == "To Do", out.strip()[:200])

        set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "To Do"})
        code, out = jf("start", "--key", "TEST-7", "--apply")
        st = get_state(state)
        c.check("start: To Do -> In Progress", code == 0
                and st["statuses"]["TEST-7"] == "In Progress", out.strip()[:200])
        c.check("start: passes --yes, or acli blocks on a prompt no agent can answer",
                bool(st.get("transitions")) and st["transitions"][0]["yes"],
                "jira.md:268 names this trap; three call sites still omit it")

        # `To Do Next` is the operator's hand-picked queue - a To Do-category status, so it
        # starts exactly like `To Do`. It exists on SCC and not on AVCH; per-board-optional.
        set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "To Do Next"})
        code, out = jf("start", "--key", "TEST-7", "--apply")
        c.check("start: To Do Next -> In Progress (the queue is a To Do category)",
                code == 0 and get_state(state)["statuses"]["TEST-7"] == "In Progress",
                out.strip()[:200])

        # Idempotence is not cosmetic: the post-commit hook fires on EVERY commit, and two
        # lanes can hold the same key. A second call must make no second transition.
        set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
        code, out = jf("start", "--key", "TEST-7", "--apply")
        c.check("start: already In Progress is a no-op that exits 0",
                code == 0 and "already" in out.lower(), out.strip()[:200])
        c.check("start: the no-op makes NO transition call at all",
                not get_state(state).get("transitions"),
                "an end-state check would pass here even if it called acli every commit")

        # Guardrail 1, in reverse. Borrowing a finished ticket's key is the defect that
        # silently decorates the wrong ticket and overwrites its Dev Record.
        set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "Done"})
        code, out = jf("start", "--key", "TEST-7", "--apply")
        c.check("start: a Done ticket is REFUSED - that means the key is wrong",
                code == 2 and "not your key" in out.lower()
                and get_state(state)["statuses"]["TEST-7"] == "Done", out.strip()[:240])

        # Narrow on purpose, exactly like flag's "only out of Done": a verb that moves from
        # anywhere erases real state. `Blocking` is an impediment and `In Review` is finished
        # work waiting on a human - starting either would destroy the only signal they carry.
        for held in ("Blocking", "In Review", "Deferred"):
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": held})
            code, out = jf("start", "--key", "TEST-7", "--apply")
            # Exit 3, not 0: "left alone" is NOT settled. The hook writes its once-per-branch
            # marker on 0, so returning 0 here silenced a lane whose ticket was `Blocking`
            # when it opened and went back to `To Do` when the blocker cleared.
            c.check(f"start: {held} is left alone, and says ASK AGAIN (exit 3, not 0)",
                    code == 3 and get_state(state)["statuses"]["TEST-7"] == held
                    and not get_state(state).get("transitions"), out.strip()[:200])

        # An Epic is allowed here and refused by `flag` - the difference is deliberate. An
        # epic under active development IS in progress; an epic is never itself broken work.
        set_state(state, types={"TEST-5": "Epic"}, statuses={"TEST-5": "To Do"})
        code, out = jf("start", "--key", "TEST-5", "--apply")
        c.check("start: an Epic IS allowed (unlike flag) - epic/ is in scope",
                code == 0 and get_state(state)["statuses"]["TEST-5"] == "In Progress",
                out.strip()[:200])

        set_state(state, types={"TEST-7": "Subtask"}, statuses={"TEST-7": "To Do"})
        code, out = jf("start", "--key", "TEST-7", "--apply")
        c.check("start: a Subtask is refused",
                code == 2 and get_state(state)["statuses"]["TEST-7"] == "To Do",
                out.strip()[:200])

        # The load-bearing negative, same as every other write verb here: acli exits 0 on a
        # transition it did not perform.
        set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "To Do"},
                  stuck_status=True)
        code, out = jf("start", "--key", "TEST-7", "--apply")
        c.check("start: a transition that silently no-ops is reported, not assumed",
                code == 2 and "still" in out.lower(), out.strip()[:240])

        # ── every acli transition in .agents/ carries --yes (SCC-113) ──────────
        # The guard that stops a FOURTH call site shipping without it. Comment lines are
        # stripped first: `jira.md` documents the trap by quoting the flag, and a raw scan
        # would read that prose as coverage for the three call sites that lack it.
        lobby = SCRIPTS.parent.parent
        me = Path(__file__).resolve()

        def offending_lines(lines: list[str]) -> list[int]:
            """Line numbers whose `acli … workitem transition` call omits `--yes`.

            ⭐ Anchored to the COMMAND SPAN, not to a window. A 3-line window passed a site
            whose real flag had been deleted because prose on the same line still said the
            word `--yes` — and one of the two it let through was
            `smh-merge-multiple-workingtrees.md`, a site THIS ticket was written to fix.
            The note explaining the flag was excusing its absence.

            Three things the span has to survive, each a real line in this repo:
              * markdown inline code — the call ends at its closing backtick; the prose
                after it is commentary, not argv;
              * a trailing `# TRAP: … --yes …` comment on the cheat-sheet line;
              * a call that WRAPS — jira_feed.py builds argv across two physical lines, so
                a line-local scan indicts the one caller that always got it right.
            """
            out = []
            for n, ln in enumerate(lines, 1):
                if ln.lstrip().startswith(("#", ">", "//")):
                    continue              # a comment quoting the trap is not a call site
                # `acli` is the discriminator, not the bare phrase: a CALL SITE invokes the
                # binary. Prose ABOUT the rule mentions the phrase and is not a call.
                if not all(t in ln for t in ("acli", "workitem", "transition")):
                    continue
                span = ln[ln.find("acli"):]
                span = span.split("`", 1)[0]          # inline code ends at the backtick
                span = span.split("#", 1)[0]          # a trailing comment is not argv
                if (span.rstrip().endswith(("\\", ","))
                        or span.count("[") > span.count("]")):
                    span += " " + " ".join(lines[n:n + 2])    # the call wraps
                if "--yes" not in span:
                    out.append(n)
            return out

        def yes_offenders() -> list[str]:
            out = []
            for p in sorted((lobby / ".agents").rglob("*")):
                if p.suffix not in (".md", ".py", ".sh") or not p.is_file():
                    continue
                if p.resolve() == me:
                    continue
                for n in offending_lines(p.read_text(encoding="utf-8").splitlines()):
                    out.append(f"{p.relative_to(lobby)}:{n}")
            return out

        # ⭐ NEGATIVE CONTROL — nothing else in this suite pins that the guard CAN fire.
        # Each row is a real shape from this repo with the flag surgically removed; the
        # guard must indict every one, or it is decoration.
        must_catch = [
            ['acli jira workitem transition --key K --status "Done"'],
            ['then `acli jira workitem transition --key K --status "Done"` (**`--yes` or '
             'acli stops on a confirm prompt no agent shell can answer**)'],
            ['acli jira workitem transition --key K --status "In Review"'
             '  # TRAP: needs --key; --yes skips the interactive confirm'],
            ['t = acli(binary, ["jira", "workitem", "transition", "--key", args.key,',
             '                  "--status", target])'],
        ]
        for i, rows in enumerate(must_catch):
            c.check(f"yes-guard NEGATIVE CONTROL {i}: an un-flagged call IS caught",
                    offending_lines(rows) == [1],
                    "prose or a comment saying --yes must never excuse the missing flag: "
                    + rows[0][:90])

        must_pass = [
            ['acli jira workitem transition --key K --status "Done" --yes'],
            ['t = acli(binary, ["jira", "workitem", "transition", "--key", args.key,',
             '                  "--status", target, "--yes"])'],
            ['`tests/test_jira_feed.py` fails if any `workitem transition` omits it.'],
        ]
        for i, rows in enumerate(must_pass):
            c.check(f"yes-guard POSITIVE CONTROL {i}: a compliant line is NOT caught",
                    offending_lines(rows) == [],
                    "a guard that indicts the fix is worse than none: " + rows[0][:90])

        offenders = yes_offenders()
        c.check("yes-guard: every `workitem transition` under .agents/ passes --yes",
                not offenders,
                "acli prompts without -y and an agent shell cannot answer: "
                + ", ".join(offenders[:6]))

        # Positive control, same shape as the interpreter probe's below: the rule documents
        # this trap by quoting the bad form in prose. If stripping ever dies, that quote
        # becomes an offender and this assertion goes red - which is the point.
        c.check("yes-guard: the comment/quote strip is load-bearing, not decorative",
                any(all(t in ln for t in ("acli", "workitem", "transition"))
                    and "--yes" not in ln
                    for ln in (lobby / ".agents/rules/jira.md")
                    .read_text(encoding="utf-8").splitlines()
                    if ln.lstrip().startswith((">", "#"))),
                "jira.md must keep quoting the un-flagged form in prose, or this guard "
                "is no longer being exercised against the case that inverts it")

        # ── the interpreter probe, in every hook that has one ──────────────────
        # The suite cannot EXECUTE these (a .sh will not run on the PC), so this asserts the
        # contract textually. It is a weak guard by nature - it cannot see order-of-execution
        # - but it does catch the exact regression it was written for: `pre-commit-encoding.sh`
        # probed `python || python3`, never tried `py`, and on a box with only `py` the whole
        # substitution failed so the gate exited 0. Armed in name, checking nothing, silently.
        hooks = SCRIPTS.parent.parent  # repo root
        probes = {
            ".agents/scripts/git-hooks/pre-commit-encoding.sh": True,
            ".agents/scripts/git-hooks/sop-currency.sh": True,
            ".githooks/post-commit": False,   # recorder: may skip, must not prefer `python`
        }
        for rel, must_announce in probes.items():
            p = hooks / rel
            if not p.is_file():
                c.check(f"probe: {rel} exists", False, "missing")
                continue
            # CODE only. The fix's own comment quotes the broken line verbatim, so a whole-file
            # grep matches the warning ABOUT the bug and reports the fix as the defect - the
            # same inversion that made a source-grep guard pass on a comment once before.
            text = "\n".join(ln for ln in p.read_text(encoding="utf-8").splitlines()
                             if not ln.lstrip().startswith("#"))
            c.check(f"probe: {rel} tries python3, python AND py",
                    "for c in python3 python py" in text,
                    "hooks must probe, never assume - the Mac has no bare `python`")
            c.check(f"probe: {rel} never falls back to a bare `python` first",
                    "command -v python |" not in text
                    and "then PY=python;" not in text)
            if must_announce:
                c.check(f"probe: {rel} SAYS so when no interpreter is found",
                        "no python interpreter found" in text,
                        "a gate that skips mutely reads as a pass")
        # Positive control for the strip above: the fix's comment DOES quote the old line, so
        # a guard reading the raw file would fail here. If this ever passes, the strip is dead.
        raw = (hooks / ".agents/scripts/git-hooks/pre-commit-encoding.sh").read_text(encoding="utf-8")
        c.check("probe: the comment-stripping is load-bearing, not decorative",
                "command -v python |" in raw,
                "the fix quotes the broken line; a raw grep would flag the fix as the defect")
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
