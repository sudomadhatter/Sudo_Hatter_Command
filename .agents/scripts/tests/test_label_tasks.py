"""label_tasks.py — the set math, the gates, and the staleness detector. (SCC-56, SCC-155)

Offline by construction: every case here drives `resolve` and `stamp` (dry run) through
temp files, so nothing reaches `acli` or the network. The two board-reading verbs (`plan`,
`check`) are exercised for their REFUSALS, which is where their damage would be.

SCC-155 renamed this from `test_parallel_check.py` when the engine became two-mode. Every
case above the `TASK MODE` banner is inherited unchanged and rides the rename as
CHARACTERIZATION — it was green before the rename and green after, and none of it is
evidence about the new behaviour. Everything below the banner was written RED first.

Stdlib only and no pytest, matching the scripts under test.
"""
from __future__ import annotations

import io
import json
import os
import stat
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases, TempDir, run_script  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import label_tasks as lt  # noqa: E402


# ── a real acli stub, so the board-WRITE path actually executes ────────────────
# ⛔ SCC-155 review finding (critical). Every case in this file drove `resolve` and `stamp`
# through temp files with no stub at all, so `--apply` was never passed and the whole write
# half - the acli argv, the comma-join, the `--key`, the failure arm - was unexecuted. A
# mutant that threw away the computed label set and wrote the ticket's EXISTING labels back
# survived a full 78/78 green run. `label_plan` being pure and well-tested proves the
# decision; nothing proved the decision reached Jira.
STUB = r'''
import json, sys
from pathlib import Path
args = sys.argv[1:]
state = Path(__import__("os").environ["STUB_STATE"])
st = json.loads(state.read_text()) if state.exists() else {}


def val(flag):
    return args[args.index(flag) + 1] if flag in args else None


head = args[:3]
if head == ["jira", "workitem", "view"]:
    if st.get("view_fail"):
        print("Error: could not reach the board", file=sys.stderr)
        sys.exit(1)
    key = args[3]
    print(json.dumps({"key": key, "fields": {
        "summary": st.get("summaries", {}).get(key, ""),
        "issuetype": {"name": st.get("types", {}).get(key, "Task")}}}))
elif head == ["jira", "workitem", "search"]:
    print(json.dumps(st.get("rows", [])))
elif head == ["jira", "workitem", "edit"]:
    # ⛔⛔ MEASURED 2026-08-17 AGAINST THE LIVE BOARD (SCC-202): `--labels` **ADDS**. It does
    # NOT replace, and `--remove-labels` is a separate flag; acli honours both in one call.
    # This stub said "REPLACES" and that lie hid a live defect for as long as it stood -
    # `set_labels` sent the reduced set to strip a label, which against an adding API re-adds
    # everything surviving and removes nothing, then reported `-parallel-ok` as done. A story
    # that WAS parallel-ok and now overlaps kept the tag while the tool said it was gone,
    # which is how two colliding lanes get run side by side. A stub differently wrong from the
    # tool it stands in for makes a broken writer look correct.
    if st.get("label_fail"):
        print("Error: labels rejected", file=sys.stderr)
        sys.exit(1)
    cur = list(st.get("labels", {}).get(val("--key"), []))
    for x in (val("--labels") or "").split(","):
        if x and x not in cur:
            cur.append(x)
    drop = {x for x in (val("--remove-labels") or "").split(",") if x}
    st.setdefault("labels", {})[val("--key")] = [x for x in cur if x not in drop]
    state.write_text(json.dumps(st))
    print("edited")
elif head == ["jira", "workitem", "comment"] and args[3] == "create":
    if st.get("comment_fail"):
        print("Error: comment rejected", file=sys.stderr)
        sys.exit(1)
    # label_tasks posts INLINE with --body; jira_feed writes a temp file and passes
    # --body-file. The stub honours both rather than the one it was written against, so it
    # cannot silently pass a caller that switched form.
    body = val("--body")
    if body is None and val("--body-file"):
        body = Path(val("--body-file")).read_text()
    st.setdefault("comments", []).append(body or "")
    state.write_text(json.dumps(st))
    print("commented")
elif head == ["jira", "workitem", "comment"] and args[3] == "list":
    print(json.dumps({"comments": []}))
else:
    print("{}")
'''


def acli_stub(root: Path) -> tuple[Path, Path]:
    """(launcher, state-file). A REAL executable on both machines: cmd.exe cannot run a
    shebang and /bin/sh cannot run a .bat, and everything downstream is the production path."""
    py = root / "stub.py"
    py.write_text(STUB, encoding="utf-8")
    if os.name == "nt":
        launcher = root / "acli.bat"
        launcher.write_text(f'@echo off\r\n"{sys.executable}" "{py}" %*\r\n', encoding="utf-8")
    else:
        launcher = root / "acli"
        launcher.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{py}" "$@"\n',
                            encoding="utf-8")
        launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)
    return launcher, root / "state.json"


def child(key: str, sid: str, *, grounded: bool = True, terminal: bool = False,
          in_flight: bool = False, labels: list[str] | None = None) -> dict:
    return {"key": key, "summary": f"{sid} - story {key}", "status": "To Do",
            "category": "done" if terminal else ("indeterminate" if in_flight else "new"),
            "labels": labels or [], "terminal": terminal, "in_flight": in_flight,
            "story_id": sid, "umbrella": False, "grounded": grounded,
            "sources": [{"kind": "story", "path": f"_bmad/bmm/stories/story-{sid}.md"}]
                       if grounded else [],
            "authority": "story" if grounded else None,
            "reason": None if grounded else f"no story file for {sid}",
            "next_command": None if grounded else f"/cicd-write-story-tests {sid}"}


def subtask(key: str, *, grounded: bool = True, terminal: bool = False,
            in_flight: bool = False, labels: list[str] | None = None,
            parent: str = "SCC-99") -> dict:
    """A Task-mode child: a `Subtask`, so no BMAD number and no story file anywhere."""
    return {"key": key, "summary": f"{key} - do the thing", "status": "To Do",
            "category": "done" if terminal else ("indeterminate" if in_flight else "new"),
            "labels": labels or [], "terminal": terminal, "in_flight": in_flight,
            "type": "Subtask", "story_id": None, "umbrella": False, "grounded": grounded,
            "sources": [{"kind": "plan",
                         "path": f"_artifacts/_main/2026-01-01_{key}/implementation_plan.md"}]
                       if grounded else [],
            "authority": "plan" if grounded else None,
            "reason": None if grounded else "no lane branch, no plan, no description",
            "next_command": None if grounded else f"/smh-plan-task {parent}"}


def packet(children: list[dict], parent: str = "AVCH-13", mode: str = "story") -> dict:
    return {"parent": parent, "parent_summary": "Epic 12 - Test", "epic": "12",
            "mode": mode, "repo": "/tmp/repo", "base": "main", "children": children,
            "child_keys": sorted(c["key"] for c in children)}


def run_resolve(tmp: Path, children: list[dict], touch: dict,
                mode: str = "story", parent: str = "AVCH-13") -> dict:
    (tmp / "plan.json").write_text(json.dumps(packet(children, parent, mode)),
                                   encoding="utf-8")
    (tmp / "touch.json").write_text(json.dumps(touch), encoding="utf-8")
    code, out = run_script("label_tasks.py", "resolve",
                           "--plan", str(tmp / "plan.json"),
                           "--touchsets", str(tmp / "touch.json"),
                           "--out", str(tmp / "verdicts.json"))
    if code != 0:
        return {"_exit": code, "_out": out}
    res = json.loads((tmp / "verdicts.json").read_text(encoding="utf-8"))
    res["_exit"] = code
    res["_by"] = {v["key"]: v for v in res["verdicts"]}
    return res


def main() -> int:
    c = Cases("label_tasks")

    # ── the grounding gate ─────────────────────────────────────────────────────
    with TempDir() as tmp:
        r = run_resolve(tmp, [child("A-1", "1.1"), child("A-2", "1.2", grounded=False)],
                        {"A-1": {"paths": ["backend/x.py"]}})
        c.check("ungrounded child reads 'no story'",
                r["_by"]["A-2"]["verdict"] == "no-story", str(r["_by"]["A-2"]))
        c.check("ungrounded child is NEVER in the approved set",
                "A-2" not in r["approved"], str(r["approved"]))
        c.check("ungrounded row prints the command that unlocks it",
                r["_by"]["A-2"].get("command") == "/cicd-write-story-tests 1.2",
                str(r["_by"]["A-2"].get("command")))

    # ── overlap ────────────────────────────────────────────────────────────────
    with TempDir() as tmp:
        r = run_resolve(tmp, [child("A-1", "1.1"), child("A-2", "1.2")],
                        {"A-1": {"paths": ["backend/shared.py", "backend/a.py"]},
                         "A-2": {"paths": ["backend/shared.py"]}})
        c.check("two children on one source path are not both approved",
                len(r["approved"]) == 1, str(r["approved"]))
        loser = "A-2" if "A-1" in r["approved"] else "A-1"
        c.check("the loser reads 'after <the winner>'",
                r["_by"][loser]["verdict"] == "after", str(r["_by"][loser]))
        c.check("the lock names the shared path as evidence",
                "backend/shared.py" in r["_by"][loser]["evidence"],
                r["_by"][loser]["evidence"])

    # ── planning artifacts are not overlap ─────────────────────────────────────
    with TempDir() as tmp:
        r = run_resolve(tmp, [child("A-1", "1.1"), child("A-2", "1.2")],
                        {"A-1": {"paths": ["_artifacts/x/implementation_plan.md",
                                           "_bmad-output/notes.md", "backend/a.py"]},
                         "A-2": {"paths": ["_artifacts/x/implementation_plan.md",
                                           "_bmad/bmm/stories/s.md", "backend/b.py"]}})
        c.check("overlap ONLY in planning dirs still approves both",
                sorted(r["approved"]) == ["A-1", "A-2"], str(r["approved"]))

    # ── contract edges ─────────────────────────────────────────────────────────
    with TempDir() as tmp:
        r = run_resolve(tmp, [child("A-1", "1.1"), child("A-2", "1.2")],
                        {"A-1": {"paths": ["backend/a.py"],
                                 "imports": ["backend/newmod.py"]},
                         "A-2": {"paths": ["backend/b.py"],
                                 "creates": ["backend/newmod.py"]}})
        c.check("import-of-a-created-symbol locks despite zero file overlap",
                len(r["approved"]) == 1, str(r["approved"]))

    with TempDir() as tmp:
        r = run_resolve(tmp, [child("A-1", "1.1"), child("A-2", "1.2")],
                        {"A-1": {"paths": ["backend/a.py"], "blocked_by": ["A-2"]},
                         "A-2": {"paths": ["backend/b.py"]}})
        c.check("declared blocked_by locks regardless of files",
                len(r["approved"]) == 1, str(r["approved"]))

    # ── blocked_by is DIRECTIONAL (SCC-226 ride-along, 2026-08-20) ────────────
    # Stored symmetric, the solver maximized set size by seating the DECLARERS and
    # locking their prerequisite behind them - measured on SCC-225's own set:
    # SCC-227 (declares blocked_by: SCC-226) came back approved, with SCC-226
    # printed "after SCC-227". Two declarers on one blocker is the minimal repro;
    # at two nodes the sort order happens to pick the blocker and hides it.
    with TempDir() as tmp:
        r = run_resolve(tmp, [child("A-1", "1.1"), child("A-2", "1.2"),
                              child("A-3", "1.3")],
                        {"A-1": {"paths": ["backend/a.py"]},
                         "A-2": {"paths": ["backend/b.py"], "blocked_by": ["A-1"]},
                         "A-3": {"paths": ["backend/c.py"], "blocked_by": ["A-1"]}})
        c.check("the BLOCKER is approved, never displaced by its dependents",
                "A-1" in r["approved"], str(r["approved"]))
        c.check("a declarer reads 'after <its blocker>' - direction preserved",
                r["_by"]["A-2"]["verdict"] == "after"
                and r["_by"]["A-2"]["detail"] == "after A-1", str(r["_by"]["A-2"]))
        c.check("both declarers wait on the same blocker",
                r["_by"]["A-3"].get("detail") == "after A-1", str(r["_by"]["A-3"]))

    # ── a blocker OUTSIDE the run keeps its declarer free (SCC-225 review wave) ──
    # The directional fix's own comment promised this and no fixture covered it -
    # executed mutant: dropping the membership test (any blocked_by = follower) ran
    # 104/104 green while silently stripping candidacy from every lane blocked by a
    # LANDED ticket. This is that missing fixture: A-9 is terminal (landed), so A-2's
    # declared dependency on it is satisfied history, not a live collision.
    with TempDir() as tmp:
        r = run_resolve(tmp, [child("A-1", "1.1"), child("A-2", "1.2"),
                              child("A-9", "1.9", terminal=True)],
                        {"A-1": {"paths": ["backend/a.py"]},
                         "A-2": {"paths": ["backend/b.py"], "blocked_by": ["A-9"]}})
        c.check("a LANDED (terminal) blocker frees its declarer - approved, not follower",
                sorted(r["approved"]) == ["A-1", "A-2"], str(r["approved"]))

    # ── blocked_by SHAPE cannot silently free a declarer (SCC-225 review wave) ──
    # Executed: a scalar string iterated characters; a case-slipped key matched
    # nothing - both approved BOTH lanes, indistinguishable from a landed blocker.
    with TempDir() as tmp:
        r = run_resolve(tmp, [child("A-1", "1.1"), child("A-2", "1.2")],
                        {"A-1": {"paths": ["backend/a.py"]},
                         "A-2": {"paths": ["backend/b.py"], "blocked_by": "A-1"}})
        c.check("a SCALAR blocked_by locks like the list form - never char-iterated",
                r["approved"] == ["A-1"] and r["_by"]["A-2"]["verdict"] == "after",
                str(r["_by"]["A-2"]))
    with TempDir() as tmp:
        r = run_resolve(tmp, [child("A-1", "1.1"), child("A-2", "1.2")],
                        {"A-1": {"paths": ["backend/a.py"]},
                         "A-2": {"paths": ["backend/b.py"], "blocked_by": ["a-1"]}})
        c.check("a case-slipped blocker key still locks its declarer",
                r["approved"] == ["A-1"] and r["_by"]["A-2"]["detail"] == "after A-1",
                str(r["_by"]["A-2"]))
    # a self-reference is dropped LOUDLY, never a permanent self-wedge
    with TempDir() as tmp:
        r = run_resolve(tmp, [child("A-1", "1.1"), child("A-2", "1.2")],
                        {"A-1": {"paths": ["backend/a.py"]},
                         "A-2": {"paths": ["backend/b.py"], "blocked_by": ["A-2"]}})
        c.check("blocked_by SELF is dropped (warned), not an unsatisfiable 'after itself'",
                sorted(r["approved"]) == ["A-1", "A-2"]
                and r["_by"]["A-2"]["verdict"] == "approved", str(r["_by"]["A-2"]))

    # ── fails toward locked ────────────────────────────────────────────────────
    with TempDir() as tmp:
        r = run_resolve(tmp, [child("A-1", "1.1"), child("A-2", "1.2"),
                              child("A-3", "1.3", grounded=False, in_flight=True)],
                        {"A-1": {"paths": ["backend/a.py"]},
                         "A-2": {"paths": ["backend/b.py"]}})
        c.check("an in-flight child with unknown surfaces approves NOTHING",
                r["approved"] == [], str(r["approved"]))
        c.check("its disjoint siblings read 'waiting', not 'approved'",
                r["_by"]["A-1"]["verdict"] == "waiting", str(r["_by"]["A-1"]))

    # ── umbrellas, terminals, and the no-blank-row rule ────────────────────────
    with TempDir() as tmp:
        kids = [child("A-1", "1.1"), child("A-2", "1.2"),
                child("A-9", "1.9", terminal=True)]
        umb = child("A-0", "1")
        umb.update({"umbrella": True, "contains": ["A-1", "A-2"]})
        r = run_resolve(tmp, [umb, *kids],
                        {"A-1": {"paths": ["backend/a.py"]},
                         "A-2": {"paths": ["backend/b.py"]}})
        c.check("an umbrella gets no verdict row", "A-0" not in r["_by"], str(r["_by"].keys()))
        c.check("the umbrella is carried as context instead",
                r["umbrellas"] and r["umbrellas"][0]["key"] == "A-0", str(r["umbrellas"]))
        c.check("a done child is not assessed", "A-9" not in r["_by"], str(r["_by"].keys()))
        c.check("every remaining child carries exactly one verdict",
                sorted(r["_by"]) == ["A-1", "A-2"], str(sorted(r["_by"])))
        c.check("the stamp records the FULL child set, umbrella included",
                "A-0" in r["stamp"] and "A-9" in r["stamp"], r["stamp"])

    # ── determinism ────────────────────────────────────────────────────────────
    with TempDir() as tmp:
        touch = {k: {"paths": [f"backend/{k}.py"]} for k in ("A-1", "A-2", "A-3")}
        touch["A-3"]["paths"].append("backend/A-1.py")
        first = run_resolve(tmp, [child("A-1", "1.1"), child("A-2", "1.2"),
                                  child("A-3", "1.3")], touch)
        second = run_resolve(tmp, [child("A-3", "1.3"), child("A-1", "1.1"),
                                   child("A-2", "1.2")], touch)
        c.check("same input, same approved set regardless of child order",
                first["approved"] == second["approved"] == ["A-1", "A-2"],
                f"{first['approved']} vs {second['approved']}")

    # ── refusing to guess ──────────────────────────────────────────────────────
    with TempDir() as tmp:
        r = run_resolve(tmp, [child("A-1", "1.1"), child("A-2", "1.2")],
                        {"A-1": {"paths": ["backend/a.py"]}})
        c.check("a grounded child with NO touch-set is refused, never assumed empty",
                r["_exit"] == 2 and "A-2" in r["_out"], f"exit={r['_exit']} {r['_out'][:120]}")

    # ── the label write is a REWRITE, not an add ───────────────────────────────
    # THE self-correcting property, and the whole reason the writer moved out of (1): the
    # approved set is recomputed and every child's label rewritten each run. A-1 carries a
    # stale `parallel-ok` and now collides with BOTH siblings, who are disjoint from each
    # other - so {A-2, A-3} wins on size and A-1 must LOSE the label it already has.
    with TempDir() as tmp:
        kids = [child("A-1", "1.1", labels=["quick-dev", "parallel-ok"]),
                child("A-2", "1.2", labels=[]), child("A-3", "1.3", labels=[])]
        (tmp / "plan.json").write_text(json.dumps(packet(kids)), encoding="utf-8")
        (tmp / "touch.json").write_text(json.dumps(
            {"A-1": {"paths": ["backend/b.py", "backend/c.py"]},
             "A-2": {"paths": ["backend/b.py"]},
             "A-3": {"paths": ["backend/c.py"]}}), encoding="utf-8")
        run_script("label_tasks.py", "resolve", "--plan", str(tmp / "plan.json"),
                   "--touchsets", str(tmp / "touch.json"), "--out", str(tmp / "v.json"))
        res = json.loads((tmp / "v.json").read_text(encoding="utf-8"))
        code, out = run_script("label_tasks.py", "stamp", "--plan", str(tmp / "plan.json"),
                               "--verdicts", str(tmp / "v.json"))
        c.check("the larger disjoint set wins over the lexicographically-first child",
                res["approved"] == ["A-2", "A-3"], str(res["approved"]))
        c.check("dry-run stamp exits 0", code == 0, out[:160])
        c.check("a child that WAS parallel-ok and now overlaps LOSES the label",
                "A-1 -parallel-ok" in out, out[-400:])
        c.check("quick-dev survives the parallel-ok strip",
                lt.set_labels("/nonexistent", "A-1", ["quick-dev", "parallel-ok"],
                              {"parallel-ok": False}, False) == "-parallel-ok")
        c.check("the dry run says so out loud", "dry run" in out, out[-200:])

    # ── label arithmetic, directly ─────────────────────────────────────────────
    # SCC-155 moved these onto the tri-state dict signature (a label the pass did not assess
    # must be LEFT ALONE, which a bool cannot say). Same three behaviours, same assertions.
    c.check("set_labels preserves unrelated labels while adding",
            lt.set_labels("/nonexistent", "K", ["quick-dev"],
                          {"parallel-ok": True}, False) == "+parallel-ok")
    c.check("set_labels reports a strip when approval is withdrawn",
            lt.set_labels("/nonexistent", "K", ["quick-dev", "parallel-ok"],
                          {"parallel-ok": False}, False) == "-parallel-ok")
    c.check("set_labels is a no-op when the label set already matches",
            lt.set_labels("/nonexistent", "K", ["parallel-ok"],
                          {"parallel-ok": True}, False) is None)

    # ── planning-prefix filter, directly ───────────────────────────────────────
    c.check("source_paths drops planning dirs and keeps source",
            lt.source_paths({"paths": ["_artifacts/a.md", "backend/x.py", "./frontend/y.tsx"],
                             "creates": ["_bmad/z.md", "backend/new.py"]})
            == {"backend/x.py", "frontend/y.tsx", "backend/new.py"})
    c.check("docs/ is NOT treated as a planning dir (projects ship from it)",
            "docs/guide.md" in lt.source_paths({"paths": ["docs/guide.md"]}))

    # ── umbrella detection, directly ───────────────────────────────────────────
    kids = [{"key": "K-0", "story_id": "12.3"}, {"key": "K-1", "story_id": "12.3.4"},
            {"key": "K-2", "story_id": "12.3.7"}, {"key": "K-3", "story_id": "12.4"}]
    lt.mark_umbrellas(kids)
    c.check("a story id that prefixes a sibling's is an umbrella",
            kids[0]["umbrella"] and kids[0]["contains"] == ["K-1", "K-2"], str(kids[0]))
    c.check("a leaf story is not an umbrella",
            not kids[1]["umbrella"] and not kids[3]["umbrella"])
    c.check("12.4 is not swallowed by 12.3 (dot boundary, not string prefix)",
            "K-3" not in kids[0].get("contains", []), str(kids[0].get("contains")))

    # ── the BMAD-epic gate refuses, by name ────────────────────────────────────
    with TempDir() as tmp:
        (tmp / ".agents").mkdir(parents=True)
        (tmp / ".agents" / "jira.conf").write_text('JIRA_KEYS="ZZZ"\n', encoding="utf-8")
        try:
            lt.gate_bmad({"key": "ZZZ-1", "summary": "CI/CD Improvment"}, tmp)
            c.check("a repo with no stories dir is refused", False, "did not exit")
        except SystemExit as e:
            c.check("a repo with no stories dir is refused", e.code == 2, f"exit={e.code}")
        (tmp / "_bmad" / "bmm" / "stories").mkdir(parents=True)
        try:
            lt.gate_bmad({"key": "ZZZ-1", "summary": "CI/CD Improvment"}, tmp)
            c.check("a grouping epic is refused", False, "did not exit")
        except SystemExit as e:
            c.check("a grouping epic is refused", e.code == 2, f"exit={e.code}")
        c.check("a BMAD epic passes the gate",
                lt.gate_bmad({"key": "ZZZ-2", "summary": "Epic 19 - ADK Upgrade"}, tmp) == "19")

    # ── repo resolution is derived, and ambiguity is reported ──────────────────
    c.check("repo_keys parses the shell-sourced conf",
            lt.repo_keys(Path(__file__).resolve().parents[3]) == ["SCC"])
    c.check("a key for no known project refuses rather than defaulting",
            run_script("label_tasks.py", "plan", "--parent", "NOSUCH-1",
                       "--acli", "/nonexistent")[0] != 0)

    # ── acli returns bare nulls in the row array ───────────────────────────────
    # Live 2026-08-09: `--fields "key"` ALONE came back `[null, null, null]` — `key` is a
    # top-level property, not a requestable field, so nothing materialized and `check` died
    # on AttributeError. Ask for a real field too, and tolerate nulls either way.
    c.check("child_keys survives an all-null payload",
            lt.child_keys([None, None, None]) == [])
    c.check("child_keys keeps the real rows and drops the nulls",
            lt.child_keys([{"key": "A-1"}, None, {"key": "A-2"}]) == ["A-1", "A-2"])
    c.check("child_keys tolerates a non-list payload", lt.child_keys(None) == [])
    c.check("child_keys drops a dict with no key", lt.child_keys([{"fields": {}}]) == [])

    # ── story-id extraction ────────────────────────────────────────────────────
    c.check("dotted BMAD number", lt.story_id_of("12.3.4 - Checkride Frontend") == "12.3.4")
    c.check("em-dash separator", lt.story_id_of("19.1 — ADK Bump") == "19.1")
    c.check("debug- id", lt.story_id_of("debug-4.1-hr-date-fixes") == "debug-4.1-hr-date-fixes")
    c.check("a Task summary yields no story id",
            lt.story_id_of("Separate front/back end deploys") is None)
    c.check("BMAD epic number off a summary",
            lt.bmad_epic_number("Epic 19 — ADK 2.x Runtime Upgrade") == "19")
    c.check("no epic number on a grouping epic",
            lt.bmad_epic_number("CI/CD Improvment") is None)

    # ═══════════════════════════════════════════════════════════════════════════
    # TASK MODE + THE SECOND LABEL — SCC-155. Everything below was written RED.
    # ═══════════════════════════════════════════════════════════════════════════

    # ── the two gates refuse INTO each other ───────────────────────────────────
    # A wrong-mode run is the likeliest operator error once there are two commands, and a
    # refusal that does not name the other command leaves them stuck. `/cicd-parallel-check`
    # is RETIRED by this same ticket, so neither refusal may name it.
    #
    # These assert on the refusal TEXT, not just the exit code, and that is load-bearing:
    # `gate_bmad` already exits 2 on a Task parent for an unrelated reason (its summary
    # carries no `Epic N`), so an exit-code-only case passes today and proves nothing about
    # the type check or the hand-off.
    def refuses(fname: str, *a: object) -> str:
        """Call lt.<fname>(*a) and return what it printed while refusing. Missing function
        or no refusal both return a string that fails the `in` assertions below, so every
        case lands on its OWN assertion instead of an AttributeError killing the file."""
        fn = getattr(lt, fname, None)
        if fn is None:
            return f"<lt.{fname} does not exist>"
        buf = io.StringIO()
        try:
            with redirect_stdout(buf), redirect_stderr(buf):
                fn(*a)
        except SystemExit:
            return buf.getvalue() or "<refused silently>"
        return f"<{fname} did not refuse>"

    with TempDir() as tmp:
        (tmp / "_bmad" / "bmm" / "stories").mkdir(parents=True)
        msg = refuses("gate_bmad", {"key": "SCC-99", "summary": "Adding a command",
                                    "type": "Task"}, tmp)
        c.check("story mode refuses a Task parent and hands it to /smh-label-tasks",
                "/smh-label-tasks" in msg, msg.strip()[:200])
        # ⛔ The line above is NOT enough on its own, and the mutation sweep proved it:
        # deleting the type check entirely leaves it green, because this parent also has no
        # `Epic N` in its summary, so the GROUPING-epic refusal fires instead — and that one
        # names `/smh-label-tasks` too. Right answer, wrong reason. Pin the sentence only the
        # type arm can produce.
        c.check("...and it refuses for the TYPE, not for the summary's shape",
                "is a Task, not an Epic" in msg, msg.strip()[:200])

    msg = refuses("gate_task", {"key": "AVCH-13", "summary": "Epic 12 - Test",
                                "type": "Epic"})
    c.check("task mode refuses an Epic parent and hands it to /cicd-label-tasks",
            "/cicd-label-tasks" in msg, msg.strip()[:200])

    # An UNTYPED parent is the other half of that arm. The board can hand back a blank
    # issuetype, and "we could not read the type" must never be treated as "it is a Task" —
    # assessing an epic's whole child set as one flat subtask pool answers nobody's question.
    msg = refuses("gate_task", {"key": "SCC-99", "summary": "Some container"})
    c.check("task mode refuses an UNTYPED parent too - unknown is not 'a Task'",
            "untyped container" in msg, msg.strip()[:200])

    gate_task = getattr(lt, "gate_task", None)
    c.check("task mode accepts a Task parent",
            gate_task is not None
            and gate_task({"key": "SCC-99", "summary": "Adding a command",
                           "type": "Task"}) is None,
            "gate_task missing" if gate_task is None else "refused a Task")

    # ── grounding a Subtask: the plan is joined by task.yaml, never by slug ─────
    # The story side matches an `implementation_plan.md` by SLUG. Task lanes already carry a
    # `task.yaml` declaring `task_key`, which is the join the rest of this toolkit uses
    # (check_gate governs on exactly this), so the plan is found by DECLARATION.
    find_task_plan = getattr(lt, "find_task_plan", None)
    with TempDir() as tmp:
        d = tmp / "_artifacts" / "_main" / "2026-08-14_something"
        d.mkdir(parents=True)
        (d / "task.yaml").write_text("task_key: SCC-146\nbranch: chore/SCC-146-x\n",
                                     encoding="utf-8")
        (d / "implementation_plan.md").write_text("# plan\n", encoding="utf-8")
        found = find_task_plan(tmp, "SCC-146") if find_task_plan else None
        c.check("a Subtask's plan is found through its sibling task.yaml",
                found is not None and found.name == "implementation_plan.md",
                "find_task_plan missing" if not find_task_plan else str(found))
        # The substring trap this repo has already been bitten by: SCC-14 inside SCC-146.
        foreign = find_task_plan(tmp, "SCC-14") if find_task_plan else "<missing>"
        c.check("a FOREIGN task_key does not ground this key", foreign is None, str(foreign))
        (d / "implementation_plan.md").unlink()
        orphan = find_task_plan(tmp, "SCC-146") if find_task_plan else "<missing>"
        c.check("a task.yaml with no plan beside it grounds nothing", orphan is None,
                str(orphan))

    # ── the grounding LADDER itself, driven directly ───────────────────────────
    # Everything else in this file feeds `resolve` a pre-built packet, so `ground_child`'s
    # task arm was never actually executed — the fixtures hand-write the `authority` and
    # `next_command` it is supposed to compute. The mutation sweep caught that: deleting the
    # ticket rung and blanking the unlock command both survived a full green run. These call
    # it for real, in a bare temp dir, so there is no branch and no plan and the third rung
    # is the only one left.
    ground_child = getattr(lt, "ground_child", None)

    def grounded_via(desc: str) -> dict:
        if ground_child is None:
            return {"authority": "<ground_child does not exist>"}
        with TempDir() as t:
            return ground_child(t, {"key": "SCC-101", "summary": "SCC-101 - do the thing",
                                    "story_id": None, "description": desc},
                                "main", "task", "SCC-99")

    g = grounded_via("ACCEPTANCE\n- `.agents/scripts/x.py` grows the new arm")
    c.check("a Subtask with only a DESCRIPTION is grounded on the ticket rung",
            g.get("grounded") is True and g.get("authority") == "ticket", str(g.get("authority")))
    c.check("the ticket rung tells the agent ambiguity counts as an EDIT",
            any("fail toward locked" in (s.get("read") or "")
                for s in (g.get("sources") or [])), str(g.get("sources")))

    g = grounded_via("   ")
    c.check("a Subtask with a BLANK description is ungrounded, not grounded on whitespace",
            g.get("grounded") is False, str(g.get("authority")))
    c.check("ground_child names /smh-plan-task as the Task-lane unlock",
            g.get("next_command") == "/smh-plan-task SCC-99", str(g.get("next_command")))
    c.check("its reason names all three rungs, so the operator knows what to supply",
            g.get("reason") == "no lane branch, no plan, no description", str(g.get("reason")))

    # ── an ungrounded Subtask reads 'no plan' and names the planner ────────────
    with TempDir() as tmp:
        r = run_resolve(tmp, [subtask("SCC-100"), subtask("SCC-101", grounded=False)],
                        {"SCC-100": {"paths": [".agents/scripts/a.py"]}},
                        mode="task", parent="SCC-99")
        c.check("an ungrounded Subtask reads 'no-plan', not 'no-story'",
                r["_by"]["SCC-101"]["verdict"] == "no-plan", str(r["_by"]["SCC-101"]))
        c.check("the ungrounded Subtask is NEVER approved",
                "SCC-101" not in r["approved"], str(r["approved"]))
        c.check("its row prints /smh-plan-task as the unlock",
                r["_by"]["SCC-101"].get("command") == "/smh-plan-task SCC-99",
                str(r["_by"]["SCC-101"].get("command")))

    # ── the set math is the SAME engine in task mode ───────────────────────────
    with TempDir() as tmp:
        r = run_resolve(tmp, [subtask("SCC-100"), subtask("SCC-101")],
                        {"SCC-100": {"paths": [".agents/scripts/label_tasks.py"]},
                         "SCC-101": {"paths": [".agents/scripts/label_tasks.py"]}},
                        mode="task", parent="SCC-99")
        c.check("two Subtasks on one source path are not both approved",
                len(r["approved"]) == 1, str(r["approved"]))

    # ── quick-dev rides the same pass, tri-state ───────────────────────────────
    def stamp_out(tmp: Path, kids: list[dict], touch: dict, mode: str = "task",
                  parent: str = "SCC-99") -> str:
        (tmp / "p.json").write_text(json.dumps(packet(kids, parent, mode)), encoding="utf-8")
        (tmp / "t.json").write_text(json.dumps(touch), encoding="utf-8")
        run_script("label_tasks.py", "resolve", "--plan", str(tmp / "p.json"),
                   "--touchsets", str(tmp / "t.json"), "--out", str(tmp / "v.json"))
        return run_script("label_tasks.py", "stamp", "--plan", str(tmp / "p.json"),
                          "--verdicts", str(tmp / "v.json"))[1]

    with TempDir() as tmp:
        out = stamp_out(tmp, [subtask("SCC-100"), subtask("SCC-101", labels=["quick-dev"])],
                        {"SCC-100": {"paths": [".agents/a.py"],
                                     "quick_dev": {"eligible": True,
                                                   "evidence": "one file, one assertion"}},
                         "SCC-101": {"paths": [".agents/b.py"],
                                     "quick_dev": {"eligible": False,
                                                   "evidence": "needs its own breakdown"}}})
        # Pinned as the whole per-ticket segment, so the label lands on the RIGHT ticket:
        # `"+quick-dev" in out` would pass just as well if both writes hit one child.
        c.check("an eligible child GAINS quick-dev in the same pass",
                "SCC-100 +parallel-ok +quick-dev" in out, out[-400:])
        c.check("an assessed-ineligible child LOSES a stale quick-dev",
                "SCC-101 +parallel-ok -quick-dev" in out, out[-400:])

    with TempDir() as tmp:
        out = stamp_out(tmp, [subtask("SCC-100", labels=["quick-dev"]), subtask("SCC-101")],
                        {"SCC-100": {"paths": [".agents/a.py"]},
                         "SCC-101": {"paths": [".agents/b.py"]}})
        c.check("a touch-set with NO quick_dev key leaves the label untouched",
                "quick-dev" not in out, out[-400:])

    # An ungrounded child is the one place the engine decides quick-dev by ITSELF rather than
    # carrying the agent's answer: nobody can size a lane they cannot see, so it is an
    # explicit False and a stale label comes off. `None` here would look identical on a clean
    # ticket and quietly keep a wrong label on a dirty one.
    with TempDir() as tmp:
        out = stamp_out(tmp, [subtask("SCC-100"),
                              subtask("SCC-101", grounded=False, labels=["quick-dev"])],
                        {"SCC-100": {"paths": [".agents/a.py"]}})
        c.check("an UNGROUNDED child LOSES a stale quick-dev - an unseen lane is unsizable",
                "SCC-101 -quick-dev" in out, out[-400:])

    # The tri-state's other input shape: the block is present but says nothing. A dict with
    # no `eligible` key is an agent that opened the question and did not answer it, which is
    # UNASSESSED — reading it as False would strip a hand-set label on a technicality.
    quick_dev_of = getattr(lt, "quick_dev_of", None)
    c.check("a quick_dev block with no 'eligible' key is UNASSESSED, not ineligible",
            quick_dev_of is not None
            and quick_dev_of({"quick_dev": {"evidence": "looked, did not decide"}})[0] is None,
            "quick_dev_of missing" if quick_dev_of is None
            else str(quick_dev_of({"quick_dev": {"evidence": "x"}})))
    c.check("a quick_dev block that DOES answer is carried through as the answer",
            quick_dev_of is not None
            and quick_dev_of({"quick_dev": {"eligible": True, "evidence": "one file"}})
            == (True, "one file"),
            "quick_dev_of missing" if quick_dev_of is None else "wrong tuple")

    # ── the mode is DERIVED, and the override still exists ─────────────────────
    # This is what makes a wrong-mode run impossible to start rather than merely refused.
    # Both verbs that read the board call it, and neither is reachable offline, so it is
    # driven directly here — the sweep showed hard-coding it to "story" changed nothing.
    resolve_mode = getattr(lt, "resolve_mode", None)
    c.check("a Task parent derives task mode with no flag at all",
            resolve_mode is not None and resolve_mode({"type": "Task"}, None) == "task",
            "resolve_mode missing" if resolve_mode is None else "wrong mode")
    c.check("an Epic parent derives story mode",
            resolve_mode is not None and resolve_mode({"type": "Epic"}, None) == "story",
            "resolve_mode missing" if resolve_mode is None else "wrong mode")
    c.check("--mode overrides the board when the board's type is wrong",
            resolve_mode is not None and resolve_mode({"type": "Epic"}, "task") == "task",
            "resolve_mode missing" if resolve_mode is None else "override ignored")

    label_plan = getattr(lt, "label_plan", None)
    c.check("label_plan leaves an unassessed label alone",
            label_plan is not None
            and label_plan(["quick-dev", "keep-me"],
                           {"parallel-ok": True, "quick-dev": None})[0]
            == ["keep-me", "parallel-ok", "quick-dev"],
            "label_plan missing" if label_plan is None else "wrong set")
    c.check("label_plan preserves labels nobody manages",
            label_plan is not None
            and label_plan(["keep-me"], {"parallel-ok": True, "quick-dev": False})[0]
            == ["keep-me", "parallel-ok"],
            "label_plan missing" if label_plan is None else "wrong set")
    c.check("label_plan reports both actions in one pass",
            label_plan is not None
            and label_plan(["quick-dev"], {"parallel-ok": True, "quick-dev": False})[1]
            == ["+parallel-ok", "-quick-dev"],
            "label_plan missing" if label_plan is None else "wrong actions")

    # ── the stamped comment names the command that can re-run it ───────────────
    # A comment naming a retired command is the SCC-63 failure: the reader follows it and
    # finds nothing. The board keeps these comments forever, so the text must be right at
    # write time — there is no sweep that can fix a stamp already on Jira.
    with TempDir() as tmp:
        out = stamp_out(tmp, [subtask("SCC-100")],
                        {"SCC-100": {"paths": [".agents/a.py"]}})
        c.check("a task-mode stamp tells you to re-run /smh-label-tasks",
                "/smh-label-tasks SCC-99" in out, out[-300:])
        c.check("no stamp anywhere names the retired /cicd-parallel-check",
                "parallel-check" not in out, out[-300:])

    with TempDir() as tmp:
        out = stamp_out(tmp, [child("A-1", "1.1")], {"A-1": {"paths": ["backend/a.py"]}},
                        mode="story", parent="AVCH-13")
        c.check("a story-mode stamp tells you to re-run /cicd-label-tasks",
                "/cicd-label-tasks AVCH-13" in out, out[-300:])

    # ── ⛔ REVIEW FINDING (critical): the board-WRITE path, executed for real ───
    # Everything above stops at the dry run. These pass --apply through a real acli stub, so
    # the argv, the comma-join, the --key and the failure arm are on the hook.
    with TempDir() as tmp:
        launcher, state = acli_stub(tmp)
        os.environ["STUB_STATE"] = str(state)
        state.write_text(json.dumps({"labels": {"SCC-100": ["keep-me"],
                                                "SCC-101": ["keep-me", "parallel-ok"]}}),
                         encoding="utf-8")
        # SCC-101 is UNGROUNDED and carries a stale `parallel-ok`, so which child loses the
        # label is deterministic - a two-way path collision would leave the tie-break to pick
        # the loser and the assertion would flap.
        (tmp / "p.json").write_text(json.dumps(
            packet([subtask("SCC-100", labels=["keep-me"]),
                    subtask("SCC-101", grounded=False,
                            labels=["keep-me", "parallel-ok"])], "SCC-99", "task")),
            encoding="utf-8")
        (tmp / "t.json").write_text(json.dumps(
            {"SCC-100": {"paths": [".agents/a.py"],
                         "quick_dev": {"eligible": True, "evidence": "one file"}}}),
            encoding="utf-8")
        run_script("label_tasks.py", "resolve", "--plan", str(tmp / "p.json"),
                   "--touchsets", str(tmp / "t.json"), "--out", str(tmp / "v.json"))
        code, out = run_script("label_tasks.py", "stamp", "--plan", str(tmp / "p.json"),
                               "--verdicts", str(tmp / "v.json"), "--apply",
                               "--acli", str(launcher))
        wrote = json.loads(state.read_text(encoding="utf-8")).get("labels", {})
        c.check("--apply actually WRITES the computed set to the board",
                "parallel-ok" in wrote.get("SCC-100", []), f"exit={code} {wrote}")
        c.check("the write PRESERVES labels this engine does not manage",
                "keep-me" in wrote.get("SCC-100", []), str(wrote))
        c.check("the write carries quick-dev through to the board, not just to stdout",
                "quick-dev" in wrote.get("SCC-100", []), str(wrote))
        c.check("and the STRIP reaches the board too - not merely the printed report",
                "parallel-ok" not in wrote.get("SCC-101", []), str(wrote))
        c.check("the stamped verdict comment is POSTED, not just rendered",
                any("Parallel check" in b
                    for b in json.loads(state.read_text(encoding="utf-8")).get("comments", [])),
                str(json.loads(state.read_text(encoding="utf-8")).get("comments"))[:200])

    # A board that REJECTS the label write must not be reported as a successful stamp.
    with TempDir() as tmp:
        launcher, state = acli_stub(tmp)
        os.environ["STUB_STATE"] = str(state)
        state.write_text(json.dumps({"label_fail": True, "labels": {}}), encoding="utf-8")
        (tmp / "p.json").write_text(json.dumps(packet([subtask("SCC-100")], "SCC-99", "task")),
                                    encoding="utf-8")
        (tmp / "t.json").write_text(json.dumps({"SCC-100": {"paths": [".agents/a.py"]}}),
                                    encoding="utf-8")
        run_script("label_tasks.py", "resolve", "--plan", str(tmp / "p.json"),
                   "--touchsets", str(tmp / "t.json"), "--out", str(tmp / "v.json"))
        code, out = run_script("label_tasks.py", "stamp", "--plan", str(tmp / "p.json"),
                               "--verdicts", str(tmp / "v.json"), "--apply",
                               "--acli", str(launcher))
        c.check("a REJECTED label write is reported, never silently counted as stamped",
                "failed" in out.lower() or "could not" in out.lower(), out[-300:])
        os.environ.pop("STUB_STATE", None)

    # A comment the board REFUSED must not be reported as posted. Same fail-open class the
    # review found in `jira_feed.finish`, in the sibling writer.
    with TempDir() as tmp:
        launcher, state = acli_stub(tmp)
        os.environ["STUB_STATE"] = str(state)
        state.write_text(json.dumps({"comment_fail": True, "labels": {}}), encoding="utf-8")
        (tmp / "p.json").write_text(json.dumps(packet([subtask("SCC-100")], "SCC-99", "task")),
                                    encoding="utf-8")
        (tmp / "t.json").write_text(json.dumps({"SCC-100": {"paths": [".agents/a.py"]}}),
                                    encoding="utf-8")
        run_script("label_tasks.py", "resolve", "--plan", str(tmp / "p.json"),
                   "--touchsets", str(tmp / "t.json"), "--out", str(tmp / "v.json"))
        code, out = run_script("label_tasks.py", "stamp", "--plan", str(tmp / "p.json"),
                               "--verdicts", str(tmp / "v.json"), "--apply",
                               "--acli", str(launcher))
        c.check("a comment the board REFUSED is never reported as posted",
                "FAILED" in out or "failed" in out.lower(), out[-300:])
        os.environ.pop("STUB_STATE", None)

    # ── ⛔ REVIEW FINDING: --mode story is inert on `plan` ──────────────────────
    # resolve_mode's docstring says the flag exists for "the case the type is wrong on the
    # board" - but gate_bmad then refuses on that very type, so the ONE input the flag was
    # added for is the one it cannot serve. An operator told to use it lands back on the
    # command they came from.
    with TempDir() as tmp:
        launcher, state = acli_stub(tmp)
        os.environ["STUB_STATE"] = str(state)
        (tmp / "_bmad" / "bmm" / "stories").mkdir(parents=True)
        (tmp / "_bmad-output" / "planning-artifacts").mkdir(parents=True)
        (tmp / "_bmad-output" / "planning-artifacts" / "epics.md").write_text(
            "# Epic 12 - Test\n", encoding="utf-8")
        state.write_text(json.dumps({"types": {"AVCH-13": "Task"},
                                     "summaries": {"AVCH-13": "Epic 12 - Test"},
                                     "rows": []}), encoding="utf-8")
        code, out = run_script("label_tasks.py", "plan", "--parent", "AVCH-13",
                               "--mode", "story", "--repo", str(tmp),
                               "--acli", str(launcher), "--out", str(tmp / "o.json"))
        c.check("--mode story OVERRIDES a board that mistyped a BMAD epic as a Task",
                "not an Epic" not in out, out.strip()[:220])
        os.environ.pop("STUB_STATE", None)

    # ── ⛔ REVIEW FINDING: gate_bmad hands a Subtask to a command that cannot serve it ──
    # gate_bmad refuses a Subtask parent with "a Subtask and its Subtasks are Task work - run
    # /smh-label-tasks". gate_task then ACCEPTS it, the child search returns nothing, and the
    # operator dies on "no children". hierarchyLevel -1 is the floor: nothing nests under a
    # Subtask, so task mode must refuse it by name and point at the parent Task.
    msg = refuses("gate_task", {"key": "SCC-160", "summary": "do the thing",
                                "type": "Subtask"})
    c.check("task mode refuses a SUBTASK parent - nothing nests under a Subtask",
            "Subtask" in msg and "parent" in msg.lower(), msg.strip()[:220])

    # ── ⛔ REVIEW FINDINGS #15/#16: the grounding pair, fixed together ─────────
    # They are ONE defect with two halves and neither can be fixed alone:
    #   #16  `story_branch` matches on the ticket KEY, so rung 1 fires for every lane
    #        /smh-plan-task cuts. Such a branch carries only `_artifacts/…`, which
    #        `source_paths` strips to NOTHING - so `authority` reads `branch-diff` over an
    #        empty set, an empty touch-set is disjoint from everything, and every planned
    #        lane comes back 🟢. A manufactured green on the command's own happy path.
    #   #15  rung 2 can't cover for it: `find_task_plan` scans the CURRENT checkout's
    #        `_artifacts/`, but the plan was committed to that LANE's branch and never
    #        merged. So the rung the planner calls "not optional" never fires.
    # Fix #16 alone and every planned lane is ungrounded; fix #15 alone and rung 1 still
    # wins with its empty set. Hence one block, one commit.
    def git_repo(tmp: Path) -> Path:
        import subprocess

        def g(*a: str) -> None:
            subprocess.run(["git", "-C", str(tmp), *a], capture_output=True, check=False)
        g("init", "-q", "-b", "main")
        g("config", "user.email", "t@t"); g("config", "user.name", "t")
        (tmp / "seed.txt").write_text("x\n", encoding="utf-8")
        g("add", "seed.txt"); g("commit", "-qm", "seed")
        return tmp

    def plan_lane(tmp: Path, key: str, extra: str | None = None) -> None:
        """A lane exactly as /smh-plan-task leaves it: plan + task.yaml committed to the
        lane's OWN branch, nothing merged to main."""
        import subprocess

        def g(*a: str) -> None:
            subprocess.run(["git", "-C", str(tmp), *a], capture_output=True, check=False)
        g("checkout", "-q", "-b", f"chore/{key}-thing")
        d = tmp / "_artifacts" / "_main" / f"2026-01-01_{key.lower()}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "task.yaml").write_text(f"task_key: {key}\n", encoding="utf-8")
        (d / "implementation_plan.md").write_text("# plan\n", encoding="utf-8")
        g("add", "-A"); g("commit", "-qm", f"{key} plan")
        if extra:
            (tmp / extra).parent.mkdir(parents=True, exist_ok=True)
            (tmp / extra).write_text("code\n", encoding="utf-8")
            g("add", "-A"); g("commit", "-qm", f"{key} code")
        g("checkout", "-q", "main")

    with TempDir() as tmp:
        repo = git_repo(tmp)
        plan_lane(repo, "SCC-101")                       # plan only - no code yet
        plan_lane(repo, "SCC-102", extra=".agents/x.py")  # plan AND real code
        gc = getattr(lt, "ground_child", None)

        g1 = gc(repo, {"key": "SCC-101", "summary": "s", "story_id": None, "description": ""},
                "main", "task", "SCC-99") if gc else {}
        c.check("#16 a PLANNING-ONLY lane branch does not ground as branch-diff",
                g1.get("authority") != "branch-diff", str(g1.get("authority")))
        c.check("#15 it grounds on the PLAN committed to that lane's own branch",
                g1.get("authority") == "plan", str(g1.get("authority")))
        c.check("#15 and the plan source names the branch it was read from",
                any("SCC-101" in str(s.get("path", "")) or "SCC-101" in str(s.get("ref", ""))
                    for s in (g1.get("sources") or [])), str(g1.get("sources")))

        g2 = gc(repo, {"key": "SCC-102", "summary": "s", "story_id": None, "description": ""},
                "main", "task", "SCC-99") if gc else {}
        c.check("a lane with REAL code still grounds on branch-diff - rung 1 keeps priority",
                g2.get("authority") == "branch-diff", str(g2.get("authority")))

        # The branch reader owes the same two guards the checkout reader already has: an
        # EXACT key match (the SCC-14 ⊂ SCC-146 trap), and a manifest with no plan beside it
        # grounds nothing. Both survived the sweep as unpinned width.
        fp = getattr(lt, "find_task_plan_on_branch", None)
        c.check("#15 a FOREIGN task_key on the branch does not ground this key",
                fp is not None
                and fp(repo, "SCC-10", "chore/SCC-101-thing") is None,
                "missing" if fp is None else str(fp(repo, "SCC-10", "chore/SCC-101-thing")))
        import subprocess as _sp
        _sp.run(["git", "-C", str(repo), "checkout", "-q", "chore/SCC-101-thing"],
                capture_output=True)
        _sp.run(["git", "-C", str(repo), "rm", "-q",
                 "_artifacts/_main/2026-01-01_scc-101/implementation_plan.md"],
                capture_output=True)
        _sp.run(["git", "-C", str(repo), "commit", "-qm", "drop the plan"], capture_output=True)
        _sp.run(["git", "-C", str(repo), "checkout", "-q", "main"], capture_output=True)
        c.check("#15 a branch task.yaml with NO plan beside it grounds nothing",
                fp is not None and fp(repo, "SCC-101", "chore/SCC-101-thing") is None,
                "missing" if fp is None else str(fp(repo, "SCC-101", "chore/SCC-101-thing")))
        c.check("and its branch-diff carries the source path, not just the plan",
                any(".agents/x.py" in (s.get("paths") or [])
                    for s in (g2.get("sources") or [])), str(g2.get("sources")))

    # ── ⛔ REVIEW FINDING #19: umbrellas are a BMAD concept ────────────────────
    # `mark_umbrellas` keys off story_id_of(summary) and ran in BOTH modes. A Subtask
    # summarised "2.1 Add the gate" beside "2.1.1 …" became an umbrella: no verdict row and
    # NO LABEL WRITE AT ALL. Silent exclusion from a labelling pass is the exact failure this
    # engine exists to prevent.
    def umbrellas_for(mode: str, summaries: list[tuple[str, str]]) -> list[bool] | str:
        """A TypeError from a not-yet-widened signature must not abort the FILE - the same
        `refuses()` discipline, applied to a call rather than a refusal."""
        fn = getattr(lt, "mark_umbrellas", None)
        if fn is None:
            return "<mark_umbrellas does not exist>"
        kids = [{"key": k, "summary": s, "umbrella": False, "story_id": lt.story_id_of(s)}
                for k, s in summaries]
        try:
            fn(kids, mode=mode)
        except TypeError:
            return "<mark_umbrellas takes no mode>"
        return [bool(k.get("umbrella")) for k in kids]

    # ⛔ The two calls differ ONLY in `mode`. A first draft gave task mode summaries like
    # "2.1 the parent-looking one", which `story_id_of` parses to None - so no umbrella was
    # detected in either mode and the case passed with the guard deleted. The sweep caught
    # it. Same summaries, one variable.
    UMB = [("SCC-100", "2.1 - the parent-looking one"),
           ("SCC-101", "2.1.1 - the child-looking one")]
    c.check("#19 task mode has no umbrellas - a dotted Subtask summary is not a BMAD tree",
            umbrellas_for("task", UMB) == [False, False], str(umbrellas_for("task", UMB)))
    c.check("#19 story mode still detects them - the gate is on MODE, not on the logic",
            umbrellas_for("story", UMB) == [True, False], str(umbrellas_for("story", UMB)))

    # ── ⛔ REVIEW FINDING #20: `check` must keep its published 0/1 contract ────
    # Both command docs promise "[FRESH] (exit 0) or [STALE] (exit 1)". SCC-155 added a
    # `parent_facts()` round-trip to `check` purely to pick one word in one message - and
    # `parent_facts` calls `wf.die(..., 2)`. A read-only staleness verb on a dropped uplink
    # (a recorded condition here) now exits 2, a code neither doc lists, before reading a
    # single comment. The word is cosmetic; the hard board dependency is not.
    with TempDir() as tmp:
        launcher, state = acli_stub(tmp)
        os.environ["STUB_STATE"] = str(state)
        state.write_text(json.dumps({"view_fail": True}), encoding="utf-8")
        code, out = run_script("label_tasks.py", "check", "--parent", "SCC-99",
                               "--acli", str(launcher))
        c.check("#20 an unreadable parent still yields the STALE contract, never exit 2",
                code in (0, 1), f"exit={code} {out.strip()[:200]}")
        os.environ.pop("STUB_STATE", None)

    # ── ⛔ REVIEW FINDING #23: cmd_plan's mode wiring, at the entrypoint ───────
    # resolve_mode is unit-tested but its CALL SITE was not, so hard-coding `mode = "story"`
    # inside cmd_plan survived a full green run - task mode could have been dead at its only
    # door. This is also the case that kills the last live mutant (NF13, the console label).
    with TempDir() as tmp:
        launcher, state = acli_stub(tmp)
        os.environ["STUB_STATE"] = str(state)
        # ⛔ The repo needs an `epic/SCC-99-*` branch or the base assertion is vacuous:
        # with none present `epic_base_ref` falls back to "main", so hard-coding the
        # story-mode branch produced "main" anyway and the mutant survived.
        import subprocess as _sp
        _sp.run(["git", "-C", str(tmp), "init", "-q", "-b", "main"], capture_output=True)
        for cfg in (("user.email", "t@t"), ("user.name", "t")):
            _sp.run(["git", "-C", str(tmp), "config", *cfg], capture_output=True)
        (tmp / "seed.txt").write_text("x\n", encoding="utf-8")
        _sp.run(["git", "-C", str(tmp), "add", "seed.txt"], capture_output=True)
        _sp.run(["git", "-C", str(tmp), "commit", "-qm", "seed"], capture_output=True)
        _sp.run(["git", "-C", str(tmp), "branch", "epic/SCC-99-labeller"], capture_output=True)
        state.write_text(json.dumps({
            "types": {"SCC-99": "Task"}, "summaries": {"SCC-99": "Add the labeller"},
            "rows": [{"key": "SCC-101",
                      "fields": {"summary": "SCC-101 - do the thing",
                                 "status": {"name": "To Do",
                                            "statusCategory": {"key": "new"}},
                                 "labels": [], "description": None}}]}), encoding="utf-8")
        code, out = run_script("label_tasks.py", "plan", "--parent", "SCC-99",
                               "--repo", str(tmp), "--acli", str(launcher),
                               "--out", str(tmp / "o.json"))
        packet_out = json.loads((tmp / "o.json").read_text(encoding="utf-8")) \
            if (tmp / "o.json").is_file() else {}
        c.check("#23 cmd_plan DERIVES task mode from the parent's type",
                packet_out.get("mode") == "task", f"exit={code} {out.strip()[:200]}")
        c.check("#23 and a Task lane's base is main, never an epic branch",
                packet_out.get("base") == "main", str(packet_out.get("base")))
        c.check("#23 the console names the verdict the BOARD will name - no [NO-STORY]",
                "NO-STORY" not in out.upper(), out.strip()[-220:])
        os.environ.pop("STUB_STATE", None)

    # ── ⛔ REVIEW FINDING: the console says [NO-STORY] in a mode with no stories ─
    with TempDir() as tmp:
        out = stamp_out(tmp, [subtask("SCC-100"), subtask("SCC-101", grounded=False)],
                        {"SCC-100": {"paths": [".agents/a.py"]}})
        c.check("a task-mode run never prints the word STORY at an ungrounded child",
                "NO-STORY" not in out.upper(), out[-300:])

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
