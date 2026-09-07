#!/usr/bin/env python3
"""tool_sync.py — Universal tool connections & MCP sync engine (SCC-432).

Single source of truth: .agents/tools/connections.json
Renders platform configs with dynamic {REPO_ROOT} path resolution:
  - Claude Code:      .mcp.json
  - OpenCode:         opencode.json ("mcp" stanza)
  - Zoo Code:         ~/.vscode-server/.../zoocodeorganization.zoo-code/settings/mcp_settings.json
  - Antigravity:      ~/.gemini/config/mcp_config.json

Usage:
  python3 tool_sync.py            # Render and apply to all platforms
  python3 tool_sync.py --check    # Exit 0 if in sync, 1 if drift detected (read-only)
  python3 tool_sync.py --status   # Report connection status & health
  python3 tool_sync.py --apply    # Explicit apply
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
CONNECTIONS_REL = Path(".agents") / "tools" / "connections.json"


def load_connections(root_or_file: Path) -> dict:
    if root_or_file.is_file():
        conn_path = root_or_file
    else:
        conn_path = root_or_file / CONNECTIONS_REL
    if not conn_path.is_file():
        raise FileNotFoundError(f"Connections registry not found: {conn_path}")
    return json.loads(conn_path.read_text(encoding="utf-8"))


def resolve_tokens(val, repo_root: Path):
    root_str = str(repo_root.resolve()).replace("\\", "/")
    if isinstance(val, str):
        return val.replace("{REPO_ROOT}", root_str)
    if isinstance(val, list):
        return [resolve_tokens(x, repo_root) for x in val]
    if isinstance(val, dict):
        return {k: resolve_tokens(v, repo_root) for k, v in val.items()}
    return val


# ── Renderers ────────────────────────────────────────────────────────────────

def render_claude_mcp(connections: dict, repo_root: Path) -> dict:
    servers = {}
    for cid, conn in connections.items():
        mcp = conn.get("mcp")
        if not mcp:
            continue
        platforms = mcp.get("platforms", ["claude"])
        if "claude" in platforms:
            entry = {
                "command": mcp["command"],
                "args": resolve_tokens(mcp.get("args", []), repo_root),
            }
            if "env" in mcp and mcp["env"]:
                entry["env"] = resolve_tokens(mcp["env"], repo_root)
            servers[cid] = entry
    return {"mcpServers": servers}


def render_opencode_mcp(connections: dict, repo_root: Path) -> dict:
    servers = {}
    for cid, conn in connections.items():
        mcp = conn.get("mcp")
        if not mcp:
            continue
        platforms = mcp.get("platforms", ["opencode"])
        if "opencode" in platforms:
            cmd = [mcp["command"]] + resolve_tokens(mcp.get("args", []), repo_root)
            entry = {
                "type": "local",
                "command": cmd,
                "enabled": True,
            }
            if "env" in mcp and mcp["env"]:
                entry["environment"] = resolve_tokens(mcp["env"], repo_root)
            servers[cid] = entry
    return servers


def render_zoo_mcp(connections: dict, repo_root: Path) -> dict:
    servers = {}
    for cid, conn in connections.items():
        mcp = conn.get("mcp")
        if not mcp:
            continue
        platforms = mcp.get("platforms", ["zoo"])
        if "zoo" in platforms:
            entry = {
                "command": mcp["command"],
                "args": resolve_tokens(mcp.get("args", []), repo_root),
                "disabled": False,
                "autoApprove": [],
            }
            if "env" in mcp and mcp["env"]:
                entry["env"] = resolve_tokens(mcp["env"], repo_root)
            servers[cid] = entry
    return {"mcpServers": servers}


def render_antigravity_mcp(connections: dict, repo_root: Path) -> dict:
    servers = {}
    for cid, conn in connections.items():
        mcp = conn.get("mcp")
        if not mcp:
            continue
        platforms = mcp.get("platforms", ["antigravity"])
        if "antigravity" in platforms:
            entry = {
                "command": mcp["command"],
                "args": resolve_tokens(mcp.get("args", []), repo_root),
            }
            if "env" in mcp and mcp["env"]:
                entry["env"] = resolve_tokens(mcp["env"], repo_root)
            servers[cid] = entry
    return {"mcpServers": servers}


# ── Target Path Resolution ───────────────────────────────────────────────────

def get_zoo_settings_paths() -> list[Path]:
    paths = []
    # 1. VS Code Server (WSL / Remote)
    p1 = Path.home() / ".vscode-server" / "data" / "User" / "globalStorage" / "zoocodeorganization.zoo-code" / "settings" / "mcp_settings.json"
    if p1.parent.is_dir() or p1.is_file():
        paths.append(p1)
    # 2. Desktop Linux Code
    p2 = Path.home() / ".config" / "Code" / "User" / "globalStorage" / "zoocodeorganization.zoo-code" / "settings" / "mcp_settings.json"
    if p2.parent.is_dir() or p2.is_file():
        paths.append(p2)
    # 3. macOS
    p3 = Path.home() / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "zoocodeorganization.zoo-code" / "settings" / "mcp_settings.json"
    if p3.parent.is_dir() or p3.is_file():
        paths.append(p3)
    # 4. Windows
    appdata = os.environ.get("APPDATA")
    if appdata:
        p4 = Path(appdata) / "Code" / "User" / "globalStorage" / "zoocodeorganization.zoo-code" / "settings" / "mcp_settings.json"
        if p4.parent.is_dir() or p4.is_file():
            paths.append(p4)
    # If none exist on disk yet, return default p1 for server or p3 for mac
    if not paths:
        paths.append(p3 if sys.platform == "darwin" else p1)
    return paths


def get_antigravity_config_path() -> Path:
    return Path.home() / ".gemini" / "config" / "mcp_config.json"


# ── Actions ──────────────────────────────────────────────────────────────────

def check_drift(root: Path, check_globals: bool = True) -> int:
    data = load_connections(root)
    conns = data.get("connections", {})
    drift = False

    # 1. Claude .mcp.json and mirrors
    claude_target = root / ".mcp.json"
    expected_claude = render_claude_mcp(conns, root)
    if not claude_target.is_file():
        print(f"[DRIFT] Claude .mcp.json missing: {claude_target}")
        drift = True
    else:
        try:
            curr = json.loads(claude_target.read_text(encoding="utf-8"))
            if curr != expected_claude:
                print("[DRIFT] Claude .mcp.json content does not match connections.json")
                drift = True
        except Exception as e:
            print(f"[DRIFT] Claude .mcp.json error: {e}")
            drift = True

    for mirror_rel in (".claude/mcp.json", ".opencode/mcp.json"):
        mirror_path = root / mirror_rel
        if mirror_path.is_file():
            try:
                curr_m = json.loads(mirror_path.read_text(encoding="utf-8"))
                if curr_m != expected_claude:
                    print(f"[DRIFT] {mirror_rel} content does not match connections.json")
                    drift = True
            except Exception as e:
                print(f"[DRIFT] {mirror_rel} error: {e}")
                drift = True

    # 2. OpenCode opencode.json
    opencode_target = root / "opencode.json"
    expected_opencode_mcp = render_opencode_mcp(conns, root)
    if opencode_target.is_file():
        try:
            curr_oc = json.loads(opencode_target.read_text(encoding="utf-8"))
            if curr_oc.get("mcp") != expected_opencode_mcp:
                print("[DRIFT] opencode.json 'mcp' stanza does not match connections.json")
                drift = True
        except Exception as e:
            print(f"[DRIFT] opencode.json error: {e}")
            drift = True
    else:
        print(f"[DRIFT] opencode.json missing: {opencode_target}")
        drift = True

    # 3. Zoo Code
    if check_globals:
        for zp in get_zoo_settings_paths():
            if zp.parent.is_dir():
                expected_zoo = render_zoo_mcp(conns, root)
                if not zp.is_file():
                    print(f"[DRIFT] Zoo Code mcp_settings.json missing: {zp}")
                    drift = True
                else:
                    try:
                        curr_zoo = json.loads(zp.read_text(encoding="utf-8"))
                        if curr_zoo != expected_zoo:
                            print(f"[DRIFT] Zoo Code mcp_settings.json does not match connections.json at {zp}")
                            drift = True
                    except Exception as e:
                        print(f"[DRIFT] Zoo Code mcp_settings.json error at {zp}: {e}")
                        drift = True

    # 4. Antigravity
    if check_globals:
        ag_path = get_antigravity_config_path()
        if ag_path.parent.is_dir():
            expected_ag = render_antigravity_mcp(conns, root)
            if not ag_path.is_file():
                print(f"[DRIFT] Antigravity mcp_config.json missing: {ag_path}")
                drift = True
            else:
                try:
                    curr_ag = json.loads(ag_path.read_text(encoding="utf-8"))
                    if curr_ag != expected_ag:
                        print(f"[DRIFT] Antigravity mcp_config.json does not match connections.json at {ag_path}")
                        drift = True
                except Exception as e:
                    print(f"[DRIFT] Antigravity mcp_config.json error at {ag_path}: {e}")
                    drift = True

    if drift:
        print("tool_sync: DRIFT DETECTED. Run `python3 .agents/scripts/tool_sync.py --apply` to synchronize.")
        return 1

    print("tool_sync: ALL PLATFORM CONFIGS IN SYNC.")
    return 0


def apply_sync(root: Path, sync_globals: bool = True) -> int:
    data = load_connections(root)
    conns = data.get("connections", {})

    # 1. Claude .mcp.json and mirrors
    claude_target = root / ".mcp.json"
    claude_content = render_claude_mcp(conns, root)
    claude_target.write_text(json.dumps(claude_content, indent=2) + "\n", encoding="utf-8")
    print(f"tool_sync: updated {claude_target}")

    for mirror_rel in (".claude/mcp.json", ".opencode/mcp.json"):
        mirror_path = root / mirror_rel
        if mirror_path.parent.is_dir():
            mirror_path.write_text(json.dumps(claude_content, indent=2) + "\n", encoding="utf-8")
            print(f"tool_sync: updated mirror {mirror_path}")

    # 2. OpenCode opencode.json
    opencode_target = root / "opencode.json"
    oc_data = {}
    if opencode_target.is_file():
        try:
            oc_data = json.loads(opencode_target.read_text(encoding="utf-8"))
        except Exception:
            oc_data = {}
    oc_data["mcp"] = render_opencode_mcp(conns, root)
    opencode_target.write_text(json.dumps(oc_data, indent=2) + "\n", encoding="utf-8")
    print(f"tool_sync: updated {opencode_target} ('mcp' stanza)")

    # 3. Zoo Code
    if sync_globals:
        zoo_content = render_zoo_mcp(conns, root)
        for zp in get_zoo_settings_paths():
            try:
                zp.parent.mkdir(parents=True, exist_ok=True)
                zp.write_text(json.dumps(zoo_content, indent=2) + "\n", encoding="utf-8")
                print(f"tool_sync: updated Zoo Code settings at {zp}")
            except Exception as e:
                print(f"tool_sync: [WARN] could not write Zoo Code settings at {zp}: {e}")

    # 4. Antigravity
    if sync_globals:
        ag_path = get_antigravity_config_path()
        try:
            ag_path.parent.mkdir(parents=True, exist_ok=True)
            ag_content = render_antigravity_mcp(conns, root)
            ag_path.write_text(json.dumps(ag_content, indent=2) + "\n", encoding="utf-8")
            print(f"tool_sync: updated Antigravity config at {ag_path}")
        except Exception as e:
            print(f"tool_sync: [WARN] could not write Antigravity config at {ag_path}: {e}")

    return 0


def status_report(root: Path, check_globals: bool = True) -> int:
    data = load_connections(root)
    conns = data.get("connections", {})
    print("\n=== Tool & Connection Status ===")
    print(f"Registry: {root / CONNECTIONS_REL} ({len(conns)} connections registered)\n")
    print(f"{'Tool ID':<15} {'Mode':<10} {'Pref':<6} {'CLI Binary':<12} {'Binary Status':<15} {'Auth / Keyway Env':<35}")
    print("-" * 95)
    for cid, conn in sorted(conns.items()):
        mode = conn.get("mode", "-")
        pref = conn.get("preferred", "-")
        cli = conn.get("cli", {})
        binary = cli.get("binary", "-")
        bin_status = "n/a"
        if binary != "-":
            bin_cmd = binary.split()[0]
            bin_status = "INSTALLED" if shutil.which(bin_cmd) else "MISSING"
        env_keys = ", ".join(conn.get("env_keys", []))
        auth_note = env_keys if env_keys else conn.get("auth", "-")
        if len(auth_note) > 35:
            auth_note = auth_note[:32] + "..."
        print(f"{cid:<15} {mode:<10} {pref:<6} {binary:<12} {bin_status:<15} {auth_note:<35}")

    print("\nRendered Target Checks:")
    print(f"  Claude Code:  {root / '.mcp.json'}")
    print(f"  OpenCode:     {root / 'opencode.json'}")
    if check_globals:
        for zp in get_zoo_settings_paths():
            print(f"  Zoo Code:     {zp} (exists: {zp.is_file()})")
        ag_path = get_antigravity_config_path()
        print(f"  Antigravity:  {ag_path} (exists: {ag_path.is_file()})\n")
    return check_drift(root, check_globals=check_globals)


def main():
    parser = argparse.ArgumentParser(description="Tool Connections & MCP Synchronization Engine")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Workspace root directory")
    parser.add_argument("--check", action="store_true", help="Check for drift without modifying files (exit 0=clean, 1=drift)")
    parser.add_argument("--status", action="store_true", help="Print tool connection status report")
    parser.add_argument("--apply", action="store_true", help="Apply synchronization to all platforms (default if no flag)")
    parser.add_argument("--no-globals", action="store_true", help="Sync/check only workspace-local files (.mcp.json, opencode.json), skipping machine-global configs")

    args = parser.parse_args()
    root = args.root.resolve()
    sync_globals = not args.no_globals

    if args.check:
        sys.exit(check_drift(root, check_globals=sync_globals))
    elif args.status:
        sys.exit(status_report(root, check_globals=sync_globals))
    else:
        # Default action is apply
        sys.exit(apply_sync(root, sync_globals=sync_globals))


if __name__ == "__main__":
    main()
