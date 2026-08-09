# SCC-56 — build `/sudo-parallel-check`: implementation plan

**Ticket** SCC-56 (`To Do Next`) · **Type** Task · **Repo** `Sudo_Hatter_Command` (lobby) ·
**Branch** `chore/SCC-56-parallel-check` off `main` · **Lane** LOCAL (no deployable path in the diff)

## Goal — in the operator's words

> *"something so I can use that `/` command after all the stories for an epic are complete. This
> command will have an agent assess and tell me with a tag what I can run in parallel."*

**"Complete" means WRITTEN, not shipped.** Prior art says so twice: the retired
`/sudo-update-scrum-board` — *"the operator's lever: to develop an epic in parallel, write all its
stories first"* — and the grounding gate, which cannot compare touch-sets that do not exist yet.
Asking "what can run in parallel?" about an epic whose stories are already *done* is a question with
no answer worth having.

## Background — why the label never worked

`parallel-ok` is ruled today by `/sudo-write-story-tests` Step 1.6, **at story pickup**. That mints
19.1's ticket before 19.2's story file exists, so there is nothing to compare against — and it is
never re-evaluated. A boolean also cannot say *"safe after AVCH-34"*; that edge is simply lost.

The proof is empirical: **zero** tickets across `SCC` + `AVCH` carry the label, and the `Parallel-OK`
saved filter returns nothing. This is not drift to repair — the seam was never able to be right.

**The fix is the writer, not the field.** A per-story writer can never see the set. A parent-scoped
pass that recomputes and **rewrites every child's label in one go** is self-correcting on every
re-run. Same label, opposite property.

## ⚖️ RULING 2026-08-09 — the name, and the scope it settles

I proposed `/parallel-check` (no `sudo-` prefix) because the ticket's ruling #2 asked for **Tasks
under a grouping epic** — which means SCC, which is the lobby, which `sudo-target-resolution.md:8`
forbids to every `/sudo-*` command.

**The operator overruled it, and narrowed the scope instead:**

> *"no i do not agree actually this is a sudo check"* · *"it only works on stories with epics written
> by the BMAD method"* · *"so no it is sudo-parallel-check"*

**Amended in the same breath** — I had over-narrowed it to "projects only", and that was wrong:

> *"if it touches the lobby it will be if we write an epic and stories for the feature or product we
> are adding to the command center. We do have the BMAD method here too."*

**The discriminator is BMAD STORIES, not project-vs-lobby.** Verified: the lobby carries a full BMAD
install — `_bmad/bmm/`, `_bmad/tea/`, `config.toml` — with no stories written *yet*. The day an epic
and its stories land here, this command answers for them exactly as it does for AGY.

**Ruling #2 as it now stands: BMAD stories under a BMAD epic, in whichever repo holds them.** What
is excluded is **grouping epics and Tasks**, wherever they live — not the lobby.

**The target is derived from the key, so nothing is asked and nothing is guessed.** Each repo
declares its project in `.agents/jira.conf` (`JIRA_KEYS="SCC"` here, `"AVCH"` in AGY), so
`--parent AVCH-13` resolves to `Projects/AGY_AVIATIONCHAT` and `--parent SCC-99` resolves to the
lobby. Mechanical, and it starts working in the lobby the moment stories exist here.

This also settles the `sudo-` prefix honestly rather than by loophole: the command does not roam the
lobby, it **follows the epic**. Consequences:

- The parent **must** be a BMAD epic (a BMAD number in its summary / a matching epic in `epics.md`).
  A **grouping** epic — `CI/CD Improvment`, `Thin toolkit`, and every SCC epic today — is **refused
  by name** with the reason, not silently handled.
- A repo with no `_bmad/bmm/stories/` at all is refused the same way — *"no BMAD stories in this
  repo yet"* — which is the lobby's answer **today** and stops being so on its own.
- Children are `Story` work items with story files. The `Task` branch of the design is **deleted**,
  not stubbed. SCC's Tasks get no parallel assessment; SCC's future Stories do.
- ⚠️ **Follow-on, not done here:** `sudo-target-resolution.md:8` says *"never the lobby"* flatly.
  That is now false for this one command. Flagged for a one-line amendment on its own ticket.

## Design — the script does the math, the agent does the judgment

The hard part is **extraction, not set math**. Across 139 AGY story files: 105 name `backend/` /
`frontend/` source paths, 58 carry negative declarations, and only 29 have a `**Task**` checklist —
so there is no field to parse. Telling *"will modify"* from *"mentions"* is a reading judgment
(story 19.1 names `google_llm.py:119`, a path inside the venv — a **reference**; and says *"NO
`firestore_session.py` changes — that is 19.2 entirely"*, a **negative declaration**, the strongest
free signal in the corpus). So: **agent extracts, script computes, script writes.**

### New — [.agents/scripts/parallel_check.py](../../../.agents/scripts/parallel_check.py)

Three subcommands, stdlib only (matching every other script in `.agents/scripts/`):

| Subcommand | Does | Never does |
|---|---|---|
| `plan --parent <KEY>` | **refuses a non-BMAD epic first**, then enumerates the children via `acli`, resolves each to its story file, applies the **grounding gate**, emits a JSON work packet naming the exact files for the agent to read | judge overlap |
| `resolve --plan F --touchsets F` | pairwise disjointness → **largest all-disjoint set**; contract edges; verdicts; the stamp | touch Jira |
| `stamp --plan F --verdicts F [--apply]` | writes `parallel-ok` onto 🟢 **and strips it from everyone else**; posts the set table as ONE comment on the epic | transition anything |
| `check --parent <KEY>` | is the existing stamp still valid, or stale? | write anything |

**The BMAD-epic gate comes first.** `plan` reads the parent's summary and the project's `epics.md`;
no BMAD number and no matching epic → it **refuses by name**: *"`AVCH-43 CI/CD Improvment` is a
grouping epic, not a BMAD epic. `/sudo-parallel-check` assesses BMAD stories only."* No fallback, no
guess — a grouping epic's children are Tasks with no story files, so every row would be 📝 anyway and
the refusal says why in one line instead of printing an empty table.

**Grounding gate**, in the retired spec's authority order — first available wins:

1. `git diff --name-only <base>...<branch>` — code written beats every declaration
2. `implementation_plan.md` "Modify/Add" lines **plus every source path its `## Self-Audit` names**
   (that section's whole job is finding the edit sites the plan missed)
3. the story file's Dev Notes surfaces / task paths

None of the three → **📝 no story**, and the printed answer is `/sudo-write-story-tests <id>`, never
a guess. (2026-07-31: the board called a story with no story file parallel-safe; its ① then found
both stories editing `check_cost_cap` **at the same line**.)

Planning artifacts (`_bmad-output/`, `_bmad/`, `_artifacts/`, `_my_resources/`) are **filtered out** —
only source paths decide overlap.

**Staleness is the load-bearing part.** The stamp records the set it was computed against —
`verified <date> against N children: <keys>`. `check --parent <KEY>` re-reads it, re-enumerates the
parent's children, and a mismatch prints **"re-run me"** — never a verdict. An undetectably stale
snapshot is the exact failure of the sprint dependency map and of the `Deferred` saved filter, both
of which bit on 2026-08-09.

**Fails toward 🔒.** A false 🟢 puts two lanes on the same line; a false 🔒 costs only serialisation.
Anything unresolved is 🔒 with the suspected surface named.

### New — [.agents/commands/sudo-parallel-check.md](../../../.agents/commands/sudo-parallel-check.md)

Step 0 **target = the repo whose `.agents/jira.conf` claims the key's project** — derived, never
asked, never guessed; documented as a §STD variant and pointing at
`.agents/rules/sudo-target-resolution.md` so `workflow_lint`'s rule-pointer check passes → Step 1
`plan` → Step 2 **agent extraction** with the "will modify vs mentions" rules written out → Step 3
`resolve` → Step 4 print → Step 5 `stamp --apply`.

**Display rule, carried forward verbatim: show the ANSWER, never the math.** One approved list
(membership = safe beside every other member) then one verdict per ticket:
🟢 approved · 🔒 after `<ticket>` · ⏳ waiting on `<story>` · 📝 no story.
⛔ Pairwise notation ("✅ vs C+D"), lane letters, and "not yet checked" are **banned** — you found the
lane-letter matrix confusing and that ruling stands.

⛔ **It STATES, it never STARTS.** Prints the commands to act on the answer; touches Jira; never the
working tree, never a branch, never a worktree.

### Edited — [.agents/commands/sudo-write-story-tests.md](../../../.agents/commands/sudo-write-story-tests.md#L44-L79)

Step 1.6 drops the **Parallel** ruling and the `parallel_ok:` frontmatter stamp; `quick-dev` and
`blocked` **stay** (both are per-story facts genuinely knowable at pickup). In their place, a pointer
to `/sudo-parallel-check` once the epic's stories are written.

### Edited — [.agents/rules/jira.md](../../../.agents/rules/jira.md#L206-L213)

Label vocabulary: `parallel-ok` is no longer "ruled by ①" — it is **written by
`/sudo-parallel-check`, carries a stamp, and is meaningless without one**. Guardrail 4 gains the
label-writing seam (and the note that this command writes labels, never a status). The `Story`
row of §Work-item types gains the one-line note that parallel assessment is Story-only.

### Edited — [_my_resources/_quick_reference/sudo_workflows_testing.md](../../../_my_resources/_quick_reference/sudo_workflows_testing.md)

Required — the armed SOP-currency gate rejects a `.agents/commands/` + `.agents/scripts/` change
that doesn't move this page.

### New — [.agents/scripts/tests/test_parallel_check.py](../../../.agents/scripts/tests/test_parallel_check.py)

Auto-discovered by `run_all.py` (`test_*.py`, no wiring). Cases, all offline — no `acli`, no network:

- **a grouping epic is refused** — named, with the reason, exit non-zero (the scope ruling, pinned)
- ungrounded child → 📝, and is **never** in the approved set
- two children naming the same source path → not both 🟢; the loser reads 🔒 **after the winner**
- overlap **only** in `_bmad-output/` / `_artifacts/` → still 🟢 (planning artifacts never collide)
- A imports a symbol B **creates**, zero file overlap → A is 🔒 (add/add has no merge base)
- `blocked_by:` frontmatter → 🔒 regardless of files
- **stamp staleness**: a stamped set that no longer matches the current children → "re-run me", not a verdict
- **label stripping**: a child that *was* 🟢 and now overlaps loses the label on re-run
- max-set determinism: same input, same answer, independent of key order

### Sync — four platforms

Mirror to `.claude/commands/` and `.opencode/commands/` (no `platforms:` key = all four, matching
`close-task-merge-tree.md`); `/sync-agents` emits the Antigravity launcher.

## Verification plan — exact commands

```bash
python3 .agents/scripts/tests/run_all.py            # must be 9/9 files passed (8 today + the new one)
python3 .agents/scripts/workflow_lint.py            # 1 pre-existing AGY error, no new ones
python3 .agents/scripts/parallel_check.py plan --parent AVCH-13     # live: Epic 12, 7 story files
python3 .agents/scripts/parallel_check.py plan --parent AVCH-43     # live: MUST refuse (grouping epic)
```

Then a real end-to-end run of `/sudo-parallel-check AVCH-13` — Epic 12 is `In Progress` with children
AVCH-14/15/16 and seven `story-12-3-*.md` files on disk, so it exercises grounded **and** ungrounded
rows. Close out with `/close-task-merge-tree`.

## What this plan deliberately does NOT do

- **No background refresher.** A "cheap Sonnet status refresher" was designed and **rejected before
  build** (2026-08-02) — a half-refreshed board looks fresher than it is. Not re-proposed.
- **No status transitions.** Labels and comments only; placement stays yours (guardrail 2).
- **No back-fill of old tickets.** Zero tickets carry the label today, so there is nothing to migrate.
