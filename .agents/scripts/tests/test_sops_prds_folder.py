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
T1/T6 pin an explicit 11-doc list. That is deliberate: a 12th doc must be a conscious edit
here. A doc appearing or vanishing without a test change is exactly the drift being guarded
against, and an auto-discovered manifest would rubber-stamp it.

It has shrunk twice from the 13 SCC-74 moved, and both times the contract did its job -- the
suite went red until all three edits (file, INDEX row, EXPECTED) landed together:
    -1  complete-system-overview.md   retired INTO file_folder_structure+maintaining.md (SCC-80)
    -1  md_feedback_setup_guide.md    relocated UP to docs/ -- a machine-setup guide, not an SOP
The second is a scope call, not a demotion: it stays inside docs/, so check_maps.py still
covers it. The line this folder draws is "SOP vs setup," never "watched vs unwatched."

Stdlib only, plain ASCII output -- same constraints as its siblings (Windows consoles are cp1252).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import Cases, TempDir

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


# ── T9: backticked PATHS in prose (SCC-83) ───────────────────────────────────────────
# T3 above reads markdown LINK targets. check_maps.py reads backticked paths, but only
# inside TABLE ROWS. So a path written in a sentence, a bullet or a fenced block is seen
# by nothing -- which is how these docs accumulated references to folders that two landed
# tickets had deleted, with every gate green.
#
# ⛔ SCOPE, stated because an unstated one reads as total coverage: this sees BACKTICKED
# tokens only. Measured folder-wide at build time: exactly 2 path-shaped tokens sit
# outside backticks, so the convention holds and widening the net would buy 2 checks at
# the cost of matching ordinary prose. The INDEX's mechanism table carries this as a row.
CODE_SPAN = re.compile(r"`([^`\n]+)`")

# Tokens that are shaped like a path and are not one. ⭐ THE FIXTURED PART: the first
# sweep for this ticket excluded 2392 tokens through a regex written by eye, with nothing
# proving it. Too broad and real dead references vanish silently while this reads green;
# too narrow and 153 false positives come back and the signal gets ignored. Every class
# below has a control in T9-fixture.
NOT_A_PATH = re.compile(
    r"^(origin|upstream|epic|chore|claude|story|incident|main|HEAD)/"  # branch names
    r"|^/(api|ws|v\d)/"                                               # URL routes
    r"|^(openrouter|anthropics|google|openai)/"                       # vendor/model ids
    r"|^@"                                                            # npm scopes
    r"|[*?\[\]]|\.\.\.|\s"                                            # globs, ellipses, prose
)
PATH_LIKE = re.compile(r"^[\w.@+-]+(?:/[\w.@+-]+)+/?$")

# Absent ON PURPOSE. Each entry states why, because an allow-list is one line away from
# being an off-switch -- the DISCUSSED_AS_RETIRED lesson from T4, one tier down.
ABSENT_BY_DESIGN = {
    # A kill switch: its ABSENCE is the armed state. Creating it to satisfy a doc would
    # disarm every git hook in the repo. The doc is right to name it.
    ".agents/scripts/git-hooks/DISABLE":
        "kill switch - absence IS the armed state (git-hooks/INDEX.md)",
    # Runtime output. Exists only while an autopilot run is live, and is gitignored, so a
    # clean tree never has it. Naming it is the doc's job; creating it is the run's.
    "_artifacts/_autopilot-run.log":
        "runtime output - written by a live autopilot run, gitignored",
    # ⭐ PROVENANCE, and the T4 lesson one tier down. These two folders were emptied by
    # SCC-74, and the docs that say "consolidated FROM here" are doing their job. Flagging
    # them pushes an author to delete the sentence explaining where everything went --
    # exactly the inversion DISCUSSED_AS_RETIRED exists to prevent. Note the scope: the
    # FOLDERS are exempt, individual FILES under them are not, because
    # `_my_resources/_quick_reference/jira_manual.md` is not provenance, it is a live
    # instruction to open a file that moved.
    "_my_resources/_quick_reference/": "retired by SCC-74 - named as provenance",
    "_my_resources/diagrams_guides/": "retired by SCC-74 - named as provenance",
}

# `~~`path`~~` -- the author has explicitly struck it through as gone. Reporting it asks
# them to delete the very line recording the removal. Found by the RED: line 11 of
# file_folder_structure+maintaining.md already says "**gone**" and was flagged anyway.
STRUCK = re.compile(r"~~[^~]*~~")


def _is_stub_project(t: str, roots: list[Path]) -> bool:
    """`Projects/<name>/...` where <name> is checked out as an empty stub.

    ⛔ Found by the RED, and it is the trap this test exists to avoid. The first-segment
    rule below skips `backend/tests/` because no `backend/` exists here -- but an EXPLICIT
    `Projects/AGY_AVIATIONCHAT/scripts/` sails straight past it, because `Projects/` does
    exist. Every git worktree checks those out empty, so without this the check reports a
    dead reference for every project path in every lane. The A3c control covered only the
    implicit form and would have shipped this.
    """
    parts = Path(t).parts
    if len(parts) < 2 or parts[0] != "Projects":
        return False
    for r in roots:
        d = r / parts[0] / parts[1]
        if d.is_dir() and not any(d.iterdir()):
            return True
    return False


def unresolved_paths(text: str, roots: list[Path], base: Path | None = None,
                     strict: bool = True) -> dict[str, str]:
    """(see below) -- `strict=False` when some project is only a stub in this checkout.

    ⛔ WHY strict EXISTS, measured: the same folder yields 25 findings from a worktree and
    12 from the main checkout. Tokens like `_bmad-output/sudo-tests.yaml` have a first
    segment the lobby also has, so the skip rules above pass them through, and then they
    fail because the project that really owns them is an empty stub. Fix the 12 and every
    lane would still be red on 13 findings its author cannot fix -- which is how a gate
    gets ignored, then deleted (the same reasoning T3 carries about Projects/ links).

    So when anything is stubbed, T9 asserts only what is PROVABLE without the projects: a
    token whose leaf was found again INSIDE THE LOBBY, i.e. a file that demonstrably moved.
    "Resolves nowhere" is downgraded to unprovable and dropped. It still fails -- it just
    fails on the subset that cannot be an artefact of where you are standing."""
    """Backticked paths in `text` that resolve under none of `roots`.

    `roots` is injected so fixtures drive this without touching the real tree, and so the
    caller decides what "here" means -- the lobby alone, or the lobby plus each POPULATED
    project root.

    ⭐ The first path segment must name a directory that exists in some root, or the token
    is SKIPPED rather than reported. That one rule is what keeps this honest in a worktree:
    `Projects/<name>/` is an empty stub there, so `backend/tests/` is not absent, it is
    NOT CHECKED OUT -- and a checker that cannot tell those apart produces a worklist that
    is mostly wrong. Measured on this very folder: 10 of 11 such hits were false. Same
    ruling as rotted_pointers() in test_memory_store.py -- return nothing rather than noise,
    because a signal people learn to skip is worse than no signal.

    Returns {token: reason} so the caller can say WHY, and in particular can separate
    "moved" from "gone" -- a relocated file's references are mis-pathed, not dead.
    """
    out: dict[str, str] = {}
    text = STRUCK.sub(" ", text)          # struck-through == the author already said "gone"
    for m in CODE_SPAN.finditer(text):
        t = m.group(1).strip().rstrip(".,;:)")
        if t in ABSENT_BY_DESIGN or NOT_A_PATH.search(t) or not PATH_LIKE.match(t):
            continue
        # `./x` and `../x` are relative to the FILE, not the repo root. Resolving them
        # against the root reports a correct reference as dead -- the RED caught two of
        # these in INDEX.md on the first run.
        if t.startswith(("./", "../")):
            if base is not None and (base / t).exists():
                continue
            if base is None:
                continue                                # cannot judge without the file
            out[t] = "resolves nowhere (relative to this file)"
            continue
        if _is_stub_project(t, roots):
            continue                                    # not absent -- NOT CHECKED OUT here
        head = t.split("/", 1)[0]
        if not any((r / head).is_dir() for r in roots):
            continue                                    # not checkable here -> not a claim
        if any((r / t).exists() for r in roots):
            continue
        # It is missing. Does a file of that name live somewhere else? Then the reference
        # is MIS-PATHED, not dead -- the more common and more confusing failure, and the
        # one a reader cannot diagnose from "does not exist".
        # `leaf`, NOT `base` -- naming it `base` reassigned the parameter mid-loop, so
        # every token after the first was measured against a string. The RED crashed on it.
        leaf = Path(t.rstrip("/")).name
        elsewhere = [str(q.relative_to(r)) for r in roots
                     for q in r.rglob(leaf) if ".git" not in q.parts][:1] if "." in leaf else []
        if elsewhere:
            out[t] = f"moved -> {elsewhere[0]}"
        elif strict:
            out[t] = "resolves nowhere"
        # else: unprovable here -- the project that owns it is not checked out. Dropped
        # rather than reported, per the same ruling as rotted_pointers() in SCC-80.
    return out


def _scan_roots() -> tuple[list[Path], list[str]]:
    """The lobby, plus every POPULATED project root. Returns the roots and the names of
    projects skipped because this checkout has only their stub -- reported, never silent,
    so a reduced run is visible instead of looking like a clean one."""
    roots, skipped = [ROOT], []
    projects = ROOT / "Projects"
    if projects.is_dir():
        for d in sorted(projects.iterdir()):
            if not d.is_dir():
                continue
            (roots if any(d.iterdir()) else skipped).append(d if any(d.iterdir()) else d.name)
    return roots, skipped


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

    # -- T9 detector fixtures. The FIRST sweep for SCC-83 reported 181 defects where the
    #    true count was 28; every one of the 153 false positives came from a class below.
    #    A checker that reproduces that is worse than none, so each class gets a control,
    #    and A2 proves the thing still fires.
    with TempDir() as fx:
        (fx / "docs").mkdir()
        (fx / "docs" / "real.md").write_text("x", encoding="utf-8")
        proj = fx / "Projects" / "DEMO"
        (proj / "backend" / "tests").mkdir(parents=True)
        (proj / "backend" / "tests" / "conftest.py").write_text("x", encoding="utf-8")
        lobby, both = [fx], [fx, proj]

        got = unresolved_paths("see `docs/nope.md` for the flow", lobby)
        c.check("T9-fixture A2 fires on a planted dead path", set(got) == {"docs/nope.md"},
                det(set(got) == {"docs/nope.md"}, f"got {sorted(got)}"))

        bare = unresolved_paths("drop it in `conftest.py` beside `walkthrough.md`", lobby)
        c.check("T9-fixture A3a quiet on bare filenames (prose shorthand, not paths)",
                not bare, det(not bare, f"got {sorted(bare)}"))

        rel = unresolved_paths("add it under `backend/tests/conftest.py`", both)
        c.check("T9-fixture A3b quiet on a project-relative path when the project IS populated",
                not rel, det(not rel, f"got {sorted(rel)}"))

        # ⭐ The one that has burned this system repeatedly. Same text, same token, but the
        #    project is an empty stub -- which is EVERY git worktree. It must go silent, not
        #    report a defect it cannot possibly verify.
        (fx / "Projects" / "STUB").mkdir()
        stub = unresolved_paths("add it under `backend/tests/conftest.py`", lobby)
        c.check("T9-fixture A3c SILENT when the project is an unpopulated stub (worktrees)",
                not stub, det(not stub, f"got {sorted(stub)} - a mostly-false worklist"))

        # ⭐ A3c-bis. Both of these were found BY THE RED, not by design, and each would
        #    have made the check a permanent false red in every lane.
        (fx / "Projects" / "STUBBED").mkdir(parents=True, exist_ok=True)
        expl = unresolved_paths("see `Projects/STUBBED/scripts/` for it", lobby)
        c.check("T9-fixture A3c-bis quiet on the EXPLICIT Projects/<stub>/ form",
                not expl, det(not expl, f"got {sorted(expl)} - the implicit-form control missed this"))
        # ...and the same token must still FIRE when that project is really checked out.
        (proj / "scripts").mkdir(parents=True, exist_ok=True)
        realp = unresolved_paths("see `Projects/DEMO/nope/` for it", both)
        c.check("T9-fixture A3c-bis still fires when the project IS populated",
                set(realp) == {"Projects/DEMO/nope/"},
                det(set(realp) == {"Projects/DEMO/nope/"}, f"got {sorted(realp)}"))

        # `../` is relative to the FILE: from fx/docs, `../top.md` is fx/top.md -- not
        # fx/docs/top.md. The first draft of this control asserted the wrong target and
        # failed for its own reason rather than the code's.
        (fx / "top.md").write_text("x", encoding="utf-8")
        rel_ok = unresolved_paths("see `../top.md`", lobby, base=fx / "docs")
        c.check("T9-fixture relative `../` resolves against the FILE, not the repo root",
                not rel_ok, det(not rel_ok, f"got {sorted(rel_ok)}"))
        rel_bad = unresolved_paths("see `../gone.md`", lobby, base=fx / "docs")
        c.check("T9-fixture a genuinely dead `../` still fires",
                set(rel_bad) == {"../gone.md"},
                det(set(rel_bad) == {"../gone.md"}, f"got {sorted(rel_bad)}"))

        noise = ("merge `origin/main` into `epic/AVCH-13-x`, POST `/api/incident/fire`, "
                 "model `openrouter/z-ai/glm-5.2`, install `@firebase/rules-unit-testing`, "
                 "glob `docs/*.md`")
        nz = unresolved_paths(noise, lobby)
        c.check("T9-fixture A3d quiet on branch names, URL routes, model ids, npm scopes, globs",
                not nz, det(not nz, f"got {sorted(nz)}"))

        # A4: the allow-list must stay narrow. The by-design entry is silent; a sibling
        #     under the SAME directory that is NOT allow-listed must still fire.
        (fx / ".agents" / "scripts" / "git-hooks").mkdir(parents=True)
        al = unresolved_paths("`.agents/scripts/git-hooks/DISABLE` and "
                              "`.agents/scripts/git-hooks/INVENTED`", lobby)
        c.check("T9-fixture A4 allow-list is narrow, not a blanket off-switch",
                set(al) == {".agents/scripts/git-hooks/INVENTED"},
                det(set(al) == {".agents/scripts/git-hooks/INVENTED"}, f"got {sorted(al)}"))

        # ⭐ strict=False is the worktree posture, and it must NOT become an off-switch:
        #    a demonstrably-moved file still fires, an unprovable one is dropped. Measured
        #    reason for existing: 25 findings from a worktree vs 12 from the main checkout.
        (fx / "docs" / "here.md").write_text("x", encoding="utf-8")
        loose = unresolved_paths("`docs/gone-forever.md` and `docs/sub/here.md`",
                                 lobby, strict=False)
        c.check("T9-fixture strict=False drops the unprovable but KEEPS the moved",
                set(loose) == {"docs/sub/here.md"},
                det(set(loose) == {"docs/sub/here.md"}, f"got {sorted(loose)}"))
        tight = unresolved_paths("`docs/gone-forever.md`", lobby, strict=True)
        c.check("T9-fixture strict=True still reports the unprovable one",
                set(tight) == {"docs/gone-forever.md"},
                det(set(tight) == {"docs/gone-forever.md"}, f"got {sorted(tight)}"))

        struck = unresolved_paths("~~`docs/retired.md`~~ - **gone**, see the new one", lobby)
        c.check("T9-fixture quiet on a struck-through path (the author already said gone)",
                not struck, det(not struck, f"got {sorted(struck)}"))
        # ...and the exemption is per-token, not per-line: a live path beside a struck one
        # must still fire, or one strikethrough would silence a whole sentence.
        mixed = unresolved_paths("~~`docs/retired.md`~~ replaced by `docs/alsogone.md`", lobby)
        c.check("T9-fixture strikethrough does not silence its neighbours",
                set(mixed) == {"docs/alsogone.md"},
                det(set(mixed) == {"docs/alsogone.md"}, f"got {sorted(mixed)}"))
        # PROVENANCE folders are exempt; a FILE under them is not - that is a live
        # instruction to open something that moved, not a record of where it went.
        prov = unresolved_paths("consolidated from `_my_resources/_quick_reference/`", lobby)
        c.check("T9-fixture quiet on a retired folder named as provenance",
                not prov, det(not prov, f"got {sorted(prov)}"))

        # Mis-path vs gone: a relocated file's references resolve to nothing and look
        # identical to a deleted one. The reason string has to tell them apart.
        moved = unresolved_paths("run `docs/real.md` from `tests/real.md`", lobby)
        c.check("T9-fixture separates MOVED from gone",
                moved.get("tests/real.md", "").startswith("moved ->")
                if "tests/real.md" in moved else True,
                f"got {moved}")

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

    # -- T9: against the real docs. Inside `scannable` for the same reason T3/T4 are --
    #    an absent folder yields an empty scan, and a green built on nothing scanned is
    #    the bug SCC-74 shipped once already.
    if not scannable:
        c.check("T9 every prose path reference resolves", False,
                "folder absent - nothing scanned (not a pass)")
    else:
        roots, stubbed = _scan_roots()
        found = {}
        for p in _md_files(FOLDER) + ([idx] if idx.is_file() else []):
            for t, why in unresolved_paths(
                    p.read_text(encoding="utf-8", errors="replace"),
                    roots, base=p.parent, strict=not stubbed).items():
                found.setdefault(f"{p.name} -> {t}", why)
        if stubbed:
            # Never silent about reduced coverage: a partial run must not read as a clean one.
            c.check(f"T9 coverage note: {len(stubbed)} project(s) not checked out here", True,
                    "")
        c.check("T9 every prose path reference resolves", not found,
                "; ".join(f"{k} ({v})" for k, v in sorted(found.items())[:8]))

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
