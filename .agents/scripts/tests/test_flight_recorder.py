"""flight_recorder.py — the close-out flight recorder must be deterministic, idempotent and honest.

Three blocks map to the SCC-133 acceptance items:
  A1  `record`     one event file per close-out, keyed on the walkthrough's VERDICT sha (never
                   HEAD — HEAD moves the moment the event itself is committed), changes read
                   three-dot from the base so an absorbed `main` never pollutes them; a replay
                   writes nothing; a missing walkthrough / missing Verdict refuses with nothing
                   written.
  A2  `candidates` the ladder counts DISTINCT tasks per fingerprint (1 evidence, 2 candidate,
                   >=3 action-required); an event with no fingerprints yields no rung; --json parses.
  A3  `surface`    prints nothing and exits 0 on an empty ledger (a boot surface is not a gate),
                   one PROPOSAL line per action-required rung otherwise, and the real
                   SessionStart hook run against a seeded temp repo emits that line.

The positive control in A3 is what keeps the empty-ledger case from being a vacuous green.
Needs a real commit graph, so it builds a throwaway git repo.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir, run_script

HOOK = SCRIPTS.parent / "hooks" / "session-start-context.sh"
EVENTS_REL = Path("_artifacts/_main/workflow-events")


def git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout.strip()


def commit(repo: Path, msg: str, **files: str) -> str:
    for rel, body in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
        git(repo, "add", rel)
    git(repo, "commit", "-qm", msg)
    return git(repo, "rev-parse", "HEAD")


def build(root: Path) -> Path:
    repo = root / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@t.t")
    git(repo, "config", "user.name", "t")
    git(repo, "config", "commit.gpgsign", "false")
    commit(repo, "seed", **{".agents/rules/r.md": "# rule\n", "docs/x.md": "x\n"})
    return repo


def receipt(result: str, sha: str, gate: str) -> str:
    return json.dumps({"gate": gate, "result": result, "exit_code": 0 if result == "pass" else 1,
                       "sha": sha, "dirty_tree": False, "command": ["x"]})


def events(repo: Path) -> list[Path]:
    return sorted((repo / EVENTS_REL).rglob("*.json")) if (repo / EVENTS_REL).exists() else []


def seed_event(repo: Path, task: str, sha7: str, fps: list[str], month: str = "2026-08") -> None:
    d = repo / EVENTS_REL / month
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{task}_{sha7}.json").write_text(json.dumps({
        "v": 1, "task": task, "sha": sha7 * 5 + "ab", "tip": sha7 * 5 + "ab",
        "trigger": "close-out", "when": f"{month}-01T00:00:00+00:00", "changes": [],
        "evidence": {}, "expected": {"verdict": "PASS"}, "outcome": {"verdict": "PASS"},
        "decisions": [], "pitfalls": [], "followons": [], "fingerprints": fps,
    }), encoding="utf-8")


def main() -> int:
    c = Cases("flight_recorder")

    # ── A1 · record ───────────────────────────────────────────────────────────────
    if c.block("A1 · record: one file, verdict-sha keyed, idempotent"):
        with TempDir() as tmp:
            repo = build(tmp)
            git(repo, "checkout", "-qb", "chore/SCC-901-lane")
            l1 = commit(repo, "SCC-901 code",
                        **{".agents/rules/r.md": "# rule v2\n", ".agents/scripts/new.py": "x=1\n"})
            root = "_artifacts/_main/2026-08-15_lane"
            wt = (f"# W\n\n## Evidence\n\nVerdict: PASS @ {l1[:7]}\n\n"
                  f"## Pitfalls\n\n- `gate_receipt.py` refused a DIRTY tree; also see /smh-code-review\n"
                  f"## Decisions\n\n- keyed on the verdict sha\n")
            l2 = commit(repo, "SCC-901 artifacts", **{
                f"{root}/walkthrough.md": wt,
                f"{root}/gates/suite.json": receipt("pass", l1, "suite"),
                f"{root}/gates/lint.json": receipt("fail", l1, "lint"),
            })
            # main moves on AFTER the lane branched: two-dot diffs would now show main's
            # file as a deletion; three-dot from the merge-base must not.
            git(repo, "checkout", "-q", "main")
            commit(repo, "main moves", **{"docs/m.md": "m\n"})
            git(repo, "checkout", "-q", "chore/SCC-901-lane")

            def rec(*extra: str) -> tuple[int, str]:
                return run_script("flight_recorder.py", "record", "--task", "SCC-901",
                                  "--root", root, "--repo", str(repo), *extra)

            code, out = rec()                                     # dry run
            c.check("A1 dry-run writes nothing, exits 0", code == 0 and not events(repo), out[-300:])
            code, out = rec("--apply")
            ev = events(repo)
            c.check("A1 record --apply writes exactly one event file", code == 0 and len(ev) == 1,
                    f"exit={code} files={[p.name for p in ev]} {out[-200:]}")
            data = json.loads(ev[0].read_text(encoding="utf-8")) if ev else {}
            need = {"v", "task", "sha", "tip", "trigger", "when", "changes", "evidence", "expected",
                    "outcome", "decisions", "pitfalls", "followons", "fingerprints"}
            c.check("A1 event carries every schema key", need <= set(data), str(sorted(need - set(data))))
            c.check("A1 file name = <KEY>_<verdict sha7>.json", ev and ev[0].name == f"SCC-901_{l1[:7]}.json",
                    ev[0].name if ev else "-")
            c.check("A1 sha is the VERDICT sha, tip is HEAD",
                    data.get("sha") == l1 and data.get("tip") == l2,
                    f"sha={str(data.get('sha'))[:7]} tip={str(data.get('tip'))[:7]} l1={l1[:7]} l2={l2[:7]}")
            c.check("A1 when = the sha's own commit date (ISO, not wall clock)",
                    str(data.get("when", "")).startswith(git(repo, "show", "-s", "--format=%cI", l1)[:10]),
                    str(data.get("when")))
            c.check("A1 changes = the lane's own files, three-dot (main's later file absent)",
                    set(data.get("changes", [])) == {".agents/rules/r.md", ".agents/scripts/new.py"},
                    str(data.get("changes")))
            fps = set(data.get("fingerprints", []))
            c.check("A1 fingerprint rule-edited for the rules file", "rule-edited:.agents/rules/r.md" in fps, str(fps))
            c.check("A1 fingerprint gate-red only for the failing receipt",
                    "gate-red:lint" in fps and "gate-red:suite" not in fps, str(fps))
            c.check("A1 fingerprint mention: script + command named in a pitfall",
                    {"mention:gate_receipt.py", "mention:/smh-code-review"} <= fps, str(fps))
            c.check("A1 no verdict fingerprint for a PASS", not any(f.startswith("verdict:") for f in fps), str(fps))
            c.check("A1 outcome/expected/evidence filled",
                    data.get("outcome", {}).get("verdict") == "PASS"
                    and data.get("expected", {}).get("verdict") == "PASS"
                    and data.get("evidence", {}).get("gates", {}).get("lint", "").startswith("fail@")
                    and data.get("evidence", {}).get("walkthrough", "").endswith("walkthrough.md"),
                    json.dumps(data.get("evidence"))[:200])
            c.check("A1 pitfalls + decisions scraped like the Dev Record",
                    len(data.get("pitfalls", [])) == 1 and len(data.get("decisions", [])) == 1,
                    f"{data.get('pitfalls')} {data.get('decisions')}")

            code, out = rec("--apply")                            # replay
            c.check("A1 replay writes nothing and says so",
                    code == 0 and len(events(repo)) == 1 and "already recorded" in out, out[-200:])
            # replay AFTER an artifacts-only commit moved HEAD — verdict sha unchanged, so still no write
            commit(repo, "SCC-901 more artifacts", **{f"{root}/note.md": "n\n"})
            code, out = rec("--apply")
            c.check("A1 replay after HEAD moved (artifacts commit) still writes nothing",
                    code == 0 and len(events(repo)) == 1, f"exit={code} n={len(events(repo))}")

            # negatives
            code, out = run_script("flight_recorder.py", "record", "--task", "SCC-902",
                                   "--root", "_artifacts/_main/nope", "--repo", str(repo), "--apply")
            c.check("A1 NEG no walkthrough -> exit 2, nothing written",
                    code == 2 and len(events(repo)) == 1, f"exit={code} {out[-160:]}")
            nov = "_artifacts/_main/2026-08-15_noverdict"
            (repo / nov).mkdir(parents=True)
            (repo / nov / "walkthrough.md").write_text("# W\n\nno verdict here\n", encoding="utf-8")
            code, out = run_script("flight_recorder.py", "record", "--task", "SCC-903",
                                   "--root", nov, "--repo", str(repo), "--apply")
            c.check("A1 NEG walkthrough without a Verdict line -> exit 2, nothing written",
                    code == 2 and len(events(repo)) == 1, f"exit={code} {out[-160:]}")

    # ── A2 · candidates ───────────────────────────────────────────────────────────
    if c.block("A2 · candidates: distinct-task ladder"):
        with TempDir() as tmp:
            repo = build(tmp)
            seed_event(repo, "SCC-1", "aaaaaaa", ["rule-edited:.agents/rules/X.md", "gate-red:suite", "mention:foo.py"])
            seed_event(repo, "SCC-2", "bbbbbbb", ["rule-edited:.agents/rules/X.md", "gate-red:suite"])
            seed_event(repo, "SCC-2", "ccccccc", ["gate-red:suite"])          # same task again
            seed_event(repo, "SCC-3", "ddddddd", ["rule-edited:.agents/rules/X.md"])
            seed_event(repo, "SCC-4", "eeeeeee", [])                          # negative control
            code, out = run_script("flight_recorder.py", "candidates", "--repo", str(repo), "--json")
            try:
                ladder = {r["fingerprint"]: r for r in json.loads(out)}
            except Exception:
                ladder = {}
            c.check("A2 --json parses to rows keyed by fingerprint", code == 0 and bool(ladder), out[-200:])
            x = ladder.get("rule-edited:.agents/rules/X.md", {})
            c.check("A2 3 distinct tasks -> action-required with 3 tasks + 3 shas",
                    x.get("rung") == "action-required" and sorted(x.get("tasks", [])) == ["SCC-1", "SCC-2", "SCC-3"]
                    and len(x.get("shas", [])) == 3, json.dumps(x)[:200])
            c.check("A2 action-required carries the commission-the-script proposal",
                    "commission the script" in x.get("proposal", ""), x.get("proposal", "-"))
            g = ladder.get("gate-red:suite", {})
            c.check("A2 same task twice counts ONCE: 2 distinct -> candidate (not action-required)",
                    g.get("rung") == "candidate" and g.get("count") == 2, json.dumps(g)[:200])
            c.check("A2 candidate rung carries no commission proposal",
                    "commission the script" not in g.get("proposal", ""), g.get("proposal", "-"))
            m = ladder.get("mention:foo.py", {})
            c.check("A2 1 task -> evidence", m.get("rung") == "evidence" and m.get("count") == 1, json.dumps(m)[:120])
            c.check("A2 NEG event with no fingerprints yields no rung",
                    not any("SCC-4" in r.get("tasks", []) for r in ladder.values()), str(list(ladder)))
            code, out = run_script("flight_recorder.py", "candidates", "--repo", str(repo))
            c.check("A2 human view lists every rung", code == 0 and all(k in out for k in ladder), out[-200:])

    # ── A3 · surface + the SessionStart hook ──────────────────────────────────────
    if c.block("A3 · surface: empty is silent, seeded proposes, hook emits"):
        with TempDir() as tmp:
            repo = build(tmp)
            code, out = run_script("flight_recorder.py", "surface", "--repo", str(repo))
            c.check("A3 empty ledger -> no output, exit 0", code == 0 and out.strip() == "", out[-120:])
            (repo / EVENTS_REL / "2026-08").mkdir(parents=True)
            (repo / EVENTS_REL / "2026-08" / "garbage.json").write_text("{not json", encoding="utf-8")
            code, out = run_script("flight_recorder.py", "surface", "--repo", str(repo))
            c.check("A3 malformed event file never breaks a boot surface (exit 0)", code == 0, out[-160:])
            for i, t in enumerate(("SCC-11", "SCC-12", "SCC-13")):
                seed_event(repo, t, f"{i}{i}{i}{i}{i}{i}{i}", ["gate-red:suite"])
            seed_event(repo, "SCC-14", "9999999", ["mention:only-once.py"])
            code, out = run_script("flight_recorder.py", "surface", "--repo", str(repo))
            lines = [ln for ln in out.splitlines() if ln.strip() and not ln.startswith("[warn]")]  # run_script merges stderr
            c.check("A3 seeded -> exactly one PROPOSAL line for the action-required rung",
                    code == 0 and len(lines) == 1 and "gate-red:suite" in lines[0]
                    and "proposal" in lines[0].lower() and "only-once" not in out, out[-240:])
            c.check("A3 proposal line names the evidence (tasks)",
                    all(t in out for t in ("SCC-11", "SCC-12", "SCC-13")), out[-240:])
            # the REAL hook, pointed at the seeded repo
            env = dict(os.environ, CLAUDE_PROJECT_DIR=str(repo))
            r = subprocess.run(["sh", str(HOOK)], capture_output=True, text=True, env=env, cwd=str(repo))
            c.check("A3 SessionStart hook emits the proposal line and exits 0",
                    r.returncode == 0 and "gate-red:suite" in r.stdout, (r.stdout + r.stderr)[-300:])
            c.check("A3 hook still prints its standing gate text (nothing lost)",
                    "MAIN IS GATED" in r.stdout, "")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
