"""epic_mode.py — which epic mode is this project on? ONE query, the word first. (SCC-446)

    epic_mode.py --repo <abs path>

    TRUNK                                    no origin/epic/* at all                      (exit 0)
    FULL  epic/<KEY>-epic-<N>-<slug>         the third token is `-epic-`                  (exit 0)
    LIGHT epic/<KEY>-light-epic-<N>-<slug>   the third token is `-light-epic-`            (exit 0)
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


def classify(names: list[str]) -> tuple[str, str]:
    """(word line, cost line) for a live-epic list."""
    if not names:
        return "TRUNK", COST["TRUNK"]
    if len(names) > 1:
        return "AMBIGUOUS", "more than one live epic on origin - prune or name one: " + ", ".join(names)
    branch = names[0]
    mode = "LIGHT" if LIGHT_TOKEN in branch else "FULL"
    return f"{mode} {branch}", COST[mode].format(branch=branch)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Which epic mode is this project on? (SCC-446)")
    ap.add_argument("--repo", required=True, help="repo root, absolute - never the cwd")
    args = ap.parse_args(argv)
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
    word, cost = classify(names)
    print(word)
    print(cost)
    return EXIT[word.split(" ", 1)[0]]


if __name__ == "__main__":
    raise SystemExit(main())
