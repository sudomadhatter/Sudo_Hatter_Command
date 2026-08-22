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
        c.check("the exemption path is exercised by real text (it rules something)",
                any(h[4] for h in hits),
                f"{sum(1 for h in hits if h[4])} ruled of {len(hits)} hits — a ruling nothing "
                f"matches is a hole waiting for a future paragraph to fall into")

    if c.block("C2 · the story door names its base as an operand"):
        wst = COMMANDS / "cicd-write-story-tests.md"
        c.check(f"{wst.name} exists", wst.is_file(), str(wst))
        text = wst.read_text(encoding="utf-8") if wst.is_file() else ""
        found = bool(BASE_AS_OPERAND.search(text))
        c.check("① opens the story tree off `origin/epic/…` NAMED, not off wherever HEAD sat",
                found, f"`worktree add … origin/epic/` present={found}")

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

            empty = tmp / "empty"
            empty.mkdir()
            c.check("an empty folder reports 0 files, so the floor FAILS it",
                    scan([empty])[1]["empty"] == 0, "floor is the smoke alarm for the scan itself")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
