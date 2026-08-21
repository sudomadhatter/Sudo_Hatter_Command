---
IsArtifact: true
ArtifactMetadata:
  title: SCC-245 — the ninth speaking obligation
  type: walkthrough
  date: 2026-08-21
---

# SCC-245 — close the loop; never end on a new problem

**Lane:** `chore/SCC-245-closing-obligation`, cut from `origin/main` @ `999c23b`.
**Shape:** lightweight — ticket → edit → gates → PR. `lane_qualify` returns `TASK` (`.agents/**` is
toolkit), so the ticket and gates are required; the plan/audit/RED ceremony is not for a doc edit the
operator approved word-for-word.

## What changed

`.agents/rules/operator-profile.md` (FLOOR — every agent, every session, both machines) gained a
**ninth speaking obligation**: *a finding without a fix is not a contribution; it is a bill.* In-lane
findings are fixed in the lane; out-of-lane findings arrive once, in one line, with the remedy named.
The rule's self-check grew a second pass for the **ending** of a reply — it only ever guarded the
opening. `AGENTS.md` and `rules/INDEX.md` both said "eight"; reconciled to nine.

The memory store's three uncommitted memories and index were committed from the shared checkout.

## Evidence

| Gate | Result |
|---|---|
| `run_all.py` (bare) | **40/40, exit 0** |
| `workflow_lint.py --toolkit-only` | **exit 0** |
| `check_maps.py --depth3-only --strict` | **exit 0** |
| SOP currency | section written, staged in the same commit |

## Your Actions

- [ ] **The merge itself** — lands via this branch's PR
