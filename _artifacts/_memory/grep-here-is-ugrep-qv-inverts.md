---
name: grep-here-is-ugrep-qv-inverts
description: "`grep` on the Ubuntu side of this PC is ugrep 7.8.4, not GNU grep. `grep -qv PATTERN` is INVERTED there — exit 1 when lines ARE selected, exit 0 on empty input — so a gate written with `-qv` passes the illegal case and stops the legal one. Use a count (`grep -vc`), never `-q` with `-v`, in anything that ships. Re-measured on this box 2026-09-04."
metadata:
  node_type: memory
  type: reference
  probe: "! printf 'a\\n' | grep -qv a"
  modified: 2026-09-04
---

`grep --version` here reports **ugrep 7.8.4**, not GNU grep. It shadows the system grep on `PATH`,
so every `grep` in a gate, hook or command fence runs ugrep on the Ubuntu side and something else on
the Windows side ([[one-pc-windows-and-wsl]]).

> ⛔ **This file used to be called `grep-here-is-ugrep-qv-inverts`.** That name was wrong twice over:
> there is no Mac ([[one-pc-windows-and-wsl]]), and the trap is **live on the box Mr. Hatter
> actually works on**. A memory whose title names the wrong machine is worse than no memory — an
> agent reads "on the Mac", concludes it does not apply here, and writes the broken gate anyway.
> Re-measured 2026-09-04 on WSL Ubuntu: ugrep 7.8.4, inversion reproduces exactly.

**The measured difference:** `grep -qv PATTERN` (any flag order — `-qv`, `-q -v`, `-v -q`) exits
**1 when lines ARE selected** and **0 on empty input**. That is inverted from GNU and BSD grep.
Plain `grep -v` prints the selected lines correctly; only the `-q` combination inverts.

    printf 'alpha\nbeta\n' | grep -qv alpha   # -> exit 1  (lines WERE selected)
    printf ''             | grep -qv alpha   # -> exit 0  (nothing selected)

Caught 2026-09-01 writing the SCC-359 approval-sha check in `/smh-quick-dev` Step 1.5: the `-qv`
form **passed the illegal case and stopped the legal one** — a gate that cannot fail, inside the
gate written to catch that class of mistake. Three review lenses had just flagged the previous
prose-only version; the replacement was worse until it was run.

**Use a count, never `-q` with `-v`, in anything that ships:**

```bash
BAD=$(… | grep -vc 'pattern')      # 0 on empty input, N when N lines are selected, everywhere
[ "$BAD" -eq 0 ] && echo OK || echo STOP
```

The probe on this file IS the falsifier: it asserts the inversion is still there. If a future
`grep` install fixes it, this memory goes red and gets rewritten rather than quietly misleading
someone. Related: [[suite-red-file-may-have-run-nothing]] — the same family of false green.
