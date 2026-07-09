---
name: lobby-search
description: "Lobby-only search gotcha: from the home-base root, Grep AND Glob are blind to Projects/ (ripgrep-based tools honor the lobby .gitignore, which ignores Projects/). Mechanics + the correct search patterns. Load when searching the tree from the lobby."
---

# Searching the tree from the LOBBY (Grep/Glob are blind to `Projects/`)

**The trap.** `Projects/` is **gitignored** at the lobby (each project is its own nested git repo). The
Grep tool runs ripgrep, which honors `.gitignore` — so a Grep whose `path` is the lobby root (or unset)
**silently skips everything under `Projects/`** and returns zero hits from the project repos. It reads as
a false "clean." A grep that finds a master file in `.agents/` is **not** proof it's the only copy: that
same file is **vendored** into each `Projects/<name>/.agents/`, and a root-level Grep can't see those.

**The fix is to go one level down.** Point the Grep tool's `path` *directly at a project repo*
(`Projects/<name>/` or deeper) — that directory is its **own git repo root**, so ripgrep starts a fresh
ignore context there and never applies the lobby's parent `.gitignore`.

- **Single project** → the Grep tool with `path: Projects/<name>` (fast, indexed).
- **One sweep across ALL projects at once** → use the **Bash tool** (`find Projects -name '<file>'`, then
  `grep`/`diff` each hit; confirm with `git check-ignore <path>`) — a single root-level Grep is blind and
  you'd otherwise have to loop Grep per project.
- **Glob caveat (observed in practice):** the Glob tool can false-negative under `Projects/` **even with
  an in-project `path`** (lobby `.gitignore` bleed). When Glob returns nothing inside `Projects/`, verify
  with Bash `find` before concluding the files don't exist. (Grep-inside-project is reliable; Glob isn't.)

Canonical fix path is unchanged: edit the master `.agents/`, then `/sync-agents <project>` to re-vendor.

*(This rule is lobby-specific — inside a project you're past the ignore boundary, so don't carry it into
a project's `AGENTS.md`.)*
