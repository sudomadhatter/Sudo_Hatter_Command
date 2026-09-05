---
name: agent-shell-grep-is-not-the-gate-grep
description: "`grep` inside a Claude Code Bash tool is a shell FUNCTION Claude Code injects (it execs the claude binary as `ugrep`, with `--ignore-files --hidden --exclude-dir=.git`). It is not installed on this box and not on PATH. Every other context — a git hook, run_all.py, `bash -c`, `bash -lc`, PowerShell, another agent — gets GNU grep 3.11 at /usr/bin/grep, with different flag semantics AND different default file selection. So a grep you measured in chat is NOT the grep your committed gate will run. Measured 2026-09-04 (SCC-401)."
metadata:
  node_type: memory
  type: reference
  probe: 'test "$(command -v grep)" = /usr/bin/grep'
  modified: 2026-09-04
---

**The trap, in one line:** you measure a `grep` by hand, it behaves one way, you commit that exact
line into a gate — and the gate runs a **different program**.

## What is actually here — measured, not assumed

```
$ type grep                       # inside a Claude Code Bash tool
grep is a function
grep () { … exec -a ugrep "$_cc_bin" -G --ignore-files --hidden -I --exclude-dir=.git … }

$ grep --version | head -1        # same shell
ugrep 7.8.4 x86_64-pc-linux-gnu

$ bash -c 'command -v grep; grep --version | head -1'
/usr/bin/grep
grep (GNU grep) 3.11

$ bash -lc 'grep --version | head -1'      # a LOGIN shell does not change it either
grep (GNU grep) 3.11
```

`ugrep` is **not installed**. It is Claude Code's own binary re-execed under the name `ugrep`, wired
in as a bash function for the duration of the tool call. Nothing outside that function sees it: not
`/usr/bin/grep`, not a hook, not `subprocess.run(["bash","-c",...])`, not the Windows side.

## Why that costs a gate

The wrapper does not only differ on flag semantics — it is invoked with
`--ignore-files --hidden -I --exclude-dir=.git`. So the same command, same cwd, returns a
**different file set** in chat than in a gate: honouring `.gitignore`, including dotfiles, skipping
binaries. A count you verified interactively can be wrong in CI for reasons that have nothing to do
with your pattern.

> ⛔ **This file has now been wrong twice, and both times the NAME carried the error.** It was
> `grep-on-the-mac-is-ugrep` (there is no Mac — [[one-pc-windows-and-wsl]]), then
> `grep-here-is-ugrep-qv-inverts` ("here" meant the box, which is false: it means *this shell*).
> The SCC-318 incident behind it was real — a shipped `grep -qv` gate passed the illegal case — but
> the attribution was wrong, and a wrong attribution sends the next agent to check the wrong thing.

## The rule that survives all of it

**Never `-q` with `-v` in anything that ships.** Count instead — one meaning on every grep, in every
shell, on both sides:

```bash
BAD=$(… | grep -vc 'pattern')      # 0 on empty input, N when N lines are selected
[ "$BAD" -eq 0 ] && echo OK || echo STOP
```

And more generally: **measure a gate the way the gate will run it** — `bash -c '…'`, or by running
the gate itself. Same family as [[interactive-startup-files-are-invisible-to-automation]] (the
environment you test in is not the environment that runs) and
[[suite-red-file-may-have-run-nothing]] (a result that cannot mean what it says).

The probe asserts the thing that would make this file wrong again: that the `grep` an automated
shell resolves is still `/usr/bin/grep`. Install a real ugrep on `PATH` and it goes red.
