# SCC-439 — retire the vendor token-size gate in `bmad-quick-dev`

**Ticket:** SCC-439 (Task) · **Branch:** `chore/SCC-439-retire-bmad-token-gate`
**Repo:** `Sudo_Hatter_Command` (the lobby) · **Date:** 2026-09-10 · **review-runtime:** fan-out

## What this is

Delete BMAD's 900–1600 token spec-size guideline and the Split/Keep halt it drives. It is a vendor
default, not house law, and the halt is an approval stop with no value. Operator ruling, 2026-09-10.

**Keep** the single-goal scope test at `step-01-clarify-and-route.md` step 4 — a different halt, on a
real product question. Only the **token count** halt at `step-02-plan.md` step 6 goes.

## The six edits

Two lobby copies carry the text — `.claude/skills/bmad-quick-dev/` (Claude's door) and
`.agent/skills/bmad-quick-dev/` (Antigravity's). Three sites each:

- `SKILL.md` § SCOPE STANDARD — drop the `900–1600 tokens` bullet, keep the single-goal paragraph
- `step-02-plan.md` — delete item 6 whole, and the token clause in CHECKPOINT 1
- `spec-template.md:9` — cut the token sentence. **Line 9 is the `<!--` opener** — preserve it, or
  the rest of the comment leaks into every spec as visible prose

Plus the durable half: a `persistent_facts` entry in `_bmad/custom/bmad-quick-dev.toml`, which
survives a BMAD update (the skill dir is replaced on every one; `_bmad/custom/` is not).

## Acceptance

| # | Statement | Check |
|---|---|---|
| A | The override toml carries the retirement fact | test block `override-fact` |
| B | Neither lobby copy contains `1600`, `900`, or the token halt — and the test proves it read all six files | test block `vendor-copies-stripped` (file-count floor of 6 + a positive control, so an unresolved path reds instead of passing) |
| C | The single-goal test survives in both copies | test block `single-goal-test-survives` |
| D | A regression reds `run_all.py` | new test seen RED then GREEN; file count 83 → 84 |

## Not in this lane

`Projects/` are all git submodules — separate repos whose armed `commit-msg` hooks refuse an `SCC-`
key. The same fact is owed to **AVCH** and **NVS** (`Projects/NEXgen-VR-Director`, key `NVS` not
`NGVR`), each on its own board. Proposed at close-out, not minted here.

`compile-epic-context.md:55` ("800–1500 tokens") is a length hint with no halt — left alone.

## Notes carried from the three-lens audit

The audit ran and returned NO-GO **against an earlier draft of the test**, not against this change.
Four of its findings survive as constraints and are baked in above:

- read every file with `encoding="utf-8"` and match on **ASCII substrings only** — the range
  separator is U+2013, and a cp1252 decode on the Windows side makes an en-dash assertion a
  permanent no-op that still prints `[PASS]`
- `spec-template.md:9` is the comment opener, not a standalone line
- the SOP-currency gate does **not** fire on any path here (`.agents/scripts/tests/` is exempt,
  `.claude/` `_bmad/` `docs/` are outside `_SURFACES`) — the SOP edit stands on content merit
- PR #200 shares `workflows_testing_SOP.md` and should land first; `docs/doc-graph.{json,md}` are
  hook-generated into this commit — on conflict take `origin/main` and re-run `refresh_maps.py`

## Declared Change Set

- NEW `.agents/scripts/tests/test_bmad_token_gate_retired.py` — the guard → A, B, C, D
- EDIT `_bmad/custom/bmad-quick-dev.toml` — the retirement fact → A
- EDIT `.claude/skills/bmad-quick-dev/SKILL.md` — drop the token range → B, C
- EDIT `.claude/skills/bmad-quick-dev/step-02-plan.md` — delete item 6 + the CHECKPOINT clause → B
- EDIT `.claude/skills/bmad-quick-dev/spec-template.md` — cut the token sentence, keep the opener → B
- EDIT `.agent/skills/bmad-quick-dev/SKILL.md` — same, Antigravity's door → B, C
- EDIT `.agent/skills/bmad-quick-dev/step-02-plan.md` — same, Antigravity's door → B
- EDIT `.agent/skills/bmad-quick-dev/spec-template.md` — same, Antigravity's door → B
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — §8 says the fast lane no longer halts on size → D
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one dated `SCC-439` line → D
- EDIT `docs/doc-graph.json` — HOOK-GENERATED, never hand-merged
- EDIT `docs/doc-graph.md` — HOOK-GENERATED, never hand-merged
- NEW `_artifacts/_main/2026-09-10_scc-439-retire-bmad-token-gate/walkthrough.md` — closing record → all
- EDIT `_artifacts/_main/INDEX.md` — the depth-3 row → all
