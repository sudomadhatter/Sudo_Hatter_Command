---
name: sop-currency
description: Activates when you change how the command center is USED — a `/` command, a rule, a safety-net script, a commit gate, or the front door. The SOP quick-reference (`_my_resources/_quick_reference/sudo_workflows_testing.md`) is the PRD for the operating system and must move in the same commit. An armed commit-msg gate enforces it; `[sop-ok]` is the logged opt-out.
---

# SOP currency — the quick-reference is not documentation, it is the spec

`_my_resources/_quick_reference/sudo_workflows_testing.md` is the **PRD for how this system is
operated**. It is the only page that answers *what do I type*, and the only one an operator reads
start to finish. Everything else — `.agents/rules/`, `.agents/commands/`, `AGENTS.md` — describes the
system to an **agent**. This one describes it to the **human**, and it is the surface where a stale
line does real damage: an instruction that fails in the operator's hands, months after the change
that broke it, with no way to tell whether the doc or the system is wrong.

**The law:** if you change how the command center is used, you update that page **in the same
commit**. Not "in a follow-up," not "at close-out." The same commit, because the context that makes
the edit correct exists only while you are making the change.

## What counts as a usage change

| Surface | Why it counts |
|---|---|
| `.agents/commands/*.md` | The `/` menu. **Adding, renaming, or retiring a command is always a usage change** — §3 of the doc IS this menu. |
| `.agents/rules/*.md` | The law the commands cite. Change what a gate permits and you change what the operator can do. |
| `.agents/scripts/*.py` · `*.ps1` | The safety net. §5 names these one by one and states what each refuses to allow. |
| `.agents/scripts/git-hooks/` · `.githooks/` | The gates that reject a commit. Arming, disarming, or re-scoping one changes the daily experience directly. |
| `AGENTS.md` (root) | The front door — the always-load contract every session begins with. |

**Not a usage change:** `INDEX.md` inventory churn, `reference/`, `templates/`, `skills/`,
`workflows/` (mirrors of commands), `_artifacts/` history, and the gate's own tests. That exclusion
list is deliberate and should stay narrow at both ends — a gate that fires on mechanical churn
trains the operator to reach for the opt-out reflexively, and then it is checking nothing.

## The gate

An armed **commit-msg** hook (`.agents/scripts/git-hooks/sop-currency.sh` → `sop_currency.py`)
rejects a commit that touches a usage surface without staging the SOP doc.

- **Opt out:** put `[sop-ok]` in the commit message. Use it for typos, comments, and internal
  refactors that genuinely change nothing about usage. It is logged in git forever, which is the
  design — a silent bypass teaches nothing, a recorded one is auditable.
- **Disarm:** delete `.agents/scripts/git-hooks/SOP-ENFORCE` → warn-only.
- **Lobby only:** the gate no-ops in any repo without the doc. A project clone has no SOP page to
  keep current.
- It checks **co-occurrence, not content.** No check can know whether the edit was the *right*
  edit. What it guarantees is that the author looked, in the one moment they still had the context.

## Writing the update

Match the page's voice: it explains every term the first time it appears and assumes no git
plumbing. Three habits keep it honest:

1. **State the consequence before the mechanism.** The operator needs to know what changes for
   them, then how.
2. **Retire, don't accrete.** A deleted command comes OUT of §3 — it does not get a "(retired)"
   note that quietly doubles the page every year.
3. **Every command you print must run on this machine.** The page said `python .agents/scripts/
   tests/run_all.py — 94 checks` when `python` does not exist here (only `python3`) and the count
   was 98. Both halves wrong, in the single place the doc hands you something to type. Paste the
   command into a shell before you write it down.

## The sibling rules

- [`living-template-sync.md`](living-template-sync.md) — change the **front door or folder layout**,
  mirror it into the `sudo-project-skeleton` clone source. Same shape, different target: that rule
  keeps *new projects* from being born stale, this one keeps *the operator's manual* from going stale.
- [`project-law.md`](project-law.md) — which tier a rule or skill belongs to. This page describes the
  centralized system that rule defines; a change to the tier model is always a usage change.

## Known drift (open)

`Projects/AGY_AVIATIONCHAT/_my_resources/_quick_reference/sudo_workflows_testing.md` is a
second copy. By design only its header block, §11 ordering, and link paths differ — the body is
meant to be identical. It is **currently behind** the lobby copy, and its header still calls that
project's `.agents/` "a synced copy — edit the master in the lobby," which the 2026-08-07
centralization made false (a project's `.agents/` is now its OWN tier-2 law). The gate does not
reach across repos. Re-sync the body on the operator's word, or collapse to one copy and have the
project point at the center — the same call the toolkit already made for `docs/workspace-standard.md`.
