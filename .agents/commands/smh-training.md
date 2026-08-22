---
description: Turn the teaching voice on or off, or report its current state; the real system is unchanged.
---

# /smh-training — control teaching mode

Argument (`$ARGUMENTS`): exactly one of `on`, `off`, or `status`.

Training mode is a committed `.training-mode` sentinel at the command-center root. It changes how the
agent explains the system; it does not unlock, disable, or replace any development command or gate.

## Procedure

1. Resolve the command-center root with `git rev-parse --show-toplevel`. If that fails because the
   teaching shell was opened from a downloaded archive, walk upward from the current directory and use
   the first parent containing `docs/_scc_sops_prds/workflows_testing_SOP.md`. Refuse if no such parent
   exists, or if Git resolves a child project whose root lacks that SOP.
2. Normalize `$ARGUMENTS` to lowercase and trim whitespace. Any value outside `on|off|status` prints
   `Usage: /smh-training on|off|status` and changes nothing.
3. Execute the selected action:
   - **`status`** — report ON when `.training-mode` exists, otherwise OFF. Change nothing.
   - **`on`** — when absent, create `.training-mode` at the resolved root with this exact content (the
     source export machinery is deliberately absent from a teaching shell):

     ```text
     # This file being here turns TRAINING MODE on.
     # Agents load .agents/rules/training-mode.md and teach the live workflow as they use it.
     # Turn it off with /smh-training off. Nothing is gated behind training mode.
     ```

     If it already exists, report that training is already on. Explain that the rule fully loads in a
     new session.
   - **`off`** — delete only `.training-mode` when present. If absent, report that training is already
     off. Drop the teaching voice immediately when the operator requests it, and explain that the
     conditional rule fully unloads in a new session.
4. Report the resulting state and the inverse command. Never touch workflow files, project files, or
   the approved-plan gate.

Deleting or restoring the sentinel by hand is equivalent. Nothing in the command center depends on
training mode being on.
