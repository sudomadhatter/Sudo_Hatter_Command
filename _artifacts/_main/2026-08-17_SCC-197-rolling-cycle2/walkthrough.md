# SCC-197 — rolling ticket, cycle 2 · walkthrough

**Lane:** `chore/SCC-197-rolling-cycle2` · **riders:** SCC-198 (Part A), SCC-200 (Part B),
SCC-202 (Part C, unplanned) · **commits:** `aad4d82..591fa76` (4) · **base:** `5123e81`
**Plan + Self-Audit:** [implementation_plan.md](implementation_plan.md) · **manifest:** [task.yaml](task.yaml)

---

## Task Checklist

- [x] **Part A (SCC-198) — `cmd_start` clones the next rolling ticket and hands the baton on**
  - The cycle instruction lived only in the ticket's description (first line, capitals) and did not
    fire. The operator's words were the brief: *"its writen in the ticket I just dont know if you
    will read it."*
  - ⭐ **The operator's ruling replaced my design mid-build.** I had two permanent labels — identity
    plus trigger. The ruling: *"I dont like the two tags — once you move it to In Progress we switch
    the tag … it now clones, it moves the original, and switches the tag to the bugs-and-updates."*
    One marker, and it **moves**.
  - The invariant everything falls out of: **a rolling ticket holds `running-bug-list` until its
    successor EXISTS, and not one moment longer.** Clone before swapping (a clone carries labels —
    that *is* the handoff); swap even when the operator's prompt did the cloning; withhold the swap
    when the clone failed, so the cycle self-heals instead of ending silently.
  - Why it is stronger than what I built: a permanent trigger can fire twice, so every guard against
    a second clone must **ask the board**. A baton is consumed by use — the common re-fire (the
    post-commit recorder) cannot clone, with nothing to query and nothing to get wrong.
- [x] **Part C (SCC-202) — unplanned, and forced by Part A**
  - ⛔ Measured live: **`acli edit --labels` ADDS. It does not replace.** `--remove-labels` is a
    separate flag; acli honours both in one call.
  - The stub had modelled a **replace**, and that lie hid a shipped defect — `cmd_finish`'s
    `user-tasks` strip built the reduced set and sent it via `--labels`, re-adding what was already
    there and removing nothing. **The strip has never worked on the board.**
  - It also meant **Part A was wrong in production for an hour** and all 18 of its cases passed.
- [x] **Part B (SCC-200) — every artifact handed back as a clickable link**
  - ⭐ **Recon reframed the part.** The plan assumed the rule was silent. It was not — the duty had
    been in `artifacts-always-first.md` all along, in one blockquote. It still did not fire.
  - So the defect is **where** it is stated, and the fix is placement: the duty now sits at each of
    the three seams where an artifact is produced.
- [x] Gates green, both sweeps clean, INDEX row added, SOP updated (gate-enforced, twice)

---

## What changed

| File | Why |
|---|---|
| [.agents/scripts/jira_feed.py](../../../.agents/scripts/jira_feed.py) | `roll_the_cycle()` + the `cmd_start` seam; `user-tasks` strip via `--remove-labels`; the sibling add site sends one label, not the union |
| [.agents/scripts/tests/test_jira_feed.py](../../../.agents/scripts/tests/test_jira_feed.py) | stub models the **measured** add/remove semantics; 18 baton cases |
| [.agents/rules/artifacts-always-first.md](../../../.agents/rules/artifacts-always-first.md) | `## Hand It Back` section + the duty at §2, §3, §5 |
| [.agents/rules/work-consolidation.md](../../../.agents/rules/work-consolidation.md) | rung 3 gains *"and not Done"*; the cycle section records the automatic successor |
| [.agents/scripts/tests/test_command_surfaces.py](../../../.agents/scripts/tests/test_command_surfaces.py) | the SCC-200 placement block + 3 negative controls |
| [docs/_scc_sops_prds/workflows_testing_SOP.md](../../../docs/_scc_sops_prds/workflows_testing_SOP.md) | both parts, in operator-facing terms |
| [_artifacts/_main/INDEX.md](../INDEX.md) | the session row (`check_maps` caught its absence) |

---

## Evidence

| # | Acceptance | Evidence |
|---|---|---|
| A1 | The trigger fires on the tagged ticket, not on ordinary ones | `A1`, `A2`, `A2b` — both directions |
| A2 | The handoff actually happens, both ends | `A1b` successor holds the baton · `A1c` original gives it up |
| A3 | Zero extra board reads on the normal path | `A3`/`A3b` **counted**: baseline 2, unchanged |
| A4 | Idempotent, and one holder never two | `A4`/`A4b`/`A4c` |
| A5 | A clone failure never fails the start, and never loses the cycle | `A5`/`A5b`/`A5c` |
| A6/A7 | A failed swap and a failed search are loud, not fatal | `A6`, `A7`/`A7b` |
| C1 | The strip actually strips | `finish: closing clean STRIPS user-tasks` — **RED against the old writer** |
| B1 | The duty sits at all three seams | `SCC-200 …ALL THREE seams` + 3 controls |

**Suite Ledger**

| Scope | Command | Result |
|---|---|---|
| full | `python3 .agents/scripts/tests/run_all.py` | **33/33 files** |
| lint | `python3 .agents/scripts/workflow_lint.py --toolkit-only` | **0 errors, 0 warnings** |
| maps | `python3 .agents/scripts/check_maps.py --depth3-only --strict` | **clean** |
| sweep A/C | `mutation_sweep.py --table sweep-partAC.json` | **7/7 killed**, restore verified |
| sweep B | `mutation_sweep.py --table sweep-partB.json` | **5/5 killed**, restore verified |

`git rev-parse HEAD` → `591fa767136bc9e10797f7976c31b1f995196774`

---

## What the reds actually caught

Three things went red that I would otherwise have shipped, and each was found by running rather
than reading:

1. **`A3` asserted a baseline I had invented.** I pinned "exactly one board read" from the plan;
   `cmd_start` has always made two (status, then the post-transition read-back). The case was
   measuring my expectation, not the program. Fixed to pin the real baseline — which is what makes
   it a cost gate: a third call now reds it.
2. **The stub lied, and the lie was load-bearing.** Fixing `--labels` to match the live board
   reddened four cases at once: the `user-tasks` strip (a **shipped** no-op) and three of Part A's.
   331/335 → 335/335. This file's own comment states the rule that was broken: *a stub more
   generous than the tool it stands in for cannot fail on the bug it exists to catch.*
3. **A negative control caught its own vacuity.** With the base green, the PLAN-seam control went
   red — a decorative `→ ## Hand It Back` pointer left a second marker in the section, so stripping
   the duty did not strip the evidence. The pointers are gone.

Also worth recording: the SCC-200 cases were first written into `test_workflow_lint.py`, where the
**sweep could not address them** (`--case` matches block labels only; every mutant scored exit 3).
Adding one block there was worse — a file is *wired* the moment it contains any `c.block(`, and
`ORPHAN` then demands all 46 of its checks be guarded. Moved to `test_command_surfaces.py`, which is
already fully blocked and already owns the sibling rule's assertions.

---

## The one gap this does NOT close

Neither the prompt nor the tag **detects its own failure.** If a hand-off fails, two tickets carry
`running-bug-list` and nothing says so — the code warns at the moment it happens and the rule tells
you what to do about it, but no gate asserts the board's shape. A board assertion (*exactly one open
ticket carries the trigger*) in `task_preflight.py check_children` would make it loud. Recorded on
SCC-198, deliberately unbuilt.

---

## Your Actions

- [ ] **Decide whether the redundant gate is worth changing.** Measured: `test_sops_prds_folder.py`
      is listed as a separate gate by `/smh-quick-fix` and `/smh-quick-dev`, but it already runs
      inside `run_all.py`. Removing it saves **0.27s** against a 128s full run — real redundancy,
      negligible payoff. My recommendation is to leave it: the line also documents *when* it
      matters. Your call, and it is the only thing here that is not already done.
- [x] The live board was corrected to the baton state by hand, since SCC-201 was cloned before the
      code existed: **SCC-197 → `bugs-and-updates`**, **SCC-201 → `running-bug-list`**.
- [x] Plan, walkthrough and manifest are linked at the top of this document and in chat.
