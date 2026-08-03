"""story_status.py must make the dual-surface drift class unreachable.

Story status lives on two surfaces (story frontmatter + board key) that nothing keeps in
agreement; it drifted again on 21.8b. The cases that matter are the REFUSALS — especially
C and J, where a half-written flip would leave the tree in a worse state than not writing
at all.

Runs against a throwaway fixture: the real tree's drifts are historic data, not fixtures.
"""
from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

from _harness import Cases, TempDir, run_script

BOARD = """# sprint-status.yaml (fixture)
last_updated: 2026-08-03

development_status:
  epic-21: in-progress
  21-8b-demo-data-quarantine: review
  8-19-two-tier-admin-umbrella: done
  8-22-1-graph-rag-exam-lane-ingestion: done
  21-2-legacy-thing: descoped
"""
STORIES = {
    "story-21-8b-demo-data-quarantine.md": "# Story 21.8b\n\nStatus: review\n\nBody.\n",
    # DRIFTED, and written in the dot form (both naming forms exist in the real tree)
    "story-8.19-two-tier-admin-umbrella.md": "# Story 8.19\n\nStatus: ready-for-dev\n\nBody.\n",
    # agrees, but carries an inline history note after the value
    "story-8.22.1-graph-rag-exam-lane-ingestion.md":
        "# Story 8.22.1\n\nStatus: done  # review -> done 2026-07-03 at close-out\n\nBody.\n",
}
BOARD_REL = Path("_bmad-output/implementation-artifacts/sprint-status.yaml")
STORY_REL = Path("_bmad/bmm/stories")


def build(root: Path) -> Path:
    proj = root / "proj"
    if proj.exists():
        for p in sorted(proj.rglob("*"), reverse=True):
            if p.is_file():
                p.chmod(stat.S_IWRITE)
                p.unlink()
            else:
                p.rmdir()
        proj.rmdir()
    (proj / BOARD_REL.parent).mkdir(parents=True)
    (proj / STORY_REL).mkdir(parents=True)
    (proj / BOARD_REL).write_text(BOARD, encoding="utf-8")
    for name, text in STORIES.items():
        (proj / STORY_REL / name).write_text(text, encoding="utf-8")
    return proj


def board_status(proj: Path, key: str) -> str | None:
    for line in (proj / BOARD_REL).read_text(encoding="utf-8").splitlines():
        if line.strip().startswith(f"{key}:"):
            return line.split(":", 1)[1].split("#")[0].strip()
    return None


def file_status(proj: Path, name: str) -> str | None:
    for line in (proj / STORY_REL / name).read_text(encoding="utf-8").splitlines():
        if line.startswith("Status:"):
            return line.split(":", 1)[1].split("#")[0].strip()
    return None


Q = "story-21-8b-demo-data-quarantine.md"
U = "story-8.19-two-tier-admin-umbrella.md"


def main() -> int:
    c = Cases("story_status")
    with TempDir() as tmp:
        def ss(*args: str) -> tuple[int, str]:
            proj = build(tmp)
            return (*run_script("story_status.py", *args, "--project", str(proj)), proj)[:2]

        # A - check reports the seeded drift only
        proj = build(tmp)
        code, out = run_script("story_status.py", "check", "--project", str(proj))
        c.check("A check finds seeded drift",
                code == 1 and "8-19-two-tier-admin-umbrella" in out and "21-8b" not in out,
                f"exit={code}")

        # B - happy path flips BOTH surfaces
        proj = build(tmp)
        code, out = run_script("story_status.py", "set", "21.8b", "done", "--project", str(proj))
        c.check("B set flips both surfaces",
                code == 0 and board_status(proj, "21-8b-demo-data-quarantine") == "done"
                and file_status(proj, Q) == "done" and "[AGREE]" in out, f"exit={code}")

        # C - THE 21.8b class: refuse a drifted story, writing NEITHER surface
        proj = build(tmp)
        code, out = run_script("story_status.py", "set", "8.19", "done", "--project", str(proj))
        c.check("C refuses drifted, writes NEITHER",
                code == 2 and "DRIFTED" in out
                and board_status(proj, "8-19-two-tier-admin-umbrella") == "done"
                and file_status(proj, U) == "ready-for-dev", f"exit={code}")

        # D - --reconcile fixes both, resolving a dot-form file from a dash-form key
        proj = build(tmp)
        code, out = run_script("story_status.py", "set", "8.19", "done", "--reconcile",
                               "--project", str(proj))
        c.check("D --reconcile fixes both (dot-form file)",
                code == 0 and file_status(proj, U) == "done"
                and board_status(proj, "8-19-two-tier-admin-umbrella") == "done", f"exit={code}")

        for name, args, needle in (
            ("E refuses terminal downgrade", ("set", "8.22.1", "review"), "terminal"),
            ("F refuses unknown status", ("set", "21.8b", "finished"), "unknown status"),
            ("G refuses ruling state w/o --force", ("set", "21.8b", "deferred"), "RULING"),
            ("H refuses rank downgrade", ("set", "21.8b", "in-progress"), "downgrade"),
        ):
            proj = build(tmp)
            code, out = run_script("story_status.py", *args, "--project", str(proj))
            c.check(name, code == 2 and needle in out, f"exit={code}")

        # I - an inline history note is not drift
        proj = build(tmp)
        code, out = run_script("story_status.py", "get", "8.22.1", "--project", str(proj))
        c.check("I inline note != drift",
                code == 0 and "board=done  frontmatter=done" in out, out.strip())

        # J - ATOMICITY: board unwritable -> the story file must be ROLLED BACK
        proj = build(tmp)
        os.chmod(proj / BOARD_REL, stat.S_IREAD)
        code, out = run_script("story_status.py", "set", "21.8b", "done", "--project", str(proj))
        os.chmod(proj / BOARD_REL, stat.S_IWRITE)
        c.check("J rolls story back when the board write fails",
                code != 0 and file_status(proj, Q) == "review"
                and board_status(proj, "21-8b-demo-data-quarantine") == "review"
                and "ROLLBACK" in out, f"exit={code} file={file_status(proj, Q)}")
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
