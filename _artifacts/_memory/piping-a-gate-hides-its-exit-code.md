---
name: piping-a-gate-hides-its-exit-code
description: "Piping a gate to head/tail makes $? report the PIPE's status, not the gate's — a failing gate prints \"exit=0\" and reads as green."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f3e01c24-9b74-4562-ba18-4cc66697fffd
  modified: 2026-08-09T15:28:46.210Z
---

`python3 some_gate.py … | tail -5` then echoing `$?` reports **tail's** exit status, not the
gate's. A gate that exited 2 prints `exit=0` and reads as a pass.

Bit twice in one session (2026-08-09):
- `sop_currency.py --staged` — the flag **does not exist**, argparse errored out, and the piped
  echo still printed `exit=0`. The gate never ran at all.
- `jira_feed.py check --key SCC-60` — really exited **2** (`description: 0 chars - no outline`);
  the piped run printed `CHECK_EXIT=0`.

**Why:** a pipeline's status is its *last* command's. This is worse than a plain wrong answer
because the output above it still looks like the gate's real output, so nothing signals that the
number is from a different process.

**How to apply:** run gates **unpiped** and read the exit code directly. If output really needs
trimming, capture first (`out=$(cmd); rc=$?`) or set `set -o pipefail`. Any gate reported as green
from a piped invocation has not been verified — re-run it bare before saying so. Related:
[[preflight-resolves-repo-from-cwd]] (a verdict that is honest about the wrong target).
