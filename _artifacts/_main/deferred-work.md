# Deferred work — the center's BLOCKED-work ledger

This is the `DEFERRED_WORK` file the code-review engine's caller contract names, for toolkit
lanes (the center is its own caller). **Nothing in this file is owed, and nothing in it becomes a
ticket** (operator rulings 2026-08-15, both): an entry exists ONLY because the lane that found it
structurally could not hold the fix — another live lane owned the file, the fix lives in another
repo, or it waits on an open decision. "Pre-existing" is not a reason to be here; a survivor with
no blocker is fixed in the lane that found it. An entry is picked up by the lane its blocker
names, or deleted when its reason dies. No close-out mints a ticket from this file, and no
review proposes one from it.

Format per entry: `- <title> [<file>] — <why it matters> · blocked by <live lane | repo | decision> · from <review>`.

## SCC-160 first live run — re-triage of the SCC-156 + SCC-154 residues (2026-08-15)

All three entries this ledger opened with were **fixed in-thread on `chore/SCC-160-fix-in-thread`**
(operator ruling the same day: survivors are fixed in the lane, not parked): Ctrl-C now stops
`run_all` (queue cancelled, children terminated — the review's one-word fix was measured
insufficient and replaced); a zero-file suite is exit 2; `dirty_paths` reads `porcelain -z` and
records both sides of a rename (direction measured: the old parse would have exempted moved
code). None of them had a structural blocker — under the recut `defer` definition they should
never have been here. The ledger is empty; that is its correct resting state.

## SCC-205 · the `-AP` law assertions — RESOLVED the same day, not carried (2026-08-18)

Opened and closed within the hour. The entry claimed a blocker of "an open decision — the `_AP`
rewrite"; the operator ruled on it directly: the `_AP` commands are being **rewritten from
scratch**, they will not resemble what is there now, and they survive only as reference while
the rebuild happens. That killed the blocker, and the fix landed in this lane where it belonged.

Worth recording, because the entry should not have been written in the first place: it framed the
problem as a binary — delete the `-AP` files (forbidden: three autopilot engines invoke them by
name) or un-pin them from `CALLER_FILES` (breaks the completeness row that caught this lane's own
`cicd-quick-dev` omission) — and deferred on the strength of that. **Both horns were real and the
dilemma was false.** The third door was to keep the file pinned as a CALLER and stop pinning its
CONTENT: `CALLER_FILES` never required a law row: nothing in the suite ties the two together. The
eight rows came out, the completeness row stands, and the case count fell 873 → 849 exactly as
8 rows × 3 checks predicts.

The ledger is empty again; that is its correct resting state.

---

## SCC-394 · two `SKILL.md` files carry unparseable YAML frontmatter (2026-09-04)

**The finding, reproduced.** `yaml.safe_load` over all 74 master `SKILL.md` frontmatter blocks
fails on exactly two: `cicd-prune-context` (`mapping values are not allowed here`, an unquoted
`: ` inside the description — `` `active-context: ~X / 5,000 tokens` ``) and
`smh-close-task-merge-tree` (same class — `STOPS: it never merges`). `New-LauncherSkillStub`
copies the brain's `description:` line into the stub raw: no quote, no escape, no truncation.

**Why it is deferred rather than fixed in SCC-394's lane.** Both description lines are
**byte-identical on `origin/main`** — verified with `git show origin/main:<path>` — so the defect
is pre-existing in lines this ticket does not touch, and Claude and Codex have been reading those
same two files all along. What SCC-394 changes is that Antigravity becomes a third reader. The
fix — quoting and escaping in the stub — rewrites the frontmatter of all 51 generated launchers,
which is a larger unreviewed change than the defect it closes, landing after the lenses ran.

**The remedy, named.** In `New-LauncherSkillStub`, emit
`('description: "' + $d.Replace('\','\\').Replace('"','\"') + '"')` after the same
`.Trim().Trim('"').Trim("'")` the Zoo emitter already applies, and add one assertion that every
`.agents/skills/*/SKILL.md` frontmatter parses as YAML — `grep -rn 'safe_load' .agents/scripts/`
returns nothing today, so no test in the repo can currently see this.

**Blocker:** it is `origin/main`'s defect, not this lane's diff.
