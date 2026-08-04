# wf-lint: allow-encoding-literals — the fixture carries real board glyphs on purpose.
"""split_sprint_status.py must be provably lossless — and provably able to FAIL.

The Wave 1 lesson, applied to Wave 4: a `verify` that cannot fire looks exactly like a
clean migration. So beyond the positive control (untouched apply reconstructs the pinned
blob byte-for-byte) this file mutates the output four ways a human reviewer would miss
— a deleted space, a deleted character in history, reordered CHANGELOG lines, a missing
history file — and each MUST fail. The CRLF case proves the OTHER direction: worktree
line endings are per-machine presentation (`* text=auto`), so a CRLF checkout must still
verify clean against the LF blob (audit F1).

Runs against a throwaway git repo: the baseline contract is `git show <sha>:<path>`,
so a bare directory cannot exercise it.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir, run_script

BOARD_REL = Path("_bmad-output/implementation-artifacts/sprint-status.yaml")
HIST = Path("_bmad-output/history")

BOARD = """\
# generated: 2026-03-07
# last_updated: see the CHANGE LOG block below — this file has ONE date, and it lives there
# STATUS DEFINITIONS: (abridged fixture)
#   - done: shipped
#
# ── CHANGE LOG — newest first. ⛔ ONE ENTRY PER LINE. ──
#   2026-08-02 (21.8b ③ PASS + CLOSED review→done): THE FIREWALL IS UP, demo traffic quarantined.
#   2026-07-31 (21.8 ③ + CLOSE-OUT): master demo mode SHIPPED, three-model clean room.
#   2026-07-22 (EPIC 21 CREATED): operator-ratified party-mode brief.
# last_updated: 2026-08-02

project: fixture-AGY
project_key: NOKEY

development_status:

  # ═══════════════════════════════════════════════════
  # Epic 21: Demo mode
  # STATUS: done
  # ═══════════════════════════════════════════════════
  epic-21: done   # ✅ CLOSED 2026-08-02 on the 21.8b close-out. All children terminal.
  21-8-master-demo-mode: done                           # ③ CONCERNS + CLOSED 2026-07-31 (operator sign-off) · three-model clean room; nothing WRONG, only things UNEXPLAINED — five commented decisions.
  21-8b-demo-data-quarantine: done      # ✅ CLOSED 2026-08-02 — ③ PASS @ 64098847. E21-FR10, the write-boundary firewall.
  21-2-server-truth: descoped           # ⛔ DESCOPED 2026-07-24 (operator ruling) — claim-primary authz stands.
  21-9-try-agent-cards: review   # short live note
  21-10-soft-wrap: in-progress          # a deliberately very long active note that keeps going well past the hundred-and-twenty character cap so the active stage must move it wholesale into history rather than truncating it into a fabricated summary
  epic-21-retrospective: optional
  # 2026-08-02 CLOSED wave-3 drift sweep landed here — dated narrative, safe to move.
  # V3 REVIEW POLICY: deferred-v3 rows are revisited as a batch at V3 — this is DOCTRINE, keep.
  21-11-cost-cap: deferred-v3      # parked to V3 batch review (ruling).

action_items:
  - epic: 21
    action: "fixture item"
    status: open
"""


def sh(cwd: Path, *args: str) -> str:
    r = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"{args}: {r.stderr}")
    return r.stdout.strip()


def build(root: Path, name: str) -> tuple[Path, str]:
    proj = root / name
    (proj / BOARD_REL.parent).mkdir(parents=True)
    (proj / BOARD_REL).write_bytes(BOARD.encode("utf-8"))
    sh(proj, "git", "init", "-q")
    sh(proj, "git", "config", "user.email", "t@t")
    sh(proj, "git", "config", "user.name", "t")
    sh(proj, "git", "add", str(BOARD_REL).replace("\\", "/"))
    sh(proj, "git", "commit", "-qm", "fixture board")
    return proj, sh(proj, "git", "rev-parse", "HEAD")


def apply_all(proj: Path, sha: str) -> tuple[int, str]:
    """terminal + changelog + comments(triaged) + active, in the wave's order."""
    codes = []
    out_all = ""
    for stage in ("terminal", "changelog"):
        code, out = run_script("split_sprint_status.py", "apply", "--stage", stage,
                               "--sha", sha, "--project", str(proj))
        codes.append(code)
        out_all += out
        commit_board(proj, stage)
    run_script("split_sprint_status.py", "plan", "--classify-comments",
               "--project", str(proj))
    code, out = run_script("split_sprint_status.py", "apply", "--stage", "comments",
                           "--triage", str(proj / HIST / "comment-triage.tsv"),
                           "--sha", sha, "--project", str(proj))
    codes.append(code)
    out_all += out
    commit_board(proj, "comments")
    code, out = run_script("split_sprint_status.py", "apply", "--stage", "active",
                           "--sha", sha, "--project", str(proj))
    codes.append(code)
    out_all += out
    commit_board(proj, "active")
    return max(codes), out_all


def commit_board(proj: Path, msg: str) -> None:
    sh(proj, "git", "add", "-A")  # fixture repo only; the real run stages explicit paths
    sh(proj, "git", "commit", "-qm", msg)


def verify(proj: Path, sha: str) -> tuple[int, str]:
    return run_script("split_sprint_status.py", "verify", "--sha", sha,
                      "--project", str(proj))


def main() -> int:
    c = Cases("split_sprint_status")
    with TempDir() as tmp:
        # ── the full pipeline on a pristine fixture ────────────────────────────
        proj, sha = build(tmp, "clean")
        code, out = apply_all(proj, sha)
        c.check("A all four stages apply", code == 0, out.splitlines()[-1] if out else "")

        code, out = verify(proj, sha)
        c.check("B positive control: untouched apply verifies byte-clean",
                code == 0 and "byte-identical" in out, out.strip().splitlines()[-1])

        board = (proj / BOARD_REL).read_bytes().decode()
        c.check("C terminal notes gone, banners + state kept",
                "CLOSED 2026-08-02 on the 21.8b" not in board
                and "epic-21: done" in board and "# Epic 21: Demo mode" in board
                and "21-8b-demo-data-quarantine: done" in board, f"{len(board)}B")
        c.check("D short active note kept, long one moved whole",
                "# short live note" in board
                and "hundred-and-twenty character cap" not in board
                and "21-10-soft-wrap: in-progress" in board)
        c.check("E last_updated promoted to a real key + pointer left",
                "\nlast_updated: 2026-08-02\n" in board
                and "CHANGE LOG moved to _bmad-output/history/CHANGELOG.md" in board)
        c.check("E2 no stale last_updated COMMENT survives the move",
                "# last_updated" not in board)
        c.check("F doctrine comment KEPT, dated narrative MOVED",
                "V3 REVIEW POLICY" in board and "wave-3 drift sweep" not in board)
        hist_story = proj / HIST / "epic-21" / "21-8-master-demo-mode.md"
        c.check("G history file carries the verbatim note",
                hist_story.exists()
                and "three-model clean room" in hist_story.read_text(encoding="utf-8"))

        # ── CRLF: a re-checkout on an autocrlf machine must STILL verify ───────
        for p in [proj / BOARD_REL, *sorted((proj / HIST).rglob("*.md"))]:
            raw = p.read_bytes()
            p.write_bytes(raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        code, out = verify(proj, sha)
        c.check("H CRLF worktree verifies clean against the LF blob (F1)",
                code == 0, out.strip().splitlines()[-1])

        # ── negative controls: each mutation MUST fail ─────────────────────────
        def mutated(name: str, mutate) -> tuple[int, str]:
            p2, s2 = build(tmp, name)
            apply_all(p2, s2)
            mutate(p2)
            return verify(p2, s2)

        code, out = mutated("n1", lambda p: (p / BOARD_REL).write_bytes(
            (p / BOARD_REL).read_bytes().replace(
                b"# Epic 21: Demo mode", b"# Epic 21:  Demo mode", 1)))
        c.check("N1 one changed SPACE in the board fails, naming the offset",
                code == 1 and "offset" in out, out.strip().splitlines()[0])

        h = HIST / "epic-21" / "21-8-master-demo-mode.md"
        code, out = mutated("n2", lambda p: (p / h).write_bytes(
            (p / h).read_bytes().replace(b"clean room", b"clean r0om", 1)))
        c.check("N2 one changed char in a history file fails", code == 1, "")

        def reorder(p: Path) -> None:
            cl = p / HIST / "CHANGELOG.md"
            t = cl.read_text(encoding="utf-8")
            a = "#   2026-08-02 (21.8b ③ PASS + CLOSED review→done): THE FIREWALL IS UP, demo traffic quarantined."
            b = "#   2026-07-31 (21.8 ③ + CLOSE-OUT): master demo mode SHIPPED, three-model clean room."
            cl.write_text(t.replace(a, "\x00").replace(b, a).replace("\x00", b),
                          encoding="utf-8")
        code, out = mutated("n3", reorder)
        c.check("N3 reordered CHANGELOG entries fail", code == 1, "")

        code, out = mutated("n4", lambda p: (p / h).unlink())
        c.check("N4 missing history file fails loudly", code != 0, "")

        # ── refusals ───────────────────────────────────────────────────────────
        p5, s5 = build(tmp, "refuse")
        (p5 / BOARD_REL).write_bytes((p5 / BOARD_REL).read_bytes() + b"# dirty\n")
        code, out = run_script("split_sprint_status.py", "apply", "--stage", "terminal",
                               "--sha", s5, "--project", str(p5))
        c.check("R1 apply refuses a dirty board", code != 0 and "uncommitted" in out, "")

        p6, s6 = build(tmp, "refuse2")
        code, out = run_script("split_sprint_status.py", "apply", "--stage", "comments",
                               "--sha", s6, "--project", str(p6))
        c.check("R2 comments stage refuses without a triage file",
                code != 0 and "triage" in out, "")

        p7, s7 = build(tmp, "refuse3")
        code, out = run_script("split_sprint_status.py", "apply", "--stage", "terminal",
                               "--sha", s7, "--project", str(p7))
        commit_board(p7, "terminal")
        # an external write lands mid-migration -> the next stage must STOP
        raw = (p7 / BOARD_REL).read_bytes()
        (p7 / BOARD_REL).write_bytes(raw.replace(
            b"21-9-try-agent-cards: review", b"21-9-try-agent-cards: done", 1))
        commit_board(p7, "external close-out")
        code, out = run_script("split_sprint_status.py", "apply", "--stage", "changelog",
                               "--sha", s7, "--project", str(p7))
        c.check("R3 mid-migration external write stops the next stage",
                code != 0 and "outside the split tool" in out, "")

        code, out = verify(p7, "deadbeef")
        c.check("R4 verify refuses a wrong --sha", code != 0 and "source_sha" in out, "")

        # manifest is cumulative and stages refuse to double-apply
        p8, s8 = build(tmp, "double")
        run_script("split_sprint_status.py", "apply", "--stage", "terminal",
                   "--sha", s8, "--project", str(p8))
        commit_board(p8, "t")
        code, out = run_script("split_sprint_status.py", "apply", "--stage", "terminal",
                               "--sha", s8, "--project", str(p8))
        c.check("R5 a stage refuses to run twice", code != 0 and "already applied" in out, "")
        man = json.loads((p8 / HIST / "migration-manifest.json").read_text(encoding="utf-8"))
        c.check("R6 manifest pins the source sha", man["source_sha"] == s8, man["source_sha"][:12])
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
