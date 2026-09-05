"""Every rule's activation frontmatter must MIRROR the Load column in `.agents/rules/INDEX.md`.

Two platforms load rules by themselves, and each reads a different field:

  * **Claude Code** reads `paths:` — a rule carrying it loads only when a file matching one of its
    globs is read, and a rule WITHOUT it loads at launch, unconditionally. So `paths:` is not
    decoration: putting it on the wrong rule either buries a gate that must always bind, or drags a
    44 KB protocol rule into every read-only session.
  * **Antigravity** reads `trigger:` — `always_on`, `glob` (with `globs:`), or `model_decision`
    (with a `description:` it judges against the request).

`INDEX.md` stays the single source of the classification (AGENTS.md §3 says the two must agree, and
that if they ever disagree they are both wrong until reconciled). This test is what makes "must
agree" mechanical instead of aspirational:

  floor      -> trigger: always_on      (loaded every session, no condition)
  protocol   -> trigger: model_decision (conditional; their law is ALSO inline in AGENTS.md, which
                                         is why they are not always_on despite being near-mandatory)
  on-demand  -> trigger: glob  + globs: + paths:   when the trigger is a FILE being touched, or
                trigger: model_decision + triggers: when the trigger is an INTENT in the prompt
                (the `triggers:` keyword list is what `.agents/hooks/rule-trigger.py` matches on)

⛔ `paths:` and `always_on`/`protocol` are mutually exclusive by construction: a path-scoped rule is
on-demand by definition. That is asserted, not assumed.

Stdlib only, no pytest — same constraint as everything else in this suite.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir

# _harness puts SCRIPTS on sys.path, so the lobby's own scripts import as top-level
# modules. SCC-399: reuse check_maps' allowlist parser rather than adding a fifth copy.
import check_maps  # noqa: E402  (must follow the _harness path insert)

ROOT = Path(__file__).resolve().parents[3]
RULES = ROOT / ".agents" / "rules"

LOAD_ROW = re.compile(r"^\|\s*`([A-Za-z0-9_.\-]+)\.md`\s*\|\s*([^|]+?)\s*\|", re.M)


def _main_checkout() -> Path:
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--git-common-dir"],
                             capture_output=True, text=True, timeout=10)
        if out.returncode == 0 and out.stdout.strip():
            g = Path(out.stdout.strip())
            if not g.is_absolute():
                g = ROOT / g
            return g.resolve().parent
    except Exception:
        pass
    return ROOT


def _index_loads() -> dict[str, str]:
    """{rule stem: 'floor' | 'protocol' | 'on-demand'} from the INDEX table."""
    out = {}
    for name, load in LOAD_ROW.findall((RULES / "INDEX.md").read_text(encoding="utf-8")):
        low = load.lower()
        out[name] = "floor" if "floor" in low else "protocol" if "protocol" in low else "on-demand"
    return out


def _project_index_loads(index_path: Path) -> dict[str, str]:
    """{rule stem: 'floor' | 'protocol' | 'on-demand'} from a project INDEX table."""
    out = {}
    if not index_path.exists():
        return out
    for name, load in LOAD_ROW.findall(index_path.read_text(encoding="utf-8")):
        low = load.lower()
        out[name] = "floor" if "floor" in low else "protocol" if "protocol" in low else "on-demand"
    return out


def _scan_project_rules(projects_dir: Path, allowed: set[str], tier1_stems: set[str]) -> dict:
    """Audit the MAINTAINED projects' rule sets. Pure function of (dir, allowlist, tier-1 stems).

    Split out of the check body so the allowlist behaviour is provable against a FIXTURE (see
    `_case_allowlist_control`). It could not be proved in place: `Projects/` is a set of submodule
    gitlinks, so it is an empty stub in every `git worktree` and populated only in the main
    checkout - a scan asserted against whatever happens to be on disk passes vacuously in exactly
    the place most work is done. Same reasoning as `test_memory_store.maintained_project_names`.

    `allowed` is the parsed `.agents/maintained-projects.txt` set. A project NOT on it is skipped
    outright - not "skipped unless it looks conformant". That distinction is the whole fix: the
    published teaching edition IS conformant-looking, which is why walking the folder found it.
    """
    out = {"unrouted": [], "dangling": [], "tier1_copies": [], "empty_indexes": [], "scanned": []}
    if not projects_dir.is_dir():
        return out
    for p in sorted(projects_dir.iterdir()):
        if not p.is_dir() or p.name not in allowed:
            continue
        p_agents = p / ".agents"
        p_rules = p_agents / "rules"
        if not p_agents.is_dir() or not p_rules.is_dir():
            continue
        p_index = p_agents / "INDEX.md"
        p_loads = _project_index_loads(p_index)
        p_on_disk = sorted(f for f in p_rules.glob("*.md") if f.name != "INDEX.md")
        out["scanned"].append(p.name)

        if p_on_disk and not p_loads:
            out["empty_indexes"].append(f"{p.name} ({len(p_on_disk)} rules on disk, 0 in INDEX.md)")

        for f in p_on_disk:
            if f.stem not in p_loads:
                out["unrouted"].append(f"{p.name}: {f.name}")
            if f.stem in tier1_stems:
                out["tier1_copies"].append(f"{p.name}: {f.name}")

        for stem in p_loads:
            # template guidance row in the skeleton is permitted if marked "create this first"
            if stem == "constitution.project" and not (p_rules / f"{stem}.md").exists():
                if p_index.exists() and "create this first" in p_index.read_text(encoding="utf-8").lower():
                    continue
            if not (p_rules / f"{stem}.md").exists():
                out["dangling"].append(f"{p.name}: {stem}.md")
    return out


def _frontmatter(path: Path) -> dict[str, object]:
    """Minimal YAML-ish front-matter reader: scalars plus one-level block lists.

    Deliberately not a YAML parser — the toolkit is stdlib-only and these files are hand-written in
    a fixed shape. An unparseable block reads as {}, which every assertion below treats as a failure
    rather than a pass.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data: dict[str, object] = {}
    key = None
    for line in text[3:end].splitlines():
        if not line.strip():
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val.startswith("[") and val.endswith("]"):
                data[key] = [x.strip().strip("\"'") for x in val[1:-1].split(",") if x.strip()]
            elif val:
                data[key] = val.strip("\"'")
            else:
                data[key] = []
        elif line.lstrip().startswith("- ") and key is not None:
            data.setdefault(key, [])
            if isinstance(data[key], list):
                data[key].append(line.lstrip()[2:].strip().strip("\"'"))
    return data


def main() -> int:
    c = Cases("rule_frontmatter")
    loads = _index_loads()
    on_disk = sorted(p for p in RULES.glob("*.md") if p.name != "INDEX.md")

    c.check("every rule on disk has a Load row in INDEX.md",
            all(p.stem in loads for p in on_disk),
            str(sorted(p.stem for p in on_disk if p.stem not in loads)))
    c.check("every INDEX row points at a rule that exists",
            all((RULES / f"{n}.md").exists() for n in loads),
            str(sorted(n for n in loads if not (RULES / f"{n}.md").exists())))

    missing_trigger, wrong, no_globs, no_triggers, path_conflict, no_desc = [], [], [], [], [], []
    for p in on_disk:
        fm = _frontmatter(p)
        load = loads.get(p.stem)
        trig = fm.get("trigger")
        if not fm.get("description"):
            no_desc.append(p.stem)
        if not trig:
            missing_trigger.append(p.stem)
            continue
        if load in ("floor", "protocol"):
            expected = "always_on" if load == "floor" else "model_decision"
            if trig != expected:
                wrong.append(f"{p.stem}: {load} -> trigger={trig!r}, expected {expected!r}")
            if fm.get("paths"):
                path_conflict.append(f"{p.stem}: {load} must not carry paths:")
        else:  # on-demand
            if trig == "glob":
                if not fm.get("globs"):
                    no_globs.append(p.stem)
                if not fm.get("paths"):
                    no_globs.append(f"{p.stem} (no paths: for Claude Code)")
            elif trig == "model_decision":
                if not fm.get("triggers"):
                    no_triggers.append(p.stem)
            else:
                wrong.append(f"{p.stem}: on-demand -> trigger={trig!r}, expected 'glob' or 'model_decision'")

    c.check("every rule carries a trigger:", not missing_trigger, str(missing_trigger))
    c.check("every rule keeps its description: (Antigravity model_decision judges on it)",
            not no_desc, str(no_desc))
    c.check("floor -> always_on, protocol -> model_decision", not wrong, str(wrong))
    c.check("a glob rule carries BOTH globs: (Antigravity) and paths: (Claude Code)",
            not no_globs, str(no_globs))
    c.check("an intent rule carries a triggers: keyword list (the hook matches on it)",
            not no_triggers, str(no_triggers))
    c.check("⛔ floor/protocol rules never carry paths: (path-scoped IS on-demand)",
            not path_conflict, str(path_conflict))

    # The generated Claude Code copies must exist for exactly the path-scoped rules — no more, no less.
    claude_rules = ROOT / ".claude" / "rules"
    want = {p.stem for p in on_disk if _frontmatter(p).get("paths")}
    have = {p.stem for p in claude_rules.glob("*.md")} if claude_rules.is_dir() else set()
    c.check(".claude/rules/ mirrors exactly the path-scoped masters",
            want == have, f"missing={sorted(want - have)} extra={sorted(have - want)}")

    # ⛔ A RELATIVE LINK THAT RESOLVES IN THE MASTER CAN DANGLE IN THE MIRROR, and the mirror is the
    # copy Claude Code actually loads. `.agents/rules/` holds all 25 rules; `.claude/rules/` holds
    # only the path-scoped ones, so `[x](project-law.md)` resolves beside the master and points at
    # nothing beside the copy. Found by SCC-270's own review, in the six mirrors that lane created.
    # Both directories sit two levels below the repo root, so `../../.agents/rules/<x>.md` is the
    # one spelling that resolves from BOTH — which is what this pins.
    link = re.compile(r"\[[^\]]*\]\(([^)\s#]+)")
    dangling = []
    for mirror in sorted(claude_rules.glob("*.md")) if claude_rules.is_dir() else []:
        for i, line in enumerate(mirror.read_text(encoding="utf-8").splitlines(), 1):
            for m in link.finditer(line):
                target = m.group(1)
                if target.startswith(("http", "mailto:", "#")) or "<" in target:
                    continue
                if not (mirror.parent / target).resolve().exists():
                    dangling.append(f"{mirror.name}:{i} -> {target}")
    c.check("⛔ no relative link in a GENERATED .claude/rules/ copy dangles",
            not dangling, str(dangling))


    # ── §Nag: the ruling that a repeatedly-broken rule gets a HOOK, not a sixth copy (SCC-369) ──
    # This lives here because the failure it prevents is a rule-shape failure: the reflex on a
    # violated rule is to restate it somewhere new, and `command-shape.md` is the measured proof
    # that restating does nothing (five copies, and 23.3% of every Bash call still breaking it).
    shape = (RULES / "command-shape.md").read_text(encoding="utf-8")
    c.check("command-shape.md carries the §Nag section (the SCC-369 ruling as law)",
            "## §Nag" in shape, "no `## §Nag` heading in command-shape.md")

    # ⛔ Scope the checks below to the SECTION, not the file. Reading the whole file made
    # "§Nag names `shape-guard.py`" actually assert "this file mentions it somewhere" — gutting
    # §Nag while leaving the heading and a stray mention in §Zoo kept every one of them green
    # (SCC-369 review). A check whose label names a section must read that section.
    _start = shape.find("## §Nag")
    _rest = shape[_start + 1:] if _start != -1 else ""
    _next = _rest.find("\n## ")
    nag = shape[_start:_start + 1 + (_next if _next != -1 else len(_rest))] if _start != -1 else ""
    c.check("the §Nag section has a BODY, not just a heading",
            len(nag.split("\n", 1)[-1].strip()) > 400,
            f"§Nag is {len(nag)} chars — a heading with no law under it asserts nothing")

    # A section that names no mechanism is a slogan. Each of these is a thing a reader can open.
    for needed, why in (
        ("shape-guard.py", "the hook that DOES the nagging"),
        ("shape_scan.py", "the measurement — the only feedback loop Zoo gets"),
        ("PostToolUse", "the one channel proven to reach the model"),
    ):
        c.check(f"§Nag names `{needed}` ({why})",
                needed in nag, f"command-shape.md §Nag never mentions {needed}")

    # ⛔ The limit that keeps a nag from becoming a gate. A nag that can block strands a headless
    # run over a style note, and `permissionDecision: \"ask\"` auto-DENIES in auto mode.
    c.check("⛔ §Nag states the never-block limit in the NEGATIVE (a nag is not a gate)",
            "never block" in nag.lower(),
            "§Nag does not say a nag may never block — the limit that keeps it off the "
            "critical path is the one a future editor is most likely to drop")

    c.check("§Nag records that Zoo gets MEASUREMENT, not a nag (Zoo has no hook surface)",
            "Zoo" in nag and "no hook surface" in nag,
            "§Nag must say why Zoo is excluded, or the next reader will try to write one")

    idx_text = (RULES / "INDEX.md").read_text(encoding="utf-8")
    row = [ln for ln in idx_text.splitlines() if ln.startswith("| `command-shape.md`")]
    c.check("rules/INDEX.md's command-shape row points at the nag",
            bool(row) and "shape-guard.py" in row[0],
            f"the INDEX row does not name the hook: {row[:1]}")

    # ── Tier-2 Project rules check (SCC-388 / SCC-391 / SCC-399) ──
    # Every MAINTAINED project under Projects/ carrying an .agents/ directory must:
    # 1. Have a Load row in .agents/INDEX.md for every rule on disk in .agents/rules/
    # 2. Every rule row in .agents/INDEX.md must point to a rule that exists on disk (or be template guidance)
    # 3. Carry NO copies of lobby tier-1 rules (project-law.md)
    # 4. If rules exist on disk, .agents/INDEX.md must not have zero rule rows
    #
    # ⛔ "MAINTAINED" is READ FROM `.agents/maintained-projects.txt`, never from what happens to be
    # on disk (SCC-399). Walking `Projects/*` audited nine repos this lobby does not drive, and the
    # one it hurt was `Projects/sudo-command-center` — the PUBLISHED TEACHING EDITION of this lobby,
    # which ships 28 sanitized rule files ON PURPOSE. All three assertions below fired on it, the
    # "fix" they demanded was deleting 27 files out of a shipped product, and so the suite floor sat
    # red at 72/73 with no legal way to clear it. The allowlist is the existing answer to "which
    # projects does the lobby drive": its own header says "Never hand-loop over `Projects/*`" and
    # `check_maps.fan_out_targets` already obeys it. This was the one fan-out that did not.
    tier1_stems = {p.stem for p in on_disk}
    main_checkout = _main_checkout()
    allowed = check_maps.maintained_projects(main_checkout)

    # None means the allowlist FILE is absent, and that is a LOUD failure — never a fall back to
    # walking every folder. The fallback would silently restore the exact behaviour this check was
    # rewritten to remove, in the one situation where nobody is looking.
    c.check("the maintained-projects allowlist exists (the project scan reads it, never Projects/*)",
            allowed is not None,
            f"missing: {main_checkout / '.agents' / 'maintained-projects.txt'}")

    found = _scan_project_rules(main_checkout / "Projects", allowed or set(), tier1_stems)

    c.check("every project rule on disk has a Load row in that project's .agents/INDEX.md",
            not found["unrouted"], str(found["unrouted"]))
    c.check("every project .agents/INDEX.md row points at a rule that exists",
            not found["dangling"], str(found["dangling"]))
    c.check("⛔ no project carries a copy of a tier-1 lobby rule (project-law.md)",
            not found["tier1_copies"], str(found["tier1_copies"]))
    c.check("no project has zero rule rows in .agents/INDEX.md when rules exist on disk",
            not found["empty_indexes"], str(found["empty_indexes"]))

    # ⛔ COVERAGE, not just a verdict. All four assertions above are satisfied by scanning NOTHING,
    # and `Projects/*` is a set of submodule gitlinks — empty in a fresh clone, empty in a bare CI
    # checkout. "0 findings" and "0 projects looked at" print identically, which is the shape of
    # `suite-red-file-may-have-run-nothing`. So name what was audited, and name what was not and why.
    not_scanned = []
    for name in sorted(allowed or set()):
        if name in found["scanned"]:
            continue
        d = main_checkout / "Projects" / name
        if not (d / ".git").exists():
            not_scanned.append(f"{name}: NOT CHECKED OUT — git submodule update --init -- Projects/{name}")
        else:
            not_scanned.append(f"{name}: checked out, but carries no .agents/rules/ — a maintained project with no tier-2 law")
    print(f"[COVERAGE] project rule sets audited: {', '.join(found['scanned']) or 'NONE'}")
    for row in not_scanned:
        print(f"[SKIP] {row}")
    c.check("every maintained project that IS checked out was actually audited",
            not [r for r in not_scanned if "NOT CHECKED OUT" not in r], str(not_scanned))

    # ── The allowlist control (SCC-399) ──
    # The four checks above went from RED to GREEN by narrowing what they look at, and a narrowing
    # is indistinguishable from a disarming unless something proves the teeth survived. Two fixture
    # projects, IDENTICAL except for one line in the allowlist: the listed one must still fire all
    # four findings, the unlisted one must produce none. That is what makes the exclusion of
    # `Projects/sudo-command-center` a deliberate rule rather than an accident that happens to be
    # quiet today.
    with TempDir() as tmp:
        for name in ("on-list", "off-list"):
            rules = tmp / "Projects" / name / ".agents" / "rules"
            rules.mkdir(parents=True)
            (rules / "jira.md").write_text("copy of a tier-1 rule\n", encoding="utf-8")       # tier-1 copy + unrouted
            (rules.parent / "INDEX.md").write_text("| `ghost.md` | on-demand | x |\n", encoding="utf-8")  # dangling row
        listed = _scan_project_rules(tmp / "Projects", {"on-list"}, {"jira"})
        unlisted = _scan_project_rules(tmp / "Projects", set(), {"jira"})

        c.check("control: a project ON the allowlist still fires all four findings (the teeth survived)",
                listed["scanned"] == ["on-list"]
                and listed["unrouted"] == ["on-list: jira.md"]
                and listed["tier1_copies"] == ["on-list: jira.md"]
                and listed["dangling"] == ["on-list: ghost.md"]
                and listed["empty_indexes"] == [],
                f"a listed project did not fire as expected: {listed}")
        c.check("⛔ control: an identical project OFF the allowlist fires NOTHING and is not scanned",
                unlisted["scanned"] == []
                and not any(unlisted[k] for k in ("unrouted", "dangling", "tier1_copies", "empty_indexes")),
                f"an unlisted project was audited anyway: {unlisted}")

    # ── Protocol size figure in AGENTS.md §3 ──
    agents_md = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    c.check("AGENTS.md §3 protocol-size figure is not stale (~44 KB was 2.1x understated)",
            "~44 KB" not in agents_md,
            "AGENTS.md still says '~44 KB' (measured ~96.6 KB)")

    # ── SCC-404 F: the allowlist's pointer at the project table actually RESOLVES ──
    # ⛔ Row F's original evidence was `check_links` "on the new anchors" - but the allowlist is a
    # `.txt` naming the section in PROSE, so no anchor existed and the check ran on nothing. A
    # pointer between two files is only real if something reads BOTH (SCC-401 review).
    # ⛔ Deliberately UNGUARDED, matching this file: it uses no block guards at all, and adding the
    # first one makes test_suite_runner's ORPHAN walker treat the file as guarded and flag all 25
    # pre-existing checks. Match the file, or convert the whole file - never half of it.
    # (The walker matches the guard call as a literal string, so even naming it in a comment
    #  flips the file. Measured SCC-401 review: writing that call here turned this file red.)
    _allow = ROOT / ".agents" / "maintained-projects.txt"
    _std = ROOT / "docs" / "workspace-standard.md"
    _heading = "### The nine projects — what each one IS"
    _atext = _allow.read_text(encoding="utf-8") if _allow.is_file() else ""
    _stext = _std.read_text(encoding="utf-8") if _std.is_file() else ""
    c.check("F1 the allowlist header names workspace-standard.md as the WHY",
            "docs/workspace-standard.md" in _atext, _atext[:120])
    c.check("F2 ...and the section it names is live in that file, spelled the same way",
            _heading in _stext, f"heading absent from {_std}")
    c.check("F3 CONTROL: not vacuous - an ASCII-hyphen twin does NOT satisfy F2",
            "### The nine projects - what each one IS" not in _stext,
            "an ASCII-hyphen twin exists; the check would pass on either")

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
