---
name: zoo-approvals-decision-store
description: "Zoo Code approvals are decided by VS Code globalState (state.vscdb), which .vscode/settings.json seeds exactly ONCE — denies never seed. After any list edit run zoo_permissions_apply.py --apply per machine with VS Code closed, or the tracked lists change the display and nothing else."
metadata:
  node_type: memory
  type: project
---

**The lists you edit are not the lists Zoo decides with.** Zoo Code reads `allowedCommands` /
`deniedCommands` from VS Code globalState — SQLite `state.vscdb`, ItemTable key
`ZooCodeOrganization.zoo-code` — at decision time. The tracked `.vscode/settings.json` seeds
`allowedCommands` only when the state key is absent (first activation ever; `[]` is truthy and
blocks re-seeding), and `deniedCommands` has NO seeding path at all. The settings UI shows the
UNION of state + file, so a file-only entry looks live while deciding nothing. Verified in
v3.80.1 compiled source; the matcher was extracted and executed (SCC-351).

**Why:** two SCC tickets were spent "fixing" the lists by editing the tracked file — the display
changed, the prompting didn't, and each session re-diagnosed from scratch.

**How to apply:**
- After ANY edit to `zoo-code.allowedCommands`/`deniedCommands`: quit VS Code fully, run
  `python3 .agents/scripts/zoo_permissions_apply.py --apply` (PC: `python`), reopen. `--status`
  must read "in sync with tracked file". Once per machine, per edit.
- The matcher is lowercase starts-with per PIECE (split on newlines/`&&`/`||`/`;`/`|`), longest
  prefix wins, tie → deny. Broad allows mean an un-denied damage spelling AUTO-RUNS — the deny
  list is the fence, kept minimum-but-load-bearing (operator ruling 2026-08-30).
- `git -C` is auto-denied (it would launder past every verb deny under the broad `git ` allow);
  the house pin is `cd <abs> && git <verb>` in ONE compound line — `command-shape.md`.
- `destructiveCommandGuardEnabled` stays OFF (ON bypasses the lists for an external binary);
  the Roo/Zoo settings-export import path carries API keys — never a tracked channel.
- Zoo rewrote `.roomodes` via its own YAML writer when modes were touched in its UI (header
  stripped, em-dashes flattened) — treat UI edits of generated files as dirt; regenerate via sync.
- Full reference: `docs/migrations/zoo-code-permissions-guide.md` · gate:
  `.agents/scripts/tests/test_zoo_permissions.py` (68-row battery → 0 approve, 25-step ceremony
  → all approve, doors stay `-C`-free).

Related: [[zoo-code-replaces-roo-code]] · [[nothing-guards-the-merge-target]] (the pin idiom this
changed) · [[hooks-armed-measures-pointer-not-payload]] (same disease: a visible setting that is
not the deciding store).
