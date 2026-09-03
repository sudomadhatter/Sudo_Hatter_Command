---
IsArtifact: true
ArtifactMetadata:
  title: SCC-378 - one permission fence, three platforms, both machines
  type: implementation_plan
  date: 2026-09-03
---

# SCC-378 — Fence Antigravity + Gemini as a live platform: permission parity with Claude and Zoo

**Lane:** `chore/SCC-378-permission-parity` · worktree `.claude/worktrees/SCC-378-permission-parity` · base `origin/main @ ab68505e`
**Ticket:** SCC-378 (Task, `In Progress`) · child SCC-382 (the Mac application, run separately by the operator)
**Door:** `/smh-quick-dev` → `/smh-code-review` → **[STOP]** → `/smh-close-task-merge-tree`

## 1. Goal and background

Three agents run terminal commands in this shop and each has its own approval fence: Claude Code
(`.claude/settings.json`, `Bash(prefix:*)` rules, judged per command segment), Zoo Code
(`.vscode/settings.json` seeding a VS Code globalState store, lowercase prefix, longest rule wins),
and — as of the operator's reinstall on 2026-09-03 — the Antigravity extension
(`~/.gemini/config/config.json` → `globalPermissionGrants`, one anchored regex per whitespace token,
strict `Deny > Ask > Allow`). The policy those three fences encode is ONE policy — "allows are broad,
denies are the fence" (operator ruling 2026-08-30) — but it is written three times in three grammars
and nothing reconciles them. `/smh-llm-approvals` grows two of the three in step when it is the door
doing the growing; every other edit path drifts them silently, and `test_settings_allowlist.py`
pins that each list exists, never that they agree.

On 2026-09-03 the Antigravity fence was built by hand on the Ubuntu machine: 116 allow / 200 deny
rules translated from Zoo's canonical 124/105, battery green (41 destructive denied, 30 ceremony
approved, 9 unknown still asking). The generator, installer and battery are in
`_artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/agy_fence_*.py` (uncommitted, in the main
checkout). This lane makes that durable and extends the same guarantee to all three platforms.

**The goal, in the operator's words:** "keep all these in sync ... so that everything has the same
permission", on the Mac and the PC. **Restated as something checkable:** the same command gets the
same verdict on every platform, and a hand edit to any rendered list turns a test red.
**Identical decisions, never identical bytes** — the three matchers are structurally different and
byte-identical deny lists would break ceremonies on one platform or open holes on another.

### Measured facts this plan stands on (2026-09-03)

- `google.google-antigravity` v1.1.0 is installed on both the WSL side and the Windows side; the
  bundled `agy` CLI is v1.1.25 and is not on PATH. The operator drives the **extension**.
- Antigravity's store had only ever carried an `allow` key. The hand-built fence added `deny`.
  **Whether the extension honours a `deny` array in that file is unverified** — the operator's
  `git clean -fd` test after a window reload is the one fact that settles it (see §5 Q3).
- The Antigravity matcher is per-token anchored regex. Two consequences the battery caught on day
  one and a renderer must encode: flag clusters (`-fd` is one token; `-f` never matches it) and
  attached spellings (`--git-dir=/x` is one token). Zoo's prefix matcher hides both.
- `sync-agents.ps1` is PowerShell. This Ubuntu machine has no `pwsh`. Any "wire into sync-agents"
  that lives only inside the `.ps1` cannot run on the PC today.
- Sibling lane **SCC-383** (`chore/SCC-383-epic-sync-check`) has uncommitted edits to
  `docs/_scc_sops_prds/workflows_testing_SOP.md` and `_artifacts/_main/INDEX.md`. This lane edits
  both. **Landing order:** whichever lands second absorbs `origin/main` first (§4 step 0); the
  conflicts are line-local (different SOP rows, different INDEX rows) and cheap in the tree.

## 2. Acceptance — the checkable list (Step 1 of the door)

| # | Statement | Checked by |
|---|---|---|
| **A** | One battery, three matchers, identical verdicts. `test_permission_parity.py` runs bare under `run_all.py`; its destructive set is `deny` on all three platforms, its ceremony set `allow` on all three, its unknown-tool set `ask` on all three | `python3 .agents/scripts/tests/test_permission_parity.py` exit 0; the `A ·` block |
| **B** | One source, three rendered outputs, drift is red. `permission_render.py --check` exits 0 iff `.vscode/settings.json` (`zoo-code.allowedCommands`/`deniedCommands` only), `.claude/settings.json` (`permissions.allow` only) and `.agents/permissions/antigravity.json` each equal the render of `.agents/permissions/families.json`; a one-character hand edit to any of the three makes it exit non-zero. **And the seed reproduces today:** the Zoo and Claude renders are SET-equal to the tracked lists at `origin/main`, and the Antigravity render is set-equal to `agy-fence.portable.json` — this morning's hand-built, battery-green list, kept in this lane's folder as the baseline. ⚠️ AUDIT FINDING (Lens 1 Scope Ledger): that baseline file had no acceptance row requiring it; this sentence is the row | `--check` exit code, both directions, plus the three set-equality checks, pinned in the `B ·` block |
| **C** | The Antigravity apply is safe and scoped. `antigravity_permissions_apply.py --apply` against a temp store writes ONLY `userSettings.globalPermissionGrants`, preserves every other key (`remoteControlHostname` named), writes `.scc-backup` once and never again; `--status` on the live Ubuntu store reads *in sync with tracked file* | the `C ·` block on a temp store; `--status` output pasted |
| **D** | Rendering rides sync-agents and runs without PowerShell. `sync-agents.ps1` shells out to `permission_render.py` (write on sync, `--check` on `-Status`); the renderer itself is stdlib `python3` and runs standalone on this machine | `grep -n permission_render .agents/scripts/sync-agents.ps1` non-empty (pinned in `D ·`); `python3 .agents/scripts/permission_render.py --check` runs here |
| **E** | `/smh-llm-approvals` writes the source and reads Antigravity. Its Step 3 edits `families.json` and calls the renderer (never the three files directly); its Step 1 reads Antigravity's store; `workflow_lint.py --toolkit-only` exits 0; the SOP §3 row and the changelog line land in the same commit | linter exit 0; `sop_currency.py` green on the commit; the `E ·` block greps the command body for `families.json` and `~/.gemini/config/config.json` |
| **F** | The record tells the truth. Guide §1's Antigravity row names store, matcher and the apply; §13's row no longer says RETIRED; a deep-dive section exists; `test_guide_currency` (in `test_zoo_permissions.py`) stays green; `zoo-code-replaces-roo-code.md` and `codex-is-fourth-platform.md` no longer teach retirement; `jira.md` says `view --json` does NOT return `parent` and names the JQL check | `F ·` block: grep the guide for `retired` in the Antigravity rows = 0 hits; `test_zoo_permissions.py` green; grep `jira.md` for the corrected sentence |
| **G** | The suite is green on the landing code, with a receipt | `gate_receipt.py run --task SCC-378 --gate suite -- python3 .agents/scripts/tests/run_all.py` → `N/N files passed`, receipt at `<lane>/gates/suite.json` |

**Out of this lane, deliberately:** deleting `C:\Users\dlohn\.gemini` (ticket line 7 — desktop-team
work, gated on the two in-flight Windows stories; this lane only HARVESTS its 27-allow / 37-deny
pair into the source); the Mac application (SCC-382, the operator's, on that machine); any change to
Zoo's or Claude's *decisions* — see §5 Q1.

## 3. Design

### 3.1 The source — `.agents/permissions/families.json`

Stdlib-only JSON (no YAML dependency on a fresh machine). One entry per family, platform-neutral,
with the per-platform exceptions the ticket demands so the source stays honest:

```json
{
  "allow": [
    {"id": "git-broad",     "cmd": "git",              "why": "every verb the doors use; damage spellings are denied"},
    {"id": "gh-pr",         "cmd": "gh pr",            "why": "open PRs, never merge (denied)"},
    {"id": "py3",           "cmd": "python3",          "why": "the toolkit"},
    {"id": "door-vars",     "cmd": "VAR=",             "why": "the standalone assignments the doors print",
                            "render": {"zoo": ["REPO=", "BRANCH=", "..."], "antigravity": "[A-Z_]+=.*", "claude": ["REPO=*", "..."]}},
    {"id": "reallow-lane-delete", "cmd": "git branch -d chore/", "only": ["zoo"],
                            "why": "Zoo re-allow beats its own -D deny by length; Antigravity denies by TARGET instead"}
  ],
  "deny": [
    {"id": "rm-recursive",  "cmd": "rm -r",  "render": {"zoo": ["rm -rf", "rm -r"], "antigravity": ["rm -[a-zA-Z]*[rR][a-zA-Z]*", "rm --recursive"]}, "claude": false},
    {"id": "branch-D-main", "cmd": "git branch -D", "render": {"antigravity": "git branch -D (main|master|develop)"}}
  ],
  "env_twin_prefix": "env -u GITHUB_TOKEN "
}
```

Rules of the source, enforced by the test: every row has `id`, `cmd`, `why`; `only`/`not` name
platforms from the closed set `{zoo, claude, antigravity}`; `render` overrides are per-platform and
optional; `claude: false` on a deny is legal because Claude's tracked file has no deny list (its
fence is hooks + the OS sandbox — guide §3) and the test's Claude leg treats "not allowed" as `ask`.

**Initial content is DERIVED, not authored** (§5 Q1): a one-off `permission_render.py --seed`
reads today's three lists, buckets every row into a family, and writes `families.json` such that
rendering it reproduces today's Zoo and Claude lists as SETS (order normalised) and this morning's
Antigravity list. Rows the three lists disagree on are written with `only:` so nothing changes, and
listed in the walkthrough as the operator's decisions. `--seed` is then deleted from the script
before the lane lands (it is a migration, not a feature).

### 3.2 The renderers — `.agents/scripts/permission_render.py`

One script, three targets, stdlib only:

| Platform | Writes | Preserves | Grammar it encodes |
|---|---|---|---|
| Zoo | `.vscode/settings.json` → `zoo-code.allowedCommands`, `zoo-code.deniedCommands` | every other key, the JSONC line comments | lowercase prefix; `env -u GITHUB_TOKEN ` twin on every git/gh deny; re-allow rows one char longer than their deny |
| Claude | `.claude/settings.json` → `permissions.allow` | `permissions.ask`, `additionalDirectories`, hooks, plugins, worktree — everything else | `Bash(<prefix>:*)`, never `X:*` after `/ = - :` (SCC-375 A2b), never `git -C *` (A6), the three sentinels A2 pins |
| Antigravity | `.agents/permissions/antigravity.json` → `{"userSettings": {"globalPermissionGrants": {"allow": [...], "deny": [...]}}}` | (rendered file, wholly owned) | `command(X)` + `unsandboxed(X)` twin per allow; regex metachars escaped; flag clusters; attached `=`; target-scoped denies |

`--check` re-renders in memory and byte-compares (after the platform's own normalisation) with each
target; exit 0 clean, 1 on drift naming the file and the first differing row. Deterministic order
(sorted within family, families in source order) so a re-render is a no-op diff.

⚠ **`.claude/settings.json` is inside Claude Code's own sandbox deny-list** (`denyWithinAllow`).
The renderer's write to it will fail inside a sandboxed Bash call by design — Claude protects its
own settings. The write runs once, unsandboxed, through the permission gate, and the walkthrough
records that. `--check` (read-only) needs no such thing.

### 3.3 The matchers — `.agents/scripts/permission_matchers.py`

Three functions with one signature, `verdict(cmd, allow, deny) -> "allow" | "deny" | "ask"`:

- `zoo()` — the mirror `test_zoo_permissions.py` already carries (`pieces()`, `_longest()`,
  `decide()`, verified against the extracted v3.80.1 parser 2026-08-30), moved here with its
  attribution comment intact. `test_zoo_permissions.py` is **not** edited in this lane — its own
  copy stays; the duplication is one lane's churn avoided and is named in the walkthrough as owed.
- `claude()` — `Bash(prefix:*)` ≡ `Bash(prefix *)`; a compound is judged per `&&`/`;`/`|` segment;
  a segment with no matching rule is `ask`; the tracked file has no deny so `deny` never returns
  from this leg (the fence is hooks + sandbox, and the battery's Claude expectations say so).
- `antigravity()` — split on whitespace, each rule token `re.fullmatch` against the command token,
  rule shorter-or-equal, `Deny > Ask > Allow`. The `agy_fence_test.py` implementation, verified
  against the vendor's documented semantics.

### 3.4 The battery — `.agents/scripts/tests/test_permission_parity.py`

One fixture module of commands with expected verdicts, three legs, one `run_all.py` file:

- **Destructive** (must be `deny` on Zoo and Antigravity, `ask` on Claude — Claude has no deny
  list and the test says so rather than pretending): the union of Zoo's 68-row battery and
  Antigravity's 41, minus the Windows spellings SCC-376 retired.
- **Ceremony** (must be `allow` on all three): the union of Zoo's 25 and Antigravity's 30 — every
  door step the close-outs and kickoffs print.
- **Unknown tools** (must be `ask` on all three): `curl`, `find -delete`, `gh api`, bare `rm`,
  `wget`, `nc`, `docker`, `ssh`, `brew`, `npx create-next-app`.
- **Parity**: for every command in all three sets, the three verdicts agree modulo the one
  documented Claude exception.
- **Structural**: `--check` is 0 on the rendered files and non-zero after a one-char mutation of
  each (written to a temp copy, never the tracked file); the source's `only`/`not` platforms are in
  the closed set; every row has `id`/`cmd`/`why`; the apply script's temp-store contract (C).
- **Currency**: the guide's Antigravity rows contain no `retired`; `sync-agents.ps1` names the renderer.

Blocks (`c.block(...)`) are lettered A–F to match §2 so `--case` runs one acceptance row.

### 3.5 The apply — `.agents/scripts/antigravity_permissions_apply.py`

The `agy_fence_apply.py` from this morning, promoted: reads `.agents/permissions/antigravity.json`
instead of a scratch file, `--status` / `--apply`, backs up once, touches only
`globalPermissionGrants`, preserves everything else, reads back and reports. Same shape and same
docstring conventions as `zoo_permissions_apply.py`. Unlike Zoo's, it has no "editor must be
closed" refusal, because the store is a plain JSON file with no second writer we have measured — the
walkthrough records that as the assumption it is, and the operator's reload-and-test is what
confirms the extension picks the file up.

### 3.6 `/smh-sync-agents` and `/smh-llm-approvals`

- `sync-agents.ps1`: after the launcher generation, `python3 .agents/scripts/permission_render.py`
  (write) on a sync and `--check` on `-Status`, surfacing drift in the same status table. It
  RENDERS only; the two apply scripts stay explicit doors. Interpreter probed `python3 → python → py`
  like the hooks.
- `smh-llm-approvals.md`: Step 1 gains a third store — Antigravity's `~/.gemini/config/config.json`,
  where every `unsandboxed(...)` / `command(...)` row not produced by the render is a command the
  operator had to click through (the store has no ask log; the grants ARE the record). Step 3 writes
  the chosen rows into `families.json` and runs the renderer; it no longer edits the three files.
  Its narrowness law ("a row is only as wide as the command it came from") is unchanged. SOP §3 row
  and the `#### /smh-llm-approvals` section updated; one changelog line.

### 3.7 The record

- `terminal-permissions-guide.md`: §1 row rewritten (store · matcher · how an approval sticks); §13
  row rewritten; a new **§3A Antigravity** deep dive after the Claude one — the two rule types, the
  precedence, the token grammar with the two day-one catches, the apply, and the measured "sandbox
  does not auto-approve" finding with its source. The §8 `CANONICAL-LISTS` markers are not moved
  (`test_guide_currency` slices between them).
- `_artifacts/_memory/zoo-code-replaces-roo-code.md` and `codex-is-fourth-platform.md`: the
  retirement sentences corrected to the 2026-09-03 state; `MEMORY.md` hooks updated if their
  one-liners change.
- `.agents/rules/jira.md` §Subtasks: the "`view` returns the parent's own issuetype and status"
  sentence corrected — `view --json` returns no `parent` field (measured on SCC-382, 2026-09-03);
  `parent = <KEY>` JQL is the check.
- `_artifacts/_main/INDEX.md`: the new session folder's row.
- This lane's artifacts: the four `agy_fence_*` files and the `SCC-378.md` / `SCC-382.md` outlines
  MOVE from the SCC-376 folder into this lane's folder (they were parked there before a lane
  existed); the SCC-376 folder returns to its landed state; SCC-382's Jira `## Files` path is
  refreshed via `jira_ticket.py describe` at close-out.

## 4. Execution order (each step names the assertion that proves it)

0. **Absorb `origin/main` first if SCC-383 has landed** (`cd <tree> && git fetch origin && cd <tree> && git merge --no-edit origin/main`). Move the parked artifacts into this lane's folder — they are untracked in the main checkout, so this is a filesystem move, not a git delete; the one MODIFIED file there (`tickets/SCC-378.md`) is copied in, then restored in main with `git checkout -- <path>`. First commit: artifacts only.
1. **RED — `test_permission_parity.py`** with all six blocks, run bare: every block fails for the right reason (missing module / missing source / missing renderer / guide still says `retired`). Paste the red. → A–F
2. **`permission_matchers.py`** — three matchers. `--case "A ·"` still red (no rendered files yet) but the matcher unit checks inside A go green. → A
3. **`families.json` via `--seed`**, then delete `--seed`. Render all three targets. The Claude write runs unsandboxed once. `--check` exit 0. Disagreements the seed found → walkthrough `## Evidence` as the operator's decisions, unchanged in behaviour. → B
4. **`antigravity_permissions_apply.py`** promoted from the scratch installer; `--status` on the live store: *in sync*. Temp-store contract green. → C
5. **`sync-agents.ps1`** call site + `-Status` drift row; `--check` standalone green here. → D
6. **`smh-llm-approvals.md`** Steps 1 and 3, **and its opencode mirror copied byte-for-byte**; SOP §3 row + `#### /smh-llm-approvals` + `.agents/commands/INDEX.md` row 65 + one changelog line, same commit; `workflow_lint.py --toolkit-only` exit 0. → E

⚠️ AUDIT FINDING (Lens 2, anchor `sop_currency.py:77` — `(".agents/scripts/", (".py", ".ps1"), "the safety-net scripts")`, tests exempt at `:82`): steps 3, 4 and 5 each add or edit a usage surface, not only step 6. The armed commit-msg gate refuses any of those commits without the SOP staged. So the SOP §5 rows for `permission_render.py` and `antigravity_permissions_apply.py` and the `/smh-sync-agents` row land **in the same commit as the scripts they describe** — steps 3–6 are one commit, or each carries its SOP half. `[sop-ok]` is not the exit here: every one of these is something the operator types.
7. **Guide, memory, `jira.md`, INDEX.** `test_zoo_permissions.py` still green. → F
8. **Mutants declared from the code, one sweep** (`mutation_sweep.py --table <lane>/sweep.json`): flip Antigravity precedence to Allow-wins; drop the env twin in the Zoo renderer; unescape the `.` in `git add \.`; make `--check` return 0 unconditionally; make the apply write a second key. Each names the case that must kill it.
9. **STAMP** — `gate_receipt.py run --task SCC-378 --gate suite -- python3 .agents/scripts/tests/run_all.py` on a clean tree. → G
10. `/smh-code-review` → `walkthrough.md` (`review-runtime: fan-out`) → `task.yaml` → Dev Record → **stop**.

## 5. Open questions for Mr. Hatter — design forks, not gates

**Q1 — Does the initial source change any Claude or Zoo decision?** My recommendation: **no.** Seed
the source FROM today's three lists so rendering reproduces them as sets; the battery then reports
where the three disagree and those become your rulings, one line each in the walkthrough, applied
in a follow-on render — never silently inside this lane. The alternative (hand-curate a fresh source
now) is a bigger change with three fences moving at once and no baseline to diff against.

**Q2 — Claude has no deny list; should the source give it one?** Recommendation: **not in this
lane.** Claude's fence is hooks plus the OS sandbox (guide §3), `permissions.deny` is empty on
purpose today, and adding one changes Claude's behaviour on both machines — that is its own ticket
with its own battery. The test's Claude leg expects `ask` on the destructive set and says so.

**Q3 — The Antigravity `deny` array is unverified until your `git clean -fd` test.** The plan
renders it. If the extension turns out to ignore an unknown key, the Antigravity renderer's deny
output moves to whichever field the extension honours (`deniedCommandsList` is the candidate — the
old Windows store carried it) inside this lane, and the battery's expectations do not change. Not a
blocker for approval; a fork the test settles.

## Port Checklist

`.claude/settings.json` and `.vscode/settings.json` exist in more than one repo — measured from the main
checkout, 2026-09-03:

```
Projects/AGY_AVIATIONCHAT/.claude/settings.json      Projects/AGY_AVIATIONCHAT/.vscode/settings.json
Projects/BRKN_Tattoos/.claude/settings.json          Projects/BRKN_Tattoos/.vscode/settings.json
Projects/Fresh_Workspace_BMAD/.claude/settings.json  Projects/Fresh_Workspace_BMAD/.vscode/settings.json
Projects/NEXgen-VR-Director/.claude/settings.json    Projects/NEXgen-VR-Director/.vscode/settings.json
Projects/sudo-command-center/.claude/settings.json   Projects/sudo-command-center/.vscode/settings.json
Projects/sudo-project-skeleton/.claude/settings.json Projects/sudo-project-skeleton/.vscode/settings.json
Projects/B-L-WorldWide/.vscode/settings.json         Projects/NEXGen-Films/.vscode/settings.json
```

**This lane ports nothing.** Every path in the Declared Change Set is a lobby path; no `Projects/*` file
is in scope. That is the standing decision, not this lane's choice — `terminal-permissions-guide.md:469`:
*"AGY's own allow rules ride AVCH-116 (the port of this ticket's shape) and AVCH-114 (the Zoo half),
never a lobby ticket."* A lobby ticket editing a project's copy produces a commit no project ticket
accounts for (the same boundary SCC-376 drew). The six checks, for the files in scope:

| # | Check | Answer |
|---|---|---|
| 1 | git-given paths used as given | n/a — the renderer writes repo-relative lobby paths resolved from `Path(__file__)`, never from a git command's output |
| 2 | operator text via `printf` | n/a for the Python scripts (`print`); the one `.ps1` edit adds a call line, no new operator text |
| 3 | on a write, verify the FILE | yes — `--check` re-reads every rendered file and the apply reads the store back (§3.2, §3.5) |
| 4 | no `.agents/rules/` path the target lacks | n/a — the target is this repo |
| 5 | runs on BOTH machines | yes — stdlib `python3` on Mac and Ubuntu; the `.ps1` half is exercised only where `pwsh` exists and is checked statically here (row D) |
| 6 | hooks repo-local, target's own key | n/a — no hook changes; branch and commits carry `SCC-378` |

The project copies get the renderer when their own tickets pick it up; nothing here reaches them, and
the walkthrough names that as owed to AVCH-116 / AVCH-114, not to this lane.

## Declared Change Set

- NEW `.agents/permissions/families.json` — the one platform-neutral source → B
- NEW `.agents/permissions/antigravity.json` — the rendered Antigravity fence → B
- NEW `.agents/scripts/permission_render.py` — three renderers + `--check`; `--seed` exists only until step 3 → B, D
- NEW `.agents/scripts/permission_matchers.py` — zoo / claude / antigravity verdict functions → A
- NEW `.agents/scripts/antigravity_permissions_apply.py` — the promoted installer → C
- NEW `.agents/scripts/tests/test_permission_parity.py` — the unified battery, six blocks A–F → A, B, C, D, E, F
- EDIT `.vscode/settings.json` — `zoo-code.*` keys re-rendered from the source, set-equal to today → B
- EDIT `.claude/settings.json` — `permissions.allow` re-rendered from the source, set-equal to today → B
- EDIT `.agents/scripts/sync-agents.ps1` — shell out to the renderer on sync, `--check` on `-Status` → D
- EDIT `.agents/commands/smh-llm-approvals.md` — Step 1 reads Antigravity, Step 3 writes the source → E
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — the `/smh-llm-approvals` rows and the `/smh-sync-agents` row → D, E
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one line → E
- EDIT `docs/migrations/terminal-permissions-guide.md` — §1 row, §13 row, new §3A → F
- EDIT `_artifacts/_memory/zoo-code-replaces-roo-code.md` — retirement sentence corrected → F
- EDIT `_artifacts/_memory/codex-is-fourth-platform.md` — platform count sentence corrected → F
- EDIT `.agents/rules/jira.md` — the `view` / `parent` sentence corrected → F
- EDIT `_artifacts/_main/INDEX.md` — this session's row → G
- NEW `_artifacts/_main/2026-09-03_SCC-378-permission-parity/walkthrough.md` — evidence, review, actions → G
- NEW `_artifacts/_main/2026-09-03_SCC-378-permission-parity/task.yaml` — the lane manifest → G
- NEW `_artifacts/_main/2026-09-03_SCC-378-permission-parity/sweep.json` — the mutant table → G
- NEW `_artifacts/_main/2026-09-03_SCC-378-permission-parity/tickets/SCC-378.md` — outline, moved from the SCC-376 folder → G
- NEW `_artifacts/_main/2026-09-03_SCC-378-permission-parity/tickets/SCC-382.md` — outline, moved from the SCC-376 folder → G
- NEW `_artifacts/_main/2026-09-03_SCC-378-permission-parity/agy-fence.portable.json` — this morning's hand-built fence, the baseline row B's set-equality check reads → B
- EDIT `.opencode/commands/smh-llm-approvals.md` — the opencode door is a FULL MIRROR, byte-identical to the command body (`test_command_surfaces.py:593`); no `pwsh` here to regenerate it, so it is copied by hand in the same commit → E
- EDIT `.agents/commands/INDEX.md` — row 65 still says the door "adds the ones he picks to both allow lists and runs the Zoo apply"; it writes the source now → E
- EDIT `.agents/scripts/INDEX.md` — one row each for `permission_render.py`, `permission_matchers.py`, `antigravity_permissions_apply.py`, the convention every script in that folder follows → B, C

⚠️ AUDIT FINDING (Lens 1, anchor: `git status --short` in the main checkout): the four `agy_fence_*` files and `tickets/SCC-382.md` under the SCC-376 folder are **untracked** (`??`) — git has never seen them, so there is no `DELETE` to declare and none appears in any diff. They MOVE on the filesystem into this lane's folder (step 0); the NEW rows above are the only git-visible change. Four `DELETE` bullets that claimed otherwise were removed from this block — `/smh-code-review` Step 2 would have read each as "declared, never changed".

## 7. Verification plan

```bash
cd <tree> && python3 .agents/scripts/tests/test_permission_parity.py                 # A-F, bare
cd <tree> && python3 .agents/scripts/permission_render.py --check                    # B, exit 0
cd <tree> && python3 .agents/scripts/antigravity_permissions_apply.py --status       # C, "in sync"
cd <tree> && python3 .agents/scripts/tests/test_zoo_permissions.py                   # F, guide currency still green
cd <tree> && python3 .agents/scripts/tests/test_settings_allowlist.py                # A2/A6/B1 sentinels survive the render
cd <tree> && python3 .agents/scripts/workflow_lint.py --toolkit-only                 # E
cd <tree> && python3 .agents/scripts/declared_change_set.py parse _artifacts/_main/2026-09-03_SCC-378-permission-parity/implementation_plan.md
cd <tree> && python3 .agents/scripts/mutation_sweep.py --table _artifacts/_main/2026-09-03_SCC-378-permission-parity/sweep.json
cd <tree> && python3 .agents/scripts/gate_receipt.py run --task SCC-378 --gate suite --root _artifacts/_main/2026-09-03_SCC-378-permission-parity --cwd <tree> -- python3 .agents/scripts/tests/run_all.py
```

Every gate runs bare — a piped gate hides its exit code.

## Self-Audit (2026-09-03)

**Level:** LEDGER+BLAST · **Mode:** PRE-WORK · **Repo:** `Sudo_Hatter_Command` (worktree
`.claude/worktrees/SCC-378-permission-parity`) · **Branch:** `chore/SCC-378-permission-parity` @ `ab68505e` ·
**Ticket:** SCC-378 · **Plan:** this file. Level derived from the Declared Change Set: a rule (`jira.md`),
scripts others call (`sync-agents.ps1`), a command surface, the SOP, three platforms — not a caller flag.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every named path exists (31 probed, 1 MISSING = `.agents/permissions/`, a NEW dir) ·
             declared_change_set.py parse -> 27 entries, 0 incomplete (after heading fix: the parser
             anchors on the literal `## Declared Change Set`, the numbered heading parsed to ZERO) ·
             both-machine interpreter: every command is `python3` stdlib (Mac + Ubuntu since SCC-376);
             the `.ps1` edit cannot EXECUTE on this machine (no pwsh) -> row D is a static check here ·
             lane fit: no deployable path in the set (backend/ frontend/ firebase/ functions/ mobile/
             .github/ absent) -> /smh-close-task-merge-tree is the door ·
             Scope Ledger: 7 acceptance rows A-G, each with a command or an inspection; 12 NEW artefacts
             x rows -> 11 had a row; `agy-fence.portable.json` had none (FINDING 1, baked into row B) ·
             caller count: `permission_matchers.py` has two callers, both created by this plan
             (`permission_render.py`, `test_permission_parity.py`); falsifiable when
             `test_zoo_permissions.py` adopts it, which the walkthrough names as owed ·
             tests-must-gate-for-real: RED-first per row, mutants declared from the code in step 8
read:        implementation_plan.md · declared_change_set.py (HEADING regex :50, ATTEMPT :56) ·
             `git status --short -- _artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/` (main) ·
             `git ls-files` on that folder (none of the parked files tracked) · worktree listing of the
             same folder (parked files ABSENT there) · sop_currency.py :71-:82 · _harness.py head ·
             test_zoo_permissions.py :1-:225 (matcher mirror, batteries, guide-currency parser)
verdict:     findings below
```

```
lens:        2 Parity + Blast
checks_run:  command file -> four doors: .agents/skills + .claude/skills launchers (thin, read the body
             live), .agents/workflows launcher (description EQUALS frontmatter today, plan keeps the
             description), .opencode/commands FULL MIRROR (`cmp` identical today; FINDING 3) ·
             command name unchanged -> no reference sweep owed · rule (`jira.md`): not in .roo/rules/
             (ls: 4 floor rules only), a sentence edit, `_RULE_POINTERS` unaffected · script
             (`sync-agents.ps1`): no .githooks caller (grep: none); `test_settings_allowlist.py` E-block
             parses `$AllPlatforms` :129, untouched by an added call · gate/hook: none · path move: the
             parked files are linked only from the two outline files that move with them + the SCC-382
             Jira description (plan §3.7 refreshes it) · SOP + usage surfaces: `.agents/scripts/*.py|.ps1`
             ARE surfaces (sop_currency.py:77), tests exempt (:82) -> steps 3-5 each need the SOP in the
             same commit, plan only said step 6 (FINDING 4) · `_artifacts/_memory/` edits: the store's
             rule bans OBLIGATIONS and sweeping others' entries, not correcting a stale fact with explicit
             paths (artifacts-always-first.md:364-392); the operator-approved SCC-378 v1 did the same ->
             clean · file in >1 repo: `.claude/settings.json` x7 and `.vscode/settings.json` x8 under
             Projects/ -> the plan LACKED the named port section (FINDING 2, NO-GO ground; baked in as
             `## Port Checklist`, every check answered with the reason, standing decision cited from
             guide :469) · twins: no cicd-* sibling for either command · sibling worktrees: fetched
             origin/main; SCC-383 touches `.agents/commands/cicd-dev-story-tests.md`,
             `.opencode/commands/cicd-dev-story-tests.md`, `_artifacts/_main/INDEX.md`,
             `docs/_scc_sops_prds/workflows_testing_SOP.md` (+ an untracked session folder) — overlap
             with this plan is the SOP and the INDEX, different rows; operator confirms the subject is
             unrelated ("keeping the branch current with main") · INDEX conventions: `.agents/commands/
             INDEX.md:65` describes the OLD door behaviour (FINDING 5); `.agents/scripts/INDEX.md` carries
             a row per script (:31-:32 the zoo_notify pair) -> three new rows owed (FINDING 6) · guide
             currency: `test_guide_currency` asserts the literal `"{len(ALLOW)} allow / {len(DENY)} deny"`
             and every backticked token in the §8 Entries cells is a real entry -> set-equal Zoo render
             (row B) keeps 124/105 true and the test green · Zoo live drift: `zoo_permissions_apply.py`
             compares as SETS (:122) -> a re-ordered tracked file creates no live drift, no Zoo apply
             owed in-lane when set-equal · risk_seam: `unclassified`, root = this worktree (SCC-289,
             correct in the centre)
read:        test_command_surfaces.py :199, :571, :593 · .agents/commands/INDEX.md:65 ·
             .agents/scripts/INDEX.md:31-:32 · `ls .roo/rules/` · sop_currency.py:71-:82 ·
             artifacts-always-first.md:364-:392 · port-checklist.md:41-:115 · terminal-permissions-
             guide.md:469 · zoo_permissions_apply.py:122 · test_settings_allowlist.py:100-:116 ·
             test_zoo_permissions.py:302-:334 · `ls Projects/*/.claude/settings.json Projects/*/.vscode/
             settings.json` (main) · SCC-383 `git diff --name-only origin/main...HEAD` + `status --short`
             · `risk_seam.py classify` · `env -u GITHUB_TOKEN git fetch origin main`
verdict:     findings below
```

```
lens:        3 Pre-Mortem (bounded: attaches to anchored findings only)
checks_run:  the silent one · the other-machine one · the fresh-clone one · the sibling-lands-first one,
             each tried against every finding above; narratives that attached are in the table
read:        the findings table
verdict:     narratives attached to findings 2, 3, 4 and to row B's sandbox paragraph (§3.2)
```

### Findings

| # | anchor | literal text read | consequence | severity |
|---|---|---|---|---|
| 2 | `.agents/rules/port-checklist.md:111-115` + `ls Projects/*/.claude/settings.json` (main, 7 hits) | *"One section, named for this rule, answering all six for the files in SCOPE ... `/smh-self-audit` ... refuse a port plan that lacks it."* | The two rendered lobby files exist in seven and eight project repos; the plan had no port section, which is the rule's NO-GO. **Baked in** as `## Port Checklist` — every check answered, the standing "never a lobby ticket" decision cited from guide :469. Pre-mortem (other-machine): a project's own Zoo store keeps deciding from its own copy; nothing here changes that, and AVCH-116/114 own the port | **high → resolved in plan** |
| 3 | `.agents/scripts/tests/test_command_surfaces.py:593` + `cmp .agents/commands/smh-llm-approvals.md .opencode/commands/smh-llm-approvals.md` → identical | *"opencode - a FULL MIRROR, byte-identical to the brain. Nothing else."* | Editing the command body without the mirror turns CS red; `pwsh` is absent here so the sync cannot regenerate it. Pre-mortem (fresh-clone / CI): `main-write-gate` runs the suite, the PR is unmergeable, and the fix is a second commit nobody planned. **Baked in:** EDIT row for the mirror, step 6 copies it byte-for-byte | high → resolved in plan |
| 4 | `.agents/scripts/sop_currency.py:77` | `(".agents/scripts/", (".py", ".ps1"), "the safety-net scripts")` (tests exempt at `:82`) | Steps 3, 4, 5 each add or edit a usage surface; the armed commit-msg gate refuses those commits without the SOP staged, and the plan promised the SOP only at step 6. Pre-mortem (the silent one): the builder reaches for `[sop-ok]` to get past the refusal, which is exactly the reflex the gate exists to un-train. **Baked in:** §4 finding block — steps 3-6 land as one SOP-carrying commit, or each carries its SOP half | medium → resolved in plan |
| 1 | this plan, `## Declared Change Set`, the `agy-fence.portable.json` NEW bullet | *"this morning's hand-built fence, kept as the baseline the seed is checked against → B"* | Created by step 0; **no acceptance row required it** — row B only compared renders to the three tracked files. **Baked in:** row B now requires the Antigravity render to be set-equal to the baseline (and the Zoo/Claude renders set-equal to `origin/main`), which is the "reproduces today" guarantee Q1 depends on | medium → resolved in plan |
| 5 | `.agents/commands/INDEX.md:65` | *"adds the ones he picks to both allow lists and runs the Zoo apply"* | Stale the moment step 6 lands; the index describes a door that no longer exists. **Baked in:** EDIT row, step 6 | low → resolved in plan |
| 6 | `.agents/scripts/INDEX.md:31-32` | one row per script (`zoo_notify.py`, `zoo_notify_install.py`, ... every script in the folder) | Three new scripts with no row break the folder's own convention and the reader's map. **Baked in:** EDIT row | low → resolved in plan |
| 7 | `git status --short -- _artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/` (main) | `?? .../agy-fence.portable.json` `?? .../agy_fence_apply.py` `?? .../agy_fence_gen.py` `?? .../agy_fence_test.py` `?? .../tickets/SCC-382.md` | Four `DELETE` bullets named files git has never tracked; no diff will ever show them, and `/smh-code-review` Step 2 reads each as declared-but-unchanged drift. **Baked in:** the four bullets removed, step 0 rewritten as a filesystem move | low → resolved in plan |

No finding survives unresolved. Corroboration: none — every anchor was raised by exactly one lens (the
lenses ran blind; finding 2 and finding 3 share a *topic*, cross-surface parity, and are deliberately
NOT merged — different anchors, different consequences).

### Observations (uncounted)

- The audit body's own Lens 1 check 3 says *"the PC has no `python3`"*. Since SCC-376 the PC works
  inside Ubuntu and has only `python3`; the line describes the retired native-Windows shape. Remedy is a
  one-word edit to `smh-self-audit.md` in a lane that owns it — not this one.
- `docs/repo-map.md`'s curated block lists `.agents/` as *"rules · commands · skills · workflows · bmad ·
  scripts · templates"*. `.agents/permissions/` is a new subfolder; `check_maps.py` (the SessionStart
  linter) may report drift at close-out. Run `python3 .agents/scripts/check_maps.py` before the receipt
  and regenerate the AUTO body if it asks — the `.ps1` drift checker cannot run here.
- The `.claude/settings.json` render needs one unsandboxed write (§3.2). If it never happens, `--check`
  is red forever and the operator reads a Claude list that "keeps drifting". The walkthrough records the
  write as a discrete step with its output, so a red `--check` on that file has one known cause.
- Row D is the weakest row: with no `pwsh` on this machine the `.ps1` call site is proven by grep and
  the renderer by running it standalone; the integrated path is first exercised on the Mac. Named
  honestly in the acceptance table; not a finding because the plan already says it.

### Sibling landing order

**SCC-383** (`chore/SCC-383-epic-sync-check`) and this lane both edit `docs/_scc_sops_prds/
workflows_testing_SOP.md` and `_artifacts/_main/INDEX.md`, different rows. No dependency either way;
whichever lands second runs `cd <tree> && git fetch origin && cd <tree> && git merge --no-edit
origin/main` before its last commit (§4 step 0). If SCC-383 lands first nothing here changes; if this
lands first SCC-383 absorbs two added rows.

```
Audit verdict: GO
```
