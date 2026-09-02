---
name: gate-receipt-cwd-needs-absolute-executable
description: "gate_receipt.py --cwd moves the CHILD's cwd but a relative executable path still resolves against the INVOKING shell's cwd — exit 127/WinError 2, a 0.0s UNRUNNABLE receipt; pass the venv python ABSOLUTE."
metadata: 
  node_type: memory
  type: reference
  originSessionId: ccec7e02-346d-4d32-b2ff-da2abcb9d9b6
  modified: 2026-09-02T01:53:44.490Z
---

**`gate_receipt.py run --cwd <worktree> -- backend/.venv/Scripts/python.exe -m pytest …` fails
exit 127 in 0.0s** when invoked from the lobby: `--cwd` sets the child process's working directory,
but Windows resolves a RELATIVE executable path against the PARENT's cwd before the child exists
(WinError 2). The receipt records `UNRUNNABLE` — an honest but wasted run.

**Why:** it bit two seats in a row on AVCH-109 (the ② recovery session's ledger row "UNRUNNABLE
(relative venv path, WinError 2)", then the follow-on seat again), because the passing receipt's
recorded `cmd` shows the relative form — copying it back reproduces the trap.

**How to apply:** when the invoking shell is not the target tree (the normal case — the script
lives in the lobby), pass the venv executable as an ABSOLUTE path:
`… --cwd "<worktree>" -- "<worktree>\backend\.venv\Scripts\python.exe" -m pytest backend/tests …`.
Same family as [[preflight-resolves-repo-from-cwd]] and [[bash-cwd-resets-to-main-checkout]].
