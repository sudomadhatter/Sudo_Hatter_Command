---
name: dependency-awareness
description: "Activates when modifying package.json, requirements.txt, pyproject.toml, or any dependency manifest. Prevents silent dependency drift."
trigger: glob
globs: ["**/package.json", "**/requirements*.txt", "**/pyproject.toml", "**/poetry.lock", "**/package-lock.json"]
paths:
  - "**/package.json"
  - "**/requirements*.txt"
  - "**/pyproject.toml"
  - "**/poetry.lock"
  - "**/package-lock.json"
# Path-scoped. `globs:` is Antigravity's field; `paths:` is Claude Code's, and Claude
# loads this file ONLY when it reads a file matching one of them. Both lists are the
# same set on purpose — one classification, two readers (test_rule_frontmatter.py).

---

# Dependency Changes — Proceed with Caution

1. **Check existing first** — never add a new dependency if an existing one covers the need
2. **Read the changelog** — never upgrade without checking for breaking changes
3. **Pin versions** — use exact versions (`==` in Python, no `^` or `~` in Node)
4. **Test after** — run full test suite after any dependency change
5. **Flag risks** — notify user of security implications or large transitive dependency trees
6. **Backend** — add to `requirements.txt`, verify `.venv` activated
7. **Frontend** — `npm install --save-exact`, verify `package-lock.json` updated
