#!/usr/bin/env python3
"""generate_doc_graph.py - markdown doc-wiring graph for the command centre.

SCOPE (SCC-290): TWO roots by default -- `.agents/` (the toolkit: rules, commands, skills,
hooks) AND `docs/` (the procedure: SOPs, PRDs, migration guides). `docs/` was outside every
graph in this system until SCC-290, which meant `workflows_testing_SOP.md` -- the one document
the operator ever asked to have mapped -- was in none. The centre carries no CODE graph at all
(SCC-289): a code graph parses code, and this repo is markdown. This IS the centre's graph.

IDS ARE LOBBY-RELATIVE (`.agents/rules/x.md`, `docs/_scc_sops_prds/y.md`). With two roots there
is no single directory every node hangs off, and anchoring at the lobby also kills a whole class
of false "dangling" reference: a rule linking `../../docs/x.md` used to escape the scanned root
and resolve to nothing.

NO ABSOLUTE PATH REACHES THE OUTPUT. The committed json recorded the worktree it was last built
in -- one that no longer exists -- so the artifact churned on every lane and its `root` was a lie
the moment that tree was pruned. Relative roots make the output identical whoever regenerates it,
which is what lets `refresh_maps.py` stage it from a pre-commit hook and byte-verify it at push.

Closes the gap the code graph does not model: it extracts code structure, not
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

Master copy lives in .agents/scripts/ ; runnable from ANY cwd (the hook runs it from the repo
root, a human from wherever they are, and both must produce the same bytes). ASCII-only on
purpose (PowerShell 5.1 reads BOM-less files as Windows-1252). stdlib only.
"""
import argparse
import json
import os
import posixpath
import re
from collections import defaultdict
from pathlib import Path

# Nested dirs never walked. The root (.agents/) itself is always entered; only its sub-entries
# are filtered. Dot-entries are skipped automatically (covers .code-review-graph, .git, ...).
DEFAULT_IGNORES = {
    ".git", ".venv", "venv", "env", "__pycache__", "node_modules",
    ".code-review-graph", "_artifacts", "dist", "build", ".pytest_cache", ".cache",
}

DEFAULT_ROOT_NAMES = (".agents", "docs")

# Any sentinel-spliced AUTO block, in any generated doc. Stripped before a file is read for
# references -- see strip_auto().
AUTO_BLOCK_RE = re.compile(r"<!--\s*[A-Z][A-Z0-9-]*:AUTO-START\s*-->.*?"
                           r"<!--\s*[A-Z][A-Z0-9-]*:AUTO-END\s*-->", re.S)


MERMAID_FENCE_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})[ \t]*mermaid\b.*?^[ \t]*\1[ \t]*$",
                              re.S | re.M | re.I)


def strip_mermaid(text):
    """Drop ```mermaid fences before extracting references. Measured, not stylistic.

    A mermaid label breaks lines with a literal backslash-n INSIDE a quoted string:

        DOCS["docs/\\nAGENTS.md (local law) + adapters\\nworkspace-standard.md"]

    `clean_target` turns every backslash into a slash (Windows paths), so that one label emits
    `docs//nAGENTS.md`, `s/nAGENTS.md` and `adapters/nworkspace-standard.md` -- three broken-path
    refs that name no file anyone ever wrote. The SOP alone carries 45 diagrams, so this class
    dominated the docs/ root's broken list the moment SCC-290 started scanning it.

    Diagrams are pictures, not doc wiring. ⛔ Note the narrowness: only `mermaid` fences are
    stripped, never code fences generally -- a shell block naming `docs/doc-graph.md` IS a real
    reference and stays in the graph.
    """
    return MERMAID_FENCE_RE.sub("", text)


def strip_auto(text):
    """Drop every generated AUTO block before extracting references.

    ⛔ WITHOUT THIS THE GRAPH IS NOT DETERMINISTIC, and the cause is that it reads its own output:
    `docs/doc-graph.md` lives inside a scanned root, so run 2 parses run 1's tables -- hundreds of
    paths -- and emits a different graph, which run 3 parses again. Measured on the fixture: 1153
    bytes, then 1795. `refresh_maps.py --verify` byte-compares, so a generator that never settles
    refuses every push.

    Stripping the AUTO block and keeping the CURATED one is the honest cut, not a special case for
    this file: an AUTO block is a machine INVENTORY of paths, never authored wiring, and the same
    is true of `docs/repo-map.md`. The file itself stays a node and a link TARGET -- only its
    generated body stops being read as a source of edges.
    """
    return AUTO_BLOCK_RE.sub("", text)


def find_lobby(first_root):
    """The directory every node id is relative to: the repo root holding `first_root`.

    Walks up looking for `.git`, accepting a FILE as readily as a directory -- in a worktree
    (`.claude/worktrees/<slug>/`) `.git` is a file holding a `gitdir:` pointer, and a probe that
    demanded a directory would anchor the graph one level too high in exactly the trees this
    system does its work in.

    No subprocess: `git rev-parse` would be one more thing to fail on a machine with no git on
    PATH, and it reads the process cwd unless carefully bound -- and cwd-independence is a hard
    contract here (see the module docstring).

    Fallback when nothing is a repo: `.agents/`'s parent, else the root itself.
    """
    p = Path(first_root).resolve()
    for cand in (p, *p.parents):
        if (cand / ".git").exists():
            return cand
    return p.parent if p.name == ".agents" else p


AUTO_START = "<!-- DOC-GRAPH:AUTO-START -->"
AUTO_END = "<!-- DOC-GRAPH:AUTO-END -->"
CURATED_START = "<!-- DOC-GRAPH:CURATED-START -->"
CURATED_END = "<!-- DOC-GRAPH:CURATED-END -->"

# Memoized existence probe. Windows `stat` is slow under Defender real-time scanning, and the
# same bare targets (e.g. `walkthrough.md`) recur hundreds of times -- caching collapses those
# repeats so a doc-graph regen runs in seconds instead of minutes.
_ISFILE = {}


def _cached_is_file(p):
    key = str(p)
    v = _ISFILE.get(key)
    if v is None:
        if key.startswith("\\\\") or key.startswith("//"):
            v = False                            # never stat a UNC path -- is_file() blocks on SMB
        else:
            try:
                v = p.is_file()
            except OSError:
                v = False
        _ISFILE[key] = v
    return v


# A path token ending in .md, not glued to a surrounding word. Allows / and \ so both
# `.agents/rules/x.md` and `.agents\rules\x.md` are caught; backslashes normalized later.
TOKEN_RE = re.compile(r"(?<![\w./\\-])([\w./\\-]+\.md)\b")
# Markdown link target: the path inside ](...), up to the first space or close paren.
LINK_RE = re.compile(r"\]\(\s*<?([^)>\s]+)")


def collect_md(root, ignores, keep=None):
    """Return sorted list of .md paths relative to root (posix).

    `keep` is an optional predicate on the ABSOLUTE path of each candidate file. `None` keeps
    everything on disk, which is what the standalone CLI wants -- it is asked to map a directory,
    and a directory is what is there. `refresh_maps.py` passes one that answers "is this file in
    git's index", because a map it regenerates is a map that gets COMMITTED (SCC-288 / R1).
    """
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignores and not d.startswith(".")]
        for fn in filenames:
            if fn.lower().endswith(".md"):
                full = os.path.join(dirpath, fn)
                if keep is not None and not keep(full):
                    continue
                rel = os.path.relpath(full, root)
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
    if t.startswith("//"):
        return None                              # protocol-relative URL (`//host/x.md`, from a
                                                 # stripped `https:`) or UNC path -- not a doc ref.
                                                 # Left in, Windows treats `root / //host` as a UNC
                                                 # network path and is_file() blocks ~30s on SMB.
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


_SUBMODULE_PATH_RE = re.compile(r"^\s*path\s*=\s*(.+?)\s*$", re.MULTILINE)


def blind_submodules(lobby):
    """EVERY declared submodule path, lobby-relative. The lobby graph does not adjudicate links
    into another repo \u2014 in ANY checkout state.

    \u26d4 SCC-288 R9 \u00b7 `git worktree add` DOES NOT INITIALIZE SUBMODULES. Every lane in this
    system works in a worktree, so `Projects/*` is empty there while the main checkout has all ten
    populated. The generator probed those targets with a plain `is_file()`, got False, and recorded
    them as dangling \u2014 so the SAME commit counted 74 broken refs from the main checkout and 77
    from a worktree, and the commit-msg RATCHET refused every worktree commit. It was papered over
    with `[maps-ok]`, which re-baselines a number that was never real.

    \u2b50 WHY EVERY SUBMODULE AND NOT JUST THE UNINITIALIZED ONES. Excusing only the ones this
    tree cannot see fixes the refusal but leaves the count tree-dependent: measured here, main
    scored 74 while the worktree scored 71, because 3 of the 6 refs into `Projects/*` are real
    files main can stat and the worktree cannot. A commit from a worktree would then bank 71, and
    the next regeneration from the main checkout would read as a RISE to 74 and be refused \u2014
    the same bug pointing the other way. **The baseline has to mean the same thing in every tree**,
    and the only version of that which holds is: the lobby never counts a link into a submodule.

    That is also the existing design, not a new carve-out. Each project is an independent repo with
    its own map artifacts and its own `check_maps` run; lobby checks are lobby-only by
    construction. A broken link inside a project is that project's gate to catch, and it is the
    only gate that can catch it reliably.

    Read from `.gitmodules` textually \u2014 no subprocess, because cwd-independence and "git may
    not be on PATH" are hard contracts here (see the module docstring).
    """
    f = lobby / ".gitmodules"
    try:
        text = f.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return frozenset()
    subs = set()
    for raw in _SUBMODULE_PATH_RE.findall(text):
        rel = raw.replace("\\", "/").strip().strip("/")
        if rel:
            subs.add(rel)
    return frozenset(subs)


def _inside_blind(cand, blind):
    """Is this lobby-relative candidate underneath a submodule we cannot see into?"""
    for sub in blind:
        if cand == sub or cand.startswith(sub + "/"):
            return True
    return False


def resolve(target, source_rel, scope_files, by_basename, lobby, blind=frozenset()):
    """(status, value) where status in resolved|ambiguous|external|dangling|unresolvable.

    Every id in `scope_files` is LOBBY-relative, so both candidates below live in that same
    space: joining a `../../docs/x.md` onto a `.agents/rules/` source now lands on `docs/x.md`
    instead of walking off the end of the scanned root. That single change is what retires the
    biggest source of false danglings (17 of the SOP's 38 flagged refs, measured).
    """
    src_dir = posixpath.dirname(source_rel)
    candidates = [
        posixpath.normpath(posixpath.join(src_dir, target)),     # relative to the source file
        posixpath.normpath(target),                              # spelled from the lobby
    ]
    for cand in candidates:
        if cand in scope_files:
            return ("resolved", cand)
    hits = by_basename.get(posixpath.basename(target), [])
    if len(hits) == 1:
        return ("resolved", hits[0])
    if len(hits) > 1:
        return ("ambiguous", hits)
    # Not in scope -- real file elsewhere (external, e.g. a `../router.md` that escapes .agents
    # into the lobby) or genuinely broken (dangling)? Probe each base via the cached, UNC-guarded
    # stat: memoization + the UNC skip keep this fast and stop a stray `//host/x.md` URL from
    # blocking ~30s on SMB (the bug that silently froze every regen since June).
    # \u26d4 BEFORE the stat, not after. A submodule that IS checked out would otherwise answer
    # `external` here while the same ref in a worktree answered `unresolvable` -- which is the
    # tree-dependence this whole fix exists to remove. Checked on the NORMALIZED candidates,
    # because the reference is usually written relative to its source (`../../Projects/Sub/x.md`)
    # and only `candidates` has resolved that into lobby space.
    if blind:
        for cand in candidates:
            if _inside_blind(cand, blind):
                return ("unresolvable", cand)
    for base in (lobby, lobby / src_dir):
        if _cached_is_file(base / target):
            return ("external", target)
    return ("dangling", target)


# --- vendor-pack collapsing (BMAD) ------------------------------------------
# BMAD self-installs ~54 skill packs under skills/bmad-* (each ~65-70 internal md
# fragments: templates, checklists, workflow steps). Enumerating + wiring every one
# made the graph 81% bmad nodes / 94% bmad edges -- vendor noise that buried the ~183
# docs WE authored and made the broken-link report useless. We COLLAPSE each pack to
# one summary node (its root + a doc count), so an agent still sees the skill exists
# and how big it is, but its internals are neither parsed nor wired. Our docs can still
# LINK to a pack (edge -> pack node); the pack itself is a leaf we do not traverse.
def pack_root(rel):
    """If rel lives inside a collapsible vendor pack, return that pack's root dir; else None."""
    parts = rel.split("/")
    for i, seg in enumerate(parts[:-1]):          # dir segments only (never the filename)
        s = seg.lower()
        if s in ("bmad", "_bmad") or s.startswith("bmad-"):
            return "/".join(parts[: i + 1])
    return None


def canon(rel):
    """Collapse a pack-internal path to its pack root; pass any other path through."""
    return pack_root(rel) or rel


def build_graph(roots, ignores, lobby=None, exclude=(), keep=None):
    """Scan every root, anchor every id at the lobby, return the graph dict.

    `roots` may be one path or several. Ids are lobby-relative and the whole list is SORTED, so
    the artifact does not depend on the order the roots were typed -- two lanes regenerating the
    same tree must produce identical bytes or the pre-commit hook stages a phantom diff.

    `keep` is the file-level predicate described on `collect_md` -- it decides which files EXIST
    for this run. `exclude` drops named nodes after the fact. Two different jobs: `exclude` is
    about this generator's own output, `keep` is about whose files these are.

    `exclude` holds lobby-relative paths this generator WRITES. ⛔ Without it the graph is not
    deterministic: `docs/doc-graph.md` lands inside a scanned root, so the run that creates it
    produces a graph of N docs and the next run produces N+1 -- forever a byte apart, which
    `refresh_maps.py --verify` reads as a stale map and refuses the push on. A reference TO the
    excluded file still resolves, as `external` (a real file outside the indexed scope), which is
    the same answer the doc has always given for that case.
    """
    if isinstance(roots, (str, os.PathLike)):
        roots = [roots]
    roots = [Path(r).resolve() for r in roots]
    lobby = Path(lobby).resolve() if lobby is not None else find_lobby(roots[0])

    rel_roots, scope_list = [], []
    for r in roots:
        try:
            prefix = "" if r == lobby else r.relative_to(lobby).as_posix()
        except ValueError:
            # A root outside the lobby cannot have a lobby-relative id. Anchoring it anyway would
            # emit `../..` ids that resolve against nothing; refusing names the real mistake.
            raise SystemExit(f"doc-graph: --root {r} is not inside --lobby {lobby}")
        rel_roots.append(prefix or ".")
        excluded = {str(x) for x in exclude}
        for rel in collect_md(str(r), ignores, keep):
            node = posixpath.join(prefix, rel) if prefix else rel
            if node not in excluded:
                scope_list.append(node)

    rel_roots = sorted(set(rel_roots))
    scope_list = sorted(set(scope_list))          # dedup: overlapping roots must not double-count
    root = lobby                                  # every read below is <lobby>/<lobby-relative id>
    scope_files = set(scope_list)                 # complete set -> links INTO a pack still resolve
    by_basename = defaultdict(list)
    for rel in scope_list:
        by_basename[posixpath.basename(rel)].append(rel)

    # One collapsed summary per vendor pack (doc count); authored docs are the real graph.
    pack_docs = defaultdict(int)
    for rel in scope_list:
        pr = pack_root(rel)
        if pr is not None:
            pack_docs[pr] += 1
    authored = [rel for rel in scope_list if pack_root(rel) is None]

    edges, externals, danglings, ambiguous, unresolvable = [], [], [], [], []
    blind = blind_submodules(lobby)
    out_deg = defaultdict(int)
    in_deg = defaultdict(int)
    for rel in authored:
        in_deg.setdefault(rel, 0)
    for pr in pack_docs:
        in_deg.setdefault(pr, 0)                  # packs are link TARGETS, never parsed as sources

    def _link(src, dest, kind):
        if dest == src:
            return                                # self / same-pack
        edges.append({"from": src, "to": dest, "kind": kind})
        out_deg[src] += 1
        in_deg[dest] += 1

    for rel in authored:                          # parse ONLY the docs we authored (skip pack internals)
        text = strip_mermaid(strip_auto((root / rel).read_text(encoding="utf-8", errors="ignore")))
        for target, kind in sorted(extract_refs(text).items()):
            status, value = resolve(target, rel, scope_files, by_basename, lobby, blind)
            if status == "resolved":
                _link(rel, canon(value), kind)    # a hit inside a pack collapses to the pack node
            elif status == "ambiguous":
                cands = []
                for c in value:                   # collapse candidates; if they reduce to ONE, it resolves
                    cc = canon(c)
                    if cc not in cands:
                        cands.append(cc)
                if len(cands) == 1:
                    _link(rel, cands[0], kind)
                else:
                    ambiguous.append({"from": rel, "target": target, "candidates": cands})
            elif status == "external":
                externals.append({"from": rel, "target": value})
            elif status == "unresolvable":
                # Recorded, never counted. A blind spot the operator can SEE is the point --
                # dropping these silently would be the same lie in the other direction.
                unresolvable.append({"from": rel, "target": value})
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

    nodes = [{"path": rel, "in": in_deg.get(rel, 0), "out": out_deg.get(rel, 0)} for rel in authored]
    nodes += [{"path": pr, "in": in_deg.get(pr, 0), "out": 0, "docs": pack_docs[pr], "pack": True}
              for pr in sorted(pack_docs)]
    # A dangling target that names a PATH (a real dir component) is a likely-broken link (signal);
    # a bare filename -- or a root-relative `/name.md`, which is a bmad output-file pattern -- is
    # usually a generated-artifact name a workflow mentions, not a link (noise).
    broken = sum(1 for d in danglings if _has_dir(d["target"]))
    return {
        # RELATIVE, always -- see the module docstring. An absolute path here made the committed
        # artifact tree-specific, so it churned on every lane and named a pruned worktree.
        "root": rel_roots,
        "counts": {
            "files": len(authored), "packs": len(pack_docs), "pack_docs": sum(pack_docs.values()),
            "edges": len(edges), "external": len(externals),
            "ambiguous": len(ambiguous),
            "dangling": len(danglings), "broken_paths": broken, "unresolved_names": len(danglings) - broken,
            # NOT part of broken_paths, on purpose -- see `blind_submodules`. Counted so the
            # number is visible in the report rather than being an invisible subtraction.
            "unresolvable": len(unresolvable),
        },
        "nodes": nodes, "edges": edges,
        "dangling": danglings, "external": externals, "ambiguous": ambiguous,
        "unresolvable": unresolvable,
        "packs": [{"path": pr, "docs": pack_docs[pr], "in": in_deg.get(pr, 0)} for pr in sorted(pack_docs)],
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
    orphans = [n["path"] for n in nodes if n["in"] == 0 and not n.get("pack")]
    orph_by_dir = Counter(_topdir(p) for p in orphans)

    L = [
        AUTO_START,
        "<!-- generated by .agents/scripts/generate_doc_graph.py -- do NOT hand-edit this block;",
        "     edit the CURATED block above. Rebuild: python .agents/scripts/generate_doc_graph.py -->",
        "",
        f"**Scope:** {' + '.join('`%s`' % r for r in graph['root'])} | "
        f"**{c['files']}** authored docs + **{c.get('packs', 0)}** bmad packs "
        f"({c.get('pack_docs', 0)} vendor docs summarized) | **{c['edges']}** resolved edges | "
        f"**{c['broken_paths']}** broken-path refs | **{c['unresolved_names']}** bare-name refs | "
        f"**{c['ambiguous']}** ambiguous | **{c['external']}** external"
        + (f" | **{c['unresolvable']}** unresolvable (inside an uninitialized submodule -- this "
           f"tree cannot see them, so they are NOT counted broken)." if c.get("unresolvable")
           else "."),
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

    packs = graph.get("packs", [])
    if packs:
        L += ["", f"## BMAD skill packs ({len(packs)}, summarized -- internals not enumerated)",
              "_Each is one vendor skill pack: `docs` = md files inside it; `from` = links to it from our toolkit._",
              "", "| Pack | docs | linked-from |", "|---|---:|---:|"]
        prows, extra = _capped(sorted(packs, key=lambda p: (-p["in"], p["path"])))
        L += [f"| `{p['path']}` | {p['docs']} | {p['in']} |" for p in prows]
        if extra:
            L.append(f"| ... | _+{extra} more_ | _in doc-graph.json_ |")

    L += ["", f"## Orphans: {len(orphans)} docs nothing in scope references (full list in doc-graph.json)",
          "_Expected for leaf docs like per-skill `SKILL.md` that are loaded by name, not linked._",
          "", "| Top-level dir | Orphans |", "|---|---:|"]
    L += [f"| `{d}/` | {n} |" for d, n in orph_by_dir.most_common()]
    L.append(AUTO_END)
    return "\n".join(L)


def scaffold():
    return "\n".join([
        "# Doc Graph - the command centre's wiring (.agents/ + docs/)",
        "",
        CURATED_START,
        "> **Hand-edit this block.** The AUTO body below is regenerated by",
        "> `.agents/scripts/generate_doc_graph.py`, and staged automatically by the pre-commit maps",
        "> hook on any commit touching `.agents/` or `docs/`. This is the doc-to-doc",
        "> \"what references what\" layer -- and in the command centre it is the ONLY graph: the",
        "> centre carries no code graph by design (SCC-289), because a code graph parses code and",
        "> this repo is markdown. Deterministic, no LLM, ~$0.",
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


def resolve_scope(root_args, lobby_arg):
    """(lobby, [roots]) from the CLI's two knobs, with the house default when neither is given.

    Default scope is `.agents/` + `docs/` under the lobby this script lives in -- the two roots
    SCC-290 settled on. Passing --root replaces the default set entirely (it does not extend it),
    so a caller scanning one directory gets exactly that.
    """
    here = Path(__file__).resolve()
    own_lobby = here.parent.parent.parent          # .agents/scripts/ -> .agents/ -> <lobby>
    if root_args:
        roots = [Path(r).resolve() for r in root_args]
        lobby = Path(lobby_arg).resolve() if lobby_arg else find_lobby(roots[0])
    else:
        lobby = Path(lobby_arg).resolve() if lobby_arg else own_lobby
        roots = [lobby / name for name in DEFAULT_ROOT_NAMES if (lobby / name).is_dir()]
    return lobby, roots


def main():
    ap = argparse.ArgumentParser(
        description="Generate the doc-wiring graph for the command centre (.agents/ + docs/)")
    ap.add_argument("--root", action="append", default=None,
                    help="dir to scan; repeatable. Default: <lobby>/.agents and <lobby>/docs")
    ap.add_argument("--lobby", default=None,
                    help="the anchor every node id is relative to (default: the repo holding --root)")
    ap.add_argument("--output", default=None, help="markdown out (default <lobby>/docs/doc-graph.md)")
    ap.add_argument("--json", default=None, help="json out (default <lobby>/docs/doc-graph.json)")
    ap.add_argument("--ignore", default="", help="comma-separated extra dir names to skip")
    ap.add_argument("--top", type=int, default=15, help="how many hubs to list")
    args = ap.parse_args()

    lobby, roots = resolve_scope(args.root, args.lobby)
    if not roots:
        raise SystemExit(f"doc-graph: nothing to scan under {lobby}")
    output = Path(args.output) if args.output else lobby / "docs" / "doc-graph.md"
    json_out = Path(args.json) if args.json else lobby / "docs" / "doc-graph.json"
    ignores = set(DEFAULT_IGNORES)
    ignores.update(x.strip() for x in args.ignore.split(",") if x.strip())

    # The generator's own markdown output is excluded from its own scan -- see build_graph.
    own = []
    for f in (output,):
        try:
            own.append(Path(f).resolve().relative_to(lobby).as_posix())
        except ValueError:
            pass                                  # written outside the lobby: nothing to exclude
    graph = build_graph(roots, ignores, lobby, exclude=own)
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
