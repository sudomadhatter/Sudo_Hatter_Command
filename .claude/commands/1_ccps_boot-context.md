---
description: Session boot — reads active-context, identifies in-scope component specs, confirms sprint state before work begins
---

# /1_ccps_boot-context — Session Boot (G1)

Execute the workflow defined in @.agent/workflows/1_ccps_boot-context.md.

**opencode execution notes:**
- The workflow uses `// turbo` and `// turbo-all` directives (Antigravity auto-approve markers). In opencode these are just comments — execute the steps using your normal tool permissions.
- Paths are relative to the project root: `_bmad-output/active-context/active-context.md`, `_bmad-output/component-specs/`.
- Per @AGENTS.md, output a concise `<context>` block summarizing Sprint Objective, Stable, Broken, In Play, Pitfalls.
- After completion, do NOT start coding — wait for the user's next instruction. This is a discovery step.

Optional additional input: $ARGUMENTS
