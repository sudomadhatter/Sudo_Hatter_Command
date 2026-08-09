"""Regression checks for high-risk workflow reach across command surfaces."""
from __future__ import annotations

from pathlib import Path

from _harness import Cases

ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    c = Cases("command surface contracts")
    command = (ROOT / ".agents/commands/close-task-merge-tree.md").read_text(encoding="utf-8")
    skill = (ROOT / ".agents/skills/close-task-merge-tree/SKILL.md").read_text(encoding="utf-8")
    metadata = (ROOT / ".agents/skills/close-task-merge-tree/agents/openai.yaml").read_text(
        encoding="utf-8"
    )
    sop = (ROOT / "_my_resources/_quick_reference/sudo_workflows_testing.md").read_text(
        encoding="utf-8"
    )
    sync_command = (ROOT / ".agents/commands/sync-agents.md").read_text(encoding="utf-8")

    head = command.split("---", 2)[1]
    c.check(
        "Task close-out command excludes deprecated Codex prompts",
        "platforms: [opencode, antigravity]" in head,
        head.strip(),
    )
    c.check(
        "native skill delegates to the canonical guarded workflow",
        ".agents/commands/close-task-merge-tree.md" in skill and "END TO END" in skill,
    )
    c.check(
        "Codex metadata exposes the native skill mention",
        "$close-task-merge-tree" in metadata,
    )
    c.check(
        "operator SOP names the real Codex invocation surface",
        "/skills" in sop and "$close-task-merge-tree" in sop,
    )
    c.check(
        "sync command states native Codex discovery and retired project fan-out",
        "/skills" in sync_command
        and "Projects stay thin" in sync_command
        and "Do not use `-Maintained`" in sync_command,
    )
    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
