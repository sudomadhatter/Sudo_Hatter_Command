#!/usr/bin/env python3
"""test_vscode_sync.py — Unit tests for VS Code environment sync engine."""

import sys
import tempfile
from pathlib import Path

# Add scripts directory to sys.path
SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

import vscode_sync


def test_keybinding_translation():
    mac_kb = '[{"key": "cmd+alt+r", "command": "workbench.scm.action.showRepositories"},\n' \
             ' {"key": "shift+cmd+z", "command": "zoo-code.openInNewTab"}]'

    win_kb = vscode_sync.translate_keybindings(mac_kb, "Windows")
    assert "ctrl+alt+r" in win_kb, f"Expected ctrl+alt+r in translated keybindings: {win_kb}"
    assert "shift+ctrl+z" in win_kb, f"Expected shift+ctrl+z in translated keybindings: {win_kb}"
    assert "cmd" not in win_kb, f"Unexpected 'cmd' remaining in Windows translation: {win_kb}"

    # Back to Mac
    restored = vscode_sync.translate_keybindings(win_kb, "Darwin")
    assert "cmd+alt+r" in restored, f"Expected cmd+alt+r in Mac translation: {restored}"
    assert "shift+cmd+z" in restored, f"Expected shift+cmd+z in Mac translation: {restored}"
    print("[PASS] test_keybinding_translation")


def test_export_import_roundtrip():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        user_dir = tmp_path / "User"
        bundle_dir = tmp_path / "bundle"
        user_dir.mkdir(parents=True)

        # Seed mock user files
        (user_dir / "settings.json").write_text('{"editor.minimap.enabled": false}', encoding="utf-8")
        (user_dir / "keybindings.json").write_text('[{"key": "cmd+alt+r", "command": "test"}]', encoding="utf-8")

        # Export
        rc = vscode_sync.cmd_export(bundle_dir, user_dir, code_bin=None, dry_run=False)
        assert rc == 0
        assert (bundle_dir / "settings.json").is_file()
        assert (bundle_dir / "keybindings.json").is_file()

        # Import into another clean user dir
        dest_user_dir = tmp_path / "DestUser"
        rc_imp = vscode_sync.cmd_import(bundle_dir, dest_user_dir, code_bin=None, dry_run=False)
        assert rc_imp == 0
        assert (dest_user_dir / "settings.json").is_file()
        assert (dest_user_dir / "keybindings.json").is_file()

        # Verify content
        assert "editor.minimap.enabled" in (dest_user_dir / "settings.json").read_text(encoding="utf-8")
        print("[PASS] test_export_import_roundtrip")


def main():
    test_keybinding_translation()
    test_export_import_roundtrip()
    print("-- All test_vscode_sync checks passed --")
    return 0


if __name__ == "__main__":
    sys.exit(main())
