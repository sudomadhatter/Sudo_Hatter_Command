# Self-Audit (2026-08-28) — Adviser Board filter rework

> **Placement note:** `/smh-self-audit` appends this section into the plan itself, but the operator's
> instruction for this run was "do NOT edit the plan", so it is delivered standalone in the plan's own
> artifact folder. Merge it into [implementation_plan.md](implementation_plan.md) as `## Self-Audit
> (2026-08-28)` before approval — the findings below are written to be baked in inline per the command.
>
> *(Update 2026-08-28: the operator then ordered the audit-remediation amendments — F1/F2 blocks,
> F3–F7 inline markers, a `## Self-Audit` note — applied to the plan; verdict flipped to GO below.
> The findings are preserved as written.)*

- **Plan audited:** `_artifacts/_main/2026-08-27_adviser-board-filter-rework/implementation_plan.md`
- **Repo:** `Sudo_Hatter_Command` (command centre — a legitimate subject for this command) · branch: main checkout
- **Mode:** PRE-WORK · **Level:** LEDGER+BLAST (the plan touches a command/door surface — `.agents/commands/smh-adviser-board.md` plus four platform doors — so all three lenses ran)
- **Ticket:** none yet (plan §10 defers minting to implementation start — see F2)

---

## lens:        1 Repo Reality + Scope Ledger

checks_run:  every path the plan names verified on disk (command brain, all 7 folder files incl. `minds/`, `.claude/skills/smh-adviser-board/SKILL.md`, `.opencode/commands/smh-adviser-board.md`, `.agents/workflows/smh-adviser-board.md`, `bmad-party-mode/SKILL.md`, `jira.md`) · plan's section-by-section claims checked against the live command body (12 traffic rows, Steps 2–8, frontmatter phrases, inline floors rule, standing rules) · plan's contract-file claims checked (TEAMS default triads, ROSTER stage annotations, SPAWNS §1–§7, DOCTRINE team line, CARD caucus clause, THIRD-SIDE two-axis paragraph) · `## Declared Change Set` block searched for in the full 267-line plan · Scope Ledger run over the change list · lane-fit check (no deployable product path touched)
read:        implementation_plan.md (full) · .agents/commands/smh-adviser-board.md (full) · .agents/commands/adviser-board/{TEAMS,ROSTER,CARD,SPAWNS,DOCTRINE,THIRD-SIDE}.md (targeted) · .claude/skills/smh-adviser-board/SKILL.md · .agents/workflows/smh-adviser-board.md · .agents/workflows/INDEX.md · .agents/commands/INDEX.md · .agents/scripts/sync-agents.ps1 (excluded list) · docs/_scc_sops_prds/{smh-adviser-board-REFERENCE.md,workflows_testing_SOP.md,workflows_testing_SOP_changelog.md,INDEX.md} · _artifacts/_memory/{adviser-board-caucus-card-contract,adviser-board-roster-is-product-shaped,operator-chairs-the-board}.md · _artifacts/_main/2026-08-26_SCC-331-adviser-board-rework/walkthrough.md
verdict:     findings below

## lens:        2 Parity + Blast

checks_run:  command-file row → all four doors + commands/INDEX.md (INDEX row found carrying retired vocabulary, plan omits it) · command-name row → no rename, N/A · SOP/usage-surface row → workflows_testing_SOP.md carries ≥4 board-usage passages the plan's change list does not name · path move/rename row → no moves, N/A · memory row → plan correctly routes memory fallout to the sanctioned flow, no direct edits · port row → single-repo, N/A · twins row → no cicd-/smh- twin of this command exists · sibling worktrees → .claude/worktrees/ empty, no live lanes found (no terminal in this session for `git worktree list`; Lens 2 re-runs as /smh-code-review Step 0.7 regardless) · risk_seam.py → not run (no terminal); pinned law answers for the command centre: `unclassified`, permanently and correctly (SCC-289) — all judgment taken from the files · tests/ and _routing-canary/ swept for adviser/triad/caucus vocabulary → zero hits
read:        same set as Lens 1 plus tests/ sweep and_routing-canary/ sweep
verdict:     findings below

## lens:        3 Pre-Mortem

checks_run:  attached failure narratives only — stale-door (SCC-331's actual failure) → attached to F6; stale-SOP-rejects-the-commit → attached to F3; stale-pointer-teaches-retired-vocabulary → attached to F4; session-boots-with-no-acceptance-list → attached to F2; drift-check-consumer-finds-no-block → attached to F1. No unattached narratives survived.
read:        SCC-331 walkthrough (pitfalls section) · sync-agents.ps1 excluded list
verdict:     findings below

---

## Findings

| anchor | literal text read | consequence | severity |
| --- | --- | --- | --- |
| [implementation_plan.md](implementation_plan.md) (full 267-line read) | sections run §1 Goal → §10 Ticket note; no `## Declared Change Set` heading anywhere | **F1** — the block is absent, which is itself a finding: `/smh-code-review`'s drift check depends on absence being loud, and the audit level had to be inferred (heavier default applied, so the level stands). Fix: append the block — EDIT rows for the command body, TEAMS/ROSTER/CARD/SPAWNS/DOCTRINE/THIRD-SIDE, the AG launcher, commands/INDEX.md, the SOP (+changelog), the REFERENCE pointer; NEW: none. | HIGH |
| [implementation_plan.md:261](implementation_plan.md:261) | "Mint the Jira ticket at **implementation start** (this plan precedes it)" | **F2** — Scope Ledger precondition unsatisfiable: no ticket exists, so there are no ≥2 acceptance rows naming concrete observables. The ledger itself ran clean (the plan creates no brand-new artefact — every change is an EDIT/wholesale-rewrite of a file that already has callers), but a plan with no acceptance list gives /smh-code-review nothing to audit against later. Fix: mint the ticket with ≥2 observable acceptance rows **before** `approved`, or write the acceptance list into the plan now. | HIGH |
| [workflows_testing_SOP.md:4161](docs/_scc_sops_prds/workflows_testing_SOP.md:4161) | "casts 3–5 lenses with **three** minds each, picked to collide" (also :101 quick-reference row, :318 mermaid "historical minds in challenge teams", :1603 "### How the adviser board sizes itself, and what the cast gate shows you") | **F3** — the SOP describes the board's usage in at least four passages; the plan's §6 handles this only conditionally ("if … describes") and the §4 change list omits it. The armed `sop_currency.py` will reject the commit unless the SOP is updated in the same commit — and the house convention adds a [workflows_testing_SOP_changelog.md:21](docs/_scc_sops_prds/workflows_testing_SOP_changelog.md:21)-style row (SCC-333/SCC-334 precedent). Fix: name the SOP + changelog in §4 and add an SOP-currency check to §8. | MEDIUM |
| [smh-adviser-board-REFERENCE.md:9](docs/_scc_sops_prds/smh-adviser-board-REFERENCE.md:9) | "Team charters — blind spot owned, when to seat, **when NOT to seat**, pool, default triad" (also :13 "The ~250-word card contract", :14 "The six spawn templates", :26 "build a triad on two independent axes") | **F4** — the board's own POINTER doc in the SOP set teaches the retired vocabulary and is not named anywhere in the plan (§6 out-of-scope excepts only workflows_testing_SOP.md). Pre-mortem: every future session that opens the pointer learns the dead triad/card model. Fix: add it to the change list — it is a pointer, so the fix is table-row updates plus the history note. | MEDIUM |
| [INDEX.md:61](.agents/commands/INDEX.md:61) | "43 historical minds across 5 debate lenses + 2 stage rooms (Execution Reality, Sales). Recon grounds it in a named project; an orchestrator casts 3 minds per lens chosen to collide … one ~250-word card" | **F5** — the commands/INDEX.md row carries the full retired model; Lens 2's command-file row explicitly demands the INDEX check and the plan omits it. Fix: rewrite the row (filters, one mind per filter, four rounds) in the same lane. | MEDIUM |
| [smh-adviser-board.md:8](.agents/workflows/smh-adviser-board.md:8) | "the third-side discipline, team charters, 43-mind roster, operator doctrine, card contract and spawn templates" | **F6** — the hand-authored Antigravity launcher's *body* carries retired vocabulary, but §8.2's grep gate scopes only the command body + `adviser-board/` folder, so the residue ships invisible. The launcher is hand-owned and prune-protected ([sync-agents.ps1:572](.agents/scripts/sync-agents.ps1:572) `$excluded = @('smh-adviser-board.md', 'INDEX.md')`) — sync will never fix it. Plan §5.2 covers its description budget but not its body. Fix: extend the §8.2 grep gate to `.agents/workflows/smh-adviser-board.md` and edit the body by hand in the lane. | LOW |
| [adviser-board-roster-is-product-shaped.md:24](_artifacts/_memory/adviser-board-roster-is-product-shaped.md:24) | "on a non-product topic, seat **2–3 lenses** and name which are observing" | **F7** — the plan's memory-fallout note (§3.9) flags only the caucus memory; this memory's *mechanics* (seat 2–3 lenses) also go obsolete under filters, though its core (charters are product-shaped; borrowed-analogy failure) survives. Fix: flag it alongside the caucus memory for the sanctioned flow — the plan's "do NOT edit memory files in this task" stance is correct and unchanged. | LOW |

No corroboration pairs — every finding has a distinct anchor (dedupe key is the shared anchor; none shared).

### Observations (uncounted)

- Plan §5.1 says sync regenerates "the `.claude/skills/` launcher" — the generated master is [.agents/skills/smh-adviser-board/SKILL.md], which embeds the command frontmatter description verbatim ([.claude/skills/smh-adviser-board/SKILL.md:3]) and is tree-copied to `.claude/skills/`. Sync handles both; wording only.
- Plan §4.1's frontmatter row says "if a workflow mirror description is derived from it" — it is not derived; the AG launcher is hand-authored ([sync-agents.ps1:563]). §5.2 already states this correctly ("hand-owned means fix it by hand").
- [INDEX.md:108](docs/_scc_sops_prds/INDEX.md:108) describes the REFERENCE pointer — rides with F4's fix.
- `docs/doc-graph.md` / `doc-graph.json` reference board paths — generated maps, refresh on the next map run; never hand-edited.
- Tests and the routing canary are clean of board vocabulary — no enforcement script or test breaks.
- SCC-331's walkthrough confirms both door pitfalls the plan cites (stale generated door caught only by CI; hand-authored door no gate covered) and the late-close-out pitfall §10 already guards against.

### Sibling landing-order dependency

None found — `.claude/worktrees/` is empty and no other lane's declared set overlaps this plan's files. Re-checked automatically as /smh-code-review Step 0.7.

---

## Audit verdict: GO *(flipped 2026-08-28 — amendments applied)*

~~NO-GO~~ → **GO**. The plan was amended per this audit's stated path to GO (plan file only — no
source files touched, no implementation started):

1. **F1** — `## Declared Change Set` appended to [implementation_plan.md](implementation_plan.md)
   (15-row table: 7 command/folder files, `minds/` explicitly UNCHANGED, 2 regenerated doors, the AG
   launcher, SOP + changelog, REFERENCE pointer, commands/INDEX.md row; session-brief path unchanged;
   F7 memory flags noted as close-out scope).
2. **F2** — `## Acceptance` block added with five observable rows (a–e): Round-0 cast menu, four
   visible rounds, vocabulary grep gate, door parity, enforcement suite.
3. **F3–F7** — baked inline as `⚠️ AUDIT FINDING` markers: F3 unconditional SOP currency (§6 + §4.10),
   F4 REFERENCE doc in the change set (§4.10), F5 INDEX row (§4.10), F6 AG launcher body + extended
   grep gate (§5.2 + §8.2), F7 second memory flag (§3.9 + Declared Change Set).
4. §8 verification now maps to the acceptance rows; a `## Self-Audit` note records the
   NO-GO → amendments → GO path and points back to this file.

Per the audit's own statement — "Once F1 and F2 are in the plan, this audit does not need to re-run —
flip the verdict to GO" — the verdict stands flipped. Original NO-GO record preserved below.

---

### Original verdict record (2026-08-28, pre-amendment): NO-GO

NO-GO on the command's two named grounds, both mechanical and both fixable before approval in one editing pass:

1. **F1** — append the `## Declared Change Set` block (the consumers depend on its presence).
2. **F2** — satisfy the Scope Ledger precondition: mint the ticket with ≥2 observable acceptance rows, or write the acceptance list into the plan.

Nothing substantive failed: every path, section claim, and contract-file claim in the plan verified against the live tree, the door-sync and close-out sequencing matches SCC-331's measured scars, and F3–F7 are GO-riding findings to bake into the plan inline (`⚠️ AUDIT FINDING` markers in §4/§5/§6/§8) so the builder reads them in context. Once F1 and F2 are in the plan, this audit does not need to re-run — flip the verdict to GO.
