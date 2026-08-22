---
name: close-out-command-is-daniels-signoff
description: Daniel runs ~60% of flows with the MANUAL sudo-* commands (not autopilot); when he invokes a close-out command that IS his sign-off — it must act, never punt the decision back to him.
metadata:
  type: feedback
  originSessionId: 315ab028-3603-4a16-812f-e70b12b06a2f
  modified: 2026-07-27T16:58:56.449Z
---

Daniel does roughly **60% of his dev flows with the MANUAL `sudo-*` commands**, not the `_AP`/autopilot variants. So manual-command correctness is the priority, and the manual command must do its job end-to-end.

**The principle (his words):** *"when I run that command, that is me signing off for the story being done."* A Daniel-invoked close-out command is itself the human sign-off — so it must ACT, not ask. Concretely for `/sudo-update-sprint-memory`: if everything is good (tests green / verdict not FAIL) it must **close the story (flip `review → done`) AND update the sprint, without asking**. The ONLY thing that may block the flip is objectively-red tests (a `/sudo-code-review` **FAIL** = a real new regression) — and holding in that case is correct (he confirmed: "if it's not [ok] that's exactly how it should handle it"). There must be **no "leave it at review and ask Daniel" punt** — that escape hatch is what made him flip story 14.11 by hand.

**Why:** discovered 2026-06-28. `sudo-update-sprint-memory.md` Step 4 contradicted itself — it called the flip "a PRIMARY purpose, by default, without asking" yet also had a live-test gate ("leave the status as-is and ask; flip only on Daniel's OK"). That gave the agent permission to punt even when things were fine. Fixed by deleting the live-test "ask" gate and making "good → close it out" the hard default, with FAIL the only refusal.

**⚠️ THIS COVERS DESTRUCTIVE STEPS TOO, NOT JUST STATUS FLIPS — the 2026-07-27 recurrence.** The example
above is a `review → done` flip, and reading it narrowly is exactly how this fails again. During a
`/sudo-close-workingtree` run the agent found the dead 21.5 worktree husk, verified it against every
condition the command names (no `.git`, no reparse points, story landed), and then wrote *"I'm flagging it
rather than removing it unasked"* — punting a **deletion the command explicitly instructs**. The operator's
reply: *"this is a / command and needs to be followed I keep having you leave them and it breaks things."*
Same failure, different verb.

**The trap is a generic instinct overriding a specific document.** "Confirm before irreversible actions" is
a good default *in the absence of instruction*. A sudo-* command IS the instruction — it has already
weighed that risk and encoded the answer, usually with the exact preconditions to check. Re-asking is not
extra safety; it is discarding a decision the operator already made and leaving the system half-cleaned,
which is its own harm (stale worktrees get picked up by the next agent).

**The line:** verify the command's OWN named preconditions, then act. Refuse **only** on a condition the
command itself names as blocking (red tests; unmerged branch; uncommitted work with no remote). Never on
"this feels destructive, I should check." If a genuinely unanticipated hazard appears — work that exists in
exactly one place, a `LOST` worktree — that is not a punt: it is a case the command names as a STOP, or a
gap in the command that you fix in the command.

**How to apply:** when building/auditing any Daniel-invoked command, the human invoking it = the authorization. Don't add "double-check with Daniel before doing X" gates to a command whose whole purpose IS X — surface info, then DO it; only block on an objective signal (red tests), never on deference. See [[sudo-commands-have-ap-twins-that-drift]], [[autopilot-engine-is-project-local]], [[own-it-plainly-dont-make-excuses]].
