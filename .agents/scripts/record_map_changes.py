#!/usr/bin/env python3
"""record_map_changes.py — commit-time drift RECORDER for the repo-map + INDEX system (any workspace).

The fast, non-blocking companion to check_maps.py. A `post-commit` git hook calls this on every
commit; it classifies the commit's changes into the linter's judgment categories and appends ONE
line to a machine-local journal (`docs/.maps-journal.jsonl`). The existing consumers — the
SessionStart nag and the /1_update-maps workflow — then read a PRE-SCOPED worklist instead of
re-deriving "what changed" from scratch.

  CACHE, NOT TRUTH. The journal only ACCELERATES. `git diff <anchor>..HEAD` (check_maps check 4)
  stays ground truth. Every consumer runs a freshness guard (journal's last sha == HEAD?) and, if
  stale — a commit made without this hook, on another machine, or a rebase — FALLS BACK to the full
  derivation. Same discipline as the machine-local GitNexus index rule. That is why the journal is
  gitignored: it is a local accelerator rebuilt as you commit, never a shared source of truth.

Modes:
    python record_map_changes.py --commit HEAD     # append one classified line for a commit (the hook)
    python record_map_changes.py --nag             # print classified tail since the anchor (SessionStart); always exit 0
    python record_map_changes.py --consume <sha>   # roll journal lines up to <sha> into the archive (called by --set-anchor)

Journal line (one per commit, even with empty changes so the freshness guard is trivial):
    {"sha":"d9a6dd2","at":"2026-07-06T...","subject":"...","changes":[
        {"kind":"toolkit-change","path":".agents/commands/foo.md","status":"A","needs":"index-row+sync"}, ...]}
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

JOURNAL_BASENAME = ".maps-journal.jsonl"          # beside the committed anchor, in docs/
ARCHIVE_BASENAME = ".maps-journal-archive.jsonl"  # consumed lines roll here (a MOVE, never a delete)
STATE_BASENAME = ".maps-state.json"               # check_maps' anchor: {"reconciled_at": "<sha7>"}

# Session-folder shape (mirrors check_maps.SESSION_FOLDER_RE) — a depth-3 _artifacts INDEX row target.
SESSION_FOLDER_RE = re.compile(r"^(story-|\d{4}-|tea-|wave-|close-out-|epic-|autopilot-)")

# Top-level segments that never warrant a curated purpose line / map row (mirrors check_maps skip sets).
TOPLEVEL_SKIP = {
    "node_modules", "venv", "env", "__pycache__", "auth_keys", "_artifacts", "_claude_artifacts",
    "_opencode_artifacts", "_test_scripts", "_debug_audio", "dist", "build", "__tests__", "_bmad",
    "_my_resources", ".git", ".gitnexus", ".claude", ".opencode", ".githooks", "Projects",
}
# Toolkit families whose .md files each need an INDEX row (+ /sync-agents to mirror the copies).
TOOLKIT_FAMILIES = ("commands", "skills", "workflows", "rules")

STATUS_WORD = {"A": "added", "D": "deleted", "M": "modified", "R": "renamed", "C": "copied"}


def sh(args, cwd):
    try:
        out = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
        return out.stdout.rstrip("\n"), out.returncode
    except FileNotFoundError:
        return "", 127


def find_root(start):
    """Workspace root: the script lives at <root>/.agents/scripts/ (master + vendored)."""
    s = Path(start).resolve()
    return s.parent.parent.parent if s.parent.parent.name == ".agents" else s.parent.parent


def journal_path(root):
    return root / "docs" / JOURNAL_BASENAME


def top_level_dirs(root):
    try:
        return {p.name for p in root.iterdir() if p.is_dir()}
    except OSError:
        return set()


# --- classification (from a single --name-status entry; no disk state needed) -------------------------
def classify(status, path, newpath, top_dirs):
    """Map one changed path to a map-relevant hint, or None if it doesn't touch the nav surface.
    Deliberately biased toward RECALL: the journal is a hint the consumer re-verifies against disk,
    so an over-flag is cheap and an under-flag is the costly miss."""
    st = status[0]  # 'R100' -> 'R'
    segs = [s for s in path.split("/") if s]
    if not segs:
        return None
    head = segs[0]

    # toolkit .md add/delete/rename under .agents/<family>/ -> needs an INDEX row (+ /sync-agents)
    if head == ".agents" and len(segs) >= 3 and segs[1] in TOOLKIT_FAMILIES \
            and path.endswith(".md") and segs[-1].lower() != "index.md" and st in "ADR":
        return {"kind": "toolkit-change", "path": path, "status": st, "needs": "index-row+sync"}

    # a new session folder under _artifacts/ -> needs a depth-3 INDEX row
    if head == "_artifacts" and st == "A":
        for seg in segs[1:-1]:                      # any intermediate dir that looks like a session folder
            if SESSION_FOLDER_RE.match(seg):
                return {"kind": "session-added", "path": path, "status": st, "needs": "depth3-index-row"}
        return None                                 # other _artifacts writes are ledger-managed, not map drift

    if head in TOPLEVEL_SKIP or head.startswith("."):
        return None

    # rename touching a documented top-level dir -> a curated/INDEX row may now be stale
    if st == "R":
        return {"kind": "rename", "path": path, "newpath": newpath, "status": st,
                "needs": "map/index-row-may-be-stale"}
    # delete of a top-level-rooted path -> may leave a dead map/INDEX row
    if st == "D":
        return {"kind": "delete", "path": path, "status": st, "needs": "map/index-row-may-be-dead"}
    # add under a real top-level dir -> candidate new top-level folder (consumer verifies it's truly new)
    if st == "A" and len(segs) >= 2 and head in top_dirs:
        return {"kind": "toplevel-added", "path": path, "status": st, "needs": "maybe-purpose-line"}
    return None


def parse_name_status(raw):
    """Yield (status, path, newpath|None) from `git ... --name-status -z`-free plain output."""
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        # git rename/copy format: "R100 <old> <new>". Report OLD as the path (the stale map row points at
        # it) and NEW as newpath, so consumers read "OLD → NEW".
        if status.startswith(("R", "C")) and len(parts) >= 3:
            yield status, parts[1], parts[2]
        else:
            yield status, parts[1] if len(parts) > 1 else "", None


# --- --commit: append one classified line ------------------------------------------------------------
def record_commit(root, ref):
    sha, rc = sh(["git", "rev-parse", "--short", ref], root)
    if rc != 0 or not sha:
        return 0  # not a git repo / bad ref — recorder never fails a commit
    # first commit has no parent: diff against the empty tree so the initial import still classifies.
    parent, prc = sh(["git", "rev-parse", "--verify", "--quiet", f"{ref}^"], root)
    base = parent if prc == 0 and parent else "4b825dc642cb6eb9a060e54bf8d69288fbee4904"  # git empty tree
    raw, rc = sh(["git", "diff", "--name-status", "-M", base, ref], root)
    if rc != 0:
        return 0
    top_dirs = top_level_dirs(root)
    changes = []
    for status, path, newpath in parse_name_status(raw):
        c = classify(status, path, newpath, top_dirs)
        if c:
            changes.append(c)
    at, _ = sh(["git", "log", "-1", "--format=%cI", ref], root)      # committer date (deterministic, not wall-clock)
    subject, _ = sh(["git", "log", "-1", "--format=%s", ref], root)
    line = {"sha": sha, "at": at, "subject": subject[:120], "changes": changes}
    jp = journal_path(root)
    jp.parent.mkdir(parents=True, exist_ok=True)
    with jp.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")
    return 0


# --- shared journal reader ---------------------------------------------------------------------------
def read_journal(root):
    jp = journal_path(root)
    if not jp.exists():
        return []
    out = []
    for ln in jp.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            out.append(json.loads(ln))
        except json.JSONDecodeError:
            continue  # tolerate a torn line rather than crash the nag
    return out


def read_anchor(root):
    sp = root / "docs" / STATE_BASENAME
    if sp.exists():
        try:
            return json.loads(sp.read_text(encoding="utf-8")).get("reconciled_at")
        except Exception:
            return None
    return None


def since_anchor(entries, anchor):
    """Lines AFTER the anchor line. If the anchor sha isn't in the journal (predates it / rebased),
    fail-safe by returning ALL entries — better to over-show than to hide drift."""
    if not anchor:
        return entries
    for i, e in enumerate(entries):
        if e.get("sha") == anchor:
            return entries[i + 1:]
    return entries


# --- --nag: classified tail since the anchor, freshness-guarded (SessionStart) ------------------------
NEEDS_LABEL = {
    "index-row+sync": "needs an INDEX row + /sync-agents",
    "depth3-index-row": "needs a depth-3 _artifacts INDEX row",
    "map/index-row-may-be-stale": "a map/INDEX row may now be stale",
    "map/index-row-may-be-dead": "may leave a dead map/INDEX row",
    "maybe-purpose-line": "candidate new top-level folder — may need a purpose line",
}


def nag(root):
    entries = read_journal(root)
    if not entries:
        return 0  # no journal yet — silent; the other SessionStart checks still run
    head, rc = sh(["git", "rev-parse", "--short", "HEAD"], root)
    last = entries[-1].get("sha")
    # FRESHNESS GUARD: if the journal's newest line isn't HEAD, a commit landed without the recorder.
    # Don't trust a partial cache — tell the reader to lean on the ground-truth linter instead.
    if rc == 0 and head and last != head:
        print(f"⚠️  maps-journal is behind HEAD (recorded {last}, HEAD {head}) — "
              "a commit bypassed the recorder. Trust `check_maps.py`, not this cache, until re-synced.")
        return 0
    fresh = since_anchor(entries, read_anchor(root))
    flat = [c for e in fresh for c in e.get("changes", [])]
    if not flat:
        return 0  # nothing map-relevant since the last reconcile — stay quiet
    # de-dupe by (kind, path) so a path touched across several commits shows once
    seen, items = set(), []
    for c in flat:
        key = (c.get("kind"), c.get("path"))
        if key not in seen:
            seen.add(key)
            items.append(c)
    print(f"\U0001f5fa️  maps-journal: {len(items)} map-relevant change(s) since last reconcile "
          "(run /1_update-maps to apply the prose fixes):")
    for c in items:
        label = NEEDS_LABEL.get(c.get("needs"), c.get("needs", ""))
        arrow = f" → {c['newpath']}" if c.get("kind") == "rename" and c.get("newpath") else ""
        print(f"  • [{STATUS_WORD.get(c.get('status'), c.get('status'))}] {c.get('path')}{arrow}  — {label}")
    return 0


# --- --consume: roll consumed lines into the archive (called by check_maps --set-anchor) --------------
def consume(root, upto_sha):
    """MOVE (never delete) every journal line up to and including <upto_sha> into the archive, keeping
    the tail live. Mirrors the workflow's 'prune is a move' rule. Idempotent + safe if the sha is absent
    (then nothing is consumed). Returns the number of lines archived."""
    entries = read_journal(root)
    if not entries or not upto_sha:
        return 0
    short = upto_sha[:7]
    cut = None
    for i, e in enumerate(entries):
        if (e.get("sha") or "")[:7] == short:
            cut = i
    if cut is None:
        return 0  # anchor not in the journal — leave everything live (fail-safe)
    consumed, kept = entries[:cut + 1], entries[cut + 1:]
    jp = journal_path(root)
    ap = root / "docs" / ARCHIVE_BASENAME
    with ap.open("a", encoding="utf-8") as f:
        for e in consumed:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    jp.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in kept), encoding="utf-8")
    return len(consumed)


def main():
    # Windows consoles default to cp1252, which can't encode the nag's emoji -> UnicodeEncodeError would
    # crash the SessionStart hook. Force UTF-8 (replace on the rare undecodable byte) so output is safe
    # in Git Bash, PowerShell, and cmd alike.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Commit-time drift recorder for the repo-map + INDEX system")
    ap.add_argument("--root", default=None, help="workspace root (default: inferred from this script's location)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--commit", metavar="REF", help="classify REF's changes and append one journal line (the post-commit hook)")
    g.add_argument("--nag", action="store_true", help="print the classified tail since the anchor (SessionStart); always exits 0")
    g.add_argument("--consume", metavar="SHA", help="roll journal lines up to SHA into the archive (called by --set-anchor)")
    args = ap.parse_args()
    root = Path(args.root).resolve() if args.root else find_root(__file__)

    if args.commit:
        sys.exit(record_commit(root, args.commit))
    if args.nag:
        sys.exit(nag(root))
    if args.consume:
        n = consume(root, args.consume)
        print(f"maps-journal: archived {n} consumed line(s) -> docs/{ARCHIVE_BASENAME}")
        sys.exit(0)


if __name__ == "__main__":
    main()
