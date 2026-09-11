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
`pr-check.yml` reads with `contains()`. The word `light` anywhere else in the slug is not it.
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
                if LIGHT_TOKEN in p.read_text(encoding="utf-8", errors="replace"):
                    return True
            except OSError:
                continue
    return False


def classify(names: list[str], repo: Path | None = None) -> tuple[str, str]:
    """(word line, cost line) for a live-epic list."""
    if not names:
        return "TRUNK", COST["TRUNK"]
    if len(names) > 1:
        return "AMBIGUOUS", "more than one live epic on origin - prune or name one: " + ", ".join(names)
    branch = names[0]
    mode = "LIGHT" if LIGHT_TOKEN in branch else "FULL"
    cost = COST[mode].format(branch=branch)
    if mode == "LIGHT" and repo is not None and not light_armed(repo):
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
