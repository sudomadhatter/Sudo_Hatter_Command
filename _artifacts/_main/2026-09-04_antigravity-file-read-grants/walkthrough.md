# Walkthrough — Antigravity file-read grants (SCC-387)

**Date:** 2026-09-04 · **Lane:** `chore/SCC-387-antigravity-read-grants` · **Cut from:** `main` @ `391bc26c`
**Ticket:** [SCC-387](https://sudo-command.atlassian.net/browse/SCC-387) · **Plan:** [implementation_plan.md](implementation_plan.md)

## What was wrong

Antigravity kept asking for permission every time it read one of the Claude memory files, and the
operator's "always allow" clicks were not making it stop.

Two separate reasons, both measured on the live store at `~/.gemini/config/config.json`:

**A click buys one file.** The store held `allow` 122 = 58 `command` + 59 `unsandboxed` + **5
`read_file`**. All five `read_file` rows were full resolved paths written by clicks on 2026-09-03,
each naming exactly one file under
`/home/dlohn/.claude/projects/-home-dlohn-Sudo-Hatter-Command/memory/`. Nothing about a click
generalises — the next memory file asks again. (This also corrects a claim the door and the guide
both carried: the click does **not** write a prefix.)

**The next apply would have erased them.** `antigravity_permissions_apply.py` writes
`us[KEY] = {"allow": [...], "deny": [...]}` — it REPLACES both arrays with the rendered ones, it does
not merge. The tracked source had no `read_file` row anywhere, and `permission_render.py:142` emitted
exactly two rule kinds, `command(` and `unsandboxed(`. So a routine apply would have silently deleted
all five grants and restarted the asking, with nothing in any gate to notice.

## The vendor fact the fix rests on

Read first-party 2026-09-04, https://antigravity.google/docs/permissions:

> `read_file(/path)`, `read_file(dir)`, or `read_file(*)` — "Match absolute paths or paths relative to
> project workspace roots. **Grants recursive read access to all contained files/folders.**"

Cross-checked against the shipped matcher rather than taken on trust: `~/.gemini/bin/agy` (the
language server, v1.2.0) carries the literal grant formats `read_file(%s)`, `write_file(%s)`,
`execute_url(%s)` and `mcp(*)`, the hardcoded grants `read_file(/)` and `read_file(*)`, and the
routines `permissions.isFilePathAllowed`, `matchesAllowedPath` and `isPathCovered`. Path coverage,
not the per-token anchored regex a command rule gets.

So a file target is a **path**, and a **directory is recursive** — one folder row retires all five
clicks and every future one.

## What changed

| File | Change |
|---|---|
| [`.agents/permissions/families.json`](../../../.agents/permissions/families.json) | One new allow row, `allow-read-claude-memory-wsl`: `grant: "read_file"`, `cmd` = the memory FOLDER, `only: ["antigravity"]`. `_doc` says what the new field means. |
| [`.agents/scripts/permission_render.py`](../../../.agents/scripts/permission_render.py) | `GRANTS`/`_grant()`; `_validate_source` refuses an unknown grant kind by row name; Zoo and Claude derive nothing for a file row; Antigravity emits one bare `read_file(<dir>)`, unescaped, with no twins. |
| [`.agents/permissions/antigravity.json`](../../../.agents/permissions/antigravity.json) | Rendered: one `read_file(...)` row added. |
| [`.agents/commands/smh-llm-approvals.md`](../../../.agents/commands/smh-llm-approvals.md) | Step 1 splits store-only rows into commands and FILES and stops calling a path a command; the "click writes a PREFIX" claim is corrected to the measured truth; Step 2's example shows the second group; Step 3 routes a picked file as its FOLDER with the narrowness warning about `~/.claude/projects`; the apply is flagged as a REPLACE that drops unpicked rows. Opencode mirror refreshed byte-identical. |
| [`docs/migrations/terminal-permissions-guide.md`](../../../docs/migrations/terminal-permissions-guide.md) | §3A.2 is now **three** rule types, with the file-rule paragraph, the vendor quote and the binary cross-check. §7's "Three residuals" corrected to Five — it had listed five for some time. |
| [`.agents/scripts/tests/test_permission_parity.py`](../../../.agents/scripts/tests/test_permission_parity.py) | A15, B2c, B10e, B10f (below). |

### The pins, and what each would catch

- **A15** — the shipped fence grants the memory store as a **directory** (no `*`, no trailing slash),
  and no `read_file` row ever lands in the deny array. Catches a regression to per-file grants.
- **B2c** — a typo in `grant` (`"read"` for `"read_file"`) is refused **by row name**. Without it a
  typo falls through to command derivation and renders a bare filesystem PATH as an allowed command
  prefix on all three platforms.
- **B10e** — a file row renders as exactly `["read_file(/dir)"]` on Antigravity and `[]`/`[]` on Zoo
  and Claude. Catches twins, escaping, or leakage into the command fences.
- **B10f** — the same holds **without** `only: ["antigravity"]`. The derivation, not the scope, is
  what keeps a path out of the command lists; a row written by hand without the scope must still be safe.

## Evidence

```
python3 .agents/scripts/tests/test_permission_parity.py     -- 62/62 passed --
python3 .agents/scripts/permission_render.py --check        permission_render: in sync (zoo, claude, antigravity)
python3 .agents/scripts/tests/run_all.py                    70/72 files passed
```

Both `run_all.py` reds are pre-existing and environmental, neither touched by this lane:

- `test_check_maps.py` **F2** wanted the `_artifacts/_main/INDEX.md` row for this lane's own folder —
  the close-out step. **Fixed in-lane; re-run green.**
- `test_sops_prds_folder.py` **T9** resolves a prose reference to `docs/.maps-journal.jsonl`, which is
  **gitignored** (`.gitignore:23`). It exists only in the checkout that generated it, so this row is red
  in every fresh worktree and green in the main checkout. Not a defect of this change.

## Your Actions

1. **Apply and reload.** `python3 .agents/scripts/antigravity_permissions_apply.py --apply`, then reload
   the VS Code window. ⛔ Before you do: that apply **drops the 6 rows your clicks wrote** — the 5 memory
   files (replaced by the folder row, so nothing is lost) and `unsandboxed(find ~/.claude -name "*.md" …)`,
   which was **already dead** — its `"*.md"` token is not a valid regex for its own text, so it has been
   returning `ask` since the moment it was written. If you want that `find` allowed for real, run
   `/smh-llm-approvals` and pick it; the renderer escapes the glob so the rule actually matches.
2. **Confirm it worked.** Open a memory file Antigravity has never read before. It should not ask.
3. **The Mac row is SCC-382's.** This grant is one absolute path, so it is machine-scoped by construction;
   the Mac's own store path is a second row in that lane.
