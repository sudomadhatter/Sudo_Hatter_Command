# Implementation Plan — SCC-351 · Zoo Code auto-approve, fixed for real

**Lane:** `chore/SCC-351-zoo-approvals` (consolidated, no subtasks) · **Ticket:** SCC-351 (parent SCC-33)
**Goal:** Zoo seats run at Claude-level automation — the only prompts the operator sees are the
designed hard stops. Fifty approvals a session becomes single digits, and the whole mechanism is
documented once so it never costs another investigation ticket.

## Ground truth (the deep dive this plan stands on — all verified in Zoo v3.80.1 source, matcher extracted and EXECUTED)

1. **Decision store = VS Code globalState** (`state.vscdb`), not `.vscode/settings.json`. The file
   seeds `allowedCommands` exactly once (first activation, key absent); `deniedCommands` NEVER
   seeds; the settings UI displays the union, so the file LOOKS live while deciding nothing.
2. **Matcher:** lowercase starts-with prefix, longest-prefix-wins allow-vs-deny, applied per PIECE
   (split on newlines, `&&`, `||`, `;`, `|`). No wildcards. Heredocs and quoted payloads survive
   as ONE piece; backslash continuations orphan their tails; `$(...)` bodies score as one
   unsplit piece; assignments are inert pieces; `-D`≡`-d` under lowercasing; `git add .` deny
   prefix-collides with our dot-dirs.
3. **`git -C` can never match a verb rule** — and under a broad `git ` allow it would BYPASS every
   verb deny, so it must be auto-denied and the house shape becomes `cd <abs> && git <verb>`.
4. `destructiveCommandGuardEnabled=ON` bypasses the lists entirely (external `dcg` binary) — stays OFF.
5. Measured (551 real commands, real matcher): today 34% auto-approve · new lists 73% · new lists
   + door rewrite ~87%. Battery: 46 destructive commands, 0 approve. Ceremony: 20/20 approve.

## Parts

- **A — Guide** (WRITTEN, in this lane): `docs/migrations/zoo-code-permissions-guide.md` — the
  permanent reference: stores, seeding trap, matcher semantics, canonical lists + rationale,
  apply procedure, shape law, measured record, incident notes (Zoo rewrites `.roomodes`),
  Claude/Antigravity comparison. Update procedure embedded.
- **B — Canonical lists** into tracked `.vscode/settings.json` (`zoo-code.*`): broad families
  (`cd `, `git `, `env -u GITHUB_TOKEN git `, `python3 `, `python `, scoped pwsh, `acli jira
  workitem `, `gh pr `, `gh run `, read-only set, door variables, dot-dir `git add` re-allows,
  lane-scoped `-d chore/`+`--delete chore/`+`claude/` re-allows) + enumerated denies (fs
  destruction, forced/main/mirror/delete pushes, reset --hard/clean/checkout main/branch -D/-M/
  rebase/filter-branch/reflog/update-ref/gc --prune=now/stash drop+clear/remote edits, add
  sweeps, `git -C`, `git --git-dir`, env twins, `gh pr merge`/repo+release delete, acli delete).
- **C — Apply script** `.agents/scripts/zoo_permissions_apply.py`: discovers every `state.vscdb`
  holding the Zoo key (default + VS Code profiles; Mac `~/Library/Application Support/Code`, PC
  `%APPDATA%\Code`), `--status` (counts, toggles, drift vs tracked file), `--apply` (writes both
  lists), refuses while VS Code runs, pure stdlib, both interpreter spellings per two-machines law.
- **D — Tests** `.agents/scripts/tests/test_zoo_permissions.py`: python mirror of the documented
  matcher (prefix/lowercase/longest-wins/piece-split), destructive battery pinned ≥46 rows → 0
  auto-approve, ceremony set → all approve, dot-dir adds approve while bare sweep denies,
  re-allow-beats-deny length checks, tracked-file ↔ guide §6 currency, apply-script source pins
  (refuse-while-running + both stores written). Fixtures fire both ways.
- **E — Shape law**: `command-shape.md` gains §Zoo (the §8 rules); `zoo-team.md` points every seat
  at it; `git-policy.md` §"Pin the merge TARGET" rewritten to the `cd <abs> && git` idiom (same
  pin, matchable shape) with a note that Zoo auto-denies `git -C`.
- **F — Door rewrite**: `git -C <path> <verb>` → `cd <path> && git <verb>` (and `env -u
  GITHUB_TOKEN git -C …` → `cd … && env -u GITHUB_TOKEN git …`) across `.agents/commands/*.md`
  and `.agents/rules/*.md` — ~236 occurrences / 33 files, mechanical sed + hand-check of every
  hunk, full suite green after. Claude runs the same shape (cd + verbs are allowed there).
- **G — SOP** paragraph (operator language: what auto-runs, what still asks and why, the
  three-step apply procedure per machine) + changelog row.
- **H — Memory**: `zoo-approvals-decision-store` memory (globalState + seeding trap + apply
  script + .roomodes-rewrite incident), MEMORY.md line.

## Declared Change Set

(Amendment ledger, review 2nd pass: regenerated from the real landed diff — the build's
consequential set is larger than the plan's first cut and every path is now declared.
`_artifacts/` planning surfaces are carved out by the grammar and stay undeclared here.)

- EDIT `.agents/commands/adviser-board/SPAWNS.md` — git -C to cd && git → F
- EDIT `.agents/commands/cicd-autopilot-claude.md` — git -C to cd && git → F
- EDIT `.agents/commands/cicd-boot-sprint-memory.md` — git -C to cd && git → F
- EDIT `.agents/commands/cicd-clean-code-audit.md` — git -C to cd && git → F
- EDIT `.agents/commands/cicd-close-story-merge-tree.md` — git -C to cd && git → F
- EDIT `.agents/commands/cicd-code-review-AP.md` — git -C to cd && git → F
- EDIT `.agents/commands/cicd-code-review.md` — git -C to cd && git → F
- EDIT `.agents/commands/cicd-create-epic-sprint.md` — git -C to cd && git → F
- EDIT `.agents/commands/cicd-dev-story-tests.md` — git -C to cd && git → F
- EDIT `.agents/commands/cicd-label-tasks.md` — git -C to cd && git → F
- EDIT `.agents/commands/cicd-merge-epic-workingtrees.md` — git -C to cd && git → F
- EDIT `.agents/commands/cicd-non-crit-pr-push.md` — git -C to cd && git → F
- EDIT `.agents/commands/cicd-prune-worktree.md` — git -C to cd && git → F
- EDIT `.agents/commands/cicd-quick-dev.md` — git -C to cd && git → F
- EDIT `.agents/commands/cicd-resume.md` — git -C to cd && git → F
- EDIT `.agents/commands/cicd-self-audit.md` — git -C to cd && git → F
- EDIT `.agents/commands/cicd-write-story-tests.md` — git -C to cd && git → F
- EDIT `.agents/commands/smh-clean-code-audit.md` — git -C to cd && git → F
- EDIT `.agents/commands/smh-close-task-merge-tree.md` — git -C to cd && git → F
- EDIT `.agents/commands/smh-code-review.md` — git -C to cd && git → F
- EDIT `.agents/commands/smh-label-tasks.md` — git -C to cd && git → F
- EDIT `.agents/commands/smh-memory-audit.md` — git -C to cd && git → F
- EDIT `.agents/commands/smh-merge-multiple-workingtrees.md` — git -C to cd && git → F
- EDIT `.agents/commands/smh-plan-task.md` — git -C to cd && git → F
- EDIT `.agents/commands/smh-quick-dev.md` — git -C to cd && git → F
- EDIT `.agents/commands/smh-quick-fix.md` — git -C to cd && git → F
- EDIT `.agents/commands/smh-self-audit.md` — git -C to cd && git → F
- EDIT `.agents/commands/smh-update-maps-indexes.md` — git -C to cd && git → F
- EDIT `.agents/rules/INDEX.md` — shape law → E
- EDIT `.agents/rules/smh-target-resolution.md` — §BIND binds PROJECT_ROOT ABSOLUTE (review 2nd pass: consecutive relative cds) → E
- EDIT `.agents/skills/smh-close-task-merge-tree/SKILL.md` — git -C residual, cd-form (review 2nd pass) → F
- EDIT `.agents/skills/code-review-engine/steps/step-01-review.md` — git -C residual, cd-form (review 2nd pass) → F
- EDIT `.claude/skills/smh-close-task-merge-tree/SKILL.md` — cache recopy of the master (review 2nd pass) → F
- EDIT `.claude/skills/code-review-engine/steps/step-01-review.md` — cache recopy of the master (review 2nd pass) → F
- EDIT `.agents/scripts/tests/run_all.py` — silent-green meta-guard (review 2nd pass) → D
- EDIT `.agents/rules/command-shape.md` — shape law → E
- EDIT `.agents/rules/git-policy.md` — shape law → E
- EDIT `.agents/rules/port-checklist.md` — git -C to cd && git → F
- EDIT `.agents/rules/worktree-per-story.md` — git -C to cd && git → F
- EDIT `.agents/rules/zoo-team.md` — shape law → E
- EDIT `.agents/scripts/tests/test_settings_allowlist.py` — suite conformance to the new law → D
- EDIT `.agents/scripts/tests/test_stale_base_refs.py` — suite conformance to the new law → D
- NEW `.agents/scripts/tests/test_zoo_permissions.py` — matcher mirror + battery/ceremony gate → D
- NEW `.agents/scripts/zoo_permissions_apply.py` — decision-store apply script → C
- EDIT `.agents/workflows/cicd-non-crit-pr-push.md` — regenerated mirror → F
- EDIT `.agents/workflows/cicd-resume.md` — regenerated mirror → F
- EDIT `.agents/workflows/smh-quick-fix.md` — regenerated mirror → F
- EDIT `.opencode/commands/cicd-boot-sprint-memory.md` — regenerated mirror → F
- EDIT `.opencode/commands/cicd-clean-code-audit.md` — regenerated mirror → F
- EDIT `.opencode/commands/cicd-close-story-merge-tree.md` — regenerated mirror → F
- EDIT `.opencode/commands/cicd-code-review.md` — regenerated mirror → F
- EDIT `.opencode/commands/cicd-create-epic-sprint.md` — regenerated mirror → F
- EDIT `.opencode/commands/cicd-dev-story-tests.md` — regenerated mirror → F
- EDIT `.opencode/commands/cicd-label-tasks.md` — regenerated mirror → F
- EDIT `.opencode/commands/cicd-merge-epic-workingtrees.md` — regenerated mirror → F
- EDIT `.opencode/commands/cicd-non-crit-pr-push.md` — regenerated mirror → F
- EDIT `.opencode/commands/cicd-prune-worktree.md` — regenerated mirror → F
- EDIT `.opencode/commands/cicd-quick-dev.md` — regenerated mirror → F
- EDIT `.opencode/commands/cicd-resume.md` — regenerated mirror → F
- EDIT `.opencode/commands/cicd-self-audit.md` — regenerated mirror → F
- EDIT `.opencode/commands/cicd-write-story-tests.md` — regenerated mirror → F
- EDIT `.opencode/commands/smh-clean-code-audit.md` — regenerated mirror → F
- EDIT `.opencode/commands/smh-close-task-merge-tree.md` — regenerated mirror → F
- EDIT `.opencode/commands/smh-code-review.md` — regenerated mirror → F
- EDIT `.opencode/commands/smh-label-tasks.md` — regenerated mirror → F
- EDIT `.opencode/commands/smh-memory-audit.md` — regenerated mirror → F
- EDIT `.opencode/commands/smh-merge-multiple-workingtrees.md` — regenerated mirror → F
- EDIT `.opencode/commands/smh-plan-task.md` — regenerated mirror → F
- EDIT `.opencode/commands/smh-quick-dev.md` — regenerated mirror → F
- EDIT `.opencode/commands/smh-quick-fix.md` — regenerated mirror → F
- EDIT `.opencode/commands/smh-self-audit.md` — regenerated mirror → F
- EDIT `.opencode/commands/smh-update-maps-indexes.md` — regenerated mirror → F
- EDIT `.roo/rules/zoo-team.md` — shape law → E
- EDIT `.vscode/settings.json` — canonical zoo-code allow/deny lists → B
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — SOP + changelog → G
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — SOP + changelog → G
- EDIT `docs/doc-graph.json` — map cache follows the new files → F
- EDIT `docs/doc-graph.md` — map cache follows the new files → F
- NEW `docs/migrations/zoo-code-permissions-guide.md` — the permanent reference → A
- NEW `docs/migrations/terminal-global-permission.md` — cross-agent front door (operator ask, close-out) → A
- NEW `docs/migrations/claude-terminal-permission.md` — operator's rename of the Claude deep dive, landed → A
- DELETE docs/migrations/install_guides/claude-permission-sandboxed.md — renamed to the above → A
- EDIT `docs/repo-map.md` — map cache follows the new files → F

## Acceptance (the checkable list)
1. `test_zoo_permissions.py` green: battery 0 auto-approve · ceremony all-approve · dot-dir adds
   approve · bare sweep denies · lists ↔ guide currency.
2. `grep -r "git -C" .agents/commands .agents/rules` → only the guide/shape-law MENTIONS
   (teaching lines), zero executable occurrences — pinned by a test row.
3. `zoo_permissions_apply.py --status` on this Mac reports state == tracked file after `--apply`;
   refuses while VS Code runs (tested via its source pin + a fake-process probe).
4. Full suite green at tip; SOP + changelog in the same commit as the usage surfaces.
5. Guide readable end-to-end with every path a clickable link.

## Batch approval
**APPROVED** — operator, 2026-08-30, verbatim: "merged lets fix this termianl command requrest
problem now once and for all" (given against the plan as committed at `e157afc9`; PR #105 merged
first, main at `070b6501`). Covers Parts B–H as declared.
