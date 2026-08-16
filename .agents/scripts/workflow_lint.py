"""workflow_lint.py — the regression net for the workflow-infrastructure upgrade (Wave 1.1).

Checks the TOOLKIT (lobby .agents/) and one TARGET PROJECT against the invariants the
command prose currently asks agents to hold by hand. Built FIRST so later waves can prove
they broke nothing.

Exit: 0 clean · 1 warnings only · 2 any error.  `--json` for machines.

Usage:
    python .agents/scripts/workflow_lint.py [--project <name-or-path>] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wf_common as wf

_LINK_RE = re.compile(r"\]\(([^)]+)\)")


# ── Toolkit checks (lobby) ─────────────────────────────────────────────────────

def check_commands(lobby: Path, rep: wf.Report) -> None:
    cmd_dir = lobby / ".agents" / "commands"
    files = sorted(cmd_dir.glob("*.md"))
    index_path = cmd_dir / "INDEX.md"
    index_text = wf.read_text(index_path) if index_path.is_file() else ""

    for f in files:
        if f.name == "INDEX.md":
            continue
        text = wf.read_text(f)
        # platforms: [] syncs to ZERO platforms while looking installed
        # (memory: platforms-empty-list-means-nowhere). Omitting the key = all four, fine.
        head = text[:800]
        if re.search(r"^platforms:\s*\[\s*\]", head, re.MULTILINE):
            rep.err("commands", f"{f.name}: `platforms: []` syncs to NOWHERE")
        if not text.startswith("---"):  # read_text strips a BOM, so this is a real absence
            rep.warn("commands", f"{f.name}: no frontmatter block")
        if wf.has_bom(f):
            rep.info("commands", f"{f.name}: UTF-8 BOM present")
        stem = f.stem
        if index_text and stem not in index_text:
            rep.warn("commands-index", f"{f.name} not mentioned in commands/INDEX.md")

    if index_text:
        # Dead pointers — LINKS only. INDEX prose legitimately names files that live
        # elsewhere (`docs/_scc_sops_prds/smh-adviser-board-REFERENCE.md`) and records
        # historical renames (`sprint-dependency-map.md` -> ...); a bare-filename scan
        # reads those as missing commands.
        for target in set(_LINK_RE.findall(index_text)):
            t = target.split("#")[0].strip()
            if not t or t.startswith(("http://", "https://", "mailto:")):
                continue
            if not (cmd_dir / t).exists():
                rep.err("commands-index", f"INDEX.md dead link: {target}")
    else:
        rep.warn("commands-index", "commands/INDEX.md missing or empty")


# A command that DOES the thing must POINT at the rule governing it. Note the direction:
# the invariant is "the pointer exists", never "the prose is deleted". The standing
# obligations stay restated inline on purpose - agents follow the literal step list, and a
# bare pointer gets skipped (memory: restate-alwayson-obligations-in-command-bodies).
_RULE_POINTERS = (
    ("git-policy", "git-mutating",
     re.compile(r"git (?:commit|push|add|merge|rebase|reset)\b|"
                r"git checkout -b|git branch -[Dd]\b")),
    ("worktree-per-story", "worktree",
     re.compile(r"git worktree\b")),
    ("smh-target-resolution", "target-resolving",
     re.compile(r"^#+\s*Step 0\b.*(?:target|project)", re.I | re.M)),
    # SCC-170. Keyed on the machinery the rule OWNS - the `riders:` / `landing:` manifest
    # keys - not on the word "consolidate". A phrase-keyed row names the files that really
    # drive the mechanism; a concept-keyed one ("one worktree") matched six unrelated cicd
    # bodies and none of the three that matter (audit F26).
    ("work-consolidation", "consolidating",
     re.compile(r"^\s*riders\s*:|`riders:|landing\s*:\s*partial", re.M)),
)


def check_rule_pointers(lobby: Path, rep: wf.Report) -> None:
    """Scans RAW text, not strip_code'd prose. In a command file a backticked `git commit`
    is an INSTRUCTION the agent will run, not a quoted example - the opposite of the
    mojibake case, where the backticks mean "this is what NOT to write"."""
    cmd_dir = lobby / ".agents" / "commands"
    for f in sorted(cmd_dir.glob("*.md")):
        if f.name == "INDEX.md":
            continue
        text = wf.read_text(f)
        for rule, label, pattern in _RULE_POINTERS:
            if pattern.search(text) and rule not in text:
                rep.warn("rule-pointers",
                         f"{f.name}: {label} but never points at "
                         f"`.agents/rules/{rule}.md`")


# SCC-128: `bmad-code-review` (the vendor skill) and `bmad_code_review_sudo_fix` (the
# adapter rule that patched it) are RETIRED - the house `code-review-engine` skill replaces
# both. This guard is permanent rather than a one-time sweep because BMAD's installer
# re-emits the vendor skill on every regen: the file comes back on its own, so the thing
# worth policing is not the skill's existence but whether any of OUR surfaces still routes
# work to it.
#
# Scope is every AUTHORED routing surface under `.agents/`: commands (what an operator
# invokes), rules (what an agent loads mid-run), skills (the door Claude and Codex enter
# through), workflows (Antigravity's door) and opencode-agents (the opencode subagent
# definitions - `opus-reviewer.md` loaded the retired rule BY PATH, so this is the surface
# the regression actually lived on).
#
# ⛔ The first draft excluded `workflows/` on the reasoning that it holds generated mirrors
# which follow their command source. That is true of `workflows/<command>.md` and FALSE of
# `workflows/INDEX.md`, which sync-agents lists in its `$excluded` set - hand-written router
# prose with no command upstream, so it follows nothing and no regeneration can fix it. It
# was carrying a live stale pointer while this guard reported the toolkit clean. A mirror
# being scanned twice is harmless noise; a hand-owned router being scanned never is a hole.
#
# Still out of scope, each for a reason that is about ownership rather than convenience:
# `.agents/bmad/` (vendor manifests, regenerated, never hand-edited), `_artifacts/` (history
# that must stay readable exactly as it was written), and the machine-global/`.opencode/`,
# `.claude/` copies (byte mirrors of masters that ARE guarded here).
_RETIRED_REVIEW_RE = re.compile(r"bmad[-_]code[-_]review", re.I)
_RETIRED_SURFACES = ("commands", "rules", "skills", "workflows", "opencode-agents")


def check_retired_review_surface(lobby: Path, rep: wf.Report) -> None:
    """No routing surface may point at the retired vendor review skill (SCC-128).

    Both spellings are caught on purpose: `bmad-code-review` is the skill, and
    `bmad_code_review_sudo_fix` was the rule that adapted it - the second half is the one
    that survives as a dangling file path an agent is told to open. Case-insensitive
    because the half that varies is the half a human retypes.

    The message carries the path relative to the lobby, never the bare filename: `SKILL.md`
    and `INDEX.md` each name dozens of files here, and a gate that blocks a close-out
    without saying WHICH file to open is a gate people learn to route around.
    """
    for sub in _RETIRED_SURFACES:
        root = lobby / ".agents" / sub
        if not root.is_dir():
            continue
        for f in sorted(root.rglob("*.md")):
            # rglob yields DIRECTORIES whose name ends in `.md` too, and read_text's
            # errors="replace" covers decoding, not I/O - either would take the whole
            # linter down with a traceback instead of a finding.
            if not f.is_file():
                continue
            try:
                text = wf.read_text(f)
            except OSError as exc:
                rep.warn("retired-surface", f"{f.relative_to(lobby)}: unreadable ({exc})")
                continue
            if _RETIRED_REVIEW_RE.search(text):
                rep.err("retired-surface",
                        f"{f.relative_to(lobby)}: references the RETIRED vendor review "
                        f"surface - route it to the `code-review-engine` skill instead "
                        f"(SCC-128)")


def _last_commit_ts(path: Path, cwd: Path) -> int | None:
    r = wf.git(["log", "-1", "--format=%ct", "--", str(path)], cwd)
    out = r.stdout.strip()
    return int(out) if r.returncode == 0 and out.isdigit() else None


def _last_commit_sha(path: Path, cwd: Path) -> str | None:
    r = wf.git(["log", "-1", "--format=%H", "--", str(path)], cwd)
    out = r.stdout.strip()
    return out if r.returncode == 0 and out else None


# The twin's claim, in its frontmatter: `ap_reconciled: <sha of the primary I read>`.
AP_RECONCILED = re.compile(r"^ap_reconciled:\s*([0-9a-f]{7,40})\s*$", re.M)


def check_ap_twins(lobby: Path, rep: wf.Report) -> None:
    """_AP twins drift from their primaries (memory: sudo-commands-have-ap-twins-that-drift).

    A twin is NOT a step-for-step mirror — it is a single-pass headless adaptation with its
    own prose headings, so comparing step sequences only ever produces noise. The signals
    that actually mean drift: the twin stopped pointing at its primary, or the primary was
    committed AFTER the twin (someone fixed one side only).

    ── SCC-82: the timestamp alone made this UNSATISFIABLE ──────────────────────────
    "Primary is newer" is a prompt to go and diff, not a defect in itself, and often the
    honest answer is *nothing to port* — the SCC-63 fix that made `cicd-code-review.md`
    newer restored a historic artifact filename its twin does not contain and does not
    need. There was no way to say so. The warning stood on `main` for weeks, every
    close-out report carried "2 pre-existing warnings" as an excuse, and the only way to
    clear it was to TOUCH the twin — which resets the clock while asserting nothing, and
    is indistinguishable from actually having done the work.

    `ap_reconciled: <sha>` is the twin's auditable claim: *I read the primary at this sha
    and there is nothing to port.* It is deliberately NOT a mute switch:

      - stamp present and current  → silent, and the twin's own mtime is irrelevant
      - stamp present but stale    → WARN, **even when the twin is the newer file** —
                                     which is precisely the touch-it-to-shut-it-up cheat
                                     the timestamp check could never see
      - no stamp at all            → the original timestamp signal, unchanged

    So the check gained teeth rather than losing them: silence now requires someone to
    have written down which version of the primary they read."""
    cmd_dir = lobby / ".agents" / "commands"
    # Suffix is `-AP` since SCC-63 (hyphens only; it was `_AP` before the rename).
    for ap in sorted(cmd_dir.glob("*-AP.md")):
        primary = cmd_dir / (ap.stem[:-3] + ".md")
        if not primary.is_file():
            rep.err("ap-twins", f"{ap.name}: primary {primary.name} missing")
            continue
        text = wf.read_text(ap)
        # Match the STEM: twins name the primary bare in their title/description
        # (`# /cicd-code-review-AP - ...`); only some use the `@.../<name>.md` path form.
        # This fires when the primary is RENAMED out from under the twin.
        if primary.stem not in text:
            rep.warn("ap-twins", f"{ap.name} no longer references {primary.stem}")
        claim = AP_RECONCILED.search(text)
        if claim:
            claimed, pr_sha = claim.group(1), _last_commit_sha(primary, lobby)
            # Abbreviated shas are accepted by prefix; a sha that is not a prefix of the
            # primary's current commit is not a claim about the file in front of you.
            if pr_sha and pr_sha.startswith(claimed):
                continue
            rep.warn("ap-twins",
                     f"{ap.name}: ap_reconciled names {claimed[:7]}, but {primary.name} "
                     f"is now at {(pr_sha or '?')[:7]} - diff the twin and restamp")
            continue
        ap_ts, pr_ts = _last_commit_ts(ap, lobby), _last_commit_ts(primary, lobby)
        if ap_ts and pr_ts and pr_ts > ap_ts:
            days = round((pr_ts - ap_ts) / 86400, 1)
            rep.warn("ap-twins",
                     f"{primary.name} committed {days}d AFTER {ap.name} - diff the twin")


# Vendor BMAD bridges keep their upstream names and take no prefix. This list is
# CLOSED: widening it is how the convention dies one exception at a time. A new
# command belongs to cicd- (one project, never the lobby) or smh- (may act on the
# lobby); sentry- is the reserved incident family.
VENDOR_COMMANDS = frozenset({
    "INDEX", "analyst", "architect", "bmad-help", "bmad-master", "dev", "pm", "qa", "sm",
    "tea", "tech-writer", "testarch-atdd", "testarch-automate", "testarch-ci",
    "testarch-framework", "testarch-nfr", "testarch-test-design", "testarch-test-review",
    "testarch-trace", "ux-designer",
})
_FAMILY_RE = re.compile(r"^(cicd|smh|sentry)-")


def check_naming_law(lobby: Path, rep: wf.Report) -> None:
    """Every command master declares its family in its name (SCC-63).

    The prefix is load-bearing, not cosmetic: `cicd-*` binds smh-target-resolution.md
    (exactly ONE project, never the lobby) while `smh-*` may act on the repo you are
    standing in. A misnamed command therefore claims the wrong permissions. Underscores
    are rejected outright — the same pass that retired `sudo-` normalised separators, and
    a lone `foo_bar.md` would quietly reintroduce the split the rename removed."""
    cmd_dir = lobby / ".agents" / "commands"
    for f in sorted(cmd_dir.glob("*.md")):
        stem = f.stem
        if stem in VENDOR_COMMANDS:
            continue
        if not _FAMILY_RE.match(stem):
            rep.err("naming-law",
                    f"{f.name}: must start with cicd- / smh- / sentry- "
                    f"(or be a listed vendor bridge) - see AGENTS.md command naming law")
        if "_" in stem:
            rep.err("naming-law", f"{f.name}: underscore in command name - hyphens only")


# ── Project checks ─────────────────────────────────────────────────────────────

def check_active_context(project: Path, rep: wf.Report) -> None:
    path = project / wf.ACTIVE_CONTEXT_REL
    if not path.is_file():
        rep.err("context", f"{wf.ACTIVE_CONTEXT_REL} missing")
        return
    size = path.stat().st_size
    if size > 20 * 1024:
        rep.err("context", f"active-context is {size} bytes (budget 20480)")
    else:
        rep.info("context", f"active-context ~{round(size / 4)} / 5,000 tokens")


# REMOVED 2026-08-08 (SCC-51, operator ruling): the hard byte budgets on
# implementation_plan.md (8 KB) and walkthrough.md (10 KB), and the check that warned on them.
#
# They were set 2026-08-02 in the SAME commit that made implementation_plan.md a TWO-author
# document - the plan plus /cicd-self-audit's findings, phase evidence and verdict
# (artifacts-always-first §7). A fixed cap on a two-author doc squeezes the second author,
# which is the auditor: the one voice you least want truncated. The number was never
# validated against a real audit, and the first Full audit run under it had to compress its
# own findings to fit. That is the gate cutting substance while the filler it was aimed at
# survives.
#
# The discipline did NOT go away - it moved to where judgement belongs, as a stated standard
# in artifacts-always-first.md: dense not short, every line carries a decision / constraint /
# finding / evidence, and LENGTH IS NEVER A REASON TO OMIT A FINDING, AN AC, OR EVIDENCE.
# Do not re-add a byte threshold here. If artifacts bloat, the answer is removing what does
# not inform a decision - never truncating what does.


def check_sprint_status(project: Path, rep: wf.Report) -> None:
    path = project / wf.BOARD_REL
    text = wf.read_text(path)
    board = wf.parse_board(text)

    for key, info in board.items():
        if info["dupes"]:
            rep.err("sprint-status",
                    f"duplicate key '{key}' (lines {info['line_no']} + {info['dupes']})")

    missing_active, missing_done = [], 0
    for key, info in board.items():
        if not wf.is_story_key(key):
            continue
        files = wf.find_story_files(project, key)
        if len(files) > 1:
            rep.warn("sprint-status", f"'{key}' matches {len(files)} story files")
        elif not files:
            # backlog = "story only exists in the epic file" (no file is correct);
            # descoped stories legitimately never had one (21-2 precedent).
            if info["status"] in ("ready-for-dev", "in-progress", "review"):
                missing_active.append(f"{key} ({info['status']})")
            elif info["status"] == "done":
                missing_done += 1
    for item in missing_active:
        rep.err("sprint-status", f"active story with NO story file: {item}")
    if missing_done:
        rep.info("sprint-status",
                 f"{missing_done} done key(s) without a story file (historic; not gated)")


BOARD_SIZE_CAP = 96 * 1024  # bytes. Post-split landing was 62 KB (2026-08-03) with all
# doctrine comments deliberately KEPT (the reviewed triage); the cap is a regrowth
# backstop, not a tripwire on the target - the per-note rule below catches the actual
# failure mode (multi-KB notes returning) directly.
NOTE_CAP = wf.NOTE_CAP  # single source; see wf_common (split_sprint_status decides by the
#                         same constant - two declarations is a splitter that emits a board
#                         failing its own gate)
MAX_NOTE_ERRORS = 10    # a flood is as muting as silence: report the first N, then count


def check_board_note_budget(project: Path, rep: wf.Report) -> None:
    """Wave 4's standing rule: narrative never lands on the board again.

    The split bought back 300 KB; the board had been growing ~15 KB/day, so without
    this check the win is spent in a quarter. A no-note-status row carries NOTHING
    (story_status.py drops the note on the flip - audit F2); a live row carries at
    most NOTE_CAP chars; the full story belongs in _bmad-output/history/ and the
    walkthrough."""
    path = project / wf.BOARD_REL
    raw = path.read_bytes()
    if b"development_status" not in raw:
        return
    if len(raw) > BOARD_SIZE_CAP:
        rep.err("board-budget", f"{wf.BOARD_REL} is {len(raw)} bytes (cap "
                                f"{BOARD_SIZE_CAP}) - narrative is landing on the board "
                                f"again; move it to _bmad-output/history/")
    hist = project / "_bmad-output/history"
    if not hist.exists():
        rep.info("board-budget", "pre-split board (no _bmad-output/history/) - "
                                 "note rules not enforced")
        return
    shown = 0
    suppressed = 0
    for i, line in enumerate(wf.read_text(path).splitlines(), 1):
        m = wf.KEY_RE.match(line)
        if not m or m.group(2) not in wf.ALL_STATUSES:
            continue
        note = m.group(3).strip().lstrip("#").strip()
        if not note:
            continue
        if m.group(2) in wf.NO_NOTE_STATUSES:
            msg = (f"line {i}: '{m.group(1)}' is {m.group(2)} but carries a note - a "
                   f"finished row's story lives in history/, not on the board")
        elif len(note) > NOTE_CAP:
            msg = (f"line {i}: '{m.group(1)}' note is {len(note)} chars (cap {NOTE_CAP}) "
                   f"- move it to history/ and keep a <={NOTE_CAP}-char pointer, or nothing")
        else:
            continue
        if shown < MAX_NOTE_ERRORS:
            rep.err("board-budget", msg)
            shown += 1
        else:
            suppressed += 1
    if suppressed:
        rep.err("board-budget", f"...and {suppressed} more note violation(s) not listed - "
                                f"run split_sprint_status.py plan for the full census")


def check_status_drift(project: Path, rep: wf.Report) -> None:
    for d in wf.status_drift(project):
        rep.warn("status-drift",
                 f"{d['key']}: board={d['board']} vs frontmatter={d['frontmatter']} "
                 f"({d['file']}) - fix with story_status.py set --reconcile")


# A file that legitimately CONTAINS these bytes as data - the detector's own constants,
# its test fixtures, a doc quoting them outside a code span - declares it once, here.
# Without this the scanner flags itself: wf_common.py holds a literal U+FFFD as
# REPLACEMENT_CHAR, so the gate blocked every commit that touched the gate. Third instance
# of this shape in the project (memory: comment-literals-invert-source-grep-tests).
ENCODING_OPT_OUT = "wf-lint: allow-encoding-literals"


def scan_encoding(paths: list[tuple[str, Path]], rep: wf.Report) -> None:
    """Two distinct corruptions, two severities:
      * U+FFFD  = bytes that are NOT valid UTF-8 -> the file is already broken (ERROR).
      * `a-hat-euro` digraphs = valid UTF-8 that encodes a cp1252 misread (WARN).
    Neither is visible in a PS 5.1 console, which renders good UTF-8 as digraphs anyway."""
    for label, path in paths:
        if not path.is_file():
            continue
        text = wf.read_text(path)
        if ENCODING_OPT_OUT in text:
            continue
        # U+FFFD is scanned RAW — an undecodable byte is broken wherever it sits.
        if wf.REPLACEMENT_CHAR in text:
            rep.err("encoding",
                    f"{label}: {text.count(wf.REPLACEMENT_CHAR)} undecodable byte(s)")
        prose = wf.strip_code(text)
        hits = sum(prose.count(m) for m in wf.MOJIBAKE_MARKERS)
        if hits:
            rep.warn("encoding", f"{label}: ~{hits} mojibake digraph(s) (cp1252 round-trip)")


# cp1252 round-trip repairs that are UNAMBIGUOUS: each left side is a byte sequence that
# cannot arise from correctly-encoded text in these documents. Anything less certain is
# reported, never rewritten - "fixing" a clean file is the failure mode this guards
# (memory: powershell-console-fakes-mojibake).
_REPAIRS = {"â€”": "—", "â€“": "–", "â€˜": "‘", "â€™": "’",
            "â€œ": "“", "â€": "”", "â€¦": "…", "Â ": " ", "Â·": "·"}


def staged_files(repo: Path) -> list[Path]:
    r = wf.git(["diff", "--cached", "--name-only", "--diff-filter=ACMR"], repo)
    out = []
    for line in r.stdout.splitlines():
        p = repo / line.strip()
        if line.strip() and p.is_file() and p.suffix.lower() in (
                ".md", ".py", ".yaml", ".yml", ".json", ".ts", ".tsx", ".js", ".sh", ".ps1"):
            out.append(p)
    return out


def cmd_staged(fix: bool) -> int:
    """Pre-commit gate: encoding only, on STAGED files only, and fast.

    A full lint here would make every commit slow and the hook would be disabled within a
    week. Encoding is the right thing to gate at commit time because it is the one defect
    that is invisible in review - a PS 5.1 console renders good UTF-8 as mojibake anyway."""
    repo = Path(wf.git(["rev-parse", "--show-toplevel"], Path.cwd()).stdout.strip() or ".")
    files = staged_files(repo)
    if not files:
        return 0
    rep = wf.Report()
    scan_encoding([(str(p.relative_to(repo)), p) for p in files], rep)
    if fix:
        for p in files:
            text = wf.read_exact(p)
            new = text
            for bad, good in _REPAIRS.items():
                new = new.replace(bad, good)
            if new != text:
                wf.write_exact(p, new)
                print(f"[FIXED] {p.relative_to(repo)} - re-stage it")
        return 0
    errs, _ = rep.counts()
    if rep.items:
        rep.print_human("pre-commit encoding gate")
    if errs:
        print("\nCOMMIT BLOCKED: undecodable bytes in a staged file.")
        print("  inspect : python .agents/scripts/workflow_lint.py --staged")
        print("  repair  : python .agents/scripts/workflow_lint.py --staged --fix   (then re-stage)")
        print("  bypass  : git commit --no-verify   (say why in the message)")
    return 2 if errs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Workflow invariants linter (Wave 1.1)")
    ap.add_argument("--project", help="project name under Projects/ or a path")
    ap.add_argument("--toolkit-only", action="store_true",
                    help="lobby/toolkit checks only; never resolves a project - a root "
                         "Task close-out must not inherit .agents/active-project.txt (SCC-64)")
    ap.add_argument("--staged", action="store_true",
                    help="pre-commit mode: encoding scan of staged files only")
    ap.add_argument("--fix", action="store_true",
                    help="with --staged: repair unambiguous cp1252 round-trips in place")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.staged:
        return cmd_staged(args.fix)
    if args.toolkit_only and args.project:
        wf.die("--toolkit-only and --project are mutually exclusive - the flag exists "
               "precisely so no project is resolved")

    rep = wf.Report()
    scan: list[tuple[str, Path]] = []
    lobby = wf.find_lobby_root(Path.cwd())
    if lobby:
        check_commands(lobby, rep)
        check_rule_pointers(lobby, rep)
        check_ap_twins(lobby, rep)
        check_naming_law(lobby, rep)
        check_retired_review_surface(lobby, rep)
        scan += [(f"commands/{f.name}", f)
                 for f in sorted((lobby / ".agents" / "commands").glob("*.md"))]
    else:
        rep.info("toolkit", "no lobby root found from cwd - toolkit checks skipped")

    if args.toolkit_only:
        # The whole point of the flag: STOP before resolve_project_root, which would fall
        # back to cwd and then .agents/active-project.txt - a root Task close-out gated on
        # whichever product project happens to be active is a gate about the wrong thing.
        if not lobby:
            wf.die("--toolkit-only: no lobby root found from cwd - there is no toolkit "
                   "here to lint")
        scan_encoding(scan, rep)
        if args.json:
            print(json.dumps({"project": None, "findings": rep.items,
                              "exit": rep.exit_code()}, indent=2))
        else:
            rep.print_human("workflow_lint - toolkit-only")
        return rep.exit_code()

    project = wf.resolve_project_root(args.project)
    check_active_context(project, rep)
    check_sprint_status(project, rep)
    check_board_note_budget(project, rep)
    check_status_drift(project, rep)
    scan += [(rel, project / rel) for rel in
             (wf.BOARD_REL, wf.ACTIVE_CONTEXT_REL)]
    scan_encoding(scan, rep)

    if args.json:
        print(json.dumps({"project": str(project), "findings": rep.items,
                          "exit": rep.exit_code()}, indent=2))
    else:
        rep.print_human(f"workflow_lint - {project.name}")
    return rep.exit_code()


if __name__ == "__main__":
    sys.exit(main())
