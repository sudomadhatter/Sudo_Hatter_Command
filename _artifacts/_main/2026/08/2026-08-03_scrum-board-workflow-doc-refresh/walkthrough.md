---
IsArtifact: true
ArtifactMetadata:
  title: Scrum-board command + AGY workflows/testing doc refresh
  type: walkthrough
  date: 2026-08-03
---

# Walkthrough — `/sudo-update-scrum-board` + `sudo_workflows_testing.md`

Plan: [implementation_plan.md](implementation_plan.md) (+ `## Self-Audit`, verdict GO)
Branch: `main_debug` · base `63c211c` · **uncommitted** (ad-hoc infra work — no worktree, no story key)

## Task Checklist

- [x] **WS-1 — six edits to [sudo-update-scrum-board.md](../../../.agents/commands/sudo-update-scrum-board.md)** (14,895 → 16,979 B)
  1. Step 1 read-list #7 — the lane's `walkthrough.md` (`Verdict: … @ <sha>`, open `## Your Actions`) and the plan's `## Self-Audit`
  2. Step 2 — the "review passed, not landed" row now names its verdict source and its collapse case
  3. Step 2 — new ⛔ *read the verdict, never infer it; a stale verdict is not a verdict* (with the legacy fallback)
  4. Step 2 — new ⛔ *collapse a landable set into ONE row* → `/sudo-merge-epic-workingtrees <epic>`
  5. Step 2.5 — touch-sets now include every source path the plan's `## Self-Audit` names
  6. Step 3 sources-of-truth gains `_artifacts/`; Step 5 gains check #9 (verdict SHA == branch HEAD, set collapsed)
  - Growth was free: body is over the 11,500 B threshold, so Antigravity ships an auto-generated 914 B thin launcher. Verified post-sync.
- [x] **WS-2 — rewrite [sudo_workflows_testing.md](../../../Projects/AGY_AVIATIONCHAT/_my_resources/_quick_reference/sudo_workflows_testing.md)** (19,519 → 34,190 B, 533 lines, 10 → 13 sections)
  - **The dead links were not dead — F1/F2 were half-wrong.** `tea_deep_reference.md` (53 KB) and `sentry_error_response_team.md` both exist, in the **lobby's** `_my_resources/diagrams_guides/`. The AGY doc is a *relocated copy* still carrying lobby-relative paths. Repointed `../../../../` instead of deleting the depth material; §13 now splits "in this project (`../../`)" from "in the lobby (`../../../../`)" and says why.
  - Plan/audit dispositions for F1 + F2 corrected in place rather than left wrong.
  - New **§5 artifact contract** and **§8 certification contract** written at reference depth only — shape, numbers, file names — each linking its owning rule as authority (audit finding F4).
  - New **§11 scrum board**; §4 loop table gained a "Writes" column and rows for ③'s blind-hunt order and `/sudo-merge-epic-workingtrees`; §7.6 documents the two-place SERIAL pinning; §7.7 verdicts now point at the walkthrough line.
  - Six commands added to §3; `/autopilot-claude` (hyphen) corrected — it exists nowhere, so the doc now says so explicitly; epic kickoff corrected to `/sudo-create-epic-sprint`.
  - Cut: the 07-24 "added X, Y, Z" header note and the `<!-- CHECKPOINT -->` md-feedback marker (F8).
- [x] **WS-3 — propagate** (`/sync-agents`, then `-Maintained`)
  - AGY's `.claude/commands` copy byte-matches master — the F7 case the plan flagged.

- [x] **Follow-on (approved separately) — split the 34 KB reference into two single-purpose docs**
  - **[sudo_workflows_testing.md](../../../Projects/AGY_AVIATIONCHAT/_my_resources/_quick_reference/sudo_workflows_testing.md)** is now the **how-to** — 20,582 B / 312 lines. Gained a `## Start here` situational lookup + section index (the navigation it never had); §2 trimmed 30 → 12 lines.
  - **[sudo_artifacts_and_gates.md](../../../Projects/AGY_AVIATIONCHAT/_my_resources/_quick_reference/sudo_artifacts_and_gates.md)** is new — the **reference**: artifact contract · certification · the test gate · P0–P3 · CI/CD · the autopilot stage contract · who-owns-what. 13,591 B / 249 lines.
  - **Killed a duplication I created:** §7.2–7.5 restated the lobby's 53 KB `tea_deep_reference.md` (its §3 test levels, §4 good-test bar, §7/§7.5 ATDD/BDD, §12 L1–L4). Deleted from AGY, replaced with pointers to the owning doc. §7 TEA-tools table also collapsed — §4's "Under the hood" column already names every workflow.
  - Registered in [`_my_resources/AGENTS.md:14`](../../../Projects/AGY_AVIATIONCHAT/_my_resources/AGENTS.md#L14).
  - ⚠️ **Missed my own size gate on the how-to** — 20,582 B / 312 lines against the ≤18,432 B / ≤280-line target I set in the plan (12% over). Everything genuinely redundant is cut; what's left is the 38-command catalog, which is the doc's primary job. Reported rather than gutted.

## Evidence

| Plan check | Result |
|---|---|
| 1 · retired-artifact mentions labelled legacy/history | ✅ 3/3 (2 in the doc, 1 in the command) — 0 bare |
| 2 · board invariants intact + six edits present | ✅ five zones · ~150-line cap · display rule · grounding gate · quick-dev P2/P3 all unchanged; 7/7 edit markers found |
| 3 · every `/command` named resolves to a real file | ✅ 36/36. Three non-matches are benign: the `` `/` `` in the §3 heading, the generic `` `/command` `` placeholder, and `/autopilot-claude` — which appears **once**, in the line saying it doesn't exist |
| 4 · every markdown link resolves from the doc's own directory | ✅ **17/17** |
| 5 · sync clean, launcher emitted, AGY mirror matches | ✅ launcher 914 B; master == AGY `.claude` / `.opencode` / vendored `.agents`, == Fresh, == lobby `.opencode`, == opencode global |

**Split verification** (`scratchpad/verify_split.sh`):

| Check | Result |
|---|---|
| every link resolves from its own directory, both docs | ✅ 29/29 |
| every `/command` named resolves to a real file | ✅ 38/38 (same 2 benign non-matches as above) |
| curriculum owns zero headings in AGY, exists as pointers | ✅ 0 headings · 2 pointer blocks into `tea_deep_reference.md` |
| size gate | how-to **OVER** (20,582 B / 312 ln vs ≤18,432 / ≤280) · contracts ✅ (13,591 B / 249 ln) |
| no content lost — 27 spot-checked anchors | ✅ 27/27 (2 initially flagged were multibyte-grep false negatives — `Feedback ≠ certification` and `P0 — Critical` both confirmed present) |

Checkers: `scratchpad/verify_ws2.sh` + `verify_split.sh` (scripted, re-runnable). No code changed → no
test suite in scope. These are AGY `_my_resources/` docs — **not** covered by `/sync-agents`.

## Suite Ledger

| Scope | Command | Result | Why this run |
|---|---|---|---|
| link + command + legacy-label + invariant checks | `bash verify_ws2.sh` | pass (1st run: 13/13 links) | plan verification 1–4 |
| same, after the F1/F2 depth-link correction | `bash verify_ws2.sh` | pass (17/17 links) | re-verify after repointing to the lobby |
| toolkit propagation | `sync-agents.ps1` then `-Maintained` | pass | WS-3 |

## Your Actions

**Landed:** nothing committed. **Two repos**, both on `main_debug`, both dirty:

- **lobby** — `.agents/commands/sudo-update-scrum-board.md` + its `.claude` / `.opencode` mirrors +
  `.agents/.sync-manifest.json`, on top of the pre-existing 35-file 08-02 restructure diff
- **AGY** — `_my_resources/_quick_reference/sudo_workflows_testing.md` + its two command mirrors

| # | Pri | Action | Closes |
|---|---|---|---|
| 1 | 🟡 | Say the word and I commit + push both repos (explicit paths) — lobby with or without the 08-02 restructure batch | this session |
| 2 | 🟢 | Lobby doc-hygiene: `_my_resources/diagrams_guides/INDEX.md:13` points at `workflows_tea_testing/sudo_workflows_testing.md`, which **does not exist** — the doc lives only in AGY now. `/update-maps-indexes` owns this; out of this session's approved scope | lobby INDEX accuracy |
| 3 | 🟢 | Restart opencode so the refreshed global command cache is picked up | sync propagation |
| 4 | 🟢 | AGY's `active-context.md` still carries last turn's xdist close-out edit, uncommitted | prior session |
