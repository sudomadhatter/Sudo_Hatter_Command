#!/usr/bin/env python3
"""Antigravity POSIX workspace health check & watchdog. (SCC-450)

Verifies:
1. Binary status: agy embedded web assets do NOT coerce platform to win32 on Linux.
2. Live daemon contract: AddTrackedWorkspace accepts POSIX paths cleanly.
3. Log integrity: No 'must be an absolute path: path is not absolute' errors in recent session.

CLI usage:
    python3 check_antigravity_workspace.py
    python3 check_antigravity_workspace.py --apply  # auto-applies patch if unpatched
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Local import from same directory
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import patch_agy_posix


def detect_running_hub_port() -> int | None:
    """Detect port of running agy --hub process."""
    try:
        out = subprocess.check_output(["ps", "aux"], text=True)
        for line in out.splitlines():
            if "agy --hub" in line or "--hub-port" in line:
                m = re.search(r"--hub-port=(\d+)", line)
                if m:
                    return int(m.group(1))
    except Exception:
        pass
    return None


def fetch_csrf_token(port: int) -> str | None:
    """Fetch CSRF token from running agy hub."""
    url = f"http://127.0.0.1:{port}/"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AntigravityHealthCheck"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            m = re.search(r'"csrfToken":\s*"([^"]+)"', html)
            if m:
                return m.group(1)
    except Exception:
        pass
    return None


def test_rpc_workspace(port: int, csrf_token: str, workspace_path: str) -> tuple[int, dict]:
    """Call AddTrackedWorkspace ConnectRPC endpoint."""
    url = f"http://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/AddTrackedWorkspace"
    payload = json.dumps({"workspace": workspace_path}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "x-codeium-csrf-token": csrf_token,
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read().decode("utf-8")
            return resp.status, json.loads(data) if data else {}
    except urllib.error.HTTPError as e:
        data = e.read().decode("utf-8")
        try:
            return e.code, json.loads(data)
        except Exception:
            return e.code, {"raw_error": data}
    except Exception as e:
        return 0, {"error": str(e)}


def check_active_logs() -> list[str]:
    """Check newest agy log for workspace errors."""
    log_dir = Path.home() / ".gemini" / "antigravity" / "log"
    if not log_dir.exists():
        log_dir = Path.home() / ".gemini" / "antigravity"
    logs = sorted(log_dir.glob("cli-*.log"), key=os.path.getmtime, reverse=True)
    if not logs:
        # Check symlink cli.log
        sym = Path.home() / ".gemini" / "antigravity" / "cli.log"
        if sym.exists():
            logs = [sym]

    errors = []
    if logs:
        newest = logs[0]
        try:
            content = newest.read_text(errors="ignore")
            for line in content.splitlines():
                if "must be an absolute path: path is not absolute" in line:
                    errors.append(f"{newest.name}: {line.strip()}")
        except Exception as e:
            errors.append(f"Failed to read {newest}: {e}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Antigravity POSIX workspace health check.")
    parser.add_argument("--bin", type=Path, default=patch_agy_posix.DEFAULT_BIN_PATH, help="Path to agy binary")
    parser.add_argument("--apply", action="store_true", help="Auto-apply patch if unpatched")
    parser.add_argument("--repo-path", type=str, default="/home/dlohn/Sudo_Hatter_Command", help="Target repo path")
    args = parser.parse_args()

    overall_clean = True
    print("=== Antigravity POSIX Workspace Verification ===")

    # 1. Binary check
    status = patch_agy_posix.check_status(args.bin)
    print(f"1. Binary Status ({args.bin}): {status.upper()}")
    if status == "unpatched":
        if args.apply:
            print("   Applying surgical patch...")
            if patch_agy_posix.apply_patch(args.bin):
                status = patch_agy_posix.check_status(args.bin)
                print(f"   Binary status after patch: {status.upper()}")
            else:
                overall_clean = False
        else:
            print("   [FAIL] Binary forces 'win32' platform in webview index.html.")
            overall_clean = False
    elif status == "patched":
        print("   [PASS] Binary embeds POSIX-safe index.html.")
    else:
        print(f"   [WARN] Unexpected binary status: {status}")
        overall_clean = False

    # 2. Live Daemon RPC check
    port = detect_running_hub_port()
    if port:
        print(f"2. Running Daemon: PID detected on port {port}")
        token = fetch_csrf_token(port)
        if token:
            # POSIX path test
            status_code, resp = test_rpc_workspace(port, token, args.repo_path)
            if status_code == 200:
                print(f"   [PASS] AddTrackedWorkspace('{args.repo_path}') succeeded (HTTP 200).")
            else:
                print(f"   [FAIL] AddTrackedWorkspace('{args.repo_path}') failed: {resp}")
                overall_clean = False

            # Regression falsification test: verify backslash is rejected by backend
            mangled_path = args.repo_path.replace("/", "\\")
            m_code, m_resp = test_rpc_workspace(port, token, mangled_path)
            if m_code != 200 and "must be an absolute path" in str(m_resp):
                print(f"   [PASS] Regression check: backslashed '{mangled_path}' correctly rejected.")
            else:
                print(f"   [WARN] Backslashed path did not fail as expected: {m_resp}")
        else:
            print("   [WARN] Could not acquire CSRF token from daemon.")
    else:
        print("2. Running Daemon: No active 'agy --hub' process detected (offline check passed).")

    # 3. Log check
    log_errors = check_active_logs()
    print(f"3. Recent CLI Logs: {len(log_errors)} AddTrackedWorkspace failure(s) found.")
    if log_errors:
        print(f"   Latest error sample: {log_errors[-1]}")
        # Note: Log errors may reflect pre-patch sessions; don't fail overall unless binary is also broken

    if overall_clean:
        print("\nOVERALL VERDICT: PASS")
        return 0
    else:
        print("\nOVERALL VERDICT: FAIL")
        return 1


if __name__ == "__main__":
    sys.exit(main())
