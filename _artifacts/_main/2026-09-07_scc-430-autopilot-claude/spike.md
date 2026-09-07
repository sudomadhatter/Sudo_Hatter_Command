---
IsArtifact: true
ArtifactMetadata:
  title: SCC-430 - S0 spike, the five measurement tables
  type: spike
  date: 2026-09-07
---

# SCC-430 - S0 spike (Step 1, acceptance row A)

**Measured on:** 2026-09-07, WSL2 Ubuntu, Claude Code CLI **2.1.263** (upgraded from 2.1.258 this
session on the operator's word). Every number below came from a real launch's `usage` block in
`--output-format json`; nothing here is estimated or recalled. Raw captures:
[`spike/`](spike/) plus the per-launch JSON in the session scratchpad.

**Total spend for the whole spike: ~$2.03.** Three-quarters of that was the first three probes,
which ran on the inherited default model before the model was pinned - which is itself finding 4.

---

## What the spike changed, in one paragraph

The runner cannot be built the way the design drew it, and the reasons are all cheap to fix. Three
of the design's assumptions are false as measured: a seat's `skills:` list does **not** preload skill
text, `--max-budget-usd` does **not** stop a child from overspending its cap, and a forked child
**silently loses its seat** unless the seat is handed to it again. Two assumptions turned out better
than feared: a sandboxed child **does** reach the model, so the `sandbox.excludedCommands` question
the audit raised is moot; and the layered fork pattern the whole cost case rests on is real, cutting
a five-step run by **63%**. One flag the audit called unconfirmed - `--append-system-prompt-file` -
does exist; it is simply undocumented in `--help`.

---

## Table 1 - which seat delivery is cheaper

Ten byte-identical launches per arm, sequential, `claude-haiku-4-5-20251001`, same prompt
(`Reply with the single word OK.`), same flags otherwise.
**Arm A:** `--agents "$(cat seat.json)" --agent gnat`. **Arm B:** `--append-system-prompt-file seat-pointer.md`.

| arm | launches | prefix built per launch | cache reads seen | mean cost / launch | total |
|---|---|---|---|---|---|
| **A - `--agents` + `--agent`** | 10 | ~11,470 tok | 3 of 10 | **$0.0262** | $0.2618 |
| **B - `--append-system-prompt-file`** | 10 | ~18,010 tok | 9 of 10 | $0.0450 | $0.4499 |

**Arm A wins on cost by 42%**, and *not* for the reason the design expected. Arm A reads the cache
*less* often. It is cheaper because the seat's `tools` list (`Read`, `Grep`, `Glob`) shrinks the
child's system prompt from ~18k tokens to ~11.5k - the tool definitions the child never needs are
simply never sent. **The saving is prefix SIZE, not cache reuse.**

⚠️ **The arms are confounded, and it does not change the verdict.** Arm B has no seat, so it carries
the full default tool set; the comparison therefore measures delivery *and* tool surface together.
Both effects push the same way and arm A is the design's choice regardless, so the confound is
recorded rather than removed.

⚠️ **Cross-launch cache reuse is unreliable in both arms.** Byte-identical launches read the cache
3 times in 10 (arm A). Any design paragraph that assumes independent headless children ride each
other's prompt cache is wrong. The reliable saving is Table 3's, and it comes from forking.

## Table 2 - the fork chain

One parent, then one child resumed from it with `--resume <id> --fork-session`.

| launch | cache_create | cache_read | cost |
|---|---|---|---|
| parent (fresh seated child) | 12,603 | 0 | $0.02647 |
| **fork (seat re-passed)** | **514** | **12,603** | **$0.00456** |

**A fork costs 83% less than a fresh child** and reads the parent's entire prefix. Design layer 2 is
real and is the single biggest lever in the runner.

⚠️ **A fork drops the seat unless `--agents` is passed AGAIN.** Resuming with only `--resume --fork-session`
produced, verbatim:

> `This session was running agent 'gnat', which is no longer available (no agent by that name in
> /home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-430-autopilot-claude). Continuing with the default`

The run **continues** - it does not fail - so a fork chain would quietly lose the seat's identity,
its model and its tool restrictions mid-run, and every later step would look normal. `--agents` is
defined per process and is **not** inherited through a resume.

## Table 3 - naive vs layered over five steps

Same five prompts, same seat, same model, same flags. **Naive:** five independent fresh children.
**Layered:** one pack parent, then five forks off it with `--agents` re-passed each time.

| step | naive cost | layered cost |
|---|---|---|
| pack parent | - | $0.03005 |
| 1 | $0.02718 | $0.00488 |
| 2 | $0.03150 | $0.00439 |
| 3 | $0.04027 | $0.00963 |
| 4 | $0.02736 | $0.00331 |
| 5 | $0.03192 | $0.00641 |
| **total** | **$0.15823** | **$0.05867** |

**Layered is 63% cheaper** over five steps. Counting only the forks against the naive children
(i.e. once the pack amortizes over a longer run) it is **82% cheaper**: each fork builds ~340 tokens
of prefix instead of ~12,600.

## Table 4 - the `--agents` + `--agent` pair, and the `skills:` field

The pair works: `--agents <json>` defines the seat and `--agent <name>` selects it for the session.
The vendor documents each half; the pair is confirmed here.

**`skills:` does NOT preload skill content.** Two launches identical except for the key:

| seat | cache_creation_input_tokens |
|---|---|
| with `"skills": ["smh-memory-audit"]` | 11,466 |
| without the key | 11,467 |

A **one-token** difference. The skill's body is not injected, and neither is its ~175-token
description. The child, asked to quote the skill's first heading with no tools, replied:

> `status: failed` / `summary: no skill preloaded` - *"my startup context contained a pointer to
> `.agents/commands/smh-team-gnat.md`, not the skill's text."*

The field is nonetheless **real and validated**: `"skills": 12345` is refused client-side with
`Invalid --agents configuration: gnat.skills: Invalid input`. A non-existent skill name is accepted
silently. So the key is parsed and then has no measurable effect on the prefix.

⛔ **Unknown keys in `--agents` are accepted silently** (`"totallyBogusKey": 123` launched fine), so
the Step 3 renderer gets no typo protection from the CLI and must be pinned by its own test.

## Table 5 - can a sandboxed child reach the model

| question | answer | evidence |
|---|---|---|
| Does a child launched from a sandboxed Bash call reach the API? | **YES** | `duration_api_ms: 5287`, real `usage`, `is_error: false` |
| Does that child persist a resumable transcript? | **NO** | no file under `~/.claude/projects/`; the fork then failed `No conversation found with session ID` |
| Unsandboxed? | **YES to both** | transcript written to `~/.claude/projects/-home-dlohn-Sudo-Hatter-Command--claude-worktrees-scc-430-autopilot-claude/<id>.jsonl`, and the fork resumed it |

**The audit's blocker is dissolved, and replaced by a smaller and better-specified one.** Network
egress was never the problem - `sandbox.excludedCommands` would have fixed nothing, exactly as the
operator said on 2026-09-05. The real constraint is a **write** path: the sandbox denies
`~/.claude/projects`, that is where a session transcript lives, and **no transcript means no fork**,
which costs the 63-83% of Table 3.

**Remedy, and it is expressible in the house tool** (unlike `excludedCommands`):
`claude_permissions_apply.py --status` already reports a `sandbox : N allowWrite path(s) to add`
line, so the sandbox write-path list is a surface this repo manages. Whether
`~/.claude/projects` can be granted there - it currently sits in the runtime's deny-within-allow
list - is **Step 2's first question**, and the fallback is simply that the runner runs unsandboxed.

---

## Findings that change what gets built

1. **Re-pass `--agents` on every launch, including every resume and fork.** Otherwise the seat is
   silently dropped and the run continues wrong (Table 2). A test pins this.
2. **`--max-budget-usd` is not a cap on a turn; it stops the NEXT one.** Two probes capped at
   `$0.05` reported `terminal_reason: "budget_exhausted"` and `errors: ["Reached maximum budget ($0.05)"]`
   while actually spending **$0.496** and **$0.296** - 10x and 6x the cap. For an unattended
   overnight runner this is the difference between a budget and a suggestion: the runner needs its
   own pre-flight ceiling (pin the model, cap `--model` per seat, and stop the RUN on the ledger's
   running total), and the door's charter must not promise a hard per-child cap it cannot enforce.
3. **`--json-schema` takes inline JSON, not a file path.** `--json-schema result.schema.json` fails
   with `--json-schema is not valid JSON: JSON Parse error`. The runner passes `"$(cat schema.json)"`.
   And the schema **shapes** the reply without guaranteeing it: with the schema applied, `result`
   came back as the *string* `"status: failed\nsummary: no skill preloaded\n\nWhy: ..."`, not a JSON
   object. **The runner must parse defensively and treat an unparseable result as `failed`** - which
   is exactly what acceptance row B's `test_result_without_status_is_failed` already demands.
4. **Pin `--model` on every child.** Unpinned children inherited `claude-opus-5[1m]` (1M context)
   and cost **$0.157-$0.496 for a one-word answer**. The same work on `claude-haiku-4-5-20251001`
   cost **$0.024**. That is a 6-20x factor on the least valuable calls in the run.
5. **Redirect stdin: `< /dev/null`.** Every headless launch otherwise stalls with
   `Warning: no stdin data received in 3s, proceeding without it.` Three seconds times every child.
6. **Read stdout and stderr separately.** The seat-drop warning arrived on the merged stream and
   broke a naive `json.loads(stdout)`.
7. **`--append-system-prompt-file` and `--system-prompt-file` DO exist** on 2.1.263 - they are
   parsed and act on the file (`Error: Append system prompt file not found: …`). They have no
   `--help` row of their own, appearing only inside `--bare`'s bracket notation, which is why the
   plan-time audit called them unconfirmed. **`--max-turns` is genuinely absent** on 2.1.263 and
   stays dropped.

## Flags confirmed present on 2.1.263

`--agent` · `--agents` · `--append-system-prompt` · `--append-system-prompt-file` (undocumented) ·
`--exclude-dynamic-system-prompt-sections` · `--fork-session` · `--json-schema` (inline JSON) ·
`--max-budget-usd` (soft) · `--model` · `--output-format` · `--permission-mode` · `--resume` ·
`--session-id` · `--system-prompt` · `--system-prompt-file` (undocumented) · `--system-prompt-snapshot`

**Absent:** `--max-turns`.

⚠️ **`--exclude-dynamic-system-prompt-sections` is ignored with `--system-prompt`** (per its own help
text) - it applies only to the default system prompt, so the runner must never combine the two.
⚠️ **`--system-prompt-snapshot` is turned OFF by passing `--system-prompt` or `--append-system-prompt`**,
which is a second reason arm A (a seat) beats arm B (an appended prompt).

## Table 6 - Step 2's first question, answered: the sandboxed child CAN fork

Table 5 left one thing open - whether `~/.claude/projects` could be granted as a sandbox
allowWrite path, or the runner had to run unsandboxed. **Neither, and the answer is better than
both.** `CLAUDE_CONFIG_DIR` moves the whole config directory, transcript store included, and
`~/.local/share` is already on the sandbox's allowWrite list. Two things have to be seeded there
once or every child dies at `Not logged in`: the OAuth credential (SYMLINKED, never copied - one
secret, one file on disk) and the workspace trust flag.

| arm (all launches SANDBOXED, `claude-haiku-4-5-20251001`) | cache_create | cache_read | cost |
|---|---|---|---|
| relocated store, no credential | - | - | `Not logged in - please run /login` |
| + credential symlinked, workspace UNTRUSTED | 9,895 | **0** | $0.0201 |
| + workspace trusted - parent | 10,425 | 9,623 | $0.0250 |
| + workspace trusted - **fork** | **399** | **10,425** | **$0.0020** |

**A fork is 92% cheaper than its parent, inside the sandbox, with no settings change and no
escalation.** Better than the 83% Table 2 measured unsandboxed.

⚠️ **The trust flag is load-bearing for COST, not just for warnings.** Untrusted, the child logs
`Ignoring 217 permissions.allow entries ... this workspace has not been trusted` and reads **zero**
cached tokens on every fork - so the entire layered saving disappears while every launch still
succeeds. Isolated by running the same chain unsandboxed, where it also read zero: the sandbox was
never the cause. Nothing about that failure looks like a cost failure; the bill is the only tell.

ⓘ **What the trust flag actually grants**, since it is a permission surface: the repo's OWN tracked
`.claude/settings.json` allow rows - the ones already in git, already the operator's. It widens
nothing beyond them, and it is written into the autopilot's own config dir, never into
`~/.claude/settings.json` or the repo's (both barred to agents).

**So the runner owns this**: `autopilot_run.py` seeds that home and sets `CLAUDE_CONFIG_DIR` on
every child. `~/.claude/projects` needs no grant, `claude_permissions_apply.py` needs no edit, and
the unsandboxed fallback is not needed.

---

## What Step 2 inherits

The runner's flag set, byte for byte:

```
claude -p "<the door name and its args>" \
  --agents "$(cat <rendered seat>.json)" --agent <seat> \
  --model <pinned per seat> \
  --permission-mode auto \
  --exclude-dynamic-system-prompt-sections \
  --output-format json \
  --json-schema "$(cat <schema>.json)" \
  --max-budget-usd <per-child, soft> \
  [--session-id <fresh uuid> | --resume <pack id> --fork-session] \
  < /dev/null
```

with stdout and stderr captured separately, the result parsed defensively, and `--agents` present on
**every** invocation including the forks.
