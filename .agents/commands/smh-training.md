---
description: Turn the teaching voice on or off, or report its current state; the real system is unchanged.
---

# /smh-training — control teaching mode

Argument (`$ARGUMENTS`): exactly one of `on`, `off`, or `status`.

Training mode is a committed `.training-mode` sentinel at the command-center root. It changes how the
agent explains the system; it does not unlock, disable, or replace any development command or gate.

## Procedure

1. Resolve the command-center root with `git rev-parse --show-toplevel`. Refuse to act inside a child
   project if that root does not contain `docs/_scc_sops_prds/workflows_testing_SOP.md`.
2. Normalize `$ARGUMENTS` to lowercase and trim whitespace. Any value outside `on|off|status` prints
   `Usage: /smh-training on|off|status` and changes nothing.
3. Execute the selected action:
   - **`status`** — report ON when `.training-mode` exists, otherwise OFF. Change nothing.
   - **`on`** — create `.training-mode` from
     `.agents/scripts/teaching-edition/replacements/training-mode-sentinel` when absent. If it already
     exists, report that training is already on. Explain that the rule fully loads in a new session.
   - **`off`** — delete only `.training-mode` when present. If absent, report that training is already
     off. Drop the teaching voice immediately when the operator requests it, and explain that the
     conditional rule fully unloads in a new session.
4. Report the resulting state and the inverse command. Never touch workflow files, project files, or
   the approved-plan gate.

Deleting or restoring the sentinel by hand is equivalent. Nothing in the command center depends on
training mode being on.
