#!/usr/bin/env python3
"""generate_repo_map.py — hybrid repo-map generator (master copy in .agents/scripts/).

Produces the AUTO body of `docs/repo-map.md`:
  - Python files: function/class signatures via AST.
  - TS/JS files: light regex signatures (exported functions/classes/consts, interfaces/types).
  - Any directory whose file count exceeds --threshold (default 8) is COLLAPSED to one summary
    line instead of enumerating every file (this is what keeps data/asset dirs from bloating the
    map, and makes a content workspace degrade to a clean folder-level map automatically).
  - --mode content forces folder-level only (never emits signatures) for non-code workspaces.

It NEVER touches the human-curated header: only the region between the
`<!-- REPO-MAP:AUTO-START -->` / `<!-- REPO-MAP:AUTO-END -->` sentinels is rewritten. If the output
file (or the sentinels) does not exist yet, a scaffold with a curated-header template is created.

Vendored to each project as `scripts/generate_repo_map.py`; run from the project root.
"""
import argparse
import ast
import os
import re
import subprocess
from collections import Counter
from pathlib import Path

DEFAULT_IGNORES = {
    ".git", ".venv", "venv", "env", "__pycache__", "node_modules",
    ".agent", ".agents", ".claude", ".opencode", ".gemini", ".antigravity",
    "auth_keys", "_artifacts", "_claude_artifacts", "_opencode_artifacts",
    "_test_scripts", "_debug_audio", ".pytest_cache", ".adk", ".next",
    "dist", "build", "__tests__", ".turbo", ".cache",
    # ephemeral test/build/report output — gitignored, machine-local, never worth mapping
    # (kept here so the generator AND check_maps.py's freshness regen agree — one source of truth)
    "coverage", "playwright-report", "test-results", "bin",
}

CODE_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx"}

AUTO_START = "<!-- REPO-MAP:AUTO-START -->"
AUTO_END = "<!-- REPO-MAP:AUTO-END -->"
CURATED_START = "<!-- REPO-MAP:CURATED-START -->"
CURATED_END = "<!-- REPO-MAP:CURATED-END -->"

TS_PATTERNS = [
    re.compile(r"^\s*export\s+(?:async\s+)?function\s+(\w+)"),
    re.compile(r"^\s*export\s+(?:default\s+)?class\s+(\w+)"),
    re.compile(r"^\s*export\s+const\s+(\w+)\s*[:=]"),
    re.compile(r"^\s*export\s+(?:interface|type)\s+(\w+)"),
]


def py_signatures(filepath):
    try:
        tree = ast.parse(Path(filepath).read_text(encoding="utf-8"), filename=str(filepath))
    except Exception as exc:  # unparseable file — note it, don't crash the whole run
        return [f"[unparsed: {exc.__class__.__name__}]"]
    out = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            out.append(f"class {node.name}")
            for m in node.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args = ", ".join(a.arg for a in m.args.args)
                    out.append(f"  def {m.name}({args})")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = ", ".join(a.arg for a in node.args.args)
            kw = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
            out.append(f"{kw} {node.name}({args})")
    return out


def ts_signatures(filepath):
    out = []
    try:
        for line in Path(filepath).read_text(encoding="utf-8", errors="ignore").splitlines():
            for pat in TS_PATTERNS:
                m = pat.match(line)
                if m:
                    out.append(m.group(0).strip().rstrip("{=:").strip())
                    break
    except Exception:
        return []
    return out


def signatures(filepath):
    ext = Path(filepath).suffix
    if ext == ".py":
        return py_signatures(filepath)
    if ext in {".ts", ".tsx", ".js", ".jsx"}:
        return ts_signatures(filepath)
    return []


def summarize(files):
    exts = Counter(Path(f).suffix or "<none>" for f in files)
    parts = ", ".join(f"{ext}x{n}" for ext, n in exts.most_common())
    return f"[{len(files)} files: {parts} | e.g. {files[0]}]"


def walk(directory, depth, threshold, mode, ignores, keep=None):
    """The AUTO block's tree, one directory deep per call.

    `keep` is an optional predicate on the ABSOLUTE path of each entry, FILE OR DIRECTORY. `None`
    maps the directory as it is on disk, which is what the standalone CLI is for.
    `refresh_maps.py` passes one that answers "does git have this", because the map it regenerates
    is one that gets COMMITTED: without it a scratch file nobody tracked ticked the content-mode
    file count up, `--verify` read that as a stale map and refused the push, and the `--repair` it
    printed as the remedy wrote the phantom into `docs/repo-map.md` (SCC-288 / R1).

    ⛔ IT IS ASKED ABOUT DIRECTORIES TOO, and pruning them on "the subtree produced no lines"
    instead was WRONG — measured against the real map, that dropped two tracked directories whose
    only files are dotfiles this walk already hides. Producing no visible line and not existing in
    the repository are different facts. So the predicate answers for the path itself, and a
    directory git has something under is kept even when everything in it is invisible here.
    """
    indent = "  " * depth
    lines = []
    try:
        entries = sorted(os.listdir(directory))
    except (PermissionError, OSError):
        return lines
    entries = [e for e in entries if e not in ignores and not e.startswith(".")]
    dirs = [e for e in entries if os.path.isdir(os.path.join(directory, e))]
    files = [e for e in entries if os.path.isfile(os.path.join(directory, e))]
    if keep is not None:
        dirs = [e for e in dirs if keep(os.path.join(directory, e))]
        files = [e for e in files if keep(os.path.join(directory, e))]

    for d in dirs:
        lines.append(f"{indent}{d}/")
        lines.extend(walk(os.path.join(directory, d), depth + 1, threshold, mode, ignores, keep))

    if not files:
        return lines

    collapse = (mode == "content") or (len(files) > threshold)
    if collapse:
        lines.append(f"{indent}  {summarize(files)}")
    else:
        for f in files:
            lines.append(f"{indent}  {f}")
            if mode != "content":
                for sig in signatures(os.path.join(directory, f)):
                    lines.append(f"{indent}      {sig}")
    return lines


def repo_label(root):
    """The repository's STABLE name — the same string from the main checkout and from every
    worktree cut off it.

    ⛔ THIS USED TO BE `Path(root).name`, AND THAT IS THE WORKTREE DIRECTORY BASENAME. Every lane in
    this system lives in `.claude/worktrees/<slug>/`, so the AUTO block's first line said
    `SCC-288-graph-to-projects/` from a lane and `Sudo_Hatter_Command/` from main — the map changed
    identity depending on who regenerated it. That is the long-recorded "check 1 always reports
    STALE in a worktree" false positive, whose printed remedy would ship the LANE NAME into the map
    bound for `main`; it is why `/smh-close-task-merge-tree` runs `check_maps --depth3-only` rather
    than the full lint. SCC-290 had to retire it: `refresh_maps.py --verify` runs at PUSH, and every
    push here comes from a worktree, so a per-tree label would have refused every push in the system.

    `--git-common-dir` is the shared `.git` for a worktree and the plain `.git` for a checkout, so
    its parent is the repo either way. `--path-format=absolute` is needed because git answers with a
    RELATIVE path in the main checkout. Any failure falls back to the old behaviour: a label is
    cosmetic, and this must never take a map generation down.
    """
    try:
        r = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                           cwd=str(root), capture_output=True, encoding="utf-8", text=True, timeout=15)
        if r.returncode == 0 and r.stdout.strip():
            common = Path(r.stdout.strip())
            if common.name == ".git":
                return common.parent.name
    except (OSError, subprocess.SubprocessError):
        pass
    return Path(root).name


def build_auto_body(root, threshold, mode, ignores, label=None, keep=None):
    body = [
        AUTO_START,
        "<!-- generated by scripts/generate_repo_map.py — do NOT hand-edit this block;",
        f"     mode={mode}, collapse-threshold={threshold} files. Edit the CURATED block above. -->",
        "",
        "```text",
        (label or repo_label(root)) + "/",
    ]
    body.extend(walk(root, 1, threshold, mode, ignores, keep))
    body.append("```")
    body.append(AUTO_END)
    return "\n".join(body)


def scaffold(root):
    name = Path(root).name
    return "\n".join([
        f"# Repo Map — {name}",
        "",
        CURATED_START,
        "> **Hand-edit this block.** It is the part a script cannot write. Keep it folder-level.",
        "",
        "## To find X -> look here",
        "| Need | Folder / file |",
        "|---|---|",
        "| _(fill in)_ | _(path)_ |",
        "",
        "## Knowledge map (which doc to read when)",
        "| Doc | Read it when |",
        "|---|---|",
        "| _(fill in)_ | _(trigger)_ |",
        CURATED_END,
        "",
    ])


def splice(output_path, auto_body, root):
    path = Path(output_path)
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if AUTO_START in text and AUTO_END in text:
            head = text.split(AUTO_START)[0]
            tail = text.split(AUTO_END, 1)[1]
            return head + auto_body + tail
        # file exists but no sentinels: append the auto block, leave existing content as curated
        return text.rstrip() + "\n\n" + auto_body + "\n"
    return scaffold(root) + "\n" + auto_body + "\n"


def main():
    here = Path(__file__).resolve()
    # Workspace root, robust to vendored location (same logic as check_maps.py): the script lives at
    # `<root>/.agents/scripts/` (master + vendored) or a legacy `<root>/scripts/`. Strip the scripts
    # dir, and the `.agents` dir if present, to land on the root.
    _scripts = here.parent
    default_root = _scripts.parent.parent if _scripts.parent.name == ".agents" else _scripts.parent
    ap = argparse.ArgumentParser(description="Generate the AUTO body of docs/repo-map.md")
    ap.add_argument("--root", default=str(default_root), help="workspace root to map")
    ap.add_argument("--output", default=None, help="output file (default <root>/docs/repo-map.md)")
    ap.add_argument("--threshold", type=int, default=8, help="collapse a dir with more files than this")
    ap.add_argument("--mode", choices=["auto", "content"], default="auto")
    ap.add_argument("--ignore", default="", help="comma-separated extra dir names to ignore")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output) if args.output else root / "docs" / "repo-map.md"
    ignores = set(DEFAULT_IGNORES)
    ignores.update(x.strip() for x in args.ignore.split(",") if x.strip())

    auto_body = build_auto_body(str(root), args.threshold, args.mode, ignores)
    result = splice(str(output), auto_body, str(root))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result, encoding="utf-8")
    print(f"repo-map written: {output}  (mode={args.mode}, threshold={args.threshold})")


if __name__ == "__main__":
    main()
