# MD Feedback MCP Setup Guide

This walkthrough covers how to set up the **MD Feedback** MCP server for Claude, OpenCode, and Antigravity on other machines. This setup ensures that your AI agents can read highlight, fix, and question annotations directly from markdown files via the Model Context Protocol without exporting manually.

## 1. Install the VS Code Extension

1. Open the VS Code Marketplace.
2. Search for and install the **MD Feedback** extension.

## 2. Setup the MCP Configurations

You need to configure Claude, OpenCode, and Antigravity to use the `md-feedback` MCP server.

### A. Claude Configuration

Create or edit `.claude/mcp.json` at the root of your workspace:

```json
{
  "mcpServers": {
    "md-feedback": {
      "command": "npx",
      "args": [
        "-y",
        "md-feedback"
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
        "md-feedback"
      ]
    }
  }
}
```

### C. Antigravity Configuration

Create or edit `.antigravity/mcp.json` at the root of your workspace:

```json
{
  "mcpServers": {
    "md-feedback": {
      "command": "npx",
      "args": [
        "-y",
        "md-feedback"
      ]
    }
  }
}
```

## 3. Usage Flow

1. **Annotate First:** Open any `.md` plan file in VS Code, select text, and press `1` (Highlight), `2` (Fix), or `3` (Question).
2. **Review with AI:** The agents will now read these annotations through the MCP connection automatically.
3. **Approve/Reject:** Once the agent implements fixes, review the changes directly in the markdown file and Approve/Reject via CodeLens or the MD Feedback sidebar.

*(Requires Node.js 18+ for* `npx`*)*

<!-- HIGHLIGHT_MARK color="#93c5fd" text="MD Feedback MCP Setup Guide" anchor="MD Feedback MCP Setup Guide" -->
<!-- HIGHLIGHT_MARK color="#fca5a5" text="This walkthrough covers how to set up the  MD Feedback  MCP server for Claude, OpenCode, and Antigravity on other machines. This setup ensures that your AI agents can read highlight, fix, and question annotations directly from markdown files via the Model Context Protocol without exporting manually." anchor="This walkthrough covers how to set up the MD Feedback MCP server for Claude, Ope" -->
