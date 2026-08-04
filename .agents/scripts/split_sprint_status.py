"""split_sprint_status.py — move narrative out of sprint-status.yaml, provably losslessly (Wave 4).

The board is ~363 KB of which 2.7 % is state; 62 % is the trailing note ON the key lines.
This tool moves narrative to `_bmad-output/history/` in staged, individually-verifiable
passes, recording every move in `migration-manifest.json` so the ORIGINAL file can be
reconstructed byte-for-byte and diffed against the pinned git blob.

    split_sprint_status.py plan   [--project P] [--classify-comments]
    split_sprint_status.py apply  --stage terminal|changelog|comments|active
                                  [--project P] [--sha SHA] [--triage FILE]
    split_sprint_status.py verify --sha SHA [--project P]

Contracts the audit made non-negotiable:

*  **The baseline is the git blob** (`git show <sha>:<path>`), never the working tree —
   `* text=auto` + autocrlf means TWO byte streams exist for this file (audit F1). Every
   read here is normalized to the LF stream; every write is LF and git re-presents it.
*  **`verify` needs `--sha`** (audit F4): unpinned, a close-out landing mid-migration
   makes an honest run read as corrupt — the exact shape that got gate_receipt's
   staleness check demoted to permanent `--advisory`.
*  **The no-note set is `wf_common.NO_NOTE_STATUSES`** (audit F3), imported, never
   re-declared, so the split and the note-budget lint cannot disagree about a row.
*  **Reconstruction never peeks at the blob.** It rebuilds the original from
   (current board + history files + manifest) alone, THEN compares to the blob.
   Narrative content lives in history files; the manifest holds structure plus the
   handful of INSERTED pointer lines (new text, not moved text).
*  **`apply --stage comments` refuses without a triage file** and refuses any candidate
   line the triage leaves unclassified or marks `?` — the fail-closed default is KEEP,
   because a comment left behind costs bytes but doctrine buried in history loses a
   ruling (audit, Gate 3).

Stages compose: each apply simulates the current board from (blob + manifest) first and
dies loudly if the tree moved outside this tool — a mid-migration write is a stop, not
a silent merge.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wf_common as wf

HISTORY_REL = "_bmad-output/history"
MANIFEST_REL = f"{HISTORY_REL}/migration-manifest.json"
NOTE_CAP = 120  # ruling 2026-08-03: max inline note on a non-terminal row, in chars after '#'

_CHANGELOG_MARK = "CHANGE LOG"


# ── byte-stream discipline ─────────────────────────────────────────────────────


def lf(text: str) -> str:
    return text.replace("\r\n", "\n")


def read_lf(path: Path) -> str:
    """Worktree read, normalized to the LF stream. autocrlf makes worktree EOLs a
    per-machine presentation detail; the blob stream is the only stable one."""
    return lf(path.read_bytes().decode("utf-8", errors="surrogateescape"))


def write_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8", errors="surrogateescape"))


def git_blob(repo: Path, sha: str, rel: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), "show", f"{sha}:{rel}"],
                       capture_output=True)
    if p.returncode != 0:
        wf.die(f"git show {sha}:{rel} failed: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode("utf-8", errors="surrogateescape")  # blobs are already LF


# ── manifest model ─────────────────────────────────────────────────────────────
# spans:      whole original lines moved verbatim   {src_start, src_end, dest, dest_start}
# tails:      key lines whose trailing note moved   {src (int), dest, dest_line}
#             original = current-line[:end of status token] + tail-from-history
# insertions: NEW lines in the current board        {after_src, lines: [...]}
#             (anchored to the original line they follow; 0 = file start)


def load_manifest(project: Path) -> dict | None:
    p = project / MANIFEST_REL
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def save_manifest(project: Path, m: dict) -> None:
    m["spans"] = sorted(m["spans"], key=lambda s: s["src_start"])
    m["tails"] = dict(sorted(m["tails"].items(), key=lambda kv: int(kv[0])))
    write_lf(project / MANIFEST_REL, json.dumps(m, indent=1, ensure_ascii=False) + "\n")


def new_manifest(sha: str, n_lines: int, trailing_nl: bool) -> dict:
    return {"source_sha": sha, "board": wf.BOARD_REL, "total_lines": n_lines,
            "trailing_newline": trailing_nl, "stages_done": [],
            "spans": [], "tails": {}, "insertions": []}


# ── line classification ────────────────────────────────────────────────────────


def key_match(line: str):
    m = wf._KEY_RE.match(line)
    return m if (m and m.group(2) in wf.ALL_STATUSES) else None


def history_dir(key: str) -> str:
    """epic-N grouping. Deterministic, and recorded in the manifest anyway — the
    reconstruction never depends on this rule."""
    if key.startswith("quick-fix"):
        return "quick-fix"
    if key.startswith("epic-"):
        return re.sub(r"-retrospective$", "", key)
    parts = key.split("-")
    prefix: list[str] = []
    for p in parts:
        prefix.append(p)
        if p and p[0].isdigit():
            return "epic-" + "-".join(prefix)
    return "misc"


def find_changelog_span(lines: list[str]) -> tuple[int, int] | None:
    """The block from the `# ── CHANGE LOG` marker through the last consecutive
    comment/blank line before the next real key. 1-based inclusive; None once moved."""
    start = next((i for i, l in enumerate(lines, 1)
                  if l.lstrip().startswith("#") and _CHANGELOG_MARK in l and "──" in l), None)
    if start is None:
        return None
    end = start
    for i in range(start, len(lines)):
        l = lines[i]  # 0-based lookahead at line i+1
        if l.strip() == "" or l.lstrip().startswith("#"):
            end = i + 1
        else:
            break
    return start, end


# ── simulation + reconstruction (the same walk, two directions) ────────────────


def simulate_current(orig: list[str], m: dict) -> list[str]:
    """What the board must look like after the manifest's operations."""
    moved: set[int] = set()
    for s in m["spans"]:
        moved.update(range(s["src_start"], s["src_end"] + 1))
    tails = {int(k): v for k, v in m["tails"].items()}
    ins_after: dict[int, list[str]] = {}
    for ins in m["insertions"]:
        ins_after.setdefault(ins["after_src"], []).extend(ins["lines"])
    out: list[str] = list(ins_after.get(0, []))
    for i, line in enumerate(orig, 1):
        if i in moved:
            pass
        elif i in tails:
            km = key_match(line)
            out.append(line[:km.end(2)] if km else line)
        else:
            out.append(line)
        out.extend(ins_after.get(i, []))
    return out


def reconstruct_original(project: Path, m: dict) -> str:
    """Rebuild the original LF stream WITHOUT reading the blob."""
    cur = read_lf(project / wf.BOARD_REL).split("\n")
    if m["trailing_newline"]:
        if cur and cur[-1] == "":
            cur.pop()
    hist_cache: dict[str, list[str]] = {}

    def hist_line(dest: str, line_no: int) -> str:
        if dest not in hist_cache:
            hist_cache[dest] = read_lf(project / dest).split("\n")
        hl = hist_cache[dest]
        if line_no < 1 or line_no > len(hl):
            wf.die(f"manifest points at {dest}:{line_no} but the file has {len(hl)} lines")
        return hl[line_no - 1]

    moved: dict[int, tuple[str, int]] = {}
    for s in m["spans"]:
        for off, i in enumerate(range(s["src_start"], s["src_end"] + 1)):
            moved[i] = (s["dest"], s["dest_start"] + off)
    tails = {int(k): v for k, v in m["tails"].items()}
    ins_after: dict[int, int] = {}
    for ins in m["insertions"]:
        ins_after[ins["after_src"]] = ins_after.get(ins["after_src"], 0) + len(ins["lines"])

    out: list[str] = []
    ci = ins_after.get(0, 0)  # cursor into cur, skipping inserted lines
    for i in range(1, m["total_lines"] + 1):
        if i in moved:
            dest, dl = moved[i]
            out.append(hist_line(dest, dl))
        else:
            if ci >= len(cur):
                wf.die(f"current board ran out of lines at original line {i} - "
                       f"the board changed outside the split tool")
            line = cur[ci]
            ci += 1
            if i in tails:
                t = tails[i]
                km = key_match(line)
                if not km:
                    wf.die(f"original line {i} should be a key line but the current "
                           f"board has {line!r} - the board changed outside the split tool")
                out.append(line[:km.end(2)] + hist_line(t["dest"], t["dest_line"]))
            else:
                out.append(line)
        ci += ins_after.get(i, 0)
    text = "\n".join(out)
    return text + "\n" if m["trailing_newline"] else text


# ── history-file writing ───────────────────────────────────────────────────────


def append_history(project: Path, dest_rel: str, header: str, marker: str,
                   content_lines: list[str]) -> int:
    """Append marker + verbatim lines; return the 1-based line number of the FIRST
    content line. Creates the file with a header when absent."""
    p = project / dest_rel
    if p.exists():
        text = read_lf(p)
        if not text.endswith("\n"):
            text += "\n"
    else:
        text = header
    lines_before = text.count("\n")  # content starts after marker line
    text += marker + "\n"
    text += "\n".join(content_lines) + "\n"
    write_lf(p, text)
    return lines_before + 2  # +1 for the marker line, +1 to land ON the first content line


def file_header(title: str, sha: str) -> str:
    return (f"# {title}\n\n"
            f"Verbatim narrative split from `sprint-status.yaml` @ {sha[:8]} "
            f"(Wave 4, 2026-08-03). Lines under each `<!-- ... -->` marker are byte-exact\n"
            f"originals; `migration-manifest.json` maps them home. Do not re-wrap them.\n\n")


# ── stages ─────────────────────────────────────────────────────────────────────


def stage_terminal(project: Path, orig: list[str], m: dict, sha: str) -> int:
    """Move the trailing note of every NO_NOTE-status key line to per-key history."""
    n = 0
    for i, line in enumerate(orig, 1):
        km = key_match(line)
        if not km or str(i) in m["tails"]:
            continue
        key, status, tail = km.group(1), km.group(2), line[km.end(2):]
        if status not in wf.NO_NOTE_STATUSES or not tail.strip():
            continue
        dest = f"{HISTORY_REL}/{history_dir(key)}/{key}.md"
        dl = append_history(project, dest, file_header(f"Board history — {key}", sha),
                            f"<!-- board-note src={i} status={status} -->", [tail])
        m["tails"][str(i)] = {"dest": dest, "dest_line": dl, "key": key}
        n += 1
    return n


def stage_active(project: Path, orig: list[str], m: dict, sha: str) -> int:
    """Move over-cap notes on non-NO_NOTE rows. A note within the cap stays verbatim;
    an over-cap note moves WHOLE - truncating it would fabricate a summary."""
    n = 0
    for i, line in enumerate(orig, 1):
        km = key_match(line)
        if not km or str(i) in m["tails"]:
            continue
        key, status, tail = km.group(1), km.group(2), line[km.end(2):]
        if status in wf.NO_NOTE_STATUSES or not tail.strip():
            continue
        note = tail.strip().lstrip("#").strip()
        if len(note) <= NOTE_CAP:
            continue
        dest = f"{HISTORY_REL}/{history_dir(key)}/{key}.md"
        dl = append_history(project, dest, file_header(f"Board history — {key}", sha),
                            f"<!-- board-note src={i} status={status} -->", [tail])
        m["tails"][str(i)] = {"dest": dest, "dest_line": dl, "key": key}
        n += 1
    return n


def stage_changelog(project: Path, orig: list[str], m: dict, sha: str) -> int:
    """Move the CHANGE LOG block wholesale; leave a pointer; promote `last_updated`
    to a real key (audit F9 - today it is a comment that rides out with the block)."""
    span = find_changelog_span(orig)
    if span is None:
        wf.die("no CHANGE LOG marker line found")
    start, end = span
    if any(s["src_start"] <= start <= s["src_end"] for s in m["spans"]):
        wf.die("changelog stage already applied")
    dest = f"{HISTORY_REL}/CHANGELOG.md"
    dl = append_history(
        project, dest, file_header("Board CHANGE LOG", sha),
        f"<!-- board-lines src={start}-{end} -->", orig[start - 1:end])
    m["spans"].append({"src_start": start, "src_end": end,
                       "dest": dest, "dest_start": dl, "what": "changelog"})
    # Every `# last_updated:` COMMENT goes with the block - line 2 redirects readers to a
    # block that is leaving, line 66 duplicates a date. Left behind, both become lies the
    # first time the real key (below) refreshes. The real key is what bmad-sprint-status's
    # freshness check reads (template line 44 shape) - audit F9.
    stamp = None
    for i, line in enumerate(orig, 1):
        if re.match(r"^#\s*last_updated:\s*\d{4}-\d{2}-\d{2}", line):
            stamp = re.search(r"(\d{4}-\d{2}-\d{2})", line).group(1)
        if (re.match(r"^#\s*last_updated:", line)
                and not (start <= i <= end)
                and not any(s["src_start"] <= i <= s["src_end"] for s in m["spans"])):
            dl2 = append_history(project, dest, "",
                                 f"<!-- board-line src={i} -->", [line])
            m["spans"].append({"src_start": i, "src_end": i,
                               "dest": dest, "dest_start": dl2, "what": "stale-lu-comment"})
    m["insertions"].append({
        "after_src": start - 1,
        "lines": [f"# CHANGE LOG moved to {HISTORY_REL}/CHANGELOG.md (Wave 4 split; "
                  f"newest first, verbatim). Add new entries THERE.",
                  f"last_updated: {stamp or '2026-08-03'}"]})
    return end - start + 1


def stage_comments(project: Path, orig: list[str], m: dict, sha: str,
                   triage: Path | None) -> int:
    """Whole-line comment moves, driven ONLY by a reviewed triage file."""
    if triage is None or not triage.exists():
        wf.die("--stage comments requires --triage <file> (fail-closed: no file, no moves)")
    verdicts: dict[int, str] = {}
    for row in read_lf(triage).split("\n"):
        if not row.strip() or row.startswith("line\t"):
            continue
        parts = row.split("\t")
        if len(parts) < 3:
            wf.die(f"triage row malformed: {row!r}")
        verdicts[int(parts[0])] = parts[2].strip().upper()
    moved_already: set[int] = set()
    for s in m["spans"]:
        moved_already.update(range(s["src_start"], s["src_end"] + 1))
    candidates = comment_candidates(orig, m)
    unruled = [i for i in candidates if verdicts.get(i) not in ("MOVE", "KEEP")]
    if unruled:
        wf.die(f"{len(unruled)} candidate line(s) unclassified or '?' in the triage "
               f"(first: {unruled[:5]}) - fail-closed, nothing moved")
    # group consecutive MOVE lines into spans
    n = 0
    run: list[int] = []
    for i in sorted(candidates) + [None]:
        if i is not None and verdicts.get(i) == "MOVE" and (not run or i == run[-1] + 1):
            run.append(i)
            continue
        if run:
            dest = f"{HISTORY_REL}/board-comments.md"
            dl = append_history(project, dest,
                                file_header("Board comments (triaged out)", sha),
                                f"<!-- board-lines src={run[0]}-{run[-1]} -->",
                                orig[run[0] - 1:run[-1]])
            m["spans"].append({"src_start": run[0], "src_end": run[-1],
                               "dest": dest, "dest_start": dl, "what": "comment"})
            n += len(run)
        run = [i] if (i is not None and verdicts.get(i) == "MOVE") else []
    return n


def comment_candidates(orig: list[str], m: dict) -> list[int]:
    """Free comment lines inside development_status, excluding epic banners and
    anything already moved. Banners stay - they are the only navigation left."""
    moved: set[int] = set()
    for s in m["spans"]:
        moved.update(range(s["src_start"], s["src_end"] + 1))
    ds = next((i for i, l in enumerate(orig, 1)
               if l.startswith("development_status:")), None)
    if ds is None:
        wf.die("no development_status: line")
    banner = re.compile(r"^\s*#\s*(═+|Epic\b|STATUS:|─+)")
    out = []
    for i in range(ds + 1, len(orig) + 1):
        l = orig[i - 1]
        if l.startswith(("action_items:",)):
            break
        if i in moved or not l.strip().startswith("#") or banner.match(l):
            continue
        out.append(i)
    return out


# ── commands ───────────────────────────────────────────────────────────────────


def resolve(project_arg: str | None) -> Path:
    return wf.resolve_project_root(project_arg)


def head_sha(project: Path) -> str:
    p = subprocess.run(["git", "-C", str(project), "rev-parse", "HEAD"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        wf.die("git rev-parse HEAD failed")
    return p.stdout.strip()


def board_clean(project: Path) -> bool:
    p = subprocess.run(["git", "-C", str(project), "status", "--porcelain", "--",
                        wf.BOARD_REL], capture_output=True, text=True)
    return p.returncode == 0 and not p.stdout.strip()


def load_orig(project: Path, m: dict) -> list[str]:
    blob = git_blob(project, m["source_sha"], m["board"])
    lines = blob.split("\n")
    if m["trailing_newline"] and lines and lines[-1] == "":
        lines.pop()
    return lines


def cmd_plan(project: Path, classify: bool) -> int:
    text = read_lf(project / wf.BOARD_REL)
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    term = act = term_b = act_b = 0
    for line in lines:
        km = key_match(line)
        if not km:
            continue
        tail = line[km.end(2):]
        if not tail.strip():
            continue
        if km.group(2) in wf.NO_NOTE_STATUSES:
            term, term_b = term + 1, term_b + len(tail.encode())
        else:
            act, act_b = act + 1, act_b + len(tail.encode())
    span = find_changelog_span(lines)
    m = load_manifest(project)
    print(f"board: {len(text.encode())} bytes (LF stream), {len(lines)} lines")
    print(f"no-note rows with a tail: {term}  ({term_b} bytes)  -> --stage terminal")
    print(f"active rows with a tail:  {act}  ({act_b} bytes)  -> --stage active (cap {NOTE_CAP})")
    if span:
        cs, ce = span
        print(f"changelog block: lines {cs}-{ce} "
              f"({sum(len(l.encode()) + 1 for l in lines[cs - 1:ce])} bytes) -> --stage changelog")
    else:
        print("changelog block: absent (already moved)")
    print(f"manifest: {'ABSENT (no stage applied)' if m is None else m['stages_done']}")
    if classify:
        # Triage lives in ORIGINAL line numbers - the coordinate system the manifest and
        # every later apply use. Pre-migration the worktree IS the original; after any
        # stage, only the pinned blob is.
        if m is not None:
            src_lines = load_orig(project, m)
            mm = m
        else:
            src_lines, mm = lines, new_manifest("WORKTREE", len(lines), text.endswith("\n"))
        rows = ["line\tpreview\tverdict"]
        for i in comment_candidates(src_lines, mm):
            l = src_lines[i - 1].strip()
            dated = bool(re.match(r"^#\s*(⛔|✅|⚠️|·)?\s*20\d\d-\d\d", l)) or "CLOSED" in l
            rows.append(f"{i}\t{l[:80]}\t{'MOVE' if dated else 'KEEP'}")
        out = project / HISTORY_REL / "comment-triage.tsv"
        write_lf(out, "\n".join(rows) + "\n")
        print(f"triage written: {out} ({len(rows) - 1} candidate lines) - REVIEW IT; "
              f"apply refuses on any line left unclassified")
    return 0


def cmd_apply(project: Path, stage: str, sha: str | None, triage: Path | None) -> int:
    if not board_clean(project):
        wf.die(f"{wf.BOARD_REL} has uncommitted changes - commit or restore first; "
               f"apply refuses to build on a moving base")
    m = load_manifest(project)
    if m is None:
        src = sha or head_sha(project)
        blob = git_blob(project, src, wf.BOARD_REL)
        lines = blob.split("\n")
        trailing = blob.endswith("\n")
        if trailing:
            lines.pop()
        m = new_manifest(src, len(lines), trailing)
    elif sha and sha != m["source_sha"] and not m["source_sha"].startswith(sha):
        wf.die(f"--sha {sha} != manifest source_sha {m['source_sha'][:12]} - one migration, "
               f"one baseline")
    if stage in m["stages_done"]:
        wf.die(f"stage '{stage}' already applied")
    orig = load_orig(project, m)

    # The board on disk must be exactly what the manifest predicts - a mid-migration
    # write from anything else is a STOP, not something to merge around.
    expect = simulate_current(orig, m)
    actual = read_lf(project / wf.BOARD_REL).split("\n")
    if m["trailing_newline"] and actual and actual[-1] == "":
        actual.pop()
    if actual != expect:
        for j, (a, e) in enumerate(zip(actual, expect), 1):
            if a != e:
                wf.die(f"board line {j} changed outside the split tool:\n  have {a[:90]!r}"
                       f"\n  want {e[:90]!r}")
        wf.die(f"board length {len(actual)} != expected {len(expect)} - "
               f"changed outside the split tool")

    fn = {"terminal": stage_terminal, "active": stage_active,
          "changelog": stage_changelog}.get(stage)
    n = (stage_comments(project, orig, m, m["source_sha"], triage) if stage == "comments"
         else fn(project, orig, m, m["source_sha"]))
    m["stages_done"].append(stage)
    new_board = "\n".join(simulate_current(orig, m))
    if m["trailing_newline"]:
        new_board += "\n"
    write_lf(project / wf.BOARD_REL, new_board)
    save_manifest(project, m)
    print(f"[APPLY {stage}] {n} move(s); board now {len(new_board.encode())} bytes "
          f"(was {sum(len(l.encode()) + 1 for l in orig)})")
    print(f"run: split_sprint_status.py verify --sha {m['source_sha'][:12]}")
    return 0


def cmd_verify(project: Path, sha: str) -> int:
    m = load_manifest(project)
    if m is None:
        wf.die("no migration-manifest.json - nothing to verify")
    if not (m["source_sha"] == sha or m["source_sha"].startswith(sha)):
        wf.die(f"--sha {sha} != manifest source_sha {m['source_sha'][:12]}")
    rebuilt = reconstruct_original(project, m)
    blob = git_blob(project, m["source_sha"], m["board"])
    rb, bb = rebuilt.encode("utf-8", "surrogateescape"), blob.encode("utf-8", "surrogateescape")
    if rb == bb:
        print(f"[VERIFY] OK - reconstruction is byte-identical to "
              f"{m['source_sha'][:12]}:{m['board']} ({len(bb)} bytes)")
        return 0
    n = min(len(rb), len(bb))
    off = next((i for i in range(n) if rb[i] != bb[i]), n)
    line = blob[:off].count("\n") + 1 if off <= len(bb) else "?"
    print(f"[VERIFY] FAIL - first differing byte at offset {off} (original line ~{line}); "
          f"rebuilt {len(rb)} bytes vs blob {len(bb)}")
    print(f"  rebuilt: ...{rebuilt[max(0, off - 40):off + 40]!r}...")
    print(f"  blob:    ...{blob[max(0, off - 40):off + 40]!r}...")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Lossless sprint-status.yaml splitter (Wave 4)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--project")
    p.add_argument("--classify-comments", action="store_true")
    p = sub.add_parser("apply")
    p.add_argument("--stage", required=True,
                   choices=["terminal", "changelog", "comments", "active"])
    p.add_argument("--project")
    p.add_argument("--sha")
    p.add_argument("--triage")
    p = sub.add_parser("verify")
    p.add_argument("--sha", required=True,
                   help="the migration's source commit; REQUIRED (audit F4)")
    p.add_argument("--project")
    args = ap.parse_args()
    project = resolve(args.project)
    if args.cmd == "plan":
        return cmd_plan(project, args.classify_comments)
    if args.cmd == "apply":
        return cmd_apply(project, args.stage, args.sha,
                         Path(args.triage) if args.triage else None)
    return cmd_verify(project, args.sha)


if __name__ == "__main__":
    sys.exit(main())
