"""jira_feed.py - feed the dev flow's knowledge back into its Jira ticket (SCC-49).

The board used to carry titles and nothing else: `/sudo-write-story-tests` minted with
`--summary` only, and close-out posted a single verdict line. Everything learned WHILE the
story was built - the decisions, the pitfalls, what is still owed - lived in the walkthrough
and never reached the ticket, so Jira could tell you a story existed but never what it was
about or what building it taught. SCC-49 closes that.

    jira_feed.py outline   --story 12.3.4 --project P [--epic 12] [--out FILE]
    jira_feed.py mint      --story 12.3.4 --project P --jira-project AVCH --epic-key AVCH-13
                           --summary "..." [--lane quick-dev] [--parallel-ok] [--apply]
    jira_feed.py devrecord --key AVCH-15 --story 12.3.4 --project P [--decision ...]
                           [--pitfall ...] [--followon ...] [--apply] [--strict]
    jira_feed.py check     --key AVCH-15 [--story 12.3.4]

Two invariants this file exists to hold, because prose could not:

1. **Nothing is invented.** The outline is rendered FROM the story file - its statement and
   its acceptance criteria, verbatim. A missing section renders as an explicit "(none found
   in ...)" line and warns; it never gets filled in with something plausible.
2. **One Dev Record per ticket, always current.** `devrecord` looks for an existing record
   first and UPDATES it rather than stacking a second one. Both `/sudo-quick-dev` (which
   closes its own branch) and `/sudo-update-sprint-memory` (which closes the story) post
   through here, and before this they would have produced two records of the same work.

Both write verbs READ THE TICKET BACK and exit non-zero if what they claimed to write is not
there - an acli call that silently no-ops looks exactly like one that worked.

Stdlib only, Python 3.11, plain-ASCII console output (Windows consoles are cp1252). `acli`
is resolved from --acli, then $ACLI_BIN, then PATH, so the tests can inject a stub.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wf_common as wf

EPICS_REL = wf.EPICS_REL
MARKER = "Dev Record"
# Descriptions shorter than this are a placeholder, not an outline. `check` uses it to tell a
# real description from acli having accepted an empty --description without complaint.
MIN_DESCRIPTION = 40

_ASCII_FOLD = {
    "—": "-", "–": "-", "‘": "'", "’": "'",
    "“": '"', "”": '"', "…": "...", " ": " ",
    "→": "->", "≥": ">=", "≤": "<=", "·": "-",
}


def ascii_out(s: str) -> str:
    """Fold typography to ASCII for CONSOLE output only.

    Ticket bodies keep whatever the story file said - Jira is UTF-8 and the board already
    carries em dashes. This is purely so `print()` cannot raise UnicodeEncodeError on the
    PC's cp1252 console, which would turn a successful post into a crash after the fact."""
    for k, v in _ASCII_FOLD.items():
        s = s.replace(k, v)
    return s.encode("ascii", "replace").decode("ascii")


def say(msg: str) -> None:
    print(ascii_out(msg))


def warn(msg: str) -> None:
    print(ascii_out("[WARN] " + msg), file=sys.stderr)


# ── acli ───────────────────────────────────────────────────────────────────────

def acli_bin(explicit: str | None) -> str:
    """--acli beats $ACLI_BIN beats PATH. The env hook is what lets the test suite run the
    whole post-and-verify path against a stub instead of the live board."""
    for cand in (explicit, os.environ.get("ACLI_BIN")):
        if cand:
            return cand
    found = shutil.which("acli")
    if not found:
        wf.die("acli not found. Install it, or pass --acli / set ACLI_BIN. "
               "See .agents/rules/jira.md")
    return found


def acli(binary: str, args: list[str], timeout: int = 90) -> subprocess.CompletedProcess:
    return subprocess.run([binary, *args], capture_output=True, text=True,
                          errors="replace", timeout=timeout)


def acli_json(binary: str, args: list[str]) -> object | None:
    """Parse acli's --json output, which is an ARRAY on some verbs and an OBJECT on others.

    `workitem search --json` returns a bare list of issues while `view` and `comment list`
    return objects, so a parser that only accepts one shape reads a perfectly good response
    as a failure. It also scans for the first balanced value rather than parsing the whole
    stream: acli prints human chatter alongside JSON on several paths."""
    r = acli(binary, args)
    if r.returncode != 0:
        return None
    out = r.stdout or ""
    dec = json.JSONDecoder()
    for i, ch in enumerate(out):
        if ch in "{[":
            try:
                return dec.raw_decode(out[i:])[0]
            except ValueError:
                continue
    return None


def as_items(data: object, key: str) -> list[dict]:
    """A bare list, or the list under `key` in an object - normalized either way."""
    if isinstance(data, list):
        return [i for i in data if isinstance(i, dict)]
    if isinstance(data, dict) and isinstance(data.get(key), list):
        return [i for i in data[key] if isinstance(i, dict)]
    return []


def adf_text(node: object) -> str:
    """Flatten an Atlassian Document Format tree to plain text.

    Descriptions and comments come BACK as ADF even when they were sent as plain text, so
    every read-back verification has to walk this. A `text` node carries the words; the
    block-level nodes only carry structure worth one newline."""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(adf_text(n) for n in node)
    if isinstance(node, dict):
        kind = node.get("type")
        if kind == "text":
            return str(node.get("text", ""))
        if kind == "hardBreak":
            return "\n"
        inner = adf_text(node.get("content"))
        if kind in ("paragraph", "heading", "listItem", "codeBlock", "blockquote"):
            return inner + "\n"
        return inner
    return ""


def field_text(value: object) -> str:
    """A Jira text field is ADF (dict), plain text (str), or absent (None)."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return adf_text(value).strip()


# ── Reading the story file ─────────────────────────────────────────────────────

_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_STORY_PREFIX_RE = re.compile(r"^story\s+[0-9][0-9.\-a-z]*\s*[:\-–—]\s*", re.IGNORECASE)
_AC_HEAD_RE = re.compile(r"^#{2,4}\s*(?:Acceptance\s+Criteria|ACs?)\b.*$",
                         re.MULTILINE | re.IGNORECASE)
_STORY_HEAD_RE = re.compile(r"^#{2,4}\s*Story\s*$", re.MULTILINE | re.IGNORECASE)
_NEXT_HEAD_RE = re.compile(r"^#{1,4}\s+\S", re.MULTILINE)
_BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")
_EMPH_RE = re.compile(r"\*\*|__|(?<!`)\*(?!\*)")


def section_body(text: str, head_match: re.Match | None) -> str:
    """Everything under a heading up to the next heading of any level."""
    if not head_match:
        return ""
    rest = text[head_match.end():]
    nxt = _NEXT_HEAD_RE.search(rest)
    return rest[:nxt.start()] if nxt else rest


def flatten(s: str, cap: int) -> str:
    s = _EMPH_RE.sub("", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= cap else s[: cap - 3].rstrip() + "..."


def story_title(text: str) -> str:
    m = _H1_RE.search(text)
    if not m:
        return ""
    return flatten(_STORY_PREFIX_RE.sub("", m.group(1).strip()), 160)


def story_statement(text: str) -> str:
    """The As-a / I-want / So-that block, collapsed to one paragraph.

    Capped hard: some story files run four paragraphs here, and a ticket description that
    reproduces the whole file is the same failure as one with no description - nobody reads
    it. The ticket points AT the story file; it does not replace it."""
    body = section_body(text, _STORY_HEAD_RE.search(text))
    return flatten(body, 700)


def acceptance_criteria(text: str) -> list[str]:
    """List items under the Acceptance Criteria heading.

    Story files write ACs as `- **AC-1 (name):** ...` and as plain `1. ...`; both reduce to
    the bullet regex. Non-bullet prose in the section is deliberately dropped - it is
    commentary around the criteria, and including it makes the ticket unreadable."""
    body = section_body(text, _AC_HEAD_RE.search(text))
    out: list[str] = []
    current: list[str] = []
    for line in body.splitlines():
        m = _BULLET_RE.match(line)
        if m:
            if current:
                out.append(flatten(" ".join(current), 240))
            current = [m.group(1)]
        elif current and line.strip() and line.startswith((" ", "\t")):
            current.append(line.strip())  # a wrapped continuation of the item above
        elif current and not line.strip():
            out.append(flatten(" ".join(current), 240))
            current = []
    if current:
        out.append(flatten(" ".join(current), 240))
    return [a for a in out if a][:15]


def resolve_story_file(project: Path, story: str, explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.is_file():
            wf.die(f"--story-file not found: {explicit}")
        return p
    hits = wf.find_story_files(project, story)
    if not hits:
        wf.die(f"no story file for '{story}' under {wf.STORIES_REL} - "
               f"pass --story-file, or check the id")
    if len(hits) > 1:
        wf.die(f"'{story}' matches {len(hits)} story files "
               f"({', '.join(h.name for h in hits)}) - pass --story-file")
    return hits[0]


def resolve_root(arg: str | None, need_board: bool) -> Path:
    """A project root - or, for ad-hoc chore work, just the repo we are standing in.

    `wf.resolve_project_root` requires a sprint board, and the command centre deliberately
    has none: toolkit chore work is not a BMAD story. But it has `_artifacts/` and it has
    tickets, so a Dev Record must be fileable there - otherwise the one repo where the
    workflow itself gets built is the one repo whose tickets stay empty. Verbs that read a
    story file or epics.md still demand a real project (need_board=True)."""
    if need_board:
        return wf.resolve_project_root(arg)
    if arg:
        cand = Path(arg)
        if cand.is_dir():
            return cand.resolve()
        lobby = wf.find_lobby_root(Path.cwd())
        if lobby and (lobby / "Projects" / arg).is_dir():
            return (lobby / "Projects" / arg).resolve()
        wf.die(f"cannot resolve project '{arg}'")
    cwd = Path.cwd()
    for p in [cwd, *cwd.parents]:
        if (p / wf.BOARD_REL).is_file() or (p / "_artifacts").is_dir() or (p / ".git").is_dir():
            return p.resolve()
    return cwd.resolve()


def rel_to(path: Path, root: Path) -> str:
    """Project-relative when possible, absolute when not.

    macOS resolves /tmp to /private/tmp and a story worktree can sit behind a symlink, so a
    path handed in with --walkthrough / --story-file and the resolved project root can name
    the same file with different prefixes. `relative_to` RAISES on that, and a ticket losing
    its whole evidence section to a ValueError is far worse than one longer path."""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def frontmatter_value(text: str, key: str) -> str:
    m = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", text[:2000], re.MULTILINE)
    return m.group(1).split("#", 1)[0].strip() if m else ""


# ── Reading the epic ───────────────────────────────────────────────────────────

def epic_section(project: Path, epic: str) -> tuple[str, str]:
    """(title, body) for `## Epic N: Title` in epics.md, at whatever heading level it uses."""
    path = project / EPICS_REL
    if not path.is_file():
        wf.die(f"no epics file at {EPICS_REL}")
    text = wf.read_text(path)
    head = re.search(rf"^(#{{2,4}})\s*Epic\s+{re.escape(epic)}\s*[:\-–—]\s*(.+?)\s*$",
                     text, re.MULTILINE | re.IGNORECASE)
    if not head:
        wf.die(f"no 'Epic {epic}' heading in {EPICS_REL}")
    rest = text[head.end():]
    same_or_higher = re.compile(rf"^#{{1,{len(head.group(1))}}}\s+\S", re.MULTILINE)
    nxt = same_or_higher.search(rest)
    return head.group(2).strip(), (rest[:nxt.start()] if nxt else rest)


# ── Rendering ──────────────────────────────────────────────────────────────────

def render_story_outline(project: Path, story_file: Path, story: str, args) -> str:
    text = wf.read_text(story_file)
    title = story_title(text)
    statement = story_statement(text)
    acs = acceptance_criteria(text)
    rel = rel_to(story_file, project)

    lines = [f"{story} - {title}" if title else f"Story {story}", ""]
    if statement:
        lines += [statement, ""]
    else:
        warn(f"{rel}: no '## Story' section - the outline has no statement")
        lines += ["(no '## Story' section in the story file)", ""]

    lines.append("Acceptance criteria")
    if acs:
        lines += [f"{i}. {a}" for i, a in enumerate(acs, 1)]
    else:
        warn(f"{rel}: no acceptance criteria found - the ticket will say so")
        lines.append("(none found in the story file)")

    lane = args.lane or (frontmatter_value(text, "lane") or "full")
    bdd = frontmatter_value(text, "bdd")
    blocked = ", ".join(args.blocked_by) if args.blocked_by else "-"
    lines += ["",
              f"Lane: {lane} | Parallel-ok: {'yes' if args.parallel_ok else 'no'} "
              f"| Blocked by: {blocked}"]
    if bdd:
        lines.append(f"BDD: {bdd}")
    if args.epic_key:
        lines.append(f"Epic: {args.epic_key}")
    lines += [f"Story file: {rel}",
              "",
              "Rendered by jira_feed.py at story pickup. The story file is the source of "
              "truth; this is its outline."]
    return "\n".join(lines) + "\n"


def render_epic_outline(project: Path, epic: str) -> str:
    title, body = epic_section(project, epic)
    goal = ""
    bullets: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("---", "#")):
            continue
        m = _BULLET_RE.match(line)
        if m:
            bullets.append(flatten(m.group(1), 200))
        elif not goal:
            goal = flatten(stripped, 700)
    lines = [f"Epic {epic} - {title}", ""]
    lines += [goal, ""] if goal else ["(no goal paragraph in epics.md)", ""]
    if bullets:
        lines.append("From epics.md")
        lines += [f"- {b}" for b in bullets[:12]]
        lines.append("")
    lines += [f"Epic source: {EPICS_REL} (Epic {epic})",
              f"Board: {wf.BOARD_REL} (epic-{epic})",
              "",
              "Rendered by jira_feed.py at epic kickoff. Stories are minted per-story by "
              "/sudo-write-story-tests as work starts."]
    return "\n".join(lines) + "\n"


# ── The Dev Record ─────────────────────────────────────────────────────────────

_VERDICT_RE = re.compile(
    r"^[>\-*#\s]*\**\s*Verdict:\**\s*\**(PASS|CONCERNS|FAIL|WAIVED)\**"
    r"(?:[^\n]*?@\s*`?([0-9a-f]{7,40}))?",
    re.MULTILINE | re.IGNORECASE)

# Headings whose bullets belong in each bucket. The scrape is a SAFETY NET under the
# --decision/--pitfall/--followon flags, never the primary source: close-out has just
# finished Step 3's learning routing and holds these buckets in hand.
_SCRAPE_HEADS = {
    "decisions": r"(?:Decisions?(?:\s+made)?|Rulings?|Choices?)",
    "pitfalls": r"(?:Pitfalls?|Gotchas?|Traps?|Surprises?|Lessons?(?:\s+learned)?)",
    "followons": r"(?:Follow[\-\s]?ons?|Follow[\-\s]?ups?|Still\s+owed|Deferred|Owed)",
}


def scrape_bucket(text: str, pattern: str) -> list[str]:
    out: list[str] = []
    for head in re.finditer(rf"^#{{2,6}}\s*{pattern}\b.*$", text, re.MULTILINE | re.IGNORECASE):
        for line in section_body(text, head).splitlines():
            m = _BULLET_RE.match(line)
            if m:
                item = flatten(m.group(1), 240)
                if item and item not in out:
                    out.append(item)
    return out


def find_walkthrough(project: Path, story: str, explicit: str | None) -> Path | None:
    if explicit:
        p = Path(explicit)
        if not p.is_file():
            wf.die(f"--walkthrough not found: {explicit}")
        return p
    slug = wf.norm_id(story)

    def owns(folder: str) -> bool:
        have = wf.norm_id(folder).removeprefix("story-")
        # slug_matches first: 21-8 must not adopt 21-8b's walkthrough (the same guard
        # closeout_preflight needs, for the same reason). The SUFFIX form additionally
        # catches dated/autopilot folders (`2026-06-22_autopilot-12-3-4`), which the plain
        # form misses entirely. Suffix only, never interior: `-12-3-` also sits inside
        # `...-12-3-4`, so an interior match is exactly how a parent adopts its child's doc.
        return wf.slug_matches(slug, have) or have.endswith("-" + slug)

    hits = [p for p in project.glob("_artifacts/**/walkthrough.md") if owns(p.parent.name)]
    return sorted(hits)[-1] if hits else None


def render_devrecord(project: Path, story: str, args) -> tuple[str, list[str]]:
    """Returns (body, empty-bucket-names). Flags first, walkthrough scrape underneath."""
    wt = find_walkthrough(project, story, args.walkthrough)
    wt_text = wf.read_text(wt) if wt else ""
    if not wt and not args.walkthrough:
        warn(f"no walkthrough.md found for '{story}' - the record carries only what was "
             f"passed on the command line")

    buckets = {
        "decisions": list(args.decision or []),
        "pitfalls": list(args.pitfall or []),
        "followons": list(args.followon or []),
    }
    for name, pattern in _SCRAPE_HEADS.items():
        for item in scrape_bucket(wt_text, pattern):
            if item not in buckets[name]:
                buckets[name].append(item)

    verdict = args.verdict or ""
    if not verdict and wt_text:
        m = _VERDICT_RE.search(wt_text)
        if m:
            verdict = f"{m.group(1).upper()}" + (f" @ {m.group(2)}" if m.group(2) else "")

    lines = [f"{MARKER} - {story} ({args.stage}, {args.date})", ""]
    outcome = args.outcome or (f"Verdict: {verdict}" if verdict else "")
    if outcome:
        lines += [f"Outcome: {outcome}", ""]

    empty: list[str] = []
    for name, label in (("decisions", "Decisions made during dev"),
                        ("pitfalls", "Pitfalls found"),
                        ("followons", "Follow-ons / still owed")):
        lines.append(label)
        if buckets[name]:
            lines += [f"- {i}" for i in buckets[name]]
        else:
            lines.append("- (none recorded)")
            empty.append(name)
        lines.append("")

    lines.append("Evidence")
    for ev in (args.evidence or []):
        lines.append(f"- {ev}")
    if wt:
        lines.append(f"- walkthrough: {rel_to(wt, project)}")
    story_file = wf.find_story_files(project, story)
    if len(story_file) == 1:
        lines.append(f"- story file: {rel_to(story_file[0], project)}")
    if verdict and outcome and verdict not in outcome:
        lines.append(f"- review verdict: {verdict}")
    lines += ["", "Posted by jira_feed.py - one Dev Record per ticket, updated in place."]
    return "\n".join(lines) + "\n", empty


# ── Ticket I/O ─────────────────────────────────────────────────────────────────

def view_fields(binary: str, key: str) -> dict:
    data = acli_json(binary, ["jira", "workitem", "view", key,
                              "--fields", "key,summary,status,description,parent,labels",
                              "--json"])
    if data is None:
        wf.die(f"could not read {key} from Jira (is acli authenticated? "
               f"`acli jira auth status`)")
    if isinstance(data, list):
        data = data[0] if data else {}
    fields = data.get("fields") if isinstance(data, dict) else None
    return fields if isinstance(fields, dict) else {}


def list_comments(binary: str, key: str) -> list[dict]:
    return as_items(acli_json(binary, ["jira", "workitem", "comment", "list", "--key", key,
                                       "--json", "--limit", "100"]), "comments")


def find_devrecord(comments: list[dict], story: str | None) -> dict | None:
    """The existing Dev Record on this ticket, if any - this is what makes it ONE record.

    Matches on the marker plus (when given) the story id, so a ticket that legitimately
    carries records for two ids does not have one overwrite the other."""
    want = wf.norm_id(story) if story else None
    for c in reversed(comments):
        text = field_text(c.get("body"))
        if MARKER.lower() not in text[:400].lower():
            continue
        if want and want not in wf.norm_id(text[:400]):
            continue
        return c
    return None


def write_temp(body: str) -> Path:
    fd, name = tempfile.mkstemp(prefix="jira-feed-", suffix=".txt", text=True)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    return Path(name)


# ── Verbs ──────────────────────────────────────────────────────────────────────

def cmd_outline(args) -> int:
    project = resolve_root(args.project, need_board=True)
    if args.epic:
        body = render_epic_outline(project, args.epic)
    else:
        if not args.story:
            wf.die("outline needs --story or --epic")
        body = render_story_outline(
            project, resolve_story_file(project, args.story, args.story_file),
            args.story, args)
    if args.out:
        Path(args.out).write_text(body, encoding="utf-8", newline="\n")
        say(f"jira-feed: outline written to {args.out} ({len(body)} chars)")
    else:
        sys.stdout.write(body)
    return 0


def issue_type(args) -> str:
    """Story vs Task follows the HIERARCHY, not a flag default (operator ruling 2026-08-08).

    A **Story** is a child of an epic - it has an epic behind it and a story file in the tree.
    A **Task** is work nobody wrote an epic and a story for: chore, toolkit, ad-hoc fixes.
    Both are real and both get used, so the type is derived from whether an epic key is in
    hand rather than hardcoded; `--type` still overrides for the odd case (a Bug, say).
    Deriving it is the point - a fixed default is how every story ticket on the board ended
    up a Task."""
    if args.type:
        if args.type.lower() == "story" and not args.epic_key:
            warn("--type Story with no --epic-key: a story hangs under an epic. Pass "
                 "--epic-key, or mint it as a Task if there is genuinely no epic.")
        return args.type
    return "Story" if args.epic_key else "Task"


def cmd_mint(args) -> int:
    """Dedupe, create with the description, then PROVE the description landed.

    The dedupe search is here rather than in the command prose because a backfilled or
    re-run board is the normal case, and a second ticket for the same story is worse than
    no ticket - two rows, one of which nothing will ever move again."""
    project = resolve_root(args.project, need_board=True)
    binary = acli_bin(args.acli)
    story_file = resolve_story_file(project, args.story, args.story_file)
    body = render_story_outline(project, story_file, args.story, args)
    summary = args.summary or f"{args.story} - {story_title(wf.read_text(story_file))}"

    if not args.apply:
        say(f"jira-feed: DRY RUN - would mint {issue_type(args)} '{summary}' "
            f"in {args.jira_project}")
        sys.stdout.write(body)
        return 0

    existing = None
    found = acli_json(binary, ["jira", "workitem", "search", "--json", "--limit", "20",
                               "--jql", f'project = {args.jira_project} '
                                        f'AND summary ~ "{args.story}"'])
    for item in as_items(found, "issues"):
        # `~` is a fuzzy text match, so 12.3 also returns 12.3.4 - only a ticket whose
        # summary STARTS with this exact BMAD number is the same story.
        head = field_text((item.get("fields") or {}).get("summary")).strip()
        if head and wf.norm_id(head.split()[0]) == wf.norm_id(args.story):
            existing = item.get("key")
            break

    tmp = write_temp(body)
    try:
        if existing:
            say(f"jira-feed: reusing existing ticket {existing} for story {args.story}")
            key = existing
            if len(field_text(view_fields(binary, key).get("description"))) < MIN_DESCRIPTION:
                # --yes: `edit` prompts interactively without it, which hangs an agent run.
                r = acli(binary, ["jira", "workitem", "edit", "--key", key, "--yes",
                                  "--description-file", str(tmp)])
                if r.returncode != 0:
                    wf.die(f"backfilling the description on {key} failed: "
                           f"{(r.stderr or r.stdout).strip()[:400]}")
                say(f"jira-feed: backfilled the outline onto bare ticket {key}")
        else:
            create = ["jira", "workitem", "create", "--project", args.jira_project,
                      "--type", issue_type(args), "--summary", summary,
                      "--description-file", str(tmp), "--json"]
            if args.epic_key:
                create += ["--parent", args.epic_key]
            labels = list(args.label or [])
            if args.lane == "quick-dev":
                labels.append("quick-dev")
            if args.parallel_ok:
                labels.append("parallel-ok")
            if args.blocked_by:
                labels.append("blocked")
            if labels:
                create += ["--label", ",".join(dict.fromkeys(labels))]
            r = acli(binary, create)
            if r.returncode != 0:
                wf.die(f"acli create failed: {(r.stderr or r.stdout).strip()[:400]}")
            m = re.search(r"\b([A-Z][A-Z0-9]+-\d+)\b", r.stdout or "")
            if not m:
                wf.die(f"created, but no key in acli output - do NOT invent one, read the "
                       f"board: {(r.stdout or '').strip()[:400]}")
            key = m.group(1)
    finally:
        tmp.unlink(missing_ok=True)

    landed = field_text(view_fields(binary, key).get("description"))
    if len(landed) < MIN_DESCRIPTION:
        say(f"jira-feed: {key} minted but its description is empty or truncated "
            f"({len(landed)} chars) - fix before continuing")
        return 2
    say(f"jira-feed: {key} carries its outline ({len(landed)} chars)")
    say(f"JIRA_KEY={key}")
    return 0


def cmd_devrecord(args) -> int:
    # need_board=False: an ad-hoc chore fix has a ticket and a walkthrough but no board.
    project = resolve_root(args.project, need_board=False)
    body, empty = render_devrecord(project, args.story, args)
    for name in empty:
        warn(f"the '{name}' bucket is empty - pass --{name.rstrip('s')}, or accept that "
             f"the ticket records none")
    if empty and args.strict:
        say(f"jira-feed: STRICT - {len(empty)} empty bucket(s): {', '.join(empty)}")
        return 2
    if not args.apply:
        say(f"jira-feed: DRY RUN - would post to {args.key or '<no --key>'}")
        sys.stdout.write(body)
        return 0
    if not args.key:
        wf.die("devrecord --apply needs --key")

    binary = acli_bin(args.acli)
    prior = find_devrecord(list_comments(binary, args.key), args.story)
    tmp = write_temp(body)
    try:
        if prior and not args.append_new:
            # ONE record per ticket: quick-dev closing its own branch and close-out closing
            # the story both post here, and stacking them buries the current one.
            cid = str(prior.get("id") or "")
            if not cid:
                wf.die(f"{args.key} already has a Dev Record but acli returned no comment "
                       f"id - refusing to post a second one")
            r = acli(binary, ["jira", "workitem", "comment", "update", "--key", args.key,
                              "--id", cid, "--body-file", str(tmp)])
            action = f"updated the existing Dev Record (comment {cid})"
        else:
            r = acli(binary, ["jira", "workitem", "comment", "create", "--key", args.key,
                              "--body-file", str(tmp)])
            action = "posted a new Dev Record"
        if r.returncode != 0:
            wf.die(f"acli comment failed: {(r.stderr or r.stdout).strip()[:400]}")
    finally:
        tmp.unlink(missing_ok=True)

    if not find_devrecord(list_comments(binary, args.key), args.story):
        say(f"jira-feed: acli reported success but {args.key} carries no Dev Record on "
            f"read-back - NOT recorded")
        return 2
    say(f"jira-feed: {args.key} {action} ({len(body)} chars)")
    return 0


def cmd_check(args) -> int:
    """Is this ticket actually carrying the feed - description AND one Dev Record?"""
    binary = acli_bin(args.acli)
    rep = wf.Report()
    fields = view_fields(binary, args.key)
    desc = field_text(fields.get("description"))
    if len(desc) < MIN_DESCRIPTION:
        rep.err("description", f"{args.key}: {len(desc)} chars - no outline "
                               f"(jira_feed.py mint renders one from the story file)")
    else:
        rep.info("description", f"{args.key}: outline present ({len(desc)} chars)")

    comments = list_comments(binary, args.key)
    records = [c for c in comments if MARKER.lower() in field_text(c.get("body"))[:400].lower()]
    if not records:
        rep.err("devrecord", f"{args.key}: no Dev Record - the decisions and pitfalls from "
                             f"dev never reached the ticket")
    elif len(records) > 1:
        # Not fatal, but it means something posted around the update path.
        rep.warn("devrecord", f"{args.key}: {len(records)} Dev Records - there should be "
                              f"exactly one, updated in place")
    else:
        rep.info("devrecord", f"{args.key}: one Dev Record "
                              f"({len(field_text(records[0].get('body')))} chars)")
    rep.print_human(f"jira-feed check {args.key}")
    return rep.exit_code()


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description="Feed dev knowledge into a Jira ticket (SCC-49)")
    sub = ap.add_subparsers(dest="verb", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--project", help="project name under Projects/, or a path")
        p.add_argument("--acli", help="path to acli (else $ACLI_BIN, else PATH)")

    def outline_flags(p: argparse.ArgumentParser) -> None:
        p.add_argument("--story", help="BMAD story id, e.g. 12.3.4")
        p.add_argument("--story-file", help="explicit story file (skips the id lookup)")
        p.add_argument("--epic-key", help="the epic's Jira key, e.g. AVCH-13")
        p.add_argument("--lane", choices=["full", "quick-dev"], help="ruled lane")
        p.add_argument("--parallel-ok", action="store_true")
        p.add_argument("--blocked-by", action="append", metavar="KEY")

    p_out = sub.add_parser("outline", help="render a ticket description; no network")
    common(p_out); outline_flags(p_out)
    p_out.add_argument("--epic", help="render an EPIC outline from epics.md instead")
    p_out.add_argument("--out", help="write to this file (for acli --description-file)")

    p_mint = sub.add_parser("mint", help="create/reuse the story ticket WITH its outline")
    common(p_mint); outline_flags(p_mint)
    p_mint.add_argument("--jira-project", required=True, help="e.g. AVCH (from .agents/jira.conf)")
    p_mint.add_argument("--summary", help="default: '<id> - <story title>'")
    p_mint.add_argument("--type", help="override; default is Story under an epic, "
                                       "Task without one (see issue_type)")
    p_mint.add_argument("--label", action="append")
    p_mint.add_argument("--apply", action="store_true", help="without this, renders only")

    p_dev = sub.add_parser("devrecord", help="post/update THE Dev Record comment")
    common(p_dev)
    p_dev.add_argument("--story", required=True)
    p_dev.add_argument("--key", help="the ticket; required with --apply")
    p_dev.add_argument("--walkthrough", help="explicit walkthrough.md (else found by id)")
    p_dev.add_argument("--decision", action="append", metavar="TEXT")
    p_dev.add_argument("--pitfall", action="append", metavar="TEXT")
    p_dev.add_argument("--followon", action="append", metavar="TEXT")
    p_dev.add_argument("--evidence", action="append", metavar="TEXT")
    p_dev.add_argument("--outcome", help="e.g. 'review -> done'")
    p_dev.add_argument("--verdict", help="override the walkthrough's Verdict line")
    p_dev.add_argument("--stage", default="close-out", help="close-out | quick-dev | ...")
    p_dev.add_argument("--date", default=date.today().isoformat())
    p_dev.add_argument("--strict", action="store_true", help="empty bucket is a hard fail")
    p_dev.add_argument("--append-new", action="store_true",
                       help="post a SECOND record instead of updating (rare)")
    p_dev.add_argument("--apply", action="store_true", help="without this, renders only")

    p_chk = sub.add_parser("check", help="does this ticket carry outline + Dev Record?")
    common(p_chk)
    p_chk.add_argument("--key", required=True)
    p_chk.add_argument("--story")

    args = ap.parse_args()
    return {"outline": cmd_outline, "mint": cmd_mint,
            "devrecord": cmd_devrecord, "check": cmd_check}[args.verb](args)


if __name__ == "__main__":
    sys.exit(main())
