#!/usr/bin/env python3
"""Apply the tracked Zoo Code command lists to every decision store on this machine.

Zoo Code decides auto-approval from VS Code globalState (SQLite ``state.vscdb``, ItemTable key
``ZooCodeOrganization.zoo-code``), NOT from ``.vscode/settings.json`` — the tracked file seeds the
store exactly once on a fresh machine and never again, and ``deniedCommands`` never seeds at all.
So after ANY edit to the tracked lists, this script must run once per machine (Mac AND PC), with
VS Code fully closed. Full mechanics: docs/migrations/zoo-code-permissions-guide.md (SCC-351).

Usage (Mac: python3 · PC: python):
    python3 .agents/scripts/zoo_permissions_apply.py --status   # read-only report, safe anytime
    python3 .agents/scripts/zoo_permissions_apply.py --apply    # write lists (VS Code must be closed)

Stdlib only. Touches ONLY the two list keys inside the Zoo memento JSON — never the secret://
rows (API keys) and never the toggles. Writes a one-off .scc-backup next to each db first.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

ZOO_KEY = "ZooCodeOrganization.zoo-code"
REPO_ROOT = Path(__file__).resolve().parents[2]
TRACKED = REPO_ROOT / ".vscode" / "settings.json"


def tracked_lists() -> tuple[list[str], list[str]]:
    """Read zoo-code.allowedCommands / deniedCommands from the JSONC settings file."""
    text = TRACKED.read_text(encoding="utf-8")
    plain = re.sub(r"^\s*//.*$", "", text, flags=re.M)  # line comments only; none are inline
    data = json.loads(plain)
    return data["zoo-code.allowedCommands"], data["zoo-code.deniedCommands"]


def candidate_dbs() -> list[Path]:
    """Every state.vscdb this machine could hold: default profile + named profiles, Mac and PC."""
    if sys.platform == "darwin":
        user = Path.home() / "Library" / "Application Support" / "Code" / "User"
    elif sys.platform.startswith("win"):
        import os
        user = Path(os.environ["APPDATA"]) / "Code" / "User"
    else:
        user = Path.home() / ".config" / "Code" / "User"
    dbs = [user / "globalStorage" / "state.vscdb"]
    profiles = user / "profiles"
    if profiles.is_dir():
        dbs += sorted(profiles.glob("*/globalStorage/state.vscdb"))
    return [d for d in dbs if d.is_file()]


def load_memento(db: Path) -> dict | None:
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        row = con.execute("SELECT value FROM ItemTable WHERE key=?", (ZOO_KEY,)).fetchone()
    finally:
        con.close()
    return json.loads(row[0]) if row else None


def vscode_running() -> bool:
    """Refuse-while-running guard: VS Code flushes globalState on exit and would overwrite us."""
    if sys.platform.startswith("win"):
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Code.exe"],
                             capture_output=True, text=True).stdout
        return "Code.exe" in out
    out = subprocess.run(["pgrep", "-f", "Visual Studio Code"], capture_output=True, text=True)
    return out.returncode == 0


def diff_counts(state: list[str], tracked: list[str]) -> str:
    s, t = set(state), set(tracked)
    if s == t:
        return "in sync with tracked file"
    return f"DRIFT: {len(t - s)} tracked entries missing from store, {len(s - t)} store-only entries"


def report(db: Path, memento: dict, allow: list[str], deny: list[str]) -> None:
    print(f"\n{db}")
    print(f"  allowedCommands: {len(memento.get('allowedCommands', []))}  "
          f"({diff_counts(memento.get('allowedCommands', []), allow)})")
    print(f"  deniedCommands:  {len(memento.get('deniedCommands', []))}  "
          f"({diff_counts(memento.get('deniedCommands', []), deny)})")
    for key in ("autoApprovalEnabled", "alwaysAllowExecute", "destructiveCommandGuardEnabled"):
        print(f"  {key}: {memento.get(key)}")
    if memento.get("destructiveCommandGuardEnabled"):
        print("  ⚠️ destructiveCommandGuardEnabled=True BYPASSES the lists (external dcg binary) — "
              "turn it OFF in Zoo settings; see the guide §5.")
    if not (memento.get("autoApprovalEnabled") and memento.get("alwaysAllowExecute")):
        print("  ⚠️ master toggles off — no list is consulted until autoApprovalEnabled AND "
              "alwaysAllowExecute are on (Zoo Auto-Approve panel).")


def apply(db: Path, memento: dict, allow: list[str], deny: list[str]) -> None:
    backup = db.with_suffix(".vscdb.scc-backup")
    if not backup.exists():
        shutil.copy2(db, backup)
    memento["allowedCommands"] = allow
    memento["deniedCommands"] = deny
    con = sqlite3.connect(db)
    try:
        con.execute("UPDATE ItemTable SET value=? WHERE key=?",
                    (json.dumps(memento), ZOO_KEY))
        con.commit()
    finally:
        con.close()
    print(f"  applied → {len(allow)} allow / {len(deny)} deny  (backup: {backup.name})")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--status", action="store_true", help="report every store, change nothing")
    mode.add_argument("--apply", action="store_true", help="write tracked lists into every store")
    args = ap.parse_args()

    allow, deny = tracked_lists()
    print(f"tracked file: {TRACKED}  ({len(allow)} allow / {len(deny)} deny)")

    stores = [(db, load_memento(db)) for db in candidate_dbs()]
    stores = [(db, m) for db, m in stores if m is not None]
    if not stores:
        print("no state.vscdb carries the Zoo key — is Zoo Code installed and activated once?")
        return 1

    if args.apply and vscode_running():
        print("REFUSED: VS Code is running — it flushes its own globalState on exit and would "
              "overwrite this write. Quit VS Code fully (Cmd+Q / close all windows), rerun, reopen.")
        return 2

    for db, memento in stores:
        if args.apply:
            apply(db, memento, allow, deny)
            memento = load_memento(db)
        report(db, memento, allow, deny)
    return 0


if __name__ == "__main__":
    sys.exit(main())
