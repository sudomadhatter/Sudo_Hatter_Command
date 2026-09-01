---
IsArtifact: true
ArtifactMetadata:
  title: Rules folder optimization pass
  type: implementation_plan
  date: 2026-08-04
---

# Implementation Plan — `.agents/rules/` optimization pass

**Approved 2026-08-04.** Remove the contradictions and dead metadata in the rule set; no rule's *content*
rewritten. Already clean, no action: all 21 rules carry frontmatter with `name:` matching filename and a
`description:`; INDEX has a row for all 21, no ghosts.

## Findings

**F1 — load class had THREE sources of truth, disagreeing.** `AGENTS.md` §3, `rules/INDEX.md` (Load
column), and a frontmatter `activation:` on **12** of 21 rules that **nothing reads** (grep-verified
across `.agents/`, `docs/`, `.claude/`, `.opencode/`). The three floor rules agreed; the rest did not:

| Rule | AGENTS.md §3 | INDEX | `activation:` |
|---|---|---|---|
| **artifacts-always-first** (21 KB) | **always-load** | **protocol** | Always On |
| **git-policy** | on-demand *(omission)* | **protocol** | *(none)* |
| **worktree-per-story** | on-demand *(omission)* | **protocol** | Protocol |
| **000-PLAN-FIRST-GATE** | on-demand *(omission)* | **protocol** | **Always On** ← three answers |
| **powershell-encoding-safety** | on-demand | on-demand | **Always On** |
| dependency-awareness | on-demand | on-demand | Model Decision (vocabulary) |

`000-PLAN-FIRST-GATE` is the priority-zero kill-chain — three sources, three answers. Vocabulary was mixed
too: house terms, **Cursor's** ("Always On", "Model Decision"), and freeform prose.

**F2 — three duplicated passages** (shared 8-word runs across all 210 rule pairs; only these three passed
threshold): the "`git status` becomes a soup" rationale → owner **worktree-per-story**; the plan-gate
**When to Skip** exemption list → owner **artifacts-always-first**; the sign-off definition → proposed
owner `git-policy`. Two copies of a gate's exemptions is the dangerous one — they drift, and each reads
authoritative.

**F3 — INDEX rows not grouped by their own Load column**, so it didn't read in load order.

## Changes

- **C1** — delete `activation:` everywhere. Load class then has two live statements: `AGENTS.md` §3 and
  the INDEX Load column.
- **C2** — reconcile §3 with the INDEX's three tiers. §3 had two, so the protocol set got flattened:
  `artifacts-always-first` promoted into always-load, the other three swept into on-demand by §3's
  "everything else" sentence. Fix: §3 keeps the three true floor rules and names all four protocol rules.
  **The only real token win** — a 21 KB rule stops loading in conversation-only sessions.
- **C3** — de-duplicate F2's passages; the non-owning copy becomes a pointer.
- **C4** — group INDEX rows by Load class, preserving every row's text.
- **C5 (added during execution)** — make the protocol load a **binding trigger**, plus the anchor
  invariant: every protocol rule's law must also be stated inline in `AGENTS.md` **and** the floor
  `constitution.md`. See Self-Audit A1/A2.

## Files touched

`AGENTS.md` (§3 + ⛔ ARTIFACTS block) · `docs/workspace-standard.md` §4 · `.agents/rules/INDEX.md` · the
12 rules carrying `activation:` · `git-policy` + `000-PLAN-FIRST-GATE` (C3) · `constitution` (C5).

## Report-only — deliberately NOT changed

- **Three `[[memory-links]]` in `tests-must-gate-for-real`** resolve to nothing here — not in the live
  slug, not in either stranded slug. **Leave them:** forward-links are legitimate by the memory
  convention and the laptop holds newer memories; deleting would destroy real links once stores merge.
- **Two pre-existing `check_maps` failures** — stale AUTO block (NEXgen folders) + dead
  `_my_resources/migrations/_secrets/master.env` in `repo-map.md`, from the `_system/` rename.
  `/update-maps-indexes`' job.

## Out of scope

Splitting `artifacts-always-first` (21 KB). Renaming `bmad_code_review_sudo_fix.md` to kebab-case — the
only underscore filename, but it touches the sync manifest + vendored copies in three projects.

## Verification

`check_maps` no worse than the two pre-existing failures · all 21 rules keep `name:`+`description:` with
`name:` matching filename · INDEX still 21 rows, regroup proven by sorted-line diff · each de-duped
passage in one place with a pointer · `activation:` zero hits · EOL integrity · anchor invariant holds.

---

## Self-Audit (2026-08-04)

**Right-size: LIGHT.** No code, no ACs, no state machine, no contract — Phase 1 blast-radius and Phase 3
pre-mortem had nothing to bite on, skipped with cause. Walked Phases 0, 2, 4. Audited **after** execution
at Daniel's direction, so findings are verified against what landed, not predicted.

**Phase 0 — traceability.** Every step maps both ways: C1→12 files, C2→§3 + `workspace-standard.md`,
C3→2 of 3, C4→regroup. One step **added** mid-execution (C5) — justified below.
**Phase 2 — over-engineering.** No new abstraction, dependency, option, or layer; C1/C3/C4 are net
deletions, C2/C5 add prose to existing sections. **Clean.**

### Findings

| # | Sev | Finding | Disposition |
|---|---|---|---|
| A1 | **MED** | **C2 made the protocol tier conditional without making the condition binding.** §3 read "load the moment a session may touch files" — descriptive, not imperative; an agent could read it and never load the plan-first gate. Caught by Daniel, not by me. | **FIXED** — §3 PROTOCOL is now an imperative trigger: load *before* the first file-writing tool call, else stop |
| A2 | **MED** | The anchor invariant from A1 **failed its own first test**: `000-PLAN-FIRST-GATE` had 0 refs in the floor `constitution.md`. Pre-dated this session, but C2 made it load-bearing. | **FIXED** — added to constitution Hard Stops; all four now OK |
| A3 | LOW | **Unapproved scope creep:** renamed §3's heading `ALWAYS-LOAD` → `WHAT LOADS, AND WHEN`, breaking three references keyed on that name. | **FIXED** — heading reverted; `workspace-standard.md:52` updated (already wrong — omitted `operator-profile`) |
| A4 | LOW | **Plan step dropped:** de-dupe 3 (constitution ↔ git-policy sign-off) NOT executed. `constitution` is floor, `git-policy` is now protocol — stripping the floor summary would leave floor deferring to an unloaded file, the exact hole C2 closed. | **DROPPED, justified** |
| A5 | INFO | Plan said 11 rules carried `activation:`; actual was **12**. | Miscount in the plan; all 12 stripped |
| A6 | **MED** | **`.agents/templates/project-template/AGENTS.md:10` still carries the old 2-tier `ALWAYS-LOAD`.** New projects cloned from the template start with the pre-fix model — the drift this pass exists to remove, reintroduced at birth. | **OPEN** — outside approved scope; folded into the propagation pass |
| A7 | LOW | `_my_resources/diagrams_guides/system/…:79` describes §3 as constitution + karpathy + artifacts-always-first only. | **REPORT ONLY** — protected area |
| A8 | **MED** | `NEXgen-VR-Director` is in `maintained-projects.txt` but has **no root `AGENTS.md` at all**. `RAG_Pipeline_AC` has one (`## 4. ALWAYS-LOAD`) but is **not** maintained. | **OPEN** — propagation scope needs Daniel's call |

### Four gates

- **Verification strategy present?** Yes — 7 checks run, output pasted. V7 (line-ending integrity) was
  **added during execution**: a scripted frontmatter strip is exactly the bug class
  `powershell-encoding-safety` exists for. All 12 files 100% CRLF, 0 bare LF, 1-line diffs. A plan that
  edits by script without checking EOLs is under-verified — a real gap in the plan as written.
- **Irreversible?** No — one frontmatter line each plus two prose passages, all recoverable from git.
- **Any step vague enough a dev would guess?** C4 ("group by load class") was; mitigated by proving the
  regroup with a sorted-line diff — identical as sets, reorder only.
- **Quality fit?** Yes — kebab-case, frontmatter shape, INDEX row shape, CRLF all preserved.

**Audit verdict: GO** — with A6 and A8 carried into the propagation pass as required work, not optional.
The landed change is sound; the two open items are about **reach**, not correctness.

<!-- CHECKPOINT id="ckpt_msfe04m0_rt87hk" time="2026-08-05T01:07:08.760Z" note="auto" fixes=0 questions=0 highlights=0 sections="" -->
