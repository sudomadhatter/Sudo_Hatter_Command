---
name: agy-story-files-canonical-dir
description: "AGY story files live in _bmad/bmm/stories/ (dotted names) — NOT implementation-artifacts/epic-N; tracker docs' \"needs story file\" flags go stale, and the next free story ID comes from sprint-status.yaml, not from the story you're working on. Verify on disk before creating a story."
metadata: 
  node_type: memory
  type: project
  originSessionId: 368aa7c1-d8da-4c4a-a0b7-13c22673ad08
  modified: 2026-07-21T02:51:21.650Z
---

AGY_AVIATIONCHAT's canonical story-file directory is `_bmad/bmm/stories/` (e.g. `story-8.23.2-operator-exam-insights-view.md`; naming mixes dotted `8.23.2` and hyphenated `8-21-1` variants — search BOTH patterns). `_bmad-output/implementation-artifacts/epic-N/` folders exist but only hold OLD epics (1–4, 9, 15); the epic-8 wave never got one.

**Why:** the sprint-dependency-map claimed 8.21.2/8.22.2/8.23.2 "need story files" when all three had existed since 2026-06-21 (fixed 2026-07-04) — acting on it would have created duplicate stories via /sudo-write-story-tests. Same failure family as [[recon-reframes-story-scope]]: tracker verdicts can be search-term/staleness artifacts.

**ID collision (2026-07-20).** A GAP story filed mid-review as `debug-1.6` collided with an existing
`.6` (coleman-session-durability) that was on the board but had no reason to surface while reviewing `.5`.
Two `story-debug-1.6-*.md` files coexisted for a day; caught at close-out and renumbered to `.8`.
**The next free ID comes from `sprint-status.yaml`'s epic block — the authoritative list — not from
incrementing the story you happen to be working on**, because backlog siblings are already numbered ahead
of you. `ls` the stories dir too: a filename collision and a board collision are different failures and
either one alone is a false all-clear.

**Debug epics are numbered by ROUND, not dated (renamed 2026-07-20).** The old `debug_7-18-26` scheme is
gone — every story/key/path moved to `debug-1`: story files `story-debug-1.N-slug.md`, sprint keys
`debug-1-N-slug`, epic key `epic-debug-1`, artifacts `_artifacts/epic_debug_1/`. **Round 1 = the 2026-07-19
live-testing session.** The next live-testing wave opens as `epic-debug-2` with `debug-2.1`, `debug-2.2`, …
— increment the ROUND, never mint a new date-stamped id. Scheme is documented in
`_artifacts/epic_debug_1/README.md` and the `sprint-status.yaml` epic block.

**Separator rule — HYPHEN in ids, underscore ONLY in the artifacts dir.** Canonical is `debug-1.N`
(prose/tables/story files) and `debug-1-N-slug` (sprint keys). `debug_1.N` with an underscore is WRONG
and reads as a different epic to other agents; the single underscore form that IS correct is the artifacts
directory `_artifacts/epic_debug_1/` (matches the `epic_15/`, `epic_19/` convention). Two bad forms have
each been mass-written into `_my_resources/_quick_reference/sprint-dependency-map.md` and had to be
reverted: a bare `debug.N` shorthand (predates the rename — commit `982ee112` renumbered every other record
and left this doc's 27 shorthand rows untouched) and a later `debug_1.N` "fix" that used the wrong
separator. Repaired 2026-07-20.

**GAP stories filed by a ③ review bypass ① — expect an odd status and missing sections.** When
`/sudo-code-review` files a gap, it hand-writes the story file directly instead of running
`/sudo-write-story-tests`. The result looks half-finished but isn't damaged: rich Why/ACs, but **no Tasks,
Dev Notes, Testing, Dev Agent Record, or Change Log**, and an off-vocabulary status (`debug-1.8` landed as
`Status: draft`, which no tool understands). **Before "fixing" such a status, check whether implementation
actually exists** — artifacts dir, test file, code. For `debug-1.8` none did, so `backlog` was right and ①
is still owed; a status that merely *looks* wrong can equally mean real work happened outside the flow.
Record the provenance in the story body so the next reader doesn't re-investigate.

**How to apply:** before creating any AGY story, `ls _bmad/bmm/stories/ | grep` both `N.N.N` and `N-N-N` forms,
AND grep the epic's block in `sprint-status.yaml` for every taken ID. An existing story + no test ⇒ the remaining step ① work is only the ATDD red half (/bmad-testarch-atdd), then straight to /sudo-dev-story-tests.
