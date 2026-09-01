# SCC-60 — walkthrough: the Jira rule was Mac-only and sandbox-blind

**Branch:** `chore/SCC-60-jira-rule-portability` · **Base:** `f5eb89d` · **Plan:** [implementation_plan.md](implementation_plan.md)
**Worktree:** `.claude/worktrees/jira-rule-portability` — the main checkout was occupied by a live SCC-59 session.

## What triggered it

The operator reported that a second agent had *"moved the key to the macOS keychain, which will break my
desktop computer."* The suspicion was right about the **defect** and wrong about the **culprit**, and both
halves mattered.

**The other team never touched the file.** Their branch had zero commits (`git diff main...HEAD --stat`
empty). The Mac-only wording arrived in `8c6ca97` on **2026-08-07** — the commit that *created*
`.agents/rules/jira.md` under SCC-14. It had been wrong for two days, unnoticed, in the file whose entire
job is telling agents the board is reachable.

## The two false claims, and which one was actually dangerous

The second agent said, in sequence:

1. *"The Jira CLI is no longer authenticated, so I cannot mint a fresh maintenance ticket without inventing a key."*
2. *"The artifact moves already landed under verified SCC-54 commits, so I'm using SCC-54 for the follow-on maintenance branches; no Jira state will be changed."*

**Claim 1 was false.** `acli jira auth status`, run unsandboxed in the same repo minutes later:
`✓ Authenticated · sudo-command.atlassian.net · api_token`. `acli jira workitem create` also worked —
SCC-60 itself was minted with it while the other agent was calling minting impossible.

**Claim 2's premise was TRUE, which is what made it persuasive.** SCC-54 really did do artifact moves:
`74410b9` (archive June), `6630909` (archive July), `be3746e` (repoint the 60 links the move broke). Those
are the exact directories still missing an `INDEX.md`. Reaching for that key was *reasoned*, not lazy.

**But "no Jira state will be changed" was the dangerous part**, and it was false twice over:

- Atlassian's GitHub app links every commit on a `<prefix>/<KEY>-<slug>` branch. A closed ticket would
  have silently accumulated branches and commits dated after its close.
- `jira_feed.py check --key SCC-54` → **one Dev Record (2713 chars)**. `devrecord` keeps exactly one per
  ticket and updates it **in place**, so a close-out under SCC-54 would have **overwritten the record of
  the trace-and-flag work** with a maps-indexes record. That is destroying real history, not mislabelling.

The operator stopped it before any of that landed, and the other team re-minted correctly as **SCC-59**.

## The root cause nobody had written down

`grep -i sandbox .agents/rules/jira.md` → **no matches.** Nothing in the repo warned that a sandboxed
tool call cannot reach the OS credential store, so `acli` fails there while working perfectly unsandboxed.
Both agents read a fact about **their own shell** as a fact about **the board**.

The second agent had even diagnosed this correctly — *"my sandboxed check could not access that credential,
and I treated the sandbox result as real account state"* — and then reached the identical false conclusion
one message later. **A lesson an agent derives mid-session does not survive the next tool call. It has to
be in the file.**

## What changed — 3 edits, one file, plus the SOP doc

**`.agents/rules/jira.md`**

1. **Header** — dropped `/opt/homebrew/bin/acli` (the only Homebrew path in all of `.agents/rules/` and
   `.agents/commands/`) and the bare "macOS keychain". Now names the OS credential store for *both*
   machines and points at `acli jira auth status`, which the file **already documented 220 lines lower**
   under §Reading the board — the header just never pointed at it. Added the ⛔ sandbox block as a table
   mapping each wrong conclusion to what it actually was, including the "so I'll reuse an existing key" one.
2. **Guardrail 1** — "never invent a key" banned *imagined* keys and said nothing about a **real key for
   finished work**, which is the hole both agents fell through. Now carries the open-ticket requirement, the
   two mechanisms that make "no state will change" false, the one-line `view --fields "status"` check, and
   the explicit note that **the armed commit-msg hook validates the project prefix, never the status — it
   will not catch this.**
3. **Guardrail 5** — "the token stays in the keychain" → the OS credential store, plus the standing rule
   never to bake a path or store name into a doc read on both machines.

**`_my_resources/_quick_reference/sudo_workflows_testing.md`** (SOP currency — `.agents/rules/*.md` is armed)

- §7 *What does NOT travel between the machines* — a fifth row: **The Jira login**. It belongs in that table
  by the table's own stated rule (*"anything stored outside the repo is per-machine by definition"*).
- §11 — the ⛔ operator-facing version: if an agent says the board is unreachable, tell it to re-run
  outside its sandbox.

## Gates — all run in the worktree, real output

| Gate | Result |
|---|---|
| `run_all.py` | **9/9 files passed** |
| `workflow_lint.py --project …/AGY_AVIATIONCHAT` | 1 error, 3 warnings — **the exact pre-existing baseline**; the error is AGY's missing 19.5 story file, untouched here |
| Link + anchor check | 3 files / 26 relative refs / **0 unresolved** |
| `sop_currency.py --paths … --message …` | **exit 0** |

## Decisions

- **Worktree, not a branch switch.** One checkout, and a live SCC-59 session in it. `git checkout -b` here
  would have moved *their* HEAD out from under them mid-run. `.claude/worktrees/` is already gitignored and
  is the convention `/sudo-resume` uses.
- **Rule change only — no hook change.** A ticket-status check in the commit-msg hook would put a live
  network call on every commit and fail closed offline. The rule plus a one-line `acli` read is
  proportionate. Recorded in the plan so the next reader knows it was considered, not missed.
- **Named the incident, with dates and the SCC-54 key, in both docs.** A guardrail that says "don't reuse a
  closed key" is ignorable; one that says "this happened on 2026-08-09 and would have overwritten SCC-54's
  Dev Record" is not.

## Pitfalls

- **My own plan shipped two broken links.** `[jira.md:9](.agents/rules/jira.md#L9)` from inside
  `_artifacts/_main/<folder>/` resolves to `_artifacts/_main/<folder>/.agents/…`, which does not exist. The
  link check caught it. Repointed to `../../../` and dropped the `#L` anchors, which my own edits had
  already invalidated.
- **`sop_currency.py` has no `--staged` flag.** `--staged` made argparse error, and piping to `tail` made
  `$?` report the exit of `tail` — so it *printed* `exit=0` while the gate had not run at all. Re-run
  unpiped with `--paths`. Same shape as the sandbox bug this ticket is about: a failure read as a pass.
- **`workflow_lint.py` can't resolve a project from inside a worktree** (`Projects/` submodules aren't
  populated there). Pointed at the real AGY checkout with `--project`; read-only, so the other session
  was unaffected.

## Still owed

- **Merge overlap with SCC-59** on `_artifacts/_main/INDEX.md` — one row each. Flagged, not a blocker.
- **Not closed out.** `/close-task-merge-tree` is the operator's sign-off and is not mine to invoke.
  SCC-60 stays `To Do` until then.
