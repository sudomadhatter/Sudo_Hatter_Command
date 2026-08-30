# Walkthrough — SCC-351 · Zoo Code auto-approve, fixed for real

**Lane:** `chore/SCC-351-zoo-approvals` · **Ticket:** SCC-351 (parent SCC-33) · **Date:** 2026-08-30
**Approval:** operator, verbatim — "merged lets fix this termianl command requrest problem now once
and for all" (against the plan at `e157afc9`), plus the mid-build design ruling: *"I am less
worried about denies than I am allows. denies should be the abosolute min only things that would
really cause damage."*

## What shipped, in order

**The root cause, named once (Part A, landed at lane-open).**
[zoo-code-permissions-guide.md](../../../docs/migrations/zoo-code-permissions-guide.md) — Zoo
decides from VS Code globalState (`state.vscdb` → `ZooCodeOrganization.zoo-code`), which the
tracked settings file seeds exactly once and denies never seed; the matcher is lowercase
starts-with per piece, longest prefix wins. Everything verified by executing Zoo v3.80.1's own
extracted parser.

**Part B — canonical lists** in [.vscode/settings.json](../../../.vscode/settings.json):
**109 allow / 97 deny.** Broad allow families (`cd `, `git `, `python3 `/`python `, `gh pr `,
`acli jira workitem `, read-only set, door variables, dot-dir adds) + minimum denies, each naming
real damage, none colliding with a ceremony step. The operator's min-deny ruling shaped three
decisions mid-build: `git checkout main`/`git switch main` denies REMOVED (parking the checkout on
main is a real close-out step; the damage — pushing main — is fenced by the GitHub ruleset + hooks),
`git clean` narrowed to `-f`/`-d` (dry-run `-n` approvable), and `git config` denied with
`--get`/`--list`/`-l` re-allowed (reads work; a config write can disarm `core.hooksPath`). Denies
under a broad allow are load-bearing: an un-denied damage spelling does not ask — it AUTO-RUNS.
Every `git `/`gh ` deny carries a generated `env -u GITHUB_TOKEN ` twin (the broad env allow would
bypass it otherwise). Lane/epic prunes re-allowed in quoted AND unquoted spellings (the quote
character defeats prefix matching — found by hand-checking door hunks).

**Part C — the apply script**
[zoo_permissions_apply.py](../../../.agents/scripts/zoo_permissions_apply.py): discovers every
`state.vscdb` carrying the Zoo key (default + named VS Code profiles, Mac + PC paths), `--status`
reports counts/toggles/drift, `--apply` writes both lists (one-time `.scc-backup` beside each db),
refuses while VS Code runs, pure stdlib. Run live on this Mac: found the store, reported the exact
stale 49/19 vs tracked 109/97 drift, toggles healthy, guard OFF.

**Part D — the gate**
[test_zoo_permissions.py](../../../.agents/scripts/tests/test_zoo_permissions.py), 12 tests:
python mirror of the documented matcher; **68-row destructive battery → 0 auto-approve (68
auto-deny)**; **25-step ceremony set → all auto-approve** (incl. quoted prunes, epic-close
`branch -D epic/…`, parking on main); legit-read pins (`git clean -n`, `git config --get`);
documented-residual pins (env-prefix assignment, `$(… && …)` subshell, `--force` behind a prefix,
heredoc python); env-twin invariant; re-allow-beats-deny length checks; no allow==deny tie
(tie → deny); guide §6 Entries-cell currency + count line; apply-script source pins; doors stay
`git -C`-free (allowlist: the three teaching files). Every verdict cross-checked against the real
extracted matcher before landing.

**Part E — the law inverted.**
[command-shape.md](../../../.agents/rules/command-shape.md) rewritten: the old rule banned
cd-chains and MANDATED `git -C`; the executed matcher proved Zoo splits compounds per piece, so
the law is now **pin in the SAME compound line — `cd <abs> && git <verb>` — never `git -C`**
(auto-denied as a launder shape), plus §Zoo (one logical line, no loops, no `$( … && … )`,
heredocs fine). [git-policy.md](../../../.agents/rules/git-policy.md) §merge-target and the
safe-revert idiom rewritten to the same pin; INDEX row updated;
[zoo-team.md](../../../.agents/rules/zoo-team.md) points every seat at the shape law + apply
procedure (mirror regenerated).

**Part F — the door rewrite.** `git -C <path> <verb>` → `cd <path> && git <verb>` (and the
`env -u GITHUB_TOKEN` form): **229 spellings across 30 files** (228 by mechanical regex, 1 in a subdirectory door
caught by making the gate's scan recursive), hand-check of every hunk. The hand-check caught what the regex could not: two deny-vs-ceremony collisions
(checkout-main parking, quoted prune spellings → Part B changes above), one malformed heading, and
25 opencode mirrors + 3 Antigravity full mirrors + the `.roo` team-rule copy regenerated to match.

**Part G — SOP.** New per-machine row in §13's what-does-NOT-travel table (the seeding trap in
operator language + the 3-step apply procedure) + changelog row.
[SOP](../../../docs/_scc_sops_prds/workflows_testing_SOP.md) ·
[changelog](../../../docs/_scc_sops_prds/workflows_testing_SOP_changelog.md)

**Part H — memory.**
[zoo-approvals-decision-store](../../../_artifacts/_memory/zoo-approvals-decision-store.md) (new) ·
[nothing-guards-the-merge-target](../../../_artifacts/_memory/nothing-guards-the-merge-target.md)
(pin idiom updated -C → cd&&git) · MEMORY.md rows.

## The measured record (real 551-command session, real extracted matcher)

| Configuration | Auto-approved |
|---|---|
| Today's decision-store lists (49/19) | **34.1%** |
| Canonical lists, historical spellings | **74.4%** |
| Canonical lists + door rewrite | **88.2%** |

Residual asks are one-off diagnostics + the few door blocks still written as multi-line `if`/loops
(§8-banned shapes for seats). Residual risks documented honestly in guide §5 — interpreters,
subshell laundering, env-prefix assignments, prefix blindness — with the real protections named
(GitHub main-write-gate ruleset, armed hooks, worktree isolation, ceremony doors).

## Suite / gates at tip

- `run_all.py`: **65/65 files** (includes the new 12-test gate; 5 files updated for the new law:
  zoo_team B6 mirror, settings_allowlist B1/B2c sentinels, stale_base_refs pinned row,
  command_surfaces mirrors, check_maps INDEX row).
- `workflow_lint.py --toolkit-only`: 0 errors, 0 warnings.
- `check_links.py`: clean on every changed doc.

## What the operator does after merge (per machine — Mac, then PC when picked up)

1. Quit VS Code fully.
2. `python3 .agents/scripts/zoo_permissions_apply.py --apply` (PC: `python`).
3. Reopen; the closing `--status` must read "in sync with tracked file".
