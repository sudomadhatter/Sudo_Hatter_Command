#!/usr/bin/env python3
"""Regression test suite for Antigravity POSIX workspace handling. (SCC-450)

Guards:
1. agy binary embeds index.html with process.platform = "linux" (never "win32").
2. The zip archive integrity and total file size are preserved byte-for-byte.
3. Live/mock RPC contract: POSIX paths succeed, backslashed paths fail.
"""
from __future__ import annotations

import io
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
        self.assertTrue(self.bin_path.exists(), f"{self.bin_path} does not exist")

    def test_zip_bounds_and_structure(self):
        """Web assets zip must be valid and contain index.html and main.js."""
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
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_bin = Path(tmpdir) / "agy"
            shutil.copy2(self.bin_path, tmp_bin)
            orig_size = tmp_bin.stat().st_size

            # If current is unpatched, apply and verify
            status_before = patch_agy_posix.check_status(tmp_bin)
            if status_before == "unpatched":
                success = patch_agy_posix.apply_patch(tmp_bin)
                self.assertTrue(success)
                self.assertEqual(patch_agy_posix.check_status(tmp_bin), "patched")
                self.assertEqual(tmp_bin.stat().st_size, orig_size)

                # Applying again should be idempotent
                self.assertTrue(patch_agy_posix.apply_patch(tmp_bin))
                self.assertEqual(tmp_bin.stat().st_size, orig_size)
            elif status_before == "patched":
                # Already patched: verify content
                data = tmp_bin.read_bytes()
                start, end = patch_agy_posix.find_zip_bounds(data)
                zf = zipfile.ZipFile(io.BytesIO(data[start:end]))
                html = zf.read("index.html")
                self.assertIn(b"? \"linux\"", html)
                self.assertNotIn(b"? \"win32\"", html)

    def test_live_daemon_rpc_contract(self):
        """Live agy daemon (if running) must accept POSIX and reject backslash."""
        port = check_antigravity_workspace.detect_running_hub_port()
        if not port:
            self.skipTest("No running agy daemon detected")

        token = check_antigravity_workspace.fetch_csrf_token(port)
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
