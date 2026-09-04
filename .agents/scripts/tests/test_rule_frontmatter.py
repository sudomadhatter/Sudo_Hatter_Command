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

from _harness import Cases

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

    # ── Tier-2 Project rules check (SCC-388 / SCC-391) ──
    # Every maintained project under Projects/ carrying an .agents/ directory must:
    # 1. Have a Load row in .agents/INDEX.md for every rule on disk in .agents/rules/
    # 2. Every rule row in .agents/INDEX.md must point to a rule that exists on disk (or be template guidance)
    # 3. Carry NO copies of lobby tier-1 rules (project-law.md)
    # 4. If rules exist on disk, .agents/INDEX.md must not have zero rule rows
    tier1_stems = {p.stem for p in on_disk}
    projects_dir = _main_checkout() / "Projects"
    unrouted_project_rules = []
    dangling_project_rows = []
    forbidden_tier1_copies = []
    empty_project_indexes = []

    if projects_dir.is_dir():
        for p in sorted(projects_dir.iterdir()):
            if not p.is_dir() or p.name in ("Fresh_Workspace_BMAD", "sudo-command-center"):
                continue
            p_agents = p / ".agents"
            if not p_agents.is_dir():
                continue
            p_rules = p_agents / "rules"
            p_index = p_agents / "INDEX.md"
            if not p_rules.is_dir():
                continue
            p_loads = _project_index_loads(p_index)
            p_on_disk = sorted(f for f in p_rules.glob("*.md") if f.name != "INDEX.md")

            # Check for zero rows when rules exist
            if p_on_disk and not p_loads:
                empty_project_indexes.append(f"{p.name} ({len(p_on_disk)} rules on disk, 0 in INDEX.md)")

            # Check unrouted rules
            for f in p_on_disk:
                if f.stem not in p_loads:
                    unrouted_project_rules.append(f"{p.name}: {f.name}")

            # Check dangling rows
            for stem in p_loads:
                # template guidance row in skeleton is permitted if marked Create this first
                if stem == "constitution.project" and not (p_rules / f"{stem}.md").exists():
                    if p_index.exists() and "create this first" in p_index.read_text(encoding="utf-8").lower():
                        continue
                if not (p_rules / f"{stem}.md").exists():
                    dangling_project_rows.append(f"{p.name}: {stem}.md")

            # Check tier-1 forbidden copies
            for f in p_on_disk:
                if f.stem in tier1_stems:
                    forbidden_tier1_copies.append(f"{p.name}: {f.name}")

    c.check("every project rule on disk has a Load row in that project's .agents/INDEX.md",
            not unrouted_project_rules, str(unrouted_project_rules))
    c.check("every project .agents/INDEX.md row points at a rule that exists",
            not dangling_project_rows, str(dangling_project_rows))
    c.check("⛔ no project carries a copy of a tier-1 lobby rule (project-law.md)",
            not forbidden_tier1_copies, str(forbidden_tier1_copies))
    c.check("no project has zero rule rows in .agents/INDEX.md when rules exist on disk",
            not empty_project_indexes, str(empty_project_indexes))

    # ── Protocol size figure in AGENTS.md §3 ──
    agents_md = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    c.check("AGENTS.md §3 protocol-size figure is not stale (~44 KB was 2.1x understated)",
            "~44 KB" not in agents_md,
            "AGENTS.md still says '~44 KB' (measured ~96.6 KB)")

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
