---
ArtifactMetadata:
  mobile: true
---

# 📱 Walkthrough — de-clutter the operator SOP

**TL;DR:** the SOP now states the current system in present tense; every "⭐ what changed / since
SCC-x / renamed from" passage was rewritten in place or deleted; the change story lives in the new
sibling `workflows_testing_SOP_changelog.md` (one line per change, 70+ entries harvested); and
`sop-currency.md` gained habit 4, so gate-driven updates must keep this shape. Executed on the
operator's tap-approval of the plan (all three recommended options chosen: execute · sibling
changelog · atlas stays in-page).

## Task Checklist

- [x] Writing contract: `sop-currency.md` §Writing the update habit 4 + SOP header contract block
- [x] Changelog home: `workflows_testing_SOP_changelog.md` + `INDEX.md` row + `EXPECTED` in `test_sops_prds_folder.py` (three-edit manifest contract; 12→13 docs, docstring + INDEX counts updated)
- [x] Spine rewrite, Parts front-matter through VII — one commit per pass
- [x] Aside audit: change-narration asides deleted or converted; incident lessons kept (the designed review surface — Part IV's check table and "incident history behind the checks" retain their ticket citations deliberately)
- [x] Verification (below)
- [x] The merge itself — lands via this branch's PR (#43)

## Evidence

Measured before → after on `workflows_testing_SOP.md`:

| Pattern | Before | After |
|---|---|---|
| `⭐` markers | 91 | 23 — all step-emphasis inside mermaid diagrams; 0 in prose |
| "what changed / since SCC-x" body passages | ~40 | 0 |
| `SCC-nnn` refs | 167 | ~81 — now confined to why-asides, the Part IV incident archive, and functional keys (`SCC-186` standing ticket) |
| Full dates | 69 | 19 — currency stamps, functional cutoffs (e.g. the 2026-08-15/20 roster scopes), and incident dates in asides |
| "no longer" / "used to / previously / renamed" | 59 | 17 — all inside why-asides or legitimate semantics ("a tree that no longer exists") |

Gates (this container; T9 fails identically on the untouched tree — uncloned project submodules):

```
test_sops_prds_folder.py  -- 60/61 passed -- (T9 pre-existing environmental)
workflow_lint --toolkit-only  -- 0 error(s), 0 warning(s), 8 info --
in-page anchors: 122/122 resolve (all internal links checked after heading cleanups)
```

Deviations from the plan: file-size reduction is ~4%, not the estimated ~40% — the bulk of the page
is the 45-diagram atlas and the Part IV incident archive, both ruled keep-in-place (atlas by your
tap; the archive is the doc's designed review surface). Every rule survived; nothing was deleted
except narration and two retired-thing notes (`/sudo-update-scrum-board` retirement aside,
`autopilot_mobile` deletion note) whose facts moved to the changelog.

## Your Actions

- [ ] Merge PR #43 (draft — mark ready and click *Merge pull request* when satisfied)
