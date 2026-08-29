# Walkthrough — SCC-346 approval fix + Roo→Zoo / Antigravity→VS Code transition

review-runtime: fan-out
lens_isolation: worktree

- **Lane:** `chore/SCC-346-approval-fix-zoo` (consolidated; rider SCC-349)
- **Plan:** [implementation_plan.md](implementation_plan.md) — batch approval recorded at `ba1cc13`
  (operator, verbatim: "then lets keep pushing and finish this whole ticket")
- **Ticket:** SCC-346 (Bug-typed Task) · rider SCC-349 (Part E)

## What shipped, part by part

- **Part D** (operator-directed, first): the extension migration guide serves VS Code —
  [vscode-ide-extension-migration.md](../../../docs/migrations/install_guides/vscode-ide-extension-migration.md)
  (renamed from `antigravity-ide-extension-migration.md`; `code --install-extension` flow, Roo→Zoo
  Part 0, per-machine checklist + user-settings port table). Inbound links repointed.
- **Part C**: [command-shape.md](../../../.agents/rules/command-shape.md) — run gates BARE (no
  cd-chains, no `; echo "EXIT=$?"` tails, no piped gates); AGENTS.md §6 gate bullet; SOP + changelog
  in the same commit (`3c9e1da`).
- **Part A**: the 77 stable allow rules promoted into tracked
  [.claude/settings.json](../../../.claude/settings.json) with 3 `python` PC twins (80 total); no
  machine-absolute paths (`36f38f8`).
- **Part B**: `zoo-code.allowedCommands` / `deniedCommands` + `zoo-code.useAgentRules` in tracked
  [.vscode/settings.json](../../../.vscode/settings.json); Zoo Code + google-antigravity added to
  [.vscode/extensions.json](../../../.vscode/extensions.json) (`b7b6e36`).
- **Part E** (SCC-349): `zoo` is sync-agents platform 5 —
  [sync-agents.ps1](../../../.agents/scripts/sync-agents.ps1) gained `Sync-ZooSurfaces` generating
  33 [.roo/commands/](../../../.roo/commands/) launchers, [.roomodes](../../../.roomodes) (six BMAD
  personas), per-persona `.roo/rules-<slug>/`, and floor-rule copies in
  [.roo/rules/](../../../.roo/rules/); `zoo` added to the 19 opencode-only masters
  (cicd-autopilot-opencode deliberately kept opencode-only); SOP + changelog same commit (`45e5db8`).
- **Part F**: the three FLOOR rules delivered mechanically on all five platforms —
  [CLAUDE.md](../../../CLAUDE.md) + [GEMINI.md](../../../GEMINI.md) `@` imports,
  [opencode.json](../../../opencode.json) instructions, Zoo via `.roo/rules/` (Part E), Codex via a
  marker-guarded floor block the sync writes into `~/.codex/AGENTS.md` (`9c5eff0`). Verified live:
  this session's own harness injected the three rules from the CLAUDE.md imports.

## Recorded decisions

- The 11 commands declaring `platforms: [opencode, antigravity, claude, codex]` (the main
  smh-/cicd- task-lane doors) were **left untouched** — the approved Declared Change Set names only
  the 20-file `[opencode]` set. Universal commands (no `platforms:` key) reach Zoo automatically
  (33 launchers). Extending the all-four doors to Zoo is a one-line-per-file follow-on if wanted.
- `.roo/` + `.roomodes` are generated-but-TRACKED (they must travel to the PC via git), pruned via
  the GENERATED marker — same contract as the Antigravity workflow mirror; no manifest key needed.
- The machine-global caches on this Mac (opencode, antigravity, codex floor block, codex skills)
  were refreshed from this lane during verification; a post-merge `/smh-sync-agents` from `main`
  re-stamps them from the landed tree.
- AGY repo halves (its allowlist promotion + zoo-code keys) and the `sudo-project-skeleton`
  front-door mirror are DEFERRED — separate repos, ticket per repo; proposed at close-out.

## Evidence

| Claim | Proof |
|---|---|
| Tracked Claude allowlist travels, both spellings, no machine paths | `test_settings_allowlist.py` A1–A4 PASS (count=80, twins=3, bad=[]) |
| Zoo allow/deny lists + extension recommendations travel | B1–B4 PASS |
| Zoo platform 5 wired + surfaces generated | E1–E7 PASS (33 launchers, 6 modes, floor copies present) |
| Floor rules always-on on five platforms | F1–F4 PASS + live confirmation (imports injected into this session) |
| Command-shape rule surfaced | `command-shape.md` exists; AGENTS.md §6 references it; `test_rule_frontmatter.py` 10/10 |
| Guide serves VS Code | guide greps: `code --install-extension` present, no live `agy-ide` step; link gate green |
| Full floor | `run_all.py` 63/63 files @ `aba65b41` (receipt: [gates/suite.json](gates/suite.json), stamped clean-tree) |
| New-test floor | `test_settings_allowlist.py` 26/26 @ `aba65b41` (identity pins, currency, door parity) |

## Task Checklist

- [x] 1 Tracked Claude allowlist (A) — test A1–A4
- [x] 2 Zoo allowlist travels via git (B) — test B1–B4
- [x] 3 Command-shape rule exists and is surfaced (C) — rule + AGENTS.md + SOP row
- [x] 4 Migration guide serves VS Code (D) — landed `987f42c`/earlier, link gate green
- [x] 5 Zoo is sync-agents platform 5 (E) — test E1–E7, sync run output pasted in plan lane
- [x] 6 Floor rules always-on everywhere (F) — test F1–F4
- [x] The merge itself — lands via this branch's PR

## Your Actions

- [ ] **Roo → Zoo import, per machine:** in Antigravity, Roo settings panel → Export; in VS Code,
  Zoo settings panel → Import; then DELETE the export file (it carries API keys — never commit it).
- [ ] **Zoo auto-approve, per machine:** enable the master toggle + tiles once (the allowlists
  themselves arrived via git in `.vscode/settings.json`).
- [ ] **PC pickup:** pull `main` after the merge, run the guide's Part 3–6 (extensions, user
  settings port, `git config --global core.hooksPath .githooks`, `python` spelling check).
- [ ] **DECISION — AVCH ticket for the AGY halves** (promote its 49 local allow rules into tracked
  settings; add its `zoo-code.*` keys) and the skeleton front-door mirror (`@` imports +
  `.roo`/`.roomodes` shape): one ticket per repo, minting is your placement call.

## Code Review (2026-08-29)

Verdict: PASS @ aba65b41
Suite evidence measured @ aba65b41 (run_all.py 63/63 through gate_receipt.py, clean tree; lenses ran against 3cad577f, fixes applied and re-gated at aba65b41 — both shas stated per the concurrency rule).

review-runtime: fan-out
lens_isolation: worktree
lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness · ok — 20-of-110 file cap applied, withheld files named; ONE top-up used (`.roo/commands/cicd-push-e2e.md`, declared)
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none

dispositions:    per-lens: blind-hunter=8/3/0 · edge-case-hunter=7/0/0 · literal-correctness=7/1/0 · acceptance-auditor=5/3/0 · test-adequacy-auditor=9/2/0
drift:           undeclared=85 · unimplemented=3 · incomplete=0 — dispositions in the findings table (62 generated mirrors/manifest/doc-graph absorbed by the plan's directory-level declarations, which also account for the 3 dir-shaped `unimplemented` rows; 19 masters named in the plan's prose as "the measured 20-file set"; 4 true undeclared support edits kept with reasons below)

**Scope:** the full `origin/main...HEAD` diff (110 files) — parts A/B/C/D/E/F plus artifacts.
**Method:** five-lens fan-out (each in a clean context; repo-reading lenses in disposable detached worktrees at `3cad577f`; Blind Hunter starved to the diff), verification folded into cross-lens convergence, assessor triage under the 2026-08-17 disposition ruling, fixes applied in-lane at `aba65b4`, full gate re-run and re-stamped.

**Findings tail (SCC-233 one-liner):** 45 finding-instances came back across five lenses (≈21 unique); 14 unique were assessed real and FIXED in-lane; 7 unique were dismissed under the assessor ruling with reasons recorded below; 0 deferred.

### Findings table (authoritative)

| Finding | Severity | Failure scenario | Disposition |
|---|---|---|---|
| `.vscode/settings.json` bare `git -C` allow prefix | important (3 lenses) | `git -C . push --force` matches the allow, no deny — full destructive-set bypass | applied @ aba65b4 — entry removed, `git add -A/./-u` denies added, comment corrected, pinned by B2b |
| `.roo/commands/cicd-push-e2e.md` unterminated quoted YAML description | important (3 lenses) | quote-blind truncation kept the opening `"`, cut the closing — the one door to `main` unparseable in Zoo | applied @ aba65b4 — quotes stripped before truncation in `Sync-ZooSurfaces`; regenerated; frontmatter parse verified. Antigravity twin (`.agents/workflows/cicd-push-e2e.md`) carries the same PRE-EXISTING defect in untouched code — noted, not gated (its fix must move `Get-AgDescription` and its Python twin `ag_description` together) |
| Codex `~/.codex/AGENTS.md` splice deletes operator text after an orphaned BEGIN; unbounded append on inverted markers | important (2 lenses) | hand-edit or crash leaves a dangling marker → next sync eats operator content between orphan and new block | applied @ aba65b4 — remove-all-blocks + dangle-truncate + single append; verified live on 4 fixture states (none/wellformed/dangling/double): all converge to exactly 1 block, idempotent, outside text kept |
| Test E3 demanded all-marked, generator preserves hand-authored files | important (3 lenses) | first legitimate hand door turns the armed suite red on every lane | applied @ aba65b4 — E3 now `marked >= 10`; contract note in the test |
| No retire path or currency gate for `.roo/rules/` + `.roo/rules-<slug>/` | important (3 lenses) | retired/edited master → stale law injected into every Zoo prompt forever, suite green | applied @ aba65b4 — marker-guarded prunes for both surfaces in `Sync-ZooSurfaces`; E5 now byte-parity (copy vs master body), E9 catches stale launchers |
| Zoo door surface exempt from door-model contract | important | zoo added/dropped on a master with no re-sync → missing/ghost door, no red | applied @ aba65b4 — E8 (eligible→door) + E9 (door→live eligible brain) both directions |
| F4 raw-source grep a comment satisfies; generation call unpinned | important | commented-out codex stage or deleted `Sync-ZooSurfaces` call → green over dead pipeline | applied @ aba65b4 — F4 on comment-stripped source; F5 pins the call site; F0 pins the masters |
| `.roomodes` dev mode "James" vs master's Amelia | suggestion (4 lenses) | user picks James, agent activates as Amelia — one generated block self-contradicts | applied @ aba65b4 — table corrected; E10 pins name-in-brain + roleDefinition target per mode |
| A2/B1/B2 cardinality-only floors | suggestion | 60 junk rules / `["ls"]` pass; deleting the `git push origin main` deny fails nothing | applied @ aba65b4 — sentinel identity pins both sides; A5 syntax pin (the plan's promised assertion, previously unshipped) |
| E7 tested "does not declare zoo", not "explicitly opencode-only" | nitpick | deleting the frontmatter line makes the door universal while the check stays green | applied @ aba65b4 — E7 demands an explicit zoo-free list |
| A3 twin check one-directional | nitpick | a `python`-only rule with no `python3` twin missed | applied @ aba65b4 — bidirectional |
| Floor copies carried routing frontmatter into every Zoo/Codex prompt | nitpick (2 lenses) | prompt noise referencing an INDEX those platforms lack | applied @ aba65b4 — `Get-RuleBody` strips frontmatter for both stages |
| `command-shape.md` grounding overstated ("prefix matcher" as a fact about Claude Code) | suggestion | rule's example could mislead about Claude's per-segment evaluation | applied @ aba65b4 — rule + AGENTS.md bullet reworded (Zoo/opencode prefix-over-string; Claude per-segment, every segment must match); bans unchanged |
| `__import__("re")` obfuscation | nitpick | none (style) | applied @ aba65b4 — proper import |
| Promoted allow rules include `git push origin main*`, `git merge *`, `git checkout *` | important (3 lenses) | permission prompt disappears for main-shaped writes on every clone | dismissed — these are the operator's own learned approvals promoted per Part A's purpose, and every horn has an armed second gate independent of allow rules: `require-push-approval.py` (tracked PreToolUse hook) gates push-to-main and commit-on-main; the armed `merge-target-guard.sh` (MERGE-TARGET-ENFORCE, verified present) refuses a merge whose target is main; `pre-push-main-approval` tokens gate publication. Recorded here so the posture change is operator-visible |
| Three wildcard spellings "incompatible"; 13 rules dead strings | important claim | learned approvals fail to travel on the PC | dismissed — doc-verified by the literal-correctness lens: all three spellings are valid current Claude Code syntax (the rules were machine-written by Claude Code's own approval flow); A5 now pins parseability |
| `Bash(cd:*)` contradicts the rule / approves chains | suggestion | either horn | dismissed — Claude evaluates compound commands per segment, so `cd:*` approves only the `cd` segment; the reworded rule states the accurate mechanism |
| Row 5 letter "manifest rows present" unmet | suggestion | none — letter-vs-precedent conflict inside the plan | dismissed — the plan's own cited precedent (the Antigravity mirror) is not manifest-tracked either; marker-prune now covers every zoo surface, which is the property the manifest row was for |
| Zoo launchers lack `argument-hint`/`mode` frontmatter named in Part E | nitpick | none functional | dismissed — the masters carry no such metadata to project; description is the menu surface |
| `is_root` wiring mutation-transparent | suggestion | `is_root=True` mutation undetected while tree is clean | dismissed — the pure function is pinned in all three directions; the wiring is guarded by the clean tree plus this review class |
| Codex splice deserves a Python-mirror fixture test | suggestion | drift between mirror and PS | dismissed in favor of live verification — the four fixture states were executed through the real PowerShell logic (output above); a second implementation would itself be a drift surface |
| Undeclared support edits (`.agents/rules/INDEX.md`, two test twins, `.sync-manifest.json`, 19 `.opencode/` mirrors) | suggestion | declared-set reconciliation noise | kept, named here: the INDEX row is the rules-INDEX convention for any new rule; the two test twins are the two-parsers-of-one-fact law (`ALL` + adapter allowance); the manifest + mirrors are sync-regenerated caches |

### Gates

- Enforcement suite: `run_all.py` → **63/63 files passed**, exit 0, receipt [gates/suite.json](gates/suite.json) `pass @ aba65b41` (clean tree).
- Toolkit lint: `workflow_lint.py --toolkit-only` → **0 error(s), 0 warning(s), 8 info** (pre-existing testarch BOM notes).
- Assertion evidence: `test_settings_allowlist.py` → **26/26** (blocks A/B/E/F, run bare); `test_entry_adapters.py` → **10/10**; `test_rule_frontmatter.py` → **10/10**; `test_command_surfaces.py` → **231/231**.
- SOP currency: `sop_currency.py --paths <diff>` → exit 0 (SOP page + changelog staged in the C and E commits).
- Link + anchor: `check_links.py --base origin/main` → **clean** (renamed guide scanned; deleted file correctly absent).
- Door parity: `test_command_surfaces.py` 231/231 + new E8/E9 for the zoo surface.

### Acceptance matrix

| Row | Verdict | Proving assertion |
|---|---|---|
| 1 tracked Claude allowlist | satisfied | A1–A5 (count=80, twins both directions, no machine paths, sentinels, syntax) |
| 2 zoo lists travel | satisfied | B1–B4 + B2b |
| 3 command-shape surfaced | satisfied | rule file + AGENTS.md §6 + SOP row; `test_rule_frontmatter.py` 10/10 |
| 4 guide serves VS Code | satisfied | guide greps (`code --install-extension`, no live `agy-ide`); link gate clean |
| 5 zoo platform 5 | satisfied | E1–E10; "manifest rows" letter resolved by the marker contract (finding above) |
| 6 floor always-on | satisfied | F0–F5 + live confirmation (imports injected into this very session) |

### Clean-Code Gate

Machine floor imported from Step 3 (receipt + pasted runs above, per SCC-146 — not re-run). Run here: `py_compile` on the three changed test files → OK; PowerShell parse of `sync-agents.ps1` → OK (plus three real executions). Comment contract §2A: new/changed code carries constraint-stating comments (the splice rationale, the prefix-matcher law, the E3 contract note); no `Story X.Y` provenance applies in the command centre. §2C conventions: stdlib-only tests, no pytest, `Cases` harness used correctly; ASCII-only PS literals held. Drift/bloat findings imported from Step 1 (source `review`) — all in the table above. No banned pattern shipped.

### Step 0.7 — re-derivation

1. Nothing this diff references moved on `main`: zero files landed on main since the branch base (main tip `c71eedf` IS the merge-base); every path and anchor the diff names re-resolved.
2. True overlap: empty; `git merge-tree --write-tree HEAD origin/main` produced a clean tree with no conflict messages.
3. No sibling lanes live (`git worktree list`: main + this lane only); no landing-order dependency.

**Changes applied:** the 14 fixes in the table, all committed at `aba65b4` and re-gated. Walkthrough body refreshed (evidence shas replaced, checklist rows hold). `## Your Actions` triage: all agent-solvable rows were done in-lane; the four open rows above are genuinely operator-only (two per-machine GUI imports, the PC run, one ticket-placement decision).
