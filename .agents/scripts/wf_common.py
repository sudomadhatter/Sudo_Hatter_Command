"""Shared helpers for the workflow-infrastructure scripts (Wave 1, 2026-08-02).

Used by workflow_lint.py / story_status.py / gate_receipt.py / closeout_preflight.py.
These scripts VERIFY the sudo dev-flow's invariants (status agreement, gate receipts,
board + context budgets) so command prose can later shrink to "run the check" — the
plan's governing principle: an instruction may only be deleted after a script enforces it.

This file declares `wf-lint: allow-encoding-literals` — it holds a literal U+FFFD and
the cp1252 digraph table as DATA, and without the opt-out the encoding gate flags the
very module that implements it.

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
# SCRUM_BOARD_REL retired 2026-08-07 (SCC-22): the scrum-board map is superseded by Jira;
# sprint-status.yaml (BOARD_REL) remains the working sprint state.
EPICS_REL = "_bmad-output/planning-artifacts/epics.md"
GATES_REL = "_bmad-output/gates"

# ── Status vocabulary (mirrors sprint-status.yaml's STATUS DEFINITIONS block) ──
PROGRESS_ORDER = ["backlog", "ready-for-dev", "in-progress", "review", "done"]
STATUS_RANK = {s: i for i, s in enumerate(PROGRESS_ORDER)}
TERMINAL = {"done", "descoped"}
ALL_STATUSES = set(PROGRESS_ORDER) | {"descoped", "deferred", "deferred-v3", "optional"}

# Statuses whose board row carries NO inline note (Wave 4 ruling, 2026-08-03): the row's
# story lives in _bmad-output/history/ + the walkthrough, so a trailing note on one of
# these is either stale (a lie about a finished thing) or misplaced narrative. This is
# deliberately NOT `TERMINAL` — that set answers "may this status ever change again?"
# (optional retros and deferred-v3 parks CAN move), while this one answers "does anyone
# still need a note here?". The split tool and the note-budget lint import THIS set; a
# private re-declaration in either is how the two disagree about day one (audit F3).
NO_NOTE_STATUSES = {"done", "descoped", "deferred-v3", "optional"}

# Max inline note on a row that may still carry one, in chars after the '#'. Lives HERE
# for the same reason as the set above: the splitter DECIDES by it and the lint JUDGES by
# it, so two declarations is the splitter emitting a board that fails its own gate.
NOTE_CAP = 120

# Mojibake signatures: UTF-8 text that was decoded as cp1252 and re-encoded.
# NOTE: a cp1252-rendered console (PS 5.1 `Get-Content`) SHOWS these for perfectly good
# UTF-8 files — only an on-disk byte check proves corruption, which is why detection lives
# here (bytes) and not in eyeballed terminal output.
MOJIBAKE_MARKERS = ("â€", "â•", "â‘", "âš",
                    "âœ", "â›", "Ã©", "ï¸")
REPLACEMENT_CHAR = "�"  # a decode FAILURE — bytes that are not valid UTF-8 at all

# Public: three modules match board lines with GROUPS (parse_board only returns statuses,
# which is not enough to read or rewrite a row's trailing note). `_KEY_RE` stays as an
# alias so nothing that already imported the private name breaks.
KEY_RE = re.compile(r"^  ([A-Za-z0-9][A-Za-z0-9_.-]*):\s*([a-z0-9-]+)(.*)$")
_KEY_RE = KEY_RE


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

    Docs that TEACH a bad pattern quote it verbatim — `cicd-prune-context.md` says
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
    """A board key that OWES a story file under `_bmad/bmm/stories/`.

    Three kinds legitimately have none: an `epic-*` umbrella, a `*-retrospective`, and a
    `quick-fix-*` track — the quick-fix ruling (2026-08-03) says a quick fix mints NO story
    file and NO epic key on purpose, so demanding one reports the rule itself as a defect."""
    return (not key.startswith(("epic-", "quick-fix-"))
            and not key.endswith("-retrospective"))


def norm_id(s: str) -> str:
    return s.lower().replace(".", "-").strip()


def slug_matches(want: str, have: str) -> bool:
    """Story-id containment WITH a separator guard.

    A bare `startswith` makes `21-8` match `21-8b-demo-data-quarantine`, so a SIBLING's
    artifacts can satisfy — or block — the wrong story's close-out. Only an exact match or
    a match ending at a `-` boundary counts."""
    want, have = norm_id(want), norm_id(have)
    return want == have or want.startswith(have + "-") or have.startswith(want + "-")


_ID_RE = re.compile(r"^(\d+(?:-\d+)*[a-z]?)")


def story_id(key: str) -> str:
    """The bare numeric id from a board key: `21-8b-demo-data-quarantine` -> `21-8b`.
    Branch names and worktree dirs carry the id, never the whole key."""
    m = _ID_RE.match(norm_id(key))
    return m.group(1) if m else norm_id(key)


def commit_exists(repo: Path, sha: str) -> bool:
    return git(["cat-file", "-e", f"{sha}^{{commit}}"], repo).returncode == 0


def same_tree(repo: Path, a: str, b: str) -> bool | None:
    """Do two commits have identical CONTENT? None if either is unknown here.

    Staleness must compare TREES, not SHAs. A story branch that lands via a merge commit
    produces a different HEAD with an identical tree — SHA equality calls that stale and
    blocks a perfectly good gate, which is how a hard gate earns a permanent `--advisory`."""
    if not (commit_exists(repo, a) and commit_exists(repo, b)):
        return None
    return git(["diff", "--quiet", a, b], repo).returncode == 0


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
    # ⛔ `encoding="utf-8"` is load-bearing on the PC. git writes UTF-8 (paths, messages,
    # `--porcelain -z` filenames unquoted); `text=True` alone decodes with the LOCALE codec,
    # which is cp1252 on Windows - so `_artifacts/café.md` came back as `cafÃ©.md` there and
    # a receipt's "exact filename" was only exact on the Mac (SCC-160 review, Blind Hunter).
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=timeout)


def git_head(cwd: Path) -> str | None:
    r = git(["rev-parse", "HEAD"], cwd)
    return r.stdout.strip() if r.returncode == 0 else None


def changed_since_fork(repo: Path, ref: str, fork: str) -> set[str]:
    """Files `ref` changed since `fork`, as repo-relative paths.

    Two arguments rather than the `fork..ref` range form: a diff treats them identically, and
    the two-argument spelling is what the merge itself compares - so this answer cannot drift
    from the thing it is predicting."""
    r = git(["diff", "--name-only", fork, ref], repo)
    if r.returncode != 0:
        return set()
    return {ln.strip() for ln in r.stdout.splitlines() if ln.strip()}


def base_overlap(repo: Path, branch: str, base: str) -> dict | None:
    """Which files BOTH `branch` and `base` touched since they forked.

    Returns `{"mine": N, "theirs": N, "overlap": [paths]}`, or None when there is no
    merge-base to compare from. Callers decide severity and wording; this only answers the
    question, so the two preflights cannot drift on the ANSWER while disagreeing on the prose.

    Why this exists: "you are 7 commits behind `main`" is true and nearly useless. Being
    behind is routine and usually free. What costs a session is being behind *on a file you
    also edited* - and without naming those, a 30-second fast-forward and a real three-way
    merge print identically, so the two correct reactions look the same.

    Deliberately answered at a gate the lane has already stopped at, not pushed at a lane the
    moment somebody merges to main: a notification cannot know whether it overlaps (most
    merges do not), and interrupting live work to absorb main is its own hazard - it drags
    other people's changes into the diff a review scopes on, and a merge under a running dev
    server has wedged this system before."""
    fork = git(["merge-base", branch, base], repo).stdout.strip()
    if not fork:
        return None
    mine = changed_since_fork(repo, branch, fork)
    theirs = changed_since_fork(repo, base, fork)
    return {"mine": len(mine), "theirs": len(theirs), "overlap": sorted(mine & theirs)}


# How many overlapping paths to name before summarizing the rest. The list answers "which of
# MY files did they touch" - a dozen names answers it; a hundred is a wall that gets scrolled
# past, which is the same as printing nothing. The COUNT is always exact.
OVERLAP_SHOWN = 12


def report_overlap(repo: Path, branch: str, base: str, rep: "Report",
                   section: str = "base") -> None:
    """Print `base_overlap`'s answer. A no-overlap result is printed too - "behind, but on
    files you never touched" is a real answer, and leaving it silent is how a clean absorb
    reads as an unknown risk."""
    info = base_overlap(repo, branch, base)
    if info is None:
        rep.warn(section, f"no merge-base with {base} - cannot tell which files overlap")
        return
    if not info["mine"] or not info["theirs"]:
        return
    overlap = info["overlap"]
    if not overlap:
        rep.info(section, f"no file overlap: {base} moved on {info['theirs']} file(s), none "
                          f"of the {info['mine']} this branch touched - the merge should be clean")
        return
    shown = overlap[:OVERLAP_SHOWN]
    more = f" (+{len(overlap) - len(shown)} more)" if len(overlap) > len(shown) else ""
    rep.err(section, f"{len(overlap)} file(s) changed on BOTH sides - resolve by keeping both "
                     f"sides' facts, never by picking a winner: " + ", ".join(shown) + more)


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


# ── What a VERDICT is, and how a manifest field is read (SCC-190 F6) ──────────────────
#
# These three lived in `task_preflight` because that is where they were first needed. But
# `main_write_gate` - the gate that guards `main` - imported them from there and thereby
# pulled in SEVEN local modules (jira_feed, gate_receipt, hooks_armed, walkthrough_roster,
# task_preflight, wf_common, sop_currency; measured) to buy one regex and two small
# helpers. An import-time break anywhere in that chain became a break in the gate itself.
#
# ⛔ RE-TYPING THEM IN THE GATE WAS NEVER THE ANSWER - a gate and a door disagreeing about
# what a verdict IS is precisely the defect class main_write_gate exists to catch. So they
# move DOWN instead, to the leaf every one of those modules already imports. Still one
# definition; the readers just no longer drag a subsystem in to reach it.
# `task_preflight` re-exports all three, so every existing importer is unaffected.

# The canonical line /smh-code-review Step 4 writes as the review section's first line.
# Anchored at line start: prose ABOUT a verdict does not match; the stamp does.
VERDICT_RE = re.compile(r"^Verdict:\s*(PASS|CONCERNS|FAIL|WAIVED)\s*@\s*([0-9a-fA-F]{7,40})\b",
                        re.MULTILINE)

def manifest_field(text: str, field: str) -> str | None:
    m = re.search(rf"^\s*{field}\s*:\s*[\"']?([^\"'\n#]+)", text, re.MULTILINE)
    return m.group(1).strip() if m else None


def strip_fenced(text: str) -> str:
    """Markdown code fences removed before any verdict scan (SCC-154, finding 8).

    A canonical stamp pasted AS EVIDENCE inside a fence sits at column 0 and matched
    VERDICT_RE — a fenced FAIL was a permanent block. ⛔ Fences close per CommonMark: the
    SAME marker kind, at least the opening length — the first cut toggled on ANY marker
    line, so a ````-or-~~~-wrapped paste whose content held a ``` pair LEAKED its inner
    lines back into the scan (measured by this lane's own review: a quoted FAIL became the
    governing latest stamp, a permanent false block). Marker lines inside an open fence of
    another kind are content and stay dropped. An UNCLOSED fence still drops everything
    after it: no verdict then means the full gate runs, the safe direction — pinned as
    declared design."""
    out: list[str] = []
    fence: tuple[str, int] | None = None      # (marker char, opening length) while inside
    for line in text.splitlines():
        m = re.match(r"^[ \t]{0,3}(`{3,}|~{3,})", line)
        if m:
            marker = m.group(1)
            if fence is None:
                fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1]:
                fence = None
            continue
        if fence is None:
            out.append(line)
    return "\n".join(out)
