# Implementation Plan — harvest the machine-local Claude allow list (SCC-392)

**Date:** 2026-09-04 · **Lane:** `_artifacts/_main/2026-09-04_claude-approvals-harvest/`
**Branch:** `chore/SCC-392-claude-approvals-harvest` (cut from `origin/main` @ `78f47333`)
**Parent subject:** SCC-378 (permission parity) · SCC-387 (file-read grants)

## The problem, measured on this machine

`/smh-llm-approvals` treats the three agents asymmetrically, and only one of the three is treated
correctly.

For **Antigravity** it diffs the live machine store against the tracked render and shows what
exists only on this machine — that is what surfaces a click-written grant so it can be routed into
the source and travel. For **Claude Code** it reads chat transcripts for commands that were
*refused*, and never looks at where Claude's approvals are actually *kept*. So a row the operator
granted from the terminal chat is invisible to the door, stays on the machine it was clicked on,
and never reaches the other one.

Measured 2026-09-04:

| List | Rows | Travels? |
|---|---|---|
| `<repo>/.claude/settings.json` — rendered from `families.json` | 140 | yes, it is tracked |
| `~/.claude/settings.json` — user scope | 82 | **no**, it is outside the repo |
| `<repo>/.claude/settings.local.json` — project scope | absent here | **no**, `.gitignore:58` |

65 of the 82 user-scope rows are already covered by the tracked list. **17 are not**, and would
simply not exist on the Mac:

```
acli:*  bash:*  chmod:*  gh:*  jq:*  mv:*  node:*  npm:*  npx:*  pytest:*
python:*  python3:*  rsync:*  sed:*  sh:*  touch:*  env -u GITHUB_TOKEN gh:*
```

There is no way to see that number today short of running the set difference by hand, which is the
gap this lane closes.

## The change — one script, one door, one page

### 1. `.agents/scripts/claude_permissions_status.py` (new, read-only)

Mirrors `antigravity_permissions_apply.py --status` in shape and vocabulary, minus the apply —
**Claude has no apply and must not grow one.** Its rendered file IS the live file: Claude Code
reads `<repo>/.claude/settings.json` directly, so a rendered row is in force the moment it is
saved. Nothing needs pushing into a store and nothing can be replaced or lost.

```
python3 .agents/scripts/claude_permissions_status.py            # report, exit 0 either way
```

Resolves three paths (never hardcoded beyond `Path.home()` and the repo root, so it is correct on
Mac and PC alike), reads `permissions.allow` from each, and prints one status line plus the
local-only rows. An absent local file is **empty, not an error** — the normal state on a fresh
machine, exactly as an empty Zoo store already is in this door.

⛔ Reports `allow` only. The door's standing law is that it never reads or writes any deny list,
and a status report that surfaces deny rows invites exactly the edit the law forbids.

### 2. `.agents/commands/smh-llm-approvals.md` — three edits

**Step 1** gains the Claude store diff beside the transcript read, with its own paragraph: the two
machine-local files by name, the script that diffs them, and the plain statement that a row living
only there does not reach the other machine.

**Step 2** gains a fourth group in the example, under its own heading, so harvested rows are never
mixed in with commands that stopped and asked — they are the opposite thing, commands that stopped
asking.

**Step 3** gains the one warning this specific source needs. A harvested row is already a *rule*,
not a command, so the existing narrowness law ("a rule is only ever as wide as the command it came
from") has nothing to measure it against. `bash:*` and `sh:*` are on the live local list right now
and each one permits any command at all. The door must show such a row for what it is and get the
operator's word out loud before it is written into the shared source, because unlike a local row it
would then land on **both** machines. It must not silently narrow it either — this door does not
compute prefixes (SCC-354).

⛔ And the warning that must NOT be copied here: the Antigravity apply REPLACES both arrays, so
that path carries a data-loss caveat. Claude's has none. Stating one anyway would be a threat that
does not exist, and the door says so explicitly so it is not cargo-culted later.

### 3. `.opencode/commands/smh-llm-approvals.md`

Byte-identical mirror, refreshed. Pinned by the existing E4 check.

### 4. `docs/_scc_sops_prds/workflows_testing_SOP.md` (+ changelog)

Usage surfaces changed (`.agents/commands/`, `.agents/scripts/`), so the SOP moves in the same
commit or the armed `sop_currency` gate rejects it. **§13 — *What does NOT travel between the
machines*** — gains a **Claude Code's approval lists** row beside Zoo's and Antigravity's; that
section is literally about this problem and was the one agent missing from it. (An earlier draft of
this plan said "§5's script inventory"; §5 is *Which lane am I in?* and carries no inventory — the
§13 table is the right home, and the scripts inventory that DOES exist is `.agents/scripts/INDEX.md`,
declared above.) The `/smh-llm-approvals` prose and the "tired of approving" quick-reference row gain
the Claude half. One changelog line.

## Declared Change Set

- NEW `.agents/scripts/claude_permissions_status.py` — the read-only diff of the two machine-local Claude lists against the tracked one; no apply, ever → 1
- EDIT `.agents/commands/smh-llm-approvals.md` — Step 1 reads both machine-local files, Step 2 shows them as their own group, Step 3 stops on a blank-cheque row → 2
- EDIT `.opencode/commands/smh-llm-approvals.md` — the opencode door is a FULL byte-identical MIRROR of the command body (pinned by E4); no `pwsh` here to regenerate it, so it is copied in the same commit → 3
- EDIT `.agents/scripts/tests/test_permission_parity.py` — the G block (G0–G8) and E6/E7/E8 → the assert-first section
- EDIT `.agents/scripts/INDEX.md` — one row for the new script, the convention every script in that folder follows → 1
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — §13 gains a **Claude Code's approval lists** row beside Zoo's and Antigravity's; the `/smh-llm-approvals` prose, the quick-reference row and the command-table row gain the Claude half → 4
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one line → 4
- EDIT `_artifacts/_main/INDEX.md` — this lane's row → 4
- NEW `_artifacts/_main/2026-09-04_claude-approvals-harvest/walkthrough.md` — evidence, review, actions → the definition of done
- NEW `_artifacts/_main/2026-09-04_claude-approvals-harvest/tickets/SCC-392.md` — the ticket outline → the definition of done
- NEW `_artifacts/_main/2026-09-04_claude-approvals-harvest/gates/suite.json` — the suite receipt → the definition of done

⛔ **Not declared, and deliberately never touched:** `~/.claude/settings.json`, `<repo>/.claude/settings.local.json`,
`.claude/settings.json`, `.vscode/settings.json`, `.agents/permissions/antigravity.json`,
`.agents/permissions/families.json` and `permission_render.py`. This lane closes a DISCOVERY gap; no
row is harvested here, so the rendered lists are byte-identical to `main` and the renderer needs no
change. A harvest is the operator's next `/smh-llm-approvals` run.

## Assert first — what proves it, before it is written

New rows in `.agents/scripts/tests/test_permission_parity.py`, against the real module:

- **G-series (the script, on synthetic inputs — no dependence on this machine's live files)** — the
  block letter is `G`; `C` is the Antigravity-apply block and `B` the Zoo seats:
  a row present locally and absent from the render is reported; a row present in both is not; an
  absent local file counts as empty rather than raising; a deny row is never reported even when
  local and render disagree on it.
- **E6 / E7 / E8 (the door's body):** it names both machine-local Claude stores; it states that
  Claude has no apply and that nothing is deleted; it carries the wildcard-shell caveat.

Then the full suite: `python3 .agents/scripts/tests/run_all.py`.

## Out of scope, deliberately

- **No edit to `~/.claude/settings.json` or `settings.local.json`, ever.** The door reads them.
  Removing a now-redundant local row is the operator's own edit to ask for by name.
- **No deny-list surface**, per the door's standing law.
- **No change to `permission_render.py`** — the rendering side already works; the gap is discovery.
- **No Zoo equivalent.** Zoo's decisions live in a SQLite `globalState`, already handled by
  `zoo_permissions_apply.py`; whether it has the same blind spot is a separate question and a
  separate lane, not a widening of this one.

## Definition of done

`run_all.py` green · `permission_render.py --check` in sync · the script's report reproduces the
17-row figure above on this machine · the door and the SOP both read correctly to someone who was
not in this session · review verdict recorded, then the PR.
