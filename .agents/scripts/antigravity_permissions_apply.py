#!/usr/bin/env python3
"""Apply the rendered Antigravity fence to this machine's live store (SCC-378).

The Antigravity extension decides terminal approvals from ``~/.gemini/config/config.json`` ->
``userSettings.globalPermissionGrants`` (``allow`` / ``deny`` arrays of ``command(...)`` /
``unsandboxed(...)`` rules, matched one anchored regex per token, Deny > Ask > Allow). The tracked
rendering of that block is ``.agents/permissions/antigravity.json``, produced by
``permission_render.py`` from the one canonical source. This script pushes it into the store the
same way ``zoo_permissions_apply.py`` pushes Zoo's - once per machine (Mac AND PC), after any
change to the source. Full mechanics: docs/migrations/terminal-permissions-guide.md.

Usage (python3 on both machines):
    python3 .agents/scripts/antigravity_permissions_apply.py --status   # read-only, safe anytime
    python3 .agents/scripts/antigravity_permissions_apply.py --apply    # write the grants block

Stdlib only. Touches ONLY ``userSettings.globalPermissionGrants``; every other key in the store
(``remoteControlHostname`` is machine-local, ``plugins``, anything the extension adds later) is
preserved in value (re-serialised, non-ASCII kept as written). Writes a one-off ``config.json.scc-backup`` beside the store
before the FIRST write and never overwrites it. Reads the store back after writing and reports.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RENDERED = REPO_ROOT / ".agents" / "permissions" / "antigravity.json"
STORE = Path.home() / ".gemini" / "config" / "config.json"
KEY = "globalPermissionGrants"
IN_SYNC = "in sync with tracked file"


def _grants(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("userSettings", {}).get(KEY, {})


def _norm(g: dict) -> tuple[set, set]:
    return set(g.get("allow", [])), set(g.get("deny", []))


def status(store: Path = STORE, rendered: Path = RENDERED) -> str:
    """One line: IN_SYNC, or what differs (counts only - the rows are in the files)."""
    if not store.exists():
        return f"no store at {store}"
    if not rendered.exists():
        return f"no rendered fence at {rendered}"
    sa, sd = _norm(_grants(store))
    ra, rd = _norm(_grants(rendered))
    if (sa, sd) == (ra, rd):
        return IN_SYNC
    return (f"DRIFT allow: store-only={len(sa - ra)} tracked-missing={len(ra - sa)} | "
            f"deny: store-only={len(sd - rd)} tracked-missing={len(rd - sd)}")


def apply(store: Path = STORE, rendered: Path = RENDERED) -> dict:
    """Write the rendered grants into the store; return a small report dict."""
    cfg = json.loads(store.read_text(encoding="utf-8"))
    fence = _grants(rendered)
    backup = store.with_suffix(".json.scc-backup")
    made_backup = False
    if not backup.exists():
        shutil.copy2(store, backup)
        made_backup = True
    us = cfg.setdefault("userSettings", {})
    us[KEY] = {"allow": list(fence.get("allow", [])), "deny": list(fence.get("deny", []))}
    store.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    back = _grants(store)
    return {
        "store": str(store),
        "backup": str(backup),
        "backup_written_now": made_backup,
        "allow": len(back.get("allow", [])),
        "deny": len(back.get("deny", [])),
        "preserved_keys": sorted(k for k in us if k != KEY),
        "status": status(store, rendered),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--status", action="store_true", help="read-only report (default)")
    p.add_argument("--apply", action="store_true", help="write the rendered grants into the store")
    p.add_argument("--store", type=Path, default=STORE, help="override the store path (tests)")
    p.add_argument("--rendered", type=Path, default=RENDERED, help="override the rendered file")
    a = p.parse_args(argv)

    print(f"store   : {a.store}")
    print(f"rendered: {a.rendered}")
    if not a.apply:
        s = status(a.store, a.rendered)
        print(f"status  : {s}")
        return 0 if s == IN_SYNC else 1
    if not a.store.exists():
        print(f"ERROR: no store at {a.store} - is the Antigravity extension installed here?")
        return 2
    if not a.rendered.exists():
        print(f"ERROR: no rendered fence at {a.rendered} - run permission_render.py first")
        return 2
    r = apply(a.store, a.rendered)
    print(f"backup  : {r['backup']} ({'written now' if r['backup_written_now'] else 'kept, already existed'})")
    print(f"wrote and read back: allow={r['allow']} deny={r['deny']}")
    print(f"preserved keys: {r['preserved_keys']}")
    print(f"status  : {r['status']}")
    return 0 if r["status"] == IN_SYNC else 1


if __name__ == "__main__":
    sys.exit(main())
