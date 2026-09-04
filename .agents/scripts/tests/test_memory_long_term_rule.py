"""Tests for SCC-386: Global .agents rule — agent memory is long-term only.

Asserts that:
- .agents/rules/constitution.md carries the floor rule establishing memory as long-term only,
  story-scoped facts in story/artifacts, delete-on-sight, and one-line chat narration.
- .agents/rules/agent-memory-is-long-term-only.md exists, carries model_decision trigger frontmatter,
  states the one test, qualifies long-term facts, forbids temporary facts, and details the duties.
- .agents/rules/INDEX.md registers the rule under on-demand.
- AGENTS.md §7 references the long-term memory rule.
- docs/_scc_sops_prds/workflows_testing_SOP.md and its changelog record the rule.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import Cases

ROOT = Path(__file__).resolve().parents[3]
RULES = ROOT / ".agents" / "rules"
DOCS = ROOT / "docs" / "_scc_sops_prds"


def main() -> int:
    c = Cases("memory_long_term_rule")

    # ── 1. constitution.md ───────────────────────────────────────────────────
    const_path = RULES / "constitution.md"
    const_text = const_path.read_text(encoding="utf-8") if const_path.exists() else ""
    c.check("constitution.md carries the long-term memory floor rule",
            "memory" in const_text.lower() and "long-term" in const_text.lower(),
            "constitution.md does not mention long-term memory")
    c.check("constitution.md requires story-scoped facts to live in the story or artifacts",
            "story-scoped" in const_text and ("story" in const_text or "artifact" in const_text),
            "constitution.md does not state that story-scoped facts go in the story or artifacts")
    c.check("constitution.md establishes the delete-on-sight duty for story-scoped memories",
            "delete" in const_text.lower() and "on sight" in const_text.lower(),
            "constitution.md does not mention deleting story-scoped memories on sight")
    c.check("constitution.md requires one-line chat narration on every memory write",
            "one line" in const_text.lower() and ("chat" in const_text.lower() or "written" in const_text.lower()),
            "constitution.md does not state the one-line chat narration duty")
    c.check("constitution.md links to agent-memory-is-long-term-only rule",
            "agent-memory-is-long-term-only" in const_text,
            "constitution.md does not reference agent-memory-is-long-term-only")

    # ── 2. agent-memory-is-long-term-only.md ──────────────────────────────────
    rule_path = RULES / "agent-memory-is-long-term-only.md"
    c.check("agent-memory-is-long-term-only.md exists on disk",
            rule_path.is_file(), f"missing file: {rule_path}")
    rule_text = rule_path.read_text(encoding="utf-8") if rule_path.is_file() else ""

    # Frontmatter
    has_fm = rule_text.startswith("---")
    c.check("rule has YAML frontmatter", has_fm, "missing frontmatter delimiters")
    c.check("rule trigger is model_decision",
            "trigger: model_decision" in rule_text, "trigger is not model_decision")
    c.check("rule frontmatter carries triggers keyword list",
            bool(re.search(r"triggers:\s*\[.*memory.*\]", rule_text)),
            "triggers list does not include memory keyword")

    # Content & Law
    c.check("rule articulates the one test: still true and useful after story closes",
            "still true and still useful" in rule_text.lower() or "after this story closes" in rule_text.lower(),
            "rule does not contain the qualifying test")
    c.check("rule enumerates qualifying categories (operator preferences, quirks, standing rulings)",
            "operator" in rule_text.lower() and "quirk" in rule_text.lower() and "ruling" in rule_text.lower(),
            "rule missing one or more qualifying categories")
    c.check("rule enumerates prohibited categories (measurements, bug mechanisms, temporary gate mismatches)",
            "measurement" in rule_text.lower() and "mechanism" in rule_text.lower() and "mismatch" in rule_text.lower(),
            "rule missing one or more prohibited categories")
    c.check("rule defines delete-on-sight duty",
            "delete" in rule_text.lower() and "on sight" in rule_text.lower(),
            "rule does not specify delete-on-sight duty")
    c.check("rule defines narrate-every-write duty",
            "one line" in rule_text.lower() and ("chat" in rule_text.lower() or "narrat" in rule_text.lower()),
            "rule does not specify narrate-every-write duty")

    # ── 3. INDEX.md and AGENTS.md ────────────────────────────────────────────
    idx_path = RULES / "INDEX.md"
    idx_text = idx_path.read_text(encoding="utf-8") if idx_path.exists() else ""
    c.check("INDEX.md registers agent-memory-is-long-term-only as on-demand",
            "| `agent-memory-is-long-term-only.md` | on-demand |" in idx_text,
            "INDEX.md missing on-demand row for agent-memory-is-long-term-only.md")

    root_agents = ROOT / "AGENTS.md"
    root_text = root_agents.read_text(encoding="utf-8") if root_agents.exists() else ""
    c.check("AGENTS.md section 7 incorporates the long-term memory mandate",
            "agent-memory-is-long-term-only" in root_text and "long-term only" in root_text.lower(),
            "AGENTS.md does not mention agent-memory-is-long-term-only in memory section")

    # ── 4. SOP and changelog ─────────────────────────────────────────────────
    sop_path = DOCS / "workflows_testing_SOP.md"
    sop_text = sop_path.read_text(encoding="utf-8") if sop_path.exists() else ""
    c.check("workflows_testing_SOP.md states long-term memory rule",
            "long-term" in sop_text.lower() and "story-scoped" in sop_text.lower(),
            "workflows_testing_SOP.md missing long-term memory rule")

    log_path = DOCS / "workflows_testing_SOP_changelog.md"
    log_text = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    c.check("workflows_testing_SOP_changelog.md carries SCC-386 entry",
            "SCC-386" in log_text,
            "workflows_testing_SOP_changelog.md missing SCC-386 entry")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
