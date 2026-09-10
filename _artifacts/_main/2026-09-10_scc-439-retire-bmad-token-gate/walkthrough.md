# SCC-439 — retire the vendor token-size gate in `bmad-quick-dev`

**Ticket:** SCC-439 (Task) · **Branch:** `chore/SCC-439-retire-bmad-token-gate`
**Repo:** `Sudo_Hatter_Command` (the lobby) · **Date:** 2026-09-10 · **review-runtime:** fan-out
**Plan:** [implementation_plan.md](implementation_plan.md)

## What changed

BMAD's quick-dev workflow no longer stops to ask about spec size. The vendor 900–1600 token
guideline and the `[S] Split / [K] Keep` halt that `step-02-plan.md` step 6 drove from it are gone
from both lobby doors and retired in the house override, which a BMAD update cannot replace.

The scope test that stays is step-01's single-goal check — two or more independently shippable
deliverables — because that halt asks a product question the operator owns. Only the token halt went.

## Task Checklist

- [x] Guard written and seen RED first (7 failing cases on the real defect)
- [x] Retirement fact added to `_bmad/custom/bmad-quick-dev.toml` (the durable half)
- [x] Token guideline stripped from `.claude/skills/bmad-quick-dev/` (3 sites)
- [x] Token guideline stripped from `.agent/skills/bmad-quick-dev/` (3 sites — Antigravity's door,
      which the ticket did not name)
- [x] Single-goal scope test verified intact in both copies
- [x] SOP §8 + changelog updated in the same commit
- [ ] Follow-ups proposed for AVCH and NVS (separate repos — see `## Your Actions`)

## Evidence

| AC | Statement | Evidence |
|---|---|---|
| A | The override carries the retirement fact | block `override-fact` — 4/4 green; `tomllib` parses, `persistent_facts` 5 → 6 |
| B | Neither lobby copy carries the token gate, and the check proves it read all six files | block `vendor-copies-stripped` — 6/6 green: file-count floor `read 6 of 6`, positive control present in both `SKILL.md`, then zero hits for `1600`, `900`, `Token count check`, `token count` |
| C | The single-goal test survives in both copies | block `single-goal-test-survives` — 4/4 green |
| D | A regression reds `run_all.py` | new guard RED **9/16** before the edits → GREEN **16/16** after; suite file count 83 → 84 |

**RED (before any edit):**

```
-- 9/16 passed --
FAILED: override retires the token-size guideline, override forbids counting or showing a token
count, override names the single-goal test as the only scope judgement, no vendor copy carries
'1600', no vendor copy carries '900', no vendor copy carries 'Token count check', no vendor copy
carries 'token count'
```

**GREEN (after):**

```
-- 16/16 passed --
```

Full suite: see `gates/suite.json` and the totals pasted below.

## The three things that would have gone wrong

Recorded because each was measured, not reasoned, and each is invisible at the call site.

**`spec-template.md:9` is the `<!--` opener.** Deleting the line as a line — the obvious reading of
"remove the token target" — orphans the comment block, and `IMPORTANT: Remove all HTML comments when
filling this template` becomes visible prose in the header of every spec quick-dev writes, on both
doors. The edit cuts the sentence and keeps the opener.

**The range separator is U+2013, not a hyphen.** An assertion written on the literal `900–1600` is a
real check on the WSL side and a permanent no-op on the Windows side, where `read_text()` with no
`encoding=` decodes cp1252 and the match silently fails — and **both machines print `[PASS]`**. Every
read in the guard passes `encoding="utf-8"` and every banned term is ASCII.

**A negative assertion over an unresolved path is trivially true.** "No file contains `1600`" passes
over zero files, so a moved or missing skill directory would have reported the gate retired while it
sat on disk armed. The block counts its files against a floor of six and checks a string the edit
*keeps* before it asserts any absence.

## Scope — what this lane deliberately did not do

`Projects/` are all git submodules: separate repos whose armed `commit-msg` hooks refuse an `SCC-`
key, so the same fact cannot be committed there from this branch. Both maintained projects do carry
the guideline and are owed the change:

- **AVCH** (`Projects/AGY_AVIATIONCHAT`) — `_bmad/custom/bmad-quick-dev.toml` + `.agent/skills/bmad-quick-dev/`,
  3 sites, byte-identical to the lobby's, so it ports verbatim.
- **NVS** (`Projects/NEXgen-VR-Director`, key `NVS` not `NGVR`) — the same two, **plus a fourth site
  the lobby does not have**: `_bmad/bmm/4-implementation/bmad-quick-dev/step-02-plan.md`, where the
  token check is item **5** and CHECKPOINT 1 carries its own `[A]/[E]` halt. Not a copy-paste.

The ticket's proposed "fail if any skill copy on disk contains 1600" test was **not** built: it
matches 13 directories across 7 submodules including `Projects/sudo-command-center`, the published
teaching edition — the SCC-399 trap, where an assertion's only fix is deleting files out of a shipped
product. The guard is scoped to the two lobby copies and pins that scope with its own case.

`compile-epic-context.md:55` ("800–1500 tokens") is a length hint with no halt attached — out of
scope, and unreachable by the guard.

## Landing order

`docs/_scc_sops_prds/workflows_testing_SOP.md` is shared with **PR #200** (`chore/SCC-186`), which is
older and not a draft — **it should land first**; this §8 paragraph rebases onto it cleanly.
`_artifacts/_main/INDEX.md` is append-only across three lanes (#205, #193, this). `docs/doc-graph.json`
and `docs/doc-graph.md` are written into this commit by the pre-commit maps delegate — on a conflict,
take `origin/main`'s copy wholesale and re-run `refresh_maps.py`; never hand-merge them.

## Your Actions

1. **Merge the PR** once its checks are green — `main` is yours, not an agent's.
2. **Say go on the two follow-ups**, or place them yourself: the retirement fact is owed to AVCH and
   to NVS, each on its own board. Nothing has been written to either.
