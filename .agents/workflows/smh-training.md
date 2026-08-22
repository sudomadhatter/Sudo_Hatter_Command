---
description: Turn the teaching voice on or off, or report its current state; the real system is unchanged.
---

# /smh-training — control teaching mode

Argument (`$ARGUMENTS`): exactly one of `on`, `off`, or `status`.

Training mode ships on through the committed `.training-mode` sentinel at the command-center root.
The ignored local `.training-mode-off` marker overrides it without dirtying the checkout. Training
changes how the agent explains the system; it does not unlock, disable, or replace any command or gate.

## Procedure

1. Walk upward from the current directory and use the first parent containing
   `docs/_scc_sops_prds/workflows_testing_SOP.md`. This works from the lobby, from a child project, and
   from a downloaded archive nested in another Git checkout. Refuse only when no such parent exists;
   when Git is available, use `git -C <resolved-root> rev-parse --show-toplevel` only to report whether
   the command center is a real clone or an archive.
2. Normalize `$ARGUMENTS` to lowercase and trim whitespace. Any value outside `on|off|status` prints
   `Usage: /smh-training on|off|status` and changes nothing.
3. Execute the selected action:
   - **`status`** — report OFF when `.training-mode-off` exists. Otherwise report ON when the committed
     `.training-mode` exists; if both are missing, report unavailable and name the missing sentinel.
   - **`on`** — delete only `.training-mode-off` when present. If `.training-mode` was removed by hand,
     recreate it at the resolved root with this exact content (the source export machinery is
     deliberately absent from a teaching shell):

     ```text
     # This file being here turns TRAINING MODE on.
     # Agents load .agents/rules/training-mode.md and teach the live workflow as they use it.
     # Turn it off with /smh-training off. Nothing is gated behind training mode.
     ```

     If the sentinel exists and the override is absent, report that training is already on. Explain
     that the rule fully loads in a new session.
   - **`off`** — create `.training-mode-off` with one line, `training disabled locally`, unless it
     already exists. Never delete or edit the committed `.training-mode`. Drop the teaching voice
     immediately and explain that the conditional rule fully unloads in a new session.
4. Report the resulting state and the inverse command. Never touch workflow files, project files, or
   the approved-plan gate.

Deleting `.training-mode-off` by hand is equivalent to `/smh-training on`. Nothing in the command
center depends on training mode being on, and `on`/`off` leaves tracked files unchanged.
