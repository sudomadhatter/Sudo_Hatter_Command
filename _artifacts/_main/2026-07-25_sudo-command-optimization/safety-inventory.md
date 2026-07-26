---
IsArtifact: true
ArtifactMetadata:
  title: sudo command safety-obligation inventory (pre-optimization baseline)
  type: implementation_plan
  date: 2026-07-25
---

> Baseline inventory of every gate/STOP/obligation in the sudo command set, captured BEFORE the slimming pass.
> The optimization is only done when every line below survives in the slimmed file or its pointed-to rule.

All files read in full. Master copies are in `.agents/commands/`; the 11 `.agents/skills/sudo-*/SKILL.md` files are 10–21-line launcher pointers only (they contain no executable content beyond Step-0 restatement — see the note at the end).

---

# PART 1 — Per-file breakdowns

## 1. `sudo-adviser-board.md` — 690 lines / 52,671 bytes
`c:\Users\dlohn\.gemini\antigravity\scratch\Sudo_Hatter_Command\.agents\commands\sudo-adviser-board.md`

| Lines | Section | Class | ≈len |
|---|---|---|---|
| 1–4 | frontmatter (single ~1.5KB description line) | metadata | 4 |
| 6–30 | Title, purpose, "How the table speaks", roster source-of-truth pointer | (d) RATIONALE | 25 |
| 31–41 | `## Arguments` (`--solo`, `--model`) | (a) EXEC | 11 |
| 42–60 | `## The chair — the operator runs this meeting` (4 numbered rules) | (b) GATE | 19 |
| 62–70 | `## Prime directive — minds, not scripts` | (d) RATIONALE | 9 |
| 71–88 | `## Open-table norms` (6 legal moves table) | (d)/(a) | 18 |
| 89–236 | `## The Board — 5 teams, 21 seats` + Real-World squad + Bench — 30+ persona bios (anchor/move/at-the-table) | **(d) RATIONALE/BACKGROUND** | **148** |
| 237–262 | `## The Third-Side Question Bank` table | (d) reference | 26 |
| 263–357 | `## The caucus, the presentation, and the card` (caucus rules · presentation contract · card slots · card discipline) | (a)+(b) | 95 |
| 358–364 | `### Caucus honesty` | (b) GATE | 7 |
| 366–380 | `### Spokesperson mode` | (a) EXEC | 15 |
| 381–442 | `## Session arc` + **Standing rules (all phases)** | (a)+(b) | 62 |
| 443–506 | Phases 0–4 (Activation · Brainstorm · Plan · Market · Brief) | (a)+(b) | 64 |
| 507–628 | `## Spawn templates` (team · individual · reopened room · spokesperson · Real-World) | (a) EXEC — **but ~90% verbatim restatement of L263–357** | 122 |
| 630–645 | `## Tone Dial` table | (a) reference | 16 |
| 647–681 | `## Session brief template` | (a) template | 35 |
| 683–691 | `## Exit` | (b) GATE | 9 |

**Category totals:** (a) ≈330 · (b) ≈55 · (c) ≈5 (only the REFERENCE-doc roster pointer) · (d) ≈215 · (e) ≈5 (no Step-0 project resolution at all — lobby-only command).
**Internal duplication (not rule duplication):** the caucus/presentation/card contract is stated twice — once as spec (263–357) and again inline in the team spawn template (533–581).

## 2. `sudo-update-sprint-memory.md` — 180 lines / 14,219 bytes

| Lines | Section | Class | ≈len |
|---|---|---|---|
| 1–4 | frontmatter | metadata | 4 |
| 6–11 | Title + "Active-context holds STATE, not history" preamble | (d) | 6 |
| 13–30 | Step 0 — Resolve target project + binding rule | **(e) BOILERPLATE** (+1 gate) | 18 |
| 32–40 | Step 1 — Read state & session artifacts (scoped reads) | (a) | 9 |
| 42–47 | Step 2 — Verify claimed work on disk (grep-check) | (a)+(b) | 6 |
| 49–61 | Step 3 — Route learnings to the 4 homes | (a) | 13 |
| 63–84 | Step 4 — Apply updates / **story-status flip** | (b) GATE-dense + (d) 31k-token history | 22 |
| 86–120 | Step 5 — Prune & budget | (a)+(b)+(d) `_archive` prose, OIDC cautionary case + (c) the "map" of other files' jobs | 35 |
| 122–140 | Step 6 — §5 artifacts, summary, memory write, manual catch | (a)+(b) | 19 |
| 142–171 | Step 7 — Land on `main_debug` | (a)+(b) — **near-verbatim `git-policy.md` "The landing"** | 30 |
| 173–180 | Step 8 — Prune merged worktree (delegates to `/sudo-close-workingtree`) | (a) | 8 |

**Category totals:** (a) ≈85 · (b) ≈35 · (c) ≈12 · (d) ≈20 · (e) ≈24.

## 3. `sudo-self-audit.md` — 173 lines / 10,626 bytes

| Lines | Section | Class | ≈len |
|---|---|---|---|
| 1–4 | frontmatter | metadata | 4 |
| 6–19 | Title, intro, "no build commands here → use `bmad-code-review`" callout | (d)+(c) | 14 |
| 22–42 | Step 0 — target project + binding rule | **(e)** | 21 |
| 45–60 | Phase 0 — Scope, Right-Size & AC Coverage | (a)+(b) | 16 |
| 63–102 | Phase 1 — Blast-Radius Trace (incl. **GitNexus MCP tool explainer ~12 lines**) | (a)+(c) | 40 |
| 105–127 | Phase 2 — AI Drift & Over-Engineering Gate (9 tripwires) | **(b) GATE** | 23 |
| 130–148 | Phase 3 — Adversarial Scenarios / Pre-Mortem table | (a) | 19 |
| 151–166 | Phase 4 — Verdict + four quick gates | (b) | 16 |
| 169–173 | Notes | (d) | 5 |

**Category totals:** (a) ≈70 · (b) ≈35 · (c) ≈15 · (d) ≈25 · (e) ≈24.

## 4. `sudo-dev-story-tests.md` — 157 lines / 11,988 bytes

| Lines | Section | Class | ≈len |
|---|---|---|---|
| 1–4 | frontmatter | metadata | 4 |
| 6–11 | Title + flow position | (c) nav | 6 |
| 13–32 | Step 0 — target project + binding rule | **(e)** | 20 |
| 34–46 | Step 0.5 — Resolve/create ARTIFACT_DIR | (a)+(e) — copy of `artifacts-always-first` §2 | 13 |
| 48–55 | Step 0.6 — Re-enter existing worktree | (a)+(e) — copy of `worktree-per-story` "Resuming" | 8 |
| 57–68 | Step 0.7 — **BDD contract gate (HARD)** | (b) | 12 |
| 70–72 | Step 1 — Plan (`bmad-dev-story` PLAN mode) | (a) | 3 |
| 74–102 | Step 2 — **Self-audit STOP gate** (continue / changed / pasted-path / skip) | **(b) — largest gate block in the repo** | 29 |
| 104–111 | Step 2.5 — Conditional ask-first gate | (b) | 8 |
| 113–121 | Step 3 — Implement (red→green) | (a)+(b) | 9 |
| 123–128 | Step 4 — Automate (expand coverage) + evidence | (a)+(b) | 6 |
| 130–147 | Step 5 — Close-out artifacts checklist | (b)+(e) | 18 |
| 149–157 | Done (status/git lane rules) | (b) | 9 |

**Category totals:** (a) ≈45 · (b) ≈65 · (c) ≈8 · (d) ≈10 · (e) ≈29.

## 5. `sudo-code-review.md` — 146 lines / 11,906 bytes

| Lines | Section | Class | ≈len |
|---|---|---|---|
| 1–4 | frontmatter | metadata | 4 |
| 6–13 | Title + "both gates live HERE" + flow position | (c) | 8 |
| 15–36 | Step 0 — target project + binding rule | **(e)** | 22 |
| 38–44 | Step 0.5 — Re-enter story worktree | (a)+(e) | 7 |
| 46–47 | Step 1 — Clean-Room adversarial review (`bmad-code-review`) | (a) | 2 |
| 49–52 | Step 2 — Gate: opt-in check (`sudo-tests.yaml`) | (b) | 4 |
| 54–81 | Step 3 — Gate: run the checks (suite · trace · nfr · test-review · automate evidence) | (a)+(b) | 28 |
| 83–103 | Step 3.5 — Gate: clean code | (b)+(c) explains `clean-code-audit` internals | 21 |
| 105–121 | Step 4 — Verdict (PASS/CONCERNS/FAIL/WAIVED) | (b) | 17 |
| 123–138 | Step 5 — Update the story walkthrough | (a)+(b) | 16 |
| 140–146 | Stay in lane | (b) | 7 |

**Category totals:** (a) ≈35 · (b) ≈65 · (c) ≈15 · (d) ≈5 · (e) ≈26.

## 6. `sudo-code-review_AP.md` — 96 lines / 7,390 bytes (autopilot twin)

| Lines | Section | Class | ≈len |
|---|---|---|---|
| 1–4 | frontmatter | metadata | 4 |
| 6–14 | Headless context + Murat persona + `bmad_code_review_sudo_fix.md` pointer | (c) | 9 |
| 15–20 | Your direction (files in the shared run folder) | (a) | 6 |
| 21–28 | The work (one pass — 3 review passes + fixes) | (a)+(b) | 8 |
| 30–65 | The test gate (TEA layer only) | (b)+(a) — compressed copy of ③ Step 3 | 36 |
| 67–92 | Stay in lane / human-in-the-loop (artifact contract, OUT-OF-SPEC, OPEN QUESTIONS, Close-Out Handoff) | (b)+(a) | 26 |
| 94–96 | PIPELINE_BLOCKER protocol | (b) | 3 |

**Category totals:** (a) ≈30 · (b) ≈45 · (c) ≈8 · (d) ≈3 · (e) ≈10. **No Step 0 project resolution** (the orchestrator supplies the run folder).

## 7. `sudo-dev-story-tests_AP.md` — 79 lines / 5,838 bytes (autopilot twin)

| Lines | Section | Class | ≈len |
|---|---|---|---|
| 1–4 | frontmatter | metadata | 4 |
| 6–10 | Headless launch context | (c) | 5 |
| 12–22 | Amelia persona + unattended rules (no asking, no git, no status, stay in lane) | (b) | 11 |
| 25–36 | `mode = plan` (Stage 1) — BDD gate first, then plan-only | (b)+(a) | 12 |
| 38–64 | `mode = implement` (Stage 3) — red → green → expand → suite → walkthrough | (a)+(b) | 27 |
| 66–68 | Missing-handoff-artifact heads-up | (b) | 3 |
| 72–79 | PIPELINE_BLOCKER protocol | (b) | 8 |

**Category totals:** (a) ≈35 · (b) ≈30 · (c) ≈5 · (d) ≈3 · (e) ≈6.

## 8. `sudo-self-audit_AP.md` — 36 lines / 2,494 bytes (autopilot twin)

| Lines | Section | Class | ≈len |
|---|---|---|---|
| 1–4 | frontmatter | metadata | 4 |
| 6–10 | Headless launch context | (c) | 5 |
| 11–19 | Murat persona + adaptation rules; **points at `@.agents/workflows/sudo-self-audit.md`** | (c) | 9 |
| 21–26 | Stay in your lane | (b) | 6 |
| 28–31 | Output contract | (a)+(b) | 4 |
| 33–36 | PIPELINE_BLOCKER | (b) | 4 |

**Category totals:** (a) ≈12 · (b) ≈14 · (c) ≈6 · (d) ≈2 · (e) ≈2.
⚠ **Stale path:** `@.agents/workflows/sudo-self-audit.md` does not exist — `.agents/workflows/` contains only `INDEX.md, merge_main_debug.md, new-project.md, security_team_aviationchat.md, slash_command_updating.md`. The real file is `.agents/commands/sudo-self-audit.md`.

## 9. `sudo-write-story-tests.md` — 95 lines / 7,083 bytes (no `_AP` twin exists)

| Lines | Section | Class | ≈len |
|---|---|---|---|
| 1–4 | frontmatter | metadata | 4 |
| 6–12 | Title + flow position | (c) | 7 |
| 14–35 | Step 0 — target project + binding rule | **(e)** | 22 |
| 37–49 | Step 0.5 — Open the story worktree (+ ordering caveat) | (a)+(e) | 13 |
| 51–55 | Step 1 — Create the story (`bmad-create-story`) | (a)+(b) | 5 |
| 57–69 | Step 2 — **BDD Vision Lock** (`/sudo-bdd-tests`) | (b) | 13 |
| 71–84 | Step 3 — Write failing acceptance tests (ATDD red) + ground-every-red | (a)+(b) | 14 |
| 86–95 | Done + Git | (b) | 10 |

**Category totals:** (a) ≈30 · (b) ≈35 · (c) ≈7 · (d) ≈5 · (e) ≈28.

## 10. `sudo-create-epic-sprint.md` — 95 lines / 7,314 bytes

| Lines | Section | Class | ≈len |
|---|---|---|---|
| 1–4 | frontmatter | metadata | 4 |
| 6–13 | Title + flow position | (c) | 8 |
| 15–36 | Step 0 — target project + binding rule | **(e)** | 22 |
| 38–55 | Step 1 — Create epic + stories, incl. **FLOW CONTRACT** (2026-07-19 retro bake-in) | (a)+(b)+(d) | 18 |
| 57–66 | Step 2 — Generate the sprint board (`backlog`, house style) | (a)+(d) fix-history parenthetical | 10 |
| 68–87 | Step 3 — Risk-score P0–P3 — **INTERACTIVE HARD STOP** | (b)+(a) | 20 |
| 89–95 | Done | (b) | 7 |

**Category totals:** (a) ≈30 · (b) ≈28 · (c) ≈8 · (d) ≈12 · (e) ≈26.

## 11. `sudo-boot-sprint-memory.md` — 89 lines / 6,585 bytes

| Lines | Section | Class | ≈len |
|---|---|---|---|
| 1–4 | frontmatter | metadata | 4 |
| 6–10 | Title + "Discovery only — do NOT start coding" | (b) | 5 |
| 12–34 | Step 0 — target project (**variant: always ASKS, never silently reuses pointer**) | **(e)**+(b) | 23 |
| 36–44 | Step 1 — Read active context (`<context>` block) | (a) | 9 |
| 45–49 | Step 2 — Load in-scope component specs | (a) | 5 |
| 50–74 | Step 2b — Sprint status + next story + worktree/origin check + "NOT the master pick-up" note | (a)+(b)+(c) | 25 |
| 76–83 | Step 3 — Confirm guardrails (5 constitution restatements) | (b)/(c) | 8 |
| 84–89 | Step 4 — Ready (stop and wait) | (b) | 6 |

**Category totals:** (a) ≈30 · (b) ≈25 · (c) ≈12 · (d) ≈3 · (e) ≈25.

## 12. `sudo-push-e2e.md` — 112 lines / 6,339 bytes

| Lines | Section | Class | ≈len |
|---|---|---|---|
| 1–3 | frontmatter (no `platforms:` key) | metadata | 3 |
| 5–12 | Title + **branch model invariant** | (b)+(d) | 8 |
| 14–19 | `## 🛑 MANDATORY RULES (Before You Start)` (3 rules) | **(b)** | 6 |
| 21–32 | Step 0 — target project (compressed variant) | **(e)** | 12 |
| 34–45 | Step 1 — Pick the path (A/B/C table) | (a)+(c) | 12 |
| 47–62 | Step 2 — Run the gate (light + full) | (b)+(a) | 16 |
| 64–71 | Step 3 — Commit & push `main_debug` | (a) | 8 |
| 73–90 | Step 4 — Promote to main (B/C, 2 human gates) | (a)+(b) | 18 |
| 92–100 | Step 5 — Reconcile the branch model | (a)+(b) | 9 |
| 102–104 | Step 6 — Deploy backend (points at `deploy-backend` skill) | (a)+(c) | 3 |
| 106–112 | Step 7 — Verify live + ledger | (a) | 7 |

**Category totals:** (a) ≈45 · (b) ≈35 · (c) ≈8 · (d) ≈5 · (e) ≈14.

## 13. `sudo-e2e.md` — 62 lines / 3,744 bytes

| Lines | Section | Class | ≈len |
|---|---|---|---|
| 1–3 | frontmatter | metadata | 3 |
| 5–9 | Title + "green here is the promotion evidence" | (c) | 5 |
| 11–21 | Step 0 — target project (compressed) | **(e)** | 11 |
| 23–26 | Step 1 — Confirm the harness exists | (b) | 4 |
| 28–49 | Step 2 — Run the suite: 1 command + **"what the harness does for you" (6 bullets)** + known failure modes | (a)+(c) ≈8+(d) ≈7 | 22 |
| 51–62 | Step 3 — Report the verdict (GREEN/RED) | (b) | 12 |

**Category totals:** (a) ≈15 · (b) ≈20 · (c) ≈10 · (d) ≈8 · (e) ≈12.

## 14. `sudo-park.md` — 110 lines / 6,232 bytes

| Lines | Section | Class | ≈len |
|---|---|---|---|
| 1–3 | frontmatter | metadata | 3 |
| 5–18 | Title + "branches travel, worktrees do not" + **⛔ Hard boundary** | (d)+(b) | 14 |
| 20–29 | Step 0 — Resolve scope (BOTH repos) | (e)+(b) | 10 |
| 31–43 | Step 1 — Guard: worktrees must never be committable (gitlink 160000) | (b)+(a)+(d) `d098dc63` incident | 13 |
| 45–70 | Step 2 — Park every story worktree (commit/sync/push + 5 rules) | (a)+(b) | 26 |
| 72–83 | Step 3 — Park the two main checkouts | (a) | 12 |
| 85–97 | Step 4 — Write the resume card | (a) | 13 |
| 99–103 | Step 5 — Report | (b) | 5 |
| 105–110 | `**Never:**` list | (b) | 6 |

**Category totals:** (a) ≈40 · (b) ≈35 · (c) ≈3 · (d) ≈18 · (e) ≈12.

## 15. `sudo-resume.md` — 84 lines / 4,657 bytes

| Lines | Section | Class | ≈len |
|---|---|---|---|
| 1–3 | frontmatter | metadata | 3 |
| 5–16 | Title + why (`git worktree list` false negative) | (d) | 12 |
| 18–25 | Step 0 — Resolve scope (BOTH repos) | (e)+(b) | 8 |
| 27–39 | Step 1 — Fetch both repos (`--ff-only`) | (a)+(b) | 13 |
| 41–43 | Step 2 — Read the handoff card | (a) | 3 |
| 45–51 | Step 3 — Find the live stories via `git ls-remote` | (a)+(b) | 7 |
| 53–69 | Step 4 — Re-create the working surface (desktop vs mobile) | (a)+(b) | 17 |
| 71–77 | Step 5 — Hand off to the boot | (b) | 7 |
| 79–84 | `**Never:**` list | (b) | 6 |

**Category totals:** (a) ≈30 · (b) ≈25 · (c) ≈5 · (d) ≈14 · (e) ≈10.

## 16. `sudo-close-workingtree.md` — 69 lines / 3,405 bytes

| Lines | Section | Class | ≈len |
|---|---|---|---|
| 1–3 | frontmatter | metadata | 3 |
| 5–7 | Title + intro | (c) | 3 |
| 9–18 | Step 0 — Resolve project + story slug (3 slug sources) | (e)+(a) | 10 |
| 20–33 | Step 1 — **Safety Verification Gate (MANDATORY)** | (b) | 14 |
| 35–36 | Step 2 — Exit worktree directory | (a) | 2 |
| 38–52 | Step 3 — Prune worktree + purge physical dir | (a) | 15 |
| 54–62 | Step 4 — Delete local + remote branches | (a) | 9 |
| 64–69 | Step 5 — Report outcome | (a) | 6 |

**Category totals:** (a) ≈40 · (b) ≈15 · (c) ≈2 · (d) ≈1 · (e) ≈11.

## 17. `sudo-quick-dev.md` — 70 lines / 5,062 bytes

| Lines | Section | Class | ≈len |
|---|---|---|---|
| 1–4 | frontmatter (only file with `platforms: [opencode, antigravity, claude, codex]`) | metadata | 4 |
| 6–14 | Title + "four cheap guards" + flow position | (d)+(c) | 9 |
| 16–26 | Step 0 — target project (**most compressed variant, 1 line per case**) | **(e)** | 11 |
| 28–31 | Step 0.5 — Worktree | (a)+(e) | 4 |
| 33–34 | Step 1 — Create the story | (a) | 2 |
| 36–48 | Step 2 — Direct implementation + **⛔ EJECT TRIPWIRE** | (a)+(b) | 13 |
| 50–57 | Step 2b — Scoped verification | (a)+(b) | 8 |
| 59–64 | Step 3 — Clean-code audit + AC-trace | (a)+(b) | 6 |
| 66–70 | Done | (b) | 5 |

**Category totals:** (a) ≈22 · (b) ≈25 · (c) ≈6 · (d) ≈7 · (e) ≈13.

---

# PART 2 — CONSOLIDATED SAFETY INVENTORY (exhaustive, per file)

### `sudo-update-sprint-memory.md` (26 obligations)
1. Step 0 case 3 — "STOP and ask Daniel *'Which project are we closing out?'* — never guess, never operate on the lobby."
2. Step 0 — "**echo exactly** `Target: Projects/<name>` before any work."
3. Step 0 binding rule — "A needed project path missing under `PROJECT_ROOT` → STOP and say so."
4. Step 1.5 — if walkthrough ends with `## Close-Out Handoff`, that block is AUTHORITATIVE; Step 3 lifts it, no re-deriving.
5. Step 2 — code-verify grep-check marking `✅ Code-Verified` / `❌ Not Found` / `⚠️ Partial`.
6. Step 2 — "Human-gated carryovers (pending live-QA / deploy) can't be grep-advanced — leave as-is."
7. Step 4 — "**Story-status → `done` (this command's PRIMARY purpose).** Daniel invoking this **IS his sign-off** — flip the just-closed story to `done` by default, without asking" in BOTH the story file and `sprint-status.yaml`.
8. Step 4 — "Print `Closing <story>: review → done`."
9. Step 4 — "Idempotent: only `ready-for-dev`/`in-progress`/`review` advance; never downgrade."
10. Step 4 — "**ONLY objectively-red tests block the flip.** Read the verdict at `sudo-code-review-<story>.md`. **FAIL** … → do NOT flip … **PASS** → flip; **CONCERNS** → flip + record them; **WAIVED / missing / stale** → flip. Fail-open: a gate-read error never blocks close-out."
11. Step 4 — "**No 'leave it at review and ask' branch — never punt the flip back to Daniel.**" Pending live-test/live-verify/live-QA/live-checkride is NOT a blocker: flip and NOTE it.
12. Step 4 — "'commit owed' is NOT a blocker … Nothing about git blocks the status flip."
13. Step 4 — `Last Updated` set to today's date at the top of `active-context.md`.
14. Step 5 — "Unconditional *apply* … **without asking** … The ONLY gate in this command is Step 4's red-tests check; everything else, incl. Step 6's memory write, just applies."
15. Step 5 — "**`active-context.md` has a hard CONTEXT budget: ≤ 20 KB ≈ 5,000 tokens** … Measure: file size in bytes ÷ 4; report `active-context: ~X / 5,000 tokens` in Step 6's summary **EVERY close-out**."
16. Step 5 — over budget → prune in the same pass, **one-in-one-out**.
17. Step 5 — "Read the entry ONCE before cutting: a buried **STILL-OWED** obligation must survive as a pointer line (the 2026-07-13 OIDC-env loss is the cautionary case)."
18. Step 5 — "a standing ruling must live in memory/specs before its text dies here."
19. Step 5 — `_archive/` is cold storage, "never a mandatory copy step."
20. Step 5 — Completed tasks > 5 → compact oldest to pointer form, move to `_archive/`.
21. Step 5 — pitfall staleness: ALWAYS re-check entries touched this session; prune-on-touch; four-rule sweep only when over the 60 KB budget.
22. Step 5 — size caps: component spec > 120 lines → keep 8 most-recent failure modes; `project-context.md` target 150 / hard cap 200.
23. Step 6 — §5 artifact obligation: `walkthrough.md` must end with `## Task Checklist` AND `## Your Actions` (per AGENTS.md §5).
24. Step 6 — memory write is **AUTOMATIC, no approval gate**, but must pass 3 self-checks (valid to store? cross-check existing MEMORY.md? then write one fact per file + pointer).
25. Step 6 — "**Then ask Daniel (always, separate from memory):** *'Saved the session updates. Any manual learnings, new bugs, or sprint-objective changes to add?'*"
26. Step 7 — "**Daniel invoking this command IS the sign-off for this push.**"
27. Step 7 precondition — HEAD must be a `claude/*` branch; if `main_debug`/`main` → "**do NOT land it.** Report it and stop — never rescue it by committing in the shared checkout."
28. Step 7 — "EXPLICIT PATHS ONLY, never `git add -A`"; `git diff --cached --stat` "must show ONLY this story's files."
29. Step 7 — sync-first merge `origin/main_debug` inside the worktree; "CONFLICT → STOP and report; never force-push, never blind-rebase."
30. Step 7 — "**`main` is untouched.** Only Daniel, directly or via `/sudo-push-e2e`."
31. Step 7 — "Landing push rejected (remote moved) → **STOP and report.** Re-run from step 2."
32. Step 8 — after landing, invoke `/sudo-close-workingtree`; "Confirm both local disk and remote origin are clean."

### `sudo-dev-story-tests.md` (24)
1. Step 0 case 3 STOP-and-ask; never guess, never operate on the lobby.
2. Step 0 — echo exactly `Target: Projects/<name>` before any work.
3. Step 0 binding rule — missing path under `PROJECT_ROOT` → "STOP and say so; never fall back to the lobby."
4. Step 0.5 — **echo `Artifacts: <ARTIFACT_DIR>` before Step 1**; "never let one [sub-skill] mint its own root-level or date-stamped folder."
5. Step 0.6 — run `git worktree list` before any planning or edit; re-enter existing `claude/<slug>` tree; echo the case.
6. Step 0.7 — **BDD contract gate (HARD)**: `bdd: locked` AND every `bdd_contract:` path exists on disk.
7. Step 0.7 — "A `locked` record whose cited files are missing **fails the gate** … never wave it through (Epic 17.7 shipped a `locked` record backed by zero files)."
8. Step 0.7 — neither locked nor waived → "**STOP. Do not plan or code.** Run **`/sudo-bdd-tests`** now … Never grandfather silently, never author the 'lock' yourself."
9. Step 2 — "**Self-audit STOP gate (MANDATORY — stop the moment the plan is written)** … STOP before the audit and before any code."
10. Step 2 — "**You can NEVER switch the model yourself — never offer to.** Only the human can (e.g. `/model`)."
11. Step 2 — gate message must carry the **clickable plan link (never a bare path)**.
12. Step 2 — "Then **WAIT — modify NO project file, write NO code.**"
13. Step 2 `continue` — run `/sudo-self-audit`, **persist as `self-audit-stress-test.md` (`type: self_audit`) in ARTIFACT_DIR** — "inline-only findings do NOT satisfy the protocol (`artifacts-always-first` §7)."
14. Step 2 `changed` — audit on the switched model, then "**STOP AGAIN**: *'Audit done — switch back, then say `continue`.'* … **never implement on the audit-switched model.**"
15. Step 2 pasted path — copy into ARTIFACT_DIR with source noted in frontmatter.
16. Step 2 "skip the audit" — confirm once; write a stub recording `Skipped by human decision (<date>)` "so the Step 5 checklist stays honest."
17. Step 2.5 — conditional gate: "**Have questions → STOP before any code** … Modify NO project file until resolved. This gate OVERRIDES bmad-dev-story's no-pause directive." No questions → don't manufacture one.
18. Step 3 — run the suites and **paste the actual output (constitution rule)**; root cause before fixing.
19. Step 3 — "**Every ① red ends green or is quarantined — never shipped red (`tests-must-gate-for-real`).**" Fiction-red → fix to the real contract or drop with a note; "**never delete-to-force-green.**"
20. Step 4 — Automate evidence: `automation-summary-<story>.md` OR `## Automate: skipped — <rationale>`; "A silent skip is an unfinished Step 4 — the Step 5 checklist and the ③ gate verify this."
21. Step 5 — **MANDATORY artifact checklist (never skip, even on "just do it")**: plan + standalone self-audit + walkthrough (with **actual pasted test output**, AC→evidence matrix, `## Task Checklist`, `## Your Actions`) + automate evidence.
22. Step 5 — "**Required even when told to 'skip the plan, just do it' — the walkthrough is never skippable.**"
23. Step 5 — "Post a clickable Markdown link to every artifact in the chat that same turn — never a bare path."
24. Done — "The dev step **may advance the story to `review`** … **Never flip to `done`** — Daniel's call at close-out via `/sudo-update-sprint-memory`."
25. Done — commit inside the worktree (explicit paths, never `git add -A`); "do NOT land it on `main_debug`."

### `sudo-code-review.md` (28)
1. Step 0 case 3 STOP-and-ask; never guess/lobby. 2. echo `Target:`. 3. Missing path → STOP, never fall back to the lobby.
4. Step 0.5 — re-enter the story worktree; echo `Worktree: reviewing in <path>` — otherwise "reviewing from the shared checkout would audit an empty or stale diff."
5. Step 1 — "You MUST act as a **Clean-Room** agent: zero out any builder's bias" — hunt AI Drift, over-engineering, bloat, unnecessary abstractions; if you change code, re-run suites and paste actual output.
6. Step 2 — `sudo-tests.yaml` absent → verdict **`WAIVED`** (do NOT block).
7. Step 3.1 — run the FULL suite of every stack the diff touched (backend pytest via `backend/.venv`; frontend vitest); other stack only on a shared cross-boundary surface.
8. Step 3.1 — baseline-diff: "only failures NEW to this story count (legacy red is grandfathered)."
9. Step 3.1 guard (a) — CI-entrypoint audit (change-triggered): confirm each CI test job invokes the real harness command; "**a green CI check on a suite that never ran is a FAIL, not a pass**"; write `ci_audit: {sha, date}` back; when skipped, state `CI audit current as of <sha>`.
10. Step 3.1 guard (b) — "a red that asserts strings, selectors, or preconditions absent from real source is **fiction, not legacy debt**; do not grandfather it, FAIL and fix/delete it."
11. Step 3.2 — `bmad-testarch-trace` traceability + coverage vs `l1_coverage_min`.
12. Step 3.3 — `bmad-testarch-nfr` when `nfr: true` or `agent_bearing: true`.
13. Step 3.4 — `bmad-testarch-test-review` + CI soft-gate scan (`continue-on-error`, `|| true`, blanket `.skip`/`xfail`, "report-only"); a soft gate is legitimate only as a one-run window with a **named owner + tracked expiry task** — else **CONCERNS floor**, named in the verdict.
14. Step 3.5(item 5) — Automate evidence (feature stories only; `tea-*` exempt): missing both → **cap at CONCERNS**, never FAIL alone (pre-2026-07-09 grandfather).
15. Step 3.5 — "**Gate: clean code (ALWAYS runs — independent of Step 2's opt-in)**"; checks the diff against `.agents/rules/code-standards.md`.
16. Step 3.5 — "**This gate does NOT depend on `sudo-tests.yaml`** … a `WAIVED` test gate never waives this one."
17. Step 3.5 — no double drift-hunt: import Step 1's findings (source `review`) instead of re-running §2B.
18. Step 3.5 — diff-scoped; legacy debt noted, never gated on.
19. Step 3.5 — "**A missing tool is a finding, not a skip** — `No module named ruff` means the floor is unrunnable and the project breaks `tests-must-gate-for-real` §2."
20. Step 3.5 — "**An empty diff is a STOP, not a pass** … a vacuously green gate is exactly what this step exists to prevent."
21. Step 3.5 — fold the findings table into the verdict **verbatim** with actual command output; apply safe fixes, re-run, paste new output.
22. Step 4 — write `_bmad-output/implementation-artifacts/sudo-code-review-<story>.md` carrying the verdict, the story id, and the **current `git HEAD` ref (so `sudo-update-sprint-memory` can detect a stale verdict)**.
23. Step 4 — **FAIL** = new test regression, required tier missing, **or** a Step 3.5 machine-floor error on a changed line / banned pattern shipped (bare `except:`, `any`, a committed secret).
24. Step 4 — **CONCERNS** = soft issues only; **PASS** = all required tiers green AND clean-code floor green on changed lines; **WAIVED** = no baseline (3.5 still ran).
25. Step 4 — "objective checks block a story, taste does not."
26. Step 5 — **REQUIRED** walkthrough update whenever anything was found or fixed: append `## Code Review (<date>)`, refresh stale AC/test matrix, pasted suite totals, `## Task Checklist`.
27. Step 5 — commit fixes in the worktree (explicit paths); keep the `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` trailer.
28. Step 5 — "**Hard rule: NEVER finish `/sudo-code-review` with the walkthrough body left stale after applying fixes.**"
29. Stay in lane — "never land on `main_debug`, and never flip the story status or edit `sprint-status.yaml`."

### `sudo-write-story-tests.md` (13)
1. Step 0 case 3 STOP-and-ask; never guess/lobby. 2. echo `Target:`. 3. Missing path → STOP, never fall back to the lobby.
4. Step 0.5 — open the worktree **BEFORE the first project file is written**; re-enter an existing tree; "never open a second for the same slug."
5. Step 0.5 — "confirm HEAD is `main_debug` (**never** `main`)" before opening the tree.
6. Step 0.5 ordering caveat — resolve the story id first, then open the tree; "never write into the shared checkout planning to move it afterwards"; echo `Worktree: <path> (<branch>)`.
7. Step 1 — "Confirm the story file + ACs exist before continuing. If create-story stops for input, surface it and stop — never guess."
8. Step 2 — "**BDD Vision Lock (ATDD Contract Phase — MANDATORY, never silently skipped)**" — interactive session with Murat until behaviors are 100% understood.
9. Step 2 — "the **ONLY exit without a contract is a recorded waiver**" — human confirms in chat; frontmatter records `bdd: waived — <rationale>`.
10. Step 2 — story leaves ① carrying `bdd: locked` (+ contract paths) or `bdd: waived`; "② **hard-gates on that record** and will refuse to dev a story without it."
11. Step 3 — "**Ground every red before it counts (per `tests-must-gate-for-real`)**" — verify every asserted string, selector, endpoint, and **precondition** (incl. the auth model) against the ACTUAL code; "A test asserting copy that does not exist in source … is **fiction, not a red** … Fix or drop it here; do not hand fiction to ②."
12. Done — report the reds and **confirmation they fail as expected**; "**Do NOT start implementing.**"
13. Git — commit inside the worktree with explicit paths; "`git add -A` / `.` / `-u` are **banned**"; do NOT push to `main_debug`.

### `sudo-create-epic-sprint.md` (10)
1. Step 0 case 3 STOP-and-ask; never guess/lobby. 2. echo `Target:`; missing path → STOP.
3. Step 1 — "Confirm the epic + story files exist before continuing. If the skill stops for input … surface it and STOP — never guess."
4. Step 1 FLOW CONTRACT — "This command has exactly **TWO human checkpoints**: 1. ONE consolidated review after Step 1 (epic definition + full story list + AC digest in a single message) … 2. the Step 3 per-story risk-scoring (the designed hard stop)."
5. Step 1 — do NOT surface nested `[C]`-continue menus one-by-one; auto-continue when the requirements source is already approved.
6. Step 1 — "A nested skill stopping on a REAL gap (missing source, contradictory scope) still surfaces + STOPs — this contract removes ceremony, never judgment."
7. Step 2 — stories land as **`backlog`, NOT `ready-for-dev`** (state-machine correction, 2026-07-19); "Confirm the keys appear before Step 3."
8. Step 3 — "**INTERACTIVE HARD STOP** — you WORK WITH Daniel to label every story, **ONE STORY AT A TIME**" (recommendation + why + what it is + levels earned).
9. Step 3.3 — Daniel confirms or overrides each label individually; "**never record a P-level that wasn't explicitly confirmed. STOP and wait** for the decisions. This is the hard stop."
10. Step 3.4 — record confirmed P-levels + test-level allocation into the test-design artifact and reflect onto each story.
11. Done — "Leave it there — **do NOT start writing tests or code**."

### `sudo-boot-sprint-memory.md` (9)
1. Header — "**Discovery only** — after completion, **do NOT start coding; wait for Daniel's next instruction.**"
2. Step 0 case 2 — "do NOT silently reuse the pointer … ASK Daniel: *'Active project is `<pointer, or none>`. Which project this session?'* … Never guess, never operate on the lobby."
3. Step 0 — echo exactly `Target: Projects/<name>`; missing path → STOP and say so.
4. Step 2b — "Read-only — cross-check against live files; **never edit anything.**"
5. Step 2b — run `git worktree list`; if a tree exists, report it and note resumed work must `cd` in first.
6. Step 2b — "**⚠️ No worktree is NOT proof of a fresh start — check the remote before you say so**" → `git ls-remote --heads origin 'refs/heads/claude/*'`; a branch on origin → report "exists on origin, not on this machine" and point at `/sudo-resume`; "Only when BOTH are empty may you say the next step opens a worktree at first edit."
7. Step 2b — "**⛔ This is NOT the master 'pick up.'**" (does not replace `AGENTS.md` §7 / `router.md`).
8. Step 3 — guardrails confirmed active: component-spec compliance · targeted edits only (no full-file rewrites) · agent authority boundaries · shared-resource singleton via the project's factory (per constitution) · research-first.
9. Step 4 — "Then stop and wait."

### `sudo-quick-dev.md` (12)
1. Step 0 case 3 — STOP and ask; never guess. 2. echo `Target:`; binding rule.
3. Step 0.5 — worktree before the first edit; "**Quick fixes are NOT exempt**."
4. Step 2 — **explicit gate REMOVAL**: "Bypass Planning Gate — the developer agent is explicitly permitted to bypass 'wait for approval' planning gates."
5. Step 2 — **explicit gate REMOVAL**: "Skip ATDD — skip the strict red-phase acceptance-test-first cycle."
6. Step 2 — "Root cause first: for a bug fix, find the root cause before touching code — no symptom patches."
7. Step 2 — "**⛔ EJECT TRIPWIRE (the safety core — check as you go, not just at the end)**: if the emerging change exceeds **~3 files / ~150 changed lines**, or touches a **protected surface** — auth/tenancy walls, payments, PII handling, DB schema or security rules, a cross-boundary API/SSE contract — **STOP. This is not a quick fix.**" Hand off to `/sudo-write-story-tests` ①; keep the worktree and story file, discard nothing.
8. Step 2b — scoped verification with the **actual** output pasted; whole endpoint/module suite when a shared handler changed.
9. Step 2b — "**Bug fixes add ONE pinning regression test**"; config/copy tweaks need none — "say so explicitly."
10. Step 2b — full suite deliberately NOT run here; "anything shipping to `main` still passes PR CI + `/sudo-e2e`."
11. Step 3 — `/clean-code-audit` **full two-half pass** (since no adversarial review runs in this lane) + one-line **AC-trace confirmation**; "anything in the diff beyond the ACs is drift — cut it or name why it stays."
12. Done — "**Stop here. Do NOT run `/sudo-update-sprint-memory`.**" Commit inside worktree, explicit paths, never `git add -A`; never land on `main_debug`; invite Daniel to review and run close-out himself (**the human review at the end is the gate**).

### `sudo-push-e2e.md` (15)
1. Branch model (never violate) — "`main` is only ever *fast-forwarded or merged up from* `main_debug` — `main` must NEVER end up ahead."
2. MANDATORY RULE 1 — "**Never commit/push autonomously**: write the exact git commands for the human to approve/run, OR propose them via execution tools so the human approves each one individually."
3. MANDATORY RULE 2 — "**Clear GITHUB_TOKEN on push/pull**" (`$env:GITHUB_TOKEN = ""` / `env -u GITHUB_TOKEN`).
4. MANDATORY RULE 3 — "**The gate is not optional**: a red gate STOPS the command. Report what failed; do not 'push anyway'."
5. Step 0 case 3 — STOP and ask; echo exactly `Target: Projects/<name>`.
6. Step 2 light gate — backend full pytest **via the canonical venv (`backend/.venv` — never the global interpreter)**.
7. Step 2 light gate — frontend production build with **zero compile errors**.
8. Step 2 light gate — CI/CD credentials: `gh secret list` → `FIREBASE_SERVICE_ACCOUNT`; `gh variable list` → `FIREBASE_PROJECT_ID`; "If any required deployment credentials are missing, STOP and warn the user."
9. Step 2 full gate (B/C) — "Run **`/sudo-e2e`** … It must finish **green**. Its report is the promotion evidence; link it in the ledger row."
10. Step 2 — "Any failure → **STOP**. Summarize the failures, file/link the evidence, and suggest the lane … Do not proceed."
11. Step 3 — `git add <explicit-file-paths>` — "never blanket-add; verify staged imports have staged modules."
12. Step 4 Path B — "`# 🛑 HUMAN GATE: summarize the commits + changed files first`" before `git push origin main`.
13. Step 4 Path C — "`# 🛑 HUMAN GATE: summarize the cherry-picked commits first`" before `git push origin main`.
14. Step 5 — reconcile after cherry-pick (`git merge main` into `main_debug`); Path B verify `git log --oneline main_debug..main` is empty; "Always finish back on `main_debug`."
15. Step 7 — live check backend `/health` + production frontend URL; ledger row in `_artifacts/INDEX.md` with the gate evidence link; record the deployment in `active-context.md`.

### `sudo-e2e.md` (8)
1. Step 0 case 3 — STOP and ask; echo exactly `Target: Projects/<name>`.
2. Step 1 — harness check `PROJECT_ROOT/frontend/e2e/run-e2e.mjs`; missing → "STOP: this project has no E2E harness yet … **Never improvise a substitute suite and call it the gate.**"
3. Step 2 — run as a background process; "What the harness does for you (**do NOT hand-roll any of it**)."
4. Step 2 — "**Never** run the suite via the default `playwright.config.ts` — the journeys config (`playwright.journeys.config.ts`) is the real gate; the default config … is NOT this gate."
5. Step 2 — known failure modes are env problems: "fix these, don't blame the tests."
6. Step 3 — post exactly one of **`E2E GATE: GREEN`** / **`E2E GATE: RED`**.
7. Step 3 — "**A harness/env failure is still RED** — fix the env and re-run; never wave it through."
8. Step 3 — when called from `/sudo-push-e2e`, "the promotion continues only on GREEN."

### `sudo-park.md` (14)
1. "**⛔ Hard boundary:** never push a story branch onto `main_debug`. Landing a story is `/sudo-update-sprint-memory` Step 7, and only after ③ turns it green. A story at ① / ② carries **deliberately RED tests** — landing those … poisons every other story's regression baseline and reds the `/sudo-e2e` gate."
2. Step 0 — BOTH repos must be parked; missing pointer → "ASK which project — never guess"; "Echo exactly `Parking: lobby + Projects/<name>` before any git command."
3. Step 1 (BEFORE any `git add`) — `git check-ignore -q .claude/worktrees/` must pass; not ignored → add to `.gitignore`.
4. Step 1 — `git ls-files -s .claude/worktrees/` "must be EMPTY; any 160000 line is the bug" → `git rm --cached <each path>`, commit with the ignore rule, "and say so in the report."
5. Step 2 — "**Count them and say the number out loud** — parallel sessions open trees you did not, so never assume you know the set."
6. Step 2 — "commit — EXPLICIT PATHS ONLY, never `git add -A`"; `git diff --cached --stat` "must show ONLY this story's files."
7. Step 2 — sync-first merge `origin/main_debug` inside the worktree; "CONFLICT → resolve HERE, on the machine that has the context."
8. Step 2 — "push the branch — this is the ONLY thing that makes the work portable."
9. Step 2 — loose files that are NOT this story's → do NOT sweep in; list as "*left dirty, deliberately*."
10. Step 2 — "**Nothing to commit** is still worth a `git push`."
11. Step 2 — "**Never delete a worktree on park.** It is the rollback point."
12. Step 3 — report untracked artifact folders explicitly; `git add <explicit paths>` — "NEVER -A."
13. Step 4 — ONE live resume card stanza (overwrite the previous — "one live card, never a log"), committed + pushed on `main_debug`.
14. Step 5 — "**If ANY push failed, say so loudly** … never soften it."
15. Footer — "**Never:** `git add -A` · force-push · rebase a pushed story branch · push a story branch to `main_debug` · delete a worktree."

### `sudo-resume.md` (7)
1. Step 0 — BOTH repos; missing pointer → "ASK which project — never guess"; "Echo exactly `Resuming: lobby + Projects/<name>` before any git command."
2. Step 1 — `git pull --ff-only origin main_debug`; "diverged → STOP and report; do not merge blind." "A `--ff-only` failure means this machine has local commits that never got parked. **Stop and report it** — do not merge or rebase your way out."
3. Step 3 — "**do NOT trust `git worktree list` here**" — use `git ls-remote --heads origin 'refs/heads/claude/*'`; cross-check each against `sprint-status.yaml`; "report the whole set … **before touching anything**."
4. Step 4 — "Ask Daniel which story he is picking up."
5. Step 4 — ghost directory → `git worktree prune`, remove the empty dir, then add. "**Never** `git worktree add --force` over real content."
6. Step 5 — hand off, "Then stop. This command restores the **git surface** … do not do the boot's work here."
7. Footer — "**Never:** force-push · rebase a pushed story branch · `git worktree add --force` · delete a worktree on the other machine's behalf · start coding (this is setup only)."

### `sudo-close-workingtree.md` (7)
1. Step 0 — "Echo `Target: Projects/<name> | Story: <story-slug>` before proceeding."
2. Step 1 — "**Safety Verification Gate (MANDATORY)**": `git fetch origin`, then `git merge-base --is-ancestor claude/<story-slug> origin/main_debug`.
3. Step 1 — exit 0 → proceed; **non-zero → "STOP IMMEDIATELY!"** print `❌ Refusing to delete: claude/<story-slug> is NOT fully merged into origin/main_debug.`
4. Step 1 — instruct: "Land the story first using /sudo-update-sprint-memory or git merge to origin/main_debug."
5. Step 2 — exit the worktree dir before removal so it unlocks.
6. Step 4 — `git branch -d` (safe delete, not `-D`); GITHUB_TOKEN cleared before `git fetch` and before the remote delete push.
7. Step 5 — report the three ✅ confirmations (local worktree removed, local branch deleted, remote branch deleted).

### `sudo-self-audit.md` (17)
1. Step 0 case 3 STOP-and-ask; never guess/lobby. 2. echo exactly `Target:`. 3. Binding rule — plan, codebase, and every bare path under `PROJECT_ROOT`, never the lobby.
4. Framing gate — "a **pre-dev gate**, run BEFORE any code"; "This is a **pre-dev gate** — it audits the plan/story, never a code diff."
5. Phase 0.2 **right-size gate** — Skip / Light (Phases 1–3) / Full (all phases); "a Light plan does not get the Full pass."
6. Phase 0.3 AC↔Plan traceability — "AC with no step → the plan will silently under-deliver. **Flag.** Step with no AC → scope creep. **Flag for cut**."
7. Phase 0.4 **Decomposition flag** — story modifies both backend AND frontend → recommend splitting (per constitution Ask-First).
8. Phase 1 — **Contract two-sidedness**: a one-sided contract change "is a guaranteed break."
9. Phase 1 — **Reinvention check** (does the helper already exist?).
10. Phase 1 — **Constitution + assumptions scan**: full-file rewrite vs surgical edit · new DB client instead of the shared singleton (`get_db()`) · hardcoded secret · one-sided contract change · untested assumption about external state.
11. Phase 1 — "**Read the confidence column** — code edges ≈ 1.0; doc/story-file mentions ≈ 0.8" + GitNexus caveat (won't surface shared-DB coupling → still needs manual reasoning).
12. Phase 2 — "**AI Drift & Over-Engineering Gate (STRICT — default NO-GO)**"; complexity guilty until proven innocent; every abstraction must trace to a **current AC**.
13. Phase 2 — "If the plan dictates building five layers of abstraction for a simple `if` statement, **hard-stop the dev flow.**"
14. Phase 2 — 9 tripwires; "if any fires, the plan is `NEEDS-REVISION` until that step is justified against a current AC or cut"; "**Default disposition for an unjustified tripwire is CUT IT.**"
15. Phase 4.1 — per-item verdict **SAFE / NEEDS REVISION / UNSAFE**.
16. Phase 4.2 — four quick gates: verification strategy present? · "**Anything irreversible / destructive?** Migrations, DB schema/rules, data deletes → flag + gate" · any step vague enough the dev will guess? · quality fit (anchored to existing conventions)?
17. Phase 4.3 — **Final Go / No-Go** for proceeding to dev.
18. Phase 4 — NEEDS-REVISION/UNSAFE → "**bake the fix into the plan/story itself** (inline `⚠️ AUDIT FINDING` …) — then re-run only the phases the change touched."

### `sudo-dev-story-tests_AP.md` (13)
1. "**Resolve ambiguity yourself** … never ask Daniel. Log any judgment call … to `decisions-log.md`."
2. "**Never** `git commit`/`push`, and **never** touch story status or `sprint-status.yaml` — the **orchestrator** owns the `review` flip (gated on its own independent green test result), and the human owns `review → done`."
3. "**Stay in your lane.** Write only the ONE artifact your mode owns … If your output artifact already exists in the folder, leave it and stop."
4. plan mode — "**BDD contract gate (HARD — check FIRST, before planning)**"; neither locked-with-files nor waived → "this is a **human-only gap** … a headless lane must NEVER author the 'lock' itself. End immediately with `PIPELINE_BLOCKER: BDD contract missing — run /sudo-bdd-tests for <story>`."
5. plan mode — "Do **not** write source, tests, or any other file. This is plan-only."
6. implement mode — "Apply **all** of the audit's proposed fixes first … Do **not** re-plan."
7. implement 1 — "**Red — author the failing acceptance tests first.** Before writing any production code" (extend the BDD contract files, don't duplicate).
8. implement 2 — "Touch only the files the plan lists … **Leave parallel teammates' unrelated working-tree changes alone.**"
9. implement 3 — Automate evidence: `automation-summary-<story>.md` or `## Automate: skipped — <rationale>`; "The QA gate checks for this evidence — a silent skip surfaces as CONCERNS."
10. implement 4 — "**Run the suite(s) until green and paste the *actual* output** … (constitution rule: real output, never a paraphrase). If a test fails, find the **root cause** before fixing."
11. implement 5 — `walkthrough.md` with "Your Actions" (worktree branch + commits); new dependency → self-install, pin, `decisions-log.md` entry, "NEW DEPENDENCIES" banner.
12. "if `implementation_plan.md` or `self-audit-stress-test.md` is absent … Don't silently re-plan or re-audit — note it, proceed … with safe defaults logged … or raise a `PIPELINE_BLOCKER`."
13. `PIPELINE_BLOCKER: <reason>` only for what no teammate can resolve; "A soft 'I'd normally confirm X with Daniel' is **not** a blocker."

### `sudo-code-review_AP.md` (18)
1. Solo adaptation per `.agents/rules/bmad_code_review_sudo_fix.md` — "run it yourself, sequentially, no subagents, no halting for confirmation."
2. "**Verify** the Dev stage addressed every finding from your audit."
3. Three review passes: blind diff → edge cases (full repo read) → acceptance vs the ACs.
4. Scope guard — "the PowerShell orchestrator already runs its own deterministic pytest/vitest suite gate AFTER this stage, so do NOT duplicate the full suite run here … **never block on a full-suite run**."
5. "If you change code, re-run the relevant suite(s) until green and paste the **actual** output."
6. Opt-in — `sudo-tests.yaml` absent → **`WAIVED`** (do NOT block).
7. `bmad-testarch-trace` coverage vs `l1_coverage_min`; 8. `bmad-testarch-nfr` when `nfr`/`agent_bearing`.
9. `tests-must-gate-for-real` (b) **always, per story** — "a red asserting strings/selectors/preconditions absent from real source is **fiction, not grandfathered legacy red** — FAIL it."
10. (a)+(c) **change-triggered**: CI test jobs must invoke the real harness entrypoint; flag soft CI steps lacking named owner + tracked expiry (**CONCERNS floor**); write `ci_audit: {sha, date}` back; when skipped state `CI audit current as of <sha>`.
11. Automate evidence — missing both → **cap at CONCERNS**, never FAIL alone.
12. Verdict PASS/CONCERNS/FAIL/WAIVED recorded **with the story id and the current `git HEAD` ref** (stale-verdict detection) inside `code-review.md`.
13. "Commit review fixes inside the story worktree (explicit paths, never `git add -A`); **never land on `main_debug`**, never set the story to `done` or edit `sprint-status.yaml` — human close-out owns both."
14. `code-review.md` **REQUIRED even if the review is clean**, incl. explicit "Changes applied: none — implementation is correct as-is."
15. Update `walkthrough.md` "Your Actions"; keep the `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` trailer.
16. TOP of walkthrough: `## OUT-OF-SPEC DECISIONS` (incl. reversible-at-close-out y/n) and `## OPEN QUESTIONS FOR DANIEL` ("Write 'none' if empty").
17. BOTTOM of walkthrough: `## Close-Out Handoff` — four sub-sections, "each a bullet list OR the literal word `none` (never leave one blank)."
18. Memory bucket — "These are PROPOSALS — Daniel approves the write at close-out; **you NEVER write memory yourself**." ⚠ **Contradicts** `sudo-update-sprint-memory` Step 6, which writes memory automatically with **no approval gate**.
19. `PIPELINE_BLOCKER: <reason>` protocol.

### `sudo-self-audit_AP.md` (8)
1. "Honor the workflow's Phase 0 right-size gate and the Phase 2 over-engineering gate."
2. "**For every finding, include a concrete proposed fix** the Dev stage can apply directly."
3. "**Resolve the plan's open questions yourself** (story-default them) and record each in `decisions-log.md`."
4. "Write **only** `self-audit-stress-test.md` … Do **NOT** modify source or tests, and do **NOT** implement the story or write `walkthrough.md` … If `self-audit-stress-test.md` already exists in the folder, leave it and stop."
5. "never land on `main_debug`, never set the story to `done`."
6. Output must contain: scope, right-size verdict, every finding with `file:line` + severity + a concrete fix, and a **Go / No-Go**.
7. "Findings WITH fixes are normal and expected … they do **not** stop the run."
8. `PIPELINE_BLOCKER` only for a flaw no autonomous teammate can resolve.

### `sudo-adviser-board.md` (30 — chair/integrity gates, not test gates)
1. Chair 1 — "**Never push the pace** … Phases advance **only on the operator's word** … If genuinely unsure what the operator wants next, ask — never advance."
2. Chair 2 — "Default to depth … never a reason to wrap."
3. Chair 3 — "**Ask for context instead of guessing** … A grounded question beats a confident invention, always."
4. Chair 4 — "**No process talk.** Never mention, recommend, or offer other slash commands or workflows during the session."
5. `--solo` — "**Announce solo mode on activation** so the operator knows responses come from one LLM."
6. Standing — "**You are the orchestrator, never a voice** … never generate team responses yourself. In `--solo` mode you roleplay the caucuses and say so."
7. Standing rendering — "**Never paraphrase, trim, merge, or reorder** either block; never re-cut a presentation or card yourself (caps are enforced at the source via respawn, not by editing)."
8. Standing — "**Withhold every CAUCUS LOG unless asked.**"
9. Standing footer — exactly one `⚖` tension line + ASK lines + ledger tally + quiet-minds tally; "Nothing else: no menus, no 'next?', no phase suggestions."
10. Caucus honesty — "'Unpack {team}' reveals the stored log **verbatim, never summarized, never ventriloquized** … **never generate retroactive dialogue and present it as what happened**"; a respawn must be labeled a reconvene.
11. Caucus honesty — "The card's caucus line must be true of the log — name only clashes and concessions that actually appear in it."
12. Presentation — "**Coverage contract:** everything the card claims outside LEDGER extras must have been actually explained in the presentation — the minutes never record a decision the chair didn't hear presented."
13. Card — "**The DISSENT slot is never silently absent** … The orchestrator polices the earned-none escape hatch."
14. Card — "**Champion, not composite.** … 'The team feels…' is manufactured consensus and a failed card."
15. Card — "**Attribution carries the move.** If a credited line could be reassigned to another member unchanged, rewrite it from that member's method or cut it."
16. Card — "a card whose speaker claims credit for points other minds minted" is a failed card.
17. Caucus — "**Diverge before you converge** … at least two genuinely different candidate ideas … If the caucus converges in under three exchanges, the member whose mental move sits furthest from the emerging consensus MUST attack it once" (PASS exemption).
18. Caucus — "**Rotate the credit** — the member credited as origin on your team's previous card must not mint again this round unless their move genuinely demands it."
19. Caucus — "**Kills are performed in the killer's method** … If the kill can't be stated in their method, it didn't happen at this table."
20. Failure playbook — contract violation → **ONE corrective respawn quoting the contract**; second failure → present as-is with a note.
21. Failure playbook — near-identical safe verdicts → respawn one as devil's advocate; credit monopoly → next spawn opens with the quiet member; circling → summarize the impasse and hand the operator the fork; weak card → present it anyway.
22. Context discipline — running summary **≤400 words**, refreshed every 2–3 rounds, from cards + the operator's words only; "caucus logs and presentations never enter the summary or other teams' spawns."
23. Idea ledger — append-only; "**Ideas never fall out**, however long the session runs"; killed ideas kept and flagged †; "teams must export even their rejects."
24. Endorsement ledger — "**Quote him; never paraphrase an endorsement into something stronger than he said, and never infer one from mere engagement**"; cooling marked `↓ cooled:` "rather than deleting it."
25. ASK — items "surface verbatim in the footer and **wait**"; answers fold into the running summary.
26. ASK cards — "never invent facts about the operator's situation."
27. Phase 0 — thin problem statement → "ask the operator the 2–4 questions that matter most *before* spawning anyone."
28. Phase 1 — "This phase has no round limit and no finish line the board can call."
29. Phase 2 — open by presenting the **full idea ledger including the odd, buried, and † killed entries** so the operator picks.
30. Phase 4 — closing overview in chat FIRST (~400–800 words incl. what the chair endorsed), then the brief file + INDEX row + clickable link; "**The overview is never skipped in favor of 'it's all in the brief'.**"
31. Phase 4 — "Then stop. **Do not propose next workflows or next steps** beyond the brief's own Next Actions."
32. Spawn rule 6 — teams "never suggest ending it, moving to another phase, or what process step should come next. That is the operator's call alone."
33. Spawn rule 8 — "**Do NOT use tools.**"
34. Brief template — "If nothing was endorsed, say so plainly rather than promoting the board's favorite."

---

# PART 3 — Duplicated rule/skill content

**Step 0 "Resolve the target project"** is the single largest duplication: present in 11 of the 14 project-scoped commands, in four different lengths — full 22-line (`sudo-code-review`, `sudo-write-story-tests`, `sudo-create-epic-sprint`, `sudo-self-audit`), 20-line (`sudo-dev-story-tests`), 18-line (`sudo-update-sprint-memory`), 23-line ASK-variant (`sudo-boot-sprint-memory`), 12-line (`sudo-push-e2e`, `sudo-e2e`), 11-line (`sudo-quick-dev`), 10-line dual-repo variant (`sudo-park`, `sudo-resume`). ≈210 duplicated lines total. Note: the command bodies write the pointer to `.agents/active-project.txt`, but 5 of the SKILL.md launchers say `_my_resources/active-project.txt` — an inconsistency between master and pointer.

**`.agents/rules/worktree-per-story.md`** — its "Resuming — a fresh chat picks the story back up" section is re-narrated in `sudo-dev-story-tests` Step 0.6, `sudo-code-review` Step 0.5, `sudo-boot-sprint-memory` Step 2b, `sudo-write-story-tests` Step 0.5, `sudo-quick-dev` Step 0.5. Its G1–G4 gate table + "Hard stops" are re-narrated in the "Done"/"Stay in lane"/"Git" footers of ①②③, `sudo-quick-dev`, `sudo-park`, `sudo-code-review_AP`. All five files name the rule by slug.

**`.agents/rules/git-policy.md`** — "The landing" bash block (fetch → merge origin/main_debug → push branch → `git push origin HEAD:main_debug`) is reproduced essentially verbatim in `sudo-update-sprint-memory` Step 7 and again (as park variant) in `sudo-park` Step 2. Its "Safe-commit mechanics" (explicit paths, `git add -A` ban, `git diff --cached --stat` check) is restated in 7 files. Its "Sync-first" and "if a push is rejected, STOP and report" appear in `sudo-update-sprint-memory` Step 7, `sudo-park` Step 2, `sudo-resume` Step 1. Its "Clear the Dummy GITHUB_TOKEN" always-rule is restated in `sudo-push-e2e` MANDATORY RULE 2 and `sudo-close-workingtree` Steps 1/4. Its "Validate CI/CD credentials" always-rule is restated in `sudo-push-e2e` Step 2.3. Only `sudo-write-story-tests` names `git-policy` explicitly.

**`.agents/rules/artifacts-always-first.md`** — §2 (artifact folder creation) is copied into `sudo-dev-story-tests` Step 0.5 (named); §5 (`walkthrough.md` as the ONE closing doc with `## Task Checklist` + `## Your Actions`) into `sudo-dev-story-tests` Step 5, `sudo-code-review` Step 5 (named), `sudo-update-sprint-memory` Step 6, both `_AP` twins; §7 (`self-audit-stress-test.md` must be standalone) into `sudo-dev-story-tests` Step 2 (named).

**`.agents/rules/tests-must-gate-for-real.md`** — named and paraphrased in `sudo-write-story-tests` Step 3 (ground-every-red), `sudo-dev-story-tests` Step 3, `sudo-code-review` Steps 3.1(a)(b)/3.4/3.5, `sudo-code-review_AP` gate step 4.

**`.agents/rules/code-standards.md`** — named as the referent of Step 3.5 in `sudo-code-review`; the clean-code-audit skill's own two-half structure (machine floor: ruff/eslint/pyrefly/tsc; judgment: comment contract §1, AI-drift bans §2/§2A/§2B) is re-explained across ~10 lines there and ~4 lines in `sudo-quick-dev` Step 3.

**`.agents/rules/bmad_code_review_sudo_fix.md`** — named by path in `sudo-code-review_AP` line 12 (pointer, not duplicated).

**`.agents/rules/constitution.md`** — "paste the actual output" rule restated in `sudo-dev-story-tests` Step 3, `sudo-dev-story-tests_AP` step 4, `sudo-push-e2e`, `sudo-quick-dev` Step 2b; "Ask-First"/decomposition in `sudo-self-audit` Phase 0.4; the shared-singleton + targeted-edits + research-first guardrails in `sudo-boot-sprint-memory` Step 3 and `sudo-self-audit` Phase 1.

**Skill-content duplication:** `sudo-code-review` Step 3.5 restates `clean-code-audit/SKILL.md`; `sudo-e2e` Step 2 restates what `frontend/e2e/run-e2e.mjs` does (6 bullets); `sudo-self-audit` Phase 1 restates the GitNexus MCP tool surface (~12 lines, overlapping the `gitnexus-*` skills); `sudo-push-e2e` Step 6 correctly points at `@.agents/skills/deploy-backend/SKILL.md` rather than duplicating.

**Stale/inconsistent references found:**
- `sudo-self-audit_AP.md:12` points at `@.agents/workflows/sudo-self-audit.md` — that file does not exist (`.agents/workflows/` holds only INDEX, merge_main_debug, new-project, security_team_aviationchat, slash_command_updating). Real path: `.agents/commands/sudo-self-audit.md`.
- Memory-write authority conflict: `sudo-code-review_AP.md:92` ("you NEVER write memory yourself … Daniel approves the write at close-out") vs `sudo-update-sprint-memory.md:129` ("**Memory (AUTOMATIC — validate, cross-check, write; no approval gate)**").
- `sudo-code-review.md:137` and `sudo-code-review_AP.md:75` both hard-code the trailer `Co-Authored-By: Claude Opus 4.8`.
- `sudo-push-e2e.md` and `sudo-e2e.md` have no `platforms:` frontmatter key; `sudo-quick-dev.md` is the only one listing all four platforms.
- No `sudo-write-story-tests_AP.md` exists (the autopilot lane folds ① into `sudo-dev-story-tests_AP` implement mode step 1).
- `sudo-bdd-tests.md` (68 lines / 5,990 bytes) is the hard dependency of both BDD gates but was not in the target list.