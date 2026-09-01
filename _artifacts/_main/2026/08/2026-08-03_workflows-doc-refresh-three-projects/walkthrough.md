---
IsArtifact: true
ArtifactMetadata:
  title: Rebuild sudo_workflows_testing.md across lobby + AGY + Fresh (mermaid-led)
  type: walkthrough
  date: 2026-08-03
---

# Walkthrough — the workflows doc, ×3

Plan: [implementation_plan.md](implementation_plan.md) · `main_debug` in each repo, explicit paths.

## Task Checklist

- [x] **WS-1 — the canonical body**, written once as the [lobby master](../../../_my_resources/_quick_reference/sudo_workflows_testing.md)
  (27,265 B / 499 lines). Replaced a **2026-07-24** ancestor that still documented retired standalone
  audit/review files and a `/autopilot-claude` launcher that has never existed.
- [x] **WS-2 — [AGY](../../../Projects/AGY_AVIATIONCHAT/_my_resources/_quick_reference/sudo_workflows_testing.md)**
  (28,001 B) — same body, AGY header + §13.
  - [x] **[sudo_artifacts_and_gates.md](../../../Projects/AGY_AVIATIONCHAT/_my_resources/_quick_reference/sudo_artifacts_and_gates.md)**
    13,591 → 18,450 B. New **§6 the enforcement layer** (six scripts, the receipt contract, the
    pre-commit encoding gate) and **§7 sprint status and history** (the Wave 4 split, the ≤120-char note
    budget, how the migration was proven). Autopilot 6→8, who-owns-what 7→9. Gate receipts added to §1's
    machine-artifact note. Without this the contracts doc would have contradicted the new how-to.
- [x] **WS-3 — [Fresh](../../../Projects/Fresh_Workspace_BMAD/_my_resources/_quick_reference/sudo_workflows_testing.md)**
  (28,312 B) — **new file**; the folder existed but held only a board stub.
- [x] **WS-4 — register + land.** No `AGENTS.md` edit was needed anywhere: both the
  [lobby's](../../../_my_resources/AGENTS.md#L11) and
  [Fresh's](../../../Projects/Fresh_Workspace_BMAD/_my_resources/AGENTS.md#L14) standing-exception lists
  already name `sudo_workflows_testing.md`. The doc was missing, not the permission.

### How the three copies were built

The body was written **once** and the two project copies were **spliced from it programmatically** —
header + extracted body + footer — rather than retyped. Byte-identity is therefore a property of the
build, not of my care, and check 1 measures it.

### What's new in the content

Seven things had landed today (21:49–23:36, after AGY's copy was last written at 20:58) and appeared in
no reference doc: the six enforcement scripts and where each one fires · the Wave 4 board split ·
the pre-commit encoding gate and its `core.hooksPath` trap · `/sudo-resume`'s `main`-promote hazard ·
boot's verdict resolution · `gate_receipt.py`'s no-`--result` design and content-not-SHA staleness ·
the 94-case suite.

## Evidence

| Plan check | Result |
|---|---|
| 1 · body byte-identical across all three | ✅ **same MD5** (`5aa51a25…`) for lobby · AGY · Fresh |
| 2 · every link resolves from its own directory | ✅ 13 / 14 / 14 unique targets, **0 dead** — plus 0 dead in the contracts doc |
| 3 · mermaid standards | ✅ **8 blocks per copy**, 8 fence-closes, `sequenceDiagram`=0, bare `&`=0, HTML tags=0 |
| 4 · every `/command` resolves to a real file | ✅ 2 benign non-matches only: `/autopilot-claude` (appears once — in the line saying it doesn't exist) and the generic `` `/command` `` placeholder |
| 5 · the new facts present in **all three** | ✅ **10/10 at 3/3** |
| 6 · voice | ✅ 8 mermaid blocks, 8 "what you're looking at" intros; hazards stated as outcomes; terms explained inline |
| 7 · repos clean and pushed | ✅ see Suite Ledger |

Checker: `scratchpad/verify_docs.sh` (scripted, re-runnable). No code changed → no test suite in scope.

**Diagrams went 1 → 8**: the system map · the ①②③ loop *showing what each stage writes* · the
enforcement layer · the verdict-validity decision tree · shipping A/B/C · park→resume with the promote
hazard on the failure edge · autopilot's resume-by-section · incidents.

## Suite Ledger

| Scope | Command | Result | Why this run |
|---|---|---|---|
| link · mermaid · command · fact · identity checks | `bash verify_docs.sh` | pass | plan checks 1–6 |
| contracts-doc numbering + links | inline grep | pass — 9 sections, 0 dead | after the §6/§7 insert |

## Your Actions

| # | Pri | Action | Closes |
|---|---|---|---|
| 1 | 🟢 | The lobby's [`diagrams_guides/INDEX.md:13`](../../../_my_resources/diagrams_guides/INDEX.md#L13) still points at a `workflows_tea_testing/sudo_workflows_testing.md` that does not exist — the doc lives in `_quick_reference/`. `/update-maps-indexes` owns it; out of this session's scope | lobby index accuracy |
| 2 | 🟢 | These are `_my_resources/` docs — **`/sync-agents` does not carry them.** Three copies stay hand-maintained; the identical-body build is what keeps that cheap. When the toolkit changes again, re-splice rather than editing three files | drift control |
| 3 | 🟢 | `B-L-WorldWide` and `BRKN_Tattoos` have no copy of this page and are [deliberately unmaintained](../2026-08-03_verdict-contract-propagation/implementation_plan.md) — noted, not owed | scope clarity |
