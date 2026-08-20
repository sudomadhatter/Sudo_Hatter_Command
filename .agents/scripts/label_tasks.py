"""label_tasks.py — which of a parent's children can run side by side? (SCC-56, SCC-155)

TWO MODES, one engine. Story mode assesses BMAD stories under a BMAD epic (`/cicd-label-tasks`);
task mode assesses Subtasks under one Task (`/smh-label-tasks`) - work with no story file, no
sprint board and no epic branch, which is the set nothing could answer for until SCC-155. The
mode is DERIVED from the parent's type, and each mode's gate refuses the other's parent BY NAME
and hands the operator across. It stamps TWO labels, `parallel-ok` and `quick-dev`.

`parallel-ok` used to be ruled by `/cicd-write-story-tests` Step 1.6, at story pickup. That
mints 19.1's ticket BEFORE 19.2's story file exists, so there is nothing to compare against,
and it is never re-evaluated. The proof it never worked is empirical: zero tickets across SCC
and AVCH carry the label, and the `Parallel-OK` saved filter returns nothing.

Parallel-safety is a property of a SET at a MOMENT, never of one story. So the writer moved:
one operator-invoked pass over ONE parent's children, recomputing every verdict and rewriting
every label in one go. Same field, opposite property — a per-story writer can never see the
set, a parent-scoped one is self-correcting on every re-run.

`quick-dev` joined it in SCC-155 for the same reason, with one difference that is load-bearing:
its decision is TRI-state. A child the pass did not assess is left ALONE (see `label_plan`),
because reading absence as "not eligible" would strip the label off work marked by hand.

    plan     --parent KEY            enumerate + ground; emits the agent's work packet
    resolve  --plan F --touchsets F  the set math; emits verdicts
    stamp    --plan F --verdicts F   write labels + the stamped comment  [--apply]
    check    --parent KEY            is the existing stamp still valid, or stale?

The split is deliberate. The SCRIPT does the set math and the board writes; the AGENT reads
the story files, because telling "will modify" from "mentions" is a judgment no parser wins:
across 139 AGY story files, 105 name source paths, 58 carry negative declarations, and only 29
have a `**Task**` checklist. Story 19.1 names `google_llm.py:119` — a path inside the venv, a
REFERENCE — and says "NO `firestore_session.py` changes, that is 19.2 entirely", a negative
declaration handing a file to a named sibling.

Two behaviours are load-bearing, both paid for by incidents:

  * GROUNDING GATE — no story file, no assessment. The answer is "write the story first",
    never a guess. On 2026-07-31 a board called a story with no story file parallel-safe; its
    (1) then found both stories editing `check_cost_cap` at the same line.
  * STALENESS — the verdict carries the set it was computed against. A stamped set that no
    longer matches the parent's current children reads "re-run me", never as a verdict. An
    undetectably stale snapshot is exactly how the sprint dependency map and the `Deferred`
    saved filter both misled on 2026-08-09.

PROJECT-AGNOSTIC BY CONSTRUCTION — no project, key, path or repo is named anywhere in this
file. The target is DERIVED: the parent key's project prefix is matched against the
`JIRA_KEYS` each repo declares in its own `.agents/jira.conf`, searching the lobby plus every
directory under `Projects/`. Adding a project is therefore zero edits here — clone it, give it
a `jira.conf`, done. Two repos claiming one key is reported as the misconfiguration it is
rather than silently resolved. Everything else it reads (`_bmad/bmm/stories/`,
`_bmad-output/planning-artifacts/epics.md`, `epic/*` branches, `_artifacts/**/
implementation_plan.md`) is a toolkit-wide convention, not one project's layout.

Scope, story mode: BMAD stories under a BMAD epic, in whichever repo holds them — so the lobby
qualifies the day it carries BMAD stories, exactly like any project. Grouping epics, and any
non-Epic parent, are refused by name and handed to task mode.

Scope, task mode: the Subtasks under ONE Task. No story file is required or looked for; a lane
is grounded by its branch diff, the plan its sibling `task.yaml` declares, or its ticket text,
in that order. An Epic parent is refused by name and handed to story mode.

Exit: 0 clean - 1 warnings - 2 blocking. It reads, computes, and writes LABELS plus one
comment. It never transitions a ticket, never touches the working tree, never starts anything.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wf_common as wf  # noqa: E402

LABEL = "parallel-ok"
QUICK = "quick-dev"
# The marker string lives on the BOARD, not in this repo, so a rename here cannot be swept:
# every stamp already posted would go invisible and read as never-checked. It is deliberately
# frozen at the name the SCC-56 pass wrote, and `check` finds those older stamps unchanged.
MARKER = "Parallel check"

# The two commands this engine serves. Which one a refusal or a stamp NAMES is load-bearing:
# `/cicd-parallel-check` was retired by SCC-155, and a board comment pointing at a retired
# command is the SCC-63 failure - the reader follows it and finds nothing.
COMMAND = {"story": "/cicd-label-tasks", "task": "/smh-label-tasks"}
# Overlap is decided by SOURCE paths only. A shared story file or a shared plan is two lanes
# documenting themselves, not two lanes editing the same code.
#
# This list is the toolkit's own planning dirs and nothing else - deliberately NOT `docs/`,
# `content/` or anything a project might legitimately ship from. Every project defines its own
# source layout, so the safe rule is "exclude what the toolkit writes", never "guess what the
# project deploys". Over-excluding here manufactures false greens, which is the one failure
# mode this command exists to prevent.
PLANNING_PREFIXES = ("_bmad-output/", "_bmad/", "_artifacts/", "_my_resources/")

_ASCII_FOLD = {
    "—": "-", "–": "-", "'": "'", "'": "'", """: '"', """: '"',
    "…": "...", "→": "->", "·": "-", "≥": ">=", "≤": "<=",
    # 📝 folds to a MODE-NEUTRAL mark. It used to fold to `[NO-STORY]`, which the renderer
    # then followed with its own words - so a task-mode console read `[NO-STORY] no plan`,
    # naming the one concept that mode exists to say does not apply. The three marks beside
    # it have the same shape (the glyph is the mark, the words carry the verdict), so this
    # is the fold matching them rather than a new convention (SCC-155 review finding).
    "🟢": "[OK]", "🔒": "[LOCK]", "⏳": "[WAIT]", "📝": "[NOTE]", "🧵": "==",
}


def ascii_out(s: str) -> str:
    """Console output only — the PC's cp1252 console raises on the verdict emoji, which would
    turn a successful run into a crash after the fact. Ticket bodies keep the real glyphs."""
    for k, v in _ASCII_FOLD.items():
        s = s.replace(k, v)
    return s.encode("ascii", "replace").decode("ascii")


def say(msg: str = "") -> None:
    print(ascii_out(msg))


def warn(msg: str) -> None:
    print(ascii_out("[WARN] " + msg), file=sys.stderr)


# ── acli ───────────────────────────────────────────────────────────────────────

def acli_bin(explicit: str | None) -> str:
    for cand in (explicit, os.environ.get("ACLI_BIN")):
        if cand:
            return cand
    found = shutil.which("acli")
    if not found:
        wf.die("acli not found. Install it, or pass --acli / set ACLI_BIN. "
               "See .agents/rules/jira.md")
    return found


def acli(binary: str, args: list[str], timeout: int = 90) -> subprocess.CompletedProcess:
    return subprocess.run([binary, *args], capture_output=True, text=True,
                          errors="replace", timeout=timeout)


def acli_json(binary: str, args: list[str]) -> object | None:
    """acli returns an ARRAY on `search` and an OBJECT on `view`, and prints human chatter
    alongside the JSON on several paths — so scan for the first balanced value."""
    r = acli(binary, args)
    if r.returncode != 0:
        return None
    dec = json.JSONDecoder()
    out = r.stdout or ""
    for i, ch in enumerate(out):
        if ch in "{[":
            try:
                return dec.raw_decode(out[i:])[0]
            except ValueError:
                continue
    return None


def child_keys(rows: object) -> list[str]:
    """Keys out of a `workitem search --json` payload, tolerating nulls.

    acli puts a bare `null` in the array for any row it could not materialize, so a naive
    `r.get("key")` raises AttributeError on a response that is otherwise perfectly good."""
    if not isinstance(rows, list):
        return []
    return [r["key"] for r in rows if isinstance(r, dict) and r.get("key")]


def adf_text(node: object) -> str:
    """Comments come BACK as Atlassian Document Format even when sent as plain text."""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(adf_text(n) for n in node)
    if isinstance(node, dict):
        if node.get("type") == "text":
            return str(node.get("text", ""))
        inner = adf_text(node.get("content", []))
        return inner + ("\n" if node.get("type") in ("paragraph", "heading") else "")
    return ""


# ── the repo the key belongs to ────────────────────────────────────────────────

def repo_keys(repo: Path) -> list[str]:
    """The Jira projects this repo answers to, from its own `.agents/jira.conf`. Sourced as
    shell by the commit-msg hook, so it is plain KEY="value" — parse, never execute."""
    conf = repo / ".agents" / "jira.conf"
    if not conf.is_file():
        return []
    m = re.search(r'^\s*JIRA_KEYS\s*=\s*"?([^"\n#]+)"?', wf.read_text(conf), re.MULTILINE)
    return m.group(1).split() if m else []


def repo_for_key(key: str, explicit: str | None) -> Path:
    """THE TARGET IS DERIVED FROM THE KEY, never asked and never guessed.

    Each repo declares its project in `.agents/jira.conf`, so `AVCH-13` resolves to
    Projects/AGY_AVIATIONCHAT and `SCC-99` resolves to the lobby. This is why the command can
    legitimately act on the command centre without roaming it: it follows the epic, and the
    lobby qualifies the day it carries BMAD stories (its `_bmad/bmm/` install is already
    there). See `.agents/rules/smh-target-resolution.md` for the ladder this varies from."""
    if explicit:
        p = Path(explicit).resolve()
        if not p.is_dir():
            wf.die(f"--repo path does not exist: {p}")
        return p
    proj = key.split("-")[0].upper()
    start = Path.cwd().resolve()
    lobby = wf.find_lobby_root(start)
    if lobby is None:
        # A project checked out on its own, with no lobby above it.
        for p in [start, *start.parents]:
            if (p / ".git").exists():
                if proj in repo_keys(p):
                    return p
                wf.die(f"{p.name} does not answer to project '{proj}' "
                       f"(its .agents/jira.conf says {repo_keys(p) or 'nothing'})")
        wf.die(f"not inside a git repository: {start}")
    candidates = [lobby, *sorted(d for d in (lobby / "Projects").iterdir() if d.is_dir())]
    hits = [c for c in candidates if proj in repo_keys(c)]
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        # Two repos claiming one project key is a real misconfiguration, and picking the first
        # would silently assess the wrong tree. Say which, and let the operator fix the conf.
        wf.die(f"Jira project '{proj}' is claimed by MORE THAN ONE repo: "
               + ", ".join(c.name for c in hits)
               + ". Fix the duplicate in .agents/jira.conf, or pass --repo.", 2)
    wf.die(f"no repo here answers to Jira project '{proj}'. Checked "
           f"{len(candidates)}: " + ", ".join(c.name for c in candidates)
           + ". Each repo declares its own key in .agents/jira.conf.")
    raise AssertionError  # unreachable


# ── the BMAD gate ──────────────────────────────────────────────────────────────

_BMAD_EPIC_RE = re.compile(r"\bEpic\s+(\d+(?:\.\d+)*)\b", re.I)
_STORY_ID_RE = re.compile(r"^\s*(\d+(?:\.\d+)+[a-z]?|\d+\.\d+)\s*[—\-–:]")
_DEBUG_ID_RE = re.compile(r"^\s*(debug-[a-z0-9.\-]+)", re.I)


def bmad_epic_number(summary: str) -> str | None:
    m = _BMAD_EPIC_RE.search(summary or "")
    return m.group(1) if m else None


def story_id_of(summary: str) -> str | None:
    """The BMAD number a Story summary leads with — `12.3.4 — Checkride Frontend` -> 12.3.4.
    Also catches the `debug-` ids, which are Stories with no dotted number of their own."""
    for rx in (_STORY_ID_RE, _DEBUG_ID_RE):
        m = rx.match(summary or "")
        if m:
            return m.group(1)
    return None


def parent_facts(binary: str, key: str) -> dict:
    data = acli_json(binary, ["jira", "workitem", "view", key, "--json"])
    if not isinstance(data, dict):
        wf.die(f"cannot read {key} from Jira (is acli authenticated? `acli jira auth status`)")
    fields = data.get("fields") or {}
    itype = ((fields.get("issuetype") or {}).get("name")
             or (data.get("issuetype") or {}).get("name") or "")
    return {"key": data.get("key", key),
            "summary": fields.get("summary") or data.get("summary") or "",
            "type": itype}


def gate_bmad(parent: dict, repo: Path, forced: bool = False) -> str:
    """Refuse a grouping epic BY NAME, with the reason. A grouping epic's children are Tasks
    with no story files, so every row would be a bare 'no story' — the refusal says why in one
    line instead of printing an empty table and looking broken.

    ⭐ Every refusal here hands the operator to `/smh-label-tasks` (SCC-155). Before there
    were two modes the only honest answer was "this is not for me"; now there is a command
    that DOES assess Tasks, and a refusal that does not name it leaves a wrong-mode run
    stuck. The type check runs FIRST, because a Task parent refused for the summary's shape
    ("no `Epic N` in it") is right by accident and says the wrong thing."""
    itype = (parent.get("type") or "").strip().lower()
    # `forced` is an EXPLICIT `--mode story`, and it must bypass this arm specifically.
    # Without that the flag is dead: its own docstring says it exists for "the case the type
    # is wrong on the board", and this is the check that reads that type - so the one input
    # the flag was added to serve was the one it could not, and the refusal handed the
    # operator to the command they had just come from (SCC-155 review finding). Every OTHER
    # gate below still binds; the operator overrode the board's type, not the whole gate.
    if itype and itype != "epic" and not forced:
        wf.die(f"`{parent['key']}` is a {parent.get('type')}, not an Epic. Story mode "
               f"assesses BMAD stories under a BMAD epic. A {parent.get('type')} and its "
               f"Subtasks are Task work — run `{COMMAND['task']} {parent['key']}`. If the "
               f"BOARD is wrong and this really is a BMAD epic, force it with `--mode "
               f"story`.", 2)
    stories_dir = repo / wf.STORIES_REL
    if not stories_dir.is_dir():
        wf.die(f"{repo.name} has no {wf.STORIES_REL}/ — no BMAD stories in this repo yet. "
               f"Story mode assesses BMAD stories only; for Task work run "
               f"`{COMMAND['task']} <TASK-KEY>`.", 2)
    num = bmad_epic_number(parent["summary"])
    if num:
        return num
    epics = repo / wf.EPICS_REL
    if epics.is_file() and parent["summary"].strip():
        head = parent["summary"].split("—")[0].strip()
        if head and head.lower() in wf.read_text(epics).lower():
            return head
    wf.die(f"`{parent['key']} {parent['summary']}` is a GROUPING epic, not a BMAD epic. "
           f"Story mode assesses BMAD stories under a BMAD epic; a grouping epic's children "
           f"are Tasks with no story files. Assess one of those Tasks and its Subtasks with "
           f"`{COMMAND['task']} <TASK-KEY>`.", 2)
    raise AssertionError  # unreachable


def gate_task(parent: dict) -> None:
    """Task mode's mirror of `gate_bmad`, and deliberately much thinner.

    There is no artifact to demand up front: a Task lane's grounding is a branch, a plan or
    the ticket text, and `ground_child` decides that per child. The ONE thing worth refusing
    here is the container — an Epic's children are Stories (or Tasks that each own their own
    Subtasks), so assessing them as one flat set answers a question nobody asked."""
    itype = (parent.get("type") or "").strip().lower()
    if itype in ("epic", ""):
        wf.die(f"`{parent['key']} {parent.get('summary', '')}` is an "
               f"{parent.get('type') or 'untyped container'}, not a Task. Task mode assesses "
               f"the Subtasks under ONE Task. For a BMAD epic's stories run "
               f"`{COMMAND['story']} {parent['key']}`; for a grouping epic, run this against "
               f"one of its Tasks.", 2)
    # The third leg, without which the two gates do not actually refuse INTO each other:
    # `gate_bmad` hands a Subtask parent here saying "a Subtask and its Subtasks are Task
    # work", this arm used to ACCEPT it, and the run then died on "no children on the board".
    # `hierarchyLevel: -1` is the floor - nothing nests under a Subtask - so the honest
    # answer names the parent Task instead (SCC-155 review finding).
    if itype == "subtask":
        wf.die(f"`{parent['key']}` is a Subtask, and nothing nests under one — it is the "
               f"bottom of the hierarchy, so it has no children to assess. Run this against "
               f"its parent Task instead.", 2)
    return None


# ── grounding ──────────────────────────────────────────────────────────────────

def epic_base_ref(repo: Path, parent_key: str) -> str:
    """A story branch's base is THIS epic's branch when one is live, else main.

    NEVER another epic's branch. The retired spec assumed "exactly one live epic branch is the
    normal case" and fell back to it — but AGY has two live right now
    (`epic/AVCH-18-adk-2x-runtime`, `epic/AVCH-23-thin-toolkit`), so that fallback would diff
    every AVCH-13 story against an unrelated epic and invent overlap out of nothing. The key
    is right there in the branch name; match it or use main."""
    r = wf.git(["for-each-ref", "--format=%(refname:short)", "refs/heads/epic/*"], repo)
    for line in (r.stdout or "").splitlines():
        if parent_key.lower() in line.lower():
            return line.strip()
    return "main"


def story_branch(repo: Path, key: str) -> str | None:
    r = wf.git(["for-each-ref", "--format=%(refname:short)", "refs/heads/"], repo)
    for line in (r.stdout or "").splitlines():
        b = line.strip()
        if b and re.search(rf"/{re.escape(key)}-", b + "-"):
            return b
    return None


def find_plan(repo: Path, story: str) -> Path | None:
    """An `implementation_plan.md` whose owning directory slug matches this story id. Layout
    varies by epic, so match the SLUG rather than hardcoding `_artifacts/epic_N/story-N-M/`."""
    art = repo / "_artifacts"
    if not art.is_dir():
        return None
    want = wf.norm_id(story)
    for p in sorted(art.rglob("implementation_plan.md")):
        slug = wf.norm_id(p.parent.name.replace("story-", ""))
        if wf.slug_matches(want, slug) or wf.slug_matches(slug, want):
            return p
    return None


_TASK_KEY_RE = re.compile(r'^\s*task_key\s*:\s*["\']?([A-Za-z][A-Za-z0-9]*-\d+)["\']?\s*$',
                          re.MULTILINE)


def find_task_plan(repo: Path, key: str) -> Path | None:
    """A Task lane's plan, joined by DECLARATION — the sibling `task.yaml`'s `task_key`.

    The story side matches a plan directory by slug, which cannot work here: a Task lane's
    folder is `<date>_<slug>` with no key in it. Every Task lane already writes a `task.yaml`
    naming its key, and that manifest is the join the rest of this toolkit governs on
    (`check_gate` resolves a walkthrough's authority exactly this way), so reuse it.

    The match is EXACT, never a prefix: `SCC-14` must not be grounded by `SCC-146`'s manifest.
    That substring collision has already misfired in this repo once, in check_gate's own
    verdict pool, and the regex anchors the number's end to keep it from recurring here."""
    want = key.strip().upper()
    art = repo / "_artifacts"
    if art.is_dir():
        for manifest in sorted(art.rglob("task.yaml")):
            m = _TASK_KEY_RE.search(wf.read_text(manifest))
            if not m or m.group(1).strip().upper() != want:
                continue
            plan = manifest.parent / "implementation_plan.md"
            if plan.is_file():
                return plan
    return None


def find_task_plan_on_branch(repo: Path, key: str, branch: str) -> str | None:
    """The lane's plan read out of its OWN branch — the repo-relative path, or None.

    ⭐ SCC-155 review finding #15. `find_task_plan` above searches the CURRENT checkout, and
    for the flow this engine was built to serve that is the wrong tree: `/smh-plan-task`
    commits each lane's `implementation_plan.md` + `task.yaml` to **that lane's branch** and
    pushes, merging nothing. So the manifest is not in `repo/_artifacts` on any branch but its
    own, and rung 2 - the rung `smh-plan-task.md` calls "not optional, this is what grounds
    the lane for the labeller" - could never fire for the lanes the planner had just created.

    `git ls-tree` reads the branch without checking it out, so this stays a read-only pass
    over a repo whose worktree belongs to somebody else."""
    r = wf.git(["ls-tree", "-r", "--name-only", branch, "_artifacts/"], repo)
    if r.returncode != 0:
        return None
    manifests = [ln.strip() for ln in (r.stdout or "").splitlines()
                 if ln.strip().endswith("/task.yaml")]
    want = key.strip().upper()
    for manifest in sorted(manifests):
        show = wf.git(["show", f"{branch}:{manifest}"], repo)
        if show.returncode != 0:
            continue
        m = _TASK_KEY_RE.search(show.stdout or "")
        if not m or m.group(1).strip().upper() != want:
            continue
        plan = manifest.rsplit("/", 1)[0] + "/implementation_plan.md"
        if wf.git(["cat-file", "-e", f"{branch}:{plan}"], repo).returncode == 0:
            return plan
    return None


def mark_umbrellas(children: list[dict], mode: str = "story") -> None:
    """A child whose BMAD number is a strict prefix of another child's is an UMBRELLA — it
    contains its siblings rather than competing with them, so it is never a candidate.

    ⭐ STORY MODE ONLY (SCC-155 review finding #19). An umbrella is a BMAD numbering concept,
    and this keys off `story_id_of(summary)`. Run against Subtasks, a summary that merely
    starts "2.1" beside one starting "2.1.1" made the first an umbrella - which means NO
    verdict row and NO LABEL WRITE AT ALL for it. Silently dropping a child out of a
    labelling pass is the precise failure this engine exists to prevent, so task mode does
    not get the behaviour rather than getting a careful version of it.

    Found by the first live run: `AVCH-14  12.3 — Igor Full-Checkride (Umbrella)` matched all
    EIGHT `story-12-3-*.md` files, because story-file lookup is prefix-based on purpose. Left
    alone it inherits the union of its siblings' touch-sets, collides with every one of them,
    and sits at a permanent lock while double-counting work already tracked as AVCH-15/16.

    Purely local — no extra board query — and it reads the decomposition off the numbering
    scheme every BMAD project shares. Umbrellas render as a context line, never a verdict row,
    the same way the retired board treated an in-flight story."""
    for c in children:
        c["umbrella"] = False
    if mode != "story":
        return
    ids = {c["key"]: (c.get("story_id") or "") for c in children}
    for c in children:
        mine = ids[c["key"]]
        kids = sorted(k for k, other in ids.items()
                      if k != c["key"] and mine and other.startswith(mine + "."))
        c["umbrella"] = bool(kids)
        if kids:
            c["contains"] = kids


def ground_child(repo: Path, child: dict, base: str, mode: str = "story",
                 parent_key: str = "") -> dict:
    """Authority order, first available wins: branch diff > implementation_plan > the
    declaration of intent. Code written beats every declaration; a declaration beats an
    intention. Only the third rung differs by mode — a story has a story file, a Subtask has
    the description `/smh-plan-task` wrote onto it."""
    sources: list[dict] = []
    sid = child.get("story_id")

    branch = story_branch(repo, child["key"])
    if branch:
        r = wf.git(["diff", "--name-only", f"{base}...{branch}"], repo)
        if r.returncode == 0:
            paths = [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]
            # ⭐ SCC-155 review finding #16. A branch whose diff is ENTIRELY planning
            # artifacts is not "code written" - it is the plan, one rung down, wearing rung
            # one's authority. Every lane `/smh-plan-task` cuts looks exactly like this
            # (`implementation_plan.md` + `task.yaml`, nothing else), and `source_paths`
            # strips all of it, so the touch-set derived from this rung is EMPTY - disjoint
            # from every sibling, and every planned lane came back 🟢. A manufactured green
            # on the command's own happy path, which is the one thing Rule 3 exists to stop.
            # An empty diff is the same story: nothing written is not evidence of scope.
            if source_paths({"paths": paths}):
                sources.append({"kind": "branch-diff", "ref": f"{base}...{branch}",
                                "paths": paths})

    if mode == "task":
        plan = find_task_plan(repo, child["key"])
        rel = str(plan.relative_to(repo)) if plan else None
        # The lane's own branch is where `/smh-plan-task` left it (finding #15); the current
        # checkout is only the fallback for a plan that has already landed.
        if not rel and branch:
            rel = find_task_plan_on_branch(repo, child["key"], branch)
        if rel:
            sources.append({"kind": "plan", "path": rel,
                            "ref": branch if not plan else None,
                            "read": "the 'Modify/Add' lines AND every source path under "
                                    "'## Self-Audit' (that section exists to catch the edit "
                                    "sites the plan missed)"})
        # The third rung is the ticket itself. It is the WEAKEST evidence in the ladder and
        # it is still evidence: a Subtask minted by /smh-plan-task carries its checkable list
        # in the description. Rule 3 governs what to do with its ambiguity - when the text
        # will not say whether a file is edited, count it as an edit and let the set lock.
        elif (child.get("description") or "").strip():
            sources.append({"kind": "ticket", "path": f"{child['key']} description",
                            "read": "the ACCEPTANCE block and any named path; ambiguity "
                                    "counts as an EDIT (fail toward locked)"})
    elif sid:
        plan = find_plan(repo, sid)
        if plan:
            sources.append({"kind": "plan", "path": str(plan.relative_to(repo)),
                            "read": "the 'Modify/Add' lines AND every source path under "
                                    "'## Self-Audit' (that section exists to catch the edit "
                                    "sites the plan missed)"})
        for f in wf.find_story_files(repo, sid):
            sources.append({"kind": "story", "path": str(f.relative_to(repo)),
                            "read": "Dev Notes surfaces, task paths, and NEGATIVE "
                                    "declarations ('no X changes, that is 19.2')"})

    child["sources"] = sources
    child["authority"] = sources[0]["kind"] if sources else None
    child["grounded"] = bool(sources)
    if not child["grounded"]:
        if mode == "task":
            child["reason"] = "no lane branch, no plan, no description"
            child["next_command"] = f"/smh-plan-task {parent_key}" if parent_key else None
        else:
            child["reason"] = (f"no story file for {sid}" if sid
                               else f"{child['key']} carries no BMAD number in its summary")
            child["next_command"] = (f"/cicd-write-story-tests {sid}" if sid else None)
    return child


# ── plan ───────────────────────────────────────────────────────────────────────

def resolve_mode(parent: dict, explicit: str | None) -> str:
    """Story mode or task mode, DERIVED from the parent's type unless the caller insists.

    Deriving it is what makes a wrong-mode run impossible to start rather than merely
    refused: an Epic's children are stories, a Task's children are subtasks, and the board
    already knows which one this is. `--mode` stays for the case the type is wrong on the
    board — it does not skip the gate, which still refuses a mismatch by name."""
    if explicit:
        return explicit
    return "task" if (parent.get("type") or "").strip().lower() != "epic" else "story"


def cmd_plan(args) -> int:
    binary = acli_bin(args.acli)
    repo = repo_for_key(args.parent, args.repo)
    parent = parent_facts(binary, args.parent)
    mode = resolve_mode(parent, args.mode)
    epic_num = None
    if mode == "story":
        epic_num = gate_bmad(parent, repo, forced=bool(args.mode))
    else:
        gate_task(parent)

    data = acli_json(binary, ["jira", "workitem", "search", "--json",
                              "--fields", "key,summary,status,labels,description",
                              "--jql", f"parent = {args.parent} ORDER BY key"])
    rows = [r for r in (data if isinstance(data, list) else []) if isinstance(r, dict)]
    if not rows:
        wf.die(f"{args.parent} has no children on the board — nothing to assess.", 2)

    # A Task lane branches off main; only a BMAD story sits under an epic branch.
    base = epic_base_ref(repo, args.parent) if mode == "story" else "main"
    children = []
    for row in rows:
        f = row.get("fields") or {}
        status = (f.get("status") or {})
        cat = ((status.get("statusCategory") or {}).get("key") or "").lower()
        child = {"key": row.get("key", ""), "summary": f.get("summary") or "",
                 "status": status.get("name") or "", "category": cat,
                 "labels": list(f.get("labels") or []),
                 "description": adf_text(f.get("description")),
                 "terminal": cat == "done", "in_flight": cat == "indeterminate"}
        child["story_id"] = story_id_of(child["summary"])
        children.append(child)

    mark_umbrellas(children, mode)
    for child in children:
        if not child["terminal"] and not child["umbrella"]:
            ground_child(repo, child, base, mode, parent["key"])

    packet = {"parent": parent["key"], "parent_summary": parent["summary"],
              "epic": epic_num, "mode": mode, "repo": str(repo), "base": base,
              "children": children,
              "child_keys": sorted(c["key"] for c in children)}

    out = json.dumps(packet, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
        say(f"work packet -> {args.out}")
    else:
        print(out)

    umbrellas = [c for c in children if c.get("umbrella")]
    live = [c for c in children if not c["terminal"] and not c.get("umbrella")]
    grounded = [c for c in live if c.get("grounded")]
    what = f"Epic {epic_num}" if mode == "story" else "Task"
    say(f"\n{parent['key']} ({what}) in {repo.name}: {len(children)} children, "
        f"{len(live)} assessable, {len(grounded)} grounded, base {base}")
    for c in umbrellas:
        say(f"  [UMBRELLA] {c['key']} ({c['story_id']}) contains "
            + ", ".join(c["contains"]) + " - not a candidate")
    # The console verdict must match the BOARD verdict `cmd_resolve` emits for the same
    # child. It printed `[NO-STORY]` in both modes while the comment said `no plan` - two
    # names for one verdict in one run, and "story" is the word task mode exists to say does
    # not apply here (SCC-155 review finding).
    ungrounded = "[NO-PLAN]" if mode == "task" else "[NO-STORY]"
    for c in live:
        if not c.get("grounded"):
            say(f"  {ungrounded} {c['key']}: {c.get('reason')}"
                + (f" -> {c['next_command']}" if c.get("next_command") else ""))
    return 0 if grounded else 1


# ── resolve: the set math ──────────────────────────────────────────────────────

def source_paths(entry: dict) -> set[str]:
    """Planning artifacts never count as overlap — only source paths decide."""
    raw = list(entry.get("paths") or []) + list(entry.get("creates") or [])
    out = set()
    for p in raw:
        p = str(p).strip().lstrip("./")
        if not p or p.startswith(PLANNING_PREFIXES):
            continue
        out.add(p)
    return out


def conflict_graph(candidates: list[str], touch: dict) -> dict[str, dict[str, str]]:
    """key -> {other_key: the reason they collide}. Reasons are kept because a verdict without
    its evidence is an assertion, and extraction from a story file is a judgment."""
    g: dict[str, dict[str, str]] = {k: {} for k in candidates}
    paths = {k: source_paths(touch.get(k) or {}) for k in candidates}
    creates = {k: {str(c).strip().lstrip("./") for c in (touch.get(k) or {}).get("creates") or []}
               for k in candidates}
    imports = {k: {str(i).strip() for i in (touch.get(k) or {}).get("imports") or []}
               for k in candidates}
    for a in candidates:
        for b in candidates:
            if a >= b:
                continue
            shared = sorted(paths[a] & paths[b])
            if shared:
                why = f"both touch {shared[0]}" + (f" (+{len(shared) - 1} more)"
                                                   if len(shared) > 1 else "")
                g[a][b] = g[b][a] = why
                continue
            # add/add on a new file has no merge base, so an import edge is a conflict even
            # with zero file overlap today.
            hit = sorted({s for s in imports[a] if any(s in c or c in s for c in creates[b])})
            if hit:
                g[a][b] = g[b][a] = f"{a} imports `{hit[0]}`, which {b} creates"
                continue
            hit = sorted({s for s in imports[b] if any(s in c or c in s for c in creates[a])})
            if hit:
                g[a][b] = g[b][a] = f"{b} imports `{hit[0]}`, which {a} creates"
    # declared dependencies are conflicts regardless of files
    for a in candidates:
        for dep in (touch.get(a) or {}).get("blocked_by") or []:
            dep = str(dep).strip()
            if dep in g:
                g[a][dep] = g[dep][a] = f"{a} declares blocked_by: {dep}"
    return g


def largest_disjoint(candidates: list[str], g: dict[str, dict[str, str]]) -> list[str]:
    """The largest set in which EVERY pair is disjoint. Exhaustive with pruning — N is a
    handful of stories, and a deterministic answer matters more than speed: same input must
    give the same set every run, or the stamp means nothing."""
    keys = sorted(candidates)
    best: list[str] = []

    def expand(current: list[str], rest: list[str]) -> None:
        nonlocal best
        if len(current) + len(rest) <= len(best):
            return
        if not rest:
            if len(current) > len(best):
                best = list(current)
            return
        head, tail = rest[0], rest[1:]
        expand(current + [head], [k for k in tail if k not in g[head]])
        expand(current, tail)

    expand([], keys)
    return sorted(best)


def quick_dev_of(entry: dict) -> tuple[bool | None, str]:
    """(the decision, its evidence) for one touch-set. **Absent means UNASSESSED, not False.**

    A pass that never looked at quick-dev eligibility must leave the label alone — see
    `label_plan`. Reading a missing key as "not eligible" would make every re-run strip the
    label off work somebody marked deliberately, which is the rot this engine exists to
    avoid, pointed at the other field."""
    q = entry.get("quick_dev")
    if not isinstance(q, dict) or "eligible" not in q:
        return None, ""
    return bool(q.get("eligible")), str(q.get("evidence") or "")


def cmd_resolve(args) -> int:
    packet = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    touch = json.loads(Path(args.touchsets).read_text(encoding="utf-8"))
    children = packet["children"]
    mode = packet.get("mode") or "story"

    live = [c for c in children if not c.get("terminal") and not c.get("umbrella")]
    umbrellas = [{"key": c["key"], "story_id": c.get("story_id"),
                  "contains": c.get("contains", [])}
                 for c in children if c.get("umbrella")]
    grounded = [c for c in live if c.get("grounded")]
    missing = [c["key"] for c in grounded if c["key"] not in touch]
    if missing:
        wf.die("no touch-set supplied for: " + ", ".join(missing)
               + " — every grounded child must be extracted, or the set math is a guess.", 2)

    candidates = sorted(c["key"] for c in grounded)
    g = conflict_graph(candidates, touch)
    # blocked_by is DIRECTIONAL: a declarer never enters the approved set while its
    # blocker is a live sibling in this run - dependents follow, they never displace.
    # Stored symmetric alone, the edge let the solver maximize set size by seating
    # the declarers and locking the prerequisite behind them (measured 2026-08-20:
    # SCC-227, declaring blocked_by SCC-226, came back approved with SCC-226 "after
    # SCC-227"). The edge stays in g so the lock row can name the blocker; candidacy
    # is what direction removes. A blocker OUTSIDE the run (landed or foreign) keeps
    # its declarer free - conflict_graph already ignores those, and so does this.
    followers = {k for k in candidates
                 if any(str(d).strip() in g
                        for d in (touch.get(k) or {}).get("blocked_by") or [])}
    approved = largest_disjoint([k for k in candidates if k not in followers], g)

    # An ungrounded IN-FLIGHT sibling has unknown surfaces. Nothing can be proved disjoint
    # from unknown ground, and this fails toward locked: a false green puts two lanes on the
    # same line, a false lock costs only serialisation.
    unknown = sorted(c["key"] for c in live
                     if c.get("in_flight") and not c.get("grounded"))

    verdicts = []
    for c in sorted(live, key=lambda x: x["key"]):
        k = c["key"]
        if not c.get("grounded"):
            # Ungrounded work is not quick-dev-eligible either — nobody can size a lane they
            # cannot see. Explicit False, not None: this pass DID assess it and the answer is
            # no, so a stale label comes off.
            verdicts.append({"key": k, "verdict": "no-plan" if mode == "task" else "no-story",
                             "mark": "📝", "detail": c.get("reason", "ungrounded"),
                             "command": c.get("next_command"), "quick_dev": False,
                             "quick_dev_evidence": "ungrounded — nothing to size",
                             "evidence": "no branch diff, no plan, "
                                         + ("no description" if mode == "task"
                                            else "no story file")})
        elif k in approved and unknown:
            verdicts.append({"key": k, "verdict": "waiting", "mark": "⏳",
                             "detail": "waiting on " + ", ".join(unknown),
                             "evidence": f"{unknown[0]} is in flight with no landed plan — "
                                         f"its surfaces are unknown"})
        elif k in approved:
            verdicts.append({"key": k, "verdict": "approved", "mark": "🟢", "detail": "",
                             "evidence": ", ".join(sorted(source_paths(touch[k]))) or
                                         "no source paths declared"})
        else:
            # A grounded candidate outside the approved set always collides with something in
            # it - otherwise approved + {k} would be a larger disjoint set. The fallbacks are
            # belt-and-braces: an unverdicted row is banned, so there is always an answer.
            blockers = sorted(b for b in g[k] if b in approved) or sorted(g[k])
            if not blockers:
                verdicts.append({"key": k, "verdict": "approved", "mark": "🟢", "detail": "",
                                 "evidence": ", ".join(sorted(source_paths(touch[k])))
                                             or "no source paths declared"})
                continue
            first = blockers[0]
            verdicts.append({"key": k, "verdict": "after", "mark": "🔒",
                             "detail": f"after {first}",
                             "evidence": g[k].get(first, "shares ground")})

    # quick-dev is decided per child by the AGENT, in the touch-set, for the same reason the
    # touch-sets themselves are: "small enough for one light lane" is a judgment about the
    # work, not a number a parser can read off it. The engine only carries the answer, and
    # carries ABSENCE faithfully (None) so an unassessed label survives the write.
    for v in verdicts:
        if "quick_dev" not in v:
            v["quick_dev"], v["quick_dev_evidence"] = quick_dev_of(touch.get(v["key"]) or {})

    stamp = (f"verified {date.today().isoformat()} against {len(packet['child_keys'])} "
             f"children: {', '.join(packet['child_keys'])}")
    result = {"parent": packet["parent"], "epic": packet.get("epic"), "mode": mode,
              "repo": packet.get("repo"), "approved": [] if unknown else approved,
              "unknown_in_flight": unknown, "umbrellas": umbrellas, "verdicts": verdicts,
              "child_keys": packet["child_keys"], "stamp": stamp}

    out = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
        say(f"verdicts -> {args.out}")
    else:
        print(out)
    return 0


# ── stamp: labels + the one comment ────────────────────────────────────────────

def render_comment(res: dict) -> str:
    lines = [f"**{MARKER}** — {res['stamp']}", ""]
    if res["approved"]:
        lines += [f"🧵 **Approved to run in parallel ({len(res['approved'])}):** "
                  + " · ".join(res["approved"]), ""]
    elif res.get("unknown_in_flight"):
        lines += ["🧵 **Nothing approved** — " + ", ".join(res["unknown_in_flight"])
                  + " is in flight with no landed plan, so no sibling can be proved disjoint "
                    "from it. Land that plan and re-run.", ""]
    else:
        lines += ["🧵 **Nothing approved.**", ""]
    # Context lines, never verdict rows — an umbrella contains its siblings rather than
    # competing with them, so a verdict on it would double-count work already in the table.
    for u in res.get("umbrellas") or []:
        lines += [f"_{u['key']} ({u['story_id']}) is an umbrella over "
                  + ", ".join(u["contains"]) + " — assessed as those, not as itself._", ""]
    mode = res.get("mode") or "story"
    lines += ["| Ticket | Verdict | Quick-dev | Evidence |", "|---|---|---|---|"]
    for v in res["verdicts"]:
        mark = {"approved": "🟢 approved", "after": f"🔒 {v['detail']}",
                "waiting": f"⏳ {v['detail']}", "no-story": "📝 no story",
                "no-plan": "📝 no plan"}[v["verdict"]]
        q = {True: "⚡ yes", False: "—", None: ""}[v.get("quick_dev")]
        if v.get("quick_dev") and v.get("quick_dev_evidence"):
            q += f" ({v['quick_dev_evidence']})"
        eve = v["evidence"] + (f" → `{v['command']}`" if v.get("command") else "")
        lines.append(f"| {v['key']} | {mark} | {q} | {eve} |")
    unit = "story" if mode == "story" else "subtask"
    lines += ["", f"_A verdict is a SNAPSHOT. Writing another {unit} invalidates it — re-run "
                  f"`{COMMAND[mode]} " + res["parent"] + "`._"]
    return "\n".join(lines)


def label_plan(current: list[str],
               wanted: dict[str, bool | None]) -> tuple[list[str], list[str]]:
    """(the full label set to write, the actions taken) — pure, no I/O.

    TRI-STATE per label, and the third state is the one that matters: True adds, False
    strips, and **None leaves it exactly as it is**. A boolean cannot say "this pass did not
    assess that label", so a bool would force every run to take a position on `quick-dev` —
    including the runs whose touch-sets never mentioned it, which would silently strip the
    label off work the operator had marked by hand."""
    have = set(current)
    want = set(current)
    actions = []
    for label, decision in sorted(wanted.items()):
        if decision is None:
            continue
        if decision and label not in have:
            want.add(label)
            actions.append(f"+{label}")
        elif not decision and label in have:
            want.discard(label)
            actions.append(f"-{label}")
    return sorted(want), actions


def set_labels(binary: str, key: str, current: list[str],
               wanted: dict[str, bool | None], apply: bool) -> str | None:
    """Add with `--labels`, strip with `--remove-labels`. The strip is the point: a child that
    WAS approved and now overlaps must lose the label on re-run — that is what makes a
    parent-scoped writer self-correcting where a per-story one rotted.

    ⛔ THE STRIP HAD NEVER WORKED ON THE BOARD (SCC-202, found by a review lens on SCC-197).
    This docstring used to open "`acli workitem edit --labels` REPLACES the set, so preserve
    everything else", and the writer below sent the reduced set accordingly. Measured against
    the live board 2026-08-17: **`--labels` ADDS.** Against an adding API, "send the set minus
    X" re-adds every surviving label as a no-op and removes nothing — exit 0, and the label
    stays on. `set_labels` then returned `-parallel-ok` as a completed action.

    Not cosmetic: a story that WAS `parallel-ok` and now overlaps keeps the tag while
    `/cicd-label-tasks` reports it removed, which is exactly how two colliding lanes get run
    side by side (`lane-collision-is-gates-not-files`). Same false belief as `jira_feed.py`'s
    `user-tasks` strip — this was the third site, and the only one on the command that does
    real project work."""
    want, actions = label_plan(current, wanted)
    if not actions:
        return None
    if apply:
        # Both directions derived from the plan, rather than trusting one flag to do both.
        adds = [x for x in want if x not in current]
        removes = [x for x in current if x not in want]
        cmd = ["jira", "workitem", "edit", "--key", key, "--yes"]
        if adds:
            cmd += ["--labels", ",".join(adds)]
        if removes:
            cmd += ["--remove-labels", ",".join(removes)]
        r = acli(binary, cmd)
        if r.returncode != 0:
            warn(f"{key}: label update failed — {(r.stderr or r.stdout).strip()[:160]}")
            return None
    # Space-joined, NOT comma-joined: the caller joins one ticket's report to the next with
    # ", ", so a comma in here makes `A +parallel-ok, +quick-dev, B +parallel-ok` unreadable —
    # nothing tells you the second entry is still A's.
    return " ".join(actions)


def cmd_stamp(args) -> int:
    # Resolve the CLI only when we are actually going to call it. Every use of `binary` below
    # is guarded by `apply`, so a dry run never touches it — yet resolving it up front made
    # `stamp` die with "acli not found" on any machine that has no acli, for a binary it was
    # never going to invoke. That is a dependency on the OPERATOR'S MACHINE hiding inside a
    # command whose whole purpose is to preview without writing, and it made this script
    # unrunnable on a CI runner (found by SCC-118, when the suite first ran off a laptop).
    binary = acli_bin(args.acli) if args.apply else (args.acli or "")
    res = json.loads(Path(args.verdicts).read_text(encoding="utf-8"))
    packet = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    by_key = {c["key"]: c for c in packet["children"]}
    approved = set(res["approved"])

    changes = []
    for v in res["verdicts"]:
        c = by_key.get(v["key"]) or {}
        act = set_labels(binary, v["key"], c.get("labels") or [],
                         {LABEL: v["key"] in approved, QUICK: v.get("quick_dev")},
                         args.apply)
        if act:
            changes.append(f"{v['key']} {act}")

    body = render_comment(res)
    posted = False
    if args.apply:
        r = acli(binary, ["jira", "workitem", "comment", "create",
                          "--key", res["parent"], "--body", body])
        posted = r.returncode == 0
        if not posted:
            warn(f"comment failed — {(r.stderr or r.stdout).strip()[:200]}")

    say(body)
    say("")
    say(f"labels: {', '.join(changes) if changes else 'no change'}"
        + ("" if args.apply else "   (dry run — pass --apply to write)"))
    if args.apply:
        say(f"comment on {res['parent']}: {'posted' if posted else 'FAILED'}")
        return 0 if posted else 2
    return 0


# ── check: is the stamp still valid? ───────────────────────────────────────────

def cmd_check(args) -> int:
    binary = acli_bin(args.acli)
    # ⭐ `check` publishes a TWO-state contract in both command bodies: `[FRESH]` (0) or
    # `[STALE]` (1). `parent_facts` dies with exit 2 when the board cannot be read, so
    # routing the mode through it gave a read-only staleness verb a third exit nobody
    # documents - and on a dropped uplink it died before reading a single comment. The type
    # is only ever used to pick which command name to print, so a failure to read it degrades
    # to the derived default instead of taking the whole verb down (SCC-155 review #20).
    try:
        mode = resolve_mode(parent_facts(binary, args.parent), args.mode)
    except SystemExit:
        mode = args.mode or "story"
    data = acli_json(binary, ["jira", "workitem", "comment", "list",
                              "--key", args.parent, "--json"])
    comments = data if isinstance(data, list) else (
        (data or {}).get("comments") if isinstance(data, dict) else []) or []
    stamped: str | None = None
    for c in comments:
        text = adf_text(c.get("body"))
        if MARKER in text and "verified" in text:
            stamped = text
    if not stamped:
        say(f"[STALE] {args.parent} has never been checked — run {COMMAND[mode]}")
        return 1

    m = re.search(r"verified (\d{4}-\d{2}-\d{2}) against \d+ children: ([^\n_*]+)", stamped)
    if not m:
        say(f"[STALE] {args.parent} carries a {MARKER} comment with no readable stamp")
        return 1
    when, was = m.group(1), sorted(k.strip() for k in m.group(2).split(",") if k.strip())

    # `--fields "key"` ALONE returns `[null, null, null]` — one null per child. `key` is a
    # top-level property of the issue, not a requestable field, so asking for only it
    # materializes nothing. Ask for a real field alongside it. Found live 2026-08-09; it
    # crashed this verb while `plan` (which already asked for summary+status) was fine.
    rows = acli_json(binary, ["jira", "workitem", "search", "--json", "--fields",
                              "key,summary",
                              "--jql", f"parent = {args.parent} ORDER BY key"])
    now = sorted(child_keys(rows))
    if not now:
        say(f"[STALE] {args.parent} returned no children to compare the stamp against")
        return 1

    if was == now:
        say(f"[FRESH] {args.parent} verified {when} against the same {len(now)} children")
        return 0
    say(f"[STALE] {args.parent} was verified {when} against {len(was)} children, "
        f"but the parent now has {len(now)}")
    for k in sorted(set(now) - set(was)):
        say(f"  + {k} (added since)")
    for k in sorted(set(was) - set(now)):
        say(f"  - {k} (gone since)")
    say("A stamped set that no longer matches the parent's children is not a verdict. Re-run.")
    return 1


# ── cli ────────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plan", help="enumerate + ground; emits the agent's work packet")
    p.add_argument("--parent", required=True)
    p.add_argument("--mode", choices=("story", "task"),
                   help="default: derived from the parent's type on the board")
    p.add_argument("--repo")
    p.add_argument("--acli")
    p.add_argument("--out")
    p.set_defaults(fn=cmd_plan)

    r = sub.add_parser("resolve", help="the set math; emits verdicts")
    r.add_argument("--plan", required=True)
    r.add_argument("--touchsets", required=True)
    r.add_argument("--out")
    r.set_defaults(fn=cmd_resolve)

    s = sub.add_parser("stamp", help="write labels + the stamped comment")
    s.add_argument("--plan", required=True)
    s.add_argument("--verdicts", required=True)
    s.add_argument("--apply", action="store_true")
    s.add_argument("--acli")
    s.set_defaults(fn=cmd_stamp)

    c = sub.add_parser("check", help="is the existing stamp still valid, or stale?")
    c.add_argument("--parent", required=True)
    c.add_argument("--mode", choices=("story", "task"),
                   help="default: derived from the parent's type on the board")
    c.add_argument("--acli")
    c.set_defaults(fn=cmd_check)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
