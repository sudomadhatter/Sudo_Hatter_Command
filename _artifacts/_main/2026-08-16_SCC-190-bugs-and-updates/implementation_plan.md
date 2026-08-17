# Implementation Plan — SCC-190 · Bugs and Updates — 2026-08 (the rolling ticket, RUN as one lane)

**Lane:** `chore/SCC-190-bugs-and-updates-2026-08` (worktree `.claude/worktrees/SCC-190-bugs-and-updates`, cut off `origin/main` @ `654f7e2`)
**Riders (task.yaml):** SCC-191 (Part R) · SCC-192 (Part S) · SCC-193 (Part T) · SCC-195 (Part U)
**Operator, 2026-08-16:** *"lets do SCC-190"* · *"this will be one tree and one branch for all of them, we will do them all then close it out"* · on SCC-194: *"yeah its stuck there and thats why SCC-195 fixes it"*
**Landing:** full — every rider flips, then the parent; then a fresh rolling ticket is cloned with no subtasks (the description's own first line).
**Approval (2026-08-16):** *"approved"* — recorded at `97f5a97` (plan unchanged since).
**review-runtime:** fan-out (probed at Step 0 — this runtime has the Agent tool).

---

## What was measured before writing this (so the plan is drawn from the code, not the tickets)

| Claim in a ticket | What the repo actually says |
|---|---|
| SCC-192: "task_preflight.py leaves a receipt" | Nothing does. `test_task_preflight_receipts.py` is the SCC-146 **gate**-receipt file (`check_gate`), not a preflight receipt. `main_write_gate.py --mode pr` checks only the branch name + SOP currency (245 lines, no artifact reads). |
| SCC-192 receipt "records the resolved head sha" | ⛔ Cannot: committing the receipt moves HEAD, so a receipt carrying HEAD is never byte-stable and the tree is dirty forever. SCC-192's own loop-1 constraint ("never key on HEAD") wins over its Part A wording — the receipt records the walkthrough's **verdict sha**, like the flight recorder. |
| SCC-193 A: fetch default-on | `--fetch` is `store_true` (line 1321); omitted fetch is `info`, failed fetch is `warn` (876/874). Verdict text is one of two strings (1399). |
| SCC-193 B: content check on `## Your Actions` | `open_actions` / `is_merge_row` / `banned_action_rows` exist (jira_feed 1440–1725). The corpus note at 1519 records **5 open rows that say "merge" and are real product decisions** — so B cannot key on the bare word; it keys on `is_merge_row()` OR a bound ceremony phrase. |
| SCC-193 D: "TWO merge-shaped rows, lane landed → both dropped" | The SCC-164 rows at `5dcc1b7` are: (1) `**Click **Merge** on the PR.**` — no door, no phrase → NOT a merge row → held; (2) `**Then re-invoke** /smh-close-task-merge-tree --after-merge SCC-164` → door → merge row → dropped when landed. So the pin is: door row SATISFIED, click row held — at the `merge_row_state()` seam, because after B `finish` refuses open door rows before it ever computes them. |
| SCC-191: "whatever pins Rule 1's search gains the case" | Nothing pins Rule 1's search today (grep of tests/: zero hits on the jql or the rungs). A pin is added, mechanical (four numbered rungs in order + the label in the jql). |
| SCC-195 / SCC-194 | `origin/chore/SCC-194-workflow-titles` (`932eda1`, 34 files) hand-edits **generated** `.agents/workflows/*.md` descriptions. `test_command_surfaces.py` `door_verdict` demands byte-identity for full mirrors and `fm_field(desc) == brain desc` for launchers → the branch can never go green, and the next `/smh-sync-agents` overwrites it. `Sync-AntigravityWorkflowMirror` copies ≤11.5 KB commands verbatim (long description included) and stubs the rest. |
| Wording surfaces (SCC-193 S5) | grep found ~15 live sites: door Rule 1 / Step 3 / Step 4 table; `git-policy.md:83` ("That click IS the sign-off"); `smh-quick-dev.md:455`, `smh-quick-fix.md:156`, `smh-code-review.md:377` ("invoking it is the operator's per-merge sign-off"); `jira_feed.py:1647,1748` ("THREE things … a main merge"), `render_user_tasks` ("things that only you can do"); SOP 693/730/907–933; `test_door_preflight_order.py:10,333`. `cicd-push-e2e.md:13/100/134` and `cicd-update-sprint-memory.md:229` say "invoking IS the sign-off" — which the ruling **keeps** (invoking `/cicd-push-e2e` is one of the three forms), so those are re-read, not rewritten. |

**Sibling lanes:** `git worktree list` → only `main`. Remote branches: `chore/SCC-186` (0 commits ahead — an empty ref), `chore/SCC-187-caller-ranking` (landed, PR #15), `chore/SCC-194-workflow-titles` (superseded by Part U — see § SCC-194 disposition), `claude/teaching-edition`. No landing-order dependency.

---

## Build order (the overlap map, not a preference)

Files shared across parts are sequenced so each part's RED is measured against the previous part's GREEN:

1. **Part S-A + T-A** — one edit of `task_preflight.py` (receipt + fetch default + verdict freshness). Same function (`check_sync` / `main`), so one part, one RED block.
2. **Part S-B** — `main_write_gate.py --mode pr` receipt demand (reads S-A's receipt shape).
3. **Part T-B + T-D** — `jira_feed.py` content check + the SCC-175 pin.
4. **Part T-C + T wording + S door text** — the door and every wording surface (docs only; grep-pinned).
5. **Part R** — `work-consolidation.md` Rule 1 + engine callout + pin + label.
6. **Part U** — `sync-agents.ps1` + parity test + regenerate. **Last, because it runs `/smh-sync-agents`**, which regenerates every mirror the earlier parts' command edits touched.
7. Gate once at the tip through the receipt writer; one sweep JSON per code part; walkthrough; Dev Record; hand back.

Every commit leads with the **subtask's** key (`SCC-192 feat(preflight): …`); the artifacts/walkthrough commits with `SCC-190`.

---

## Part S — SCC-192 · the ceremony leaves RECEIPTS the PR gate requires

### S-A · `task_preflight.py` writes a receipt (with T-A folded in)

**Receipt:** `<task-artifacts>/preflight-receipt.json`, beside the **live** `task.yaml` (the one `check_manifest` accepted for this branch; if no live manifest → no receipt, and the PR gate later says so). Written at the end of `main()` after the verdict is computed. Content, and only this — nothing that changes when the receipt itself is committed:

```json
{"schema_v": 1, "task_key": "SCC-190", "branch": "chore/…", "verdict_sha": "<walkthrough's governing Verdict sha or null>",
 "fetch_requested": true, "fresh": true, "accept_unpushed_main": false, "lane": "LOCAL",
 "verdict": "clear to close out and merge", "exit": 0, "errors": 0, "warnings": 0,
 "when": "<verdict_sha's commit date, or null>"}
```

- **Idempotent on content:** written only when the bytes differ (A7). `when` is the verdict sha's own commit date (flight-recorder rule) — never wall-clock, never HEAD.
- **Self-dirt exemption:** `check_sync` ignores a dirty path whose basename is `preflight-receipt.json` under `_artifacts/` — the SCC-178 rule (`gate_receipt` excludes its own `gates/`), applied to the one file this script writes. Everything else still counts. The door commits it with the flight event at Step 2.5 (one artifacts-only commit, one push).
- **T-A, same edit:** `--fetch/--no-fetch` via `argparse.BooleanOptionalAction`, default **True** (`--fetch` stays accepted, so the door's line and every caller keep working). Not fresh (`--no-fetch`, or the fetch failed) → `check_sync` **warns** in both cases (severity parity: never trying does not outrank failing) and the verdict line becomes `VERDICT: clear - vs LAST fetch (stale); re-run with fetch` with exit ≥ 1. The old string `clear to close out and merge` prints **only** when fresh and error-free (S1, A6).

**RED (test_task_preflight.py, new block `SCC-192/193: preflight receipt + fetch default`):**
- R1 preflight on a clean pushed lane → `preflight-receipt.json` exists beside task.yaml, `fresh: true`, `verdict` = clear, `fetch_requested: true` (no flag passed).
- R2 `--no-fetch` → verdict line contains `stale`, never `clear to close out and merge`; exit ≠ 0; receipt `fresh: false`; a `[warn ] sync` line (not info).
- R3 fetch FAILED (origin URL pointed at a nonexistent path) → same shape as R2, and the same severity word.
- R4 run twice unchanged → receipt bytes identical (A7); the second run's `sync` says clean (self-dirt exempt) — and a *sibling* dirty file under `_artifacts/` still errs (the exemption is one basename, not a directory).
- R5 receipt carries no `head`/`tip` key and `verdict_sha` equals the walkthrough's stamp.
Existing cases that ran without `--fetch` now fetch from their local bare origins (fresh → unchanged verdicts). Any fixture with no reachable origin gets `--no-fetch` explicitly, or asserts the stale verdict — decided per red, recorded in the walkthrough.

### S-B · `main_write_gate.py --mode pr` REQUIRES the receipts

Scoped exactly as the ticket: `git diff --name-only <base>..<head>` contains a `task.yaml` whose `close_command:` is `smh-close-task-merge-tree` (a PR without one owes nothing — A5). For each such manifest (`task_key`, `branch`), in the **HEAD tree**:
1. the walkthrough beside it → governing `Verdict: … @ <sha>` (reuse `task_preflight.strip_fenced` + `VERDICT_RE`, latest stamp governs — the same reader the flight recorder trusts). No stamp → FAIL, named.
2. `_artifacts/_main/workflow-events/*/<KEY>_<sha7>.json` exists → else FAIL "no flight event for KEY @ sha7" (A1).
3. `preflight-receipt.json` beside the manifest with `task_key`, `branch` matching, `fresh: true`, `verdict` starting `clear` → else FAIL naming which field (A2, A3).
Artifacts-only commits after the verdict sha are irrelevant to this check by construction — nothing here reads HEAD's sha (A4, loop 1). Mode `gate` untouched (loop 2). Manifest with `landing_mode:` or riders: no special casing — the demand is per manifest in the diff.

**RED (test_main_write_gate_ci.py, new block):** A1–A5 as literal cases on a temp repo with a bare origin (fixture: lane commit with task.yaml + walkthrough + stamp; then add event / receipt / two artifacts-only commits per case). Sweep table S (below).

### S-C · the door names the receipt — Step 1 (no new step)
One paragraph under Step 1: the preflight leaves `preflight-receipt.json`; it rides the branch; Step 2.5's commit block adds `<task-artifacts>/preflight-receipt.json` beside `workflow-events/`; the PR gate refuses without it. Rule 2 gains: "and without a fresh fetch it says `stale` — that is not a clear".

**Acceptance S:** A1–A9 (A8 = sweep table S: drop the event demand · drop the receipt demand · drop the fetch=true check · key the receipt on HEAD (must make A4/R4 red) · trigger on every PR (must make A5 red)). SOP row.

---

## Part T — SCC-193 · six slips → four one-shot fixes + the sign-off wording

### T-A — built inside S-A above (S1).

### T-B · `## Your Actions` CONTENT check (jira_feed.py) — the third pattern family
`ceremony_rows(text) -> list[(row, reason)]`: an **open** row that (a) `is_merge_row()` — names a merge door or the canonical phrase — or (b) matches a bound ceremony phrase: `click … merge` / `merge pull request` / `re-invoke` / `--after-merge` / `run|invoke the (close-out|door)` / `Step \d`. Refusal sentence, verbatim: **"this section holds what only the operator decides; the ceremony's steps are not entries."** Exit 2, nothing written; runs in `finish` **before** the board is read, next to `banned_action_rows`; `check-actions` reports it too. `--warn-actions` covers it the same way (one opt-out flag, not two).
- Interaction with SCC-175: a **ticked** canonical row (`- [x] The merge itself — lands via this branch's PR`) is untouched — it is the door's own record and `merge_row_state` still verifies it against ancestry. Only OPEN ceremony rows are refused.
- Fixture: the two SCC-164 rows from `5dcc1b7`, byte-for-byte. Control rows that must stay GREEN: `Decide whether the CONCERNS is worth clearing before the merge` · `Rule the landing order` · `Install the board column` · a ticked canonical row.
- Door Step 3 pre-PR check: `python3 .agents/scripts/jira_feed.py check-actions --walkthrough <wt>` replaces the two greps (it already reports banned rows; now ceremony rows too).

**RED (test_jira_feed.py, new block `T-B`):** S2 red/green as above, plus `finish` on the fixture → exit 2 and no `acli` call (the stub records calls).

### T-C · the door reads ITSELF from origin/main on `--after-merge`
After the ancestry block: `git -C "$REPO" rev-list --count HEAD..origin/main` → if N > 0 print the ⛔ stale-door line naming N and `git show origin/main:.agents/commands/smh-close-task-merge-tree.md`. Same line in the launcher skill's "Execute now" (`.agents/skills/smh-close-task-merge-tree/SKILL.md` — check whether it is GENERATED; if so the line goes in the command and the sync carries it). **RED:** `test_door_preflight_order.py` (the file that already pins the door's text) gains a check that the `--after-merge` block contains the `rev-list --count HEAD..origin/main` line and the sentence "behind origin/main by" — S3.

### T-D · the SCC-175 pin
`test_jira_feed.py` block G gains: real repo, manifest branch present on origin, lane landed, walkthrough with the two SCC-164 rows → `merge_row_state()` returns SATISFIED for the door row; `is_merge_row("**Click **Merge** on the PR.** …")` is False (so it holds, as designed); run twice — once with `GITHUB_TOKEN=deadbeef` in env, once without. Green = the `--apply`-time hold was environmental and the test says so forever; red = the defect, fixed here (S4).

### T-wording · the sign-off is the operator's DECISION
One consistent sentence on every surface: *The operator's decision to proceed is the sign-off. It is given in exactly one of three ways: the word `approved`, or invoking `/smh-close-task-merge-tree`, or invoking `/cicd-push-e2e`. From that word on every step is the ceremony's and the agent runs it. The merge is not an operator task and never appears as an open box; `## Your Actions` holds product decisions.*
Surfaces: door Rule 1 + Step 3 (table row WHY + the "click is the sign-off" paragraph) + Step 4 table · `smh-quick-dev.md` Done box + Your-Actions note · `smh-quick-fix.md` · `smh-code-review.md` Step 5 · `cicd-code-review.md` Step 5 · `jira_feed.py` (SCC-163 comment, `render_banned_banner` "THREE things", `render_user_tasks` "things that only you can do" → "what only you decide") · `git-policy.md` § road to main · SOP (693, 730, 907–933) · `test_door_preflight_order.py:10,333` (comments) · `.opencode/commands/*` via sync. **Memory files are LISTED in the walkthrough, not edited** (S7): `close-out-command-is-daniels-signoff`, `main-merge-needs-operator-verbatim-approval`, `landing-ceremony-is-the-block-not-the-gates`, `git-branch-model-standard`.
**Grep pin (S5), both directions**, in `test_command_surfaces.py`: forbidden phrases (`the merge is the operator's`, `the merge is yours`, `that click is the sign-off`, `THREE things: a product decision, a main merge`, `things that only you can do`, `is the operator's per-merge sign-off`) appear nowhere under `.agents/` (rules, commands, skills, scripts) or `docs/_scc_sops_prds/` except inside the sentence forbidding them (the pin lists its own allow-list: this test file, and one sentence in the door). Positive half: the door's Rule 1 and `git-policy.md` both contain `decision to proceed is the sign-off`.

### ⛔ S6 — the click decision, settled by the operator at THIS stop
(i) **WORDING ONLY** — the click on *Merge pull request* stays a physical operator act; it is HOW the decision reaches GitHub, not a task owed. Nothing mechanical changes. **Recommended** — it keeps SCC-183's "one click, one merge, held by something that cannot be talked out of it".
(ii) **MECHANISM** — after `approved` the agent may run `gh pr merge` (main-write-gate still gates server-side); the click is no longer the operator's.
**SETTLED — operator, 2026-08-16, verbatim: *"i wording only"* → (i).** The click stays a physical operator act; it is HOW the decision reaches GitHub, never a task owed. The door's Rule 1 quotes these words.

**Acceptance T:** S1–S9. Sweep table T: `--fetch` default flipped back · freshness off the verdict line · ceremony check disabled · stale-door line removed · a forbidden wording phrase re-added (must make the pin red).

---

## Part R — SCC-191 · Rule 1 gains the rolling ticket and the cycle

- `work-consolidation.md` Rule 1 → **four rungs**: (1) own ticket → (2) open thematic parent → (3) **the OPEN ROLLING TICKET** (`Bugs and Updates - <YYYY-MM>`; label `bugs-and-updates`; exactly one open; discovered work is a lettered Subtask under it; index-row) → (4) mint, saying what you looked at. Plus **the cycle**: run as one lane (riders, SCC-170 contract unchanged) or split into Tasks; close every subtask and the parent; open the next. "Big enough" is the operator's call — the rule names the cycle, not a threshold. Names SCC-190 as the live instance (R3). Names SCC-192's re-filing as the worked example (R4). The jql block gains the label search so an agent cannot claim "nothing fits" while one is open (R2).
- `code-review-engine/steps/step-01-review.md:447` callout names the rolling ticket as rung 3; `smh-quick-dev.md` Step 1.6 box and `smh-quick-fix.md`'s same box updated (they restate rule 1 — a stale restatement is a second source).
- `jira.md` — check its §Who-mints-tickets seam for a one-line pointer.
- Board: `acli jira workitem edit --key SCC-190 --labels bugs-and-updates` (label add is agent's write; R3), read back.
- **RED (test_command_surfaces.py, new block R):** the rule file has four `^\d\.` rungs under `## Rule 1` in that order with `rolling` on rung 3; the jql block contains `labels = bugs-and-updates`; the engine callout contains `rolling`. Written before the edit, seen red.
- SOP row.

---

## Part U — SCC-195 · the sync emits an Antigravity-sized description; the parity test agrees

**Rule (mechanical, one function, two implementations):** `ag_description(desc)`: if `len(desc) ≤ 135` → unchanged; else cut at the last space at or before 132 chars and append `...` (ASCII, PS-5.1-safe). Character-based on both sides (PowerShell `.Length` is UTF-16 code units; every current description is BMP-only, and the parity test IS the agreement check — a disagreement goes red naming the file).
- `sync-agents.ps1` `Sync-AntigravityWorkflowMirror`: full mirrors are no longer `Copy-Item` — the file is written with its `description:` line replaced by `ag_description(...)`, everything else byte-identical; launcher stubs use the same function. `New-LauncherSkillStub` (Claude/Codex skills) is untouched — Claude has no such cap.
- `test_command_surfaces.py` `door_verdict` for antigravity: legal forms become (a) brain with only the description line replaced by `ag_description(brain desc)`, or (b) a launcher whose description equals `ag_description(brain desc)`. Opencode stays byte-identical (it has no cap and no launcher form). A new check: every `.agents/workflows/*.md` description ≤ 135 chars (the budget, enforced — the thing SCC-194 measured by hand).
- Regenerate: run `/smh-sync-agents` (pwsh is on this Mac at `/opt/homebrew/bin/pwsh`) → the 34 workflow files change; `INDEX.md` and `smh-adviser-board.md` are hand-owned and untouched.
- **RED:** the parity test with the new rule against the current tree → every long-description workflow reads `stale` (before the sync); the ≤135 check red on 34 files. GREEN after the sync.
- **SCC-194 disposition** (operator's call, made by approving this plan): its branch is superseded — Part U delivers what SCC-194's summary asks ("truncate workflow titles and update sync script"). At close-out: comment on SCC-194 linking this landing, transition it to Done, and delete `origin/chore/SCC-194-workflow-titles` (a delete of another lane's ref — named here so `approved` covers it; nothing on it survives Part U anyway). Its hand-written summaries are **not** harvested: they cannot be regenerated by a machine, which is the whole defect.
- Sweep table U: truncation length off by one · `...` dropped · the parity test comparing raw descriptions again · the ≤135 check removed.
- SOP row (the SOP's `/smh-sync-agents` entry says descriptions are shortened for Antigravity and why).

---

## Verification — one block at the tip (work-consolidation rule 3)
Per part: its own test file, `--case`-scoped during the loop, whole file once after the last fix. For the lane: `gate_receipt.py run --task SCC-190 --gate suite -- python3 .agents/scripts/tests/run_all.py` once on the landing code · `workflow_lint.py --toolkit-only` · `check_maps.py --depth3-only --strict` · `mutation_sweep.py` per table (S, T, U; R is a doc pin — its mutant is the phrase removed, run through the same harness) · link+anchor sweep on the door and rule edits · SOP staged in every usage-surface commit.

## What is NOT built (on purpose, from the tickets)
No rule/memory for slips 1, 2, 6 · no general Your-Actions schema · no new bypass flag on the PR gate (break-glass stays `enforcement=disabled`) · no change to Road 2 or project repos · the lane-ownership gap (ListAgents) stays recorded, not built · the "ticket transition as an operator thing" tension named, not touched · no memory file edited (S7).

## Steps → assertions (summary)
| # | Step | Assertion that proves it |
|---|---|---|
| 1 | S-A/T-A preflight receipt + fetch default | test_task_preflight R1–R5 |
| 2 | S-B PR gate demands receipts | test_main_write_gate_ci A1–A5 |
| 3 | T-B ceremony rows refused; T-D pin | test_jira_feed new blocks |
| 4 | T-C stale-door line; wording; S-C door text | test_door_preflight_order S3; wording pin S5 |
| 5 | R rule + callout + label | test_command_surfaces block R; `acli view SCC-190` shows label |
| 6 | U sync + parity + regen | test_command_surfaces antigravity checks; ≤135 |
| 7 | gate at tip, sweeps, walkthrough, Dev Record | receipt under gates/, sweep records, `jira_feed.py devrecord` exit 0 |

---

## Self-Audit (2026-08-16) — PRE-WORK, Full

Repo: `Sudo_Hatter_Command` | Branch: `chore/SCC-190-bugs-and-updates-2026-08` (from `rev-parse`). Plan: this file. Key: SCC-190, riders SCC-191/192/193/195.

**Phase 0 — scope.** Change set: `task_preflight.py` · `main_write_gate.py` · `jira_feed.py` · `sync-agents.ps1` · tests `test_task_preflight.py`, `test_main_write_gate_ci.py`, `test_jira_feed.py`, `test_door_preflight_order.py`, `test_command_surfaces.py` · commands `smh-close-task-merge-tree.md`, `smh-quick-dev.md`, `smh-quick-fix.md`, `smh-code-review.md`, `cicd-code-review.md` · rules `work-consolidation.md`, `git-policy.md`, (`jira.md` pointer) · `code-review-engine/steps/step-01-review.md` · SOP · 34 regenerated `.agents/workflows/*.md` + regenerated `.opencode/commands/*` and launcher skills. **Full** audit: rules, a gate, scripts other scripts import (`task_preflight` is imported by six scripts), four platform surfaces. Checkable list = the four tickets' ACCEPTANCE blocks (A1–A9, S1–S9, R1–R4; SCC-195 has none → U's list written above: parity legal forms, ≤135 enforced, regen green). Traceability: every plan step maps to an item; no step without one. Lane: no deployable path (`.github/` is named "only if a new arg is needed" — **it is not**: `--mode pr` already receives base/head/branch, so the yml is untouched and the lane stays LOCAL).

**Phase 1 — blast radius (grep-measured).**
- `task_preflight.py` importers: `flight_recorder`, `gate_receipt`, `closeout_preflight`, `evidence_extract`, `hooks_armed`, `lane_qualify`, `walkthrough_roster` — all import names (`VERDICT_RE`, `strip_fenced`, `PRODUCT_DIRS`, …), none reads `args.fetch` or the verdict string. `merge-target-guard.sh` mentions it in prose only. Callers passing `--fetch`: the door (140) and `smh-merge-multiple-workingtrees.md` (119) — both keep working under `BooleanOptionalAction`. `closeout_preflight.py` has its own `--fetch` (store_true, line 360) — **out of scope** (project lane, `/cicd-*`); named so nobody "harmonises" it here.
- `main_write_gate.py`: run only by the CI yml and `test_main_write_gate_ci.py`; imports `sop_currency`. It will now import `task_preflight` (for `VERDICT_RE`/`strip_fenced`) — same directory, same pattern as the flight recorder.
- `jira_feed.py finish` / `check-actions`: called by the door Step 4 and by nothing else; `test_jira_feed.py` legacy block B (1470) runs `finish` fixtures — any that carry an OPEN door row now exit 2 instead of 3. Expected under the ruling; each such case is re-aimed and named in the walkthrough.
- `work-consolidation.md`: `workflow_lint._RULE_POINTERS` has a `("work-consolidation", "consolidating", …)` row → the rule's citations must survive; four commands cite it (grep above) and none is renamed.
- `sync-agents.ps1`: `test_command_surfaces.py` parses `$excluded` out of it (line 95) — the exclusion list is not moved. Hand-owned `smh-adviser-board.md` + `INDEX.md` untouched.
- Skill `smh-close-task-merge-tree/SKILL.md` is a **generated** launcher (1.4 KB, "GENERATED" marker absent from the head but body is the stub form) — the T-C line goes in the command; the sync carries it. ⚠ verify the marker at build time; if hand-owned, edit both.
- Sibling lanes: none live (`worktree list` = main only). `origin/chore/SCC-194-workflow-titles` overlaps Part U's 34 files by construction — it is superseded, not a landing-order dependency.
- SOP: every usage-surface commit stages `workflows_testing_SOP.md` (rows for R, S, T, U) or is `[sop-ok]` for test-only commits.

**Phase 2 — over-engineering.** No new command, rule, or script. New receipt file type — required by A1–A7. `--no-fetch` — required by S1. `ceremony_rows` sits beside `banned_action_rows` (a third family, same reader, same banner plumbing) — not a schema. `ag_description` exists twice (PS + Python) — a deliberate two-parser pair, and the parity test is the thing that keeps them agreeing (the same shape `fm_field`/`Get-CommandPlatforms` already live in). No flag beyond acceptance. **One tripwire fired and is cut:** the plan's first draft demanded a flight event for *every* task.yaml with the door's `close_command` — see finding F1.

**Phase 3 — pre-mortem.**
| Scenario | Handled? | |
|---|---|---|
| Other machine | `python3` everywhere with the PC note; the ps1 runs under pwsh here and PS 5.1 there (ASCII-only stub literals kept) | ✅ |
| Fresh clone | the PR gate is server-side (`bypass_actors []`), receipts are content in the tree — nothing to arm | ✅ |
| Gate fires on someone else's commit | S-B's failure text names the key, which artifact is missing, and the door step that writes it | ✅ |
| Escape hatch | unchanged: `enforcement=disabled` on the ruleset, documented; `--no-fetch` prints itself into the verdict | ✅ |
| Empty input | no task.yaml in the diff → no demand (A5, by ticket). task.yaml present but walkthrough/receipt missing → FAIL, never pass. Empty `## Your Actions` → still closes | ✅ |
| Four platform caches | `/smh-sync-agents` runs LAST, after the ps1 edit, so the regen uses the new rule; the parity test proves all four | ✅ |
| Sibling lane lands first | none live | ✅ |
| Rollback | code: git. Board: SCC-190 label (harmless), SCC-194 Done + branch delete (named for `approved`; `932eda1` stays in the local reflog). Regenerated workflows: git | ✅ |
| **Offline close-out** | fetch fails → `stale` verdict, exit 1, receipt `fresh:false` → the PR gate would refuse. Correct: a PR needs GitHub anyway; there is no offline PR | ✅ |

Failure modes that survive: (silent) a follow-on PR whose task.yaml is *unchanged* is not in the diff → not gated — inside the ticket's stated scope ("the PR diff carries a task.yaml"), recorded, not built. (other-machine) PowerShell `.Length` vs Python `len` on a non-BMP character — would show as a red parity check naming the file, not silently.

**Findings**
| where | sev | failure scenario | disposition |
|---|---|---|---|
| F1 · Part S-B | **HIGH** | `/smh-quick-fix` lanes write `task.yaml` with `close_command: smh-close-task-merge-tree` and have **no review verdict** (10 landed lanes measured with no `Verdict:` line); `flight_recorder record` dies without a stamp (`build_event`, line 199). Demanding a flight event on every such manifest refuses **every lightweight lane** — SCC-192's own loop-3 constraint broken. | **Baked in:** the receipt is demanded for every door-manifest in the diff; the flight event is demanded **only when the walkthrough carries a governing `Verdict:` stamp** (a reviewed lane — the one that can and must record). Case A5b added: quick-fix shape (manifest + receipt, no stamp) → passes. |
| F2 · T-wording pin | MED | first-draft forbidden list included `is the operator's per-merge sign-off`; `cicd-push-e2e.md:13/100/134`, `cicd-update-sprint-memory.md:229` and the door-invoking lines in `smh-quick-dev/quick-fix/code-review` say invoking the command IS the sign-off — which the ruling **keeps** (two of the three forms are invocations). A pin on that phrase would force deleting true sentences. | **Baked in:** forbidden set = `the merge is the operator's` · `the merge is yours` · `that click is the sign-off` · `click IS the sign-off` · `THREE things: a product decision, a main merge` · `things that only you can do` · `you merge it`. The invocation sentences are re-read against the ruling and kept. Door Rule 1 is rewritten (its current text says the invocation is *not* the sign-off, which the ruling contradicts). |
| F3 · S-A receipt | MED | receipt written **before** the verdict is final would record a stale verdict; written with HEAD would never converge | Baked in: written last in `main()`, verdict-sha keyed, `when` = that sha's commit date, byte-compare before write; self-dirt exemption is one basename |
| F4 · T-B vs SCC-175 | LOW | refusing OPEN door rows at `finish` makes some legacy-B `finish` fixtures flip 3→2 | Named; re-aimed at build, each listed in the walkthrough |
| F5 · Part U | LOW | door_verdict currently demands byte-identity for antigravity full mirrors; the SCC-194 branch proves the parity test blocks the very fix | Baked in (U's legal forms) |

**Four quick gates.** Verification strategy present — every item names its test/command. Irreversible — SCC-194 transition + remote branch delete, SCC-190 label; all named for `approved`, executed at close-out only. Vague steps — S6 (i)/(ii) is deliberately the operator's; everything else is pinned to a file:line. Convention fit — subtask key per commit, `[sop-ok]` only on test-only commits, artifacts in `_artifacts/_main/2026-08-16_SCC-190-bugs-and-updates/`, sync last.

Audit verdict: GO
