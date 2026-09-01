#!/usr/bin/env python3
"""vscode_sync.py — Synchronize VS Code configurations (extensions, settings, keybindings) across machines.

Supports macOS and Windows PC. Handles:
  1. Extensions: exports list via `code --list-extensions` and installs missing on import.
  2. User Settings: copies/merges user settings.json to/from docs/migrations/vscode_sync/.
  3. Keybindings: copies keybindings.json with automatic 'cmd' <-> 'ctrl' modifier translation.
  4. Zoo Code Providers: reminds operator to use Zoo's 1-click private export/import for API keys.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_BUNDLE_REL = "docs/migrations/vscode_sync"


def find_repo_root(start: Path | None = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for p in [cur, *cur.parents]:
        if (p / ".git").exists() or (p / ".agents").exists():
            return p
    return cur


def get_vscode_user_dir() -> Path:
    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library/Application Support/Code/User"
    elif system == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "Code/User"
        return Path.home() / "AppData/Roaming/Code/User"
    else:
        # Linux
        config = os.environ.get("XDG_CONFIG_HOME")
        if config:
            return Path(config) / "Code/User"
        return Path.home() / ".config/Code/User"


def find_code_binary() -> str | None:
    code = shutil.which("code")
    if code:
        return code

    system = platform.system()
    if system == "Darwin":
        mac_path = "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
        if Path(mac_path).is_file():
            return mac_path
    elif system == "Windows":
        local_app = os.environ.get("LOCALAPPDATA")
        if local_app:
            win_path = Path(local_app) / "Programs/Microsoft VS Code/bin/code.cmd"
            if win_path.is_file():
                return str(win_path)
            win_exe = Path(local_app) / "Programs/Microsoft VS Code/bin/code.exe"
            if win_exe.is_file():
                return str(win_exe)
    return None


def get_installed_extensions(code_bin: str) -> list[str]:
    try:
        res = subprocess.run([code_bin, "--list-extensions"], capture_output=True, text=True, check=True)
        lines = [line.strip().lower() for line in res.stdout.splitlines() if line.strip()]
        return sorted(list(set(lines)))
    except Exception as e:
        print(f"Warning: Could not list extensions using {code_bin}: {e}", file=sys.stderr)
        return []


def read_jsonc(path: Path) -> str:
    """Read a JSON/JSONC file returning raw text."""
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def translate_keybindings(raw_content: str, target_os: str) -> str:
    """Translate keyboard shortcuts between Mac ('cmd') and Windows/Linux ('ctrl')."""
    if not raw_content.strip():
        return raw_content

    if target_os == "Windows" or target_os == "Linux":
        # Replace cmd with ctrl (word-boundary aware)
        translated = re.sub(r'\bcmd\b', 'ctrl', raw_content)
    elif target_os == "Darwin":
        # Replace ctrl with cmd
        translated = re.sub(r'\bctrl\b', 'cmd', raw_content)
    else:
        translated = raw_content

    return translated


def cmd_export(bundle_dir: Path, user_dir: Path, code_bin: str | None, dry_run: bool) -> int:
    print(f"== Exporting VS Code environment to {bundle_dir} ==")
    bundle_dir.mkdir(parents=True, exist_ok=True)

    # 1. Extensions
    if code_bin:
        extensions = get_installed_extensions(code_bin)
        ext_file = bundle_dir / "extensions.txt"
        print(f"Found {len(extensions)} installed extensions.")
        if not dry_run:
            ext_file.write_text("\n".join(extensions) + "\n", encoding="utf-8")
            print(f"  ✓ Exported extensions to {ext_file.name}")
            # Also keep antigravity_extensions/antigravity-extension-ids.txt in sync
            legacy_file = bundle_dir.parent / "antigravity_extensions/antigravity-extension-ids.txt"
            if legacy_file.parent.is_dir():
                legacy_file.write_text("\n".join(extensions) + "\n", encoding="utf-8")
                print(f"  ✓ Updated {legacy_file.name}")
    else:
        print("Notice: 'code' CLI not found on PATH. Skipping extension list export.")

    # 2. Settings
    local_settings = user_dir / "settings.json"
    if local_settings.is_file():
        content = read_jsonc(local_settings)
        out_file = bundle_dir / "settings.json"
        if not dry_run:
            out_file.write_text(content, encoding="utf-8")
            print(f"  ✓ Exported user settings to {out_file.name}")
    else:
        print(f"Notice: No local settings.json found at {local_settings}")

    # 3. Keybindings
    local_kb = user_dir / "keybindings.json"
    if local_kb.is_file():
        content = read_jsonc(local_kb)
        out_kb = bundle_dir / "keybindings.json"
        if not dry_run:
            out_kb.write_text(content, encoding="utf-8")
            print(f"  ✓ Exported keybindings to {out_kb.name}")
    else:
        print(f"Notice: No local keybindings.json found at {local_kb}")

    print("\n[REMINDER] Zoo Code Provider Profiles & API Keys:")
    print("  Private keys (Command Code, OpenRouter, etc.) live in VS Code's internal database.")
    print("  To sync keys to your other machine: Open Zoo Code -> Gear Icon -> 'Export' (save JSON),")
    print("  then on the other machine click 'Import'. Never commit private keys to git.")
    print("\nExport complete.")
    return 0


def cmd_import(bundle_dir: Path, user_dir: Path, code_bin: str | None, dry_run: bool) -> int:
    print(f"== Importing VS Code environment from {bundle_dir} ==")
    target_os = platform.system()
    user_dir.mkdir(parents=True, exist_ok=True)

    # 1. Extensions
    ext_file = bundle_dir / "extensions.txt"
    if not ext_file.is_file():
        # Fallback to legacy
        ext_file = bundle_dir.parent / "antigravity_extensions/antigravity-extension-ids.txt"

    if ext_file.is_file() and code_bin:
        target_exts = [line.strip().lower() for line in ext_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        current_exts = set(get_installed_extensions(code_bin))
        missing = [ext for ext in target_exts if ext not in current_exts]

        if missing:
            print(f"Found {len(missing)} missing extension(s) to install:")
            for ext in missing:
                print(f"  - {ext}")
                if not dry_run:
                    res = subprocess.run([code_bin, "--install-extension", ext], capture_output=True, text=True)
                    if res.returncode == 0:
                        print(f"    ✓ Installed {ext}")
                    else:
                        print(f"    ✗ Failed to install {ext}: {res.stderr.strip()}")
        else:
            print("  ✓ All extensions from bundle are already installed.")
    elif not code_bin:
        print("Warning: 'code' CLI not found. Extensions must be installed manually.")

    # 2. Settings
    bundle_settings = bundle_dir / "settings.json"
    if bundle_settings.is_file():
        target_file = user_dir / "settings.json"
        if target_file.is_file() and not dry_run:
            bak = user_dir / "settings.json.pre-sync.bak"
            shutil.copy2(target_file, bak)
            print(f"  Backed up existing settings to {bak.name}")

        content = read_jsonc(bundle_settings)
        if not dry_run:
            target_file.write_text(content, encoding="utf-8")
            print(f"  ✓ Applied settings to {target_file}")
    else:
        print(f"Notice: No settings.json in bundle at {bundle_settings}")

    # 3. Keybindings
    bundle_kb = bundle_dir / "keybindings.json"
    if bundle_kb.is_file():
        target_kb = user_dir / "keybindings.json"
        if target_kb.is_file() and not dry_run:
            bak_kb = user_dir / "keybindings.json.pre-sync.bak"
            shutil.copy2(target_kb, bak_kb)
            print(f"  Backed up existing keybindings to {bak_kb.name}")

        raw_kb = read_jsonc(bundle_kb)
        adapted_kb = translate_keybindings(raw_kb, target_os)
        if not dry_run:
            target_kb.write_text(adapted_kb, encoding="utf-8")
            print(f"  ✓ Applied adapted keybindings ({target_os} modifiers) to {target_kb}")
    else:
        print(f"Notice: No keybindings.json in bundle at {bundle_kb}")

    print("\n[REMINDER] Zoo Code Provider Profiles & API Keys:")
    print("  If you exported a private Zoo Code profile from your other machine:")
    print("  Open Zoo Code -> Gear Icon -> 'Import' -> select the exported JSON file.")
    print("\nImport complete. Please reload VS Code (Cmd+R or Ctrl+R) to apply changes.")
    return 0


def cmd_status(bundle_dir: Path, user_dir: Path, code_bin: str | None) -> int:
    print(f"== VS Code Sync Status ({platform.system()}) ==")
    target_os = platform.system()

    # 1. Extensions
    ext_file = bundle_dir / "extensions.txt"
    if not ext_file.is_file():
        ext_file = bundle_dir.parent / "antigravity_extensions/antigravity-extension-ids.txt"

    if ext_file.is_file() and code_bin:
        target_exts = [line.strip().lower() for line in ext_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        current_exts = set(get_installed_extensions(code_bin))
        missing = [ext for ext in target_exts if ext not in current_exts]
        extra = [ext for ext in current_exts if ext not in set(target_exts)]

        if missing:
            print(f"\nMissing extensions (in bundle, not installed locally) [{len(missing)}]:")
            for m in missing:
                print(f"  + {m}")
        else:
            print(f"\nExtensions: in sync ({len(target_exts)} bundle extensions installed).")

        if extra:
            print(f"Extra extensions (installed locally, not in bundle) [{len(extra)}]:")
            for e in extra:
                print(f"  ? {e}")
    else:
        print("\nExtensions: Cannot compare (missing bundle or 'code' binary).")

    # 2. Settings check
    bundle_settings = bundle_dir / "settings.json"
    local_settings = user_dir / "settings.json"
    if bundle_settings.is_file() and local_settings.is_file():
        b_txt = read_jsonc(bundle_settings).strip()
        l_txt = read_jsonc(local_settings).strip()
        if b_txt == l_txt:
            print("\nSettings: in sync (byte-for-byte match).")
        else:
            print("\nSettings: DRIFT detected between local and bundle.")
    elif not bundle_settings.is_file():
        print("\nSettings: Bundle file missing.")
    else:
        print("\nSettings: Local file missing.")

    # 3. Keybindings check
    bundle_kb = bundle_dir / "keybindings.json"
    local_kb = user_dir / "keybindings.json"
    if bundle_kb.is_file() and local_kb.is_file():
        adapted_b = translate_keybindings(read_jsonc(bundle_kb), target_os).strip()
        l_kb = read_jsonc(local_kb).strip()
        if adapted_b == l_kb:
            print("Keybindings: in sync (matches target OS bindings).")
        else:
            print("Keybindings: DRIFT detected between local and bundle.")
    elif not bundle_kb.is_file():
        print("Keybindings: Bundle file missing.")
    else:
        print("Keybindings: Local file missing.")

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synchronize VS Code environment between Mac and Windows PC.")
    sub = parser.add_subparsers(dest="command", help="Command to run")

    export_p = sub.add_parser("export", help="Export local VS Code configuration to repo bundle")
    export_p.add_argument("--dry-run", action="store_true", help="Preview export actions without writing files")

    import_p = sub.add_parser("import", help="Import configuration from repo bundle to local VS Code")
    import_p.add_argument("--dry-run", action="store_true", help="Preview import actions without installing/writing")

    sub.add_parser("status", help="Show drift between local VS Code and repo bundle")

    parser.add_argument("--bundle-dir", type=Path, help="Override bundle directory path")
    parser.add_argument("--user-dir", type=Path, help="Override local VS Code user directory path")

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    repo_root = find_repo_root()
    bundle_dir = (args.bundle_dir or (repo_root / DEFAULT_BUNDLE_REL)).resolve()
    user_dir = (args.user_dir or get_vscode_user_dir()).resolve()
    code_bin = find_code_binary()

    if args.command == "export":
        return cmd_export(bundle_dir, user_dir, code_bin, args.dry_run)
    elif args.command == "import":
        return cmd_import(bundle_dir, user_dir, code_bin, args.dry_run)
    elif args.command == "status":
        return cmd_status(bundle_dir, user_dir, code_bin)
    return 0


if __name__ == "__main__":
    sys.exit(main())
