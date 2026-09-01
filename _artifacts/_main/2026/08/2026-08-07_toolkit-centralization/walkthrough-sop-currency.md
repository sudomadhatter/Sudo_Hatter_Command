# Walkthrough — SOP currency gate + two-machine parity (2026-08-08)

Follow-on to the toolkit-centralization epic. Plan section: `implementation_plan.md`
→ "Follow-on Plan — SOP doc currency (2026-08-08)".

## What shipped

**1. The SOP quick-reference is current again.** `_my_resources/_quick_reference/sudo_workflows_testing.md`
had drifted on eight points, the worst being the single line that hands the operator something to type:
`python .agents/scripts/tests/run_all.py — 94 checks`, when the count was 98 (now 123/6 files) and the
Mac has no bare `python`. Also fixed: the two-tier centralization ruling was entirely absent, the
retired `-Maintained` sync fan-out, `/autopilot_mobile` (deleted 08-07) still listed as a live engine,
and `/review` + `/slash_command_updating` undocumented.

**2. An armed gate so it can't drift again** — three seams:
- `.agents/rules/sop-currency.md` — the law + the surface list.
- `.agents/scripts/sop_currency.py` ← `git-hooks/sop-currency.sh` — a commit touching a *usage surface*
  (`commands/*.md` · `rules/*.md` · `scripts/*.py|*.ps1` · `git-hooks/` · `.githooks/` · root `AGENTS.md`)
  is REJECTED unless the SOP doc is staged with it. `[sop-ok]` opts out and stays in the log.
- Restated inline in `/sync-agents` and root `AGENTS.md` §3.

`.githooks/commit-msg` now *calls and checks* the Jira gate rather than `exec`ing it — `exec` replaces
the process, so any second gate would have been dead code.

**3. Two-machine parity.** The `python3` fix was itself a Mac-only claim; a python.org PC has only
`python`. Walked back across 5 files, and the machine differences now live in SOP §7 ("What does NOT
travel between the machines") plus a new `machine_setup_card.md` and a step in the migrations kit.

## Defects found and fixed en route

| # | Defect | How it surfaced |
|---|---|---|
| 1 | `lstrip("./")` in the gate's own path normalizer — lstrip takes a character SET, so it ate the leading dot off every `.agents/` path and the gate matched **nothing** while reporting success (only `AGENTS.md` passed) | the new test file's cases A–D, on first run |
| 2 | An em dash inside `print()` — raises `UnicodeEncodeError` on the PC's cp1252 console, **crashing the hook** and turning "warn-only, commit allowed" into a hard failure with a traceback | auditing my own delivery after the operator flagged the two-machine reality |
| 3 | `workflows/INDEX.md` described `slash_command_updating` as the command-authoring contract (frontmatter, `platforms:`, propagation). It is a thin `/sync-agents -GlobalsOnly` alias, and that contract existed **nowhere** | the operator asked what the command does |
| 4 | The `platforms: []` = NOWHERE trap was undocumented — the exact bug that silently broke `/review` | while fixing #3; now stated in `sync-agents.md` |
| 5 | Duplicate, disagreeing test-count lines in `.agents/scripts/INDEX.md` (mine + an existing one) | pre-merge read-through |
| 6 | `RAG_Pipeline_AC` has `core.hooksPath` unset — harmless today (no `.githooks/` yet), but any gate added later would be silently off | the two-machine audit |

## Evidence

| Gate | Result |
|---|---|
| `python3 .agents/scripts/tests/run_all.py` | **6/6 files, 124/124 checks** (was 5/5, 98) |
| Gate live-fired: surface-only commit | **REJECTED** — HEAD unchanged, staged files untouched (clean no-op) |
| Gate live-fired: `[sop-ok]` in message | allowed |
| Gate live-fired: surface + SOP doc staged | allowed |
| Gate on `.claude`/`.opencode` mirror churn | correctly silent (mirrors are not surfaces) |
| Relative global `core.hooksPath` resolves per-repo | verified in a throwaway two-repo fixture |
| ASCII-only hook output, both modes | test case Y |
| `check_maps.py` (lobby) | clean apart from ledger rows for two other lanes' folders, since reconciled |

## Task Checklist

- [x] Audit the SOP doc against the tree (8 stale points, verified — not from memory)
- [x] Plan appended to the epic plan; STOPPED for approval; operator chose ARMED
- [x] `sop_currency.py` + 26 test cases; `sop-currency.sh`; `SOP-ENFORCE`; commit-msg chain rewired
- [x] `sop-currency.md` + rules INDEX row + `AGENTS.md` §3 pointer
- [x] SOP doc de-staled; `/sync-agents` + `/update-maps-indexes` updated; `platforms: []` trap documented
- [x] Live-fired the gate three ways on real commits
- [x] Two-machine walk-back across 5 files; cp1252 print bug fixed and guarded
- [x] `machine_setup_card.md` + migrations kit step 2b + guide §5
- [x] Memories: `two-machines-mac-and-pc`, `sop-doc-currency-gate`; index compacted 164 → 139 lines
- [x] Landed on `main` and pushed

## Your Actions

1. **Both machines** — arm the gates. Nothing looks wrong if you skip it:
   `git config --global core.hooksPath .githooks`
2. **AGY** — the one push I can't make:
   `git -C Projects/AGY_AVIATIONCHAT merge --ff-only epic/AVCH-23-thin-toolkit` then
   `git -C Projects/AGY_AVIATIONCHAT push origin main`. Say the word and I'll transition AVCH-23,
   watch the deploy, prune the branch, and bump the gitlink.
3. **Optional** — ~20 `.md` lines across the toolkit still say bare `python …`. Correct on the PC,
   broken on the Mac. Say so and I'll sweep them machine-neutral.
