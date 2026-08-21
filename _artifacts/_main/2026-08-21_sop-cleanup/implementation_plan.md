---
ArtifactMetadata:
  mobile: true
---

# 📱 Implementation plan — de-clutter the operator SOP (`workflows_testing_SOP.md`)

**Ask (Daniel, 2026-08-21, web session):** *"The goal of this document is supposed to be a place to
keep all the changes to your SOPs for development, as well as be a guide for me and other users to
reference. When it gets cluttered with explanations of changes it's not serving its purpose. We need
clean rules and descriptions, and clean guides of how to use them."*
**Branch:** `claude/sop-document-cleanup-qk778r` · plan-only until approved.

## TL;DR

The SOP is a good guide with a changelog leaking through it. The fix is three moves: **(1)** give
change-history its own file (a one-line-per-change changelog beside the SOP), **(2)** rewrite the
SOP's spine to state only the *current* rule in present tense — every "⭐ what changed", "since
SCC-x", "renamed from", "no longer" passage either becomes a plain statement of today's rule or
moves to the changelog, **(3)** add a writing contract to `sop-currency.md` so the gate that forces
every future update also forces the *clean* shape of update — otherwise the clutter grows back
within weeks.

## Diagnosis — measured 2026-08-21 on this branch

`docs/_scc_sops_prds/workflows_testing_SOP.md` is **319 KB / 3,770 lines** — larger than the next
four SOPs combined. The page's two-level design (a clean "spine" + 39 `ⓘ Why it works this way`
asides) is sound, but change-narration has leaked into the spine itself:

| Pattern | Count |
|---|---|
| `SCC-nnn` ticket references | 167 |
| Full dates (`2026-mm-dd`) | 69 |
| `⭐` "new/changed" markers | 91 |
| "changed" | 42 |
| "used to / previously / renamed from" | 32 |
| "no longer" | 27 |
| "retired" | 17 |
| Blockquote lines (asides + change notes) | 596 |

Typical spine text today: *"⭐ What changed at Step 4 (SCC-240): the roster example is no longer
shown in a code box…"*, *"Renamed 2026-08-14 (SCC-155). This was `/cicd-parallel-check`; that name
is retired…"*, *"since SCC-210 it is named for what you asked for"*. An operator reading to learn
*what to type* has to parse the delta against a version they never saw.

**Root cause, not carelessness:** the `sop-currency` commit gate forces this page to move in the
same commit as every usage change — correct — but nothing constrains the *shape* of that edit. The
cheapest compliant edit is an appended "what changed" note, so every ticket appended one. The rule
file (`sop-currency.md` §Writing the update) already says **"Retire, don't accrete"**; the doc shows
the habit is not self-enforcing. A cleanup without a codified writing contract will re-clutter.

## The design

- **The SOP spine states the current system only** — timeless present tense. No ticket numbers, no
  dates, no ⭐-new markers, no before/after narration. A retired command or rule simply is not on
  the page (per the existing habit 2).
- **Change-record lives in a new sibling file** `workflows_testing_SOP_changelog.md` — reverse-
  chronological, **one line per change**: `date · ticket · what changed for the operator`. This
  keeps "a place for all the changes" (the ask) without interleaving it with the rules. All 167
  ticket references get harvested into it during the rewrite, so no provenance is lost (git history
  keeps the rest).
- **The `ⓘ` asides stay, compressed** — they are the doc's designed review surface (real incident →
  rule), and that is *why*-history, not *what-changed*-history. Each is capped at one short
  paragraph; asides that are pure change-narration move to the changelog or die.
- **The writing contract becomes law**: `sop-currency.md` §Writing the update gains rule 4 — *"Write
  the current state, present tense. Change-narration ('since SCC-x', dates, ⭐ markers, before/after)
  goes in the changelog file as one line, never in the spine; incident lessons go in a ⓘ aside."*
  The SOP's own "How to read this page" header states the same contract, so both the human and the
  gate-driven agent see it at edit time.

## Steps

| # | Step | Proof |
|---|---|---|
| 0 | Baseline: record size/pattern counts (above); snapshot heading list so anchors can be diffed | this plan |
| 1 | **Contract first.** Add rule 4 to `sop-currency.md` §Writing the update; add the contract to the SOP header. (`sop-currency.md` is a usage surface → SOP staged in the same commit satisfies the gate honestly.) | gate passes without `[sop-ok]` |
| 2 | **Changelog home.** Create `workflows_testing_SOP_changelog.md`; add its INDEX.md row; add filename to `EXPECTED` in `.agents/scripts/tests/test_sops_prds_folder.py` (the manifest is a three-edit contract) | manifest test green |
| 3–9 | **Rewrite the spine, one Part per commit** (I, II, III, IV, V, VI, VII). Per passage: current-state rewrite in place · ticket/date → one changelog line · retired references deleted · `⭐` removed (from headings too, updating TOC + every in-doc link — the folder test checks link targets) | per-Part commit, links test green |
| 10 | **Aside audit.** Compress the 39 `ⓘ` asides to ≤1 paragraph each; relocate/delete pure change-notes | count + size report |
| 11 | **Verify.** `python3 .agents/scripts/tests/test_sops_prds_folder.py` · `check_maps.py` · full `run_all` if the container permits; confirm every command named in "Start here" resolves to a real master | pasted output |
| 12 | **Report.** Size before/after (target: spine ≤ ~60% of today without losing one rule); walkthrough.md with evidence | walkthrough |

## Not in scope (named so it isn't silently absorbed)

- The stale **AGY twin** (`sudo_workflows_testing.md`) — cross-repo, needs an AVCH ticket per
  `sop-currency.md` §Known drift. The changelog gives that future ticket a clean base.
- The **other 11 docs** in `docs/_scc_sops_prds/` — same disease in milder form; follow-up ticket
  after this one proves the pattern.
- Any change to what the **rules themselves say** — this is form, never content. Where a passage is
  ambiguous about what the current rule *is*, I stop and ask rather than guess.

## Decisions for Daniel (tap in chat)

1. **Approve / change** this plan.
2. **Changelog home:** separate file (recommended) · appendix at the SOP's bottom · git-history only.
3. **Command atlas (Part VI, 45 diagrams, ~30% of the page):** keep in-page (recommended — it's
   reference, not clutter) · split to its own doc.
