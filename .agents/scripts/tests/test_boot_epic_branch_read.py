"""Boot reads `sprint-status.yaml` off the EPIC BRANCH, not off the checkout (SCC-254).

`/cicd-close-story-merge-tree` runs **inside the story worktree**, so the `sprint-status.yaml`
it writes rides `claude/<KEY>-<slug>` and lands on `epic/<KEY>-<slug>`. The shared checkout
stays on `main`, which only moves when the whole epic merges. So the copy sitting on disk in
the checkout is stale by **every story that has landed since the epic last shipped** — and
`/cicd-boot-sprint-memory` Step 2b read exactly that copy, with no ref named at all. Measured
on 2026-08-21 against AVCH Epic 19: boot recommended a story three landings behind.

The fix is not "read a different file" — it is **read both and say when they differ**. A
project between epics has no epic branch, and there the checkout copy IS the authority.

⛔ THIS SCAN IS ANCHORED, NOT KEYWORD-COUNTED. Step 2b already resolves a *different*
disagreement (the board's `To Do Next` vs the YAML) and already contains the words "disagree"
and "report both" — so a whole-section keyword check would have passed before the fix was
written and guarded nothing. Every disagreement requirement below is measured in a WINDOW
after the `git show` anchor, and block A3 plants a mutant per requirement to prove each one
still fires.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir

COMMANDS = SCRIPTS.parent / "commands"
BOOT = COMMANDS / "cicd-boot-sprint-memory.md"
HEADING = "## Step 2b"

MIN_BODY_LINES = 20
"""Step 2b is ~57 lines. A body far below this means the heading moved or the file was
gutted, and every "no hits" check below would pass while reading almost nothing."""

WINDOW = 10
"""Lines after the `git show` anchor that count as "in the same breath". Generous enough to
survive a reflow, far short of the ~14 lines back to the board-vs-YAML paragraph whose
wording this must NOT be allowed to satisfy."""

# The `git show` of the epic copy — the anchor everything else is measured from.
# ⛔ The objectspec COLON is part of the requirement. `git show <ref>:<path>` is the form; degrade
# that colon to a slash and git answers `fatal: ambiguous argument` — but a pattern that only
# looked for `epic/` … `sprint-status.yaml` on one line called the broken command satisfied.
ANCHOR = re.compile(r"git\s+(?:-C\s+\S+\s+)?show\s[^\n]*\bepic/\S*:\S*sprint-status\.yaml")

# (name, pattern, where it must appear, why it is required)
_SECTION, _AFTER, _CLAIM = "section", "window", "claim"
REQUIRED: tuple[tuple[str, re.Pattern[str], str, str], ...] = (
    ("epic-read", ANCHOR, _SECTION,
     "a `git show <epic-ref>:…/sprint-status.yaml` — close-out writes the YAML INSIDE the "
     "story worktree, so the landed truth is on the epic branch, not in the checkout"),
    ("ref-discovery", re.compile(r"""cd\s+["']\$L["']\s*&&\s*\S*python3?\s+[^\n]*?"""
                                 r"""epic_mode\.py\s+--repo\s+["']\S"""), _SECTION,
     "`cd \"$L\" && python3 .agents/scripts/epic_mode.py --repo \"$PROJECT_ROOT\"` — the epic ref is "
     "DISCOVERED by the one query every door shares (SCC-446), which reads ORIGIN only "
     "(a local epic head is only as fresh as the last pull) and prints the mode word first. "
     "A door that re-types its own `for-each-ref` glob is the drift this script retired. "
     "⛔ The QUOTES are load-bearing and pinned, exactly as the retired `for-each-ref` "
     "refspec's were: unquoted, a `PROJECT_ROOT` holding a space word-splits and argparse "
     "answers `unrecognized arguments` on stderr with exit 2, so the door's mode line "
     "becomes a usage message and no mode is ever printed (SCC-446 review). "
     "⛔ AND THE `cd \"$L\"` PIN IS PART OF THE REQUIREMENT, not decoration. `epic_mode.py` "
     "lives in the LOBBY and no project ships it, while the line above this one `cd`s into "
     "`$PROJECT_ROOT` to fetch — so the bare `python3 .agents/scripts/epic_mode.py` this row "
     "used to ask for resolves against the PROJECT and dies `No such file or directory` in "
     "every repo. That is not hypothetical: it is what shipped, and this row is what told the "
     "author to write it. `$L` is pinned at Step 0 with `L=$(pwd)` BEFORE any `cd` "
     "(`command-shape.md` §Absolute fills)"),
    ("no-epic-fallback", re.compile(r"no epic branch|between epics", re.I), _AFTER,
     "the project that has NO epic branch — there the checkout copy is the authority, and a "
     "boot that errors out instead of saying so is a worse boot than the stale one"),
    ("disagreement", re.compile(r"disagree", re.I), _AFTER,
     "what happens when the two copies differ — measured in the window, because Step 2b "
     "already says this about the BOARD and that sentence must not be allowed to count"),
    ("report-both", re.compile(r"report\s+both", re.I), _AFTER,
     "the words `report both`, in the window — one disagreement idiom in this file, not two"),
    ("names-both-copies", re.compile(r"(?is)epic.*checkout|checkout.*epic"), _CLAIM,
     "the disagreement sentence must name BOTH copies — the epic branch and the checkout. "
     "⛔ Step 2b already says `disagree` and `report both` about the BOARD, and the window is "
     "the only thing keeping that sentence out; reflow it ten lines up and the two checks "
     "above go green on a section that never mentions the epic copy at all. Measured on the "
     "SENTENCE, not the window — the no-epic fallback line names both copies too, and a "
     "window-wide check let it stand in for the claim"),
)

# Characterization: true before the fix and after it. The fix ADDS the epic read; a future
# edit that swaps to it and drops the checkout read breaks the no-epic project silently.
CHECKOUT_COPY = re.compile(r"_bmad-output/implementation-artifacts/sprint-status\.yaml")


def section(text: str, prefix: str) -> tuple[str, int]:
    """(body, how many headings matched `prefix`) — body ends at the next SAME-or-shallower head.

    The count is returned, not swallowed: a duplicated `## Step 2b` would otherwise let the
    scan read one copy and pass while the other one carried the defect.

⛔ FENCE-AWARE. A `# comment` on the first column of a ```bash block is byte-identical to an
`<h1>`, and the very fix this scan demanded plants one. Un-guarded, the section ended AT the
code it was checking for and the body check reported a section a third of its real length.
    """
    level = len(prefix) - len(prefix.lstrip("#"))
    stop = re.compile(rf"^#{{1,{level}}}\s+\S")
    body: list[str] = []
    hits, on, fenced = 0, False, False
    for ln in text.splitlines():
        if ln.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced:
            if ln.startswith(prefix):
                hits, on = hits + 1, True
                continue
            if on and stop.match(ln):
                on = False
        if on:
            body.append(ln)
    return "\n".join(body), hits


def after_anchor(body: str) -> str:
    """The WINDOW lines following the first anchor line — `""` when there is no anchor."""
    lines = body.splitlines()
    for i, ln in enumerate(lines):
        if ANCHOR.search(ln):
            return "\n".join(lines[i + 1: i + 1 + WINDOW])
    return ""


def claim(win: str) -> str:
    """The ONE sentence in the window that carries `report both`, whitespace-flattened.

    ⛔ Not the window. The window also holds the no-epic fallback — *"the checkout copy IS the
    authority"* — which names both copies all by itself, so a window-wide check for "epic AND
    checkout" is satisfied no matter what the disagreement sentence says. The requirement is
    about the CLAIM."""
    flat = " ".join(win.split())
    m = re.search(r"report\s+both", flat, re.I)
    if not m:
        return ""
    start = flat.rfind(". ", 0, m.start()) + 1
    dot = flat.find(". ", m.end())
    return flat[start:len(flat) if dot < 0 else dot + 1]


def missing(body: str) -> list[tuple[str, str]]:
    """-> [(requirement name, why it is required)] for every one not satisfied."""
    win = after_anchor(body)
    hays = {_SECTION: body, _AFTER: win, _CLAIM: claim(win)}
    out = []
    for name, pat, where, why in REQUIRED:
        if not pat.search(hays[where]):
            out.append((name, why))
    return out


def report(rows: list[tuple[str, str]]) -> str:
    if not rows:
        return ""
    return "\n      " + "\n      ".join(f"MISSING [{n}] — {w}" for n, w in rows)


# ⛔ `$L` MUST BE BOUND IN THE FENCE THAT USES IT — every fence, not just Step 2b's.
# A ```bash fence is its OWN SHELL: nothing a previous fence assigned survives into it. So the
# `ref-discovery` row above, which pins the shape `cd "$L" && python3 …`, is satisfied by a line
# whose `$L` is empty — and `cd ""` exits 0 WITHOUT MOVING. The door then runs the lobby's script
# from inside `$PROJECT_ROOT` (the line above it `cd`s there to fetch) and dies `No such file or
# directory`, which is the exact death the pin was added to prevent. Reproduced 2026-09-11 on
# Step 2b: cwd stayed at the project, the mode line exited 2, no mode was ever printed.
#
# Why this is file-wide and not another `REQUIRED` row: `missing()` measures ONE section and
# takes the FIRST match per pattern, so a second door-step that repeats the call unbound stays
# invisible to it. The binding is a property of each fence, so it is measured per fence.
L_USE = re.compile(r"\$L\b|\$\{L\}")
L_BIND = re.compile(r"(?:^|[\s;&|(])L=")


def unbound_L(text: str) -> list[tuple[int, str]]:
    """-> [(line number, the offending line)] for every `$L` used before `L=` in ITS OWN fence."""
    out: list[tuple[int, str]] = []
    bound, fenced = False, False
    for n, ln in enumerate(text.splitlines(), 1):
        if ln.lstrip().startswith("```"):
            fenced = not fenced
            bound = False  # a new fence is a new shell; the old binding does not cross
            continue
        if not fenced:
            continue
        if L_BIND.search(ln):
            bound = True
        if L_USE.search(ln) and not bound:
            out.append((n, ln.strip()))
    return out


# A Step 2b that satisfies every requirement, used to prove each check can FAIL.
GOOD = """
Read `_bmad-output/implementation-artifacts/sprint-status.yaml` — it is ~62 KB of bare rows.
Read it off the EPIC BRANCH, not off the checkout:
```bash
cd "$L" && python3 .agents/scripts/epic_mode.py --repo "$PROJECT_ROOT"
git show origin/epic/<KEY>-<slug>:_bmad-output/implementation-artifacts/sprint-status.yaml
```
No epic branch (a project between epics) → the checkout copy IS the authority; say so and move on.
When the two disagree, report both ("the epic branch has <id> at <status>; the checkout copy
still says <status>") and lead with the epic branch.
"""

# Each mutant breaks exactly one requirement in GOOD. Several requirements have MORE THAN ONE
# way to fail — a `git show` can lose its ref or just its colon; a refspec can lose its star or
# just its quotes — so this is a list of triples, not one mutant per name.
MUTANTS: tuple[tuple[str, str, str], ...] = (
    ("epic-read", "git show origin/epic/<KEY>-<slug>:_bmad-output/implementation-artifacts/"
                  "sprint-status.yaml", "cat sprint-status.yaml"),
    # git: `fatal: ambiguous argument` — a path is not an objectspec.
    ("epic-read", "epic/<KEY>-<slug>:_bmad", "epic/<KEY>-<slug>/_bmad"),
    # the door re-types its own glob instead of the shared query (the drift SCC-446 retired)
    ("ref-discovery", 'python3 .agents/scripts/epic_mode.py --repo "$PROJECT_ROOT"',
     "git for-each-ref --format='%(refname:short)' 'refs/remotes/origin/epic/*'"),
    # cwd is not intent: the script REQUIRES --repo, and a call without it exits 2
    ("ref-discovery", 'epic_mode.py --repo "$PROJECT_ROOT"', "epic_mode.py"),
    # the QUOTES alone: a path with a space word-splits and argparse exits 2 on stderr
    ("ref-discovery", '--repo "$PROJECT_ROOT"', "--repo $PROJECT_ROOT"),
    # ⛔ THE LOBBY PIN ALONE, AND THIS IS THE SHAPE THAT ACTUALLY SHIPPED (SCC-441 review).
    # `epic_mode.py` lives in the lobby; the line above this one `cd`s into `$PROJECT_ROOT`,
    # and no project carries the script. So the unpinned call resolves against the PROJECT and
    # dies `No such file or directory` at the door's first step, in every repo. The regex used
    # to accept it and the requirement text used to ASK for it.
    ("ref-discovery", 'cd "$L" && python3 .agents/scripts/epic_mode.py',
     "python3 .agents/scripts/epic_mode.py"),
    # the pin present but aimed at the project: the same death, spelled the other way
    ("ref-discovery", 'cd "$L" &&', 'cd "$PROJECT_ROOT" &&'),
    # the line dropped altogether: a boot that never asks which epic it is on
    ("ref-discovery", 'cd "$L" && python3 .agents/scripts/epic_mode.py --repo "$PROJECT_ROOT"\n', ""),
    ("no-epic-fallback", "No epic branch (a project between epics) → the checkout copy IS "
                         "the authority; say so and move on.", "Otherwise carry on."),
    ("disagreement", "When the two disagree, report both", "When the two differ, report both"),
    ("report-both", "report both (\"the epic", "prefer the epic branch ((\"the epic"),
    # ⛔ B1's mutant: Step 2b's own pre-existing BOARD sentence, moved into the window. It keeps
    # `disagree` and `report both` and mentions neither copy — the exact sentence the window was
    # built to exclude, and before `names-both-copies` it satisfied both of those requirements.
    ("names-both-copies",
     "When the two disagree, report both (\"the epic branch has <id> at <status>; the checkout "
     "copy\nstill says <status>\") and lead with the epic branch.",
     "When the board and the YAML disagree, report both and lead with the board."),
)


def main() -> int:
    c = Cases("boot reads sprint-status off the epic branch (SCC-254)")

    if c.block("A1 · the live boot command"):
        c.check(f"{BOOT.name} exists (a rename must FAIL, not scan nothing)", BOOT.is_file(),
                str(BOOT))
        text = BOOT.read_text(encoding="utf-8") if BOOT.is_file() else ""
        body, hits = section(text, HEADING)
        c.check(f"exactly one `{HEADING}` heading", hits == 1, f"matched {hits}")
        c.check(f"the Step 2b body is at least {MIN_BODY_LINES} lines",
                len(body.splitlines()) >= MIN_BODY_LINES, f"{len(body.splitlines())} lines")

        gaps = missing(body)
        c.check("Step 2b names the epic-branch read AND reports the disagreement",
                not gaps, f"{len(gaps)} requirement(s) unmet" + report(gaps))
        in_tree = bool(CHECKOUT_COPY.search(body))
        c.check("...and still reads the checkout's own copy (no blind swap)", in_tree,
                f"plain in-tree path present={in_tree} — a project between epics has no epic "
                f"branch, so dropping it would leave that project reading nothing")

    if c.block("A2 · the pre-fix shape is what this scan REJECTS"):
        # Verbatim shape of the defect: the path, no ref, no epic anywhere.
        stale = ("Read `_bmad-output/implementation-artifacts/sprint-status.yaml` — post-split it "
                 "is\n~62 KB of bare `key: status` rows and fits one read.\n"
                 "When the board and the YAML disagree, report both and lead with the board.\n")
        gaps = {n for n, _ in missing(stale)}
        c.check("the un-fixed section fails on the epic read", "epic-read" in gaps, f"{gaps}")
        c.check("...and its board-vs-YAML `disagree`/`report both` do NOT satisfy the window",
                {"disagreement", "report-both"} <= gaps,
                "a whole-section keyword check would have passed here and guarded nothing")

    if c.block("A3 · every requirement fails its own mutant"):
        c.check("the reference section satisfies all of them", not missing(GOOD),
                report(missing(GOOD)))
        for name, find, replace in MUTANTS:
            mutant = GOOD.replace(find, replace)
            c.check(f"mutant fires: {name} → {replace[:44]!r}",
                    mutant != GOOD and name in {n for n, _ in missing(mutant)},
                    f"substitution applied={mutant != GOOD}; "
                    f"missing={[n for n, _ in missing(mutant)]}")

    if c.block("A5 · the claim is measured as a SENTENCE, not as the window"):
        win = after_anchor(GOOD)
        c.check("the window really does name both copies twice over — claim AND fallback",
                len(re.findall(r"(?i)checkout", win)) >= 2, f"{re.findall(r'(?i)checkout', win)}")
        c.check("...so `claim()` isolates one sentence, not the lot",
                "report both" in claim(win).lower() and "authority" not in claim(win).lower(),
                claim(win))
        board = GOOD.replace(
            'When the two disagree, report both ("the epic branch has <id> at <status>; '
            'the checkout copy\nstill says <status>") and lead with the epic branch.',
            "When the two disagree, report both and lead with the newer one.")
        c.check("a claim that names only ONE copy fires, even though the fallback names both",
                "names-both-copies" in {n for n, _ in missing(board)},
                f"claim={claim(after_anchor(board))!r}")
        c.check("...and the window-wide reading would have MISSED it",
                bool(re.search(r"(?is)epic.*checkout|checkout.*epic", after_anchor(board))),
                "this is why the requirement moved off the window")
        c.check("no `report both` at all yields an empty claim, which fails closed",
                claim("nothing here") == "", "an absent claim is never a satisfied one")

    if c.block("A4 · the scan's own failure modes"):
        with TempDir() as tmp:
            gone = tmp / "nope.md"
            c.check("a missing file reads as absent, never as a clean scan", not gone.is_file(),
                    str(gone))
            plant = tmp / "b.md"
            plant.write_text("## Step 2b — one\nx\n## Step 2b — two\ny\n", encoding="utf-8")
            _, hits = section(plant.read_text(encoding="utf-8"), HEADING)
            c.check("a DUPLICATED Step 2b heading is caught, not silently halved", hits == 2,
                    f"hits={hits}")
            plant.write_text(f"## Step 2b — x\n{GOOD}\n### child stays in\nkeep\n## Step 3\ndrop\n",
                             encoding="utf-8")
            body, _ = section(plant.read_text(encoding="utf-8"), HEADING)
            c.check("a `###` child stays IN the section; the next `##` ends it",
                    "keep" in body and "drop" not in body, body[-60:].replace("\n", "|"))
            plant.write_text("## Step 2b — x\n```bash\n# origin/ FIRST — a shell comment\n"
                             "git show origin/epic/k:sprint-status.yaml\n```\nafter the fence\n"
                             "## Step 3\ndrop\n", encoding="utf-8")
            body, _ = section(plant.read_text(encoding="utf-8"), HEADING)
            c.check("a `# comment` inside a ```fence``` does NOT end the section",
                    "after the fence" in body and "drop" not in body,
                    "the fix this scan demands plants exactly such a comment")

            c.check("an anchor at the very end yields an empty window, not the lines before it",
                    after_anchor("filler\n" * 5 + "git show origin/epic/x:sprint-status.yaml") == "",
                    "window must never read BACKWARDS")

    if c.block("A6 · every `$L` is bound in the fence that uses it"):
        loose = unbound_L(BOOT.read_text(encoding="utf-8")) if BOOT.is_file() else [(0, "absent")]
        c.check(f"{BOOT.name}: no fence uses `$L` before binding it", not loose,
                "; ".join(f"line {n}: {ln}" for n, ln in loose) or "clean")

        # The two shapes, proved to fail. A fence is its own shell, so the binding must be IN it.
        crosses = ('```bash\nL=$(pwd)\ncd "$PROJECT_ROOT" && git fetch\n```\n'
                   'prose between the fences\n'
                   '```bash\ncd "$PROJECT_ROOT" && git fetch\ncd "$L" && python3 x.py\n```\n')
        c.check("a binding in an EARLIER fence does not carry into a later one",
                [n for n, _ in unbound_L(crosses)] == [8], f"{unbound_L(crosses)}")
        after = '```bash\ncd "$L" && python3 x.py\nL=$(pwd)\n```\n'
        c.check("...and a binding placed AFTER the use is still unbound at the use",
                len(unbound_L(after)) == 1, f"{unbound_L(after)}")
        ok = '```bash\nL=$(pwd)\ncd "$PROJECT_ROOT" && git fetch\ncd "$L" && python3 x.py\n```\n'
        c.check("the fixed shape — bind first, in the same fence — passes", not unbound_L(ok),
                f"{unbound_L(ok)}")
        c.check("`$LOBBY` is not a use of `$L`", not unbound_L('```bash\ncd "$LOBBY"\n```\n'),
                "a prefix match here would fire on every unrelated variable")
        c.check("`${L}` IS a use of `$L`", len(unbound_L('```bash\ncd "${L}"\n```\n')) == 1,
                "the braced spelling is the same variable")
        c.check("prose outside a fence is not scanned",
                not unbound_L('the door pins `$L` at Step 0\n'),
                "the requirement text names `$L` constantly and is not a shell")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
