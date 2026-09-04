# Implementation Plan — Antigravity file-read grants (follow-on to SCC-378)

**Date:** 2026-09-04 · **Lane:** `_artifacts/_main/2026-09-04_antigravity-file-read-grants/`
**Parent subject:** SCC-378 (permission parity, merged @ `391bc26c`)

## The problem, measured on the live store

`~/.gemini/config/config.json` right now: `allow` 122 = 58 `command` + 59 `unsandboxed` + **5 `read_file`**.
Those five were written by the operator's "always allow" clicks tonight, one per file, all under
`/home/dlohn/.claude/projects/-home-dlohn-Sudo-Hatter-Command/memory/`. Antigravity auto-allows reads
**inside** the workspace and asks for everything outside it; the Claude memory store is outside it.

Two consequences the fence does not currently survive:

1. **A click buys one file.** The stored row is the exact resolved path, so the next memory file asks again.
2. **The next apply erases them.** `antigravity_permissions_apply.py` writes
   `us[KEY] = {"allow": [...], "deny": [...]}` — it REPLACES both arrays with the rendered ones
   (`antigravity_permissions_apply.py:69`). The source has no `read_file` row anywhere, so a routine
   `--apply` silently deletes all five grants and the asking starts over.

## The vendor fact that decides the fix

Read first-party 2026-09-04, https://antigravity.google/docs/permissions:

> `read_file(/path)`, `read_file(dir)`, or `read_file(*)` — "Match absolute paths or paths relative to
> project workspace roots. **Grants recursive read access to all contained files/folders.**"

Confirmed against the shipped matcher: `~/.gemini/bin/agy` carries the literal grant formats
`read_file(%s)`, `write_file(%s)`, `execute_url(%s)`, `mcp(*)`, and hardcoded `read_file(/)` /
`read_file(*)`, alongside `permissions.isFilePathAllowed` / `matchesAllowedPath` / `isPathCovered`.

So a **directory** grant is recursive. One row replaces all five clicks and every future one.

## The change — four small pieces, no renderer surgery

1. **`.agents/permissions/families.json`** — ONE new allow row, scoped `only: ["antigravity"]`, with an
   explicit `render.antigravity` of `read_file(<memory dir>)`. The source already supports both
   platform scoping and explicit per-platform renders, so `permission_render.py` needs **no change**:
   an explicit render is emitted verbatim and never passes through `_derive_antigravity`, so it grows
   no `command(`/`unsandboxed(` twins and no `cd .* && ` house twin (that twin is denies-only).
2. **`.agents/commands/smh-llm-approvals.md`** — Step 1 currently strips only `unsandboxed(`/`command(`
   and calls every store-only row "a command the operator had to stop for"; a file path is neither.
   Show `read_file(` rows as their own group. Step 3 routes a picked one into the source as a
   **directory** row, never the single file that asked. Fix the stale sentence claiming the click
   records "a PREFIX" — measured tonight, it records the full resolved string.
3. **`docs/migrations/terminal-permissions-guide.md`** — §3A gains a File rules paragraph with the
   vendor citation and the recursive-directory rule; §7's residual list drops the read_file gap.
4. **`.agents/scripts/tests/test_permission_parity.py`** — two rows: the read family lands in
   `antigravity.json` and stays out of `.vscode/settings.json` and `.claude/settings.json`; and the
   five paths the operator clicked are all covered by the single directory grant.

## The one judgment call — how wide the read grant is

**Recommendation: the memory folder of this project only** —
`read_file(/home/dlohn/.claude/projects/-home-dlohn-Sudo-Hatter-Command/memory)`.

That is exactly as wide as the five commands it came from, which is the narrowness law this door
already runs on. The wider row, `read_file(/home/dlohn/.claude/projects)`, would also cover every
session transcript — convenient, and the thing `/smh-llm-approvals` itself reads, but it hands
Antigravity every word of every Claude session on this machine. Not a width to take by default.

## Done looks like

- `permission_render.py --check` prints *in sync* for all three lists.
- `antigravity_permissions_apply.py --status` prints *in sync with tracked file*.
- `test_permission_parity.py` green, run bare, with the two new rows.
- The five click-written rows are gone from the store and the one directory row stands in their place.
- Operator action: reload the VS Code window, then open a memory file that never asked before.
