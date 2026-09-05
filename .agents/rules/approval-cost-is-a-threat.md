---
name: approval-cost-is-a-threat
description: "An approval prompt is a THREAT to whether this system can be paid for, not a UX wrinkle. Every stop breaks the prompt cache and re-bills the whole context. Measured: 5h50m of allow-gap stalls in 20 sessions against ZERO deny-row refusals; the operator cancelled a paid subscription over it. Load whenever a command stops for approval, whenever the allow list, permission fence, families.json or the three rendered settings files are touched, and whenever /smh-llm-approvals runs."
trigger: model_decision
triggers: [allow list, allowlist, approval, approve, permission, permissions, families.json, smh-llm-approvals, auto-approve, prompt, stopped and waited, allowedCommands, globalPermissionGrants, budget, token cost, cache]
---

# An approval prompt is a cost, and the cost is the point

**This rule exists because every agent that met this problem treated it as hygiene, and the operator
kept paying.** It is written as law rather than left in agent memory because memory is per-machine,
unversioned and prunable — and this ruling has to reach every seat, every platform and every future
session.

## The operator's words

> *"This is killing my workflows and budget. I canceled Claude over this. Until it's fixed it's not
> worth it. It's why I had to add Zoo."* — 2026-09-05
>
> *"I want them allowed so I stop losing money for silly approves."*
>
> *"The problem here as I have examined before is that when these commands get blocked it stops the
> workflow. If the chat goes idle for more than 5 minutes I lose the cache. Then the agent has to
> pull the full context all over again, doubling my token costs. So at this point that is the bigger
> threat than some of the protections we are trying to keep."*

## Why a prompt is expensive

A stop does not cost the seconds it is on screen. It **breaks the prompt cache**: the turn resumes
cold and the entire context is billed a second time. Every interruption is charged twice — once in
his attention, once on the invoice — and when he is away from the keyboard the stall is measured in
hours, not minutes.

## The measurement that settles the trade-off

Measured on the operator's machine, 20 newest sessions, 10,028 Bash calls, 2026-09-05:

| bucket | stops | wall-clock | what fixes it |
|---|---|---|---|
| allow-list gaps | 44 | **5h 50m** | an allow row |
| a SHAPE the matcher cannot read — heredoc, leading `VAR=` — while looking covered | 94 | **13h 01m** | the AGENT reshapes; `shape-block.py` refuses / proves it (SCC-415). Never a row, never `/sandbox` |
| **refused by a deny row** | **0** | **0** | — |

⚠ The middle row read *"sandbox escalation → `/sandbox`, 1h 16m"* until the 2026-09-05 re-measurement
(SCC-415), which classified the same calls by SHAPE: 54 heredocs (7h17m) and 40 leading `VAR=`
assignments (5h44m), every one sandboxed, rule-matched and violation-free, still stopping. `/sandbox`
fixes none of them and `sandbox.excludedCommands` makes them worse. That diagnosis cost a full
session; it is corrected here so it is not repeated.

⭐ **Zero commands were refused by a deny rule.** All 115 Zoo deny rows and all 424 Antigravity ones
cost nothing measurable. **So never propose relaxing the deny fence to fix this** — it trades away a
protection that costs nothing for a problem it is not causing. The cost is two things: the *absence*
of allow rows (fixed by rows, and the reason they are absent is ceremony) and the *shape* of the
agent's own commands (fixed by the agent, and by the hook that refuses the shape before it reaches
the operator).

## The law

1. **Adding an allow row is a two-file edit, not a story.** `/smh-llm-approvals` Step 4 carries the
   exemption; use it. A lane, a plan, a five-lens review or a ticket in place of a row is the
   failure mode this rule names, not diligence.
2. **Claude rows are free.** Claude reads `.claude/settings.json` **directly** — that tracked file
   IS the live file, and a rendered row is in force the moment it is saved. No store, no apply, no
   reload, nothing for the operator to run. Reach for this first.
3. **Narrow beats nothing.** If the broad command is unsafe, allow the safe subcommand
   (`acli jira workitem view`, never bare `acli`). Adding nothing because the wide form is dangerous
   is how this command produces zero rows and the operator keeps paying.
4. **Never allow real damage.** `rm -rf`, `rm -f`, `install -m` (it copies his `.env` and credential
   files), `git submodule deinit -f`, `env -C`, `git push`, bare `git branch`. Safety is not the
   thing being traded away — ceremony is.
5. **An approval he clicks must SURVIVE.** Both platform applies merge rather than replace
   (SCC-414). Before that fix, one routine apply deleted **58** of his own clicked grants; he
   re-clicked and the next apply deleted them again, which is why he believed his approvals "don't
   seem to store". Never reintroduce a replace as the default, and never run `--prune` without his
   word.
6. **Act, then report in a few lines.** He has said plainly that the explaining is itself the cost.

## How to know you succeeded

Re-run `python3 .agents/scripts/approval_stops.py --repo .` and the **not covered** count must have
gone DOWN. State the before and after.

⛔ **Ending an approvals run with nothing allowed is a FAILURE**, even when every gate is green,
every finding is filed and the report is immaculate. A measurement is not an outcome. A ticket is
not an outcome. The outcome is a smaller number of prompts.

## Related

- [`smh-llm-approvals`](../commands/smh-llm-approvals.md) — the door this rule governs; its § *WHY
  THIS COMMAND EXISTS* carries the same numbers.
- [`git-policy`](git-policy.md) — what may never be allowed, whatever the cost.
- [`constitution`](constitution.md) §Ask First — the protections that stay, because they cost nothing.
