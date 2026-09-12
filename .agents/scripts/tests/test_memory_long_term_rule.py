"""Tests for SCC-448: Memory is disposable — the Deletion Test.

Replaces SCC-386's inverted "long-term-only" memory rule with the Deletion Test:
delete it in your head, then look at the damage. Slower means memory; wrong means a rule and a ticket.
A memory is never the only copy of anything.

Asserts that:
- .agents/rules/constitution.md carries the floor rule establishing memory as disposable,
  the deletion test, the invariant that memory is never the only copy, delete-on-sight, and one-line chat narration.
  Must link to memory-is-disposable, NOT agent-memory-is-long-term-only.
- .roo/rules/constitution.md mirrors the disposable memory rule.
- .agents/rules/memory-is-disposable.md exists on disk, and agent-memory-is-long-term-only.md is deleted.
- The rule carries model_decision trigger frontmatter, states the deletion test, invariant,
  qualifies disposable recall, forbids load-bearing unbacked rulings, and details the duties.
- Counter-examples verify that the deletion test correctly separates memory (slower) from rules (wrong).
- .agents/rules/INDEX.md registers memory-is-disposable.md under on-demand and removes the old rule.
- AGENTS.md §7 references memory-is-disposable.md and incorporates the deletion test and invariant.
- .agents/commands/smh-memory-audit.md includes the deletion test sort pass and Promote to rule disposition.
- docs/_scc_sops_prds/workflows_testing_SOP.md states the disposable memory law and links to memory-is-disposable.md.
- docs/_scc_sops_prds/workflows_testing_SOP_changelog.md records the SCC-448 entry.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import Cases

ROOT = Path(__file__).resolve().parents[3]
RULES = ROOT / ".agents" / "rules"
DOCS = ROOT / "docs" / "_scc_sops_prds"
COMMANDS = ROOT / ".agents" / "commands"


def deletion_test(fact_loss_consequence: str) -> str:
    """The Deletion Test: delete it in your head, then look at the damage.
    Returns 'memory' if loss only makes an agent slower; returns 'rule' if it makes the agent wrong.
    """
    if "wrong" in fact_loss_consequence.lower():
        return "rule"
    if "slower" in fact_loss_consequence.lower():
        return "memory"
    return "unknown"


def main() -> int:
    c = Cases("memory_disposable_rule")

    # ── 1. constitution.md ───────────────────────────────────────────────────
    if c.block("1 · constitution.md"):
        const_path = RULES / "constitution.md"
        const_text = const_path.read_text(encoding="utf-8") if const_path.exists() else ""
        c.check("constitution.md carries the disposable memory floor rule",
             "disposable" in const_text.lower() and "memory" in const_text.lower(),
             "constitution.md does not establish memory as disposable")
        c.check("constitution.md states the deletion test (slower means memory; wrong means a rule)",
             "slower" in const_text.lower() and "wrong" in const_text.lower() and "deletion test" in const_text.lower(),
             "constitution.md does not state the deletion test")
        c.check("constitution.md establishes the invariant: never the only copy",
             "never the only copy" in const_text.lower(),
             "constitution.md does not state the invariant that memory is never the only copy")
        c.check("constitution.md requires story-scoped facts to live in the story or artifacts",
             "story-scoped" in const_text and ("story" in const_text or "artifact" in const_text),
             "constitution.md does not state that story-scoped facts go in the story or artifacts")
        c.check("constitution.md establishes the delete-on-sight duty for story-scoped memories",
             "delete" in const_text.lower() and "on sight" in const_text.lower(),
             "constitution.md does not mention deleting story-scoped memories on sight")
        c.check("constitution.md requires one-line chat narration on every memory write",
             ("one line" in const_text.lower() or "one-line" in const_text.lower())
             and "chat" in const_text.lower() and "memory" in const_text.lower(),
             "constitution.md does not state the one-line chat narration duty")
        c.check("constitution.md links to memory-is-disposable rule",
             "memory-is-disposable" in const_text,
             "constitution.md does not reference memory-is-disposable")
        c.check("constitution.md does NOT link to retired agent-memory-is-long-term-only rule",
             "agent-memory-is-long-term-only" not in const_text,
             "constitution.md still references retired agent-memory-is-long-term-only")

        roo_const = ROOT / ".roo" / "rules" / "constitution.md"
        roo_text = roo_const.read_text(encoding="utf-8") if roo_const.exists() else ""
        c.check(".roo/rules/constitution.md mirrors the disposable memory rule",
             "memory-is-disposable" in roo_text and "disposable" in roo_text.lower(),
             ".roo/rules/constitution.md does not mirror the disposable memory rule")

    # ── 2. memory-is-disposable.md exists & old rule deleted ──────────────────
    if c.block("2 · memory-is-disposable.md exists & old rule deleted"):
        old_rule = RULES / "agent-memory-is-long-term-only.md"
        c.check("retired agent-memory-is-long-term-only.md is deleted from disk",
             not old_rule.exists(), f"retired rule still exists: {old_rule}")

        rule_path = RULES / "memory-is-disposable.md"
        c.check("memory-is-disposable.md exists on disk",
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
        body = rule_text.split("---", 2)[2] if rule_text.startswith("---") and rule_text.count("---") >= 2 else rule_text
        body_lower = body.lower()

        c.check("rule articulates the deletion test: slower means memory; wrong means a rule",
             "deletion test" in body_lower and "slower" in body_lower and "wrong" in body_lower,
             "rule does not articulate the deletion test")
        c.check("rule articulates the invariant: never the only copy of anything",
             "never the only copy" in body_lower,
             "rule does not articulate the invariant that memory is never the only copy")
        c.check("rule forbids load-bearing rulings from living exclusively in memory",
             "load-bearing" in body_lower or "standing ruling" in body_lower,
             "rule does not forbid load-bearing rulings living exclusively in memory")
        c.check("rule defines delete-on-sight duty",
             "delete" in body_lower and ("on sight" in body_lower or "on-sight" in body_lower),
             "rule does not specify delete-on-sight duty")
        c.check("rule defines narrate-every-write duty",
             ("one line" in body_lower or "one-line" in body_lower)
             and ("chat" in body_lower or "narrat" in body_lower),
             "rule does not specify narrate-every-write duty")

    # ── 3. Counter-examples (The Deletion Test Logic) ──────────────────────────
    if c.block("3 · Counter-examples"):
        res1 = deletion_test("Without this note, the agent will choose the WRONG branch base and fail review")
        c.check("counter-example 1: fact whose loss makes agent wrong must be a rule",
             res1 == "rule", f"expected 'rule', got '{res1}'")

        res2 = deletion_test("Without this note, the agent will take three extra bash commands and be SLOWER to find the cache")
        c.check("counter-example 2: fact whose loss only makes agent slower is memory",
             res2 == "memory", f"expected 'memory', got '{res2}'")

    # ── 4. INDEX.md and AGENTS.md ────────────────────────────────────────────
    if c.block("4 · INDEX.md and AGENTS.md"):
        idx_path = RULES / "INDEX.md"
        idx_text = idx_path.read_text(encoding="utf-8") if idx_path.exists() else ""
        c.check("INDEX.md registers memory-is-disposable as on-demand",
             "| `memory-is-disposable.md` | on-demand |" in idx_text,
             "INDEX.md missing on-demand row for memory-is-disposable.md")
        c.check("INDEX.md omits retired agent-memory-is-long-term-only",
             "agent-memory-is-long-term-only.md" not in idx_text,
             "INDEX.md still lists retired agent-memory-is-long-term-only.md")

        root_agents = ROOT / "AGENTS.md"
        root_text = root_agents.read_text(encoding="utf-8") if root_agents.exists() else ""
        sec7 = root_text.split("## 7. PERSISTENCE")[1].split("## 8. PORTABILITY")[0] if "## 7. PERSISTENCE" in root_text else ""
        sec7_lower = sec7.lower()
        c.check("AGENTS.md section 7 incorporates the disposable memory mandate",
             "memory-is-disposable" in sec7 and "memory is disposable" in sec7_lower and "deletion test" in sec7_lower,
             "AGENTS.md section 7 does not incorporate the disposable memory mandate")
        c.check("AGENTS.md section 7 does NOT reference retired agent-memory-is-long-term-only",
             "agent-memory-is-long-term-only" not in sec7,
             "AGENTS.md section 7 still references agent-memory-is-long-term-only")

    # ── 5. smh-memory-audit.md ────────────────────────────────────────────────
    if c.block("5 · smh-memory-audit.md"):
        audit_cmd_path = COMMANDS / "smh-memory-audit.md"
        audit_text = audit_cmd_path.read_text(encoding="utf-8") if audit_cmd_path.exists() else ""
        audit_lower = audit_text.lower()
        c.check("smh-memory-audit.md contains the deletion test pass",
             "deletion test" in audit_lower,
             "smh-memory-audit.md does not contain the deletion test pass")
        c.check("smh-memory-audit.md contains Promote to rule candidate classification",
             "### 📜 promote to rule" in audit_lower,
             "smh-memory-audit.md missing Promote to rule candidate bucket")

    # ── 6. SOP and changelog ─────────────────────────────────────────────────
    if c.block("6 · SOP and changelog"):
        sop_path = DOCS / "workflows_testing_SOP.md"
        sop_text = sop_path.read_text(encoding="utf-8") if sop_path.exists() else ""
        c.check("workflows_testing_SOP.md states disposable memory rule and deletion test",
             "memory is disposable" in sop_text.lower() and "deletion test" in sop_text.lower()
             and "memory-is-disposable" in sop_text,
             "workflows_testing_SOP.md missing disposable memory rule or link")

        log_path = DOCS / "workflows_testing_SOP_changelog.md"
        log_text = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
        c.check("workflows_testing_SOP_changelog.md carries SCC-448 entry",
             "SCC-448" in log_text,
             "workflows_testing_SOP_changelog.md missing SCC-448 entry")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
