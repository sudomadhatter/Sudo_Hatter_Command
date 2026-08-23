"""jira_feed.py must never invent ticket content, and must leave exactly ONE Dev Record.

The two defects this covers are the ones that motivated SCC-49 and the ones a hand-written
step reintroduces every time:

  * a ticket that reports success while carrying nothing (acli exits 0, the comment is not
    there) - covered by the `swallow` stub mode, the load-bearing negative here;
  * two Dev Records for one story, because /cicd-quick-dev closed the branch and then
    /cicd-close-story-merge-tree closed the story and both posted.

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
    # ⛔⛔ THE JQL IS HONOURED, and until it was this stub answered EVERY query with the same
    # canned rows - so `roll_the_cycle`'s successor search was pinned by nothing at all. Measured
    # by the Test-Adequacy lens: deleting `AND key != {key}` from the production JQL left the
    # suite 18/18 GREEN, while on a live board that mutant is terminal (the ticket matches its own
    # query, skips its clone, swaps anyway, and names ITSELF as the successor that already exists).
    # A stub that ignores the question cannot fail on a wrong question.
    # Only the three clauses this repo's queries actually use are modelled, and an UNKNOWN clause
    # is left alone rather than silently ignored - a stub that quietly drops a filter it does not
    # understand is the same defect one level down.
    rows = state.get("search", [])
    jql = val("--jql") or ""
    if "labels = " in jql:
        want = jql.split('labels = "')[1].split('"')[0] if 'labels = "' in jql else None
        if want:
            rows = [r for r in rows
                    if want in state.get("labels", {}).get(r.get("key"), [])]
    if "key != " in jql:
        excl = jql.split("key != ")[1].split()[0].strip()
        rows = [r for r in rows if r.get("key") != excl]
    if 'statusCategory = "To Do"' in jql:
        rows = [r for r in rows
                if state.get("statuses", {}).get(r.get("key"), "To Do").lower()
                in ("to do", "to do next")]
    print(json.dumps(rows))
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
    # ⛔ `--yes` is RECORDED, like the transition stub already does. Without it a clone shipped
    # without `--yes` blocks forever on acli's interactive confirm - the exact trap this file
    # documents in three other places - while every case stays green.
    state["clones"] = state.get("clones", []) + [src]
    state.setdefault("clone_args", []).append({"key": src, "yes": "--yes" in args,
                                               "to_project": val("--to-project")})
    state.setdefault("labels", {})[new_key] = list(state.get("labels", {}).get(src, []))
    state.setdefault("statuses", {})[new_key] = "To Do"
    state.setdefault("summaries", {})[new_key] = state.get("summaries", {}).get(src, "")
    # ⛔ NO SUBTASKS, and the DESCRIPTION carried verbatim - the two properties `clone` was
    # actually chosen for, and neither was modelled. The comment above claimed the stub "has to
    # model it or the case proves nothing about the property it was picked for", and then did not.
    # A later switch from `clone` to `create` would have kept every case green while silently
    # dragging the closed parent's subtasks into the new cycle.
    state.setdefault("subtasks", {})[new_key] = []
    state.setdefault("descriptions", {})[new_key] = state.get("descriptions", {}).get(src, "")
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

        # ── SCC-271 A · the placeholder index-row REPLACES is not "data loss" ──
        if c.block("SCC-271 index-row: the placeholder it replaces is not data loss"):
            # ⛔ THE DEFECT. `keep` snapshotted EVERY prior line, `index_append` then
            # deliberately drops the `(empty ...)` placeholder - its documented job - and the
            # read-back falsified `now` against the pre-drop snapshot. So the command reported
            # its own correct write as data loss and exited 2, on the FIRST row of every fresh
            # rolling ticket. Measured on SCC-262, 2026-08-22.
            #
            # Why this is worth a guard rather than a shrug: the message tells the reader to
            # "restore the ticket before doing anything else" - i.e. to undo a good write - and
            # a data-loss guard that cries wolf on first use is one that gets trained out of the
            # system. The teeth are re-pinned by the control at the end of this block.
            FRESH = ("THE ROLLING TICKET - the ONE open home for discovered work.\n"
                     "\n"
                     "PREDECESSOR\n"
                     "  Cycle 4 was SCC-244, run as one consolidated lane.\n"
                     "\n"
                     "INDEX\n"
                     "  (empty - this cycle has taken no work yet)\n")
            ROW1 = "  Part A - SCC-269 - the first row this ticket ever took"

            set_state(state, description=FRESH, lossy_drop=None)
            code, out = jf("index-row", "--key", "TEST-1", "--line", ROW1, "--apply")
            st = get_state(state)
            c.check("index-row: the first row on a FRESH index exits 0",
                    code == 0, f"exit {code}: " + out.strip()[:300])
            c.check("index-row: ...and does NOT cry data loss over the placeholder",
                    "MISSING" not in out and "data loss" not in out.lower(),
                    out.strip()[:400])
            c.check("index-row: ...the row landed", "SCC-269" in st["description"],
                    st["description"][-200:])
            c.check("index-row: ...the placeholder is gone (index_append's job)",
                    "(empty" not in st["description"], st["description"][-200:])
            c.check("index-row: ...and the deliberate replacement is REPORTED, not silent",
                    "placeholder" in out.lower(), out.strip()[:400])

            # ⭐ THE TEETH, re-pinned on the SAME shape. A line that index_append promised to
            # KEEP and that came back missing is still data loss and still exits 2 - the fix
            # narrows what counts as loss, it does not remove the check.
            set_state(state, description=FRESH, lossy_drop="SCC-244")
            code, out = jf("index-row", "--key", "TEST-1", "--line", ROW1, "--apply")
            c.check("index-row: a REAL dropped line on a fresh index is still caught",
                    code == 2 and "usage: jira_feed.py" not in out,
                    f"exit {code}: " + out.strip()[:300])
            c.check("index-row: ...and it still names the line that went missing",
                    "SCC-244" in out, out.strip()[:400])

            set_state(state, description="", lossy_drop=None, comments=[])

        # ── SCC-271 B · --append-new cannot manufacture two records for one id ─
        if c.block("SCC-271 devrecord: --append-new cannot forge two records for one id"):
            # `find_devrecord` already filters by story id, so `prior` is non-None ONLY when
            # the id MATCHES. That makes "one id, two records" the flag's only reachable
            # effect - the exact state `record_story_id`'s own docstring calls "the failure
            # SCC-49 wrote `check` for", and that `cmd_check` reports as a defect.
            #
            # SEVEN command bodies plus the SOP say "never --append-new" and nothing enforced
            # it. This block is that enforcement. The legitimate two-records case (two LANES,
            # two different ids) needs no flag: prior is None and it creates anyway - pinned
            # by the second control below.
            set_state(state, description="", comments=[])
            code, out = jf("devrecord", "--story", "9.1", "--key", "TEST-7", "--apply",
                           "--stage", "quick-dev", "--followon", "none")
            c.check("devrecord: the first record posts", code == 0
                    and len(get_state(state)["comments"]) == 1, out.strip()[:200])

            code, out = jf("devrecord", "--story", "9.1", "--key", "TEST-7", "--apply",
                           "--append-new", "--followon", "none")
            c.check("--append-new over a MATCHING prior is refused (exit 2)",
                    code == 2 and "usage: jira_feed.py" not in out,
                    f"exit {code}: " + out.strip()[:300])
            c.check("...and the ticket still carries exactly ONE record",
                    len(get_state(state)["comments"]) == 1,
                    f"{len(get_state(state)['comments'])} comments")
            c.check("...and the refusal names the remedy (drop the flag / update in place)",
                    "drop the flag" in out.lower(), out.strip()[:400])

            # Control 1: no prior record -> --append-new is harmless, still creates.
            set_state(state, description="", comments=[])
            code, out = jf("devrecord", "--story", "9.1", "--key", "TEST-7", "--apply",
                           "--append-new", "--followon", "none")
            c.check("control: --append-new with NO prior record still creates",
                    code == 0 and len(get_state(state)["comments"]) == 1,
                    f"exit {code}, {len(get_state(state)['comments'])} comments")

            # Control 2: a DIFFERENT id is a second LANE, not a fork - it must still post,
            # and it must not disturb the first lane's record.
            code, out = jf("devrecord", "--story", "scc-271-other-lane", "--key", "TEST-7",
                           "--apply", "--followon", "none")
            bodies = "\n".join(x["body"] for x in get_state(state)["comments"])
            c.check("control: a SECOND LANE (different id) still gets its own record",
                    code == 0 and len(get_state(state)["comments"]) == 2
                    and "9.1" in bodies and "scc-271-other-lane" in bodies,
                    f"exit {code}, {len(get_state(state)['comments'])} comments")

            set_state(state, description="", comments=[])

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

            # ⚠ SCC-271 INVERTED this assertion, deliberately. It used to read "--append-new:
            # opts out of the one-record rule" (exit 0, two comments) and it PINNED A FOOTGUN:
            # the opt-out's only reachable effect is the two-records-one-id state `cmd_check`
            # reports as a defect, and seven command bodies already banned it in prose. The
            # flag is now refused over a matching prior. Full coverage lives in the
            # `SCC-271 devrecord` block above; this line stays here so the legacy block cannot
            # drift back to asserting the old behaviour.
            code, out = jf("devrecord", "--story", "9.1", "--key", "TEST-7", "--apply",
                           "--append-new", "--followon", "none")
            c.check("devrecord --append-new: the one-record rule can NOT be opted out of",
                    code == 2 and len(get_state(state)["comments"]) == 1,
                    f"exit {code}, {len(get_state(state)['comments'])} comments")

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

            # Positive control: a checker that never reports clean gets muted. The description
            # carries the RENDERED-BY trailer, because that is what a minted one looks like and
            # `check` reads the trailer, not the length.
            fed_desc = ("9.1 - Widget Archive. Acceptance criteria 1. AC-1 archive. "
                        "Rendered by jira_feed.py")
            set_state(state, description=fed_desc,
                      comments=[{"id": "1", "body": "Dev Record - 9.1 (close-out)\nDecisions"}])
            code, out = jf("check", "--key", "TEST-7")
            c.check("check: fed ticket -> exit 0 (positive control)",
                    code == 0 and "0 error(s)" in out and "outline present" in out,
                    out.strip()[:200])

            # ⛔ LENGTH IS NOT CONTENT. A hand-typed note clears MIN_DESCRIPTION, and `check`
            # reported "outline present (213 chars)" over it — at close-out, in both doors,
            # where the operator reads that line as the sign-off. The exit code is deliberately
            # UNCHANGED (a hand note passed before and passes now); the claim is what was wrong.
            hand = ("Blocked on the auth migration - ping me before touching this one, the "
                    "staging keys rotate on Friday and the runbook is out of date.")
            set_state(state, description=hand,
                      comments=[{"id": "1", "body": "Dev Record - 9.1 (close-out)\nDecisions"}])
            code, out = jf("check", "--key", "TEST-7")
            c.check(f"check: a {len(hand)}-char HAND NOTE is not called an outline",
                    "outline present" not in out and "NO rendered outline" in out,
                    out.strip()[:300])
            c.check("check: ...and it still exits 0 — the severity boundary did not move",
                    code == 0, f"exit={code}")

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
            # cicd-close-story-merge-tree.md the command) and read by none of them. Story-awareness
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
            # ⛔ THIS CASE'S PREMISE WAS DISPROVEN BY ITS OWN LANE. It read "`--labels` REPLACES
            # the set on the real acli. A writer that sends only `user-tasks` passes every
            # 'is user-tasks on the ticket?' assertion while silently deleting `quick-dev`,
            # `parallel-ok`". Measured 2026-08-17: `--labels` ADDS. So no `--labels` writer can
            # clobber, the shipped writer now sends exactly that single label, and this check
            # passes for BOTH idioms - it can no longer fail on the thing it was written to catch.
            # Reverting the writer to the union form was measured at 335/335 green.
            # It is kept as a state assertion (the labels really are all there afterwards) and the
            # ARGV row below is what actually distinguishes the two writers now.
            set_state(state, types={"TEST-7": "Task"}, statuses={"TEST-7": "In Progress"},
                      labels={"TEST-7": ["quick-dev", "parallel-ok"]})
            code, out = jf("finish", "--key", "TEST-7", "--walkthrough", walkthrough(OWED),
                           "--apply")
            st = get_state(state)
            c.check("finish: adding user-tasks PRESERVES every label already on the ticket",
                    set(st["labels"]["TEST-7"]) == {"quick-dev", "parallel-ok", "user-tasks"},
                    str(st.get("labels")))
            # ⭐ THE ARGV, because the end state can no longer tell the two writers apart under
            # an ADDING api. A read-modify-write regression sends the whole union and produces an
            # identical board; only what was SENT still differs.
            sent_f = " ".join(st.get("edit_args") or [])
            c.check("finish: ...and it SENDS only that label, never a recomputed union",
                    "--labels user-tasks" in sent_f and "quick-dev" not in sent_f,
                    f"a read-modify-write regression is invisible in the end state: {sent_f}")

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

        def started(tmp, *, labels, statuses=None, search=None, board=None, apply=True,
                    **extra):
            repo, acli, state = build(tmp)
            # `board` seeds OTHER tickets' labels. Needed the moment the stub started honouring
            # the JQL: a canned search row for a ticket with no labels is now correctly filtered
            # out, which is what exposed A4's fixture as a lie - it asserted "a successor exists"
            # against a row that carried no trigger at all.
            lab = {"TEST-7": labels}
            lab.update(board or {})
            set_state(state, types={"TEST-7": "Task"},
                      statuses=statuses or {"TEST-7": "To Do"},
                      labels=lab, search=search or [], **extra)
            os.environ["STUB_STATE"] = str(state)
            cmd = ["jira_feed.py", "start", "--key", "TEST-7", "--acli", str(acli)]
            rc, out = run_script(*(cmd + ["--apply"] if apply else cmd))
            return rc, out, get_state(state)

        SUCC = [{"key": "TEST-88", "fields": {"summary": "the successor"}}]

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

            # ── SCC-242 row H · a clone must announce what it did NOT do ──────────────
            # ⛔ THE COPY IS VERBATIM ON PURPOSE and nothing here asks to change it: the
            # description carries the operator's own cycle prompt, and building a
            # `--description` is how backticks execute (the ruling is at jira_feed.py
            # :1364-1370). The defect is the SILENCE. A fresh clone is word-for-word its
            # predecessor, so three things are wrong the instant it exists - the summary
            # still says the OLD cycle number, the INDEX still lists the predecessor's
            # subtasks, and PREDECESSOR still names the cycle before that - and the run
            # says only "cloned the next rolling ticket".
            #
            # ⭐ NOT HYPOTHETICAL: SCC-244 was corrected BY HAND on 2026-08-20, in this
            # session, precisely because nothing told the agent those edits were owed.
            OWED = ("summary", "INDEX", "PREDECESSOR")
            missing = [w for w in OWED if w.lower() not in out.lower()]
            c.check("A1f the clone NAMES the three edits it left owed",
                    not missing,
                    f"the run announced a clone and said nothing about {missing}. A "
                    f"verbatim copy is correct; a verbatim copy nobody is told to finish "
                    f"is a ticket that reads as the wrong cycle. Output was: "
                    + out.strip()[-300:])
            # ...and it must say which TICKET owes them, or the reader edits the wrong one.
            c.check("A1g ...and it says which ticket carries them",
                    "TEST-CLONE" in out, out.strip()[-300:])

        # ⛔ A1d · THE PREMISE THIS CASE SHIPPED WITH WAS FALSE, and it is the lane's own thesis.
        # It read "`--labels` REPLACES the whole set on the real acli", citing a pin that no longer
        # pins that. Measured 2026-08-17: `--labels` ADDS. So under the corrected stub NO `--labels`
        # writer can clobber, and "preserves the others" is now a property of acli rather than of
        # the writer - which is why this case can no longer distinguish the two implementations it
        # was written to distinguish. It is kept because it still pins the SWAP's shape (identity
        # added, trigger removed, siblings untouched), and A1e below asserts the ARGV that a
        # regression to a read-modify-write would change.
        with TempDir() as tmp:
            _, _, st = started(tmp, labels=[TRIG, "user-tasks"])
            c.check("A1d the swap PRESERVES every other label the ticket carried",
                    set(st.get("labels", {}).get("TEST-7", [])) == {ROLL, "user-tasks"},
                    f"TEST-7 labels={st.get('labels', {}).get('TEST-7')}")
            # ⭐ A1e · THE ARGV, because the end state can no longer tell the idioms apart. A
            # read-modify-write regression ("send the surviving set") produces the SAME labels
            # under an adding API and only differs in what it SENT - so the sent command is the
            # only place the difference is still visible.
            sent = " ".join(st.get("edit_args") or [])
            c.check("A1e ...and it SENDS the two markers, never a recomputed set",
                    f"--labels {ROLL}" in sent and f"--remove-labels {TRIG}" in sent
                    and "user-tasks" not in sent,
                    f"a read-modify-write regression is invisible in the end state: {sent}")

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
            _, _, st = started(tmp, labels=[TRIG], search=SUCC,
                               board={"TEST-88": [TRIG]},
                               statuses={"TEST-7": "To Do", "TEST-88": "To Do"})
            c.check("A4 an existing open successor means NO second clone",
                    not st.get("clones"), f"clones={st.get('clones')}")
            c.check("A4b ...but the baton is STILL handed on - one holder, never two",
                    st.get("labels", {}).get("TEST-7") == [ROLL],
                    f"TEST-7 labels={st.get('labels', {}).get('TEST-7')}")

        # ⛔⛔ A4c/A4d · THE SUCCESSOR IS AN **UN-STARTED** TICKET, AND THAT IS THE WHOLE QUERY.
        # A ticket left holding the trigger by a failed swap is a STRANDED PREDECESSOR, not a
        # successor - it is In Progress. The first version of the query asked only
        # `statusCategory != Done`, so starting the real successor found its own predecessor,
        # skipped its clone and consumed its own baton: the two-holder state "repairing" itself
        # into ZERO holders, last line printed "exactly one open ticket holds the baton".
        # Reproduced by a review lens, not theorised.
        with TempDir() as tmp:
            _, _, st = started(tmp, labels=[TRIG], search=SUCC,
                               board={"TEST-88": [TRIG]},
                               statuses={"TEST-7": "To Do", "TEST-88": "In Progress"})
            c.check("A4c a STRANDED PREDECESSOR is not a successor - clone anyway",
                    st.get("clones") == ["TEST-7"],
                    f"an In Progress trigger-holder must not satisfy the successor check; "
                    f"clones={st.get('clones')}")

        # ⭐ A4d · THE RETRY THE MESSAGES PROMISE, AND IT DID NOT EXIST. Every failure path printed
        # "the label was LEFT IN PLACE, so the next `start` tries again"; the roll was bound to the
        # TRANSITION EDGE, so once the ticket was In Progress every later `start` returned above
        # the trigger check and no retry was reachable. Three lenses found it independently. The
        # roll now keys on STATE, which is safe because a ticket that handed off no longer carries
        # the trigger (A4e is that control).
        with TempDir() as tmp:
            rc, out, st = started(tmp, labels=[TRIG], statuses={"TEST-7": "In Progress"})
            c.check("A4d an In Progress ticket STILL holding the baton rolls - the real retry",
                    st.get("clones") == ["TEST-7"] and rc == 0,
                    f"rc={rc} clones={st.get('clones')}")
            c.check("A4d ...and says it is the retry, rather than going quiet",
                    "retry" in out.lower(), out.strip()[-200:])
        with TempDir() as tmp:
            _, _, st = started(tmp, labels=[ROLL], statuses={"TEST-7": "In Progress"})
            c.check("A4e CONTROL: an In Progress ticket with a SPENT baton does nothing at all",
                    not st.get("clones") and not st.get("edit_args"),
                    f"clones={st.get('clones')} edit={st.get('edit_args')}")

        # ⛔ A4f · PLACEMENT, and it was pinned by NOTHING. Moving the roll above the `--apply`
        # guard left the suite 18/18 green - a mutant under which a DRY RUN clones a real ticket
        # and swaps a real label. The code comment asserted the placement was load-bearing; only
        # this case makes that true.
        with TempDir() as tmp:
            rc, out, st = started(tmp, labels=[TRIG], apply=False)
            c.check("A4f a DRY RUN never rolls the cycle - no clone, no label touched",
                    not st.get("clones") and st.get("labels", {}).get("TEST-7") == [TRIG],
                    f"clones={st.get('clones')} labels={st.get('labels', {}).get('TEST-7')}")
        with TempDir() as tmp:
            rc, out, st = started(tmp, labels=[TRIG], no_status=["In Progress"])
            c.check("A4g a transition that never LANDED does not roll the cycle",
                    rc == 2 and not st.get("clones"),
                    f"rc={rc} clones={st.get('clones')}")

        # ⛔ A5 · A CLONE FAILURE MUST NOT FAIL THE START. This seam sits on the path of every
        # commit in the repo (`post-commit-jira-start.sh`), so work is never blocked because a
        # successor could not be minted: it says so loudly and the lane proceeds.
        with TempDir() as tmp:
            rc, out, st = started(tmp, labels=[TRIG], clone_fail=True)
            c.check("A5 a failed clone leaves start's own exit code intact", rc == 0,
                    f"rc={rc}: " + out.strip()[-300:])
            # ⛔ `"clone" in out.lower()` also matched "cloned" on the SUCCESS path, so this said
            # nothing about the failure branch. A5c is what actually killed that mutant; this row
            # now names the WARN so both halves stand on their own.
            c.check("A5b ...and says so loudly rather than silently",
                    "[WARN]" in out and "clone FAILED" in out
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
            # ⛔ `TRIG in out` ALSO MATCHED THE SUCCESS LINE, so deleting the swap-failure branch
            # outright left this green while the run printed "exactly one open ticket holds the
            # baton" with two tickets holding it. Measured by a lens. The assertion now names the
            # WARN and the specific wording, so only the branch it is about can satisfy it.
            c.check("A6 a failed baton hand-off neither fails the start nor goes quiet",
                    rc == 0 and "[WARN]" in out and "could NOT be handed on" in out,
                    f"rc={rc}: " + out.strip()[-300:])
            c.check("A6b ...and it does NOT claim exactly one holder while two hold it",
                    "exactly one open ticket holds the baton" not in out,
                    "a false all-clear is worse than silence: " + out.strip()[-200:])

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

    # ── SCC-242 · the closer cannot answer for a STORY lane ──────────────────────────────
    #
    # ⛔ THE DEFECT, AND WHY THE OBVIOUS FIX IS A NO-OP.
    #
    # `merge_row_state` compares the lane tip against a LITERAL `origin/main` (:1789-1790).
    # A Task lands on main, so that is right for Tasks. A STORY lands on `epic/<KEY>-<slug>`
    # and is not an ancestor of main until the epic itself ships - so `finish` would answer
    # "held" forever while the story status file already read `done`. That is why
    # `cicd-close-story-merge-tree.md:320-324` BANS `finish` and transitions with raw `acli`,
    # and why that lane gets none of the `## Your Actions` refusal this reader exists to give.
    #
    # ⭐ But teaching it a landing ref ALONE changes nothing, and case A2 is why: `MERGE_DOORS`
    # (:1666) does not contain `/cicd-close-story-merge-tree`, so a story walkthrough's merge
    # row is not recognised as a merge row at all and `merge_row_state` returns None before the
    # comparison is ever reached. Both halves, or neither half does anything.
    if c.block("SCC-242 · the closer answers for a STORY lane, and knows the story door"):
        import jira_feed  # noqa: E402

        def git(repo, *a):
            return subprocess.run(["git", *a], cwd=str(repo), capture_output=True, text=True)

        # ⛔ THIS ROW MUST NOT CARRY THE CANONICAL PHRASE, and the first cut of this block
        # did. `is_merge_row` is `any(door in low) OR MERGE_PHRASE in low`, so a row opening
        # `**The merge itself**` matches on the PHRASE and case A2 passed green while
        # `MERGE_DOORS` was still missing the story door - a vacuous green that would have
        # let the no-op ship. The row names the DOOR and nothing else, so A2 isolates exactly
        # the one term under test, and A1/A3/A5 genuinely depend on it.
        STORY_ROW = "**Land the story on its epic** - run `/cicd-close-story-merge-tree`"
        EPIC = "epic/SCC-33-toolkit"

        def story_lane(name: str, *, land_on_epic: bool = True):
            """A story lane merged onto its EPIC branch - never onto main.

            main exists and is pushed, so `origin/main` resolves; the point is that the tip
            is NOT an ancestor of it. Only the epic ref can answer for this shape.
            """
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

            git(repo, "checkout", "-q", "-b", EPIC)
            git(repo, "push", "-q", "--no-verify", "origin", EPIC)

            branch = "claude/SCC-77-widget-archive"
            git(repo, "checkout", "-q", "-b", branch)
            d = repo / "_artifacts/_main/2026-08-20_story"
            d.mkdir(parents=True)
            (d / "task.yaml").write_text(f"task_key: SCC-77\nbranch: {branch}\n")
            (d / "walkthrough.md").write_text(
                f"# W\n\n## Your Actions\n\n- [ ] {STORY_ROW}\n")
            git(repo, "add", "-A"), git(repo, "commit", "-qm", "story work", "--no-verify")

            if land_on_epic:
                git(repo, "checkout", "-q", EPIC)
                git(repo, "merge", "-q", "--no-ff", "--no-verify", branch, "-m", "land")
                git(repo, "push", "-q", "--no-verify", "origin", EPIC)
                git(repo, "checkout", "-q", branch)
            git(repo, "fetch", "-q", "origin")
            return d / "walkthrough.md"

        def state(wt, **kw):
            """Call the reader, turning 'the parameter does not exist' into a real failure.

            ⛔ A bare TypeError would die in SETUP and look identical to a failed assertion
            (`tests-must-gate-for-real`). Catching it here makes the red say WHY.
            """
            try:
                return jira_feed.merge_row_state(wt, **kw), None
            except TypeError as e:
                return None, f"merge_row_state does not accept that yet: {e}"

        with TempDir() as tmp:
            # A2 (row D) · the recogniser must know the story door. Checked FIRST because
            # every case below it is unreachable while this is False.
            c.check("A2 · a row naming /cicd-close-story-merge-tree IS a merge row",
                    jira_feed.is_merge_row(STORY_ROW),
                    "MERGE_DOORS omits the story door, so merge_row_state returns None "
                    "before any comparison - the landing-ref fix alone is a no-op")

            # A1 (row A) · the whole point: a tip that is an ancestor of the EPIC, not of main.
            wt = story_lane("s1")
            st, err = state(wt, landing_ref=f"origin/{EPIC}")
            c.check("A1 · a lane landed on its EPIC branch reads as MERGED",
                    err is None and st is not None and st["satisfied"],
                    err or str(st))

            # A3 (row E) · the message must name the ref it actually compared against.
            c.check("A3 · ...and the reason NAMES that ref, not a hardcoded origin/main",
                    err is None and st is not None and EPIC in st["why"],
                    err or f"why must carry the resolved ref: {st}")

            # A4 (row B) · CONTROL. No ref, no manifest key -> today's behaviour, exactly.
            # This is the assertion that says the lane cannot silently change how every
            # existing Task lane closes.
            st4, err4 = state(story_lane("s2"))
            c.check("A4 · (control) with NO landing ref the default is still origin/main",
                    err4 is None and st4 is not None and not st4["satisfied"]
                    and "origin/main" in st4["why"],
                    err4 or str(st4))

            # A6 · ⭐ THE FIXTURE'S OWN CONTROL - GREEN TODAY, and it must stay green.
            # Everything above is red, so nothing above proves the harness is sound rather
            # than simply broken. This runs the UNCHANGED path - a Task row on a lane merged
            # to main, no landing ref - through the same helpers. Red here means the fixture
            # is wrong; red above with this green means the DEFECT is real.
            task_wt = story_lane("s4", land_on_epic=False)
            (task_wt).write_text(
                "# W\n\n## Your Actions\n\n"
                "- [ ] **The merge itself** - lands via this branch's PR\n", encoding="utf-8")
            git(task_wt.parents[3], "add", "-A")
            git(task_wt.parents[3], "commit", "-qm", "task row", "--no-verify")
            st6, err6 = state(task_wt)
            c.check("A6 · (control, green today) a Task-shaped row still resolves unchanged",
                    err6 is None and st6 is not None and not st6["satisfied"]
                    and "origin/main" in st6["why"],
                    err6 or f"the UNCHANGED path must be unaffected by this lane: {st6}")

            # A5 (row C) · fail CLOSED. An unresolvable ref is not evidence of a merge.
            st5, err5 = state(story_lane("s3"), landing_ref="origin/epic/SCC-00-does-not-exist")
            c.check("A5 · an UNRESOLVABLE landing ref HOLDS, and says which ref it tried",
                    err5 is None and st5 is not None and not st5["satisfied"]
                    and "SCC-00-does-not-exist" in st5["why"],
                    err5 or f"a ref git cannot resolve must never pass: {st5}")

            # ── row F · THE FLAG THE STORY DOOR WILL ACTUALLY CALL ────────────────────
            # A1-A5 exercise `merge_row_state` directly. That is not what
            # `cicd-close-story-merge-tree.md` runs - it runs the CLI, and a parameter that
            # exists on the function but is unreachable from `finish` leaves the door with
            # nothing to call and the ban block correct as written. A7/A8 run the real verb.
            #
            # DRY RUN on purpose: the merge check happens before the board write, so the exit
            # code alone answers the question (0 = the section is clear, 3 = HELD) and no
            # transition has to be stubbed to read it.
            cli_repo, cli_acli, cli_state = build(tmp / "cli")
            set_state(cli_state, types={"SCC-77": "Story"},
                      statuses={"SCC-77": "In Progress"})
            os.environ["STUB_STATE"] = str(cli_state)
            story_wt = story_lane("s5")

            def finish_on(wt, *extra):
                return run_script("jira_feed.py", "finish", "--key", "SCC-77",
                                  "--project", str(cli_repo), "--acli", str(cli_acli),
                                  "--walkthrough", str(wt), *extra)

            rc7, out7 = finish_on(story_wt, "--landing-ref", f"origin/{EPIC}")
            c.check("A7 (row F) · `finish --landing-ref` answers for the story lane",
                    rc7 == 0 and "SATISFIED" in out7 and EPIC in out7,
                    f"exit={rc7} (2 = argparse rejected the flag; 3 = it never reached the "
                    f"comparison): " + out7.strip()[-400:])

            # A8 · CONTROL, GREEN TODAY. The same walkthrough with NO flag must still HOLD.
            # Without this, A7 could be made green by making `finish` stop checking at all.
            rc8, out8 = finish_on(story_wt)
            c.check("A8 · (control, green today) with NO flag that same lane still HOLDS",
                    rc8 == 3 and "origin/main" in out8,
                    f"exit={rc8}: " + out8.strip()[-400:])


    # ── SCC-206 · the continuation window has to CLOSE ───────────────────────────────────
    # ⛔ THE DEFECT, IN ONE LINE: `_collect` folds an indented line into `items[-1]` without
    # ever asking whether the item above it is still open. A `- [x]` is skipped (it matches
    # `_ANY_ITEM_RE`, so it appends nothing) - but its own WRAPPED LINES do not match, so they
    # land on the last OPEN item. The operator is then shown work they already did, glued onto
    # a row that says something else, and `finish` posts that to the board as owed.
    if c.block("SCC-206 · a ticked item ENDS the continuation window"):
        import jira_feed  # noqa: E402

        def sect(*rows: str) -> str:
            return "# W\n\n## Your Actions\n\n" + "\n".join(rows) + "\n"

        # I · the reproduction. A wrapped `- [x]` under a `- [ ]`.
        BLED = sect(
            "- [ ] **Install the board column** - the `user-tasks` filter needs it",
            "- [x] **Run the memory audit** - the index passed 90% of the 25 KB cap",
            "      and was compacted on 2026-08-19, so this one is genuinely done",
        )
        got = jira_feed.open_actions(BLED)
        c.check("I a ticked item's wrapped prose does NOT land on the open item above it",
                got == ["**Install the board column** - the `user-tasks` filter needs it"],
                f"the open row was contaminated by the DONE row's second line: {got}")

        # J · an HTML comment is invisible. Authors leave them in walkthroughs constantly;
        # indented under an item, every one of them is currently owed work.
        COMMENTED = sect(
            "- [ ] **Decide the landing order**",
            "  <!-- agent note: SCC-240 lands first per the operator, 2026-08-20 -->",
        )
        got_j = jira_feed.open_actions(COMMENTED)
        c.check("J an indented HTML comment folds into NO item",
                got_j == ["**Decide the landing order**"],
                f"a comment is not the operator's instruction: {got_j}")

        # J2 · ...including a comment that spans lines, which is how the long ones are written.
        MULTI = sect(
            "- [ ] **Decide the landing order**",
            "  <!-- agent note:",
            "       SCC-240 lands first per the operator -->",
        )
        got_j2 = jira_feed.open_actions(MULTI)
        c.check("J2 ...and a MULTI-LINE comment folds in no part of itself",
                got_j2 == ["**Decide the landing order**"], str(got_j2))

        # ⛔ J3 · AN UNTERMINATED COMMENT MUST NOT EAT THE SECTION. Found by this lane's own
        # review: `<!-- note` with no `-->` swallowed every item below it, so a typo in a
        # walkthrough silently dropped owed operator work and `finish` closed the ticket over
        # it - SCC-206's own fail-open shape, reintroduced by SCC-206's fix.
        c.check("J3 an UNTERMINATED comment does not swallow the items below it",
                jira_feed.open_actions(sect(
                    "- [ ] **A**", "  <!-- a note nobody closed", "- [ ] **B**"))
                == ["**A**", "**B**"],
                "over-reporting holds a ticket; under-reporting closes one that should hold")

        # ⛔ K · THE CONTROL THAT FORBIDS THE LAZY FIX. Deleting the fold entirely makes I, J
        # and J2 green in one edit - and truncates every genuine multi-line instruction to its
        # first line, which is the half that never says WHY. `smh-quick-dev.md` publishes
        # ride-along as a MACHINE CONTRACT. This row is green today and must stay green.
        RIDES = sect(
            "- [ ] **Install the board column**",
            "      because the `user-tasks` filter has nowhere to render without it",
        )
        got_k = jira_feed.open_actions(RIDES)
        c.check("K (control, green today) a real continuation still rides along",
                got_k == ["**Install the board column** because the `user-tasks` filter "
                          "has nowhere to render without it"], str(got_k))

        # K2 · and the window REOPENS on the next open item - a ticked row must end the
        # window, not disable folding for the rest of the section.
        REOPEN = sect(
            "- [ ] **First**",
            "- [x] **Done** - with a wrapped line",
            "      that must vanish",
            "- [ ] **Second**",
            "      and its own continuation, which must survive",
        )
        got_k2 = jira_feed.open_actions(REOPEN)
        c.check("K2 the window REOPENS on the next open item",
                got_k2 == ["**First**",
                           "**Second** and its own continuation, which must survive"],
                str(got_k2))

        # ⛔ L · THE REFUSAL PATH MUST NOT SHIFT. `None` (no section) and `[]` (a section with
        # nothing open) mean different things upstream - one refuses, one closes the ticket.
        c.check("L (control) no section at all is still None, never []",
                jira_feed.open_actions("# W\n\nnothing here\n") is None,
                "an absent section is a REFUSAL, and collapsing it into 'nothing owed' "
                "closes a ticket over work the operator was promised")
        c.check("L (control) a section with only TICKED items is still []",
                jira_feed.open_actions(sect("- [x] **Done**", "      wrapped")) == [],
                "nothing open means nothing owed - and the wrapped line has no item to "
                "attach to, so it must not resurrect one")


    # ── SCC-242 row G · an INDEX that is actually an index ───────────────────────────────
    # ⛔ MEASURED ON THE LIVE TICKET, 2026-08-20. SCC-201's description reads:
    #
    #     INDEX
    #       (empty - this ticket is fresh)
    #     SCC-242 - jira_feed finish cannot close a story lane...
    #     SCC-243 - /cicd-non-crit-pr-push Step 0.5 calls lane_qualify...
    #
    # The placeholder outlived its own falsification, and the rows sit OUTSIDE the section at
    # a different indent. They land in the right place only because INDEX happens to be last;
    # add one section after it and every row files under the wrong heading. The read-back
    # guard (SCC-170) was watching for data LOSS and saw none - every row is there. What it
    # cannot see is a row in the wrong place, which is the same ticket unreadable.
    if c.block("SCC-242 row G · index-row files INTO the INDEX section"):
        import jira_feed  # noqa: E402

        BASE = ("THE ROLLING TICKET\n"
                "\n"
                "PREDECESSOR\n"
                "  Cycle 2 was SCC-197.\n"
                "\n"
                "INDEX\n"
                "  (empty - this ticket is fresh)\n")

        def append(before, row):
            try:
                return jira_feed.index_append(before, row), None
            except AttributeError as e:
                return None, f"index_append does not exist yet: {e}"

        # G1 · the first row REPLACES the placeholder. A section that says "empty" while
        # listing rows is a ticket nobody can read at a glance.
        g1, e1 = append(BASE, "SCC-206 - open_actions folds a ticked item's prose upward.")
        c.check("G1 the first append REPLACES the `(empty ...)` placeholder",
                e1 is None and g1 is not None and "(empty" not in g1,
                e1 or f"the placeholder outlived its own falsification:\n{g1}")
        c.check("G1 ...and the row is INDENTED to the section, like the placeholder was",
                e1 is None and g1 is not None
                and any(ln.startswith("  SCC-206") for ln in g1.splitlines()),
                e1 or f"a flush-left row is not in the section:\n{g1}")

        # G2 · the second append keeps the first. This is the read-back guard's own promise,
        # asserted on the composer rather than on the board.
        g2, e2 = append(g1 or BASE, "SCC-242 - the closer cannot answer for a story lane.")
        c.check("G2 a second append keeps BOTH rows, in order",
                e2 is None and g2 is not None
                and [ln.strip()[:7] for ln in g2.splitlines() if ln.strip().startswith("SCC-2")]
                == ["SCC-206", "SCC-242"],
                e2 or str(g2))

        # ⛔ G3 · THE ROW THAT PROVES THE SECTION IS FOUND RATHER THAN GUESSED. Today's code
        # appends at the very END of the description, which lands inside INDEX only because
        # INDEX is last. Put a section after it and the same code files the row under the
        # wrong heading - silently, and the read-back still sees no loss.
        TRAILING = BASE + "\nNOTES\n  keep this last\n"
        g3, e3 = append(TRAILING, "SCC-238 - the walkthrough roster drifts.")
        idx = g3.splitlines().index("INDEX") if e3 is None else -1
        nts = g3.splitlines().index("NOTES") if e3 is None else -1
        rows_at = ([n for n, ln in enumerate(g3.splitlines())
                    if ln.strip().startswith("SCC-238")] if e3 is None else [])
        c.check("G3 the row lands INSIDE the INDEX section, not at the end of the field",
                e3 is None and rows_at and idx < rows_at[0] < nts,
                e3 or f"INDEX@{idx} NOTES@{nts} row@{rows_at} - the section is being "
                      f"guessed from position:\n{g3}")

        # G4 · CONTROL. Everything outside the section is untouched, byte for byte.
        c.check("G4 (control) no other line of the description is disturbed",
                e3 is None and all(ln in g3.splitlines()
                                   for ln in TRAILING.splitlines() if "(empty" not in ln),
                e3 or "this command REPLACES the whole field - every other line must survive")

        # G5 · CONTROL. No INDEX section at all -> today's behaviour, unchanged. A ticket that
        # is not a rolling ticket must not be reshaped by a command that only files rows.
        NOIDX = "THE TICKET\n\nSCOPE\n  do the thing\n"
        g5, e5 = append(NOIDX, "SCC-999 - something.")
        c.check("G5 (control) a description with no INDEX section still appends at the end",
                e5 is None and g5 is not None and g5.rstrip().endswith("SCC-999 - something."),
                e5 or str(g5))

    # ── SCC-257 · a section ends at its own LEVEL, not at the next line starting with # ──
    # ⛔ MEASURED ON AVCH EPIC 19, 2026-08-21. Its stories group ACs under themes:
    #
    #     ## Acceptance Criteria
    #     ### Theme A - grounding
    #     - **AC-1 (cite):** ...
    #
    # `_NEXT_HEAD_RE` is `^#{1,4}\s+\S`, so `section_body` cut the section at `### Theme A`
    # - the FIRST line inside it. `acceptance_criteria` then read an empty body and the
    # outline rendered "(none found in the story file)" over a story with nine ACs. That
    # warning is indistinguishable from a story that genuinely has none.
    if c.block("SCC-257 · ac-theme-subheadings: a section ends at its own heading level"):
        import jira_feed  # noqa: E402

        THEMED = """# Story 19.1: Grounding

## Story

As **a pilot**, I want **cited answers**, so that **I can verify them.**

## Acceptance Criteria

### Theme A - grounding

- **AC-1 (cite):** every claim carries a source.
- **AC-2 (refuse):** an uncited claim is refused.

### Theme B - safety

- **AC-3 (override):** the safety override always wins.

## Tasks

- this is not an acceptance criterion
"""
        acs = jira_feed.acceptance_criteria(THEMED)
        c.check("D1 renders ACs from under a `###` sub-heading",
                any("AC-1" in a for a in acs) and any("AC-2" in a for a in acs), str(acs))
        c.check("D1 crosses a SECOND sub-heading to reach AC-3",
                any("AC-3" in a for a in acs), str(acs))
        c.check("D1 still STOPS at the next `##` - Tasks is not an AC",
                not any("not an acceptance criterion" in a for a in acs), str(acs))

        # D2 · REGRESSION. The flat shape is what the 139 story files on disk use. It must
        # not move a byte.
        FLAT = """# Story 9.1: Widget Archive

## Story

As **an admin**, I want **archived widgets to stay readable**, so that **nothing is deleted.**

## Acceptance Criteria

1. archiving a widget sets `archived_at` and keeps the document.
2. the list view hides archived widgets by default.

## Tasks

- not an AC
"""
        flat = jira_feed.acceptance_criteria(FLAT)
        c.check("D2 (regression) the flat AC list is unchanged, exactly",
                flat == ["archiving a widget sets `archived_at` and keeps the document.",
                         "the list view hides archived widgets by default."], str(flat))

        # ⛔ D3 · THE CALLER THAT MUST **NOT** CHANGE (audit finding 3). `story_statement`
        # shares `section_body`. Making the cut depth-aware for EVERYONE silently grows every
        # `## Story` block that has `###` children - and that function exists precisely to stop
        # the ticket reproducing the story file ("a description that reproduces the whole file
        # is the same failure as one with no description"). So the depth rule is opt-in per
        # caller, and this case is what fails if someone flips it globally.
        # A FLAT story cannot detect this; the `### Context` child is the whole point.
        SUBBED = """# Story 19.2: Overrides

## Story

As **a controller**, I want **overrides logged**, so that **they can be audited.**

### Context

Six paragraphs of background that belong in the story file and nowhere near the ticket.
The override subsystem dates to 2024 and has three historical shapes still in the data.

## Acceptance Criteria

- **AC-1 (log):** every override writes an audit row.
"""
        # ⛔ D4 · THE OTHER KIND OF CHILD. `include_subheadings=True` swallows EVERY `###`
        # child, and the sub-heading text was then dropped because it is not a bullet — so
        # `### Out of scope` contributed its bullets to the AC list with the one word that
        # said otherwise deleted on the way. "the mobile app" is not a criterion the story
        # is measured against. Latent when it was found (0 of 123 AGY story files carry such
        # a child today) and cheap to leave broken until the first one does.
        SCOPED = """# Story 21.4: Archive

## Story

As **an admin**, I want **archive**, so that **nothing is lost.**

## Acceptance Criteria

- **AC-1 (archive):** archiving keeps the document.

### Out of scope

- the mobile app
- the bulk importer

## Tasks

- not an AC
"""
        scoped = jira_feed.acceptance_criteria(SCOPED)
        c.check("D4 the real AC still renders", any("AC-1" in a for a in scoped), str(scoped))
        c.check("D4 the out-of-scope bullets are still CARRIED (dropping them is the other bug)",
                any("mobile app" in a for a in scoped), str(scoped))
        c.check("D4 ...but the boundary is VISIBLE — the sub-heading renders as a label",
                "[Out of scope]" in scoped, str(scoped))
        # ⛔ `.index()` on a missing label RAISES, and a crashed run prints no `FAILED:` line —
        # which is the one thing the mutation sweep scores. A guard that can only explode is a
        # guard the sweep records as SURVIVED. Positions first, assertions second.
        def at(pred) -> int:
            hits = [i for i, a in enumerate(scoped) if pred(a)]
            return hits[0] if hits else -1

        label_i, ac_i, oos_i = (at(lambda a: a == "[Out of scope]"),
                                at(lambda a: "AC-1" in a),
                                at(lambda a: "mobile app" in a))
        c.check("D4 the label sits ABOVE the bullets it introduces, not below",
                0 <= label_i < oos_i, f"label={label_i} out-of-scope bullet={oos_i} {scoped}")
        c.check("D4 the AC above it is NOT under the label",
                0 <= ac_i < label_i, f"AC-1={ac_i} label={label_i} {scoped}")
        c.check("D4 Tasks is still out of the section entirely",
                not any("not an AC" in a for a in scoped), str(scoped))

        themed = jira_feed.acceptance_criteria(THEMED)
        c.check("D4 the theme case gets its labels too, and keeps every AC",
                themed.count("[Theme A - grounding]") == 1
                and themed.count("[Theme B - safety]") == 1
                and sum(1 for a in themed if a.startswith("AC-")) == 3, str(themed))

        EMPTY_CHILD = """# Story 21.5: X

## Acceptance Criteria

- **AC-1:** one.

### Out of scope

## Tasks
"""
        c.check("D4 a sub-heading with NO bullets under it leaves no orphan label",
                "[Out of scope]" not in jira_feed.acceptance_criteria(EMPTY_CHILD),
                str(jira_feed.acceptance_criteria(EMPTY_CHILD)))

        stmt = jira_feed.story_statement(SUBBED)
        c.check("D3 the story statement still carries the As-a/I-want/So-that",
                "controller" in stmt and "audited" in stmt, stmt)
        c.check("D3 the story statement does NOT swallow its `###` child",
                "Six paragraphs" not in stmt and "2024" not in stmt, stmt)
        c.check("D3 ...and its own ACs still render (the section under test is unaffected)",
                any("AC-1" in a for a in jira_feed.acceptance_criteria(SUBBED)),
                str(jira_feed.acceptance_criteria(SUBBED)))

    # ── SCC-258 · mint must not call a hand note "its outline" ───────────────────────────
    # ⛔ MEASURED 2026-08-21. `mint` reuses an existing ticket and backfills the outline only
    # when `len(description) < MIN_DESCRIPTION` (40). A ticket somebody typed two sentences
    # into is longer than that, so the outline is never written - and mint then prints
    # "<key> carries its outline (213 chars)". It carries 213 characters of somebody's note.
    # The length test cannot tell CONTENT from LENGTH, and this whole file exists to stop a
    # command reporting success over a ticket that holds nothing it claims to hold.
    if c.block("SCC-258 · mint-reuse-stale-description + flag parity across subcommands"):
        with TempDir() as tmp:
            repo, acli, state = build(tmp)

            def jf(*args: str) -> tuple[int, str]:
                os.environ["STUB_STATE"] = str(state)
                return run_script("jira_feed.py", args[0], "--project", str(repo),
                                  "--acli", str(acli), *args[1:])

            HAND_NOTE = ("Spoke to the operator on the 14th - this one is blocked on the "
                         "auth migration and should not be picked up before it lands. "
                         "Ping me before starting.")
            EXISTING = [{"key": "TEST-42", "fields": {"summary": "9.1 - Widget Archive"}}]

            # E1a · CONTROL, and it must keep passing: a genuinely BARE ticket is backfilled.
            # Without this the fix could "work" by never writing anything at all.
            set_state(state, search=EXISTING, description="")
            code, out = jf("mint", "--story", "9.1", "--jira-project", "TEST", "--apply")
            st = get_state(state)
            c.check("E1a (control) a BARE reused ticket still gets the outline",
                    code == 0 and "AC-1 (archive)" in st["description"], out.strip()[:200])

            set_state(state, search=EXISTING, description=HAND_NOTE)
            code, out = jf("mint", "--story", "9.1", "--jira-project", "TEST", "--apply")
            st = get_state(state)
            c.check("E1 reuses the existing ticket", "reusing existing ticket TEST-42" in out,
                    out.strip()[:200])
            c.check("E1 REPLACES the hand note with the real outline",
                    "AC-1 (archive)" in st["description"], st["description"][:300])
            c.check("E1 the description carries the render trailer",
                    "Rendered by jira_feed.py" in st["description"], st["description"][:300])
            c.check("E1 the hand note is KEPT, under PREVIOUS NOTE",
                    "PREVIOUS NOTE" in st["description"]
                    and "blocked on the auth migration" in st["description"],
                    st["description"][-400:])
            c.check("E1 SAYS it kept the note, rather than reporting a plain backfill",
                    "kept under PREVIOUS NOTE" in out and "bare ticket" not in out,
                    out.strip()[:300])

            # ⛔ E1c · THE LIE ITSELF. A description that is long enough but is NOT the outline
            # must never be reported as one. `lossy_drop` strips the trailer from the write, so
            # the field lands long, plausible, and wrong - the exact shape a length test blesses.
            set_state(state, search=EXISTING, description="",
                      lossy_drop="Rendered by jira_feed.py")
            code, out = jf("mint", "--story", "9.1", "--jira-project", "TEST", "--apply")
            c.check("E1c a long-but-not-the-outline description is exit 2, not a success line",
                    code == 2 and "carries its outline" not in out, f"exit={code}: {out.strip()[:300]}")

            # ⛔ E1d · THE RETRY THAT NESTS. `lossy_drop` strips the trailer on the way in, so
            # the field lands WITHOUT it and the read-back guard exits 2 — which is exactly the
            # state an operator re-runs from. On that re-run `current` already held the outline
            # AND its PREVIOUS NOTE, and the reuse branch wrapped the lot in a fresh one.
            # Measured before the fix: 502 → 986 → 1498 → 2038 chars, one block becoming four,
            # the operator's actual note a level deeper every time.
            set_state(state, search=EXISTING, description=HAND_NOTE,
                      lossy_drop="Rendered by jira_feed.py")
            sizes, blocks = [], []
            for _ in range(4):
                jf("mint", "--story", "9.1", "--jira-project", "TEST", "--apply")
                landed = get_state(state)["description"]
                sizes.append(len(landed))
                blocks.append(landed.count("PREVIOUS NOTE"))
                set_state(state, search=EXISTING, description=landed,
                          lossy_drop="Rendered by jira_feed.py")
            c.check("E1d four retries leave exactly ONE PREVIOUS NOTE block, every time",
                    blocks == [1, 1, 1, 1], f"blocks per run: {blocks}")
            c.check("E1d ...and the description stops growing",
                    len(set(sizes)) == 1, f"chars per run: {sizes}")
            c.check("E1d ...and the operator's note is still the thing being preserved",
                    "blocked on the auth migration" in get_state(state)["description"],
                    get_state(state)["description"][-300:])

            # E1e · the unit underneath, including a ticket this bug has ALREADY nested.
            import jira_feed as _jf  # noqa: E402
            hdr = _jf.PREVIOUS_NOTE_HEADER
            c.check("E1e a plain field is the note",
                    _jf.preserved_note("just a note") == "just a note")
            c.check("E1e one existing block yields its contents, de-indented",
                    _jf.preserved_note(f"outline\n\n{hdr}\n  the note\n") == "the note")
            c.check("E1e a ticket already nested FOUR deep converges on the original note",
                    _jf.preserved_note(f"o1\n\n{hdr}\n  o2\n\n  {hdr}\n    o3\n\n"
                                       f"    {hdr}\n      original") == "original",
                    "rfind, not find - the deepest block is the human's")

            # E1f · TWO MACHINES. `write_temp` pins newline="\n" on purpose; the reuse branch
            # rewrote the same file with Path.write_text, which defaults to newline=None and
            # translates to os.linesep. ⛔ This check CANNOT go red on POSIX, where os.linesep
            # is already "\n" — it is a guard for the PC half of this system, and it is here
            # because that is the half nobody runs the suite on first.
            body = "line one\nline two\n"
            wt = Path(_jf.write_temp(body))
            rw = wt.parent / (wt.name + ".rw")
            rw.write_text(body, encoding="utf-8", newline="\n")
            c.check("E1f the reuse rewrite pins LF the same way write_temp does",
                    wt.read_bytes() == rw.read_bytes() == body.encode(),
                    f"write_temp={wt.read_bytes()!r} rewrite={rw.read_bytes()!r}")
            wt.unlink(missing_ok=True)
            rw.unlink(missing_ok=True)

            # E2 · FLAG PARITY. `outline` and `mint` render the same thing from the same story
            # file; the measured friction is copying a working `mint` line to `outline` and
            # getting `unrecognized arguments: --jira-project`.
            set_state(state)
            code, out = jf("outline", "--story", "9.1", "--jira-project", "TEST")
            c.check("E2 outline accepts --jira-project, like mint",
                    code == 0 and "unrecognized arguments" not in out, f"exit={code}: {out.strip()[:200]}")
            c.check("E2 ...and still renders the outline", "AC-1 (archive)" in out, out[:200])

            # ⛔ E3 · THE ARMED HOOK'S EXACT LINE (audit finding 4).
            # .agents/scripts/git-hooks/post-commit-jira-start.sh:119 runs
            #     "$PY" .agents/scripts/jira_feed.py start --key "$KEY" --timeout 10 --apply
            # on the FIRST commit of every chore/ · claude/ · epic/ branch, in every repo. An
            # argparse edit that disturbs `start` fires there - and VS Code HIDES hook output,
            # so it reads as a clean commit. This pins the hook's flags to the parser.
            set_state(state)
            code, out = jf("start", "--key", "TEST-7", "--timeout", "10", "--apply")
            c.check("E3 the post-commit hook's exact flag set still parses",
                    "unrecognized arguments" not in out and "invalid choice" not in out
                    and "error: argument" not in out, f"exit={code}: {out.strip()[:300]}")
            c.check("E3 ...and it actually transitions the ticket",
                    code == 0 and any(t["key"] == "TEST-7"
                                      for t in get_state(state).get("transitions", [])),
                    f"exit={code}: {out.strip()[:200]}")

    if c.block("SCC-298 · reconcile-actions: the close-out VERIFIES the task list"):
        import jira_feed  # noqa: E402

        # ⛔ THE DEFECT THIS BLOCK PINS. `finish` decides `Done` from what `## Your Actions`
        # CLAIMS, and nothing has ever checked whether a row's claim is still true - so SCC-288
        # sat at `Review Required` for a day over one box whose work was finished, authenticated
        # and attached. SCC-175 already ruled on the general shape for the merge row: "a tick is
        # a CLAIM, and `finish --apply` is what writes `Done` to Jira on the strength of it."
        # This is that ruling applied to every OTHER row - the difference being that most rows
        # have no `merge-base` to ask, so the check is derived per row and its ANSWER is recorded
        # beside it.
        #
        # Operator, 2026-08-23: "agents are terrible at checking off those task lists, especially
        # when its a user task, even if I tell them" - and the ruling on how a row gets ticked:
        # evidence where a check exists; where none does, ask the operator and tick on their
        # word, recorded either way.
        WT = (
            "# Walkthrough\n"
            "\n"
            "## Task Checklist\n"
            "\n"
            "- [ ] THE AGENT'S OWN ROW - must never be listed or tickable\n"
            "\n"
            "## Your Actions\n"
            "\n"
            "- [ ] **C0 - store the Jira API token.** The keychain item the attach door reads.\n"
            "- [x] **C1 - already settled.** Nothing owed here.\n"
            "- [ ] Click **Merge** on the PR when CI is green.\n"
            "- [ ] **The merge itself** - lands via this branch's PR.\n"
            "- [ ] **Rule the landing order.** SCC-280 or this lane first.\n"
        )
        # The line numbers a human sees, pinned here so a drift in the fixture is loud rather
        # than silently re-aiming every case below at a different row.
        L_C0, L_C1, L_CLICK, L_MERGE, L_ORDER = 9, 10, 11, 12, 13
        assert WT.splitlines()[L_C0 - 1].startswith("- [ ] **C0"), "fixture line map drifted"
        assert WT.splitlines()[L_MERGE - 1].startswith("- [ ] **The merge itself"), "drifted"

        GOOD = "keychain item `sudo-jira` present; REST GET returned 200 with the file listed"

        def wt_file(tmp: Path, text: str = WT) -> Path:
            p = tmp / "walkthrough.md"
            p.write_text(text, encoding="utf-8")
            return p

        def ra(path: Path, *args: str) -> tuple[int, str]:
            return run_script("jira_feed.py", "reconcile-actions",
                              "--walkthrough", str(path), *args)

        # ── A1 · the list, and the HOLD ───────────────────────────────────────────────
        with TempDir() as tmp:
            p = wt_file(tmp)
            code, out = ra(p)
            c.check("A1 an open section EXITS 3 - the same HELD code `finish` uses",
                    code == 3, f"exit={code}: {out.strip()[:300]}")
            # ⛔ PADDED, because `f"L{n}" in out` is a SUBSTRING test: "L1" matches "L10", so a
            # fixture whose rows moved into double digits would stop discriminating silently.
            c.check("A1 ...and every open row is named with its line number",
                    all(f"  L{n}  " in out for n in (L_C0, L_CLICK, L_MERGE, L_ORDER)),
                    f"missing a line number: {out.strip()[:400]}")
            # Bound to `code == 3` for the same reason as the refusal marker above: "the
            # string is absent" is trivially true of the empty output an unknown verb produces.
            c.check("A1 ...the SETTLED row is not listed",
                    code == 3 and f"  L{L_C1}  " not in out, out.strip()[:300])
            # ⛔ ANTI-VACUITY. `## Task Checklist` is full of `- [ ]` rows that are the AGENT's.
            # Listing them would hold every ticket forever - the mirror of the bug being fixed.
            c.check("A1 ...and the AGENT's own checklist rows are invisible",
                    code == 3 and "THE AGENT'S OWN ROW" not in out, out.strip()[:300])

        with TempDir() as tmp:
            p = wt_file(tmp, "# W\n\n## Your Actions\n\n- [x] settled\n")
            code, out = ra(p)
            c.check("A1 a section with nothing open EXITS 0",
                    code == 0, f"exit={code}: {out.strip()[:300]}")

        # ── A2 · the tick writes ONE line and proves itself ───────────────────────────
        with TempDir() as tmp:
            p = wt_file(tmp)
            before = p.read_text(encoding="utf-8").splitlines()
            code, out = ra(p, "--tick", str(L_C0), "--evidence", GOOD, "--source", "measured")
            after = p.read_text(encoding="utf-8").splitlines()
            c.check("A2 the tick exits 0", code == 0, f"exit={code}: {out.strip()[:300]}")
            diff = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
            c.check("A2 EXACTLY ONE line changed, and it is the one asked for",
                    len(before) == len(after) and diff == [L_C0 - 1],
                    f"changed lines (0-based): {diff}")
            row = after[L_C0 - 1] if len(after) >= L_C0 else ""
            c.check("A2 the row is now ticked", row.startswith("- [x] "), row)
            # Bound to the tick for the same reason: the ORIGINAL row also contains this text.
            c.check("A2 ...the original text survives",
                    row.startswith("- [x] ") and "**C0 - store the Jira API token.**" in row, row)
            c.check("A2 ...the SOURCE is recorded, not just the claim", "(measured)" in row, row)
            c.check("A2 ...and the evidence itself is in the file, where a human reads it",
                    GOOD in row, row)

        # ⛔ A2b · A WRAPPED ROW. Found by the review, reproduced before it was fixed: the proof
        # was appended to the CHECKBOX line, which for a row that wraps splices machine text
        # through the middle of the operator's sentence and orphans the rest of it -
        #     - [x] **Decide ...** This lane synced only the in-repo -- verified ... (operator): ...
        #           mirrors, deliberately, because it had not landed.
        # This lane's OWN walkthrough carries a three-line row, so it fired on its own artifact.
        # SCC-206 taught continuations to ride along because truncating them meant "the half that
        # says WHY reached nobody"; writing through them is that injury by another route.
        with TempDir() as tmp:
            p = wt_file(tmp, "# W\n\n## Your Actions\n\n"
                             "- [ ] **Decide the menu refresh.** This lane synced only the in-repo\n"
                             "      mirrors, deliberately, because it had not landed.\n"
                             "- [ ] A single-line row that must be untouched.\n")
            before = p.read_text(encoding="utf-8").splitlines()
            code, out = ra(p, "--tick", "5", "--evidence", GOOD, "--source", "operator")
            after = p.read_text(encoding="utf-8").splitlines()
            c.check("A2b a wrapped row ticks", code == 0, f"exit={code}: {out.strip()[:250]}")
            c.check("A2b the checkbox flips on the FIRST line and its text is NOT cut",
                    after[4].startswith("- [x] ")
                    and after[4].endswith("This lane synced only the in-repo"),
                    repr(after[4] if len(after) > 4 else after))
            c.check("A2b the proof lands after the operator's LAST word, not through the middle",
                    after[5].rstrip().endswith(GOOD) and "mirrors, deliberately," in after[5],
                    repr(after[5] if len(after) > 5 else after))
            c.check("A2b the line COUNT is unchanged, so every other row keeps its number",
                    len(before) == len(after), f"{len(before)} -> {len(after)}")
            c.check("A2b the sibling row is byte-identical",
                    before[6] == after[6], repr(after[6] if len(after) > 6 else after))
            c.check("A2b ...and the row is settled as far as `finish` is concerned",
                    jira_feed.open_actions(p.read_text(encoding="utf-8"))
                    == ["A single-line row that must be untouched."],
                    str(jira_feed.open_actions(p.read_text(encoding="utf-8"))))

        # ── A3 · the five refusals. Each must write NOTHING. ─────────────────────────
        REFUSALS = [
            ("A3a a line that is already ticked is not an open row", L_C1, GOOD, "measured"),
            ("A3b a line OUTSIDE `## Your Actions` is not tickable", 5, GOOD, "measured"),
            ("A3c empty evidence is refused", L_C0, "   ", "measured"),
            # ⛔ LONG on purpose. "done" is 4 characters, so the FLOOR refuses it and this
            # row never reached the deny-set at all - which is precisely how mutant M2
            # survived a green suite. This phrase clears the floor (21 chars, 3 words) and
            # can only be refused by the set.
            ("A3d contentless evidence that CLEARS the floor is still refused",
             L_C0, "confirmed by operator", "operator"),
            ("A3d2 ...and the archetypal one-word claim is refused too",
             L_C0, "done", "operator"),
            ("A3e a CEREMONY row is refused (SCC-193 - the agent RUNS those)",
             L_CLICK, GOOD, "measured"),
            ("A3f a MERGE row is refused (SCC-175 - `finish` computes it from the repo)",
             L_MERGE, GOOD, "measured"),
        ]
        # ⛔ EXIT 2 ALONE IS NOT EVIDENCE OF A REFUSAL, and this block's own first RED run
        # proved it: argparse exits 2 on an unknown verb, so every row below PASSED against a
        # `jira_feed.py` that had never heard of `reconcile-actions` - nothing ran, so nothing
        # was written either. A case that is green before the feature exists cannot fail when
        # the feature breaks (`red-test-can-die-before-its-assertion`). So the refusal must
        # ANNOUNCE itself with a marker the verb owns, and the row asserts on that.
        REFUSAL_MARK = "jira-feed: REFUSED"
        for label, line, ev, src in REFUSALS:
            with TempDir() as tmp:
                p = wt_file(tmp)
                raw = p.read_bytes()
                code, out = ra(p, "--tick", str(line), "--evidence", ev, "--source", src)
                c.check(label, code == 2 and REFUSAL_MARK in out,
                        f"exit={code} (argparse also exits 2 - the marker is the tell): "
                        f"{out.strip()[:300]}")
                c.check(label + " - and NOTHING was written",
                        p.read_bytes() == raw, "the file changed on a refusal")

        # ⛔ A3i · THE DENY-SET POLICES ITSELF. Every entry must be something the FLOOR cannot
        # already refuse, or it is an unreachable branch that looks like a guard. The first draft
        # was 37 short words and 35 of them were dead - measured, not guessed: mutant M2 gutted
        # the whole set to `()` and the suite stayed green. This row is what stops that returning
        # the next time somebody adds "ok" to the list.
        c.check("A3i every deny-set entry CLEARS the floor (else it is dead weight)",
                not [e for e in jira_feed._GENERIC_EVIDENCE
                     if len(e) < jira_feed._MIN_EVIDENCE_CHARS
                     or len(e.split()) < jira_feed._MIN_EVIDENCE_WORDS],
                str(sorted(e for e in jira_feed._GENERIC_EVIDENCE
                           if len(e) < jira_feed._MIN_EVIDENCE_CHARS
                           or len(e.split()) < jira_feed._MIN_EVIDENCE_WORDS)))
        # ⛔ "Not empty" was `>= 10` against a 19-entry set - pruning nine would have passed.
        # The property that actually matters is that every entry is REFUSED end to end, which
        # also fails if the set is emptied (`all([])` is True, so the count guards that).
        c.check("A3i ...and EVERY entry is genuinely refused, not just listed",
                len(jira_feed._GENERIC_EVIDENCE) > 0
                and all(not jira_feed.evidence_ok(e)[0] for e in jira_feed._GENERIC_EVIDENCE),
                str([e for e in jira_feed._GENERIC_EVIDENCE if jira_feed.evidence_ok(e)[0]]))

        # ⛔ THE FLOOR NEEDS ITS OWN CASE, and designing the mutant table is what showed it.
        # A3d ticks with "done", which the DENY-SET catches - so deleting the length/word floor
        # entirely left every case green. This row refuses on the floor ALONE: "ran it" is in no
        # deny-set and says nothing.
        with TempDir() as tmp:
            p = wt_file(tmp)
            raw = p.read_bytes()
            code, out = ra(p, "--tick", str(L_C0), "--evidence", "ran it", "--source", "measured")
            c.check("A3g thin evidence the deny-set has never seen is STILL refused",
                    code == 2 and REFUSAL_MARK in out, f"exit={code}: {out.strip()[:300]}")
            c.check("A3g - and NOTHING was written", p.read_bytes() == raw, "the file changed")

        # ⛔ FAIL CLOSED, exactly as `finish` does. A walkthrough with no section at all is a
        # REFUSAL, never "nothing is owed" - an absent section is not evidence of anything, and
        # collapsing the two is the empty-input-reads-as-pass shape. Also found by the sweep
        # table: nothing here distinguished `None` from `[]`.
        for label, args_ in (("listing", ()),
                             ("ticking", ("--tick", "5", "--evidence", GOOD,
                                          "--source", "measured"))):
            with TempDir() as tmp:
                p = wt_file(tmp, "# W\n\n## Task Checklist\n\n- [ ] the agent's own row\n")
                raw = p.read_bytes()
                code, out = ra(p, *args_)
                c.check(f"A1c no `## Your Actions` section at all REFUSES when {label}",
                        code == 2 and REFUSAL_MARK in out, f"exit={code}: {out.strip()[:300]}")
                c.check(f"A1c - and NOTHING was written when {label}",
                        p.read_bytes() == raw, "the file changed")

        # A3h · `--tick` with no recorded source is the unattributed claim this verb replaces.
        # argparse cannot say "required WITH another flag", so the parser says it by hand.
        for missing in (("--evidence", GOOD), ("--source", "measured")):
            with TempDir() as tmp:
                p = wt_file(tmp)
                raw = p.read_bytes()
                code, out = ra(p, "--tick", str(L_C0), *missing)
                c.check(f"A3h --tick without its companion is refused (gave only {missing[0]})",
                        code != 0 and "--tick needs" in out, f"exit={code}: {out.strip()[:250]}")
                c.check(f"A3h - and NOTHING was written (gave only {missing[0]})",
                        p.read_bytes() == raw, "the file changed")

        # ⛔ THE CONTROL THAT FORBIDS THE LAZY FIX. Every refusal above passes if the verb
        # refuses everything, and a gate that rejects every case is as broken as one that
        # rejects none. This row must stay green.
        with TempDir() as tmp:
            p = wt_file(tmp)
            code, out = ra(p, "--tick", str(L_ORDER),
                           "--evidence", "operator ruled SCC-298 lands first, 2026-08-23",
                           "--source", "operator")
            c.check("A3 (control, must stay green) a REAL operator row with REAL words is ACCEPTED",
                    code == 0, f"exit={code}: {out.strip()[:300]}")

        # ── The review's edge-case findings, every one reproduced on the real CLI first ──
        #
        # ⛔ A3j IS THE CRITICAL ONE. `evidence_ok` normalised a COLLAPSED copy while `tick_row`
        # wrote the RAW string, so a newline in the evidence went into the walkthrough. A line
        # starting `## ` ends the section for `_collect`; a stray ``` opens a fence `_unfenced`
        # hides the rest of the file behind. Either way `open_actions` returns `[]` rather than
        # `None`, `cmd_finish` takes the "nothing owed" path, and the ticket CLOSES over rows
        # nobody checked - while this verb prints "`## Your Actions` is now CLEAR". Measured
        # before the fix: two open rows survived and `open_actions` returned `[]`.
        for label, ev in (("a heading", "ran the suite:\n## Summary\n12 passed"),
                          ("a fence", "the doc opens with\n```bash\npython3 check_gate.py"),
                          ("a bare newline", "ran the suite\nand it passed cleanly here")):
            with TempDir() as tmp:
                p = wt_file(tmp)
                raw = p.read_bytes()
                code, out = ra(p, "--tick", str(L_C0), "--evidence", ev, "--source", "measured")
                c.check(f"A3j evidence carrying {label} is refused",
                        code == 2 and REFUSAL_MARK in out, f"exit={code}: {out.strip()[:250]}")
                c.check(f"A3j - and NOTHING was written ({label})",
                        p.read_bytes() == raw, "a line break reached the file")
        with TempDir() as tmp:   # the whole point: the OTHER rows must still hold the ticket
            p = wt_file(tmp)
            ra(p, "--tick", str(L_C0), "--evidence", "ran it:\n## Summary\nok", "--source", "measured")
            c.check("A3j ...so `open_actions` still HOLDS the ticket",
                    len(jira_feed.open_actions(p.read_text(encoding="utf-8"))) == 4,
                    str(jira_feed.open_actions(p.read_text(encoding="utf-8"))))

        # A3k · the proof becomes part of the row, so it can CREATE a merge row that `finish`
        # then re-opens forever. `tick_row` refused to TICK one; nothing stopped it writing one.
        with TempDir() as tmp:
            p = wt_file(tmp)
            raw = p.read_bytes()
            code, out = ra(p, "--tick", str(L_C0), "--source", "operator",
                           "--evidence", "SCC-280 lands first, then /smh-close-task-merge-tree")
            c.check("A3k evidence that would MANUFACTURE a merge row is refused",
                    code == 2 and REFUSAL_MARK in out, f"exit={code}: {out.strip()[:250]}")
            c.check("A3k - and NOTHING was written", p.read_bytes() == raw, "the file changed")

        # A3l · `--expect` verifies the ROW, not the number. Both directions.
        with TempDir() as tmp:
            p = wt_file(tmp)
            raw = p.read_bytes()
            code, out = ra(p, "--tick", str(L_ORDER), "--evidence", GOOD, "--source", "measured",
                           "--expect", "store the Jira API token")
            c.check("A3l --expect refuses when the row is not the one you read",
                    code == 2 and REFUSAL_MARK in out, f"exit={code}: {out.strip()[:250]}")
            c.check("A3l - and NOTHING was written", p.read_bytes() == raw, "the file changed")
        with TempDir() as tmp:
            p = wt_file(tmp)
            code, _ = ra(p, "--tick", str(L_C0), "--evidence", GOOD, "--source", "measured",
                         "--expect", "store the Jira API token")
            c.check("A3l (control) --expect ACCEPTS when it does match", code == 0, f"exit={code}")

        # A3m · `--date` lands on the same line as the evidence and took the same vector.
        with TempDir() as tmp:
            p = wt_file(tmp)
            raw = p.read_bytes()
            code, out = ra(p, "--tick", str(L_C0), "--evidence", GOOD, "--source", "measured",
                           "--date", "today\n## Summary")
            c.check("A3m --date must be a plain ISO date",
                    code == 2 and REFUSAL_MARK in out, f"exit={code}: {out.strip()[:200]}")
            c.check("A3m - and NOTHING was written", p.read_bytes() == raw, "the file changed")

        # ⛔ A2c · THIS VERB REWRITES THE WHOLE FILE, so it must not damage the bytes it did not
        # touch. `wf.read_text` is utf-8-sig + errors="replace" + universal newlines, and all
        # three are destructive on a round trip. Measured before the fix: `caf\xe9` came back
        # U+FFFD permanently, a BOM was swallowed, and a CRLF walkthrough was rewritten to LF.
        with TempDir() as tmp:
            p = tmp / "walkthrough.md"
            p.write_bytes(b"\xef\xbb\xbf# W\r\n\r\n## Your Actions\r\n\r\n"
                          b"- [ ] **C0** store the token for caf\xe9.\r\n"
                          b"- [ ] **C1** attach the plan.\r\n")
            code, out = ra(p, "--tick", "5", "--evidence", GOOD, "--source", "measured")
            got = p.read_bytes()
            c.check("A2c the tick lands on a CRLF/BOM/invalid-byte file",
                    code == 0, f"exit={code}: {out.strip()[:200]}")
            c.check("A2c the BOM survives", got.startswith(b"\xef\xbb\xbf"), repr(got[:8]))
            c.check("A2c CRLF is not rewritten to LF",
                    got.count(b"\r\n") == 6 and b"\n\n" not in got.replace(b"\r\n", b"|"),
                    f"crlf={got.count(bytes([13,10]))}")
            c.check("A2c the undecodable byte is preserved, not replaced with U+FFFD",
                    b"caf\xe9" in got and b"\xef\xbf\xbd" not in got, repr(got[-90:]))

        # A2d · `splitlines` breaks on \u2028 but `rstrip("\r\n")` never knew about it, so the
        # separator was dropped on write: two rows welded and the open one below it vanished.
        with TempDir() as tmp:
            p = wt_file(tmp, "# W\n\n## Your Actions\n\n"
                             "- [ ] **C0** first row.\u2028- [ ] **C1** second row.\n")
            code, _ = ra(p, "--tick", "5", "--evidence", GOOD, "--source", "measured")
            left = jira_feed.open_actions(p.read_text(encoding="utf-8"))
            c.check("A2d an exotic line separator does not weld the row below into the tick",
                    code == 0 and left == ["**C1** second row."], f"exit={code} left={left}")

        # A1d · an empty `- [ ]` is a real obligation, but printed bare it is a line number with
        # nothing to check, next to a banner ordering the reader to check it.
        with TempDir() as tmp:
            p = wt_file(tmp, "# W\n\n## Your Actions\n\n- [ ]\n")
            code, out = ra(p)
            c.check("A1d an empty row is listed with a placeholder, not as a bare number",
                    code == 3 and "(empty row" in out, f"exit={code}: {out.strip()[:200]}")

        # ⛔ A1e · THE EXIT CODE MUST ANSWER THE QUESTION `finish` ANSWERS. Reproduced: with every
        # operator obligation settled, the verb still said "1 row(s) still open" and exited 3 -
        # over the MERGE row, which it refuses to tick and which `finish` clears from the repo
        # (SCC-175). Almost every walkthrough carries one, so the verb could essentially never
        # reach 0, and the door's rule 3 would report a finished lane as held: SCC-288 rebuilt
        # for the merge row. Found by the blind lens; it was live in this lane's own dogfood run
        # and I had read that output as correct.
        with TempDir() as tmp:
            p = wt_file(tmp, "# W\n\n## Your Actions\n\n"
                             "- [x] **C0** settled.\n"
                             "- [ ] **The merge itself** - lands via this branch's PR.\n")
            code, out = ra(p)
            c.check("A1e a merge row ALONE does not hold the verb - it exits 0 like `finish`",
                    code == 0, f"exit={code}: {out.strip()[:300]}")
            c.check("A1e ...and it is still LISTED, attributed to `finish`",
                    "  L6  " in out and "merge row" in out, out.strip()[:300])
        with TempDir() as tmp:   # the complement: a real row still holds
            p = wt_file(tmp, "# W\n\n## Your Actions\n\n"
                             "- [ ] **C0** store the token.\n"
                             "- [ ] **The merge itself** - lands via this branch's PR.\n")
            code, out = ra(p)
            c.check("A1e (complement) a settleable row beside it STILL holds at 3",
                    code == 3 and "1 row(s) you must settle" in out,
                    f"exit={code}: {out.strip()[:300]}")

        # A1f · a CEREMONY row is not operator work, but it still blocks - `finish` REFUSES on
        # one (exit 2). So it is reported as something to DELETE, and the listing says to re-run
        # afterwards, because deleting shifts every number below it.
        with TempDir() as tmp:
            p = wt_file(tmp, "# W\n\n## Your Actions\n\n"
                             "- [ ] Click **Merge** on the PR when CI is green.\n")
            code, out = ra(p)
            c.check("A1f a ceremony row still blocks, and is reported as a DELETE",
                    code == 3 and "DELETE" in out, f"exit={code}: {out.strip()[:300]}")
            c.check("A1f ...and the banner warns that deleting invalidates the numbers",
                    "RE-RUN" in out.upper(), out.strip()[:600])

        # TA-2 · the decoration strip is the deny-set's ONLY defence against "add a full stop",
        # and a mutant emptying `_EVIDENCE_TRIM` survived all 462 cases. The code comment claims
        # "a deny-set alone is defeated by adding a full stop"; this is that claim, pinned.
        for variant in ("`Confirmed By Operator.`", "confirmed by operator!!",
                        "  *Confirmed by operator*  "):
            c.check(f"A3n decorated/cased deny-set text is still refused: {variant!r}",
                    not jira_feed.evidence_ok(variant)[0], jira_feed.evidence_ok(variant)[1])

        # TA-3 · `_TICK_RE` and `_OPEN_ITEM_RE` must agree about what an open row looks like.
        # Narrowing `_TICK_RE` to `^(- )\[\s\]` survived all 462 cases: every fixture was a
        # flush `- [ ]`, so the "unreachable, kept as a hard stop" comment was untested.
        with TempDir() as tmp:
            p = wt_file(tmp, "# W\n\n## Your Actions\n\n"
                             "  - [ ] **C0** an indented row.\n"
                             "* [ ] **C1** a star bullet.\n")
            code, _ = ra(p, "--tick", "5", "--evidence", GOOD, "--source", "measured")
            code2, _ = ra(p, "--tick", "6", "--evidence", GOOD, "--source", "measured")
            got = p.read_text(encoding="utf-8").splitlines()
            c.check("A2e an INDENTED row ticks and keeps its indentation verbatim",
                    code == 0 and got[4].startswith("  - [x] **C0**"), repr(got[4]))
            c.check("A2e a `*` bullet ticks and keeps its bullet character",
                    code2 == 0 and got[5].startswith("* [x] **C1**"), repr(got[5]))

        # TA-6 · neither the marker nor the date was pinned; deleting both from the proof string
        # survived all 462 cases, because A2 only checked `(measured)` and the evidence text.
        with TempDir() as tmp:
            p = wt_file(tmp)
            ra(p, "--tick", str(L_C0), "--evidence", GOOD, "--source", "measured",
               "--date", "2026-01-01")
            row = p.read_text(encoding="utf-8").splitlines()[L_C0 - 1]
            c.check("A2f the `-- verified` marker is in the row",
                    jira_feed.TICK_MARK in row, repr(row))
            c.check("A2f ...and the DATE the caller gave, not today's",
                    "2026-01-01" in row, repr(row))

        # TA-4 · the missing-walkthrough refusal is the one branch with no case; `if False:`
        # survived the whole suite. The reject half of a gate is half the gate.
        with TempDir() as tmp:
            code, out = ra(tmp / "nope.md")
            c.check("A1g a walkthrough that does not exist is REFUSED, with the marker",
                    code == 2 and REFUSAL_MARK in out, f"exit={code}: {out.strip()[:200]}")

        # TA-5 · the listing's guidance tags are what the agent acts on; blanking them survived.
        with TempDir() as tmp:
            p = wt_file(tmp)
            _, out = ra(p)
            c.check("A1h the listing TELLS the agent what to do with each special row",
                    "leave it" in out and "DELETE the row" in out, out.strip()[:600])

        # TA-9 · one walk, so the two readers cannot disagree - pinned across TWO sections,
        # which is the shape SCC-155 was raised on.
        TWO = ("# W\n\n## Your Actions\n\n- [ ] A\n\n## Notes\n\nx\n\n"
               "## Your Actions\n\n- [ ] B that\n      wraps\n")
        c.check("A1i `open_actions` and `open_action_rows` agree, across two sections",
                jira_feed.open_actions(TWO) == [r for _, _, r in jira_feed.open_action_rows(TWO)]
                == ["A", "B that wraps"],
                f"{jira_feed.open_actions(TWO)} vs {jira_feed.open_action_rows(TWO)}")
        c.check("A1i ...and both answer None for a file with no section",
                jira_feed.open_actions("# W\n") is None
                and jira_feed.open_action_rows("# W\n") is None, "one of them collapsed to []")

        # ── A5 · end to end: the row SCC-288 hung on, reconciled, then finish is clear ──
        with TempDir() as tmp:
            p = wt_file(tmp, "# W\n\n## Your Actions\n\n"
                             "- [ ] **C0 - store the Jira API token.** Already done on the Mac.\n")
            code, out = ra(p, "--tick", "5", "--evidence", GOOD, "--source", "measured")
            c.check("A5 the only open row reconciles", code == 0, f"exit={code}: {out.strip()[:200]}")
            c.check("A5 ...and `open_actions` - what `finish` reads - is now CLEAR",
                    jira_feed.open_actions(p.read_text(encoding="utf-8")) == [],
                    str(jira_feed.open_actions(p.read_text(encoding="utf-8"))))
            code2, _ = ra(p)
            c.check("A5 ...so the list exits 0", code2 == 0, f"exit={code2}")


    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
