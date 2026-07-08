# MD Feedback MCP Setup Guide

This walkthrough covers how to set up the **MD Feedback** MCP server for Claude and OpenCode on other machines. This setup ensures that your AI agents can read highlight, fix, and question annotations directly from markdown files via the Model Context Protocol without exporting manually.

## 1. Install the VS Code Extension
1. Open the VS Code Marketplace.
2. Search for and install the **MD Feedback** extension.

## 2. Setup the MCP Configurations
You need to configure both Claude and OpenCode to use the `md-feedback` MCP server. Because some clients might not set the current working directory correctly, we explicitly pass the `--workspace` argument pointing to the root of your project/lobby.

**Note:** Be sure to adjust the `C:\\Sudo_Hatter_Command` path below if your base directory is located elsewhere on the target machine.

### A. Claude Configuration
Create or edit `.claude/mcp.json` at the root of your workspace:

```json
{
  "mcpServers": {
    "md-feedback": {
      "command": "npx",
      "args": [
        "-y",
        "md-feedback",
        "--workspace=C:\\Sudo_Hatter_Command"
      ]
    }
  }
}
```

### B. OpenCode Configuration
Create or edit `.opencode/mcp.json` at the root of your workspace:

```json
{
  "mcpServers": {
    "md-feedback": {
      "command": "npx",
      "args": [
        "-y",
        "md-feedback",
        "--workspace=C:\\Sudo_Hatter_Command"
      ]
    }
  }
}
```

## 3. Usage Flow
1. **Annotate First:** Open any `.md` plan file in VS Code, select text, and press `1` (Highlight), `2` (Fix), or `3` (Question).
2. **Review with AI:** The agents will now read these annotations through the MCP connection automatically.
3. **Approve/Reject:** Once the agent implements fixes, review the changes directly in the markdown file and Approve/Reject via CodeLens or the MD Feedback sidebar.

*(Requires Node.js 18+ for `npx`)*
