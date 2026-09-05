---
name: zsh-does-not-word-split-gate-args
description: "The false-GREEN family: a gate RAN, printed nothing alarming and exited 0 about a question it was never actually asked. Worked example — in zsh `--paths $VAR` passes ONE argument, not many, so the gate matched nothing and passed. ALWAYS run a positive control before believing a green. Recorded on the retired Mac 2026-08-13; the lesson is shell-independent."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2855f5d7-72ec-49bb-832c-b15be7fea258
  modified: 2026-08-13T01:31:20.958Z
---

Running a gate as `python3 sop_currency.py --paths $PATHS` returned **exit 0** on a change set it
should have rejected. zsh (unlike bash) does **not** word-split unquoted variables, so argparse
received a *single* argument holding 11 space-joined paths. It matched no surface prefix, found
nothing to complain about, and passed. Re-run with `${=PATHS}` (forced split) or
`$(git diff --name-only)` (command substitution **does** split) and the same gate correctly
exits **1**.

**Why:** this is a false GREEN, the most expensive kind. The gate ran, printed nothing alarming,
and exited clean — there is no error to notice. Same family as [[piping-a-gate-hides-its-exit-code]]:
the mechanism reports success about a question it was never actually asked. Both were hit in the
same session, on the same repo, minutes apart.

**How to apply:** when a gate passes, prove it can fail — run a **positive control** (feed it one
path you know is a violation and confirm non-zero) before believing the green. Echo the argument
count (`$#` after `set --`) or the path count when passing a list. Two related zsh/bash traps that
bit in the same run: `${PIPESTATUS[0]}` is a **bash-ism** — zsh spells it `$pipestatus[1]`, so it
silently expands to empty and prints no exit code at all (run gates bare instead); and `grep -E`
treats `\|` as a **literal pipe**, not alternation, so `grep -cE 'A\|B'` reported 0 hits for three
strings that were present 7, 4 and 12 times, nearly causing duplicate content to be folded into a
command. Measured on the Mac that was retired 2026-09-02 ([[one-pc-windows-and-wsl]]); this PC's Ubuntu side runs bash, which DOES word-split, so the specific zsh trap cannot fire here. **The lesson still can** — [[agent-shell-grep-is-not-the-gate-grep]] is the same false-green on the current box, and it is live.
