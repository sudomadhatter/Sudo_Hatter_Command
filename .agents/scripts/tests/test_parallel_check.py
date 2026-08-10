"""parallel_check.py — the set math, the gates, and the staleness detector. (SCC-56)

Offline by construction: every case here drives `resolve` and `stamp` (dry run) through
temp files, so nothing reaches `acli` or the network. The two board-reading verbs (`plan`,
`check`) are exercised for their REFUSALS, which is where their damage would be.

Stdlib only and no pytest, matching the scripts under test.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases, TempDir, run_script  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import parallel_check as pc  # noqa: E402


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


def packet(children: list[dict], parent: str = "AVCH-13") -> dict:
    return {"parent": parent, "parent_summary": "Epic 12 - Test", "epic": "12",
            "repo": "/tmp/repo", "base": "main", "children": children,
            "child_keys": sorted(c["key"] for c in children)}


def run_resolve(tmp: Path, children: list[dict], touch: dict) -> dict:
    (tmp / "plan.json").write_text(json.dumps(packet(children)), encoding="utf-8")
    (tmp / "touch.json").write_text(json.dumps(touch), encoding="utf-8")
    code, out = run_script("parallel_check.py", "resolve",
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
    c = Cases("parallel_check")

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
        run_script("parallel_check.py", "resolve", "--plan", str(tmp / "plan.json"),
                   "--touchsets", str(tmp / "touch.json"), "--out", str(tmp / "v.json"))
        res = json.loads((tmp / "v.json").read_text(encoding="utf-8"))
        code, out = run_script("parallel_check.py", "stamp", "--plan", str(tmp / "plan.json"),
                               "--verdicts", str(tmp / "v.json"))
        c.check("the larger disjoint set wins over the lexicographically-first child",
                res["approved"] == ["A-2", "A-3"], str(res["approved"]))
        c.check("dry-run stamp exits 0", code == 0, out[:160])
        c.check("a child that WAS parallel-ok and now overlaps LOSES the label",
                "A-1 -parallel-ok" in out, out[-400:])
        c.check("quick-dev survives the parallel-ok strip",
                pc.set_labels("/nonexistent", "A-1", ["quick-dev", "parallel-ok"],
                              False, False) == "-parallel-ok")
        c.check("the dry run says so out loud", "dry run" in out, out[-200:])

    # ── label arithmetic, directly ─────────────────────────────────────────────
    c.check("set_labels preserves unrelated labels while adding",
            pc.set_labels("/nonexistent", "K", ["quick-dev"], True, False) == "+parallel-ok")
    c.check("set_labels reports a strip when approval is withdrawn",
            pc.set_labels("/nonexistent", "K", ["quick-dev", "parallel-ok"], False, False)
            == "-parallel-ok")
    c.check("set_labels is a no-op when the label set already matches",
            pc.set_labels("/nonexistent", "K", ["parallel-ok"], True, False) is None)

    # ── planning-prefix filter, directly ───────────────────────────────────────
    c.check("source_paths drops planning dirs and keeps source",
            pc.source_paths({"paths": ["_artifacts/a.md", "backend/x.py", "./frontend/y.tsx"],
                             "creates": ["_bmad/z.md", "backend/new.py"]})
            == {"backend/x.py", "frontend/y.tsx", "backend/new.py"})
    c.check("docs/ is NOT treated as a planning dir (projects ship from it)",
            "docs/guide.md" in pc.source_paths({"paths": ["docs/guide.md"]}))

    # ── umbrella detection, directly ───────────────────────────────────────────
    kids = [{"key": "K-0", "story_id": "12.3"}, {"key": "K-1", "story_id": "12.3.4"},
            {"key": "K-2", "story_id": "12.3.7"}, {"key": "K-3", "story_id": "12.4"}]
    pc.mark_umbrellas(kids)
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
            pc.gate_bmad({"key": "ZZZ-1", "summary": "CI/CD Improvment"}, tmp)
            c.check("a repo with no stories dir is refused", False, "did not exit")
        except SystemExit as e:
            c.check("a repo with no stories dir is refused", e.code == 2, f"exit={e.code}")
        (tmp / "_bmad" / "bmm" / "stories").mkdir(parents=True)
        try:
            pc.gate_bmad({"key": "ZZZ-1", "summary": "CI/CD Improvment"}, tmp)
            c.check("a grouping epic is refused", False, "did not exit")
        except SystemExit as e:
            c.check("a grouping epic is refused", e.code == 2, f"exit={e.code}")
        c.check("a BMAD epic passes the gate",
                pc.gate_bmad({"key": "ZZZ-2", "summary": "Epic 19 - ADK Upgrade"}, tmp) == "19")

    # ── repo resolution is derived, and ambiguity is reported ──────────────────
    c.check("repo_keys parses the shell-sourced conf",
            pc.repo_keys(Path(__file__).resolve().parents[3]) == ["SCC"])
    c.check("a key for no known project refuses rather than defaulting",
            run_script("parallel_check.py", "plan", "--parent", "NOSUCH-1",
                       "--acli", "/nonexistent")[0] != 0)

    # ── acli returns bare nulls in the row array ───────────────────────────────
    # Live 2026-08-09: `--fields "key"` ALONE came back `[null, null, null]` — `key` is a
    # top-level property, not a requestable field, so nothing materialized and `check` died
    # on AttributeError. Ask for a real field too, and tolerate nulls either way.
    c.check("child_keys survives an all-null payload",
            pc.child_keys([None, None, None]) == [])
    c.check("child_keys keeps the real rows and drops the nulls",
            pc.child_keys([{"key": "A-1"}, None, {"key": "A-2"}]) == ["A-1", "A-2"])
    c.check("child_keys tolerates a non-list payload", pc.child_keys(None) == [])
    c.check("child_keys drops a dict with no key", pc.child_keys([{"fields": {}}]) == [])

    # ── story-id extraction ────────────────────────────────────────────────────
    c.check("dotted BMAD number", pc.story_id_of("12.3.4 - Checkride Frontend") == "12.3.4")
    c.check("em-dash separator", pc.story_id_of("19.1 — ADK Bump") == "19.1")
    c.check("debug- id", pc.story_id_of("debug-4.1-hr-date-fixes") == "debug-4.1-hr-date-fixes")
    c.check("a Task summary yields no story id",
            pc.story_id_of("Separate front/back end deploys") is None)
    c.check("BMAD epic number off a summary",
            pc.bmad_epic_number("Epic 19 — ADK 2.x Runtime Upgrade") == "19")
    c.check("no epic number on a grouping epic",
            pc.bmad_epic_number("CI/CD Improvment") is None)

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
