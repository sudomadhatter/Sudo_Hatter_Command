#!/usr/bin/env python3
"""Apply the tracked Zoo Code command lists to every decision store on this machine.

Zoo Code decides auto-approval from VS Code globalState (SQLite ``state.vscdb``, ItemTable key
``ZooCodeOrganization.zoo-code``), NOT from ``.vscode/settings.json`` — the tracked file seeds the
store exactly once on a fresh machine and never again, and ``deniedCommands`` never seeds at all.
So after ANY edit to the tracked lists, this script must run once per machine (Mac AND PC), with
VS Code fully closed. Full mechanics: docs/migrations/terminal-permissions-guide.md (SCC-351, SCC-376).

Usage (python3 on both machines; on the PC run it FROM UBUNTU - the Windows stores, the code2
seat's included, are reached through /mnt/c; SCC-376):
    python3 .agents/scripts/zoo_permissions_apply.py --status   # read-only report, safe anytime
    python3 .agents/scripts/zoo_permissions_apply.py --apply    # write lists (VS Code must be closed)
    python3 .agents/scripts/zoo_permissions_apply.py --apply --enable-auto-approve
                                                                # + turn the two master toggles ON

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


def under_wsl() -> bool:
    """True inside a WSL distro: the stores that decide live on the Windows side (SCC-376)."""
    import os
    return bool(os.environ.get("WSL_DISTRO_NAME")) or Path("/proc/sys/fs/binfmt_misc/WSLInterop").exists()


WINDOWS_USERS = Path("/mnt/c/Users")


def _is(p: Path, kind: str) -> bool:
    """is_dir/is_file that reads an UNREADABLE path as absent. Under /mnt/c the other Windows
    accounts (Default, CodexSandboxOffline, ...) raise PermissionError on stat, and the first
    one killed --status before it reached the operator's own store (measured 2026-09-02)."""
    try:
        return p.is_dir() if kind == "dir" else p.is_file()
    except OSError:
        return False


def candidate_dbs(home: Path | None = None, windows_users: Path | None = None) -> list[Path]:
    """Every state.vscdb this machine could hold: the default profile, the named profiles, and the
    ISOLATED second seat (`~/vscode-isolated`, the user-data-dir `code2` launches with) - Mac and PC.

    Under WSL the list is the WINDOWS user's: SCC-376 Phase 4 measured that Zoo runs inside the
    distro but keeps its globalState in the Windows user-data-dir (no state.vscdb exists in a
    distro), so from Ubuntu both Windows stores are reached through /mnt/c. `home` and
    `windows_users` exist for the test; the defaults are the live machine."""
    home = home or Path.home()
    if sys.platform == "darwin":
        users = [home / "Library" / "Application Support" / "Code" / "User"]
    elif sys.platform.startswith("win"):
        import os
        users = [Path(os.environ["APPDATA"]) / "Code" / "User"]
    else:
        users = [home / ".config" / "Code" / "User"]
    isolated = [home / "vscode-isolated" / "User"]
    if windows_users is None and under_wsl():
        windows_users = WINDOWS_USERS
    if windows_users is not None and _is(windows_users, "dir"):
        for u in sorted(p for p in windows_users.iterdir() if _is(p, "dir")):
            users.append(u / "AppData" / "Roaming" / "Code" / "User")
            isolated.append(u / "vscode-isolated" / "User")
    dbs: list[Path] = []
    for user in users:
        dbs.append(user / "globalStorage" / "state.vscdb")
        profiles = user / "profiles"
        if _is(profiles, "dir"):
            dbs += sorted(profiles.glob("*/globalStorage/state.vscdb"))
    dbs += [u / "globalStorage" / "state.vscdb" for u in isolated]
    return [d for d in dbs if _is(d, "file")]


def load_memento(db: Path) -> dict | None:
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        row = con.execute("SELECT value FROM ItemTable WHERE key=?", (ZOO_KEY,)).fetchone()
    finally:
        con.close()
    return json.loads(row[0]) if row else None


def vscode_running() -> bool:
    """Refuse-while-running guard: VS Code flushes globalState on exit and would overwrite us.
    Under WSL the process that matters is the WINDOWS Code.exe, asked through interop by full
    path (the distro's PATH carries no Windows entries). Unable to ask = treat as running."""
    if sys.platform.startswith("win") or under_wsl():
        exe = "tasklist" if sys.platform.startswith("win") else "/mnt/c/Windows/System32/tasklist.exe"
        try:
            out = subprocess.run([exe, "/FI", "IMAGENAME eq Code.exe"], capture_output=True,
                                 encoding="utf-8", errors="replace", text=True).stdout
        except OSError:
            return True
        return "Code.exe" in out
    out = subprocess.run(["pgrep", "-f", "Visual Studio Code"], capture_output=True, encoding="utf-8", text=True)
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
        print("  WARNING: destructiveCommandGuardEnabled=True BYPASSES the lists (external dcg "
              "binary) - turn it OFF in Zoo settings; see the guide section 7.")
    if not (memento.get("autoApprovalEnabled") and memento.get("alwaysAllowExecute")):
        print("  WARNING: master toggles off - no list is consulted until autoApprovalEnabled AND "
              "alwaysAllowExecute are on (Zoo Auto-Approve panel).")


MASTER_TOGGLES = ("autoApprovalEnabled", "alwaysAllowExecute")


def apply(db: Path, memento: dict, allow: list[str], deny: list[str],
          enable_auto_approve: bool = False) -> None:
    backup = db.with_suffix(".vscdb.scc-backup")
    if not backup.exists():
        shutil.copy2(db, backup)
    memento["allowedCommands"] = allow
    memento["deniedCommands"] = deny
    # SCC-376 Phase 6: a seat whose master toggles are off consults NO list - it asks for
    # everything, which is the state this migration exists to remove. Measured on the code2 seat:
    # lists perfectly in sync, autoApprovalEnabled absent, alwaysAllowExecute false. Only these two
    # keys, only behind the flag, and never turned OFF here.
    flipped = []
    if enable_auto_approve:
        for k in MASTER_TOGGLES:
            if memento.get(k) is not True:
                memento[k] = True
                flipped.append(k)
    con = sqlite3.connect(db)
    try:
        con.execute("UPDATE ItemTable SET value=? WHERE key=?",
                    (json.dumps(memento), ZOO_KEY))
        con.commit()
    finally:
        con.close()
    # ⛔ ASCII ONLY, and this line is WHY (SCC-338, measured on the Windows PC 2026-09-01).
    # It used to carry U+2192. Windows' default stdout encoding is cp1252, which cannot encode it,
    # so `print` raised UnicodeEncodeError HERE — after con.commit() above. The lists were written
    # and the operator saw a traceback, so the only sane reading was "it failed": the PC row on
    # SCC-351 sat open for days over a decorative arrow. Same defect family as SCC-335, which fixed
    # the READ side of this pair; keep every operator-facing string in this file 7-bit.
    extra = ("  [master toggles turned ON: " + ", ".join(flipped) + "]") if flipped else ""
    print(f"  applied -> {len(allow)} allow / {len(deny)} deny  (backup: {backup.name}){extra}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--status", action="store_true", help="report every store, change nothing")
    mode.add_argument("--apply", action="store_true", help="write tracked lists into every store")
    ap.add_argument("--enable-auto-approve", action="store_true",
                    help="with --apply: also turn autoApprovalEnabled and alwaysAllowExecute ON in "
                         "any store where they are off (a seat with them off consults no list)")
    args = ap.parse_args()
    if args.enable_auto_approve and not args.apply:
        print("--enable-auto-approve only means anything with --apply")
        return 2

    allow, deny = tracked_lists()
    print(f"tracked file: {TRACKED}  ({len(allow)} allow / {len(deny)} deny)")

    stores = [(db, load_memento(db)) for db in candidate_dbs()]
    stores = [(db, m) for db, m in stores if m is not None]
    if not stores:
        print("no state.vscdb carries the Zoo key - is Zoo Code installed and activated once?")
        return 1

    if args.apply and vscode_running():
        print("REFUSED: VS Code is running - it flushes its own globalState on exit and would "
              "overwrite this write. Quit VS Code fully (Cmd+Q / close all windows), rerun, reopen.")
        return 2

    for db, memento in stores:
        if args.apply:
            apply(db, memento, allow, deny, args.enable_auto_approve)
            memento = load_memento(db)
        report(db, memento, allow, deny)
    return 0


if __name__ == "__main__":
    sys.exit(main())
