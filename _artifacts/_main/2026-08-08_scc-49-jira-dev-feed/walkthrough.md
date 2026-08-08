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
- [x] **`/sudo-quick-dev` Step 3.5 (new)** — it closes its own branch, so it files its own record.
      **Exactly one Dev Record per ticket:** an existing record is *updated in place*, never stacked,
      so the branch-closer and a later story close-out cannot leave two partial records.
- [x] **45 test cases**, joined to `run_all.py` by auto-discovery.
- [x] **Docs** — SOP quick-reference §5, `.agents/rules/jira.md`, `.agents/scripts/INDEX.md`.
- [x] `/sync-agents` — mirrors regenerated for opencode, Antigravity, Codex.

## Evidence

| Claim | Proof |
|---|---|
| Full enforcement suite green | `python3 .agents/scripts/tests/run_all.py` → **7/7 files, 169 cases** |
| New file's own cases | `test_jira_feed.py` → **45/45 passed** |
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

Three things need your call:

1. **The live post to SCC-49 is held.** You said the ticket was being updated, so I did not write to it.
   The command is ready and its dry-run output is in the chat — say go and I'll run it.
2. **Ticket type.** SCC-49 says "as a **Story** under the epic". Every existing ticket is `Task`
   parented to the Epic, and parenting already works (`AVCH-15`/`AVCH-16` → `AVCH-13`). Changing the
   type scheme is a board decision, so `mint` still uses `--type Task`. Say the word and it is a
   one-word default change.
3. **SCC-40 rewrote `/sudo-quick-dev` on its own unmerged branch.** I added Step 3.5 to the `main`
   version here; the same step must be mirrored onto the SCC-40 branch or the merge will drop it.

**Two pre-existing findings, not fixed here** (they belong to their own tickets):

- `/sudo-update-sprint-memory` Steps 0.6, 4 and 4's gate note invoke bare **`python`**, which does not
  exist on the Mac at all. Those three lines are broken on this machine today.
- `/sudo-quick-dev`'s ad-hoc chore lane still writes no `walkthrough.md` on the `main` version of the
  command (SCC-40 adds one).
