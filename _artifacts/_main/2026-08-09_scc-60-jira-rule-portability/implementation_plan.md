# SCC-60 — Make the Jira rule portable across machines and platforms

**Ticket:** SCC-60 · **Branch:** `chore/SCC-60-jira-rule-portability` · **Base:** `f5eb89d`
**Worktree:** `.claude/worktrees/jira-rule-portability` (the main checkout is occupied by SCC-59)

## The trigger

Two agents, two hours apart, both concluded the Jira board was unreachable while `acli` was working
perfectly. The second one then proposed committing new work under **SCC-54**, a ticket that closed at
`74b1f02`, on the reasoning that it *"cannot mint a fresh ticket without inventing a key"* and that
*"no Jira state will be changed."*

Both halves were false, and neither was caught by anything in the repo.

## Ground truth (verified, this session)

```
$ acli jira auth status
✓ Authenticated
  Site: sudo-command.atlassian.net
  Email: sudomadhatter@gmail.com
  Authentication Type: api_token
```

- `acli jira workitem create` works — SCC-60 was minted with it while the other agent called minting impossible.
- SCC-54 is `Done`, and `jira_feed.py check --key SCC-54` reports **one Dev Record (2713 chars)**.
- `grep -i sandbox .agents/rules/jira.md` → **no matches**. Nothing warned either agent.
- `/opt/homebrew/bin/acli` in the opening paragraph of
  [.agents/rules/jira.md](../../../.agents/rules/jira.md) was the **only** Homebrew path in all of
  `.agents/rules/` and `.agents/commands/` (pre-edit line 9).
- That same file **already documented** `acli jira auth status` under §Reading the board (pre-edit
  line 231) — the header simply never pointed at it.

## Why this is a portability bug, not a typo

`.agents/rules/jira.md` travels via git to both machines and is read by all four platforms. It opens
by telling the reader the binary is at `/opt/homebrew/bin/acli` and the token is in "the macOS
keychain". On the Windows desktop **neither exists**, so the rule's own opening paragraph manufactures
the exact belief the paragraph three lines below calls *"false by design"* — `"I have no Jira
integration"`. See `two-machines-mac-and-pc`.

The sandbox case is the same failure from a different direction: a sandboxed shell cannot reach the
credential store, so `acli` fails, and the agent reads a fact about **its own shell** as a fact about
**the board**.

## The three edits — all in `.agents/rules/jira.md`

### 1. Header (lines 8–13) — de-machine it, and name the sandbox trap where it will be read

Drop the hardcoded path and the store name. Point at `acli jira auth status` as the one portable
answer. Add the ⛔ block: *an `acli` failure is a fact about your shell*, with the three wrong
conclusions it has actually produced spelled out — "no such ticket", "no longer authenticated", and
"I cannot mint, so I'll reuse a key".

### 2. Guardrail 1 — "never invent a key" must also mean "never reuse a closed one"

The existing guardrail bans *imagined* keys. It says nothing about a **real key for finished work**,
which is the hole both agents fell through. Add the two mechanisms that make "no Jira state will be
changed" false:

- Atlassian's GitHub app links every commit on a `<prefix>/<KEY>-<slug>` branch → a closed ticket
  silently accumulates branches and commits dated after its close.
- `jira_feed.py devrecord` keeps **exactly one** Dev Record per ticket and updates it **in place** →
  a close-out under a reused key **overwrites** the record of the work that earned it.

And the reason the machine won't save you: the armed commit-msg hook validates the *project* prefix,
never the *status*.

### 3. Guardrail 5 — the token line is Mac-only too

`"The token stays in the keychain"` → the OS credential store, plus the standing instruction never to
hardcode a path or a store name into a doc that is read on both machines.

## Out of scope (deliberate)

- **No script or hook change.** A status check in the commit-msg hook would put a live network call on
  every commit and fail closed when offline. The rule + `acli jira workitem view <KEY> --fields
  "status"` is the proportionate fix. Recorded here so the next reader knows it was considered.
- **Not touching SCC-59's lane.** The other team already corrected their own branch key unprompted.

## Gates

| Gate | Command |
|---|---|
| Enforcement suite | `python3 .agents/scripts/tests/run_all.py` |
| Toolkit self-consistency | `python3 .agents/scripts/workflow_lint.py` |
| Link + anchor check | every path and `#L` anchor the diff touches |
| SOP currency | `_my_resources/_quick_reference/sudo_workflows_testing.md` must move — `.agents/rules/*.md` is an armed surface |

## Known merge overlap

SCC-59 is editing `_artifacts/_main/INDEX.md` in the main checkout; this lane adds a row to the same
file. One row each, resolvable at merge — flagged, not a blocker. See `parallel-lanes-fix-the-same-finding`.
