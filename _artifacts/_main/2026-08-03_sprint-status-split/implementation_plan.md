---
IsArtifact: true
ArtifactMetadata:
  title: "Implementation Plan — Wave 4: split state from narrative in sprint-status.yaml"
  type: implementation_plan
  date: 2026-08-03
---

<!-- wf-lint: allow-encoding-literals — §5 quotes a cp1252 digraph as an EXAMPLE of what the console
     fakes. Without this declaration the Wave 5 pre-commit gate blocks every commit touching this
     plan, which is the same trap `wf_common.py` and `test_workflow_lint.py` already carry. -->

# Wave 4 — Split state from narrative (`sprint-status.yaml`)

> Wave 4 of `_artifacts/_main/2026-08-02_workflow-infrastructure-upgrade/implementation_plan.md`.
> Waves 1, 2, 3 and 5 are done. This is the last wave, deliberately placed last because it is the
> only irreversible one and because Waves 1/3 built the harness that proves it broke nothing.
>
> **Governing principle, unchanged:** *an instruction may only be deleted after a script enforces it.*
> Applied here it has a second edge — **a byte may only be moved after a script can put it back.**

---

## 1. The parent plan's premise was wrong — measured 2026-08-03

The parent plan says: *"its 541 comment lines and 47 multi-kilobyte rows move to history."* That
describes about a third of the file. Full byte census of the live file today:

| Class | lines | bytes | % | Disposition |
|---|---|---|---|---|
| **trailing `#` note on a key line** | 218 | **228,577** | **62 %** | → per-story history |
| **CHANGE LOG block** (lines 67–118) | 52 | **~76,000** | **21 %** | → `history/CHANGELOG.md` |
| free comment inside `development_status` | 347 | 34,651 | 9 % | mixed — triage, see §3 |
| epic banner (`# ═══` / `# Epic N:` / `# STATUS:`) | 98 | 11,458 | 3 % | **stays** (navigation) |
| **`key: status` — the actual state** | 261 | **9,721** | **2.7 %** | **stays** |
| header / status doctrine (lines 1–66) | 66 | 4,822 | 1.3 % | stays |
| `action_items:` | 14 | 721 | 0.2 % | stays |
| blank | 34 | 34 | — | stays |

> ⚠️ **AUDIT FINDING (F1/F8)** — every byte figure in this table is the **LF stream** (the git blob).
> The working-tree file is CRLF and therefore 872 bytes larger: **364,206 B on disk / 363,334 B in
> git.** Percentages are unaffected. See §5, which is now anchored to the blob.

**363,334 bytes total; 9,721 of them are state.** The narrative is not mostly in standalone comment
lines — it is *trailing each key line*, which is the one line every writer in the system edits. That
is a different and more dangerous operation than the parent plan assumed, and it is why this wave
gets its own plan instead of the four paragraphs it had.

### The measurement that de-risks the whole thing

Of the 218 rows carrying a trailing note:

| | total rows | rows carrying a note | note bytes |
|---|---|---|---|
| **terminal** (`done` 218 · `optional` 13 · `descoped` 2 · `deferred-v3` 2) | 235 | **199** | **219,193** |
| **active** (`deferred` 21 · `review` 2 · `in-progress` 2 · `ready-for-dev` 1) | 26 | **19** | 6,017 |

> ⚠️ **AUDIT FINDING (F3)** — "terminal" above is **not** `wf_common.TERMINAL`, which is only
> `{done, descoped}`. The disagreement is `optional` + `deferred-v3` = **15 rows, 215 note bytes**.
> Small in bytes, fatal in logic: `--terminal-only` would strip rows the new lint check calls live.
> **One set, defined once in `wf_common` and imported by both** — see §4.1 and §6.

**96 % of the bytes being moved belong to rows that are already terminal** — rows no command will
write again. Only 5 rows are genuinely in flight. The "concurrent writer races the migration"
scenario, which is the risk that makes this wave HIGH, applies to a handful of lines and can be
excluded from the first pass entirely. §4 is built around that.

### Two other facts the plan did not have

- **The file is CRLF, no BOM, trailing newline present** (872 CRLF / 872 LF). Any tool that reads it
  in Python text mode and writes it back silently converts to LF and the "byte-for-byte" guarantee is
  a lie that still passes a line-by-line diff. **Binary I/O is mandatory**, not a preference.
- **It grew 348 KB → 363 KB between 2026-08-02 and 2026-08-03** — one day, ~15 KB. 296 commits have
  touched it. A one-time split with no standing enforcement is undone inside a quarter; §6 is
  therefore not optional polish, it is half the deliverable.

---

## 2. Target shape

```
_bmad-output/implementation-artifacts/sprint-status.yaml     ~24–29 KB   state + navigation
_bmad-output/implementation-artifacts/sprint-status.yaml.pre-split       verbatim rollback copy
_bmad-output/history/CHANGELOG.md                            ~76 KB      52 entries, newest first
_bmad-output/history/epic-21/21-8b-demo-data-quarantine.md   per-story narrative
_bmad-output/history/migration-manifest.json                 every moved byte range → destination
```

**Projected board size, from the census above:** 9,721 (keys) + 11,458 (banners) + 4,822 (header)
+ 721 (action items) + ≤2,280 (active notes at the cap) ≈ **29 KB**, ~24 KB if the epic banners are
compressed from three lines to one. The parent plan's "~25 KB" is right, but by different arithmetic
than it stated. **It is under the Read tool's limit, which is the point** — the file becomes readable
again by the agents that depend on it.

The retained inline note is capped at **120 chars and permitted only on non-terminal rows**. A
terminal row's story is in history and in the story's own walkthrough; repeating it on the board is
what produced a 16,343-character line. `/sudo-prune-context` already declares this routing —
*"`sprint-status.yaml` story line → per-story ledger + dated history log"* — so the destination is
existing doctrine, not a new invention.

---

## 3. Consumer map — who actually breaks

50 files in the toolkit mention `sprint-status`. Most are prose references that need no change. The
ones that do split into two classes, and they fail in **opposite** ways:

**Writers — break loudly if the line format changes.** Each does a line-oriented regex edit:

| Consumer | What it writes |
|---|---|
| `story_status.py set` | atomic dual write; already `^  key: status(.*)$`, note preserved |
| `sudo-update-sprint-memory` | story line + a CHANGE LOG entry (Step ~143) |
| `sudo-merge-epic-workingtrees` | per-story flip + CHANGE-LOG entry (Step ~93) |
| `sudo-create-epic-sprint` | appends new keys as `backlog` (Step ~43) |
| `autopilot-dev-story.ps1` + `-opencode.ps1` (**AGY-local, two diverged copies**) | `ready-for-dev\|in-progress → review`, comment preserved |
| `sudo-park` | conflict resolution on the board |

All six preserve the trailing text rather than parsing it, so **none breaks on the split itself**.
Two need a follow-up edit anyway: `sudo-update-sprint-memory` and `sudo-merge-epic-workingtrees`
write CHANGE-LOG entries into a block that will no longer be in this file.

**Narrative readers — break silently, which is worse.** They read the trailing note for "what
happened on this story." After the split they find a bare status, report less, and nothing errors:

| Consumer | Today |
|---|---|
| `sudo-boot-sprint-memory` | *"grep the epic blocks"* — the session-boot summary comes from these notes |
| `sudo-update-scrum-board` | *"the **master**. Dump `development_status`"* — the board's source of truth |
| `sudo-resume` | reads status + context for the resume report |
| `sudo-close-workingtree` | corroborates `done` from the key (state only — safe) |

⚠️ `sudo-resume.md`, `sudo-boot-sprint-memory.md` and `sudo-update-scrum-board.md` are **in flight in
another session** at the time of writing. Wave 4 must not edit them under that session; §4 Phase 4.5
either waits for those to land or coordinates explicitly. This is a real sequencing constraint, not a
courtesy.

> ⚠️ **AUDIT FINDING (F9) — a whole consumer surface was missing from this section.** AGY carries
> **two** toolkit trees: `.agents/` (the synced lobby toolkit, mapped above) and **`.agent/`
> (singular) — the vendored BMAD skills**, ~20 more files that reference this board. My first sweep
> was a `head_limit`-truncated result I read as a complete inventory. The additions:
>
> | Consumer | Role | Impact |
> |---|---|---|
> | `.agent/skills/bmad-quick-dev/sync-sprint-status.md` | **a 7th writer** — *"Load the FULL file"*, edits the key, *"Save preserving ALL comments"* | Loading the full file is **impossible today** at 364 KB — an argument *for* the split, not against |
> | `.agent/skills/bmad-sprint-status/SKILL.md` | validates the status vocabulary, checks freshness, offers "show raw sprint-status.yaml" | See the `last_updated` break below |
> | `.agent/skills/bmad-sprint-planning/sprint-status-template.yaml` | defines the canonical shape for a newly generated board | **Carries no trailing-note convention** — it is *already* the lean shape this wave targets |
> | `bmad-create-story` · `bmad-dev-story` · `bmad-retrospective` · `bmad-code-review` steps | read status | state only — safe |
>
> **The template finding cuts the other way and is worth stating plainly:** the split moves AGY
> *toward* BMAD's canonical shape, not away from it. The house rule *"fix the rule, not BMAD
> internals"* is not in tension here — no BMAD internal needs editing.
>
> ⛔ **But one concrete break:** `bmad-sprint-status` warns "may be stale" from `last_updated`,
> falling back to `generated`. AGY has **no `last_updated` key** — it is a *comment* at line 66,
> sitting directly above the CHANGE LOG block, and line 2 redirects readers to that block. §4.4 moves
> that block to history and takes the date with it, leaving only `generated: 2026-03-07`. **Fix:
> promote `last_updated` to a real key in the retained header**, as the template already has it
> (`sprint-status-template.yaml:44`). ~30 bytes, repairs a pre-existing latent defect instead of
> making it permanent.

**Non-consumers, verified clear:** `scripts/git-hooks/board-stale-stamp.sh` diffs the board between
the last reconcile commit and HEAD. ~~The migration commit is a whole-file rewrite, so the stamp will
fire once, loudly.~~ ⚠️ **AUDIT FINDING (F5) — checked and false.** Line 55 strips the trailing
comment *before* comparing values, and line 10 states the intent outright: *"comment-only edits
ignored."* A note-only rewrite yields `old[k] == new[k]`, the drift file comes out empty, and the
hook exits 0 at line 67 without stamping. **No action needed** — the original claim overstated the
risk and is retracted.

---

## 4. Phases

Ordered so that every irreversible step happens **after** a reversible one has proven the machinery.

### 4.0 — Freeze and snapshot (no edits)
- Confirm the board is clean and pushed in AGY; confirm no story is mid-`②`/`③` writing to it.
- `git rev-parse HEAD` recorded in the manifest as `source_sha` — the reconstruction is only
  meaningful against a named commit.
- Copy the file to `sprint-status.yaml.pre-split` and commit it *before* anything is moved. Rollback
  must exist in git history before the risk is taken.
- Capture the pre-migration output of all four Wave-1 tools to files — §8 item 4 diffs against them,
  and "identical to before" is worthless if *before* was never written down.

> ⚠️ **AUDIT FINDING (F1)** — `.gitattributes` sets `* text=auto` and `core.autocrlf=true`, so a
> "verbatim binary copy" is **not** what git stores: the blob is LF-normalised (verified — worktree
> 364,206 B / blob 363,334 B). Off a machine with `autocrlf=true` the restore comes back LF and the
> rollback is silently 872 bytes different. **Fix:** add `*.pre-split -text` to `.gitattributes` so
> git stores it untouched, **and** treat `git show <source_sha>:<path>` as the real baseline (§5) —
> a pinned blob cannot be re-normalised by anything.

### 4.1 — Build `split_sprint_status.py` (no migration yet)
Stdlib-only, binary I/O, line-oriented. Lives in `.agents/scripts/` beside the Wave 1 tools and
imports `wf_common` for `BOARD_REL`, `_KEY_RE`, `parse_board` — **it must use the same parser the
enforcement scripts use**, or the split and the linter can disagree about what a key line is.

```
split_sprint_status.py plan   --project P            # dry run: classify every line, print the census
                                                     # + the projected post-split size. Writes nothing.
split_sprint_status.py apply  --project P [--terminal-only]
                                                     # performs the move, writes migration-manifest.json
split_sprint_status.py verify --project P --sha <source_sha>
                                                     # reconstructs the ORIGINAL from
                                                     # (new board + history files + manifest) and
                                                     # compares BYTES against `git show <sha>:<path>`.
                                                     # Exit 1 on any difference, naming the first
                                                     # differing offset.
```

**The manifest is the contract.** For every moved span: source line number, source byte offset,
byte length, destination path, destination anchor. `verify` walks it in source order and rebuilds
the file; it is not a heuristic re-merge.

> ⚠️ **AUDIT FINDING (F4)** — `--sha` is **required, not optional.** Without it `verify` reconstructs
> whatever is in the tree *now*, so a close-out landing between `apply` and `verify` makes an honest
> migration read as corrupt. This is the exact shape of Wave 1's F5 (`gate_receipt` staleness by
> equality), whose consequence was a gate permanently demoted to `--advisory`. Two rows sit in
> `review` today, so the race is live, not hypothetical. Pin the baseline or the check is noise.
>
> ⚠️ **AUDIT FINDING (F3)** — the terminal set used by `--terminal-only` **must be the same object**
> the lint check in §6 uses. Define it once in `wf_common` (extending or replacing `TERMINAL`) and
> import it in both; do not re-declare a local set in this script.
>
> ⚠️ **AUDIT FINDING (F6, over-engineering)** — per-span `sha256` was cut from the manifest above: a
> whole-file byte comparison already subsumes it, and no check consumed it. The simplest thing that
> proves losslessness wins.

**No YAML round-trip, ever.** A round-trip reflows 872 hand-tuned lines, drops every comment, and
converts CRLF. The whole value of this file is in the structure a round-trip destroys.

### 4.2 — Prove `verify` can fail
The Wave 1 lesson, applied: *a checker that cannot fire looks exactly like a clean pass.* Before
trusting `verify`, break the output on purpose and confirm each is caught:

1. flip one line ending in the new board → must fail, naming the offset (a whitespace-only mutation
   is the one a line-by-line diff would wave through, which is why it is case 1)
2. delete one character from one history file → must fail
3. reorder two entries in `CHANGELOG.md` → must fail
4. an unmodified apply → must **pass** (the positive control; a `verify` that always fails is as
   useless as one that never does)

Every one of these is a test case in `.agents/scripts/tests/test_split_sprint_status.py`, run by
`tests/run_all.py`, following the one-test-file-per-script convention.

### 4.3 — Migrate **terminal rows only** (`--terminal-only`)
199 rows, 219,193 bytes, **96 % of the win, ~0 % of the concurrency risk**. Board drops to roughly
130 KB. Run `verify --sha`; it must be byte-clean. Then run the full existing harness against the
migrated tree:

> ⚠️ **AUDIT FINDING (F7)** — the justification is *"no command writes a row that is **already**
> terminal."* A close-out landing mid-window writes a row **into** terminal state and, today, carries
> its active-phase note along with it (F2). So the window is not risk-free by construction — it is
> risk-free **only while no story is in `review` or `in-progress`.** Four rows are today.
> **Gate 4.3 on that condition explicitly**; it costs nothing to wait and it is the whole basis of
> the phase's safety claim.

```
python .agents/scripts/tests/run_all.py
python .agents/scripts/workflow_lint.py  --project AGY_AVIATIONCHAT
python .agents/scripts/story_status.py   check --project AGY_AVIATIONCHAT
python .agents/scripts/closeout_preflight.py --story 21.8b --project AGY_AVIATIONCHAT
```

All four must report exactly what they reported before the migration. **This is the gate**: a
diff in their output is a regression regardless of what `verify` says.

Commit. Stop here if anything is unexpected — 96 % of the benefit is already banked and the
remaining 4 % is the dangerous part.

### 4.4 — Migrate the CHANGE LOG and the free comments
- 52 entries → `history/CHANGELOG.md`, one `##` section each, newest first, verbatim text.
- **Promote `last_updated` to a real YAML key in the retained header** before moving the block —
  today it is the comment at line 66 that rides along with the CHANGE LOG (F9). Match the template's
  shape (`sprint-status-template.yaml:44`), and have `story_status.py set` refresh it on every flip
  so it cannot rot the way the comment did.
- The 347 free-comment lines are **triaged, not bulk-moved**: policy notes (the V3 REVIEW POLICY
  block, the epic-8 rulings) are *doctrine* and belong in the header or a rule; dated narrative goes
  to history. Anything ambiguous stays put — leaving a comment behind costs bytes; moving doctrine
  into history loses a ruling.

  > ⚠️ **AUDIT FINDING (Gate 3 — vagueness)** — "triage 347 lines by judgment" is the one step in
  > this plan a dev will guess at, and guessing buries a ruling. **Make the triage an artifact, not a
  > judgment call at apply time:** `plan --classify-comments` writes `comment-triage.tsv`
  > (line no · first 80 chars · proposed MOVE/KEEP · reason); a human edits it; `apply` reads it and
  > **refuses to run on any line marked `?` or absent from the file.** Default for anything the
  > classifier is unsure about is KEEP.
- Re-point the two CHANGE-LOG writers (`sudo-update-sprint-memory`, `sudo-merge-epic-workingtrees`)
  in the same pass, `_AP` twins diffed alongside.

### 4.5 — Migrate the 19 active rows and re-point the narrative readers
The only phase with live-writer exposure, now isolated to 19 rows. Cap each retained note at 120
chars; the full text goes to history. Re-point `sudo-boot-sprint-memory`, `sudo-update-scrum-board`
and `sudo-resume` to read `history/<epic>/<story>.md` when they need narrative.

⛔ **Blocked on the other session's edits to those three files landing first** (§3).

### 4.6 — Propagate and enforce
- `/sync-agents -Maintained` for the script and the edited commands; commit per repo; bump the
  NEXgen gitlink. `commit-and-push-are-one-action` — no repo left dirty.
- `.agents/scripts/INDEX.md` and the parent plan's Wave 4 section updated to point here.
- Memory: extend `workflow-enforcement-scripts`; the CRLF trap and the terminal/active asymmetry are
  both worth their own entries.
- Drop `.pre-split` **one sprint later**, not in this wave.

---

## 5. Byte-exactness contract

> ⚠️ **AUDIT FINDING (F1) — this section was rewritten by the audit.** The original contract compared
> against the working-tree `.pre-split` file and mandated CRLF preservation. Both are wrong here:
> `* text=auto` + `core.autocrlf=true` mean **two byte streams exist for this file** — 364,206 B CRLF
> on disk, 363,334 B LF in git (verified). A contract that does not name its stream is not a contract,
> and the working-tree stream is the one that varies by machine.

The migration is "done" when, and only when:

```
reconstruct(new_board, history/**, manifest) == git show <source_sha>:<board path>
```

compared as **bytes** against the **pinned git blob** — the LF stream, which is identical on every
machine regardless of `core.autocrlf`. Concretely that requires:

- `open(..., "rb")` on every read and write in the tool; no `newline=` guessing, no `text=True`
- the tool reads its input from `git show <source_sha>:<path>`, never from the working tree, so the
  input is normalised the same way on every machine
- outputs written LF; git's `text=auto` then round-trips them to the local convention on checkout
- `.gitattributes` gains `*.pre-split -text` so the rollback copy is the one file git leaves alone
- no BOM added, trailing newline preserved
- non-ASCII preserved exactly — the file is full of `═ ✅ ⛔ ③ →`, and `workflow_lint`'s encoding
  scan is the independent check that none of it degraded. Run `--staged` before the commit; the
  Wave 5 pre-commit hook will run it anyway.
- **PowerShell must not touch this file.** `Get-Content`/`Set-Content` re-encode and the console
  renders valid UTF-8 as `â€"` besides. Python binary I/O or nothing.

---

## 6. The standing rule — without this the split undoes itself

The file gained ~15 KB in a single day. The split buys back 340 KB; at that rate it is spent in
about three weeks of active development. So the wave ships a rule **and its enforcement together**:

> Narrative never lands in `sprint-status.yaml`. A row carries `key: status` and, only while
> non-terminal, an inline note of **≤120 characters**. The story goes in the story's walkthrough and
> in `_bmad-output/history/`.

Enforced by a new `workflow_lint` check, `check_board_note_budget()`:

- **ERROR** — any inline note >120 chars, or any note on a terminal row
- **ERROR** — total board size >64 KB (a ceiling with headroom, not a tripwire on the target)
- **WARN** — a `history/` file referenced by a key that does not exist

> ⚠️ **AUDIT FINDING (F2 — BLOCKING).** `story_status.py set` **preserves the board note across a
> flip.** Verified by execution:
> `  21-8b…: review   # WIP note` → `  21-8b…: done   # WIP note` (`\g<3>` carries it verbatim).
> Wave 3 wired `set` into close-out Step 4, so *"ERROR — any note on a terminal row"* would fire on
> the **very next close-out**, on a line the toolkit itself just wrote. A rule that indicts its own
> tooling gets muted within a day — the precise failure this whole upgrade exists to end.
>
> **Fix, using an existing pattern rather than a new one:** `story_status.py set` already drops the
> stale inline note from the *story frontmatter* on a flip, for exactly this reason — *"an inline
> history note describes the OLD transition; carrying it past a flip would make it a lie."* Extend
> that same behaviour to the **board** surface when the new status is terminal: drop the note, print
> the `[NOTE] dropping…` line it already prints, and let git hold the original. **This must land
> before §6's check is switched on**, and it needs its own case in `test_story_status.py`.

Two positive controls, per the standing convention: a board with an over-long note must **fail**, and
today's post-split board must **pass**. A check that cannot fire is the Wave 1 failure mode, and this
one guards the entire value of the wave.

While the header is being rewritten anyway, fix the vocabulary drift found during recon: **21 rows
use `deferred`, which the STATUS DEFINITIONS block does not document** (it documents `deferred-v3`
only). `wf_common.ALL_STATUSES` accepts both, so nothing has been failing — the *documentation* is
wrong, and a status that 21 rows use and the doctrine omits is exactly how `deferred` and
`deferred-v3` get mixed, which the block itself warns rots the V3 review list.

---

## 7. Risk register

| Risk | Sev | Mitigation |
|---|---|---|
| **Two byte streams (CRLF worktree / LF blob) make "byte-for-byte" unfalsifiable** | **HIGH** | **F1** — contract pinned to `git show <source_sha>:<path>`; `*.pre-split -text`; 4.2 case 1 asserts a line-ending mutation is caught |
| **The §6 rule indicts `story_status.py`'s own output on the next close-out** | **HIGH** | **F2** — extend `set`'s existing note-drop to the board surface *before* the check is switched on |
| **`verify` unpinned → an honest migration reads as corrupt** | **HIGH** | **F4** — `--sha` required; same fix as Wave 1's `gate_receipt` staleness |
| Migration and lint disagree about "terminal" | MED | **F3** — one set in `wf_common`, imported by both |
| A command writes a row mid-migration | MED | 4.0 freeze; **F7** — 4.3 gated on zero rows in `review`/`in-progress`; 19 noted live rows deferred to 4.5 |
| Doctrine buried in history by an unreviewed triage | MED | 4.4 — `comment-triage.tsv` is a reviewed artifact; `apply` refuses on `?`; default KEEP |
| A narrative reader degrades silently | MED | §3 classifies readers explicitly; 4.5 re-points each; the failure is *less output*, never an error — so it must be checked by reading the output, not by exit codes |
| Two diverged AGY autopilot `.ps1` copies | MED | both listed in §3; `autopilot-has-three-drifting-engines` — fix in all copies or none |
| BMAD's freshness signal dies with the CHANGE LOG | MED | **F9** — promote `last_updated` to a real key in 4.4; `story_status.py set` refreshes it |
| Board regrows | MED | §6 rule + `check_board_note_budget()`, shipped in the same wave |
| Stale-stamp hook fires on the migration commit | LOW | expected; noted in the commit message |
| Merge conflict against another lane's board edit | LOW | the split *reduces* this class — conflicts today are on multi-KB story lines |

**Rollback:** `git checkout <pre-split-sha> -- _bmad-output/implementation-artifacts/sprint-status.yaml`
plus deleting `history/`. Committed in 4.0, before any risk is taken, and held one sprint.

---

## 8. Verification (the wave is not done until all pass)

1. `split_sprint_status.py verify --sha <source_sha>` → byte-clean, at each of 4.3 / 4.4 / 4.5.
2. The four negative controls in 4.2 all fail; the positive control passes.
3. `tests/run_all.py` green, including the new test file **and** the new `test_story_status.py` case
   proving a terminal flip drops the board note (F2).
4. `workflow_lint`, `story_status check`, `closeout_preflight` produce **output identical to their
   pre-migration output** — captured to files in 4.0 and diffed, not remembered.
5. One real close-out (`/sudo-update-sprint-memory`) runs end-to-end against the split board.
6. `/sudo-update-scrum-board` rebuilds correctly from the split board.
7. Every repo `0 0` and clean; NEXgen gitlink bumped.

## 9. Explicitly out of scope

- Changing the status vocabulary itself (only its *documentation* is corrected — §6).
- Reformatting `epics.md` or the scrum board map.
- **BMAD internals** — and per F9 none need touching: `sprint-status-template.yaml` already describes
  the lean shape, so the split converges on it. The one BMAD-facing change is *adding* the
  `last_updated` key the template already expects, which is repair, not a fork.
- Any new dependency. Stdlib Python 3.11 + git.
- Dropping `.pre-split` — that is a separate action one sprint later.

## 10. Rulings needed before 4.1 starts

1. **Note cap: 120 chars, non-terminal rows only** — confirm, or set a different cap.
2. **Epic banners: keep 3 lines or compress to 1?** Keeping costs 11.5 KB of a ~29 KB file; they are
   the only navigation left once the narrative is gone. **Recommend keep.**
3. **Sequencing vs the other session** holding `sudo-resume` / `sudo-boot-sprint-memory` /
   `sudo-update-scrum-board` — wait for it to land, or coordinate the edit (§3, blocks 4.5).
4. **Stop-after-4.3 option** — banking 96 % of the win and deferring 4.4/4.5 is a legitimate landing
   spot, not a failure. Worth deciding now, while it is a plan rather than a retreat.
5. **F3's single terminal set** — extend `wf_common.TERMINAL` to include `optional` and `deferred-v3`
   (affects `check_artifact_budgets`, which today treats 15 such rows as live), or add a second
   named set `NO_NOTE_STATUSES` beside it. **Recommend the second** — `TERMINAL` has existing callers
   with a different question in mind, and widening it is a silent behaviour change to a shipped check.

---

## Self-Audit (2026-08-03)

**Right-size: FULL.** Target `Projects/AGY_AVIATIONCHAT` (the migrated data) plus the lobby toolkit
(the tooling). It qualifies on three counts independently: a shared data model with ~20 consumers, an
irreversible one-way migration, and a new hard rule. Audited **before** any code, by executing every
claim against the live tree — the Wave 1 lesson was that fixture-green proves nothing.

- **Phase 0 (scope · right-size · traceability)** — no ACs exist (initiative plan, not a story), so
  traceability ran against the **parent plan's seven Wave-4 promises**: target shape, per-story
  history, CHANGELOG, line-oriented tool with no YAML round-trip, the 4-step lossless procedure,
  reader re-pointing, and the parent's verification clause. **All seven trace to a phase.** Reverse
  direction: §6 (standing rule + note-budget lint) and §4.2 (prove `verify` can fail) have **no**
  parent promise — both are kept, justified below, and named here so they are not mistaken for creep.
- **Phase 1 (blast radius)** — traced by execution, not reading. `wf._KEY_RE` and `parse_board`
  confirmed to match a **bare** `key: status` line (`note=''`) so the split does not break the
  parsers; `story_status.py`'s rewrite regex confirmed to flip a bare line (`n=1`). Six writers and
  four narrative readers classified in §3. Three consumer defects found: **F1, F2, F4.** One claimed
  risk **disproved** (F5). `check_artifact_budgets` globs `_artifacts/**` only, so `_bmad-output/history/`
  does not interact with it. **A second sweep of the same question found a surface the first had
  missed entirely (F9)** — the first result was `head_limit`-truncated and I read it as complete.
  The lesson is the one this initiative keeps re-learning in a new costume: *a truncated inventory
  looks exactly like a complete one.* The corrected count is **~70 referencing files across three
  trees** (lobby `.agents/`, AGY `.agents/`, AGY `.agent/`), not the 50 originally stated.
- **Phase 2 (over-engineering gate)** — one tripwire fires: per-span `sha256` in the manifest, a
  field no check consumes once a whole-file compare exists (**F6**, cut). `.pre-split` was also
  challenged as duplicating `git show <sha>:path` — **kept**, demoted from verification baseline to
  non-git convenience rollback. Everything else earns its place: three modes are three distinct
  questions, `--terminal-only` is justified by a 96 %/4 % measurement, and §6 traces directly to a
  measured 15 KB/day regrowth rate plus the parent's governing principle. No new dependency.
- **Phase 3 (pre-mortem)** — "shipped and silently corrupted state." The dominant mode here is not
  data loss (the reconstruction catches that); it is **a guarantee that cannot fail** (F1: comparing
  the wrong stream) and **a guarantee that fails on honest work** (F4: no SHA pin → muted, exactly
  as Wave 1's F5 demoted a gate to `--advisory` permanently). Third mode, unique to this wave: a
  **narrative reader degrades silently** — it reports less and nothing errors (§3, mitigated in 4.5
  but only checkable by reading output, not by exit codes).

| # | Location | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| F1 | §5, §4.0 | **HIGH** | `* text=auto` + `core.autocrlf=true` → **two byte streams**: worktree 364,206 B CRLF vs blob 363,334 B LF (verified). "Byte-for-byte against `.pre-split`" names neither, and `.pre-split` is itself LF-normalised by git, so the rollback restores 872 different bytes on a machine with `autocrlf=false`. The guarantee reads as airtight and proves nothing. | ✅ **Baked in** — contract pinned to `git show <source_sha>:<path>`; `*.pre-split -text`; §1 numbers labelled as the LF stream |
| F2 | §6 vs `story_status.py:103` | **HIGH** | `set` carries the board note across a flip — verified: `review # WIP note` → `done # WIP note`. Wave 3 wired `set` into close-out Step 4, so §6's *"ERROR — note on a terminal row"* fires on the **next close-out**, against a line the toolkit itself wrote. A rule that indicts its own tooling is muted within a day. | ✅ **Baked in** — extend `set`'s existing frontmatter note-drop to the board surface; lands **before** the check is enabled; owed a `test_story_status.py` case |
| F4 | §4.1 | **HIGH** | `verify` has no baseline pin, so it reconstructs the tree *as of now*. A close-out landing between `apply` and `verify` makes an honest migration read as corrupt. Two rows are in `review` today. Identical in shape to Wave 1's F5, whose consequence was a hard gate permanently demoted to `--advisory`. | ✅ **Baked in** — `--sha` required, compare against the pinned blob |
| F3 | §1, §4.1, §6 | MED | The plan's "terminal" (`done · descoped · deferred-v3 · optional`) ≠ `wf_common.TERMINAL` (`done · descoped`). 15 rows / 215 note bytes sit in the gap. `--terminal-only` strips notes the new lint check considers live → migration and enforcement disagree on day one. | ✅ **Baked in** — one set in `wf_common`; ruling #5 added (recommend a second named set, not widening `TERMINAL`) |
| F7 | §4.3 | MED | "No command writes a terminal row" holds only for rows *already* terminal. A close-out mid-window writes a row **into** terminal state, note attached (F2). The phase's entire safety claim is conditional and the condition was unstated. | ✅ **Baked in** — 4.3 gated on zero rows in `review`/`in-progress` |
| — | §4.4 | MED | "Triage 347 comment lines, doctrine vs narrative" is the one step vague enough that a dev guesses — and a wrong guess buries a ruling in history, which is the failure `settled-decisions-are-not-gaps` already has a memory for. | ✅ **Baked in** — `comment-triage.tsv` as a reviewed artifact; `apply` refuses on `?`; default KEEP |
| F6 | §4.1 | LOW | Per-span `sha256` in the manifest is consumed by nothing once the whole-file compare exists. Over-engineering tripwire: a field that looks like rigour and adds none. | ✅ **Cut** |
| F9 | §3, §4.4, §9 | MED | **§3's consumer map was incomplete.** AGY has two toolkit trees — `.agents/` (synced lobby) and **`.agent/` (vendored BMAD skills, ~20 more files)**. Missing from it: a **7th writer** (`bmad-quick-dev/sync-sprint-status.md`), the `bmad-sprint-status` skill, and the template defining the board's canonical shape. Concrete break: `last_updated` is a *comment* at line 66 riding directly above the CHANGE LOG, so 4.4 moves the date to history and `bmad-sprint-status` falls back to `generated: 2026-03-07` and warns "stale" forever. | ✅ **Baked in** — §3 table extended; 4.4 promotes `last_updated` to a real key per the template; §9 clarified |
| F5 | §3 | LOW | The plan claimed `board-stale-stamp.sh` "will fire once, loudly" on the migration commit. **False** — line 55 strips the comment before comparing values and line 10 says "comment-only edits ignored"; the drift file comes out empty and the hook exits 0. The plan overstated its own risk. | ✅ **Retracted** in §3 |
| F8 | §1 | INFO | The terminal/active table conflated *total rows* (235/26) with *rows carrying a note* (199/19). The 199/19 split — the number the whole phasing rests on — is correct. | ✅ **Column added** |

**Four gates**

- *Verification strategy present?* Yes — §8's seven items plus §4.2's four negative controls **and** a
  positive control. Two gaps closed by the audit: item 1 was unfalsifiable until F1/F4 pinned it, and
  item 4 said "identical to before" without ever writing *before* down (4.0 now captures it to files).
- *Irreversible / destructive?* **Yes — this is the only such wave in the initiative.** Mitigations
  are adequate as amended: rollback committed before any risk (4.0), `-text` so git cannot re-normalise
  it, held one sprint, and the 96 %/4 % phasing means the dangerous 4 % can be abandoned with the win
  already banked.
- *Any step vague enough the dev will guess?* One — §4.4's comment triage. Tightened into a reviewed
  artifact with a fail-closed default. No others.
- *Quality fit?* Yes. `.agents/scripts/` beside the Wave 1 tools, stdlib-only, `wf_common` imported
  rather than re-implemented, one test file per script under `tests/run_all.py`, ASCII output. F3 was
  the single place it drifted from that and is corrected.

**Decomposition flag:** this is a **two-repo** change — lobby toolkit (`split_sprint_status.py`,
`workflow_lint`, `story_status.py`, four commands) and AGY data (the migration itself). §4 already
orders it correctly: the tool and its tests land and go green in the lobby **before** the AGY
migration commit. No split recommended; the ordering already carries the benefit.

**Audit verdict: NO-GO as written · GO conditional on F1 · F2 · F4 landing first.**

All three are the same failure class this initiative exists to end — an enforcement point that either
cannot fail (F1) or fails on honest work and gets muted (F2, F4). They are cheap now and expensive
after the migration, which is exactly why this gate runs before a line of code. F3 · F5 · F6 · F7 · F8
· F9 and the §4.4 tightening are already baked into the plan above; **the four rulings in §10 plus the
new fifth are owed before 4.1 starts.**

> **Audit addendum (same day, after the first verdict).** A second, slower sweep of the consumer
> question returned **F9** — an entire vendored BMAD skill tree (`.agent/`, singular) that the first
> sweep truncated away. It does not change the verdict: F9 is MED, fully mitigated in §3/§4.4/§9, and
> its largest sub-finding actually *reduces* risk (BMAD's own template already describes the lean
> shape this wave produces). It is recorded rather than quietly folded in because the miss is the
> point — **the audit's own blast-radius phase was one truncated tool result away from shipping an
> incomplete consumer map**, which is precisely the defect class the map exists to prevent.
