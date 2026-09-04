---
IsArtifact: true
ArtifactMetadata:
  title: Scrum-board command + AGY workflows/testing doc refresh
  type: implementation_plan
  date: 2026-08-03
---

# Plan — refresh `/sudo-update-scrum-board` + `sudo_workflows_testing.md`

**Goal:** bring both surfaces current with the uncommitted 2026-08-02 artifact restructure + the
test-certification contract, so the board reads the right verdict and the reference stops confusing you.
**Grounding:** the full uncommitted `git diff` (rules, ①②③, `_AP` twins, autopilot).

**The delta both files miss** — `self-audit-stress-test.md` → `## Self-Audit` **inside** the plan
(`Audit verdict:`); `code-review.md` / `sudo-code-review-<story>.md` → `## Code Review` **inside** the
walkthrough (`Verdict: … @ <sha>`); walkthrough now outline-first (`Task Checklist → Evidence → Suite
Ledger → Code Review → Your Actions`); plan ≤8 KB / walkthrough ≤10 KB. Pre-08-02 stories keep the old
files as **read-only history**.

## WS-1 — [sudo-update-scrum-board.md](.agents/commands/sudo-update-scrum-board.md)

14,895 B — already over the 11,500 B threshold and already a verified THIN LAUNCHER, so growth is free.
Six edits, in the file's existing ⛔ / one-line-per-cell voice:

1. **Step 1 read-list #7** — add the lane's `walkthrough.md`: its `Verdict: … @ <sha>` line, its open
   `## Your Actions` rows, the plan's `## Self-Audit` findings.
2. **Step 2, "Review PASS, not landed"** — name where the verdict is read: walkthrough `## Code Review`
   → `Verdict:`; legacy fallback `sudo-code-review-<story>.md`.
3. **Step 2 hard rules — new ⛔ a stale verdict is not a verdict.** `@ <sha>` ≠ branch HEAD → the row is
   `/sudo-code-review <id>`, never `/sudo-update-sprint-memory`.
4. **Step 2 hard rules — new ⛔ collapse the set.** ≥2 landable lanes of one epic = **ONE** row,
   `/sudo-merge-epic-workingtrees <epic>`, not N× close-out. ⚠️ **F5** — traces to no uncommitted
   change; pre-existing gap, **operator-cuttable**. A *collapse* rule, not an extra row, to protect the
   ~150-line cap.
5. **Step 2.5 touch-sets** — add the plan's `## Self-Audit` findings paths to the authority order.
6. **Step 3 tail + Step 5 checklist** — sources-of-truth gains `_artifacts/`; checklist gains "every
   landable row's verdict read at a SHA matching branch HEAD" (makes #3 enforced, not advisory).

**Not changing:** five zones, ~150-line cap, display rule, grounding gate, quick-dev P2/P3 eligibility.

## WS-2 — [sudo_workflows_testing.md](Projects/AGY_AVIATIONCHAT/_my_resources/_quick_reference/sudo_workflows_testing.md)

Rewrite in place (19,519 B, stamped 2026-07-24). Committed + clean → git is the undo.

**Dead links — verified against disk, must not survive**
- ⚠️ **F1 (revised at build time):** `tea_deep_reference.md` (6, 302) is not in AGY — but it **does**
  exist in the lobby at `_my_resources/diagrams_guides/workflows_tea_testing/`. The AGY doc is a
  relocated copy still carrying lobby-relative links. **Repoint `../../../../`, don't delete.**
- ⚠️ **F2 (revised at build time):** same cause — `sentry_error_response_team.md` lives at the lobby's
  `_my_resources/diagrams_guides/security/`. Keep it as §12's "full picture" link, repointed.
- ⚠️ **F3:** `docs/workspace-standard.md` + `AGENTS.md` (304–305) are bare paths **and** resolve wrong
  from `_quick_reference/` → `../../docs/workspace-standard.md`, `../../AGENTS.md`.

**Corrections** — `/autopilot-claude` (hyphen) exists in **no** command dir; only `/autopilot_claude`.
Epic kickoff is `/sudo-create-epic-sprint` (verified: wraps `bmad-create-epics-and-stories`). §8:
Stage 2 → *appends `## Self-Audit` to the plan*, Stage 4 → *appends `## Code Review` to the
walkthrough*; resume is section-presence, not file-presence.

**Added to §3:** `/sudo-update-scrum-board` · `/sudo-create-epic-sprint` ·
`/sudo-merge-epic-workingtrees` · `/sudo-prune-context` · `/sudo-adviser-board` · `/autopilot_deepseek4`.

**New § artifact contract** — one table: the two living docs, sections in order, who writes each
(② dev / ③ review), budgets, retired vs read-only history, and that TEA test-artifacts are **out of the
lean set by design**.

**New § certification contract** — feedback ≠ certification; the full suite certifies **once**, at the
shipping SHA, **after** `testarch-automate`. ② Step 4.5 emits
`_bmad-output/test-artifacts/certification-<story>.json` (verified); ③ compares its `sha` to HEAD —
match + `failed: 0` → inherit, else re-run. Backend suite = **278 s serial**; per-story floor **2 runs
≈ 9.3 min**; ②+③ ~17 → ~11 min. `_AP` lanes carry the rule, emit **no JSON**. Mutation proof =
**RELOCATE** the guard. Only citable forms count (FULL-TREE).

> ⚠️ **F4 — binding constraint on both new sections.** They restate content OWNED by `.agents/rules/`
> (`tests-must-gate-for-real` Rule 4, `artifacts-always-first` §5–7). A duplicated invariant is the
> toolkit's known drift mechanism. Write at **reference depth only** — shape, numbers, file names — and
> link the rule as authority. Never restate normative text the rule owns.

**Updated:** §4 loop table (② Step 4.5 · ③ inherits-or-reruns · close-out reads `Verdict:`). §6.6 — the
backend suite is pinned **SERIAL** in two verified places (`pr-check.yml:166` AIDEV-NOTE +
`backend/requirements.txt:49`) and **both flip together**.
**New § scrum board:** five zones · 🧵 membership = safe beside every other 🟢 · only
`/sudo-update-scrum-board` writes it.
**Cut:** the 07-24 header note (→ dated one-liner) + the `<!-- CHECKPOINT -->` md-feedback marker (F8).

## WS-3 — propagation

`/sync-agents` (lobby) + `-Maintained`. ⚠️ **F7:** verify the **AGY mirror**
`Projects/AGY_AVIATIONCHAT/.claude/commands/sudo-update-scrum-board.md` — separate copy; a lobby-only
sync leaves AGY on the old body. WS-2 is an AGY doc — **not** synced.

## Verification plan

1. In both files, every hit for `self-audit-stress-test|code-review\.md` must **also** match
   `legacy|history|pre-2026-08-02` (F6 — the earlier phrasing wasn't runnable).
2. Board: six edits present; five zones + ~150-line language + display rule unchanged (`diff`).
3. Every `/command` the doc names resolves to a real file in `.agents/commands/` — scripted.
4. Every link in the doc resolves **from its own directory** — scripted (what F1–F3 would have reshipped).
5. `/sync-agents` clean; launcher still emitted; AGY mirror byte-matches master.

## Your Actions

Reply **`approved`** to proceed. Nothing outside `_artifacts/` is touched until then.

---

## Self-Audit (2026-08-03)

**Right-size: Full** — rewrites an operator-facing reference and edits the command that drives every
"what do I run next" decision. Target: `Projects/AGY_AVIATIONCHAT` + the lobby toolkit master (WS-1).

| Phase | Walked — checked and cleared |
|---|---|
| 0 Scope/AC | Both asks map to concrete WS; no AC without a step; **one step without an AC → F5**; docs-only, no BE/FE split. |
| 1 Blast radius | Every claim traced to disk, not memory: launcher ✅ · cert-JSON path ✅ · `sudo-create-epic-sprint` wraps `bmad-create-epics-and-stories` ✅ · no hyphen `autopilot-claude` anywhere ✅ · SERIAL pinning ✅ (`pr-check.yml:166`, `requirements.txt:49`). **Link targets failed → F1–F3.** Board consumers (drift-stamp markers, five-zone contract) unaffected by all six edits. Neither file is in the uncommitted set — no lane collision. |
| 2 Over-engineering | No new abstraction, dependency, or generalization; WS-1 stays inside the existing zones. Two tripwires fired: step-with-no-AC → **F5**; rebuilding-what-exists → **F4**. |
| 3 Pre-mortem | Dominant failure: reshipping the same dead links (**F1–F3** — the doc's whole §10 is unreachable today). Then master-edited-mirror-stale (**F7**); then a verification step that can't run (**F6**). Destructive check: WS-2 overwrites 19.5 KB, committed + clean → git is the undo. |

| # | Where | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| F1 | `sudo_workflows_testing.md:6,302` | HIGH | The doc's stated home for all depth material is unreachable from AGY; "keeps its shape" carries the broken link forward | **Revised at build:** target is real, in the LOBBY — repointed `../../../../`, not deleted |
| F2 | `:294,303` | HIGH | §9's "full picture" link unreachable → incident runbook lost | **Revised at build:** same cause — repointed to the lobby copy; `incident-triage.md` added beside it |
| F3 | `:304-305` | MED | Bare paths that also resolve wrong from `_quick_reference/` — breaks the clickable-link rule this plan cites | Fixed to `../../` form |
| F4 | WS-2 new §§ | MED | Restating rule-owned invariants creates a second body that drifts | Reference depth + link authority |
| F5 | WS-1 #4 | MED | Scope creep; an extra row per lane also fights the ~150-line cap | Kept as a **collapse** rule, operator-cuttable |
| F6 | Verification #1 | LOW | "0 outside labelled legacy lines" isn't machine-checkable → vacuous green | Runnable two-pattern check |
| F7 | WS-3 | LOW | Lobby-only sync leaves AGY's copy on the old body | Explicit mirror check |
| F8 | WS-2 cut | LOW | Silently deleting an md-feedback marker | Stated; that MCP is disconnected, nothing breaks |

**Four gates.** *Verification:* present, now runnable (F6). *Irreversible:* one full-file overwrite,
committed + clean, git is the undo — no migrations, no data. *Vague steps:* WS-2's "rewrite in place"
tightened by the explicit section list + F1–F3's named fixes. *Quality fit:* anchored — WS-1 matches the
command's ⛔/one-line-per-cell voice; WS-2 keeps its section shape and the house link rule.

**Audit verdict: GO** — F1–F3 + F6 mandatory and already baked in; F4 binds how WS-2 is written; F5 is
yours to cut.
