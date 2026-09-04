---
name: a-script-plus-an-instruction-is-not-delivery
description: If a feature needs a live process, shipping the script plus an SOP line telling the operator to run it delivers NOTHING — SCC-355's notifier was 100% silent from the day it landed because nobody ever ran it. Ship the installer.
metadata:
  type: project
---

SCC-355 (2026-08-30) shipped `zoo_notify.py --watch` — a foreground poll loop — plus an SOP row
reading *"Start the watcher once per machine."* Zoo Code contributes no event hook, so a live
process is the only possible trigger, and no process ever existed: no `ps` entry, no LaunchAgent.
The feature was silent on the Mac from the day it landed until the operator reported it a day
later. A classifier bug found in the same investigation would only have made it *partly* silent;
this made it *entirely* silent, and it is the bigger half by far.

**Why:** an instruction a human must remember is not a delivery mechanism. Every gate passed —
38 green tests, a mutation sweep, a review verdict — because they all tested the script, and the
script was correct. Nothing in the system asks *"and what starts it?"*, so the gap is invisible to
every check the house owns.

**How to apply:** when a lane's deliverable needs something RUNNING — a watcher, a daemon, a
poller, a listener — the acceptance list gets a row for the **install**, with its own test, in the
same lane. Ship a `*_install.py` beside the script (SCC-355's fix: launchd `RunAtLoad` +
`KeepAlive` on the Mac, a `pythonw` Startup `.cmd` on the PC) and prove it live: `launchctl list`
plus the agent's own log, not "the operator will run it." Three traps that only appear on a real
install, all of them silent: launchd sources **no** shell profile (so `NTFY_TOPIC` from `~/.zshrc`
is gone — [[zshrc-is-invisible-to-automation]]), its default `PATH` cannot see `/opt/homebrew/bin`
(so a Homebrew notifier half-works — push lands, banner dies), and Python **block-buffers stdout
when it is not a TTY** (so the log you would check is empty, which is indistinguishable from never
started). Related: [[hooks-armed-measures-pointer-not-payload]] — the same disease, a pointer
checked instead of the payload.
