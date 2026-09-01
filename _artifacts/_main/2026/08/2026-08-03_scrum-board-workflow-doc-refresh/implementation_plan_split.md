---
IsArtifact: true
ArtifactMetadata:
  title: Split sudo_workflows_testing.md into a how-to + a contracts reference
  type: implementation_plan
  date: 2026-08-03
---

# Plan — split the 34 KB quick reference into two single-purpose docs

**Goal:** no question costs more than ~16 KB of context, and no section duplicates a doc that already
owns the material. **Follow-on to the approved WS-2**, same file.

## What's actually wrong (measured, not opinion)

1. **One file serves four different jobs.** How-to (what do I type), reference (the exact contract
   shape), explanation (the map), and tutorial (learn-once testing method) are interleaved across 533
   lines. Separating those four is the [Diátaxis](https://diataxis.fr) standard; mixing them is its
   named anti-pattern. It's why you scroll.
2. **§7.2–7.5 duplicate the lobby's `tea_deep_reference.md` (53 KB), which owns them deeper** — its §3
   test levels, §4 good-test bar, §7 + §7.5 ATDD/BDD, §12 the L1–L4 pyramid. ~60 redundant lines that
   will drift.
3. **The directory is already a multi-doc set** — `sprint_scrum_board_map.md` (12 KB),
   `SOP_curriculum_operations.md` (15 KB), `login_testing_credentials.md` (7 KB). One doc at 34 KB is
   the outlier, at 2.8× the next largest. Splitting is the house pattern, not a new idea.

**Context cost today:** every question loads 34 KB (~10k tokens). After: a "what do I run" question
loads ~16 KB (~4.5k); a "what's the exact contract" question loads ~12 KB (~3.5k).

## WS-A — `sudo_workflows_testing.md` becomes the how-to (~16 KB, ~260 lines)

Name stays — it is referenced from four projects' `_my_resources/AGENTS.md`. Keeps:

| § | Content | Why it's here |
|---|---|---|
| — | **`## Start here`** — the situational "I want to → run this" table + a one-line section index | the entry point the doc has never had |
| 1 | the map (mermaid) | orientation |
| 2 | style in 60 seconds — **cut 30 → ~8 lines** (drop what §3/§5/§6 restate) | the two rules that sit above every command |
| 3 | every `/` command by lane | the daily lookup |
| 4 | the loop step by step (+ the "Writes" column) | what happens in what order |
| 5 | shipping / the e2e gate | — |
| 6 | the autopilot lane | — |
| 7 | the scrum board | — |
| 8 | the security / error team | — |
| 9 | where the depth lives (both homes) + **a link to the new contracts doc** | navigation |

## WS-B — new `sudo_artifacts_and_gates.md` (~12 KB)

Everything you or an agent needs **verbatim and exact**, moved out of the how-to:

- **The artifact contract** (today's §5) — the two living docs, sections in order, who appends what,
  the two canonical lines (`Audit verdict:` / `Verdict: … @ <sha>`), budgets, retired-vs-history.
- **The certification contract** (today's §8) — feedback ≠ certification, ③'s mechanical
  inherit-or-rerun, the JSON shape, the binding consequences, what it costs.
- **The test gate + verdicts** (today's §7.7) — `sudo-tests.yaml` + the four verdicts.
- **CI/CD — what runs where** (today's §7.6), including the two-place SERIAL pinning.
- **P0–P3 risk matrix + quick-dev eligibility** (today's §7.1) — a lookup table, not curriculum.

Same F4 constraint as before: **reference depth only** — shape, numbers, file names — each section
linking its owning rule in `.agents/rules/` as authority. Never restate normative text.

## WS-C — the curriculum stops being duplicated

Today's §7.2–7.5 are **deleted from AGY** and replaced with four one-line pointers into
`tea_deep_reference.md` (§3 · §4 · §7/§7.5 · §12). Zero information loss — the lobby copy is deeper
and is the owner. This is the fix for finding 2.

## WS-D — registration

- New doc added to §9's depth table **and** to the how-to's `## Start here` index.
- Add `sudo_artifacts_and_gates.md` to the `e.g.` list in
  `Projects/AGY_AVIATIONCHAT/_my_resources/AGENTS.md:14` so agents know it's readable.
- ⚠️ **Out of scope, flagged only:** the lobby's `_my_resources/diagrams_guides/INDEX.md:13` points at
  a `sudo_workflows_testing.md` that doesn't exist there, and `tea_deep_reference.md` §10–§11 carry
  their own slash-command + sudo-flow sections that now lag. Both belong to `/update-maps-indexes`.

## Verification

1. Both docs: every markdown link resolves **from its own directory** — the existing scripted checker,
   re-pointed at each file.
2. Every `/command` named in either doc resolves to a real file in `.agents/commands/`.
3. `grep` proves the curriculum sections are gone from AGY and present as pointers — zero headings
   matching `Test levels|L1–L4 pyramid|ATDD · BDD|What a good test is` outside a pointer line.
4. Size gate: how-to ≤ 18 KB, contracts ≤ 14 KB, neither over ~280 lines.
5. No content lost: every §-heading in today's 13-section file maps to a destination (kept / moved to
   contracts / pointed at the lobby) — one table, checked row by row before writing.

## Your Actions

Reply **`approved`** to proceed. Nothing is touched until then; today's file stays as it is.

One call worth making now, not after: **`sudo_artifacts_and_gates.md`** is my proposed name for the new
doc — descriptive and greppable. Say the word if you want a different one.
