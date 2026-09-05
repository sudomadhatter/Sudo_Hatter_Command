"""The SOPs + PRDs folder must not rot (SCC-74, 2026-08-10).

`docs/_scc_sops_prds/` holds every procedural document in this system: the pages that tell the
operator what to do and what to type. They were scattered across `_my_resources/_quick_reference/`
and `_my_resources/diagrams_guides/` until this ticket moved them.

  -- WHY THEY ROTTED, WHICH IS THE WHOLE POINT ---------------------------------------------
They did not rot from neglect. They rotted because `_my_resources/` is named in SCAN_IGNORES
(check_maps.py), in DEFAULT_REGEN_IGNORE for the repo-map, and in the code graph's own exclusion
list -- and its own local law says "excluded from repo-map regen + linter scans ... do not fix
that." (SCC-289 removed the centre's code graph entirely; projects keep theirs. The other two
exclusions are live, so the reason below still holds.)
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
T1/T6 pin an explicit 13-doc list. That is deliberate: a 14th doc must be a conscious edit
here. A doc appearing or vanishing without a test change is exactly the drift being guarded
against, and an auto-discovered manifest would rubber-stamp it.

It has moved three times from the 13 SCC-74 brought, and every time the contract did its job --
the suite went red until all three edits (file, INDEX row, EXPECTED) landed together:
    -1  complete-system-overview.md   retired INTO file_folder_structure+maintaining.md (SCC-80)
    -1  md_feedback_setup_guide.md    relocated UP to docs/ -- a machine-setup guide, not an SOP
    +1  sharing_keys_secrets_secure.md  the Keyway secrets-sharing guide (SCC-37)
The second is a scope call, not a demotion: it stays inside docs/, so check_maps.py still
covers it. The line this folder draws is "SOP vs setup," never "watched vs unwatched."

The third is that same line read the other way, and it is worth stating because the obvious
call was the wrong one. A secrets guide LOOKS like setup -- it opens with two install commands,
which is precisely what got md_feedback_setup_guide.md moved OUT. What keeps it here is the
other 90%: onboarding and offboarding a teammate, which environment a person may hold, and the
rotate-after-revoke rule. Those are things you do DURING the work and repeatedly, not once per
machine. Install lives in machine_setup_card.md; the procedure lives here.

Stdlib only, plain ASCII output -- same constraints as its siblings (Windows consoles are cp1252).

This file declares `wf-lint: allow-windows-venv` - the KNOWN_ABSENT map below carries
`.venv/Scripts/python.exe` as a DATA key (a path named in the autopilot PRD, allow-listed
with its reason). It is not an invocation and has no POSIX twin to sit beside it, so the
both-machines check cannot tell it from a hardcode by context alone.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir

ROOT = Path(__file__).resolve().parents[3]
FOLDER_REL = "docs/_scc_sops_prds"
FOLDER = ROOT / FOLDER_REL

# The contract. Renames land here in the same commit that performs them.
EXPECTED = {
    "workflows_testing_SOP.md",          # was _quick_reference/sudo_workflows_testing.md
    "workflows_testing_SOP_changelog.md",  # SCC change history, one line per change (2026-08-21 cleanup)
    "operator_workflows_quickref.md",    # SCC-380: Human flight manual & visual quick-reference
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
    "sharing_keys_secrets_secure.md",     # SCC-37 - the Keyway secrets-sharing guide
    "frontend_UI_design_guide.md",        # House Frontend & UI/UX Design Guide
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
    # SCC-155 retired this on 2026-08-14, renaming it to `/cicd-label-tasks`;
    # workflows_testing_SOP.md section 6 names the old command in its rename note, which is
    # the sentence a reader needs to connect the command they remember to the one that exists.
    "cicd-parallel-check",
    # SCC-367 retired this on 2026-09-01, folding it into `/smh-sync-agents -GlobalsOnly`;
    # workflows_testing_SOP.md's `/smh-sync-agents` entry names it to explain what absorbed it
    # and why the flag is now the only way to run that pass. It was a thin alias for exactly
    # that flag, and its own body already told the operator to prefer the command that remains.
    "smh-slash-command-updating",  # retired by SCC-367 (marker on THIS line: CS-22 B is line-scoped)
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
#
# ⛔ "ROUND 1" and "ROUND 2" below both mean SCC-83, and the distinction is load-bearing
# rather than trivia. ROUND 1 (sha 6cdca82) shipped this check and FAILED code review: its
# call site passed `strict=not stubbed`, a mode that was OFF in every checkout that exists,
# so the primary detection arm was dead code while every gate reported green -- and it was
# "verified" by calling the function with its DEFAULT argument, i.e. against a program that
# was never committed. ROUND 2 is the remediation. Comments naming round 1 are recording
# what was wrong and why the current shape is not an accident; deleting them re-opens the
# door. Full verdict + findings: _artifacts/_main/2026-08-11_scc-83-sop-content-audit/
# walkthrough.md, sections "Code Review (2026-08-11)" and "Round 2 - remediation".
# T3 above reads markdown LINK targets. check_maps.py reads backticked paths, but only
# inside TABLE ROWS. So a path written in a sentence, a bullet or a fenced block is seen
# by nothing -- which is how these docs accumulated references to folders that two landed
# tickets had deleted, with every gate green.
#
# ⛔ SCOPE, stated because an unstated one reads as total coverage: this sees BACKTICKED
# tokens only. Widening the net is not a close call: strip the code spans and the markdown
# links from this folder and a couple of hundred slash-bearing PATH_LIKE tokens remain, and
# they are overwhelmingly PROSE -- `Dev/QA`, `and/or`, `PASS/CONCERNS/FAIL`, `7/7`. So the
# backtick convention IS the boundary, and that -- not a low count -- is the reason.
#
# ⛔ NO EXACT COUNT HERE, deliberately. Round 1 wrote "exactly 2" (fabricated). Round 2
# wrote "242" (real, but method-dependent and already 260 two commits later, because it
# moves with every doc edit). A number that rots is a false claim with a delay on it. If
# you want today's figure, run the probe rather than trusting a comment:
#   strip CODE_SPAN and []() links, then count PATH_LIKE tokens that NOT_A_PATH keeps.
CODE_SPAN = re.compile(r"`([^`\n]+)`")

# ⭐ WHAT ACTUALLY REJECTS A NON-PATH, because knowing this is the difference between
# maintaining the filter and decorating it. Two rules do essentially all the work:
#
#   1. PATH_LIKE's character class. Anything carrying a glob char, whitespace, a leading
#      `/`, or any other punctuation outside [\w.@+-] never matches in the first place.
#      That alone kills globs (`docs/*.md`), URL routes (`/api/incident/fire`) and prose.
#   2. The first-segment rule in unresolved_paths(): the head must name a real directory
#      in some root, or the token is skipped. That kills branch names (`origin/main`),
#      vendor model ids (`openrouter/z-ai/glm-5.2`) and npm scopes (`@firebase/...`),
#      because no such directory exists.
#
# ⛔ Round 1 of SCC-83 shipped SEVEN alternations here as belt-and-braces. Measured against
# the lobby plus all 8 populated projects, SIX could never fire -- and the code review
# proved it the only way that counts: deleting the whole regex left the suite 34/34 GREEN.
# A filter nothing can falsify is not defence in depth, it is decoration that reads as
# coverage. Cut to the one class that is genuinely live, which has a control below.
#
# ⛔ And the ONE class is narrower than it first looks: a TRAILING ellipsis never reaches
# here, because the token is rstrip'd of ".,;:)" before matching -- `docs/...` becomes
# `docs/`, which then fails PATH_LIKE (it needs two segments) and is dropped there, not
# here. (An earlier draft of this line said `docs/` "resolves". Right conclusion, wrong
# mechanism -- and a comment that names the wrong guard sends the next maintainer to the
# wrong line.) Only a MID-path elision (`docs/.../deep.md`) is live. Round 2's
# first fixture used the trailing form and the mutation run caught it: deleting this regex
# still left the suite green. The control below uses the mid-path form.
NOT_A_PATH = re.compile(r"\.\.\.")            # `docs/.../x` -- an elision, not a directory
PATH_LIKE = re.compile(r"^[\w.@+-]+(?:/[\w.@+-]+)+/?$")

# Absent ON PURPOSE. Each entry states why, because an allow-list is one line away from
# being an off-switch -- the DISCUSSED_AS_RETIRED lesson from T4, one tier down.
#
# ⛔ TWO CLASSES, and missing the second one caused a shipped regression. "Absent" is not
# one thing: a path can be absent because it must never exist, or because it does not
# exist YET. Round 1 had no class for the second, so the only way to quieten a correct
# sentence about a file the reader is being told to CREATE was to make the doc wrong --
# and that is exactly what happened to tea_testing_guide.md's decision table, which ended
# up giving two different options the same path. The inversion this list exists to prevent,
# committed by the person maintaining the list.
ABSENT_BY_DESIGN = {
    # -- class 1: must never exist ---------------------------------------------------
    # A kill switch: its ABSENCE is the armed state. Creating it to satisfy a doc would
    # disarm every git hook in the repo. The doc is right to name it.
    ".agents/scripts/git-hooks/DISABLE":
        "kill switch - absence IS the armed state (git-hooks/INDEX.md)",
    # Runtime output. Exists only while an autopilot run is live, and is gitignored, so a
    # clean tree never has it. Naming it is the doc's job; creating it is the run's.
    "_artifacts/_autopilot-run.log":
        "runtime output - written by a live autopilot run, gitignored",
    # Gitignored machine-local file (SCC-392): exists only on machines where local Claude settings
    # are written, gitignored by design, so a clean tree never has it.
    ".claude/settings.local.json":
        "gitignored machine-local file - written by Claude Code per-project, never tracked (SCC-392)",
    # ⭐ PROVENANCE, and the T4 lesson one tier down. These two folders were emptied by
    # SCC-74, and the docs that say "consolidated FROM here" are doing their job. Flagging
    # them pushes an author to delete the sentence explaining where everything went --
    # exactly the inversion DISCUSSED_AS_RETIRED exists to prevent. Note the scope: the
    # FOLDERS are exempt, individual FILES under them are not, because
    # `_my_resources/_quick_reference/jira_manual.md` is not provenance, it is a live
    # instruction to open a file that moved.
    "_my_resources/_quick_reference/": "retired by SCC-74 - named as provenance",
    "_my_resources/diagrams_guides/": "retired by SCC-74 - named as provenance",
    "Projects/Fresh_Workspace_BMAD/backend/requirements.txt":
        "retired submodule path - SCC-403 removed Fresh_Workspace_BMAD from git (tdad_stack_install_guide.md)",
    # Named as the WRONG place, and the sentence depends on it being empty: "without
    # core.hooksPath git reads `.git/hooks`, which is empty - so the gates are silently
    # off." Flagging it asks the author to delete the warning. (Structurally it could never
    # resolve anyway: `.git` is pruned from the index, and in a worktree it is a FILE.)
    ".git/hooks": "named as the empty default core.hooksPath bypasses - the SOP's point",
    # ⭐ THE PAIR IS THE POINT, AND NEITHER HALF CAN EVER RESOLVE (SCC-321). These name the
    # CONVENTION a virtualenv follows - `bin` on POSIX, `Scripts` on Windows - which is the
    # `code-standards` §6 rule that a venv path must be resolved and never hardcoded. Whichever
    # machine reads the doc, the other machine's spelling is absent BY DEFINITION; and neither
    # is a repo-relative path in the first place, since a real one lives at `backend/.venv/…`.
    # So flagging them asks an author to delete the one sentence that stops the next agent
    # hardcoding a Windows path into a script the Mac has to run - the same inversion
    # DISCUSSED_AS_RETIRED exists to prevent, one tier down.
    ".venv/bin": "names the POSIX half of the venv convention - code-standards §6",
    ".venv/Scripts": "names the Windows half of the venv convention - code-standards §6",

    # -- class 2: PROSPECTIVE -- the doc is telling you to create it -------------------
    # Each of these sits in a sentence whose whole job is "make this". Flagging them asks
    # the author to delete the instruction. Narrowness is enforced by the A4 control: a
    # sibling in the same directory that is NOT listed here still fires.
    "_artifacts/opencode/":
        "prospective - the opencode namespace is 'created on first use' by the engine",
    ".agents/rules/testing-standards.md":
        "prospective - tea_testing_guide P9 option A tells the reader to write it",
    "Projects/AGY_AVIATIONCHAT/.agents/rules/testing-standards.md":
        "prospective - the same rule, option B (project-local, the documented default)",
    "_test_scripts/sentry_smoke_test.py":
        "prospective - drill test script referenced in sentry runbooks",
    ".venv/Scripts/python.exe":
        "example / runtime binary path referenced in autopilot PRD",
}

# `~~`path`~~` -- the author has explicitly struck it through as gone. Reporting it asks
# them to delete the very line recording the removal. Found by the RED: line 11 of
# file_folder_structure+maintaining.md already says "**gone**" and was flagged anyway.
#
# ⛔ `[^~\n]*` -- the `\n` is the whole fix. Round 1 used `[^~]*`, which spanned newlines:
# one unbalanced `~~` plus any later strikethrough blanked everything between them, and a
# `~~~` fence was eaten whole. A whole-file off-switch reachable by a typo, inside the gate
# written to stop silent misses. (Latent, not live -- the folder measures 2 and 8
# occurrences, both balanced -- but the failure mode is silent.)
#
# ONE mechanism, not two. Round 2 first bounded the class AND applied it per line; the
# mutation run showed each alone was sufficient, so neither mutation was observable and
# both fixtures were green against a defect. Same disease as the six dead NOT_A_PATH
# alternations above, so it got the same treatment: keep the one that is falsifiable.
# Matches CODE_SPAN's idiom (`[^`\n]+`) -- markdown inline spans do not cross lines.
STRUCK = re.compile(r"~~[^~\n]*~~")

# Directories that are never part of an answer. `worktrees` is the one that matters: the
# round-1 index descended into `.claude/worktrees/` and cited a SIBLING LANE's transient
# copy as the place a file had moved to.
PRUNE = {".git", "node_modules", ".venv", "venv", ".venv_stale", "__pycache__", "dist", "build", ".next",
         ".pytest_cache", ".mypy_cache", ".ruff_cache", ".turbo", "coverage", "worktrees"}


class RootIndex:
    """One pruned walk per root, built once -- paths, leaf names and top-level dirs.

    ⛔ REPLACES a per-token `rglob` that never short-circuited (`[:1]` slices AFTER full
    evaluation). Measured HERE, at 9 roots: **1.06s per unresolved token**, so ~7.4s at this
    folder's current finding count -- against **0.11s for the whole index, built once**
    (20,508 paths). ~69x. (The SCC-83 round-1 review reported +18.3s; that was at its own
    higher defect count and does not reproduce at this one. Repeating it here would ship a
    number I had not measured -- the exact defect finding M4 was about.)

    ⭐ And it fixes a correctness bug the rglob could not: membership here is EXACT-CASE.
    macOS is case-insensitive, so `(root / "DOCS/foo.md").exists()` is True and a
    wrong-case path resolved silently on the Mac while being dead on the PC.
    """

    def __init__(self, root: Path, skip_top: frozenset[str] = frozenset()) -> None:
        self.root = root
        self.paths: set[str] = set()
        self.leaves: dict[str, str] = {}
        self.heads: set[str] = set()
        # ⛔ NOT HANDLING PermissionError, and that is a decision with a reason (SCC-83).
        #    An unreadable directory contributes nothing to the index, so every path under
        #    it reports "resolves nowhere" -- false findings that look real. Round 2 added
        #    an `onerror` recorder for exactly that; round 3 found nothing ever READ the
        #    list, then found the control written for it was vacuous too (it exercised a
        #    Python list, not the consumer). Making it genuinely falsifiable needs
        #    `chmod 000`, which is a NO-OP on Windows -- so the control would pass on the PC
        #    for the wrong reason, in a repo read on both machines. This file's own law is
        #    that machinery nothing can falsify is decoration, and it has already deleted
        #    six NOT_A_PATH alternations and a redundant STRUCK half on that basis. Same
        #    ruling here. Carried as a NAMED limitation in the round-3 verdict instead of
        #    as code that reads like a fix.
        for dirpath, dirnames, filenames in os.walk(root):
            if os.path.relpath(dirpath, root) == "." and skip_top:
                # The lobby does not index `Projects/` -- each project is indexed as its
                # OWN root, so indexing it here walks all eight of them a second time.
                # MEASURED, which is the only reason this is here: from the main checkout
                # the lobby index drops from 20,597 paths to 3,574 (0.12s -> 0.02s). From a
                # lane it changes nothing (the projects are stubs there). It is a
                # double-indexing fix, NOT the lane/main equality fix -- that is the
                # `Projects/<name>/` prefix on the moved-> target below. The directory
                # itself is still recorded, so `Projects/` remains a valid head and path.
                dirnames[:] = [d for d in dirnames if d not in skip_top]
                present = skip_top & set(os.listdir(root))
                self.heads.update(present)
                self.paths.update(present)
                # ...plus ONE level inside, so "is `Projects/<name>` a project this repo
                # knows about?" is answerable without walking it. Without this, a typo'd or
                # renamed project name is indistinguishable from one that is simply not
                # checked out, and both go silent (SCC-83 round-2 review, M-A).
                for d in present:
                    self.paths.update(f"{d}/{c.name}".replace("\\", "/") for c in (root / d).iterdir())
            rel = os.path.relpath(dirpath, root).replace("\\", "/")
            # ⛔ RECORD FIRST, prune SECOND. Pruning before recording made every pruned
            #    directory read as absent, and the docs legitimately name several of them:
            #    `backend/.venv`, `frontend/node_modules`. The first run of this index
            #    reported all three as dead. Pruning is about not DESCENDING; the directory
            #    itself still exists and is still a valid answer.
            for n in dirnames + filenames:
                q = n if rel == "." else f"{rel}/{n}"
                self.paths.add(q)
                self.leaves.setdefault(n, q)
            if rel == ".":
                self.heads.update(dirnames)
            dirnames[:] = [d for d in dirnames if d not in PRUNE and "venv" not in d.lower()]

    def has(self, t: str) -> bool:
        return t.rstrip("/") in self.paths


def build_index(roots: list[Path]) -> dict[Path, RootIndex]:
    """ONE construction site, used by the real run AND by every fixture.

    ⛔ Round 1's defect in miniature: the shipped call site passed `strict=not stubbed`
    while every fixture and every verification took the default. Two programs, one of them
    never exercised. Any per-root asymmetry belongs here, where both paths get it."""
    return {r: RootIndex(r, frozenset({"Projects"}) if i == 0 else frozenset())
            for i, r in enumerate(roots)}


def _project_token(t: str, roots: list[Path], idx: dict[Path, RootIndex]) -> str | None:
    """Classify `Projects/<name>/<rest>`: "skip", "ok", or "miss" (None if not that shape).

    ⛔ Found by the RED, and it is the trap this test exists to avoid. The first-segment
    rule below skips `backend/tests/` because no `backend/` exists here -- but an EXPLICIT
    `Projects/AGY_AVIATIONCHAT/scripts/` sails straight past it, because `Projects/` does
    exist. Without this, any project not checked out on this machine reports a dead
    reference for every path it owns.

    ⛔ TWO JOBS, and round 2's first cut conflated them -- which left a lane and main
    still disagreeing on this one token class, invisibly, because the allow-list happened
    to mask the only example. The old version asked "is `<root>/Projects/<name>` an empty
    directory?", and in a LANE every one of them is, so every explicit project path was
    skipped there and checked from main. Separated:

      - no root is named <name>  -> this machine genuinely cannot see it        -> "skip"
      - otherwise resolve <rest> INSIDE that root, because the token is spelled
        lobby-relative while the project is its own checkout                    -> ok/miss

    Deriving both from `roots` (never from the filesystem directly) is what keeps the
    fixtures honest: they pass their own roots and get the same code path.
    """
    parts = t.rstrip("/").split("/")
    if len(parts) < 2 or parts[0] != "Projects":
        return None
    pr = next((r for r in roots if r.name == parts[1]), None)
    if pr is None:
        # ⛔ "Not checked out" and "no such project" are DIFFERENT, and collapsing them made
        #    the likeliest defect in an explicit project path -- a rename or a typo --
        #    permanently invisible (SCC-83 round-2 review, M-A). A name the lobby knows is
        #    skipped; a name nothing has ever heard of is a dead reference.
        known = any(idx[r].has(f"Projects/{parts[1]}") for r in roots)
        return "skip" if known else "miss"
    return "ok" if (len(parts) == 2 or idx[pr].has("/".join(parts[2:]))) else "miss"


def unresolved_paths(text: str, roots: list[Path], base: Path | None = None,
                     index: dict[Path, RootIndex] | None = None) -> dict[str, str]:
    """Backticked paths in `text` that resolve under none of `roots`.

    `roots` is injected so fixtures drive this without touching the real tree, and so the
    caller decides what "here" means -- the lobby plus each project root.

    ⭐ The first path segment must name a directory that exists in some root, or the token
    is SKIPPED rather than reported. Measured on this very folder: 10 of 11 such hits were
    false. Same ruling as rotted_pointers() in test_memory_store.py -- return nothing
    rather than noise, because a signal people learn to skip is worse than no signal.

    Returns {token: reason} so the caller can say WHY, and in particular can separate
    "moved" from "gone" -- a relocated file's references are mis-pathed, not dead.

    ⛔ THERE IS NO `strict` MODE, and its removal is the point of round 2. Round 1 passed
    `strict=not stubbed`: a GLOBAL switch, off whenever any project was a stub. A lane sees
    9 stubs and main sees 1 (an uninitialised submodule), so it was off EVERYWHERE and the
    "resolves nowhere" arm was dead code in every checkout that exists. Worse, it keyed on
    untracked state -- one stray .DS_Store in a stub would flip a whole run strict and turn
    every lane red. The cure is not a per-token version of the same switch; it is
    _scan_roots() below, which makes coverage identical no matter where you stand.
    """
    out: dict[str, str] = {}
    idx = index if index is not None else build_index(roots)
    text = STRUCK.sub(" ", text)          # struck-through == the author already said "gone"
    for m in CODE_SPAN.finditer(text):
        t = m.group(1).strip().rstrip(".,;:)")
        # This repo is read on a Mac AND a PC, and a doc written on Windows says
        # `docs\foo.md`. PATH_LIKE rejects the backslash, so round 1 skipped those in
        # total silence -- unchecked, and indistinguishable from clean.
        t = t.replace("\\", "/")
        if _by_design(t) or NOT_A_PATH.search(t) or not PATH_LIKE.match(t):
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
        pj = _project_token(t, roots, idx)
        if pj in ("skip", "ok"):
            continue                    # not checked out here / resolves inside that project
        head = t.split("/", 1)[0]
        # ⛔ LOBBY-OWNED namespaces resolve against the LOBBY ONLY (SCC-83 round-2 review,
        #    H-B). Cross-root leniency is deliberate everywhere else -- a lobby doc that
        #    writes `_bmad-output/x.yaml` means the project's, and SCC-85 ruled that "state
        #    the root once" is the fix for those, not 13 red rows. But `any()` also let an
        #    unrelated repo answer for a path only the LOBBY can own, and it silently hid
        #    the single most likely stale reference in this folder: the SOP's own
        #    pre-SCC-74 name, `_my_resources/_quick_reference/sudo_workflows_testing.md`,
        #    resolved because AGY_AVIATIONCHAT happens to have a file at that same relative
        #    path. The allow-list comment above PROMISES that a file under a vacated folder
        #    still fires; it was true by luck for one filename and false for its neighbours.
        cands = [roots[0]] if _lobby_owned(t) else [r for r in roots if head in idx[r].heads]
        if not any(head in idx[r].heads for r in cands):
            continue                                    # not checkable here -> not a claim
        if any(idx[r].has(t) for r in cands):
            continue
        # It is missing. Does a file of that name live somewhere else? Then the reference
        # is MIS-PATHED, not dead -- the more common and more confusing failure, and the
        # one a reader cannot diagnose from "does not exist".
        # `leaf`, NOT `base` -- naming it `base` reassigned the parameter mid-loop, so
        # every token after the first was measured against a string. The RED crashed on it.
        leaf = Path(t.rstrip("/")).name
        # Report the target relative to the LOBBY, whichever root it was found in --
        # `Projects/<name>/...` for a project hit. An answer whose spelling depends on
        # which checkout you ran from is an answer you cannot paste into a doc.
        elsewhere = []
        if "." in leaf:
            # Same scope as the resolution above: if only the lobby may ANSWER for this
            # token, only the lobby may say where it went. Otherwise a vacated-folder
            # reference is told it "moved" to a project's identically-named copy -- true as
            # a statement, useless as advice, and the class of output round 1 acted on.
            for i, r in enumerate(cands if _lobby_owned(t) else roots):
                if leaf in idx[r].leaves:
                    rel = idx[r].leaves[leaf]
                    elsewhere.append(rel if i == 0 else f"Projects/{r.name}/{rel}")
        if not elsewhere:
            # ⛔ FRESH CLONE (SCC-83 round-3 review, H1). These docs legitimately carry
            #    project-relative paths -- SCC-85 ruled "state the root once" -- and those
            #    resolve only because a cloned project answers for them. Clone the command
            #    centre WITHOUT `--recurse-submodules` and nothing answers: 13 findings, exit
            #    1, run_all RED, on a correct machine. That is the false worklist SCC-87's
            #    AC3 forbids in those words, and the plan's A3c fixture claims to prevent.
            #
            #    So a token that could belong to an un-cloned project is UNPROVABLE here,
            #    not dead -- dropped, and counted in the coverage note so the reduced run is
            #    visible. On a fully-cloned machine `uncloned` is 0 and this never fires,
            #    which is why it is NOT the round-1 `strict` mode returning: that switch was
            #    off in every checkout that existed, this one is off in every checkout that
            #    is complete. A LOBBY-OWNED token is never unprovable -- no project can own
            #    it -- so H-B's guarantee is untouched.
            #    ⛔ AND NO PER-TOKEN CLASSIFIER, because I could not build an honest one.
            #    Three discriminators were tried and MEASURED, all three failing:
            #      - "not lobby-owned"        -> also suppresses `docs/gone.md`, a real defect
            #      - "head not tracked in git" -> `_bmad-output` and `docs` are both tracked
            #      - "lobby lacks the parent"  -> `_bmad-output/sudo-tests.yaml` has its parent
            #    `_bmad-output/sudo-tests.yaml` is structurally identical to `docs/gone.md`;
            #    only intent separates them, and no rule reads intent. Guessing would trade a
            #    false RED for a false GREEN, and this file exists because a silent miss is
            #    the worse of the two. So the check stays strict and the CALLER makes the
            #    failure actionable -- see the `git submodule update --init` hint in T9.
            out[t] = "resolves nowhere"
        elif len(elsewhere) == 1:
            out[t] = f"moved -> {elsewhere[0]}"
        else:
            # ⛔ SAY when the answer is a guess (SCC-83 round-2 review, M-C). `leaves` is a
            #    setdefault map over an os.walk, so with several same-named files the target
            #    is whichever the walk reached first -- and round 1 shipped a doc regression
            #    by acting on exactly that output as if it were an instruction. A reader who
            #    is told there are four candidates checks; one handed a single path pastes.
            # ASCII only in anything PRINTED -- see the module docstring. run_all captures
            # each child through a pipe, so Python encodes with the locale's preferred
            # encoding; on a cp1252 Windows console a `!` is fine and a `⚠` raises
            # UnicodeEncodeError and takes the whole file down (SCC-83 round-3 review, H2).
            out[t] = (f"moved -> {elsewhere[0]} (!! {len(elsewhere)} files share this name "
                      f"- verify before using)")
    return out


# Why _main_checkout() fell back to ROOT, or "" when it resolved. Read by T9's check so a
# degraded resolution is reported rather than passing as a healthy one (SCC-83).
_MAIN_CHECKOUT_FALLBACK: str = ""


def cp1252_offenders(rows: list[tuple[str, bool, str]]) -> list[str]:
    """Emitted strings a cp1252 console cannot print. A function ONLY so it is fixturable --
    T10 is a meta-check over the other checks, so it cannot catch its own removal, and this
    file has already shipped fixes nothing could falsify (SCC-83)."""
    out = []
    for name, _ok, detail in rows:
        for label, s in (("name", name), ("detail", detail)):
            try:
                s.encode("cp1252")
            except UnicodeEncodeError as e:
                out.append(f"{label} {name[:40]!r}: {e.object[e.start:e.end]!r}")
    return out


def uncloned_note(stubbed: list[str]) -> str:
    """The remedy appended to a T9 failure when some project is not cloned here.

    A separate function ONLY so it can be fixtured: built inline it was unreachable from
    any control, and this file has already shipped two 'fixes' that nothing could falsify
    (SCC-83). Empty when everything is cloned, so a complete machine sees a clean message.
    """
    if not stubbed:
        return ""
    return (f" | NOTE: {len(stubbed)} project(s) not cloned here ({', '.join(stubbed)}) - "
            f"project-relative paths cannot resolve without them. Run "
            f"`git submodule update --init` and re-run BEFORE treating the above as defects.")


def t9_inconclusive(found: dict, stubbed: list[str], env: dict) -> bool:
    """Can T9's failure be believed in THIS checkout? (SCC-118)

    ⛔ Read the round-3 ruling above `uncloned_note` before touching this. That ruling —
    "the check stays STRICT, and the failure carries its own remedy" — is CORRECT and is not
    being reversed. It rests on one assumption that was true of every checkout that existed
    when it was written: **the remedy is actionable.** Tell a laptop
    `git submodule update --init` and it complies, so a red there is a real red.

    A CI runner is the case that assumption never met. 4 of the 9 declared submodules are
    PRIVATE, and the runner holds no credential for them — supplying one would mean parking a
    token with read access to every private repo inside a PUBLIC repo's Actions, to satisfy a
    doc-link check. The remedy is not merely unrun there; it is unavailable. A gate that goes
    permanently red on a correct state is the disease that ruling named, and this is that
    state, reached from the other direction.

    So the strictness is unchanged everywhere it can mean anything, and narrows ONLY where
    all three hold at once:

      found    there is something to report at all
      stubbed  projects really are missing from this checkout — with a COMPLETE clone the
               remedy is irrelevant and any finding is real, in CI exactly as anywhere else
      env      this is a runner, declared by the platform, not inferred from a symptom

    Keyed on the environment rather than on the shape of the findings on purpose: there is no
    honest per-token classifier separating "dead" from "unreachable" (see `unresolved_paths`),
    and inventing one is how this file previously shipped fixes nothing could falsify. An env
    var is a fact the platform states, and a control can set it both ways — which C-T9a/b/c do.
    """
    return bool(found) and bool(stubbed) and bool(env.get("GITHUB_ACTIONS") or env.get("CI"))


def _lobby_owned(t: str) -> bool:
    """Namespaces only the LOBBY can own, so a project checkout must not answer for them.

    Scoped to `VACATED` on purpose: those folders were emptied by SCC-74, so every live
    reference into them is by definition a lobby path that moved -- and a project having
    the same relative layout is a coincidence, never an answer. Widening this to every
    shared head would flag the 13 project-relative paths SCC-85 already ruled on."""
    return any(t.startswith(v + "/") for v in VACATED)


def _by_design(t: str) -> bool:
    """Allow-list membership, insensitive to a trailing slash on either side -- `docs/x`
    and `docs/x/` name the same thing and an exact-string match said otherwise."""
    return t.rstrip("/") in {k.rstrip("/") for k in ABSENT_BY_DESIGN}


def _main_checkout() -> Path:
    """The checkout that owns `Projects/`, asked of GIT rather than of the CWD.

    ⭐ THE FIX FOR THE ROUND-1 FAIL, and the same cure as the repo-map label bug: a tool
    that asks the CWD what repo it is in gets a DIFFERENT ANSWER PER LANE. `Projects/*`
    are separate gitignored repos, so `git worktree add` leaves them as empty stubs -- a
    lane saw 9 stubs, main saw 1. Round 1 built a `strict` mode to cope with the
    difference, and the mode swallowed the entire check.

    A worktree's .git FILE points at <main>/.git/worktrees/<lane>, and --git-common-dir
    resolves to <main>/.git regardless. Its parent is the checkout holding the projects.
    Measured at the shipping sha: a lane and main report an IDENTICAL finding set -- 0 and 0
    with the allow-list on, 8 and 8 with every exemption lifted, keys AND values equal both
    ways. (Round 1 was 0 and 0 shipped but 14 and 1 under the mode it never actually ran in.
    An earlier draft of this line said "1 and 1"; that was a projection written before the
    doc fixes landed, and it shipped as a present-tense measurement. Third time in this
    ticket, hence the no-unverified-numbers rule at the top of the T9 section.)

    ⛔ THE FALLBACK IS NAMED, NEVER SILENT (SCC-83, clean-code gate). Falling back to ROOT
    in a LANE reinstates the exact lane-dependent coverage this function exists to remove --
    H1's failure mode returning through the error path. `except Exception: pass` would hide
    git being off PATH, a timeout, or a permissions error behind a result that merely looks
    reduced. The reason is recorded for the T9 check below to print, so a degraded
    resolution is legible instead of being indistinguishable from a healthy one.
    """
    global _MAIN_CHECKOUT_FALLBACK
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--git-common-dir"],
                             capture_output=True, text=True, timeout=10)
        if out.returncode == 0 and out.stdout.strip():
            g = Path(out.stdout.strip())
            if not g.is_absolute():
                g = ROOT / g
            _MAIN_CHECKOUT_FALLBACK = ""
            return g.resolve().parent
        _MAIN_CHECKOUT_FALLBACK = (f"git rev-parse --git-common-dir rc={out.returncode} "
                                   f"{(out.stderr or '').strip()[:120]}")
    except Exception as e:                               # git absent, timeout, permissions
        _MAIN_CHECKOUT_FALLBACK = f"{type(e).__name__}: {e}"
    return ROOT                                          # not a git tree -> best effort


def _scan_roots() -> tuple[list[Path], list[str]]:
    """The lobby, plus every POPULATED project root. Returns the roots and the names of
    projects this machine has only as a stub -- named, never silent, because a partial run
    that reads like a clean one is the failure this whole file exists to prevent."""
    roots, skipped = [ROOT], []
    projects = _main_checkout() / "Projects"
    if projects.is_dir():
        for d in sorted(projects.iterdir()):
            if not d.is_dir():
                continue
            # ⛔ `.git`, NOT "is it non-empty" (SCC-83 round-2 review, H-A). Every project
            #    here is its own repo or submodule, so `.git` is exactly the "is this
            #    checked out" signal. `any(d.iterdir())` looked equivalent and was not:
            #    Finder writes `.DS_Store` into any folder a human opens -- there is
            #    already one in `Projects/` itself -- and one such file would have promoted
            #    an uninitialised submodule to a "populated root", after which
            #    `tdad_stack_install_guide.md`'s correct reference into it goes hard RED in
            #    run_all on a machine where nothing is wrong. That is the SAME
            #    untracked-state trigger this ticket deleted `strict` to be rid of; the
            #    replacement had quietly re-armed it one layer down.
            if (d / ".git").exists():
                roots.append(d)
            else:
                skipped.append(d.name)
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

        # ⛔ NAMED FOR WHAT IT ACTUALLY CONTROLS. Round 1 called this the stub control and
        #    mkdir'd a stub for it -- but `backend/...` never reaches _is_stub_project(),
        #    which only handles the explicit `Projects/<name>/` form. The mkdir was inert
        #    and the comment claimed otherwise. What is really under test is the
        #    FIRST-SEGMENT rule: no `backend/` in any root, so the token is not a claim.
        seg = unresolved_paths("add it under `backend/tests/conftest.py`", lobby)
        c.check("T9-fixture A3c first-segment rule: silent when no root has that head",
                not seg, det(not seg, f"got {sorted(seg)} - a mostly-false worklist"))

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
        # ⛔ ...and the token is spelled LOBBY-relative while the project is its own
        #    checkout, so it has to resolve INSIDE that root. Without this the lane's empty
        #    `Projects/<name>/` made every explicit project path unresolvable there while
        #    main resolved it -- a lane/main disagreement that the allow-list happened to
        #    mask on the only real example. Nothing found it until this control existed.
        inside = unresolved_paths("see `Projects/DEMO/backend/tests/conftest.py`", both)
        c.check("T9-fixture an explicit project path resolves INSIDE that project's root",
                not inside, det(not inside, f"got {sorted(inside)} - the lane would disagree "
                                            f"with main on every Projects/<name>/ token"))

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

        # ⭐ A3d, REBUILT SO IT CAN FAIL. The round-1 version asserted this same silence and
        #    was worthless: every token in it was already killed by PATH_LIKE or the
        #    first-segment rule, so deleting NOT_A_PATH entirely left the suite 34/34 GREEN.
        #    The elision class is the one alternation that survived measurement -- and here
        #    its head (`docs/`) DOES exist, so NOT_A_PATH is the only thing that can hold
        #    it. Delete that regex and this control goes red, which is the whole job.
        elide = unresolved_paths("under `docs/.../deep.md` somewhere", lobby)
        c.check("T9-fixture A3d NOT_A_PATH holds the elision class (head exists, so only it can)",
                not elide, det(not elide, f"got {sorted(elide)}"))

        # ...and the classes round 1 listed are silenced by a DIFFERENT mechanism. Pinned
        # here so nobody re-adds them believing the filter is what stops them.
        noise = ("merge `origin/main` into `epic/AVCH-13-x`, POST `/api/incident/fire`, "
                 "model `openrouter/z-ai/glm-5.2`, install `@firebase/rules-unit-testing`, "
                 "glob `docs/*.md`")
        nz = unresolved_paths(noise, lobby)
        c.check("T9-fixture A3d branch/route/vendor/scope/glob quiet via PATH_LIKE + first-segment",
                not nz, det(not nz, f"got {sorted(nz)}"))

        # A4: the allow-list must stay narrow. The by-design entry is silent; a sibling
        #     under the SAME directory that is NOT allow-listed must still fire.
        (fx / ".agents" / "scripts" / "git-hooks").mkdir(parents=True)
        al = unresolved_paths("`.agents/scripts/git-hooks/DISABLE` and "
                              "`.agents/scripts/git-hooks/INVENTED`", lobby)
        c.check("T9-fixture A4 allow-list is narrow, not a blanket off-switch",
                set(al) == {".agents/scripts/git-hooks/INVENTED"},
                det(set(al) == {".agents/scripts/git-hooks/INVENTED"}, f"got {sorted(al)}"))

        # ⛔ THE ROUND-1 FAIL, fixtured. There is no `strict` mode any more: a dead path is
        #    reported wherever you stand. The old pair of controls asserted that a mode
        #    worked, while the shipped call site pinned that mode OFF in every checkout
        #    that exists -- green fixtures guarding dead code.
        gone = unresolved_paths("`docs/gone-forever.md`", lobby)
        c.check("T9-fixture the 'resolves nowhere' arm EXECUTES (no mode can switch it off)",
                set(gone) == {"docs/gone-forever.md"},
                det(set(gone) == {"docs/gone-forever.md"}, f"got {sorted(gone)}"))

        struck = unresolved_paths("~~`docs/retired.md`~~ - **gone**, see the new one", lobby)
        c.check("T9-fixture quiet on a struck-through path (the author already said gone)",
                not struck, det(not struck, f"got {sorted(struck)}"))
        # ...and the exemption is per-token, not per-line: a live path beside a struck one
        # must still fire, or one strikethrough would silence a whole sentence.
        mixed = unresolved_paths("~~`docs/retired.md`~~ replaced by `docs/alsogone.md`", lobby)
        c.check("T9-fixture strikethrough does not silence its neighbours",
                set(mixed) == {"docs/alsogone.md"},
                det(set(mixed) == {"docs/alsogone.md"}, f"got {sorted(mixed)}"))

        # ⛔ H2: an UNBALANCED `~~` must not reach across lines. With the round-1 regex the
        #    stray marker below paired with the one two lines down and blanked everything
        #    between -- a whole-file off-switch reachable by a typo. 6 real references
        #    vanished when this was measured.
        stray = ("~~`docs/one.md`~~ retired\n"
                 "a stray ~~ marker left by a typo\n"
                 "`docs/survivor.md` must still be checked\n"
                 "~~`docs/two.md`~~ also retired\n")
        sv = unresolved_paths(stray, lobby)
        c.check("T9-fixture an unbalanced ~~ cannot blank the lines below it",
                set(sv) == {"docs/survivor.md"},
                det(set(sv) == {"docs/survivor.md"}, f"got {sorted(sv)}"))
        fence = "~~~\nsee `docs/infence.md`\n~~~\n"
        fv = unresolved_paths(fence, lobby)
        c.check("T9-fixture a ~~~ fence is not swallowed as a strikethrough",
                set(fv) == {"docs/infence.md"},
                det(set(fv) == {"docs/infence.md"}, f"got {sorted(fv)}"))

        # PROVENANCE folders are exempt; a FILE under them is not - that is a live
        # instruction to open something that moved, not a record of where it went.
        # ⛔ The mkdir is LOAD-BEARING and must come FIRST: without `_my_resources/` on
        #    disk the first-segment rule kills the token before the allow-list is consulted,
        #    and this control passes no matter what the allow-list says. Round 2 shipped it
        #    eight lines too late -- documented that exact trap for the NEXT control and
        #    missed it here (SCC-83 round-2 review, M-B).
        (fx / "_my_resources").mkdir()
        prov = unresolved_paths("consolidated from `_my_resources/_quick_reference/`", lobby)
        c.check("T9-fixture quiet on a retired folder named as provenance",
                not prov, det(not prov, f"got {sorted(prov)}"))
        # ...and the allow-list is written without a trailing slash on some entries and with
        # one on others. Both spellings name the same thing; an exact-string match did not.
        slash = unresolved_paths("see `_my_resources/diagrams_guides`", lobby)
        c.check("T9-fixture allow-list ignores a trailing-slash mismatch",
                not slash, det(not slash, f"got {sorted(slash)}"))

        # ⛔ Mis-path vs gone. Round 1's version was `X if 'tests/real.md' in moved else True`
        #    -- a ternary whose else-branch is literally True, and `tests/` did not exist so
        #    the token never reached the arm at all. The ONE working arm had zero coverage;
        #    mutating it survived. Assert the set AND the reason.
        (fx / "tests").mkdir()
        moved = unresolved_paths("run `docs/real.md` from `tests/real.md`", lobby)
        ok_mv = (set(moved) == {"tests/real.md"}
                 and moved["tests/real.md"] == "moved -> docs/real.md")
        c.check("T9-fixture separates MOVED from gone, and names where it went",
                ok_mv, det(ok_mv, f"got {moved}"))

        # L3: this repo is read on a Mac AND a PC. A Windows-authored `docs\nope.md` failed
        #     PATH_LIKE and was skipped in silence -- unchecked, yet indistinguishable from
        #     clean. Normalising the separator makes it a real check.
        win = unresolved_paths("open `docs\\nope.md` to see", lobby)
        c.check("T9-fixture a Windows-separator path is checked, not silently skipped",
                set(win) == {"docs/nope.md"},
                det(set(win) == {"docs/nope.md"}, f"got {sorted(win)}"))

        # L4: macOS is case-insensitive, so Path.exists() said `docs/case.md` was fine when
        #     only `docs/Case.md` was on disk -- green on the Mac, dead on the PC. Exact-case
        #     set membership is what makes this reachable at all.
        (fx / "docs" / "Case.md").write_text("x", encoding="utf-8")
        case = unresolved_paths("open `docs/case.md`", lobby)
        c.check("T9-fixture wrong CASE is a finding (the Mac's FS would have hidden it)",
                "docs/case.md" in case, det("docs/case.md" in case, f"got {sorted(case)}"))

        # ⛔ H3, and the reason PRUNE has `worktrees` in it. The round-1 index descended into
        #    `.claude/worktrees/` and named a SIBLING LANE's transient copy as the place a
        #    file had moved to -- advice that points at a directory which will not exist
        #    tomorrow. Un-prune and this control goes red, which is what makes the prune set
        #    a decision rather than a comment. (Nothing asserted this until the mutation run
        #    showed un-pruning was invisible.)
        ghost = fx / ".claude" / "worktrees" / "other-lane" / "docs"
        ghost.mkdir(parents=True)
        (ghost / "ghost.md").write_text("x", encoding="utf-8")
        (fx / "elsewhere").mkdir()
        wt = unresolved_paths("see `elsewhere/ghost.md`", lobby)
        ok_wt = wt.get("elsewhere/ghost.md") == "resolves nowhere"
        c.check("T9-fixture never cites a sibling lane's worktree as where a file went",
                ok_wt, det(ok_wt, f"got {wt} - a moved-> into .claude/worktrees/ is advice "
                                  f"pointing at a directory that will not exist tomorrow"))

    # ⭐⭐ THE ROUND-1 FAIL AS A FIXTURE. Everything above runs in ONE checkout, and a suite
    #     that only ever stands in one place cannot see the defect that shipped: an answer
    #     that changes depending on where you stand. Round 1 "confirmed" this out of band
    #     and got it wrong; round 2 found a SECOND asymmetry the same out-of-band probe
    #     missed, because an allow-list entry happened to mask the only example. So the
    #     equality itself is asserted here -- same docs, same project root, two lobbies:
    #     one with `Projects/DEMO` populated (the main checkout) and one where it is an
    #     empty stub (every git worktree). The two must agree exactly.
    with TempDir() as fxm, TempDir() as fxl:
        demo = fxm / "Projects" / "DEMO"
        (demo / "src").mkdir(parents=True)
        (demo / "src" / "moved.md").write_text("x", encoding="utf-8")
        (fxl / "Projects" / "DEMO").mkdir(parents=True)      # the lane: an empty stub
        for b in (fxm, fxl):
            (b / "docs").mkdir()

        txt = ("see `Projects/DEMO/src/moved.md`, `Projects/DEMO/gone.md` "
               "and `docs/moved.md`")
        as_main = unresolved_paths(txt, [fxm, demo])
        as_lane = unresolved_paths(txt, [fxl, demo])
        same = as_main == as_lane
        c.check("T9-fixture a lane and the main checkout return the IDENTICAL answer",
                same, det(same, f"main={as_main} lane={as_lane}"))

        # ...and the moved-> target must be pastable: spelled from the LOBBY, so it names
        # the same file whichever root the index happened to find it in.
        tgt = as_main.get("docs/moved.md")
        ok_t = tgt == "moved -> Projects/DEMO/src/moved.md"
        c.check("T9-fixture the moved-> target is lobby-relative, not root-relative",
                ok_t, det(ok_t, f"got {tgt!r} - a bare 'src/moved.md' names no real file"))

        # The lobby must not index `Projects/` -- each project is its own root, so doing
        # both walks every project twice (measured: 20,597 paths vs 3,574 from main). This
        # asserts the PROPERTY rather than a wall-clock number, because a timing assertion
        # in a test suite is a flake waiting to happen.
        li = build_index([fxm, demo])[fxm]
        ok_i = "Projects" in li.paths and "Projects/DEMO/src/moved.md" not in li.paths
        c.check("T9-fixture the lobby index records Projects/ without duplicating it",
                ok_i, det(ok_i, f"{len(li.paths)} paths; project contents indexed twice"))
        # ...but it must record ONE level in, or "no such project" and "not cloned here"
        # are indistinguishable and both go silent (round-2 review, M-A).
        ok_k = "Projects/DEMO" in li.paths
        c.check("T9-fixture the lobby index knows WHICH projects exist",
                ok_k, det(ok_k, "a typo'd project name would be silently unchecked"))
        unknown = unresolved_paths("see `Projects/NoSuchProject/x.md`", [fxm, demo])
        c.check("T9-fixture a project name nothing knows about is a FINDING, not a skip",
                set(unknown) == {"Projects/NoSuchProject/x.md"},
                det(set(unknown) == {"Projects/NoSuchProject/x.md"},
                    f"got {sorted(unknown)} - a rename is the likeliest defect here"))

        # ⛔ H-A: "populated" is decided by `.git`, never by "is the folder non-empty".
        #    Finder writes .DS_Store into any folder a human opens - there is already one in
        #    the real `Projects/` - and under the non-empty test one such file promotes an
        #    uninitialised submodule to a root, turning a correct reference into it hard RED
        #    on a machine where nothing is wrong. That is the same untracked-state trigger
        #    this ticket deleted `strict` to be rid of (round-2 review, H-A).
        (fxm / "Projects" / "NOTCLONED").mkdir()
        (fxm / "Projects" / "NOTCLONED" / ".DS_Store").write_bytes(b"\x00" * 8)
        noise_ok = not (fxm / "Projects" / "NOTCLONED" / ".git").exists()
        seen = unresolved_paths("see `Projects/NOTCLONED/backend/req.txt`", [fxm, demo])
        c.check("T9-fixture OS noise (.DS_Store) does not promote an uncloned project",
                noise_ok and not seen,
                det(noise_ok and not seen, f"got {sorted(seen)} - a stray Finder file "
                                           f"would red every lane"))

    # ⛔⛔ H-B (round-2 review): cross-root leniency must NOT answer for a namespace only the
    #     lobby can own. This hid the single most likely stale reference in the folder --
    #     the SOP's own pre-SCC-74 name under `_my_resources/_quick_reference/` -- because
    #     AGY_AVIATIONCHAT happens to carry a file at the same relative path. The allow-list
    #     comment PROMISED a file under a vacated folder still fires; it was true by luck
    #     for one filename and false for its neighbours, and nothing tested it.
    with TempDir() as fxl, TempDir() as fxp:
        (fxl / VACATED[0]).mkdir(parents=True)          # the emptied lobby folder
        (fxp / VACATED[0]).mkdir(parents=True)          # a project with the SAME layout
        (fxp / VACATED[0] / "moved_away.md").write_text("x", encoding="utf-8")
        (fxl / "docs").mkdir()
        (fxp / "docs").mkdir()
        (fxp / "docs" / "shared.md").write_text("x", encoding="utf-8")

        masked = unresolved_paths(f"open `{VACATED[0]}/moved_away.md`", [fxl, fxp])
        # Assert the REASON too: if the relocation search still ranges over every root, the
        # finding fires but points at the project's copy as "where it went" -- true as a
        # statement, useless as advice, and the shape round 1 acted on.
        ok_m = masked.get(f"{VACATED[0]}/moved_away.md") == "resolves nowhere"
        c.check("T9-fixture a project copy cannot answer for a vacated LOBBY path",
                ok_m, det(ok_m, f"got {masked} - this is the exact silent miss H-B found "
                                f"on the SOP's own pre-SCC-74 name"))
        # ...and the leniency itself must SURVIVE, or 13 project-relative paths SCC-85
        # already ruled on ("state the root once") come back as red rows.
        lenient = unresolved_paths("see `docs/shared.md`", [fxl, fxp])
        c.check("T9-fixture cross-root leniency still holds outside vacated folders",
                not lenient, det(not lenient, f"got {sorted(lenient)} - SCC-85's 13 would return"))

    # ⛔⛔ _scan_roots() ITSELF, driven end to end (round-2 review, H-A structural note).
    #     Every control above hands `unresolved_paths` a roots list it built by hand, so the
    #     ONE function that decides what "here" means -- and which produced the round-1
    #     failure -- had no test at all. Round 1 shipped an argument no fixture exercised;
    #     round 2 nearly shipped the function that chooses the argument. ROOT and
    #     _main_checkout are module state, so they are swapped and restored in a finally.
    with TempDir() as fxr:
        (fxr / "Projects" / "CLONED" / ".git").mkdir(parents=True)
        (fxr / "Projects" / "NOTCLONED").mkdir(parents=True)
        (fxr / "Projects" / "NOISY").mkdir(parents=True)
        (fxr / "Projects" / "NOISY" / ".DS_Store").write_bytes(b"\x00" * 8)
        _root, _mc = ROOT, _main_checkout
        try:
            globals()["ROOT"] = fxr
            globals()["_main_checkout"] = lambda: fxr
            sr_roots, sr_stubbed = _scan_roots()
        finally:
            globals()["ROOT"] = _root
            globals()["_main_checkout"] = _mc
        got_r, got_s = sorted(p.name for p in sr_roots[1:]), sorted(sr_stubbed)
        ok_sr = got_r == ["CLONED"] and got_s == ["NOISY", "NOTCLONED"]
        c.check("T9-fixture _scan_roots counts .git as checked-out and OS noise as not",
                ok_sr, det(ok_sr, f"roots={got_r} stubbed={got_s} - expected ['CLONED'] / "
                                  f"['NOISY','NOTCLONED']; a stray .DS_Store must not "
                                  f"promote an uninitialised submodule to a root"))

    # ⛔⛔ THE FRESH CLONE (round-3 review, H1), asserted rather than assumed. Clone without
    #     `--recurse-submodules` and the docs' project-relative paths have nothing to
    #     resolve against: measured, 13 findings on a correct machine. SCC-87's AC3 asks for
    #     "silence, not noise" there, and round 2 marked it satisfied on two controls that
    #     never ran the scan with nothing cloned.
    #
    #     ⛔ The check is deliberately NOT silenced -- see unresolved_paths for the three
    #     discriminators that were tried and measured failing. A guess would trade a false
    #     RED for a silent MISS. What IS asserted: the failure names the cause and the one
    #     command that fixes it, so the operator is never left staring at unfixable rows.
    with TempDir() as fxfc:
        (fxfc / "docs").mkdir()
        (fxfc / "backend").mkdir()                  # a project-shaped head the lobby also has
        fresh = unresolved_paths("run `backend/tests/conftest.py` and see `docs/gone.md`",
                                 [fxfc])
        both_flagged = set(fresh) == {"backend/tests/conftest.py", "docs/gone.md"}
        # ...and the REMEDY is what makes that acceptable. Asserted against the SAME
        # function the check calls -- not a copy of the string, which would assert nothing.
        remedy = uncloned_note(["AGY_AVIATIONCHAT", "NEXgen-VR-Director"])
        ok_fc = (both_flagged
                 and "git submodule update --init" in remedy
                 and "AGY_AVIATIONCHAT" in remedy
                 and uncloned_note([]) == "")        # silent on a fully-cloned machine
        c.check("T9-fixture a fresh clone still reports, and the failure carries its remedy",
                ok_fc, det(ok_fc, f"found={sorted(fresh)} remedy={remedy!r}"))

        # ── C-T9a/b/c: the narrowing added by SCC-118, driven directly ────────────────
        # Three cases, because the change is only defensible if the FIRST one holds: the
        # gate must be untouched on a developer machine, which is the only place its
        # remedy works. Asserting only the CI case would prove the softening and not the
        # strictness -- the shape of fix this file has shipped twice and had to undo.
        FOUND = {"doc.md -> a/b.md": "resolves nowhere"}
        STUB = ["AGY_AVIATIONCHAT"]
        c.check("C-T9a a developer checkout still HARD FAILS (remedy works there)",
                not t9_inconclusive(FOUND, STUB, {}),
                "no CI marker -> the ruling above uncloned_note stands, unchanged")
        c.check("C-T9b a runner with projects uncloned is INCONCLUSIVE, not a defect",
                t9_inconclusive(FOUND, STUB, {"GITHUB_ACTIONS": "true"})
                and t9_inconclusive(FOUND, STUB, {"CI": "true"}),
                "4 of 9 submodules are private; a runner cannot clone them")
        c.check("C-T9c a runner with a COMPLETE checkout still HARD FAILS",
                not t9_inconclusive(FOUND, [], {"GITHUB_ACTIONS": "true"}),
                "nothing is missing, so the finding is real wherever it was found")
        c.check("C-T9d nothing found is never 'inconclusive'",
                not t9_inconclusive({}, STUB, {"GITHUB_ACTIONS": "true"}),
                "a clean scan reports clean, not unanswerable")

    # T10 is a meta-check over the other rows, so it cannot catch its own removal. Its
    # detector is fixtured here instead: it must FIRE on a star and stay QUIET on an em dash
    # (which IS in cp1252, so banning all non-ASCII would be wrong).
    star, dash = "⭐", "—"
    fires = cp1252_offenders([(f"name {star}", True, ""), ("ok", True, f"detail {star}")])
    quiet = cp1252_offenders([(f"name {dash}", True, "plain ascii")])
    ok_cp = len(fires) == 2 and quiet == []
    c.check("T10-fixture the cp1252 detector fires on U+2B50 and is quiet on an em dash",
            ok_cp, det(ok_cp, f"fires={fires} quiet={quiet}"))

    # ⛔ A token headed by a PRUNED directory must still be checkable: `heads` is recorded
    #    before the prune for exactly that reason, and nothing tested the heads half.
    with TempDir() as fxp2:
        (fxp2 / "node_modules").mkdir()
        pruned_head = unresolved_paths("see `node_modules/gone.md`", [fxp2])
        ok_ph = set(pruned_head) == {"node_modules/gone.md"}
        c.check("T9-fixture a token headed by a pruned dir is still checked",
                ok_ph, det(ok_ph, f"got {sorted(pruned_head)} - heads recorded after the "
                                  f"prune silently skips every such token"))

    # ⛔ M-C: a `moved ->` target is whichever same-named file os.walk reached first. With
    #    more than one candidate it must SAY so -- round 1 shipped a doc regression by
    #    treating exactly this output as an instruction.
    with TempDir() as fxa, TempDir() as fxb:
        for b in (fxa, fxb):
            (b / "docs").mkdir()
            (b / "docs" / "dupe.md").write_text("x", encoding="utf-8")
        (fxa / "elsewhere").mkdir()
        many = unresolved_paths("see `elsewhere/dupe.md`", [fxa, fxb])
        ok_many = "share this name" in many.get("elsewhere/dupe.md", "")
        c.check("T9-fixture an ambiguous moved-> target says it is ambiguous",
                ok_many, det(ok_many, f"got {many} - a single path reads as an instruction"))

    # ⛔ M-D: CODE_SPAN's `\n` is the same guard STRUCK gets three fixtures for, and it had
    #    none. An unbalanced backtick would re-pair every span after it and silently swallow
    #    real tokens -- the identical silent-miss shape, one line above the fix for it.
    with TempDir() as fxc:
        (fxc / "docs").mkdir()
        spill = ("a stray ` backtick opened here\n"
                 "`docs/still-checked.md` must still be seen\n"
                 "and ` another one closes far below\n")
        sp = unresolved_paths(spill, [fxc])
        ok_sp = set(sp) == {"docs/still-checked.md"}
        c.check("T9-fixture an unbalanced backtick cannot swallow the spans below it",
                ok_sp, det(ok_sp, f"got {sorted(sp)}"))

    # ⭐ And the mechanism behind A3d's second row, pinned in its own tree so the assertion
    #    above cannot be read as "NOT_A_PATH stops branch names". It does not; the absence
    #    of a directory by that name does. Create one and the token becomes a real claim.
    with TempDir() as fx2:
        (fx2 / "origin").mkdir()
        br = unresolved_paths("merge `origin/main` into it", [fx2])
        c.check("T9-fixture branch names are held by the FIRST-SEGMENT rule, not the filter",
                set(br) == {"origin/main"},
                det(set(br) == {"origin/main"}, f"got {sorted(br)} - if quiet, something "
                                                f"else is filtering and the comment lies"))

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
        # Built ONCE for the whole scan, not per token. See RootIndex: the round-1 rglob
        # cost ~1.06s per unresolved token and walked into sibling lanes' worktrees.
        index = build_index(roots)
        found, blocked = {}, []
        for p in _md_files(FOLDER) + ([idx] if idx.is_file() else []):
            txt = p.read_text(encoding="utf-8", errors="replace")
            for t, why in unresolved_paths(txt, roots, base=p.parent, index=index).items():
                found.setdefault(f"{p.name} -> {t}", why)
            for s in stubbed:
                if f"`Projects/{s}/" in txt:
                    blocked.append(f"{p.name} -> Projects/{s}/...")
        # ⛔ A NOTE, DELIBERATELY NOT A CHECK -- and the reason is worth writing down.
        #    Round 1 emitted this through c.check(..., True, "") : a print dressed as a
        #    passing check, inflating the count and reading as coverage (L5). Round 2 first
        #    tried the opposite -- FAIL when a doc reaches into a project this machine
        #    cannot see -- and that fired immediately on tdad_stack_install_guide.md naming
        #    `Projects/Fresh_Workspace_BMAD/backend/requirements.txt`. That WAS a declared
        #    submodule (.gitmodules, `ignore = all`) deliberately left uninitialised -- it left
        #    git entirely on 2026-09-04 (SCC-403), and the same shape still holds for the nine
        #    that remain: the doc is right, the machine is right, and nothing is broken. A gate that goes
        #    permanently red on a correct state is the same disease as one that never fires.
        #    So: named, counted, and attributed to the docs that depend on it -- loud enough
        #    that a partial run cannot read as a clean one, without asserting a defect.
        if stubbed:
            print(f"     (T9 coverage: {len(stubbed)} project(s) not cloned here: "
                  f"{', '.join(stubbed)}"
                  + (f"; {len(blocked)} explicit reference(s) into them unverified: "
                     + "; ".join(sorted(set(blocked))[:3]) if blocked else "; unreferenced")
                  + " - run `git submodule update --init` for full coverage)")
        # ⛔ An unreadable directory contributes nothing to the index, so every path under it
        #    reports "resolves nowhere" -- a FALSE finding that looks exactly like a real
        #    one. Round 2 recorded these and then never read the list: a fix that was
        #    written, shipped, and consumed by nothing (SCC-83 round-3 review). Reported
        #    alongside the findings, because it is the reason to distrust them.
        # ⛔ A FAILURE THAT CARRIES ITS OWN REMEDY (SCC-83 round-3 review, H1). Clone this
        #    repo without `--recurse-submodules` and the docs' project-relative paths --
        #    which SCC-85 ruled are written that way on purpose -- have nothing to resolve
        #    against: 13 findings on a correct machine. The check stays STRICT (see
        #    unresolved_paths: no honest per-token classifier exists), so instead the
        #    failure says WHY it might be lying and what one command fixes it. Silence
        #    would be a silent miss; noise without a remedy is how a gate gets ignored.
        detail = "; ".join(f"{k} ({v})" for k, v in sorted(found.items())[:8])
        if t9_inconclusive(found, stubbed, os.environ):
            # Loud, attributed, and NOT counted as a pass — the exact failure mode the round-1
            # `c.check(..., True, "")` had. Nothing green is printed here; the check is simply
            # not asked, because in this checkout it has no answer. See t9_inconclusive.
            print(f"[SIGNAL] T9 cannot be answered on this runner: {len(found)} unresolved "
                  f"path(s) with {len(stubbed)} project(s) uncloned and no credential to "
                  f"clone them. NOT proven absent, NOT proven dead.")
            print(f"[SIGNAL]   {detail}")
            print("[SIGNAL] T9 gates on a developer checkout, where the remedy works: "
                  "`git submodule update --init`.")
        else:
            c.check("T9 every prose path reference resolves", not found,
                    detail + (uncloned_note(stubbed) if found else ""))
        # ⭐ B1: the property whose absence let the round-1 fail hide. Project roots come
        #    from git's COMMON dir, so a lane and main see the same set. In a worktree
        #    ROOT/.git is a FILE; the resolved main checkout's is always a directory.
        mc = _main_checkout()
        gitdir_ok = (mc / ".git").is_dir() and not _MAIN_CHECKOUT_FALLBACK
        c.check("T9 project roots resolve to the MAIN checkout, not this lane", gitdir_ok,
                det(gitdir_ok,
                    f"_main_checkout()={mc}"
                    + (f" - FELL BACK: {_MAIN_CHECKOUT_FALLBACK}" if _MAIN_CHECKOUT_FALLBACK
                       else " has no .git directory")))

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
    #
    #    `quick_links.md` (SCC-156): the OPERATOR's own signpost, rolled in on their order
    #    2026-08-14 -- links INTO docs/_scc_sops_prds/, no procedure content. That is the
    #    pointer shape SCC-74 wants _my_resources to hold, same as INDEX.md. The allowlist
    #    stays by-NAME on purpose (this file's own doctrine: an addition is a conscious
    #    edit); procedural content under any other name still fails here.
    left = sorted(p.relative_to(ROOT).as_posix()
                  for v in VACATED for p in (ROOT / v).rglob("*.md")
                  if p.name not in ("INDEX.md", "quick_links.md")
                  ) if any((ROOT / v).is_dir() for v in VACATED) else []
    c.check("T6 no procedural docs in _my_resources", not left,
            det(not left, f"{len(left)} left: " + "; ".join(left[:4])
                          + (" ..." if len(left) > 4 else "")))

    # -- T7: one copy of the doc that existed twice with 508 differing lines.
    #    Filter the RELATIVE path, never p.parts -- this repo is checked out inside
    #    .claude/worktrees/<lane>/, so the absolute parts contain "worktrees" for every file
    #    and an absolute-path filter silently excludes the entire tree (found 0 of 2 copies).
    copies = []
    # ⛔ PRUNE THE WALK — A RESULT-FILTER DOES NOT PROTECT IT. `ROOT.rglob(...)` ENTERS every
    # directory before the test below can reject it, so it descended into
    # `Projects/<p>/.claude/worktrees/<lane>/backend/.venv/Lib/site-packages/torch-*.dist-info/
    # licenses/third_party/kineto/.../civetweb/examples/rest` and died with WinError 3 (Windows
    # refuses paths over 260 chars). That crash took the WHOLE FILE down, and a file that dies
    # has run nothing — the suite reported it as one red among many rather than as unrun.
    # `os.walk` lets the same names be dropped from `dirnames`, so they are never entered.
    # The exclusion set is the original four plus the module's own PRUNE (a real second copy of
    # this doc cannot live in `.venv`/`node_modules`), so the assertion is unchanged.
    skip = {".git", "_artifacts", "Projects", "worktrees"} | PRUNE
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in skip]
        if "autopilot_bmad_dev_loop.md" in filenames:
            copies.append((Path(dirpath) / "autopilot_bmad_dev_loop.md")
                          .relative_to(ROOT).as_posix())
    ok = len(copies) == 1
    c.check("T7 exactly one autopilot_bmad_dev_loop.md", ok, det(ok, f"copies: {sorted(copies)}"))

    # -- T10: everything this file PRINTS must survive a cp1252 console. LAST, so it sees
    #    every row above -- and it checks the emitted strings rather than the source, so a
    #    decorative character in a comment is free while one in a check name or a runtime
    #    detail is caught.
    #
    #    ⛔ The docstring has promised "plain ASCII output" since SCC-74 and nothing enforced
    #    it. This diff then put a U+2B50 in a check NAME and a U+26A0 in a finding detail.
    #    run_all captures each child through a PIPE, so Python encodes with the locale's
    #    preferred encoding -- cp1252 on a stock Windows box -- and the whole file dies with
    #    UnicodeEncodeError before reporting anything. Reproduced on the Mac with
    #    PYTHONIOENCODING=cp1252 (SCC-83 round-3 review, H2). This repo is read on BOTH
    #    machines and the PC was not reachable to test on, which is exactly when a machine
    #    check beats a promise in a docstring.
    unencodable = cp1252_offenders(c.rows)
    c.check("T10 all printed output survives a cp1252 (Windows) console", not unencodable,
            det(not unencodable, f"{len(unencodable)} string(s): " + "; ".join(unencodable[:3])))

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
