---
name: grep-on-the-mac-is-ugrep
description: "The Mac's `grep` is ugrep in a Claude session (7.8.4, 2026-09-01) but BSD grep 2.6.0 from a terminal script (2026-09-02) — the shadow depends on launch context. ugrep's `grep -qv` returns the INVERTED exit code. Count with `grep -vc`; never `-q`."
metadata: 
  node_type: memory
  type: reference
  originSessionId: b96e3a56-55ff-4082-9cc0-aff4e62375a3
  modified: 2026-09-02T18:29:47.487Z
---

`grep --version` on the Mac reports **ugrep 7.8.4**, not BSD grep. It shadows the system grep on
`PATH`, so every `grep` in a gate, hook, or command fence runs ugrep there and something else on the
PC ([[one-pc-windows-and-wsl]]).

**The measured difference:** `grep -qv PATTERN` (any flag order — `-qv`, `-q -v`, `-v -q`) exits
**1 when lines ARE selected** and **0 on empty input**. That is inverted from both GNU and BSD grep.
Plain `grep -v` prints the selected lines correctly; only the `-q` combination inverts.

Caught 2026-09-01 writing the SCC-359 approval-sha check in `/smh-quick-dev` Step 1.5: the `-qv`
form **passed the illegal case and stopped the legal one** — a gate that cannot fail, inside the
gate written to catch that class of mistake. Three review lenses had just flagged the previous
prose-only version; the replacement was worse until it was run.

**Use a count, never `-q`, in anything that ships:**

```bash
BAD=$(… | grep -vc 'pattern')      # 0 on empty input, N when N lines are selected, everywhere
[ "$BAD" -eq 0 ] && echo OK || echo STOP
```

**2026-09-02 correction (SCC-376):** `grep --version` inside `bash /tmp/mac_install.sh`, launched from
the operator's terminal, reported **BSD grep 2.6.0-FreeBSD**, not ugrep. So the shadow is not on the
base PATH; it comes from the launch context (an alias or PATH entry the Claude session had on
2026-09-01 that a plain terminal script does not). Do not assume either implementation on the Mac —
the count idiom is right on both, and only the count idiom is.

A count has one meaning on every grep implementation. Same family as
[[piping-a-gate-hides-its-exit-code]] and [[zsh-does-not-word-split-gate-args]] — the shell layer,
not the logic, is where these gates die. Related: [[mac-authored-code-hides-windows-bugs]].
