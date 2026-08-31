"""closeout_preflight.py — run the close-out checklist instead of narrating it (Wave 1.4).

`/cicd-close-story-merge-tree` asks an agent to hold ~8 mechanical facts in its head at once:
did the code land, is every repo pushed, are the worktrees real, do both status surfaces
agree, is the context inside budget, did the gates actually run, can the epic close, and is
the story's verdict recorded. Each is a git or filesystem question with an exact answer, and
each has failed silently at least once (see the memory index). This answers all of them.

    closeout_preflight.py --story 21.8b --expect-key AVCH-91 [--project P]
                          [--worktree PATH] [--branch B] [--require-gates ruff,pytest]
                          [--sha X] [--no-fetch] [--json]

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
import walkthrough_roster as roster
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

# The ticket key as it appears in a branch NAME, for any lane prefix. ⛔ Deliberately NOT
# `task_preflight.BRANCH_RE`, which is anchored to `chore/`: the branches this script
# resolves are story lanes (`claude/*`) and epic branches, so reusing that pattern would
# match nothing here and the intent check would be dead code that always passes.
BRANCH_KEY_RE = re.compile(r"^[a-z]+/([A-Z][A-Z0-9]*-\d+)-")

# `find_branches` runs `git branch --list --all`, which returns remote-tracking branches as
# `origin/claude/SCC-99-slug`. Left alone, `^[a-z]+/` eats the `origin/` and the key group then
# fails on `claude` — so a WRONG-lane remote ref classified as "carries no key segment" and
# warned (exit 1, non-blocking) instead of erroring. That is the 2026-08-09 failure downgraded
# to a shrug, on the one path where it is hardest to notice: a sibling lane parked with its
# local branch already deleted, resolvable only through its remote ref.
REMOTE_PREFIX_RE = re.compile(r"^[^/]+/(?=[a-z]+/[A-Z])")


def branch_key(branch: str) -> str | None:
    """The Jira key a branch NAME carries, local or remote-tracking, or None."""
    m = BRANCH_KEY_RE.match(REMOTE_PREFIX_RE.sub("", branch))
    return m.group(1) if m else None


def check_intent(branches: list[str], expect: str, rep: wf.Report) -> None:
    """cwd is not intent — does the branch we resolved carry the key the caller MEANT?

    This script guesses. `find_branches` walks branch names, story-id spellings and the
    worktree list, and given an explicit `--branch` it simply returns it — never once
    comparing any of that to the lane the caller believes it is closing. So on 2026-08-09 a
    close-out preflight resolved a SIBLING lane's branch and reported every check honestly
    about the wrong work: `VERDICT: clear to close out`, exit 0.

    ⛔ Prose cannot catch that, and prose is what was there. `task_preflight.py` made the
    same check mechanical after the same failure (`--expect-key`, required); this is that
    guard, for the story lane.

    Three outcomes, and the third one matters as much as the first: a branch carrying the
    WRONG key is an error, a branch carrying no key at all is a WARN — refusing every
    pre-Jira branch (`claude/xdist-tail-hang`) would make the flag unusable on real history —
    and neither may be silent, because "I could not check" printing like "I checked and it
    is clean" is the failure this whole script exists to remove.
    """
    if not branches:
        return                       # check_landed already warned; a second row buries it
    keyed = {b: branch_key(b) for b in branches}
    right = sorted(b for b, k in keyed.items() if k == expect)
    wrong = sorted(b for b, k in keyed.items() if k and k != expect)
    bare = sorted(b for b, k in keyed.items() if k is None)

    if wrong and not right:
        found = sorted({keyed[b] for b in wrong})
        rep.err("intent", f"--expect-key {expect} but the resolved branch(es) carry "
                          f"{', '.join(found)} ({', '.join(wrong)}) - this preflight is "
                          f"aimed at ANOTHER lane. cwd is not intent: re-run against the "
                          f"branch you actually mean")
    elif wrong:
        rep.warn("intent", f"--expect-key {expect} matched {', '.join(right)}, but "
                           f"{', '.join(wrong)} also resolved and carries a different key")
    if bare and not right and not wrong:
        rep.warn("intent", f"--expect-key {expect}: {', '.join(bare)} carries no key "
                           f"segment, so the branch cannot confirm the lane - a pre-Jira "
                           f"branch; confirm by hand which lane this is")
    if right:
        rep.info("intent", f"--expect-key {expect} matches {', '.join(right)}")

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


def check_landed(project: Path, key: str, rep: wf.Report, branch: str | None = None,
                 expect: str | None = None) -> None:
    """Landing and close-out are separate events (memory: landing-is-not-closeout) -
    code merges while the board still reads `review`, and the board never notices."""
    branches = find_branches(project, key, branch)
    if expect:
        check_intent(branches, expect, rep)
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

def check_sync(label: str, repo: Path, fetch: bool, rep: wf.Report) -> bool:
    """`commit-and-push-are-one-action`: 0/0 + clean, per repo, or the step isn't done.

    Returns FRESHNESS, so the verdict line can carry it. It used to return nothing and the
    unfetched path emitted an INFO - exit-code-neutral, three lines above a verdict still
    reading "clear to close out". The verdict line is the only line an agent acts on, so a
    comparison made against yesterday's remote has to appear THERE, not near there.
    """
    if not (repo / ".git").exists():
        rep.info("sync", f"{label}: not a git repo, skipped")
        return True                  # nothing here can be stale
    fresh = True
    if fetch:
        f = wf.git(["fetch", "--quiet"], repo, timeout=180)
        if f.returncode != 0:
            # ⛔ WARN, and it costs freshness: a fetch that was ASKED for and failed is a
            # different remedy from one that was never asked for, and the verdict says which.
            rep.warn("sync", f"{label}: fetch FAILED - ahead/behind is vs the LAST fetch")
            fresh = False
    else:
        rep.warn("sync", f"{label}: --no-fetch, so ahead/behind is vs the LAST fetch, "
                         f"not the remote")
        fresh = False

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

    # ⛔ SCC-210 review · `-c core.quotepath=false`, and `.splitlines()` on the RAW stdout — both
    # are load-bearing
    # for the split below, and both were missing in the first cut of it.
    #   · quotepath: git octal-quotes any path holding a non-ASCII byte, `"` or `\`, so
    #     `_artifacts/_memory/café.md` arrives as `"_artifacts/_memory/caf\303\251.md"` and the
    #     `ln[3:]` test below never matches (`task_preflight.py` ~923 carries the same flag and
    #     the incident that forced it).
    #   · no `.strip()`: porcelain codes are TWO columns, so an unstaged modification is
    #     `" M path"` with a LEADING SPACE. Stripping the whole blob eats that space off the
    #     FIRST line only, shifting `ln[3:]` by one and turning `_artifacts/_memory/x.md` into
    #     `artifacts/_memory/x.md`. The memory class then misses and the generic class hands out
    #     "commit before closing out" — the exact instruction this split exists to prevent, on
    #     the single most common shape (one modified memory file, listed first).
    dirty = wf.git(["-c", "core.quotepath=false", "status", "--porcelain"], repo).stdout
    if dirty.strip():
        lines = [ln for ln in dirty.splitlines() if ln.strip()]
        # ⛔ ANOTHER SESSION'S MEMORY IS NOT THIS LANE'S DIRT, and folding the two together
        # does not merely under-report - it hands out the wrong instruction. Every session on
        # this machine writes `_artifacts/_memory/`, so a lane closing out routinely finds
        # files there it did not write. "commit before closing out" tells the agent to sweep
        # them under this story's key, which is the exact act `artifacts-always-first` forbids.
        # `task_preflight.py` (~926, ~952-960) split this class out for the Task lane; this is
        # the same split for the story lane, with the same ruling attached. Both classes stay
        # errors, so no exit code moves - only the reporting, and the instruction, divide.
        mem = [ln for ln in lines if ln[3:].startswith("_artifacts/_memory/")]
        rest = [ln for ln in lines if ln not in mem]
        if rest:
            rep.err("sync", f"{label}: {len(rest)} uncommitted change(s) - commit "
                            f"(explicit paths) before closing out")
        if mem:
            rep.err("sync", f"{label}: {len(mem)} dirty file(s) under `_artifacts/_memory/` - "
                            f"if ANOTHER session wrote them, park or leave them: never sweep, "
                            f"delete, or commit them under this story; if THIS session wrote "
                            f"them, commit them with explicit paths first")
    return fresh


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


def story_walkthroughs(project: Path, key: str) -> list[Path]:
    """Every walkthrough belonging to this story.

    ⛔ ONE finder, shared by `check_artifacts` and `check_overview` (SCC-357). Two copies of
    a `slug_matches` glob is two chances to disagree about WHICH walkthrough is the story's,
    and the second reader would be the one nobody tested against `21-8`/`21-8b`.
    """
    slug = wf.norm_id(key)
    # slug_matches, not startswith: `21-8` must not adopt `21-8b`'s walkthrough.
    return [p for p in project.glob("_artifacts/**/walkthrough.md")
            if wf.slug_matches(slug, wf.norm_id(p.parent.name).removeprefix("story-"))]


def check_artifacts(project: Path, key: str, rep: wf.Report) -> None:
    """The two-doc close puts the flip gate in the walkthrough's `Verdict:` line
    (memory: story-artifacts-two-doc-close). Absent section = the step never ran."""
    hits = story_walkthroughs(project, key)
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
        # ⛔ SCC-173/SCC-177 — A VERDICT IS THE REVIEW'S CONCLUSION, NOT EVIDENCE IT RAN.
        # `Verdict: PASS @ <sha>` with zero lenses run merged cleanly here until now: the only
        # proof of a review was the line asserting its own result. ONE parser, shared with
        # task_preflight, so the two gates cannot drift; it is handed the verdict THIS reader
        # just resolved, so scoping is answered by the reader's own eyes. Ships ARMED and
        # BLOCKING by operator ruling 2026-08-15; the dated cutoff is the scope limiter.
        ok_roster, why = roster.judge(text, path, verdict)
        for line in why:
            (rep.info if ok_roster else rep.err)("artifacts", f"{rel}: {line}")
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


# ── 4b. Is the project's overview guide current? (SCC-357) ─────────────────────────
#
# `docs/project_overview_guide.md` is the page that says what was BUILT and how a request
# flows through it — for a human. It is not the PRD: the PRD says what was WANTED, and it is
# never rewritten from this page. The guide goes stale story by story, so it is kept current
# story by story, at the save, while the context that makes the edit correct still exists.
#
# ⛔ THE DATED CUTOFF IS LOAD-BEARING, NOT A COURTESY. This script is ALSO run by
# `/cicd-prune-worktree` and `/cicd-merge-epic-workingtrees`. Without the cutoff, the day a
# project gains a guide every story saved before the law existed starts failing here — and
# those stories are `Done`, their worktrees are what the operator is trying to prune, and the
# only "remedy" the error could name is re-running a save on closed work. A gate whose refusal
# has no reachable fix is a gate that gets disarmed. Same mechanism as
# `walkthrough_roster.CUTOFF`, and the lane's date comes from `roster.lane_date` — the artifact
# folder's prefix, never an mtime a checkout rewrites nor a `git log` a rebase rewrites.
OVERVIEW_REL = "docs/project_overview_guide.md"
OVERVIEW_CUTOFF = "2026-08-31"
# The two states the save may CLAIM. Anything else is prose: "updated", "reviewed" and
# "looked at" are all things an agent writes having done nothing, and accepting them would
# make the check satisfiable by wording (test OV6 is that control).
_OVERVIEW_LINE_RE = re.compile(
    r"^[>\-*#\s]*\**\s*project\s+overview\s+guide\s*:\**\s*(unchanged|absent)\b",
    re.I | re.M)


def check_overview(project: Path, key: str, rep: wf.Report) -> None:
    guide = project / OVERVIEW_REL
    if not guide.is_file():
        rep.warn("overview", f"no {OVERVIEW_REL} in this project - the save records it "
                             f"`absent`; writing the first edition is that project's own "
                             f"ticket, and nothing here blocks until it exists")
        return

    # Edited on this lane? Then it was kept current and there is nothing to account for.
    base = integration_branch(project)
    diff = wf.git(["diff", "--name-only", f"{base}...HEAD", "--", OVERVIEW_REL], project)
    if diff.returncode == 0 and any(ln.strip() for ln in diff.stdout.splitlines()):
        rep.info("overview", f"{OVERVIEW_REL} edited on this lane (vs {base})")
        return

    hits = story_walkthroughs(project, key)
    if not hits:
        # `check_artifacts` already errors on this and it is the same root cause; a second
        # error for one missing file reads as two problems.
        return
    for path in hits:
        rel = path.relative_to(project)
        if _OVERVIEW_LINE_RE.search(wf.read_text(path)):
            rep.info("overview", f"{rel}: guide unchanged, and the walkthrough says why")
            return
    date = roster.lane_date(hits[0])
    if date is not None and date < OVERVIEW_CUTOFF:
        rep.info("overview", f"lane dated {date} predates the guide law "
                             f"({OVERVIEW_CUTOFF}) - exempt")
        return
    rep.err("overview", f"{OVERVIEW_REL} is unchanged on this lane and no walkthrough "
                        f"accounts for it - `/cicd-update-sprint-memory` Step 3.5 never ran. "
                        f"Either edit the guide, or write `Project overview guide: unchanged "
                        f"- <reason>` into the walkthrough")


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
    """An umbrella cannot close itself (memory: `agy-epic-keys-rot-silently`, relocated by SCC-88
    to AGY's own store — `Projects/AGY_AVIATIONCHAT/_artifacts/_memory/`). When every child is
    terminal the epic key is the only thing left holding the epic open."""
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
    ap.add_argument("--expect-key", required=True,
                    help="the Jira key you INTEND to close (e.g. SCC-64) - the resolved "
                         "branch must carry it; cwd is not intent (SCC-64, SCC-210)")
    ap.add_argument("--project")
    ap.add_argument("--worktree", help="the story's worktree, checked for sync too")
    ap.add_argument("--branch", help="the story's branch, when it is not named after the story")
    ap.add_argument("--require-gates", default="", help="comma-separated gate names")
    ap.add_argument("--sha", help="check gate receipts against THIS commit, not HEAD")
    # ⭐ DEFAULT-ON. It was opt-in, so freshness rested on an agent remembering a flag, and
    # the unfetched verdict read exactly like a fetched one. `--fetch` still parses, so every
    # existing caller keeps working; `--no-fetch` is the explicit offline opt-out and it puts
    # STALE on the verdict line. A FAILED fetch only warns, so default-on is safe on a plane.
    ap.add_argument("--fetch", action=argparse.BooleanOptionalAction, default=True,
                    help="fetch before comparing (default: on). --no-fetch is the offline "
                         "opt-out and makes the VERDICT say the comparison is stale")
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
    check_landed(project, key, rep, args.branch, args.expect_key)
    fresh = check_sync("project", project, args.fetch, rep)
    lobby = wf.find_lobby_root(Path.cwd())
    if lobby and lobby != project:
        fresh = check_sync("lobby", lobby, args.fetch, rep) and fresh
    # ⭐ SCC-211 · THE LANE'S TREE IS DERIVED, NOT TAKEN ON TRUST. This used to be
    # `if args.worktree:` and nothing else, so the one tree whose dirt actually matters was
    # measured only when the caller remembered to name it. The door's prose said the flag was
    # mandatory; argparse did not, and `/cicd-prune-worktree` calls this script without it —
    # so in that shape the project root (standing on `main`, spotless) was the whole answer
    # while the lane's tree was dirty, and the run cleared the close-out.
    #
    # Making the flag `required=True` was the obvious fix and it is the weaker one: a required
    # flag can still be aimed at the wrong tree, and it breaks every caller that has none.
    # `wf.trees_to_measure` asks git which tree holds the branch — that cannot be forgotten and
    # cannot be aimed wrong — and keeps `--worktree` as an ADDITIONAL tree. One body, shared
    # with `/cicd-push-e2e` and `/smh-close-task-merge-tree`, so the three doors cannot drift
    # apart about what they are measuring.
    if args.branch:
        explicit = Path(args.worktree).resolve() if args.worktree else None
        for label, tree in wf.trees_to_measure(project, args.branch, explicit)[1:]:
            fresh = check_sync(label, tree, args.fetch, rep) and fresh
    elif args.worktree:
        fresh = check_sync("worktree", Path(args.worktree).resolve(), args.fetch, rep) and fresh
    check_worktrees(project, rep)
    check_surfaces(project, key, rep)
    check_artifacts(project, key, rep)
    check_overview(project, key, rep)
    check_file_list(project, key, rep)
    check_budget(project, rep)
    check_gates(project, args.story,
                [g.strip() for g in args.require_gates.split(",") if g.strip()], rep, args.sha)
    check_epic(project, key, rep)

    # ⭐ THE VERDICT IS COMPUTED ONCE, ABOVE BOTH OUTPUT PATHS. Three states, not two: the
    # third exists because "clear" computed against the LAST fetch reads identically to
    # "clear" computed against the remote, and the difference is a sibling lane that landed
    # while you were not looking. The two ways freshness is lost need DIFFERENT remedies, so
    # the line says which: a fetch that was asked for and failed is an uplink to fix; one
    # that was never asked for is a flag to drop.
    e, _w = rep.counts()
    if e:
        verdict = "BLOCKED - resolve the errors above"
    elif not fresh:
        verdict = ("clear - but vs the LAST fetch (STALE), not the remote; "
                   + ("the fetch was asked for and FAILED - fix the uplink and re-run"
                      if args.fetch else "re-run WITHOUT --no-fetch")
                   + " before you land anything")
    else:
        verdict = "clear to close out"

    if args.json:
        print(json.dumps({"story": key, "expect_key": args.expect_key, "fresh": fresh,
                          "findings": rep.items, "verdict": verdict,
                          "exit": rep.exit_code()}, indent=2))
    else:
        rep.print_human(f"closeout preflight - {key}")
        print("VERDICT: " + verdict)
    return rep.exit_code()


if __name__ == "__main__":
    sys.exit(main())
