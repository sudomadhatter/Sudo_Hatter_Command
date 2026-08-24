#!/usr/bin/env python3
"""Resolve every Markdown link path and `#L` anchor a diff touched — the LAST unscripted gate row.

⛔ WHY THIS FILE EXISTS.

`/smh-clean-code-audit` Step 1 is the command centre's machine floor. Every row is a real command
with a real exit code — except one:

    | **Link + anchor** | resolve every Markdown link path and every `#L` anchor the diff touched |

That row is PROSE. It names no command, so every agent improvises a matcher, and an improvised
matcher is worse than none: on SCC-285 one reported **31 unresolved paths**, ~30 of them false —
it did not know this repo cites scripts short (`tests/test_twin_parity.py` for the real
`.agents/scripts/tests/test_twin_parity.py`), so it called live files dead. A gate that cries wolf
thirty times teaches the reader to skip the one real hit. Operator, 2026-08-22: *"how are we still
having to manually prove these commands?"*

⛔ THE FIVE CONVENTIONS THAT MAKE A NAIVE `Path.exists()` WRONG HERE. Every one is a measured false
positive from this file's own first draft — which is why `tests/test_check_links.py` pins all five:

  1. SHORT CITATIONS. Docs cite a TAIL — `tests/test_x.py`, `scripts/INDEX.md`. Resolved by
     unambiguous suffix match against the tracked set.
  2. RELATIVE LINKS. `](../../.agents/rules/jira.md)` from `docs/_scc_sops_prds/` resolves from the
     CITING FILE's directory. `..` must be normalised, not string-stripped.
  3. THE BRANCH, NOT `main`. The first draft resolved against the main checkout's index to dodge
     convention 4 — and every file this lane ADDED read as dead. Tracked set comes from the
     worktree; the main checkout is consulted only as an existence fallback.
  4. WORKTREE ABSENCE. A gitignored asset (`docs/migrations/auth_keys/...`) lives in the main
     checkout and not in a worktree — `link-worktree-assets.py` links a different set. Alive in the
     repo, absent here. Hence the fallback in 3.
  5. NOT EVERY TOKEN IS A CLAIM. URLs, directories, fenced examples and placeholders
     (`<KEY>`, `path/to/x`) are not assertions that a file exists.

⭐ WHAT IT GATES ON, stated once: a path a DOC CLAIMS exists, that does NOT — the defect
`relocated-doc-links-are-mispathed-not-dead` names, where a lane moves a file and every citation of
it keeps resolving in the author's head and nowhere else.

Usage — diff-scoped by default, the only scope the audit gates on:

    python3 .agents/scripts/check_links.py --base origin/main
    python3 .agents/scripts/check_links.py --paths a.md b.md
    python3 .agents/scripts/check_links.py --all          # whole tree, report-only sweep

Exit 0 clean · 1 unresolved references found · 2 could not run.
Stdlib only, no venv. Never names an interpreter internally (`python3` Mac / `python` PC).
"""
from __future__ import annotations

import argparse
import posixpath
import re
import subprocess
import sys
from pathlib import Path

LINK = re.compile(r"\]\(\s*([^)\s#]+?)\s*(#[^)\s]*)?\s*\)")
TICKED = re.compile(r"`([^`\n]+?)`")
ANCHOR_L = re.compile(r"^#L(\d+)(?:-L(\d+))?$")

# A backticked token is a path CLAIM only with a separator AND a known extension. Without the
# extension test, prose like `_artifacts/` and every `a/b` fragment becomes a finding.
PATHISH = re.compile(r"^[\w./@-]+/[\w./@-]*\.(md|py|ps1|sh|json|ya?ml|txt|cjs|js|ts|tsx|toml|cfg)$")

# Convention 5. A doc showing the SHAPE of a path is not claiming one exists.
PLACEHOLDER = re.compile(
    r"<[^>]+>|\{[^}]+\}|\.\.\.|\*|"
    r"\b(path/to|your|example|some|foo|bar|baz|NAME|SLUG|KEY)\b",
    re.I,
)
URL = re.compile(r"^(https?|mailto|ftp|file):", re.I)
FENCE = re.compile(r"^\s*(```|~~~)")

# Convention 6. A `cicd-*` command acts on a CHILD PROJECT, so it cites that project's tree —
# `backend/requirements.txt`, `_bmad-output/sudo-tests.yaml`. Those paths are correct and simply do
# not exist in the lobby. Resolving them would need the target repo, which the audit does not bind.
PROJECT_ROOTS = ("backend/", "frontend/", "firebase/", "functions/", "mobile/",
                 "_bmad-output/", "_bmad/", "docs/stories/")

# Convention 7. A NARRATIVE LEDGER records what a session did, including deleting things. A row
# naming a file that a later lane removed is HISTORY, not a broken link — the same carve-out
# `check_maps.py` makes with its own `NARRATIVE_LEDGERS`. Kept in step with that file deliberately:
# two dead-path checkers with different exemption sets would disagree on the same tree.
# ⛔ `active-context.md` BELONGS HERE, and the authority is `check_maps.py`, not a preference.
# That file carries `PRUNE_KEEP_BLOCKS = 10` — the house already models a continuity brief as a
# chronological log of DATED session blocks whose old end is PRUNED, never repaired. So a path
# inside a five-week-old block is a mention in a record, and the remedy for a stale one is the
# prune, which is that script's job. Measured cost of adding it, stated so nobody has to
# rediscover it: 11 real dead paths in the lobby's brief stop being reported here — every one
# inside a 2026-07 block, and one of which the prose ITSELF records as permanently lost and
# deliberately de-linked on 2026-08-12. What this does NOT excuse is a stale pointer in the
# LIVE header, and that is not a gap this exemption opens: the stale SOP path fixed at
# `active-context.md:9` this lane was prose, not a path claim, so no version of this checker
# ever saw it. The brief is 5x over its declared 20 KB budget; the prune is what it is owed.
NARRATIVE_LEDGERS = ("_artifacts/INDEX.md", "_artifacts/_main/INDEX.md",
                     "_artifacts/_main/active-context.md")


def _strip_dot_slash(p: str) -> str:
    """Drop a leading `./`, and NOTHING else.

    ⛔ NOT `p.lstrip("./")`. `lstrip` takes a character SET, so it eats the leading dot off every
    `.agents/...` path and turns it into `agents/...`, which matches nothing — so the checker
    reports every house rule and command as a dead link. This exact trap is already written down
    in `sop_currency.py`'s `_norm()`, where it shipped for one test run; this file walked into it
    anyway on its second draft, which is why the case is pinned in `tests/test_check_links.py`.
    """
    while p.startswith("./"):
        p = p[2:]
    return p


def run(args: list[str], cwd: Path) -> str:
    r = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} -> {r.returncode}: {r.stderr.strip()[:200]}")
    return r.stdout


def strip_fences(text: str) -> str:
    """Blank fenced blocks, preserving line numbers so reports stay accurate."""
    out, inside = [], False
    for line in text.splitlines():
        if FENCE.match(line):
            inside = not inside
            out.append("")
            continue
        out.append("" if inside else line)
    return "\n".join(out)


# ⛔ A GENERATED BLOCK IS MACHINE OUTPUT, NOT AUTHORED LINKS (SCC-288). `docs/doc-graph.md`'s
# AUTO block is a REPORT whose whole job is to LIST the dangling references the graph found, and
# every one of them is a backticked path this checker's LINK pattern matches. Read literally, the
# graph's 40 findings became 40 findings of this checker's own, in a file no human wrote a link
# into. `generate_doc_graph.strip_auto()` already draws this exact line for the same reason; this
# is the same rule applied by the other reader of the same files. The sentinels are the ones the
# two generators splice on.
AUTO_SENTINEL = re.compile(r"<!--\s*(?:REPO-MAP|DOC-GRAPH):AUTO-(START|END)\s*-->")


def strip_auto(text: str) -> str:
    """Blank generated AUTO blocks, preserving line numbers so reports stay accurate.

    ⛔ AN UNPAIRED `START` STRIPS NOTHING. A line scanner that latches `inside` on `START` and
    only clears it on `END` goes SILENT over the whole remainder of a file whose `END` is missing
    — a truncated write, an interrupted `_land`, a hand-edit of the curated header. That is the
    link gate switching itself off at the exact moment the file is known to be corrupt. So the
    pairs are resolved FIRST, and only a block with both ends is blanked; a dangling sentinel is
    left in place and its content stays checked. `generate_doc_graph.AUTO_BLOCK_RE` reaches the
    same answer by requiring a matching `END` in the pattern — this is that rule, line-wise.
    """
    lines = text.splitlines()
    blank, open_at = set(), None
    for i, line in enumerate(lines):
        m = AUTO_SENTINEL.search(line)
        if not m:
            continue
        if m.group(1) == "START":
            open_at = i                       # a second START just re-opens; the last one wins
        elif open_at is not None:
            blank.update(range(open_at, i + 1))
            open_at = None
    return "\n".join("" if i in blank else ln for i, ln in enumerate(lines))


def candidates(text: str):
    """Yield (line_no, token, anchor) for every token that CLAIMS to be a path."""
    for n, line in enumerate(strip_auto(strip_fences(text)).splitlines(), 1):
        for m in LINK.finditer(line):
            yield n, m.group(1), m.group(2)
        for m in TICKED.finditer(line):
            tok = m.group(1).strip()
            if PATHISH.match(tok):
                yield n, tok, None


class Resolver:
    def __init__(self, worktree: Path, main_checkout: Path | None, tracked: set[str] | None = None):
        self.worktree = worktree
        self.main = main_checkout
        # Convention 3: the BRANCH's index, so files this lane added resolve.
        # `tracked` is injectable so `tests/test_check_links.py` can pin every convention against a
        # synthetic file set instead of whatever this repo happens to contain today — a test that
        # reads the live tree passes or fails for reasons that have nothing to do with the code.
        self.tracked = tracked if tracked is not None else set(run(["git", "ls-files"], worktree).split())
        self.dirs = {d for f in self.tracked for d in _ancestors(f)}
        self.by_suffix: dict[str, list[str]] = {}
        for f in self.tracked:
            parts = f.split("/")
            for i in range(1, len(parts)):
                self.by_suffix.setdefault("/".join(parts[i:]), []).append(f)

    def resolve(self, token: str, citing: str) -> str | None:
        tok = token.rstrip("/")
        # Convention 2: normalise `..` against the citing file's directory.
        rel = posixpath.normpath(posixpath.join(posixpath.dirname(citing), tok))
        for cand in (tok, rel):
            cand = _strip_dot_slash(cand)
            if not cand or cand.startswith(".."):
                continue
            if cand in self.tracked or cand in self.dirs:
                return cand
            if (self.worktree / cand).exists():
                return cand
            # Convention 4: gitignored assets live only in the main checkout.
            if self.main and (self.main / cand).exists():
                return cand
        # Convention 1: an unambiguous suffix match is a resolve.
        hits = self.by_suffix.get(_strip_dot_slash(tok))
        if hits:
            return hits[0]
        return None


def _ancestors(path: str):
    parts = path.split("/")[:-1]
    for i in range(1, len(parts) + 1):
        yield "/".join(parts[:i])


def check_anchor(root: Path, target: str, anchor: str) -> str | None:
    """`#L12-L20` must name lines the target actually has."""
    m = ANCHOR_L.match(anchor)
    if not m:
        return None
    start, end = int(m.group(1)), int(m.group(2) or m.group(1))
    p = root / target
    if not p.is_file():
        return None
    total = len(p.read_text(encoding="utf-8", errors="replace").splitlines())
    if end < start:
        return f"anchor {anchor} ends before it starts"
    if start > total or end > total:
        return f"anchor {anchor} exceeds {target}'s {total} lines"
    return None


def scan(worktree: Path, resolver: Resolver, files: list[str]):
    dead, anchors, checked = [], [], 0
    for f in files:
        p = worktree / f
        if not p.is_file():
            continue
        ledger = f.endswith(NARRATIVE_LEDGERS)      # convention 7
        for n, tok, anc in candidates(p.read_text(encoding="utf-8", errors="replace")):
            if URL.match(tok) or PLACEHOLDER.search(tok):
                continue
            if tok.startswith(PROJECT_ROOTS):       # convention 6
                continue
            if ledger:
                continue
            checked += 1
            target = resolver.resolve(tok, f)
            if target is None:
                dead.append(f"{f}:{n}  ->  {tok}")
            elif anc:
                bad = check_anchor(worktree, target, anc)
                if bad:
                    anchors.append(f"{f}:{n}  ->  {bad}")
    return dead, anchors, checked


def main() -> int:
    ap = argparse.ArgumentParser(description="Resolve markdown path claims and #L anchors.")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--base", help="diff against this ref, e.g. origin/main")
    ap.add_argument("--paths", nargs="*")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()

    try:
        wt = Path(run(["git", "rev-parse", "--show-toplevel"], Path(a.repo).resolve()).strip())
        common = Path(run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], wt).strip())
        main_checkout = common.parent if (common.parent / ".git").exists() else None
        res = Resolver(wt, main_checkout if main_checkout != wt else None)
    except Exception as e:
        print(f"check_links: cannot run - {e}", file=sys.stderr)
        return 2

    untracked: list[str] = []          # SCC-303: filled on the --base path only
    if a.paths:
        files = [f for f in a.paths if f.endswith(".md")]
    elif a.all:
        files = sorted(f for f in res.tracked if f.endswith(".md"))
    else:
        base = a.base or "origin/main"
        try:
            files = [f for f in run(["git", "diff", "--name-only", f"{base}...HEAD"], wt).split()
                     if f.endswith(".md")]
        except Exception as e:
            print(f"check_links: cannot diff against {base} - {e}", file=sys.stderr)
            return 2
        # ⛔ SCC-303: `git diff --name-only` is tracked-only BY CONSTRUCTION, so an untracked
        # markdown file - the lane's own walkthrough, at exactly the moment the gate runs - was
        # never scanned, and the run printed a clean count over a set it had narrowed silently.
        # Untracked .md under the DIFF'S directories is swept in and scanned like anything else;
        # untracked files elsewhere stay out of scope (a stray note is not this diff's business).
        try:
            others = [u for u in run(["git", "ls-files", "--others", "--exclude-standard"],
                                     wt).split() if u.endswith(".md")]
        except Exception:
            others = []
        dirs = {str(Path(f).parent) for f in files}
        untracked = [u for u in others
                     if str(Path(u).parent) in dirs
                     or any(str(Path(u)).startswith(d + "/") for d in dirs if d != ".")]
        files += [u for u in untracked if u not in files]

    if not files:
        # ⛔ An empty input is NOT a pass (`tests-must-gate-for-real` §5). Say so plainly.
        print("check_links: no markdown in scope - nothing was checked (this is not a pass)")
        return 0

    dead, anchors, checked = scan(wt, res, files)
    print(f"check_links: {len(files)} markdown file(s), {checked} path claim(s) checked")
    # SCC-303: the NAMES, every run - a count cannot distinguish "all clean" from "one file
    # was invisible", and that ambiguity is what shipped four dead paths under a green gate.
    swept = set(untracked)
    for f in files:
        print(f"  [scanned] {f}" + ("  (untracked - swept in)" if f in swept else ""))
    for d in sorted(set(dead)):
        print(f"  [dead]   {d}")
    for x in sorted(set(anchors)):
        print(f"  [anchor] {x}")
    if dead or anchors:
        print(f"\n{len(set(dead))} unresolved path(s), {len(set(anchors))} bad anchor(s)")
        return 1
    print("  clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
