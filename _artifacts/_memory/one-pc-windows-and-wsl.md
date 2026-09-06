---
name: one-pc-windows-and-wsl
description: "TWO machines: a Mac (Darwin, Homebrew, `/Users/sudohatter`) and ONE PC — Windows with Ubuntu inside WSL2. The PC is the primary; the Mac is the second seat and goes stale between sessions. On the PC, Windows runs PowerShell, `python`, the Antigravity IDE and the credential store while Ubuntu runs bash, `python3`, Claude Code, Codex, opencode and the Antigravity CLI; three checkouts live there and only the Ubuntu `Ubuntu` one is live. Every fact here carries the command that proves it, and every probe branches per machine. Measured 2026-09-04 (SCC-400); the Mac half restored 2026-09-06 after the 09-04 rewrite over-corrected and deleted a true fact."
metadata:
  node_type: memory
  type: project
  probe: 'if [ -e /proc/version ]; then grep -q microsoft-standard-WSL2 /proc/version; else [ "$(uname)" = Darwin ]; fi'
  probe: 'if [ "$(uname)" = Darwin ]; then [ -d /opt/homebrew ]; else test -x /usr/bin/pwsh; fi'
  probe: 'if [ "$(uname)" = Darwin ]; then command -v python3 >/dev/null; else test -x /usr/bin/python3 && test ! -e /usr/bin/python; fi'
  probe: 'if [ "$(uname)" = Darwin ]; then test -d ~/.antigravity-ide; else ls ~/.gemini/bin/agy && test ! -d ~/.gemini/antigravity-ide; fi'
  probe: 'if [ "$(uname)" = Darwin ]; then test -d ~/Sudo_Hatter_Command; else test -d /mnt/c/Sudo_Hatter_Command; fi'
  modified: 2026-09-06
---

**TWO machines: a Mac, and one PC that is Windows hosting Ubuntu in WSL2.**

⚠️ **Corrected 2026-09-06.** The 2026-09-04 rewrite (SCC-400) said *"There is no Mac and there
never was one on this system."* **That is false, and it was false when written.** The 08-08 claim
it replaced was wrong about *which* environments exist on the PC; it was **right** that a Mac
exists. Killing both halves at once meant every agent booting on the Mac — where this is the
first-listed `⛔ Read first` memory — was told its own machine did not exist. Restore the Mac half;
keep the PC half exactly as SCC-400 measured it. Superseded: `two-machines-mac-and-pc`.

Which machine am I on? One command, and every probe on this file branches on it:

    uname            # Darwin -> the Mac. Linux -> the PC's Ubuntu side.

| | The Mac | The PC (Windows + WSL2 Ubuntu) |
|---|---|---|
| Role | **second seat** — goes stale between sessions; sync it first | **primary** — a week of work can land here while the Mac sits idle |
| Home | `/Users/sudohatter` | `C:\Users\dlohn` · `/home/dlohn` |
| Checkout | `~/Sudo_Hatter_Command` | three of them — see below |
| Toolchain | Homebrew `/opt/homebrew`, `python3`, `gcloud` **authenticated** | `python` (Windows) · `python3` (Ubuntu); `gcloud` **not** authenticated |
| Antigravity | IDE at `~/.antigravity-ide`, store `~/.gemini/config/config.json` | IDE on Windows, CLI `~/.gemini/bin/agy` on Ubuntu |

**Some work can only be done on one of them, and that is the point of keeping both.** The Firestore
TTL question that sat open on AVCH-105 was answered on the Mac on 2026-09-06 purely because
`gcloud auth` is live there and not on the PC. Read a machine-shaped blocker as *"do it on the other
seat"*, never as *"cannot be done."*

    grep -q microsoft-standard-WSL2 /proc/version   # PC only: kernel 5.15.167.4-microsoft-standard-WSL2

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
