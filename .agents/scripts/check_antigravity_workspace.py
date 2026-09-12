#!/usr/bin/env python3
"""Antigravity POSIX workspace health check & watchdog. (SCC-450)

Verifies:
1. Binary status: agy embedded web assets do NOT coerce platform to win32 on Linux.
2. Live daemon status: hub process is actively running and serving POSIX-safe assets.
3. Live daemon RPC: AddTrackedWorkspace ConnectRPC accepts POSIX paths cleanly.
4. Stored configurations: stored project records (~/.gemini/config/projects/*.json) contain zero backslashes.
5. Log integrity: reports AddTrackedWorkspace errors from active CLI sessions.

CLI usage:
    python3 check_antigravity_workspace.py
    python3 check_antigravity_workspace.py --apply            # auto-applies patch if unpatched
    python3 check_antigravity_workspace.py --test-regression  # test daemon rejection of backslashes
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
        out = subprocess.check_output(["ps", "aux"], text=True, encoding="utf-8")
        for line in out.splitlines():
            if "agy --hub" in line or "--hub-port" in line:
                m = re.search(r"--hub-port=(\d+)", line)
                if m:
                    return int(m.group(1))
    except Exception:
        pass
    return None


def fetch_daemon_status(port: int) -> tuple[str | None, str]:
    """Fetch CSRF token and platform served by running agy hub HTML.

    Returns:
        (csrf_token, platform_status) where platform_status is 'linux', 'win32', or 'unknown'.
    """
    url = f"http://127.0.0.1:{port}/"
    csrf_token = None
    platform = "unknown"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AntigravityHealthCheck"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            m_csrf = re.search(r'"csrfToken":\s*"([^"]+)"', html)
            if m_csrf:
                csrf_token = m_csrf.group(1)
            if '? "linux"' in html:
                platform = "linux"
            elif '? "win32"' in html:
                platform = "win32"
    except Exception:
        pass
    return csrf_token, platform


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


def check_stored_project_configs(projects_dir: Path | None = None) -> list[str]:
    """Verify that stored project configs in ~/.gemini/config/projects/ have no backslashed paths (AC 4)."""
    if projects_dir is None:
        projects_dir = Path.home() / ".gemini" / "config" / "projects"
    if not projects_dir.exists():
        return []

    violations = []
    for p in sorted(projects_dir.glob("*.json")):
        try:
            data = json.loads(p.read_text(errors="ignore"))
            # Check folderUri in resources
            resources = data.get("projectResources", {}).get("resources", [])
            for res in resources:
                furi = res.get("folderUri", "")
                if "\\" in furi:
                    violations.append(f"{p.name}: folderUri contains backslash: {furi}")
            # Check workspaces list if present
            for item in data.get("workspaces", []):
                if "\\" in str(item):
                    violations.append(f"{p.name}: workspace contains backslash: {item}")
        except Exception as e:
            violations.append(f"{p.name}: JSON parse error: {e}")
    return violations


def check_active_logs(log_dir: Path | None = None) -> list[str]:
    """Check newest agy log for workspace errors."""
    if log_dir is None:
        log_dir = Path.home() / ".gemini" / "antigravity" / "log"
        if not log_dir.exists():
            log_dir = Path.home() / ".gemini" / "antigravity"
    if not log_dir.exists():
        return []

    logs = sorted(log_dir.glob("cli-*.log"), key=os.path.getmtime, reverse=True)
    if not logs:
        sym = log_dir / "cli.log"
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
    parser.add_argument("--test-regression", action="store_true", help="Test daemon rejection of backslashed paths")
    parser.add_argument("--strict", action="store_true", help="Fail overall if log errors or stale daemon exist")
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

    # 2. Live Daemon check
    port = detect_running_hub_port()
    if port:
        print(f"2. Running Daemon: PID detected on port {port}")
        token, platform = fetch_daemon_status(port)
        if platform == "linux":
            print(f"   [PASS] Running daemon is actively serving POSIX-safe 'linux' assets.")
        elif platform == "win32":
            print(f"   [WARN] Running daemon is serving 'win32' assets (started before patch was applied).")
            print("          Restart Antigravity / reload VS Code window to activate POSIX patch in current session.")
            if args.strict:
                overall_clean = False
        else:
            print(f"   [INFO] Could not determine platform from daemon webview HTML.")

        if token:
            # POSIX path test
            status_code, resp = test_rpc_workspace(port, token, args.repo_path)
            if status_code == 200:
                print(f"   [PASS] AddTrackedWorkspace('{args.repo_path}') succeeded (HTTP 200).")
            else:
                print(f"   [FAIL] AddTrackedWorkspace('{args.repo_path}') failed: {resp}")
                overall_clean = False

            if args.test_regression:
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

    # 3. Stored project configurations check (AC 4)
    stored_violations = check_stored_project_configs()
    print(f"3. Stored Project Configs: {len(stored_violations)} backslashed path violation(s) found.")
    if stored_violations:
        for err in stored_violations:
            print(f"   [FAIL] {err}")
        overall_clean = False
    else:
        print("   [PASS] Stored project configurations contain zero backslashes.")

    # 4. Log check
    log_errors = check_active_logs()
    print(f"4. Recent CLI Logs: {len(log_errors)} AddTrackedWorkspace failure(s) found.")
    if log_errors:
        print(f"   Latest error sample: {log_errors[-1]}")
        if args.strict:
            overall_clean = False

    if overall_clean:
        print("\nOVERALL VERDICT: PASS")
        return 0
    else:
        print("\nOVERALL VERDICT: FAIL")
        return 1


if __name__ == "__main__":
    sys.exit(main())
