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


def _chk(c: Cases, name: str, ok: bool, fail_msg: str) -> None:
    c.check(name, ok, "" if ok else fail_msg)


def main() -> int:
    c = Cases("memory_long_term_rule")

    # ── 1. constitution.md ───────────────────────────────────────────────────
    const_path = RULES / "constitution.md"
    const_text = const_path.read_text(encoding="utf-8") if const_path.exists() else ""
    _chk(c, "constitution.md carries the long-term memory floor rule",
         "memory" in const_text.lower() and "long-term" in const_text.lower(),
         "constitution.md does not mention long-term memory")
    _chk(c, "constitution.md requires story-scoped facts to live in the story or artifacts",
         "story-scoped" in const_text and ("story" in const_text or "artifact" in const_text),
         "constitution.md does not state that story-scoped facts go in the story or artifacts")
    _chk(c, "constitution.md establishes the delete-on-sight duty for story-scoped memories",
         "delete" in const_text.lower() and "on sight" in const_text.lower(),
         "constitution.md does not mention deleting story-scoped memories on sight")
    _chk(c, "constitution.md requires one-line chat narration on every memory write",
         ("one line" in const_text.lower() or "one-line" in const_text.lower())
         and "chat" in const_text.lower() and "memory" in const_text.lower(),
         "constitution.md does not state the one-line chat narration duty")
    _chk(c, "constitution.md links to agent-memory-is-long-term-only rule",
         "agent-memory-is-long-term-only" in const_text,
         "constitution.md does not reference agent-memory-is-long-term-only")

    roo_const = ROOT / ".roo" / "rules" / "constitution.md"
    roo_text = roo_const.read_text(encoding="utf-8") if roo_const.exists() else ""
    _chk(c, ".roo/rules/constitution.md mirrors the long-term memory rule",
         "agent-memory-is-long-term-only" in roo_text and "long-term" in roo_text.lower(),
         ".roo/rules/constitution.md does not mirror the long-term memory rule")

    # ── 2. agent-memory-is-long-term-only.md ──────────────────────────────────
    rule_path = RULES / "agent-memory-is-long-term-only.md"
    _chk(c, "agent-memory-is-long-term-only.md exists on disk",
         rule_path.is_file(), f"missing file: {rule_path}")
    rule_text = rule_path.read_text(encoding="utf-8") if rule_path.is_file() else ""

    # Frontmatter
    has_fm = rule_text.startswith("---")
    _chk(c, "rule has YAML frontmatter", has_fm, "missing frontmatter delimiters")
    _chk(c, "rule trigger is model_decision",
         "trigger: model_decision" in rule_text, "trigger is not model_decision")
    _chk(c, "rule frontmatter carries triggers keyword list",
         bool(re.search(r"triggers:\s*\[.*memory.*\]", rule_text)),
         "triggers list does not include memory keyword")

    # Content & Law (inspected on markdown body to prevent frontmatter masking)
    body = rule_text.split("---", 2)[2] if rule_text.startswith("---") and rule_text.count("---") >= 2 else rule_text
    body_lower = body.lower()

    _chk(c, "rule articulates the one test: still true and useful after story closes",
         ("still be true" in body_lower or "still true" in body_lower)
         and "useful" in body_lower and "after this story closes" in body_lower,
         "rule does not contain the qualifying test")
    _chk(c, "rule enumerates qualifying categories (operator preferences, quirks, standing rulings)",
         "operator" in body_lower and "quirk" in body_lower and "ruling" in body_lower,
         "rule missing one or more qualifying categories")
    _chk(c, "rule enumerates prohibited categories (measurements, bug mechanisms, temporary gate mismatches)",
         "measurement" in body_lower and "mechanism" in body_lower and "mismatch" in body_lower,
         "rule missing one or more prohibited categories")
    _chk(c, "rule defines delete-on-sight duty",
         "delete" in body_lower and ("on sight" in body_lower or "on-sight" in body_lower),
         "rule does not specify delete-on-sight duty")
    _chk(c, "rule defines narrate-every-write duty",
         ("one line" in body_lower or "one-line" in body_lower)
         and ("chat" in body_lower or "narrat" in body_lower),
         "rule does not specify narrate-every-write duty")

    # ── 3. INDEX.md and AGENTS.md ────────────────────────────────────────────
    idx_path = RULES / "INDEX.md"
    idx_text = idx_path.read_text(encoding="utf-8") if idx_path.exists() else ""
    _chk(c, "INDEX.md registers agent-memory-is-long-term-only as on-demand",
         "| `agent-memory-is-long-term-only.md` | on-demand |" in idx_text,
         "INDEX.md missing on-demand row for agent-memory-is-long-term-only.md")

    root_agents = ROOT / "AGENTS.md"
    root_text = root_agents.read_text(encoding="utf-8") if root_agents.exists() else ""
    sec7 = root_text.split("## 7. PERSISTENCE")[1].split("## 8. PORTABILITY")[0] if "## 7. PERSISTENCE" in root_text else ""
    _chk(c, "AGENTS.md section 7 incorporates the long-term memory mandate",
         "agent-memory-is-long-term-only" in sec7 and "long-term only" in sec7.lower(),
         "AGENTS.md does not mention agent-memory-is-long-term-only in memory section")

    # ── 4. SOP and changelog ─────────────────────────────────────────────────
    sop_path = DOCS / "workflows_testing_SOP.md"
    sop_text = sop_path.read_text(encoding="utf-8") if sop_path.exists() else ""
    _chk(c, "workflows_testing_SOP.md states long-term memory rule",
         "long-term" in sop_text.lower() and "story-scoped" in sop_text.lower(),
         "workflows_testing_SOP.md missing long-term memory rule")

    log_path = DOCS / "workflows_testing_SOP_changelog.md"
    log_text = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    _chk(c, "workflows_testing_SOP_changelog.md carries SCC-386 entry",
         "SCC-386" in log_text,
         "workflows_testing_SOP_changelog.md missing SCC-386 entry")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
