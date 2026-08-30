"""The Wonderland team contract — the Zoo mode picker IS the operator's org chart (SCC-350).

Six seats override Zoo Code's five built-in mode slugs plus one new one. The law this file pins,
each piece an operator ruling from the SCC-350 planning session:

  * THE SLUG SET IS CLOSED. Exactly {orchestrator, architect, code, ask, debug, designer} — the
    five built-ins (a same-slug custom mode replaces a built-in wholesale, verified against the
    Zoo v3.80.1 bundle) plus `designer`. A missing slug resurrects a stock Zoo persona in the
    picker; an extra one is a seat nobody chartered.
  * THE NAME LAW. Emoji first, character name in regular case, then an em-dash and the ROLE in
    ALL CAPS: `🫖🐰 March Hare — TEAM LEAD`. The operator reads the role from the picker; a
    lowercase role or a bare name is a regression of his correction ("Use regular March Hare for
    the name then TEAM LEAD for the title in caps").
  * THE QA EDIT-STRIP. The `ask` seat (Queen of Hearts — QA) judges and never edits: its groups
    exclude `edit` MECHANICALLY. This is the one refusal enforced by the platform rather than by
    prose, so it is the one this file must prove can actually fail.
  * ONE SOURCE. Each mode's name/slug/groups live in its master's frontmatter
    (`.agents/commands/smh-team-*.md`); `sync-agents.ps1` reads them (the ps1 stays pure ASCII — no
    emoji survive Windows PowerShell 5.1's no-BOM codepage mangling); `.roomodes` is generated.
    So the currency check here compares GENERATED against MASTER, never against a second copy of
    the table typed into this file.

Fixtures fire both ways first — a validator that has never flagged a mutant proves nothing by
staying quiet on the live tree (`suite-red-file-may-have-run-nothing`, `stubbed-children` lessons).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases

ROOT = SCRIPTS.parents[1]

LAW_SLUGS = {"orchestrator", "architect", "code", "ask", "debug", "designer"}
NO_EDIT_SLUGS = {"ask"}                    # the QA seat judges; the platform strips its pen
BASE_GROUPS = {"read", "command"}          # every seat carries these

# name = emoji cluster · space · Regular-case character name · space-emdash-space · ALL-CAPS role
NAME_RE = re.compile(r"^(?P<emoji>\S+) (?P<name>[A-Z][A-Za-z]*(?: [A-Za-z]+)*) — (?P<role>[A-Z][A-Z &]*)$")


def parse_roomodes(text: str) -> list[dict]:
    """Parse the GENERATED .roomodes shape (never a general YAML parser — stdlib only)."""
    modes: list[dict] = []
    for chunk in re.split(r"(?m)^  - slug: ", text)[1:]:
        slug = chunk.split("\n", 1)[0].strip()
        name_m = re.search(r'(?m)^    name: "(.*)"$', chunk) or re.search(r"(?m)^    name: (.+)$", chunk)
        groups = re.findall(r"(?m)^      - (\S+)$", chunk)
        role_m = re.search(r"(?ms)^    roleDefinition: >-\n(.*?)(?=^    \w|\Z)", chunk)
        modes.append({
            "slug": slug,
            "name": name_m.group(1).strip() if name_m else "",
            "groups": set(groups),
            "roledef": role_m.group(1) if role_m else chunk,
        })
    return modes


def mode_problems(text: str) -> list[str]:
    """Every way a .roomodes can break the team law, named so the failure reads itself."""
    problems: list[str] = []
    modes = parse_roomodes(text)
    slugs = {m["slug"] for m in modes}
    if slugs != LAW_SLUGS:
        problems.append(f"slug set {sorted(slugs)} != law {sorted(LAW_SLUGS)}")
    for m in modes:
        nm = NAME_RE.match(m["name"])
        if not nm:
            problems.append(f"{m['slug']}: name {m['name']!r} breaks the name law")
        else:
            if not any(ord(ch) > 0x2000 for ch in nm.group("emoji")):
                problems.append(f"{m['slug']}: name has no emoji prefix")
            if not re.search(r"[a-z]", nm.group("name")):
                problems.append(f"{m['slug']}: character name {nm.group('name')!r} is not regular case")
        missing = BASE_GROUPS - m["groups"]
        if missing:
            problems.append(f"{m['slug']}: groups missing {sorted(missing)}")
        if m["slug"] in NO_EDIT_SLUGS and "edit" in m["groups"]:
            problems.append(f"{m['slug']}: QA seat carries `edit` — the strip is the refusal")
        if m["slug"] not in NO_EDIT_SLUGS and "edit" not in m["groups"]:
            problems.append(f"{m['slug']}: working seat has no `edit` group")
    return problems


def fixture(names_groups: dict[str, tuple[str, list[str]]]) -> str:
    lines = ["# GENERATED fixture", "customModes:"]
    for slug, (name, groups) in names_groups.items():
        lines += [f"  - slug: {slug}", f'    name: "{name}"',
                  "    roleDefinition: >-", f"      Read .agents/commands/smh-team-x.md ({slug}).",
                  "    groups:"] + [f"      - {g}" for g in groups]
    return "\n".join(lines) + "\n"


GOOD = {
    "orchestrator": ("🫖🐰 March Hare — TEAM LEAD", ["read", "edit", "command", "mcp"]),
    "architect":    ("⏰🐇 White Rabbit — PM", ["read", "edit", "command"]),
    "code":         ("🔨🪚 Carpenter — ENGINEER", ["read", "edit", "command"]),
    "ask":          ("♥️👑 Queen of Hearts — QA", ["read", "command"]),
    "debug":        ("😼 Cheshire Cat — TESTER", ["read", "edit", "command"]),
    "designer":     ("🦋 Caterpillar — DESIGNER", ["read", "edit", "command"]),
}


def frontmatter(path: Path) -> dict[str, str]:
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"(?s)^---\r?\n(.*?)\r?\n---", raw)
    out: dict[str, str] = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith((" ", "\t")):
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip()
    return out


def main() -> int:
    c = Cases("the Wonderland team — six seats over Zoo's slugs (SCC-350)")

    if c.block("A · the validator fires on every shape the law forbids"):
        c.check("the six-seat fixture is clean", mode_problems(fixture(GOOD)) == [],
                " | ".join(mode_problems(fixture(GOOD))))
        bad = dict(GOOD); bad["ask"] = ("♥️👑 Queen of Hearts — QA", ["read", "edit", "command"])
        c.check("QA seat carrying `edit` is caught (the strip can actually fail)",
                any("QA seat carries" in p for p in mode_problems(fixture(bad))))
        bad = dict(GOOD); bad["orchestrator"] = ("🫖🐰 March Hare — team lead", ["read", "edit", "command"])
        c.check("a lowercase role is caught", mode_problems(fixture(bad)) != [])
        bad = dict(GOOD); bad["code"] = ("Carpenter — ENGINEER", ["read", "edit", "command"])
        c.check("a missing emoji prefix is caught", mode_problems(fixture(bad)) != [])
        bad = dict(GOOD); bad["debug"] = ("😼 CHESHIRE CAT — TESTER", ["read", "edit", "command"])
        c.check("an ALL-CAPS character name (the pre-correction shape) is caught",
                any("regular case" in p or "name law" in p for p in mode_problems(fixture(bad))))
        bad = {k: v for k, v in GOOD.items() if k != "designer"}
        bad["analyst"] = ("🧠 Mary — ANALYST", ["read", "edit", "command"])
        c.check("a wrong slug set (a BMAD persona back in the picker) is caught",
                any("slug set" in p for p in mode_problems(fixture(bad))))
        bad = dict(GOOD); bad["architect"] = ("⏰🐇 White Rabbit — PM", ["edit"])
        c.check("a seat missing its base groups is caught",
                any("groups missing" in p for p in mode_problems(fixture(bad))))

    if c.block("B · the live tree"):
        roomodes = ROOT / ".roomodes"
        text = roomodes.read_text(encoding="utf-8") if roomodes.is_file() else ""
        c.check("B1 .roomodes exists", bool(text))
        probs = mode_problems(text)
        c.check("B2 the live .roomodes satisfies the whole team law (slugs · names · groups)",
                probs == [], " | ".join(probs))

        modes = {m["slug"]: m for m in parse_roomodes(text)}
        bad_master: list[str] = []
        for slug, m in sorted(modes.items()):
            tgt = re.search(r"\.agents/commands/(smh-team-[a-z-]+\.md)", m["roledef"])
            if not tgt:
                bad_master.append(f"{slug}: roleDefinition names no smh-team master")
                continue
            master = ROOT / ".agents" / "commands" / tgt.group(1)
            if not master.is_file():
                bad_master.append(f"{slug}: {tgt.group(1)} does not exist")
                continue
            fm = frontmatter(master)
            if fm.get("mode-slug") != slug:
                bad_master.append(f"{slug}: master mode-slug={fm.get('mode-slug')!r}")
            if fm.get("mode-name", "").strip('"') != m["name"]:
                bad_master.append(f"{slug}: generated name {m['name']!r} != master mode-name")
            declared = {g.strip() for g in fm.get("mode-groups", "").strip("[]").split(",") if g.strip()}
            if declared != m["groups"]:
                bad_master.append(f"{slug}: generated groups {sorted(m['groups'])} != master {sorted(declared)}")
            plats = fm.get("platforms", "")
            if "zoo" not in plats:
                bad_master.append(f"{slug}: master platforms {plats!r} lacks zoo")
        c.check("B3 every mode is generated FROM its master frontmatter (one source, current)",
                not bad_master, " | ".join(bad_master))

        qa = ROOT / ".agents" / "commands" / "smh-team-queen-of-hearts.md"
        qa_text = qa.read_text(encoding="utf-8") if qa.is_file() else ""
        c.check("B4 the QA master states the no-edit refusal in prose too",
                bool(re.search(r"(?i)never (edits?|writes?|touch)", qa_text)),
                "team-queen-of-hearts.md missing the refusal (or the file)")

        retired = [d for d in ("analyst", "dev", "pm", "tech-writer", "ux-designer")
                   if (ROOT / ".roo" / f"rules-{d}").is_dir()]
        no_dir = [s for s in sorted(LAW_SLUGS)
                  if not (ROOT / ".roo" / f"rules-{s}" / "01-persona.md").is_file()]
        c.check("B5 seat rule dirs exist; retired persona dirs are pruned",
                not retired and not no_dir, f"retired-still-present={retired} missing={no_dir}")

        team_rule = ROOT / ".roo" / "rules" / "zoo-team.md"
        master_rule = ROOT / ".agents" / "rules" / "zoo-team.md"
        ok_cur = False
        detail = "copy or master absent"
        if team_rule.is_file() and master_rule.is_file():
            raw = master_rule.read_text(encoding="utf-8")
            m2 = re.match(r"(?s)^---.*?\r?\n---\r?\n", raw)
            body = raw[m2.end():].lstrip("\r\n") if m2 else raw
            copy = team_rule.read_text(encoding="utf-8").split("\n", 1)
            ok_cur = len(copy) == 2 and copy[1] == body
            detail = "copy differs from master — run /smh-sync-agents" if not ok_cur else ""
        c.check("B6 the team rule reaches every Zoo seat, CURRENT with its master", ok_cur, detail)

        vs = ROOT / ".vscode" / "settings.json"
        vs_text = vs.read_text(encoding="utf-8") if vs.is_file() else ""
        stripped = re.sub(r"(?m)^\s*//.*$", "", vs_text)
        try:
            vs_json = json.loads(stripped)
        except ValueError:
            vs_json = {}
        c.check("B7 tracked .vscode/settings.json ships git.detectWorktrees=true (PC parity)",
                vs_json.get("git.detectWorktrees") is True,
                f"value={vs_json.get('git.detectWorktrees')!r}")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
