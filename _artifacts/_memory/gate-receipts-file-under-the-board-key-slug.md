---
name: gate-receipts-file-under-the-board-key-slug
description: gate_receipt.py files receipts at _bmad-output/gates/<norm_id(--story)>/ and closeout_preflight looks under the BOARD key (24-7-coleman-adk-rebuild) — stamp with --story avch-109 and three real greens read as NO RECEIPT.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ccec7e02-346d-4d32-b2ff-da2abcb9d9b6
  modified: 2026-09-02T19:03:45.880Z
---

**`gate_receipt.py run --story <X>` writes to `_bmad-output/gates/<norm_id(X)>/`, and
`closeout_preflight.py` resolves `--story 24.7` to the board key and reads
`_bmad-output/gates/24-7-coleman-adk-rebuild/`. The two must be the same string.** AVCH-109 stamped
all three receipts with `--story avch-109` (the Jira key), so a lane with three real, green,
clean-tree receipts reported `gates: suite: NO RECEIPT` and blocked.

**Why:** one lane has two names — the Jira key on the branch and the board key on `sprint-status.yaml`
— and the receipt writer takes whatever you type. Nothing cross-checks. A receipt under the wrong
slug is not evidence anything downstream can see.

**How to apply:** `--story` on `gate_receipt.py run` takes the **board key slug**, the same string
the board line starts with (`24-7-coleman-adk-rebuild`, `19-3-clean-slate-test-data-wipe`) — never
the Jira key. Verify with `gate_receipt.py check --story <slug> --require suite --sha <sha> --cwd <tree>`
before ③ reports. If they were filed under the wrong slug: **re-run, never rename** — a receipt is
evidence of a run, and its JSON carries the `story` it was stamped with. Freshness is a whole-tree
`git diff --quiet`, so any later commit (even docs) makes a receipt STALE against HEAD — pass
`--sha <the gate commit>` to the preflight and say so. Related:
[[gate-receipt-cwd-needs-absolute-executable]], [[test-certification-at-shipping-sha]],
[[review-is-narrated-until-the-block-is-in-the-walkthrough]].
