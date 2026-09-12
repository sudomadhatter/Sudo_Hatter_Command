#!/usr/bin/env python3
"""Regression test suite for Antigravity POSIX workspace handling. (SCC-450)

Guards:
1. agy binary embeds index.html with process.platform = "linux" (never "win32").
2. The zip archive integrity and total file size are preserved byte-for-byte.
3. Live/mock RPC contract: POSIX paths succeed, backslashed paths fail.
4. AC 4 check: Stored project configurations (~/.gemini/config/projects/*.json) contain zero backslashes.
5. Deterministic unit tests: log parsing, backup restoration, dynamic zip bounds, and patch idempotency.
"""
from __future__ import annotations

import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))
import patch_agy_posix
import check_antigravity_workspace


class TestAntigravityPosix(unittest.TestCase):

    def setUp(self):
        self.bin_path = patch_agy_posix.DEFAULT_BIN_PATH

    def test_binary_exists(self):
        """Binary ~/.gemini/bin/agy must exist on this machine."""
        if not self.bin_path.exists():
            self.skipTest(f"Binary {self.bin_path} not installed in this environment")
        self.assertTrue(self.bin_path.exists(), f"{self.bin_path} does not exist")

    def test_zip_bounds_and_structure(self):
        """Web assets zip must be valid and contain index.html and main.js."""
        if not self.bin_path.exists():
            self.skipTest(f"Binary {self.bin_path} not installed in this environment")
        data = self.bin_path.read_bytes()
        start, end = patch_agy_posix.find_zip_bounds(data)
        self.assertGreater(end, start)
        self.assertEqual(end - start, patch_agy_posix.EXPECTED_ZIP_LEN)

        zf = zipfile.ZipFile(io.BytesIO(data[start:end]))
        names = zf.namelist()
        self.assertIn("index.html", names)
        self.assertIn("main.js", names)
        self.assertEqual(len(names), 300)

    def test_patch_application_and_idempotency(self):
        """Patching must be idempotent and preserve exact binary length."""
        if not self.bin_path.exists():
            self.skipTest(f"Binary {self.bin_path} not installed in this environment")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_bin = Path(tmpdir) / "agy"
            orig_backup = self.bin_path.with_name(f"{self.bin_path.name}.bak.orig")

            # 1. Deterministic unpatched -> patched test using baseline backup if present
            if orig_backup.exists():
                shutil.copy2(orig_backup, tmp_bin)
                self.assertEqual(patch_agy_posix.check_status(tmp_bin), "unpatched")
                orig_size = tmp_bin.stat().st_size

                success = patch_agy_posix.apply_patch(tmp_bin)
                self.assertTrue(success)
                self.assertEqual(patch_agy_posix.check_status(tmp_bin), "patched")
                self.assertEqual(tmp_bin.stat().st_size, orig_size)

                # Applying again on patched binary must be idempotent
                self.assertTrue(patch_agy_posix.apply_patch(tmp_bin))
                self.assertEqual(tmp_bin.stat().st_size, orig_size)
            else:
                # Fallback: copy current binary
                shutil.copy2(self.bin_path, tmp_bin)
                orig_size = tmp_bin.stat().st_size
                # Test idempotency directly
                self.assertTrue(patch_agy_posix.apply_patch(tmp_bin))
                self.assertEqual(tmp_bin.stat().st_size, orig_size)

            # Verify index.html content
            data = tmp_bin.read_bytes()
            start, end = patch_agy_posix.find_zip_bounds(data)
            zf = zipfile.ZipFile(io.BytesIO(data[start:end]))
            html = zf.read("index.html")
            self.assertIn(b"? \"linux\"", html)
            self.assertNotIn(b"? \"win32\"", html)

    def test_backup_and_restore(self):
        """Restore must prioritize newest timestamped backup over .orig unless requested."""
        with tempfile.TemporaryDirectory() as tmpdir:
            td = Path(tmpdir)
            bin_p = td / "agy"
            bin_p.write_text("v2_live")
            (td / "agy.bak.orig").write_text("v1_orig")
            (td / "agy.bak.20261001_120000").write_text("v2_recent")

            # Default restore chooses newest timestamped backup
            self.assertTrue(patch_agy_posix.restore_backup(bin_p, use_orig=False))
            self.assertEqual(bin_p.read_text(), "v2_recent")

            # Explicit orig restore chooses .orig
            self.assertTrue(patch_agy_posix.restore_backup(bin_p, use_orig=True))
            self.assertEqual(bin_p.read_text(), "v1_orig")

            # Nonexistent path returns False
            self.assertFalse(patch_agy_posix.restore_backup(Path("/nonexistent/bin/agy")))

    def test_find_zip_bounds_error_handling(self):
        """find_zip_bounds must raise RuntimeError cleanly on malformed or trailing buffers."""
        # Trailing partial EOCD marker should not crash with struct.error
        corrupt_trailing = b"x" * 100 + b"PK\x05\x06" + b"y" * 5
        with self.assertRaises(RuntimeError):
            patch_agy_posix.find_zip_bounds(corrupt_trailing)

        # Non-zip buffer
        with self.assertRaises(RuntimeError):
            patch_agy_posix.find_zip_bounds(b"random content without zip headers")

    def test_check_status_corrupted_binary(self):
        """check_status must return 'unknown' on invalid binary instead of crashing."""
        self.assertEqual(patch_agy_posix.check_status(Path(sys.executable)), "unknown")
        self.assertEqual(patch_agy_posix.check_status(Path("/nonexistent_agy_path")), "missing")

    def test_stored_project_configs_ac4(self):
        """check_stored_project_configs must pass clean POSIX and catch backslashes (AC 4)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            proj_dir = Path(tmpdir)
            # 1. Valid POSIX record
            valid_file = proj_dir / "valid.json"
            valid_file.write_text(json.dumps({
                "id": "test-id-1",
                "projectResources": {
                    "resources": [{"folderUri": "file:///home/dlohn/Sudo_Hatter_Command"}]
                }
            }))
            self.assertEqual(check_antigravity_workspace.check_stored_project_configs(proj_dir), [])

            # 2. Corrupted record with backslashes
            invalid_file = proj_dir / "invalid.json"
            invalid_file.write_text(json.dumps({
                "id": "test-id-2",
                "projectResources": {
                    "resources": [{"folderUri": "file:///home\\dlohn\\Sudo_Hatter_Command"}]
                }
            }))
            errors = check_antigravity_workspace.check_stored_project_configs(proj_dir)
            self.assertEqual(len(errors), 1)
            self.assertIn("folderUri contains backslash", errors[0])

    def test_check_active_logs_unit(self):
        """check_active_logs must parse errors accurately in isolation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            clean_log = log_dir / "cli-20260912_100000.log"
            clean_log.write_text("I0912 10:00:00 Starting daemon\nI0912 10:00:01 Ready\n")
            self.assertEqual(check_antigravity_workspace.check_active_logs(log_dir), [])

            # Error log
            err_log = log_dir / "cli-20260912_110000.log"
            err_log.write_text(
                "I0912 11:00:00 Starting daemon\n"
                "E0912 11:00:01 123 interceptor.go:70] /AddTrackedWorkspace: \\home\\dlohn must be an absolute path: path is not absolute\n"
            )
            errors = check_antigravity_workspace.check_active_logs(log_dir)
            self.assertEqual(len(errors), 1)
            self.assertIn("must be an absolute path: path is not absolute", errors[0])

    def test_live_daemon_rpc_contract(self):
        """Live agy daemon (if running) must accept POSIX and reject backslash."""
        port = check_antigravity_workspace.detect_running_hub_port()
        if not port:
            self.skipTest("No running agy daemon detected")

        token, _ = check_antigravity_workspace.fetch_daemon_status(port)
        self.assertIsNotNone(token, "CSRF token could not be retrieved from live hub")

        # 1. POSIX path must succeed
        posix_path = "/home/dlohn/Sudo_Hatter_Command"
        code, resp = check_antigravity_workspace.test_rpc_workspace(port, token, posix_path)
        self.assertEqual(code, 200, f"AddTrackedWorkspace failed for {posix_path}: {resp}")

        # 2. Mangled path must fail
        mangled_path = posix_path.replace("/", "\\")
        m_code, m_resp = check_antigravity_workspace.test_rpc_workspace(port, token, mangled_path)
        self.assertNotEqual(m_code, 200)
        self.assertIn("must be an absolute path", str(m_resp))


if __name__ == "__main__":
    unittest.main()
