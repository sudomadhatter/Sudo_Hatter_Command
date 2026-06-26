---
name: adk-prompting
description: "Antigravity prompt architecture guide. Use when the user asks to create or fix a rule, workflow, or skill for the .agents/ directory. Covers taxonomy routing, YAML frontmatter standards, and generation guidelines."
---

# Antigravity Prompt Architecture Guide

## When To Use This Skill
The user asks you to create or fix a rule, workflow, or skill for the `.agents/` directory.

## Control Construct Routing

Catigorize the user's issue before generating:

| Type | Location | Use For |
|---|---|---|
| **Rule** | `.agents/rules/` | Passive constraints, formatting mandates, negative boundaries |
| **Workflow** | `.agents/workflows/` | Active, sequential multi-step playbooks |
| **Skill** | `.agents/skills/` | Domain expertise, executable tools, capability extensions |

## Generation Standards

### Rules
- Write in Markdown. Focus on project-specific deviations, not general style guides.
- Define activation mode in YAML frontmatter: `Always On`, `Manual`, `Glob Pattern`, or `Model Decision`.
- Keep rules focused — one concern per file.

### Workflows
- Markdown files, max 12,000 characters.
- Structure: title → description → enumerated steps with specific instructions.
- Include Plan Mode in initial steps to generate `implementation_plan.md`.
- Mandate a human-approval pause after planning artifacts.

### Skills
- Use Progressive Disclosure to optimize context window.
- Standard structure: `SKILL.md` + optional `scripts/`, `references/`, `examples/`, `assets/`.
- YAML frontmatter description ≤1024 chars with explicit keyword triggers.
- Include clear argument mapping so the agent can extract parameters from natural language.

## Quality Check
Before delivering, confirm all user constraints, negative boundaries, and structural requirements are addressed.
