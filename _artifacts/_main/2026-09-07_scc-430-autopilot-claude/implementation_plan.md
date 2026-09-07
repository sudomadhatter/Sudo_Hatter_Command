---
IsArtifact: true
ArtifactMetadata:
  title: SCC-430 - Autopilot v3, the Claude half
  type: implementation_plan
  date: 2026-09-07
---

# Implementation Plan - SCC-430: Autopilot v3, the Claude half

**Parent:** SCC-429 (Task). **The design** this lane builds is
[`_artifacts/_main/2026-09-07_autopilot-v3-design/implementation_plan.md`](../2026-09-07_autopilot-v3-design/implementation_plan.md)
(attached to SCC-429; carried to `main` on this branch). Sections cited below as "design 2.3", "design 9.3" etc.
**Lane:** `chore/SCC-430-autopilot-claude` in `.claude/worktrees/scc-430-autopilot-claude`, base `origin/main` @ `d70347ba`.
**Mode:** per-subtask lane (SCC-431, the Zoo half, has its own; see "Landing order" at the end).

## Goal

Replace the retired autopilot lane with the design's Claude shape: one interactive lead session (the March Hare)
calls a deterministic runner once per workflow step; the runner launches a fresh headless `claude -p` child as one
Wonderland seat, the child runs the EXISTING door by name, returns a structured result, and every step lands on the
Jira ticket as a comment - proven on one real story, then the old lane deleted.

Glossary (design 0): a **door** is a slash command the operator types today; a **seat** is one Wonderland team member;
a **child** is one headless `claude -p` process running one step; the **runner** is the script that launches children
and holds the rules an LLM must not be trusted with; **the charter** is the written list of gates the lead may pass
without the operator.

## Acceptance - the ticket's checklist, one row each (proof named per row)

| Row | Statement (checkable) | Proved by |
|---|---|---|
| **A** | S0 spike done and MEASURED: `claude -p` over an `--agents <json>` seat preloads that seat's `skills:`; the `--json-schema` result round-trips; **whether a child launched by the runner reaches the model under the lead's sandbox** (a measurement, not an assumption - see the ⚠️ below); the three cost numbers of design 9 are on the ticket | `spike.md` in this folder carrying five tables (agent-vs-appended cache reads over ten launches; a fork's `cache_read_input_tokens` against its parent; one small story naive vs layered; the `--agents` + `--agent` pair; the sandbox reachability result and its named remedy), the same tables as a comment on SCC-430, and the design record committed on this branch so every citation in this plan resolves |
| **B** | `autopilot_run.py` exists with its negative control: a missing door exits non-zero BEFORE any `claude` call; a result without `status` is `failed`; the review launch refuses a session id the runner has seen; the runner carries no door, rule or seat text | `test_autopilot_run.py`: `test_missing_door_exits_before_claude`, `test_result_without_status_is_failed`, `test_review_refuses_seen_session`, `test_runner_carries_no_door_rule_or_seat_text`, `test_flags_never_bare_never_bypass` - each seen RED against a naive stub first |
| **C** | The seat renderer turns a master's frontmatter into `--agents` JSON at launch; the six masters carry `claude-*` keys; no `.claude/agents/` file is ever written; the Zoo projection is untouched | `test_seat_render_matches_master_frontmatter` (all six masters), `test_render_writes_no_agent_file`; `test_zoo_team.py` and `test_command_surfaces.py` still green |
| **D** | `jira_feed.py step` posts one comment per child with read-back; `needs_human` carries the `Needs Mr. Hatter` marker; the verb is self-contained in `jira_feed.py` | `test_jira_feed.py`: `test_step_posts_and_reads_back`, `test_step_needs_human_marker`, `test_step_refuses_unknown_status`; `test_jira_start_hook.py` still green (its fixture copies only `jira_feed.py` + `wf_common.py`) |
| **E** | `/cicd-autopilot-claude` is the lead's door: the charter (design 2.5), the launch-approval scope, the escalation shape; the SOP's autopilot sections and the quickref twin updated in the same commit | `test_command_surfaces.py` green with the door's case; `workflow_lint.py` exit 0 (the charter's `NO-GO` word requires the door to cite `code-standards.md`); the `sop_currency.py` commit-msg gate passes without `[sop-ok]` |
| **F** | One real AGY story driven end to end with a capped budget, at least one escalation answered from the operator's phone | the story ticket's comment thread (one `step` comment per child, session ids), the per-child usage table in `walkthrough.md`, the operator's word that the phone chip reached him |
| **G** | The old lane is gone: three `-AP` twins, the opencode launcher and the deepseek door deleted, with every live caller updated in the same diff; their tracked launchers purged by the sync; SOP, quickref and INDEX rows retired | `git diff --name-status origin/main...HEAD` shows **seven** `D` rows (five commands + two tracked launchers) and the caller edits; `sync-agents.ps1 -Status` shows no orphan; `gate_receipt.py` green at the tip (the three tests that name the deleted doors were updated, not left red) |

## ⚠️ AUDIT FINDINGS baked in (self-audit 2026-09-07, this file's `## Self-Audit` section)

Three blockers were raised against the first draft and are resolved here; the builder reads them in context:

1. **The sandbox row does not exist as an edit.** The design assumed the runner would be added to
   `sandbox.excludedCommands`. `.agents/scripts/claude_permissions_apply.py:32` says *"⛔ IT NEVER TOUCHES
   `sandbox.excludedCommands`"* and `:131` asserts the key is byte-identical before and after, pinned by
   `test_claude_permissions_apply.py:90`; `families.json` cannot express that key at all. The operator also ruled on
   2026-09-05, verbatim, *"those are exclude commands. that does nothing to help me"* - about approval prompts, which
   is a different problem from network egress, so the ruling is not overturned here, it is simply not the mechanism.
   **So: no `families.json` edit is in this lane.** Step 1 MEASURES whether a sandboxed child reaches the model and
   names the remedy if it does not (Step 1, item 3).
2. **Deleting the five doors turns three suite files red and orphans two engine docs.** They are now declared and
   edited in the same commit (Step 7).
3. **The port rule fired** - nine declared files exist in a second registered repo. Answered in `## Port check` below.

## Decisions carried from the design (the builder does not re-derive these)

- Children run `--permission-mode auto`, never `bypassPermissions`; a permission prompt in a child is an instant
  deny the child reports in `denials[]`; `/smh-llm-approvals` harvests them (design 2.4).
- **Never `--bare` on a child.** `--bare` skips hooks, and the hooks are how the rules reach the child (design 11.1).
- The seat is built AT LAUNCH from `.agents/commands/smh-team-<seat>.md` and handed over as `--agents <json>`;
  the prompt is the one-line pointer `.roomodes` carries. Nothing is written under `.claude/agents/` (design 11).
- The runner passes the door's NAME (`/cicd-dev-story-tests AGY_AVIATIONCHAT 14.2`), never its text; it has no list
  of doors and no landing verb (design 2.3 rules 1 and 6, 11.2).
- Result contract, enforced by `--json-schema`: `{status: done|blocked|needs_human|failed, summary, artifacts[],
  question?, evidence{sha, suite_totals}, denials[], usage}` (design 2.3 rule 3, 9.6 item 1).
- Byte-identical prefix: `--exclude-dynamic-system-prompt-sections` on every child; the first child of a run is
  launched alone, siblings after it starts streaming (design 9.3 layer 0, 9.6 item 2).
- Fork chains are homogeneous: one seat, one model, one effort per `--resume --fork-session` chain; the Cheshire
  Cat runs ② end to end for that reason (design 9.3 layer 2, 2.2).
- The review (③) is a fresh Fable child with no seat, in a session id the runner has never seen (design 2.3 rule 5).
- Budgets: `--max-budget-usd` per child and a run-level cap in the runner (design 2.3 rule 4). ⚠️ `--max-turns` is
  **not in `claude --help` on 2.1.258** - Step 1 probes for it after the upgrade and it is only pinned if it exists.
- The DeepSeek lane survives as runner flags (`--dev-model`, `--dev-base-url`), not as a door (design 4).

## Port check (the rule fired; this is the section it demands)

`.agents/rules/port-checklist.md` fires mechanically because files in this lane's scope exist in a second repo.
Measured with `git diff --no-index`: `Projects/sudo-command-center/.agents/` carries `jira_feed.py` (differs,
169+/190-), `cicd-autopilot-claude.md` (differs, 19+/19-), all five delete targets (differ), `smh-team-caterpillar.md`
(differs, 3+/8-) and the other five seat masters (identical).

**Disposition: out of scope, and the six checks are not due.** `docs/workspace-standard.md:253-260` states what that
submodule is: *"the **published teaching edition** of this lobby - a sanitized export, never edited in place"*, kept
current by `export-teaching-edition.ps1` from the `claude/teaching-edition` branch, and *"**no** - it is a mirror"*
in the audited column. A port pushes a change into a repo that is maintained; this one is regenerated, and editing
it in place is what its own row forbids. SCC-399 is the ticket that established this after the suite audited it as a
thin project by mistake. **The obligation this lane does carry:** nothing, until the next export runs - and that
export is not this lane's work. No AVCH-side copy of any file in this scope exists (`find Projects -name
"cicd-autopilot*"` returns only `sudo-command-center`).

## Steps (one per acceptance row; each names the assertion that proves it)

### Step 1 - S0, the spike (row A) - half a day, nothing built until its tables exist

Everything the spike writes lives in this artifact folder under `spike/` (`spike/seat.json`,
`spike/result.schema.json`, `spike/seat-pointer.md`), so nothing lands outside `_artifacts/`.

1. **Prerequisites, printed.** `claude --version` (>= 2.1.259 is Ask-First item 1), then
   `claude --help | grep -n "max-turns\|append-system-prompt-file"` - **`--max-turns` is absent on 2.1.258 and
   `--append-system-prompt-file` appears only inside `--bare`'s description text**, so this line decides whether
   Step 2's flag set may name them. A flag that does not print here is dropped before any test pins it.
   Read the current settings with `python3 .agents/scripts/claude_permissions_apply.py --status` (**`--status`, not
   `--check`** - `--check` belongs to `permission_render.py`).
2. **The preload measurement.** Write `spike/seat.json` by hand for ONE seat (the Gnat: read-only, cheapest) whose
   `skills:` names one real entry under `.claude/skills/` (`smh-memory-audit`). Launch ten byte-identical children:
   `claude -p --agents "$(cat spike/seat.json)" --agent gnat --output-format json --json-schema
   spike/result.schema.json --exclude-dynamic-system-prompt-sections "Reply with only the first heading line of the
   skill you were given, then stop."` Record per launch `usage.cache_read_input_tokens` and `usage.cache_creation.*`.
   Then the same ten with `--append-system-prompt-file spike/seat-pointer.md` instead of `--agents`.
   **Table 1** = which delivery reads the cache. **Table 4** = whether the reply quotes the skill's heading (the
   `--agents` + `--agent` pair on one launch line; the vendor documents each half, not the pair).
3. **The sandbox measurement (replaces the assumed settings edit).** Run one of those launches from a sandboxed
   Bash call, exactly as the lead would invoke the runner. **Table 5** records reached / did not reach. If it did
   not, the remedy is named there and is the operator's call, not the builder's: either he hand-adds the runner to
   `sandbox.excludedCommands` in `~/.claude/settings.json` knowing it drops that command's sandbox auto-approval
   (his 2026-09-05 ruling quoted beside it), or `api.anthropic.com` is added to the sandbox's network allowlist, or
   the lead invokes the runner unsandboxed and eats one approval per run (a budget threat, so last).
4. **The fork measurement.** One plan child, then `--resume <id> --fork-session` a second; **Table 2** = the fork's
   cache reads against the parent's prefix size.
5. **The layered measurement.** One small story naive (every child fresh, no pack) then layered (pack + fork +
   identical prefix); **Table 3** = the two totals from each child's `usage`.
6. Post the five tables as one comment on SCC-430
   (`acli jira workitem comment create --key SCC-430 --body-file <file>`).

**Proof:** `spike.md` exists with five tables and the comment reads back. **What S1 inherits:** the winning delivery
of Table 1 becomes the runner's flag set, byte for byte, minus any flag item 1 could not find.

### Step 2 - S1, the runner and its negative control (row B)

`.agents/scripts/autopilot_run.py` (stdlib only, both sides), one verb: `run`.

```
autopilot_run.py run --door /cicd-dev-story-tests --seat cheshire-cat --cwd <story worktree>
                     --args "AGY_AVIATIONCHAT 14.2" --key AVCH-140 --stage 2
                     [--model …] [--effort …] [--budget-usd 8]
                     [--fork-of <session-id>] [--review] [--dev-model … --dev-base-url …]
```

What `run` does, in order, and what a test pins for each:

1. Resolve the door: `/name` to `.agents/commands/name.md`; absent → exit 2 before anything else.
   **`test_missing_door_exits_before_claude`**: a fake `claude` on `PATH` that records every invocation; assert
   zero invocations and exit 2. Seen RED first against a stub that launches anyway (design 2.3 rule 1).
2. Render the seat (Step 3's function) and build the flag set: `-p`, `--agents <json>`, `--agent <seat>`,
   `--permission-mode auto`, `--exclude-dynamic-system-prompt-sections`, `--output-format json`,
   `--json-schema <schema>`, `--max-budget-usd`, `--session-id <fresh uuid>` or `--resume <id> --fork-session`,
   plus `--max-turns` only if Step 1 found it. **`test_flags_never_bare_never_bypass`** and
   **`test_flags_are_byte_stable`** (two builds for one seat are identical).
3. `--review` launches with NO seat, the reviewing model, and refuses any `--fork-of` or a session id present in
   the run's ledger. **`test_review_refuses_seen_session`**.
4. Launch, capture stdout JSON, validate: no `status` → `failed`. **`test_result_without_status_is_failed`**.
5. Append the child's `usage` and session id to the run ledger (`<cwd>/_artifacts/…/autopilot-ledger.json`) and call
   `jira_feed.py step` (Step 4) with the summary. Print the result JSON; exit code by status.
6. **`test_runner_carries_no_door_rule_or_seat_text`**: for every heading and every sentence longer than 40
   characters in `.agents/commands/*.md` and `.agents/rules/*.md`, assert it does not appear in
   `autopilot_run.py` (design 11.3).

### Step 3 - S2, the seat renderer (row C)

`render_seat(master: Path) -> dict` inside `autopilot_run.py`: reads the master's frontmatter keys
`mode-name`, `claude-skills` (list), `claude-model`, `claude-effort`, `claude-tools` / `claude-disallowed-tools`;
the `prompt` is exactly *"You are <mode-name>. Read `.agents/commands/<master>` (repo root) and follow it END TO
END - it is this seat: its identity, its doors and its refusals."* (the `.roomodes` sentence).

⚠️ **The new keys go BELOW `mode-groups`, one line each, values with no unquoted `: `.** `sync-agents.ps1:776`
reads `Get-Content $src -TotalCount 12` and `test_zoo_team.py:439` mirrors that window; today's frontmatter is
seven lines with `mode-name` at 5 and `mode-groups` at 6, so six appended single-line keys keep both inside the
window. Inserting above `mode-name`, or writing `claude-skills:` as a multi-line block list, silently drops the
seat from `.roomodes`. No parser rejects unknown keys (`test_zoo_team.py:154-167` accepts any `k: v`).
**Then run `/smh-sync-agents`** and commit whatever the six tracked `.roo/commands/smh-team-*.md` launchers gain
(`test_settings_allowlist.py:160` counts GENERATED launchers).

**Proof:** `test_seat_render_matches_master_frontmatter` iterates all six masters and compares the rendered JSON
against the frontmatter it read (the twin of `test_zoo_team.py`'s generated-vs-master check; never a table typed
into the test); `test_render_writes_no_agent_file` asserts `.claude/agents/` gains nothing (it does not exist
today, so the assertion is meaningful); `test_zoo_team.py` and `test_command_surfaces.py` stay green.

### Step 4 - S3, the ticket verb (row D)

`jira_feed.py step --key <KEY> --stage <n> --door <name> --seat <seat> --status done|blocked|needs_human|failed
--summary-file <f> --session <id> [--usage-file <f>] --apply`: posts one comment in the house shape (stage, door,
seat, status, session id, the summary, the usage line) and **reads it back like `devrecord`** (`jira_feed.py:1089`
posts, `:1097` refuses with exit 2 when the read-back does not find it). `needs_human` prefixes the comment with the
literal marker line `Needs Mr. Hatter` followed by the child's `question`.

⚠️ **`step` imports nothing new.** `test_jira_start_hook.py:58-60` copies only `jira_feed.py`, `wf_common.py` and
the two hook files into its fixture; a `step` that imports `autopilot_run.py` breaks `jira_feed.py start` inside
that fixture. Keep it self-contained.

**Proof:** `test_step_posts_and_reads_back`, `test_step_needs_human_marker`, `test_step_refuses_unknown_status`,
on the fake-acli harness `test_jira_feed.py` already uses; `test_jira_start_hook.py` still green.

### Step 5 - S4, the lead's door (row E)

Rewrite `.agents/commands/cicd-autopilot-claude.md` (keep the name; the launcher regenerates on sync):
Step 0 bind the project + prerequisite check (CLI version, the sandbox answer from Step 1); Step 1 the
launch-approval scope - what the operator's launch word covers (the charter table of design 2.5, pasted as the
door's own table: the lead passes ② Step 2's `continue`, answers Step 2.5 questions from the pack, parks ③ PASS,
runs one fix cycle on CONCERNS/FAIL; escalates NO-GO, dependencies, schema, CI, security, file deletes, a second
non-PASS, PIPELINE_BLOCKER; never lands); Step 2 the loop (call the runner per step, read the result, act by the
charter, escalate with `AskUserQuestion` AND `step --status needs_human`); Step 3 park at review-ready or PASS.

⚠️ **The door must cite `.agents/rules/code-standards.md` in its rules block.** `workflow_lint.py:124` triggers the
code-standards pointer on the literal `NO-GO`, which the charter table contains; without the citation the lint
exits 2.

**SOP in the same commit, and the right sections:** the autopilot rows are at `workflows_testing_SOP.md:2925`
(§15 The autopilot lane, rows at 2933-2935), `:3974` and `:3988-3989` (§18), and `:4426` (the *Not in your menu*
table) - **not §3**, which carries no command table. The operator's flight manual
`docs/_scc_sops_prds/operator_workflows_quickref.md` mirrors that prose by hand at `:422` and `:1306-1323` and gets
the same edit in the same commit, plus one changelog line.

**Proof:** `test_command_surfaces.py` green including the door's case; `workflow_lint.py` exit 0; the commit passes
the `sop_currency.py` gate without `[sop-ok]`. The new surfaces case is proved non-vacuous by mutation: delete the
charter table from the door and the case goes red.

### Step 6 - S5, one real story (row F)

Run the door on one AGY story the operator names (design 3's worked example is 14.2), `--budget-usd` per child and
a run cap. The story's code lands through the story's own lane and doors - THIS lane's diff stays in the lobby;
its evidence is the thread.

**Proof:** the story ticket carries one `step` comment per child with session ids; `walkthrough.md` here carries
the per-child usage table (cache reads per child, totals naive-equivalent vs actual); the operator confirms one
escalation reached his phone and his answer moved the run.

### Step 7 - S6, retire the old lane (row G) - on ruling 3

`git rm` the three `-AP` twins, `cicd-autopilot-opencode.md`, and `cicd-autopilot-deepseek4.md` (its cost lever is
now `--dev-model`). ⚠️ **Three suite files read those names and go red unless they are edited in the same commit:**

| File | The line that breaks | The edit |
|---|---|---|
| `.agents/scripts/tests/test_review_engine.py:68,90,1258,1370` | `AP_CMD = ".agents/commands/cicd-code-review-AP.md"` in `CALLER_FILES`, checked for a body and against the discovered caller set | drop `AP_CMD` from `CALLER_FILES`; update the `capped` row assertion at `:928` |
| `.agents/scripts/tests/test_twin_parity.py:155-156,333` | the two `NOT_PAIRED` rows, and `A0c every NOT_PAIRED row names a command that still exists` | delete both rows |
| `.agents/scripts/tests/test_settings_allowlist.py:183,194` | `_declared("cicd-autopilot-opencode.md")` reads the file unguarded → `FileNotFoundError` aborts the file | retire case E7 or repoint it at a surviving non-zoo door |

**And two engine docs name the deleted reviewer:** `.agents/skills/code-review-engine/steps/step-01-review.md:534`
(the `capped | /cicd-code-review-AP (autopilot)` row, pinned by `test_review_engine.py:928`) and
`.agents/skills/code-review-engine/SKILL.md`.

Then run `/smh-sync-agents` (sandbox off once - it writes `.claude/skills`). It purges the two **tracked**
launchers, so the diff carries seven deletions, not five: `.claude/skills/cicd-autopilot-deepseek4/SKILL.md` and
`.opencode/commands/cicd-autopilot-opencode.md`, plus the rewritten `.claude/skills/cicd-autopilot-claude/SKILL.md`
and the regenerated `.agents/.sync-manifest.json`. The three `-AP` twins have no launchers anywhere
(`sync-agents.ps1:465` skips them), so for them the purge is a no-op.

**Live callers to update in the same commit** (each verified by grep at plan time):
`docs/_scc_sops_prds/autopilot_bmad_dev_loop.md` (20 hits - the SOP INDEX calls it *the autopilot reference*, so it
is rewritten to describe the new lane or retired outright), `operator_workflows_quickref.md` (the two mermaid
graphs at `:422` and `:1306-1323`), `tea_deep_reference.md:605`, `new_machine-migration-guide.md:439`,
`.agents/commands/INDEX.md` (`:29-30`, `:52-53`, `:74` - prose as well as rows), and
`docs/migrations/install_guides/propagate-autopilot-glm-hybrid.md:115,119` (it forbids touching the door this lane
rewrites). `docs/doc-graph.json` regenerates through the maps hook; one dangling link in a 2026-08 walkthrough is
history and stays.

**Not here, named so it is not lost:** the project-side engines (`Projects/*/scripts/autopilot-dev-story.ps1`, four
submodules) live in other repos; cross-repo work takes a ticket per repo. One AVCH ticket (and one per other
project) banners or deletes them after row F proves the replacement.

## Declared Change Set

- NEW `.agents/scripts/autopilot_run.py` — the runner and the seat renderer, stdlib only → B
- NEW `.agents/scripts/tests/test_autopilot_run.py` — negative control, result contract, seen-session refusal, no-door-text grep, renderer parity, flag stability → B
- NEW `_artifacts/_main/2026-09-07_scc-430-autopilot-claude/spike.md` — the five S0 measurement tables → A
- NEW `_artifacts/_main/2026-09-07_scc-430-autopilot-claude/walkthrough.md` — RED/GREEN captures per part, the S5 usage table → F
- NEW `_artifacts/_main/2026-09-07_autopilot-v3-design/implementation_plan.md` — the design record this plan cites throughout; on the branch so the citations resolve → A
- NEW `_artifacts/_main/2026-09-07_autopilot-v3-design/tickets/SCC-429.md` — the parent's fast-read outline, beside the record it describes → A
- NEW `_artifacts/_main/2026-09-07_autopilot-v3-design/tickets/brainstorm-history-scc-208.md` — the deleted brainstorm ticket's snapshot, the record's provenance → A
- EDIT `.agents/commands/smh-team-march-hare.md` — `claude-*` frontmatter keys below `mode-groups` → C
- EDIT `.agents/commands/smh-team-white-rabbit.md` — `claude-*` frontmatter keys below `mode-groups` → C
- EDIT `.agents/commands/smh-team-cheshire-cat.md` — `claude-*` frontmatter keys below `mode-groups` → C
- EDIT `.agents/commands/smh-team-caterpillar.md` — `claude-*` frontmatter keys below `mode-groups` → C
- EDIT `.agents/commands/smh-team-queen-of-hearts.md` — `claude-*` frontmatter keys below `mode-groups` → C
- EDIT `.agents/commands/smh-team-gnat.md` — `claude-*` frontmatter keys below `mode-groups` → C
- EDIT `.roo/commands/smh-team-march-hare.md` — regenerated launcher after the frontmatter edit → C
- EDIT `.agents/scripts/jira_feed.py` — the `step` verb and the `Needs Mr. Hatter` marker, self-contained → D
- EDIT `.agents/scripts/tests/test_jira_feed.py` — the three `step` cases → D
- EDIT `.agents/commands/cicd-autopilot-claude.md` — rewritten as the lead's door with the charter, citing code-standards → E
- EDIT `.claude/skills/cicd-autopilot-claude/SKILL.md` — regenerated launcher, description parity → E
- EDIT `.agents/scripts/tests/test_command_surfaces.py` — the door's surface case → E
- EDIT `.agents/scripts/tests/test_review_engine.py` — CALLER_FILES and the capped row lose the deleted reviewer → G
- EDIT `.agents/scripts/tests/test_twin_parity.py` — the two NOT_PAIRED rows retired with their commands → G
- EDIT `.agents/scripts/tests/test_settings_allowlist.py` — case E7 retired or repointed → G
- EDIT `.agents/skills/code-review-engine/steps/step-01-review.md` — the capped row names a live door → G
- EDIT `.agents/skills/code-review-engine/SKILL.md` — same → G
- EDIT `.agents/.sync-manifest.json` — regenerated by the sync after the deletions → G
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — §15, §18 and the not-in-your-menu row → E
- EDIT `docs/_scc_sops_prds/operator_workflows_quickref.md` — the two mermaid graphs, the hand-mirrored twin → E
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one line per landing → E
- EDIT `docs/_scc_sops_prds/autopilot_bmad_dev_loop.md` — the autopilot reference describes the new lane → G
- EDIT `docs/_scc_sops_prds/tea_deep_reference.md` — the `*_AP` row retired → G
- EDIT `docs/migrations/install_guides/new_machine-migration-guide.md` — the opencode pin line retired → G
- EDIT `docs/migrations/install_guides/propagate-autopilot-glm-hybrid.md` — its do-not-touch clause updated for the rewrite → G
- EDIT `.agents/scripts/INDEX.md` — the runner's row → B
- EDIT `.agents/commands/INDEX.md` — the door's row updated, five retired, the prose at 29-30 and 74 → G
- EDIT `_artifacts/_main/INDEX.md` — this lane folder's row and the design folder's row → A
- DELETE `.agents/commands/cicd-dev-story-tests-AP.md` — frozen twin, replaced by the runner → G
- DELETE `.agents/commands/cicd-code-review-AP.md` — frozen twin, replaced by the runner → G
- DELETE `.agents/commands/cicd-self-audit-AP.md` — frozen twin, replaced by the runner → G
- DELETE `.agents/commands/cicd-autopilot-opencode.md` — there is no opencode lead → G
- DELETE `.agents/commands/cicd-autopilot-deepseek4.md` — its lever survives as `--dev-model` → G
- DELETE `.claude/skills/cicd-autopilot-deepseek4/SKILL.md` — tracked launcher, purged by the sync → G
- DELETE `.opencode/commands/cicd-autopilot-opencode.md` — tracked launcher, purged by the sync → G

## Verification plan

- Per part: the part's test file seen RED (against the naive stub or the missing function) then GREEN, both
  captures pasted into `walkthrough.md`. Mutation check per guard: revert the guarded line, the case goes red.
  Step 5's surfaces case is proved by deleting the charter table; Step 7's edits are proved by the suite that was
  red before them.
- Lane tip, once, sandboxed: `python3 .agents/scripts/gate_receipt.py` (the receipt run IS the suite run). It
  includes `test_check_maps.py` F2, which is why `_artifacts/_main/INDEX.md` carries this lane's row.
- ⚠️ **`sop_currency.py` is armed and fires per commit, not per lane** (`.agents/scripts/git-hooks/SOP-ENFORCE`
  present, `core.hooksPath=.githooks`). Its surfaces are `.agents/commands/*.md`, `.agents/rules/*.md`,
  `.agents/scripts/*.py|*.ps1`, the hook dirs and `AGENTS.md`; `INDEX.md` and `.agents/scripts/tests/` are exempt.
  So every commit carrying the runner, the verb, a master or the door needs the SOP staged with it or `[sop-ok]`
  in the message. The plan-only commit that grounds this lane touches only `_artifacts/`, which is not a surface, so it needs no marker.
- Both sides: scripts probe `python3` → `python`; nothing here needs a venv.
- No deployable path is touched (no `backend/`, `frontend/`, `firebase/`, `functions/`, `mobile/`, `.github/`).

## Ask-First items (the operator's word, before the step that needs it)

1. **Claude CLI upgrade to >= 2.1.259** (dependency upgrade) - before Step 1.
2. **The sandbox remedy, only if Step 1 Table 5 says a sandboxed child cannot reach the model** - and it is his
   choice between the three options named there. No agent writes `~/.claude/settings.json`, and this lane no longer
   assumes a `families.json` row can express it.
3. **Ruling 1** (the charter rows, design 2.5) - before Step 5.
4. **Ruling 3** (the five deletions) - before Step 7; his ruling is the Ask-First for deleting files.
5. **Which AGY story** for Step 6.

## Not in this lane

The Zoo remote and the Zoo variant (SCC-431). The project-side `.ps1` engines (other repos, their own tickets).
The teaching-edition mirror (`## Port check`). Any hand edit of `~/.claude/settings.json` or `.claude/settings.json`
by an agent.

## Landing order with SCC-431

Shared paths: `.agents/commands/smh-team-march-hare.md` (here: frontmatter above the body; SCC-431 part G: the body),
`.agents/scripts/INDEX.md`, `_artifacts/_main/INDEX.md`, `.agents/.sync-manifest.json` (both lanes run the sync),
the SOP and its changelog. SCC-431 also **imports** `jira_feed.py step` (Step 4 here) for its ticket mirror.
This lane lands first (the operator's order: Claude, then Zoo); SCC-431 rebases small hunks and re-runs the sync on
the rebased tip rather than hand-merging the manifest. If SCC-431 ever lands first, this lane's frontmatter hunk
rebases trivially and its `step` import is satisfied the other way round.

## Self-Audit (2026-09-07)

**Level: LEDGER+BLAST** (the change set touches scripts others import, four command/door surfaces, the sync's
frontmatter contract, and seven DELETEs). **Mode: PRE-WORK.** Lenses 1 and 2 ran blind to each other in isolated
read-only agents; Lens 3 ran after them, over their survivors, as the bounded attachment pass it is defined to be.
**The findings below were raised against the first draft and are resolved in the plan above** - the three blockers
by rewriting the sections they broke, the rest by naming the correct file, flag, or section. Nothing is left open.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  existence of 39 paths/commands/scripts/rules/doors/flags/skills (argparse of claude_permissions_apply.py;
             lobby-search searched across .agents/skills .claude/skills .agents/commands; the 5 DELETE targets and their
             launchers; sync-agents.ps1 -Status and its 12-line frontmatter window; test_zoo_team.py's parser;
             claude --help against all 12 flags the plan names; every design section the plan cites)
             declared_change_set.py parse; both-sides command fit; lane fit over every declared path;
             the Scope Ledger (acceptance observables A-G, NEW x row, caller count per NEW file);
             tests-must-gate-for-real per step; internal step references
read:        the plan; the design record (headings + 119-153, 178-192, 485-541, 568-592, 868-876);
             claude_permissions_apply.py, permission_render.py, families.json; sync-agents.ps1 (77, 745-795, 815-835,
             890-925); test_zoo_team.py, test_settings_allowlist.py, test_twin_parity.py, test_review_engine.py,
             test_command_surfaces.py, test_jira_feed.py, test_doc_examples_parse.py, test_refresh_maps.py,
             test_workflow_lint.py, test_doc_graph.py, test_claude_permissions_apply.py; jira_feed.py, sop_currency.py,
             workflow_lint.py, check_links.py, gate_receipt.py, run_all.py, declared_change_set.py;
             the six seat masters, the 5 delete targets, .sync-manifest.json, .roomodes, lobby-search.md;
             workflows_testing_SOP.md (headings; 278-341, 2925-2936, 3965-3989, 4422-4429);
             propagate-autopilot-glm-hybrid.md; claude --version, claude --help, git rev-parse / ls-remote
verdict:     findings below
```

```
lens:        2 Parity + Blast
checks_run:  fetch origin main and base ancestry; git worktree list (and the scc-386 directory's status);
             tracked launchers for the five deleted names (git ls-files + the sync manifest + the -AP skip);
             live callers of the five names across .agents docs _artifacts AGENTS.md README .roo .claude _bmad;
             the six test files that name them, read at the consuming line; workflow_lint _RULE_POINTERS;
             jira_feed verbs/callers/read-back and the hook fixture's copy list; SOP-ENFORCE armed + its surfaces;
             the frontmatter window and every parser that reads it; families.json shape and the apply path;
             the port rule (submodule identity + --no-index diffs of 13 files); twins; sibling worktree diffs;
             risk_seam classify; check_maps check 7 and the maps hooks
read:        both lane plans; .sync-manifest.json; sync-agents.ps1 (31-47, 221-396, 455-465, 604, 674, 740-800, 999);
             smh-sync-agents.md; workflow_lint.py (38-44, 70-145); sop_currency.py (60-115); .githooks/commit-msg;
             the git-hooks dir; jira_feed.py (1078-1110, 3516-3697); fourteen test files; families.json;
             permission_render.py, claude_permissions_apply.py, check_maps.py, refresh_maps.py, risk_seam.py;
             port-checklist.md; the command files and both code-review-engine docs; .gitmodules;
             Projects/sudo-command-center; the SOP, quickref, autopilot_bmad_dev_loop.md, INDEX.md,
             tea_deep_reference.md, propagate-autopilot-glm-hybrid.md, new_machine-migration-guide.md
verdict:     findings below
```

```
lens:        3 Pre-Mortem (bounded: attaches narratives, originates nothing)
checks_run:  for each surviving anchored finding, the silent-failure / other-machine / fresh-clone /
             sibling-lands-first narrative
read:        the survivors of lenses 1 and 2 only
verdict:     three narratives attached (below the table); no unattached output
```

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/scripts/claude_permissions_apply.py:32,131` (x2) | `⛔ IT NEVER TOUCHES \`sandbox.excludedCommands\`` and `assert excluded_before == excluded_after, "excludedCommands must never change here"`, pinned by `test_claude_permissions_apply.py:90`; `families.json` has no such row shape | the first draft's row A observable and its `families.json` EDIT named a mechanism that refuses by design and by test, and leaned on a key the operator ruled useless on 2026-09-05 (about approval prompts, a different problem from network egress) | **blocker - resolved**: the edit is gone; Step 1 item 3 MEASURES reachability and names three remedies, the choice his (Ask-First 2) |
| `.agents/scripts/tests/test_review_engine.py:68,90,1258,1370` · `test_twin_parity.py:155-156,333` · `test_settings_allowlist.py:183,194` (x2) | `AP_CMD = ".agents/commands/cicd-code-review-AP.md"` in `CALLER_FILES`; `A0c every NOT_PAIRED row names a command that still exists`; `ap_platforms = _declared("cicd-autopilot-opencode.md")` reading the file unguarded | Step 7's `git rm` turns three suite files red (one by `FileNotFoundError`, two by named checks) and orphans the `capped` row in both code-review-engine docs, so `gate_receipt.py` fails at the tip | **blocker - resolved**: all five files are declared and edited in the same commit (Step 7's table) |
| `.agents/rules/port-checklist.md:29-38` + `docs/workspace-standard.md:253-260` | `Both copies differ → every check below is due, and the plan carries a section answering them`; the target is `the **published teaching edition** of this lobby - a sanitized export, never edited in place` … `**no** - it is a mirror` | nine declared files exist in a second registered repo and six differ; a plan with no port section fails a hard gate | **blocker - resolved**: `## Port check` answers it with the disposition and its evidence |
| `implementation_plan.md` (first draft) vs `claude_permissions_apply.py --help` | `usage: … [--status] [--apply] [--prune] …`; `--check` belongs to `permission_render.py:26` | Step 1's first command would exit 2 on an unrecognized argument | important - resolved (`--status`) |
| `.agents/rules/lobby-search.md:2` | `name: lobby-search` - it is a **rule**, and no door or skill of that name exists | the spike's ten launches would invoke a door that does not exist, and Table 4 would have no skill to preload | important - resolved: a real `.claude/skills/` entry (`smh-memory-audit`) and a fixed trivial prompt |
| `claude --help` on 2.1.258 | `--max-budget-usd` is listed; **`--max-turns` is not**, and `--append-system-prompt-file` appears only inside `--bare`'s description text | two flags the runner's stability test would pin are unconfirmed on the installed CLI | important - resolved: Step 1 item 1 probes both after the upgrade; an absent flag is dropped before any test pins it |
| `workflows_testing_SOP.md:278` vs `:2925,:3974,:3988,:4426` | `## 3. The two laws above every command` contains no autopilot text; the rows live in §15, §18 and the *Not in your menu* table | row G's SOP observable was vacuously true before any deletion, and row E sent the builder to a section with no command table | important - resolved: the real sections are named, and the hand-mirrored quickref is edited with them |
| `.agents/scripts/tests/test_check_maps.py:161-163` | `F2 the live _artifacts tree reports no MISSING rows … add the INDEX row before closing out` | two new lane folders with no `_artifacts/_main/INDEX.md` row turn the lane-tip suite red and the close-out gate refuses | important - resolved: the INDEX edit is declared |
| `.agents/.sync-manifest.json:20,92` + `git ls-files` | `"cicd-autopilot-deepseek4"` under `.claude\skills`, `"cicd-autopilot-opencode.md"` under `.opencode\commands`, both tracked; `Invoke-ManifestPurge … Remove-Item $f -Force` | the sync deletes two tracked launchers and rewrites the manifest, so the diff carries seven `D` rows, not the five row G claimed | important - resolved: the four sync outputs are declared and row G says seven |
| `docs/_scc_sops_prds/autopilot_bmad_dev_loop.md:58-61` (20 hits) + quickref `:422,:1306-1323` + `tea_deep_reference.md:605` + `new_machine-migration-guide.md:439` + `.agents/commands/INDEX.md:29-30,74` | `Stage 1  Plan … /cicd-dev-story-tests-AP plan`; `AP["/cicd-autopilot-claude\nStage 4 = /cicd-code-review-AP"]` | the autopilot **reference** doc and four other live pages would keep describing a deleted lane | important - resolved: every one is named in Step 7 and declared |
| `.agents/scripts/workflow_lint.py:124` | the code-standards pointer triggers on the literal `\bNO-GO\b`, which the charter table contains | the rewritten door would exit 2 on the lint unless it cites `code-standards.md` | important - resolved: Step 5 says so |
| `sync-agents.ps1:776` + `test_zoo_team.py:439` | `Get-Content $src -TotalCount 12` and `splitlines()[:12]`, matching `^mode-name:` and `^mode-groups:` | six new frontmatter keys placed above `mode-name`, or written as a block list, silently drop the seat from `.roomodes` | important - resolved: Step 3 pins them single-line below `mode-groups` and re-runs the sync |
| `.agents/scripts/tests/test_jira_start_hook.py:58-60` | `for rel in (".agents/scripts/jira_feed.py", ".agents/scripts/wf_common.py", …)` - "The production files, copied - not re-implemented" | a `step` verb importing a new sibling module breaks `jira_feed.py start` inside that fixture | minor - resolved: Step 4 pins `step` as self-contained |
| the first draft's change set | `NEW …/tickets/SCC-429.md` and `NEW …/tickets/brainstorm-history-scc-208.md`, neither named by an acceptance row | Scope Ledger: an artefact no row requires | minor - resolved: row A's proof now names the design record and its two ticket files, which is what makes this plan's citations resolve |

### Lens 3 - Pre-Mortem narratives (attached to the findings above, originating nothing)

- **The silent one, on the sandbox finding.** Shipped as first drafted, the builder edits `families.json`, runs the
  apply, sees exit 0 and a clean report - because the tool deliberately ignores that key - and concludes the runner
  is excluded. The first real run's children fail to reach the model one at a time, each looking like a model
  outage rather than a settings no-op. The measurement in Step 1 is what makes that failure loud on day one.
- **The other-machine one, on the frontmatter finding.** The keys go in above `mode-name` on the PC, the suite is
  green (nothing tests the window from the Claude side), and the operator opens Zoo on the Mac the next morning to
  find the mode picker missing seats - a regression with no failing test and no obvious cause.
- **The sibling-lands-first one, on the manifest.** Both lanes run `/smh-sync-agents`, so `.agents/.sync-manifest.json`
  conflicts by construction. Hand-merging it produces a manifest that describes neither tree, and the next sync
  purges the wrong files. Both plans now say: re-run the sync on the rebased tip, never hand-merge.

### Observations (uncounted)

- The three `-AP` twins have no launchers on any surface, so row G's "purged on every surface" is a no-op for them
  and `-Status` shows no orphan trivially. Only the deepseek and opencode launchers are real deletions.
- `risk_seam.py classify` returns `{"status": "unclassified", "root": "/home/dlohn/Sudo_Hatter_Command"}` - correct
  and permanent in the command centre (SCC-289, it parses code and this repo is markdown). Every judgement above
  came from the diff and the tests.
- No parser rejects unknown frontmatter keys: `test_zoo_team.py:154-167` accepts any `k: v`, nothing runs
  `yaml.safe_load`, and `workflow_lint.py:41-44` errors only on `platforms: []`. Values must avoid an unquoted `: `.
- `_artifacts/_main/2026-09-07_autopilot-v3-design/` is byte-identical in the lobby and on this branch. After this
  lane merges, the lobby's untracked copy vanishes cleanly; the INDEX row this lane commits is the one that stands.
- One dangling Markdown link into a delete target exists in a 2026-08 walkthrough. `check_links.py` is diff-scoped,
  so it stays amber history rather than a gate break.
- `pwsh` is at `/usr/bin/pwsh`, so `/smh-sync-agents` runs on this WSL box; it writes `.claude/skills`, a
  sandbox-denied path, so that one run is sandbox-off.
- `.claude/worktrees/scc-386-memory-long-term-only` is a stale plain directory, not a registered worktree. Unrelated
  to this lane; flagged so nobody treats it as a live sibling.

### Landing-order dependency

`git worktree list` shows the lobby and both new lanes, all at `d70347ba` with zero commits ahead. The overlap with
SCC-431 is by declaration, not by diff: `smh-team-march-hare.md` (frontmatter here, body there),
`.agents/scripts/INDEX.md`, `_artifacts/_main/INDEX.md`, `.agents/.sync-manifest.json`, the SOP and its changelog,
plus SCC-431's import of `jira_feed.py step`. **This lane lands first**, which is also the operator's stated order.

Audit verdict: GO

**Batch approval (2026-09-07):** "approved scc-430" — covers the plans listed in `/smh-plan-task SCC-429`
Step 5: **SCC-430**, and only that one. SCC-431 was deliberately left out of the operator's words; its gate
stays armed and that lane stops for its own approval. This plan as it stood at `001d6e78`, carrying
`Audit verdict: GO` at that commit — recorded at `<pending>`.

**Ask-First item 1 answered (2026-09-07):** "yes for the cli upgrade" — the operator's word for the Claude
CLI upgrade to >= 2.1.259. Measured on PATH before asking: `2.1.258`, with `--max-turns` and
`--append-system-prompt-file` absent from `--help`. Step 1 item 1 re-probes both after the upgrade and
drops any flag that still does not print.
