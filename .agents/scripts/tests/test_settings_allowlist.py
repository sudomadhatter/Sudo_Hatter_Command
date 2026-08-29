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
      surfaces exist in the tree (`.roo/commands/` launchers, `.roomodes` with the six BMAD
      personas, per-persona `.roo/rules-<slug>/`, floor-rule copies in `.roo/rules/`); the six
      persona masters declare `zoo` and the opencode-runtime autopilot does NOT.
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
    c.check("A2 floor count >= 60 (the stable set, not a token few)", len(allow) >= 60,
            f"count={len(allow)}")
    py3 = {r for r in allow if r.startswith("Bash(python3 ")}
    py_twin = {r.replace("Bash(python3 ", "Bash(python ", 1) for r in py3}
    missing = sorted(py_twin - set(allow))
    c.check("A3 every python3 rule has its `python` twin (PC spelling)",
            bool(py3) and not missing, f"python3_rules={len(py3)} missing_twins={missing}")
    bad = [r for r in allow if "/Users/" in r or re.search(r"[A-Za-z]:\\", r)]
    c.check("A4 no machine-absolute path in any tracked rule", not bad, f"bad={bad}")

if c.block("B · Zoo Code allowlist + extension recommendations travel"):
    vs = _jsonc(ROOT / ".vscode" / "settings.json")
    allowed = vs.get("zoo-code.allowedCommands")
    denied = vs.get("zoo-code.deniedCommands")
    c.check("B1 zoo-code.allowedCommands is a non-empty list",
            isinstance(allowed, list) and len(allowed) > 0)
    c.check("B2 zoo-code.deniedCommands is a list (destructive set)",
            isinstance(denied, list) and len(denied) > 0)
    ext = _jsonc(ROOT / ".vscode" / "extensions.json")
    recs = ext.get("recommendations", [])
    c.check("B3 Zoo Code is a workspace recommendation",
            "ZooCodeOrganization.zoo-code" in recs)
    c.check("B4 the Gemini agent surface is a workspace recommendation",
            "google.google-antigravity" in recs)

PERSONAS = ("analyst", "architect", "dev", "pm", "tech-writer", "ux-designer")
FLOOR = ("operator-profile.md", "constitution.md", "karpathy-guidelines.md")

if c.block("E · zoo is sync-agents platform 5 (SCC-349)"):
    ps1 = (ROOT / ".agents" / "scripts" / "sync-agents.ps1").read_text(encoding="utf-8")
    m = re.search(r"^\$AllPlatforms\s*=\s*@\((.*?)\)", ps1, re.M)
    c.check("E1 $AllPlatforms names 'zoo'", bool(m) and "'zoo'" in m.group(1),
            m.group(1) if m else "assignment line not found")
    roomodes = ROOT / ".roomodes"
    slugs = (re.findall(r"^\s*-\s*slug:\s*(\S+)", roomodes.read_text(encoding="utf-8"), re.M)
             if roomodes.exists() else [])
    c.check("E2 .roomodes carries exactly the six BMAD personas",
            sorted(slugs) == sorted(PERSONAS), f"slugs={slugs}")
    cmds = list((ROOT / ".roo" / "commands").glob("*.md")) if (ROOT / ".roo" / "commands").is_dir() else []
    marked = [f for f in cmds if "GENERATED by sync-agents" in f.read_text(encoding="utf-8")]
    c.check("E3 .roo/commands/ holds generated launchers (>= 10, all marked)",
            len(cmds) >= 10 and len(marked) == len(cmds),
            f"launchers={len(cmds)} marked={len(marked)}")
    missing_rule_dirs = [p for p in PERSONAS if not (ROOT / ".roo" / f"rules-{p}").is_dir()]
    c.check("E4 per-persona .roo/rules-<slug>/ dirs exist", not missing_rule_dirs,
            f"missing={missing_rule_dirs}")
    floor_copies = [f for f in FLOOR if (ROOT / ".roo" / "rules" / f).is_file()]
    c.check("E5 floor-rule copies land in .roo/rules/ (Zoo injects them every prompt)",
            sorted(floor_copies) == sorted(FLOOR), f"present={floor_copies}")
    def _declares_zoo(name: str) -> bool:
        text = (ROOT / ".agents" / "commands" / name).read_text(encoding="utf-8")
        m2 = re.search(r"^platforms:\s*\[(.*?)\]", text, re.M)
        return bool(m2) and "zoo" in [x.strip() for x in m2.group(1).split(",")]
    not_zoo = [p for p in PERSONAS if not _declares_zoo(f"{p}.md")]
    c.check("E6 the six persona masters declare zoo", not not_zoo, f"missing={not_zoo}")
    c.check("E7 cicd-autopilot-opencode stays opencode-only (runtime-specific)",
            not _declares_zoo("cicd-autopilot-opencode.md"))

if c.block("F · floor rules always-on across the platforms"):
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
    ps1_f = (ROOT / ".agents" / "scripts" / "sync-agents.ps1").read_text(encoding="utf-8")
    c.check("F4 the sync engine writes the Codex machine cache (~/.codex/AGENTS.md)",
            ".codex\\AGENTS.md" in ps1_f and "GENERATED floor-rules" in ps1_f)

sys.exit(c.finish())
