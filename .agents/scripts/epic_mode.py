"""epic_mode.py — which epic mode is this project on? ONE query, the word first. (SCC-446)

    epic_mode.py --repo <abs path>

    TRUNK                                    no origin/epic/* at all                      (exit 0)
    FULL  epic/<KEY>-epic-<N>-<slug>         no `-light-epic-` anywhere in the name       (exit 0)
    LIGHT epic/<KEY>-light-epic-<N>-<slug>   the name CONTAINS `-light-epic-`             (exit 0)
    AMBIGUOUS                                two or more live epics; the refs follow      (exit 2)
    ERROR                                    not a git repo, or git failed; the reason    (exit 2)

Line 1 is the bare word (a piped gate reports the PIPE's status, not the script's - read the word).
Line 2 is the landing cost the operator reads: where a story lands, which checks run, when E2E runs.

  ── WHY A SCRIPT, AND WHY ORIGIN DECIDES ───────────────────────────────────────────────────
The mode is chosen once by the operator at kickoff and carried in the branch NAME (git-policy § The
epic's mode). Every branch-touching door used to carry its own `for-each-ref` query and read a
`-quickdev` suffix nothing ever cut; twelve doors now call this at the top of Step 0 and echo both
lines, so an agent knows which epic it is on from command output, never from belief. Only
REMOTE-tracking refs are read: a local epic head is a cache that outlives the epic it belonged to,
and a stale one must not turn a trunk project back into an epic project. The caller fetches first
(`git fetch origin --prune`, as every door's Step 0 does); this script makes no network call.

  ── THE TOKEN ──────────────────────────────────────────────────────────────────────────────
`-light-epic-` after the key is the whole switch - the same substring the epic ruleset globs and
the one a repo's `pr-check.yml` will read with `contains()` once that repo arms it (AVCH-152 for
AviationChat; today no repo does, and `light_armed` below derives that from the repo and says so
on the cost line). The word `light` anywhere else in the slug is not it.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wf_common import git  # noqa: E402

EXIT = {"TRUNK": 0, "FULL": 0, "LIGHT": 0, "AMBIGUOUS": 2, "ERROR": 2}
LIGHT_TOKEN = "-light-epic-"

COST = {
    "TRUNK": "lands on main by a PR the operator merges; main's ruleset checks; E2E at that PR",
    "FULL": "lands by PR into {branch}; four checks; E2E on every landing",
    "LIGHT": ("lands by PR into {branch}; two checks (Backend (Python), Frontend (Node.js)); "
              "E2E once at /cicd-push-e2e, or /cicd-e2e on demand"),
}


def live_epics(repo: Path) -> tuple[list[str] | None, str]:
    """The epic branches on ORIGIN, as `epic/...` names; (None, why) when git could not answer."""
    r = git(["for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/epic/*"], repo)
    if r.returncode != 0:
        return None, (r.stderr or r.stdout).strip() or f"git for-each-ref failed in {repo}"
    names = []
    for line in r.stdout.splitlines():
        ref = line.strip()
        if not ref:
            continue
        names.append(ref[len("origin/"):] if ref.startswith("origin/") else ref)
    return sorted(names), ""


def _closing_quote(line: str, start: int) -> int:
    """Index of the quote that closes the one opened at `start`, or -1 when nothing does.
    Inside a double-quoted scalar a backslash escapes the next character."""
    quote = line[start]
    i = start + 1
    while i < len(line):
        if quote == '"' and line[i] == "\\":
            i += 2
            continue
        if line[i] == quote:
            return i
        i += 1
    return -1


def uncommented(line: str) -> str:
    """`line` with its YAML comment removed, or unchanged when it has none.

    A `#` opens a comment only when it starts the line or follows whitespace, and only outside
    a quoted scalar - the `#` in `"build #4 targets -light-epic-"` is not a comment. Inside a
    double-quoted scalar a backslash escapes the next character, so `"a \\" b"` closes at its
    second bare quote, not its first. A quote nothing closes is an apostrophe, not a scalar
    (`echo it's fine   # ...`): it is plain text, and the scan keeps looking for the marker.

    ⛔ THE ESCAPE AND THE APOSTROPHE BOTH OVER-REPORTED ARMED (SCC-441 review, reproduced): the
    first cut ended a quote at any matching character and never closed an unmatched one, so a
    token living only in a trailing comment survived either shape, the NOT-ARMED caveat went
    quiet, and the cost line promised the discount in a repo still running four checks."""
    i = 0
    while i < len(line):
        ch = line[i]
        if ch in "\"'":
            end = _closing_quote(line, i)
            if end != -1:
                i = end + 1
                continue
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i]
        i += 1
    return line


def light_armed(repo: Path) -> bool:
    """Does THIS repo's CI actually read the `-light-epic-` token yet?

    ⛔ THE COST LINE IS A PROMISE, AND AN UNARMED REPO BREAKS IT (SCC-446 review, reproduced).
    LIGHT is a local convention until a repo's `pr-check.yml` skips its E2E jobs on the token —
    which today NO repo does (AVCH-152 is the lane that arms AviationChat, and the skeleton every
    new project clones ships no classifier either). Printing "two checks, E2E once" in a repo that
    still runs all four is the worst kind of wrong: the operator chose LIGHT precisely to avoid
    that cost, and the close-out door tells the agent a skipped E2E "is the design, not a red" —
    so a genuinely red E2E reads as the expected skip. Derived from the repo, never asserted, so
    the caveat disappears by itself the moment the workflow lands."""
    wf_dir = repo / ".github" / "workflows"
    if not wf_dir.is_dir():
        return False
    for p in sorted(wf_dir.iterdir()):
        if p.suffix in (".yml", ".yaml") and p.is_file():
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            # ⛔ A COMMENT IS NOT AN IMPLEMENTATION (SCC-441 review, reproduced). A raw-bytes
            # search called a repo armed on `# TODO: skip E2E on -light-epic-` while it still
            # ran all four checks — and a TODO is the likeliest way the token first appears,
            # because the intent gets written before the code. AVCH-152 is that TODO today.
            if any(LIGHT_TOKEN in uncommented(ln) for ln in text.splitlines()):
                return True
    return False


def classify(names: list[str], repo: Path) -> tuple[str, str]:
    """(word line, cost line) for a live-epic list, as read in `repo`.

    `repo` is REQUIRED. It was optional-with-a-None-default for one revision, and the
    `repo is not None` guard that default forced was unreachable: `main()` is the only caller
    and always passes one (SCC-441 review). An optional parameter nobody omits is flexibility
    nobody asked for, and the dead branch it creates reads as a case someone meant to handle."""
    if not names:
        return "TRUNK", COST["TRUNK"]
    if len(names) > 1:
        return "AMBIGUOUS", "more than one live epic on origin - prune or name one: " + ", ".join(names)
    branch = names[0]
    mode = "LIGHT" if LIGHT_TOKEN in branch else "FULL"
    cost = COST[mode].format(branch=branch)
    if mode == "LIGHT" and not light_armed(repo):
        cost += ("  ⛔ NOT ARMED HERE: no workflow under .github/workflows/ reads `-light-epic-`, "
                 "so every landing still pays the FULL checks and a red E2E is a red, not the "
                 "designed skip")
    return f"{mode} {branch}", cost


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Which epic mode is this project on? (SCC-446)")
    ap.add_argument("--repo", required=True, help="repo root, absolute - never the cwd")
    args = ap.parse_args(argv)
    # ⛔ AN EMPTY --repo IS THE CWD, AND THE CWD IS THE LOBBY (SCC-446 review, reproduced).
    # `cd ""` exits 0 without moving in both shells, so an unbound `$PROJECT_ROOT` reaches here
    # as `""`; `Path("").resolve()` is the working directory, which is a real git repo, so every
    # check below passes and the script answers confidently about the WRONG repo. From the lobby
    # that answer is `TRUNK`, which routes a story on a live FULL epic to the close-out's trunk
    # arm — a pull request into `main`. Refuse it before anything resolves.
    if not args.repo.strip():
        print("ERROR")
        print("--repo was empty - an unbound $PROJECT_ROOT reaches here as \"\", and an empty "
              "path resolves to the CWD. Bind it (Step 0 §BIND) and re-run.")
        return EXIT["ERROR"]
    repo = Path(args.repo).resolve()
    if not (repo / ".git").exists():
        print("ERROR")
        print(f"{repo} is not a git repository (no .git)")
        return EXIT["ERROR"]
    names, why = live_epics(repo)
    if names is None:
        print("ERROR")
        print(why)
        return EXIT["ERROR"]
    word, cost = classify(names, repo)
    print(word)
    print(cost)
    return EXIT[word.split(" ", 1)[0]]


if __name__ == "__main__":
    raise SystemExit(main())
