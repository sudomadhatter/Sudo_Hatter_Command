"""test_settings_allowlist.py — the promoted allowlists actually travel via git (SCC-346).

Until SCC-346, the 77 Claude Code allow rules lived only in gitignored
`.claude/settings.local.json` — tracked `.claude/settings.json` carried ZERO — so every approval
learned on one machine died at the machine/worktree boundary, and Zoo Code had no tracked
allowlist at all. These cases pin the tracked files, which are the only copies a fresh clone or
the other machine ever sees:

  A · `.claude/settings.json` `permissions.allow`: parses, floor count, BOTH interpreter
      spellings (`python3` Mac / `python` PC — `two-machines`), and no machine-absolute path
      (`/Users/…`, `C:\\…`) in any tracked rule.
  B · `.vscode/settings.json` (JSONC): `zoo-code.allowedCommands` non-empty +
      `zoo-code.deniedCommands` present; `.vscode/extensions.json` recommends Zoo Code and the
      Gemini agent surface.
  E · Zoo is sync-agents platform 5 (SCC-349): `$AllPlatforms` names `zoo`; the generated
      surfaces exist in the tree (`.roo/commands/` launchers, `.roomodes` with the six team
      seats since SCC-350, per-seat `.roo/rules-<slug>/`, floor-rule copies in `.roo/rules/`);
      the six BMAD persona masters still declare `zoo` (they keep their launchers) and the
      opencode-runtime autopilot does NOT.
  F · the three FLOOR rules are delivered MECHANICALLY on every platform (SCC-346 Part F):
      CLAUDE.md and GEMINI.md carry `@` imports (resolved at session start by Claude Code and
      Gemini respectively), opencode.json `instructions` names all three, and the sync engine
      writes the `~/.codex/AGENTS.md` machine cache for Codex's global merge. Zoo's half is E5.

Stdlib only, no pytest — same constraint as everything else in this suite.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from _harness import Cases

ROOT = Path(__file__).resolve().parents[3]


def _jsonc(path: Path) -> object:
    """Parse VS Code-flavoured JSON: whole-line // comments stripped, nothing else.

    Deliberately conservative — a `//` inside a string value (a URL) is untouched because only
    lines whose first non-blank characters are `//` are dropped.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    return json.loads("\n".join(l for l in lines if not l.lstrip().startswith("//")))


c = Cases("settings_allowlist")

if c.block("A · tracked Claude allowlist travels"):
    tracked = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    allow = tracked.get("permissions", {}).get("allow", [])
    c.check("A1 tracked permissions.allow exists and is a list", isinstance(allow, list))
    # Identity, not only cardinality (the CS-01 lesson): a wrong-but-numerous list must not pass.
    sentinels = {"Bash(git status:*)", "Bash(python3 .agents/scripts/:*)", "Bash(git add:*)"}
    c.check("A2 floor count >= 60 AND the sentinel identities are present",
            len(allow) >= 60 and sentinels <= set(allow),
            f"count={len(allow)} missing_sentinels={sorted(sentinels - set(allow))}")
    py3 = {r for r in allow if r.startswith("Bash(python3 ")}
    py = {r for r in allow if r.startswith("Bash(python ")}
    missing = sorted({r.replace("Bash(python3 ", "Bash(python ", 1) for r in py3} - set(allow)) \
        + sorted({r.replace("Bash(python ", "Bash(python3 ", 1) for r in py} - set(allow))
    c.check("A3 interpreter twins hold in BOTH directions (python3 Mac / python PC)",
            bool(py3) and bool(py) and not missing,
            f"python3={len(py3)} python={len(py)} missing_twins={missing}")
    bad = [r for r in allow if "/Users/" in r or re.search(r"[A-Za-z]:\\", r)]
    c.check("A4 no machine-absolute path in any tracked rule", not bad, f"bad={bad}")
    # The plan promised a syntax pin: every rule is Tool(specifier) — a bare string or a typo'd
    # paren never silently matches nothing.
    bad_syntax = [r for r in allow if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*\(.+\)", r)]
    c.check("A5 every rule parses as Tool(specifier)", not bad_syntax, f"bad={bad_syntax}")

if c.block("B · Zoo Code allowlist + extension recommendations travel"):
    vs = _jsonc(ROOT / ".vscode" / "settings.json")
    allowed = vs.get("zoo-code.allowedCommands")
    denied = vs.get("zoo-code.deniedCommands")
    c.check("B1 zoo-code.allowedCommands is non-empty and carries the read-only sentinels",
            isinstance(allowed, list) and {"git status", "ls"} <= set(allowed or []))
    c.check("B2 the deny list pins the destructive sentinels (identity, not count)",
            isinstance(denied, list)
            and {"git push origin main", "rm -rf", "git reset --hard"} <= set(denied or []))
    # Both zoo lists are prefix matchers and deny wins only when its prefix MATCHES — so a broad
    # allow prefix that fronts a denied family is a bypass, not a convenience. `git -C . push
    # --force` starts with "git -C" and with no deny entry; that one allow row defeated the whole
    # destructive set (found at review, SCC-346).
    c.check("B2b no bare `git -C` allow prefix (it would bypass every git deny)",
            "git -C" not in (allowed or []))
    ext = _jsonc(ROOT / ".vscode" / "extensions.json")
    recs = ext.get("recommendations", [])
    c.check("B3 Zoo Code is a workspace recommendation",
            "ZooCodeOrganization.zoo-code" in recs)
    c.check("B4 the Gemini agent surface is a workspace recommendation",
            "google.google-antigravity" in recs)

PERSONAS = ("analyst", "architect", "dev", "pm", "tech-writer", "ux-designer")
# The mode picker belongs to the Wonderland TEAM since SCC-350 (the BMAD personas keep their
# .roo/commands/ launchers — E6/E8/E9 still hold them to that — but the modes are the seats).
# Deep seat law (names, groups, master currency) lives in test_zoo_team.py; here only the
# lineup and the mode→master join are pinned.
SEATS = ("orchestrator", "architect", "code", "debug", "designer")
FLOOR = ("operator-profile.md", "constitution.md", "karpathy-guidelines.md")

if c.block("E · zoo is sync-agents platform 5 (SCC-349)"):
    ps1 = (ROOT / ".agents" / "scripts" / "sync-agents.ps1").read_text(encoding="utf-8")
    m = re.search(r"^\$AllPlatforms\s*=\s*@\((.*?)\)", ps1, re.M)
    c.check("E1 $AllPlatforms names 'zoo'", bool(m) and "'zoo'" in m.group(1),
            m.group(1) if m else "assignment line not found")
    roomodes = ROOT / ".roomodes"
    slugs = (re.findall(r"^\s*-\s*slug:\s*(\S+)", roomodes.read_text(encoding="utf-8"), re.M)
             if roomodes.exists() else [])
    c.check("E2 .roomodes carries exactly the five team seats (SCC-350; ask is deliberately "
            "left to stock Zoo Ask)",
            sorted(slugs) == sorted(SEATS), f"slugs={slugs}")
    cmds = list((ROOT / ".roo" / "commands").glob("*.md")) if (ROOT / ".roo" / "commands").is_dir() else []
    marked = [f for f in cmds if "GENERATED by sync-agents" in f.read_text(encoding="utf-8")]
    # >= on the marked set, never equality over every file: the generator's own contract preserves
    # hand-authored (unmarked) files, so demanding all-marked would go red on the first legitimate
    # hand door (the smh-adviser-board precedent on the Antigravity surface).
    c.check("E3 .roo/commands/ holds >= 10 GENERATED launchers", len(marked) >= 10,
            f"launchers={len(cmds)} marked={len(marked)}")
    missing_rule_dirs = [s for s in SEATS if not (ROOT / ".roo" / f"rules-{s}").is_dir()]
    c.check("E4 per-seat .roo/rules-<slug>/ dirs exist", not missing_rule_dirs,
            f"missing={missing_rule_dirs}")
    # Currency, not existence: the copies are tracked, so a master edited without a re-sync would
    # ship stale law into every Zoo prompt with a green suite (the SCC-77 stale-door shape).
    def _master_body(name: str) -> str:
        raw = (ROOT / ".agents" / "rules" / name).read_text(encoding="utf-8")
        m2 = re.match(r"(?s)^---.*?\r?\n---\r?\n", raw)
        return raw[m2.end():].lstrip("\r\n") if m2 else raw
    stale = []
    for f in FLOOR:
        copy = ROOT / ".roo" / "rules" / f
        if not copy.is_file():
            stale.append(f"{f} (absent)")
            continue
        body = copy.read_text(encoding="utf-8").split("\n", 1)
        if len(body) < 2 or body[1] != _master_body(f):
            stale.append(f"{f} (differs from master — run /smh-sync-agents)")
    c.check("E5 floor copies in .roo/rules/ are CURRENT with their masters", not stale,
            f"stale={stale}")
    def _declared(name: str):
        text = (ROOT / ".agents" / "commands" / name).read_text(encoding="utf-8")
        m2 = re.search(r"^platforms:\s*\[(.*?)\]", text, re.M)
        return None if not m2 else [x.strip() for x in m2.group(1).split(",") if x.strip()]
    def _declares_zoo(name: str) -> bool:
        d = _declared(name)
        return bool(d) and "zoo" in d
    not_zoo = [p for p in PERSONAS if not _declares_zoo(f"{p}.md")]
    c.check("E6 the six persona masters declare zoo", not not_zoo, f"missing={not_zoo}")
    # An EXPLICIT non-zoo list, not merely "does not say zoo": if the frontmatter line were
    # deleted, the absent-key=universal rule would grow this door a zoo launcher while a
    # does-not-declare check stayed green.
    ap_platforms = _declared("cicd-autopilot-opencode.md")
    c.check("E7 cicd-autopilot-opencode explicitly declares a zoo-free platform list",
            ap_platforms is not None and "zoo" not in ap_platforms and "opencode" in ap_platforms,
            f"declared={ap_platforms}")
    # Door parity, both directions (the CS-02 contract applied to the zoo surface): every
    # zoo-eligible master has its launcher, and every GENERATED launcher points at a live master.
    masters_dir = ROOT / ".agents" / "commands"
    eligible = []
    for mf in sorted(masters_dir.glob("*.md")):
        if mf.name == "INDEX.md" or mf.name.endswith("-AP.md"):
            continue
        d = _declared(mf.name)
        if d is None or "zoo" in d:            # absent = universal = zoo-eligible
            eligible.append(mf.name)
    no_door = [n for n in eligible if not (ROOT / ".roo" / "commands" / n).is_file()]
    c.check("E8 every zoo-eligible master has its .roo/commands/ door", not no_door,
            f"eligible={len(eligible)} missing={no_door}")
    bad_launchers = []
    for lf in marked:
        body = lf.read_text(encoding="utf-8")
        if f".agents/commands/{lf.name}" not in body:
            bad_launchers.append(f"{lf.name} (does not point at its own brain)")
        elif not (masters_dir / lf.name).is_file():
            bad_launchers.append(f"{lf.name} (brain gone — stale, prune owed)")
        elif lf.name not in eligible:
            bad_launchers.append(f"{lf.name} (brain no longer zoo-eligible — prune owed)")
    c.check("E9 every GENERATED launcher points at a live, zoo-eligible brain", not bad_launchers,
            f"bad={bad_launchers}")
    # .roomodes content tier: each mode must target a LIVE team master, and the character name
    # must agree with that brain's description (the James/Amelia contradiction shipped exactly
    # here). The full name/groups/frontmatter currency contract lives in test_zoo_team.py.
    roomodes_text = roomodes.read_text(encoding="utf-8") if roomodes.exists() else ""
    mode_bad = []
    for s in SEATS:
        m3 = re.search(rf"(?s)- slug: {re.escape(s)}\n(.*?)(?=\n  - slug: |\Z)", roomodes_text)
        entry = m3.group(1) if m3 else ""
        tgt = re.search(r"\.agents/commands/(smh-team-[a-z-]+\.md)", entry)
        if not tgt or not (masters_dir / tgt.group(1)).is_file():
            mode_bad.append(f"{s} (roleDefinition does not name a live team master)")
            continue
        n = re.search(r'name: "(.+)"', entry)
        char = (n.group(1).split("—")[0].split(" ", 1)[1].strip()
                if n and "—" in n.group(1) and " " in n.group(1).split("—")[0] else None)
        desc = re.search(r"^description:\s*(.+)$",
                         (masters_dir / tgt.group(1)).read_text(encoding="utf-8"), re.M)
        if not char or not desc or char not in desc.group(1):
            mode_bad.append(f"{s} (display name {char!r} not in master description)")
    c.check("E10 every .roomodes entry targets a live team master and names the seat's character",
            not mode_bad, f"bad={mode_bad}")

if c.block("F · floor rules always-on across the platforms"):
    # The whole delivery chain rests on the three masters existing — a renamed master would make
    # every import resolve to nothing while the line-greps below stayed green.
    gone = [f for f in FLOOR if not (ROOT / ".agents" / "rules" / f).is_file()]
    c.check("F0 the three floor-rule masters exist", not gone, f"missing={gone}")
    imports = tuple(f"@.agents/rules/{f}" for f in FLOOR)
    claude_md = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    missing_cl = [i for i in imports if i not in claude_md.splitlines()]
    c.check("F1 CLAUDE.md imports the three floor rules via @path", not missing_cl,
            f"missing={missing_cl}")
    gemini_md = (ROOT / "GEMINI.md").read_text(encoding="utf-8")
    missing_ge = [i for i in imports if i not in gemini_md.splitlines()]
    c.check("F2 GEMINI.md imports the three floor rules via @path", not missing_ge,
            f"missing={missing_ge}")
    oc = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    instr = oc.get("instructions", [])
    missing_oc = [f for f in FLOOR if f".agents/rules/{f}" not in instr]
    c.check("F3 opencode.json instructions carries all three floor rules", not missing_oc,
            f"missing={missing_oc}")
    # Comment-stripped source, never the raw file: a commented-out stage keeps its string
    # literals, so a raw grep passes over dead code (`comment-literals-invert-source-grep-tests`).
    ps1_raw = (ROOT / ".agents" / "scripts" / "sync-agents.ps1").read_text(encoding="utf-8")
    ps1_code = "\n".join(l for l in ps1_raw.splitlines() if not l.lstrip().startswith("#"))
    c.check("F4 the LIVE code writes the Codex floor cache (~/.codex/AGENTS.md)",
            ".codex\\AGENTS.md" in ps1_code and "GENERATED floor-rules" in ps1_code)
    c.check("F5 Sync-ZooSurfaces is CALLED, not merely defined (dead pipeline = green artifacts)",
            re.search(r"^\s*\$\w+\s*=\s*Sync-ZooSurfaces\s+\$Master", ps1_code, re.M) is not None)

sys.exit(c.finish())
