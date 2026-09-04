# Walkthrough — harvest the machine-local Claude allow list (SCC-392)

**Date:** 2026-09-04 · **Lane:** `chore/SCC-392-claude-approvals-harvest` · **Cut from:** `main` @ `78f47333`
**Ticket:** [SCC-392](https://sudo-command.atlassian.net/browse/SCC-392) · **Plan:** [implementation_plan.md](implementation_plan.md)

## What was wrong

`/smh-llm-approvals` treated the three agents asymmetrically, and only one of the three was treated
correctly.

For **Antigravity** it diffs the live machine store against the tracked render and shows what exists
only on this machine. That diff is the whole mechanism by which a click-written grant becomes
something that travels: the door sees it, the operator names it, it lands in the one source, and the
renderer puts it on both machines.

For **Claude Code** it read chat transcripts, pairing an `is_error` refusal back to the Bash
`tool_use` that earned it. That finds commands which **stopped**. It cannot find the ones that
stopped *asking*, because an approval granted from a terminal chat is written to no transcript — it
is written to one of two machine-local files:

| List | Rows | Travels? |
|---|---|---|
| `<repo>/.claude/settings.json` — rendered from `families.json` | 140 | yes, it is tracked |
| `~/.claude/settings.json` — user scope | 82 | **no**, it is outside the repo |
| `<repo>/.claude/settings.local.json` — project scope | absent here | **no**, gitignored at `.gitignore:58` |

Measured on the WSL box 2026-09-04: 65 of the 82 user-scope rows were already covered by the tracked
list, and **17 were not**. Those 17 decide on this machine and nowhere else — the Mac goes on asking
for every one of them — and nothing in the door, the renderer or any gate could see that number
short of running the set difference by hand.

```
Bash(acli:*)   Bash(bash:*)   Bash(chmod:*)   Bash(gh:*)    Bash(jq:*)     Bash(mv:*)
Bash(node:*)   Bash(npm:*)    Bash(npx:*)     Bash(pytest:*) Bash(python:*) Bash(python3:*)
Bash(rsync:*)  Bash(sed:*)    Bash(sh:*)      Bash(touch:*)  Bash(env -u GITHUB_TOKEN gh:*)
```

## One thing checked before the diff was trusted

The tracked list and the user list do not have to use the same rule spelling, and a set difference
over two grammars would over-report every row as machine-local. Measured before building anything:
the tracked list is 75 colon-form rows (`Bash(cd:*)`), 9 space-form (`Bash(git checkout *)`) and 56
literals; the user list is 66 / 6 / 10 in the same three shapes, and the forms that appear in both
files match exactly. `Bash(git checkout *)` is present in the tracked list in that spelling, not a
colon variant. So a plain set difference is honest here, and the 17 are genuinely absent rules rather
than the same intent written another way.

## The change

### `.agents/scripts/claude_permissions_status.py` — new, read-only

Shaped like `antigravity_permissions_apply.py --status` in vocabulary and argument surface, minus the
apply. It resolves all three paths from `Path.home()` and the repo root, so it is correct on the Mac
and the PC without a hardcoded path, reads `permissions.allow` from each, and prints one status line
plus the rows the tracked list does not carry. On this machine:

```
status  : MACHINE-LOCAL allow rows: 17 (settings.json=17) - they decide on this machine only
```

Three properties are load-bearing rather than incidental.

**There is no apply, and there must never be one.** Antigravity's store is a separate file the
extension reads at startup, so a rendered fence has to be pushed into it; Claude reads
`<repo>/.claude/settings.json` directly, so a rendered row is in force the moment the file is saved.
There is nothing to push into and nothing that can be replaced or lost. That absence is pinned by a
test rather than left to a comment (G8): the module exposes no `apply`, the code contains no write
call and no `--apply` flag.

**It reports `allow` only.** The door's standing law is that it never reads or writes any deny list.
A status report that surfaced deny rows would invite exactly the edit that law forbids, so the
reader never sees one (G4).

**An absent file counts as empty, not as an error.** `settings.local.json` does not exist on this
machine and normally does not exist anywhere — the same status an empty Zoo store already has in this
door, and it must not read like a failure (G3).

### `.agents/commands/smh-llm-approvals.md` — three edits

**Step 1** gains the Claude store diff beside the transcript read, naming both machine-local files and
the script that diffs them, and stating plainly that a rule living only there reaches no other
machine.

**Step 2** gains a fourth output group under its own heading. Harvested rows are not commands that
stopped; they are rules that already stopped asking, and the question about them is not *may I run
this* but *should this travel*. Folded into the list above they lose that distinction.

**Step 3** gains the one caveat this particular source needs. The existing narrowness law reads *a
rule is only ever as wide as the command it came from* — but a row lifted out of
`~/.claude/settings.json` did not come from a command, so that law has nothing to measure it against.
Two rows on the live list, `Bash(bash:*)` and `Bash(sh:*)`, permit any command at all. Locally that is
the operator's call on a machine he is watching; promoting one into the source is a different act,
because it then renders to both machines. The door shows the row for what it is and takes his word out
loud — and does not narrow it for him, because this door does not compute prefixes (SCC-354).

And one warning is explicitly **barred**: the Antigravity apply REPLACES both arrays, which is why
that path carries a data-loss caveat. Claude's path has none. The door says so in the negative, so the
caveat is not cargo-culted across later by someone reading the two paragraphs side by side.

The "what this command does NOT do" list gains the read-only law: the two machine-local files are
read and never edited. Deleting a now-redundant row from `~/.claude/settings.json` is the operator's
own edit to ask for by name.

### `.opencode/commands/smh-llm-approvals.md`

Refreshed byte-identical, as E4 requires.

### `docs/_scc_sops_prds/workflows_testing_SOP.md` (+ changelog)

Usage surfaces changed, so the SOP moves in the same commit or the armed `sop_currency` gate rejects
it. §13 *What does NOT travel between the machines* gains a **Claude Code's approval lists** row
beside Zoo's and Antigravity's — that section is literally about this problem, and it was the one
agent missing from it. The `/smh-llm-approvals` prose gains a paragraph on the second half of Claude
and a paragraph on the blank-cheque stop; the existing Antigravity data-loss caveat is now scoped to
Antigravity in the operator's own page as well as in the door. The quick-reference row and the command
table row both gain the Claude half. One changelog line.

## Assert first — what was pinned before it was written

Nine new rows for the script, on synthetic inputs in a tempdir, so nothing depends on this machine's
live files; three for the door's body.

| Row | What it refuses to let happen |
|---|---|
| G1 / G2 | A local-only row silently dropped from the report, or a shared row reported as local |
| G3 | An absent `settings.local.json` raising instead of counting as empty |
| G4 | A deny row reaching the operator's eyes, against the door's standing law |
| G5 / G6 | A `status()` hard-wired to one answer — it is seen saying both (the lesson C6 records for the sibling script) |
| G7 | A missing tracked list passing silently instead of exiting 2 |
| G8 | An apply growing here later, which could only destroy |
| E6 / E7 / E8 | The door losing the store names, the no-apply statement, or the blank-cheque caveat |

G8 was seen red first, for the right reason and then the wrong one: its first spelling scanned the
whole file for `--apply`, and the module **docstring states the law** ("there is NO `--apply`"), so
the check read its own law as a breach. It now scans the code with the docstring removed.

## Evidence

```
python3 .agents/scripts/tests/test_permission_parity.py        -- 74/74 passed --
python3 .agents/scripts/permission_render.py --check           permission_render: in sync (zoo, claude, antigravity)
python3 .agents/scripts/claude_permissions_status.py           MACHINE-LOCAL allow rows: 17 (settings.json=17)
python3 .agents/scripts/tests/run_all.py                       70/72 files passed
```

`run_all.py`'s two reds are pre-existing and neither is in this lane's radius:

- **`test_check_maps.py` F2** — `_artifacts/_main/INDEX.md` was missing this lane's own row. **Fixed
  in the lane**; it is this lane's bookkeeping.
- **`test_sops_prds_folder.py` T9** — `file_folder_structure+maintaining.md` cites
  `docs/.maps-journal.jsonl`, which is gitignored (`.gitignore:23`) and exists only in the main
  checkout, so it resolves nowhere from any worktree. Proved rather than assumed: the same test run
  in the main checkout with `--on-main` passes 61/61. Environmental, not a defect, and not mine.

## What is live now

The script and the door are live in this lane. Nothing was pushed into any machine store, because
Claude has none — the tracked `.claude/settings.json` is unchanged by this lane, since no row was
harvested yet. The harvest itself is the operator's next `/smh-llm-approvals` run, where the 17 rows
will appear as their own group and he picks which ones travel.
