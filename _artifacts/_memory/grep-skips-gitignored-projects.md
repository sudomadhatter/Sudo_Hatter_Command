---
name: grep-skips-gitignored-projects
description: "The Grep tool is blind to Projects/ ONLY from the lobby root; point its path one level down at a project repo and it works — or use Bash for an all-projects sweep."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 75f1a599-830b-46bf-acea-c89d1d70f2a8
---

In the Sudo_Hatter_Command home base, `Projects/` is gitignored (each project is its own git repo). The Grep tool runs ripgrep, which honors `.gitignore` — **but the blindness is path-dependent, not absolute.** A Grep whose `path` is the lobby root (or unset) **silently returns nothing from inside the project repos** — it looked like the master `.agents/workflows/` was the only copy of a file when AGY_AVIATIONCHAT and Fresh_Workspace_BMAD held their own vendored copies too.

**The fix (Daniel's correction, verified 2026-06-28):** go one level down. Point the Grep tool's `path` *directly at a project repo* (`Projects/<name>/` or deeper) and it works fine — that directory is its **own git repo root**, so ripgrep starts a fresh ignore context and never applies the lobby's parent `.gitignore`. Confirmed both ways: same pattern → 0 project hits from the root, 17 hits with `path: Projects/AGY_AVIATIONCHAT`.

**Why:** a *root-level* grep-based "it only exists in one place" conclusion is unreliable here and led to a wrong answer Daniel had to correct. The earlier "never use Grep, always Bash" rule was over-broad — Grep is fine, you just have to scope it past the ignore boundary.

**How to apply:**
- **Single project** → use the Grep tool with `path: Projects/<name>` (fast, indexed).
- **One sweep across ALL projects at once** → use the Bash tool (`find Projects -name '...'` + `grep`/`diff`; `git check-ignore <path>` to confirm), because a single root Grep is blind and you'd otherwise loop Grep per project.
- Canonical fix path unchanged: edit master `.agents/` then `/sync-agents <project>` to re-vendor.

See [[git-branch-model-standard]], [[sync-leaves-local-command-ghosts]].
