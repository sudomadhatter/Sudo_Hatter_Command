---
IsArtifact: true
ArtifactMetadata:
  title: SCC-378 review - resume card (written before a context compaction)
  type: walkthrough
  date: 2026-09-03
---

# SCC-378 — where the review stands (resume card)

> **Superseded 2026-09-03:** the review completed — see `## Code Review (2026-09-03)` in [walkthrough.md](walkthrough.md). Kept as the record of the compaction hand-off.

**Lane:** `chore/SCC-378-permission-parity` · worktree `/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/SCC-378-permission-parity` · **HEAD `59e15eff`** (the reviewed sha; the diff was re-taken there) · SCC-378 `In Progress` · child SCC-382 (Mac) open.
⚠ The shell's cwd may have reset to the MAIN checkout — every command below pins the worktree by absolute path (`cd <worktree> && …` in one line).

## Door position
`/smh-quick-dev` Steps 0–3 DONE → `/smh-code-review` IN PROGRESS → then `/smh-quick-dev` Step 5 (Dev Record) → STOP for the operator.

## `/smh-code-review` — done so far
- Step 0 / 0.5 / 0.7 DONE: `origin/main` = merge-base = `1909df46`; zero overlap; `merge-tree` clean; sibling SCC-383 landed before the lane opened; risk_seam `unclassified` (correct in the centre). **review_level = standard** (radius holds `sync-agents.ps1`, the SOP, a command surface, 3 new scripts).
- Step 0.9: `review-runtime: fan-out` (header already in walkthrough).
- Step 3 gates ALREADY RUN at 59e15eff (paste from these files): suite bare 72/72 (`<scratch>/suite_review.out`); `workflow_lint --toolkit-only` 0 errors (`lint_review.out`); `test_command_surfaces` 322/322 (`cs_review.out`); RED blocks by name A 12/12 · B 15/15 · C 6/6 · D 3/3 · E 5/5 · F 5/5 (`case_*.out`); `test_settings_allowlist` 29/29, `test_zoo_permissions` 25/25; `permission_render.py --check` in sync; `antigravity_permissions_apply.py --status` in sync; `sop_currency.py` silent/green (`sop2.out`); `check_links.py --base origin/main` **clean** after the fix commit 59e15eff (`links2.out`) — before it, two dead `../permissions/` links in the opencode mirror (fixed by citing paths, mirror re-copied).
- Receipt: `gates/suite.json` PASS exit 0 @ `5f9ce171`, `dirty_paths` = the operator's seven untracked `.claude/` files (HIS restored files — do NOT ignore them; a `.gitignore` attempt was reverted in 5f9ce171). Commits since are artifacts-only + the link fix (59e15eff touched `.agents/commands/` + `.opencode/commands/` → receipt tree differs → cite the bare 72/72 run at 59e15eff as the suite evidence, or re-stamp).
- Step 2 declared-set diff (`<scratch>/dcs.out`): `undeclared` = `.agents/permissions/INDEX.md` (check_maps demanded it — keep, named), `docs/doc-graph.json`, `docs/doc-graph.md` (commit hook regenerated — keep, named); `unimplemented` = `.agents/rules/jira.md` (CUT: the "view returns parent" premise was false — `acli … view --fields parent` DOES return it); `incomplete` = none. → `drift: undeclared=3 · unimplemented=1 · incomplete=0`.
- Step 1 ENGINE (`code-review-engine`) launched at 59e15eff with FIVE background lenses, each in its own isolated worktree: Blind Hunter (diff only) · Edge Case Hunter · Acceptance Auditor · Test-Adequacy Auditor · Literal-Correctness Hunter (given the first 20 files' patch at `<lane>/lens-literal-context.patch`, 13 files withheld and NAMED in its prompt). Their results arrive as task notifications. **The diff file:** `<scratch>/scc378.diff`.

## Next, in order
1. Collect the five lens outputs (raw, tagged by lens). Any lens that wrote to the builder tree → `dead — wrote to the tree`, findings discarded. Delete `<lane>/lens-literal-context.patch` after the Literal lens returns (it is untracked review scaffolding).
2. Engine Step 2 (verify): self-gate on RAW count; group same-location/same-claim; Evidence Verifier + Compound Synthesis as subagents with the dossier block (`evidence_extract.py --repo <WORKTREE>`); record skipped waves in notes.
3. Engine Step 3 (triage): normalise severities, dedupe, bucket (decision/patch/defer/dismiss), relevance gate, severity_floor. The assessor rule: REAL · changes BEHAVIOUR · in THIS diff — all three or dismiss.
4. Engine Step 4 (record): findings block; return the summary lines (`review-runtime`, `lens_isolation: worktree`, `lenses_run:` rows, `lenses_counted`, `lenses_na: none` (full mode, standard level → all 5 applicable), `findings:`, `dispositions:`, `severity_floor:`, `notes:`).
5. Fix every `patch` in-lane; walk any `decision_needed` with the operator; re-run scoped checks; if code moved, re-stamp the suite receipt (`gate_receipt.py run --task SCC-378 --gate suite --root <lane> --cwd <worktree> -- python3 .agents/scripts/tests/run_all.py`).
6. Step 3.5: invoke `/smh-clean-code-audit` bound to the worktree; import Step 1 drift findings + Step 3 receipts; py_compile + comment contract + convention table.
7. Step 4: append `## Code Review (2026-09-03)` to `<lane>/walkthrough.md` — FIRST line `Verdict: … @ <sha>`, then the sha the suite was measured on, the `lenses_run:` block UNFENCED + `lenses_counted` + `lenses_na`, `dispositions:` and `drift:` lines, scope/method, ONE findings table, gate results with real output, acceptance matrix A–G, `### Clean-Code Gate`, `### Step 0.7 — re-derivation` with THREE numbered lines. Check with `python3 .agents/scripts/walkthrough_roster.py <walkthrough>` then `--gate --verdict <V>`.
8. Step 5: refresh walkthrough body (tick Step 4 in the checklist), triage `## Your Actions` (three operator rows stay: the `git clean -fd` deny test; commit his `.claude/` files on main; delete the Windows `.gemini` after the two stories land). Commit walkthrough (+ delete this resume card or keep as record).
9. `/smh-quick-dev` Step 5: `python3 .agents/scripts/jira_feed.py devrecord --key SCC-378 --stage quick-dev --walkthrough <walkthrough> --outcome "…" --verdict "…" --decision "…" --pitfall "…" --followon "…" --apply` (never `--append-new`, never `--story`). Then STOP: print plan link · walkthrough link · RED→GREEN · verdict · branch + push state (branch is UNPUSHED — push it: `cd <worktree> && git push -u origin chore/SCC-378-permission-parity`) · what is owed. Close-out is the operator's (`/smh-close-task-merge-tree`).

## Facts that bite
- `acli jira workitem view … --fields parent --json` DOES return `parent`; `jira.md` is right; the plan's jira.md row was wrong and is cut.
- The seven `.claude/*` untracked files are the OPERATOR's restored files. Never ignore, never sweep.
- Every gate runs BARE (no `| tail`, no `; echo $?`); use `> file` then read the file.
- `git -C` is banned; `cd <abs> && git <verb>` in ONE line.
- Antigravity's sandbox does NOT auto-approve; Deny > Ask > Allow is absolute; tokens are anchored regex; the click writes `unsandboxed(...)`, the render writes both types.
- Live Ubuntu store is applied and `in sync` (allow=116, deny=204). Mac = SCC-382.
