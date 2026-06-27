#!/usr/bin/env python3
"""check_maps.py — deterministic drift linter for the repo map + INDEX.md files (ANY workspace).

The detection engine behind the /1_update-maps workflow. It does ONLY the checks a script can do
reliably (no judgment) and prints a structured report; the agent workflow supplies the prose fixes
(purpose lines, INDEX categorisation, the actual prune). Exit code is non-zero when drift is found.

GENERIC BY DESIGN (one tool, every workspace). It used to be home-base-only; it now detects the
workspace MODE and applies the right paths from the PATH CONTRACT in `workspace-standard.md`, so the
SAME script reconciles the lobby OR any conformant project. Point it at a workspace with --root:
    python .agents/scripts/check_maps.py                                # the repo holding this script
    python .agents/scripts/check_maps.py --root Projects/AGY_AVIATIONCHAT
    python .agents/scripts/check_maps.py --root Projects/Fresh_Workspace_BMAD
    python .agents/scripts/check_maps.py --set-anchor                   # record HEAD as the reconciled baseline

Mode detection (PATH CONTRACT, two columns):
  - HOME BASE  — has a `Projects/` dir. Map at `_docs/repo-map.md`; continuity briefs at
                 `_artifacts/<bucket>/active-context.md`; `Projects/` are separate repos (never descended).
  - PROJECT    — no `Projects/`. Map at `docs/repo-map.md`. A BMAD project (`_bmad-output/` present) keeps
                 its continuity brief at `_bmad-output/active-context/active-context.md` and uses `_artifacts/`
                 for session *history*; a non-BMAD project uses `_artifacts/active-context.md`.

Six checks (1-4 fatal drift; 5 non-fatal hint; 6 fatal):
  1. AUTO-block freshness   — regenerate the map's AUTO body in memory (mode-preserving) and diff.
  2. Path existence         — every backticked table-row path in the map CURATED block + each INDEX.md resolves.
  3. Folder coverage        — every real TOP-LEVEL folder appears in the map text.
  4. Git baseline           — diff HEAD against the last reconciled SHA (<docs>/.maps-state.json); list renames.
  5. Context hygiene        — NON-FATAL nag: continuity brief over the prune window / INDEX.md over the row cap.
  6. Structure conformance  — the workspace carries the standard files in the standard places (the contract gate).
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Import the generator that lives beside us so the freshness check uses the exact same logic.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_repo_map as grm  # noqa: E402

# Dirs we never descend into when hunting for INDEX.md files. Projects/ are separate repos (own maps,
# own linter). _my_resources is PROTECTED (don't even read); _bmad is BMAD-regenerated. Rest is noise.
SCAN_IGNORES = {
    ".git", ".venv", "venv", "env", "__pycache__", "node_modules", ".next", "dist", "build",
    ".pytest_cache", ".turbo", ".cache", "coverage", "_my_resources", "_bmad", "Projects",
}
# Extra ignores fed to the generator's regen — MUST match the documented invocation in the repo-map
# header. Home base uses `Projects,_my_resources`; a project's header may declare its own (e.g. `_bmad`).
# Override per workspace with --ignore; the default suits the home base.
DEFAULT_REGEN_IGNORE = "Projects,_my_resources"

# Top-level folders that are intentionally NOT named in the map (mirrors check-repo-map-drift.ps1 $skip).
TOPLEVEL_SKIP = {
    "node_modules", "venv", "env", "__pycache__", "auth_keys",
    "_artifacts", "_claude_artifacts", "_opencode_artifacts",
    "_test_scripts", "_debug_audio", "dist", "build", "__tests__",
    "_bmad", "_my_resources",
}

STATE_BASENAME = ".maps-state.json"   # sits in the docs folder beside the repo-map (mode-dependent dir)

# Append-only NARRATIVE ledgers: rows are immutable history (cross-repo + renamed/deleted paths by
# design), so path-existence linting is a category error here — old rows SHOULD keep their old paths.
NARRATIVE_LEDGERS = {"_artifacts/INDEX.md"}

# A backticked token is disqualified as a checkable path if it carries any of this shape-noise
# (whitespace = a command/prose fragment; braces/angles/glob = a pattern, not a literal path).
SHAPE_NOISE = re.compile(r"[\s{}<>§*…]")

# --- context-hygiene thresholds (the prune window; see workspace-standard.md "Context hygiene") -------
PRUNE_KEEP_BLOCKS = 10      # newest dated blocks to keep in a continuity active-context.md
PRUNE_NAG_BLOCKS = 12       # hint to prune once a brief exceeds this many blocks (hysteresis, not every session)
PRUNE_NAG_LINES = 220       # fallback signal when a brief has no dated blocks to count
INDEX_KEEP_ROWS = 25        # newest session rows to keep in INDEX.md
INDEX_NAG_ROWS = 35         # hint to archive older rows once past this

BLOCK_RE = re.compile(r"^\s*\*\*\d{4}-\d{2}-\d{2}", re.M)         # a dated PRIME-STATE session block
INDEX_ROW_RE = re.compile(r"^\|\s*\d{4}-\d{2}-\d{2}\s*\|", re.M)  # a dated INDEX.md session row


def sh(args, cwd):
    try:
        out = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
        return out.stdout.strip(), out.returncode
    except FileNotFoundError:
        return "", 127


# --- mode + path detection (genericity: one tool, any conformant workspace) ---------------------------
def find_map_path(root):
    """Repo-map lives at _docs/repo-map.md (lobby) or docs/repo-map.md (project). Prefer the one that exists."""
    for cand in ("_docs/repo-map.md", "docs/repo-map.md"):
        if (root / cand).exists():
            return root / cand
    # neither present yet — point at the mode-appropriate default so the 'missing' message is right
    return root / ("_docs" if (root / "Projects").is_dir() else "docs") / "repo-map.md"


def detect_mode(root):
    """(is_home, is_bmad). The home base hosts a Projects/ dir; a BMAD workspace has _bmad-output/."""
    return (root / "Projects").is_dir(), (root / "_bmad-output").is_dir()


def continuity_briefs(root, is_home, is_bmad):
    """The pickup/handoff brief(s) the prune trims — location depends on mode (see the PATH CONTRACT)."""
    found = []
    adir = root / "_artifacts"
    if is_home and adir.is_dir():
        for b in sorted(p for p in adir.iterdir() if p.is_dir() and p.name != "_archived"):
            ac = b / "active-context.md"
            if ac.exists():
                found.append(ac)
    if is_bmad:
        ac = root / "_bmad-output" / "active-context" / "active-context.md"
        if ac.exists():
            found.append(ac)
    flat = adir / "active-context.md"          # non-BMAD project-local fallback
    if flat.exists():
        found.append(flat)
    return found


# --- check 1: AUTO-block freshness -------------------------------------------------------------------
def declared_mode(map_text):
    m = re.search(r"mode=(content|auto)", map_text)
    return m.group(1) if m else "auto"


def check_auto_block(root, map_path, regen_ignore):
    text = map_path.read_text(encoding="utf-8")
    mode = declared_mode(text)
    ignores = set(grm.DEFAULT_IGNORES)
    ignores.update(x.strip() for x in regen_ignore.split(",") if x.strip())
    fresh = grm.build_auto_body(str(root), threshold=8, mode=mode, ignores=ignores)
    if grm.AUTO_START in text and grm.AUTO_END in text:
        current = grm.AUTO_START + text.split(grm.AUTO_START, 1)[1].split(grm.AUTO_END, 1)[0] + grm.AUTO_END
    else:
        return ["repo-map has no AUTO sentinels - run the generator to scaffold it"], mode
    if current.strip() == fresh.strip():
        return [], mode
    # Report which folder lines differ, not the whole block.
    cur_lines = set(current.splitlines())
    new_lines = set(fresh.splitlines())
    added = [l.strip() for l in sorted(new_lines - cur_lines) if l.strip().endswith("/")]
    removed = [l.strip() for l in sorted(cur_lines - new_lines) if l.strip().endswith("/")]
    msgs = ["AUTO block is STALE - regenerate: "
            f"python .agents/scripts/generate_repo_map.py --output {map_path.name} "
            f"--ignore {regen_ignore} --mode {mode}"]
    if added:
        msgs.append("  on disk but not in map: " + ", ".join(added[:12]))
    if removed:
        msgs.append("  in map but not on disk: " + ", ".join(removed[:12]))
    return msgs, mode


# --- check 2: path existence -------------------------------------------------------------------------
# Precision over recall: a routing TABLE row that points at a path is a *promise* ("look here"), so a dead
# one is real drift worth flagging. Prose/blockquotes narrate history & cross-repo paths — never linted.
def top_level_names(root):
    try:
        return {p.name for p in root.iterdir()}
    except OSError:
        return set()


def resolve(tok, root, base):
    """OK if it resolves relative to repo root OR to the doc's own dir (INDEX rows are often folder-relative)."""
    return (root / tok).exists() or (base / tok).exists()


def dead_paths(md_text, root, base, top_level):
    """High-confidence dead paths: backticked, multi-segment, real top-level first segment, in a table row."""
    dead = []
    for line in md_text.splitlines():
        if "|" not in line:           # table rows only — skip prose & blockquotes
            continue
        for tok in re.findall(r"`([^`]+)`", line):
            tok = re.sub(r"\s*\([^)]*\)\s*$", "", tok.strip()).rstrip("/")  # drop trailing "(§6)" etc.
            if not tok or tok.endswith("()") or SHAPE_NOISE.search(tok):
                continue
            segs = [s for s in tok.split("/") if s]
            if len(segs) < 2:                                   # single-segment = too ambiguous, skip
                continue
            if any(len(s) == 1 or re.fullmatch(r"[A-Z]", s) for s in segs):  # placeholder seg (epic-N, x/Y)
                continue
            if segs[0] not in top_level:                        # cross-repo / prose path, skip
                continue
            if not resolve(tok, root, base):
                dead.append(tok)
    return list(dict.fromkeys(dead))


def check_paths(root, md_path, top_level):
    base = md_path.parent
    rel = md_path.relative_to(root).as_posix()
    return [f"{rel}: dead path `{d}`" for d in dead_paths(md_path.read_text(encoding="utf-8"), root, base, top_level)]


# --- check 3: top-level folder coverage --------------------------------------------------------------
# Mirrors check-repo-map-drift.ps1: every real top-level folder (minus the skip set + dot-folders) must
# be named as `<folder>/` somewhere in the map.
def check_coverage(root, map_text):
    misses = []
    for child in sorted(p.name for p in root.iterdir() if p.is_dir()):
        if child in TOPLEVEL_SKIP or child.startswith("."):
            continue
        if (child + "/") not in map_text:
            misses.append(child)
    return [f"top-level folder not documented in repo-map: {m}/" for m in misses]


# --- check 4: git baseline ---------------------------------------------------------------------------
def read_anchor(state_path):
    if state_path.exists():
        try:
            return json.loads(state_path.read_text(encoding="utf-8")).get("reconciled_at")
        except Exception:
            return None
    return None


def check_git(root, state_path):
    sha = read_anchor(state_path)
    rel = state_path.relative_to(root).as_posix()
    head, rc = sh(["git", "rev-parse", "--short", "HEAD"], root)
    if rc != 0:
        return ["(not a git repo / git unavailable - skipping change detection)"], []
    if not sha:
        return [f"no baseline anchor ({rel} missing) - after reconciling, run: "
                "python .agents/scripts/check_maps.py --set-anchor"], []
    out, rc = sh(["git", "diff", "--name-status", f"{sha}..HEAD"], root)
    if rc != 0:
        return [f"baseline {sha} not found in history (rebased?) - re-anchor with --set-anchor"], []
    changes = [l for l in out.splitlines() if l.strip()]
    renames = [l for l in changes if l.startswith("R")]
    notes = [f"changes since last reconcile ({sha}..{head}): {len(changes)} files"]
    if renames:
        notes.append(f"  !! {len(renames)} RENAME(S) - most likely to have broken map/INDEX paths:")
        notes.extend("    " + r for r in renames[:15])
    return notes, changes


def set_anchor(root, state_path):
    head, rc = sh(["git", "rev-parse", "--short", "HEAD"], root)
    if rc != 0:
        print("cannot set anchor: not a git repo", file=sys.stderr)
        return 1
    date, _ = sh(["git", "log", "-1", "--format=%cs"], root)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps({"reconciled_at": head, "reconciled_date": date}, indent=2) + "\n", encoding="utf-8")
    print(f"baseline anchored at {head} ({date}) -> {state_path.relative_to(root).as_posix()}")
    return 0


def find_indexes(root):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SCAN_IGNORES and not d.startswith(".")]
        for f in filenames:
            if f.lower() == "index.md":
                found.append(Path(dirpath) / f)
    return sorted(found)


# --- check 5: context hygiene (NON-FATAL hint — the prune nag) ----------------------------------------
def check_context_hygiene(root, is_home, is_bmad):
    hints = []
    for ac in continuity_briefs(root, is_home, is_bmad):
        text = ac.read_text(encoding="utf-8")
        blocks = len(BLOCK_RE.findall(text))
        lines = text.count("\n") + 1
        rel = ac.relative_to(root).as_posix()
        if blocks >= PRUNE_NAG_BLOCKS:
            hints.append(f"{rel}: {blocks} session blocks - prune to newest ~{PRUNE_KEEP_BLOCKS} via /1_update-maps")
        elif blocks == 0 and lines >= PRUNE_NAG_LINES:
            hints.append(f"{rel}: {lines} lines (no dated blocks detected) - review length")
    idx = root / "_artifacts" / "INDEX.md"
    if idx.exists():
        rows = len(INDEX_ROW_RE.findall(idx.read_text(encoding="utf-8")))
        if rows >= INDEX_NAG_ROWS:
            hints.append(f"_artifacts/INDEX.md: {rows} session rows - archive older past ~{INDEX_KEEP_ROWS} to INDEX-archive.md")
    return hints


# --- check 6: structure conformance (the contract gate — 'verify structures stay standard') -----------
def check_conformance(root, is_home, is_bmad, map_path):
    """Confirm the workspace carries the standard files in the standard places (workspace-standard.md PATH CONTRACT)."""
    docs = map_path.parent  # _docs (lobby) or docs (project)
    missing = []

    def need(rel, label):
        if not (root / rel).exists():
            missing.append(f"{label} (`{rel}`)")

    need("AGENTS.md", "brain")
    need("CLAUDE.md", "adapter")
    need("GEMINI.md", "adapter")
    need(".agents", "toolkit dir")
    need(".agents/scripts/check_maps.py", "maintenance script")
    need(".agents/scripts/generate_repo_map.py", "map generator")
    need("_my_resources/open_tasks/todo_list.md", "open-tasks list")
    need("_artifacts/INDEX.md", "session ledger")
    if not map_path.exists():
        missing.append(f"navigation index (`{map_path.relative_to(root).as_posix()}`)")
    if not (docs / "workspace-standard.md").exists():
        missing.append(f"structure standard (`{(docs / 'workspace-standard.md').relative_to(root).as_posix()}`)")
    if not continuity_briefs(root, is_home, is_bmad):
        loc = "_bmad-output/active-context/active-context.md" if is_bmad else "_artifacts/<bucket>/active-context.md"
        missing.append(f"continuity brief (expected `{loc}`)")
    return [f"NOT conformant - missing {m}" for m in missing]


def main():
    here = Path(__file__).resolve()
    # Workspace root, robust to vendored location: the script lives at `<root>/.agents/scripts/` (master +
    # vendored) or a legacy `<root>/scripts/`. Strip the scripts dir, and the `.agents` dir if present, to
    # land on the root — so the SAME file works from either location (decision: byte-identical synced copies).
    _scripts = here.parent
    default_root = _scripts.parent.parent if _scripts.parent.name == ".agents" else _scripts.parent
    ap = argparse.ArgumentParser(description="Drift linter for repo-map + INDEX.md (any conformant workspace)")
    ap.add_argument("--root", default=str(default_root), help="workspace to lint (lobby or a Projects/<name>)")
    ap.add_argument("--ignore", default=DEFAULT_REGEN_IGNORE, help="extra dirs for the regen comparison")
    ap.add_argument("--set-anchor", action="store_true", help="record HEAD as the reconciled baseline and exit")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    is_home, is_bmad = detect_mode(root)
    map_path = find_map_path(root)
    state_path = map_path.parent / STATE_BASENAME
    mode_label = "home base" if is_home else ("BMAD project" if is_bmad else "project")

    if args.set_anchor:
        sys.exit(set_anchor(root, state_path))

    top_level = top_level_names(root)
    drift = {}

    if map_path.exists():
        map_text = map_path.read_text(encoding="utf-8")
        drift["AUTO block freshness"], _ = check_auto_block(root, map_path, args.ignore)
        # path check on the CURATED block only (the AUTO block is machine-generated, trusted)
        curated = map_text.split(grm.AUTO_START)[0] if grm.AUTO_START in map_text else map_text
        drift["repo-map paths"] = [f"repo-map.md (CURATED): dead path `{d}`"
                                   for d in dead_paths(curated, root, map_path.parent, top_level)]
        drift["folder coverage"] = check_coverage(root, map_text)
    else:
        drift["repo-map"] = [f"missing: {map_path.relative_to(root).as_posix()}"]

    index_problems = []
    for idx in find_indexes(root):
        if idx.relative_to(root).as_posix() in NARRATIVE_LEDGERS:
            continue  # immutable narrative ledger — don't lint historical paths
        index_problems.extend(check_paths(root, idx, top_level))
    drift["INDEX.md paths"] = index_problems

    drift["structure conformance"] = check_conformance(root, is_home, is_bmad, map_path)

    git_notes, _ = check_git(root, state_path)
    hygiene = check_context_hygiene(root, is_home, is_bmad)

    # ---- report ----
    print("=" * 78)
    print(f"MAP & INDEX DRIFT LINT  ({mode_label}: {root.name})")
    print("=" * 78)
    print("\n[git] change detection")
    for n in git_notes:
        print("  " + n)

    has_drift = False
    for title, problems in drift.items():
        print(f"\n[{title}]")
        if problems:
            has_drift = True
            for p in problems:
                print("  [x] " + p)
        else:
            print("  [ok] clean")

    # context hygiene is a NON-FATAL nag — it never sets the exit code (semi-automated prune nudge)
    print("\n[context hygiene]  (hint only - does not fail the lint)")
    if hygiene:
        for h in hygiene:
            print("  [hint] " + h)
    else:
        print("  [ok] continuity brief + INDEX within the prune window")

    print("\n" + "=" * 78)
    if has_drift:
        print("DRIFT FOUND - run /1_update-maps to reconcile (it supplies the prose a script can't).")
        sys.exit(1)
    print("All maps & INDEXes agree with disk. [ok]")
    sys.exit(0)


if __name__ == "__main__":
    main()
