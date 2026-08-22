---
name: two-machines-mac-and-pc
description: "The command center is driven from TWO machines — this Mac AND a Windows PC desktop — and every shared doc is read on both. Never write a machine-specific command into a shared doc, and never assume the Mac's answer is the system's answer. Confirmed by the operator 2026-08-08 after a python3 sweep broke the PC's copy."
metadata: 
  node_type: memory
  type: project
  originSessionId: ea1c7963-b655-4c4b-861f-0b832da17b1e
  modified: 2026-08-08T06:00:51.375Z
---

`Sudo_Hatter_Command` and every project under it are worked from **both a Mac and a Windows PC
desktop**, alternating via `/sudo-park` → `/sudo-resume`. **Every `.md` in the repo is read on both
machines.** A doc that only works here is a doc that is broken half the time.

**What actually differs between them** (each of these has already cost a cycle):

| | Mac | PC |
|---|---|---|
| Python | **only `python3`** — no bare `python`, not even in a login shell | `python` (python.org); `python3` exists only on Microsoft Store installs |
| Shell | zsh — and `.zshrc` is invisible to automation ([[zshrc-is-invisible-to-automation]]) | PowerShell / Git-Bash |
| `core.hooksPath` | **LOCAL config — does NOT travel via git.** Set per clone AND per machine, so every gate is silently off on a fresh clone ([[git-hooks-live-in-githooks-not-git-hooks]]) | same |
| Global gitconfig | applied 2026-08-07 ([[gitconfig-never-migrated-to-the-mac]]) | the original |
| Paths / tooling | POSIX, `/`, no robocopy ([[windows-authored-code-hides-posix-bugs]]) | `\`, `robocopy`, `USERPROFILE` |

**Why: `core.hooksPath` is the sharp one.** It arms every commit gate (Jira, encoding, and the SOP
gate — [[sop-doc-currency-gate]]) and it is *local config*, so a repo cloned on the other machine has
**no gates at all** while looking identical. One command fixes it machine-wide, verified 2026-08-08:

    git config --global core.hooksPath .githooks

A **relative** value resolves against each repo's own root, so it arms every clone (present and
future) and is a harmless no-op in repos with no `.githooks/` dir. Set it once per machine.

**How to apply:**

1. **Never hardcode an interpreter or a shell-ism in a shared doc.** Say which name belongs to which
   machine, or write it machine-neutral. A blanket "it's `python3`, `python` is wrong" sweep is a
   Mac-only claim — that exact mistake shipped on 2026-08-08 and had to be walked back.
2. **Scripts and hooks probe, never assume**: `for c in python3 python py`. That is what makes a gate
   work on either box untouched.
3. **When something "is broken," ask which machine wrote it** before assuming the code is wrong —
   a Windows-authored assumption reads as "the Mac is broken" and vice versa.
4. **A fix belongs on both.** Platform-branch it; never convert a script to Mac-only.
