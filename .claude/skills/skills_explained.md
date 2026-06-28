---
name: Skills Guide
description: A research guide and outline on how to use, create, and manage Agent Skills.
---

# 🧠 User Guide: Agent Skills

## What are Skills?
Skills are **markdown files** that teach your AI agent how to perform specific, often complex, tasks. Think of them as "knowledge cartridges" or "playbooks". When you have a skill for a topic (e.g., `react-patterns.md`), the agent can read it to instantly become an expert in that domain, following the exact best practices and steps you've defined.

## 📂 Where do they live?
All skills reside in your `.agents/skills/` directory.
- **Path**: `.agents/skills/` (relative to the workspace root)
- **Extension**: `.md` (Markdown)

## 🛠️ How to Use a Skill
There are two main ways to use a skill:

1.  **Explicit Mention**: You can specifically ask the agent to use a skill.
    > "Use the @react-patterns skill to review this component."
    > "Please write this email using the @marketing-copywriter skill."

2.  **Implicit Detection**: If a skill is well-defined, the agent may check it automatically when the task is relevant, but explicit mentions are most reliable for specific workflows.

## 📝 How to Create a Skill
To create a new skill, simply make a new Markdown file in the `.agent/skills` folder.

**Format:**
Every skill file should ideally start with YAML frontmatter (metadata) followed by clear instructions.

```markdown
---
name: unique-skill-name
description: A short description of what this skill does.
---

# Skill Description
A detailed explanation of the task.

## Rules
1. Always do X.
2. Never do Y.

## Steps
1. Step one...
2. Step two...
```

## 🧹 Managing Your Skills
- **Organize**: You can group skills into subfolders.
- **Delete**: If a skill is no longer needed, simply delete the `.md` file.
- **Import**: You can download collections of skills (like the `antigravity_awesome_skills` pack) to instantly gain capabilities.

## ❓ What is `antigravity_awesome_skills`?
This folder (`.agent/skills/antigravity_awesome_skills`) is a community-curated library of over 200+ pre-written skills covering everything from **Cybersecurity** to **SEO** and **Software Architecture**.

- **Pros**: Instant access to expert knowledge.
- **Cons**: Can be overwhelming if you don't need all features.
- **Recommendation**: Browse the `skills` folder within it, move the ones you like to your main `skills` folder, and delete the rest to keep your workspace clean.
