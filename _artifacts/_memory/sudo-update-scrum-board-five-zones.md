---
name: sudo-update-scrum-board-five-zones
description: "⛔ /sudo-update-scrum-board was RETIRED 2026-08-07 (SCC-13) — Jira is the human view. Recover it with `git show 8144518^:.agents/commands/sudo-update-scrum-board.md`. Its Step 2.5 parallel logic is the surviving value and is the spec for SCC-56 /sudo-parallel-check."
metadata:
  node_type: memory
  type: project
  originSessionId: b80fc075-1753-4842-9946-7a790b19dc98
  modified: 2026-08-09T10:47:36.953Z
---

⛔ **RETIRED 2026-08-07, commit `8144518` (SCC-13)** — *"retire the scrum-board apparatus — Jira is
the human view."* All four lobby copies deleted (`.agents/commands/`, `.agents/workflows/`,
`.claude/`, `.opencode/`). Decided in **SCC-20**: `sprint-status.yaml` **survives**; the map, the
command and the stale-stamp hook retire. Everything below the first section describes a command that
**no longer exists** — kept because its parallel model is being rebuilt.

**The operator could not find it on 2026-08-09 and had to ask.** Recover the last good version:

```bash
git show 8144518^:.agents/commands/sudo-update-scrum-board.md     # 281 lines
```

⚠️ A **stale live copy** survives at `Projects/OpenChat-Openrouter/commands/sudo-update-scrum-board.md`
(279 lines, dated the day before retirement — an earlier draft that escaped the sweep). Do not read
it as authoritative; use the git command above.

**What survives, and why it matters:** Step 2.5 — *Parallel Approved Stories (the set is the
verdict)* — is the spec for **SCC-56 `/sudo-parallel-check`** → [[parallel-ok-is-a-set-property]].
Its touch-set authority order (branch diff > `implementation_plan.md` "Modify/Add" lines + every path
its `## Self-Audit` names > story-file Dev Notes surfaces), its four verdicts, and its grounding gate
are all still correct.

---

## What it was (historical — the command is gone)

**Renamed 2026-08-02** (operator-directed redesign): `/update-personal-sprint-map` →
`/sudo-update-scrum-board`; board doc `sprint-dependency-map.md` → `sprint_scrum_board_map.md`.

**Five zones, fixed order, ~150-line cap:** 🎯 Right now (≤8 lines, pointers only) → 🧵 **Parallel
Approved Stories** → 🛠 Work queue (ONE table: 🟢 ready → 🔴 blocked → 📋 pipeline, a command per
row) → 👤 Your actions → 📚 Reference.

**Display rule (operator-driven): show the ANSWER, never the math.** The 🧵 zone prints an approved
list (membership = safe beside every other member) + a one-verdict-per-ticket table: 🟢 approved ·
🔒 after `<ticket>` · ⏳ waiting on `<in-flight story>` · 📝 no story. Pairwise notation ("✅ vs
C+D"), lane letters, and "not yet checked" are BANNED — the operator found the lane-letter matrix
confusing. **This display rule carries forward to SCC-56.**

**The team-lane rule (operator runs 2–4 teams):** a parallel verdict requires both touch-sets, which
exist only for GROUNDED stories. Ungrounded = never lane-eligible; the board says "write the story
first", never guesses. **The operator's lever: to develop an epic in parallel, write all its stories
first.** The 2026-07-31 incident proved it: the board called a story with **no story file**
parallel-safe, and its ① then found both stories editing `check_cost_cap` at the same line.

**OPERATOR RULING (2026-08-02): no background model ever updates this board.** A "cheap Sonnet status
refresher" was designed and REJECTED before build — a half-refreshed board looks fresher than it is.
Don't re-propose background refreshers. **Carries forward to SCC-56.**

Related: [[parallel-ok-is-a-set-property]], [[sprint-dependency-map-recommends-stale-work]],
[[parallel-lanes-fix-the-same-finding]], [[jira-integration-live]].
