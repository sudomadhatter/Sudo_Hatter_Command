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

sys.exit(c.finish())
