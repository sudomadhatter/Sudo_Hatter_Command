"""Tests for tool_sync.py — universal tool and MCP connection configuration engine (SCC-432).

Verifies:
- .agents/tools/connections.json structure, required fields, and tool registrations
- Token replacement ({REPO_ROOT} -> absolute repository path)
- Multi-platform config rendering (Claude Code, OpenCode, Zoo Code, Antigravity)
- opencode.json merge preservation (preserves user settings outside the 'mcp' stanza)
- Drift detection (--check flag)
- Live repository synchronization check
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / ".agents" / "scripts"
TOOLS_DIR = ROOT / ".agents" / "tools"

import tool_sync


def main() -> int:
    c = Cases("tool_sync")

    # 1. Master files existence
    conn_file = TOOLS_DIR / "connections.json"
    schema_file = TOOLS_DIR / "connections.schema.json"
    index_file = TOOLS_DIR / "INDEX.md"

    c.check("connections.json exists", conn_file.is_file(), str(conn_file))
    c.check("connections.schema.json exists", schema_file.is_file(), str(schema_file))
    c.check("INDEX.md exists in .agents/tools/", index_file.is_file(), str(index_file))

    # 2. Schema and JSON parsing
    data = tool_sync.load_connections(conn_file)
    c.check("connections.json parses with 'connections' object", "connections" in data)
    conns = data.get("connections", {})

    # 3. Expected tools roster
    expected_tools = [
        "md-feedback",
        "gcloud",
        "jira",
        "github",
        "firebase",
        "keyway",
        "sentry",
        "playwright",
    ]
    missing = [t for t in expected_tools if t not in conns]
    c.check("all 8 core tools are registered in connections.json", not missing, str(missing))

    # 4. Tool entry contracts
    valid_modes = {"mcp-only", "cli-only", "hybrid"}
    valid_preferred = {"mcp", "cli"}
    contract_errors = []
    for key, item in conns.items():
        for req in ("name", "category", "mode", "preferred", "description"):
            if req not in item:
                contract_errors.append(f"{key}: missing {req}")
        if item.get("mode") not in valid_modes:
            contract_errors.append(f"{key}: invalid mode {item.get('mode')}")
        if item.get("preferred") not in valid_preferred:
            contract_errors.append(f"{key}: invalid preferred {item.get('preferred')}")
        if item.get("mode") in ("mcp-only", "hybrid") and "mcp" not in item:
            contract_errors.append(f"{key}: mode={item.get('mode')} requires 'mcp' block")
        if item.get("mode") in ("cli-only", "hybrid") and "cli" not in item:
            contract_errors.append(f"{key}: mode={item.get('mode')} requires 'cli' block")

    c.check("every connection satisfies schema contract", not contract_errors, str(contract_errors))

    # 5. Token replacement ({REPO_ROOT})
    fake_root = Path("/test/mock/repo")
    rendered_claude = tool_sync.render_claude_mcp(conns, fake_root)
    md_args = rendered_claude.get("mcpServers", {}).get("md-feedback", {}).get("args", [])
    has_resolved_root = any("--workspace=/test/mock/repo" in arg for arg in md_args)
    c.check("{REPO_ROOT} token is dynamically expanded to repo root", has_resolved_root, str(md_args))

    # 6. Multi-platform structure validation
    # 6a. Claude Code (.mcp.json)
    c.check("Claude config has mcpServers object", "mcpServers" in rendered_claude)
    c.check("Claude config contains md-feedback, sentry, playwright",
            all(k in rendered_claude["mcpServers"] for k in ("md-feedback", "sentry", "playwright")))

    # 6b. OpenCode (opencode.json 'mcp' stanza format)
    rendered_opencode = tool_sync.render_opencode_mcp(conns, fake_root)
    c.check("OpenCode stanza has dict of servers", isinstance(rendered_opencode, dict))
    first_opencode_tool = next(iter(rendered_opencode.values()), {})
    c.check("OpenCode local MCP uses type='local' and command array",
            first_opencode_tool.get("type") == "local" and isinstance(first_opencode_tool.get("command"), list),
            str(first_opencode_tool))

    # 6c. Zoo Code (mcp_settings.json)
    rendered_zoo = tool_sync.render_zoo_mcp(conns, fake_root)
    c.check("Zoo Code config has mcpServers with disabled/autoApprove",
            "mcpServers" in rendered_zoo and "disabled" in next(iter(rendered_zoo["mcpServers"].values())))

    # 6d. Antigravity (mcp_config.json)
    rendered_ag = tool_sync.render_antigravity_mcp(conns, fake_root)
    c.check("Antigravity config has mcpServers with command and args",
            "mcpServers" in rendered_ag and "command" in next(iter(rendered_ag["mcpServers"].values())))

    # 7. OpenCode config preservation in apply & drift detection
    with TempDir() as td:
        temp_root = Path(td)
        temp_tools = temp_root / ".agents" / "tools"
        temp_tools.mkdir(parents=True, exist_ok=True)
        shutil.copy2(conn_file, temp_tools / "connections.json")

        # Create a mock opencode.json with custom user settings
        opencode_path = temp_root / "opencode.json"
        opencode_path.write_text(json.dumps({"theme": "dark", "customSetting": 123}), encoding="utf-8")

        # Apply sync targeting the temp root (isolated from machine globals)
        ret = tool_sync.apply_sync(temp_root, sync_globals=False)
        c.check("apply_sync returns 0 on success", ret == 0)

        # Verify opencode.json preserved existing settings while adding 'mcp'
        updated_opencode = json.loads(opencode_path.read_text(encoding="utf-8"))
        c.check("apply_sync preserves non-mcp fields in opencode.json",
                updated_opencode.get("theme") == "dark" and updated_opencode.get("customSetting") == 123)
        c.check("apply_sync added 'mcp' stanza in opencode.json",
                "mcp" in updated_opencode and "md-feedback" in updated_opencode["mcp"])

        # Check that .mcp.json was created
        claude_mcp = temp_root / ".mcp.json"
        c.check("apply_sync created .mcp.json", claude_mcp.is_file())

        # 8. Drift detection (--check)
        clean = (tool_sync.check_drift(temp_root, check_globals=False) == 0)
        c.check("check_drift reports clean (0) when files match rendered output", clean)

        # Tamper with .mcp.json and verify check_drift detects it
        claude_mcp.write_text("{}", encoding="utf-8")
        dirty = (tool_sync.check_drift(temp_root, check_globals=False) == 1)
        c.check("check_drift reports drift (1) when file is tampered", dirty)

    # 9. Live repository check (tool_sync.py --check)
    res = subprocess.run(
        [sys.executable, str(SCRIPTS / "tool_sync.py"), "--check", "--root", str(ROOT)],
        capture_output=True,
        text=True,
    )
    c.check("live tool_sync.py --check exits 0 on current checkout", res.returncode == 0,
            f"exit={res.returncode}, stdout={res.stdout}, stderr={res.stderr}")

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
