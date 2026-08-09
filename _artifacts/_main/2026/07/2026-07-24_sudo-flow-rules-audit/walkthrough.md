---
IsArtifact: true
ArtifactMetadata:
  title: Walkthrough — sudo flow + rules audit fixes (F1–F12) + quick-dev hardening
  type: walkthrough
  date: 2026-07-24
---

# Walkthrough — audit fixes applied + synced

Round 2 of the sudo-flow audit initiative (the session folder predates this chat — commit `5ed4330`
documented the earlier findings; this session's [audit report](2026-07-24_sudo-flow-rules-audit.md)
and [plan](implementation_plan.md) replaced the prior uncommitted plan draft, whose committed version
remains in git history). Daniel answered the plan's open questions (F8 → diff-scoped stacks;
quick-dev → full hardening) and the fixes were applied and synced.

## What changed, file by file (lobby masters)

- **[sudo-update-sprint-memory.md](../../../../../.agents/commands/sudo-update-sprint-memory.md)** —
  12,420 → **11,903 chars** (back under the 12k Antigravity workflow limit). Step 2 renamed to
  *"Verify the claimed work exists on disk (grep-check — NOT a code review)"*; `(G1)` dropped from
  the H1; ~10 explanatory parentheticals compressed. Every gate and contract (no-punt flip, fail-open
  verdict read, explicit-paths ban, Step 7/8 landing) is semantically unchanged.
- **[constitution.md](../../../../../.agents/rules/constitution.md)** — the `continue`-as-authorization ban
  now carries its ONE exception: a gate word a sudo command's own body defines (②'s Step-2
  `continue`; invoking close-out as sign-off) IS explicit approval for exactly that step. The
  code-review bullet now names both review-output homes (session `code-review.md` + the machine-read
  verdict file) so neither gets "fixed" away.
- **[000-PLAN-FIRST-GATE.md](../../../../../.agents/rules/000-PLAN-FIRST-GATE.md)** — both `task.md`
  mentions replaced with the current TodoWrite + walkthrough-checklist contract; no other changes.
- **[sudo-boot-sprint-memory.md](../../../../../.agents/commands/sudo-boot-sprint-memory.md)** — orphaned
  G2/G3/G5/G6/G8 numbering dropped (same five checks, plainly named); the Firestore line generalized
  to shared-resource singleton; `(G1)` and the "Guardrail G1" sentence removed.
- **[sudo-code-review.md](../../../../../.agents/commands/sudo-code-review.md)** (11,906 chars) — three
  behavior changes: **(1)** Step 3.1 suites are diff-scoped by stack (other stack only on shared
  cross-boundary surface changes; PR CI + `/sudo-e2e` still run both pre-ship); **(2)** the
  CI-entrypoint audit + soft-step scan are change-triggered via a `ci_audit: {sha, date}` record in
  `sudo-tests.yaml` (re-audits exactly when `.github/workflows/**` or test configs changed);
  **(3)** Step 3.5 no longer re-hunts the AI-drift bans Step 1 already hunted — it imports those
  findings and runs the machine floor + comment contract.
- **[clean-code-audit.md](../../../../../.agents/commands/clean-code-audit.md)** — matching note: Part B
  (drift bans) is standalone-only; inside ③ it imports the review's findings.
- **[sudo-code-review_AP.md](../../../../../.agents/commands/sudo-code-review_AP.md)** — the robot twin
  mirrored (memory: `_AP` twins drift): its check 4's (a)/(c) CI audits now use the same
  change-trigger; the fiction-red check (b) stays per-story. Suite scoping/Step 3.5 don't exist in
  the twin (the orchestrator owns the suite), so nothing else applied.
- **[sudo-quick-dev.md](../../../../../.agents/commands/sudo-quick-dev.md)** — rewritten (3,274 → 5,062
  chars): worktree Step 0.5; root-cause-first line; the **EJECT TRIPWIRE** (~3 files / ~150 lines or
  any protected surface — auth/tenancy, payments, PII, DB schema/rules, cross-boundary contracts →
  STOP, hand to ①, keep the worktree); scoped verification with the one-pinning-regression-test rule
  for bug fixes; `/clean-code-audit` (full pass) replacing the misfit pre-dev self-audit; Done section
  now states the git contract (commit in worktree, explicit paths, never land).
- **[sudo_workflows_testing.md](../../../../../_my_resources/_quick_reference/sudo_workflows_testing.md)** —
  kickoff command corrected to `/sudo-create-epic-sprint` in all four places; ③'s order fixed
  (review → test gate → clean-code → verdict); quick-dev row rewritten for the new lane; yaml sample
  gained the `ci_audit` comment line; clean-code section notes the drift-findings import.

## Verification (actual output)

Char counts after edits (limit 12,000):

```
sudo-update-sprint-memory    11903
sudo-code-review             11906
sudo-code-review_AP           7390
clean-code-audit              7477
sudo-quick-dev                5062
sudo-boot-sprint-memory       6433
```

`/sync-agents -Maintained` ran clean: lobby (18 AG workflow mirrors, 18 `.claude` + 44 `.opencode`
cmds, opencode/antigravity/codex globals refreshed) + AGY_AVIATIONCHAT + Fresh_Workspace_BMAD (18
mirrors + 21/47 cmds each); **Fresh living-template drift-check OK**. ② (`sudo-dev-story-tests.md`)
deliberately untouched at 11,988.

## Task Checklist

- [x] Implementation plan drafted; open questions answered by Daniel (F8 → diff-scoped stacks)
- [x] F1+F11 close-out trimmed under 12k + Step 2 renamed
- [x] F2+F12 constitution gate-word carve-out + review-output homes
- [x] F3 `task.md` purged from 000-PLAN-FIRST-GATE
- [x] F4 boot guardrail numbering fixed
- [x] F5 ③ double drift-hunt removed (+ clean-code-audit note)
- [x] F6 CI audit change-triggered (③ + `_AP` twin)
- [x] F7+ quick-dev hardened (worktree · eject tripwire · scoped tests · clean-code audit)
- [x] F9+F10 quick-ref corrected
- [x] Char counts verified; `/sync-agents -Maintained` clean
- [ ] Commits — owed in 3 repos (Daniel's git lane; commands below)

## Your Actions

Lobby toolkit maintenance ran in the shared checkout (HEAD `main_debug`), so per git-policy G1 no
agent commit was made — the commit is yours. **Pre-existing unrelated changes are in all three trees**
(lobby: `.gitignore`, `todo_list.md`, `repo-map.md`, `_system/*` env scripts) — the explicit paths
below exclude them.

**Lobby** (`Sudo_Hatter_Command`, `main_debug`):
```powershell
git add .agents/commands .agents/workflows .agents/rules .claude/commands .opencode/commands _my_resources/_quick_reference/sudo_workflows_testing.md _artifacts/_main/2026-07-24_sudo-flow-rules-audit _artifacts/INDEX.md
git diff --cached --stat   # must show ONLY the paths above
git commit -m "chore(sudo-flow): audit fixes - close-out under AG limit, gate-word carve-out, change-triggered CI audit, diff-scoped suites, quick-dev hardening, quick-ref corrections"
```

**AGY_AVIATIONCHAT** and **Fresh_Workspace_BMAD** (sync-vendored copies, each on `main_debug`):
```powershell
git add .agents .claude/commands .opencode/commands
git diff --cached --stat
git commit -m "chore(toolkit): vendor synced .agents - sudo-flow audit fixes 2026-07-24"
```

Still open for a future session: nothing from this audit — all 12 findings closed or deliberately
descoped (② untouched at its char ceiling).
