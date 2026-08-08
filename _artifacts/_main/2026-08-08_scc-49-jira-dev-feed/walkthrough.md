---
type: walkthrough
story: SCC-49
date: 2026-08-08
branch: chore/SCC-49-jira-dev-feed
---

# SCC-49 — Feed dev knowledge back into the Jira ticket

The board could tell you a story existed. It could never tell you what the story was about, or what
building it taught. ① minted with `--summary` and nothing else, and close-out posted one verdict line —
so the outline, the decisions, the pitfalls and the still-owed all died in the walkthrough. This puts
them on the ticket, and makes it impossible to skip quietly.

## Task Checklist

- [x] **Read the ticket and ground it in the code.** Confirmed both halves were genuinely absent, not
      just thin: no `--description` anywhere in ① Step 1.6, one line in close-out Step 4.5.
- [x] **`.agents/scripts/jira_feed.py`** — four verbs: `outline` · `mint` · `devrecord` · `check`.
  - Both write verbs **read the ticket back** and exit 2 if what they claimed to write is not there.
    An `acli` call that exits 0 while recording nothing is indistinguishable from one that worked.
  - `acli --json` returns an **array** on `search` and an **object** on `view` / `comment list`; a
    parser accepting one shape reads a good response as a failure. Both shapes handled.
  - Descriptions and comments come back as **ADF**, never plain text, so every read-back flattens it.
  - *Found while testing:* `relative_to()` raises when a path handed in with `--walkthrough` resolves
    differently from the project root (macOS `/tmp` → `/private/tmp`, or any symlinked worktree). It
    killed the whole evidence section with a traceback. Now routed through `rel_to()`, which falls back
    to the absolute path.
  - *Found while wiring quick-dev:* `wf.resolve_project_root` **dies without a sprint board**, and the
    command centre deliberately has none — so the one repo where the workflow itself is built was the
    one repo whose tickets could never carry a record. `devrecord` now resolves leniently.
- [x] **① `/sudo-write-story-tests` Step 1.6** — the dedupe search and the mint collapse into one
      `jira_feed.py mint` call. The lane / parallel / blocked ruling stays the agent's judgment.
- [x] **Close-out Step 4.5** — rewritten from "transition + one line" to transition, **file the Dev
      Record**, verify. Content comes from Step 3's routing as `--decision` / `--pitfall` /
      `--followon`; the walkthrough scrape is only a safety net beneath it.
- [x] **`/sudo-create-epic-sprint` Step 1.5** — epic mint now renders its outline from `epics.md`.
- [x] **`/sudo-quick-dev` Step 4.5 (new)** — it closes its own branch, so it files its own record.
      **Exactly one Dev Record per ticket:** an existing record is *updated in place*, never stacked,
      so the branch-closer and a later story close-out cannot leave two partial records.
- [x] **Work-item type derived from the STORY FILE, not the parent** (operator ruling; corrected on
      the third pass after reading the real AVCH board). *Everything* is parented, and a BMAD epic
      (`Epic 19 — …`) is indistinguishable in Jira from one of the operator's grouping epics
      (`CI/CD Improvment`, `New Epic Feature or Fix`) — so keying off the parent, as the first cut did,
      types every chore Task as a Story. The discriminator is whether a file in `_bmad/bmm/stories/`
      backs the ticket. `--type` overrides; a Story with no `--epic-key` warns.
- [x] **The split lane, closed.** SCC-40 landed on `main` mid-session, so `main` was absorbed here.
      The merge auto-resolved and **placed Step 3.5 after Step 4** — the silent misplacement predicted
      in the first pass. Renumbered to **Step 4.5**, which is where it belonged anyway: it points at the
      walkthrough Step 4 writes, and it now mirrors close-out's own Step 4.5.
- [x] **Bare `python` swept** — 18 call sites across 5 files (`sudo-code-review`, its `_AP` twin,
      `sudo-update-sprint-memory` ×3, `sudo-close-workingtree`, `update-maps-indexes` ×12). The Mac has
      no bare `python` at all, so every one of those was broken on this machine.
      `rules/sop-currency.md` keeps its bare `python` — it *quotes* the bug as the example.
- [x] **A silently-disarmed gate, found by the sweep.** Fixing the docs' `python` surfaced the same bug
      one layer down: `pre-commit-encoding.sh` probed `python || python3`, **never tried `py`**, and on
      a box with only the Windows launcher the whole substitution failed so the hook `exit 0`'d —
      **armed in name, checking nothing.** VS Code hides hook output, so that would have stayed
      invisible indefinitely. Both it and `.githooks/post-commit` now use the same
      `python3 → python → py` probe as `sop-currency.sh`, and the armed gates *announce* a skip.
- [x] **59 test cases** in this file (183 across the suite), joined to `run_all.py` by auto-discovery.
      The probe guard reads **code only** — the fix's own comment quotes the broken line, and a raw
      grep flagged the fix as the defect on first run. It carries a positive control asserting the
      strip is load-bearing.
- [x] **Docs** — SOP quick-reference §5, `.agents/rules/jira.md`, `.agents/scripts/INDEX.md`.
- [x] `/sync-agents` — mirrors regenerated for opencode, Antigravity, Codex.

## Evidence

| Claim | Proof |
|---|---|
| Full enforcement suite green | `python3 .agents/scripts/tests/run_all.py` → **7/7 files, 183 cases** |
| New file's own cases | `test_jira_feed.py` → **59/59 passed** |
| Outline renders real ACs, invents nothing | `outline --story 12.3.4 --project AGY_AVIATIONCHAT` → all 7 ACs verbatim, story statement, story-file path |
| Epic outline reads `epics.md` | `outline --epic 12` → goal + the 3 child stories, stops before Epic 13 |
| `check` works against the LIVE board | `check --key AVCH-15` → description present (142 chars), **no Dev Record → exit 2** |
| Toolkit lint clean for this change | `workflow_lint.py` → its 1 error is pre-existing AGY epic-19 state, untouched here |

**The load-bearing test cases** (a checker nobody can trust is worse than none):

- acli exits 0 and records nothing → **exit 2, not a false success**
- a second `devrecord` post → **still exactly one record**, carrying the newer content
- a fuzzy `~` search hit on a *child* story (`9.1.2` when minting `9.1`) → **not** treated as a reuse
- a minted ticket whose description never landed → **exit 2**
- positive control: a fully-fed ticket reports clean (`0 error(s)`)

## Your Actions

**Landed** on `chore/SCC-49-jira-dev-feed` (off `main`). Nothing pushed to `main`.

Two things need your call:

1. **The live post to SCC-49 is held.** You said the ticket was being updated, so I did not write to
   it. The command is ready and its dry-run output is in the chat — say go and I'll run it.
2. **The existing board is all `Task`, including the real stories.** New tickets type themselves
   correctly now, but **21 AVCH tickets that ARE stories still read `Task`** — every one whose summary
   starts with a BMAD number: `AVCH-14/15/16`, `24`–`32`, `33`–`36`, `37`, `38`–`40`, `45`. The other
   **10** (`9`–`12`, `21`, `22`, `41`, `44`, `46`, `48`) are correctly `Task` already. Converting is
   `acli jira workitem edit --key <K> --type Story --yes` per ticket — a board migration, so it is
   yours to call. Say the word and I'll script the 21.

**Note for whoever picks this up next:** the shared checkout was flipped to another branch mid-session
by a parallel session (SCC-50), which is why the command bodies briefly appeared to revert. Nothing was
lost — the work was already committed and pushed. In this checkout, verify
`git rev-parse --abbrev-ref HEAD` before trusting what a file says.
