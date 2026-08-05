---
description: Turn the tutor lane on or off. Training mode teaches the system as you use it — explain before executing, define every term, never invent a command.
---

# /training — tutor lane on/off

Argument (`$ARGUMENTS`): `on` · `off` · `status` (default: `status`).

The toggle is a single file, **`.training-mode`** at the repo root. Present = on. The rule that reads
it is `.agents/rules/training-mode.md`, which owns the trigger; `AGENTS.md` §3 only points at it.

## `status`

```
Test-Path .training-mode
```

Report plainly: **on** or **off**, and one line on what that means right now.

## `on`

```
New-Item -ItemType File .training-mode -Force | Out-Null
```

Then say: training mode is on, and it takes full effect **next session** because rules load at session
start. Offer to start behaving that way immediately anyway — the file is the durable switch, the voice
can change now.

## `off`

```
Remove-Item .training-mode -ErrorAction SilentlyContinue
```

Then say the same thing in reverse — and mean it:

> Dropping the tutor voice now; the rule fully unloads next session.

**Do not treat this as a graduation.** No congratulations, no "are you sure", no re-offering it later.
They own the switch, it is reversible with `/training on`, and nothing in the system is gated behind
it — what remains is the real system, not a crippled one.

## Notes

- Deleting or creating `.training-mode` by hand is exactly equivalent. This command is a convenience,
  not the mechanism.
- The file is committed in the teaching repos, so a fresh clone starts **on**. That is deliberate: an
  environment variable would not survive a clone, and the newcomer would land with no tutor at all.
- If someone asks for training mode in a repo that has no `training-mode.md` rule, say so rather than
  creating the file — an empty toggle that switches nothing is worse than no toggle.
