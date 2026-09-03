#!/usr/bin/env python3
"""Install the translated fence into Antigravity's live store.

Preserves every machine-local key (remoteControlHostname, plugins, ...) and
touches ONLY globalPermissionGrants. Backs the store up once before writing.
Also emits the portable block -- no absolute paths -- for the other machine.

  --status   read-only: what is there now vs what would be written
  --apply    write it
"""
import json, shutil, sys
from pathlib import Path

STORE = Path.home() / ".gemini" / "config" / "config.json"
BACKUP = STORE.with_suffix(".json.scc-backup")
HERE = Path(__file__).parent
FENCE = HERE / "agy_fence.json"
PORTABLE = HERE / "agy-fence.portable.json"


def main(apply_it):
    fence = json.loads(FENCE.read_text())
    cfg = json.loads(STORE.read_text(encoding="utf-8"))
    us = cfg.setdefault("userSettings", {})
    old = us.get("globalPermissionGrants", {})

    print(f"store   : {STORE}")
    print(f"current : allow={len(old.get('allow', []))} deny={len(old.get('deny', []))}")
    print(f"proposed: allow={len(fence['allow'])} deny={len(fence['deny'])}")
    print(f"preserved machine-local keys: "
          f"{sorted(k for k in us if k != 'globalPermissionGrants')}")

    # the portable half: the fence only, identical on every machine
    PORTABLE.write_text(json.dumps(
        {"userSettings": {"globalPermissionGrants": fence}}, indent=2) + "\n")
    print(f"portable block written: {PORTABLE}")

    if not apply_it:
        print("\n(status only -- nothing written)")
        return 0

    if not BACKUP.exists():
        shutil.copy2(STORE, BACKUP)
        print(f"backup  : {BACKUP}")
    else:
        print(f"backup  : {BACKUP} (kept, already existed)")

    us["globalPermissionGrants"] = fence
    STORE.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

    back = json.loads(STORE.read_text(encoding="utf-8"))
    g = back["userSettings"]["globalPermissionGrants"]
    print(f"\nwrote and read back: allow={len(g['allow'])} deny={len(g['deny'])}")
    print("hostname preserved:", back["userSettings"].get("remoteControlHostname"))
    return 0


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv))
