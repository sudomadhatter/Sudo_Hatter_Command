#!/usr/bin/env python3
"""check_maps.py — deterministic drift linter for the repo map + INDEX.md files (HOME BASE).

The detection engine behind the /1_update-maps workflow. It does ONLY the checks a script can do
reliably (no judgment) and prints a structured report; the agent workflow supplies the prose fixes
(purpose lines, INDEX categorisation). Exit code is non-zero when drift is found, so it can gate CI
or back the SessionStart hook.

Home-base specifics (this is the LOBBY, not an app repo):
  - The map lives at `_docs/repo-map.md` (note the underscore), generated mode=content with
    `--ignore Projects,_my_resources`.
  - `Projects/` are SEPARATE git repos — each has its own repo-map + its own /1_update-maps. This
    linter never descends into them (coverage + INDEX scan both skip `Projects`).
  - There is no vendored `scripts/` copy here: the home base runs this master directly from
    `.agents/scripts/`. `generate_repo_map.py` lives beside it, so the freshness check reuses it.

Four checks:
  1. AUTO-block freshness  — regenerate _docs/repo-map.md's AUTO body in memory (mode-preserving) and
                             compare; any diff means the folder tree moved since the map was generated.
  2. Path existence        — every backticked path in the repo-map CURATED tables and in each INDEX.md
                             must resolve on disk (catches reverse drift: map points at a moved/dead path).
  3. Folder coverage       — every real TOP-LEVEL folder must appear in the map text (catches forward
                             drift: new folder nobody documented). Mirrors check-repo-map-drift.ps1.
  4. Git baseline          — diff HEAD against the last reconciled SHA (_docs/.maps-state.json) and list
                             adds/deletes/RENAMES since then. Renames are the usual cause of dead paths.
                             `--set-anchor` records the current HEAD as the new baseline.

Run from anywhere (root auto-detected as the repo holding .agents/):
    python .agents/scripts/check_maps.py
    python .agents/scripts/check_maps.py --set-anchor   # after a clean reconcile, record the baseline
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
# header (`--ignore Projects,_my_resources`), or the freshness check will false-positive.
DEFAULT_REGEN_IGNORE = "Projects,_my_resources"

# Top-level folders that are intentionally NOT named in the map (mirrors check-repo-map-drift.ps1 $skip).
TOPLEVEL_SKIP = {
    "node_modules", "venv", "env", "__pycache__", "auth_keys",
    "_artifacts", "_claude_artifacts", "_opencode_artifacts",
    "_test_scripts", "_debug_audio", "dist", "build", "__tests__",
    "_bmad", "_my_resources",
}

STATE_FILE = "_docs/.maps-state.json"

# Append-only NARRATIVE ledgers: rows are immutable history (cross-repo + renamed/deleted paths by
# design), so path-existence linting is a category error here — old rows SHOULD keep their old paths.
# Routing maps (repo-map curated tables) are still linted; these prose ledgers are not.
NARRATIVE_LEDGERS = {"_artifacts/INDEX.md"}

# A backticked token is disqualified as a checkable path if it carries any of this shape-noise
# (whitespace = a command/prose fragment; braces/angles/glob = a pattern, not a literal path).
SHAPE_NOISE = re.compile(r"[\s{}<>§*…]")


def sh(args, cwd):
    try:
        out = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
        return out.stdout.strip(), out.returncode
    except FileNotFoundError:
        return "", 127


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
            f"python .agents/scripts/generate_repo_map.py --output _docs/repo-map.md "
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
# be named as `<folder>/` somewhere in the map. The home-base map documents top-level folders, not the
# contents of code roots, so coverage is a top-level check (not an app's backend/frontend walk).
def check_coverage(root, map_text):
    misses = []
    for child in sorted(p.name for p in root.iterdir() if p.is_dir()):
        if child in TOPLEVEL_SKIP or child.startswith("."):
            continue
        if (child + "/") not in map_text:
            misses.append(child)
    return [f"top-level folder not documented in repo-map: {m}/" for m in misses]


# --- check 4: git baseline ---------------------------------------------------------------------------
def read_anchor(root):
    p = root / STATE_FILE
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8")).get("reconciled_at")
        except Exception:
            return None
    return None


def check_git(root):
    sha = read_anchor(root)
    head, rc = sh(["git", "rev-parse", "--short", "HEAD"], root)
    if rc != 0:
        return ["(not a git repo / git unavailable - skipping change detection)"], []
    if not sha:
        return [f"no baseline anchor ({STATE_FILE} missing) - after reconciling, run: "
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


def set_anchor(root):
    head, rc = sh(["git", "rev-parse", "--short", "HEAD"], root)
    if rc != 0:
        print("cannot set anchor: not a git repo", file=sys.stderr)
        return 1
    date, _ = sh(["git", "log", "-1", "--format=%cs"], root)
    (root / STATE_FILE).write_text(
        json.dumps({"reconciled_at": head, "reconciled_date": date}, indent=2) + "\n", encoding="utf-8")
    print(f"baseline anchored at {head} ({date}) -> {STATE_FILE}")
    return 0


def find_indexes(root):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SCAN_IGNORES and not d.startswith(".")]
        for f in filenames:
            if f.lower() == "index.md":
                found.append(Path(dirpath) / f)
    return sorted(found)


def main():
    here = Path(__file__).resolve()
    # Master lives at <repo>/.agents/scripts/check_maps.py → repo root is two parents up from scripts/.
    default_root = here.parents[2]
    ap = argparse.ArgumentParser(description="Drift linter for repo-map + INDEX.md (home base)")
    ap.add_argument("--root", default=str(default_root))
    ap.add_argument("--ignore", default=DEFAULT_REGEN_IGNORE, help="extra dirs for the regen comparison")
    ap.add_argument("--set-anchor", action="store_true", help="record HEAD as the reconciled baseline and exit")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    if args.set_anchor:
        sys.exit(set_anchor(root))

    map_path = root / "_docs" / "repo-map.md"
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
        drift["repo-map"] = [f"missing: {map_path}"]

    index_problems = []
    for idx in find_indexes(root):
        if idx.relative_to(root).as_posix() in NARRATIVE_LEDGERS:
            continue  # immutable narrative ledger — don't lint historical paths
        index_problems.extend(check_paths(root, idx, top_level))
    drift["INDEX.md paths"] = index_problems

    git_notes, _ = check_git(root)

    # ---- report ----
    print("=" * 78)
    print("MAP & INDEX DRIFT LINT (home base)")
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

    print("\n" + "=" * 78)
    if has_drift:
        print("DRIFT FOUND - run /1_update-maps to reconcile (it supplies the prose a script can't).")
        sys.exit(1)
    print("All maps & INDEXes agree with disk. [ok]")
    sys.exit(0)


if __name__ == "__main__":
    main()
