# Implementation plan — SCC-346 approval fix + Roo→Zoo / Antigravity→VS Code transition

- **Lane:** `chore/SCC-346-approval-fix-zoo` (CONSOLIDATED — one worktree, one branch for the whole Task)
- **Riders:** SCC-349 (Part E). No new subtasks minted — SCC-349 was the only piece that earned a
  ticket, and it already exists. Mode rationale (work-consolidation rule 2): same repo, same lane
  class (toolkit config / rules / sync script), no genuine parallelism.
- **Parent:** SCC-346 (type `Bug` — minted as a Bug by the operator, Task-shaped toolkit work; per
  `jira.md` nothing retypes a Bug mid-flight, `devrecord --closing` clears it at close-out).
- **Source of truth:** SCC-346 comments 10316 (research findings) + 10318 (transition handoff),
  memory `zoo-code-replaces-roo-code`, session `7819434c-21de-47ca-a4e3-8d39fabdbc3a`.

## Parent's checkable list (Step 1)

1. **Tracked Claude allowlist:** `.claude/settings.json` (lobby) carries the stable allow rules with
   BOTH interpreter spellings (`python3` Mac / `python` PC); machine-specific residue stays in
   gitignored `settings.local.json`. Check: JSON parses; allow count ≥ 60; both spellings present;
   no machine-absolute paths (`/Users/`, `C:\`) in tracked rules.
2. **Zoo Code allowlist travels via git:** tracked `.vscode/settings.json` carries
   `zoo-code.allowedCommands` / `zoo-code.deniedCommands`; `.vscode/extensions.json` recommends
   `ZooCodeOrganization.zoo-code`. Check: JSON parse + key/entry presence.
3. **Command-shape rule exists and is surfaced:** a rule in `.agents/rules/` bans the shapes no
   allowlist can match (compound `cd X && …` chains, `; echo "EXIT=$?"` tails, piped gates) and
   AGENTS.md points at it, so Zoo/opencode/Codex (all read AGENTS.md natively) inherit it. Check:
   file exists; AGENTS.md references it; SOP page updated in the same commit.
4. **Extension migration guide serves VS Code:** the install guide's flow uses
   `code --install-extension` (VS Code), not `agy-ide`; Antigravity-only IDs are marked skip; the
   Zoo/VS Code transition checklist (comment 10318) is captured for both machines. Check: guide
   greps; link+anchor gate green.
5. **Zoo is sync-agents platform 5** (SCC-349): `$AllPlatforms` includes `zoo`; sync generates
   `.roo/commands/*.md` launchers for eligible smh-/cicd- commands and `.roomodes` with the six BMAD
   personas, manifest-tracked; persona commands' `platforms:` frontmatter includes `zoo`. Check:
   grep on the script; generated files exist after a sync run; manifest rows present.

## Part sections

### Part A — Promote the Claude allowlist into tracked settings (SCC-346)

The 77 allow rules live only in gitignored `.claude/settings.local.json` (tracked file: 0 rules),
so every approval learned on the Mac dies at the machine/worktree boundary. Promote the **stable,
machine-neutral** subset into `.claude/settings.json`; for every `python3 …` rule add the `python …`
twin (PC); drop/leave-local anything machine-specific (absolute homes, one-off experiments).
The `link-worktree-assets.py` symlink workaround stays (harmless belt-and-braces for local extras).

- Assertion (RED first): `.agents/scripts/tests/test_settings_allowlist.py` — parses tracked JSON,
  count ≥ 60, both spellings, no `/Users/` or `C:\` literals, valid rule syntax.
- ⚠ Review each promoted rule once: tracked = runs on BOTH machines and every future clone.

### Part B — Zoo Code portable allowlist + extension recommendation (SCC-346)

Add `zoo-code.allowedCommands` / `zoo-code.deniedCommands` to tracked `.vscode/settings.json`
(workspace scope — Mac+PC parity; namespace is `zoo-code.*`, NOT `roo-cline.*`). Seed the allowed
list from the same stable command families as Part A (git, python3/python, acli, ls/grep-class
read-onlys); denied list seeds with the destructive set (rm -rf, git push --force, etc.). Add
`ZooCodeOrganization.zoo-code` to `.vscode/extensions.json` recommendations.

- Assertion (RED first): extend the Part A test file — keys exist, allowed non-empty, recommendation
  present.
- Note: Zoo keeps `.roo/*` paths and reads AGENTS.md natively (`zoo-code.useAgentRules`) — no rule
  duplication here.

### Part C — Command-shape rule, surfaced via AGENTS.md (SCC-346)

New `.agents/rules/command-shape.md`: agents run gates BARE — no `cd X && …` chains (use `git -C` /
absolute paths), no `; echo "EXIT=$?"` tails, no piping a gate through `| tee`/`head` (exit code
hidden). This is the one change that cuts prompts in EVERY tool at once, because no prefix
allowlist (Claude, Zoo, opencode) can match a compound command by design; the SCC-287
`allow-readonly-chain.py` hook already handles read-only chains. Add the AGENTS.md pointer.

- **SOP currency:** `.agents/rules/` + AGENTS.md are usage surfaces — stage
  `docs/_scc_sops_prds/workflows_testing_SOP.md` (+ one changelog line) IN THE SAME COMMIT. No `[sop-ok]`.
- Assertion: structural — rule file exists with the three bans, AGENTS.md references it, SOP row
  present. (No prose-pinning mutant tests — `prose-pinning-guards-are-vacuous`.)

### Part D — Migration guide repoint: Antigravity → VS Code (SCC-346)

`docs/migrations/install_guides/antigravity-ide-extension-migration.md` still drives `agy-ide`.
Repoint to VS Code: install via `code --install-extension <id>`, reuse the portable IDs kit
(`docs/migrations/antigravity_extensions/antigravity-extension-ids.txt`), mark Antigravity-only ids
skip, fold in the per-machine transition checklist from comment 10318 (Roo export BEFORE
uninstall — file carries API keys, never commit; Zoo import; per-machine auto-approve toggles; PC
`core.hooksPath` reminder; do NOT carry the Antigravity `git.path` shim into VS Code).
**Rename decision:** rename to `vscode-ide-extension-migration.md` and fix the two live inbound
links (`docs/migrations/INDEX.md`, `docs/repo-map.md`); history artifacts stay untouched. If the
link gate turns up more inbound edges than measured, keep the filename and retitle in place — the
gate is the check, not my grep.

- Assertion: guide greps (`code --install-extension` present; no live `agy-ide` install step);
  link+anchor gate green.

### Part E — Zoo as sync-agents platform 5 (rider SCC-349)

At `.agents/scripts/sync-agents.ps1:125`, `$AllPlatforms = @('claude','opencode','antigravity','codex')`.
Add `'zoo'` and give it a lane, manifest-tracked like the Antigravity workflow mirror (one door per
platform, SCC-66):
1. `.roo/commands/*.md` launchers for zoo-eligible smh-/cicd- commands (md + description /
   argument-hint / mode frontmatter). Zoo keeps `.roo/` paths — do NOT invent `.zoo/`.
2. `.roomodes` YAML: six BMAD personas (analyst/architect/dev/pm/tech-writer/ux) as custom modes
   with roleDefinition + groups; per-mode rules in `.roo/rules-{slug}/`.
3. Extend `platforms:` frontmatter to include `zoo` on the opencode-only masters — measured set, 20
   files (⚠️ AUDIT FINDING: the ticket says "persona commands"; there is no `bmad-agent-*.md` in
   `.agents/commands/` — the real set is `grep -l "platforms: \[opencode\]" .agents/commands/*.md`:
   analyst / architect / dev / pm / qa / sm / tea / tech-writer / ux-designer / bmad-help /
   bmad-master / testarch-* (8) / cicd-autopilot-opencode). Decide per file at dev time whether zoo
   gets it (cicd-autopilot-opencode is opencode-runtime-specific — likely stays opencode-only).
4. **Opencode lane: KEEP.** Operator's ruling in the ticket: "opencode" now stands for
   open-coding-with-OpenRouter generally, names/commands stay. Retiring antigravity/opencode lanes
   is comment 10318 item 8, "later/optional" — a later cycle, not this lane.
- PowerShell portability: probe interpreters, no bare `python`; watch `,@()` unroll and encoding
  memories (`powershell-comma-array-wrapper-unrolls-once`, `powershell-encoding-safety`).
- **SOP currency:** `sync-agents.ps1` is a usage surface — SOP page + changelog in the same commit.
- Assertion (RED first): grep `$AllPlatforms` for `'zoo'`; after a lobby sync run, `.roo/commands/`
  holds launchers for every zoo-eligible command, `.roomodes` parses with 6 modes, manifest rows exist.

### Part F — WITHDRAWN (2026-08-29, operator's correction, same session)

Proposed as template edits requiring links in hand-backs; withdrawn on the operator's ruling: the
obligation already exists in `constitution.md:46` (always-on law), and adding per-command template
text is context an agent re-reads every session for a rule it already has. The incident was an
agent skipping the AGENTS.md front-door read, not missing law. No files change under this part.

## Declared Change Set

- EDIT `.claude/settings.json` — promote stable allowlist, both spellings → 1
- NEW `.agents/scripts/tests/test_settings_allowlist.py` — the Part A/B assertions → 1, 2
- EDIT `.vscode/settings.json` — zoo-code.allowedCommands / deniedCommands → 2
- EDIT `.vscode/extensions.json` — recommend ZooCodeOrganization.zoo-code → 2
- NEW `.agents/rules/command-shape.md` — the three bans → 3
- EDIT `AGENTS.md` — pointer at the new rule → 3
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — rule + zoo platform rows → 3, 5
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one line per change → 3, 5
- DELETE `docs/migrations/install_guides/antigravity-ide-extension-migration.md` — renamed away (fallback: in-place retitle, drop this pair) → 4
- NEW `docs/migrations/install_guides/vscode-ide-extension-migration.md` — the repointed guide → 4
- EDIT `docs/migrations/INDEX.md` — inbound link to the renamed guide → 4
- EDIT `docs/repo-map.md` — inbound link to the renamed guide → 4
- EDIT `.agents/scripts/sync-agents.ps1` — zoo as platform 5 → 5
- NEW `.roomodes` — six BMAD persona modes (generated) → 5
- NEW `.roo/commands/` — zoo launcher files (generated, manifest-tracked) → 5
- NEW `.roo/rules-analyst/` — per-mode rules, one dir per persona slug (generated) → 5
- EDIT `.agents/commands/analyst.md` — platforms: + zoo; same edit across the measured 20-file opencode-only set named in Part E → 5

No deployable paths (`backend/ frontend/ firebase/ functions/ mobile/ .github/`) — Task lane confirmed.

## Port check (MANDATORY RULE 5)

Trigger run 2026-08-29 from the lobby root:

```
git diff --no-index -- .claude/settings.json Projects/AGY_AVIATIONCHAT/.claude/settings.json  → differ=1
git diff --no-index -- .vscode/settings.json Projects/AGY_AVIATIONCHAT/.vscode/settings.json  → differ=1
```

Six-check answer: both files exist in both repos and differ, **and that is correct** — the copies
are deliberately divergent (lobby allowlist ≠ AGY allowlist; `repo-local-enforcement-never-centralizes`).
This lane ports NOTHING into AGY: AGY is a separate git repo with its own board, and cross-repo work
takes a ticket per repo. The AGY halves of fixes (a)/(b) — promote its 49 local rules into its
tracked settings (currently 13), add its `zoo-code.*` keys — are **DEFERRED against a named
structural blocker: separate repo, needs an AVCH ticket.** Proposed at close-out as one AVCH ticket;
minting is the operator's placement call.

## Out of scope (recorded, not lost)

- **AGY repo edits** — deferred above (AVCH ticket).
- **Per-machine operator actions** (Roo settings Export→Zoo Import — carries API keys, keep private;
  Zoo auto-approve master toggle + tiles per machine; VS Code + extension installs; PC
  `core.hooksPath`) → the guide documents them (Part D) and close-out's walkthrough lists them under
  `## Your Actions`; `jira_feed.py finish` HOLDs the ticket until ticked.
- **Retiring antigravity/opencode sync lanes** — later/optional (comment 10318 item 8).
- **Memory-store platform roster** — updated at the next memory audit, per the same comment.

## Build order

C → A → B → D → E. C and E share the SOP page (sequenced, C first); E is the largest and lands last
so sync-generation runs against the finished rule set; A/B/D are file-disjoint from everything else.
`/smh-label-tasks SCC-346` output supersedes this if it disagrees.

## Self-Audit (2026-08-29)

Level: **LEDGER+BLAST** (rules + a script others run + 20 command masters + files existing in >1
repo). Mode: PRE-WORK. Plan: this file. Ticket: SCC-346 (riders: SCC-349).

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every named path ls'd; Declared Change Set parsed; both-machine command check; lane-fit (deployable paths) check; Scope Ledger over NEW entries
read:        .claude/settings.json + settings.local.json (rule counts 0/77), .vscode/settings.json, .vscode/extensions.json, .agents/scripts/sync-agents.ps1:125, .agents/rules/ listing, docs/_scc_sops_prds/* (both SOP files), docs/migrations/INDEX.md, docs/repo-map.md, .agents/scripts/tests/ listing, declared_change_set.py parse output
verdict:     findings below (both fixed inline)
```

```
lens:        2 Parity + Blast
checks_run:  rule row (workflow_lint _RULE_POINTERS exists at workflow_lint.py:70 — register pointer if command-shape law gets citing commands); script row (sync-agents.ps1 has scripts/INDEX.md rows 3+76; test_command_surfaces.py references platforms); path-rename row (inbound links measured: docs/migrations/INDEX.md:85, docs/repo-map.md:120 live; rest is _artifacts/ history, untouched); SOP row (same-commit staging planned in Parts C and E); >1-repo row (port section, trigger diffs quoted); sibling worktrees (fetched, listed); risk_seam classify
read:        grep -l "platforms: \[opencode\]" .agents/commands/*.md (20 files); git worktree list (this lane only — NO sibling lanes, no landing-order deps); risk_seam → unclassified, root=this tree (correct in the centre, SCC-289)
verdict:     findings below (fixed inline)
```

```
lens:        3 Pre-Mortem
checks_run:  attach-only pass over Lens 1/2 survivors
read:        the two findings below
verdict:     narratives attached, none originated
```

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `declared_change_set.py:50` | `HEADING = re.compile(r"^##\s+Declared Change Set\s*$"` | plan's original heading `## Declared Change Set (SCC-226)` returned `present: false` — review's drift check would have fired "absent block" as an important finding; **fixed**: heading normalized, block re-parses 17 entries / 0 incomplete | medium (fixed) |
| `.agents/commands/` listing | `no matches found: .agents/commands/bmad-agent-*.md` | Part E targeted non-existent files; dev would have stalled or invented them. Real set is the 20 `platforms: [opencode]` masters; **fixed**: Part E + change set name the measured set | medium (fixed) |

Pre-mortem narratives: (1) had the heading stayed unparseable, the silent path was a
CONCERNS-flavored review noise storm on an otherwise clean lane — absence must be loud, and it was.
(2) had Part E shipped against `bmad-agent-*`, the other-machine failure was a PC sync run
generating zero zoo persona modes with exit 0 — a vacuous green.

### Observations (uncounted)

- Part A's "stable subset" filter is judgment at dev time; the test pins floor count + spellings +
  no absolute paths, which is the falsifiable part.
- `.roo/` generated dirs are declared at directory level; the drift check may report per-file noise
  at review — acceptable, the manifest is the per-file record.
- `cicd-autopilot-opencode.md` probably stays opencode-only (runtime-specific); decided per file at
  dev time, recorded in the walkthrough.

Audit verdict: GO

### Audit addendum — Part F added then WITHDRAWN (2026-08-29, pre-approval)

Part F (template link edits) was added on an operator report and withdrawn on the operator's
correction the same session: the obligation is already always-on law (`constitution.md:46`), and
per-command template text would be re-read context for a rule agents already carry. Change set
restored to the A–E shape. Verdict unchanged: GO.
