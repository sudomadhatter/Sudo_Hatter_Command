"""closeout_preflight.py — run the close-out checklist instead of narrating it (Wave 1.4).

`/cicd-update-sprint-memory` asks an agent to hold ~8 mechanical facts in its head at once:
did the code land, is every repo pushed, are the worktrees real, do both status surfaces
agree, is the context inside budget, did the gates actually run, can the epic close, and is
the story's verdict recorded. Each is a git or filesystem question with an exact answer, and
each has failed silently at least once (see the memory index). This answers all of them.

    closeout_preflight.py --story 21.8b [--project P] [--worktree PATH] [--branch B]
                          [--require-gates ruff,pytest] [--sha X] [--fetch] [--json]

Exit: 0 clean · 1 warnings · 2 blocking. It never flips a status - it reports whether the
flip is safe; `story_status.py set` does the write.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate_receipt as gr
import wf_common as wf

def integration_branch(project: Path) -> str:
    """The landing target for a story: its epic branch (`epic/*`), falling back to `main`.

    main_debug retired 2026-08-07 — epics integrate on short-lived epic/* branches that merge
    to main via /cicd-push-e2e. With exactly one live epic branch the target is unambiguous;
    with zero or several, `main` is the only branch every landing eventually reaches, so the
    ancestor check stays meaningful (a story merged via its epic IS an ancestor of main once
    the epic ships — before that, several-epics ambiguity must be resolved with --branch)."""
    r = wf.git(["branch", "--list", "--format=%(refname:short)", "epic/*"], project)
    branches = [b.strip() for b in r.stdout.splitlines() if b.strip()]
    return branches[0] if len(branches) == 1 else "main"


# ── 1. Did the code actually land? ─────────────────────────────────────────────

def find_branches(project: Path, key: str, explicit: str | None) -> list[str]:
    """Candidate branches for a story, in order of how much they prove.

    Branches here are named descriptively (`claude/xdist-tail-hang`, `Epic-7`) far more
    often than by story id, so a slug-only match finds nothing for almost every story.
    Worktrees are the reliable link: a story tree is checked out on the story's branch."""
    if explicit:
        return [explicit]
    sid = wf.story_id(key)
    found: list[str] = []
    for pat in (f"*{key}*", f"*{sid}*", f"*{sid.replace('-', '.')}*"):
        r = wf.git(["branch", "--list", "--all", "--format=%(refname:short)", pat], project)
        found += [b.strip() for b in r.stdout.splitlines() if b.strip()]
    # A worktree whose directory carries the id is checked out on this story's branch.
    out = wf.git(["worktree", "list", "--porcelain"], project).stdout
    for block in out.split("\n\n"):
        wt = re.search(r"^worktree (.+)$", block, re.MULTILINE)
        br = re.search(r"^branch refs/heads/(.+)$", block, re.MULTILINE)
        if wt and br and (wf.slug_matches(sid, Path(wt.group(1)).name)
                          or wf.story_id(Path(wt.group(1)).name) == sid):
            found.append(br.group(1).strip())
    seen: dict[str, None] = {}
    for b in found:
        seen.setdefault(b, None)
    return list(seen)


def check_landed(project: Path, key: str, rep: wf.Report, branch: str | None = None) -> None:
    """Landing and close-out are separate events (memory: landing-is-not-closeout) -
    code merges while the board still reads `review`, and the board never notices."""
    branches = find_branches(project, key, branch)
    if not branches:
        # NOT an info. "I could not check" and "I checked and it is clean" must never
        # print the same way - a check that cannot fire is indistinguishable from a pass.
        rep.warn("landed", f"no branch or worktree carries '{wf.story_id(key)}' - branches here "
                           f"are often named descriptively, so landing was NOT verified; "
                           f"confirm by hand or pass --branch <name>")
        return
    target = integration_branch(project)
    for b in branches:
        merged = wf.git(["merge-base", "--is-ancestor", b, target], project)
        if merged.returncode == 0:
            rep.info("landed", f"{b} is an ancestor of {target} (landed)")
        else:
            ahead = wf.git(["rev-list", "--count", f"{target}..{b}"], project)
            n = ahead.stdout.strip() or "?"
            rep.err("landed", f"{b} has {n} commit(s) NOT on {target} - "
                              f"closing out now would strand them")
            # This is the moment the operator goes and does the landing merge, so it is the
            # moment worth knowing whether a SIBLING lane already changed the same files.
            # `worktree-per-story.md`: "The epic branch moves under you... never assume the
            # base you opened on." Naming the overlap is the difference between a
            # fast-forward and a three-way merge that needs both sides' facts kept.
            wf.report_overlap(project, b, target, rep, section="landed")


# ── 2. Is every repo pushed and clean? ─────────────────────────────────────────

def check_sync(label: str, repo: Path, fetch: bool, rep: wf.Report) -> None:
    """`commit-and-push-are-one-action`: 0/0 + clean, per repo, or the step isn't done."""
    if not (repo / ".git").exists():
        rep.info("sync", f"{label}: not a git repo, skipped")
        return
    if fetch:
        f = wf.git(["fetch", "--quiet"], repo, timeout=180)
        if f.returncode != 0:
            rep.warn("sync", f"{label}: fetch failed - ahead/behind may be stale")
    else:
        rep.info("sync", f"{label}: no --fetch, ahead/behind is vs the LAST fetch")

    branch = wf.git(["rev-parse", "--abbrev-ref", "HEAD"], repo).stdout.strip()
    counts = wf.git(["rev-list", "--left-right", "--count", f"origin/{branch}...{branch}"], repo)
    if counts.returncode == 0 and counts.stdout.strip():
        behind, ahead = (counts.stdout.split() + ["?", "?"])[:2]
        if ahead != "0" or behind != "0":
            rep.err("sync", f"{label} [{branch}]: {ahead} ahead / {behind} behind origin")
        else:
            rep.info("sync", f"{label} [{branch}]: 0/0 with origin")
    else:
        rep.warn("sync", f"{label} [{branch}]: no upstream to compare against")

    dirty = wf.git(["status", "--porcelain"], repo).stdout.strip()
    if dirty:
        n = len(dirty.splitlines())
        rep.err("sync", f"{label}: {n} uncommitted change(s) - commit before closing out")


# ── 3. Are the registered worktrees real? ──────────────────────────────────────

def check_worktrees(project: Path, rep: wf.Report) -> None:
    """A pruned worktree leaves a directory that blocks the next `worktree add`
    (memory: pruned-worktree-leaves-a-blocking-shell). Three states, not two."""
    out = wf.git(["worktree", "list", "--porcelain"], project).stdout
    paths = [Path(m) for m in re.findall(r"^worktree (.+)$", out, re.MULTILINE)]
    for p in paths[1:]:  # [0] is the main checkout
        if not p.exists():
            rep.warn("worktrees", f"LOST (registered, no directory): {p.name} - `git worktree prune`")
        elif not (p / ".git").exists():
            rep.err("worktrees", f"HUSK (directory, no .git): {p.name} - "
                                 f"blocks re-adding; remove it with PowerShell")
        else:
            rep.info("worktrees", f"LIVE: {p.name}")


# ── 4-8. Board, artifacts, budget, gates, epic ─────────────────────────────────

def check_surfaces(project: Path, key: str, rep: wf.Report) -> None:
    for d in wf.status_drift(project):
        sev = rep.err if d["key"] == key else rep.warn
        sev("surfaces", f"{d['key']}: board={d['board']} vs frontmatter={d['frontmatter']}"
                        f" - story_status.py set --reconcile")


# Lenient READER, strict writer. The canonical form is `Verdict: PASS @ <sha>`, but humans
# write `**Verdict: PASS**` and `## Verdict: CONCERNS` - anchoring on a bare `^Verdict:`
# reads a recorded verdict as "the review never ran", which is the worst possible miss.
_VERDICT_RE = re.compile(
    r"^[>\-*#\s]*\**\s*Verdict:\**\s*\**(PASS|CONCERNS|FAIL|WAIVED)\**"
    r"(?:[^\n]*?@\s*`?([0-9a-f]{7,40}))?",
    re.MULTILINE | re.IGNORECASE)


_LEGACY_REL = "_bmad-output/implementation-artifacts"


def legacy_verdict(project: Path, key: str) -> Path | None:
    """Stories closed before the two-doc change (2026-08-02) recorded their verdict in a
    standalone `sudo-code-review-<story>.md`. Plan A's back-compat contract is explicit:
    section first, legacy file second. Without this fallback every historic story reports
    'the review never ran' - a false red on correctly-closed work, which is exactly how a
    checker gets muted.

    BOTH prefixes are matched (SCC-63). The `sudo-` form is not legacy-by-accident here:
    those files already exist under project `_bmad-output/`, the rename never touched them,
    and dropping the pattern would re-break every historic story the fallback exists for."""
    d = project / _LEGACY_REL
    if not d.is_dir():
        return None
    for prefix in ("sudo-code-review-", "cicd-code-review-"):
        for p in sorted(d.glob(prefix + "*.md")):
            if wf.slug_matches(wf.story_id(key), p.stem[len(prefix):]):
                return p
    return None


def check_artifacts(project: Path, key: str, rep: wf.Report) -> None:
    """The two-doc close puts the flip gate in the walkthrough's `Verdict:` line
    (memory: story-artifacts-two-doc-close). Absent section = the step never ran."""
    slug = wf.norm_id(key)
    # slug_matches, not startswith: `21-8` must not adopt `21-8b`'s walkthrough.
    hits = [p for p in project.glob("_artifacts/**/walkthrough.md")
            if wf.slug_matches(slug, wf.norm_id(p.parent.name).removeprefix("story-"))]
    if not hits:
        legacy = legacy_verdict(project, key)
        if legacy:
            rep.info("artifacts", f"no walkthrough.md; verdict is in the pre-08-02 standalone "
                                  f"file {legacy.relative_to(project)}")
            return
        rep.err("artifacts", f"no walkthrough.md found for '{slug}' - "
                             f"code review never recorded a verdict")
        return
    for path in hits:
        text = wf.read_text(path)
        m = _VERDICT_RE.search(text)
        rel = path.relative_to(project)
        if not m:
            legacy = legacy_verdict(project, key)
            if legacy:
                rep.info("artifacts", f"{rel}: no `Verdict:` line, but the pre-08-02 standalone "
                                      f"{legacy.name} holds it (legacy fallback)")
                continue
            rep.err("artifacts", f"{rel}: no `Verdict:` line - "
                                 f"the review step has not run (or did not record it)")
            continue
        verdict, sha = m.group(1).upper(), m.group(2)
        if verdict == "FAIL":
            rep.err("artifacts", f"{rel}: Verdict FAIL - blocks the done-flip")
            continue
        rep.info("artifacts", f"{rel}: Verdict {verdict}"
                              f"{' @ ' + sha[:8] if sha else ''}")
        if not sha:
            # Without a SHA the verdict floats free of any tree, so "has the code changed
            # since review?" is unanswerable - the exact question the flip depends on.
            rep.warn("artifacts", f"{rel}: verdict carries no `@ <sha>` - staleness "
                                  f"CANNOT be checked; re-record as `Verdict: {verdict} @ <sha>`")
        if sha:
            # A verdict is only evidence about the tree it was taken on.
            diff = wf.git(["diff", "--name-only", f"{sha}..HEAD", "--",
                           "backend/", "frontend/"], project)
            changed = [ln for ln in diff.stdout.splitlines() if ln.strip()]
            if diff.returncode != 0:
                rep.warn("artifacts", f"{rel}: reviewed SHA {sha[:8]} not in this repo")
            elif changed:
                rep.err("artifacts", f"{rel}: {len(changed)} code file(s) changed since the "
                                     f"reviewed SHA - the verdict is STALE, re-gate")


_FILELIST_RE = re.compile(r"^\s*(?:#{1,6}\s*|\**)File List\**\s*:?\s*$",
                          re.MULTILINE | re.IGNORECASE)
_PATH_RE = re.compile(r"[A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)+\.[A-Za-z0-9]+")


def check_file_list(project: Path, key: str, rep: wf.Report) -> None:
    """Verify the story's claimed File List against the tree (plan §1.4 code-verify).

    The File List is the dev's own claim about what changed; nothing has ever checked it.
    A path that does not exist means the claim is wrong, the file was renamed, or the work
    is on a branch that never landed - all three are close-out blockers."""
    files = wf.find_story_files(project, key)
    if len(files) != 1:
        return  # missing/ambiguous story files are check_surfaces' report
    text = wf.read_text(files[0])
    m = _FILELIST_RE.search(text)
    if not m:
        rep.warn("file-list", f"{files[0].name}: no `File List` section - "
                              f"nothing to verify the change set against")
        return
    body: list[str] = []
    for line in text[m.end():].splitlines():
        if line.lstrip().startswith("#") or re.match(r"^\s*\*\*[A-Z]", line):
            break
        body.append(line)
    claimed: list[str] = []
    for cand in _PATH_RE.findall("\n".join(body)):
        if cand not in claimed:
            claimed.append(cand)
    if not claimed:
        rep.warn("file-list", f"{files[0].name}: File List section has no file paths")
        return

    tracked = {ln.strip() for ln in
               wf.git(["ls-files"], project).stdout.splitlines() if ln.strip()}
    missing, untracked, ok = [], [], 0
    for c in claimed:
        if c in tracked:
            ok += 1
        elif (project / c).exists():
            untracked.append(c)
        else:
            missing.append(c)
    rep.info("file-list", f"{ok}/{len(claimed)} claimed file(s) tracked at HEAD")
    for c in untracked:
        rep.warn("file-list", f"claimed but UNTRACKED: {c} - never committed")
    for c in missing:
        rep.err("file-list", f"claimed but ABSENT: {c} - renamed, or the work never landed")


def check_budget(project: Path, rep: wf.Report) -> None:
    path = project / wf.ACTIVE_CONTEXT_REL
    if not path.is_file():
        rep.warn("budget", f"{wf.ACTIVE_CONTEXT_REL} missing")
        return
    size = path.stat().st_size
    (rep.err if size > 20 * 1024 else rep.info)(
        "budget", f"active-context {size} bytes (~{round(size / 4)} tokens, budget 20480)")


def check_gates(project: Path, story: str, require: list[str], rep: wf.Report,
                sha: str | None = None) -> None:
    """Delegates to gate_receipt so the two tools can never disagree about 'stale' -
    they had two different definitions, and the stricter one was wrong."""
    if not require:
        return
    target = sha or wf.git_head(project)
    for gate in require:
        if not (gr.receipt_dir(project, story) / f"{gate}.json").is_file():
            # WARN, not ERROR: ruling 2026-08-02 keeps the receipt gate advisory for one
            # sprint. gate_receipt's own `check` is where the hard block lives.
            rep.warn("gates", f"{gate}: no receipt (gate_receipt.py run ...)")
            continue
        data = gr.load_receipt(project, story, gate, rep)
        if data is not None:
            gr.check_receipt(project, data, gate, target, rep)


def check_epic(project: Path, key: str, rep: wf.Report) -> None:
    """An umbrella cannot close itself (memory: agy-epic-keys-rot-silently). When every
    child is terminal the epic key is the only thing left holding the epic open."""
    m = re.match(r"^(\d+)-", wf.norm_id(key))
    if not m:
        return
    epic_num = m.group(1)
    board = wf.parse_board(wf.read_text(project / wf.BOARD_REL))
    epic_key = f"epic-{epic_num}"
    if epic_key not in board:
        return
    children = {k: v["status"] for k, v in board.items()
                if wf.is_story_key(k) and wf.norm_id(k).startswith(f"{epic_num}-")}
    open_kids = {k: s for k, s in children.items() if s not in wf.TERMINAL}
    if board[epic_key]["status"] in wf.TERMINAL:
        rep.info("epic", f"{epic_key} already {board[epic_key]['status']}")
    elif open_kids:
        rep.info("epic", f"{epic_key} stays open: {len(open_kids)} child(ren) not terminal "
                         f"({', '.join(sorted(open_kids)[:4])}{'...' if len(open_kids) > 4 else ''})")
    else:
        rep.warn("epic", f"{epic_key} is '{board[epic_key]['status']}' but ALL "
                         f"{len(children)} children are terminal - it can close now")


def main() -> int:
    ap = argparse.ArgumentParser(description="Close-out preflight (Wave 1.4)")
    ap.add_argument("--story", required=True)
    ap.add_argument("--project")
    ap.add_argument("--worktree", help="the story's worktree, checked for sync too")
    ap.add_argument("--branch", help="the story's branch, when it is not named after the story")
    ap.add_argument("--require-gates", default="", help="comma-separated gate names")
    ap.add_argument("--sha", help="check gate receipts against THIS commit, not HEAD")
    ap.add_argument("--fetch", action="store_true", help="fetch first (network)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    project = wf.resolve_project_root(args.project)
    board = wf.parse_board(wf.read_text(project / wf.BOARD_REL))
    want = wf.norm_id(args.story)
    matches = [k for k in board if wf.is_story_key(k)
               and (wf.norm_id(k) == want or wf.norm_id(k).startswith(want + "-"))]
    if not matches:
        wf.die(f"no board key matches '{args.story}'")
    key = matches[0]

    rep = wf.Report()
    rep.info("story", f"{key} = {board[key]['status']}")
    check_landed(project, key, rep, args.branch)
    check_sync("project", project, args.fetch, rep)
    lobby = wf.find_lobby_root(Path.cwd())
    if lobby and lobby != project:
        check_sync("lobby", lobby, args.fetch, rep)
    if args.worktree:
        check_sync("worktree", Path(args.worktree).resolve(), args.fetch, rep)
    check_worktrees(project, rep)
    check_surfaces(project, key, rep)
    check_artifacts(project, key, rep)
    check_file_list(project, key, rep)
    check_budget(project, rep)
    check_gates(project, args.story,
                [g.strip() for g in args.require_gates.split(",") if g.strip()], rep, args.sha)
    check_epic(project, key, rep)

    if args.json:
        print(json.dumps({"story": key, "findings": rep.items, "exit": rep.exit_code()},
                         indent=2))
    else:
        rep.print_human(f"closeout preflight - {key}")
        e, _ = rep.counts()
        print("VERDICT: " + ("BLOCKED - resolve the errors above" if e
                             else "clear to close out"))
    return rep.exit_code()


if __name__ == "__main__":
    sys.exit(main())
