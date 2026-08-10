"""The SOPs + PRDs folder must not rot (SCC-74, 2026-08-10).

`docs/_scc_sops_prds/` holds every procedural document in this system: the pages that tell the
operator what to do and what to type. They were scattered across `_my_resources/_quick_reference/`
and `_my_resources/diagrams_guides/` until this ticket moved them.

  -- WHY THEY ROTTED, WHICH IS THE WHOLE POINT ---------------------------------------------
They did not rot from neglect. They rotted because `_my_resources/` is named in SCAN_IGNORES
(check_maps.py), in DEFAULT_REGEN_IGNORE for the repo-map, and in the GitNexus ignore list --
and its own local law says "excluded from repo-map regen + linter scans ... do not fix that."
Ten of the thirteen lived inside a folder every drift-checker in this system is FORBIDDEN to
look at. No automation could reach them, so nothing could notice when they went wrong. It
showed: the index they lived under listed 2 files that did not exist and omitted 4 that did.

Operator ruling 2026-08-10 makes the split explicit and permanent:

    _my_resources/  = human thinking and brainstorming space. Agents ignore it unless
                      Daniel links a specific document. Staleness there is FINE by design.
    docs/           = the maintained surface. Must always be kept from going stale.

A procedural doc sitting in the first is therefore a defect BY DEFINITION. That is what this
file enforces, and why it is a test rather than a convention.

  -- WHAT THIS CHECKS ----------------------------------------------------------------------
    T1  the folder holds exactly the expected manifest
    T2  its INDEX.md matches the directory -- no phantom rows, no unlisted files
    T3  every relative link inside the folder resolves
    T4  every command reference resolves to a real command master
    T5  sop_currency.py's SOP_DOC points at a file that exists
    T6  no procedural doc is left behind in _my_resources/
    T7  autopilot_bmad_dev_loop.md exists exactly once in the repo
    T8  the hook's shell guard and sop_currency.SOP_DOC name the SAME file

  -- WHY A TEST AND NOT JUST THE COMMIT GATE -----------------------------------------------
`sop_currency.py` asks "did the author update the PRD in the same commit." That is
co-occurrence: it proves someone LOOKED, never that the folder is correct. These checks prove
the folder is correct, on every run_all, on both machines. The two are complements and neither
replaces the other. `check_maps.py` independently covers INDEX-path validity repo-wide once
the docs are inside `docs/`; T2 is the regression that keeps THIS folder's INDEX honest even
if that scope ever narrows.

  -- T4 IS SCOPED ON PURPOSE ---------------------------------------------------------------
The naive check ("flag every `sudo-` string") is wrong in both directions and was tried first.
`sudo-command.atlassian.net` is the REAL Jira site slug; `_bmad-output/sudo-tests...` is a
path, not a command. A blanket pattern flags all of those and would have had someone "fix" the
live Jira URL. Meanwhile the genuinely dead reference -- `/sudo-update-scrum-board`, a command
retired by SCC-13 -- hides inside backticks, where a path-avoiding pattern misses it.

So T4 resolves references against `.agents/commands/` instead of pattern-matching a prefix: a
command reference is dead when no master answers to that name. That is self-maintaining -- it
catches the NEXT rename with no edit here -- and it is scoped to this system's command families
plus a short list of pre-SCC-63 bare aliases, so URL segments (`/api`), doc words (`/how-to`),
and directory names (`/scripts`) cannot trip it. The fixture controls below prove both halves:
it fires on real defects and stays quiet on the look-alikes.

One deliberate exemption: DISCUSSED_AS_RETIRED. A doc whose SUBJECT is a retirement must be able
to name the thing that was retired -- flagging that would push an author to delete the sentence
explaining the change. What T4 really guards is "no doc tells you to RUN something that does not
exist," and a fixture proves the exemption stays narrow rather than becoming an off-switch.

  -- THE MANIFEST IS A CONTRACT, NOT AN INVENTORY ------------------------------------------
T1/T6 pin an explicit 13-doc list. That is deliberate: adding a 14th doc must be a conscious
edit here. A doc appearing or vanishing without a test change is exactly the drift being
guarded against, and an auto-discovered manifest would rubber-stamp it.

Stdlib only, plain ASCII output -- same constraints as its siblings (Windows consoles are cp1252).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import Cases

ROOT = Path(__file__).resolve().parents[3]
FOLDER_REL = "docs/_scc_sops_prds"
FOLDER = ROOT / FOLDER_REL

# The contract. Renames land here in the same commit that performs them.
EXPECTED = {
    "workflows_testing_SOP.md",          # was _quick_reference/sudo_workflows_testing.md
    "jira_manual.md",
    "jira_integration_guide.md",
    "git_walkthrough_settings.md",
    "autopilot_bmad_dev_loop.md",
    "sentry_error_response_team.md",
    "file_folder_structure+maintaining.md",
    "md_feedback_setup_guide.md",
    "tea_testing_guide.md",
    "tea_deep_reference.md",
    "tdad_stack_install_guide.md",
    "smh-adviser-board-REFERENCE.md",
}

# Folders that must hold no procedural docs once the move lands. Both are removed by SCC-74;
# the check survives their removal (a missing dir trivially holds nothing) so it keeps guarding
# against a doc being re-created there later.
VACATED = ("_my_resources/_quick_reference", "_my_resources/diagrams_guides")

# A slash NOT preceded by a word char, dot, or slash. Kills `_bmad-output/sudo-tests` (path) and
# `https://sudo-command.atlassian.net` (URL) while KEEPING `` `/cmd` `` -- backticks are where
# commands are actually written, so excluding them misses the real defects.
TOKEN = re.compile(r"(?<![\w./])/([a-z][a-z0-9-]*[a-z0-9])")
# This system's command families (AGENTS.md naming law, SCC-63). `sudo-` is retired and kept here
# precisely so any surviving reference resolves to nothing and fails.
FAMILY = re.compile(r"^(cicd|smh|sentry|sudo)-")
# Pre-SCC-63 bare names that carried no prefix. Short and closed by design -- every command minted
# since carries a family prefix, so this list does not grow.
RETIRED_ALIASES = {"new-project", "sync-agents", "update-maps-indexes", "adviser-board"}

# Names these docs are ALLOWED to mention, because the retirement itself is the subject.
#
# A doc that records "`/sudo-update-scrum-board` is gone, use the Jira board" is doing its job --
# flagging it would push an author to delete the very sentence that explains the change to the next
# reader. This is the classic source-grep inversion: the literal appears most often in the prose
# ABOUT its removal. The check still has teeth, because what it really guards is "no doc tells you
# to RUN something that does not exist," and an entry here is a deliberate, reviewable claim that a
# given name is discussed historically rather than prescribed.
#
# Keep it SHORT. Each entry needs a reason, and a name that stops appearing should be removed.
DISCUSSED_AS_RETIRED = {
    # SCC-13 retired the scrum board on 2026-08-07; workflows_testing_SOP.md section 11 is the
    # written record of the scrum-board -> Jira transition and names it to explain what replaced it.
    "sudo-update-scrum-board",
}

LINK = re.compile(r"\[[^\]]*\]\(([^)\s#]+)")


def det(ok: bool, msg: str) -> str:
    """Detail text, suppressed on success.

    The harness prints whatever detail it is handed regardless of outcome, so an
    unconditional f-string makes a PASS line carry its own failure message -- e.g.
    `[PASS] T1 folder exists: docs/_scc_sops_prds missing`. A gate whose green output
    reads like red is a gate people stop reading.
    """
    return "" if ok else msg


def _md_files(d: Path) -> list[Path]:
    return sorted(p for p in d.glob("*.md") if p.name != "INDEX.md") if d.is_dir() else []


def _command_masters() -> set[str]:
    return {p.stem for p in (ROOT / ".agents" / "commands").glob("*.md")}


def unresolved_commands(text: str, masters: set[str]) -> set[str]:
    """Command references in `text` that no master answers to. Pure, so fixtures can drive it."""
    out = set()
    for m in TOKEN.finditer(text):
        t = m.group(1)
        if t in DISCUSSED_AS_RETIRED:
            continue
        if (FAMILY.match(t) or t in RETIRED_ALIASES) and t not in masters:
            out.add(t)
    return out


def main() -> int:
    c = Cases("sops-prds folder (SCC-74)")
    masters = _command_masters()

    # -- T4 detector fixtures FIRST: a checker nobody has proven is a checker nobody can trust.
    c.check("T4-fixture fires on a retired command",
            unresolved_commands("see `/sudo-write-story-tests` for the flow", masters)
            == {"sudo-write-story-tests"})
    c.check("T4-fixture fires on a pre-SCC-63 alias",
            unresolved_commands("run /sync-agents to publish", masters) == {"sync-agents"})
    quiet = ("visit https://sudo-command.atlassian.net and read "
             "_bmad-output/sudo-tests/report.md via /api and the /how-to guide")
    qok = unresolved_commands(quiet, masters) == set()
    c.check("T4-fixture quiet on Jira slug + paths + URL segments", qok,
            det(qok, f"got {sorted(unresolved_commands(quiet, masters))}"))
    c.check("T4-fixture allow-list is narrow, not a blanket off-switch",
            unresolved_commands("run `/sudo-update-scrum-board` and `/sudo-made-up-name`", masters)
            == {"sudo-made-up-name"})
    live = sorted(masters)[0] if masters else ""
    c.check("T4-fixture quiet on a LIVE command",
            unresolved_commands(f"run /{live} now", masters) == set() if live else False)

    # -- T1: the manifest
    present = {p.name for p in _md_files(FOLDER)}
    ok = FOLDER.is_dir()
    c.check("T1 folder exists", ok, det(ok, f"{FOLDER_REL} missing"))
    ok = present == EXPECTED
    c.check("T1 manifest matches", ok,
            det(ok, f"missing={sorted(EXPECTED - present)} unexpected={sorted(present - EXPECTED)}"))

    # -- T2: INDEX matches disk, both directions. The defect that rotted the old folder was
    #        exactly this: 2 rows pointing at nothing, 4 files nobody listed.
    idx = FOLDER / "INDEX.md"
    if not idx.is_file():
        c.check("T2 INDEX.md exists", False, f"{FOLDER_REL}/INDEX.md missing")
    else:
        text = idx.read_text(encoding="utf-8", errors="replace")
        linked = {t for m in LINK.finditer(text)
                  if not (t := m.group(1)).startswith(("http", "mailto:"))}
        phantom = sorted(t for t in linked if not (idx.parent / t).exists())
        unlisted = sorted(n for n in present if n not in {Path(t).name for t in linked})
        c.check("T2 INDEX.md exists", True)
        c.check("T2 no phantom rows", not phantom, det(not phantom, f"dead: {phantom}"))
        c.check("T2 no unlisted files", not unlisted, det(not unlisted, f"absent from INDEX: {unlisted}"))

    # -- T3/T4 scan the folder's contents, so an ABSENT folder gives them an empty set and a
    #    vacuous green. That is the failure mode where deleting the folder makes the suite
    #    healthier, so both fail loudly instead of quietly finding nothing to complain about.
    scannable = FOLDER.is_dir() and bool(present)

    # -- T3: relative links resolve
    if not scannable:
        c.check("T3 no dead relative links", False, "folder absent - nothing scanned (not a pass)")
    else:
        dead = []
        for p in _md_files(FOLDER) + ([idx] if idx.is_file() else []):
            for m in LINK.finditer(p.read_text(encoding="utf-8", errors="replace")):
                t = m.group(1)
                if t.startswith(("http", "mailto:")):
                    continue
                # Cross-repo targets are OUT OF SCOPE for a lobby gate. Projects/<name>/ are
                # separate git repos: they are gitignored here, and a `git worktree` checkout
                # gets only empty stub dirs for them. Asserting on their contents makes this
                # test a permanent false RED in every lane -- and a gate that is red for
                # reasons the author cannot fix is a gate that gets ignored or deleted.
                # Their currency is the OTHER repo's ticket (cross-repo = a ticket per repo).
                if "Projects/" in t:
                    continue
                if not (p.parent / t).exists():
                    dead.append(f"{p.name} -> {t}")
        c.check("T3 no dead relative links", not dead, "; ".join(dead[:6]))

    # -- T4: against the real docs
    if not scannable:
        c.check("T4 every command reference resolves", False,
                "folder absent - nothing scanned (not a pass)")
    else:
        bad = {}
        for p in _md_files(FOLDER):
            for t in unresolved_commands(p.read_text(encoding="utf-8", errors="replace"), masters):
                bad.setdefault(t, []).append(p.name)
        c.check("T4 every command reference resolves", not bad,
                "; ".join(f"/{k} in {','.join(v)}" for k, v in sorted(bad.items())))

    # -- T5: the gate points somewhere real. A SOP_DOC aimed at a moved file is a gate that can
    #        never be satisfied -- it blocks every usage-surface commit until someone notices.
    try:
        sys.path.insert(0, str(ROOT / ".agents" / "scripts"))
        import sop_currency
        ok5 = (ROOT / sop_currency.SOP_DOC).is_file()
        # detail ONLY on failure -- the harness prints it either way, and a PASS carrying a
        # "does not exist" string reads as a failure to anyone scanning the log.
        c.check("T5 sop_currency.SOP_DOC resolves", ok5,
                "" if ok5 else f"SOP_DOC={sop_currency.SOP_DOC} does not exist")
    except Exception as e:                                  # import failure is a real failure
        c.check("T5 sop_currency.SOP_DOC resolves", False, f"{type(e).__name__}: {e}")

    # -- T8: the shell guard and the python constant must name the SAME file.
    #
    #    sop-currency.sh line ~26 does `[ -f <SOP doc> ] || exit 0` so the gate degrades
    #    gracefully in a project clone that has no SOP page. Move the doc without moving that
    #    literal and the LOBBY starts looking like a project clone: the hook exits 0 before it
    #    ever reaches the python, and the gate disarms ITSELF, silently, with no output anywhere
    #    -- under VS Code, which renders hook output nowhere the operator looks, that is
    #    indistinguishable from a clean pass. T5 cannot see this: it only checks the python
    #    constant, and the two drifting apart is exactly the bug.
    sh = ROOT / ".agents/scripts/git-hooks/sop-currency.sh"
    try:
        import sop_currency as _sc                          # already on sys.path from T5
        # ALL `[ -f x ]` guards, not the first -- the script opens with the DISABLE kill-switch
        # guard, so a first-match regex asserts against the wrong literal and can never pass.
        guards = re.findall(r"\[\s*-f\s+(\S+)\s*\]",
                            sh.read_text(encoding="utf-8", errors="replace"))
        ok8 = _sc.SOP_DOC in guards
        c.check("T8 hook guard matches SOP_DOC", ok8,
                "" if ok8 else f"SOP_DOC={_sc.SOP_DOC} not among the hook's -f guards: {guards}")
    except Exception as e:
        c.check("T8 hook guard matches SOP_DOC", False, f"{type(e).__name__}: {e}")

    # -- T6: nothing left behind. RECURSIVE on purpose -- diagrams_guides/ nested its docs under
    #    system/, security/ and workflows_tea_testing/, so a top-level glob saw 3 of 13 and
    #    reported a near-clean folder while ten procedural docs sat one level down.
    left = sorted(p.relative_to(ROOT).as_posix()
                  for v in VACATED for p in (ROOT / v).rglob("*.md")
                  if p.name != "INDEX.md") if any((ROOT / v).is_dir() for v in VACATED) else []
    c.check("T6 no procedural docs in _my_resources", not left,
            det(not left, f"{len(left)} left: " + "; ".join(left[:4])
                          + (" ..." if len(left) > 4 else "")))

    # -- T7: one copy of the doc that existed twice with 508 differing lines.
    #    Filter the RELATIVE path, never p.parts -- this repo is checked out inside
    #    .claude/worktrees/<lane>/, so the absolute parts contain "worktrees" for every file
    #    and an absolute-path filter silently excludes the entire tree (found 0 of 2 copies).
    copies = []
    for p in ROOT.rglob("autopilot_bmad_dev_loop.md"):
        rel = p.relative_to(ROOT).as_posix()
        parts = rel.split("/")
        if {".git", "_artifacts", "Projects", "worktrees"} & set(parts):
            continue
        copies.append(rel)
    ok = len(copies) == 1
    c.check("T7 exactly one autopilot_bmad_dev_loop.md", ok, det(ok, f"copies: {sorted(copies)}"))

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
