#!/usr/bin/env python3
"""Apply the sandbox half of /smh-llm-approvals to ~/.claude/settings.json.

WHY THIS IS A SCRIPT THE OPERATOR RUNS, AND NOT SOMETHING THE AGENT DOES
-----------------------------------------------------------------------
`/smh-llm-approvals` closes the ALLOW-LIST gate by editing
`.agents/permissions/families.json` and re-rendering. That half an agent can do,
and does.

The SECOND gate — the sandbox escalation gate — is a different file and a
different fence. Measured 2026-09-05 across 20 sessions: 96 stops, 1h16m, every
one of them a command that was ALREADY on the allow list. No permission row can
fix those, because the stop is not "may I run this", it is "this cannot run
inside the sandbox, escalate?".

⛔ The agent CANNOT write `~/.claude/settings.json`. Claude Code's auto-mode
classifier refuses it unconditionally — an agent widening its own sandbox is the
exact thing that guard exists to prevent, and that is correct. Every reshaping of
the edit is refused identically, so retrying is a waste of the operator's turn.
Hence: one script, run by the operator, once per machine.

WHAT IT CHANGES, AND WHY EACH ENTRY
-----------------------------------
`sandbox.filesystem.allowWrite` only. A command escalates when it needs to write
somewhere the sandbox denies; with `autoAllowBashIfSandboxed: true` already set,
a command that CAN run sandboxed is auto-approved and never prompts. So the fix
is to widen what the sandbox permits, NOT to pull commands out of it.

⛔ Do NOT "fix" this by adding rows to `sandbox.excludedCommands`. That does the
OPPOSITE: it removes a command from the sandbox, so it loses the
`autoAllowBashIfSandboxed` auto-approval and needs a permission rule instead.
Operator ruling 2026-09-05, in his words: "those are exclude commands. that does
nothing to help me why are you excluding anything the whole point is to make this
so I dont have to approve them."

The paths added are tool caches every gate run touches and none of which hold
anything secret:

  ~/.cache        pip, ruff, uv, playwright browsers, pytest
  ~/.npm          npm's cache; `npm ci` in the E2E tier writes here
  ~/.local/share  XDG data for the same tools
  ~/.config       XDG config the same tools read-modify-write

Run it:  python3 .agents/scripts/sandbox_widen.py
Preview: python3 .agents/scripts/sandbox_widen.py --dry-run

Idempotent — a path already present is left alone, and the file is only written
when something actually changed. A timestamped backup is made first.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import pathlib
import shutil
import sys

# AIDEV-NOTE: allowWrite ONLY. See the module docstring — excludedCommands is the
# opposite of what this script is for, and adding entries there re-creates the
# prompts this exists to remove.
WANTED_WRITE_PATHS = [
    "~/.cache",
    "~/.npm",
    "~/.local/share",
    "~/.config",
]

SETTINGS = pathlib.Path.home() / ".claude" / "settings.json"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would change and write nothing")
    ap.add_argument("--settings", default=str(SETTINGS),
                    help="settings file to edit (default: ~/.claude/settings.json)")
    a = ap.parse_args()

    path = pathlib.Path(a.settings).expanduser()
    if not path.exists():
        print(f"sandbox-widen: {path} does not exist — nothing to do.", file=sys.stderr)
        return 2

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"sandbox-widen: {path} is not valid JSON ({e}) — refusing to touch it.",
              file=sys.stderr)
        return 2

    sandbox = data.setdefault("sandbox", {})
    fs = sandbox.setdefault("filesystem", {})
    allow = fs.setdefault("allowWrite", [])
    if not isinstance(allow, list):
        print("sandbox-widen: sandbox.filesystem.allowWrite is not a list — refusing.",
              file=sys.stderr)
        return 2

    added = [p for p in WANTED_WRITE_PATHS if p not in allow]
    if not added:
        print("sandbox-widen: already in sync — every path is present. Nothing written.")
        return 0

    allow.extend(added)

    print("sandbox-widen: adding to sandbox.filesystem.allowWrite:")
    for p in added:
        print(f"  + {p}")

    if a.dry_run:
        print("sandbox-widen: --dry-run, nothing written.")
        return 0

    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_suffix(f".json.bak-{stamp}")
    shutil.copy2(path, backup)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"sandbox-widen: wrote {path}")
    print(f"sandbox-widen: backup at {backup}")
    print("sandbox-widen: restart the session (or reload the window) for it to take effect.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
