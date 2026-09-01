---
IsArtifact: true
ArtifactMetadata:
  title: Agnostic-system program — machine contract · memory routing · uniform doors — plan
  type: implementation_plan
  date: 2026-08-09
---

# Program plan — model- & machine-agnostic dev system (post-debrief hardening)

## Goal & background

Source: the 2026-08-09 debrief of the failed Codex session, plus operator rulings in this
conversation. Three verified findings drive three lanes:

1. **Close-out targeting is still inference.** `task_preflight.py` accepts a defaulted repo/branch
   and verdicts honestly about the wrong lane. SCC-61 pinned this at the prompt level; the machine
   enforcement (an intent input the script can assert against) is still owed. Verified: its only
   args today are `--repo / --branch / --fetch / --json`.
2. **Memory is readable by every model but routed to none of them.** `_artifacts/_memory/` (145
   tracked files, index 19,254 B) is plain markdown in the repo, but only Claude's harness injects
   `MEMORY.md`; AGENTS.md never names the path. The `~/.claude/...` symlink is per-machine plumbing.
3. **The command surface is non-uniform.** 55 command bodies, 19 `.claude/commands/` mirrors, 14
   hand-made launcher skills, ≥5 names with double doors. Codex can only enter through skills.

Operator rulings (this session, binding on the plan): the system must be model- and
machine-agnostic · other models get **READ** access to memory, no new write path · one uniform door
shape for every command · memory compaction lives in `/update-maps-indexes` (propose-for-approval,
never auto-edit) · 20 KB cap on the memory index · the `/` command **naming rethink is PARKED** as a
future ticket, out of scope here.

**Shape:** three sequential lanes. Each lane: its own SCC Task (minted at lane open with a
description file), its own `chore/SCC-<n>-<slug>` branch off `main`, its own gates, closed via
`/close-task-merge-tree` (whose invocation is the per-merge sign-off). A lane merges before the next
opens — Lane 1's `--expect-key` then guards Lanes 2 and 3's own close-outs.

## Lane 1 — the machine contract (close-out targeting)

[.agents/scripts/task_preflight.py](.agents/scripts/task_preflight.py)
- New **required** `--expect-key <JIRA-KEY>`. Bare invocation exits 2 naming the flag. Assert
  key-parsed-from-branch == expect-key; mismatch exits 2 naming **both keys and both branches**.
  (`--repo`/`--branch` stay optional: a wrong default now fails the key match instead of lying.)
- **Manifest check:** if a `_artifacts/_main/*/task.yaml` with `task_key == expect-key` exists,
  assert its `branch` matches the resolved branch — mismatch is an error. No manifest = warning
  only (incremental adoption), printing the schema.
- **Dirty-tree failure names memory files separately:** untracked `_artifacts/_memory/` files get
  their own block — "another session's memory: park or leave; never sweep, delete, or commit them
  under this task."
- `gate:` block prints `workflow_lint.py --toolkit-only` when the resolved repo is the lobby.

[.agents/scripts/workflow_lint.py](.agents/scripts/workflow_lint.py)
- New `--toolkit-only`: run the lobby/toolkit checks, skip the four project checks entirely (no
  `resolve_project_root` call — root close-outs stop inheriting `.agents/active-project.txt`).

[.agents/commands/close-task-merge-tree.md](.agents/commands/close-task-merge-tree.md)
- Step 0 additionally authors `task.yaml` in the task's artifact folder if missing. Schema inline:
  `task_key`, `primary_repo`, `branch`, `close_command`, `secondary_repos: [{repo, landing,
  ticket}]` (landing values: `independent-task` | `retain-on-epic`).
- Step 1 invocation becomes
  `task_preflight.py --fetch --repo "$REPO" --branch "$BRANCH" --expect-key "$EXPECTED_KEY"`.
  The prose 🛑 header check stays as the belt over the new mechanical suspenders.

[.agents/rules/worktree-per-story.md](.agents/rules/worktree-per-story.md)
- Two lines in the existing "cwd is not intent" section: the preflight now demands the key
  mechanically; the prose guard is no longer the only thing standing there.

Tests (run_all suite, extending the existing preflight tests): missing `--expect-key` → 2 ·
branch/key mismatch → 2 · manifest/branch mismatch → 2 · manifest absent → warning · memory-file
wording present in the dirty-tree error.

SOP currency: usage surfaces move ⇒ `_my_resources/_quick_reference/sudo_workflows_testing.md`
updated in the same change (armed gate).

## Lane 2 — machine-agnostic memory

[AGENTS.md](AGENTS.md) — one routing block:
- Canonical store is the **repo path** `_artifacts/_memory/` (travels via git — machine-agnostic;
  the per-machine harness symlink is a convenience, never the mechanism).
- Every session, every platform: read `_artifacts/_memory/MEMORY.md` at start (~5k tokens); open
  full files relevant to the task.
- **READ-ONLY for all models.** Writes only through the existing sanctioned flows (Claude harness
  memory, `/sudo-update-sprint-memory`). Write law stated inline: one index line per memory ·
  update in place, never duplicate · wrong → delete (git is the undo) · closed-but-instructive →
  compress to a one-line lesson.

New memory check in the run_all suite: index ≤ 20,480 B (hard) · every index link resolves to a
tracked file · every tracked memory file has an index line · frontmatter parses. Index is 19,254 B
today — passes with ~1.2 KB headroom; new memories will force the first curation pass soon, by
design.

[.agents/commands/update-maps-indexes.md](.agents/commands/update-maps-indexes.md) — memory
reconcile step: run the same link/orphan/budget checks, **propose** retirements/merges/compressions
for approval (its existing report-before-edit contract), and assert this machine's harness symlink
resolves into the repo — flag if absent.

Env migration kit doc (locate at lane open; it exists per memory): add the symlink-creation step for
fresh machines.

SOP currency move.

## Lane 3 — uniform doors (one brain, generated doors)

**Inventory first, report before editing:** map each of the 19 `.claude/commands/` mirrors to its
`.agents/commands/` master — any orphan mirror gets a master or an explicit keep-local ruling in the
lane report. Lift the 14 hand-written launcher-skill descriptions into their command frontmatter so
nothing hand-authored is lost.

[.agents/scripts/sync-agents.ps1](.agents/scripts/sync-agents.ps1)
- Generate a launcher `SKILL.md` per command: templated body ("read
  `.agents/commands/<name>.md` … follow it END TO END") + description from the command's
  frontmatter. This one skill is the door for **Claude and Codex both**.
- Per-platform emit honors `platforms:` for skills too (Codex reads `.agents/skills/` natively;
  Claude reads the `.claude/skills/` cache — filtering requires emitting per target, not one
  unfiltered tree copy).
- **Retire `.claude/commands/` publishing**; ghost-purge the retired files via
  `.sync-manifest.json`.
- opencode + Antigravity mirrors unchanged (12k thin-launcher fallback stays).

[.agents/scripts/tests/test_command_surfaces.py](.agents/scripts/tests/test_command_surfaces.py) —
upgrade to the real assertion: **exactly one door per platform per command**, with the Antigravity
thin-launcher accepted as a valid door shape.

Two-machine note: platform caches are per-machine — PC re-sync + verification owed after the merge;
recorded as a follow-on on the ticket.

## Open questions

None blocking — every fork was ruled in-conversation. Two decisions made in this plan to flag
rather than ask: (1) `--expect-key` is strictly **required** (bare runs die loudly) instead of a
warn-first grace period; (2) orphan `.claude/commands/` files are resolved during Lane 3's
inventory with a per-file ruling in the lane report.

## Verification (exact commands, per lane — run unpiped)

```bash
out=$(python3 .agents/scripts/tests/run_all.py); rc=$?                    # N/N files passed, exit 0
out=$(python3 .agents/scripts/workflow_lint.py --toolkit-only); rc=$?     # Lane 1 onward: exit 0
out=$(python3 .agents/scripts/sop_currency.py --repo . --paths <changed>); rc=$?   # exit 0
# dogfood — each lane's own close-out runs the new contract:
python3 .agents/scripts/task_preflight.py --fetch --repo "$REPO" --branch "$BRANCH" --expect-key SCC-<n>
# Lane 3 additionally:
pwsh .agents/scripts/sync-agents.ps1                                      # exit 0
out=$(python3 .agents/scripts/tests/test_command_surfaces.py); rc=$?      # all doors, exit 0
```

Each lane ends with `/close-task-merge-tree`: merge `--no-ff` to `main`, Dev Record updated in
place, ticket → Done, `check` exit 0, branch pruned local + remote, `main` `0 0` clean.
