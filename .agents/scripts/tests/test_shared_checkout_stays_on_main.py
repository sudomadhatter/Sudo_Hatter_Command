"""The shared checkout stands on `main` — opening a story tree must not move it (SCC-256).

`worktree-per-story.md` says both of these, ~150 lines apart:

  :70  the `worktree.baseRef: "head"` setting makes the new worktree inherit the current HEAD,
       so **check out the base branch before opening the worktree**
  :221 The shared checkout needs no reconcile after a landing — **it stands on `main`**

Both are true of a DIFFERENT door and the file never says so, and
`cicd-write-story-tests.md:27` inherited the seam as a flat precondition — *"and HEAD is on it
(**never** `main`)"*. Followed literally it parks the shared checkout on the epic branch and
never brings it home; the next `git status`, the next `worktree add`, the next boot all read a
tree the operator believes is `main`.

`worktree.baseRef: "head"` is REAL (`.claude/settings.json`), so the precondition is not
wrong — it is unqualified. `git worktree add <path> -b <branch> origin/epic/<…>` takes its
base as an OPERAND and needs no HEAD move at all; `EnterWorktree` inherits HEAD and does. The
law below is therefore not "never say HEAD" but: **a HEAD precondition must name the door it
belongs to AND the return to `main` in the same breath.**

⛔ PARAGRAPHS, NOT LINES. The authority states its precondition across a line break ("check
out the / base branch before opening the worktree"), so a line scan is blind to exactly the
rule the command is following. Every match and every ruling below is measured on the
whitespace-normalised paragraph.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir

AGENTS = SCRIPTS.parent
COMMANDS = AGENTS / "commands"
RULES = AGENTS / "rules"

MIN_COMMANDS = 40
MIN_RULES = 10
"""Floors, not censuses (66 and 26 as of SCC-256). An empty glob — wrong CWD, a renamed
folder — must FAIL, never report a clean scan of nothing."""

# A precondition on where HEAD is standing, in the two shapes the surface actually uses.
PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    # "and HEAD is on it (never `main`)" — the command's shape.
    ("head-position",
     re.compile(r"\bHEAD\b[^\n]{0,40}?\b(?:is|must be|should be|needs to be|has to be) on\b")),
    # "check out the base branch before opening the worktree" — the rule's shape.
    ("checkout-first",
     re.compile(r"\b(?:check ?out|switch to)\b.{0,60}?\bbefore (?:opening|you open|creating)\b")),
)

# What makes a HEAD precondition CORRECT rather than a contradiction. Both halves, same
# paragraph: the door that genuinely inherits HEAD, and the trip home.
DOOR = re.compile(r"EnterWorktree|baseRef")
RETURN_HOME = re.compile(r"\b(?:back|return)(?:ing)?\s+to\s+\W?main\b", re.I)

# The replacement wiring, pinned so the fix cannot be "delete the sentence and say nothing".
BASE_AS_OPERAND = re.compile(r"worktree add[^\n]*\\?\n?[^\n]*origin/epic/")

# ...and the operand carries a cost the pin above cannot see. `origin/epic/<…>` is a
# REMOTE-TRACKING start point, so `branch.autoSetupMerge` (on by default) sets the new lane's
# upstream to the EPIC: `git status -sb` reads `## claude/…...origin/epic/…` and every later
# `0 0` check measures the wrong remote, while a bare `git push` refuses outright —
#   fatal: The upstream branch of your current branch does not match the name of your current
#   branch. …use  git push origin HEAD:epic/<…>
# — and that suggested remedy is the mid-story epic push G3 of `worktree-per-story.md` BANS.
# `push.autoSetupRemote=true` does not rescue it. `--no-track` leaves the lane with no upstream
# until its own first push. Measured on the whitespace-normalised PARAGRAPH, so the command's
# backslash continuation is already joined for us.
WORKTREE_EPIC = re.compile(r"worktree add\b(?P<flags>[^\n]*?)\borigin/epic/")
NO_TRACK = re.compile(r"--no-track\b")
UNSET_UPSTREAM = re.compile(r"branch\s+--unset-upstream\b")

CURE_WINDOW = 4
"""⛔ There are TWO cures and the house uses both, so this scan may not demand one idiom.
`--no-track` rides the call itself; `git -C <tree> branch --unset-upstream` is a separate line
after it, and that is the shape `smh-plan-task.md` and `cicd-quick-dev.md` already ship — both
with their own "not optional" note. A gate that saw only the flag would go red on a surface that
is already correct. The window is LOGICAL lines, so a `link-worktree-assets` call or a comment
between the two does not break the pairing."""


def logical_lines(text: str) -> list[tuple[int, str]]:
    """-> [(1-based number of the line it STARTS on, the line with continuations joined)].

    ⛔ Physical lines are the wrong unit here. The story door writes its call across a backslash
    continuation, so a physical-line scan sees `worktree add …` and `… origin/epic/<…>` as two
    unrelated lines and never matches the call at all — and `paragraphs()` is the wrong unit in
    the other direction: it joins a fenced call to whatever prose shares its block, which is how
    an `origin/epic/` mentioned three lines below an unrelated `worktree add --track` got read as
    one command."""
    out: list[tuple[int, str]] = []
    buf: list[str] = []
    start = 0
    for n, raw in enumerate(text.splitlines(), 1):
        if not buf:
            start = n
        s = raw.rstrip()
        if s.endswith("\\"):
            buf.append(s[:-1])
            continue
        buf.append(s)
        out.append((start, " ".join(x.strip() for x in buf).strip()))
        buf = []
    if buf:
        out.append((start, " ".join(x.strip() for x in buf).strip()))
    return out


def untracked_bases(folders: list[Path]) -> list[tuple[str, int, str]]:
    """-> [(file, line, the call)] for every epic-based `worktree add` left tracking the epic."""
    out: list[tuple[str, int, str]] = []
    for folder in folders:
        for f in sorted(folder.glob("*.md")):
            lines = logical_lines(f.read_text(encoding="utf-8"))
            for i, (n, line) in enumerate(lines):
                m = WORKTREE_EPIC.search(line)
                if not m or NO_TRACK.search(m.group("flags")):
                    continue
                after = " ".join(x for _, x in lines[i + 1: i + 1 + CURE_WINDOW])
                if UNSET_UPSTREAM.search(after):
                    continue
                out.append((f"{folder.name}/{f.name}", n, line))
    return out


def paragraphs(text: str) -> list[tuple[int, str]]:
    """-> [(1-based line number of the paragraph's first line, whitespace-normalised text)]."""
    out: list[tuple[int, str]] = []
    start, buf = 0, []
    for n, raw in enumerate(text.splitlines(), 1):
        if raw.strip():
            if not buf:
                start = n
            buf.append(raw)
        elif buf:
            out.append((start, " ".join(buf)))
            buf = []
    if buf:
        out.append((start, " ".join(buf)))
    return out


def scan(folders: list[Path]) -> tuple[list[tuple[str, int, str, str, bool]], dict[str, int]]:
    """-> ([(file, line, pattern, paragraph, ruled)], {folder name: files read}).

    `ruled` is carried, not filtered out, so the caller can assert both directions: no
    unruled hits, AND at least one ruled hit (an exemption path nothing exercises is a hole).
    """
    hits: list[tuple[str, int, str, str, bool]] = []
    counts: dict[str, int] = {}
    for folder in folders:
        files = sorted(folder.glob("*.md"))
        counts[folder.name] = len(files)
        for path in files:
            for line, para in paragraphs(path.read_text(encoding="utf-8")):
                for name, pat in PATTERNS:
                    if pat.search(para):
                        ruled = bool(DOOR.search(para) and RETURN_HOME.search(para))
                        hits.append((path.name, line, name, para, ruled))
                        break
    return hits, counts


def report(rows: list[tuple[str, int, str, str, bool]]) -> str:
    if not rows:
        return ""
    lines = [f"{f}:{n}  [{p}]  {para[:110]}…" for f, n, p, para, _ in rows]
    return ("\n      " + "\n      ".join(lines) + "\n      REMEDY: either drop the precondition "
            "and name the base as an OPERAND (`git worktree add <path> -b <branch> "
            "origin/epic/<…>`), or keep it and name BOTH the HEAD-inheriting door "
            "(`EnterWorktree` / `baseRef`) and the return to `main` in the same paragraph.")


def main() -> int:
    c = Cases("the shared checkout stands on main (SCC-256)")

    hits, counts = scan([COMMANDS, RULES])

    if c.block("C1 · the live command + rule surface"):
        c.check(f"read at least {MIN_COMMANDS} commands and {MIN_RULES} rules "
                "(an empty glob is a FAIL)",
                counts.get("commands", 0) >= MIN_COMMANDS and counts.get("rules", 0) >= MIN_RULES,
                f"{counts}")
        bad = [h for h in hits if not h[4]]
        c.check("no unqualified HEAD precondition for opening a worktree",
                not bad, f"{len(bad)} unruled" + report(bad))
        # ⛔ Do NOT assert that the live surface still HAS a ruled hit. Exactly one exists today
        # and it is the ruled one, so `any(ruled)` only restates the check above — and it goes RED
        # the day the paragraph is reworded or `EnterWorktree` is retired, which is a surface that
        # is strictly BETTER. C3 exercises the ruling path on planted text either way. What is
        # worth asserting here is that a live ruling was earned: re-derive both halves from the
        # paragraph, independently of `scan()`'s own bookkeeping.
        ruled = [h for h in hits if h[4]]
        c.check("every live exemption names BOTH halves — the HEAD-inheriting door and the "
                "trip home",
                all(DOOR.search(h[3]) and RETURN_HOME.search(h[3]) for h in ruled),
                f"{len(ruled)} ruled of {len(hits)} hits; zero is a PASS — a surface that no "
                f"longer needs the exemption has outgrown it")

    if c.block("C2 · the story door names its base as an operand"):
        wst = COMMANDS / "cicd-write-story-tests.md"
        c.check(f"{wst.name} exists", wst.is_file(), str(wst))
        text = wst.read_text(encoding="utf-8") if wst.is_file() else ""
        found = bool(BASE_AS_OPERAND.search(text))
        c.check("① opens the story tree off `origin/epic/…` NAMED, not off wherever HEAD sat",
                found, f"`worktree add … origin/epic/` present={found}")
        c.check("...and does it `--no-track`, so the lane's upstream is not the EPIC",
                not untracked_bases([COMMANDS]),
                f"{[(f, n) for f, n, _ in untracked_bases([COMMANDS])]}")

    if c.block("C4 · no `worktree add … origin/epic/…` anywhere tracks the epic"):
        offenders = untracked_bases([COMMANDS, RULES])
        c.check("every epic-based worktree call passes `--no-track`",
                not offenders,
                f"{len(offenders)} tracking the epic: "
                + "; ".join(f"{f}:{n}" for f, n, _ in offenders)
                + ("\n      REMEDY: add `--no-track` to the `worktree add`. Without it "
                   "`branch.autoSetupMerge` points the lane's upstream at `origin/epic/<…>`, "
                   "`0 0` measures the wrong remote, and a bare `git push` fatals — offering "
                   "the mid-story epic push G3 bans." if offenders else ""))

    if c.block("C3 · the scan fires, and the ruling is not a rubber stamp"):
        with TempDir() as tmp:
            plant = tmp / "s"
            plant.mkdir()

            def one(body: str) -> list[tuple[str, int, str, str, bool]]:
                (plant / "z.md").write_text(body, encoding="utf-8")
                return scan([plant])[0]

            defect = ("2. Else confirm the story's EPIC branch exists and HEAD is on it "
                      "(**never** `main`),\n   then open the worktree off it.\n")
            r = one(defect)
            c.check("caught: the command's flat precondition",
                    len(r) == 1 and not r[0][4], f"{[(h[2], h[4]) for h in r]}")

            across = ("The `worktree.baseRef: \"head\"` setting makes the new worktree inherit "
                      "the current HEAD, so **check out the\nbase branch before opening the "
                      "worktree** — if you are somewhere else, get there first.\n")
            r = one(across)
            c.check("caught: the rule's precondition, which SPANS a line break",
                    len(r) == 1 and not r[0][4], f"{[(h[2], h[4]) for h in r]}")

            c.check("...and a line-by-line scan would have missed that one entirely",
                    not any(p.search(ln) for _, p in PATTERNS for ln in across.splitlines()),
                    "this is why the scan reads paragraphs")

            half = across.rstrip() + " Get there first.\n"
            c.check("half-ruled is NOT ruled: the door alone does not excuse it",
                    not one(half)[0][4], "names baseRef, never says how you get home")

            whole = (across.rstrip() + " Go **back to `main`** the moment the tree is open.\n")
            c.check("both halves in one paragraph → ruled",
                    one(whole)[0][4], f"{[(h[2], h[4]) for h in one(whole)]}")

            split = across.rstrip() + "\n\nGo back to `main` afterwards — a DIFFERENT paragraph.\n"
            c.check("...and the trip home in a different paragraph does NOT rule it",
                    not one(split)[0][4], "the ruling is per-paragraph on purpose")

            quiet = ("git -C \"$PROJECT_ROOT\" worktree add .claude/worktrees/<slug> \\\n"
                     "    -b claude/<KEY>-<slug> origin/epic/<KEY>-<slug>\n")
            c.check("quiet: naming the base as an operand needs no precondition at all",
                    not one(quiet), f"{one(quiet)}")
            c.check("...and that same block satisfies the operand pin",
                    bool(BASE_AS_OPERAND.search(quiet)), quiet.replace("\n", "|"))

            # C4's mutant: the SAME call, one flag short. It must be caught, and the catch must
            # survive the backslash continuation the real command is written across.
            (plant / "z.md").write_text(quiet, encoding="utf-8")
            c.check("caught: the operand form WITHOUT `--no-track` tracks the epic",
                    len(untracked_bases([plant])) == 1, f"{untracked_bases([plant])}")

            fixed = quiet.replace("worktree add", "worktree add --no-track")
            (plant / "z.md").write_text(fixed, encoding="utf-8")
            c.check("...and clean once the flag is there, continuation and all",
                    not untracked_bases([plant]), fixed.replace("\n", "|"))

            (plant / "z.md").write_text(
                fixed.replace("origin/epic/<KEY>-<slug>", "origin/main"), encoding="utf-8")
            c.check("...and a `main`-based tree is not this scan's business",
                    not untracked_bases([plant]), "the flag matters where the base is REMOTE-tracking")

            # The SECOND cure, which the quick-dev door already ships: no flag, but the upstream
            # is unset on a following line. A gate that demanded the flag would go red on it.
            cured = quiet.rstrip() + ('\ngit -C "<the new tree>" branch --unset-upstream'
                                      "   # an origin/… start-point sets upstream to the BASE\n")
            (plant / "z.md").write_text(cured, encoding="utf-8")
            c.check("`branch --unset-upstream` on a following line is the OTHER cure, and counts",
                    not untracked_bases([plant]), cured.replace("\n", "|"))

            far = quiet.rstrip() + "\nfiller\n" * (CURE_WINDOW + 1) + \
                'git -C "<t>" branch --unset-upstream\n'
            (plant / "z.md").write_text(far, encoding="utf-8")
            c.check(f"...but not {CURE_WINDOW + 1} lines later — a cure that far off is not the pair",
                    len(untracked_bases([plant])) == 1, f"{untracked_bases([plant])}")

            prose = ('git worktree add --track -b claude/<K>-<s> .claude/worktrees/<s> '
                     "origin/claude/<K>-<s>\n\nA story with no parked branch opens off "
                     "`origin/epic/<K>-<s>` instead.\n")
            (plant / "z.md").write_text(prose, encoding="utf-8")
            c.check("prose naming `origin/epic/…` near an UNRELATED call is not a call",
                    not untracked_bases([plant]),
                    "logical lines, not paragraphs — this is cicd-resume.md's real shape")

            empty = tmp / "empty"
            empty.mkdir()
            c.check("an empty folder reports 0 files, so the floor FAILS it",
                    scan([empty])[1]["empty"] == 0, "floor is the smoke alarm for the scan itself")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
