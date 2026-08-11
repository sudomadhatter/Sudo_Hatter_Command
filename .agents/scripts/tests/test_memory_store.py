"""The memory store is read by every platform now (SCC-65) — so its index is a context cost
paid by every session, and its integrity is what recall is worth.

AGENTS.md §7 routes EVERY model on EVERY machine through `_artifacts/_memory/MEMORY.md` at
session start. That contract holds only while three things stay true, and each one rots
silently without a gate:

  * the index stays under 25 KB — it is loaded whole into every session, so growth past it
    means narrative crept into what must stay a one-line-per-memory index (content belongs
    in the memory FILES). Raised from 20 KB by operator ruling 2026-08-09 (SCC-69): the 20 KB
    figure was inherited from the active-context budget by analogy and never measured against
    a real store. The first full audit ground-truthed all 145 memories, freed only 633 bytes,
    and proved the rest are load-bearing — a cap that forces deletion of true things is the
    wrong instrument. ⛔ This is still not an agent's call to make: never raise it yourself;
  * every index line points at a file that exists — a dead link is recall of nothing;
  * every memory file has an index line — an unindexed memory is invisible to the exact
    mechanism that makes memory worth writing (`README.md` exempt by name: it documents
    the store, it is not a memory).

⚠ THE TRIGGER (SCC-68). Upkeep used to hang off `/update-maps-indexes` Step 3.9, and so it
never ran: nobody reaches for a MAP workflow because memory feels heavy, and the store filled
to 99.5% of cap with the remedy parked in an unrelated command. Now the gate that already runs
in `run_all` on every close-out, on every machine, raises the alarm itself — at TRIGGER_PCT,
BELOW the cap, while the run still passes. A trigger that only fires at 100% is useless: its
first signal would already be a red blocking unrelated work.

This script cannot ask anything — it runs headless, inside hooks, inside `run_all`; it has
stdout and an exit code. So the ask is a two-part contract: the block below is the imperative,
and root `AGENTS.md` §7 binds every platform to STOP and ask the operator when it appears.
The candidate worklist is computed here so the audit starts from evidence rather than a blank
page — but they are SIGNALS, never verdicts.

Deliberately NOT here: any auto-compaction. Deciding which memories merge or retire is
judgment work — `/memory-audit` proposes it per item and the operator approves. A cheap model
summarizing away a hard-won pitfall is silent, permanent loss of exactly the recall the store
exists for. This gate makes rot loud; it never edits a memory.

Checks run against fixtures both ways (fire on defects, stay quiet on look-alikes), then
against the REAL store — the real store passing is the gate; the fixtures prove the
detector is alive.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir

# _harness puts SCRIPTS on sys.path, so the lobby's own scripts import as top-level modules.
# SCC-73: reuse check_maps' allowlist parser rather than adding a fourth copy of it.
import check_maps  # noqa: E402  (must follow the _harness path insert)

INDEX_CAP = 25 * 1024
TRIGGER_PCT = 0.90          # audit is DUE here — below the cap, on purpose (see module docstring)
BODY_SOFT_CAP = 4 * 1024    # a memory this long is usually narrative that wants compressing
EXEMPT = {"MEMORY.md", "README.md"}
CLOSED_MARKS = ("CLOSED", "RETIRED", "FIXED", "SUPERSEDED", "⛔")

REAL_STORE = SCRIPTS.parent.parent / "_artifacts" / "_memory"
# The repo REAL_STORE lives in - rotted_pointers() resolves memory paths against it,
# and against the sibling project repo, because a memory about AGY names AGY's paths.
REPO_ROOT = REAL_STORE.parent.parent

# ── SCC-73 Phase 1: the store is TWO-TIER ────────────────────────────────────────────────────
# The lobby store is the INBOX - every platform writes here, because the Claude harness bakes an
# absolute per-workspace path into its memory instruction and no repo law can redirect it. What
# settles into project-only truth is RELOCATED to that project's own store by /smh-memory-audit,
# per item, on the operator's word. Two consequences this file has to enforce:
#
#   1. a relocated memory leaves the lobby index, so the index must SIGNPOST where it went, or
#      relocation is indistinguishable from deletion for every session that loads the index;
#   2. project stores are then load-bearing, so they need the same integrity contract the lobby
#      has always had. AGY's 15 memories were gated by NOTHING until this landed.
POINTER_HEADING = "## Project stores"


def maintained_project_names(repo: Path) -> list[str] | None:
    """Projects the home base keeps in sync, from the TRACKED allowlist. None = file ABSENT.

    Read the allowlist, never `Projects/*` on disk. The allowlist is a committed file present in
    every checkout; `Projects/` is an EMPTY STUB in every `git worktree` - which is where nearly
    all work happens. A pointer contract asserted against directories would therefore pass
    vacuously in exactly the place it needs to hold, and a check that cannot fail where you work
    is not a check.

    Delegates to `check_maps.maintained_projects()` - ONE parser for this file, not a fourth. Its
    None-vs-set distinction is the load-bearing part and the reason not to hand-roll this: an
    absent allowlist must be a LOUD failure, never an empty list. An empty list silently disarms
    both tiers and prints output identical to a normal worktree run (`[COVERAGE] 0`, no `[SKIP]`
    lines) - the fail-open this module exists to make impossible."""
    names = check_maps.maintained_projects(repo)
    return None if names is None else sorted(names)


def _section(text: str, heading: str) -> str | None:
    """The heading's OWN section - bounded at the next `## `, not 'the rest of the file'.

    `text.split(heading)[1]` is the whole remainder. `## Project stores` sits near the top of a
    21 KB index, so ~99% of every memory row in the file would count as being 'in' the section,
    and one future row mentioning a project path would anaesthetize the check permanently."""
    if heading not in text:
        return None
    rest = text.split(heading, 1)[1]
    out: list[str] = []
    for line in rest.splitlines():
        if line.startswith("## "):
            break
        out.append(line)
    return "\n".join(out)


def _names_a_project(section: str, name: str) -> bool:
    """Is `name` listed as its OWN entry - not merely a substring of a longer sibling?

    Raw containment lets `NEXgen-VR-Director`'s row satisfy an allowlist entry for `NEXgen`, so a
    genuinely missing signpost reads as present. Latent with today's two names; armed the moment
    anyone adds a name that prefixes another - which the allowlist header openly invites."""
    return re.search(rf"^\s*[-*].*(?<![\w-]){re.escape(name)}(?![\w-])", section, re.M) is not None


def project_stores(repo: Path) -> tuple[list[Path], list[str]]:
    """(stores to check, skips to NAME) - never a silent skip.

    Two absences are correct and must not read as defects, and neither may pass unmentioned:
      * the submodule is not checked out - true in every worktree and every fresh clone;
      * the project is checked out but has no memory store yet - a new project has no memories,
        which is a beginning, not rot. NEXgen-VR-Director is exactly this today: it has the
        directory and no index, and a fan-out that called `check_store()` on it would report
        "the store is unreadable by contract" and red `run_all` for every unrelated lane.
    Skips come back as sentences because a fan-out that skips silently reports green while
    checking nothing - the same vacuous pass this module exists to prevent."""
    stores: list[Path] = []
    skips: list[str] = []
    names = maintained_project_names(repo)
    if names is None:
        # LOUD, never an empty list. Absent allowlist = both tiers disarmed, and the output would
        # be indistinguishable from a healthy worktree run except for two lines nobody watches for.
        return [], ["ALLOWLIST MISSING: .agents/maintained-projects.txt is gone - the project tier "
                    "is checking NOTHING and cannot say which projects it should have checked"]
    for name in names:
        root = repo / "Projects" / name
        store = root / "_artifacts" / "_memory"
        if (store / "MEMORY.md").is_file():
            stores.append(store)
        elif not (root / ".git").exists():
            skips.append(f"{name}: submodule not checked out - not gated here "
                         f"(git submodule update --init -- Projects/{name})")
        else:
            skips.append(f"{name}: no memory store yet - nothing to gate")
    return stores, skips


def pointer_problems(store: Path, repo: Path) -> list[str]:
    """The lobby index must signpost every maintained project's store.

    This is the half of relocation that makes it safe. Moving a memory out of the lobby is only
    a compaction if something is left behind saying where it went; without the signpost it is
    silent removal from every session's view, and the failure mode of this store has always been
    "the agent repeated a mistake it had a memory for"."""
    names = maintained_project_names(repo)
    if names is None:
        return [f"cannot verify `{POINTER_HEADING}`: .agents/maintained-projects.txt is missing, "
                f"so there is no list of projects this index is required to signpost"]
    if not names:
        return []
    section = _section(index_text(store), POINTER_HEADING)
    if section is None:
        return [f"MEMORY.md has no `{POINTER_HEADING}` section - project memories relocate out "
                f"of this index, and with no signpost left behind they are invisible to every "
                f"session that loads it"]
    return [f"`{POINTER_HEADING}` never names `{n}` - that project's store is unreachable from "
            f"the one index every platform loads" for n in names if not _names_a_project(section, n)]


# The back-pointer must be recognisable by a token that CANNOT also describe the project's own
# store. `_artifacts/_memory` fails that test outright: it is the project's own path too, so a
# project index saying nothing but "my memories live in _artifacts/_memory/" would satisfy a check
# meant to prove it points somewhere ELSE. This sentinel names the lobby unambiguously.
LOBBY_BACKPOINTER = "Sudo_Hatter_Command/_artifacts/_memory/"


def backpointer_problems(repo: Path) -> list[str]:
    """Each project store points BACK at the lobby, or a project-launched lane is blind.

    Lanes launched inside a project read that repo's store and never load the lobby's - so the
    workflow law and the cross-cutting hazards (the two-machine trap, backticks executing in
    `-m`) are absent for exactly the sessions doing the most dangerous work. One line fixes it."""
    stores, _ = project_stores(repo)
    return [f"`{s.parent.parent.name}`'s MEMORY.md never names the lobby store "
            f"(`{LOBBY_BACKPOINTER}`) - a lane launched inside that project reads only its own "
            f"store, so cross-project law and hazards are invisible there"
            for s in stores if LOBBY_BACKPOINTER not in index_text(s)]


# ── Why the two-tier checks are ADVISORY, and it is not a hedge ───────────────────────────────
# `Projects/<name>` is a separate repo with its own armed commit-msg hook: AGY answers to AVCH keys
# ONLY, so an SCC lane physically cannot commit a fix to a project store - the hook rejects it. A
# hard failure here would red `run_all` in the lobby for a defect nobody standing in the lobby is
# allowed to repair, and block every unrelated lane until someone opened a ticket in another
# project. That is the precise failure `rotted_pointers()` documents one screen up, and the reason
# it is advisory too.
#
# So the split is by OWNERSHIP, not by importance:
#   * HARD FAIL  - the lobby index and its pointer section. This repo owns them; fixable here.
#   * ADVISORY   - project-store integrity and back-pointers. Another repo owns them; reported on
#                  every run so the rot is loud, never blocking so the lobby stays workable.
# The durable fix for a project store is a gate INSIDE that project (AVCH work, owed). Until then
# this is the only detection that exists for AGY's memories, which had none at all before SCC-73.
def project_store_signals(repo: Path) -> list[str]:
    """Cross-repo memory health, as SIGNALS for the audit worklist - never a blocking failure."""
    out: list[str] = []
    stores, _ = project_stores(repo)
    for s in stores:
        probs = check_store(s)
        if probs:
            out.append(f"project store `{s.parent.parent.name}`: {len(probs)} integrity "
                       f"problem(s) - {probs[0][:90]} (fix in that repo, under its own key)")
    out += [f"{p} (fix in that repo, under its own key)" for p in backpointer_problems(repo)]
    return out


def index_text(store: Path) -> str:
    idx = store / "MEMORY.md"
    return idx.read_text(encoding="utf-8") if idx.is_file() else ""


def check_store(store: Path) -> list[str]:
    """Every problem as one human sentence; empty list = the contract holds."""
    problems: list[str] = []
    idx = store / "MEMORY.md"
    if not idx.is_file():
        return [f"no MEMORY.md index in {store} - the store is unreadable by contract"]
    text = idx.read_text(encoding="utf-8")
    size = len(text.encode("utf-8"))
    if size > INDEX_CAP:
        problems.append(
            f"MEMORY.md is {size} bytes (cap {INDEX_CAP}) - every session on every "
            f"platform pays this; run /memory-audit to retire and compress (the 90% "
            f"trigger fired before this and was not acted on)")
    links = {m.split("/")[-1] for m in re.findall(r"\]\(([^)#]+\.md)\)", text)}
    files = {p.name for p in store.glob("*.md")} - EXEMPT
    for dead in sorted(links - files):
        problems.append(f"MEMORY.md links `{dead}` but no such file is in the store - "
                        f"recall of nothing; fix or delete the line")
    for orphan in sorted(files - links):
        problems.append(f"`{orphan}` has no MEMORY.md line - an unindexed memory is "
                        f"invisible to every session; add a one-line pointer")
    for p in sorted(store.glob("*.md")):
        if p.name in EXEMPT:
            continue
        head = p.read_text(encoding="utf-8", errors="replace")[:800]
        if not head.startswith("---") or "description:" not in head:
            problems.append(f"`{p.name}`: no frontmatter description - recall relevance "
                            f"is judged from it; add the ---/description header")
    return problems


def audit_due(store: Path) -> bool:
    """True once the index crosses TRIGGER_PCT of the cap. Separate from check_store because
    this is NOT a failure - the run still passes; it is a standing request for judgment work."""
    return len(index_text(store).encode("utf-8")) >= INDEX_CAP * TRIGGER_PCT


# In-repo path shapes a memory body may name. A rotted one teaches a dead move, and NOTHING
# caught it before SCC-80: check_store() validates the INDEX (links, orphans, cap) and never
# reads a body's paths, while audit_due() triggers on SIZE alone. A store can sit at 79% of cap,
# pass every check, and still route every reader to a folder that was deleted months ago -
# which is exactly what the 2026-08-10 audit found by hand, 15 times over.
_REPO_ROOTS = ("_my_resources/", "docs/", ".agents/", "_artifacts/", ".claude/",
               ".opencode/", ".githooks/", "_bmad/", "_bmad-output/")
_BACKTICK_PATH = re.compile(r"`([_.A-Za-z0-9][\w./+-]*/[\w./+-]+)`")
# Absences that are CORRECT. Each is a by-design gap, not rot:
#   - a retired surface the memory's own subject is the removal of
#   - a kill-switch you CREATE to disable something (absent = armed)
#   - gitignored payloads (secrets, PII exports, machine-local caches) that must never be committed
_BY_DESIGN = (".claude/commands", ".claude/rules", ".opencode/skills", "sudo-dev-story-tests",
              "sudo-target-resolution", "sudo-code-review", "close-task-merge-tree/SKILL.md",
              "sprint-dependency-map", "_secrets/", "git-hooks/DISABLE", "auth_keys",
              "_my_resources/backups", ".maps-journal")


def _is_placeholder(path: str) -> bool:
    """`epic-N`, `<name>`, `x/Y` - a template, not a claim about a real file.

    The `-N` / `-X` SUFFIX form matters as much as a bare segment: `epic-N` is how this system
    writes "any epic", and treating it as a real path makes the detector cry wolf on correct prose."""
    return any(len(s) == 1 or s in {"N", "X"} or s.startswith("<")
               or re.search(r"[-_](N|X)$", s) for s in path.split("/"))


def rotted_pointers(store: Path, repo: Path, sibling: Path | None = None) -> dict:
    """Memory bodies naming an in-repo path that resolves NOWHERE. {file: {paths}}.

    Resolution is tried against `repo` AND `sibling` (a project repo) because memories about a
    project legitimately name that project's paths. Anything gitignored is skipped: it is absent
    from a clean checkout on purpose. A path that resolves in either repo, is gitignored, is a
    template, or is a by-design absence is NOT rot.

    ADVISORY on purpose - returned as a signal, never a hard failure. `Projects/` is not populated
    in a `git worktree` checkout, so sibling resolution is unavailable in exactly the place most
    work happens; failing there would make this red for a reason the author cannot fix."""
    # If the sibling project repo is not CHECKED OUT, this check cannot ground-truth anything:
    # `Projects/<name>/` is an empty stub in every `git worktree`, so every project path would
    # read as rot. Measured: 10 of 11 hits were false that way. Report NOTHING rather than a
    # worklist that is mostly wrong - a signal with that hit-rate is one people learn to skip,
    # and this file's whole thesis is that a gate nobody reads is a gate that checks nothing.
    if sibling is not None and (not sibling.is_dir() or not any(sibling.iterdir())):
        return {}

    out: dict[str, set] = {}
    for f in sorted(store.glob("*.md")):
        if f.name in EXEMPT:
            continue
        for m in _BACKTICK_PATH.finditer(f.read_text(encoding="utf-8", errors="replace")):
            path = m.group(1).rstrip("/.,)")
            if not path.startswith(_REPO_ROOTS) or _is_placeholder(path):
                continue
            if any(b in path for b in _BY_DESIGN):
                continue
            if (repo / path).exists() or (sibling and (sibling / path).exists()):
                continue
            try:
                if subprocess.run(["git", "check-ignore", "-q", path], cwd=repo,
                                  capture_output=True).returncode == 0:
                    continue
            except OSError:
                pass
            out.setdefault(f.name, set()).add(path)
    return out


def audit_signals(store: Path, repo: Path | None = None) -> list[str]:
    """A worklist for /memory-audit, derived mechanically so the audit opens on evidence.

    ⛔ `repo` is EXPLICIT and defaults to None - cross-repo signals are opt-in per call. It was a
    module global for one commit and that was a blocking bug: a hermetic fixture store, holding
    nothing but its own two files, inherited AGY's missing back-pointer and failed the fixture
    assertion "a healthy store produces NO candidates". In a worktree `Projects/` is empty so it
    passed; on `main` it would have turned `run_all` red for every unrelated lane, over a defect
    this repo is forbidden to commit a fix for - verbatim the failure the ownership split below
    exists to prevent, reintroduced by the wiring. A function that reads live state a caller never
    handed it cannot be tested hermetically, and this one is called from inside its own test file.

    SIGNALS, NOT VERDICTS. Every one of these can be legitimate - a `CLOSED` row whose lesson
    is still load-bearing stays; a dangling `[[link]]` is the sanctioned way to mark a memory
    worth writing later. The audit ground-truths each against the live repo. Nothing here is
    an instruction to delete."""
    out: list[str] = []
    text = index_text(store)

    closed = [ln.strip() for ln in text.splitlines()
              if ln.lstrip().startswith("-") and any(m in ln for m in CLOSED_MARKS)]
    if closed:
        out.append(f"{len(closed)} index row(s) marked {'/'.join(CLOSED_MARKS[:3])} - closed "
                   f"work whose lesson may compress to one line (or retire outright)")

    names = {p.stem for p in store.glob("*.md")} - {Path(e).stem for e in EXEMPT}
    dangling: set[str] = set()
    big: list[str] = []
    for p in sorted(store.glob("*.md")):
        if p.name in EXEMPT:
            continue
        body = p.read_text(encoding="utf-8", errors="replace")
        dangling |= {w for w in re.findall(r"\[\[([^\]]+)\]\]", body) if w not in names}
        if len(body.encode("utf-8")) > BODY_SOFT_CAP:
            big.append(p.name)
    if dangling:
        out.append(f"{len(dangling)} dangling [[link]] target(s) ({', '.join(sorted(dangling)[:4])}"
                   f"{'...' if len(dangling) > 4 else ''}) - either a forward reference (fine, "
                   f"leave it) or danglers left behind by a retirement (fix the source)")
    if big:
        out.append(f"{len(big)} memory file(s) over {BODY_SOFT_CAP // 1024} KB "
                   f"({', '.join(big[:3])}{'...' if len(big) > 3 else ''}) - long bodies are "
                   f"usually narrative; the lesson is what earns the space")

    if repo is not None:
        out += project_store_signals(repo)

    rotted = rotted_pointers(store, REPO_ROOT, REPO_ROOT / "Projects" / "AGY_AVIATIONCHAT")
    if rotted:
        n = sum(len(v) for v in rotted.values())
        out.append(f"{n} rotted path pointer(s) across {len(rotted)} memory file(s) "
                   f"({', '.join(sorted(rotted)[:3])}{'...' if len(rotted) > 3 else ''}) - the "
                   f"lesson may still be true while the path it names is gone; correct, do not retire")
    return out


def audit_block(store: Path, repo: Path | None = None) -> str:
    """The imperative the agent must surface. Loud on purpose - this is the whole trigger.

    `repo` threads through to audit_signals: the REAL block wants cross-repo candidates, fixtures
    must not inherit them. Same opt-in contract, same reason (see audit_signals)."""
    size = len(index_text(store).encode("utf-8"))
    pct = size * 100 / INDEX_CAP
    lines = [
        "",
        "!! ---------------------------------------------------------------- !!",
        "!!  MEMORY AUDIT DUE                                                 !!",
        "!! ---------------------------------------------------------------- !!",
        f"   MEMORY.md is {size} bytes - {pct:.0f}% of the {INDEX_CAP}-byte cap "
        f"({INDEX_CAP - size} bytes of headroom left).",
        "   Every session on every platform loads this index before doing any work.",
        "",
        "   ACTION REQUIRED OF THE AGENT READING THIS: stop and ask the operator",
        "   whether to run /memory-audit now. Do not compact anything yourself, and",
        "   do not raise the cap - compaction is judgment work and it is the",
        "   operator's call, per AGENTS.md section 7.",
        "",
        # Printed HERE rather than filed in a ticket nobody re-reads, because this block is the
        # one moment the question is live. SCC-69 ground-truthed all 145 memories and freed 633
        # bytes: compaction is spent as a lever, and an audit run expecting to find slack will
        # find none and cost a session. If relocation has also run dry, the remaining move is
        # structural, and the agent reading this needs to know that before it starts.
        "   ⚠ IF THE AUDIT FINDS NOTHING LEFT TO COMPACT OR RELOCATE: the remedy is",
        "   SCC-73 Phase 2 (thin root index + per-category files), NOT another audit.",
        "   Compaction was measured spent in SCC-69 - 145 memories, 633 bytes freed.",
    ]
    sig = audit_signals(store, repo)
    if sig:
        lines.append("")
        lines.append("   Candidates the audit will ground-truth against the live repo:")
        lines += [f"     - {s}" for s in sig]
    lines += ["!! ---------------------------------------------------------------- !!", ""]
    return "\n".join(lines)


def write(store: Path, name: str, text: str) -> None:
    store.mkdir(parents=True, exist_ok=True)
    (store / name).write_text(text, encoding="utf-8")


MEMO = "---\nname: a-fact\ndescription: one fact\n---\n\nThe fact.\n"


def sized_index(pct: float) -> str:
    """An index padded to `pct` of the cap - the pad is a comment line so it stays a valid index."""
    head = "# Index\n- [A fact](a-fact.md) - hook\n"
    return head + "<!-- " + "x" * int(INDEX_CAP * pct - len(head) - 8) + " -->\n"


def main() -> int:
    c = Cases("memory store")

    # ── fixture positive control: a correct tiny store is CLEAN ──
    with TempDir() as t:
        s = t / "mem"
        write(s, "a-fact.md", MEMO)
        write(s, "MEMORY.md", "# Index\n- [A fact](a-fact.md) - hook\n")
        write(s, "README.md", "just a readme, no frontmatter\n")
        got = check_store(s)
        c.check("clean fixture store passes (README exempt by name)", got == [], str(got)[:150])
        c.check("a small index does NOT trigger the audit", not audit_due(s), "")

    # ── each defect fires, separately ──
    with TempDir() as t:
        s = t / "mem"
        write(s, "MEMORY.md", "- [gone](never-written.md) - hook\n")
        got = check_store(s)
        c.check("a dead index link fires", any("never-written.md" in p for p in got),
                str(got)[:150])

    with TempDir() as t:
        s = t / "mem"
        write(s, "a-fact.md", MEMO)
        write(s, "MEMORY.md", "# Index\n(no links yet)\n")
        got = check_store(s)
        c.check("an unindexed memory file fires", any("a-fact.md" in p and "no MEMORY.md line"
                in p for p in got), str(got)[:150])

    with TempDir() as t:
        s = t / "mem"
        write(s, "a-fact.md", "no frontmatter at all\n")
        write(s, "MEMORY.md", "- [A fact](a-fact.md) - hook\n")
        got = check_store(s)
        c.check("a memory without a description fires",
                any("frontmatter" in p for p in got), str(got)[:150])

    with TempDir() as t:
        s = t / "mem"
        write(s, "a-fact.md", MEMO)
        write(s, "MEMORY.md", "- [A fact](a-fact.md) - hook\n" + "x" * INDEX_CAP)
        got = check_store(s)
        c.check("an over-budget index fires with the cap named",
                any(str(INDEX_CAP) in p and "/memory-audit" in p for p in got), str(got)[:150])

    with TempDir() as t:
        c.check("a store with no index at all is one loud problem",
                check_store(t / "mem") != [], "")

    # ── the TRIGGER band (SCC-68): fires BELOW the cap, and the run still passes ──
    with TempDir() as t:
        s = t / "mem"
        write(s, "a-fact.md", MEMO)
        write(s, "MEMORY.md", sized_index(0.91))
        c.check("an index at 91% of cap triggers the audit", audit_due(s), "")
        c.check("...and 91% is NOT a failure - the run still passes", check_store(s) == [],
                str(check_store(s))[:150])
        c.check("...and the block names the command + the ask",
                "/memory-audit" in audit_block(s) and "ask the operator" in audit_block(s), "")

    with TempDir() as t:
        s = t / "mem"
        write(s, "a-fact.md", MEMO)
        write(s, "MEMORY.md", sized_index(0.89))
        c.check("an index at 89% stays silent (a trigger that cries wolf gets ignored)",
                not audit_due(s), f"{len(index_text(s).encode('utf-8'))} bytes")

    # ── the signal worklist: derived, and honest about being signals ──
    with TempDir() as t:
        s = t / "mem"
        write(s, "a-fact.md", MEMO.replace("The fact.", "See [[never-written-yet]]."))
        write(s, "MEMORY.md", "# Index\n- [A fact](a-fact.md) - ⛔ RETIRED 08-07\n")
        sig = audit_signals(s)
        c.check("a CLOSED/RETIRED index row surfaces as a candidate",
                any("index row" in x for x in sig), str(sig)[:150])
        c.check("a dangling [[link]] surfaces, described as possibly legitimate",
                any("dangling" in x and "forward reference" in x for x in sig), str(sig)[:150])

    with TempDir() as t:
        s = t / "mem"
        write(s, "a-fact.md", MEMO)
        write(s, "MEMORY.md", "# Index\n- [A fact](a-fact.md) - hook\n")
        c.check("a healthy store produces NO candidates", audit_signals(s) == [],
                str(audit_signals(s))[:150])
        # ⛔ REGRESSION PIN (the SCC-73 blocker). This exact fixture passed in a worktree and failed
        # on main, because audit_signals reached for a module-global REPO_ROOT and inherited AGY's
        # missing back-pointer. A hermetic store must stay hermetic no matter what the live repo
        # holds - assert it against the REAL repo, which is the state that broke it.
        c.check("...even when the live repo has real cross-repo findings (hermetic stays hermetic)",
                audit_signals(s, None) == [] and audit_signals(s) == [],
                str(audit_signals(s, REPO_ROOT))[:110])
        c.check("...and passing a repo explicitly is what opts INTO cross-repo signals",
                audit_signals(s, REPO_ROOT) == project_store_signals(REPO_ROOT), "")

    # ── SCC-73: the two-tier contract, on fixtures first ──
    with TempDir() as t:
        repo = t / "repo"
        (repo / ".agents").mkdir(parents=True)
        (repo / ".agents" / "maintained-projects.txt").write_text(
            "# a comment\n\nPRESENT\nUNCLONED\nNOSTORE\n", encoding="utf-8")
        # SORTED, not file order: check_maps returns a set, so insertion order is not a property
        # to rely on. Deterministic ordering is what the reports need; sorted gives that.
        c.check("the allowlist is read from the tracked file, comments and blanks dropped",
                maintained_project_names(repo) == ["NOSTORE", "PRESENT", "UNCLONED"],
                str(maintained_project_names(repo)))
        c.check("an ABSENT allowlist is None (loud), never an empty list (silently disarmed)",
                maintained_project_names(t / "no-such-repo") is None, "")

        ps = repo / "Projects" / "PRESENT" / "_artifacts" / "_memory"
        write(ps, "p-fact.md", MEMO)
        # The good case must be TEXTUALLY DISTINCT from the project's own store path. Writing the
        # bare `_artifacts/_memory/` here is what made the old check unfalsifiable: that string
        # also describes where this very file lives, so the "has a back-pointer" fixture proved
        # nothing. It must name the LOBBY unambiguously.
        write(ps, "MEMORY.md",
              f"# P\n- [A fact](p-fact.md) - hook\nlobby law: `{LOBBY_BACKPOINTER}`\n")
        (repo / "Projects" / "PRESENT" / ".git").write_text("gitdir: x", encoding="utf-8")
        (repo / "Projects" / "NOSTORE").mkdir(parents=True)
        (repo / "Projects" / "NOSTORE" / ".git").write_text("gitdir: x", encoding="utf-8")
        (repo / "Projects" / "UNCLONED").mkdir(parents=True)   # empty stub: submodule not init'd

        stores, skips = project_stores(repo)
        c.check("a checked-out project store with an index IS gated",
                [p.parent.parent.name for p in stores] == ["PRESENT"], str(stores))
        c.check("an uninitialized submodule is skipped, and the skip NAMES itself",
                any("UNCLONED" in s and "not checked out" in s for s in skips), str(skips))
        c.check("a project with no store yet is skipped as a beginning, not rot",
                any("NOSTORE" in s and "nothing to gate" in s for s in skips), str(skips))
        c.check("...and every skip is a sentence, never a silent pass", len(skips) == 2, str(skips))

        # The defect must FIRE through the fan-out, or gating project stores means nothing.
        write(ps, "orphan.md", MEMO)
        got = check_store(stores[0])
        c.check("a defect seeded in a PROJECT store fires the same contract as the lobby",
                any("orphan.md" in p for p in got), str(got)[:150])

        # F1: asserted against the ALLOWLIST, so it still bites where Projects/ is an empty stub.
        write(repo / "mem", "MEMORY.md", "# Index\n(no pointer section)\n")
        got = pointer_problems(repo / "mem", repo)
        c.check("an index with no `## Project stores` section fires",
                any(POINTER_HEADING in p for p in got), str(got)[:150])
        write(repo / "mem", "MEMORY.md", f"# Index\n{POINTER_HEADING}\n- PRESENT -> somewhere\n")
        got = pointer_problems(repo / "mem", repo)
        c.check("a section that omits an allowlisted project fires - even one never checked out",
                any("UNCLONED" in p for p in got) and any("NOSTORE" in p for p in got),
                str(got)[:150])
        write(repo / "mem", "MEMORY.md",
              f"# Index\n{POINTER_HEADING}\n- PRESENT\n- UNCLONED\n- NOSTORE\n")
        c.check("a section naming every allowlisted project passes",
                pointer_problems(repo / "mem", repo) == [], str(pointer_problems(repo / "mem", repo)))

        # ── the two ways this check could be DEFEATED, both pinned ──
        # An EMPTY section whose names appear in unrelated rows further down the index. The old
        # code took `split(heading)[1]` - the whole rest of the file - so ~99% of a 21 KB index
        # counted as "the section", and one future memory row naming a project path would have
        # anaesthetized this permanently.
        write(repo / "mem", "MEMORY.md",
              f"# Index\n{POINTER_HEADING}\n(nothing here)\n\n## Other memories\n"
              f"- [a row](x.md) - about PRESENT and UNCLONED and NOSTORE\n")
        got = pointer_problems(repo / "mem", repo)
        c.check("an EMPTY section is not saved by names appearing elsewhere in the index",
                len(got) == 3, str(got)[:130])

        # A LONGER sibling satisfying a SHORTER allowlisted name by raw containment.
        (repo / ".agents" / "maintained-projects.txt").write_text(
            "PRESENT\nPRESENT-VR\n", encoding="utf-8")
        write(repo / "mem", "MEMORY.md", f"# Index\n{POINTER_HEADING}\n- PRESENT-VR -> somewhere\n")
        got = pointer_problems(repo / "mem", repo)
        c.check("a longer sibling row does NOT satisfy a shorter allowlisted name",
                any("PRESENT`" in p for p in got), str(got)[:130])
        (repo / ".agents" / "maintained-projects.txt").write_text(
            "# a comment\n\nPRESENT\nUNCLONED\nNOSTORE\n", encoding="utf-8")

        c.check("a project index that names the lobby store passes the back-pointer check",
                backpointer_problems(repo) == [], str(backpointer_problems(repo)))
        # The AMBIGUOUS case, pinned: an index that names only its OWN store path must still FIRE.
        # This is the case the pre-review check could not see, and the reason the sentinel exists.
        write(ps, "MEMORY.md",
              "# P\n- [A fact](p-fact.md) - hook\nmy memories live in `_artifacts/_memory/`\n")
        c.check("a project index with no back-pointer to the lobby fires",
                any("PRESENT" in p for p in backpointer_problems(repo)),
                str(backpointer_problems(repo))[:150])

        # OWNERSHIP: a project store lives in a repo whose commit-msg hook rejects this repo's
        # ticket keys, so its defects must be LOUD but never BLOCKING here (see the block comment
        # above project_store_signals). Both halves asserted - reported, and not a failure.
        sig = project_store_signals(repo)
        c.check("a broken project store is REPORTED as an audit signal",
                any("PRESENT" in x for x in sig), str(sig)[:150])
        c.check("...and says where the fix belongs, since it cannot be made from here",
                any("under its own key" in x for x in sig), str(sig)[:150])
        c.check("...and is NOT a blocking failure of the lobby's own contract",
                check_store(repo / "mem") == [], str(check_store(repo / "mem"))[:150])

    # ── the pins the operator asked to hold (SCC-73: relocate, do NOT raise) ──
    c.check("INDEX_CAP is unchanged at 25 KB", INDEX_CAP == 25 * 1024, str(INDEX_CAP))
    c.check("TRIGGER_PCT is unchanged at 90%", TRIGGER_PCT == 0.90, str(TRIGGER_PCT))
    c.check("the audit block names Phase 2 as the remedy once the levers are spent",
            "SCC-73 Phase 2" in audit_block(REAL_STORE), "")

    # ── THE gate: the real store honors the contract it advertises ──
    c.check("real store exists where AGENTS.md routes every platform",
            (REAL_STORE / "MEMORY.md").is_file(), str(REAL_STORE))
    got = check_store(REAL_STORE)
    c.check("real store: index <= 25KB, links resolve, no orphans, frontmatter present",
            got == [], " | ".join(got[:4]))

    # ── THE gate, tier two: every project store that exists honors it too ──
    # Every case below reports HOW MANY stores it actually read. In a worktree that is zero, and a
    # bare green there would claim coverage this run cannot have - the same vacuous pass F1 caught
    # in the first draft of this section. The count is the difference between "checked, clean" and
    # "checked nothing"; the [SKIP] lines after the tally say which projects and why.
    real_stores, real_skips = project_stores(REPO_ROOT)
    got = pointer_problems(REAL_STORE, REPO_ROOT)
    c.check("lobby index signposts every maintained project store (from the TRACKED allowlist, "
            "so this holds in a worktree too)", got == [], " | ".join(got[:3]))

    rc = c.finish()
    # Coverage is stated, never implied. Skips are printed because a run that checked nothing must
    # not read like one that checked everything - in a worktree that is EVERY project, which is
    # exactly when silence would mislead most. Signals print too: they are real findings that this
    # repo is not allowed to fix (another repo's key), so they must be seen without blocking.
    print(f"[COVERAGE] project stores read this run: {len(real_stores)}"
          f"{' (' + ', '.join(s.parent.parent.name for s in real_stores) + ')' if real_stores else ''}")
    for s in real_skips:
        print(f"[SKIP] project store not gated - {s}")
    for s in project_store_signals(REPO_ROOT):
        print(f"[SIGNAL] {s}")
    # AFTER the tally, so it is the last thing on screen and survives a `| tail`.
    if audit_due(REAL_STORE):
        print(audit_block(REAL_STORE, REPO_ROOT))
    return rc


if __name__ == "__main__":
    sys.exit(main())
