"""scope_check.py — does this work touch a critical surface? (SCC-443, 2026-09-10)

The quick lane exists because most work is a UI fix, a document, a file update — and it needs a
LINE or it becomes the default because it is faster. The line is a list of critical surfaces
(auth, billing, security rules, FAA-facing answers, CI), declared per repo, and this script
answers one question from PATHS: does the planned set — or the real diff — touch one?

    scope_check.py --repo <abs path> (--paths P [P ...] | --diff <base>)

    CLEAR      nothing named touches a critical surface                              (exit 0)
    OVERLAP    one line per hit follows: `<path>  <surface>: <why>` — the agent STOPS  (exit 3)
    ERROR      the check could not run: empty --paths, an unreadable map, a --diff    (exit 2)
               base git cannot resolve. Silence is UNKNOWN scope, never clear.

  ── READ THE WORD, NOT THE EXIT CODE ───────────────────────────────────────────────────────
The verdict is a bare word on the first line, because a piped gate reports the PIPE's status,
not the script's (`lane_qualify.py:24-27`). The exit code is there for scripts.

  ── THE STOP IS SOFT, AND THE SCRIPT HAS NO PART IN LIFTING IT ─────────────────────────────
`OVERLAP` means: stop, print the lines, say in one sentence what the full lane would cost, and
wait. The only thing that moves the lane past this point is the operator's word in this turn,
quoted verbatim into the plan (`.agents/rules/critical-surfaces.md` § The wire-in). There is
no override flag here on purpose: a flag is a thing an agent can pass, a quoted sentence is
not. The script never prompts, never reads an answer, never writes anything.

  ── WHERE THE LIST LIVES ───────────────────────────────────────────────────────────────────
`<repo>/.agents/critical-surfaces.json` — each repo declares its own paths (project law stays
in the project). A path ending in `/` is a prefix; anything else is an exact repo-relative file.
That is `classify_changes.py`'s convention in AviationChat and `sop_currency._SURFACES`'s, and
it is what keeps `backend-notes/` from matching `backend/`. A repo with no map gets the generic
set below and a LOUD line (`MAP: none for <repo> - generic surfaces only`), so an unmapped repo
is never silently clear. A map that exists and does not parse is an ERROR, never a fallback.

  ── WHY THE GENERIC FRAGMENTS MATCH A SEGMENT, NEVER A SUBSTRING ───────────────────────────
`auth` as a substring makes `docs/author-guide.md` a critical surface in every unmapped repo,
and a soft stop that fires on a docs lane is the first thing the operator switches off. A
fragment matches a whole path segment, or a segment prefix followed by `_`, `-` or `.`
(`auth/`, `auth_service.py`, `auth-wall.spec.ts`, `session.ts`), and nothing else.

  ── --diff IS THE MERGE-BASE DIFF ──────────────────────────────────────────────────────────
`--diff <base>` reads what THIS branch changed since it forked from `<base>` — the two-argument
form `wf_common.changed_since_fork` uses, never the two-dot range (`risk_seam.py` names the
two-dot mistake as the expensive one). It counts committed changes only and prints how many it
compared (`DIFF: <n> file(s) vs <base>`); the eject tripwire runs it after the lane's last commit.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wf_common import changed_since_fork, git  # noqa: E402

MAP_REL = ".agents/critical-surfaces.json"
EXIT = {"CLEAR": 0, "OVERLAP": 3, "ERROR": 2}

# The generic set, for a repo that declared no map. (surface, pattern, why) — a pattern ending
# in "/" is a prefix, "*.<ext>" a suffix, a bare word a path-segment fragment, anything else an
# exact repo-relative file.
GENERIC: tuple[tuple[str, str, str], ...] = (
    ("ci", ".github/", "a workflow or gate edit changes what green means for everyone"),
    ("ci", ".agents/hooks/", "a hook edit changes what every session is allowed to do"),
    ("ci", ".agents/scripts/git-hooks/", "a commit gate: arming or re-scoping it is a usage change for everyone"),
    ("ci", ".githooks/", "the hook dispatchers: a silent exit 0 here switches a gate off"),
    ("rules", "*.rules", "Firestore and Storage rules are the last wall; the constitution says ask first"),
    ("rules", "firebase.json", "the deploy topology: which rules file guards which store"),
    ("auth", "auth", "a wrong line here is every user's account"),
    ("auth", "session", "a wrong line here is every user's session"),
    ("billing", "billing", "a wrong line here is revenue or a runaway bill"),
    ("billing", "payment", "a wrong line here is revenue or a runaway bill"),
    ("billing", "entitlement", "a wrong line here is what a paying user is allowed to do"),
)


def norm(path: str) -> str:
    """Normalize for prefix comparison. NOT `lstrip("./")` — that is a character SET and eats
    the leading dot off every `.agents/...` path (`sop_currency._norm`, `lane_qualify.norm`)."""
    p = path.replace("\\", "/").strip()
    while p.startswith("./"):
        p = p[2:]
    return p


def segment_hit(path: str, fragment: str) -> bool:
    """A fragment matches a whole path segment, or a segment prefix followed by `_` `-` `.`."""
    for seg in path.lower().split("/"):
        if seg == fragment:
            return True
        if seg.startswith(fragment) and len(seg) > len(fragment) and seg[len(fragment)] in "_-.":
            return True
    return False


def pattern_hit(path: str, pattern: str, *, fragments: bool) -> bool:
    if pattern.endswith("/"):
        return path.startswith(pattern)
    if pattern.startswith("*."):
        return path.endswith(pattern[1:])
    if fragments and "/" not in pattern and "." not in pattern:
        return segment_hit(path, pattern)
    return path == pattern


def load_map(repo: Path) -> tuple[list[tuple[str, str, str]] | None, str | None]:
    """The repo's declared surfaces as (surface, pattern, why) rows, or None when no map exists.
    The second value is an error message when a map exists and cannot be read."""
    f = repo / MAP_REL
    if not f.is_file():
        return None, None
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return None, f"{MAP_REL} could not be read: {e}"
    surfaces = data.get("surfaces") if isinstance(data, dict) else None
    if not isinstance(surfaces, dict):
        return None, f"{MAP_REL} has no `surfaces` object"
    rows: list[tuple[str, str, str]] = []
    for name, spec in surfaces.items():
        if not isinstance(spec, dict) or not isinstance(spec.get("paths"), list):
            return None, f"{MAP_REL}: surface `{name}` needs a `paths` list"
        why = str(spec.get("why", "")).strip() or "declared critical by this repo's map"
        for p in spec["paths"]:
            rows.append((str(name), norm(str(p)), why))
    return rows, None


def overlaps(paths: list[str], rows: list[tuple[str, str, str]], *,
             fragments: bool) -> list[tuple[str, str, str]]:
    hits: list[tuple[str, str, str]] = []
    for path in paths:
        for surface, pattern, why in rows:
            if pattern_hit(path, pattern, fragments=fragments):
                hits.append((path, surface, why))
                break  # one line per path, the first surface that claims it
    return hits


def diff_paths(repo: Path, base: str) -> tuple[list[str] | None, str | None]:
    """What HEAD changed since it forked from `base` — the merge-base diff."""
    mb = git(["merge-base", base, "HEAD"], repo)
    fork = mb.stdout.strip() if mb.returncode == 0 else ""
    if not fork:
        return None, f"git merge-base {base} HEAD failed: {(mb.stderr or mb.stdout).strip()}"
    return sorted(changed_since_fork(repo, "HEAD", fork)), None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Does this work touch a critical surface? (SCC-443)")
    ap.add_argument("--repo", required=True, help="repo root, absolute - never the cwd")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--paths", nargs="*", help="the planned set (Step 1 of the quick lane)")
    src.add_argument("--diff", metavar="BASE",
                     help="the real diff: what HEAD changed since it forked from BASE (the tripwire)")
    args = ap.parse_args(argv)

    repo = Path(args.repo).resolve()
    info: list[str] = []
    if args.diff is not None:
        paths, err = diff_paths(repo, args.diff)
        if err:
            print("ERROR")
            print(err)
            return EXIT["ERROR"]
        info.append(f"DIFF: {len(paths)} file(s) vs {args.diff}")
    else:
        paths = [norm(p) for p in (args.paths or []) if norm(p)]
        if not paths:
            print("ERROR")
            print("no paths given - that is UNKNOWN scope, not empty scope; silence is never clear")
            return EXIT["ERROR"]

    rows, err = load_map(repo)
    if err:
        print("ERROR")
        print(err)
        return EXIT["ERROR"]
    if rows is None:
        info.insert(0, f"MAP: none for {repo} - generic surfaces only")
        rows, fragments = list(GENERIC), True
    else:
        fragments = False

    hits = overlaps(paths, rows, fragments=fragments)
    print("OVERLAP" if hits else "CLEAR")
    for line in info:
        print(line)
    for path, surface, why in hits:
        print(f"{path}  {surface}: {why}")
    return EXIT["OVERLAP" if hits else "CLEAR"]


if __name__ == "__main__":
    raise SystemExit(main())
