"""jira_feed.py - feed the dev flow's knowledge back into its Jira ticket (SCC-49).

The board used to carry titles and nothing else: `/cicd-write-story-tests` minted with
`--summary` only, and close-out posted a single verdict line. Everything learned WHILE the
story was built - the decisions, the pitfalls, what is still owed - lived in the walkthrough
and never reached the ticket, so Jira could tell you a story existed but never what it was
about or what building it taught. SCC-49 closes that.

    jira_feed.py outline   --story 12.3.4 --project P [--epic 12] [--out FILE]
    jira_feed.py mint      --story 12.3.4 --project P --jira-project AVCH --epic-key AVCH-13
                           --summary "..." [--lane quick-dev] [--parallel-ok] [--apply]
    jira_feed.py devrecord --key AVCH-15 --project P [--story 12.3.4] [--decision ...]
                           # --story defaults to this lane's task.yaml branch slug
                           [--pitfall ...] [--followon ...] [--apply] [--strict]
    jira_feed.py audit     --jira-project AVCH --project P [--apply]
    jira_feed.py check     --key AVCH-15 [--story 12.3.4]
    jira_feed.py trace     --path backend/x.py:42 [--path ...] [--json]
    jira_feed.py flag      --key AVCH-15 --reason "..." [--evidence ...] [--apply]

`trace` + `flag` are the RAISE half of the `Bug` rule (SCC-54); `devrecord --closing` is the
clear half. They are two verbs and not one on purpose: `trace` reads git history and proposes,
`flag` writes the board and will only ever take a `--key` a human typed. A trace that guessed
wrong and flipped its own answer would pull a finished ticket out of `Done` on no evidence.

Two invariants this file exists to hold, because prose could not:

1. **Nothing is invented.** The outline is rendered FROM the story file - its statement and
   its acceptance criteria, verbatim. A missing section renders as an explicit "(none found
   in ...)" line and warns; it never gets filled in with something plausible.
2. **One Dev Record per ticket, always current.** `devrecord` looks for an existing record
   first and UPDATES it rather than stacking a second one. Both `/cicd-quick-dev` (which
   closes its own branch) and `/cicd-update-sprint-memory` (which closes the story) post
   through here, and before this they would have produced two records of the same work.
   ⛔ It finds that record by the **slug**, never by `--key` - so on a Task lane the slug comes
   from ONE place, the lane's `task.yaml branch:`, and `--story` is left off. Two spellings of
   one lane post two records, and `check` reports that as a FORK (SCC-174).

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


ACLI_UNREACHABLE = 124   # conventional "timed out"; also covers a binary that is not there


def acli(binary: str, args: list[str], timeout: int = 90) -> subprocess.CompletedProcess:
    try:
        return subprocess.run([binary, *args], capture_output=True, text=True,
                              errors="replace", timeout=timeout)
    except (subprocess.TimeoutExpired, OSError) as e:
        # A hung uplink and a missing/unresolvable binary both used to escape as an UNCAUGHT
        # traceback - process exit 1, which is not one of the documented codes. The hook
        # swallows any non-zero, so it never showed there; the agent lane is where it bit.
        # `/smh-quick-dev` reads this code, and its table says exit 2 means "the key is
        # wrong, mint a new ticket" - so a dead uplink was instructing a DUPLICATE ticket.
        return subprocess.CompletedProcess([binary, *args], ACLI_UNREACHABLE, "",
                                           f"acli unreachable: {e}")


def acli_json(binary: str, args: list[str], timeout: int = 90) -> object | None:
    """Parse acli's --json output, which is an ARRAY on some verbs and an OBJECT on others.

    `workitem search --json` returns a bare list of issues while `view` and `comment list`
    return objects, so a parser that only accepts one shape reads a perfectly good response
    as a failure. It also scans for the first balanced value rather than parsing the whole
    stream: acli prints human chatter alongside JSON on several paths."""
    r = acli(binary, args, timeout=timeout)
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
              "/cicd-write-story-tests as work starts."]
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

def view_fields(binary: str, key: str, timeout: int = 90,
                strict: bool = True) -> dict | None:
    """`--fields` is a WHITELIST, and `issuetype` has to be on it (SCC-54).

    It was not, and every type read in this file goes through here - so `have` came back `""`
    on a live board while reading perfectly on the stub, which ignored `--fields` and returned
    the whole shape regardless. Three things were silently broken by one missing word:
    `devrecord --closing` never saw a `Bug` so it never cleared one; its read-back would have
    reported FAILED if it had; and `audit --apply` reports FAILED on every conversion that in
    fact succeeded. A stub that is more generous than the real tool tests nothing."""
    data = acli_json(binary, ["jira", "workitem", "view", key,
                              "--fields",
                              "key,summary,status,description,parent,labels,issuetype",
                              "--json"], timeout=timeout)
    if data is None:
        if not strict:
            # The caller wants to TELL APART "the board said no" from "I could not reach the
            # board". Dying here collapses those into one exit code, and they call for
            # opposite actions: fix your key, versus try again later.
            return None
        wf.die(f"could not read {key} from Jira (is acli authenticated? "
               f"`acli jira auth status`)")
    if isinstance(data, list):
        data = data[0] if data else {}
    fields = data.get("fields") if isinstance(data, dict) else None
    return fields if isinstance(fields, dict) else {}


def list_comments(binary: str, key: str) -> list[dict]:
    return as_items(acli_json(binary, ["jira", "workitem", "comment", "list", "--key", key,
                                       "--json", "--limit", "100"]), "comments")


def find_user_tasks(comments: list[dict]) -> dict | None:
    """The existing "User tasks" comment, so `finish` UPDATES rather than stacks (SCC-155).

    Same shape and same reason as `find_devrecord` below: `finish` is designed to be re-run
    after every box the operator ticks, so posting unconditionally left one held ticket
    carrying a pile of near-identical comments with nothing marking the current one."""
    for c in reversed(comments):
        if USER_TASKS_MARKER.lower() in field_text(c.get("body"))[:200].lower():
            return c
    return None


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


_RECORD_ID_RE = re.compile(r"^\s*" + re.escape(MARKER) + r"\s*[-–—]\s*(.+?)\s*\(",
                           re.IGNORECASE)


def record_story_id(comment: dict) -> str:
    """The story id out of a Dev Record's own header - `Dev Record - <id> (<stage>, <date>)`.

    Two records on one ticket is TWO different situations and only one of them is a defect
    (SCC-113):

      * one id, two records - /cicd-quick-dev closed the branch and /cicd-update-sprint-memory
        closed the story and both posted. That is the failure SCC-49 wrote `check` for.
      * two ids, one record each - two LANES on one ticket. `find_devrecord` filters by id on
        purpose, exactly "so a ticket that legitimately carries records for two ids does not
        have one overwrite the other", and both Task surfaces pass `--story <branch-slug>`,
        which changes per lane. A follow-on rides the ticket it came from rather than minting
        a key, so this is the normal shape of a second lane - not something posting around
        the update path.

    Counting cannot tell them apart; the id can. A header that will not parse returns `""`, and
    `cmd_check` treats that bucket as UNIDENTIFIABLE rather than as a lane - an unparseable
    header is not evidence that a second lane exists, and letting it read as one turned a
    warning into a clean exit.

    ⚠ The id stops at the first `(`, so an id containing parentheses truncates and two such
    records collapse into one bucket - a FALSE duplicate warning. Ids are branch slugs and BMAD
    numbers today, neither of which carries parentheses; noted rather than guarded, because the
    failure is loud (a warning) rather than silent.
    """
    head = field_text(comment.get("body"))[:400]
    m = _RECORD_ID_RE.search(head)
    return wf.norm_id(m.group(1)) if m else ""


# ── SCC-174 · which lanes can this repo PROVE? ─────────────────────────────────
# A Dev Record's id is a free-text string a caller typed. Two ids on one ticket is therefore
# TWO situations - two lanes, or one lane filed under two spellings of itself - and the strings
# alone cannot tell them apart, because `devrecord` picks update-vs-create off the slug. What
# CAN tell them apart is the repo: a lane leaves a `task.yaml branch:` behind and it leaves refs
# behind. Everything below answers exactly that and nothing else.

_MANIFEST_BRANCH_RE = re.compile(r"^branch:\s*(\S+)\s*$", re.M)


def manifest_branches(repo: Path, include_new: bool = False) -> list[str]:
    """The `branch:` of every `task.yaml` git knows about - `git ls-files`, never a glob.

    ⛔ `Path.glob("**/task.yaml")` is the obvious shape and it is wrong HERE, for two reasons
    that are both about the lobby specifically. `Projects/` is gitignored and holds other repos'
    manifests, and `.claude/worktrees/` holds a second copy of this repo's own tree - a glob
    reads both and hands back slugs that prove nothing about THIS repo's lanes. `git ls-files`
    answers from the index, which is the question actually being asked, and `--exclude-standard`
    keeps both of those directories out even when untracked files are included.

    Tracked, not merely present, also buys the durable half (F17): a LANDED lane's branch is
    pruned within the day, but its manifest is committed forever. Scoping this to the current
    lane's own manifest - the first sketch - would have made every landed lane's record read as
    a fork the moment a second lane joined the ticket.

    `include_new` adds untracked-but-not-ignored manifests, and ONLY `lane_slug_here` may ask
    for it. The difference is what anchors the answer: that function intersects the manifests
    with the branch you are standing on, so a manifest git has not seen yet can only ever name
    YOUR lane - and /smh-quick-fix writes its `task.yaml` in the same breath as the Dev Record,
    so demanding a commit first would make the default useless exactly where it is needed. The
    fork verdict has no such anchor, so it trusts nothing git is not tracking."""
    spec = ["ls-files", "-z", "--exclude-standard"]
    if include_new:
        spec += ["--cached", "--others"]
    r = wf.git(spec + ["--", "*task.yaml"], repo)
    if r.returncode != 0:
        return []
    out: list[str] = []
    for rel in (r.stdout or "").split("\0"):
        if not rel.endswith("task.yaml"):
            continue
        m = _MANIFEST_BRANCH_RE.search(wf.read_text(repo / rel))
        if m:
            out.append(m.group(1).strip())
    return out


def ref_lane_slugs(repo: Path) -> list[str]:
    """Lane slugs from refs - local heads AND `origin/`, and both arms are load-bearing.

    A lane that has not landed yet may have only a local branch (its manifest is committed on
    the first push, not before). A lane that HAS landed usually has only its `origin/` ref, the
    local one having been pruned by the close-out. Drop either arm and a real lane reads as a
    fork.

    Only a PREFIXED name counts - `chore/<KEY>-<slug>`, `epic/...`, `story/...`. `main` is not a
    lane, and `origin/main` must not contribute the slug `main`: `main-write-gate` was one half
    of the live AVCH-59 fork, and a check that accepted bare trunk tails would be one careless
    branch name away from clearing it."""
    r = wf.git(["for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes"], repo)
    if r.returncode != 0:
        return []
    slugs: list[str] = []
    for ref in (r.stdout or "").splitlines():
        ref = ref.strip()
        if ref.startswith("refs/heads/"):
            name = ref[len("refs/heads/"):]
        elif ref.startswith("refs/remotes/"):
            rest = ref[len("refs/remotes/"):]
            name = rest.split("/", 1)[1] if "/" in rest else ""
        else:
            continue
        if "/" in name:
            slugs.append(name.rsplit("/", 1)[-1])
    return slugs


def lane_slugs(repo: Path) -> set[str] | None:
    """Every lane slug this repo can prove, normalised - or None when it CANNOT answer.

    ⛔ None is not the empty set, and a caller that conflates them has rebuilt the defect. "No
    lane exists" is a verdict; "this is not a git checkout" is a missing instrument. Blessing a
    pair of Dev Records because the evidence could not be READ is the same silence SCC-174
    exists to end, wearing a different coat."""
    if wf.git(["rev-parse", "--is-inside-work-tree"], repo).returncode != 0:
        return None
    slugs = [b.rsplit("/", 1)[-1] for b in manifest_branches(repo)]
    return {wf.norm_id(s) for s in slugs + ref_lane_slugs(repo) if s}


def lane_slug_here(repo: Path) -> str:
    """The branch slug of the lane you are STANDING ON - if a tracked manifest declares it.

    Both conditions are required and neither is sufficient. The branch alone is not a lane
    (`main` is a branch; so is a stray local experiment), and the manifests alone cannot say
    which of sixty lanes is yours. Their intersection is unambiguous, and it is the ONE slug
    source F3 settles on: the same string `check` will later look for."""
    r = wf.git(["rev-parse", "--abbrev-ref", "HEAD"], repo)
    branch = (r.stdout or "").strip()
    if r.returncode != 0 or "/" not in branch:
        return ""
    declared = manifest_branches(repo, include_new=True)
    return branch.rsplit("/", 1)[-1] if branch in declared else ""


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


_BMAD_NUM_RE = re.compile(r"^\d+\.\d")
# Debug stories are ordinary BMAD stories - story file, board row, the full dev loop - they
# just fix rather than build. Their ids carry the marker (`debug-1.1-toaster-safe-area`,
# `debug-4.1-hr-date-fixes`) but no dotted number of their own, so they need their own signal.
_DEBUG_RE = re.compile(r"^debug[-.]", re.IGNORECASE)


def work_type(head: str, has_story_file: bool) -> str:
    """The ONE type rule, in one place (operator ruling 2026-08-08). See .agents/rules/jira.md.

    `head` is the leading token of a story id or a ticket summary - `19.2`, `debug-1.1`,
    `Separate the front end`. The parent is NEVER the tell: everything is parented, and BMAD
    epics are indistinguishable in Jira from the operator's grouping epics.

      Story - BMAD sprint work, debug stories included
      Task  - workflow / IDE / rules / skills work, filed under a grouping epic
      Epic  - a container; never computed here

    THREE signals feed Story, because no one of them survives the real board alone: the NUMBER
    (`19.2`) is true before the story file exists - backfilled rows are minted from `epics.md`
    long before (1) picks them up; the DEBUG marker carries ids with no dotted number of their
    own; the FILE catches the rest (`tea-16-...`).

    **`Bug` is never computed here, and never corrected in bulk.** It is TEMPORARY: a Story or
    a Task found to be broken wears `Bug` until the fix lands. It is the same ticket, flagged -
    so it looks to every rule here like a mistype, and "correcting" it mid-flight would erase
    the only signal that the work is broken. Exactly one thing clears it: `devrecord --closing`
    at close-out, which restores whatever THIS function says the ticket is.
    """
    if _DEBUG_RE.match(head) or _BMAD_NUM_RE.match(head) or has_story_file:
        return "Story"
    return "Task"


def issue_type(args, story_file: Path | None) -> str:
    """Story vs Task turns on WHETHER THIS IS BMAD SPRINT WORK - never on having a parent
    (operator ruling 2026-08-08).

    Every ticket on this board gets an epic parent, so the parent cannot be the tell. Two
    kinds of epic exist and they are indistinguishable in Jira:

      * a **BMAD epic** (`Epic 19 - ADK 2.x Runtime Upgrade`) has an entry in the project's
        `epics.md` and rows on `sprint-status.yaml`; its children carry BMAD numbers (`19.1`,
        `12.3.4`) and become story files -> **Story**;
      * a **grouping epic** (`CI/CD Improvment`, `New Epic Feature or Fix`) is an umbrella the
        operator keeps so workflow / IDE / rules / skills work is filed somewhere instead of
        floating loose. Jira offers no other container for it. Its children are **Tasks**.

    TWO signals, EITHER of which makes it a Story, because neither alone is sufficient:

      * a **BMAD number** on the id/summary (`19.2`) - true even before the story file is
        written. Backfilled board rows are minted from `epics.md` long before ① picks them up,
        and typing those Task said 19.2 was toolkit work when it is a planned sprint story;
      * a **story file** in `_bmad/bmm/stories/` - which catches the ids that carry no dotted
        number at all (`tea-16-...`), and those are real stories too.

    Neither signal alone survives contact with the real board, which is exactly how the first
    two cuts of this function were wrong. `--type` overrides for anything else (a Bug, an
    operator reclassification).
    """
    if args.type:
        return args.type
    want = work_type((args.story or "").strip(), story_file is not None)
    # `work_type` returns only Story or Task, so this is the Story arm - Bug never reaches it.
    if want == "Story" and args.epic_key is None:
        warn("this story has no --epic-key: BMAD sprint work belongs under its BMAD epic. "
             "Pass --epic-key, or type it explicitly with --type.")
    return want


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
        say(f"jira-feed: DRY RUN - would mint {issue_type(args, story_file)} '{summary}' "
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
                      "--type", issue_type(args, story_file), "--summary", summary,
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

    # ── SCC-174 F3 · ONE slug source, and the lane already wrote it down ──────
    # `devrecord` decides update-vs-create from the SLUG, never from --key, so a free-text
    # slug is a fork waiting to happen. It happened on AVCH-59 (2026-08-15): /smh-quick-dev
    # filed under `main-write-gate`, the close-out passed `avch-59-main-write-gate` - the
    # BRANCH slug, which is what the ceremony's own text literally asks for - and the ticket
    # ended up carrying two records that `check` then blessed as "two lanes".
    #
    # The manifest on the branch you are standing on already knows the answer, so read it
    # instead of asking. Silence when there is no manifest for this branch is deliberate: a
    # BMAD story lane passes `--story 12.3.4`, which matches no manifest and never should,
    # and warning there would put a false alarm on every story close-out in the system.
    lane = lane_slug_here(project)
    if not args.story:
        if not lane:
            wf.die("devrecord needs --story: no task.yaml declares the branch you are on, "
                   "so there is no manifest to read the lane slug from")
        args.story = lane
        say(f"jira-feed: --story defaults to `{lane}` - this lane's task.yaml branch slug")
    elif lane and wf.norm_id(args.story) != wf.norm_id(lane):
        warn(f"--story '{args.story}' is not this lane's slug: the tracked task.yaml for the "
             f"branch you are on says `{lane}`. Filing under a second slug POSTS A SECOND "
             f"record instead of updating this lane's, and `check` will call it a fork "
             f"(SCC-174). Pass `{lane}` unless you really are opening another lane's record.")

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

    if args.closing:
        # The other half of the `Bug` rule. A `Bug` is a TEMPORARY flag on a broken ticket,
        # raised two ways: an audit that traced a live bug back to the ticket that introduced
        # it, or the operator by hand. Either way, when the fix lands THE BUG IS GONE and the
        # ticket goes back to being what it always was. Close-out is the only moment anything
        # can know that - a bulk audit cannot tell "still broken" from "fixed", which is why
        # it leaves Bugs alone.
        have = ((view_fields(binary, args.key).get("issuetype") or {}).get("name") or "").strip()
        if have == "Bug":
            # Restore to whatever the RULE says this ticket is - Story OR Task. Restoring only
            # to Story (the shape shipped in SCC-49) stranded every flagged Task as a permanent
            # Bug: it hit a "does not look like BMAD sprint work" warning and nothing else ever
            # cleared it. A Task can be found broken exactly as easily as a Story.
            want = work_type((args.story or "").strip(),
                             bool(wf.find_story_files(project, args.story)))
            r = acli(binary, ["jira", "workitem", "edit", "--key", args.key,
                              "--type", want, "--yes"])
            landed = ((view_fields(binary, args.key).get("issuetype") or {})
                      .get("name") or "").strip()
            if r.returncode != 0 or landed != want:
                say(f"jira-feed: {args.key} Bug -> {want} FAILED (still {landed or '?'}) "
                    f"{(r.stderr or r.stdout).strip()[:160]}")
                return 2
            say(f"jira-feed: {args.key} Bug -> {want} (the fix landed, the bug is gone)")
    return 0


# A subtask's own status vs its parent's. Only these two ranks mean "not started yet" -
# `Blocking`, `In Review` and `Deferred` all carry real state that a lag report would
# misread as neglect.
_STARTED = ("in progress", "in review", "done")
_NOT_STARTED = ("to do", "to do next")


def check_subtask(binary: str, key: str, summary: str, rep: "wf.Report") -> bool:
    """Subtask PLACEMENT invariants (SCC-119). True = something is wrong.

    `work_type()` is deliberately not run on a subtask: it answers Story-or-Task from a
    SUMMARY, and a subtask is not a third answer to that question. What makes a ticket a
    subtask is its parent's type - Jira's own hierarchy (Epic=1, Story/Task=0, Subtask=-1) -
    which is a board read, not a string test. That is why the old pass skipping every subtask
    as "a container" was wrong twice: a subtask is a LEAF, and skipping meant nothing ever
    checked the three things that actually rot on a parented board.

    ⛔ One `view` per subtask, and it cannot be folded into the bulk search: `parent` is
    REJECTED as a `--fields` value on `search` (the real acli exits 1), while `view` returns
    it complete with the parent's own type and status. One call answers every check here.
    """
    fields = view_fields(binary, key, strict=False)
    if fields is None:
        # Transport, not a verdict - and reported rather than swallowed, because "I could not
        # look" must never read the same as "I looked and it was fine".
        rep.warn("subtask", f"{key}: could not be read back - placement UNCHECKED")
        return True

    parent = fields.get("parent") or {}
    pkey = parent.get("key")
    if not pkey:
        rep.warn("subtask", f"{key}: Subtask with no parent - nothing owns this work, and no "
                            f"close-out can reach it ({summary[:40]})")
        return True

    pfields = parent.get("fields") or {}
    ptype = ((pfields.get("issuetype") or {}).get("name") or "").strip()
    pstatus = ((pfields.get("status") or {}).get("name") or "").strip()

    if ptype == "Epic":
        rep.warn("subtask", f"{key}: parented to {pkey}, which is an Epic - a Subtask sits "
                            f"under a Story or Task, never directly under an Epic")
        return True
    if ptype in ("Subtask", "Sub-task"):
        rep.warn("subtask", f"{key}: nested under {pkey}, itself a {ptype} - hierarchyLevel "
                            f"-1 is the floor. Promote it to a Task, or keep the breakdown "
                            f"as a checklist inside {pkey}")
        return True
    if ptype not in ("Story", "Task", "Bug"):
        rep.warn("subtask", f"{key}: parent {pkey} reads as type '{ptype or '?'}' - refusing "
                            f"to judge a placement this rule does not know")
        return True

    # ⭐ The replacement for the parent cascade that SCC-119 cut out of `start`. The board
    # still gets told when a parent lags its children - it is told by this pass, which
    # REPORTS, instead of by a write verb that would have needed a second board call and a
    # second verdict on the one path post-commit's marker logic depends on.
    cstatus = ((fields.get("status") or {}).get("name") or "").strip()
    if cstatus.lower() in _STARTED and pstatus.lower() in _NOT_STARTED:
        rep.warn("subtask", f"{pkey}: parent is behind its children - {key} is already "
                            f"{cstatus} while {pkey} is still {pstatus}")
        return True

    rep.info("subtask", f"{key}: under {pkey} ({ptype}) OK")
    return False


def cmd_audit(args) -> int:
    """Does every ticket's TYPE agree with what the work actually is?

    Nobody noticed the whole board was `Task` - including 21 real sprint stories - because a
    wrong type is invisible until you go looking. This is the going-looking, and `--apply`
    is the migration: idempotent, re-runnable, and it reads each ticket back.
    """
    project = resolve_root(args.project, need_board=False)
    binary = acli_bin(args.acli)
    found = acli_json(binary, ["jira", "workitem", "search", "--json", "--limit", "200",
                               # NOT `parent`: acli rejects it on search ("field 'parent' is
                               # not allowed") - and the parent was never the discriminator.
                               "--fields", "key,issuetype,summary",
                               "--jql", f"project = {args.jira_project} ORDER BY key"])
    items = as_items(found, "issues")
    if not items:
        wf.die(f"no work items read for project {args.jira_project}")

    rep = wf.Report()
    wrong: list[tuple[str, str, str]] = []
    sub_problems: list[str] = []
    for item in items:
        fields = item.get("fields") or {}
        key = item.get("key") or ""
        have = ((fields.get("issuetype") or {}).get("name") or "").strip()
        summary = field_text(fields.get("summary"))
        if have == "Epic":
            continue  # a container - the type rule has nothing to say about it
        if have in ("Subtask", "Sub-task"):
            # NOT skipped any more (SCC-119). A subtask is a leaf, and its own set of things
            # that can be wrong is placement, not type - checked one `view` at a time.
            if check_subtask(binary, key, summary, rep):
                sub_problems.append(key)
            continue
        if have == "Bug":
            # HANDS OFF - and this is the one skip that matters. `Bug` is TEMPORARY: a Story or
            # Task found broken wears it until the fix lands. It carries the same number and the
            # same story file as before, so every rule here reads it as a mistype and the
            # "helpful" fix would erase the only signal that the work is broken. This pass
            # cannot tell "still broken" from "fixed" - only close-out can, which is why
            # `devrecord --closing` is the one thing that clears it.
            rep.info("type", f"{key}: Bug - a flag on broken work, left for close-out to clear")
            continue
        head = summary.split()[0] if summary else ""
        has_file = bool(head and wf.find_story_files(project, head))
        want = work_type(head, has_file)
        if have == want:
            rep.info("type", f"{key}: {have} OK")
        else:
            why = ("debug story" if _DEBUG_RE.match(head) else
                   "BMAD number" if _BMAD_NUM_RE.match(head) else
                   "story file" if has_file else "no BMAD work")
            wrong.append((key, have, want))
            rep.warn("type", f"{key}: {have} -> {want} ({why}) - {summary[:52]}")

    # print_human moved OUT of the branches (SCC-119): the --apply path never printed the
    # report, so subtask placement findings would have been invisible on exactly the run an
    # operator makes when they intend to fix the board.
    rep.print_human(f"jira-feed audit {args.jira_project}")
    if sub_problems:
        # ⛔ Never auto-fixed, and not for lack of nerve: re-parenting is a board MOVE, not a
        # type edit, and WHICH parent a stray subtask belongs under is a judgment about the
        # work - guardrail 2, placement stays the operator's.
        say(f"jira-feed: {len(sub_problems)} subtask placement problem(s) - "
            f"{', '.join(sub_problems)}. NOT auto-fixable: re-parenting is a board move and "
            f"the right parent is the operator's call.")
    if not wrong:
        if not sub_problems:
            say(f"jira-feed: every type agrees with the rule ({len(items)} items)")
            return 0
        return 1
    if not args.apply:
        say(f"jira-feed: DRY RUN - {len(wrong)} ticket(s) mistyped; re-run with --apply")
        return 1

    failed = []
    for key, have, want in wrong:
        r = acli(binary, ["jira", "workitem", "edit", "--key", key, "--type", want, "--yes"])
        landed = ((view_fields(binary, key).get("issuetype") or {}).get("name") or "").strip()
        if r.returncode != 0 or landed != want:
            failed.append(key)
            say(f"jira-feed: {key} {have} -> {want} FAILED (now {landed or '?'}) "
                f"{(r.stderr or r.stdout).strip()[:160]}")
        else:
            say(f"jira-feed: {key} {have} -> {want}")
    say(f"jira-feed: converted {len(wrong) - len(failed)}/{len(wrong)}"
        + (f"; FAILED: {', '.join(failed)}" if failed else ""))
    if failed:
        return 2
    # A clean conversion run still exits 1 when a subtask is misplaced: --apply fixed the
    # types it can fix, and reporting 0 would say "the board is now correct" over a board
    # that still has work hanging off nothing.
    return 1 if sub_problems else 0


# ── The raise path: a live bug -> the ticket that introduced it (SCC-54) ───────

_KEY_RE = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")
_CONF_RE = re.compile(r'^\s*JIRA_KEYS\s*=\s*"?([^"#\n]*)"?', re.MULTILINE)
_LINE_SPEC_RE = re.compile(r"^(.*):(\d+)$")


def conf_projects(repo: Path) -> list[str]:
    """The project key(s) THIS repo answers to, from `.agents/jira.conf`.

    The same file the armed commit-msg hook reads. Without it every `ABC-1`-shaped token in a
    commit subject becomes a candidate ticket - and prose says things like "unlike AVCH-13"
    all the time. With it, a trace inside the lobby can only ever propose `SCC` tickets."""
    text = wf.read_text(repo / ".agents" / "jira.conf")
    m = _CONF_RE.search(text)
    return [k for k in (m.group(1).replace(",", " ").split() if m else []) if k]


def keys_in(subject: str, projects: list[str]) -> list[str]:
    hits = _KEY_RE.findall(subject or "")
    if not projects:
        return hits
    return [k for k in hits if k.split("-")[0] in projects]


def commit_meta(repo: Path, sha: str) -> tuple[str, str]:
    r = wf.git(["log", "-1", "--format=%s%x00%aI", sha], repo)
    parts = (r.stdout or "").strip().split("\0")
    return (parts[0] if parts else ""), (parts[1] if len(parts) > 1 else "")


def trace_paths(repo: Path, specs: list[str], depth: int) -> tuple[dict, list[str]]:
    """Which ticket last touched this code? Evidence only - this NEVER writes.

    Two signals, and they are not equal. `git blame` on an exact line names the commit that
    wrote THAT line, which is as close to "who introduced it" as git can get. `git log` on the
    file only says the ticket worked in the neighbourhood. Both are reported; blame ranks first.

    `--no-merges` on the log pass: a `--no-ff` merge subject carries the branch's key too, so
    counting it double-weights whichever ticket merged most recently for no added information.

    None of this proves authorship of a BUG. The line that shows a symptom is often not the
    line that broke it, and a later unrelated edit takes the blame outright. That is exactly
    why this prints and stops - `flag` will not take a key from here, only from a human."""
    projects = conf_projects(repo)
    cand: dict[str, dict] = {}
    notes: list[str] = []

    def bump(key: str, kind: str, why: str, when: str) -> None:
        c = cand.setdefault(key, {"hits": 0, "blame": False, "why": [], "when": ""})
        c["hits"] += 1
        c["blame"] = c["blame"] or kind == "blame"
        c["why"].append(why)
        c["when"] = max(c["when"], when)

    for spec in specs:
        m = _LINE_SPEC_RE.match(spec)
        rel, line = (m.group(1), int(m.group(2))) if m else (spec, None)
        if not (repo / rel).is_file():
            notes.append(f"{rel}: not a file in this repo - skipped "
                         f"(a path that does not exist cannot be blamed)")
            continue
        if line:
            r = wf.git(["blame", "-L", f"{line},{line}", "--porcelain", "--", rel], repo)
            sha = (r.stdout or "").split(" ")[0].strip()
            if r.returncode == 0 and re.fullmatch(r"[0-9a-f]{7,40}", sha):
                subject, when = commit_meta(repo, sha)
                found = keys_in(subject, projects)
                for key in found:
                    bump(key, "blame", f"blame {rel}:{line} -> {sha[:8]} {subject[:60]}", when)
                if not found:
                    notes.append(f"{rel}:{line} blames {sha[:8]} whose subject carries no "
                                 f"{'/'.join(projects) or 'project'} key: {subject[:60]}")
            else:
                notes.append(f"{rel}:{line} could not be blamed (line out of range?)")

        r = wf.git(["log", "--no-merges", "-n", str(depth), "--format=%H%x00%s%x00%aI",
                    "--", rel], repo)
        for row in (r.stdout or "").splitlines():
            parts = row.split("\0")
            if len(parts) < 3:
                continue
            for key in keys_in(parts[1], projects):
                bump(key, "log", f"log  {rel} <- {parts[0][:8]} {parts[1][:60]}", parts[2])

    return cand, notes


def cmd_trace(args) -> int:
    """Propose the ticket(s) behind a set of paths. Read-only, no network, no board write."""
    repo = resolve_root(args.project, need_board=False)
    if not (repo / ".git").exists():
        wf.die(f"{repo} is not a git checkout - there is no history to trace")
    cand, notes = trace_paths(repo, args.path, args.depth)
    ranked = sorted(cand.items(),
                    key=lambda kv: (kv[1]["blame"], kv[1]["hits"], kv[1]["when"]),
                    reverse=True)

    if args.json:
        say(json.dumps({"repo": str(repo), "candidates": [
            {"key": k, "hits": v["hits"], "blame": v["blame"], "last": v["when"],
             "why": v["why"][:6]} for k, v in ranked], "notes": notes}, indent=2))
        return 0 if ranked else 1

    rep = wf.Report()
    for n in notes:
        rep.warn("trace", n)
    for key, v in ranked:
        how = "blame + log" if v["blame"] else "log only"
        rep.info("trace", f"{key}  {v['hits']} hit(s), {how}, last {v['when'][:10]}")
        for why in v["why"][:4]:
            rep.info("trace", f"    {why}")
    rep.print_human(f"jira-feed trace ({len(args.path)} path(s))")
    if not ranked:
        say("jira-feed: no ticket proposed - no commit touching these paths carries a "
            "project key. Flag by hand if you know the ticket.")
        return 1
    say(f"jira-feed: {len(ranked)} candidate(s), best first. THIS IS A PROPOSAL - the last "
        f"ticket to touch a line is not always the one that broke it.")
    say(f"jira-feed: confirm with a human, then: jira_feed.py flag --key {ranked[0][0]} "
        f"--reason \"...\" --apply")
    return 0


# The statuses a ticket can legitimately be STARTED from. Deliberately narrow, exactly like
# `flag`'s "only out of Done": a verb that moves from anywhere erases real state. `Blocking` is
# an impediment, `In Review` is finished work waiting on a human, `Deferred` is descoped - and
# starting any of them destroys the only signal each one carries. A board that lacks one of
# these simply never matches it (per-board-optional, like every other rule in jira.md).
STARTABLE = ("to do", "to do next")


def cmd_start(args) -> int:
    """Work has started: move a ticket to `In Progress` (SCC-113).

    The seam that did not exist. Four wrote `Done` and one wrote `In Progress` - the BMAD
    story lane - so on a board whose every non-epic ticket is a Task, nothing was ever
    visible in flight. This is a verb rather than a prose step for the reason SCC-49 gave
    for the other four: prose could not hold the failure mode. The prose one never ran.

    Idempotent on purpose. The post-commit recorder fires on every commit and two lanes can
    hold one key, so a second call must make no second transition.

    ⭐ THREE outcomes, three exit codes, because the caller has to tell them apart:
        0  moved, or already there        -> settled; the hook may stop asking
        3  LEFT ALONE (see STARTABLE)     -> not settled; the hook must ASK AGAIN later
        2  refused or the move failed     -> not settled either
    Collapsing 3 into 0 is a real defect, not a nicety: a lane opened while its ticket sat
    in `Blocking` wrote the hook's marker, and when the blocker cleared and the ticket went
    back to `To Do` nothing ever asked again - the ticket stayed there for the whole build,
    which is precisely the failure SCC-113 exists to close.
    """
    binary = acli_bin(args.acli)
    fields = view_fields(binary, args.key, timeout=args.timeout, strict=False)
    if fields is None:
        say(f"jira-feed: could not reach the board to read {args.key} - nothing was "
            f"changed. This is a TRANSPORT failure, not a verdict on the ticket: retry "
            f"when you have a connection. (If it persists: `acli jira auth status`.)")
        return 4
    # No `issuetype` read here any more: with the Subtask refusal gone (SCC-119) and an Epic
    # already allowed, `start` gates on STATUS alone - every type this repo's branches can
    # carry is startable. It stays on view_fields' whitelist for the callers that do read it.
    status = ((fields.get("status") or {}).get("name") or "").strip()
    summary = field_text(fields.get("summary"))
    target = args.status

    # ⭐ A Subtask IS allowed (SCC-119). It used to be refused here - "start the parent it
    # belongs to" - and that refusal was a live defect, not a guard: a subtask carries its
    # own `chore/<KEY>-<slug>` branch and ships code exactly like a Task, so the refusal
    # exited 2 on a real lane. `post-commit-jira-start.sh` writes its once-per-branch marker
    # ONLY on exit 0, so the lane never marked, re-fired a board round-trip on EVERY commit
    # with both streams swallowed, and its ticket sat in `To Do` for the whole build - the
    # precise failure SCC-113 exists to close, coming back through a type check. SCC-123
    # shipped that way. There is deliberately NO parent cascade: one board write, one
    # verdict, because the marker logic hangs off there being exactly one. A parent that
    # lags its children is reported by `audit`, which reports rather than writes.
    #
    # An Epic is allowed too, and that is where `start` differs from `flag`, which refuses
    # containers outright. An epic under active development is genuinely in progress; an
    # epic is never itself broken work. `epic/` is in the branch scope.

    if status.lower() == target.lower():
        say(f"jira-feed: {args.key} is already {target} - nothing to do ({summary[:60]})")
        return 0

    if status.lower() == "done":
        # Guardrail 1, in reverse. Borrowing a finished ticket's key because the work is
        # adjacent is how a closed ticket silently accumulates branches - and `devrecord`
        # keeps ONE record per ticket and updates it in place, so a close-out under a
        # borrowed key overwrites the record of the work that earned it.
        say(f"[ERR] {args.key} is Done - that is not your key. A ticket you are starting "
            f"work on cannot already be finished ({summary[:60]}). Mint one at the seam "
            f"in jira.md #Who-mints-tickets; never reuse a closed key.")
        return 2

    if status.lower() not in STARTABLE:
        # Exit 3, NOT 0. This ticket is not settled - it is waiting on something (an
        # impediment, a reviewer, a descope decision). Whatever asked must ask again.
        say(f"jira-feed: {args.key} is {status or '?'} - left alone. `start` only moves a "
            f"ticket out of {' / '.join(STARTABLE)}, so that a status carrying real state "
            f"is never overwritten. Nothing was recorded; ask again later.")
        return 3

    if not args.apply:
        say(f"jira-feed: DRY RUN - would move {args.key} {status} -> {target} "
            f"({summary[:60]})")
        return 0

    # --yes or acli blocks on an interactive confirm no agent shell can answer. This is the
    # trap jira.md:268 names and three call sites shipped without.
    t = acli(binary, ["jira", "workitem", "transition", "--key", args.key,
                      "--status", target, "--yes"], timeout=args.timeout)
    back = view_fields(binary, args.key, timeout=args.timeout, strict=False)
    if back is None:
        # The write may or may not have landed and we cannot see which. NOT settled: no
        # marker, so the next commit re-reads and settles it.
        say(f"jira-feed: {args.key} was sent {status} -> {target}, but the board could not "
            f"be re-read to confirm it. Treating as unconfirmed; it will be retried.")
        return 4
    now = ((back.get("status") or {}).get("name") or "").strip()
    if t.returncode != 0 or now != target:
        say(f"jira-feed: {args.key} is still {now or '?'} - the move did NOT land: "
            f"{(t.stderr or t.stdout).strip()[:160]}")
        return 2
    say(f"jira-feed: {args.key} {status} -> {target}")
    return 0


# ── finish: the close-out's Done, held back by the operator's own actions ──────

# The walkthrough section that carries what the OPERATOR still owes. Fixed by name because
# both close-out commands already require the section, and `artifacts-always-first` fixes
# its position - this reads an artifact that exists rather than inventing a new one.
YOUR_ACTIONS = "## Your Actions"
USER_TASKS_LABEL = "user-tasks"
# The marker `find_user_tasks` matches on, and it lives on the BOARD - a rename here cannot
# be swept, so every comment already posted would go invisible and `finish` would start
# stacking again. Same reasoning as label_tasks.MARKER, and frozen for the same reason.
USER_TASKS_MARKER = "**User tasks**"
# Attempted in order; the first one the board actually has wins. jira.md: a status a board
# does not carry is "not installed yet", never an error - so this falls THROUGH rather than
# failing, and the `user-tasks` label carries the signal on a board with none of them.
#
# `Review Required` leads because the operator installed exactly that column on SCC
# (2026-08-14, this ticket's own `## Your Actions`), which turns the fall-through from the
# LIVE path into the corner case it was always meant to be. The other two stay as fallbacks
# for AVCH and any board that named it differently.
#
# ⛔ The literal is BOARD CONFIGURATION, not a property of this code: get it wrong and the
# ladder silently never fires. `--review-status` overrides the whole ladder, so a rename on
# the board is a flag on one invocation rather than an edit here and a release.
REVIEW_LADDER = ("Review Required", "Awaiting Review", "In Review")
# `(.*?)` not `(.+?)`: an unchecked box with no text after it is still an open obligation.
# Requiring a character silently dropped it - fail-open, one level in from the shape the
# docstring bans (SCC-155 review finding).
_OPEN_ITEM_RE = re.compile(r"^\s*[-*]\s*\[\s\]\s*(.*?)\s*$")
_ANY_ITEM_RE = re.compile(r"^\s*[-*]\s+")
# CommonMark: a fence opens on >=3 backticks or tildes and closes only on the SAME marker
# kind, at least as long. Ported from check_gate.strip_fenced (SCC-154) rather than
# re-derived - that lane paid for the close-marker rule with a live miss.
_FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")


def _unfenced(lines: list[str]):
    """Yield (index, line) for every line OUTSIDE a fenced code block.

    ⛔ SCC-155 review finding (critical). Without this, a walkthrough is read as markup that
    it isn't, in two directions that are both wrong and one that is dangerous:

      - The house convention writes `# PC: run from the lobby root` inside a ```bash block,
        and `## Your Actions` is precisely the section that carries "here is what you still
        have to run". Read line-by-line, that comment looked like a top-level heading and
        ENDED the section - `open_actions` returned `[]`, not `None`, so no refusal fired and
        the ticket closed over work the operator was promised. 26 of the 92 walkthroughs
        already in `_artifacts/` carry that shape.
      - A doc that TEACHES the convention quotes `## Your Actions` inside a fence. The quoted
        example won the heading match, its ticked example rows returned `[]`, and the real
        section below was never read.
      - Mirror direction: a `- [ ]` template row inside a fence is an EXAMPLE, and counting
        it holds a ticket nobody can ever close.

    Same class as the source-grep guards a comment inverts, and the same fix SCC-154 landed
    in `check_gate`: match PROSE, never quoted examples."""
    fence = ""
    for i, ln in enumerate(lines):
        m = _FENCE_RE.match(ln)
        if m:
            mark = m.group(1)
            if not fence:
                fence = mark
                continue
            if mark[0] == fence[0] and len(mark) >= len(fence):
                fence = ""
            continue
        if not fence:
            yield i, ln


def open_actions(text: str) -> list[str] | None:
    """The unchecked `- [ ]` items under `## Your Actions`, or **None if there is no such
    section at all** — which is a REFUSAL upstream, never an empty list.

    Collapsing "no section" into "nothing owed" is the empty-input-reads-as-pass shape that
    `tests-must-gate-for-real` bans, and here it would close a ticket over work the operator
    was promised. A renamed heading is exactly how that happens in practice.

    Scoped to the section: the walkthrough's `## Task Checklist` is full of `- [ ]` lines
    that are the AGENT's, and counting those would hold every ticket forever.

    Fenced blocks are invisible throughout — see `_unfenced` for the three ways that bit."""
    lines = text.splitlines()
    live = list(_unfenced(lines))
    starts = [i for i, ln in live if ln.strip().lower() == YOUR_ACTIONS.lower()]
    if not starts:
        return None
    items: list[str] = []
    # EVERY such section, not just the first. `next(...)` took the first heading only, so a
    # walkthrough that opened a second `## Your Actions` later (a close-out appending its own
    # asks is exactly how) had those items silently dropped and the ticket closed over them
    # (SCC-155 review finding).
    for start in starts:
        _collect(live, start, items)
    return items


def _collect(live: list[tuple[int, str]], start: int, items: list[str]) -> None:
    for i, ln in live:
        if i <= start:
            continue
        # Only a heading of the SAME level or higher ends the section. `###` under it is
        # still the operator's - a close-out that groups its asks under `### Board` must not
        # lose them, so this must never widen to a bare `#` (SCC-155 review finding: the
        # narrowing direction was pinned, this widening one was not).
        s = ln.strip()
        if s.startswith("## ") or s.startswith("# "):
            break
        m = _OPEN_ITEM_RE.match(ln)
        if m:
            items.append(m.group(1).strip())
        elif items and s and not _ANY_ITEM_RE.match(ln) and ln[:1].isspace():
            # A continuation line indented under the item it belongs to. `smh-quick-dev.md`
            # publishes this as a MACHINE CONTRACT ("Continuation lines indented under it
            # ride along"), and dropping them truncated the operator's own instructions to
            # their first line - the half that says WHY reached nobody. It must NOT become a
            # second owed item, so it folds into the item above rather than appending.
            items[-1] += " " + s
    return items


# ── SCC-175: the merge row is COMPUTED, never read off a tick ─────────────────
#
# ⛔ THE DEFECT THIS CLOSES, AND WHY A TICK CANNOT BE THE ANSWER.
#
# A walkthrough's `## Your Actions` almost always carries a row for the merge. Left open,
# `finish` reads it as work still owed and HOLDS a ticket whose only outstanding item is the
# merge that just landed. The old remedy was for the close-out to TICK it — after the merge,
# on `main`, in a commit the main-write gate then refused. That refusal is what produced the
# 2026-08-15 `reset --hard` incident (SCC-180 is its other half).
#
# SCC-183 removed the reason: the door now requires the tick committed on the lane BEFORE the
# PR opens. But a tick is a CLAIM, and `finish --apply` is what writes `Done` to Jira on the
# strength of it — so a box ticked without a merge closes the ticket over an unlanded lane.
# That is self-certification, which house law bans outright.
#
# So the row is not read, it is CHECKED: is the lane's tip an ancestor of `origin/main`?
#
# ⭐ AND IT IS READ FROM `HEAD`, NOT THE WORKING TREE (F18). Reading the file on disk means an
# UNCOMMITTED tick satisfies the check — the exact SCC-169 shape, where the tick was left
# uncommitted in the main checkout and later wiped by a reset. The committed copy is the only
# one that survives the session that wrote it.
MERGE_DOORS = ("/smh-close-task-merge-tree", "/cicd-push-e2e")
MERGE_PHRASE = "the merge itself"

# ⛔ THE RECOGNISER IS DOOR-NAMED-OR-CANONICAL-PHRASE, AND THAT IS FROM THE CORPUS, NOT TASTE.
# Measured over 145 tracked walkthroughs on 2026-08-16: 12 open rows name a door, 7 rows carry
# the canonical phrase SCC-183 mandates — and 5 open rows say "merge" or "land" while naming no
# door, every one of them a REAL operator decision this must never clear:
#
#     - [ ] **Rule the landing order.** Recommended: SCC-126 lands first …
#     - [ ] **Decide whether the CONCERNS is worth clearing before the merge.**
#     - [ ] **Follow-on ticket decision (C1/C3 + deferred tests)** …
#
# A bare merge/land keyword would clear all three. So the row must either invoke a DOOR — an
# act only this ceremony performs — or use the one phrase the door itself now writes.
_ANY_ROW_RE = re.compile(r"^\s*-\s*\[([ xX])\]\s*(.+?)\s*$")


def is_merge_row(item: str) -> bool:
    low = item.lower()
    return any(d in low for d in MERGE_DOORS) or MERGE_PHRASE in low


def committed_copy(wt: Path) -> tuple[str, str]:
    """`HEAD`'s version of the walkthrough, and where it came from.

    Falls back to the working tree ONLY when git cannot answer at all (the file is not
    committed yet, or this is not a repo) — and says so, so a merge row judged against an
    uncommitted file is never silently treated as equivalent."""
    # ⛔ The cwd must EXIST or subprocess raises rather than returning non-zero. `finish`
    # has already proved the file is there, but this is called directly by tests and by any
    # later caller, and a crash is not a verdict.
    if not wt.parent.is_dir():
        return wf.read_text(wt), "working tree (no directory to ask git from)"
    r = wf.git(["rev-parse", "--show-toplevel"], wt.parent)
    if r.returncode != 0 or not (r.stdout or "").strip():
        return wf.read_text(wt), "working tree (not a git repository)"
    root = Path((r.stdout or "").strip())
    try:
        rel = wt.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return wf.read_text(wt), "working tree (walkthrough is outside the repo)"
    show = wf.git(["show", f"HEAD:{rel}"], root)
    if show.returncode != 0:
        return wf.read_text(wt), "working tree (no committed copy at HEAD yet)"
    return show.stdout or "", "HEAD"


def lane_tip(wt: Path) -> tuple[str | None, list[str]]:
    """The lane's tip sha, and the list of what was tried.

    Order matters and every arm is load-bearing (F6a). A LANDED lane is pruned local and
    remote within the day — `chore/SCC-162-lightweight-lane` and `chore/SCC-163-gate-hardening`
    were both already gone when this was designed — so the manifest branch resolves to nothing
    and only the walkthrough's own `Verdict: … @ <sha>` still names the tip. Both of those
    lanes' verdict shas are ancestors of `origin/main`; verified 2026-08-16."""
    tried: list[str] = []
    if not wt.parent.is_dir():
        return None, ["no directory to ask git from"]
    r = wf.git(["rev-parse", "--show-toplevel"], wt.parent)
    if r.returncode != 0:
        return None, ["not a git repository"]
    root = Path((r.stdout or "").strip())

    manifest = wt.parent / "task.yaml"
    branch = ""
    if manifest.is_file():
        m = _MANIFEST_BRANCH_RE.search(wf.read_text(manifest))
        branch = m.group(1).strip() if m else ""
    if branch:
        for ref in (f"refs/heads/{branch}", f"refs/remotes/origin/{branch}"):
            got = wf.git(["rev-parse", "--verify", "--quiet", ref], root)
            tried.append(ref)
            if got.returncode == 0 and (got.stdout or "").strip():
                return (got.stdout or "").strip(), tried
    else:
        tried.append("task.yaml `branch:` (absent)")

    # The pruned-lane fallback. Read from the COMMITTED copy for the same reason as the row.
    text, _src = committed_copy(wt)
    m = _VERDICT_RE.search(text)
    tried.append("walkthrough `Verdict: … @ <sha>`")
    if m and m.group(2):
        got = wf.git(["rev-parse", "--verify", "--quiet", m.group(2)], root)
        if got.returncode == 0 and (got.stdout or "").strip():
            return (got.stdout or "").strip(), tried
    return None, tried


def merge_row_state(wt: Path) -> dict | None:
    """None when the walkthrough has no merge row at all. Otherwise the verdict and why.

    ⛔ Rows are taken from `HEAD`'s copy and BOTH `- [ ]` and `- [x]` count. A ticked row is
    still a claim about a merge, and this is the thing that checks the claim."""
    text, source = committed_copy(wt)
    lines = list(_unfenced(text.splitlines()))
    starts = [i for i, ln in lines if ln.strip().lower() == YOUR_ACTIONS.lower()]
    row = None
    for start in starts:
        for i, ln in lines:
            if i <= start:
                continue
            s = ln.strip()
            if s.startswith("## ") or s.startswith("# "):
                break
            m = _ANY_ROW_RE.match(ln)
            if m and is_merge_row(m.group(2)):
                row = m.group(2)
                break
        if row:
            break
    if row is None:
        return None

    tip, tried = lane_tip(wt)
    if tip is None:
        return {"row": row, "satisfied": False, "source": source, "tip": None,
                "why": f"the lane tip could not be resolved. Tried: {', '.join(tried)}. "
                       f"An unresolvable tip is not evidence of a merge, so the row HOLDS."}

    root = Path((wf.git(["rev-parse", "--show-toplevel"], wt.parent).stdout or "").strip())
    # Best effort — a stale `origin/main` would answer "not merged" for a lane that IS merged,
    # which holds a ticket that should close. Failure here is not fatal: the ancestry check
    # below still runs against whatever ref this repo has.
    wf.git(["fetch", "origin", "main"], root)
    anc = wf.git(["merge-base", "--is-ancestor", tip, "origin/main"], root)
    if anc.returncode == 0:
        return {"row": row, "satisfied": True, "source": source, "tip": tip,
                "why": f"{tip[:9]} is an ancestor of origin/main"}
    return {"row": row, "satisfied": False, "source": source, "tip": tip,
            "why": f"{tip[:9]} is NOT an ancestor of origin/main - the lane has not landed"}


# ── SCC-163 Part B: what may go in `## Your Actions` ──────────────────────────
#
# Step 5 of /smh-code-review and /cicd-code-review permits the operator to be left exactly
# three things: A PRODUCT DECISION, A MAIN MERGE, A TICKET TRANSITION. A row handing them any
# ticket born from review findings - mint it, file it, "fold into <KEY>", rule on where it
# goes - is the retired defect, and an open box here HOLDS the ticket on the review ladder
# forever (see `finish` below). That was prose until now, and it was broken the same day it
# was written: AVCH-58 shipped three unchecked rows, zero of them operator calls.
#
# ⛔ WHY THIS IS A VERB x OBJECT PAIR AND NOT A PHRASE LIST. The ticket's own phrase list, read
# literally, was measured against every walkthrough in `_artifacts/` BEFORE this was written:
# 101 carry the section, 25 unchecked rows, and the list flags 8 of them - of which at most 4
# are real. "Rule on A1" is an acceptance dispute. "Rule the landing order" is merge
# sequencing. "Decide whether the CONCERNS is worth clearing" is a product decision. All three
# are precisely what Step 5 PERMITS. So a trigger verb alone is never enough: it must land on
# an object that is ticket-shaped work.
# ⛔ THE VERB AND THE OBJECT ARE BOUND AS A PHRASE, NOT SEARCHED INDEPENDENTLY, and that is a
# review finding rather than a first draft. Two independent searches over the same row - a verb
# anywhere, an object anywhere - flagged four honest rows in an adversarial probe:
#
#     "The SCC-99 ticket is still open from last sprint"   'open' + 'ticket'
#     "Ticket SCC-12 remains open; nothing owed here"      'open' + 'ticket'
#     "Open the ticket and read the Dev Record"            'open' + 'ticket'  <- an INSTRUCTION
#     "The task file is in _artifacts/"                    'file' + 'task'    <- both are NOUNS
#
# `file` and `open` are among the most common non-verbs in this vocabulary, and co-occurrence
# cannot tell "open a ticket" (create) from "open the ticket" (go read it). Binding them into
# one pattern is also the more faithful reading of acceptance B3's "VERB+OBJECT pair".
#
# ⓘ `open` is dropped from the creation verbs outright. It is in the ticket's phrase list, but
# no row in the 25-row live corpus uses "open a ticket", and the article that would separate
# creation from reference ("a" vs "the") is not reliable: "File THE follow-on Task" is creation
# and "Open THE ticket" is not. Dropping the ambiguous verb costs nothing measurable and
# removes three of the four false positives; the fourth dies with the phrase binding.
_BANNED_PATTERNS = [
    # ⓘ `(?:[A-Z]{2,10}\s+)?` is the PROJECT TOKEN, and it was missing until a pinned-shape case
    # went red. AVCH-58's real row says "or mint its own AVCH key" - the key phrase this ticket
    # exists to catch - and without this group the pattern stopped dead at `AVCH`. Row 1 still
    # flagged, which is exactly why it went unnoticed: it ALSO says "board placement", so the
    # known-positive passed while the creation shape it was supposed to prove did not match.
    # All-caps only, so it cannot open a general word gap ("file the report about the ticket").
    (re.compile(r"\b(?:mint|file|create|raise|log)\s+(?:a|an|its\s+own|the|one)?\s*"
                r"(?:new\s+)?(?:follow[-\s]?on\s+)?(?:jira\s+)?(?:[A-Z]{2,10}\s+)?"
                r"(?:ticket|task|subtask|issue|key)\b", re.I),
     "asks the operator to CREATE ticket work"),
    (re.compile(r"\bfold\b[^\n]{0,60}?\binto\s+[A-Z]{2,10}-\d+", re.I),
     "asks the operator to PLACE this work onto another ticket"),
    (re.compile(r"\bboard\s+placement\b", re.I),
     "'board placement' is the retired hand-off, by name"),
    (re.compile(r"\bearns?\s+(?:a|an|its\s+own)\s+(?:ticket|task|key)\b", re.I),
     "asks the operator to rule whether a finding becomes a ticket"),
    (re.compile(r"\b(?:rule\s+on|decide)\b[^\n]{0,80}?\b(?:ticket|subtask|backlog)\b", re.I),
     "asks the operator to rule on ticket placement"),
    (re.compile(r"\bticket\b[^\n]{0,40}?\byour\s+call\b", re.I),
     "hands a ticket decision to the operator"),
]
# ⛔ DELIBERATELY NOT DETECTED: a row that is a STATUS NOTE rather than an imperative -
# AVCH-58's rows 2 and 3 ("X remains AVCH-55's, still correctly deferred", "your local main is
# behind origin/main"). Both are real defects: neither is an action. But they are not reliably
# machine-detectable, they read exactly like the context prose that legitimately surrounds an
# owed item, and a detector that guesses at them false-reds honest walkthroughs. Acceptance B5
# scopes Part B to row 1's class only. Widening this is a decision, not a tidy-up.


def banned_action_rows(text: str) -> list[tuple[str, str]]:
    """The `## Your Actions` rows that hand the operator ticket work. `(row, reason)` each.

    Reads the same rows `open_actions` does - through `_unfenced`, so a `- [ ]` template
    quoted inside a ``` block stays documentation (SCC-154 paid for that close-marker rule
    with a live miss; it is reused here, never re-derived)."""
    rows = open_actions(text)
    if not rows:
        return []
    out: list[tuple[str, str]] = []
    for row in rows:
        for pat, why in _BANNED_PATTERNS:
            m = pat.search(row)
            if m:
                out.append((row, f"{why} (matched: '{m.group(0).strip()[:60]}')"))
                break          # one reason per row; the first match is the clearest one
    return out


def render_banned_banner(rows: list[tuple[str, str]], walkthrough: str) -> str:
    """The banner. ⛔ It is LOUD ON PURPOSE and it is pinned by a test.

    The ruling (2026-08-15, "1. yes") is that this ships WARN: a block at `finish` fires AFTER
    the merge, so it would trade a held ticket for an erroring close-out. But a warn nobody
    reads is the `vscode-hides-git-hook-output` failure - a warn-only gate reads as clean
    success - so the fix is volume and a named remedy, not a quieter conscience."""
    n = len(rows)
    lines = ["", "  " + "=" * 74,
             f"  ⛔ BANNED ACTION ROW{'' if n == 1 else 'S'} - {n} row{'' if n == 1 else 's'} "
             f"in `{YOUR_ACTIONS}` hand{'s' if n == 1 else ''} the operator ticket work",
             "  " + "=" * 74, ""]
    for row, reason in rows:
        lines += [f"    - {row[:160]}", f"      why: {reason}", ""]
    lines += [
        "  Step 5 leaves the operator THREE things: a product decision, a main merge, a",
        "  ticket transition. A ticket born from review findings is not one of them - and an",
        "  open box here holds this ticket on the review ladder until someone edits the file.",
        "",
        f"  Fix the walkthrough ({walkthrough}), do not hand the row over:",
        "    - the finding is evidenced and in YOUR lane -> file it yourself, or fix it here",
        "    - it is genuinely the operator's -> say which of the three classes it is",
        "",
        "  This is a WARNING. The ticket's hold below is unchanged. `--strict-actions` makes",
        "  it a refusal.", ""]
    return "\n".join(lines)


def render_user_tasks(items: list[str], walkthrough: str, when: str) -> str:
    lines = [f"**User tasks** - {when}", "",
             f"This ticket's work is merged, but the walkthrough leaves "
             f"**{len(items)}** thing{'' if len(items) == 1 else 's'} that only you can do. "
             f"It is deliberately NOT `Done`:", ""]
    lines += [f"- [ ] {it}" for it in items]
    lines += ["", f"Source: `{walkthrough}` -> `{YOUR_ACTIONS}`.", "",
              "Tick an item off in the walkthrough (`- [x]`), commit that, and re-run "
              "`jira_feed.py finish` - when the section has no open items left it closes "
              "the ticket. There is no force flag, on purpose."]
    return "\n".join(lines) + "\n"


def cmd_check_actions(args) -> int:
    """`## Your Actions` inspected on its own - no board, no key, no network.

    Exit 1 on hits rather than 2: this is a report, and 2 in this script means THE ARTIFACT IS
    WRONG (`cmd_finish`'s contract). A missing section is not this command's business - that is
    `finish`'s refusal, and duplicating it here would give the same defect two different exit
    codes depending on which entry point found it."""
    wt = Path(args.walkthrough)
    if not wt.is_file():
        say(f"[ERR] no walkthrough at `{wt}`")
        return 2
    rows = banned_action_rows(wf.read_text(wt))
    if not rows:
        say(f"jira-feed: `{wt}` - no banned action rows.")
        return 0
    say(render_banned_banner(rows, str(wt)))
    return 1


def cmd_finish(args) -> int:
    """Close the ticket - UNLESS the walkthrough still owes the operator something (SCC-155).

    Every close-out wrote `Done` unconditionally, so an operator action recorded in the
    walkthrough ("install the board column", "run the memory audit") landed on a ticket
    nobody would open again. The record of what was still owed died with the lane.

    FOUR outcomes, four exit codes, because the caller reports different things:
        0  closed (or already Done)          -> the close-out says "closed"
        3  HELD: open user tasks, posted     -> the close-out says "awaiting you"
        2  refused (no walkthrough/section)  -> fix the artifact; nothing was written
        4  the board would not take a write  -> transport, not a verdict; retry

    ⛔ SCC-155 review finding: 2 means THE ARTIFACT IS WRONG, and nothing else. It used to
    also cover a transition that would not land and a comment that would not post - both
    board failures, both with a write already attempted. An agent reading the close-out's
    table went hunting for a defect in a walkthrough that was fine, and re-running produced
    the same result forever. Every board failure is 4, whose row already says "retry".
    """
    binary = acli_bin(args.acli)
    wt = Path(args.walkthrough)
    if not wt.is_file():
        say(f"[ERR] {args.key}: no walkthrough at `{wt}` - refusing to close. The close-out "
            f"requires one, and a ticket cannot be certified clean against a file that is "
            f"not there.")
        return 2
    text = wf.read_text(wt)
    items = open_actions(text)
    if items is None:
        say(f"[ERR] {args.key}: `{wt}` has no `{YOUR_ACTIONS}` section - refusing to close. "
            f"An absent section is not evidence that nothing is owed; add the section (even "
            f"empty) so the answer is recorded rather than assumed.")
        return 2

    # ── SCC-175 · the merge row is computed, not read ─────────────────────────────────
    # Runs before anything else looks at `items`, and it moves the count in BOTH directions:
    # a merge that landed stops holding the ticket, and a merge row TICKED without a merge
    # (in the working tree, or by hand) is put back on the list it was taken off.
    merge = merge_row_state(wt)
    if merge is not None:
        was_open = [i for i in items if is_merge_row(i)]
        if merge["satisfied"]:
            items = [i for i in items if not is_merge_row(i)]
            if was_open:
                say(f"jira-feed: {args.key}: the merge row is SATISFIED by the repo, not by a "
                    f"tick - {merge['why']} (row read from {merge['source']}). It no longer "
                    f"holds the ticket; every other open row is untouched.")
        else:
            if not was_open:
                items.append(merge["row"])
                say(f"[WARN] {args.key}: the merge row is TICKED but the merge did not happen "
                    f"- {merge['why']}. Re-opened: a tick is a claim, and this is the check. "
                    f"(row read from {merge['source']})")
            else:
                say(f"jira-feed: {args.key}: the merge row still HOLDS - {merge['why']}.")

    # SCC-163 Part B. Runs BEFORE the board is touched, so a refusal under `--strict-actions`
    # writes nothing at all. Warn-only by the operator's ruling (2026-08-15, "1. yes"): the
    # rows below still count as owed exactly as they did, and the hold is unchanged - what is
    # added is that the close-out now SAYS the row should not have been handed over.
    banned = banned_action_rows(text)
    if banned:
        say(render_banned_banner(banned, str(wt)))
        if args.strict_actions:
            say(f"[ERR] {args.key}: refusing on {len(banned)} banned action row(s) "
                f"(--strict-actions). Nothing was written; fix the walkthrough.")
            return 2

    fields = view_fields(binary, args.key, timeout=args.timeout, strict=False)
    if fields is None:
        say(f"jira-feed: could not reach the board to read {args.key} - nothing was changed. "
            f"TRANSPORT failure, not a verdict: retry when you have a connection.")
        return 4
    status = ((fields.get("status") or {}).get("name") or "").strip()
    labels = list(fields.get("labels") or [])

    if not items:
        if status.lower() == args.status.lower():
            say(f"jira-feed: {args.key} is already {args.status} - nothing to do")
            return 0
        if not args.apply:
            say(f"jira-feed: DRY RUN - `{YOUR_ACTIONS}` is clear, would move {args.key} "
                f"{status} -> {args.status}")
            return 0
        t = acli(binary, ["jira", "workitem", "transition", "--key", args.key,
                          "--status", args.status, "--yes"], timeout=args.timeout)
        back = view_fields(binary, args.key, timeout=args.timeout, strict=False)
        now = ((back or {}).get("status") or {}).get("name") or ""
        if t.returncode != 0 or now.strip() != args.status:
            say(f"jira-feed: {args.key} is still {now.strip() or '?'} - the close did NOT "
                f"land. TRANSPORT, not an artifact defect: the walkthrough is fine and there "
                f"is nothing to fix in it. Retry: {(t.stderr or t.stdout).strip()[:160]}")
            return 4
        # The hold is over, so the signal comes OFF. `user-tasks` means "the walkthrough
        # leaves something only the operator can do"; on a board with no review column it is
        # THE signal, so a Done ticket still carrying it poisons the filter it exists to
        # feed. The sibling half of this same change is built on "the strip is the point" -
        # this writer only ever added (SCC-155 review finding).
        if USER_TASKS_LABEL in labels:
            want = sorted(set(labels) - {USER_TASKS_LABEL})
            lr = acli(binary, ["jira", "workitem", "edit", "--key", args.key, "--yes",
                               "--labels", ",".join(want)], timeout=args.timeout)
            if lr.returncode != 0:
                say(f"[WARN] {args.key}: closed, but `{USER_TASKS_LABEL}` could not be "
                    f"stripped - {(lr.stderr or lr.stdout).strip()[:120]}")
        say(f"jira-feed: {args.key} {status} -> {args.status} "
            f"(`{YOUR_ACTIONS}` had nothing open)")
        return 0

    # ── HELD ───────────────────────────────────────────────────────────────────
    # Hoisted ABOVE the dry run: the DRY RUN message names the ladder too, so a
    # definition further down was a NameError on the path that writes nothing.
    ladder = ((args.review_status,) if getattr(args, "review_status", None)
              else REVIEW_LADDER)
    body = render_user_tasks(items, str(wt), args.date)
    if not args.apply:
        say(f"jira-feed: DRY RUN - {args.key} HELD, {len(items)} open user task(s); would "
            f"post them, add `{USER_TASKS_LABEL}` and try {' -> '.join(ladder)}")
        for it in items:
            say(f"  - [ ] {it}")
        return 3

    # ONE user-tasks comment per ticket, updated in place. `render_user_tasks` tells the
    # operator to tick a box and re-run, so repeated invocation is the DESIGNED happy path -
    # posting unconditionally left a held ticket carrying N near-identical comments, each
    # asserting a different count, with nothing saying which was current. `devrecord` in this
    # same file is documented as "exactly one per ticket, never stacked"; this verb needs the
    # same property for the same reason (SCC-155 review finding).
    existing = find_user_tasks(list_comments(binary, args.key))
    cid = str(existing.get("id") or "") if existing else ""
    tmp = write_temp(body)
    try:
        if cid:
            cm = acli(binary, ["jira", "workitem", "comment", "update", "--key", args.key,
                               "--id", cid, "--body-file", str(tmp)], timeout=args.timeout)
        else:
            cm = acli(binary, ["jira", "workitem", "comment", "create", "--key", args.key,
                               "--body-file", str(tmp)], timeout=args.timeout)
    finally:
        tmp.unlink(missing_ok=True)
    # VERIFY the write, do not trust the exit code. acli returns 0 on writes the board
    # accepted and lost - the close path already reads its transition back for exactly that
    # reason, and the comment is the only thing on the ticket that says WHY it is held, so it
    # earns the same treatment (SCC-155 review #24).
    comment_failed = cm.returncode != 0
    if not comment_failed:
        comment_failed = find_user_tasks(list_comments(binary, args.key)) is None
        if comment_failed:
            say(f"[WARN] {args.key}: acli reported the user-tasks comment posted, but a "
                f"read-back does not find it - the write was accepted and lost.")
    if comment_failed:
        # Do NOT return here. The early return skipped the label and the ladder below, so a
        # failed narration left the ticket held while saying nothing about why - the loss this
        # verb exists to prevent. Signal the hold, THEN report the transport failure.
        say(f"[WARN] {args.key}: the user-tasks comment did NOT land - "
            f"{(cm.stderr or cm.stdout).strip()[:160]}")

    # `--labels` REPLACES the set, so read-modify-write or every other label is destroyed.
    if USER_TASKS_LABEL not in labels:
        want = sorted(set(labels) | {USER_TASKS_LABEL})
        lr = acli(binary, ["jira", "workitem", "edit", "--key", args.key, "--yes",
                           "--labels", ",".join(want)], timeout=args.timeout)
        if lr.returncode != 0:
            say(f"[WARN] {args.key}: could not add `{USER_TASKS_LABEL}` - "
                f"{(lr.stderr or lr.stdout).strip()[:120]}")

    # Already parked on ANY rung? Then there is nothing to do. Comparing only against the rung
    # being tried dragged a ticket an operator had advanced to `In Review` BACKWARDS to
    # `Awaiting Review` on the next held re-run (SCC-155 review finding).
    moved = next((t for t in ladder if status.lower() == t.lower()), "")
    unverified = False
    if not moved:
        for target in ladder:
            acli(binary, ["jira", "workitem", "transition", "--key", args.key,
                          "--status", target, "--yes"], timeout=args.timeout)
            back = view_fields(binary, args.key, timeout=args.timeout, strict=False)
            if back is None:
                # CANNOT-VERIFY is not DID-NOT-MOVE. Marching on would transition the ticket a
                # SECOND time, to a column nobody asked for, and then report "no review column
                # on this board" - false on both counts (SCC-155 review finding).
                unverified = True
                break
            now = ((back.get("status") or {}).get("name") or "").strip()
            if now.lower() == target.lower():
                moved = target
                break

    if moved:
        where = f"moved to `{moved}`"
    elif unverified:
        where = (f"tried `{ladder[0]}` but the board would not confirm it - status "
                 f"UNKNOWN, not unchanged; re-run to settle it")
    else:
        where = (f"left at `{status or '?'}` - no review column on this board yet, so the "
                 f"`{USER_TASKS_LABEL}` label is the signal")
    say(f"jira-feed: {args.key} HELD, not closed - {len(items)} open user task(s), {where}")
    for it in items:
        say(f"  - [ ] {it}")
    # The hold is real and signalled either way; the exit code says whether the NARRATION
    # landed. 4 sends the caller to "transport - retry", which is the true remedy.
    return 4 if comment_failed else 3


def render_flag(args, was: str, status: str) -> str:
    lines = [f"**Bug flag** - {args.date}",
             "",
             f"This ticket shipped as a **{was}** and has been found broken. It wears `Bug` "
             f"until the fix lands; close-out restores it to `{was}`.",
             "",
             f"**What is broken:** {args.reason}"]
    if args.evidence:
        lines += ["", "**Evidence:**"] + [f"- {e}" for e in args.evidence]
    if args.found_by:
        lines += ["", f"**Found by:** {args.found_by}"]
    moved = (f"**Status:** `Done` -> `{args.status}` - back into the work queue."
             if status == "Done" else
             f"**Status:** left at `{status or '?'}` - it was never finished, so there is "
             f"nothing to reopen.")
    lines += ["", moved, "",
              "Cleared by `jira_feed.py devrecord --closing` at whichever close-out owns this "
              "ticket. Nothing else may retype it - see `.agents/rules/jira.md`."]
    return "\n".join(lines) + "\n"


def cmd_flag(args) -> int:
    """Raise the flag: a shipped ticket is broken. Story|Task -> Bug, and out of `Done`.

    Deliberately takes `--key` and nothing else as its target. `trace` can hand you a
    candidate but it cannot hand it to THIS - a wrong trace would pull an innocent ticket out
    of `Done`, and there is no undo that restores the board's history of having been right."""
    binary = acli_bin(args.acli)
    fields = view_fields(binary, args.key)
    have = ((fields.get("issuetype") or {}).get("name") or "").strip()
    status = ((fields.get("status") or {}).get("name") or "").strip()
    summary = field_text(fields.get("summary"))

    if have == "Epic":
        wf.die(f"{args.key} is an Epic - a container is never a Bug. Flag the child ticket "
               f"whose work broke.")
    if have in ("Subtask", "Sub-task"):
        # ⭐ SCC-119, operator ruling: a subtask is NEVER labelled `Bug`. Breakage is recorded
        # on the main ticket - the parent that owns the job - so the flag goes up, not onto
        # the leaf. The old message lumped this in with Epic and called a subtask "a
        # container", which is false twice over: it is a leaf (hierarchyLevel -1), and its
        # own advice - "flag the child ticket whose work broke" - pointed straight back at
        # the ticket it had just refused.
        #
        # The redirect NAMES the parent, because a refusal the operator cannot act on is a
        # dead end. `parent` is on view_fields' whitelist and comes back from `view` (it is
        # rejected on `search`, which is why nothing here reads it that way).
        parent = (fields.get("parent") or {}).get("key")
        wf.die(f"{args.key} is a {have} - a subtask is never labelled Bug (SCC-119); "
               f"breakage is recorded on the ticket that owns the job. "
               + (f"Flag {parent} instead." if parent else
                  "It has no parent on the board, which is itself the defect - "
                  "`jira_feed.py audit` reports it, and re-parenting is a board fix."))
    if have == "Bug":
        # Idempotent on purpose: two testers finding the same bug must not fight over the
        # board, and a re-run must not stack a second flag comment on a ticket already flagged.
        say(f"jira-feed: {args.key} is already flagged Bug - nothing to do "
            f"({summary[:60]})")
        return 0
    if have not in ("Story", "Task"):
        wf.die(f"{args.key} reads as type '{have or '?'}' - refusing to flag a type this rule "
               f"does not know. Check the ticket by hand.")

    body = render_flag(args, have, status)
    if not args.apply:
        say(f"jira-feed: DRY RUN - would flag {args.key} {have} -> Bug"
            + (f", {status} -> {args.status}" if status == "Done" else
               f", status left at {status or '?'}"))
        sys.stdout.write(body)
        return 0

    r = acli(binary, ["jira", "workitem", "edit", "--key", args.key, "--type", "Bug", "--yes"])
    landed = ((view_fields(binary, args.key).get("issuetype") or {}).get("name") or "").strip()
    if r.returncode != 0 or landed != "Bug":
        say(f"jira-feed: {args.key} {have} -> Bug FAILED (still {landed or '?'}) "
            f"{(r.stderr or r.stdout).strip()[:160]}")
        return 2
    say(f"jira-feed: {args.key} {have} -> Bug")

    if status == "Done":
        # ONLY out of Done. A ticket sitting In Progress or In Review is still in flight -
        # shoving it back to To Do would erase real state to record something the type
        # already says. `Deferred` is a To Do-category status by design, so it is not finished
        # either and is left where it is.
        t = acli(binary, ["jira", "workitem", "transition", "--key", args.key,
                          "--status", args.status, "--yes"])
        now = ((view_fields(binary, args.key).get("status") or {}).get("name") or "").strip()
        if t.returncode != 0 or now != args.status:
            say(f"jira-feed: {args.key} is Bug but the status is still {now or '?'} - move it "
                f"off Done by hand: {(t.stderr or t.stdout).strip()[:160]}")
            return 2
        say(f"jira-feed: {args.key} Done -> {args.status}")
    else:
        say(f"jira-feed: {args.key} status left at {status or '?'} (not finished, nothing to "
            f"reopen)")

    tmp = write_temp(body)
    try:
        c = acli(binary, ["jira", "workitem", "comment", "create", "--key", args.key,
                          "--body-file", str(tmp)])
    finally:
        tmp.unlink(missing_ok=True)
    posted = [x for x in list_comments(binary, args.key)
              if "bug flag" in field_text(x.get("body"))[:200].lower()]
    if c.returncode != 0 or not posted:
        # The flag itself landed, so this is not a rollback - it is a ticket that says
        # "broken" with no record of HOW, which is a mystery on the board six weeks later.
        say(f"jira-feed: {args.key} is flagged, but the reason comment did NOT land - post it "
            f"by hand: {(c.stderr or c.stdout).strip()[:160]}")
        return 2
    say(f"jira-feed: {args.key} carries the reason ({len(body)} chars)")
    return 0


def cmd_index_row(args) -> int:
    """Append ONE row to a parent ticket's index description, and PROVE it survived (SCC-170).

    ⛔ `acli jira workitem edit --description` REPLACES the field. It does not append, it has
    no merge, and it exits 0 either way. Every "add the new part to the parent's index" step
    in this system is therefore a read-modify-write against a field other sessions also
    write - and on 2026-08-15 one of them lost SCC-164's Part E row exactly that way:
    silently, exit 0, discovered by a human reading the ticket later.

    This is a DATA-LOSS guard, not a policy gate - the one place `work-consolidation.md`
    puts a mechanism, because the failure is invisible at the point it happens and the lost
    text is not recoverable from anywhere. The read-back is the entire feature: write, read
    the field again, and refuse (exit 2) if any line that was there before is missing.

    Exits: 0 appended (or already present, or a dry run) · 2 refused / the read-back lost a
    line · 4 the board was unreachable (transport, never a verdict on the ticket).
    """
    binary = acli_bin(args.acli)
    row = args.line.rstrip("\n")
    if not row.strip():
        say("jira-feed: --line is empty - nothing to add")
        return 2

    fields = view_fields(binary, args.key, timeout=args.timeout, strict=False)
    if fields is None:
        say(f"jira-feed: could not reach the board to read {args.key} - NOTHING was "
            f"written. Transport, not a verdict: retry when you have a connection.")
        return 4
    before = field_text(fields.get("description"))
    if len(before.strip()) < MIN_DESCRIPTION:
        # An empty read is not evidence the ticket is bare - it is equally what an
        # unreadable or partially-fetched description looks like, and writing one row over
        # it is the same data loss this command exists to stop, wearing a different mask.
        say(f"jira-feed: {args.key}'s description reads as empty ({len(before.strip())} "
            f"chars) and this command REPLACES the field - refusing to write one row over "
            f"it. An empty read is not proof the ticket is bare. Check the ticket, then "
            f"write the whole description with `acli ... edit --description-file`.")
        return 2

    keep = [ln for ln in before.splitlines()]
    if any(ln.strip() == row.strip() for ln in keep):
        say(f"jira-feed: {args.key} already carries that row - nothing to do "
            f"(this step is re-run safe)")
        return 0

    after = before.rstrip("\n") + "\n" + row + "\n"
    if not args.apply:
        say(f"jira-feed: DRY RUN - would append to {args.key}:\n  {row}\n"
            f"(re-run with --apply; the read-back check runs then)")
        return 0

    tmp = write_temp(after)
    try:
        r = acli(binary, ["jira", "workitem", "edit", "--key", args.key, "--yes",
                          "--description-file", str(tmp)])
    finally:
        tmp.unlink(missing_ok=True)
    if r.returncode != 0:
        say(f"jira-feed: the edit failed on {args.key} - nothing was written: "
            f"{(r.stderr or r.stdout).strip()[:400]}")
        return 2

    # ⭐ THE POINT. acli exited 0; that proves nothing. Read the field back and compare.
    again = view_fields(binary, args.key, timeout=args.timeout, strict=False)
    if again is None:
        say(f"jira-feed: {args.key} was written but could NOT be read back - treat this as "
            f"UNVERIFIED and check the ticket by hand before relying on the row.")
        return 2
    now = field_text(again.get("description"))
    lost = [ln for ln in keep if ln.strip() and ln.strip() not in
            {x.strip() for x in now.splitlines()}]
    if lost:
        say(f"jira-feed: ⛔ {args.key}'s description was REPLACED and the read back is "
            f"MISSING {len(lost)} line(s) that were there before:\n"
            + "\n".join(f"    {ln.strip()[:120]}" for ln in lost[:10])
            + f"\n  `edit --description` replaces the whole field. Restore the ticket from "
              f"the text above before doing anything else - this is data loss, not a "
              f"formatting difference.")
        return 2
    if row.strip() not in {x.strip() for x in now.splitlines()}:
        say(f"jira-feed: {args.key} accepted the edit but the new row is not in the read "
            f"back - nothing landed. Do not re-run blindly; read the ticket.")
        return 2
    say(f"jira-feed: {args.key} index row added and read back "
        f"({len(keep)} prior line(s) intact):\n  {row.strip()[:160]}")
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

    story = getattr(args, "story", None)
    if story:
        # Scoped to ONE lane: "did this lane file its record?" - the question a close-out
        # actually needs. Until SCC-113 this flag was accepted and ignored, while three
        # surfaces - including a rule - told agents to pass it.
        #
        # ⛔ This does NOT delegate to find_devrecord, and the difference is the whole safety of
        # it. A first cut did, on a "one rule, one implementation" argument - and that argument
        # INVERTS between the two paths. find_devrecord matches `want not in norm_id(text[:400])`,
        # bare containment over the whole head; on the WRITE path over-matching is conservative
        # (it updates a record in place instead of posting a twin), but here it CERTIFIES that a
        # lane filed a record when it never did. Dev Record bodies are scraped from walkthrough
        # bullets, which routinely name sibling lanes, so the collision is the normal case rather
        # than a corner: a record for lane A whose body mentions lane B passed `--story B`.
        # Matched on the HEADER, exactly - the primitive record_story_id() already provides.
        want = wf.norm_id(story)
        rec = next((c for c in reversed(records) if record_story_id(c) == want), None)
        if rec is None:
            rep.err("devrecord", f"{args.key}: no Dev Record for '{story}' - that lane never "
                                 f"filed one ({len(records)} record(s) on the ticket: "
                                 f"{', '.join(sorted(filter(None, (record_story_id(c) for c in records)))) or 'none with a parseable header'})")
        else:
            rep.info("devrecord", f"{args.key}: one Dev Record for '{story}' "
                                  f"({len(field_text(rec.get('body')))} chars)")
    elif not records:
        rep.err("devrecord", f"{args.key}: no Dev Record - the decisions and pitfalls from "
                             f"dev never reached the ticket")
    else:
        # GROUP, never count - see record_story_id(). The defect is one id carrying two
        # records; distinct ids are two lanes, which is the designed state.
        by_id: dict[str, list] = {}
        for c in records:
            by_id.setdefault(record_story_id(c), []).append(c)
        dupes = {sid: rs for sid, rs in by_id.items() if len(rs) > 1}
        if dupes:
            for sid, rs in sorted(dupes.items()):
                rep.warn("devrecord", f"{args.key}: {len(rs)} Dev Records for "
                                      f"'{sid or '(unparseable header)'}' - there should be "
                                      f"exactly one per lane, updated in place")
        elif "" in by_id and len(records) > 1:
            # ⛔ An unparseable header is NOT evidence of a lane, so it must never be counted as
            # one. The first cut let a "" bucket sit beside a real id and satisfy the "two lanes"
            # arm below - INFO, exit 0, where the old count-based check warned. The trigger is
            # not exotic: `records` is bare containment on the first 400 chars, so any ordinary
            # comment saying "Dev Record" becomes a second record and silences the duplicate
            # check for the whole ticket.
            rep.warn("devrecord", f"{args.key}: {len(records)} Dev Records and "
                                  f"{len(by_id[''])} with no parseable header - cannot tell "
                                  f"which lane filed what. A real record's header reads "
                                  f"`Dev Record - <lane> (<stage>, <date>)`")
        elif len(by_id) > 1:
            # ⛔ SCC-174. Two ids used to be read as self-evidently two lanes, and that is
            # exactly backwards: `devrecord` picks update-vs-create off the SLUG, so filing ONE
            # lane under two slugs is how a ticket gets two ids in the first place. The check
            # was blind precisely when the bug happens (the slugs differ) and loud only once it
            # had been fixed (the slugs match) - it answered "are these two lanes?" when the
            # question is "is this one lane filed twice?". Live instance: AVCH-59, 2026-08-15.
            #
            # The id strings cannot settle it, so stop asking them. A lane leaves a tracked
            # `task.yaml branch:` behind, or a prefixed ref, or both. An id nothing claims is
            # not a lane.
            project = resolve_root(getattr(args, "project", None), need_board=False)
            lanes = lane_slugs(project)
            ids = ", ".join(f"`{s}`" for s in sorted(by_id))
            newest = record_story_id(records[-1])
            if lanes is None:
                rep.warn("devrecord", f"{args.key}: {len(records)} Dev Records under "
                                      f"{len(by_id)} ids ({ids}), and {project} is not a git "
                                      f"checkout - so nothing here can tell two LANES from one "
                                      f"lane filed under two slugs. Point --project at the repo "
                                      f"the lanes live in; a clean exit off unreadable evidence "
                                      f"is what this check was written to stop")
            elif [s for s in sorted(by_id) if s not in lanes]:
                orphans = ", ".join(f"`{s}`" for s in sorted(by_id) if s not in lanes)
                rep.warn("devrecord", f"{args.key}: FORKED Dev Record - {len(records)} records "
                                      f"under {len(by_id)} ids ({ids}), but {orphans} is "
                                      f"claimed by no tracked `task.yaml` branch: and no "
                                      f"branch ref. That is not a second lane, it is ONE lane "
                                      f"filed under two slugs. Newest: `{newest}`. Delete the "
                                      f"record filed under the slug that is not a lane, then "
                                      f"re-post with --story <the manifest's branch slug>")
            else:
                rep.info("devrecord", f"{args.key}: {len(by_id)} Dev Records, one per lane "
                                      f"({', '.join(sorted(by_id))}) - each id is claimed by a "
                                      f"manifest or a branch, and a follow-on lane rides the "
                                      f"ticket it came from, so this is the designed state")
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
    p_mint.add_argument("--type", help="override; default is Story when a BMAD story file "
                                       "backs the ticket, else Task (see issue_type)")
    p_mint.add_argument("--label", action="append")
    p_mint.add_argument("--apply", action="store_true", help="without this, renders only")

    p_dev = sub.add_parser("devrecord", help="post/update THE Dev Record comment")
    common(p_dev)
    p_dev.add_argument("--story", help="the lane slug this record is filed under; defaults "
                                       "to the branch slug in this lane's task.yaml (SCC-174)")
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
    p_dev.add_argument("--closing", action="store_true",
                       help="this is the close-out: clear a `Bug` flag back to Story or Task")
    p_dev.add_argument("--append-new", action="store_true",
                       help="post a SECOND record instead of updating (rare)")
    p_dev.add_argument("--apply", action="store_true", help="without this, renders only")

    p_aud = sub.add_parser("audit", help="do all the ticket TYPES agree with the rule?")
    common(p_aud)
    p_aud.add_argument("--jira-project", required=True, help="e.g. AVCH")
    p_aud.add_argument("--apply", action="store_true", help="fix the mistyped ones")

    p_tr = sub.add_parser("trace", help="which ticket last touched this code? proposes only")
    common(p_tr)
    p_tr.add_argument("--path", action="append", required=True, metavar="FILE[:LINE]",
                      help="repeatable; a :LINE suffix enables the stronger blame signal")
    p_tr.add_argument("--depth", type=int, default=25, help="commits of file history to read")
    p_tr.add_argument("--json", action="store_true")

    p_flag = sub.add_parser("flag", help="this shipped ticket is broken: Story|Task -> Bug")
    common(p_flag)
    p_flag.add_argument("--key", required=True, help="the ticket - NEVER taken from a trace")
    p_flag.add_argument("--reason", required=True, help="what is broken, in one sentence")
    p_flag.add_argument("--evidence", action="append", metavar="TEXT")
    p_flag.add_argument("--found-by", help="e.g. '/cicd-live-testing-team 2026-08-09'")
    p_flag.add_argument("--status", default="To Do",
                        help="where a Done ticket lands (default: To Do)")
    p_flag.add_argument("--date", default=date.today().isoformat())
    p_flag.add_argument("--apply", action="store_true", help="without this, renders only")

    p_start = sub.add_parser("start", help="work has started: move it to In Progress")
    common(p_start)
    p_start.add_argument("--key", required=True, help="the ticket, from the BRANCH name")
    p_start.add_argument("--status", default="In Progress",
                         help="the board's in-flight status (default: In Progress)")
    p_start.add_argument("--timeout", type=int, default=90, metavar="SEC",
                         help="per-acli-call ceiling. The post-commit hook passes a SHORT "
                              "one: it runs inline on every commit until it succeeds, and "
                              "the default 90 would stall each commit for a minute and a "
                              "half on a dead uplink - which is exactly where the operator "
                              "commits from")
    p_start.add_argument("--apply", action="store_true", help="without this, renders only")

    p_fin = sub.add_parser("finish", help="close it - unless the walkthrough owes the "
                                          "operator something")
    common(p_fin)
    p_fin.add_argument("--key", required=True)
    p_fin.add_argument("--walkthrough", required=True,
                       help="the lane's walkthrough.md; its `## Your Actions` section "
                            "decides whether this closes or holds")
    p_fin.add_argument("--status", default="Done",
                       help="the board's terminal status (default: Done)")
    p_fin.add_argument("--review-status",
                       help="the board's review column, overriding the whole ladder "
                            f"({' -> '.join(REVIEW_LADDER)}). The name is board config, "
                            "not code: use this rather than editing the ladder")
    p_fin.add_argument("--timeout", type=int, default=90, metavar="SEC")
    p_fin.add_argument("--date", default=date.today().isoformat())
    p_fin.add_argument("--apply", action="store_true", help="without this, renders only")
    # ⛔ SHIPS DISARMED, and that is the operator's ruling (2026-08-15), not a default someone
    # picked. Arming a gate that can block a shipping path is its own act of law and needs its
    # own quoted words (`blocking-gates-need-a-quoted-ruling`); building the flag now means
    # arming it later is one flag on one invocation rather than a code change and a release.
    p_fin.add_argument("--strict-actions", action="store_true",
                       help="REFUSE (exit 2) when `## Your Actions` carries a row handing the "
                            "operator ticket work, instead of only warning about it")

    # `check-actions` - the same detector, standalone. It is what makes the corpus run
    # reproducible ("run it over every walkthrough and show me the hits") without anyone
    # importing a private helper, and it needs no board, no key and no network.
    p_ca = sub.add_parser("check-actions",
                          help=f"does this walkthrough's `{YOUR_ACTIONS}` hand the operator "
                               f"ticket work? no board, no network")
    p_ca.add_argument("--walkthrough", required=True)

    p_ix = sub.add_parser("index-row",
                          help="append ONE row to a parent's index description and PROVE "
                               "the rest of it survived (acli edit REPLACES the field)")
    common(p_ix)
    p_ix.add_argument("--key", required=True, help="the PARENT ticket whose index this is")
    p_ix.add_argument("--line", required=True, help="the row to append, verbatim")
    p_ix.add_argument("--apply", action="store_true", help="without this, renders only")
    p_ix.add_argument("--timeout", type=int, default=90, metavar="SEC")

    p_chk = sub.add_parser("check", help="does this ticket carry outline + Dev Record?")
    common(p_chk)
    p_chk.add_argument("--key", required=True)
    p_chk.add_argument("--story", help="scope to ONE lane's record (a BMAD story id, or the "
                                       "branch slug a Task lane passes to devrecord): "
                                       "did THIS lane file one? missing is an error")

    args = ap.parse_args()
    return {"outline": cmd_outline, "mint": cmd_mint, "devrecord": cmd_devrecord,
            "audit": cmd_audit, "check": cmd_check, "trace": cmd_trace,
            "flag": cmd_flag, "start": cmd_start, "check-actions": cmd_check_actions,
            "finish": cmd_finish, "index-row": cmd_index_row}[args.verb](args)


if __name__ == "__main__":
    sys.exit(main())
