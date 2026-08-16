"""A bare `main` in a command body is a STALE ref (SCC-165).

`git fetch` updates `origin/main`; it does NOT move the local `main` branch. In a shared
checkout that has sat on `main` for a week — or in a worktree, where `main` is whatever the
main checkout last pulled — every `main...HEAD`, `merge-base HEAD main` and
`worktree add … main` silently answers a question about a ref nobody refreshed. The diff is
wrong, the "commits behind" count is wrong, and a lane cut from it is born stale.

Not every one is a defect. A line that deliberately asks about the LOCAL branch
(`rev-list --left-right --count main...origin/main`, the "am I in sync" check) is correct as
written, and a blanket sed would break it. Those live in ALLOWED, each with the reason.

⛔ ALLOWED is keyed on the exact operand line TEXT, never a line NUMBER. A number breaks on
the next edit above it, and worse, it lets a NEW bare-main hit inherit the old line's pass.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir

COMMANDS = SCRIPTS.parent / "commands"

MIN_FILES = 10
"""An empty glob is a FAIL, never a count of 0.

Run from the wrong CWD, or after the folder is renamed, `glob("*.md")` returns nothing and a
"no hits" guard passes while scanning NOTHING. The floor is far below the real count (63 as
of SCC-165) — it is a smoke alarm for the scan itself, not a census.
"""

# `main` as a git OPERAND. The lookarounds are the whole trick: `(?<![\w/.-])` rejects
# `origin/main` (the fix), `_main` (`_artifacts/_main/`) and `<epic-branch-or-main>` (a
# placeholder), so the scan sees only a bare ref where a branch name belongs.
_BARE = r"(?<![\w/.-])main(?![\w/.-])"
PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    # `main..X` / `main...X`
    ("range-left", re.compile(r"(?<![\w/.-])main\.\.\.?")),
    # `X..main` / `X...main`
    ("range-right", re.compile(r"\.\.\.?main(?![\w/.-])")),
    # `merge-base HEAD main`, `merge-tree … HEAD main`, `worktree add … <branch> main`.
    # `[^`\n]*?` cannot cross a backtick, so a code span in prose is scanned as its own unit.
    ("cmd-operand", re.compile(r"\b(?:merge-base|merge-tree|worktree add)\b[^`\n]*?" + _BARE)),
    # SCC-165 follow-on (Part 6): a bare `main` reached as a shell DEFAULT, not as an operand.
    # ⛔ `_BARE` cannot be reused here and that is the whole finding: its `(?<![\w/.-])`
    # lookbehind - the thing that makes `origin/main` and `_main` safe - also rejects the `-`
    # of `${BASE:-main}`, so the operand scan was structurally blind to the default-value
    # operator. `cicd-clean-code-audit.md:49` sat unseen through the entire A sweep because of
    # it: sighted by a human reading the file, invisible to the scan that was supposed to find it.
    ("ref-default", re.compile(r":-\s*main(?![\w/.-])")),
    # `BASE=main`, `EPIC="main"` - assignment position, which is operand position one line later.
    ("ref-assign", re.compile(r"\b(?:BASE|EPIC|TARGET|TRUNK|REF)=\"?" + _BARE)),
)

# (file name, exact stripped line text) -> why this bare `main` is CORRECT.
_SYNC = ("the `0 0` local-vs-remote sync check: the LEFT operand is deliberately the local "
         "branch — that IS the question being asked, and `origin/main...origin/main` would "
         "be a tautology that always passes")
ALLOWED: dict[tuple[str, str], str] = {
    ("cicd-push-e2e.md",
     "git rev-list --left-right --count main...origin/main    # must be 0 0"): _SYNC,
    ("smh-close-task-merge-tree.md",
     "git rev-list --left-right --count main...origin/main    # must be 0 0"): _SYNC,
    # ⛔ SCC-183 removed a THIRD row here. `/smh-merge-multiple-workingtrees` step 4d used to
    # merge and push `main` itself and then verify the sync with `main...origin/main`; it now
    # lands each lane through its own PR, so that line is gone and its exemption ruled nothing.
    # The "no rows left ruling nothing" check is what noticed — an exemption that outlives the
    # line it excused is a hole waiting for a future line to fall into.
    ("smh-merge-multiple-workingtrees.md",
     'git -C "$REPO" rev-list --left-right --count main...origin/main    # 0 0'): _SYNC,
}


def scan(folder: Path) -> tuple[list[tuple[str, int, str, str]], int]:
    """-> ([(file, lineno, stripped line, pattern name)], number of files READ).

    One hit per line: the allowlist is keyed on line text, so a line is ruled once.
    """
    hits: list[tuple[str, int, str, str]] = []
    files = sorted(folder.glob("*.md"))
    for path in files:
        for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for name, pat in PATTERNS:
                if pat.search(raw):
                    hits.append((path.name, n, raw.strip(), name))
                    break
    return hits, len(files)


def unruled(hits: list[tuple[str, int, str, str]]) -> list[tuple[str, int, str, str]]:
    return [h for h in hits if (h[0], h[2]) not in ALLOWED]


def report(rows: list[tuple[str, int, str, str]]) -> str:
    if not rows:
        return ""
    lines = [f"{f}:{n}  [{p}]  {t}" for f, n, t, p in rows]
    return ("\n      " + "\n      ".join(lines) + "\n      REMEDY: `origin/main` preceded by "
            "`git fetch origin main` in that command — or, if the line genuinely asks about "
            "the LOCAL branch, an ALLOWED row in this file carrying the reason.")


def main() -> int:
    c = Cases("stale base refs (SCC-165)")

    live, n_files = scan(COMMANDS)

    if c.block("A1 · the live command surface"):
        c.check(f"the scan read at least {MIN_FILES} command files (an empty glob is a FAIL)",
                n_files >= MIN_FILES, f"read {n_files} from {COMMANDS}")
        bad = unruled(live)
        c.check("no command diffs, counts or cuts against a bare local `main`",
                not bad, f"{len(bad)} unruled operand(s)" + report(bad))
        seen = {(f, t) for f, _, t, _ in live}
        stale = [k for k in ALLOWED if k not in seen]
        c.check("every ALLOWED row still matches a real line (no rows left ruling nothing)",
                not stale, f"stale rows: {stale}")

    if c.block("A2 · the scan catches each operand shape"):
        with TempDir() as tmp:
            plant = tmp / "cmds"
            plant.mkdir()
            caught = {
                "main...HEAD": 'git -C "$REPO" diff --name-only main...HEAD',
                "X..main": 'git diff --name-only "$BASE"..main | sort',
                "..main quoted": 'git rev-list --count "chore/<KEY>-<slug>..main"',
                "merge-base": 'BASE=$(git -C "$REPO" merge-base HEAD main)',
                "merge-tree": "git merge-tree --write-tree --messages HEAD main | head -40",
                "worktree add": "git worktree add .claude/worktrees/<slug> -b chore/<KEY>-<slug> main",
                "in a table cell": "| `git diff --name-only main...chore/<KEY>-<slug>` | code beats talk |",
                # SCC-165 follow-on: the two shapes the operand scan was blind to. The first is
                # the real line from `cicd-clean-code-audit.md:49`, verbatim.
                "${BASE:-main} default": ("BASE=$(git for-each-ref --format='%(refname:short)' "
                                          "refs/heads/epic/* | head -1); BASE=${BASE:-main}"),
                "BASE=main assignment": 'BASE=main   # the trunk, one line before it becomes an operand',
            }
            for label, line in caught.items():
                (plant / "z.md").write_text(line + "\n", encoding="utf-8")
                hits, _ = scan(plant)
                c.check(f"caught: {label}", len(hits) == 1, f"hits={hits}")

    if c.block("A3 · the scan does NOT fire on a ref that is already right"):
        with TempDir() as tmp:
            plant = tmp / "cmds"
            plant.mkdir()
            quiet = {
                "origin/main...HEAD (the fix itself)": 'git diff --name-only origin/main...HEAD',
                "merge-base HEAD origin/main": "BASE=$(git merge-base HEAD origin/main)",
                "worktree add … origin/main": "git worktree add <t> -b chore/<KEY>-<slug> origin/main",
                "_artifacts/_main/ path": "see `_artifacts/_main/<date>_<slug>/task.yaml`",
                "<epic-branch-or-main> placeholder": "| `git diff --name-only <epic-branch-or-main>...<story-branch>` |",
                "checkout main (local BY DEFINITION)": "git checkout main",
                "pull/push origin main (local by definition)": "env -u GITHUB_TOKEN git pull --ff-only origin main",
                "prose about the main checkout": "lanes junction shared assets back to the **main checkout**",
                "${BASE:-origin/main} (the fix)": "BASE=${BASE:-origin/main}",
                "BASE=origin/main assignment": "BASE=origin/main",
                "an epic default is not a trunk default": "BASE=${BASE:-origin/epic/<KEY>-<slug>}",
            }
            for label, line in quiet.items():
                (plant / "z.md").write_text(line + "\n", encoding="utf-8")
                hits, _ = scan(plant)
                c.check(f"quiet: {label}", not hits, f"hits={hits}")

    if c.block("A4 · the guard's own failure modes"):
        with TempDir() as tmp:
            empty = tmp / "empty"
            empty.mkdir()
            _, n = scan(empty)
            c.check("an empty folder FAILS the floor rather than reporting a clean scan",
                    n < MIN_FILES, f"read {n} files -> floor {MIN_FILES} not met")

            plant = tmp / "cmds"
            plant.mkdir()
            line = "git rev-list --left-right --count main...origin/main    # must be 0 0"
            (plant / "cicd-push-e2e.md").write_text(line + "\n", encoding="utf-8")
            hits, _ = scan(plant)
            c.check("an ALLOWED row exempts its exact line", not unruled(hits), f"{unruled(hits)}")

            (plant / "cicd-push-e2e.md").write_text(line.replace("0 0", "0 1") + "\n",
                                                    encoding="utf-8")
            hits, _ = scan(plant)
            c.check("...and one changed character in that line does NOT inherit the exemption",
                    len(unruled(hits)) == 1, f"{unruled(hits)}")

            (plant / "some-other-command.md").write_text(line + "\n", encoding="utf-8")
            hits, _ = scan(plant)
            c.check("...nor does the same text in a DIFFERENT file",
                    any(f == "some-other-command.md" for f, _, _, _ in unruled(hits)),
                    f"{unruled(hits)}")

            c.check("the failure message names file:line and BOTH remedies",
                    all(s in report(unruled(hits)) for s in
                        ("some-other-command.md:1", "origin/main", "git fetch origin main",
                         "ALLOWED row")),
                    report(unruled(hits))[:120])

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
