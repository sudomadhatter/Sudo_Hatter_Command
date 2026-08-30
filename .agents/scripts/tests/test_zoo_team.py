"""The Wonderland team contract — the Zoo mode picker IS the operator's org chart (SCC-350).

Five seats override four of Zoo Code's built-in mode slugs plus one new one. The law this file
pins, each piece an operator ruling from the SCC-350 planning session:

  * THE SLUG SET IS CLOSED. Exactly {orchestrator, architect, code, debug, designer} — four
    built-ins (a same-slug custom mode replaces a built-in wholesale, verified against the
    Zoo v3.80.1 bundle) plus `designer`. The `ask` slug is DELIBERATELY unclaimed — stock Zoo
    Ask stays for plain Q&A (operator amendment 3) — while claiming `debug` suppresses the
    stock, law-free Debug mode. A missing slug resurrects a stock Zoo persona in the picker;
    an extra one is a seat nobody chartered.
  * THE NAME LAW. Emoji first, character name in regular case, then an em-dash and the ROLE in
    ALL CAPS: `🫖🐰 March Hare — TEAM LEAD`. The operator reads the role from the picker; a
    lowercase role or a bare name is a regression of his correction ("Use regular March Hare for
    the name then TEAM LEAD for the title in caps").
  * THE MERGED QUALITY SEAT. The operator's ruling (2026-08-29): "the tester and the QA need to
    really be one" and she is still the Queen of Hearts — one seat, `debug`, full pen, both the
    red phase and the review doors. Every seat is a working seat; a seat without `edit` is a
    regression to the retired scoped-pen design.
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

LAW_SLUGS = {"orchestrator", "architect", "code", "debug", "designer"}
BASE_GROUPS = {"read", "command"}          # every seat carries these

# name = emoji cluster · space · Regular-case character name · space-emdash-space · ALL-CAPS role
NAME_RE = re.compile(r"^(?P<emoji>\S+) (?P<name>[A-Z][A-Za-z]*(?: [A-Za-z]+)*) — (?P<role>[A-Z][A-Z &]*)$")


def parse_roomodes(text: str) -> list[dict]:
    """Parse the GENERATED .roomodes shape (never a general YAML parser — stdlib only)."""
    modes: list[dict] = []
    for chunk in re.split(r"(?m)^  - slug: ", text)[1:]:
        slug = chunk.split("\n", 1)[0].strip()
        name_m = re.search(r'(?m)^    name: "(.*)"$', chunk) or re.search(r"(?m)^    name: (.+)$", chunk)
        groups = set(re.findall(r"(?m)^      - ([a-z]+)$", chunk))
        role_m = re.search(r"(?ms)^    roleDefinition: >-\n(.*?)(?=^    \w|\Z)", chunk)
        modes.append({
            "slug": slug,
            "name": name_m.group(1).strip() if name_m else "",
            "groups": groups,
            "roledef": role_m.group(1) if role_m else chunk,
        })
    return modes


def mode_problems(text: str) -> list[str]:
    """Every way a .roomodes can break the team law, named so the failure reads itself."""
    problems: list[str] = []
    modes = parse_roomodes(text)
    slug_list = [m["slug"] for m in modes]
    dups = sorted({s for s in slug_list if slug_list.count(s) > 1})
    if dups:
        # A set-compare alone cannot see this (review finding: a duplicated slug collapsed
        # silently); Zoo resolves one of the two at random and the picker lies.
        problems.append(f"duplicate slug(s): {dups}")
    slugs = set(slug_list)
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
        if '"' in m["name"] or "\\" in m["name"]:
            # stdlib bars a real YAML parse; these are the two characters that break the
            # generated double-quoted scalar for the consumer while regex parsing stays green.
            problems.append(f"{m['slug']}: name carries a YAML-breaking character")
        missing = BASE_GROUPS - m["groups"]
        if missing:
            problems.append(f"{m['slug']}: groups missing {sorted(missing)}")
        if "edit" not in m["groups"]:
            # Every seat is a working seat since the quality merge (amendment 3) — a stripped
            # pen is a regression to the retired edit-strip/scoped-pen design.
            problems.append(f"{m['slug']}: working seat has no `edit` group")
    return problems


def fixture(names_groups) -> str:
    """Accepts a dict OR a list of (slug, name, groups) tuples — the list form is what lets a
    fixture carry a DUPLICATE slug, which a dict cannot represent."""
    entries = (names_groups.items() if isinstance(names_groups, dict)
               else [(s, (n, g)) for s, n, g in names_groups])
    lines = ["# GENERATED fixture", "customModes:"]
    for slug, (name, groups) in entries:
        lines += [f"  - slug: {slug}", f'    name: "{name}"',
                  "    roleDefinition: >-", f"      Read .agents/commands/smh-team-x.md ({slug}).",
                  "    groups:"]
        for g in groups:
            lines.append(f"      - {g}")
    return "\n".join(lines) + "\n"


GOOD = {
    "orchestrator": ("🫖🐰 March Hare — TEAM LEAD", ["read", "edit", "command", "mcp"]),
    "architect":    ("⏰🐇 White Rabbit — PM", ["read", "edit", "command"]),
    "code":         ("🔨🪚 Carpenter — ENGINEER", ["read", "edit", "command"]),
    "debug":        ("♥️👑 Queen of Hearts — TESTER & QA", ["read", "edit", "command"]),
    "designer":     ("🦋 Caterpillar — DESIGNER", ["read", "edit", "command"]),
}


def frontmatter(path: Path) -> dict[str, str]:
    # utf-8-sig, deliberately: a PS 5.1 `>` redirect writes a BOM, and a BOM under plain utf-8
    # makes `^---` unmatchable — frontmatter "vanishes" and every downstream message points at
    # the generator instead of the byte (wf_common.py documents the same trap).
    raw = path.read_text(encoding="utf-8-sig")
    m = re.match(r"(?s)^---\r?\n(.*?)\r?\n---", raw)
    out: dict[str, str] = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith((" ", "\t")):
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip()
    return out


def main() -> int:
    c = Cases("the Wonderland team — five seats over Zoo's slugs (SCC-350)")

    if c.block("A · the validator fires on every shape the law forbids"):
        c.check("the five-seat fixture is clean", mode_problems(fixture(GOOD)) == [],
                " | ".join(mode_problems(fixture(GOOD))))
        bad = dict(GOOD); bad["debug"] = ('♥️👑 Queen "of" Hearts — TESTER & QA', ["read", "edit", "command"])
        c.check("a YAML-breaking character in a name is caught (stdlib bars a real YAML parse)",
                any("YAML-breaking" in p for p in mode_problems(fixture(bad))))
        bad = dict(GOOD); bad["orchestrator"] = ("🫖🐰 March Hare — team lead", ["read", "edit", "command"])
        c.check("a lowercase role is caught",
                any("name law" in p or "not regular case" in p for p in mode_problems(fixture(bad))))
        bad = dict(GOOD); bad["code"] = ("Carpenter — ENGINEER", ["read", "edit", "command"])
        c.check("a bare name with no leading token is caught",
                any("name law" in p for p in mode_problems(fixture(bad))))
        # The emoji BRANCH needs a name that survives NAME_RE — a word-shaped ASCII prefix.
        # (Review finding: the fixture above dies at the regex, so the ord()>0x2000 branch was
        # deletable with the file staying green.)
        bad = dict(GOOD); bad["code"] = ("Mr Carpenter — ENGINEER", ["read", "edit", "command"])
        c.check("an ASCII word prefix (no emoji) is caught by the emoji branch itself",
                any("no emoji prefix" in p for p in mode_problems(fixture(bad))))
        bad = dict(GOOD); bad["architect"] = ("⏰🐇 White Rabbit — PM", ["read", "command"])
        c.check("a seat silently stripped of `edit` is caught (regression to the retired edit-strip)",
                any("working seat has no" in p for p in mode_problems(fixture(bad))))
        dup = [(s, n, g) for s, (n, g) in GOOD.items()] + [("code", "🔨 Ship Wright — ENGINEER", ["read", "edit", "command"])]
        c.check("a DUPLICATE slug is caught (a set-compare alone cannot see it)",
                any("duplicate slug" in p for p in mode_problems(fixture(dup))))
        bad = dict(GOOD); bad["debug"] = ("♥️👑 QUEEN OF HEARTS — TESTER & QA", ["read", "edit", "command"])
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
        text = roomodes.read_text(encoding="utf-8-sig") if roomodes.is_file() else ""
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
            plats = [x.strip() for x in fm.get("platforms", "").strip("[]").split(",") if x.strip()]
            if plats != ["zoo"]:
                bad_master.append(f"{slug}: master platforms {plats!r} != ['zoo']")
            # whenToUse ships the FULL description - the 135-char Antigravity cut amputated the
            # delegation signal (review finding); this row is what keeps it amputation-free.
            wtu_m = re.search(r"(?ms)^    whenToUse: >-\n(.*?)(?=^    \S|\Z)",
                              text.split(f"- slug: {slug}\n", 1)[1].split("\n  - slug: ")[0]
                              if f"- slug: {slug}\n" in text else "")
            wtu_text = " ".join(l.strip() for l in wtu_m.group(1).splitlines()).strip() if wtu_m else ""
            desc = fm.get("description", "").strip().strip('"').strip("'")
            if desc and wtu_text != desc:
                bad_master.append(f"{slug}: whenToUse != master description "
                                  f"(truncated or stale: {wtu_text[-30:]!r})")
        c.check("B3 every mode is generated FROM its master frontmatter (one source, current)",
                not bad_master, " | ".join(bad_master))

        # The merged quality seat (amendment 3): one master carries BOTH ends — the red phase
        # and the review doors — plus the refusal that makes owning both safe (never weaken an
        # assertion to reach green). Losing any half un-merges the seat silently.
        qa = ROOT / ".agents" / "commands" / "smh-team-queen-of-hearts.md"
        qa_text = qa.read_text(encoding="utf-8") if qa.is_file() else ""
        qa_missing = [w for w in ("cicd-write-story-tests", "smh-code-review", "smh-self-audit",
                                  "weakening the assertion")
                      if w not in qa_text]
        c.check("B4 the TESTER & QA master carries both halves (red-phase + review doors + the "
                "never-weaken refusal)", not qa_missing,
                f"missing from smh-team-queen-of-hearts.md: {qa_missing}")

        retired = [d for d in ("analyst", "dev", "pm", "tech-writer", "ux-designer", "ask")
                   if (ROOT / ".roo" / f"rules-{d}").is_dir()]
        # Currency, not existence (review finding: a stale rules-architect naming the RETIRED
        # BMAD master passed when this row read only is_file()). Each seat rule must be
        # GENERATED-marked and name the same master and mode-name its .roomodes entry does.
        bad_rule: list[str] = []
        for s in sorted(LAW_SLUGS):
            pf = ROOT / ".roo" / f"rules-{s}" / "01-persona.md"
            if not pf.is_file():
                bad_rule.append(f"{s}: 01-persona.md missing")
                continue
            body = pf.read_text(encoding="utf-8-sig")
            m = modes.get(s, {})
            tgt = re.search(r"\.agents/commands/(smh-team-[a-z-]+\.md)", m.get("roledef", ""))
            if "GENERATED by sync-agents" not in body:
                bad_rule.append(f"{s}: no GENERATED marker (hand-authored shadow?)")
            elif tgt and tgt.group(1) not in body:
                bad_rule.append(f"{s}: names a different master than .roomodes ({tgt.group(1)} absent)")
            elif m.get("name") and m["name"] not in body:
                bad_rule.append(f"{s}: seat rule does not carry the mode name {m['name']!r}")
        c.check("B5 seat rules are GENERATED, CURRENT, and retired persona dirs are pruned",
                not retired and not bad_rule,
                f"retired-still-present={retired} bad={bad_rule}")

        team_rule = ROOT / ".roo" / "rules" / "zoo-team.md"
        master_rule = ROOT / ".agents" / "rules" / "zoo-team.md"
        ok_cur = False
        detail = "copy or master absent"
        if team_rule.is_file() and master_rule.is_file():
            raw = master_rule.read_text(encoding="utf-8-sig")
            m2 = re.match(r"(?s)^---.*?\r?\n---\r?\n", raw)
            body = raw[m2.end():].lstrip("\r\n") if m2 else raw
            copy = team_rule.read_text(encoding="utf-8-sig").split("\n", 1)
            ok_cur = len(copy) == 2 and copy[1] == body
            detail = "copy differs from master — run /smh-sync-agents" if not ok_cur else ""
        c.check("B6 the team rule reaches every Zoo seat, CURRENT with its master", ok_cur, detail)

        vs = ROOT / ".vscode" / "settings.json"
        vs_text = vs.read_text(encoding="utf-8-sig") if vs.is_file() else ""
        stripped = re.sub(r"(?m)^\s*//.*$", "", vs_text)
        parse_err = ""
        try:
            vs_json = json.loads(stripped)
        except ValueError as e:
            vs_json = {}
            parse_err = f" (settings.json did not parse after comment-strip: {e})"
        c.check("B7 tracked .vscode/settings.json ships git.detectWorktrees=true (PC parity)",
                vs_json.get("git.detectWorktrees") is True,
                "" if vs_json.get("git.detectWorktrees") is True
                else f"value={vs_json.get('git.detectWorktrees')!r}{parse_err}")

    if c.block("C · the GENERATOR source agrees with what it generated (currency, not faith)"):
        # Recomputed here, never borrowed from block B: a `--case "C ·"` filtered run must not
        # NameError on block-B locals (the harness filter runs blocks independently).
        roomodes = ROOT / ".roomodes"
        text = roomodes.read_text(encoding="utf-8-sig") if roomodes.is_file() else ""
        modes = {m["slug"]: m for m in parse_roomodes(text)}
        # These two regexes MIRROR sync-agents.ps1's seat-frontmatter readers ON PURPOSE - the
        # ps1 demands the quotes and the brackets, while frontmatter() above forgives their
        # absence. A master authored unquoted keeps every B check green while the NEXT sync
        # silently skips the seat and a stock Zoo mode returns to the picker (review finding).
        ps1_name_re = re.compile(r'^mode-name:\s*"(.+)"\s*$')
        ps1_groups_re = re.compile(r"^mode-groups:\s*\[(.+)\]\s*$")
        c.check("C0 the mirrored regexes can actually REJECT (unquoted / unbracketed mutants)",
                not ps1_name_re.match("mode-name: Bare March Hare — TEAM LEAD")
                and not ps1_groups_re.match("mode-groups: read, command")
                and bool(ps1_name_re.match('mode-name: "🫖🐰 March Hare — TEAM LEAD"')))
        ps1 = (ROOT / ".agents" / "scripts" / "sync-agents.ps1").read_text(encoding="utf-8-sig")
        code = "\n".join(l for l in ps1.splitlines() if not l.lstrip().startswith("#"))
        table = re.findall(r"@\{\s*Slug\s*=\s*'([a-z-]+)';\s*Master\s*=\s*'(smh-team-[a-z-]+\.md)'",
                           code)
        c.check("C1 the ps1 $seats table carries exactly the law's five slugs",
                {s for s, _ in table} == LAW_SLUGS and len(table) == 5,
                f"table={table}")
        bad_fm: list[str] = []
        for s, master_name in sorted(table):
            mp = ROOT / ".agents" / "commands" / master_name
            if not mp.is_file():
                bad_fm.append(f"{s}: {master_name} missing")
                continue
            head = mp.read_text(encoding="utf-8-sig").splitlines()[:12]
            if not any(ps1_name_re.match(l) for l in head):
                bad_fm.append(f"{s}: no ps1-parseable mode-name in the first 12 lines")
            if not any(ps1_groups_re.match(l) for l in head):
                bad_fm.append(f"{s}: no ps1-parseable mode-groups in the first 12 lines")
        c.check("C2 every seat master parses under the ps1's OWN stricter regexes, within its "
                "12-line read window", not bad_fm, " | ".join(bad_fm))
        c.check("C3 .roomodes carries one mode per table row (a skipped seat resurrects a stock "
                "Zoo mode)", len(parse_roomodes(text)) == len(table),
                f"modes={len(parse_roomodes(text))} table={len(table)}")
        pair_bad = [f"{s}: table says {mn}, .roomodes says otherwise" for s, mn in table
                    if s in modes and mn not in modes[s].get("roledef", "")]
        c.check("C4 each mode's roleDefinition names the SAME master as the ps1 table row",
                not pair_bad, " | ".join(pair_bad))
        floor_m = re.search(r"\$floor\s*=\s*@\(([^)]*)\)", code)
        c.check("C5 the ps1 zoo floor-copy list carries zoo-team.md (its ONLY publisher — the "
                "tracked copy stays byte-equal for a while after a silent drop)",
                bool(floor_m) and "zoo-team.md" in floor_m.group(1),
                floor_m.group(1) if floor_m else "no $floor assignment found")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
