---
name: one-pc-windows-and-wsl
description: "There is ONE PC — Windows, with Ubuntu inside WSL2 — not two machines and not a Mac. The Windows side runs PowerShell, `python`, the Antigravity IDE and the credential store; the Ubuntu side runs bash, `python3`, Claude Code, Codex, opencode and the Antigravity CLI. Three checkouts of this repo exist on it; only the Ubuntu `Ubuntu` one is live. Every fact here carries the command that proves it. Measured 2026-09-04 (SCC-400), replacing the false two-machines claim of 2026-08-08."
metadata:
  node_type: memory
  type: project
  probe: 'grep -q microsoft-standard-WSL2 /proc/version'
  probe: 'test -x /usr/bin/pwsh'
  probe: 'test -x /usr/bin/python3 && test ! -e /usr/bin/python'
  probe: 'ls ~/.gemini/bin/agy && test ! -d ~/.gemini/antigravity-ide'
  probe: 'test -d /mnt/c/Sudo_Hatter_Command'
  modified: 2026-09-04
---

**One PC.** Windows is the host; Ubuntu runs inside WSL2 on it. There is no Mac and there never
was one on this system — the claim written 2026-08-08 ("driven from TWO machines, this Mac AND a
Windows PC") went false when SCC-376 moved the working environment into WSL2 on 2026-09-02, and it
stayed loaded and trusted until an agent used it on 2026-09-04 to make four wrong statements to
Mr. Hatter in one afternoon. This file replaces it. Superseded: `two-machines-mac-and-pc`.

    grep -q microsoft-standard-WSL2 /proc/version   # kernel 5.15.167.4-microsoft-standard-WSL2

## The two sides — one box, two environments

| | Windows side | Ubuntu side (WSL2, distro `Ubuntu`) |
|---|---|---|
| Native shell | PowerShell | bash (`pwsh` is installed here too, at `/usr/bin/pwsh` — that is how `sync-agents.ps1` runs) |
| Python | `python` | `python3` (no bare `python`) |
| Antigravity | the **IDE** — `C:\Users\dlohn\.gemini\antigravity-ide\` | the **CLI** — `~/.gemini/bin/agy`, store `~/.gemini/antigravity/` |
| Agents | — | Claude Code, Codex, opencode |
| Credentials | the Windows credential store | `JIRA_API_TOKEN` read from `~/.profile` — so `jira_ticket.py` needs a **login** shell (`bash -lc`) |
| Paths | `\`, `robocopy`, `USERPROFILE` | POSIX `/` ([[windows-authored-code-hides-posix-bugs]]) |

`python` vs `python3` is still a real difference and still costs cycles — but for **this** reason,
two environments on one box, not two machines. Never delete that distinction while sweeping.

    test -x /usr/bin/pwsh                                        # pwsh IS on the Ubuntu side
    test -x /usr/bin/python3 && test ! -e /usr/bin/python        # python3 here, no bare python
    ls ~/.gemini/bin/agy && test ! -d ~/.gemini/antigravity-ide  # CLI here, IDE is not

**Each of those is a `probe:` on this file, not just a line to read.** Five facts, five falsifiers:
the kernel, `/usr/bin/pwsh`, the `python`/`python3` asymmetry, the Antigravity CLI-not-IDE split,
and the Windows checkout below. The suite runs all five and names the one that fails.

## Three checkouts of this repo — only one is live

| Where | Distro / host | State on 2026-09-04 |
|---|---|---|
| `/home/dlohn/Sudo_Hatter_Command` | WSL `Ubuntu` | **the live working tree** — every lane, every worktree |
| `/home/dlohn/Sudo_Hatter_Command` | WSL `Ubuntu-zoo2` | its own clone, HEAD `23c9f911`, far behind. **Confirmed present** — this was an open question |
| `C:\Sudo_Hatter_Command` | Windows-native | HEAD `ab68505e`, far behind, ~3,850 dirty rows |

**Never call a non-`Ubuntu` checkout "the live side."** An agent did on 2026-09-04, and told
Mr. Hatter a repo he had refreshed minutes earlier was unchanged.

    test -d /mnt/c/Sudo_Hatter_Command   # the Windows checkout exists (do not work in it)

The behind-counts are **deliberately not probed** — they move every time `main` does, so a probe
asserting one would go red on the next merge and teach everyone to ignore probes.

### Why the Windows clone is kept — measured, not guessed

Because the **Antigravity IDE is a Windows application, and a Windows application opens Windows
paths.** Its transcripts name `c:/Sudo_Hatter_Command` 106 times and no WSL path even once:

    grep -rhoi 'c:/Sudo_Hatter_Command' /mnt/c/Users/dlohn/.gemini/antigravity-ide/ | wc -l

That is the whole reason. It is not an abandoned copy and not a mistake — deleting it would take
the IDE's workspace with it. What it is *not* is a place work happens: it is far behind `main` and
holds no commits of its own.

Its ~3,850 dirty rows are **line-ending flips only** — `git ls-files --eol` reports `i/lf w/crlf`
with no attr, and `git diff --ignore-cr-at-eol` returns empty. `core.autocrlf` is set in neither
`/mnt/c/Users/dlohn/.gitconfig` nor the repo config, so the conversion comes from the Windows Git
install's own default. **Nothing is lost there and nothing needs rescuing.**

## Caches are per-side — a purge cleans only the side that ran it

Antigravity's door is `.agents/skills/`; the `global_workflows` cache is the **retired** surface's,
and SCC-394 purged it. That purge is the worked example of this whole section. On 2026-09-04, after
it ran on Ubuntu: the Ubuntu copy held **0** files, while the Windows copy under
`C:\Users\dlohn\.gemini\` still held **42**. The sync writes to `$UserHome` = `USERPROFILE` if
set, else `HOME` — and `USERPROFILE` is empty under WSL's pwsh, so a purge run from Ubuntu never
reaches the Windows side at all.

**How to apply:** when a sync, purge or install "did not take", ask *which side ran it* before
assuming the script is broken. Run it on both, or say in the doc which side it is for.

## How to apply

1. **Never write "Mac", "the Mac", "two machines" or "keychain" into a shared doc.** Name the
   *side* — Windows or Ubuntu — or write it side-neutral.
2. **Probe, never assume the interpreter**: `for c in python3 python py`.
3. **When something is "broken", ask which side wrote it**, exactly as before — the two sides are
   real; the two machines were not.
4. `core.hooksPath` is still LOCAL config and does not travel with a clone
   ([[git-hooks-live-in-githooks-not-git-hooks]]) — arm it per checkout, and note there are three.
