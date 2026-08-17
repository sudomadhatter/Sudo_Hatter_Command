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

The guard for this file proves that claim by running it with **process creation blocked inside the
interpreter** — a `sitecustomize.py` on `PYTHONPATH` that makes every spawn primitive raise, with a
control shell-out asserted to die under the same block — and requiring byte-identical output.
Emptying PATH is NOT that proof: CPython falls back to `os.defpath` (`:/bin:/usr/bin`), so a
shelled-out grep survives a no-PATH run untouched. A source-level scan for the word would be
inverted by this very paragraph.

  ── DEVIATIONS FROM THE PORT, EACH ON PURPOSE ──────────────────────────────────────────────
* `_python_module_names`/`_python_importers` (Python) and `_ts_importers` (TS/JS) replace pr-af's
  `_path_to_module`, which returns one dotted name and, for anything that is not `.py`, the empty
  string. Two consequences it had, both silent: every
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

  ── THE CAPS: WHAT WAS TRANSCRIBED, AND WHAT WAS DERIVED (SCC-187) ─────────────────────────
Every number below the fold was **transcribed** from pr-af `evidence.py` @ `8593130`, and the
transcription was careful — each one carries the line it came from, and the docstring above says
why they are not in that project's `config.py`. ⚠ Transcribing a number is not deriving one, and
nothing here was ever re-derived against THIS repo's files. `_PACK_MAX_CHARS = 16000` is the one
where that shows: this file alone is well over 50 KB, and its first 400 lines — the separate
`_PACK_MAX_LINES` cap — are already over 22 KB, so **the engine cannot pack its own main script**.
(Deliberately stated as bounds rather than exact byte counts: an exact figure for the file that
CONTAINS it is stale the moment anyone edits the file, and this docstring shipped with one that
was already 4.8 KB wrong on the very commit that introduced it. Measure it when you need it:
`wc -c` and `awk 'NR<=400'`.) `build_pack`'s own comment concedes the shape of it: a six-file
change leaves each file "a preamble rather than a readable extent... a trade, not a win."

⭐ **No cap NUMBER here has been re-derived — one cap's SELECTION POLICY has.** `_CALLER_SNIPPETS`
is still the transcribed 10; what SCC-187 derived is *which* 10, because measurement showed the
walk's own cap silently deciding it by file order (see `_find_function_callers`' `prefer` and its
reserve). Do not read the paragraph above as "10 was measured against this repo" — it was not.

  ⛔ IF YOU WIRE `--pack` INTO A CALLER, FIX THIS FIRST. When the pack overruns its budget it
  DROPS whole files (`build_pack`, "pack: <rel> dropped") and trims bodies — and it says so via
  `_note()`, which writes to **stderr**, while every caller pastes **stdout** into a lens. So the
  lens is handed a partial evidence set and is never told it is partial: a false all-clear over
  every file nobody opened, which is the SCC-147 failure class. Nothing calls `--pack` today, so
  this cannot currently fire. The moment something does, the drop notice has to reach the same
  stream as the pack, or the truncation has to become a spill that loses nothing. ⛔ Wiring and
  that fix ship TOGETHER — wiring alone is a net negative.

  ── FAILURE CONTRACT ───────────────────────────────────────────────────────────────────────
This is code, not a review lens: if it dies, the caller runs cold with a note, and it must never
cap a verdict. So a missing file, an undecodable file, a malformed finding, or a search that blows
its deadline yields an empty or partial field — never a traceback. Exit 2 is reserved for a usage
error (bad flags, unreadable input), which is the caller's mistake rather than the repo's.

Stdlib only. The script's own labels are ASCII, but repo content is arbitrary text, so both output
streams are forced to UTF-8 with `errors="replace"`: a cp1252 Windows console degrades a character
rather than killing the run. Unfixed, this script could not pack its own source on the PC.
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
# A nested checkout under `.claude/worktrees/<lane>/` is ANOTHER BRANCH'S copy of this repo:
# listing its files as importers or callers primes the lens with code that is not on the branch
# under review. Matched as an adjacent (parent, child) pair, not a bare name, so a legitimate
# `worktrees/` directory elsewhere in a repo is not swallowed with it.
_SKIP_DIR_PAIRS = ((".claude", "worktrees"),)

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


def _note(message: str) -> None:
    """Degrading is allowed; degrading SILENTLY is not (the failure contract above). Notes go to
    stderr so stdout stays parseable — it is pack text or findings JSON."""
    sys.stderr.write("note: " + message + "\n")


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
    parts = rel.split("/")
    if any(part in _SKIP_DIRS for part in parts):
        return True
    return any(tuple(parts[i:i + 2]) in _SKIP_DIR_PAIRS for i in range(len(parts) - 1))


def _repo_files(repo: str) -> list[str]:
    """Every repo-relative text file, skip-dirs pruned, sorted. One walk per repo."""
    cached = _REPO_FILES.get(repo)
    if cached is not None:
        return cached
    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(repo):
        base = os.path.basename(dirpath)
        dirnames[:] = sorted(d for d in dirnames
                             if d not in _SKIP_DIRS and (base, d) not in _SKIP_DIR_PAIRS)
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
    """Repo-relative path, trying the DIRECT join first — and never resolving OUTSIDE the repo.

    The fallback normalizer strips a `<repo-name>/` marker found anywhere in the path, so a repo
    containing a directory named after itself has every such path mangled into one that does not
    exist. pr-af hit this and fixed it in one function; the fix belongs at every entry point.

    Containment is the other half: absolute paths were always neutralised, but a relative
    `../../..` walked straight out of the repo and read whatever it landed on. Every candidate
    that LEXICALLY escapes is dropped — including the not-a-file fallback, which callers go on
    to open. Lexical means `abspath`, not `realpath`, and that is a choice: a path through an
    in-repo symlink is treated as the repo's own content, because this system plants junctions
    inside repos on purpose (the portable memory store) and following them is the intended
    read. A repo that links to a file outside itself has vouched for that file.
    """
    raw = (file_path or "").strip().replace("\\", "/")
    if not raw:
        return ""
    candidates: list[str] = []
    if not os.path.isabs(raw):
        direct = raw[2:] if raw.startswith("./") else raw
        candidates.append(direct.lstrip("/"))
    candidates.append(_normalize_relative_path(repo, raw))

    repo_abs = os.path.abspath(repo)

    def contained(cand: str) -> bool:
        abspath = os.path.abspath(os.path.join(repo_abs, cand))
        return abspath == repo_abs or abspath.startswith(repo_abs + os.sep)

    inside = [c for c in candidates if c and contained(c)]
    for cand in inside:
        if os.path.isfile(os.path.join(repo_abs, cand)):
            return os.path.normpath(cand).replace("\\", "/")
    return os.path.normpath(inside[-1]).replace("\\", "/") if inside else ""


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
def _find_function_callers(repo: str, function_name: str, exclude_rel: str = "",
                           prefer: "list[str] | tuple[str, ...]" = ()) -> list[str]:
    """Call sites for `function_name`, capped at `_CALLER_SNIPPETS`, `prefer`-ed files FIRST.

    ⭐ `prefer` is not a nicety and it is not a filter — it is what makes ranking possible at all.
    This walk stops the moment it has `_CALLER_SNIPPETS` hits, so on a repo where enough
    lower-value files sort ahead of a high-value one, the high-value file is never READ, never
    returned, and no downstream sort can reorder a snippet that was never collected. Measured
    while planning SCC-187: with 12 name-match callers sorting ahead of the importer, the
    importer resolved correctly and was absent from the output entirely.

    ⛔ THE RESERVE IS WHY THIS IS RANKING AND NOT FILTERING, AND IT IS NOT OPTIONAL. Scanning the
    preferred group first with ONE shared cap has the same bug pointed the other way: on a
    well-imported module, ten importer call sites fill the cap and the walk never opens a
    non-preferred file, so the whole `[name-match]` class — attribute dispatch
    (`self.<attr>.<method>()`), the shape this module exists to surface — disappears with no note
    on either stream. Measured on this repo at review time: a finding on `wf_common.py` naming
    `read_text` returned 10 importer snippets and ZERO name-matches, where the pre-SCC-187 code
    returned the opposite. So the groups are scanned with SEPARATE budgets and the merge reserves
    a slot for the non-preferred class whenever one has a hit at all. Ordering may decide which
    evidence leads; it may never decide that a whole class of evidence is absent.

    Both groups keep `_repo_files`' sorted order, so the result stays deterministic.
    """
    ident = function_name.strip()
    if not ident or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", ident):
        return []
    pattern = re.compile(r"\b" + re.escape(ident) + r"\s*\(")
    deadline = time.monotonic() + _SEARCH_SECONDS

    def scan(group: list[str], budget: int) -> list[str]:
        """Up to `budget` call-site snippets from `group`, sharing the one outer deadline."""
        found: list[str] = []
        for rel in group:
            if len(found) >= budget:
                break
            if time.monotonic() > deadline:
                _note(f"caller search for '{ident}' hit its {_SEARCH_SECONDS}s deadline; "
                      "the list is partial")
                break
            if rel == exclude_rel:
                continue
            for idx, text in enumerate(_read_file_lines(os.path.join(repo, rel))):
                if not pattern.search(text):
                    continue
                snippet = _read_code_snippet(repo, rel, idx + 1, _CALLER_CONTEXT)
                if snippet:
                    found.append(f"{rel}:{idx + 1}\n{snippet}")
                if len(found) >= budget:
                    break
        return found

    candidates = _repo_files(repo)
    if not prefer:
        return _dedupe(scan(candidates, _CALLER_SNIPPETS))

    preferred = set(prefer)
    head = scan([rel for rel in candidates if rel in preferred], _CALLER_SNIPPETS)
    # SCC-187: always look for at least one non-preferred hit, even when the preferred group filled
    # the cap: that single scan is what keeps the other class representable.
    tail = scan([rel for rel in candidates if rel not in preferred],
                max(1, _CALLER_SNIPPETS - len(head)))
    reserve = 1 if tail else 0
    return _dedupe(head[:max(0, _CALLER_SNIPPETS - reserve)] + tail)[:_CALLER_SNIPPETS]


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


def _python_importers(repo: str, rel: str) -> "tuple[list[str], bool]":
    """(files importing `rel`, walk-completed?). The flag is a CLAIM ABOUT ABSENCE.

    A partial walk can only say which files it DID see importing `rel`; it cannot say the rest
    do not. Callers that turn "absent from this list" into a positive statement — SCC-187's
    `[name-match]` tag does exactly that — must read the flag, or a deadline silently converts an
    unknown into an assertion.
    """
    names = _python_module_names(repo, rel)
    if not names:
        return [], True

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
    complete = True
    for cand in _repo_files(repo):
        if time.monotonic() > deadline:
            _note(f"importer search for '{rel}' hit its {_SEARCH_SECONDS}s deadline; "
                  "IMPORTED BY is partial")
            complete = False
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
    return importers, complete


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
    saw_config = False
    for rel in _repo_files(repo):
        if posixpath.basename(rel) not in ("tsconfig.json", "jsconfig.json"):
            continue
        saw_config = True
        try:
            data = json.loads("\n".join(_read_file_lines(os.path.join(repo, rel))))
        except (ValueError, TypeError):
            # JSONC (comments, trailing commas) is legal in real tsconfigs and fails strict
            # json.loads. Any paths it declares are invisible here, so IMPORTED BY can read
            # empty for every aliased import -- the silent-emptiness class this file exists
            # to kill. Degrade, never die, but NAME the skip.
            _note(f"tsconfig is not strict JSON, alias paths unread: {rel}")
            continue
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

    if not roots and not saw_config:
        # Default ONLY when no config exists anywhere. A tsconfig that declares no `paths` means
        # the repo has no alias — inventing one produces confident wrong resolutions, which is
        # the exact silent failure this function documents itself as preventing.
        roots = [("@/", "src")]
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


def _ts_importers(repo: str, rel: str) -> "tuple[list[str], bool]":
    """Files that import `rel`, for TS/JS, resolved per importer rather than by name.

    A JS specifier means different things depending on who wrote it, so every candidate's
    specifiers are resolved against ITS own directory (relative), against the tsconfig that
    declared the alias (`@/`), and through `index.*` for a directory import. Matching a bare
    module string instead is what emptied IMPORTED BY for the whole TS side in the port.
    Bounded by `_SEARCH_SECONDS`: a huge repo returns a partial answer, never a hang.
    """
    aliases = _alias_roots(repo)
    deadline = time.monotonic() + _SEARCH_SECONDS
    importers: list[str] = []
    complete = True
    for cand in _repo_files(repo):
        if time.monotonic() > deadline:
            _note(f"importer search for '{rel}' hit its {_SEARCH_SECONDS}s deadline; "
                  "IMPORTED BY is partial")
            complete = False
            break
        if cand == rel or os.path.splitext(cand)[1].lower() not in _TS_EXTS:
            continue
        for text in _read_file_lines(os.path.join(repo, cand)):
            if any(_resolve_specifier(repo, cand, spec, aliases) == rel
                   for spec in _JS_SPEC_RE.findall(text)):
                importers.append(cand)
                break
    return importers, complete


def _snippet_file(snippet: str) -> str:
    """The repo-relative path out of a `<rel>:<line>\n<code>` caller snippet.

    ⚠ NOT `snippet.split(":", 1)[0]`. A snippet is multi-line and a POSIX path may legally hold a
    colon, so a first-colon split cuts `pkg/a:b.py:4` down to `pkg/a` — which is in no importer
    set, so a genuine importer gets labelled `[name-match]` while `IMPORTED BY` lists it, and the
    one package contradicts itself. Take the header LINE, then its LAST colon.
    """
    return snippet.split("\n", 1)[0].rsplit(":", 1)[0]


def _importers_of(repo: str, rel: str) -> "tuple[list[str], bool]":
    """Every file that imports `rel`, dispatched on its extension. `[]` for anything else.

    Split out of `_build_import_context`, which computed this list and kept only the formatted
    string. `_extract_one` needs the list itself — for caller ranking — and each branch below is
    a full repo walk under its own deadline, so recomputing it would cost a second walk per
    finding. One walk, two consumers.
    """
    # The skip-dir guard lives HERE, not only in `_build_import_context`. Before SCC-187 the walk
    # sat below that function's `if not rel or _under_skip_dir(rel): return ""`, so a finding on a
    # `node_modules/` path never triggered it; hoisting the call into `_extract_one` lost that and
    # bought a full 10s repo walk per skip-dir finding whose result is then discarded.
    if not rel or _under_skip_dir(rel):
        return [], True
    ext = os.path.splitext(rel)[1].lower()
    if ext == ".py":
        return _python_importers(repo, rel)
    if ext in _TS_EXTS:
        return _ts_importers(repo, rel)
    return [], True


def _build_import_context(repo: str, rel: str, importers: "list[str] | None" = None) -> str:
    """`importers` is accepted already-computed; `None` means compute it here (the pack's case)."""
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

    if importers is None:
        importers, _complete = _importers_of(repo, rel)

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
    """A unified diff -> {repo-relative path: that file's patch text}.

    Header detection is POSITIONAL, not textual. An added source line that itself begins `++ `
    renders in the body as `+++ `, and treating every such line as a file header truncates the
    real patch AND invents a bogus key. So `--- ` opens a header pair only where a header can
    be — before any file's body has started — and `+++ ` is a header only immediately after that
    `--- ` half; inside a body, both spellings are kept as content. Accepted cost: a bare
    concatenated multi-file diff with no `diff --git` separators collapses into the FIRST
    file's patch — the later files' headers and hunks are absorbed into its body, so a hunk
    lookup there can return a later file's hunk under the first file's key. Git output, which
    is what the engine feeds this, always carries the separators.
    """
    patches: dict[str, str] = {}
    key: str | None = None
    body: list[str] = []
    minus_header = False       # was the previous line the `--- ` half of a header pair?

    def flush() -> None:
        if key is not None:
            patches[key] = "\n".join(body)

    for line in (text or "").splitlines():
        if line.startswith("diff --git "):
            flush()
            key, body = None, []
            minus_header = False
        elif line.startswith("--- ") and key is None:
            minus_header = True
        elif line.startswith("+++ ") and minus_header:
            path = _normalize_patch_key(line[4:].strip())
            if path and path != "dev/null":
                key, body = path, []
            minus_header = False
        else:
            minus_header = False
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


def _extract_diff_hunk(patches: dict[str, str], rel: str, line: int) -> str:
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
    hunk = _extract_hunk_for_line(patch_lines, line)
    return "\n".join((hunk or patch_lines)[:_DIFF_HUNK_LINES])


# ── Blast radius ──────────────────────────────────────────────────────────────
def _extract_blast_radius_code(repo: str, rel: str, identifiers: list[str],
                               blast_radius: list[str]) -> str:
    """Code from the files a finding claims it also touches, capped at `_BLAST_SNIPPETS`.

    The blast-radius list arrives from the caller as untrusted strings, so each entry is
    re-resolved against the repo and dropped if it does not exist -- an asserted radius is a
    claim, not a fact. The finding's own file and anything under `_SKIP_DIRS` are excluded, or
    the lens gets its own subject back as corroboration.
    """
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
_LINE_TRUNCATED = " ...[line truncated to fit the pack budget]"


def _render_pack_block(rel: str, context: str, body_lines: list[str], total: int,
                       partial: bool = False) -> str:
    """One file's pack block. The label always states what is ACTUALLY shown.

    The label is derived here rather than passed in because a block is rendered more than once:
    at full size to measure it, then again at whatever line count its share of the char budget
    turns out to fund. A label carried in from the first render would describe the first.

    Import context goes ABOVE the body, which is a deliberate deviation from the port. pr-af
    appends it, then truncates the assembled blob -- and one 400-line file fills the whole budget
    on its own, so the context is cut off the end. Caught by running this on a real file in this
    repo (`wf_common.py`, 16093 bytes, IMPORTED BY truncated away). Keeping it above means what
    trimming eats is body lines rather than the dependency map, which is the highest value per
    byte in the pack and the reason a lens is primed at all.
    """
    shown = len(body_lines)
    if partial:
        trunc = f" (showing part of line 1 of {total})"
    elif shown < total:
        trunc = f" (showing first {shown} of {total})"
    else:
        trunc = ""
    block = f"### {rel}{trunc}"
    if context:
        block += f"\n_import/usage context:_ {context}"
    return block + "\n```\n" + "\n".join(body_lines) + "\n```"


def _fit_lines(body: list[str], room: int) -> int:
    """How many whole lines fit in `room` chars, each costing its length plus one newline."""
    used = keep = 0
    for line in body:
        if used + len(line) + 1 > room:
            break
        used += len(line) + 1
        keep += 1
    return keep


def build_pack(repo: str, target_files: list[str]) -> str:
    """Pre-read a lens's target files (+ import context) so it reasons over a primed dossier."""
    if not repo or not target_files:
        return ""
    parts: list[tuple[str, str, list[str], int]] = []
    for raw in target_files:
        # The cap counts files PACKED, not files asked for: slicing the request first let six
        # bad paths evict the one real file and produce an empty pack with a clean exit.
        if len(parts) >= _PACK_MAX_FILES:
            _note(f"pack: file cap ({_PACK_MAX_FILES}) reached; remaining targets skipped")
            break
        rel = _resolve_rel(repo, raw)
        if not rel or _under_skip_dir(rel):
            _note(f"pack: skipped (outside the repo, or under a skip-dir): {raw}")
            continue
        abspath = os.path.join(repo, rel)
        if not (os.path.isfile(abspath) and _is_text_file(abspath)):
            _note(f"pack: skipped (missing, or not a text file): {raw}")
            continue
        lines = _read_file_lines(abspath)
        if not lines:
            _note(f"pack: skipped (empty or unreadable): {raw}")
            continue
        shown = lines[:_PACK_MAX_LINES]
        body = [f"{i + 1}: {line.rstrip()}" for i, line in enumerate(shown)]
        context = _build_import_context(repo, rel)[:_PACK_IMPORT_SLICE]
        parts.append((rel, context, body, len(lines)))
    if not parts:
        _note(f"pack: nothing packed — none of the {len(target_files)} target(s) was readable")
        return ""

    full = [_render_pack_block(*p) for p in parts]
    separators = 2 * (len(full) - 1)
    if sum(len(b) for b in full) + separators <= _PACK_MAX_CHARS:
        return "\n\n".join(full)

    # Divide the budget instead of spending it first-come. The port sliced the assembled blob at
    # _PACK_MAX_CHARS, so whatever sat at the end lost: SCC-124's trial caught a real run packing
    # `task_preflight.py` at 11 of its 686 lines while quoting smaller files whole. The TOTAL cap
    # is unchanged; only its distribution is.
    #
    # Smallest block first, carrying the residue forward. A block that spends less than its share
    # -- it fits whole, or its whole lines do not divide evenly into the share -- leaves the
    # difference to the blocks after it, and the biggest file, the one trimming actually costs,
    # is served last with everything the others did not use. Without that carry, whole-line
    # rounding silently threw away up to half the budget.
    #
    # ⚠ The cost of the split, so nobody reads it as free: on a six-file change set every file
    # gets a ~2.6k share, of which the header plus the protected import context can be a third,
    # so each lands a preamble rather than a readable extent. That is still better than five
    # files packed as nothing, but it is a trade, not a win.
    blocks: dict[int, str] = {}
    remaining, left = _PACK_MAX_CHARS - separators, len(parts)
    for i in sorted(range(len(parts)), key=lambda j: len(full[j])):
        share = remaining // left if left else 0
        left -= 1
        if len(full[i]) <= share:
            blocks[i] = full[i]
            remaining -= len(full[i])
            continue
        rel, context, body, total = parts[i]
        # Whole lines, never mid-line: a lens reading half a statement reasons about a syntax
        # error that is not in the file. Step back after rendering -- the label's own digit
        # count shifts as lines drop, so the arithmetic can overshoot by a character or two.
        keep = _fit_lines(body, share - len(_render_pack_block(rel, context, [], total)))
        block = None
        if keep:
            block = _render_pack_block(rel, context, body[:keep], total)
            while len(block) > share and keep > 1:
                keep -= 1
                block = _render_pack_block(rel, context, body[:keep], total)
        elif body:
            # A file can be ONE line -- minified JS, a lock file, a base64 data URI -- and a
            # whole-lines rule alone would render an empty fence under its header, telling the
            # lens the file is empty. That is the single most dangerous thing a primer can say,
            # so this one case degrades to a marked partial line instead.
            room = share - len(_render_pack_block(rel, context, [""], total, True))
            if room > len(_LINE_TRUNCATED):
                head = body[0][:room - len(_LINE_TRUNCATED)] + _LINE_TRUNCATED
                block = _render_pack_block(rel, context, [head], total, True)
        if block is None or len(block) > share:
            # Dropping beats emitting a header over an empty fence: absent from the pack, the
            # lens still has the live file: present but empty, it has a false fact.
            _note(f"pack: {rel} dropped — a {share}-char share cannot carry its header and a line")
            continue
        if len(block) < len(full[i]):
            _note(f"pack: {rel} trimmed to fit a {share}-char share of the "
                  f"{_PACK_MAX_CHARS}-char budget across {len(parts)} file(s)")
        blocks[i] = block
        remaining -= len(block)
    # No final slice: every block was measured against its own share and sum(shares) never
    # exceeds the budget, so the whole-line guarantee cannot be undone by a trailing cut.
    return "\n\n".join(blocks[i] for i in sorted(blocks))


# ── Mode 2: per-finding evidence ──────────────────────────────────────────────
def _extract_one(repo: str, finding: dict, patches: dict[str, str],
                 blast_radius: list[str]) -> dict:
    """One finding's `EvidencePackage`, as a dict carrying all six fields -- always.

    Every field is present even when empty, because a consumer that has to distinguish "absent"
    from "nothing found" will get it wrong. A finding naming a file that does not exist, or a
    line past the end of one, yields empty strings and exit 0: this primes a reviewer, so it
    degrades rather than dying and taking the other findings' evidence with it.
    """
    title = str(finding.get("title") or "")
    rel = _resolve_rel(repo, str(finding.get("file_path") or ""))
    try:
        line = int(finding.get("line_start") or 1)
    except (TypeError, ValueError, OverflowError):
        # OverflowError is real input, not paranoia: JSON accepts `1e400`, which parses to
        # float infinity, and int(inf) raises it. Uncaught, it escaped the thread pool and
        # destroyed every OTHER finding's evidence with it.
        line = 1

    blob = "\n".join(str(finding.get(key) or "") for key in ("title", "body", "evidence"))
    identifiers = _extract_mentioned_identifiers(blob)[:_MAX_IDENTIFIERS_PER_FINDING]

    primary = _read_code_snippet(repo, rel, line, _PRIMARY_CONTEXT)
    if not primary:
        _note(f"finding {title!r}: no readable code at "
              f"{str(finding.get('file_path') or '')!r} line {line}")

    # Who imports the finding's file, computed ONCE and spent twice: as the caller search's scan
    # order, and as the rank tag below. `_build_import_context` takes it too, so the walk that
    # produces it happens once per finding rather than once per consumer.
    importers, importers_complete = _importers_of(repo, rel)
    importer_set = set(importers)

    # ⛔ SCC-187 — TAG AND ORDER, NEVER FILTER. A name-match hit is weaker evidence, not absent:
    # dropping it would take attribute-dispatch call sites (`self.<attr>.<method>()`) with it,
    # and that is precisely the shape this file exists to surface. The tag lets the reader
    # discount a hit; a filter would decide for them, invisibly.
    # ⚠ SCC-187 review finding — `[name-match]` is a CLAIM THAT THIS FILE DOES NOT IMPORT THE
    # SUBJECT, which the code asserted unconditionally. A truncated
    # importer walk cannot support it: the file may simply sit past where the walk stopped. A
    # deadline must degrade the label to an honest unknown rather than assert the negative — the
    # note that says the walk was partial goes to stderr, which no consumer of stdout ever reads.
    unknown = "[name-match] " if importers_complete else "[unranked] "
    tagged = ["[importer] " + snippet if _snippet_file(snippet) in importer_set
              else unknown + snippet
              for ident in identifiers
              for snippet in _find_function_callers(repo, ident, rel, importers)]
    # SCC-187: stable, and BEFORE the cap — this slice runs across up to
    # `_MAX_IDENTIFIERS_PER_FINDING`
    # identifiers, so one noisy identifier can fill all ten slots on its own. Sorting after the
    # slice would rank ten snippets that had already lost the importer.
    tagged.sort(key=lambda snippet: 0 if snippet.startswith("[importer] ") else 1)
    callers = _dedupe(tagged)[:_CALLER_SNIPPETS]

    cross_refs = _dedupe([
        _read_code_snippet(repo, path, 1, _PRIMARY_CONTEXT)
        for path in _extract_mentioned_file_paths(blob, repo)[:_CROSS_REF_FILES]
    ])

    return {
        "finding_title": title,
        "primary_code": primary,
        "caller_snippets": callers,
        "cross_ref_snippets": cross_refs,
        "diff_hunk": _extract_diff_hunk(patches, rel, line),
        "import_context": _build_import_context(repo, rel, importers),
        "related_code": _extract_blast_radius_code(repo, rel, identifiers, blast_radius),
    }


def _safe_extract(repo: str, finding: dict, patches: dict[str, str],
                  blast_radius: list[str]) -> dict:
    """The contract boundary: one poisoned finding degrades to an empty package, WITH a note.

    `_extract_one` absorbs every malformed-input shape it can see coming; this catch is for the
    one it cannot, because an exception here propagates out of `pool.map` and destroys every
    OTHER finding's evidence with it — the exact failure the contract forbids.
    """
    try:
        return _extract_one(repo, finding, patches, blast_radius)
    except Exception as exc:  # noqa: BLE001 — deliberate: degrade one, never kill all
        title = ""
        try:
            title = str(finding.get("title") or "")
        except Exception:
            pass
        _note(f"finding {title!r} degraded to an empty package: {exc!r}")
        return {
            "finding_title": title,
            "primary_code": "",
            "caller_snippets": [],
            "cross_ref_snippets": [],
            "diff_hunk": "",
            "import_context": "",
            "related_code": "",
        }


def extract_for_findings(repo: str, findings: list[dict], patches: dict[str, str],
                         blast_radius: list[str]) -> list[dict]:
    """One `EvidencePackage` per finding, as a LIST in the caller's finding order — ALWAYS
    one per input entry, junk included (a non-dict or titleless entry degrades in place).

    Not a dict keyed by title: duplicate titles are the EXPECTED case for a multi-lens fan-out
    over one diff, and keying by title silently collapsed them onto one package carrying the
    wrong file's code. Order is input order, so an index join is always available — which is
    exactly why nothing may be dropped: titles being non-unique makes the index THE join, and
    a silent drop would misassign every package after it.
    """
    if not findings:
        return []
    _repo_files(repo)          # build the index BEFORE the pool, so workers only read it
    _alias_roots(repo)
    with ThreadPoolExecutor(max_workers=_EXTRACT_WORKERS) as pool:
        return list(pool.map(
            lambda finding: _safe_extract(repo, finding, patches, blast_radius), findings))


# ── CLI ───────────────────────────────────────────────────────────────────────
def _read_input(source: str) -> str:
    if source == "-":
        return sys.stdin.read()
    with open(source, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def main(argv: list[str] | None = None) -> int:
    # Repo content is arbitrary text and a cp1252 console (the Windows default) cannot encode
    # all of it; the run must degrade a character, never die. hasattr-guarded because a captured
    # or StringIO stream has no reconfigure.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
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
    if args.pack and (args.diff or args.blast_radius):
        parser.error("--diff and --blast-radius apply to --findings only")
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

    # No pre-filter: every input entry yields exactly one package, IN PLACE. Titles are not
    # unique (H-2), so a consumer's only reliable join is by index -- silently dropping a
    # titleless or non-dict entry would misassign every package after it. Junk degrades
    # inside _safe_extract, with a note.
    result = extract_for_findings(repo, findings, patches, list(args.blast_radius))
    sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
