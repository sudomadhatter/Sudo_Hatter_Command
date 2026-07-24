---
name: clean-code-audit
description: 'Audit a code diff against the house standard — machine checks (ruff / eslint / pyrefly / tsc) that can FAIL, plus a judgment pass over the comment contract and AI-drift bans that caps at CONCERNS. Diff-scoped, so legacy debt never red-walls a story. Runs standalone, and is Step 3.5 of /sudo-code-review. Use when the user says "audit the code" / "is this code clean" / "clean code audit", or before closing out any story.'
---

# /clean-code-audit — the code-standards gate

Checks a diff against **`.agents/rules/code-standards.md`** — the single house definition of "clean"
(the comment contract, the AI-drift bans, style, and the machine-checkable floor).

**Execute now:** read `.agents/commands/clean-code-audit.md` (relative to the repo root) and follow it END
TO END. Its **Step 0** resolves which child project to target — a leading `$ARGUMENTS` project name, else
the `.agents/active-project.txt` pointer, else it asks Daniel. Pass `$ARGUMENTS` through verbatim; the
leading token may name the project, e.g. `AGY_AVIATIONCHAT 21.12`.

Two halves, two severities: the **machine floor** can FAIL a story; the **judgment pass** caps at
CONCERNS. Objective things block, taste does not.
