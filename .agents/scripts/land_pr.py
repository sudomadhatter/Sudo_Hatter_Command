"""SCC-183 — the PR door: open (and sometimes merge) the pull request that lands a lane.

    python3 .agents/scripts/land_pr.py [--repo PATH] [--merge] [--dry-run]

WHY THIS EXISTS. SCC-184 was 226 lines of docs with every gate green and it could not reach
`main` in a full session. The block was never a gate — it was the LANDING: ~15 hand-typed
git/gh incantations in the shared checkout, each string judged separately by the agent's
permission layer, several denied, state stranded halfway. This replaces that ceremony with one
command whose whole job is to hand back a URL.

⛔ WHAT THIS IS NOT. It is not a way around the operator's control of the agent. The permission
layer is theirs; this script is one stable command string so it can be granted (or refused)
ONCE, on purpose, instead of fifteen times by accident.

THE SPLIT (operator's ruling, 2026-08-16). Prose lanes may merge themselves; everything else
opens the PR and hands the operator the link — their click is the sign-off. `merge_eligible()`
is that ruling made mechanical, and it is deliberately NARROWER than the words: `.agents/` rule
edits and toolkit `INDEX.md` files still need a click, and that narrowing is declared in the
plan rather than smuggled in here.

⛔ THE ONE DEFECT THIS FILE KEEPS RE-LEARNING. Three cuts of the plan shipped a "which files are
safe to land unread" rule, and all three were wrong the same way — written from what the author
had in mind instead of from what `git ls-files` returns. R1 said `docs/**` was a prose tree
(reviewed FAIL). Cut 1 leaned on `lane_qualify` alone, which rates the agent's own permission
hook LIGHT. Cut 2's allowlist admitted the nine per-folder `AGENTS.md`/`CLAUDE.md`/`GEMINI.md`
front doors. Cut 3 still had root `router.md` — the MASTER ROUTER — sitting in an allow arm.
Hence `is_prose` below is REFUSALS FIRST, and its test enumerates the real repo and asserts on
the SHAPE of what survives. A hand-written row list cannot catch the file nobody remembered.

Stdlib only, no pytest, no install step — matching every other script in this directory.
"""
from __future__ import annotations

import argparse
import json
import posixpath
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import lane_qualify  # noqa: E402 — same directory; see module docstring
import main_write_gate  # noqa: E402

CHECK_NAME = "main-write-gate"
"""The required check on the live ruleset. Not re-typed anywhere else in this file."""

FRONT_DOORS = frozenset({"AGENTS.md", "CLAUDE.md", "GEMINI.md"})
"""Per-folder entry points. NINE are tracked, and only three are at the root — which is exactly
how cut 2's root-path refusal let `_artifacts/CLAUDE.md` through. Matched by BASENAME, at any
depth, forever."""

PROSE_ROOTS = ("docs/", "_artifacts/", "_my_resources/")

REGULAR_MODES = frozenset({"100644"})
"""A plain, non-executable blob. A symlink (120000) or a submodule bump (160000) is not prose
however its path reads, and `lane_qualify` rates a bare gitlink bump LIGHT — the prefix check is
the only other thing holding that door."""

WRITE_VERBS = frozenset({"create", "merge", "edit", "close", "reopen", "comment", "ready"})

_SHAPE = re.compile(r"^(epic|chore)/([A-Z][A-Z0-9]+)-\d+-.+")


# --------------------------------------------------------------------------- the predicate

norm = lane_qualify.norm
"""⛔ IMPORTED, never re-implemented. The first cut of this file wrote `lstrip("./")`, which
takes a character SET and therefore eats the leading dot off every `.agents/…` and `.claude/…`
path — so `lane_qualify` stopped seeing them as toolkit paths and rated them LIGHT, silently
disabling one of `merge_eligible`'s two halves. `sop_currency._norm` shipped that same bug once
and `lane_qualify.norm`'s docstring exists to stop it recurring. It has now been written wrong
three times in this repo; the cure is one normalizer, not three that agree today."""


def is_prose(path: str) -> bool:
    """May this file land on `main` with no human reading the diff?

    ⛔ REFUSALS ARE EVALUATED FIRST AND THEY WIN. `docs/CLAUDE.md` matches both an allow arm and
    a refusal; precedence is the only thing that decides it, so it is stated, tested (AC-4b) and
    load-bearing — not an ordering accident.
    """
    p = norm(path)
    if not p:
        return False

    # --- refused ---------------------------------------------------------
    if posixpath.basename(p) in FRONT_DOORS:
        return False                       # routing law at ANY depth (nine tracked today)
    if p.startswith("docs/migrations/"):
        return False                       # the guides that tell a human what to run on a new
        #                                    machine. Refusing only `.../scripts/` missed by one
        #                                    directory level and admitted all six.
    if "/" not in p:
        return False                       # no repo-root file is prose. `router.md` IS the
        #                                    master router; it was an allow arm for three cuts.
    if not p.endswith(".md"):
        return False                       # `docs/.maps-state.json` is `check_maps`' own
        #                                    baseline and one of THIS lane's gates.

    # --- allowed ---------------------------------------------------------
    # Deliberately ONE arm. `docs/repo-map.md`, `_artifacts/**/INDEX.md` and
    # `_artifacts/_memory/**.md` are all subsumed by it; the plan's separate exact-path bullets
    # were unreachable decoration, which is how a refusal list scores 100% while doing no work.
    return p.startswith(PROSE_ROOTS)


def merge_eligible(repo: Path, entries) -> tuple[bool, str]:
    """BOTH halves must hold, and EITHER ALONE must refuse the agent's own permission hook.

    `lane_qualify` answers "which dev lane does this work belong in". This asks "may this land
    with no human looking at it". Different questions — measured: `lane_qualify` rates
    `.claude/hooks/require-push-approval.py` LIGHT.
    """
    entries = [(m, norm(p)) for m, p in entries if norm(p)]
    paths = [p for _, p in entries]

    verdict, why = lane_qualify.classify(Path(repo), paths, no_file_changes=False)
    if verdict != "LIGHT":
        return False, f"lane_qualify says {verdict} — {why}"

    bad_mode = [f"{p} (mode {m})" for m, p in entries if m not in REGULAR_MODES]
    if bad_mode:
        return False, "not a regular file: " + ", ".join(bad_mode[:3])

    bad = [p for p in paths if not is_prose(p)]
    if bad:
        return False, "not prose: " + ", ".join(bad[:3])

    return True, f"prose only ({len(paths)} file(s))"


def branch_ok(name: str, keys: list[str]) -> tuple[bool, str]:
    """R2 + R3. ⛔ The pattern is IMPORTED, never re-typed — `branch_pattern` builds it from
    `AUTHORISED_PREFIXES` and this repo's `jira.conf`, and a copy here would drift from the very
    gate this check exists to anticipate."""
    name = (name or "").strip()
    if main_write_gate.branch_pattern(keys).match(name):
        return True, f"'{name}'"
    m = _SHAPE.match(name)
    if m and keys and m.group(2) not in keys:
        return False, (f"R3: branch key '{m.group(2)}' is not one this repo answers to "
                       f"(jira.conf JIRA_KEYS = {' '.join(keys)}). A wrong-project key never "
                       f"lands here.")
    return False, (f"R2: branch '{name}' is not an authorised source for main. Expected "
                   f"(epic|chore)/<KEY>-<number>-<slug>. A story lane (claude/*) lands on its "
                   f"epic branch, never on main.")


# --------------------------------------------------------------------------- the seams

def git(repo: Path, *args: str) -> tuple[int, str]:
    """⛔ `-C` on every call, always. `.agents/rules/nothing-guards-the-merge-target.md`: every
    gate in this system checks what you merge FROM and nothing guards the target, so the target
    is pinned here rather than inherited from a cwd that a stray `cd` can move."""
    r = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True, errors="replace")
    return r.returncode, (r.stdout or "").strip()


def is_write(argv) -> bool:
    a = list(argv)
    return len(a) >= 2 and a[0] == "pr" and a[1] in WRITE_VERBS


class GhCli:
    """The default `gh` seam. Every test substitutes a recorder, so no test calls GitHub."""

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run

    def __call__(self, *args: str) -> tuple[int, str]:
        if self.dry_run and is_write(args):
            return 0, "[dry-run] not executed"
        r = subprocess.run(["gh", *args], capture_output=True, text=True, errors="replace")
        return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


# --------------------------------------------------------------------------- the run

def _pr_for_branch(gh, branch: str):
    rc, out = gh("pr", "list", "--head", branch, "--state", "all",
                 "--json", "number,state,url,headRefOid,mergeCommit")
    if rc != 0 or not out.strip():
        return None
    try:
        rows = json.loads(out)
    except (ValueError, TypeError):
        return None
    if not rows:
        return None
    for r in rows:                              # an OPEN one always wins over history
        if (r.get("state") or "").upper() == "OPEN":
            return r
    return rows[0]


def _changed(repo: Path, base: str) -> list[tuple[str, str]]:
    """(dst-mode, path) for the landing set.

    ⛔ THREE dots, not two: `origin/main...HEAD` is what the branch ADDED, measured from the
    merge base. Two dots would classify every file a sibling landed while this lane was open,
    turning someone else's code into this lane's eligibility question.
    ⛔ `--raw`, not `--name-only`: `--name-only` carries no MODE, and the mode is the only thing
    that tells a symlink or a submodule bump from a file.
    """
    rc, out = git(repo, "diff", "--raw", "--no-renames", f"{base}...HEAD")
    if rc != 0:
        return []
    entries: list[tuple[str, str]] = []
    for line in out.splitlines():
        if not line.startswith(":") or "\t" not in line:
            continue
        meta, path = line.split("\t", 1)
        f = meta.split()
        if len(f) < 5:
            continue
        src_mode, dst_mode = f[0].lstrip(":"), f[1]
        # A deletion has dst_mode 000000; what was deleted is what matters.
        entries.append((dst_mode if dst_mode != "000000" else src_mode, path.strip()))
    return entries


def run(repo, *, merge: bool = False, dry_run: bool = False, gh=None,
        poll_seconds: int = 300) -> tuple[int, list[str]]:
    """Returns (exit code, lines). The LAST line is always the actionable identifier —
    the PR URL when handing back, `landed: …` when it merged (AC-6)."""
    repo = Path(repo)
    gh = gh if gh is not None else GhCli(dry_run=dry_run)
    lines: list[str] = []

    def say(s: str) -> None:
        lines.append(s)

    def no(s: str) -> tuple[int, list[str]]:
        say(f"REFUSED — {s}")
        return 1, lines

    def act(*argv: str) -> tuple[int, str]:
        if dry_run:
            say("[dry-run] gh " + " ".join(argv))
        return gh(*argv)

    # R1 ------------------------------------------------------------------
    rc, _ = git(repo, "rev-parse", "--git-dir")
    if rc != 0:
        return no(f"R1: {repo} is not a git repo (or git cannot resolve it). "
                  f"Nothing here acts on belief.")

    rc, branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    if rc != 0 or not branch or branch == "HEAD":
        return no("R1: cannot resolve a branch name (detached HEAD?).")

    # R2 + R3 -------------------------------------------------------------
    keys = main_write_gate.read_jira_keys(repo)
    ok, why = branch_ok(branch, keys)
    if not ok:
        return no(why)

    # R4 ------------------------------------------------------------------
    rc, dirty = git(repo, "status", "--porcelain")
    if dirty.strip():
        n = len(dirty.splitlines())
        return no(f"R4: the working tree is dirty ({n} path(s)). A PR describes COMMITTED work; "
                  f"a dirty tree is the SCC-184 failure condition itself.")

    git(repo, "fetch", "-q", "origin")     # a read; never act on a stale origin/main

    # R7 — before P, because P is the first thing that needs `gh` ---------
    rc_gh, out_gh = gh("auth", "status")
    gh_ok = rc_gh == 0
    if not gh_ok:
        if not dry_run:
            return no("R7: `gh` is missing or not authenticated. Install it "
                      "(`brew install gh`) and run `gh auth login`. "
                      f"({out_gh.splitlines()[0] if out_gh else 'no output'})")
        say("⚠ gh unavailable — --dry-run degrades to an argv-only preview (offline is exactly "
            "when a preview is most useful).")

    # P — branches on STATE. A bare "a PR exists" probe reported success on a CLOSED PR.
    pr = _pr_for_branch(gh, branch) if gh_ok else None
    state = (pr.get("state") or "").upper() if pr else ""

    if pr and state == "CLOSED":
        return no(f"P: PR #{pr['number']} for this branch was CLOSED without merging "
                  f"({pr.get('url', '')}). Reopen it or re-cut the branch — this will not "
                  f"quietly open a second one, and it will not report success.")

    if pr and state == "MERGED":
        sha = ((pr.get("mergeCommit") or {}) or {}).get("oid") or ""
        rc, _ = git(repo, "merge-base", "--is-ancestor", "HEAD", sha) if sha else (1, "")
        if rc == 0:
            say(f"landed: PR #{pr['number']} · merge commit {sha[:12]}")
            return 0, lines
        say(f"note: PR #{pr['number']} merged at {sha[:12]}, but this branch has moved since — "
            f"opening a new one.")
        pr = None
        state = ""

    if pr and state == "OPEN" and not merge:
        say(f"PR #{pr['number']} is already open for {branch}.")
        say(pr.get("url", ""))
        return 0, lines

    # R5 ------------------------------------------------------------------
    rc, ahead = git(repo, "rev-list", "--count", "origin/main..HEAD")
    n_ahead = int(ahead) if ahead.isdigit() else 0
    if n_ahead == 0 and not pr:
        return no("R5: nothing to land — this branch is 0 commits ahead of origin/main and has "
                  "no PR. An empty input is never a pass.")

    # R6 ------------------------------------------------------------------
    rc, upstream = git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    if rc == 0 and upstream:
        rc, counts = git(repo, "rev-list", "--left-right", "--count", f"{upstream}...HEAD")
        parts = counts.split()
        behind = int(parts[0]) if len(parts) == 2 and parts[0].isdigit() else 0
        if behind:
            return no(f"R6: this branch has DIVERGED from {upstream} (behind {behind}). "
                      f"Force-push is banned here — reconcile it by hand.")
    # No upstream at all is ABSENCE, not divergence (it is what `--delete-branch` leaves).

    # Freshness — at CREATE time, so the CLICK path is covered too --------
    if n_ahead:
        rc, _ = git(repo, "merge-base", "--is-ancestor", "origin/main", "HEAD")
        if rc != 0:
            rc, om = git(repo, "rev-parse", "--short", "origin/main")
            return no(f"stale: origin/main ({om}) is not an ancestor of this branch — it moved "
                      f"while this lane was open. The required check certifies the PR head "
                      f"ONLY (strict_required_status_checks_policy is false), so a PR opened "
                      f"now could merge on a green that never saw the sibling's code. Absorb "
                      f"origin/main and re-gate.")

    # Push, then open -----------------------------------------------------
    if not pr:
        if not dry_run:
            rc, out = git(repo, "push", "-u", "origin", "HEAD")
            if rc != 0:
                return no(f"could not push {branch}: {out.splitlines()[-1] if out else ''}")
        else:
            say(f"[dry-run] git -C {repo} push -u origin HEAD")

        rc, out = act("pr", "create", "--base", "main", "--head", branch,
                      "--title", _title(repo, branch), "--body", _body(repo, branch))
        url = (out or "").strip().splitlines()[-1] if out.strip() else ""
        if rc != 0 and not dry_run:
            return no(f"gh pr create failed: {out[-300:]}")
        pr = _pr_for_branch(gh, branch) if gh_ok else None
        if pr:
            url = pr.get("url", url)
    else:
        url = pr.get("url", "")

    number = pr.get("number") if pr else None

    # R8 — eligibility ----------------------------------------------------
    if merge:
        entries = _changed(repo, "origin/main")
        eligible, why = merge_eligible(repo, entries)
        if not eligible:
            say(f"NOT auto-mergeable — {why}")
            say("This one is yours to merge; the gate result is on the PR.")
            say(url)
            return 0, lines

        say(f"auto-mergeable — {why}")

        if not dry_run:
            ok_check, detail = _await_check(gh, number, poll_seconds)
            if not ok_check:
                say(f"the {CHECK_NAME} check did not pass: {detail}")
                say(url)
                return 1, lines

            # ⛔ Re-check freshness: origin/main can move WHILE the check runs.
            git(repo, "fetch", "-q", "origin")
            rc, _ = git(repo, "merge-base", "--is-ancestor", "origin/main", "HEAD")
            if rc != 0:
                say("origin/main moved while the check ran — refusing to merge stale.")
                say(url)
                return 1, lines

        # ⛔ --merge ONLY. --squash and --rebase each put a single-parent commit on main and
        # break the one-merge-per-landing shape every gate in this system assumes.
        rc, out = act("pr", "merge", str(number or ""), "--merge", "--delete-branch")
        if rc != 0 and not dry_run:
            say(f"gh pr merge failed: {out[-300:]}")
            say(url)
            return 1, lines

        sha = ""
        if not dry_run:
            git(repo, "fetch", "-q", "origin")
            _, sha = git(repo, "rev-parse", "--short", "origin/main")
        say(f"landed: PR {_label(number)} · merge commit {sha or '(dry-run)'}")
        return 0, lines

    say(f"PR {_label(number)} is open and the {CHECK_NAME} check is running.")
    say("Merge it when it goes green:")
    say(url)
    return 0, lines


def _await_check(gh, number, seconds: int) -> tuple[bool, str]:
    deadline = time.monotonic() + max(1, seconds)
    last = "no check reported"
    while time.monotonic() < deadline:
        rc, out = gh("pr", "checks", str(number or ""), "--json", "name,state")
        if rc == 0 and out.strip():
            try:
                rows = json.loads(out)
            except (ValueError, TypeError):
                rows = []
            for r in rows:
                if r.get("name") == CHECK_NAME:
                    st = (r.get("state") or "").upper()
                    last = f"{CHECK_NAME} is {st}"
                    if st == "SUCCESS":
                        return True, last
                    if st in ("FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED"):
                        return False, last
        time.sleep(5)
    return False, f"timed out after {seconds}s ({last})"


def _label(number) -> str:
    """A dry run has no PR number because no PR was created — say that, rather than `#None`."""
    return f"#{number}" if number else "#(not created — dry run)"


def _title(repo: Path, branch: str) -> str:
    _, subject = git(repo, "log", "-1", "--format=%s")
    return subject or branch


def _body(repo: Path, branch: str) -> str:
    _, stat = git(repo, "diff", "--stat", "origin/main...HEAD")
    _, log = git(repo, "log", "--oneline", "--no-merges", "origin/main..HEAD")
    return (f"Lands `{branch}`.\n\n## Commits\n\n```\n{log}\n```\n\n"
            f"## Files\n\n```\n{stat}\n```\n\n"
            f"The `{CHECK_NAME}` check on this PR is the gate.\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Open (and optionally merge) the PR that lands a lane.")
    ap.add_argument("--repo", default=".", help="repo root (default: cwd)")
    ap.add_argument("--merge", action="store_true",
                    help="merge it too, IF the lane is prose-only (otherwise hands back the link)")
    ap.add_argument("--dry-run", action="store_true",
                    help="network reads only; prints the argv it would have run")
    a = ap.parse_args(argv)
    rc, lines = run(Path(a.repo).resolve(), merge=a.merge, dry_run=a.dry_run)
    for ln in lines:
        print(ln)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
