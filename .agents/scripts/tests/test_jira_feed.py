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
import re
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
    # `blind_after` models a READ that starts failing partway through while WRITES keep
    # working - a transport blip on the LADDER's read-back, which view_fields(strict=False)
    # turns into None. It has to be a COUNT, not a flag: a flag also kills cmd_finish's very
    # first read, so the run bails at "could not reach the board" and never reaches the
    # ladder at all - the case would pass while testing nothing.
    state["views"] = state.get("views", 0) + 1
    save()
    if state.get("blind_after") and state["views"] > state["blind_after"]:
        print("Error: could not read work item", file=sys.stderr)
        sys.exit(1)
    vkey = args[3] if len(args) > 3 else "TEST-7"
    fields = {"description": adf(state.get("description")),
              "summary": state.get("summary", ""),
              "labels": list(state.get("labels", {}).get(vkey, [])),
              "status": {"name": state.get("statuses", {}).get(vkey, "To Do")},
              "issuetype": {"name": state.get("types", {}).get(vkey, "Task")}}
    # `parent` is returned by the real `view` (and IS on view_fields' whitelist) but is
    # REJECTED by `search` - verified against the live board 2026-08-12, SCC-119. Modelling
    # it only here is what makes that asymmetry testable: a caller that tries to read a
    # parent out of a search result gets nothing, exactly as it would in production.
    pkey = state.get("parents", {}).get(vkey)
    if pkey:
        fields["parent"] = {"key": pkey,
                            "fields": {"issuetype":
                                       {"name": state.get("types", {}).get(pkey, "Task")},
                                       "status":
                                       {"name": state.get("statuses", {}).get(pkey, "To Do")},
                                       "summary": state.get("summaries", {}).get(pkey, "")}}
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
    # `no_status` models a column the board does not carry: the call is recorded (acli says
    # it transitioned) but the status does NOT move. That is the shape a missing column
    # actually has, and it is the only way to test a LADDER - `stuck_status` blocks every
    # rung at once, so it can never tell "fell through to the second" from "never tried".
    if not state.get("stuck_status") and val("--status") not in state.get("no_status", []):
        state.setdefault("statuses", {})[val("--key")] = val("--status")
    save()
    print("Work item transitioned")
elif head == ["jira", "workitem", "comment", "list"]:
    print(json.dumps({"comments": [{"id": c["id"], "body": adf(c["body"])}
                                   for c in state["comments"]]}))
elif head == ["jira", "workitem", "comment", "create"]:
    # `swallow` drops the comment but still reports success (the board accepted it and lost
    # it); `comment_fail` is the honest failure - acli exits non-zero. They are different
    # bugs and only the second one a caller can react to.
    if state.get("comment_fail"):
        print("Error: could not create comment", file=sys.stderr)
        sys.exit(1)
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
    # ⛔ `parent` is NOT an allowed --fields value on search - the real acli exits 1 with
    # "field 'parent' is not allowed" (verified live 2026-08-12, SCC-119). The stub enforces
    # it for the same reason it enforces the view whitelist: a stub more generous than the
    # tool it stands in for cannot fail on the bug it exists to catch. Asking for `parent`
    # while checking parentage is the natural mistake, and it must fail HERE too.
    if "parent" in [w.strip() for w in (val("--fields") or "").split(",")]:
        print("Error: field 'parent' is not allowed", file=sys.stderr)
        sys.exit(1)
    # A failing search (bad key, malformed JQL) exits NON-ZERO with no rows - which is
    # byte-identical to a legitimately empty result unless the caller reads the exit code.
    # That is the whole point of the gate in task_preflight.py.
    if state.get("search_fail"):
        print("Error: the search failed", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(state.get("search", [])))
elif head[:3] == ["jira", "workitem", "clone"]:
    # Modelled on the REAL behaviour, measured 2026-08-17 against the live board (test clone
    # SCC-199, created + inspected + deleted): the clone carries summary, description and
    # LABELS, lands in `To Do` regardless of the source's status, and carries NO SUBTASKS.
    # That last one is the whole reason clone is the chosen mechanism, so the stub has to
    # model it or the case proves nothing about the property it was picked for.
    if state.get("clone_fail"):
        print("Error: the clone failed", file=sys.stderr)
        sys.exit(1)
    src = val("--key")
    new_key = state.get("clone_key", "TEST-CLONE")
    state["clones"] = state.get("clones", []) + [src]
    state.setdefault("labels", {})[new_key] = list(state.get("labels", {}).get(src, []))
    state.setdefault("statuses", {})[new_key] = "To Do"
    state.setdefault("summaries", {})[new_key] = state.get("summaries", {}).get(src, "")
    save()
    print("Work item " + str(src) + " has been successfully cloned as "
          "https://example.atlassian.net/browse/" + new_key)
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
    elif "--labels" in args or "--remove-labels" in args:
        # `label_edit_fail` is scoped to the LABEL form deliberately: a blanket `edit_fail`
        # would also kill the DESCRIPTION writers, and a large share of this file's cases
        # edit descriptions - the knob would break far more than the branch it aims at.
        if state.get("label_edit_fail"):
            print("Error: could not set labels", file=sys.stderr)
            sys.exit(1)
        # ⛔⛔ MEASURED 2026-08-17 against the LIVE board (SCC-197: probe label added, then
        # removed, reading the field back at every step). `--labels` **ADDS**. It does NOT
        # replace. `--remove-labels` is a separate flag, and acli honours BOTH in one call.
        #
        # ⭐ THIS STUB SAID "REPLACES" FOR MONTHS, AND THE LIE COST A SHIPPED DEFECT. Because
        # a replace-modelled stub turns "send the set minus X" into a working strip,
        # `cmd_finish`'s `user-tasks` strip passed its test while doing NOTHING on the real
        # board: it built the reduced set, sent it via `--labels`, acli added labels that were
        # already there, exited 0, and the label stayed on. A Done ticket kept the very signal
        # the strip exists to clear. This file's own view-whitelist comment states the rule
        # that was broken here: a stub more generous than the tool it stands in for cannot
        # fail on the bug it exists to catch.
        cur = list(state.get("labels", {}).get(val("--key"), []))
        for x in (val("--labels") or "").split(","):
            if x and x not in cur:
                cur.append(x)
        drop = {x for x in (val("--remove-labels") or "").split(",") if x}
        state.setdefault("labels", {})[val("--key")] = [x for x in cur if x not in drop]
    else:
        body = read("--description-file")
        # SCC-170: the LOSSY WRITER. `lossy_drop` models the real failure this guard exists
        # for - a write that lands, exits 0, and quietly comes back short. Nothing about the
        # exit code tells you; only reading the field back does.
        drop = state.get("lossy_drop")
        if drop:
            body = "\n".join(ln for ln in body.splitlines() if drop not in ln)
        state["description"] = body
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


def make_lane_repo(root: Path, name: str,
                   manifests: tuple[tuple[str, str], ...] = (),
                   branches: tuple[str, ...] = (),
                   remotes: tuple[str, ...] = (),
                   untracked: tuple[tuple[str, str], ...] = (),
                   on: str = "") -> Path:
    """A repo whose COMMITTED tree and refs are the only evidence of which lanes exist.

    SCC-174 asks one question - "can this repo PROVE that id is a lane?" - so every source here
    has to be the real article. `manifests` are `(dir, branch)` pairs written to
    `_artifacts/_main/<dir>/task.yaml` and COMMITTED. `branches` are real refs. `remotes` are
    written straight into `refs/remotes/origin/<name>`: a landed lane's local branch is pruned
    but its origin ref usually survives, there is no network here to fetch one, and a fixture
    that could only model local branches could not fail on the arm that matters.

    `untracked` writes a manifest git does not track, under a gitignored `Projects/`. That is
    not a corner case - it is the lobby's actual shape, where `Projects/` holds other repos'
    manifests and `.claude/worktrees/` holds a second copy of this repo's. A slug from there
    proves nothing about THIS repo's lanes, and a fixture with no such file cannot tell a
    `git ls-files` implementation from a `Path.glob` one.

    `on` checks the branch out, because "which lane am I standing on" is F3's whole question and
    a fixture parked on `main` answers it by accident."""
    repo = root / name
    repo.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    git(repo, "config", "commit.gpgsign", "false")
    (repo / ".gitignore").write_text("Projects/\n", encoding="utf-8")
    for d, branch in manifests:
        m = repo / "_artifacts" / "_main" / d
        m.mkdir(parents=True)
        (m / "task.yaml").write_text(
            f"task_key: TEST-7\nprimary_repo: fixture\nbranch: {branch}\n"
            f"close_command: smh-close-task-merge-tree\n", encoding="utf-8")
    (repo / "_artifacts").mkdir(exist_ok=True)
    commit(repo, "TEST-7 chore: the lane manifests")
    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    for b in branches:
        git(repo, "branch", b, head)
    for r in remotes:
        git(repo, "update-ref", f"refs/remotes/origin/{r}", head)
    for d, branch in untracked:
        m = repo / "Projects" / "other" / "_artifacts" / "_main" / d
        m.mkdir(parents=True)
        (m / "task.yaml").write_text(f"task_key: TEST-7\nbranch: {branch}\n",
                                     encoding="utf-8")
    if on:
        git(repo, "checkout", "-q", on)
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

        # ── SCC-170 · index-row: a parent's index survives its own edit ────────
        if c.block("SCC-170 index-row: a parent index survives its own edit"):
            # `acli edit --description` REPLACES the field. Every "add a row to the parent"
            # step in this system is therefore a read-modify-write, and one of them lost
            # SCC-164's Part E row on 2026-08-15 - silently, exit 0. The row was gone and the
            # only evidence was a human noticing later. This subcommand is the read-BACK that
            # turns that class of loss into an exit code.
            INDEX = ("Command-surface family. THE PARTS\n"
                     "  Part A  SCC-165  stale main refs\n"
                     "  Part B  SCC-166  review steps\n"
                     "  Part C  SCC-171  git-common-dir\n")
            ROW = "  Part M  SCC-999  a newly discovered part"

            set_state(state, description=INDEX, lossy_drop=None)
            code, out = jf("index-row", "--key", "TEST-1", "--line", ROW, "--apply")
            st = get_state(state)
            c.check("index-row: appends the row and exits 0", code == 0, out.strip()[:300])
            c.check("index-row: the new row is on the ticket",
                    "SCC-999" in st["description"], st["description"][-200:])
            c.check("index-row: EVERY pre-existing row survived",
                    all(k in st["description"] for k in ("SCC-165", "SCC-166", "SCC-171")),
                    st["description"][-300:])

            # ⛔ THE load-bearing negative. A writer that drops a line still exits 0 at the
            # acli layer; only the read-back catches it. Without this case the whole
            # subcommand is a more elaborate way to lose the same row.
            set_state(state, description=INDEX, lossy_drop="SCC-166")
            code, out = jf("index-row", "--key", "TEST-1", "--line", ROW, "--apply")
            # ⛔ `code == 2` alone is vacuous here: argparse ALSO exits 2 on an unknown
            # subcommand, so before this shipped the assertion passed by the feature not
            # existing. The output must prove the guard ran, not the parser.
            c.check("index-row: a write that DROPS a line is caught (exit 2), not blessed",
                    code == 2 and "usage: jira_feed.py" not in out,
                    f"exit {code}: " + out.strip()[:300])
            c.check("index-row: ...and it names the line that went missing",
                    "SCC-166" in out, out.strip()[:400])
            c.check("index-row: ...and it says the field was REPLACED, not appended to",
                    "read back" in out.lower(), out.strip()[:400])

            # A row already present is a no-op, not a duplicate: the discovery step re-runs.
            set_state(state, description=INDEX + ROW + "\n", lossy_drop=None)
            code, out = jf("index-row", "--key", "TEST-1", "--line", ROW, "--apply")
            st = get_state(state)
            c.check("index-row: an already-present row is a no-op (exit 0)", code == 0,
                    out.strip()[:200])
            c.check("index-row: ...and it is not duplicated",
                    st["description"].count("SCC-999") == 1, st["description"][-300:])

            # Without --apply nothing is written: the dry run is the default, as everywhere
            # else in this file.
            set_state(state, description=INDEX, lossy_drop=None)
            code, out = jf("index-row", "--key", "TEST-1", "--line", ROW)
            st = get_state(state)
            c.check("index-row: without --apply nothing is written", code == 0
                    and "SCC-999" not in st["description"], out.strip()[:200])

            # An EMPTY description is not a licence to replace it with one row - that is the
            # same data loss wearing a different mask (the ticket may be unreadable, not bare).
            set_state(state, description="", lossy_drop=None)
            code, out = jf("index-row", "--key", "TEST-1", "--line", ROW, "--apply")
            c.check("index-row: refuses to write a row onto an EMPTY description",
                    code == 2, f"exit {code}: " + out.strip()[:300])

            set_state(state, description="", lossy_drop=None, comments=[])

        # ── outline: rendered FROM the story file, never invented ──────────────
        if c.block("jira_feed · legacy A: outline, devrecord, mint, check, types, audit, trace, flag, start"):
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
            c.check("check: two Dev Records for ONE story id -> warns, does not block",
                    code == 1 and "there should be" in out, out.strip()[:200])

            # ── SCC-113: two LANES on one ticket is the designed state, not a defect ──
            # `find_devrecord` filters by story id ON PURPOSE - its docstring: "so a ticket that
            # legitimately carries records for two ids does not have one overwrite the other" - and
            # both Task surfaces pass `--story <branch-slug>` (smh-close-task-merge-tree.md:236,
            # smh-quick-dev.md:246), which changes per lane. A follow-on lane rides the ticket it
            # came from rather than minting a key, so N lanes -> N records is NORMAL.
            #
            # Counting records cannot tell "one lane posted twice" (the real defect, pinned by the
            # case ABOVE, which must stay red-capable) from "two lanes each posted once" (this
            # case). Grouping by id can. The test above is this fix's negative control: if it ever
            # goes green, the check was deleted rather than narrowed.
            set_state(state,
                      description="9.1 - Widget Archive. Acceptance criteria 1. AC-1 archive.",
                      comments=[{"id": "1",
                                 "body": "Dev Record - scc-113-jira-in-progress-seam (close-out)"},
                                {"id": "2",
                                 "body": "Dev Record - scc-113-door-content-parity (close-out)"}])
            # ⚠ SCC-174 RETARGETED this assertion, and the reason is the finding. Two ids used
            # to be exit 0 on their own say-so; they are now exit 0 only where a manifest or a
            # ref CLAIMS each one. This fixture is a plain directory - not a git checkout - so
            # it can no longer answer, and "cannot answer" must not read as "designed state".
            # The designed-state control moved to the SCC-174 block below, where the lanes are
            # backed by committed manifests and real refs; grouping-not-counting is still what
            # gets it past the duplicate arm above.
            code, out = jf("check", "--key", "TEST-7")
            c.check("check: two story ids off a repo that cannot be read -> exit 1, not blessed",
                    code == 1 and "not a git checkout" in out, out.strip()[:280])

            # `--story` is documented on THREE surfaces (jira_feed.py:15 usage, jira.md:302 a RULE,
            # cicd-update-sprint-memory.md:191 a command) and read by none of them. Story-awareness
            # gives it the meaning a close-out actually needs: did THIS lane file its record?
            # It delegates to find_devrecord, so it answers exactly "would devrecord update this
            # one?" - one rule, one implementation.
            code, out = jf("check", "--key", "TEST-7", "--story", "scc-113-door-content-parity")
            c.check("check: --story scopes to that lane's record -> exit 0",
                    code == 0 and "one Dev Record" in out, out.strip()[:200])

            # The load-bearing half: a lane that never filed one must be an ERROR, not silence.
            # Asserted on the MESSAGE, because an unknown flag also exits 2 - which is exactly how
            # this would pass for the wrong reason while `--story` stayed unwired.
            code, out = jf("check", "--key", "TEST-7", "--story", "scc-113-lane-that-never-filed")
            c.check("check: --story naming a lane with no record -> exit 2, names the lane",
                    code == 2 and "no Dev Record" in out
                    and "scc-113-lane-that-never-filed" in out, out.strip()[:200])

            # ⛔ A record whose header will not parse is NOT evidence of a lane (clean-room H-2).
            # `record_story_id` returns "" for it, and the first cut let that "" sit beside a real id
            # and read as "two lanes, the designed state" - exit 0 where the old count-based check
            # warned. The trigger is not exotic: the record filter is bare containment on the first
            # 400 chars, so ANY human comment saying "Dev Record" becomes a second record.
            set_state(state,
                      description="9.1 - Widget Archive. Acceptance criteria 1. AC-1 archive.",
                      comments=[{"id": "1", "body": "Dev Record - 9.1 (close-out, 2026-08-12)"},
                                {"id": "2", "body": "See the Dev Record above, I fixed the typo."}])
            code, out = jf("check", "--key", "TEST-7")
            c.check("check: a record with no parseable header never reads as a second LANE",
                    code == 1 and "no parseable header" in out, out.strip()[:200])

            # ⛔ `--story` is a READ GATE, and over-matching inverts on a read gate (clean-room H-3).
            # `find_devrecord` matches `want not in norm_id(text[:400])` - the whole head, not the
            # header - and Dev Record bodies are SCRAPED FROM WALKTHROUGH BULLETS, which routinely
            # name sibling lanes. Over-match on the WRITE path is conservative (it updates in place);
            # here it certifies that a lane filed a record when it never did.
            set_state(state,
                      description="9.1 - Widget Archive. Acceptance criteria 1. AC-1 archive.",
                      comments=[{"id": "1", "body": "Dev Record - scc-113-gate-honesty (close-out)"
                                                "\n\nDecisions made during dev\n"
                                                "- supersedes the scc-113-door-content-parity lane"}])
            code, out = jf("check", "--key", "TEST-7", "--story", "scc-113-door-content-parity")
            c.check("check: --story does not match a sibling lane NAMED IN THE BODY",
                    code == 2 and "no Dev Record" in out, out.strip()[:200])
            code, out = jf("check", "--key", "TEST-7", "--story", "scc-113-gate-honesty")
            c.check("check: --story still matches its OWN header (positive control)",
                    code == 0 and "one Dev Record" in out, out.strip()[:200])

            # The separator trap slug_matches() was written for: 9.1 must not adopt 9.10's record.
            set_state(state,
                      description="9.1 - Widget Archive. Acceptance criteria 1. AC-1 archive.",
                      comments=[{"id": "1", "body": "Dev Record - 9.10 (close-out)"}])
            code, out = jf("check", "--key", "TEST-7", "--story", "9.1")
            c.check("check: --story 9.1 does not adopt 9.10's record",
                    code == 2 and "no Dev Record" in out, out.strip()[:200])

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

            # ⭐ SCC-119 CHARACTERIZATION - no code backs this, and that is the point. A subtask
            # closes its own branch and files its own Dev Record, so it DOES reach this path; it
            # simply never carries `Bug` (operator ruling), so the restore branch never fires.
            # Pinning it costs nothing and catches the promotion a future edit would introduce:
            # `work_type()` answers "Task" for a subtask's slug, so any change that widened the
            # restore beyond `have == "Bug"` would silently lift a subtask out of its parent.
            set_state(state, types={"TEST-7": "Subtask", "TEST-4": "Task"},
                      parents={"TEST-7": "TEST-4"})
            code, out = jf("devrecord", "--story", "subtask-thing", "--key", "TEST-7", "--apply",
                           "--closing", "--followon", "none")
            st = get_state(state)
            c.check("closing: a Subtask files its record and is NEVER re-typed to Task (SCC-119)",
                    code == 0 and st["types"]["TEST-7"] == "Subtask" and "retyped" not in st,
                    out.strip()[:200])

            # ── audit: report + migrate types, and NEVER touch a Bug ───────────────
            def board(*rows, **extra):
                """rows: (key, type, summary). `extra` seeds parents/statuses for SCC-119.

            ⛔ The search rows carry NO `parent` on purpose - the real acli rejects that
            field on search (exit 1), so the audit has to `view` each subtask to learn its
            parentage. Putting parents in the search rows here would test a call production
            can never make."""
                types = {k: t for k, t, _ in rows}
                types.update(extra.pop("types", {}))
                set_state(state,
                          search=[{"key": k, "fields": {"issuetype": {"name": t},
                                                        "summary": s}} for k, t, s in rows],
                          types=types, **extra)

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

            # ── audit: subtask invariants (SCC-119) ───────────────────────────────
            # The old pass SKIPPED every Subtask as "a container", which is doubly wrong: a
            # subtask is a LEAF, and skipping meant nothing ever checked the three things that
            # actually rot on a parented board. `work_type()` is deliberately NOT run on them -
            # it answers Story|Task from a summary, and a subtask's type comes from its PARENT'S
            # type, which is a board read.
            def aud(*extra):
                return run_script("jira_feed.py", "audit", "--project", str(repo),
                                  "--acli", str(acli), "--jira-project", "TEST", *extra)

            board(("T-1", "Task", "Parent job"), ("T-2", "Subtask", "A real piece of work"),
                  parents={"T-2": "T-1"},
                  statuses={"T-1": "In Progress", "T-2": "In Progress"})
            code, out = aud()
            c.check("audit: a well-formed Subtask under a Task is OK, not noise",
                    code == 0 and "every type agrees" in out, out.strip()[:240])

            board(("T-1", "Task", "Parent job"), ("T-2", "Subtask", "Orphan"))
            code, out = aud()
            c.check("audit: a PARENTLESS Subtask is reported (it was silently skipped before)",
                    code == 1 and "T-2" in out and "no parent" in out.lower(),
                    out.strip()[:240])

            board(("T-1", "Epic", "Grouping epic"), ("T-2", "Subtask", "Wrong level"),
                  parents={"T-2": "T-1"})
            code, out = aud()
            c.check("audit: a Subtask parented to an EPIC is reported - Jira's level -1 sits "
                "under a Story or Task, never an Epic",
                    code == 1 and "T-2" in out and "Epic" in out, out.strip()[:240])

            board(("T-1", "Subtask", "A subtask"), ("T-2", "Subtask", "Nested under it"),
                  parents={"T-2": "T-1"})
            code, out = aud()
            c.check("audit: a NESTED Subtask is reported - hierarchyLevel -1 is the floor",
                    code == 1 and "T-2" in out, out.strip()[:240])

            # ⭐ This row is what replaced the cut parent-cascade (F6). The board still gets told
            # when a parent lags its children - it is just told by the audit, which reports, and
            # not by `start`, which writes.
            board(("T-1", "Task", "Parent job"), ("T-2", "Subtask", "Already shipping"),
                  parents={"T-2": "T-1"},
                  statuses={"T-1": "To Do Next", "T-2": "In Progress"})
            code, out = aud()
            c.check("audit: reports a parent that LAGS its children (replaces the cut cascade)",
                    code == 1 and "T-1" in out and "behind" in out.lower(),
                    out.strip()[:240])

            # A subtask flagged Bug by hand in the UI: still hands-off, same reason as always.
            board(("T-1", "Task", "Parent job"), ("T-2", "Bug", "Hand-flagged in the UI"),
                  parents={"T-2": "T-1"})
            code, out = aud("--apply")
            c.check("audit: a hand-flagged Bug under a parent is still left for close-out",
                    "retyped" not in get_state(state), out.strip()[:240])

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

            # ⭐ SCC-119, operator ruling: a Subtask is never labelled `Bug`. Breakage is recorded
            # on the MAIN ticket - the parent that owns the job. So `flag` still refuses a
            # subtask, but for the RIGHT reason: the old message called it a container, which is
            # false (it is a leaf), and told the operator to "flag the child ticket whose work
            # broke" - which IS the subtask, so the message argued against itself.
            set_state(state, types={"TEST-7": "Subtask", "TEST-4": "Task"},
                      statuses={"TEST-7": "Done", "TEST-4": "In Progress"},
                      parents={"TEST-7": "TEST-4"})
            code, out = jf("flag", "--key", "TEST-7", "--reason", "broke", "--apply")
            c.check("flag: a Subtask is refused and REDIRECTS to its parent by key (SCC-119)",
                    code == 2 and "TEST-4" in out
                    and get_state(state)["types"]["TEST-7"] == "Subtask",
                    out.strip()[:240])
            c.check("flag: the refusal no longer calls a Subtask a container - it is a leaf",
                    "container" not in out.lower(), out.strip()[:240])

            # A parentless subtask must still refuse rather than crash on the missing field. The
            # board should never hold one (audit reports it), but `flag` is a write verb and a
            # traceback here would read as "the board rejected it".
            set_state(state, types={"TEST-7": "Subtask"}, statuses={"TEST-7": "Done"})
            code, out = jf("flag", "--key", "TEST-7", "--reason", "broke", "--apply")
            c.check("flag: a PARENTLESS Subtask refuses cleanly, never tracebacks",
                    code == 2 and get_state(state)["types"]["TEST-7"] == "Subtask",
                    out.strip()[:240])

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

            # ⭐ SCC-119: this assertion is INVERTED from its first cut, which pinned the defect
            # in place. A Subtask is a LEAF (`hierarchyLevel: -1`), not a container - it carries
            # its own `chore/<KEY>-<slug>` branch and ships code exactly like a Task. Refusing it
            # here exited 2, and `post-commit-jira-start.sh` writes its once-per-branch marker
            # ONLY on exit 0 - so a subtask lane re-fired a board round-trip on EVERY commit, with
            # both streams swallowed, while its ticket sat in `To Do` for the whole build. That is
            # the exact failure SCC-113 exists to close, returning through a type check. Proven on
            # SCC-123, which shipped from `chore/SCC-123-evidence-extract` and was never seen
            # `In Progress`.
            set_state(state, types={"TEST-7": "Subtask"}, statuses={"TEST-7": "To Do"})
            code, out = jf("start", "--key", "TEST-7", "--apply")
            c.check("start: a Subtask is ACCEPTED - it is a leaf that carries a branch (SCC-119)",
                    code == 0 and get_state(state)["statuses"]["TEST-7"] == "In Progress",
                    out.strip()[:200])

            # The cascade was CUT (SCC-119, operator ruling): `start` moves the child and ONLY
            # the child. One board write, one verdict - which is what post-commit's
            # write-the-marker-only-on-settled logic depends on. `audit` reports a parent that
            # lags its children instead.
            set_state(state, types={"TEST-7": "Subtask", "TEST-4": "Task"},
                      statuses={"TEST-7": "To Do", "TEST-4": "To Do Next"},
                      parents={"TEST-7": "TEST-4"})
            code, out = jf("start", "--key", "TEST-7", "--apply")
            moved = [t["key"] for t in get_state(state).get("transitions", [])]
            c.check("start: the parent is NOT cascaded - one board write, one verdict",
                    code == 0 and moved == ["TEST-7"]
                    and get_state(state)["statuses"]["TEST-4"] == "To Do Next",
                    f"transitioned={moved} " + out.strip()[:160])

            # ⭐ "the board said no" and "I could not reach the board" are OPPOSITE instructions
            # - fix your key, versus try again later - and they shared exit 2 until the second
            # review pass. Worse, a missing binary escaped as an uncaught traceback (exit 1,
            # which is not a documented code at all), while /smh-quick-dev's table read exit 2
            # as "the key is wrong, mint a new ticket": a dead uplink instructed a DUPLICATE.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "To Do"})
            code, out = run_script("jira_feed.py", "start", "--key", "TEST-7", "--apply",
                                   "--project", str(repo), "--acli", str(tmp / "not-a-binary"))
            c.check("start: an UNREACHABLE board is exit 4, not 2 and not a traceback",
                    code == 4 and "transport" in out.lower(), out.strip()[:200])
            c.check("start: unreachable changes nothing on the board",
                    get_state(state)["statuses"]["TEST-7"] == "To Do"
                    and not get_state(state).get("transitions"))

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

            # Matches the START of a real invocation, in either shape this repo writes:
            #   shell/markdown   acli jira workitem transition --key …
            #   python argv      acli(binary, ["jira", "workitem", "transition", …
            # Anchoring on `acli` ALONE was wrong: `ln.find("acli")` locks onto a prose mention
            # earlier in the sentence ("make sure acli is authenticated, then run `acli jira
            # workitem transition … --yes`") and truncates the span before the real call.
            CALL = re.compile(r"""acli(?:\s+jira\s+workitem\s+transition
                                  |\s*\(.*?["']jira["']\s*,\s*["']workitem["']\s*,
                                                       \s*["']transition["'])""", re.X)

            def argv_of(ln: str) -> str:
                """The part of a line that is actually ARGV: inline code ends at its closing
            backtick, and a trailing `# …` comment is commentary, not an argument."""
                return ln.split("`", 1)[0].split("#", 1)[0]

            def unterminated(span: str) -> bool:
                t = span.rstrip()
                return (t.endswith(("\\", ","))
                        or span.count("[") > span.count("]")
                        or span.count("(") > span.count(")"))

            def offending_lines(lines: list[str]) -> list[int]:
                """Line numbers whose `acli … workitem transition` call omits `--yes`.

            ⭐ Anchored to the COMMAND SPAN, not to a window — a window let prose on the
            same line excuse a deleted flag, at a site this very ticket was fixing.

            ⭐ And every JOINED line is stripped too. The first cut stripped backticks and
            comments from the matched line, then appended the next two lines RAW — which
            re-opened the identical hole for WRAPPED calls, and `jira_feed.py`'s own
            transition is the repo's only executable call site and is wrapped. Deleting its
            `--yes` and writing `# --yes: see jira.md` below read clean.

            Known, deliberate limits (real call sites in this repo are fenced blocks or
            inline instructions, never these):
              * a line starting `>` is treated as commentary — jira.md TEACHES the trap by
                quoting the un-flagged form in a callout, and the positive control below
                pins that this stays true;
              * `docs/` is out of scope (see the caller).
            """
                out = []
                for n, ln in enumerate(lines, 1):
                    if ln.lstrip().startswith(("#", ">", "//")):
                        continue              # a comment quoting the trap is not a call site
                    # finditer, not search: `… --yes && acli … transition --key K2 --status X`
                    # is two call sites on one line and only the first was ever scanned.
                    for m in CALL.finditer(argv_of(ln) if "`" not in ln else ln):
                        span = argv_of(ln[m.start():])
                        j = n
                        while unterminated(span) and j < len(lines) and j - n < 6:
                            span += " " + argv_of(lines[j])       # STRIP each joined line too
                            j += 1
                        if "--yes" not in span:
                            out.append(n)
                            break
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
                # ⭐ The shapes that defeated the previous cut: the joined lines were appended
                # RAW, so a comment BELOW a wrapped call excused the missing flag - and the
                # repo's only executable call site is exactly this shape.
                ['t = acli(binary, ["jira", "workitem", "transition", "--key", args.key,',
                 '                  "--status", target])   # --yes is required here, see jira.md'],
                ['t = acli(binary, ["jira", "workitem", "transition", "--key", args.key,',
                 '                  "--status", target])',
                 '# --yes: see jira.md for why this flag is mandatory'],
                ['acli jira workitem transition --key K --status "Done" \\',
                 '# NOTE: --yes skips the confirm'],
                # Two calls on one line - only the first was ever scanned.
                ['acli jira workitem transition --key K1 --status "Done" --yes && '
             'acli jira workitem transition --key K2 --status "Done"'],
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
                # A compliant call wrapped over FOUR lines - the repo's own continuation style,
                # and the two-line lookahead indicted it. A guard that flags correct code
                # pressures the next author into a worse layout to appease it.
                ['acli jira workitem transition \\', '  --key K \\', '  --status "Done" \\',
                 '  --yes'],
                ['t = acli(binary, ["jira", "workitem", "transition",', '  "--key", args.key,',
                 '  "--status", target,', '  "--yes"])'],
                # A prose mention of `acli` BEFORE the real call: anchoring on the first `acli`
                # truncated the span before the command and indicted a compliant line.
                ['Make sure acli is authenticated, then run '
             '`acli jira workitem transition --key K --status "Done" --yes`.'],
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

    # ═══════════════════════════════════════════════════════════════════════════
    # finish — the close-out's Done, held back by the operator's own actions.
    # SCC-155. Written RED first.
    #
    # A close-out today writes `Done` unconditionally. When the walkthrough hands the
    # operator work ("install the board column", "run the memory audit"), that lands on a
    # ticket nobody will look at again - the record of what is still owed dies with the
    # lane. `finish` reads the artifact the close-out already requires and refuses to
    # close over open items.
    # ═══════════════════════════════════════════════════════════════════════════
    with TempDir() as tmp:
        repo, acli, state = build(tmp)

        def jf(*args: str) -> tuple[int, str]:
            os.environ["STUB_STATE"] = str(state)
            return run_script("jira_feed.py", args[0], "--project", str(repo),
                              "--acli", str(acli), *args[1:])

        def walkthrough(body: str) -> str:
            p = tmp / "wt.md"
            p.write_text(body, encoding="utf-8")
            return str(p)

        CLEAR = """# Walkthrough

## Your Actions

- [x] main absorbed
- [x] gate green

Nothing else is owed.
"""
        OWED = """# Walkthrough

## Your Actions

- [x] main absorbed
- [ ] Install the `Awaiting Review` column on the SCC board (Jira UI, operator-only)
      it is a two-minute change and nothing here can do it for you
- [ ] Run /memory-audit for the dead SOP path

## Something After
- [ ] this one is NOT under Your Actions and must not count
"""
        if c.block("jira_feed · legacy B: finish - Done held back by the operator's own actions (SCC-155)"):

            # ── nothing owed: closes exactly as the close-out does today ───────────
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(CLEAR),
                           "--apply")
            st = get_state(state)
            c.check("finish: a walkthrough with no open items closes the ticket",
                    code == 0 and st["statuses"]["TEST-7"] == "Done", out.strip()[:200])
            c.check("finish: the close carries --yes",
                    bool(st.get("transitions")) and all(t["yes"] for t in st["transitions"]),
                    "acli blocks on an interactive confirm no agent shell can answer")

            # ── something owed: HELD, and the board says what and why ──────────────
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(OWED),
                           "--apply")
            st = get_state(state)
            # Tied to a POSITIVE marker on purpose: "the status is not Done" is also true when
            # the verb does not exist, so on its own it is a control that can never go red.
            c.check("finish: an open operator action REFUSES to write Done",
                    st["statuses"]["TEST-7"] != "Done" and "held" in out.lower(),
                    f"{st['statuses']} {out.strip()[:120]}")
            c.check("finish: holding is its own exit code, not a generic failure",
                    code == 3, f"exit={code}")
            c.check("finish: the owed items are posted to the ticket",
                    any("Awaiting Review" in cm["body"]
                        and "memory-audit" in cm["body"]
                        for cm in st["comments"]),
                    str([cm["body"][:80] for cm in st["comments"]]))
            c.check("finish: a checkbox OUTSIDE ## Your Actions is not an operator action",
                    bool(st["comments"])
                    and not any("must not count" in cm["body"]
                                for cm in st["comments"]),
                    "the section is the contract; every other checklist in the file is not")
            c.check("finish: the ticket is labelled user-tasks so it reads at a glance",
                    "user-tasks" in st.get("labels", {}).get("TEST-7", []),
                    str(st.get("labels")))
            c.check("finish: a status ladder is attempted before giving up on the move",
                    any(t["status"] in ("Review Required", "Awaiting Review", "In Review")
                        for t in st.get("transitions", [])),
                    str(st.get("transitions")))

            # ── the ladder is per-board-optional: neither status installed ─────────
            # jira.md: a status a board does not have is "not installed yet", never an error.
            # SCC has neither of these today, so this is the LIVE path, not a corner case.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"},
                      stuck_status=True)
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(OWED),
                           "--apply")
            st = get_state(state)
            c.check("finish: a board with no review column still holds, and still exits 3",
                    code == 3 and st["statuses"]["TEST-7"] == "In Progress", out.strip()[:200])
            c.check("finish: with no column installed the LABEL still lands - it is the signal",
                    "user-tasks" in st.get("labels", {}).get("TEST-7", []), str(st.get("labels")))

            # ── FAIL CLOSED — the audit's HIGH finding ─────────────────────────────
            # A missing file or a renamed section must never read as "nothing owed". This is
            # the empty-input-reads-as-pass shape that `tests-must-gate-for-real` bans, and it
            # would close a ticket over work the operator was promised.
            # ⛔ These assert the REASON, not just the code. `argparse` exits 2 on an unknown
            # verb, so `code == 2` alone passes while `finish` does not exist at all - the
            # vacuous green this whole file exists to refuse. The message has to prove the
            # refusal came from the walkthrough check.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            code, out = jf("finish", "--key", "TEST-7",
                           "--walkthrough", str(tmp / "nope.md"), "--apply")
            c.check("finish: a MISSING walkthrough refuses; it never closes the ticket",
                    code == 2 and "walkthrough" in out.lower() and "usage:" not in out.lower()
                    and get_state(state)["statuses"]["TEST-7"] != "Done",
                    f"exit={code} {out.strip()[:160]}")

            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            code, out = jf("finish", "--key", "TEST-7",
                           "--walkthrough", walkthrough("# Walkthrough\n\nNo such section.\n"),
                           "--apply")
            c.check("finish: a walkthrough with NO '## Your Actions' refuses, never closes",
                    code == 2 and "your actions" in out.lower() and "usage:" not in out.lower()
                    and get_state(state)["statuses"]["TEST-7"] != "Done",
                    f"exit={code} {out.strip()[:160]}")

            # ── dry run is the default, like every other verb here ─────────────────
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(CLEAR))
            c.check("finish: without --apply it writes NOTHING",
                    code == 0 and "dry run" in out.lower()
                    and get_state(state)["statuses"]["TEST-7"] == "In Progress"
                    and not get_state(state).get("transitions"), out.strip()[:200])

            # The HELD path has its OWN dry-run guard, three writes further down (comment, label,
            # ladder). The case above only covers the close, and the mutation sweep proved the
            # difference: unguarding the HELD branch left the whole file green.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(OWED))
            st = get_state(state)
            c.check("finish: a HELD dry run posts nothing, labels nothing and moves nothing",
                    code == 3 and "dry run" in out.lower() and not st["comments"]
                    and not st.get("labels") and not st.get("transitions"),
                    f"exit={code} {out.strip()[:160]}")
            c.check("finish: the HELD dry run still PRINTS what it would have posted",
                    "memory-audit" in out, out.strip()[-200:])

            # ── the label write is read-modify-write, and that is load-bearing ─────
            # `--labels` REPLACES the set on the real acli. A writer that sends only `user-tasks`
            # passes every "is user-tasks on the ticket?" assertion while silently deleting
            # `quick-dev`, `parallel-ok` and everything else the board was carrying.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"},
                      labels={"TEST-7": ["quick-dev", "parallel-ok"]})
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(OWED),
                           "--apply")
            st = get_state(state)
            c.check("finish: adding user-tasks PRESERVES every label already on the ticket",
                    set(st["labels"]["TEST-7"]) == {"quick-dev", "parallel-ok", "user-tasks"},
                    str(st.get("labels")))

            # ── the ladder is a ladder: rung two is reached when rung one is absent ─
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"},
                      no_status=["Review Required"])
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(OWED),
                           "--apply")
            st = get_state(state)
            c.check("finish: a board missing the FIRST rung still lands on the second",
                    code == 3 and st["statuses"]["TEST-7"] == "Awaiting Review",
                    f"exit={code} {st.get('statuses')}")
            c.check("finish: and it says where it put the ticket, not just that it held",
                    "Awaiting Review" in out, out.strip()[-200:])

            # ── the close is VERIFIED, never assumed ───────────────────────────────
            # acli prints "Work item transitioned" and exits 0 whether or not the status moved.
            # Trusting the exit code would report a closed ticket that is still In Progress -
            # and the close-out would prune the branch on the strength of it.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"},
                      stuck_status=True)
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(CLEAR),
                           "--apply")
            st = get_state(state)
            # This case owns the DETECTION (acli exits 0 on a move it did not make, so the
            # read-back is the only thing that knows). The exit code it should carry is pinned
            # separately below - it was 2 when this was written, and the review moved every board
            # failure to 4; asserting the code in both places is how a contract change goes half-
            # applied.
            c.check("finish: a close that REPORTS success but does not land is caught",
                    code != 0 and st["statuses"]["TEST-7"] == "In Progress"
                    and "did not" in out.lower(), f"exit={code} {out.strip()[:160]}")

            # ── re-running on a closed ticket is a no-op, not a second transition ──
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "Done"})
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(CLEAR),
                           "--apply")
            st = get_state(state)
            c.check("finish: an already-Done ticket exits 0 and transitions nothing",
                    code == 0 and "already" in out.lower() and not st.get("transitions"),
                    f"exit={code} {out.strip()[:160]}")

            # ── the section ends at ANY heading of the same level or higher ────────
            # `## Something After` is covered above; a top-level `# ` is the other boundary, and
            # an appendix is exactly where a doc-wide checklist tends to live.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            code, out = jf("finish", "--key", "TEST-7", "--apply", "--walkthrough", walkthrough(
                "# Walkthrough\n\n## Your Actions\n\n- [x] all done\n\n"
            "# Appendix\n\n- [ ] a doc-wide checklist item that is not the operator's\n"))
            c.check("finish: a top-level `# ` heading closes the section too",
                    code == 0 and get_state(state)["statuses"]["TEST-7"] == "Done",
                    f"exit={code} {out.strip()[:160]}")

            # ── ⛔ REVIEW FINDING (critical): a FENCED `#` comment is not a heading ──
            # The house convention puts `# PC: run from the lobby root` inside a bash block, and
            # `## Your Actions` is exactly the section that carries "here is what you still have
            # to run". Read line-by-line with no fence awareness, that comment ENDS the section:
            # open_actions returns [] (not None, so no refusal fires) and the ticket closes over
            # work the operator was promised. 26 of the 92 walkthroughs already in _artifacts/
            # carry that shape. This is the SCC-154 `strip_fenced` lesson recurring - and
            # wf_common already ships _FENCE_RE.
            FENCED = """# Walkthrough

## Your Actions

Arm the hooks on the PC before anything else:

```bash
# PC: run from the lobby root
git config core.hooksPath .githooks
```

- [ ] Install the `Awaiting Review` column on the SCC board
- [ ] Run /memory-audit for the dead SOP path
"""
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(FENCED),
                           "--apply")
            st = get_state(state)
            c.check("finish: a `#` comment INSIDE a fence does not end the section",
                    code == 3 and st["statuses"]["TEST-7"] != "Done",
                    f"exit={code} {st.get('statuses')} {out.strip()[:160]}")
            c.check("finish: and both items below that fence are still owed",
                    any("Awaiting Review" in cm["body"] and "memory-audit" in cm["body"]
                        for cm in st["comments"]),
                    str([cm["body"][:80] for cm in st["comments"]]))

            # The mirror direction, and it must hold at the same time: a checkbox that is only an
            # EXAMPLE inside a fence is not an owed action. A fix that counts everything would
            # trade a fail-open for a ticket nobody can ever close.
            EXAMPLE = """# Walkthrough

## Your Actions

Write your own rows in this shape:

```markdown
- [ ] a template row that is an EXAMPLE, not an obligation
```

Nothing is actually owed.
"""
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(EXAMPLE),
                           "--apply")
            c.check("finish: a `- [ ]` inside a fence is an EXAMPLE, not an owed action",
                    code == 0 and get_state(state)["statuses"]["TEST-7"] == "Done",
                    f"exit={code} {out.strip()[:160]}")

            # The nastiest shape of the same bug: the section HEADING itself quoted in a fence,
            # earlier in the file. `start` matched the fenced example, its ticked rows returned
            # [], and the REAL section below was never read - Done written straight over two live
            # obligations. A doc teaching the convention is exactly where this shape appears.
            QUOTED_HEAD = """# Walkthrough

Write the hand-off like this:

```markdown
## Your Actions

- [x] an EXAMPLE row, already ticked
```

## Your Actions

- [ ] Install the `Awaiting Review` column on the SCC board
- [ ] Run /memory-audit for the dead SOP path
"""
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(QUOTED_HEAD),
                           "--apply")
            st = get_state(state)
            c.check("finish: a FENCED `## Your Actions` example never wins over the real section",
                    code == 3 and st["statuses"]["TEST-7"] != "Done",
                    f"exit={code} {st.get('statuses')} {out.strip()[:160]}")

            # ── ⛔ REVIEW FINDING: the published contract says continuations ride ────
            # smh-quick-dev.md declares as a MACHINE CONTRACT: "Continuation lines indented under
            # it ride along." They did not - only the bullet line was collected, so the half of
            # the instruction that says WHY reached nobody. Either the reader honours the
            # contract or the contract is a lie; this pins the reader.
            CONT = """# Walkthrough

## Your Actions

- [ ] Install the `Awaiting Review` column on the SCC board
      it is a two-minute change and nothing here can do it for you
- [ ] Run /memory-audit
"""
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(CONT),
                           "--apply")
            st = get_state(state)
            c.check("finish: an item's indented continuation line rides along to the board",
                    any("two-minute change" in cm["body"] for cm in st["comments"]),
                    str([cm["body"][:120] for cm in st["comments"]]))
            c.check("finish: and the continuation does NOT become a second owed item",
                    any("**2** things" in cm["body"] for cm in st["comments"]),
                    str([cm["body"][:120] for cm in st["comments"]]))

            # ── ⛔ REVIEW FINDING: user-tasks is a one-way door ──────────────────────
            # The HELD arm adds the label; the close arm never removed it. jira.md defines it as
            # "the walkthrough leaves something only the operator can do", and on a board with no
            # review column the runtime message calls it THE signal - so a Done ticket carrying
            # it poisons the very filter it exists to feed. The sibling half of this same change
            # is built on "the strip is the point"; this writer only ever added.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"},
                      labels={"TEST-7": ["user-tasks", "quick-dev"]})
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(CLEAR),
                           "--apply")
            st = get_state(state)
            c.check("finish: closing clean STRIPS user-tasks - the hold is over",
                    "user-tasks" not in st.get("labels", {}).get("TEST-7", []),
                    str(st.get("labels")))
            c.check("finish: and the strip leaves every other label alone",
                    "quick-dev" in st.get("labels", {}).get("TEST-7", []), str(st.get("labels")))

            # ── ⛔ REVIEW FINDING: exit 2 is overloaded onto BOARD failures ──────────
            # The docstring and BOTH close-out tables fix exit 2 as "refused - no walkthrough or
            # no section; NOTHING was written; fix the artifact". A transition that was issued and
            # did not land is a board problem with a write already attempted, and the agent that
            # follows the table goes hunting for a defect in a walkthrough that is fine. 4 is the
            # code that already means "transport, not a verdict; retry".
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"},
                      stuck_status=True)
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(CLEAR),
                           "--apply")
            c.check("finish: a close that does not land is TRANSPORT (4), not a refusal (2)",
                    code == 4, f"exit={code} {out.strip()[:160]}")

            # A comment that fails to post is the same class - and worse, the early return used to
            # skip the label and the ladder below it, so the ticket was held while saying nothing
            # about why. The hold must still be SIGNALLED even when the narration fails.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"},
                      comment_fail=True)
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(OWED),
                           "--apply")
            st = get_state(state)
            c.check("finish: a comment that fails to post is TRANSPORT (4), not a refusal (2)",
                    code == 4, f"exit={code} {out.strip()[:160]}")
            c.check("finish: and the label still lands, so the hold is not silent",
                    "user-tasks" in st.get("labels", {}).get("TEST-7", []), str(st.get("labels")))

            # ── ⛔ REVIEW FINDING: re-running a hold STACKS comments ─────────────────
            # render_user_tasks tells the operator to tick a box and re-run, so repeated
            # invocation is the designed happy path, not an edge. Each run posted another "User
            # tasks" comment, each asserting a different count, with nothing saying which is
            # current. `devrecord` in this same file is documented as "exactly one per ticket,
            # updated in place, never stacked" - this verb needs the same property.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(OWED), "--apply")
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(CONT),
                           "--apply")
            st = get_state(state)
            c.check("finish: a second hold UPDATES the user-tasks comment, never stacks it",
                    len([cm for cm in st["comments"] if "User tasks" in cm["body"]]) == 1,
                    str([cm["body"][:60] for cm in st["comments"]]))
            c.check("finish: and the surviving comment is the CURRENT one",
                    any("two-minute change" in cm["body"] for cm in st["comments"]),
                    str([cm["body"][:120] for cm in st["comments"]]))

            # ── ⛔ REVIEW FINDING: the ladder advances on an UNVERIFIABLE read ───────
            # The rung's success test is a fresh view_fields(strict=False), which returns None on
            # any transport blip - indistinguishable from "the move did not take". On a blip the
            # loop marched to rung two and moved the ticket a SECOND time, to a column nobody
            # asked for, then reported "left at In Progress - no review column on this board".
            # Cannot-verify is not the same as did-not-move: stop and say so.
            # blind_after=1: the opening read succeeds (so we reach the ladder at all), and every
            # read-back after it fails. Without the count this case is vacuous - see the stub.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"},
                      blind_after=1)
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(OWED),
                           "--apply")
            st = get_state(state)
            moves = [t["status"] for t in st.get("transitions", [])]
            # ⛔ Both assertions below need a POSITIVE anchor. "at most one move" and "the string
            # is absent" are BOTH true when the script crashes, which is exactly what the sweep
            # caught: a mutant that removed the `back is None` guard raised an AttributeError,
            # produced no output and no second transition, and this case stayed green.
            c.check("finish: an unverifiable ladder read does NOT march on to the next rung",
                    code == 3 and len(moves) <= 1, f"exit={code} {moves}")
            c.check("finish: and it says the status is UNKNOWN, not that the column is missing",
                    "UNKNOWN" in out and "no review column" not in out, out.strip()[-220:])

            # The CommonMark close rule: a fence closes only on the SAME marker kind, at least as
            # long. Without it a ``` inside a ~~~ block (or a shorter run inside a longer one)
            # ends the fence early and the section is read as markup again - the precise rule
            # SCC-154 paid for in check_gate, so it is pinned here rather than re-learned.
            # The fixture has to DISCRIMINATE: everything that must stay invisible is INSIDE the
            # ~~~ block, and it includes an OPEN box. Correct code sees zero obligations and
            # closes; a mutant that lets any fence marker close any fence ends the ~~~ at the
            # inner ``` , exposes that box, and holds. A first draft of this case put the open box
            # outside the block and passed under the mutant either way.
            NESTED = """# Walkthrough

## Your Actions

~~~markdown
Write your rows like this:
```
- [ ] an EXAMPLE obligation that must never count
```
~~~

Nothing is actually owed.
"""
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(NESTED),
                           "--apply")
            c.check("finish: a ``` inside a ~~~ block does not close it early",
                    code == 0 and get_state(state)["statuses"]["TEST-7"] == "Done",
                    f"exit={code} {out.strip()[:180]}")

            # A SECOND `## Your Actions` - a close-out appending its own asks is exactly how one
            # appears. Taking only the first heading dropped everything under the later one.
            TWICE = """# Walkthrough

## Your Actions

- [x] the first round is done

## Notes

## Your Actions

- [ ] the round that was silently dropped
"""
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(TWICE),
                           "--apply")
            c.check("finish: a SECOND `## Your Actions` section is read too, never dropped",
                    code == 3 and get_state(state)["statuses"]["TEST-7"] != "Done",
                    f"exit={code} {out.strip()[:160]}")

            # An unchecked box with no text is still an unchecked box. Requiring a character made
            # an empty obligation invisible - the fail-open shape, one level in.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            code, out = jf("finish", "--key", "TEST-7", "--apply", "--walkthrough", walkthrough(
                "# Walkthrough\n\n## Your Actions\n\n- [ ]\n"))
            c.check("finish: an EMPTY unchecked box still holds the ticket",
                    code == 3, f"exit={code} {out.strip()[:160]}")

            # `###` groups the operator's asks; it must NOT end the section. The narrowing
            # direction was pinned (the appendix case); this is the widening one.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            code, out = jf("finish", "--key", "TEST-7", "--apply", "--walkthrough", walkthrough(
                "# Walkthrough\n\n## Your Actions\n\n### Board\n\n- [ ] install the column\n"))
            c.check("finish: a `###` sub-heading GROUPS the asks, it does not end the section",
                    code == 3 and "install the column" in out,
                    f"exit={code} {out.strip()[:160]}")

            # ── ⛔ REVIEW FINDING #24: acli exits 0 on writes it did not perform ────
            # The close path already read back its transition for exactly this reason. The HELD
            # path took the comment on faith, so `swallow` (accepted-then-lost, exit 0) produced
            # "HELD, moved to Review Required" on a ticket with NO comment at all - the state the
            # verb's own error message exists to prevent. The label is the signal; the comment is
            # the only thing that says WHY, so it gets the same read-back.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"},
                      swallow=True)
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(OWED),
                           "--apply")
            st = get_state(state)
            c.check("#24 a comment acli ACCEPTED and lost is caught by a read-back",
                    code == 4 and not st["comments"], f"exit={code} {out.strip()[:200]}")
            c.check("#24 and the hold is still signalled by the label despite the lost comment",
                    "user-tasks" in st.get("labels", {}).get("TEST-7", []), str(st.get("labels")))

            # ── the operator installed the column, and it is named "Review Required" ──
            # SCC now carries it (2026-08-14), so the fall-through that used to be the LIVE path
            # is now the corner case. It is the FIRST rung: a board that has it must land there,
            # not on a legacy name.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"},
                      no_status=["Awaiting Review", "In Review"])
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(OWED),
                           "--apply")
            st = get_state(state)
            c.check("finish: a board carrying `Review Required` lands the hold there",
                    code == 3 and st["statuses"]["TEST-7"] == "Review Required",
                    f"exit={code} {st.get('statuses')}")

            # ⛔ The exact status STRING is board configuration, not a property of this code, and
            # a wrong literal makes the ladder silently never fire. `--review-status` overrides
            # the whole ladder so a rename on the board is a flag, never an edit here.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(OWED),
                           "--apply", "--review-status", "Needs Daniel")
            st = get_state(state)
            c.check("finish: --review-status overrides the ladder outright",
                    code == 3 and st["statuses"]["TEST-7"] == "Needs Daniel",
                    f"exit={code} {st.get('statuses')}")

            # Already parked on a rung: do nothing. Comparing only against the rung being tried
            # dragged a ticket an operator had advanced to `In Review` BACKWARDS.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Review"})
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(OWED),
                           "--apply")
            st = get_state(state)
            c.check("finish: a ticket already on a rung is NOT dragged back down the ladder",
                    st["statuses"]["TEST-7"] == "In Review" and not st.get("transitions"),
                    f"{st.get('statuses')} {st.get('transitions')}")

            # ═══════════════════════════════════════════════════════════════════════
            # SCC-163 Part B — what may go in `## Your Actions` is now CHECKED.
            # Written RED first, against a REAL corpus (acceptance B1).
            #
            # Step 5 of both review commands permits exactly three things to be left for the
            # operator what only THEY can decide: a product decision, or a ticket transition
            # they have reserved. (It named a third, the main merge, until the operator's
            # 2026-08-17 ruling retired it - the sign-off is the DECISION.) A row assigning
            # them a ticket BORN FROM REVIEW FINDINGS - mint it, file it, rule on where it goes -
            # is the retired defect. It is prose, nothing checked it, and it was broken the same
            # day it was written: AVCH-58 shipped three unchecked rows, zero of them operator
            # calls, and `finish` held the ticket on Review Required. That is the loop.
            #
            # ⛔ THE HARD PART IS THE FALSE POSITIVES, NOT THE DETECTION. Measured before the rule
            # was written: `open_actions` over every .md in `_artifacts/` finds 101 walkthroughs
            # carrying the section and 25 unchecked rows. The phrase list read literally
            # (mint|file|open...ticket|fold...into|rule on|decide whether|your call|board
            # placement) flags 8 of those 25 - and at most 4 are true positives. "Rule on A1" is
            # an acceptance dispute; "Rule the landing order" is merge sequencing. Both are
            # genuine operator calls. So a bare verb is NEVER a trigger: the detector fires only
            # on a trigger verb PAIRED WITH a ticket-work object, and the survivors of that
            # measurement are pinned below as negative controls.
            # ═══════════════════════════════════════════════════════════════════════
            FIXTURES = Path(__file__).resolve().parent / "fixtures"
            avch58 = (FIXTURES / "avch58_your_actions.md").read_text(encoding="utf-8")

            import jira_feed as jf_mod  # noqa: E402 - the tests run scripts/ on sys.path

            def flagged(text: str) -> list[str]:
                return [row for row, _ in jf_mod.banned_action_rows(text)]

            # ── B1 · the known-positive, from the real AVCH-58 walkthrough ─────────
            hits = flagged(avch58)
            c.check("B1 · AVCH-58 row 1 (fold into AVCH-54 / mint its own key) is FLAGGED",
                    len(hits) == 1 and "symlink defect" in hits[0],
                    f"the ticket's named known-positive; got {hits}")
            c.check("B1 · ...and row 2, a settled deferral, is NOT flagged (B5: status notes)",
                    not any("requirements.txt" in h for h in hits), f"{hits}")
            c.check("B1 · ...and row 3, a branch-freshness note, is NOT flagged (B5)",
                    not any("behind" in h for h in hits), f"{hits}")

            # ── B2/B3/B4 · the three named cases from acceptance B3 ────────────────
            # Two negative controls and one positive, and the first two are the trap: a detector
            # keyed on a bare ticket key false-reds both, because both CONTAIN one.
            def one_row(row: str) -> str:
                return f"# W\n\n## Your Actions\n\n- [ ] {row}\n"

            c.check("B2 · 'Merge AVCH-59 to main' is ALLOWED (a main merge, and it has a key)",
                    flagged(one_row("Merge AVCH-59 to main")) == [],
                    "keying on a bare ticket key false-reds the allowed classes")
            c.check("B3 · 'Move SCC-99 to Done' is ALLOWED (a ticket transition, verb + key)",
                    flagged(one_row("Move SCC-99 to Done")) == [],
                    "a transition is one of Step 5's three permitted classes")
            c.check("B4 · 'Mint a ticket for the N deferred items' is FLAGGED",
                    len(flagged(one_row("Mint a ticket for the N deferred items"))) == 1,
                    "the banned shape with no ticket key in it at all")

            # ── B5 · the live corpus is the regression suite ───────────────────────
            # Verbatim rows from walkthroughs already in `_artifacts/`. Every one is a genuine
            # operator call that the naive phrase list flags. If the detector reds any of these it
            # is worse than nothing: it teaches the next agent to stop writing honest rows.
            REAL_ALLOWED = [
                "**Rule the landing order.** Recommended: **SCC-126 lands first** - merging this "
            "lane first would leave the AP autopilot instructed to read a rule file that does "
            "not exist yet.",
                "**Decide whether the CONCERNS is worth clearing before the merge.** Unchanged by "
            "the absorb and deliberately not actioned here.",
                "**Rule on A1.** It is not delivered: no replay, no timings, no identical-verdict "
            "comparison against SCC-154's table.",
                "**Rule on A2's missed target.** 68.57 s measured against <= 60 s.",
                "**Rule on A6's phrasing** - it asks for a \"sweep script template\" to be grepped, "
            "and the standing SCC-145 ruling keeps sweep scripts out of the tree.",
                "**Close out and merge** - `/smh-close-task-merge-tree` with `--expect-key SCC-123`. "
            "The lane is pushed, clean, 0 behind `origin/main`.",
                "**Pass SCC-126 the restamp requirement** (`ap_reconciled: 024f58a`, or drop the "
            "stamp) - without it, `main` is red once both lanes land.",
            ]
            for i, row in enumerate(REAL_ALLOWED, 1):
                c.check(f"B5.{i} · a REAL operator call from the corpus is not flagged",
                        flagged(one_row(row)) == [], f"{row[:80]}...")

            # ...and the true positives the same corpus carries, so B5 cannot pass by a detector
            # that simply never fires (the vacuous green this suite exists to refuse).
            REAL_BANNED = [
                "**SOP-nag ticket (optional, your call from the plan's 9b):** the suite-count "
            "staleness now has three recorded instances in two days.",
                "Decide whether finding 13 earns a ticket: the vendor skill is still installed and "
            "BMAD re-emits it.",
                "**File the follow-on Task** from the review section's \"Follow-on\" block (one "
            "ticket: check_gate's remaining edges).",
            ]
            for i, row in enumerate(REAL_BANNED, 1):
                c.check(f"B5.{i}x · a REAL banned row from the same corpus IS flagged",
                        len(flagged(one_row(row))) == 1, f"{row[:80]}...")

            # ── B11 · each banned SHAPE is pinned ALONE ────────────────────────────
            # ⛔ Found by a SURVIVING MUTANT, not by reading. Deleting the `fold ... into <KEY>`
            # pattern outright left the whole suite green: the only row exercising it was AVCH-58's,
            # which ALSO says "board placement is the operator's" and so kept flagging through a
            # different pattern. A shape acceptance B2 names by name was therefore unpinned, and
            # deleting it would have been invisible. Each row below matches exactly ONE pattern.
            SHAPES = [
                ("fold into <KEY>", "Fold the one-line fix into AVCH-54 (it hits that lane directly)"),
                ("board placement", "Board placement is the operator's, not mine"),
                ("create/mint", "Mint its own AVCH ticket for the remainder"),
                ("earns a ticket", "Decide whether finding 13 earns a ticket"),
                ("rule on + ticket", "Rule on whether the residue ticket should exist"),
                ("ticket + your call", "The nag ticket is optional, your call"),
            ]
            for label, row in SHAPES:
                c.check(f"B11 · the '{label}' shape is flagged on its own",
                        len(flagged(one_row(row))) == 1,
                        f"if only a multi-shape row covers this pattern, deleting the pattern is "
                    f"invisible: {row}")

            # ── B10 · the FALSE POSITIVES a review probe found, pinned ─────────────
            # ⛔ These four flagged under the first implementation, which searched for a banned VERB
            # anywhere in the row and a ticket OBJECT anywhere in the row, independently. `file` and
            # `open` are among the commonest NON-verbs in this vocabulary, and co-occurrence cannot
            # tell "open a ticket" (create) from "open the ticket" (go read it). None of these came
            # from the live corpus - they are the rows an honest walkthrough writes NEXT - so
            # without them the regression returns silently the first time someone says "the ticket
            # is still open". The fix binds verb and object into one phrase; these hold that line.
            FALSE_POSITIVE_PROBE = [
                "The SCC-99 ticket is still open from last sprint",
                "Ticket SCC-12 remains open; nothing owed here",
                "Open the ticket and read the Dev Record",
                "The task file is in `_artifacts/`",
            ]
            for i, row in enumerate(FALSE_POSITIVE_PROBE, 1):
                c.check(f"B10.{i} · a NOUN-sense 'open'/'file' row is not flagged",
                        flagged(one_row(row)) == [],
                        f"verb x object must be ONE phrase, not two searches: {row}")

            # ── B6 · fenced examples are documentation, not rows (B4) ──────────────
            # `jira_feed._unfenced` was written for exactly this after a live miss (SCC-154,
            # ported from check_gate). Reuse it; a re-derived fence walker is how the close-marker
            # rule gets lost a second time.
            FENCED = (
                "# W\n\n## Your Actions\n\n"
            "A doc that TEACHES the convention quotes the banned shape:\n\n"
            "```markdown\n- [ ] Mint a ticket for the deferred items\n```\n\n"
            "- [x] nothing is actually owed\n"
            )
            c.check("B6 · a banned-shape row inside a fence is an EXAMPLE, not a row",
                    flagged(FENCED) == [],
                    "counting a fenced template holds a ticket nobody can ever close")

            # ── B7 · finish REFUSES by default (ARMED 2026-08-16, SCC-164 clause 3) ─
            # ⭐ THIS CASE INVERTED, and the inversion is the point. It shipped WARN on
            # 2026-08-15 ("1. yes") as a MEASUREMENT WINDOW; SCC-164 § ARMING clause 3 closed
            # the window on a measured count — 0 hits across the 11 post-cutoff walkthroughs,
            # while still firing on 3 legacy ones that really do hand ticket work over. The
            # ordering objection that justified WARN ("a block fires AFTER the merge") does not
            # survive the detail that this runs BEFORE the board is touched: a refusal writes
            # nothing, so there is no half-written state to trade against.
            BANNED_WT = (
                "# W\n\n## Your Actions\n\n"
            "- [ ] Rule on the symlink defect - fold the one-line fix into AVCH-54, or mint "
            "its own AVCH key. Board placement is the operator's.\n"
            )
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"})
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(BANNED_WT),
                           "--apply")
            c.check("B7 · finish prints the banned-row banner", "BANNED ACTION ROW" in out,
                    out.strip()[-400:])
            c.check("B7 · ...and names the row it objects to", "AVCH-54" in out,
                    out.strip()[-400:])
            c.check("B7 · ...and REFUSES with no flag at all - armed is the DEFAULT now",
                    code == 2,
                    f"exit={code} - clause 3 flips the default; a flag-only block is the "
                    f"disarmed state wearing an arming ticket")
            c.check("B7b · ...and the refusal says the board was not touched",
                    "Nothing was written" in out, out.strip()[-400:])

            # ── B8 · the opt-out is NAMED, LOGGED, and a real discriminator ─────────
            # ⛔ THE VACUITY TRAP THAT CAUGHT THE FIRST VERSION: with no such flag defined,
            # argparse exits 2 on "unrecognized arguments" - the same 2 a real refusal returns -
            # so `code == 2` alone was satisfied by the flag NOT EXISTING. Every exit code here
            # is therefore paired with output only the real path produces.
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(BANNED_WT),
                           "--apply", "--warn-actions")
            c.check("B8 · --warn-actions restores the warn and does NOT block",
                    code == 3 and "BANNED ACTION ROW" in out,
                    f"exit={code} - 3 is finish's own held verdict, unchanged by the warn: "
                    f"{out.strip()[-300:]}")
            c.check("B8b · ...and the opt-out is LOGGED, not silent",
                    "--warn-actions given" in out and "on the record" in out,
                    f"a bypass nobody can see in the transcript is the shape this whole gate "
                    f"exists to refuse: {out.strip()[-300:]}")
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(CLEAR),
                           "--apply")
            c.check("B8c · ...and a CLEAN walkthrough still closes, armed and all",
                    code == 0,
                    f"exit={code} - a gate that refuses everything is as broken as one that "
                    f"refuses nothing: {out.strip()[-300:]}")
            # The explicit flag stays accepted: docs, older invocations and the SOP all name it.
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(BANNED_WT),
                           "--apply", "--strict-actions")
            c.check("B8d · --strict-actions is still accepted and still refuses",
                    code == 2 and "BANNED ACTION ROW" in out,
                    f"exit={code} - dropping the flag would break every doc that names it: "
                    f"{out.strip()[-300:]}")

            # ── B9 · the standalone inspection entry point ─────────────────────────
            code, out = run_script("jira_feed.py", "check-actions", "--walkthrough",
                                   str(FIXTURES / "avch58_your_actions.md"))
            c.check("B9 · check-actions reports the fixture's one banned row", code == 1
                    and "symlink defect" in out, f"exit={code} {out.strip()[-300:]}")
            code, out = run_script("jira_feed.py", "check-actions", "--walkthrough",
                                   walkthrough(CLEAR))
            c.check("B9 · ...and exits 0 on a clean walkthrough", code == 0,
                    f"exit={code} {out.strip()[-200:]}")

        # ── SCC-174 · a FORKED Dev Record stops reading as "two lanes" ─────────
        # `devrecord` picks update-vs-create off the SLUG, never off --key, so filing one lane
        # under two slugs is exactly how a ticket GETS two ids. `check` used to read two ids as
        # self-evidently two lanes and exit 0 - blind precisely when the bug happens (the slugs
        # differ) and loud only once it has been fixed (the slugs match). AVCH-59 on 2026-08-15
        # is the live instance: /smh-quick-dev filed under `main-write-gate`, the close-out
        # passed `avch-59-main-write-gate` - the ceremony's own wording - and the gate blessed
        # the pair. The id string cannot settle it. The repo can.
        if c.block("SCC-174 check: a forked Dev Record is not 'the designed state'"):

            def jfp(project: Path, *args: str) -> tuple[int, str]:
                os.environ["STUB_STATE"] = str(state)
                return run_script("jira_feed.py", args[0], "--project", str(project),
                                  "--acli", str(acli), *args[1:])

            FED = "9.1 - Widget Archive. Acceptance criteria 1. AC-1 archive."
            WIDGET, ROSTER = "chore/TEST-7-widget-archive", "chore/TEST-7-roster-filter"

            def rec(sid: str, cid: str, stage: str = "close-out") -> dict:
                return {"id": cid,
                        "body": f"Dev Record - {sid} ({stage}, 2026-08-15)\n\nDecisions made"}

            def forked(project: Path) -> tuple[int, str]:
                """ONE lane's two slugs: the branch slug, and the truncation quick-dev filed."""
                set_state(state, description=FED,
                          comments=[rec("TEST-7-widget-archive", "1", "quick-dev"),
                                    rec("widget-archive", "2")])
                return jfp(project, "check", "--key", "TEST-7")

            # ── F1 · the live shape: one manifest, one branch, two records ────────
            one = make_lane_repo(tmp, "lane_one",
                                 manifests=(("2026-08-15_widget", WIDGET),),
                                 branches=(WIDGET,), on=WIDGET)
            code, out = forked(one)
            c.check("F1 · one lane filed under two slugs -> exit 1, not blessed",
                    code == 1, f"exit={code} {out.strip()[:400]}")
            # ⛔ Asserted WITH the backticks. `widget-archive` is a SUBSTRING of
            # `test-7-widget-archive`, so a bare containment test passes on any message that
            # names only the real lane - the assertion would be green against a check that
            # never noticed the fork at all.
            c.check("F1 · ...and it names the slug nothing claims, as a slug",
                    "`widget-archive`" in out and "`test-7-widget-archive`" in out,
                    out.strip()[:400])
            c.check("F1 · ...and it says which record is NEWEST",
                    "newest: `widget-archive`" in out.lower(), out.strip()[:400])
            c.check("F1 · ...and it does NOT still call the pair the designed state",
                    "designed state" not in out, out.strip()[:400])

            # ── F4 · the negative control: two manifested lanes on one ticket ─────
            # A follow-on lane rides the ticket it came from rather than minting a key, so N
            # lanes -> N records is the DESIGNED state and must stay exit 0. If this ever goes
            # red the fork check was widened into "two records are bad", which is the count-based
            # check SCC-113 already removed once.
            two = make_lane_repo(tmp, "lane_two",
                                 manifests=(("2026-08-15_widget", WIDGET),
                                            ("2026-08-15_roster", ROSTER)),
                                 branches=(WIDGET, ROSTER), on=WIDGET)
            set_state(state, description=FED,
                      comments=[rec("TEST-7-widget-archive", "1"),
                                rec("TEST-7-roster-filter", "2")])
            code, out = jfp(two, "check", "--key", "TEST-7")
            c.check("F4 · two manifested lanes -> exit 0, the designed-state line survives",
                    code == 0 and "one per lane" in out, f"exit={code} {out.strip()[:400]}")

            # ── the `origin/` arm · a landed follow-on whose local branch was pruned ──
            # /cicd-push-e2e prunes the lane branch on landing. Local-refs-only would read every
            # landed lane's record as a fork the moment a second lane joins the ticket - F17.
            landed = make_lane_repo(tmp, "lane_landed",
                                    manifests=(("2026-08-15_widget", WIDGET),),
                                    branches=(WIDGET,), remotes=(ROSTER,), on=WIDGET)
            set_state(state, description=FED,
                      comments=[rec("TEST-7-widget-archive", "1"),
                                rec("TEST-7-roster-filter", "2")])
            code, out = jfp(landed, "check", "--key", "TEST-7")
            c.check("the origin/ ref alone proves a lane (a landed, locally-pruned follow-on)",
                    code == 0 and "one per lane" in out, f"exit={code} {out.strip()[:400]}")

            # ── the manifest arm · a lane with no ref left anywhere ───────────────
            # The durable half: months later both refs are gone and the committed task.yaml is
            # the only thing that still says the lane existed.
            pruned = make_lane_repo(tmp, "lane_pruned",
                                    manifests=(("2026-08-15_widget", WIDGET),
                                               ("2026-08-15_roster", ROSTER)),
                                    branches=(WIDGET,), on=WIDGET)
            set_state(state, description=FED,
                      comments=[rec("TEST-7-widget-archive", "1"),
                                rec("TEST-7-roster-filter", "2")])
            code, out = jfp(pruned, "check", "--key", "TEST-7")
            c.check("the committed manifest alone proves a lane (no branch left at all)",
                    code == 0 and "one per lane" in out, f"exit={code} {out.strip()[:400]}")

            # ── a manifest git does not track proves NOTHING ──────────────────────
            # The lobby keeps other repos under a gitignored `Projects/` and a copy of its own
            # tree under `.claude/worktrees/`. A `Path.glob("**/task.yaml")` reads both and
            # would clear a fork using a slug that belongs to a different repo entirely.
            foreign = make_lane_repo(tmp, "lane_foreign",
                                     manifests=(("2026-08-15_widget", WIDGET),),
                                     branches=(WIDGET,),
                                     untracked=(("2026-08-15_roster", ROSTER),), on=WIDGET)
            set_state(state, description=FED,
                      comments=[rec("TEST-7-widget-archive", "1"),
                                rec("TEST-7-roster-filter", "2")])
            code, out = jfp(foreign, "check", "--key", "TEST-7")
            c.check("an UNTRACKED manifest under a gitignored dir does not claim a lane",
                    code == 1 and "`test-7-roster-filter`" in out,
                    f"exit={code} {out.strip()[:400]}")

            # ── the split: what `check` may trust vs what the DEFAULT may trust ───
            # An untracked manifest that git is not ignoring either. `check` must not count it -
            # a stray file is not a lane, and the fork verdict has nothing to cross-check it
            # against. `lane_slug_here` may, because it intersects with the branch you are ON,
            # so an unseen manifest can only ever name your own lane.
            (foreign / "_artifacts" / "_main" / "stray").mkdir(parents=True)
            ((foreign / "_artifacts" / "_main" / "stray" / "task.yaml")
             .write_text(f"task_key: TEST-7\nbranch: {ROSTER}\n", encoding="utf-8"))
            code, out = jfp(foreign, "check", "--key", "TEST-7")
            c.check("an UNCOMMITTED manifest does not claim a lane either (check reads --cached)",
                    code == 1 and "`test-7-roster-filter`" in out,
                    f"exit={code} {out.strip()[:400]}")
            # /smh-quick-fix writes its task.yaml in the same breath as the Dev Record, so a
            # default that demanded a commit first would be dead on the one lane that needs it.
            fresh = make_lane_repo(tmp, "lane_fresh", manifests=(("2026-08-15_widget", WIDGET),),
                                   branches=(WIDGET, ROSTER), on=ROSTER)
            m = fresh / "_artifacts" / "_main" / "2026-08-16_roster"
            m.mkdir(parents=True)
            (m / "task.yaml").write_text(f"task_key: TEST-7\nbranch: {ROSTER}\n",
                                         encoding="utf-8")
            code, out = jfp(fresh, "devrecord", "--decision", "x")
            c.check("F3 · a task.yaml written but not yet committed still names YOUR lane",
                    code == 0 and "Dev Record - TEST-7-roster-filter" in out,
                    f"exit={code} {out.strip()[:300]}")

            # ── "cannot tell" must never be reported as "designed state" ──────────
            # None is not the empty set. If the instrument is missing the honest answer is that
            # it is missing - blessing the pair because the evidence could not be READ is the
            # same failure in a new coat.
            code, out = forked(repo)          # `repo` is a fixture tree, not a git checkout
            c.check("no git checkout -> exit 1 and says the lanes could not be read, not 0",
                    code == 1 and "not a git checkout" in out,
                    f"exit={code} {out.strip()[:400]}")

            # ── F3 · ONE slug source, and it is the lane's own manifest ───────────
            code, out = jfp(one, "devrecord", "--decision", "x")
            c.check("F3 · --story defaults to the branch slug in this lane's task.yaml",
                    code == 0 and "Dev Record - TEST-7-widget-archive" in out,
                    f"exit={code} {out.strip()[:300]}")
            code, out = jfp(one, "devrecord", "--story", "widget-archive", "--decision", "x")
            # ⛔ NOT asserted on the `[WARN]` marker. `devrecord` already warns about the
            # missing walkthrough on this fixture, so the marker is present either way and the
            # check would have been green against a build that never noticed the wrong slug.
            c.check("F3 · a slug that is not this lane's is WARNED, naming both",
                    "is not this lane's slug" in out and "`TEST-7-widget-archive`" in out,
                    out.strip()[:300])
            code, out = jfp(one, "devrecord", "--story", "TEST-7-widget-archive",
                            "--decision", "x")
            c.check("F3 · ...and the lane's OWN slug is silent (positive control)",
                    code == 0 and "is not this lane" not in out, out.strip()[:300])
            # Optional does not mean guessable: with no source to default from, rendering a
            # headerless record would fork the ticket a third way. Both halves of "no source"
            # get their own case, and the SECOND one is here because the sweep demanded it -
            # mutant F3c (drop the manifest cross-check, so any prefixed branch is a lane)
            # SURVIVED against the non-git fixture alone: `rev-parse` fails there, so the
            # branch guard answered and the cross-check was never reached.
            code, out = jfp(repo, "devrecord", "--decision", "x")
            c.check("F3 · off a git checkout entirely -> --story is still REQUIRED",
                    code == 2 and "no task.yaml declares the branch" in out,
                    f"exit={code} {out.strip()[:300]}")
            stray = make_lane_repo(tmp, "lane_stray",
                                   manifests=(("2026-08-15_widget", WIDGET),),
                                   branches=(WIDGET, ROSTER), on=ROSTER)
            code, out = jfp(stray, "devrecord", "--decision", "x")
            c.check("F3 · a prefixed branch NO manifest declares is not a lane to default from",
                    code == 2 and "no task.yaml declares the branch" in out,
                    f"exit={code} {out.strip()[:300]}")

    # ── G (SCC-175) · the merge row is COMPUTED, and a tick is only a claim ───────────────
    with TempDir() as tmp:
        if c.block("G · SCC-175: the merge row is computed from the repo, never from a tick"):
            import jira_feed  # noqa: E402 — the tests run scripts/ on sys.path

            def git(repo, *a):
                return subprocess.run(["git", *a], cwd=str(repo), capture_output=True, text=True)

            def lane(name: str, *, land: bool, row: str, tick: str = " ",
                     prune: bool = False, verdict: bool = False, commit_wt: bool = True):
                """A repo whose `main` has (or has not) absorbed a lane, plus its artifacts."""
                repo = tmp / name
                repo.mkdir()
                bare = tmp / f"{name}.git"
                git(repo, "init", "-q", "-b", "main")
                git(repo, "config", "user.email", "t@t.t")
                git(repo, "config", "user.name", "t")
                (repo / "README").write_text("x\n")
                git(repo, "add", "-A"), git(repo, "commit", "-qm", "base", "--no-verify")
                git(repo, "init", "--bare", "-q", str(bare))
                git(repo, "remote", "add", "origin", str(bare))
                git(repo, "push", "-q", "--no-verify", "origin", "main")

                branch = "chore/SCC-999-lane"
                git(repo, "checkout", "-q", "-b", branch)
                d = repo / "_artifacts/_main/2026-08-16_lane"
                d.mkdir(parents=True)
                (d / "task.yaml").write_text(f"task_key: SCC-999\nbranch: {branch}\n")
                (d / "walkthrough.md").write_text(
                    "# W\n\n" + ("Verdict: PASS @ HEADSHA\n\n" if verdict else "")
                    + f"## Your Actions\n\n- [{tick}] {row}\n")
                git(repo, "add", "-A")
                if commit_wt:
                    git(repo, "commit", "-qm", "lane work", "--no-verify")
                tip = git(repo, "rev-parse", "HEAD").stdout.strip()
                if verdict:  # rewrite the placeholder now that the sha exists, and re-commit
                    wtp = d / "walkthrough.md"
                    wtp.write_text(wtp.read_text().replace("HEADSHA", tip))
                    git(repo, "add", "-A"), git(repo, "commit", "-qm", "verdict", "--no-verify")
                    tip = git(repo, "rev-parse", "HEAD").stdout.strip()
                # ⛔ Only go back to `main` when the lane LANDS. On an unlanded fixture the
                # artifacts exist solely on the lane branch, so checking out main deletes the
                # very walkthrough the case is about — the first cut did exactly that and died
                # in `committed_copy` on a directory that no longer existed.
                if land:
                    git(repo, "checkout", "-q", "main")
                    git(repo, "merge", "-q", "--no-ff", "--no-verify", branch, "-m", "merge")
                    git(repo, "push", "-q", "--no-verify", "origin", "main")
                git(repo, "fetch", "-q", "origin")
                if prune:
                    git(repo, "branch", "-q", "-D", branch)
                return repo / "_artifacts/_main/2026-08-16_lane/walkthrough.md"

            DOOR_ROW = "**Merge and close out** — `/smh-close-task-merge-tree --expect-key SCC-999`"

            # G1 · the row that HELD every landed lane now clears — on evidence, not a tick.
            st = jira_feed.merge_row_state(lane("g1", land=True, row=DOOR_ROW))
            c.check("G1 · an OPEN merge row whose lane IS on origin/main is SATISFIED",
                    st is not None and st["satisfied"] and st["source"] == "HEAD",
                    str(st))

            # G2 · ⭐ THE POINT. A tick is a claim; the claim is checked.
            st = jira_feed.merge_row_state(lane("g2", land=False, row=DOOR_ROW, tick="x"))
            c.check("G2 · a TICKED merge row on a lane that never landed is NOT satisfied",
                    st is not None and not st["satisfied"] and "NOT an ancestor" in st["why"],
                    "a `- [x]` closes the ticket on a claim nobody checked - this is the "
                    f"self-certification house law bans: {st}")

            # G3 · negative control: not landed, still open -> still holds, as it always did.
            st = jira_feed.merge_row_state(lane("g3", land=False, row=DOOR_ROW))
            c.check("G3 · (control) an open row on an unlanded lane still HOLDS",
                    st is not None and not st["satisfied"], str(st))

            # G4 · the pruned-lane fallback (F6a). SCC-162 and SCC-163 were BOTH already pruned
            # local and remote when this was designed, so without this arm the recogniser could
            # not compute an answer for either of the two live instances it exists to fix.
            st = jira_feed.merge_row_state(
                lane("g4", land=True, row=DOOR_ROW, prune=True, verdict=True))
            c.check("G4 · a PRUNED lane resolves through the walkthrough's `Verdict: … @ sha`",
                    st is not None and st["satisfied"], str(st))

            # G5 · unresolvable -> HOLD, naming what it tried. Never a silent pass.
            wt5 = lane("g5", land=True, row=DOOR_ROW, prune=True)
            (wt5.parent / "task.yaml").write_text("task_key: SCC-999\n")   # no branch:
            st = jira_feed.merge_row_state(wt5)
            c.check("G5 · an UNRESOLVABLE tip HOLDS and says what it tried",
                    st is not None and not st["satisfied"] and "could not be resolved" in st["why"]
                    and "Verdict" in st["why"],
                    "an unresolvable tip is not evidence of a merge: " + str(st))

            # G6 · an uncommitted tick is still only a claim, and still gets checked.
            wt6 = lane("g6", land=False, row=DOOR_ROW)
            wt6.write_text(wt6.read_text().replace("- [ ]", "- [x]"))      # uncommitted tick
            st = jira_feed.merge_row_state(wt6)
            c.check("G6 · an UNCOMMITTED tick does not satisfy the row",
                    st is not None and st["source"] == "HEAD" and not st["satisfied"],
                    "SCC-169's tick was left uncommitted in the main checkout and later wiped "
                    f"by a reset - the committed copy is the only one that survives: {st}")

            # G6b · ⛔ THE CASE THAT ACTUALLY PINS `HEAD` (F18), AND G6 DOES NOT.
            # The declared mutant M2 (read the working tree instead of HEAD) SURVIVED G6 — and it
            # was right to. A ticked row still MATCHES the row regex, and the verdict comes from
            # ancestry, which does not read the file at all, so both sources agree. The only
            # divergence is a row that exists in the COMMITTED walkthrough and not on disk:
            # deleting it locally is how an owed merge silently stops being checked. Working-tree
            # read -> no row -> None -> no hold. HEAD read -> found -> held.
            wt6b = lane("g6b", land=False, row=DOOR_ROW)
            wt6b.write_text("# W\n\n## Your Actions\n\n- [ ] something else entirely\n")
            st = jira_feed.merge_row_state(wt6b)
            c.check("G6b · a merge row DELETED from the working tree is still found in HEAD",
                    st is not None and not st["satisfied"] and st["source"] == "HEAD",
                    "the committed walkthrough owes a merge; editing the local copy must not "
                    f"be how that stops being checked: {st}")

            # G7 · the recogniser itself, against the LIVE corpus classes measured 2026-08-16.
            for row, want, why in (
                    (DOOR_ROW, True, "names a door"),
                    ("The merge itself — lands via this branch's PR", True, "canonical phrase"),
                    ("**Land it** — `/cicd-push-e2e`", True, "the other door"),
                    ("**Rule the landing order.** Recommended: SCC-126 lands first", False,
                     "a real operator decision"),
                    ("**Decide whether the CONCERNS is worth clearing before the merge.**", False,
                     "a real operator decision"),
                    ("Try the lane on something real", False, "SCC-162's genuinely open row")):
                c.check(f"G7 · recogniser: {'MERGE' if want else 'not a merge row'} — {why}",
                        jira_feed.is_merge_row(row) == want, repr(row))

            # G8 · no merge row at all is not the same as a satisfied one.
            st = jira_feed.merge_row_state(lane("g8", land=True, row="Install the board column"))
            c.check("G8 · a walkthrough with no merge row returns None, not a verdict",
                    st is None, str(st))


    # ══ SCC-193 Part B · `## Your Actions` holds DECISIONS, never the ceremony's steps ══════
    #
    # SLIP #4 OF SIX, MEASURED ON SCC-164'S LANDING (walkthrough at 5dcc1b7, 2026-08-16). The
    # agent wrote the close-out's OWN REMAINING STEPS into `## Your Actions` as operator tasks:
    #
    #     - [ ] **Click **Merge** on the PR.** ...
    #     - [ ] **Then re-invoke** `/smh-close-task-merge-tree --after-merge SCC-164`. ...
    #
    # `finish` then correctly HELD the ticket — on work that was the AGENT's. The cause is that
    # `## Your Actions` has no content schema: `open_actions()` is a `- [ ]` scanner, presence is
    # grep-checked by the door, and content was never checked at all.
    #
    # ⭐ AND THE WORDING RULING (operator, 2026-08-17) IS WHY THIS IS A REFUSAL AND NOT A STYLE
    # NOTE: the sign-off is the operator's DECISION TO PROCEED — the word `approved`, or invoking
    # one of the two doors. From that word on, every step is the ceremony's and the agent runs
    # it. So "click Merge" and "re-invoke the door" are not merely misfiled; under the ruling
    # they are not operator tasks at all.
    #
    # ⛔ WHAT THIS MUST NOT FLAG, AND WHY EACH ONE WOULD WEDGE A LANDING:
    #   * the canonical ledger row `- [x] The merge itself — lands via this branch's PR`. The
    #     door MANDATES it (SCC-183 Step 3) and SCC-175 verifies it against ancestry. Flagging
    #     it would make the door's own required row a refusal — and post-merge the only fix is
    #     a commit on `main`, which is the write the gate refuses. That is the 2026-08-15
    #     `reset --hard` incident, rebuilt.
    #   * a real operator DECISION that happens to say "merge" — five such rows exist in the
    #     145-walkthrough corpus (jira_feed.py:1519). Those are exactly what the section is for.
    if c.block("SCC-193 B · the ceremony's own steps are not `Your Actions` entries"):
        import jira_feed  # noqa: E402

        # The two rows, verbatim from SCC-164's walkthrough at 5dcc1b7.
        CLICK = ("**Click **Merge** on the PR.** `main-write-gate` is a required check and "
                 "`bypass_actors` is empty, so nothing lands until you do. That click is the "
                 "sign-off.")
        REINVOKE = ("**Then re-invoke** `/smh-close-task-merge-tree --after-merge SCC-164`. "
                    "That second call is what writes `Done` to SCC-164 and all six riders; the "
                    "door opens the PR and **stops**.")

        def wt(*rows: str) -> str:
            body = "\n".join(f"- [ ] {r}" for r in rows)
            return f"# W\n\n## Your Actions\n\n{body}\n"

        # ⛔ Existence is its own case. While this block is RED the function does not exist,
        # and an AttributeError kills the FILE - a crash reads nothing like a failed assertion
        # (`red-test-can-die-before-its-assertion`). It also means a mutant that deletes the
        # detector outright is killed here rather than sailing past a crashed suite.
        have = hasattr(jira_feed, "ceremony_rows")
        c.check("B0 the content check exists", have,
                "jira_feed.ceremony_rows is missing - `## Your Actions` has no content rule")
        if not have:
            return c.finish()

        rows = jira_feed.ceremony_rows(wt(CLICK, REINVOKE))
        c.check("B1 RED: SCC-164's two rows are BOTH refused",
                len(rows) == 2, f"{len(rows)} flagged: {rows}")
        c.check("B1 ...and the refusal says what the section is for, in the ruling's words",
                bool(rows) and all("only the operator decides" in r[1] for r in rows),
                str(rows))

        # B2 · the controls. Every one of these is a row the section EXISTS to carry.
        for row, why in (
                ("**Decide whether the CONCERNS is worth clearing before the merge.**",
                 "a product decision that names the merge"),
                ("**Rule the landing order.** Recommended: SCC-126 lands first, then SCC-129",
                 "merge SEQUENCING is the operator's"),
                ("Install the board column", "an ordinary operator task"),
                ("Try the lane on something real", "SCC-162's genuinely open row"),
                ("**Ship the copy change to the marketing site when you are ready**",
                 "a product decision containing 'ship'"),
                # ⛔ THE BOUNDARY THE RULING DRAWS. A bare door invocation is one of the three
                # FORMS the operator's decision takes ("the way I approve you to push or close
                # is by saying approved or one of the 2 / commands"), so it is a decision, not a
                # chore - and SCC-175 already owns whether it still holds. What is refused is
                # the ceremony's CONTINUATION after that word, which is the agent's.
                ("**Merge and close out** - `/smh-close-task-merge-tree --expect-key SCC-999`",
                 "a bare door invocation IS the decision's form"),
                ("**Land it** - `/cicd-push-e2e`", "the other door, same reason")):
            c.check(f"B2 CONTROL: not flagged — {why}",
                    not jira_feed.ceremony_rows(wt(row)), repr(row))

        # ⭐ B1b · THE CASE T-M4 PROVED WAS MISSING. SCC-164's re-invoke row ALSO carries
        # `--after-merge`, so it matched two patterns at once and removing the re-invoke one
        # changed nothing the suite could see. A row that trips exactly one pattern is what
        # isolates it - otherwise the redundancy IS the test's blind spot.
        c.check("B1b a re-invocation with no --after-merge is still refused",
                len(jira_feed.ceremony_rows(wt("Then re-invoke the close-out when I have merged"))) == 1,
                "the re-invoke pattern must stand on its own")

        # B3 · ⛔ the ledger row, both ways. This is the wedge control.
        c.check("B3 CONTROL: the canonical merge row is the door's LEDGER, never a ceremony step",
                not jira_feed.ceremony_rows(
                    "# W\n\n## Your Actions\n\n"
                    "- [x] **The merge itself** — lands via this branch's PR\n"),
                "SCC-183 mandates this row; flagging it makes the door refuse itself")
        # ⭐ B3b · THE CASE T-M2 PROVED WAS MISSING. The two rows above do not trip ANY
        # pattern even without the exemption, so dropping `if MERGE_PHRASE in row` was
        # invisible - the control was passing for the wrong reason. This row would be refused
        # on its own merits, and is spared ONLY by the exemption. That is the wedge: SCC-183
        # mandates a ledger row, and refusing it post-merge leaves a fix that can only be
        # committed on `main`.
        # ⛔ AND THE BOX MUST BE OPEN. The first cut of this control used `- [x]`, and
        # `open_actions` returns UNCHECKED rows only - so the row never reached a pattern at
        # all, exemption or not, and T-M2 survived a second time against a control written
        # specifically to kill it. A ticked row is not evidence about a rule that only ever
        # sees open ones.
        c.check("B3b CONTROL: an OPEN ledger row is spared even when it names the click",
                not jira_feed.ceremony_rows(
                    "# W\n\n## Your Actions\n\n"
                    "- [ ] **The merge itself** - click **Merge** on the PR to land it\n"),
                "without the MERGE_PHRASE exemption this row IS flagged (`click **Merge`) - "
                "which is what makes it the control that pins the exemption")

        c.check("B3 CONTROL: ...and an OPEN one is still SCC-175's business, not this check's",
                not jira_feed.ceremony_rows(
                    "# W\n\n## Your Actions\n\n"
                    "- [ ] **The merge itself** — lands via this branch's PR\n"),
                "post-merge the only fix would be a commit on main - the write the gate refuses")

        # B4 · a fenced example is documentation, not an entry (the SCC-154 close-marker rule,
        # reused through open_actions rather than re-derived).
        c.check("B4 CONTROL: a row quoted inside a code fence is documentation",
                not jira_feed.ceremony_rows(
                    "# W\n\n## Your Actions\n\n```\n- [ ] " + CLICK + "\n```\n"),
                "fenced rows are invisible to open_actions, and must stay so here")

        # B5 · the check runs where it is cheap: `check-actions`, which the door's Step 3 calls
        # BEFORE the PR opens. Post-merge is where fixing it costs a commit on main.
        with TempDir() as tmp:
            path = tmp / "walkthrough.md"
            path.write_text(wt(CLICK, REINVOKE), encoding="utf-8")
            rc, out = run_script("jira_feed.py", "check-actions", "--walkthrough", str(path))
            c.check("B5 check-actions reports ceremony rows and exits non-zero",
                    rc != 0 and "only the operator decides" in out, out.strip()[-500:])
            clean = tmp / "clean.md"
            clean.write_text(wt("**Decide whether to ship the copy change.**"), encoding="utf-8")
            rc2, out2 = run_script("jira_feed.py", "check-actions", "--walkthrough", str(clean))
            c.check("B5 CONTROL: a walkthrough of real decisions passes",
                    rc2 == 0, out2.strip()[-300:])

        # ⭐ B6 · THE CASE T-M5 PROVED WAS MISSING, and it is the acceptance criterion itself.
        # B5 drives `check-actions`; SCC-193 S2 says `finish` must refuse "exit 2, nothing
        # written". Nothing tested that, so deleting the refusal from `cmd_finish` outright
        # left every case green - the detector existed and the close-out ignored it.
        with TempDir() as tmp2:
            repo2, acli2, state2 = build(tmp2)
            wt2 = tmp2 / "wt.md"
            wt2.write_text(wt(CLICK, REINVOKE), encoding="utf-8")
            set_state(state2, types={"TEST-9": "Task"}, statuses={"TEST-9": "In Progress"})
            os.environ["STUB_STATE"] = str(state2)
            rc3, out3 = run_script("jira_feed.py", "finish", "--key", "TEST-9",
                                   "--project", str(repo2), "--acli", str(acli2),
                                   "--walkthrough", str(wt2), "--apply")
            st3 = get_state(state2)
            c.check("B6 finish REFUSES a walkthrough carrying the ceremony's steps",
                    rc3 == 2 and "only the operator decides" in out3,
                    f"exit={rc3}: " + out3.strip()[-300:])
            c.check("B6 ...and NOTHING was written to the board",
                    st3["statuses"].get("TEST-9") == "In Progress"
                    and not st3.get("transitions") and not st3.get("comments"),
                    f"{st3.get('statuses')} transitions={st3.get('transitions')} "
                    f"comments={len(st3.get('comments') or [])}")

            # The control: the same lane with an honest decision row closes as it always did.
            wt3 = tmp2 / "wt3.md"
            wt3.write_text(wt("**Decide whether to ship the copy change.**"), encoding="utf-8")
            set_state(state2, types={"TEST-9": "Task"}, statuses={"TEST-9": "In Progress"})
            rc4, out4 = run_script("jira_feed.py", "finish", "--key", "TEST-9",
                                   "--project", str(repo2), "--acli", str(acli2),
                                   "--walkthrough", str(wt3), "--apply")
            c.check("B6 CONTROL: a real decision row HOLDS (3), it is not refused (2)",
                    rc4 == 3, f"exit={rc4}: " + out4.strip()[-200:])

        # ⭐ B3c · THE EXEMPTION IS A SHAPE, NOT A SUBSTRING - and this is the bypass the
        # edge-case lens executed. `MERGE_PHRASE in row` waved through the WHOLE row, so
        # appending five words to SCC-164's verbatim defect row cleared the check written to
        # refuse that exact row. An exemption a defect can opt into is not an exemption.
        # The ledger row's subject IS the phrase (all 11 in the live corpus begin with it);
        # a row that merely MENTIONS it is some other row.
        c.check("B3c RED: appending the ledger phrase does NOT excuse a ceremony row",
                len(jira_feed.ceremony_rows(wt(CLICK + " That is the merge itself."))) == 1,
                "the exemption must key on the row's SUBJECT, or any row can claim it")
        c.check("B3c ...and mid-row is not the subject either",
                len(jira_feed.ceremony_rows(
                    wt("**Then re-invoke** the door once the merge itself has landed."))) == 1,
                "trailing or mid-row: only the SUBJECT position is the ledger")
        # ⛔ DECLARED DESIGN, stated so it is never mistaken for an oversight: a row that
        # genuinely OPENS as the ledger row keeps the exemption for its WHOLE text. The door
        # writes that row and its prose legitimately names the click (B3b), and a false refusal
        # there is only fixable by a commit on `main` - the write the gate refuses. The bypass
        # this closes is the one that was EXECUTED: a ceremony row claiming the exemption by
        # mentioning the phrase. Narrowing further re-opens the wedge for no measured gain.

        # ⭐ B7 · THE BLIND LENS'S F4. `\bthen\s+(?:invoke|run|call)\b` bound a verb to
        # NOTHING - every sibling pattern names a ceremony-specific object. These three are
        # plain operator decisions, and the third is the boundary note's own carve-out (a bare
        # door invocation is one of the three FORMS of the decision). The refusal is default-on
        # and hard, and `finish` runs AFTER the merge - when the fix is a commit on `main`,
        # the write the gate refuses. A false positive here is unfixable by design.
        for row, why in (
                ("**Decide the pricing tier for the launch**, then run the campaign when "
                 "you are happy.", "a product decision that happens to say 'then run'"),
                ("**Rule on the vendor**: pick A or B, then call the account manager.",
                 "'then call' about a person, not a script"),
                ("**Approve the copy**, then invoke `/cicd-push-e2e` when the marketing "
                 "site is ready.", "a door invocation IS the decision's form (the boundary note)")):
            c.check(f"B7 CONTROL: not flagged — {why}",
                    not jira_feed.ceremony_rows(wt(row)), repr(row))
        c.check("B7 ...but the ceremony's own SECOND HALF still is",
                len(jira_feed.ceremony_rows(wt("**Merge it**, then run the close-out's "
                                               "second half for the riders."))) == 1,
                "bound to the ceremony, the pattern must still catch the ceremony")

        # ⭐ B9 · ONE ROW PER PATTERN, because `ceremony_rows` breaks on the FIRST match and
        # every fixture above trips pattern 1 or 3 first. The test-adequacy audit measured
        # patterns 2, 4 and 6 each SURVIVING deletion with the suite green - exactly the
        # redundancy blind spot T-M4 caught once already, in this same table. A row that trips
        # exactly one pattern is the only thing that isolates it.
        for row, which in (
                ("Merge the pull request when the demo is done", "2 · merge x pull request"),
                ("Finish with --after-merge SCC-999", "4 · the ceremony's second half"),
                ("run .agents/scripts/jira_feed.py finish", "6 · running the machinery")):
            got = jira_feed.ceremony_rows(wt(row))
            c.check(f"B9 pattern {which} stands on its own", len(got) == 1,
                    f"{len(got)} flagged for {row!r}: {got}")

        # ⭐ B11 · THE THREE ROWS THE LITERAL-CORRECTNESS LENS EXECUTED, each one a place the
        # detector contradicted its own documentation. All were hard exit-2 refusals of an
        # operator DECISION, fired by `finish` after the merge - when the fix is a commit on
        # `main`, the write the gate refuses.
        for row, why in (
                ("Re-invoke `/cicd-push-e2e` once staging is verified.",
                 "a bare door invocation, refused on the two characters `re-` while "
                 "'Then invoke /cicd-push-e2e' passed"),
                ("**Decide whether to merge the PR before the marketing launch.**",
                 "the SOP names 'a product decision that happens to mention a merge' as exempt"),
                ("Run the memory audit (`python3 .agents/scripts/memory_audit.py`) when you "
                 "have a moment.",
                 "cmd_finish's own docstring names this as the row that must HOLD a ticket")):
            c.check(f"B11 CONTROL: not flagged — {why[:60]}",
                    not jira_feed.ceremony_rows(wt(row)), repr(row))
        # ⛔ AND THE TEETH SURVIVE ALL THREE NARROWINGS. Each of these is the same shape with
        # the ceremony actually named, or with an ACT the decision carve-out must not excuse.
        for row, why in (
                ("Re-invoke the door once I have merged", "re-invoke bound to the ceremony"),
                ("**Decide** to click **Merge** on the PR", "a decision prefix is not a way in"),
                ("Run `python3 .agents/scripts/jira_feed.py finish --key SCC-9`",
                 "this ceremony's own machinery, still refused")):
            got = jira_feed.ceremony_rows(wt(row))
            c.check(f"B11 ...still REFUSED — {why}", len(got) == 1, f"{len(got)}: {got}")

        # ⭐ B10 · THE OPT-OUT IS LOGGED, and a warn nobody records is the
        # `vscode-hides-git-hook-output` shape the banner's own comment names. Deleting the log
        # line was measured as a survivor: the flag worked and the record of using it did not.
        with TempDir() as tmp5:
            repo5, acli5, state5 = build(tmp5)
            wt5 = tmp5 / "wt.md"
            wt5.write_text(wt(CLICK, REINVOKE), encoding="utf-8")
            set_state(state5, types={"TEST-9": "Task"}, statuses={"TEST-9": "In Progress"})
            os.environ["STUB_STATE"] = str(state5)
            rc6, out6 = run_script("jira_feed.py", "finish", "--key", "TEST-9",
                                   "--project", str(repo5), "--acli", str(acli5),
                                   "--walkthrough", str(wt5), "--warn-actions", "--apply")
            c.check("B10 --warn-actions does NOT refuse, and logs that it was chosen",
                    rc6 != 2 and "Logged opt-out, on the record" in out6
                    and "2 ceremony row(s)" in out6, f"exit={rc6}: " + out6.strip()[-400:])

        # ⭐ B8 · BOTH FAMILIES IN ONE RUN. `cmd_finish` returned 2 on the ceremony rows before
        # `banned_action_rows` was ever computed, so a walkthrough carrying both was reported
        # one family at a time - two fix-and-re-run round trips for one file, and the second
        # family only discovered after the first was fixed. `check-actions` already reported
        # both; the two entry points have to agree about what is wrong with the file.
        with TempDir() as tmp4:
            repo4, acli4, state4 = build(tmp4)
            wt4 = tmp4 / "wt.md"
            wt4.write_text(wt(CLICK, "Rule on the symlink defect - fold the one-line fix into "
                                     "AVCH-54, or mint its own AVCH key. Board placement is "
                                     "the operator's."), encoding="utf-8")
            set_state(state4, types={"TEST-9": "Task"}, statuses={"TEST-9": "In Progress"})
            os.environ["STUB_STATE"] = str(state4)
            rc5, out5 = run_script("jira_feed.py", "finish", "--key", "TEST-9",
                                   "--project", str(repo4), "--acli", str(acli4),
                                   "--walkthrough", str(wt4), "--apply")
            c.check("B8 finish reports BOTH families in one run, then refuses once",
                    rc5 == 2 and "only the operator decides" in out5
                    and "BANNED ACTION ROW" in out5, f"exit={rc5}: " + out5.strip()[-600:])

    # ══ SCC-198 · `start` clones the successor and HANDS THE BATON ON ══════════════════════
    #
    # ⛔ THE DEFECT THIS CLOSES, MEASURED. SCC-190's cycle instruction lived only in its own
    # description - first line, capitals: "BEFORE CLOSING THIS OUT CLONE A NEW ONE WITH NO SUB
    # TASKS". It did not fire. The operator had to say it out loud, and their words are the
    # whole design brief: "its writen in the ticket I just dont know if you will read it."
    #
    # ⭐⛔ THE LABEL IS A BATON, NOT A PROPERTY - operator ruling 2026-08-17, which REPLACED an
    # earlier two-tag design of mine where both markers sat on the ticket permanently:
    #   "I dont like the two tags - once you move it to In Progress we switch the tag. this
    #    avoids issues with the tag linked to the script cloning again too. this way it can
    #    only [clone] one. it now clones, it moves the original, and switches the tag to the
    #    bugs-and-updates."
    # So exactly ONE ticket carries `running-bug-list` at any moment - the next cycle,
    # un-started - and `bugs-and-updates` is what a cycle wears AFTER it has started.
    #
    # WHY THAT IS STRONGER, which is also why these cases are shaped the way they are. A
    # PERMANENT trigger can fire twice, so every guard against a second clone has to ASK THE
    # BOARD: a network call that can be wrong, slow or unavailable. A BATON is consumed by
    # use - after the swap the trigger is gone, so a re-fire cannot clone, with nothing to
    # query and nothing to get wrong. A2b is that guard, and it is the load-bearing case here.
    #
    # ⭐ THE INVARIANT EVERY BRANCH BELOW IS DERIVED FROM, rather than patched onto:
    #      a rolling ticket holds `running-bug-list` until its successor EXISTS,
    #      and not one moment longer.
    # Hence clone BEFORE swapping (A1b - the clone inherits labels, and that IS the handoff);
    # swap even when this run did not do the cloning (A4b); and WITHHOLD the swap when no
    # successor was made (A5c, A7), which is what lets the next `start` retry.
    #
    # ⭐ AT START, NOT AT CLOSE-OUT. Running the rolling ticket is exactly the window in which
    # the system has NO open home for discovered work - the only open one is the one being
    # run. Cloning at start means cycle N+1 exists from the lane's first minute.
    if c.block("SCC-198 · start clones the successor and hands the baton on"):
        ROLL, TRIG = "bugs-and-updates", "running-bug-list"

        def started(tmp, *, labels, statuses=None, search=None, **extra):
            repo, acli, state = build(tmp)
            set_state(state, types={"TEST-7": "Task"},
                      statuses=statuses or {"TEST-7": "To Do"},
                      labels={"TEST-7": labels}, search=search or [], **extra)
            os.environ["STUB_STATE"] = str(state)
            rc, out = run_script("jira_feed.py", "start", "--key", "TEST-7",
                                 "--acli", str(acli), "--apply")
            return rc, out, get_state(state)

        with TempDir() as tmp:
            rc, out, st = started(tmp, labels=[TRIG])
            lab = st.get("labels", {})
            c.check("A1 a ticket carrying the baton clones its successor on start",
                    st.get("clones") == ["TEST-7"], f"clones={st.get('clones')} rc={rc}")
            c.check("A1a ...and the run still reports the transition it was asked for",
                    rc == 0 and st.get("statuses", {}).get("TEST-7") == "In Progress",
                    f"rc={rc} {st.get('statuses')}")
            # ⭐ BOTH ENDS OF THE HANDOFF. Asserting only that a clone happened would pass an
            # implementation that swapped FIRST and handed on a dead marker - the cycle would
            # end silently one ticket later, and every case above would still be green.
            c.check("A1b the SUCCESSOR inherits the baton (clone carries labels)",
                    TRIG in lab.get("TEST-CLONE", []),
                    f"successor labels={lab.get('TEST-CLONE')}")
            c.check("A1c the ORIGINAL gives the baton up and takes the identity label",
                    lab.get("TEST-7") == [ROLL], f"TEST-7 labels={lab.get('TEST-7')}")

        # ⛔ A1d · `--labels` REPLACES the whole set on the real acli (pinned independently at
        # "finish: adding user-tasks PRESERVES the labels already there"). A swap that sends
        # only its own two markers silently strips everything else the ticket carried.
        with TempDir() as tmp:
            _, _, st = started(tmp, labels=[TRIG, "user-tasks"])
            c.check("A1d the swap PRESERVES every other label the ticket carried",
                    set(st.get("labels", {}).get("TEST-7", [])) == {ROLL, "user-tasks"},
                    f"TEST-7 labels={st.get('labels', {}).get('TEST-7')}")

        # ⛔ A2 · THE CONTROL THAT IS THE WHOLE POINT. Every OTHER ticket in the system goes
        # through this seam - `/smh-quick-fix`, `/smh-quick-dev`, `/smh-plan-task` and the
        # post-commit recorder, which fires on EVERY commit. A trigger that leaked here would
        # clone a rolling ticket on ordinary work.
        with TempDir() as tmp:
            rc, out, st = started(tmp, labels=[])
            c.check("A2 CONTROL: an ordinary ticket clones NOTHING", not st.get("clones"),
                    f"clones={st.get('clones')}")
        # ⭐⛔ A2b · THE LOAD-BEARING CASE - the baton's entire payoff. A ticket whose trigger
        # is already SPENT cannot clone, and no board query is consulted to decide it. Under
        # the two-tag design this same ticket WOULD have cloned, and only a search standing
        # between it and a duplicate would have stopped it.
        with TempDir() as tmp:
            rc, out, st = started(tmp, labels=[ROLL])
            c.check("A2b CONTROL: a SPENT baton clones nothing, with nothing to query",
                    not st.get("clones"),
                    "bugs-and-updates says a cycle already STARTED; it must never say DO")

        # ⭐ A3 · ZERO EXTRA BOARD READS on the normal path, COUNTED rather than assumed.
        # `view_fields` already puts `labels` on its whitelist, so the trigger is a list
        # membership test on data already in memory.
        # ⛔ THE BASELINE IS **2**, AND THAT IS MEASURED, NOT GUESSED: `cmd_start` reads once
        # to see the status and once AFTER the transition to verify it landed. The first cut
        # of this case asserted 1 and went red against unmodified code - a number taken from
        # the plan instead of from the program. Pinning the real baseline is what makes this a
        # cost gate: an implementation that re-read the ticket to check the label shows up
        # here as a THIRD call and reds this case.
        with TempDir() as tmp:
            _, _, st = started(tmp, labels=[])
            c.check("A3 an ordinary start adds NO board read beyond its own baseline of 2",
                    st.get("views") == 2, f"views={st.get('views')}")
        with TempDir() as tmp:
            _, _, st = started(tmp, labels=[TRIG])
            c.check("A3b ...and a full cycle adds no READ either (it searches and writes)",
                    st.get("views") == 2, f"views={st.get('views')}")

        # ⛔ A4 · THE PROMPT AND THE TAG BOTH FIRE, BY DESIGN. The operator's prompt at the top
        # of the ticket clones by hand, so two things race to do this. The first draft had the
        # code RETURN here - wrong under the baton: the hand-made clone inherited the trigger
        # too, so returning leaves TWO tickets holding a marker that must be unique. Skip the
        # clone; still hand the baton on.
        with TempDir() as tmp:
            _, _, st = started(tmp, labels=[TRIG],
                               search=[{"key": "TEST-88", "fields": {"summary": "successor"}}])
            c.check("A4 an existing open successor means NO second clone",
                    not st.get("clones"), f"clones={st.get('clones')}")
            c.check("A4b ...but the baton is STILL handed on - one holder, never two",
                    st.get("labels", {}).get("TEST-7") == [ROLL],
                    f"TEST-7 labels={st.get('labels', {}).get('TEST-7')}")
        with TempDir() as tmp:
            _, _, st = started(tmp, labels=[TRIG], statuses={"TEST-7": "In Progress"})
            c.check("A4c a ticket ALREADY In Progress does nothing at all",
                    not st.get("clones") and not st.get("edit_args"),
                    f"clones={st.get('clones')} edit={st.get('edit_args')}")

        # ⛔ A5 · A CLONE FAILURE MUST NOT FAIL THE START. This seam sits on the path of every
        # commit in the repo (`post-commit-jira-start.sh`), so work is never blocked because a
        # successor could not be minted: it says so loudly and the lane proceeds.
        with TempDir() as tmp:
            rc, out, st = started(tmp, labels=[TRIG], clone_fail=True)
            c.check("A5 a failed clone leaves start's own exit code intact", rc == 0,
                    f"rc={rc}: " + out.strip()[-300:])
            c.check("A5b ...and says so loudly rather than silently",
                    "clone" in out.lower()
                    and st.get("statuses", {}).get("TEST-7") == "In Progress",
                    out.strip()[-300:])
            # ⭐ THE SELF-HEAL, and the case most worth having. Swapping here would retire the
            # trigger with NOBODY holding it: the cycle ends silently and forever, which is
            # the exact failure this whole part exists to prevent, reintroduced by a
            # mis-ordered fix. Leaving it put means the next `start` simply tries again.
            c.check("A5c ...and the baton STAYS PUT, so the next start retries",
                    st.get("labels", {}).get("TEST-7") == [TRIG],
                    f"TEST-7 labels={st.get('labels', {}).get('TEST-7')}")

        # ⛔ A6 · A FAILED HAND-OFF IS LOUD, and still not fatal - same reason as A5. The board
        # is left with two trigger-holders until someone notices, which is the one gap this
        # part does NOT close; it is recorded rather than hidden.
        with TempDir() as tmp:
            rc, out, st = started(tmp, labels=[TRIG], label_edit_fail=True)
            c.check("A6 a failed baton hand-off neither fails the start nor goes quiet",
                    rc == 0 and TRIG in out, f"rc={rc}: " + out.strip()[-300:])

        # ⛔ A7 · A FAILED SEARCH IS NOT AN EMPTY ONE. `acli_json` returns None when the call
        # fails and [] when it legitimately found nothing - byte-identical to a caller that
        # only checks truthiness, and cloning on that mistake mints a duplicate every time the
        # network hiccups. Refusing BOTH the clone and the swap is the self-healing direction:
        # the trigger survives and the next start retries.
        with TempDir() as tmp:
            rc, out, st = started(tmp, labels=[TRIG], search_fail=True)
            c.check("A7 a failed successor search clones nothing and keeps the baton",
                    not st.get("clones")
                    and st.get("labels", {}).get("TEST-7") == [TRIG],
                    f"clones={st.get('clones')} labels={st.get('labels', {}).get('TEST-7')}")
            c.check("A7b ...and start still succeeds, loudly", rc == 0 and TRIG in out,
                    f"rc={rc}: " + out.strip()[-300:])

    # ══ SCC-193 Part D · the SCC-175 merge-row pin, run BOTH ways ══════════════════════════
    #
    # THE SUSPECTED DEFECT, RECORDED SO IT IS NEVER RE-DIAGNOSED FROM MEMORY. At SCC-164's
    # `finish --apply` the ticket was HELD on 2 rows and NO "merge row SATISFIED/HOLDS" line was
    # printed at all — meaning `merge_row_state` returned **None** (it prints on every other
    # path). A dry run on the IDENTICAL committed file the next day printed SATISFIED and held
    # 1. Never reproduced. The one environmental difference: `--apply` ran WITHOUT
    # `env -u GITHUB_TOKEN`, which the door mandates.
    #
    # So this pins the SHAPE that was live — two merge-ish rows, the lane landed — with and
    # without `GITHUB_TOKEN` in the environment. GREEN both ways says the --apply-time hold was
    # environmental and says so forever; RED is the defect, and then it is a fix, not a mystery.
    if c.block("SCC-193 D · two merge-shaped rows, lane landed - pinned with and without a token"):
        import os as _os
        import jira_feed  # noqa: E402

        def git(repo, *a):
            return subprocess.run(["git", *a], cwd=str(repo), capture_output=True, text=True)

        def landed_lane(name: str):
            """SCC-164's exact shape: a ticked ledger row, an OPEN click row, lane merged."""
            repo = tmp / name
            repo.mkdir()
            bare = tmp / f"{name}.git"
            git(repo, "init", "-q", "-b", "main")
            git(repo, "config", "user.email", "t@t.t")
            git(repo, "config", "user.name", "t")
            (repo / "README").write_text("x\n")
            git(repo, "add", "-A"), git(repo, "commit", "-qm", "base", "--no-verify")
            git(repo, "init", "--bare", "-q", str(bare))
            git(repo, "remote", "add", "origin", str(bare))
            git(repo, "push", "-q", "--no-verify", "origin", "main")
            branch = "chore/SCC-164-gate-cluster"
            git(repo, "checkout", "-q", "-b", branch)
            d = repo / "_artifacts/_main/2026-08-16_SCC-164-gate-cluster"
            d.mkdir(parents=True)
            (d / "task.yaml").write_text(f"task_key: SCC-164\nbranch: {branch}\n")
            (d / "walkthrough.md").write_text(
                "# W\n\n## Your Actions\n\n"
                "- [x] **The merge itself** - lands via this branch's PR\n"
                "- [ ] **Click **Merge** on the PR.** That click is the sign-off.\n")
            git(repo, "add", "-A"), git(repo, "commit", "-qm", "lane", "--no-verify")
            git(repo, "checkout", "-q", "main")
            git(repo, "merge", "-q", "--no-ff", "--no-verify", branch, "-m", "merge")
            git(repo, "push", "-q", "--no-verify", "origin", "main")
            git(repo, "fetch", "-q", "origin")
            return d / "walkthrough.md"

        with TempDir() as tmp:
            path = landed_lane("d1")
            had = _os.environ.get("GITHUB_TOKEN")
            try:
                for label, token in (("without GITHUB_TOKEN", None),
                                     ("with a stale GITHUB_TOKEN in env", "ghp_deadbeefdeadbeef")):
                    if token is None:
                        _os.environ.pop("GITHUB_TOKEN", None)
                    else:
                        _os.environ["GITHUB_TOKEN"] = token
                    st = jira_feed.merge_row_state(path)
                    c.check(f"D1 {label}: the merge row RESOLVES (never a silent None)",
                            st is not None,
                            "None is the state SCC-164's --apply run showed, and it prints "
                            "nothing at all - a hold with no reason given")
                    c.check(f"D1 {label}: ...and the landed lane SATISFIES it",
                            bool(st) and st["satisfied"], str(st))
                    rows = jira_feed.open_actions(path.read_text(encoding="utf-8"))
                    held = [r for r in (rows or []) if not jira_feed.is_merge_row(r)]
                    c.check(f"D1 {label}: the click row is NOT a merge row, so exactly 1 holds",
                            len(held) == 1 and "Click" in held[0], str(rows))
            finally:
                if had is None:
                    _os.environ.pop("GITHUB_TOKEN", None)
                else:
                    _os.environ["GITHUB_TOKEN"] = had

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
