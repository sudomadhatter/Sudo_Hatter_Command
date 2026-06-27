#!/usr/bin/env python3
"""generate_doc_graph.py - markdown doc-wiring graph for the .agents/ toolkit.

Closes the gap that GitNexus is structurally blind to: GitNexus extracts headings, not
doc-to-doc references, so the prose toolkit (rules / workflows / skills / commands) shows
few cross-file edges (see the note in docs/repo-map.md). This script reads every .md under
a root, extracts the references that actually dominate these files -- markdown links
`](rules/x.md)` and inline/backtick path tokens `router.md`, `.agents/rules/x.md` -- resolves
each against the real file set, and emits a deterministic, no-LLM, ~$0 wiring map. There are
NO wikilinks (`[[ ]]`) in .agents/ (those live only in the memory files), so they are skipped.

It doubles as a broken-link detector: a reference that resolves to nothing on disk is reported
as DANGLING (this is how the stale `.agent/` (singular) refs surface). A reference to a real
file OUTSIDE the indexed scope (e.g. the lobby `router.md`) is reported as EXTERNAL, not broken,
so the dangling list stays trustworthy.

Outputs (mirrors generate_repo_map.py's sentinel-splice contract):
  - <lobby>/docs/doc-graph.md   human-readable: hubs, orphans, dangling, ambiguous, externals.
    Only the region between <!-- DOC-GRAPH:AUTO-START --> / <!-- DOC-GRAPH:AUTO-END --> is rewritten;
    the curated header above it is never touched. A scaffold is created on first run.
  - <lobby>/docs/doc-graph.json machine-readable {nodes, edges, dangling, external, ambiguous}.

Master copy lives in .agents/scripts/ ; run from the lobby. ASCII-only on purpose (PowerShell 5.1
reads BOM-less files as Windows-1252). stdlib only.
"""
import argparse
import json
import os
import posixpath
import re
from collections import defaultdict
from pathlib import Path

# Nested dirs never walked. The root (.agents/) itself is always entered; only its sub-entries
# are filtered. Dot-entries are skipped automatically (covers .gitnexus, .git, ...).
DEFAULT_IGNORES = {
    ".git", ".venv", "venv", "env", "__pycache__", "node_modules",
    ".gitnexus", "_artifacts", "dist", "build", ".pytest_cache", ".cache",
}

AUTO_START = "<!-- DOC-GRAPH:AUTO-START -->"
AUTO_END = "<!-- DOC-GRAPH:AUTO-END -->"
CURATED_START = "<!-- DOC-GRAPH:CURATED-START -->"
CURATED_END = "<!-- DOC-GRAPH:CURATED-END -->"

# A path token ending in .md, not glued to a surrounding word. Allows / and \ so both
# `.agents/rules/x.md` and `.agents\rules\x.md` are caught; backslashes normalized later.
TOKEN_RE = re.compile(r"(?<![\w./\\-])([\w./\\-]+\.md)\b")
# Markdown link target: the path inside ](...), up to the first space or close paren.
LINK_RE = re.compile(r"\]\(\s*<?([^)>\s]+)")


def collect_md(root, ignores):
    """Return sorted list of .md paths relative to root (posix)."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignores and not d.startswith(".")]
        for fn in filenames:
            if fn.lower().endswith(".md"):
                rel = os.path.relpath(os.path.join(dirpath, fn), root)
                out.append(rel.replace(os.sep, "/"))
    return sorted(out)


def clean_target(raw):
    """Normalize a raw reference to a comparable posix .md path, or None to drop it."""
    t = raw.strip().strip("\"'").rstrip(">")
    t = t.split("#", 1)[0]                       # drop anchor
    t = t.replace("\\", "/")
    if not t.lower().endswith(".md"):
        return None
    if "://" in t or t.startswith("http") or t.startswith("mailto:"):
        return None                              # external URL, not doc wiring
    if "*" in t or " " in t:
        return None
    if t.startswith("./"):
        t = t[2:]
    return t


def extract_refs(text):
    """All cleaned .md targets in a file, tagged kind ('link' wins over 'ref')."""
    refs = {}
    for m in TOKEN_RE.finditer(text):
        t = clean_target(m.group(1))
        if t:
            refs.setdefault(t, "ref")
    for m in LINK_RE.finditer(text):
        t = clean_target(m.group(1))
        if t:
            refs[t] = "link"                     # link overrides a bare ref
    return refs


def resolve(target, source_rel, scope_files, by_basename, lobby_root, root):
    """(status, value) where status in resolved|ambiguous|external|dangling."""
    src_dir = posixpath.dirname(source_rel)
    candidates = [
        posixpath.normpath(posixpath.join(src_dir, target)),     # relative to source file
        posixpath.normpath(target),                              # relative to root
    ]
    for prefix in (".agents/", "agents/"):                       # refs that spell the full lobby path
        if target.startswith(prefix):
            candidates.append(posixpath.normpath(target[len(prefix):]))
    for cand in candidates:
        if cand in scope_files:
            return ("resolved", cand)
    hits = by_basename.get(posixpath.basename(target), [])
    if len(hits) == 1:
        return ("resolved", hits[0])
    if len(hits) > 1:
        return ("ambiguous", hits)
    # not in scope -- real file elsewhere (external) or genuinely broken (dangling)?
    for base in (lobby_root, root, root / src_dir):
        try:
            if (base / target).is_file():
                return ("external", target)
        except OSError:
            pass
    return ("dangling", target)


def build_graph(root, ignores):
    root = Path(root).resolve()
    lobby_root = root.parent if root.name == ".agents" else root
    scope_list = collect_md(str(root), ignores)
    scope_files = set(scope_list)
    by_basename = defaultdict(list)
    for rel in scope_list:
        by_basename[posixpath.basename(rel)].append(rel)

    edges, externals, danglings, ambiguous = [], [], [], []
    out_deg = defaultdict(int)
    in_deg = defaultdict(int)
    for rel in scope_list:
        in_deg.setdefault(rel, 0)
        text = (root / rel).read_text(encoding="utf-8", errors="ignore")
        for target, kind in sorted(extract_refs(text).items()):
            status, value = resolve(target, rel, scope_files, by_basename, lobby_root, root)
            if status == "resolved":
                if value == rel:
                    continue                      # self-reference
                edges.append({"from": rel, "to": value, "kind": kind})
                out_deg[rel] += 1
                in_deg[value] += 1
            elif status == "ambiguous":
                ambiguous.append({"from": rel, "target": target, "candidates": value})
            elif status == "external":
                externals.append({"from": rel, "target": value})
            else:
                danglings.append({"from": rel, "target": value})

    # dedup edges (a doc may name another doc several ways)
    seen, uniq = set(), []
    for e in edges:
        key = (e["from"], e["to"])
        if key not in seen:
            seen.add(key)
            uniq.append(e)
    edges = uniq

    nodes = [{"path": rel, "in": in_deg.get(rel, 0), "out": out_deg.get(rel, 0)} for rel in scope_list]
    # A dangling target that names a PATH (a real dir component) is a likely-broken link (signal);
    # a bare filename -- or a root-relative `/name.md`, which is a bmad output-file pattern -- is
    # usually a generated-artifact name a workflow mentions, not a link (noise).
    broken = sum(1 for d in danglings if _has_dir(d["target"]))
    return {
        "root": str(root),
        "counts": {
            "files": len(scope_list), "edges": len(edges), "external": len(externals),
            "ambiguous": len(ambiguous),
            "dangling": len(danglings), "broken_paths": broken, "unresolved_names": len(danglings) - broken,
        },
        "nodes": nodes, "edges": edges,
        "dangling": danglings, "external": externals, "ambiguous": ambiguous,
    }


CAP = 60  # max rows shown per table in the human report; full lists always live in the json


def _topdir(p):
    return p.split("/", 1)[0]


def _has_dir(target):
    """True if the target names a real directory component (signal), not a bare/`/name.md`."""
    return "/" in target.lstrip("/")


def _capped(rows):
    extra = len(rows) - CAP
    return (rows[:CAP], extra if extra > 0 else 0)


def render_auto(graph, top):
    from collections import Counter
    c = graph["counts"]
    nodes = graph["nodes"]
    hubs = sorted(nodes, key=lambda n: (-n["in"], n["path"]))[:top]

    broken = sorted((d for d in graph["dangling"] if _has_dir(d["target"])),
                    key=lambda d: (d["from"], d["target"]))
    name_counts = Counter(d["target"] for d in graph["dangling"] if not _has_dir(d["target"]))
    amb_specific = sorted((a for a in graph["ambiguous"] if len(a["candidates"]) <= 4),
                          key=lambda a: (a["from"], a["target"]))
    amb_generic = Counter(a["target"] for a in graph["ambiguous"] if len(a["candidates"]) > 4)
    orphans = [n["path"] for n in nodes if n["in"] == 0]
    orph_by_dir = Counter(_topdir(p) for p in orphans)

    L = [
        AUTO_START,
        "<!-- generated by .agents/scripts/generate_doc_graph.py -- do NOT hand-edit this block;",
        "     edit the CURATED block above. Rebuild: python .agents/scripts/generate_doc_graph.py -->",
        "",
        f"**Scope:** `{graph['root']}` | **{c['files']}** docs | **{c['edges']}** resolved edges | "
        f"**{c['broken_paths']}** broken-path refs | **{c['unresolved_names']}** bare-name refs | "
        f"**{c['ambiguous']}** ambiguous | **{c['external']}** external.",
        f"_Human summary -- tables capped at {CAP} rows; the complete lists are in `doc-graph.json`._",
        "",
        f"## Hubs (most-referenced docs, top {top})",
        "| In | Out | Doc |",
        "|---:|---:|---|",
    ]
    L += [f"| {n['in']} | {n['out']} | `{n['path']}` |" for n in hubs]

    L += ["", "## Broken-path references (a doc names a path that resolves to nothing -- likely stale)"]
    if broken:
        rows, extra = _capped(broken)
        L += ["| In doc | Broken target |", "|---|---|"]
        L += [f"| `{d['from']}` | `{d['target']}` |" for d in rows]
        if extra:
            L.append(f"| ... | _+{extra} more in doc-graph.json_ |")
    else:
        L.append("_None._")

    total_names = sum(name_counts.values())
    L += ["", f"## Unresolved bare names ({total_names} refs to {len(name_counts)} names)",
          "_Usually generated-artifact filenames a workflow mentions (e.g. `walkthrough.md`), not links._",
          "", "<details><summary>show name counts</summary>", ""]
    L += [f"- `{name}` x{n}" for name, n in name_counts.most_common()] or ["_None._"]
    L += ["", "</details>"]

    L += ["", "## Ambiguous references (bare name matches 2-4 docs)"]
    if amb_specific:
        rows, extra = _capped(amb_specific)
        L += ["| In doc | Name | Candidates |", "|---|---|---|"]
        L += [f"| `{a['from']}` | `{a['target']}` | {', '.join('`' + x + '`' for x in a['candidates'])} |"
              for a in rows]
        if extra:
            L.append(f"| ... | _+{extra} more_ | _in doc-graph.json_ |")
    else:
        L.append("_None._")
    if amb_generic:
        generic = ", ".join(f"`{nm}` x{n}" for nm, n in amb_generic.most_common(8))
        L.append(f"\n_Plus {sum(amb_generic.values())} refs to generic names omitted: {generic} ..._")

    L += ["", f"## Orphans: {len(orphans)} docs nothing in scope references (full list in doc-graph.json)",
          "_Expected for leaf docs like per-skill `SKILL.md` that are loaded by name, not linked._",
          "", "| Top-level dir | Orphans |", "|---|---:|"]
    L += [f"| `{d}/` | {n} |" for d, n in orph_by_dir.most_common()]
    L.append(AUTO_END)
    return "\n".join(L)


def scaffold():
    return "\n".join([
        "# Doc Graph - .agents/ toolkit wiring",
        "",
        CURATED_START,
        "> **Hand-edit this block.** The AUTO body below is regenerated by",
        "> `.agents/scripts/generate_doc_graph.py`. This is the doc-to-doc \"what references what\"",
        "> layer GitNexus cannot see (it extracts headings, not references). Deterministic, no LLM, ~$0.",
        "> Dangling = a reference that resolves to no file (likely broken). External = a real file",
        "> outside the indexed scope (not broken). Rebuild after editing rules/workflows.",
        CURATED_END,
        "",
    ])


def splice(output_path, auto_body):
    path = Path(output_path)
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if AUTO_START in text and AUTO_END in text:
            head = text.split(AUTO_START)[0]
            tail = text.split(AUTO_END, 1)[1]
            return head + auto_body + tail
        return text.rstrip() + "\n\n" + auto_body + "\n"
    return scaffold() + "\n" + auto_body + "\n"


def main():
    here = Path(__file__).resolve()
    default_root = here.parent.parent            # .agents/scripts/ -> .agents/
    lobby = default_root.parent
    ap = argparse.ArgumentParser(description="Generate the doc-wiring graph for the .agents/ toolkit")
    ap.add_argument("--root", default=str(default_root), help="dir to scan (default: .agents/)")
    ap.add_argument("--output", default=None, help="markdown out (default <lobby>/docs/doc-graph.md)")
    ap.add_argument("--json", default=None, help="json out (default <lobby>/docs/doc-graph.json)")
    ap.add_argument("--ignore", default="", help="comma-separated extra dir names to skip")
    ap.add_argument("--top", type=int, default=15, help="how many hubs to list")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output) if args.output else lobby / "docs" / "doc-graph.md"
    json_out = Path(args.json) if args.json else lobby / "docs" / "doc-graph.json"
    ignores = set(DEFAULT_IGNORES)
    ignores.update(x.strip() for x in args.ignore.split(",") if x.strip())

    graph = build_graph(str(root), ignores)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(splice(str(output), render_auto(graph, args.top)), encoding="utf-8")
    json_out.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    c = graph["counts"]
    print(f"doc-graph written: {output}")
    print(f"  json: {json_out}")
    print(f"  {c['files']} docs | {c['edges']} edges | {c['dangling']} dangling | "
          f"{c['external']} external | {c['ambiguous']} ambiguous")


if __name__ == "__main__":
    main()
