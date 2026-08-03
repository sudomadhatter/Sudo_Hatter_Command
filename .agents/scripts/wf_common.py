"""Shared helpers for the workflow-infrastructure scripts (Wave 1, 2026-08-02).

Used by workflow_lint.py / story_status.py / gate_receipt.py / closeout_preflight.py.
These scripts VERIFY the sudo dev-flow's invariants (status agreement, gate receipts,
board + context budgets) so command prose can later shrink to "run the check" — the
plan's governing principle: an instruction may only be deleted after a script enforces it.

Stdlib only (no yq/jq on this machine). Output is plain ASCII — Windows consoles may be
cp1252 and choke on emoji (the flag_demo_school.py precedent).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# ── Canonical relative paths (one place, so a rename is one edit) ──────────────
BOARD_REL = "_bmad-output/implementation-artifacts/sprint-status.yaml"
STORIES_REL = "_bmad/bmm/stories"
ACTIVE_CONTEXT_REL = "_bmad-output/active-context/active-context.md"
SCRUM_BOARD_REL = "_my_resources/_quick_reference/sprint_scrum_board_map.md"
EPICS_REL = "_bmad-output/planning-artifacts/epics.md"
GATES_REL = "_bmad-output/gates"

# ── Status vocabulary (mirrors sprint-status.yaml's STATUS DEFINITIONS block) ──
PROGRESS_ORDER = ["backlog", "ready-for-dev", "in-progress", "review", "done"]
STATUS_RANK = {s: i for i, s in enumerate(PROGRESS_ORDER)}
TERMINAL = {"done", "descoped"}
ALL_STATUSES = set(PROGRESS_ORDER) | {"descoped", "deferred", "deferred-v3", "optional"}

# Mojibake signatures: UTF-8 text that was decoded as cp1252 and re-encoded.
# NOTE: a cp1252-rendered console (PS 5.1 `Get-Content`) SHOWS these for perfectly good
# UTF-8 files — only an on-disk byte check proves corruption, which is why detection lives
# here (bytes) and not in eyeballed terminal output.
MOJIBAKE_MARKERS = ("â€", "â•", "â‘", "âš",
                    "âœ", "â›", "Ã©", "ï¸")
REPLACEMENT_CHAR = "�"  # a decode FAILURE — bytes that are not valid UTF-8 at all

_KEY_RE = re.compile(r"^  ([A-Za-z0-9][A-Za-z0-9_.-]*):\s*([a-z0-9-]+)(.*)$")


def die(msg: str, code: int = 2) -> "None":
    print(f"[ERR] {msg}")
    sys.exit(code)


def find_lobby_root(start: Path) -> Path | None:
    """Walk up looking for the command center (has .agents/ AND Projects/)."""
    for p in [start, *start.parents]:
        if (p / ".agents").is_dir() and (p / "Projects").is_dir():
            return p
    return None


def resolve_project_root(arg: str | None) -> Path:
    """--project may be a name under Projects/, a path, or omitted (cwd walk-up,
    then the lobby's active-project.txt). A project is a dir holding the board file."""
    cwd = Path.cwd()
    if arg:
        cand = Path(arg)
        if (cand / BOARD_REL).is_file():
            return cand.resolve()
        lobby = find_lobby_root(cwd)
        if lobby and (lobby / "Projects" / arg / BOARD_REL).is_file():
            return (lobby / "Projects" / arg).resolve()
        die(f"cannot resolve project '{arg}' (no {BOARD_REL} under it)")
    for p in [cwd, *cwd.parents]:
        if (p / BOARD_REL).is_file():
            return p.resolve()
    lobby = find_lobby_root(cwd)
    if lobby:
        ptr = lobby / ".agents" / "active-project.txt"
        if ptr.is_file():
            name = ptr.read_text(encoding="utf-8").strip()
            cand = lobby / "Projects" / name
            if (cand / BOARD_REL).is_file():
                return cand.resolve()
    die("no project resolved: pass --project, or run inside one")
    raise AssertionError  # unreachable


def read_text(path: Path) -> str:
    """Read-only convenience. `utf-8-sig` strips a BOM if present — several command files
    carry one, and a BOM makes `text.startswith("---")` false so frontmatter looks absent.
    Undecodable bytes become U+FFFD (see REPLACEMENT_CHAR) rather than raising."""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def has_bom(path: Path) -> bool:
    with open(path, "rb") as f:
        return f.read(3) == b"\xef\xbb\xbf"


_FENCE_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
_SPAN_RE = re.compile(r"`[^`\n]*`")


def strip_code(text: str) -> str:
    """Blank out fenced blocks and inline code spans.

    Docs that TEACH a bad pattern quote it verbatim — `sudo-prune-context.md` says
    "no `a-hat-euro` mojibake, use a real em dash" — so a naive scan flags the very file
    telling you not to do it. Same shape as the source-grep gate a comment satisfied
    (memory: comment-literals-invert-source-grep-tests): match PROSE, not quoted examples."""
    return _SPAN_RE.sub("``", _FENCE_RE.sub("", text))


def read_exact(path: Path) -> str:
    """Byte-preserving read for files we will WRITE BACK (surrogateescape keeps
    any broken bytes intact instead of corrupting them further)."""
    with open(path, encoding="utf-8", errors="surrogateescape", newline="") as f:
        return f.read()


def write_exact(path: Path, text: str) -> None:
    with open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
        f.write(text)


def parse_board(board_text: str) -> dict[str, dict]:
    """development_status children: 2-space-indented `key: status  # note` lines.
    Line-oriented on purpose — a YAML round-trip would reflow 800+ hand-tuned lines."""
    out: dict[str, dict] = {}
    for i, line in enumerate(board_text.splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue
        m = _KEY_RE.match(line)
        if m and m.group(2) in ALL_STATUSES:
            key = m.group(1)
            out.setdefault(key, {"status": m.group(2), "line_no": i, "dupes": []})
            if out[key]["line_no"] != i:
                out[key]["dupes"].append(i)
    return out


def is_story_key(key: str) -> bool:
    return not key.startswith("epic-") and not key.endswith("-retrospective")


def norm_id(s: str) -> str:
    return s.lower().replace(".", "-").strip()


def find_story_files(project_root: Path, key: str) -> list[Path]:
    """Story files exist in BOTH naming forms (story-21.8b-* and story-21-8b-*), and a
    file's slug may be a prefix of the board key (or vice versa). Exact match wins."""
    stories = project_root / STORIES_REL
    if not stories.is_dir():
        return []
    want = norm_id(key)
    exact, prefix = [], []
    for f in stories.glob("story-*.md"):
        have = norm_id(f.stem[len("story-"):])
        if have == want:
            exact.append(f)
        elif want.startswith(have + "-") or have.startswith(want + "-"):
            prefix.append(f)
    return exact if exact else prefix


_FM_STATUS_RE = re.compile(r"^Status:\s*(.+?)\s*$", re.MULTILINE)


def frontmatter_status(story_text: str) -> str | None:
    """The status TOKEN only. Story files legitimately carry an inline audit note after the
    value (`Status: done  # review -> done 2026-07-03 at close-out ...`), which is history,
    not drift — comparing the whole line would flag every annotated story forever."""
    head = story_text[:2000]
    m = _FM_STATUS_RE.search(head)
    if not m:
        return None
    return m.group(1).split("#", 1)[0].strip().split()[0] if m.group(1).strip() else None


def status_drift(project_root: Path) -> list[dict]:
    """Every story key whose story file's frontmatter Status disagrees with the board.
    THE recurring failure class (3 memory entries + recurred on 21.8b, 2026-08-02)."""
    board = parse_board(read_text(project_root / BOARD_REL))
    out = []
    for key, info in board.items():
        if not is_story_key(key):
            continue
        files = find_story_files(project_root, key)
        if len(files) != 1:
            continue  # missing/ambiguous files are workflow_lint's report, not drift
        fm = frontmatter_status(read_text(files[0]))
        if fm is None:
            continue
        if norm_id(fm) != norm_id(info["status"]):
            out.append({"key": key, "board": info["status"], "frontmatter": fm,
                        "file": str(files[0].relative_to(project_root))})
    return out


def git(args: list[str], cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True, errors="replace", timeout=timeout)


def git_head(cwd: Path) -> str | None:
    r = git(["rev-parse", "HEAD"], cwd)
    return r.stdout.strip() if r.returncode == 0 else None


class Report:
    """Severity-tiered findings. Exit: 0 clean, 1 warnings only, 2 any error."""

    def __init__(self) -> None:
        self.items: list[dict] = []

    def err(self, section: str, msg: str) -> None:
        self.items.append({"sev": "ERROR", "section": section, "msg": msg})

    def warn(self, section: str, msg: str) -> None:
        self.items.append({"sev": "WARN", "section": section, "msg": msg})

    def info(self, section: str, msg: str) -> None:
        self.items.append({"sev": "INFO", "section": section, "msg": msg})

    def counts(self) -> tuple[int, int]:
        e = sum(1 for i in self.items if i["sev"] == "ERROR")
        w = sum(1 for i in self.items if i["sev"] == "WARN")
        return e, w

    def exit_code(self) -> int:
        e, w = self.counts()
        return 2 if e else (1 if w else 0)

    def print_human(self, title: str) -> None:
        print(f"== {title} ==")
        for i in self.items:
            print(f"[{i['sev']:5}] {i['section']}: {i['msg']}")
        e, w = self.counts()
        print(f"-- {e} error(s), {w} warning(s), "
              f"{len(self.items) - e - w} info --")
