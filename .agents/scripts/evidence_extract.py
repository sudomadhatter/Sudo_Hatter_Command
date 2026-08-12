"""evidence_extract.py — ground-truth code evidence for the house review engine (SCC-123).

Zero LLM calls. It reads a repository and prints facts. Nothing here judges anything.

  ── WHAT IT IS FOR ─────────────────────────────────────────────────────────────────────────
Review lenses cold-read a repo: they open files one at a time over many turns, and whatever they
never happen to open, they never reason about. This script does that reading in code and hands the
lens a dossier up front.

    --pack <files>      BEFORE a lens reviews: the changed files' content plus who imports them.
    --findings <json>   AFTER a finding is asserted: the code at the line, its call sites, the
                        diff hunk, cross-referenced files, and blast-radius neighbours.

Ported from pr-af (`github.com/Agent-Field/pr-af`) `src/pr_af/evidence.py` @ **8593130**. Every cap
below was re-read at that SHA rather than taken from second-hand notes. ⚠ They are NOT in that
project's `config.py`, whatever a summary may say — at the port SHA that file holds only the on/off
toggle `evidence_pack_reviewers`, and the numbers live in `evidence.py` as module constants and
function defaults which its orchestrator calls without overriding.

  ── WHY NOT GitNexus ───────────────────────────────────────────────────────────────────────
This system already has a code-intelligence index (GitNexus), and the overlap is deliberate, not an
oversight. Fresh search wins **here** for three reasons that are properties of that index, not
preferences: it is **machine-local** and does not travel via git, so a teammate or a fresh clone has
no index at all; it goes **stale after a pull**, and a reviewer primed with last week's call graph
is worse off than one primed with nothing; and it **misses attribute-dispatch call sites**
(`self.<attr>.<method>()`), which is precisely the shape a review needs to see. A review must never
depend on state that may silently not exist.

⛔ Two standing instructions for whoever reads this next:
   1. Do NOT "deduplicate" this script into GitNexus calls. The duplication is the point.
   2. Do NOT grow it into a blast-radius or impact tool. It fetches evidence for a review that is
      already scoped; scoping is somebody else's job.

  ── PURE-PYTHON SEARCH, AND WHY ────────────────────────────────────────────────────────────
pr-af shells out to `grep` twice. This system runs on a Mac and a Windows PC, so a shelled-out
`grep` is banned outright — it is not portable and it is not present everywhere. The replacement
walks the tree once, prunes the skip-dirs, and matches compiled patterns over a byte-bounded file
cache: the same work, in process. The repo's file list is built once and reused, so eight
identifier searches cost one walk, not eight.

The guard for this file proves that claim by running it with **PATH emptied** and requiring
byte-identical output — a source-level scan for the word would be inverted by this very paragraph.

  ── DEVIATIONS FROM THE PORT, EACH ON PURPOSE ──────────────────────────────────────────────
* `_import_specifiers` replaces pr-af's `_path_to_module`, which returns one dotted name and, for
  anything that is not `.py`, the empty string. Two consequences it had, both silent: every
  TypeScript file reported `IMPORTED BY: none`, and so did every script in THIS repo, because
  `.agents/scripts/wf_common.py` is imported as bare `wf_common` off a `sys.path` entry and never
  as `.agents.scripts.wf_common`. "Nothing depends on this file" is the most dangerous false
  statement you can prime a reviewer with, so both branches resolve properly now.
* TS/JS importers are matched by **resolving each importer's own specifier** against its own
  directory, never by matching a basename — `Foo.tsx` matched by name would claim every `Foo` in
  the repo imports it. `@/`-style aliases resolve against the roots declared in the nearest
  `tsconfig.json`/`jsconfig.json`, **relative to that config's directory**: the one real frontend
  here keeps its config at `frontend/tsconfig.json` with `"@/*": ["./src/*"]`, so a repo-root
  assumption would resolve every aliased import to a path that does not exist.
* Path normalization tries the **direct join first** and only falls back to pr-af's marker-stripping
  normalizer, which mangles any path where the repo name recurs as a directory component. That is
  their own documented fix; it was applied in one function upstream and is applied everywhere here.
* The caller supplies a **unified diff**; pr-af receives per-file patches from its own diff engine,
  so the split happens here.
* Concurrency is a thread pool rather than asyncio, bounded at the same 10.

  ── FAILURE CONTRACT ───────────────────────────────────────────────────────────────────────
This is code, not a review lens: if it dies, the caller runs cold with a note, and it must never
cap a verdict. So a missing file, an undecodable file, a malformed finding, or a search that blows
its deadline yields an empty or partial field — never a traceback. Exit 2 is reserved for a usage
error (bad flags, unreadable input), which is the caller's mistake rather than the repo's.

Stdlib only, plain ASCII output — same constraints as its siblings (Windows consoles are cp1252).
"""
from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# ── Caps, every one re-read from pr-af @ 8593130 ──────────────────────────────
_PACK_MAX_FILES = 6              # evidence.py:486
_PACK_MAX_LINES = 400            # evidence.py:487
_PACK_MAX_CHARS = 16000          # evidence.py:488
_PACK_IMPORT_SLICE = 1200        # evidence.py:516
_EXTRACT_WORKERS = 10            # evidence.py:152  (asyncio.Semaphore(10))
_MAX_IDENTIFIERS_PER_FINDING = 8  # evidence.py:28
_SEARCH_SECONDS = 10             # evidence.py:279, :421  (grep timeout=10)
_FILE_CACHE_MAX_BYTES = 128 * 1024 * 1024   # evidence.py:23
_FILE_CACHE_MAX_ENTRIES = 2000              # evidence.py:24
_PRIMARY_CONTEXT = 30            # evidence.py:166
_CALLER_CONTEXT = 5              # evidence.py:301
_CALLER_SNIPPETS = 10            # evidence.py:205, :305
_CROSS_REF_FILES = 10            # evidence.py:209
_BLAST_SNIPPETS = 5              # evidence.py:475
_BLAST_CONTEXT = 10              # evidence.py:470
_IMPORT_LIST = 30                # evidence.py:430-431
_DIFF_HUNK_LINES = 200           # evidence.py:372-377

_SKIP_DIRS = (".git", "node_modules", "__pycache__", ".venv", "vendor", "venv")  # evidence.py:57

_TEXT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".rb", ".php",
    ".c", ".h", ".cpp", ".hpp", ".cs", ".swift", ".kt", ".scala", ".sh",
    ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", ".md", ".sql",
    ".html", ".css", ".scss", ".txt",
}

_COMMON_IDENTIFIER_WORDS = {
    "the", "this", "that", "with", "from", "when", "where", "which", "there",
    "their", "returns", "return", "found", "check", "line", "file", "code",
    "issue", "error", "value", "values", "class", "function", "method",
    "should", "could", "would", "into", "over", "under", "each", "name",
    "data", "test", "tests",
}

# Module suffixes JS/TS resolution will try, longest-lived first.
_TS_EXTS = (".ts", ".tsx", ".js", ".jsx", ".mts", ".cts", ".mjs", ".cjs")

# Every way a JS/TS file names another module, including the side-effect form.
_JS_SPEC_RE = re.compile(
    r"""(?:\bfrom\s*|\brequire\s*\(\s*|\bimport\s*\(\s*|\bimport\s+)['"]([^'"\n]+)['"]"""
)

# ── File cache (bytes-bounded; shared across threads) ─────────────────────────
_CACHE_LOCK = threading.Lock()
_FILE_CACHE: dict[tuple[str, float], list[str]] = {}
_FILE_CACHE_BYTES = 0

# Repo -> sorted list of repo-relative text files. Built once, before any pool starts,
# so the workers only ever read it.
_REPO_FILES: dict[str, list[str]] = {}
_ALIAS_ROOTS: dict[str, list[tuple[str, str]]] = {}


def _read_file_lines(abspath: str) -> list[str]:
    """Cached line read. Keyed by (path, mtime), so a re-checkout invalidates naturally."""
    global _FILE_CACHE_BYTES
    try:
        mtime = os.path.getmtime(abspath)
    except OSError:
        return []
    key = (abspath, mtime)
    with _CACHE_LOCK:
        cached = _FILE_CACHE.get(key)
    if cached is not None:
        return cached
    try:
        with open(abspath, encoding="utf-8", errors="ignore") as handle:
            lines = handle.read().splitlines()
    except OSError:
        return []
    size = sum(len(line) for line in lines)
    if size > _FILE_CACHE_MAX_BYTES:   # a pathological single file: serve it uncached
        return lines
    with _CACHE_LOCK:
        if (len(_FILE_CACHE) >= _FILE_CACHE_MAX_ENTRIES
                or _FILE_CACHE_BYTES + size > _FILE_CACHE_MAX_BYTES):
            _FILE_CACHE.clear()
            _FILE_CACHE_BYTES = 0
        _FILE_CACHE[key] = lines
        _FILE_CACHE_BYTES += size
    return lines


def _is_text_file(path: str) -> bool:
    if not path or not os.path.isfile(path):
        return False
    ext = os.path.splitext(path)[1].lower()
    if ext in _TEXT_EXTENSIONS:
        return True
    if ext:
        return False
    try:                              # extension-less: scan for null bytes
        with open(path, "rb") as handle:
            return b"\x00" not in handle.read(1024)
    except OSError:
        return False


def _under_skip_dir(rel: str) -> bool:
    return any(part in _SKIP_DIRS for part in rel.split("/"))


def _repo_files(repo: str) -> list[str]:
    """Every repo-relative text file, skip-dirs pruned, sorted. One walk per repo."""
    cached = _REPO_FILES.get(repo)
    if cached is not None:
        return cached
    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = sorted(d for d in dirnames if d not in _SKIP_DIRS)
        for name in sorted(filenames):
            abspath = os.path.join(dirpath, name)
            if _is_text_file(abspath):
                found.append(os.path.relpath(abspath, repo).replace("\\", "/"))
    found.sort()
    _REPO_FILES[repo] = found
    return found


# ── Path resolution ───────────────────────────────────────────────────────────
def _normalize_relative_path(repo: str, file_path: str) -> str:
    """pr-af's normalizer (evidence.py:522). Kept as the FALLBACK only — see _resolve_rel."""
    path = (file_path or "").strip().replace("\\", "/")
    if not path:
        return ""
    if path.startswith("/workspaces/"):
        path = path[len("/workspaces/"):]
    if path.startswith("./"):
        path = path[2:]

    repo_abs = os.path.abspath(repo) if repo else ""
    path_abs = os.path.abspath(path) if os.path.isabs(path) else ""
    if repo_abs and path_abs.startswith(repo_abs):
        path = os.path.relpath(path_abs, repo_abs)
    elif path.startswith("/"):
        path = path.lstrip("/")

    marker = os.path.basename(repo_abs) + "/"
    if marker != "/" and marker in path:
        path = path[path.find(marker) + len(marker):]
    return os.path.normpath(path).replace("\\", "/")


def _resolve_rel(repo: str, file_path: str) -> str:
    """Repo-relative path, trying the DIRECT join first.

    The fallback normalizer strips a `<repo-name>/` marker found anywhere in the path, so a repo
    containing a directory named after itself has every such path mangled into one that does not
    exist. pr-af hit this and fixed it in one function; the fix belongs at every entry point.
    """
    raw = (file_path or "").strip().replace("\\", "/")
    if not raw:
        return ""
    candidates: list[str] = []
    if not os.path.isabs(raw):
        direct = raw[2:] if raw.startswith("./") else raw
        candidates.append(direct.lstrip("/"))
    candidates.append(_normalize_relative_path(repo, raw))
    for cand in candidates:
        if cand and os.path.isfile(os.path.join(repo, cand)):
            return os.path.normpath(cand).replace("\\", "/")
    return candidates[-1] if candidates else ""


# ── Snippets ──────────────────────────────────────────────────────────────────
def _format_lines(lines: list[str], target_line: int, context: int) -> str:
    if not lines:
        return ""
    start = max(0, target_line - 1 - context)
    end = min(len(lines), target_line + context)
    return "\n".join(f"{i + 1}: {lines[i].rstrip()}" for i in range(start, end))


def _read_code_snippet(repo: str, rel: str, line: int, context: int = _PRIMARY_CONTEXT) -> str:
    rel = _resolve_rel(repo, rel)
    if not rel or _under_skip_dir(rel):
        return ""
    abspath = os.path.join(repo, rel)
    if not _is_text_file(abspath):
        return ""
    return _format_lines(_read_file_lines(abspath), max(1, line), context)


# ── Identifier / path mentions ────────────────────────────────────────────────
def _extract_mentioned_identifiers(text: str) -> list[str]:
    candidates: list[str] = []
    candidates += re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", text)
    candidates += re.findall(r"\b([A-Z][a-zA-Z0-9]{2,})\b", text)
    candidates += re.findall(r"\b([a-z_][a-z0-9_]{2,})\s*\(", text)

    ordered: dict[str, None] = {}
    for raw in candidates:
        name = raw.strip("` ")
        if len(name) < 3 or name.lower() in _COMMON_IDENTIFIER_WORDS:
            continue
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            continue
        ordered[name] = None
    return list(ordered)


def _extract_mentioned_file_paths(text: str, repo: str) -> list[str]:
    found: set[str] = set()
    for value in (re.findall(r"`([^`]*?/[^`]*?)`", text)
                  + re.findall(r"([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)", text)):
        if "/" not in value or " " in value:
            continue
        rel = _resolve_rel(repo, value)
        if rel and not _under_skip_dir(rel) and os.path.isfile(os.path.join(repo, rel)):
            found.add(rel)
    return sorted(found)


# ── Caller search (pure Python; replaces `grep -RInE`) ────────────────────────
def _find_function_callers(repo: str, function_name: str, exclude_rel: str = "") -> list[str]:
    ident = function_name.strip()
    if not ident or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", ident):
        return []
    pattern = re.compile(r"\b" + re.escape(ident) + r"\s*\(")
    deadline = time.monotonic() + _SEARCH_SECONDS

    snippets: list[str] = []
    for rel in _repo_files(repo):
        if time.monotonic() > deadline or len(snippets) >= _CALLER_SNIPPETS:
            break
        if rel == exclude_rel:
            continue
        for idx, text in enumerate(_read_file_lines(os.path.join(repo, rel))):
            if not pattern.search(text):
                continue
            snippet = _read_code_snippet(repo, rel, idx + 1, _CALLER_CONTEXT)
            if snippet:
                snippets.append(f"{rel}:{idx + 1}\n{snippet}")
            if len(snippets) >= _CALLER_SNIPPETS:
                break
    return _dedupe(snippets)


# ── Import context ────────────────────────────────────────────────────────────
def _python_module_names(repo: str, rel: str) -> set[str]:
    """Every name `rel` can legitimately be imported as.

    Two, in general: the root-relative dotted path (`src.pkg.target`), and the longest suffix that
    forms a real package chain (`pkg.target` — walking up only while each parent holds an
    `__init__.py`). The second is what makes a flat `sys.path` script findable: `scripts/tool.py`
    with no `scripts/__init__.py` is imported as bare `tool`, and by nothing else.
    """
    if not rel.endswith(".py"):
        return set()
    parts = rel[:-3].split("/")
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    if not parts:
        return set()

    names: set[str] = set()
    if all(p.isidentifier() for p in parts):
        names.add(".".join(parts))

    idx = len(parts) - 1
    while idx > 0 and os.path.isfile(os.path.join(repo, *parts[:idx], "__init__.py")):
        idx -= 1
    chain = parts[idx:]
    if all(p.isidentifier() for p in chain):
        names.add(".".join(chain))
    return names


def _imported_names_at(lines: list[str], start: int, head: str) -> str:
    """The name list of a `from X import ...`, following a parenthesised continuation."""
    text = head
    if "(" in head and ")" not in head:
        for follow in lines[start + 1:start + 40]:
            text += " " + follow
            if ")" in follow:
                break
    return text


def _python_importers(repo: str, rel: str) -> list[str]:
    names = _python_module_names(repo, rel)
    if not names:
        return []

    direct: list[re.Pattern[str]] = []
    parent_forms: list[tuple[re.Pattern[str], str]] = []
    for name in names:
        esc = re.escape(name)
        # `import X` / `import X.y` / `import X as z`, but never `import Xbox`
        direct.append(re.compile(r"^\s*import\s+" + esc + r"(?=[\s.,]|$)"))
        # `from X import ...` / `from X.y import ...`, but never `from Xbox import ...`
        direct.append(re.compile(r"^\s*from\s+" + esc + r"(?=[\s.]|$)"))
        if "." in name:
            parent, leaf = name.rsplit(".", 1)
            parent_forms.append(
                (re.compile(r"^\s*from\s+" + re.escape(parent) + r"\s+import\s+(.*)$"), leaf))
        else:
            # a top-level module is also reachable as `from . import tool` inside its own package
            parent_forms.append((re.compile(r"^\s*from\s+\.\s+import\s+(.*)$"), name))

    deadline = time.monotonic() + _SEARCH_SECONDS
    importers: list[str] = []
    for cand in _repo_files(repo):
        if time.monotonic() > deadline:
            break
        if cand == rel or not cand.endswith(".py"):
            continue
        lines = _read_file_lines(os.path.join(repo, cand))
        hit = False
        for idx, text in enumerate(lines):
            if any(p.search(text) for p in direct):
                hit = True
                break
            for pattern, leaf in parent_forms:
                match = pattern.search(text)
                if match and re.search(r"\b" + re.escape(leaf) + r"\b",
                                       _imported_names_at(lines, idx, match.group(1))):
                    hit = True
                    break
            if hit:
                break
        if hit:
            importers.append(cand)
    return importers


def _alias_roots(repo: str) -> list[tuple[str, str]]:
    """(`@/`, `frontend/src`)-style pairs, read from every tsconfig/jsconfig in the tree.

    Roots are resolved relative to the DIRECTORY OF THE CONFIG THAT DECLARED THEM. A repo-root
    assumption silently empties `IMPORTED BY` for every aliased import in a nested frontend, which
    is the failure this whole function exists to prevent.
    """
    cached = _ALIAS_ROOTS.get(repo)
    if cached is not None:
        return cached

    roots: list[tuple[str, str]] = []
    for rel in _repo_files(repo):
        if posixpath.basename(rel) not in ("tsconfig.json", "jsconfig.json"):
            continue
        try:
            data = json.loads("\n".join(_read_file_lines(os.path.join(repo, rel))))
        except (ValueError, TypeError):
            continue                      # not strict JSON: degrade, never die
        if not isinstance(data, dict):
            continue
        paths = (data.get("compilerOptions") or {}).get("paths") or {}
        if not isinstance(paths, dict):
            continue
        cfg_dir = posixpath.dirname(rel)
        for key, values in paths.items():
            if not (isinstance(key, str) and key.endswith("*") and isinstance(values, list)):
                continue
            for value in values:
                if not (isinstance(value, str) and value.endswith("*")):
                    continue
                root = posixpath.normpath(posixpath.join(cfg_dir, value[:-1]))
                roots.append((key[:-1], "" if root == "." else root))
                break

    if not roots:
        roots = [("@/", "src")]           # the common default, for a repo with no config at all
    roots.sort(key=lambda pair: -len(pair[0]))
    _ALIAS_ROOTS[repo] = roots
    return roots


def _resolve_specifier(repo: str, importer_rel: str, spec: str,
                       aliases: list[tuple[str, str]]) -> str:
    """The repo-relative file `spec` names when written inside `importer_rel`, or ''."""
    if spec.startswith("."):
        base = posixpath.normpath(posixpath.join(posixpath.dirname(importer_rel), spec))
    else:
        base = ""
        for prefix, root in aliases:
            if spec.startswith(prefix):
                base = posixpath.normpath(posixpath.join(root, spec[len(prefix):]))
                break
        if not base:
            return ""                     # a bare package name: not this repo's file
    if base.startswith("..") or base == ".":
        return ""
    for cand in [base] + [base + e for e in _TS_EXTS] + [f"{base}/index{e}" for e in _TS_EXTS]:
        if os.path.isfile(os.path.join(repo, cand)):
            return cand
    return ""


def _ts_importers(repo: str, rel: str) -> list[str]:
    aliases = _alias_roots(repo)
    deadline = time.monotonic() + _SEARCH_SECONDS
    importers: list[str] = []
    for cand in _repo_files(repo):
        if time.monotonic() > deadline:
            break
        if cand == rel or os.path.splitext(cand)[1].lower() not in _TS_EXTS:
            continue
        for text in _read_file_lines(os.path.join(repo, cand)):
            if any(_resolve_specifier(repo, cand, spec, aliases) == rel
                   for spec in _JS_SPEC_RE.findall(text)):
                importers.append(cand)
                break
    return importers


def _build_import_context(repo: str, rel: str) -> str:
    rel = _resolve_rel(repo, rel)
    if not rel or _under_skip_dir(rel):
        return ""
    abspath = os.path.join(repo, rel)

    imports: list[str] = []
    if _is_text_file(abspath):
        for raw in _read_file_lines(abspath):
            stripped = raw.strip()
            if (stripped.startswith("import ") or stripped.startswith("from ")
                    or _JS_SPEC_RE.search(stripped)):
                imports.append(stripped)

    ext = os.path.splitext(rel)[1].lower()
    if ext == ".py":
        importers = _python_importers(repo, rel)
    elif ext in _TS_EXTS:
        importers = _ts_importers(repo, rel)
    else:
        importers = []

    shown_imports = ", ".join(imports[:_IMPORT_LIST]) if imports else "none"
    shown_by = ", ".join(sorted(set(importers))[:_IMPORT_LIST]) if importers else "none"
    return "IMPORTS: " + shown_imports + "\nIMPORTED BY: " + shown_by


# ── Diff ──────────────────────────────────────────────────────────────────────
def _normalize_patch_key(file_path: str) -> str:
    normalized = file_path.replace("\\", "/").strip()
    for prefix in ("a/", "b/"):
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
    return normalized.lstrip("/")


def split_unified_diff(text: str) -> dict[str, str]:
    """A unified diff -> {repo-relative path: that file's patch text}."""
    patches: dict[str, str] = {}
    key: str | None = None
    body: list[str] = []

    def flush() -> None:
        if key is not None:
            patches[key] = "\n".join(body)

    for line in (text or "").splitlines():
        if line.startswith("diff --git "):
            flush()
            key, body = None, []
            continue
        if line.startswith("+++ "):
            path = _normalize_patch_key(line[4:].strip())
            if path and path != "dev/null":
                flush()
                key, body = path, []
            continue
        if line.startswith("--- "):
            continue
        if key is not None:
            body.append(line)
    flush()
    return patches


def _extract_hunk_for_line(patch_lines: list[str], line: int) -> list[str]:
    hunk: list[str] = []
    start = count = 0
    for raw in patch_lines:
        if raw.startswith("@@"):
            if hunk and count > 0 and start <= line < start + count:
                return hunk
            hunk = [raw]
            match = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", raw)
            start = int(match.group(1)) if match else 0
            count = int(match.group(2) or "1") if match else 0
        elif hunk:
            hunk.append(raw)
    if hunk and count > 0 and start <= line < start + count:
        return hunk
    return []


def _extract_diff_hunk(patches: dict[str, str], rel: str, line: int | None) -> str:
    normalized = _normalize_patch_key(rel)
    patch = patches.get(normalized, "")
    if not patch:
        for key, value in patches.items():
            if _normalize_patch_key(key) == normalized:
                patch = value
                break
    if not patch:
        return ""
    patch_lines = patch.splitlines()
    if line is None:
        return "\n".join(patch_lines[:_DIFF_HUNK_LINES])
    hunk = _extract_hunk_for_line(patch_lines, line)
    return "\n".join((hunk or patch_lines)[:_DIFF_HUNK_LINES])


# ── Blast radius ──────────────────────────────────────────────────────────────
def _extract_blast_radius_code(repo: str, rel: str, identifiers: list[str],
                               blast_radius: list[str]) -> str:
    if not identifiers or not blast_radius:
        return ""
    snippets: list[str] = []
    for candidate in blast_radius:
        if len(snippets) >= _BLAST_SNIPPETS:
            break
        other = _resolve_rel(repo, candidate)
        if not other or other == rel or _under_skip_dir(other):
            continue
        abspath = os.path.join(repo, other)
        if not _is_text_file(abspath):
            continue
        lines = _read_file_lines(abspath)
        if not lines:
            continue
        for ident in identifiers:
            pattern = re.compile(r"\b" + re.escape(ident) + r"\b")
            idx = next((i for i, text in enumerate(lines) if pattern.search(text)), None)
            if idx is None:
                continue
            snippet = _format_lines(lines, idx + 1, _BLAST_CONTEXT)
            if snippet:
                snippets.append(f"{other}:{idx + 1}\n{snippet}")
            break
    return "\n\n".join(snippets[:_BLAST_SNIPPETS])


def _dedupe(values: list[str]) -> list[str]:
    ordered: dict[str, None] = {}
    for value in values:
        if value:
            ordered[value] = None
    return list(ordered)


# ── Mode 1: the pre-lens pack ─────────────────────────────────────────────────
def build_pack(repo: str, target_files: list[str]) -> str:
    """Pre-read a lens's target files (+ import context) so it reasons over a primed dossier."""
    if not repo or not target_files:
        return ""
    blocks: list[str] = []
    for raw in target_files[:_PACK_MAX_FILES]:
        rel = _resolve_rel(repo, raw)
        if not rel or _under_skip_dir(rel):
            continue
        abspath = os.path.join(repo, rel)
        if not (os.path.isfile(abspath) and _is_text_file(abspath)):
            continue
        lines = _read_file_lines(abspath)
        if not lines:
            continue
        shown = lines[:_PACK_MAX_LINES]
        body = "\n".join(f"{i + 1}: {line.rstrip()}" for i, line in enumerate(shown))
        trunc = (f" (showing first {_PACK_MAX_LINES} of {len(lines)})"
                 if len(lines) > _PACK_MAX_LINES else "")
        # Import context goes ABOVE the body, which is a deliberate deviation from the port.
        # pr-af appends it, then truncates the assembled blob at _PACK_MAX_CHARS -- and one
        # 400-line file fills that budget on its own, so the context is cut off the end. Caught
        # by running this on a real file in this repo (`wf_common.py`, 16093 bytes, IMPORTED BY
        # truncated away). The caps are pinned and unchanged; only the ORDER changed, so what
        # truncation eats is body lines rather than the dependency map -- which is the highest
        # value per byte in the whole pack and the reason a lens is primed at all.
        block = f"### {rel}{trunc}"
        context = _build_import_context(repo, rel)
        if context:
            block += f"\n_import/usage context:_ {context[:_PACK_IMPORT_SLICE]}"
        block += f"\n```\n{body}\n```"
        blocks.append(block)
    return "\n\n".join(blocks)[:_PACK_MAX_CHARS]


# ── Mode 2: per-finding evidence ──────────────────────────────────────────────
def _extract_one(repo: str, finding: dict, patches: dict[str, str],
                 blast_radius: list[str]) -> dict:
    title = str(finding.get("title") or "")
    rel = _resolve_rel(repo, str(finding.get("file_path") or ""))
    try:
        line = int(finding.get("line_start") or 1)
    except (TypeError, ValueError):
        line = 1

    blob = "\n".join(str(finding.get(key) or "") for key in ("title", "body", "evidence"))
    identifiers = _extract_mentioned_identifiers(blob)[:_MAX_IDENTIFIERS_PER_FINDING]

    callers = _dedupe([snippet for ident in identifiers
                       for snippet in _find_function_callers(repo, ident, rel)])[:_CALLER_SNIPPETS]

    cross_refs = _dedupe([
        _read_code_snippet(repo, path, 1, _PRIMARY_CONTEXT)
        for path in _extract_mentioned_file_paths(blob, repo)[:_CROSS_REF_FILES]
    ])

    return {
        "finding_title": title,
        "primary_code": _read_code_snippet(repo, rel, line, _PRIMARY_CONTEXT),
        "caller_snippets": callers,
        "cross_ref_snippets": cross_refs,
        "diff_hunk": _extract_diff_hunk(patches, rel, line),
        "import_context": _build_import_context(repo, rel),
        "related_code": _extract_blast_radius_code(repo, rel, identifiers, blast_radius),
    }


def extract_for_findings(repo: str, findings: list[dict], patches: dict[str, str],
                         blast_radius: list[str]) -> dict[str, dict]:
    if not findings:
        return {}
    _repo_files(repo)          # build the index BEFORE the pool, so workers only read it
    _alias_roots(repo)
    with ThreadPoolExecutor(max_workers=_EXTRACT_WORKERS) as pool:
        packages = list(pool.map(
            lambda finding: _extract_one(repo, finding, patches, blast_radius), findings))
    return {package["finding_title"]: package for package in packages}


# ── CLI ───────────────────────────────────────────────────────────────────────
def _read_input(source: str) -> str:
    if source == "-":
        return sys.stdin.read()
    with open(source, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="evidence_extract.py",
        description="Ground-truth code evidence for the house review engine. Prints to stdout.")
    parser.add_argument("--repo", required=True, help="repository root to read")
    parser.add_argument("--pack", nargs="+", metavar="FILE",
                        help="pre-lens dossier for these target files")
    parser.add_argument("--findings", metavar="JSON",
                        help="per-finding evidence; a path, or '-' for stdin")
    parser.add_argument("--diff", metavar="PATCH",
                        help="unified diff for hunk extraction; a path, or '-' for stdin")
    parser.add_argument("--blast-radius", nargs="*", default=[], metavar="FILE",
                        help="non-diff files a finding may reach")
    args = parser.parse_args(argv)

    if bool(args.pack) == bool(args.findings):
        parser.error("exactly one of --pack or --findings is required")
    if not os.path.isdir(args.repo):
        parser.error(f"--repo is not a directory: {args.repo}")
    if args.findings == "-" and args.diff == "-":
        parser.error("only one input may read from stdin")
    repo = os.path.abspath(args.repo)

    if args.pack:
        sys.stdout.write(build_pack(repo, args.pack) + "\n")
        return 0

    try:
        findings = json.loads(_read_input(args.findings))
    except (OSError, ValueError) as exc:
        parser.error(f"--findings could not be read as JSON: {exc}")
    if not isinstance(findings, list):
        parser.error("--findings must be a JSON list of finding objects")

    patches: dict[str, str] = {}
    if args.diff:
        try:
            patches = split_unified_diff(_read_input(args.diff))
        except OSError as exc:
            parser.error(f"--diff could not be read: {exc}")

    usable = [f for f in findings if isinstance(f, dict) and str(f.get("title") or "")]
    result = extract_for_findings(repo, usable, patches, list(args.blast_radius))
    sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
