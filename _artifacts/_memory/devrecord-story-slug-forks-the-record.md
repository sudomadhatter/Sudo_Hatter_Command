---
name: devrecord-story-slug-forks-the-record
description: "jira_feed devrecord keys on --story; a different slug for the same lane silently posts a SECOND Dev Record, and `check` exits 0 calling it \"one per lane, the designed state\"."
metadata:
  node_type: memory
  type: feedback
---

`jira_feed.py devrecord` decides update-vs-create from **`--story`**, not from `--key`. Pass a
different slug than the earlier record used and it posts a **second** Dev Record instead of
updating in place — no warning, and the new comment still footers itself *"one Dev Record per
ticket, updated in place."*

2026-08-15, AVCH-59: `/smh-quick-dev` filed under `main-write-gate`; at close-out I passed
`--story avch-59-main-write-gate` (the branch slug, which is what the command's `--story
<branch-slug>` literally asks for). Two records.

**Why it is worse than a duplicate:** `check` **exited 0** and explained the pair away —
*"2 Dev Records, one per lane (avch-59-main-write-gate, main-write-gate) — a follow-on lane rides
the ticket it came from, so this is the designed state."* The gate that exists to catch this read
my typo as a second lane and blessed it. Only after I re-filed under the right slug did it warn at
all (`2 Dev Records for 'main-write-gate'`, exit 1) — i.e. **the check is blind precisely when the
slugs differ, which is the only way the bug happens.** A green check is not evidence here.

**How to apply:** before `devrecord` at close-out, read the existing record's title —
`acli jira workitem comment list --key <KEY>` — and pass **that** slug verbatim. If a duplicate
already exists: re-file under the correct slug (it updates the newest), fold in anything only the
older one carried, verify the merged text, then
`acli jira workitem comment delete --key <KEY> --id <ID>` — there is no `--yes` flag, pipe `y`.
Confirm with `jira_feed.py check` → `one Dev Record`.

Same class as [[piping-a-gate-hides-its-exit-code]]: the exit code answered a different question
than the one I was asking. Related: [[closeout-target-is-a-machine-contract]].
